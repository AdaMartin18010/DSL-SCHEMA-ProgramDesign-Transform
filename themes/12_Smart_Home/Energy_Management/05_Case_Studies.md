# 能源管理案例研究

## 案例一：绿能科技智慧能耗管理平台

### 企业背景

**绿能科技有限公司**（以下简称"绿能科技"）成立于2012年，总部位于苏州，是国内领先的智慧能源管理解决方案提供商。公司专注于为商业建筑、工业园区、数据中心、医院学校等场景提供AI驱动的能源管理系统，助力客户实现节能减排目标。

**企业基本信息：**
- **成立时间**：2012年
- **总部位置**：苏州工业园区
- **员工规模**：380人（能源专家40人，算法研发60人，软件研发100人，工程实施120人，运营服务60人）
- **年营收**：6.8亿元人民币
- **服务客户**：商业综合体150个、工业园区45个、公共建筑80栋
- **核心产品**：智慧能耗监测平台、AI空调节能系统、照明智能控制系统、光伏储能管理系统、碳排放管理平台

**市场定位**：面向年能耗成本500万元以上的中大型客户，提供端到端的能源管理解决方案，帮助客户实现15%-30%的能耗节约。

### 业务痛点

1. **能耗数据不透明**
   - 缺乏分项计量，只能获取总表数据，无法定位高耗能设备
   - 能耗数据以月度账单形式呈现，实时性极差
   - 各系统（电力、空调、照明、动力）数据分散，无法关联分析
   - 缺少与业务量、天气、人流等外部因素的关联分析

2. **空调系统能耗高企**
   - 中央空调系统占建筑总能耗的40%-60%
   - 空调温度设置依赖人工经验，无法根据负荷动态调节
   - 冷热源设备运行策略粗放，部分负荷下效率低下
   - 新风量控制固定，无法根据CO2浓度自动调节

3. **照明控制粗放**
   - 公共区域照明24小时常亮，无法按需控制
   - 自然光利用不足，人工照明与自然光未联动
   - 分区控制粒度粗，无法根据人员分布精确控制
   - 缺乏故障监测，损坏灯具不能及时发现更换

4. **缺乏预测性维护**
   - 设备维护依赖定期巡检，效率低下
   - 设备故障多为事后发现，影响正常运营
   - 无法根据设备运行状态预测剩余寿命
   - 维护计划制定缺乏数据支撑，资源分配不合理

5. **碳排放管理困难**
   - 碳排放数据手工统计，准确性差
   - 缺乏碳足迹追踪，无法识别减排重点
   - 无法自动生成碳排放报告，应对监管核查压力大
   - 缺乏碳交易决策支持，无法优化碳资产配置

### 业务目标

1. **建立精细化能耗监测体系**
   - 实现设备级、区域级、系统级三级分项计量
   - 能耗数据5分钟级采集，实时可视化展示
   - 建立能耗基准线，支持同比环比分析
   - 实现能耗异常自动告警，15分钟内推送

2. **AI驱动空调系统节能**
   - 部署AI优化控制算法，自动调节空调运行参数
   - 实现冷热负荷预测，提前30分钟预调节
   - 优化设备启停策略，提升系统COP 15%以上
   - 根据人员密度动态调节新风量，节省新风能耗20%

3. **智能照明系统改造**
   - 部署人体感应+光照感应双模控制
   - 实现自然光自适应调光，最大化利用自然光
   - 建立照明分区控制策略，按需照明
   - 灯具故障自动监测，24小时内完成维修响应

4. **构建设备预测性维护平台**
   - 建立设备健康度评估模型，实时评分
   - 实现故障提前7天预警，准确率85%以上
   - 优化维护计划，降低维护成本20%
   - 延长关键设备使用寿命15%以上

5. **碳排放数字化管理**
   - 建立碳排放自动核算体系，数据实时更新
   - 实现产品级碳足迹追踪，识别减排机会
   - 自动生成碳排放报告，支持监管合规
   - 提供碳交易策略建议，优化碳资产价值

### 技术挑战

1. **多源异构数据集成**
   - 需对接电力、水、燃气、冷热等多种能源计量系统
   - 通信协议多样：Modbus、BACnet、OPC UA、MQTT等
   - 数据质量参差不齐，需清洗与校验
   - 时序数据量大，单客户日均数据点可达1000万+

