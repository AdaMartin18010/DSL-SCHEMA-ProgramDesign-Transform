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

**完整的EPCIS事件处理类**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime
from xml.etree.ElementTree import Element, fromstring
import json

logger = logging.getLogger(__name__)

class EPCISEventProcessor:
    """EPCIS事件处理器 - 完整实现"""

    def __init__(self, storage):
        self.storage = storage

    def process_object_event(self, epcis_event: Dict) -> Dict:
        """处理ObjectEvent事件"""
        event_data = {
            "event_id": epcis_event.get("event_id") or self._generate_event_id(),
            "event_time": epcis_event.get("eventTime"),
            "event_timezone": epcis_event.get("eventTimeZoneOffset", "+00:00"),
            "event_type": "ObjectEvent",
            "action": epcis_event.get("action", "ADD"),
            "biz_step": epcis_event.get("bizStep"),
            "disposition": epcis_event.get("disposition"),
            "read_point": epcis_event.get("readPoint", {}).get("id") if isinstance(epcis_event.get("readPoint"), dict) else epcis_event.get("readPoint"),
            "biz_location": epcis_event.get("bizLocation", {}).get("id") if isinstance(epcis_event.get("bizLocation"), dict) else epcis_event.get("bizLocation"),
            "epc_list": epcis_event.get("epcList", []),
            "quantity_list": epcis_event.get("quantityList", []),
            "biz_transaction_list": epcis_event.get("bizTransactionList", []),
            "source_list": epcis_event.get("sourceList", []),
            "destination_list": epcis_event.get("destinationList", [])
        }

        # 存储事件
        event_id = self.storage.store_epcis_event(event_data)
        logger.info(f"Processed ObjectEvent: {event_id}")

        return {"event_id": event_id, **event_data}

    def process_aggregation_event(self, epcis_event: Dict) -> Dict:
        """处理AggregationEvent事件"""
        event_data = {
            "event_id": epcis_event.get("event_id") or self._generate_event_id(),
            "event_time": epcis_event.get("eventTime"),
            "event_timezone": epcis_event.get("eventTimeZoneOffset", "+00:00"),
            "event_type": "AggregationEvent",
            "parent_id": epcis_event.get("parentID"),
            "child_epcs": epcis_event.get("childEPCs", []),
            "action": epcis_event.get("action", "ADD"),
            "biz_step": epcis_event.get("bizStep"),
            "disposition": epcis_event.get("disposition"),
            "read_point": epcis_event.get("readPoint", {}).get("id") if isinstance(epcis_event.get("readPoint"), dict) else epcis_event.get("readPoint"),
            "biz_location": epcis_event.get("bizLocation", {}).get("id") if isinstance(epcis_event.get("bizLocation"), dict) else epcis_event.get("bizLocation"),
            "biz_transaction_list": epcis_event.get("bizTransactionList", []),
            "source_list": epcis_event.get("sourceList", []),
            "destination_list": epcis_event.get("destinationList", [])
        }

        # 存储事件
        event_id = self.storage.store_epcis_event(event_data)
        logger.info(f"Processed AggregationEvent: {event_id}")

        return {"event_id": event_id, **event_data}

    def process_transaction_event(self, epcis_event: Dict) -> Dict:
        """处理TransactionEvent事件"""
        biz_transactions = epcis_event.get("bizTransactionList", [])

        event_data = {
            "event_id": epcis_event.get("event_id") or self._generate_event_id(),
            "event_time": epcis_event.get("eventTime"),
            "event_timezone": epcis_event.get("eventTimeZoneOffset", "+00:00"),
            "event_type": "TransactionEvent",
            "epc_list": epcis_event.get("epcList", []),
            "action": epcis_event.get("action", "ADD"),
            "biz_step": epcis_event.get("bizStep"),
            "disposition": epcis_event.get("disposition"),
            "read_point": epcis_event.get("readPoint", {}).get("id") if isinstance(epcis_event.get("readPoint"), dict) else epcis_event.get("readPoint"),
            "biz_location": epcis_event.get("bizLocation", {}).get("id") if isinstance(epcis_event.get("bizLocation"), dict) else epcis_event.get("bizLocation"),
            "biz_transaction_list": biz_transactions,
            "source_list": epcis_event.get("sourceList", []),
            "destination_list": epcis_event.get("destinationList", [])
        }

        # 存储事件
        event_id = self.storage.store_epcis_event(event_data)
        logger.info(f"Processed TransactionEvent: {event_id}")

        return {"event_id": event_id, **event_data}

    def process_transformation_event(self, epcis_event: Dict) -> Dict:
        """处理TransformationEvent事件"""
        event_data = {
            "event_id": epcis_event.get("event_id") or self._generate_event_id(),
            "event_time": epcis_event.get("eventTime"),
            "event_timezone": epcis_event.get("eventTimeZoneOffset", "+00:00"),
            "event_type": "TransformationEvent",
            "transformation_id": epcis_event.get("transformationID"),
            "input_epcs": epcis_event.get("inputEPCList", []),
            "output_epcs": epcis_event.get("outputEPCList", []),
            "biz_step": epcis_event.get("bizStep"),
            "disposition": epcis_event.get("disposition"),
            "read_point": epcis_event.get("readPoint", {}).get("id") if isinstance(epcis_event.get("readPoint"), dict) else epcis_event.get("readPoint"),
            "biz_location": epcis_event.get("bizLocation", {}).get("id") if isinstance(epcis_event.get("bizLocation"), dict) else epcis_event.get("bizLocation"),
            "biz_transaction_list": epcis_event.get("bizTransactionList", []),
            "source_list": epcis_event.get("sourceList", []),
            "destination_list": epcis_event.get("destinationList", [])
        }

        # 存储事件
        event_id = self.storage.store_epcis_event(event_data)
        logger.info(f"Processed TransformationEvent: {event_id}")

        return {"event_id": event_id, **event_data}

    def process_epcis_xml(self, xml_content: str) -> List[Dict]:
        """处理EPCIS XML文档"""
        root = fromstring(xml_content)
        events = []

        # 查找EventList
        event_list = root.find(".//{urn:epcglobal:epcis:xsd:1}EventList")
        if event_list is None:
            return events

        # 处理ObjectEvent
        for event_elem in event_list.findall(".//{urn:epcglobal:epcis:xsd:1}ObjectEvent"):
            event_dict = self._parse_object_event_xml(event_elem)
            events.append(self.process_object_event(event_dict))

        # 处理AggregationEvent
        for event_elem in event_list.findall(".//{urn:epcglobal:epcis:xsd:1}AggregationEvent"):
            event_dict = self._parse_aggregation_event_xml(event_elem)
            events.append(self.process_aggregation_event(event_dict))

        # 处理TransactionEvent
        for event_elem in event_list.findall(".//{urn:epcglobal:epcis:xsd:1}TransactionEvent"):
            event_dict = self._parse_transaction_event_xml(event_elem)
            events.append(self.process_transaction_event(event_dict))

        # 处理TransformationEvent
        for event_elem in event_list.findall(".//{urn:epcglobal:epcis:xsd:1}TransformationEvent"):
            event_dict = self._parse_transformation_event_xml(event_elem)
            events.append(self.process_transformation_event(event_dict))

        return events

    def _parse_object_event_xml(self, event_elem: Element) -> Dict:
        """解析ObjectEvent XML元素"""
        event = {}

        # eventTime
        event_time_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}eventTime")
        if event_time_elem is not None:
            event["eventTime"] = event_time_elem.text

        # eventTimeZoneOffset
        timezone_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}eventTimeZoneOffset")
        if timezone_elem is not None:
            event["eventTimeZoneOffset"] = timezone_elem.text

        # epcList
        epc_list = []
        epc_list_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}epcList")
        if epc_list_elem is not None:
            for epc_elem in epc_list_elem.findall(".//{urn:epcglobal:epcis:xsd:1}epc"):
                epc_list.append(epc_elem.text)
        event["epcList"] = epc_list

        # action
        action_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}action")
        if action_elem is not None:
            event["action"] = action_elem.text

        # bizStep
        biz_step_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}bizStep")
        if biz_step_elem is not None:
            event["bizStep"] = biz_step_elem.text

        # readPoint
        read_point_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}readPoint")
        if read_point_elem is not None:
            read_point_id = read_point_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if read_point_id is not None:
                event["readPoint"] = {"id": read_point_id.text}

        # bizLocation
        biz_location_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}bizLocation")
        if biz_location_elem is not None:
            biz_location_id = biz_location_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if biz_location_id is not None:
                event["bizLocation"] = {"id": biz_location_id.text}

        return event

    def _parse_aggregation_event_xml(self, event_elem: Element) -> Dict:
        """解析AggregationEvent XML元素"""
        event = self._parse_object_event_xml(event_elem)

        # parentID
        parent_id_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}parentID")
        if parent_id_elem is not None:
            event["parentID"] = parent_id_elem.text

        # childEPCs
        child_epcs = []
        child_epcs_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}childEPCs")
        if child_epcs_elem is not None:
            for epc_elem in child_epcs_elem.findall(".//{urn:epcglobal:epcis:xsd:1}epc"):
                child_epcs.append(epc_elem.text)
        event["childEPCs"] = child_epcs

        return event

    def _parse_transaction_event_xml(self, event_elem: Element) -> Dict:
        """解析TransactionEvent XML元素"""
        event = self._parse_object_event_xml(event_elem)

        # bizTransactionList
        biz_transactions = []
        biz_trans_list_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}bizTransactionList")
        if biz_trans_list_elem is not None:
            for biz_trans_elem in biz_trans_list_elem.findall(".//{urn:epcglobal:epcis:xsd:1}bizTransaction"):
                trans_type = biz_trans_elem.get("type")
                trans_value = biz_trans_elem.text
                biz_transactions.append({"type": trans_type, "bizTransaction": trans_value})
        event["bizTransactionList"] = biz_transactions

        return event

    def _parse_transformation_event_xml(self, event_elem: Element) -> Dict:
        """解析TransformationEvent XML元素"""
        event = {}

        # eventTime
        event_time_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}eventTime")
        if event_time_elem is not None:
            event["eventTime"] = event_time_elem.text

        # transformationID
        transformation_id_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}transformationID")
        if transformation_id_elem is not None:
            event["transformationID"] = transformation_id_elem.text

        # inputEPCList
        input_epcs = []
        input_epc_list_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}inputEPCList")
        if input_epc_list_elem is not None:
            for epc_elem in input_epc_list_elem.findall(".//{urn:epcglobal:epcis:xsd:1}epc"):
                input_epcs.append(epc_elem.text)
        event["inputEPCList"] = input_epcs

        # outputEPCList
        output_epcs = []
        output_epc_list_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}outputEPCList")
        if output_epc_list_elem is not None:
            for epc_elem in output_epc_list_elem.findall(".//{urn:epcglobal:epcis:xsd:1}epc"):
                output_epcs.append(epc_elem.text)
        event["outputEPCList"] = output_epcs

        return event

    def _generate_event_id(self) -> str:
        """生成事件ID"""
        import uuid
        return str(uuid.uuid4())
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
                parent_id VARCHAR(255),
                child_epcs JSONB,
                input_epcs JSONB,
                output_epcs JSONB,
                transformation_id VARCHAR(255),
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
        """存储EPCIS事件 - 完整实现"""
        cursor = self.conn.cursor()
        import json

        # 插入EPCIS事件主记录
        cursor.execute("""
            INSERT INTO epcis_events (
                event_id, event_time, event_timezone, event_type,
                action, biz_step, disposition, read_point, biz_location,
                parent_id, child_epcs, input_epcs, output_epcs, transformation_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s
            ) ON CONFLICT (event_id) DO UPDATE SET
                event_time = EXCLUDED.event_time,
                event_type = EXCLUDED.event_type,
                action = EXCLUDED.action,
                biz_step = EXCLUDED.biz_step,
                disposition = EXCLUDED.disposition,
                read_point = EXCLUDED.read_point,
                biz_location = EXCLUDED.biz_location,
                parent_id = EXCLUDED.parent_id,
                child_epcs = EXCLUDED.child_epcs,
                input_epcs = EXCLUDED.input_epcs,
                output_epcs = EXCLUDED.output_epcs,
                transformation_id = EXCLUDED.transformation_id
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
            epcis_event.get("biz_location"),
            epcis_event.get("parent_id"),
            json.dumps(epcis_event.get("child_epcs", [])),
            json.dumps(epcis_event.get("input_epcs", [])),
            json.dumps(epcis_event.get("output_epcs", [])),
            epcis_event.get("transformation_id")
        ))

        result = cursor.fetchone()
        if result:
            event_db_id = result[0]

            # 删除旧的EPC列表（如果更新）
            cursor.execute("""
                DELETE FROM epcis_epc_list WHERE event_id = %s
            """, (event_db_id,))

            # 插入EPC列表（epc_list用于ObjectEvent和TransactionEvent）
            for epc in epcis_event.get("epc_list", []):
                cursor.execute("""
                    INSERT INTO epcis_epc_list (event_id, epc)
                    VALUES (%s, %s)
                """, (event_db_id, epc))

            # 插入child EPCs（用于AggregationEvent）
            for epc in epcis_event.get("child_epcs", []):
                cursor.execute("""
                    INSERT INTO epcis_epc_list (event_id, epc)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (event_db_id, epc))

            # 插入input EPCs（用于TransformationEvent）
            for epc in epcis_event.get("input_epcs", []):
                cursor.execute("""
                    INSERT INTO epcis_epc_list (event_id, epc)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (event_db_id, epc))

            # 插入output EPCs（用于TransformationEvent）
            for epc in epcis_event.get("output_epcs", []):
                cursor.execute("""
                    INSERT INTO epcis_epc_list (event_id, epc)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (event_db_id, epc))

            # 删除旧的业务交易列表（如果更新）
            cursor.execute("""
                DELETE FROM epcis_biz_transactions WHERE event_id = %s
            """, (event_db_id,))

            # 插入业务交易列表
            for biz_transaction in epcis_event.get("biz_transaction_list", []):
                transaction_type = biz_transaction.get("type") if isinstance(biz_transaction, dict) else None
                transaction_value = biz_transaction.get("bizTransaction") if isinstance(biz_transaction, dict) else str(biz_transaction)
                cursor.execute("""
                    INSERT INTO epcis_biz_transactions (event_id, transaction_type, transaction_value)
                    VALUES (%s, %s, %s)
                """, (event_db_id, transaction_type, transaction_value))

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
        """根据EPC查询EPCIS事件 - 完整实现"""
        cursor = self.conn.cursor()
        import json

        query = """
            SELECT DISTINCT e.id, e.event_id, e.event_time, e.event_timezone, e.event_type,
                   e.action, e.biz_step, e.disposition, e.read_point, e.biz_location,
                   e.parent_id, e.child_epcs, e.input_epcs, e.output_epcs, e.transformation_id
            FROM epcis_events e
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

        query += " ORDER BY e.event_time ASC"

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        events = []
        for row in rows:
            events.append({
                "id": str(row[0]),
                "event_id": row[1],
                "event_time": row[2],
                "event_timezone": row[3],
                "event_type": row[4],
                "action": row[5],
                "biz_step": row[6],
                "disposition": row[7],
                "read_point": row[8],
                "biz_location": row[9],
                "parent_id": row[10],
                "child_epcs": json.loads(row[11]) if isinstance(row[11], str) else row[11] if row[11] else [],
                "input_epcs": json.loads(row[12]) if isinstance(row[12], str) else row[12] if row[12] else [],
                "output_epcs": json.loads(row[13]) if isinstance(row[13], str) else row[13] if row[13] else [],
                "transformation_id": row[14]
            })

        cursor.close()
        return events
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

**完整的追溯链查询类**：

```python
class GS1TraceabilityQuery:
    """GS1追溯链查询类 - 完整实现"""

    def __init__(self, storage):
        self.storage = storage

    def trace_forward(self, epc: str) -> Dict:
        """正向追溯（从生产到销售）"""
        events = self.storage.query_epcis_events_by_epc(epc)

        if not events:
            return {"error": f"No events found for EPC: {epc}"}

        # 按时间顺序排序
        sorted_events = sorted(events, key=lambda x: x.get("event_time", datetime.min))

        trace_path = []
        for i, event in enumerate(sorted_events):
            trace_path.append({
                "step": i + 1,
                "event_id": event.get("id"),
                "event_type": event.get("event_type"),
                "event_time": event.get("event_time"),
                "biz_step": event.get("biz_step"),
                "action": event.get("action"),
                "read_point": event.get("read_point"),
                "biz_location": event.get("biz_location")
            })

        # 获取第一个和最后一个事件的位置
        origin = None
        destination = None

        if sorted_events:
            first_event = sorted_events[0]
            origin = {
                "read_point": first_event.get("read_point"),
                "biz_location": first_event.get("biz_location"),
                "event_time": first_event.get("event_time")
            }

            last_event = sorted_events[-1]
            destination = {
                "read_point": last_event.get("read_point"),
                "biz_location": last_event.get("biz_location"),
                "event_time": last_event.get("event_time")
            }

        return {
            "epc": epc,
            "trace_direction": "forward",
            "origin": origin,
            "destination": destination,
            "trace_path": trace_path,
            "total_steps": len(trace_path)
        }

    def trace_backward(self, epc: str) -> Dict:
        """反向追溯（从销售到生产）"""
        events = self.storage.query_epcis_events_by_epc(epc)

        if not events:
            return {"error": f"No events found for EPC: {epc}"}

        # 按时间倒序排序
        sorted_events = sorted(events, key=lambda x: x.get("event_time", datetime.min), reverse=True)

        trace_path = []
        for i, event in enumerate(sorted_events):
            trace_path.append({
                "step": i + 1,
                "event_id": event.get("id"),
                "event_type": event.get("event_type"),
                "event_time": event.get("event_time"),
                "biz_step": event.get("biz_step"),
                "action": event.get("action"),
                "read_point": event.get("read_point"),
                "biz_location": event.get("biz_location")
            })

        # 获取最后一个和第一个事件的位置（反向）
        starting_point = None
        origin = None

        if sorted_events:
            last_event = sorted_events[0]  # 最新的事件
            starting_point = {
                "read_point": last_event.get("read_point"),
                "biz_location": last_event.get("biz_location"),
                "event_time": last_event.get("event_time")
            }

            first_event = sorted_events[-1]  # 最早的事件
            origin = {
                "read_point": first_event.get("read_point"),
                "biz_location": first_event.get("biz_location"),
                "event_time": first_event.get("event_time")
            }

        return {
            "epc": epc,
            "trace_direction": "backward",
            "starting_point": starting_point,
            "origin": origin,
            "trace_path": trace_path,
            "total_steps": len(trace_path)
        }

    def trace_by_gtin(self, gtin: str, serial: str = None) -> Dict:
        """根据GTIN追溯"""
        # 将GTIN转换为EPC
        if serial:
            epc = convert_gtin_to_epc(gtin, serial)
        else:
            # 如果没有序列号，查找所有相关的EPC
            epcs = self._find_epcs_by_gtin(gtin)
            if not epcs:
                return {"error": f"No EPCs found for GTIN: {gtin}"}

            # 返回所有EPC的追溯结果
            results = []
            for epc in epcs:
                forward_trace = self.trace_forward(epc)
                if "error" not in forward_trace:
                    results.append(forward_trace)

            return {
                "gtin": gtin,
                "epc_count": len(epcs),
                "trace_results": results
            }

        return self.trace_forward(epc)

    def trace_by_gln(self, gln: str, start_time: datetime = None, end_time: datetime = None) -> Dict:
        """根据GLN追溯（位置追溯）"""
        cursor = self.storage.conn.cursor()

        query = """
            SELECT DISTINCT e.*
            FROM epcis_events e
            WHERE (e.read_point = %s OR e.biz_location = %s)
        """
        params = [gln, gln]

        if start_time:
            query += " AND e.event_time >= %s"
            params.append(start_time)

        if end_time:
            query += " AND e.event_time <= %s"
            params.append(end_time)

        query += " ORDER BY e.event_time ASC"

        cursor.execute(query, tuple(params))
        events = cursor.fetchall()

        if not events:
            return {"error": f"No events found for GLN: {gln}"}

        # 获取所有相关的EPC
        epcs = set()
        for event in events:
            event_id = event[0]  # 假设id是第一个字段
            cursor.execute("""
                SELECT epc FROM epcis_epc_list WHERE event_id = %s
            """, (event_id,))
            for row in cursor.fetchall():
                epcs.add(row[0])

        return {
            "gln": gln,
            "event_count": len(events),
            "epc_count": len(epcs),
            "epcs": list(epcs),
            "events": [
                {
                    "event_id": event[0],
                    "event_time": event[1],
                    "event_type": event[2],
                    "biz_step": event[3],
                    "read_point": event[4],
                    "biz_location": event[5]
                }
                for event in events
            ]
        }

    def get_traceability_chain(self, epc: str) -> Dict:
        """获取完整的追溯链（包含上下游关系）"""
        forward_trace = self.trace_forward(epc)
        backward_trace = self.trace_backward(epc)

        # 查找聚合关系（父子关系）
        aggregation_events = self._find_aggregation_events(epc)

        # 查找转换关系（输入输出关系）
        transformation_events = self._find_transformation_events(epc)

        return {
            "epc": epc,
            "forward_trace": forward_trace,
            "backward_trace": backward_trace,
            "aggregation_relations": aggregation_events,
            "transformation_relations": transformation_events,
            "chain_complete": True
        }

    def visualize_trace_path(self, epc: str, direction: str = "forward") -> Dict:
        """追溯路径可视化"""
        if direction == "forward":
            trace_result = self.trace_forward(epc)
        else:
            trace_result = self.trace_backward(epc)

        if "error" in trace_result:
            return trace_result

        # 构建可视化数据
        nodes = []
        edges = []

        # 添加起始节点
        if direction == "forward":
            origin = trace_result.get("origin", {})
            nodes.append({
                "id": "origin",
                "label": origin.get("biz_location", "Origin"),
                "type": "origin",
                "data": origin
            })
        else:
            starting_point = trace_result.get("starting_point", {})
            nodes.append({
                "id": "start",
                "label": starting_point.get("biz_location", "Start"),
                "type": "start",
                "data": starting_point
            })

        # 添加事件节点
        trace_path = trace_result.get("trace_path", [])
        for i, step in enumerate(trace_path):
            node_id = f"step_{i+1}"
            nodes.append({
                "id": node_id,
                "label": step.get("biz_step", step.get("event_type", "")),
                "type": step.get("event_type", ""),
                "location": step.get("read_point", ""),
                "time": step.get("event_time"),
                "data": step
            })

            # 添加边
            if i == 0:
                prev_node_id = "origin" if direction == "forward" else "start"
            else:
                prev_node_id = f"step_{i}"

            edges.append({
                "from": prev_node_id,
                "to": node_id,
                "label": step.get("biz_step", "")
            })

        # 添加结束节点
        if direction == "forward":
            destination = trace_result.get("destination", {})
            nodes.append({
                "id": "destination",
                "label": destination.get("biz_location", "Destination"),
                "type": "destination",
                "data": destination
            })
            if trace_path:
                edges.append({
                    "from": f"step_{len(trace_path)}",
                    "to": "destination",
                    "label": "Final destination"
                })
        else:
            origin = trace_result.get("origin", {})
            nodes.append({
                "id": "origin",
                "label": origin.get("biz_location", "Origin"),
                "type": "origin",
                "data": origin
            })
            if trace_path:
                edges.append({
                    "from": f"step_{len(trace_path)}",
                    "to": "origin",
                    "label": "Original source"
                })

        return {
            "epc": epc,
            "direction": direction,
            "visualization": {
                "nodes": nodes,
                "edges": edges
            },
            "summary": {
                "total_steps": trace_result.get("total_steps", 0),
                "origin": trace_result.get("origin", {}),
                "destination": trace_result.get("destination", {})
            }
        }

    def _find_epcs_by_gtin(self, gtin: str) -> List[str]:
        """根据GTIN查找所有EPC"""
        cursor = self.storage.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT el.epc
            FROM epcis_epc_list el
            WHERE el.epc LIKE %s
        """, (f"%{gtin}%",))
        return [row[0] for row in cursor.fetchall()]

    def _find_aggregation_events(self, epc: str) -> List[Dict]:
        """查找聚合事件（父子关系）"""
        cursor = self.storage.conn.cursor()
        cursor.execute("""
            SELECT e.id, e.event_time, e.parent_id, e.child_epcs
            FROM epcis_events e
            WHERE e.event_type = 'AggregationEvent'
            AND (%s = ANY(e.child_epcs::jsonb::text[]) OR e.parent_id = %s)
            ORDER BY e.event_time ASC
        """, (epc, epc))

        return [
            {
                "event_id": row[0],
                "event_time": row[1],
                "parent_id": row[2],
                "child_epcs": json.loads(row[3]) if isinstance(row[3], str) else row[3]
            }
            for row in cursor.fetchall()
        ]

    def _find_transformation_events(self, epc: str) -> List[Dict]:
        """查找转换事件（输入输出关系）"""
        cursor = self.storage.conn.cursor()
        cursor.execute("""
            SELECT e.id, e.event_time, e.input_epcs, e.output_epcs, e.transformation_id
            FROM epcis_events e
            WHERE e.event_type = 'TransformationEvent'
            AND (%s = ANY(e.input_epcs::jsonb::text[]) OR %s = ANY(e.output_epcs::jsonb::text[]))
            ORDER BY e.event_time ASC
        """, (epc, epc))

        return [
            {
                "event_id": row[0],
                "event_time": row[1],
                "input_epcs": json.loads(row[2]) if isinstance(row[2], str) else row[2],
                "output_epcs": json.loads(row[3]) if isinstance(row[3], str) else row[3],
                "transformation_id": row[4]
            }
            for row in cursor.fetchall()
        ]
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
