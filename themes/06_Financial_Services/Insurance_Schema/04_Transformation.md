# 保险业务Schema转换应用

## 📑 目录

- [保险业务Schema转换应用](#保险业务schema转换应用)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
    - [1.2 转换架构](#12-转换架构)
  - [2. 保单生命周期转换](#2-保单生命周期转换)
    - [2.1 投保申请转换](#21-投保申请转换)
    - [2.2 保单承保转换](#22-保单承保转换)
    - [2.3 保全变更转换](#23-保全变更转换)
    - [2.4 保单续期转换](#24-保单续期转换)
  - [3. 理赔流程转换](#3-理赔流程转换)
    - [3.1 理赔报案转换](#31-理赔报案转换)
    - [3.2 查勘定损转换](#32-查勘定损转换)
    - [3.3 理算核赔转换](#33-理算核赔转换)
  - [4. ACORD标准转换](#4-acord标准转换)
    - [4.1 保单到ACORD转换](#41-保单到acord转换)
    - [4.2 理赔到ACORD转换](#42-理赔到acord转换)
    - [4.3 ACORD到内部格式转换](#43-acord到内部格式转换)
  - [5. IFRS 17转换](#5-ifrs-17转换)
    - [5.1 保单到IFRS 17合同组转换](#51-保单到ifrs-17合同组转换)
    - [5.2 履约现金流计算](#52-履约现金流计算)
    - [5.3 CSM计算与摊销](#53-csm计算与摊销)
  - [6. 保险数据存储与分析](#6-保险数据存储与分析)
    - [6.1 PostgreSQL保险数据存储](#61-postgresql保险数据存储)
    - [6.2 保险业务分析查询](#62-保险业务分析查询)
  - [7. 转换验证与测试](#7-转换验证与测试)
    - [7.1 数据一致性验证](#71-数据一致性验证)
    - [7.2 业务规则验证](#72-业务规则验证)
  - [8. 精算计算转换](#8-精算计算转换)
    - [8.1 准备金评估转换](#81-准备金评估转换)
    - [8.2 保费计算转换](#82-保费计算转换)

---

## 1. 转换体系概述

### 1.1 转换目标

保险业务Schema转换体系支持以下转换目标：

1. **保单生命周期转换**：投保、承保、保全、续期、理赔
2. **ACORD标准转换**：内部格式与ACORD标准互转
3. **IFRS 17转换**：传统会计到IFRS 17会计
4. **监管报送转换**：偿付能力报告、业务统计报送
5. **再保险转换**：分保、转分保数据处理
6. **数据存储转换**：业务数据到分析数据仓库

**转换函数定义**：

```text
Insurance_Transform = {
  policy_lifecycle_transform: PolicyEvent × State → PolicyState',
  acord_transform: InternalFormat ↔ ACORDFormat,
  ifrs17_transform: Policy × AccountingBasis → IFRS17Contract,
  regulatory_transform: Data × ReportTemplate → RegulatoryReport,
  reinsurance_transform: Cession × Treaty → ReinsuranceEntry,
  analytics_transform: Transaction × Schema → AnalyticsRecord
}
```

### 1.2 转换架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        转换架构层                                │
├───────────────────┬───────────────────┬─────────────────────────┤
│    业务系统层      │     转换引擎层     │       目标系统层         │
├───────────────────┼───────────────────┼─────────────────────────┤
│ 核心保险系统       │   Schema解析器     │    ACORD平台            │
│ 理赔系统          │   数据映射引擎      │    IFRS 17系统          │
│ 精算系统          │   精算计算引擎      │    监管报送系统          │
│ 再保险系统        │   会计引擎         │    数据仓库              │
│ 渠道系统          │   错误处理         │    分析平台              │
└───────────────────┴───────────────────┴─────────────────────────┘
           │                    │                    │
           └────────────────────┼────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │     监控与治理层       │
                    │  日志、审计、质量监控   │
                    └───────────────────────┘
```

---

## 2. 保单生命周期转换

### 2.1 投保申请转换

**投保单格式转换**：

```python
def transform_proposal_to_policy(proposal: ProposalApplication) -> Policy:
    """将投保申请转换为保单"""
    policy = Policy()
    
    # 保单基础信息
    policy.policy_id = generate_policy_id()
    policy.policy_number = generate_policy_number(proposal.product_code)
    policy.proposal_number = proposal.proposal_number
    
    # 产品信息
    policy.product_code = proposal.product_code
    policy.product_name = proposal.product_name
    policy.product_type = map_product_type(proposal.product_type)
    
    # 保险期间
    policy.policy_term = proposal.policy_term
    policy.policy_term_unit = proposal.policy_term_unit
    policy.effective_date = proposal.requested_effective_date
    policy.expiry_date = calculate_expiry_date(
        proposal.requested_effective_date,
        proposal.policy_term,
        proposal.policy_term_unit
    )
    
    # 初始状态
    policy.policy_status = PolicyStatus.INFORCE
    
    # 销售渠道
    policy.channel_type = proposal.channel_type
    policy.sales_code = proposal.sales_code
    policy.organization_code = proposal.organization_code
    
    # 时间戳
    policy.issue_date = datetime.now().date()
    policy.input_date = datetime.now()
    policy.last_modified = datetime.now()
    
    # 保险责任转换
    policy.policy_coverages = []
    for prop_coverage in proposal.coverages:
        coverage = transform_proposal_coverage(prop_coverage)
        coverage.policy_id = policy.policy_id
        policy.policy_coverages.append(coverage)
    
    # 保费信息转换
    policy.premium_info = calculate_premium_info(policy.policy_coverages)
    
    # 当事人信息转换
    policy.policy_parties = PolicyParties()
    policy.policy_parties.policyholder = transform_proposal_policyholder(
        proposal.policyholder
    )
    policy.policy_parties.insured = transform_proposal_insured(
        proposal.insured
    )
    policy.policy_parties.beneficiaries = [
        transform_proposal_beneficiary(b) 
        for b in proposal.beneficiaries
    ]
    
    return policy

def transform_proposal_coverage(prop_coverage: ProposalCoverage) -> PolicyCoverage:
    """转换投保责任为保单责任"""
    coverage = PolicyCoverage()
    
    coverage.coverage_id = generate_coverage_id()
    coverage.coverage_code = prop_coverage.coverage_code
    coverage.coverage_name = prop_coverage.coverage_name
    coverage.coverage_type = prop_coverage.coverage_type
    
    # 保额与保费
    coverage.sum_assured = prop_coverage.sum_assured
    coverage.premium = prop_coverage.calculated_premium
    coverage.premium_frequency = prop_coverage.premium_frequency
    coverage.premium_term = prop_coverage.premium_term
    coverage.premium_term_unit = prop_coverage.premium_term_unit
    
    # 责任期间
    coverage.coverage_start_date = prop_coverage.start_date
    coverage.coverage_end_date = prop_coverage.end_date
    
    # 等待期与免责期
    coverage.waiting_period_days = prop_coverage.waiting_period_days
    coverage.survival_period_days = prop_coverage.survival_period_days
    
    # 状态
    coverage.status = CoverageStatus.ACTIVE
    
    # 特殊条款
    coverage.exclusions = prop_coverage.exclusions
    coverage.special_clauses = prop_coverage.special_clauses
    
    return coverage
```

### 2.2 保单承保转换

**核保决定转换**：

```python
def transform_underwriting_decision(policy: Policy, 
                                     decision: UnderwritingDecision) -> Policy:
    """根据核保决定更新保单"""
    
    if decision.decision_type == UnderwritingDecisionType.ACCEPT:
        # 标准体承保
        policy.policy_status = PolicyStatus.INFORCE
        policy.underwriting_result = UnderwritingResult.STANDARD
        
    elif decision.decision_type == UnderwritingDecisionType.ACCEPT_RATED:
        # 加费承保
        policy.policy_status = PolicyStatus.INFORCE
        policy.underwriting_result = UnderwritingResult.RATED
        
        # 应用加费
        for coverage in policy.policy_coverages:
            if coverage.coverage_code in decision.rated_coverages:
                rating = decision.rated_coverages[coverage.coverage_code]
                coverage.premium = coverage.premium * (1 + rating.loading_rate)
        
        # 重新计算总保费
        policy.premium_info = recalculate_premium_info(policy.policy_coverages)
        
    elif decision.decision_type == UnderwritingDecisionType.ACCEPT_EXCLUSION:
        # 除外承保
        policy.policy_status = PolicyStatus.INFORCE
        policy.underwriting_result = UnderwritingResult.EXCLUSION
        
        # 应用除外条款
        for coverage in policy.policy_coverages:
            if coverage.coverage_code in decision.exclusion_clauses:
                exclusion = decision.exclusion_clauses[coverage.coverage_code]
                coverage.exclusions = coverage.exclusions or []
                coverage.exclusions.extend(exclusion.exclusions)
        
    elif decision.decision_type == UnderwritingDecisionType.DECLINE:
        # 拒保
        policy.policy_status = PolicyStatus.TERMINATED
        policy.underwriting_result = UnderwritingResult.DECLINED
        policy.decline_reason = decision.decline_reason
        
    elif decision.decision_type == UnderwritingDecisionType.POSTPONE:
        # 延期
        policy.policy_status = PolicyStatus.PROPOSAL
        policy.underwriting_result = UnderwritingResult.POSTPONED
        policy.postpone_until = decision.postpone_until
        policy.postpone_reason = decision.postpone_reason
    
    policy.underwriting_date = decision.decision_date
    policy.underwriter = decision.underwriter_id
    policy.last_modified = datetime.now()
    
    return policy
```

### 2.3 保全变更转换

**保全变更处理**：

```python
def transform_endorsement(policy: Policy, 
                          endorsement: EndorsementApplication) -> Policy:
    """处理保单保全变更"""
    
    # 创建批单
    endorsement_record = Endorsement()
    endorsement_record.endorsement_id = generate_endorsement_id()
    endorsement_record.policy_id = policy.policy_id
    endorsement_record.endorsement_type = endorsement.endorsement_type
    endorsement_record.effective_date = endorsement.effective_date
    endorsement_record.application_date = datetime.now().date()
    
    if endorsement.endorsement_type == EndorsementType.CONTACT_CHANGE:
        # 联系方式变更
        policy.policy_parties.policyholder.contact_info.phone = \
            endorsement.new_phone
        policy.policy_parties.policyholder.contact_info.email = \
            endorsement.new_email
        policy.policy_parties.policyholder.contact_info.address = \
            endorsement.new_address
            
    elif endorsement.endorsement_type == EndorsementType.BENEFICIARY_CHANGE:
        # 受益人变更
        policy.policy_parties.beneficiaries = [
            transform_beneficiary(b) for b in endorsement.new_beneficiaries
        ]
        
        # 验证受益人份额总和
        total_share = sum(b.share_percentage for b in policy.policy_parties.beneficiaries)
        if abs(total_share - 100) > 0.01:
            raise ValueError(f"Beneficiary shares must sum to 100%, got {total_share}%")
            
    elif endorsement.endorsement_type == EndorsementType.SUM_ASSURED_INCREASE:
        # 保额增加
        coverage = find_coverage(policy, endorsement.coverage_code)
        coverage.sum_assured = endorsement.new_sum_assured
        
        # 计算新增保费
        additional_premium = calculate_additional_premium(
            coverage, 
            endorsement.new_sum_assured - endorsement.old_sum_assured,
            endorsement.effective_date
        )
        
        endorsement_record.additional_premium = additional_premium
        coverage.premium += additional_premium
        
        # 重新计算总保费
        policy.premium_info = recalculate_premium_info(policy.policy_coverages)
        
    elif endorsement.endorsement_type == EndorsementType.PAID_UP:
        # 减额交清
        policy.policy_status = PolicyStatus.PAID_UP
        
        for coverage in policy.policy_coverages:
            # 计算现金价值
            cash_value = calculate_cash_value(policy, coverage)
            
            # 计算新保额
            new_sum_assured = calculate_paid_up_sum_assured(
                coverage, cash_value
            )
            
            coverage.sum_assured = new_sum_assured
            coverage.premium = 0
            coverage.premium_term = 0
            
        policy.premium_info.total_premium = 0
        policy.premium_info.payment_status = PaymentStatus.PAID
        
    elif endorsement.endorsement_type == EndorsementType.SURRENDER:
        # 退保
        surrender_value = calculate_surrender_value(policy)
        
        policy.policy_status = PolicyStatus.SURRENDERED
        policy.surrender_date = datetime.now().date()
        policy.surrender_value = surrender_value
        
        for coverage in policy.policy_coverages:
            coverage.status = CoverageStatus.CANCELLED
            coverage.coverage_end_date = datetime.now().date()
    
    policy.endorsements.append(endorsement_record)
    policy.version += 1
    policy.last_modified = datetime.now()
    
    return policy
```

### 2.4 保单续期转换

**续期处理**：

```python
def transform_renewal(policy: Policy, renewal_date: date) -> Policy:
    """处理保单续期"""
    
    # 检查是否可续期
    if policy.policy_status != PolicyStatus.INFORCE:
        raise ValueError(f"Policy {policy.policy_number} is not inforce")
    
    # 创建续期记录
    renewal = Renewal()
    renewal.renewal_id = generate_renewal_id()
    renewal.policy_id = policy.policy_id
    renewal.renewal_date = renewal_date
    
    # 计算应缴保费
    renewal_due = calculate_renewal_due(policy, renewal_date)
    renewal.renewal_premium = renewal_due.premium_amount
    renewal.due_date = renewal_due.due_date
    
    # 更新保费信息
    policy.premium_info.next_due_date = renewal_due.due_date
    policy.premium_info.next_due_amount = renewal_due.premium_amount
    policy.premium_info.payment_status = PaymentStatus.DUE
    
    policy.renewals.append(renewal)
    policy.last_modified = datetime.now()
    
    return policy

def process_premium_payment(policy: Policy, 
                            payment: PremiumPayment) -> Policy:
    """处理保费缴纳"""
    
    # 验证支付金额
    if payment.amount < policy.premium_info.next_due_amount:
        raise ValueError("Payment amount less than due amount")
    
    # 更新已缴保费
    policy.premium_info.total_paid_premium += payment.amount
    policy.premium_info.total_paid_periods += 1
    
    # 计算下一缴费期
    next_due = calculate_next_due_date(
        policy.premium_info.next_due_date,
        policy.policy_coverages[0].premium_frequency
    )
    
    policy.premium_info.next_due_date = next_due
    policy.premium_info.next_due_amount = calculate_next_premium(policy)
    policy.premium_info.payment_status = PaymentStatus.PAID
    
    # 如果之前是失效状态，恢复有效
    if policy.policy_status == PolicyStatus.LAPSED:
        policy.policy_status = PolicyStatus.REINSTATED
        policy.reinstatement_date = datetime.now().date()
    
    policy.last_modified = datetime.now()
    
    return policy
```

---

## 3. 理赔流程转换

### 3.1 理赔报案转换

**报案登记转换**：

```python
def transform_claim_notification(notification: ClaimNotification) -> Claim:
    """将理赔报案转换为理赔案件"""
    claim = Claim()
    
    # 基本信息
    claim.claim_id = generate_claim_id()
    claim.claim_number = generate_claim_number()
    claim.policy_id = notification.policy_id
    
    # 查找保单和责任
    policy = find_policy(notification.policy_id)
    claim.coverage_id = determine_coverage(policy, notification.incident_type)
    
    # 出险信息
    claim.date_of_loss = notification.date_of_loss
    claim.time_of_loss = notification.time_of_loss
    claim.place_of_loss = notification.place_of_loss
    claim.cause_of_loss = notification.cause_of_loss
    claim.loss_description = notification.loss_description
    
    # 报案信息
    claim.reported_date = datetime.now()
    claim.reported_by = notification.reporter_name
    claim.reporter_phone = notification.reporter_phone
    claim.report_channel = notification.report_channel
    
    # 事故类型
    claim.incident_type = notification.incident_type
    claim.claim_type = determine_claim_type(policy, notification.incident_type)
    
    # 初始状态
    claim.claim_status = ClaimStatus.REGISTERED
    
    # 分配
    claim.assigned_branch = policy.organization_code
    claim.assigned_adjuster = assign_adjuster(claim)
    
    # 时间戳
    claim.created_at = datetime.now()
    claim.updated_at = datetime.now()
    
    # 验证保单有效性
    if policy.policy_status != PolicyStatus.INFORCE:
        claim.claim_status = ClaimStatus.REJECTED
        claim.rejection_reason = f"Policy status is {policy.policy_status}"
    
    # 验证是否在保险期间内
    if not (policy.effective_date <= notification.date_of_loss <= policy.expiry_date):
        claim.claim_status = ClaimStatus.REJECTED
        claim.rejection_reason = "Loss date outside policy period"
    
    return claim
```

### 3.2 查勘定损转换

**查勘定损处理**：

```python
def transform_survey_assessment(claim: Claim, 
                                 survey: SurveyReport) -> Claim:
    """处理查勘定损结果"""
    
    assessment = ClaimAssessment()
    assessment.assessment_id = generate_assessment_id()
    assessment.claim_id = claim.claim_id
    
    # 查勘信息
    assessment.survey_date = survey.survey_date
    assessment.surveyor_name = survey.surveyor_name
    assessment.survey_report = survey.report
    assessment.survey_findings = survey.findings
    
    # 损失评估
    assessment.loss_assessment = LossAssessment()
    assessment.loss_assessment.assessed_amount = survey.total_assessed_amount
    assessment.loss_assessment.assessment_currency = survey.currency
    assessment.loss_assessment.assessment_basis = survey.assessment_basis
    assessment.loss_assessment.depreciation_rate = survey.depreciation_rate
    assessment.loss_assessment.salvage_value = survey.salvage_value
    assessment.loss_assessment.deductible = survey.deductible_amount
    
    # 损失明细
    assessment.loss_assessment.loss_items = [
        transform_loss_item(item) for item in survey.loss_items
    ]
    
    # 责任认定
    assessment.liability_assessment = LiabilityAssessment()
    assessment.liability_assessment.is_liability_accepted = survey.is_liability_accepted
    assessment.liability_assessment.liability_percentage = survey.liability_percentage
    assessment.liability_assessment.rejection_reason = survey.rejection_reason
    assessment.liability_assessment.policy_applicable = survey.policy_applicable
    assessment.liability_assessment.exclusion_applicable = survey.exclusion_applicable
    assessment.liability_assessment.exclusion_clauses = survey.exclusion_clauses
    
    assessment.assessment_date = datetime.now()
    assessment.assessor = survey.surveyor_name
    
    claim.claim_assessment = assessment
    
    # 更新状态
    if survey.is_liability_accepted:
        claim.claim_status = ClaimStatus.UNDER_ASSESSMENT
    else:
        claim.claim_status = ClaimStatus.REJECTED
    
    claim.updated_at = datetime.now()
    
    return claim
```

### 3.3 理算核赔转换

**理算处理**：

```python
def transform_claim_calculation(claim: Claim, 
                                 calculation: ClaimCalculationInput) -> Claim:
    """处理理算计算"""
    
    calc = ClaimCalculation()
    calc.calculation_id = generate_calculation_id()
    calc.claim_id = claim.claim_id
    
    assessment = claim.claim_assessment.loss_assessment
    
    # 毛赔款额
    calc.gross_claim_amount = assessment.assessed_amount
    
    # 扣减项
    calc.deductible_amount = assessment.deductible
    calc.depreciation_amount = assessment.assessed_amount * assessment.depreciation_rate
    calc.salvage_recovery = assessment.salvage_value
    calc.subrogation_recovery = calculation.subrogation_recovery or 0
    calc.previous_payments = calculation.previous_payments or 0
    
    # 净赔款额
    calc.net_claim_amount = (
        calc.gross_claim_amount
        - calc.deductible_amount
        - calc.depreciation_amount
        - calc.salvage_recovery
        - calc.subrogation_recovery
        - calc.previous_payments
    )
    
    # 确保非负
    calc.net_claim_amount = max(0, calc.net_claim_amount)
    
    # 利息
    calc.interest_amount = calculate_claim_interest(
        claim.date_of_loss,
        datetime.now().date(),
        calc.net_claim_amount
    )
    
    # 总赔付额
    calc.total_payable_amount = calc.net_claim_amount + calc.interest_amount
    
    # 理算明细
    calc.calculation_details = []
    for coverage_calc in calculation.coverage_calculations:
        detail = CalculationDetail()
        detail.coverage_code = coverage_calc.coverage_code
        detail.benefit_type = coverage_calc.benefit_type
        detail.claimed_amount = coverage_calc.claimed_amount
        detail.approved_amount = coverage_calc.approved_amount
        detail.deduction_reason = coverage_calc.deduction_reason
        calc.calculation_details.append(detail)
    
    calc.calculation_date = datetime.now()
    calc.calculator = calculation.calculator_id
    
    claim.claim_calculation = calc
    claim.claim_status = ClaimStatus.PENDING_APPROVAL
    claim.updated_at = datetime.now()
    
    return claim

def process_claim_approval(claim: Claim, 
                           approval: ClaimApproval) -> Claim:
    """处理理赔审批"""
    
    if approval.decision == ApprovalDecision.APPROVED:
        claim.claim_status = ClaimStatus.APPROVED
        claim.approved_amount = claim.claim_calculation.total_payable_amount
        
        # 创建支付记录
        payment = ClaimPayment()
        payment.payment_id = generate_payment_id()
        payment.claim_id = claim.claim_id
        payment.calculation_id = claim.claim_calculation.calculation_id
        payment.payment_amount = claim.approved_amount
        payment.payment_currency = claim.claim_assessment.loss_assessment.assessment_currency
        payment.payment_type = PaymentType.CLAIM_PAYMENT
        
        # 收款人信息
        payment.payee = determine_payee(claim, approval)
        payment.payment_method = approval.payment_method
        payment.payment_status = PaymentStatus.PENDING
        payment.requested_date = datetime.now()
        
        claim.claim_payment = payment
        claim.claim_status = ClaimStatus.PAYMENT_PENDING
        
    elif approval.decision == ApprovalDecision.REJECTED:
        claim.claim_status = ClaimStatus.REJECTED
        claim.rejection_reason = approval.rejection_reason
        
    elif approval.decision == ApprovalDecision.PARTIAL:
        claim.claim_status = ClaimStatus.APPROVED
        claim.approved_amount = approval.partial_amount
        # 重新理算...
    
    claim.approved_by = approval.approver_id
    claim.approved_at = datetime.now()
    claim.updated_at = datetime.now()
    
    return claim
```

---

## 4. ACORD标准转换

### 4.1 保单到ACORD转换

```python
def convert_policy_to_acord(policy: Policy) -> ACORDPolicy:
    """将内部保单格式转换为ACORD格式"""
    acord = ACORDPolicy()
    
    # SignonRq
    acord.signon_rq = SignonRq()
    acord.signon_rq.signon_pswd = SignonPswd()
    acord.signon_rq.signon_pswd.cust_id = CustId()
    acord.signon_rq.signon_pswd.cust_id.sp_name = "Insurance Company"
    acord.signon_rq.signon_pswd.cust_id.cust_login_id = "system"
    acord.signon_rq.client_dt = datetime.now()
    
    # InsuranceSvcRq
    acord.insurance_svc_rq = InsuranceSvcRq()
    acord.insurance_svc_rq.rq_uid = generate_uuid()
    
    # PolicyInqRs（查询响应）
    acord.insurance_svc_rq.policy_inq_rs = PolicyInqRs()
    
    # 保单信息
    acord_policy = AcordPolicy()
    acord_policy.policy_number = policy.policy_number
    acord_policy.company_product_code = policy.product_code
    acord_policy.effective_dt = policy.effective_date
    acord_policy.expiration_dt = policy.expiry_date
    
    # 保单持有人
    acord_policy.named_insured = NamedInsured()
    acord_policy.named_insured.comml_name = \
        policy.policy_parties.policyholder.name
    acord_policy.named_insured.addr = convert_address_to_acord(
        policy.policy_parties.policyholder.contact_info.address
    )
    
    # 保险责任
    acord_policy.coverage = []
    for cov in policy.policy_coverages:
        acord_cov = Coverage()
        acord_cov.coverage_cd = cov.coverage_code
        acord_cov.coverage_desc = cov.coverage_name
        acord_cov.limit = Limit()
        acord_cov.limit.format_currency_amt = FormatCurrencyAmt()
        acord_cov.limit.format_currency_amt.amt = float(cov.sum_assured)
        acord_cov.limit.format_currency_amt.currency_cd = policy.premium_info.premium_currency if hasattr(policy.premium_info, 'premium_currency') else 'CNY'
        
        acord_cov.current_term_amt = CurrentTermAmt()
        acord_cov.current_term_amt.format_currency_amt = FormatCurrencyAmt()
        acord_cov.current_term_amt.format_currency_amt.amt = float(cov.premium)
        
        acord_policy.coverage.append(acord_cov)
    
    acord.insurance_svc_rq.policy_inq_rs.policy = acord_policy
    
    # SignoffRq
    acord.signoff_rq = SignoffRq()
    acord.signoff_rq.client_dt = datetime.now()
    
    return acord

def convert_address_to_acord(address: PostalAddress) -> Addr:
    """转换地址为ACORD格式"""
    acord_addr = Addr()
    
    acord_addr.addr1 = address.address_line[0] if address.address_line else ""
    acord_addr.addr2 = address.address_line[1] if len(address.address_line) > 1 else ""
    acord_addr.city = address.city
    acord_addr.state_prov_cd = address.state_province or ""
    acord_addr.postal_code = address.postal_code or ""
    acord_addr.country_cd = address.country
    
    return acord_addr
```

### 4.2 理赔到ACORD转换

```python
def convert_claim_to_acord(claim: Claim) -> ACORDClaim:
    """将内部理赔格式转换为ACORD格式"""
    acord = ACORDClaim()
    
    # ClaimInqRs
    acord.claim_inq_rs = ClaimInqRs()
    acord.claim_inq_rs.rq_uid = generate_uuid()
    
    # 理赔信息
    acord_claim = AcordClaim()
    acord_claim.claim_number = claim.claim_number
    acord_claim.policy_number = claim.policy_number
    acord_claim.loss_dt = claim.date_of_loss
    acord_claim.reported_dt = claim.reported_date
    
    # 事故详情
    acord_claim.loss_info = LossInfo()
    acord_claim.loss_info.cause_of_loss = claim.cause_of_loss
    acord_claim.loss_info.loss_description = claim.loss_description
    acord_claim.loss_info.loss_addr = Addr()
    acord_claim.loss_info.loss_addr.addr1 = claim.place_of_loss
    
    # 理赔状态
    acord_claim.claim_status_cd = map_claim_status_to_acord(claim.claim_status)
    
    # 损失评估
    if claim.claim_assessment:
        acord_claim.claim_amount = FormatCurrencyAmt()
        acord_claim.claim_amount.amt = float(
            claim.claim_assessment.loss_assessment.assessed_amount
        )
        acord_claim.claim_amount.currency_cd = \
            claim.claim_assessment.loss_assessment.assessment_currency
    
    # 赔付金额
    if claim.claim_calculation:
        acord_claim.settlement_amount = FormatCurrencyAmt()
        acord_claim.settlement_amount.amt = float(
            claim.claim_calculation.total_payable_amount
        )
    
    acord.claim_inq_rs.claim = acord_claim
    
    return acord

def map_claim_status_to_acord(status: ClaimStatus) -> str:
    """映射理赔状态到ACORD代码"""
    status_mapping = {
        ClaimStatus.REGISTERED: "01",
        ClaimStatus.UNDER_INVESTIGATION: "02",
        ClaimStatus.UNDER_ASSESSMENT: "03",
        ClaimStatus.PENDING_APPROVAL: "04",
        ClaimStatus.APPROVED: "05",
        ClaimStatus.REJECTED: "06",
        ClaimStatus.PAYMENT_PENDING: "07",
        ClaimStatus.PAID: "08",
        ClaimStatus.CLOSED: "09"
    }
    return status_mapping.get(status, "99")
```

### 4.3 ACORD到内部格式转换

```python
def convert_acord_to_policy(acord: ACORDPolicy) -> Policy:
    """将ACORD格式转换为内部保单格式"""
    policy = Policy()
    
    acord_policy = acord.insurance_svc_rq.policy_inq_rs.policy
    
    # 保单信息
    policy.policy_number = acord_policy.policy_number
    policy.product_code = acord_policy.company_product_code
    policy.effective_date = acord_policy.effective_dt
    policy.expiry_date = acord_policy.expiration_dt
    
    # 投保人
    policy.policy_parties = PolicyParties()
    policy.policy_parties.policyholder = Party()
    policy.policy_parties.policyholder.name = acord_policy.named_insured.comml_name
    policy.policy_parties.policyholder.contact_info = ContactInformation()
    policy.policy_parties.policyholder.contact_info.address = \
        convert_acord_to_address(acord_policy.named_insured.addr)
    
    # 保险责任
    policy.policy_coverages = []
    for acord_cov in acord_policy.coverage:
        cov = PolicyCoverage()
        cov.coverage_code = acord_cov.coverage_cd
        cov.coverage_name = acord_cov.coverage_desc
        cov.sum_assured = Decimal(str(acord_cov.limit.format_currency_amt.amt))
        cov.premium = Decimal(str(acord_cov.current_term_amt.format_currency_amt.amt))
        policy.policy_coverages.append(cov)
    
    return policy
```

---

## 5. IFRS 17转换

### 5.1 保单到IFRS 17合同组转换

```python
def convert_policy_to_ifrs17_group(policy: Policy) -> IFRS17ContractGroup:
    """将保单转换为IFRS 17合同组"""
    
    contract_group = IFRS17ContractGroup()
    contract_group.group_id = generate_group_id()
    
    # 合同组识别（按IFRS 17组合标准）
    contract_group.portfolio = policy.product_code
    contract_group.profitability = determine_profitability(policy)
    contract_group.initial_recognition_year = policy.effective_date.year
    
    # 选择计量模型
    contract_group.measurement_model = select_measurement_model(policy)
    
    # 初始确认
    contract_group.initial_recognition_date = policy.effective_date
    
    # 履约现金流
    contract_group.fulfilment_cash_flows = calculate_fulfilment_cash_flows(policy)
    
    # 合同服务边际
    contract_group.csm = calculate_csm(contract_group.fulfilment_cash_flows)
    
    # 亏损部分（如适用）
    if contract_group.csm < 0:
        contract_group.loss_component = -contract_group.csm
        contract_group.csm = 0
    
    return contract_group

def determine_profitability(policy: Policy) -> Profitability:
    """确定合同组盈利能力"""
    # 简化逻辑：根据产品类型和定价利润率判断
    profitable_products = ['TERM_LIFE', 'WHOLE_LIFE', 'ENDOWMENT']
    onerous_products = ['GUARANTEED_ANNUITY', 'LONG_TERM_CARE']
    
    if policy.product_type in onerous_products:
        return Profitability.ONEROUS
    elif policy.product_type in profitable_products:
        return Profitability.PROFITABLE
    else:
        return Profitability.PROFITABLE

def select_measurement_model(policy: Policy) -> MeasurementModel:
    """选择计量模型"""
    # 短期合同使用PAA
    if policy.policy_term <= 1:
        return MeasurementModel.PAA
    
    # 具有相机参与分红特征的使用VFA
    if has_discretionary_participation_features(policy):
        return MeasurementModel.VFA
    
    # 默认使用GMM
    return MeasurementModel.GMM
```

### 5.2 履约现金流计算

```python
def calculate_fulfilment_cash_flows(policy: Policy) -> FulfilmentCashFlows:
    """计算履约现金流"""
    
    fcf = FulfilmentCashFlows()
    
    # 未来现金流估计
    future_cf = estimate_future_cash_flows(policy)
    fcf.estimates_of_future_cash_flows = future_cf.total_pv
    
    # 折现效应
    discount_rate = get_discount_rate(policy.currency, policy.policy_term)
    fcf.discount_effect = calculate_discount_effect(future_cf, discount_rate)
    
    # 非金融风险风险调整
    fcf.risk_adjustment = calculate_risk_adjustment(policy, future_cf)
    
    return fcf

def estimate_future_cash_flows(policy: Policy) -> FutureCashFlows:
    """估计未来现金流"""
    
    fcf = FutureCashFlows()
    fcf.cash_flows = []
    
    current_date = datetime.now().date()
    
    # 按年度预测现金流
    for year in range(policy.policy_term):
        projection_date = add_years(current_date, year)
        
        annual_cf = AnnualCashFlow()
        annual_cf.year = year + 1
        annual_cf.date = projection_date
        
        # 保费现金流
        if year < policy.policy_coverages[0].premium_term:
            annual_cf.premium = policy.premium_info.total_premium
        else:
            annual_cf.premium = 0
        
        # 理赔现金流（简化假设）
        claim_rate = get_claim_rate(policy.product_type)
        annual_cf.claims = policy.policy_coverages[0].sum_assured * claim_rate
        
        # 费用现金流
        annual_cf.expenses = get_maintenance_expense(policy) * (1 + 0.02) ** year
        
        # 净现金流
        annual_cf.net_cash_flow = (
            annual_cf.premium - annual_cf.claims - annual_cf.expenses
        )
        
        fcf.cash_flows.append(annual_cf)
    
    # 计算现值
    fcf.total_pv = sum(
        cf.net_cash_flow / ((1 + discount_rate) ** cf.year)
        for cf in fcf.cash_flows
    )
    
    return fcf

def calculate_risk_adjustment(policy: Policy, 
                               future_cf: FutureCashFlows) -> Decimal:
    """计算非金融风险风险调整"""
    
    # 使用置信度技术（75th percentile）
    confidence_level = 0.75
    
    # 计算非金融风险分布
    risk_distribution = simulate_non_financial_risk(policy, future_cf)
    
    # 取分位数
    risk_adjustment = risk_distribution.quantile(confidence_level) - \
                      risk_distribution.expected_value()
    
    return max(0, risk_adjustment)
```

### 5.3 CSM计算与摊销

```python
def calculate_csm(fcf: FulfilmentCashFlows) -> Decimal:
    """计算合同服务边际"""
    
    # CSM = max(0, -PVFP)
    # PVFP = 履约现金流现值（不含融资成分）
    
    pvfp = -fcf.estimates_of_future_cash_flows
    
    csm = max(0, pvfp)
    
    return csm

def amortize_csm(contract_group: IFRS17ContractGroup, 
                 reporting_date: date) -> Decimal:
    """摊销合同服务边际"""
    
    # 计算覆盖范围单位
    coverage_units = calculate_coverage_units(contract_group)
    
    # 当期应摊销单位
    current_period_cu = get_current_period_coverage_units(
        contract_group, reporting_date
    )
    
    # 预计剩余单位
    remaining_cu = sum(cu.units for cu in coverage_units 
                       if cu.period > reporting_date.year)
    
    # 当期摊销比例
    amortization_ratio = current_period_cu / (current_period_cu + remaining_cu)
    
    # 当期摊销金额
    current_amortization = contract_group.csm * amortization_ratio
    
    # 更新CSM
    contract_group.csm -= current_amortization
    
    return current_amortization

def calculate_coverage_units(contract_group: IFRS17ContractGroup) -> List[CoverageUnit]:
    """计算覆盖范围单位"""
    
    coverage_units = []
    
    # 基于保额和保单数量计算
    for year in range(contract_group.remaining_coverage_period):
        cu = CoverageUnit()
        cu.period = contract_group.initial_recognition_year + year
        
        # 考虑预期赔付、保额、保单数量
        expected_claims = estimate_expected_claims(contract_group, year)
        sum_assured = get_remaining_sum_assured(contract_group, year)
        policy_count = get_expected_policy_count(contract_group, year)
        
        # 综合计算单位
        cu.units = expected_claims * 0.4 + sum_assured * 0.3 + policy_count * 0.3
        
        coverage_units.append(cu)
    
    return coverage_units
```

---

## 6. 保险数据存储与分析

### 6.1 PostgreSQL保险数据存储

```python
import psycopg2
import json
from datetime import datetime
from decimal import Decimal

class InsuranceDataStorage:
    """保险业务数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建保险数据表"""
        
        # 保单表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id BIGSERIAL PRIMARY KEY,
                policy_id VARCHAR(30) UNIQUE NOT NULL,
                policy_number VARCHAR(30) UNIQUE NOT NULL,
                proposal_number VARCHAR(30) NOT NULL,
                product_code VARCHAR(20) NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                product_type VARCHAR(30) NOT NULL,
                policy_term INTEGER NOT NULL,
                effective_date DATE NOT NULL,
                expiry_date DATE NOT NULL,
                policy_status VARCHAR(20) NOT NULL,
                channel_type VARCHAR(20) NOT NULL,
                organization_code VARCHAR(20) NOT NULL,
                issue_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 保险责任表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS coverages (
                id BIGSERIAL PRIMARY KEY,
                coverage_id VARCHAR(30) UNIQUE NOT NULL,
                policy_id VARCHAR(30) NOT NULL REFERENCES policies(policy_id),
                coverage_code VARCHAR(10) NOT NULL,
                coverage_name VARCHAR(100) NOT NULL,
                coverage_type VARCHAR(10) NOT NULL,
                sum_assured DECIMAL(15,2) NOT NULL,
                premium DECIMAL(12,2) NOT NULL,
                premium_frequency VARCHAR(20) NOT NULL,
                premium_term INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 理赔表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id BIGSERIAL PRIMARY KEY,
                claim_id VARCHAR(30) UNIQUE NOT NULL,
                claim_number VARCHAR(30) UNIQUE NOT NULL,
                policy_id VARCHAR(30) NOT NULL REFERENCES policies(policy_id),
                coverage_id VARCHAR(30) NOT NULL,
                date_of_loss DATE NOT NULL,
                place_of_loss VARCHAR(200) NOT NULL,
                cause_of_loss VARCHAR(500) NOT NULL,
                reported_date TIMESTAMP NOT NULL,
                incident_type VARCHAR(30) NOT NULL,
                claim_type VARCHAR(30) NOT NULL,
                claim_status VARCHAR(30) NOT NULL,
                assessed_amount DECIMAL(15,2),
                approved_amount DECIMAL(15,2),
                paid_amount DECIMAL(15,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 保费记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS premium_payments (
                id BIGSERIAL PRIMARY KEY,
                payment_id VARCHAR(30) UNIQUE NOT NULL,
                policy_id VARCHAR(30) NOT NULL REFERENCES policies(policy_id),
                payment_type VARCHAR(20) NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                payment_date DATE NOT NULL,
                payment_method VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_claims_policy 
            ON claims(policy_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_claims_status 
            ON claims(claim_status)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_coverages_policy 
            ON coverages(policy_id)
        """)
        
        self.conn.commit()

    def store_policy(self, policy_data: dict):
        """存储保单"""
        self.cur.execute("""
            INSERT INTO policies 
            (policy_id, policy_number, proposal_number, product_code, product_name,
             product_type, policy_term, effective_date, expiry_date, policy_status,
             channel_type, organization_code, issue_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (policy_id) DO UPDATE SET
            policy_status = EXCLUDED.policy_status,
            updated_at = CURRENT_TIMESTAMP
        """, (
            policy_data['policy_id'],
            policy_data['policy_number'],
            policy_data['proposal_number'],
            policy_data['product_code'],
            policy_data['product_name'],
            policy_data['product_type'],
            policy_data['policy_term'],
            policy_data['effective_date'],
            policy_data['expiry_date'],
            policy_data['policy_status'],
            policy_data['channel_type'],
            policy_data['organization_code'],
            policy_data['issue_date']
        ))
        self.conn.commit()

    def store_claim(self, claim_data: dict):
        """存储理赔"""
        self.cur.execute("""
            INSERT INTO claims 
            (claim_id, claim_number, policy_id, coverage_id, date_of_loss,
             place_of_loss, cause_of_loss, reported_date, incident_type,
             claim_type, claim_status, assessed_amount, approved_amount, paid_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (claim_id) DO UPDATE SET
            claim_status = EXCLUDED.claim_status,
            assessed_amount = EXCLUDED.assessed_amount,
            approved_amount = EXCLUDED.approved_amount,
            paid_amount = EXCLUDED.paid_amount,
            updated_at = CURRENT_TIMESTAMP
        """, (
            claim_data['claim_id'],
            claim_data['claim_number'],
            claim_data['policy_id'],
            claim_data['coverage_id'],
            claim_data['date_of_loss'],
            claim_data['place_of_loss'],
            claim_data['cause_of_loss'],
            claim_data['reported_date'],
            claim_data['incident_type'],
            claim_data['claim_type'],
            claim_data['claim_status'],
            claim_data.get('assessed_amount'),
            claim_data.get('approved_amount'),
            claim_data.get('paid_amount')
        ))
        self.conn.commit()
```

### 6.2 保险业务分析查询

```python
class InsuranceAnalytics:
    """保险业务分析查询"""
    
    def __init__(self, storage: InsuranceDataStorage):
        self.storage = storage
    
    def get_premium_summary(self, start_date: date, end_date: date) -> dict:
        """获取保费汇总"""
        self.storage.cur.execute("""
            SELECT 
                product_type,
                COUNT(DISTINCT policy_id) as policy_count,
                SUM(amount) as total_premium
            FROM premium_payments
            WHERE payment_date BETWEEN %s AND %s
            AND status = 'COMPLETED'
            GROUP BY product_type
        """, (start_date, end_date))
        
        results = self.storage.cur.fetchall()
        return {
            row[0]: {
                'policy_count': row[1],
                'total_premium': float(row[2])
            }
            for row in results
        }
    
    def get_claim_statistics(self, start_date: date, end_date: date) -> dict:
        """获取理赔统计"""
        self.storage.cur.execute("""
            SELECT 
                claim_status,
                COUNT(*) as claim_count,
                SUM(assessed_amount) as total_assessed,
                SUM(approved_amount) as total_approved,
                SUM(paid_amount) as total_paid
            FROM claims
            WHERE date_of_loss BETWEEN %s AND %s
            GROUP BY claim_status
        """, (start_date, end_date))
        
        results = self.storage.cur.fetchall()
        return {
            row[0]: {
                'claim_count': row[1],
                'total_assessed': float(row[2]) if row[2] else 0,
                'total_approved': float(row[3]) if row[3] else 0,
                'total_paid': float(row[4]) if row[4] else 0
            }
            for row in results
        }
    
    def get_loss_ratio(self, product_type: str, year: int) -> float:
        """计算赔付率"""
        # 已赚保费
        self.storage.cur.execute("""
            SELECT SUM(amount)
            FROM premium_payments
            WHERE product_type = %s
            AND EXTRACT(YEAR FROM payment_date) = %s
        """, (product_type, year))
        
        earned_premium = self.storage.cur.fetchone()[0] or 0
        
        # 已付赔款
        self.storage.cur.execute("""
            SELECT SUM(paid_amount)
            FROM claims
            WHERE incident_type = %s
            AND EXTRACT(YEAR FROM date_of_loss) = %s
            AND claim_status IN ('PAID', 'CLOSED')
        """, (product_type, year))
        
        incurred_claims = self.storage.cur.fetchone()[0] or 0
        
        if earned_premium == 0:
            return 0.0
        
        return float(incurred_claims / earned_premium)
```

---

## 7. 转换验证与测试

### 7.1 数据一致性验证

```python
class InsuranceDataValidator:
    """保险数据验证器"""
    
    def validate_policy_integrity(self, policy: Policy) -> ValidationResult:
        """验证保单完整性"""
        result = ValidationResult()
        
        # 验证保单期间
        if policy.effective_date >= policy.expiry_date:
            result.add_error("Effective date must be before expiry date")
        
        # 验证保额和保费
        for coverage in policy.policy_coverages:
            if coverage.sum_assured <= 0:
                result.add_error(f"Sum assured must be positive for coverage {coverage.coverage_code}")
            if coverage.premium < 0:
                result.add_error(f"Premium cannot be negative for coverage {coverage.coverage_code}")
        
        # 验证受益人份额
        if policy.policy_parties.beneficiaries:
            total_share = sum(b.share_percentage 
                            for b in policy.policy_parties.beneficiaries)
            if abs(total_share - 100) > 0.01:
                result.add_error(f"Beneficiary shares must sum to 100%, got {total_share}%")
        
        return result
    
    def validate_claim_integrity(self, claim: Claim) -> ValidationResult:
        """验证理赔完整性"""
        result = ValidationResult()
        
        # 验证出险日期在保险期间内
        policy = find_policy(claim.policy_id)
        if not (policy.effective_date <= claim.date_of_loss <= policy.expiry_date):
            result.add_error("Loss date must be within policy period")
        
        # 验证赔款金额
        if claim.claim_calculation:
            if claim.claim_calculation.net_claim_amount < 0:
                result.add_error("Net claim amount cannot be negative")
            
            if claim.claim_payment:
                if claim.claim_payment.payment_amount > claim.claim_calculation.total_payable_amount:
                    result.add_error("Payment amount cannot exceed total payable")
        
        return result
```

### 7.2 业务规则验证

```python
class InsuranceBusinessRules:
    """保险业务规则验证"""
    
    def validate_insurable_interest(self, policy: Policy) -> bool:
        """验证保险利益"""
        # 投保人必须对被保险人有保险利益
        if policy.policy_parties.insured.relationship_to_policyholder == Relationship.SELF:
            return True
        
        valid_relationships = [
            Relationship.SPOUSE,
            Relationship.CHILD,
            Relationship.PARENT
        ]
        
        return policy.policy_parties.insured.relationship_to_policyholder in valid_relationships
    
    def validate_age_limit(self, policy: Policy) -> ValidationResult:
        """验证年龄限制"""
        result = ValidationResult()
        
        insured_age = calculate_age(policy.policy_parties.insured.date_of_birth)
        
        # 不同产品的年龄限制
        age_limits = {
            'TERM_LIFE': (18, 65),
            'WHOLE_LIFE': (0, 70),
            'ENDOWMENT': (0, 60),
            'ANNUITY': (18, 75)
        }
        
        min_age, max_age = age_limits.get(policy.product_type, (0, 100))
        
        if insured_age < min_age:
            result.add_error(f"Insured age {insured_age} below minimum {min_age}")
        
        if insured_age > max_age:
            result.add_error(f"Insured age {insured_age} above maximum {max_age}")
        
        return result
```

---

## 8. 精算计算转换

### 8.1 准备金评估转换

```python
def transform_claims_to_triangle(claims: List[Claim], 
                                  origin_period: str = 'yearly',
                                  development_period: str = 'yearly') -> TriangleData:
    """将理赔数据转换为三角形数据"""
    
    triangle = TriangleData()
    
    # 按事故年和进展年组织数据
    origin_years = sorted(set(get_origin_year(c, origin_period) for c in claims))
    triangle.origin_periods = origin_years
    
    dev_years = list(range(len(origin_years)))
    triangle.development_periods = dev_years
    
    # 构建累积赔款三角形
    values = []
    for origin in origin_years:
        row = []
        for dev in dev_years:
            # 计算累积赔款
            cumulative_paid = sum(
                c.paid_amount for c in claims
                if get_origin_year(c, origin_period) == origin
                and get_development_year(c, origin_period) <= dev
            )
            row.append(cumulative_paid)
        values.append(row)
    
    triangle.values = values
    triangle.cumulative = True
    
    return triangle

def apply_chain_ladder(triangle: TriangleData) -> ReserveEstimate:
    """应用链梯法计算准备金"""
    
    estimate = ReserveEstimate()
    
    # 计算进展因子
    factors = []
    for j in range(len(triangle.development_periods) - 1):
        numerator = sum(triangle.values[i][j+1] 
                       for i in range(len(triangle.values) - j - 1))
        denominator = sum(triangle.values[i][j] 
                         for i in range(len(triangle.values) - j - 1))
        factor = numerator / denominator if denominator > 0 else 1
        factors.append(factor)
    
    # 预测终极赔款
    ultimate_claims = []
    case_reserves = []
    
    for i, origin in enumerate(triangle.origin_periods):
        current_cumulative = triangle.values[i][-1]
        
        # 应用尾部因子预测
        remaining_factor = 1
        for f in factors[i:]:
            remaining_factor *= f
        
        ultimate = current_cumulative * remaining_factor
        ultimate_claims.append(ultimate)
        
        # 未决赔款
        case_reserve = ultimate - current_cumulative
        case_reserves.append(case_reserve)
    
    estimate.case_reserve = sum(case_reserves)
    estimate.ibnr_reserve = estimate.case_reserve * 0.2  # 简化假设
    estimate.total_reserve = estimate.case_reserve + estimate.ibnr_reserve
    
    return estimate
```

### 8.2 保费计算转换

```python
def transform_pricing_to_premium(pricing_model: PricingModel,
                                  insured: Insured) -> PremiumCalculation:
    """将定价模型转换为保费计算"""
    
    calc = PremiumCalculation()
    
    # 基础风险保费
    mortality_rate = get_mortality_rate(
        pricing_model.pricing_assumptions.mortality_table,
        insured.age,
        insured.gender
    )
    
    sum_assured = 100000  # 示例保额
    
    calc.risk_premium = sum_assured * mortality_rate * \
                        pricing_model.pricing_assumptions.mortality_adjustment
    
    # 储蓄保费（如适用）
    if pricing_model.product_type in ['WHOLE_LIFE', 'ENDOWMENT']:
        calc.savings_premium = calculate_savings_premium(
            pricing_model, sum_assured
        )
    
    # 费用保费
    calc.cost_premium = (
        pricing_model.pricing_assumptions.maintenance_expense_per_policy +
        sum_assured * pricing_model.pricing_assumptions.maintenance_expense_rate
    )
    
    # 基础保费
    calc.base_premium = calc.risk_premium + calc.savings_premium
    
    # 附加费用
    acquisition_loading = calc.base_premium * \
                          pricing_model.pricing_assumptions.acquisition_cost_rate
    profit_loading = calc.base_premium * 0.05  # 5%利润附加
    
    calc.loading = acquisition_loading + profit_loading + calc.cost_premium
    
    # 总保费
    calc.total_premium = calc.base_premium + calc.loading
    
    # 分解
    calc.mortality_cost = calc.risk_premium
    calc.expense_loading = calc.loading
    calc.profit_loading = profit_loading
    calc.contingency_loading = 0
    
    return calc
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标

**创建时间**：2025-01-21
**最后更新**：2025-01-21
