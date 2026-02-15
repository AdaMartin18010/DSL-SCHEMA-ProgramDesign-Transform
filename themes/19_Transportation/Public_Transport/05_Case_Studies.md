# 公共交通案例研究

## 案例一：深圳公交集团智能调度系统

### 1. 企业背景

**企业名称**：深圳巴士集团股份有限公司  
**行业领域**：城市公共交通服务  
**运营规模**：超过12,000辆公交车，1,200+条公交线路  
**日均客运量**：超过600万人次  
**服务区域**：深圳市全域，覆盖福田、南山、罗湖、宝安、龙岗等10个行政区

深圳公交集团是中国最大的城市公交运营企业之一，承担着深圳市民日常出行的重要使命。随着城市扩张和人口增长，传统的人工调度模式已无法满足复杂的公交运营需求。高峰期车辆拥挤、平峰期空驶率高、乘客等候时间长等问题日益突出，亟需构建智能化的公交调度系统。

#### 业务痛点

1. **供需不匹配严重**：早晚高峰部分线路拥挤度超过120%，而平峰期空驶率高达35%，运力分配严重失衡
2. **调度响应滞后**：人工调度依赖经验判断，突发大客流响应时间超过20分钟，无法及时调整运力
3. **乘客体验差**：高峰期乘客平均等候时间超过15分钟，车内拥挤舒适度差，投诉率居高不下
4. **能源消耗高**：车辆空驶和怠速时间长，单车百公里能耗高于行业平均水平18%
5. **安全监控薄弱**：驾驶员疲劳驾驶、违规操作难以及时发现，年安全事故超过200起

#### 业务目标

1. **精准运力匹配**：实现基于实时客流的动态发车调度，将高峰期拥挤度控制在85%以内
2. **缩短等候时间**：将乘客平均等候时间从15分钟缩短至8分钟以内
3. **降低空驶率**：通过智能调度将平峰期空驶率从35%降低至15%以下
4. **节能减排**：优化行驶策略，实现单车能耗降低20%以上
5. **提升安全水平**：建立全方位安全监控体系，将事故率降低40%以上

---

### 2. 技术挑战

#### 挑战一：大规模实时客流预测

日均600万人次的客流，分布在1,200条线路、超过10,000个站点。需要构建高精度的短时客流预测模型，准确预测未来15-60分钟各站点上下客人数，为调度决策提供依据。

#### 挑战二：多目标动态调度优化

公交调度需要同时优化多个目标：减少乘客等候时间、降低运营成本、保证服务质量、减少车辆空驶等。这些目标之间存在冲突，需要在实时性和最优性之间取得平衡。

#### 挑战三：多模式公交协同

深圳拥有常规公交、BRT快速公交、微循环巴士、定制公交等多种模式。如何实现不同模式间的无缝衔接和协同调度，提升整体公交网络效率是关键挑战。

#### 挑战四：大规模GPS实时处理

12,000辆公交车每10秒上报GPS位置，日均产生超过1亿条轨迹数据。需要构建高并发、低延迟的流处理架构，支持实时位置追踪、到站预测、异常检测等功能。

#### 挑战五：智能信号优先

与交管部门合作，实现公交信号优先。需要根据公交车实时位置、载客情况、晚点程度等因素，动态请求绿灯延长或红灯缩短，最大化公交通行效率。

---

### 3. 代码实现

