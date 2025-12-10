"""
AIS数据处理器

专注于AIS消息解析、位置追踪、轨迹分析
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import struct

from .logger import logger
from .exceptions import ParseError, ValidationError


class AISMessageType(IntEnum):
    """AIS消息类型"""
    TYPE_1 = 1  # 位置报告（A类）
    TYPE_2 = 2  # 位置报告（A类）
    TYPE_3 = 3  # 位置报告（A类）
    TYPE_4 = 4  # 基站报告
    TYPE_5 = 5  # 静态和航程相关数据（A类）
    TYPE_6 = 6  # 二进制寻址消息
    TYPE_7 = 7  # 二进制确认消息
    TYPE_8 = 8  # 二进制广播消息
    TYPE_9 = 9  # 标准SAR飞机位置报告
    TYPE_10 = 10  # UTC和日期查询
    TYPE_11 = 11  # UTC和日期响应
    TYPE_12 = 12  # 寻址安全相关消息
    TYPE_13 = 13  # 安全相关确认
    TYPE_14 = 14  # 安全相关广播消息
    TYPE_15 = 15  # 询问
    TYPE_16 = 16  # 分配模式命令
    TYPE_17 = 17  # DGNSS广播二进制消息
    TYPE_18 = 18  # 标准B类位置报告
    TYPE_19 = 19  # 扩展B类位置报告
    TYPE_20 = 20  # 数据链路管理消息
    TYPE_21 = 21  # 辅助定位报告
    TYPE_22 = 22  # 信道管理
    TYPE_23 = 23  # 组分配命令
    TYPE_24 = 24  # 静态数据报告


@dataclass
class AISPosition:
    """AIS位置"""
    mmsi: str
    latitude: float
    longitude: float
    timestamp: datetime
    speed: Optional[float] = None
    course: Optional[float] = None
    heading: Optional[float] = None
    navigation_status: Optional[int] = None


@dataclass
class AISMessage:
    """AIS消息"""
    message_id: str
    message_type: AISMessageType
    mmsi: str
    timestamp: datetime
    position: Optional[AISPosition] = None
    static_data: Optional[Dict[str, Any]] = None
    voyage_data: Optional[Dict[str, Any]] = None
    raw_data: str = None


class AISProcessor:
    """
    AIS数据处理器
    
    专注于AIS消息解析、位置追踪、轨迹分析
    """
    
    def __init__(self):
        self.messages: Dict[str, AISMessage] = {}
        self.positions: Dict[str, List[AISPosition]] = {}  # MMSI到位置列表的映射
        logger.info("AISProcessor initialized")
    
    def parse_nmea(self, nmea_sentence: str) -> AISMessage:
        """
        解析NMEA格式AIS消息
        
        Args:
            nmea_sentence: NMEA格式句子（如：!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46）
            
        Returns:
            AIS消息对象
        """
        parts = nmea_sentence.split(',')
        
        if len(parts) < 6:
            raise ValueError("无效的NMEA格式")
        
        # 解析消息类型和MMSI（简化实现）
        payload = parts[5]
        
        # 解码6位ASCII到二进制
        binary_payload = self._decode_6bit_ascii(payload)
        
        # 解析消息类型（前6位）
        message_type = self._parse_message_type(binary_payload)
        
        # 解析MMSI（位置8-37，30位）
        mmsi = self._parse_mmsi(binary_payload)
        
        # 解析位置（根据消息类型）
        position = None
        if message_type in [AISMessageType.TYPE_1, AISMessageType.TYPE_2, AISMessageType.TYPE_3,
                           AISMessageType.TYPE_18, AISMessageType.TYPE_19]:
            position = self._parse_position(binary_payload, message_type)
        
        message_id = f"ais_{datetime.utcnow().timestamp()}"
        message = AISMessage(
            message_id=message_id,
            message_type=message_type,
            mmsi=mmsi,
            timestamp=datetime.utcnow(),
            position=position,
            raw_data=nmea_sentence
        )
        
        self.messages[message_id] = message
        
        # 更新位置历史
        if position:
            if mmsi not in self.positions:
                self.positions[mmsi] = []
            self.positions[mmsi].append(position)
        
        return message
    
    def _decode_6bit_ascii(self, payload: str) -> str:
        """解码6位ASCII到二进制字符串"""
        binary = ""
        for char in payload:
            # 6位ASCII字符范围：0-63
            # 映射：0-9 -> 48-57, : -> 58, ; -> 59, < -> 60, = -> 61, > -> 62, ? -> 63
            # A-W -> 64-87, 但实际编码是：0-9, :, ;, <, =, >, ?, @, A-W
            ascii_val = ord(char)
            
            # 转换为6位值
            if 48 <= ascii_val <= 57:  # 0-9
                value = ascii_val - 48
            elif ascii_val == 58:  # :
                value = 10
            elif ascii_val == 59:  # ;
                value = 11
            elif ascii_val == 60:  # <
                value = 12
            elif ascii_val == 61:  # =
                value = 13
            elif ascii_val == 62:  # >
                value = 14
            elif ascii_val == 63:  # ?
                value = 15
            elif 64 <= ascii_val <= 87:  # @, A-W
                value = ascii_val - 64 + 16
            else:
                value = 0
            
            # 转换为6位二进制
            binary += format(value, '06b')
        
        return binary
    
    def _parse_message_type(self, binary_payload: str) -> AISMessageType:
        """解析消息类型（前6位）"""
        if len(binary_payload) < 6:
            return AISMessageType.TYPE_1
        
        message_type_bits = binary_payload[:6]
        message_type = int(message_type_bits, 2)
        
        try:
            return AISMessageType(message_type)
        except:
            return AISMessageType.TYPE_1
    
    def _parse_mmsi(self, binary_payload: str) -> str:
        """解析MMSI（位置8-37，30位）"""
        if len(binary_payload) < 38:
            return "000000000"
        
        mmsi_bits = binary_payload[8:38]
        mmsi = int(mmsi_bits, 2)
        
        return str(mmsi).zfill(9)
    
    def _parse_position(self, binary_payload: str, message_type: AISMessageType) -> Optional[AISPosition]:
        """解析位置信息"""
        if len(binary_payload) < 168:  # 位置报告消息至少需要168位
            return None
        
        # 解析纬度（位置89-115，27位）
        latitude_bits = binary_payload[89:116]
        latitude_raw = int(latitude_bits, 2)
        latitude = latitude_raw / 600000.0  # 转换为度
        
        # 解析经度（位置61-88，28位）
        longitude_bits = binary_payload[61:89]
        longitude_raw = int(longitude_bits, 2)
        longitude = longitude_raw / 600000.0  # 转换为度
        
        # 解析速度（位置50-59，10位）
        speed_bits = binary_payload[50:60]
        speed_raw = int(speed_bits, 2)
        speed = speed_raw / 10.0 if speed_raw < 1023 else None  # 1023表示不可用
        
        # 解析航向（位置128-137，10位）
        course_bits = binary_payload[128:138]
        course_raw = int(course_bits, 2)
        course = course_raw / 10.0 if course_raw < 3600 else None
        
        # 解析船首向（位置128-137，10位，某些消息类型）
        heading_bits = binary_payload[128:138] if message_type in [AISMessageType.TYPE_1, AISMessageType.TYPE_2, AISMessageType.TYPE_3] else None
        heading = int(heading_bits, 2) if heading_bits and len(heading_bits) >= 9 else None
        
        # 解析导航状态（位置38-41，4位）
        nav_status_bits = binary_payload[38:42]
        navigation_status = int(nav_status_bits, 2) if nav_status_bits else None
        
        return AISPosition(
            mmsi=self._parse_mmsi(binary_payload),
            latitude=latitude,
            longitude=longitude,
            timestamp=datetime.utcnow(),
            speed=speed,
            course=course,
            heading=heading,
            navigation_status=navigation_status
        )
    
    def get_vessel_trajectory(self, mmsi: str, start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None) -> List[AISPosition]:
        """
        获取船舶轨迹
        
        Args:
            mmsi: 海上移动服务标识
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            位置列表
        """
        if mmsi not in self.positions:
            return []
        
        positions = self.positions[mmsi]
        
        # 时间过滤
        if start_time:
            positions = [p for p in positions if p.timestamp >= start_time]
        
        if end_time:
            positions = [p for p in positions if p.timestamp <= end_time]
        
        # 按时间排序
        positions.sort(key=lambda p: p.timestamp)
        
        return positions
    
    def calculate_distance(self, pos1: AISPosition, pos2: AISPosition) -> float:
        """
        计算两点间距离（海里）
        
        Args:
            pos1: 位置1
            pos2: 位置2
            
        Returns:
            距离（海里）
        """
        import math
        
        # 使用Haversine公式
        lat1_rad = math.radians(pos1.latitude)
        lat2_rad = math.radians(pos2.latitude)
        delta_lat = math.radians(pos2.latitude - pos1.latitude)
        delta_lon = math.radians(pos2.longitude - pos1.longitude)
        
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # 地球半径（海里）
        R = 3440.065  # 海里
        
        distance = R * c
        return distance


def main():
    """主函数 - 示例用法"""
    processor = AISProcessor()
    
    # 解析AIS消息
    nmea_sentence = "!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46"
    
    message = processor.parse_nmea(nmea_sentence)
    print(f"AIS消息: MMSI={message.mmsi}, 类型={message.message_type.value}")
    
    if message.position:
        print(f"位置: 纬度={message.position.latitude}, 经度={message.position.longitude}")


if __name__ == '__main__':
    main()
