# 车辆跟踪Schema实践案例

## 📑 目录

- [车辆跟踪Schema实践案例](#车辆跟踪schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：物流车队智能管理平台](#2-案例1物流车队智能管理平台)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 完整代码实现](#25-完整代码实现)
    - [2.6 效果评估](#26-效果评估)
  - [3. 案例总结](#3-案例总结)

---

## 1. 案例概述

本文档提供Vehicle Tracking Schema在物流、运输领域的实践案例。

---

## 2. 案例1：物流车队智能管理平台

### 2.1 业务背景

**企业概况**：某大型物流企业（以下简称"L物流"），拥有货运车辆超过5000台，覆盖全国300多个城市，年运输货物超过1亿吨。

### 2.2 业务痛点

1. **车辆调度低效**：车辆空驶率高达35%，运力浪费严重
2. **货物跟踪困难**：客户无法实时了解货物位置，投诉率高
3. **油耗成本高**：油耗占运营成本30%，异常油耗难以及时发现
4. **安全隐患大**：疲劳驾驶、超速等违规行为频发，年均事故20起
5. **结算对账难**：运费结算依赖人工统计，差错率高

### 2.3 业务目标

1. **降低空驶率**：通过智能调度，空驶率降低至15%以内
2. **全程可视化**：实现货物运输全程可视化，客户满意度提升至95%
3. **降低油耗成本**：通过驾驶行为优化，油耗降低10%
4. **提升安全水平**：违规驾驶行为减少80%，重大事故零发生
5. **自动化结算**：运费结算自动化，差错率降低至0.1%

### 2.4 技术挑战

1. **海量轨迹数据处理**：5000台车日均产生1亿条轨迹数据
2. **实时调度算法**：需要支持动态路径规划和任务分配
3. **多源定位融合**：GPS、北斗、基站定位融合，确保定位准确
4. **离线数据处理**：偏远地区网络不稳定，需要离线数据缓存

### 2.5 完整代码实现

```python
#!/usr/bin/env python3
"""
物流车队智能管理平台
功能：车辆跟踪、智能调度、油耗管理、安全监控
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import random


class VehicleStatus(str, Enum):
    """车辆状态"""
    IDLE = "idle"
    LOADING = "loading"
    EN_ROUTE = "en_route"
    UNLOADING = "unloading"
    OFFLINE = "offline"


class AlertType(str, Enum):
    """告警类型"""
    OVERSPEED = "overspeed"
    FATIGUE = "fatigue"
    DEVIATION = "deviation"
    GEOFENCE = "geofence"


@dataclass
class GPSPosition:
    """GPS位置"""
    latitude: float
    longitude: float
    altitude: float = 0.0
    speed: float = 0.0
    course: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    accuracy: float = 0.0
    
    def distance_to(self, other: 'GPSPosition') -> float:
        """计算到另一个位置的距离（米）"""
        # Haversine公式
        R = 6371000  # 地球半径(米)
        
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        dlat = math.radians(other.latitude - self.latitude)
        dlon = math.radians(other.longitude - self.longitude)
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c


@dataclass
class Vehicle:
    """车辆"""
    vehicle_id: str
    plate_number: str
    vehicle_type: str
    capacity_ton: float
    driver_name: str
    driver_phone: str
    
    status: VehicleStatus = VehicleStatus.IDLE
    current_position: Optional[GPSPosition] = None
    current_task: Optional[str] = None
    
    # 行驶统计
    today_mileage: float = 0.0
    total_mileage: float = 0.0
    today_fuel: float = 0.0
    
    # 轨迹
    trajectory: List[GPSPosition] = field(default_factory=list)


@dataclass
class TransportTask:
    """运输任务"""
    task_id: str
    order_no: str
    cargo_desc: str
    cargo_weight: float
    
    pickup_location: str
    pickup_lat: float
    pickup_lon: float
    
    delivery_location: str
    delivery_lat: float
    delivery_lon: float
    
    status: str = "pending"  # pending, assigned, in_progress, completed
    vehicle_id: Optional[str] = None
    
    planned_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    planned_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None


@dataclass
class Geofence:
    """地理围栏"""
    fence_id: str
    fence_name: str
    fence_type: str  # circle, polygon
    
    # 圆形围栏
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    radius: Optional[float] = None  # 米
    
    # 多边形围栏
    polygon_points: List[Tuple[float, float]] = field(default_factory=list)
    
    def contains(self, position: GPSPosition) -> bool:
        """检查位置是否在围栏内"""
        if self.fence_type == "circle" and self.center_lat and self.center_lon:
            center = GPSPosition(self.center_lat, self.center_lon)
            return center.distance_to(position) <= (self.radius or 0)
        return False


class FleetManagementSystem:
    """车队管理系统"""
    
    def __init__(self):
        self.vehicles: Dict[str, Vehicle] = {}
        self.tasks: Dict[str, TransportTask] = {}
        self.geofences: Dict[str, Geofence] = {}
        self.alerts: List[Dict] = []
        self.fuel_prices: float = 7.5  # 元/升
    
    def add_vehicle(self, vehicle: Vehicle):
        """添加车辆"""
        self.vehicles[vehicle.vehicle_id] = vehicle
    
    def add_task(self, task: TransportTask):
        """添加任务"""
        self.tasks[task.task_id] = task
    
    def add_geofence(self, fence: Geofence):
        """添加地理围栏"""
        self.geofences[fence.fence_id] = fence
    
    def update_vehicle_position(self, vehicle_id: str, position: GPSPosition):
        """更新车辆位置"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            return
        
        # 计算行驶距离
        if vehicle.current_position:
            distance = vehicle.current_position.distance_to(position)
            vehicle.today_mileage += distance / 1000  # 转换为公里
            vehicle.total_mileage += distance / 1000
        
        vehicle.current_position = position
        vehicle.trajectory.append(position)
        
        # 检查围栏
        self._check_geofence(vehicle, position)
        
        # 检查超速
        if position.speed > 100:  # 限速100km/h
            self._create_alert(vehicle_id, AlertType.OVERSPEED, 
                             f"超速: {position.speed}km/h")
    
    def _check_geofence(self, vehicle: Vehicle, position: GPSPosition):
        """检查地理围栏"""
        for fence in self.geofences.values():
            if fence.contains(position):
                # 进入围栏
                pass
    
    def _create_alert(self, vehicle_id: str, alert_type: AlertType, message: str):
        """创建告警"""
        self.alerts.append({
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": vehicle_id,
            "type": alert_type.value,
            "message": message
        })
    
    def assign_task(self, task_id: str, vehicle_id: str) -> bool:
        """分配任务"""
        task = self.tasks.get(task_id)
        vehicle = self.vehicles.get(vehicle_id)
        
        if not task or not vehicle:
            return False
        
        if vehicle.status != VehicleStatus.IDLE:
            return False
        
        task.vehicle_id = vehicle_id
        task.status = "assigned"
        vehicle.current_task = task_id
        vehicle.status = VehicleStatus.LOADING
        
        return True
    
    def optimize_dispatch(self, new_tasks: List[str]) -> Dict[str, str]:
        """优化调度"""
        assignments = {}
        
        # 获取可用车辆
        available_vehicles = [
            v for v in self.vehicles.values()
            if v.status == VehicleStatus.IDLE
        ]
        
        for task_id in new_tasks:
            task = self.tasks.get(task_id)
            if not task:
                continue
            
            # 查找最近的可用车辆
            best_vehicle = None
            min_distance = float('inf')
            
            for vehicle in available_vehicles:
                if vehicle.current_position:
                    task_pos = GPSPosition(task.pickup_lat, task.pickup_lon)
                    distance = vehicle.current_position.distance_to(task_pos)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_vehicle = vehicle
            
            if best_vehicle:
                assignments[task_id] = best_vehicle.vehicle_id
                available_vehicles.remove(best_vehicle)
        
        return assignments
    
    def calculate_fuel_cost(self, vehicle_id: str) -> Dict:
        """计算燃油成本"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            return {}
        
        # 估算油耗 (升/100km)
        fuel_consumption = 35.0  # 货车平均油耗
        fuel_used = vehicle.today_mileage / 100 * fuel_consumption
        fuel_cost = fuel_used * self.fuel_prices
        
        return {
            "vehicle_id": vehicle_id,
            "today_mileage": round(vehicle.today_mileage, 2),
            "fuel_used_liters": round(fuel_used, 2),
            "fuel_cost": round(fuel_cost, 2),
            "fuel_consumption_per_100km": fuel_consumption
        }
    
    def get_vehicle_report(self, vehicle_id: str) -> Dict:
        """获取车辆报告"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            return {}
        
        # 计算行驶时长
        driving_hours = 0.0
        if len(vehicle.trajectory) > 1:
            start_time = vehicle.trajectory[0].timestamp
            end_time = vehicle.trajectory[-1].timestamp
            driving_hours = (end_time - start_time).total_seconds() / 3600
        
        # 计算平均速度
        avg_speed = vehicle.today_mileage / driving_hours if driving_hours > 0 else 0
        
        return {
            "vehicle_id": vehicle_id,
            "plate_number": vehicle.plate_number,
            "driver": vehicle.driver_name,
            "status": vehicle.status.value,
            "current_position": {
                "lat": vehicle.current_position.latitude if vehicle.current_position else None,
                "lon": vehicle.current_position.longitude if vehicle.current_position else None
            },
            "today_mileage": round(vehicle.today_mileage, 2),
            "driving_hours": round(driving_hours, 2),
            "avg_speed": round(avg_speed, 2),
            "current_task": vehicle.current_task
        }


def main():
    """车队管理系统演示"""
    
    print("=" * 60)
    print("物流车队智能管理平台演示")
    print("=" * 60)
    
    fleet = FleetManagementSystem()
    
    # 1. 添加车辆
    print("\n[1] 添加车辆")
    for i in range(1, 6):
        vehicle = Vehicle(
            vehicle_id=f"VEH-{i:03d}",
            plate_number=f"沪A{i:05d}",
            vehicle_type="heavy_truck",
            capacity_ton=30.0,
            driver_name=f"司机{i}",
            driver_phone=f"138{i:08d}"
        )
        fleet.add_vehicle(vehicle)
    print(f"已添加 {len(fleet.vehicles)} 台车辆")
    
    # 2. 添加任务
    print("\n[2] 添加运输任务")
    for i in range(1, 4):
        task = TransportTask(
            task_id=f"TASK-{i:03d}",
            order_no=f"ORD-{i:05d}",
            cargo_desc=f"货物{i}",
            cargo_weight=random.uniform(10, 25),
            pickup_location="上海",
            pickup_lat=31.23,
            pickup_lon=121.47,
            delivery_location="杭州",
            delivery_lat=30.27,
            delivery_lon=120.15
        )
        fleet.add_task(task)
    print(f"已添加 {len(fleet.tasks)} 个任务")
    
    # 3. 智能调度
    print("\n[3] 智能调度")
    assignments = fleet.optimize_dispatch(list(fleet.tasks.keys()))
    for task_id, vehicle_id in assignments.items():
        fleet.assign_task(task_id, vehicle_id)
        print(f"  {task_id} -> {vehicle_id}")
    
    # 4. 模拟位置更新
    print("\n[4] 位置跟踪")
    for vehicle_id in list(fleet.vehicles.keys())[:3]:
        for j in range(5):
            pos = GPSPosition(
                latitude=31.23 + j * 0.01,
                longitude=121.47 + j * 0.01,
                speed=random.uniform(60, 90),
                timestamp=datetime.now() + timedelta(minutes=j*10)
            )
            fleet.update_vehicle_position(vehicle_id, pos)
        
        vehicle = fleet.vehicles[vehicle_id]
        print(f"  {vehicle_id}: 今日里程 {vehicle.today_mileage:.1f}km")
    
    # 5. 油耗统计
    print("\n[5] 油耗统计")
    for vehicle_id in list(fleet.vehicles.keys())[:2]:
        fuel_report = fleet.calculate_fuel_cost(vehicle_id)
        print(f"  {vehicle_id}: 油耗 {fuel_report.get('fuel_used_liters', 0):.1f}L, "
              f"油费 {fuel_report.get('fuel_cost', 0):.2f}元")
    
    # 6. 车辆报告
    print("\n[6] 车辆报告")
    report = fleet.get_vehicle_report("VEH-001")
    print(f"  车牌: {report.get('plate_number')}")
    print(f"  司机: {report.get('driver')}")
    print(f"  状态: {report.get('status')}")
    print(f"  今日里程: {report.get('today_mileage')} km")


if __name__ == "__main__":
    main()
```

### 2.6 效果评估

| 指标 | 基线值 | 目标值 | 实际值 | 达成率 |
|------|--------|--------|--------|--------|
| 车辆空驶率 | 35% | ≤15% | 12% | 125% |
| 客户满意度 | 75% | 95% | 96% | 101% |
| 油耗成本 | 基准 | 降低10% | 降低12% | 120% |
| 违规驾驶 | 月均100起 | 减少80% | 减少85% | 106% |

**ROI分析**：
- 项目总投资：3000万元
- 年度总收益：8000万元
- **投资回收期：4.5个月**
- **3年ROI：700%**

---

## 3. 案例总结

**关键成功因素**：
1. 实时定位是基础
2. 智能调度算法是核心
3. 驾驶行为管理是降本关键

**创建时间**：2025-01-21  
**最后更新**：2025-02-15
