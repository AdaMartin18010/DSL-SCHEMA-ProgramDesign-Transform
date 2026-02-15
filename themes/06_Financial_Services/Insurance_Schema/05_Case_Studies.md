# 保险业务Schema实践案例

## 📑 目录

- [保险业务Schema实践案例](#保险业务schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：大型保险公司核心系统升级](#2-案例1大型保险公司核心系统升级)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 代码实现](#26-代码实现)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：互联网保险智能核保系统](#3-案例2互联网保险智能核保系统)
    - [3.1 企业背景](#31-企业背景)
    - [3.2 业务痛点](#32-业务痛点)
    - [3.3 业务目标](#33-业务目标)
    - [3.4 技术挑战](#34-技术挑战)
    - [3.5 Schema定义](#35-schema定义)
    - [3.6 代码实现](#36-代码实现)
    - [3.7 效果评估](#37-效果评估)
  - [4. 案例3：保险理赔智能反欺诈平台](#4-案例3保险理赔智能反欺诈平台)
    - [4.1 企业背景](#41-企业背景)
    - [4.2 业务痛点](#42-业务痛点)
    - [4.3 业务目标](#43-业务目标)
    - [4.4 技术挑战](#44-技术挑战)
    - [4.5 Schema定义](#45-schema定义)
    - [4.6 代码实现](#46-代码实现)
    - [4.7 效果评估](#47-效果评估)

---

## 1. 案例概述

本文档提供保险业务Schema在实际应用中的三个典型案例，涵盖大型保险公司核心系统升级、互联网保险智能核保系统、保险理赔智能反欺诈平台等场景，展示DSL Schema在保险产品管理、智能核保、理赔风控等领域的实际应用价值。

---

## 2. 案例1：大型保险公司核心系统升级

### 2.1 企业背景

**企业名称**：中国人寿XX分公司（化名：华安保险集团）  
**企业规模**：总资产规模超过1.2万亿元，年度保费收入超过3,000亿元，服务客户超过1.5亿人，拥有各级分支机构3,000余家  
**业务范围**：涵盖人寿保险、健康保险、意外伤害保险、养老保险、资产管理等全牌照保险业务  
**系统现状**：核心系统建于2005年，采用AS/400小型机架构，使用RPG语言开发，产品参数化程度低，新产品开发周期长达6-8个月

华安保险集团作为国内领先的综合性保险集团，其传统核心系统已无法支撑业务快速发展。随着互联网保险、场景化保险、定制化保险等新业态兴起，系统僵化、产品创新能力弱、客户体验差等问题日益凸显，急需进行核心系统架构升级。

### 2.2 业务痛点

| 序号 | 痛点领域 | 具体问题描述 | 业务影响 |
|------|----------|--------------|----------|
| 1 | **产品创新慢** | 新产品上线周期6-8个月，需修改大量代码和进行多轮测试，无法快速响应市场需求 | 错失互联网保险红利，市场份额下滑 |
| 2 | **渠道割裂** | 个险、团险、银保、电销、网销等渠道数据独立，客户信息不互通，同一客户在不同渠道被视为不同客户 | 交叉销售困难，客户体验差 |
| 3 | **保单管理复杂** | 传统保单采用固定格式，难以支持万能险、投连险等复杂产品的灵活账户管理 | 复杂产品运营成本高，差错率高 |
| 4 | **精算定价滞后** | 精算数据分散，分析周期长，无法基于实时数据进行动态定价 | 定价精准度低，承保利润波动大 |
| 5 | **合规压力大** | 监管报送需要手工整合多个系统数据，报送质量差，合规风险高 | 监管检查问题多，整改成本高 |

### 2.3 业务目标

| 序号 | 目标维度 | 具体目标 | 预期指标 |
|------|----------|----------|----------|
| 1 | **产品创新** | 建立产品工厂，实现保险产品参数化配置和快速组装 | 新产品上线周期缩短至2周 |
| 2 | **客户统一** | 建立统一客户视图，实现全渠道客户信息共享 | 客户识别准确率>99.5% |
| 3 | **灵活账户** | 支持万能险、投连险等复杂产品的灵活账户管理 | 账户处理效率提升10倍 |
| 4 | **智能定价** | 建立基于大数据的精准定价模型，支持动态费率调整 | 定价精准度提升30% |
| 5 | **监管合规** | 实现监管数据自动采集、校验和报送 | 监管报送自动化率>95% |

### 2.4 技术挑战

| 挑战编号 | 挑战领域 | 具体描述 | 解决方案 |
|----------|----------|----------|----------|
| 1 | **产品模型抽象** | 保险产品结构复杂（条款、费率、责任、特约），不同险种差异大，需建立统一的产品元模型 | 基于Schema定义保险产品DSL，支持责任组合、条件费率、多维度特约 |
| 2 | **精算数据安全** | 精算数据涉及商业机密和客户隐私，需严格管控访问权限，同时支持复杂分析 | Schema标记数据敏感度，RBAC+ABAC混合权限模型，数据脱敏展示 |
| 3 | **历史数据迁移** | 20年历史保单数据超过50TB，数据格式不统一，需保证迁移过程保单权益无损 | 双轨并行架构，Schema映射转换，迁移过程权益试算校验 |
| 4 | **高并发处理** | 开门红等业务高峰期日保单量超过100万单，需支持高并发投保和保全处理 | 微服务架构+读写分离，核心投保链路异步化，Redis缓存热点数据 |
| 5 | **多渠道协同** | 代理人APP、官网、微信公众号、银保通等多渠道同时接入，需保证数据一致性 | 基于Schema的API网关，统一接入标准，分布式事务Saga模式 |

### 2.5 Schema定义

**保险产品配置Schema**：

```dsl
schema InsuranceProduct {
  // 产品基础信息
  product_basic: ProductBasicInfo {
    product_code: String @value("P2025L00001") @primary_key
    product_name: String @value("华安康宁终身重大疾病保险")
    product_type: Enum @value("LIFE_HEALTH")  // 健康险
    product_category: Enum @value("CRITICAL_ILLNESS")  // 重疾险
    insurance_type: Enum @value("TERM_LIFE")  // 定期寿险
    sale_status: Enum @value("ON_SALE")
    
    // 监管机构备案信息
    regulatory_info: RegulatoryInfo {
      approval_number: String @value("P0001-2025-A001")
      approval_date: Date @value("2025-01-01")
      regulatory_category: String @value("人身险"
      filing_company: String @value("华安保险集团")
    }
  }

  // 投保规则
  underwriting_rules: UnderwritingRules {
    // 投保年龄限制
    age_limit: AgeLimit {
      min_age_days: Int @value(28)  // 最小28天
      max_age_years: Int @value(60)  // 最大60岁
    }
    
    // 保额限制
    sum_assured_limit: SumAssuredLimit {
      min_amount: Decimal @value(100000.00)
      max_amount: Decimal @value(5000000.00)
      amount_step: Decimal @value(10000.00)
    }
    
    // 缴费规则
    payment_rules: PaymentRules {
      payment_methods: List[Enum] @value(["LUMP_SUM", "ANNUAL", "MONTHLY"])
      payment_periods: List[Int] @value([1, 5, 10, 15, 20, 30])
      grace_period_days: Int @value(60)
      reinstatement_period_years: Int @value(2)
    }
    
    // 职业限制
    occupation_limit: OccupationLimit {
      allowed_categories: List[Int] @value([1, 2, 3, 4])  // 1-4类职业
      excluded_occupations: List[String] @value(["高空作业", "潜水员"])
    }
    
    // 健康告知
    health_declaration: HealthDeclaration {
      required: Boolean @value(true)
      questions: List[Question] {
        q1: Question {
          question_id: String @value("HD001")
          question_text: String @value("是否曾被诊断或治疗过以下疾病：恶性肿瘤...")
          answer_type: Enum @value("YES_NO")
          follow_up_action: String @value("MANUAL_REVIEW")
        }
      }
    }
  }

  // 保险责任
  coverage_liabilities: List[CoverageLiability] {
    // 重大疾病保险金
    liability1: CoverageLiability {
      liability_code: String @value("LIAB_001")
      liability_name: String @value("重大疾病保险金")
      liability_type: Enum @value("BASIC")
      payment_type: Enum @value("LUMP_SUM")
      
      // 责任计算
      calculation: CalculationRule {
        basis: Enum @value("SUM_ASSURED")
        multiplier: Decimal @value(1.0)
        min_amount: Decimal @value(100000.00)
        max_amount: Decimal @value(5000000.00)
      }
      
      // 覆盖病种
      covered_diseases: CoveredDiseases {
        total_count: Int @value(120)
        critical_illnesses: List[String] @value(["恶性肿瘤", "急性心肌梗塞", "脑中风后遗症"])
        disease_grouping: Boolean @value(true)
        group_count: Int @value(6)
        max_claims_per_group: Int @value(1)
      }
      
      // 等待期
      waiting_period: WaitingPeriod {
        days: Int @value(180)
        exception: String @value("意外伤害无等待期")
      }
    }
    
    // 轻症疾病保险金
    liability2: CoverageLiability {
      liability_code: String @value("LIAB_002")
      liability_name: String @value("轻症疾病保险金")
      liability_type: Enum @value("ADDITIONAL")
      
      calculation: CalculationRule {
        basis: Enum @value("SUM_ASSURED")
        multiplier: Decimal @value(0.3)
        max_claims: Int @value(3)
      }
      
      covered_diseases: CoveredDiseases {
        total_count: Int @value(40)
        waiting_period: WaitingPeriod {
          days: Int @value(90)
        }
      }
    }
    
    // 身故保险金
    liability3: CoverageLiability {
      liability_code: String @value("LIAB_003")
      liability_name: String @value("身故保险金")
      liability_type: Enum @value("BASIC")
      
      calculation: CalculationRule {
        basis: Enum @value("MAX")
        options: List[String] @value(["SUM_ASSURED", "PAID_PREMIUM", "CASH_VALUE"])
      }
    }
  }

  // 费率表
  premium_rates: PremiumRateTable {
    rate_type: Enum @value("AGE_GENDER_SMOKING")
    currency: String @value("CNY")
    unit: Decimal @value(1000.00)  // 每千元保额费率
    
    // 费率分档
    rate_tiers: List[RateTier] {
      tier1: RateTier {
        age_range: Range @value([0, 30])
        gender: Enum @value("MALE")
        smoking_status: Enum @value("NON_SMOKER")
        rate_per_thousand: Decimal @value(2.5)
      }
      tier2: RateTier {
        age_range: Range @value([0, 30])
        gender: Enum @value("FEMALE")
        smoking_status: Enum @value("NON_SMOKER")
        rate_per_thousand: Decimal @value(2.2)
      }
    }
    
    // 优惠规则
    discount_rules: List[DiscountRule] {
      rule1: DiscountRule {
        rule_code: String @value("DISC_001")
        condition: String @value("payment_method == 'LUMP_SUM'")
        discount_rate: Decimal @value(0.95)
        description: String @value("趸交优惠5%")
      }
    }
  }

  // 现金价值表
  cash_value_table: CashValueTable {
    calculation_method: Enum @value("PROSPECTIVE")
    surrender_charge_period: Int @value(5)
    
    // 退保费用率
    surrender_charges: List[SurrenderCharge] {
      year1: SurrenderCharge {
        policy_year: Int @value(1)
        charge_rate: Decimal @value(0.05)
      }
      year2: SurrenderCharge {
        policy_year: Int @value(2)
        charge_rate: Decimal @value(0.03)
      }
      year3: SurrenderCharge {
        policy_year: Int @value(3)
        charge_rate: Decimal @value(0.01)
      }
    }
  }

  // 特别约定
  special_clauses: List[SpecialClause] {
    clause1: SpecialClause {
      clause_code: String @value("SC001")
      clause_type: Enum @value("EXCLUSION")
      clause_text: String @value("遗传性疾病、先天性畸形不在保障范围")
      effective_date: Date @value("2025-01-01")
    }
  }

  // 版本管理
  version_info: VersionInfo {
    version: String @value("1.0.0")
    effective_date: Date @value("2025-01-01")
    expiry_date: Optional[Date]
    created_by: String @value("产品管理部")
    approved_by: String @value("总精算师")
    approval_date: Date @value("2024-12-15")
  }
} @standard("CIRC 人身险产品条款格式") @regulatory_filing_required(true)
```

---

### 2.6 代码实现

**保险产品工厂与保单管理系统完整实现**：

```python
"""
保险产品工厂与保单管理系统 - 基于DSL Schema驱动架构
支持产品参数化配置、智能核保、灵活账户管理
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from functools import lru_cache
import uuid

import redis.asyncio as redis
import asyncpg
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InsuranceCoreSystem")


class ProductType(Enum):
    """产品类型"""
    LIFE_HEALTH = "健康险"
    LIFE_ENDOWMENT = "两全险"
    LIFE_ANNUITY = "年金险"
    LIFE_WHOLE = "终身寿险"
    LIFE_TERM = "定期寿险"
    ACCIDENT = "意外险"


class LiabilityType(Enum):
    """责任类型"""
    BASIC = "基本责任"
    ADDITIONAL = "附加责任"
    RIDER = "附加险"


class PaymentType(Enum):
    """给付类型"""
    LUMP_SUM = "一次性给付"
    ANNUITY = "年金给付"
    REIMBURSEMENT = "报销"


class PolicyStatus(Enum):
    """保单状态"""
    PENDING = "待生效"
    INFORCE = "有效"
    LAPSED = "失效"
    SURRENDERED = "退保"
    MATURED = "满期"
    CLAIMED = "已理赔"


@dataclass
class AgeLimit:
    """年龄限制"""
    min_age_days: int
    max_age_years: int


@dataclass
class SumAssuredLimit:
    """保额限制"""
    min_amount: Decimal
    max_amount: Decimal
    amount_step: Decimal


@dataclass
class CalculationRule:
    """计算规则"""
    basis: str
    multiplier: Decimal = Decimal('1.0')
    min_amount: Decimal = Decimal('0')
    max_amount: Decimal = Decimal('999999999')
    options: List[str] = field(default_factory=list)


@dataclass
class CoverageLiability:
    """保险责任"""
    liability_code: str
    liability_name: str
    liability_type: LiabilityType
    payment_type: PaymentType
    calculation: CalculationRule
    waiting_period_days: int = 0
    max_claims: int = 1


@dataclass
class RateTier:
    """费率分档"""
    age_range: tuple
    gender: str
    smoking_status: str
    rate_per_thousand: Decimal


@dataclass
class InsuranceProduct:
    """保险产品实体"""
    product_code: str
    product_name: str
    product_type: ProductType
    sale_status: str
    approval_number: str
    
    # 投保规则
    age_limit: AgeLimit
    sum_assured_limit: SumAssuredLimit
    payment_methods: List[str]
    payment_periods: List[int]
    grace_period_days: int
    
    # 责任和费率
    liabilities: List[CoverageLiability]
    rate_tiers: List[RateTier]
    currency: str = "CNY"
    
    # 版本
    version: str = "1.0.0"
    effective_date: datetime = field(default_factory=datetime.now)


@dataclass
class Insured:
    """被保险人"""
    name: str
    gender: str
    birth_date: datetime
    id_type: str
    id_number: str
    occupation_code: str
    occupation_name: str
    smoking_status: str = "NON_SMOKER"
    height_cm: int = 0
    weight_kg: int = 0
    health_declaration: Dict = field(default_factory=dict)


@dataclass
class Policy:
    """保单实体"""
    policy_number: str
    product_code: str
    policy_status: PolicyStatus
    
    # 投保人信息
    applicant_name: str
    applicant_id_number: str
    applicant_phone: str
    
    # 被保险人
    insured: Insured
    
    // 保单要素
    sum_assured: Decimal
    premium: Decimal
    payment_method: str
    payment_period: int
    coverage_period: int
    
    // 日期
    application_date: datetime
    effective_date: datetime
    first_premium_date: datetime
    next_premium_due_date: datetime
    maturity_date: datetime
    
    // 账户信息（万能险/投连险）
    account_value: Decimal = Decimal('0')
    accumulated_premium: Decimal = Decimal('0')
    
    // 状态
    total_premiums_paid: Decimal = Decimal('0')
    lapse_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ProductFactory:
    """产品工厂 - 基于Schema的产品配置管理"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.products: Dict[str, InsuranceProduct] = {}
    
    async def initialize(self):
        """初始化产品工厂"""
        self.redis_client = redis.Redis(
            host='localhost', port=6379, db=1, decode_responses=True
        )
        await self._load_products()
        logger.info("产品工厂初始化完成")
    
    async def _load_products(self):
        """加载产品配置"""
        # 模拟加载产品
        product_data = {
            "product_code": "P2025L00001",
            "product_name": "华安康宁终身重大疾病保险",
            "product_type": "LIFE_HEALTH",
            "sale_status": "ON_SALE",
            "approval_number": "P0001-2025-A001",
            "age_limit": {"min_age_days": 28, "max_age_years": 60},
            "sum_assured_limit": {"min_amount": 100000, "max_amount": 5000000, "amount_step": 10000},
            "payment_methods": ["LUMP_SUM", "ANNUAL", "MONTHLY"],
            "payment_periods": [1, 5, 10, 15, 20, 30],
            "grace_period_days": 60,
            "liabilities": [
                {
                    "liability_code": "LIAB_001",
                    "liability_name": "重大疾病保险金",
                    "liability_type": "BASIC",
                    "payment_type": "LUMP_SUM",
                    "calculation": {"basis": "SUM_ASSURED", "multiplier": 1.0},
                    "waiting_period_days": 180,
                    "max_claims": 1
                },
                {
                    "liability_code": "LIAB_002",
                    "liability_name": "轻症疾病保险金",
                    "liability_type": "ADDITIONAL",
                    "payment_type": "LUMP_SUM",
                    "calculation": {"basis": "SUM_ASSURED", "multiplier": 0.3},
                    "waiting_period_days": 90,
                    "max_claims": 3
                }
            ],
            "rate_tiers": [
                {"age_range": [0, 30], "gender": "MALE", "smoking_status": "NON_SMOKER", "rate_per_thousand": 2.5},
                {"age_range": [0, 30], "gender": "FEMALE", "smoking_status": "NON_SMOKER", "rate_per_thousand": 2.2},
                {"age_range": [31, 40], "gender": "MALE", "smoking_status": "NON_SMOKER", "rate_per_thousand": 4.2},
                {"age_range": [31, 40], "gender": "FEMALE", "smoking_status": "NON_SMOKER", "rate_per_thousand": 3.8},
                {"age_range": [41, 50], "gender": "MALE", "smoking_status": "NON_SMOKER", "rate_per_thousand": 8.5},
                {"age_range": [41, 50], "gender": "FEMALE", "smoking_status": "NON_SMOKER", "rate_per_thousand": 7.2}
            ]
        }
        
        product = self._parse_product(product_data)
        self.products[product.product_code] = product
    
    def _parse_product(self, data: Dict) -> InsuranceProduct:
        """解析产品数据"""
        liabilities = []
        for liab_data in data.get("liabilities", []):
            liabilities.append(CoverageLiability(
                liability_code=liab_data["liability_code"],
                liability_name=liab_data["liability_name"],
                liability_type=LiabilityType(liab_data["liability_type"]),
                payment_type=PaymentType(liab_data["payment_type"]),
                calculation=CalculationRule(**liab_data["calculation"]),
                waiting_period_days=liab_data.get("waiting_period_days", 0),
                max_claims=liab_data.get("max_claims", 1)
            ))
        
        rate_tiers = []
        for tier_data in data.get("rate_tiers", []):
            rate_tiers.append(RateTier(
                age_range=tuple(tier_data["age_range"]),
                gender=tier_data["gender"],
                smoking_status=tier_data["smoking_status"],
                rate_per_thousand=Decimal(str(tier_data["rate_per_thousand"]))
            ))
        
        return InsuranceProduct(
            product_code=data["product_code"],
            product_name=data["product_name"],
            product_type=ProductType(data["product_type"]),
            sale_status=data["sale_status"],
            approval_number=data["approval_number"],
            age_limit=AgeLimit(**data["age_limit"]),
            sum_assured_limit=SumAssuredLimit(
                min_amount=Decimal(str(data["sum_assured_limit"]["min_amount"])),
                max_amount=Decimal(str(data["sum_assured_limit"]["max_amount"])),
                amount_step=Decimal(str(data["sum_assured_limit"]["amount_step"]))
            ),
            payment_methods=data["payment_methods"],
            payment_periods=data["payment_periods"],
            grace_period_days=data["grace_period_days"],
            liabilities=liabilities,
            rate_tiers=rate_tiers
        )
    
    def get_product(self, product_code: str) -> Optional[InsuranceProduct]:
        """获取产品"""
        return self.products.get(product_code)
    
    def calculate_premium(self, product_code: str, 
                         sum_assured: Decimal,
                         insured_age: int,
                         insured_gender: str,
                         smoking_status: str,
                         payment_method: str,
                         payment_period: int) -> Dict:
        """计算保费"""
        product = self.get_product(product_code)
        if not product:
            return {"error": "产品不存在"}
        
        # 查找费率
        rate = self._find_rate(product, insured_age, insured_gender, smoking_status)
        if not rate:
            return {"error": "未找到匹配费率"}
        
        # 计算年缴保费
        annual_premium = sum_assured / Decimal('1000') * rate.rate_per_thousand
        
        # 根据缴费方式调整
        if payment_method == "LUMP_SUM":
            # 趸交，计算现值
            premium = annual_premium * Decimal(str(payment_period)) * Decimal('0.95')
        elif payment_method == "ANNUAL":
            premium = annual_premium
        elif payment_method == "MONTHLY":
            premium = annual_premium / Decimal('12') * Decimal('1.05')
        else:
            premium = annual_premium
        
        return {
            "product_code": product_code,
            "sum_assured": float(sum_assured),
            "annual_premium": float(annual_premium),
            "premium": float(premium.quantize(Decimal('0.01'))),
            "payment_method": payment_method,
            "payment_period": payment_period,
            "rate_per_thousand": float(rate.rate_per_thousand)
        }
    
    def _find_rate(self, product: InsuranceProduct, age: int, gender: str, smoking: str) -> Optional[RateTier]:
        """查找匹配费率"""
        for tier in product.rate_tiers:
            if (tier.age_range[0] <= age <= tier.age_range[1] and
                tier.gender == gender and
                tier.smoking_status == smoking):
                return tier
        return None
    
    def validate_application(self, product_code: str, application: Dict) -> List[Dict]:
        """校验投保申请"""
        product = self.get_product(product_code)
        if not product:
            return [{"field": "product", "error": "产品不存在"}]
        
        errors = []
        
        # 校验年龄
        age = application.get("insured_age", 0)
        if age < product.age_limit.min_age_days / 365:
            errors.append({"field": "age", "error": f"年龄低于最低要求{product.age_limit.min_age_days}天"})
        if age > product.age_limit.max_age_years:
            errors.append({"field": "age", "error": f"年龄超过最高限制{product.age_limit.max_age_years}岁"})
        
        # 校验保额
        sum_assured = Decimal(str(application.get("sum_assured", 0)))
        if sum_assured < product.sum_assured_limit.min_amount:
            errors.append({"field": "sum_assured", "error": f"保额低于最低要求{product.sum_assured_limit.min_amount}"})
        if sum_assured > product.sum_assured_limit.max_amount:
            errors.append({"field": "sum_assured", "error": f"保额超过最高限制{product.sum_assured_limit.max_amount}"})
        
        # 校验缴费方式
        payment_method = application.get("payment_method")
        if payment_method not in product.payment_methods:
            errors.append({"field": "payment_method", "error": f"不支持的缴费方式: {payment_method}"})
        
        # 校验缴费期间
        payment_period = application.get("payment_period", 0)
        if payment_period not in product.payment_periods:
            errors.append({"field": "payment_period", "error": f"不支持的缴费期间: {payment_period}"})
        
        return errors


class UnderwritingEngine:
    """智能核保引擎"""
    
    def __init__(self):
        self.rules = self._load_underwriting_rules()
    
    def _load_underwriting_rules(self) -> List[Dict]:
        """加载核保规则"""
        return [
            {
                "rule_id": "UW_001",
                "name": "年龄超限",
                "condition": lambda app: app.get("insured_age", 0) > 55,
                "decision": "DECLINE",
                "priority": 100
            },
            {
                "rule_id": "UW_002",
                "name": "BMI超标",
                "condition": lambda app: self._calc_bmi(app) > 32,
                "decision": "RATED_UP",
                "loading": 1.25,
                "priority": 80
            },
            {
                "rule_id": "UW_003",
                "name": "高危职业",
                "condition": lambda app: app.get("occupation_category", 1) > 4,
                "decision": "DECLINE",
                "priority": 100
            },
            {
                "rule_id": "UW_004",
                "name": "健康告知异常",
                "condition": lambda app: any(app.get("health_declaration", {}).values()),
                "decision": "MANUAL_REVIEW",
                "priority": 90
            },
            {
                "rule_id": "UW_005",
                "name": "保额过高",
                "condition": lambda app: Decimal(str(app.get("sum_assured", 0))) > Decimal('2000000'),
                "decision": "FINANCIAL_UNDERWRITING",
                "priority": 70
            }
        ]
    
    def _calc_bmi(self, application: Dict) -> float:
        """计算BMI"""
        height_m = application.get("height_cm", 170) / 100
        weight_kg = application.get("weight_kg", 65)
        if height_m > 0:
            return weight_kg / (height_m ** 2)
        return 0
    
    async def underwrite(self, application: Dict) -> Dict:
        """执行核保"""
        decisions = []
        final_decision = "ACCEPT"
        loading = Decimal('1.0')
        
        for rule in sorted(self.rules, key=lambda r: r["priority"], reverse=True):
            try:
                if rule["condition"](application):
                    decisions.append({
                        "rule_id": rule["rule_id"],
                        "rule_name": rule["name"],
                        "decision": rule["decision"]
                    })
                    
                    # 更新最终决策
                    if rule["decision"] == "DECLINE":
                        final_decision = "DECLINE"
                        break
                    elif rule["decision"] == "MANUAL_REVIEW":
                        final_decision = "MANUAL_REVIEW"
                    elif rule["decision"] == "RATED_UP":
                        if final_decision not in ["DECLINE", "MANUAL_REVIEW"]:
                            final_decision = "RATED_UP"
                            loading *= Decimal(str(rule.get("loading", 1.0)))
            except Exception as e:
                logger.error(f"核保规则 {rule['rule_id']} 执行失败: {e}")
        
        return {
            "decision": final_decision,
            "decision_desc": {
                "ACCEPT": "标准体承保",
                "RATED_UP": "加费承保",
                "EXCLUSION": "除外承保",
                "MANUAL_REVIEW": "人工核保",
                "DECLINE": "拒保"
            }.get(final_decision, final_decision),
            "loading": float(loading),
            "triggered_rules": decisions,
            "underwriting_time": datetime.now().isoformat()
        }


class PolicyManagementSystem:
    """保单管理系统"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.product_factory = ProductFactory()
        self.underwriting_engine = UnderwritingEngine()
    
    async def initialize(self):
        """初始化系统"""
        self.redis_client = redis.Redis(
            host='localhost', port=6379, db=1, decode_responses=True
        )
        self.db_pool = await asyncpg.create_pool(
            host='localhost', port=5432,
            user='admin', password='admin',
            database='insurance_core'
        )
        await self.product_factory.initialize()
        logger.info("保单管理系统初始化完成")
    
    async def submit_application(self, application: Dict) -> Dict:
        """提交投保申请"""
        try:
            product_code = application.get("product_code")
            
            # 1. 产品校验
            errors = self.product_factory.validate_application(product_code, application)
            if errors:
                return {
                    "code": "VALIDATION_ERROR",
                    "message": "投保申请校验失败",
                    "errors": errors
                }
            
            # 2. 智能核保
            uw_result = await self.underwriting_engine.underwrite(application)
            
            if uw_result["decision"] == "DECLINE":
                return {
                    "code": "UNDERWRITING_DECLINE",
                    "message": "未通过核保",
                    "underwriting_result": uw_result
                }
            
            # 3. 计算保费
            premium_result = self.product_factory.calculate_premium(
                product_code=product_code,
                sum_assured=Decimal(str(application.get("sum_assured", 0))),
                insured_age=application.get("insured_age", 30),
                insured_gender=application.get("insured_gender", "MALE"),
                smoking_status=application.get("smoking_status", "NON_SMOKER"),
                payment_method=application.get("payment_method", "ANNUAL"),
                payment_period=application.get("payment_period", 20)
            )
            
            # 4. 应用加费系数
            if uw_result["decision"] == "RATED_UP":
                premium_result["premium"] *= uw_result["loading"]
                premium_result["premium"] = round(premium_result["premium"], 2)
            
            # 5. 生成投保单号
            application_no = f"APP{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
            
            # 6. 存储投保申请
            await self._store_application(application_no, application, uw_result, premium_result)
            
            return {
                "code": "SUCCESS",
                "message": "投保申请提交成功",
                "data": {
                    "application_no": application_no,
                    "underwriting_result": uw_result,
                    "premium": premium_result,
                    "next_steps": ["支付首期保费"] if uw_result["decision"] == "ACCEPT" else ["等待人工核保"]
                }
            }
            
        except Exception as e:
            logger.error(f"投保申请提交失败: {e}")
            return {"code": "SYSTEM_ERROR", "message": f"系统异常: {str(e)}"}
    
    async def issue_policy(self, application_no: str, payment_confirmation: Dict) -> Dict:
        """承保出单"""
        try:
            # 1. 查询投保申请
            application = await self._get_application(application_no)
            if not application:
                return {"code": "NOT_FOUND", "message": "投保申请不存在"}
            
            # 2. 校验支付
            if not await self._verify_payment(payment_confirmation):
                return {"code": "PAYMENT_FAILED", "message": "支付校验失败"}
            
            # 3. 生成保单号
            policy_number = f"POL{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
            
            # 4. 创建保单
            policy = await self._create_policy(policy_number, application)
            
            # 5. 存储保单
            await self._store_policy(policy)
            
            # 6. 发送电子保单
            await self._send_e_policy(policy)
            
            return {
                "code": "SUCCESS",
                "message": "保单承保成功",
                "data": {
                    "policy_number": policy_number,
                    "effective_date": policy.effective_date.isoformat(),
                    "first_premium_date": policy.first_premium_date.isoformat(),
                    "next_premium_due_date": policy.next_premium_due_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"承保出单失败: {e}")
            return {"code": "SYSTEM_ERROR", "message": f"系统异常: {str(e)}"}
    
    async def _store_application(self, application_no: str, application: Dict, 
                                 uw_result: Dict, premium: Dict):
        """存储投保申请"""
        key = f"application:{application_no}"
        data = {
            "application_no": application_no,
            "application_data": application,
            "underwriting_result": uw_result,
            "premium": premium,
            "status": "PENDING_PAYMENT",
            "created_at": datetime.now().isoformat()
        }
        await self.redis_client.setex(key, 86400, json.dumps(data))
    
    async def _get_application(self, application_no: str) -> Optional[Dict]:
        """查询投保申请"""
        key = f"application:{application_no}"
        data = await self.redis_client.get(key)
        return json.loads(data) if data else None
    
    async def _verify_payment(self, confirmation: Dict) -> bool:
        """校验支付"""
        # 模拟支付校验
        return confirmation.get("status") == "SUCCESS"
    
    async def _create_policy(self, policy_number: str, application: Dict) -> Policy:
        """创建保单"""
        app_data = application.get("application_data", {})
        premium_data = application.get("premium", {})
        
        effective_date = datetime.now() + timedelta(days=1)
        
        return Policy(
            policy_number=policy_number,
            product_code=app_data.get("product_code"),
            policy_status=PolicyStatus.INFORCE,
            applicant_name=app_data.get("applicant_name"),
            applicant_id_number=app_data.get("applicant_id_number"),
            applicant_phone=app_data.get("applicant_phone"),
            insured=Insured(
                name=app_data.get("insured_name"),
                gender=app_data.get("insured_gender"),
                birth_date=datetime.strptime(app_data.get("insured_birth_date", "1990-01-01"), "%Y-%m-%d"),
                id_type="ID_CARD",
                id_number=app_data.get("insured_id_number"),
                occupation_code=app_data.get("occupation_code"),
                occupation_name=app_data.get("occupation_name")
            ),
            sum_assured=Decimal(str(app_data.get("sum_assured", 0))),
            premium=Decimal(str(premium_data.get("premium", 0))),
            payment_method=app_data.get("payment_method", "ANNUAL"),
            payment_period=app_data.get("payment_period", 20),
            coverage_period=app_data.get("coverage_period", 30),
            application_date=datetime.now(),
            effective_date=effective_date,
            first_premium_date=effective_date,
            next_premium_due_date=effective_date + timedelta(days=365),
            maturity_date=effective_date + timedelta(days=365 * app_data.get("coverage_period", 30)),
            total_premiums_paid=Decimal(str(premium_data.get("premium", 0)))
        )
    
    async def _store_policy(self, policy: Policy):
        """存储保单"""
        key = f"policy:{policy.policy_number}"
        await self.redis_client.setex(key, 86400 * 365, json.dumps({
            "policy_number": policy.policy_number,
            "product_code": policy.product_code,
            "policy_status": policy.policy_status.value,
            "applicant_name": policy.applicant_name,
            "sum_assured": float(policy.sum_assured),
            "premium": float(policy.premium),
            "effective_date": policy.effective_date.isoformat()
        }))
    
    async def _send_e_policy(self, policy: Policy):
        """发送电子保单"""
        logger.info(f"发送电子保单至: {policy.applicant_phone}")


# 使用示例
async def main():
    """主函数 - 演示保险核心系统使用"""
    system = PolicyManagementSystem()
    await system.initialize()
    
    # 提交投保申请
    application = {
        "product_code": "P2025L00001",
        "applicant_name": "张三",
        "applicant_id_number": "110101199001011234",
        "applicant_phone": "13800138000",
        "insured_name": "张三",
        "insured_gender": "MALE",
        "insured_age": 35,
        "insured_birth_date": "1990-01-01",
        "insured_id_number": "110101199001011234",
        "occupation_code": "001",
        "occupation_name": "企业管理人员",
        "occupation_category": 2,
        "sum_assured": 1000000,
        "payment_method": "ANNUAL",
        "payment_period": 20,
        "coverage_period": 30,
        "height_cm": 175,
        "weight_kg": 70,
        "smoking_status": "NON_SMOKER",
        "health_declaration": {
            "q1": False,
            "q2": False,
            "q3": False
        }
    }
    
    result = await system.submit_application(application)
    print(f"投保结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 如果核保通过，模拟支付并承保
    if result.get("code") == "SUCCESS":
        application_no = result["data"]["application_no"]
        payment_confirmation = {"status": "SUCCESS", "amount": result["data"]["premium"]["premium"]}
        
        policy_result = await system.issue_policy(application_no, payment_confirmation)
        print(f"\n承保结果: {json.dumps(policy_result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
```


### 2.7 效果评估

#### 2.7.1 性能指标对比

| 指标类别 | 指标项 | 升级前 | 升级后 | 提升幅度 |
|----------|--------|--------|--------|----------|
| **产品创新** | 新产品上线周期 | 6-8个月 | 2周 | **缩短96%** |
| | 产品配置效率 | 人工编码 | 参数化配置 | **效率提升10倍** |
| | 产品版本管理 | 无版本控制 | 全生命周期管理 | **规范性100%** |
| | 产品测试周期 | 4周 | 3天 | **缩短82%** |
| **核保效率** | 标准体自动核保率 | 15% | 78% | **提升63%** |
| | 核保平均时效 | 3天 | 5分钟 | **提升99.7%** |
| | 人工核保工作量 | 100% | 22% | **降低78%** |
| | 核保准确率 | 85% | 97% | **提升12%** |
| **保单管理** | 保单查询响应 | 5秒 | 200ms | **提升96%** |
| | 保全处理时效 | 2天 | 实时 | **实时化** |
| | 保单变更成功率 | 92% | 99.5% | **提升7.5%** |
| | 账户计算精度 | 分 | 厘 | **精度提升10倍** |
| **客户服务** | 电子保单发送时效 | 24小时 | 实时 | **实时化** |
| | 客户自助服务率 | 30% | 75% | **提升45%** |
| | 客户满意度 | 82% | 94% | **提升12%** |
| | 投诉率 | 0.8% | 0.15% | **降低81%** |
| **监管合规** | 监管报送时效 | T+5 | T+1 | **缩短80%** |
| | 数据准确率 | 88% | 99.2% | **提升11.2%** |
| | 合规检查通过率 | 75% | 98% | **提升23%** |

#### 2.7.2 业务价值评估

| 价值维度 | 具体收益 | 量化指标 | ROI计算 |
|----------|----------|----------|---------|
| **产品创新收益** | 新产品快速上线带来的保费增长 | 年度新增保费：¥18亿 | 3年累计：¥54亿 |
| **运营成本节约** | 核保人力成本、保单管理成本降低 | 年度节约成本：¥6,500万 | 3年累计：¥1.95亿 |
| **风险损失减少** | 核保准确率提升带来的赔付减少 | 年度减少损失：¥2,800万 | 3年累计：¥8,400万 |
| **客户体验价值** | 客户满意度提升带来的续保率增长 | 续保率提升15% | 客户终身价值提升¥32亿 |
| **合规价值** | 监管报送自动化、合规成本降低 | 合规成本降低60% | 年度节约¥3,000万 |

**总投资回报率（ROI）**：
- 项目总投资：¥4.8亿（含系统建设、数据迁移、人员培训）
- 首年收益：¥24.8亿
- 3年累计收益：¥96.25亿
- **3年ROI = 1,905%**
- **投资回收期 = 2.3个月**

#### 2.7.3 经验教训

**成功经验**：

1. **产品DSL标准化**：建立了统一的保险产品领域特定语言（DSL），将产品要素抽象为12大类、200+属性，支持任意组合配置。产品DSL使业务人员能够直接参与产品设计，开发沟通效率提升70%。

2. **微服务+事件驱动**：核心系统拆分为产品、承保、保全、理赔、财务等8个微服务，通过Kafka事件总线进行异步通信。服务解耦使单服务故障不影响全局，系统可用性达99.99%。

3. **数据双轨并行**：新旧系统并行运行6个月，每日进行数据对账和差异分析。Schema映射工具确保数据一致性，迁移过程零保单权益损失。

**教训与改进**：

1. **遗留接口兼容**：300+外围系统接口格式不一，初期集成工作量超预期。改进：建立API网关，统一接入标准，提供SDK简化集成。

2. **精算模型迁移**：传统精算模型代码逻辑复杂，迁移过程中发现多处隐式假设。改进：建立精算模型知识库，详细记录每个计算公式的业务含义。

3. **组织变革管理**：核心系统升级涉及20+部门协作，初期协调成本高。改进：成立项目PMO，建立周例会机制，设立专项激励。

---

## 3. 案例2：互联网保险智能核保系统

### 3.1 企业背景

**企业名称**：众安在线XX事业部（化名：云保科技）  
**企业规模**：年度保费收入超过80亿元，服务客户超过5,000万人，日均投保量超过10万单  
**业务特色**：专注互联网场景保险，涵盖退货运费险、意外险、健康险、财产险等碎片化险种  
**核保现状**：传统人工核保无法满足互联网高并发需求，高峰期核保积压严重，客户流失率高

云保科技作为国内领先的互联网保险公司，其业务模式高度依赖线上自动核保。随着业务快速增长，日均核保请求从1万激增至10万+，传统核保系统面临严峻挑战。同时，互联网保险欺诈手段层出不穷，急需构建智能化、实时化的核保风控体系。

### 3.2 业务痛点

| 序号 | 痛点领域 | 具体问题描述 | 业务影响 |
|------|----------|--------------|----------|
| 1 | **核保时效慢** | 高峰期核保队列积压，平均等待时间超过30秒，客户流失率高达40% | 保费损失严重，获客成本浪费 |
| 2 | **逆选择严重** | 无法有效识别带病投保、超额投保等逆选择行为，赔付率居高不下 | 综合成本率(COR)高达105% |
| 3 | **欺诈识别弱** | 团伙欺诈、虚假身份、骗保案件频发，年欺诈损失超过¥2,000万 | 直接经济损失，合规风险 |
| 4 | **风控规则僵化** | 风控规则硬编码，调整需要发版，响应市场变化慢 | 黑产对抗被动，风险敞口大 |
| 5 | **数据利用不足** | 拥有海量投保数据但未充分利用，风控主要依赖简单规则 | 精准风控能力弱 |

### 3.3 业务目标

| 序号 | 目标维度 | 具体目标 | 预期指标 |
|------|----------|----------|----------|
| 1 | **实时核保** | 实现毫秒级智能核保决策，支撑高并发投保 | 核保响应<100ms，吞吐量>50,000TPS |
| 2 | **精准风控** | 构建AI驱动的风险识别模型，精准拦截高风险投保 | 逆选择识别率>90%，误杀率<3% |
| 3 | **动态对抗** | 建立规则动态调整机制，快速响应新型欺诈手段 | 规则调整时效<1小时 |
| 4 | **智能定价** | 基于风险评分实现千人千价，优化承保利润 | 定价精准度提升25% |
| 5 | **合规透明** | 建立可解释的风控决策体系，满足监管要求 | 决策可解释率100% |

### 3.4 技术挑战

| 挑战编号 | 挑战领域 | 具体描述 | 解决方案 |
|----------|----------|----------|----------|
| 1 | **超高并发处理** | 促销活动期间核保请求峰值达20万QPS，需在100ms内返回决策 | 多级缓存+本地计算，Redis Cluster存储热数据，核保决策本地缓存 |
| 2 | **实时特征计算** | 单笔核保需实时计算500+风险特征，包括设备指纹、行为序列、图谱关联等 | Flink流处理+特征预计算，Schema定义特征依赖关系图 |
| 3 | **模型实时更新** | 风控模型需每日更新，更新过程不能影响在线服务 | 蓝绿部署+模型版本管理，Schema定义模型接口契约 |
| 4 | **可解释性要求** | 监管要求核保拒保必须有明确依据，需支持决策解释 | Schema嵌入规则元数据，自动生成决策解释 |
| 5 | **数据安全合规** | 涉及健康告知等敏感信息，需满足《个人信息保护法》 | 数据脱敏+差分隐私，Schema标记敏感等级 |

### 3.5 Schema定义

**智能核保决策Schema**：

```dsl
schema IntelligentUnderwriting {
  // 投保请求
  application: UnderwritingApplication {
    application_id: String @value("APP20250121000001")
    product_code: String @value("PA2025ACC001")
    channel: String @value("WECHAT_MINI")
    application_time: DateTime @value("2025-01-21T14:30:25.123Z")
    
    // 投保人信息
    applicant: ApplicantInfo {
      name_hash: String @value("HASH-abc123...") @sensitive
      id_hash: String @value("HASH-def456...") @sensitive
      phone_hash: String @value("HASH-ghi789...") @sensitive
      age: Int @value(28)
      gender: Enum @value("MALE")
      occupation_category: Int @value(2)
      city: String @value("上海市")
    }
    
    // 投保计划
    coverage_plan: CoveragePlan {
      sum_assured: Decimal @value(1000000.00)
      coverage_period: Int @value(1)  // 年
      premium: Decimal @value(365.00)
      deductible: Decimal @value(10000.00)
    }
    
    // 健康告知
    health_declaration: HealthDeclaration {
      has_chronic_disease: Boolean @value(false)
      has_surgery_history: Boolean @value(false)
      has_family_history: Boolean @value(false)
      bmi: Decimal @value(22.5)
    }
  }

  // 设备与环境信息
  device_context: DeviceContext {
    device_id: String @value("DEV-a1b2c3d4")
    device_type: Enum @value("ANDROID")
    os_version: String @value("13.0")
    app_version: String @value("3.5.0")
    device_fingerprint: String @value("FP-xyz789...")
    
    // 安全指标
    security_indicators: SecurityIndicators {
      is_emulator: Boolean @value(false)
      is_rooted: Boolean @value(false)
      is_proxy: Boolean @value(false)
      is_vpn: Boolean @value(false)
      risk_score: Decimal @value(12.0)
    }
    
    // 行为特征
    behavior_features: BehaviorFeatures {
      input_speed_wpm: Decimal @value(45.5)
      field_change_count: Int @value(3)
      hesitation_time_ms: Int @value(2500)
      form_completion_time_sec: Int @value(180)
      is_paste_used: Boolean @value(false)
    }
  }

  // 历史行为
  historical_behavior: HistoricalBehavior {
    // 本用户历史
    user_history: UserHistory {
      previous_applications_30d: Int @value(0)
      previous_policies: Int @value(2)
      claim_count_12m: Int @value(0)
      total_premium_12m: Decimal @value(1250.00)
      payment_history: Enum @value("GOOD")
    }
    
    // 设备历史
    device_history: DeviceHistory {
      unique_users_30d: Int @value(1)
      application_count_30d: Int @value(2)
      claim_count_30d: Int @value(0)
      is_shared_device: Boolean @value(false)
    }
    
    // IP历史
    ip_history: IPHistory {
      ip: String @value("123.45.67.89") @sensitive
      unique_users_24h: Int @value(5)
      application_count_24h: Int @value(12)
      is_high_risk_ip: Boolean @value(false)
    }
  }

  // 图谱特征
  graph_features: GraphFeatures {
    // 关联用户
    connected_users: ConnectedUsers {
      same_device_users: Int @value(0)
      same_ip_users_24h: Int @value(4)
      same_phone_prefix_users: Int @value(1)
    }
    
    // 黑产关联
    fraud_association: FraudAssociation {
      blacklisted_connections: Int @value(0)
      greylisted_connections: Int @value(1)
      fraud_community_score: Decimal @value(15.0)
    }
  }

  // 外部数据
  external_data: ExternalData {
    // 征信数据
    credit_data: CreditData @sensitive {
      credit_score: Int @value(750)
      overdue_count_24m: Int @value(0)
      inquiry_count_3m: Int @value(1)
    }
    
    // 司法数据
    judicial_data: JudicialData {
      lawsuit_count: Int @value(0)
      execution_count: Int @value(0)
      is_dishonest: Boolean @value(false)
    }
    
    // 反欺诈联盟
    antifraud_alliance: AntifraudAlliance {
      fraud_flag: Boolean @value(false)
      risk_tag: Optional[String]
      confidence: Decimal @value(0.0)
    }
  }

  // 风险评分
  risk_assessment: RiskAssessment {
    // 综合评分
    composite_score: Decimal @value(25.5)
    risk_level: Enum @value("LOW")
    
    // 分项评分
    sub_scores: SubScores {
      identity_risk: Decimal @value(10.0)
      device_risk: Decimal @value(12.0)
      behavior_risk: Decimal @value(15.0)
      credit_risk: Decimal @value(5.0)
      association_risk: Decimal @value(20.0)
    }
    
    // 模型评分
    model_scores: ModelScores {
      xgb_score: Decimal @value(0.25)
      dnn_score: Decimal @value(0.18)
      graph_score: Decimal @value(0.22)
      ensemble_score: Decimal @value(0.22)
    }
  }

  // 核保决策
  underwriting_decision: UnderwritingDecision {
    decision: Enum @value("ACCEPT")
    decision_code: String @value("UW000")
    confidence: Decimal @value(0.95)
    
    // 触发规则
    triggered_rules: List[TriggeredRule] {
      rule1: TriggeredRule {
        rule_id: String @value("UW001")
        rule_name: String @value("标准体规则")
        rule_type: Enum @value("AUTO")
        score_contribution: Decimal @value(-10.0)
        explanation: String @value("投保人年龄、职业、健康状况符合标准体要求")
      }
    }
    
    // 定价调整
    pricing_adjustment: PricingAdjustment {
      base_premium: Decimal @value(365.00)
      risk_adjustment_rate: Decimal @value(1.0)
      final_premium: Decimal @value(365.00)
      adjustment_reason: Optional[String]
    }
    
    // 决策解释
    decision_explanation: DecisionExplanation {
      summary: String @value("投保人风险评分低，自动承保")
      key_factors: List[String] @value(["无历史理赔记录", "设备环境安全", "行为特征正常"])
      recommendations: List[String] @value([])
    }
  }

  // 性能指标
  performance_metrics: PerformanceMetrics {
    total_latency_ms: Int @value(45)
    feature_calculation_ms: Int @value(15)
    model_inference_ms: Int @value(12)
    rule_evaluation_ms: Int @value(8)
    decision_generation_ms: Int @value(10)
  }
} @standard("互联网保险监管办法") @data_classification("SENSITIVE")
```

---

### 3.6 代码实现

**互联网保险智能核保引擎完整实现**：

```python
"""
互联网保险智能核保引擎 - 基于DSL Schema的实时风控系统
支持高并发核保、AI风险识别、动态规则管理
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import numpy as np

import redis.asyncio as redis
from kafka import KafkaProducer
import tensorflow as tf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntelligentUnderwriting")


class UnderwritingDecision(Enum):
    """核保决策枚举"""
    ACCEPT = "接受"
    RATED_UP = "加费"
    EXCLUSION = "除外"
    MANUAL_REVIEW = "人工审核"
    DECLINE = "拒保"
    POSTPONE = "延期"


class RiskLevel(Enum):
    """风险等级枚举"""
    VERY_LOW = "极低"
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    VERY_HIGH = "极高"


@dataclass
class ApplicantInfo:
    """投保人信息"""
    name_hash: str
    id_hash: str
    phone_hash: str
    age: int
    gender: str
    occupation_category: int
    city: str


@dataclass
class CoveragePlan:
    """投保计划"""
    sum_assured: Decimal
    coverage_period: int
    premium: Decimal
    deductible: Decimal


@dataclass
class SecurityIndicators:
    """安全指标"""
    is_emulator: bool
    is_rooted: bool
    is_proxy: bool
    is_vpn: bool
    risk_score: Decimal


@dataclass
class BehaviorFeatures:
    """行为特征"""
    input_speed_wpm: Decimal
    field_change_count: int
    hesitation_time_ms: int
    form_completion_time_sec: int
    is_paste_used: bool


@dataclass
class RiskAssessment:
    """风险评估"""
    composite_score: Decimal
    risk_level: RiskLevel
    identity_risk: Decimal
    device_risk: Decimal
    behavior_risk: Decimal
    credit_risk: Decimal
    association_risk: Decimal


@dataclass
class UnderwritingResult:
    """核保结果"""
    application_id: str
    decision: UnderwritingDecision
    decision_code: str
    confidence: Decimal
    risk_score: Decimal
    risk_level: RiskLevel
    final_premium: Decimal
    triggered_rules: List[Dict]
    explanation: str
    latency_ms: int


class FeatureCalculationEngine:
    """特征计算引擎"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.feature_cache = {}
    
    async def calculate_features(self, application: Dict) -> Dict[str, Any]:
        """计算核保特征"""
        features = {}
        
        # 并行计算各类特征
        await asyncio.gather(
            self._calc_identity_features(application, features),
            self._calc_device_features(application, features),
            self._calc_behavior_features(application, features),
            self._calc_historical_features(application, features),
            self._calc_graph_features(application, features),
            self._calc_external_features(application, features)
        )
        
        return features
    
    async def _calc_identity_features(self, app: Dict, features: Dict):
        """计算身份特征"""
        applicant = app.get("applicant", {})
        
        features["age"] = applicant.get("age", 0)
        features["age_risk"] = self._calc_age_risk(applicant.get("age", 30))
        features["occupation_risk"] = applicant.get("occupation_category", 1) * 10
        features["city_tier"] = self._get_city_tier(applicant.get("city", ""))
    
    async def _calc_device_features(self, app: Dict, features: Dict):
        """计算设备特征"""
        device = app.get("device_context", {})
        security = device.get("security_indicators", {})
        
        features["device_risk_score"] = security.get("risk_score", 0)
        features["is_emulator"] = 1 if security.get("is_emulator") else 0
        features["is_rooted"] = 1 if security.get("is_rooted") else 0
        features["is_proxy"] = 1 if security.get("is_proxy") else 0
        features["is_vpn"] = 1 if security.get("is_vpn") else 0
    
    async def _calc_behavior_features(self, app: Dict, features: Dict):
        """计算行为特征"""
        behavior = app.get("device_context", {}).get("behavior_features", {})
        
        features["input_speed"] = float(behavior.get("input_speed_wpm", 40))
        features["field_changes"] = behavior.get("field_change_count", 0)
        features["hesitation_time"] = behavior.get("hesitation_time_ms", 0)
        features["completion_time"] = behavior.get("form_completion_time_sec", 120)
        features["is_paste_used"] = 1 if behavior.get("is_paste_used") else 0
        
        # 异常行为检测
        features["behavior_anomaly"] = self._detect_behavior_anomaly(behavior)
    
    async def _calc_historical_features(self, app: Dict, features: Dict):
        """计算历史特征"""
        history = app.get("historical_behavior", {})
        user_hist = history.get("user_history", {})
        device_hist = history.get("device_history", {})
        ip_hist = history.get("ip_history", {})
        
        features["prev_applications_30d"] = user_hist.get("previous_applications_30d", 0)
        features["prev_policies"] = user_hist.get("previous_policies", 0)
        features["claim_count_12m"] = user_hist.get("claim_count_12m", 0)
        features["device_users_30d"] = device_hist.get("unique_users_30d", 0)
        features["ip_users_24h"] = ip_hist.get("unique_users_24h", 0)
    
    async def _calc_graph_features(self, app: Dict, features: Dict):
        """计算图谱特征"""
        graph = app.get("graph_features", {})
        fraud_assoc = graph.get("fraud_association", {})
        
        features["fraud_community_score"] = fraud_assoc.get("fraud_community_score", 0)
        features["blacklisted_connections"] = fraud_assoc.get("blacklisted_connections", 0)
        features["greylisted_connections"] = fraud_assoc.get("greylisted_connections", 0)
    
    async def _calc_external_features(self, app: Dict, features: Dict):
        """计算外部特征"""
        external = app.get("external_data", {})
        credit = external.get("credit_data", {})
        judicial = external.get("judicial_data", {})
        
        features["credit_score"] = credit.get("credit_score", 600)
        features["credit_normalized"] = (credit.get("credit_score", 600) - 350) / 5
        features["overdue_count"] = credit.get("overdue_count_24m", 0)
        features["lawsuit_count"] = judicial.get("lawsuit_count", 0)
        features["is_dishonest"] = 1 if judicial.get("is_dishonest") else 0
    
    def _calc_age_risk(self, age: int) -> float:
        """计算年龄风险"""
        if age < 18 or age > 65:
            return 100
        elif age > 55:
            return 50
        elif age > 45:
            return 30
        return 10
    
    def _get_city_tier(self, city: str) -> int:
        """获取城市等级"""
        tier1 = ["北京", "上海", "广州", "深圳"]
        tier2 = ["杭州", "南京", "成都", "武汉", "西安"]
        
        if city in tier1:
            return 1
        elif city in tier2:
            return 2
        return 3
    
    def _detect_behavior_anomaly(self, behavior: Dict) -> float:
        """检测行为异常"""
        anomaly_score = 0
        
        # 填写过快（可能使用脚本）
        if behavior.get("form_completion_time_sec", 120) < 30:
            anomaly_score += 30
        
        # 输入速度异常
        if behavior.get("input_speed_wpm", 40) > 100:
            anomaly_score += 20
        
        # 频繁切换字段
        if behavior.get("field_change_count", 0) > 10:
            anomaly_score += 15
        
        return min(anomaly_score, 100)


class RiskScoringEngine:
    """风险评分引擎"""
    
    def __init__(self):
        self.models = self._load_models()
    
    def _load_models(self) -> Dict:
        """加载模型"""
        return {
            "xgb": None,  # xgboost.Booster()
            "dnn": None,  # tf.keras.models.load_model()
            "graph": None
        }
    
    def calculate_risk(self, features: Dict) -> RiskAssessment:
        """计算风险评分"""
        # 分项风险评分
        identity_risk = self._calc_identity_risk(features)
        device_risk = self._calc_device_risk(features)
        behavior_risk = self._calc_behavior_risk(features)
        credit_risk = self._calc_credit_risk(features)
        association_risk = self._calc_association_risk(features)
        
        # 综合评分（加权平均）
        composite = (
            identity_risk * Decimal('0.15') +
            device_risk * Decimal('0.20') +
            behavior_risk * Decimal('0.25') +
            credit_risk * Decimal('0.25') +
            association_risk * Decimal('0.15')
        )
        
        # 确定风险等级
        if composite < Decimal('20'):
            level = RiskLevel.VERY_LOW
        elif composite < Decimal('40'):
            level = RiskLevel.LOW
        elif composite < Decimal('60'):
            level = RiskLevel.MEDIUM
        elif composite < Decimal('80'):
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.VERY_HIGH
        
        return RiskAssessment(
            composite_score=composite,
            risk_level=level,
            identity_risk=identity_risk,
            device_risk=device_risk,
            behavior_risk=behavior_risk,
            credit_risk=credit_risk,
            association_risk=association_risk
        )
    
    def _calc_identity_risk(self, features: Dict) -> Decimal:
        """计算身份风险"""
        score = Decimal('0')
        score += Decimal(str(features.get("age_risk", 0)))
        score += Decimal(str(features.get("occupation_risk", 0)))
        return min(score, Decimal('100'))
    
    def _calc_device_risk(self, features: Dict) -> Decimal:
        """计算设备风险"""
        score = Decimal(str(features.get("device_risk_score", 0)))
        if features.get("is_emulator"):
            score += Decimal('50')
        if features.get("is_proxy"):
            score += Decimal('30')
        return min(score, Decimal('100'))
    
    def _calc_behavior_risk(self, features: Dict) -> Decimal:
        """计算行为风险"""
        return Decimal(str(features.get("behavior_anomaly", 0)))
    
    def _calc_credit_risk(self, features: Dict) -> Decimal:
        """计算信用风险"""
        score = Decimal('100') - Decimal(str(features.get("credit_normalized", 50)))
        score += Decimal(str(features.get("overdue_count", 0))) * Decimal('20')
        if features.get("is_dishonest"):
            score += Decimal('100')
        return min(score, Decimal('100'))
    
    def _calc_association_risk(self, features: Dict) -> Decimal:
        """计算关联风险"""
        score = Decimal(str(features.get("fraud_community_score", 0)))
        score += Decimal(str(features.get("blacklisted_connections", 0))) * Decimal('30')
        score += Decimal(str(features.get("ip_users_24h", 0))) * Decimal('5')
        return min(score, Decimal('100'))


class DynamicRuleEngine:
    """动态规则引擎"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.rules = []
        self.rule_version = "1.0.0"
    
    async def load_rules(self):
        """加载规则"""
        # 从Redis加载规则
        rules_data = await self.redis.get("underwriting:rules")
        if rules_data:
            self.rules = json.loads(rules_data)
        else:
            self.rules = self._default_rules()
    
    def _default_rules(self) -> List[Dict]:
        """默认规则"""
        return [
            {
                "rule_id": "R001",
                "name": "极高风险拦截",
                "condition": "risk_score >= 80",
                "action": "DECLINE",
                "priority": 100,
                "explanation": "风险评分过高，系统自动拒保"
            },
            {
                "rule_id": "R002",
                "name": "模拟器检测",
                "condition": "is_emulator == 1",
                "action": "DECLINE",
                "priority": 95,
                "explanation": "检测到模拟器环境，存在欺诈风险"
            },
            {
                "rule_id": "R003",
                "name": "失信人员",
                "condition": "is_dishonest == 1",
                "action": "DECLINE",
                "priority": 95,
                "explanation": "投保人存在失信记录"
            },
            {
                "rule_id": "R004",
                "name": "高风险职业",
                "condition": "occupation_category >= 5",
                "action": "DECLINE",
                "priority": 90,
                "explanation": "职业风险等级超出承保范围"
            },
            {
                "rule_id": "R005",
                "name": "加费承保",
                "condition": "risk_score >= 40 and risk_score < 60",
                "action": "RATED_UP",
                "loading": 1.3,
                "priority": 70,
                "explanation": "风险评分中等，需加费承保"
            },
            {
                "rule_id": "R006",
                "name": "人工审核",
                "condition": "risk_score >= 60 and risk_score < 80",
                "action": "MANUAL_REVIEW",
                "priority": 80,
                "explanation": "风险评分较高，需人工审核"
            },
            {
                "rule_id": "R007",
                "name": "标准体",
                "condition": "risk_score < 20",
                "action": "ACCEPT",
                "priority": 10,
                "explanation": "风险评分低，标准体承保"
            }
        ]
    
    def evaluate(self, features: Dict, risk_assessment: RiskAssessment) -> Tuple[UnderwritingDecision, List[Dict]]:
        """评估规则"""
        triggered_rules = []
        decision = UnderwritingDecision.ACCEPT
        
        # 准备规则执行上下文
        context = {
            **features,
            "risk_score": float(risk_assessment.composite_score),
            "risk_level": risk_assessment.risk_level.name
        }
        
        for rule in sorted(self.rules, key=lambda r: r["priority"], reverse=True):
            try:
                if eval(rule["condition"], context):
                    triggered_rules.append({
                        "rule_id": rule["rule_id"],
                        "rule_name": rule["name"],
                        "explanation": rule["explanation"]
                    })
                    
                    action = rule["action"]
                    if action == "DECLINE":
                        return UnderwritingDecision.DECLINE, triggered_rules
                    elif action == "MANUAL_REVIEW":
                        decision = UnderwritingDecision.MANUAL_REVIEW
                    elif action == "RATED_UP":
                        if decision == UnderwritingDecision.ACCEPT:
                            decision = UnderwritingDecision.RATED_UP
                    elif action == "POSTPONE":
                        if decision in [UnderwritingDecision.ACCEPT]:
                            decision = UnderwritingDecision.POSTPONE
                            
            except Exception as e:
                logger.error(f"规则 {rule['rule_id']} 执行失败: {e}")
        
        return decision, triggered_rules
    
    async def update_rules(self, new_rules: List[Dict], version: str):
        """更新规则"""
        await self.redis.setex("underwriting:rules", 86400, json.dumps(new_rules))
        await self.redis.setex("underwriting:rules:version", 86400, version)
        self.rules = new_rules
        self.rule_version = version
        logger.info(f"规则已更新至版本 {version}")


class IntelligentUnderwritingEngine:
    """智能核保引擎主类"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.feature_engine: Optional[FeatureCalculationEngine] = None
        self.risk_engine = RiskScoringEngine()
        self.rule_engine: Optional[DynamicRuleEngine] = None
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "accept_count": 0,
            "rated_up_count": 0,
            "manual_review_count": 0,
            "decline_count": 0,
            "avg_latency_ms": 0
        }
    
    async def initialize(self):
        """初始化引擎"""
        self.redis_client = redis.Redis(
            host='localhost', port=6379, db=2, decode_responses=True
        )
        self.feature_engine = FeatureCalculationEngine(self.redis_client)
        self.rule_engine = DynamicRuleEngine(self.redis_client)
        await self.rule_engine.load_rules()
        logger.info("智能核保引擎初始化完成")
    
    async def underwrite(self, application: Dict) -> UnderwritingResult:
        """执行智能核保"""
        start_time = time.time()
        application_id = application.get("application_id", str(uuid.uuid4()))
        
        try:
            # 1. 特征计算
            features = await self.feature_engine.calculate_features(application)
            
            # 2. 风险评分
            risk_assessment = self.risk_engine.calculate_risk(features)
            
            # 3. 规则评估
            decision, triggered_rules = self.rule_engine.evaluate(features, risk_assessment)
            
            # 4. 定价调整
            base_premium = Decimal(str(application.get("coverage_plan", {}).get("premium", 0)))
            final_premium = base_premium
            
            if decision == UnderwritingDecision.RATED_UP:
                for rule in triggered_rules:
                    if rule.get("action") == "RATED_UP":
                        loading = Decimal(str(rule.get("loading", 1.0)))
                        final_premium = base_premium * loading
                        break
            
            # 5. 构建结果
            latency_ms = int((time.time() - start_time) * 1000)
            
            result = UnderwritingResult(
                application_id=application_id,
                decision=decision,
                decision_code=self._get_decision_code(decision),
                confidence=Decimal('0.95') if decision != UnderwritingDecision.MANUAL_REVIEW else Decimal('0.7'),
                risk_score=risk_assessment.composite_score,
                risk_level=risk_assessment.risk_level,
                final_premium=final_premium.quantize(Decimal('0.01')),
                triggered_rules=triggered_rules,
                explanation=self._generate_explanation(decision, triggered_rules, risk_assessment),
                latency_ms=latency_ms
            )
            
            # 6. 更新统计
            await self._update_stats(decision, latency_ms)
            
            # 7. 记录决策日志
            await self._log_decision(result, features)
            
            logger.info(f"核保完成: application_id={application_id}, "
                       f"decision={decision.value}, risk_score={risk_assessment.composite_score}, "
                       f"latency={latency_ms}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"核保异常: {e}")
            # 异常时转人工审核
            return UnderwritingResult(
                application_id=application_id,
                decision=UnderwritingDecision.MANUAL_REVIEW,
                decision_code="UW999",
                confidence=Decimal('0.5'),
                risk_score=Decimal('50'),
                risk_level=RiskLevel.MEDIUM,
                final_premium=Decimal('0'),
                triggered_rules=[{"rule_id": "SYSTEM", "rule_name": "系统异常", "explanation": str(e)}],
                explanation=f"系统异常，转人工审核: {str(e)}",
                latency_ms=int((time.time() - start_time) * 1000)
            )
    
    def _get_decision_code(self, decision: UnderwritingDecision) -> str:
        """获取决策代码"""
        codes = {
            UnderwritingDecision.ACCEPT: "UW000",
            UnderwritingDecision.RATED_UP: "UW100",
            UnderwritingDecision.EXCLUSION: "UW200",
            UnderwritingDecision.MANUAL_REVIEW: "UW300",
            UnderwritingDecision.DECLINE: "UW400",
            UnderwritingDecision.POSTPONE: "UW500"
        }
        return codes.get(decision, "UW999")
    
    def _generate_explanation(self, decision: UnderwritingDecision, 
                              rules: List[Dict], risk: RiskAssessment) -> str:
        """生成决策解释"""
        if decision == UnderwritingDecision.ACCEPT:
            return f"风险评分{risk.composite_score}，属于{risk.risk_level.value}风险，标准体承保"
        elif decision == UnderwritingDecision.DECLINE:
            return f"触发规则：{rules[0]['explanation']}" if rules else "风险评分过高"
        elif decision == UnderwritingDecision.RATED_UP:
            return f"风险评分{risk.composite_score}，需加费承保"
        elif decision == UnderwritingDecision.MANUAL_REVIEW:
            return f"风险评分{risk.composite_score}，需人工进一步审核"
        return ""
    
    async def _update_stats(self, decision: UnderwritingDecision, latency: int):
        """更新统计"""
        self.stats["total_requests"] += 1
        
        if decision == UnderwritingDecision.ACCEPT:
            self.stats["accept_count"] += 1
        elif decision == UnderwritingDecision.RATED_UP:
            self.stats["rated_up_count"] += 1
        elif decision == UnderwritingDecision.MANUAL_REVIEW:
            self.stats["manual_review_count"] += 1
        elif decision == UnderwritingDecision.DECLINE:
            self.stats["decline_count"] += 1
        
        # 更新平均延迟
        n = self.stats["total_requests"]
        self.stats["avg_latency_ms"] = (self.stats["avg_latency_ms"] * (n - 1) + latency) / n
    
    async def _log_decision(self, result: UnderwritingResult, features: Dict):
        """记录决策日志"""
        log_data = {
            "application_id": result.application_id,
            "decision": result.decision.value,
            "risk_score": float(result.risk_score),
            "risk_level": result.risk_level.value,
            "features": features,
            "timestamp": datetime.now().isoformat()
        }
        
        key = f"uw_log:{result.application_id}"
        await self.redis_client.setex(key, 86400 * 30, json.dumps(log_data))
    
    def get_stats(self) -> Dict:
        """获取统计"""
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "accept_rate": round(self.stats["accept_count"] / total * 100, 2),
            "auto_underwriting_rate": round(
                (self.stats["accept_count"] + self.stats["rated_up_count"] + self.stats["decline_count"]) / total * 100, 2
            ),
            "manual_review_rate": round(self.stats["manual_review_count"] / total * 100, 2)
        }


# 使用示例
async def main():
    """主函数 - 演示智能核保引擎"""
    engine = IntelligentUnderwritingEngine()
    await engine.initialize()
    
    # 构造投保申请
    application = {
        "application_id": "APP20250121000001",
        "product_code": "PA2025ACC001",
        "channel": "WECHAT_MINI",
        "applicant": {
            "name_hash": "HASH-abc123",
            "id_hash": "HASH-def456",
            "phone_hash": "HASH-ghi789",
            "age": 28,
            "gender": "MALE",
            "occupation_category": 2,
            "city": "上海市"
        },
        "coverage_plan": {
            "sum_assured": 1000000,
            "coverage_period": 1,
            "premium": 365.00,
            "deductible": 10000
        },
        "device_context": {
            "security_indicators": {
                "is_emulator": False,
                "is_rooted": False,
                "is_proxy": False,
                "is_vpn": False,
                "risk_score": 12.0
            },
            "behavior_features": {
                "input_speed_wpm": 45.5,
                "field_change_count": 3,
                "hesitation_time_ms": 2500,
                "form_completion_time_sec": 180,
                "is_paste_used": False
            }
        },
        "historical_behavior": {
            "user_history": {
                "previous_applications_30d": 0,
                "previous_policies": 2,
                "claim_count_12m": 0
            },
            "device_history": {
                "unique_users_30d": 1,
                "unique_users_24h": 5
            },
            "ip_history": {
                "unique_users_24h": 5,
                "is_high_risk_ip": False
            }
        },
        "graph_features": {
            "fraud_association": {
                "blacklisted_connections": 0,
                "greylisted_connections": 1,
                "fraud_community_score": 15.0
            }
        },
        "external_data": {
            "credit_data": {
                "credit_score": 750,
                "overdue_count_24m": 0
            },
            "judicial_data": {
                "lawsuit_count": 0,
                "is_dishonest": False
            }
        }
    }
    
    # 执行核保
    result = await engine.underwrite(application)
    print(f"核保结果:")
    print(f"  决策: {result.decision.value}")
    print(f"  风险评分: {result.risk_score}")
    print(f"  风险等级: {result.risk_level.value}")
    print(f"  最终保费: {result.final_premium}")
    print(f"  决策解释: {result.explanation}")
    print(f"  处理耗时: {result.latency_ms}ms")
    print(f"\n引擎统计: {json.dumps(engine.get_stats(), ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
```


### 3.7 效果评估

#### 3.7.1 性能指标对比

| 指标类别 | 指标项 | 实施前 | 实施后 | 提升幅度 |
|----------|--------|--------|--------|----------|
| **核保时效** | 平均核保响应时间 | 3,500ms | 42ms | **提升98.8%** |
| | P99响应时间 | 15,000ms | 85ms | **提升99.4%** |
| | 峰值吞吐量 | 2,000TPS | 55,000TPS | **提升26.5倍** |
| | 核保队列积压 | 高峰期>10,000单 | 0单 | **完全消除** |
| **风控效果** | 逆选择识别率 | 35% | 92% | **提升57%** |
| | 欺诈拦截率 | 12% | 87% | **提升75%** |
| | 误杀率 | 18% | 2.5% | **降低86%** |
| | 综合成本率(COR) | 105% | 96% | **降低9%** |
| **自动化率** | 自动核保通过率 | 15% | 82% | **提升67%** |
| | 人工核保占比 | 85% | 18% | **降低67%** |
| | 规则调整时效 | 2周 | 1小时 | **缩短99.7%** |
| **业务指标** | 客户流失率 | 40% | 8% | **降低80%** |
| | 投保转化率 | 55% | 82% | **提升49%** |
| | 客户满意度 | 72% | 91% | **提升26%** |
| | 投诉率 | 1.2% | 0.2% | **降低83%** |

#### 3.7.2 业务价值评估

| 价值维度 | 具体收益 | 量化指标 | ROI计算 |
|----------|----------|----------|---------|
| **核保效率提升** | 自动化率提升带来的人力成本节约 | 年度节约：¥1,800万 | 3年累计：¥5,400万 |
| **欺诈损失减少** | 欺诈识别率提升带来的赔付减少 | 年度减少：¥2,500万 | 3年累计：¥7,500万 |
| **客户转化提升** | 核保时效提升带来的投保转化率增长 | 年度增收：¥8,000万 | 3年累计：¥2.4亿 |
| **COR优化** | 风控能力提升带来的承保利润改善 | 年度增收：¥6,000万 | 3年累计：¥1.8亿 |
| **获客成本节约** | 流失率降低带来的获客成本节约 | 年度节约：¥3,200万 | 3年累计：¥9,600万 |

**总投资回报率（ROI）**：
- 项目总投资：¥3,500万（含平台建设、模型开发、数据采购）
- 首年收益：¥2.15亿
- 3年累计收益：¥6.41亿
- **3年ROI = 1,732%**
- **投资回收期 = 2个月**

#### 3.7.3 经验教训

**成功经验**：

1. **实时特征体系**：构建了500+维实时特征，涵盖设备、行为、图谱、外部数据等维度。特征Schema标准化使模型迭代周期从3周缩短至3天，支持快速响应黑产变化。

2. **端到端延迟优化**：通过特征预计算、本地缓存、异步处理等手段，将核保延迟从3.5秒降至42毫秒。客户体验大幅改善，投保流失率从40%降至8%。

3. **对抗学习机制**：建立"监测-分析-响应-验证"闭环，每日分析拒保案例，每周更新风控规则，每月重训练模型。新型欺诈模式识别时间从30天缩短至3天。

**教训与改进**：

1. **冷启动困境**：新渠道上线初期缺乏历史数据，误杀率偏高。改进：采用迁移学习，利用其他渠道数据预训练模型，新渠道冷启动期从2周缩短至3天。

2. **模型可解释性**：初期ML模型"黑盒"特性导致业务方不信任。改进：引入SHAP值解释，为每笔决策生成可视化解释，业务接受度从60%提升至95%。

3. **跨公司协作**：反欺诈联盟数据共享存在法律顾虑。改进：采用联邦学习，原始数据不出域，仅共享模型参数，在保护隐私的同时提升识别能力。

---

## 4. 案例3：保险理赔智能反欺诈平台

### 4.1 企业背景

**企业名称**：中国平安XX财产险分公司（化名：安盛财险）  
**企业规模**：年度保费收入超过500亿元，年理赔案件超过300万件，理赔金额超过¥300亿  
**理赔现状**：传统理赔审核主要依赖人工经验，欺诈识别能力弱，年度欺诈损失估计超过¥15亿

安盛财险作为国内领先的财产保险公司，其理赔业务覆盖车险、财产险、责任险等多个险种。随着理赔量持续增长，传统的"人盯人"审核模式已无法有效识别日益复杂的保险欺诈行为。虚假事故、骗保团伙、内外勾结等欺诈手段层出不穷，急需构建智能化的理赔反欺诈体系。

### 4.2 业务痛点

| 序号 | 痛点领域 | 具体问题描述 | 业务影响 |
|------|----------|--------------|----------|
| 1 | **欺诈损失巨大** | 年度欺诈损失估计¥15亿，车险欺诈率约15%，财产险欺诈率约8% | 直接经济损失，保费上涨压力 |
| 2 | **识别能力弱** | 依赖人工经验识别欺诈，复杂欺诈案件发现率低，团伙欺诈难以识别 | 大量欺诈案件漏网 |
| 3 | **审核效率低** | 理赔案件平均审核时效5天，人工调查成本高，小额案件审核不经济 | 运营成本增加，客户体验差 |
| 4 | **数据未打通** | 理赔数据与承保数据、外部数据（交警、医院、维修厂）未打通 | 信息孤岛，无法交叉验证 |
| 5 | **调查成本高** | 委托第三方调查公司成本高，平均调查费用¥3,000/案，投入产出比低 | 调查成本居高不下 |

### 4.3 业务目标

| 序号 | 目标维度 | 具体目标 | 预期指标 |
|------|----------|----------|----------|
| 1 | **欺诈识别** | 建立AI驱动的理赔反欺诈模型，精准识别各类欺诈案件 | 欺诈识别率>85%，误报率<5% |
| 2 | **审核提效** | 实现理赔案件智能分流，简单案件自动审核 | 自动化审核率>70%，时效提升3倍 |
| 3 | **成本降低** | 精准定位高风险案件，减少无效调查 | 调查成本降低40% |
| 4 | **团伙打击** | 构建理赔知识图谱，识别骗保团伙 | 团伙发现率>90% |
| 5 | **数据整合** | 打通内外部数据源，构建统一理赔视图 | 数据覆盖率>95% |

### 4.4 技术挑战

| 挑战编号 | 挑战领域 | 具体描述 | 解决方案 |
|----------|----------|----------|----------|
| 1 | **多模态数据处理** | 理赔数据包括结构化数据（保单、定损）、半结构化数据（查勘报告）、非结构化数据（照片、视频） | 基于Schema统一数据模型，OCR+NLP提取关键信息，多模态特征融合 |
| 2 | **团伙欺诈识别** | 骗保团伙组织严密，单案件看似正常，需从关联关系中发现异常模式 | 构建理赔知识图谱，Graph Neural Network识别团伙模式 |
| 3 | **正负样本失衡** | 欺诈案件占比<5%，严重样本失衡，传统模型效果差 | SMOTE过采样+代价敏感学习，结合主动学习持续标注 |
| 4 | **实时性要求** | 理赔审核需在定损后即时给出欺诈风险提示 | 流式计算+预训练模型，秒级风险评分 |
| 5 | **可解释性要求** | 拒赔案件需有明确证据支持，需提供可解释的欺诈依据 | 注意力机制可视化+规则引擎，生成欺诈证据链 |

### 4.5 Schema定义

**理赔反欺诈案件Schema**：

```dsl
schema ClaimsFraudDetection {
  // 案件基础信息
  claim_basic: ClaimBasicInfo {
    claim_no: String @value("CLM20250121000001")
    policy_no: String @value("POL2025000001")
    report_no: String @value("RPT2025012100001")
    
    // 险种信息
    insurance_type: Enum @value("AUTO")
    product_code: String @value("PAUTO2025")
    coverage_type: String @value("VEHICLE_DAMAGE")
    
    // 时间信息
    accident_date: DateTime @value("2025-01-20T15:30:00Z")
    report_date: DateTime @value("2025-01-20T16:45:00Z")
    claim_date: DateTime @value("2025-01-21T09:00:00Z")
    
    // 出险信息
    accident_location: Location {
      province: String @value("广东省")
      city: String @value("深圳市")
      district: String @value("南山区")
      address: String @value("深南大道XX路段")
      longitude: Decimal @value(113.9433)
      latitude: Decimal @value(22.5233)
    }
    
    accident_description: String @value("两车追尾，本车车头受损")
    accident_type: Enum @value("REAR_END")
    weather_condition: String @value("晴")
    is_night: Boolean @value(false)
    is_weekend: Boolean @value(true)
    
    // 损失信息
    estimated_loss: Decimal @value(15000.00)
    claim_amount: Decimal @value(12000.00)
    deductible: Decimal @value(1000.00)
    salvage_value: Decimal @value(0)
  }

  // 当事人信息
  parties: PartiesInfo {
    // 被保险人
    insured: InsuredInfo {
      name_hash: String @value("HASH-insured001") @sensitive
      id_hash: String @value("HASH-id001") @sensitive
      phone_hash: String @value("HASH-phone001") @sensitive
      age: Int @value(32)
      gender: Enum @value("MALE")
      driver_license_no: String @value("HASH-license001") @sensitive
      license_issue_date: Date @value("2015-03-15")
      driving_experience_years: Int @value(10)
    }
    
    // 驾驶员
    driver: DriverInfo {
      is_insured: Boolean @value(true)
      name_hash: String @value("HASH-driver001") @sensitive
      id_hash: String @value("HASH-id001") @sensitive
      license_type: String @value("C1")
      license_status: String @value("VALID")
    }
    
    // 对方当事人（如有）
    third_party: Optional[ThirdPartyInfo] {
      name_hash: String @value("HASH-tp001") @sensitive
      vehicle_plate: String @value("粤B-XXXXX")
      insurance_company: String @value("平安财险")
      has_compulsory_insurance: Boolean @value(true)
    }
  }

  // 车辆信息
  vehicle_info: VehicleInfo {
    vehicle_plate: String @value("粤A-XXXXX")
    vin: String @value("LSVXXXXXXXXXXXXXX")
    engine_no: String @value("ENGINE001")
    brand_model: String @value("大众-帕萨特")
    vehicle_type: String @value("轿车")
    purchase_date: Date @value("2022-06-15")
    vehicle_age_months: Int @value(31)
    mileage_km: Int @value(45000)
    is_commercial_use: Boolean @value(false)
    
    // 历史理赔
    claim_history: ClaimHistory {
      total_claims: Int @value(2)
      total_claim_amount: Decimal @value(8000.00)
      last_claim_date: Optional[Date] @value("2024-08-10")
      last_claim_amount: Decimal @value(3500.00)
      days_since_last_claim: Int @value(164)
    }
  }

  // 维修信息
  repair_info: RepairInfo {
    repair_shop: RepairShop {
      shop_code: String @value("RS001")
      shop_name: String @value("XX汽车维修中心")
      shop_rating: Decimal @value(4.2)
      is_authorized: Boolean @value(true)
      cooperation_years: Int @value(3)
      monthly_claims_avg: Int @value(45)
      fraud_flag_count: Int @value(0)
    }
    
    damage_parts: List[DamagePart] {
      part1: DamagePart {
        part_code: String @value("BUMPER_FRONT")
        part_name: String @value("前保险杠")
        damage_type: String @value("REPLACE")
        part_price: Decimal @value(2800.00)
        labor_cost: Decimal @value(500.00)
        paint_cost: Decimal @value(800.00)
      }
      part2: DamagePart {
        part_code: String @value("HEADLIGHT_LEFT")
        part_name: String @value("左前大灯")
        damage_type: String @value("REPLACE")
        part_price: Decimal @value(3500.00)
        labor_cost: Decimal @value(300.00)
      }
    }
    
    total_repair_estimate: Decimal @value(15000.00)
    repair_days: Int @value(5)
  }

  // 查勘信息
  survey_info: SurveyInfo {
    surveyor_id: String @value("SUR001")
    surveyor_name: String @value("王查勘")
    survey_date: DateTime @value("2025-01-21T10:30:00Z")
    survey_method: Enum @value("ON_SITE")
    
    // 查勘发现
    findings: SurveyFindings {
      damage_consistent_with_description: Boolean @value(true)
      old_damage_found: Boolean @value(false)
      suspicious_damage_found: Boolean @value(false)
      vehicle_condition_matches: Boolean @value(true)
      driver_matches_id: Boolean @value(true)
    }
    
    // 影像资料
    photos: List[Photo] {
      photo_count: Int @value(12)
      has_overview: Boolean @value(true)
      has_damage_detail: Boolean @value(true)
      has_vin_photo: Boolean @value(true)
      has_license_photo: Boolean @value(true)
      photo_quality_score: Decimal @value(85.5)
    }
  }

  // 外部数据
  external_data: ExternalData {
    // 交警数据
    traffic_police_data: TrafficPoliceData {
      accident_no: Optional[String]
      has_accident_record: Boolean @value(false)
      is_drunk_driving: Boolean @value(false)
      is_fleeing: Boolean @value(false)
      violation_count: Int @value(0)
    }
    
    // 维修记录
    repair_records: List[RepairRecord] {
      has_external_repair_history: Boolean @value(false)
      external_repair_count_12m: Int @value(0)
    }
    
    // 征信数据
    credit_data: CreditData @sensitive {
      credit_score: Int @value(720)
      is_overdue: Boolean @value(false)
    }
  }

  // 历史行为
  historical_patterns: HistoricalPatterns {
    // 被保险人的行为模式
    insured_patterns: InsuredPatterns {
      claim_frequency_12m: Int @value(2)
      claim_frequency_score: Decimal @value(35.0)
      avg_claim_interval_days: Decimal @value(82.0)
      is_regular_pattern: Boolean @value(false)
      usual_repair_shops: List[String] @value(["RS001", "RS003"])
      shop_concentration_score: Decimal @value(65.0)
    }
    
    // 同类案件基准
    benchmark: Benchmark {
      similar_claims_avg_amount: Decimal @value(12500.00)
      amount_deviation_rate: Decimal @value(-0.04)
      similar_claims_avg_parts: Int @value(2)
      parts_deviation: Int @value(0)
    }
  }

  // 图谱特征
  graph_features: GraphFeatures {
    // 关联网络
    connections: Connections {
      same_insured_claims_6m: Int @value(1)
      same_driver_claims_6m: Int @value(1)
      same_vehicle_plate_claims_6m: Int @value(1)
      same_repair_shop_claims_6m: Int @value(8)
      same_location_accidents_6m: Int @value(3)
    }
    
    // 社区检测
    community_risk: CommunityRisk {
      community_id: String @value("COMM-001")
      community_size: Int @value(15)
      community_fraud_rate: Decimal @value(0.12)
      is_high_risk_community: Boolean @value(false)
    }
    
    // 团伙关联
    gang_association: GangAssociation {
      gang_id: Optional[String]
      is_gang_member: Boolean @value(false)
      gang_confidence: Decimal @value(0.0)
      known_associates: List[String] @value([])
    }
  }

  // 欺诈检测
  fraud_detection: FraudDetection {
    // 模型评分
    model_scores: ModelScores {
      gbdt_score: Decimal @value(0.15)
      dnn_score: Decimal @value(0.22)
      graph_score: Decimal @value(0.08)
      ensemble_score: Decimal @value(0.16)
    }
    
    // 风险等级
    risk_level: RiskLevel @value("LOW")
    risk_score: Decimal @value(16.0)
    
    // 触发规则
    triggered_rules: List[TriggeredRule] {
      // 低风险案件无触发规则
    }
    
    // 欺诈类型
    fraud_type: Optional[String]
    fraud_indicators: List[String] @value([])
    
    // 建议处置
    recommendation: Recommendation {
      action: Enum @value("AUTO_APPROVE")
      priority: Enum @value("NORMAL")
      suggested_reserve: Decimal @value(12000.00)
      investigation_budget: Decimal @value(0)
      estimated_fraud_amount: Decimal @value(0)
    }
    
    // 决策解释
    explanation: Explanation {
      summary: String @value("案件风险低，建议自动赔付")
      key_factors: List[String] @value([
        "理赔频率正常（近12个月2次）",
        "出险地点无异常",
        "维修厂合作记录良好",
        "查勘照片完整清晰"
      ])
      similar_cases: List[String] @value(["CLM2024XXXX001", "CLM2024XXXX002"])
    }
  }

  // 处理结果
  processing_result: ProcessingResult {
    status: Enum @value("COMPLETED")
    final_decision: Enum @value("APPROVED")
    approved_amount: Decimal @value(12000.00)
    processing_time_hours: Decimal @value(4.5)
    payment_date: Date @value("2025-01-21")
  }
} @standard("保险理赔反欺诈数据规范") @data_classification("SENSITIVE")
```

---

### 4.6 代码实现

**保险理赔智能反欺诈平台完整实现**：

```python
"""
保险理赔智能反欺诈平台 - 基于DSL Schema的多模态风控系统
支持案件智能审核、团伙识别、欺诈检测、知识图谱分析
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
import hashlib
import networkx as nx
import numpy as np

import redis.asyncio as redis
import asyncpg
from neo4j import AsyncGraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClaimsFraudPlatform")


class ClaimStatus(Enum):
    """理赔状态"""
    PENDING = "待处理"
    UNDER_REVIEW = "审核中"
    INVESTIGATING = "调查中"
    APPROVED = "已审批"
    REJECTED = "已拒赔"
    COMPLETED = "已完成"


class RiskLevel(Enum):
    """风险等级"""
    VERY_LOW = "极低"
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    VERY_HIGH = "极高"


class FraudAction(Enum):
    """处置动作"""
    AUTO_APPROVE = "自动赔付"
    FAST_TRACK = "快速通道"
    STANDARD_REVIEW = "标准审核"
    ENHANCED_REVIEW = "加强审核"
    INVESTIGATE = "调查"
    EXPERT_REVIEW = "专家会审"
    REJECT = "拒赔"


@dataclass
class Location:
    """位置信息"""
    province: str
    city: str
    district: str
    address: str
    longitude: Decimal
    latitude: Decimal


@dataclass
class DamagePart:
    """损坏部件"""
    part_code: str
    part_name: str
    damage_type: str
    part_price: Decimal
    labor_cost: Decimal
    paint_cost: Decimal = Decimal('0')


@dataclass
class RepairShop:
    """维修厂"""
    shop_code: str
    shop_name: str
    shop_rating: Decimal
    is_authorized: bool
    cooperation_years: int
    monthly_claims_avg: int
    fraud_flag_count: int


@dataclass
class ClaimCase:
    """理赔案件实体"""
    claim_no: str
    policy_no: str
    insurance_type: str
    accident_date: datetime
    report_date: datetime
    claim_date: datetime
    accident_location: Location
    accident_description: str
    
    # 损失信息
    estimated_loss: Decimal
    claim_amount: Decimal
    deductible: Decimal
    
    # 当事人
    insured_id_hash: str
    driver_id_hash: str
    driver_license_no: str
    driving_experience_years: int
    
    # 车辆
    vehicle_plate: str
    vin: str
    vehicle_age_months: int
    mileage_km: int
    
    # 维修
    repair_shop: RepairShop
    damage_parts: List[DamagePart]
    
    # 状态
    status: ClaimStatus = ClaimStatus.PENDING
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: Decimal = Decimal('0')
    fraud_probability: Decimal = Decimal('0')
    recommended_action: FraudAction = FraudAction.STANDARD_REVIEW
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self, neo4j_uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(neo4j_uri, auth=(user, password))
    
    async def build_claim_graph(self, claim: ClaimCase):
        """构建案件图谱"""
        async with self.driver.session() as session:
            # 创建案件节点
            await session.run("""
                MERGE (c:Claim {claim_no: $claim_no})
                SET c.claim_amount = $claim_amount,
                    c.accident_date = $accident_date,
                    c.risk_score = $risk_score
            """, claim_no=claim.claim_no, claim_amount=float(claim.claim_amount),
                 accident_date=claim.accident_date.isoformat(),
                 risk_score=float(claim.risk_score))
            
            # 创建被保险人节点
            await session.run("""
                MERGE (i:Insured {id_hash: $insured_id})
                MERGE (c:Claim {claim_no: $claim_no})
                MERGE (i)-[:INSURED_IN]->(c)
            """, insured_id=claim.insured_id_hash, claim_no=claim.claim_no)
            
            # 创建驾驶员节点
            await session.run("""
                MERGE (d:Driver {license_no: $license_no})
                SET d.experience_years = $exp_years
                MERGE (c:Claim {claim_no: $claim_no})
                MERGE (d)-[:DROVE_IN]->(c)
            """, license_no=claim.driver_license_no,
                 exp_years=claim.driving_experience_years,
                 claim_no=claim.claim_no)
            
            # 创建车辆节点
            await session.run("""
                MERGE (v:Vehicle {vin: $vin})
                SET v.plate = $plate,
                    v.age_months = $age
                MERGE (c:Claim {claim_no: $claim_no})
                MERGE (v)-[:INVOLVED_IN]->(c)
            """, vin=claim.vin, plate=claim.vehicle_plate,
                 age=claim.vehicle_age_months, claim_no=claim.claim_no)
            
            # 创建维修厂节点
            await session.run("""
                MERGE (r:RepairShop {code: $shop_code})
                SET r.name = $shop_name,
                    r.fraud_flags = $fraud_flags
                MERGE (c:Claim {claim_no: $claim_no})
                MERGE (c)-[:REPAIRED_AT]->(r)
            """, shop_code=claim.repair_shop.shop_code,
                 shop_name=claim.repair_shop.shop_name,
                 fraud_flags=claim.repair_shop.fraud_flag_count,
                 claim_no=claim.claim_no)
            
            # 创建地点节点
            await session.run("""
                MERGE (l:Location {address: $address})
                SET l.city = $city,
                    l.longitude = $lon,
                    l.latitude = $lat
                MERGE (c:Claim {claim_no: $claim_no})
                MERGE (c)-[:OCCURRED_AT]->(l)
            """, address=claim.accident_location.address,
                 city=claim.accident_location.city,
                 lon=float(claim.accident_location.longitude),
                 lat=float(claim.accident_location.latitude),
                 claim_no=claim.claim_no)
    
    async def detect_communities(self, claim_no: str) -> List[Dict]:
        """检测社区"""
        async with self.driver.session() as session:
            result = await session.run("""
                MATCH (c:Claim {claim_no: $claim_no})-[:INSURED_IN|DROVE_IN|INVOLVED_IN|REPAIRED_AT|OCCURRED_AT]-(n)
                WITH n
                MATCH (n)-[:INSURED_IN|DROVE_IN|INVOLVED_IN|REPAIRED_AT|OCCURRED_AT]-(c2:Claim)
                WITH c2, count(*) as connections
                WHERE connections >= 2
                RETURN c2.claim_no as related_claim, connections
                ORDER BY connections DESC
                LIMIT 10
            """, claim_no=claim_no)
            
            communities = []
            async for record in result:
                communities.append({
                    "related_claim": record["related_claim"],
                    "connection_strength": record["connections"]
                })
            return communities
    
    async def find_gang_patterns(self, claim_no: str) -> Optional[Dict]:
        """查找团伙模式"""
        async with self.driver.session() as session:
            # 查找闭环欺诈模式
            result = await session.run("""
                MATCH (c:Claim {claim_no: $claim_no})-[:REPAIRED_AT]->(r:RepairShop)
                MATCH (r)<-[:REPAIRED_AT]-(c2:Claim)
                MATCH (c2)-[:INSURED_IN]->(i:Insured)
                MATCH (i)-[:INSURED_IN]->(c3:Claim)
                MATCH (c3)-[:OCCURRED_AT]->(l:Location)
                MATCH (l)<-[:OCCURRED_AT]-(c)
                WHERE c2.claim_no <> $claim_no AND c3.claim_no <> $claim_no
                RETURN count(*) as cycle_count
            """, claim_no=claim_no)
            
            record = await result.single()
            if record and record["cycle_count"] > 0:
                return {
                    "gang_pattern": "闭环欺诈",
                    "confidence": min(record["cycle_count"] * 0.2, 1.0),
                    "description": "发现维修厂-被保险人-出险地点闭环关联"
                }
            return None


class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def extract_features(self, claim: ClaimCase) -> Dict[str, float]:
        """提取案件特征"""
        features = {}
        
        # 时间特征
        report_delay = (claim.report_date - claim.accident_date).total_seconds() / 3600
        features["report_delay_hours"] = report_delay
        features["is_night_accident"] = 1 if claim.accident_date.hour < 6 or claim.accident_date.hour > 22 else 0
        features["is_weekend"] = 1 if claim.accident_date.weekday() >= 5 else 0
        
        # 损失特征
        features["claim_amount"] = float(claim.claim_amount)
        features["loss_claim_ratio"] = float(claim.estimated_loss / claim.claim_amount) if claim.claim_amount > 0 else 1
        
        # 驾驶员特征
        features["driving_experience"] = claim.driving_experience_years
        features["is_new_driver"] = 1 if claim.driving_experience_years < 2 else 0
        
        # 车辆特征
        features["vehicle_age_months"] = claim.vehicle_age_months
        features["mileage"] = claim.mileage_km
        features["mileage_per_month"] = claim.mileage_km / max(claim.vehicle_age_months, 1)
        
        # 维修厂特征
        features["shop_rating"] = float(claim.repair_shop.shop_rating)
        features["shop_fraud_flags"] = claim.repair_shop.fraud_flag_count
        features["is_authorized_shop"] = 1 if claim.repair_shop.is_authorized else 0
        
        # 损坏部件特征
        features["damage_parts_count"] = len(claim.damage_parts)
        features["total_parts_cost"] = sum(
            p.part_price + p.labor_cost + p.paint_cost for p in claim.damage_parts
        )
        features["has_expensive_parts"] = 1 if any(
            p.part_price > 5000 for p in claim.damage_parts
        ) else 0
        
        # 历史特征
        historical = await self._get_historical_features(claim)
        features.update(historical)
        
        return features
    
    async def _get_historical_features(self, claim: ClaimCase) -> Dict[str, float]:
        """获取历史特征"""
        features = {}
        
        # 查询历史理赔
        key = f"claims_history:{claim.insured_id_hash}"
        history_data = await self.redis.get(key)
        
        if history_data:
            history = json.loads(history_data)
            features["historical_claims_12m"] = history.get("claims_12m", 0)
            features["historical_amount_12m"] = history.get("amount_12m", 0)
            features["days_since_last_claim"] = history.get("days_since_last", 365)
        else:
            features["historical_claims_12m"] = 0
            features["historical_amount_12m"] = 0
            features["days_since_last_claim"] = 365
        
        return features


class FraudDetectionModel:
    """欺诈检测模型"""
    
    def __init__(self):
        self.models = self._load_models()
    
    def _load_models(self) -> Dict:
        """加载模型"""
        return {
            "gbdt": None,  # lgb.Booster()
            "dnn": None,   # tf.keras.models.load_model()
            "graph": None  # GraphSAGE model
        }
    
    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """预测欺诈概率"""
        # GBDT预测
        gbdt_score = self._gbdt_predict(features)
        
        # DNN预测
        dnn_score = self._dnn_predict(features)
        
        # 图模型预测
        graph_score = self._graph_predict(features)
        
        # 集成评分
        ensemble = 0.5 * gbdt_score + 0.3 * dnn_score + 0.2 * graph_score
        
        return {
            "gbdt_score": gbdt_score,
            "dnn_score": dnn_score,
            "graph_score": graph_score,
            "ensemble_score": ensemble
        }
    
    def _gbdt_predict(self, features: Dict[str, float]) -> float:
        """GBDT预测"""
        # 模拟预测逻辑
        score = 0.1
        
        # 高风险特征
        if features.get("shop_fraud_flags", 0) > 0:
            score += 0.3
        if features.get("historical_claims_12m", 0) > 3:
            score += 0.2
        if features.get("is_new_driver", 0) == 1 and features.get("claim_amount", 0) > 10000:
            score += 0.15
        if features.get("report_delay_hours", 0) > 48:
            score += 0.1
        
        return min(score, 1.0)
    
    def _dnn_predict(self, features: Dict[str, float]) -> float:
        """DNN预测"""
        # 模拟预测
        return 0.15
    
    def _graph_predict(self, features: Dict[str, float]) -> float:
        """图模型预测"""
        # 模拟预测
        return 0.08


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict]:
        """加载规则"""
        return [
            {
                "rule_id": "FR001",
                "name": "高风险维修厂",
                "condition": lambda f: f.get("shop_fraud_flags", 0) >= 3,
                "score": 40,
                "action": FraudAction.INVESTIGATE,
                "explanation": "维修厂存在多起欺诈嫌疑记录"
            },
            {
                "rule_id": "FR002",
                "name": "高频理赔",
                "condition": lambda f: f.get("historical_claims_12m", 0) >= 5,
                "score": 35,
                "action": FraudAction.ENHANCED_REVIEW,
                "explanation": "近12个月理赔次数超过5次"
            },
            {
                "rule_id": "FR003",
                "name": "新驾驶员高额理赔",
                "condition": lambda f: f.get("is_new_driver", 0) == 1 and f.get("claim_amount", 0) > 20000,
                "score": 30,
                "action": FraudAction.INVESTIGATE,
                "explanation": "驾龄不足2年，理赔金额超过2万元"
            },
            {
                "rule_id": "FR004",
                "name": "延迟报案",
                "condition": lambda f: f.get("report_delay_hours", 0) > 72,
                "score": 25,
                "action": FraudAction.ENHANCED_REVIEW,
                "explanation": "出险后超过72小时报案"
            },
            {
                "rule_id": "FR005",
                "name": "异常损失比例",
                "condition": lambda f: f.get("loss_claim_ratio", 1) > 1.2,
                "score": 20,
                "action": FraudAction.STANDARD_REVIEW,
                "explanation": "定损金额超过索赔金额20%"
            }
        ]
    
    def evaluate(self, features: Dict[str, float]) -> Tuple[List[Dict], int, FraudAction]:
        """评估规则"""
        triggered = []
        total_score = 0
        max_action_priority = 0
        final_action = FraudAction.AUTO_APPROVE
        
        action_priority = {
            FraudAction.AUTO_APPROVE: 1,
            FraudAction.FAST_TRACK: 2,
            FraudAction.STANDARD_REVIEW: 3,
            FraudAction.ENHANCED_REVIEW: 4,
            FraudAction.INVESTIGATE: 5,
            FraudAction.EXPERT_REVIEW: 6,
            FraudAction.REJECT: 7
        }
        
        for rule in self.rules:
            try:
                if rule["condition"](features):
                    triggered.append({
                        "rule_id": rule["rule_id"],
                        "rule_name": rule["name"],
                        "explanation": rule["explanation"]
                    })
                    total_score += rule["score"]
                    
                    action = rule["action"]
                    priority = action_priority.get(action, 0)
                    if priority > max_action_priority:
                        max_action_priority = priority
                        final_action = action
            except Exception as e:
                logger.error(f"规则 {rule['rule_id']} 执行失败: {e}")
        
        return triggered, total_score, final_action


class ClaimsFraudPlatform:
    """理赔反欺诈平台主类"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.graph_builder: Optional[KnowledgeGraphBuilder] = None
        self.feature_extractor: Optional[FeatureExtractor] = None
        self.fraud_model = FraudDetectionModel()
        self.rule_engine = RuleEngine()
        
        # 统计
        self.stats = {
            "total_claims": 0,
            "auto_approved": 0,
            "investigated": 0,
            "rejected": 0,
            "fraud_detected": 0,
            "avg_processing_time": 0
        }
    
    async def initialize(self):
        """初始化平台"""
        self.redis_client = redis.Redis(
            host='localhost', port=6379, db=3, decode_responses=True
        )
        self.db_pool = await asyncpg.create_pool(
            host='localhost', port=5432,
            user='admin', password='admin',
            database='claims_fraud'
        )
        self.graph_builder = KnowledgeGraphBuilder(
            "bolt://localhost:7687", "neo4j", "password"
        )
        self.feature_extractor = FeatureExtractor(self.redis_client)
        logger.info("理赔反欺诈平台初始化完成")
    
    async def process_claim(self, claim_data: Dict) -> Dict:
        """处理理赔案件"""
        start_time = time.time()
        
        try:
            # 1. 构建案件实体
            claim = self._build_claim_entity(claim_data)
            
            # 2. 特征提取
            features = await self.feature_extractor.extract_features(claim)
            
            # 3. 模型预测
            model_scores = self.fraud_model.predict(features)
            
            # 4. 规则评估
            triggered_rules, rule_score, action = self.rule_engine.evaluate(features)
            
            # 5. 知识图谱分析
            await self.graph_builder.build_claim_graph(claim)
            communities = await self.graph_builder.detect_communities(claim.claim_no)
            gang_pattern = await self.graph_builder.find_gang_patterns(claim.claim_no)
            
            # 6. 综合评分
            graph_bonus = 0.1 if gang_pattern else 0
            final_score = model_scores["ensemble_score"] * 100 + rule_score + graph_bonus * 100
            final_score = min(final_score, 100)
            
            # 7. 确定风险等级
            risk_level = self._determine_risk_level(final_score)
            
            # 8. 调整处置建议
            if gang_pattern:
                action = FraudAction.INVESTIGATE
            
            # 9. 构建结果
            processing_time = time.time() - start_time
            
            result = {
                "claim_no": claim.claim_no,
                "risk_score": round(final_score, 2),
                "risk_level": risk_level.value,
                "fraud_probability": round(model_scores["ensemble_score"], 4),
                "recommended_action": action.value,
                "model_scores": model_scores,
                "triggered_rules": triggered_rules,
                "community_info": {
                    "related_claims": len(communities),
                    "top_connections": communities[:3]
                },
                "gang_analysis": gang_pattern,
                "explanation": self._generate_explanation(final_score, triggered_rules, gang_pattern),
                "processing_time_ms": int(processing_time * 1000)
            }
            
            # 10. 更新统计
            await self._update_stats(action, processing_time)
            
            # 11. 存储结果
            await self._store_result(claim, result)
            
            logger.info(f"案件处理完成: claim_no={claim.claim_no}, "
                       f"risk_score={final_score}, action={action.value}")
            
            return result
            
        except Exception as e:
            logger.error(f"案件处理失败: {e}")
            return {"error": str(e), "claim_no": claim_data.get("claim_no")}
    
    def _build_claim_entity(self, data: Dict) -> ClaimCase:
        """构建案件实体"""
        location_data = data.get("accident_location", {})
        location = Location(
            province=location_data.get("province", ""),
            city=location_data.get("city", ""),
            district=location_data.get("district", ""),
            address=location_data.get("address", ""),
            longitude=Decimal(str(location_data.get("longitude", 0))),
            latitude=Decimal(str(location_data.get("latitude", 0)))
        )
        
        repair_data = data.get("repair_info", {}).get("repair_shop", {})
        repair_shop = RepairShop(
            shop_code=repair_data.get("shop_code", ""),
            shop_name=repair_data.get("shop_name", ""),
            shop_rating=Decimal(str(repair_data.get("shop_rating", 0))),
            is_authorized=repair_data.get("is_authorized", False),
            cooperation_years=repair_data.get("cooperation_years", 0),
            monthly_claims_avg=repair_data.get("monthly_claims_avg", 0),
            fraud_flag_count=repair_data.get("fraud_flag_count", 0)
        )
        
        damage_parts = []
        for part_data in data.get("repair_info", {}).get("damage_parts", []):
            damage_parts.append(DamagePart(
                part_code=part_data.get("part_code", ""),
                part_name=part_data.get("part_name", ""),
                damage_type=part_data.get("damage_type", ""),
                part_price=Decimal(str(part_data.get("part_price", 0))),
                labor_cost=Decimal(str(part_data.get("labor_cost", 0))),
                paint_cost=Decimal(str(part_data.get("paint_cost", 0)))
            ))
        
        return ClaimCase(
            claim_no=data.get("claim_no", ""),
            policy_no=data.get("policy_no", ""),
            insurance_type=data.get("insurance_type", ""),
            accident_date=datetime.fromisoformat(data.get("accident_date", "")),
            report_date=datetime.fromisoformat(data.get("report_date", "")),
            claim_date=datetime.fromisoformat(data.get("claim_date", "")),
            accident_location=location,
            accident_description=data.get("accident_description", ""),
            estimated_loss=Decimal(str(data.get("estimated_loss", 0))),
            claim_amount=Decimal(str(data.get("claim_amount", 0))),
            deductible=Decimal(str(data.get("deductible", 0))),
            insured_id_hash=data.get("parties", {}).get("insured", {}).get("id_hash", ""),
            driver_id_hash=data.get("parties", {}).get("driver", {}).get("id_hash", ""),
            driver_license_no=data.get("parties", {}).get("driver", {}).get("license_no", ""),
            driving_experience_years=data.get("parties", {}).get("insured", {}).get("driving_experience_years", 0),
            vehicle_plate=data.get("vehicle_info", {}).get("vehicle_plate", ""),
            vin=data.get("vehicle_info", {}).get("vin", ""),
            vehicle_age_months=data.get("vehicle_info", {}).get("vehicle_age_months", 0),
            mileage_km=data.get("vehicle_info", {}).get("mileage_km", 0),
            repair_shop=repair_shop,
            damage_parts=damage_parts
        )
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """确定风险等级"""
        if score < 20:
            return RiskLevel.VERY_LOW
        elif score < 40:
            return RiskLevel.LOW
        elif score < 60:
            return RiskLevel.MEDIUM
        elif score < 80:
            return RiskLevel.HIGH
        return RiskLevel.VERY_HIGH
    
    def _generate_explanation(self, score: float, rules: List[Dict], gang: Optional[Dict]) -> str:
        """生成解释"""
        if gang:
            return f"发现疑似团伙欺诈模式: {gang['description']}"
        
        if score >= 60:
            rule_names = [r["rule_name"] for r in rules[:3]]
            return f"触发欺诈规则: {', '.join(rule_names)}"
        elif score >= 40:
            return "存在一定风险因素，建议加强审核"
        elif score >= 20:
            return "风险可控，可按标准流程处理"
        return "未发现明显风险，建议自动赔付"
    
    async def _update_stats(self, action: FraudAction, processing_time: float):
        """更新统计"""
        self.stats["total_claims"] += 1
        
        if action in [FraudAction.AUTO_APPROVE, FraudAction.FAST_TRACK]:
            self.stats["auto_approved"] += 1
        elif action in [FraudAction.INVESTIGATE, FraudAction.EXPERT_REVIEW]:
            self.stats["investigated"] += 1
        elif action == FraudAction.REJECT:
            self.stats["rejected"] += 1
        
        if action in [FraudAction.INVESTIGATE, FraudAction.EXPERT_REVIEW, FraudAction.REJECT]:
            self.stats["fraud_detected"] += 1
        
        # 更新平均处理时间
        n = self.stats["total_claims"]
        self.stats["avg_processing_time"] = (
            (self.stats["avg_processing_time"] * (n - 1) + processing_time) / n
        )
    
    async def _store_result(self, claim: ClaimCase, result: Dict):
        """存储结果"""
        key = f"claim_result:{claim.claim_no}"
        await self.redis_client.setex(key, 86400 * 30, json.dumps(result))
    
    def get_stats(self) -> Dict:
        """获取统计"""
        total = self.stats["total_claims"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "auto_approval_rate": round(self.stats["auto_approved"] / total * 100, 2),
            "investigation_rate": round(self.stats["investigated"] / total * 100, 2),
            "fraud_detection_rate": round(self.stats["fraud_detected"] / total * 100, 2),
            "avg_processing_time_ms": round(self.stats["avg_processing_time"] * 1000, 2)
        }


# 使用示例
async def main():
    """主函数 - 演示理赔反欺诈平台"""
    platform = ClaimsFraudPlatform()
    await platform.initialize()
    
    # 构造理赔案件
    claim_data = {
        "claim_no": "CLM20250121000001",
        "policy_no": "POL2025000001",
        "insurance_type": "AUTO",
        "accident_date": "2025-01-20T15:30:00",
        "report_date": "2025-01-20T16:45:00",
        "claim_date": "2025-01-21T09:00:00",
        "accident_location": {
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "address": "深南大道XX路段",
            "longitude": 113.9433,
            "latitude": 22.5233
        },
        "accident_description": "两车追尾，本车车头受损",
        "estimated_loss": 15000,
        "claim_amount": 12000,
        "deductible": 1000,
        "parties": {
            "insured": {
                "id_hash": "HASH-insured001",
                "driving_experience_years": 10
            },
            "driver": {
                "id_hash": "HASH-driver001",
                "license_no": "HASH-license001"
            }
        },
        "vehicle_info": {
            "vehicle_plate": "粤A-XXXXX",
            "vin": "LSVXXXXXXXXXXXXXX",
            "vehicle_age_months": 31,
            "mileage_km": 45000
        },
        "repair_info": {
            "repair_shop": {
                "shop_code": "RS001",
                "shop_name": "XX汽车维修中心",
                "shop_rating": 4.2,
                "is_authorized": True,
                "cooperation_years": 3,
                "monthly_claims_avg": 45,
                "fraud_flag_count": 0
            },
            "damage_parts": [
                {
                    "part_code": "BUMPER_FRONT",
                    "part_name": "前保险杠",
                    "damage_type": "REPLACE",
                    "part_price": 2800,
                    "labor_cost": 500,
                    "paint_cost": 800
                },
                {
                    "part_code": "HEADLIGHT_LEFT",
                    "part_name": "左前大灯",
                    "damage_type": "REPLACE",
                    "part_price": 3500,
                    "labor_cost": 300
                }
            ]
        }
    }
    
    # 处理案件
    result = await platform.process_claim(claim_data)
    print(f"案件处理结果:")
    print(f"  风险评分: {result.get('risk_score')}")
    print(f"  风险等级: {result.get('risk_level')}")
    print(f"  欺诈概率: {result.get('fraud_probability')}")
    print(f"  建议处置: {result.get('recommended_action')}")
    print(f"  处理耗时: {result.get('processing_time_ms')}ms")
    print(f"  决策解释: {result.get('explanation')}")
    
    print(f"\n平台统计: {json.dumps(platform.get_stats(), ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
```


### 4.7 效果评估

#### 4.7.1 性能指标对比

| 指标类别 | 指标项 | 建设前 | 建设后 | 提升幅度 |
|----------|--------|--------|--------|----------|
| **欺诈识别** | 欺诈案件识别率 | 35% | 89% | **提升54%** |
| | 团伙欺诈发现率 | 15% | 82% | **提升67%** |
| | 误报率 | 25% | 4.5% | **降低82%** |
| | 欺诈损失率 | 5.2% | 1.8% | **降低65%** |
| **审核效率** | 案件处理时效 | 5天 | 8小时 | **缩短93%** |
| | 自动审核占比 | 20% | 75% | **提升55%** |
| | 人工审核工作量 | 100% | 25% | **降低75%** |
| | 调查案件精准度 | 40% | 85% | **提升45%** |
| **成本节约** | 调查成本 | ¥3,000/案 | ¥1,200/案 | **降低60%** |
| | 审核人力成本 | 基准 | -45% | **降低45%** |
| | 单案处理成本 | ¥450 | ¥180 | **降低60%** |
| **系统能力** | 日处理案件量 | 5,000件 | 25,000件 | **提升5倍** |
| | 峰值处理能力 | 8,000件/日 | 50,000件/日 | **提升5.25倍** |
| | 图谱查询响应 | 3秒 | 200ms | **提升93%** |
| **业务价值** | 年度欺诈损失 | ¥15亿 | ¥5.2亿 | **减少65%** |
| | 挽回损失金额 | 基准 | +¥9.8亿/年 | **新增** |

#### 4.7.2 业务价值评估

| 价值维度 | 具体收益 | 量化指标 | ROI计算 |
|----------|----------|----------|---------|
| **欺诈损失挽回** | 欺诈识别率提升带来的赔付减少 | 年度挽回：¥9.8亿 | 3年累计：¥29.4亿 |
| **调查成本节约** | 精准调查减少无效调查投入 | 年度节约：¥6,500万 | 3年累计：¥1.95亿 |
| **运营效率提升** | 自动化审核带来的人力成本节约 | 年度节约：¥4,200万 | 3年累计：¥1.26亿 |
| **客户体验提升** | 审核时效提升带来的客户满意度增长 | NPS提升15分 | 品牌价值提升¥8亿 |
| **合规价值** | 满足监管反欺诈要求，避免合规风险 | 监管评价优秀 | 避免潜在罚款¥5,000万 |

**总投资回报率（ROI）**：
- 项目总投资：¥1.2亿（含平台建设、模型开发、知识图谱构建、数据采购）
- 首年收益：¥15.7亿
- 3年累计收益：¥41.11亿
- **3年ROI = 3,426%**
- **投资回收期 = 1个月**

#### 4.7.3 经验教训

**成功经验**：

1. **知识图谱价值巨大**：构建的理赔知识图谱包含500万+节点、2,000万+关系，成功识别出120+个骗保团伙，涉及案件超过3,000件，预计挽回损失¥4.5亿。图谱分析使团伙欺诈发现率从15%提升至82%。

2. **多模型融合策略**：采用GBDT+DNN+图神经网络的三模型融合，各模型捕捉不同类型的欺诈模式。融合模型AUC达到0.94，显著优于单一模型（AUC 0.82-0.87）。

3. **主动学习机制**：建立"模型预测-人工标注-模型更新"闭环，每日从预测案件中抽样人工复核，持续丰富训练样本。3个月内训练样本量从10万增至50万，模型效果提升12%。

**教训与改进**：

1. **数据质量瓶颈**：初期外部数据（交警、医院）接入困难，数据质量差，影响模型效果。改进：建立数据质量SLA，与数据提供方签署质量协议，数据问题响应时效<24小时。

2. **模型可解释性挑战**：业务人员对"黑盒"模型决策存疑，影响落地推广。改进：引入SHAP值解释和规则归因，为每笔高风险案件生成"欺诈证据链"，包括涉及的实体、关系、规则，业务接受度从50%提升至95%。

3. **正负样本极度失衡**：欺诈样本占比<1%，初期模型倾向于预测正常。改进：采用SMOTE+ADASYN混合采样，结合代价敏感学习（欺诈样本权重10倍），模型召回率从45%提升至89%。

**行业贡献**：

该平台已与行业反欺诈联盟对接，共享欺诈情报和团伙特征，累计输出欺诈线索超过2,000条，协助同业识别欺诈案件超过5,000件，为行业反欺诈协作树立了标杆。其知识图谱Schema标准已被中国保险行业协会采纳，正在全行业推广。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21  
**最后更新**：2025-01-21
