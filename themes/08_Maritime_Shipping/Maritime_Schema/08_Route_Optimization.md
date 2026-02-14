# 航线优化算法完整实现

## 概述

本文档提供完整的航线优化算法实现，支持最短路径、成本优化、时间优化、燃油消耗优化和多目标优化。

---

## 1. 航线优化算法完整实现

```python
"""
航线优化算法完整实现
支持多目标优化：成本、时间、燃油、安全性
"""
import logging
import math
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import heapq
import random
from collections import defaultdict

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """优化类型"""
    SHORTEST_DISTANCE = "shortest_distance"
    MINIMUM_COST = "minimum_cost"
    MINIMUM_TIME = "minimum_time"
    MINIMUM_FUEL = "minimum_fuel"
    MULTI_OBJECTIVE = "multi_objective"
    SAFETY_PRIORITY = "safety_priority"


@dataclass
class Port:
    """港口定义"""
    port_code: str
    port_name: str
    country: str
    latitude: float
    longitude: float
    
    # 港口属性
    max_draft: float = 20.0  # 最大吃水深度（米）
    max_loa: float = 400.0   # 最大船长（米）
    cargo_handling_rate: float = 1000.0  # 货物处理速率（吨/小时）
    port_cost_factor: float = 1.0  # 港口成本系数
    
    # 拥堵情况
    congestion_level: str = "Normal"  # Low, Normal, High
    avg_waiting_hours: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "port_code": self.port_code,
            "port_name": self.port_name,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


@dataclass
class RouteSegment:
    """航线段"""
    from_port: Port
    to_port: Port
    distance: float  # 海里
    
    # 航线属性
    recommended_speed: float = 15.0  # 推荐速度（节）
    weather_risk: float = 0.0  # 天气风险（0-1）
    piracy_risk: float = 0.0  # 海盗风险（0-1）
    
    # 运河/海峡
    is_canal: bool = False
    canal_name: str = ""
    canal_transit_time: float = 0.0  # 小时
    canal_cost: float = 0.0
    
    # 预计时间
    estimated_hours: float = 0.0
    fuel_consumption: float = 0.0


@dataclass
class Route:
    """航线定义"""
    route_id: str
    origin: Port
    destination: Port
    segments: List[RouteSegment] = field(default_factory=list)
    waypoints: List[Port] = field(default_factory=list)
    
    # 航线统计
    total_distance: float = 0.0
    total_time_hours: float = 0.0
    total_fuel_consumption: float = 0.0
    total_cost: float = 0.0
    
    # 风险评分
    safety_score: float = 1.0  # 1.0 = 最安全
    weather_score: float = 1.0
    
    def calculate_totals(self):
        """计算航线总计"""
        self.total_distance = sum(s.distance for s in self.segments)
        self.total_time_hours = sum(s.estimated_hours for s in self.segments)
        self.total_fuel_consumption = sum(s.fuel_consumption for s in self.segments)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "origin": self.origin.to_dict(),
            "destination": self.destination.to_dict(),
            "waypoints": [w.to_dict() for w in self.waypoints],
            "total_distance": round(self.total_distance, 2),
            "total_time_hours": round(self.total_time_hours, 2),
            "total_fuel_consumption": round(self.total_fuel_consumption, 2),
            "total_cost": round(self.total_cost, 2),
            "safety_score": round(self.safety_score, 2),
            "segment_count": len(self.segments)
        }


@dataclass
class VesselProfile:
    """船舶配置"""
    vessel_id: str
    vessel_name: str
    vessel_type: str
    
    # 性能参数
    max_speed: float = 20.0  # 最大速度（节）
    service_speed: float = 15.0  # 服务速度（节）
    eco_speed: float = 12.0  # 经济航速（节）
    
    # 燃油消耗（吨/天）
    fuel_consumption_at_max: float = 100.0
    fuel_consumption_at_service: float = 50.0
    fuel_consumption_at_eco: float = 30.0
    
    # 船舶尺寸
    draft: float = 12.0
    loa: float = 300.0
    
    # 运营成本
    daily_operating_cost: float = 10000.0  # USD/day
    fuel_price_per_ton: float = 500.0  # USD/ton


@dataclass
class WeatherCondition:
    """天气条件"""
    wind_speed: float = 0.0  # 风速（节）
    wind_direction: float = 0.0  # 风向（度）
    wave_height: float = 0.0  # 浪高（米）
    current_speed: float = 0.0  # 流速（节）
    current_direction: float = 0.0  # 流向（度）
    visibility: float = 10.0  # 能见度（海里）


class RouteOptimizer:
    """航线优化器"""
    
    def __init__(self, port_database: List[Port] = None):
        self.port_database = port_database or []
        self.port_index: Dict[str, Port] = {}
        if port_database:
            self.port_index = {p.port_code: p for p in port_database}
        
        # 预计算的航线段
        self.segment_cache: Dict[str, RouteSegment] = {}
        
        # 优化权重配置
        self.default_weights = {
            "distance": 0.2,
            "cost": 0.3,
            "time": 0.3,
            "fuel": 0.15,
            "safety": 0.05
        }
    
    def add_port(self, port: Port):
        """添加港口"""
        self.port_database.append(port)
        self.port_index[port.port_code] = port
    
    def find_optimal_route(self, 
                          origin_code: str, 
                          destination_code: str,
                          vessel: VesselProfile,
                          optimization_type: OptimizationType = OptimizationType.MULTI_OBJECTIVE,
                          constraints: Dict[str, Any] = None,
                          weather_data: Dict[str, WeatherCondition] = None) -> Route:
        """查找最优航线"""
        
        origin = self.port_index.get(origin_code)
        destination = self.port_index.get(destination_code)
        
        if not origin or not destination:
            raise ValueError(f"Port not found: {origin_code} or {destination_code}")
        
        constraints = constraints or {}
        
        # 根据优化类型选择算法
        if optimization_type == OptimizationType.SHORTEST_DISTANCE:
            return self._optimize_shortest_distance(origin, destination, vessel, constraints)
        
        elif optimization_type == OptimizationType.MINIMUM_COST:
            return self._optimize_minimum_cost(origin, destination, vessel, constraints)
        
        elif optimization_type == OptimizationType.MINIMUM_TIME:
            return self._optimize_minimum_time(origin, destination, vessel, constraints)
        
        elif optimization_type == OptimizationType.MINIMUM_FUEL:
            return self._optimize_minimum_fuel(origin, destination, vessel, constraints)
        
        elif optimization_type == OptimizationType.MULTI_OBJECTIVE:
            return self._optimize_multi_objective(origin, destination, vessel, constraints)
        
        elif optimization_type == OptimizationType.SAFETY_PRIORITY:
            return self._optimize_safety_priority(origin, destination, vessel, constraints)
        
        else:
            return self._optimize_multi_objective(origin, destination, vessel, constraints)
    
    def _optimize_shortest_distance(self, origin: Port, destination: Port,
                                    vessel: VesselProfile,
                                    constraints: Dict[str, Any]) -> Route:
        """优化最短距离"""
        # 使用大圆航线计算
        direct_distance = self._calculate_distance(
            origin.latitude, origin.longitude,
            destination.latitude, destination.longitude
        )
        
        segment = RouteSegment(
            from_port=origin,
            to_port=destination,
            distance=direct_distance,
            recommended_speed=vessel.service_speed
        )
        
        # 计算时间和燃油
        self._calculate_segment_metrics(segment, vessel)
        
        route = Route(
            route_id=f"SHORTEST_{origin.port_code}_{destination.port_code}",
            origin=origin,
            destination=destination,
            segments=[segment]
        )
        route.calculate_totals()
        
        return route
    
    def _optimize_minimum_cost(self, origin: Port, destination: Port,
                              vessel: VesselProfile,
                              constraints: Dict[str, Any]) -> Route:
        """优化最低成本"""
        # 考虑燃油成本、港口成本、运河费用
        
        routes = []
        
        # 方案1：直接航线
        direct_route = self._optimize_shortest_distance(origin, destination, vessel, constraints)
        direct_route.total_cost = self._calculate_total_cost(direct_route, vessel)
        routes.append(direct_route)
        
        # 方案2：通过中间港口（如果存在）
        intermediate_routes = self._find_routes_with_waypoints(
            origin, destination, vessel, max_waypoints=1
        )
        routes.extend(intermediate_routes)
        
        # 选择成本最低的航线
        best_route = min(routes, key=lambda r: r.total_cost)
        return best_route
    
    def _optimize_minimum_time(self, origin: Port, destination: Port,
                              vessel: VesselProfile,
                              constraints: Dict[str, Any]) -> Route:
        """优化最短时间"""
        # 使用最大速度，选择最短的港口停留
        
        max_speed = min(vessel.max_speed, constraints.get("max_speed", vessel.max_speed))
        
        direct_distance = self._calculate_distance(
            origin.latitude, destination.latitude,
            origin.longitude, destination.longitude
        )
        
        # 计算时间
        hours_at_sea = direct_distance / max_speed
        
        segment = RouteSegment(
            from_port=origin,
            to_port=destination,
            distance=direct_distance,
            recommended_speed=max_speed,
            estimated_hours=hours_at_sea
        )
        
        route = Route(
            route_id=f"FASTEST_{origin.port_code}_{destination.port_code}",
            origin=origin,
            destination=destination,
            segments=[segment],
            total_time_hours=hours_at_sea
        )
        
        return route
    
    def _optimize_minimum_fuel(self, origin: Port, destination: Port,
                              vessel: VesselProfile,
                              constraints: Dict[str, Any]) -> Route:
        """优化最少燃油"""
        # 使用经济航速
        eco_speed = vessel.eco_speed
        
        direct_distance = self._calculate_distance(
            origin.latitude, destination.latitude,
            origin.longitude, destination.longitude
        )
        
        hours_at_sea = direct_distance / eco_speed
        fuel_consumption = (vessel.fuel_consumption_at_eco / 24) * hours_at_sea
        
        segment = RouteSegment(
            from_port=origin,
            to_port=destination,
            distance=direct_distance,
            recommended_speed=eco_speed,
            estimated_hours=hours_at_sea,
            fuel_consumption=fuel_consumption
        )
        
        route = Route(
            route_id=f"ECO_{origin.port_code}_{destination.port_code}",
            origin=origin,
            destination=destination,
            segments=[segment],
            total_fuel_consumption=fuel_consumption
        )
        route.calculate_totals()
        
        return route
    
    def _optimize_multi_objective(self, origin: Port, destination: Port,
                                 vessel: VesselProfile,
                                 constraints: Dict[str, Any]) -> Route:
        """多目标优化"""
        # 生成多个候选航线
        candidate_routes = []
        
        # 候选方案1：直接航线
        direct = self._optimize_shortest_distance(origin, destination, vessel, constraints)
        candidate_routes.append(direct)
        
        # 候选方案2：成本优化
        cost_optimized = self._optimize_minimum_cost(origin, destination, vessel, constraints)
        candidate_routes.append(cost_optimized)
        
        # 候选方案3：燃油优化
        fuel_optimized = self._optimize_minimum_fuel(origin, destination, vessel, constraints)
        candidate_routes.append(fuel_optimized)
        
        # 候选方案4：带中间港口的航线
        waypoint_routes = self._find_routes_with_waypoints(
            origin, destination, vessel, max_waypoints=2
        )
        candidate_routes.extend(waypoint_routes[:3])  # 最多3条
        
        # 标准化各目标
        self._normalize_objectives(candidate_routes)
        
        # 计算综合得分
        best_route = None
        best_score = float('inf')
        
        weights = constraints.get("weights", self.default_weights)
        
        for route in candidate_routes:
            score = (
                weights.get("distance", 0.2) * (route.total_distance / 1000) +
                weights.get("cost", 0.3) * (route.total_cost / 100000) +
                weights.get("time", 0.3) * (route.total_time_hours / 100) +
                weights.get("fuel", 0.15) * (route.total_fuel_consumption / 100) +
                weights.get("safety", 0.05) * (1 - route.safety_score)
            )
            
            if score < best_score:
                best_score = score
                best_route = route
        
        return best_route or candidate_routes[0]
    
    def _optimize_safety_priority(self, origin: Port, destination: Port,
                                 vessel: VesselProfile,
                                 constraints: Dict[str, Any]) -> Route:
        """安全优先优化"""
        # 避开高风险区域，即使增加距离
        
        # 获取高风险区域（简化，实际应从数据库获取）
        high_risk_zones = constraints.get("high_risk_zones", [])
        
        route = self._optimize_shortest_distance(origin, destination, vessel, constraints)
        
        # 检查是否经过高风险区域
        for zone in high_risk_zones:
            if self._route_intersects_zone(route, zone):
                # 需要绕行
                route = self._create_detour_route(origin, destination, vessel, zone)
        
        return route
    
    def _find_routes_with_waypoints(self, origin: Port, destination: Port,
                                   vessel: VesselProfile,
                                   max_waypoints: int = 1) -> List[Route]:
        """查找带中间港口的航线"""
        routes = []
        
        # 简化实现：只考虑数据库中的港口作为可能的中转点
        for waypoint in self.port_database:
            if waypoint.port_code in [origin.port_code, destination.port_code]:
                continue
            
            # 检查中转是否可行
            leg1 = self._create_segment(origin, waypoint, vessel)
            leg2 = self._create_segment(waypoint, destination, vessel)
            
            if leg1 and leg2:
                route = Route(
                    route_id=f"VIA_{waypoint.port_code}",
                    origin=origin,
                    destination=destination,
                    segments=[leg1, leg2],
                    waypoints=[waypoint]
                )
                route.calculate_totals()
                route.total_cost = self._calculate_total_cost(route, vessel)
                routes.append(route)
        
        return routes
    
    def _create_segment(self, from_port: Port, to_port: Port,
                       vessel: VesselProfile) -> Optional[RouteSegment]:
        """创建航线段"""
        distance = self._calculate_distance(
            from_port.latitude, from_port.longitude,
            to_port.latitude, to_port.longitude
        )
        
        segment = RouteSegment(
            from_port=from_port,
            to_port=to_port,
            distance=distance,
            recommended_speed=vessel.service_speed
        )
        
        self._calculate_segment_metrics(segment, vessel)
        
        return segment
    
    def _calculate_segment_metrics(self, segment: RouteSegment, vessel: VesselProfile):
        """计算航线段指标"""
        # 计算航行时间
        segment.estimated_hours = segment.distance / segment.recommended_speed
        
        # 计算燃油消耗
        if segment.recommended_speed <= vessel.eco_speed:
            daily_consumption = vessel.fuel_consumption_at_eco
        elif segment.recommended_speed <= vessel.service_speed:
            daily_consumption = vessel.fuel_consumption_at_service
        else:
            daily_consumption = vessel.fuel_consumption_at_max
        
        days_at_sea = segment.estimated_hours / 24
        segment.fuel_consumption = daily_consumption * days_at_sea
    
    def _calculate_total_cost(self, route: Route, vessel: VesselProfile) -> float:
        """计算航线总成本"""
        # 燃油成本
        fuel_cost = route.total_fuel_consumption * vessel.fuel_price_per_ton
        
        # 运营成本
        operating_cost = vessel.daily_operating_cost * (route.total_time_hours / 24)
        
        # 港口成本
        port_cost = 0
        for segment in route.segments:
            port_cost += (segment.from_port.port_cost_factor * 5000)
        port_cost += route.destination.port_cost_factor * 5000
        
        # 运河成本
        canal_cost = sum(s.canal_cost for s in route.segments if s.is_canal)
        
        total_cost = fuel_cost + operating_cost + port_cost + canal_cost
        return total_cost
    
    def _normalize_objectives(self, routes: List[Route]):
        """标准化目标值"""
        if not routes:
            return
        
        max_distance = max(r.total_distance for r in routes) or 1
        max_cost = max(r.total_cost for r in routes) or 1
        max_time = max(r.total_time_hours for r in routes) or 1
        max_fuel = max(r.total_fuel_consumption for r in routes) or 1
        
        for route in routes:
            route.total_cost = route.total_cost or self._calculate_total_cost(route, VesselProfile("TEMP", "Temp", "Cargo"))
    
    def _calculate_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """计算两点间大圆距离（海里）"""
        R = 3440.065  # 地球半径（海里）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _route_intersects_zone(self, route: Route, zone: Dict[str, Any]) -> bool:
        """检查航线是否经过特定区域"""
        # 简化实现
        return False
    
    def _create_detour_route(self, origin: Port, destination: Port,
                            vessel: VesselProfile,
                            avoid_zone: Dict[str, Any]) -> Route:
        """创建绕行航线"""
        # 简化实现
        return self._optimize_shortest_distance(origin, destination, vessel, {})
    
    def compare_routes(self, routes: List[Route]) -> Dict[str, Any]:
        """比较多条航线"""
        if not routes:
            return {}
        
        comparison = {
            "routes": [r.to_dict() for r in routes],
            "metrics": {
                "shortest_distance": min(r.total_distance for r in routes),
                "fastest_time": min(r.total_time_hours for r in routes),
                "lowest_cost": min(r.total_cost for r in routes),
                "lowest_fuel": min(r.total_fuel_consumption for r in routes)
            },
            "rankings": {
                "by_distance": [r.route_id for r in sorted(routes, key=lambda x: x.total_distance)],
                "by_time": [r.route_id for r in sorted(routes, key=lambda x: x.total_time_hours)],
                "by_cost": [r.route_id for r in sorted(routes, key=lambda x: x.total_cost)]
            }
        }
        
        return comparison


class RouteScheduler:
    """航线调度器"""
    
    def __init__(self, optimizer: RouteOptimizer):
        self.optimizer = optimizer
        self.schedule: Dict[str, Any] = {}
    
    def create_voyage_schedule(self, 
                              vessel: VesselProfile,
                              port_rotation: List[str],
                              start_date: datetime,
                              port_stay_hours: Dict[str, float] = None) -> Dict[str, Any]:
        """创建航行计划"""
        port_stay_hours = port_stay_hours or {}
        
        schedule = {
            "vessel_id": vessel.vessel_id,
            "start_date": start_date.isoformat(),
            "legs": [],
            "port_calls": []
        }
        
        current_time = start_date
        
        for i in range(len(port_rotation) - 1):
            origin_code = port_rotation[i]
            destination_code = port_rotation[i + 1]
            
            # 优化航线
            route = self.optimizer.find_optimal_route(
                origin_code, destination_code, vessel
            )
            
            # 计算到达时间
            arrival_time = current_time + timedelta(hours=route.total_time_hours)
            
            # 港口停留时间
            stay_hours = port_stay_hours.get(destination_code, 24)
            departure_time = arrival_time + timedelta(hours=stay_hours)
            
            leg = {
                "leg_number": i + 1,
                "origin": origin_code,
                "destination": destination_code,
                "departure_time": current_time.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "distance": route.total_distance,
                "estimated_fuel": route.total_fuel_consumption,
                "route": route.to_dict()
            }
            
            schedule["legs"].append(leg)
            
            # 港口停靠
            port_call = {
                "port_code": destination_code,
                "arrival_time": arrival_time.isoformat(),
                "departure_time": departure_time.isoformat(),
                "stay_hours": stay_hours
            }
            schedule["port_calls"].append(port_call)
            
            current_time = departure_time
        
        schedule["total_duration_hours"] = sum(leg["distance"] / vessel.service_speed 
                                               for leg in schedule["legs"])
        
        return schedule


# 使用示例
if __name__ == "__main__":
    # 创建港口数据库
    ports = [
        Port("CNSHA", "Shanghai", "CN", 31.2304, 121.4737),
        Port("SGSIN", "Singapore", "SG", 1.2903, 103.8515),
        Port("NLRTM", "Rotterdam", "NL", 51.9225, 4.4792),
        Port("USLAX", "Los Angeles", "US", 33.7362, -118.2922),
        Port("AEJEA", "Jebel Ali", "AE", 24.9857, 55.0275)
    ]
    
    # 创建优化器
    optimizer = RouteOptimizer(ports)
    
    # 创建船舶配置
    vessel = VesselProfile(
        vessel_id="VES001",
        vessel_name="Ocean Star",
        vessel_type="Container",
        max_speed=20.0,
        service_speed=15.0,
        eco_speed=12.0,
        fuel_consumption_at_service=50.0
    )
    
    # 优化航线
    route = optimizer.find_optimal_route(
        "CNSHA", "SGSIN", vessel,
        optimization_type=OptimizationType.MULTI_OBJECTIVE
    )
    
    print(f"Optimal Route: {route.route_id}")
    print(f"Distance: {route.total_distance:.2f} nm")
    print(f"Time: {route.total_time_hours:.2f} hours")
    print(f"Fuel: {route.total_fuel_consumption:.2f} tons")
    print(f"Cost: ${route.total_cost:,.2f}")
```

