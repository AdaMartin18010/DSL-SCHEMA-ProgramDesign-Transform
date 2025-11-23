# 食品行业Schema转换体系

## 📑 目录

- [食品行业Schema转换体系](#食品行业schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. GS1到EPCIS转换实现](#2-gs1到epcis转换实现)
    - [2.1 GS1解析和EPCIS转换](#21-gs1解析和epcis转换)
  - [3. EPCIS到GS1转换](#3-epcis到gs1转换)
  - [4. 食品安全追溯系统](#4-食品安全追溯系统)
    - [4.1 追溯链管理](#41-追溯链管理)
  - [5. 转换工具](#5-转换工具)
    - [5.1 GS1解析器集成](#51-gs1解析器集成)
    - [5.2 EPCIS转换器集成](#52-epcis转换器集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 GS1到EPCIS转换验证](#61-gs1到epcis转换验证)
  - [7. 食品行业数据存储与分析](#7-食品行业数据存储与分析)
    - [7.1 PostgreSQL食品行业数据存储](#71-postgresql食品行业数据存储)
    - [7.2 食品行业数据分析查询](#72-食品行业数据分析查询)

---

## 1. 转换体系概述

食品行业Schema转换体系支持GS1标准、EPCIS事件、
数据库存储之间的转换。

### 1.1 转换目标

1. **GS1到EPCIS转换**：GS1食品信息到EPCIS事件
2. **EPCIS到GS1转换**：EPCIS事件到GS1食品信息
3. **数据到数据库转换**：食品行业数据到PostgreSQL存储

---

## 2. GS1到EPCIS转换实现

### 2.1 GS1解析和EPCIS转换

**完整的GS1到EPCIS转换实现**：

```python
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import json

logger = logging.getLogger(__name__)

class GS1Parser:
    """GS1标准解析器"""

    def __init__(self):
        self.application_identifiers = {
            "01": "gtin",
            "10": "batch_number",
            "11": "production_date",
            "17": "expiry_date",
            "21": "serial_number",
            "310": "net_weight",
            "311": "net_weight_kg",
            "410": "ship_to_gln",
            "411": "bill_to_gln",
            "412": "purchase_from_gln",
            "414": "gln"
        }

    def parse_gs1_barcode(self, barcode: str) -> Dict:
        """解析GS1条码"""
        result = {}
        i = 0

        while i < len(barcode):
            # 查找应用标识符
            ai = None
            ai_length = 2

            # 检查2位AI
            if i + 2 <= len(barcode):
                ai = barcode[i:i+2]
                if ai in self.application_identifiers:
                    i += 2
                else:
                    # 检查3位AI
                    if i + 3 <= len(barcode):
                        ai = barcode[i:i+3]
                        if ai in self.application_identifiers:
                            ai_length = 3
                            i += 3
                        else:
                            i += 1
                            continue
                    else:
                        i += 1
                        continue

            if ai:
                # 获取数据长度
                data_length = self._get_data_length(ai)
                if i + data_length <= len(barcode):
                    data = barcode[i:i+data_length]
                    field_name = self.application_identifiers.get(ai)
                    if field_name:
                        result[field_name] = self._parse_field_value(ai, data)
                    i += data_length

        return result

    def _get_data_length(self, ai: str) -> int:
        """获取应用标识符的数据长度"""
        # 根据GS1标准定义的数据长度
        length_map = {
            "01": 14,  # GTIN
            "10": 20,  # Batch number (可变长度)
            "11": 6,   # Production date
            "17": 6,   # Expiry date
            "21": 20,  # Serial number (可变长度)
            "310": 6,  # Net weight
            "311": 6,  # Net weight kg
            "410": 13, # Ship to GLN
            "411": 13, # Bill to GLN
            "412": 13, # Purchase from GLN
            "414": 13  # GLN
        }
        return length_map.get(ai, 0)

    def _parse_field_value(self, ai: str, data: str) -> Any:
        """解析字段值"""
        if ai in ["11", "17"]:
            # 日期格式：YYMMDD
            year = int(data[:2])
            year = 2000 + year if year < 50 else 1900 + year
            month = int(data[2:4])
            day = int(data[4:6])
            return f"{year:04d}-{month:02d}-{day:02d}"
        elif ai in ["310", "311"]:
            # 重量：前3位为小数位数，后3位为重量值
            decimal_places = int(data[0])
            weight_value = int(data[1:])
            return weight_value / (10 ** decimal_places)
        else:
            return data.strip()

class GS1ToEPCISConverter:
    """GS1到EPCIS转换器"""

    def __init__(self):
        self.parser = GS1Parser()

    def convert_food_info_to_object_event(self, food_info: Dict) -> Dict:
        """将GS1食品信息转换为EPCIS ObjectEvent"""
        epcis_event = {
            "eventTime": food_info.get("production_date", datetime.now().isoformat()),
            "eventTimeZoneOffset": "+00:00",
            "eventType": "ObjectEvent",
            "epcList": [food_info.get("gtin", "")],
            "action": "ADD",
            "bizStep": "commissioning",
            "disposition": "active",
            "readPoint": {
                "id": food_info.get("production_location", "")
            },
            "bizLocation": {
                "id": food_info.get("manufacturer_gln", "")
            },
            "extension": {
                "foodInfo": {
                    "food_id": food_info.get("food_id"),
                    "food_name": food_info.get("food_name"),
                    "food_category": food_info.get("food_category"),
                    "batch_number": food_info.get("batch_number"),
                    "production_date": food_info.get("production_date"),
                    "expiry_date": food_info.get("expiry_date")
                }
            }
        }
        return epcis_event

    def convert_production_info_to_aggregation_event(self, production_info: Dict) -> Dict:
        """将GS1生产信息转换为EPCIS AggregationEvent"""
        epcis_event = {
            "eventTime": production_info.get("production_date", datetime.now().isoformat()),
            "eventTimeZoneOffset": "+00:00",
            "eventType": "AggregationEvent",
            "parentID": production_info.get("production_facility", ""),
            "childEPCs": [production_info.get("gtin", "")],
            "action": "ADD",
            "bizStep": "packing",
            "disposition": "in_transit",
            "readPoint": {
                "id": production_info.get("production_location", "")
            },
            "bizLocation": {
                "id": production_info.get("manufacturer_gln", "")
            },
            "extension": {
                "productionInfo": {
                    "production_id": production_info.get("production_id"),
                    "batch_number": production_info.get("batch_number"),
                    "batch_size": production_info.get("batch_size"),
                    "production_line": production_info.get("production_line")
                }
            }
        }
        return epcis_event

    def convert_traceability_info_to_transaction_event(self, traceability_info: Dict) -> Dict:
        """将GS1追溯信息转换为EPCIS TransactionEvent"""
        epcis_event = {
            "eventTime": traceability_info.get("event_time", datetime.now().isoformat()),
            "eventTimeZoneOffset": "+00:00",
            "eventType": "TransactionEvent",
            "epcList": [traceability_info.get("gtin", "")],
            "action": "ADD",
            "bizStep": traceability_info.get("biz_step", "shipping"),
            "disposition": "in_transit",
            "readPoint": {
                "id": traceability_info.get("event_location", "")
            },
            "bizLocation": {
                "id": traceability_info.get("location_gln", "")
            },
            "bizTransactionList": [
                {
                    "type": traceability_info.get("transaction_type", "PO"),
                    "bizTransaction": traceability_info.get("transaction_id", "")
                }
            ],
            "extension": {
                "traceabilityInfo": {
                    "event_type": traceability_info.get("event_type"),
                    "from_location": traceability_info.get("from_location"),
                    "to_location": traceability_info.get("to_location"),
                    "transport_method": traceability_info.get("transport_method")
                }
            }
        }
        return epcis_event

    def convert_to_epcis_xml(self, epcis_event: Dict) -> str:
        """将EPCIS事件转换为XML格式"""
        root = Element("epcis:EPCISDocument")
        root.set("xmlns:epcis", "urn:epcglobal:epcis:xsd:1")
        root.set("xmlns:cbvmda", "urn:epcglobal:cbv:mda")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xsi:schemaLocation", "urn:epcglobal:epcis:xsd:1 EPCISDocument.xsd")

        epcis_body = SubElement(root, "EPCISBody")
        event_list = SubElement(epcis_body, "EventList")

        # 根据事件类型创建相应的事件元素
        event_type = epcis_event.get("eventType")
        if event_type == "ObjectEvent":
            event_elem = self._create_object_event_xml(epcis_event)
        elif event_type == "AggregationEvent":
            event_elem = self._create_aggregation_event_xml(epcis_event)
        elif event_type == "TransactionEvent":
            event_elem = self._create_transaction_event_xml(epcis_event)
        else:
            event_elem = Element("UnknownEvent")

        event_list.append(event_elem)

        return tostring(root, encoding='unicode')

    def _create_object_event_xml(self, event: Dict) -> Element:
        """创建ObjectEvent XML元素"""
        event_elem = Element("ObjectEvent")

        # eventTime
        event_time_elem = SubElement(event_elem, "eventTime")
        event_time_elem.text = event.get("eventTime", "")

        # eventTimeZoneOffset
        timezone_elem = SubElement(event_elem, "eventTimeZoneOffset")
        timezone_elem.text = event.get("eventTimeZoneOffset", "+00:00")

        # epcList
        epc_list_elem = SubElement(event_elem, "epcList")
        for epc in event.get("epcList", []):
            epc_elem = SubElement(epc_list_elem, "epc")
            epc_elem.text = epc

        # action
        action_elem = SubElement(event_elem, "action")
        action_elem.text = event.get("action", "ADD")

        # bizStep
        biz_step_elem = SubElement(event_elem, "bizStep")
        biz_step_elem.text = event.get("bizStep", "")

        # disposition
        disposition_elem = SubElement(event_elem, "disposition")
        disposition_elem.text = event.get("disposition", "")

        # readPoint
        if "readPoint" in event:
            read_point_elem = SubElement(event_elem, "readPoint")
            read_point_id_elem = SubElement(read_point_elem, "id")
            read_point_id_elem.text = event["readPoint"].get("id", "")

        # bizLocation
        if "bizLocation" in event:
            biz_location_elem = SubElement(event_elem, "bizLocation")
            biz_location_id_elem = SubElement(biz_location_elem, "id")
            biz_location_id_elem.text = event["bizLocation"].get("id", "")

        # extension
        if "extension" in event:
            extension_elem = SubElement(event_elem, "extension")
            self._add_extension_xml(extension_elem, event["extension"])

        return event_elem

    def _create_aggregation_event_xml(self, event: Dict) -> Element:
        """创建AggregationEvent XML元素"""
        event_elem = Element("AggregationEvent")

        # eventTime
        event_time_elem = SubElement(event_elem, "eventTime")
        event_time_elem.text = event.get("eventTime", "")

        # eventTimeZoneOffset
        timezone_elem = SubElement(event_elem, "eventTimeZoneOffset")
        timezone_elem.text = event.get("eventTimeZoneOffset", "+00:00")

        # parentID
        if "parentID" in event:
            parent_id_elem = SubElement(event_elem, "parentID")
            parent_id_elem.text = event["parentID"]

        # childEPCs
        child_epcs_elem = SubElement(event_elem, "childEPCs")
        for epc in event.get("childEPCs", []):
            epc_elem = SubElement(child_epcs_elem, "epc")
            epc_elem.text = epc

        # action
        action_elem = SubElement(event_elem, "action")
        action_elem.text = event.get("action", "ADD")

        # bizStep
        biz_step_elem = SubElement(event_elem, "bizStep")
        biz_step_elem.text = event.get("bizStep", "")

        # disposition
        disposition_elem = SubElement(event_elem, "disposition")
        disposition_elem.text = event.get("disposition", "")

        # readPoint
        if "readPoint" in event:
            read_point_elem = SubElement(event_elem, "readPoint")
            read_point_id_elem = SubElement(read_point_elem, "id")
            read_point_id_elem.text = event["readPoint"].get("id", "")

        # bizLocation
        if "bizLocation" in event:
            biz_location_elem = SubElement(event_elem, "bizLocation")
            biz_location_id_elem = SubElement(biz_location_elem, "id")
            biz_location_id_elem.text = event["bizLocation"].get("id", "")

        # extension
        if "extension" in event:
            extension_elem = SubElement(event_elem, "extension")
            self._add_extension_xml(extension_elem, event["extension"])

        return event_elem

    def _create_transaction_event_xml(self, event: Dict) -> Element:
        """创建TransactionEvent XML元素"""
        event_elem = Element("TransactionEvent")

        # eventTime
        event_time_elem = SubElement(event_elem, "eventTime")
        event_time_elem.text = event.get("eventTime", "")

        # eventTimeZoneOffset
        timezone_elem = SubElement(event_elem, "eventTimeZoneOffset")
        timezone_elem.text = event.get("eventTimeZoneOffset", "+00:00")

        # epcList
        epc_list_elem = SubElement(event_elem, "epcList")
        for epc in event.get("epcList", []):
            epc_elem = SubElement(epc_list_elem, "epc")
            epc_elem.text = epc

        # action
        action_elem = SubElement(event_elem, "action")
        action_elem.text = event.get("action", "ADD")

        # bizStep
        biz_step_elem = SubElement(event_elem, "bizStep")
        biz_step_elem.text = event.get("bizStep", "")

        # disposition
        disposition_elem = SubElement(event_elem, "disposition")
        disposition_elem.text = event.get("disposition", "")

        # bizTransactionList
        if "bizTransactionList" in event:
            biz_trans_list_elem = SubElement(event_elem, "bizTransactionList")
            for biz_trans in event["bizTransactionList"]:
                biz_trans_elem = SubElement(biz_trans_list_elem, "bizTransaction")
                biz_trans_elem.set("type", biz_trans.get("type", ""))
                biz_trans_elem.text = biz_trans.get("bizTransaction", "")

        # readPoint
        if "readPoint" in event:
            read_point_elem = SubElement(event_elem, "readPoint")
            read_point_id_elem = SubElement(read_point_elem, "id")
            read_point_id_elem.text = event["readPoint"].get("id", "")

        # bizLocation
        if "bizLocation" in event:
            biz_location_elem = SubElement(event_elem, "bizLocation")
            biz_location_id_elem = SubElement(biz_location_elem, "id")
            biz_location_id_elem.text = event["bizLocation"].get("id", "")

        # extension
        if "extension" in event:
            extension_elem = SubElement(event_elem, "extension")
            self._add_extension_xml(extension_elem, event["extension"])

        return event_elem

    def _add_extension_xml(self, parent: Element, extension: Dict):
        """添加扩展字段到XML"""
        for key, value in extension.items():
            if isinstance(value, dict):
                elem = SubElement(parent, key)
                self._add_extension_xml(elem, value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        elem = SubElement(parent, key)
                        self._add_extension_xml(elem, item)
                    else:
                        item_elem = SubElement(parent, key)
                        item_elem.text = str(item)
            else:
                elem = SubElement(parent, key)
                elem.text = str(value)
```

---

## 3. EPCIS到GS1转换

**转换规则**：

- EPCIS ObjectEvent → GS1 Food Info
- EPCIS AggregationEvent → GS1 Production Info
- EPCIS TransactionEvent → GS1 Traceability Info

**完整转换实现**：

```python
from xml.etree.ElementTree import parse, ElementTree
from typing import Dict, Optional

class EPCISToGS1Converter:
    """EPCIS到GS1转换器"""

    def __init__(self):
        pass

    def convert_object_event_to_food_info(self, epcis_event: Dict) -> Dict:
        """将EPCIS ObjectEvent转换为GS1食品信息"""
        food_info = {
            "gtin": epcis_event.get("epcList", [])[0] if epcis_event.get("epcList") else None,
            "production_date": epcis_event.get("eventTime", "").split("T")[0] if epcis_event.get("eventTime") else None,
            "production_location": epcis_event.get("readPoint", {}).get("id"),
            "manufacturer_gln": epcis_event.get("bizLocation", {}).get("id")
        }

        # 从扩展字段提取食品信息
        if "extension" in epcis_event and "foodInfo" in epcis_event["extension"]:
            food_info.update(epcis_event["extension"]["foodInfo"])

        return food_info

    def convert_aggregation_event_to_production_info(self, epcis_event: Dict) -> Dict:
        """将EPCIS AggregationEvent转换为GS1生产信息"""
        production_info = {
            "gtin": epcis_event.get("childEPCs", [])[0] if epcis_event.get("childEPCs") else None,
            "production_date": epcis_event.get("eventTime", "").split("T")[0] if epcis_event.get("eventTime") else None,
            "production_location": epcis_event.get("readPoint", {}).get("id"),
            "manufacturer_gln": epcis_event.get("bizLocation", {}).get("id"),
            "production_facility": epcis_event.get("parentID")
        }

        # 从扩展字段提取生产信息
        if "extension" in epcis_event and "productionInfo" in epcis_event["extension"]:
            production_info.update(epcis_event["extension"]["productionInfo"])

        return production_info

    def convert_transaction_event_to_traceability_info(self, epcis_event: Dict) -> Dict:
        """将EPCIS TransactionEvent转换为GS1追溯信息"""
        traceability_info = {
            "gtin": epcis_event.get("epcList", [])[0] if epcis_event.get("epcList") else None,
            "event_time": epcis_event.get("eventTime"),
            "event_location": epcis_event.get("readPoint", {}).get("id"),
            "location_gln": epcis_event.get("bizLocation", {}).get("id"),
            "biz_step": epcis_event.get("bizStep"),
            "transaction_id": None
        }

        # 从业务事务列表提取事务ID
        if "bizTransactionList" in epcis_event:
            for biz_trans in epcis_event["bizTransactionList"]:
                traceability_info["transaction_type"] = biz_trans.get("type")
                traceability_info["transaction_id"] = biz_trans.get("bizTransaction")
                break

        # 从扩展字段提取追溯信息
        if "extension" in epcis_event and "traceabilityInfo" in epcis_event["extension"]:
            traceability_info.update(epcis_event["extension"]["traceabilityInfo"])

        return traceability_info

    def convert_from_epcis_xml(self, xml_file_path: str) -> Dict:
        """从EPCIS XML文件转换为GS1信息"""
        tree = parse(xml_file_path)
        root = tree.getroot()

        # 查找事件
        event_list = root.find(".//{urn:epcglobal:epcis:xsd:1}EventList")
        if event_list is None:
            return {}

        # 获取第一个事件
        events = event_list.findall(".//{urn:epcglobal:epcis:xsd:1}ObjectEvent")
        if events:
            event = self._parse_object_event_xml(events[0])
            return self.convert_object_event_to_food_info(event)

        events = event_list.findall(".//{urn:epcglobal:epcis:xsd:1}AggregationEvent")
        if events:
            event = self._parse_aggregation_event_xml(events[0])
            return self.convert_aggregation_event_to_production_info(event)

        events = event_list.findall(".//{urn:epcglobal:epcis:xsd:1}TransactionEvent")
        if events:
            event = self._parse_transaction_event_xml(events[0])
            return self.convert_transaction_event_to_traceability_info(event)

        return {}

    def _parse_object_event_xml(self, event_elem) -> Dict:
        """解析ObjectEvent XML元素"""
        event = {
            "eventType": "ObjectEvent",
            "epcList": []
        }

        # 解析eventTime
        event_time_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}eventTime")
        if event_time_elem is not None:
            event["eventTime"] = event_time_elem.text

        # 解析epcList
        epc_list_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}epcList")
        if epc_list_elem is not None:
            for epc_elem in epc_list_elem.findall(".//{urn:epcglobal:epcis:xsd:1}epc"):
                if epc_elem.text:
                    event["epcList"].append(epc_elem.text)

        # 解析readPoint
        read_point_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}readPoint")
        if read_point_elem is not None:
            read_point_id_elem = read_point_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if read_point_id_elem is not None:
                event["readPoint"] = {"id": read_point_id_elem.text}

        # 解析bizLocation
        biz_location_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}bizLocation")
        if biz_location_elem is not None:
            biz_location_id_elem = biz_location_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if biz_location_id_elem is not None:
                event["bizLocation"] = {"id": biz_location_id_elem.text}

        # 解析extension
        extension_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}extension")
        if extension_elem is not None:
            event["extension"] = self._parse_extension_xml(extension_elem)

        return event

    def _parse_aggregation_event_xml(self, event_elem) -> Dict:
        """解析AggregationEvent XML元素"""
        event = {
            "eventType": "AggregationEvent",
            "childEPCs": []
        }

        # 解析eventTime
        event_time_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}eventTime")
        if event_time_elem is not None:
            event["eventTime"] = event_time_elem.text

        # 解析parentID
        parent_id_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}parentID")
        if parent_id_elem is not None:
            event["parentID"] = parent_id_elem.text

        # 解析childEPCs
        child_epcs_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}childEPCs")
        if child_epcs_elem is not None:
            for epc_elem in child_epcs_elem.findall(".//{urn:epcglobal:epcis:xsd:1}epc"):
                if epc_elem.text:
                    event["childEPCs"].append(epc_elem.text)

        # 解析readPoint和bizLocation（同ObjectEvent）
        read_point_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}readPoint")
        if read_point_elem is not None:
            read_point_id_elem = read_point_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if read_point_id_elem is not None:
                event["readPoint"] = {"id": read_point_id_elem.text}

        biz_location_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}bizLocation")
        if biz_location_elem is not None:
            biz_location_id_elem = biz_location_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if biz_location_id_elem is not None:
                event["bizLocation"] = {"id": biz_location_id_elem.text}

        # 解析extension
        extension_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}extension")
        if extension_elem is not None:
            event["extension"] = self._parse_extension_xml(extension_elem)

        return event

    def _parse_transaction_event_xml(self, event_elem) -> Dict:
        """解析TransactionEvent XML元素"""
        event = {
            "eventType": "TransactionEvent",
            "epcList": [],
            "bizTransactionList": []
        }

        # 解析eventTime
        event_time_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}eventTime")
        if event_time_elem is not None:
            event["eventTime"] = event_time_elem.text

        # 解析epcList
        epc_list_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}epcList")
        if epc_list_elem is not None:
            for epc_elem in epc_list_elem.findall(".//{urn:epcglobal:epcis:xsd:1}epc"):
                if epc_elem.text:
                    event["epcList"].append(epc_elem.text)

        # 解析bizTransactionList
        biz_trans_list_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}bizTransactionList")
        if biz_trans_list_elem is not None:
            for biz_trans_elem in biz_trans_list_elem.findall(".//{urn:epcglobal:epcis:xsd:1}bizTransaction"):
                trans_type = biz_trans_elem.get("type", "")
                trans_id = biz_trans_elem.text or ""
                event["bizTransactionList"].append({
                    "type": trans_type,
                    "bizTransaction": trans_id
                })

        # 解析readPoint和bizLocation
        read_point_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}readPoint")
        if read_point_elem is not None:
            read_point_id_elem = read_point_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if read_point_id_elem is not None:
                event["readPoint"] = {"id": read_point_id_elem.text}

        biz_location_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}bizLocation")
        if biz_location_elem is not None:
            biz_location_id_elem = biz_location_elem.find(".//{urn:epcglobal:epcis:xsd:1}id")
            if biz_location_id_elem is not None:
                event["bizLocation"] = {"id": biz_location_id_elem.text}

        # 解析extension
        extension_elem = event_elem.find(".//{urn:epcglobal:epcis:xsd:1}extension")
        if extension_elem is not None:
            event["extension"] = self._parse_extension_xml(extension_elem)

        return event

    def _parse_extension_xml(self, extension_elem) -> Dict:
        """解析扩展字段XML"""
        extension = {}

        for child in extension_elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            if len(child) > 0:
                # 有子元素
                extension[tag] = self._parse_extension_xml(child)
            else:
                # 文本内容
                extension[tag] = child.text

        return extension
```

---

## 4. 食品安全追溯系统

### 4.1 追溯链管理

**完整的追溯链管理实现**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FoodTraceabilitySystem:
    """食品安全追溯系统"""

    def __init__(self, storage):
        self.storage = storage

    def create_traceability_chain(self, food_id: str, batch_number: str,
                                 traceability_data: Dict) -> str:
        """创建追溯链"""
        traceability_id = f"TRACE_{food_id}_{batch_number}"

        chain_data = {
            "traceability_id": traceability_id,
            "food_id": food_id,
            "batch_number": batch_number,
            "supplier_name": traceability_data.get("supplier_name"),
            "supplier_gln": traceability_data.get("supplier_gln"),
            "manufacturer_name": traceability_data.get("manufacturer_name"),
            "manufacturer_gln": traceability_data.get("manufacturer_gln"),
            "distributor_name": traceability_data.get("distributor_name"),
            "distributor_gln": traceability_data.get("distributor_gln"),
            "retailer_name": traceability_data.get("retailer_name"),
            "retailer_gln": traceability_data.get("retailer_gln")
        }

        self.storage.store_traceability_chain(chain_data)
        logger.info(f"Created traceability chain: {traceability_id}")
        return traceability_id

    def add_traceability_event(self, food_id: str, batch_number: str,
                              event_type: str, event_location: str,
                              event_operator: str = None, event_description: str = ""):
        """添加追溯事件"""
        event_id = f"EVENT_{food_id}_{batch_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        event_data = {
            "event_id": event_id,
            "food_id": food_id,
            "batch_number": batch_number,
            "event_type": event_type,
            "event_time": datetime.now(),
            "event_location": event_location,
            "event_operator": event_operator,
            "event_description": event_description,
            "event_data": {}
        }

        self.storage.store_traceability_event(event_data)
        logger.info(f"Added traceability event: {event_id} - {event_type}")
        return event_id

    def get_traceability_chain(self, food_id: str, batch_number: str) -> Optional[Dict]:
        """获取追溯链"""
        return self.storage.get_traceability_chain(food_id, batch_number)

    def get_traceability_history(self, food_id: str, batch_number: str) -> List[Dict]:
        """获取追溯历史"""
        return self.storage.get_traceability_events(food_id, batch_number)

    def trace_food_origin(self, food_id: str, batch_number: str) -> Dict:
        """追溯食品来源"""
        chain = self.get_traceability_chain(food_id, batch_number)
        history = self.get_traceability_history(food_id, batch_number)

        return {
            "traceability_chain": chain,
            "event_history": history,
            "origin_info": {
                "supplier": chain.get("supplier_name") if chain else None,
                "manufacturer": chain.get("manufacturer_name") if chain else None,
                "first_event": history[0] if history else None
            }
        }

    def trace_food_destination(self, food_id: str, batch_number: str) -> Dict:
        """追溯食品去向"""
        chain = self.get_traceability_chain(food_id, batch_number)
        history = self.get_traceability_history(food_id, batch_number)

        return {
            "traceability_chain": chain,
            "event_history": history,
            "destination_info": {
                "distributor": chain.get("distributor_name") if chain else None,
                "retailer": chain.get("retailer_name") if chain else None,
                "last_event": history[-1] if history else None
            }
        }

### 4.2 生产批次管理

**生产批次管理实现**：

```python
class ProductionBatchManager:
    """生产批次管理器"""

    def __init__(self, storage):
        self.storage = storage

    def create_production_batch(self, food_id: str, batch_data: Dict) -> str:
        """创建生产批次"""
        batch_number = batch_data.get("batch_number") or \
                      f"BATCH_{food_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        production_data = {
            "production_id": f"PROD_{batch_number}",
            "food_id": food_id,
            "batch_number": batch_number,
            "batch_size": batch_data.get("batch_size"),
            "production_date": batch_data.get("production_date", datetime.now().date()),
            "production_time": batch_data.get("production_time"),
            "production_location": batch_data.get("production_location"),
            "production_facility": batch_data.get("production_facility"),
            "production_line": batch_data.get("production_line")
        }

        self.storage.store_production_batch(production_data)
        logger.info(f"Created production batch: {batch_number}")
        return batch_number

    def get_batch_info(self, batch_number: str) -> Optional[Dict]:
        """获取批次信息"""
        return self.storage.get_production_batch(batch_number)

    def get_batches_by_food(self, food_id: str) -> List[Dict]:
        """获取食品的所有批次"""
        return self.storage.get_production_batches_by_food(food_id)
```

---

## 5. 转换工具

### 5.1 GS1解析器集成

详见第2.1节GS1Parser实现。

### 5.2 EPCIS转换器集成

详见第3节EPCISToGS1Converter实现。

---

## 6. 转换验证

### 6.1 GS1到EPCIS转换验证

**转换验证器实现**：

```python
class GS1EPCISConversionValidator:
    """GS1到EPCIS转换验证器"""

    def validate_gs1_to_epcis(self, gs1_data: Dict, epcis_event: Dict) -> bool:
        """验证GS1到EPCIS转换"""
        # 验证GTIN一致性
        gs1_gtin = gs1_data.get("gtin")
        epcis_gtin = epcis_event.get("epcList", [])[0] if epcis_event.get("epcList") else None

        if gs1_gtin != epcis_gtin:
            return False

        # 验证生产日期一致性
        gs1_prod_date = gs1_data.get("production_date")
        epcis_event_time = epcis_event.get("eventTime", "")
        if gs1_prod_date and epcis_event_time:
            if gs1_prod_date not in epcis_event_time:
                return False

        # 验证位置一致性
        gs1_location = gs1_data.get("production_location")
        epcis_location = epcis_event.get("readPoint", {}).get("id")
        if gs1_location != epcis_location:
            return False

        return True

    def validate_epcis_to_gs1(self, epcis_event: Dict, gs1_data: Dict) -> bool:
        """验证EPCIS到GS1转换"""
        # 验证GTIN一致性
        epcis_gtin = epcis_event.get("epcList", [])[0] if epcis_event.get("epcList") else None
        gs1_gtin = gs1_data.get("gtin")

        if epcis_gtin != gs1_gtin:
            return False

        return True
```

---

## 7. 食品行业数据存储与分析

### 7.1 PostgreSQL食品行业数据存储

**食品行业数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class FoodIndustryStorage:
    """食品行业数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建食品行业数据表"""
        # 食品表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id BIGSERIAL PRIMARY KEY,
                food_id VARCHAR(20) UNIQUE NOT NULL,
                gtin VARCHAR(14) UNIQUE NOT NULL,
                food_name VARCHAR(200) NOT NULL,
                food_category VARCHAR(50) NOT NULL,
                food_type VARCHAR(100),
                brand_name VARCHAR(100),
                manufacturer VARCHAR(200) NOT NULL,
                country_of_origin VARCHAR(2),
                food_description TEXT,
                production_date DATE NOT NULL,
                expiry_date DATE NOT NULL,
                shelf_life_days INTEGER,
                storage_conditions VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 食品成分表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS food_compositions (
                id BIGSERIAL PRIMARY KEY,
                food_id VARCHAR(20) NOT NULL,
                ingredient_name VARCHAR(200) NOT NULL,
                quantity DECIMAL(10,2),
                unit VARCHAR(20),
                FOREIGN KEY (food_id) REFERENCES foods(food_id)
            )
        """)

        # 生产批次表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS production_batches (
                id BIGSERIAL PRIMARY KEY,
                production_id VARCHAR(20) UNIQUE NOT NULL,
                food_id VARCHAR(20) NOT NULL,
                batch_number VARCHAR(50) UNIQUE NOT NULL,
                batch_size INTEGER NOT NULL,
                production_date DATE NOT NULL,
                production_time TIME,
                production_location VARCHAR(200) NOT NULL,
                production_facility VARCHAR(200) NOT NULL,
                production_line VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (food_id) REFERENCES foods(food_id)
            )
        """)

        # 追溯事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS traceability_events (
                id BIGSERIAL PRIMARY KEY,
                event_id VARCHAR(20) UNIQUE NOT NULL,
                food_id VARCHAR(20) NOT NULL,
                batch_number VARCHAR(50) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_time TIMESTAMP NOT NULL,
                event_location VARCHAR(200) NOT NULL,
                event_operator VARCHAR(100),
                event_description VARCHAR(500),
                event_data JSONB,
                FOREIGN KEY (food_id) REFERENCES foods(food_id)
            )
        """)

        # 追溯链表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS traceability_chains (
                id BIGSERIAL PRIMARY KEY,
                traceability_id VARCHAR(20) UNIQUE NOT NULL,
                food_id VARCHAR(20) NOT NULL,
                batch_number VARCHAR(50) NOT NULL,
                supplier_name VARCHAR(200),
                supplier_gln VARCHAR(13),
                manufacturer_name VARCHAR(200) NOT NULL,
                manufacturer_gln VARCHAR(13) NOT NULL,
                distributor_name VARCHAR(200),
                distributor_gln VARCHAR(13),
                retailer_name VARCHAR(200),
                retailer_gln VARCHAR(13),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (food_id) REFERENCES foods(food_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_foods_food_id
            ON foods(food_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_foods_gtin
            ON foods(gtin)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_production_batches_batch_number
            ON production_batches(batch_number)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_traceability_events_food_id
            ON traceability_events(food_id, event_time DESC)
        """)

        self.conn.commit()

    def store_food(self, food_data: Dict) -> int:
        """存储食品信息"""
        self.cur.execute("""
            INSERT INTO foods (
                food_id, gtin, food_name, food_category,
                food_type, brand_name, manufacturer,
                country_of_origin, food_description,
                production_date, expiry_date, shelf_life_days,
                storage_conditions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (food_id) DO UPDATE SET
                food_name = EXCLUDED.food_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            food_data.get("food_id"),
            food_data.get("gtin"),
            food_data.get("food_name"),
            food_data.get("food_category"),
            food_data.get("food_type"),
            food_data.get("brand_name"),
            food_data.get("manufacturer"),
            food_data.get("country_of_origin"),
            food_data.get("food_description"),
            food_data.get("production_date"),
            food_data.get("expiry_date"),
            food_data.get("shelf_life_days"),
            food_data.get("storage_conditions")
        ))
        return self.cur.fetchone()[0]

    def store_traceability_event(self, event_data: Dict) -> int:
        """存储追溯事件"""
        self.cur.execute("""
            INSERT INTO traceability_events (
                event_id, food_id, batch_number,
                event_type, event_time, event_location,
                event_operator, event_description, event_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (event_id) DO UPDATE SET
                event_time = EXCLUDED.event_time
            RETURNING id
        """, (
            event_data.get("event_id"),
            event_data.get("food_id"),
            event_data.get("batch_number"),
            event_data.get("event_type"),
            event_data.get("event_time"),
            event_data.get("event_location"),
            event_data.get("event_operator"),
            event_data.get("event_description"),
            json.dumps(event_data.get("event_data", {}))
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_traceability_chain(self, chain_data: Dict) -> int:
        """存储追溯链"""
        self.cur.execute("""
            INSERT INTO traceability_chains (
                traceability_id, food_id, batch_number,
                supplier_name, supplier_gln,
                manufacturer_name, manufacturer_gln,
                distributor_name, distributor_gln,
                retailer_name, retailer_gln
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (traceability_id) DO UPDATE SET
                supplier_name = EXCLUDED.supplier_name,
                distributor_name = EXCLUDED.distributor_name,
                retailer_name = EXCLUDED.retailer_name
            RETURNING id
        """, (
            chain_data.get("traceability_id"),
            chain_data.get("food_id"),
            chain_data.get("batch_number"),
            chain_data.get("supplier_name"),
            chain_data.get("supplier_gln"),
            chain_data.get("manufacturer_name"),
            chain_data.get("manufacturer_gln"),
            chain_data.get("distributor_name"),
            chain_data.get("distributor_gln"),
            chain_data.get("retailer_name"),
            chain_data.get("retailer_gln")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_traceability_chain(self, food_id: str, batch_number: str) -> Optional[Dict]:
        """获取追溯链"""
        self.cur.execute("""
            SELECT traceability_id, food_id, batch_number,
                   supplier_name, supplier_gln,
                   manufacturer_name, manufacturer_gln,
                   distributor_name, distributor_gln,
                   retailer_name, retailer_gln
            FROM traceability_chains
            WHERE food_id = %s AND batch_number = %s
        """, (food_id, batch_number))
        row = self.cur.fetchone()
        if row:
            return {
                "traceability_id": row[0],
                "food_id": row[1],
                "batch_number": row[2],
                "supplier_name": row[3],
                "supplier_gln": row[4],
                "manufacturer_name": row[5],
                "manufacturer_gln": row[6],
                "distributor_name": row[7],
                "distributor_gln": row[8],
                "retailer_name": row[9],
                "retailer_gln": row[10]
            }
        return None

    def get_traceability_events(self, food_id: str, batch_number: str) -> List[Dict]:
        """获取追溯事件"""
        self.cur.execute("""
            SELECT event_id, event_type, event_time, event_location,
                   event_operator, event_description, event_data
            FROM traceability_events
            WHERE food_id = %s AND batch_number = %s
            ORDER BY event_time ASC
        """, (food_id, batch_number))
        return [
            {
                "event_id": row[0],
                "event_type": row[1],
                "event_time": row[2],
                "event_location": row[3],
                "event_operator": row[4],
                "event_description": row[5],
                "event_data": json.loads(row[6]) if row[6] else {}
            }
            for row in self.cur.fetchall()
        ]

    def store_production_batch(self, batch_data: Dict) -> int:
        """存储生产批次"""
        self.cur.execute("""
            INSERT INTO production_batches (
                production_id, food_id, batch_number, batch_size,
                production_date, production_time, production_location,
                production_facility, production_line
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (production_id) DO UPDATE SET
                batch_size = EXCLUDED.batch_size
            RETURNING id
        """, (
            batch_data.get("production_id"),
            batch_data.get("food_id"),
            batch_data.get("batch_number"),
            batch_data.get("batch_size"),
            batch_data.get("production_date"),
            batch_data.get("production_time"),
            batch_data.get("production_location"),
            batch_data.get("production_facility"),
            batch_data.get("production_line")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_production_batch(self, batch_number: str) -> Optional[Dict]:
        """获取生产批次"""
        self.cur.execute("""
            SELECT production_id, food_id, batch_number, batch_size,
                   production_date, production_time, production_location,
                   production_facility, production_line
            FROM production_batches
            WHERE batch_number = %s
        """, (batch_number,))
        row = self.cur.fetchone()
        if row:
            return {
                "production_id": row[0],
                "food_id": row[1],
                "batch_number": row[2],
                "batch_size": row[3],
                "production_date": row[4],
                "production_time": row[5],
                "production_location": row[6],
                "production_facility": row[7],
                "production_line": row[8]
            }
        return None

    def get_production_batches_by_food(self, food_id: str) -> List[Dict]:
        """获取食品的所有批次"""
        self.cur.execute("""
            SELECT production_id, batch_number, batch_size,
                   production_date, production_location
            FROM production_batches
            WHERE food_id = %s
            ORDER BY production_date DESC
        """, (food_id,))
        return [
            {
                "production_id": row[0],
                "batch_number": row[1],
                "batch_size": row[2],
                "production_date": row[3],
                "production_location": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 7.2 食品行业数据分析查询

**查询示例**：

```python
    def get_food_traceability_chain(self, food_id: str, batch_number: str) -> List[Dict]:
        """查询食品追溯链"""
        self.cur.execute("""
            SELECT
                tc.traceability_id, tc.supplier_name, tc.manufacturer_name,
                tc.distributor_name, tc.retailer_name,
                te.event_type, te.event_time, te.event_location
            FROM traceability_chains tc
            LEFT JOIN traceability_events te
            ON tc.food_id = te.food_id AND tc.batch_number = te.batch_number
            WHERE tc.food_id = %s AND tc.batch_number = %s
            ORDER BY te.event_time
        """, (food_id, batch_number))
        return [
            {
                "traceability_id": row[0],
                "supplier_name": row[1],
                "manufacturer_name": row[2],
                "distributor_name": row[3],
                "retailer_name": row[4],
                "event_type": row[5],
                "event_time": row[6],
                "event_location": row[7]
            }
            for row in self.cur.fetchall()
        ]

    def get_production_statistics(self, start_date: datetime) -> List[Dict]:
        """查询生产批次统计"""
        self.cur.execute("""
            SELECT
                f.food_category,
                COUNT(*) as batch_count,
                SUM(pb.batch_size) as total_quantity,
                AVG(pb.batch_size) as avg_batch_size,
                MIN(pb.production_date) as first_batch_date,
                MAX(pb.production_date) as last_batch_date
            FROM production_batches pb
            JOIN foods f ON pb.food_id = f.food_id
            WHERE pb.production_date >= %s
            GROUP BY f.food_category
            ORDER BY batch_count DESC
        """, (start_date,))
        return [
            {
                "food_category": row[0],
                "batch_count": row[1],
                "total_quantity": float(row[2]) if row[2] else 0,
                "avg_batch_size": float(row[3]) if row[3] else 0,
                "first_batch_date": row[4],
                "last_batch_date": row[5]
            }
            for row in self.cur.fetchall()
        ]

    def get_traceability_event_statistics(self, food_id: str, batch_number: str) -> Dict:
        """查询追溯事件统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as event_count,
                COUNT(DISTINCT event_type) as event_type_count,
                MIN(event_time) as first_event_time,
                MAX(event_time) as last_event_time,
                COUNT(DISTINCT event_location) as location_count
            FROM traceability_events
            WHERE food_id = %s AND batch_number = %s
        """, (food_id, batch_number))
        row = self.cur.fetchone()
        return {
            "event_count": row[0],
            "event_type_count": row[1],
            "first_event_time": row[2],
            "last_event_time": row[3],
            "location_count": row[4]
        }

    def get_food_expiry_analysis(self, days_ahead: int = 30) -> List[Dict]:
        """查询即将过期的食品"""
        self.cur.execute("""
            SELECT
                food_id, food_name, food_category,
                expiry_date, production_date,
                EXTRACT(DAY FROM (expiry_date - CURRENT_DATE)) as days_until_expiry
            FROM foods
            WHERE expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
            ORDER BY expiry_date ASC
        """, (days_ahead,))
        return [
            {
                "food_id": row[0],
                "food_name": row[1],
                "food_category": row[2],
                "expiry_date": row[3],
                "production_date": row[4],
                "days_until_expiry": int(row[5]) if row[5] else None
            }
            for row in self.cur.fetchall()
        ]

    def get_batch_quality_summary(self, batch_number: str) -> Dict:
        """查询批次质量摘要"""
        self.cur.execute("""
            SELECT
                pb.batch_number, pb.batch_size, pb.production_date,
                f.food_name, f.food_category,
                COUNT(te.event_id) as event_count,
                COUNT(CASE WHEN te.event_type = 'QualityCheck' THEN 1 END) as quality_check_count
            FROM production_batches pb
            JOIN foods f ON pb.food_id = f.food_id
            LEFT JOIN traceability_events te ON pb.food_id = te.food_id AND pb.batch_number = te.batch_number
            WHERE pb.batch_number = %s
            GROUP BY pb.batch_number, pb.batch_size, pb.production_date, f.food_name, f.food_category
        """, (batch_number,))
        row = self.cur.fetchone()
        if row:
            return {
                "batch_number": row[0],
                "batch_size": row[1],
                "production_date": row[2],
                "food_name": row[3],
                "food_category": row[4],
                "event_count": row[5],
                "quality_check_count": row[6]
            }
        return {}
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
