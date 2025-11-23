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

    def convert_transformation_info_to_transformation_event(self, transformation_info: Dict) -> Dict:
        """将GS1转换信息转换为EPCIS TransformationEvent"""
        epcis_event = {
            "eventTime": transformation_info.get("event_time", datetime.now().isoformat()),
            "eventTimeZoneOffset": "+00:00",
            "eventType": "TransformationEvent",
            "inputEPCList": transformation_info.get("input_epcs", []),
            "outputEPCList": transformation_info.get("output_epcs", []),
            "bizStep": transformation_info.get("biz_step", "transforming"),
            "disposition": "in_transit",
            "readPoint": {
                "id": transformation_info.get("transformation_location", "")
            },
            "bizLocation": {
                "id": transformation_info.get("location_gln", "")
            },
            "extension": {
                "transformationInfo": {
                    "transformation_type": transformation_info.get("transformation_type"),
                    "input_quantity": transformation_info.get("input_quantity"),
                    "output_quantity": transformation_info.get("output_quantity"),
                    "transformation_process": transformation_info.get("transformation_process"),
                    "equipment_id": transformation_info.get("equipment_id")
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
        elif event_type == "TransformationEvent":
            event_elem = self._create_transformation_event_xml(epcis_event)
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

    def _create_transformation_event_xml(self, event: Dict) -> Element:
        """创建TransformationEvent XML元素"""
        event_elem = Element("TransformationEvent")

        # eventTime
        event_time_elem = SubElement(event_elem, "eventTime")
        event_time_elem.text = event.get("eventTime", "")

        # eventTimeZoneOffset
        timezone_elem = SubElement(event_elem, "eventTimeZoneOffset")
        timezone_elem.text = event.get("eventTimeZoneOffset", "+00:00")

        # inputEPCList
        input_epc_list_elem = SubElement(event_elem, "inputEPCList")
        for epc in event.get("inputEPCList", []):
            epc_elem = SubElement(input_epc_list_elem, "epc")
            epc_elem.text = epc

        # outputEPCList
        output_epc_list_elem = SubElement(event_elem, "outputEPCList")
        for epc in event.get("outputEPCList", []):
            epc_elem = SubElement(output_epc_list_elem, "epc")
            epc_elem.text = epc

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

**完整的EPCIS事件处理类**：

```python
class EPCISEventProcessor:
    """EPCIS事件处理器"""

    def __init__(self, storage):
        self.storage = storage
        self.converter = GS1ToEPCISConverter()

    def process_object_event(self, epcis_event: Dict) -> Dict:
        """处理ObjectEvent事件"""
        event_data = {
            "event_id": f"OBJ_{epcis_event.get('epcList', [''])[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "event_type": "ObjectEvent",
            "epc": epcis_event.get("epcList", [""])[0] if epcis_event.get("epcList") else "",
            "action": epcis_event.get("action", ""),
            "biz_step": epcis_event.get("bizStep", ""),
            "disposition": epcis_event.get("disposition", ""),
            "event_time": epcis_event.get("eventTime", ""),
            "read_point": epcis_event.get("readPoint", {}).get("id", ""),
            "biz_location": epcis_event.get("bizLocation", {}).get("id", ""),
            "event_data": epcis_event
        }

        # 存储事件
        self.storage.store_epcis_event(event_data)

        logger.info(f"Processed ObjectEvent: {event_data['event_id']}")
        return event_data

    def process_aggregation_event(self, epcis_event: Dict) -> Dict:
        """处理AggregationEvent事件"""
        event_data = {
            "event_id": f"AGG_{epcis_event.get('parentID', '')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "event_type": "AggregationEvent",
            "parent_id": epcis_event.get("parentID", ""),
            "child_epcs": epcis_event.get("childEPCs", []),
            "action": epcis_event.get("action", ""),
            "biz_step": epcis_event.get("bizStep", ""),
            "disposition": epcis_event.get("disposition", ""),
            "event_time": epcis_event.get("eventTime", ""),
            "read_point": epcis_event.get("readPoint", {}).get("id", ""),
            "biz_location": epcis_event.get("bizLocation", {}).get("id", ""),
            "event_data": epcis_event
        }

        # 存储事件
        self.storage.store_epcis_event(event_data)

        logger.info(f"Processed AggregationEvent: {event_data['event_id']}")
        return event_data

    def process_transaction_event(self, epcis_event: Dict) -> Dict:
        """处理TransactionEvent事件"""
        biz_transactions = epcis_event.get("bizTransactionList", [])
        transaction_id = ""
        transaction_type = ""

        if biz_transactions:
            transaction_id = biz_transactions[0].get("bizTransaction", "")
            transaction_type = biz_transactions[0].get("type", "")

        event_data = {
            "event_id": f"TXN_{transaction_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "event_type": "TransactionEvent",
            "epc": epcis_event.get("epcList", [""])[0] if epcis_event.get("epcList") else "",
            "transaction_id": transaction_id,
            "transaction_type": transaction_type,
            "action": epcis_event.get("action", ""),
            "biz_step": epcis_event.get("bizStep", ""),
            "disposition": epcis_event.get("disposition", ""),
            "event_time": epcis_event.get("eventTime", ""),
            "read_point": epcis_event.get("readPoint", {}).get("id", ""),
            "biz_location": epcis_event.get("bizLocation", {}).get("id", ""),
            "event_data": epcis_event
        }

        # 存储事件
        self.storage.store_epcis_event(event_data)

        logger.info(f"Processed TransactionEvent: {event_data['event_id']}")
        return event_data

    def process_transformation_event(self, epcis_event: Dict) -> Dict:
        """处理TransformationEvent事件"""
        event_data = {
            "event_id": f"TRF_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "event_type": "TransformationEvent",
            "input_epcs": epcis_event.get("inputEPCList", []),
            "output_epcs": epcis_event.get("outputEPCList", []),
            "biz_step": epcis_event.get("bizStep", ""),
            "disposition": epcis_event.get("disposition", ""),
            "event_time": epcis_event.get("eventTime", ""),
            "read_point": epcis_event.get("readPoint", {}).get("id", ""),
            "biz_location": epcis_event.get("bizLocation", {}).get("id", ""),
            "event_data": epcis_event
        }

        # 从扩展字段提取转换信息
        if "extension" in epcis_event and "transformationInfo" in epcis_event["extension"]:
            transformation_info = epcis_event["extension"]["transformationInfo"]
            event_data.update({
                "transformation_type": transformation_info.get("transformation_type"),
                "input_quantity": transformation_info.get("input_quantity"),
                "output_quantity": transformation_info.get("output_quantity"),
                "transformation_process": transformation_info.get("transformation_process"),
                "equipment_id": transformation_info.get("equipment_id")
            })

        # 存储事件
        self.storage.store_epcis_event(event_data)

        logger.info(f"Processed TransformationEvent: {event_data['event_id']}")
        return event_data

    def process_epcis_event(self, epcis_event: Dict) -> Dict:
        """处理EPCIS事件（自动识别类型）"""
        event_type = epcis_event.get("eventType", "")

        if event_type == "ObjectEvent":
            return self.process_object_event(epcis_event)
        elif event_type == "AggregationEvent":
            return self.process_aggregation_event(epcis_event)
        elif event_type == "TransactionEvent":
            return self.process_transaction_event(epcis_event)
        elif event_type == "TransformationEvent":
            return self.process_transformation_event(epcis_event)
        else:
            raise ValueError(f"Unknown event type: {event_type}")

    def process_epcis_xml(self, xml_content: str) -> List[Dict]:
        """处理EPCIS XML文档"""
        from xml.etree.ElementTree import fromstring

        root = fromstring(xml_content)
        events = []

        # 查找所有事件
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

    def _parse_object_event_xml(self, event_elem) -> Dict:
        """解析ObjectEvent XML元素"""
        event = {"eventType": "ObjectEvent"}
        # 解析逻辑（简化）
        return event

    def _parse_aggregation_event_xml(self, event_elem) -> Dict:
        """解析AggregationEvent XML元素"""
        event = {"eventType": "AggregationEvent"}
        # 解析逻辑（简化）
        return event

    def _parse_transaction_event_xml(self, event_elem) -> Dict:
        """解析TransactionEvent XML元素"""
        event = {"eventType": "TransactionEvent"}
        # 解析逻辑（简化）
        return event

    def _parse_transformation_event_xml(self, event_elem) -> Dict:
        """解析TransformationEvent XML元素"""
        event = {"eventType": "TransformationEvent"}
        # 解析逻辑（简化）
        return event
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

    def trace_forward(self, food_id: str, batch_number: str) -> Dict:
        """正向追溯（从生产到销售）"""
        chain = self.get_traceability_chain(food_id, batch_number)
        history = self.get_traceability_history(food_id, batch_number)

        # 按时间顺序排序
        sorted_history = sorted(history, key=lambda x: x.get("event_time", datetime.min))

        trace_path = []
        current_location = None

        for event in sorted_history:
            event_type = event.get("event_type", "")
            event_location = event.get("event_location", "")

            trace_path.append({
                "step": len(trace_path) + 1,
                "event_type": event_type,
                "event_time": event.get("event_time"),
                "location": event_location,
                "operator": event.get("event_operator"),
                "description": event.get("event_description")
            })

            current_location = event_location

        return {
            "food_id": food_id,
            "batch_number": batch_number,
            "trace_direction": "forward",
            "origin": {
                "supplier": chain.get("supplier_name") if chain else None,
                "manufacturer": chain.get("manufacturer_name") if chain else None,
                "first_event": sorted_history[0] if sorted_history else None
            },
            "destination": {
                "distributor": chain.get("distributor_name") if chain else None,
                "retailer": chain.get("retailer_name") if chain else None,
                "last_event": sorted_history[-1] if sorted_history else None
            },
            "trace_path": trace_path,
            "total_steps": len(trace_path)
        }

    def trace_backward(self, food_id: str, batch_number: str) -> Dict:
        """反向追溯（从销售到生产）"""
        chain = self.get_traceability_chain(food_id, batch_number)
        history = self.get_traceability_history(food_id, batch_number)

        # 按时间倒序排序
        sorted_history = sorted(history, key=lambda x: x.get("event_time", datetime.min), reverse=True)

        trace_path = []

        for event in sorted_history:
            event_type = event.get("event_type", "")
            event_location = event.get("event_location", "")

            trace_path.append({
                "step": len(trace_path) + 1,
                "event_type": event_type,
                "event_time": event.get("event_time"),
                "location": event_location,
                "operator": event.get("event_operator"),
                "description": event.get("event_description")
            })

        return {
            "food_id": food_id,
            "batch_number": batch_number,
            "trace_direction": "backward",
            "starting_point": {
                "retailer": chain.get("retailer_name") if chain else None,
                "distributor": chain.get("distributor_name") if chain else None,
                "last_event": sorted_history[0] if sorted_history else None
            },
            "origin": {
                "supplier": chain.get("supplier_name") if chain else None,
                "manufacturer": chain.get("manufacturer_name") if chain else None,
                "first_event": sorted_history[-1] if sorted_history else None
            },
            "trace_path": trace_path,
            "total_steps": len(trace_path)
        }

    def visualize_trace_path(self, food_id: str, batch_number: str, direction: str = "forward") -> Dict:
        """追溯路径可视化"""
        if direction == "forward":
            trace_result = self.trace_forward(food_id, batch_number)
        else:
            trace_result = self.trace_backward(food_id, batch_number)

        # 构建可视化数据
        nodes = []
        edges = []

        # 添加起始节点
        if direction == "forward":
            origin = trace_result.get("origin", {})
            nodes.append({
                "id": "origin",
                "label": origin.get("manufacturer", "Origin"),
                "type": "manufacturer",
                "data": origin
            })
        else:
            starting_point = trace_result.get("starting_point", {})
            nodes.append({
                "id": "start",
                "label": starting_point.get("retailer", "Start"),
                "type": "retailer",
                "data": starting_point
            })

        # 添加事件节点
        trace_path = trace_result.get("trace_path", [])
        for i, step in enumerate(trace_path):
            node_id = f"step_{i+1}"
            nodes.append({
                "id": node_id,
                "label": step.get("event_type", ""),
                "type": step.get("event_type", ""),
                "location": step.get("location", ""),
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
                "label": step.get("description", "")
            })

        # 添加结束节点
        if direction == "forward":
            destination = trace_result.get("destination", {})
            end_node_id = f"step_{len(trace_path)+1}"
            nodes.append({
                "id": "destination",
                "label": destination.get("retailer", "Destination"),
                "type": "retailer",
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
                "label": origin.get("manufacturer", "Origin"),
                "type": "manufacturer",
                "data": origin
            })
            if trace_path:
                edges.append({
                    "from": f"step_{len(trace_path)}",
                    "to": "origin",
                    "label": "Original source"
                })

        return {
            "food_id": food_id,
            "batch_number": batch_number,
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

    def trace_by_epc(self, epc: str) -> Dict:
        """根据EPC追溯"""
        # 从EPCIS事件中查找相关事件
        events = self.storage.get_epcis_events_by_epc(epc)

        if not events:
            return {"error": "No events found for EPC"}

        # 提取food_id和batch_number
        first_event = events[0]
        event_data = first_event.get("event_data", {})

        # 尝试从扩展字段提取
        food_id = None
        batch_number = None

        if "extension" in event_data:
            if "foodInfo" in event_data["extension"]:
                food_id = event_data["extension"]["foodInfo"].get("food_id")
                batch_number = event_data["extension"]["foodInfo"].get("batch_number")
            elif "productionInfo" in event_data["extension"]:
                batch_number = event_data["extension"]["productionInfo"].get("batch_number")

        if food_id and batch_number:
            return self.trace_forward(food_id, batch_number)
        else:
            return {
                "epc": epc,
                "events": events,
                "warning": "Could not extract food_id and batch_number from events"
            }

class QualityMonitor:
    """质量监控系统"""

    def __init__(self, storage):
        self.storage = storage
        self.quality_rules = {}

    def add_quality_rule(self, rule_id: str, rule_config: Dict):
        """添加质量检测规则"""
        rule = {
            "rule_id": rule_id,
            "rule_name": rule_config.get("rule_name", ""),
            "rule_type": rule_config.get("rule_type", "threshold"),  # threshold, range, pattern
            "parameter_name": rule_config.get("parameter_name", ""),
            "threshold_value": rule_config.get("threshold_value"),
            "min_value": rule_config.get("min_value"),
            "max_value": rule_config.get("max_value"),
            "pattern": rule_config.get("pattern"),
            "severity": rule_config.get("severity", "medium"),  # low, medium, high, critical
            "alert_message": rule_config.get("alert_message", ""),
            "enabled": rule_config.get("enabled", True)
        }

        self.quality_rules[rule_id] = rule
        self.storage.store_quality_rule(rule)

        logger.info(f"Added quality rule: {rule_id}")
        return rule_id

    def check_quality(self, food_id: str, batch_number: str, quality_data: Dict) -> Dict:
        """质量检测"""
        results = {
            "food_id": food_id,
            "batch_number": batch_number,
            "check_time": datetime.now(),
            "passed": True,
            "violations": [],
            "warnings": [],
            "quality_score": 100.0
        }

        # 检查所有启用的规则
        for rule_id, rule in self.quality_rules.items():
            if not rule.get("enabled", True):
                continue

            parameter_name = rule.get("parameter_name", "")
            if parameter_name not in quality_data:
                continue

            parameter_value = quality_data[parameter_name]
            rule_type = rule.get("rule_type", "")

            violation = None

            if rule_type == "threshold":
                threshold = rule.get("threshold_value")
                if threshold is not None:
                    if rule.get("parameter_name", "").endswith("_max"):
                        if parameter_value > threshold:
                            violation = {
                                "rule_id": rule_id,
                                "rule_name": rule.get("rule_name", ""),
                                "parameter": parameter_name,
                                "value": parameter_value,
                                "threshold": threshold,
                                "severity": rule.get("severity", "medium"),
                                "message": rule.get("alert_message", "")
                            }
                    elif rule.get("parameter_name", "").endswith("_min"):
                        if parameter_value < threshold:
                            violation = {
                                "rule_id": rule_id,
                                "rule_name": rule.get("rule_name", ""),
                                "parameter": parameter_name,
                                "value": parameter_value,
                                "threshold": threshold,
                                "severity": rule.get("severity", "medium"),
                                "message": rule.get("alert_message", "")
                            }

            elif rule_type == "range":
                min_value = rule.get("min_value")
                max_value = rule.get("max_value")
                if min_value is not None and parameter_value < min_value:
                    violation = {
                        "rule_id": rule_id,
                        "rule_name": rule.get("rule_name", ""),
                        "parameter": parameter_name,
                        "value": parameter_value,
                        "min_value": min_value,
                        "severity": rule.get("severity", "medium"),
                        "message": rule.get("alert_message", "")
                    }
                elif max_value is not None and parameter_value > max_value:
                    violation = {
                        "rule_id": rule_id,
                        "rule_name": rule.get("rule_name", ""),
                        "parameter": parameter_name,
                        "value": parameter_value,
                        "max_value": max_value,
                        "severity": rule.get("severity", "medium"),
                        "message": rule.get("alert_message", "")
                    }

            elif rule_type == "pattern":
                pattern = rule.get("pattern", "")
                import re
                if pattern and not re.match(pattern, str(parameter_value)):
                    violation = {
                        "rule_id": rule_id,
                        "rule_name": rule.get("rule_name", ""),
                        "parameter": parameter_name,
                        "value": parameter_value,
                        "pattern": pattern,
                        "severity": rule.get("severity", "medium"),
                        "message": rule.get("alert_message", "")
                    }

            if violation:
                results["passed"] = False
                severity = violation.get("severity", "medium")

                if severity in ["high", "critical"]:
                    results["violations"].append(violation)
                else:
                    results["warnings"].append(violation)

        # 计算质量得分
        total_rules = len([r for r in self.quality_rules.values() if r.get("enabled", True)])
        if total_rules > 0:
            violation_count = len(results["violations"]) + len(results["warnings"])
            results["quality_score"] = max(0, 100 - (violation_count / total_rules) * 100)

        # 存储质量检测结果
        self.storage.store_quality_check(results)

        # 触发预警
        if results["violations"]:
            self._trigger_alert(food_id, batch_number, results)

        return results

    def _trigger_alert(self, food_id: str, batch_number: str, check_results: Dict):
        """触发质量预警"""
        for violation in check_results.get("violations", []):
            alert = {
                "alert_id": f"ALERT_{food_id}_{batch_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "food_id": food_id,
                "batch_number": batch_number,
                "rule_id": violation.get("rule_id"),
                "rule_name": violation.get("rule_name", ""),
                "severity": violation.get("severity", "medium"),
                "message": violation.get("message", ""),
                "alert_time": datetime.now(),
                "status": "active"
            }

            self.storage.store_quality_alert(alert)
            logger.warning(f"Quality alert triggered: {alert['alert_id']} - {violation.get('message', '')}")

    def generate_quality_report(self, food_id: str = None, batch_number: str = None,
                               start_date: datetime = None, end_date: datetime = None) -> Dict:
        """生成质量报告"""
        # 获取质量检测记录
        quality_checks = self.storage.get_quality_checks(
            food_id=food_id,
            batch_number=batch_number,
            start_date=start_date,
            end_date=end_date
        )

        if not quality_checks:
            return {"error": "No quality checks found"}

        # 统计信息
        total_checks = len(quality_checks)
        passed_checks = len([c for c in quality_checks if c.get("passed", False)])
        failed_checks = total_checks - passed_checks

        # 计算平均质量得分
        avg_quality_score = sum(c.get("quality_score", 0) for c in quality_checks) / total_checks if total_checks > 0 else 0

        # 统计违规类型
        violation_types = {}
        for check in quality_checks:
            for violation in check.get("violations", []):
                rule_name = violation.get("rule_name", "Unknown")
                violation_types[rule_name] = violation_types.get(rule_name, 0) + 1

        # 统计预警
        alerts = self.storage.get_quality_alerts(
            food_id=food_id,
            batch_number=batch_number,
            start_date=start_date,
            end_date=end_date
        )

        active_alerts = len([a for a in alerts if a.get("status") == "active"])

        return {
            "report_period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "pass_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
                "average_quality_score": avg_quality_score,
                "active_alerts": active_alerts
            },
            "violation_statistics": violation_types,
            "quality_checks": quality_checks,
            "alerts": alerts,
            "generated_at": datetime.now().isoformat()
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

import psycopg2
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FoodIndustryStorage:
    """食品行业数据存储系统 - 增强错误处理"""

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
            logger.info("FoodIndustryStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing FoodIndustryStorage: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize FoodIndustryStorage: {e}") from e

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

        # EPCIS事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS epcis_events (
                id BIGSERIAL PRIMARY KEY,
                event_id VARCHAR(50) UNIQUE NOT NULL,
                event_type VARCHAR(20) NOT NULL,
                epc VARCHAR(50),
                parent_id VARCHAR(50),
                child_epcs JSONB,
                input_epcs JSONB,
                output_epcs JSONB,
                transaction_id VARCHAR(50),
                transaction_type VARCHAR(20),
                action VARCHAR(10),
                biz_step VARCHAR(50),
                disposition VARCHAR(50),
                event_time TIMESTAMP NOT NULL,
                read_point VARCHAR(200),
                biz_location VARCHAR(200),
                event_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 质量检测表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_checks (
                id BIGSERIAL PRIMARY KEY,
                check_id VARCHAR(50) UNIQUE NOT NULL,
                food_id VARCHAR(20) NOT NULL,
                batch_number VARCHAR(50) NOT NULL,
                check_time TIMESTAMP NOT NULL,
                passed BOOLEAN NOT NULL,
                quality_score DECIMAL(5,2),
                violations JSONB,
                warnings JSONB,
                check_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (food_id) REFERENCES foods(food_id)
            )
        """)

        # 质量检测规则表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_rules (
                id BIGSERIAL PRIMARY KEY,
                rule_id VARCHAR(50) UNIQUE NOT NULL,
                rule_name VARCHAR(200) NOT NULL,
                rule_type VARCHAR(20) NOT NULL,
                parameter_name VARCHAR(100) NOT NULL,
                threshold_value DECIMAL(10,2),
                min_value DECIMAL(10,2),
                max_value DECIMAL(10,2),
                pattern VARCHAR(200),
                severity VARCHAR(20) NOT NULL,
                alert_message TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 质量预警表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_alerts (
                id BIGSERIAL PRIMARY KEY,
                alert_id VARCHAR(50) UNIQUE NOT NULL,
                food_id VARCHAR(20) NOT NULL,
                batch_number VARCHAR(50) NOT NULL,
                rule_id VARCHAR(50) NOT NULL,
                rule_name VARCHAR(200),
                severity VARCHAR(20) NOT NULL,
                message TEXT,
                alert_time TIMESTAMP NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                resolved_time TIMESTAMP,
                resolution_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (food_id) REFERENCES foods(food_id),
                FOREIGN KEY (rule_id) REFERENCES quality_rules(rule_id)
            )
        """)

        # 传感器数据表（用于质量监控）
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id BIGSERIAL PRIMARY KEY,
                sensor_id VARCHAR(50) NOT NULL,
                food_id VARCHAR(20),
                batch_number VARCHAR(50),
                sensor_type VARCHAR(50) NOT NULL,
                parameter_name VARCHAR(100) NOT NULL,
                parameter_value DECIMAL(10,4) NOT NULL,
                unit VARCHAR(20),
                measurement_time TIMESTAMP NOT NULL,
                location VARCHAR(200),
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

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_epcis_events_event_type
            ON epcis_events(event_type, event_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_epcis_events_epc
            ON epcis_events(epc, event_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_quality_checks_food_id
            ON quality_checks(food_id, batch_number, check_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_quality_alerts_status
            ON quality_alerts(status, alert_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_sensor_data_food_id
            ON sensor_data(food_id, batch_number, measurement_time DESC)
        """)

        self.conn.commit()

    def store_food(self, food_data: Dict) -> int:
        """存储食品信息 - 增强错误处理"""
        # 输入验证
        if not isinstance(food_data, dict):
            raise TypeError(f"Food data must be a dictionary, got {type(food_data)}")

        if not food_data:
            raise ValueError("Food data cannot be empty")

        food_id = food_data.get("food_id")
        if not food_id:
            raise ValueError("Food ID is required")

        if not isinstance(food_id, str):
            raise TypeError(f"Food ID must be a string, got {type(food_id)}")

        if len(food_id) > 20:
            raise ValueError(f"Food ID too long: {len(food_id)} (max 20)")

        gtin = food_data.get("gtin")
        if not gtin:
            raise ValueError("GTIN is required")

        if not isinstance(gtin, str):
            raise TypeError(f"GTIN must be a string, got {type(gtin)}")

        if len(gtin) > 14:
            raise ValueError(f"GTIN too long: {len(gtin)} (max 14)")

        food_name = food_data.get("food_name")
        if not food_name:
            raise ValueError("Food name is required")

        if not isinstance(food_name, str):
            raise TypeError(f"Food name must be a string, got {type(food_name)}")

        if len(food_name) > 200:
            raise ValueError(f"Food name too long: {len(food_name)} (max 200)")

        manufacturer = food_data.get("manufacturer")
        if not manufacturer:
            raise ValueError("Manufacturer is required")

        if not isinstance(manufacturer, str):
            raise TypeError(f"Manufacturer must be a string, got {type(manufacturer)}")

        # 验证日期
        production_date = food_data.get("production_date")
        if not production_date:
            raise ValueError("Production date is required")

        if not isinstance(production_date, date):
            raise TypeError(f"Production date must be a date, got {type(production_date)}")

        expiry_date = food_data.get("expiry_date")
        if not expiry_date:
            raise ValueError("Expiry date is required")

        if not isinstance(expiry_date, date):
            raise TypeError(f"Expiry date must be a date, got {type(expiry_date)}")

        if expiry_date <= production_date:
            raise ValueError(f"Expiry date ({expiry_date}) must be after production date ({production_date})")

        # 验证国家代码
        country_of_origin = food_data.get("country_of_origin")
        if country_of_origin is not None:
            if not isinstance(country_of_origin, str):
                raise TypeError(f"Country of origin must be a string or None, got {type(country_of_origin)}")
            if len(country_of_origin) != 2:
                raise ValueError(f"Country code must be 2 characters long, got {len(country_of_origin)}")

        try:
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
                food_id,
                gtin,
                food_name,
                food_data.get("food_category"),
                food_data.get("food_type"),
                food_data.get("brand_name"),
                manufacturer,
                country_of_origin,
                food_data.get("food_description"),
                production_date,
                expiry_date,
                food_data.get("shelf_life_days"),
                food_data.get("storage_conditions")
            ))

            result = self.cur.fetchone()
            if not result:
                raise ValueError("Failed to store food data")

            self.conn.commit()
            logger.info(f"Stored food data: {food_id}")
            return result[0]

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing food data: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate food ID or GTIN or constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing food data: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing food data: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store food data: {e}") from e

    def store_traceability_event(self, event_data: Dict) -> int:
        """存储追溯事件 - 增强错误处理"""
        # 输入验证
        if not isinstance(event_data, dict):
            raise TypeError(f"Event data must be a dictionary, got {type(event_data)}")

        if not event_data:
            raise ValueError("Event data cannot be empty")

        event_id = event_data.get("event_id")
        if not event_id:
            raise ValueError("Event ID is required")

        if not isinstance(event_id, str):
            raise TypeError(f"Event ID must be a string, got {type(event_id)}")

        if len(event_id) > 20:
            raise ValueError(f"Event ID too long: {len(event_id)} (max 20)")

        food_id = event_data.get("food_id")
        if not food_id:
            raise ValueError("Food ID is required")

        if not isinstance(food_id, str):
            raise TypeError(f"Food ID must be a string, got {type(food_id)}")

        batch_number = event_data.get("batch_number")
        if not batch_number:
            raise ValueError("Batch number is required")

        if not isinstance(batch_number, str):
            raise TypeError(f"Batch number must be a string, got {type(batch_number)}")

        event_type = event_data.get("event_type")
        if not event_type:
            raise ValueError("Event type is required")

        if not isinstance(event_type, str):
            raise TypeError(f"Event type must be a string, got {type(event_type)}")

        event_time = event_data.get("event_time")
        if not event_time:
            raise ValueError("Event time is required")

        if not isinstance(event_time, datetime):
            raise TypeError(f"Event time must be a datetime, got {type(event_time)}")

        event_location = event_data.get("event_location")
        if not event_location:
            raise ValueError("Event location is required")

        try:
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
                event_id,
                food_id,
                batch_number,
                event_type,
                event_time,
                event_location,
                event_data.get("event_operator"),
                event_data.get("event_description"),
                json.dumps(event_data.get("event_data", {}))
            ))

            result = self.cur.fetchone()
            if not result:
                raise ValueError("Failed to store traceability event")

            self.conn.commit()
            logger.info(f"Stored traceability event: {event_id}")
            return result[0]

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing traceability event: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate event ID or foreign key constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing traceability event: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing traceability event: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store traceability event: {e}") from e

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

    def store_epcis_event(self, event_data: Dict) -> int:
        """存储EPCIS事件"""
        self.cur.execute("""
            INSERT INTO epcis_events (
                event_id, event_type, epc, parent_id, child_epcs,
                input_epcs, output_epcs, transaction_id, transaction_type,
                action, biz_step, disposition, event_time,
                read_point, biz_location, event_data
            ) VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id
        """, (
            event_data.get("event_id"),
            event_data.get("event_type"),
            event_data.get("epc"),
            event_data.get("parent_id"),
            json.dumps(event_data.get("child_epcs", [])),
            json.dumps(event_data.get("input_epcs", [])),
            json.dumps(event_data.get("output_epcs", [])),
            event_data.get("transaction_id"),
            event_data.get("transaction_type"),
            event_data.get("action"),
            event_data.get("biz_step"),
            event_data.get("disposition"),
            event_data.get("event_time"),
            event_data.get("read_point"),
            event_data.get("biz_location"),
            json.dumps(event_data.get("event_data", {}))
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_epcis_events_by_epc(self, epc: str) -> List[Dict]:
        """根据EPC获取EPCIS事件"""
        self.cur.execute("""
            SELECT event_id, event_type, epc, event_time, event_data
            FROM epcis_events
            WHERE epc = %s OR %s = ANY(child_epcs::jsonb::text[]) OR %s = ANY(input_epcs::jsonb::text[]) OR %s = ANY(output_epcs::jsonb::text[])
            ORDER BY event_time ASC
        """, (epc, epc, epc, epc))

        return [
            {
                "event_id": row[0],
                "event_type": row[1],
                "epc": row[2],
                "event_time": row[3],
                "event_data": json.loads(row[4]) if isinstance(row[4], str) else row[4]
            }
            for row in self.cur.fetchall()
        ]

    def store_quality_rule(self, rule_data: Dict) -> int:
        """存储质量检测规则"""
        self.cur.execute("""
            INSERT INTO quality_rules (
                rule_id, rule_name, rule_type, parameter_name,
                threshold_value, min_value, max_value, pattern,
                severity, alert_message, enabled
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rule_id) DO UPDATE SET
                rule_name = EXCLUDED.rule_name,
                enabled = EXCLUDED.enabled,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            rule_data.get("rule_id"),
            rule_data.get("rule_name"),
            rule_data.get("rule_type"),
            rule_data.get("parameter_name"),
            rule_data.get("threshold_value"),
            rule_data.get("min_value"),
            rule_data.get("max_value"),
            rule_data.get("pattern"),
            rule_data.get("severity"),
            rule_data.get("alert_message"),
            rule_data.get("enabled", True)
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_quality_check(self, check_data: Dict) -> int:
        """存储质量检测结果"""
        check_id = check_data.get("check_id") or \
                  f"QC_{check_data.get('food_id')}_{check_data.get('batch_number')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        self.cur.execute("""
            INSERT INTO quality_checks (
                check_id, food_id, batch_number, check_time,
                passed, quality_score, violations, warnings, check_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
            RETURNING id
        """, (
            check_id,
            check_data.get("food_id"),
            check_data.get("batch_number"),
            check_data.get("check_time"),
            check_data.get("passed"),
            check_data.get("quality_score"),
            json.dumps(check_data.get("violations", [])),
            json.dumps(check_data.get("warnings", [])),
            json.dumps(check_data)
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_quality_checks(self, food_id: str = None, batch_number: str = None,
                          start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """获取质量检测记录"""
        query = """
            SELECT check_id, food_id, batch_number, check_time,
                   passed, quality_score, violations, warnings
            FROM quality_checks
            WHERE 1=1
        """
        params = []

        if food_id:
            query += " AND food_id = %s"
            params.append(food_id)

        if batch_number:
            query += " AND batch_number = %s"
            params.append(batch_number)

        if start_date:
            query += " AND check_time >= %s"
            params.append(start_date)

        if end_date:
            query += " AND check_time <= %s"
            params.append(end_date)

        query += " ORDER BY check_time DESC"

        self.cur.execute(query, tuple(params))

        return [
            {
                "check_id": row[0],
                "food_id": row[1],
                "batch_number": row[2],
                "check_time": row[3],
                "passed": row[4],
                "quality_score": float(row[5]) if row[5] else None,
                "violations": json.loads(row[6]) if isinstance(row[6], str) else row[6],
                "warnings": json.loads(row[7]) if isinstance(row[7], str) else row[7]
            }
            for row in self.cur.fetchall()
        ]

    def store_quality_alert(self, alert_data: Dict) -> int:
        """存储质量预警"""
        self.cur.execute("""
            INSERT INTO quality_alerts (
                alert_id, food_id, batch_number, rule_id, rule_name,
                severity, message, alert_time, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            alert_data.get("alert_id"),
            alert_data.get("food_id"),
            alert_data.get("batch_number"),
            alert_data.get("rule_id"),
            alert_data.get("rule_name"),
            alert_data.get("severity"),
            alert_data.get("message"),
            alert_data.get("alert_time"),
            alert_data.get("status", "active")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_quality_alerts(self, food_id: str = None, batch_number: str = None,
                          start_date: datetime = None, end_date: datetime = None,
                          status: str = None) -> List[Dict]:
        """获取质量预警"""
        query = """
            SELECT alert_id, food_id, batch_number, rule_id, rule_name,
                   severity, message, alert_time, status, resolved_time
            FROM quality_alerts
            WHERE 1=1
        """
        params = []

        if food_id:
            query += " AND food_id = %s"
            params.append(food_id)

        if batch_number:
            query += " AND batch_number = %s"
            params.append(batch_number)

        if start_date:
            query += " AND alert_time >= %s"
            params.append(start_date)

        if end_date:
            query += " AND alert_time <= %s"
            params.append(end_date)

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY alert_time DESC"

        self.cur.execute(query, tuple(params))

        return [
            {
                "alert_id": row[0],
                "food_id": row[1],
                "batch_number": row[2],
                "rule_id": row[3],
                "rule_name": row[4],
                "severity": row[5],
                "message": row[6],
                "alert_time": row[7],
                "status": row[8],
                "resolved_time": row[9]
            }
            for row in self.cur.fetchall()
        ]

    def store_sensor_data(self, sensor_data: Dict) -> int:
        """存储传感器数据"""
        self.cur.execute("""
            INSERT INTO sensor_data (
                sensor_id, food_id, batch_number, sensor_type,
                parameter_name, parameter_value, unit, measurement_time, location
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            sensor_data.get("sensor_id"),
            sensor_data.get("food_id"),
            sensor_data.get("batch_number"),
            sensor_data.get("sensor_type"),
            sensor_data.get("parameter_name"),
            sensor_data.get("parameter_value"),
            sensor_data.get("unit"),
            sensor_data.get("measurement_time"),
            sensor_data.get("location")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

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
