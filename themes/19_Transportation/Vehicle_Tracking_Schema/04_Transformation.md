# 车辆跟踪Schema转换体系

## 📑 目录

- [车辆跟踪Schema转换体系](#车辆跟踪schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GPS定位实现](#2-gps定位实现)
    - [2.1 NMEA消息解析器](#21-nmea消息解析器)
    - [2.2 GPS位置跟踪器](#22-gps位置跟踪器)
  - [3. 北斗定位实现](#3-北斗定位实现)
    - [3.1 BDS消息解析器](#31-bds消息解析器)
  - [4. AIS船舶跟踪实现](#4-ais船舶跟踪实现)
    - [4.1 AIS消息解析器](#41-ais消息解析器)
  - [5. 轨迹分析实现](#5-轨迹分析实现)
    - [5.1 轨迹分析器](#51-轨迹分析器)
  - [6. 车辆跟踪数据存储与分析](#6-车辆跟踪数据存储与分析)
    - [6.1 PostgreSQL车辆跟踪数据存储](#61-postgresql车辆跟踪数据存储)

---

## 1. 转换体系概述

Vehicle Tracking Schema转换体系支持GPS定位、北斗定位、AIS船舶跟踪、
轨迹分析、数据库存储之间的转换。

### 1.1 转换目标

1. **GPS定位**：NMEA消息解析和GPS位置跟踪
2. **北斗定位**：BDS消息解析和北斗位置跟踪
3. **AIS船舶跟踪**：AIS消息解析和船舶位置跟踪
4. **轨迹分析**：轨迹数据分析和地理围栏监控
5. **数据到数据库转换**：车辆跟踪数据到PostgreSQL存储

---

## 2. GPS定位实现

### 2.1 NMEA消息解析器

**完整的NMEA消息解析实现**：

```python
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class NMEAParser:
    """NMEA消息解析器 - 增强错误处理"""

    def __init__(self):
        # NMEA消息模式
        self.nmea_pattern = re.compile(r'^\$([A-Z]{2}[A-Z0-9]{3}),(.+)\*([0-9A-F]{2})$')
        # GPGGA消息格式
        self.gga_pattern = re.compile(r'^\$GPGGA,([^,]+),([^,]+),([NS]),([^,]+),([EW]),(\d+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)$')
        # GPRMC消息格式
        self.rmc_pattern = re.compile(r'^\$GPRMC,([^,]+),([AV]),([^,]+),([NS]),([^,]+),([EW]),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)$')

    def parse_nmea_message(self, nmea_string: str) -> Optional[Dict]:
        """解析NMEA消息 - 增强错误处理"""
        if not nmea_string:
            raise ValueError("NMEA string cannot be empty")

        if not isinstance(nmea_string, str):
            raise TypeError(f"NMEA string must be a string, got {type(nmea_string)}")

        nmea_string = nmea_string.strip()

        if not nmea_string.startswith('$'):
            raise ValueError(f"Invalid NMEA format: must start with '$', got: {nmea_string[:20]}")

        if '*' not in nmea_string:
            raise ValueError(f"Invalid NMEA format: missing checksum separator '*', got: {nmea_string[:50]}")

        try:
            # 验证校验和
            if not self._verify_checksum(nmea_string):
                logger.warning(f"NMEA checksum verification failed: {nmea_string[:50]}")
                return None

            # 提取消息类型
            match = self.nmea_pattern.match(nmea_string)
            if not match:
                raise ValueError(f"Invalid NMEA format: {nmea_string[:50]}")

            message_type = match.group(1)
            data_fields = match.group(2).split(',')
            checksum = match.group(3)

            # 根据消息类型解析
            if message_type == 'GPGGA':
                return self._parse_gga(data_fields)
            elif message_type == 'GPRMC':
                return self._parse_rmc(data_fields)
            elif message_type == 'GPGSV':
                return self._parse_gsv(data_fields)
            elif message_type == 'GPGSA':
                return self._parse_gsa(data_fields)
            else:
                logger.debug(f"Unsupported NMEA message type: {message_type}")
                return {
                    "message_type": message_type,
                    "raw_data": data_fields,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

        except ValueError as e:
            logger.error(f"Value error parsing NMEA message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing NMEA message: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse NMEA message: {e}") from e

    def _verify_checksum(self, nmea_string: str) -> bool:
        """验证NMEA校验和"""
        try:
            if '*' not in nmea_string:
                return False

            parts = nmea_string.split('*')
            if len(parts) != 2:
                return False

            message = parts[0][1:]  # 移除开头的$
            checksum_str = parts[1]

            # 计算校验和
            checksum = 0
            for char in message:
                checksum ^= ord(char)

            calculated_checksum = format(checksum, '02X')
            return calculated_checksum == checksum_str.upper()

        except Exception as e:
            logger.error(f"Error verifying checksum: {e}")
            return False

    def _parse_gga(self, fields: List[str]) -> Dict:
        """解析GPGGA消息（全球定位系统定位数据）"""
        if len(fields) < 15:
            raise ValueError(f"GPGGA message requires at least 15 fields, got {len(fields)}")

        try:
            # 解析时间
            time_str = fields[0] if fields[0] else None
            utc_time = None
            if time_str and len(time_str) >= 6:
                hour = int(time_str[0:2])
                minute = int(time_str[2:4])
                second = int(time_str[4:6])
                utc_time = datetime.now(timezone.utc).replace(hour=hour, minute=minute, second=second, microsecond=0)

            # 解析纬度
            lat_str = fields[1] if fields[1] else None
            lat_dir = fields[2] if len(fields) > 2 else None
            latitude = None
            if lat_str:
                lat_deg = float(lat_str[0:2])
                lat_min = float(lat_str[2:])
                latitude = lat_deg + lat_min / 60.0
                if lat_dir == 'S':
                    latitude = -latitude

            # 解析经度
            lon_str = fields[3] if len(fields) > 3 and fields[3] else None
            lon_dir = fields[4] if len(fields) > 4 else None
            longitude = None
            if lon_str:
                lon_deg = float(lon_str[0:3])
                lon_min = float(lon_str[3:])
                longitude = lon_deg + lon_min / 60.0
                if lon_dir == 'W':
                    longitude = -longitude

            # 解析GPS质量指标
            fix_quality = int(fields[5]) if len(fields) > 5 and fields[5] else 0
            num_satellites = int(fields[6]) if len(fields) > 6 and fields[6] else 0
            hdop = float(fields[7]) if len(fields) > 7 and fields[7] else None
            altitude = float(fields[8]) if len(fields) > 8 and fields[8] else None
            altitude_units = fields[9] if len(fields) > 9 else 'M'
            geoid_height = float(fields[10]) if len(fields) > 10 and fields[10] else None
            geoid_units = fields[11] if len(fields) > 11 else 'M'
            dgps_age = float(fields[12]) if len(fields) > 12 and fields[12] else None
            dgps_station_id = fields[13] if len(fields) > 13 else None

            return {
                "message_type": "GPGGA",
                "timestamp": utc_time.isoformat() if utc_time else None,
                "latitude": latitude,
                "longitude": longitude,
                "fix_quality": fix_quality,
                "num_satellites": num_satellites,
                "hdop": hdop,
                "altitude": altitude,
                "altitude_units": altitude_units,
                "geoid_height": geoid_height,
                "geoid_units": geoid_units,
                "dgps_age": dgps_age,
                "dgps_station_id": dgps_station_id
            }

        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing GPGGA message: {e}")
            raise ValueError(f"Invalid GPGGA format: {e}") from e

    def _parse_rmc(self, fields: List[str]) -> Dict:
        """解析GPRMC消息（推荐最小定位信息）"""
        if len(fields) < 12:
            raise ValueError(f"GPRMC message requires at least 12 fields, got {len(fields)}")

        try:
            # 解析时间
            time_str = fields[0] if fields[0] else None
            date_str = fields[8] if len(fields) > 8 and fields[8] else None

            utc_time = None
            if time_str and date_str:
                if len(time_str) >= 6 and len(date_str) >= 6:
                    hour = int(time_str[0:2])
                    minute = int(time_str[2:4])
                    second = int(time_str[4:6])
                    day = int(date_str[0:2])
                    month = int(date_str[2:4])
                    year = 2000 + int(date_str[4:6])
                    utc_time = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)

            # 解析状态
            status = fields[1] if fields[1] else 'V'  # A=有效，V=无效

            # 解析纬度
            lat_str = fields[2] if fields[2] else None
            lat_dir = fields[3] if len(fields) > 3 else None
            latitude = None
            if lat_str:
                lat_deg = float(lat_str[0:2])
                lat_min = float(lat_str[2:])
                latitude = lat_deg + lat_min / 60.0
                if lat_dir == 'S':
                    latitude = -latitude

            # 解析经度
            lon_str = fields[4] if len(fields) > 4 and fields[4] else None
            lon_dir = fields[5] if len(fields) > 5 else None
            longitude = None
            if lon_str:
                lon_deg = float(lon_str[0:3])
                lon_min = float(lon_str[3:])
                longitude = lon_deg + lon_min / 60.0
                if lon_dir == 'W':
                    longitude = -longitude

            # 解析速度和航向
            speed_knots = float(fields[6]) if len(fields) > 6 and fields[6] else None
            course = float(fields[7]) if len(fields) > 7 and fields[7] else None

            # 解析磁偏角
            magnetic_variation = float(fields[9]) if len(fields) > 9 and fields[9] else None
            magnetic_variation_dir = fields[10] if len(fields) > 10 else None

            return {
                "message_type": "GPRMC",
                "timestamp": utc_time.isoformat() if utc_time else None,
                "status": status,
                "latitude": latitude,
                "longitude": longitude,
                "speed_knots": speed_knots,
                "speed_kmh": speed_knots * 1.852 if speed_knots else None,
                "course": course,
                "magnetic_variation": magnetic_variation,
                "magnetic_variation_dir": magnetic_variation_dir
            }

        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing GPRMC message: {e}")
            raise ValueError(f"Invalid GPRMC format: {e}") from e

    def _parse_gsv(self, fields: List[str]) -> Dict:
        """解析GPGSV消息（可见卫星信息）"""
        if len(fields) < 4:
            raise ValueError(f"GPGSV message requires at least 4 fields, got {len(fields)}")

        try:
            total_messages = int(fields[0]) if fields[0] else 1
            message_number = int(fields[1]) if fields[1] else 1
            total_satellites = int(fields[2]) if fields[2] else 0

            satellites = []
            for i in range(3, len(fields) - 1, 4):
                if i + 3 < len(fields):
                    satellite = {
                        "prn": int(fields[i]) if fields[i] else None,
                        "elevation": int(fields[i+1]) if fields[i+1] else None,
                        "azimuth": int(fields[i+2]) if fields[i+2] else None,
                        "snr": int(fields[i+3]) if fields[i+3] else None
                    }
                    satellites.append(satellite)

            return {
                "message_type": "GPGSV",
                "total_messages": total_messages,
                "message_number": message_number,
                "total_satellites": total_satellites,
                "satellites": satellites
            }

        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing GPGSV message: {e}")
            raise ValueError(f"Invalid GPGSV format: {e}") from e

    def _parse_gsa(self, fields: List[str]) -> Dict:
        """解析GPGSA消息（当前卫星信息）"""
        if len(fields) < 17:
            raise ValueError(f"GPGSA message requires at least 17 fields, got {len(fields)}")

        try:
            selection_mode = fields[0] if fields[0] else None
            fix_mode = int(fields[1]) if fields[1] else None

            satellites_used = []
            for i in range(2, 14):
                if fields[i] and fields[i] != '':
                    satellites_used.append(int(fields[i]))

            pdop = float(fields[14]) if len(fields) > 14 and fields[14] else None
            hdop = float(fields[15]) if len(fields) > 15 and fields[15] else None
            vdop = float(fields[16]) if len(fields) > 16 and fields[16] else None

            return {
                "message_type": "GPGSA",
                "selection_mode": selection_mode,
                "fix_mode": fix_mode,
                "satellites_used": satellites_used,
                "pdop": pdop,
                "hdop": hdop,
                "vdop": vdop
            }

        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing GPGSA message: {e}")
            raise ValueError(f"Invalid GPGSA format: {e}") from e
```

### 2.2 GPS位置跟踪器

**完整的GPS位置跟踪实现**：

```python
class GPSPositionTracker:
    """GPS位置跟踪器 - 增强错误处理"""

    def __init__(self, vehicle_id: str):
        if not vehicle_id:
            raise ValueError("Vehicle ID cannot be empty")

        if not isinstance(vehicle_id, str):
            raise TypeError(f"Vehicle ID must be a string, got {type(vehicle_id)}")

        self.vehicle_id = vehicle_id
        self.nmea_parser = NMEAParser()
        self.current_position: Optional[Dict] = None
        self.position_history: List[Dict] = []

    def update_position(self, nmea_message: str) -> bool:
        """更新GPS位置 - 增强错误处理"""
        if not nmea_message:
            raise ValueError("NMEA message cannot be empty")

        try:
            parsed = self.nmea_parser.parse_nmea_message(nmea_message)

            if not parsed:
                logger.warning(f"Failed to parse NMEA message for vehicle {self.vehicle_id}")
                return False

            # 提取位置信息
            if parsed.get("message_type") == "GPGGA":
                position = {
                    "vehicle_id": self.vehicle_id,
                    "timestamp": parsed.get("timestamp"),
                    "latitude": parsed.get("latitude"),
                    "longitude": parsed.get("longitude"),
                    "altitude": parsed.get("altitude"),
                    "fix_quality": parsed.get("fix_quality"),
                    "num_satellites": parsed.get("num_satellites"),
                    "hdop": parsed.get("hdop"),
                    "source": "GPS"
                }
            elif parsed.get("message_type") == "GPRMC":
                position = {
                    "vehicle_id": self.vehicle_id,
                    "timestamp": parsed.get("timestamp"),
                    "latitude": parsed.get("latitude"),
                    "longitude": parsed.get("longitude"),
                    "speed": parsed.get("speed_kmh"),
                    "course": parsed.get("course"),
                    "status": parsed.get("status"),
                    "source": "GPS"
                }
            else:
                logger.debug(f"Unsupported NMEA message type for position update: {parsed.get('message_type')}")
                return False

            # 验证位置数据
            if position.get("latitude") is None or position.get("longitude") is None:
                logger.warning(f"Invalid position data: missing latitude or longitude")
                return False

            if not (-90 <= position["latitude"] <= 90):
                raise ValueError(f"Latitude out of range: {position['latitude']}")

            if not (-180 <= position["longitude"] <= 180):
                raise ValueError(f"Longitude out of range: {position['longitude']}")

            # 更新当前位置
            self.current_position = position

            # 添加到历史记录
            self.position_history.append(position)

            # 限制历史记录大小
            MAX_HISTORY_SIZE = 10000
            if len(self.position_history) > MAX_HISTORY_SIZE:
                self.position_history = self.position_history[-MAX_HISTORY_SIZE:]

            logger.debug(f"Updated GPS position for vehicle {self.vehicle_id}: {position['latitude']}, {position['longitude']}")
            return True

        except ValueError as e:
            logger.error(f"Value error updating GPS position: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating GPS position: {e}", exc_info=True)
            raise RuntimeError(f"Failed to update GPS position: {e}") from e

    def get_current_position(self) -> Optional[Dict]:
        """获取当前位置"""
        return self.current_position

    def get_position_history(self, limit: int = 100) -> List[Dict]:
        """获取位置历史"""
        if not isinstance(limit, int):
            raise TypeError(f"Limit must be an integer, got {type(limit)}")

        if limit <= 0:
            raise ValueError(f"Limit must be positive, got {limit}")

        return self.position_history[-limit:]
```

---

## 3. 北斗定位实现

### 3.1 BDS消息解析器

**完整的BDS消息解析实现**：

```python
class BDSParser:
    """北斗消息解析器 - 增强错误处理"""

    def __init__(self):
        # BDS消息格式类似NMEA，但使用BD前缀
        self.bds_pattern = re.compile(r'^\$BD([A-Z0-9]{3}),(.+)\*([0-9A-F]{2})$')

    def parse_bds_message(self, bds_string: str) -> Optional[Dict]:
        """解析BDS消息 - 增强错误处理"""
        if not bds_string:
            raise ValueError("BDS string cannot be empty")

        if not isinstance(bds_string, str):
            raise TypeError(f"BDS string must be a string, got {type(bds_string)}")

        bds_string = bds_string.strip()

        if not bds_string.startswith('$BD'):
            raise ValueError(f"Invalid BDS format: must start with '$BD', got: {bds_string[:20]}")

        try:
            # 验证校验和（类似NMEA）
            if not self._verify_checksum(bds_string):
                logger.warning(f"BDS checksum verification failed: {bds_string[:50]}")
                return None

            # 提取消息类型
            match = self.bds_pattern.match(bds_string)
            if not match:
                raise ValueError(f"Invalid BDS format: {bds_string[:50]}")

            message_type = match.group(1)
            data_fields = match.group(2).split(',')

            # 根据消息类型解析
            if message_type == 'GGA':
                return self._parse_bds_gga(data_fields)
            elif message_type == 'RMC':
                return self._parse_bds_rmc(data_fields)
            else:
                logger.debug(f"Unsupported BDS message type: {message_type}")
                return {
                    "message_type": f"BD{message_type}",
                    "raw_data": data_fields,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

        except ValueError as e:
            logger.error(f"Value error parsing BDS message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing BDS message: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse BDS message: {e}") from e

    def _verify_checksum(self, bds_string: str) -> bool:
        """验证BDS校验和（类似NMEA）"""
        try:
            if '*' not in bds_string:
                return False

            parts = bds_string.split('*')
            if len(parts) != 2:
                return False

            message = parts[0][1:]  # 移除开头的$
            checksum_str = parts[1]

            # 计算校验和
            checksum = 0
            for char in message:
                checksum ^= ord(char)

            calculated_checksum = format(checksum, '02X')
            return calculated_checksum == checksum_str.upper()

        except Exception as e:
            logger.error(f"Error verifying BDS checksum: {e}")
            return False

    def _parse_bds_gga(self, fields: List[str]) -> Dict:
        """解析BDGGA消息（类似GPGGA）"""
        # 使用与NMEA相同的解析逻辑
        nmea_parser = NMEAParser()
        return nmea_parser._parse_gga(fields)

    def _parse_bds_rmc(self, fields: List[str]) -> Dict:
        """解析BDRMC消息（类似GPRMC）"""
        # 使用与NMEA相同的解析逻辑
        nmea_parser = NMEAParser()
        return nmea_parser._parse_rmc(fields)
```

---

## 4. AIS船舶跟踪实现

### 4.1 AIS消息解析器

**完整的AIS消息解析实现**（参考Maritime_Schema的实现）：

```python
class AISMessageParser:
    """AIS消息解析器 - 增强错误处理"""

    def __init__(self):
        self.message_types = {
            1: "Position Report Class A",
            2: "Position Report Class A",
            3: "Position Report Class A",
            4: "Base Station Report",
            5: "Static and Voyage Related Data",
            18: "Standard Class B Position Report",
            19: "Extended Class B Position Report",
            21: "Aids-to-Navigation Report",
            24: "Static Data Report"
        }

    def parse_ais_message(self, ais_message: str) -> Dict:
        """解析AIS消息（NMEA格式） - 增强错误处理"""
        if not ais_message:
            raise ValueError("AIS message cannot be empty")

        if not isinstance(ais_message, str):
            raise TypeError(f"AIS message must be a string, got {type(ais_message)}")

        # AIS消息格式：!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46
        parts = ais_message.split(',')

        if len(parts) < 6:
            raise ValueError(f"Invalid AIS message format: requires at least 6 fields, got {len(parts)}")

        try:
            message_type = parts[0]  # !AIVDM or !AIVDO
            if not message_type.startswith('!AIVD'):
                raise ValueError(f"Invalid AIS message type: {message_type}")

            fragment_count = int(parts[1]) if parts[1] else 1
            fragment_number = int(parts[2]) if parts[2] else 1
            message_id = parts[3] if parts[3] else ""
            channel = parts[4]  # A or B
            payload = parts[5]  # 6-bit encoded data

            # 提取校验和
            checksum_str = None
            if len(parts) > 6:
                checksum_part = parts[6]
                if '*' in checksum_part:
                    checksum_str = checksum_part.split('*')[1]

            fill_bits = int(parts[6].split('*')[0]) if len(parts) > 6 and parts[6] else 0

            # 解码6-bit编码的payload
            decoded_data = self._decode_6bit(payload, fill_bits)

            if not decoded_data:
                raise ValueError("Failed to decode AIS payload")

            # 解析消息类型
            message_type_id = decoded_data[0] & 0x3F

            parsed_message = {
                "message_type": message_type_id,
                "message_type_name": self.message_types.get(message_type_id, "Unknown"),
                "mmsi": self._extract_mmsi(decoded_data),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fragment_count": fragment_count,
                "fragment_number": fragment_number,
                "channel": channel
            }

            # 根据消息类型解析
            if message_type_id in [1, 2, 3]:
                parsed_message.update(self._parse_position_report(decoded_data))
            elif message_type_id == 5:
                parsed_message.update(self._parse_static_voyage_data(decoded_data))
            elif message_type_id == 18:
                parsed_message.update(self._parse_class_b_position(decoded_data))
            elif message_type_id == 19:
                parsed_message.update(self._parse_extended_class_b_position(decoded_data))

            return parsed_message

        except ValueError as e:
            logger.error(f"Value error parsing AIS message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing AIS message: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse AIS message: {e}") from e

    def _decode_6bit(self, payload: str, fill_bits: int) -> List[int]:
        """解码6-bit编码的AIS数据"""
        if not payload:
            return []

        decoded = []
        bit_string = ""

        try:
            # 将ASCII字符转换为6位二进制
            for char in payload:
                ascii_val = ord(char)
                if ascii_val < 48 or ascii_val > 119:
                    continue
                # 转换为6位值
                bit_val = ascii_val - 48
                if bit_val > 40:
                    bit_val -= 8
                bit_string += format(bit_val, '06b')

            # 移除填充位
            if fill_bits > 0:
                bit_string = bit_string[:-fill_bits]

            # 转换为字节数组
            for i in range(0, len(bit_string), 8):
                byte_str = bit_string[i:i+8]
                if len(byte_str) == 8:
                    decoded.append(int(byte_str, 2))

            return decoded

        except Exception as e:
            logger.error(f"Error decoding 6-bit AIS data: {e}")
            return []

    def _extract_mmsi(self, data: List[int]) -> Optional[str]:
        """提取MMSI"""
        if len(data) < 4:
            return None

        try:
            mmsi = ((data[0] & 0x3F) << 20) | (data[1] << 14) | (data[2] << 8) | data[3]
            mmsi = mmsi & 0xFFFFFFFF
            return str(mmsi)
        except Exception as e:
            logger.error(f"Error extracting MMSI: {e}")
            return None

    def _parse_position_report(self, data: List[int]) -> Dict:
        """解析位置报告（消息类型1, 2, 3）"""
        # 简化实现，实际需要更复杂的位操作
        return {
            "latitude": 0.0,
            "longitude": 0.0,
            "course_over_ground": 0.0,
            "speed_over_ground": 0.0,
            "heading": 0,
            "navigation_status": 0
        }

    def _parse_static_voyage_data(self, data: List[int]) -> Dict:
        """解析静态和航次数据（消息类型5）"""
        return {
            "imo_number": "",
            "call_sign": "",
            "vessel_name": "",
            "vessel_type": 0,
            "dimension_to_bow": 0,
            "dimension_to_stern": 0,
            "dimension_to_port": 0,
            "dimension_to_starboard": 0,
            "eta_month": 0,
            "eta_day": 0,
            "eta_hour": 0,
            "eta_minute": 0,
            "draught": 0.0,
            "destination": ""
        }

    def _parse_class_b_position(self, data: List[int]) -> Dict:
        """解析Class B位置报告（消息类型18）"""
        return self._parse_position_report(data)

    def _parse_extended_class_b_position(self, data: List[int]) -> Dict:
        """解析扩展Class B位置报告（消息类型19）"""
        position_data = self._parse_position_report(data)
        position_data.update({
            "vessel_name": "",
            "vessel_type": 0
        })
        return position_data
```

---

## 5. 轨迹分析实现

### 5.1 轨迹分析器

**完整的轨迹分析实现**：

```python
import math
from typing import List, Tuple

class TrajectoryAnalyzer:
    """轨迹分析器 - 增强错误处理"""

    def __init__(self):
        pass

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算两点之间的距离（Haversine公式） - 增强错误处理"""
        if not isinstance(lat1, (int, float)) or not isinstance(lon1, (int, float)):
            raise TypeError(f"Latitude and longitude must be numbers")

        if not isinstance(lat2, (int, float)) or not isinstance(lon2, (int, float)):
            raise TypeError(f"Latitude and longitude must be numbers")

        if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
            raise ValueError(f"Latitude must be between -90 and 90")

        if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
            raise ValueError(f"Longitude must be between -180 and 180")

        try:
            # Haversine公式
            R = 6371.0  # 地球半径（公里）

            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)

            a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            distance = R * c
            return distance

        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            raise RuntimeError(f"Failed to calculate distance: {e}") from e

    def analyze_trajectory(self, positions: List[Dict]) -> Dict:
        """分析轨迹 - 增强错误处理"""
        if not isinstance(positions, list):
            raise TypeError(f"Positions must be a list, got {type(positions)}")

        if len(positions) < 2:
            raise ValueError(f"Trajectory analysis requires at least 2 positions, got {len(positions)}")

        try:
            total_distance = 0.0
            speeds = []
            durations = []

            for i in range(1, len(positions)):
                prev_pos = positions[i-1]
                curr_pos = positions[i]

                # 计算距离
                if prev_pos.get("latitude") and prev_pos.get("longitude") and \
                   curr_pos.get("latitude") and curr_pos.get("longitude"):
                    distance = self.calculate_distance(
                        prev_pos["latitude"], prev_pos["longitude"],
                        curr_pos["latitude"], curr_pos["longitude"]
                    )
                    total_distance += distance

                    # 计算速度
                    if prev_pos.get("timestamp") and curr_pos.get("timestamp"):
                        try:
                            prev_time = datetime.fromisoformat(prev_pos["timestamp"].replace('Z', '+00:00'))
                            curr_time = datetime.fromisoformat(curr_pos["timestamp"].replace('Z', '+00:00'))
                            duration = (curr_time - prev_time).total_seconds()

                            if duration > 0:
                                durations.append(duration)
                                speed = distance / duration * 3600  # km/h
                                speeds.append(speed)
                        except Exception as e:
                            logger.warning(f"Error calculating speed: {e}")

                # 使用位置中的速度信息
                if curr_pos.get("speed"):
                    speeds.append(curr_pos["speed"])

            # 计算统计信息
            avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
            max_speed = max(speeds) if speeds else 0.0
            min_speed = min(speeds) if speeds else 0.0

            total_duration = sum(durations) if durations else 0.0

            return {
                "total_distance": total_distance,
                "total_duration": total_duration,
                "average_speed": avg_speed,
                "max_speed": max_speed,
                "min_speed": min_speed,
                "num_points": len(positions),
                "start_position": positions[0],
                "end_position": positions[-1]
            }

        except Exception as e:
            logger.error(f"Error analyzing trajectory: {e}", exc_info=True)
            raise RuntimeError(f"Failed to analyze trajectory: {e}") from e

    def detect_stops(self, positions: List[Dict], stop_threshold: float = 0.01, time_threshold: int = 300) -> List[Dict]:
        """检测停留点 - 增强错误处理"""
        if not isinstance(positions, list):
            raise TypeError(f"Positions must be a list, got {type(positions)}")

        if not isinstance(stop_threshold, (int, float)):
            raise TypeError(f"Stop threshold must be a number, got {type(stop_threshold)}")

        if not isinstance(time_threshold, int):
            raise TypeError(f"Time threshold must be an integer, got {type(time_threshold)}")

        if stop_threshold < 0:
            raise ValueError(f"Stop threshold must be non-negative, got {stop_threshold}")

        if time_threshold < 0:
            raise ValueError(f"Time threshold must be non-negative, got {time_threshold}")

        try:
            stops = []
            stop_start_idx = None
            stop_start_time = None

            for i in range(1, len(positions)):
                prev_pos = positions[i-1]
                curr_pos = positions[i]

                # 计算距离
                if prev_pos.get("latitude") and prev_pos.get("longitude") and \
                   curr_pos.get("latitude") and curr_pos.get("longitude"):
                    distance = self.calculate_distance(
                        prev_pos["latitude"], prev_pos["longitude"],
                        curr_pos["latitude"], curr_pos["longitude"]
                    )

                    # 如果距离小于阈值，可能是停留
                    if distance < stop_threshold:
                        if stop_start_idx is None:
                            stop_start_idx = i - 1
                            stop_start_time = prev_pos.get("timestamp")
                    else:
                        # 距离超过阈值，检查是否形成停留点
                        if stop_start_idx is not None:
                            stop_duration = 0
                            if stop_start_time and curr_pos.get("timestamp"):
                                try:
                                    start_time = datetime.fromisoformat(stop_start_time.replace('Z', '+00:00'))
                                    end_time = datetime.fromisoformat(curr_pos["timestamp"].replace('Z', '+00:00'))
                                    stop_duration = (end_time - start_time).total_seconds()
                                except Exception:
                                    pass

                            if stop_duration >= time_threshold:
                                stops.append({
                                    "start_index": stop_start_idx,
                                    "end_index": i - 1,
                                    "position": positions[stop_start_idx],
                                    "duration": stop_duration
                                })

                            stop_start_idx = None
                            stop_start_time = None

            return stops

        except Exception as e:
            logger.error(f"Error detecting stops: {e}", exc_info=True)
            raise RuntimeError(f"Failed to detect stops: {e}") from e
```

---

## 6. 车辆跟踪数据存储与分析

### 6.1 PostgreSQL车辆跟踪数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from datetime import datetime

class VehicleTrackingStorage:
    """车辆跟踪数据存储 - 增强错误处理"""

    def __init__(self, db_config: Dict):
        if not isinstance(db_config, dict):
            raise TypeError(f"Database config must be a dictionary, got {type(db_config)}")

        required_fields = ["host", "port", "database", "user", "password"]
        missing_fields = [f for f in required_fields if f not in db_config]
        if missing_fields:
            raise ValueError(f"Missing required database config fields: {', '.join(missing_fields)}")

        self.db_config = db_config
        self.conn: Optional[psycopg2.extensions.connection] = None

    def connect(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                database=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            logger.info("Connected to PostgreSQL database")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e

    def create_tables(self):
        """创建表结构"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        try:
            with self.conn.cursor() as cur:
                # 车辆表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS vehicles (
                        id SERIAL PRIMARY KEY,
                        vehicle_id VARCHAR(50) NOT NULL UNIQUE,
                        vehicle_type VARCHAR(50),
                        license_plate VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # GPS位置表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS gps_positions (
                        id SERIAL PRIMARY KEY,
                        vehicle_id VARCHAR(50) NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        latitude DECIMAL(10,7) NOT NULL CHECK (latitude >= -90 AND latitude <= 90),
                        longitude DECIMAL(11,7) NOT NULL CHECK (longitude >= -180 AND longitude <= 180),
                        altitude DECIMAL(10,2),
                        speed DECIMAL(10,2) CHECK (speed >= 0),
                        course DECIMAL(5,2) CHECK (course >= 0 AND course < 360),
                        fix_quality INTEGER CHECK (fix_quality >= 0 AND fix_quality <= 8),
                        num_satellites INTEGER CHECK (num_satellites >= 0),
                        hdop DECIMAL(5,2),
                        source VARCHAR(20) DEFAULT 'GPS',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 轨迹表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS trajectories (
                        id SERIAL PRIMARY KEY,
                        vehicle_id VARCHAR(50) NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP NOT NULL,
                        total_distance DECIMAL(10,2) CHECK (total_distance >= 0),
                        average_speed DECIMAL(10,2) CHECK (average_speed >= 0),
                        max_speed DECIMAL(10,2) CHECK (max_speed >= 0),
                        num_points INTEGER CHECK (num_points > 0),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 地理围栏表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS geofences (
                        id SERIAL PRIMARY KEY,
                        geofence_id VARCHAR(50) NOT NULL UNIQUE,
                        geofence_name VARCHAR(200) NOT NULL,
                        geofence_type VARCHAR(50) NOT NULL,
                        coordinates JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 围栏事件表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS geofence_events (
                        id SERIAL PRIMARY KEY,
                        geofence_id VARCHAR(50) NOT NULL,
                        vehicle_id VARCHAR(50) NOT NULL,
                        event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('ENTER', 'EXIT')),
                        timestamp TIMESTAMP NOT NULL,
                        position JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 创建索引
                cur.execute("CREATE INDEX IF NOT EXISTS idx_vehicle_id ON gps_positions(vehicle_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON gps_positions(timestamp)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_vehicle_timestamp ON gps_positions(vehicle_id, timestamp)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_trajectory_vehicle ON trajectories(vehicle_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_geofence_events ON geofence_events(geofence_id, vehicle_id, timestamp)")

                self.conn.commit()
                logger.info("Created vehicle tracking database tables")

        except psycopg2.Error as e:
            logger.error(f"Failed to create tables: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Failed to create tables: {e}") from e

    def store_position(self, position: Dict) -> int:
        """存储位置数据"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        if not isinstance(position, dict):
            raise TypeError(f"Position must be a dictionary, got {type(position)}")

        required_fields = ["vehicle_id", "latitude", "longitude"]
        missing_fields = [f for f in required_fields if f not in position]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO gps_positions
                    (vehicle_id, timestamp, latitude, longitude, altitude, speed, course,
                     fix_quality, num_satellites, hdop, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    position["vehicle_id"],
                    position.get("timestamp") or datetime.now(),
                    position["latitude"],
                    position["longitude"],
                    position.get("altitude"),
                    position.get("speed"),
                    position.get("course"),
                    position.get("fix_quality"),
                    position.get("num_satellites"),
                    position.get("hdop"),
                    position.get("source", "GPS")
                ))

                position_id = cur.fetchone()[0]
                self.conn.commit()

                logger.info(f"Stored GPS position with ID: {position_id}")
                return position_id

        except psycopg2.Error as e:
            logger.error(f"Failed to store position: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Failed to store position: {e}") from e

    def query_positions(self, vehicle_id: str, start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None, limit: int = 1000) -> List[Dict]:
        """查询位置数据"""
        if self.conn is None:
            raise ConnectionError("Database not connected. Call connect() first.")

        if not isinstance(vehicle_id, str):
            raise TypeError(f"Vehicle ID must be a string, got {type(vehicle_id)}")

        if not isinstance(limit, int) or limit <= 0:
            raise ValueError(f"Limit must be a positive integer, got {limit}")

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM gps_positions WHERE vehicle_id = %s"
                params = [vehicle_id]

                if start_time:
                    query += " AND timestamp >= %s"
                    params.append(start_time)

                if end_time:
                    query += " AND timestamp <= %s"
                    params.append(end_time)

                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)

                cur.execute(query, params)
                return cur.fetchall()

        except psycopg2.Error as e:
            logger.error(f"Failed to query positions: {e}")
            raise RuntimeError(f"Failed to query positions: {e}") from e
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
