# TMS Schema概述

## 📑 目录

- [TMS Schema概述](#tms-schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 TMS Schema定义](#11-tms-schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 TMS Schema定义](#21-tms-schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. 运输管理核心模块](#3-运输管理核心模块)
    - [3.1 运输订单管理](#31-运输订单管理)
    - [3.2 路线规划](#32-路线规划)
    - [3.3 承运人管理](#33-承运人管理)
    - [3.4 运费计算](#34-运费计算)
  - [4. 标准对标](#4-标准对标)
    - [4.1 GS1标准](#41-gs1标准)
    - [4.2 ISO 14001](#42-iso-14001)
    - [4.3 物流EDI标准](#43-物流edi标准)
  - [5. 应用场景](#5-应用场景)
    - [5.1 干线运输](#51-干线运输)
    - [5.2 城配运输](#52-城配运输)
    - [5.3 多式联运](#53-多式联运)
    - [5.4 最后一公里配送](#54-最后一公里配送)
  - [6. TMS数据存储与分析](#6-tms数据存储与分析)
    - [6.1 PostgreSQL TMS数据存储](#61-postgresql-tms数据存储)
    - [6.2 数据分析应用价值](#62-数据分析应用价值)
  - [7. 行业最佳实践](#7-行业最佳实践)
    - [7.1 运输优化策略](#71-运输优化策略)
    - [7.2 成本控制实践](#72-成本控制实践)
  - [8. 思维导图](#8-思维导图)

---

## 1. 核心结论

**物流供应链存在强制性的TMS Schema体系**。

### 1.1 TMS Schema定义

```text
TMS_Schema = (Transportation_Order ⊕ Route_Planning ⊕ Carrier_Management ⊕ Freight_Calculation) × Logistics_Profile
```

### 1.2 标准依据

- **GS1标准**：全球统一标识系统标准
- **ISO 14001**：环境管理体系标准
- **物流EDI标准**：X12、EDIFACT物流相关交易集
- **智能交通系统标准**：ISO/TS 14813
- **危险品运输标准**：ADR、IMDG、IATA

---

## 2. 概念定义

### 2.1 TMS Schema定义

**TMS Schema**是描述运输管理系统（Transportation Management System）的形式化规范，包括运输订单、路线规划、承运人管理、运费计算等核心模块。

### 2.2 核心特征

1. **标准化**：基于国际物流和运输标准
2. **可追溯性**：支持运输全程追溯
3. **实时性**：支持实时跟踪和调度
4. **优化性**：支持路线和成本优化
5. **形式化**：数学形式化定义

### 2.3 Schema分类

- **运输订单Schema**：描述运输订单的数据结构
- **路线规划Schema**：描述运输路线和规划的数据结构
- **车辆Schema**：描述运输车辆的数据结构
- **承运人Schema**：描述承运人信息的数据结构
- **运费Schema**：描述运费计算的数据结构
- **跟踪Schema**：描述运输跟踪的数据结构

---

## 3. 运输管理核心模块

### 3.1 运输订单管理

**定义**：管理从订单创建到完成的整个运输生命周期。

**包含内容**：

- **订单创建**：客户订单信息录入
- **订单分配**：分配给合适的承运人或车辆
- **订单调度**：安排取货和配送时间
- **订单跟踪**：实时监控订单状态
- **订单完成**：签收确认和结算

**订单状态流转**：

```text
CREATED → CONFIRMED → PICKUP_ASSIGNED → IN_TRANSIT → DELIVERED → COMPLETED
   ↓           ↓             ↓              ↓            ↓           ↓
 CANCELLED   PENDING     PICKUP_READY    AT_HUB    OUT_FOR_DELIVERY  INVOICED
```

**关键字段**：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| order_id | String | 订单唯一标识符 |
| customer_id | String | 客户标识符 |
| pickup_location | Location | 取货地点 |
| delivery_location | Location | 配送地点 |
| cargo_info | Cargo | 货物信息 |
| service_type | Enum | 服务类型（标准/加急/定时） |
| status | Enum | 订单状态 |
| created_at | DateTime | 创建时间 |
| scheduled_pickup | DateTime | 计划取货时间 |
| scheduled_delivery | DateTime | 计划配送时间 |

### 3.2 路线规划

**定义**：基于约束条件和优化目标，规划最优运输路线。

**包含内容**：

- **路径优化**：最短路径、最快路径、最省成本路径
- **车辆调度**：车辆分配和调度优化
- **装载优化**：货物装载和空间利用优化
- **时间窗约束**：满足客户时间窗要求
- **多停靠点规划**：多点取送货规划

**路线规划算法**：

| 算法 | 适用场景 | 时间复杂度 |
|------|----------|------------|
| Dijkstra | 单源最短路径 | O(V²) |
| A* | 启发式最短路径 | O(E) |
| VRP | 车辆路径问题 | NP-hard |
| VRPTW | 带时间窗VRP | NP-hard |
| 遗传算法 | 大规模优化 | 启发式 |

**优化目标**：

```text
Minimize: α·Total_Distance + β·Total_Time + γ·Total_Cost + δ·Carbon_Emission
Subject to:
  - 车辆容量约束
  - 时间窗约束
  - 司机工作时长约束
  - 车辆类型约束
  - 道路限制约束
```

### 3.3 承运人管理

**定义**：管理承运人信息、资质、绩效和合作关系。

**包含内容**：

- **承运人档案**：基本信息、资质认证
- **服务评估**：服务质量评分
- **合同管理**：合同条款和价格协议
- **绩效管理**：KPI跟踪和评估
- **结算管理**：运费结算和对账

**承运人评估指标**：

| 指标类别 | 具体指标 | 权重 |
|----------|----------|------|
| 服务质量 | 准时率、货损率 | 30% |
| 成本控制 | 运价竞争力 | 25% |
| 响应速度 | 接单响应时间 | 20% |
| 信息系统 | EDI/API对接能力 | 15% |
| 合规性 | 资质认证、安全记录 | 10% |

**承运人评级体系**：

```text
评级 = (准时率 × 0.3) + (货损率反向 × 0.2) + (成本评分 × 0.2) + (响应评分 × 0.15) + (技术评分 × 0.15)

等级划分：
- S级 (95-100)：战略合作伙伴
- A级 (85-94)：核心承运人
- B级 (70-84)：合格承运人
- C级 (60-69)：观察名单
- D级 (<60)：淘汰
```

### 3.4 运费计算

**定义**：基于多种计费规则和因素，计算运输费用。

**包含内容**：

- **基础运费**：按距离、重量、体积计费
- **附加费用**：燃油附加费、偏远地区费、特殊处理费
- **折扣规则**：批量折扣、合同折扣
- **税费计算**：增值税、关税
- **多式联运费用**：多种运输方式组合计费

**运费计算模型**：

```text
总运费 = 基础运费 + 附加费 + 特殊处理费 - 折扣 + 税费

其中：
基础运费 = max(重量计费, 体积计费, 最低收费)
重量计费 = 实际重量 × 重量单价
体积计费 = 体积重量 × 体积单价
体积重量 = 长 × 宽 × 高 / 体积系数

附加费 = 燃油附加费 + 偏远地区费 + 超重/超大费 + 保险费
```

**计费方式对比**：

| 计费方式 | 适用场景 | 计算公式 |
|----------|----------|----------|
| 按重量计费 | 重货 | 重量(kg) × 单价 |
| 按体积计费 | 轻泡货 | 体积(m³) × 单价 |
| 按件计费 | 标准化货物 | 件数 × 单价 |
| 按距离计费 | 整车运输 | 距离(km) × 单价 |
| 按车次计费 | 专线运输 | 固定价格/车次 |

---

## 4. 标准对标

### 4.1 GS1标准

- **GS1标准**：全球统一标识系统标准
- **SSCC**：系列货运包装箱代码，用于运输单元标识
- **GSIN**：全球货运标识符
- **GINC**：全球托运货物标识符
- **GS1物流标签**：运输标签标准

### 4.2 ISO 14001

- **ISO 14001:2015**：环境管理体系要求
- **ISO 14064**：温室气体排放核算
- **碳足迹计算**：运输过程碳排放计量
- **绿色物流**：环保运输实践

### 4.3 物流EDI标准

**EDI X12物流交易集**：

| 交易集代码 | 名称 | 描述 |
|-----------|------|------|
| 204 | Motor Carrier Shipment Information | 承运人货运信息 |
| 214 | Transportation Carrier Shipment Status Message | 运输状态消息 |
| 990 | Response to a Load Tender | 装运投标响应 |
| 210 | Motor Carrier Freight Details and Invoice | 货运详情和发票 |
| 215 | Motor Carrier Pickup Manifest | 提货清单 |
| 217 | Motor Carrier Loading and Route Guide | 装载和路线指南 |

**EDIFACT物流消息**：

| 消息代码 | 名称 | 描述 |
|---------|------|------|
| IFTMIN | Instruction Message | 运输指示消息 |
| IFTMBC | Booking Confirmation Message | 订舱确认消息 |
| IFTMAN | Arrival Notice Message | 到货通知消息 |
| CUSCAR | Customs Cargo Report Message | 海关货物报告 |
| COPRAR | Container Discharge/Loading Order Message | 集装箱装卸订单 |

---

## 5. 应用场景

### 5.1 干线运输

**场景描述**：
城市之间或区域之间的长途货物运输。

**TMS应用**：

- 线路优化：选择最优运输路线
- 车辆配载：整车/零担配载优化
- 在途跟踪：GPS/GIS实时跟踪
- 异常处理：延误、故障处理

**关键指标**：

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 准点率 | >95% | 按时到达比例 |
| 满载率 | >85% | 车辆利用率 |
| 货损率 | <0.1% | 货损比例 |
| 吨公里成本 | 行业基准 | 单位运输成本 |

### 5.2 城配运输

**场景描述**：
城市内部的货物配送，多点配送。

**TMS应用**：

- 路径规划：多目的地路径优化
- 时间窗管理：满足客户时间要求
- 车辆调度：动态调度调整
- 电子签收：数字化签收确认

**优化策略**：

```text
城配优化目标：
1. 最小化总行驶距离
2. 最小化总配送时间
3. 最大化客户满意度
4. 最小化车辆使用数量

约束条件：
- 车辆容量限制
- 客户时间窗限制
- 司机工作时间限制
- 交通规则限制
```

### 5.3 多式联运

**场景描述**：
两种或多种运输方式的组合运输。

**运输方式组合**：

| 联运类型 | 运输方式 | 适用场景 |
|----------|----------|----------|
| 海铁联运 | 海运+铁路 | 国际贸易 |
| 公铁联运 | 公路+铁路 | 中长距离 |
| 海公联运 | 海运+公路 | 港口配送 |
| 空陆联运 | 空运+公路 | 高价值货物 |

**TMS应用**：

- 运输方式选择：基于成本、时效选择最优组合
- 转运协调：不同运输方式间的衔接
- 全程跟踪：跨运输方式的货物跟踪
- 单证管理：多式联运提单管理

### 5.4 最后一公里配送

**场景描述**：
货物从配送中心到最终客户的最后一段配送。

**TMS应用**：

- 智能分单：自动分配订单到配送员
- 路径优化：配送员路线优化
- 实时跟踪：客户可查看配送进度
- 异常处理：拒收、地址错误处理

**配送模式**：

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| 直送 | 直接配送到客户 | B2B配送 |
| 快递柜 | 配送到自提柜 | B2C住宅 |
| 驿站 | 配送到代收点 | 社区配送 |
| 即时配 | 小时级配送 | 同城即时 |

---

## 6. TMS数据存储与分析

### 6.1 PostgreSQL TMS数据存储

**数据库存储应用场景**：

- **运输订单存储**：订单信息、货物信息、收发货人信息
- **车辆数据存储**：车辆档案、运力信息、维护记录
- **路线数据存储**：路线规划、历史路线、优化记录
- **承运人数据存储**：承运人档案、绩效数据、合同信息
- **运费数据存储**：费率表、计费记录、结算数据
- **跟踪数据存储**：GPS轨迹、状态更新、异常事件
- **TMS统计信息存储**：运输统计、成本分析、绩效报表

**数据库表设计**：

```sql
-- 运输订单表
CREATE TABLE transportation_orders (
    order_id UUID PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    service_level VARCHAR(20),
    status VARCHAR(20) NOT NULL,
    pickup_address JSONB NOT NULL,
    delivery_address JSONB NOT NULL,
    cargo_info JSONB NOT NULL,
    scheduled_pickup TIMESTAMP,
    scheduled_delivery TIMESTAMP,
    actual_pickup TIMESTAMP,
    actual_delivery TIMESTAMP,
    assigned_carrier_id UUID,
    assigned_vehicle_id UUID,
    freight_charge DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 车辆表
CREATE TABLE vehicles (
    vehicle_id UUID PRIMARY KEY,
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(30) NOT NULL,
    capacity_weight DECIMAL(10,2),
    capacity_volume DECIMAL(10,2),
    carrier_id UUID,
    driver_id UUID,
    status VARCHAR(20),
    current_location GEOGRAPHY(POINT),
    last_updated TIMESTAMP
);

-- 路线表
CREATE TABLE routes (
    route_id UUID PRIMARY KEY,
    route_number VARCHAR(50) UNIQUE NOT NULL,
    origin_location JSONB NOT NULL,
    destination_location JSONB NOT NULL,
    waypoints JSONB,
    total_distance DECIMAL(10,2),
    estimated_duration INTEGER,
    vehicle_type_required VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 数据分析应用价值

- 高效存储大规模运输订单和跟踪数据
- 支持运输数据分析和报表生成
- 提供运输全程追溯和追踪
- 支持运输成本分析和优化
- 支持承运人绩效评估

---

## 7. 行业最佳实践

### 7.1 运输优化策略

**装载优化**：

```text
装载优化原则：
1. 重货在下，轻货在上
2. 大货在下，小货在上
3. 先卸后装
4. 充分利用空间
5. 确保货物安全

装载率目标：
- 重量装载率：>90%
- 体积装载率：>85%
- 空间利用率：>80%
```

**路线优化策略**：

1. **聚类分析**：将相近目的地聚类
2. **Sweep算法**：角度扫描算法
3. **节约算法**：Clarke-Wright节约算法
4. **遗传算法**：大规模问题优化
5. **实时调度**：动态调整路线

### 7.2 成本控制实践

**成本控制策略**：

| 成本类型 | 控制策略 | 目标 |
|----------|----------|------|
| 运输成本 | 线路优化、装载优化 | 降低10-15% |
| 燃油成本 | 驾驶行为优化、路线优化 | 降低5-10% |
| 人工成本 | 自动化调度、效率提升 | 降低8-12% |
| 设备成本 | 预防性维护、寿命延长 | 降低5-8% |
| 管理成本 | 系统集成、流程优化 | 降低10-20% |

**KPI管理**：

```text
关键绩效指标：
1. 运输准时率：>95%
2. 订单准确率：>99.5%
3. 货损货差率：<0.1%
4. 客户满意度：>90%
5. 车辆利用率：>85%
6. 成本节约率：年均5-10%
```

---

## 8. 思维导图

```text
TMS Schema
│
├─ 运输订单管理
│   ├─ 订单创建
│   ├─ 订单分配
│   ├─ 订单调度
│   ├─ 订单跟踪
│   └─ 订单完成
│
├─ 路线规划
│   ├─ 路径优化算法
│   ├─ 车辆调度
│   ├─ 装载优化
│   ├─ 时间窗约束
│   └─ 多停靠点规划
│
├─ 承运人管理
│   ├─ 承运人档案
│   ├─ 服务评估
│   ├─ 合同管理
│   ├─ 绩效管理
│   └─ 结算管理
│
├─ 运费计算
│   ├─ 基础运费
│   ├─ 附加费用
│   ├─ 折扣规则
│   ├─ 税费计算
│   └─ 多式联运费用
│
├─ 车辆管理
│   ├─ 车辆档案
│   ├─ 运力管理
│   ├─ 维护记录
│   └─ GPS跟踪
│
└─ 跟踪与监控
    ├─ GPS/GIS跟踪
    ├─ 异常预警
    ├─ 电子签收
    └─ 客户通知
```

---

**参考文档**：

- `../README.md` - 主题概览
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
