# EDI Schema转换体系

## 📑 目录

- [EDI Schema转换体系](#edi-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. EDI X12解析实现](#2-edi-x12解析实现)
    - [2.1 EDI X12解析器](#21-edi-x12解析器)
    - [2.2 EDIFACT解析器](#22-edifact解析器)
  - [2. EDI X12到EDIFACT转换](#2-edi-x12到edifact转换)
  - [3. EDIFACT到EDI X12转换](#3-edifact到edi-x12转换)
  - [4. EDI消息验证](#4-edi消息验证)
  - [5. EDI数据存储与分析](#5-edi数据存储与分析)
    - [5.1 PostgreSQL EDI数据存储](#51-postgresql-edi数据存储)
    - [5.2 EDI数据分析查询](#52-edi数据分析查询)

---

## 1. 转换体系概述

EDI Schema转换体系支持EDI X12、EDIFACT之间的转换，
以及EDI数据到数据库存储的转换。

### 1.1 转换目标

1. **EDI X12到EDIFACT转换**：EDI X12交易集到EDIFACT消息
2. **EDIFACT到EDI X12转换**：EDIFACT消息到EDI X12交易集
3. **EDI消息验证**：EDI消息格式和内容验证
4. **EDI数据到数据库转换**：EDI消息到PostgreSQL存储

---

## 2. EDI X12解析实现

### 2.1 EDI X12解析器

**完整的EDI X12解析实现**：

```python
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class EDIX12Parser:
    """EDI X12消息解析器 - 完整实现"""

    def __init__(self):
        # X12默认分隔符
        self.element_separator = "*"
        self.segment_terminator = "~"
        self.sub_element_separator = ">"
        self.release_character = "?"

    def parse_interchange(self, x12_message: str) -> Dict:
        """解析X12交换（ISA/ISE）"""
        lines = x12_message.split('\n')
        isa_line = None
        ise_line = None

        for line in lines:
            line = line.strip()
            if line.startswith("ISA"):
                isa_line = line
            elif line.startswith("IEA"):
                ise_line = line

        if not isa_line:
            raise ValueError("Missing ISA segment")

        # 解析ISA段
        isa_elements = isa_line.split(self.element_separator)
        if len(isa_elements) < 17:
            raise ValueError("Invalid ISA segment format")

        interchange = {
            "isa": {
                "authorization_qualifier": isa_elements[1],
                "authorization_information": isa_elements[2],
                "security_qualifier": isa_elements[3],
                "security_information": isa_elements[4],
                "interchange_id_qualifier": isa_elements[5],
                "interchange_sender_id": isa_elements[6],
                "interchange_id_qualifier_2": isa_elements[7],
                "interchange_receiver_id": isa_elements[8],
                "interchange_date": isa_elements[9],
                "interchange_time": isa_elements[10],
                "interchange_control_standards_id": isa_elements[11],
                "interchange_control_version_number": isa_elements[12],
                "interchange_control_number": isa_elements[13],
                "acknowledgment_requested": isa_elements[14],
                "usage_indicator": isa_elements[15],
                "component_element_separator": isa_elements[16] if len(isa_elements) > 16 else ">"
            }
        }

        # 解析IEA段
        if ise_line:
            ise_elements = ise_line.split(self.element_separator)
            if len(ise_elements) >= 2:
                interchange["iea"] = {
                    "number_of_included_functional_groups": ise_elements[1],
                    "interchange_control_number": ise_elements[2] if len(ise_elements) > 2 else ""
                }

        return interchange

    def parse_functional_group(self, gs_ge_block: str) -> Dict:
        """解析功能组（GS/GE）"""
        lines = gs_ge_block.split('\n')
        gs_line = None
        ge_line = None

        for line in lines:
            line = line.strip()
            if line.startswith("GS"):
                gs_line = line
            elif line.startswith("GE"):
                ge_line = line

        if not gs_line:
            raise ValueError("Missing GS segment")

        # 解析GS段
        gs_elements = gs_line.split(self.element_separator)
        if len(gs_elements) < 8:
            raise ValueError("Invalid GS segment format")

        functional_group = {
            "gs": {
                "functional_identifier_code": gs_elements[1],
                "application_sender_code": gs_elements[2],
                "application_receiver_code": gs_elements[3],
                "date": gs_elements[4],
                "time": gs_elements[5],
                "group_control_number": gs_elements[6],
                "responsible_agency_code": gs_elements[7],
                "version_release_industry_identifier": gs_elements[8] if len(gs_elements) > 8 else ""
            }
        }

        # 解析GE段
        if ge_line:
            ge_elements = ge_line.split(self.element_separator)
            if len(ge_elements) >= 2:
                functional_group["ge"] = {
                    "number_of_transaction_sets_included": ge_elements[1],
                    "group_control_number": ge_elements[2] if len(ge_elements) > 2 else ""
                }

        return functional_group

    def parse_transaction_set(self, st_se_block: str) -> Dict:
        """解析交易集（ST/SE）"""
        lines = st_se_block.split('\n')
        st_line = None
        se_line = None
        segments = []

        for line in lines:
            line = line.strip()
            if line.startswith("ST"):
                st_line = line
            elif line.startswith("SE"):
                se_line = line
            elif line and not line.startswith("ISA") and not line.startswith("IEA") and not line.startswith("GS") and not line.startswith("GE"):
                segments.append(line)

        if not st_line:
            raise ValueError("Missing ST segment")

        # 解析ST段
        st_elements = st_line.split(self.element_separator)
        if len(st_elements) < 3:
            raise ValueError("Invalid ST segment format")

        transaction_set = {
            "st": {
                "transaction_set_identifier_code": st_elements[1],
                "transaction_set_control_number": st_elements[2],
                "implementation_convention_reference": st_elements[3] if len(st_elements) > 3 else ""
            },
            "segments": []
        }

        # 解析所有段
        for segment_line in segments:
            segment = self.parse_segment(segment_line)
            if segment:
                transaction_set["segments"].append(segment)

        # 解析SE段
        if se_line:
            se_elements = se_line.split(self.element_separator)
            if len(se_elements) >= 2:
                transaction_set["se"] = {
                    "number_of_included_segments": se_elements[1],
                    "transaction_set_control_number": se_elements[2] if len(se_elements) > 2 else ""
                }

        return transaction_set

    def parse_segment(self, segment_line: str) -> Optional[Dict]:
        """解析单个段"""
        if not segment_line or not segment_line.strip():
            return None

        # 移除段终止符
        segment_line = segment_line.rstrip(self.segment_terminator)

        elements = segment_line.split(self.element_separator)
        if not elements:
            return None

        segment_tag = elements[0]
        segment_data = {
            "tag": segment_tag,
            "elements": []
        }

        # 解析元素
        for element in elements[1:]:
            if self.sub_element_separator in element:
                # 复合元素
                sub_elements = element.split(self.sub_element_separator)
                segment_data["elements"].append({
                    "type": "composite",
                    "sub_elements": sub_elements
                })
            else:
                # 简单元素
                segment_data["elements"].append({
                    "type": "simple",
                    "value": element
                })

        return segment_data

    def parse_x12_message(self, x12_message: str) -> Dict:
        """解析完整的X12消息"""
        # 解析交换
        interchange = self.parse_interchange(x12_message)

        # 提取功能组和交易集
        lines = x12_message.split('\n')
        functional_groups = []
        current_group = []
        in_group = False

        for line in lines:
            line = line.strip()
            if line.startswith("GS"):
                if current_group:
                    functional_groups.append('\n'.join(current_group))
                current_group = [line]
                in_group = True
            elif line.startswith("GE"):
                current_group.append(line)
                functional_groups.append('\n'.join(current_group))
                current_group = []
                in_group = False
            elif in_group:
                current_group.append(line)

        # 解析功能组
        parsed_groups = []
        for group_block in functional_groups:
            group = self.parse_functional_group(group_block)

            # 提取交易集
            transactions = []
            lines = group_block.split('\n')
            current_transaction = []
            in_transaction = False

            for line in lines:
                line = line.strip()
                if line.startswith("ST"):
                    if current_transaction:
                        transactions.append('\n'.join(current_transaction))
                    current_transaction = [line]
                    in_transaction = True
                elif line.startswith("SE"):
                    current_transaction.append(line)
                    transactions.append('\n'.join(current_transaction))
                    current_transaction = []
                    in_transaction = False
                elif in_transaction:
                    current_transaction.append(line)

            # 解析交易集
            parsed_transactions = []
            for transaction_block in transactions:
                transaction = self.parse_transaction_set(transaction_block)
                parsed_transactions.append(transaction)

            group["transactions"] = parsed_transactions
            parsed_groups.append(group)

        return {
            "interchange": interchange,
            "functional_groups": parsed_groups
        }

    def validate_x12_message(self, x12_message: str) -> Tuple[bool, List[str]]:
        """验证X12消息"""
        errors = []

        try:
            parsed = self.parse_x12_message(x12_message)
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return False, errors

        # 验证ISA/IEA
        interchange = parsed.get("interchange", {})
        if "isa" not in interchange:
            errors.append("Missing ISA segment")
        if "iea" not in interchange:
            errors.append("Missing IEA segment")

        # 验证段计数
        if "isa" in interchange and "iea" in interchange:
            isa_control_number = interchange["isa"].get("interchange_control_number")
            iea_control_number = interchange["iea"].get("interchange_control_number")
            if isa_control_number != iea_control_number:
                errors.append(f"Interchange control number mismatch: ISA={isa_control_number}, IEA={iea_control_number}")

        # 验证功能组
        for group in parsed.get("functional_groups", []):
            if "gs" not in group:
                errors.append("Missing GS segment in functional group")
            if "ge" not in group:
                errors.append("Missing GE segment in functional group")

            # 验证交易集
            for transaction in group.get("transactions", []):
                if "st" not in transaction:
                    errors.append("Missing ST segment in transaction set")
                if "se" not in transaction:
                    errors.append("Missing SE segment in transaction set")

                # 验证段计数
                if "st" in transaction and "se" in transaction:
                    expected_count = int(transaction["se"].get("number_of_included_segments", 0))
                    actual_count = len(transaction.get("segments", [])) + 2  # ST + SE
                    if expected_count != actual_count:
                        errors.append(f"Segment count mismatch in transaction {transaction['st'].get('transaction_set_control_number')}: expected {expected_count}, actual {actual_count}")

        return len(errors) == 0, errors
```

### 2.2 EDIFACT解析器

**完整的EDIFACT解析实现**：

```python
class EDIFACTParser:
    """EDIFACT消息解析器 - 完整实现"""

    def __init__(self):
        self.segment_terminator = "'"
        self.element_separator = "+"
        self.component_separator = ":"
        self.release_character = "?"

    def parse_interchange(self, edifact_message: str) -> Dict:
        """解析EDIFACT交换（UNB/UNZ）"""
        lines = edifact_message.split('\n')
        unb_line = None
        unz_line = None

        for line in lines:
            line = line.strip()
            if line.startswith("UNB"):
                unb_line = line
            elif line.startswith("UNZ"):
                unz_line = line

        if not unb_line:
            raise ValueError("Missing UNB segment")

        # 解析UNB段
        unb_elements = unb_line.rstrip(self.segment_terminator).split(self.element_separator)
        if len(unb_elements) < 5:
            raise ValueError("Invalid UNB segment format")

        interchange = {
            "unb": {
                "syntax_identifier": unb_elements[1] if len(unb_elements) > 1 else "",
                "sender_identification": unb_elements[2] if len(unb_elements) > 2 else "",
                "receiver_identification": unb_elements[3] if len(unb_elements) > 3 else "",
                "date_of_preparation": unb_elements[4] if len(unb_elements) > 4 else "",
                "time_of_preparation": unb_elements[5] if len(unb_elements) > 5 else "",
                "interchange_control_reference": unb_elements[6] if len(unb_elements) > 6 else ""
            }
        }

        # 解析UNZ段
        if unz_line:
            unz_elements = unz_line.rstrip(self.segment_terminator).split(self.element_separator)
            if len(unz_elements) >= 2:
                interchange["unz"] = {
                    "interchange_control_count": unz_elements[1],
                    "interchange_control_reference": unz_elements[2] if len(unz_elements) > 2 else ""
                }

        return interchange

    def parse_message(self, edifact_message: str) -> List[Dict]:
        """解析EDIFACT消息中的所有段"""
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

    def parse_edifact_message(self, edifact_message: str) -> Dict:
        """解析完整的EDIFACT消息"""
        # 解析交换
        interchange = self.parse_interchange(edifact_message)

        # 解析消息
        segments = self.parse_message(edifact_message)

        # 查找UNH/UNT
        unh_segment = None
        unt_segment = None
        message_segments = []

        in_message = False
        for segment in segments:
            tag = segment.get("tag", "")
            if tag == "UNH":
                unh_segment = segment
                in_message = True
                message_segments.append(segment)
            elif tag == "UNT":
                unt_segment = segment
                message_segments.append(segment)
                in_message = False
            elif in_message:
                message_segments.append(segment)

        message = {
            "unh": unh_segment,
            "unt": unt_segment,
            "segments": message_segments
        }

        return {
            "interchange": interchange,
            "message": message
        }

    def validate_edifact_message(self, edifact_message: str) -> Tuple[bool, List[str]]:
        """验证EDIFACT消息"""
        errors = []

        try:
            parsed = self.parse_edifact_message(edifact_message)
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return False, errors

        # 验证UNB/UNZ
        interchange = parsed.get("interchange", {})
        if "unb" not in interchange:
            errors.append("Missing UNB segment")
        if "unz" not in interchange:
            errors.append("Missing UNZ segment")

        # 验证UNH/UNT
        message = parsed.get("message", {})
        if not message.get("unh"):
            errors.append("Missing UNH segment")
        if not message.get("unt"):
            errors.append("Missing UNT segment")

        # 验证段计数
        if message.get("unh") and message.get("unt"):
            unh_elements = message["unh"].get("elements", [])
            unt_elements = message["unt"].get("elements", [])

            if unt_elements and len(unt_elements) > 0:
                declared_count = unt_elements[0].get("value", "")
                try:
                    declared_count_int = int(declared_count)
                    actual_count = len(message.get("segments", []))
                    if declared_count_int != actual_count:
                        errors.append(f"Segment count mismatch: declared {declared_count_int}, actual {actual_count}")
                except ValueError:
                    errors.append(f"Invalid segment count in UNT: {declared_count}")

        return len(errors) == 0, errors

    def parse_orders_message(self, segments: List[Dict]) -> Dict:
        """解析ORDERS消息"""
        orders = {
            "message_type": "ORDERS",
            "order_details": []
        }

        current_order_line = {}

        for segment in segments:
            tag = segment.get("tag", "")

            if tag == "UNH":
                # 消息头
                if segment.get("elements"):
                    msg_ref_elem = segment["elements"][0] if segment["elements"] else {}
                    orders["message_reference"] = msg_ref_elem.get("value", "") if msg_ref_elem.get("type") == "simple" else msg_ref_elem.get("components", [""])[0] if msg_ref_elem.get("type") == "composite" else ""

            elif tag == "BGM":
                # 消息开始
                if segment.get("elements"):
                    orders["document_number"] = segment["elements"][1].get("value", "") if len(segment["elements"]) > 1 else ""

            elif tag == "DTM":
                # 日期时间
                if segment.get("elements"):
                    date_type = segment["elements"][0].get("value", "")
                    date_value = segment["elements"][1].get("value", "") if len(segment["elements"]) > 1 else ""
                    if date_type == "137":
                        orders["order_date"] = self._parse_edifact_date(date_value)

            elif tag == "LIN":
                # 订单行项
                if current_order_line:
                    orders["order_details"].append(current_order_line)
                current_order_line = {
                    "line_number": segment["elements"][0].get("value", "") if segment.get("elements") else "",
                    "product_id": "",
                    "quantity": 0,
                    "unit_price": 0
                }

            elif tag == "PIA":
                # 产品标识
                if current_order_line and segment.get("elements"):
                    product_id_elem = segment["elements"][1] if len(segment["elements"]) > 1 else {}
                    if product_id_elem.get("type") == "composite":
                        current_order_line["product_id"] = product_id_elem.get("components", [""])[0] if product_id_elem.get("components") else ""

            elif tag == "QTY":
                # 数量
                if current_order_line and segment.get("elements"):
                    quantity_elem = segment["elements"][1] if len(segment["elements"]) > 1 else {}
                    if quantity_elem.get("type") == "simple":
                        try:
                            current_order_line["quantity"] = float(quantity_elem.get("value", 0))
                        except ValueError:
                            pass

            elif tag == "PRI":
                # 价格
                if current_order_line and segment.get("elements"):
                    price_elem = segment["elements"][1] if len(segment["elements"]) > 1 else {}
                    if price_elem.get("type") == "simple":
                        try:
                            current_order_line["unit_price"] = float(price_elem.get("value", 0))
                        except ValueError:
                            pass

        if current_order_line:
            orders["order_details"].append(current_order_line)

        return orders

    def parse_invoic_message(self, segments: List[Dict]) -> Dict:
        """解析INVOIC消息"""
        invoice = {
            "message_type": "INVOIC",
            "invoice_lines": []
        }

        current_line = {}

        for segment in segments:
            tag = segment.get("tag", "")

            if tag == "UNH":
                if segment.get("elements"):
                    msg_ref_elem = segment["elements"][0] if segment["elements"] else {}
                    invoice["message_reference"] = msg_ref_elem.get("value", "") if msg_ref_elem.get("type") == "simple" else msg_ref_elem.get("components", [""])[0] if msg_ref_elem.get("type") == "composite" else ""

            elif tag == "BGM":
                if segment.get("elements"):
                    invoice["invoice_number"] = segment["elements"][1].get("value", "") if len(segment["elements"]) > 1 else ""

            elif tag == "DTM":
                if segment.get("elements"):
                    date_type = segment["elements"][0].get("value", "")
                    date_value = segment["elements"][1].get("value", "") if len(segment["elements"]) > 1 else ""
                    if date_type == "137":
                        invoice["invoice_date"] = self._parse_edifact_date(date_value)

            elif tag == "LIN":
                if current_line:
                    invoice["invoice_lines"].append(current_line)
                current_line = {
                    "line_number": segment["elements"][0].get("value", "") if segment.get("elements") else "",
                    "product_id": "",
                    "quantity": 0,
                    "unit_price": 0,
                    "line_total": 0
                }

            elif tag == "MOA":
                # 货币金额
                if segment.get("elements"):
                    amount_type = segment["elements"][0].get("value", "")
                    amount_elem = segment["elements"][1] if len(segment["elements"]) > 1 else {}
                    if amount_elem.get("type") == "simple":
                        try:
                            amount = float(amount_elem.get("value", 0))
                            if amount_type == "79":
                                if current_line:
                                    current_line["line_total"] = amount
                                else:
                                    invoice["total_amount"] = amount
                        except ValueError:
                            pass

        if current_line:
            invoice["invoice_lines"].append(current_line)

        return invoice

    def _parse_edifact_date(self, date_str: str) -> Optional[str]:
        """解析EDIFACT日期格式"""
        if len(date_str) == 8:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        elif len(date_str) >= 12:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T{date_str[8:10]}:{date_str[10:12]}:00Z"
        return None
```

---

## 2. EDI X12到EDIFACT转换

**转换规则**：

- 850 (Purchase Order) → ORDERS
- 855 (Purchase Order Acknowledgment) → ORDRSP
- 856 (Ship Notice) → DESADV
- 810 (Invoice) → INVOIC

**转换示例**：

```python
def convert_x12_850_to_edifact_orders(x12_850: dict) -> dict:
    """将EDI X12 850交易集转换为EDIFACT ORDERS消息"""
    edifact_orders = {
        "UNH": {
            "message_reference_number": generate_message_ref(),
            "message_type": "ORDERS",
            "message_version_number": "D",
            "message_release_number": "23A",
            "controlling_agency": "UN"
        },
        "BGM": {
            "document_message_name": "220",
            "document_message_number": x12_850.get("BEG", {}).get("purchase_order_number"),
            "message_function_code": "9"  # Original
        },
        "DTM": [
            {
                "date_time_period_qualifier": "137",
                "date_time_period": format_date(x12_850.get("BEG", {}).get("date")),
                "date_time_period_format_qualifier": "102"
            }
        ],
        "LIN": []
    }

    # 转换订单行项
    for po1 in x12_850.get("PO1_segments", []):
        lin_segment = {
            "line_item_number": po1.get("assigned_identification"),
            "item_number_identification": {
                "item_number_type_code_qualifier": map_product_id_qualifier(po1.get("product_id_qualifier")),
                "item_number": po1.get("product_id")
            },
            "quantity_details": {
                "quantity_type_code_qualifier": "21",
                "quantity": po1.get("quantity_ordered"),
                "measure_unit_code": po1.get("unit_of_measure")
            },
            "price_information": {
                "price_code_qualifier": "AAA",
                "price_amount": po1.get("unit_price"),
                "price_type_code": "CA"
            }
        }
        edifact_orders["LIN"].append(lin_segment)

    return edifact_orders

def map_product_id_qualifier(x12_qualifier: str) -> str:
    """映射EDI X12产品ID限定符到EDIFACT"""
    mapping = {
        "UP": "EN",  # Universal Product Code -> EAN
        "VN": "EN",  # Vendor Item Number -> EAN
        "IN": "IN"   # Buyer Item Number -> Item Number
    }
    return mapping.get(x12_qualifier, "IN")
```

---

## 3. EDIFACT到EDI X12转换

**转换规则**：

- ORDERS → 850 (Purchase Order)
- ORDRSP → 855 (Purchase Order Acknowledgment)
- DESADV → 856 (Ship Notice)
- INVOIC → 810 (Invoice)

**转换示例**：

```python
def convert_edifact_orders_to_x12_850(edifact_orders: dict) -> dict:
    """将EDIFACT ORDERS消息转换为EDI X12 850交易集"""
    x12_850 = {
        "ST": {
            "transaction_set_identifier_code": "850",
            "transaction_set_control_number": generate_control_number()
        },
        "BEG": {
            "transaction_set_purpose_code": map_message_function_code(edifact_orders.get("BGM", {}).get("message_function_code")),
            "purchase_order_type_code": "SA",  # Stand-alone
            "purchase_order_number": edifact_orders.get("BGM", {}).get("document_message_number"),
            "date": parse_date(edifact_orders.get("DTM", [{}])[0].get("date_time_period"))
        },
        "PO1_segments": []
    }

    # 转换订单行项
    for lin in edifact_orders.get("LIN", []):
        po1_segment = {
            "assigned_identification": lin.get("line_item_number", "1"),
            "quantity_ordered": lin.get("quantity_details", {}).get("quantity"),
            "unit_of_measure": lin.get("quantity_details", {}).get("measure_unit_code"),
            "unit_price": lin.get("price_information", {}).get("price_amount"),
            "product_id_qualifier": map_item_number_qualifier(lin.get("item_number_identification", {}).get("item_number_type_code_qualifier")),
            "product_id": lin.get("item_number_identification", {}).get("item_number")
        }
        x12_850["PO1_segments"].append(po1_segment)

    x12_850["SE"] = {
        "number_of_included_segments": calculate_segment_count(x12_850),
        "transaction_set_control_number": x12_850["ST"]["transaction_set_control_number"]
    }

    return x12_850

def map_message_function_code(edifact_code: str) -> str:
    """映射EDIFACT消息功能代码到EDI X12"""
    mapping = {
        "9": "00",   # Original -> Original
        "5": "08",   # Replace -> Change
        "36": "01"   # Cancellation -> Cancellation
    }
    return mapping.get(edifact_code, "00")
```

---

## 4. EDI消息验证

**验证规则**：

- 消息结构验证
- 段顺序验证
- 数据元素格式验证
- 必填字段验证

**验证示例**：

```python
def validate_edi_x12_message(x12_message: dict) -> dict:
    """验证EDI X12消息"""
    errors = []
    warnings = []

    # 验证交易集头
    if "ST" not in x12_message:
        errors.append("Missing ST segment (Transaction Set Header)")

    # 验证交易集尾
    if "SE" not in x12_message:
        errors.append("Missing SE segment (Transaction Set Trailer)")

    # 验证段计数
    if "ST" in x12_message and "SE" in x12_message:
        expected_count = x12_message["SE"]["number_of_included_segments"]
        actual_count = count_segments(x12_message)
        if expected_count != actual_count:
            errors.append(f"Segment count mismatch: expected {expected_count}, actual {actual_count}")

    # 验证必填字段
    if "BEG" in x12_message:
        if not x12_message["BEG"].get("purchase_order_number"):
            errors.append("BEG segment missing required field: purchase_order_number")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_edifact_message(edifact_message: dict) -> dict:
    """验证EDIFACT消息"""
    errors = []
    warnings = []

    # 验证消息头
    if "UNH" not in edifact_message:
        errors.append("Missing UNH segment (Message Header)")

    # 验证消息尾
    if "UNT" not in edifact_message:
        errors.append("Missing UNT segment (Message Trailer)")

    # 验证段计数
    if "UNH" in edifact_message and "UNT" in edifact_message:
        expected_count = edifact_message["UNT"]["number_of_segments_in_message"]
        actual_count = count_segments(edifact_message)
        if expected_count != actual_count:
            errors.append(f"Segment count mismatch: expected {expected_count}, actual {actual_count}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
```

---

## 5. EDI数据存储与分析

### 5.1 PostgreSQL EDI数据存储

**数据库设计**：

```python
import psycopg2
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class EDIStorage:
    """EDI数据PostgreSQL存储类 - 增强错误处理"""

    def __init__(self, connection_string: str):
        # 输入验证
        if not connection_string:
            raise ValueError("Connection string cannot be empty")

        if not isinstance(connection_string, str):
            raise TypeError(f"Connection string must be a string, got {type(connection_string)}")

        try:
            self.conn = psycopg2.connect(connection_string)
            self.create_tables()
            logger.info("EDIStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing EDIStorage: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize EDIStorage: {e}") from e

    def create_tables(self):
        """创建EDI数据存储表"""
        cursor = self.conn.cursor()

        # EDI交换表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_interchanges (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                interchange_type VARCHAR(10) NOT NULL,
                interchange_control_number VARCHAR(14) NOT NULL UNIQUE,
                sender_id VARCHAR(35),
                receiver_id VARCHAR(35),
                interchange_date DATE,
                interchange_time TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI功能组表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_functional_groups (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                interchange_id UUID NOT NULL REFERENCES edi_interchanges(id) ON DELETE CASCADE,
                functional_identifier_code VARCHAR(2),
                group_control_number VARCHAR(9) NOT NULL,
                sender_code VARCHAR(15),
                receiver_code VARCHAR(15),
                date DATE,
                time TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI交易集/消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                functional_group_id UUID NOT NULL REFERENCES edi_functional_groups(id) ON DELETE CASCADE,
                transaction_type VARCHAR(10) NOT NULL,
                transaction_set_id VARCHAR(3),
                transaction_control_number VARCHAR(14) NOT NULL,
                message_type VARCHAR(6),
                message_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI段表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_segments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                transaction_id UUID NOT NULL REFERENCES edi_transactions(id) ON DELETE CASCADE,
                segment_id VARCHAR(3) NOT NULL,
                segment_position INTEGER NOT NULL,
                segment_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI元素表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_elements (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                segment_id UUID NOT NULL REFERENCES edi_segments(id) ON DELETE CASCADE,
                element_position INTEGER NOT NULL,
                element_value TEXT,
                element_format VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # EDI统计信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edi_statistics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                statistic_type VARCHAR(50) NOT NULL,
                transaction_type VARCHAR(10),
                statistic_date DATE NOT NULL,
                count_value BIGINT DEFAULT 0,
                additional_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interchange_control_number ON edi_interchanges(interchange_control_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interchange_date ON edi_interchanges(interchange_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_functional_group_number ON edi_functional_groups(group_control_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_type ON edi_transactions(transaction_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transaction_control_number ON edi_transactions(transaction_control_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_segment_id ON edi_segments(segment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_segment_position ON edi_segments(segment_position)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edi_statistics_date ON edi_statistics(statistic_date)")

        self.conn.commit()
        cursor.close()

    def store_edi_x12_transaction(self, interchange_data: dict, functional_group_data: dict, transaction_data: dict) -> str:
        """存储EDI X12交易集 - 增强错误处理"""
        # 输入验证
        if not isinstance(interchange_data, dict):
            raise TypeError(f"Interchange data must be a dictionary, got {type(interchange_data)}")

        if not interchange_data:
            raise ValueError("Interchange data cannot be empty")

        if "isa" not in interchange_data:
            raise ValueError("Interchange data missing 'isa' section")

        if not isinstance(functional_group_data, dict):
            raise TypeError(f"Functional group data must be a dictionary, got {type(functional_group_data)}")

        if "gs" not in functional_group_data:
            raise ValueError("Functional group data missing 'gs' section")

        if not isinstance(transaction_data, dict):
            raise TypeError(f"Transaction data must be a dictionary, got {type(transaction_data)}")

        if not transaction_data:
            raise ValueError("Transaction data cannot be empty")

        if "ST" not in transaction_data:
            raise ValueError("Transaction data missing 'ST' segment")

        # 验证交换控制号
        interchange_control_number = interchange_data.get("isa", {}).get("interchange_control_number")
        if not interchange_control_number:
            raise ValueError("Interchange control number is required")

        if not isinstance(interchange_control_number, str):
            raise TypeError(f"Interchange control number must be a string, got {type(interchange_control_number)}")

        if len(interchange_control_number) > 14:
            raise ValueError(f"Interchange control number too long: {len(interchange_control_number)} (max 14)")

        # 验证功能组控制号
        group_control_number = functional_group_data.get("gs", {}).get("group_control_number")
        if not group_control_number:
            raise ValueError("Group control number is required")

        if len(str(group_control_number)) > 9:
            raise ValueError(f"Group control number too long: {len(str(group_control_number))} (max 9)")

        # 验证交易集控制号
        transaction_control_number = transaction_data.get("ST", {}).get("transaction_set_control_number")
        if not transaction_control_number:
            raise ValueError("Transaction set control number is required")

        if len(str(transaction_control_number)) > 14:
            raise ValueError(f"Transaction set control number too long: {len(str(transaction_control_number))} (max 14)")

        try:
            cursor = self.conn.cursor()

            # 存储交换
            cursor.execute("""
                INSERT INTO edi_interchanges (
                    interchange_type, interchange_control_number,
                    sender_id, receiver_id, interchange_date, interchange_time
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (interchange_control_number) DO UPDATE SET
                    sender_id = EXCLUDED.sender_id,
                    receiver_id = EXCLUDED.receiver_id
                RETURNING id
            """, (
                "X12",
                interchange_control_number,
                interchange_data.get("isa", {}).get("interchange_sender_id"),
                interchange_data.get("isa", {}).get("interchange_receiver_id"),
                parse_date(interchange_data.get("isa", {}).get("interchange_date")),
                parse_time(interchange_data.get("isa", {}).get("interchange_time"))
            ))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Failed to store interchange")

            interchange_id = result[0]

            # 存储功能组
            cursor.execute("""
                INSERT INTO edi_functional_groups (
                    interchange_id, functional_identifier_code,
                    group_control_number, sender_code, receiver_code, date, time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                interchange_id,
                functional_group_data.get("gs", {}).get("functional_identifier_code"),
                group_control_number,
                functional_group_data.get("gs", {}).get("application_sender_code"),
                functional_group_data.get("gs", {}).get("application_receiver_code"),
                parse_date(functional_group_data.get("gs", {}).get("date")),
                parse_time(functional_group_data.get("gs", {}).get("time"))
            ))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Failed to store functional group")

            functional_group_id = result[0]

            # 存储交易集
            cursor.execute("""
                INSERT INTO edi_transactions (
                    functional_group_id, transaction_type,
                    transaction_set_id, transaction_control_number, message_data
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                functional_group_id,
                "X12",
                transaction_data.get("ST", {}).get("transaction_set_identifier_code"),
                transaction_control_number,
                json.dumps(transaction_data)
            ))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Failed to store transaction")

            transaction_id = result[0]

            # 存储段
            segment_position = 1
            for segment_id, segment_data in transaction_data.items():
                if segment_id not in ["ST", "SE"]:  # 跳过头尾段
                    if not isinstance(segment_id, str):
                        raise TypeError(f"Segment ID must be a string, got {type(segment_id)}")

                    if len(segment_id) > 3:
                        raise ValueError(f"Segment ID too long: {len(segment_id)} (max 3)")

                    cursor.execute("""
                        INSERT INTO edi_segments (
                            transaction_id, segment_id, segment_position, segment_data
                        ) VALUES (%s, %s, %s, %s)
                    """, (transaction_id, segment_id, segment_position, json.dumps(segment_data)))
                    segment_position += 1

            self.conn.commit()
            cursor.close()
            logger.info(f"Stored EDI X12 transaction: {transaction_control_number}")
            return str(transaction_id)

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing EDI X12 transaction: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate control number or constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing EDI X12 transaction: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing EDI X12 transaction: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store EDI X12 transaction: {e}") from e

    def store_edifact_message(self, interchange_data: dict, message_data: dict) -> str:
        """存储EDIFACT消息 - 增强错误处理"""
        # 输入验证
        if not isinstance(interchange_data, dict):
            raise TypeError(f"Interchange data must be a dictionary, got {type(interchange_data)}")

        if not interchange_data:
            raise ValueError("Interchange data cannot be empty")

        if "UNB" not in interchange_data:
            raise ValueError("Interchange data missing 'UNB' segment")

        if not isinstance(message_data, dict):
            raise TypeError(f"Message data must be a dictionary, got {type(message_data)}")

        if not message_data:
            raise ValueError("Message data cannot be empty")

        if "UNH" not in message_data:
            raise ValueError("Message data missing 'UNH' segment")

        # 验证交换控制引用
        interchange_control_reference = interchange_data.get("UNB", {}).get("interchange_control_reference")
        if not interchange_control_reference:
            raise ValueError("Interchange control reference is required")

        if not isinstance(interchange_control_reference, str):
            raise TypeError(f"Interchange control reference must be a string, got {type(interchange_control_reference)}")

        if len(interchange_control_reference) > 14:
            raise ValueError(f"Interchange control reference too long: {len(interchange_control_reference)} (max 14)")

        # 验证消息引用号
        message_reference_number = message_data.get("UNH", {}).get("message_reference_number")
        if not message_reference_number:
            raise ValueError("Message reference number is required")

        try:
            cursor = self.conn.cursor()

            # 存储交换
            cursor.execute("""
                INSERT INTO edi_interchanges (
                    interchange_type, interchange_control_number,
                    sender_id, receiver_id, interchange_date, interchange_time
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (interchange_control_number) DO UPDATE SET
                    sender_id = EXCLUDED.sender_id,
                    receiver_id = EXCLUDED.receiver_id
                RETURNING id
            """, (
                "EDIFACT",
                interchange_control_reference,
                interchange_data.get("UNB", {}).get("sender_identification"),
                interchange_data.get("UNB", {}).get("recipient_identification"),
                parse_date(interchange_data.get("UNB", {}).get("date_of_preparation")),
                parse_time(interchange_data.get("UNB", {}).get("time_of_preparation"))
            ))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Failed to store interchange")

            interchange_id = result[0]

            # 存储功能组（EDIFACT中为消息）
            cursor.execute("""
                INSERT INTO edi_functional_groups (
                    interchange_id, group_control_number
                ) VALUES (%s, %s)
                RETURNING id
            """, (
                interchange_id,
                message_reference_number
            ))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Failed to store functional group")

            functional_group_id = result[0]

            # 存储消息
            cursor.execute("""
                INSERT INTO edi_transactions (
                    functional_group_id, transaction_type,
                    message_type, transaction_control_number, message_data
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                functional_group_id,
                "EDIFACT",
                message_data.get("UNH", {}).get("message_type"),
                message_reference_number,
                json.dumps(message_data)
            ))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Failed to store transaction")

            transaction_id = result[0]

            self.conn.commit()
            cursor.close()
            logger.info(f"Stored EDIFACT message: {message_reference_number}")
            return str(transaction_id)

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error storing EDIFACT message: {e}")
            self.conn.rollback()
            raise ValueError(f"Duplicate control number or constraint violation: {e}") from e
        except psycopg2.Error as e:
            logger.error(f"Database error storing EDIFACT message: {e}")
            self.conn.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error storing EDIFACT message: {e}", exc_info=True)
            self.conn.rollback()
            raise RuntimeError(f"Failed to store EDIFACT message: {e}") from e

    def query_transactions_by_type(self, transaction_type: str, start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[dict]:
        """根据交易类型查询交易集"""
        cursor = self.conn.cursor()
        query = """
            SELECT t.*, fg.group_control_number, i.interchange_control_number
            FROM edi_transactions t
            INNER JOIN edi_functional_groups fg ON t.functional_group_id = fg.id
            INNER JOIN edi_interchanges i ON fg.interchange_id = i.id
            WHERE t.transaction_type = %s
        """
        params = [transaction_type]

        if start_date:
            query += " AND i.interchange_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND i.interchange_date <= %s"
            params.append(end_date)

        query += " ORDER BY i.interchange_date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
```

---

### 5.2 EDI数据分析查询

**查询示例**：

```python
# 查询EDI交易统计
def query_edi_statistics(storage: EDIStorage, start_date: datetime, end_date: datetime):
    """查询EDI交易统计"""
    cursor = storage.conn.cursor()
    cursor.execute("""
        SELECT
            t.transaction_type,
            t.transaction_set_id,
            COUNT(*) as transaction_count,
            COUNT(DISTINCT i.sender_id) as sender_count,
            COUNT(DISTINCT i.receiver_id) as receiver_count
        FROM edi_transactions t
        INNER JOIN edi_functional_groups fg ON t.functional_group_id = fg.id
        INNER JOIN edi_interchanges i ON fg.interchange_id = i.id
        WHERE i.interchange_date BETWEEN %s AND %s
        GROUP BY t.transaction_type, t.transaction_set_id
        ORDER BY transaction_count DESC
    """, (start_date, end_date))
    return cursor.fetchall()

# 查询订单处理流程
def query_order_processing_flow(storage: EDIStorage, order_number: str):
    """查询订单处理流程"""
    cursor = storage.conn.cursor()
    cursor.execute("""
        SELECT
            t.transaction_type,
            t.transaction_set_id,
            t.message_data->>'BEG'->>'purchase_order_number' as order_number,
            i.interchange_date,
            i.sender_id,
            i.receiver_id
        FROM edi_transactions t
        INNER JOIN edi_functional_groups fg ON t.functional_group_id = fg.id
        INNER JOIN edi_interchanges i ON fg.interchange_id = i.id
        WHERE t.message_data::text LIKE %s
        ORDER BY i.interchange_date
    """, (f'%{order_number}%',))
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
