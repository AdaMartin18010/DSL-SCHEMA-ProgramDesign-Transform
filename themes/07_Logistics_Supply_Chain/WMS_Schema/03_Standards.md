# WMS Schema标准对标

## 📑 目录

- [WMS Schema标准对标](#wms-schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
  - [2. GS1标准体系](#2-gs1标准体系)
    - [2.1 GS1标识符标准](#21-gs1标识符标准)
    - [2.2 GS1条码标准](#22-gs1条码标准)
    - [2.3 GS1 EPCIS标准](#23-gs1-epcis标准)
  - [3. ISO 8000数据质量标准](#3-iso-8000数据质量标准)
    - [3.1 ISO 8000-1核心概念](#31-iso-8000-1核心概念)
    - [3.2 数据质量维度](#32-数据质量维度)
    - [3.3 WMS数据质量规则](#33-wms数据质量规则)
  - [4. Warehousing EDI标准](#4-warehousing-edi标准)
    - [4.1 EDI X12仓储交易集](#41-edi-x12仓储交易集)
    - [4.2 EDIFACT仓储消息](#42-edifact仓储消息)
    - [4.3 EDI映射矩阵](#43-edi映射矩阵)
  - [5. 仓库管理相关标准](#5-仓库管理相关标准)
    - [5.1 MH10.8.2](#51-mh1082)
    - [5.2 ISO 28560](#52-iso-28560)
    - [5.3 ISO/IEC 15459](#53-isoiec-15459)
  - [6. 标准对比矩阵](#6-标准对比矩阵)
  - [7. 标准实施指南](#7-标准实施指南)
    - [7.1 实施步骤](#71-实施步骤)
    - [7.2 合规检查清单](#72-合规检查清单)
  - [8. 标准发展趋势](#8-标准发展趋势)

---

## 1. 标准体系概述

WMS Schema标准体系分为四个层次：

1. **GS1标准体系**：全球统一标识系统，用于商品和货位标识
2. **ISO 8000数据质量**：数据质量管理和主数据标准
3. **Warehousing EDI标准**：EDI X12和EDIFACT仓储相关交易集
4. **仓库管理标准**：MH10.8.2、ISO 28560等专业标准

---

## 2. GS1标准体系

### 2.1 GS1标识符标准

**核心标识符**：

| 标识符 | 名称 | 长度 | WMS应用场景 |
|--------|------|------|-------------|
| GTIN | 全球贸易项目代码 | 8/12/13/14位 | SKU唯一标识 |
| SSCC | 系列货运包装箱代码 | 18位 | 托盘/箱标识 |
| GLN | 全球位置码 | 13位 | 仓库/库位标识 |
| GRAI | 全球可回收资产标识符 | 最多30位 | 周转箱、托盘 |
| GIAI | 全球单个资产标识符 | 最多30位 | 叉车、设备 |
| GSIN | 全球货运标识符 | 17位 | 发货批次标识 |

**GTIN结构**：

```
GTIN-13 = 指示符(1) + GS1公司前缀(7-9) + 项目参考(3-5) + 校验位(1)

示例：6 1234567 89012 8
      │ └─┬───┘ └─┬─┘ │
      │   │       │   └─ 校验位
      │   │       └────── 项目参考
      │   └────────────── GS1公司前缀
      └────────────────── 包装级别指示符
```

**GLN在WMS中的应用**：

```
仓库层级GLN结构：

仓库级 GLN：1234567890123 (仓库主标识)
  ├─ 区域级 GLN：1234567890123 + 区域码
  │   ├─ 货架级 GLN：1234567890123 + 货架编码
  │   │   ├─ 货位级 GLN：1234567890123 + 完整货位编码
  │   │   └─ ...
  │   └─ ...
  └─ ...
```

### 2.2 GS1条码标准

**条码类型对比**：

| 条码类型 | 数据容量 | 扫描方向 | WMS应用 |
|---------|---------|---------|---------|
| EAN-13 | 13位数字 | 单向 | 商品零售包装 |
| GS1-128 | 48字符 | 双向 | 物流标签、SSCC |
| GS1 DataMatrix | 3116字符 | 全方位 | 小件标识、DPM |
| GS1 QR Code | 7089字符 | 全方位 | 移动应用 |
| EPC/RFID | 可变 | 非接触 | 批量扫描、追踪 |

**GS1-128应用标识符（WMS常用）**：

| AI | 名称 | 格式 | 示例 | 应用 |
|----|------|------|------|------|
| 00 | SSCC | n2+n18 | (00)312345678901234560 | 托盘标识 |
| 01 | GTIN | n2+n14 | (01)00612345678901 | 商品标识 |
| 10 | 批号 | n2+an..20 | (10)LOT123456 | 批次追踪 |
| 11 | 生产日期 | n2+n6 | (11)250115 | 效期管理 |
| 15 | 保质期 | n2+n6 | (15)251115 | 效期管理 |
| 17 | 有效期 | n2+n6 | (17)260115 | 效期管理 |
| 21 | 序列号 | n2+an..20 | (21)SN123456789 | 单品追踪 |
| 30 | 数量 | n2+n..8 | (30)100 | 数量标识 |
| 310n | 净重 | n4+n6 | (3102)12500 | 重量标识 |
| 410 | 出货地GLN | n3+n13 | (410)1234567890123 | 库位标识 |

**WMS标签示例**：

```
┌─────────────────────────────────────────┐
│  入库标签                                │
│                                         │
│  商品: (01)00612345678901               │
│  名称: 示例商品                          │
│  批号: (10)B20250115                     │
│  数量: (30)100                           │
│  效期: (17)260115                        │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  [GS1-128 BARCODE]              │   │
│  │  ]C1010061234567890110B202...   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  库位: (410)1234567890123               │
│  入库日期: 2025-01-15                   │
└─────────────────────────────────────────┘
```

### 2.3 GS1 EPCIS标准

**标准名称**：
EPC Information Services (EPCIS)

**核心事件类型**：

| 事件类型 | 描述 | WMS应用 |
|---------|------|---------|
| ObjectEvent | 对象级事件 | 单品追踪 |
| AggregationEvent | 聚合事件 | 包装关系 |
| TransformationEvent | 转换事件 | 加工转换 |
| TransactionEvent | 交易事件 | 所有权转移 |

**WMS事件映射**：

```
WMS操作 → EPCIS事件：

收货 → ObjectEvent OBSERVE + AggregationEvent ADD
上架 → ObjectEvent OBSERVE
拣货 → ObjectEvent OBSERVE
包装 → AggregationEvent ADD
发货 → ObjectEvent OBSERVE + TransactionEvent ADD
盘点 → ObjectEvent OBSERVE
```

---

## 3. ISO 8000数据质量标准

### 3.1 ISO 8000-1核心概念

**标准名称**：
Data quality — Part 1: Overview

**数据质量管理流程**：

```
┌─────────────────────────────────────────┐
│         数据质量管理循环                 │
│                                         │
│    ┌───────┐      ┌───────┐            │
│    │ 定义   │ ───► │ 测量   │            │
│    │ 标准   │      │ 质量   │            │
│    └───────┘      └───┬───┘            │
│         ▲             │                 │
│         │             ▼                 │
│    ┌───────┐      ┌───────┐            │
│    │ 持续   │ ◄─── │ 分析   │            │
│    │ 改进   │      │ 改进   │            │
│    └───────┘      └───────┘            │
│                                         │
└─────────────────────────────────────────┘
```

### 3.2 数据质量维度

**ISO 8000-8数据质量特性**：

| 维度 | 定义 | WMS指标 | 测量方法 |
|------|------|---------|---------|
| 准确性 | 数据与真实值的一致程度 | 库存准确率 | 盘点对比 |
| 完整性 | 必需数据的完整程度 | 必填字段完整率 | 数据校验 |
| 一致性 | 不同系统间数据一致 | 库存同步差异 | 系统对账 |
| 时效性 | 数据的更新及时程度 | 数据延迟时间 | 时间戳分析 |
| 有效性 | 数据符合定义规则 | 格式合规率 | 规则验证 |
| 唯一性 | 数据记录的唯一程度 | 重复记录率 | 重复检测 |
| 可访问性 | 数据可被获取的程度 | 查询响应时间 | 性能测试 |
| 合规性 | 符合标准和法规 | 标准符合率 | 合规审计 |

**数据质量评分模型**：

```
数据质量评分 = Σ(维度权重 × 维度得分)

权重分配：
- 准确性: 30%
- 完整性: 20%
- 一致性: 20%
- 时效性: 15%
- 有效性: 10%
- 唯一性: 5%

等级划分：
- 优秀: 95-100分
- 良好: 85-94分
- 合格: 70-84分
- 不合格: <70分
```

### 3.3 WMS数据质量规则

**库存数据质量规则**：

```python
class InventoryDataQualityRules:
    """库存数据质量规则"""
    
    RULES = {
        "INV001": {
            "name": "库存数量非负",
            "condition": "on_hand >= 0 AND allocated >= 0 AND picked >= 0",
            "severity": "CRITICAL",
            "auto_fix": False
        },
        "INV002": {
            "name": "可用数量计算正确",
            "condition": "available = on_hand - allocated - picked",
            "severity": "CRITICAL",
            "auto_fix": True
        },
        "INV003": {
            "name": "库位编码有效",
            "condition": "location_code EXISTS IN locations",
            "severity": "HIGH",
            "auto_fix": False
        },
        "INV004": {
            "name": "SKU编码有效",
            "condition": "sku EXISTS IN products",
            "severity": "HIGH",
            "auto_fix": False
        },
        "INV005": {
            "name": "效期格式正确",
            "condition": "expiration_date IS NULL OR expiration_date > '2000-01-01'",
            "severity": "MEDIUM",
            "auto_fix": False
        },
        "INV006": {
            "name": "批次号格式",
            "condition": "batch_number IS NULL OR LENGTH(batch_number) <= 50",
            "severity": "LOW",
            "auto_fix": False
        }
    }
    
    def validate_inventory(self, inventory: dict) -> List[dict]:
        """验证库存数据"""
        violations = []
        
        for rule_id, rule in self.RULES.items():
            if not self._check_rule(inventory, rule["condition"]):
                violations.append({
                    "rule_id": rule_id,
                    "rule_name": rule["name"],
                    "severity": rule["severity"],
                    "inventory_id": inventory.get("inventory_id"),
                    "suggested_action": "AUTO_FIX" if rule["auto_fix"] else "MANUAL_REVIEW"
                })
        
        return violations
```

**货位数据质量规则**：

| 规则ID | 规则描述 | 验证逻辑 | 严重级别 |
|--------|---------|---------|---------|
| LOC001 | 货位编码唯一 | COUNT(*) = 1 WHERE location_code = X | CRITICAL |
| LOC002 | 重量容量非负 | max_weight >= 0 | CRITICAL |
| LOC003 | 尺寸有效 | length > 0 AND width > 0 AND height > 0 | HIGH |
| LOC004 | 区域编码有效 | zone_code EXISTS IN zones | HIGH |
| LOC005 | 利用率计算正确 | fill_percentage = current_weight / max_weight | MEDIUM |
| LOC006 | 坐标有效 | x >= 0 AND y >= 0 | LOW |

---

## 4. Warehousing EDI标准

### 4.1 EDI X12仓储交易集

**交易集详细说明**：

| 交易集 | 名称 | 用途 | 关键段 |
|--------|------|------|--------|
| 940 | Warehouse Shipping Order | 仓库发货指令 | W05, N1, N3, N4, G62, W01 |
| 943 | Warehouse Stock Transfer Shipment Advice | 库存转移发货通知 | W06, N1, G62, W04 |
| 944 | Warehouse Stock Transfer Receipt Advice | 库存转移收货通知 | W17, N1, G62, W07 |
| 945 | Warehouse Shipping Advice | 仓库发货确认 | W06, N1, G62, W03, W04 |
| 946 | Delivery Information Message | 配送信息 | IT1, N1, G62 |
| 947 | Warehouse Inventory Adjustment Advice | 库存调整通知 | W1, W2, W3 |

**940交易集示例**：

```
ST*940*0001
W05*N*12345*ORD789
N1*ST*ABC Company
N3*123 Main Street
N4*New York*NY*10001*US
N1*DE*XYZ Distribution
N3*456 Oak Avenue
N4*Los Angeles*CA*90001*US
G62*10*20250115
G62*08*20250118
W01*12*EA*UP*123456789012
W01*24*EA*UP*987654321098
SE*14*0001
```

**945交易集示例**：

```
ST*945*0001
W06*M*SHIP123*ORD789*20250115
N1*ST*ABC Company
N3*123 Main Street
N4*New York*NY*10001*US
G62*11*20250115
W03*36*EA*G*10*LB
W04*12*EA*UP*123456789012
W04*24*EA*UP*987654321098
SE*10*0001
```

### 4.2 EDIFACT仓储消息

**消息详细说明**：

| 消息代码 | 名称 | 描述 | 关键段 |
|---------|------|------|--------|
| RECADV | Receiving Advice Message | 收货通知 | BGM, DTM, RFF, NAD, LIN, QTY |
| RESADV | Reservation Advice Message | 预留通知 | BGM, DTM, RFF, LIN, QTY |
| INVRPT | Inventory Report Message | 库存报告 | BGM, DTM, LIN, QTY, LOC |
| SLSRPT | Sales Data Report Message | 销售数据报告 | BGM, DTM, LIN, QTY |
| DELJIT | Delivery Just In Time Message | 准时交付 | BGM, DTM, LIN, QTY, LOC |
| DELFOR | Delivery Schedule Message | 交付计划 | BGM, DTM, LIN, QTY, LOC |

**RECADV消息示例**：

```
UNB+UNOA:3+RECEIVER+SENDER+250115:1430+1234567'
UNH+1+RECADV:D:21A:UN'
BGM+351+REC001+9'
DTM+137:20250115:102'
RFF+ON:PO123456'
NAD+BY+12345::87+ABC Company'
NAD+SU+67890::87+XYZ Supplier'
LIN+1++1234567890123:EN'
QTY+48:100:C62'
LIN+2++9876543210987:EN'
QTY+48:50:C62'
UNT+10+1'
UNZ+1+1234567'
```

**INVRPT消息示例**：

```
UNB+UNOA:3+WAREHOUSE+CLIENT+250115:1430+1234568'
UNH+1+INVRPT:D:21A:UN'
BGM+73+INV001+9'
DTM+137:20250115:102'
DTM+356:20250115:102'
LIN+1++1234567890123:EN'
QTY+145:1000:C62'
LOC+11+A-01-01'
LIN+2++9876543210987:EN'
QTY+145:500:C62'
LOC+11+B-02-03'
UNT+12+1'
UNZ+1+1234568'
```

### 4.3 EDI映射矩阵

**X12与EDIFACT对照**：

| 业务场景 | EDI X12 | EDIFACT |
|---------|---------|---------|
| 发货指令 | 940 | IFTMIN |
| 发货确认 | 945 | RECADV |
| 收货通知 | 944 | RECADV |
| 库存转移发货 | 943 | IFTMBF |
| 库存转移收货 | 944 | IFTMBC |
| 库存报告 | 846 | INVRPT |
| 库存调整 | 947 | INVRPT |
| 配送信息 | 946 | IFTSTA |

---

## 5. 仓库管理相关标准

### 5.1 MH10.8.2

**标准名称**：
Unit Loads and Transport Packages - Linear Bar Code and Two-Dimensional Symbols

**应用场景**：

| 应用 | 说明 | WMS使用 |
|------|------|---------|
| 单元负载标识 | 托盘/集装箱标识 | 托盘追踪 |
| 运输包装标识 | 箱/包装标识 | 箱级管理 |
| 条码符号选择 | 条码类型选择 | 标签打印 |
| 标签尺寸规格 | 标签尺寸标准 | 标签设计 |

**标签规格**：

```
标准物流标签尺寸：
- 最小: 148mm x 105mm (A6)
- 标准: 148mm x 210mm (A5)
- 大型: 210mm x 297mm (A4)

条码规格：
- 高度: 最小32mm
- 窄条宽度: 0.5mm (标准)
- 静区: 最小6.4mm
```

### 5.2 ISO 28560

**标准名称**：
Information and documentation - RFID in libraries

**（注：虽为图书馆标准，但RFID原理适用于仓库）**

**RFID应用对比**：

| 特性 | 图书馆RFID | 仓库RFID |
|------|-----------|---------|
| 频率 | 13.56MHz (HF) | 860-960MHz (UHF) |
| 读取距离 | <1m | 3-15m |
| 数据容量 | 可读写 | 多为只读或简单读写 |
| 应用场景 | 单件借还 | 批量盘点、门禁 |

**WMS RFID应用**：

| 应用 | 效益 |
|------|------|
| 批量收货 | 一次性扫描整托盘 |
| 快速盘点 | 手持/固定式批量读取 |
| 实时追踪 | 通道读取记录移动 |
| 防盗管理 | 未授权出库报警 |

### 5.3 ISO/IEC 15459

**标准名称**：
Information technology - Unique identifiers

**唯一标识符类型**：

| 部分 | 名称 | 应用 |
|------|------|------|
| 15459-1 | 运输单元 | SSCC、集装箱 |
| 15459-2 | 注册流程 | 注册机构规范 |
| 15459-4 | 个人与组织 | GLN、DUNS |
| 15459-5 | 可回收运输品 | GRAI |
| 15459-6 | 产品分组 | 产品集合标识 |

---

## 6. 标准对比矩阵

| 标准类型 | 标准名称 | 覆盖范围 | Schema支持 | 优先级 |
|---------|---------|---------|-----------|--------|
| 标识标准 | GS1 GTIN | 全球 | 完整支持 | P0 |
| 标识标准 | GS1 SSCC | 全球 | 完整支持 | P0 |
| 标识标准 | GS1 GLN | 全球 | 完整支持 | P0 |
| 数据质量 | ISO 8000 | 全球 | 参考支持 | P1 |
| EDI标准 | EDI X12 940/945 | 北美 | 完整支持 | P0 |
| EDI标准 | EDIFACT RECADV | 国际 | 完整支持 | P0 |
| 条码标准 | GS1-128 | 全球 | 完整支持 | P0 |
| RFID标准 | ISO 28560 | 全球 | 参考支持 | P2 |
| 唯一标识 | ISO/IEC 15459 | 全球 | 参考支持 | P1 |
| 单元负载 | MH10.8.2 | 全球 | 参考支持 | P1 |

---

## 7. 标准实施指南

### 7.1 实施步骤

**阶段1：评估与规划（1-2个月）**

1. **现状评估**
   - 现有编码体系分析
   - 数据质量评估
   - 标签使用情况

2. **标准选择**
   - 确定GS1前缀需求
   - 选择EDI标准
   - 制定数据质量目标

3. **制定计划**
   - 实施路线图
   - 培训计划
   - 测试计划

**阶段2：基础设施（2-3个月）**

1. **GS1注册**
   - 申请GS1公司前缀
   - 制定编码规则
   - 设计标签模板

2. **系统升级**
   - WMS系统配置
   - 条码/RFID设备
   - EDI接口开发

3. **数据准备**
   - 主数据清洗
   - 历史数据迁移
   - 数据质量规则配置

**阶段3：试运行（1-2个月）**

1. **小规模试点**
   - 单个仓库试点
   - 关键流程验证
   - 问题修复

2. **培训**
   - 操作人员培训
   - 管理人员培训
   - 供应商培训

**阶段4：全面推广（2-3个月）**

1. **分批切换**
   - 按仓库切换
   - 按流程切换
   - 监控与支持

2. **持续优化**
   - 数据质量监控
   - 流程优化
   - 标准升级

### 7.2 合规检查清单

**GS1合规检查清单**：

- [ ] GS1公司前缀已申请
- [ ] GTIN编码规则已制定
- [ ] SSCC编码规则已制定
- [ ] GLN分配完成
- [ ] 标签模板符合GS1标准
- [ ] 条码设备已配置
- [ ] 扫描验证通过率>99%

**数据质量合规检查清单**：

- [ ] 数据质量标准已定义
- [ ] 数据质量规则已配置
- [ ] 数据清洗已完成
- [ ] 数据监控已启用
- [ ] 质量报告已生成
- [ ] 改进流程已建立

**EDI合规检查清单**：

- [ ] EDI标准已确定
- [ ] 交易伙伴已注册
- [ ] 映射规则已开发
- [ ] 测试已完成
- [ ] 997确认已启用
- [ ] 错误处理流程已建立

**条码合规检查清单**：

- [ ] 条码类型已确定
- [ ] 标签尺寸符合标准
- [ ] 条码质量达到C级以上
- [ ] 静区符合要求
- [ ] 人工可读信息完整
- [ ] 扫描设备已校准

---

## 8. 标准发展趋势

**趋势1：数字化转型**

- 数字孪生仓库
- 实时数据可视化
- API-first架构
- 云原生WMS

**趋势2：智能化升级**

- AI驱动的库存优化
- 预测性维护
- 自动补货
- 智能库位分配

**趋势3：自动化集成**

- AMR/AGV集成
- 自动化立体库
- 机器人拣选
- 无人仓运营

**趋势4：可持续发展**

- 绿色仓储标准
- 碳足迹追踪
- 循环经济实践
- 包装材料回收

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
