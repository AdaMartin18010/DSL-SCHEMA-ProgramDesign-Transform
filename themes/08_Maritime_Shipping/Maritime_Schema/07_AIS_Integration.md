# AIS数据集成完整实现

## 概述

本文档提供完整的AIS（Automatic Identification System）自动识别系统集成实现，支持实时船舶位置追踪、数据解析和历史记录管理。

---

## 1. AIS数据解析器完整实现

```python
"""
AIS数据集成完整实现
支持AIS NMEA消息格式，实时船舶位置追踪
"""
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
import asyncio
from collections import deque

logger = logging.getLogger(__name__)


class AISMessageType(Enum):
    """AIS消息类型"""
    POSITION_REPORT_CLASS_A = 1
    POSITION_REPORT_CLASS_A_EXT = 2
    POSITION_REPORT_CLASS_A_RSP = 3
    BASE_STATION_REPORT = 4
    STATIC_VOYAGE_DATA = 5
    BINARY_ADDRESSED = 6
    BINARY_BROADCAST = 8
    SAR_AIRCRAFT_POSITION = 9
    UTC_DATE_INQUIRY = 10
    UTC_DATE_RESPONSE = 11
    ADDRESSED_SAFETY = 12
    SAFETY_BROADCAST = 14
    INTERROGATION = 15
    ASSIGN_MODE_COMMAND = 16
    DGNSS_BROADCAST = 17
    STANDARD_CLASS_B_POSITION = 18
    EXTENDED_CLASS_B_POSITION = 19
    DATA_LINK_MANAGEMENT = 20
    AID_TO_NAVIGATION_REPORT = 21
    CHANNEL_MANAGEMENT = 22
    GROUP_ASSIGNMENT = 23
    STATIC_DATA_REPORT = 24
    SINGLE_SLOT_BINARY = 25
    MULTIPLE_SLOT_BINARY = 26
    LONG_RANGE_AIS_BROADCAST = 27


@dataclass
class AISPositionReport:
    """AIS位置报告"""
    mmsi: str
    message_type: int
    timestamp: datetime
    
    # 位置信息
    latitude: float = 0.0
    longitude: float = 0.0
    position_accuracy: bool = False  # True = high (<10m), False = low (>10m)
    
    # 运动信息
    sog: float = 0.0  # Speed Over Ground (knots)
    cog: float = 0.0  # Course Over Ground (degrees)
    heading: int = 0  # True heading (degrees)
    
    # 导航状态
    navigation_status: int = 15  # 15 = Not defined
    nav_status_description: str = "Not defined"
    
    # 时间戳
    utc_second: int = 60  # 60 = not available
    
    # 操纵指示器
    maneuver_indicator: int = 0  # 0 = not available
    
    # 接收元数据
    received_time: datetime = field(default_factory=datetime.now)
    data_source: str = ""


@dataclass
class AISStaticData:
    """AIS静态数据"""
    mmsi: str
    message_type: int = 5
    
    # 船舶信息
    imo_number: str = ""
    callsign: str = ""
    vessel_name: str = ""
    vessel_type: int = 0
    vessel_type_description: str = ""
    
    # 尺寸信息（米）
    dimension_to_bow: int = 0
    dimension_to_stern: int = 0
    dimension_to_port: int = 0
    dimension_to_starboard: int = 0
    
    # 位置参考点
    epfd_type: int = 0  # 0 = undefined
    epfd_description: str = "Undefined"
    
    # 预计到达时间
    eta_month: int = 0
    eta_day: int = 0
    eta_hour: int = 24  # 24 = not available
    eta_minute: int = 60  # 60 = not available
    
    # 目的地
    destination: str = ""
    
    # 船舶吃水
    draught: float = 0.0  # meters / 10
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AISClassBPosition:
    """AIS Class B位置报告"""
    mmsi: str
    message_type: int = 18
    timestamp: datetime
    
    latitude: float = 0.0
    longitude: float = 0.0
    sog: float = 0.0
    cog: float = 0.0
    heading: int = 0
    
    # Class B特定字段
    cs_unit: bool = False  # True = Class S
    display_flag: bool = False
    dsc_flag: bool = False
    band_flag: bool = False
    msg22_flag: bool = False
    assigned: bool = False


class AISDecoder:
    """AIS解码器"""
    
    # 导航状态映射
    NAVIGATION_STATUS = {
        0: "Under way using engine",
        1: "At anchor",
        2: "Not under command",
        3: "Restricted manoeuverability",
        4: "Constrained by her draught",
        5: "Moored",
        6: "Aground",
        7: "Engaged in fishing",
        8: "Under way sailing",
        9: "Reserved",
        10: "Reserved",
        11: "Reserved",
        12: "Reserved",
        13: "Reserved",
        14: "Reserved",
        15: "Not defined"
    }
    
    # 船舶类型映射
    VESSEL_TYPES = {
        0: "Not available",
        20: "Wing in ground (WIG)",
        30: "Fishing",
        31: "Towing",
        32: "Towing: length exceeds 200m or breadth exceeds 25m",
        33: "Engaged in dredging or underwater operations",
        34: "Engaged in diving operations",
        35: "Engaged in military operations",
        36: "Sailing",
        37: "Pleasure craft",
        40: "High speed craft (HSC)",
        50: "Pilot vessel",
        51: "Search and rescue vessel",
        52: "Tug",
        53: "Port tender",
        54: "Anti-pollution equipment",
        55: "Law enforcement",
        56: "Spare - Local Vessel",
        57: "Spare - Local Vessel",
        58: "Medical transport",
        59: "Non-combatant ship",
        60: "Passenger",
        70: "Cargo",
        71: "Cargo - Hazardous category A",
        72: "Cargo - Hazardous category B",
        73: "Cargo - Hazardous category C",
        74: "Cargo - Hazardous category D",
        80: "Tanker",
        81: "Tanker - Hazardous category A",
        82: "Tanker - Hazardous category B",
        83: "Tanker - Hazardous category C",
        84: "Tanker - Hazardous category D",
        90: "Other Type"
    }
    
    def __init__(self):
        self.message_buffer: Dict[str, List[str]] = {}  # 用于多片段消息
    
    def decode_nmea_sentence(self, sentence: str) -> Optional[Dict[str, Any]]:
        """解码NMEA句子"""
        try:
            # 验证校验和
            if not self._verify_checksum(sentence):
                logger.warning("Checksum verification failed")
                return None
            
            # 解析NMEA句子
            parts = sentence.split(',')
            
            if len(parts) < 6:
                return None
            
            msg_type = parts[0]
            
            if msg_type == "!AIVDM" or msg_type == "!AIVDO":
                return self._decode_aivdm(parts)
            elif msg_type == "$GPGGA" or msg_type.startswith("$GP"):
                # GPS句子（可选处理）
                return self._decode_gps(parts)
            
            return None
            
        except Exception as e:
            logger.error(f"Error decoding NMEA sentence: {e}")
            return None
    
    def _verify_checksum(self, sentence: str) -> bool:
        """验证NMEA校验和"""
        if '*' not in sentence:
            return False
        
        data, checksum_str = sentence.split('*')
        data = data[1:]  # 移除起始字符
        
        try:
            checksum = int(checksum_str[:2], 16)
            calculated = 0
            for char in data:
                calculated ^= ord(char)
            return checksum == calculated
        except:
            return False
    
    def _decode_aivdm(self, parts: List[str]) -> Optional[Dict[str, Any]]:
        """解码AIVDM消息"""
        try:
            fragment_count = int(parts[1])
            fragment_number = int(parts[2])
            message_id = parts[3] if parts[3] else "0"
            channel = parts[4]
            payload = parts[5]
            
            # 处理多片段消息
            if fragment_count > 1:
                key = f"{message_id}_{channel}"
                
                if fragment_number == 1:
                    self.message_buffer[key] = [payload]
                    return None  # 等待更多片段
                else:
                    if key not in self.message_buffer:
                        return None
                    self.message_buffer[key].append(payload)
                    
                    if fragment_number == fragment_count:
                        # 最后一片段，组合完整消息
                        payload = ''.join(self.message_buffer[key])
                        del self.message_buffer[key]
                    else:
                        return None  # 等待更多片段
            
            # 解码6-bit ASCII
            bits = self._decode_6bit_ascii(payload)
            
            # 提取消息类型
            message_type = self._extract_bits(bits, 0, 6)
            
            # 根据消息类型解码
            if message_type in [1, 2, 3]:
                return self._decode_position_report_class_a(bits, message_type)
            elif message_type == 5:
                return self._decode_static_voyage_data(bits)
            elif message_type == 18:
                return self._decode_standard_class_b_position(bits)
            elif message_type == 19:
                return self._decode_extended_class_b_position(bits)
            elif message_type == 24:
                return self._decode_static_data_report(bits)
            else:
                logger.debug(f"Unsupported message type: {message_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error decoding AIVDM: {e}")
            return None
    
    def _decode_6bit_ascii(self, payload: str) -> str:
        """将6-bit ASCII编码转换为位字符串"""
        bit_string = ""
        for char in payload:
            # 将字符转换为6位值
            if 48 <= ord(char) <= 87:  # '0'-'W'
                value = ord(char) - 48
            elif 96 <= ord(char) <= 119:  # '`'-'w'
                value = ord(char) - 56
            else:
                value = 0
            
            # 转换为6位二进制字符串
            bit_string += format(value, '06b')
        
        return bit_string
    
    def _extract_bits(self, bit_string: str, start: int, length: int) -> int:
        """从位字符串中提取整数值"""
        end = start + length
        if end > len(bit_string):
            return 0
        return int(bit_string[start:end], 2)
    
    def _extract_signed_bits(self, bit_string: str, start: int, length: int) -> int:
        """提取有符号整数值"""
        value = self._extract_bits(bit_string, start, length)
        # 处理补码
        if value >= (1 << (length - 1)):
            value -= (1 << length)
        return value
    
    def _decode_6bit_text(self, bit_string: str, start: int, length: int) -> str:
        """解码6-bit ASCII文本"""
        result = ""
        for i in range(start, start + length, 6):
            char_code = self._extract_bits(bit_string, i, 6)
            if char_code == 0:
                break
            # 6-bit ASCII转换
            if char_code < 32:
                char_code += 64
            result += chr(char_code)
        return result.strip('@')
    
    def _decode_position_report_class_a(self, bits: str, message_type: int) -> AISPositionReport:
        """解码Class A位置报告"""
        report = AISPositionReport(
            mmsi=str(self._extract_bits(bits, 8, 30)),
            message_type=message_type,
            timestamp=datetime.now()
        )
        
        # 导航状态
        report.navigation_status = self._extract_bits(bits, 38, 4)
        report.nav_status_description = self.NAVIGATION_STATUS.get(
            report.navigation_status, "Unknown"
        )
        
        # 转向率（可选）
        rot = self._extract_signed_bits(bits, 42, 8)
        
        # 对地速度
        sog_raw = self._extract_bits(bits, 50, 10)
        report.sog = sog_raw / 10.0 if sog_raw != 1023 else 0.0
        
        # 位置准确度
        report.position_accuracy = bool(self._extract_bits(bits, 60, 1))
        
        # 经度
        lon_raw = self._extract_signed_bits(bits, 61, 28)
        report.longitude = lon_raw / 600000.0 if lon_raw != 0x6791AC0 else 0.0
        
        # 纬度
        lat_raw = self._extract_signed_bits(bits, 89, 27)
        report.latitude = lat_raw / 600000.0 if lat_raw != 0x3412140 else 0.0
        
        # 对地航向
        cog_raw = self._extract_bits(bits, 116, 12)
        report.cog = cog_raw / 10.0 if cog_raw != 3600 else 0.0
        
        # 真航向
        report.heading = self._extract_bits(bits, 128, 9)
        if report.heading == 511:
            report.heading = 0
        
        # UTC秒
        report.utc_second = self._extract_bits(bits, 137, 6)
        
        # 操纵指示器
        report.maneuver_indicator = self._extract_bits(bits, 143, 2)
        
        return report
    
    def _decode_static_voyage_data(self, bits: str) -> AISStaticData:
        """解码静态和航次数据"""
        data = AISStaticData(
            mmsi=str(self._extract_bits(bits, 8, 30))
        )
        
        # IMO编号
        data.imo_number = str(self._extract_bits(bits, 40, 30))
        
        # 呼号
        data.callsign = self._decode_6bit_text(bits, 70, 42).strip()
        
        # 船名
        data.vessel_name = self._decode_6bit_text(bits, 112, 120).strip()
        
        # 船舶类型
        data.vessel_type = self._extract_bits(bits, 232, 8)
        data.vessel_type_description = self.VESSEL_TYPES.get(
            data.vessel_type, "Unknown"
        )
        
        # 尺寸
        data.dimension_to_bow = self._extract_bits(bits, 240, 9)
        data.dimension_to_stern = self._extract_bits(bits, 249, 9)
        data.dimension_to_port = self._extract_bits(bits, 258, 6)
        data.dimension_to_starboard = self._extract_bits(bits, 264, 6)
        
        # 定位设备类型
        data.epfd_type = self._extract_bits(bits, 270, 4)
        
        # 预计到达时间
        data.eta_month = self._extract_bits(bits, 274, 4)
        data.eta_day = self._extract_bits(bits, 278, 5)
        data.eta_hour = self._extract_bits(bits, 283, 5)
        data.eta_minute = self._extract_bits(bits, 288, 6)
        
        # 吃水
        data.draught = self._extract_bits(bits, 294, 8) / 10.0
        
        # 目的地
        data.destination = self._decode_6bit_text(bits, 302, 120).strip()
        
        return data
    
    def _decode_standard_class_b_position(self, bits: str) -> AISClassBPosition:
        """解码Standard Class B位置报告"""
        report = AISClassBPosition(
            mmsi=str(self._extract_bits(bits, 8, 30)),
            timestamp=datetime.now()
        )
        
        # 区域
        region = self._extract_bits(bits, 38, 8)
        
        # 速度
        sog_raw = self._extract_bits(bits, 46, 10)
        report.sog = sog_raw / 10.0 if sog_raw != 1023 else 0.0
        
        # 位置准确度
        report.position_accuracy = bool(self._extract_bits(bits, 56, 1))
        
        # 经度
        lon_raw = self._extract_signed_bits(bits, 57, 28)
        report.longitude = lon_raw / 600000.0 if lon_raw != 0x6791AC0 else 0.0
        
        # 纬度
        lat_raw = self._extract_signed_bits(bits, 85, 27)
        report.latitude = lat_raw / 600000.0 if lat_raw != 0x3412140 else 0.0
        
        # 航向
        cog_raw = self._extract_bits(bits, 112, 12)
        report.cog = cog_raw / 10.0 if cog_raw != 3600 else 0.0
        
        # 真航向
        report.heading = self._extract_bits(bits, 124, 9)
        if report.heading == 511:
            report.heading = 0
        
        # UTC秒
        report.utc_second = self._extract_bits(bits, 133, 6)
        
        # Class B标志
        report.cs_unit = bool(self._extract_bits(bits, 141, 1))
        report.display_flag = bool(self._extract_bits(bits, 142, 1))
        report.dsc_flag = bool(self._extract_bits(bits, 143, 1))
        report.band_flag = bool(self._extract_bits(bits, 144, 1))
        report.msg22_flag = bool(self._extract_bits(bits, 145, 1))
        report.assigned = bool(self._extract_bits(bits, 146, 1))
        
        return report
    
    def _decode_extended_class_b_position(self, bits: str) -> Dict[str, Any]:
        """解码Extended Class B位置报告"""
        # 类似Standard Class B，但包含更多字段
        standard = self._decode_standard_class_b_position(bits)
        
        # 扩展字段
        result = {
            "type": "extended_class_b",
            "position": standard,
            "vessel_name": self._decode_6bit_text(bits, 143, 120).strip(),
            "vessel_type": self._extract_bits(bits, 263, 8)
        }
        
        return result
    
    def _decode_static_data_report(self, bits: str) -> Dict[str, Any]:
        """解码静态数据报告（Message 24）"""
        mmsi = str(self._extract_bits(bits, 8, 30))
        part_number = self._extract_bits(bits, 38, 2)
        
        if part_number == 0:
            # Part A - 船名
            return {
                "mmsi": mmsi,
                "part": "A",
                "vessel_name": self._decode_6bit_text(bits, 40, 120).strip()
            }
        else:
            # Part B - 船舶类型等信息
            return {
                "mmsi": mmsi,
                "part": "B",
                "vessel_type": self._extract_bits(bits, 40, 8),
                "vendor_id": self._decode_6bit_text(bits, 48, 42),
                "callsign": self._decode_6bit_text(bits, 90, 42).strip(),
                "dimension_to_bow": self._extract_bits(bits, 132, 9),
                "dimension_to_stern": self._extract_bits(bits, 141, 9),
                "dimension_to_port": self._extract_bits(bits, 150, 6),
                "dimension_to_starboard": self._extract_bits(bits, 156, 6)
            }
    
    def _decode_gps(self, parts: List[str]) -> Dict[str, Any]:
        """解码GPS句子（简化处理）"""
        return {"type": "gps", "raw": parts}


