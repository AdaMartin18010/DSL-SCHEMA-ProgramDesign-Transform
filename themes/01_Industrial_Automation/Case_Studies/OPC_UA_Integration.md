# OPC UA 集成案例研究

## 案例概述

**项目名称**: 智能工厂OPC UA统一架构改造
**行业**: 工业自动化 - 智能制造
**涉及标准**: OPC UA, IEC 62541, MQTT, JSON, XML
**目标**: 将分散的PLC、SCADA、MES系统通过OPC UA统一集成，建立数字孪生基础

---

## 背景介绍

### 业务背景

某汽车零部件制造厂拥有：

- 5条生产线，每条线8-10台PLC（西门子、罗克韦尔、三菱混用）
- 3套SCADA系统（不同品牌，数据孤岛）
- 1套MES系统，与设备通信困难
- 多种私有协议（S7、EtherNet/IP、Modbus TCP）

### 改造目标

1. 建立统一的OPC UA信息模型
2. 实现跨品牌设备互联互通
3. 建立实时数据平台支撑数字孪生
4. 实现预测性维护

---

## Schema分析

### 源Schema: 西门子S7 Tag点表

```text
DB1.DBD0    - Real    - Line1.Speed          [生产线1速度]
DB1.DBD4    - Real    - Line1.Temperature    [生产线1温度]
DB1.DBX8.0  - Bool    - Line1.Running        [生产线1运行状态]
DB1.DBW10   - Int     - Line1.PartCount      [生产线1产量计数]
DB2.DBD0    - Real    - Line1.Motor.Current  [电机电流]
DB2.DBD4    - Real    - Line1.Motor.Voltage  [电机电压]
DB2.DBX8.0  - Bool    - Line1.Motor.Fault    [电机故障]
```

**结构特点**:

- 扁平地址结构（DB块+偏移）
- 无语义信息（需要额外文档说明）
- 厂商私有格式
- 无数据类型元信息

### 目标Schema: OPC UA信息模型

```xml
<?xml version="1.0" encoding="utf-8"?>
<UANodeSet xmlns="http://opcfoundation.org/UA/2008/02/Types.xsd">
  <NamespaceUris>
    <Uri>http://manufacturer.com/UA/ProductionLine/</Uri>
  </NamespaceUris>

  <!-- 生产线类型定义 -->
  <UAObjectType NodeId="ns=1;i=1001" BrowseName="1:ProductionLineType">
    <DisplayName>Production Line Type</DisplayName>
    <References>
      <Reference ReferenceType="HasSubtype" IsForward="false">i=58</Reference>
      <Reference ReferenceType="HasComponent">ns=1;i=1002</Reference>
      <Reference ReferenceType="HasComponent">ns=1;i=1003</Reference>
      <Reference ReferenceType="HasComponent">ns=1;i=1004</Reference>
    </References>
  </UAObjectType>

  <!-- 速度变量 -->
  <UAVariable NodeId="ns=1;i=1002" BrowseName="1:Speed"
              DataType="Double" ParentNodeId="ns=1;i=1001">
    <DisplayName>Line Speed</DisplayName>
    <Description>Production line speed in m/min</Description>
    <References>
      <Reference ReferenceType="HasTypeDefinition">i=63</Reference>
      <Reference ReferenceType="HasModellingRule">i=78</Reference>
    </References>
    <Value>
      <Double>0.0</Double>
    </Value>
  </UAVariable>

  <!-- 温度变量 -->
  <UAVariable NodeId="ns=1;i=1003" BrowseName="1:Temperature"
              DataType="Double" ParentNodeId="ns=1;i=1001">
    <DisplayName>Temperature</DisplayName>
    <Description>Line temperature in Celsius</Description>
    <References>
      <Reference ReferenceType="HasTypeDefinition">i=63</Reference>
      <Reference ReferenceType="HasModellingRule">i=78</Reference>
    </References>
  </UAVariable>

  <!-- 运行状态 -->
  <UAVariable NodeId="ns=1;i=1004" BrowseName="1:IsRunning"
              DataType="Boolean" ParentNodeId="ns=1;i=1001">
    <DisplayName>Is Running</DisplayName>
    <References>
      <Reference ReferenceType="HasTypeDefinition">i=63</Reference>
      <Reference ReferenceType="HasModellingRule">i=78</Reference>
    </References>
  </UAVariable>

  <!-- 电机类型 -->
  <UAObjectType NodeId="ns=1;i=2001" BrowseName="1:MotorType">
    <DisplayName>Motor Type</DisplayName>
    <References>
      <Reference ReferenceType="HasSubtype" IsForward="false">i=58</Reference>
      <Reference ReferenceType="HasComponent">ns=1;i=2002</Reference>
      <Reference ReferenceType="HasComponent">ns=1;i=2003</Reference>
      <Reference ReferenceType="HasComponent">ns=1;i=2004</Reference>
    </References>
  </UAObjectType>

  <!-- 电机电流 -->
  <UAVariable NodeId="ns=1;i=2002" BrowseName="1:Current"
              DataType="Double" ParentNodeId="ns=1;i=2001">
    <DisplayName>Current</DisplayName>
    <Description>Motor current in Ampere</Description>
    <References>
      <Reference ReferenceType="HasTypeDefinition">i=63</Reference>
      <Reference ReferenceType="HasModellingRule">i=78</Reference>
    </References>
  </UAVariable>

  <!-- 电机方法：启动 -->
  <UAMethod NodeId="ns=1;i=2010" BrowseName="1:Start"
            ParentNodeId="ns=1;i=2001">
    <DisplayName>Start Motor</DisplayName>
    <References>
      <Reference ReferenceType="HasModellingRule">i=78</Reference>
    </References>
  </UAMethod>
</UANodeSet>
```

