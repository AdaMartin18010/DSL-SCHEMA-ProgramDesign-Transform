# Energy Management标准对标

## 📑 目录

- [Energy Management标准对标](#energy-management标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. Zigbee/Thread能源标准](#2-zigbeethread能源标准)
    - [2.1 Zigbee Smart Energy (SE) 1.4](#21-zigbee-smart-energy-se-14)
    - [2.2 Thread 1.3能源管理](#22-thread-13能源管理)
  - [3. Green Energy标准](#3-green-energy标准)
    - [3.1 IEEE 2030.5](#31-ieee-20305)
    - [3.2 OpenADR 2.0b](#32-openadr-20b)
  - [4. Energy Star标准](#4-energy-star标准)
    - [4.1 Energy Star智能恒温器](#41-energy-star智能恒温器)
    - [4.2 Energy Star智能照明](#42-energy-star智能照明)
  - [5. 国际电工标准](#5-国际电工标准)
    - [5.1 IEC 62056 (DLMS/COSEM)](#51-iec-62056-dlmscosem)
    - [5.2 IEC 61850](#52-iec-61850)
  - [6. 通信协议标准](#6-通信协议标准)
    - [6.1 DALI-2照明控制](#61-dali-2照明控制)
    - [6.2 Modbus能源管理](#62-modbus能源管理)
  - [7. 能效评估标准](#7-能效评估标准)
    - [7.1 ASHRAE 90.1](#71-ashrae-901)
    - [7.2 ISO 50001能源管理](#72-iso-50001能源管理)
  - [8. 标准对比矩阵](#8-标准对比矩阵)
  - [9. 标准发展趋势](#9-标准发展趋势)

---

## 1. 标准体系概述

Energy Management标准体系分为五个层次：

1. **网络层标准**：Zigbee SE、Thread能源管理、Zigbee Green Power
2. **应用层标准**：IEEE 2030.5、OpenADR 2.0b、Energy Service Interface
3. **能效认证标准**：Energy Star、EU Energy Label、中国能效标识
4. **国际电工标准**：IEC 62056、IEC 61850、IEC 62325
5. **建筑能效标准**：ASHRAE 90.1、ISO 50001、ISO 7730

---

## 2. Zigbee/Thread能源标准

### 2.1 Zigbee Smart Energy (SE) 1.4

**标准名称**：Zigbee Smart Energy Profile 1.4

**核心内容**：

- **能源计量**：标准化的能源数据采集和传输
- **价格信息**：实时电价和费率信息传递
- **需求响应**：负载控制和需求响应事件
- **消息集群**：能源相关的Zigbee集群定义

**关键集群**：

| 集群名称 | 集群ID | 功能描述 |
|---------|-------|---------|
| Simple Metering | 0x0702 | 基本计量数据（电能、功率） |
| Price | 0x0700 | 当前和计划价格信息 |
| Demand Response | 0x0701 | 需求响应事件和控制 |
| Messaging | 0x0703 | 文本消息传递 |
| Tunneling | 0x0704 | 隧道协议传输 |
| Key Establishment | 0x0800 | 安全密钥建立 |

**设备类型**：

1. **Energy Service Interface (ESI)**：能源服务接口设备
2. **Metering Device**：计量设备（智能电表）
3. **In-Premises Display (IPD)**：户内显示设备
4. **Load Control Device**：负载控制设备
5. **Smart Appliance**：智能家电
6. **Prepayment Terminal**：预付费终端

**安全机制**：

- **证书基础安全**：基于X.509证书的认证
- **密钥建立**：Elliptic Curve Cryptography (ECC)
- **网络层加密**：AES-128加密
- **应用层安全**：APS层安全

**Schema支持**：完整支持

**最新版本**：Zigbee SE 1.4（2019年发布）

**参考链接**：[CSA连接标准联盟](https://csa-iot.org/)

---

### 2.2 Thread 1.3能源管理

**标准名称**：Thread Specification 1.3

**核心内容**：

- **IPv6网络**：基于6LoWPAN的IPv6网络
- **网格网络**：自组织、自愈的网格拓扑
- **低功耗**：sleepy end devices支持
- **边界路由**：与外部IP网络连接
- **与Matter集成**：支持Matter over Thread

**网络特性**：

| 特性 | 参数 |
|-----|-----|
| 网络规模 | 最大250个节点 |
| 跳数 | 最大32跳 |
| 延迟 | 典型小于100ms |
| 数据速率 | 250 kbps (2.4GHz) |

**能源管理应用**：

- 智能电表通信
- 分布式能源监控
- 智能家居能源管理
- 需求响应通信

**与Zigbee SE对比**：

| 特性 | Thread 1.3 | Zigbee SE 1.4 |
|-----|-----------|---------------|
| 网络层 | IPv6 | Zigbee Pro |
| 互操作性 | 更好（IP基础） | 好（需要网关） |
| 功耗 | 低 | 低 |
| 安全性 | DTLS/TLS | AES-128 |
| 应用协议 | Matter/自定义 | SE Profile |

**Schema支持**：完整支持

**最新版本**：Thread 1.3.1（2023年发布）

**参考链接**：[Thread Group](https://www.threadgroup.org/)

---

## 3. Green Energy标准

### 3.1 IEEE 2030.5

**标准名称**：IEEE 2030.5-2018 - Smart Energy Profile 2.0

**核心内容**：

- **IP基础**：基于RESTful架构的IP协议
- **应用层协议**：定义能源管理应用层协议
- **功能集**：价格、需求响应、分布式能源、计量
- **安全性**：传输层安全和应用层安全

**功能集（Function Sets）**：

| 功能集 | 描述 |
|-------|-----|
| Pricing | 价格信息获取和显示 |
| Demand Response | 需求响应信号接收和执行 |
| Distributed Energy Resources | DER监控和控制 |
| Metering | 计量数据读取 |
| Flow Reservation | 电力流动预约 |
| prepayment | 预付费管理 |

**资源模型**：

```
EndDevice
├── DeviceCapability
├── DeviceInformation
├── DeviceStatus
├── PowerStatus
├── FlowReservationRequest/Response
├── DER
│   ├── DERAvailability
│   ├── DERCapability
│   ├── DERSettings
│   ├── DERStatus
│   └── DERControl
├── UsagePoint
│   ├── MeterReading
│   ├── ReadingType
│   └── ReadingSet
└── ...
```

**通信协议**：

- **传输层**：TCP或UDP
- **安全层**：TLS 1.2+
- **应用层**：HTTP/1.1 + EXI（高效XML交换）
- **内容类型**：application/sep+xml 或 application/sep-exi

**Schema支持**：完整支持

**最新版本**：IEEE 2030.5-2018

**参考链接**：[IEEE 2030.5](https://standards.ieee.org/standard/2030.5-2018.html)

---

### 3.2 OpenADR 2.0b

**标准名称**：Open Automated Demand Response (OpenADR) 2.0b

**核心内容**：

- **自动需求响应**：标准化的DR信号传输
- **信号类型**：简单信号、价格信号、负荷控制信号
- **报告机制**：DR事件结果报告
- **互操作性**：多厂商设备互操作

**信号类型**：

| 信号类型 | 描述 | 典型应用 |
|---------|-----|---------|
| Simple | 简单级别信号（0-5级） | 紧急减负荷 |
| Price | 实时价格信号 | 电价响应 |
| LoadControl | 负载控制信号 | 直接负载控制 |
| Reliability | 可靠性信号 | 电网稳定 |
| Emergency | 紧急信号 | 电网紧急情况 |

**参与角色**：

- **Virtual Top Node (VTN)**：信号发送端（公用事业、Aggregator）
- **Virtual End Node (VEN)**：信号接收端（客户设备）

**事件流程**：

```
1. VTN发布DR事件
2. VEN接收并确认事件
3. VEN执行DR动作
4. VEN报告事件结果
5. VTN确认报告
```

**消息类型**：

- oadrDistributeEvent：分发DR事件
- oadrCreatedEvent：确认事件创建
- oadrRegisterReport：注册报告
- oadrUpdateReport：更新报告
- oadrRequestEvent：请求事件
- oadrResponse：通用响应

**Schema支持**：完整支持

**最新版本**：OpenADR 2.0b（2015年发布）

**参考链接**：[OpenADR Alliance](https://www.openadr.org/)

---

## 4. Energy Star标准

### 4.1 Energy Star智能恒温器

**标准名称**：Energy Star Certified Smart Thermostat

**核心要求**：

- **节能效果**：比传统恒温器平均节能8-15%
- **功能要求**：
  - 可编程日程
  - 远程访问
  - 占用检测
  - 使用报告
- **数据报告**：向EPA提供脱敏使用数据

**测试方法**：

- 基于EPA认可的模拟工具
- 测试7个气候区的表现
- 评估制冷和制热季节的节能效果

**当前要求（Version 3.0）**：

| 指标 | 要求 |
|-----|------|
| 年节能率 | 大于等于8%（与基线恒温器相比） |
| 远程控制 | 必需 |
| 占用感应 | 必需 |
| 地理围栏 | 推荐 |

**Schema支持**：良好支持

**参考链接**：[Energy Star Thermostats](https://www.energystar.gov/products/heating_cooling/smart_thermostats)

---

### 4.2 Energy Star智能照明

**标准名称**：Energy Star Certified Light Bulbs / Fixtures

**核心要求**：

- **能效**：光效（lm/W）要求
- **显色性**：CRI 大于等于 80
- **寿命**：最低使用寿命要求
- **色温**：标称色温准确性

**灯泡类型要求（Version 2.1）**：

| 类型 | 最低光效 |
|-----|---------|
| 全向灯泡（A型） | 60 lm/W |
| 定向灯泡（PAR/R） | 50 lm/W |
| 装饰灯泡 | 45 lm/W |
| GU10灯杯 | 50 lm/W |

**智能功能要求**：

- 调光兼容性（如声明支持调光）
- 联网控制（智能灯泡）
- 颜色控制（彩色灯泡）

**待机功耗**：

- 智能灯泡待机功耗 小于等于 0.5W
- 带传感器的灯具待机功耗 小于等于 0.5W

**Schema支持**：良好支持

**参考链接**：[Energy Star Lighting](https://www.energystar.gov/products/lighting_fans)

---

## 5. 国际电工标准

### 5.1 IEC 62056 (DLMS/COSEM)

**标准名称**：IEC 62056 - Electricity metering data exchange

**标准组成**：

| 部分 | 标题 | 内容 |
|-----|-----|-----|
| 62056-6-1 | Object identification system (OBIS) | 对象标识系统 |
| 62056-6-2 | COSEM interface classes | COSEM接口类 |
| 62056-5-3 | DLMS/COSEM application layer | 应用层协议 |
| 62056-8-3 | DLMS/COSEM over TCP/UDP | 传输层映射 |
| 62056-7-3 | Wired M-Bus | M-Bus映射 |
| 62056-9-1 | Communication profile using S-FSK | S-FSK配置文件 |
| 62056-9-2 | Communication profile using G3-PLC | G3-PLC配置文件 |

**COSEM对象模型**：

```
Logical Device
├── Association (对象关联)
├── Security Setup (安全设置)
├── Clock (时钟)
├── Data (通用数据对象)
├── Register (寄存器)
├── Extended Register (扩展寄存器)
├── Demand Register (需量寄存器)
├── Register Monitor (寄存器监控)
├── Profile Generic (通用曲线)
├── Script Table (脚本表)
├── Schedule (日程表)
└── Activity Calendar (活动日历)
```

**OBIS代码结构**：

```
A-B:C.D.E*F

A: 介质（0=抽象对象，1=电，6=热...）
B: 通道号
C: 物理量
D: 测量方法
E: 费率
F: 历史值
```

**常见OBIS代码**：

| OBIS代码 | 含义 |
|---------|-----|
| 1-0:1.8.0*255 | 正向有功总电能 |
| 1-0:2.8.0*255 | 反向有功总电能 |
| 1-0:1.7.0*255 | 瞬时有功功率 |
| 1-0:32.7.0*255 | L1电压 |
| 1-0:31.7.0*255 | L1电流 |
| 0-0:1.0.0*255 | 时钟 |

**Schema支持**：完整支持

**最新版本**：IEC 62056系列（2017-2021年更新）

**参考链接**：[DLMS User Association](https://www.dlms.com/)

---

### 5.2 IEC 61850

**标准名称**：IEC 61850 - Communication networks and systems for power utility automation

**核心内容**：

- **变电站自动化**：变电站通信网络和系统
- **抽象通信服务接口（ACSI）**：与具体协议无关的服务接口
- **变电站配置语言（SCL）**：基于XML的配置描述
- **数据模型**：标准化的电力系统数据模型

**逻辑节点（Logical Nodes）**：

| 前缀 | 类别 | 示例 |
|-----|-----|-----|
| MMXU | 测量 | 三相电气测量 |
| MSTA | 计量 | 计量数据 |
| CSWI | 控制 | 开关控制 |
| XCBR | 一次设备 | 断路器 |
| ATCC | 自动功能 | 变压器调压 |
| STMP | 传感器 | 温度传感器 |

**数据属性命名**：

```
DataObjectName[.SubDataObjectName].AttributeName[.SubAttributeName]
FunctionalConstraint

示例：
MMXU1.Hz.mag.f [MX] - 频率测量值
MMXU1.TotW.mag.f [MX] - 总有功功率测量值
```

**通信服务**：

- **关联服务**：建立/终止通信关联
- **数据服务**：读取/写入数据值
- **报告服务**：事件驱动的数据报告
- **日志服务**：历史数据访问
- **控制服务**：设备控制操作
- **文件传输**：文件传输服务

**SCL文件类型**：

| 文件扩展名 | 用途 |
|-----------|-----|
| .ICD | IED能力描述 |
| .SSD | 系统规范描述 |
| .SCD | 变电站配置描述 |
| .CID | 配置后的IED描述 |
| .IID | 实例化IED描述 |

**Schema支持**：完整支持

**最新版本**：IEC 61850 Ed 2.1（2020年）

**参考链接**：[IEC 61850](https://webstore.iec.ch/publication/66912)

---

## 6. 通信协议标准

### 6.1 DALI-2照明控制

**标准名称**：DALI-2 (Digital Addressable Lighting Interface - Part 2)

**核心内容**：

- **数字照明控制**：照明设备的数字寻址控制接口
- **总线拓扑**：两线总线，支持最多64个设备
- **认证要求**：必须经过DiiA认证
- **向后兼容**：与DALI（Part 1）部分兼容

**控制功能**：

| 功能 | 命令 | 范围 |
|-----|-----|-----|
| 直接调光 | DIRECT ARC POWER | 1-254 |
| 关闭 | OFF | - |
| 上调 | UP | 步进 |
| 下调 | DOWN | 步进 |
| 最大电平 | MAX LEVEL | - |
| 最小电平 | MIN LEVEL | - |

**设备类型**：

- Device Type 0: 荧光灯镇流器
- Device Type 1: 自容式应急照明
- Device Type 6: LED模块
- Device Type 7: 开关功能
- Device Type 8: 颜色控制

**与Zigbee/Thread集成**：

```
Zigbee/Thread网络 通过 DALI网关 连接 DALI总线 再连接 DALI设备
```

**Schema支持**：良好支持

**最新版本**：DALI-2（IEC 62386系列）

**参考链接**：[DiiA](https://www.dali-alliance.org/)

---

### 6.2 Modbus能源管理

**标准名称**：Modbus Application Protocol Specification

**核心内容**：

- **主从协议**：简单的请求-响应协议
- **传输模式**：RTU（二进制）和ASCII模式
- **TCP/IP**：Modbus TCP over IP
- **应用广泛**：工业和能源管理应用

**功能码**：

| 功能码 | 功能 | 说明 |
|-------|-----|-----|
| 01 | 读线圈 | 读离散输出 |
| 02 | 读离散输入 | 读离散输入 |
| 03 | 读保持寄存器 | 读多个保持寄存器 |
| 04 | 读输入寄存器 | 读多个输入寄存器 |
| 05 | 写单线圈 | 写单个线圈 |
| 06 | 写单寄存器 | 写单个保持寄存器 |
| 16 | 写多寄存器 | 写多个保持寄存器 |

**能源管理应用**：

- 智能电表数据读取
- 逆变器监控
- 储能系统控制
- HVAC设备控制

**SunSpec标准**：

基于Modbus的可再生能源设备标准
- 模型1: 通用设备信息
- 模型101-103: 单相/三相逆变器
- 模型111-113: 分相/三相逆变器
- 模型120-122: 储能

**Schema支持**：良好支持

**参考链接**：[Modbus Organization](https://modbus.org/)

---

## 7. 能效评估标准

### 7.1 ASHRAE 90.1

**标准名称**：ANSI/ASHRAE/IES 90.1 - Energy Standard for Buildings Except Low-Rise Residential Buildings

**核心内容**：

- **建筑能效**：商业建筑节能标准
- **最低要求**：新建和改造建筑的最低能效要求
- **合规路径**：规定性路径和性能路径
- **设备效率**：HVAC、照明、电气设备效率要求

**照明功率密度（LPD）要求**（部分）：

| 空间类型 | LPD (W/m2) |
|---------|-----------|
| 办公室 - 开放式 | 11.8 |
| 会议室 | 12.9 |
| 走廊 | 5.1 |
| 储藏室 | 8.5 |
| 停车场 | 2.8 |

**HVAC要求**：

- 最低设备效率（EER、COP）
- 控制系统要求（DDC控制）
- 经济器要求
- 能量回收要求

**住宅建筑对应标准**：
- IECC（国际节能规范）
- ASHRAE 90.2

**Schema支持**：部分支持

**最新版本**：ASHRAE 90.1-2019

**参考链接**：[ASHRAE](https://www.ashrae.org/)

---

### 7.2 ISO 50001能源管理

**标准名称**：ISO 50001 - Energy management systems

**核心内容**：

- **能源管理体系**：系统化的能源管理方法
- **PDCA循环**：计划-执行-检查-改进
- **持续改进**：能源绩效的持续改进
- **认证基础**：能源管理体系认证的基础

**管理要素**：

```
1. 组织环境
2. 领导作用
3. 策划
   - 能源评审
   - 能源基准
   - 能源绩效指标
   - 能源目标
4. 支持
5. 运行
6. 绩效评价
7. 改进
```

**与ISO 14001关系**：

- 基于相同的HLS（高级结构）
- 可整合实施
- ISO 50001专注能源，ISO 14001专注环境

**Schema支持**：部分支持

**最新版本**：ISO 50001:2018

**参考链接**：[ISO 50001](https://www.iso.org/iso-50001-energy-management.html)

---

## 8. 标准对比矩阵

| 标准 | 组织 | Schema支持 | 网络层 | 应用层 | 安全 | 主要应用 |
|------|------|-----------|-------|-------|-----|---------|
| **Zigbee SE 1.4** | CSA | 完整支持 | Zigbee | SE Profile | AES-128 | 智能电表、DR |
| **Thread 1.3** | Thread Group | 完整支持 | 6LoWPAN | Matter/自定义 | DTLS | 智能家居能源 |
| **IEEE 2030.5** | IEEE | 完整支持 | IP | SEP 2.0 | TLS | 公用事业通信 |
| **OpenADR 2.0b** | OpenADR Alliance | 完整支持 | IP | OpenADR | TLS | 需求响应 |
| **Energy Star** | EPA | 良好支持 | - | - | - | 能效认证 |
| **IEC 62056** | IEC | 完整支持 | 多种 | DLMS/COSEM | 应用层安全 | 计量通信 |
| **IEC 61850** | IEC | 完整支持 | 多种 | ACSI/MMS | 多层安全 | 变电站自动化 |
| **DALI-2** | DiiA | 良好支持 | DALI总线 | DALI协议 | - | 照明控制 |
| **Modbus** | Modbus Org | 良好支持 | 多种 | Modbus | - | 工业通信 |
| **ASHRAE 90.1** | ASHRAE | 部分支持 | - | - | - | 建筑能效 |
| **ISO 50001** | ISO | 部分支持 | - | - | - | 能源管理体系 |

**说明**：

- 完整支持：完全支持
- 良好支持：良好支持
- 部分支持：部分支持
- 有限支持：有限支持

---

## 9. 标准发展趋势

### 9.1 2024-2025年趋势

#### 9.1.1 Matter over Thread统一

- **趋势**：Matter标准推动智能家居能源管理的统一
- **影响**：Zigbee SE和Thread能源管理功能整合到Matter
- **标准**：Matter Energy Management Cluster开发中
- **预期**：2024-2025年发布

#### 9.1.2 虚拟电厂（VPP）标准化

- **趋势**：分布式能源聚合的标准化需求
- **影响**：IEEE 2030.5扩展支持VPP
- **标准**：IEEE P2809 VPP标准制定中
- **预期**：2025年发布

#### 9.1.3 碳排放数据标准化

- **趋势**：碳足迹追踪的数据交换标准化
- **影响**：能源数据中嵌入碳排放信息
- **标准**：基于GHG Protocol的标准化
- **预期**：2024年开始应用

### 9.2 2025-2026年展望

#### 9.2.1 AI优化能源管理

- **趋势**：AI/ML驱动的能源管理标准化
- **影响**：标准化的模型训练和推理接口
- **标准**：机器学习模型互操作性标准
- **预期**：2025-2026年

#### 9.2.2 区块链能源交易

- **趋势**：P2P能源交易的区块链标准化
- **影响**：分布式能源交易的智能合约标准
- **标准**：IEEE P2140区块链能源标准
- **预期**：2026年

#### 9.2.3 数字孪生能源系统

- **趋势**：能源系统的数字孪生标准化
- **影响**：虚拟能源系统的互操作性
- **标准**：ISO/IEC 30173数字孪生参考架构
- **预期**：2025-2026年

---

**参考文档**：

- `01_Overview.md` - 概述文档
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系

**创建时间**：2026-02-15
**最后更新**：2026-02-15
