# 家庭自动化案例研究

## 案例一：智慧雅居全屋智能系统

### 企业背景

**智慧雅居科技有限公司**（以下简称"智慧雅居"）成立于2018年，总部位于深圳，是国内领先的智能家居解决方案提供商。公司专注于为高端住宅、别墅及精装公寓提供全屋智能系统集成服务，业务覆盖华东、华南、华北等核心城市群。

**企业基本信息：**
- **成立时间**：2018年
- **总部位置**：深圳南山区科技园
- **员工规模**：280人（技术研发120人，工程实施100人，运营服务60人）
- **年营收**：3.2亿元人民币
- **服务客户**：累计服务高端住宅项目150+，覆盖家庭用户2.8万户
- **核心产品**：智能照明控制系统、智能窗帘系统、环境感知调节系统、智能场景联动平台

**市场定位**：面向年收入50万以上的中产及以上家庭，提供一站式全屋智能解决方案，单户平均客单价15-35万元。

### 业务痛点

1. **设备协议碎片化严重**
   - 合作品牌涵盖小米、华为、涂鸦、欧瑞博等20余家厂商
   - 通信协议混杂：Zigbee 3.0、Z-Wave、Wi-Fi、蓝牙Mesh、Thread并存
   - 设备接入调试耗时过长，单户部署周期平均需要5-7天
   - 跨品牌设备无法直接联动，需通过第三方中间件转接

2. **场景配置复杂度高**
   - 现有系统需要专业人员上门配置，用户无法自主调整
   - 场景规则编写依赖特定领域语言，学习曲线陡峭
   - 场景联动响应延迟高，平均响应时间800ms以上
   - 用户场景需求频繁变更，维护成本居高不下

3. **系统稳定性不足**
   - 网络波动导致设备离线率高达12%
   - 场景执行失败率约5%，影响用户体验
   - 边缘网关故障时，本地自动化完全失效
   - 固件升级过程中出现设备变砖案例，客诉率上升

4. **能耗数据不透明**
   - 缺乏细粒度的设备级能耗监测
   - 无法根据用户行为习惯自动优化能耗策略
   - 月度能耗账单无法下钻到具体设备和场景
   - 用户节能意识薄弱，系统缺乏有效的节能引导机制

5. **售后服务效率低**
   - 故障定位依赖用户描述，远程诊断能力弱
   - 平均故障响应时间24小时，上门维修周期3-5天
   - 设备更换缺乏预测性维护，多为事后补救
   - 客户满意度评分仅72分（行业平均85分）

### 业务目标

1. **统一设备接入层**
   - 实现95%以上主流品牌设备即插即用
   - 将单户部署周期从5-7天缩短至1-2天
   - 建立统一的设备抽象模型，屏蔽底层协议差异
   - 支持设备自动发现与自动配网，减少人工干预

2. **构建可视化场景引擎**
   - 开发拖拽式场景编排工具，零代码配置场景
   - 场景响应延迟控制在200ms以内
   - 支持用户通过手机APP自主创建和修改场景
   - 实现AI驱动的场景推荐与自动优化

3. **提升系统可靠性**
   - 将设备离线率从12%降至3%以下
   - 场景执行成功率达到99.5%以上
   - 实现边缘节点的故障自动切换与自愈
   - 建立OTA升级的安全回滚机制

4. **实现智慧能耗管理**
   - 实现设备级实时能耗监测与分钟级数据上报
   - 基于用户行为模式自动生成节能策略
   - 为用户节省年度电费支出15%-25%
   - 提供可视化的能耗报告与节能建议

5. **优化售后服务体系**
   - 建立远程故障诊断平台，80%问题远程解决
   - 故障响应时间缩短至2小时以内
   - 实现预测性维护，提前7天预警潜在故障
   - 客户满意度提升至90分以上

### 技术挑战

1. **异构设备互联互通**
   - 需要设计统一的设备抽象层，支持多种通信协议适配
   - 设备发现机制需兼容mDNS、SSDP、CoAP等多种发现协议
   - 状态同步需处理不同设备的报告周期差异（1秒至5分钟）
   - 需解决Zigbee与Thread网络的边界路由问题

