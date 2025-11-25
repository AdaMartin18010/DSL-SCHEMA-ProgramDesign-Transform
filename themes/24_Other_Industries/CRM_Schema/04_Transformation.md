# 客户关系管理Schema转换体系

## 📑 目录

- [客户关系管理Schema转换体系](#客户关系管理schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Salesforce到Microsoft Dynamics转换](#2-salesforce到microsoft-dynamics转换)
  - [3. PostgreSQL CRM数据存储](#3-postgresql-crm数据存储)

---

## 1. 转换体系概述

CRM Schema转换体系支持Salesforce API、Microsoft Dynamics、数据库存储之间的转换。

### 1.1 转换目标

1. **Salesforce到Microsoft Dynamics转换**：Salesforce账户数据到Dynamics格式
2. **数据到数据库转换**：CRM数据到PostgreSQL存储

---

## 2. Salesforce到Microsoft Dynamics转换

**完整的Salesforce到Dynamics转换实现**：

```python
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SalesforceToDynamicsConverter:
    """Salesforce到Microsoft Dynamics转换器"""

    def convert_account(self, sf_account: Dict) -> Dict:
        """将Salesforce账户转换为Dynamics格式"""
        dynamics_account = {
            "name": sf_account.get("Name", ""),
            "accountnumber": sf_account.get("AccountNumber", ""),
            "industrycode": self._convert_industry(sf_account.get("Industry", "")),
            "revenue": sf_account.get("AnnualRevenue", 0),
            "telephone1": sf_account.get("Phone", ""),
            "websiteurl": sf_account.get("Website", "")
        }
        return dynamics_account

    def _convert_industry(self, industry: str) -> int:
        """转换行业代码"""
        industry_map = {
            "Technology": 1,
            "Manufacturing": 2,
            "Financial Services": 3
        }
        return industry_map.get(industry, 0)
```

---

## 3. PostgreSQL CRM数据存储

**完整的PostgreSQL存储实现**：

```python
import psycopg2
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CRMStorage:
    """CRM数据PostgreSQL存储"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 账户表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id VARCHAR(50) PRIMARY KEY,
                account_name VARCHAR(200) NOT NULL,
                account_type VARCHAR(50),
                industry VARCHAR(100),
                annual_revenue DECIMAL(15, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 联系人表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                contact_id VARCHAR(50) PRIMARY KEY,
                account_id VARCHAR(50) REFERENCES accounts(account_id),
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 商机表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                opportunity_id VARCHAR(50) PRIMARY KEY,
                account_id VARCHAR(50) REFERENCES accounts(account_id),
                opportunity_name VARCHAR(200) NOT NULL,
                stage VARCHAR(50) NOT NULL,
                amount DECIMAL(15, 2),
                close_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def store_account(self, account_id: str, account_name: str,
                     account_type: str = None, industry: str = None,
                     annual_revenue: float = None) -> Optional[str]:
        """存储账户"""
        if not account_id or not account_name:
            raise ValueError("Account ID and account name are required")

        try:
            self.cur.execute("""
                INSERT INTO accounts (
                    account_id, account_name, account_type, industry, annual_revenue
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (account_id) DO UPDATE SET
                    account_name = EXCLUDED.account_name,
                    account_type = EXCLUDED.account_type,
                    industry = EXCLUDED.industry,
                    annual_revenue = EXCLUDED.annual_revenue
                RETURNING account_id
            """, (account_id, account_name, account_type, industry, annual_revenue))
            result = self.cur.fetchone()
            self.conn.commit()
            logger.info(f"Stored account: {account_id}")
            return result[0] if result else None
        except psycopg2.Error as e:
            logger.error(f"Database error storing account: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