```python
"""
深圳公交集团智能调度系统 - 核心模块实现
包含：客流预测、智能调度、到站预测、信号优先、安全监控
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq
import json
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')


class BusStatus(Enum):
    """公交车辆状态"""
    IDLE = "idle"                # 待发
    IN_SERVICE = "in_service"    # 运营中
    AT_STOP = "at_stop"          # 到站停靠
    DELAYED = "delayed"          # 晚点
    OUT_OF_SERVICE = "out_of_service"  # 停运
    MAINTENANCE = "maintenance"  # 维保


class AlertType(Enum):
    """告警类型"""
    OVERCROWDING = "overcrowding"      # 过度拥挤
    DELAY = "delay"                    # 车辆晚点
    SKIPPED_STOP = "skipped_stop"      # 跳站
    DRIVER_FATIGUE = "driver_fatigue"  # 疲劳驾驶
    EMERGENCY = "emergency"            # 紧急情况


@dataclass
class GPSPoint:
    """GPS轨迹点"""
    bus_id: str
    route_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed: float           # km/h
    direction: float       # 行驶方向角度
    
    def to_dict(self) -> Dict:
        return {
            'bus_id': self.bus_id,
            'route_id': self.route_id,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed
        }


@dataclass
class BusStop:
    """公交站点"""
    stop_id: str
    stop_name: str
    latitude: float
    longitude: float
    routes: Set[str] = field(default_factory=set)  # 经过该站点的线路
    avg_boarding: float = 0.0      # 平均上车人数
    avg_alighting: float = 0.0     # 平均下车人数
    
    def get_transfer_routes(self) -> Set[str]:
        """获取可换乘线路"""
        return self.routes


@dataclass
class Bus:
    """公交车辆"""
    bus_id: str
    route_id: str
    capacity: int = 80             # 核定载客数
    current_passengers: int = 0    # 当前载客数
    status: BusStatus = BusStatus.IDLE
    current_location: Optional[GPSPoint] = None
    next_stop_index: int = 0       # 下一站索引
    schedule_deviation: int = 0    # 与计划偏差（秒）
    driver_id: Optional[str] = None
    fuel_level: float = 100.0      # 油量%
    
    def get_load_factor(self) -> float:
        """获取满载率"""
        return self.current_passengers / self.capacity if self.capacity > 0 else 0
    
    def is_overcrowded(self, threshold: float = 0.85) -> bool:
        """判断是否拥挤"""
        return self.get_load_factor() > threshold


@dataclass
class Route:
    """公交线路"""
    route_id: str
    route_name: str
    route_type: str = "regular"    # regular/btr/micro/custom
    stops: List[BusStop] = field(default_factory=list)
    distance_km: float = 0.0
    base_interval_minutes: int = 10  # 基础发车间隔
    operating_hours: Tuple[int, int] = (5, 23)  # 运营时间
    fleet_size: int = 20           # 配车数
    
    def get_stop_distance(self, from_idx: int, to_idx: int) -> float:
        """计算站点间距离"""
        if from_idx < 0 or to_idx >= len(self.stops):
            return 0.0
        # 简化的距离计算
        return abs(to_idx - from_idx) * (self.distance_km / max(len(self.stops) - 1, 1))


@dataclass
class PassengerFlow:
    """客流数据"""
    route_id: str
    stop_id: str
    timestamp: datetime
    boarding: int = 0              # 上车人数
    alighting: int = 0             # 下车人数
    load_factor: float = 0.0       # 车厢满载率


class PassengerFlowPredictor:
    """客流预测器"""
    
    def __init__(self):
        self.historical_patterns: Dict = {}  # 历史客流模式
        self.special_events: Dict = {}       # 特殊事件（节假日、大型活动等）
        self.prediction_cache: Dict = {}     # 预测缓存
    
    def train(self, historical_data: List[PassengerFlow]):
        """训练预测模型"""
        # 按路线、站点、时间段聚合历史数据
        for flow in historical_data:
            key = (flow.route_id, flow.stop_id, flow.timestamp.hour)
            if key not in self.historical_patterns:
                self.historical_patterns[key] = {
                    'boarding': [],
                    'alighting': [],
                    'load_factors': []
                }
            self.historical_patterns[key]['boarding'].append(flow.boarding)
            self.historical_patterns[key]['alighting'].append(flow.alighting)
            self.historical_patterns[key]['load_factors'].append(flow.load_factor)
    
    def predict_flow(self, route_id: str, stop_id: str, 
                    target_time: datetime, horizon_minutes: int = 30) -> Dict:
        """
        预测指定站点未来客流
        返回: {'boarding': int, 'alighting': int, 'confidence': float}
        """
        # 获取历史同期数据
        hour = target_time.hour
        key = (route_id, stop_id, hour)
        
        if key not in self.historical_patterns:
            # 无历史数据时返回默认值
            return {'boarding': 10, 'alighting': 10, 'confidence': 0.5}
        
        pattern = self.historical_patterns[key]
        
        # 计算统计特征
        avg_boarding = np.mean(pattern['boarding'])
        avg_alighting = np.mean(pattern['alighting'])
        std_boarding = np.std(pattern['boarding'])
        
        # 时间衰减因子（越近越相关）
        time_factor = 1.0
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # 高峰期
            time_factor = 1.5
        elif 10 <= hour <= 16:  # 平峰期
            time_factor = 0.7
        
        # 特殊事件调整
        if self._is_special_event(target_time):
            time_factor *= 1.3
        
        predicted_boarding = int(avg_boarding * time_factor)
        predicted_alighting = int(avg_alighting * time_factor)
        
        # 置信度计算（数据越多越可靠）
        confidence = min(0.95, 0.5 + len(pattern['boarding']) * 0.01)
        
        return {
            'boarding': predicted_boarding,
            'alighting': predicted_alighting,
            'confidence': confidence,
            'std_boarding': std_boarding
        }
    
    def predict_route_demand(self, route_id: str, 
                            target_time: datetime,
                            horizon_minutes: int = 30) -> Dict:
        """预测整条线路的客流需求"""
        # 获取线路所有站点的预测
        total_boarding = 0
        max_load_factor = 0.0
        
        # 简化为假设线路有20个站点
        for i in range(20):
            stop_id = f"{route_id}_STOP_{i:03d}"
            prediction = self.predict_flow(route_id, stop_id, target_time, horizon_minutes)
            total_boarding += prediction['boarding']
            max_load_factor = max(max_load_factor, prediction.get('load_factor', 0.5))
        
        # 估算所需运力
        required_capacity = int(total_boarding * 1.2)  # 20%冗余
        required_buses = max(1, required_capacity // 60)  # 假设单车载客60人
        
        return {
            'total_demand': total_boarding,
            'required_buses': required_buses,
            'peak_load_factor': max_load_factor,
            'recommended_interval': max(5, 30 // required_buses)  # 建议发车间隔
        }
    
    def _is_special_event(self, date: datetime) -> bool:
        """判断是否为特殊日期"""
        # 周末
        if date.weekday() >= 5:
            return True
        # 节假日（简化处理）
        return False


class BusScheduler:
    """公交调度优化器"""
    
    def __init__(self, flow_predictor: PassengerFlowPredictor):
        self.flow_predictor = flow_predictor
        self.routes: Dict[str, Route] = {}
        self.buses: Dict[str, Bus] = {}
        self.active_trips: Dict[str, Dict] = {}  # 正在执行的任务
        self.dispatch_queue: List[Dict] = []     # 待发车辆队列
    
    def add_route(self, route: Route):
        """添加线路"""
        self.routes[route.route_id] = route
    
    def add_bus(self, bus: Bus):
        """添加车辆"""
        self.buses[bus.bus_id] = bus
    
    def optimize_dispatch(self, route_id: str, 
                         current_time: datetime) -> List[Dict]:
        """
        优化指定线路的发车调度
        返回调度指令列表
        """
        route = self.routes.get(route_id)
        if not route:
            return []
        
        # 预测未来30分钟客流需求
        demand = self.flow_predictor.predict_route_demand(
            route_id, current_time, 30
        )
        
        # 获取当前在线车辆
        active_buses = [
            b for b in self.buses.values()
            if b.route_id == route_id and b.status in [BusStatus.IN_SERVICE, BusStatus.AT_STOP]
        ]
        
        # 计算当前运力供给
        current_supply = sum(b.capacity * 0.7 for b in active_buses)  # 按70%利用率
        
        # 供需差距
        supply_gap = demand['total_demand'] - current_supply
        
        dispatch_plan = []
        
        # 如果供不应求，增加发车
        if supply_gap > 0:
            additional_buses_needed = int(supply_gap / 60) + 1
            available_buses = [
                b for b in self.buses.values()
                if b.route_id == route_id and b.status == BusStatus.IDLE
            ][:additional_buses_needed]
            
            for i, bus in enumerate(available_buses):
                dispatch_plan.append({
                    'action': 'dispatch',
                    'bus_id': bus.bus_id,
                    'route_id': route_id,
                    'departure_time': current_time + timedelta(minutes=i * demand['recommended_interval']),
                    'reason': f'客流预测需求增加，需补充运力'
                })
        
        # 检查是否有车辆晚点严重，需要调整
        for bus in active_buses:
            if bus.schedule_deviation > 300:  # 晚点超过5分钟
                dispatch_plan.append({
                    'action': 'adjust_speed',
                    'bus_id': bus.bus_id,
                    'suggestion': 'skip_less_critical_stops',  # 建议跳站
                    'reason': f'车辆晚点 {bus.schedule_deviation} 秒'
                })
        
        return dispatch_plan
    
    def handle_overcrowding(self, bus_id: str) -> Dict:
        """处理车辆过度拥挤情况"""
        bus = self.buses.get(bus_id)
        if not bus or not bus.is_overcrowded():
            return {}
        
        route = self.routes.get(bus.route_id)
        
        # 寻找前方短驳车辆
        relief_bus = self._find_relief_bus(bus.route_id, bus.current_location)
        
        return {
            'alert_type': AlertType.OVERCROWDING.value,
            'bus_id': bus_id,
            'current_load': bus.current_passengers,
            'load_factor': bus.get_load_factor(),
            'suggested_actions': [
                'notify_passengers_to_wait',
                'dispatch_relief_bus' if relief_bus else 'increase_frequency',
                'request_signal_priority'
            ],
            'relief_bus_id': relief_bus.bus_id if relief_bus else None
        }
    
    def _find_relief_bus(self, route_id: str, 
                        location: GPSPoint) -> Optional[Bus]:
        """寻找支援车辆"""
        # 寻找同线路空闲车辆
        candidates = [
            b for b in self.buses.values()
            if b.route_id == route_id and b.status == BusStatus.IDLE
        ]
        
        if candidates:
            return candidates[0]
        return None
    
    def calculate_headway_adherence(self, route_id: str) -> float:
        """计算发车间隔遵守率"""
        route_buses = [b for b in self.buses.values() if b.route_id == route_id]
        
        if len(route_buses) < 2:
            return 100.0
        
        # 简化的间隔计算
        actual_intervals = []
        sorted_buses = sorted(route_buses, 
                            key=lambda b: b.current_location.timestamp if b.current_location else datetime.min)
        
        for i in range(1, len(sorted_buses)):
            if sorted_buses[i].current_location and sorted_buses[i-1].current_location:
                time_diff = (sorted_buses[i].current_location.timestamp - 
                           sorted_buses[i-1].current_location.timestamp).total_seconds() / 60
                actual_intervals.append(time_diff)
        
        if not actual_intervals:
            return 100.0
        
        target_interval = self.routes[route_id].base_interval_minutes
        adherence_scores = [
            max(0, 100 - abs(actual - target_interval) / target_interval * 100)
            for actual in actual_intervals
        ]
        
        return np.mean(adherence_scores)


class ArrivalTimePredictor:
    """到站时间预测器"""
    
    def __init__(self):
        self.traffic_patterns: Dict = {}
        self.historical_travel_times: Dict = defaultdict(list)
    
    def predict_arrival(self, bus: Bus, target_stop_idx: int,
                       current_time: datetime) -> Dict:
        """
        预测到达指定站点的时间
        返回: {'estimated_arrival': datetime, 'confidence': float, 'delay_risk': str}
        """
        route = bus.route_id
        current_idx = bus.next_stop_index
        
        if current_idx >= target_stop_idx:
            return {
                'estimated_arrival': current_time,
                'confidence': 1.0,
                'delay_risk': 'none'
            }
        
        # 计算剩余距离
        stops_to_travel = target_stop_idx - current_idx
        avg_speed = self._get_historical_speed(route, current_time.hour)
        
        # 考虑实时交通
        traffic_factor = self._get_traffic_factor(route, current_time)
        effective_speed = avg_speed * traffic_factor
        
        # 计算行驶时间（简化：每站之间约2分钟）
        base_travel_time = stops_to_travel * 2  # 分钟
        adjusted_travel_time = base_travel_time / traffic_factor
        
        # 添加停靠时间
        dwell_time = stops_to_travel * 0.5  # 每站停靠30秒
        
        total_minutes = adjusted_travel_time + dwell_time
        estimated_arrival = current_time + timedelta(minutes=total_minutes)
        
        # 置信度（基于历史数据量）
        confidence = min(0.95, 0.7 + len(self.historical_travel_times[route]) * 0.001)
        
        # 晚点风险评估
        delay_risk = 'low'
        if traffic_factor < 0.6:  # 严重拥堵
            delay_risk = 'high'
        elif traffic_factor < 0.8:
            delay_risk = 'medium'
        
        return {
            'estimated_arrival': estimated_arrival,
            'confidence': confidence,
            'delay_risk': delay_risk,
            'travel_time_minutes': total_minutes
        }
    
    def _get_historical_speed(self, route_id: str, hour: int) -> float:
        """获取历史平均速度"""
        # 高峰期速度慢
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return 18.0  # km/h
        return 25.0
    
    def _get_traffic_factor(self, route_id: str, current_time: datetime) -> float:
        """获取交通影响因子（0-1，越小越拥堵）"""
        hour = current_time.hour
        
        # 高峰期拥堵
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return 0.6
        elif 10 <= hour <= 16:
            return 0.9
        else:
            return 1.0
    
    def update_travel_time(self, route_id: str, from_stop: int, 
                          to_stop: int, actual_minutes: float):
        """更新历史行驶时间"""
        key = f"{route_id}_{from_stop}_{to_stop}"
        self.historical_travel_times[key].append(actual_minutes)
        # 保留最近100条记录
        if len(self.historical_travel_times[key]) > 100:
            self.historical_travel_times[key].pop(0)


class TransitSignalPriority:
    """公交信号优先系统"""
    
    def __init__(self):
        self.signal_controllers: Dict = {}  # 信号机控制器
        self.priority_requests: deque = deque(maxlen=1000)  # 优先请求队列
        self.granted_priorities: Dict = {}  # 已授权优先
    
    def request_priority(self, bus: Bus, intersection_id: str,
                        arrival_estimate: datetime) -> Dict:
        """
        请求信号优先
        返回: {'granted': bool, 'green_extension': int, 'red_truncation': int}
        """
        # 评估优先需求等级
        priority_level = self._calculate_priority_level(bus)
        
        request = {
            'bus_id': bus.bus_id,
            'route_id': bus.route_id,
            'intersection_id': intersection_id,
            'estimated_arrival': arrival_estimate,
            'priority_level': priority_level,
            'timestamp': datetime.now()
        }
        
        self.priority_requests.append(request)
        
        # 简化的优先决策逻辑
        if priority_level >= 3:  # 高优先级
            granted = True
            green_extension = 10  # 延长绿灯10秒
            red_truncation = 5    # 缩短红灯5秒
        elif priority_level >= 2:
            granted = True
            green_extension = 5
            red_truncation = 3
        else:
            granted = False
            green_extension = 0
            red_truncation = 0
        
        if granted:
            self.granted_priorities[bus.bus_id] = {
                'intersection_id': intersection_id,
                'granted_at': datetime.now(),
                'green_extension': green_extension
            }
        
        return {
            'granted': granted,
            'priority_level': priority_level,
            'green_extension': green_extension,
            'red_truncation': red_truncation,
            'reason': '晚点补偿' if bus.schedule_deviation > 120 else '常规优先'
        }
    
    def _calculate_priority_level(self, bus: Bus) -> int:
        """计算优先等级 (1-5)"""
        level = 1
        
        # 晚点程度
        if bus.schedule_deviation > 300:  # 晚点>5分钟
            level += 2
        elif bus.schedule_deviation > 120:
            level += 1
        
        # 满载程度
        if bus.is_overcrowded():
            level += 1
        
        # 线路类型（BRT优先）
        if bus.route_id.startswith('BRT'):
            level += 1
        
        return min(5, level)
    
    def get_priority_statistics(self) -> Dict:
        """获取信号优先统计"""
        total_requests = len(self.priority_requests)
        granted_requests = len(self.granted_priorities)
        
        return {
            'total_requests': total_requests,
            'granted_requests': granted_requests,
            'grant_rate': granted_requests / total_requests if total_requests > 0 else 0,
            'avg_green_extension': np.mean([p['green_extension'] 
                                           for p in self.granted_priorities.values()]) if self.granted_priorities else 0
        }


class DriverSafetyMonitor:
    """驾驶员安全监控"""
    
    def __init__(self):
        self.driving_behaviors: Dict[str, deque] = {}  # 驾驶行为历史
        self.fatigue_records: Dict[str, Dict] = {}     # 疲劳记录
        self.safety_scores: Dict[str, float] = {}      # 安全评分
        self.alert_thresholds = {
            'continuous_driving_minutes': 240,  # 4小时
            'harsh_braking_per_hour': 5,
            'speeding_count_per_day': 3
        }
    
    def record_behavior(self, driver_id: str, behavior_type: str, 
                       timestamp: datetime, severity: float = 1.0):
        """记录驾驶行为"""
        if driver_id not in self.driving_behaviors:
            self.driving_behaviors[driver_id] = deque(maxlen=1000)
        
        self.driving_behaviors[driver_id].append({
            'type': behavior_type,
            'timestamp': timestamp,
            'severity': severity
        })
    
    def check_fatigue(self, driver_id: str, 
                     current_shift_start: datetime) -> Dict:
        """检查疲劳驾驶"""
        continuous_hours = (datetime.now() - current_shift_start).total_seconds() / 3600
        
        if continuous_hours > 4:
            return {
                'alert': True,
                'level': 'critical',
                'message': f'连续驾驶超过4小时，必须立即休息',
                'continuous_hours': continuous_hours
            }
        elif continuous_hours > 3:
            return {
                'alert': True,
                'level': 'warning',
                'message': f'连续驾驶接近4小时，建议尽快休息',
                'continuous_hours': continuous_hours
            }
        
        return {'alert': False}
    
    def calculate_safety_score(self, driver_id: str) -> Dict:
        """计算驾驶员安全评分"""
        behaviors = list(self.driving_behaviors.get(driver_id, []))
        
        if not behaviors:
            return {'score': 100, 'risk_level': 'low'}
        
        # 计算各类违规次数
        today = datetime.now().date()
        today_behaviors = [b for b in behaviors if b['timestamp'].date() == today]
        
        harsh_braking = sum(1 for b in today_behaviors if b['type'] == 'harsh_braking')
        speeding = sum(1 for b in today_behaviors if b['type'] == 'speeding')
        fatigue_alerts = sum(1 for b in today_behaviors if b['type'] == 'fatigue')
        
        # 扣分计算
        deductions = (
            harsh_braking * 3 +
            speeding * 5 +
            fatigue_alerts * 10
        )
        
        score = max(0, 100 - deductions)
        
        # 风险等级
        if score >= 90:
            risk_level = 'low'
        elif score >= 70:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        self.safety_scores[driver_id] = score
        
        return {
            'score': score,
            'risk_level': risk_level,
            'today_violations': {
                'harsh_braking': harsh_braking,
                'speeding': speeding,
                'fatigue_alerts': fatigue_alerts
            }
        }
    
    def generate_alerts(self, driver_id: str) -> List[Dict]:
        """生成安全告警"""
        alerts = []
        score_info = self.calculate_safety_score(driver_id)
        
        if score_info['score'] < 60:
            alerts.append({
                'type': AlertType.DRIVER_FATIGUE.value,
                'level': 'critical',
                'driver_id': driver_id,
                'message': f'驾驶员安全评分过低: {score_info["score"]}，建议暂停运营',
                'score': score_info['score']
            })
        
        return alerts


class PublicTransportSystem:
    """公共交通系统主类"""
    
    def __init__(self):
        self.flow_predictor = PassengerFlowPredictor()
        self.scheduler = BusScheduler(self.flow_predictor)
        self.arrival_predictor = ArrivalTimePredictor()
        self.signal_priority = TransitSignalPriority()
        self.safety_monitor = DriverSafetyMonitor()
        
        self.routes: Dict[str, Route] = {}
        self.buses: Dict[str, Bus] = {}
        self.stops: Dict[str, BusStop] = {}
        self.all_alerts: List[Dict] = []
    
    def register_route(self, route: Route):
        """注册线路"""
        self.routes[route.route_id] = route
        self.scheduler.add_route(route)
        
        # 注册站点
        for stop in route.stops:
            if stop.stop_id not in self.stops:
                self.stops[stop.stop_id] = stop
            self.stops[stop.stop_id].routes.add(route.route_id)
    
    def register_bus(self, bus: Bus):
        """注册车辆"""
        self.buses[bus.bus_id] = bus
        self.scheduler.add_bus(bus)
    
    def update_bus_location(self, gps_point: GPSPoint) -> List[Dict]:
        """更新车辆位置"""
        bus = self.buses.get(gps_point.bus_id)
        if not bus:
            return []
        
        bus.current_location = gps_point
        
        alerts = []
        
        # 检查是否到站
        route = self.routes.get(bus.route_id)
        if route and bus.next_stop_index < len(route.stops):
            next_stop = route.stops[bus.next_stop_index]
            distance = self._calculate_distance(
                gps_point.latitude, gps_point.longitude,
                next_stop.latitude, next_stop.longitude
            )
            
            if distance < 0.05:  # 小于50米认为到站
                bus.status = BusStatus.AT_STOP
                bus.next_stop_index += 1
        
        # 检查拥挤度
        if bus.is_overcrowded():
            alert = self.scheduler.handle_overcrowding(bus.bus_id)
            if alert:
                alerts.append(alert)
        
        # 驾驶行为监控
        if gps_point.speed > 60:  # 公交车超速
            self.safety_monitor.record_behavior(
                bus.driver_id, 'speeding', datetime.now()
            )
        
        self.all_alerts.extend(alerts)
        return alerts
    
    def _calculate_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """计算两点距离（公里）"""
        R = 6371
        lat1_rad, lat2_rad = np.radians(lat1), np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c
    
    def get_passenger_info(self, stop_id: str, route_id: str) -> Dict:
        """获取乘客信息（用于电子站牌）"""
        stop = self.stops.get(stop_id)
        if not stop:
            return {}
        
        # 查找即将到达的车辆
        arriving_buses = []
        for bus in self.buses.values():
            if bus.route_id == route_id and bus.status in [BusStatus.IN_SERVICE, BusStatus.AT_STOP]:
                prediction = self.arrival_predictor.predict_arrival(
                    bus, bus.next_stop_index, datetime.now()
                )
                arriving_buses.append({
                    'bus_id': bus.bus_id,
                    'estimated_arrival': prediction['estimated_arrival'].strftime('%H:%M'),
                    'delay_risk': prediction['delay_risk'],
                    'load_factor': bus.get_load_factor()
                })
        
        arriving_buses.sort(key=lambda x: x['estimated_arrival'])
        
        return {
            'stop_name': stop.stop_name,
            'next_buses': arriving_buses[:3]  # 最近3班车
        }
    
    def get_operation_dashboard(self) -> Dict:
        """获取运营仪表盘"""
        total_buses = len(self.buses)
        in_service = sum(1 for b in self.buses.values() if b.status == BusStatus.IN_SERVICE)
        at_stop = sum(1 for b in self.buses.values() if b.status == BusStatus.AT_STOP)
        idle = sum(1 for b in self.buses.values() if b.status == BusStatus.IDLE)
        
        overcrowded = sum(1 for b in self.buses.values() if b.is_overcrowded())
        delayed = sum(1 for b in self.buses.values() if b.schedule_deviation > 120)
        
        avg_load_factor = np.mean([b.get_load_factor() for b in self.buses.values()]) if self.buses else 0
        
        return {
            'total_buses': total_buses,
            'in_service': in_service,
            'at_stop': at_stop,
            'idle': idle,
            'overcrowded_buses': overcrowded,
            'delayed_buses': delayed,
            'avg_load_factor': f"{avg_load_factor*100:.1f}%",
            'system_alerts': len(self.all_alerts)
        }


# ==================== 使用示例 ====================

def demo():
    """演示公交调度系统的使用"""
    
    # 初始化系统
    transit_system = PublicTransportSystem()
    
    # 创建线路
    route1_stops = [
        BusStop(f"R1_S{i:03d}", f"站点{i}", 22.5 + i*0.01, 114.0 + i*0.01)
        for i in range(20)
    ]
    route1 = Route(
        route_id="M201",
        route_name="201路",
        route_type="regular",
        stops=route1_stops,
        distance_km=25.0,
        base_interval_minutes=8,
        fleet_size=30
    )
    transit_system.register_route(route1)
    
    # 注册车辆
    for i in range(10):
        bus = Bus(
            bus_id=f"B{100+i}",
            route_id="M201",
            capacity=80,
            current_passengers=np.random.randint(30, 90),
            driver_id=f"D{100+i}"
        )
        transit_system.register_bus(bus)
    
    # 训练客流预测模型
    historical_flows = []
    for hour in range(5, 23):
        for stop_idx in range(20):
            # 模拟高峰期高客流
            base_boarding = 50 if 7 <= hour <= 9 or 17 <= hour <= 19 else 20
            historical_flows.append(PassengerFlow(
                route_id="M201",
                stop_id=f"R1_S{stop_idx:03d}",
                timestamp=datetime(2024, 1, 15, hour, 0),
                boarding=base_boarding + np.random.randint(-5, 5),
                alighting=base_boarding - 5 + np.random.randint(-3, 3)
            ))
    
    transit_system.flow_predictor.train(historical_flows)
    
    print("=" * 60)
    print("深圳公交智能调度系统演示")
    print("=" * 60)
    
    # 客流预测演示
    print("\n📊 客流预测")
    print("-" * 40)
    current_time = datetime(2024, 1, 15, 8, 0)  # 早高峰
    demand = transit_system.flow_predictor.predict_route_demand("M201", current_time)
    print(f"线路 M201 未来30分钟预测:")
    print(f"  预计客流需求: {demand['total_demand']} 人次")
    print(f"  建议投入车辆: {demand['required_buses']} 辆")
    print(f"  推荐发车间隔: {demand['recommended_interval']} 分钟")
    
    # 调度优化演示
    print("\n🚌 智能调度")
    print("-" * 40)
    dispatch_plan = transit_system.scheduler.optimize_dispatch("M201", current_time)
    print(f"生成调度指令 {len(dispatch_plan)} 条:")
    for cmd in dispatch_plan:
        print(f"  [{cmd['action']}] 车辆 {cmd['bus_id']} - {cmd['reason']}")
    
    # 到站预测演示
    print("\n⏱️ 到站时间预测")
    print("-" * 40)
    test_bus = transit_system.buses["B100"]
    test_bus.current_location = GPSPoint(
        "B100", "M201", current_time, 22.52, 114.02, 25.0, 0.0
    )
    test_bus.next_stop_index = 3
    
    prediction = transit_system.arrival_predictor.predict_arrival(
        test_bus, 5, current_time
    )
    print(f"车辆 B100 到达第5站预测:")
    print(f"  预计到达: {prediction['estimated_arrival'].strftime('%H:%M:%S')}")
    print(f"  置信度: {prediction['confidence']*100:.1f}%")
    print(f"  晚点风险: {prediction['delay_risk']}")
    
    # 信号优先演示
    print("\n🚦 信号优先")
    print("-" * 40)
    test_bus.schedule_deviation = 180  # 晚点3分钟
    priority_result = transit_system.signal_priority.request_priority(
        test_bus, "INT_001", current_time + timedelta(minutes=5)
    )
    print(f"车辆 B100 信号优先请求:")
    print(f"  是否授权: {'是' if priority_result['granted'] else '否'}")
    print(f"  优先等级: {priority_result['priority_level']}/5")
    print(f"  绿灯延长: {priority_result['green_extension']} 秒")
    
    # 安全监控演示
    print("\n👮 安全监控")
    print("-" * 40)
    
    # 模拟危险驾驶行为
    for _ in range(3):
        transit_system.safety_monitor.record_behavior("D100", "harsh_braking", current_time)
    transit_system.safety_monitor.record_behavior("D100", "speeding", current_time)
    
    safety_report = transit_system.safety_monitor.calculate_safety_score("D100")
    print(f"驾驶员 D100 安全评估:")
    print(f"  安全评分: {safety_report['score']}/100")
    print(f"  风险等级: {safety_report['risk_level']}")
    print(f"  今日违规: {safety_report['today_violations']}")
    
    # 运营仪表盘
    print("\n📈 运营仪表盘")
    print("-" * 40)
    dashboard = transit_system.get_operation_dashboard()
    print(f"总车辆数: {dashboard['total_buses']}")
    print(f"运营中: {dashboard['in_service']} | 到站: {dashboard['at_stop']} | 待发: {dashboard['idle']}")
    print(f"拥挤车辆: {dashboard['overcrowded_buses']} | 晚点车辆: {dashboard['delayed_buses']}")
    print(f"平均满载率: {dashboard['avg_load_factor']}")
    
    # 乘客信息展示
    print("\n🚏 电子站牌信息")
    print("-" * 40)
    passenger_info = transit_system.get_passenger_info("R1_S005", "M201")
    print(f"站点: {passenger_info.get('stop_name', 'N/A')}")
    print("即将到站:")
    for bus in passenger_info.get('next_buses', []):
        crowd_status = "拥挤" if bus['load_factor'] > 0.8 else "舒适"
        print(f"  {bus['bus_id']} - {bus['estimated_arrival']} ({crowd_status})")
    
    print("\n" + "=" * 60)
    print("系统演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
```

