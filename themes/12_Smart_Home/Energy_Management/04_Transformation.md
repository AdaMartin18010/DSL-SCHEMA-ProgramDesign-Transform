# Energy Management转换体系

## 📑 目录

- [Energy Management转换体系](#energy-management转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 能源数据转换](#2-能源数据转换)
    - [2.1 DLMS/COSEM到JSON转换](#21-dlmscosem到json转换)
    - [2.2 IEEE 2030.5到内部模型转换](#22-ieee-20305到内部模型转换)
    - [2.3 Modbus到能源数据转换](#23-modbus到能源数据转换)
  - [3. 设备状态同步](#3-设备状态同步)
    - [3.1 智能电表状态同步](#31-智能电表状态同步)
    - [3.2 储能系统状态同步](#32-储能系统状态同步)
    - [3.3 可控负载状态同步](#33-可控负载状态同步)
  - [4. 协议转换网关](#4-协议转换网关)
    - [4.1 Zigbee SE到IP转换](#41-zigbee-se到ip转换)
    - [4.2 Thread到BACnet转换](#42-thread到bacnet转换)
    - [4.3 DALI到Zigbee转换](#43-dali到zigbee转换)
  - [5. 能源优化转换](#5-能源优化转换)
    - [5.1 负荷预测模型转换](#51-负荷预测模型转换)
    - [5.2 优化调度策略转换](#52-优化调度策略转换)
    - [5.3 碳排放数据转换](#53-碳排放数据转换)
  - [6. 转换工具](#6-转换工具)
    - [6.1 协议分析器](#61-协议分析器)
    - [6.2 数据映射工具](#62-数据映射工具)
    - [6.3 性能分析器](#63-性能分析器)
  - [7. 转换验证](#7-转换验证)
    - [7.1 数据完整性验证](#71-数据完整性验证)
    - [7.2 协议一致性验证](#72-协议一致性验证)
    - [7.3 性能基准测试](#73-性能基准测试)
  - [8. Energy Management数据存储与分析](#8-energy-management数据存储与分析)
    - [8.1 PostgreSQL能源数据存储](#81-postgresql能源数据存储)
    - [8.2 时序数据库应用](#82-时序数据库应用)
    - [8.3 能源数据分析查询](#83-能源数据分析查询)

---

## 1. 转换体系概述

Energy Management Schema转换体系支持能源数据在不同协议、
不同标准之间的转换，以及设备状态的实时同步。

### 1.1 转换目标

1. **协议转换**：Zigbee SE、Thread、IEEE 2030.5、Modbus等协议互转
2. **数据格式转换**：DLMS/COSEM、JSON、XML等格式互转
3. **设备状态同步**：多协议设备状态统一同步
4. **优化模型转换**：负荷预测、调度策略模型转换
5. **数据到数据库存储**：能源数据到PostgreSQL/时序数据库存储

---

## 2. 能源数据转换

### 2.1 DLMS/COSEM到JSON转换

**转换规则**：

- COSEM对象 → JSON对象
- OBIS代码 → JSON字段名
- 寄存器值 → JSON数值
- 时间戳 → ISO 8601格式

**转换示例**：

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class COSEMObject:
    """COSEM对象表示"""
    logical_name: str  # OBIS代码
    class_id: int
    attributes: Dict[int, Any]

class DLMSCOSEMtoJSONConverter:
    """DLMS/COSEM到JSON转换器"""
    
    # OBIS代码到字段名映射
    OBIS_MAPPING = {
        "1-0:1.8.0*255": "total_active_energy_import",
        "1-0:2.8.0*255": "total_active_energy_export",
        "1-0:1.7.0*255": "instantaneous_active_power",
        "1-0:32.7.0*255": "voltage_l1",
        "1-0:52.7.0*255": "voltage_l2",
        "1-0:72.7.0*255": "voltage_l3",
        "1-0:31.7.0*255": "current_l1",
        "1-0:51.7.0*255": "current_l2",
        "1-0:71.7.0*255": "current_l3",
        "0-0:1.0.0*255": "device_time",
    }
    
    def convert(self, cosem_objects: list) -> Dict[str, Any]:
        """将COSEM对象列表转换为JSON"""
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "meter_id": None,
            "readings": {}
        }
        
        for obj in cosem_objects:
            field_name = self.OBIS_MAPPING.get(obj.logical_name, obj.logical_name)
            
            # 根据COSEM类ID解析属性
            if obj.class_id == 1:  # Data类
                result["readings"][field_name] = self._parse_data_object(obj)
            elif obj.class_id == 3:  # Register类
                result["readings"][field_name] = self._parse_register(obj)
            elif obj.class_id == 4:  # Extended Register类
                result["readings"][field_name] = self._parse_extended_register(obj)
            
            # 提取电表ID
            if obj.logical_name == "0-0:96.1.0*255":
                result["meter_id"] = obj.attributes.get(2)
        
        return result
    
    def _parse_data_object(self, obj: COSEMObject) -> Any:
        """解析Data对象"""
        return obj.attributes.get(2)  # value属性
    
    def _parse_register(self, obj: COSEMObject) -> Dict[str, Any]:
        """解析Register对象"""
        return {
            "value": obj.attributes.get(2),  # value
            "unit": self._parse_unit(obj.attributes.get(3)),  # scaler_unit
            "scaler": obj.attributes.get(3, {}).get("scaler", 0)
        }
    
    def _parse_extended_register(self, obj: COSEMObject) -> Dict[str, Any]:
        """解析Extended Register对象"""
        return {
            "value": obj.attributes.get(2),
            "unit": self._parse_unit(obj.attributes.get(3)),
            "timestamp": obj.attributes.get(5),  # capture_time
            "status": obj.attributes.get(6)  # status
        }
    
    def _parse_unit(self, scaler_unit: Optional[Dict]) -> str:
        """解析计量单位"""
        if not scaler_unit:
            return "unknown"
        
        unit_enum = {
            1: "year", 2: "month", 3: "week", 4: "day",
            5: "hour", 6: "minute", 7: "second",
            27: "W", 28: "VA", 29: "var",
            30: "Wh", 31: "VAh", 32: "varh",
            33: "A", 34: "C", 35: "V"
        }
        
        unit_code = scaler_unit.get("unit", 0)
        return unit_enum.get(unit_code, f"code_{unit_code}")

# 使用示例
def example_conversion():
    """DLMS/COSEM到JSON转换示例"""
    converter = DLMSCOSEMtoJSONConverter()
    
    # 模拟COSEM对象
    cosem_objects = [
        COSEMObject(
            logical_name="1-0:1.8.0*255",
            class_id=3,
            attributes={
                2: 1234567.8,
                3: {"scaler": -1, "unit": 30}  # Wh, scaler -1 = 0.1
            }
        ),
        COSEMObject(
            logical_name="1-0:1.7.0*255",
            class_id=3,
            attributes={
                2: 2.5,
                3: {"scaler": 0, "unit": 27}  # W
            }
        ),
        COSEMObject(
            logical_name="1-0:32.7.0*255",
            class_id=3,
            attributes={
                2: 230.5,
                3: {"scaler": -1, "unit": 35}  # V
            }
        ),
        COSEMObject(
            logical_name="0-0:96.1.0*255",
            class_id=1,
            attributes={2: "METER00123456"}
        )
    ]
    
    json_data = converter.convert(cosem_objects)
    print(json.dumps(json_data, indent=2))
    return json_data
```

### 2.2 IEEE 2030.5到内部模型转换

**转换规则**：

- SEP 2.0资源 → 内部能源数据模型
- XML/EXI → 内部对象
- 时间戳格式转换
- 单位换算

**转换示例**：

```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import xml.etree.ElementTree as ET

@dataclass
class InternalEnergyReading:
    """内部能源读数模型"""
    timestamp: datetime
    device_id: str
    power_kw: float
    energy_kwh: float
    voltage: Optional[float] = None
    current: Optional[float] = None
    power_factor: Optional[float] = None

class IEEE2030_5_Converter:
    """IEEE 2030.5到内部模型转换器"""
    
    NAMESPACES = {
        'sep': 'http://zigbee.org/sep'
    }
    
    def convert_meter_reading(self, sep_xml: str) -> List[InternalEnergyReading]:
        """将SEP 2.0 MeterReading转换为内部模型"""
        root = ET.fromstring(sep_xml)
        readings = []
        
        # 解析ReadingSet
        for reading_set in root.findall('.//sep:ReadingSet', self.NAMESPACES):
            time_period = reading_set.find('sep:timePeriod', self.NAMESPACES)
            if time_period is not None:
                start_time = time_period.find('sep:start', self.NAMESPACES)
                duration = time_period.find('sep:duration', self.NAMESPACES)
                
                timestamp = self._parse_timestamp(start_time.text) if start_time else datetime.utcnow()
            else:
                timestamp = datetime.utcnow()
            
            # 解析Reading
            for reading in reading_set.findall('.//sep:Reading', self.NAMESPACES):
                internal_reading = self._parse_reading(reading, timestamp)
                readings.append(internal_reading)
        
        return readings
    
    def _parse_reading(self, reading_elem: ET.Element, timestamp: datetime) -> InternalEnergyReading:
        """解析单个Reading元素"""
        device_id = self._get_text(reading_elem, 'sep:consumptionBlock/sep:mRID') or "unknown"
        
        # 解析功率值
        value_elem = reading_elem.find('sep:value', self.NAMESPACES)
        power = float(value_elem.text) if value_elem is not None else 0.0
        
        # 解析单位并转换
        reading_type = reading_elem.find('.//sep:ReadingType', self.NAMESPACES)
        unit = self._get_text(reading_type, 'sep:unit') if reading_type else "W"
        
        # 转换为标准单位
        power_kw = self._convert_to_kw(power, unit)
        
        # 计算电能（假设是15分钟间隔）
        energy_kwh = power_kw * 0.25
        
        return InternalEnergyReading(
            timestamp=timestamp,
            device_id=device_id,
            power_kw=power_kw,
            energy_kwh=energy_kwh
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """解析SEP时间戳"""
        # SEP 2.0使用时间偏移格式
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    
    def _get_text(self, parent: ET.Element, xpath: str) -> Optional[str]:
        """安全获取XML文本"""
        elem = parent.find(xpath, self.NAMESPACES)
        return elem.text if elem is not None else None
    
    def _convert_to_kw(self, value: float, unit: str) -> float:
        """转换为千瓦"""
        conversions = {
            "W": 0.001,
            "kW": 1.0,
            "MW": 1000.0,
            "Wh": 0.001,
            "kWh": 1.0
        }
        return value * conversions.get(unit, 1.0)

# 使用示例
sep_xml_example = '''
<MeterReading xmlns="http://zigbee.org/sep">
    <mRID>meter-001</mRID>
    <ReadingSet>
        <timePeriod>
            <start>2026-02-15T10:00:00Z</start>
            <duration>900</duration>
        </timePeriod>
        <Reading>
            <consumptionBlock>
                <mRID>device-001</mRID>
            </consumptionBlock>
            <value>2500</value>
            <ReadingType>
                <unit>W</unit>
            </ReadingType>
        </Reading>
    </ReadingSet>
</MeterReading>
'''
```

### 2.3 Modbus到能源数据转换

**转换规则**：

- Modbus寄存器 → 能源数据字段
- 字节序转换（Big Endian/Little Endian）
- 缩放因子应用
- 数据类型转换

**转换示例**：

```python
from dataclasses import dataclass
from typing import List, Tuple, Dict
from enum import IntEnum
import struct

class RegisterType(IntEnum):
    """寄存器类型"""
    INPUT = 1      # 读输入寄存器 (FC 04)
    HOLDING = 2    # 读保持寄存器 (FC 03)
    COIL = 3       # 读线圈 (FC 01)
    DISCRETE = 4   # 读离散输入 (FC 02)

@dataclass
class RegisterMapping:
    """寄存器映射定义"""
    address: int
    count: int
    data_type: str  # uint16, int16, uint32, float32, etc.
    scale: float
    unit: str
    field_name: str
    description: str

class ModbusToEnergyConverter:
    """Modbus到能源数据转换器"""
    
    # SunSpec模型寄存器映射
    SUNSPEC_MAPPINGS: List[RegisterMapping] = [
        RegisterMapping(40000, 2, "uint32", 1.0, "", "model_id", "Model ID"),
        RegisterMapping(40002, 2, "uint32", 1.0, "", "model_length", "Model Length"),
        RegisterMapping(40004, 16, "string", 1.0, "", "manufacturer", "Manufacturer"),
        RegisterMapping(40020, 16, "string", 1.0, "", "model", "Model"),
        RegisterMapping(40036, 16, "string", 1.0, "", "version", "Version"),
        RegisterMapping(40052, 16, "string", 1.0, "", "serial", "Serial Number"),
    ]
    
    # 单相逆变器模型 (Model 101)
    INVERTER_101_MAPPINGS: List[RegisterMapping] = [
        RegisterMapping(40069, 1, "uint16", 1.0, "W", "watts", "AC Power"),
        RegisterMapping(40070, 1, "uint16", 1.0, "VA", "va", "AC Apparent Power"),
        RegisterMapping(40071, 1, "uint16", 1.0, "var", "var", "AC Reactive Power"),
        RegisterMapping(40072, 1, "int16", 0.01, "A", "amps", "AC Current"),
        RegisterMapping(40073, 1, "int16", 0.1, "V", "voltage", "AC Voltage"),
        RegisterMapping(40074, 1, "int16", 0.01, "Hz", "frequency", "AC Frequency"),
        RegisterMapping(40075, 1, "int16", 0.001, "", "power_factor", "Power Factor"),
        RegisterMapping(40076, 2, "acc32", 1.0, "Wh", "energy_wh", "Total Energy"),
        RegisterMapping(40078, 2, "acc32", 1.0, "Wh", "energy_dc_wh", "DC Energy"),
        RegisterMapping(40080, 1, "int16", 0.1, "V", "dc_voltage", "DC Voltage"),
        RegisterMapping(40081, 1, "int16", 0.01, "A", "dc_current", "DC Current"),
        RegisterMapping(40082, 1, "int16", 0.1, "C", "temperature", "Temperature"),
        RegisterMapping(40083, 1, "uint16", 1.0, "", "status", "Operating State"),
    ]
    
    def __init__(self, byte_order: str = 'big', word_order: str = 'big'):
        self.byte_order = byte_order
        self.word_order = word_order
    
    def convert_registers(self, registers: List[int], 
                         mappings: List[RegisterMapping]) -> Dict[str, any]:
        """将Modbus寄存器转换为能源数据"""
        result = {}
        
        for mapping in mappings:
            try:
                # 提取原始寄存器值
                raw_values = registers[mapping.address:mapping.address + mapping.count]
                
                # 解析数据
                parsed_value = self._parse_value(raw_values, mapping.data_type)
                
                # 应用缩放因子
                scaled_value = parsed_value * mapping.scale
                
                result[mapping.field_name] = {
                    "value": scaled_value,
                    "unit": mapping.unit,
                    "description": mapping.description
                }
                
            except Exception as e:
                result[mapping.field_name] = {
                    "error": str(e),
                    "description": mapping.description
                }
        
        return result
    
    def _parse_value(self, registers: List[int], data_type: str) -> float:
        """解析寄存器值为具体数据类型"""
        if data_type == "uint16":
            return float(registers[0])
        
        elif data_type == "int16":
            # 处理有符号16位整数
            val = registers[0]
            if val > 32767:
                val -= 65536
            return float(val)
        
        elif data_type == "uint32":
            # 32位无符号整数
            if self.word_order == 'big':
                return float((registers[0] << 16) | registers[1])
            else:
                return float((registers[1] << 16) | registers[0])
        
        elif data_type == "int32":
            # 32位有符号整数
            if self.word_order == 'big':
                val = (registers[0] << 16) | registers[1]
            else:
                val = (registers[1] << 16) | registers[0]
            if val > 2147483647:
                val -= 4294967296
            return float(val)
        
        elif data_type == "float32":
            # 32位浮点数
            if self.word_order == 'big':
                raw = (registers[0] << 16) | registers[1]
            else:
                raw = (registers[1] << 16) | registers[0]
            return struct.unpack('>f', raw.to_bytes(4, 'big'))[0]
        
        elif data_type == "acc32":
            # 32位累积值（SunSpec）
            if self.word_order == 'big':
                val = (registers[0] << 16) | registers[1]
            else:
                val = (registers[1] << 16) | registers[0]
            # 处理特殊值
            if val == 0x00000000:
                return 0.0
            elif val == 0xFFFFFFFF:
                return float('nan')
            return float(val)
        
        elif data_type == "string":
            # 字符串类型
            chars = []
            for reg in registers:
                chars.append(chr((reg >> 8) & 0xFF))
                chars.append(chr(reg & 0xFF))
            return ''.join(chars).rstrip('\x00').strip()
        
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

# 使用示例
converter = ModbusToEnergyConverter()

# 模拟Modbus寄存器数据（单相逆变器）
sample_registers = [0] * 40100  # 初始化寄存器数组

# 填充示例数据（从地址40069开始）
sample_registers[40069] = 2500      # Power (W)
sample_registers[40070] = 2600      # VA
sample_registers[40071] = 500       # var
sample_registers[40072] = 1080      # Current (10.80 A * 100)
sample_registers[40073] = 2305      # Voltage (230.5 V * 10)
sample_registers[40074] = 5000      # Frequency (50.00 Hz * 100)
sample_registers[40075] = 960       # Power Factor (0.96 * 1000)
sample_registers[40076] = 0x0001    # Energy high word
sample_registers[40077] = 0x86A0    # Energy low word (100000 Wh)
sample_registers[40082] = 450       # Temperature (45.0 C * 10)

# 转换数据
energy_data = converter.convert_registers(
    sample_registers, 
    ModbusToEnergyConverter.INVERTER_101_MAPPINGS
)
```

---

## 3. 设备状态同步

### 3.1 智能电表状态同步

**状态同步实现**：

```python
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MeterStatus(Enum):
    """电表状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    COMMUNICATION_ERROR = "comm_error"
    CALIBRATION_ERROR = "cal_error"

@dataclass
class MeterState:
    """电表状态"""
    meter_id: str
    status: MeterStatus
    last_reading: Optional[Dict] = None
    last_communication: Optional[datetime] = None
    communication_quality: float = 100.0  # 百分比
    error_count: int = 0
    consecutive_errors: int = 0

class SmartMeterSyncManager:
    """智能电表状态同步管理器"""
    
    def __init__(self, sync_interval: int = 60):
        self.sync_interval = sync_interval
        self.meter_states: Dict[str, MeterState] = {}
        self.state_callbacks: Dict[str, Callable] = {}
        self.running = False
        self._sync_task: Optional[asyncio.Task] = None
    
    def register_meter(self, meter_id: str, 
                       callback: Optional[Callable] = None):
        """注册电表进行状态同步"""
        self.meter_states[meter_id] = MeterState(
            meter_id=meter_id,
            status=MeterStatus.OFFLINE
        )
        if callback:
            self.state_callbacks[meter_id] = callback
        logger.info(f"Registered meter: {meter_id}")
    
    async def start_sync(self):
        """启动状态同步"""
        self.running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        logger.info("Meter sync manager started")
    
    async def stop_sync(self):
        """停止状态同步"""
        self.running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info("Meter sync manager stopped")
    
    async def _sync_loop(self):
        """同步循环"""
        while self.running:
            for meter_id in self.meter_states:
                try:
                    await self._sync_meter(meter_id)
                except Exception as e:
                    logger.error(f"Error syncing meter {meter_id}: {e}")
                    await self._handle_sync_error(meter_id, e)
            
            await asyncio.sleep(self.sync_interval)
    
    async def _sync_meter(self, meter_id: str):
        """同步单个电表状态"""
        # 模拟读取电表数据
        # 实际实现会调用相应的通信协议（DLMS、Modbus等）
        reading = await self._read_meter_data(meter_id)
        
        state = self.meter_states[meter_id]
        state.last_reading = reading
        state.last_communication = datetime.utcnow()
        state.status = MeterStatus.ONLINE
        state.consecutive_errors = 0
        state.communication_quality = min(100, state.communication_quality + 5)
        
        # 触发回调
        if meter_id in self.state_callbacks:
            await self._trigger_callback(meter_id, state)
    
    async def _read_meter_data(self, meter_id: str) -> Dict:
        """读取电表数据（模拟实现）"""
        # 实际实现需要根据电表协议进行通信
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "active_power": 2.5,
            "voltage": 230.5,
            "current": 10.8,
            "energy_total": 12345.6
        }
    
    async def _handle_sync_error(self, meter_id: str, error: Exception):
        """处理同步错误"""
        state = self.meter_states[meter_id]
        state.error_count += 1
        state.consecutive_errors += 1
        state.communication_quality = max(0, state.communication_quality - 20)
        
        # 连续错误超过阈值，标记为离线
        if state.consecutive_errors >= 3:
            state.status = MeterStatus.COMMUNICATION_ERROR
            logger.warning(f"Meter {meter_id} marked as offline due to communication errors")
        
        # 触发回调
        if meter_id in self.state_callbacks:
            await self._trigger_callback(meter_id, state)
    
    async def _trigger_callback(self, meter_id: str, state: MeterState):
        """触发状态变化回调"""
        callback = self.state_callbacks[meter_id]
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(meter_id, state)
            else:
                callback(meter_id, state)
        except Exception as e:
            logger.error(f"Error in callback for meter {meter_id}: {e}")
    
    def get_meter_state(self, meter_id: str) -> Optional[MeterState]:
        """获取电表状态"""
        return self.meter_states.get(meter_id)
    
    def get_all_states(self) -> Dict[str, MeterState]:
        """获取所有电表状态"""
        return self.meter_states.copy()
```

### 3.2 储能系统状态同步

**储能系统状态同步实现**：

```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class BatteryStatus(Enum):
    """电池状态"""
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    FAULT = "fault"
    STANDBY = "standby"

@dataclass
class BatteryState:
    """电池状态"""
    battery_id: str
    status: BatteryStatus
    soc: float  # 0-1
    soh: float  # 0-1
    voltage: float
    current: float
    temperature: float
    power: float
    capacity_remaining: float
    cycle_count: int
    fault_codes: List[str]

class EnergyStorageSyncManager:
    """储能系统状态同步管理器"""
    
    def __init__(self):
        self.battery_states: Dict[str, BatteryState] = {}
    
    async def sync_battery_state(self, battery_id: str, 
                                 protocol_interface) -> BatteryState:
        """同步电池状态"""
        # 通过协议接口读取电池状态
        raw_data = await protocol_interface.read_battery_status(battery_id)
        
        # 转换为标准状态模型
        state = BatteryState(
            battery_id=battery_id,
            status=self._parse_status(raw_data.get("status")),
            soc=raw_data.get("soc", 0) / 100.0,  # 转换为0-1
            soh=raw_data.get("soh", 100) / 100.0,
            voltage=raw_data.get("voltage", 0),
            current=raw_data.get("current", 0),
            temperature=raw_data.get("temperature", 0),
            power=raw_data.get("power", 0),
            capacity_remaining=raw_data.get("capacity_remaining", 0),
            cycle_count=raw_data.get("cycle_count", 0),
            fault_codes=raw_data.get("fault_codes", [])
        )
        
        self.battery_states[battery_id] = state
        return state
    
    def _parse_status(self, status_code: int) -> BatteryStatus:
        """解析状态码"""
        status_map = {
            0: BatteryStatus.IDLE,
            1: BatteryStatus.CHARGING,
            2: BatteryStatus.DISCHARGING,
            3: BatteryStatus.STANDBY,
            99: BatteryStatus.FAULT
        }
        return status_map.get(status_code, BatteryStatus.FAULT)
```

### 3.3 可控负载状态同步

**可控负载状态同步实现**：

```python
@dataclass
class ControllableLoadState:
    """可控负载状态"""
    load_id: str
    name: str
    is_on: bool
    power: float
    priority: int
    schedule_enabled: bool
    current_schedule: Optional[Dict] = None
    override_until: Optional[datetime] = None

class LoadControlSyncManager:
    """负载控制状态同步管理器"""
    
    def __init__(self):
        self.load_states: Dict[str, ControllableLoadState] = {}
        self.command_queue: asyncio.Queue = asyncio.Queue()
    
    async def sync_load_state(self, load_id: str, 
                             device_interface) -> ControllableLoadState:
        """同步负载状态"""
        # 读取设备状态
        device_state = await device_interface.get_state(load_id)
        
        # 更新本地状态
        state = ControllableLoadState(
            load_id=load_id,
            name=device_state.get("name", load_id),
            is_on=device_state.get("power_state", False),
            power=device_state.get("current_power", 0),
            priority=device_state.get("priority", 5),
            schedule_enabled=device_state.get("schedule_enabled", False)
        )
        
        self.load_states[load_id] = state
        return state
    
    async def execute_command(self, load_id: str, command: str, 
                             params: Dict = None) -> bool:
        """执行负载控制命令"""
        await self.command_queue.put({
            "load_id": load_id,
            "command": command,
            "params": params or {},
            "timestamp": datetime.utcnow()
        })
        return True
```

---

## 4. 协议转换网关

### 4.1 Zigbee SE到IP转换

**网关实现**：

```python
class ZigbeeSEtoIPGateway:
    """Zigbee Smart Energy到IP协议网关"""
    
    def __init__(self):
        self.zigbee_network = None
        self.ip_server = None
        self.device_mappings = {}
    
    async def start(self):
        """启动网关"""
        # 初始化Zigbee网络
        await self._init_zigbee_network()
        
        # 启动IP服务器（REST API或MQTT）
        await self._start_ip_server()
        
        # 启动协议转换循环
        asyncio.create_task(self._conversion_loop())
    
    async def _conversion_loop(self):
        """协议转换循环"""
        while True:
            # 从Zigbee网络接收消息
            zigbee_msg = await self.zigbee_network.receive()
            
            # 转换为IP协议格式（IEEE 2030.5或自定义JSON）
            ip_msg = self._convert_zigbee_to_ip(zigbee_msg)
            
            # 发送到IP网络
            await self.ip_server.publish(ip_msg)
    
    def _convert_zigbee_to_ip(self, zigbee_msg) -> Dict:
        """将Zigbee消息转换为IP格式"""
        cluster_id = zigbee_msg.cluster_id
        
        if cluster_id == 0x0702:  # Simple Metering
            return {
                "type": "meter_reading",
                "device_id": zigbee_msg.device_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "energy": self._parse_energy_attribute(zigbee_msg.attributes),
                    "power": self._parse_power_attribute(zigbee_msg.attributes)
                }
            }
        elif cluster_id == 0x0700:  # Price
            return {
                "type": "price_event",
                "device_id": zigbee_msg.device_id,
                "data": self._parse_price_attributes(zigbee_msg.attributes)
            }
        # ... 其他集群转换
```

### 4.2 Thread到BACnet转换

**网关实现**：

```python
class ThreadToBACnetGateway:
    """Thread到BACnet协议网关"""
    
    def __init__(self):
        self.thread_border_router = None
        self.bacnet_device = None
    
    async def _convert_thread_to_bacnet(self, thread_msg) -> BACnetObject:
        """将Thread消息转换为BACnet对象"""
        # 根据Matter Cluster类型映射到BACnet对象
        cluster = thread_msg.cluster
        
        if cluster == "OnOff":
            return BACnetBinaryOutput(
                object_identifier="BO1",
                present_value=thread_msg.payload["on"]
            )
        elif cluster == "LevelControl":
            return BACnetAnalogOutput(
                object_identifier="AO1",
                present_value=thread_msg.payload["level"] / 254.0 * 100
            )
        elif cluster == "Thermostat":
            return BACnetAnalogValue(
                object_identifier="AV1",
                present_value=thread_msg.payload["occupied_cooling_setpoint"]
            )
        # ... 其他Cluster转换
```

### 4.3 DALI到Zigbee转换

**网关实现**：

```python
class DALItoZigbeeGateway:
    """DALI到Zigbee协议网关"""
    
    def __init__(self):
        self.dali_bus = None
        self.zigbee_network = None
        self.address_mappings = {}
    
    async def _convert_dali_to_zigbee(self, dali_msg):
        """将DALI消息转换为Zigbee消息"""
        dali_address = dali_msg.address
        command = dali_msg.command
        
        # 查找对应的Zigbee设备
        zigbee_device = self.address_mappings.get(dali_address)
        if not zigbee_device:
            return None
        
        # 转换命令
        if command == "DIRECT ARC POWER":
            brightness = dali_msg.data / 254.0  # DALI: 1-254, Zigbee: 0-1
            return ZigbeeLevelControlCommand(
                device=zigbee_device,
                level=int(brightness * 254)
            )
        elif command == "OFF":
            return ZigbeeOnOffCommand(
                device=zigbee_device,
                state=False
            )
        # ... 其他命令转换
```

---

## 5. 能源优化转换

### 5.1 负荷预测模型转换

**模型转换实现**：

```python
import pickle
import json

class LoadForecastModelConverter:
    """负荷预测模型转换器"""
    
    SUPPORTED_FORMATS = ["sklearn", "tensorflow", "pytorch", "onnx"]
    
    def convert_to_onnx(self, model, model_type: str, 
                       input_shape: tuple) -> bytes:
        """将模型转换为ONNX格式"""
        if model_type == "sklearn":
            from skl2onnx import convert_sklearn
            from skl2onnx.common.data_types import FloatTensorType
            
            initial_type = [('float_input', FloatTensorType(input_shape))]
            onnx_model = convert_sklearn(model, initial_types=initial_type)
            return onnx_model.SerializeToString()
        
        elif model_type == "tensorflow":
            import tf2onnx
            import tensorflow as tf
            
            onnx_model, _ = tf2onnx.convert.from_keras(model)
            return onnx_model.SerializeToString()
        
        elif model_type == "pytorch":
            import torch
            import torch.onnx
            
            dummy_input = torch.randn(*input_shape)
            torch.onnx.export(model, dummy_input, "model.onnx")
            
            with open("model.onnx", "rb") as f:
                return f.read()
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def serialize_model_metadata(self, model_info: Dict) -> str:
        """序列化模型元数据"""
        return json.dumps({
            "model_type": model_info["type"],
            "framework": model_info["framework"],
            "version": model_info["version"],
            "input_features": model_info["features"],
            "output_type": model_info["output"],
            "accuracy_metrics": model_info["metrics"],
            "training_date": model_info["training_date"]
        }, indent=2)
```

### 5.2 优化调度策略转换

**策略转换实现**：

```python
class SchedulingStrategyConverter:
    """调度策略转换器"""
    
    def convert_to_milp_model(self, strategy: Dict) -> str:
        """将调度策略转换为MILP模型（Pyomo格式）"""
        template = """
from pyomo.environ import *

model = ConcreteModel()

# 集合
model.T = Set(initialize=range({time_horizon}))  # 时间周期
model.L = Set(initialize={load_ids})  # 负载集合

# 参数
model.P_max = Param(model.L, initialize={max_powers})
model.E_req = Param(model.L, initialize={energy_requirements})
model.T_start = Param(model.L, initialize={earliest_starts})
model.T_end = Param(model.L, initialize={latest_ends})
model.Price = Param(model.T, initialize={electricity_prices})

# 变量
model.x = Var(model.L, model.T, within=Binary)  # 负载l在t时刻是否运行
model.P = Var(model.L, model.T, within=NonNegativeReals)  # 功率

# 目标函数：最小化成本
def obj_rule(model):
    return sum(model.Price[t] * model.P[l,t] for l in model.L for t in model.T)
model.objective = Objective(rule=obj_rule, sense=minimize)

# 约束条件
# ... 约束定义

# 求解
solver = SolverFactory('glpk')
results = solver.solve(model)
"""
        return template.format(
            time_horizon=strategy.get("horizon_hours", 24),
            load_ids=strategy.get("loads", []),
            max_powers={l["id"]: l["max_power"] for l in strategy.get("loads", [])},
            energy_requirements={l["id"]: l["energy"] for l in strategy.get("loads", [])},
            earliest_starts={l["id"]: l["earliest_start"] for l in strategy.get("loads", [])},
            latest_ends={l["id"]: l["latest_end"] for l in strategy.get("loads", [])},
            electricity_prices=strategy.get("prices", [])
        )
    
    def convert_to_heuristic_rules(self, strategy: Dict) -> List[Dict]:
        """将调度策略转换为启发式规则"""
        rules = []
        
        # 峰谷电价规则
        if strategy.get("peak_shaving_enabled"):
            rules.append({
                "name": "peak_shaving",
                "trigger": "price > threshold",
                "action": "defer_loads",
                "priority": 1
            })
        
        # 优先级调度规则
        for load in strategy.get("loads", []):
            if load.get("priority") == "high":
                rules.append({
                    "name": f"priority_{load['id']}",
                    "trigger": "always",
                    "action": f"schedule_first({load['id']})",
                    "priority": 2
                })
        
        return rules
```

### 5.3 碳排放数据转换

**碳排放数据转换实现**：

```python
class CarbonEmissionConverter:
    """碳排放数据转换器"""
    
    # 排放因子（kg CO2/kWh）
    EMISSION_FACTORS = {
        "china_grid_average": 0.5703,
        "china_grid_north": 0.6091,
        "china_grid_northeast": 0.5984,
        "china_grid_east": 0.5257,
        "china_grid_central": 0.4728,
        "china_grid_northwest": 0.5646,
        "china_grid_south": 0.4038,
        "us_grid_average": 0.386,
        "eu_grid_average": 0.276,
        "solar_pv": 0.048,
        "wind": 0.011,
        "natural_gas": 0.490,
        "coal": 0.820
    }
    
    def convert_energy_to_carbon(self, energy_kwh: float, 
                                 source: str,
                                 timestamp: datetime = None) -> Dict:
        """将能源数据转换为碳排放数据"""
        emission_factor = self.EMISSION_FACTORS.get(source, 
                                                     self.EMISSION_FACTORS["china_grid_average"])
        
        carbon_kg = energy_kwh * emission_factor
        
        return {
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
            "energy_kwh": energy_kwh,
            "emission_factor_kg_co2_per_kwh": emission_factor,
            "carbon_emission_kg": round(carbon_kg, 4),
            "energy_source": source,
            "methodology": "grid_average"
        }
    
    def convert_to_carbon_footprint_report(self, 
                                          energy_data: List[Dict],
                                          period: str = "monthly") -> Dict:
        """生成碳足迹报告"""
        total_energy = sum(d.get("energy_kwh", 0) for d in energy_data)
        total_carbon = sum(d.get("carbon_emission_kg", 0) for d in energy_data)
        
        # 按能源类型汇总
        by_source = {}
        for d in energy_data:
            source = d.get("energy_source", "unknown")
            if source not in by_source:
                by_source[source] = {"energy": 0, "carbon": 0}
            by_source[source]["energy"] += d.get("energy_kwh", 0)
            by_source[source]["carbon"] += d.get("carbon_emission_kg", 0)
        
        return {
            "report_period": period,
            "total_energy_kwh": round(total_energy, 2),
            "total_carbon_emission_kg": round(total_carbon, 2),
            "total_carbon_emission_tonnes": round(total_carbon / 1000, 4),
            "average_emission_factor": round(total_carbon / total_energy, 4) if total_energy > 0 else 0,
            "breakdown_by_source": by_source,
            "reduction_recommendations": self._generate_recommendations(by_source)
        }
    
    def _generate_recommendations(self, by_source: Dict) -> List[str]:
        """生成减排建议"""
        recommendations = []
        
        grid_sources = [s for s in by_source.keys() if "grid" in s]
        if grid_sources:
            grid_percentage = sum(by_source[s]["energy"] for s in grid_sources) / \
                            sum(d["energy"] for d in by_source.values()) * 100
            if grid_percentage > 50:
                recommendations.append(
                    f"Consider installing solar panels to reduce grid dependency ({grid_percentage:.1f}%)"
                )
        
        return recommendations
```

---

## 6. 转换工具

### 6.1 协议分析器

**协议分析工具**：

```python
class ProtocolAnalyzer:
    """协议分析器"""
    
    def __init__(self):
        self.packet_log = []
    
    def analyze_packet(self, packet: bytes, protocol: str) -> Dict:
        """分析协议数据包"""
        result = {
            "protocol": protocol,
            "timestamp": datetime.utcnow().isoformat(),
            "raw_hex": packet.hex(),
            "parsed": None,
            "errors": []
        }
        
        try:
            if protocol == "dlms":
                result["parsed"] = self._parse_dlms_packet(packet)
            elif protocol == "modbus":
                result["parsed"] = self._parse_modbus_packet(packet)
            elif protocol == "zigbee":
                result["parsed"] = self._parse_zigbee_packet(packet)
            # ... 其他协议
        except Exception as e:
            result["errors"].append(str(e))
        
        self.packet_log.append(result)
        return result
    
    def _parse_dlms_packet(self, packet: bytes) -> Dict:
        """解析DLMS数据包"""
        # HDLC帧解析
        if packet[0] == 0x7E:  # HDLC帧标志
            return {
                "frame_type": "HDLC",
                "destination": packet[2:6].hex(),
                "source": packet[6:10].hex(),
                "control": packet[10],
                "payload_length": len(packet) - 4
            }
        return {"error": "Unknown DLMS frame format"}
    
    def _parse_modbus_packet(self, packet: bytes) -> Dict:
        """解析Modbus数据包"""
        return {
            "slave_id": packet[0],
            "function_code": packet[1],
            "function_name": self._get_modbus_function_name(packet[1]),
            "data": packet[2:-2].hex(),
            "crc": packet[-2:].hex()
        }
    
    def _get_modbus_function_name(self, code: int) -> str:
        """获取Modbus功能码名称"""
        functions = {
            1: "Read Coils",
            2: "Read Discrete Inputs",
            3: "Read Holding Registers",
            4: "Read Input Registers",
            5: "Write Single Coil",
            6: "Write Single Register",
            16: "Write Multiple Registers"
        }
        return functions.get(code, f"Unknown ({code})")
```

### 6.2 数据映射工具

**数据映射配置工具**：

```python
class DataMappingTool:
    """数据映射工具"""
    
    def __init__(self):
        self.mappings = {}
    
    def create_mapping(self, source_format: str, target_format: str,
                      field_mappings: Dict[str, str]) -> Dict:
        """创建数据映射配置"""
        mapping_config = {
            "source": source_format,
            "target": target_format,
            "version": "1.0",
            "created": datetime.utcnow().isoformat(),
            "fields": field_mappings,
            "transforms": {}
        }
        
        self.mappings[f"{source_format}_to_{target_format}"] = mapping_config
        return mapping_config
    
    def apply_mapping(self, data: Dict, mapping_key: str) -> Dict:
        """应用数据映射"""
        mapping = self.mappings.get(mapping_key)
        if not mapping:
            raise ValueError(f"Mapping not found: {mapping_key}")
        
        result = {}
        for source_field, target_field in mapping["fields"].items():
            if source_field in data:
                result[target_field] = data[source_field]
        
        return result
    
    def validate_mapping(self, mapping_key: str) -> List[str]:
        """验证映射配置的完整性"""
        errors = []
        mapping = self.mappings.get(mapping_key)
        
        if not mapping:
            errors.append("Mapping not found")
            return errors
        
        if not mapping.get("fields"):
            errors.append("No field mappings defined")
        
        # 检查重复的target字段
        targets = list(mapping["fields"].values())
        if len(targets) != len(set(targets)):
            errors.append("Duplicate target fields found")
        
        return errors
```

### 6.3 性能分析器

**性能分析工具**：

```python
import time
from statistics import mean, stdev

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.metrics = {
            "conversion_times": [],
            "packet_sizes": [],
            "error_rates": [],
            "throughput": []
        }
    
    def measure_conversion(self, func, *args, **kwargs):
        """测量转换性能"""
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()
        
        result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        end_memory = self._get_memory_usage()
        
        metrics = {
            "execution_time_ms": (end_time - start_time) * 1000,
            "memory_used_kb": end_memory - start_memory,
            "input_size_bytes": len(str(args)),
            "output_size_bytes": len(str(result))
        }
        
        self.metrics["conversion_times"].append(metrics["execution_time_ms"])
        return result, metrics
    
    def get_statistics(self) -> Dict:
        """获取性能统计"""
        times = self.metrics["conversion_times"]
        
        if not times:
            return {"error": "No data collected"}
        
        return {
            "conversion_time": {
                "count": len(times),
                "mean_ms": mean(times),
                "std_dev_ms": stdev(times) if len(times) > 1 else 0,
                "min_ms": min(times),
                "max_ms": max(times)
            }
        }
    
    def _get_memory_usage(self) -> int:
        """获取当前内存使用"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss // 1024  # KB
```

---

## 7. 转换验证

### 7.1 数据完整性验证

**数据完整性验证实现**：

```python
class DataIntegrityValidator:
    """数据完整性验证器"""
    
    def validate_energy_reading(self, reading: Dict) -> Dict:
        """验证能源读数的完整性"""
        errors = []
        warnings = []
        
        # 必需字段检查
        required_fields = ["timestamp", "device_id", "power_kw"]
        for field in required_fields:
            if field not in reading:
                errors.append(f"Missing required field: {field}")
        
        # 数值范围检查
        if "power_kw" in reading:
            power = reading["power_kw"]
            if power < 0:
                errors.append("Power cannot be negative")
            elif power > 1000:  # 假设家庭最大功率1000kW
                warnings.append("Power value unusually high")
        
        if "voltage" in reading:
            voltage = reading["voltage"]
            if voltage < 100 or voltage > 300:
                errors.append("Voltage out of normal range (100-300V)")
        
        # 时间戳检查
        if "timestamp" in reading:
            try:
                ts = datetime.fromisoformat(reading["timestamp"].replace('Z', '+00:00'))
                age = (datetime.utcnow() - ts.replace(tzinfo=None)).total_seconds()
                if age > 3600:  # 超过1小时
                    warnings.append("Reading is older than 1 hour")
            except ValueError:
                errors.append("Invalid timestamp format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
```

### 7.2 协议一致性验证

**协议一致性验证实现**：

```python
class ProtocolConformanceValidator:
    """协议一致性验证器"""
    
    def validate_dlms_message(self, message: bytes) -> Dict:
        """验证DLMS消息的一致性"""
        errors = []
        
        # HDLC帧格式检查
        if len(message) < 10:
            errors.append("Message too short for HDLC frame")
            return {"valid": False, "errors": errors}
        
        # 帧标志检查
        if message[0] != 0x7E or message[-1] != 0x7E:
            errors.append("Invalid HDLC frame delimiters")
        
        # 长度字段检查
        frame_length = (message[1] & 0x07) << 8 | message[2]
        if frame_length != len(message) - 2:
            errors.append(f"Frame length mismatch: expected {frame_length}, got {len(message) - 2}")
        
        # CRC检查
        calculated_crc = self._calculate_crc16(message[1:-3])
        received_crc = int.from_bytes(message[-3:-1], 'big')
        if calculated_crc != received_crc:
            errors.append("CRC mismatch")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _calculate_crc16(self, data: bytes) -> int:
        """计算CRC16"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
```

### 7.3 性能基准测试

**性能基准测试实现**：

```python
class ConversionBenchmark:
    """转换性能基准测试"""
    
    def __init__(self):
        self.results = {}
    
    async def run_benchmark(self, converter, test_data: List[Dict],
                           iterations: int = 1000) -> Dict:
        """运行基准测试"""
        import time
        
        times = []
        
        for _ in range(iterations):
            for data in test_data:
                start = time.perf_counter()
                await converter.convert(data)
                end = time.perf_counter()
                times.append((end - start) * 1000)  # ms
        
        return {
            "converter": converter.__class__.__name__,
            "iterations": iterations,
            "test_data_count": len(test_data),
            "average_time_ms": mean(times),
            "median_time_ms": sorted(times)[len(times) // 2],
            "p95_time_ms": sorted(times)[int(len(times) * 0.95)],
            "p99_time_ms": sorted(times)[int(len(times) * 0.99)],
            "throughput_per_second": iterations * len(test_data) / sum(times) * 1000
        }
```

---

## 8. Energy Management数据存储与分析

### 8.1 PostgreSQL能源数据存储

**数据库存储实现**：

```python
import psycopg2
import psycopg2.extras
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta

class EnergyDataStorage:
    """能源数据存储系统"""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表"""
        # 能源读数表（分区表）
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_readings (
                id BIGSERIAL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                device_id VARCHAR(50) NOT NULL,
                device_type VARCHAR(30),
                power_kw DECIMAL(8,3),
                energy_kwh DECIMAL(12,6),
                voltage DECIMAL(6,2),
                current DECIMAL(6,4),
                power_factor DECIMAL(4,3),
                frequency DECIMAL(5,2),
                metadata JSONB,
                PRIMARY KEY (timestamp, device_id)
            ) PARTITION BY RANGE (timestamp)
        """)
        
        # 创建月度分区
        self._create_partitions()
        
        # 设备信息表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id VARCHAR(50) PRIMARY KEY,
                device_type VARCHAR(30) NOT NULL,
                device_name VARCHAR(100),
                location VARCHAR(100),
                rated_power DECIMAL(8,3),
                installation_date DATE,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 能源统计表（按小时/日/月汇总）
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_statistics (
                id SERIAL PRIMARY KEY,
                period_type VARCHAR(10) NOT NULL,  -- hour, day, month
                period_start TIMESTAMP WITH TIME ZONE NOT NULL,
                device_id VARCHAR(50),
                total_energy_kwh DECIMAL(12,6),
                avg_power_kw DECIMAL(8,3),
                max_power_kw DECIMAL(8,3),
                min_power_kw DECIMAL(8,3),
                cost DECIMAL(10,4),
                UNIQUE(period_type, period_start, device_id)
            )
        """)
        
        self.conn.commit()
    
    def _create_partitions(self):
        """创建时间分区"""
        # 创建未来12个月的分区
        for i in range(12):
            start_date = datetime.now().replace(day=1) + timedelta(days=30*i)
            end_date = start_date + timedelta(days=32)
            end_date = end_date.replace(day=1)
            
            partition_name = f"energy_readings_{start_date.strftime('%Y%m')}"
            
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {partition_name} 
                PARTITION OF energy_readings
                FOR VALUES FROM ('{start_date.isoformat()}') 
                TO ('{end_date.isoformat()}')
            """)
        
        self.conn.commit()
    
    def store_reading(self, reading: Dict):
        """存储能源读数"""
        self.cursor.execute("""
            INSERT INTO energy_readings 
            (timestamp, device_id, device_type, power_kw, energy_kwh,
             voltage, current, power_factor, frequency, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp, device_id) DO UPDATE SET
            power_kw = EXCLUDED.power_kw,
            energy_kwh = EXCLUDED.energy_kwh,
            voltage = EXCLUDED.voltage,
            current = EXCLUDED.current,
            power_factor = EXCLUDED.power_factor,
            frequency = EXCLUDED.frequency,
            metadata = EXCLUDED.metadata
        """, (
            reading.get("timestamp"),
            reading.get("device_id"),
            reading.get("device_type"),
            reading.get("power_kw"),
            reading.get("energy_kwh"),
            reading.get("voltage"),
            reading.get("current"),
            reading.get("power_factor"),
            reading.get("frequency"),
            json.dumps(reading.get("metadata", {}))
        ))
        
        self.conn.commit()
    
    def store_readings_batch(self, readings: List[Dict]):
        """批量存储能源读数"""
        data = [(
            r.get("timestamp"),
            r.get("device_id"),
            r.get("device_type"),
            r.get("power_kw"),
            r.get("energy_kwh"),
            r.get("voltage"),
            r.get("current"),
            r.get("power_factor"),
            r.get("frequency"),
            json.dumps(r.get("metadata", {}))
        ) for r in readings]
        
        psycopg2.extras.execute_values(
            self.cursor,
            """
            INSERT INTO energy_readings 
            (timestamp, device_id, device_type, power_kw, energy_kwh,
             voltage, current, power_factor, frequency, metadata)
            VALUES %s
            ON CONFLICT (timestamp, device_id) DO UPDATE SET
            power_kw = EXCLUDED.power_kw,
            energy_kwh = EXCLUDED.energy_kwh,
            metadata = EXCLUDED.metadata
            """,
            data
        )
        
        self.conn.commit()
    
    def get_readings(self, device_id: str, start_time: datetime,
                    end_time: datetime) -> List[Dict]:
        """查询能源读数"""
        self.cursor.execute("""
            SELECT * FROM energy_readings
            WHERE device_id = %s AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp
        """, (device_id, start_time, end_time))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
```

### 8.2 时序数据库应用

**InfluxDB集成实现**：

```python
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import List, Dict

class InfluxDBEnergyStorage:
    """基于InfluxDB的能源数据存储"""
    
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = bucket
    
    def store_reading(self, reading: Dict):
        """存储能源读数到InfluxDB"""
        point = Point("energy_reading") \
            .tag("device_id", reading["device_id"]) \
            .tag("device_type", reading.get("device_type", "unknown")) \
            .field("power_kw", reading.get("power_kw", 0.0)) \
            .field("voltage", reading.get("voltage", 0.0)) \
            .field("current", reading.get("current", 0.0)) \
            .time(reading["timestamp"])
        
        if "energy_kwh" in reading:
            point = point.field("energy_kwh", reading["energy_kwh"])
        
        if "power_factor" in reading:
            point = point.field("power_factor", reading["power_factor"])
        
        self.write_api.write(bucket=self.bucket, record=point)
    
    def query_aggregate(self, device_id: str, start: str, stop: str,
                       window: str = "1h") -> List[Dict]:
        """查询聚合数据"""
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: {start}, stop: {stop})
            |> filter(fn: (r) => r._measurement == "energy_reading")
            |> filter(fn: (r) => r.device_id == "{device_id}")
            |> aggregateWindow(every: {window}, fn: mean)
        '''
        
        tables = self.query_api.query(query)
        
        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "timestamp": record.get_time(),
                    "field": record.get_field(),
                    "value": record.get_value()
                })
        
        return results
```

### 8.3 能源数据分析查询

**数据分析查询实现**：

```python
class EnergyDataAnalyzer:
    """能源数据分析器"""
    
    def __init__(self, storage: EnergyDataStorage):
        self.storage = storage
    
    def get_daily_consumption(self, device_id: str, 
                             date: datetime) -> Dict:
        """获取日用电量"""
        start = date.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        
        readings = self.storage.get_readings(device_id, start, end)
        
        if not readings:
            return {"error": "No data available"}
        
        total_energy = sum(r.get("energy_kwh", 0) for r in readings if r.get("energy_kwh"))
        avg_power = sum(r.get("power_kw", 0) for r in readings) / len(readings) if readings else 0
        max_power = max(r.get("power_kw", 0) for r in readings) if readings else 0
        
        # 按小时分组
        hourly_data = {}
        for r in readings:
            hour = r["timestamp"].hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(r.get("power_kw", 0))
        
        hourly_avg = {h: sum(v)/len(v) for h, v in hourly_data.items()}
        
        return {
            "date": date.isoformat(),
            "device_id": device_id,
            "total_energy_kwh": round(total_energy, 4),
            "average_power_kw": round(avg_power, 3),
            "max_power_kw": round(max_power, 3),
            "peak_hour": max(hourly_avg, key=hourly_avg.get) if hourly_avg else None,
            "hourly_consumption": {h: round(v, 3) for h, v in hourly_avg.items()}
        }
    
    def get_load_profile(self, device_id: str, start_date: datetime,
                        days: int = 7) -> List[Dict]:
        """获取负荷曲线"""
        end_date = start_date + timedelta(days=days)
        
        readings = self.storage.get_readings(device_id, start_date, end_date)
        
        # 按15分钟间隔聚合
        profile = []
        current_slot = None
        slot_values = []
        
        for r in sorted(readings, key=lambda x: x["timestamp"]):
            ts = r["timestamp"]
            slot_start = ts.replace(minute=(ts.minute // 15) * 15, second=0, microsecond=0)
            
            if current_slot != slot_start:
                if slot_values:
                    profile.append({
                        "timestamp": current_slot.isoformat(),
                        "average_power_kw": round(sum(slot_values) / len(slot_values), 3),
                        "max_power_kw": round(max(slot_values), 3),
                        "min_power_kw": round(min(slot_values), 3)
                    })
                current_slot = slot_start
                slot_values = []
            
            slot_values.append(r.get("power_kw", 0))
        
        return profile
    
    def calculate_baseline(self, device_id: str, 
                          period_days: int = 30) -> Dict:
        """计算能耗基准线"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        readings = self.storage.get_readings(device_id, start_date, end_date)
        
        if not readings:
            return {"error": "Insufficient data"}
        
        powers = [r.get("power_kw", 0) for r in readings]
        
        # 按星期几分组
        weekday_powers = {i: [] for i in range(7)}
        for r in readings:
            weekday = r["timestamp"].weekday()
            weekday_powers[weekday].append(r.get("power_kw", 0))
        
        baseline = {
            "device_id": device_id,
            "period_days": period_days,
            "overall": {
                "average_power_kw": round(sum(powers) / len(powers), 3),
                "max_power_kw": round(max(powers), 3),
                "min_power_kw": round(min(powers), 3)
            },
            "by_weekday": {
                day: {
                    "average": round(sum(vals)/len(vals), 3) if vals else 0,
                    "max": round(max(vals), 3) if vals else 0
                }
                for day, vals in weekday_powers.items()
            }
        }
        
        return baseline
```

---

**参考文档**：

- `01_Overview.md` - 概述文档
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标

**创建时间**：2026-02-15
**最后更新**：2026-02-15
