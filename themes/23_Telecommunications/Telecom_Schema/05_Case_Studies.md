# 电信运营Schema实践案例

## 📑 目录

- [1. 案例概述](#1-案例概述)
- [2. 企业背景](#2-企业背景)
- [3. 业务痛点与目标](#3-业务痛点与目标)
- [4. 技术挑战](#4-技术挑战)
- [5. 解决方案架构](#5-解决方案架构)
- [6. 完整实现代码](#6-完整实现代码)
- [7. 效果评估与ROI分析](#7-效果评估与roi分析)

---

## 1. 案例概述

本文档提供电信运营Schema在实际应用中的完整实践案例，涵盖客户管理、产品服务、计费账务、资源管理等核心电信运营场景。

---

## 2. 企业背景

### 2.1 企业概况

**企业名称**：中云通信集团有限公司（虚构案例企业）

**企业规模**：
- 移动用户：2.5亿
- 宽带用户：8000万
- 基站数量：300万
- 年营业额：3800亿元人民币

---

## 3. 业务痛点与目标

### 3.1 五大业务痛点

| 序号 | 痛点 | 具体表现 | 影响程度 |
|------|------|----------|----------|
| 1 | **客户流失率高** | 月流失率3%，难以挽留 | 高 |
| 2 | **计费错误多** | 投诉中计费问题占比40% | 高 |
| 3 | **产品同质化** | 与竞品差异化不明显 | 高 |
| 4 | **网络利用率低** | 峰值与谷期差异大 | 中 |
| 5 | **客服效率低** | 人工处理占比过高 | 中 |

### 3.2 五大业务目标

| 序号 | 目标 | 具体指标 | 完成期限 |
|------|------|----------|----------|
| 1 | **降低流失率** | 月流失率<1.5% | 12个月 |
| 2 | **计费准确率** | 计费准确率>99.99% | 9个月 |
| 3 | **个性化套餐** | 推荐转化率>30% | 12个月 |
| 4 | **网络优化** | 利用率提升至70% | 18个月 |
| 5 | **智能客服** | 80%问题自动处理 | 12个月 |

---

## 4. 技术挑战

1. **海量数据处理**：数亿用户的实时计费与信令处理
2. **系统高可用**：99.999%可用性要求
3. **多厂商互通**：与不同厂商设备的互联互通
4. **数据一致性**：分布式系统的数据一致性保障
5. **实时决策**：毫秒级的业务决策响应

---

## 5. 解决方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    业务支撑层 (BSS)                          │
│  CRM  订单管理  计费账务  产品管理  营销管理                   │
├─────────────────────────────────────────────────────────────┤
│                    运营支撑层 (OSS)                          │
│  资源管理  服务开通  故障管理  性能管理  网络规划              │
├─────────────────────────────────────────────────────────────┤
│                    数据层                                    │
│  客户数据  产品数据  计费数据  网络数据  大数据平台            │
├─────────────────────────────────────────────────────────────┤
│                    网络层                                    │
│  5G核心网  传输网  承载网  接入网  边缘计算                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 完整实现代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电信运营Schema实践案例
企业：中云通信集团有限公司
"""

import json
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerType(Enum):
    """客户类型"""
    INDIVIDUAL = "个人客户"
    FAMILY = "家庭客户"
    ENTERPRISE = "企业客户"


class CustomerStatus(Enum):
    """客户状态"""
    ACTIVE = "正常"
    SUSPENDED = "停机"
    TERMINATED = "销户"
    ARREARS = "欠费"


class ServiceType(Enum):
    """服务类型"""
    MOBILE = "移动业务"
    BROADBAND = "宽带业务"
    IPTV = "IPTV业务"
    CLOUD = "云服务"
    IOT = "物联网"


class BillingCycle(Enum):
    """计费周期"""
    DAILY = "按日"
    MONTHLY = "按月"
    YEARLY = "按年"


@dataclass
class Customer:
    """客户实体"""
    customer_id: str
    name: str
    customer_type: CustomerType
    phone: str
    email: str
    id_number: str = ""  # 身份证号/营业执照号
    address: str = ""
    registration_date: date = field(default_factory=date.today)
    status: CustomerStatus = CustomerStatus.ACTIVE
    credit_score: int = 100  # 信用积分
    segment: str = "普通"  # 客户分群
    
    # 统计信息
    lifetime_value: float = 0.0
    churn_risk: float = 0.0  # 流失风险 0-1
    
    def calculate_tenure_months(self) -> int:
        """计算在网时长（月）"""
        today = date.today()
        return (today.year - self.registration_date.year) * 12 + \
               (today.month - self.registration_date.month)
    
    def to_dict(self) -> Dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "customer_type": self.customer_type.value,
            "phone": self.phone,
            "email": self.email,
            "status": self.status.value,
            "tenure_months": self.calculate_tenure_months(),
            "credit_score": self.credit_score,
            "segment": self.segment,
            "churn_risk": round(self.churn_risk, 2)
        }


@dataclass
class Subscription:
    """订购关系"""
    subscription_id: str
    customer_id: str
    service_type: ServiceType
    product_code: str
    product_name: str
    msisdn: str  # 手机号码/宽带账号
    status: str = "active"  # active, suspended, terminated
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None
    monthly_fee: float = 0.0
    data_allowance: int = 0  # MB
    voice_allowance: int = 0  # 分钟
    
    def to_dict(self) -> Dict:
        return {
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "service_type": self.service_type.value,
            "product_name": self.product_name,
            "msisdn": self.msisdn,
            "status": self.status,
            "monthly_fee": self.monthly_fee,
            "data_allowance": self.data_allowance,
            "voice_allowance": self.voice_allowance
        }


@dataclass
class UsageRecord:
    """使用记录"""
    record_id: str
    subscription_id: str
    msisdn: str
    usage_type: str  # data, voice, sms
    usage_amount: float
    unit: str
    timestamp: datetime
    location: str = ""
    cost: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "msisdn": self.msisdn,
            "usage_type": self.usage_type,
            "usage_amount": self.usage_amount,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "cost": self.cost
        }


@dataclass
class Bill:
    """账单"""
    bill_id: str
    customer_id: str
    billing_period: str
    bill_date: date
    due_date: date
    
    # 费用明细
    subscription_fees: float = 0.0
    usage_fees: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    
    @property
    def total_amount(self) -> float:
        return self.subscription_fees + self.usage_fees - self.discount + self.tax
    
    @property
    def net_amount(self) -> float:
        return max(0, self.total_amount)
    
    def to_dict(self) -> Dict:
        return {
            "bill_id": self.bill_id,
            "billing_period": self.billing_period,
            "bill_date": self.bill_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "subscription_fees": self.subscription_fees,
            "usage_fees": self.usage_fees,
            "discount": self.discount,
            "tax": self.tax,
            "total_amount": round(self.total_amount, 2)
        }


@dataclass
class NetworkResource:
    """网络资源"""
    resource_id: str
    resource_type: str  # 基站、频谱、传输
    location: str
    capacity: float
    current_load: float = 0.0
    status: str = "active"
    
    @property
    def utilization(self) -> float:
        return (self.current_load / self.capacity * 100) if self.capacity > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "location": self.location,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "utilization": round(self.utilization, 2),
            "status": self.status
        }


class TelecomCRM:
    """电信CRM系统"""
    
    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.usage_records: List[UsageRecord] = []
        self.bills: Dict[str, List[Bill]] = {}
        self.network_resources: Dict[str, NetworkResource] = {}
    
    def register_customer(self, customer: Customer):
        """注册客户"""
        self.customers[customer.customer_id] = customer
        self.bills[customer.customer_id] = []
        logger.info(f"Registered customer: {customer.name}")
    
    def create_subscription(self, subscription: Subscription):
        """创建订购"""
        self.subscriptions[subscription.subscription_id] = subscription
        
        # 更新客户生命周期价值
        customer = self.customers.get(subscription.customer_id)
        if customer:
            customer.lifetime_value += subscription.monthly_fee * 12
        
        logger.info(f"Created subscription: {subscription.msisdn}")
    
    def record_usage(self, record: UsageRecord):
        """记录使用"""
        self.usage_records.append(record)
    
    def generate_bill(self, customer_id: str, billing_period: str) -> Bill:
        """生成账单"""
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        
        # 计算订购费用
        customer_subs = [s for s in self.subscriptions.values() 
                        if s.customer_id == customer_id and s.status == "active"]
        subscription_fees = sum(s.monthly_fee for s in customer_subs)
        
        # 计算使用费用
        usage_fees = sum(r.cost for r in self.usage_records 
                        if r.subscription_id in [s.subscription_id for s in customer_subs])
        
        bill = Bill(
            bill_id=f"BILL-{customer_id}-{billing_period}",
            customer_id=customer_id,
            billing_period=billing_period,
            bill_date=date.today(),
            due_date=date.today() + timedelta(days=15),
            subscription_fees=subscription_fees,
            usage_fees=usage_fees,
            tax=(subscription_fees + usage_fees) * 0.06
        )
        
        self.bills[customer_id].append(bill)
        return bill
    
    def analyze_churn_risk(self, customer_id: str) -> Dict:
        """分析流失风险"""
        customer = self.customers.get(customer_id)
        if not customer:
            return {}
        
        # 流失风险评分模型
        risk_score = 0.0
        factors = []
        
        # 1. 在网时长
        tenure = customer.calculate_tenure_months()
        if tenure < 6:
            risk_score += 0.3
            factors.append("在网时间较短")
        elif tenure > 24:
            risk_score -= 0.2
        
        # 2. 使用行为
        recent_usage = [r for r in self.usage_records 
                       if r.subscription_id in [s.subscription_id for s in self.subscriptions.values() 
                                               if s.customer_id == customer_id]]
        if len(recent_usage) < 10:  # 近期使用少
            risk_score += 0.2
            factors.append("近期使用活跃度低")
        
        # 3. 欠费历史
        if customer.status == CustomerStatus.ARREARS:
            risk_score += 0.4
            factors.append("当前欠费")
        
        # 4. 套餐价值
        subs = [s for s in self.subscriptions.values() if s.customer_id == customer_id]
        total_monthly = sum(s.monthly_fee for s in subs)
        if total_monthly < 50:
            risk_score += 0.1
        
        customer.churn_risk = min(1.0, max(0, risk_score))
        
        return {
            "customer_id": customer_id,
            "churn_risk_score": round(customer.churn_risk, 2),
            "risk_level": "高" if customer.churn_risk > 0.7 else "中" if customer.churn_risk > 0.4 else "低",
            "risk_factors": factors,
            "recommendations": self._get_retention_recommendations(customer.churn_risk)
        }
    
    def _get_retention_recommendations(self, risk_score: float) -> List[str]:
        """获取挽留建议"""
        if risk_score > 0.7:
            return ["客户经理主动关怀", "提供专属优惠", "推荐更适合的套餐"]
        elif risk_score > 0.4:
            return ["发送关怀短信", "推送优惠活动"]
        return ["保持正常服务"]
    
    def recommend_products(self, customer_id: str) -> List[Dict]:
        """推荐产品"""
        customer = self.customers.get(customer_id)
        if not customer:
            return []
        
        recommendations = []
        
        # 基于使用行为的推荐
        data_usage = sum(r.usage_amount for r in self.usage_records 
                        if r.subscription_id in [s.subscription_id for s in self.subscriptions.values() 
                                                if s.customer_id == customer_id]
                        and r.usage_type == "data")
        
        if data_usage > 10000:  # 使用超过10GB
            recommendations.append({
                "product_code": "DATA-UNLIMITED",
                "product_name": "无限流量包",
                "reason": "您的流量使用较多，升级无限流量更划算",
                "monthly_fee": 99,
                "potential_savings": 30
            })
        
        # 基于客户类型的推荐
        if customer.customer_type == CustomerType.FAMILY:
            recommendations.append({
                "product_code": "FAMILY-PLAN",
                "product_name": "家庭共享套餐",
                "reason": "多人共享更优惠",
                "monthly_fee": 199,
                "potential_savings": 50
            })
        
        return recommendations
    
    def get_network_status(self) -> Dict:
        """获取网络状态"""
        total_capacity = sum(r.capacity for r in self.network_resources.values())
        total_load = sum(r.current_load for r in self.network_resources.values())
        
        return {
            "total_resources": len(self.network_resources),
            "total_capacity": total_capacity,
            "total_load": round(total_load, 2),
            "overall_utilization": round(total_load / total_capacity * 100, 2) if total_capacity else 0,
            "active_alarms": sum(1 for r in self.network_resources.values() if r.status != "active"),
            "resource_breakdown": self._get_resource_breakdown()
        }
    
    def _get_resource_breakdown(self) -> Dict:
        """资源分类统计"""
        breakdown = {}
        for resource in self.network_resources.values():
            if resource.resource_type not in breakdown:
                breakdown[resource.resource_type] = {"count": 0, "total_capacity": 0}
            breakdown[resource.resource_type]["count"] += 1
            breakdown[resource.resource_type]["total_capacity"] += resource.capacity
        return breakdown


def create_demo_telecom():
    """创建演示电信系统"""
    crm = TelecomCRM()
    
    # 创建客户
    customers = [
        Customer("C001", "张三", CustomerType.INDIVIDUAL, "13800138001", "zhangsan@example.com"),
        Customer("C002", "李四", CustomerType.FAMILY, "13800138002", "lisi@example.com"),
        Customer("C003", "王五", CustomerType.ENTERPRISE, "13800138003", "wangwu@example.com"),
    ]
    
    for customer in customers:
        crm.register_customer(customer)
    
    # 创建订购
    subscriptions = [
        Subscription("S001", "C001", ServiceType.MOBILE, "4G-59", "4G畅享套餐", "13800138001", 
                    monthly_fee=59, data_allowance=10240, voice_allowance=300),
        Subscription("S002", "C002", ServiceType.BROADBAND, "BB-100", "100M宽带", "02112345678",
                    monthly_fee=88, data_allowance=0, voice_allowance=0),
        Subscription("S003", "C002", ServiceType.MOBILE, "5G-129", "5G畅享套餐", "13800138002",
                    monthly_fee=129, data_allowance=51200, voice_allowance=500),
    ]
    
    for sub in subscriptions:
        crm.create_subscription(sub)
    
    # 模拟使用记录
    for _ in range(100):
        record = UsageRecord(
            record_id=str(uuid.uuid4()),
            subscription_id=random.choice(["S001", "S002", "S003"]),
            msisdn="13800138001",
            usage_type=random.choice(["data", "voice", "sms"]),
            usage_amount=random.uniform(10, 500),
            unit=random.choice(["MB", "分钟", "条"]),
            timestamp=datetime.now() - timedelta(hours=random.randint(0, 720)),
            cost=random.uniform(0, 20)
        )
        crm.record_usage(record)
    
    # 创建网络资源
    resources = [
        NetworkResource("BS-001", "基站", "南京市区", 1000, 650),
        NetworkResource("BS-002", "基站", "南京郊区", 800, 320),
        NetworkResource("TR-001", "传输", "南京-上海", 10000, 7200),
    ]
    
    for resource in resources:
        crm.network_resources[resource.resource_id] = resource
    
    return crm


def main():
    """主函数"""
    print("=" * 80)
    print("电信运营Schema实践案例 - 中云通信")
    print("=" * 80)
    
    # 创建系统
    print("\n【步骤1】初始化电信系统...")
    crm = create_demo_telecom()
    print(f"  注册客户: {len(crm.customers)} 人")
    print(f"  订购关系: {len(crm.subscriptions)} 个")
    
    # 流失风险分析
    print("\n【步骤2】客户流失风险分析...")
    for customer_id in ["C001", "C002"]:
        risk_analysis = crm.analyze_churn_risk(customer_id)
        print(f"\n  客户: {customer_id}")
        print(f"    流失风险: {risk_analysis['churn_risk_score']}")
        print(f"    风险等级: {risk_analysis['risk_level']}")
        print(f"    建议: {risk_analysis['recommendations'][0] if risk_analysis['recommendations'] else 'N/A'}")
    
    # 产品推荐
    print("\n【步骤3】个性化产品推荐...")
    for customer_id in ["C001", "C002"]:
        recommendations = crm.recommend_products(customer_id)
        customer = crm.customers[customer_id]
        print(f"\n  {customer.name}:")
        for rec in recommendations:
            print(f"    - {rec['product_name']}: {rec['reason']}")
    
    # 生成账单
    print("\n【步骤4】生成账单...")
    bill = crm.generate_bill("C001", "2025-06")
    print(f"  账单周期: {bill.billing_period}")
    print(f"  订购费: ¥{bill.subscription_fees}")
    print(f"  使用费: ¥{bill.usage_fees}")
    print(f"  应缴金额: ¥{bill.net_amount}")
    
    # 网络状态
    print("\n【步骤5】网络资源状态...")
    network_status = crm.get_network_status()
    print(f"  资源总数: {network_status['total_resources']}")
    print(f"  整体利用率: {network_status['overall_utilization']}%")
    print(f"  活跃告警: {network_status['active_alarms']}")
    
    print("\n" + "=" * 80)
    print("电信运营Schema实践案例执行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
```

---

## 7. 效果评估与ROI分析

### 7.1 关键绩效指标

| 指标 | 实施前 | 实施后 | 改善 |
|------|--------|--------|------|
| 月流失率 | 3.0% | 1.4% | -53% |
| 计费准确率 | 99.5% | 99.995% | +0.5% |
| 推荐转化率 | 5% | 35% | +600% |
| 网络利用率 | 45% | 72% | +60% |
| 客服效率 | 60% | 85% | +42% |

### 7.2 ROI分析

**投资**：¥2000万  
**年收益**：¥5000万  
**ROI**：150%（3年）

---

**创建时间**：2026-02-15  
**版本**：1.0.0
