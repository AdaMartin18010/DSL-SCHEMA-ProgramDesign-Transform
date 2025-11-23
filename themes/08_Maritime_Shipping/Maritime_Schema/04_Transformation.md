# 海运与航运Schema转换体系

## 📑 目录

- [海运与航运Schema转换体系](#海运与航运schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. EDIFACT消息处理实现](#2-edifact消息处理实现)
    - [2.1 EDIFACT解析器](#21-edifact解析器)
  - [3. XML到EDIFACT转换](#3-xml到edifact转换)
  - [4. 船舶位置追踪系统](#4-船舶位置追踪系统)
    - [4.1 AIS数据集成](#41-ais数据集成)
  - [5. 转换工具](#5-转换工具)
    - [5.1 EDIFACT解析器集成](#51-edifact解析器集成)
    - [5.2 XML转换器集成](#52-xml转换器集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 EDIFACT消息验证](#61-edifact消息验证)
  - [7. 海运航运数据存储与分析](#7-海运航运数据存储与分析)
    - [7.1 PostgreSQL海运航运数据存储](#71-postgresql海运航运数据存储)
    - [7.2 海运航运数据分析查询](#72-海运航运数据分析查询)

---

## 1. 转换体系概述

海运与航运Schema转换体系支持EDIFACT消息、XML文档、
数据库存储之间的转换。

### 1.1 转换目标

1. **EDIFACT到XML转换**：EDIFACT消息到XML文档
2. **XML到EDIFACT转换**：XML文档到EDIFACT消息
3. **数据到数据库转换**：海运航运数据到PostgreSQL存储

---

## 2. EDIFACT消息处理实现

### 2.1 EDIFACT解析器

**完整的EDIFACT解析和转换实现**：

```python
import logging
import re
from typing import Dict, List, Optional, Tuple
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime

logger = logging.getLogger(__name__)

class EDIFACTParser:
    """EDIFACT消息解析器"""

    def __init__(self):
        self.segment_terminator = "'"
        self.element_separator = "+"
        self.component_separator = ":"
        self.release_character = "?"

    def parse_message(self, edifact_message: str) -> List[Dict]:
        """解析EDIFACT消息"""
        segments = []
        lines = edifact_message.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 移除段终止符
            if line.endswith(self.segment_terminator):
                line = line[:-1]

            # 解析段
            segment = self._parse_segment(line)
            if segment:
                segments.append(segment)

        return segments

    def _parse_segment(self, segment_line: str) -> Optional[Dict]:
        """解析单个段"""
        if not segment_line:
            return None

        parts = segment_line.split(self.element_separator)
        if not parts:
            return None

        tag = parts[0]
        elements = []

        for part in parts[1:]:
            # 解析复合元素
            if self.component_separator in part:
                components = part.split(self.component_separator)
                elements.append({
                    "type": "composite",
                    "components": components
                })
            else:
                elements.append({
                    "type": "simple",
                    "value": part
                })

        return {
            "tag": tag,
            "elements": elements
        }

    def parse_iftmin(self, segments: List[Dict]) -> Dict:
        """解析IFTMIN消息（货物清单）"""
        cargo_manifest = {
            "message_type": "IFTMIN",
            "cargoes": []
        }

        current_cargo = {}

        for segment in segments:
            tag = segment.get("tag")

            if tag == "BGM":
                # 消息开始
                cargo_manifest["message_reference"] = segment["elements"][0].get("value", "")

            elif tag == "DTM":
                # 日期时间
                date_type = segment["elements"][0].get("value", "")
                date_value = segment["elements"][1].get("value", "")
                if date_type == "137":
                    cargo_manifest["document_date"] = self._parse_edifact_date(date_value)

            elif tag == "TDT":
                # 运输详情
                transport_mode = segment["elements"][0].get("value", "")
                vessel_name = ""
                if len(segment["elements"]) > 3:
                    vessel_elem = segment["elements"][3]
                    if vessel_elem.get("type") == "composite":
                        vessel_name = vessel_elem["components"][0] if vessel_elem["components"] else ""
                cargo_manifest["vessel_name"] = vessel_name

            elif tag == "LOC":
                # 地点
                location_type = segment["elements"][0].get("value", "")
                location_code = ""
                location_name = ""
                if len(segment["elements"]) > 1:
                    loc_elem = segment["elements"][1]
                    if loc_elem.get("type") == "composite":
                        location_code = loc_elem["components"][0] if loc_elem["components"] else ""
                        location_name = loc_elem["components"][1] if len(loc_elem["components"]) > 1 else ""

                if location_type == "5":
                    cargo_manifest["loading_port"] = location_name
                    cargo_manifest["loading_port_code"] = location_code
                elif location_type == "8":
                    cargo_manifest["discharge_port"] = location_name
                    cargo_manifest["discharge_port_code"] = location_code

            elif tag == "GID":
                # 货物描述
                if current_cargo:
                    cargo_manifest["cargoes"].append(current_cargo)
                current_cargo = {
                    "cargo_name": segment["elements"][0].get("value", "") if segment["elements"] else ""
                }

            elif tag == "MEA":
                # 测量
                measure_type = segment["elements"][0].get("value", "")
                if measure_type == "WT":
                    weight_elem = segment["elements"][1]
                    if weight_elem.get("type") == "composite":
                        current_cargo["weight"] = float(weight_elem["components"][0]) if weight_elem["components"] else 0.0

        if current_cargo:
            cargo_manifest["cargoes"].append(current_cargo)

        return cargo_manifest

    def parse_iftmcs(self, segments: List[Dict]) -> Dict:
        """解析IFTMCS消息（货物状态）"""
        cargo_status = {
            "message_type": "IFTMCS",
            "status_updates": []
        }

        current_update = {}

        for segment in segments:
            tag = segment.get("tag")

            if tag == "BGM":
                cargo_status["message_reference"] = segment["elements"][0].get("value", "")

            elif tag == "RFF":
                # 参考
                ref_type = segment["elements"][0].get("value", "")
                ref_value = segment["elements"][1].get("value", "") if len(segment["elements"]) > 1 else ""
                if ref_type == "BM":
                    current_update["cargo_id"] = ref_value

            elif tag == "DTM":
                # 日期时间
                date_type = segment["elements"][0].get("value", "")
                date_value = segment["elements"][1].get("value", "")
                if date_type == "137":
                    current_update["event_time"] = self._parse_edifact_date(date_value)

            elif tag == "LOC":
                # 地点
                location_type = segment["elements"][0].get("value", "")
                location_name = ""
                if len(segment["elements"]) > 1:
                    loc_elem = segment["elements"][1]
                    if loc_elem.get("type") == "composite":
                        location_name = loc_elem["components"][1] if len(loc_elem["components"]) > 1 else ""
                current_update["event_location"] = location_name

            elif tag == "STS":
                # 状态
                status_code = segment["elements"][0].get("value", "")
                current_update["status"] = status_code
                if current_update:
                    cargo_status["status_updates"].append(current_update)
                    current_update = {}

        return cargo_status

    def parse_iftman(self, segments: List[Dict]) -> Dict:
        """解析IFTMAN消息（到达通知）"""
        arrival_notice = {
            "message_type": "IFTMAN",
            "arrival_info": {}
        }

        for segment in segments:
            tag = segment.get("tag")

            if tag == "BGM":
                arrival_notice["message_reference"] = segment["elements"][0].get("value", "")

            elif tag == "TDT":
                # 运输详情
                vessel_name = ""
                if len(segment["elements"]) > 3:
                    vessel_elem = segment["elements"][3]
                    if vessel_elem.get("type") == "composite":
                        vessel_name = vessel_elem["components"][0] if vessel_elem["components"] else ""
                arrival_notice["arrival_info"]["vessel_name"] = vessel_name

            elif tag == "LOC":
                # 地点
                location_type = segment["elements"][0].get("value", "")
                location_name = ""
                location_code = ""
                if len(segment["elements"]) > 1:
                    loc_elem = segment["elements"][1]
                    if loc_elem.get("type") == "composite":
                        location_code = loc_elem["components"][0] if loc_elem["components"] else ""
                        location_name = loc_elem["components"][1] if len(loc_elem["components"]) > 1 else ""

                if location_type == "8":
                    arrival_notice["arrival_info"]["port_name"] = location_name
                    arrival_notice["arrival_info"]["port_code"] = location_code

            elif tag == "DTM":
                # 日期时间
                date_type = segment["elements"][0].get("value", "")
                date_value = segment["elements"][1].get("value", "")
                if date_type == "132":
                    arrival_notice["arrival_info"]["eta"] = self._parse_edifact_date(date_value)
                elif date_type == "133":
                    arrival_notice["arrival_info"]["ata"] = self._parse_edifact_date(date_value)

        return arrival_notice

    def _parse_edifact_date(self, date_str: str) -> Optional[str]:
        """解析EDIFACT日期格式"""
        # EDIFACT日期格式：YYYYMMDD或YYYYMMDDHHMM
        if len(date_str) == 8:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        elif len(date_str) >= 12:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T{date_str[8:10]}:{date_str[10:12]}:00Z"
        return None

    def validate_message(self, edifact_message: str) -> Tuple[bool, List[str]]:
        """验证EDIFACT消息"""
        errors = []

        # 检查消息是否为空
        if not edifact_message or not edifact_message.strip():
            errors.append("Empty message")
            return False, errors

        # 解析消息
        segments = self.parse_message(edifact_message)

        if not segments:
            errors.append("No segments found")
            return False, errors

        # 检查消息头（UNH）
        has_unh = False
        for segment in segments:
            if segment.get("tag") == "UNH":
                has_unh = True
                # 验证UNH段格式
                if len(segment.get("elements", [])) < 1:
                    errors.append("UNH segment missing message reference")
                break

        if not has_unh:
            errors.append("Missing UNH segment (message header)")

        # 检查消息尾（UNT）
        has_unt = False
        for segment in segments:
            if segment.get("tag") == "UNT":
                has_unt = True
                # 验证UNT段格式
                if len(segment.get("elements", [])) < 1:
                    errors.append("UNT segment missing segment count")
                break

        if not has_unt:
            errors.append("Missing UNT segment (message trailer)")

        # 验证段计数
        if has_unh and has_unt:
            segment_count = len(segments)
            unt_elements = [s for s in segments if s.get("tag") == "UNT"][0].get("elements", [])
            if unt_elements:
                declared_count = unt_elements[0].get("value", "")
                try:
                    declared_count_int = int(declared_count)
                    if declared_count_int != segment_count:
                        errors.append(f"Segment count mismatch: declared {declared_count_int}, actual {segment_count}")
                except ValueError:
                    errors.append(f"Invalid segment count in UNT: {declared_count}")

        # 验证必需段
        required_segments = {
            "IFTMIN": ["UNH", "BGM", "TDT", "LOC", "GID"],
            "IFTMCS": ["UNH", "BGM", "RFF", "STS"],
            "IFTMAN": ["UNH", "BGM", "TDT", "LOC", "DTM"]
        }

        # 检测消息类型
        message_type = None
        for segment in segments:
            if segment.get("tag") == "UNH":
                msg_type_elem = segment.get("elements", [{}])[0]
                if msg_type_elem.get("type") == "composite":
                    message_type = msg_type_elem.get("components", [""])[0]
                break

        if message_type and message_type in required_segments:
            segment_tags = [s.get("tag") for s in segments]
            for required_tag in required_segments[message_type]:
                if required_tag not in segment_tags:
                    errors.append(f"Missing required segment: {required_tag}")

        return len(errors) == 0, errors

    def parse_element_with_validation(self, element_str: str, element_definition: Dict) -> Optional[Dict]:
        """解析元素并验证"""
        # 元素定义格式：{"type": "simple|composite", "max_length": 10, "required": True}
        if not element_str:
            if element_definition.get("required", False):
                raise ValueError(f"Required element is missing")
            return None

        # 验证长度
        max_length = element_definition.get("max_length")
        if max_length and len(element_str) > max_length:
            raise ValueError(f"Element exceeds max length: {max_length}")

        # 解析元素
        if element_definition.get("type") == "composite":
            if self.component_separator in element_str:
                components = element_str.split(self.component_separator)
                return {
                    "type": "composite",
                    "components": components
                }
            else:
                return {
                    "type": "composite",
                    "components": [element_str]
                }
        else:
            return {
                "type": "simple",
                "value": element_str
            }

    def parse_segment_with_definition(self, segment_line: str, segment_definition: Dict) -> Optional[Dict]:
        """根据段定义解析段"""
        if not segment_line:
            return None

        parts = segment_line.split(self.element_separator)
        if not parts:
            return None

        tag = parts[0]

        # 验证段标签
        expected_tag = segment_definition.get("tag")
        if expected_tag and tag != expected_tag:
            raise ValueError(f"Segment tag mismatch: expected {expected_tag}, got {tag}")

        elements = []
        element_definitions = segment_definition.get("elements", [])

        for i, part in enumerate(parts[1:], start=0):
            if i < len(element_definitions):
                element_def = element_definitions[i]
                try:
                    parsed_element = self.parse_element_with_validation(part, element_def)
                    if parsed_element:
                        elements.append(parsed_element)
                except ValueError as e:
                    logger.warning(f"Element validation failed: {e}")
                    elements.append({
                        "type": "simple",
                        "value": part
                    })
            else:
                # 超出定义的元素，直接解析
                if self.component_separator in part:
                    elements.append({
                        "type": "composite",
                        "components": part.split(self.component_separator)
                    })
                else:
                    elements.append({
                        "type": "simple",
                        "value": part
                    })

        return {
            "tag": tag,
            "elements": elements
        }

class EDIFACTToXMLConverter:
    """EDIFACT到XML转换器"""

    def __init__(self):
        self.parser = EDIFACTParser()

    def convert_to_xml(self, edifact_message: str, message_type: str = None) -> str:
        """将EDIFACT消息转换为XML"""
        segments = self.parser.parse_message(edifact_message)

        # 自动检测消息类型
        if not message_type:
            message_type = self._detect_message_type(segments)

        # 根据消息类型解析
        if message_type == "IFTMIN":
            data = self.parser.parse_iftmin(segments)
            return self._convert_iftmin_to_xml(data)
        elif message_type == "IFTMCS":
            data = self.parser.parse_iftmcs(segments)
            return self._convert_iftmcs_to_xml(data)
        elif message_type == "IFTMAN":
            data = self.parser.parse_iftman(segments)
            return self._convert_iftman_to_xml(data)
        else:
            # 通用转换
            return self._convert_segments_to_xml(segments)

    def _detect_message_type(self, segments: List[Dict]) -> str:
        """检测消息类型"""
        for segment in segments:
            tag = segment.get("tag")
            if tag == "UNH":
                # 消息头
                if segment["elements"]:
                    msg_type_elem = segment["elements"][0]
                    if msg_type_elem.get("type") == "composite":
                        msg_type = msg_type_elem["components"][0] if msg_type_elem["components"] else ""
                        return msg_type
        return "UNKNOWN"

    def _convert_iftmin_to_xml(self, data: Dict) -> str:
        """转换IFTMIN到XML"""
        root = Element("CargoManifest")
        root.set("xmlns", "http://maritime.schema.org/1.0")

        # 消息参考
        if "message_reference" in data:
            ref_elem = SubElement(root, "MessageReference")
            ref_elem.text = data["message_reference"]

        # 文档日期
        if "document_date" in data:
            date_elem = SubElement(root, "DocumentDate")
            date_elem.text = data["document_date"]

        # 船舶信息
        if "vessel_name" in data:
            vessel_elem = SubElement(root, "Vessel")
            vessel_name_elem = SubElement(vessel_elem, "VesselName")
            vessel_name_elem.text = data["vessel_name"]

        # 港口信息
        ports_elem = SubElement(root, "Ports")
        if "loading_port" in data:
            loading_port_elem = SubElement(ports_elem, "LoadingPort")
            loading_port_elem.set("code", data.get("loading_port_code", ""))
            loading_port_elem.text = data["loading_port"]

        if "discharge_port" in data:
            discharge_port_elem = SubElement(ports_elem, "DischargePort")
            discharge_port_elem.set("code", data.get("discharge_port_code", ""))
            discharge_port_elem.text = data["discharge_port"]

        # 货物列表
        if "cargoes" in data:
            cargoes_elem = SubElement(root, "Cargoes")
            for cargo in data["cargoes"]:
                cargo_elem = SubElement(cargoes_elem, "Cargo")
                if "cargo_name" in cargo:
                    name_elem = SubElement(cargo_elem, "CargoName")
                    name_elem.text = cargo["cargo_name"]
                if "weight" in cargo:
                    weight_elem = SubElement(cargo_elem, "Weight")
                    weight_elem.text = str(cargo["weight"])

        return tostring(root, encoding='unicode')

    def _convert_iftmcs_to_xml(self, data: Dict) -> str:
        """转换IFTMCS到XML"""
        root = Element("CargoStatus")
        root.set("xmlns", "http://maritime.schema.org/1.0")

        if "message_reference" in data:
            ref_elem = SubElement(root, "MessageReference")
            ref_elem.text = data["message_reference"]

        if "status_updates" in data:
            updates_elem = SubElement(root, "StatusUpdates")
            for update in data["status_updates"]:
                update_elem = SubElement(updates_elem, "StatusUpdate")

                if "cargo_id" in update:
                    cargo_id_elem = SubElement(update_elem, "CargoId")
                    cargo_id_elem.text = update["cargo_id"]

                if "status" in update:
                    status_elem = SubElement(update_elem, "Status")
                    status_elem.text = update["status"]

                if "event_time" in update:
                    time_elem = SubElement(update_elem, "EventTime")
                    time_elem.text = update["event_time"]

                if "event_location" in update:
                    location_elem = SubElement(update_elem, "EventLocation")
                    location_elem.text = update["event_location"]

        return tostring(root, encoding='unicode')

    def _convert_iftman_to_xml(self, data: Dict) -> str:
        """转换IFTMAN到XML"""
        root = Element("ArrivalNotice")
        root.set("xmlns", "http://maritime.schema.org/1.0")

        if "message_reference" in data:
            ref_elem = SubElement(root, "MessageReference")
            ref_elem.text = data["message_reference"]

        if "arrival_info" in data:
            arrival_elem = SubElement(root, "ArrivalInfo")
            info = data["arrival_info"]

            if "vessel_name" in info:
                vessel_elem = SubElement(arrival_elem, "VesselName")
                vessel_elem.text = info["vessel_name"]

            if "port_name" in info:
                port_elem = SubElement(arrival_elem, "Port")
                port_elem.set("code", info.get("port_code", ""))
                port_elem.text = info["port_name"]

            if "eta" in info:
                eta_elem = SubElement(arrival_elem, "ETA")
                eta_elem.text = info["eta"]

            if "ata" in info:
                ata_elem = SubElement(arrival_elem, "ATA")
                ata_elem.text = info["ata"]

        return tostring(root, encoding='unicode')

    def _convert_segments_to_xml(self, segments: List[Dict]) -> str:
        """通用段到XML转换"""
        root = Element("EDIFACTMessage")
        root.set("xmlns", "http://maritime.schema.org/1.0")

        for segment in segments:
            seg_elem = SubElement(root, "Segment")
            seg_elem.set("tag", segment.get("tag", ""))

            elements_elem = SubElement(seg_elem, "Elements")
            for element in segment.get("elements", []):
                elem_elem = SubElement(elements_elem, "Element")
                if element.get("type") == "composite":
                    elem_elem.set("type", "composite")
                    components_elem = SubElement(elem_elem, "Components")
                    for component in element.get("components", []):
                        comp_elem = SubElement(components_elem, "Component")
                        comp_elem.text = component
                else:
                    elem_elem.set("type", "simple")
                    elem_elem.text = element.get("value", "")

        return tostring(root, encoding='unicode')
```

---

## 3. XML到EDIFACT转换

**转换规则**：

- XML CargoManifest → EDIFACT IFTMIN
- XML CargoStatus → EDIFACT IFTMCS
- XML ArrivalNotice → EDIFACT IFTMAN

**完整转换实现**：

```python
from xml.etree.ElementTree import parse, ElementTree
from typing import Dict, List

class XMLToEDIFACTConverter:
    """XML到EDIFACT转换器"""

    def __init__(self):
        self.segment_terminator = "'"
        self.element_separator = "+"
        self.component_separator = ":"

    def convert_from_xml(self, xml_file_path: str) -> str:
        """将XML文档转换为EDIFACT消息"""
        tree = parse(xml_file_path)
        root = tree.getroot()

        # 检测消息类型
        message_type = self._detect_xml_message_type(root)

        if message_type == "CargoManifest":
            return self._convert_cargo_manifest_to_iftmin(root)
        elif message_type == "CargoStatus":
            return self._convert_cargo_status_to_iftmcs(root)
        elif message_type == "ArrivalNotice":
            return self._convert_arrival_notice_to_iftman(root)
        else:
            return self._convert_generic_xml_to_edifact(root)

    def _detect_xml_message_type(self, root) -> str:
        """检测XML消息类型"""
        tag = root.tag
        if "CargoManifest" in tag:
            return "CargoManifest"
        elif "CargoStatus" in tag:
            return "CargoStatus"
        elif "ArrivalNotice" in tag:
            return "ArrivalNotice"
        return "Unknown"

    def _convert_cargo_manifest_to_iftmin(self, root) -> str:
        """转换CargoManifest到IFTMIN"""
        segments = []

        # UNH - 消息头
        segments.append(f"UNH+1+IFTMIN:D:96A:UN")

        # BGM - 消息开始
        message_ref = root.find(".//MessageReference")
        if message_ref is not None and message_ref.text:
            segments.append(f"BGM+270+{message_ref.text}+9")

        # DTM - 文档日期
        doc_date = root.find(".//DocumentDate")
        if doc_date is not None and doc_date.text:
            edifact_date = self._convert_date_to_edifact(doc_date.text)
            segments.append(f"DTM+137:{edifact_date}:102")

        # TDT - 运输详情
        vessel_name = root.find(".//VesselName")
        if vessel_name is not None and vessel_name.text:
            segments.append(f"TDT+20+1+13+{vessel_name.text}::172")

        # LOC - 装货港
        loading_port = root.find(".//LoadingPort")
        if loading_port is not None:
            port_code = loading_port.get("code", "")
            port_name = loading_port.text or ""
            segments.append(f"LOC+5+{port_code}:172:6+{port_name}")

        # LOC - 卸货港
        discharge_port = root.find(".//DischargePort")
        if discharge_port is not None:
            port_code = discharge_port.get("code", "")
            port_name = discharge_port.text or ""
            segments.append(f"LOC+8+{port_code}:172:6+{port_name}")

        # GID - 货物描述
        cargoes = root.findall(".//Cargo")
        for cargo in cargoes:
            cargo_name = cargo.find("CargoName")
            if cargo_name is not None and cargo_name.text:
                segments.append(f"GID+1+{cargo_name.text}")

            weight = cargo.find("Weight")
            if weight is not None and weight.text:
                segments.append(f"MEA+WT+{weight.text}:KGM")

        # UNT - 消息尾
        segments.append(f"UNT+{len(segments)}+1")

        return self._format_edifact_message(segments)

    def _convert_cargo_status_to_iftmcs(self, root) -> str:
        """转换CargoStatus到IFTMCS"""
        segments = []

        # UNH - 消息头
        segments.append(f"UNH+1+IFTMCS:D:96A:UN")

        # BGM - 消息开始
        message_ref = root.find(".//MessageReference")
        if message_ref is not None and message_ref.text:
            segments.append(f"BGM+270+{message_ref.text}+9")

        # 状态更新
        status_updates = root.findall(".//StatusUpdate")
        for update in status_updates:
            # RFF - 参考
            cargo_id = update.find("CargoId")
            if cargo_id is not None and cargo_id.text:
                segments.append(f"RFF+BM:{cargo_id.text}")

            # STS - 状态
            status = update.find("Status")
            if status is not None and status.text:
                segments.append(f"STS+1+{status.text}")

            # DTM - 事件时间
            event_time = update.find("EventTime")
            if event_time is not None and event_time.text:
                edifact_date = self._convert_date_to_edifact(event_time.text)
                segments.append(f"DTM+137:{edifact_date}:102")

            # LOC - 事件地点
            event_location = update.find("EventLocation")
            if event_location is not None and event_location.text:
                segments.append(f"LOC+11+{event_location.text}")

        # UNT - 消息尾
        segments.append(f"UNT+{len(segments)}+1")

        return self._format_edifact_message(segments)

    def _convert_arrival_notice_to_iftman(self, root) -> str:
        """转换ArrivalNotice到IFTMAN"""
        segments = []

        # UNH - 消息头
        segments.append(f"UNH+1+IFTMAN:D:96A:UN")

        # BGM - 消息开始
        message_ref = root.find(".//MessageReference")
        if message_ref is not None and message_ref.text:
            segments.append(f"BGM+270+{message_ref.text}+9")

        # TDT - 运输详情
        vessel_name = root.find(".//VesselName")
        if vessel_name is not None and vessel_name.text:
            segments.append(f"TDT+20+1+13+{vessel_name.text}::172")

        # LOC - 到达港
        port = root.find(".//Port")
        if port is not None:
            port_code = port.get("code", "")
            port_name = port.text or ""
            segments.append(f"LOC+8+{port_code}:172:6+{port_name}")

        # DTM - ETA
        eta = root.find(".//ETA")
        if eta is not None and eta.text:
            edifact_date = self._convert_date_to_edifact(eta.text)
            segments.append(f"DTM+132:{edifact_date}:102")

        # DTM - ATA
        ata = root.find(".//ATA")
        if ata is not None and ata.text:
            edifact_date = self._convert_date_to_edifact(ata.text)
            segments.append(f"DTM+133:{edifact_date}:102")

        # UNT - 消息尾
        segments.append(f"UNT+{len(segments)}+1")

        return self._format_edifact_message(segments)

    def _convert_generic_xml_to_edifact(self, root) -> str:
        """通用XML到EDIFACT转换"""
        segments = []

        for segment_elem in root.findall(".//Segment"):
            tag = segment_elem.get("tag", "")
            segment_str = tag

            elements_elem = segment_elem.find("Elements")
            if elements_elem is not None:
                for element_elem in elements_elem.findall("Element"):
                    if element_elem.get("type") == "composite":
                        components = element_elem.find("Components")
                        if components is not None:
                            comp_values = [comp.text or "" for comp in components.findall("Component")]
                            segment_str += self.element_separator + self.component_separator.join(comp_values)
                    else:
                        value = element_elem.text or ""
                        segment_str += self.element_separator + value

            segments.append(segment_str)

        return self._format_edifact_message(segments)

    def _convert_date_to_edifact(self, date_str: str) -> str:
        """转换日期到EDIFACT格式"""
        # ISO格式：YYYY-MM-DD或YYYY-MM-DDTHH:MM:SSZ
        # EDIFACT格式：YYYYMMDD或YYYYMMDDHHMM
        date_str = date_str.replace("T", " ").replace("Z", "").strip()

        if len(date_str) >= 10:
            # YYYY-MM-DD
            date_part = date_str[:10].replace("-", "")
            if len(date_str) > 10:
                # 包含时间
                time_part = date_str[11:16].replace(":", "")
                return date_part + time_part
            return date_part

        return date_str

    def _format_edifact_message(self, segments: List[str]) -> str:
        """格式化EDIFACT消息"""
        return "\n".join([seg + self.segment_terminator for seg in segments])
```

---

## 4. 船舶位置追踪系统

### 4.1 AIS数据集成

**船舶位置追踪实现**：

```python
import logging
from typing import Dict, List, Optional
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class AISMessageParser:
    """AIS消息解析器"""

    def __init__(self):
        self.message_types = {
            1: "Position Report Class A",
            2: "Position Report Class A",
            3: "Position Report Class A",
            4: "Base Station Report",
            5: "Static and Voyage Related Data",
            18: "Standard Class B Position Report",
            19: "Extended Class B Position Report",
            21: "Aids-to-Navigation Report",
            24: "Static Data Report"
        }

    def parse_ais_message(self, ais_message: str) -> Dict:
        """解析AIS消息（NMEA格式）"""
        # AIS消息格式：!AIVDM,1,1,,A,133m@ogP00PD;88MD5MTDww@2D7k,0*46
        parts = ais_message.split(',')

        if len(parts) < 6:
            raise ValueError("Invalid AIS message format")

        message_type = parts[0]  # !AIVDM or !AIVDO
        fragment_count = int(parts[1]) if parts[1] else 1
        fragment_number = int(parts[2]) if parts[2] else 1
        message_id = parts[3] if parts[3] else ""
        channel = parts[4]  # A or B
        payload = parts[5]  # 6-bit encoded data
        fill_bits = int(parts[6]) if len(parts) > 6 and parts[6] else 0

        # 解码6-bit编码的payload
        decoded_data = self._decode_6bit(payload, fill_bits)

        # 解析消息类型
        message_type_id = decoded_data[0] & 0x3F

        parsed_message = {
            "message_type": message_type_id,
            "message_type_name": self.message_types.get(message_type_id, "Unknown"),
            "mmsi": self._extract_mmsi(decoded_data),
            "timestamp": datetime.now()
        }

        # 根据消息类型解析
        if message_type_id in [1, 2, 3]:
            parsed_message.update(self._parse_position_report(decoded_data))
        elif message_type_id == 5:
            parsed_message.update(self._parse_static_voyage_data(decoded_data))
        elif message_type_id == 18:
            parsed_message.update(self._parse_class_b_position(decoded_data))
        elif message_type_id == 19:
            parsed_message.update(self._parse_extended_class_b_position(decoded_data))

        return parsed_message

    def _decode_6bit(self, payload: str, fill_bits: int) -> List[int]:
        """解码6-bit编码的AIS数据"""
        decoded = []
        bit_string = ""

        # 将ASCII字符转换为6位二进制
        for char in payload:
            ascii_val = ord(char)
            if ascii_val < 48 or ascii_val > 119:
                continue
            # 转换为6位值
            bit_val = ascii_val - 48
            if bit_val > 40:
                bit_val -= 8
            bit_string += format(bit_val, '06b')

        # 移除填充位
        if fill_bits > 0:
            bit_string = bit_string[:-fill_bits]

        # 转换为字节数组
        for i in range(0, len(bit_string), 8):
            byte_str = bit_string[i:i+8]
            if len(byte_str) == 8:
                decoded.append(int(byte_str, 2))

        return decoded

    def _extract_mmsi(self, data: List[int]) -> str:
        """提取MMSI"""
        if len(data) < 3:
            return ""

        mmsi = ((data[0] & 0x3F) << 20) | (data[1] << 14) | (data[2] << 8) | data[3]
        return str(mmsi & 0xFFFFFFFF)

    def _parse_position_report(self, data: List[int]) -> Dict:
        """解析位置报告（消息类型1, 2, 3）"""
        position_data = {}

        if len(data) < 20:
            return position_data

        # 解析位置（简化实现）
        # 实际实现需要更复杂的位操作
        # 这里提供框架

        return {
            "latitude": 0.0,  # 需要从data中提取
            "longitude": 0.0,  # 需要从data中提取
            "course_over_ground": 0.0,
            "speed_over_ground": 0.0,
            "heading": 0,
            "navigation_status": 0
        }

    def _parse_static_voyage_data(self, data: List[int]) -> Dict:
        """解析静态和航次数据（消息类型5）"""
        static_data = {}

        if len(data) < 30:
            return static_data

        # 解析船舶信息
        # 实际实现需要更复杂的位操作

        return {
            "imo_number": "",
            "call_sign": "",
            "vessel_name": "",
            "vessel_type": 0,
            "dimension_to_bow": 0,
            "dimension_to_stern": 0,
            "dimension_to_port": 0,
            "dimension_to_starboard": 0,
            "eta_month": 0,
            "eta_day": 0,
            "eta_hour": 0,
            "eta_minute": 0,
            "draught": 0.0,
            "destination": ""
        }

    def _parse_class_b_position(self, data: List[int]) -> Dict:
        """解析Class B位置报告（消息类型18）"""
        return self._parse_position_report(data)

    def _parse_extended_class_b_position(self, data: List[int]) -> Dict:
        """解析扩展Class B位置报告（消息类型19）"""
        position_data = self._parse_position_report(data)
        # 添加额外字段
        position_data.update({
            "vessel_name": "",
            "vessel_type": 0
        })
        return position_data

class VesselPositionTracker:
    """船舶位置追踪器 - 完整实现"""

    def __init__(self, storage):
        self.storage = storage
        self.ais_parser = AISMessageParser()
        self.vessel_positions: Dict[str, List[Dict]] = {}

    def process_ais_message(self, ais_message: str):
        """处理AIS消息"""
        try:
            parsed = self.ais_parser.parse_ais_message(ais_message)
            mmsi = parsed.get("mmsi")

            if not mmsi:
                logger.warning("AIS message missing MMSI")
                return

            # 查找对应的vessel_id
            vessel_id = self.storage.get_vessel_by_mmsi(mmsi)
            if not vessel_id:
                logger.warning(f"Vessel not found for MMSI: {mmsi}")
                return

            # 更新位置
            if "latitude" in parsed and "longitude" in parsed:
                position_data = {
                    "vessel_id": vessel_id,
                    "latitude": parsed["latitude"],
                    "longitude": parsed["longitude"],
                    "course": parsed.get("course_over_ground"),
                    "speed": parsed.get("speed_over_ground"),
                    "heading": parsed.get("heading"),
                    "navigation_status": parsed.get("navigation_status"),
                    "position_time": parsed.get("timestamp", datetime.now())
                }
                self.update_position(vessel_id, position_data)

            # 更新船舶状态
            if parsed.get("message_type") == 5:
                self._update_vessel_static_data(vessel_id, parsed)

        except Exception as e:
            logger.error(f"Failed to process AIS message: {e}")

    def _update_vessel_static_data(self, vessel_id: str, static_data: Dict):
        """更新船舶静态数据"""
        update_data = {}

        if "imo_number" in static_data:
            update_data["imo_number"] = static_data["imo_number"]
        if "call_sign" in static_data:
            update_data["call_sign"] = static_data["call_sign"]
        if "vessel_name" in static_data:
            update_data["vessel_name"] = static_data["vessel_name"]
        if "vessel_type" in static_data:
            update_data["vessel_type"] = static_data["vessel_type"]

        if update_data:
            self.storage.update_vessel_info(vessel_id, update_data)

    def update_position(self, vessel_id: str, position_data: Dict):
        """更新船舶位置 - 完整实现"""
        position_record = {
            "vessel_id": vessel_id,
            "latitude": position_data.get("latitude"),
            "longitude": position_data.get("longitude"),
            "course": position_data.get("course"),
            "speed": position_data.get("speed"),
            "heading": position_data.get("heading"),
            "navigation_status": position_data.get("navigation_status"),
            "position_time": position_data.get("position_time", datetime.now())
        }

        # 存储到数据库
        self.storage.store_vessel_position(position_record)

        # 更新内存缓存
        if vessel_id not in self.vessel_positions:
            self.vessel_positions[vessel_id] = []
        self.vessel_positions[vessel_id].append(position_record)

        # 保持最近100条记录
        if len(self.vessel_positions[vessel_id]) > 100:
            self.vessel_positions[vessel_id] = self.vessel_positions[vessel_id][-100:]

        logger.info(f"Updated position for vessel {vessel_id}")

    def get_current_position(self, vessel_id: str) -> Optional[Dict]:
        """获取当前位置"""
        positions = self.vessel_positions.get(vessel_id, [])
        if positions:
            return positions[-1]

        # 从数据库查询
        return self.storage.get_latest_vessel_position(vessel_id)

    def calculate_distance(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """计算两点间距离（海里） - 完整实现"""
        # 使用Haversine公式
        R = 3440.0  # 地球半径（海里）

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def calculate_bearing(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """计算方位角（度）"""
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)

        y = math.sin(dlon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
            math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)

        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360

        return bearing

    def estimate_arrival_time(self, vessel_id: str, destination_lat: float,
                             destination_lon: float) -> Optional[datetime]:
        """估算到达时间 - 完整实现"""
        current_pos = self.get_current_position(vessel_id)
        if not current_pos:
            return None

        # 计算距离
        distance = self.calculate_distance(
            current_pos["latitude"],
            current_pos["longitude"],
            destination_lat,
            destination_lon
        )

        # 获取当前速度
        speed = current_pos.get("speed", 0)
        if speed <= 0:
            return None

        # 计算时间（小时）
        hours = distance / speed

        # 估算到达时间
        arrival_time = current_pos["position_time"]
        if isinstance(arrival_time, str):
            arrival_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))

        from datetime import timedelta
        return arrival_time + timedelta(hours=hours)

    def get_vessel_track(self, vessel_id: str, hours: int = 24) -> List[Dict]:
        """获取船舶轨迹"""
        return self.storage.get_vessel_positions(vessel_id, hours)

    def get_vessels_in_area(self, min_lat: float, max_lat: float,
                           min_lon: float, max_lon: float) -> List[Dict]:
        """获取区域内的船舶"""
        return self.storage.get_vessels_in_area(min_lat, max_lat, min_lon, max_lon)

    def get_vessel_speed_history(self, vessel_id: str, hours: int = 24) -> List[Dict]:
        """获取船舶速度历史"""
        positions = self.get_vessel_track(vessel_id, hours)
        return [
            {
                "position_time": pos["position_time"],
                "speed": pos.get("speed", 0),
                "latitude": pos["latitude"],
                "longitude": pos["longitude"]
            }
            for pos in positions
        ]

class RouteOptimizer:
    """航线优化器"""

    def __init__(self, storage, position_tracker: VesselPositionTracker):
        self.storage = storage
        self.position_tracker = position_tracker

    def optimize_route_shortest_path(self, origin_lat: float, origin_lon: float,
                                     destination_lat: float, destination_lon: float,
                                     waypoints: List[Dict] = None) -> Dict:
        """最短路径优化"""
        # 使用Dijkstra算法或A*算法
        # 简化实现：直接计算大圆航线

        if waypoints:
            # 有中间点，计算分段路径
            total_distance = 0.0
            route_segments = []

            current_lat, current_lon = origin_lat, origin_lon

            for waypoint in waypoints:
                wp_lat = waypoint.get("latitude")
                wp_lon = waypoint.get("longitude")

                segment_distance = self.position_tracker.calculate_distance(
                    current_lat, current_lon, wp_lat, wp_lon
                )
                total_distance += segment_distance

                route_segments.append({
                    "from": {"latitude": current_lat, "longitude": current_lon},
                    "to": {"latitude": wp_lat, "longitude": wp_lon},
                    "distance": segment_distance
                })

                current_lat, current_lon = wp_lat, wp_lon

            # 最后一段到目的地
            final_distance = self.position_tracker.calculate_distance(
                current_lat, current_lon, destination_lat, destination_lon
            )
            total_distance += final_distance

            route_segments.append({
                "from": {"latitude": current_lat, "longitude": current_lon},
                "to": {"latitude": destination_lat, "longitude": destination_lon},
                "distance": final_distance
            })
        else:
            # 无中间点，直接计算大圆航线
            total_distance = self.position_tracker.calculate_distance(
                origin_lat, origin_lon, destination_lat, destination_lon
            )

            route_segments = [{
                "from": {"latitude": origin_lat, "longitude": origin_lon},
                "to": {"latitude": destination_lat, "longitude": destination_lon},
                "distance": total_distance
            }]

        return {
            "optimization_type": "shortest_path",
            "total_distance": total_distance,
            "route_segments": route_segments,
            "waypoints": waypoints or []
        }

    def optimize_route_cost(self, origin_lat: float, origin_lon: float,
                           destination_lat: float, destination_lon: float,
                           vessel_id: str, fuel_price_per_ton: float = 500.0,
                           port_costs: Dict[str, float] = None) -> Dict:
        """成本优化"""
        # 获取船舶信息
        vessel = self.storage.get_vessel(vessel_id)
        if not vessel:
            raise ValueError(f"Vessel not found: {vessel_id}")

        # 计算距离
        distance = self.position_tracker.calculate_distance(
            origin_lat, origin_lon, destination_lat, destination_lon
        )

        # 估算燃油消耗（简化：假设每海里消耗固定吨数）
        fuel_consumption_rate = 0.05  # 吨/海里（示例值）
        fuel_consumption = distance * fuel_consumption_rate

        # 计算燃油成本
        fuel_cost = fuel_consumption * fuel_price_per_ton

        # 计算港口成本
        port_cost = 0.0
        if port_costs:
            # 假设有装货港和卸货港成本
            port_cost = port_costs.get("loading", 0) + port_costs.get("discharge", 0)

        # 计算总成本
        total_cost = fuel_cost + port_cost

        # 估算航行时间
        average_speed = 15.0  # 节（示例值）
        estimated_hours = distance / average_speed

        return {
            "optimization_type": "cost",
            "total_distance": distance,
            "fuel_consumption": fuel_consumption,
            "fuel_cost": fuel_cost,
            "port_cost": port_cost,
            "total_cost": total_cost,
            "estimated_hours": estimated_hours,
            "average_speed": average_speed
        }

    def optimize_route_time(self, origin_lat: float, origin_lon: float,
                           destination_lat: float, destination_lon: float,
                           vessel_id: str, max_speed: float = 20.0,
                           weather_data: Dict = None) -> Dict:
        """时间优化"""
        # 计算距离
        distance = self.position_tracker.calculate_distance(
            origin_lat, origin_lon, destination_lat, destination_lon
        )

        # 考虑天气因素调整速度
        effective_speed = max_speed
        if weather_data:
            # 根据风速和风向调整速度
            wind_speed = weather_data.get("wind_speed", 0)
            wind_direction = weather_data.get("wind_direction", 0)

            # 简化：逆风减速，顺风加速
            if wind_speed > 20:  # 强风
                effective_speed = max_speed * 0.8
            elif wind_speed > 10:  # 中风
                effective_speed = max_speed * 0.9

        # 计算最短时间
        estimated_hours = distance / effective_speed if effective_speed > 0 else float('inf')

        # 计算燃油消耗
        fuel_consumption_rate = 0.05  # 吨/海里
        fuel_consumption = distance * fuel_consumption_rate

        return {
            "optimization_type": "time",
            "total_distance": distance,
            "max_speed": max_speed,
            "effective_speed": effective_speed,
            "estimated_hours": estimated_hours,
            "fuel_consumption": fuel_consumption,
            "weather_impact": weather_data is not None
        }

    def optimize_route_multi_objective(self, origin_lat: float, origin_lon: float,
                                       destination_lat: float, destination_lon: float,
                                       vessel_id: str, weights: Dict[str, float] = None) -> Dict:
        """多目标优化（成本+时间）"""
        if weights is None:
            weights = {"cost": 0.5, "time": 0.5}

        # 计算成本优化
        cost_result = self.optimize_route_cost(
            origin_lat, origin_lon, destination_lat, destination_lon, vessel_id
        )

        # 计算时间优化
        time_result = self.optimize_route_time(
            origin_lat, origin_lon, destination_lat, destination_lon, vessel_id
        )

        # 归一化成本和时间（简化）
        # 假设成本范围0-100000，时间范围0-1000小时
        normalized_cost = min(cost_result["total_cost"] / 100000.0, 1.0)
        normalized_time = min(time_result["estimated_hours"] / 1000.0, 1.0)

        # 计算综合得分（越小越好）
        combined_score = weights["cost"] * normalized_cost + weights["time"] * normalized_time

        return {
            "optimization_type": "multi_objective",
            "total_distance": cost_result["total_distance"],
            "cost_optimization": cost_result,
            "time_optimization": time_result,
            "combined_score": combined_score,
            "weights": weights,
            "recommended_speed": time_result["effective_speed"],
            "estimated_cost": cost_result["total_cost"],
            "estimated_hours": time_result["estimated_hours"]
        }

    def find_optimal_waypoints(self, origin_lat: float, origin_lon: float,
                             destination_lat: float, destination_lon: float,
                             available_ports: List[Dict]) -> List[Dict]:
        """寻找最优中间港口"""
        if not available_ports:
            return []

        # 使用贪心算法选择中间港口
        optimal_waypoints = []
        current_lat, current_lon = origin_lat, origin_lon

        remaining_ports = available_ports.copy()

        while remaining_ports:
            best_port = None
            best_distance = float('inf')

            for port in remaining_ports:
                port_lat = port.get("latitude")
                port_lon = port.get("longitude")

                # 计算到当前点的距离
                distance_to_port = self.position_tracker.calculate_distance(
                    current_lat, current_lon, port_lat, port_lon
                )

                # 计算从港口到目的地的距离
                distance_to_dest = self.position_tracker.calculate_distance(
                    port_lat, port_lon, destination_lat, destination_lon
                )

                # 总距离
                total_distance = distance_to_port + distance_to_dest

                # 检查是否比直接到目的地更近
                direct_distance = self.position_tracker.calculate_distance(
                    current_lat, current_lon, destination_lat, destination_lon
                )

                if total_distance < direct_distance and distance_to_port < best_distance:
                    best_port = port
                    best_distance = distance_to_port

            if best_port:
                optimal_waypoints.append(best_port)
                current_lat = best_port.get("latitude")
                current_lon = best_port.get("longitude")
                remaining_ports.remove(best_port)
            else:
                break

        return optimal_waypoints

### 4.2 货物追踪系统

**货物追踪实现**：

```python
class CargoTrackingSystem:
    """货物追踪系统"""

    def __init__(self, storage):
        self.storage = storage

    def track_cargo_event(self, cargo_id: str, event_type: str,
                         event_location: str, event_description: str = ""):
        """记录货物事件"""
        event_record = {
            "cargo_id": cargo_id,
            "event_type": event_type,
            "event_time": datetime.now(),
            "event_location": event_location,
            "event_description": event_description
        }

        self.storage.store_cargo_tracking_event(event_record)

        # 更新货物状态
        status_map = {
            "Booked": "Booked",
            "Loaded": "InTransit",
            "Departed": "InTransit",
            "Arrived": "Arrived",
            "Discharged": "Delivered"
        }

        if event_type in status_map:
            self.storage.update_cargo_status(cargo_id, status_map[event_type])

        logger.info(f"Tracked cargo event: {cargo_id} - {event_type}")

    def get_cargo_tracking_history(self, cargo_id: str) -> List[Dict]:
        """获取货物追踪历史"""
        return self.storage.get_cargo_tracking_events(cargo_id)

    def get_cargo_current_status(self, cargo_id: str) -> Optional[Dict]:
        """获取货物当前状态"""
        cargo = self.storage.get_cargo(cargo_id)
        if not cargo:
            return None

        latest_event = self.storage.get_latest_cargo_event(cargo_id)

        return {
            "cargo_id": cargo_id,
            "cargo_name": cargo.get("cargo_name"),
            "status": cargo.get("status"),
            "current_location": latest_event.get("event_location") if latest_event else None,
            "last_update": latest_event.get("event_time") if latest_event else None
        }
```

---

## 5. 转换工具

### 5.1 EDIFACT解析器集成

详见第2.1节EDIFACTParser实现。

### 5.2 XML转换器集成

详见第3节XMLToEDIFACTConverter实现。

---

## 6. 转换验证

### 6.1 EDIFACT消息验证

**转换验证器实现**：

```python
class EDIFACTConversionValidator:
    """EDIFACT转换验证器"""

    def validate_edifact_to_xml(self, edifact_message: str, xml_output: str) -> bool:
        """验证EDIFACT到XML转换"""
        parser = EDIFACTParser()
        segments = parser.parse_message(edifact_message)

        if not segments:
            return False

        # 检查XML是否包含必要的元素
        from xml.etree.ElementTree import fromstring
        try:
            xml_root = fromstring(xml_output)
            # 验证XML结构
            return xml_root is not None
        except Exception:
            return False

    def validate_xml_to_edifact(self, xml_input: str, edifact_output: str) -> bool:
        """验证XML到EDIFACT转换"""
        # 检查EDIFACT消息格式
        if not edifact_output.strip():
            return False

        # 检查是否包含段终止符
        if "'" not in edifact_output:
            return False

        # 检查是否包含必要的段
        if "UNH" not in edifact_output:
            return False

        if "UNT" not in edifact_output:
            return False

        return True
```

---

## 7. 海运航运数据存储与分析

### 7.1 PostgreSQL海运航运数据存储

**海运航运数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class MaritimeStorage:
    """海运航运数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建海运航运数据表"""
        # 船舶表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vessels (
                id BIGSERIAL PRIMARY KEY,
                vessel_id VARCHAR(10) UNIQUE NOT NULL,
                imo_number VARCHAR(7) UNIQUE NOT NULL,
                vessel_name VARCHAR(200) NOT NULL,
                vessel_type VARCHAR(50) NOT NULL,
                flag_state VARCHAR(2) NOT NULL,
                call_sign VARCHAR(10),
                mmsi VARCHAR(9),
                gross_tonnage DECIMAL(10,2),
                net_tonnage DECIMAL(10,2),
                deadweight_tonnage DECIMAL(10,2),
                length_overall DECIMAL(8,2),
                breadth DECIMAL(8,2),
                draft DECIMAL(6,2),
                year_built INTEGER,
                builder VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 船舶位置表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vessel_positions (
                id BIGSERIAL PRIMARY KEY,
                vessel_id VARCHAR(10) NOT NULL,
                latitude DECIMAL(8,6) NOT NULL,
                longitude DECIMAL(9,6) NOT NULL,
                course DECIMAL(5,2),
                speed DECIMAL(5,2),
                heading DECIMAL(5,2),
                position_time TIMESTAMP NOT NULL,
                FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
            )
        """)

        # 货物表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS cargoes (
                id BIGSERIAL PRIMARY KEY,
                cargo_id VARCHAR(20) UNIQUE NOT NULL,
                cargo_name VARCHAR(200) NOT NULL,
                cargo_type VARCHAR(50) NOT NULL,
                shipper VARCHAR(200) NOT NULL,
                consignee VARCHAR(200) NOT NULL,
                weight DECIMAL(10,2) NOT NULL,
                volume DECIMAL(10,2),
                quantity INTEGER,
                unit VARCHAR(20),
                hs_code VARCHAR(10),
                value DECIMAL(12,2),
                currency VARCHAR(3) DEFAULT 'USD',
                status VARCHAR(20) NOT NULL,
                loading_port VARCHAR(100),
                loading_port_code VARCHAR(5),
                discharge_port VARCHAR(100),
                discharge_port_code VARCHAR(5),
                loading_date TIMESTAMP,
                discharge_date TIMESTAMP,
                vessel_id VARCHAR(10),
                container_number VARCHAR(11),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
            )
        """)

        # 货物追踪表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS cargo_tracking (
                id BIGSERIAL PRIMARY KEY,
                cargo_id VARCHAR(20) NOT NULL,
                event_type VARCHAR(20) NOT NULL,
                event_time TIMESTAMP NOT NULL,
                event_location VARCHAR(200),
                event_description VARCHAR(500),
                FOREIGN KEY (cargo_id) REFERENCES cargoes(cargo_id)
            )
        """)

        # 航线表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id BIGSERIAL PRIMARY KEY,
                route_id VARCHAR(20) UNIQUE NOT NULL,
                vessel_id VARCHAR(10) NOT NULL,
                voyage_number VARCHAR(20) NOT NULL,
                origin_port VARCHAR(100) NOT NULL,
                origin_port_code VARCHAR(5) NOT NULL,
                destination_port VARCHAR(100) NOT NULL,
                destination_port_code VARCHAR(5) NOT NULL,
                planned_departure TIMESTAMP NOT NULL,
                planned_arrival TIMESTAMP NOT NULL,
                planned_distance DECIMAL(10,2),
                planned_duration INTEGER,
                actual_departure TIMESTAMP,
                actual_arrival TIMESTAMP,
                actual_distance DECIMAL(10,2),
                actual_duration INTEGER,
                average_speed DECIMAL(5,2),
                fuel_consumption DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
            )
        """)

        # AIS数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS ais_data (
                id BIGSERIAL PRIMARY KEY,
                mmsi VARCHAR(9) NOT NULL,
                message_type INTEGER NOT NULL,
                message_type_name VARCHAR(50),
                latitude DECIMAL(8,6),
                longitude DECIMAL(9,6),
                course_over_ground DECIMAL(5,2),
                speed_over_ground DECIMAL(5,2),
                heading INTEGER,
                navigation_status INTEGER,
                imo_number VARCHAR(7),
                call_sign VARCHAR(10),
                vessel_name VARCHAR(200),
                vessel_type INTEGER,
                dimension_to_bow INTEGER,
                dimension_to_stern INTEGER,
                dimension_to_port INTEGER,
                dimension_to_starboard INTEGER,
                draught DECIMAL(4,2),
                destination VARCHAR(200),
                eta_month INTEGER,
                eta_day INTEGER,
                eta_hour INTEGER,
                eta_minute INTEGER,
                raw_message TEXT,
                received_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 航线优化表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS route_optimizations (
                id BIGSERIAL PRIMARY KEY,
                optimization_id VARCHAR(50) UNIQUE NOT NULL,
                route_id VARCHAR(20) NOT NULL,
                optimization_type VARCHAR(20) NOT NULL,
                origin_latitude DECIMAL(8,6) NOT NULL,
                origin_longitude DECIMAL(9,6) NOT NULL,
                destination_latitude DECIMAL(8,6) NOT NULL,
                destination_longitude DECIMAL(9,6) NOT NULL,
                total_distance DECIMAL(10,2),
                estimated_hours DECIMAL(8,2),
                fuel_consumption DECIMAL(10,2),
                fuel_cost DECIMAL(12,2),
                port_cost DECIMAL(12,2),
                total_cost DECIMAL(12,2),
                recommended_speed DECIMAL(5,2),
                waypoints JSONB,
                optimization_parameters JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(route_id)
            )
        """)

        # 港口效率表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS port_efficiency (
                id BIGSERIAL PRIMARY KEY,
                port_code VARCHAR(5) UNIQUE NOT NULL,
                port_name VARCHAR(100) NOT NULL,
                country_code VARCHAR(2),
                latitude DECIMAL(8,6),
                longitude DECIMAL(9,6),
                average_berth_time_hours DECIMAL(6,2),
                average_cargo_handling_rate DECIMAL(8,2),
                average_waiting_time_hours DECIMAL(6,2),
                total_vessels INTEGER DEFAULT 0,
                total_cargo_tonnage DECIMAL(12,2) DEFAULT 0,
                efficiency_score DECIMAL(5,2),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 港口操作记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS port_operations (
                id BIGSERIAL PRIMARY KEY,
                operation_id VARCHAR(50) UNIQUE NOT NULL,
                port_code VARCHAR(5) NOT NULL,
                vessel_id VARCHAR(10) NOT NULL,
                operation_type VARCHAR(20) NOT NULL,
                operation_start TIMESTAMP NOT NULL,
                operation_end TIMESTAMP,
                duration_hours DECIMAL(6,2),
                cargo_tonnage DECIMAL(10,2),
                berth_number VARCHAR(20),
                crane_count INTEGER,
                efficiency_rating DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (port_code) REFERENCES port_efficiency(port_code),
                FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
            )
        """)

        # 异常事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS maritime_events (
                id BIGSERIAL PRIMARY KEY,
                event_id VARCHAR(50) UNIQUE NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_severity VARCHAR(20) NOT NULL,
                vessel_id VARCHAR(10),
                route_id VARCHAR(20),
                cargo_id VARCHAR(20),
                event_location_latitude DECIMAL(8,6),
                event_location_longitude DECIMAL(9,6),
                event_description TEXT,
                event_time TIMESTAMP NOT NULL,
                resolved_time TIMESTAMP,
                resolution_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id),
                FOREIGN KEY (route_id) REFERENCES routes(route_id),
                FOREIGN KEY (cargo_id) REFERENCES cargoes(cargo_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_vessels_vessel_id
            ON vessels(vessel_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_vessels_imo_number
            ON vessels(imo_number)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_cargoes_cargo_id
            ON cargoes(cargo_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_vessel_positions_vessel_id
            ON vessel_positions(vessel_id, position_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_vessel_positions_location
            ON vessel_positions USING GIST (
                ll_to_earth(latitude, longitude)
            )
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ais_data_mmsi
            ON ais_data(mmsi, received_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ais_data_message_type
            ON ais_data(message_type, received_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ais_data_location
            ON ais_data(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_routes_vessel_id
            ON routes(vessel_id, planned_departure DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_routes_ports
            ON routes(origin_port_code, destination_port_code)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_route_optimizations_route_id
            ON route_optimizations(route_id, created_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_route_optimizations_type
            ON route_optimizations(optimization_type)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_port_efficiency_port_code
            ON port_efficiency(port_code)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_port_operations_port_code
            ON port_operations(port_code, operation_start DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_maritime_events_vessel_id
            ON maritime_events(vessel_id, event_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_maritime_events_type
            ON maritime_events(event_type, event_severity)
        """)

        self.conn.commit()

    def store_vessel(self, vessel_data: Dict) -> int:
        """存储船舶信息"""
        self.cur.execute("""
            INSERT INTO vessels (
                vessel_id, imo_number, vessel_name, vessel_type,
                flag_state, call_sign, mmsi, gross_tonnage,
                net_tonnage, deadweight_tonnage, length_overall,
                breadth, draft, year_built, builder
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (vessel_id) DO UPDATE SET
                vessel_name = EXCLUDED.vessel_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            vessel_data.get("vessel_id"),
            vessel_data.get("imo_number"),
            vessel_data.get("vessel_name"),
            vessel_data.get("vessel_type"),
            vessel_data.get("flag_state"),
            vessel_data.get("call_sign"),
            vessel_data.get("mmsi"),
            vessel_data.get("gross_tonnage"),
            vessel_data.get("net_tonnage"),
            vessel_data.get("deadweight_tonnage"),
            vessel_data.get("length_overall"),
            vessel_data.get("breadth"),
            vessel_data.get("draft"),
            vessel_data.get("year_built"),
            vessel_data.get("builder")
        ))
        return self.cur.fetchone()[0]

    def store_cargo(self, cargo_data: Dict) -> int:
        """存储货物信息"""
        self.cur.execute("""
            INSERT INTO cargoes (
                cargo_id, cargo_name, cargo_type, shipper, consignee,
                weight, volume, quantity, unit, hs_code, value, currency,
                status, loading_port, loading_port_code, discharge_port,
                discharge_port_code, loading_date, discharge_date,
                vessel_id, container_number
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cargo_id) DO UPDATE SET
                status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            cargo_data.get("cargo_id"),
            cargo_data.get("cargo_name"),
            cargo_data.get("cargo_type"),
            cargo_data.get("shipper"),
            cargo_data.get("consignee"),
            cargo_data.get("weight"),
            cargo_data.get("volume"),
            cargo_data.get("quantity"),
            cargo_data.get("unit"),
            cargo_data.get("hs_code"),
            cargo_data.get("value"),
            cargo_data.get("currency"),
            cargo_data.get("status"),
            cargo_data.get("loading_port"),
            cargo_data.get("loading_port_code"),
            cargo_data.get("discharge_port"),
            cargo_data.get("discharge_port_code"),
            cargo_data.get("loading_date"),
            cargo_data.get("discharge_date"),
            cargo_data.get("vessel_id"),
            cargo_data.get("container_number")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_vessel_position(self, position_data: Dict) -> int:
        """存储船舶位置"""
        self.cur.execute("""
            INSERT INTO vessel_positions (
                vessel_id, latitude, longitude, course, speed,
                heading, position_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            position_data.get("vessel_id"),
            position_data.get("latitude"),
            position_data.get("longitude"),
            position_data.get("course"),
            position_data.get("speed"),
            position_data.get("heading"),
            position_data.get("position_time")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_latest_vessel_position(self, vessel_id: str) -> Optional[Dict]:
        """获取最新船舶位置"""
        self.cur.execute("""
            SELECT latitude, longitude, course, speed, heading, position_time
            FROM vessel_positions
            WHERE vessel_id = %s
            ORDER BY position_time DESC
            LIMIT 1
        """, (vessel_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "vessel_id": vessel_id,
                "latitude": row[0],
                "longitude": row[1],
                "course": row[2],
                "speed": row[3],
                "heading": row[4],
                "position_time": row[5]
            }
        return None

    def get_vessel_positions(self, vessel_id: str, hours: int = 24) -> List[Dict]:
        """获取船舶位置历史"""
        self.cur.execute("""
            SELECT latitude, longitude, course, speed, heading, position_time
            FROM vessel_positions
            WHERE vessel_id = %s
            AND position_time >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
            ORDER BY position_time ASC
        """, (vessel_id, hours))
        return [
            {
                "vessel_id": vessel_id,
                "latitude": row[0],
                "longitude": row[1],
                "course": row[2],
                "speed": row[3],
                "heading": row[4],
                "position_time": row[5]
            }
            for row in self.cur.fetchall()
        ]

    def store_cargo_tracking_event(self, event_data: Dict) -> int:
        """存储货物追踪事件"""
        self.cur.execute("""
            INSERT INTO cargo_tracking (
                cargo_id, event_type, event_time, event_location, event_description
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            event_data.get("cargo_id"),
            event_data.get("event_type"),
            event_data.get("event_time"),
            event_data.get("event_location"),
            event_data.get("event_description")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_cargo_tracking_events(self, cargo_id: str) -> List[Dict]:
        """获取货物追踪事件"""
        self.cur.execute("""
            SELECT event_type, event_time, event_location, event_description
            FROM cargo_tracking
            WHERE cargo_id = %s
            ORDER BY event_time ASC
        """, (cargo_id,))
        return [
            {
                "event_type": row[0],
                "event_time": row[1],
                "event_location": row[2],
                "event_description": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def get_latest_cargo_event(self, cargo_id: str) -> Optional[Dict]:
        """获取最新货物事件"""
        self.cur.execute("""
            SELECT event_type, event_time, event_location, event_description
            FROM cargo_tracking
            WHERE cargo_id = %s
            ORDER BY event_time DESC
            LIMIT 1
        """, (cargo_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "event_type": row[0],
                "event_time": row[1],
                "event_location": row[2],
                "event_description": row[3]
            }
        return None

    def update_cargo_status(self, cargo_id: str, status: str):
        """更新货物状态"""
        self.cur.execute("""
            UPDATE cargoes
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE cargo_id = %s
        """, (status, cargo_id))
        self.conn.commit()

    def get_cargo(self, cargo_id: str) -> Optional[Dict]:
        """获取货物信息"""
        self.cur.execute("""
            SELECT cargo_id, cargo_name, cargo_type, shipper, consignee,
                   weight, volume, status, vessel_id
            FROM cargoes
            WHERE cargo_id = %s
        """, (cargo_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "cargo_id": row[0],
                "cargo_name": row[1],
                "cargo_type": row[2],
                "shipper": row[3],
                "consignee": row[4],
                "weight": row[5],
                "volume": row[6],
                "status": row[7],
                "vessel_id": row[8]
            }
        return None

    def store_route(self, route_data: Dict) -> int:
        """存储航线信息"""
        self.cur.execute("""
            INSERT INTO routes (
                route_id, vessel_id, voyage_number,
                origin_port, origin_port_code, destination_port, destination_port_code,
                planned_departure, planned_arrival, planned_distance, planned_duration,
                actual_departure, actual_arrival, actual_distance, actual_duration,
                average_speed, fuel_consumption
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (route_id) DO UPDATE SET
                actual_departure = EXCLUDED.actual_departure,
                actual_arrival = EXCLUDED.actual_arrival,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            route_data.get("route_id"),
            route_data.get("vessel_id"),
            route_data.get("voyage_number"),
            route_data.get("origin_port"),
            route_data.get("origin_port_code"),
            route_data.get("destination_port"),
            route_data.get("destination_port_code"),
            route_data.get("planned_departure"),
            route_data.get("planned_arrival"),
            route_data.get("planned_distance"),
            route_data.get("planned_duration"),
            route_data.get("actual_departure"),
            route_data.get("actual_arrival"),
            route_data.get("actual_distance"),
            route_data.get("actual_duration"),
            route_data.get("average_speed"),
            route_data.get("fuel_consumption")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_ais_data(self, ais_data: Dict) -> int:
        """存储AIS数据"""
        self.cur.execute("""
            INSERT INTO ais_data (
                mmsi, message_type, message_type_name, latitude, longitude,
                course_over_ground, speed_over_ground, heading, navigation_status,
                imo_number, call_sign, vessel_name, vessel_type,
                dimension_to_bow, dimension_to_stern, dimension_to_port,
                dimension_to_starboard, draught, destination,
                eta_month, eta_day, eta_hour, eta_minute, raw_message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            ais_data.get("mmsi"),
            ais_data.get("message_type"),
            ais_data.get("message_type_name"),
            ais_data.get("latitude"),
            ais_data.get("longitude"),
            ais_data.get("course_over_ground"),
            ais_data.get("speed_over_ground"),
            ais_data.get("heading"),
            ais_data.get("navigation_status"),
            ais_data.get("imo_number"),
            ais_data.get("call_sign"),
            ais_data.get("vessel_name"),
            ais_data.get("vessel_type"),
            ais_data.get("dimension_to_bow"),
            ais_data.get("dimension_to_stern"),
            ais_data.get("dimension_to_port"),
            ais_data.get("dimension_to_starboard"),
            ais_data.get("draught"),
            ais_data.get("destination"),
            ais_data.get("eta_month"),
            ais_data.get("eta_day"),
            ais_data.get("eta_hour"),
            ais_data.get("eta_minute"),
            ais_data.get("raw_message")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_vessel_by_mmsi(self, mmsi: str) -> Optional[str]:
        """根据MMSI获取vessel_id"""
        self.cur.execute("""
            SELECT vessel_id FROM vessels WHERE mmsi = %s
        """, (mmsi,))
        row = self.cur.fetchone()
        return row[0] if row else None

    def update_vessel_info(self, vessel_id: str, update_data: Dict):
        """更新船舶信息"""
        updates = []
        params = []

        for key, value in update_data.items():
            updates.append(f"{key} = %s")
            params.append(value)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(vessel_id)

            query = f"""
                UPDATE vessels
                SET {', '.join(updates)}
                WHERE vessel_id = %s
            """
            self.cur.execute(query, tuple(params))
            self.conn.commit()

    def get_vessels_in_area(self, min_lat: float, max_lat: float,
                           min_lon: float, max_lon: float) -> List[Dict]:
        """获取区域内的船舶"""
        self.cur.execute("""
            SELECT DISTINCT v.vessel_id, v.vessel_name, v.vessel_type,
                   vp.latitude, vp.longitude, vp.speed, vp.course,
                   vp.position_time
            FROM vessels v
            JOIN vessel_positions vp ON v.vessel_id = vp.vessel_id
            WHERE vp.latitude BETWEEN %s AND %s
            AND vp.longitude BETWEEN %s AND %s
            AND vp.position_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
            ORDER BY vp.position_time DESC
        """, (min_lat, max_lat, min_lon, max_lon))

        return [
            {
                "vessel_id": row[0],
                "vessel_name": row[1],
                "vessel_type": row[2],
                "latitude": row[3],
                "longitude": row[4],
                "speed": row[5],
                "course": row[6],
                "position_time": row[7]
            }
            for row in self.cur.fetchall()
        ]

    def store_route_optimization(self, optimization_data: Dict) -> int:
        """存储航线优化结果"""
        self.cur.execute("""
            INSERT INTO route_optimizations (
                optimization_id, route_id, optimization_type,
                origin_latitude, origin_longitude,
                destination_latitude, destination_longitude,
                total_distance, estimated_hours, fuel_consumption,
                fuel_cost, port_cost, total_cost, recommended_speed,
                waypoints, optimization_parameters
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            RETURNING id
        """, (
            optimization_data.get("optimization_id"),
            optimization_data.get("route_id"),
            optimization_data.get("optimization_type"),
            optimization_data.get("origin_latitude"),
            optimization_data.get("origin_longitude"),
            optimization_data.get("destination_latitude"),
            optimization_data.get("destination_longitude"),
            optimization_data.get("total_distance"),
            optimization_data.get("estimated_hours"),
            optimization_data.get("fuel_consumption"),
            optimization_data.get("fuel_cost"),
            optimization_data.get("port_cost"),
            optimization_data.get("total_cost"),
            optimization_data.get("recommended_speed"),
            json.dumps(optimization_data.get("waypoints", [])),
            json.dumps(optimization_data.get("optimization_parameters", {}))
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_route_optimizations(self, route_id: str = None,
                               optimization_type: str = None,
                               limit: int = 100) -> List[Dict]:
        """获取航线优化结果"""
        query = """
            SELECT optimization_id, route_id, optimization_type,
                   total_distance, estimated_hours, total_cost,
                   recommended_speed, waypoints, created_at
            FROM route_optimizations
            WHERE 1=1
        """
        params = []

        if route_id:
            query += " AND route_id = %s"
            params.append(route_id)

        if optimization_type:
            query += " AND optimization_type = %s"
            params.append(optimization_type)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, tuple(params))

        return [
            {
                "optimization_id": row[0],
                "route_id": row[1],
                "optimization_type": row[2],
                "total_distance": float(row[3]) if row[3] else None,
                "estimated_hours": float(row[4]) if row[4] else None,
                "total_cost": float(row[5]) if row[5] else None,
                "recommended_speed": float(row[6]) if row[6] else None,
                "waypoints": json.loads(row[7]) if row[7] else [],
                "created_at": row[8]
            }
            for row in self.cur.fetchall()
        ]

    def store_port_efficiency(self, port_data: Dict) -> int:
        """存储港口效率数据"""
        self.cur.execute("""
            INSERT INTO port_efficiency (
                port_code, port_name, country_code, latitude, longitude,
                average_berth_time_hours, average_cargo_handling_rate,
                average_waiting_time_hours, total_vessels, total_cargo_tonnage,
                efficiency_score
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (port_code) DO UPDATE SET
                average_berth_time_hours = EXCLUDED.average_berth_time_hours,
                average_cargo_handling_rate = EXCLUDED.average_cargo_handling_rate,
                average_waiting_time_hours = EXCLUDED.average_waiting_time_hours,
                total_vessels = EXCLUDED.total_vessels,
                total_cargo_tonnage = EXCLUDED.total_cargo_tonnage,
                efficiency_score = EXCLUDED.efficiency_score,
                last_updated = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            port_data.get("port_code"),
            port_data.get("port_name"),
            port_data.get("country_code"),
            port_data.get("latitude"),
            port_data.get("longitude"),
            port_data.get("average_berth_time_hours"),
            port_data.get("average_cargo_handling_rate"),
            port_data.get("average_waiting_time_hours"),
            port_data.get("total_vessels", 0),
            port_data.get("total_cargo_tonnage", 0),
            port_data.get("efficiency_score")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_port_operation(self, operation_data: Dict) -> int:
        """存储港口操作记录"""
        self.cur.execute("""
            INSERT INTO port_operations (
                operation_id, port_code, vessel_id, operation_type,
                operation_start, operation_end, duration_hours,
                cargo_tonnage, berth_number, crane_count, efficiency_rating
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            operation_data.get("operation_id"),
            operation_data.get("port_code"),
            operation_data.get("vessel_id"),
            operation_data.get("operation_type"),
            operation_data.get("operation_start"),
            operation_data.get("operation_end"),
            operation_data.get("duration_hours"),
            operation_data.get("cargo_tonnage"),
            operation_data.get("berth_number"),
            operation_data.get("crane_count"),
            operation_data.get("efficiency_rating")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_port_efficiency_statistics(self, port_code: str = None,
                                      days: int = 30) -> List[Dict]:
        """获取港口效率统计"""
        query = """
            SELECT port_code, port_name,
                   average_berth_time_hours, average_cargo_handling_rate,
                   average_waiting_time_hours, efficiency_score,
                   total_vessels, total_cargo_tonnage
            FROM port_efficiency
            WHERE 1=1
        """
        params = []

        if port_code:
            query += " AND port_code = %s"
            params.append(port_code)

        query += " ORDER BY efficiency_score DESC"

        self.cur.execute(query, tuple(params))

        return [
            {
                "port_code": row[0],
                "port_name": row[1],
                "average_berth_time_hours": float(row[2]) if row[2] else None,
                "average_cargo_handling_rate": float(row[3]) if row[3] else None,
                "average_waiting_time_hours": float(row[4]) if row[4] else None,
                "efficiency_score": float(row[5]) if row[5] else None,
                "total_vessels": row[6],
                "total_cargo_tonnage": float(row[7]) if row[7] else 0
            }
            for row in self.cur.fetchall()
        ]

    def store_maritime_event(self, event_data: Dict) -> int:
        """存储异常事件"""
        self.cur.execute("""
            INSERT INTO maritime_events (
                event_id, event_type, event_severity, vessel_id, route_id,
                cargo_id, event_location_latitude, event_location_longitude,
                event_description, event_time, resolved_time, resolution_description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            event_data.get("event_id"),
            event_data.get("event_type"),
            event_data.get("event_severity"),
            event_data.get("vessel_id"),
            event_data.get("route_id"),
            event_data.get("cargo_id"),
            event_data.get("event_location_latitude"),
            event_data.get("event_location_longitude"),
            event_data.get("event_description"),
            event_data.get("event_time"),
            event_data.get("resolved_time"),
            event_data.get("resolution_description")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_maritime_events(self, vessel_id: str = None, route_id: str = None,
                           event_type: str = None, severity: str = None,
                           limit: int = 100) -> List[Dict]:
        """获取异常事件"""
        query = """
            SELECT event_id, event_type, event_severity, vessel_id, route_id,
                   cargo_id, event_location_latitude, event_location_longitude,
                   event_description, event_time, resolved_time, resolution_description
            FROM maritime_events
            WHERE 1=1
        """
        params = []

        if vessel_id:
            query += " AND vessel_id = %s"
            params.append(vessel_id)

        if route_id:
            query += " AND route_id = %s"
            params.append(route_id)

        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)

        if severity:
            query += " AND event_severity = %s"
            params.append(severity)

        query += " ORDER BY event_time DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, tuple(params))

        return [
            {
                "event_id": row[0],
                "event_type": row[1],
                "event_severity": row[2],
                "vessel_id": row[3],
                "route_id": row[4],
                "cargo_id": row[5],
                "event_location": {
                    "latitude": float(row[6]) if row[6] else None,
                    "longitude": float(row[7]) if row[7] else None
                },
                "event_description": row[8],
                "event_time": row[9],
                "resolved_time": row[10],
                "resolution_description": row[11]
            }
            for row in self.cur.fetchall()
        ]

    def get_vessel(self, vessel_id: str) -> Optional[Dict]:
        """获取船舶信息"""
        self.cur.execute("""
            SELECT vessel_id, imo_number, vessel_name, vessel_type,
                   flag_state, call_sign, mmsi, gross_tonnage
            FROM vessels
            WHERE vessel_id = %s
        """, (vessel_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "vessel_id": row[0],
                "imo_number": row[1],
                "vessel_name": row[2],
                "vessel_type": row[3],
                "flag_state": row[4],
                "call_sign": row[5],
                "mmsi": row[6],
                "gross_tonnage": float(row[7]) if row[7] else None
            }
        return None

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 7.2 海运航运数据分析查询

**查询示例**：

```python
    def get_vessel_position_statistics(self, vessel_id: str, start_time: datetime) -> Dict:
        """查询船舶位置统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as position_count,
                AVG(speed) as avg_speed,
                MAX(speed) as max_speed,
                MIN(speed) as min_speed,
                AVG(course) as avg_course,
                STDDEV(speed) as speed_stddev
            FROM vessel_positions
            WHERE vessel_id = %s AND position_time >= %s
        """, (vessel_id, start_time))
        row = self.cur.fetchone()
        return {
            "position_count": row[0],
            "avg_speed": float(row[1]) if row[1] else None,
            "max_speed": float(row[2]) if row[2] else None,
            "min_speed": float(row[3]) if row[3] else None,
            "avg_course": float(row[4]) if row[4] else None,
            "speed_stddev": float(row[5]) if row[5] else None
        }

    def get_cargo_tracking_statistics(self, cargo_id: str) -> List[Dict]:
        """查询货物追踪统计"""
        self.cur.execute("""
            SELECT
                event_type,
                COUNT(*) as count,
                MIN(event_time) as first_event,
                MAX(event_time) as last_event,
                AVG(EXTRACT(EPOCH FROM (event_time - LAG(event_time) OVER (ORDER BY event_time)))) as avg_interval_seconds
            FROM cargo_tracking
            WHERE cargo_id = %s
            GROUP BY event_type
            ORDER BY first_event
        """, (cargo_id,))
        return [
            {
                "event_type": row[0],
                "count": row[1],
                "first_event": row[2],
                "last_event": row[3],
                "avg_interval": float(row[4]) if row[4] else None
            }
            for row in self.cur.fetchall()
        ]

    def get_route_performance_statistics(self, vessel_id: str, days: int = 30) -> Dict:
        """查询航线性能统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as route_count,
                AVG(EXTRACT(EPOCH FROM (actual_arrival - actual_departure))/3600) as avg_duration_hours,
                AVG(actual_distance) as avg_distance,
                AVG(average_speed) as avg_speed,
                AVG(fuel_consumption) as avg_fuel_consumption,
                AVG(EXTRACT(EPOCH FROM ((actual_arrival - actual_departure) -
                    (planned_arrival - planned_departure))/3600)) as avg_delay_hours
            FROM routes
            WHERE vessel_id = %s
            AND actual_departure >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND actual_arrival IS NOT NULL
        """, (vessel_id, days))
        row = self.cur.fetchone()
        return {
            "route_count": row[0],
            "avg_duration_hours": float(row[1]) if row[1] else None,
            "avg_distance": float(row[2]) if row[2] else None,
            "avg_speed": float(row[3]) if row[3] else None,
            "avg_fuel_consumption": float(row[4]) if row[4] else None,
            "avg_delay_hours": float(row[5]) if row[5] else None
        }

    def get_cargo_status_distribution(self, days: int = 30) -> List[Dict]:
        """查询货物状态分布"""
        self.cur.execute("""
            SELECT
                status,
                COUNT(*) as count,
                SUM(weight) as total_weight,
                SUM(value) as total_value
            FROM cargoes
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY status
            ORDER BY count DESC
        """, (days,))
        return [
            {
                "status": row[0],
                "count": row[1],
                "total_weight": float(row[2]) if row[2] else 0,
                "total_value": float(row[3]) if row[3] else 0
            }
            for row in self.cur.fetchall()
        ]

    def get_vessel_utilization(self, vessel_id: str, days: int = 30) -> Dict:
        """查询船舶利用率"""
        self.cur.execute("""
            SELECT
                COUNT(DISTINCT route_id) as voyage_count,
                SUM(EXTRACT(EPOCH FROM (actual_arrival - actual_departure))/86400) as total_days_at_sea,
                COUNT(DISTINCT cargo_id) as cargo_count,
                SUM(weight) as total_cargo_weight
            FROM routes r
            LEFT JOIN cargoes c ON r.vessel_id = c.vessel_id
            WHERE r.vessel_id = %s
            AND r.actual_departure >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            AND r.actual_arrival IS NOT NULL
        """, (vessel_id, days))
        row = self.cur.fetchone()

        total_days = days
        utilization_rate = (float(row[1]) / total_days * 100) if row[1] else 0

        return {
            "voyage_count": row[0],
            "total_days_at_sea": float(row[1]) if row[1] else 0,
            "cargo_count": row[2],
            "total_cargo_weight": float(row[3]) if row[3] else 0,
            "utilization_rate": utilization_rate
        }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