---

### 4. 效果评估

#### 性能指标

| 指标项 | 实施前 | 实施后 | 改善幅度 |
|--------|--------|--------|----------|
| 高峰拥挤度 | 120%+ | 82% | ↓ 31.7% |
| 平均等候时间 | 15.2分钟 | 7.8分钟 | ↓ 48.7% |
| 平峰空驶率 | 35% | 12% | ↓ 65.7% |
| 单车百公里能耗 | 42L | 33L | ↓ 21.4% |
| 年安全事故数 | 208起 | 115起 | ↓ 44.7% |
| 乘客满意度 | 76% | 91% | ↑ 19.7% |
| 准点率 | 72% | 89% | ↑ 23.6% |

#### ROI分析

**投资成本**：
- 系统开发：4,500万元
- 车载设备（GPS、客流计数器等）：6,800万元
- 调度中心建设：1,200万元
- 人员培训：800万元
- **总投资**：13,300万元

**年度收益**：
- 能源成本节约：12,000万元/年
- 人力成本优化（调度员减少）：3,500万元/年
- 事故损失减少：2,200万元/年
- 广告收入增加（电子站牌）：1,800万元/年
- **年度总收益**：19,500万元/年

**投资回报**：
- 投资回收期：8.2个月
- 5年累计净收益：84,200万元
- 5年ROI：533%

