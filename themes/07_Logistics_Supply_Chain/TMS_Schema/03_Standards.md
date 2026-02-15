# TMS Schema标准对标

## 📑 目录

- [TMS Schema标准对标](#tms-schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. GS1标准体系](#2-gs1标准体系)
    - [2.1 GS1物流标识标准](#21-gs1物流标识标准)
    - [2.2 GS1物流标签标准](#22-gs1物流标签标准)
    - [2.3 GS1 EDI标准](#23-gs1-edi标准)
  - [3. ISO 14001环境管理标准](#3-iso-14001环境管理标准)
    - [3.1 ISO 14001:2015核心要求](#31-iso-140012015核心要求)
    - [3.2 绿色物流实践](#32-绿色物流实践)
    - [3.3 碳排放核算](#33-碳排放核算)
  - [4. 物流EDI标准](#4-物流edi标准)
    - [4.1 EDI X12物流交易集](#41-edi-x12物流交易集)
    - [4.2 EDIFACT物流消息](#42-edifact物流消息)
    - [4.3 EDI消息映射](#43-edi消息映射)
  - [5. 智能交通系统标准](#5-智能交通系统标准)
    - [5.1 ISO/TS 14813](#51-isots-14813)
    - [5.2 SAE J2735](#52-sae-j2735)
    - [5.3 IEEE 1512](#53-ieee-1512)
  - [6. 危险品运输标准](#6-危险品运输标准)
    - [6.1 ADR（欧洲道路危险品运输）](#61-adr欧洲道路危险品运输)
    - [6.2 IMDG Code（国际海运危险品）](#62-imdg-code国际海运危险品)
    - [6.3 IATA DGR（航空危险品规则）](#63-iata-dgr航空危险品规则)
  - [7. 标准对比矩阵](#7-标准对比矩阵)
  - [8. 标准实施指南](#8-标准实施指南)
    - [8.1 实施步骤](#81-实施步骤)
    - [8.2 合规检查清单](#82-合规检查清单)
  - [9. 标准发展趋势](#9-标准发展趋势)

---

## 1. 标准体系概述

TMS Schema标准体系分为五个层次：

1. **GS1标准体系**：全球统一标识系统，用于货物和运输单元标识
2. **ISO 14001环境管理**：环境管理体系和碳排放核算标准
3. **物流EDI标准**：EDI X12和EDIFACT物流相关交易集和消息
4. **智能交通系统标准**：ITS架构和数据交换标准
5. **危险品运输标准**：ADR、IMDG、IATA危险品运输规则

---

## 2. GS1标准体系

### 2.1 GS1物流标识标准

**标准名称**：
GS1 Identification Keys for Logistics

**核心标识符**：

| 标识符 | 名称 | 长度 | 应用场景 |
|--------|------|------|----------|
| SSCC | 系列货运包装箱代码 | 18位 | 运输单元、托盘、集装箱 |
| GSIN | 全球货运标识符 | 17位 | 多式联运货物 |
| GINC | 全球托运货物标识符 | 最多30位 | 托运货物分组 |
| GRAI | 全球可回收资产标识符 | 最多30位 | 可回收运输资产 |
| GIAI | 全球单个资产标识符 | 最多30位 | 车辆、设备等 |

**SSCC结构**：

```
SSCC = 扩展位(1位) + GS1公司前缀(7-10位) + 序列号(9-6位) + 校验位(1位)

示例：3 1234567 890123456 0
      │ └─┬───┘ └────┬────┘ │
      │   │          │      └─ 校验位
      │   │          └──────── 序列号
      │   └─────────────────── GS1公司前缀
      └─────────────────────── 扩展位
```

**TMS应用**：

```dsl
schema TransportUnit {
  sscc: String @required @pattern("^[0-9]{18}$")
  gs1_company_prefix: String @required
  serial_number: String @required
  check_digit: String @required @computed("calculate_sscc_check_digit")
  
  unit_type: Enum { Pallet, Carton, Container, Roll, Drum, Bundle }
  contents: List<SSCC_Content]
  
  // 物理属性
  weight: WeightInfo
  dimensions: Dimensions
  
  // 关联信息
  parent_sscc: Optional[String]
  child_ssccs: List<String]
  
  // 运输信息
  associated_order_id: String
  origin_location: String
  destination_location: String
  
  // 状态
  status: Enum { Created, In_Transit, Delivered, Received }
} @standard("GS1")
```

### 2.2 GS1物流标签标准

**标准名称**：
GS1 Logistics Label (GTL)

**标签规格**：

| 元素 | 规格 | 说明 |
|------|------|------|
| 标签尺寸 | 148mm x 210mm (A5) | 标准物流标签尺寸 |
| 条码类型 | GS1-128 (EAN/UCC-128) | 支持GS1应用标识符 |
| 人类可读 | SSCC + 其他信息 | 便于人工识别 |
| 条码高度 | 最小32mm | 确保扫描可靠性 |

**标签区域**：

```
┌─────────────────────────────────────────────────┐
│  供应商区 (Ship From)                           │
│  - 供应商名称、地址                              │
│  - GS1 GLN                                      │
├─────────────────────────────────────────────────┤
│  客户区 (Ship To)                               │
│  - 客户名称、地址                                │
│  - 收货地点GLN                                  │
├─────────────────────────────────────────────────┤
│  承运商区 (Carrier)                             │
│  - 承运商信息                                    │
│  - 路线/区域代码                                │
├─────────────────────────────────────────────────┤
│  SSCC条码区                                     │
│  ┌─────────────────────────────────────────┐   │
│  │  [GS1-128 Barcode with SSCC]            │   │
│  │  (00) 3 1234567 890123456 0             │   │
│  └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  附加信息区                                     │
│  - 订单号、货物品类、重量等                      │
└─────────────────────────────────────────────────┘
```

**应用标识符**：

| AI | 名称 | 格式 | 示例 |
|----|------|------|------|
| 00 | SSCC | n2+n18 | (00)312345678901234560 |
| 401 | 托运单号 | n3+an..30 | (401)SHIP123456 |
| 402 | 发货通知单号 | n3+n17 | (402)12345678901234567 |
| 403 | 路线代码 | n3+an..30 | (403)ROUTE-A1 |
| 410 | 发货地GLN | n3+n13 | (410)1234567890123 |
| 411 | 收货地GLN | n3+n13 | (411)9876543210987 |
| 412 | 采购方GLN | n3+n13 | (412)5555555555555 |
| 413 | 供应商GLN | n3+n13 | (413)6666666666666 |
| 420 | 发货地邮编 | n3+an..20 | (420)12345 |
| 421 | 发货地邮编+国家 | n3+n3+an..9 | (421)84012345 |

### 2.3 GS1 EDI标准

**标准名称**：
GS1 EDI Standards for Logistics

**GS1 EDI消息类型**：

| 消息代码 | 名称 | 描述 | 对应X12 |
|---------|------|------|---------|
| DESADV | Despatch Advice | 发货通知 | 856 |
| IFTMIN | Instruction | 运输指示 | 304 |
| IFTMBC | Booking Confirmation | 订舱确认 | 990/997 |
| IFTMAN | Arrival Notice | 到货通知 | 214 |
| IFTMCS | Instruction Contract Status | 合同状态 | - |
| COPRAR | Container Discharge/Loading | 集装箱装卸 | - |
| COARRI | Container Arrival/Departure | 集装箱到离 | - |
| CODECO | Container Gate-In/Gate-Out | 集装箱进出门 | 322 |
| COPINO | Container Pre-Gate Notice | 集装箱预进场 | - |
| BAPLIE | Bayplan/Stowage Plan | 配载图 | - |

---

## 3. ISO 14001环境管理标准

### 3.1 ISO 14001:2015核心要求

**标准名称**：
Environmental management systems - Requirements with guidance for use

**核心要素**：

| 条款 | 要求 | TMS应用 |
|------|------|---------|
| 4.1 理解组织环境 | 识别内外部环境问题 | 分析运输环境影响因素 |
| 4.2 理解相关方需求 | 识别利益相关方要求 | 客户绿色物流要求 |
| 4.3 确定EMS范围 | 界定环境管理体系范围 | 运输运营环境范围 |
| 5.1 领导作用和承诺 | 管理层环境承诺 | 绿色物流战略 |
| 6.1 应对风险和机遇 | 环境风险评估 | 运输环境风险识别 |
| 6.2 环境目标 | 制定可测量的目标 | 碳减排目标设定 |
| 7.1 资源 | 提供必要资源 | 绿色运输投资 |
| 8.1 运行策划和控制 | 环境运行控制 | 运输过程环境控制 |
| 9.1 监视、测量、分析 | 环境绩效监测 | 碳排放监测 |
| 9.3 管理评审 | 定期管理评审 | 环境绩效评审 |

**环境方针示例**：

```
环境方针声明：

我们致力于通过以下措施减少运输活动对环境的影响：

1. 持续优化运输路线，减少空驶和无效运输
2. 优先选择低碳排放的运输方式和车辆
3. 投资清洁能源车辆和替代燃料技术
4. 实施车辆维护计划，确保最佳燃油效率
5. 培训司机采用环保驾驶技术
6. 与供应商合作，推动绿色供应链实践
7. 定期监测和报告碳排放数据
8. 遵守所有适用的环境法律法规

我们设定以下环境目标：
- 到2030年，单位运输碳排放减少50%
- 到2025年，车队中电动/混动车辆占比达到30%
- 每年燃油效率提升5%
```

### 3.2 绿色物流实践

**绿色运输策略**：

| 策略类别 | 具体措施 | 预期效果 |
|----------|----------|----------|
| 车辆技术 | 电动车、混动车、天然气车 | 减排30-50% |
| 路线优化 | 智能路径规划、装载优化 | 减排10-20% |
| 模式转换 | 公转铁、公转水 | 减排50-70% |
| 驾驶行为 | 经济驾驶培训 | 节油5-15% |
| 车辆维护 | 定期保养、胎压监测 | 节油3-8% |
| 替代燃料 | 生物柴油、氢燃料 | 减排40-90% |

### 3.3 碳排放核算

**ISO 14064碳核算**：

| 范围 | 排放源 | 核算方法 |
|------|--------|----------|
| 范围1 | 自有车辆燃油燃烧 | 燃油消耗量 x 排放因子 |
| 范围2 | 外购电力 | 电量 x 电网排放因子 |
| 范围3 | 外包运输、员工通勤 | 基于活动数据计算 |

**排放因子参考值**：

| 燃料类型 | 排放因子 (kg CO2e/L) | 排放因子 (kg CO2e/kg) |
|----------|---------------------|----------------------|
| 柴油 | 2.68 | 3.17 |
| 汽油 | 2.31 | 3.15 |
| 天然气（CNG） | - | 2.75 |
| 生物柴油 (B100) | 0.27 | 0.32 |
| 电力 | 0.5-0.8 kg CO2e/kWh | - |

---

## 4. 物流EDI标准

### 4.1 EDI X12物流交易集

**交易集列表**：

| 交易集 | 名称 | 用途 | 关键段 |
|--------|------|------|--------|
| 204 | Motor Carrier Shipment Information | 承运人货运信息 | B2, B12, N1, N3, N4, G61, OID, AT8 |
| 214 | Transportation Carrier Shipment Status Message | 运输状态消息 | B10, L11, N1, AT7, MS1, MS2, AT8 |
| 990 | Response to a Load Tender | 装运投标响应 | B1, L3, N1, N3, N4 |
| 210 | Motor Carrier Freight Details and Invoice | 货运详情和发票 | B3, C2, C3, N1, N3, N4, LX, L1 |
| 215 | Motor Carrier Pickup Manifest | 提货清单 | B10, N1, N3, N4, G61, AT7 |
| 217 | Motor Carrier Loading and Route Guide | 装载和路线指南 | B9, B9A, N1, N3, N4, G61 |
| 300 | Reservation (Booking Request) | 订舱请求 | B1, V5, N1, N3, N4, G61, R4 |
| 301 | Confirmation (Ocean) | 订舱确认 | B1, V9, Y2, N1, R4 |
| 303 | Booking Cancellation (Ocean) | 订舱取消 | B1, V9, N1, R4 |
| 304 | Shipping Instructions | 装运指示 | B1, V9, Y2, N1, R4, L0, L1 |
| 309 | Customs Manifest | 海关舱单 | B1, Y2, N1, R4, M10, P4 |
| 310 | Freight Receipt and Invoice (Ocean) | 海运收据和发票 | B3, C2, C3, N1, R4, LX, L0, L1 |
| 322 | Terminal Operations and Intermodal Ramp Activity | 码头作业和多式联运 | B17, N1, N9, R4, V1, V9 |

**214交易集结构**：

```
ST*214*0001
B10*PRO123456*SHP789012*CC
L11*BOL345678*BM
N1*SH*ABC Manufacturing
N3*123 Industrial Blvd
N4*Chicago*IL*60601*US
N1*CN*XYZ Distribution
N3*456 Commerce St
N4*Los Angeles*CA*90001*US
AT7*X3*NS***20250115*1430*LT
MS1*Los Angeles*CA*US
MS2*CAR123*TRUCK
AT8*G*L*5000*500
SE*14*0001
```

**状态代码（AT7段）**：

| 代码 | 名称 | 描述 |
|------|------|------|
| X1 | Arrived at Pickup Location | 到达取货地点 |
| X3 | Arrived at Delivery Location | 到达送货地点 |
| X6 | En Route to Delivery Location | 前往送货地点 |
| AF | Freight Picked Up | 货物已取 |
| AG | Estimated to Arrive | 预计到达 |
| D1 | Completed Unloading at Delivery Location | 完成卸货 |
| NS | Normal Status | 正常状态 |
| XD | Arrived at Destination | 到达目的地 |

### 4.2 EDIFACT物流消息

**消息列表**：

| 消息代码 | 名称 | 描述 | 应用场景 |
|---------|------|------|----------|
| IFTMIN | Instruction Message | 运输指示 | 下达运输指令 |
| IFTMBC | Booking Confirmation Message | 订舱确认 | 确认订舱 |
| IFTMAN | Arrival Notice Message | 到货通知 | 通知到货 |
| IFTMCS | Contract Status Message | 合同状态 | 合同状态更新 |
| IFTCCA | Consignment Contract Advice | 托运合同通知 | 合同信息 |
| IFTDGN | Dangerous Goods Notification | 危险品通知 | 危险品运输 |
| COPRAR | Container Discharge/Loading Order | 集装箱装卸订单 | 港口作业 |
| COARRI | Container Arrival/Departure | 集装箱到离 | 集装箱追踪 |
| CODECO | Container Gate-In/Gate-Out | 集装箱进出门 | 堆场管理 |
| COPINO | Container Pre-Gate Notice | 集装箱预进场 | 预约进场 |
| BAPLIE | Bayplan/Stowage Plan | 配载图 | 船舶配载 |
| MOVINS | Stowage Instruction | 积载指示 | 装船指示 |
| CASRES | Cargo Summary | 货物汇总 | 货物统计 |
| CUSCAR | Customs Cargo Report | 海关货物报告 | 海关申报 |

**IFTMIN消息结构**：

```
UNB+UNOA:3+SENDER+RECEIVER+250115:1430+1234567'
UNH+1+IFTMIN:D:21A:UN'
BGM+610+SHIP001+9'
DTM+137:20250115:102'
TSR++30'
FTX+AAI+++Please handle with care'
TDT+20+1++3+TRUCK+12345:172:87'
LOC+5+USCHI:139:6+Chicago'
LOC+8+USLAX:139:6+Los Angeles'
DTM+133:20250116:102'
NAD+CZ+12345::87+ABC Manufacturing'
CTA+IC+:John Smith'
COM+555-0100:TE'
NAD+CN+67890::87+XYZ Distribution'
CTA+IC+:Jane Doe'
GID+1+10:CT'
FTX+AAA+++Electronic equipment'
MEA+WT++KGM:5000'
MEA+VOL++MTQ:25'
PCI+18+SSCC'
GIN+BJ+312345678901234560'
UNT+22+1'
UNZ+1+1234567'
```

### 4.3 EDI消息映射

**X12与EDIFACT对照**：

| 业务场景 | EDI X12 | EDIFACT |
|---------|---------|---------|
| 订舱请求 | 300 | IFTMBF |
| 订舱确认 | 301 | IFTMBC |
| 运输指示 | 304 | IFTMIN |
| 发货通知 | 856 | DESADV |
| 运输状态 | 214 | IFTSTA |
| 运费发票 | 210 | IFTFCC |
| 货物追踪 | 214 | COPRAR |
| 集装箱到离 | 322 | COARRI |

---

## 5. 智能交通系统标准

### 5.1 ISO/TS 14813

**标准名称**：
Transport information and control systems - Reference model architecture(s) for the TICS sector

**ITS架构层次**：

| 层次 | 名称 | 功能 | TMS应用 |
|------|------|------|---------|
| 1 | 企业层 | 业务目标、政策 | 运输策略规划 |
| 2 | 运输层 | 运输服务管理 | 运输计划管理 |
| 3 | 通信层 | 数据传输 | EDI/数据交换 |
| 4 | 处理层 | 数据处理 | TMS核心处理 |
| 5 | 道路层 | 道路基础设施 | 路线信息 |
| 6 | 车辆层 | 车辆系统 | 车辆追踪 |
| 7 | 感知层 | 传感器数据 | 位置采集 |

### 5.2 SAE J2735

**标准名称**：
Dedicated Short Range Communications (DSRC) Message Set Dictionary

**消息集**：

| 消息ID | 名称 | 描述 |
|--------|------|------|
| BSM | Basic Safety Message | 基本安全消息 |
| SPAT | Signal Phase and Timing | 信号相位和配时 |
| MAP | Map Data | 地图数据 |
| SRM | Signal Request Message | 信号请求消息 |
| SSM | Signal Status Message | 信号状态消息 |
| PSM | Personal Safety Message | 个人安全消息 |
| RSA | Roadside Alert | 路侧警报 |
| TIM | Traveler Information Message | 出行者信息 |

### 5.3 IEEE 1512

**标准名称**：
Common Traffic Incident Management Message Sets

**消息集**：

| 消息类型 | 用途 | 数据元素 |
|---------|------|---------|
| 事故报告 | 交通事故信息 | 位置、类型、严重程度 |
| 道路封闭 | 道路封闭信息 | 路段、方向、预计时长 |
| 作业区域 | 施工作业信息 | 位置、时间、影响 |
| 天气事件 | 恶劣天气信息 | 类型、范围、建议 |

---

## 6. 危险品运输标准

### 6.1 ADR（欧洲道路危险品运输）

**适用范围**：
国际道路危险品运输（欧洲）

**危险品分类**：

| 类别 | 名称 | 示例 |
|------|------|------|
| 1 | 爆炸品 | 炸药、烟花 |
| 2 | 气体 | 压缩气体、液化气 |
| 3 | 易燃液体 | 汽油、酒精 |
| 4 | 易燃固体 | 磷、硫 |
| 5 | 氧化剂和有机过氧化物 | 过氧化氢 |
| 6 | 毒性物质和感染性物质 | 农药、病毒样本 |
| 7 | 放射性物质 | 铀、钴-60 |
| 8 | 腐蚀性物质 | 硫酸、氢氧化钠 |
| 9 | 杂项危险品 | 锂电池、磁性材料 |

**包装要求**：

| 包装等级 | 危险程度 | 包装要求 |
|---------|---------|---------|
| I | 高危险 | 严格包装 |
| II | 中等危险 | 标准包装 |
| III | 低危险 | 基本包装 |

### 6.2 IMDG Code（国际海运危险品）

**适用范围**：
国际海运危险品运输

**关键要求**：

| 要求 | 说明 | TMS应用 |
|------|------|---------|
| 正确运输名称 | 使用联合国正式名称 | 货物描述验证 |
| 分类 | 9大类危险品分类 | 自动分类检查 |
| 包装 | IMDG包装规范 | 包装合规验证 |
| 标记和标签 | 9类标签+海洋污染物标记 | 标签生成 |
| 运输文件 | 危险品申报单 | 文档生成 |
| 积载和隔离 | 船舶积载图 | 积载规划 |

### 6.3 IATA DGR（航空危险品规则）

**适用范围**：
航空危险品运输

**限制说明**：

| 项目 | 限制 | 说明 |
|------|------|------|
| 旅客行李 | 严格限制 | 多数危险品禁止 |
| 货机运输 | 部分允许 | 符合包装说明 |
| 客机运输 | 更严格限制 | 比货机更严格 |
| 例外数量 | 允许 | 严格限量 |
| 有限数量 | 允许 | 包装要求降低 |

---

## 7. 标准对比矩阵

| 标准类型 | 标准名称 | 覆盖范围 | Schema支持 | 优先级 |
|---------|---------|---------|-----------|--------|
| 标识标准 | GS1 SSCC | 全球 | 完整支持 | P0 |
| 标识标准 | GSIN/GINC | 国际货运 | 完整支持 | P0 |
| 环境标准 | ISO 14001 | 全球 | 参考支持 | P1 |
| 碳核算 | ISO 14064 | 全球 | 参考支持 | P1 |
| EDI标准 | EDI X12 | 北美 | 完整支持 | P0 |
| EDI标准 | EDIFACT | 国际 | 完整支持 | P0 |
| 智能交通 | ISO/TS 14813 | 全球 | 参考支持 | P2 |
| 车辆通信 | SAE J2735 | 全球 | 参考支持 | P2 |
| 危险品 | ADR | 欧洲 | 完整支持 | P1 |
| 危险品 | IMDG | 国际海运 | 完整支持 | P1 |
| 危险品 | IATA DGR | 航空 | 完整支持 | P1 |

---

## 8. 标准实施指南

### 8.1 实施步骤

**阶段1：评估与规划（1-2个月）**

1. **现状评估**
   - 现有系统能力分析
   - 数据质量评估
   - 流程差距分析

2. **标准选择**
   - 确定适用标准
   - 优先级排序
   - 实施范围界定

3. **制定计划**
   - 分阶段实施路线图
   - 资源配置
   - 时间表制定

**阶段2：基础设施准备（2-3个月）**

1. **系统集成**
   - TMS系统升级
   - EDI接口开发
   - 数据交换平台搭建

2. **标识系统**
   - GS1公司前缀申请
   - 编码规则制定
   - 标签打印系统部署

**阶段3：流程实施（3-4个月）**

1. **标准流程设计**
   - 订单处理流程
   - 运输执行流程
   - 状态更新流程

2. **培训与试运行**
   - 员工培训
   - 系统测试
   - 试运行验证

**阶段4：全面推广（2-3个月）**

1. **正式上线**
   - 分批次切换
   - 监控与支持
   - 问题修复

2. **持续优化**
   - 性能监控
   - 流程优化
   - 标准升级

### 8.2 合规检查清单

**GS1合规检查清单**：

- [ ] GS1公司前缀已申请
- [ ] SSCC编码规则已制定
- [ ] 标签格式符合GS1标准
- [ ] 条码扫描设备已配置
- [ ] 标签打印系统已测试
- [ ] 上下游SSCC数据交换已验证

**EDI合规检查清单**：

- [ ] EDI通信协议已配置
- [ ] 交易集映射已开发
- [ ] 消息验证规则已配置
- [ ] 997功能确认已启用
- [ ] 错误处理流程已建立
- [ ] 交易伙伴测试已完成

**环境合规检查清单**：

- [ ] 碳排放核算方法已制定
- [ ] 排放因子数据库已建立
- [ ] 数据采集系统已部署
- [ ] 碳足迹报告已生成
- [ ] 减排目标已设定
- [ ] 绿色运输政策已发布

**危险品合规检查清单**：

- [ ] 危险品分类能力已具备
- [ ] UN编号数据库已集成
- [ ] 包装要求验证已启用
- [ ] 标签生成系统已部署
- [ ] 运输限制检查已配置
- [ ] 应急响应信息已关联

---

## 9. 标准发展趋势

**趋势1：数字化转型**

- API优先的集成模式
- 实时数据交换
- 区块链溯源
- 数字孪生应用

**趋势2：可持续发展**

- 碳中和运输目标
- 绿色供应链标准
- 循环经济实践
- ESG报告要求

**趋势3：智能化升级**

- 自动驾驶卡车
- 智能调度算法
- 预测性维护
- 物联网传感器

**趋势4：标准化统一**

- 全球标准趋同
- 互操作性提升
- 行业标准整合
- 开放式API标准

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
