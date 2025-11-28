# 合规Schema转换体系

## 📑 目录

- [合规Schema转换体系](#合规schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GDPR到HIPAA转换](#2-gdpr到hipaa转换)
  - [3. HIPAA到PCI-DSS转换](#3-hipaa到pci-dss转换)
  - [4. 合规Schema到安全标准Schema转换](#4-合规schema到安全标准schema转换)
  - [5. 转换验证](#5-转换验证)
  - [6. 合规数据存储与分析](#6-合规数据存储与分析)
    - [6.1 PostgreSQL合规数据存储](#61-postgresql合规数据存储)
    - [6.2 合规数据分析查询](#62-合规数据分析查询)

---

## 1. 转换体系概述

合规Schema转换体系支持不同合规标准之间的转换和映射。

### 1.1 转换目标

1. **GDPR到HIPAA转换**：GDPR要求映射到HIPAA要求
2. **HIPAA到PCI-DSS转换**：HIPAA要求映射到PCI-DSS要求
3. **合规Schema到安全标准Schema转换**：合规要求转换为安全标准要求
4. **Schema到数据库转换**：合规Schema定义到PostgreSQL存储

---

## 2. GDPR到HIPAA转换

**转换规则**：

- GDPR数据保护原则 → HIPAA隐私规则
- GDPR数据主体权利 → HIPAA患者权利
- GDPR数据保护措施 → HIPAA安全措施

**转换示例**：

```python
def gdpr_to_hipaa(gdpr_schema: dict) -> dict:
    """将GDPR Schema转换为HIPAA Schema"""
    hipaa_schema = {
        "phi_protection": map_gdpr_data_protection_to_phi_protection(
            gdpr_schema["data_protection_measures"]
        ),
        "privacy_rule": map_gdpr_principles_to_hipaa_privacy(
            gdpr_schema["data_processing_principles"]
        ),
        "security_rule": map_gdpr_measures_to_hipaa_security(
            gdpr_schema["data_protection_measures"]
        )
    }
    return hipaa_schema
```

---

## 3. HIPAA到PCI-DSS转换

**转换规则**：

- HIPAA安全措施 → PCI-DSS安全要求
- HIPAA访问控制 → PCI-DSS访问控制

---

## 4. 合规Schema到安全标准Schema转换

**转换规则**：

- GDPR要求 → ISO 27001控制措施
- HIPAA要求 → NIST框架功能

---

## 5. 转换验证

验证转换的合规要求完整性、映射准确性和合规性等价性。

---

## 6. 合规数据存储与分析

### 6.1 PostgreSQL合规数据存储

**合规数据存储方案**：

```python
import psycopg2
import json

class ComplianceDataStore:
    """合规数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建合规数据存储表"""
        with self.conn.cursor() as cur:
            # 合规标准定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS compliance_standards (
                    id SERIAL PRIMARY KEY,
                    standard_name VARCHAR(255) NOT NULL UNIQUE,
                    standard_type VARCHAR(50) NOT NULL,
                    standard_version VARCHAR(50),
                    standard_definition JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 合规要求表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS compliance_requirements (
                    id SERIAL PRIMARY KEY,
                    standard_id INTEGER REFERENCES compliance_standards(id),
                    requirement_id VARCHAR(50) NOT NULL,
                    requirement_name VARCHAR(255) NOT NULL,
                    requirement_type VARCHAR(50),
                    implementation_status VARCHAR(50),
                    requirement_definition JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(standard_id, requirement_id)
                )
            """)

            # 合规评估表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    id SERIAL PRIMARY KEY,
                    standard_id INTEGER REFERENCES compliance_standards(id),
                    assessment_date TIMESTAMP NOT NULL,
                    compliance_status VARCHAR(50) NOT NULL,
                    assessment_results JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
```

### 6.2 合规数据分析查询

**分析查询示例**：

```python
def analyze_compliance(db_config: Dict):
    """分析合规状态"""
    store = ComplianceDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询合规状态统计
        cur.execute("""
            SELECT
                cs.standard_name,
                COUNT(cr.id) as requirement_count,
                SUM(CASE WHEN cr.implementation_status = 'Implemented' THEN 1 ELSE 0 END) as implemented_count,
                COUNT(DISTINCT ca.id) as assessment_count
            FROM compliance_standards cs
            LEFT JOIN compliance_requirements cr ON cs.id = cr.standard_id
            LEFT JOIN compliance_assessments ca ON cs.id = ca.standard_id
            GROUP BY cs.id, cs.standard_name
            ORDER BY assessment_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