**结构特点**:

- 面向对象的信息模型
- 语义丰富的类型系统
- 机器可读的元数据
- 支持方法调用
- 跨平台互操作性

---

## 信息模型设计

### 设备层级结构

```text
ManufacturingPlant (工厂)
├── Line1 (生产线1)
│   ├── Speed (速度传感器)
│   ├── Temperature (温度传感器)
│   ├── Status (运行状态)
│   ├── PartCounter (产量计数器)
│   └── Motor1 (电机)
│       ├── Current (电流)
│       ├── Voltage (电压)
│       ├── Temperature (温度)
│       ├── Start() (启动方法)
│       └── Stop() (停止方法)
├── Line2 (生产线2)
│   └── ...
└── CentralSCADA (中央监控系统)
```

### 类型定义

```python
from opcua import ua, Server
from opcua.common.type_dictionary_builder import DataTypeDictionaryBuilder
from opcua.common.xmlexporter import XmlExporter

class ProductionLineModel:
    """生产线OPC UA信息模型构建器"""

    def __init__(self, server: Server):
        self.server = server
        self.idx = self.server.register_namespace("http://manufacturer.com/UA/ProductionLine/")

    def build_model(self):
        """构建完整信息模型"""
        # 创建对象类型
        self._create_motor_type()
        self._create_production_line_type()

        # 创建设备实例
        self._create_line_instances()

    def _create_motor_type(self):
        """创建电机类型"""
        # 获取Types对象
        types = self.server.get_objects_node()

        # 创建MotorType对象类型
        motor_type = types.add_object_type(self.idx, "MotorType")

        # 添加属性
        current = motor_type.add_variable(self.idx, "Current", 0.0)
        current.set_modelling_rule(True)
        current.set_description("Motor current in Ampere")
        current.set_unit("A")

        voltage = motor_type.add_variable(self.idx, "Voltage", 0.0)
        voltage.set_modelling_rule(True)
        voltage.set_description("Motor voltage in Volt")
        voltage.set_unit("V")

        temp = motor_type.add_variable(self.idx, "Temperature", 0.0)
        temp.set_modelling_rule(True)
        temp.set_description("Motor temperature in Celsius")
        temp.set_unit("°C")

        # 添加状态变量
        status = motor_type.add_variable(self.idx, "Status", "Stopped")
        status.set_modelling_rule(True)

        # 添加故障变量
        fault = motor_type.add_variable(self.idx, "Fault", False)
        fault.set_modelling_rule(True)

        # 添加方法
        motor_type.add_method(
            self.idx,
            "Start",
            self._motor_start_method,
            [],
            [ua.VariantType.Boolean]
        )

        motor_type.add_method(
            self.idx,
            "Stop",
            self._motor_stop_method,
            [],
            [ua.VariantType.Boolean]
        )

        self.motor_type = motor_type

    def _create_production_line_type(self):
        """创建生产线类型"""
        types = self.server.get_objects_node()

        line_type = types.add_object_type(self.idx, "ProductionLineType")

        # 生产线参数
        speed = line_type.add_variable(self.idx, "Speed", 0.0)
        speed.set_modelling_rule(True)
        speed.set_description("Line speed in m/min")
        speed.set_unit("m/min")

        temp = line_type.add_variable(self.idx, "Temperature", 0.0)
        temp.set_modelling_rule(True)
        temp.set_description("Line temperature in Celsius")
        temp.set_unit("°C")

        is_running = line_type.add_variable(self.idx, "IsRunning", False)
        is_running.set_modelling_rule(True)

        part_count = line_type.add_variable(self.idx, "PartCount", 0)
        part_count.set_modelling_rule(True)

        # 添加电机组件（使用MotorType）
        motor = line_type.add_object(self.idx, "MainMotor", self.motor_type.nodeid)
        motor.set_modelling_rule(True)

        self.line_type = line_type

    def _create_line_instances(self):
        """创建设备实例"""
        objects = self.server.get_objects_node()

        for i in range(1, 6):  # 5条生产线
            line = objects.add_object(
                self.idx,
                f"Line{i}",
                self.line_type.nodeid
            )

            # 设置初始值
            line.get_child(f"{self.idx}:Speed").set_value(0.0)
            line.get_child(f"{self.idx}:IsRunning").set_value(False)

    def _motor_start_method(self, parent):
        """电机启动方法"""
        print(f"Starting motor: {parent}")
        # 实际实现会调用PLC控制逻辑
        return [ua.Variant(True, ua.VariantType.Boolean)]

    def _motor_stop_method(self, parent):
        """电机停止方法"""
        print(f"Stopping motor: {parent}")
        return [ua.Variant(True, ua.VariantType.Boolean)]
```

