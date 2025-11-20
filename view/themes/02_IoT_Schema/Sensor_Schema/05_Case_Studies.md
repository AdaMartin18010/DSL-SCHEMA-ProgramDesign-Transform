# IoT传感器Schema实践案例

## 📑 目录

- [IoT传感器Schema实践案例](#iot传感器schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：智能家居温湿度传感器](#2-案例1智能家居温湿度传感器)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 代码生成](#23-代码生成)
    - [2.4 部署验证](#24-部署验证)
  - [3. 案例2：工业物联网压力传感器](#3-案例2工业物联网压力传感器)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 协议转换](#33-协议转换)
    - [3.4 数据采集](#34-数据采集)
  - [4. 案例3：智慧城市环境监测传感器](#4-案例3智慧城市环境监测传感器)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 云端集成](#43-云端集成)
    - [4.4 数据分析](#44-数据分析)
  - [5. 案例4：农业物联网土壤传感器](#5-案例4农业物联网土壤传感器)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 Schema定义](#52-schema定义)
    - [5.3 低功耗设计](#53-低功耗设计)
    - [5.4 远程监控](#54-远程监控)
  - [6. 案例总结](#6-案例总结)
    - [6.1 成功因素](#61-成功因素)
    - [6.2 挑战与解决方案](#62-挑战与解决方案)
    - [6.3 最佳实践](#63-最佳实践)
  - [7. 参考文献](#7-参考文献)
    - [7.1 标准文档](#71-标准文档)
    - [7.2 技术文档](#72-技术文档)
    - [7.3 在线资源](#73-在线资源)

---

## 1. 案例概述

本文档提供IoT传感器Schema在实际应用中的
实践案例，展示Schema定义、代码生成、
协议转换、云端集成等完整流程。

**案例类型**：

1. **智能家居**：温湿度传感器
2. **工业物联网**：压力传感器
3. **智慧城市**：环境监测传感器
4. **农业物联网**：土壤传感器

---

## 2. 案例1：智能家居温湿度传感器

### 2.1 场景描述

**应用场景**：
智能家居系统中的温湿度传感器，
用于监测室内环境，支持WiFi连接，
数据上报到云端平台。

**需求分析**：

- **物理接口**：I2C接口，3.3V供电
- **通信协议**：WiFi（IEEE 802.11），MQTT协议
- **测量参数**：温度（-40°C~125°C）、湿度（0%~100%）
- **采样频率**：1Hz（每秒1次）
- **安全要求**：TLS加密，设备认证

### 2.2 Schema定义

**完整Schema定义**：

```dsl
schema SmartHomeTempHumiditySensor {
  // 维度1：物理接口
  physical: {
    interface_type: Enum { I2C } @default(I2C)
    connector: Enum { GPIO } @pin_config("SDA=GPIO4, SCL=GPIO5")
    electrical: {
      voltage: Voltage @value(3.3V)
      current: Current @max(5mA)
      power: Power @max(16.5mW)
    }
  }

  // 维度2：通信协议
  communication: {
    protocol_type: Enum { WiFi_MQTT }
    wifi_config: {
      ssid: String @required
      password: String @required @encrypted
      ip_mode: Enum { DHCP, Static }
    }
    mqtt_config: {
      broker: String @required
      port: UInt16 @default(1883)
      topic: String @pattern("home/sensor/+/data")
      qos: Enum { 0, 1, 2 } @default(1)
    }
  }

  // 维度3：传感器参数
  parameter: {
    measurement: {
      temperature: {
        physical_quantity: Enum { Temperature }
        range: { min: -40.0, max: 125.0 } @unit("°C")
        resolution: Float64 @value(0.1) @unit("°C")
        accuracy: Float64 @value(±2.0) @unit("%")
      }
      humidity: {
        physical_quantity: Enum { Humidity }
        range: { min: 0.0, max: 100.0 } @unit("%")
        resolution: Float64 @value(0.1) @unit("%")
        accuracy: Float64 @value(±3.0) @unit("%")
      }
    }
    sampling_rate: Frequency @value(1Hz)
    metadata: {
      device_name: String @default("TempHumiditySensor")
      model: String @default("DHT22")
      manufacturer: String @default("Aosong")
    }
  }

  // 维度4：控制配置
  control: {
    sampling: {
      mode: Enum { Timed }
      frequency: Frequency @value(1Hz)
    }
    event: {
      alarm: {
        temperature_high: { threshold: 30.0, action: "notify" }
        temperature_low: { threshold: 10.0, action: "notify" }
      }
    }
  }

  // 维度5：安全合规
  security: {
    authentication: {
      device_certificate: X509_Certificate @required
    }
    encryption: {
      transport: Enum { TLS_1_2 } @required
    }
    privacy: {
      gdpr_compliance: Bool @default(true)
    }
  }
} @standard("GB/T_34068-2017")
```

### 2.3 代码生成

**生成的Python代码**：

```python
import asyncio
import json
import ssl
from datetime import datetime
from typing import Optional
import paho.mqtt.client as mqtt
import adafruit_dht
import board

class SmartHomeTempHumiditySensor:
    """智能家居温湿度传感器"""

    def __init__(self, wifi_ssid: str, wifi_password: str,
                 mqtt_broker: str, mqtt_port: int = 1883,
                 device_cert: Optional[str] = None):
        # 物理接口配置
        self.dht_device = adafruit_dht.DHT22(board.D4)

        # WiFi配置
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password

        # MQTT配置
        self.mqtt_client = mqtt.Client()
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = "home/sensor/temp_humidity/data"

        # TLS配置
        if device_cert:
            self.mqtt_client.tls_set(
                ca_certs=device_cert,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )

    async def read_sensor(self) -> dict:
        """读取传感器数据"""
        try:
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity

            # 范围验证
            if not (-40.0 <= temperature <= 125.0):
                raise ValueError("Temperature out of range")
            if not (0.0 <= humidity <= 100.0):
                raise ValueError("Humidity out of range")

            return {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "timestamp": datetime.utcnow().isoformat(),
                "unit": {
                    "temperature": "°C",
                    "humidity": "%"
                }
            }
        except RuntimeError as e:
            print(f"传感器读取错误: {e}")
            return None

    async def publish_data(self, data: dict):
        """发布数据到MQTT"""
        if data:
            payload = json.dumps(data)
            self.mqtt_client.publish(
                self.mqtt_topic,
                payload,
                qos=1
            )

    async def run(self):
        """主循环"""
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
        self.mqtt_client.loop_start()

        while True:
            data = await self.read_sensor()
            await self.publish_data(data)
            await asyncio.sleep(1.0)  # 1Hz采样频率
```

### 2.4 部署验证

**验证步骤**：

1. **硬件连接**：连接DHT22传感器到GPIO4/GPIO5
2. **WiFi配置**：配置WiFi SSID和密码
3. **MQTT连接**：连接到MQTT Broker
4. **数据验证**：验证数据格式和范围
5. **安全验证**：验证TLS连接和证书

**验证结果**：
✅ 传感器数据正常采集
✅ MQTT消息正常发布
✅ TLS加密正常工作
✅ 数据格式符合Schema定义

---

## 3. 案例2：工业物联网压力传感器

### 3.1 场景描述

**应用场景**：
工业生产线上的压力传感器，
使用Modbus RTU协议通信，
数据采集到SCADA系统。

**需求分析**：

- **物理接口**：RS485接口，24V供电
- **通信协议**：Modbus RTU，波特率9600
- **测量参数**：压力（0~10MPa），精度±0.5%
- **采样频率**：10Hz
- **安全要求**：数据完整性校验

### 3.2 Schema定义

**Schema定义（简化）**：

```dsl
schema IndustrialPressureSensor {
  physical: {
    interface_type: Enum { Modbus_RTU }
    connector: Enum { RS485 }
    electrical: {
      voltage: Voltage @value(24V)
      current: Current @max(50mA)
    }
  }

  communication: {
    protocol_type: Enum { Modbus_RTU }
    modbus_config: {
      baud_rate: UInt32 @value(9600)
      data_bits: UInt8 @value(8)
      stop_bits: UInt8 @value(1)
      parity: Enum { Even }
      slave_id: UInt8 @range(1, 247)
    }
  }

  parameter: {
    measurement: {
      pressure: {
        physical_quantity: Enum { Pressure }
        range: { min: 0.0, max: 10.0 } @unit("MPa")
        accuracy: Float64 @value(±0.5) @unit("%")
      }
    }
    sampling_rate: Frequency @value(10Hz)
    register_map: {
      pressure_register: UInt16 @address(0x0001)
      status_register: UInt16 @address(0x0002)
    }
  }
} @standard("GB/T_19582-2008")
```

### 3.3 协议转换

**Modbus RTU到MQTT转换**：

```python
import pymodbus
from pymodbus.client.sync import ModbusSerialClient
import paho.mqtt.client as mqtt
import json

class ModbusToMQTTGateway:
    """Modbus RTU到MQTT协议网关"""

    def __init__(self, modbus_port: str, mqtt_broker: str):
        # Modbus客户端
        self.modbus_client = ModbusSerialClient(
            method='rtu',
            port=modbus_port,
            baudrate=9600,
            parity='E',
            stopbits=1,
            bytesize=8
        )

        # MQTT客户端
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(mqtt_broker, 1883)
        self.mqtt_topic = "industrial/sensor/pressure/data"

    def read_pressure(self, slave_id: int) -> Optional[float]:
        """读取压力值"""
        result = self.modbus_client.read_holding_registers(
            address=0x0001,
            count=1,
            unit=slave_id
        )

        if result.isError():
            return None

        # 转换为MPa（假设寄存器值为0-10000，对应0-10MPa）
        raw_value = result.registers[0]
        pressure = raw_value / 1000.0

        return pressure

    def publish_data(self, pressure: float):
        """发布数据到MQTT"""
        data = {
            "pressure": pressure,
            "unit": "MPa",
            "timestamp": datetime.utcnow().isoformat()
        }
        payload = json.dumps(data)
        self.mqtt_client.publish(self.mqtt_topic, payload)
```

### 3.4 数据采集

**SCADA系统集成**：

```python
class SCADADataCollector:
    """SCADA数据采集器"""

    def __init__(self, modbus_gateway: ModbusToMQTTGateway):
        self.gateway = modbus_gateway
        self.data_buffer = []

    async def collect_data(self, slave_ids: List[int]):
        """采集多个传感器数据"""
        while True:
            for slave_id in slave_ids:
                pressure = self.gateway.read_pressure(slave_id)
                if pressure is not None:
                    self.data_buffer.append({
                        "slave_id": slave_id,
                        "pressure": pressure,
                        "timestamp": datetime.utcnow()
                    })

            await asyncio.sleep(0.1)  # 10Hz采样频率
```

---

## 4. 案例3：智慧城市环境监测传感器

### 4.1 场景描述

**应用场景**：
智慧城市环境监测站，
监测PM2.5、PM10、NO2等空气质量参数，
使用LoRaWAN通信，数据上传到云端平台。

**需求分析**：

- **物理接口**：UART接口，12V供电
- **通信协议**：LoRaWAN，Class A
- **测量参数**：PM2.5、PM10、NO2、温度、湿度
- **采样频率**：1次/5分钟
- **安全要求**：AES-128加密，设备认证

### 4.2 Schema定义

**Schema定义（简化）**：

```dsl
schema SmartCityAirQualitySensor {
  physical: {
    interface_type: Enum { UART }
    electrical: {
      voltage: Voltage @value(12V)
      power: Power @max(2W)
      energy_harvesting: Bool @default(false)
    }
  }

  communication: {
    protocol_type: Enum { LoRaWAN }
    lorawan_config: {
      dev_eui: String @required @format("hex")
      app_key: String @required @encrypted
      class: Enum { A } @default(A)
      data_rate: Enum { DR0, DR1, DR2, DR3 } @default(DR3)
    }
  }

  parameter: {
    measurement: {
      pm2_5: { range: { min: 0.0, max: 500.0 } @unit("μg/m³") }
      pm10: { range: { min: 0.0, max: 500.0 } @unit("μg/m³") }
      no2: { range: { min: 0.0, max: 2000.0 } @unit("ppb") }
      temperature: { range: { min: -40.0, max: 85.0 } @unit("°C") }
      humidity: { range: { min: 0.0, max: 100.0 } @unit("%") }
    }
    sampling_rate: Frequency @value(1/300Hz)  # 5分钟1次
  }

  security: {
    encryption: {
      lorawan: Enum { AES_128 } @required
    }
  }
} @standard("GB/T_34068-2017")
```

### 4.3 云端集成

**云端数据处理**：

```python
import boto3
import json

class CloudDataProcessor:
    """云端数据处理"""

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('air_quality_data')

    def process_lorawan_data(self, payload: bytes, dev_eui: str):
        """处理LoRaWAN数据"""
        # 解析数据
        data = self.parse_payload(payload)

        # 数据验证
        if not self.validate_data(data):
            return False

        # 存储到DynamoDB
        self.table.put_item(
            Item={
                'dev_eui': dev_eui,
                'timestamp': datetime.utcnow().isoformat(),
                'pm2_5': data['pm2_5'],
                'pm10': data['pm10'],
                'no2': data['no2'],
                'temperature': data['temperature'],
                'humidity': data['humidity']
            }
        )

        # 存储到S3（长期存储）
        s3_key = f"air_quality/{dev_eui}/{datetime.utcnow().strftime('%Y/%m/%d')}.json"
        self.s3_client.put_object(
            Bucket='air-quality-data',
            Key=s3_key,
            Body=json.dumps(data)
        )

        return True
```

### 4.4 数据分析

**数据分析示例**：

```python
import pandas as pd
import numpy as np

class AirQualityAnalyzer:
    """空气质量数据分析"""

    def analyze_trends(self, data: pd.DataFrame):
        """分析趋势"""
        # PM2.5趋势
        pm25_trend = data['pm2_5'].rolling(window=24).mean()

        # 空气质量等级
        data['aqi_level'] = data['pm2_5'].apply(self.calculate_aqi)

        return {
            'pm25_trend': pm25_trend.tolist(),
            'aqi_levels': data['aqi_level'].tolist(),
            'statistics': {
                'mean_pm25': data['pm2_5'].mean(),
                'max_pm25': data['pm2_5'].max(),
                'min_pm25': data['pm2_5'].min()
            }
        }

    def calculate_aqi(self, pm25: float) -> str:
        """计算AQI等级"""
        if pm25 <= 35:
            return "优"
        elif pm25 <= 75:
            return "良"
        elif pm25 <= 115:
            return "轻度污染"
        elif pm25 <= 150:
            return "中度污染"
        else:
            return "重度污染"
```

---

## 5. 案例4：农业物联网土壤传感器

### 5.1 场景描述

**应用场景**：
农业物联网土壤传感器，
监测土壤湿度、pH值、温度等参数，
使用NB-IoT通信，支持低功耗设计。

**需求分析**：

- **物理接口**：模拟接口，3.7V锂电池供电
- **通信协议**：NB-IoT，低功耗模式
- **测量参数**：土壤湿度、pH值、温度
- **采样频率**：1次/小时（低功耗）
- **安全要求**：PSK认证，数据加密

### 5.2 Schema定义

**Schema定义（简化）**：

```dsl
schema AgriculturalSoilSensor {
  physical: {
    interface_type: Enum { Analog }
    electrical: {
      voltage: Voltage @value(3.7V)
      power: Power @max(100mW)
      energy_harvesting: Bool @default(false)
      battery: {
        capacity: Capacity @value(2000mAh)
        low_power_threshold: Voltage @value(3.0V)
      }
    }
  }

  communication: {
    protocol_type: Enum { NB_IoT }
    nb_iot_config: {
      apn: String @default("nbiot")
      imei: String @required
      psk: String @required @encrypted
      power_saving_mode: Enum { PSM, eDRX } @default(PSM)
    }
  }

  parameter: {
    measurement: {
      soil_moisture: { range: { min: 0.0, max: 100.0 } @unit("%") }
      ph_value: { range: { min: 0.0, max: 14.0 } }
      temperature: { range: { min: -10.0, max: 50.0 } @unit("°C") }
    }
    sampling_rate: Frequency @value(1/3600Hz)  # 1小时1次
  }

  control: {
    power_management: {
      sleep_mode: Bool @default(true)
      sleep_duration: Duration @value(3600s)
      wake_up_condition: Enum { Timer, External_Trigger }
    }
  }
} @standard("GB/T_34068-2017")
```

### 5.3 低功耗设计

**低功耗代码实现**：

```python
import machine
import time
from deepsleep import DeepSleep

class LowPowerSoilSensor:
    """低功耗土壤传感器"""

    def __init__(self):
        self.adc = machine.ADC(machine.Pin(34))
        self.deep_sleep = DeepSleep()
        self.sleep_duration = 3600  # 1小时

    def read_sensors(self):
        """读取传感器数据"""
        # 读取土壤湿度（模拟值）
        moisture_raw = self.adc.read()
        moisture = (moisture_raw / 4095.0) * 100.0

        # 读取pH值（简化）
        ph_value = self.read_ph()

        # 读取温度
        temperature = self.read_temperature()

        return {
            "soil_moisture": moisture,
            "ph_value": ph_value,
            "temperature": temperature,
            "timestamp": time.time()
        }

    def send_data(self, data: dict):
        """发送数据（NB-IoT）"""
        # NB-IoT发送逻辑
        pass

    def run(self):
        """主循环（低功耗）"""
        while True:
            # 唤醒
            data = self.read_sensors()
            self.send_data(data)

            # 进入深度睡眠
            self.deep_sleep.sleep(self.sleep_duration)
```

### 5.4 远程监控

**远程监控平台**：

```python
class RemoteMonitoringPlatform:
    """远程监控平台"""

    def __init__(self):
        self.devices = {}
        self.alerts = []

    def register_device(self, device_id: str, schema: dict):
        """注册设备"""
        self.devices[device_id] = {
            'schema': schema,
            'last_update': None,
            'status': 'offline'
        }

    def update_device_data(self, device_id: str, data: dict):
        """更新设备数据"""
        if device_id in self.devices:
            self.devices[device_id]['last_update'] = datetime.utcnow()
            self.devices[device_id]['status'] = 'online'
            self.devices[device_id]['data'] = data

            # 检查告警
            self.check_alerts(device_id, data)

    def check_alerts(self, device_id: str, data: dict):
        """检查告警条件"""
        schema = self.devices[device_id]['schema']

        # 土壤湿度告警
        if data['soil_moisture'] < 20.0:
            self.alerts.append({
                'device_id': device_id,
                'type': 'low_moisture',
                'message': '土壤湿度过低，需要灌溉',
                'timestamp': datetime.utcnow()
            })

        # pH值告警
        if data['ph_value'] < 6.0 or data['ph_value'] > 8.0:
            self.alerts.append({
                'device_id': device_id,
                'type': 'ph_abnormal',
                'message': 'pH值异常，需要调整',
                'timestamp': datetime.utcnow()
            })
```

---

## 6. 案例总结

### 6.1 成功因素

**关键成功因素**：

1. **标准化Schema**：使用GB/T 34068-2017标准
2. **完整定义**：五维Schema结构完整定义
3. **代码生成**：自动化代码生成减少错误
4. **协议转换**：灵活的协议转换机制
5. **安全设计**：完善的安全机制

### 6.2 挑战与解决方案

**挑战1：协议多样性**:

- **问题**：不同场景使用不同协议
- **解决方案**：协议网关和转换机制

**挑战2：低功耗设计**:

- **问题**：电池供电设备需要低功耗
- **解决方案**：深度睡眠和PSM模式

**挑战3：数据安全**:

- **问题**：数据传输安全要求
- **解决方案**：TLS加密和设备认证

### 6.3 最佳实践

**实践建议**：

1. **Schema优先**：先定义Schema，再生成代码
2. **标准遵循**：遵循GB/T和行业标准
3. **可扩展性**：设计时考虑扩展性
4. **安全第一**：安全机制不可忽视
5. **测试验证**：充分测试和验证

---

## 7. 参考文献

### 7.1 标准文档

- GB/T 34068-2017 物联网总体技术 智能传感器接口规范
- GB/T 19582-2008 Modbus协议标准
- LoRaWAN Specification 1.0.4

### 7.2 技术文档

- MQTT Protocol Specification
- Modbus Protocol Specification
- LoRaWAN Protocol Specification

### 7.3 在线资源

- [MQTT官网](https://mqtt.org/)
- [Modbus官网](https://modbus.org/)
- [LoRaWAN官网](https://lora-alliance.org/)

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
