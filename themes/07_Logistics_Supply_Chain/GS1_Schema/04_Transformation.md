# GS1 Schema转换体系

## 📑 目录

- [GS1 Schema转换体系](#gs1-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GTIN转换](#2-gtin转换)
  - [3. GLN转换](#3-gln转换)
  - [4. SSCC转换](#4-sscc转换)
  - [5. EPCIS转换](#5-epcis转换)
  - [6. GS1数据存储与分析](#6-gs1数据存储与分析)
    - [6.1 PostgreSQL GS1数据存储](#61-postgresql-gs1数据存储)
    - [6.2 GS1数据分析查询](#62-gs1数据分析查询)

---

## 1. 转换体系概述

GS1 Schema转换体系支持GTIN、GLN、SSCC、
EPCIS之间的转换，以及GS1数据到数据库存储的转换。

### 1.1 转换目标

1. **GTIN格式转换**：不同GTIN格式之间的转换
2. **EPC转换**：GTIN到EPC的转换
3. **EPCIS事件转换**：EPCIS事件到数据库记录的转换
4. **GS1数据到数据库转换**：GS1标识符和事件到PostgreSQL存储

---

## 2. GTIN转换

**转换规则**：

- GTIN-8 ↔ GTIN-12 ↔ GTIN-13 ↔ GTIN-14
- GTIN → EPC（EPC编码）

**转换示例**：

```python
def convert_gtin13_to_gtin14(gtin13: str, indicator: str = "0") -> str:
    """将GTIN-13转换为GTIN-14"""
    # GTIN-14 = 指示符 + GTIN-13（不含校验位）+ 新校验位
    gtin14_base = indicator + gtin13[:-1]
    check_digit = calculate_check_digit(gtin14_base)
    return gtin14_base + check_digit

def convert_gtin_to_epc(gtin: str, serial: str) -> str:
    """将GTIN转换为EPC"""
    # EPC格式：urn:epc:id:sgtin:CompanyPrefix.ItemRef.SerialNumber
    if len(gtin) == 13:
        # GTIN-13: 前7-9位是公司前缀，剩余是项目参考
        company_prefix = gtin[:7]  # 假设7位公司前缀
        item_ref = gtin[7:12]
    elif len(gtin) == 14:
        # GTIN-14: 第1位是指示符，第2-8位是公司前缀，剩余是项目参考
        company_prefix = gtin[1:8]
        item_ref = gtin[8:13]
    else:
        raise ValueError(f"Unsupported GTIN length: {len(gtin)}")

    epc = f"urn:epc:id:sgtin:{company_prefix}.{item_ref}.{serial}"
    return epc
```

---

## 3. GLN转换

**转换规则**：

- GLN ↔ 位置信息
- GLN → 地理坐标

**转换示例**：

```python
def convert_gln_to_location(gln: str) -> dict:
    """将GLN转换为位置信息"""
    # 从数据库查询GLN对应的位置信息
    location = query_gln_location(gln)
    return {
        "gln": gln,
        "location_name": location.name,
        "address": location.address,
        "coordinates": location.coordinates
    }

def convert_location_to_gln(location_info: dict) -> str:
    """将位置信息转换为GLN"""
    # 检查是否已存在GLN
    existing_gln = query_gln_by_location(location_info)
    if existing_gln:
        return existing_gln

    # 生成新GLN
    gln = generate_gln()
    store_gln_location(gln, location_info)
    return gln
```

---

## 4. SSCC转换

**转换规则**：

- SSCC ↔ 包装信息
- SSCC层级关系转换

**转换示例**：

```python
def convert_sscc_to_packaging(sscc: str) -> dict:
    """将SSCC转换为包装信息"""
    packaging = {
        "sscc": sscc,
        "extension_digit": sscc[0],
        "company_prefix": sscc[1:9],
        "serial_reference": sscc[9:17],
        "check_digit": sscc[17]
    }
    return packaging

def convert_packaging_to_sscc(packaging_info: dict) -> str:
    """将包装信息转换为SSCC"""
    extension_digit = packaging_info.get("extension_digit", "0")
    company_prefix = packaging_info["company_prefix"]
    serial_reference = packaging_info["serial_reference"]

    sscc_base = extension_digit + company_prefix + serial_reference
    check_digit = calculate_check_digit(sscc_base)
    return sscc_base + check_digit
```

---

## 5. EPCIS转换

**转换规则**：

- EPCIS事件 ↔ 数据库记录
- EPCIS事件类型转换

**转换示例**：

```python
def convert_epcis_to_database(epcis_event: dict) -> dict:
    """将EPCIS事件转换为数据库记录"""
    db_record = {
        "event_id": generate_uuid(),
        "event_time": epcis_event["eventTime"],
        "event_timezone": epcis_event.get("eventTimeZoneOffset"),
        "event_type": determine_event_type(epcis_event),
        "action": epcis_event.get("action"),
        "biz_step": epcis_event.get("bizStep"),
        "disposition": epcis_event.get("disposition"),
        "read_point": epcis_event.get("readPoint", {}).get("id"),
        "biz_location": epcis_event.get("bizLocation", {}).get("id"),
        "epc_list": epcis_event.get("epcList", []),
        "quantity_list": epcis_event.get("quantityList", []),
        "biz_transaction_list": epcis_event.get("bizTransactionList", []),
        "source_list": epcis_event.get("sourceList", []),
        "destination_list": epcis_event.get("destinationList", []),
        "created_at": datetime.now()
    }
    return db_record

def determine_event_type(event: dict) -> str:
    """确定EPCIS事件类型"""
    if "epcList" in event and "parentID" not in event:
        return "ObjectEvent"
    elif "parentID" in event:
        return "AggregationEvent"
    elif "transformationID" in event:
        return "TransformationEvent"
    elif "bizTransactionList" in event and len(event.get("bizTransactionList", [])) > 0:
        return "TransactionEvent"
    else:
        return "Unknown"
```

---

## 6. GS1数据存储与分析

### 6.1 PostgreSQL GS1数据存储

**数据库设计**：

```python
import psycopg2
from datetime import datetime
from typing import List, Optional, Dict
import uuid

class GS1Storage:
    """GS1数据PostgreSQL存储类"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.create_tables()

    def create_tables(self):
        """创建GS1数据存储表"""
        cursor = self.conn.cursor()

        # GTIN表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gtin_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                gtin_type VARCHAR(10) NOT NULL,
                gtin_identifier VARCHAR(20) NOT NULL UNIQUE,
                company_prefix VARCHAR(20),
                item_reference VARCHAR(20),
                check_digit VARCHAR(1),
                product_name VARCHAR(255),
                brand_name VARCHAR(100),
                product_category VARCHAR(100),
                unit_of_measure VARCHAR(20),
                net_weight DECIMAL(10, 3),
                gross_weight DECIMAL(10, 3),
                dimensions_length DECIMAL(10, 2),
                dimensions_width DECIMAL(10, 2),
                dimensions_height DECIMAL(10, 2),
                dimensions_unit VARCHAR(10) DEFAULT 'CM',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # GLN表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gln_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                location_identifier VARCHAR(13) NOT NULL UNIQUE,
                location_type VARCHAR(20) NOT NULL,
                location_name VARCHAR(255) NOT NULL,
                street_address VARCHAR(255),
                city VARCHAR(100),
                state_province VARCHAR(100),
                postal_code VARCHAR(20),
                country VARCHAR(2),
                phone VARCHAR(50),
                email VARCHAR(255),
                website VARCHAR(255),
                latitude DECIMAL(10, 7),
                longitude DECIMAL(10, 7),
                parent_gln VARCHAR(13),
                gln_status VARCHAR(20) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # SSCC表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sscc_data (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                sscc_identifier VARCHAR(18) NOT NULL UNIQUE,
                extension_digit VARCHAR(1),
                company_prefix VARCHAR(20),
                serial_reference VARCHAR(20),
                check_digit VARCHAR(1),
                packaging_type VARCHAR(20),
                packaging_level INTEGER DEFAULT 0,
                parent_sscc VARCHAR(18),
                quantity INTEGER,
                shipper_gln VARCHAR(13),
                receiver_gln VARCHAR(13),
                ship_date DATE,
                expected_delivery_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EPCIS事件表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS epcis_events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                event_id VARCHAR(255) UNIQUE,
                event_time TIMESTAMP NOT NULL,
                event_timezone VARCHAR(10),
                event_type VARCHAR(50) NOT NULL,
                action VARCHAR(20),
                biz_step VARCHAR(100),
                disposition VARCHAR(100),
                read_point VARCHAR(255),
                biz_location VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EPC列表表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS epcis_epc_list (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                event_id UUID NOT NULL REFERENCES epcis_events(id) ON DELETE CASCADE,
                epc VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 业务交易列表表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS epcis_biz_transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                event_id UUID NOT NULL REFERENCES epcis_events(id) ON DELETE CASCADE,
                transaction_type VARCHAR(50) NOT NULL,
                transaction_value VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # GS1统计信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gs1_statistics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                statistic_type VARCHAR(50) NOT NULL,
                identifier_type VARCHAR(20),
                identifier_value VARCHAR(255),
                statistic_date DATE NOT NULL,
                count_value BIGINT DEFAULT 0,
                additional_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gtin_identifier ON gtin_data(gtin_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gln_identifier ON gln_data(location_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sscc_identifier ON sscc_data(sscc_identifier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_epcis_event_time ON epcis_events(event_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_epcis_event_type ON epcis_events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_epcis_read_point ON epcis_events(read_point)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_epcis_biz_location ON epcis_events(biz_location)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_epcis_epc ON epcis_epc_list(epc)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gs1_statistics_date ON gs1_statistics(statistic_date)")

        self.conn.commit()
        cursor.close()

    def store_gtin(self, gtin_data: dict) -> str:
        """存储GTIN数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO gtin_data (
                gtin_type, gtin_identifier, company_prefix, item_reference,
                check_digit, product_name, brand_name, product_category,
                unit_of_measure, net_weight, gross_weight,
                dimensions_length, dimensions_width, dimensions_height, dimensions_unit
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (gtin_identifier) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                brand_name = EXCLUDED.brand_name,
                product_category = EXCLUDED.product_category,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            gtin_data.get("gtin_type"),
            gtin_data.get("gtin_identifier"),
            gtin_data.get("company_prefix"),
            gtin_data.get("item_reference"),
            gtin_data.get("check_digit"),
            gtin_data.get("product_name"),
            gtin_data.get("brand_name"),
            gtin_data.get("product_category"),
            gtin_data.get("unit_of_measure"),
            gtin_data.get("net_weight"),
            gtin_data.get("gross_weight"),
            gtin_data.get("dimensions_length"),
            gtin_data.get("dimensions_width"),
            gtin_data.get("dimensions_height"),
            gtin_data.get("dimensions_unit", "CM")
        ))
        gtin_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return str(gtin_id)

    def store_gln(self, gln_data: dict) -> str:
        """存储GLN数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO gln_data (
                location_identifier, location_type, location_name,
                street_address, city, state_province, postal_code, country,
                phone, email, website, latitude, longitude, parent_gln, gln_status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (location_identifier) DO UPDATE SET
                location_name = EXCLUDED.location_name,
                street_address = EXCLUDED.street_address,
                city = EXCLUDED.city,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            gln_data.get("location_identifier"),
            gln_data.get("location_type"),
            gln_data.get("location_name"),
            gln_data.get("street_address"),
            gln_data.get("city"),
            gln_data.get("state_province"),
            gln_data.get("postal_code"),
            gln_data.get("country"),
            gln_data.get("phone"),
            gln_data.get("email"),
            gln_data.get("website"),
            gln_data.get("latitude"),
            gln_data.get("longitude"),
            gln_data.get("parent_gln"),
            gln_data.get("gln_status", "Active")
        ))
        gln_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return str(gln_id)

    def store_sscc(self, sscc_data: dict) -> str:
        """存储SSCC数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sscc_data (
                sscc_identifier, extension_digit, company_prefix, serial_reference,
                check_digit, packaging_type, packaging_level, parent_sscc,
                quantity, shipper_gln, receiver_gln, ship_date, expected_delivery_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (sscc_identifier) DO UPDATE SET
                packaging_type = EXCLUDED.packaging_type,
                packaging_level = EXCLUDED.packaging_level,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            sscc_data.get("sscc_identifier"),
            sscc_data.get("extension_digit"),
            sscc_data.get("company_prefix"),
            sscc_data.get("serial_reference"),
            sscc_data.get("check_digit"),
            sscc_data.get("packaging_type"),
            sscc_data.get("packaging_level", 0),
            sscc_data.get("parent_sscc"),
            sscc_data.get("quantity"),
            sscc_data.get("shipper_gln"),
            sscc_data.get("receiver_gln"),
            sscc_data.get("ship_date"),
            sscc_data.get("expected_delivery_date")
        ))
        sscc_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return str(sscc_id)

    def store_epcis_event(self, epcis_event: dict) -> str:
        """存储EPCIS事件"""
        cursor = self.conn.cursor()

        # 插入EPCIS事件主记录
        cursor.execute("""
            INSERT INTO epcis_events (
                event_id, event_time, event_timezone, event_type,
                action, biz_step, disposition, read_point, biz_location
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (event_id) DO NOTHING
            RETURNING id
        """, (
            epcis_event.get("event_id"),
            epcis_event.get("event_time"),
            epcis_event.get("event_timezone"),
            epcis_event.get("event_type"),
            epcis_event.get("action"),
            epcis_event.get("biz_step"),
            epcis_event.get("disposition"),
            epcis_event.get("read_point"),
            epcis_event.get("biz_location")
        ))

        result = cursor.fetchone()
        if result:
            event_db_id = result[0]

            # 插入EPC列表
            for epc in epcis_event.get("epc_list", []):
                cursor.execute("""
                    INSERT INTO epcis_epc_list (event_id, epc)
                    VALUES (%s, %s)
                """, (event_db_id, epc))

            # 插入业务交易列表
            for biz_transaction in epcis_event.get("biz_transaction_list", []):
                cursor.execute("""
                    INSERT INTO epcis_biz_transactions (event_id, transaction_type, transaction_value)
                    VALUES (%s, %s, %s)
                """, (event_db_id, biz_transaction.get("type"), biz_transaction.get("value")))

            self.conn.commit()
            cursor.close()
            return str(event_db_id)
        else:
            cursor.close()
            return None

    def query_gtin_by_identifier(self, gtin_identifier: str) -> Optional[dict]:
        """根据GTIN标识符查询GTIN数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM gtin_data WHERE gtin_identifier = %s
        """, (gtin_identifier,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def query_epcis_events_by_epc(self, epc: str, start_time: Optional[datetime] = None,
                                   end_time: Optional[datetime] = None) -> List[dict]:
        """根据EPC查询EPCIS事件"""
        cursor = self.conn.cursor()
        query = """
            SELECT e.* FROM epcis_events e
            INNER JOIN epcis_epc_list el ON e.id = el.event_id
            WHERE el.epc = %s
        """
        params = [epc]

        if start_time:
            query += " AND e.event_time >= %s"
            params.append(start_time)
        if end_time:
            query += " AND e.event_time <= %s"
            params.append(end_time)

        query += " ORDER BY e.event_time DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
```

---

### 6.2 GS1数据分析查询

**查询示例**：

```python
# 查询GTIN使用统计
def query_gtin_statistics(storage: GS1Storage, start_date: datetime, end_date: datetime):
    """查询GTIN使用统计"""
    cursor = storage.conn.cursor()
    cursor.execute("""
        SELECT
            g.gtin_type,
            COUNT(DISTINCT g.gtin_identifier) as gtin_count,
            COUNT(DISTINCT e.id) as event_count
        FROM gtin_data g
        LEFT JOIN epcis_epc_list el ON el.epc LIKE '%' || g.gtin_identifier || '%'
        LEFT JOIN epcis_events e ON e.id = el.event_id
        WHERE e.event_time BETWEEN %s AND %s
        GROUP BY g.gtin_type
        ORDER BY gtin_count DESC
    """, (start_date, end_date))
    return cursor.fetchall()

# 查询供应链追溯路径
def query_supply_chain_trace(storage: GS1Storage, epc: str):
    """查询供应链追溯路径"""
    cursor = storage.conn.cursor()
    cursor.execute("""
        WITH RECURSIVE trace_path AS (
            SELECT e.id, e.event_time, e.biz_location, e.read_point, e.action, e.biz_step, 1 as level
            FROM epcis_events e
            INNER JOIN epcis_epc_list el ON e.id = el.event_id
            WHERE el.epc = %s
            ORDER BY e.event_time ASC
            LIMIT 1

            UNION ALL

            SELECT e.id, e.event_time, e.biz_location, e.read_point, e.action, e.biz_step, tp.level + 1
            FROM epcis_events e
            INNER JOIN epcis_epc_list el ON e.id = el.event_id
            INNER JOIN trace_path tp ON e.event_time > tp.event_time
            WHERE el.epc = %s
        )
        SELECT * FROM trace_path ORDER BY level
    """, (epc, epc))
    return cursor.fetchall()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
