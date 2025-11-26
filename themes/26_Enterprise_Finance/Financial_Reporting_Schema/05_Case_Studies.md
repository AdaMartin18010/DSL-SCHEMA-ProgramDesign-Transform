# 财务报告Schema实践案例

## 📑 目录

- [财务报告Schema实践案例](#财务报告schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：财务报表生成](#2-案例1财务报表生成)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：IFRS 18财务报表列报](#3-案例2-ifrs-18财务报表列报)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：财务报告到XBRL转换](#4-案例3财务报告到xbrl转换)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：财务报告分析](#5-案例4财务报告分析)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：财务报告数据存储与分析系统](#6-案例5财务报告数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供财务报告Schema在实际应用中的实践案例。

---

## 2. 案例1：财务报表生成

### 2.1 场景描述

**应用场景**：
基于会计数据生成IFRS格式的财务报表，包括资产负债表、利润表、现金流量表。

**业务需求**：

- 支持IFRS 18财务报表列报标准
- 自动计算报表项目金额
- 支持多期间对比
- 支持XBRL格式导出

### 2.2 Schema定义

**财务报表生成Schema**：

```dsl
schema FinancialStatementsGeneration {
  balance_sheet: BalanceSheet {
    report_date: Date @value("2025-12-31")
    assets: Assets {
      current_assets: Map<String, Decimal> {
        "cash_and_equivalents": Decimal @value(100000.00)
        "accounts_receivable": Decimal @value(200000.00)
        "inventory": Decimal @value(150000.00)
      }
      non_current_assets: Map<String, Decimal> {
        "property_plant_equipment": Decimal @value(500000.00)
        "intangible_assets": Decimal @value(200000.00)
      }
      total_assets: Decimal @value(1150000.00)
    }
    liabilities: Liabilities {
      current_liabilities: Map<String, Decimal> {
        "accounts_payable": Decimal @value(150000.00)
        "short_term_debt": Decimal @value(100000.00)
      }
      non_current_liabilities: Map<String, Decimal> {
        "long_term_debt": Decimal @value(300000.00)
      }
      total_liabilities: Decimal @value(550000.00)
    }
    equity: Equity {
      share_capital: Decimal @value(300000.00)
      retained_earnings: Decimal @value(300000.00)
      total_equity: Decimal @value(600000.00)
    }
    total_liabilities_equity: Decimal @value(1150000.00)
  }

  income_statement: IncomeStatement {
    period_start: Date @value("2025-01-01")
    period_end: Date @value("2025-12-31")
    revenue: Revenue {
      operating_revenue: Map<String, Decimal> {
        "sales_revenue": Decimal @value(2000000.00)
      }
      total_revenue: Decimal @value(2000000.00)
    }
    expenses: Expenses {
      cost_of_sales: Decimal @value(1200000.00)
      operating_expenses: Map<String, Decimal> {
        "selling_expenses": Decimal @value(200000.00)
        "administrative_expenses": Decimal @value(150000.00)
      }
      total_expenses: Decimal @value(1550000.00)
    }
    profit: Profit {
      operating_profit: Decimal @value(600000.00)
      net_profit: Decimal @value(450000.00)
    }
  }
} @standard("IFRS 18")
```

---

## 3. 案例2：IFRS 18财务报表列报

### 3.1 场景描述

**应用场景**：
按照IFRS 18标准生成财务报表，包括经营损益和筹资损益的分类。

**业务需求**：

- 支持IFRS 18财务报表列报标准
- 按经营损益和筹资损益分类
- 支持管理层业绩指标披露

### 3.2 Schema定义

**IFRS 18财务报表列报Schema**：

```dsl
schema IFRS18FinancialStatements {
  income_statement: IFRS18IncomeStatement {
    period_start: Date @value("2025-01-01")
    period_end: Date @value("2025-12-31")
    operating_income: OperatingIncome {
      operating_revenue: Decimal @value(2000000.00)
      operating_expenses: Decimal @value(1400000.00)
      operating_profit: Decimal @value(600000.00)
    }
    financing_income: FinancingIncome {
      financing_revenue: Decimal @value(50000.00)
      financing_expenses: Decimal @value(200000.00)
      financing_profit: Decimal @value(-150000.00)
    }
    profit_before_tax: Decimal @value(450000.00)
    income_tax: Decimal @value(112500.00)
    net_profit: Decimal @value(337500.00)
  }
} @standard("IFRS 18")
```

---

## 4. 案例3：财务报告到XBRL转换

### 4.1 场景描述

**应用场景**：
将企业财务报告转换为XBRL格式，用于向监管机构提交标准化财务报告。

**业务需求**：

- 支持XBRL 2.1标准
- 支持IFRS Taxonomy分类标准
- 自动生成XBRL实例文档
- 支持XBRL验证

### 4.2 Schema定义

**财务报告到XBRL转换Schema**：

```dsl
schema FinancialReportToXBRLConversion {
  financial_report: FinancialReportingSchema {
    company_code: String @value("COMP-001")
    report_date: Date @value("2025-12-31")
    balance_sheet: BalanceSheet {
      assets: Assets {
        current_assets: Map<String, Decimal> {
          "cash_and_equivalents": Decimal @value(100000.00)
        }
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
        element_id: String @value("ifrs:Assets_Current_Cash")
        context_ref: String @value("context_report_date")
        unit_ref: String @value("unit_usd")
        fact_value: String @value("100000.00")
      }
    }
  }
} @standard("XBRL 2.1", "IFRS Taxonomy")
```

---

## 5. 案例4：财务报告分析

### 5.1 场景描述

**应用场景**：
企业财务报告分析，包括财务比率分析、财务趋势分析、财务对比分析。

**业务需求**：

- 计算财务比率
- 分析财务趋势
- 对比不同企业、不同期间的财务报告

### 5.2 实现代码

```python
from financial_reporting_schema import FinancialReportingSchema

def analyze_financial_report(financial_report: FinancialReportingSchema) -> FinancialAnalysis:
    """分析财务报告"""
    analysis = FinancialAnalysis()

    # 计算财务比率
    balance_sheet = financial_report.balance_sheet
    income_statement = financial_report.income_statement

    # 流动比率
    current_assets = sum(balance_sheet.assets.current_assets.values())
    current_liabilities = sum(balance_sheet.liabilities.current_liabilities.values())
    analysis.current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0

    # 资产负债率
    total_liabilities = balance_sheet.total_liabilities
    total_assets = balance_sheet.total_assets
    analysis.debt_to_assets_ratio = total_liabilities / total_assets if total_assets > 0 else 0

    # 净资产收益率
    net_profit = income_statement.profit.net_profit
    total_equity = balance_sheet.total_equity
    analysis.return_on_equity = net_profit / total_equity if total_equity > 0 else 0

    return analysis
```

---

## 6. 案例5：财务报告数据存储与分析系统

### 6.1 场景描述

**应用场景**：
企业财务报告数据存储与分析系统，支持财务报告数据存储、查询、分析和报表生成。

**业务需求**：

- PostgreSQL数据库存储
- 支持复杂查询和分析
- 支持财务比率计算
- 支持财务趋势分析

### 6.2 实现代码

```python
import psycopg2
from financial_reporting_schema import FinancialReportingSchema, BalanceSheet, IncomeStatement

class FinancialReportingDataStore:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def store_financial_report(self, financial_report: FinancialReportingSchema):
        """存储财务报告"""
        cursor = self.conn.cursor()

        report_id = f"FR-{financial_report.company_code}-{financial_report.report_date}"

        # 插入资产负债表
        cursor.execute("""
            INSERT INTO balance_sheets
            (report_id, company_code, report_date, total_assets, total_liabilities, total_equity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (report_id, financial_report.company_code, financial_report.report_date,
              financial_report.balance_sheet.total_assets,
              financial_report.balance_sheet.total_liabilities,
              financial_report.balance_sheet.total_equity))

        # 插入利润表
        cursor.execute("""
            INSERT INTO income_statements
            (report_id, company_code, period_start, period_end, total_revenue, total_expenses, net_profit)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (report_id, financial_report.company_code,
              financial_report.income_statement.period_start,
              financial_report.income_statement.period_end,
              financial_report.income_statement.revenue.total_revenue,
              financial_report.income_statement.expenses.total_expenses,
              financial_report.income_statement.profit.net_profit))

        self.conn.commit()

    def generate_financial_analysis(self, company_code, period_start, period_end):
        """生成财务分析报告"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                bs.report_date,
                bs.total_assets,
                bs.total_liabilities,
                bs.total_equity,
                is_net.net_profit,
                (bs.total_liabilities / NULLIF(bs.total_equity, 0)) as debt_to_equity_ratio,
                (is_net.net_profit / NULLIF(bs.total_assets, 0)) as return_on_assets,
                (is_net.net_profit / NULLIF(bs.total_equity, 0)) as return_on_equity
            FROM balance_sheets bs
            JOIN income_statements is_net ON bs.report_id = is_net.report_id
            WHERE bs.company_code = %s AND bs.report_date BETWEEN %s AND %s
            ORDER BY bs.report_date
        """, (company_code, period_start, period_end))

        return cursor.fetchall()

# 使用示例
db_config = {
    "host": "localhost",
    "database": "financial_reporting",
    "user": "fr_user",
    "password": "password"
}

store = FinancialReportingDataStore(db_config)

# 生成财务分析报告
financial_analysis = store.generate_financial_analysis("COMP-001", "2025-01-01", "2025-12-31")
print("财务分析报告:")
for row in financial_analysis:
    print(f"日期: {row[0]}, 总资产: {row[1]}, 净利润: {row[4]}, ROE: {row[8]:.2f}%")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