#### 经验教训

**成功因素**：
1. **数据驱动决策**：建立了覆盖全集团的数据采集和分析体系，所有调度决策基于实时数据
2. **产学研合作**：与清华大学、哈工大合作开发核心算法，确保技术领先性
3. **以人为本**：重视驾驶员培训和参与，通过激励机制提升配合度
4. **政府支持**：获得市交通局、交警局大力支持，实现公交信号优先

**面临的挑战**：
1. **初期准确率问题**：客流预测初期准确率仅75%，通过积累数据和模型迭代提升至92%
2. **司机抵触情绪**：部分老司机对系统不信任，通过示范线路和激励机制逐步化解
3. **极端天气应对**：暴雨等极端天气下系统稳定性受影响，建立了应急预案

**最佳实践**：
1. 建立"调度中心-分公司-线路"三级响应机制，确保异常情况快速处理
2. 开发乘客APP，提供实时到站信息，提升服务体验
3. 建立数据质量监控体系，每日核查数据准确性
4. 与地铁、共享单车数据打通，实现多模式协同

---

## 案例二：杭州公交"云公交"智慧出行系统

### 1. 企业背景

**企业名称**：杭州市公共交通集团有限公司  
**创新模式**："云公交"定制公交  
**运营规模**：超过10,000辆公交车，800+条线路  
**特色服务**：需求响应式公交、社区微公交、旅游专线

