# EDI Schema实践案例

## 📑 目录

- [EDI Schema实践案例](#edi-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：GlobalLogistics集团EDI现代化项目](#2-案例1globallogistics集团edi现代化项目)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：EDIFACT ORDERS订单消息](#3-案例2edifact-orders订单消息)
  - [4. 案例3：EDI X12到EDIFACT转换](#4-案例3edi-x12到edifact转换)
  - [5. 案例4：EDI消息验证](#5-案例4edi消息验证)
  - [6. 案例5：EDI数据存储与分析](#6-案例5edi数据存储与分析)

---

## 1. 案例概述

本文档提供EDI Schema在实际应用中的案例，涵盖EDI X12、EDIFACT等场景，适用于物流供应链管理。

---

## 2. 案例1：GlobalLogistics集团EDI现代化项目

### 2.1 企业背景

**GlobalLogistics集团**是全球第三大物流服务提供商，业务覆盖150个国家，拥有850个物流中心和35,000辆运输车辆，为全球5,000+企业客户提供端到端供应链服务。

- **成立时间**：1982年
- **员工规模**：85,000人
- **年处理订单**：1.2亿笔
- **合作伙伴**：12,000+供应商和承运商
- **原系统**：混合使用EDI X12（北美）、EDIFACT（欧洲/亚太）和专有格式，系统分散

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **EDI标准不统一** | 严重 | 同时使用X12、EDIFACT和5种专有格式，集成成本占IT预算40% |
| 2 | **订单错误率高** | 高 | 8%的订单因数据格式问题需人工修正，年处理成本1,800万美元 |
| 3 | **供应链可见性差** | 高 | 货主实时可见率仅35%，客户投诉率高 |
| 4 | **新伙伴集成慢** | 高 | 新供应商平均集成周期3个月，影响业务拓展 |
| 5 | **ASN延迟率高** | 中 | 到货通知(ASN)延迟率25%，导致仓库排程混乱 |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 订单自动化率 | 62% | 95% | 12个月 |
| 2 | 数据错误率 | 8% | <0.5% | 9个月 |
| 3 | 供应链实时可见率 | 35% | 90% | 12个月 |
| 4 | 新伙伴集成周期 | 3个月 | 2周 | 6个月 |
| 5 | ASN准时率 | 75% | 98% | 9个月 |

### 2.4 技术挑战

1. **多标准兼容**：需同时支持X12 4010/5010、EDIFACT D96A/D01B、以及向JSON API演进

2. **实时处理能力**：大促期间订单峰值达50,000笔/小时，需保证99.95%可用性

3. **复杂映射逻辑**：同一数据元素在不同标准间存在语义差异，如日期格式、计量单位

4. **全球化合规**：需满足各国海关电子申报要求（如美国ACE、欧盟ICS2）

5. **遗留系统整合**：需与ERP（SAP/Oracle）、WMS、TMS等20+类系统无缝集成

### 2.5 Schema定义

**EDI X12 850采购订单数据结构**：

```dsl
schema EDI_X12_850 {
  interchange_header: ISA {
    authorization_info_qualifier: String @value("00")
    authorization_info: String @value("          ")
    security_info_qualifier: String @value("00")
    security_info: String @value("          ")
    sender_id_qualifier: String @value("ZZ")
    sender_id: String @value("SUPPLIER01  ")
    receiver_id_qualifier: String @value("ZZ")
    receiver_id: String @value("CUSTOMER01  ")
    interchange_date: String @value("250121") @format(YYMMDD)
    interchange_time: String @value("1200")
    repetition_separator: String @value("^")
    interchange_version: String @value("00501")
    interchange_control_number: String @value("000000001")
    acknowledgement_requested: String @value("0")
    test_indicator: String @value("T")
    component_separator: String @value(":")
  }

  functional_group: GS {
    functional_id: String @value("PO")
    sender_code: String @value("SUPPLIER01")
    receiver_code: String @value("CUSTOMER01")
    group_date: String @value("20250121")
    group_time: String @value("1200")
    group_control_number: String @value("000000001")
    agency_code: String @value("X")
    version_code: String @value("005010")
  }

  transaction_set: ST {
    transaction_id: String @value("850")
    control_number: String @value("0001")
  }

  beginning_segment: BEG {
    transaction_purpose: String @value("00")
    purchase_order_type: String @value("SA")
    purchase_order_number: String @value("PO-2025-001")
    release_number: Optional[String]
    purchase_order_date: String @value("20250121")
  }

  reference_identification: List[REF] {
    reference1: REF {
      qualifier: String @value("DP")
      reference_id: String @value("DEPT-001")
    }
  }

  name_segment: List[N1] {
    ship_to: N1 {
      entity_id: String @value("ST")
      name: String @value("ABC Distribution Center")
      id_qualifier: String @value("92")
      id_code: String @value("DC001")
    }
    bill_to: N1 {
      entity_id: String @value("BT")
      name: String @value("ABC Corporation")
      id_qualifier: String @value("92")
      id_code: String @value("CORP001")
    }
  }

  baseline_item_data: List[PO1] {
    item1: PO1 {
      assigned_id: String @value("1")
      quantity: Decimal @value(100.0)
      unit_code: String @value("EA")
      unit_price: Decimal @value(25.50)
      basis_code: String @value("PE")
      product_id_qualifier1: String @value("UP")
      product_id1: String @value("123456789012")
      product_id_qualifier2: String @value("VN")
      product_id2: String @value("SKU-001")
    }
  }

  summary: CTT {
    line_item_count: Integer @value(1)
  }

  transaction_trailer: SE {
    segment_count: Integer @value(12)
    control_number: String @value("0001")
  }

  group_trailer: GE {
    transaction_count: Integer @value(1)
    control_number: String @value("000000001")
  }

  interchange_trailer: IEA {
    group_count: Integer @value(1)
    control_number: String @value("000000001")
  }
} @standard("X12_005010")
```

### 2.6 完整实现代码

```python
"""
GlobalLogistics集团EDI处理系统
支持X12和EDIFACT解析、验证、转换和路由
"""

import re
import json
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
from abc import ABC, abstractmethod


class EDIStandard(Enum):
    """EDI标准"""
    X12 = "X12"
    EDIFACT = "EDIFACT"


class TransactionType(Enum):
    """交易类型"""
    PURCHASE_ORDER = "850"        # X12
    ORDER_RESPONSE = "855"        # X12
    SHIP_NOTICE = "856"           # X12
    INVOICE = "810"               # X12
    ORDERS = "ORDERS"             # EDIFACT
    ORDRSP = "ORDRSP"             # EDIFACT
    DESADV = "DESADV"             # EDIFACT
    INVOIC = "INVOIC"             # EDIFACT


@dataclass
class X12Segment:
    """X12段"""
    segment_id: str
    elements: List[str]
    
    def to_string(self, element_separator: str = "*", segment_terminator: str = "~") -> str:
        """转换为X12字符串"""
        return f"{self.segment_id}{element_separator}{element_separator.join(self.elements)}{segment_terminator}"
    
    @classmethod
    def parse(cls, text: str, element_separator: str = "*") -> 'X12Segment':
        """解析X12段"""
        parts = text.split(element_separator)
        return cls(segment_id=parts[0], elements=parts[1:] if len(parts) > 1 else [])


@dataclass
class X12Transaction:
    """X12事务集"""
    transaction_id: str
    control_number: str
    segments: List[X12Segment]
    
    def get_segments_by_id(self, segment_id: str) -> List[X12Segment]:
        """获取指定ID的所有段"""
        return [s for s in self.segments if s.segment_id == segment_id]
    
    def get_first_segment(self, segment_id: str) -> Optional[X12Segment]:
        """获取第一个指定ID的段"""
        for s in self.segments:
            if s.segment_id == segment_id:
                return s
        return None


@dataclass
class X12FunctionalGroup:
    """X12功能组"""
    functional_id: str
    sender_code: str
    receiver_code: str
    group_date: str
    group_time: str
    control_number: str
    transactions: List[X12Transaction]
    
    @property
    def transaction_count(self) -> int:
        return len(self.transactions)


@dataclass
class X12Interchange:
    """X12交换"""
    sender_id: str
    receiver_id: str
    interchange_date: str
    interchange_time: str
    control_number: str
    functional_groups: List[X12FunctionalGroup]
    element_separator: str = "*"
    segment_terminator: str = "~"
    
    @property
    def group_count(self) -> int:
        return len(self.functional_groups)
    
    def to_x12_string(self) -> str:
        """转换为X12格式字符串"""
        lines = []
        
        # ISA段
        isa = X12Segment("ISA", [
            "00", "          ", "00", "          ",
            "ZZ", self.sender_id.ljust(15), "ZZ", self.receiver_id.ljust(15),
            self.interchange_date, self.interchange_time, "^", "00501", self.control_number, "0", "T", ":"
        ])
        lines.append(isa.to_string(self.element_separator, self.segment_terminator))
        
        for fg in self.functional_groups:
            # GS段
            gs = X12Segment("GS", [
                fg.functional_id, fg.sender_code, fg.receiver_code,
                fg.group_date, fg.group_time, fg.control_number, "X", "005010"
            ])
            lines.append(gs.to_string(self.element_separator, self.segment_terminator))
            
            for txn in fg.transactions:
                # ST段
                st = X12Segment("ST", [txn.transaction_id, txn.control_number])
                lines.append(st.to_string(self.element_separator, self.segment_terminator))
                
                for seg in txn.segments:
                    lines.append(seg.to_string(self.element_separator, self.segment_terminator))
                
                # SE段
                se = X12Segment("SE", [str(len(txn.segments) + 2), txn.control_number])
                lines.append(se.to_string(self.element_separator, self.segment_terminator))
            
            # GE段
            ge = X12Segment("GE", [str(fg.transaction_count), fg.control_number])
            lines.append(ge.to_string(self.element_separator, self.segment_terminator))
        
        # IEA段
        iea = X12Segment("IEA", [str(self.group_count), self.control_number])
        lines.append(iea.to_string(self.element_separator, self.segment_terminator))
        
        return "\n".join(lines)
    
    @classmethod
    def parse(cls, x12_text: str) -> 'X12Interchange':
        """解析X12字符串"""
        # 检测分隔符
        if x12_text.startswith("ISA"):
            element_sep = x12_text[3]
            segment_sep = x12_text[106] if len(x12_text) > 106 else "~"
        else:
            element_sep = "*"
            segment_sep = "~"
        
        # 分割段
        segments_text = x12_text.split(segment_sep)
        segments = []
        for seg_text in segments_text:
            seg_text = seg_text.strip()
            if seg_text:
                segments.append(X12Segment.parse(seg_text, element_sep))
        
        # 解析ISA
        isa = segments[0]
        interchange = cls(
            sender_id=isa.elements[5].strip(),
            receiver_id=isa.elements[7].strip(),
            interchange_date=isa.elements[8],
            interchange_time=isa.elements[9],
            control_number=isa.elements[12],
            functional_groups=[],
            element_separator=element_sep,
            segment_terminator=segment_sep
        )
        
        # 解析功能组和事务
        current_fg = None
        current_txn = None
        
        for seg in segments[1:]:
            if seg.segment_id == "GS":
                current_fg = X12FunctionalGroup(
                    functional_id=seg.elements[0],
                    sender_code=seg.elements[1],
                    receiver_code=seg.elements[2],
                    group_date=seg.elements[3],
                    group_time=seg.elements[4],
                    control_number=seg.elements[5],
                    transactions=[]
                )
                interchange.functional_groups.append(current_fg)
            
            elif seg.segment_id == "ST" and current_fg:
                current_txn = X12Transaction(
                    transaction_id=seg.elements[0],
                    control_number=seg.elements[1],
                    segments=[]
                )
                current_fg.transactions.append(current_txn)
            
            elif seg.segment_id == "SE":
                current_txn = None
            
            elif seg.segment_id == "GE":
                current_fg = None
            
            elif current_txn and seg.segment_id not in ["IEA"]:
                current_txn.segments.append(seg)
        
        return interchange


@dataclass
class PurchaseOrder:
    """采购订单数据类"""
    po_number: str
    po_date: date
    buyer: Dict[str, str]
    seller: Dict[str, str]
    ship_to: Dict[str, str]
    items: List[Dict[str, Any]]
    total_amount: Decimal = Decimal("0")
    currency: str = "USD"
    
    @classmethod
    def from_x12_850(cls, transaction: X12Transaction) -> 'PurchaseOrder':
        """从X12 850创建采购订单"""
        # 解析BEG段
        beg = transaction.get_first_segment("BEG")
        po_number = beg.elements[2] if beg else ""
        po_date_str = beg.elements[4] if beg and len(beg.elements) > 4 else ""
        try:
            po_date = datetime.strptime(po_date_str, "%Y%m%d").date() if po_date_str else date.today()
        except ValueError:
            po_date = date.today()
        
        # 解析N1段
        ship_to = {}
        for n1 in transaction.get_segments_by_id("N1"):
            if n1.elements[0] == "ST" and len(n1.elements) > 1:
                ship_to = {
                    "name": n1.elements[1],
                    "id": n1.elements[3] if len(n1.elements) > 3 else ""
                }
        
        # 解析PO1段
        items = []
        for po1 in transaction.get_segments_by_id("PO1"):
            if len(po1.elements) >= 7:
                item = {
                    "line_number": po1.elements[0],
                    "quantity": Decimal(po1.elements[1]) if po1.elements[1] else Decimal("0"),
                    "unit": po1.elements[2],
                    "unit_price": Decimal(po1.elements[3]) if po1.elements[3] else Decimal("0"),
                    "upc": po1.elements[6] if len(po1.elements) > 6 else "",
                    "sku": po1.elements[8] if len(po1.elements) > 8 else ""
                }
                items.append(item)
        
        return cls(
            po_number=po_number,
            po_date=po_date,
            buyer={},
            seller={},
            ship_to=ship_to,
            items=items
        )
    
    def calculate_total(self) -> Decimal:
        """计算订单总额"""
        total = Decimal("0")
        for item in self.items:
            total += item["quantity"] * item["unit_price"]
        self.total_amount = total
        return total


class EDIValidator:
    """EDI验证器"""
    
    def __init__(self):
        self.validation_rules = {}
    
    def validate_x12(self, interchange: X12Interchange) -> Tuple[bool, List[str]]:
        """验证X12交换"""
        errors = []
        
        # 验证控制号
        if not interchange.control_number:
            errors.append("缺少交换控制号")
        
        # 验证功能组
        for fg in interchange.functional_groups:
            # 验证事务集数量
            if fg.transaction_count == 0:
                errors.append(f"功能组 {fg.control_number} 缺少事务集")
            
            for txn in fg.transactions:
                # 验证必需段
                segment_ids = {s.segment_id for s in txn.segments}
                required = {"BEG", "PO1"}
                for req in required:
                    if req not in segment_ids and txn.transaction_id == "850":
                        errors.append(f"事务集 {txn.control_number} 缺少必需段 {req}")
                
                # 验证ST-SE匹配
                st = txn.get_first_segment("ST")
                se = txn.get_first_segment("SE")
                if st and se:
                    if st.elements[1] != se.elements[1]:
                        errors.append(f"事务集控制号不匹配: ST={st.elements[1]}, SE={se.elements[1]}")
                    expected_count = len(txn.segments) + 2
                    actual_count = int(se.elements[0]) if se.elements[0].isdigit() else 0
                    if expected_count != actual_count:
                        errors.append(f"段计数不匹配: 期望{expected_count}, 实际{actual_count}")
        
        return len(errors) == 0, errors


class EDIMapper:
    """EDI映射器"""
    
    def x12_to_edifact_orders(self, x12_interchange: X12Interchange) -> Dict[str, Any]:
        """将X12 850转换为EDIFACT ORDERS"""
        po = PurchaseOrder.from_x12_850(x12_interchange.functional_groups[0].transactions[0])
        
        # 构建EDIFACT结构
        edifact = {
            "UNB": {
                "syntax_identifier": "UNOA",
                "syntax_version": "3",
                "sender": x12_interchange.sender_id,
                "recipient": x12_interchange.receiver_id,
                "date": datetime.now().strftime("%y%m%d"),
                "time": datetime.now().strftime("%H%M"),
                "reference": x12_interchange.control_number
            },
            "UNH": {
                "reference": "1",
                "type": "ORDERS",
                "version": "D",
                "release": "96A",
                "agency": "UN"
            },
            "BGM": {
                "document_name": "220",
                "document_number": po.po_number,
                "function": "9"
            },
            "DTM": [
                {
                    "qualifier": "137",
                    "date": po.po_date.strftime("%Y%m%d"),
                    "format": "102"
                }
            ],
            "NAD": [
                {
                    "qualifier": "ST",
                    "party_id": po.ship_to.get("id", ""),
                    "party_name": po.ship_to.get("name", "")
                }
            ],
            "LIN": [
                {
                    "line_number": i + 1,
                    "item_number": item.get("upc", ""),
                    "quantity": float(item["quantity"]),
                    "unit": item["unit"],
                    "price": float(item["unit_price"])
                }
                for i, item in enumerate(po.items)
            ]
        }
        
        return edifact


class EDIProcessor:
    """EDI处理器"""
    
    def __init__(self):
        self.validator = EDIValidator()
        self.mapper = EDIMapper()
        self.metrics = {
            "total_processed": 0,
            "validation_passed": 0,
            "validation_failed": 0,
            "conversion_success": 0
        }
    
    def process_x12(self, x12_text: str) -> Dict[str, Any]:
        """处理X12消息"""
        result = {
            "status": "RECEIVED",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }
        
        self.metrics["total_processed"] += 1
        
        try:
            # 解析
            interchange = X12Interchange.parse(x12_text)
            result["details"]["sender"] = interchange.sender_id
            result["details"]["receiver"] = interchange.receiver_id
            result["details"]["group_count"] = interchange.group_count
            
            # 验证
            is_valid, errors = self.validator.validate_x12(interchange)
            if not is_valid:
                result["status"] = "VALIDATION_FAILED"
                result["details"]["errors"] = errors
                self.metrics["validation_failed"] += 1
                return result
            
            self.metrics["validation_passed"] += 1
            result["status"] = "VALIDATED"
            
            # 提取采购订单
            if interchange.functional_groups:
                txn = interchange.functional_groups[0].transactions[0]
                if txn.transaction_id == "850":
                    po = PurchaseOrder.from_x12_850(txn)
                    result["details"]["purchase_order"] = {
                        "po_number": po.po_number,
                        "po_date": po.po_date.isoformat(),
                        "item_count": len(po.items),
                        "total_amount": float(po.calculate_total())
                    }
            
            return result
            
        except Exception as e:
            result["status"] = "ERROR"
            result["details"]["exception"] = str(e)
            return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        total = self.metrics["total_processed"]
        return {
            **self.metrics,
            "validation_rate": (self.metrics["validation_passed"] / total * 100) if total > 0 else 0
        }


def main():
    """主函数 - 演示"""
    # 示例X12 850消息
    x12_sample = """ISA*00*          *00*          *ZZ*SUPPLIER01    *ZZ*CUSTOMER01    *250121*1200*^*00501*000000001*0*T*:~
GS*PO*SUPPLIER01*CUSTOMER01*20250121*1200*000000001*X*005010~
ST*850*0001~
BEG*00*SA*PO-2025-001**20250121~
REF*DP*DEPT-001~
N1*ST*ABC Distribution Center*92*DC001~
N1*BT*ABC Corporation*92*CORP001~
PO1*1*100*EA*25.50*PE*UP*123456789012*VN*SKU-001~
PO1*2*50*EA*15.75*PE*UP*987654321098*VN*SKU-002~
CTT*2~
SE*10*0001~
GE*1*000000001~
IEA*1*000000001~"""
    
    processor = EDIProcessor()
    result = processor.process_x12(x12_sample)
    
    print("处理结果:")
    print(json.dumps(result, indent=2, default=str))
    
    print("\n处理指标:")
    print(json.dumps(processor.get_metrics(), indent=2))
    
    # 转换示例
    interchange = X12Interchange.parse(x12_sample)
    edifact = processor.mapper.x12_to_edifact_orders(interchange)
    print("\nEDIFACT ORDERS:")
    print(json.dumps(edifact, indent=2, default=str))


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 订单自动化率 | 62% | 96% | +34% |
| 数据错误率 | 8% | 0.3% | -96% |
| 供应链可见率 | 35% | 92% | +63% |
| 新伙伴集成周期 | 3个月 | 10天 | -89% |
| ASN准时率 | 75% | 97% | +22% |

#### ROI计算

**投资成本**（15个月项目周期）：
- EDI平台开发：480万美元
- 系统整合：220万美元
- 培训与变更：80万美元
- **总投资**：780万美元

**年度收益**：
- 人工成本节约：1,200万美元
- 错误处理成本节约：800万美元
- 客户满意度提升收益：600万美元
- **年度总收益**：2,600万美元

**ROI分析**：
- 投资回收期：3.6个月
- 3年ROI：900%

#### 经验教训

**成功因素**：
1. **统一数据模型**：建立企业级数据字典，统一150+核心数据元素定义
2. **API优先策略**：新合作伙伴优先使用REST API，老旧伙伴使用EDI
3. **实时监控**：部署EDI流量监控大屏，异常自动告警

**挑战与应对**：
1. **遗留伙伴迁移困难**：提供转换网关，逐步引导升级
2. **多标准并发复杂性**：建立标准化映射库，减少重复开发
3. **数据质量问题**：实施数据治理，从源头确保准确性

---

## 3. 案例2：EDIFACT ORDERS订单消息

详见 `04_Transformation.md` 第3章。

## 4. 案例3：EDI X12到EDIFACT转换

详见 `04_Transformation.md` 第2章。

## 5. 案例4：EDI消息验证

详见 `04_Transformation.md` 第5章。

## 6. 案例5：EDI数据存储与分析

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
