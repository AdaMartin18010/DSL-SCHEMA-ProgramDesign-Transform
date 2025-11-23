# ERP Schema转换体系

## 📑 目录

- [ERP Schema转换体系](#erp-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. ERP到OAGIS转换](#2-erp到oagis转换)
  - [3. ERP到ISA-95转换](#3-erp到isa-95转换)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. ERP数据存储与分析](#6-erp数据存储与分析)
    - [6.1 PostgreSQL ERP数据存储](#61-postgresql-erp数据存储)
    - [6.2 ERP数据分析查询](#62-erp数据分析查询)

---

## 1. 转换体系概述

ERP Schema转换体系支持ERP系统间数据交换、
ERP到OAGIS/ISA-95转换，以及ERP数据存储。

### 1.1 转换目标

1. **ERP到OAGIS转换**：ERP数据到OAGIS BOD格式
2. **ERP到ISA-95转换**：ERP数据到ISA-95格式
3. **ERP到数据库转换**：ERP数据到PostgreSQL存储

---

## 2. ERP到OAGIS转换

**转换规则**：

- ERP财务数据 → OAGIS ProcessPurchaseOrder
- ERP销售订单 → OAGIS ProcessSalesOrder
- ERP库存数据 → OAGIS SyncInventory

**转换示例**：

```python
def convert_erp_to_oagis_purchase_order(erp_po: PurchaseOrder) -> OAGISProcessPurchaseOrder:
    """将ERP采购订单转换为OAGIS格式"""
    oagis_po = OAGISProcessPurchaseOrder()

    # 转换基本信息
    oagis_po.application_area.creation_date_time = erp_po.order_date
    oagis_po.data_area.purchase_order_header.document_id = erp_po.po_number

    # 转换供应商信息
    oagis_po.data_area.purchase_order_header.supplier_party.party_id = erp_po.supplier_id

    # 转换订单行项
    for item in erp_po.items:
        line_item = OAGISLineItem()
        line_item.line_number = item.line_number
        line_item.item_id = item.item_code
        line_item.quantity = item.quantity
        line_item.unit_price = item.unit_price
        oagis_po.data_area.purchase_order_line.append(line_item)

    return oagis_po
```

---

## 3. ERP到ISA-95转换

**转换规则**：

- ERP生产订单 → ISA-95 ProductionSchedule
- ERP物料清单 → ISA-95 BillOfMaterial
- ERP工艺路线 → ISA-95 ProductionCapability

**转换示例**：

```python
def convert_erp_to_isa95_production_schedule(erp_order: ProductionOrder) -> ISA95ProductionSchedule:
    """将ERP生产订单转换为ISA-95格式"""
    isa95_schedule = ISA95ProductionSchedule()

    # 转换基本信息
    isa95_schedule.id = erp_order.order_number
    isa95_schedule.start_time = erp_order.start_date
    isa95_schedule.end_time = erp_order.end_date

    # 转换产品信息
    isa95_schedule.product_segment.product_id = erp_order.product_code
    isa95_schedule.product_segment.quantity = erp_order.quantity

    # 转换BOM信息
    bom = get_bom(erp_order.product_code, erp_order.bom_version)
    for component in bom.components:
        material = ISA95Material()
        material.material_id = component.component_code
        material.quantity = component.quantity
        isa95_schedule.material_requirements.append(material)

    return isa95_schedule
```

---

## 4. 转换工具

- **SAP PI/PO**：SAP流程集成/流程编排
- **Oracle Integration Cloud**：Oracle云集成平台
- **MuleSoft**：企业集成平台
- **自定义转换器**：基于Schema的转换器

---

## 5. 转换验证

验证转换的数据完整性、格式正确性和业务逻辑一致性。

---

## 6. ERP数据存储与分析

### 6.1 PostgreSQL ERP数据存储

**ERP数据存储方案**：

```python
import psycopg2
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal

logger = logging.getLogger(__name__)

class ERPStorage:
    """ERP数据存储系统 - 增强错误处理"""

    def __init__(self, connection_string: str):
        # 输入验证
        if not connection_string:
            raise ValueError("Connection string cannot be empty")

        if not isinstance(connection_string, str):
            raise TypeError(f"Connection string must be a string, got {type(connection_string)}")

        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor()
            self._create_tables()
            logger.info("ERPStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing ERPStorage: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize ERPStorage: {e}") from e

    def _create_tables(self):
        """创建ERP数据表"""
        # 财务模块表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS chart_of_accounts (
                account_code VARCHAR(20) PRIMARY KEY,
                account_name VARCHAR(200) NOT NULL,
                account_type VARCHAR(50) NOT NULL,
                parent_account VARCHAR(20),
                level INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                entry_id VARCHAR(50) PRIMARY KEY,
                entry_date DATE NOT NULL,
                entry_type VARCHAR(50) NOT NULL,
                description TEXT,
                total_debit NUMERIC(18, 2) NOT NULL,
                total_credit NUMERIC(18, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS journal_lines (
                id SERIAL PRIMARY KEY,
                entry_id VARCHAR(50) NOT NULL,
                account_code VARCHAR(20) NOT NULL,
                debit_amount NUMERIC(18, 2) DEFAULT 0,
                credit_amount NUMERIC(18, 2) DEFAULT 0,
                cost_center VARCHAR(50),
                FOREIGN KEY (entry_id) REFERENCES journal_entries(entry_id),
                FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code)
            )
        """)

        # 供应链模块表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS purchase_orders (
                po_number VARCHAR(50) PRIMARY KEY,
                supplier_id VARCHAR(50) NOT NULL,
                order_date DATE NOT NULL,
                delivery_date DATE,
                status VARCHAR(50) NOT NULL,
                total_amount NUMERIC(18, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS purchase_order_items (
                id SERIAL PRIMARY KEY,
                po_number VARCHAR(50) NOT NULL,
                item_code VARCHAR(50) NOT NULL,
                quantity NUMERIC(18, 3) NOT NULL,
                unit_price NUMERIC(18, 2) NOT NULL,
                total_amount NUMERIC(18, 2) NOT NULL,
                FOREIGN KEY (po_number) REFERENCES purchase_orders(po_number)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sales_orders (
                so_number VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50) NOT NULL,
                order_date DATE NOT NULL,
                delivery_date DATE,
                status VARCHAR(50) NOT NULL,
                total_amount NUMERIC(18, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                item_code VARCHAR(50) PRIMARY KEY,
                item_name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                unit_of_measure VARCHAR(20) NOT NULL,
                current_stock NUMERIC(18, 3) NOT NULL DEFAULT 0,
                reorder_point NUMERIC(18, 3) DEFAULT 0,
                max_stock NUMERIC(18, 3),
                unit_cost NUMERIC(18, 2),
                total_value NUMERIC(18, 2),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 生产制造模块表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS production_orders (
                order_number VARCHAR(50) PRIMARY KEY,
                product_code VARCHAR(50) NOT NULL,
                quantity NUMERIC(18, 3) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                status VARCHAR(50) NOT NULL,
                bom_version VARCHAR(20) NOT NULL,
                routing_version VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bills_of_material (
                bom_id VARCHAR(50) PRIMARY KEY,
                product_code VARCHAR(50) NOT NULL,
                version VARCHAR(20) NOT NULL,
                effective_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_code, version)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bom_components (
                id SERIAL PRIMARY KEY,
                bom_id VARCHAR(50) NOT NULL,
                component_code VARCHAR(50) NOT NULL,
                quantity NUMERIC(18, 3) NOT NULL,
                unit_of_measure VARCHAR(20) NOT NULL,
                scrap_percentage NUMERIC(5, 2) DEFAULT 0,
                FOREIGN KEY (bom_id) REFERENCES bills_of_material(bom_id)
            )
        """)

        # 人力资源模块表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id VARCHAR(50) PRIMARY KEY,
                employee_name VARCHAR(200) NOT NULL,
                department VARCHAR(100) NOT NULL,
                position VARCHAR(100) NOT NULL,
                hire_date DATE NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                manager_id VARCHAR(50),
                status VARCHAR(50) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS payroll_records (
                record_id VARCHAR(50) PRIMARY KEY,
                employee_id VARCHAR(50) NOT NULL,
                pay_period_start DATE NOT NULL,
                pay_period_end DATE NOT NULL,
                base_salary NUMERIC(18, 2) NOT NULL,
                allowances JSONB DEFAULT '{}',
                deductions JSONB DEFAULT '{}',
                gross_pay NUMERIC(18, 2) NOT NULL,
                net_pay NUMERIC(18, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)

        # ERP业务统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS erp_statistics (
                id SERIAL PRIMARY KEY,
                statistic_type VARCHAR(50) NOT NULL,
                module VARCHAR(50) NOT NULL,
                time_window DATE NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(statistic_type, module, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_journal_entries_date
            ON journal_entries(entry_date DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_purchase_orders_status
            ON purchase_orders(status, order_date DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_orders_status
            ON sales_orders(status, order_date DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_production_orders_status
            ON production_orders(status, start_date DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_employees_department
            ON employees(department, status)
        """)

        self.conn.commit()

    def store_journal_entry(self, entry_id: str, entry_date: date,
                           entry_type: str, description: str,
                           lines: List[Dict], total_debit: Decimal,
                           total_credit: Decimal):
        """存储财务凭证 - 增强错误处理"""
        # 输入验证
        if not entry_id:
            raise ValueError("Entry ID cannot be empty")

        if not isinstance(entry_id, str):
            raise TypeError(f"Entry ID must be a string, got {type(entry_id)}")

        if len(entry_id) > 50:
            raise ValueError(f"Entry ID too long: {len(entry_id)} (max 50)")

        if not isinstance(entry_date, date):
            raise TypeError(f"Entry date must be a date, got {type(entry_date)}")

        if not entry_type:
            raise ValueError("Entry type cannot be empty")

        if not isinstance(entry_type, str):
            raise TypeError(f"Entry type must be a string, got {type(entry_type)}")

        if description is not None and not isinstance(description, str):
            raise TypeError(f"Description must be a string or None, got {type(description)}")

        if not isinstance(lines, list):
            raise TypeError(f"Lines must be a list, got {type(lines)}")

        if not lines:
            raise ValueError("Lines cannot be empty")

        if not isinstance(total_debit, (int, float, Decimal)):
            raise TypeError(f"Total debit must be numeric, got {type(total_debit)}")

        if not isinstance(total_credit, (int, float, Decimal)):
            raise TypeError(f"Total credit must be numeric, got {type(total_credit)}")

        total_debit = Decimal(str(total_debit))
        total_credit = Decimal(str(total_credit))

        if total_debit < 0:
            raise ValueError(f"Total debit cannot be negative: {total_debit}")

        if total_credit < 0:
            raise ValueError(f"Total credit cannot be negative: {total_credit}")

        # 验证借贷平衡
        if total_debit != total_credit:
            raise ValueError(f"Debit and credit must be balanced: debit={total_debit}, credit={total_credit}")

        # 验证凭证行
        line_debit_sum = Decimal('0')
        line_credit_sum = Decimal('0')

        for i, line in enumerate(lines):
            if not isinstance(line, dict):
                raise TypeError(f"Line {i} must be a dictionary, got {type(line)}")

            if 'account_code' not in line:
                raise ValueError(f"Line {i} missing 'account_code'")

            account_code = line['account_code']
            if not isinstance(account_code, str):
                raise TypeError(f"Line {i} account_code must be a string, got {type(account_code)}")

            if len(account_code) > 20:
                raise ValueError(f"Line {i} account_code too long: {len(account_code)} (max 20)")

            debit_amount = Decimal(str(line.get('debit_amount', 0)))
            credit_amount = Decimal(str(line.get('credit_amount', 0)))

            if debit_amount < 0:
                raise ValueError(f"Line {i} debit_amount cannot be negative: {debit_amount}")

            if credit_amount < 0:
                raise ValueError(f"Line {i} credit_amount cannot be negative: {credit_amount}")

            if debit_amount > 0 and credit_amount > 0:
                raise ValueError(f"Line {i} cannot have both debit and credit amounts")

            line_debit_sum += debit_amount
            line_credit_sum += credit_amount

        # 验证凭证行合计与总金额一致
        if line_debit_sum != total_debit:
            raise ValueError(f"Line debit sum ({line_debit_sum}) does not match total debit ({total_debit})")

        if line_credit_sum != total_credit:
            raise ValueError(f"Line credit sum ({line_credit_sum}) does not match total credit ({total_credit})")

        try:
            self.cur.execute("""
                INSERT INTO journal_entries
                (entry_id, entry_date, entry_type, description, total_debit, total_credit)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entry_id, entry_date, entry_type, description, total_debit, total_credit))

            # 存储凭证行
            for line in lines:
                self.cur.execute("""
                    INSERT INTO journal_lines
                    (entry_id, account_code, debit_amount, credit_amount, cost_center)
                    VALUES (%s, %s, %s, %s, %s)
                """, (entry_id, line['account_code'],
                      Decimal(str(line.get('debit_amount', 0))),
                      Decimal(str(line.get('credit_amount', 0))),
                      line.get('cost_center')))

            self.conn.commit()
            logger.info(f"Stored journal entry: {entry_id}")

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing journal entry: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate entry ID or constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing journal entry: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing journal entry: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store journal entry: {e}") from e

    def calculate_financial_statistics(self, start_date: date, end_date: date):
        """计算财务统计信息 - 增强错误处理"""
        # 输入验证
        if not isinstance(start_date, date):
            raise TypeError(f"Start date must be a date, got {type(start_date)}")

        if not isinstance(end_date, date):
            raise TypeError(f"End date must be a date, got {type(end_date)}")

        if start_date > end_date:
            raise ValueError(f"Start date ({start_date}) cannot be after end date ({end_date})")

        try:
            self.cur.execute("""
                SELECT
                    account_type,
                    SUM(debit_amount) as total_debit,
                    SUM(credit_amount) as total_credit,
                    COUNT(*) as transaction_count
                FROM journal_lines jl
                JOIN journal_entries je ON jl.entry_id = je.entry_id
                JOIN chart_of_accounts coa ON jl.account_code = coa.account_code
                WHERE je.entry_date BETWEEN %s AND %s
                GROUP BY account_type
            """, (start_date, end_date))

            stats = {}
            for row in self.cur.fetchall():
                stats[row[0]] = {
                    'total_debit': float(row[1]) if row[1] is not None else 0.0,
                    'total_credit': float(row[2]) if row[2] is not None else 0.0,
                    'transaction_count': row[3] if row[3] is not None else 0
                }

            # 存储统计信息
            self.cur.execute("""
                INSERT INTO erp_statistics
                (statistic_type, module, time_window, statistics)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (statistic_type, module, time_window)
                DO UPDATE SET statistics = EXCLUDED.statistics
            """, ('financial', 'Finance', end_date, json.dumps(stats)))
            self.conn.commit()

            logger.info(f"Calculated financial statistics from {start_date} to {end_date}")
            return stats

        except psycopg2.Error as e:
            logger.error(f"Database error calculating financial statistics: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error calculating financial statistics: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to calculate financial statistics: {e}") from e
```

### 6.2 ERP数据分析查询

**查询示例**：

```python
# 查询财务凭证
storage.cur.execute("""
    SELECT entry_id, entry_date, total_debit, total_credit
    FROM journal_entries
    WHERE entry_date BETWEEN %s AND %s
    ORDER BY entry_date DESC
""", (start_date, end_date))

# 查询采购订单统计
storage.cur.execute("""
    SELECT status, COUNT(*) as order_count, SUM(total_amount) as total_amount
    FROM purchase_orders
    WHERE order_date >= %s
    GROUP BY status
""", (start_date,))

# 查询库存周转率
storage.cur.execute("""
    SELECT
        i.item_code,
        i.item_name,
        i.current_stock,
        COALESCE(SUM(soi.quantity), 0) as sales_quantity,
        CASE
            WHEN i.current_stock > 0
            THEN COALESCE(SUM(soi.quantity), 0) / i.current_stock
            ELSE 0
        END as turnover_rate
    FROM inventory i
    LEFT JOIN sales_order_items soi ON i.item_code = soi.item_code
    LEFT JOIN sales_orders so ON soi.so_number = so.so_number
    WHERE so.order_date >= %s OR so.order_date IS NULL
    GROUP BY i.item_code, i.item_name, i.current_stock
""", (start_date,))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