2. **低延迟场景联动**
   - 场景规则引擎需在边缘侧运行，降低云端依赖
   - 复杂场景涉及10+设备联动，需保证原子性执行
   - 需支持条件触发、定时触发、事件触发等多种模式
   - 场景冲突检测与优先级仲裁机制设计

3. **离线自治能力**
   - 边缘网关需具备完整的场景执行能力
   - 本地设备数据库需与云端保持最终一致性
   - 网络恢复后的状态同步与冲突解决
   - 关键场景（安防、照明）必须支持离线执行

4. **大规模数据实时处理**
   - 单户日均产生传感器数据50万条
   - 需支持实时流处理与批量分析的双轨架构
   - 时序数据存储需优化压缩比与查询性能
   - 实时异常检测与告警机制

5. **安全与隐私保护**
   - 设备通信需端到端加密，防止中间人攻击
   - 本地数据处理需保护用户隐私
   - 访问控制需支持多级别权限管理
   - 安全审计日志需完整记录所有操作

### 代码实现

```python
"""
智慧雅居全屋智能系统 - 核心模块实现
包含：设备管理、MQTT通信、场景引擎、规则处理、数据持久化
"""

import asyncio
import json
import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set
from threading import Lock, Thread
import queue
import paho.mqtt.client as mqtt

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """设备类型枚举"""
    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    CURTAIN = "curtain"
    AC = "ac"
    CAMERA = "camera"
    LOCK = "lock"
    SPEAKER = "speaker"


class ProtocolType(Enum):
    """通信协议类型"""
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    WIFI = "wifi"
    BLE = "ble"
    THREAD = "thread"
    MATTER = "matter"


@dataclass
class DeviceState:
    """设备状态数据类"""
    power: bool = False
    brightness: Optional[int] = None
    color_temp: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    position: Optional[int] = None
    mode: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Device:
    """设备数据类"""
    device_id: str
    name: str
    device_type: DeviceType
    protocol: ProtocolType
    manufacturer: str
    model: str
    room: str
    state: DeviceState
    online: bool = False
    last_seen: float = 0.0
    
    def __post_init__(self):
        if isinstance(self.device_type, str):
            self.device_type = DeviceType(self.device_type)
        if isinstance(self.protocol, str):
            self.protocol = ProtocolType(self.protocol)


class DatabaseManager:
    """SQLite数据库管理器 - 负责数据持久化"""
    
    def __init__(self, db_path: str = "smart_home.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地连接"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 设备表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                protocol TEXT NOT NULL,
                manufacturer TEXT,
                model TEXT,
                room TEXT,
                state_json TEXT,
                online INTEGER DEFAULT 0,
                last_seen REAL,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # 场景表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scenes (
                scene_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                triggers_json TEXT,
                actions_json TEXT,
                enabled INTEGER DEFAULT 1,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # 设备状态历史表（时序数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                state_json TEXT,
                timestamp REAL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        ''')
        
        # 能耗数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                power_watts REAL,
                energy_wh REAL,
                timestamp REAL DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        ''')
        
        # 创建索引优化查询
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_device_time ON device_history(device_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_device_time ON energy_data(device_id, timestamp)')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def save_device(self, device: Device):
        """保存或更新设备信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO devices 
            (device_id, name, device_type, protocol, manufacturer, model, room, state_json, online, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device.device_id, device.name, device.device_type.value,
            device.protocol.value, device.manufacturer, device.model, device.room,
            json.dumps(device.state.to_dict()), int(device.online), device.last_seen
        ))
        conn.commit()
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """获取设备信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_device(row)
        return None
    
    def get_all_devices(self) -> List[Device]:
        """获取所有设备"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices')
        return [self._row_to_device(row) for row in cursor.fetchall()]
    
    def _row_to_device(self, row: sqlite3.Row) -> Device:
        """将数据库行转换为Device对象"""
        state_dict = json.loads(row['state_json']) if row['state_json'] else {}
        return Device(
            device_id=row['device_id'],
            name=row['name'],
            device_type=DeviceType(row['device_type']),
            protocol=ProtocolType(row['protocol']),
            manufacturer=row['manufacturer'],
            model=row['model'],
            room=row['room'],
            state=DeviceState(**state_dict),
            online=bool(row['online']),
            last_seen=row['last_seen']
        )
    
    def save_device_history(self, device_id: str, state: DeviceState):
        """保存设备状态历史"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO device_history (device_id, state_json, timestamp)
            VALUES (?, ?, ?)
        ''', (device_id, json.dumps(state.to_dict()), time.time()))
        conn.commit()
    
    def save_energy_data(self, device_id: str, power_watts: float, energy_wh: float):
        """保存能耗数据"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO energy_data (device_id, power_watts, energy_wh, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (device_id, power_watts, energy_wh, time.time()))
        conn.commit()
    
    def get_energy_stats(self, device_id: str, start_time: float, end_time: float) -> Dict[str, float]:
        """获取能耗统计"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(energy_wh) as total_energy, AVG(power_watts) as avg_power,
                   MAX(power_watts) as max_power, MIN(power_watts) as min_power
            FROM energy_data
            WHERE device_id = ? AND timestamp BETWEEN ? AND ?
        ''', (device_id, start_time, end_time))
        row = cursor.fetchone()
        return {
            'total_energy_wh': row['total_energy'] or 0,
            'avg_power_w': row['avg_power'] or 0,
            'max_power_w': row['max_power'] or 0,
            'min_power_w': row['min_power'] or 0
        }


import threading


class MQTTClient:
    """MQTT客户端 - 负责设备通信"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id=f"smart_home_hub_{int(time.time())}")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.message_handlers: Dict[str, List[Callable]] = {}
        self._connected = False
        self._lock = Lock()
        
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self._connected = True
            logger.info(f"MQTT连接成功: {self.broker_host}:{self.broker_port}")
            # 订阅设备相关主题
            self.client.subscribe("home/+/status")
            self.client.subscribe("home/+/telemetry")
            self.client.subscribe("home/discovery/+")
        else:
            logger.error(f"MQTT连接失败，返回码: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self._connected = False
        logger.warning(f"MQTT断开连接，返回码: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """消息回调"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.debug(f"收到消息 - Topic: {topic}, Payload: {payload}")
            
            with self._lock:
                handlers = self.message_handlers.get(topic, [])
                # 支持通配符匹配
                for pattern, pattern_handlers in self.message_handlers.items():
                    if '+' in pattern or '#' in pattern:
                        if mqtt.topic_matches_sub(pattern, topic):
                            handlers.extend(pattern_handlers)
            
            for handler in handlers:
                try:
                    handler(topic, payload)
                except Exception as e:
                    logger.error(f"消息处理异常: {e}")
        except Exception as e:
            logger.error(f"消息解析异常: {e}")
    
    def connect(self):
        """连接MQTT Broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"MQTT连接异常: {e}")
    
    def disconnect(self):
        """断开连接"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def subscribe(self, topic: str, handler: Callable):
        """订阅主题"""
        with self._lock:
            if topic not in self.message_handlers:
                self.message_handlers[topic] = []
                self.client.subscribe(topic)
            self.message_handlers[topic].append(handler)
    
    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        """发布消息"""
        if self._connected:
            self.client.publish(topic, json.dumps(payload), qos=qos)
        else:
            logger.warning("MQTT未连接，无法发布消息")


class DeviceManager:
    """设备管理器 - 负责设备生命周期管理"""
    
    def __init__(self, db: DatabaseManager, mqtt: MQTTClient):
        self.db = db
        self.mqtt = mqtt
        self.devices: Dict[str, Device] = {}
        self._lock = Lock()
        self._state_callbacks: List[Callable[[Device], None]] = []
        self._discovery_enabled = True
        
        # 注册MQTT消息处理器
        self.mqtt.subscribe("home/+/status", self._handle_device_status)
        self.mqtt.subscribe("home/+/telemetry", self._handle_device_telemetry)
        self.mqtt.subscribe("home/discovery/+", self._handle_device_discovery)
        
        # 加载持久化的设备
        self._load_devices()
        
        # 启动设备健康检查线程
        self._health_check_thread = Thread(target=self._device_health_check, daemon=True)
        self._health_check_thread.start()
    
    def _load_devices(self):
        """从数据库加载设备"""
        devices = self.db.get_all_devices()
        with self._lock:
            for device in devices:
                self.devices[device.device_id] = device
        logger.info(f"从数据库加载了 {len(devices)} 个设备")
    
    def _handle_device_status(self, topic: str, payload: Dict):
        """处理设备状态消息"""
        device_id = topic.split('/')[1]
        online = payload.get('online', False)
        
        with self._lock:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.online = online
                device.last_seen = time.time()
                self.db.save_device(device)
                self._notify_state_change(device)
    
    def _handle_device_telemetry(self, topic: str, payload: Dict):
        """处理设备遥测数据"""
        device_id = topic.split('/')[1]
        
        with self._lock:
            if device_id in self.devices:
                device = self.devices[device_id]
                # 更新设备状态
                state_dict = payload.get('state', {})
                for key, value in state_dict.items():
                    if hasattr(device.state, key):
                        setattr(device.state, key, value)
                device.last_seen = time.time()
                
                # 持久化
                self.db.save_device(device)
                self.db.save_device_history(device_id, device.state)
                
                # 处理能耗数据
                if 'power' in payload:
                    power = payload['power']
                    energy = payload.get('energy', 0)
                    self.db.save_energy_data(device_id, power, energy)
                
                self._notify_state_change(device)
    
    def _handle_device_discovery(self, topic: str, payload: Dict):
        """处理设备发现消息"""
        if not self._discovery_enabled:
            return
        
        device_info = payload.get('device', {})
        device_id = device_info.get('id')
        
        if device_id and device_id not in self.devices:
            device = Device(
                device_id=device_id,
                name=device_info.get('name', f"设备_{device_id}"),
                device_type=DeviceType(device_info.get('type', 'sensor')),
                protocol=ProtocolType(device_info.get('protocol', 'wifi')),
                manufacturer=device_info.get('manufacturer', 'Unknown'),
                model=device_info.get('model', 'Unknown'),
                room=device_info.get('room', 'default'),
                state=DeviceState(),
                online=True,
                last_seen=time.time()
            )
            
            with self._lock:
                self.devices[device_id] = device
            
            self.db.save_device(device)
            logger.info(f"发现新设备: {device.name} ({device_id})")
            
            # 发送确认响应
            self.mqtt.publish(f"home/discovery/{device_id}/ack", {"status": "registered"})
    
    def _device_health_check(self):
        """设备健康检查线程"""
        while True:
            time.sleep(60)  # 每分钟检查一次
            current_time = time.time()
            offline_threshold = 300  # 5分钟无响应视为离线
            
            with self._lock:
                for device in self.devices.values():
                    if device.online and (current_time - device.last_seen) > offline_threshold:
                        device.online = False
                        self.db.save_device(device)
                        logger.warning(f"设备离线: {device.name} ({device.device_id})")
    
    def _notify_state_change(self, device: Device):
        """通知设备状态变更"""
        for callback in self._state_callbacks:
            try:
                callback(device)
            except Exception as e:
                logger.error(f"状态回调异常: {e}")
    
    def add_state_callback(self, callback: Callable[[Device], None]):
        """添加状态变更回调"""
        self._state_callbacks.append(callback)
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """获取设备"""
        with self._lock:
            return self.devices.get(device_id)
    
    def get_devices_by_room(self, room: str) -> List[Device]:
        """按房间获取设备"""
        with self._lock:
            return [d for d in self.devices.values() if d.room == room]
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[Device]:
        """按类型获取设备"""
        with self._lock:
            return [d for d in self.devices.values() if d.device_type == device_type]
    
    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = None):
        """发送设备控制命令"""
        device = self.get_device(device_id)
        if not device:
            logger.error(f"设备不存在: {device_id}")
            return False
        
        if not device.online:
            logger.warning(f"设备离线，命令可能无法执行: {device_id}")
        
        topic = f"home/{device_id}/command"
        payload = {"command": command, "params": params or {}}
        self.mqtt.publish(topic, payload)
        logger.info(f"发送命令到 {device.name}: {command}")
        return True


@dataclass
class SceneAction:
    """场景动作"""
    device_id: str
    command: str
    params: Dict[str, Any]
    delay_ms: int = 0  # 延迟执行（毫秒）


@dataclass
class SceneTrigger:
    """场景触发器"""
    trigger_type: str  # 'time', 'event', 'condition', 'manual'
    config: Dict[str, Any]  # 触发器配置


class Scene:
    """场景类"""
    
    def __init__(self, scene_id: str, name: str, description: str = ""):
        self.scene_id = scene_id
        self.name = name
        self.description = description
        self.triggers: List[SceneTrigger] = []
        self.actions: List[SceneAction] = []
        self.enabled = True
        self.last_executed = 0.0
        self.execution_count = 0
    
    def add_trigger(self, trigger: SceneTrigger):
        """添加触发器"""
        self.triggers.append(trigger)
    
    def add_action(self, action: SceneAction):
        """添加动作"""
        self.actions.append(action)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'scene_id': self.scene_id,
            'name': self.name,
            'description': self.description,
            'triggers': [{'type': t.trigger_type, 'config': t.config} for t in self.triggers],
            'actions': [
                {
                    'device_id': a.device_id,
                    'command': a.command,
                    'params': a.params,
                    'delay_ms': a.delay_ms
                } for a in self.actions
            ],
            'enabled': self.enabled
        }


class SceneEngine:
    """场景引擎 - 负责场景管理与执行"""
    
    def __init__(self, device_manager: DeviceManager, db: DatabaseManager):
        self.device_manager = device_manager
        self.db = db
        self.scenes: Dict[str, Scene] = {}
        self._lock = Lock()
        self._running = True
        self._executor_queue: queue.Queue = queue.Queue()
        
        # 启动场景执行线程
        self._executor_thread = Thread(target=self._action_executor, daemon=True)
        self._executor_thread.start()
        
        # 启动定时检查线程
        self._scheduler_thread = Thread(target=self._time_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        # 注册设备状态回调
        self.device_manager.add_state_callback(self._on_device_state_change)
        
        # 加载持久化场景
        self._load_scenes()
    
    def _load_scenes(self):
        """从数据库加载场景"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scenes WHERE enabled = 1')
        
        for row in cursor.fetchall():
            scene = Scene(row['scene_id'], row['name'], row['description'])
            scene.enabled = bool(row['enabled'])
            
            triggers = json.loads(row['triggers_json'])
            for t in triggers:
                scene.add_trigger(SceneTrigger(t['type'], t['config']))
            
            actions = json.loads(row['actions_json'])
            for a in actions:
                scene.add_action(SceneAction(
                    a['device_id'], a['command'], a['params'], a.get('delay_ms', 0)
                ))
            
            self.scenes[scene.scene_id] = scene
        
        conn.close()
        logger.info(f"加载了 {len(self.scenes)} 个场景")
    
    def save_scene(self, scene: Scene):
        """保存场景到数据库"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO scenes (scene_id, name, description, triggers_json, actions_json, enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            scene.scene_id, scene.name, scene.description,
            json.dumps([{'type': t.trigger_type, 'config': t.config} for t in scene.triggers]),
            json.dumps([
                {
                    'device_id': a.device_id,
                    'command': a.command,
                    'params': a.params,
                    'delay_ms': a.delay_ms
                } for a in scene.actions
            ]),
            int(scene.enabled)
        ))
        conn.commit()
        conn.close()
        
        with self._lock:
            self.scenes[scene.scene_id] = scene
    
    def _action_executor(self):
        """动作执行线程"""
        while self._running:
            try:
                action_data = self._executor_queue.get(timeout=1)
                scene_id = action_data['scene_id']
                action = action_data['action']
                
                # 处理延迟
                if action.delay_ms > 0:
                    time.sleep(action.delay_ms / 1000)
                
                # 执行动作
                success = self.device_manager.send_command(
                    action.device_id, action.command, action.params
                )
                
                if not success:
                    logger.error(f"场景 {scene_id} 动作执行失败: {action.device_id} - {action.command}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"动作执行异常: {e}")
    
    def _time_scheduler(self):
        """定时调度线程"""
        while self._running:
            current_time = datetime.now()
            current_minute = current_time.strftime('%H:%M')
            
            with self._lock:
                for scene in self.scenes.values():
                    if not scene.enabled:
                        continue
                    
                    for trigger in scene.triggers:
                        if trigger.trigger_type == 'time':
                            schedule = trigger.config.get('schedule', '')
                            if schedule == current_minute:
                                self.execute_scene(scene.scene_id)
            
            time.sleep(60)  # 每分钟检查一次
    
    def _on_device_state_change(self, device: Device):
        """设备状态变更回调 - 检查事件触发"""
        with self._lock:
            for scene in self.scenes.values():
                if not scene.enabled:
                    continue
                
                for trigger in scene.triggers:
                    if trigger.trigger_type == 'event':
                        config = trigger.config
                        if (config.get('device_id') == device.device_id and
                            config.get('event_type') == 'state_change'):
                            # 检查条件
                            condition = config.get('condition', {})
                            state_key = condition.get('key')
                            state_value = condition.get('value')
                            
                            if state_key and hasattr(device.state, state_key):
                                actual_value = getattr(device.state, state_key)
                                if actual_value == state_value:
                                    self.execute_scene(scene.scene_id)
    
    def execute_scene(self, scene_id: str) -> bool:
        """执行场景"""
        with self._lock:
            scene = self.scenes.get(scene_id)
            if not scene:
                logger.error(f"场景不存在: {scene_id}")
                return False
            
            if not scene.enabled:
                logger.warning(f"场景已禁用: {scene_id}")
                return False
        
        logger.info(f"执行场景: {scene.name}")
        scene.last_executed = time.time()
        scene.execution_count += 1
        
        # 将动作加入执行队列
        for action in scene.actions:
            self._executor_queue.put({
                'scene_id': scene_id,
                'action': action
            })
        
        return True
    
    def create_scene(self, name: str, description: str = "") -> Scene:
        """创建新场景"""
        scene_id = f"scene_{int(time.time() * 1000)}"
        scene = Scene(scene_id, name, description)
        return scene
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """获取场景"""
        with self._lock:
            return self.scenes.get(scene_id)
    
    def list_scenes(self) -> List[Scene]:
        """列出所有场景"""
        with self._lock:
            return list(self.scenes.values())


# 使用示例
if __name__ == "__main__":
    # 初始化组件
    db = DatabaseManager()
    mqtt = MQTTClient()
    mqtt.connect()
    
    # 创建设备管理器
    device_manager = DeviceManager(db, mqtt)
    
    # 创建场景引擎
    scene_engine = SceneEngine(device_manager, db)
    
    # 模拟创建设备
    light1 = Device(
        device_id="light_001",
        name="客厅主灯",
        device_type=DeviceType.LIGHT,
        protocol=ProtocolType.ZIGBEE,
        manufacturer="Philips",
        model="Hue White",
        room="客厅",
        state=DeviceState(power=True, brightness=80)
    )
    device_manager.devices[light1.device_id] = light1
    db.save_device(light1)
    
    # 模拟创建"回家模式"场景
    home_scene = scene_engine.create_scene("回家模式", "打开客厅灯光，调节温度")
    home_scene.add_trigger(SceneTrigger('manual', {}))
    home_scene.add_action(SceneAction('light_001', 'turn_on', {'brightness': 100}))
    scene_engine.save_scene(home_scene)
    
    logger.info("智慧雅居全屋智能系统启动完成")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mqtt.disconnect()
        logger.info("系统已关闭")
```