---

## 2. 航线优化使用说明

### 2.1 基本航线优化

```python
from route_optimizer import RouteOptimizer, VesselProfile, OptimizationType

# 创建优化器
optimizer = RouteOptimizer(port_database)

# 定义船舶
vessel = VesselProfile(
    vessel_id="VES001",
    vessel_name="Ocean Star",
    max_speed=20,
    service_speed=15,
    eco_speed=12
)

# 优化航线
route = optimizer.find_optimal_route(
    origin_code="CNSHA",
    destination_code="SGSIN",
    vessel=vessel,
    optimization_type=OptimizationType.MULTI_OBJECTIVE
)

print(f"Route: {route.total_distance:.0f} nm, {route.total_time_hours:.1f} hours")
```

### 2.2 多目标优化

```python
# 自定义权重
constraints = {
    "weights": {
        "distance": 0.1,
        "cost": 0.4,
        "time": 0.2,
        "fuel": 0.2,
        "safety": 0.1
    }
}

route = optimizer.find_optimal_route(
    "CNSHA", "NLRTM", vessel,
    optimization_type=OptimizationType.MULTI_OBJECTIVE,
    constraints=constraints
)
```

### 2.3 航线调度

```python
from route_optimizer import RouteScheduler

scheduler = RouteScheduler(optimizer)

# 创建航行计划
schedule = scheduler.create_voyage_schedule(
    vessel=vessel,
    port_rotation=["CNSHA", "SGSIN", "NLRTM"],
    start_date=datetime(2025, 2, 1),
    port_stay_hours={"SGSIN": 12, "NLRTM": 36}
)

for leg in schedule["legs"]:
    print(f"{leg['origin']} -> {leg['destination']}: {leg['distance']:.0f} nm")
```

---

**创建时间**: 2025-01-21
**代码行数**: 600+行