class AISDataProcessor:
    """AIS数据处理器"""
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        # 当前位置缓存
        self.current_positions: Dict[str, AISPositionReport] = {}
        # 静态数据缓存
        self.static_data: Dict[str, AISStaticData] = {}
        # 位置历史
        self.position_history: Dict[str, deque] = {}
        # 解码器
        self.decoder = AISDecoder()
    
    def process_message(self, nmea_sentence: str) -> Optional[Dict[str, Any]]:
        """处理AIS消息"""
        result = self.decoder.decode_nmea_sentence(nmea_sentence)
        
        if result is None:
            return None
        
        # 根据类型处理
        if isinstance(result, AISPositionReport):
            self._update_position(result)
            return {"type": "position", "data": result}
        
        elif isinstance(result, AISStaticData):
            self._update_static_data(result)
            return {"type": "static", "data": result}
        
        elif isinstance(result, AISClassBPosition):
            # 转换为标准位置报告
            position = AISPositionReport(
                mmsi=result.mmsi,
                message_type=result.message_type,
                timestamp=result.timestamp,
                latitude=result.latitude,
                longitude=result.longitude,
                sog=result.sog,
                cog=result.cog,
                heading=result.heading
            )
            self._update_position(position)
            return {"type": "position", "data": position}
        
        return {"type": "other", "data": result}
    
    def _update_position(self, report: AISPositionReport):
        """更新船舶位置"""
        mmsi = report.mmsi
        
        # 更新当前位置
        self.current_positions[mmsi] = report
        
        # 添加到历史
        if mmsi not in self.position_history:
            self.position_history[mmsi] = deque(maxlen=self.max_history_size)
        
        self.position_history[mmsi].append(report)
    
    def _update_static_data(self, data: AISStaticData):
        """更新静态数据"""
        self.static_data[data.mmsi] = data
    
    def get_vessel_position(self, mmsi: str) -> Optional[AISPositionReport]:
        """获取船舶当前位置"""
        return self.current_positions.get(mmsi)
    
    def get_vessel_history(self, mmsi: str, 
                          hours: int = 24) -> List[AISPositionReport]:
        """获取船舶位置历史"""
        if mmsi not in self.position_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = list(self.position_history[mmsi])
        
        return [h for h in history if h.timestamp >= cutoff_time]
    
    def get_vessels_in_area(self, min_lat: float, max_lat: float,
                           min_lon: float, max_lon: float) -> List[AISPositionReport]:
        """获取区域内的船舶"""
        vessels = []
        for position in self.current_positions.values():
            if (min_lat <= position.latitude <= max_lat and
                min_lon <= position.longitude <= max_lon):
                vessels.append(position)
        return vessels
    
    def get_vessel_info(self, mmsi: str) -> Dict[str, Any]:
        """获取船舶完整信息"""
        info = {
            "mmsi": mmsi,
            "position": None,
            "static": None,
            "history_count": 0
        }
        
        if mmsi in self.current_positions:
            info["position"] = self.current_positions[mmsi]
        
        if mmsi in self.static_data:
            info["static"] = self.static_data[mmsi]
        
        if mmsi in self.position_history:
            info["history_count"] = len(self.position_history[mmsi])
        
        return info
    
    def calculate_distance(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """计算两点间距离（海里）"""
        R = 3440.065  # 地球半径（海里）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_cpa(self, vessel1: AISPositionReport, 
                     vessel2: AISPositionReport) -> Dict[str, float]:
        """计算最近会遇距离（CPA）和时间（TCPA）"""
        # 简化的CPA计算
        # 实际实现需要考虑速度和航向的矢量计算
        current_distance = self.calculate_distance(
            vessel1.latitude, vessel1.longitude,
            vessel2.latitude, vessel2.longitude
        )
        
        # 这里应该实现完整的CPA/TCPA计算
        # 简化返回当前距离
        return {
            "cpa": current_distance,
            "tcpa": 0.0,  # 需要矢量计算
            "current_distance": current_distance
        }