### 效果评估

#### 关键指标达成情况

| 指标项 | 实施前 | 目标值 | 实施后 | 达成率 |
|--------|--------|--------|--------|--------|
| 设备接入周期 | 5-7天 | 1-2天 | 1.5天 | 100% |
| 场景响应延迟 | 800ms | 200ms | 150ms | 100% |
| 设备离线率 | 12% | 3% | 2.1% | 100% |
| 场景执行成功率 | 95% | 99.5% | 99.7% | 100% |
| 客户满意度 | 72分 | 90分 | 92分 | 100% |
| 故障响应时间 | 24小时 | 2小时 | 1.5小时 | 100% |

#### 投资回报率（ROI）分析

**项目总投资**：680万元

| 投资项 | 金额（万元） |
|--------|-------------|
| 边缘网关硬件（2000台） | 240 |
| 软件开发与定制 | 280 |
| 云平台部署与运维 | 100 |
| 人员培训与知识转移 | 40 |
| 项目管理与咨询 | 20 |

**年度收益**：

| 收益项 | 年度金额（万元） |
|--------|-----------------|
| 部署效率提升节省人力成本 | 180 |
| 售后服务成本降低 | 120 |
| 能耗优化带来的增值服务费 | 85 |
| 客户续约率提升带来的收入 | 150 |
| 新增客户转化率提升 | 200 |
| **年度总收益** | **735** |

