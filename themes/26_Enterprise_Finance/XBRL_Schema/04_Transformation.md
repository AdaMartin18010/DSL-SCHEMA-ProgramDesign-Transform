# XBRL Schema转换体系

## 📑 目录

- [XBRL Schema转换体系](#xbrl-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. 会计到XBRL转换](#2-会计到xbrl转换)
  - [3. 财务报告到XBRL转换](#3-财务报告到xbrl转换)
  - [4. XBRL验证](#4-xbrl验证)
  - [5. XBRL数据存储与分析](#5-xbrl数据存储与分析)
    - [5.1 PostgreSQL XBRL数据存储](#51-postgresql-xbrl数据存储)
    - [5.2 XBRL数据分析查询](#52-xbrl数据分析查询)

---

## 1. 转换体系概述

XBRL Schema转换体系支持会计数据、财务报告数据到XBRL格式转换，
以及XBRL数据存储。

### 1.1 转换目标

1. **会计到XBRL转换**：会计数据到XBRL实例文档
2. **财务报告到XBRL转换**：财务报告到XBRL实例文档
3. **XBRL到数据库转换**：XBRL数据到PostgreSQL存储

---

## 2. 会计到XBRL转换

**转换规则**：

- 会计科目 → XBRL Taxonomy Element
- 凭证数据 → XBRL Fact Element
- 财务报表 → XBRL Instance Document

**转换示例**：

```python
def convert_accounting_to_xbrl(accounting_data: AccountingSchema) -> XBRLInstanceDocument:
    """将会计数据转换为XBRL格式"""
    xbrl_doc = XBRLInstanceDocument()

    # 创建上下文
    context = XBRLContext()
    context.id = "context_entity_period"
    context.entity_identifier = accounting_data.company_code
    context.entity_scheme = "http://www.example.com/company"
    context.period_type = "Duration"
    context.period_start = accounting_data.period_start
    context.period_end = accounting_data.period_end
    xbrl_doc.contexts.append(context)

    # 创建单位
    unit = XBRLUnit()
    unit.id = "unit_usd"
    unit.measure = "iso4217:USD"
    xbrl_doc.units.append(unit)

    # 转换会计科目余额
    for account in accounting_data.chart_of_accounts:
        fact = XBRLFact()
        fact.element_id = f"ifrs:Assets_{account.account_code}"
        fact.context_ref = context.id
        fact.unit_ref = unit.id
        fact.value = str(account.closing_balance)
        fact.decimals = "2"
        xbrl_doc.facts.append(fact)

    return xbrl_doc
```

---

## 3. 财务报告到XBRL转换

**转换规则**：

- 财务报表项目 → XBRL Taxonomy Element
- 财务报表金额 → XBRL Fact Element
- 财务报表 → XBRL Instance Document

**转换示例**：

```python
def convert_financial_report_to_xbrl(financial_report: FinancialReportingSchema) -> XBRLInstanceDocument:
    """将财务报告转换为XBRL格式"""
    xbrl_doc = XBRLInstanceDocument()

    # 创建上下文
    context = XBRLContext()
    context.id = "context_report_date"
    context.entity_identifier = financial_report.company_code
    context.period_type = "Instant"
    context.period_end = financial_report.report_date
    xbrl_doc.contexts.append(context)

    # 转换资产负债表
    for asset_item in financial_report.balance_sheet.assets:
        fact = XBRLFact()
        fact.element_id = f"ifrs:Assets_{asset_item.account_code}"
        fact.context_ref = context.id
        fact.unit_ref = "unit_usd"
        fact.value = str(asset_item.amount)
        xbrl_doc.facts.append(fact)

    return xbrl_doc
```

---

## 4. XBRL验证

**验证规则**：

- 实例文档验证：验证实例文档结构正确性
- 分类标准验证：验证分类标准正确性
- 链接库验证：验证链接库正确性
- 计算验证：验证计算链接库一致性

**验证示例**：

```python
def validate_xbrl_instance(xbrl_doc: XBRLInstanceDocument) -> ValidationResult:
    """验证XBRL实例文档"""
    result = ValidationResult()

    # 验证上下文引用
    for fact in xbrl_doc.facts:
        context_exists = any(c.id == fact.context_ref for c in xbrl_doc.contexts)
        if not context_exists:
            result.add_error(f"Fact {fact.fact_id} references invalid context {fact.context_ref}")

    # 验证单位引用
    for fact in xbrl_doc.facts:
        unit_exists = any(u.id == fact.unit_ref for u in xbrl_doc.units)
        if not unit_exists:
            result.add_error(f"Fact {fact.fact_id} references invalid unit {fact.unit_ref}")

    # 验证计算链接库
    for calculation in xbrl_doc.linkbases.calculation_linkbase.calculations:
        total_weight = sum(c.weight for c in calculation.calculations)
        if abs(total_weight) != 1:
            result.add_error(f"Calculation {calculation.from_element} has invalid weight sum: {total_weight}")

    return result
```

---

## 5. XBRL数据存储与分析

### 5.1 PostgreSQL XBRL数据存储

**表结构设计**：

```sql
-- XBRL分类元素表
CREATE TABLE xbrl_taxonomy_elements (
    element_id VARCHAR(100) PRIMARY KEY,
    element_name VARCHAR(200) NOT NULL,
    element_type VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    period_type VARCHAR(50) NOT NULL,
    balance_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- XBRL实例文档表
CREATE TABLE xbrl_instance_documents (
    document_id VARCHAR(50) PRIMARY KEY,
    company_code VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    taxonomy_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- XBRL事实元素表
CREATE TABLE xbrl_facts (
    fact_id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50) NOT NULL,
    element_id VARCHAR(100) NOT NULL,
    context_id VARCHAR(50) NOT NULL,
    unit_id VARCHAR(50) NOT NULL,
    fact_value DECIMAL(18, 2) NOT NULL,
    decimals INTEGER,
    FOREIGN KEY (document_id) REFERENCES xbrl_instance_documents(document_id),
    FOREIGN KEY (element_id) REFERENCES xbrl_taxonomy_elements(element_id)
);

-- 创建索引
CREATE INDEX idx_xbrl_facts_document ON xbrl_facts(document_id);
CREATE INDEX idx_xbrl_facts_element ON xbrl_facts(element_id);
```

**数据插入示例**：

```python
def store_xbrl_data(xbrl_doc: XBRLInstanceDocument, conn):
    """存储XBRL数据到PostgreSQL"""
    cursor = conn.cursor()

    # 插入实例文档
    document_id = f"XBRL-{xbrl_doc.company_code}-{xbrl_doc.report_date}"
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

    conn.commit()
```

### 5.2 XBRL数据分析查询

**查询示例**：

```python
def analyze_xbrl_data(conn, company_code, report_date):
    """分析XBRL数据"""
    cursor = conn.cursor()

    # 查询财务报表数据
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

    financial_data = cursor.fetchall()

    return financial_data
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
