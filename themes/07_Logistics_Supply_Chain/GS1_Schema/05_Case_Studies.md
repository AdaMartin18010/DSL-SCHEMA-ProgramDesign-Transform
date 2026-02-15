# GS1 Schema实践案例

## 📑 目录

- [GS1 Schema实践案例](#gs1-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：MegaRetail零售供应链数字化转型](#2-案例1megaretail零售供应链数字化转型)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：物流GLN位置管理](#3-案例2物流gln位置管理)
  - [4. 案例3：包装SSCC追踪](#4-案例3包装sscc追踪)
  - [5. 案例4：EPCIS供应链追溯](#5-案例4epcis供应链追溯)
  - [6. 案例5：GS1数据存储与分析](#6-案例5gs1数据存储与分析)

---

## 1. 案例概述

本文档提供GS1 Schema在实际应用中的案例，涵盖GTIN、GLN、SSCC、EPCIS等场景，适用于零售供应链数字化转型。

---

## 2. 案例1：MegaRetail零售供应链数字化转型

### 2.1 企业背景

**MegaRetail**是全球第二大零售商，在35个国家拥有12,000+门店，年营业额超过1,200亿美元，SKU数量超过300万，供应商网络覆盖8,000+企业。

- **成立时间**：1967年
- **员工规模**：230万人
- **年库存周转**：500亿美元
- **供应商数量**：8,000+活跃供应商
- **物流网络**：350个配送中心，25,000辆运输车辆
- **原系统**：条码系统分散，ERP与门店POS数据不同步，缺货率高达8%

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **库存准确度低** | 严重 | 库存准确率仅78%，导致缺货损失年达15亿美元 |
| 2 | **产品追溯困难** | 高 | 食品安全事件响应时间平均72小时，面临监管风险 |
| 3 | **供应链可视化差** | 高 | 从供应商到门店的全链路可见性不足30% |
| 4 | **新品上架慢** | 中 | 新产品从采购到上架平均45天，错失市场机会 |
| 5 | **退货处理低效** | 中 | 退货处理周期14天，损耗率高达12% |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 库存准确率 | 78% | 98% | 12个月 |
| 2 | 食品安全响应时间 | 72小时 | <4小时 | 18个月 |
| 3 | 供应链端到端可见性 | 30% | 95% | 18个月 |
| 4 | 新品上架周期 | 45天 | 14天 | 12个月 |
| 5 | 退货处理周期 | 14天 | 3天 | 9个月 |

### 2.4 技术挑战

1. **大规模数据处理**：日均处理3亿次扫描事件，峰值达500,000次/分钟

2. **全球标准统一**：需统一GTIN、GLN、SSCC在全球12,000+门店的应用

3. **遗留系统集成**：需与SAP、Oracle、门店POS、WMS等50+系统无缝集成

4. **实时追溯需求**：食品安全事件需在4小时内定位受影响批次

5. **供应商合规**：8,000+供应商需在18个月内完成GS1标准升级

### 2.5 Schema定义

**GTIN产品标识Schema**：

```dsl
schema GS1_GTIN_Product {
  gtin: {
    gtin_type: Enum { GTIN8, GTIN12, GTIN13, GTIN14 } @value(GTIN13)
    gtin_identifier: String @value("1234567890128") @length(8..14)
    check_digit: Integer @value(8) @range(0..9)
    
    structure: {
      company_prefix: String @value("1234567") @length(4..12)
      item_reference: String @value("89012") @length(1..6)
    }
  } @required
  
  product_info: {
    brand_name: String @value("Premium Coffee")
    product_description: String @value("Organic Arabica Coffee Beans 500g")
    product_category: String @value("Food & Beverage")
    net_content: {
      value: Decimal @value(500.0)
      unit: Enum { G, KG, ML, L, OZ, LB } @value(G)
    }
    country_of_origin: String @value("CO") @length(2)
  }
  
  packaging: {
    hierarchy: List[PackageLevel] {
      base_unit: {
        level: Integer @value(1)
        gtin: String @value("1234567890128")
        quantity: Integer @value(1)
      }
      case: {
        level: Integer @value(2)
        gtin: String @value("2234567890125")
        quantity: Integer @value(12)
      }
      pallet: {
        level: Integer @value(3)
        sscc: String @value("012345678901234567")
        quantity: Integer @value(48)
      }
    }
  }
  
  traceability: {
    batch_lot: String @value("LOT-2025-A001")
    serial_number: Optional[String]
    expiry_date: Date @value("2025-12-31")
    production_date: Date @value("2025-01-15")
  }
} @standard("GS1_General_Specifications")
```

### 2.6 完整实现代码

```python
"""
MegaRetail零售供应链GS1标识系统
支持GTIN、GLN、SSCC管理和EPCIS追溯
"""

import re
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict


class GS1IdentifierType(Enum):
    """GS1标识类型"""
    GTIN = "GTIN"
    GLN = "GLN"
    SSCC = "SSCC"
    GRAI = "GRAI"
    GIAI = "GIAI"
    GSRN = "GSRN"


class PackageLevel(Enum):
    """包装层级"""
    BASE_UNIT = 1
    CASE = 2
    PALLET = 3
    CONTAINER = 4


@dataclass
class GTIN:
    """全球贸易项目编号"""
    identifier: str
    gtin_type: str = "GTIN13"
    
    def __post_init__(self):
        # 清理并标准化
        self.identifier = self.identifier.strip()
        if len(self.identifier) == 8:
            self.gtin_type = "GTIN8"
        elif len(self.identifier) == 12:
            self.gtin_type = "GTIN12"
        elif len(self.identifier) == 13:
            self.gtin_type = "GTIN13"
        elif len(self.identifier) == 14:
            self.gtin_type = "GTIN14"
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证GTIN"""
        errors = []
        
        if not self.identifier.isdigit():
            errors.append("GTIN必须全是数字")
        
        if len(self.identifier) not in [8, 12, 13, 14]:
            errors.append(f"GTIN长度无效: {len(self.identifier)}")
        
        # 校验位验证
        if len(errors) == 0 and not self._validate_check_digit():
            errors.append("GTIN校验位无效")
        
        return len(errors) == 0, errors
    
    def _validate_check_digit(self) -> bool:
        """验证校验位"""
        digits = [int(d) for d in self.identifier]
        check_digit = digits[-1]
        payload = digits[:-1]
        
        # 计算校验位
        total = 0
        for i, d in enumerate(reversed(payload)):
            if i % 2 == 0:
                total += d * 3
            else:
                total += d
        
        calculated = (10 - (total % 10)) % 10
        return calculated == check_digit
    
    def calculate_check_digit(self, payload: str) -> int:
        """计算校验位"""
        digits = [int(d) for d in payload]
        total = 0
        for i, d in enumerate(reversed(digits)):
            if i % 2 == 0:
                total += d * 3
            else:
                total += d
        return (10 - (total % 10)) % 10
    
    def to_upc_a(self) -> str:
        """转换为UPC-A格式"""
        if len(self.identifier) == 12:
            return self.identifier
        elif len(self.identifier) == 13:
            return self.identifier[1:]  # 移除首位
        return self.identifier
    
    def to_gtin14(self) -> str:
        """转换为GTIN-14"""
        if len(self.identifier) == 14:
            return self.identifier
        elif len(self.identifier) == 13:
            return "0" + self.identifier
        elif len(self.identifier) == 12:
            return "00" + self.identifier
        return self.identifier.zfill(14)
    
    @classmethod
    def from_upc_a(cls, upc: str) -> 'GTIN':
        """从UPC-A创建"""
        return cls(identifier="0" + upc, gtin_type="GTIN13")


@dataclass
class GLN:
    """全球位置编号"""
    identifier: str
    location_name: str = ""
    location_type: str = ""
    address: Dict[str, str] = field(default_factory=dict)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证GLN"""
        errors = []
        
        if len(self.identifier) != 13:
            errors.append(f"GLN长度必须为13位: {len(self.identifier)}")
        
        if not self.identifier.isdigit():
            errors.append("GLN必须全是数字")
        
        # 校验位
        if len(errors) == 0:
            digits = [int(d) for d in self.identifier]
            check_digit = digits[-1]
            payload = digits[:-1]
            
            total = 0
            for i, d in enumerate(reversed(payload)):
                if i % 2 == 0:
                    total += d
                else:
                    total += d * 3
            
            calculated = (10 - (total % 10)) % 10
            if calculated != check_digit:
                errors.append("GLN校验位无效")
        
        return len(errors) == 0, errors


@dataclass
class SSCC:
    """系列货运包装箱代码"""
    identifier: str
    extension_digit: str = "0"
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证SSCC"""
        errors = []
        
        if len(self.identifier) != 18:
            errors.append(f"SSCC长度必须为18位: {len(self.identifier)}")
        
        if not self.identifier.isdigit():
            errors.append("SSCC必须全是数字")
        
        return len(errors) == 0, errors
    
    def to_gs1_element_string(self) -> str:
        """转换为GS1元素字符串"""
        return f"(00){self.identifier}"
    
    def to_human_readable(self) -> str:
        """转换为人类可读格式"""
        return f"{self.identifier[:2]} {self.identifier[2:10]} {self.identifier[10:17]} {self.identifier[17]}"


@dataclass
class EPCIS_Event:
    """EPCIS事件"""
    event_id: str
    event_type: str  # ObjectEvent, AggregationEvent, TransactionEvent, TransformationEvent
    event_time: datetime
    event_timezone: str
    action: str  # ADD, OBSERVE, DELETE
    biz_step: str
    disposition: str
    read_point: str
    biz_location: str
    epc_list: List[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    child_epcs: List[str] = field(default_factory=list)
    biz_transaction_list: List[Dict[str, str]] = field(default_factory=list)
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON格式"""
        return {
            "eventID": self.event_id,
            "type": self.event_type,
            "eventTime": self.event_time.isoformat(),
            "eventTimeZoneOffset": self.event_timezone,
            "action": self.action,
            "bizStep": self.biz_step,
            "disposition": self.disposition,
            "readPoint": {"id": self.read_point},
            "bizLocation": {"id": self.biz_location},
            "epcList": self.epc_list if self.epc_list else None,
            "parentID": self.parent_id,
            "childEPCs": self.child_epcs if self.child_epcs else None,
            "bizTransactionList": [{"type": bt["type"], "bizTransaction": bt["value"]} 
                                  for bt in self.biz_transaction_list] if self.biz_transaction_list else None
        }


class GS1Validator:
    """GS1验证器"""
    
    def validate_gtin(self, gtin: GTIN) -> Tuple[bool, List[str]]:
        """验证GTIN"""
        return gtin.validate()
    
    def validate_gln(self, gln: GLN) -> Tuple[bool, List[str]]:
        """验证GLN"""
        return gln.validate()
    
    def validate_sscc(self, sscc: SSCC) -> Tuple[bool, List[str]]:
        """验证SSCC"""
        return sscc.validate()


class EPCISQueryEngine:
    """EPCIS查询引擎"""
    
    def __init__(self):
        self.events: Dict[str, EPCIS_Event] = {}
        self.epc_index: Dict[str, List[str]] = defaultdict(list)
        self.time_index: Dict[str, List[str]] = defaultdict(list)
    
    def add_event(self, event: EPCIS_Event):
        """添加事件"""
        self.events[event.event_id] = event
        
        # 索引EPC
        for epc in event.epc_list:
            self.epc_index[epc].append(event.event_id)
        
        # 索引时间
        date_key = event.event_time.strftime("%Y-%m-%d")
        self.time_index[date_key].append(event.event_id)
    
    def query_by_epc(self, epc: str) -> List[EPCIS_Event]:
        """按EPC查询事件"""
        event_ids = self.epc_index.get(epc, [])
        return [self.events[eid] for eid in event_ids]
    
    def query_trace_path(self, epc: str) -> List[Dict[str, Any]]:
        """查询追溯路径"""
        events = self.query_by_epc(epc)
        events.sort(key=lambda e: e.event_time)
        
        return [
            {
                "step": i + 1,
                "timestamp": e.event_time.isoformat(),
                "location": e.biz_location,
                "biz_step": e.biz_step,
                "action": e.action
            }
            for i, e in enumerate(events)
        ]
    
    def query_aggregation_children(self, parent_sscc: str) -> List[str]:
        """查询聚合事件的子项"""
        children = []
        for event in self.events.values():
            if (event.event_type == "AggregationEvent" and 
                event.parent_id == parent_sscc and 
                event.action in ["ADD", "OBSERVE"]):
                children.extend(event.child_epcs)
        return children


class SupplyChainTracer:
    """供应链追溯器"""
    
    def __init__(self, query_engine: EPCISQueryEngine):
        self.query_engine = query_engine
    
    def trace_forward(self, gtin: str, batch_lot: str) -> Dict[str, Any]:
        """正向追溯（从生产到消费）"""
        # 构建SGTIN EPC
        sgtin = f"urn:epc:id:sgtin:{gtin[:7]}.{gtin[7:12]}.{batch_lot}"
        
        trace_path = self.query_engine.query_trace_path(sgtin)
        
        return {
            "trace_type": "forward",
            "gtin": gtin,
            "batch_lot": batch_lot,
            "epc": sgtin,
            "steps": len(trace_path),
            "trace_path": trace_path,
            "origin": trace_path[0] if trace_path else None,
            "destination": trace_path[-1] if trace_path else None
        }
    
    def trace_backward(self, gtin: str, batch_lot: str) -> Dict[str, Any]:
        """反向追溯（从消费到生产）"""
        sgtin = f"urn:epc:id:sgtin:{gtin[:7]}.{gtin[7:12]}.{batch_lot}"
        
        trace_path = self.query_engine.query_trace_path(sgtin)
        trace_path.reverse()
        
        return {
            "trace_type": "backward",
            "gtin": gtin,
            "batch_lot": batch_lot,
            "epc": sgtin,
            "steps": len(trace_path),
            "trace_path": trace_path,
            "origin": trace_path[-1] if trace_path else None,
            "current_location": trace_path[0] if trace_path else None
        }
    
    def find_affected_products(self, batch_lot: str, location: str) -> List[str]:
        """查找受影响的产品（召回场景）"""
        affected = []
        for event in self.query_engine.events.values():
            if (any(batch_lot in epc for epc in event.epc_list) and
                event.biz_location == location):
                affected.extend(event.epc_list)
        return list(set(affected))


class GS1BarcodeEncoder:
    """GS1条码编码器"""
    
    def encode_gtin_14(self, gtin14: str) -> str:
        """编码GTIN-14到GS1-128"""
        return f"(01){gtin14}"
    
    def encode_sscc(self, sscc: str) -> str:
        """编码SSCC到GS1-128"""
        return f"(00){sscc}"
    
    def encode_batch_lot(self, gtin: str, batch: str, expiry: str) -> str:
        """编码GTIN+批次+有效期"""
        return f"(01){gtin}(10){batch}(17){expiry}"
    
    def parse_barcode(self, barcode: str) -> Dict[str, str]:
        """解析GS1条码"""
        result = {}
        pattern = r'\((\d{2})\)([^\(]+)'
        matches = re.findall(pattern, barcode)
        
        ai_mapping = {
            "00": "sscc",
            "01": "gtin",
            "10": "batch_lot",
            "11": "production_date",
            "15": "best_before",
            "17": "expiry_date",
            "21": "serial_number",
            "30": "count"
        }
        
        for ai, value in matches:
            key = ai_mapping.get(ai, f"AI_{ai}")
            result[key] = value.strip()
        
        return result


def main():
    """主函数 - 演示"""
    # 创建GTIN
    gtin = GTIN(identifier="1234567890128")
    is_valid, errors = gtin.validate()
    print(f"GTIN验证: {'通过' if is_valid else '失败'} {errors}")
    print(f"GTIN-14格式: {gtin.to_gtin14()}")
    
    # 创建GLN
    gln = GLN(
        identifier="1234567890123",
        location_name="Distribution Center A",
        location_type="WAREHOUSE",
        address={"city": "Shanghai", "country": "CN"}
    )
    is_valid, errors = gln.validate()
    print(f"\nGLN验证: {'通过' if is_valid else '失败'} {errors}")
    
    # 创建SSCC
    sscc = SSCC(identifier="012345678901234567")
    is_valid, errors = sscc.validate()
    print(f"\nSSCC验证: {'通过' if is_valid else '失败'}")
    print(f"SSCC可读格式: {sscc.to_human_readable()}")
    
    # 创建EPCIS事件
    query_engine = EPCISQueryEngine()
    
    events = [
        EPCIS_Event(
            event_id="evt-001",
            event_type="ObjectEvent",
            event_time=datetime(2025, 1, 15, 10, 0, 0),
            event_timezone="+08:00",
            action="ADD",
            biz_step="urn:epcglobal:cbv:bizstep:receiving",
            disposition="urn:epcglobal:cbv:disp:in_progress",
            read_point="urn:epc:id:sgln:1234567890123.pos1",
            biz_location="urn:epc:id:sgln:1234567890123",
            epc_list=["urn:epc:id:sgtin:1234567.89012.LOT001"],
            biz_transaction_list=[{"type": "po", "value": "PO-2025-001"}]
        ),
        EPCIS_Event(
            event_id="evt-002",
            event_type="ObjectEvent",
            event_time=datetime(2025, 1, 16, 14, 0, 0),
            event_timezone="+08:00",
            action="OBSERVE",
            biz_step="urn:epcglobal:cbv:bizstep:shipping",
            disposition="urn:epcglobal:cbv:disp:in_transit",
            read_point="urn:epc:id:sgln:1234567890123.dock1",
            biz_location="urn:epc:id:sgln:1234567890123",
            epc_list=["urn:epc:id:sgtin:1234567.89012.LOT001"]
        ),
        EPCIS_Event(
            event_id="evt-003",
            event_type="ObjectEvent",
            event_time=datetime(2025, 1, 18, 9, 0, 0),
            event_timezone="+08:00",
            action="OBSERVE",
            biz_step="urn:epcglobal:cbv:bizstep:receiving",
            disposition="urn:epcglobal:cbv:disp:in_progress",
            read_point="urn:epc:id:sgln:9876543210987.pos1",
            biz_location="urn:epc:id:sgln:9876543210987",
            epc_list=["urn:epc:id:sgtin:1234567.89012.LOT001"]
        )
    ]
    
    for event in events:
        query_engine.add_event(event)
    
    # 追溯查询
    tracer = SupplyChainTracer(query_engine)
    epc = "urn:epc:id:sgtin:1234567.89012.LOT001"
    
    print("\n正向追溯:")
    forward = tracer.trace_forward("1234567890128", "LOT001")
    print(json.dumps(forward, indent=2, default=str))
    
    # 条码编码
    encoder = GS1BarcodeEncoder()
    barcode = encoder.encode_batch_lot("12345678901234", "LOT001", "250131")
    print(f"\nGS1条码: {barcode}")
    
    parsed = encoder.parse_barcode(barcode)
    print(f"解析结果: {json.dumps(parsed, indent=2)}")


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 库存准确率 | 78% | 98.5% | +20.5% |
| 缺货率 | 8% | 1.5% | -81% |
| 食品安全响应时间 | 72小时 | 2.5小时 | -96% |
| 供应链可见性 | 30% | 96% | +66% |
| 新品上架周期 | 45天 | 12天 | -73% |
| 退货处理周期 | 14天 | 2.5天 | -82% |

#### ROI计算

**投资成本**（24个月项目周期）：
- GS1标识系统：1,200万美元
- EPCIS追溯平台：800万美元
- 门店系统集成：600万美元
- 供应商培训：200万美元
- **总投资**：2,800万美元

**年度收益**：
- 缺货损失减少：8,500万美元
- 库存优化节约：3,200万美元
- 退货损耗减少：1,800万美元
- **年度总收益**：1.35亿美元

**ROI分析**：
- 投资回收期：2.5个月
- 3年ROI：1,346%

#### 经验教训

**成功因素**：
1. **供应商协同**：建立供应商门户，自助完成GTIN/GLN注册
2. **分阶段推广**：先试点100家门店，再全面推广
3. **全员培训**：对230万员工进行GS1标准培训

**挑战与应对**：
1. **中小供应商阻力**：提供免费工具和咨询服务
2. **数据质量参差不齐**：建立数据质量评分体系
3. **跨国标准差异**：建立区域化映射表

---

## 3. 案例2：物流GLN位置管理

详见 `04_Transformation.md` 第3章。

## 4. 案例3：包装SSCC追踪

详见 `04_Transformation.md` 第4章。

## 5. 案例4：EPCIS供应链追溯

详见 `04_Transformation.md` 第5章。

## 6. 案例5：GS1数据存储与分析

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
