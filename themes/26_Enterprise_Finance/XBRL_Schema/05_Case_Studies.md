# XBRL Schema实践案例

## 📑 目录

- [XBRL Schema实践案例](#xbrl-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：会计数据到XBRL转换](#2-案例1会计数据到xbrl转换)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：财务报告到XBRL转换](#3-案例2财务报告到xbrl转换)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：XBRL验证](#4-案例3xbrl验证)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：XBRL数据存储与分析](#5-案例4xbrl数据存储与分析)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：XBRL监管报告提交](#6-案例5xbrl监管报告提交)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供XBRL Schema在实际应用中的实践案例。

---

## 2. 案例1：会计数据到XBRL转换

### 2.1 场景描述

**应用场景**：
将企业会计数据转换为XBRL格式，用于向监管机构提交标准化财务报告。

**业务需求**：

- 支持XBRL 2.1标准
- 支持IFRS Taxonomy分类标准
- 自动生成XBRL实例文档
- 支持XBRL验证

### 2.2 Schema定义

**会计数据到XBRL转换Schema**：

```dsl
schema AccountingToXBRLConversion {
  accounting_data: AccountingSchema {
    company_code: String @value("COMP-001")
    period_start: Date @value("2025-01-01")
    period_end: Date @value("2025-12-31")
    chart_of_accounts: List<Account> {
      account1: Account {
        account_code: String @value("1001")
        account_name: String @value("库存现金")
        account_type: Enum @value("Asset")
        closing_balance: Decimal @value(100000.00)
      }
    }
  }

  xbrl_instance: XBRLInstanceDocument {
    context: ContextElement {
      context_id: String @value("context_entity_period")
      entity_identifier: String @value("COMP-001")
      period_type: Enum @value("Duration")
      period_start: Date @value("2025-01-01")
      period_end: Date @value("2025-12-31")
    }
    facts: List<FactElement> {
      fact1: FactElement {
        element_id: String @value("ifrs:Assets_Cash")
        context_ref: String @value("context_entity_period")
        unit_ref: String @value("unit_usd")
        fact_value: String @value("100000.00")
      }
    }
  }
} @standard("XBRL 2.1", "IFRS Taxonomy")
```

---

## 3. 案例2：财务报告到XBRL转换

### 3.1 场景描述

**应用场景**：
将企业财务报告转换为XBRL格式，用于财务报告标准化和监管报告。

**业务需求**：

- 支持IFRS 18财务报表列报标准
- 支持XBRL实例文档生成
- 支持XBRL验证

### 3.2 Schema定义

**财务报告到XBRL转换Schema**：

```dsl
schema FinancialReportToXBRLConversion {
  financial_report: FinancialReportingSchema {
    company_code: String @value("COMP-001")
    report_date: Date @value("2025-12-31")
    balance_sheet: BalanceSheet {
      assets: Map<String, Decimal> {
        "current_assets": Decimal @value(500000.00)
        "non_current_assets": Decimal @value(1000000.00)
      }
    }
  }

  xbrl_instance: XBRLInstanceDocument {
    context: ContextElement {
      context_id: String @value("context_report_date")
      entity_identifier: String @value("COMP-001")
      period_type: Enum @value("Instant")
      period_end: Date @value("2025-12-31")
    }
    facts: List<FactElement> {
      fact1: FactElement {
        element_id: String @value("ifrs:Assets_Current")
        context_ref: String @value("context_report_date")
        unit_ref: String @value("unit_usd")
        fact_value: String @value("500000.00")
      }
    }
  }
} @standard("XBRL 2.1", "IFRS 18")
```

---

## 4. 案例3：XBRL验证

### 4.1 场景描述

**应用场景**：
验证XBRL实例文档的正确性，确保符合XBRL标准和分类标准要求。

**业务需求**：

- 验证实例文档结构
- 验证分类标准引用
- 验证链接库一致性
- 验证计算链接库

### 4.2 Schema定义

**XBRL验证Schema**：

```dsl
schema XBRLValidation {
  xbrl_instance: XBRLInstanceDocument {
    document_id: String @value("XBRL-COMP-001-2025-12-31")
    contexts: List<ContextElement> {
      context1: ContextElement {
        context_id: String @value("context_entity_period")
        entity_identifier: String @value("COMP-001")
      }
    }
    facts: List<FactElement> {
      fact1: FactElement {
        context_ref: String @value("context_entity_period")
        unit_ref: String @value("unit_usd")
      }
    }
  }

  validation_result: ValidationResult {
    is_valid: Boolean @value(true)
    errors: List<String> @value([])
    warnings: List<String> @value([])
  }
} @standard("XBRL 2.1")
```

---

## 5. 案例4：XBRL数据存储与分析

### 5.1 场景描述

**应用场景**：
XBRL数据存储与分析系统，支持XBRL数据存储、查询、分析和报表生成。

**业务需求**：

- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持XBRL数据对比分析
- 支持XBRL数据挖掘

### 5.2 实现代码

```python
import psycopg2
from xbrl_schema import XBRLInstanceDocument, XBRLFact

class XBRLDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_xbrl_instance(self, xbrl_doc: XBRLInstanceDocument):
        """存储XBRL实例文档"""
        cursor = self.conn.cursor()

        document_id = f"XBRL-{xbrl_doc.company_code}-{xbrl_doc.report_date}"

        # 插入实例文档
        cursor.execute("""
            INSERT INTO xbrl_instance_documents
            (document_id, company_code, report_date, taxonomy_version)
            VALUES (%s, %s, %s, %s)
        """, (document_id, xbrl_doc.company_code, xbrl_doc.report_date, "IFRS-2025"))

        # 插入事实元素
        for fact in xbrl_doc.facts:
            fact_id = f"{document_id}-{fact.element_id}"
            cursor.execute("""
                INSERT INTO xbrl_facts
                (fact_id, document_id, element_id, context_id, unit_id, fact_value, decimals)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (fact_id, document_id, fact.element_id, fact.context_ref,
                  fact.unit_ref, fact.value, fact.decimals))

        self.conn.commit()

    def analyze_xbrl_data(self, company_code, report_date):
        """分析XBRL数据"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                te.element_name,
                xf.fact_value
            FROM xbrl_facts xf
            JOIN xbrl_taxonomy_elements te ON xf.element_id = te.element_id
            JOIN xbrl_instance_documents xid ON xf.document_id = xid.document_id
            WHERE xid.company_code = %s AND xid.report_date = %s
            ORDER BY te.element_name
        """, (company_code, report_date))

        return cursor.fetchall()

# 使用示例
db_config = {
    "host": "localhost",
    "database": "xbrl",
    "user": "xbrl_user",
    "password": "password"
}

store = XBRLDataStore(db_config)

# 分析XBRL数据
xbrl_data = store.analyze_xbrl_data("COMP-001", "2025-12-31")
print("XBRL财务数据:")
for row in xbrl_data:
    print(f"{row[0]}: {row[1]}")
```

---

## 6. 案例5：XBRL监管报告提交

### 6.1 场景描述

**应用场景**：
企业向监管机构提交XBRL格式的财务报告，包括报告生成、验证、提交。

**业务需求**：

- 生成XBRL格式财务报告
- 验证XBRL报告正确性
- 提交XBRL报告到监管机构
- 跟踪报告提交状态

### 6.2 实现代码

```python
from xbrl_schema import XBRLInstanceDocument
from accounting_schema import AccountingSchema

def generate_and_submit_xbrl_report(accounting_data: AccountingSchema, regulator_api):
    """生成并提交XBRL报告"""
    # 转换为XBRL
    xbrl_doc = convert_accounting_to_xbrl(accounting_data)

    # 验证XBRL
    validation_result = validate_xbrl_instance(xbrl_doc)
    if not validation_result.is_valid:
        raise ValueError(f"XBRL validation failed: {validation_result.errors}")

    # 提交到监管机构
    submission_result = regulator_api.submit_xbrl_report(xbrl_doc)

    return submission_result
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
