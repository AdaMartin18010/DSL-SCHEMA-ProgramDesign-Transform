# Schema转换应用

## 📑 目录

- [Schema转换应用](#schema转换应用)
  - [📑 目录](#-目录)
  - [1. 类型系统在转换中的作用](#1-类型系统在转换中的作用)
    - [1.1 类型映射](#11-类型映射)
    - [1.2 类型转换](#12-类型转换)
  - [2. 控制逻辑在转换中的应用](#2-控制逻辑在转换中的应用)
    - [2.1 条件转换](#21-条件转换)
    - [2.2 循环转换](#22-循环转换)
  - [3. 类型安全转换实现](#3-类型安全转换实现)
    - [3.1 类型检查](#31-类型检查)
    - [3.2 类型转换](#32-类型转换)
  - [6. 数据库存储与分析](#6-数据库存储与分析)
    - [6.1 PostgreSQL数据存储](#61-postgresql数据存储)
    - [6.2 数据分析查询示例](#62-数据分析查询示例)

---

## 1. 类型系统在转换中的作用

### 1.1 类型映射

**源类型到目标类型的映射**：

- 字符串类型映射
- 数值类型映射
- 日期类型映射

### 1.2 类型转换

**类型间的转换规则**：

- 字符串到数值转换
- 日期格式转换
- 枚举值转换

---

## 2. 控制逻辑在转换中的应用

### 2.1 条件转换

**根据条件选择转换规则**：

- 根据数据类型选择转换规则
- 根据数据值选择转换规则

### 2.2 循环转换

**批量转换处理**：

- 列表数据转换
- 数组数据转换

---

## 3. 类型安全转换实现

### 3.1 类型检查

**转换前类型检查**：

- 验证源数据类型
- 验证目标类型兼容性

### 3.2 类型转换

**安全的类型转换**：

- 显式类型转换
- 类型转换验证

---

## 6. 数据库存储与分析

### 6.1 PostgreSQL数据存储

**表结构设计**：

```sql
-- 类型系统转换表
CREATE TABLE type_system_conversions (
    id SERIAL PRIMARY KEY,
    source_language VARCHAR(50) NOT NULL,
    target_language VARCHAR(50) NOT NULL,
    source_type VARCHAR(200) NOT NULL,
    target_type VARCHAR(200) NOT NULL,
    conversion_rule JSONB NOT NULL,
    type_safety_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_language, target_language, source_type, target_type)
);

-- 类型转换记录表
CREATE TABLE type_conversion_records (
    id SERIAL PRIMARY KEY,
    conversion_id INTEGER REFERENCES type_system_conversions(id),
    source_value JSONB,
    target_value JSONB,
    conversion_status VARCHAR(20) DEFAULT 'PENDING',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_type_conversions_source_target ON type_system_conversions(source_language, target_language);
CREATE INDEX idx_type_conversions_safety ON type_system_conversions(type_safety_verified);
CREATE INDEX idx_type_records_conversion_id ON type_conversion_records(conversion_id);
```

**Python存储实现**：

```python
import psycopg2
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TypeSystemConversionStorage:
    """类型系统转换数据存储类"""

    def __init__(self, db_config: Dict[str, Any]):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建表结构"""
        # 类型系统转换表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS type_system_conversions (
                id SERIAL PRIMARY KEY,
                source_language VARCHAR(50) NOT NULL,
                target_language VARCHAR(50) NOT NULL,
                source_type VARCHAR(200) NOT NULL,
                target_type VARCHAR(200) NOT NULL,
                conversion_rule JSONB NOT NULL,
                type_safety_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_language, target_language, source_type, target_type)
            )
        """)

        # 类型转换记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS type_conversion_records (
                id SERIAL PRIMARY KEY,
                conversion_id INTEGER REFERENCES type_system_conversions(id),
                source_value JSONB,
                target_value JSONB,
                conversion_status VARCHAR(20) DEFAULT 'PENDING',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_type_conversions_source_target
            ON type_system_conversions(source_language, target_language)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_type_conversions_safety
            ON type_system_conversions(type_safety_verified)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_type_records_conversion_id
            ON type_conversion_records(conversion_id)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_type_records_status
            ON type_conversion_records(conversion_status, created_at DESC)
        """)

        self.conn.commit()

    def store_type_conversion(self, source_language: str, target_language: str,
                             source_type: str, target_type: str,
                             conversion_rule: Dict, type_safety_verified: bool = False) -> int:
        """存储类型系统转换"""
        try:
            self.cur.execute("""
                INSERT INTO type_system_conversions
                (source_language, target_language, source_type, target_type,
                 conversion_rule, type_safety_verified)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                ON CONFLICT (source_language, target_language, source_type, target_type) DO UPDATE
                SET conversion_rule = EXCLUDED.conversion_rule,
                    type_safety_verified = EXCLUDED.type_safety_verified,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (source_language, target_language, source_type, target_type,
                  json.dumps(conversion_rule), type_safety_verified))
            conversion_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored type conversion: {source_language}.{source_type} -> {target_language}.{target_type} (ID: {conversion_id})")
            return conversion_id
        except Exception as e:
            logger.error(f"Failed to store type conversion: {e}")
            self.conn.rollback()
            raise

    def store_type_conversion_record(self, conversion_id: int, source_value: Dict,
                                    target_value: Optional[Dict] = None,
                                    conversion_status: str = 'PENDING',
                                    error_message: Optional[str] = None) -> int:
        """存储类型转换记录"""
        try:
            self.cur.execute("""
                INSERT INTO type_conversion_records
                (conversion_id, source_value, target_value, conversion_status, error_message)
                VALUES (%s, %s::jsonb, %s::jsonb, %s, %s)
                RETURNING id
            """, (conversion_id, json.dumps(source_value),
                  json.dumps(target_value) if target_value else None,
                  conversion_status, error_message))
            record_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"Stored type conversion record: {record_id}")
            return record_id
        except Exception as e:
            logger.error(f"Failed to store type conversion record: {e}")
            self.conn.rollback()
            raise

    def get_type_safety_statistics(self) -> Dict:
        """获取类型安全统计信息"""
        try:
            self.cur.execute("""
                SELECT
                    source_language,
                    target_language,
                    COUNT(*) as total_conversions,
                    COUNT(CASE WHEN type_safety_verified THEN 1 END) as verified_count,
                    ROUND(100.0 * COUNT(CASE WHEN type_safety_verified THEN 1 END) / COUNT(*), 2) as verification_rate
                FROM type_system_conversions
                GROUP BY source_language, target_language
                ORDER BY verification_rate DESC
            """)
            results = []
            for row in self.cur.fetchall():
                results.append({
                    'source_language': row[0],
                    'target_language': row[1],
                    'total_conversions': row[2],
                    'verified_count': row[3],
                    'verification_rate': float(row[4]) if row[4] else 0.0
                })
            return {'by_language_pair': results}
        except Exception as e:
            logger.error(f"Failed to get type safety statistics: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 6.2 数据分析查询示例

**查询类型安全验证统计**：

```python
# 查询类型安全验证状态
storage.cur.execute("""
    SELECT source_language, target_language,
           COUNT(*) as total,
           COUNT(CASE WHEN type_safety_verified THEN 1 END) as verified
    FROM type_system_conversions
    GROUP BY source_language, target_language
    ORDER BY verified DESC
""")
```

**查询类型转换成功率**：

```python
# 查询类型转换成功率
storage.cur.execute("""
    SELECT
        tsc.source_language,
        tsc.target_language,
        tsc.source_type,
        tsc.target_type,
        COUNT(tcr.id) as conversion_count,
        COUNT(CASE WHEN tcr.conversion_status = 'COMPLETED' THEN 1 END) as completed_count,
        ROUND(100.0 * COUNT(CASE WHEN tcr.conversion_status = 'COMPLETED' THEN 1 END) / NULLIF(COUNT(tcr.id), 0), 2) as success_rate
    FROM type_system_conversions tsc
    LEFT JOIN type_conversion_records tcr ON tsc.id = tcr.conversion_id
    GROUP BY tsc.id, tsc.source_language, tsc.target_language, tsc.source_type, tsc.target_type
    HAVING COUNT(tcr.id) > 0
    ORDER BY success_rate DESC
""")
```

**查询类型转换错误分析**：

```python
# 查询类型转换错误分析
storage.cur.execute("""
    SELECT
        tsc.source_language,
        tsc.target_language,
        tcr.error_message,
        COUNT(*) as error_count
    FROM type_system_conversions tsc
    JOIN type_conversion_records tcr ON tsc.id = tcr.conversion_id
    WHERE tcr.conversion_status = 'FAILED' AND tcr.error_message IS NOT NULL
    GROUP BY tsc.source_language, tsc.target_language, tcr.error_message
    ORDER BY error_count DESC
    LIMIT 20
""")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 类型系统分析
- `03_Standards.md` - 控制逻辑分析
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
