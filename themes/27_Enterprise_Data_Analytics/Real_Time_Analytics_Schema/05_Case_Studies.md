# 实时分析Schema实践案例

## 📑 目录

- [实时分析Schema实践案例](#实时分析schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：物流集团实时物流追踪与调度系统](#2-案例1物流集团实时物流追踪与调度系统)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估与ROI分析](#27-效果评估与roi分析)

---

## 1. 案例概述

本文档提供实时分析Schema在实际企业应用中的深度实践案例，涵盖物流追踪、IoT数据分析、实时风控等企业级场景。

---

## 2. 案例1：物流集团实时物流追踪与调度系统

### 2.1 企业背景

**企业简介**：
某大型物流集团（以下简称"华运物流"）拥有车辆5万台、员工10万人，覆盖全国3000个区县，日处理订单500万单，是中国领先的综合物流服务商。

**业务规模**：

| 指标 | 数值 |
|------|------|
| 运输车辆 | 5万+ |
| 日处理订单 | 500万+ |
| 服务网点 | 1万+ |
| 覆盖区县 | 3000+ |
| 日数据量 | 10TB+ |
| IoT设备 | 50万+ |

### 2.2 业务痛点

**痛点1：货物追踪滞后**
客户无法实时了解货物位置，客服查询响应慢，客户满意度低。

**痛点2：运力调度低效**
车辆空驶率高达30%，路线规划依赖经验，运输成本高。

**痛点3：异常处理滞后**
延误、破损等异常发现慢，被动处理导致客户投诉多。

**痛点4：资源利用率低**
仓储、车辆、人员资源无法动态优化配置，浪费严重。

**痛点5：决策缺乏实时性**
管理层依赖日报/周报，无法实时掌握运营状况，决策滞后。

### 2.3 业务目标

**目标1：全链路实时追踪**
实现货物从揽收到签收的全链路实时追踪，位置更新延迟<30秒。

**目标2：智能调度优化**
基于实时数据动态调度运力，将空驶率降至15%以下。

**目标3：异常实时预警**
建立实时异常检测机制，异常发现时间<5分钟。

**目标4：资源动态优化**
实现仓储、车辆、人员的实时优化配置，提升资源利用率。

**目标5：实时决策支持**
构建实时运营仪表盘，支持管理层实时决策。

### 2.4 技术挑战

**挑战1：海量IoT数据处理**
50万+ IoT设备每秒产生数百万数据点，需要高吞吐的流处理能力。

**挑战2：实时地理计算**
需要实时进行路径规划、ETA计算、距离计算等地理运算。

**挑战3：复杂事件处理**
需要识别延误风险、异常事件、最优调度时机等复杂模式。

**挑战4：高可用保障**
7×24小时不间断服务，不能容忍数据丢失或服务中断。

**挑战5：多源数据融合**
需要融合GPS、订单、天气、路况等多源异构数据。

### 2.5 解决方案

**架构设计**：
- **数据采集层**：IoT Hub + Kafka
- **流处理层**：Flink + Kafka Streams
- **分析计算层**：Redis + ClickHouse
- **应用服务层**：实时API + 推送服务

### 2.6 完整代码实现

```python
#!/usr/bin/env python3
"""
物流集团实时物流追踪与调度系统
基于Flink和Kafka的企业级实时物流解决方案
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import math
from collections import defaultdict


class VehicleStatus(str, Enum):
    """车辆状态"""
    IDLE = "Idle"
    LOADING = "Loading"
    IN_TRANSIT = "InTransit"
    UNLOADING = "Unloading"
    MAINTENANCE = "Maintenance"


class OrderStatus(str, Enum):
    """订单状态"""
    CREATED = "Created"
    PICKED_UP = "PickedUp"
    IN_TRANSIT = "InTransit"
    DELIVERED = "Delivered"
    EXCEPTION = "Exception"


class AlertType(str, Enum):
    """预警类型"""
    DELAY_RISK = "DelayRisk"
    ROUTE_DEVIATION = "RouteDeviation"
    TEMPERATURE_ALERT = "TemperatureAlert"
    VEHICLE_BREAKDOWN = "VehicleBreakdown"
    CONGESTION_DETECTED = "CongestionDetected"


@dataclass
class GPSPoint:
    """GPS坐标点"""
    latitude: float
    longitude: float
    timestamp: datetime
    speed: float = 0.0  # km/h
    altitude: float = 0.0
    
    def distance_to(self, other: 'GPSPoint') -> float:
        """计算两点间距离（简化版）"""
        # 使用Haversine公式
        R = 6371  # 地球半径(km)
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c


@dataclass
class Vehicle:
    """车辆"""
    vehicle_id: str
    plate_number: str
    vehicle_type: str  # truck, van, etc.
    capacity_kg: float
    capacity_cbm: float
    
    current_status: VehicleStatus = VehicleStatus.IDLE
    current_location: Optional[GPSPoint] = None
    current_order_id: Optional[str] = None
    driver_id: Optional[str] = None
    
    # 历史轨迹
    trajectory: List[GPSPoint] = field(default_factory=list)
    
    def update_location(self, point: GPSPoint):
        """更新位置"""
        self.current_location = point
        self.trajectory.append(point)
        # 保留最近1000个点
        if len(self.trajectory) > 1000:
            self.trajectory = self.trajectory[-1000:]
    
    def calculate_eta(self, destination: GPSPoint) -> timedelta:
        """计算预计到达时间"""
        if not self.current_location:
            return timedelta(hours=999)
        
        distance = self.current_location.distance_to(destination)
        # 假设平均速度60km/h
        hours = distance / 60
        return timedelta(hours=hours)


@dataclass
class Shipment:
    """运单"""
    shipment_id: str
    order_id: str
    origin: Dict[str, Any]  # 起点信息
    destination: Dict[str, Any]  # 终点信息
    cargo_info: Dict[str, Any]  # 货物信息
    
    status: OrderStatus = OrderStatus.CREATED
    assigned_vehicle_id: Optional[str] = None
    
    planned_pickup_time: Optional[datetime] = None
    planned_delivery_time: Optional[datetime] = None
    actual_pickup_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    
    current_temperature: Optional[float] = None  # 冷链监控
    
    def is_delayed(self) -> bool:
        """检查是否延误"""
        if self.status == OrderStatus.DELIVERED:
            return False
        if not self.planned_delivery_time:
            return False
        return datetime.now() > self.planned_delivery_time
    
    def get_delay_risk_score(self, vehicle: Optional[Vehicle]) -> float:
        """获取延误风险评分（0-1）"""
        if not self.planned_delivery_time:
            return 0.0
        
        if not vehicle or not vehicle.current_location:
            return 0.5
        
        dest = GPSPoint(
            latitude=self.destination.get("lat", 0),
            longitude=self.destination.get("lng", 0),
            timestamp=datetime.now()
        )
        eta = vehicle.calculate_eta(dest)
        estimated_arrival = datetime.now() + eta
        
        time_diff = (self.planned_delivery_time - estimated_arrival).total_seconds()
        if time_diff < 0:
            return 1.0  # 肯定会延误
        elif time_diff < 3600:  # 1小时内
            return 0.8
        elif time_diff < 7200:  # 2小时内
            return 0.5
        else:
            return 0.0


@dataclass
class RealTimeAlert:
    """实时预警"""
    alert_id: str
    alert_type: AlertType
    severity: str  # Low, Medium, High, Critical
    shipment_id: Optional[str]
    vehicle_id: Optional[str]
    message: str
    created_at: datetime
    location: Optional[GPSPoint] = None
    suggested_action: Optional[str] = None


@dataclass
class LogisticsRealTimePlatform:
    """物流实时平台"""
    platform_id: str
    platform_name: str
    
    # 车辆注册表
    vehicles: Dict[str, Vehicle] = field(default_factory=dict)
    
    # 运单注册表
    shipments: Dict[str, Shipment] = field(default_factory=dict)
    
    # 预警列表
    active_alerts: List[RealTimeAlert] = field(default_factory=list)
    
    # 区域热力图
    zone_heatmap: Dict[str, int] = field(default_factory=dict)
    
    def register_vehicle(self, vehicle: Vehicle):
        """注册车辆"""
        self.vehicles[vehicle.vehicle_id] = vehicle
    
    def register_shipment(self, shipment: Shipment):
        """注册运单"""
        self.shipments[shipment.shipment_id] = shipment
    
    def process_iot_message(self, message: Dict[str, Any]):
        """处理IoT消息"""
        msg_type = message.get("type")
        
        if msg_type == "GPS_UPDATE":
            self._process_gps_update(message)
        elif msg_type == "TEMPERATURE_UPDATE":
            self._process_temperature_update(message)
        elif msg_type == "STATUS_UPDATE":
            self._process_status_update(message)
    
    def _process_gps_update(self, message: Dict):
        """处理GPS更新"""
        vehicle_id = message.get("vehicle_id")
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            return
        
        point = GPSPoint(
            latitude=message.get("lat"),
            longitude=message.get("lng"),
            timestamp=datetime.fromisoformat(message.get("timestamp")),
            speed=message.get("speed", 0)
        )
        
        vehicle.update_location(point)
        
        # 更新热力图
        zone_key = f"{int(point.latitude)},{int(point.longitude)}"
        self.zone_heatmap[zone_key] = self.zone_heatmap.get(zone_key, 0) + 1
        
        # 检查路线偏离
        self._check_route_deviation(vehicle, point)
    
    def _process_temperature_update(self, message: Dict):
        """处理温度更新（冷链）"""
        shipment_id = message.get("shipment_id")
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            return
        
        temperature = message.get("temperature")
        shipment.current_temperature = temperature
        
        # 检查温度异常
        if temperature and (temperature > 8 or temperature < -2):
            alert = RealTimeAlert(
                alert_id=f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                alert_type=AlertType.TEMPERATURE_ALERT,
                severity="High" if temperature > 10 or temperature < -5 else "Medium",
                shipment_id=shipment_id,
                vehicle_id=shipment.assigned_vehicle_id,
                message=f"Temperature out of range: {temperature}°C",
                created_at=datetime.now(),
                suggested_action="Check refrigeration system immediately"
            )
            self.active_alerts.append(alert)
    
    def _process_status_update(self, message: Dict):
        """处理状态更新"""
        shipment_id = message.get("shipment_id")
        shipment = self.shipments.get(shipment_id)
        if not shipment:
            return
        
        new_status = message.get("status")
        if new_status == "PICKED_UP":
            shipment.status = OrderStatus.PICKED_UP
            shipment.actual_pickup_time = datetime.now()
        elif new_status == "DELIVERED":
            shipment.status = OrderStatus.DELIVERED
            shipment.actual_delivery_time = datetime.now()
            
            # 释放车辆
            if shipment.assigned_vehicle_id:
                vehicle = self.vehicles.get(shipment.assigned_vehicle_id)
                if vehicle:
                    vehicle.current_status = VehicleStatus.IDLE
                    vehicle.current_order_id = None
    
    def _check_route_deviation(self, vehicle: Vehicle, point: GPSPoint):
        """检查路线偏离"""
        # 简化实现，实际应对比规划路线
        if vehicle.current_order_id:
            shipment = self.shipments.get(vehicle.current_order_id)
            if shipment:
                dest = GPSPoint(
                    latitude=shipment.destination.get("lat", 0),
                    longitude=shipment.destination.get("lng", 0),
                    timestamp=datetime.now()
                )
                # 如果距离终点越来越远，可能存在偏离
                # 简化逻辑
                pass
    
    def check_delay_risks(self) -> List[RealTimeAlert]:
        """检查延误风险"""
        alerts = []
        
        for shipment in self.shipments.values():
            if shipment.status in [OrderStatus.DELIVERED, OrderStatus.EXCEPTION]:
                continue
            
            vehicle = None
            if shipment.assigned_vehicle_id:
                vehicle = self.vehicles.get(shipment.assigned_vehicle_id)
            
            risk_score = shipment.get_delay_risk_score(vehicle)
            
            if risk_score > 0.5:
                severity = "Critical" if risk_score > 0.8 else "High"
                alert = RealTimeAlert(
                    alert_id=f"ALERT-DELAY-{shipment.shipment_id}",
                    alert_type=AlertType.DELAY_RISK,
                    severity=severity,
                    shipment_id=shipment.shipment_id,
                    vehicle_id=shipment.assigned_vehicle_id,
                    message=f"High delay risk detected for shipment {shipment.shipment_id}",
                    created_at=datetime.now(),
                    suggested_action="Consider rerouting or backup vehicle"
                )
                alerts.append(alert)
                self.active_alerts.append(alert)
        
        return alerts
    
    def optimize_dispatch(self, new_shipment: Shipment) -> Optional[Vehicle]:
        """智能调度优化"""
        best_vehicle = None
        best_score = -999
        
        for vehicle in self.vehicles.values():
            if vehicle.current_status != VehicleStatus.IDLE:
                continue
            
            if not vehicle.current_location:
                continue
            
            # 计算调度评分
            pickup_point = GPSPoint(
                latitude=new_shipment.origin.get("lat", 0),
                longitude=new_shipment.origin.get("lng", 0),
                timestamp=datetime.now()
            )
            
            # 距离因素（越近越好）
            distance = vehicle.current_location.distance_to(pickup_point)
            distance_score = max(0, 100 - distance)
            
            # 车辆容量匹配
            cargo_weight = new_shipment.cargo_info.get("weight_kg", 0)
            capacity_score = 100 if vehicle.capacity_kg >= cargo_weight else 0
            
            # 综合评分
            score = distance_score * 0.6 + capacity_score * 0.4
            
            if score > best_score:
                best_score = score
                best_vehicle = vehicle
        
        if best_vehicle:
            # 分配运单
            new_shipment.assigned_vehicle_id = best_vehicle.vehicle_id
            best_vehicle.current_status = VehicleStatus.LOADING
            best_vehicle.current_order_id = new_shipment.shipment_id
        
        return best_vehicle
    
    def get_realtime_dashboard(self) -> Dict[str, Any]:
        """获取实时仪表盘数据"""
        total_vehicles = len(self.vehicles)
        active_vehicles = len([v for v in self.vehicles.values() 
                             if v.current_status == VehicleStatus.IN_TRANSIT])
        
        total_shipments = len(self.shipments)
        delivered_shipments = len([s for s in self.shipments.values() 
                                  if s.status == OrderStatus.DELIVERED])
        
        critical_alerts = len([a for a in self.active_alerts 
                              if a.severity in ["High", "Critical"]])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "fleet_status": {
                "total_vehicles": total_vehicles,
                "active_vehicles": active_vehicles,
                "idle_vehicles": total_vehicles - active_vehicles,
                "utilization_rate": active_vehicles / total_vehicles if total_vehicles else 0
            },
            "shipment_status": {
                "total": total_shipments,
                "delivered": delivered_shipments,
                "in_transit": len([s for s in self.shipments.values() 
                                  if s.status == OrderStatus.IN_TRANSIT]),
                "delayed": len([s for s in self.shipments.values() 
                               if s.is_delayed()])
            },
            "alerts": {
                "total_active": len(self.active_alerts),
                "critical": critical_alerts
            },
            "hot_zones": sorted(self.zone_heatmap.items(), 
                               key=lambda x: x[1], reverse=True)[:10]
        }


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("华运物流 - 实时物流追踪与调度系统")
    print("=" * 70)
    
    # 创建平台
    platform = LogisticsRealTimePlatform(
        platform_id="RT-HUAYUN-001",
        platform_name="华运物流实时平台"
    )
    
    # 1. 注册车辆
    print("\n[1] 注册运输车辆...")
    for i in range(5):
        vehicle = Vehicle(
            vehicle_id=f"VEH-{1000+i}",
            plate_number=f"京A{80000+i}",
            vehicle_type="HeavyTruck",
            capacity_kg=20000,
            capacity_cbm=80
        )
        platform.register_vehicle(vehicle)
    print(f"已注册 {len(platform.vehicles)} 辆车辆")
    
    # 2. 注册运单
    print("\n[2] 注册运单...")
    shipment1 = Shipment(
        shipment_id="SHIP-001",
        order_id="ORD-202502-001",
        origin={"lat": 39.9042, "lng": 116.4074, "address": "北京"},
        destination={"lat": 31.2304, "lng": 121.4737, "address": "上海"},
        cargo_info={"weight_kg": 5000, "volume_cbm": 20, "type": " Electronics"},
        planned_delivery_time=datetime.now() + timedelta(hours=18)
    )
    platform.register_shipment(shipment1)
    print(f"运单ID: {shipment1.shipment_id}")
    print(f"路线: {shipment1.origin['address']} -> {shipment1.destination['address']}")
    
    # 3. 智能调度
    print("\n[3] 智能调度...")
    vehicle = platform.optimize_dispatch(shipment1)
    if vehicle:
        print(f"分配车辆: {vehicle.vehicle_id}")
        print(f"车牌号: {vehicle.plate_number}")
        print(f"车辆状态: {vehicle.current_status.value}")
    
    # 4. 模拟GPS更新
    print("\n[4] 模拟GPS位置更新...")
    gps_message = {
        "type": "GPS_UPDATE",
        "vehicle_id": vehicle.vehicle_id,
        "lat": 39.9042,
        "lng": 116.4074,
        "speed": 80,
        "timestamp": datetime.now().isoformat()
    }
    platform.process_iot_message(gps_message)
    print(f"车辆位置已更新")
    
    # 5. 模拟温度监控（冷链）
    print("\n[5] 模拟冷链温度监控...")
    temp_message = {
        "type": "TEMPERATURE_UPDATE",
        "shipment_id": shipment1.shipment_id,
        "temperature": 12.5
    }
    platform.process_iot_message(temp_message)
    
    if platform.active_alerts:
        print(f"检测到 {len(platform.active_alerts)} 个预警")
        for alert in platform.active_alerts:
            print(f"  [{alert.severity}] {alert.message}")
    
    # 6. 延误风险检查
    print("\n[6] 延误风险检查...")
    # 更新车辆位置到远离目的地的位置
    vehicle.current_location = GPSPoint(
        latitude=35.0,  # 还在中间位置
        longitude=118.0,
        timestamp=datetime.now(),
        speed=60
    )
    
    delay_alerts = platform.check_delay_risks()
    if delay_alerts:
        print(f"检测到 {len(delay_alerts)} 个延误风险")
        for alert in delay_alerts:
            print(f"  - {alert.message}")
            print(f"    建议: {alert.suggested_action}")
    
    # 7. 实时仪表盘
    print("\n[7] 实时运营仪表盘...")
    dashboard = platform.get_realtime_dashboard()
    print(f"车队状态:")
    print(f"  总车辆: {dashboard['fleet_status']['total_vehicles']}")
    print(f"  运输中: {dashboard['fleet_status']['active_vehicles']}")
    print(f"  利用率: {dashboard['fleet_status']['utilization_rate']:.1%}")
    print(f"运单状态:")
    print(f"  总运单: {dashboard['shipment_status']['total']}")
    print(f"  延误: {dashboard['shipment_status']['delayed']}")
    print(f"预警状态:")
    print(f"  活跃预警: {dashboard['alerts']['total_active']}")
    print(f"  严重预警: {dashboard['alerts']['critical']}")
```

### 2.7 效果评估与ROI分析

**项目投入**：

| 投入类别 | 金额（万元） |
|---------|------------|
| IoT设备 | 2000 |
| 软件平台 | 800 |
| 云服务 | 400 |
| 实施服务 | 600 |
| **总投资** | **3800** |

**量化收益**：

| 收益类别 | 年收益（万元） |
|---------|--------------|
| 空驶率降低 | 4500 |
| 异常损失减少 | 1200 |
| 客户留存提升 | 800 |
| 运营效率提升 | 600 |
| **年总收益** | **7100** |

**ROI**：95%（年收益7100万 vs 投资3800万，回收期约6个月）

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 位置更新延迟 | 5分钟 | 10秒 | 30倍 |
| 空驶率 | 30% | 15% | -50% |
| 异常发现时间 | 2小时 | 3分钟 | 40倍 |
| 客户满意度 | 75% | 92% | +23% |

---

**创建时间**：2025-02-15
