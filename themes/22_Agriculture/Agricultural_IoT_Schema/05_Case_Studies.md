# 农业物联网Schema实践案例

## 📑 目录

- [农业物联网Schema实践案例](#农业物联网schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：智慧农业园区数字化管理平台](#2-案例1智慧农业园区数字化管理平台)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 完整代码实现](#25-完整代码实现)
    - [2.6 效果评估](#26-效果评估)
  - [3. 案例总结](#3-案例总结)

---

## 1. 案例概述

本文档提供农业物联网Schema在智慧农业领域的实践案例。

---

## 2. 案例1：智慧农业园区数字化管理平台

### 2.1 业务背景

**企业概况**：某现代农业示范园区（以下简称"Q农业"），占地5000亩，种植温室大棚200个，主要种植番茄、黄瓜、草莓等高附加值作物，年产值超过8000万元。

### 2.2 业务痛点

1. **环境调控粗放**：温湿度控制依赖人工经验，作物生长环境不稳定，品质波动大
2. **水肥浪费严重**：大水漫灌、过量施肥，水肥利用率不足50%
3. **病虫害发现晚**：病虫害发现时往往已大面积扩散，损失严重
4. **劳动力短缺**：农村劳动力流失，用工成本高，年均涨幅15%
5. **数据利用低**：缺乏数据积累和分析，无法指导精准生产

### 2.3 业务目标

1. **精准环境调控**：实现温室环境自动调控，作物品质稳定性提升30%
2. **节水节肥**：水肥一体化精准施用，利用率提升至85%以上
3. **病虫害预警**：AI图像识别病虫害，提前7天预警，损失降低50%
4. **减少人工投入**：自动化程度提升至70%，人工投入减少40%
5. **数据驱动决策**：建立农业大数据平台，支撑精准生产决策

### 2.4 技术挑战

1. **复杂环境适应**：农业环境复杂多变，传感器需要防水、防腐、耐高温高湿
2. **网络覆盖困难**：园区面积大，部分区域网络信号差
3. **多源数据融合**：环境数据、图像数据、生产数据融合分析
4. **边缘计算能力**：需要本地实时决策，降低云端依赖

### 2.5 完整代码实现

```python
#!/usr/bin/env python3
"""
智慧农业园区数字化管理平台
功能：环境监测、智能灌溉、病虫害识别、生产管理
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import json


class CropType(str, Enum):
    """作物类型"""
    TOMATO = "tomato"
    CUCUMBER = "cucumber"
    STRAWBERRY = "strawberry"
    PEPPER = "pepper"


class DeviceStatus(str, Enum):
    """设备状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class Greenhouse:
    """温室大棚"""
    gh_id: str
    gh_name: str
    area_sqm: float
    crop_type: CropType
    crop_variety: str
    planting_date: date
    
    target_temp_day: float = 25.0
    target_temp_night: float = 18.0
    target_humidity: float = 70.0
    
    devices: List[str] = field(default_factory=list)


@dataclass
class SensorDevice:
    """传感器设备"""
    device_id: str
    device_type: str  # temperature, humidity, soil_moisture, light
    greenhouse_id: str
    status: DeviceStatus
    battery_level: float = 100.0
    last_reading: Optional[datetime] = None


@dataclass
class SensorData:
    """传感器数据"""
    data_id: str
    device_id: str
    greenhouse_id: str
    timestamp: datetime
    
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None
    soil_temperature: Optional[float] = None
    light_intensity: Optional[float] = None
    co2_level: Optional[float] = None
    
    def is_abnormal(self, thresholds: Dict) -> List[str]:
        """检测异常数据"""
        abnormal = []
        
        if self.temperature and thresholds.get('temp_max'):
            if self.temperature > thresholds['temp_max']:
                abnormal.append(f"温度过高: {self.temperature}°C")
            elif self.temperature < thresholds.get('temp_min', 0):
                abnormal.append(f"温度过低: {self.temperature}°C")
        
        if self.humidity and thresholds.get('humidity_max'):
            if self.humidity > thresholds['humidity_max']:
                abnormal.append(f"湿度过高: {self.humidity}%")
        
        if self.soil_moisture and thresholds.get('soil_moisture_min'):
            if self.soil_moisture < thresholds['soil_moisture_min']:
                abnormal.append(f"土壤湿度过低: {self.soil_moisture}%")
        
        return abnormal


@dataclass
class IrrigationTask:
    """灌溉任务"""
    task_id: str
    greenhouse_id: str
    start_time: datetime
    duration_minutes: int
    water_amount_liters: float
    fertilizer_type: Optional[str] = None
    fertilizer_amount: Optional[float] = None
    status: str = "scheduled"  # scheduled, running, completed


@dataclass
class PestDetection:
    """病虫害检测"""
    detection_id: str
    greenhouse_id: str
    timestamp: datetime
    image_url: str
    
    pest_type: Optional[str] = None
    severity: str = "low"  # low, medium, high
    affected_area_percent: float = 0.0
    recommendation: str = ""


class SmartAgriculturePlatform:
    """智慧农业平台"""
    
    def __init__(self):
        self.greenhouses: Dict[str, Greenhouse] = {}
        self.devices: Dict[str, SensorDevice] = {}
        self.sensor_data: Dict[str, List[SensorData]] = {}
        self.irrigation_tasks: Dict[str, IrrigationTask] = {}
        self.pest_detections: Dict[str, PestDetection] = {}
        
        self.thresholds = {
            CropType.TOMATO: {
                'temp_min': 18, 'temp_max': 28,
                'humidity_min': 60, 'humidity_max': 80,
                'soil_moisture_min': 60
            },
            CropType.CUCUMBER: {
                'temp_min': 20, 'temp_max': 30,
                'humidity_min': 70, 'humidity_max': 90,
                'soil_moisture_min': 70
            },
            CropType.STRAWBERRY: {
                'temp_min': 15, 'temp_max': 25,
                'humidity_min': 70, 'humidity_max': 80,
                'soil_moisture_min': 65
            }
        }
    
    def add_greenhouse(self, gh: Greenhouse):
        """添加温室"""
        self.greenhouses[gh.gh_id] = gh
        self.sensor_data[gh.gh_id] = []
    
    def add_device(self, device: SensorDevice):
        """添加设备"""
        self.devices[device.device_id] = device
        
        # 关联到温室
        gh = self.greenhouses.get(device.greenhouse_id)
        if gh:
            gh.devices.append(device.device_id)
    
    def collect_sensor_data(self, greenhouse_id: str) -> SensorData:
        """采集传感器数据"""
        gh = self.greenhouses.get(greenhouse_id)
        if not gh:
            return None
        
        # 模拟数据采集
        data = SensorData(
            data_id=f"DATA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            device_id=random.choice(gh.devices) if gh.devices else "",
            greenhouse_id=greenhouse_id,
            timestamp=datetime.now(),
            temperature=random.uniform(gh.target_temp_day - 2, gh.target_temp_day + 2),
            humidity=random.uniform(gh.target_humidity - 5, gh.target_humidity + 5),
            soil_moisture=random.uniform(50, 80),
            soil_temperature=random.uniform(18, 22),
            light_intensity=random.uniform(20000, 40000),
            co2_level=random.uniform(400, 600)
        )
        
        self.sensor_data[greenhouse_id].append(data)
        
        # 更新设备状态
        device = self.devices.get(data.device_id)
        if device:
            device.last_reading = data.timestamp
        
        return data
    
    def check_environment(self, greenhouse_id: str) -> Dict:
        """检查环境状况"""
        gh = self.greenhouses.get(greenhouse_id)
        if not gh:
            return {}
        
        # 获取最新数据
        data_list = self.sensor_data.get(greenhouse_id, [])
        if not data_list:
            return {}
        
        latest = data_list[-1]
        thresholds = self.thresholds.get(gh.crop_type, {})
        
        abnormalities = latest.is_abnormal(thresholds)
        
        # 生成控制建议
        suggestions = []
        if latest.temperature and latest.temperature > thresholds.get('temp_max', 30):
            suggestions.append("开启通风降温")
        if latest.soil_moisture and latest.soil_moisture < thresholds.get('soil_moisture_min', 60):
            suggestions.append("启动灌溉")
        if latest.humidity and latest.humidity > thresholds.get('humidity_max', 85):
            suggestions.append("开启除湿")
        
        return {
            "greenhouse_id": greenhouse_id,
            "timestamp": latest.timestamp.isoformat(),
            "current_conditions": {
                "temperature": round(latest.temperature, 1) if latest.temperature else None,
                "humidity": round(latest.humidity, 1) if latest.humidity else None,
                "soil_moisture": round(latest.soil_moisture, 1) if latest.soil_moisture else None,
                "light_intensity": round(latest.light_intensity, 0) if latest.light_intensity else None
            },
            "abnormalities": abnormalities,
            "suggestions": suggestions
        }
    
    def create_irrigation_task(self, greenhouse_id: str,
                              duration: int, water_amount: float,
                              fertilizer: str = None, fertilizer_amount: float = None) -> IrrigationTask:
        """创建灌溉任务"""
        task = IrrigationTask(
            task_id=f"IRR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            greenhouse_id=greenhouse_id,
            start_time=datetime.now(),
            duration_minutes=duration,
            water_amount_liters=water_amount,
            fertilizer_type=fertilizer,
            fertilizer_amount=fertilizer_amount
        )
        
        self.irrigation_tasks[task.task_id] = task
        return task
    
    def detect_pest(self, greenhouse_id: str, image_url: str) -> PestDetection:
        """病虫害检测"""
        # 模拟AI检测
        pest_types = [None, "白粉病", "蚜虫", "灰霉病"]
        detected_pest = random.choice(pest_types)
        
        detection = PestDetection(
            detection_id=f"PEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            greenhouse_id=greenhouse_id,
            timestamp=datetime.now(),
            image_url=image_url,
            pest_type=detected_pest,
            severity=random.choice(["low", "medium", "high"]) if detected_pest else "none",
            affected_area_percent=random.uniform(0, 30) if detected_pest else 0
        )
        
        if detected_pest:
            detection.recommendation = f"检测到{detected_pest}，建议及时防治"
        else:
            detection.recommendation = "未检测到病虫害"
        
        self.pest_detections[detection.detection_id] = detection
        return detection
    
    def get_yield_forecast(self, greenhouse_id: str) -> Dict:
        """产量预测"""
        gh = self.greenhouses.get(greenhouse_id)
        if not gh:
            return {}
        
        # 基于作物类型和生长天数预测产量
        days_since_planting = (date.today() - gh.planting_date).days
        
        # 不同作物产量模型（简化）
        yield_models = {
            CropType.TOMATO: {"max_yield": 10, "peak_day": 90},  # kg/m2
            CropType.CUCUMBER: {"max_yield": 8, "peak_day": 60},
            CropType.STRAWBERRY: {"max_yield": 5, "peak_day": 120}
        }
        
        model = yield_models.get(gh.crop_type, {"max_yield": 5, "peak_day": 90})
        
        # 简化的高斯分布模型
        if days_since_planting < model["peak_day"]:
            progress = days_since_planting / model["peak_day"]
            expected_yield = model["max_yield"] * progress * 0.8
        else:
            expected_yield = model["max_yield"]
        
        total_yield = expected_yield * gh.area_sqm
        
        return {
            "greenhouse_id": greenhouse_id,
            "crop_type": gh.crop_type.value,
            "days_since_planting": days_since_planting,
            "expected_yield_kg": round(total_yield, 0),
            "yield_per_sqm": round(expected_yield, 2),
            "harvest_readiness": "ready" if days_since_planting > model["peak_day"] * 0.8 else "growing"
        }
    
    def generate_daily_report(self) -> Dict:
        """生成日报"""
        total_gh = len(self.greenhouses)
        online_devices = sum(1 for d in self.devices.values() if d.status == DeviceStatus.ONLINE)
        
        # 统计异常
        total_abnormal = 0
        for gh_id in self.greenhouses:
            check = self.check_environment(gh_id)
            if check.get('abnormalities'):
                total_abnormal += 1
        
        # 统计灌溉
        today_irrigation = sum(
            1 for t in self.irrigation_tasks.values()
            if t.start_time.date() == date.today()
        )
        
        return {
            "report_date": date.today().isoformat(),
            "total_greenhouses": total_gh,
            "online_devices": online_devices,
            "total_devices": len(self.devices),
            "abnormal_greenhouses": total_abnormal,
            "today_irrigation_tasks": today_irrigation,
            "pest_alerts": sum(1 for p in self.pest_detections.values() if p.pest_type)
        }


def main():
    """智慧农业平台演示"""
    
    print("=" * 60)
    print("智慧农业园区数字化管理平台演示")
    print("=" * 60)
    
    platform = SmartAgriculturePlatform()
    
    # 1. 添加温室
    print("\n[1] 添加温室大棚")
    for i in range(1, 6):
        gh = Greenhouse(
            gh_id=f"GH-{i:03d}",
            gh_name=f"温室{i}号",
            area_sqm=1000.0,
            crop_type=random.choice(list(CropType)),
            crop_variety=f"品种{i}",
            planting_date=date(2025, 1, 1)
        )
        platform.add_greenhouse(gh)
    print(f"已添加 {len(platform.greenhouses)} 个温室")
    
    # 2. 添加传感器设备
    print("\n[2] 添加传感器设备")
    sensor_types = ["temperature", "humidity", "soil_moisture", "light"]
    for gh_id in platform.greenhouses:
        for sensor_type in sensor_types:
            device = SensorDevice(
                device_id=f"DEV-{gh_id}-{sensor_type}",
                device_type=sensor_type,
                greenhouse_id=gh_id,
                status=DeviceStatus.ONLINE
            )
            platform.add_device(device)
    print(f"已添加 {len(platform.devices)} 个传感器")
    
    # 3. 数据采集
    print("\n[3] 环境数据采集")
    for gh_id in list(platform.greenhouses.keys())[:3]:
        data = platform.collect_sensor_data(gh_id)
        print(f"  {gh_id}: 温度={data.temperature:.1f}°C, "
              f"湿度={data.humidity:.1f}%, "
              f"土壤湿度={data.soil_moisture:.1f}%")
    
    # 4. 环境检查
    print("\n[4] 环境监控")
    for gh_id in list(platform.greenhouses.keys())[:2]:
        check = platform.check_environment(gh_id)
        print(f"  {gh_id}:")
        if check.get('abnormalities'):
            print(f"    异常: {check['abnormalities']}")
        if check.get('suggestions'):
            print(f"    建议: {check['suggestions']}")
    
    # 5. 智能灌溉
    print("\n[5] 智能灌溉")
    task = platform.create_irrigation_task(
        "GH-001", 30, 500,
        fertilizer="氮磷钾复合肥", fertilizer_amount=2.5
    )
    print(f"创建灌溉任务: {task.task_id}")
    print(f"  水量: {task.water_amount_liters}L")
    print(f"  肥料: {task.fertilizer_type} {task.fertilizer_amount}kg")
    
    # 6. 病虫害检测
    print("\n[6] 病虫害检测")
    for gh_id in list(platform.greenhouses.keys())[:2]:
        detection = platform.detect_pest(gh_id, f"/images/{gh_id}.jpg")
        print(f"  {gh_id}: {detection.recommendation}")
    
    # 7. 产量预测
    print("\n[7] 产量预测")
    for gh_id in list(platform.greenhouses.keys())[:2]:
        forecast = platform.get_yield_forecast(gh_id)
        print(f"  {gh_id} ({forecast['crop_type']}): "
              f"预计产量 {forecast['expected_yield_kg']}kg")
    
    # 8. 日报
    print("\n[8] 运营日报")
    report = platform.generate_daily_report()
    print(f"温室总数: {report['total_greenhouses']}")
    print(f"在线设备: {report['online_devices']}/{report['total_devices']}")
    print(f"异常温室: {report['abnormal_greenhouses']}")
    print(f"今日灌溉: {report['today_irrigation_tasks']}次")


if __name__ == "__main__":
    main()
```

### 2.6 效果评估

| 指标 | 基线值 | 目标值 | 实际值 | 达成率 |
|------|--------|--------|--------|--------|
| 作物品质稳定性 | 基准 | 提升30% | 提升35% | 117% |
| 水肥利用率 | 50% | ≥85% | 88% | 104% |
| 病虫害损失 | 15% | 降低50% | 降低60% | 120% |
| 人工投入 | 基准 | 减少40% | 减少45% | 113% |

**ROI分析**：
- 项目总投资：1500万元
- 年度总收益：4000万元
- **投资回收期：4.5个月**
- **3年ROI：700%**

---

## 3. 案例总结

**关键成功因素**：
1. 传感器稳定性是基础
2. 精准控制是核心
3. 数据分析是增值

**技术演进方向**：
1. AI病虫害识别精度提升
2. 农业机器人广泛应用
3. 数字孪生农场

**创建时间**：2025-01-21  
**最后更新**：2025-02-15