---

## 数据映射实现

### PLC到OPC UA网关

```python
from snap7 import client as s7client
from opcua import Server, ua
import threading
import time

class PLCtoOPCUAGateway:
    """西门子PLC到OPC UA网关"""

    def __init__(self, plc_ip: str, rack: int, slot: int, opc_port: int = 4840):
        self.plc = s7client.Client()
        self.plc_ip = plc_ip
        self.rack = rack
        self.slot = slot

        # OPC UA服务器
        self.server = Server()
        self.server.set_endpoint(f"opc.tcp://0.0.0.0:{opc_port}")
        self.idx = self.server.register_namespace("http://gateway.local/PLC/")

        # 映射表：PLC地址 -> OPC UA节点
        self.tag_mappings = {}
        self.running = False

    def connect(self):
        """连接PLC"""
        self.plc.connect(self.plc_ip, self.rack, self.slot)
        print(f"Connected to PLC at {self.plc_ip}")

        # 启动OPC UA服务器
        self.server.start()
        print(f"OPC UA Server started on port 4840")

    def add_tag_mapping(self, tag_name: str, db_number: int,
                        offset: int, data_type: str, opc_path: str):
        """
        添加标签映射

        Args:
            tag_name: 标签名称
            db_number: DB块号
            offset: 偏移地址
            data_type: 数据类型 (Real, Int, Bool, etc.)
            opc_path: OPC UA节点路径
        """
        # 创建OPC UA变量
        objects = self.server.get_objects_node()
        parts = opc_path.split('.')

        current = objects
        for part in parts[:-1]:
            try:
                current = current.get_child(f"{self.idx}:{part}")
            except:
                current = current.add_object(self.idx, part)

        # 创建变量
        var = current.add_variable(self.idx, parts[-1], self._get_default_value(data_type))
        var.set_writable()

        # 保存映射
        self.tag_mappings[tag_name] = {
            'db': db_number,
            'offset': offset,
            'type': data_type,
            'node': var
        }

    def _get_default_value(self, data_type: str):
        """获取默认值"""
        defaults = {
            'Real': 0.0,
            'Int': 0,
            'Bool': False,
            'DInt': 0,
            'Word': 0,
            'DWord': 0
        }
        return defaults.get(data_type, 0)

    def _read_plc_value(self, mapping: dict):
        """从PLC读取值"""
        db = mapping['db']
        offset = mapping['offset']
        data_type = mapping['type']

        try:
            if data_type == 'Real':
                data = self.plc.db_read(db, offset, 4)
                return s7client.util.get_real(data, 0)

            elif data_type == 'Int':
                data = self.plc.db_read(db, offset, 2)
                return s7client.util.get_int(data, 0)

            elif data_type == 'Bool':
                # 计算字节和位偏移
                byte_offset = offset // 8
                bit_offset = offset % 8
                data = self.plc.db_read(db, byte_offset, 1)
                return bool(data[0] & (1 << bit_offset))

            elif data_type == 'DInt':
                data = self.plc.db_read(db, offset, 4)
                return s7client.util.get_dint(data, 0)

        except Exception as e:
            print(f"Error reading from PLC: {e}")
            return None

    def _update_opcua(self, tag_name: str, value):
        """更新OPC UA节点值"""
        if value is not None:
            mapping = self.tag_mappings[tag_name]
            mapping['node'].set_value(value)

    def poll_loop(self, interval: float = 1.0):
        """轮询循环"""
        self.running = True

        while self.running:
            for tag_name, mapping in self.tag_mappings.items():
                value = self._read_plc_value(mapping)
                self._update_opcua(tag_name, value)

            time.sleep(interval)

    def start_polling(self, interval: float = 1.0):
        """启动轮询线程"""
        self.poll_thread = threading.Thread(target=self.poll_loop, args=(interval,))
        self.poll_thread.daemon = True
        self.poll_thread.start()

    def stop(self):
        """停止网关"""
        self.running = False
        self.server.stop()
        self.plc.disconnect()


# 使用示例
if __name__ == "__main__":
    gateway = PLCtoOPCUAGateway("192.168.1.10", rack=0, slot=1)

    # 连接
    gateway.connect()

    # 添加映射
    gateway.add_tag_mapping("Line1.Speed", 1, 0, "Real", "Line1.Speed")
    gateway.add_tag_mapping("Line1.Temperature", 1, 4, "Real", "Line1.Temperature")
    gateway.add_tag_mapping("Line1.Running", 1, 8, "Bool", "Line1.IsRunning")
    gateway.add_tag_mapping("Line1.PartCount", 1, 10, "Int", "Line1.PartCount")

    # 启动轮询
    gateway.start_polling(interval=0.5)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gateway.stop()
```

---

## 实施成果

### 集成效果

| 指标 | 改造前 | 改造后 | 提升 |
|------|--------|--------|------|
| 系统集成时间 | 2-3周 | 2-3天 | 85% ↓ |
| 设备接入成本 | 高（定制开发） | 低（标准接口） | 70% ↓ |
| 数据访问延迟 | 5-10秒 | <1秒 | 90% ↓ |
| 跨品牌兼容性 | 困难 | 原生支持 | - |

### 业务价值

1. **数字孪生基础**: 建立了完整的设备数字孪生模型
2. **预测性维护**: 基于实时数据的故障预测准确率达85%
3. **生产优化**: OEE（设备综合效率）提升12%
4. **快速扩展**: 新产线接入时间从3天缩短到2小时

---

**创建时间**: 2026-02-17
**维护者**: DSL Schema研究团队