2. **空调系统AI建模**
   - 需建立建筑热动力学模型，参数多且耦合复杂
   - 冷热负荷受天气、人员、设备散热等多因素影响
   - AI模型需适应不同建筑类型与气候区域
   - 控制策略需在舒适度与节能间平衡

3. **实时优化控制**
   - 控制指令需秒级响应，延迟要求<5秒
   - 需处理大量并发控制请求（单项目设备点可达10万+）
   - 控制决策需考虑设备约束与安全边界
   - 系统故障时需平滑降级，保证基本功能

4. **时序数据存储与分析**
   - 需支持高并发写入（10万+点/秒）
   - 历史数据需保留5年以上，存储成本需可控
   - 聚合查询需秒级响应，支撑实时分析
   - 需支持降采样与数据压缩

5. **边缘云协同架构**
   - 边缘节点需具备本地自治能力
   - 网络中断时需保证本地控制不中断
   - 云端需汇聚多项目数据，支撑全局优化
   - 模型训练在云端，推理在边缘，需高效协同

### 代码实现

```python
"""
绿能科技智慧能耗管理平台 - 核心模块实现
包含：数据采集、能耗分析、AI优化控制、碳排放管理、预测性维护
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Tuple
from collections import defaultdict
import numpy as np
from sklearn.ensemble import IsolationForest, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnergyType(Enum):
    """能源类型"""
    ELECTRICITY = "electricity"  # 电力
    WATER = "water"              # 水
    GAS = "gas"                  # 天然气
    STEAM = "steam"              # 蒸汽
    COOLING = "cooling"          # 冷量
    HEATING = "heating"          # 热量


class DeviceCategory(Enum):
    """设备类别"""
    HVAC = "hvac"               # 暖通空调
    LIGHTING = "lighting"       # 照明
    POWER = "power"             # 动力
    IT = "it"                   # IT设备
    OTHER = "other"             # 其他


@dataclass
class MeterReading:
    """仪表读数"""
    meter_id: str
    energy_type: EnergyType
    timestamp: float
    value: float           # 累计值
    delta: float          # 本次读数差值
    power: Optional[float] = None  # 瞬时功率
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'meter_id': self.meter_id,
            'energy_type': self.energy_type.value,
            'timestamp': self.timestamp,
            'value': self.value,
            'delta': self.delta,
            'power': self.power
        }


@dataclass
class EnergyDevice:
    """能源设备"""
    device_id: str
    name: str
    category: DeviceCategory
    rated_power: float    # 额定功率(kW)
    location: str
    meter_id: str
    status: str = "normal"
    health_score: float = 100.0  # 健康度评分
    last_maintenance: float = 0.0
    
    def __post_init__(self):
        if isinstance(self.category, str):
            self.category = DeviceCategory(self.category)


class EnergyDatabase:
    """能源数据库管理器"""
    
    def __init__(self, db_path: str = "energy_management.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 仪表数据表（按小时分区存储）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meter_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meter_id TEXT NOT NULL,
                energy_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                value REAL,
                delta REAL,
                power REAL,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # 设备表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_devices (
                device_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                rated_power REAL,
                location TEXT,
                meter_id TEXT,
                status TEXT DEFAULT 'normal',
                health_score REAL DEFAULT 100.0,
                last_maintenance REAL,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # 能耗统计表（按日汇总）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meter_id TEXT NOT NULL,
                energy_type TEXT NOT NULL,
                total_consumption REAL,
                peak_power REAL,
                avg_power REAL,
                min_power REAL,
                cost_estimate REAL,
                UNIQUE(date, meter_id)
            )
        ''')
        
        # 碳排放表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                scope TEXT NOT NULL,  # scope1, scope2, scope3
                emission_source TEXT,
                energy_type TEXT,
                consumption REAL,
                emission_factor REAL,
                carbon_kg REAL,
                UNIQUE(date, scope, emission_source)
            )
        ''')
        
        # 告警表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT,
                severity TEXT,
                meter_id TEXT,
                device_id TEXT,
                description TEXT,
                threshold_value REAL,
                actual_value REAL,
                status TEXT DEFAULT 'active',
                created_at REAL,
                resolved_at REAL
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_meter_time ON meter_readings(meter_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_type_time ON meter_readings(energy_type, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_date ON energy_daily_stats(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_carbon_date ON carbon_emissions(date)')
        
        conn.commit()
        conn.close()
        logger.info("能源数据库初始化完成")
    
    def save_meter_reading(self, reading: MeterReading):
        """保存仪表读数"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meter_readings (meter_id, energy_type, timestamp, value, delta, power)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            reading.meter_id, reading.energy_type.value, reading.timestamp,
            reading.value, reading.delta, reading.power
        ))
        conn.commit()
    
    def get_readings(self, meter_id: str, start_time: float, end_time: float) -> List[MeterReading]:
        """获取仪表读数"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM meter_readings 
            WHERE meter_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        ''', (meter_id, start_time, end_time))
        
        readings = []
        for row in cursor.fetchall():
            readings.append(MeterReading(
                meter_id=row['meter_id'],
                energy_type=EnergyType(row['energy_type']),
                timestamp=row['timestamp'],
                value=row['value'],
                delta=row['delta'],
                power=row['power']
            ))
        return readings
    
    def save_daily_stats(self, date: str, meter_id: str, energy_type: EnergyType,
                         consumption: float, peak: float, avg: float, min_p: float, cost: float):
        """保存日统计数据"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO energy_daily_stats 
            (date, meter_id, energy_type, total_consumption, peak_power, avg_power, min_power, cost_estimate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, meter_id, energy_type.value, consumption, peak, avg, min_p, cost))
        conn.commit()
    
    def save_carbon_emission(self, date: str, scope: str, source: str,
                            energy_type: EnergyType, consumption: float,
                            factor: float, carbon_kg: float):
        """保存碳排放数据"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO carbon_emissions 
            (date, scope, emission_source, energy_type, consumption, emission_factor, carbon_kg)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, scope, source, energy_type.value, consumption, factor, carbon_kg))
        conn.commit()
    
    def get_carbon_report(self, start_date: str, end_date: str) -> Dict:
        """获取碳排放报告"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT scope, SUM(carbon_kg) as total_carbon
            FROM carbon_emissions
            WHERE date BETWEEN ? AND ?
            GROUP BY scope
        ''', (start_date, end_date))
        
        result = {'scope1': 0, 'scope2': 0, 'scope3': 0, 'total': 0}
        for row in cursor.fetchall():
            result[row['scope']] = row['total_carbon']
            result['total'] += row['total_carbon']
        
        return result


class DataCollector:
    """数据采集器 - 支持多种通信协议"""
    
    def __init__(self, db: EnergyDatabase):
        self.db = db
        self.collectors: Dict[str, 'BaseCollector'] = {}
        self._running = True
        self._callbacks: List[Callable[[MeterReading], None]] = []
    
    def register_collector(self, meter_id: str, collector: 'BaseCollector'):
        """注册数据采集器"""
        self.collectors[meter_id] = collector
    
    def add_callback(self, callback: Callable[[MeterReading], None]):
        """添加数据回调"""
        self._callbacks.append(callback)
    
    def start(self):
        """启动采集"""
        for meter_id, collector in self.collectors.items():
            threading.Thread(target=self._collect_loop, args=(meter_id, collector), daemon=True).start()
    
    def _collect_loop(self, meter_id: str, collector: 'BaseCollector'):
        """采集循环"""
        last_value = None
        while self._running:
            try:
                reading_data = collector.read()
                if reading_data is not None:
                    current_value = reading_data['value']
                    delta = current_value - last_value if last_value is not None else 0
                    
                    reading = MeterReading(
                        meter_id=meter_id,
                        energy_type=collector.energy_type,
                        timestamp=time.time(),
                        value=current_value,
                        delta=delta,
                        power=reading_data.get('power')
                    )
                    
                    # 保存到数据库
                    self.db.save_meter_reading(reading)
                    
                    # 通知回调
                    for callback in self._callbacks:
                        try:
                            callback(reading)
                        except Exception as e:
                            logger.error(f"数据回调异常: {e}")
                    
                    last_value = current_value
                
                time.sleep(collector.interval)
            except Exception as e:
                logger.error(f"采集异常 {meter_id}: {e}")
                time.sleep(5)


class BaseCollector(ABC):
    """数据采集器基类"""
    
    def __init__(self, energy_type: EnergyType, interval: int = 300):
        self.energy_type = energy_type
        self.interval = interval  # 采集间隔（秒）
    
    @abstractmethod
    def read(self) -> Optional[Dict]:
        """读取数据"""
        pass


class ModbusCollector(BaseCollector):
    """Modbus RTU/TCP 采集器"""
    
    def __init__(self, host: str, port: int, register: int, energy_type: EnergyType):
        super().__init__(energy_type, interval=60)
        self.host = host
        self.port = port
        self.register = register
    
    def read(self) -> Optional[Dict]:
        # 模拟Modbus读取
        # 实际应使用pymodbus库
        return {'value': np.random.uniform(1000, 5000), 'power': np.random.uniform(50, 200)}


class MqttCollector(BaseCollector):
    """MQTT 采集器"""
    
    def __init__(self, topic: str, energy_type: EnergyType):
        super().__init__(energy_type, interval=60)
        self.topic = topic
    
    def read(self) -> Optional[Dict]:
        # 模拟MQTT数据
        return {'value': np.random.uniform(1000, 5000), 'power': np.random.uniform(50, 200)}


class EnergyAnalyzer:
    """能耗分析器"""
    
    def __init__(self, db: EnergyDatabase):
        self.db = db
        self.baseline_model = None
        self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = StandardScaler()
        self._is_fitted = False
    
    def analyze_consumption_pattern(self, meter_id: str, days: int = 30) -> Dict:
        """分析能耗模式"""
        end_time = time.time()
        start_time = end_time - days * 24 * 3600
        
        readings = self.db.get_readings(meter_id, start_time, end_time)
        
        if len(readings) < 24:
            return {'error': '数据不足'}
        
        powers = [r.power for r in readings if r.power is not None]
        if not powers:
            return {'error': '无功率数据'}
        
        # 统计指标
        return {
            'avg_power_kw': np.mean(powers),
            'peak_power_kw': np.max(powers),
            'min_power_kw': np.min(powers),
            'load_factor': np.mean(powers) / np.max(powers) if np.max(powers) > 0 else 0,
            'total_consumption_kwh': sum(r.delta for r in readings),
            'data_points': len(readings)
        }
    
    def detect_anomaly(self, meter_id: str) -> List[Dict]:
        """检测能耗异常"""
        # 获取最近7天数据
        end_time = time.time()
        start_time = end_time - 7 * 24 * 3600
        
        readings = self.db.get_readings(meter_id, start_time, end_time)
        
        if len(readings) < 48:
            return []
        
        anomalies = []
        hourly_consumption = defaultdict(list)
        
        # 按小时分组
        for r in readings:
            hour = datetime.fromtimestamp(r.timestamp).hour
            hourly_consumption[hour].append(r.delta)
        
        # 检测异常小时
        for hour, values in hourly_consumption.items():
            if len(values) < 3:
                continue
            
            mean_val = np.mean(values[:-1])  # 排除最新值
            std_val = np.std(values[:-1])
            latest = values[-1]
            
            if std_val > 0 and abs(latest - mean_val) > 2 * std_val:
                anomalies.append({
                    'hour': hour,
                    'expected': mean_val,
                    'actual': latest,
                    'deviation': (latest - mean_val) / mean_val * 100
                })
        
        return anomalies
    
    def predict_consumption(self, meter_id: str, hours_ahead: int = 24) -> List[float]:
        """预测未来能耗"""
        # 获取历史数据
        end_time = time.time()
        start_time = end_time - 30 * 24 * 3600
        readings = self.db.get_readings(meter_id, start_time, end_time)
        
        if len(readings) < 168:  # 至少需要一周数据
            return []
        
        # 简单的时间序列预测（实际应使用LSTM等深度学习模型）
        powers = [r.power for r in readings if r.power is not None]
        
        # 使用最近7天同时间段的平均值作为预测
        predictions = []
        for i in range(hours_ahead):
            # 获取历史同期数据
            idx = len(powers) - 24 * 7 + (i % 24)
            if idx >= 0:
                predictions.append(powers[idx])
            else:
                predictions.append(np.mean(powers[-24:]))
        
        return predictions


class HVACOptimizer:
    """空调系统AI优化器"""
    
    def __init__(self, db: EnergyDatabase):
        self.db = db
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.comfort_range = {'temp_min': 24, 'temp_max': 26, 'rh_max': 65}
    
    def train_model(self, meter_id: str, weather_data: List[Dict]):
        """训练负荷预测模型"""
        # 获取历史能耗数据
        end_time = time.time()
        start_time = end_time - 90 * 24 * 3600  # 90天数据
        readings = self.db.get_readings(meter_id, start_time, end_time)
        
        if len(readings) < 1000:
            logger.warning("数据不足，无法训练模型")
            return
        
        # 构建特征
        X = []
        y = []
        
        for i, r in enumerate(readings):
            dt = datetime.fromtimestamp(r.timestamp)
            features = [
                dt.hour,  # 小时
                dt.weekday(),  # 星期
                dt.month,  # 月份
                weather_data[i].get('outdoor_temp', 25) if i < len(weather_data) else 25,
                weather_data[i].get('solar_radiation', 500) if i < len(weather_data) else 500,
            ]
            X.append(features)
            y.append(r.power if r.power else 0)
        
        # 训练模型
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("空调负荷预测模型训练完成")
    
    def predict_cooling_load(self, features: List[float]) -> float:
        """预测冷负荷"""
        if not self.is_trained:
            return 0.0
        return self.model.predict([features])[0]
    
    def generate_control_strategy(self, predicted_load: float, current_temp: float,
                                   outdoor_temp: float) -> Dict[str, Any]:
        """生成控制策略"""
        strategy = {
            'chiller_setpoint': 7.0,  # 冷水机组设定温度
            'chilled_water_temp': 6.0,  # 冷冻水供水温度
            'fan_speed': 80,  # 风机转速百分比
            'fresh_air_damper': 30,  # 新风阀开度
            'chiller_count': 1,  # 开启的冷水机组数量
        }
        
        # 根据负荷调整策略
        if predicted_load > 500:  # 高负荷
            strategy['chiller_count'] = 2
            strategy['chiller_setpoint'] = 6.0
            strategy['fan_speed'] = 100
        elif predicted_load < 200:  # 低负荷
            strategy['chiller_count'] = 1
            strategy['chiller_setpoint'] = 8.0
            strategy['fan_speed'] = 50
        
        # 根据室外温度调整新风量
        if outdoor_temp < 20:  # 室外凉爽，可增加新风
            strategy['fresh_air_damper'] = 50
        elif outdoor_temp > 35:  # 室外炎热，减少新风
            strategy['fresh_air_damper'] = 20
        
        return strategy


class CarbonManager:
    """碳排放管理器"""
    
    # 排放因子（kg CO2/单位能源）
    EMISSION_FACTORS = {
        EnergyType.ELECTRICITY: 0.5703,  # 电网平均排放因子
        EnergyType.GAS: 2.162,           # 天然气
        EnergyType.WATER: 0.168,         # 自来水
        EnergyType.STEAM: 0.12,          # 蒸汽
    }
    
    def __init__(self, db: EnergyDatabase):
        self.db = db
    
    def calculate_daily_emission(self, date: str):
        """计算日碳排放"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # 获取当日能耗统计
        cursor.execute('''
            SELECT energy_type, SUM(total_consumption) as consumption
            FROM energy_daily_stats
            WHERE date = ?
            GROUP BY energy_type
        ''', (date,))
        
        for row in cursor.fetchall():
            energy_type = EnergyType(row['energy_type'])
            consumption = row['consumption']
            
            factor = self.EMISSION_FACTORS.get(energy_type, 0)
            carbon_kg = consumption * factor
            
            # 判断排放范围
            if energy_type == EnergyType.ELECTRICITY:
                scope = 'scope2'  # 间接排放
            elif energy_type == EnergyType.GAS:
                scope = 'scope1'  # 直接排放
            else:
                scope = 'scope3'  # 其他间接排放
            
            self.db.save_carbon_emission(
                date, scope, energy_type.value,
                energy_type, consumption, factor, carbon_kg
            )
        
        conn.close()
    
    def generate_report(self, year: int, month: int) -> Dict:
        """生成月度碳排放报告"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        emissions = self.db.get_carbon_report(start_date, end_date)
        
        # 计算环比
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_start = f"{prev_year}-{prev_month:02d}-01"
        prev_end = start_date
        prev_emissions = self.db.get_carbon_report(prev_start, prev_end)
        
        mom_change = 0
        if prev_emissions['total'] > 0:
            mom_change = (emissions['total'] - prev_emissions['total']) / prev_emissions['total'] * 100
        
        return {
            'period': f"{year}年{month}月",
            'total_emission_tons': emissions['total'] / 1000,
            'scope1_tons': emissions.get('scope1', 0) / 1000,
            'scope2_tons': emissions.get('scope2', 0) / 1000,
            'scope3_tons': emissions.get('scope3', 0) / 1000,
            'mom_change_percent': round(mom_change, 2),
            'intensity_per_area': None,  # 需要建筑面积数据
        }


class PredictiveMaintenance:
    """预测性维护模块"""
    
    def __init__(self, db: EnergyDatabase):
        self.db = db
        self.health_threshold = 70.0
    
    def calculate_health_score(self, device: EnergyDevice) -> float:
        """计算设备健康度评分"""
        # 获取设备运行数据
        end_time = time.time()
        start_time = end_time - 30 * 24 * 3600
        readings = self.db.get_readings(device.meter_id, start_time, end_time)
        
        if len(readings) < 100:
            return 100.0
        
        powers = [r.power for r in readings if r.power is not None]
        if not powers:
            return 100.0
        
        # 基于多种指标计算健康度
        scores = []
        
        # 1. 功率稳定性（变异系数）
        cv = np.std(powers) / np.mean(powers) if np.mean(powers) > 0 else 0
        stability_score = max(0, 100 - cv * 100)
        scores.append(stability_score)
        
        # 2. 负载率合理性
        avg_power = np.mean(powers)
        load_ratio = avg_power / device.rated_power if device.rated_power > 0 else 0
        load_score = 100 - abs(load_ratio - 0.7) * 50  # 70%负载率最优
        scores.append(max(0, load_score))
        
        # 3. 维护周期
        days_since_maintenance = (time.time() - device.last_maintenance) / 86400
        maintenance_score = max(0, 100 - days_since_maintenance / 3)  # 3个月降为零
        scores.append(maintenance_score)
        
        # 综合评分
        health_score = np.mean(scores)
        return round(health_score, 1)
    
    def predict_failure(self, device: EnergyDevice) -> Dict:
        """预测设备故障"""
        health_score = self.calculate_health_score(device)
        
        # 更新数据库
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE energy_devices SET health_score = ? WHERE device_id = ?
        ''', (health_score, device.device_id))
        conn.commit()
        conn.close()
        
        prediction = {
            'device_id': device.device_id,
            'device_name': device.name,
            'health_score': health_score,
            'risk_level': 'low',
            'predicted_failure_days': None,
            'recommended_action': '正常运行'
        }
        
        if health_score < 50:
            prediction['risk_level'] = 'critical'
            prediction['predicted_failure_days'] = 7
            prediction['recommended_action'] = '立即安排检修'
        elif health_score < 70:
            prediction['risk_level'] = 'high'
            prediction['predicted_failure_days'] = 30
            prediction['recommended_action'] = '计划维护'
        elif health_score < 85:
            prediction['risk_level'] = 'medium'
            prediction['recommended_action'] = '加强监测'
        
        return prediction


class EnergyManagementPlatform:
    """能源管理平台主类"""
    
    def __init__(self):
        self.db = EnergyDatabase()
        self.collector = DataCollector(self.db)
        self.analyzer = EnergyAnalyzer(self.db)
        self.hvac_optimizer = HVACOptimizer(self.db)
        self.carbon_manager = CarbonManager(self.db)
        self.maintenance = PredictiveMaintenance(self.db)
        
        # 设备列表
        self.devices: Dict[str, EnergyDevice] = {}
        
        # 注册采集器回调
        self.collector.add_callback(self._on_meter_reading)
    
    def register_device(self, device: EnergyDevice, collector: BaseCollector):
        """注册设备"""
        self.devices[device.device_id] = device
        self.collector.register_collector(device.meter_id, collector)
        
        # 保存到数据库
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO energy_devices 
            (device_id, name, category, rated_power, location, meter_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device.device_id, device.name, device.category.value,
              device.rated_power, device.location, device.meter_id))
        conn.commit()
        conn.close()
    
    def _on_meter_reading(self, reading: MeterReading):
        """仪表读数回调"""
        # 触发异常检测
        if reading.power and reading.power > 1000:  # 功率突增
            anomalies = self.analyzer.detect_anomaly(reading.meter_id)
            if anomalies:
                logger.warning(f"检测到能耗异常: {reading.meter_id}")
    
    def get_realtime_dashboard(self) -> Dict:
        """获取实时监控仪表板数据"""
        total_power = 0
        device_status = []
        
        for device in self.devices.values():
            # 获取最新读数
            readings = self.db.get_readings(device.meter_id, time.time() - 3600, time.time())
            if readings:
                latest = readings[-1]
                if latest.power:
                    total_power += latest.power
                    device_status.append({
                        'device_id': device.device_id,
                        'name': device.name,
                        'power_kw': latest.power,
                        'status': device.status
                    })
        
        # 今日能耗
        today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        today_consumption = 0
        for device in self.devices.values():
            readings = self.db.get_readings(device.meter_id, today_start, time.time())
            today_consumption += sum(r.delta for r in readings)
        
        return {
            'total_power_kw': round(total_power, 2),
            'today_consumption_kwh': round(today_consumption, 2),
            'device_count': len(self.devices),
            'online_devices': len([d for d in self.devices.values() if d.status == 'normal']),
            'device_status': device_status
        }
    
    def run_daily_analysis(self):
        """执行每日分析"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 1. 计算日统计
        for device in self.devices.values():
            start_time = datetime.strptime(yesterday, '%Y-%m-%d').timestamp()
            end_time = start_time + 24 * 3600
            readings = self.db.get_readings(device.meter_id, start_time, end_time)
            
            if readings:
                powers = [r.power for r in readings if r.power is not None]
                if powers:
                    self.db.save_daily_stats(
                        yesterday, device.meter_id, EnergyType.ELECTRICITY,
                        sum(r.delta for r in readings),
                        max(powers), np.mean(powers), min(powers),
                        sum(r.delta for r in readings) * 0.8  # 假设电价0.8元/kWh
                    )
        
        # 2. 计算碳排放
        self.carbon_manager.calculate_daily_emission(yesterday)
        
        # 3. 预测性维护检查
        for device in self.devices.values():
            prediction = self.maintenance.predict_failure(device)
            if prediction['risk_level'] in ['high', 'critical']:
                logger.warning(f"设备维护预警: {device.name} - {prediction['recommended_action']}")
        
        logger.info(f"每日分析完成: {yesterday}")


# 使用示例
if __name__ == "__main__":
    # 初始化平台
    platform = EnergyManagementPlatform()
    
    # 注册空调设备
    chiller = EnergyDevice(
        device_id="chiller_01",
        name="1号冷水机组",
        category=DeviceCategory.HVAC,
        rated_power=500,
        location="地下机房",
        meter_id="meter_chiller_01"
    )
    collector = ModbusCollector("192.168.1.100", 502, 40001, EnergyType.ELECTRICITY)
    platform.register_device(chiller, collector)
    
    # 注册照明设备
    lighting = EnergyDevice(
        device_id="light_floor1",
        name="1层照明总表",
        category=DeviceCategory.LIGHTING,
        rated_power=100,
        location="1层配电间",
        meter_id="meter_light_01"
    )
    light_collector = MqttCollector("building/meter/light01", EnergyType.ELECTRICITY)
    platform.register_device(lighting, light_collector)
    
    # 启动数据采集
    platform.collector.start()
    
    logger.info("绿能科技智慧能耗管理平台启动完成")
    
    try:
        while True:
            time.sleep(60)
            # 每小时输出仪表板
            dashboard = platform.get_realtime_dashboard()
            logger.info(f"实时数据: 总功率={dashboard['total_power_kw']}kW, "
                       f"今日用电={dashboard['today_consumption_kwh']}kWh")
    except KeyboardInterrupt:
        logger.info("平台已关闭")
```

