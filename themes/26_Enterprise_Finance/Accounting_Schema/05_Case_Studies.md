# 会计Schema实践案例

## 📑 目录

- [会计Schema实践案例](#会计schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：财务会计凭证处理](#2-案例1财务会计凭证处理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：财务报表生成](#3-案例2财务报表生成)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：成本会计作业成本法](#4-案例3成本会计作业成本法)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：会计到XBRL转换](#5-案例4会计到xbrl转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：会计数据存储与分析系统](#6-案例5会计数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供会计Schema在实际应用中的实践案例。

---

## 2. 案例1：财务会计凭证处理

### 2.1 场景描述

**应用场景**：
企业日常财务会计凭证处理，包括凭证录入、审核、过账等流程。

**业务需求**：
- 支持手工凭证和自动凭证
- 凭证借贷必须平衡
- 支持成本中心分配
- 支持凭证审核流程

### 2.2 Schema定义

**财务会计凭证处理Schema**：

```dsl
schema FinancialJournalEntry {
  entry_id: String @value("JE-2025-001")
  entry_date: Date @value("2025-01-21")
  entry_type: Enum @value("Manual")
  description: String @value("材料采购凭证")

  lines: List<JournalLine> {
    line1: JournalLine {
      account_code: String @value("1001")
      account_name: String @value("库存现金")
      debit_amount: Decimal @value(10000.00)
      credit_amount: Decimal @value(0.00)
      cost_center: String @value("CC-001")
    }

    line2: JournalLine {
      account_code: String @value("1201")
      account_name: String @value("原材料")
      debit_amount: Decimal @value(0.00)
      credit_amount: Decimal @value(10000.00)
      cost_center: String @value("CC-001")
    }
  }

  total_debit: Decimal @value(10000.00)
  total_credit: Decimal @value(10000.00)
  balance: Decimal @value(0.00)
} @standard("IFRS", "GAAP")
```

---

## 3. 案例2：财务报表生成

### 3.1 场景描述

**应用场景**：
基于会计数据生成IFRS格式的财务报表，包括资产负债表、利润表、现金流量表。

**业务需求**：
- 支持IFRS 18财务报表列报标准
- 自动计算报表项目金额
- 支持多期间对比
- 支持XBRL格式导出

### 3.2 Schema定义

**财务报表生成Schema**：

```dsl
schema FinancialStatements {
  balance_sheet: BalanceSheet {
    report_date: Date @value("2025-01-31")
    assets: Map<String, Decimal> {
      "current_assets": Decimal @value(500000.00)
      "non_current_assets": Decimal @value(1000000.00)
    }
    liabilities: Map<String, Decimal> {
      "current_liabilities": Decimal @value(200000.00)
      "non_current_liabilities": Decimal @value(300000.00)
    }
    equity: Map<String, Decimal> {
      "share_capital": Decimal @value(500000.00)
      "retained_earnings": Decimal @value(500000.00)
    }
    total_assets: Decimal @value(1500000.00)
    total_liabilities_equity: Decimal @value(1500000.00)
  }

  income_statement: IncomeStatement {
    period_start: Date @value("2025-01-01")
    period_end: Date @value("2025-01-31")
    revenue: Map<String, Decimal> {
      "sales_revenue": Decimal @value(1000000.00)
      "other_revenue": Decimal @value(50000.00)
    }
    expenses: Map<String, Decimal> {
      "cost_of_sales": Decimal @value(600000.00)
      "operating_expenses": Decimal @value(200000.00)
      "financial_expenses": Decimal @value(10000.00)
    }
    net_income: Decimal @value(240000.00)
  }
} @standard("IFRS 18")
```

---

## 4. 案例3：成本会计作业成本法

### 4.1 场景描述

**应用场景**：
使用作业成本法（ABC）进行产品成本核算，识别作业、成本动因，分配间接成本。

**业务需求**：
- 识别主要作业和成本动因
- 计算作业成本率
- 将间接成本分配到产品
- 支持成本分析和优化

### 4.2 Schema定义

**作业成本法Schema**：

```dsl
schema ActivityBasedCosting {
  activities: List<Activity> {
    activity1: Activity {
      activity_id: String @value("ACT-001")
      activity_name: String @value("机器设置")
      cost_pool: Decimal @value(50000.00)
      cost_driver: String @value("设置次数")
      driver_quantity: Decimal @value(100.00)
      activity_rate: Decimal @value(500.00)
    }

    activity2: Activity {
      activity_id: String @value("ACT-002")
      activity_name: String @value("质量检验")
      cost_pool: Decimal @value(30000.00)
      cost_driver: String @value("检验批次")
      driver_quantity: Decimal @value(50.00)
      activity_rate: Decimal @value(600.00)
    }
  }

  cost_objects: List<ABCCostObject> {
    product1: ABCCostObject {
      object_id: String @value("PROD-001")
      object_code: String @value("产品A")
      direct_costs: Decimal @value(100000.00)
      activity_consumption: Map<String, Decimal> {
        "ACT-001": Decimal @value(20.00)
        "ACT-002": Decimal @value(10.00)
      }
      allocated_costs: Decimal @value(16000.00)
      total_costs: Decimal @value(116000.00)
    }
  }
} @standard("ABC")
```

---

## 5. 案例4：会计到XBRL转换

### 5.1 场景描述

**应用场景**：
将企业会计数据转换为XBRL格式，用于向监管机构提交标准化财务报告。

**业务需求**：
- 支持XBRL 2.1标准
- 支持IFRS Taxonomy分类标准
- 自动生成XBRL实例文档
- 支持XBRL验证

### 5.2 实现代码

```python
from accounting_schema import AccountingSchema
from xbrl import XBRLInstanceDocument, XBRLContext, XBRLFact

def convert_accounting_to_xbrl(accounting_data: AccountingSchema) -> XBRLInstanceDocument:
    """将会计数据转换为XBRL格式"""
    xbrl_doc = XBRLInstanceDocument()

    # 创建实体上下文
    entity_context = XBRLContext()
    entity_context.id = "entity_context_1"
    entity_context.entity_identifier = accounting_data.company_code
    entity_context.entity_scheme = "http://www.example.com/company"
    entity_context.period_start = accounting_data.period_start
    entity_context.period_end = accounting_data.period_end
    xbrl_doc.contexts.append(entity_context)

    # 创建单位
    unit_usd = XBRLUnit()
    unit_usd.id = "unit_usd"
    unit_usd.measure = "iso4217:USD"
    xbrl_doc.units.append(unit_usd)

    # 转换资产负债表数据
    for account in accounting_data.chart_of_accounts:
        if account.account_type == "Asset":
            fact = XBRLFact()
            fact.context_ref = entity_context.id
            fact.unit_ref = unit_usd.id
            fact.name = f"ifrs:Assets_{account.account_code}"
            fact.value = str(account.closing_balance)
            fact.decimals = "2"
            xbrl_doc.facts.append(fact)

    return xbrl_doc

# 使用示例
accounting_data = AccountingSchema.load_from_database("2025-01-31")
xbrl_doc = convert_accounting_to_xbrl(accounting_data)
xbrl_doc.save("financial_report_2025-01-31.xbrl")
```

---

## 6. 案例5：会计数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业会计数据存储与分析系统，支持会计数据存储、查询、分析和报表生成。

**业务需求**：
- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持财务报表生成
- 支持数据导出

### 6.2 实现代码

```python
import psycopg2
from accounting_schema import AccountingSchema, JournalEntry, ChartOfAccounts

class AccountingDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_journal_entry(self, entry: JournalEntry):
        """存储凭证"""
        cursor = self.conn.cursor()

        # 验证借贷平衡
        if entry.total_debit != entry.total_credit:
            raise ValueError("凭证借贷不平衡")

        # 插入凭证
        cursor.execute("""
            INSERT INTO journal_entries
            (entry_id, entry_date, entry_type, description, total_debit, total_credit)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (entry.entry_id, entry.entry_date, entry.entry_type,
              entry.description, entry.total_debit, entry.total_credit))

        # 插入凭证分录
        for line in entry.lines:
            cursor.execute("""
                INSERT INTO journal_lines
                (entry_id, account_code, debit_amount, credit_amount, cost_center)
                VALUES (%s, %s, %s, %s, %s)
            """, (entry.entry_id, line.account_code, line.debit_amount,
                  line.credit_amount, line.cost_center))

        self.conn.commit()

    def generate_trial_balance(self, period_start, period_end):
        """生成试算平衡表"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                coa.account_code,
                coa.account_name,
                COALESCE(SUM(jl.debit_amount), 0) as debit_total,
                COALESCE(SUM(jl.credit_amount), 0) as credit_total,
                COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN journal_lines jl ON coa.account_code = jl.account_code
            LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id
            WHERE (je.entry_date BETWEEN %s AND %s OR je.entry_date IS NULL)
            GROUP BY coa.account_code, coa.account_name
            ORDER BY coa.account_code
        """, (period_start, period_end))

        return cursor.fetchall()

    def generate_balance_sheet(self, report_date):
        """生成资产负债表"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                coa.account_type,
                SUM(gl.closing_balance) as total_balance
            FROM general_ledger gl
            JOIN chart_of_accounts coa ON gl.account_code = coa.account_code
            WHERE gl.period_end = %s
            GROUP BY coa.account_type
        """, (report_date,))

        return cursor.fetchall()

# 使用示例
db_config = {
    "host": "localhost",
    "database": "accounting",
    "user": "accounting_user",
    "password": "password"
}

store = AccountingDataStore(db_config)

# 存储凭证
entry = JournalEntry(
    entry_id="JE-2025-001",
    entry_date="2025-01-21",
    entry_type="Manual",
    description="材料采购",
    lines=[
        JournalLine(account_code="1001", debit_amount=10000, credit_amount=0),
        JournalLine(account_code="1201", debit_amount=0, credit_amount=10000)
    ],
    total_debit=10000,
    total_credit=10000
)
store.store_journal_entry(entry)

# 生成试算平衡表
trial_balance = store.generate_trial_balance("2025-01-01", "2025-01-31")
print("试算平衡表:")
for row in trial_balance:
    print(f"{row[0]}: {row[1]} - 借方: {row[2]}, 贷方: {row[3]}, 余额: {row[4]}")

# 生成资产负债表
balance_sheet = store.generate_balance_sheet("2025-01-31")
print("\n资产负债表:")
for row in balance_sheet:
    print(f"{row[0]}: {row[1]}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