**ROI计算**：
- **投资回收期**：11个月
- **首年净收益**：55万元
- **三年期ROI**：224%（三年累计收益2,205万元，投资回报率224%）

#### 业务价值总结

1. **运营效率提升**：部署周期缩短70%，单项目交付成本降低45%
2. **用户体验改善**：客户满意度提升28%，NPS评分从32提升至67
3. **商业模式创新**：能耗管理服务成为新的收入增长点，占总收入12%
4. **市场竞争力增强**：中标率从35%提升至58%，成功进入北京、上海高端市场
5. **技术壁垒构建**：获得发明专利3项，形成核心技术护城河

---

## 案例二：未来社区智慧物业平台

### 企业背景

**未来社区物业服务集团**是华东地区领先的综合性物业管理服务商，管理着超过120个中高端住宅小区，服务业主超过30万户。集团致力于打造"科技+服务"的新型物业模式，通过智能化手段提升物业服务品质和运营效率。

### 业务痛点

1. **设备管理分散**：社区内照明、门禁、电梯、给排水等设备系统独立运行，缺乏统一管理平台
2. **报修响应滞后**：业主报修需通过电话或APP，工单分派依赖人工，平均响应时间超过4小时
3. **能耗成本居高不下**：公共区域照明、空调系统能耗占运营成本35%以上
4. **安防盲区多**：传统视频监控存在盲区，异常事件发现依赖人工巡查
5. **数据孤岛严重**：各业务系统数据不互通，无法支撑精细化运营决策

### 业务目标

1. 建设统一的IoT设备管理平台，实现98%以上设备在线监控
2. 建立智能工单系统，将报修响应时间缩短至30分钟以内
3. 通过AI节能策略，降低公共区域能耗20%以上
4. 实现智能安防预警，异常事件主动发现率达到90%
5. 构建数据驾驶舱，支撑管理决策效率提升50%

### 技术架构亮点

- **边缘计算节点**：每社区部署边缘网关，实现本地自治
- **数字孪生建模**：建立社区设备3D可视化模型
- **AI预测维护**：基于设备运行数据预测故障
- **移动工单引擎**：支持报修、派单、处理、验收全流程移动化

### 实施效果

- 设备在线率从67%提升至98.5%
- 平均报修响应时间从4.2小时降至18分钟
- 年度能耗成本降低23%，节省电费约380万元
- 安防事件主动发现率从35%提升至92%
- 管理决策效率提升60%，报表生成时间从3天缩短至实时

---

*案例研究文档版本：v1.0 | 最后更新：2026年2月*
