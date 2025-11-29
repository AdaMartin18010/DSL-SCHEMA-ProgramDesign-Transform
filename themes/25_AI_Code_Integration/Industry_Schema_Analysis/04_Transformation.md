# 行业标准映射

## 📑 目录

- [行业标准映射](#行业标准映射)
  - [📑 目录](#-目录)
  - [1. 标准映射矩阵](#1-标准映射矩阵)
  - [2. 映射规则](#2-映射规则)
    - [2.1 字段映射规则](#21-字段映射规则)
    - [2.2 类型转换规则](#22-类型转换规则)
  - [3. 映射工具](#3-映射工具)
    - [3.1 自动映射工具](#31-自动映射工具)
  - [6. 数据库存储与分析](#6-数据库存储与分析)
    - [6.1 PostgreSQL数据存储](#61-postgresql数据存储)
    - [6.2 数据分析查询示例](#62-数据分析查询示例)

---

## 1. 标准映射矩阵

| 源标准 | 目标标准 | 映射复杂度 | 支持状态 |
|--------|---------|-----------|---------|
| **EDI** | **GS1** | 中 | ✅ 支持 |
| **HL7** | **FHIR** | 低 | ✅ 支持 |
| **ISO20022** | **SWIFT** | 中 | ✅ 支持 |
| **OpenAPI** | **AsyncAPI** | 中 | ✅ 支持 |
| **MQTT** | **OpenAPI** | 高 | ✅ 支持 |

---

## 2. 映射规则

### 2.1 字段映射规则

- **直接映射**：字段名称和类型相同
- **转换映射**：字段名称不同但语义相同
- **组合映射**：多个字段组合为一个字段

### 2.2 类型转换规则

- **字符串转换**：编码转换、格式转换
- **数值转换**：单位转换、精度转换
- **日期转换**：格式转换、时区转换

---

## 3. 映射工具

### 3.1 自动映射工具

- **规则引擎**：基于规则的自动映射
- **机器学习**：基于机器学习的映射
- **模板匹配**：基于模板的映射

---

## 6. 数据库存储与分析

### 6.1 PostgreSQL数据存储

**表结构设计**：

```sql
-- 行业标准映射表
CREATE TABLE industry_schema_mappings (
    id SERIAL PRIMARY KEY,
    source_standard VARCHAR(100) NOT NULL,
    target_standard VARCHAR(100) NOT NULL,
    mapping_complexity VARCHAR(20),  -- Low, Medium, High
    support_status VARCHAR(20) DEFAULT 'SUPPORTED',
    mapping_rules JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_standard, target_standard)
);

-- 字段映射规则表
CREATE TABLE field_mapping_rules (
    id SERIAL PRIMARY KEY,
    mapping_id INTEGER REFERENCES industry_schema_mappings(id),
    source_field VARCHAR(200) NOT NULL,
    target_field VARCHAR(200) NOT NULL,
    mapping_type VARCHAR(50),  -- Direct, Transform, Combine
    transformation_rule JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_mappings_source_target ON industry_schema_mappings(source_standard, target_standard);
CREATE INDEX idx_field_mappings_mapping_id ON field_mapping_rules(mapping_id);
```

**Python存储实现**：

```python
import psycopg2
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class IndustrySchemaMappingStorage:
    """行业Schema映射数据存储类"""

    def __init__(self, db_config: Dict[str, Any]):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建表结构"""
        # 行业标准映射表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS industry_schema_mappings (
                id SERIAL PRIMARY KEY,
                source_standard VARCHAR(100) NOT NULL,
                target_standard VARCHAR(100) NOT NULL,
                mapping_complexity VARCHAR(20),
                support_status VARCHAR(20) DEFAULT 'SUPPORTED',
                mapping_rules JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_standard, target_standard)
            )
        """)

        # 字段映射规则表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS field_mapping_rules (
                id SERIAL PRIMARY KEY,
                mapping_id INTEGER REFERENCES industry_schema_mappings(id),
                source_field VARCHAR(200) NOT NULL,
                target_field VARCHAR(200) NOT NULL,
                mapping_type VARCHAR(50),
                transformation_rule JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mappings_source_target
            ON industry_schema_mappings(source_standard, target_standard)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_field_mappings_mapping_id
            ON field_mapping_rules(mapping_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mappings_status
            ON industry_schema_mappings(support_status)
        """)

        self.conn.commit()

    def store_mapping(self, source_standard: str, target_standard: str,
                     mapping_complexity: str, mapping_rules: Dict,
                     support_status: str = 'SUPPORTED') -> int:
        """存储行业标准映射"""
        try:
            self.cur.execute("""
                INSERT INTO industry_schema_mappings
                (source_standard, target_standard, mapping_complexity,
                 support_status, mapping_rules)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (source_standard, target_standard) DO UPDATE
                SET mapping_complexity = EXCLUDED.mapping_complexity,
                    support_status = EXCLUDED.support_status,
                    mapping_rules = EXCLUDED.mapping_rules,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (source_standard, target_standard, mapping_complexity,
                  support_status, json.dumps(mapping_rules)))
            mapping_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored mapping: {source_standard} -> {target_standard} (ID: {mapping_id})")
            return mapping_id
        except Exception as e:
            logger.error(f"Failed to store mapping: {e}")
            self.conn.rollback()
            raise

    def store_field_mapping_rule(self, mapping_id: int, source_field: str,
                                 target_field: str, mapping_type: str,
                                 transformation_rule: Optional[Dict] = None) -> int:
        """存储字段映射规则"""
        try:
            self.cur.execute("""
                INSERT INTO field_mapping_rules
                (mapping_id, source_field, target_field, mapping_type, transformation_rule)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                RETURNING id
            """, (mapping_id, source_field, target_field, mapping_type,
                  json.dumps(transformation_rule) if transformation_rule else None))
            rule_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored field mapping rule: {rule_id}")
            return rule_id
        except Exception as e:
            logger.error(f"Failed to store field mapping rule: {e}")
            self.conn.rollback()
            raise

    def get_mapping_statistics(self) -> Dict:
        """获取映射统计信息"""
        try:
            self.cur.execute("""
                SELECT
                    source_standard,
                    COUNT(*) as mapping_count,
                    COUNT(CASE WHEN support_status = 'SUPPORTED' THEN 1 END) as supported_count
                FROM industry_schema_mappings
                GROUP BY source_standard
                ORDER BY mapping_count DESC
            """)
            results = []
            for row in self.cur.fetchall():
                results.append({
                    'source_standard': row[0],
                    'mapping_count': row[1],
                    'supported_count': row[2]
                })
            return {'by_source': results}
        except Exception as e:
            logger.error(f"Failed to get mapping statistics: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 数据分析查询示例

**查询映射统计**：

```python
# 查询各标准间的映射数量
storage.cur.execute("""
    SELECT source_standard, target_standard, mapping_complexity
    FROM industry_schema_mappings
    WHERE support_status = 'SUPPORTED'
    ORDER BY source_standard, target_standard
""")
```

**查询映射复杂度分布**：

```python
# 查询映射复杂度分布
storage.cur.execute("""
    SELECT
        mapping_complexity,
        COUNT(*) as count,
        COUNT(CASE WHEN support_status = 'SUPPORTED' THEN 1 END) as supported_count
    FROM industry_schema_mappings
    GROUP BY mapping_complexity
    ORDER BY count DESC
""")
```

**查询字段映射规则统计**：

```python
# 查询字段映射规则统计
storage.cur.execute("""
    SELECT
        ism.source_standard,
        ism.target_standard,
        COUNT(fmr.id) as field_rule_count,
        COUNT(CASE WHEN fmr.mapping_type = 'Direct' THEN 1 END) as direct_mappings,
        COUNT(CASE WHEN fmr.mapping_type = 'Transform' THEN 1 END) as transform_mappings
    FROM industry_schema_mappings ism
    LEFT JOIN field_mapping_rules fmr ON ism.id = fmr.mapping_id
    GROUP BY ism.id, ism.source_standard, ism.target_standard
    ORDER BY field_rule_count DESC
""")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 行业Schema对比
- `03_Standards.md` - 跨行业转换
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
