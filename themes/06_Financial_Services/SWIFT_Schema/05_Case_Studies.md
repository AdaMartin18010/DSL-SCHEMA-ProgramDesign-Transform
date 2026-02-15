# SWIFT Schema实践案例

## 📑 目录

- [SWIFT Schema实践案例](#swift-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：SwiftNet银行跨境支付网络升级](#2-案例1swiftnet银行跨境支付网络升级)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：MT202银行间转账](#3-案例2mt202银行间转账)
  - [4. 案例3：SWIFT gpi支付追踪](#4-案例3swift-gpi支付追踪)
  - [5. 案例4：MT到MX转换](#5-案例4mt到mx转换)
  - [6. 案例5：SWIFT数据存储与分析系统](#6-案例5swift数据存储与分析系统)

---

## 1. 案例概述

本文档提供SWIFT Schema在实际应用中的实践案例，涵盖MT消息、gpi支付追踪、ISO 20022迁移等场景。

---

## 2. 案例1：SwiftNet银行跨境支付网络升级

### 2.1 企业背景

**SwiftNet银行网络**是由85家国际银行组成的跨境支付联盟，年处理跨境支付交易量超过2500万笔，覆盖120个国家，是全球贸易金融的重要基础设施。

- **成立时间**：1998年
- **成员银行**：85家国际银行
- **年交易量**：2500万笔跨境支付
- **年交易额**：4.5万亿美元
- **原系统**：主要基于SWIFT MT标准，MT103占比65%，MT202占比30%
- **技术债务**：部分成员银行仍使用COBOL系统，与SWIFT gpi不兼容

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 具体表现 |
|------|------|----------|----------|
| 1 | **支付状态不透明** | 严重 | 客户无法追踪支付进度，60%的查询需要人工响应 |
| 2 | **费用信息缺失** | 高 | MT格式无法传递完整费用明细，导致35%的费用争议 |
| 3 | **处理时间长** | 高 | 跨境支付平均耗时2-5个工作日，客户满意度低 |
| 4 | **合规检查分散** | 高 | 各银行独立进行制裁筛查，重复检查增加成本 |
| 5 | **异常处理慢** | 中 | 支付异常平均解决时间48小时，影响资金周转 |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 支付追踪覆盖率 | 15% | 100% | 12个月 |
| 2 | 平均支付处理时间 | 3.5天 | <1天 | 18个月 |
| 3 | 费用透明度 | 40% | 95% | 12个月 |
| 4 | 客户查询响应时间 | 4小时 | <5分钟 | 6个月 |
| 5 | 直通处理率 | 65% | 92% | 12个月 |

### 2.4 技术挑战

1. **SWIFT gpi集成**：需要在不中断现有MT流程的情况下，逐步引入gpi追踪能力

2. **ISO 20022迁移**：成员银行系统异构，迁移进度不一，需支持双向转换

3. **实时消息处理**：gpi要求30分钟内确认支付状态，对系统响应时间要求极高

4. **多币种清算**：支持35种货币的实时汇率处理和货币兑换

5. **监管合规一致性**：需要建立联盟级别的制裁筛查和反洗钱共享机制

### 2.5 Schema定义

**MT103跨境支付Schema**：

```dsl
schema MT103CrossBorderPayment {
  field_20: String @value("REF123456789") @tag(":20:")

  field_23B: Enum { CRED } @value(CRED) @tag(":23B:")

  field_32A: DateAmountCurrency {
    date: Date @value("250121") @format("YYMMDD")
    currency: String @value("USD")
    amount: Decimal @value(10000.00) @precision(15,2)
  } @tag(":32A:")

  field_50A: PartyIdentifier {
    account: String @value("1234567890")
    name_and_address: String @value("ABC COMPANY\n123 MAIN ST\nNEW YORK NY 10001")
  } @tag(":50A:")

  field_59: Beneficiary {
    account: String @value("9876543210")
    name_and_address: String @value("XYZ CORPORATION\n456 BROADWAY\nLONDON EC1A 1BB")
  } @tag(":59:")

  field_71A: Enum { SHA } @value(SHA) @tag(":71A:")

  field_72: Optional<String> @tag(":72:")
} @standard("SWIFT_MT103")
```

### 2.6 完整实现代码

```python
"""
SwiftNet银行跨境支付处理系统
支持MT消息解析、gpi追踪、ISO 20022转换
"""

import re
import uuid
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from abc import ABC, abstractmethod
import json


class MTFieldType(Enum):
    """MT字段类型"""
    TEXT = "TEXT"
    NUMERIC = "NUMERIC"
    AMOUNT = "AMOUNT"
    DATE = "DATE"
    CHOICE = "CHOICE"


class GPIStatus(Enum):
    """gpi支付状态"""
    ACSP = "ACSP"  # AcceptedSettlementInProcess
    ACSC = "ACSC"  # AcceptedSettlementCompleted
    ACWC = "ACWC"  # AcceptedWithChange
    PART = "PART"  # PartiallyAccepted
    PDNG = "PDNG"  # Pending
    RJCT = "RJCT"  # Rejected


@dataclass
class MTField:
    """MT消息字段"""
    tag: str
    value: str
    field_type: MTFieldType = MTFieldType.TEXT
    
    def parse_amount(self) -> Optional[Tuple[str, Decimal, str]]:
        """解析金额字段 (32A格式: YYMMDDCURRENCYAMOUNT)"""
        if self.field_type == MTFieldType.AMOUNT and len(self.value) >= 10:
            dt_str = self.value[:6]
            currency = self.value[6:9]
            amount_str = self.value[9:].replace(',', '.')
            try:
                dt = datetime.strptime(dt_str, "%y%m%d")
                amount = Decimal(amount_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                return currency, amount, dt.strftime("%Y-%m-%d")
            except (ValueError, IndexError):
                pass
        return None
    
    def parse_party(self) -> Dict[str, str]:
        """解析参与方字段 (50A/59格式)"""
        lines = self.value.split('\n')
        result = {"account": "", "name": "", "address": ""}
        if lines:
            result["account"] = lines[0].strip()
            if len(lines) > 1:
                result["name"] = lines[1].strip()
            if len(lines) > 2:
                result["address"] = '\n'.join(lines[2:]).strip()
        return result


@dataclass
class MT103Message:
    """MT103消息数据类"""
    sender_bic: str
    receiver_bic: str
    message_type: str = "103"
    fields: Dict[str, MTField] = field(default_factory=dict)
    uetr: Optional[str] = None  # SWIFT gpi唯一端对端交易参考
    
    @property
    def transaction_reference(self) -> Optional[str]:
        return self.fields.get(":20:").value if ":20:" in self.fields else None
    
    @property
    def amount_info(self) -> Optional[Tuple[str, Decimal, str]]:
        field_32a = self.fields.get(":32A:")
        if field_32a:
            return field_32a.parse_amount()
        return None
    
    @property
    def ordering_customer(self) -> Dict[str, str]:
        field_50a = self.fields.get(":50A:") or self.fields.get(":50K:")
        if field_50a:
            return field_50a.parse_party()
        return {}
    
    @property
    def beneficiary(self) -> Dict[str, str]:
        field_59 = self.fields.get(":59:") or self.fields.get(":59A:")
        if field_59:
            return field_59.parse_party()
        return {}
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证MT103消息"""
        errors = []
        
        required_fields = [":20:", ":23B:", ":32A:", ":50A:", ":59:"]
        for field_tag in required_fields:
            if field_tag not in self.fields:
                errors.append(f"缺少必需字段: {field_tag}")
        
        # 验证金额
        if ":32A:" in self.fields:
            amount_info = self.amount_info
            if amount_info is None:
                errors.append("字段32A格式无效")
            elif amount_info[1] <= 0:
                errors.append("金额必须大于0")
        
        # 验证BIC
        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', self.sender_bic):
            errors.append(f"发送方BIC格式无效: {self.sender_bic}")
        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', self.receiver_bic):
            errors.append(f"接收方BIC格式无效: {self.receiver_bic}")
        
        return len(errors) == 0, errors
    
    def to_swift_format(self) -> str:
        """转换为SWIFT MT格式"""
        lines = [
            "{1:F01" + self.sender_bic + "0000000000}",
            "{2:I103" + self.receiver_bic + "N}",
            "{4:",
        ]
        for tag, field in sorted(self.fields.items()):
            lines.append(f"{tag}{field.value}")
        lines.append("-}")
        return "\n".join(lines)
    
    @classmethod
    def parse(cls, swift_text: str) -> 'MT103Message':
        """解析SWIFT MT文本"""
        lines = swift_text.strip().split('\n')
        sender_bic = ""
        receiver_bic = ""
        fields = {}
        
        for line in lines:
            if line.startswith("{1:F01"):
                sender_bic = line[6:14]
            elif line.startswith("{2:I103"):
                receiver_bic = line[7:15]
            elif line.startswith(":"):
                tag_end = line.find(":", 1)
                if tag_end > 0:
                    tag = line[:tag_end+1]
                    value = line[tag_end+1:]
                    field_type = MTFieldType.AMOUNT if tag == ":32A:" else MTFieldType.TEXT
                    fields[tag] = MTField(tag, value, field_type)
        
        return cls(sender_bic=sender_bic, receiver_bic=receiver_bic, fields=fields)


@dataclass
class GPITrackingEvent:
    """gpi追踪事件"""
    event_id: str
    uetr: str
    timestamp: datetime
    status: GPIStatus
    location: str
    bank_bic: str
    additional_info: Optional[str] = None


@dataclass
class SWIFTGPIMessage:
    """SWIFT gpi消息"""
    uetr: str
    transaction_status: GPIStatus
    initiation_time: datetime
    last_update_time: datetime
    debtor_agent: str
    creditor_agent: str
    instructed_amount: Decimal
    instructed_currency: str
    events: List[GPITrackingEvent] = field(default_factory=list)
    
    def get_status_description(self) -> str:
        """获取状态描述"""
        descriptions = {
            GPIStatus.ACSP: "支付正在处理中，尚未完成结算",
            GPIStatus.ACSC: "支付已完成结算",
            GPIStatus.ACWC: "支付已接受但有修改",
            GPIStatus.PART: "支付部分接受",
            GPIStatus.PDNG: "支付待处理",
            GPIStatus.RJCT: "支付被拒绝"
        }
        return descriptions.get(self.transaction_status, "未知状态")
    
    def get_processing_time_hours(self) -> float:
        """获取处理时长（小时）"""
        return (self.last_update_time - self.initiation_time).total_seconds() / 3600


class SanctionsScreeningService:
    """制裁筛查服务"""
    
    def __init__(self):
        self.sanctions_list = set()  # 制裁名单
        self.pep_list = set()  # 政治敏感人物名单
    
    def screen_party(self, party_info: Dict[str, str]) -> Tuple[bool, List[str]]:
        """筛查参与方"""
        alerts = []
        name = party_info.get("name", "").upper()
        account = party_info.get("account", "")
        
        # 检查制裁名单
        for sanctioned in self.sanctions_list:
            if sanctioned in name:
                alerts.append(f"制裁名单命中: {sanctioned}")
        
        # 检查PEP名单
        for pep in self.pep_list:
            if pep in name:
                alerts.append(f"PEP名单命中: {pep}")
        
        return len(alerts) == 0, alerts
    
    def screen_message(self, message: MT103Message) -> Tuple[bool, Dict[str, List[str]]]:
        """筛查整个消息"""
        results = {}
        is_clean = True
        
        # 筛查汇款人
        debtor = message.ordering_customer
        clean, alerts = self.screen_party(debtor)
        if not clean:
            results["debtor"] = alerts
            is_clean = False
        
        # 筛查收款人
        creditor = message.beneficiary
        clean, alerts = self.screen_party(creditor)
        if not clean:
            results["creditor"] = alerts
            is_clean = False
        
        return is_clean, results


class SWIFTMessageProcessor:
    """SWIFT消息处理器"""
    
    def __init__(self, sanctions_service: SanctionsScreeningService):
        self.sanctions_service = sanctions_service
        self.gpi_messages: Dict[str, SWIFTGPIMessage] = {}
        self.processed_messages: Dict[str, MT103Message] = {}
        self.metrics = {
            "total_received": 0,
            "validated": 0,
            "sanctions_blocked": 0,
            "gpi_tracked": 0,
            "settled": 0
        }
    
    def process_mt103(self, message: MT103Message) -> Dict[str, Any]:
        """处理MT103消息"""
        result = {
            "message_id": message.transaction_reference,
            "status": "RECEIVED",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }
        
        self.metrics["total_received"] += 1
        
        # 1. 验证消息
        is_valid, errors = message.validate()
        if not is_valid:
            result["status"] = "REJECTED"
            result["details"]["validation_errors"] = errors
            return result
        
        self.metrics["validated"] += 1
        result["status"] = "VALIDATED"
        
        # 2. 制裁筛查
        is_clean, screening_results = self.sanctions_service.screen_message(message)
        if not is_clean:
            result["status"] = "SANCTIONS_BLOCKED"
            result["details"]["sanctions_alerts"] = screening_results
            self.metrics["sanctions_blocked"] += 1
            return result
        
        # 3. 创建gpi追踪
        if message.uetr:
            gpi_msg = SWIFTGPIMessage(
                uetr=message.uetr,
                transaction_status=GPIStatus.ACSP,
                initiation_time=datetime.now(),
                last_update_time=datetime.now(),
                debtor_agent=message.sender_bic,
                creditor_agent=message.receiver_bic,
                instructed_amount=message.amount_info[1] if message.amount_info else Decimal("0"),
                instructed_currency=message.amount_info[0] if message.amount_info else "",
                events=[
                    GPITrackingEvent(
                        event_id=str(uuid.uuid4()),
                        uetr=message.uetr,
                        timestamp=datetime.now(),
                        status=GPIStatus.ACSP,
                        location="ORIGINATING_BANK",
                        bank_bic=message.sender_bic,
                        additional_info="Payment received and validated"
                    )
                ]
            )
            self.gpi_messages[message.uetr] = gpi_msg
            self.metrics["gpi_tracked"] += 1
            result["details"]["gpi_status"] = gpi_msg.transaction_status.value
        
        # 4. 存储消息
        if message.transaction_reference:
            self.processed_messages[message.transaction_reference] = message
        
        result["status"] = "PROCESSING"
        return result
    
    def update_gpi_status(self, uetr: str, status: GPIStatus, location: str, 
                         bank_bic: str, info: Optional[str] = None) -> bool:
        """更新gpi状态"""
        if uetr not in self.gpi_messages:
            return False
        
        gpi_msg = self.gpi_messages[uetr]
        gpi_msg.transaction_status = status
        gpi_msg.last_update_time = datetime.now()
        
        event = GPITrackingEvent(
            event_id=str(uuid.uuid4()),
            uetr=uetr,
            timestamp=datetime.now(),
            status=status,
            location=location,
            bank_bic=bank_bic,
            additional_info=info
        )
        gpi_msg.events.append(event)
        
        if status == GPIStatus.ACSC:
            self.metrics["settled"] += 1
        
        return True
    
    def get_gpi_tracking(self, uetr: str) -> Optional[SWIFTGPIMessage]:
        """获取gpi追踪信息"""
        return self.gpi_messages.get(uetr)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取处理指标"""
        total = self.metrics["total_received"]
        return {
            **self.metrics,
            "validation_rate": (self.metrics["validated"] / total * 100) if total > 0 else 0,
            "gpi_coverage": (self.metrics["gpi_tracked"] / total * 100) if total > 0 else 0,
            "settlement_rate": (self.metrics["settled"] / self.metrics["gpi_tracked"] * 100) 
                              if self.metrics["gpi_tracked"] > 0 else 0
        }


class SWIFTMessageRouter:
    """SWIFT消息路由器"""
    
    def __init__(self):
        self.routing_table: Dict[str, Dict[str, Any]] = {}
        self.correspondent_banks: Dict[str, List[str]] = {}
    
    def add_route(self, currency: str, destination_country: str, 
                  intermediary_bic: Optional[str], beneficiary_bic: str):
        """添加路由"""
        key = f"{currency}:{destination_country}"
        self.routing_table[key] = {
            "intermediary": intermediary_bic,
            "beneficiary": beneficiary_bic
        }
    
    def find_route(self, currency: str, beneficiary_bic: str) -> Optional[Dict[str, Any]]:
        """查找最优路由"""
        country = beneficiary_bic[4:6] if len(beneficiary_bic) >= 6 else ""
        key = f"{currency}:{country}"
        return self.routing_table.get(key)
    
    def build_mt103_with_routing(self, base_message: MT103Message, 
                                 beneficiary_bic: str) -> MT103Message:
        """构建带路由信息的MT103"""
        message = MT103Message(
            sender_bic=base_message.sender_bic,
            receiver_bic=base_message.receiver_bic,
            message_type="103",
            fields=base_message.fields.copy(),
            uetr=base_message.uetr or str(uuid.uuid4()).upper()
        )
        
        # 查找路由
        amount_info = base_message.amount_info
        if amount_info:
            currency = amount_info[0]
            route = self.find_route(currency, beneficiary_bic)
            if route:
                # 添加中间行信息
                if route.get("intermediary"):
                    message.fields[":56A:"] = MTField(":56A:", route["intermediary"])
        
        return message


def main():
    """主函数 - 演示用法"""
    # 初始化服务
    sanctions_service = SanctionsScreeningService()
    processor = SWIFTMessageProcessor(sanctions_service)
    router = SWIFTMessageRouter()
    
    # 添加路由
    router.add_route("USD", "GB", "CHASUS33", "BARCGB22")
    router.add_route("EUR", "DE", "COBADEFF", "DEUTDEFF")
    
    # 创建示例MT103消息
    mt103_text = """{1:F01CITIUS33AXXX0000000000}
{2:I103BARCGB22XXXXN}
{4:
:20:REFERENCE123
:23B:CRED
:32A:250121USD50000,00
:50A:/1234567890
ABC COMPANY
123 MAIN STREET
NEW YORK NY 10001
:59:/9876543210
XYZ CORPORATION
456 BROADWAY
LONDON EC1A 1BB
:71A:SHA
-}"""
    
    message = MT103Message.parse(mt103_text)
    message.uetr = str(uuid.uuid4()).upper()
    
    print(f"解析的MT103消息:")
    print(f"  交易参考: {message.transaction_reference}")
    print(f"  金额信息: {message.amount_info}")
    print(f"  汇款人: {message.ordering_customer}")
    print(f"  收款人: {message.beneficiary}")
    print(f"  UETR: {message.uetr}")
    
    # 处理消息
    result = processor.process_mt103(message)
    print(f"\n处理结果: {json.dumps(result, indent=2, default=str)}")
    
    # 更新gpi状态
    processor.update_gpi_status(
        message.uetr,
        GPIStatus.ACSC,
        "BENEFICIARY_BANK",
        "BARCGB22",
        "Payment credited to beneficiary account"
    )
    
    # 查询追踪信息
    tracking = processor.get_gpi_tracking(message.uetr)
    if tracking:
        print(f"\ngpi追踪信息:")
        print(f"  状态: {tracking.transaction_status.value}")
        print(f"  处理时长: {tracking.get_processing_time_hours():.2f}小时")
        print(f"  事件数: {len(tracking.events)}")
    
    # 打印统计
    print(f"\n处理统计: {json.dumps(processor.get_metrics(), indent=2)}")


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| gpi追踪覆盖率 | 15% | 98% | +83% |
| 平均处理时间 | 3.5天 | 18小时 | -79% |
| 费用透明度 | 40% | 96% | +56% |
| 客户查询响应 | 4小时 | 2分钟 | -99% |
| 直通处理率 | 65% | 94% | +29% |
| 异常解决时间 | 48小时 | 6小时 | -87% |

#### ROI计算

**投资成本**（18个月项目周期）：
- SWIFT gpi接入费：450万美元
- 系统开发：680万美元
- 基础设施升级：320万美元
- 成员银行培训：150万美元
- **总投资**：1600万美元

**年度收益**：
- 查询处理成本节约：800万美元
- 争议处理成本节约：1200万美元
- 客户留存提升：2400万美元
- **年度总收益**：4400万美元

**ROI分析**：
- 投资回收期：4.4个月
- 3年ROI：725%

#### 经验教训

**成功因素**：
1. **渐进式迁移**：先接入gpi追踪，再推进ISO 20022全面迁移
2. **共享服务**：建立联盟级制裁筛查中心，避免重复建设
3. **标准化API**：统一接口规范，成员银行平均集成时间从6个月降至6周

**挑战与应对**：
1. **成员银行步调不一**：设立技术援助基金，帮助小型银行升级
2. **数据隐私担忧**：采用零知识证明技术，在保护隐私前提下完成合规检查
3. **历史系统兼容**：保留MT-MX转换网关至少5年

---

## 3. 案例2：MT202银行间转账

详见 `04_Transformation.md` 第3章。

## 4. 案例3：SWIFT gpi支付追踪

详见 `04_Transformation.md` 第4章。

## 5. 案例4：MT到MX转换

详见 `04_Transformation.md` 第2章。

## 6. 案例5：SWIFT数据存储与分析系统

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
