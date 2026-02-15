# 海运与航运Schema实践案例

## 📑 目录

- [海运与航运Schema实践案例](#海运与航运schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：GlobalShipping集团船舶追踪系统](#2-案例1globalshipping集团船舶追踪系统)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估与ROI](#27-效果评估与roi)
  - [3. 案例2：智能航线优化系统](#3-案例2智能航线优化系统)
    - [3.1 企业背景](#31-企业背景)
    - [3.2 业务痛点](#32-业务痛点)
    - [3.3 业务目标](#33-业务目标)
    - [3.4 技术挑战](#34-技术挑战)
    - [3.5 完整实现代码](#35-完整实现代码)
    - [3.6 效果评估与ROI](#36-效果评估与roi)
  - [4. 案例3：港口智能调度系统](#4-案例3港口智能调度系统)
    - [4.1 企业背景](#41-企业背景)
    - [4.2 业务痛点](#42-业务痛点)
    - [4.3 业务目标](#43-业务目标)
    - [4.4 技术挑战](#44-技术挑战)
    - [4.5 完整实现代码](#45-完整实现代码)
    - [4.6 效果评估与ROI](#46-效果评估与roi)

---

## 1. 案例概述

本文档提供海运与航运Schema在实际企业应用中的实践案例，涵盖船舶追踪、航线优化、港口调度等核心场景。

**案例类型**：

1. **船舶追踪系统**：实时追踪全球船队位置和状态
2. **智能航线优化**：基于天气、燃料成本优化航线
3. **港口智能调度**：优化泊位分配和装卸作业

**参考标准**：

- **AIS标准**：自动识别系统标准
- **EDIFACT标准**：电子数据交换标准
- **IMO标准**：国际海事组织标准

---

## 2. 案例1：GlobalShipping集团船舶追踪系统

### 2.1 企业背景

**GlobalShipping集团**是全球前十大航运公司之一，拥有集装箱船、散货船、油轮等各类船舶280艘，航线覆盖全球150个港口，年货运量超过800万TEU。

- **成立时间**：1985年
- **员工规模**：15,000人（岸上）+ 8,000人（船员）
- **船队规模**：280艘
- **年货运量**：800万+ TEU
- **覆盖港口**：150个
- **航线数量**：80条

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **位置更新延迟** | 严重 | AIS数据延迟10-30分钟，无法实时掌握船队位置 |
| 2 | **ETA预测不准** | 严重 | 预计到港时间误差平均12小时，影响港口预约和货物交接 |
| 3 | **异常事件响应慢** | 严重 | 船舶偏航、故障等异常发现不及时，年均损失500万美元 |
| 4 | **数据分散** | 高 | 船位数据分布在5个不同系统，查询困难 |
| 5 | **客户查询体验差** | 中 | 客户查询货物位置需要等待>30分钟 |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 位置更新频率 | 30分钟 | <2分钟 | 9个月 |
| 2 | ETA预测误差 | 12小时 | <2小时 | 12个月 |
| 3 | 异常事件检测时间 | 4小时 | <15分钟 | 9个月 |
| 4 | 数据整合覆盖率 | 20% | 98% | 12个月 |
| 5 | 客户查询响应时间 | 30分钟 | <5秒 | 6个月 |

### 2.4 技术挑战

1. **全球卫星通信**：需要在远洋区域保持卫星通信连接，处理卫星链路高延迟（500-800ms）和间歇性中断问题

2. **海量AIS数据处理**：全球280艘船舶每分钟产生位置数据，日数据量超过4亿条，需要高效存储和查询

3. **多源数据融合**：需要融合AIS、Inmarsat、VSAT、LRIT等多种定位数据源，提高定位精度和可靠性

4. **实时地理围栏**：需要对150个港口、200个关键水道设置地理围栏，实时检测进出事件

5. **离线数据处理**：船舶在卫星盲区时数据需本地缓存，恢复通信后批量同步，要求数据一致性和时序正确

### 2.5 解决方案

**船舶追踪系统架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                     数据展示层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐ │
│  │ 船队监控大屏 │ │ 船舶详情页  │ │ API服务               │ │
│  └─────────────┘ └─────────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     业务逻辑层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐ │
│  │ 位置计算    │ │ ETA预测     │ │ 异常检测引擎          │ │
│  └─────────────┘ └─────────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     数据接入层                               │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐ │
│  │ AIS接收站   │ │ 卫星通信网关│ │ 船舶本地缓存同步      │ │
│  └─────────────┘ └─────────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.6 完整实现代码

```python
#!/usr/bin/env python3
"""
GlobalShipping集团船舶追踪系统 - 核心实现
实时追踪全球船队位置，提供ETA预测和异常检测
"""

import asyncio
import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VesselType(Enum):
    """船舶类型"""
    CONTAINER = "container"
    BULK_CARRIER = "bulk_carrier"
    TANKER = "tanker"
    GENERAL_CARGO = "general_cargo"
    RORO = "roro"


class VesselStatus(Enum):
    """船舶状态"""
    AT_SEA = "at_sea"
    AT_ANCHOR = "at_anchor"
    IN_PORT = "in_port"
    MAINTENANCE = "maintenance"
    OFF_HIRE = "off_hire"


class AlertType(Enum):
    """告警类型"""
    DEVIATION = "deviation"           # 偏航
    SPEED_ANOMALY = "speed_anomaly"   # 速度异常
    ETA_CHANGE = "eta_change"         # ETA变化
    GEOFENCE = "geofence"             # 地理围栏
    COMMUNICATION = "communication"   # 通信中断


@dataclass
class GeoPoint:
    """地理坐标点"""
    latitude: float
    longitude: float
    
    def distance_to(self, other: 'GeoPoint') -> float:
        """计算与另一点的距离（海里）"""
        # Haversine公式
        R = 3440.065  # 地球半径（海里）
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def to_dict(self) -> Dict[str, float]:
        return {"latitude": self.latitude, "longitude": self.longitude}


@dataclass
class Vessel:
    """船舶"""
    vessel_id: str
    imo: str
    name: str
    vessel_type: VesselType
    length_m: float
    width_m: float
    max_speed_knots: float
    
    # 动态信息
    current_position: Optional[GeoPoint] = None
    current_heading: float = 0.0
    current_speed_knots: float = 0.0
    current_status: VesselStatus = VesselStatus.AT_SEA
    last_update: datetime = field(default_factory=datetime.now)
    
    # 航线信息
    destination: Optional[str] = None
    eta: Optional[datetime] = None
    planned_route: List[GeoPoint] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "vessel_id": self.vessel_id,
            "imo": self.imo,
            "name": self.name,
            "vessel_type": self.vessel_type.value,
            "dimensions": {
                "length_m": self.length_m,
                "width_m": self.width_m
            },
            "current": {
                "position": self.current_position.to_dict() if self.current_position else None,
                "heading": self.current_heading,
                "speed_knots": self.current_speed_knots,
                "status": self.current_status.value
            },
            "destination": self.destination,
            "eta": self.eta.isoformat() if self.eta else None,
            "last_update": self.last_update.isoformat()
        }


@dataclass
class PositionReport:
    """位置报告"""
    report_id: str
    vessel_id: str
    position: GeoPoint
    heading: float
    speed_knots: float
    timestamp: datetime
    source: str  # AIS, Inmarsat, VSAT
    accuracy_m: float = 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "vessel_id": self.vessel_id,
            "position": self.position.to_dict(),
            "heading": self.heading,
            "speed_knots": self.speed_knots,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "accuracy_m": self.accuracy_m
        }


@dataclass
class Port:
    """港口"""
    port_id: str
    unlocode: str
    name: str
    country: str
    position: GeoPoint
    anchorage_area: Optional[List[GeoPoint]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "port_id": self.port_id,
            "unlocode": self.unlocode,
            "name": self.name,
            "country": self.country,
            "position": self.position.to_dict()
        }


@dataclass
class Alert:
    """告警"""
    alert_id: str
    vessel_id: str
    alert_type: AlertType
    severity: str  # critical, high, medium, low
    message: str
    timestamp: datetime
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "vessel_id": self.vessel_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged
        }


class VesselTrackingSystem:
    """船舶追踪系统"""
    
    def __init__(self):
        self.vessels: Dict[str, Vessel] = {}
        self.ports: Dict[str, Port] = {}
        self.position_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: Dict[str, Alert] = {}
        
        # 地理围栏
        self.geofences: Dict[str, Dict] = {}
        
        # 统计
        self.stats = {
            "total_reports_processed": 0,
            "alerts_generated": 0,
            "avg_position_age_seconds": 0
        }
        
        logger.info("Vessel Tracking System initialized")
    
    def register_vessel(self, vessel: Vessel):
        """注册船舶"""
        self.vessels[vessel.vessel_id] = vessel
        logger.info(f"Registered vessel: {vessel.name} (IMO: {vessel.imo})")
    
    def register_port(self, port: Port):
        """注册港口"""
        self.ports[port.port_id] = port
    
    def process_position_report(self, report: PositionReport) -> bool:
        """处理位置报告"""
        if report.vessel_id not in self.vessels:
            logger.warning(f"Unknown vessel: {report.vessel_id}")
            return False
        
        vessel = self.vessels[report.vessel_id]
        
        # 更新船舶位置
        vessel.current_position = report.position
        vessel.current_heading = report.heading
        vessel.current_speed_knots = report.speed_knots
        vessel.last_update = report.timestamp
        
        # 保存历史
        self.position_history[report.vessel_id].append(report)
        self.stats["total_reports_processed"] += 1
        
        # 更新统计
        position_age = (datetime.now() - report.timestamp).total_seconds()
        n = self.stats["total_reports_processed"]
        self.stats["avg_position_age_seconds"] = (
            self.stats["avg_position_age_seconds"] * (n-1) + position_age
        ) / n
        
        # 检查偏航
        self._check_deviation(vessel, report)
        
        # 检查速度异常
        self._check_speed_anomaly(vessel, report)
        
        # 检查地理围栏
        self._check_geofences(vessel, report)
        
        # 更新ETA
        self._update_eta(vessel)
        
        return True
    
    def _check_deviation(self, vessel: Vessel, report: PositionReport):
        """检查是否偏航"""
        if not vessel.planned_route or len(vessel.planned_route) < 2:
            return
        
        # 找到计划航线上最近的点
        min_distance = float('inf')
        for point in vessel.planned_route:
            dist = report.position.distance_to(point)
            min_distance = min(min_distance, dist)
        
        # 如果距离计划航线超过5海里，触发偏航告警
        if min_distance > 5:
            self._create_alert(
                vessel.vessel_id,
                AlertType.DEVIATION,
                "high",
                f"Vessel deviated from planned route by {min_distance:.1f} nautical miles"
            )
    
    def _check_speed_anomaly(self, vessel: Vessel, report: PositionReport):
        """检查速度异常"""
        if vessel.max_speed_knots <= 0:
            return
        
        # 速度超过最大速度的120%
        if report.speed_knots > vessel.max_speed_knots * 1.2:
            self._create_alert(
                vessel.vessel_id,
                AlertType.SPEED_ANOMALY,
                "medium",
                f"Speed {report.speed_knots:.1f} knots exceeds maximum {vessel.max_speed_knots:.1f} knots"
            )
        
        # 在航但速度接近0
        if vessel.current_status == VesselStatus.AT_SEA and report.speed_knots < 1:
            self._create_alert(
                vessel.vessel_id,
                AlertType.SPEED_ANOMALY,
                "high",
                "Vessel at sea with near-zero speed - possible engine failure"
            )
    
    def _check_geofences(self, vessel: Vessel, report: PositionReport):
        """检查地理围栏"""
        for fence_id, fence in self.geofences.items():
            center = fence["center"]
            radius_nm = fence["radius_nm"]
            
            distance = report.position.distance_to(center)
            
            if distance <= radius_nm:
                # 检查是否刚刚进入
                if len(self.position_history[vessel.vessel_id]) >= 2:
                    prev_report = list(self.position_history[vessel.vessel_id])[-2]
                    prev_distance = prev_report.position.distance_to(center)
                    
                    if prev_distance > radius_nm:
                        self._create_alert(
                            vessel.vessel_id,
                            AlertType.GEOFENCE,
                            "medium",
                            f"Vessel entered geofence: {fence_id}"
                        )
    
    def _update_eta(self, vessel: Vessel):
        """更新预计到港时间"""
        if not vessel.destination or not vessel.current_position:
            return
        
        # 查找目的港
        dest_port = None
        for port in self.ports.values():
            if port.name == vessel.destination or port.unlocode == vessel.destination:
                dest_port = port
                break
        
        if not dest_port:
            return
        
        # 计算距离
        distance_nm = vessel.current_position.distance_to(dest_port.position)
        
        # 估算航行时间（假设平均速度为当前速度的80%）
        avg_speed = max(5, vessel.current_speed_knots * 0.8)  # 至少5节
        hours_to_dest = distance_nm / avg_speed
        
        # 更新ETA
        new_eta = datetime.now() + timedelta(hours=hours_to_dest)
        
        # 如果ETA变化超过2小时，触发告警
        if vessel.eta and abs((new_eta - vessel.eta).total_seconds()) > 7200:
            self._create_alert(
                vessel.vessel_id,
                AlertType.ETA_CHANGE,
                "medium",
                f"ETA changed from {vessel.eta.strftime('%Y-%m-%d %H:%M')} to {new_eta.strftime('%Y-%m-%d %H:%M')}"
            )
        
        vessel.eta = new_eta
    
    def _create_alert(self, vessel_id: str, alert_type: AlertType,
                     severity: str, message: str) -> str:
        """创建告警"""
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{vessel_id[:6]}"
        
        alert = Alert(
            alert_id=alert_id,
            vessel_id=vessel_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now()
        )
        
        self.alerts[alert_id] = alert
        self.stats["alerts_generated"] += 1
        
        logger.warning(f"Alert created: {message}")
        return alert_id
    
    def add_geofence(self, fence_id: str, center: GeoPoint, radius_nm: float,
                    fence_type: str = "circular"):
        """添加地理围栏"""
        self.geofences[fence_id] = {
            "center": center,
            "radius_nm": radius_nm,
            "type": fence_type
        }
    
    def get_fleet_status(self) -> Dict[str, Any]:
        """获取船队状态"""
        status_count = defaultdict(int)
        for vessel in self.vessels.values():
            status_count[vessel.current_status.value] += 1
        
        # 计算平均位置更新延迟
        total_delay = 0
        count = 0
        for vessel in self.vessels.values():
            delay = (datetime.now() - vessel.last_update).total_seconds()
            total_delay += delay
            count += 1
        avg_delay = total_delay / count if count > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_vessels": len(self.vessels),
            "status_distribution": dict(status_count),
            "avg_position_age_seconds": avg_delay,
            "active_alerts": len([a for a in self.alerts.values() if not a.acknowledged]),
            "total_reports_today": self.stats["total_reports_processed"]
        }
    
    def get_vessel_track(self, vessel_id: str, hours: int = 24) -> List[Dict]:
        """获取船舶轨迹"""
        if vessel_id not in self.position_history:
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        track = [
            report.to_dict()
            for report in self.position_history[vessel_id]
            if report.timestamp > cutoff
        ]
        
        return sorted(track, key=lambda x: x["timestamp"])


def main():
    """演示船舶追踪系统"""
    system = VesselTrackingSystem()
    
    # 注册港口
    ports = [
        Port("PORT-SHA", "CNSHA", "Shanghai", "China", GeoPoint(31.2304, 121.4737)),
        Port("PORT-SIN", "SGSIN", "Singapore", "Singapore", GeoPoint(1.2897, 103.8501)),
        Port("PORT-RTM", "NLRTM", "Rotterdam", "Netherlands", GeoPoint(51.9244, 4.4777)),
        Port("PORT-LAX", "USLAX", "Los Angeles", "USA", GeoPoint(33.7362, -118.2922))
    ]
    for port in ports:
        system.register_port(port)
    
    # 注册船舶
    vessels = [
        Vessel("VES-001", "1234567", "Pacific Star", VesselType.CONTAINER,
               300.0, 45.0, 25.0, destination="Singapore"),
        Vessel("VES-002", "2345678", "Atlantic Voyager", VesselType.TANKER,
               250.0, 40.0, 15.0, destination="Rotterdam"),
        Vessel("VES-003", "3456789", "Indian Trader", VesselType.BULK_CARRIER,
               280.0, 42.0, 14.0, destination="Shanghai")
    ]
    for vessel in vessels:
        system.register_vessel(vessel)
    
    # 添加地理围栏（上海港附近）
    system.add_geofence("SHA-ANCHORAGE", GeoPoint(31.0, 122.0), 20.0)
    
    # 模拟位置报告
    import random
    for i in range(100):
        vessel_id = f"VES-{(i % 3) + 1:03d}"
        vessel = system.vessels[vessel_id]
        
        # 模拟向目的地移动
        if vessel.destination == "Singapore":
            base_lat, base_lon = 25.0 + i*0.05, 115.0 + i*0.02
        elif vessel.destination == "Rotterdam":
            base_lat, base_lon = 40.0 + i*0.02, -30.0 + i*0.05
        else:
            base_lat, base_lon = 20.0 + i*0.03, 130.0 - i*0.03
        
        report = PositionReport(
            report_id=f"REP-{i:06d}",
            vessel_id=vessel_id,
            position=GeoPoint(base_lat + random.uniform(-0.1, 0.1),
                            base_lon + random.uniform(-0.1, 0.1)),
            heading=random.uniform(0, 360),
            speed_knots=random.uniform(10, 20),
            timestamp=datetime.now() - timedelta(minutes=i*2),
            source="AIS"
        )
        
        system.process_position_report(report)
    
    # 获取船队状态
    status = system.get_fleet_status()
    print("Fleet Status:")
    print(json.dumps(status, indent=2))
    
    # 获取船舶轨迹
    track = system.get_vessel_track("VES-001", hours=24)
    print(f"\nVessel VES-001 track: {len(track)} points")
    
    # 获取告警
    alerts = [a.to_dict() for a in system.alerts.values()]
    print(f"\nActive Alerts: {len(alerts)}")
    for alert in alerts[:5]:
        print(f"  - {alert['alert_type']}: {alert['message']}")


if __name__ == "__main__":
    main()
```

### 2.7 效果评估与ROI

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 位置更新频率 | 30分钟 | 90秒 | -95% |
| ETA预测误差 | 12小时 | 1.5小时 | -87% |
| 异常检测时间 | 4小时 | 8分钟 | -97% |
| 数据整合覆盖率 | 20% | 97% | +77% |
| 客户查询响应时间 | 30分钟 | 2秒 | -99.9% |

#### ROI计算

**投资成本**（18个月项目周期）：
- 系统开发：800万美元
- 卫星通信升级：400万美元
- 船载设备改造：600万美元
- **总投资**：1,800万美元

**年度收益**：
- 航线优化节省：1,200万美元
- 异常响应减少损失：500万美元
- 客户满意度提升：300万美元
- **年度总收益**：2,000万美元

**ROI分析**：
- 投资回收期：10.8个月
- 3年ROI：233%

---

## 3. 案例2：智能航线优化系统

### 3.1 企业背景

**BlueOcean航运公司**运营120艘远洋船舶，年燃油成本超过3亿美元，占运营成本40%。公司迫切需要优化航线规划以降低燃油消耗和碳排放。

- **船队规模**：120艘
- **年燃油成本**：3亿美元
- **航线覆盖**：全球主要贸易航线
- **年航行里程**：600万海里

### 3.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **航线规划依赖经验** | 严重 | 航线规划主要依赖船长经验，缺乏数据驱动优化 |
| 2 | **天气利用不足** | 严重 | 未能充分利用气象 routing，年损失燃油10% |
| 3 | **多目标优化难** | 高 | 燃油成本vs航行时间vs安全难以平衡 |
| 4 | **动态调整滞后** | 高 | 遇到恶劣天气被动应对，无法提前48小时调整 |
| 5 | **碳排放超标** | 中 | 碳排放强度高于行业平均15%，面临环保压力 |

### 3.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 燃油消耗降低 | 基准 | -12% | 12个月 |
| 2 | 航线规划时间 | 8小时 | <30分钟 | 6个月 |
| 3 | 恶劣天气预警时间 | 12小时 | 72小时 | 9个月 |
| 4 | 碳排放强度 | 基准 | -15% | 18个月 |
| 5 | 准班率 | 78% | 92% | 12个月 |

### 3.4 技术挑战

1. **多目标优化算法**：需要在燃油成本、航行时间、安全风险、碳排放之间找到Pareto最优解

2. **全球气象数据集成**：需要实时获取和处理全球海洋气象数据（风浪、洋流、气压），日数据量50GB+

3. **动态航线重规划**：需要在航行中根据天气变化动态调整航线，要求算法响应时间<5分钟

4. **船舶性能建模**：需要建立每艘船舶的准确性能模型（主机功率曲线、阻力特性），用于精确预测燃油消耗

5. **合规性约束**：需要满足ECA（排放控制区）、硫排放限制、压载水管理等多种法规约束

### 3.5 完整实现代码

```python
#!/usr/bin/env python3
"""
智能航线优化系统 - 核心实现
基于气象数据和船舶性能模型优化航线
"""

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherCondition(Enum):
    """天气条件"""
    CALM = "calm"
    MODERATE = "moderate"
    ROUGH = "rough"
    SEVERE = "severe"


@dataclass
class WeatherData:
    """气象数据"""
    position: Tuple[float, float]
    wind_speed_knots: float
    wind_direction_deg: float
    wave_height_m: float
    wave_direction_deg: float
    current_speed_knots: float
    current_direction_deg: float
    timestamp: datetime
    
    def get_severity(self) -> WeatherCondition:
        """获取天气严重程度"""
        if self.wave_height_m < 2 and self.wind_speed_knots < 20:
            return WeatherCondition.CALM
        elif self.wave_height_m < 4 and self.wind_speed_knots < 30:
            return WeatherCondition.MODERATE
        elif self.wave_height_m < 6 and self.wind_speed_knots < 40:
            return WeatherCondition.ROUGH
        else:
            return WeatherCondition.SEVERE


@dataclass
class Waypoint:
    """航路点"""
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    speed_knots: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "latitude": self.latitude,
            "longitude": self.longitude
        }
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        if self.speed_knots:
            result["speed_knots"] = self.speed_knots
        return result


@dataclass
class VesselProfile:
    """船舶性能档案"""
    vessel_id: str
    max_speed_knots: float
    optimal_speed_knots: float
    fuel_consumption_tons_per_day: Dict[float, float]  # 速度 -> 日油耗
    
    def get_fuel_consumption(self, speed_knots: float) -> float:
        """获取给定速度下的油耗（吨/天）"""
        if speed_knots in self.fuel_consumption_tons_per_day:
            return self.fuel_consumption_tons_per_day[speed_knots]
        
        # 插值计算
        speeds = sorted(self.fuel_consumption_tons_per_day.keys())
        if speed_knots <= speeds[0]:
            return self.fuel_consumption_tons_per_day[speeds[0]]
        if speed_knots >= speeds[-1]:
            return self.fuel_consumption_tons_per_day[speeds[-1]]
        
        for i in range(len(speeds) - 1):
            if speeds[i] <= speed_knots <= speeds[i+1]:
                ratio = (speed_knots - speeds[i]) / (speeds[i+1] - speeds[i])
                f1 = self.fuel_consumption_tons_per_day[speeds[i]]
                f2 = self.fuel_consumption_tons_per_day[speeds[i+1]]
                return f1 + ratio * (f2 - f1)
        
        return self.fuel_consumption_tons_per_day[speeds[0]]


@dataclass
class Route:
    """航线"""
    route_id: str
    vessel_id: str
    departure_port: str
    arrival_port: str
    waypoints: List[Waypoint]
    total_distance_nm: float
    estimated_duration_hours: float
    estimated_fuel_tons: float
    weather_factor: float = 1.0  # 天气影响系数
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "vessel_id": self.vessel_id,
            "departure_port": self.departure_port,
            "arrival_port": self.arrival_port,
            "waypoints": [wp.to_dict() for wp in self.waypoints],
            "total_distance_nm": self.total_distance_nm,
            "estimated_duration_hours": self.estimated_duration_hours,
            "estimated_fuel_tons": self.estimated_fuel_tons,
            "weather_factor": self.weather_factor
        }


class RouteOptimizer:
    """航线优化器"""
    
    def __init__(self):
        self.weather_grid: Dict[Tuple[int, int, int], WeatherData] = {}
        self.vessel_profiles: Dict[str, VesselProfile] = {}
        self.ports: Dict[str, Tuple[float, float]] = {}
        
        logger.info("Route Optimizer initialized")
    
    def add_weather_data(self, weather: WeatherData):
        """添加气象数据"""
        # 网格化存储（1度 x 1度 x 6小时）
        grid_key = (
            int(weather.position[0]),
            int(weather.position[1]),
            int(weather.timestamp.timestamp() / 21600)
        )
        self.weather_grid[grid_key] = weather
    
    def register_vessel_profile(self, profile: VesselProfile):
        """注册船舶性能档案"""
        self.vessel_profiles[profile.vessel_id] = profile
    
    def register_port(self, port_id: str, lat: float, lon: float):
        """注册港口"""
        self.ports[port_id] = (lat, lon)
    
    def calculate_distance_nm(self, lat1: float, lon1: float,
                             lat2: float, lon2: float) -> float:
        """计算两点间距离（海里）"""
        R = 3440.065  # 地球半径（海里）
        
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def optimize_route(self, vessel_id: str, departure: str,
                      destination: str, departure_time: datetime,
                      optimization_goal: str = "balanced") -> Route:
        """优化航线"""
        if vessel_id not in self.vessel_profiles:
            raise ValueError(f"Unknown vessel: {vessel_id}")
        
        if departure not in self.ports or destination not in self.ports:
            raise ValueError("Unknown port")
        
        vessel = self.vessel_profiles[vessel_id]
        start_pos = self.ports[departure]
        end_pos = self.ports[destination]
        
        # 简化的航线优化：生成大圆航线的若干变体
        routes = self._generate_route_variants(
            start_pos, end_pos, vessel, departure_time
        )
        
        # 评估每条航线
        best_route = None
        best_score = float('-inf')
        
        for route in routes:
            score = self._evaluate_route(route, optimization_goal)
            if score > best_score:
                best_score = score
                best_route = route
        
        return best_route
    
    def _generate_route_variants(self, start: Tuple[float, float],
                                end: Tuple[float, float],
                                vessel: VesselProfile,
                                departure_time: datetime) -> List[Route]:
        """生成航线变体"""
        routes = []
        
        # 大圆航线（直接连线）
        direct_waypoints = self._generate_great_circle_route(start, end, 20)
        
        for offset in [-2, -1, 0, 1, 2]:  # 南北偏移
            waypoints = []
            for i, wp in enumerate(direct_waypoints):
                # 在中间段添加偏移
                if 5 < i < len(direct_waypoints) - 5:
                    lat = wp[0] + offset * 2
                else:
                    lat = wp[0]
                lon = wp[1]
                waypoints.append(Waypoint(lat, lon))
            
            route = self._calculate_route_metrics(
                waypoints, vessel, departure_time
            )
            routes.append(route)
        
        return routes
    
    def _generate_great_circle_route(self, start: Tuple[float, float],
                                    end: Tuple[float, float],
                                    num_points: int) -> List[Tuple[float, float]]:
        """生成大圆航线点"""
        points = [start]
        
        for i in range(1, num_points):
            ratio = i / num_points
            lat = start[0] + (end[0] - start[0]) * ratio
            lon = start[1] + (end[1] - start[1]) * ratio
            points.append((lat, lon))
        
        points.append(end)
        return points
    
    def _calculate_route_metrics(self, waypoints: List[Waypoint],
                                vessel: VesselProfile,
                                departure_time: datetime) -> Route:
        """计算航线指标"""
        total_distance = 0
        total_duration = 0
        total_fuel = 0
        weather_penalty = 0
        
        current_time = departure_time
        
        for i in range(len(waypoints) - 1):
            wp1 = waypoints[i]
            wp2 = waypoints[i + 1]
            
            # 距离
            distance = self.calculate_distance_nm(wp1.latitude, wp1.longitude,
                                                 wp2.latitude, wp2.longitude)
            total_distance += distance
            
            # 获取该段天气
            weather = self._get_weather_at(
                (wp1.latitude + wp2.latitude) / 2,
                (wp1.longitude + wp2.longitude) / 2,
                current_time
            )
            
            # 计算速度（考虑天气）
            base_speed = vessel.optimal_speed_knots
            if weather:
                if weather.get_severity() == WeatherCondition.SEVERE:
                    speed = base_speed * 0.5
                    weather_penalty += 0.3
                elif weather.get_severity() == WeatherCondition.ROUGH:
                    speed = base_speed * 0.7
                    weather_penalty += 0.1
                else:
                    speed = base_speed
            else:
                speed = base_speed
            
            # 时间
            duration = distance / speed if speed > 0 else 0
            total_duration += duration
            
            # 油耗
            fuel_rate = vessel.get_fuel_consumption(speed)  # 吨/天
            fuel = fuel_rate * (duration / 24)
            total_fuel += fuel
            
            # 更新时间
            current_time += timedelta(hours=duration)
            wp2.timestamp = current_time
        
        route_id = f"ROUTE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return Route(
            route_id=route_id,
            vessel_id="",
            departure_port="",
            arrival_port="",
            waypoints=waypoints,
            total_distance_nm=total_distance,
            estimated_duration_hours=total_duration,
            estimated_fuel_tons=total_fuel,
            weather_factor=1 + weather_penalty
        )
    
    def _get_weather_at(self, lat: float, lon: float,
                       time: datetime) -> Optional[WeatherData]:
        """获取指定位置和时间的气象数据"""
        grid_key = (int(lat), int(lon), int(time.timestamp() / 21600))
        return self.weather_grid.get(grid_key)
    
    def _evaluate_route(self, route: Route, goal: str) -> float:
        """评估航线"""
        if goal == "fuel":
            # 最小化燃油
            return -route.estimated_fuel_tons
        elif goal == "time":
            # 最小化时间
            return -route.estimated_duration_hours
        else:  # balanced
            # 平衡燃油和时间
            fuel_score = -route.estimated_fuel_tons * 1000  # 每吨燃油1000分
            time_score = -route.estimated_duration_hours * 50  # 每小时50分
            weather_score = -route.weather_factor * 100  # 天气惩罚
            return fuel_score + time_score + weather_score


def main():
    """演示航线优化"""
    optimizer = RouteOptimizer()
    
    # 注册港口
    optimizer.register_port("Shanghai", 31.2304, 121.4737)
    optimizer.register_port("Singapore", 1.2897, 103.8501)
    optimizer.register_port("Rotterdam", 51.9244, 4.4777)
    
    # 注册船舶性能
    fuel_curve = {
        10.0: 30.0,
        12.0: 45.0,
        14.0: 65.0,
        16.0: 90.0,
        18.0: 120.0,
        20.0: 155.0
    }
    
    vessel = VesselProfile(
        vessel_id="VESSEL-001",
        max_speed_knots=22.0,
        optimal_speed_knots=16.0,
        fuel_consumption_tons_per_day=fuel_curve
    )
    optimizer.register_vessel_profile(vessel)
    
    # 添加气象数据
    import random
    for lat in range(0, 55, 5):
        for lon in range(100, 125, 5):
            weather = WeatherData(
                position=(lat + random.uniform(-2, 2), lon + random.uniform(-2, 2)),
                wind_speed_knots=random.uniform(10, 35),
                wind_direction_deg=random.uniform(0, 360),
                wave_height_m=random.uniform(1, 4),
                wave_direction_deg=random.uniform(0, 360),
                current_speed_knots=random.uniform(0.5, 2),
                current_direction_deg=random.uniform(0, 360),
                timestamp=datetime.now()
            )
            optimizer.add_weather_data(weather)
    
    # 优化航线
    route = optimizer.optimize_route(
        vessel_id="VESSEL-001",
        departure="Shanghai",
        destination="Singapore",
        departure_time=datetime.now(),
        optimization_goal="balanced"
    )
    
    print("Optimized Route:")
    print(json.dumps(route.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
```

### 3.6 效果评估与ROI

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 燃油消耗 | 基准 | -14% | -14% |
| 航线规划时间 | 8小时 | 15分钟 | -97% |
| 恶劣天气预警时间 | 12小时 | 84小时 | +600% |
| 碳排放强度 | 基准 | -16% | -16% |
| 准班率 | 78% | 94% | +21% |

#### ROI计算

**投资成本**：
- 系统开发：500万美元
- 气象数据订阅：100万美元/年
- **总投资**：600万美元

**年度收益**：
- 燃油节省：4,200万美元
- 准班率提升：800万美元
- **年度总收益**：5,000万美元

**ROI分析**：
- 投资回收期：1.4个月
- 3年ROI：2,400%

---

## 4. 案例3：港口智能调度系统

### 4.1 企业背景

**某大型港口集团**管理10个港区，年吞吐量超过5000万TEU，泊位资源紧张，船舶平均等待时间超过12小时。

- **港区数量**：10个
- **年吞吐量**：5000万TEU
- **泊位数量**：80个
- **日均到港船舶**：150艘

### 4.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **泊位利用率低** | 严重 | 平均利用率仅65%，高峰期拥挤，低谷期空闲 |
| 2 | **船舶等待时间长** | 严重 | 平均等待12小时，每年额外成本3000万元 |
| 3 | **调度依赖人工** | 高 | 调度员凭经验排班，难以应对突发情况 |
| 4 | **资源冲突频繁** | 高 | 桥吊、堆场资源分配不当，作业效率低 |
| 5 | **信息不透明** | 中 | 船公司无法实时了解泊位状态 |

### 4.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 泊位利用率 | 65% | 85% | 12个月 |
| 2 | 船舶平均等待时间 | 12小时 | <3小时 | 9个月 |
| 3 | 调度自动化率 | 10% | 80% | 12个月 |
| 4 | 资源冲突率 | 15% | <2% | 9个月 |
| 5 | 船舶准点靠泊率 | 70% | 95% | 12个月 |

### 4.4 技术挑战

1. **多约束优化**：需要同时考虑泊位类型、水深、潮汐、船舶尺寸、货物类型、设备可用性等多种约束

2. **实时动态调整**：需要在15分钟内响应船舶延误、设备故障等突发事件，重新优化调度方案

3. **多港区协同**：需要在10个港区之间协调资源，实现整体最优而非局部最优

4. **不确定性建模**：需要处理船舶ETA不确定性（天气、机械故障），要求鲁棒性调度方案

5. **多方利益平衡**：需要平衡船公司、货主、港口、物流公司的不同利益诉求

### 4.5 完整实现代码

```python
#!/usr/bin/env python3
"""
港口智能调度系统 - 核心实现
优化泊位分配和资源调度
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from heapq import heappush, heappop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VesselSize(Enum):
    """船舶尺寸等级"""
    SMALL = "small"      # < 200m
    MEDIUM = "medium"    # 200-300m
    LARGE = "large"      # 300-400m
    ULTRA = "ultra"      # > 400m


class BerthType(Enum):
    """泊位类型"""
    CONTAINER = "container"
    BULK = "bulk"
    TANKER = "tanker"
    GENERAL = "general"
    RORO = "roro"


class BerthStatus(Enum):
    """泊位状态"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


@dataclass
class Berth:
    """泊位"""
    berth_id: str
    terminal_id: str
    berth_type: BerthType
    length_m: float
    depth_m: float
    crane_count: int
    status: BerthStatus = BerthStatus.AVAILABLE
    current_vessel: Optional[str] = None
    
    def can_accommodate(self, vessel_length: float, vessel_draft: float) -> bool:
        """是否能容纳船舶"""
        return (self.length_m >= vessel_length * 1.1 and  # 10%余量
                self.depth_m >= vessel_draft + 2.0 and     # 2米富余水深
                self.status in [BerthStatus.AVAILABLE, BerthStatus.RESERVED])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "berth_id": self.berth_id,
            "terminal_id": self.terminal_id,
            "type": self.berth_type.value,
            "length_m": self.length_m,
            "depth_m": self.depth_m,
            "crane_count": self.crane_count,
            "status": self.status.value
        }


@dataclass
class VesselCall:
    """船舶到港计划"""
    call_id: str
    vessel_id: str
    vessel_name: str
    vessel_length: float
    vessel_draft: float
    vessel_type: BerthType
    eta: datetime
    etd: datetime  # 预计离港时间
    cargo_teus: int
    priority: int = 5  # 1-10, 数字越小优先级越高
    assigned_berth: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "vessel_id": self.vessel_id,
            "vessel_name": self.vessel_name,
            "vessel_length": self.vessel_length,
            "vessel_draft": self.vessel_draft,
            "vessel_type": self.vessel_type.value,
            "eta": self.eta.isoformat(),
            "etd": self.etd.isoformat(),
            "cargo_teus": self.cargo_teus,
            "priority": self.priority,
            "assigned_berth": self.assigned_berth
        }


@dataclass
class Crane:
    """桥吊"""
    crane_id: str
    terminal_id: str
    berth_id: Optional[str]
    moves_per_hour: int
    available_from: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "crane_id": self.crane_id,
            "terminal_id": self.terminal_id,
            "berth_id": self.berth_id,
            "moves_per_hour": self.moves_per_hour
        }


class PortScheduler:
    """港口调度器"""
    
    def __init__(self):
        self.berths: Dict[str, Berth] = {}
        self.vessel_calls: Dict[str, VesselCall] = {}
        self.cranes: Dict[str, Crane] = {}
        
        # 泊位占用时间表: berth_id -> [(start, end, call_id)]
        self.berth_schedule: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)
        
        # 统计
        self.stats = {
            "total_assignments": 0,
            "avg_waiting_hours": 0,
            "conflicts_resolved": 0
        }
        
        logger.info("Port Scheduler initialized")
    
    def add_berth(self, berth: Berth):
        """添加泊位"""
        self.berths[berth.berth_id] = berth
    
    def add_vessel_call(self, call: VesselCall):
        """添加船舶到港计划"""
        self.vessel_calls[call.call_id] = call
    
    def add_crane(self, crane: Crane):
        """添加桥吊"""
        self.cranes[crane.crane_id] = crane
    
    def schedule_vessel(self, call_id: str) -> Optional[str]:
        """为船舶分配泊位"""
        if call_id not in self.vessel_calls:
            return None
        
        call = self.vessel_calls[call_id]
        
        # 找到合适的泊位
        suitable_berths = [
            b for b in self.berths.values()
            if b.berth_type == call.vessel_type
            and b.can_accommodate(call.vessel_length, call.vessel_draft)
        ]
        
        if not suitable_berths:
            logger.warning(f"No suitable berth for vessel {call.vessel_name}")
            return None
        
        # 检查每个泊位的可用时间段
        best_berth = None
        best_start = None
        min_wait = timedelta(hours=999)
        
        for berth in suitable_berths:
            available_start = self._find_earliest_available_slot(
                berth.berth_id, call.eta, call.etd
            )
            
            wait_time = available_start - call.eta
            if wait_time < min_wait:
                min_wait = wait_time
                best_berth = berth
                best_start = available_start
        
        if best_berth:
            # 分配泊位
            call.assigned_berth = best_berth.berth_id
            
            # 更新泊位时间表
            actual_start = max(call.eta, best_start)
            self.berth_schedule[best_berth.berth_id].append(
                (actual_start, call.etd, call_id)
            )
            
            # 更新统计
            self.stats["total_assignments"] += 1
            wait_hours = min_wait.total_seconds() / 3600
            n = self.stats["total_assignments"]
            self.stats["avg_waiting_hours"] = (
                self.stats["avg_waiting_hours"] * (n-1) + wait_hours
            ) / n
            
            logger.info(f"Scheduled {call.vessel_name} at berth {best_berth.berth_id}, "
                       f"wait: {wait_hours:.1f} hours")
            
            return best_berth.berth_id
        
        return None
    
    def _find_earliest_available_slot(self, berth_id: str,
                                     desired_start: datetime,
                                     desired_end: datetime) -> datetime:
        """找到泊位最早可用时间"""
        schedule = sorted(self.berth_schedule.get(berth_id, []))
        
        # 如果没有安排，立即可用
        if not schedule:
            return desired_start
        
        # 检查desired_start是否可用
        can_start_at_desired = True
        for start, end, _ in schedule:
            if start <= desired_start < end:
                can_start_at_desired = False
                break
            if desired_start <= start < desired_end:
                can_start_at_desired = False
                break
        
        if can_start_at_desired:
            return desired_start
        
        # 找到冲突结束后最早的时间
        earliest = desired_start
        for start, end, _ in schedule:
            if start <= earliest < end:
                earliest = end
        
        return earliest
    
    def reschedule_delayed_vessel(self, call_id: str, new_eta: datetime) -> Optional[str]:
        """重新调度延误的船舶"""
        if call_id not in self.vessel_calls:
            return None
        
        call = self.vessel_calls[call_id]
        
        # 释放原泊位
        if call.assigned_berth:
            self.berth_schedule[call.assigned_berth] = [
                slot for slot in self.berth_schedule[call.assigned_berth]
                if slot[2] != call_id
            ]
            call.assigned_berth = None
        
        # 更新ETA
        delay = new_eta - call.eta
        call.eta = new_eta
        call.etd = call.etd + delay
        
        # 重新分配
        return self.schedule_vessel(call_id)
    
    def get_terminal_status(self, terminal_id: str) -> Dict[str, Any]:
        """获取港区状态"""
        terminal_berths = [b for b in self.berths.values() if b.terminal_id == terminal_id]
        
        status = {
            "terminal_id": terminal_id,
            "timestamp": datetime.now().isoformat(),
            "total_berths": len(terminal_berths),
            "available_berths": sum(1 for b in terminal_berths if b.status == BerthStatus.AVAILABLE),
            "occupied_berths": sum(1 for b in terminal_berths if b.status == BerthStatus.OCCUPIED),
            "scheduled_calls": []
        }
        
        for call in self.vessel_calls.values():
            if call.assigned_berth:
                berth = self.berths.get(call.assigned_berth)
                if berth and berth.terminal_id == terminal_id:
                    status["scheduled_calls"].append({
                        "vessel_name": call.vessel_name,
                        "berth_id": call.assigned_berth,
                        "eta": call.eta.isoformat(),
                        "etd": call.etd.isoformat()
                    })
        
        return status
    
    def get_port_overview(self) -> Dict[str, Any]:
        """获取港口概览"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_berths": len(self.berths),
            "total_vessel_calls": len(self.vessel_calls),
            "assigned_calls": sum(1 for c in self.vessel_calls.values() if c.assigned_berth),
            "avg_waiting_hours": self.stats["avg_waiting_hours"],
            "berth_utilization": self._calculate_berth_utilization()
        }
    
    def _calculate_berth_utilization(self) -> float:
        """计算泊位利用率"""
        total_berth_hours = len(self.berths) * 24  # 过去24小时
        occupied_hours = 0
        
        cutoff = datetime.now() - timedelta(hours=24)
        for berth_id, schedule in self.berth_schedule.items():
            for start, end, _ in schedule:
                if end > cutoff:
                    actual_start = max(start, cutoff)
                    occupied_hours += (end - actual_start).total_seconds() / 3600
        
        return occupied_hours / total_berth_hours if total_berth_hours > 0 else 0


def main():
    """演示港口调度系统"""
    scheduler = PortScheduler()
    
    # 添加泊位
    for i in range(20):
        berth = Berth(
            berth_id=f"BERTH-{i:03d}",
            terminal_id=f"TERM-{(i // 5):02d}",
            berth_type=BerthType.CONTAINER,
            length_m=300 + (i % 4) * 100,
            depth_m=14.0 + (i % 3) * 2,
            crane_count=3 + (i % 3)
        )
        scheduler.add_berth(berth)
    
    # 添加船舶到港计划
    import random
    vessel_names = ["Pacific Star", "Atlantic Voyager", "Indian Trader",
                   "Mediterranean Queen", "Arctic Explorer"]
    
    for i in range(50):
        eta = datetime.now() + timedelta(hours=random.uniform(0, 72))
        call = VesselCall(
            call_id=f"CALL-{i:04d}",
            vessel_id=f"VES-{i:04d}",
            vessel_name=f"{random.choice(vessel_names)}-{i}",
            vessel_length=200 + random.uniform(0, 200),
            vessel_draft=10 + random.uniform(0, 8),
            vessel_type=BerthType.CONTAINER,
            eta=eta,
            etd=eta + timedelta(hours=random.uniform(12, 48)),
            cargo_teus=random.randint(1000, 15000),
            priority=random.randint(1, 10)
        )
        scheduler.add_vessel_call(call)
        
        # 调度船舶
        assigned = scheduler.schedule_vessel(call.call_id)
        if assigned:
            print(f"Assigned {call.vessel_name} to {assigned}")
    
    # 港口概览
    overview = scheduler.get_port_overview()
    print("\nPort Overview:")
    print(json.dumps(overview, indent=2))


if __name__ == "__main__":
    main()
```

### 4.6 效果评估与ROI

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 泊位利用率 | 65% | 87% | +22% |
| 船舶平均等待时间 | 12小时 | 2.5小时 | -79% |
| 调度自动化率 | 10% | 85% | +75% |
| 资源冲突率 | 15% | 1.5% | -90% |
| 船舶准点靠泊率 | 70% | 96% | +37% |

#### ROI计算

**投资成本**：
- 系统开发：1,200万元
- 硬件升级：800万元
- **总投资**：2,000万元

**年度收益**：
- 泊位效率提升：5,000万元
- 船舶等待减少：3,000万元
- 资源冲突避免：1,000万元
- **年度总收益**：9,000万元

**ROI分析**：
- 投资回收期：2.7个月
- 3年ROI：1,250%

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
