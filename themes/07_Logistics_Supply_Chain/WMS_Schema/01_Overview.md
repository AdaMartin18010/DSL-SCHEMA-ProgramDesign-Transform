# WMS Schema概述

## 📑 目录

- [WMS Schema概述](#wms-schema概述)
  - [📑 目录](#-目录)
  - [1. 核心结论](#1-核心结论)
    - [1.1 WMS Schema定义](#11-wms-schema定义)
    - [1.2 标准依据](#12-标准依据)
  - [2. 概念定义](#2-概念定义)
    - [2.1 WMS Schema定义](#21-wms-schema定义)
    - [2.2 核心特征](#22-核心特征)
    - [2.3 Schema分类](#23-schema分类)
  - [3. 仓储管理核心模块](#3-仓储管理核心模块)
    - [3.1 入库管理](#31-入库管理)
    - [3.2 库存管理](#32-库存管理)
    - [3.3 出库管理](#33-出库管理)
    - [3.4 仓库作业](#34-仓库作业)
  - [4. 标准对标](#4-标准对标)
    - [4.1 GS1标准](#41-gs1标准)
    - [4.2 ISO 8000数据质量](#42-iso-8000数据质量)
    - [4.3 Warehousing EDI标准](#43-warehousing-edi标准)
  - [5. 应用场景](#5-应用场景)
    - [5.1 电商仓储](#51-电商仓储)
    - [5.2 冷链仓储](#52-冷链仓储)
    - [5.3 危险品仓储](#53-危险品仓储)
    - [5.4 跨境保税仓](#54-跨境保税仓)
  - [6. WMS数据存储与分析](#6-wms数据存储与分析)
    - [6.1 PostgreSQL WMS数据存储](#61-postgresql-wms数据存储)
    - [6.2 数据分析应用价值](#62-数据分析应用价值)
  - [7. 行业最佳实践](#7-行业最佳实践)
    - [7.1 库位优化策略](#71-库位优化策略)
    - [7.2 作业效率提升](#72-作业效率提升)
  - [8. 思维导图](#8-思维导图)

---

## 1. 核心结论

**物流供应链存在强制性的WMS Schema体系**。

### 1.1 WMS Schema定义

```
WMS_Schema = (Inbound ⊕ Inventory ⊕ Outbound ⊕ Warehouse_Operations) × Supply_Chain_Profile
```

### 1.2 标准依据

- **GS1标准**：全球统一标识系统标准
- **ISO 8000**：数据质量标准
- **Warehousing EDI标准**：EDI X12和EDIFACT仓储相关交易集
- **ISO/IEC 15459**：唯一标识符标准
- **仓库管理系统标准**：MH10.8.2、ISO 28560

---

## 2. 概念定义

### 2.1 WMS Schema定义

**WMS Schema**是描述仓储管理系统（Warehouse Management System）的形式化规范，包括入库管理、库存管理、出库管理、仓库作业等核心模块。

### 2.2 核心特征

1. **标准化**：基于国际仓储和物流标准
2. **可追溯性**：支持库存全程追溯
3. **实时性**：支持实时库存可见
4. **优化性**：支持库位和作业优化
5. **形式化**：数学形式化定义

### 2.3 Schema分类

- **入库Schema**：描述入库流程的数据结构
- **库存Schema**：描述库存和货位的数据结构
- **出库Schema**：描述出库流程的数据结构
- **作业任务Schema**：描述仓库作业任务的数据结构
- **库位Schema**：描述仓库库位和区域的数据结构
- **盘点Schema**：描述库存盘点和差异的数据结构

---

## 3. 仓储管理核心模块

### 3.1 入库管理

**定义**：管理货物从到达仓库到上架完成的整个入库流程。

**包含内容**：

- **预约管理**：入库预约、车辆排队
- **收货作业**：卸货、清点、质检
- **上架作业**：库位分配、上架确认
- **异常处理**：短溢、破损、拒收处理

**入库流程**：

```
预约到达 → 车辆登记 → 卸货 → 清点 → 质检 → 上架 → 入库完成
    ↓           ↓        ↓       ↓       ↓       ↓           ↓
  取消      车辆等待   异常处理  短溢处理  不合格  库位调整    入库确认
```

**关键字段**：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| asn_id | String | 到货通知单唯一标识符 |
| po_number | String | 采购订单号 |
| supplier_id | String | 供应商标识符 |
| expected_date | DateTime | 预计到货日期 |
| actual_date | DateTime | 实际到货日期 |
| items | List | 到货明细 |
| receipt_status | Enum | 收货状态 |
| putaway_status | Enum | 上架状态 |

**ASN（到货通知）结构**：

| 元素 | 必填 | 说明 |
|------|------|------|
| ASN编号 | 是 | 到货通知唯一标识 |
| 采购订单号 | 是 | 关联的PO号 |
| 供应商信息 | 是 | 供应商代码、名称 |
| 预计到货时间 | 是 | 精确到小时 |
| 商品明细 | 是 | SKU、数量、批次 |
| 包装信息 | 否 | 托盘数、箱数 |
| 运输信息 | 否 | 承运商、车牌号 |

### 3.2 库存管理

**定义**：管理仓库内所有货物的存储状态和数量信息。

**包含内容**：

- **库存记录**：SKU级库存、批次库存、序列号库存
- **货位管理**：库位状态、库位容量、库位属性
- **库存移动**：库位间移动、库位调整
- **库存冻结**：质检冻结、盘点冻结、锁定冻结

**库存类型**：

| 库存类型 | 说明 | 适用场景 |
|---------|------|---------|
| 可用库存 | 可正常出库的库存 | 正常销售/生产 |
| 冻结库存 | 被锁定的库存 | 质检、盘点 |
| 在途库存 | 运输中的库存 | 采购在途、调拨在途 |
| 预留库存 | 已分配但尚未出库 | 订单预留 |
| 残次库存 | 有质量问题的库存 | 待处理、退货 |

**库存状态流转**：

```
待收货 → 在库 → 可用 → 预留 → 拣货中 → 已分配 → 已出库
   ↓       ↓      ↓       ↓        ↓         ↓         ↓
 取消   质检    冻结    释放    取消    回库    退库
```

**库存关键指标**：

| 指标 | 计算公式 | 目标值 |
|------|---------|--------|
| 库存准确率 | (1 - |实际-系统|/总库存) x 100% | >99.5% |
| 库存周转率 | 出库成本 / 平均库存成本 | 行业基准 |
| 库存天数 | 平均库存 / 日均出库量 | <30天 |
| 滞销品比例 | 滞销品SKU数 / 总SKU数 | <10% |

### 3.3 出库管理

**定义**：管理从订单接收到货物发运的整个出库流程。

**包含内容**：

- **订单处理**：订单分配、波次计划、优先级管理
- **拣货作业**：拣货路径、拣货方式、拣货确认
- **包装作业**：包装分配、称重、贴标
- **发货作业**：装车、发运、回单

**出库流程**：

```
订单导入 → 库存分配 → 波次创建 → 拣货 → 复核 → 包装 → 称重 → 装车 → 发运
    ↓          ↓          ↓        ↓       ↓       ↓       ↓       ↓       ↓
  订单异常   缺货处理   波次优化   拣货异常  差异处理  包材选择  运费计算  装车优化  回单确认
```

**拣货方式对比**：

| 拣货方式 | 描述 | 适用场景 | 效率 |
|---------|------|---------|------|
| 订单拣货 | 按单拣货 | 大订单、B2B | 中等 |
| 批量拣货 | 合并拣货后分拣 | 小订单、B2C | 高 |
| 分区拣货 | 仓库分区并行拣货 | 大仓库 | 高 |
| 接力拣货 | 分区接力完成 | 长巷道 | 中等 |
| 播种拣货 | 批量拣货到播种墙 | 多订单 | 高 |

**波次计划策略**：

```
波次创建策略：
1. 时间策略：每2小时创建一波
2. 订单量策略：每波200-500单
3. 承运商策略：按承运商分波
4. 优先级策略：优先订单单独成波
5. 区域策略：按配送区域分波

波次优化目标：
- 最小化拣货路径
- 最大化拣货密度
- 平衡各区域工作量
- 满足时效要求
```

### 3.4 仓库作业

**定义**：管理仓库内的各类作业任务和人员设备。

**包含内容**：

- **任务管理**：任务创建、任务分配、任务跟踪
- **人员管理**：人员技能、工作量分配、绩效考核
- **设备管理**：叉车、输送线、自动化设备
- **作业监控**：作业进度、异常预警、效率分析

**作业类型**：

| 作业类型 | 代码 | 说明 |
|---------|------|------|
| 收货 | RCPT | 入库收货作业 |
| 上架 | PUTW | 货物上架作业 |
| 补货 | REPL | 补货作业 |
| 拣货 | PICK | 订单拣货作业 |
| 盘点 | CYCL | 周期盘点作业 |
| 移库 | MOVE | 库位移动作业 |
| 包装 | PACK | 包装作业 |
| 装车 | LOAD | 装车作业 |

**任务分配算法**：

```
任务分配优先级：
1. 任务优先级（高>中>低）
2. 截止时间（先到期的优先）
3. 距离最近（就近分配）
4. 人员技能匹配
5. 工作量平衡

分配策略：
- 智能推荐：系统推荐最优人员
- 自动分配：按规则自动分配
- 手动分配：主管手动分配
- 抢单模式：人员自主抢单
```

---

## 4. 标准对标

### 4.1 GS1标准

- **GTIN**：全球贸易项目代码
- **SSCC**：系列货运包装箱代码
- **GLN**：全球位置码（仓库位置标识）
- **GS1-128**：条码标准
- **EPCIS**：电子产品代码信息服务

**GS1在WMS中的应用**：

| GS1标准 | WMS应用场景 | 效益 |
|--------|------------|------|
| GTIN | SKU标识、库存管理 | 统一商品编码 |
| SSCC | 托盘/箱管理、收发货 | 追踪货物流转 |
| GLN | 仓库/库位标识 | 精确位置管理 |
| GS1-128 | 条码标签打印扫描 | 提高作业效率 |
| EPCIS | 库存事件追踪 | 全程可追溯 |

### 4.2 ISO 8000数据质量

**标准名称**：
Data quality — Part 1: Overview

**数据质量维度**：

| 维度 | 定义 | WMS应用 |
|------|------|---------|
| 准确性 | 数据与真实值的一致程度 | 库存数量准确 |
| 完整性 | 必需数据的完整程度 | 必填字段完整 |
| 一致性 | 不同系统间数据一致 | 库存同步一致 |
| 时效性 | 数据的更新及时程度 | 实时库存更新 |
| 有效性 | 数据符合定义规则 | 数据格式正确 |
| 唯一性 | 数据记录的唯一程度 | SKU唯一标识 |

**数据质量检查规则**：

```
库存数据质量检查：
1. 库存数量 >= 0
2. 库位编码格式正确
3. SKU编码在商品主数据中存在
4. 批次号格式符合规则
5. 库存状态值在有效范围内
6. 最后更新时间 < 24小时

入库数据质量检查：
1. ASN编号唯一
2. 供应商编码存在
3. 商品数量 > 0
4. 预计到货日期 >= 今天
5. 商品编码有效
```

### 4.3 Warehousing EDI标准

**EDI X12仓储交易集**：

| 交易集代码 | 名称 | 描述 |
|-----------|------|------|
| 940 | Warehouse Shipping Order | 仓库发货订单 |
| 943 | Warehouse Stock Transfer Shipment Advice | 库存转移发货通知 |
| 944 | Warehouse Stock Transfer Receipt Advice | 库存转移收货通知 |
| 945 | Warehouse Shipping Advice | 仓库发货通知 |
| 946 | Delivery Information Message | 配送信息消息 |
| 947 | Warehouse Inventory Adjustment Advice | 库存调整通知 |

**EDIFACT仓储消息**：

| 消息代码 | 名称 | 描述 |
|---------|------|------|
| RECADV | Receiving Advice Message | 收货通知 |
| RESADV | Reservation Advice Message | 预留通知 |
| INVRPT | Inventory Report Message | 库存报告 |
| SLSRPT | Sales Data Report Message | 销售数据报告 |
| DELJIT | Delivery Just In Time Message | 准时交付 |
| DELFOR | Delivery Schedule Message | 交付计划 |

---

## 5. 应用场景

### 5.1 电商仓储

**场景描述**：
支持B2C订单的快速履约，高SKU、小批量、高频次特点。

**WMS应用**：

- 波次拣货：支持多订单合并拣货
- 播种墙：支持批量分拣
- 快递面单：自动打印快递单
- 退货处理：支持退货质检上架

**关键指标**：

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 日单处理能力 | >10万单 | 峰值处理能力 |
| 订单履约时效 | <24小时 | 从下单到出库 |
| 拣货准确率 | >99.9% | 减少错发 |
| 发货及时率 | >98% | 按时发货比例 |

### 5.2 冷链仓储

**场景描述**：
温控商品的存储，需要严格的温度监控和追溯。

**WMS应用**：

- 温控管理：多温区管理（冷冻/冷藏/恒温）
- 温度监控：实时温度采集、异常报警
- 效期管理：先进先出、效期预警
- 追溯管理：全程温度追溯链

**温控要求**：

| 温区 | 温度范围 | 适用商品 |
|------|---------|---------|
| 冷冻 | -18℃以下 | 肉类、海鲜、冰淇淋 |
| 冷藏 | 0-4℃ | 生鲜、乳制品、熟食 |
| 恒温 | 15-25℃ | 药品、化妆品 |
| 阴凉 | 不超过20℃ | 药品、保健品 |

### 5.3 危险品仓储

**场景描述**：
危险化学品的存储，需要严格的安全管理和合规。

**WMS应用**：

- 分类存储：按危险品类别分区
- 隔离管理：不相容品隔离
- 限量存储：最大存储量控制
- 安全库存：安全库存预警
- 应急处理：应急响应流程

**危险品分类存储要求**：

| 类别 | 存储要求 | 隔离要求 |
|------|---------|---------|
| 爆炸品 | 专用仓库 | 与其他类别隔离 |
| 易燃液体 | 通风良好 | 远离火源、氧化剂 |
| 氧化剂 | 阴凉干燥 | 远离易燃品 |
| 有毒品 | 专用区域 | 隔离存放 |
| 腐蚀品 | 耐腐蚀地面 | 远离其他类别 |

### 5.4 跨境保税仓

**场景描述**：
跨境电商保税进口商品的存储，涉及海关监管。

**WMS应用**：

- 账册管理：海关账册管理
- 核注清单：核注清单生成
- 库存申报：库存数据申报海关
- 三单对碰：订单/支付/物流对碰

**保税业务流程**：

```
商品备案 → 报关入区 → 保税存储 → 订单生成 → 三单对碰 → 清关出库 → 国内配送
    ↓         ↓         ↓          ↓          ↓          ↓          ↓
  商品信息  报关单    库存管理   电商平台   数据核对   缴纳关税   快递发货
```

---

## 6. WMS数据存储与分析

### 6.1 PostgreSQL WMS数据存储

**数据库存储应用场景**：

- **入库数据存储**：ASN、收货记录、上架记录
- **库存数据存储**：库存记录、货位占用、批次信息
- **出库数据存储**：订单、波次、拣货记录、发货记录
- **作业数据存储**：任务记录、人员绩效、设备使用
- **盘点数据存储**：盘点计划、盘点记录、差异记录
- **追溯数据存储**：库存移动历史、批次追溯链

**数据库表设计**：

```sql
-- 库存主表
CREATE TABLE inventory (
    inventory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) NOT NULL,
    sku_name VARCHAR(200),
    batch_number VARCHAR(50),
    lot_number VARCHAR(50),
    serial_number VARCHAR(100),
    
    -- 货位信息
    location_code VARCHAR(50) NOT NULL,
    zone_code VARCHAR(20),
    area_code VARCHAR(20),
    
    -- 数量
    quantity INTEGER NOT NULL DEFAULT 0,
    allocated_quantity INTEGER DEFAULT 0,
    picked_quantity INTEGER DEFAULT 0,
    available_quantity INTEGER GENERATED ALWAYS AS (quantity - allocated_quantity - picked_quantity) STORED,
    
    -- 状态
    inventory_status VARCHAR(20) NOT NULL, -- Available, Frozen, Blocked, Quarantine
    quality_status VARCHAR(20), -- Good, Damaged, Expired, Hold
    
    -- 效期
    manufacturing_date DATE,
    expiration_date DATE,
    received_date DATE NOT NULL,
    
    -- 属性
    owner_code VARCHAR(50),
    supplier_code VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(sku, location_code, batch_number, lot_number)
);

-- 货位主表
CREATE TABLE locations (
    location_code VARCHAR(50) PRIMARY KEY,
    location_name VARCHAR(100),
    
    -- 层级
    zone_code VARCHAR(20) NOT NULL,
    area_code VARCHAR(20) NOT NULL,
    aisle VARCHAR(10),
    bay VARCHAR(10),
    level VARCHAR(10),
    position VARCHAR(10),
    
    -- 类型
    location_type VARCHAR(20), -- Picking, Bulk, Receiving, Shipping, CrossDock
    location_class VARCHAR(20), -- Fast, Medium, Slow
    
    -- 容量
    max_weight DECIMAL(10,2),
    max_volume DECIMAL(10,4),
    max_pallets INTEGER,
    
    -- 尺寸
    length DECIMAL(8,2),
    width DECIMAL(8,2),
    height DECIMAL(8,2),
    
    -- 属性
    abc_class VARCHAR(1),
    temperature_zone VARCHAR(20),
    hazardous_class VARCHAR(20),
    
    -- 状态
    status VARCHAR(20) DEFAULT 'Empty', -- Empty, Occupied, Full, Blocked
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 入库记录表
CREATE TABLE receipts (
    receipt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    asn_id VARCHAR(50),
    asn_number VARCHAR(50),
    
    -- 来源
    po_number VARCHAR(50),
    supplier_code VARCHAR(50),
    supplier_name VARCHAR(100),
    
    -- 时间
    expected_date DATE,
    actual_date DATE,
    
    -- 状态
    receipt_status VARCHAR(20) NOT NULL, -- Pending, Receiving, Received, Putaway, Completed
    
    -- 合计
    total_lines INTEGER,
    total_quantity INTEGER,
    total_cartons INTEGER,
    total_pallets INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 入库明细表
CREATE TABLE receipt_lines (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id UUID REFERENCES receipts(receipt_id),
    line_number INTEGER NOT NULL,
    
    sku VARCHAR(50) NOT NULL,
    sku_name VARCHAR(200),
    
    expected_quantity INTEGER,
    received_quantity INTEGER DEFAULT 0,
    accepted_quantity INTEGER DEFAULT 0,
    rejected_quantity INTEGER DEFAULT 0,
    
    batch_number VARCHAR(50),
    lot_number VARCHAR(50),
    manufacturing_date DATE,
    expiration_date DATE,
    
    quality_status VARCHAR(20),
    putaway_location VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 出库订单表
CREATE TABLE outbound_orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_type VARCHAR(20), -- Sales, Transfer, Return
    
    -- 客户
    customer_code VARCHAR(50),
    customer_name VARCHAR(100),
    customer_address JSONB,
    
    -- 时间
    order_date TIMESTAMP,
    required_ship_date DATE,
    promised_ship_date DATE,
    actual_ship_date DATE,
    
    -- 优先级
    priority INTEGER DEFAULT 5,
    
    -- 状态
    order_status VARCHAR(20) NOT NULL, -- New, Allocated, Picked, Packed, Shipped, Delivered
    
    -- 波次
    wave_id UUID,
    wave_number VARCHAR(50),
    
    -- 承运商
    carrier_code VARCHAR(50),
    carrier_name VARCHAR(100),
    tracking_number VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_inventory_sku ON inventory(sku);
CREATE INDEX idx_inventory_location ON inventory(location_code);
CREATE INDEX idx_inventory_batch ON inventory(batch_number);
CREATE INDEX idx_inventory_status ON inventory(inventory_status);
CREATE INDEX idx_locations_zone ON locations(zone_code);
CREATE INDEX idx_receipts_status ON receipts(receipt_status);
CREATE INDEX idx_receipts_date ON receipts(actual_date);
CREATE INDEX idx_orders_status ON outbound_orders(order_status);
CREATE INDEX idx_orders_wave ON outbound_orders(wave_id);
```

### 6.2 数据分析应用价值

- 高效存储大规模库存和交易数据
- 支持库存数据分析和报表生成
- 提供库存全程追溯和追踪
- 支持库存优化和预测分析
- 支持作业效率评估

---

## 7. 行业最佳实践

### 7.1 库位优化策略

**ABC分类法**：

```
ABC分类标准：
A类：销售额/出库量占比约80%，SKU占比约20%
B类：销售额/出库量占比约15%，SKU占比约30%
C类：销售额/出库量占比约5%，SKU占比约50%

库位分配策略：
A类：黄金区域（靠近出入口），拣货位充足
B类：一般区域，标准配置
C类：偏远区域，集中存放
```

**库位优化目标**：

| 目标 | 策略 | 效果 |
|------|------|------|
| 最小化拣货路径 | 热销品靠近包装区 | 减少30%行走距离 |
| 最大化空间利用 | 垂直空间充分利用 | 提升20%库容 |
| 减少补货次数 | 拣货位容量充足 | 减少50%补货 |
| 平衡工作量 | 各区域均匀分布 | 提升整体效率 |

### 7.2 作业效率提升

**效率提升策略**：

| 策略 | 具体措施 | 目标提升 |
|------|----------|---------|
| 流程优化 | 简化作业步骤 | 20-30% |
| 系统优化 | 减少系统等待 | 15-20% |
| 布局优化 | 优化仓库布局 | 25-35% |
| 设备升级 | 自动化设备 | 40-60% |
| 人员培训 | 技能培训 | 10-15% |

**KPI管理**：

```
关键绩效指标：
1. 收货效率：>50托盘/人/小时
2. 上架效率：>30托盘/人/小时
3. 拣货效率：>150行/人/小时
4. 包装效率：>80单/人/小时
5. 库存准确率：>99.5%
6. 订单履约时效：>95%按时履约
7. 作业差错率：<0.1%
```

---

## 8. 思维导图

```
WMS Schema
│
├─ 入库管理
│   ├─ 预约管理
│   ├─ 收货作业
│   ├─ 质检作业
│   ├─ 上架作业
│   └─ 异常处理
│
├─ 库存管理
│   ├─ 库存记录
│   ├─ 货位管理
│   ├─ 库存移动
│   ├─ 库存冻结
│   └─ 效期管理
│
├─ 出库管理
│   ├─ 订单处理
│   ├─ 波次计划
│   ├─ 拣货作业
│   ├─ 包装作业
│   └─ 发货作业
│
├─ 仓库作业
│   ├─ 任务管理
│   ├─ 人员管理
│   ├─ 设备管理
│   └─ 作业监控
│
├─ 盘点管理
│   ├─ 盘点计划
│   ├─ 盘点执行
│   ├─ 差异处理
│   └─ 盘点分析
│
└─ 系统管理
    ├─ 基础数据
    ├─ 用户权限
    ├─ 接口管理
    └─ 报表分析
```

---

**参考文档**：

- `../README.md` - 主题概览
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
