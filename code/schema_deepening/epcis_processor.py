"""
EPCIS事件处理器

专注于EPCIS事件处理、解析、查询
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import xml.etree.ElementTree as ET

from .logger import logger
from .exceptions import ProcessingError, ValidationError, ParseError


class EPCISEventType(Enum):
    """EPCIS事件类型"""
    OBJECT_EVENT = "ObjectEvent"
    AGGREGATION_EVENT = "AggregationEvent"
    TRANSACTION_EVENT = "TransactionEvent"
    TRANSFORMATION_EVENT = "TransformationEvent"
    QUANTITY_EVENT = "QuantityEvent"


@dataclass
class EPCISEvent:
    """EPCIS事件"""
    event_id: str
    event_type: EPCISEventType
    event_time: datetime
    record_time: Optional[datetime] = None
    epc_list: List[str] = None
    parent_id: Optional[str] = None
    child_epcs: List[str] = None
    input_epc_list: List[str] = None
    output_epc_list: List[str] = None
    quantity_list: List[Dict[str, Any]] = None
    action: Optional[str] = None
    biz_step: Optional[str] = None
    disposition: Optional[str] = None
    read_point: Optional[Dict[str, Any]] = None
    biz_location: Optional[Dict[str, Any]] = None
    biz_transaction_list: List[Dict[str, Any]] = None
    source_list: List[Dict[str, Any]] = None
    destination_list: List[Dict[str, Any]] = None
    sensor_element_list: List[Dict[str, Any]] = None
    event_data: Dict[str, Any] = None


class EPCISProcessor:
    """
    EPCIS事件处理器
    
    专注于EPCIS事件处理、解析、查询
    """
    
    def __init__(self):
        self.events: Dict[str, EPCISEvent] = {}
        self.epc_index: Dict[str, List[str]] = {}  # EPC到事件ID的索引
        logger.info("EPCISProcessor initialized")
    
    def parse_epcis_xml(self, epcis_xml: str) -> List[EPCISEvent]:
        """
        解析EPCIS XML
        
        Args:
            epcis_xml: EPCIS XML字符串
            
        Returns:
            EPCIS事件列表
        """
        root = ET.fromstring(epcis_xml)
        
        # 查找事件列表
        events = []
        event_list_elem = root.find('.//{urn:epcglobal:epcis:xsd:1}EventList')
        
        if event_list_elem is not None:
            for event_elem in event_list_elem:
                event = self._parse_event_element(event_elem)
                if event:
                    events.append(event)
                    self.events[event.event_id] = event
                    
                    # 更新EPC索引
                    self._update_epc_index(event)
        
        return events
    
    def _parse_event_element(self, event_elem: ET.Element) -> Optional[EPCISEvent]:
        """解析事件元素"""
        # 确定事件类型
        tag = event_elem.tag.split('}')[-1] if '}' in event_elem.tag else event_elem.tag
        
        event_type_mapping = {
            'ObjectEvent': EPCISEventType.OBJECT_EVENT,
            'AggregationEvent': EPCISEventType.AGGREGATION_EVENT,
            'TransactionEvent': EPCISEventType.TRANSACTION_EVENT,
            'TransformationEvent': EPCISEventType.TRANSFORMATION_EVENT,
            'QuantityEvent': EPCISEventType.QUANTITY_EVENT
        }
        
        event_type = event_type_mapping.get(tag)
        if not event_type:
            return None
        
        # 解析事件ID
        event_id = event_elem.get('id') or f"event_{datetime.utcnow().timestamp()}"
        
        # 解析事件时间
        event_time_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}eventTime')
        event_time = datetime.utcnow()
        if event_time_elem is not None and event_time_elem.text:
            try:
                event_time = datetime.fromisoformat(event_time_elem.text.replace('Z', '+00:00'))
            except:
                pass
        
        # 解析EPC列表
        epc_list = []
        epc_list_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}epcList')
        if epc_list_elem is not None:
            for epc_elem in epc_list_elem.findall('.//{urn:epcglobal:epcis:xsd:1}epc'):
                if epc_elem.text:
                    epc_list.append(epc_elem.text)
        
        # 解析其他字段
        action_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}action')
        action = action_elem.text if action_elem is not None else None
        
        biz_step_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}bizStep')
        biz_step = biz_step_elem.text if biz_step_elem is not None else None
        
        disposition_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}disposition')
        disposition = disposition_elem.text if disposition_elem is not None else None
        
        # 解析聚合事件特定字段
        parent_id = None
        child_epcs = []
        if event_type == EPCISEventType.AGGREGATION_EVENT:
            parent_id_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}parentID')
            if parent_id_elem is not None:
                parent_id = parent_id_elem.text
            
            child_epcs_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}childEPCs')
            if child_epcs_elem is not None:
                for child_epc_elem in child_epcs_elem.findall('.//{urn:epcglobal:epcis:xsd:1}epc'):
                    if child_epc_elem.text:
                        child_epcs.append(child_epc_elem.text)
        
        # 解析转换事件特定字段
        input_epc_list = []
        output_epc_list = []
        if event_type == EPCISEventType.TRANSFORMATION_EVENT:
            input_epc_list_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}inputEPCList')
            if input_epc_list_elem is not None:
                for input_epc_elem in input_epc_list_elem.findall('.//{urn:epcglobal:epcis:xsd:1}epc'):
                    if input_epc_elem.text:
                        input_epc_list.append(input_epc_elem.text)
            
            output_epc_list_elem = event_elem.find('.//{urn:epcglobal:epcis:xsd:1}outputEPCList')
            if output_epc_list_elem is not None:
                for output_epc_elem in output_epc_list_elem.findall('.//{urn:epcglobal:epcis:xsd:1}epc'):
                    if output_epc_elem.text:
                        output_epc_list.append(output_epc_elem.text)
        
        event = EPCISEvent(
            event_id=event_id,
            event_type=event_type,
            event_time=event_time,
            epc_list=epc_list,
            parent_id=parent_id,
            child_epcs=child_epcs,
            input_epc_list=input_epc_list,
            output_epc_list=output_epc_list,
            action=action,
            biz_step=biz_step,
            disposition=disposition
        )
        
        return event
    
    def _update_epc_index(self, event: EPCISEvent):
        """更新EPC索引"""
        # 索引EPC列表
        if event.epc_list:
            for epc in event.epc_list:
                if epc not in self.epc_index:
                    self.epc_index[epc] = []
                self.epc_index[epc].append(event.event_id)
        
        # 索引子EPC
        if event.child_epcs:
            for child_epc in event.child_epcs:
                if child_epc not in self.epc_index:
                    self.epc_index[child_epc] = []
                self.epc_index[child_epc].append(event.event_id)
        
        # 索引输入EPC
        if event.input_epc_list:
            for input_epc in event.input_epc_list:
                if input_epc not in self.epc_index:
                    self.epc_index[input_epc] = []
                self.epc_index[input_epc].append(event.event_id)
        
        # 索引输出EPC
        if event.output_epc_list:
            for output_epc in event.output_epc_list:
                if output_epc not in self.epc_index:
                    self.epc_index[output_epc] = []
                self.epc_index[output_epc].append(event.event_id)
    
    def query_events_by_epc(self, epc: str) -> List[EPCISEvent]:
        """
        根据EPC查询事件
        
        Args:
            epc: EPC代码
            
        Returns:
            事件列表
        """
        event_ids = self.epc_index.get(epc, [])
        events = [self.events[eid] for eid in event_ids if eid in self.events]
        
        # 按时间排序
        events.sort(key=lambda e: e.event_time)
        
        return events
    
    def query_events_by_biz_step(self, biz_step: str) -> List[EPCISEvent]:
        """
        根据业务步骤查询事件
        
        Args:
            biz_step: 业务步骤
            
        Returns:
            事件列表
        """
        events = [e for e in self.events.values() if e.biz_step == biz_step]
        events.sort(key=lambda e: e.event_time)
        
        return events
    
    def query_events_by_time_range(self, start_time: datetime,
                                   end_time: datetime) -> List[EPCISEvent]:
        """
        根据时间范围查询事件
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            事件列表
        """
        events = [
            e for e in self.events.values()
            if start_time <= e.event_time <= end_time
        ]
        events.sort(key=lambda e: e.event_time)
        
        return events


def main():
    """主函数 - 示例用法"""
    processor = EPCISProcessor()
    
    # 解析EPCIS XML
    epcis_xml = """
    <epcis:EPCISDocument>
        <epcis:EPCISBody>
            <epcis:EventList>
                <epcis:ObjectEvent>
                    <epcis:eventTime>2024-01-21T10:00:00Z</epcis:eventTime>
                    <epcis:epcList>
                        <epcis:epc>urn:epc:id:sgtin:0614141.107346.20240121</epcis:epc>
                    </epcis:epcList>
                    <epcis:action>OBSERVE</epcis:action>
                    <epcis:bizStep>shipping</epcis:bizStep>
                </epcis:ObjectEvent>
            </epcis:EventList>
        </epcis:EPCISBody>
    </epcis:EPCISDocument>
    """
    
    events = processor.parse_epcis_xml(epcis_xml)
    print(f"解析事件数: {len(events)}")
    
    # 查询事件
    if events:
        epc = events[0].epc_list[0] if events[0].epc_list else None
        if epc:
            related_events = processor.query_events_by_epc(epc)
            print(f"相关事件数: {len(related_events)}")


if __name__ == '__main__':
    main()
