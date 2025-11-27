# 审计Schema实践案例

## 📑 目录

- [审计Schema实践案例](#审计schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：财务报表审计](#2-案例1财务报表审计)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：内部控制审计](#3-案例2内部控制审计)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：合规性审计](#4-案例3合规性审计)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：财务报告到审计转换](#5-案例4财务报告到审计转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：审计数据存储与分析系统](#6-案例5审计数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供审计Schema在实际应用中的实践案例。

---

## 2. 案例1：财务报表审计

### 2.1 场景描述

**应用场景**：
企业财务报表审计，包括审计程序执行、审计证据收集、审计意见形成。

**业务需求**：

- 执行财务报表审计程序
- 收集充分适当的审计证据
- 形成审计意见
- 出具审计报告

### 2.2 Schema定义

**财务报表审计Schema**：

```dsl
schema FinancialStatementAudit {
  audit_scope: AuditScope {
    audit_period_start: Date @value("2025-01-01")
    audit_period_end: Date @value("2025-12-31")
    audit_entities: List<String> @value(["COMP-001"])
    audit_areas: List<String> @value(["Balance Sheet", "Income Statement", "Cash Flow Statement"])
  }

  audit_procedures: List<AuditProcedure> {
    procedure1: AuditProcedure {
      procedure_id: String @value("PROC-BS-001")
      procedure_type: Enum @value("Inspection")
      procedure_description: String @value("检查资产负债表项目余额")
      procedure_date: Date @value("2025-12-31")
      procedure_result: Enum @value("Pass")
    }
    procedure2: AuditProcedure {
      procedure_id: String @value("PROC-IS-001")
      procedure_type: Enum @value("Recalculation")
      procedure_description: String @value("重新计算利润表项目")
      procedure_date: Date @value("2025-12-31")
      procedure_result: Enum @value("Pass")
    }
  }

  audit_opinion: AuditOpinion {
    opinion_type: Enum @value("Unqualified")
    opinion_basis: String @value("财务报表在所有重大方面按照IFRS编制")
    opinion_date: Date @value("2026-02-15")
    auditor_name: String @value("ABC会计师事务所")
  }

  audit_report: AuditReport {
    report_id: String @value("AUDIT-REPORT-2025")
    report_date: Date @value("2026-02-15")
    report_content: String @value("审计报告内容...")
    audit_opinion: AuditOpinion @ref("audit_opinion")
    auditor_signature: String @value("ABC会计师事务所")
  }
} @standard("ISA")
```

---

## 3. 案例2：内部控制审计

### 3.1 场景描述

**应用场景**：
企业内部控制审计，包括控制环境评价、控制活动测试、控制缺陷识别。

**业务需求**：

- 评价内部控制环境
- 测试控制活动有效性
- 识别控制缺陷
- 制定改进建议

### 3.2 Schema定义

**内部控制审计Schema**：

```dsl
schema InternalControlAudit {
  control_environment: ControlEnvironment {
    control_environment_id: String @value("CE-001")
    management_philosophy: String @value("管理层重视内部控制")
    organizational_structure: String @value("组织结构清晰，权责明确")
    control_environment_rating: Enum @value("Effective")
  }

  control_activities: List<ControlActivity> {
    control1: ControlActivity {
      control_id: String @value("CTRL-001")
      control_type: Enum @value("Preventive")
      control_description: String @value("采购审批控制")
      control_frequency: Enum @value("Continuous")
      control_effectiveness: Enum @value("Effective")
    }
  }

  control_deficiencies: List<ControlDeficiency> {
    deficiency1: ControlDeficiency {
      deficiency_id: String @value("DEF-001")
      control_id: String @value("CTRL-002")
      deficiency_type: Enum @value("Deficiency")
      deficiency_description: String @value("库存盘点控制执行不充分")
      deficiency_impact: String @value("可能导致库存账实不符")
      remediation_plan: String @value("加强库存盘点频率和程序")
    }
  }
} @standard("COSO", "SOX")
```

---

## 4. 案例3：合规性审计

### 4.1 场景描述

**应用场景**：
企业合规性审计，包括合规性检查、合规性报告、违规事项管理。

**业务需求**：

- 检查合规性要求
- 生成合规性报告
- 管理违规事项
- 采取纠正措施

### 4.2 Schema定义

**合规性审计Schema**：

```dsl
schema ComplianceAudit {
  compliance_checks: List<ComplianceCheck> {
    check1: ComplianceCheck {
      check_id: String @value("CHECK-001")
      check_item: String @value("财务报告披露")
      compliance_standard: String @value("IFRS 18")
      check_result: Enum @value("Compliant")
      check_date: Date @value("2025-12-31")
    }
  }

  compliance_reports: List<ComplianceReport> {
    report1: ComplianceReport {
      report_id: String @value("COMP-REPORT-2025")
      report_period_start: Date @value("2025-01-01")
      report_period_end: Date @value("2025-12-31")
      compliance_status: Enum @value("Fully_Compliant")
      compliance_summary: String @value("企业完全符合所有合规性要求")
      report_date: Date @value("2026-01-15")
    }
  }

  violations: List<Violation> {
    violation1: Violation {
      violation_id: String @value("VIOL-001")
      violation_type: Enum @value("Regulatory")
      violation_severity: Enum @value("Low")
      violation_description: String @value("税务申报延迟")
      violation_date: Date @value("2025-02-20")
      violation_status: Enum @value("Resolved")
      remediation_action: String @value("已补报并缴纳滞纳金")
    }
  }
} @standard("Compliance")
```

---

## 5. 案例4：财务报告到审计转换

### 5.1 场景描述

**应用场景**：
将企业财务报告转换为审计数据，用于财务报表审计。

**业务需求**：

- 财务报告数据转换为审计范围
- 财务报表项目转换为审计程序
- 财务报表金额转换为审计证据

### 5.2 实现代码

```python
from financial_reporting_schema import FinancialReportingSchema
from audit_schema import AuditSchema, FinancialAudit, AuditProcedure

def convert_financial_report_to_audit(financial_report: FinancialReportingSchema) -> AuditSchema:
    """将财务报告转换为审计数据"""
    audit_schema = AuditSchema()
    audit_schema.company_code = financial_report.company_code
    
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

# 使用示例
financial_report = FinancialReportingSchema.load_from_database("2025-12-31")
audit_data = convert_financial_report_to_audit(financial_report)
audit_data.save_to_database()
```

---

## 6. 案例5：审计数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业审计数据存储与分析系统，支持审计数据存储、查询、分析和报表生成。

**业务需求**：

- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持审计程序结果分析
- 支持控制缺陷分析

### 6.2 实现代码

```python
import psycopg2
from audit_schema import AuditSchema, FinancialAudit, ControlDeficiency

class AuditDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
    
    def store_audit_data(self, audit_data: AuditSchema):
        """存储审计数据"""
        cursor = self.conn.cursor()
        
        audit_id = f"AUDIT-{audit_data.company_code}-{audit_data.financial_audit.audit_scope.audit_period_end}"
        
        # 插入审计程序
        for procedure in audit_data.financial_audit.audit_procedures:
            cursor.execute("""
                INSERT INTO audit_procedures 
                (procedure_id, audit_id, procedure_type, procedure_description, procedure_date, procedure_result)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (procedure.procedure_id, audit_id, procedure.procedure_type,
                  procedure.procedure_description, procedure.procedure_date, procedure.procedure_result))
        
        # 插入控制缺陷
        for deficiency in audit_data.internal_control_audit.control_deficiencies:
            cursor.execute("""
                INSERT INTO control_deficiencies 
                (deficiency_id, control_id, deficiency_type, deficiency_description, deficiency_impact, remediation_plan)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (deficiency.deficiency_id, deficiency.control_id,
                  deficiency.deficiency_type, deficiency.deficiency_description,
                  deficiency.deficiency_impact, deficiency.remediation_plan))
        
        self.conn.commit()
    
    def generate_audit_analysis(self, company_code, period_start, period_end):
        """生成审计分析报告"""
        cursor = self.conn.cursor()
        
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

# 使用示例
db_config = {
    "host": "localhost",
    "database": "audit",
    "user": "audit_user",
    "password": "password"
}

store = AuditDataStore(db_config)

# 生成审计分析报告
audit_analysis = store.generate_audit_analysis("COMP-001", "2025-01-01", "2025-12-31")
print("审计程序结果:")
for row in audit_analysis["procedure_summary"]:
    print(f"{row[0]}: 总计={row[1]}, 通过={row[2]}, 失败={row[3]}")

print("\n控制缺陷:")
for row in audit_analysis["deficiency_summary"]:
    print(f"{row[0]}: {row[1]}个")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21