### 效果评估

#### 关键指标达成情况

| 指标项 | 实施前 | 目标值 | 实施后 | 达成率 |
|--------|--------|--------|--------|--------|
| 分项计量覆盖率 | 15% | 95% | 98% | 100% |
| 数据实时性 | 月度 | 5分钟 | 1分钟 | 100% |
| 空调系统节能率 | 0% | 15% | 22% | 100% |
| 照明系统节能率 | 0% | 20% | 28% | 100% |
| 故障预警准确率 | 0% | 85% | 89% | 100% |
| 碳排放核算周期 | 3个月 | 实时 | 日度 | 100% |

#### 投资回报率（ROI）分析

**项目总投资**：1,250万元

| 投资项 | 金额（万元） |
|--------|-------------|
| 智能计量设备（电表、水表、气表） | 380 |
| 传感器与网关（温度、湿度、CO2等） | 220 |
| 软件平台开发与部署 | 420 |
| AI算法模型定制与训练 | 150 |
| 系统集成与调试 | 80 |

**年度收益**：

| 收益项 | 年度金额（万元） |
|--------|-----------------|
| 电费节省（整体节能18%） | 580 |
| 维护成本降低（预测性维护） | 120 |
| 碳交易收益（CCER） | 85 |
| 政府节能补贴 | 45 |
| 设备延寿价值 | 60 |
| **年度总收益** | **890** |

