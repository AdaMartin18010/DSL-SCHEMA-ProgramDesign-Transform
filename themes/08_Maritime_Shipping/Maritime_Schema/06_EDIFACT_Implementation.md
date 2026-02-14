# EDIFACT完整解析实现

## 概述

本文档提供完整的EDIFACT（Electronic Data Interchange for Administration, Commerce and Transport）消息解析和转换实现，支持海运行业常用的IFTMIN、IFTMCS、IFTMAN等消息类型。

---

## 1. EDIFACT解析器完整实现

```python
"""
EDIFACT解析器完整实现
支持EDIFACT D.96A标准，海运相关消息类型
"""
import logging
import re
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import xml.etree.ElementTree as ET
from xml.dom import minidom

logger = logging.getLogger(__name__)


class EDIFACTMessageType(Enum):
    """EDIFACT消息类型"""
    IFTMIN = "IFTMIN"  # 货物清单指令
    IFTMCS = "IFTMCS"  # 货物状态报告
    IFTMAN = "IFTMAN"  # 到达通知
    IFTDGN = "IFTDGN"  # 危险品通知
    IFTFCC = "IFTFCC"  # 运费计算
    IFTRIN = "IFTRIN"  # 运输指令
    IFTSTA = "IFTSTA"  # 运输状态
    COPARN = "COPARN"  # 集装箱预约
    CODECO = "CODECO"  # 集装箱装卸通知
    COARRI = "COARRI"  # 集装箱到达通知


@dataclass
class EDIFACTSegment:
    """EDIFACT段"""
    tag: str
    elements: List[Union[str, List[str]]] = field(default_factory=list)
    segment_number: int = 0
    
    def get_element(self, position: int) -> Optional[str]:
        """获取指定位置的元素"""
        if position < len(self.elements):
            element = self.elements[position]
            if isinstance(element, str):
                return element
            elif isinstance(element, list) and element:
                return element[0]
        return None
    
    def get_composite_element(self, position: int, sub_position: int = 0) -> Optional[str]:
        """获取复合元素"""
        if position < len(self.elements):
            element = self.elements[position]
            if isinstance(element, list) and sub_position < len(element):
                return element[sub_position]
        return None


@dataclass
class EDIFACTMessage:
    """EDIFACT消息"""
    message_type: str
    message_reference: str
    segments: List[EDIFACTSegment] = field(default_factory=list)
    sender: str = ""
    recipient: str = ""
    date_time: datetime = None
    version: str = "D96A"
    unb_reference: str = ""
    
    def get_segments_by_tag(self, tag: str) -> List[EDIFACTSegment]:
        """获取指定标签的所有段"""
        return [s for s in self.segments if s.tag == tag]
    
    def get_first_segment(self, tag: str) -> Optional[EDIFACTSegment]:
        """获取指定标签的第一个段"""
        for segment in self.segments:
            if segment.tag == tag:
                return segment
        return None


@dataclass
class CargoItem:
    """货物项"""
    cargo_id: str = ""
    cargo_description: str = ""
    hs_code: str = ""
    packages_count: int = 0
    package_type: str = ""
    gross_weight: float = 0.0
    net_weight: float = 0.0
    volume: float = 0.0
    length: float = 0.0
    width: float = 0.0
    height: float = 0.0
    marks_and_numbers: str = ""
    dangerous_goods_info: Dict[str, str] = field(default_factory=dict)


@dataclass
class TransportDetails:
    """运输详情"""
    vessel_name: str = ""
    voyage_number: str = ""
    carrier: str = ""
    transport_mode: str = ""
    estimated_departure: datetime = None
    estimated_arrival: datetime = None
    loading_port: str = ""
    loading_port_code: str = ""
    discharge_port: str = ""
    discharge_port_code: str = ""
    place_of_receipt: str = ""
    place_of_delivery: str = ""


@dataclass
class PartyInfo:
    """参与方信息"""
    party_type: str = ""  # Shipper, Consignee, NotifyParty, etc.
    party_name: str = ""
    address: str = ""
    city: str = ""
    country: str = ""
    contact_person: str = ""
    contact_phone: str = ""
    contact_email: str = ""


class EDIFACTParser:
    """EDIFACT解析器"""
    
    # 默认分隔符
    DEFAULT_SEGMENT_TERMINATOR = "'"
    DEFAULT_ELEMENT_SEPARATOR = "+"
    DEFAULT_COMPONENT_SEPARATOR = ":"
    DEFAULT_RELEASE_CHARACTER = "?"
    
    def __init__(self, 
                 segment_terminator: str = None,
                 element_separator: str = None,
                 component_separator: str = None,
                 release_character: str = None):
        self.segment_terminator = segment_terminator or self.DEFAULT_SEGMENT_TERMINATOR
        self.element_separator = element_separator or self.DEFAULT_ELEMENT_SEPARATOR
        self.component_separator = component_separator or self.DEFAULT_COMPONENT_SEPARATOR
        self.release_character = release_character or self.DEFAULT_RELEASE_CHARACTER
        
        self.validation_errors: List[str] = []
    
    def parse_message(self, edifact_message: str) -> EDIFACTMessage:
        """解析EDIFACT消息"""
        self.validation_errors = []
        
        # 规范化消息
        message = self._normalize_message(edifact_message)
        
        # 提取UNA段（如果有）
        if message.startswith("UNA"):
            self._parse_una_segment(message[:9])
            message = message[9:]
        
        # 分割段
        raw_segments = message.split(self.segment_terminator)
        
        # 解析每个段
        segments = []
        segment_number = 0
        message_type = ""
        message_reference = ""
        sender = ""
        recipient = ""
        
        for raw_segment in raw_segments:
            raw_segment = raw_segment.strip()
            if not raw_segment:
                continue
            
            segment_number += 1
            segment = self._parse_segment(raw_segment, segment_number)
            segments.append(segment)
            
            # 提取关键信息
            if segment.tag == "UNH":
                message_type = self._extract_message_type(segment)
                message_reference = segment.get_element(0) or ""
            elif segment.tag == "UNB":
                sender = self._extract_sender(segment)
                recipient = self._extract_recipient(segment)
        
        edifact_msg = EDIFACTMessage(
            message_type=message_type,
            message_reference=message_reference,
            segments=segments,
            sender=sender,
            recipient=recipient
        )
        
        return edifact_msg
    
    def _normalize_message(self, message: str) -> str:
        """规范化消息"""
        # 移除换行符和多余空格
        message = re.sub(r'\r?\n', '', message)
        message = message.strip()
        
        # 确保消息以段终止符结束
        if not message.endswith(self.segment_terminator):
            message += self.segment_terminator
        
        return message
    
    def _parse_una_segment(self, una: str):
        """解析UNA服务字符串建议段"""
        if len(una) >= 9 and una.startswith("UNA"):
            # UNA:+.? '
            self.component_separator = una[3]
            self.element_separator = una[4]
            # 第5个字符是十进制符号（通常忽略）
            self.release_character = una[6]
            # 第7个字符是保留
            self.segment_terminator = una[8]
    
    def _parse_segment(self, raw_segment: str, segment_number: int) -> EDIFACTSegment:
        """解析单个段"""
        # 提取标签（前3个字符）
        tag = raw_segment[:3]
        
        # 提取数据元素
        data_part = raw_segment[3:] if len(raw_segment) > 3 else ""
        
        # 分割元素
        raw_elements = data_part.split(self.element_separator)
        
        # 解析每个元素（处理复合元素）
        elements = []
        for element in raw_elements:
            if not element:
                elements.append("")
            elif self.component_separator in element:
                # 复合元素
                components = element.split(self.component_separator)
                # 处理转义字符
                components = [self._unescape(c) for c in components]
                elements.append(components)
            else:
                # 简单元素
                elements.append(self._unescape(element))
        
        return EDIFACTSegment(
            tag=tag,
            elements=elements,
            segment_number=segment_number
        )
    
    def _unescape(self, value: str) -> str:
        """处理转义字符"""
        result = ""
        i = 0
        while i < len(value):
            if value[i] == self.release_character and i + 1 < len(value):
                # 跳过释放字符，保留下一个字符
                i += 1
                result += value[i]
            else:
                result += value[i]
            i += 1
        return result
    
    def _extract_message_type(self, segment: EDIFACTSegment) -> str:
        """提取消息类型"""
        # UNH段中，消息类型在第一个复合元素的第一个组件
        if segment.elements and len(segment.elements) > 1:
            msg_type_elem = segment.elements[1]
            if isinstance(msg_type_elem, list) and msg_type_elem:
                return msg_type_elem[0]
        return ""
    
    def _extract_sender(self, segment: EDIFACTSegment) -> str:
        """提取发送方"""
        # UNB段中，发送方在第2个元素
        return segment.get_element(1) or ""
    
    def _extract_recipient(self, segment: EDIFACTSegment) -> str:
        """提取接收方"""
        # UNB段中，接收方在第3个元素
        return segment.get_element(2) or ""
    
    def parse_iftmin(self, edifact_message: str) -> Dict[str, Any]:
        """解析IFTMIN消息（货物清单指令）"""
        message = self.parse_message(edifact_message)
        
        result = {
            "message_type": "IFTMIN",
            "message_reference": message.message_reference,
            "sender": message.sender,
            "recipient": message.recipient,
            "booking_reference": "",
            "document_date": None,
            "transport_details": TransportDetails(),
            "cargo_items": [],
            "parties": [],
            "special_instructions": []
        }
        
        current_cargo: Optional[CargoItem] = None
        
        for segment in message.segments:
            if segment.tag == "BGM":
                # 消息开始
                result["booking_reference"] = segment.get_element(1) or ""
                doc_code = segment.get_element(0)
                if doc_code:
                    result["document_code"] = doc_code
            
            elif segment.tag == "DTM":
                # 日期/时间
                date_type = segment.get_element(0)
                date_value = segment.get_composite_element(0, 1)
                if date_value:
                    parsed_date = self._parse_edifact_date(date_value)
                    if date_type == "137":  # 文档日期
                        result["document_date"] = parsed_date
                    elif date_type == "133":  # 预计到达
                        result["transport_details"].estimated_arrival = parsed_date
                    elif date_type == "132":  # 预计出发
                        result["transport_details"].estimated_departure = parsed_date
            
            elif segment.tag == "TDT":
                # 运输详情
                result["transport_details"].transport_mode = segment.get_element(2) or ""
                result["transport_details"].carrier = segment.get_composite_element(3, 0) or ""
                result["transport_details"].vessel_name = segment.get_composite_element(4, 0) or ""
                result["transport_details"].voyage_number = segment.get_composite_element(4, 1) or ""
            
            elif segment.tag == "LOC":
                # 地点
                loc_type = segment.get_element(0)
                loc_code = segment.get_composite_element(1, 0)
                loc_name = segment.get_composite_element(1, 2)
                
                if loc_type == "5":  # 装货港
                    result["transport_details"].loading_port_code = loc_code or ""
                    result["transport_details"].loading_port = loc_name or ""
                elif loc_type == "8":  # 卸货港
                    result["transport_details"].discharge_port_code = loc_code or ""
                    result["transport_details"].discharge_port = loc_name or ""
                elif loc_type == "7":  # 接货地点
                    result["transport_details"].place_of_receipt = loc_name or ""
                elif loc_type == "1":  # 交货地点
                    result["transport_details"].place_of_delivery = loc_name or ""
            
            elif segment.tag == "NAD":
                # 参与方名称和地址
                party = self._parse_nad_segment(segment)
                result["parties"].append(party)
            
            elif segment.tag == "GID":
                # 货物描述 - 开始新货物项
                if current_cargo:
                    result["cargo_items"].append(current_cargo)
                
                current_cargo = CargoItem()
                item_number = segment.get_element(0)
                if item_number:
                    current_cargo.cargo_id = item_number
            
            elif segment.tag == "FTX":
                # 自由文本
                text_type = segment.get_element(0)
                text_content = segment.get_composite_element(3, 0)
                
                if text_type == "AAA":  # 货物描述
                    if current_cargo:
                        current_cargo.cargo_description = text_content or ""
                elif text_type == "AAI":  # 特殊指令
                    result["special_instructions"].append(text_content or "")
            
            elif segment.tag == "MEA":
                # 测量
                if current_cargo:
                    measure_type = segment.get_element(0)
                    measure_value = segment.get_composite_element(1, 0)
                    measure_unit = segment.get_composite_element(1, 1)
                    
                    if measure_value:
                        value = float(measure_value) if measure_value else 0.0
                        if measure_type == "WT":  # 重量
                            if measure_unit == "KGM":
                                current_cargo.gross_weight = value
                        elif measure_type == "VOL":  # 体积
                            current_cargo.volume = value
            
            elif segment.tag == "PCI":
                # 包装标识
                if current_cargo:
                    marks = segment.get_composite_element(0, 0)
                    if marks:
                        current_cargo.marks_and_numbers = marks
        
        # 添加最后一个货物项
        if current_cargo:
            result["cargo_items"].append(current_cargo)
        
        return result
    
    def parse_iftmcs(self, edifact_message: str) -> Dict[str, Any]:
        """解析IFTMCS消息（货物状态报告）"""
        message = self.parse_message(edifact_message)
        
        result = {
            "message_type": "IFTMCS",
            "message_reference": message.message_reference,
            "cargo_reference": "",
            "status_updates": [],
            "transport_reference": "",
            "current_location": "",
            "estimated_arrival": None,
            "actual_events": []
        }
        
        current_status = {}
        
        for segment in message.segments:
            if segment.tag == "BGM":
                result["transport_reference"] = segment.get_element(1) or ""
            
            elif segment.tag == "RFF":
                # 参考
                ref_type = segment.get_element(0)
                ref_value = segment.get_composite_element(0, 1)
                
                if ref_type == "BM":  # 提单号
                    result["cargo_reference"] = ref_value or ""
            
            elif segment.tag == "STS":
                # 状态
                status_category = segment.get_element(0)
                status_code = segment.get_element(1)
                status_description = segment.get_element(2)
                
                current_status = {
                    "status_category": status_category,
                    "status_code": status_code,
                    "description": status_description,
                    "timestamp": None,
                    "location": ""
                }
            
            elif segment.tag == "DTM":
                # 日期/时间
                date_type = segment.get_element(0)
                date_value = segment.get_composite_element(0, 1)
                
                if date_value:
                    parsed_date = self._parse_edifact_date(date_value)
                    if current_status:
                        current_status["timestamp"] = parsed_date
                        result["status_updates"].append(current_status)
                        current_status = {}
                    elif date_type == "132":  # ETA
                        result["estimated_arrival"] = parsed_date
            
            elif segment.tag == "LOC":
                # 地点
                if current_status:
                    current_status["location"] = segment.get_composite_element(1, 2) or ""
        
        return result
    
    def parse_iftman(self, edifact_message: str) -> Dict[str, Any]:
        """解析IFTMAN消息（到达通知）"""
        message = self.parse_message(edifact_message)
        
        result = {
            "message_type": "IFTMAN",
            "message_reference": message.message_reference,
            "arrival_notice_reference": "",
            "vessel_details": {},
            "arrival_information": {
                "port_of_arrival": "",
                "port_code": "",
                "estimated_arrival": None,
                "actual_arrival": None,
                "berth": ""
            },
            "consignments": []
        }
        
        for segment in message.segments:
            if segment.tag == "BGM":
                result["arrival_notice_reference"] = segment.get_element(1) or ""
            
            elif segment.tag == "TDT":
                # 运输详情
                result["vessel_details"]["transport_stage"] = segment.get_element(0)
                result["vessel_details"]["vessel_name"] = segment.get_composite_element(4, 0)
                result["vessel_details"]["voyage_number"] = segment.get_composite_element(4, 1)
            
            elif segment.tag == "LOC":
                # 地点
                loc_type = segment.get_element(0)
                
                if loc_type == "8":  # 到达港
                    result["arrival_information"]["port_code"] = segment.get_composite_element(1, 0)
                    result["arrival_information"]["port_of_arrival"] = segment.get_composite_element(1, 2)
                elif loc_type == "11":  # 泊位
                    result["arrival_information"]["berth"] = segment.get_composite_element(1, 2)
            
            elif segment.tag == "DTM":
                # 日期/时间
                date_type = segment.get_element(0)
                date_value = segment.get_composite_element(0, 1)
                
                if date_value:
                    parsed_date = self._parse_edifact_date(date_value)
                    if date_type == "132":  # 预计到达
                        result["arrival_information"]["estimated_arrival"] = parsed_date
                    elif date_type == "133":  # 实际到达
                        result["arrival_information"]["actual_arrival"] = parsed_date
            
            elif segment.tag == "CNI":
                # 托运信息
                consignment = {
                    "consignment_number": segment.get_element(0),
                    "document_number": segment.get_element(1)
                }
                result["consignments"].append(consignment)
        
        return result
    
    def _parse_nad_segment(self, segment: EDIFACTSegment) -> PartyInfo:
        """解析NAD段（名称和地址）"""
        party = PartyInfo()
        
        party_code = segment.get_element(0)
        if party_code:
            party_type_map = {
                "CN": "Consignee",
                "CZ": "Consignor",
                "FW": "FreightForwarder",
                "NI": "NotifyParty",
                "CA": "Carrier",
                "SU": "Supplier"
            }
            party.party_type = party_type_map.get(party_code, party_code)
        
        # 参与方标识
        party_id = segment.get_composite_element(1, 0)
        
        # 参与方名称（可能有多行）
        name_lines = []
        for i in range(4):  # C080复合元素最多4行
            name = segment.get_composite_element(3, i)
            if name:
                name_lines.append(name)
        party.party_name = " ".join(name_lines)
        
        # 街道地址
        street_lines = []
        for i in range(4):
            street = segment.get_composite_element(4, i)
            if street:
                street_lines.append(street)
        party.address = " ".join(street_lines)
        
        # 城市
        party.city = segment.get_composite_element(5, 0) or ""
        
        # 国家
        party.country = segment.get_composite_element(8, 0) or ""
        
        return party
    
    def _parse_edifact_date(self, date_str: str) -> Optional[datetime]:
        """解析EDIFACT日期格式"""
        if not date_str:
            return None
        
        # 尝试不同格式
        formats = [
            "%Y%m%d",      # 20250121
            "%y%m%d",      # 250121
            "%Y%m%d%H%M",  # 202501211430
            "%Y%m%d%H%M%S" # 20250121143000
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def validate_message(self, edifact_message: str) -> Tuple[bool, List[str]]:
        """验证EDIFACT消息"""
        errors = []
        
        try:
            # 基本格式检查
            if not edifact_message or len(edifact_message) < 10:
                errors.append("Message too short")
                return False, errors
            
            # 解析消息
            message = self.parse_message(edifact_message)
            
            # 检查必需段
            required_segments = ["UNH", "UNT"]
            segment_tags = [s.tag for s in message.segments]
            
            for required in required_segments:
                if required not in segment_tags:
                    errors.append(f"Missing required segment: {required}")
            
            # 检查段计数
            unt_segment = message.get_first_segment("UNT")
            if unt_segment:
                declared_count = unt_segment.get_element(0)
                if declared_count:
                    try:
                        count = int(declared_count)
                        # UNH和UNT都计入总数
                        if count != len(message.segments):
                            errors.append(f"Segment count mismatch: declared {count}, actual {len(message.segments)}")
                    except ValueError:
                        errors.append("Invalid segment count in UNT")
            
            # 检查消息类型
            if not message.message_type:
                errors.append("Could not determine message type")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors


class EDIFACTGenerator:
    """EDIFACT消息生成器"""
    
    def __init__(self):
        self.segment_terminator = "'"
        self.element_separator = "+"
        self.component_separator = ":"
    
    def generate_iftmin(self, data: Dict[str, Any]) -> str:
        """生成IFTMIN消息"""
        segments = []
        
        # UNB - 消息头
        segments.append(self._build_segment("UNB", [
            ["UNOA", "3"],
            [data.get("sender", ""), ""],
            [data.get("recipient", "")],
            [datetime.now().strftime("%y%m%d"), datetime.now().strftime("%H%M")],
            data.get("reference", "")
        ]))
        
        # UNH - 消息头
        segments.append(self._build_segment("UNH", [
            data.get("message_reference", "1"),
            ["IFTMIN", "D", "96A", "UN"]
        ]))
        
        # BGM - 消息开始
        segments.append(self._build_segment("BGM", [
            "340",  # 运输指令
            data.get("booking_reference", ""),
            "9"     # 原始
        ]))
        
        # DTM - 日期/时间
        if data.get("document_date"):
            segments.append(self._build_segment("DTM", [
                ["137", data["document_date"].strftime("%Y%m%d"), "102"]
            ]))
        
        # TDT - 运输详情
        transport = data.get("transport_details", {})
        segments.append(self._build_segment("TDT", [
            "20",  # 主要运输
            "",
            transport.get("transport_mode", ""),
            ["", "", "", transport.get("carrier", "")],
            [transport.get("vessel_name", ""), transport.get("voyage_number", "")]
        ]))
        
        # LOC - 地点
        if transport.get("loading_port_code"):
            segments.append(self._build_segment("LOC", [
                "5",  # 装货港
                [transport["loading_port_code"], "", "6", transport.get("loading_port", "")]
            ]))
        
        if transport.get("discharge_port_code"):
            segments.append(self._build_segment("LOC", [
                "8",  # 卸货港
                [transport["discharge_port_code"], "", "6", transport.get("discharge_port", "")]
            ]))
        
        # GID + MEA - 货物项
        for cargo in data.get("cargo_items", []):
            segments.append(self._build_segment("GID", [
                cargo.get("cargo_id", "")
            ]))
            
            if cargo.get("gross_weight"):
                segments.append(self._build_segment("MEA", [
                    "WT",
                    ["G", str(cargo["gross_weight"]), "KGM"]
                ]))
            
            if cargo.get("cargo_description"):
                segments.append(self._build_segment("FTX", [
                    "AAA",
                    "",
                    "",
                    "",
                    [cargo["cargo_description"]]
                ]))
        
        # UNT - 消息尾
        segments.append(self._build_segment("UNT", [
            str(len(segments)),
            data.get("message_reference", "1")
        ]))
        
        # UNZ - 交换尾
        segments.append(self._build_segment("UNZ", [
            "1",
            data.get("reference", "")
        ]))
        
        return self.segment_terminator.join(segments) + self.segment_terminator
    
    def _build_segment(self, tag: str, elements: List[Any]) -> str:
        """构建段"""
        parts = [tag]
        
        for element in elements:
            if isinstance(element, list):
                # 复合元素
                parts.append(self.component_separator.join(str(e) for e in element))
            else:
                # 简单元素
                parts.append(str(element))
        
        return self.element_separator.join(parts)


# 使用示例
if __name__ == "__main__":
    parser = EDIFACTParser()
    
    # 示例IFTMIN消息
    iftmin_message = """UNA:+.? '
UNB+UNOA:3+SENDER+RECEIVER+250121:1430+REF123'
UNH+1+IFTMIN:D:96A:UN'
BGM+340+BOOK123+9'
DTM+137:20250121:102'
TDT+20++1++MV OCEAN STAR:VOY123'
LOC+5+CNSHA::6+SHANGHAI'
LOC+8+SGSIN::6+SINGAPORE'
GID+1'
MEA+WT+G+20000:KGM'
FTX+AAA+++ELECTRONICS'
UNT+9+1'
UNZ+1+REF123'"""
    
    # 解析消息
    result = parser.parse_iftmin(iftmin_message)
    print(f"Booking Reference: {result['booking_reference']}")
    print(f"Vessel: {result['transport_details'].vessel_name}")
    print(f"Cargo Items: {len(result['cargo_items'])}")
```

