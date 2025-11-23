# 可再生能源Schema转换体系

## 📑 目录

- [可再生能源Schema转换体系](#可再生能源schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 风电数据采集和转换](#2-风电数据采集和转换)
    - [2.1 风电数据采集器](#21-风电数据采集器)
    - [2.2 风电数据转换器](#22-风电数据转换器)
  - [3. 光伏数据采集和转换](#3-光伏数据采集和转换)
    - [3.1 光伏数据采集器](#31-光伏数据采集器)
    - [3.2 光伏数据转换器](#32-光伏数据转换器)
  - [4. 储能数据采集和转换](#4-储能数据采集和转换)
    - [4.1 储能数据采集器](#41-储能数据采集器)
  - [5. 可再生能源数据存储与分析](#5-可再生能源数据存储与分析)
    - [5.1 PostgreSQL可再生能源数据存储](#51-postgresql可再生能源数据存储)
    - [5.2 可再生能源数据分析查询](#52-可再生能源数据分析查询)

---

## 1. 转换体系概述

可再生能源Schema转换体系支持设备数据采集、
监控系统集成、数据库存储之间的转换。

### 1.1 转换目标

1. **设备数据采集**：从风电、光伏、储能设备采集数据
2. **数据格式转换**：设备数据格式到标准Schema格式
3. **监控系统集成**：与IEC 61850监控系统集成
4. **数据到数据库转换**：可再生能源数据到PostgreSQL存储

---

## 2. 风电数据采集和转换

### 2.1 风电数据采集器

**完整的风电数据采集实现**：

```python
import logging
import socket
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WindTurbineDataCollector:
    """风力发电机组数据采集器"""

    def __init__(self, turbine_id: str, host: str, port: int = 502):
        self.turbine_id = turbine_id
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False

    def connect(self, timeout: float = 10.0) -> bool:
        """连接到风机控制器 - 增强错误处理"""
        # 输入验证
        if not self.turbine_id:
            raise ValueError("Turbine ID cannot be empty")

        if not isinstance(self.turbine_id, str):
            raise TypeError(f"Turbine ID must be a string, got {type(self.turbine_id)}")

        if not self.host:
            raise ValueError("Host cannot be empty")

        if not isinstance(self.host, str):
            raise TypeError(f"Host must be a string, got {type(self.host)}")

        if not isinstance(self.port, int):
            raise TypeError(f"Port must be an integer, got {type(self.port)}")

        if not (1 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {self.port}")

        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")

        # 如果已连接，先断开
        if self.connected and self.socket:
            try:
                self.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting existing connection: {e}")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)

            # 尝试连接
            self.socket.connect((self.host, self.port))
            self.connected = True

            logger.info(f"Connected to wind turbine {self.turbine_id} at {self.host}:{self.port}")
            return True

        except socket.timeout:
            logger.error(f"Connection timeout to wind turbine {self.turbine_id} at {self.host}:{self.port} (timeout: {timeout}s)")
            self._cleanup_socket()
            raise TimeoutError(f"Connection timeout to wind turbine {self.turbine_id}") from None
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for wind turbine {self.turbine_id} host {self.host}: {e}")
            self._cleanup_socket()
            raise ConnectionError(f"Cannot resolve hostname {self.host}: {e}") from e
        except socket.error as e:
            logger.error(f"Socket error connecting to wind turbine {self.turbine_id} at {self.host}:{self.port}: {e}")
            self._cleanup_socket()
            raise ConnectionError(f"Cannot connect to wind turbine {self.turbine_id}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error connecting to wind turbine {self.turbine_id}: {e}", exc_info=True)
            self._cleanup_socket()
            raise RuntimeError(f"Failed to connect to wind turbine {self.turbine_id}: {e}") from e

    def _cleanup_socket(self):
        """清理socket资源"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.socket = None
                self.connected = False

    def disconnect(self):
        """断开连接 - 增强错误处理"""
        if self.socket:
            try:
                self.socket.close()
                logger.info(f"Disconnected from wind turbine {self.turbine_id}")
            except Exception as e:
                logger.warning(f"Error closing socket: {e}")
            finally:
                self.socket = None
                self.connected = False

    def read_turbine_status(self) -> Optional[Dict]:
        """读取风机状态 - 增强错误处理"""
        # 连接状态检查
        if not self.connected:
            raise ConnectionError(f"Not connected to wind turbine {self.turbine_id}. Call connect() first.")

        if self.socket is None:
            raise ConnectionError("Socket is not initialized")

        try:
            # Modbus读取状态寄存器（简化实现）
            status_data = self._read_modbus_registers(0x1000, 10)
            if not status_data:
                logger.warning(f"No status data received from wind turbine {self.turbine_id}")
                return None

            if len(status_data) < 3:
                raise ValueError(f"Insufficient status data: expected at least 3 registers, got {len(status_data)}")

            return {
                "turbine_id": self.turbine_id,
                "timestamp": datetime.now().isoformat(),
                "operational_status": self._parse_operational_status(status_data[0]),
                "fault_status": self._parse_fault_status(status_data[1]),
                "maintenance_status": self._parse_maintenance_status(status_data[2])
            }

        except socket.timeout:
            logger.error(f"Timeout reading status from wind turbine {self.turbine_id}")
            raise TimeoutError(f"Timeout reading status from wind turbine {self.turbine_id}") from None
        except socket.error as e:
            logger.error(f"Socket error reading status from wind turbine {self.turbine_id}: {e}")
            self.connected = False
            raise ConnectionError(f"Socket error: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid status data from wind turbine {self.turbine_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading status from wind turbine {self.turbine_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to read turbine status: {e}") from e

    def read_turbine_performance(self) -> Optional[Dict]:
        """读取风机性能数据"""
        if not self.connected:
            return None

        # Modbus读取性能寄存器
        perf_data = self._read_modbus_registers(0x2000, 20)
        if perf_data:
            return {
                "current_power": self._parse_float(perf_data[0:2]) / 1000.0,  # kW
                "wind_speed": self._parse_float(perf_data[2:4]),  # m/s
                "rotor_speed": self._parse_float(perf_data[4:6]),  # rpm
                "generator_speed": self._parse_float(perf_data[6:8]),  # rpm
                "temperature": self._parse_float(perf_data[8:10]) / 10.0,  # °C
                "vibration": self._parse_float(perf_data[10:12]) / 100.0,  # mm/s
                "power_factor": self._parse_float(perf_data[12:14]) / 1000.0,
                "efficiency": self._parse_float(perf_data[14:16]) / 100.0  # %
            }
        return None

    def read_turbine_control(self) -> Optional[Dict]:
        """读取风机控制数据"""
        if not self.connected:
            return None

        # Modbus读取控制寄存器
        ctrl_data = self._read_modbus_registers(0x3000, 10)
        if ctrl_data:
            return {
                "pitch_angle": self._parse_float(ctrl_data[0:2]),  # degrees
                "yaw_angle": self._parse_float(ctrl_data[2:4]),  # degrees
                "converter_status": self._parse_converter_status(ctrl_data[4]),
                "brake_status": self._parse_brake_status(ctrl_data[5])
            }
        return None

    def _read_modbus_registers(self, start_address: int, count: int) -> Optional[List[int]]:
        """读取Modbus寄存器（简化实现）"""
        # 实际实现需要使用pymodbus库
        return None

    def _parse_float(self, data: List[int]) -> float:
        """解析浮点数"""
        # 实际实现需要根据数据格式解析
        return 0.0

    def _parse_operational_status(self, value: int) -> str:
        """解析运行状态"""
        status_map = {0: "Stopped", 1: "Running", 2: "Maintenance", 3: "Fault"}
        return status_map.get(value, "Unknown")

    def _parse_fault_status(self, value: int) -> str:
        """解析故障状态"""
        if value == 0:
            return "None"
        elif value < 10:
            return "Minor"
        elif value < 50:
            return "Major"
        else:
            return "Critical"

    def _parse_maintenance_status(self, value: int) -> str:
        """解析维护状态"""
        status_map = {0: "None", 1: "Scheduled", 2: "InProgress", 3: "Completed"}
        return status_map.get(value, "Unknown")

    def _parse_converter_status(self, value: int) -> str:
        """解析变流器状态"""
        status_map = {0: "Standby", 1: "Active", 2: "Fault"}
        return status_map.get(value, "Unknown")

    def _parse_brake_status(self, value: int) -> str:
        """解析制动状态"""
        return "Applied" if value == 1 else "Released"
```

### 2.2 风电数据转换器

**风电数据转换器实现**：

```python
class WindTurbineDataConverter:
    """风电数据转换器"""

    def __init__(self):
        pass

    def convert_to_schema(self, turbine_id: str, collector_data: Dict) -> Dict:
        """转换为标准Schema格式"""
        return {
            "turbine_id": turbine_id,
            "turbine_status": collector_data.get("status", {}),
            "turbine_performance": collector_data.get("performance", {}),
            "turbine_control": collector_data.get("control", {}),
            "timestamp": datetime.now().isoformat()
        }

    def convert_to_iec61850(self, schema_data: Dict) -> Dict:
        """转换为IEC 61850格式"""
        return {
            "logical_node": "WTUR1",
            "data_objects": {
                "OpSt": {
                    "stVal": schema_data["turbine_status"]["operational_status"]
                },
                "W": {
                    "mag": {
                        "f": schema_data["turbine_performance"]["current_power"]
                    }
                },
                "Spd": {
                    "mag": {
                        "f": schema_data["turbine_performance"]["rotor_speed"]
                    }
                }
            }
        }
```

---

## 3. 光伏数据采集和转换

### 3.1 光伏数据采集器

**完整的光伏数据采集实现**：

```python
class SolarSystemDataCollector:
    """光伏系统数据采集器"""

    def __init__(self, system_id: str, inverter_hosts: List[str]):
        self.system_id = system_id
        self.inverter_hosts = inverter_hosts
        self.inverters: Dict[str, socket.socket] = {}

    def connect_all(self) -> bool:
        """连接所有逆变器"""
        for host in self.inverter_hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, 502))
                self.inverters[host] = sock
                logger.info(f"Connected to inverter at {host}")
            except Exception as e:
                logger.error(f"Failed to connect to inverter {host}: {e}")

        return len(self.inverters) > 0

    def read_generation_data(self) -> Optional[Dict]:
        """读取发电数据"""
        total_dc_power = 0.0
        total_ac_power = 0.0

        for host, sock in self.inverters.items():
            inv_data = self._read_inverter_data(sock)
            if inv_data:
                total_dc_power += inv_data.get("dc_power", 0)
                total_ac_power += inv_data.get("ac_power", 0)

        return {
            "dc_power": total_dc_power,
            "ac_power": total_ac_power,
            "system_efficiency": (total_ac_power / total_dc_power * 100) if total_dc_power > 0 else 0
        }

    def read_environmental_data(self) -> Optional[Dict]:
        """读取环境数据"""
        # 从气象站读取环境数据
        return {
            "irradiance": 800.0,  # W/m²
            "ambient_temperature": 25.0,  # °C
            "module_temperature": 45.0,  # °C
            "wind_speed": 3.5,  # m/s
            "humidity": 60.0  # %
        }

    def _read_inverter_data(self, sock: socket.socket) -> Optional[Dict]:
        """读取逆变器数据"""
        # Modbus读取逆变器寄存器
        return {
            "dc_power": 100.0,
            "ac_power": 95.0,
            "efficiency": 95.0
        }
```

### 3.2 光伏数据转换器

**光伏数据转换器实现**：

```python
class SolarSystemDataConverter:
    """光伏数据转换器"""

    def convert_to_schema(self, system_id: str, collector_data: Dict) -> Dict:
        """转换为标准Schema格式"""
        return {
            "system_id": system_id,
            "generation_data": collector_data.get("generation", {}),
            "environmental_data": collector_data.get("environmental", {}),
            "timestamp": datetime.now().isoformat()
        }
```

---

## 4. 储能数据采集和转换

### 4.1 储能数据采集器

**完整的储能数据采集实现**：

```python
class EnergyStorageDataCollector:
    """储能系统数据采集器"""

    def __init__(self, storage_id: str, bms_host: str, port: int = 502):
        self.storage_id = storage_id
        self.bms_host = bms_host
        self.port = port
        self.socket: Optional[socket.socket] = None

    def connect(self) -> bool:
        """连接到BMS"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.bms_host, self.port))
            logger.info(f"Connected to BMS for {self.storage_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to BMS: {e}")
            return False

    def read_battery_status(self) -> Optional[Dict]:
        """读取电池状态"""
        if not self.socket:
            return None

        # Modbus读取电池状态寄存器
        status_data = self._read_modbus_registers(0x4000, 20)
        if status_data:
            return {
                "soc": status_data[0] / 100.0,  # %
                "soh": status_data[1] / 100.0,  # %
                "voltage": status_data[2] / 100.0,  # V
                "current": status_data[3] / 100.0,  # A
                "temperature": status_data[4] / 10.0,  # °C
                "health_status": self._parse_health_status(status_data[5])
            }
        return None

    def read_charge_discharge_data(self) -> Optional[Dict]:
        """读取充放电数据"""
        if not self.socket:
            return None

        # Modbus读取充放电寄存器
        cd_data = self._read_modbus_registers(0x5000, 20)
        if cd_data:
            return {
                "charge_power": cd_data[0] / 1000.0,  # kW
                "discharge_power": cd_data[1] / 1000.0,  # kW
                "charge_energy": cd_data[2] / 100.0,  # kWh
                "discharge_energy": cd_data[3] / 100.0,  # kWh
                "cycle_count": cd_data[4]
            }
        return None

    def read_bms_data(self) -> Optional[Dict]:
        """读取BMS数据"""
        if not self.socket:
            return None

        # Modbus读取BMS寄存器
        bms_data = self._read_modbus_registers(0x6000, 30)
        if bms_data:
            return {
                "bms_status": self._parse_bms_status(bms_data[0]),
                "protection_status": self._parse_protection_status(bms_data[1]),
                "balancing_status": self._parse_balancing_status(bms_data[2]),
                "cell_voltages": [bms_data[i] / 1000.0 for i in range(3, 19)],
                "cell_temperatures": [bms_data[i] / 10.0 for i in range(19, 35)]
            }
        return None

    def _read_modbus_registers(self, start_address: int, count: int) -> Optional[List[int]]:
        """读取Modbus寄存器"""
        return None

    def _parse_health_status(self, value: int) -> str:
        """解析健康状态"""
        if value >= 80:
            return "Good"
        elif value >= 60:
            return "Fair"
        elif value >= 40:
            return "Poor"
        else:
            return "Critical"

    def _parse_bms_status(self, value: int) -> str:
        """解析BMS状态"""
        status_map = {0: "Standby", 1: "Active", 2: "Fault"}
        return status_map.get(value, "Unknown")

    def _parse_protection_status(self, value: int) -> str:
        """解析保护状态"""
        if value == 0:
            return "Normal"
        elif value & 0x01:
            return "OverVoltage"
        elif value & 0x02:
            return "UnderVoltage"
        elif value & 0x04:
            return "OverCurrent"
        elif value & 0x08:
            return "OverTemperature"
        elif value & 0x10:
            return "UnderTemperature"
        return "Normal"

    def _parse_balancing_status(self, value: int) -> str:
        """解析均衡状态"""
        status_map = {0: "Balanced", 1: "Balancing", 2: "Fault"}
        return status_map.get(value, "Unknown")
```

---

## 5. 可再生能源数据存储与分析

### 5.1 PostgreSQL可再生能源数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class RenewableEnergyStorage:
    """可再生能源数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建可再生能源数据表"""
        # 风力发电机组表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS wind_turbines (
                id BIGSERIAL PRIMARY KEY,
                turbine_id VARCHAR(20) UNIQUE NOT NULL,
                turbine_name VARCHAR(200) NOT NULL,
                turbine_model VARCHAR(100),
                manufacturer VARCHAR(200),
                rated_power DECIMAL(10,2),
                rotor_diameter DECIMAL(8,2),
                hub_height DECIMAL(8,2),
                installation_date DATE,
                latitude DECIMAL(8,6),
                longitude DECIMAL(9,6),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 风机状态表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS wind_turbine_status (
                id BIGSERIAL PRIMARY KEY,
                turbine_id VARCHAR(20) NOT NULL,
                operational_status VARCHAR(20) NOT NULL,
                fault_status VARCHAR(20),
                maintenance_status VARCHAR(20),
                status_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turbine_id) REFERENCES wind_turbines(turbine_id)
            )
        """)

        # 风机性能表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS wind_turbine_performance (
                id BIGSERIAL PRIMARY KEY,
                turbine_id VARCHAR(20) NOT NULL,
                current_power DECIMAL(10,2),
                wind_speed DECIMAL(5,2),
                rotor_speed DECIMAL(5,2),
                generator_speed DECIMAL(5,2),
                temperature DECIMAL(5,2),
                vibration DECIMAL(5,2),
                power_factor DECIMAL(4,3),
                efficiency DECIMAL(5,2),
                performance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (turbine_id) REFERENCES wind_turbines(turbine_id)
            )
        """)

        # 光伏系统表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS solar_systems (
                id BIGSERIAL PRIMARY KEY,
                system_id VARCHAR(20) UNIQUE NOT NULL,
                system_name VARCHAR(200) NOT NULL,
                total_modules INTEGER,
                module_type VARCHAR(100),
                total_capacity DECIMAL(12,2),
                installation_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 光伏发电数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS solar_generation (
                id BIGSERIAL PRIMARY KEY,
                system_id VARCHAR(20) NOT NULL,
                dc_power DECIMAL(10,2),
                ac_power DECIMAL(10,2),
                daily_generation DECIMAL(12,2),
                system_efficiency DECIMAL(5,2),
                irradiance DECIMAL(8,2),
                ambient_temperature DECIMAL(5,2),
                generation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (system_id) REFERENCES solar_systems(system_id)
            )
        """)

        # 储能系统表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS energy_storage (
                id BIGSERIAL PRIMARY KEY,
                storage_id VARCHAR(20) UNIQUE NOT NULL,
                storage_name VARCHAR(200) NOT NULL,
                battery_type VARCHAR(50),
                battery_capacity DECIMAL(10,2),
                rated_voltage DECIMAL(8,2),
                installation_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 储能状态表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS storage_status (
                id BIGSERIAL PRIMARY KEY,
                storage_id VARCHAR(20) NOT NULL,
                soc DECIMAL(5,2),
                soh DECIMAL(5,2),
                voltage DECIMAL(8,2),
                current DECIMAL(8,2),
                temperature DECIMAL(5,2),
                health_status VARCHAR(20),
                status_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (storage_id) REFERENCES energy_storage(storage_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_wind_turbines_turbine_id
            ON wind_turbines(turbine_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_wind_turbine_performance_time
            ON wind_turbine_performance(turbine_id, performance_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_solar_generation_time
            ON solar_generation(system_id, generation_time DESC)
        """)

        self.conn.commit()

    def store_wind_turbine(self, turbine_data: Dict) -> int:
        """存储风力发电机组信息"""
        self.cur.execute("""
            INSERT INTO wind_turbines (
                turbine_id, turbine_name, turbine_model, manufacturer,
                rated_power, rotor_diameter, hub_height, installation_date,
                latitude, longitude
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (turbine_id) DO UPDATE SET
                turbine_name = EXCLUDED.turbine_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            turbine_data.get("turbine_id"),
            turbine_data.get("turbine_name"),
            turbine_data.get("turbine_model"),
            turbine_data.get("manufacturer"),
            turbine_data.get("rated_power"),
            turbine_data.get("rotor_diameter"),
            turbine_data.get("hub_height"),
            turbine_data.get("installation_date"),
            turbine_data.get("latitude"),
            turbine_data.get("longitude")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_wind_turbine_status(self, status_data: Dict):
        """存储风机状态"""
        self.cur.execute("""
            INSERT INTO wind_turbine_status (
                turbine_id, operational_status, fault_status, maintenance_status
            ) VALUES (%s, %s, %s, %s)
        """, (
            status_data.get("turbine_id"),
            status_data.get("operational_status"),
            status_data.get("fault_status"),
            status_data.get("maintenance_status")
        ))
        self.conn.commit()

    def store_wind_turbine_performance(self, perf_data: Dict):
        """存储风机性能数据"""
        self.cur.execute("""
            INSERT INTO wind_turbine_performance (
                turbine_id, current_power, wind_speed, rotor_speed,
                generator_speed, temperature, vibration, power_factor, efficiency
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            perf_data.get("turbine_id"),
            perf_data.get("current_power"),
            perf_data.get("wind_speed"),
            perf_data.get("rotor_speed"),
            perf_data.get("generator_speed"),
            perf_data.get("temperature"),
            perf_data.get("vibration"),
            perf_data.get("power_factor"),
            perf_data.get("efficiency")
        ))
        self.conn.commit()

    def store_solar_system(self, system_data: Dict) -> int:
        """存储光伏系统信息"""
        self.cur.execute("""
            INSERT INTO solar_systems (
                system_id, system_name, total_modules, module_type, total_capacity, installation_date
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (system_id) DO UPDATE SET
                system_name = EXCLUDED.system_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            system_data.get("system_id"),
            system_data.get("system_name"),
            system_data.get("total_modules"),
            system_data.get("module_type"),
            system_data.get("total_capacity"),
            system_data.get("installation_date")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_solar_generation(self, gen_data: Dict):
        """存储光伏发电数据"""
        self.cur.execute("""
            INSERT INTO solar_generation (
                system_id, dc_power, ac_power, daily_generation,
                system_efficiency, irradiance, ambient_temperature
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            gen_data.get("system_id"),
            gen_data.get("dc_power"),
            gen_data.get("ac_power"),
            gen_data.get("daily_generation"),
            gen_data.get("system_efficiency"),
            gen_data.get("irradiance"),
            gen_data.get("ambient_temperature")
        ))
        self.conn.commit()

    def store_energy_storage(self, storage_data: Dict) -> int:
        """存储储能系统信息"""
        self.cur.execute("""
            INSERT INTO energy_storage (
                storage_id, storage_name, battery_type, battery_capacity,
                rated_voltage, installation_date
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (storage_id) DO UPDATE SET
                storage_name = EXCLUDED.storage_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            storage_data.get("storage_id"),
            storage_data.get("storage_name"),
            storage_data.get("battery_type"),
            storage_data.get("battery_capacity"),
            storage_data.get("rated_voltage"),
            storage_data.get("installation_date")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_storage_status(self, status_data: Dict):
        """存储储能状态"""
        self.cur.execute("""
            INSERT INTO storage_status (
                storage_id, soc, soh, voltage, current, temperature, health_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            status_data.get("storage_id"),
            status_data.get("soc"),
            status_data.get("soh"),
            status_data.get("voltage"),
            status_data.get("current"),
            status_data.get("temperature"),
            status_data.get("health_status")
        ))
        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 5.2 可再生能源数据分析查询

**数据分析查询实现**：

```python
    def get_wind_turbine_statistics(self, turbine_id: str, hours: int = 24) -> Dict:
        """查询风机统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as data_count,
                AVG(current_power) as avg_power,
                MAX(current_power) as max_power,
                MIN(current_power) as min_power,
                AVG(wind_speed) as avg_wind_speed,
                AVG(efficiency) as avg_efficiency
            FROM wind_turbine_performance
            WHERE turbine_id = %s
            AND performance_time >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """, (turbine_id, hours))
        row = self.cur.fetchone()
        return {
            "data_count": row[0],
            "avg_power": float(row[1]) if row[1] else None,
            "max_power": float(row[2]) if row[2] else None,
            "min_power": float(row[3]) if row[3] else None,
            "avg_wind_speed": float(row[4]) if row[4] else None,
            "avg_efficiency": float(row[5]) if row[5] else None
        }

    def get_solar_generation_statistics(self, system_id: str, days: int = 30) -> Dict:
        """查询光伏发电统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as data_count,
                SUM(daily_generation) as total_generation,
                AVG(ac_power) as avg_power,
                AVG(system_efficiency) as avg_efficiency,
                MAX(ac_power) as max_power
            FROM solar_generation
            WHERE system_id = %s
            AND generation_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """, (system_id, days))
        row = self.cur.fetchone()
        return {
            "data_count": row[0],
            "total_generation": float(row[1]) if row[1] else None,
            "avg_power": float(row[2]) if row[2] else None,
            "avg_efficiency": float(row[3]) if row[3] else None,
            "max_power": float(row[4]) if row[4] else None
        }

    def get_storage_statistics(self, storage_id: str, hours: int = 24) -> Dict:
        """查询储能统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(*) as data_count,
                AVG(soc) as avg_soc,
                AVG(soh) as avg_soh,
                AVG(voltage) as avg_voltage,
                AVG(current) as avg_current,
                MIN(soc) as min_soc,
                MAX(soc) as max_soc
            FROM storage_status
            WHERE storage_id = %s
            AND status_time >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """, (storage_id, hours))
        row = self.cur.fetchone()
        return {
            "data_count": row[0],
            "avg_soc": float(row[1]) if row[1] else None,
            "avg_soh": float(row[2]) if row[2] else None,
            "avg_voltage": float(row[3]) if row[3] else None,
            "avg_current": float(row[4]) if row[4] else None,
            "min_soc": float(row[5]) if row[5] else None,
            "max_soc": float(row[6]) if row[6] else None
        }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