#### 业务痛点

1. **固定线路僵化**：传统固定线路无法满足乘客多样化出行需求
2. **社区出行难**：大型社区到地铁站的"最后一公里"问题突出
3. **旅游资源闲置**：景区间公交线路规划不合理，游客体验差
4. **信息不对称**：乘客无法获取准确的到站时间和车厢拥挤度
5. **支付方式落后**：多种支付方式并存，乘车效率低

#### 业务目标

1. **按需响应**：实现基于乘客预约的动态线路生成和车辆调度
2. **微循环覆盖**：解决社区、园区内的短途接驳需求
3. **旅游一体化**：构建景区间的无缝公交网络
4. **信息透明化**：提供实时、准确的公交信息服务
5. **支付一体化**：实现一码通行，提升乘车效率

---

### 2. 技术挑战

1. **动态路径规划**：根据实时预约请求，动态生成最优行驶路线
2. **需求聚合算法**：将分散的出行需求智能聚合，平衡服务质量和运营成本
3. **多模式协同**：实现常规公交、地铁、共享单车、步行的无缝衔接
4. **实时客流统计**：基于视频AI的精准客流计数和车厢拥挤度分析
5. **大规模并发处理**：支持百万级用户同时查询和预约

---

### 3. 效果评估

#### 核心指标改善

| 指标 | 改善效果 |
|------|----------|
| 云公交预约响应时间 | < 3分钟 |
| 社区微公交覆盖率 | 从60%提升至95% |
| 乘客平均步行距离 | 减少42% |
| 景区公交满意度 | 从78%提升至94% |
| APP月活用户 | 超过500万 |

#### 创新亮点

1. **AI智能派单**：基于深度强化学习的动态派单算法，实现需求与运力的最优匹配
2. **数字孪生站台**：AR技术实现虚拟线路规划和实时车辆位置展示
3. **碳积分体系**：绿色出行可累积碳积分，兑换公交优惠，提升用户粘性

---

*文档版本: v1.0 | 最后更新: 2026-02-15*
