# 保险业务Schema形式化定义

## 📑 目录

- [保险业务Schema形式化定义](#保险业务schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 保单Schema](#2-保单schema)
  - [3. 理赔Schema](#3-理赔schema)
  - [4. 精算模型定义](#4-精算模型定义)
  - [5. 再保险Schema](#5-再保险schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 保单一致性定理](#91-保单一致性定理)
    - [9.2 理赔完备性定理](#92-理赔完备性定理)
    - [9.3 准备金充足性定理](#93-准备金充足性定理)
  - [10. 数学模型](#10-数学模型)
    - [10.1 保单状态机](#101-保单状态机)
    - [10.2 理赔状态机](#102-理赔状态机)
    - [10.3 精算计算模型](#103-精算计算模型)

---

## 1. 形式化模型

**定义1（保险业务Schema）**：
保险业务Schema是一个六元组：

```text
Insurance_Schema = (Policy, Claim, Actuarial, Reinsurance, Customer, Product)
```

其中：

- `Policy`：保单Schema
- `Claim`：理赔Schema
- `Actuarial`：精算模型Schema
- `Reinsurance`：再保险Schema
- `Customer`：客户信息Schema
- `Product`：产品定义Schema

**形式化定义**：

$$
\mathcal{I} = \langle P, C, A, R, U, D, \Sigma, \Phi \rangle
$$

其中：

- $\mathcal{I}$：保险业务Schema
- $P$：保单实体集合
- $C$：理赔实体集合
- $A$：精算计算集合
- $R$：再保险合约集合
- $U$：客户实体集合
- $D$：产品定义集合
- $\Sigma$：状态转移函数
- $\Phi$：约束规则集合

---

## 2. 保单Schema

**定义2（保单Schema）**：

```text
Policy_Schema = (Policy_Basic × Policy_Coverage × Policy_Premium × Policy_Parties)
```

**形式化DSL定义**：

```dsl
schema InsurancePolicy {
  // 保单基本信息
  policy_basic: PolicyBasic {
    policy_id: String(30) @required @unique
    policy_number: String(30) @required @unique
    proposal_number: String(30) @required

    // 产品信息
    product_code: String(20) @required
    product_name: String(200) @required
    product_type: Enum {
      TERM_LIFE,          // 定期寿险
      WHOLE_LIFE,         // 终身寿险
      ENDOWMENT,          // 两全保险
      ANNUITY,            // 年金保险
      UL,                 // 万能寿险
      VARIABLE_LIFE,      // 投连险
      PARTICIPATING,      // 分红险
      MOTOR,              // 机动车辆保险
      PROPERTY,           // 财产保险
      LIABILITY,          // 责任保险
      HEALTH,             // 健康保险
      ACCIDENT,           // 意外伤害保险
      GROUP_LIFE,         // 团体寿险
      GROUP_HEALTH        // 团体健康险
    } @required

    // 保险期间
    policy_term: Integer @required @min(1) @max(100)  // 年
    policy_term_unit: Enum { YEARS, MONTHS, DAYS } @default("YEARS")
    effective_date: Date @required
    expiry_date: Date @required

    // 保单状态
    policy_status: Enum {
      PROPOSAL,           // 投保单
      UNDERWRITING,       // 核保中
      INFORCE,            // 有效
      PAID_UP,            // 交清
      LAPSED,             // 失效
      REINSTATED,         // 复效
      MATURED,            // 满期
      TERMINATED,         // 终止
      SURRENDERED,        // 退保
      CLAIMED             // 理赔终止
    } @required

    // 销售信息
    channel_type: Enum {
      AGENT,              // 个人代理
      BROKER,             // 保险经纪
      BANK,               // 银行保险
      DIRECT,             // 直销
      GROUP,              // 团体渠道
      ONLINE,             // 网销
      TELESALES           // 电销
    } @required
    sales_code: String(20)?
    organization_code: String(20) @required

    // 系统信息
    issue_date: Date @required
    input_date: DateTime @required
    last_modified: DateTime @required
    version: Integer @default(1)
  }

  // 保险责任
  policy_coverage: PolicyCoverage {
    coverage_id: String(30) @required @unique
    policy_id: String(30) @required @reference(PolicyBasic.policy_id)

    // 险种代码
    coverage_code: String(10) @required
    coverage_name: String(100) @required
    coverage_type: Enum { MAIN, RIDER } @required

    // 保额与保费
    sum_assured: Decimal(15,2) @required @min(0)
    premium: Decimal(12,2) @required @min(0)
    premium_frequency: Enum {
      SINGLE,             // 趸缴
      ANNUAL,             // 年缴
      SEMI_ANNUAL,        // 半年缴
      QUARTERLY,          // 季缴
      MONTHLY             // 月缴
    } @required

    // 缴费期间
    premium_term: Integer @required @min(0)
    premium_term_unit: Enum { YEARS, MONTHS, SINGLE } @default("YEARS")

    // 责任期间
    coverage_start_date: Date @required
    coverage_end_date: Date @required

    // 等待期与免责期
    waiting_period_days: Integer @default(0)
    survival_period_days: Integer @default(0)

    // 状态
    status: Enum { ACTIVE, EXPIRED, CANCELLED } @required

    // 特殊条款
    exclusions: List<String(500)>?
    special_clauses: List<String(500)>?
  }

  // 保费信息
  premium_info: PremiumInfo {
    premium_id: String(30) @required @unique
    policy_id: String(30) @required
    coverage_id: String(30) @required

    // 保费构成
    base_premium: Decimal(12,2) @required @min(0)
    risk_premium: Decimal(12,2) @required @min(0)
    savings_premium: Decimal(12,2) @default(0)
    cost_premium: Decimal(12,2) @default(0)
    total_premium: Decimal(12,2) @required @min(0)

    // 已缴保费
    total_paid_premium: Decimal(15,2) @default(0)
    total_paid_periods: Integer @default(0)
    next_due_date: Date?
    next_due_amount: Decimal(12,2)?

    // 缴费状态
    payment_status: Enum {
      PAID,               // 已缴
      DUE,                // 到期
      GRACE,              // 宽限期
      OVERDUE             // 逾期
    } @required

    // 账户价值（适用于万能/投连）
    account_value: Decimal(15,2) @default(0)
    cash_value: Decimal(15,2) @default(0)
  }

  // 保单当事人
  policy_parties: PolicyParties {
    // 投保人
    policyholder: Party {
      party_id: String(20) @required
      party_type: Enum { INDIVIDUAL, CORPORATE } @required
      name: String(140) @required
      identification_type: Enum { ID_CARD, PASSPORT, BUSINESS_LICENSE } @required
      identification_number: String(50) @required
      date_of_birth: Date?
      gender: Enum { MALE, FEMALE }?
      occupation_code: String(10)?
      annual_income: Decimal(15,2)?

      contact_info: ContactInformation {
        phone: String(20) @required
        email: String(254)?
        address: PostalAddress @required
      }

      risk_rating: Enum { STANDARD, SUBSTANDARD, DECLINED } @default("STANDARD")
    }

    // 被保险人
    insured: Party {
      party_id: String(20) @required
      name: String(140) @required
      relationship_to_policyholder: Enum {
        SELF,               // 本人
        SPOUSE,             // 配偶
        CHILD,              // 子女
        PARENT,             // 父母
        OTHER               // 其他
      } @required
      date_of_birth: Date @required
      gender: Enum { MALE, FEMALE } @required
      identification_type: Enum { ID_CARD, PASSPORT, BIRTH_CERT } @required
      identification_number: String(50) @required
      occupation_code: String(10)?
      health_declaration: List<HealthQuestion>?
    }

    // 受益人
    beneficiaries: List<Beneficiary> {
      beneficiary_id: String(20) @required
      name: String(140) @required
      relationship_to_insured: Enum {
        SELF,
        SPOUSE,
        CHILD,
        PARENT,
        SIBLING,
        OTHER
      } @required
      beneficiary_type: Enum { PRIMARY, CONTINGENT } @required
      share_percentage: Decimal(5,2) @required @min(0) @max(100)
      identification_type: Enum { ID_CARD, PASSPORT }?
      identification_number: String(50)?
      is_estate: Boolean @default(false)
    }
  }
} @domain("INSURANCE") @version("1.0")
```

**保单数学模型**：

**现金价值计算**：

$$
CV_t = \sum_{k=t}^{n} P_k^s \cdot v^{k-t} - \sum_{k=t}^{n} E_k \cdot v^{k-t}
$$

其中：

- $CV_t$：第t年的现金价值
- $P_k^s$：第k年的储蓄保费
- $E_k$：第k年的费用支出
- $v = \frac{1}{1+i}$：折现因子
- $i$：评估利率

---

## 3. 理赔Schema

**定义3（理赔Schema）**：

```text
Claim_Schema = (Claim_Basic × Claim_Assessment × Claim_Settlement × Claim_Payment)
```

**形式化DSL定义**：

```dsl
schema InsuranceClaim {
  // 理赔基本信息
  claim_basic: ClaimBasic {
    claim_id: String(30) @required @unique
    claim_number: String(30) @required @unique
    policy_id: String(30) @required @reference(Policy.policy_id)
    coverage_id: String(30) @required

    // 出险信息
    date_of_loss: Date @required
    time_of_loss: Time?
    place_of_loss: String(200) @required
    cause_of_loss: String(500) @required
    loss_description: String(1000) @required

    // 报案信息
    reported_date: DateTime @required
    reported_by: String(140) @required
    reporter_phone: String(20) @required
    report_channel: Enum {
      PHONE,
      MOBILE_APP,
      WECHAT,
      WEBSITE,
      AGENT,
      EMAIL
    } @required

    // 事故类型
    incident_type: Enum {
      DEATH,              // 死亡
      DISABILITY,         // 残疾
      ILLNESS,            // 疾病
      ACCIDENT,           // 意外
      MEDICAL,            // 医疗
      PROPERTY_DAMAGE,    // 财产损失
      LIABILITY,          // 责任
      OTHER
    } @required

    // 理赔类型
    claim_type: Enum {
      DEATH_BENEFIT,      // 身故保险金
      MATURITY_BENEFIT,   // 满期保险金
      SURVIVAL_BENEFIT,   // 生存保险金
      DISABILITY_BENEFIT, // 残疾保险金
      ILLNESS_BENEFIT,    // 疾病保险金
      MEDICAL_REIMBURSE,  // 医疗费用报销
      SURRENDER,          // 退保金
      POLICY_LOAN         // 保单贷款
    } @required

    // 理赔状态
    claim_status: Enum {
      REGISTERED,         // 已登记
      UNDER_INVESTIGATION,// 查勘中
      DOCUMENT_PENDING,   // 待补充资料
      UNDER_ASSESSMENT,   // 理算中
      PENDING_APPROVAL,   // 待审批
      APPROVED,           // 已审批
      REJECTED,           // 已拒赔
      WITHDRAWN,          // 已撤案
      PAYMENT_PENDING,    // 待付款
      PAID,               // 已赔付
      CLOSED              // 已结案
    } @required

    // 分配信息
    assigned_adjuster: String(50)?
    assigned_surveyor: String(50)?
    assigned_branch: String(20) @required

    // 时间戳
    created_at: DateTime @required
    updated_at: DateTime @required
    closed_at: DateTime?
  }

  // 理赔查勘
  claim_assessment: ClaimAssessment {
    assessment_id: String(30) @required @unique
    claim_id: String(30) @required

    // 查勘信息
    survey_date: Date?
    surveyor_name: String(50)?
    survey_report: String(2000)?
    survey_findings: List<SurveyFinding>?

    // 损失评估
    loss_assessment: LossAssessment {
      assessed_amount: Decimal(15,2) @required
      assessment_currency: String(3) @required
      assessment_basis: Enum {
        INVOICE,            // 发票
        MARKET_VALUE,       // 市场价值
        REPLACEMENT_COST,   // 重置成本
        DEPRECIATED_VALUE,  // 折旧价值
        AGREED_VALUE        // 协议价值
      } @required
      depreciation_rate: Decimal(5,2) @default(0)
      salvage_value: Decimal(15,2) @default(0)
      deductible: Decimal(15,2) @default(0)

      // 损失明细
      loss_items: List<LossItem> {
        item_id: String(20) @required
        item_description: String(200) @required
        quantity: Decimal(10,2) @required
        unit_price: Decimal(12,2) @required
        assessed_amount: Decimal(15,2) @required
        remarks: String(200)?
      }
    }

    // 责任认定
    liability_assessment: LiabilityAssessment {
      is_liability_accepted: Boolean @required
      liability_percentage: Decimal(5,2) @default(100)
      rejection_reason: String(500)?
      policy_applicable: Boolean @required
      exclusion_applicable: Boolean @default(false)
      exclusion_clauses: List<String(50)>?
    }

    assessment_date: DateTime @required
    assessor: String(50) @required
  }

  // 理赔理算
  claim_calculation: ClaimCalculation {
    calculation_id: String(30) @required @unique
    claim_id: String(30) @required

    // 理算金额
    gross_claim_amount: Decimal(15,2) @required @min(0)
    deductible_amount: Decimal(15,2) @default(0)
    depreciation_amount: Decimal(15,2) @default(0)
    salvage_recovery: Decimal(15,2) @default(0)
    subrogation_recovery: Decimal(15,2) @default(0)
    previous_payments: Decimal(15,2) @default(0)

    // 净赔付额
    net_claim_amount: Decimal(15,2) @required @min(0)
    interest_amount: Decimal(15,2) @default(0)
    total_payable_amount: Decimal(15,2) @required @min(0)

    // 理算明细
    calculation_details: List<CalculationDetail> {
      coverage_code: String(10) @required
      benefit_type: String(30) @required
      claimed_amount: Decimal(15,2) @required
      approved_amount: Decimal(15,2) @required
      deduction_reason: String(200)?
    }

    calculation_date: DateTime @required
    calculator: String(50) @required
  }

  // 理赔支付
  claim_payment: ClaimPayment {
    payment_id: String(30) @required @unique
    claim_id: String(30) @required
    calculation_id: String(30) @required

    // 支付金额
    payment_amount: Decimal(15,2) @required @min(0)
    payment_currency: String(3) @required
    payment_type: Enum {
      CLAIM_PAYMENT,      // 理赔款
      EXPENSE_PAYMENT,    // 费用
      RECOVERY            // 追偿款
    } @required

    // 收款人信息
    payee: Payee {
      payee_type: Enum { INSURED, BENEFICIARY, THIRD_PARTY, PROVIDER } @required
      payee_name: String(140) @required
      payee_account: AccountIdentification @required
      payee_bank: FinancialInstitution?
      identification_number: String(50)?
    }

    // 支付方式
    payment_method: Enum {
      BANK_TRANSFER,      // 银行转账
      CHECK,              // 支票
      CASH,               // 现金
      OFFSET              // 冲抵
    } @required

    // 支付状态
    payment_status: Enum {
      PENDING,
      PROCESSING,
      COMPLETED,
      FAILED,
      CANCELLED
    } @required

    // 时间戳
    requested_date: DateTime @required
    processed_date: DateTime?
    completed_date: DateTime?

    // 支付凭证
    payment_reference: String(35)?
    bank_reference: String(35)?
  }

  // 理赔文档
  claim_documents: List<ClaimDocument> {
    document_id: String(30) @required @unique
    claim_id: String(30) @required
    document_type: Enum {
      CLAIM_FORM,         // 理赔申请书
      POLICY_COPY,        // 保单复印件
      ID_PROOF,           // 身份证明
      MEDICAL_RECORD,     // 医疗记录
      DEATH_CERT,         // 死亡证明
      POLICE_REPORT,      // 警方报告
      INVOICE,            // 发票
      PHOTO,              // 照片
      OTHER
    } @required
    document_name: String(100) @required
    file_path: String(500) @required
    file_size: Integer @required
    uploaded_by: String(50) @required
    uploaded_at: DateTime @required
    verified: Boolean @default(false)
    verified_by: String(50)?
    verified_at: DateTime?
  }
} @domain("INSURANCE") @version("1.0")
```

**理赔金额计算**：

$$
\text{Net Claim} = \text{Gross Claim} - \text{Deductible} - \text{Depreciation} + \text{Interest}
$$

$$
\text{Total Payable} = \text{Net Claim} - \text{Previous Payments} - \text{Recoveries}
$$

---

## 4. 精算模型定义

**定义4（精算模型Schema）**：

```text
Actuarial_Schema = (Reserving_Model × Pricing_Model × Valuation_Model)
```

**形式化DSL定义**：

```dsl
schema ActuarialModel {
  // 准备金模型
  reserving_model: ReservingModel {
    model_id: String(30) @required @unique
    model_name: String(100) @required
    model_type: Enum {
      CHAIN_LADDER,       // 链梯法
      BORNHUETTER_FERGUSON, // BF法
      AVERAGE_COST,       // 案均法
      LOSS_RATIO,         // 赔付率法
      GENERALIZED_LINEAR, // GLM
      BOOTSTRAP,          // Bootstrap
      MACK,               // Mack法
      STOCHASTIC          // 随机模型
    } @required

    // 数据三角形
    triangle_data: TriangleData {
      origin_periods: List<String(20)> @required  // 事故年/季/月
      development_periods: List<String(20)> @required  // 进展年/季/月
      cumulative: Boolean @default(true)

      // 数据矩阵
      values: Matrix<Decimal(15,2)> @required

      // 增量数据
      incremental_values: Matrix<Decimal(15,2)>?
    }

    // 进展因子
    development_factors: List<DevelopmentFactor> {
      period: String(20) @required
      factor: Decimal(10,6) @required @min(0)
      selected: Boolean @required
      volume_weighted: Decimal(10,6)?
      simple_average: Decimal(10,6)?
    }

    // 尾部因子
    tail_factor: Decimal(10,6) @default(1.0)

    // 准备金计算结果
    reserve_estimate: ReserveEstimate {
      case_reserve: Decimal(15,2) @required
      ibnr_reserve: Decimal(15,2) @required
      ibner_reserve: Decimal(15,2) @default(0)
      total_reserve: Decimal(15,2) @required
      uepr_reserve: Decimal(15,2) @default(0)  // 未到期责任准备金
    }

    // 预测值
    projected_values: Matrix<Decimal(15,2)>?
    ultimate_claims: List<Decimal(15,2)>?

    // 不确定性
    prediction_error: Decimal(15,2)?
    coefficient_of_variation: Decimal(5,4)?
    confidence_interval: Tuple<Decimal(15,2), Decimal(15,2)>?

    calculation_date: Date @required
    actuary: String(50) @required
  }

  // 定价模型
  pricing_model: PricingModel {
    model_id: String(30) @required @unique
    product_code: String(20) @required

    // 定价假设
    pricing_assumptions: PricingAssumptions {
      // 死亡率/发病率假设
      mortality_table: String(50)?
      morbidity_table: String(50)?
      mortality_adjustment: Decimal(5,4) @default(1.0)

      // 利率假设
      valuation_interest_rate: Decimal(5,4) @required
      pricing_interest_rate: Decimal(5,4) @required

      // 费用假设
      acquisition_cost_rate: Decimal(5,4) @required
      maintenance_expense_rate: Decimal(5,4) @required
      maintenance_expense_per_policy: Decimal(10,2) @required

      // 失效率假设
      lapse_rate_table: List<LapseRate> {
        policy_year: Integer @required
        lapse_rate: Decimal(5,4) @required
      }

      // 分红假设
      dividend_scale: Decimal(5,4)?

      // 税率
      tax_rate: Decimal(5,4) @default(0.25)
    }

    // 保费计算
    premium_calculation: PremiumCalculation {
      gross_premium: Decimal(12,2) @required
      net_premium: Decimal(12,2) @required
      risk_premium: Decimal(12,2) @required
      savings_premium: Decimal(12,2) @default(0)
      loading: Decimal(12,2) @required

      // 保费分解
      mortality_cost: Decimal(12,2) @required
      expense_loading: Decimal(12,2) @required
      profit_loading: Decimal(12,2) @required
      contingency_loading: Decimal(12,2) @default(0)
    }

    // 利润测试
    profit_testing: ProfitTesting {
      projection_years: Integer @required
      discount_rate: Decimal(5,4) @required

      // 利润向量
      profit_vector: List<Decimal(12,2)> @required

      // 利润指标
      npv_profit: Decimal(15,2) @required
      profit_margin: Decimal(5,4) @required
      irr: Decimal(5,4)?
      payback_period: Integer?

      // 敏感性分析
      sensitivity_analysis: List<SensitivityResult> {
        scenario_name: String(50) @required
        assumption_change: String(100) @required
        npv_impact: Decimal(5,4) @required
        margin_impact: Decimal(5,4) @required
      }
    }

    model_date: Date @required
    actuary: String(50) @required
    approved: Boolean @default(false)
  }

  // 评估模型
  valuation_model: ValuationModel {
    model_id: String(30) @required @unique
    valuation_date: Date @required
    valuation_basis: Enum {
      IFRS_17,
      SOLVENCY_II,
      US_GAAP,
      LOCAL_GAAP
    } @required

    // 保险合同负债
    insurance_contract_liability: ContractLiability {
      fulfillment_cash_flows: FulfillmentCashFlows {
        estimates_of_future_cash_flows: Decimal(15,2) @required
        discount_effect: Decimal(15,2) @required
        risk_adjustment: Decimal(15,2) @required
      }

      contractual_service_margin: Decimal(15,2) @required
      loss_component: Decimal(15,2) @default(0)

      total_liability: Decimal(15,2) @required
    }

    // 折现率
    discount_rate: DiscountRate {
      risk_free_rate: Decimal(5,4) @required
      liquidity_premium: Decimal(5,4) @default(0)
      illiquidity_premium: Decimal(5,4) @default(0)
      effective_rate: Decimal(5,4) @required

      // 收益率曲线
      yield_curve: List<YieldPoint> {
        maturity: Integer @required  // 年
        spot_rate: Decimal(5,4) @required
        forward_rate: Decimal(5,4) @required
      }
    }

    // 敏感性分析
    sensitivity_analysis: List<SensitivityAnalysis> {
      risk_factor: Enum {
        INTEREST_RATE,
        MORTALITY,
        LAPSE,
        EXPENSE
      } @required
      shift_basis: Decimal(5,4) @required
      liability_impact: Decimal(15,2) @required
      csm_impact: Decimal(15,2) @required
    }

    actuary: String(50) @required
    reviewer: String(50)?
  }
} @domain("INSURANCE") @version("1.0")
```

**精算公式**：

**未决赔款准备金（IBNR）**：

$$
\text{IBNR} = \sum_{i} \text{Ultimate}_i \times \text{IBNR\_Factor}_i - \text{Case\_Reserve}_i
$$

**合同服务边际（CSM）**：

$$
CSM = \max(0, -\text{PVFP})
$$

其中PVFP为保单未来利润的现值。

---

## 5. 再保险Schema

**定义5（再保险Schema）**：

```text
Reinsurance_Schema = (Treaty × Cession × Recovery)
```

**形式化DSL定义**：

```dsl
schema Reinsurance {
  // 再保险合约
  treaty: ReinsuranceTreaty {
    treaty_id: String(30) @required @unique
    treaty_reference: String(30) @required @unique

    // 合约类型
    treaty_type: Enum {
      QUOTA_SHARE,        // 成数再保险
      SURPLUS,            // 溢额再保险
      EXCESS_OF_LOSS,     // 超赔再保险
      STOP_LOSS,          // stop loss再保险
      CATASTROPHE,        // 巨灾超赔
      FACULTATIVE,        // 临时再保险
      TREATY              // 合约再保险
    } @required

    // 当事人
    cedant: String(50) @required  // 分出公司
    reinsurer: String(50) @required  // 接受公司
    broker: String(50)?  // 经纪人

    // 业务范围
    line_of_business: List<String(50)> @required
    covered_perils: List<String(50)>?
    territorial_scope: List<String(2)> @required  // ISO国家代码

    // 限额与分层
    limits: TreatyLimits {
      cession_percentage: Decimal(5,2)?  // 成数比例
      retention_line: Decimal(15,2)?     // 自留额
      number_of_lines: Integer?          // 线数
      treaty_limit: Decimal(15,2) @required

      // 超赔结构
      attachment_point: Decimal(15,2)?   // 起赔点
      layer_limit: Decimal(15,2)?        // 层限额

      // stop loss
      stop_loss_ratio: Decimal(5,4)?     // stop loss比率
    }

    // 合约期间
    effective_date: Date @required
    expiry_date: Date @required
    termination_clause: String(500)?

    // 合约条件
    commission: Commission {
      ceding_commission_rate: Decimal(5,4) @default(0)
      profit_commission: ProfitCommission?
      override_commission: Decimal(5,4) @default(0)
    }

    premium: TreatyPremium {
      minimum_deposit_premium: Decimal(15,2) @default(0)
      deposit_premium_adjustment: Boolean @default(false)
      rate_on_line: Decimal(10,6)?
    }

    // 合约状态
    status: Enum { ACTIVE, EXPIRED, TERMINATED, RENEWED } @required

    created_at: DateTime @required
    updated_at: DateTime @required
  }

  // 分保业务
  cession: Cession {
    cession_id: String(30) @required @unique
    treaty_id: String(30) @required
    original_policy_id: String(30) @required

    // 分保金额
    original_sum_assured: Decimal(15,2) @required
    ceded_sum_assured: Decimal(15,2) @required
    retention: Decimal(15,2) @required

    // 分保费
    original_premium: Decimal(12,2) @required
    ceded_premium: Decimal(12,2) @required
    ceding_commission: Decimal(12,2) @default(0)
    net_premium: Decimal(12,2) @required

    // 分保比例
    cession_rate: Decimal(5,4) @required

    // 状态
    status: Enum { ACTIVE, CANCELLED, EXPIRED } @required

    cession_date: Date @required
  }

  // 摊回赔款
  recovery: Recovery {
    recovery_id: String(30) @required @unique
    cession_id: String(30) @required
    claim_id: String(30) @required

    // 赔款信息
    original_claim_amount: Decimal(15,2) @required
    recovery_amount: Decimal(15,2) @required
    retention_amount: Decimal(15,2) @required

    // 摊回比例
    recovery_rate: Decimal(5,4) @required

    // 状态
    status: Enum { PENDING, APPROVED, RECOVERED, DISPUTED } @required

    // 时间
    claim_date: Date @required
    recovery_date: Date?

    // 备注
    remarks: String(500)?
  }
} @domain("INSURANCE") @version("1.0")
```

**再保险数学模型**：

**成数分保计算**：

$$
\text{Ceded Premium} = \text{Original Premium} \times \text{Cession Rate}
$$

$$
\text{Recovery} = \text{Claim Amount} \times \text{Cession Rate}
$$

**超赔分保计算**：

$$
\text{Recovery} = \min(\max(\text{Claim} - \text{Attachment}, 0), \text{Layer Limit})
$$

---

## 6. 类型系统

**定义6（保险业务数据类型）**：

```text
Insurance_Data_Type = Policy_Type | Claim_Type | Actuarial_Type | Customer_Type | Financial_Type
```

**基本类型定义**：

```dsl
type PostalAddress {
  address_line: List<String(70)>?
  city: String(35) @required
  state_province: String(35)?
  postal_code: String(16)?
  country: String(2) @required @pattern("[A-Z]{2}")
}

type ContactInformation {
  phone: String(20) @required
  mobile: String(20)?
  fax: String(20)?
  email: String(254)?
  website: String(100)?
}

type AccountIdentification {
  account_type: Enum { IBAN, OTHER } @required
  account_number: String(34) @required
  account_holder_name: String(140) @required
  bank_name: String(100)?
  bank_code: String(20)?
  branch_code: String(20)?
}

type FinancialInstitution {
  bic: String(11)? @pattern("[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?")
  name: String(140) @required
  clearing_code: String(20)?
  address: PostalAddress?
}

type HealthQuestion {
  question_code: String(10) @required
  question_text: String(500) @required
  answer: Enum { YES, NO, NA } @required
  details: String(500)?
  declaration_date: Date @required
}

type SurveyFinding {
  finding_id: String(20) @required
  category: String(50) @required
  description: String(500) @required
  severity: Enum { LOW, MEDIUM, HIGH, CRITICAL } @required
  recommendation: String(500)?
}

type LossItem {
  item_id: String(20) @required
  item_category: String(50) @required
  item_description: String(200) @required
  quantity: Decimal(10,2) @required
  unit: String(20) @required
  original_cost: Decimal(12,2) @required
  depreciation_rate: Decimal(5,4) @default(0)
  depreciated_value: Decimal(12,2) @required
  assessed_value: Decimal(12,2) @required
  currency: String(3) @required
}

type ProfitCommission {
  enabled: Boolean @default(false)
  commission_percentage: Decimal(5,4)?
  loss_carry_forward: Boolean @default(true)
  loss_limit_years: Integer @default(3)
}
```

---

## 7. 约束规则

**约束1（保单有效性）**：

```text
∀ policy ∈ Policy:
  policy.effective_date ≤ policy.expiry_date
  ∧ policy.sum_assured > 0
  ∧ policy.premium > 0
  ∧ (policy.policy_type = TERM_LIFE → policy.policy_term > 0)
  ∧ (policy.policy_status = INFORCE → policy.effective_date ≤ today ≤ policy.expiry_date)
```

**约束2（受益人份额）**：

```text
∀ policy ∈ Policy:
  let beneficiaries = policy.policy_parties.beneficiaries
  in ∀ b ∈ beneficiaries: b.share_percentage ≥ 0
  ∧ sum([b.share_percentage for b in beneficiaries]) = 100
```

**约束3（理赔金额约束）**：

```text
∀ claim ∈ Claim:
  claim.claim_calculation.net_claim_amount ≥ 0
  ∧ claim.claim_calculation.net_claim_amount ≤ claim.claim_assessment.loss_assessment.assessed_amount
  ∧ claim.claim_payment.payment_amount ≤ claim.claim_calculation.total_payable_amount
```

**约束4（准备金非负）**：

```text
∀ reserve ∈ ReserveEstimate:
  reserve.case_reserve ≥ 0
  ∧ reserve.ibnr_reserve ≥ 0
  ∧ reserve.total_reserve ≥ 0
```

**约束5（再保险限额）**：

```text
∀ cession ∈ Cession:
  cession.ceded_sum_assured ≤ cession.original_sum_assured
  ∧ cession.ceded_sum_assured + cession.retention = cession.original_sum_assured
  ∧ cession.cession_rate = cession.ceded_sum_assured / cession.original_sum_assured
```

---

## 8. 转换函数

**函数1（保单到ACORD转换）**：

```text
convert_policy_to_acord: Policy → ACORD_Policy
```

**函数2（理赔到ACORD转换）**：

```text
convert_claim_to_acord: Claim → ACORD_Claim
```

**函数3（IFRS 17合同组转换）**：

```text
convert_policy_to_ifrs17_group: Policy → IFRS17_ContractGroup
```

**函数4（准备金到监管报送格式转换）**：

```text
convert_reserve_to_regulatory: ReserveEstimate → RegulatoryReserveReport
```

**函数5（现金价值计算）**：

```text
calculate_cash_value: Policy × Integer → Decimal
calculate_cash_value(policy, year) = policy.premium_info.account_value - surrender_charge
```

---

## 9. 形式化定理

### 9.1 保单一致性定理

**定理1（保单期间一致性）**：

```text
∀ policy ∈ Policy:
  policy.expiry_date = add_period(policy.effective_date, policy.policy_term, policy.policy_term_unit)
```

**证明**：
由定义2中PolicyBasic的约束可得，保单到期日必须等于生效日加上保险期间。
对于年为单位：
$$
\text{expiry\_date} = \text{effective\_date} + \text{policy\_term} \text{ years} \quad \square
$$

### 9.2 理赔完备性定理

**定理2（理赔金额一致性）**：

```text
∀ claim ∈ Claim:
  claim.claim_calculation.net_claim_amount =
    claim.claim_assessment.loss_assessment.assessed_amount
    - claim.claim_calculation.deductible_amount
    - claim.claim_calculation.depreciation_amount
    + claim.claim_calculation.interest_amount
```

**证明**：
由定义3中ClaimCalculation的约束可得，净赔付额等于评估金额减去扣减项加上利息。 $\square$

### 9.3 准备金充足性定理

**定理3（准备金非负性）**：

```text
∀ estimate ∈ ReserveEstimate:
  estimate.total_reserve = estimate.case_reserve + estimate.ibnr_reserve + estimate.ibner_reserve ≥ 0
```

**证明**：
由定义4中ReserveEstimate的约束：

1. 每个分项准备金均 ≥ 0
2. 总准备金 = 各分项之和
因此总准备金 ≥ 0 $\square$

---

## 10. 数学模型

### 10.1 保单状态机

**保单状态转换**：

```
                     ┌─────────────┐
                     │   PROPOSAL  │
                     └──────┬──────┘
                            │ submit
                            ▼
                     ┌─────────────┐
                     │UNDERWRITING │◄──────────────┐
                     └──────┬──────┘               │
                            │ approve              │ decline
              ┌─────────────┴─────────────┐        │
              │                           │        │
              ▼                           ▼        │
       ┌─────────────┐             ┌─────────────┐ │
       │   INFORCE   │◄────────────│   LAPSED    │─┘
       └──────┬──────┘  reinstate  └─────────────┘
               │
    ┌──────┬───┴───┬──────┬──────┐
    │      │       │      │      │
    ▼      ▼       ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│PAID_UP││MATURED││CLAIMED││SURRENDERED││TERMINATED│
└──────┘└──────┘└──────┘└──────┘└──────┘
```

**状态转移函数**：

$$
\delta_P: S_P \times E_P \rightarrow S_P
$$

其中：

- $S_P = \{\text{PROPOSAL}, \text{UNDERWRITING}, \text{INFORCE}, \text{LAPSED}, \text{PAID_UP}, \text{MATURED}, \text{CLAIMED}, \text{SURRENDERED}, \text{TERMINATED}\}$
- $E_P = \{\text{submit}, \text{approve}, \text{decline}, \text{reinstate}, \text{mature}, \text{claim}, \text{surrender}, \text{terminate}\}$

### 10.2 理赔状态机

**理赔状态转换**：

```
┌──────────────┐  register   ┌─────────────────┐  investigate  ┌──────────────┐
│    NEW       │────────────►│   REGISTERED    │──────────────►│   UNDER_     │
│   CLAIM      │             │                 │               │INVESTIGATION │
└──────────────┘             └─────────────────┘               └──────┬───────┘
                                                                      │
                    ┌─────────────────────────────────────────────────┼───────┐
                    │                                                 │       │
                    ▼                                                 ▼       ▼
             ┌──────────────┐                                 ┌──────────────┐
             │   DOCUMENT   │◄────────────────────────────────│ DOCUMENT_    │
             │   PENDING    │                                 │   PENDING    │
             └──────┬───────┘                                 └──────────────┘
                    │
                    │ docs received
                    ▼
             ┌──────────────┐  assess   ┌──────────────┐  approve  ┌──────────┐
             │  UNDER_      │──────────►│   APPROVED   │──────────►│  PAID    │
             │ASSESSMENT    │           │   REJECTED   │           │  CLOSED  │
             └──────────────┘           └──────────────┘           └──────────┘
```

**状态转移函数**：

$$
\delta_C: S_C \times E_C \rightarrow S_C
$$

### 10.3 精算计算模型

**链梯法模型**：

**进展因子计算**：

$$
f_j = \frac{\sum_{i=1}^{n-j} C_{i,j+1}}{\sum_{i=1}^{n-j} C_{i,j}}
$$

其中：

- $f_j$：第j个进展年的进展因子
- $C_{i,j}$：事故年i在进展年j的累计赔款
- $n$：事故年数

**终极赔款预测**：

$$
\hat{C}_{i,\infty} = C_{i,n-i+1} \times \prod_{j=n-i+1}^{\infty} f_j
$$

**IBNR准备金**：

$$
\text{IBNR}_i = \hat{C}_{i,\infty} - C_{i,n-i+1}
$$

**BF法模型**：

$$
\hat{C}_{i,\infty} = Z_i \times \hat{C}_{i,\infty}^{CL} + (1-Z_i) \times \text{ELR} \times \text{EP}_i
$$

其中：

- $\hat{C}_{i,\infty}^{CL}$：链梯法预测的终极赔款
- ELR：预期赔付率
- $EP_i$：事故年i的已赚保费
- $Z_i$：可信度因子

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
