# OSS/BSS集成Schema实践案例

## 📑 目录

- [1. 案例概述](#1-案例概述)
- [2. 企业背景](#2-企业背景)
- [3. 业务痛点与目标](#3-业务痛点与目标)
- [4. 技术挑战](#4-技术挑战)
- [5. 解决方案架构](#5-解决方案架构)
- [6. 完整实现代码](#6-完整实现代码)
- [7. 效果评估与ROI分析](#7-效果评估与roi分析)

---

## 1. 案例概述

本文档提供OSS（运营支撑系统）与BSS（业务支撑系统）集成Schema实践案例，涵盖服务开通、故障管理、资源调度、服务保障等核心运营场景。

---

## 2. 企业背景

### 2.1 企业概况

**企业名称**：中云通信集团有限公司（虚构案例企业）

**系统规模**：
- OSS系统：服务开通、故障管理、资源管理
- BSS系统：CRM、计费、产品管理
- 日均工单：50万+
- 系统响应时间要求：<100ms

---

## 3. 业务痛点与目标

### 3.1 五大业务痛点

| 序号 | 痛点 | 具体表现 | 影响程度 |
|------|------|----------|----------|
| 1 | **系统割裂** | OSS与BSS数据不同步 | 高 |
| 2 | **开通周期长** | 新业务开通需3-5天 | 高 |
| 3 | **故障响应慢** | 平均修复时间(MTTR)4小时 | 高 |
| 4 | **资源调度难** | 跨域资源协调困难 | 中 |
| 5 | **数据不一致** | 订单状态与资源状态不一致 | 中 |

### 3.2 五大业务目标

| 序号 | 目标 | 具体指标 | 完成期限 |
|------|------|----------|----------|
| 1 | **自动开通** | 业务开通时间<30分钟 | 9个月 |
| 2 | **故障自愈** | 60%故障自动修复 | 12个月 |
| 3 | **端到端可视化** | 全流程状态实时可见 | 6个月 |
| 4 | **资源利用率** | 提升至75% | 18个月 |
| 5 | **数据一致性** | 一致性>99.9% | 9个月 |

---

## 4. 技术挑战

1. **系统解耦**：OSS与BSS的松耦合设计
2. **实时同步**：订单与资源的实时状态同步
3. **事务一致性**：跨系统分布式事务处理
4. **流程编排**：复杂业务场景的流程自动化
5. **事件驱动**：基于事件驱动的系统架构

---

## 5. 解决方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    BSS层                                     │
│  CRM  订单  计费  产品  营销                                 │
├─────────────────────────────────────────────────────────────┤
│                    集成层                                    │
│  ESB  API网关  消息队列  数据同步  流程编排                  │
├─────────────────────────────────────────────────────────────┤
│                    OSS层                                     │
│  开通  故障  资源  性能  优化                                │
├─────────────────────────────────────────────────────────────┤
│                    网络层                                    │
│  SDN控制器  NFV编排  云网协同                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 完整实现代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS/BSS集成Schema实践案例
企业：中云通信集团有限公司
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    """订单状态"""
    CREATED = "已创建"
    VALIDATED = "已校验"
    RESOURCE_CHECKED = "资源已核查"
    PROVISIONING = "开通中"
    ACTIVATED = "已激活"
    COMPLETED = "已完成"
    FAILED = "失败"


class ServiceType(Enum):
    """服务类型"""
    BROADBAND = "宽带开通"
    MOBILE = "移动业务"
    CLOUD = "云服务"
    VPN = "专线VPN"
    IOT = "物联网"


class TicketPriority(Enum):
    """工单优先级"""
    CRITICAL = "紧急"
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class TicketStatus(Enum):
    """工单状态"""
    NEW = "新建"
    ASSIGNED = "已分派"
    IN_PROGRESS = "处理中"
    RESOLVED = "已解决"
    CLOSED = "已关闭"


@dataclass
class ServiceOrder:
    """服务订单"""
    order_id: str
    customer_id: str
    service_type: ServiceType
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # 业务信息
    product_code: str = ""
    product_name: str = ""
    monthly_fee: float = 0.0
    
    # 资源配置
    required_resources: Dict[str, Any] = field(default_factory=dict)
    allocated_resources: List[str] = field(default_factory=list)
    
    # 流程追踪
    workflow_steps: List[Dict] = field(default_factory=list)
    
    def add_step(self, step_name: str, status: str, details: Dict = None):
        """添加流程步骤"""
        self.workflow_steps.append({
            "step": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        })
    
    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "service_type": self.service_type.value,
            "status": self.status.value,
            "product_name": self.product_name,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "workflow_steps": self.workflow_steps
        }


@dataclass
class TroubleTicket:
    """故障工单"""
    ticket_id: str
    title: str
    description: str
    priority: TicketPriority
    service_id: str
    customer_id: str
    status: TicketStatus = TicketStatus.NEW
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    assigned_to: str = ""
    resolution: str = ""
    
    def calculate_mttr(self) -> Optional[float]:
        """计算修复时间（分钟）"""
        if self.resolved_at:
            return (self.resolved_at - self.created_at).total_seconds() / 60
        return None
    
    def to_dict(self) -> Dict:
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "priority": self.priority.value,
            "status": self.status.value,
            "service_id": self.service_id,
            "created_at": self.created_at.isoformat(),
            "mttr_minutes": self.calculate_mttr()
        }


@dataclass
class NetworkResource:
    """网络资源"""
    resource_id: str
    resource_type: str
    location: str
    capacity: float
    available: float
    status: str = "available"
    allocated_to: Optional[str] = None
    
    @property
    def utilization(self) -> float:
        used = self.capacity - self.available
        return (used / self.capacity * 100) if self.capacity > 0 else 0
    
    def allocate(self, amount: float, service_id: str) -> bool:
        """分配资源"""
        if self.available >= amount:
            self.available -= amount
            self.allocated_to = service_id
            self.status = "allocated"
            return True
        return False
    
    def release(self, amount: float):
        """释放资源"""
        self.available = min(self.capacity, self.available + amount)
        if self.available == self.capacity:
            self.status = "available"
            self.allocated_to = None
    
    def to_dict(self) -> Dict:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "location": self.location,
            "capacity": self.capacity,
            "available": self.available,
            "utilization": round(self.utilization, 2),
            "status": self.status
        }


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.event_queue = queue.Queue()
        self.running = False
    
    def subscribe(self, event_type: str, handler: callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event_type: str, event_data: Dict):
        """发布事件"""
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        self.event_queue.put(event)
        
        # 同步通知订阅者
        for handler in self.subscribers.get(event_type, []):
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    def start(self):
        """启动事件处理"""
        self.running = True
        threading.Thread(target=self._process_events, daemon=True).start()
    
    def _process_events(self):
        """处理事件队列"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                logger.info(f"Processed event: {event['type']}")
            except queue.Empty:
                continue


class BSSSystem:
    """BSS系统"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.orders: Dict[str, ServiceOrder] = {}
        self.customers: Dict[str, Dict] = {}
    
    def create_order(self, customer_id: str, service_type: ServiceType, 
                     product_code: str, product_name: str, monthly_fee: float) -> ServiceOrder:
        """创建订单"""
        order = ServiceOrder(
            order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            customer_id=customer_id,
            service_type=service_type,
            product_code=product_code,
            product_name=product_name,
            monthly_fee=monthly_fee
        )
        order.add_step("订单创建", "完成")
        
        self.orders[order.order_id] = order
        
        # 发布订单创建事件
        self.event_bus.publish("ORDER_CREATED", order.to_dict())
        
        logger.info(f"BSS: Created order {order.order_id}")
        return order
    
    def update_order_status(self, order_id: str, status: OrderStatus):
        """更新订单状态"""
        order = self.orders.get(order_id)
        if order:
            order.status = status
            self.event_bus.publish("ORDER_STATUS_CHANGED", {
                "order_id": order_id,
                "status": status.value
            })


class OSSSystem:
    """OSS系统"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.resources: Dict[str, NetworkResource] = {}
        self.tickets: Dict[str, TroubleTicket] = {}
        self.provisioned_services: Dict[str, Dict] = {}
        
        # 订阅BSS事件
        self.event_bus.subscribe("ORDER_CREATED", self._handle_new_order)
    
    def add_resource(self, resource: NetworkResource):
        """添加资源"""
        self.resources[resource.resource_id] = resource
    
    def _handle_new_order(self, order_data: Dict):
        """处理新订单"""
        order_id = order_data["order_id"]
        service_type = order_data["service_type"]
        
        logger.info(f"OSS: Received order {order_id} for provisioning")
        
        # 启动开通流程
        threading.Thread(
            target=self._provision_service,
            args=(order_id, service_type),
            daemon=True
        ).start()
    
    def _provision_service(self, order_id: str, service_type: str):
        """开通服务"""
        import time
        
        # 模拟开通流程
        steps = [
            ("资源核查", 1),
            ("资源分配", 2),
            ("设备配置", 3),
            ("业务激活", 2),
            ("测试验证", 1)
        ]
        
        for step_name, duration in steps:
            time.sleep(duration)  # 模拟处理时间
            logger.info(f"OSS: Order {order_id} - {step_name} completed")
            
            # 分配资源
            if step_name == "资源分配":
                self._allocate_resources(order_id)
        
        # 开通完成
        self.provisioned_services[order_id] = {
            "status": "active",
            "activated_at": datetime.now().isoformat()
        }
        
        # 通知BSS
        self.event_bus.publish("PROVISIONING_COMPLETED", {
            "order_id": order_id,
            "status": "SUCCESS"
        })
        
        logger.info(f"OSS: Order {order_id} provisioning completed")
    
    def _allocate_resources(self, order_id: str) -> List[str]:
        """分配资源"""
        allocated = []
        for resource in self.resources.values():
            if resource.status == "available":
                if resource.allocate(10, order_id):  # 分配10单位
                    allocated.append(resource.resource_id)
                    break
        return allocated
    
    def create_trouble_ticket(self, service_id: str, title: str, 
                              description: str, priority: TicketPriority,
                              customer_id: str) -> TroubleTicket:
        """创建故障工单"""
        ticket = TroubleTicket(
            ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            title=title,
            description=description,
            priority=priority,
            service_id=service_id,
            customer_id=customer_id
        )
        
        self.tickets[ticket.ticket_id] = ticket
        
        # 自动分派
        self._auto_assign_ticket(ticket)
        
        # 紧急故障自动触发修复
        if priority == TicketPriority.CRITICAL:
            self._auto_heal(ticket)
        
        logger.info(f"OSS: Created trouble ticket {ticket.ticket_id}")
        return ticket
    
    def _auto_assign_ticket(self, ticket: TroubleTicket):
        """自动分派工单"""
        # 根据位置和负载分派
        ticket.assigned_to = "AUTO-SYSTEM"
        ticket.status = TicketStatus.ASSIGNED
    
    def _auto_heal(self, ticket: TroubleTicket):
        """自动修复"""
        import time
        
        logger.info(f"OSS: Auto-healing triggered for {ticket.ticket_id}")
        time.sleep(2)  # 模拟修复过程
        
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.now()
        ticket.resolution = "系统自动修复完成"
        
        self.event_bus.publish("TICKET_RESOLVED", ticket.to_dict())
    
    def get_resource_utilization(self) -> Dict:
        """获取资源利用率"""
        total_capacity = sum(r.capacity for r in self.resources.values())
        total_used = sum(r.capacity - r.available for r in self.resources.values())
        
        by_type = {}
        for r in self.resources.values():
            if r.resource_type not in by_type:
                by_type[r.resource_type] = {"capacity": 0, "used": 0}
            by_type[r.resource_type]["capacity"] += r.capacity
            by_type[r.resource_type]["used"] += r.capacity - r.available
        
        return {
            "overall": round(total_used / total_capacity * 100, 2) if total_capacity else 0,
            "by_type": {
                t: round(v["used"] / v["capacity"] * 100, 2) if v["capacity"] else 0
                for t, v in by_type.items()
            }
        }


class OSSBSSIntegration:
    """OSS/BSS集成平台"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.bss = BSSSystem(self.event_bus)
        self.oss = OSSSystem(self.event_bus)
        
        # 订阅OSS事件
        self.event_bus.subscribe("PROVISIONING_COMPLETED", self._handle_provisioning_complete)
        self.event_bus.subscribe("TICKET_RESOLVED", self._handle_ticket_resolved)
    
    def start(self):
        """启动系统"""
        self.event_bus.start()
        logger.info("OSS/BSS Integration platform started")
    
    def _handle_provisioning_complete(self, event_data: Dict):
        """处理开通完成事件"""
        order_id = event_data["order_id"]
        self.bss.update_order_status(order_id, OrderStatus.COMPLETED)
        logger.info(f"Integration: Order {order_id} completed")
    
    def _handle_ticket_resolved(self, event_data: Dict):
        """处理工单解决事件"""
        ticket_id = event_data["ticket_id"]
        mttr = event_data.get("mttr_minutes")
        logger.info(f"Integration: Ticket {ticket_id} resolved, MTTR: {mttr} min")
    
    def get_end_to_end_view(self, order_id: str) -> Optional[Dict]:
        """端到端视图"""
        order = self.bss.orders.get(order_id)
        if not order:
            return None
        
        service = self.oss.provisioned_services.get(order_id, {})
        allocated_resources = [
            r.to_dict() for r in self.oss.resources.values()
            if r.allocated_to == order_id
        ]
        
        return {
            "order": order.to_dict(),
            "provisioning_status": service,
            "allocated_resources": allocated_resources,
            "end_to_end_time": self._calculate_e2e_time(order)
        }
    
    def _calculate_e2e_time(self, order: ServiceOrder) -> Optional[float]:
        """计算端到端时间（分钟）"""
        if order.completed_at:
            return (order.completed_at - order.created_at).total_seconds() / 60
        return None


def create_demo_integration():
    """创建演示集成系统"""
    integration = OSSBSSIntegration()
    
    # 添加网络资源
    resources = [
        NetworkResource("RES-001", "OLT端口", "南京鼓楼", 100, 100),
        NetworkResource("RES-002", "OLT端口", "南京鼓楼", 100, 100),
        NetworkResource("RES-003", "BRAS端口", "南京中心", 1000, 1000),
        NetworkResource("RES-004", "传输带宽", "南京-上海", 10000, 10000),
    ]
    
    for res in resources:
        integration.oss.add_resource(res)
    
    return integration


def main():
    """主函数"""
    print("=" * 80)
    print("OSS/BSS集成Schema实践案例 - 中云通信")
    print("=" * 80)
    
    # 创建集成系统
    print("\n【步骤1】初始化OSS/BSS集成平台...")
    integration = create_demo_integration()
    integration.start()
    
    # BSS创建订单
    print("\n【步骤2】BSS创建服务订单...")
    order = integration.bss.create_order(
        customer_id="C001",
        service_type=ServiceType.BROADBAND,
        product_code="BB-300M",
        product_name="300M宽带",
        monthly_fee=88.0
    )
    print(f"  订单号: {order.order_id}")
    print(f"  产品: {order.product_name}")
    
    # 等待开通完成
    print("\n【步骤3】OSS自动开通服务...")
    import time
    max_wait = 15
    waited = 0
    while waited < max_wait:
        if order.order_id in integration.oss.provisioned_services:
            break
        time.sleep(1)
        waited += 1
        print(f"  等待开通... {waited}s")
    
    # 端到端视图
    print("\n【步骤4】端到端流程视图...")
    e2e_view = integration.get_end_to_end_view(order.order_id)
    if e2e_view:
        print(f"  订单状态: {e2e_view['order']['status']}")
        print(f"  开通状态: {e2e_view['provisioning_status'].get('status', 'N/A')}")
        print(f"  分配资源: {len(e2e_view['allocated_resources'])} 个")
        if e2e_view['end_to_end_time']:
            print(f"  端到端时长: {e2e_view['end_to_end_time']:.1f} 分钟")
    
    # 创建故障工单
    print("\n【步骤5】创建故障工单（自动修复演示）...")
    ticket = integration.oss.create_trouble_ticket(
        service_id=order.order_id,
        title="宽带连接中断",
        description="用户报告无法上网",
        priority=TicketPriority.CRITICAL,
        customer_id="C001"
    )
    print(f"  工单号: {ticket.ticket_id}")
    print(f"  优先级: {ticket.priority.value}")
    
    # 等待自动修复
    time.sleep(3)
    ticket = integration.oss.tickets[ticket.ticket_id]
    print(f"  工单状态: {ticket.status.value}")
    print(f"  修复时间: {ticket.calculate_mttr():.1f} 分钟" if ticket.calculate_mttr() else "  修复中...")
    
    # 资源利用率
    print("\n【步骤6】资源利用率统计...")
    utilization = integration.oss.get_resource_utilization()
    print(f"  整体利用率: {utilization['overall']}%")
    print(f"  按类型: {utilization['by_type']}")
    
    print("\n" + "=" * 80)
    print("OSS/BSS集成Schema实践案例执行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
```

---

## 7. 效果评估与ROI分析

### 7.1 关键绩效指标

| 指标 | 实施前 | 实施后 | 改善 |
|------|--------|--------|------|
| 业务开通时间 | 3-5天 | 15分钟 | -99% |
| MTTR | 4小时 | 45分钟 | -81% |
| 自动修复率 | 10% | 65% | +550% |
| 数据一致性 | 95% | 99.95% | +5% |

### 7.2 ROI分析

**投资**：¥800万  
**年收益**：¥2400万  
**ROI**：200%（3年）

---

**创建时间**：2026-02-15  
**版本**：1.0.0
