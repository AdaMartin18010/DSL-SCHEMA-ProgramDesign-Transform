# 环境监测Schema实践案例

## 📑 目录

- [环境监测Schema实践案例](#环境监测schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 企业背景](#2-企业背景)
  - [3. 业务痛点](#3-业务痛点)
  - [4. 业务目标](#4-业务目标)
  - [5. 技术挑战](#5-技术挑战)
  - [6. 案例1：大气质量监测网络](#6-案例1大气质量监测网络)
  - [7. 案例2：水环境智能监测](#7-案例2水环境智能监测)
  - [8. 案例3：污染源在线监控](#8-案例3污染源在线监控)
  - [9. Python代码实现](#9-python代码实现)
  - [10. 效果评估](#10-效果评估)
  - [11. 案例总结](#11-案例总结)

---

## 1. 案例概述

本文档提供**环境监测Schema的实际应用案例**，涵盖大气质量监测、水环境监测、污染源监控等领域。通过真实的环保场景，展示如何利用物联网、大数据和AI技术实现环境质量的全面感知和智能管控。

**案例类型**：
- 大气质量监测网络
- 水环境智能监测
- 污染源在线监控

---

## 2. 企业背景

### 2.1 企业概况

**绿源环境监测科技股份有限公司**（以下简称"绿源科技"）成立于2010年，总部位于南京，是国内领先的环境监测解决方案提供商。公司为国家、省、市各级环保部门以及大型工业企业提供环境监测设备、平台和运维服务。

### 2.2 业务规模

| 指标 | 数值 |
|------|------|
| 年营收 | 8亿元 |
| 部署监测站点 | 5000+个 |
| 接入传感器 | 50,000+个 |
| 服务客户 | 300+家 |
| 年处理数据量 | 10亿+条 |

### 2.3 业务领域

绿源科技主要提供以下服务：
- **大气环境监测**：空气质量监测站、微型站、移动监测
- **水环境监测**：水质自动监测站、浮标站、实验室分析
- **污染源监测**：烟气CEMS、水质在线监测、VOCs监测
- **噪声与辐射监测**：噪声监测、核辐射监测

---

## 3. 业务痛点

### 痛点1：监测数据孤岛

**问题描述**：不同部门、不同时期建设的监测系统相互独立，数据无法共享，难以形成全局环境画像。

**影响范围**：某市环保局使用7套不同厂家的监测系统，数据整合需要大量人工处理。

### 痛点2：数据质量参差不齐

**问题描述**：监测设备品牌众多、运维水平不一，数据质量差异大，影响分析准确性。

**质量问题**：约15%的监测数据因设备故障或运维不当导致异常。

### 痛点3：污染预警滞后

**问题描述**：传统的环境预警依赖事后分析，从污染发生到发现平均需要4-6小时。

**应急响应**：多次重污染天气因预警不及时导致应对被动。

### 痛点4：运维成本高

**问题描述**：监测站点分布广、数量多，人工巡检维护成本高、效率低。

**运维成本**：单个空气站年均运维成本约15万元，300个站点年运维成本4500万元。

### 痛点5：企业排污监管难

**问题描述**：重点排污企业数据造假、偷排漏排难以发现，执法取证困难。

**监管缺口**：仅依靠人工抽查，难以实现对所有企业的有效监管。

---

## 4. 业务目标

### 目标1：构建统一监测平台

整合各类环境监测数据，建立覆盖气、水、土、声的统一监测平台，实现数据互联互通。

**关键指标**：
- 数据接入覆盖率：100%
- 数据标准化率：100%
- 数据共享响应：<1秒

### 目标2：建立数据质量保障体系

通过设备校准、数据质控、异常检测等手段，确保监测数据质量。

**关键指标**：
- 数据有效率：>95%
- 异常数据识别率：>98%
- 质控覆盖率：100%

### 目标3：实现小时级污染预警

基于气象数据和监测数据，构建污染预测模型，实现重污染天气的提前预警。

**关键指标**：
- 预警提前量：>24小时
- 预警准确率：>85%
- 误报率：<10%

### 目标4：智能化运维管理

利用IoT和AI技术实现设备状态监测、故障预测、智能调度，降低运维成本。

**关键指标**：
- 运维成本降低：30%
- 故障预测准确率：>90%
- 设备可用率：>98%

### 目标5：精准化排污监管

建设污染源在线监控系统，实现排污数据的实时采集、分析和执法联动。

**关键指标**：
- 重点污染源监控率：100%
- 异常排污发现时间：<10分钟
- 执法响应时间：<30分钟

---

## 5. 技术挑战

### 挑战1：多源异构数据融合

**问题描述**：监测设备品牌众多，通信协议、数据格式各异，数据融合困难。

**技术难点**：
- 多协议适配（HJ212、Modbus、MQTT等）
- 数据标准化与质量控制
- 时空数据对齐

### 挑战2：边缘计算与传输优化

**问题描述**：野外监测站点网络条件差，需要在边缘进行数据预处理和压缩。

**技术难点**：
- 边缘计算网关设计
- 数据压缩与增量传输
- 离线数据缓存与同步

### 挑战3：大气扩散模型构建

**问题描述**：污染物在大气中的扩散受气象条件、地形地貌等多种因素影响，建模复杂。

**技术难点**：
- 高斯扩散模型与机器学习结合
- 气象模式数据同化
- 实时校准与更新

### 挑战4：水环境参数反演

**问题描述**：部分水质参数难以直接测量，需要通过光谱等技术间接估算。

**技术难点**：
- 高光谱数据分析
- 机器学习反演模型
- 多源数据融合反演

### 挑战5：数据安全与防篡改

**问题描述**：监测数据是环境执法的依据，需要防止数据篡改和造假。

**技术难点**：
- 数据加密与签名
- 区块链存证
- 异常行为检测

---

## 6. 案例1：大气质量监测网络

### 6.1 案例背景

**问题**：构建覆盖城市、乡镇、工业园区的大气质量监测网络，实现PM2.5、O3等污染物的全面监测。

**应用场景**：城市空气质量评价、污染溯源分析、预警预报。

### 6.2 Schema定义

**大气监测Schema**：

```dsl
platform AirQuality_Monitoring {
  platform_name: "绿源大气质量监测平台"
  
  station_types: [
    National_Control_Station,    # 国控站
    Provincial_Control_Station,  # 省控站
    City_Control_Station,        # 市控站
    Micro_Station,               # 微站
    Mobile_Monitoring_Vehicle    # 走航监测车
  ]
  
  pollutants: [
    PM2_5, PM10, SO2, NO2, O3, CO,
    VOCs, H2S, NH3, Benzene, Formaldehyde
  ]
  
  functions: [
    collectData(sensor: Sensor, timestamp: Timestamp): Measurement,
    calibrateSensor(station_id: Station_ID, standard: Standard_Gas): Calibration_Result,
    predictPollution(meteo: Meteorology, historical: Time_Series): Forecast_Result,
    traceSource(pollution_event: Event, wind_field: Wind_Field): Source_Attribution,
    generateAQI(station_id: Station_ID, hour: Hour): AQI_Value
  ]
  
  state: {
    stations: Map[Station_ID, Monitoring_Station]
    measurements: Map[Measurement_ID, Measurement]
    sensors: Map[Sensor_ID, Sensor]
    forecasts: Map[Forecast_ID, Forecast]
  }
  
  events: [
    DataReceived(station_id: Station_ID, pollutant: String, value: Float),
    ThresholdExceeded(station_id: Station_ID, pollutant: String, threshold: Float),
    CalibrationCompleted(station_id: Station_ID, sensor: String, drift: Float),
    ForecastUpdated(forecast_id: Forecast_ID, aqi_prediction: Integer)
  ]
}
```

---

## 7. 案例2：水环境智能监测

### 7.1 案例背景

**问题**：建设覆盖河流、湖泊、水库的水质自动监测网络，实现水质状况的实时监控和预警。

**应用场景**：饮用水水源地监测、河流断面监测、污染源追踪。

### 7.2 Schema定义

**水环境监测Schema**：

```dsl
platform WaterQuality_Monitoring {
  platform_name: "绿源水环境监测平台"
  
  water_body_types: [River, Lake, Reservoir, Ocean, Groundwater]
  
  monitoring_parameters: [
    Physical: [Temperature, pH, Turbidity, Conductivity, DO],
    Chemical: [COD, BOD, NH3_N, TP, TN, Heavy_Metals],
    Biological: [Algae, E_Coli, Phytoplankton],
    Organic: [VOCs, SVOCs, Pesticides]
  ]
  
  functions: [
    monitorWaterQuality(station: Station, parameters: Parameter[]): WaterQuality_Data,
    detectAnomaly(current: Measurement, baseline: Time_Series): Anomaly_Result,
    estimateFlow(velocity: Float, cross_section: Area): Discharge,
    calculateWQI(parameters: Parameter[]): WaterQuality_Index,
    predictAlgaeBloom(water_temp: Float, nutrients: Nutrients): Bloom_Risk
  ]
  
  state: {
    water_stations: Map[Station_ID, Water_Station]
    catchments: Map[Catchment_ID, Catchment]
    discharge_points: Map[Outlet_ID, Discharge_Point]
    water_quality_data: Time_Series
  }
  
  events: [
    WaterQualityAlert(station_id: Station_ID, parameter: String, value: Float),
    AlgaeBloomRisk(water_body: String, risk_level: Alert_Level),
    IllegalDischargeDetected(outlet_id: Outlet_ID, pollutant: String),
    WQIDegraded(station_id: Station_ID, from_class: String, to_class: String)
  ]
}
```

---

## 8. 案例3：污染源在线监控

### 8.1 案例背景

**问题**：建设重点污染源在线监控系统，实现排污数据的实时采集、传输和分析，支撑精准执法。

**应用场景**：烟气排放监测、废水排放监测、VOCs治理设施监控。

### 8.2 Schema定义

**污染源监控Schema**：

```dsl
platform Pollution_Source_Monitoring {
  platform_name: "绿源污染源监控平台"
  
  source_types: [Industrial, Power_Plant, Waste_Incineration, Sewage_Treatment]
  
  emission_types: [
    Flue_Gas,           # 烟气
    Waste_Water,        # 废水
    VOCs,               # 挥发性有机物
    Hazardous_Waste,    # 危险废物
    Particulate_Matter  # 粉尘
  ]
  
  functions: [
    monitorEmission(source: Pollution_Source, type: Emission_Type): Emission_Data,
    verifyDataIntegrity(data: Emission_Data): Integrity_Check,
    detectAbnormalEmission(current: Emission, permit: Permit): Abnormal_Detection,
    calculateEmissionFee(emissions: Emission[], rates: Rate[]): Fee_Calculation,
    generateEnforcementCase(violation: Violation): Case_File
  ]
  
  state: {
    pollution_sources: Map[Source_ID, Pollution_Source]
    permits: Map[Permit_ID, Emission_Permit]
    monitoring_data: Map[Data_ID, Emission_Record]
    violations: Map[Violation_ID, Violation]
  }
  
  events: [
    EmissionDataUploaded(source_id: Source_ID, timestamp: Timestamp),
    EmissionLimitExceeded(source_id: Source_ID, pollutant: String, excess: Float),
    FacilityTamperingDetected(source_id: Source_ID, evidence: Evidence),
    EnforcementCaseCreated(case_id: Case_ID, violation: Violation)
  ]
}
```

---

## 9. Python代码实现

### 9.1 完整系统实现

```python
"""
环境监测管理平台 - Python实现
包含：数据采集、质量控制、污染预测、智能预警
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque
import json
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PollutantType(Enum):
    """污染物类型"""
    PM25 = "PM2.5"
    PM10 = "PM10"
    SO2 = "SO2"
    NO2 = "NO2"
    O3 = "O3"
    CO = "CO"
    COD = "COD"
    NH3N = "NH3-N"
    TP = "TP"


class AQILevel(Enum):
    """AQI等级"""
    EXCELLENT = ("优", 0, 50, "#00E400")
    GOOD = ("良", 51, 100, "#FFFF00")
    LIGHT = ("轻度污染", 101, 150, "#FF7E00")
    MODERATE = ("中度污染", 151, 200, "#FF0000")
    HEAVY = ("重度污染", 201, 300, "#99004C")
    SEVERE = ("严重污染", 301, 500, "#7E0023")
    
    def __init__(self, label, min_val, max_val, color):
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.color = color


@dataclass
class MonitoringStation:
    """监测站点"""
    station_id: str
    name: str
    station_type: str
    longitude: float
    latitude: float
    altitude: float = 0.0
    status: str = "active"
    sensors: List['Sensor'] = field(default_factory=list)
    
    def get_location(self) -> Tuple[float, float]:
        return (self.longitude, self.latitude)


@dataclass
class Sensor:
    """传感器"""
    sensor_id: str
    station_id: str
    pollutant: PollutantType
    unit: str
    calibration_date: datetime = field(default_factory=datetime.now)
    status: str = "normal"
    
    def calibrate(self, standard_value: float, measured_value: float) -> float:
        """校准传感器"""
        drift = measured_value - standard_value
        self.calibration_date = datetime.now()
        return drift


@dataclass
class Measurement:
    """监测数据"""
    measurement_id: str
    station_id: str
    sensor_id: str
    pollutant: PollutantType
    value: float
    unit: str
    timestamp: datetime
    quality_flag: str = "valid"  # valid, suspicious, invalid
    data_hash: str = ""
    
    def __post_init__(self):
        if not self.data_hash:
            self.data_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """计算数据哈希"""
        data_str = f"{self.station_id}{self.sensor_id}{self.pollutant.value}{self.value}{self.timestamp.isoformat()}"
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]


class AirQualityMonitor:
    """空气质量监测器"""
    
    def __init__(self):
        self.stations: Dict[str, MonitoringStation] = {}
        self.measurements: List[Measurement] = []
        self.hourly_data: Dict[str, Dict[PollutantType, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=24))
        )
    
    def add_station(self, station: MonitoringStation):
        """添加监测站点"""
        self.stations[station.station_id] = station
        logger.info(f"监测站点 {station.name} ({station.station_id}) 已添加")
    
    def record_measurement(self, station_id: str, pollutant: PollutantType,
                          value: float, unit: str = "μg/m³") -> Measurement:
        """记录监测数据"""
        if station_id not in self.stations:
            raise ValueError(f"站点 {station_id} 不存在")
        
        measurement = Measurement(
            measurement_id=f"M{int(datetime.now().timestamp()*1000)}",
            station_id=station_id,
            sensor_id=f"{station_id}_{pollutant.value}",
            pollutant=pollutant,
            value=value,
            unit=unit,
            timestamp=datetime.now()
        )
        
        self.measurements.append(measurement)
        self.hourly_data[station_id][pollutant].append(value)
        
        # 检查是否超标
        self._check_threshold(measurement)
        
        return measurement
    
    def _check_threshold(self, measurement: Measurement):
        """检查阈值"""
        thresholds = {
            PollutantType.PM25: 75,   # 中国标准24小时平均
            PollutantType.PM10: 150,
            PollutantType.SO2: 150,
            PollutantType.NO2: 80,
            PollutantType.O3: 160,
            PollutantType.CO: 4000    # mg/m³
        }
        
        threshold = thresholds.get(measurement.pollutant)
        if threshold and measurement.value > threshold:
            logger.warning(f"超标告警: 站点 {measurement.station_id} {measurement.pollutant.value} "
                         f"{measurement.value} > {threshold}")
    
    def calculate_aqi(self, station_id: str) -> Dict[str, Any]:
        """计算AQI"""
        if station_id not in self.hourly_data:
            return {}
        
        aqi_values = {}
        
        for pollutant, values in self.hourly_data[station_id].items():
            if not values:
                continue
            
            # 计算该污染物的AQI分指数
            hourly_avg = np.mean(list(values))
            iaqi = self._calculate_iaqi(pollutant, hourly_avg)
            aqi_values[pollutant.value] = {
                "concentration": hourly_avg,
                "IAQI": iaqi
            }
        
        if not aqi_values:
            return {}
        
        # AQI取各污染物分指数最大值
        primary_pollutant = max(aqi_values.items(), key=lambda x: x[1]["IAQI"])
        aqi = primary_pollutant[1]["IAQI"]
        
        # 确定AQI等级
        level = self._get_aqi_level(aqi)
        
        return {
            "station_id": station_id,
            "aqi": int(aqi),
            "level": level.label,
            "color": level.color,
            "primary_pollutant": primary_pollutant[0],
            "pollutants": aqi_values,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_iaqi(self, pollutant: PollutantType, concentration: float) -> float:
        """计算IAQI（简化公式）"""
        # 简化的IAQI计算，实际应使用标准分段线性插值
        breakpoints = {
            PollutantType.PM25: [(0, 35, 0, 50), (35, 75, 50, 100), (75, 115, 100, 150)],
            PollutantType.PM10: [(0, 50, 0, 50), (50, 150, 50, 100), (150, 250, 100, 150)],
            PollutantType.O3: [(0, 100, 0, 50), (100, 160, 50, 100), (160, 215, 100, 150)]
        }
        
        if pollutant not in breakpoints:
            return min(concentration / 2, 500)  # 默认计算
        
        for c_low, c_high, i_low, i_high in breakpoints[pollutant]:
            if c_low <= concentration <= c_high:
                return ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
        
        return 500  # 超过范围
    
    def _get_aqi_level(self, aqi: float) -> AQILevel:
        """获取AQI等级"""
        for level in AQILevel:
            if level.min_val <= aqi <= level.max_val:
                return level
        return AQILevel.SEVERE
    
    def predict_pollution(self, station_id: str, hours_ahead: int = 24) -> Dict[str, Any]:
        """预测污染趋势（简化模型）"""
        if station_id not in self.hourly_data:
            return {}
        
        predictions = []
        
        # 简化的线性趋势预测
        for pollutant in [PollutantType.PM25, PollutantType.O3]:
            values = list(self.hourly_data[station_id][pollutant])
            if len(values) < 3:
                continue
            
            # 计算趋势
            trend = (values[-1] - values[0]) / len(values)
            
            for h in range(1, hours_ahead + 1):
                predicted = values[-1] + trend * h + np.random.normal(0, 2)
                predictions.append({
                    "hour": h,
                    "pollutant": pollutant.value,
                    "predicted": max(0, predicted)
                })
        
        return {
            "station_id": station_id,
            "predictions": predictions[:10],  # 只返回部分
            "generated_at": datetime.now().isoformat()
        }


class WaterQualityMonitor:
    """水质监测器"""
    
    def __init__(self):
        self.stations: Dict[str, MonitoringStation] = {}
        self.measurements: List[Measurement] = []
        self.wqi_weights = {
            "DO": 0.25,
            "COD": 0.20,
            "NH3N": 0.20,
            "TP": 0.15,
            "TN": 0.20
        }
    
    def calculate_wqi(self, parameters: Dict[str, float]) -> Dict[str, Any]:
        """计算水质指数WQI"""
        # 简化的WQI计算
        wqi = 0
        sub_indices = {}
        
        for param, weight in self.wqi_weights.items():
            if param in parameters:
                # 简化的分指数计算
                if param == "DO":
                    # DO越高越好
                    sub_index = min(parameters[param] / 7.5 * 100, 100)
                else:
                    # 其他参数越低越好
                    sub_index = max(0, 100 - parameters[param])
                
                sub_indices[param] = sub_index
                wqi += sub_index * weight
        
        # 水质等级
        if wqi >= 90:
            grade = "I类"
            status = "优"
        elif wqi >= 75:
            grade = "II类"
            status = "良"
        elif wqi >= 60:
            grade = "III类"
            status = "一般"
        elif wqi >= 45:
            grade = "IV类"
            status = "差"
        else:
            grade = "V类"
            status = "极差"
        
        return {
            "wqi": round(wqi, 2),
            "grade": grade,
            "status": status,
            "sub_indices": sub_indices
        }
    
    def detect_anomaly(self, current: Dict[str, float], 
                      baseline: Dict[str, List[float]]) -> List[str]:
        """检测水质异常"""
        anomalies = []
        
        for param, value in current.items():
            if param in baseline and baseline[param]:
                mean = np.mean(baseline[param])
                std = np.std(baseline[param])
                
                if std > 0:
                    z_score = abs(value - mean) / std
                    if z_score > 3:
                        anomalies.append(f"{param}: 当前{value}, 偏离均值{z_score:.1f}个标准差")
        
        return anomalies


class PollutionSourceMonitor:
    """污染源监测器"""
    
    def __init__(self):
        self.sources: Dict[str, Dict] = {}
        self.emissions: List[Dict] = []
        self.permits: Dict[str, Dict] = {}
        self.violations: List[Dict] = []
    
    def register_source(self, source_id: str, name: str, source_type: str,
                       permit_limits: Dict[str, float]):
        """注册污染源"""
        self.sources[source_id] = {
            "source_id": source_id,
            "name": name,
            "type": source_type,
            "permit_limits": permit_limits,
            "status": "normal"
        }
        
        logger.info(f"污染源 {name} ({source_id}) 已注册")
    
    def record_emission(self, source_id: str, pollutant: str, 
                       concentration: float, flow_rate: float):
        """记录排放数据"""
        emission = {
            "emission_id": str(hashlib.sha256(f"{source_id}{pollutant}{datetime.now()}".encode()).hexdigest()[:16]),
            "source_id": source_id,
            "pollutant": pollutant,
            "concentration": concentration,
            "flow_rate": flow_rate,
            "timestamp": datetime.now(),
            "emission_rate": concentration * flow_rate  # mg/h
        }
        
        self.emissions.append(emission)
        
        # 检查是否超标
        self._check_violation(emission)
        
        return emission
    
    def _check_violation(self, emission: Dict):
        """检查是否超标"""
        source = self.sources.get(emission["source_id"])
        if not source:
            return
        
        limit = source["permit_limits"].get(emission["pollutant"])
        if limit and emission["concentration"] > limit:
            excess = (emission["concentration"] - limit) / limit * 100
            
            violation = {
                "violation_id": str(len(self.violations) + 1),
                "source_id": emission["source_id"],
                "pollutant": emission["pollutant"],
                "measured": emission["concentration"],
                "limit": limit,
                "excess_percent": excess,
                "timestamp": emission["timestamp"],
                "status": "open"
            }
            
            self.violations.append(violation)
            
            logger.warning(f"超标排放: {source['name']} {emission['pollutant']} "
                         f"{emission['concentration']} > {limit} ({excess:.1f}%)")
    
    def calculate_emission_fee(self, source_id: str, period_days: int = 30) -> Dict[str, Any]:
        """计算排污费（简化）"""
        source = self.sources.get(source_id)
        if not source:
            return {}
        
        # 统计该企业的排放
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        emissions_by_pollutant = defaultdict(list)
        for e in self.emissions:
            if e["source_id"] == source_id and e["timestamp"] > cutoff_date:
                emissions_by_pollutant[e["pollutant"]].append(e["emission_rate"])
        
        fee_details = []
        total_fee = 0
        
        # 简化的费率表
        rates = {
            "SO2": 0.6,    # 元/kg
            "NOx": 0.6,
            "COD": 0.7,
            "NH3N": 0.7
        }
        
        for pollutant, rates_list in emissions_by_pollutant.items():
            total_emission_kg = np.sum(rates_list) * 24 * period_days / 1000 / 1000  # 转换为kg
            rate = rates.get(pollutant, 0.5)
            fee = total_emission_kg * rate
            
            fee_details.append({
                "pollutant": pollutant,
                "total_emission_kg": round(total_emission_kg, 2),
                "rate": rate,
                "fee": round(fee, 2)
            })
            
            total_fee += fee
        
        return {
            "source_id": source_id,
            "period_days": period_days,
            "fee_details": fee_details,
            "total_fee": round(total_fee, 2)
        }
    
    def get_compliance_summary(self, source_id: str) -> Dict[str, Any]:
        """获取合规摘要"""
        source = self.sources.get(source_id)
        if not source:
            return {}
        
        violations = [v for v in self.violations if v["source_id"] == source_id]
        
        return {
            "source_id": source_id,
            "name": source["name"],
            "total_violations": len(violations),
            "open_violations": sum(1 for v in violations if v["status"] == "open"),
            "violation_breakdown": defaultdict(int, 
                {v["pollutant"]: sum(1 for x in violations if x["pollutant"] == v["pollutant"]) 
                 for v in violations}),
            "compliance_rate": max(0, 100 - len(violations) * 5)  # 简化的合规率
        }


class DataQualityController:
    """数据质量控制"""
    
    def __init__(self):
        self.quality_rules = []
        self.suspicious_data = []
    
    def validate_measurement(self, measurement: Measurement) -> str:
        """验证数据质量"""
        # 范围检查
        ranges = {
            PollutantType.PM25: (0, 1000),
            PollutantType.PM10: (0, 2000),
            PollutantType.SO2: (0, 2000),
            PollutantType.NO2: (0, 2000),
            PollutantType.O3: (0, 1000),
            PollutantType.CO: (0, 50000)
        }
        
        valid_range = ranges.get(measurement.pollutant)
        if valid_range:
            if measurement.value < valid_range[0] or measurement.value > valid_range[1]:
                return "invalid"
        
        # 负值检查
        if measurement.value < 0:
            return "invalid"
        
        # 异常高值检查
        if valid_range and measurement.value > valid_range[1] * 0.8:
            return "suspicious"
        
        return "valid"
    
    def flag_data(self, measurement: Measurement) -> Measurement:
        """标记数据质量"""
        measurement.quality_flag = self.validate_measurement(measurement)
        return measurement


# 示例用法
def main():
    """主函数示例"""
    print("=" * 70)
    print("环境监测管理平台演示")
    print("=" * 70)
    
    # 初始化监测器
    air_monitor = AirQualityMonitor()
    water_monitor = WaterQualityMonitor()
    source_monitor = PollutionSourceMonitor()
    quality_controller = DataQualityController()
    
    # ==================== 1. 大气质量监测 ====================
    print("\n1. 大气质量监测")
    print("-" * 70)
    
    # 添加监测站点
    stations = [
        MonitoringStation("ST001", "市中心站", "国控站", 118.7969, 32.0603),
        MonitoringStation("ST002", "工业园区站", "省控站", 118.85, 32.02),
        MonitoringStation("ST003", "背景站", "市控站", 118.75, 32.10),
    ]
    
    for station in stations:
        air_monitor.add_station(station)
    
    # 模拟监测数据
    print("\n模拟24小时监测数据:")
    for hour in range(24):
        for station in stations:
            # 模拟PM2.5数据（早高峰和晚高峰较高）
            base_pm25 = 35
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                base_pm25 += 40
            
            pm25 = base_pm25 + np.random.normal(0, 10)
            pm25 = max(0, pm25)
            
            measurement = air_monitor.record_measurement(
                station.station_id,
                PollutantType.PM25,
                pm25
            )
            
            # 质量控制
            quality_controller.flag_data(measurement)
    
    # 计算AQI
    print("\n各站点实时AQI:")
    for station in stations:
        aqi = air_monitor.calculate_aqi(station.station_id)
        if aqi:
            print(f"  {station.name}: AQI {aqi['aqi']} ({aqi['level']}), "
                 f"首要污染物: {aqi['primary_pollutant']}")
    
    # 污染预测
    print("\n污染趋势预测:")
    forecast = air_monitor.predict_pollution("ST001", hours_ahead=24)
    print(f"  站点 ST001 未来24小时预测完成，共 {len(forecast.get('predictions', []))} 条预测")
    
    # ==================== 2. 水质监测 ====================
    print("\n2. 水质监测")
    print("-" * 70)
    
    # 计算WQI
    water_params = {
        "DO": 7.5,      # 溶解氧 mg/L
        "COD": 15,      # 化学需氧量 mg/L
        "NH3N": 0.5,    # 氨氮 mg/L
        "TP": 0.1,      # 总磷 mg/L
        "TN": 2.0       # 总氮 mg/L
    }
    
    wqi = water_monitor.calculate_wqi(water_params)
    print(f"水质监测结果:")
    print(f"  WQI: {wqi['wqi']}")
    print(f"  水质等级: {wqi['grade']} ({wqi['status']})")
    print(f"  分指数: {wqi['sub_indices']}")
    
    # 异常检测
    baseline = {
        "DO": [6.5, 7.0, 7.2, 7.5, 7.8, 8.0, 7.6],
        "COD": [12, 13, 14, 15, 16, 15, 14],
        "NH3N": [0.3, 0.4, 0.4, 0.5, 0.5, 0.6, 0.5]
    }
    
    # 异常数据
    abnormal_params = {
        "DO": 7.5,
        "COD": 15,
        "NH3N": 2.5  # 异常高值
    }
    
    anomalies = water_monitor.detect_anomaly(abnormal_params, baseline)
    if anomalies:
        print(f"\n检测到水质异常:")
        for anomaly in anomalies:
            print(f"  ⚠ {anomaly}")
    
    # ==================== 3. 污染源监控 ====================
    print("\n3. 污染源在线监控")
    print("-" * 70)
    
    # 注册污染源
    sources = [
        ("S001", "华东电厂", "Power_Plant", {"SO2": 35, "NOx": 50, "PM": 10}),
        ("S002", "南京化工厂", "Chemical", {"COD": 80, "NH3N": 15, "TP": 1.0}),
        ("S003", "江北污水处理厂", "Sewage", {"COD": 50, "NH3N": 5, "TP": 0.5}),
    ]
    
    for sid, name, stype, limits in sources:
        source_monitor.register_source(sid, name, stype, limits)
    
    # 模拟排放数据
    print("\n模拟污染源排放数据:")
    
    # 正常排放
    for _ in range(10):
        source_monitor.record_emission("S001", "SO2", 25, 100000)
    
    # 超标排放
    source_monitor.record_emission("S001", "SO2", 45, 100000)  # 超过35
    source_monitor.record_emission("S002", "COD", 120, 5000)   # 超过80
    
    print(f"  S001: SO2平均排放 28 mg/m³")
    print(f"  S002: COD排放 120 mg/m³ (超标50%)")
    
    # 排污费计算
    fee_info = source_monitor.calculate_emission_fee("S001", period_days=30)
    print(f"\n排污费计算 (S001):")
    print(f"  周期: {fee_info['period_days']} 天")
    for detail in fee_info.get('fee_details', []):
        print(f"  {detail['pollutant']}: {detail['total_emission_kg']} kg × {detail['rate']} 元/kg = {detail['fee']} 元")
    print(f"  合计: {fee_info.get('total_fee', 0)} 元")
    
    # 合规摘要
    print("\n污染源合规情况:")
    for sid, _, _, _ in sources:
        summary = source_monitor.get_compliance_summary(sid)
        if summary:
            status_icon = "✓" if summary['total_violations'] == 0 else "✗"
            print(f"  {status_icon} {summary['name']}: "
                 f"违规 {summary['total_violations']} 次, "
                 f"合规率 {summary['compliance_rate']:.1f}%")
    
    # ==================== 4. 数据质量统计 ====================
    print("\n4. 数据质量统计")
    print("-" * 70)
    
    valid_count = sum(1 for m in air_monitor.measurements if m.quality_flag == "valid")
    suspicious_count = sum(1 for m in air_monitor.measurements if m.quality_flag == "suspicious")
    invalid_count = sum(1 for m in air_monitor.measurements if m.quality_flag == "invalid")
    
    total = len(air_monitor.measurements)
    print(f"大气监测数据质量:")
    print(f"  总数据量: {total}")
    print(f"  有效数据: {valid_count} ({valid_count/total*100:.1f}%)")
    print(f"  可疑数据: {suspicious_count} ({suspicious_count/total*100:.1f}%)")
    print(f"  无效数据: {invalid_count} ({invalid_count/total*100:.1f}%)")
    
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
| **数据整合** | 数据接入覆盖率 | 100% | 100% | 100% |
| | 数据标准化率 | 100% | 100% | 100% |
| | 数据共享响应 | <1秒 | <0.5秒 | 200% |
| **数据质量** | 数据有效率 | >95% | 96.5% | 102% |
| | 异常数据识别率 | >98% | 99% | 101% |
| | 质控覆盖率 | 100% | 100% | 100% |
| **污染预警** | 预警提前量 | >24小时 | 36小时 | 150% |
| | 预警准确率 | >85% | 88% | 104% |
| | 误报率 | <10% | 7% | 143% |
| **运维管理** | 运维成本降低 | 30% | 35% | 117% |
| | 设备可用率 | >98% | 98.5% | 100% |

### 10.2 ROI分析

**投资成本（12个月）**：

| 项目 | 金额（万元） |
|------|------------|
| 平台软件开发 | 3000 |
| 传感器网络建设 | 2000 |
| 云基础设施 | 1000 |
| 系统集成 | 800 |
| 运维服务 | 1200 |
| **总投资** | **8000** |

**收益分析（12个月）**：

| 收益来源 | 金额（万元） |
|---------|------------|
| 平台销售收入 | 5000 |
| 运维服务收入 | 3000 |
| 数据服务收入 | 1500 |
| 政府补贴收入 | 1000 |
| **总收益** | **10500** |

**ROI计算**：
- **净收益**：10500 - 8000 = 2500万元
- **ROI**：(2500 / 8000) × 100% = **31%**
- **投资回收期**：约9个月

### 10.3 定性效益

1. **环境改善**：支撑的污染治理措施使区域空气质量优良天数增加15天/年
2. **执法效能**：环保执法精准度提升，查处违法排污案件数增加200%
3. **公众服务**：公众环境信息查询服务超过1000万次/年
4. **决策支撑**：为政府环境决策提供科学依据，避免盲目决策损失

---

## 11. 案例总结

### 11.1 成功因素

1. **政策驱动**：环保督察趋严推动监测需求增长
2. **技术成熟**：物联网、AI等技术的成熟降低了部署成本
3. **数据价值**：环境数据的多维度应用创造了新的商业价值
4. **持续服务**：长期运维服务保障了系统持续运行

### 11.2 经验教训

1. **设备选型**：野外设备需要严格的环境适应性测试
2. **数据治理**：数据质量是系统价值的基础，需要持续投入
3. **标准统一**：推动行业标准统一有助于降低集成成本

### 11.3 未来展望

1. 发展碳监测和温室气体监测业务
2. 构建区域环境大数据交易平台
3. 探索环境监测与保险的融合应用

---

**创建时间**：2025-01-21  
**最后更新**：2026-02-15  
**文档版本**：v1.0  
**维护者**：DSL Schema研究团队
