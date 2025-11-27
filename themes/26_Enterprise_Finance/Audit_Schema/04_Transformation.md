# 审计Schema转换体系

## 📑 目录

- [审计Schema转换体系](#审计schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 财务报告到审计转换](#2-财务报告到审计转换)
  - [3. 审计到报告转换](#3-审计到报告转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 审计数据存储与分析](#5-审计数据存储与分析)
    - [5.1 PostgreSQL审计数据存储](#51-postgresql审计数据存储)
    - [5.2 审计数据分析查询](#52-审计数据分析查询)

---

## 1. 转换体系概述

审计Schema转换体系支持财务报告到审计数据、审计数据到审计报告格式转换，
以及审计数据存储。

### 1.1 转换目标

1. **财务报告到审计转换**：财务报告数据到审计格式
2. **审计到报告转换**：审计数据到审计报告格式
3. **审计到数据库转换**：审计数据到PostgreSQL存储

---

## 2. 财务报告到审计转换

**转换规则**：

- 财务报表项目 → 审计范围
- 财务报表金额 → 审计程序
- 财务报表 → 审计证据

**转换示例**：

```python
def convert_financial_report_to_audit(financial_report: FinancialReportingSchema) -> AuditSchema:
    """将财务报告转换为审计数据"""
    audit_schema = AuditSchema()
    
    # 转换审计范围
    financial_audit = FinancialAudit()
    financial_audit.audit_scope.audit_period_start = financial_report.income_statement.period_start
    financial_audit.audit_scope.audit_period_end = financial_report.income_statement.period_end
    financial_audit.audit_scope.audit_entities = [financial_report.company_code]
    financial_audit.audit_scope.audit_areas = ["Balance Sheet", "Income Statement", "Cash Flow Statement"]
    
    # 转换审计程序
    # 资产负债表审计程序
    balance_sheet_procedure = AuditProcedure()
    balance_sheet_procedure.procedure_id = "PROC-BS-001"
    balance_sheet_procedure.procedure_type = "Inspection"
    balance_sheet_procedure.procedure_description = "检查资产负债表项目余额"
    balance_sheet_procedure.procedure_date = financial_report.report_date
    financial_audit.audit_procedures.append(balance_sheet_procedure)
    
    # 利润表审计程序
    income_statement_procedure = AuditProcedure()
    income_statement_procedure.procedure_id = "PROC-IS-001"
    income_statement_procedure.procedure_type = "Recalculation"
    income_statement_procedure.procedure_description = "重新计算利润表项目"
    income_statement_procedure.procedure_date = financial_report.report_date
    financial_audit.audit_procedures.append(income_statement_procedure)
    
    audit_schema.financial_audit = financial_audit
    
    return audit_schema
```

---

## 3. 审计到报告转换

**转换规则**：

- 审计程序结果 → 审计意见
- 审计证据 → 审计报告内容
- 审计发现 → 审计报告结论

**转换示例**：

```python
def convert_audit_to_report(audit_data: AuditSchema) -> AuditReport:
    """将审计数据转换为审计报告"""
    audit_report = AuditReport()
    
    # 基于审计程序结果形成审计意见
    all_procedures_passed = all(
        proc.procedure_result == "Pass" 
        for proc in audit_data.financial_audit.audit_procedures
    )
    
    if all_procedures_passed:
        audit_opinion = AuditOpinion()
        audit_opinion.opinion_type = "Unqualified"
        audit_opinion.opinion_basis = "财务报表在所有重大方面按照适用的财务报告框架编制"
    else:
        audit_opinion = AuditOpinion()
        audit_opinion.opinion_type = "Qualified"
        audit_opinion.opinion_basis = "除某些事项外，财务报表在所有重大方面按照适用的财务报告框架编制"
    
    audit_report.audit_opinion = audit_opinion
    audit_report.report_date = audit_data.financial_audit.audit_scope.audit_period_end
    audit_report.report_content = generate_audit_report_content(audit_data)
    
    return audit_report
```

---

## 4. 转换工具

### 4.1 审计软件

- **审计管理软件**：审计程序管理、审计证据收集
- **数据分析工具**：审计数据分析、异常检测
- **审计报告生成器**：审计报告自动生成

---

## 5. 审计数据存储与分析

### 5.1 PostgreSQL审计数据存储

**表结构设计**：

```sql
-- 审计程序表
CREATE TABLE audit_procedures (
    procedure_id VARCHAR(50) PRIMARY KEY,
    audit_id VARCHAR(50) NOT NULL,
    procedure_type VARCHAR(50) NOT NULL,
    procedure_description TEXT NOT NULL,
    procedure_date DATE NOT NULL,
    procedure_result VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 审计意见表
CREATE TABLE audit_opinions (
    opinion_id VARCHAR(50) PRIMARY KEY,
    audit_id VARCHAR(50) NOT NULL,
    opinion_type VARCHAR(50) NOT NULL,
    opinion_basis TEXT NOT NULL,
    opinion_date DATE NOT NULL,
    auditor_name VARCHAR(200) NOT NULL
);

-- 控制缺陷表
CREATE TABLE control_deficiencies (
    deficiency_id VARCHAR(50) PRIMARY KEY,
    control_id VARCHAR(50) NOT NULL,
    deficiency_type VARCHAR(50) NOT NULL,
    deficiency_description TEXT NOT NULL,
    deficiency_impact TEXT NOT NULL,
    remediation_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 合规性检查表
CREATE TABLE compliance_checks (
    check_id VARCHAR(50) PRIMARY KEY,
    check_item VARCHAR(200) NOT NULL,
    compliance_standard VARCHAR(200) NOT NULL,
    check_result VARCHAR(50) NOT NULL,
    check_date DATE NOT NULL,
    check_comment TEXT
);

-- 创建索引
CREATE INDEX idx_audit_procedures_audit ON audit_procedures(audit_id);
CREATE INDEX idx_control_deficiencies_control ON control_deficiencies(control_id);
CREATE INDEX idx_compliance_checks_date ON compliance_checks(check_date);
```

**数据插入示例**：

```python
def store_audit_data(audit_data: AuditSchema, conn):
    """存储审计数据到PostgreSQL"""
    cursor = conn.cursor()
    
    audit_id = f"AUDIT-{audit_data.company_code}-{audit_data.financial_audit.audit_scope.audit_period_end}"
    
    # 插入审计程序
    for procedure in audit_data.financial_audit.audit_procedures:
        cursor.execute("""
            INSERT INTO audit_procedures 
            (procedure_id, audit_id, procedure_type, procedure_description, procedure_date, procedure_result)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (procedure.procedure_id, audit_id, procedure.procedure_type,
              procedure.procedure_description, procedure.procedure_date, procedure.procedure_result))
    
    # 插入审计意见
    if audit_data.financial_audit.audit_opinion:
        opinion_id = f"OPINION-{audit_id}"
        cursor.execute("""
            INSERT INTO audit_opinions 
            (opinion_id, audit_id, opinion_type, opinion_basis, opinion_date, auditor_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (opinion_id, audit_id, audit_data.financial_audit.audit_opinion.opinion_type,
              audit_data.financial_audit.audit_opinion.opinion_basis,
              audit_data.financial_audit.audit_opinion.opinion_date,
              audit_data.financial_audit.audit_opinion.auditor_name))
    
    conn.commit()
```

### 5.2 审计数据分析查询

**查询示例**：

```python
def analyze_audit_data(conn, company_code, period_start, period_end):
    """分析审计数据"""
    cursor = conn.cursor()
    
    # 查询审计程序结果
    cursor.execute("""
        SELECT 
            procedure_type,
            COUNT(*) as total_procedures,
            SUM(CASE WHEN procedure_result = 'Pass' THEN 1 ELSE 0 END) as passed_procedures,
            SUM(CASE WHEN procedure_result = 'Fail' THEN 1 ELSE 0 END) as failed_procedures
        FROM audit_procedures ap
        JOIN audits a ON ap.audit_id = a.audit_id
        WHERE a.company_code = %s AND a.audit_period_end BETWEEN %s AND %s
        GROUP BY procedure_type
    """, (company_code, period_start, period_end))
    
    procedure_summary = cursor.fetchall()
    
    # 查询控制缺陷
    cursor.execute("""
        SELECT 
            deficiency_type,
            COUNT(*) as deficiency_count
        FROM control_deficiencies
        WHERE created_at BETWEEN %s AND %s
        GROUP BY deficiency_type
        ORDER BY deficiency_count DESC
    """, (period_start, period_end))
    
    deficiency_summary = cursor.fetchall()
    
    return {
        "procedure_summary": procedure_summary,
        "deficiency_summary": deficiency_summary
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21

