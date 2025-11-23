# Matter Schema转换体系

## 📑 目录

- [Matter Schema转换体系](#matter-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Matter设备控制实现](#2-matter设备控制实现)
    - [2.1 Matter SDK设备控制封装](#21-matter-sdk设备控制封装)
    - [2.2 Matter到Zigbee转换](#22-matter到zigbee转换)
  - [3. Zigbee到Matter转换](#3-zigbee到matter转换)
  - [4. Matter设备发现和管理](#4-matter设备发现和管理)
    - [4.1 设备发现实现](#41-设备发现实现)
  - [5. 转换工具](#5-转换工具)
    - [5.1 Matter SDK集成](#51-matter-sdk集成)
    - [5.2 CHIP Tool集成](#52-chip-tool集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 转换正确性验证](#61-转换正确性验证)
    - [6.2 设备控制验证](#62-设备控制验证)
  - [7. Matter数据存储与分析](#7-matter数据存储与分析)
    - [7.1 PostgreSQL Matter数据存储](#71-postgresql-matter数据存储)
    - [7.2 Matter数据分析查询](#72-matter数据分析查询)

---

## 1. 转换体系概述

Matter Schema转换体系支持Matter设备、Zigbee设备、
数据库存储之间的转换。

### 1.1 转换目标

1. **Matter到Zigbee转换**：Matter集群到Zigbee集群
2. **Zigbee到Matter转换**：Zigbee集群到Matter集群
3. **数据到数据库转换**：Matter数据到PostgreSQL存储

---

## 2. Matter设备控制实现

### 2.1 Matter SDK设备控制封装

**完整的Matter设备控制实现**：

```python
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import IntEnum

logger = logging.getLogger(__name__)

# Matter集群ID定义 - 完整标准集群
class MatterClusterId(IntEnum):
    """Matter集群ID - 完整定义"""
    # 通用集群
    BASIC = 0x0028
    IDENTIFY = 0x0003
    GROUPS = 0x0004
    SCENES = 0x0005
    ON_OFF = 0x0006
    ON_OFF_SWITCH_CONFIG = 0x0007
    LEVEL_CONTROL = 0x0008
    BINARY_INPUT_BASIC = 0x000F
    POWER_PROFILE = 0x001A
    APPLIANCE_CONTROL = 0x001B
    DESCRIPTOR = 0x001D
    BINDING = 0x001E
    ACCESS_CONTROL = 0x001F

    # 照明集群
    COLOR_CONTROL = 0x0300
    BALLAST_CONFIGURATION = 0x0301

    # 安防集群
    DOOR_LOCK = 0x0101
    WINDOW_COVERING = 0x0102
    BARRIER_CONTROL = 0x0103

    # HVAC集群
    THERMOSTAT = 0x0201
    FAN_CONTROL = 0x0202
    DEHUMIDIFICATION_CONTROL = 0x0203
    THERMOSTAT_USER_INTERFACE_CONFIG = 0x0204

    # 测量集群
    TEMPERATURE_MEASUREMENT = 0x0402
    PRESSURE_MEASUREMENT = 0x0403
    FLOW_MEASUREMENT = 0x0404
    RELATIVE_HUMIDITY_MEASUREMENT = 0x0405
    OCCUPANCY_SENSING = 0x0406
    ILLUMINANCE_MEASUREMENT = 0x0400
    TEMPERATURE_SENSOR_CONFIG = 0x0401

    # 其他集群
    PUMP_CONFIG_AND_CONTROL = 0x0200
    TEMPERATURE_CONTROL = 0x0205
    REFRIGERATOR_ALARM = 0x0700
    DISH_WASHER_ALARM = 0x0701
    AIR_QUALITY = 0x0800

# Matter属性ID定义 - 完整定义
class MatterAttributeId(IntEnum):
    """Matter属性ID - 完整定义"""
    # Basic Cluster
    BASIC_VENDOR_ID = 0x0001
    BASIC_PRODUCT_ID = 0x0002
    BASIC_HARDWARE_VERSION = 0x0007
    BASIC_SOFTWARE_VERSION = 0x0009
    BASIC_MANUFACTURING_DATE = 0x000B
    BASIC_PRODUCT_LABEL = 0x0013

    # On/Off Cluster
    ON_OFF_ON_OFF = 0x0000
    ON_OFF_GLOBAL_SCENE_CONTROL = 0x4000
    ON_OFF_ON_TIME = 0x4001
    ON_OFF_OFF_WAIT_TIME = 0x4002
    ON_OFF_START_UP_ON_OFF = 0x4003

    # Level Control Cluster
    LEVEL_CONTROL_CURRENT_LEVEL = 0x0000
    LEVEL_CONTROL_REMAINING_TIME = 0x0001
    LEVEL_CONTROL_MIN_LEVEL = 0x0002
    LEVEL_CONTROL_MAX_LEVEL = 0x0003
    LEVEL_CONTROL_CURRENT_FREQUENCY = 0x0004
    LEVEL_CONTROL_MIN_FREQUENCY = 0x0005
    LEVEL_CONTROL_MAX_FREQUENCY = 0x0006
    LEVEL_CONTROL_OPTIONS = 0x000F
    LEVEL_CONTROL_ON_OFF_TRANSITION_TIME = 0x0010
    LEVEL_CONTROL_ON_LEVEL = 0x0011
    LEVEL_CONTROL_ON_TRANSITION_TIME = 0x0012
    LEVEL_CONTROL_OFF_TRANSITION_TIME = 0x0013
    LEVEL_CONTROL_DEFAULT_MOVE_RATE = 0x0014
    LEVEL_CONTROL_START_UP_CURRENT_LEVEL = 0x4000

    # Color Control Cluster
    COLOR_CONTROL_CURRENT_HUE = 0x0000
    COLOR_CONTROL_CURRENT_SATURATION = 0x0001
    COLOR_CONTROL_REMAINING_TIME = 0x0002
    COLOR_CONTROL_CURRENT_X = 0x0003
    COLOR_CONTROL_CURRENT_Y = 0x0004
    COLOR_CONTROL_DRIFT_COMPENSATION = 0x0005
    COLOR_CONTROL_COMPENSATION_TEXT = 0x0006
    COLOR_CONTROL_COLOR_TEMPERATURE_MIREDS = 0x0007
    COLOR_CONTROL_COLOR_MODE = 0x0008
    COLOR_CONTROL_OPTIONS = 0x000F
    COLOR_CONTROL_NUMBER_OF_PRIMARIES = 0x0010
    COLOR_CONTROL_PRIMARY1_X = 0x0011
    COLOR_CONTROL_PRIMARY1_Y = 0x0012
    COLOR_CONTROL_PRIMARY1_INTENSITY = 0x0013
    COLOR_CONTROL_PRIMARY2_X = 0x0015
    COLOR_CONTROL_PRIMARY2_Y = 0x0016
    COLOR_CONTROL_PRIMARY2_INTENSITY = 0x0017
    COLOR_CONTROL_PRIMARY3_X = 0x0019
    COLOR_CONTROL_PRIMARY3_Y = 0x001A
    COLOR_CONTROL_PRIMARY3_INTENSITY = 0x001B
    COLOR_CONTROL_PRIMARY4_X = 0x0020
    COLOR_CONTROL_PRIMARY4_Y = 0x0021
    COLOR_CONTROL_PRIMARY4_INTENSITY = 0x0022
    COLOR_CONTROL_PRIMARY5_X = 0x0024
    COLOR_CONTROL_PRIMARY5_Y = 0x0025
    COLOR_CONTROL_PRIMARY5_INTENSITY = 0x0026
    COLOR_CONTROL_PRIMARY6_X = 0x0028
    COLOR_CONTROL_PRIMARY6_Y = 0x0029
    COLOR_CONTROL_PRIMARY6_INTENSITY = 0x002A
    COLOR_CONTROL_WHITE_POINT_X = 0x0030
    COLOR_CONTROL_WHITE_POINT_Y = 0x0031
    COLOR_CONTROL_COLOR_POINT_RX = 0x0032
    COLOR_CONTROL_COLOR_POINT_RY = 0x0033
    COLOR_CONTROL_COLOR_POINT_R_INTENSITY = 0x0034
    COLOR_CONTROL_COLOR_POINT_GX = 0x0036
    COLOR_CONTROL_COLOR_POINT_GY = 0x0037
    COLOR_CONTROL_COLOR_POINT_G_INTENSITY = 0x0038
    COLOR_CONTROL_COLOR_POINT_BX = 0x003A
    COLOR_CONTROL_COLOR_POINT_BY = 0x003B
    COLOR_CONTROL_COLOR_POINT_B_INTENSITY = 0x003C
    COLOR_CONTROL_ENHANCED_CURRENT_HUE = 0x4000
    COLOR_CONTROL_ENHANCED_COLOR_MODE = 0x4001
    COLOR_CONTROL_COLOR_LOOP_ACTIVE = 0x4002
    COLOR_CONTROL_COLOR_LOOP_DIRECTION = 0x4003
    COLOR_CONTROL_COLOR_LOOP_TIME = 0x4004
    COLOR_CONTROL_COLOR_LOOP_START_ENHANCED_HUE = 0x4005
    COLOR_CONTROL_COLOR_LOOP_STORED_ENHANCED_HUE = 0x4006
    COLOR_CONTROL_COLOR_CAPABILITIES = 0x400A
    COLOR_CONTROL_COLOR_TEMP_PHYSICAL_MIN_MIREDS = 0x400B
    COLOR_CONTROL_COLOR_TEMP_PHYSICAL_MAX_MIREDS = 0x400C

    # Door Lock Cluster
    DOOR_LOCK_LOCK_STATE = 0x0000
    DOOR_LOCK_LOCK_TYPE = 0x0001
    DOOR_LOCK_ACTUATOR_ENABLED = 0x0002
    DOOR_LOCK_DOOR_STATE = 0x0003
    DOOR_LOCK_DOOR_OPEN_EVENTS = 0x0004
    DOOR_LOCK_DOOR_CLOSED_EVENTS = 0x0005
    DOOR_LOCK_OPEN_PERIOD = 0x0006
    DOOR_LOCK_NUMBER_OF_LOG_RECORDS_SUPPORTED = 0x0010
    DOOR_LOCK_NUMBER_OF_TOTAL_USERS_SUPPORTED = 0x0011
    DOOR_LOCK_NUMBER_OF_PIN_USERS_SUPPORTED = 0x0012
    DOOR_LOCK_NUMBER_OF_RFID_USERS_SUPPORTED = 0x0013
    DOOR_LOCK_NUMBER_OF_WEEKDAY_SCHEDULES_SUPPORTED_PER_USER = 0x0014
    DOOR_LOCK_NUMBER_OF_YEARDAY_SCHEDULES_SUPPORTED_PER_USER = 0x0015
    DOOR_LOCK_NUMBER_OF_HOLIDAY_SCHEDULES_SUPPORTED = 0x0016
    DOOR_LOCK_MAX_PIN_LENGTH = 0x0017
    DOOR_LOCK_MIN_PIN_LENGTH = 0x0018
    DOOR_LOCK_MAX_RFID_CODE_LENGTH = 0x0019
    DOOR_LOCK_MIN_RFID_CODE_LENGTH = 0x001A
    DOOR_LOCK_CREDENTIAL_RULES_SUPPORTED = 0x001B
    DOOR_LOCK_NUMBER_OF_CREDENTIALS_SUPPORTED_PER_USER = 0x001C
    DOOR_LOCK_ENABLE_LOGGING = 0x0020
    DOOR_LOCK_LANGUAGE = 0x0021
    DOOR_LOCK_LED_SETTINGS = 0x0022
    DOOR_LOCK_AUTO_RELOCK_TIME = 0x0023
    DOOR_LOCK_SOUND_VOLUME = 0x0024
    DOOR_LOCK_OPERATING_MODE = 0x0025
    DOOR_LOCK_SUPPORTED_OPERATING_MODES = 0x0026
    DOOR_LOCK_DEFAULT_CONFIGURATION_REGISTER = 0x0027
    DOOR_LOCK_ENABLE_LOCAL_PROGRAMMING = 0x0028
    DOOR_LOCK_ENABLE_ONE_TOUCH_LOCKING = 0x0029
    DOOR_LOCK_ENABLE_INSIDE_STATUS_LED = 0x002A
    DOOR_LOCK_ENABLE_PRIVACY_BUTTON = 0x002B
    DOOR_LOCK_WRONG_CODE_ENTRY_LIMIT = 0x0030
    DOOR_LOCK_USER_CODE_TEMPORARY_DISABLE_TIME = 0x0031
    DOOR_LOCK_SEND_PIN_OVER_THE_AIR = 0x0032
    DOOR_LOCK_REQUIRE_PIN_FOR_RF_OPERATION = 0x0033
    DOOR_LOCK_ZIGBEE_SECURITY_LEVEL = 0x0034
    DOOR_LOCK_ALARM_MASK = 0x0040
    DOOR_LOCK_KEYPAD_OPERATION_EVENT_MASK = 0x0041
    DOOR_LOCK_RF_OPERATION_EVENT_MASK = 0x0042
    DOOR_LOCK_MANUAL_OPERATION_EVENT_MASK = 0x0043
    DOOR_LOCK_RFID_OPERATION_EVENT_MASK = 0x0044
    DOOR_LOCK_KEYPAD_PROGRAMMING_EVENT_MASK = 0x0045
    DOOR_LOCK_RF_PROGRAMMING_EVENT_MASK = 0x0046
    DOOR_LOCK_RFID_PROGRAMMING_EVENT_MASK = 0x0047

    # Thermostat Cluster
    THERMOSTAT_LOCAL_TEMPERATURE = 0x0000
    THERMOSTAT_OUTDOOR_TEMPERATURE = 0x0001
    THERMOSTAT_OCCUPANCY = 0x0002
    THERMOSTAT_ABS_MIN_HEAT_SETPOINT_LIMIT = 0x0003
    THERMOSTAT_ABS_MAX_HEAT_SETPOINT_LIMIT = 0x0004
    THERMOSTAT_ABS_MIN_COOL_SETPOINT_LIMIT = 0x0005
    THERMOSTAT_ABS_MAX_COOL_SETPOINT_LIMIT = 0x0006
    THERMOSTAT_PI_COOLING_DEMAND = 0x0007
    THERMOSTAT_PI_HEATING_DEMAND = 0x0008
    THERMOSTAT_HVAC_SYSTEM_TYPE_CONFIG = 0x0009
    THERMOSTAT_LOCAL_TEMPERATURE_CALIBRATION = 0x0010
    THERMOSTAT_OCCUPIED_COOLING_SETPOINT = 0x0011
    THERMOSTAT_OCCUPIED_HEATING_SETPOINT = 0x0012
    THERMOSTAT_UNOCCUPIED_COOLING_SETPOINT = 0x0013
    THERMOSTAT_UNOCCUPIED_HEATING_SETPOINT = 0x0014
    THERMOSTAT_MIN_HEAT_SETPOINT_LIMIT = 0x0015
    THERMOSTAT_MAX_HEAT_SETPOINT_LIMIT = 0x0016
    THERMOSTAT_MIN_COOL_SETPOINT_LIMIT = 0x0017
    THERMOSTAT_MAX_COOL_SETPOINT_LIMIT = 0x0018
    THERMOSTAT_MIN_SETPOINT_DEAD_BAND = 0x0019
    THERMOSTAT_REMOTE_SENSING = 0x001A
    THERMOSTAT_CONTROL_SEQUENCE_OF_OPERATION = 0x001B
    THERMOSTAT_SYSTEM_MODE = 0x001C
    THERMOSTAT_ALARM_MASK = 0x001D
    THERMOSTAT_THERMOSTAT_RUNNING_MODE = 0x001E
    THERMOSTAT_START_OF_WEEK = 0x0020
    THERMOSTAT_NUMBER_OF_WEEKLY_TRANSITIONS = 0x0021
    THERMOSTAT_NUMBER_OF_DAILY_TRANSITIONS = 0x0022
    THERMOSTAT_TEMPERATURE_SETPOINT_HOLD = 0x0023
    THERMOSTAT_TEMPERATURE_SETPOINT_HOLD_DURATION = 0x0024
    THERMOSTAT_THERMOSTAT_PROGRAMMING_OPERATION_MODE = 0x0025
    THERMOSTAT_THERMOSTAT_RUNNING_STATE = 0x0029
    THERMOSTAT_SETPOINT_CHANGE_SOURCE = 0x0030
    THERMOSTAT_SETPOINT_CHANGE_AMOUNT = 0x0031
    THERMOSTAT_SETPOINT_CHANGE_SOURCE_TIMESTAMP = 0x0032
    THERMOSTAT_OCCUPIED_SETBACK = 0x0034
    THERMOSTAT_OCCUPIED_SETBACK_MIN = 0x0035
    THERMOSTAT_OCCUPIED_SETBACK_MAX = 0x0036
    THERMOSTAT_UNOCCUPIED_SETBACK = 0x0037
    THERMOSTAT_UNOCCUPIED_SETBACK_MIN = 0x0038
    THERMOSTAT_UNOCCUPIED_SETBACK_MAX = 0x0039
    THERMOSTAT_EMERGENCY_HEAT_DELTA = 0x003A
    THERMOSTAT_AC_TYPE = 0x0040
    THERMOSTAT_AC_CAPACITY = 0x0041
    THERMOSTAT_AC_REFRIGERANT_TYPE = 0x0042
    THERMOSTAT_AC_COMPRESSOR_TYPE = 0x0043
    THERMOSTAT_AC_ERROR_CODE = 0x0044
    THERMOSTAT_AC_LOUVER_POSITION = 0x0045
    THERMOSTAT_AC_COIL_TEMPERATURE = 0x0046
    THERMOSTAT_AC_CAPACITY_FORMAT = 0x0047

# Matter命令ID定义 - 完整定义
class MatterCommandId(IntEnum):
    """Matter命令ID - 完整定义"""
    # On/Off Cluster
    ON_OFF_ON = 0x00
    ON_OFF_OFF = 0x01
    ON_OFF_TOGGLE = 0x02
    ON_OFF_OFF_WITH_EFFECT = 0x40
    ON_OFF_ON_WITH_RECALL_GLOBAL_SCENE = 0x41
    ON_OFF_ON_WITH_TIMED_OFF = 0x42

    # Level Control Cluster
    LEVEL_CONTROL_MOVE_TO_LEVEL = 0x00
    LEVEL_CONTROL_MOVE = 0x01
    LEVEL_CONTROL_STEP = 0x02
    LEVEL_CONTROL_STOP = 0x03
    LEVEL_CONTROL_MOVE_TO_LEVEL_WITH_ON_OFF = 0x04
    LEVEL_CONTROL_MOVE_WITH_ON_OFF = 0x05
    LEVEL_CONTROL_STEP_WITH_ON_OFF = 0x06
    LEVEL_CONTROL_STOP_WITH_ON_OFF = 0x07
    LEVEL_CONTROL_MOVE_TO_CLOSEST_FREQUENCY = 0x08

    # Color Control Cluster
    COLOR_CONTROL_MOVE_TO_HUE = 0x00
    COLOR_CONTROL_MOVE_HUE = 0x01
    COLOR_CONTROL_STEP_HUE = 0x02
    COLOR_CONTROL_MOVE_TO_SATURATION = 0x03
    COLOR_CONTROL_MOVE_SATURATION = 0x04
    COLOR_CONTROL_STEP_SATURATION = 0x05
    COLOR_CONTROL_MOVE_TO_COLOR = 0x06
    COLOR_CONTROL_MOVE_COLOR = 0x07
    COLOR_CONTROL_STEP_COLOR = 0x08
    COLOR_CONTROL_MOVE_TO_COLOR_TEMPERATURE = 0x0A
    COLOR_CONTROL_ENHANCED_MOVE_TO_HUE = 0x40
    COLOR_CONTROL_ENHANCED_MOVE_HUE = 0x41
    COLOR_CONTROL_ENHANCED_STEP_HUE = 0x42
    COLOR_CONTROL_ENHANCED_MOVE_TO_HUE_AND_SATURATION = 0x43
    COLOR_CONTROL_COLOR_LOOP_SET = 0x44
    COLOR_CONTROL_STOP_MOVE_STEP = 0x47
    COLOR_CONTROL_MOVE_COLOR_TEMPERATURE = 0x4B
    COLOR_CONTROL_STEP_COLOR_TEMPERATURE = 0x4C

    # Door Lock Cluster
    DOOR_LOCK_LOCK_DOOR = 0x00
    DOOR_LOCK_UNLOCK_DOOR = 0x01
    DOOR_LOCK_TOGGLE = 0x02
    DOOR_LOCK_UNLOCK_WITH_TIMEOUT = 0x03
    DOOR_LOCK_GET_LOG_RECORD = 0x04
    DOOR_LOCK_SET_PIN = 0x05
    DOOR_LOCK_GET_PIN = 0x06
    DOOR_LOCK_CLEAR_PIN = 0x07
    DOOR_LOCK_CLEAR_ALL_PINS = 0x08
    DOOR_LOCK_SET_USER_STATUS = 0x09
    DOOR_LOCK_GET_USER_STATUS = 0x0A
    DOOR_LOCK_SET_WEEKDAY_SCHEDULE = 0x0B
    DOOR_LOCK_GET_WEEKDAY_SCHEDULE = 0x0C
    DOOR_LOCK_CLEAR_WEEKDAY_SCHEDULE = 0x0D
    DOOR_LOCK_SET_YEARDAY_SCHEDULE = 0x0E
    DOOR_LOCK_GET_YEARDAY_SCHEDULE = 0x0F
    DOOR_LOCK_CLEAR_YEARDAY_SCHEDULE = 0x10
    DOOR_LOCK_SET_HOLIDAY_SCHEDULE = 0x11
    DOOR_LOCK_GET_HOLIDAY_SCHEDULE = 0x12
    DOOR_LOCK_CLEAR_HOLIDAY_SCHEDULE = 0x13
    DOOR_LOCK_SET_USER_TYPE = 0x14
    DOOR_LOCK_GET_USER_TYPE = 0x15
    DOOR_LOCK_SET_RFID = 0x16
    DOOR_LOCK_GET_RFID = 0x17
    DOOR_LOCK_CLEAR_RFID = 0x18
    DOOR_LOCK_CLEAR_ALL_RFIDS = 0x19
    DOOR_LOCK_OPERATION_EVENT_NOTIFICATION = 0x20
    DOOR_LOCK_PROGRAMMING_EVENT_NOTIFICATION = 0x21
    DOOR_LOCK_SET_CREDENTIAL = 0x22
    DOOR_LOCK_GET_CREDENTIAL_STATUS = 0x23
    DOOR_LOCK_CLEAR_CREDENTIAL = 0x24

    # Thermostat Cluster
    THERMOSTAT_SETPOINT_RAISE_LOWER = 0x00
    THERMOSTAT_SET_WEEKLY_SCHEDULE = 0x01
    THERMOSTAT_GET_WEEKLY_SCHEDULE = 0x02
    THERMOSTAT_CLEAR_WEEKLY_SCHEDULE = 0x03
    THERMOSTAT_GET_RELAY_STATUS_LOG = 0x04

class MatterDeviceController:
    """Matter设备控制器 - 完整实现"""

    def __init__(self, device_id: str, node_id: int, endpoint_id: int = 1,
                 matter_sdk_wrapper=None):
        self.device_id = device_id
        self.node_id = node_id
        self.endpoint_id = endpoint_id
        self.matter_sdk = matter_sdk_wrapper
        self.connected = False
        self.connection_retry_count = 0
        self.max_retry_count = 3
        self.attribute_subscriptions: Dict[tuple, Callable] = {}
        self.command_history: List[Dict] = []
        self.last_error: Optional[str] = None
        self.device_info: Optional[Dict] = None

    async def connect(self, timeout: int = 10) -> bool:
        """连接到Matter设备 - 增强错误处理"""
        """
        连接到Matter设备，支持重试和超时处理
        """
        # 输入验证
        if not isinstance(timeout, int):
            raise TypeError(f"Timeout must be an integer, got {type(timeout)}")

        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")

        if timeout > 300:  # 最大5分钟
            raise ValueError(f"Timeout too large: {timeout} seconds (max 300)")

        if not self.device_id:
            raise ValueError("Device ID cannot be empty")

        if not isinstance(self.device_id, str):
            raise TypeError(f"Device ID must be a string, got {type(self.device_id)}")

        if self.connected:
            logger.debug(f"Device {self.device_id} already connected")
            return True

        for attempt in range(self.max_retry_count):
            try:
                logger.info(f"Connecting to Matter device {self.device_id} (attempt {attempt + 1}/{self.max_retry_count})")

                if self.matter_sdk:
                    # 使用Matter SDK连接
                    device = self.matter_sdk.get_device(self.device_id)
                    if device:
                        self.connected = True
                        self.device_info = {
                            "device_id": self.device_id,
                            "node_id": self.node_id,
                            "endpoint_id": self.endpoint_id,
                            "mesh_local_address": device.mesh_local_address,
                            "device_type": device.device_type
                        }
                        logger.info(f"Connected to Matter device {self.device_id}")
                        self.connection_retry_count = 0
                        return True
                else:
                    # Mock实现用于测试
                    await asyncio.sleep(0.1)
                    self.connected = True
                    self.device_info = {
                        "device_id": self.device_id,
                        "node_id": self.node_id,
                        "endpoint_id": self.endpoint_id
                    }
                    logger.info(f"Connected to Matter device {self.device_id} (mock)")
                    return True

            except TimeoutError as e:
                self.last_error = f"Connection timeout: {e}"
                logger.warning(f"Connection attempt {attempt + 1} timeout: {e}")
                if attempt < self.max_retry_count - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"Failed to connect to device {self.device_id} after {self.max_retry_count} attempts (timeout)")
                    raise TimeoutError(f"Connection timeout after {self.max_retry_count} attempts: {e}") from e
            except ConnectionError as e:
                self.last_error = f"Connection error: {e}"
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retry_count - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"Failed to connect to device {self.device_id} after {self.max_retry_count} attempts")
                    raise ConnectionError(f"Connection failed after {self.max_retry_count} attempts: {e}") from e
            except Exception as e:
                self.last_error = str(e)
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retry_count - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"Failed to connect to device {self.device_id} after {self.max_retry_count} attempts: {e}", exc_info=True)
                    raise RuntimeError(f"Connection failed after {self.max_retry_count} attempts: {e}") from e

        return False

    async def disconnect(self):
        """断开Matter设备连接 - 完整实现"""
        if not self.connected:
            return

        try:
            # 取消所有订阅
            self.attribute_subscriptions.clear()

            # 断开连接
            self.connected = False
            self.device_info = None
            logger.info(f"Disconnected from Matter device {self.device_id}")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def read_attribute(self, cluster_id: int, attribute_id: int,
                            timeout: int = 5, retry_count: int = 2) -> Optional[Any]:
        """读取设备属性 - 增强错误处理"""
        """
        读取设备属性，支持重试和超时处理
        """
        # 输入验证
        if not isinstance(cluster_id, int):
            raise TypeError(f"Cluster ID must be an integer, got {type(cluster_id)}")

        if not (0 <= cluster_id <= 0xFFFF):
            raise ValueError(f"Cluster ID out of range: {cluster_id} (must be 0-65535)")

        if not isinstance(attribute_id, int):
            raise TypeError(f"Attribute ID must be an integer, got {type(attribute_id)}")

        if not (0 <= attribute_id <= 0xFFFF):
            raise ValueError(f"Attribute ID out of range: {attribute_id} (must be 0-65535)")

        if not isinstance(timeout, int):
            raise TypeError(f"Timeout must be an integer, got {type(timeout)}")

        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")

        if timeout > 60:
            raise ValueError(f"Timeout too large: {timeout} seconds (max 60)")

        if not isinstance(retry_count, int):
            raise TypeError(f"Retry count must be an integer, got {type(retry_count)}")

        if retry_count < 0:
            raise ValueError(f"Retry count must be non-negative, got {retry_count}")

        if retry_count > 10:
            raise ValueError(f"Retry count too large: {retry_count} (max 10)")

        if not self.connected:
            raise ConnectionError(f"Device {self.device_id} not connected. Call connect() first.")

        for attempt in range(retry_count + 1):
            try:
                logger.debug(f"Reading attribute {attribute_id:04X} from cluster {cluster_id:04X}")

                if self.matter_sdk:
                    # 使用Matter SDK读取属性
                    value = self.matter_sdk.read_attribute(
                        self.device_id,
                        self.endpoint_id,
                        cluster_id,
                        attribute_id
                    )

                    if value is not None:
                        logger.debug(f"Read attribute success: {value}")
                        return value
                    elif attempt < retry_count:
                        logger.warning(f"Read attribute returned None, retrying...")
                        await asyncio.sleep(0.5)
                    else:
                        logger.error(f"Failed to read attribute after {retry_count + 1} attempts")
                        return None
                else:
                    # Mock实现
                    await asyncio.sleep(0.05)
                    # 返回模拟值
                    return self._mock_read_attribute(cluster_id, attribute_id)

            except Exception as e:
                self.last_error = str(e)
                logger.error(f"Failed to read attribute (attempt {attempt + 1}): {e}")
                if attempt < retry_count:
                    await asyncio.sleep(0.5)
                else:
                    return None

        return None

    def _mock_read_attribute(self, cluster_id: int, attribute_id: int) -> Any:
        """Mock属性读取实现"""
        if cluster_id == MatterClusterId.ON_OFF:
            if attribute_id == MatterAttributeId.ON_OFF_ON_OFF:
                return True  # 模拟开关状态
        elif cluster_id == MatterClusterId.LEVEL_CONTROL:
            if attribute_id == MatterAttributeId.LEVEL_CONTROL_CURRENT_LEVEL:
                return 128  # 模拟亮度级别
        elif cluster_id == MatterClusterId.COLOR_CONTROL:
            if attribute_id == MatterAttributeId.COLOR_CONTROL_CURRENT_HUE:
                return 128
            elif attribute_id == MatterAttributeId.COLOR_CONTROL_CURRENT_SATURATION:
                return 200
        elif cluster_id == MatterClusterId.DOOR_LOCK:
            if attribute_id == 0x0000:  # LockState
                return 1  # Locked
        elif cluster_id == MatterClusterId.THERMOSTAT:
            if attribute_id == 0x0000:  # LocalTemperature
                return 2500  # 25.00°C
        return None

    async def write_attribute(self, cluster_id: int, attribute_id: int, value: Any,
                             timeout: int = 5, retry_count: int = 2) -> bool:
        """写入设备属性 - 完整实现"""
        """
        写入设备属性，支持重试和超时处理
        """
        if not self.connected:
            raise RuntimeError(f"Device {self.device_id} not connected")

        for attempt in range(retry_count + 1):
            try:
                logger.debug(f"Writing attribute {attribute_id:04X} = {value} to cluster {cluster_id:04X}")

                if self.matter_sdk:
                    # 使用Matter SDK写入属性
                    success = self.matter_sdk.write_attribute(
                        self.device_id,
                        self.endpoint_id,
                        cluster_id,
                        attribute_id,
                        value
                    )

                    if success:
                        logger.info(f"Write attribute success")
                        return True
                    elif attempt < retry_count:
                        logger.warning(f"Write attribute failed, retrying...")
                        await asyncio.sleep(0.5)
                    else:
                        logger.error(f"Failed to write attribute after {retry_count + 1} attempts")
                        return False
                else:
                    # Mock实现
                    await asyncio.sleep(0.05)
                    logger.info(f"Write attribute success (mock)")
                    return True

            except Exception as e:
                self.last_error = str(e)
                logger.error(f"Failed to write attribute (attempt {attempt + 1}): {e}")
                if attempt < retry_count:
                    await asyncio.sleep(0.5)
                else:
                    return False

        return False

    async def send_command(self, cluster_id: int, command_id: int,
                          parameters: Dict = None, timeout: int = 5,
                          retry_count: int = 2) -> bool:
        """发送命令到设备 - 增强错误处理"""
        """
        发送命令到设备，支持重试和超时处理
        """
        # 输入验证
        if not isinstance(cluster_id, int):
            raise TypeError(f"Cluster ID must be an integer, got {type(cluster_id)}")

        if not (0 <= cluster_id <= 0xFFFF):
            raise ValueError(f"Cluster ID out of range: {cluster_id} (must be 0-65535)")

        if not isinstance(command_id, int):
            raise TypeError(f"Command ID must be an integer, got {type(command_id)}")

        if not (0 <= command_id <= 0xFF):
            raise ValueError(f"Command ID out of range: {command_id} (must be 0-255)")

        if parameters is not None:
            if not isinstance(parameters, dict):
                raise TypeError(f"Parameters must be a dictionary, got {type(parameters)}")
        else:
            parameters = {}

        if not isinstance(timeout, int):
            raise TypeError(f"Timeout must be an integer, got {type(timeout)}")

        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")

        if timeout > 60:
            raise ValueError(f"Timeout too large: {timeout} seconds (max 60)")

        if not isinstance(retry_count, int):
            raise TypeError(f"Retry count must be an integer, got {type(retry_count)}")

        if retry_count < 0:
            raise ValueError(f"Retry count must be non-negative, got {retry_count}")

        if retry_count > 10:
            raise ValueError(f"Retry count too large: {retry_count} (max 10)")

        if not self.connected:
            raise ConnectionError(f"Device {self.device_id} not connected. Call connect() first.")

        command_record = {
            "cluster_id": cluster_id,
            "command_id": command_id,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

        for attempt in range(retry_count + 1):
            try:
                logger.info(f"Sending command {command_id:02X} to cluster {cluster_id:04X} with {parameters}")

                if self.matter_sdk:
                    # 使用Matter SDK发送命令
                    success = self.matter_sdk.send_command(
                        self.device_id,
                        self.endpoint_id,
                        cluster_id,
                        command_id,
                        parameters
                    )

                    if success:
                        command_record["success"] = True
                        self.command_history.append(command_record)
                        logger.info(f"Command sent successfully")
                        return True
                    elif attempt < retry_count:
                        logger.warning(f"Command failed, retrying...")
                        await asyncio.sleep(0.5)
                    else:
                        logger.error(f"Failed to send command after {retry_count + 1} attempts")
                        self.command_history.append(command_record)
                        return False
                else:
                    # Mock实现
                    await asyncio.sleep(0.1)
                    command_record["success"] = True
                    self.command_history.append(command_record)
                    logger.info(f"Command sent successfully (mock)")
                    return True

            except Exception as e:
                self.last_error = str(e)
                logger.error(f"Failed to send command (attempt {attempt + 1}): {e}")
                if attempt < retry_count:
                    await asyncio.sleep(0.5)
                else:
                    self.command_history.append(command_record)
                    return False

        return False

    def subscribe_attribute(self, cluster_id: int, attribute_id: int,
                          callback: Callable[[Any], None], min_interval: int = 0,
                          max_interval: int = 60):
        """订阅属性变化 - 增强错误处理"""
        """
        订阅属性变化，支持最小和最大间隔设置
        """
        # 输入验证
        if not isinstance(cluster_id, int):
            raise TypeError(f"Cluster ID must be an integer, got {type(cluster_id)}")

        if not (0 <= cluster_id <= 0xFFFF):
            raise ValueError(f"Cluster ID out of range: {cluster_id} (must be 0-65535)")

        if not isinstance(attribute_id, int):
            raise TypeError(f"Attribute ID must be an integer, got {type(attribute_id)}")

        if not (0 <= attribute_id <= 0xFFFF):
            raise ValueError(f"Attribute ID out of range: {attribute_id} (must be 0-65535)")

        if not callable(callback):
            raise TypeError(f"Callback must be callable, got {type(callback)}")

        if not isinstance(min_interval, int):
            raise TypeError(f"Min interval must be an integer, got {type(min_interval)}")

        if min_interval < 0:
            raise ValueError(f"Min interval must be non-negative, got {min_interval}")

        if not isinstance(max_interval, int):
            raise TypeError(f"Max interval must be an integer, got {type(max_interval)}")

        if max_interval <= 0:
            raise ValueError(f"Max interval must be positive, got {max_interval}")

        if max_interval > 3600:  # 最大1小时
            raise ValueError(f"Max interval too large: {max_interval} seconds (max 3600)")

        if min_interval > max_interval:
            raise ValueError(f"Min interval ({min_interval}) cannot be greater than max interval ({max_interval})")

        if not self.connected:
            raise ConnectionError(f"Device {self.device_id} not connected. Call connect() first.")

        key = (cluster_id, attribute_id)
        self.attribute_subscriptions[key] = callback

        if self.matter_sdk:
            # 使用Matter SDK订阅事件
            self.matter_sdk.subscribe_events(
                self.device_id,
                self.endpoint_id,
                cluster_id,
                callback,
                min_interval,
                max_interval
            )

        logger.info(f"Subscribed to attribute {attribute_id:04X} in cluster {cluster_id:04X}")

    def unsubscribe_attribute(self, cluster_id: int, attribute_id: int):
        """取消订阅属性变化"""
        key = (cluster_id, attribute_id)
        if key in self.attribute_subscriptions:
            del self.attribute_subscriptions[key]
            logger.info(f"Unsubscribed from attribute {attribute_id:04X} in cluster {cluster_id:04X}")

    def get_device_info(self) -> Optional[Dict]:
        """获取设备信息"""
        return self.device_info

    def get_command_history(self, limit: int = 100) -> List[Dict]:
        """获取命令历史"""
        return self.command_history[-limit:]

    def get_last_error(self) -> Optional[str]:
        """获取最后的错误信息"""
        return self.last_error

    def is_connected(self) -> bool:
        """检查设备是否已连接"""
        return self.connected

    async def ping(self) -> bool:
        """ping设备以检查连接状态"""
        if not self.connected:
            return False

        try:
            # 尝试读取Basic Cluster的属性来检查连接
            value = await self.read_attribute(
                MatterClusterId.BASIC if hasattr(MatterClusterId, 'BASIC') else 0x0028,
                0x0000,  # VendorID
                timeout=2,
                retry_count=0
            )
            return value is not None
        except Exception:
            return False

class MatterOnOffLightController(MatterDeviceController):
    """Matter On/Off Light控制器"""

    async def turn_on(self) -> bool:
        """打开灯光"""
        return await self.send_command(
            MatterClusterId.ON_OFF,
            MatterCommandId.ON_OFF_ON
        )

    async def turn_off(self) -> bool:
        """关闭灯光"""
        return await self.send_command(
            MatterClusterId.ON_OFF,
            MatterCommandId.ON_OFF_OFF
        )

    async def toggle(self) -> bool:
        """切换灯光状态"""
        return await self.send_command(
            MatterClusterId.ON_OFF,
            MatterCommandId.ON_OFF_TOGGLE
        )

    async def get_state(self) -> Optional[bool]:
        """获取灯光状态"""
        value = await self.read_attribute(
            MatterClusterId.ON_OFF,
            MatterAttributeId.ON_OFF_ON_OFF
        )
        return value if value is not None else None

class MatterDimmableLightController(MatterOnOffLightController):
    """Matter Dimmable Light控制器"""

    async def set_level(self, level: int) -> bool:
        """设置亮度级别（0-254）"""
        if level < 0 or level > 254:
            raise ValueError("Level must be between 0 and 254")

        return await self.send_command(
            MatterClusterId.LEVEL_CONTROL,
            MatterCommandId.LEVEL_CONTROL_MOVE_TO_LEVEL,
            {
                "level": level,
                "transition_time": 0  # 立即切换
            }
        )

    async def get_level(self) -> Optional[int]:
        """获取当前亮度级别"""
        value = await self.read_attribute(
            MatterClusterId.LEVEL_CONTROL,
            MatterAttributeId.LEVEL_CONTROL_CURRENT_LEVEL
        )
        return value if value is not None else None

    async def move_level(self, move_mode: str, rate: int) -> bool:
        """移动亮度级别"""
        # move_mode: "Up" or "Down"
        move_mode_map = {"Up": 0, "Down": 1}
        return await self.send_command(
            MatterClusterId.LEVEL_CONTROL,
            MatterCommandId.LEVEL_CONTROL_MOVE,
            {
                "move_mode": move_mode_map.get(move_mode, 0),
                "rate": rate
            }
        )

class MatterColorLightController(MatterDimmableLightController):
    """Matter Color Light控制器"""

    async def set_hue_saturation(self, hue: int, saturation: int) -> bool:
        """设置色相和饱和度"""
        if hue < 0 or hue > 254:
            raise ValueError("Hue must be between 0 and 254")
        if saturation < 0 or saturation > 254:
            raise ValueError("Saturation must be between 0 and 254")

        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_MOVE_TO_HUE,
            {
                "hue": hue,
                "saturation": saturation,
                "transition_time": 0,
                "options_mask": 0,
                "options_override": 0
            }
        )

    async def set_color_temperature(self, color_temp_mireds: int) -> bool:
        """设置色温（mireds）"""
        if color_temp_mireds < 153 or color_temp_mireds > 500:
            raise ValueError("Color temperature must be between 153 and 500 mireds")

        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_MOVE_TO_COLOR_TEMPERATURE,
            {
                "color_temperature_mireds": color_temp_mireds,
                "transition_time": 0,
                "options_mask": 0,
                "options_override": 0
            }
        )

    async def get_hue_saturation(self) -> Optional[Dict]:
        """获取当前色相和饱和度"""
        hue = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_CURRENT_HUE
        )
        saturation = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_CURRENT_SATURATION
        )

        if hue is not None and saturation is not None:
            return {"hue": hue, "saturation": saturation}
        return None

    async def get_color_temperature(self) -> Optional[int]:
        """获取当前色温"""
        value = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_COLOR_TEMPERATURE_MIREDS
        )
        return value if value is not None else None

    async def enhanced_move_to_hue(self, enhanced_hue: int, direction: int,
                                   transition_time: int, options_mask: int = 0,
                                   options_override: int = 0) -> bool:
        """增强移动到色相（使用增强色相值0-65535）"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_ENHANCED_MOVE_TO_HUE,
            {
                "enhanced_hue": enhanced_hue,
                "direction": direction,
                "transition_time": transition_time,
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def enhanced_move_hue(self, move_mode: int, rate: int,
                               options_mask: int = 0, options_override: int = 0) -> bool:
        """增强移动色相"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_ENHANCED_MOVE_HUE,
            {
                "move_mode": move_mode,
                "rate": rate,
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def enhanced_step_hue(self, step_mode: int, step_size: int,
                               transition_time: int, options_mask: int = 0,
                               options_override: int = 0) -> bool:
        """增强步进色相"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_ENHANCED_STEP_HUE,
            {
                "step_mode": step_mode,
                "step_size": step_size,
                "transition_time": transition_time,
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def enhanced_move_to_hue_and_saturation(self, enhanced_hue: int,
                                                  saturation: int,
                                                  direction: int,
                                                  transition_time: int,
                                                  options_mask: int = 0,
                                                  options_override: int = 0) -> bool:
        """增强移动到色相和饱和度"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_ENHANCED_MOVE_TO_HUE_AND_SATURATION,
            {
                "enhanced_hue": enhanced_hue,
                "saturation": saturation,
                "direction": direction,
                "transition_time": transition_time,
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def color_loop_set(self, update_flags: int, action: int,
                            direction: int, time: int, start_hue: int,
                            options_mask: int = 0,
                            options_override: int = 0) -> bool:
        """设置颜色循环"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_COLOR_LOOP_SET,
            {
                "update_flags": update_flags,
                "action": action,
                "direction": direction,
                "time": time,
                "start_hue": start_hue,
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def stop_move_step(self, options_mask: int = 0,
                            options_override: int = 0) -> bool:
        """停止移动/步进操作"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_STOP_MOVE_STEP,
            {
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def move_color_temperature(self, move_mode: int, rate: int,
                                    color_temperature_min_mireds: int,
                                    color_temperature_max_mireds: int,
                                    options_mask: int = 0,
                                    options_override: int = 0) -> bool:
        """移动色温"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_MOVE_COLOR_TEMPERATURE,
            {
                "move_mode": move_mode,
                "rate": rate,
                "color_temperature_min_mireds": color_temperature_min_mireds,
                "color_temperature_max_mireds": color_temperature_max_mireds,
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def step_color_temperature(self, step_mode: int, step_size: int,
                                    transition_time: int,
                                    color_temperature_min_mireds: int,
                                    color_temperature_max_mireds: int,
                                    options_mask: int = 0,
                                    options_override: int = 0) -> bool:
        """步进色温"""
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_STEP_COLOR_TEMPERATURE,
            {
                "step_mode": step_mode,
                "step_size": step_size,
                "transition_time": transition_time,
                "color_temperature_min_mireds": color_temperature_min_mireds,
                "color_temperature_max_mireds": color_temperature_max_mireds,
                "options_mask": options_mask,
                "options_override": options_override
            }
        )

    async def set_rgb_color(self, red: int, green: int, blue: int) -> bool:
        """设置RGB颜色（转换为XY坐标）"""
        # 将RGB转换为XY坐标
        x, y = self._rgb_to_xy(red, green, blue)
        return await self.send_command(
            MatterClusterId.COLOR_CONTROL,
            MatterCommandId.COLOR_CONTROL_MOVE_TO_COLOR,
            {
                "color_x": int(x * 65536),
                "color_y": int(y * 65536),
                "transition_time": 0
            }
        )

    def _rgb_to_xy(self, r: int, g: int, b: int) -> tuple:
        """将RGB转换为XY坐标"""
        # 归一化RGB值
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        # 应用gamma校正
        r_gamma = self._gamma_correct(r_norm)
        g_gamma = self._gamma_correct(g_norm)
        b_gamma = self._gamma_correct(b_norm)

        # 转换为XYZ颜色空间
        X = r_gamma * 0.4124 + g_gamma * 0.3576 + b_gamma * 0.1805
        Y = r_gamma * 0.2126 + g_gamma * 0.7152 + b_gamma * 0.0722
        Z = r_gamma * 0.0193 + g_gamma * 0.1192 + b_gamma * 0.9505

        # 转换为xy坐标
        total = X + Y + Z
        if total == 0:
            return (0.3127, 0.3290)  # D65白点

        x = X / total
        y = Y / total

        return (x, y)

    def _gamma_correct(self, value: float) -> float:
        """Gamma校正"""
        if value > 0.04045:
            return ((value + 0.055) / 1.055) ** 2.4
        else:
            return value / 12.92

    async def get_color_info(self) -> Dict:
        """获取颜色完整信息"""
        hue_sat = await self.get_hue_saturation()
        color_temp = await self.get_color_temperature()

        # 读取XY坐标
        current_x = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_CURRENT_X
        )
        current_y = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_CURRENT_Y
        )

        # 读取颜色模式
        color_mode = await self.read_attribute(
            MatterClusterId.COLOR_CONTROL,
            MatterAttributeId.COLOR_CONTROL_COLOR_MODE
        )

        return {
            "hue": hue_sat.get("hue") if hue_sat else None,
            "saturation": hue_sat.get("saturation") if hue_sat else None,
            "color_temperature": color_temp,
            "color_x": current_x / 65536.0 if current_x else None,
            "color_y": current_y / 65536.0 if current_y else None,
            "color_mode": color_mode
        }

class MatterDoorLockController(MatterDeviceController):
    """Matter Door Lock控制器 - 完整实现"""

    async def lock_door(self, pin_code: Optional[str] = None) -> bool:
        """锁定门锁 - 完整实现"""
        parameters = {}
        if pin_code:
            parameters["pin_code"] = pin_code

        return await self.send_command(
            MatterClusterId.DOOR_LOCK,
            MatterCommandId.DOOR_LOCK_LOCK_DOOR,
            parameters
        )

    async def unlock_door(self, pin_code: Optional[str] = None, timeout: int = None) -> bool:
        """解锁门锁 - 完整实现"""
        parameters = {}
        if pin_code:
            parameters["pin_code"] = pin_code
        if timeout is not None:
            parameters["timeout"] = timeout

        if timeout is not None:
            return await self.send_command(
                MatterClusterId.DOOR_LOCK,
                MatterCommandId.DOOR_LOCK_UNLOCK_WITH_TIMEOUT,
                parameters
            )
        else:
            return await self.send_command(
                MatterClusterId.DOOR_LOCK,
                MatterCommandId.DOOR_LOCK_UNLOCK_DOOR,
                parameters
            )

    async def toggle_door(self) -> bool:
        """切换门锁状态"""
        return await self.send_command(
            MatterClusterId.DOOR_LOCK,
            MatterCommandId.DOOR_LOCK_TOGGLE,
            {}
        )

    async def get_lock_state(self) -> Optional[str]:
        """获取门锁状态 - 完整实现"""
        value = await self.read_attribute(
            MatterClusterId.DOOR_LOCK,
            MatterAttributeId.DOOR_LOCK_LOCK_STATE
        )
        # Matter锁状态：0=NotFullyLocked, 1=Locked, 2=Unlocked
        state_map = {0: "NotFullyLocked", 1: "Locked", 2: "Unlocked"}
        return state_map.get(value, "Unknown") if value is not None else None

    async def get_door_state(self) -> Optional[str]:
        """获取门状态"""
        value = await self.read_attribute(
            MatterClusterId.DOOR_LOCK,
            MatterAttributeId.DOOR_LOCK_DOOR_STATE
        )
        # 0=Open, 1=Closed
        state_map = {0: "Open", 1: "Closed"}
        return state_map.get(value, "Unknown") if value is not None else None

    async def set_pin(self, user_id: int, user_status: int, user_type: int,
                     pin_code: str) -> bool:
        """设置PIN码"""
        return await self.send_command(
            MatterClusterId.DOOR_LOCK,
            MatterCommandId.DOOR_LOCK_SET_PIN,
            {
                "user_id": user_id,
                "user_status": user_status,
                "user_type": user_type,
                "pin_code": pin_code
            }
        )

    async def clear_pin(self, user_id: int) -> bool:
        """清除PIN码"""
        return await self.send_command(
            MatterClusterId.DOOR_LOCK,
            MatterCommandId.DOOR_LOCK_CLEAR_PIN,
            {"user_id": user_id}
        )

    async def get_log_record(self, log_index: int) -> Optional[Dict]:
        """获取日志记录"""
        result = await self.send_command(
            MatterClusterId.DOOR_LOCK,
            MatterCommandId.DOOR_LOCK_GET_LOG_RECORD,
            {"log_index": log_index}
        )
        return result if result else None

    async def set_weekday_schedule(self, user_id: int, schedule_id: int,
                                   days_mask: int, start_hour: int, start_minute: int,
                                   end_hour: int, end_minute: int) -> bool:
        """设置工作日计划"""
        return await self.send_command(
            MatterClusterId.DOOR_LOCK,
            MatterCommandId.DOOR_LOCK_SET_WEEKDAY_SCHEDULE,
            {
                "user_id": user_id,
                "schedule_id": schedule_id,
                "days_mask": days_mask,
                "start_hour": start_hour,
                "start_minute": start_minute,
                "end_hour": end_hour,
                "end_minute": end_minute
            }
        )

    async def get_weekday_schedule(self, user_id: int, schedule_id: int) -> Optional[Dict]:
        """获取工作日计划"""
        result = await self.send_command(
            MatterClusterId.DOOR_LOCK,
            MatterCommandId.DOOR_LOCK_GET_WEEKDAY_SCHEDULE,
            {
                "user_id": user_id,
                "schedule_id": schedule_id
            }
        )
        return result if result else None

    async def get_lock_info(self) -> Dict:
        """获取门锁完整信息"""
        lock_state = await self.get_lock_state()
        door_state = await self.get_door_state()

        # 读取其他属性
        lock_type = await self.read_attribute(
            MatterClusterId.DOOR_LOCK,
            MatterAttributeId.DOOR_LOCK_LOCK_TYPE
        )
        actuator_enabled = await self.read_attribute(
            MatterClusterId.DOOR_LOCK,
            MatterAttributeId.DOOR_LOCK_ACTUATOR_ENABLED
        )

        return {
            "lock_state": lock_state,
            "door_state": door_state,
            "lock_type": lock_type,
            "actuator_enabled": actuator_enabled
        }

class MatterThermostatController(MatterDeviceController):
    """Matter Thermostat控制器 - 完整实现"""

    async def set_target_temperature(self, temperature: float, mode: str = "Cool",
                                    occupied: bool = True) -> bool:
        """设置目标温度 - 完整实现"""
        temp_centidegrees = int(temperature * 100)  # Matter使用0.01°C单位

        if mode == "Cool":
            attribute_id = MatterAttributeId.THERMOSTAT_OCCUPIED_COOLING_SETPOINT if occupied else MatterAttributeId.THERMOSTAT_UNOCCUPIED_COOLING_SETPOINT
        elif mode == "Heat":
            attribute_id = MatterAttributeId.THERMOSTAT_OCCUPIED_HEATING_SETPOINT if occupied else MatterAttributeId.THERMOSTAT_UNOCCUPIED_HEATING_SETPOINT
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        return await self.write_attribute(
            MatterClusterId.THERMOSTAT,
            attribute_id,
            temp_centidegrees
        )

    async def get_current_temperature(self) -> Optional[float]:
        """获取当前温度 - 完整实现"""
        value = await self.read_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_LOCAL_TEMPERATURE
        )
        return value / 100.0 if value is not None else None

    async def get_outdoor_temperature(self) -> Optional[float]:
        """获取室外温度"""
        value = await self.read_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_OUTDOOR_TEMPERATURE
        )
        return value / 100.0 if value is not None else None

    async def set_system_mode(self, mode: str) -> bool:
        """设置系统模式 - 完整实现"""
        # Matter系统模式：0=Off, 1=Auto, 2=Cool, 3=Heat, 4=Emergency Heat, 5=Precooling, 6=Fan Only, 7=Dry, 8=Sleep
        mode_map = {
            "Off": 0,
            "Auto": 1,
            "Cool": 2,
            "Heat": 3,
            "EmergencyHeat": 4,
            "Precooling": 5,
            "FanOnly": 6,
            "Dry": 7,
            "Sleep": 8
        }
        return await self.write_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_SYSTEM_MODE,
            mode_map.get(mode, 1)
        )

    async def get_system_mode(self) -> Optional[str]:
        """获取系统模式"""
        value = await self.read_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_SYSTEM_MODE
        )
        mode_map = {
            0: "Off", 1: "Auto", 2: "Cool", 3: "Heat",
            4: "EmergencyHeat", 5: "Precooling", 6: "FanOnly",
            7: "Dry", 8: "Sleep"
        }
        return mode_map.get(value, "Unknown") if value is not None else None

    async def set_occupied_cooling_setpoint(self, temperature: float) -> bool:
        """设置占用时的制冷设定点"""
        return await self.write_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_OCCUPIED_COOLING_SETPOINT,
            int(temperature * 100)
        )

    async def set_occupied_heating_setpoint(self, temperature: float) -> bool:
        """设置占用时的制热设定点"""
        return await self.write_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_OCCUPIED_HEATING_SETPOINT,
            int(temperature * 100)
        )

    async def set_unoccupied_cooling_setpoint(self, temperature: float) -> bool:
        """设置未占用时的制冷设定点"""
        return await self.write_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_UNOCCUPIED_COOLING_SETPOINT,
            int(temperature * 100)
        )

    async def set_unoccupied_heating_setpoint(self, temperature: float) -> bool:
        """设置未占用时的制热设定点"""
        return await self.write_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_UNOCCUPIED_HEATING_SETPOINT,
            int(temperature * 100)
        )

    async def setpoint_raise_lower(self, mode: str, amount: int) -> bool:
        """提高或降低设定点"""
        # mode: "Heat" or "Cool"
        mode_value = 0 if mode == "Heat" else 1
        return await self.send_command(
            MatterClusterId.THERMOSTAT,
            MatterCommandId.THERMOSTAT_SETPOINT_RAISE_LOWER,
            {
                "mode": mode_value,
                "amount": amount
            }
        )

    async def set_weekly_schedule(self, number_of_transitions: int,
                                  day_of_week: int, mode: int,
                                  transitions: List[Dict]) -> bool:
        """设置每周计划"""
        return await self.send_command(
            MatterClusterId.THERMOSTAT,
            MatterCommandId.THERMOSTAT_SET_WEEKLY_SCHEDULE,
            {
                "number_of_transitions": number_of_transitions,
                "day_of_week": day_of_week,
                "mode": mode,
                "transitions": transitions
            }
        )

    async def get_weekly_schedule(self, days_to_return: int, mode: int) -> Optional[Dict]:
        """获取每周计划"""
        result = await self.send_command(
            MatterClusterId.THERMOSTAT,
            MatterCommandId.THERMOSTAT_GET_WEEKLY_SCHEDULE,
            {
                "days_to_return": days_to_return,
                "mode": mode
            }
        )
        return result if result else None

    async def clear_weekly_schedule(self) -> bool:
        """清除每周计划"""
        return await self.send_command(
            MatterClusterId.THERMOSTAT,
            MatterCommandId.THERMOSTAT_CLEAR_WEEKLY_SCHEDULE,
            {}
        )

    async def get_thermostat_info(self) -> Dict:
        """获取温控器完整信息"""
        current_temp = await self.get_current_temperature()
        outdoor_temp = await self.get_outdoor_temperature()
        system_mode = await self.get_system_mode()

        # 读取设定点
        occupied_cooling = await self.read_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_OCCUPIED_COOLING_SETPOINT
        )
        occupied_heating = await self.read_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_OCCUPIED_HEATING_SETPOINT
        )

        # 读取运行状态
        running_mode = await self.read_attribute(
            MatterClusterId.THERMOSTAT,
            MatterAttributeId.THERMOSTAT_THERMOSTAT_RUNNING_MODE
        )

        return {
            "current_temperature": current_temp,
            "outdoor_temperature": outdoor_temp,
            "system_mode": system_mode,
            "occupied_cooling_setpoint": occupied_cooling / 100.0 if occupied_cooling else None,
            "occupied_heating_setpoint": occupied_heating / 100.0 if occupied_heating else None,
            "running_mode": running_mode
        }
```

### 2.2 Matter到Zigbee转换

**转换规则**：

- Matter On/Off Cluster → Zigbee On/Off Cluster
- Matter Level Control Cluster → Zigbee Level Control Cluster
- Matter Color Control Cluster → Zigbee Color Control Cluster
- Matter Door Lock Cluster → Zigbee Door Lock Cluster
- Matter Thermostat Cluster → Zigbee Thermostat Cluster

**完整转换实现**：

详见 `Smart_Home_Schema/04_Transformation.md` 第2章。

---

## 3. Zigbee到Matter转换

**转换规则**：

- Zigbee On/Off Cluster → Matter On/Off Cluster
- Zigbee Level Control Cluster → Matter Level Control Cluster
- Zigbee Color Control Cluster → Matter Color Control Cluster
- Zigbee Door Lock Cluster → Matter Door Lock Cluster
- Zigbee Thermostat Cluster → Matter Thermostat Cluster

**完整转换实现**：

详见 `Smart_Home_Schema/04_Transformation.md` 第3章。

---

## 4. Matter设备发现和管理

### 4.1 设备发现实现

**完整的设备发现实现**：

```python
import asyncio
from typing import List, Dict, Optional
from matter_device_controller import MatterDeviceController

class MatterDeviceDiscovery:
    """Matter设备发现"""

    def __init__(self):
        self.discovered_devices: Dict[str, Dict] = {}

    async def discover_devices(self, timeout: int = 30) -> List[Dict]:
        """发现Matter设备"""
        logger.info("Starting Matter device discovery")

        # 这里需要实际的Matter SDK设备发现代码
        # 使用chip-device-ctrl或Matter SDK进行设备发现
        # 模拟设备发现过程
        devices = []

        # 模拟发现的设备
        sample_devices = [
            {
                "device_id": "LIGHT001",
                "device_type": "OnOffLight",
                "vendor_id": 0x1234,
                "product_id": 0x5678,
                "serial_number": "SN001",
                "firmware_version": "1.0.0"
            },
            {
                "device_id": "LOCK001",
                "device_type": "DoorLock",
                "vendor_id": 0x1234,
                "product_id": 0x5679,
                "serial_number": "SN002",
                "firmware_version": "1.0.0"
            }
        ]

        for device_info in sample_devices:
            devices.append(device_info)
            self.discovered_devices[device_info["device_id"]] = device_info

        logger.info(f"Discovered {len(devices)} Matter devices")
        return devices

    async def get_device_info(self, device_id: str) -> Optional[Dict]:
        """获取设备信息"""
        return self.discovered_devices.get(device_id)

class MatterDeviceManager:
    """Matter设备管理器"""

    def __init__(self, storage):
        self.storage = storage
        self.devices: Dict[str, MatterDeviceController] = {}
        self.discovery = MatterDeviceDiscovery()

    async def discover_and_register(self) -> List[str]:
        """发现并注册设备"""
        discovered = await self.discovery.discover_devices()
        registered_ids = []

        for device_info in discovered:
            # 存储设备信息
            self.storage.store_device(device_info)

            # 创建设备控制器
            controller = self._create_controller(device_info)
            if controller:
                self.devices[device_info["device_id"]] = controller
                registered_ids.append(device_info["device_id"])

        return registered_ids

    def _create_controller(self, device_info: Dict) -> Optional[MatterDeviceController]:
        """根据设备类型创建控制器"""
        device_type = device_info.get("device_type")

        if device_type == "OnOffLight":
            return MatterOnOffLightController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "DimmableLight":
            return MatterDimmableLightController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "ExtendedColorLight":
            return MatterColorLightController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "DoorLock":
            return MatterDoorLockController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        elif device_type == "Thermostat":
            return MatterThermostatController(
                device_info["device_id"],
                device_info.get("node_id", 0x12344321)
            )
        else:
            logger.warning(f"Unknown device type: {device_type}")
            return None

    async def connect_device(self, device_id: str) -> bool:
        """连接设备"""
        controller = self.devices.get(device_id)
        if not controller:
            logger.error(f"Device {device_id} not found")
            return False

        return await controller.connect()

    async def disconnect_device(self, device_id: str):
        """断开设备连接"""
        controller = self.devices.get(device_id)
        if controller:
            await controller.disconnect()

    def get_controller(self, device_id: str) -> Optional[MatterDeviceController]:
        """获取设备控制器"""
        return self.devices.get(device_id)
```

---

## 5. 转换工具

### 5.1 Matter SDK集成

**Matter SDK Python封装**：

详见 `Smart_Home_Schema/04_Transformation.md` 第5.1章。

### 5.2 CHIP Tool集成

**CHIP Tool命令行封装**：

```python
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class CHIPToolWrapper:
    """CHIP Tool命令行封装"""

    def __init__(self, chip_tool_path: str = "chip-tool"):
        self.chip_tool_path = chip_tool_path

    def read_attribute(self, node_id: int, endpoint_id: int,
                      cluster_name: str, attribute_name: str) -> Optional[Any]:
        """读取属性"""
        cmd = [
            self.chip_tool_path,
            "read",
            cluster_name,
            attribute_name,
            str(node_id),
            str(endpoint_id)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # 解析输出
                return self._parse_output(result.stdout)
            else:
                logger.error(f"CHIP Tool error: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Failed to read attribute: {e}")
            return None

    def write_attribute(self, node_id: int, endpoint_id: int,
                       cluster_name: str, attribute_name: str, value: Any) -> bool:
        """写入属性"""
        cmd = [
            self.chip_tool_path,
            "write",
            cluster_name,
            attribute_name,
            str(value),
            str(node_id),
            str(endpoint_id)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to write attribute: {e}")
            return False

    def send_command(self, node_id: int, endpoint_id: int,
                    cluster_name: str, command_name: str, *args) -> bool:
        """发送命令"""
        cmd = [
            self.chip_tool_path,
            cluster_name,
            command_name,
            str(node_id),
            str(endpoint_id),
            *[str(arg) for arg in args]
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def _parse_output(self, output: str) -> Optional[Any]:
        """解析CHIP Tool输出"""
        # 这里需要根据CHIP Tool的实际输出格式进行解析
        # 示例：解析JSON格式的输出
        try:
            # 尝试提取JSON部分
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = output[json_start:json_end]
                data = json.loads(json_str)
                return data.get("value")
        except Exception as e:
            logger.error(f"Failed to parse output: {e}")
        return None
```

---

## 6. 转换验证

### 6.1 转换正确性验证

**转换验证器实现**：

详见 `Smart_Home_Schema/04_Transformation.md` 第6章。

### 6.2 设备控制验证

**设备控制测试**：

```python
import pytest
from matter_device_controller import (
    MatterOnOffLightController,
    MatterDimmableLightController,
    MatterColorLightController
)

@pytest.mark.asyncio
async def test_on_off_light_control():
    """测试On/Off Light控制"""
    controller = MatterOnOffLightController("LIGHT001", 0x12344321)
    await controller.connect()

    # 测试打开
    result = await controller.turn_on()
    assert result == True

    # 测试获取状态
    state = await controller.get_state()
    assert state == True

    # 测试关闭
    result = await controller.turn_off()
    assert result == True

    # 测试切换
    result = await controller.toggle()
    assert result == True

    await controller.disconnect()

@pytest.mark.asyncio
async def test_dimmable_light_control():
    """测试Dimmable Light控制"""
    controller = MatterDimmableLightController("LIGHT002", 0x12344322)
    await controller.connect()

    # 测试设置亮度
    result = await controller.set_level(128)
    assert result == True

    # 测试获取亮度
    level = await controller.get_level()
    assert level == 128

    # 测试移动亮度
    result = await controller.move_level("Up", 10)
    assert result == True

    await controller.disconnect()

@pytest.mark.asyncio
async def test_color_light_control():
    """测试Color Light控制"""
    controller = MatterColorLightController("LIGHT003", 0x12344323)
    await controller.connect()

    # 测试设置色相和饱和度
    result = await controller.set_hue_saturation(120, 200)
    assert result == True

    # 测试设置色温
    result = await controller.set_color_temperature(400)
    assert result == True

    # 测试获取色温
    color_temp = await controller.get_color_temperature()
    assert color_temp == 400

    await controller.disconnect()
```

---

## 7. Matter数据存储与分析

### 7.1 PostgreSQL Matter数据存储

**Matter数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class MatterStorage:
    """Matter数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建Matter数据表"""
        # Matter设备表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_devices (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) UNIQUE NOT NULL,
                device_type VARCHAR(50) NOT NULL,
                device_name VARCHAR(100) NOT NULL,
                vendor_id INTEGER,
                product_id INTEGER,
                serial_number VARCHAR(100),
                firmware_version VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Matter集群表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_clusters (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                cluster_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id),
                UNIQUE(device_id, endpoint_id, cluster_id)
            )
        """)

        # Matter属性表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_attributes (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                attribute_id INTEGER NOT NULL,
                attribute_name VARCHAR(100),
                attribute_value JSONB,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id),
                UNIQUE(device_id, endpoint_id, cluster_id, attribute_id)
            )
        """)

        # Matter命令表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_commands (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                command_id INTEGER NOT NULL,
                command_name VARCHAR(100),
                command_parameters JSONB,
                command_status VARCHAR(20) DEFAULT 'Pending',
                executed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id)
            )
        """)

        # Matter事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_events (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                event_name VARCHAR(100),
                event_data JSONB,
                event_time TIMESTAMP NOT NULL,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id)
            )
        """)

        # Matter集群定义表（标准集群定义）
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_cluster_definitions (
                id BIGSERIAL PRIMARY KEY,
                cluster_id INTEGER UNIQUE NOT NULL,
                cluster_name VARCHAR(100) NOT NULL,
                cluster_description TEXT,
                cluster_version INTEGER DEFAULT 1,
                is_standard BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Matter属性定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_attribute_definitions (
                id BIGSERIAL PRIMARY KEY,
                cluster_id INTEGER NOT NULL,
                attribute_id INTEGER NOT NULL,
                attribute_name VARCHAR(100) NOT NULL,
                attribute_type VARCHAR(50),
                attribute_description TEXT,
                is_writable BOOLEAN DEFAULT FALSE,
                is_readable BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (cluster_id) REFERENCES matter_cluster_definitions(cluster_id),
                UNIQUE(cluster_id, attribute_id)
            )
        """)

        # Matter命令定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_command_definitions (
                id BIGSERIAL PRIMARY KEY,
                cluster_id INTEGER NOT NULL,
                command_id INTEGER NOT NULL,
                command_name VARCHAR(100) NOT NULL,
                command_description TEXT,
                command_parameters_schema JSONB,
                FOREIGN KEY (cluster_id) REFERENCES matter_cluster_definitions(cluster_id),
                UNIQUE(cluster_id, command_id)
            )
        """)

        # Matter设备组表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_device_groups (
                id BIGSERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL,
                group_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(group_id)
            )
        """)

        # Matter设备组成员表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_device_group_members (
                id BIGSERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES matter_device_groups(group_id),
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id),
                UNIQUE(group_id, device_id, endpoint_id)
            )
        """)

        # Matter固件升级表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_firmware_updates (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                firmware_version VARCHAR(50) NOT NULL,
                firmware_url TEXT,
                firmware_size BIGINT,
                firmware_checksum VARCHAR(64),
                update_status VARCHAR(20) DEFAULT 'Pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id)
            )
        """)

        # Matter设备状态历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_device_state_history (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) NOT NULL,
                endpoint_id INTEGER NOT NULL,
                cluster_id INTEGER NOT NULL,
                attribute_id INTEGER NOT NULL,
                attribute_value JSONB,
                recorded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id)
            )
        """)

        # Matter网络信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS matter_network_info (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(64) UNIQUE NOT NULL,
                fabric_id BIGINT,
                node_id INTEGER,
                mesh_local_address VARCHAR(64),
                network_type VARCHAR(20),
                ipv6_address VARCHAR(64),
                rssi INTEGER,
                lqi INTEGER,
                last_seen TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES matter_devices(device_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_devices_device_id
            ON matter_devices(device_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_devices_device_type
            ON matter_devices(device_type)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_clusters_device_id
            ON matter_clusters(device_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_clusters_cluster_id
            ON matter_clusters(cluster_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_attributes_device_id
            ON matter_attributes(device_id, updated_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_attributes_cluster
            ON matter_attributes(device_id, endpoint_id, cluster_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_commands_device_id
            ON matter_commands(device_id, created_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_commands_status
            ON matter_commands(command_status, created_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_events_device_id
            ON matter_events(device_id, event_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_events_cluster
            ON matter_events(cluster_id, event_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_device_state_history_device
            ON matter_device_state_history(device_id, recorded_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_firmware_updates_device
            ON matter_firmware_updates(device_id, created_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_matter_firmware_updates_status
            ON matter_firmware_updates(update_status)
        """)

        self.conn.commit()

    def store_device(self, device_data: Dict) -> int:
        """存储Matter设备"""
        self.cur.execute("""
            INSERT INTO matter_devices (
                device_id, device_type, device_name, vendor_id,
                product_id, serial_number, firmware_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_id) DO UPDATE SET
                device_type = EXCLUDED.device_type,
                device_name = EXCLUDED.device_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            device_data.get("device_id"),
            device_data.get("device_type"),
            device_data.get("device_name"),
            device_data.get("vendor_id"),
            device_data.get("product_id"),
            device_data.get("serial_number"),
            device_data.get("firmware_version")
        ))
        return self.cur.fetchone()[0]

    def store_attribute(self, device_id: str, endpoint_id: int,
                       cluster_id: int, attribute_id: int,
                       attribute_name: str, attribute_value: Dict) -> int:
        """存储Matter属性"""
        self.cur.execute("""
            INSERT INTO matter_attributes (
                device_id, endpoint_id, cluster_id, attribute_id,
                attribute_name, attribute_value
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id, endpoint_id, cluster_id, attribute_id)
            DO UPDATE SET
                attribute_value = EXCLUDED.attribute_value,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (device_id, endpoint_id, cluster_id, attribute_id,
              attribute_name, json.dumps(attribute_value)))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_command(self, device_id: str, endpoint_id: int,
                     cluster_id: int, command_id: int,
                     command_name: str, parameters: Dict = None) -> int:
        """存储Matter命令"""
        self.cur.execute("""
            INSERT INTO matter_commands (
                device_id, endpoint_id, cluster_id, command_id,
                command_name, command_parameters, command_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, 'Pending', CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            device_id, endpoint_id, cluster_id, command_id,
            command_name, json.dumps(parameters or {})
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def update_command_status(self, command_db_id: int, status: str):
        """更新命令状态"""
        self.cur.execute("""
            UPDATE matter_commands
            SET command_status = %s, executed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (status, command_db_id))
        self.conn.commit()

    def store_event(self, device_id: str, endpoint_id: int,
                   cluster_id: int, event_id: int,
                   event_name: str, event_data: Dict = None) -> int:
        """存储Matter事件"""
        self.cur.execute("""
            INSERT INTO matter_events (
                device_id, endpoint_id, cluster_id, event_id,
                event_name, event_data, event_time
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            device_id, endpoint_id, cluster_id, event_id,
            event_name, json.dumps(event_data or {})
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_device_clusters(self, device_id: str) -> List[Dict]:
        """获取设备的所有集群"""
        self.cur.execute("""
            SELECT cluster_id, cluster_name, endpoint_id
            FROM matter_clusters
            WHERE device_id = %s
            ORDER BY endpoint_id, cluster_id
        """, (device_id,))
        return [
            {
                "cluster_id": row[0],
                "cluster_name": row[1],
                "endpoint_id": row[2]
            }
            for row in self.cur.fetchall()
        ]

    def get_cluster_attributes(self, device_id: str, endpoint_id: int,
                              cluster_id: int) -> List[Dict]:
        """获取集群的所有属性"""
        self.cur.execute("""
            SELECT attribute_id, attribute_name, attribute_value, updated_at
            FROM matter_attributes
            WHERE device_id = %s AND endpoint_id = %s AND cluster_id = %s
            ORDER BY attribute_id
        """, (device_id, endpoint_id, cluster_id))
        return [
            {
                "attribute_id": row[0],
                "attribute_name": row[1],
                "attribute_value": json.loads(row[2]) if row[2] else None,
                "updated_at": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def store_cluster_definition(self, cluster_id: int, cluster_name: str,
                                 cluster_description: str = None,
                                 cluster_version: int = 1) -> int:
        """存储集群定义"""
        self.cur.execute("""
            INSERT INTO matter_cluster_definitions (
                cluster_id, cluster_name, cluster_description, cluster_version
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (cluster_id) DO UPDATE SET
                cluster_name = EXCLUDED.cluster_name,
                cluster_description = EXCLUDED.cluster_description,
                cluster_version = EXCLUDED.cluster_version
            RETURNING id
        """, (cluster_id, cluster_name, cluster_description, cluster_version))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_attribute_definition(self, cluster_id: int, attribute_id: int,
                                   attribute_name: str, attribute_type: str = None,
                                   is_writable: bool = False,
                                   is_readable: bool = True) -> int:
        """存储属性定义"""
        self.cur.execute("""
            INSERT INTO matter_attribute_definitions (
                cluster_id, attribute_id, attribute_name, attribute_type,
                is_writable, is_readable
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (cluster_id, attribute_id) DO UPDATE SET
                attribute_name = EXCLUDED.attribute_name,
                attribute_type = EXCLUDED.attribute_type,
                is_writable = EXCLUDED.is_writable,
                is_readable = EXCLUDED.is_readable
            RETURNING id
        """, (cluster_id, attribute_id, attribute_name, attribute_type,
              is_writable, is_readable))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_command_definition(self, cluster_id: int, command_id: int,
                                command_name: str,
                                command_parameters_schema: Dict = None) -> int:
        """存储命令定义"""
        self.cur.execute("""
            INSERT INTO matter_command_definitions (
                cluster_id, command_id, command_name, command_parameters_schema
            ) VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (cluster_id, command_id) DO UPDATE SET
                command_name = EXCLUDED.command_name,
                command_parameters_schema = EXCLUDED.command_parameters_schema
            RETURNING id
        """, (cluster_id, command_id, command_name,
              json.dumps(command_parameters_schema or {})))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def create_device_group(self, group_id: int, group_name: str) -> int:
        """创建设备组"""
        self.cur.execute("""
            INSERT INTO matter_device_groups (group_id, group_name)
            VALUES (%s, %s)
            ON CONFLICT (group_id) DO UPDATE SET
                group_name = EXCLUDED.group_name
            RETURNING id
        """, (group_id, group_name))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def add_device_to_group(self, group_id: int, device_id: str,
                           endpoint_id: int = 1) -> int:
        """添加设备到组"""
        self.cur.execute("""
            INSERT INTO matter_device_group_members (group_id, device_id, endpoint_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (group_id, device_id, endpoint_id) DO NOTHING
            RETURNING id
        """, (group_id, device_id, endpoint_id))
        self.conn.commit()
        result = self.cur.fetchone()
        return result[0] if result else None

    def get_group_devices(self, group_id: int) -> List[Dict]:
        """获取组内所有设备"""
        self.cur.execute("""
            SELECT d.device_id, d.device_type, d.device_name, g.endpoint_id
            FROM matter_device_group_members g
            JOIN matter_devices d ON g.device_id = d.device_id
            WHERE g.group_id = %s
            ORDER BY d.device_id
        """, (group_id,))
        return [
            {
                "device_id": row[0],
                "device_type": row[1],
                "device_name": row[2],
                "endpoint_id": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def store_firmware_update(self, device_id: str, firmware_version: str,
                             firmware_url: str = None, firmware_size: int = None,
                             firmware_checksum: str = None) -> int:
        """存储固件升级记录"""
        self.cur.execute("""
            INSERT INTO matter_firmware_updates (
                device_id, firmware_version, firmware_url, firmware_size,
                firmware_checksum, update_status, started_at
            ) VALUES (%s, %s, %s, %s, %s, 'Pending', CURRENT_TIMESTAMP)
            RETURNING id
        """, (device_id, firmware_version, firmware_url, firmware_size,
              firmware_checksum))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def update_firmware_status(self, update_id: int, status: str,
                               error_message: str = None):
        """更新固件升级状态"""
        if status == 'Completed':
            self.cur.execute("""
                UPDATE matter_firmware_updates
                SET update_status = %s, completed_at = CURRENT_TIMESTAMP,
                    error_message = %s
                WHERE id = %s
            """, (status, error_message, update_id))
        elif status == 'Failed':
            self.cur.execute("""
                UPDATE matter_firmware_updates
                SET update_status = %s, completed_at = CURRENT_TIMESTAMP,
                    error_message = %s
                WHERE id = %s
            """, (status, error_message, update_id))
        else:
            self.cur.execute("""
                UPDATE matter_firmware_updates
                SET update_status = %s, error_message = %s
                WHERE id = %s
            """, (status, error_message, update_id))
        self.conn.commit()

    def store_device_state_history(self, device_id: str, endpoint_id: int,
                                  cluster_id: int, attribute_id: int,
                                  attribute_value: Dict):
        """存储设备状态历史"""
        self.cur.execute("""
            INSERT INTO matter_device_state_history (
                device_id, endpoint_id, cluster_id, attribute_id,
                attribute_value, recorded_at
            ) VALUES (%s, %s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
        """, (device_id, endpoint_id, cluster_id, attribute_id,
              json.dumps(attribute_value)))
        self.conn.commit()

    def store_network_info(self, device_id: str, fabric_id: int = None,
                          node_id: int = None, mesh_local_address: str = None,
                          network_type: str = None, ipv6_address: str = None,
                          rssi: int = None, lqi: int = None):
        """存储网络信息"""
        self.cur.execute("""
            INSERT INTO matter_network_info (
                device_id, fabric_id, node_id, mesh_local_address,
                network_type, ipv6_address, rssi, lqi, last_seen
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (device_id) DO UPDATE SET
                fabric_id = EXCLUDED.fabric_id,
                node_id = EXCLUDED.node_id,
                mesh_local_address = EXCLUDED.mesh_local_address,
                network_type = EXCLUDED.network_type,
                ipv6_address = EXCLUDED.ipv6_address,
                rssi = EXCLUDED.rssi,
                lqi = EXCLUDED.lqi,
                last_seen = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
        """, (device_id, fabric_id, node_id, mesh_local_address,
              network_type, ipv6_address, rssi, lqi))
        self.conn.commit()

    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        """根据ID获取设备"""
        self.cur.execute("""
            SELECT device_id, device_type, device_name, vendor_id, product_id,
                   serial_number, firmware_version, created_at, updated_at
            FROM matter_devices
            WHERE device_id = %s
        """, (device_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "device_id": row[0],
                "device_type": row[1],
                "device_name": row[2],
                "vendor_id": row[3],
                "product_id": row[4],
                "serial_number": row[5],
                "firmware_version": row[6],
                "created_at": row[7],
                "updated_at": row[8]
            }
        return None

    def get_all_devices(self, device_type: str = None) -> List[Dict]:
        """获取所有设备"""
        if device_type:
            self.cur.execute("""
                SELECT device_id, device_type, device_name, vendor_id, product_id,
                       serial_number, firmware_version, created_at
                FROM matter_devices
                WHERE device_type = %s
                ORDER BY device_id
            """, (device_type,))
        else:
            self.cur.execute("""
                SELECT device_id, device_type, device_name, vendor_id, product_id,
                       serial_number, firmware_version, created_at
                FROM matter_devices
                ORDER BY device_id
            """)
        return [
            {
                "device_id": row[0],
                "device_type": row[1],
                "device_name": row[2],
                "vendor_id": row[3],
                "product_id": row[4],
                "serial_number": row[5],
                "firmware_version": row[6],
                "created_at": row[7]
            }
            for row in self.cur.fetchall()
        ]

    def get_device_state_history(self, device_id: str, cluster_id: int = None,
                                attribute_id: int = None,
                                start_time: datetime = None,
                                end_time: datetime = None,
                                limit: int = 1000) -> List[Dict]:
        """获取设备状态历史"""
        query = """
            SELECT endpoint_id, cluster_id, attribute_id, attribute_value, recorded_at
            FROM matter_device_state_history
            WHERE device_id = %s
        """
        params = [device_id]

        if cluster_id:
            query += " AND cluster_id = %s"
            params.append(cluster_id)

        if attribute_id:
            query += " AND attribute_id = %s"
            params.append(attribute_id)

        if start_time:
            query += " AND recorded_at >= %s"
            params.append(start_time)

        if end_time:
            query += " AND recorded_at <= %s"
            params.append(end_time)

        query += " ORDER BY recorded_at DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, tuple(params))
        return [
            {
                "endpoint_id": row[0],
                "cluster_id": row[1],
                "attribute_id": row[2],
                "attribute_value": json.loads(row[3]) if row[3] else None,
                "recorded_at": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def get_firmware_updates(self, device_id: str = None,
                            status: str = None) -> List[Dict]:
        """获取固件升级记录"""
        query = "SELECT * FROM matter_firmware_updates WHERE 1=1"
        params = []

        if device_id:
            query += " AND device_id = %s"
            params.append(device_id)

        if status:
            query += " AND update_status = %s"
            params.append(status)

        query += " ORDER BY created_at DESC"

        self.cur.execute(query, tuple(params))
        columns = [desc[0] for desc in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur.fetchall()]

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 7.2 Matter数据分析查询

**查询示例**：

```python
    def get_cluster_statistics(self, device_id: str) -> List[Dict]:
        """查询设备集群统计"""
        self.cur.execute("""
            SELECT
                c.cluster_id,
                c.cluster_name,
                COUNT(DISTINCT a.attribute_id) as attribute_count,
                COUNT(DISTINCT cmd.command_id) as command_count,
                MAX(a.updated_at) as last_attribute_update
            FROM matter_clusters c
            LEFT JOIN matter_attributes a
            ON c.device_id = a.device_id AND c.cluster_id = a.cluster_id
            LEFT JOIN matter_commands cmd
            ON c.device_id = cmd.device_id AND c.cluster_id = cmd.cluster_id
            WHERE c.device_id = %s
            GROUP BY c.cluster_id, c.cluster_name
            ORDER BY c.cluster_id
        """, (device_id,))
        return [
            {
                "cluster_id": row[0],
                "cluster_name": row[1],
                "attribute_count": row[2],
                "command_count": row[3],
                "last_attribute_update": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def get_command_statistics(self, start_time: datetime) -> List[Dict]:
        """查询命令执行统计"""
        self.cur.execute("""
            SELECT
                command_name,
                command_status,
                COUNT(*) as count,
                AVG(EXTRACT(EPOCH FROM (executed_at - created_at))) as avg_execution_time_seconds,
                MIN(EXTRACT(EPOCH FROM (executed_at - created_at))) as min_execution_time_seconds,
                MAX(EXTRACT(EPOCH FROM (executed_at - created_at))) as max_execution_time_seconds
            FROM matter_commands
            WHERE created_at >= %s AND executed_at IS NOT NULL
            GROUP BY command_name, command_status
            ORDER BY command_name, command_status
        """, (start_time,))
        return [
            {
                "command_name": row[0],
                "command_status": row[1],
                "count": row[2],
                "avg_execution_time": row[3],
                "min_execution_time": row[4],
                "max_execution_time": row[5]
            }
            for row in self.cur.fetchall()
        ]

    def get_device_event_statistics(self, device_id: str, days: int = 7) -> List[Dict]:
        """查询设备事件统计"""
        self.cur.execute("""
            SELECT
                event_name,
                COUNT(*) as event_count,
                MIN(event_time) as first_event,
                MAX(event_time) as last_event
            FROM matter_events
            WHERE device_id = %s
            AND event_time >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY event_name
            ORDER BY event_count DESC
        """, (device_id, days))
        return [
            {
                "event_name": row[0],
                "event_count": row[1],
                "first_event": row[2],
                "last_event": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def get_attribute_history(self, device_id: str, endpoint_id: int,
                             cluster_id: int, attribute_id: int,
                             hours: int = 24) -> List[Dict]:
        """查询属性历史变化"""
        # 注意：这里需要属性历史表，当前实现仅查询最新值
        self.cur.execute("""
            SELECT
                attribute_name,
                attribute_value,
                updated_at
            FROM matter_attributes
            WHERE device_id = %s
            AND endpoint_id = %s
            AND cluster_id = %s
            AND attribute_id = %s
            AND updated_at >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
            ORDER BY updated_at DESC
        """, (device_id, endpoint_id, cluster_id, attribute_id, hours))
        return [
            {
                "attribute_name": row[0],
                "attribute_value": json.loads(row[1]) if row[1] else None,
                "updated_at": row[2]
            }
            for row in self.cur.fetchall()
        ]

    def get_device_usage_statistics(self, device_id: str, days: int = 7) -> Dict:
        """查询设备使用统计"""
        self.cur.execute("""
            SELECT
                COUNT(DISTINCT DATE(created_at)) as active_days,
                COUNT(*) as total_commands,
                COUNT(CASE WHEN command_status = 'Success' THEN 1 END) as success_commands,
                COUNT(CASE WHEN command_status = 'Failed' THEN 1 END) as failed_commands,
                AVG(EXTRACT(EPOCH FROM (executed_at - created_at))) as avg_response_time_seconds
            FROM matter_commands
            WHERE device_id = %s
            AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND executed_at IS NOT NULL
        """, (device_id, days))
        row = self.cur.fetchone()
        return {
            "active_days": row[0],
            "total_commands": row[1],
            "success_commands": row[2],
            "failed_commands": row[3],
            "avg_response_time": row[4]
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
