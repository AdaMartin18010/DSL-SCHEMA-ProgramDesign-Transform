# Payment Schema实践案例

## 📑 目录

- [Payment Schema实践案例](#payment-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：QuickPay电商平台支付系统重构](#2-案例1quickpay电商平台支付系统重构)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：支付清算结算](#3-案例2支付清算结算)
  - [4. 案例3：数字货币支付](#4-案例3数字货币支付)
  - [5. 案例4：Payment到ISO 20022转换](#5-案例4payment到iso-20022转换)
  - [6. 案例5：Payment数据存储与分析系统](#6-案例5payment数据存储与分析系统)

---

## 1. 案例概述

本文档提供Payment Schema在实际应用中的实践案例，涵盖在线支付、清算结算、数字货币等场景。

---

## 2. 案例1：QuickPay电商平台支付系统重构

### 2.1 企业背景

**QuickPay**是亚太地区领先的电商平台，年交易额超过800亿美元，日均订单量300万笔，支持50+国家的跨境交易。

- **成立时间**：2010年
- **用户规模**：4.5亿注册用户
- **商户数量**：200万活跃商户
- **支付方式**：信用卡、借记卡、电子钱包、银行转账等15种
- **原系统问题**：基于单体架构，扩展性差，高峰期频繁宕机

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **支付成功率低** | 严重 | 支付成功率仅89%，每月流失订单价值1.2亿美元 |
| 2 | **欺诈损失高** | 严重 | 年欺诈损失达4500万美元，拒付率2.3% |
| 3 | **结算周期长** | 高 | 商户资金T+7到账，竞争对手已T+1 |
| 4 | **多币种处理复杂** | 中 | 32种货币汇率更新延迟，汇率损失年化800万 |
| 5 | **退款处理慢** | 中 | 平均退款周期14天，客户满意度低 |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 支付成功率 | 89% | 97% | 6个月 |
| 2 | 欺诈拒付率 | 2.3% | <0.5% | 12个月 |
| 3 | 商户结算周期 | T+7 | T+1 | 9个月 |
| 4 | 系统可用性 | 99.5% | 99.99% | 6个月 |
| 5 | 退款处理时间 | 14天 | 3天 | 6个月 |

### 2.4 技术挑战

1. **高并发处理**：大促期间支付请求可达50,000 TPS，需保证99.99%可用性

2. **全球合规要求**：需满足PCI DSS Level 1、GDPR、各地支付牌照要求

3. **实时风控决策**：需在200ms内完成风险评估，误杀率<0.1%

4. **多支付渠道管理**：需统一管理15+支付渠道，智能路由最优渠道

5. **数据一致性保障**：分布式事务处理，确保支付状态最终一致性

### 2.5 Schema定义

**在线支付处理Payment Schema**：

```dsl
schema OnlinePaymentProcessing {
  payment_request: PaymentRequest {
    request_id: String @value("REQ-2025-001")
    merchant_id: String @value("MERCHANT-001")
    order_id: String @value("ORDER-2025-001")
    amount: Decimal @value(1000.00)
    currency: String @value("USD")
    payment_method: Enum @value("CreditCard")

    card_info: CardInfo {
      card_number: String @value("4111111111111111")
      card_holder_name: String @value("John Doe")
      expiry_date: String @value("12/25")
      cvv: String @value("123")
    }

    customer_info: CustomerInfo {
      customer_id: String @value("CUST-001")
      customer_name: String @value("John Doe")
      email: String @value("john.doe@example.com")
      phone: String @value("+1234567890")
    }

    callback_url: String @value("https://merchant.com/callback")
    timestamp: DateTime @value("2025-01-21T10:00:00Z")
    signature: String @value("signature_hash")
  }

  payment_response: PaymentResponse {
    response_id: String @value("RESP-2025-001")
    request_id: String @value("REQ-2025-001")
    status: Enum @value("Success")
    transaction_id: String @value("TXN-2025-001")
    amount: Decimal @value(1000.00)
    currency: String @value("USD")
    payment_time: DateTime @value("2025-01-21T10:00:05Z")
    timestamp: DateTime @value("2025-01-21T10:00:05Z")
    signature: String @value("response_signature_hash")
  }
} @standard("PCI_DSS")
```

### 2.6 完整实现代码

```python
"""
QuickPay电商平台支付处理系统
支持多渠道支付、实时风控、智能路由
"""

import hashlib
import hmac
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
import random


class PaymentStatus(Enum):
    """支付状态"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class PaymentMethod(Enum):
    """支付方式"""
    CREDIT_CARD = "CreditCard"
    DEBIT_CARD = "DebitCard"
    E_WALLET = "EWallet"
    BANK_TRANSFER = "BankTransfer"
    BNPL = "BNPL"


class RiskLevel(Enum):
    """风险等级"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCK = "BLOCK"


@dataclass
class CardInfo:
    """银行卡信息"""
    card_number: str
    card_holder_name: str
    expiry_month: str
    expiry_year: str
    cvv: str
    
    def mask_card_number(self) -> str:
        """脱敏显示卡号"""
        return f"****-****-****-{self.card_number[-4:]}"
    
    def validate(self) -> List[str]:
        """验证卡信息"""
        errors = []
        if not re.match(r'^[0-9]{13,19}$', self.card_number):
            errors.append("卡号格式无效")
        if not self._luhn_check(self.card_number):
            errors.append("卡号校验失败")
        if not re.match(r'^[0-9]{3,4}$', self.cvv):
            errors.append("CVV格式无效")
        return errors
    
    @staticmethod
    def _luhn_check(card_number: str) -> bool:
        """Luhn算法验证"""
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(int(x) for x in str(d * 2))
        return checksum % 10 == 0
    
    def get_card_brand(self) -> str:
        """获取卡品牌"""
        patterns = {
            'Visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
            'Mastercard': r'^5[1-5][0-9]{14}$',
            'Amex': r'^3[47][0-9]{13}$',
            'Discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$'
        }
        for brand, pattern in patterns.items():
            if re.match(pattern, self.card_number):
                return brand
        return "Unknown"


@dataclass
class CustomerInfo:
    """客户信息"""
    customer_id: str
    customer_name: str
    email: str
    phone: str
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    billing_address: Optional[Dict[str, str]] = None
    
    def validate(self) -> List[str]:
        """验证客户信息"""
        errors = []
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
            errors.append("邮箱格式无效")
        return errors


@dataclass
class PaymentRequest:
    """支付请求"""
    request_id: str
    merchant_id: str
    order_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    card_info: Optional[CardInfo] = None
    customer_info: Optional[CustomerInfo] = None
    callback_url: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.amount, (int, float)):
            self.amount = Decimal(str(self.amount))
        self.amount = self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证请求"""
        errors = []
        
        if self.amount <= 0 or self.amount > Decimal('1000000'):
            errors.append(f"金额无效: {self.amount}")
        
        if not re.match(r'^[A-Z]{3}$', self.currency):
            errors.append(f"币种代码无效: {self.currency}")
        
        if self.payment_method == PaymentMethod.CREDIT_CARD and self.card_info:
            errors.extend(self.card_info.validate())
        
        if self.customer_info:
            errors.extend(self.customer_info.validate())
        
        return len(errors) == 0, errors
    
    def generate_signature(self, secret_key: str) -> str:
        """生成请求签名"""
        content = f"{self.request_id}|{self.merchant_id}|{self.order_id}|{self.amount}|{self.currency}"
        return hmac.new(secret_key.encode(), content.encode(), hashlib.sha256).hexdigest()


@dataclass
class PaymentResponse:
    """支付响应"""
    response_id: str
    request_id: str
    status: PaymentStatus
    transaction_id: str
    amount: Decimal
    currency: str
    auth_code: Optional[str] = None
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    payment_time: datetime = field(default_factory=datetime.now)
    message: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None


class RiskEngine:
    """风控引擎"""
    
    def __init__(self):
        self.rules = []
        self.velocity_cache = {}
        self.blocklist = set()
    
    def evaluate(self, request: PaymentRequest) -> Tuple[RiskLevel, float, List[str]]:
        """评估风险"""
        risk_score = 0.0
        risk_factors = []
        
        # 1. 金额检查
        if request.amount > Decimal('10000'):
            risk_score += 20
            risk_factors.append("大额交易")
        
        # 2. 频率检查（简单实现）
        customer_key = request.customer_info.customer_id if request.customer_info else "anonymous"
        current_count = self.velocity_cache.get(customer_key, 0)
        if current_count > 5:
            risk_score += 30
            risk_factors.append("交易频率异常")
        self.velocity_cache[customer_key] = current_count + 1
        
        # 3. 黑名单检查
        if customer_key in self.blocklist:
            risk_score = 100
            risk_factors.append("黑名单用户")
        
        # 4. 卡品牌风险（模拟）
        if request.card_info and request.card_info.get_card_brand() == "Unknown":
            risk_score += 15
            risk_factors.append("未知卡品牌")
        
        # 确定风险等级
        if risk_score >= 80:
            level = RiskLevel.BLOCK
        elif risk_score >= 50:
            level = RiskLevel.HIGH
        elif risk_score >= 20:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return level, risk_score, risk_factors


class PaymentGateway(ABC):
    """支付网关抽象基类"""
    
    @abstractmethod
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        pass
    
    @abstractmethod
    def refund(self, transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def supported_methods(self) -> List[PaymentMethod]:
        pass


class StripeGateway(PaymentGateway):
    """Stripe支付网关（模拟）"""
    
    @property
    def name(self) -> str:
        return "Stripe"
    
    @property
    def supported_methods(self) -> List[PaymentMethod]:
        return [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD, PaymentMethod.BNPL]
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        # 模拟处理
        time.sleep(0.05)  # 模拟网络延迟
        success = random.random() > 0.05  # 95%成功率
        
        return PaymentResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            status=PaymentStatus.CAPTURED if success else PaymentStatus.FAILED,
            transaction_id=f"STRIPE-{uuid.uuid4().hex[:16].upper()}",
            amount=request.amount,
            currency=request.currency,
            auth_code=f"AUTH-{random.randint(100000, 999999)}" if success else None,
            message="Payment successful" if success else "Card declined"
        )
    
    def refund(self, transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        return {
            "refund_id": f"REF-{uuid.uuid4().hex[:12]}",
            "transaction_id": transaction_id,
            "amount": str(amount),
            "status": "SUCCESS"
        }


class PayPalGateway(PaymentGateway):
    """PayPal支付网关（模拟）"""
    
    @property
    def name(self) -> str:
        return "PayPal"
    
    @property
    def supported_methods(self) -> List[PaymentMethod]:
        return [PaymentMethod.E_WALLET, PaymentMethod.CREDIT_CARD]
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        time.sleep(0.08)
        success = random.random() > 0.03
        
        return PaymentResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            status=PaymentStatus.CAPTURED if success else PaymentStatus.FAILED,
            transaction_id=f"PAYPAL-{uuid.uuid4().hex[:16].upper()}",
            amount=request.amount,
            currency=request.currency,
            message="Payment completed" if success else "Payment failed"
        )
    
    def refund(self, transaction_id: str, amount: Decimal) -> Dict[str, Any]:
        return {
            "refund_id": f"PPRF-{uuid.uuid4().hex[:12]}",
            "status": "SUCCESS"
        }


class PaymentRouter:
    """支付路由器 - 智能选择最优支付渠道"""
    
    def __init__(self):
        self.gateways: List[PaymentGateway] = []
        self.gateway_stats: Dict[str, Dict[str, Any]] = {}
    
    def register_gateway(self, gateway: PaymentGateway):
        """注册支付网关"""
        self.gateways.append(gateway)
        self.gateway_stats[gateway.name] = {
            "total_requests": 0,
            "success_count": 0,
            "avg_latency": 0.0
        }
    
    def route(self, request: PaymentRequest) -> PaymentGateway:
        """选择最优支付渠道"""
        # 筛选支持的网关
        candidates = [
            g for g in self.gateways 
            if request.payment_method in g.supported_methods
        ]
        
        if not candidates:
            raise ValueError(f"No gateway supports {request.payment_method}")
        
        # 基于成功率排序
        def score(gateway):
            stats = self.gateway_stats[gateway.name]
            if stats["total_requests"] == 0:
                return 1.0
            return stats["success_count"] / stats["total_requests"]
        
        return max(candidates, key=score)
    
    def update_stats(self, gateway_name: str, success: bool, latency: float):
        """更新网关统计"""
        stats = self.gateway_stats[gateway_name]
        stats["total_requests"] += 1
        if success:
            stats["success_count"] += 1
        # 更新平均延迟
        stats["avg_latency"] = (stats["avg_latency"] * (stats["total_requests"] - 1) + latency) / stats["total_requests"]


class PaymentProcessor:
    """支付处理器"""
    
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.router = PaymentRouter()
        self.transactions: Dict[str, PaymentResponse] = {}
        self.metrics = {
            "total_requests": 0,
            "successful_payments": 0,
            "failed_payments": 0,
            "blocked_by_risk": 0,
            "total_amount_processed": Decimal("0")
        }
    
    def register_gateway(self, gateway: PaymentGateway):
        """注册支付网关"""
        self.router.register_gateway(gateway)
    
    def process(self, request: PaymentRequest) -> PaymentResponse:
        """处理支付请求"""
        self.metrics["total_requests"] += 1
        
        # 1. 验证请求
        is_valid, errors = request.validate()
        if not is_valid:
            return PaymentResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                status=PaymentStatus.FAILED,
                transaction_id="",
                amount=request.amount,
                currency=request.currency,
                message=f"Validation failed: {', '.join(errors)}"
            )
        
        # 2. 风控检查
        risk_level, risk_score, risk_factors = self.risk_engine.evaluate(request)
        
        if risk_level == RiskLevel.BLOCK:
            self.metrics["blocked_by_risk"] += 1
            return PaymentResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                status=PaymentStatus.FAILED,
                transaction_id="",
                amount=request.amount,
                currency=request.currency,
                risk_score=risk_score,
                risk_level=risk_level,
                message=f"Transaction blocked by risk engine: {', '.join(risk_factors)}"
            )
        
        # 3. 选择支付渠道
        gateway = self.router.route(request)
        
        # 4. 执行支付
        start_time = time.time()
        try:
            response = gateway.process_payment(request)
            latency = time.time() - start_time
            
            # 更新统计
            self.router.update_stats(gateway.name, 
                                   response.status == PaymentStatus.CAPTURED, 
                                   latency)
            
            # 更新指标
            if response.status == PaymentStatus.CAPTURED:
                self.metrics["successful_payments"] += 1
                self.metrics["total_amount_processed"] += request.amount
            else:
                self.metrics["failed_payments"] += 1
            
            # 保存交易
            self.transactions[response.transaction_id] = response
            
            # 添加风控信息
            response.risk_score = risk_score
            response.risk_level = risk_level
            
            return response
            
        except Exception as e:
            self.metrics["failed_payments"] += 1
            return PaymentResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                status=PaymentStatus.FAILED,
                transaction_id="",
                amount=request.amount,
                currency=request.currency,
                message=f"Gateway error: {str(e)}"
            )
    
    def refund(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """处理退款"""
        if transaction_id not in self.transactions:
            return {"status": "ERROR", "message": "Transaction not found"}
        
        original = self.transactions[transaction_id]
        refund_amount = amount or original.amount
        
        # 这里应该调用原始网关的退款接口
        return {
            "refund_id": f"RFD-{uuid.uuid4().hex[:12]}",
            "transaction_id": transaction_id,
            "amount": str(refund_amount),
            "status": "PENDING"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取处理指标"""
        total = self.metrics["total_requests"]
        return {
            **self.metrics,
            "success_rate": (self.metrics["successful_payments"] / total * 100) if total > 0 else 0,
            "block_rate": (self.metrics["blocked_by_risk"] / total * 100) if total > 0 else 0
        }


def main():
    """主函数 - 演示用法"""
    processor = PaymentProcessor()
    
    # 注册支付网关
    processor.register_gateway(StripeGateway())
    processor.register_gateway(PayPalGateway())
    
    # 创建测试支付请求
    test_requests = []
    for i in range(100):
        request = PaymentRequest(
            request_id=f"REQ-2025-{i:04d}",
            merchant_id=f"MERCHANT-{random.randint(1, 100):03d}",
            order_id=f"ORDER-2025-{i:04d}",
            amount=Decimal(random.randint(10, 1000)),
            currency=random.choice(["USD", "EUR", "GBP"]),
            payment_method=random.choice([PaymentMethod.CREDIT_CARD, PaymentMethod.E_WALLET]),
            card_info=CardInfo(
                card_number="4111111111111111",
                card_holder_name="Test User",
                expiry_month="12",
                expiry_year="25",
                cvv="123"
            ) if random.random() > 0.3 else None,
            customer_info=CustomerInfo(
                customer_id=f"CUST-{random.randint(1, 50):03d}",
                customer_name="Test User",
                email="test@example.com",
                phone="+1234567890"
            )
        )
        test_requests.append(request)
    
    # 处理支付
    results = {"success": 0, "failed": 0, "blocked": 0}
    for request in test_requests:
        response = processor.process(request)
        if response.status == PaymentStatus.CAPTURED:
            results["success"] += 1
        elif "blocked" in response.message.lower():
            results["blocked"] += 1
        else:
            results["failed"] += 1
    
    print(f"\n处理结果: {json.dumps(results, indent=2)}")
    print(f"\n处理指标: {json.dumps(processor.get_metrics(), indent=2, default=str)}")


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 支付成功率 | 89% | 97.5% | +8.5% |
| 系统可用性 | 99.5% | 99.99% | +0.49% |
| 平均处理时间 | 3.2秒 | 180ms | -94% |
| 欺诈拒付率 | 2.3% | 0.42% | -82% |
| 商户结算周期 | T+7 | T+1 | -86% |
| 峰值处理能力 | 8,000 TPS | 55,000 TPS | +588% |

#### ROI计算

**投资成本**（12个月项目周期）：
- 系统开发：320万美元
- 基础设施：150万美元
- 风控系统：80万美元
- 合规认证：50万美元
- **总投资**：600万美元

**年度收益**：
- 挽回支付失败损失：8,000万美元
- 欺诈损失减少：3,800万美元
- 运维成本节约：400万美元
- **年度总收益**：1.22亿美元

**ROI分析**：
- 投资回收期：0.6个月
- 首年ROI：1,933%
- 3年NPV（折现率10%）：2.8亿美元

#### 经验教训

**成功因素**：
1. **微服务架构**：将支付、风控、路由拆分为独立服务，支持独立扩展
2. **机器学习风控**：采用实时特征工程，风险识别准确率提升40%
3. **多活部署**：三地三中心架构，故障自动切换

**挑战与应对**：
1. **数据迁移风险**：采用双写模式，逐步切流，零停机迁移
2. **跨境合规复杂**：建立本地实体，获取各国支付牌照
3. **商户集成成本**：提供SDK和沙箱环境，集成时间从2周缩短至2天

---

## 3. 案例2：支付清算结算

详见 `04_Transformation.md` 第3章。

## 4. 案例3：数字货币支付

详见 `04_Transformation.md` 第4章。

## 5. 案例4：Payment到ISO 20022转换

详见 `04_Transformation.md` 第2章。

## 6. 案例5：Payment数据存储与分析系统

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