**ROI计算**：
- **投资回收期**：17个月
- **首年净收益**：-360万元（建设期）
- **三年期ROI**：113%（三年累计收益2,670万元，投资回报率113%）
- **五年期ROI**：256%（五年累计收益4,450万元）

#### 碳减排成效

| 指标 | 数值 |
|------|------|
| 年度节电量 | 725万kWh |
| 年度节约标煤 | 2,900吨 |
| 年度CO2减排 | 4,140吨 |
| 相当于植树 | 22.8万棵 |

#### 业务价值总结

1. **经济效益显著**：年度能源成本降低18%，三年收回全部投资
2. **运营效率提升**：设备故障响应时间从平均4小时缩短至30分钟
3. **合规能力提升**：满足碳排放监管要求，通过ISO50001能源管理体系认证
4. **品牌形象提升**：入选工信部"绿色制造示范企业"，获得省级节能先进单位称号
5. **数据资产价值**：积累的能耗数据支撑了建筑能源性能保险等创新业务

---

## 案例二：智能制造园区综合能源服务

### 企业背景

某新能源汽车制造园区，占地2000亩，年用电量超过5亿kWh，拥有冲压、焊装、涂装、总装四大工艺车间，以及电池、电机等核心零部件生产线。园区对能源成本高度敏感，同时面临碳达峰碳中和目标压力。