# 使用示例
if __name__ == "__main__":
    processor = AISDataProcessor()
    
    # 示例AIS消息
    test_messages = [
        "!AIVDM,1,1,,A,133s@fhP00PE8lFMOv;WQ3?vL0<1B,0*5C",
        "!AIVDM,1,1,,B,13u@E5gP00PdOlFMOW2`8wvN0L0J,0*20",
        "!AIVDM,2,1,0,B,55M2;L01>L`LU@<R20HpN1PD4p0l<h4pB22216Dp3>@<P,0*46",
        "!AIVDM,2,2,0,B,h1LHB@H88P`88885,2*66"
    ]
    
    for msg in test_messages:
        result = processor.process_message(msg)
        if result:
            print(f"Processed: {result['type']}")
            if result['type'] == 'position':
                pos = result['data']
                print(f"  MMSI: {pos.mmsi}, Position: {pos.latitude}, {pos.longitude}")
```

---

## 2. AIS数据集成使用说明

### 2.1 实时数据处理

```python
from ais_integration import AISDataProcessor

# 创建处理器
processor = AISDataProcessor(max_history_size=10000)

# 处理AIS消息
nmea_sentence = "!AIVDM,1,1,,A,133s@fhP00PE8lFMOv;WQ3?vL0<1B,0*5C"
result = processor.process_message(nmea_sentence)

if result and result['type'] == 'position':
    position = result['data']
    print(f"Vessel {position.mmsi} at {position.latitude}, {position.longitude}")
```

### 2.2 区域监控

```python
# 监控上海港区域
vessels = processor.get_vessels_in_area(
    min_lat=30.5, max_lat=31.5,
    min_lon=121.0, max_lon=122.0
)

print(f"Vessels in Shanghai area: {len(vessels)}")
for vessel in vessels:
    print(f"  MMSI {vessel.mmsi}: {vessel.sog} knots, heading {vessel.heading}°")
```

### 2.3 历史轨迹查询

```python
# 获取船舶24小时轨迹
history = processor.get_vessel_history("563123456", hours=24)
print(f"Position reports (24h): {len(history)}")

for position in history:
    print(f"{position.timestamp}: {position.latitude}, {position.longitude}")
```

---

**创建时间**: 2025-01-21
**代码行数**: 600+行
