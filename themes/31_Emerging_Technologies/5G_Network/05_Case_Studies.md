# 5G网络Schema实践案例

## 📑 目录

- [5G网络Schema实践案例](#5g网络schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 企业背景](#2-企业背景)
  - [3. 业务痛点](#3-业务痛点)
  - [4. 业务目标](#4-业务目标)
  - [5. 技术挑战](#5-技术挑战)
  - [6. 案例1：智慧工厂5G专网](#6-案例1智慧工厂5g专网)
  - [7. 案例2：智慧港口远程操控](#7-案例2智慧港口远程操控)
  - [8. 案例3：车联网V2X应用](#8-案例3车联网v2x应用)
  - [9. Python代码实现](#9-python代码实现)
  - [10. 效果评估](#10-效果评估)
  - [11. 案例总结](#11-案例总结)

---

## 1. 案例概述

本文档提供**5G网络Schema的实际应用案例**，涵盖智慧工厂、智慧港口、车联网等领域。通过真实的行业场景，展示如何利用5G技术的大带宽、低延迟、广连接特性支撑数字化转型。

**案例类型**：
- 智慧工厂5G专网
- 智慧港口远程操控
- 车联网V2X应用

---

## 2. 企业背景

### 2.1 企业概况

**数联通信技术有限公司**（以下简称"数联通信"）成立于2016年，总部位于杭州，是国内领先的5G专网解决方案提供商。公司拥有工信部颁发的5G专网运营牌照，为制造业、港口、交通等行业提供5G网络规划、建设、运维一站式服务。

### 2.2 业务规模

| 指标 | 数值 |
|------|------|
| 年营收 | 15亿元 |
| 5G专网项目 | 100+个 |
| 服务客户 | 200+家 |
| 技术团队 | 800人 |
| 5G基站部署 | 10,000+个 |

### 2.3 业务领域

数联通信主要提供以下服务：
- **5G专网建设**：公网专用、专网专用等多种部署模式
- **网络切片服务**：端到端切片设计与交付
- **边缘计算集成**：5G MEC平台建设
- **行业解决方案**：针对特定场景的5G应用开发

---

## 3. 业务痛点

### 痛点1：工业WiFi不稳定

**问题描述**：传统工厂使用WiFi连接移动设备和AGV，存在信号覆盖盲区、切换掉线、同频干扰等问题，影响生产连续性。

**损失数据**：某工厂每月因网络问题导致停产损失约200万元。

### 痛点2：有线连接限制柔性生产

**问题描述**：工业设备通过有线网络连接，生产线改造时需要重新布线，周期长、成本高，难以支撑柔性生产需求。

**改造成本**：某汽车工厂生产线改造布线成本占总改造成本的30%。

### 痛点3：远程操控延迟高

**问题描述**：港口、矿山的远程操控通过4G或WiFi传输视频和控制信号，延迟在100ms以上，操作体验差且存在安全隐患。

**安全影响**：某港口因远程操控延迟导致集装箱碰撞事故。

### 痛点4：设备连接数受限

**问题描述**：工厂内传感器、仪表数量庞大，传统网络连接数受限，难以支撑大规模物联网部署。

**连接瓶颈**：单个WiFi AP最大连接数约50个，无法满足高密度场景。

### 痛点5：数据安全风险

**问题描述**：生产数据通过公网传输存在被截获风险，企业希望实现数据不出园区。

**合规要求**：部分军工、涉密企业要求数据完全物理隔离。

---

## 4. 业务目标

### 目标1：实现5G全连接工厂

建设覆盖全厂区的5G专网，实现设备全连接、数据全采集、业务全在线。

**关键指标**：
- 5G覆盖率：100%
- 设备连接数：10万+
- 网络可用性：99.999%

### 目标2：支撑毫秒级远程操控

提供端到端延迟低于10ms的5G网络，支撑远程操控、AR/VR等高实时性应用。

**关键指标**：
- 空口延迟：<5ms
- 端到端延迟：<10ms
- 抖动：<1ms

### 目标3：部署端到端网络切片

通过网络切片实现不同业务的资源隔离和SLA保障。

**关键指标**：
- 切片数量：10+个
- 切片部署时间：<1小时
- 切片隔离度：99.9%

### 目标4：构建5G+边缘计算平台

建设5G MEC平台，实现数据本地化处理，降低回传带宽需求。

**关键指标**：
- 边缘计算节点：50+个
- 本地数据处理率：90%
- MEC应用部署时间：<10分钟

### 目标5：实现网络自运维

基于AI实现网络自配置、自优化、自修复，降低运维成本。

**关键指标**：
- 故障预测准确率：>95%
- 自动优化成功率：>90%
- 运维人员减少：50%

---

## 5. 技术挑战

### 挑战1：工业环境适应性

**问题描述**：工业现场存在电磁干扰、粉尘、高温、震动等恶劣条件，对5G设备可靠性提出极高要求。

**技术难点**：
- 工业级5G基站和终端的设计
- 防爆、防尘、防腐蚀的防护等级
- 极端温度下的稳定运行

### 挑战2：多频段协同优化

**问题描述**：5G使用Sub-6GHz和毫米波多个频段，需要合理的频谱规划和干扰管理。

**技术难点**：
- 高低频段的协同覆盖
- 室内外场景的频谱分配
- 与现有WiFi、4G系统的共存

### 挑战3：端到端切片管理

**问题描述**：网络切片涉及无线、传输、核心网多个域，需要统一的管理编排系统。

**技术难点**：
- 跨域切片的协同编排
- 切片SLA的实时监控和保障
- 切片资源的动态调整

### 挑战4：精准定位服务

**问题描述**：工厂、港口等场景需要厘米级定位精度，5G原生定位能力需要增强。

**技术难点**：
- 5G+UWB/蓝牙的融合定位
- 多径环境下的定位精度优化
- 定位与通信的资源复用

### 挑战5：安全隔离与合规

**问题描述**：不同安全等级的业务需要物理或逻辑隔离，满足等保2.0和关基保护要求。

**技术难点**：
- 端到端安全隔离方案
- 零信任网络架构设计
- 安全审计与合规证明

---

## 6. 案例1：智慧工厂5G专网

### 6.1 案例背景

**问题**：建设覆盖全厂区的5G专网，支撑工业视觉质检、AGV调度、AR远程协助等应用。

**应用场景**：机器视觉检测、无线化产线、数字孪生、预测性维护。

### 6.2 Schema定义

**5G智慧工厂Schema**：

```dsl
5g_network SmartFactory_5G {
  network_name: "数联智慧工厂5G专网"
  deployment_mode: Private_Network  # 专网专用
  
  coverage_area: {
    production_floor: 50000,  # 平方米
    warehouse: 20000,
    office: 10000
  }
  
  network_slices: [
    URLLC_Slice {  # 超可靠低延迟通信
      latency: 10ms
      reliability: 99.999%
      applications: [AGV_Control, Remote_Control]
    },
    eMBB_Slice {  # 增强移动宽带
      bandwidth: 1Gbps
      applications: [Video_Inspection, AR_Assistance]
    },
    mMTC_Slice {  # 海量机器类通信
      connections: 100000
      applications: [Sensor_Monitoring, Asset_Tracking]
    }
  ]
  
  functions: [
    provisionSlice(slice_type: Slice_Type, requirements: SLA_Requirements): Slice_ID,
    registerDevice(device: UE_Device, slice_id: Slice_ID): Device_ID,
    allocateResources(slice_id: Slice_ID, resources: Resource_Request): Allocation_Result,
    monitorSLA(slice_id: Slice_ID): SLA_Metrics,
    optimizeCoverage(performance_data: Performance_Data): Optimization_Plan
  ]
  
  state: {
    base_stations: Map[BS_ID, Base_Station]
    devices: Map[Device_ID, UE_Device]
    slices: Map[Slice_ID, Network_Slice]
    mec_nodes: Map[MEC_ID, MEC_Node]
  }
  
  events: [
    SliceProvisioned(slice_id: Slice_ID, slice_type: Slice_Type),
    DeviceConnected(device_id: Device_ID, slice_id: Slice_ID),
    SLABreach(slice_id: Slice_ID, metric: String, actual_value: Float),
    HandoverCompleted(device_id: Device_ID, from_cell: Cell_ID, to_cell: Cell_ID)
  ]
}
```

---

## 7. 案例2：智慧港口远程操控

### 7.1 案例背景

**问题**：通过5G网络实现港口龙门吊、岸桥的远程操控，降低司机作业强度，提升作业效率和安全性。

**应用场景**：龙门吊远程操控、岸桥远程操控、无人集卡调度、智能理货。

### 7.2 Schema定义

**5G智慧港口Schema**：

```dsl
5g_network SmartPort_5G {
  network_name: "数联智慧港口5G专网"
  deployment_mode: Hybrid_Public_Private  # 公网专用
  
  coverage_area: {
    container_yard: 2000000,  # 平方米
    berth_area: 500000,
    control_center: 5000
  }
  
  latency_requirements: {
    remote_control: 20ms,      # 远程操控
    video_transmission: 50ms,  # 视频回传
    fleet_management: 100ms    # 车队管理
  }
  
  functions: [
    establishControlSession(operator: Operator_ID, equipment: Equipment_ID): Session_ID,
    transmitControlCommand(session_id: Session_ID, command: Control_Command): Acknowledgment,
    receiveVideoFeed(equipment_id: Equipment_ID): Video_Stream,
    locateEquipment(equipment_id: Equipment_ID): GPS_Coordinates,
    optimizeFleetRoutes(fleet: Equipment[], tasks: Task[]): Route_Plan
  ]
  
  state: {
    active_sessions: Map[Session_ID, Control_Session]
    equipment_positions: Map[Equipment_ID, Position]
    video_streams: Map[Camera_ID, Stream_Config]
    fleet_status: Map[Vehicle_ID, Vehicle_Status]
  }
  
  events: [
    ControlSessionStarted(session_id: Session_ID, operator: String, equipment: String),
    CommandExecuted(session_id: Session_ID, command: String, latency_ms: Float),
    VideoFrameDropped(camera_id: String, timestamp: Timestamp),
    EquipmentProximityAlert(equipment1: String, equipment2: String, distance: Float)
  ]
}
```

---

## 8. 案例3：车联网V2X应用

### 8.1 案例背景

**问题**：建设车路协同的5G+V2X网络，支撑自动驾驶、交通优化、安全预警等应用。

**应用场景**：红绿灯信息推送、碰撞预警、车辆编队行驶、自动泊车。

### 8.2 Schema定义

**5G车联网Schema**：

```dsl
5g_network ConnectedVehicle_5G {
  network_name: "数联车联网5G平台"
  v2x_mode: PC5_Mode  # 直连通信模式
  
  v2x_services: [
    V2V_Service {  # 车对车
      latency: 10ms
      applications: [Collision_Warning, Platooning]
    },
    V2I_Service {  # 车对基础设施
      latency: 20ms
      applications: [Signal_Phase_Timing, Road_Hazard_Warning]
    },
    V2P_Service {  # 车对行人
      latency: 50ms
      applications: [Pedestrian_Collision_Warning]
    },
    V2N_Service {  # 车对网络
      latency: 100ms
      applications: [Traffic_Optimization, Entertainment]
    }
  ]
  
  functions: [
    broadcastBSM(vehicle: Vehicle_ID, bsm: Basic_Safety_Message),
    subscribeRSI(service: V2X_Service, location: Geo_Coordinates): Subscription_ID,
    transmitSPAT(intersection: Intersection_ID, spat: Signal_Phase_Timing),
    processCAM(message: Cooperative_Awareness_Message): Traffic_State,
    provideDENM(event: Detected_Event, location: Geo_Area): DENM_ID
  ]
  
  state: {
    vehicles: Map[Vehicle_ID, Vehicle_State]
    roadside_units: Map[RSU_ID, RSU_Status]
    traffic_signals: Map[Intersection_ID, Signal_Status]
    v2x_subscriptions: Map[Subscription_ID, Subscription_Info]
  }
  
  events: [
    BSMReceived(vehicle_id: String, position: Geo_Coordinates, speed: Float),
    CollisionRiskDetected(vehicle1: String, vehicle2: String, ttc: Float),
    EmergencyVehicleApproaching(vehicle_id: String, route: Geo_Coordinates[]),
    RoadworkWarningPosted(location: Geo_Area, duration: Duration)
  ]
}
```

---

## 9. Python代码实现

### 9.1 完整系统实现

```python
"""
5G网络管理平台 - Python实现
包含：网络切片管理、设备接入控制、SLA监控、定位服务
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Set
from enum import Enum
import logging
from abc import ABC, abstractmethod
import math
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SliceType(Enum):
    """切片类型"""
    URLLC = "uRLLC"  # 超可靠低延迟
    EMBB = "eMBB"    # 增强移动宽带
    MMTC = "mMTC"    # 海量机器类通信


class DeviceType(Enum):
    """设备类型"""
    MOBILE_PHONE = "mobile_phone"
    IOT_SENSOR = "iot_sensor"
    INDUSTRAL_CAMERA = "industrial_camera"
    AGV = "agv"
    ROBOT = "robot"
    VEHICLE = "vehicle"
    RSU = "rsu"


class ConnectionStatus(Enum):
    """连接状态"""
    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    HANDOVER = "handover"
    DISCONNECTED = "disconnected"


@dataclass
class SLARequirements:
    """SLA需求"""
    latency_ms: float = 20.0
    bandwidth_mbps: float = 100.0
    reliability_percent: float = 99.9
    jitter_ms: float = 1.0
    packet_loss_percent: float = 0.01


@dataclass
class NetworkSlice:
    """网络切片"""
    slice_id: str
    name: str
    slice_type: SliceType
    requirements: SLARequirements
    allocated_resources: Dict[str, Any] = field(default_factory=dict)
    connected_devices: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    status: str = "active"
    
    def to_dict(self) -> Dict:
        return {
            "slice_id": self.slice_id,
            "name": self.name,
            "type": self.slice_type.value,
            "requirements": asdict(self.requirements),
            "device_count": len(self.connected_devices),
            "status": self.status
        }


@dataclass
class BaseStation:
    """5G基站"""
    bs_id: str
    name: str
    location: Tuple[float, float]
    coverage_radius_m: float = 500.0
    frequency_ghz: float = 3.5
    bandwidth_mhz: float = 100.0
    max_connections: int = 1000
    connected_devices: int = 0
    tx_power_dbm: float = 46.0
    status: str = "active"
    
    def calculate_signal_strength(self, device_location: Tuple[float, float]) -> float:
        """计算信号强度（简化路径损耗模型）"""
        distance = self._calculate_distance(device_location)
        if distance > self.coverage_radius_m:
            return -120.0  # 无信号
        
        # 简化自由空间路径损耗模型
        path_loss = 20 * math.log10(distance) + 20 * math.log10(self.frequency_ghz) + 32.45
        rssi = self.tx_power_dbm - path_loss
        return rssi
    
    def _calculate_distance(self, point: Tuple[float, float]) -> float:
        """计算两点间距离（米）"""
        lat1, lon1 = self.location
        lat2, lon2 = point
        
        # 简化计算，假设1度约等于111公里
        dx = (lon2 - lon1) * 111000 * math.cos(math.radians(lat1))
        dy = (lat2 - lat1) * 111000
        return math.sqrt(dx**2 + dy**2)


@dataclass
class UEDevice:
    """用户设备"""
    device_id: str
    name: str
    device_type: DeviceType
    imei: str
    imsi: str
    current_slice: Optional[str] = None
    connected_bs: Optional[str] = None
    location: Optional[Tuple[float, float]] = None
    status: ConnectionStatus = ConnectionStatus.IDLE
    ip_address: Optional[str] = None
    connected_at: Optional[float] = None
    data_usage_mb: float = 0.0
    
    def connect(self, slice_id: str, bs_id: str, ip: str):
        """连接网络"""
        self.current_slice = slice_id
        self.connected_bs = bs_id
        self.ip_address = ip
        self.status = ConnectionStatus.CONNECTED
        self.connected_at = time.time()
    
    def disconnect(self):
        """断开连接"""
        self.current_slice = None
        self.connected_bs = None
        self.ip_address = None
        self.status = ConnectionStatus.DISCONNECTED


@dataclass
class MECNode:
    """MEC边缘计算节点"""
    mec_id: str
    name: str
    location: Tuple[float, float]
    connected_bs: List[str] = field(default_factory=list)
    cpu_cores: int = 32
    memory_gb: int = 128
    storage_tb: float = 10.0
    deployed_apps: List[str] = field(default_factory=list)
    latency_to_core_ms: float = 5.0
    
    def get_available_resources(self) -> Dict[str, float]:
        """获取可用资源（简化）"""
        return {
            "cpu_percent": 100 - len(self.deployed_apps) * 5,
            "memory_gb": self.memory_gb - len(self.deployed_apps) * 2,
            "storage_tb": self.storage_tb - len(self.deployed_apps) * 0.5
        }


class NetworkSliceManager:
    """网络切片管理器"""
    
    def __init__(self):
        self.slices: Dict[str, NetworkSlice] = {}
        self.slice_counter = 0
    
    def provision_slice(self, name: str, slice_type: SliceType, 
                       requirements: SLARequirements) -> NetworkSlice:
        """创建网络切片"""
        self.slice_counter += 1
        slice_id = f"slice-{self.slice_counter:04d}"
        
        # 根据SLA需求分配资源
        allocated_resources = self._allocate_resources(slice_type, requirements)
        
        slice_obj = NetworkSlice(
            slice_id=slice_id,
            name=name,
            slice_type=slice_type,
            requirements=requirements,
            allocated_resources=allocated_resources
        )
        
        self.slices[slice_id] = slice_obj
        
        logger.info(f"网络切片 {slice_id} ({name}) 已创建，类型: {slice_type.value}")
        logger.info(f"  延迟要求: {requirements.latency_ms}ms, 带宽: {requirements.bandwidth_mbps}Mbps")
        
        return slice_obj
    
    def _allocate_resources(self, slice_type: SliceType, 
                           requirements: SLARequirements) -> Dict[str, Any]:
        """为切片分配资源"""
        resources = {
            "prb_percent": 20,  # 物理资源块百分比
            "cpu_percent": 25,
            "memory_gb": 8
        }
        
        if slice_type == SliceType.URLLC:
            resources["prb_percent"] = 30  # uRLLC需要更多资源保障
            resources["priority"] = 10
        elif slice_type == SliceType.EMBB:
            resources["prb_percent"] = 50  # eMBB需要大带宽
            resources["priority"] = 5
        elif slice_type == SliceType.MMTC:
            resources["prb_percent"] = 20  # mMTC连接数多但带宽小
            resources["priority"] = 3
        
        return resources
    
    def get_slice(self, slice_id: str) -> Optional[NetworkSlice]:
        """获取切片信息"""
        return self.slices.get(slice_id)
    
    def list_slices(self, slice_type: Optional[SliceType] = None) -> List[NetworkSlice]:
        """列出切片"""
        slices = list(self.slices.values())
        if slice_type:
            slices = [s for s in slices if s.slice_type == slice_type]
        return slices
    
    def delete_slice(self, slice_id: str) -> bool:
        """删除切片"""
        if slice_id in self.slices:
            del self.slices[slice_id]
            logger.info(f"网络切片 {slice_id} 已删除")
            return True
        return False
    
    def add_device_to_slice(self, slice_id: str, device_id: str) -> bool:
        """将设备添加到切片"""
        slice_obj = self.slices.get(slice_id)
        if not slice_obj:
            return False
        
        if device_id not in slice_obj.connected_devices:
            slice_obj.connected_devices.append(device_id)
        
        return True


class BaseStationManager:
    """基站管理器"""
    
    def __init__(self):
        self.base_stations: Dict[str, BaseStation] = {}
        self.cell_id_counter = 0
    
    def deploy_base_station(self, name: str, location: Tuple[float, float],
                           frequency_ghz: float = 3.5,
                           coverage_radius_m: float = 500.0) -> BaseStation:
        """部署基站"""
        self.cell_id_counter += 1
        bs_id = f"BS-{self.cell_id_counter:04d}"
        
        bs = BaseStation(
            bs_id=bs_id,
            name=name,
            location=location,
            frequency_ghz=frequency_ghz,
            coverage_radius_m=coverage_radius_m
        )
        
        self.base_stations[bs_id] = bs
        logger.info(f"基站 {bs_id} ({name}) 已部署在 {location}")
        
        return bs
    
    def find_best_base_station(self, device_location: Tuple[float, float],
                               min_rssi: float = -100.0) -> Optional[BaseStation]:
        """查找最佳基站"""
        best_bs = None
        best_rssi = min_rssi
        
        for bs in self.base_stations.values():
            if bs.status != "active":
                continue
            
            rssi = bs.calculate_signal_strength(device_location)
            if rssi > best_rssi:
                best_rssi = rssi
                best_bs = bs
        
        return best_bs
    
    def get_coverage_map(self) -> Dict[str, Any]:
        """获取覆盖地图"""
        return {
            bs_id: {
                "location": bs.location,
                "radius": bs.coverage_radius_m,
                "frequency": bs.frequency_ghz,
                "connected_devices": bs.connected_devices
            }
            for bs_id, bs in self.base_stations.items()
        }


class DeviceManager:
    """设备管理器"""
    
    def __init__(self, slice_manager: NetworkSliceManager, 
                 bs_manager: BaseStationManager):
        self.slice_manager = slice_manager
        self.bs_manager = bs_manager
        self.devices: Dict[str, UEDevice] = {}
        self.ip_pool = self._generate_ip_pool()
    
    def _generate_ip_pool(self) -> List[str]:
        """生成IP地址池"""
        return [f"10.0.0.{i}" for i in range(2, 254)]
    
    def register_device(self, name: str, device_type: DeviceType,
                       imei: str, imsi: str) -> UEDevice:
        """注册设备"""
        device_id = f"UE-{uuid.uuid4().hex[:8]}"
        
        device = UEDevice(
            device_id=device_id,
            name=name,
            device_type=device_type,
            imei=imei,
            imsi=imsi
        )
        
        self.devices[device_id] = device
        logger.info(f"设备 {device_id} ({name}) 已注册")
        
        return device
    
    def connect_device(self, device_id: str, slice_id: str,
                      location: Tuple[float, float]) -> bool:
        """连接设备到网络"""
        device = self.devices.get(device_id)
        if not device:
            logger.error(f"设备 {device_id} 不存在")
            return False
        
        slice_obj = self.slice_manager.get_slice(slice_id)
        if not slice_obj:
            logger.error(f"切片 {slice_id} 不存在")
            return False
        
        # 查找最佳基站
        bs = self.bs_manager.find_best_base_station(location)
        if not bs:
            logger.error(f"设备 {device_id} 位置无5G覆盖")
            return False
        
        # 分配IP
        if not self.ip_pool:
            logger.error("IP地址池耗尽")
            return False
        
        ip = self.ip_pool.pop(0)
        
        # 连接设备
        device.location = location
        device.connect(slice_id, bs.bs_id, ip)
        bs.connected_devices += 1
        
        # 添加到切片
        self.slice_manager.add_device_to_slice(slice_id, device_id)
        
        logger.info(f"设备 {device_id} 已连接到切片 {slice_id} (基站: {bs.bs_id})")
        
        return True
    
    def disconnect_device(self, device_id: str):
        """断开设备连接"""
        device = self.devices.get(device_id)
        if not device or device.status != ConnectionStatus.CONNECTED:
            return
        
        # 释放IP
        if device.ip_address:
            self.ip_pool.append(device.ip_address)
        
        # 更新基站计数
        if device.connected_bs:
            bs = self.bs_manager.base_stations.get(device.connected_bs)
            if bs:
                bs.connected_devices = max(0, bs.connected_devices - 1)
        
        device.disconnect()
        logger.info(f"设备 {device_id} 已断开连接")
    
    def handover(self, device_id: str, new_location: Tuple[float, float]) -> bool:
        """执行切换"""
        device = self.devices.get(device_id)
        if not device or device.status != ConnectionStatus.CONNECTED:
            return False
        
        device.status = ConnectionStatus.HANDOVER
        
        # 查找新的最佳基站
        new_bs = self.bs_manager.find_best_base_station(new_location)
        if not new_bs or new_bs.bs_id == device.connected_bs:
            device.status = ConnectionStatus.CONNECTED
            return False
        
        # 执行切换
        old_bs_id = device.connected_bs
        
        # 更新旧基站计数
        old_bs = self.bs_manager.base_stations.get(old_bs_id)
        if old_bs:
            old_bs.connected_devices = max(0, old_bs.connected_devices - 1)
        
        # 更新设备信息
        device.connected_bs = new_bs.bs_id
        device.location = new_location
        new_bs.connected_devices += 1
        device.status = ConnectionStatus.CONNECTED
        
        logger.info(f"设备 {device_id} 从 {old_bs_id} 切换到 {new_bs.bs_id}")
        
        return True
    
    def get_device_stats(self) -> Dict[str, Any]:
        """获取设备统计"""
        total = len(self.devices)
        connected = sum(1 for d in self.devices.values() 
                       if d.status == ConnectionStatus.CONNECTED)
        
        by_type = {}
        for device in self.devices.values():
            type_name = device.device_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        return {
            "total_devices": total,
            "connected_devices": connected,
            "available_ips": len(self.ip_pool),
            "by_type": by_type
        }


class SLAMonitor:
    """SLA监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict]] = {}
        self.alerts: List[Dict] = []
    
    def record_metric(self, slice_id: str, metric_type: str, value: float):
        """记录指标"""
        if slice_id not in self.metrics:
            self.metrics[slice_id] = []
        
        self.metrics[slice_id].append({
            "type": metric_type,
            "value": value,
            "timestamp": time.time()
        })
        
        # 保留最近100条记录
        self.metrics[slice_id] = self.metrics[slice_id][-100:]
    
    def check_sla_compliance(self, slice_obj: NetworkSlice) -> Dict[str, Any]:
        """检查SLA合规性"""
        slice_id = slice_obj.slice_id
        slice_metrics = self.metrics.get(slice_id, [])
        
        if not slice_metrics:
            return {"status": "no_data", "violations": []}
        
        violations = []
        
        # 检查延迟
        latency_metrics = [m for m in slice_metrics if m["type"] == "latency"]
        if latency_metrics:
            avg_latency = np.mean([m["value"] for m in latency_metrics[-10:]])
            if avg_latency > slice_obj.requirements.latency_ms:
                violations.append({
                    "metric": "latency",
                    "required": slice_obj.requirements.latency_ms,
                    "actual": avg_latency
                })
        
        # 检查带宽
        bandwidth_metrics = [m for m in slice_metrics if m["type"] == "bandwidth"]
        if bandwidth_metrics:
            avg_bandwidth = np.mean([m["value"] for m in bandwidth_metrics[-10:]])
            if avg_bandwidth < slice_obj.requirements.bandwidth_mbps * 0.9:
                violations.append({
                    "metric": "bandwidth",
                    "required": slice_obj.requirements.bandwidth_mbps,
                    "actual": avg_bandwidth
                })
        
        status = "compliant" if not violations else "violated"
        
        return {
            "status": status,
            "violations": violations,
            "slice_id": slice_id
        }


class V2XService:
    """V2X服务"""
    
    def __init__(self):
        self.vehicles: Dict[str, Dict] = {}
        self.rsus: Dict[str, Dict] = {}
        self.v2x_messages: List[Dict] = []
    
    def register_vehicle(self, vehicle_id: str, vehicle_type: str) -> Dict:
        """注册车辆"""
        self.vehicles[vehicle_id] = {
            "vehicle_id": vehicle_id,
            "type": vehicle_type,
            "position": None,
            "speed": 0.0,
            "heading": 0.0,
            "status": "idle"
        }
        logger.info(f"车辆 {vehicle_id} 已注册V2X服务")
        return self.vehicles[vehicle_id]
    
    def update_vehicle_state(self, vehicle_id: str, position: Tuple[float, float],
                            speed: float, heading: float):
        """更新车辆状态"""
        if vehicle_id not in self.vehicles:
            return
        
        vehicle = self.vehicles[vehicle_id]
        vehicle["position"] = position
        vehicle["speed"] = speed
        vehicle["heading"] = heading
        
        # 广播BSM消息
        self._broadcast_bsm(vehicle_id, position, speed)
    
    def _broadcast_bsm(self, vehicle_id: str, position: Tuple[float, float], speed: float):
        """广播基本安全消息"""
        bsm = {
            "msg_type": "BSM",
            "vehicle_id": vehicle_id,
            "timestamp": time.time(),
            "position": position,
            "speed": speed,
            "transmission_mode": "PC5"  # 直连通信
        }
        self.v2x_messages.append(bsm)
    
    def check_collision_risk(self, vehicle_id: str) -> List[Dict]:
        """检查碰撞风险"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle or not vehicle["position"]:
            return []
        
        risks = []
        for other_id, other in self.vehicles.items():
            if other_id == vehicle_id or not other["position"]:
                continue
            
            # 计算距离
            dist = self._calculate_distance(vehicle["position"], other["position"])
            
            # 计算TTC (Time To Collision)
            relative_speed = abs(vehicle["speed"] - other["speed"])
            if relative_speed > 0:
                ttc = dist / relative_speed
                if ttc < 3.0:  # 小于3秒认为有风险
                    risks.append({
                        "vehicle_id": other_id,
                        "distance_m": dist,
                        "ttc_seconds": ttc,
                        "risk_level": "high" if ttc < 1.5 else "medium"
                    })
        
        return risks
    
    def _calculate_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """计算两点距离（简化）"""
        lat1, lon1 = p1
        lat2, lon2 = p2
        dx = (lon2 - lon1) * 111000 * math.cos(math.radians(lat1))
        dy = (lat2 - lat1) * 111000
        return math.sqrt(dx**2 + dy**2)


# 示例用法
def main():
    """主函数示例"""
    print("=" * 70)
    print("5G网络管理平台演示")
    print("=" * 70)
    
    # 初始化管理器
    slice_manager = NetworkSliceManager()
    bs_manager = BaseStationManager()
    device_manager = DeviceManager(slice_manager, bs_manager)
    sla_monitor = SLAMonitor()
    v2x_service = V2XService()
    
    # ==================== 1. 创建网络切片 ====================
    print("\n1. 创建5G网络切片")
    print("-" * 70)
    
    # uRLLC切片 - 用于工业控制
    urllc_slice = slice_manager.provision_slice(
        name="工业控制切片",
        slice_type=SliceType.URLLC,
        requirements=SLARequirements(
            latency_ms=10,
            bandwidth_mbps=50,
            reliability_percent=99.999
        )
    )
    
    # eMBB切片 - 用于视频传输
    embb_slice = slice_manager.provision_slice(
        name="视频监控切片",
        slice_type=SliceType.EMBB,
        requirements=SLARequirements(
            latency_ms=50,
            bandwidth_mbps=1000,
            reliability_percent=99.9
        )
    )
    
    # mMTC切片 - 用于传感器
    mmtc_slice = slice_manager.provision_slice(
        name="物联网切片",
        slice_type=SliceType.MMTC,
        requirements=SLARequirements(
            latency_ms=1000,
            bandwidth_mbps=1,
            reliability_percent=99
        )
    )
    
    print(f"已创建 {len(slice_manager.slices)} 个网络切片")
    
    # ==================== 2. 部署基站 ====================
    print("\n2. 部署5G基站")
    print("-" * 70)
    
    # 在工厂区域部署基站
    factory_location = (31.2304, 121.4737)
    for i in range(4):
        bs = bs_manager.deploy_base_station(
            name=f"工厂基站-{i+1}",
            location=(factory_location[0] + i*0.005, factory_location[1] + i*0.003),
            frequency_ghz=3.5,
            coverage_radius_m=500
        )
    
    coverage = bs_manager.get_coverage_map()
    print(f"已部署 {len(coverage)} 个基站")
    
    # ==================== 3. 注册并连接设备 ====================
    print("\n3. 注册并连接设备")
    print("-" * 70)
    
    # 注册AGV
    agvs = []
    for i in range(5):
        agv = device_manager.register_device(
            name=f"AGV-{i+1}",
            device_type=DeviceType.AGV,
            imei=f"860000000000{i:03d}",
            imsi=f"460000000000{i:03d}"
        )
        agvs.append(agv)
        
        # 连接到uRLLC切片
        device_manager.connect_device(
            device_id=agv.device_id,
            slice_id=urllc_slice.slice_id,
            location=(factory_location[0] + i*0.001, factory_location[1])
        )
    
    # 注册工业相机
    cameras = []
    for i in range(3):
        camera = device_manager.register_device(
            name=f"工业相机-{i+1}",
            device_type=DeviceType.INDUSTRAL_CAMERA,
            imei=f"860000000010{i:03d}",
            imsi=f"460000000010{i:03d}"
        )
        cameras.append(camera)
        
        # 连接到eMBB切片
        device_manager.connect_device(
            device_id=camera.device_id,
            slice_id=embb_slice.slice_id,
            location=(factory_location[0] + 0.002, factory_location[1] + i*0.001)
        )
    
    # 注册传感器
    sensors = []
    for i in range(20):
        sensor = device_manager.register_device(
            name=f"传感器-{i+1}",
            device_type=DeviceType.IOT_SENSOR,
            imei=f"860000000020{i:03d}",
            imsi=f"460000000020{i:03d}"
        )
        sensors.append(sensor)
        
        # 连接到mMTC切片
        device_manager.connect_device(
            device_id=sensor.device_id,
            slice_id=mmtc_slice.slice_id,
            location=(factory_location[0] + np.random.uniform(-0.005, 0.005),
                     factory_location[1] + np.random.uniform(-0.005, 0.005))
        )
    
    stats = device_manager.get_device_stats()
    print(f"已注册设备: {stats['total_devices']} 个")
    print(f"已连接设备: {stats['connected_devices']} 个")
    print(f"设备类型分布: {stats['by_type']}")
    
    # ==================== 4. SLA监控 ====================
    print("\n4. 模拟SLA监控")
    print("-" * 70)
    
    # 模拟记录指标
    for _ in range(20):
        # uRLLC延迟应该在10ms以内
        sla_monitor.record_metric(urllc_slice.slice_id, "latency", 
                                  np.random.uniform(5, 12))
        # eMBB带宽应该在1000Mbps以上
        sla_monitor.record_metric(embb_slice.slice_id, "bandwidth",
                                  np.random.uniform(800, 1200))
    
    # 检查SLA合规性
    for slice_obj in slice_manager.list_slices():
        compliance = sla_monitor.check_sla_compliance(slice_obj)
        print(f"\n切片 {slice_obj.name}:")
        print(f"  SLA状态: {compliance['status']}")
        if compliance['violations']:
            for v in compliance['violations']:
                print(f"  违规: {v['metric']} - 要求: {v['required']:.1f}, 实际: {v['actual']:.1f}")
    
    # ==================== 5. V2X服务 ====================
    print("\n5. 车联网V2X服务")
    print("-" * 70)
    
    # 注册车辆
    vehicles = []
    for i in range(5):
        vehicle = v2x_service.register_vehicle(f"VEH-{i+1:03d}", "passenger_car")
        vehicles.append(vehicle)
    
    # 模拟车辆行驶
    for i, vehicle_id in enumerate([v["vehicle_id"] for v in vehicles]):
        position = (31.2400 + i*0.0005, 121.4800)
        speed = 30 + i * 10  # km/h
        heading = 0
        
        v2x_service.update_vehicle_state(vehicle_id, position, speed, heading)
    
    # 检查碰撞风险
    for vehicle_id in [v["vehicle_id"] for v in vehicles[:3]]:
        risks = v2x_service.check_collision_risk(vehicle_id)
        if risks:
            print(f"\n车辆 {vehicle_id} 碰撞风险:")
            for risk in risks:
                print(f"  与 {risk['vehicle_id']}: 距离 {risk['distance_m']:.1f}m, "
                      f"TTC {risk['ttc_seconds']:.2f}s, 等级: {risk['risk_level']}")
    
    # ==================== 6. 切换演示 ====================
    print("\n6. 设备移动切换演示")
    print("-" * 70)
    
    # 移动AGV到新位置
    agv = agvs[0]
    old_bs = agv.connected_bs
    new_location = (factory_location[0] + 0.02, factory_location[1] + 0.01)
    
    print(f"AGV {agv.device_id} 从位置 {agv.location} 移动到 {new_location}")
    
    # 执行切换
    success = device_manager.handover(agv.device_id, new_location)
    if success:
        print(f"切换成功: {old_bs} -> {agv.connected_bs}")
    else:
        print("无需切换或切换失败")
    
    # ==================== 7. 统计信息 ====================
    print("\n7. 网络统计信息")
    print("-" * 70)
    
    # 切片统计
    print("网络切片:")
    for slice_obj in slice_manager.list_slices():
        print(f"  {slice_obj.name}: {len(slice_obj.connected_devices)} 设备")
    
    # 基站统计
    print("\n基站状态:")
    for bs in bs_manager.base_stations.values():
        print(f"  {bs.name}: {bs.connected_devices} 连接")
    
    print("\n" + "=" * 70)
    print("演示完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

---

## 10. 效果评估

### 10.1 关键指标达成情况

| 指标类别 | 指标名称 | 目标值 | 实际值 | 达成率 |
|---------|---------|-------|-------|-------|
| **覆盖指标** | 5G覆盖率 | 100% | 100% | 100% |
| | 设备连接数 | 10万 | 12万 | 120% |
| | 网络可用性 | 99.999% | 99.9995% | 100% |
| **性能指标** | 空口延迟 | <5ms | 3ms | 167% |
| | 端到端延迟 | <10ms | 8ms | 125% |
| | 峰值速率 | 1Gbps | 1.2Gbps | 120% |
| **切片指标** | 切片数量 | 10个 | 15个 | 150% |
| | 切片部署时间 | <1小时 | 30分钟 | 200% |
| | 切片隔离度 | 99.9% | 99.99% | 100% |

### 10.2 ROI分析

**投资成本（12个月）**：

| 项目 | 金额（万元） |
|------|------------|
| 5G基站设备 | 8000 |
| 核心网建设 | 3000 |
| 切片平台开发 | 2000 |
| MEC边缘节点 | 2500 |
| 系统集成 | 1500 |
| **总投资** | **17000** |

**收益分析（12个月）**：

| 收益来源 | 金额（万元） |
|---------|------------|
| 生产效率提升 | 4000 |
| 网络运维成本降低 | 1500 |
| 设备故障减少 | 1000 |
| 柔性生产能力 | 3000 |
| 安全事故减少 | 2000 |
| **总收益** | **11500** |

**ROI计算**：
- **净收益（第1年）**：11500 - 17000 = -5500万元（投资回收期约18个月）
- **3年ROI**：约120%
- **社会效益**：提升行业数字化水平，创造就业机会

### 10.3 定性效益

1. **生产效率**：产线换型时间从4小时缩短至30分钟
2. **质量控制**：视觉质检准确率达到99.7%，漏检率降低90%
3. **安全保障**：实现危险区域的远程操控，零安全事故
4. **绿色环保**：通过优化减少能源消耗15%

---

## 11. 案例总结

### 11.1 成功因素

1. **需求明确**：前期充分调研业务需求，确保5G能力与场景匹配
2. **共建共享**：与运营商共建专网，降低建设成本
3. **生态合作**：与设备商、应用开发商建立紧密合作
4. **持续优化**：基于实际运行数据持续优化网络配置

### 11.2 经验教训

1. **频段选择**：毫米波覆盖范围小，室内部署成本高
2. **终端生态**：工业级5G终端种类有限，价格高
3. **人才短缺**：5G与行业结合的复合型人才稀缺

### 11.3 未来展望

1. 推进5G-A（5G-Advanced）技术应用
2. 探索5G与卫星通信的融合
3. 发展5G+AI的智能化运维

---

**创建时间**：2025-01-21  
**最后更新**：2026-02-15  
**文档版本**：v1.0  
**维护者**：DSL Schema研究团队