### 业务痛点

1. **高能耗成本高企**：年电费超过3亿元，占制造成本8%以上
2. **峰谷电价差利用不足**：高峰时段大量设备运行，电费支出高企
3. **光伏储能利用率低**：屋顶光伏所发电力无法有效消纳
4. **多能协同不足**：电、气、热、冷系统独立运行，综合效率低
5. **碳配额管理粗放**：缺乏精准的碳排放核算与配额预警机制

### 业务目标

1. 建设园区级能源管理平台，实现全能源品种实时监测
2. 通过AI优化控制，降低整体能耗成本15%以上
3. 构建光储充一体化系统，提升可再生能源消纳率至90%
4. 实现多能互补优化，综合能源效率提升20%
5. 建立碳资产管理体系，支撑碳交易决策

### 技术架构亮点

- **数字孪生能源系统**：1:1还原园区能源流，实时仿真优化
- **AI负荷预测模型**：预测精度达95%，支撑需量申报与调度
- **虚拟电厂聚合**：参与电力需求响应，获取辅助服务收益
- **区块链碳溯源**：实现产品碳足迹全程可追溯

### 实施效果

- 年度综合能耗成本降低16.5%，节约电费约5,000万元
- 光伏发电自消纳率从65%提升至92%
- 参与电力需求响应32次，获得补贴收入420万元
- 年度碳减排8.2万吨，碳配额盈余创造价值680万元
- 通过能源管理体系ISO50001认证，获国家级绿色工厂称号

---

*案例研究文档版本：v1.0 | 最后更新：2026年2月*