---

## 2. 转换使用说明

### 2.1 解析EDIFACT消息

```python
from edifact_parser import EDIFACTParser

parser = EDIFACTParser()

# 解析IFTMIN消息
result = parser.parse_iftmin(edifact_message)
print(f"Booking: {result['booking_reference']}")
print(f"Vessel: {result['transport_details'].vessel_name}")

# 解析IFTMCS消息
status_result = parser.parse_iftmcs(status_message)
for update in status_result['status_updates']:
    print(f"Status: {update['description']} at {update['timestamp']}")
```

### 2.2 验证消息

```python
# 验证EDIFACT消息
is_valid, errors = parser.validate_message(edifact_message)
if not is_valid:
    for error in errors:
        print(f"Validation Error: {error}")
```

### 2.3 生成EDIFACT消息

```python
from edifact_parser import EDIFACTGenerator

generator = EDIFACTGenerator()

# 生成IFTMIN消息
iftmin_data = {
    "sender": "SHIPPER",
    "recipient": "CARRIER",
    "booking_reference": "BOOK001",
    "message_reference": "1",
    "transport_details": {
        "vessel_name": "MV OCEAN STAR",
        "voyage_number": "VOY001",
        "loading_port": "Shanghai",
        "loading_port_code": "CNSHA",
        "discharge_port": "Singapore",
        "discharge_port_code": "SGSIN"
    },
    "cargo_items": [
        {"cargo_id": "1", "gross_weight": 20000, "cargo_description": "Electronics"}
    ]
}

message = generator.generate_iftmin(iftmin_data)
print(message)
```

---

**创建时间**: 2025-01-21
**代码行数**: 600+行
