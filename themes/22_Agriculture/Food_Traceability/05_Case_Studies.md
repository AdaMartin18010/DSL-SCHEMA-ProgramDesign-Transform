# 食品溯源Schema实践案例

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

本文档提供食品溯源Schema在实际应用中的完整实践案例，涵盖从农田到餐桌的全链条溯源管理，包括种植、加工、仓储、物流、销售等环节的数据追踪。

---

## 2. 企业背景

### 2.1 企业概况

**企业名称**：食安链溯源科技有限公司（虚构案例企业）

**企业规模**：
- 服务食品企业：300+家
- 溯源产品种类：500+种
- 年溯源数据量：10亿条
- 年营业额：1.2亿元人民币

---

## 3. 业务痛点与目标

### 3.1 五大业务痛点

| 序号 | 痛点 | 具体表现 | 影响程度 |
|------|------|----------|----------|
| 1 | **信息不透明** | 消费者无法了解食品来源 | 高 |
| 2 | **数据易篡改** | 传统纸质记录可随意修改 | 高 |
| 3 | **召回效率低** | 问题食品召回范围难确定 | 高 |
| 4 | **监管困难** | 监管部门难以实时掌握 | 中 |
| 5 | **品牌信任度** | 食品安全事件频发影响信任 | 中 |

### 3.2 五大业务目标

| 序号 | 目标 | 具体指标 | 完成期限 |
|------|------|----------|----------|
| 1 | **全程可追溯** | 覆盖100%产品 | 12个月 |
| 2 | **数据防篡改** | 区块链存证，不可篡改 | 9个月 |
| 3 | **秒级查询** | 溯源查询<3秒 | 6个月 |
| 4 | **精准召回** | 召回范围缩小90% | 12个月 |
| 5 | **消费者信任** | 品牌信任度提升50% | 24个月 |

---

## 4. 技术挑战

1. **多环节数据整合**：种植、加工、物流等多环节数据格式不一
2. **区块链性能**：高频数据上链的性能瓶颈
3. **二维码安全**：防伪防复制技术
4. **数据隐私保护**：商业机密与消费者知情权平衡
5. **跨境溯源**：进出口食品的国际标准对接

---

## 5. 解决方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层                                    │
│  消费者查询  企业后台  监管平台  数据分析                     │
├─────────────────────────────────────────────────────────────┤
│                    服务层                                    │
│  溯源服务  区块链服务  二维码服务  告警服务                   │
├─────────────────────────────────────────────────────────────┤
│                    数据层                                    │
│  溯源数据库  区块链  文件存储  缓存                           │
├─────────────────────────────────────────────────────────────┤
│                    接入层                                    │
│  种植端  加工端  仓储端  物流端  销售端                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 完整实现代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
食品溯源Schema实践案例
企业：食安链溯源科技有限公司
"""

import json
import uuid
import hashlib
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TraceabilityStage(Enum):
    """溯源环节"""
    PLANTING = "种植"
    HARVESTING = "采收"
    PROCESSING = "加工"
    PACKAGING = "包装"
    STORAGE = "仓储"
    TRANSPORT = "运输"
    DISTRIBUTION = "分销"
    RETAIL = "零售"


class ProductCategory(Enum):
    """产品类别"""
    VEGETABLES = "蔬菜"
    FRUITS = "水果"
    GRAINS = "粮油"
    MEAT = "肉类"
    DAIRY = "乳制品"
    AQUATIC = "水产"
    PROCESSED = "加工食品"


@dataclass
class Producer:
    """生产者"""
    producer_id: str
    name: str
    type: str  # 农户、合作社、企业
    address: str
    contact: str
    license_number: str
    certification: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "producer_id": self.producer_id,
            "name": self.name,
            "type": self.type,
            "address": self.address,
            "contact": self.contact,
            "license_number": self.license_number,
            "certification": self.certification
        }


@dataclass
class TraceabilityEvent:
    """溯源事件"""
    event_id: str
    product_id: str
    stage: TraceabilityStage
    timestamp: datetime
    location: str
    operator: str
    operation: str
    details: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    blockchain_tx: Optional[str] = None
    
    def calculate_hash(self) -> str:
        """计算事件哈希"""
        data = f"{self.event_id}:{self.product_id}:{self.timestamp}:{self.operation}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "product_id": self.product_id,
            "stage": self.stage.value,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "operator": self.operator,
            "operation": self.operation,
            "details": self.details,
            "attachments": self.attachments,
            "blockchain_tx": self.blockchain_tx,
            "hash": self.calculate_hash()
        }


@dataclass
class Product:
    """产品"""
    product_id: str
    trace_code: str  # 追溯码
    name: str
    category: ProductCategory
    batch_number: str
    production_date: date
    shelf_life_days: int
    producer: Producer
    specifications: str = ""
    storage_conditions: str = ""
    qr_code: str = ""
    
    def generate_qr_code(self) -> str:
        """生成二维码内容"""
        return f"https://trace.example.com/{self.trace_code}"
    
    def __post_init__(self):
        if not self.qr_code:
            self.qr_code = self.generate_qr_code()
    
    def to_dict(self) -> Dict:
        return {
            "product_id": self.product_id,
            "trace_code": self.trace_code,
            "name": self.name,
            "category": self.category.value,
            "batch_number": self.batch_number,
            "production_date": self.production_date.isoformat(),
            "shelf_life_days": self.shelf_life_days,
            "producer": self.producer.to_dict(),
            "specifications": self.specifications,
            "storage_conditions": self.storage_conditions,
            "qr_code": self.qr_code
        }


@dataclass
class QualityTest:
    """质量检测"""
    test_id: str
    product_id: str
    test_type: str
    test_date: date
    test_items: List[Dict]
    overall_result: str  # 合格/不合格
    tester: str
    certificate_url: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "product_id": self.product_id,
            "test_type": self.test_type,
            "test_date": self.test_date.isoformat(),
            "test_items": self.test_items,
            "overall_result": self.overall_result,
            "tester": self.tester,
            "certificate_url": self.certificate_url
        }


class BlockchainLedger:
    """区块链账本（简化版）"""
    
    def __init__(self):
        self.blocks: List[Dict] = []
        self.pending_transactions: List[Dict] = []
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """创建创世区块"""
        genesis = {
            "index": 0,
            "timestamp": datetime.now().isoformat(),
            "data": "Genesis Block",
            "previous_hash": "0" * 64,
            "hash": self._calculate_hash(0, "0" * 64, "Genesis Block")
        }
        self.blocks.append(genesis)
    
    def _calculate_hash(self, index: int, previous_hash: str, data: str) -> str:
        """计算区块哈希"""
        block_string = f"{index}{previous_hash}{data}{datetime.now().isoformat()}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def add_transaction(self, event: TraceabilityEvent):
        """添加交易"""
        transaction = {
            "event_id": event.event_id,
            "product_id": event.product_id,
            "hash": event.calculate_hash(),
            "timestamp": datetime.now().isoformat()
        }
        self.pending_transactions.append(transaction)
        
        # 简化：每个交易直接打包成区块
        return self._mine_block(transaction)
    
    def _mine_block(self, transaction: Dict) -> str:
        """打包区块（简化挖矿）"""
        previous_block = self.blocks[-1]
        new_block = {
            "index": len(self.blocks),
            "timestamp": datetime.now().isoformat(),
            "data": transaction,
            "previous_hash": previous_block["hash"],
            "hash": self._calculate_hash(len(self.blocks), previous_block["hash"], json.dumps(transaction))
        }
        self.blocks.append(new_block)
        return new_block["hash"]
    
    def verify_chain(self) -> bool:
        """验证区块链完整性"""
        for i in range(1, len(self.blocks)):
            current = self.blocks[i]
            previous = self.blocks[i - 1]
            
            if current["previous_hash"] != previous["hash"]:
                return False
            
            if current["hash"] != self._calculate_hash(
                current["index"], current["previous_hash"], 
                json.dumps(current["data"])
            ):
                return False
        
        return True


class TraceabilitySystem:
    """溯源系统"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.events: Dict[str, List[TraceabilityEvent]] = {}
        self.quality_tests: Dict[str, List[QualityTest]] = {}
        self.blockchain = BlockchainLedger()
        self.producers: Dict[str, Producer] = {}
    
    def register_producer(self, producer: Producer):
        """注册生产者"""
        self.producers[producer.producer_id] = producer
        logger.info(f"Registered producer: {producer.name}")
    
    def register_product(self, product: Product):
        """注册产品"""
        self.products[product.product_id] = product
        self.events[product.product_id] = []
        self.quality_tests[product.product_id] = []
        
        # 记录上链
        genesis_event = TraceabilityEvent(
            event_id=str(uuid.uuid4()),
            product_id=product.product_id,
            stage=TraceabilityStage.PLANTING,
            timestamp=datetime.now(),
            location=product.producer.address,
            operator=product.producer.name,
            operation="产品注册"
        )
        tx_hash = self.blockchain.add_transaction(genesis_event)
        genesis_event.blockchain_tx = tx_hash
        self.events[product.product_id].append(genesis_event)
        
        logger.info(f"Registered product: {product.name} ({product.trace_code})")
        return product
    
    def record_event(self, event: TraceabilityEvent):
        """记录溯源事件"""
        if event.product_id not in self.events:
            raise ValueError(f"Product {event.product_id} not found")
        
        # 上链存证
        tx_hash = self.blockchain.add_transaction(event)
        event.blockchain_tx = tx_hash
        
        self.events[event.product_id].append(event)
        logger.info(f"Recorded event: {event.operation} for {event.product_id}")
        return event
    
    def add_quality_test(self, test: QualityTest):
        """添加质检记录"""
        if test.product_id not in self.quality_tests:
            raise ValueError(f"Product {test.product_id} not found")
        
        self.quality_tests[test.product_id].append(test)
        
        # 记录质检事件
        event = TraceabilityEvent(
            event_id=str(uuid.uuid4()),
            product_id=test.product_id,
            stage=TraceabilityStage.PROCESSING,
            timestamp=datetime.combine(test.test_date, datetime.min.time()),
            location="检测中心",
            operator=test.tester,
            operation=f"质量检测:{test.test_type}",
            details={"result": test.overall_result, "test_id": test.test_id}
        )
        self.record_event(event)
        
        logger.info(f"Added quality test: {test.test_id}")
    
    def trace_product(self, trace_code: str) -> Optional[Dict]:
        """追溯产品全链路"""
        product = next((p for p in self.products.values() if p.trace_code == trace_code), None)
        if not product:
            return None
        
        events = self.events.get(product.product_id, [])
        tests = self.quality_tests.get(product.product_id, [])
        
        return {
            "product": product.to_dict(),
            "trace_history": [e.to_dict() for e in sorted(events, key=lambda x: x.timestamp)],
            "quality_tests": [t.to_dict() for t in tests],
            "total_events": len(events),
            "blockchain_verified": self.blockchain.verify_chain()
        }
    
    def quick_query(self, trace_code: str) -> Dict:
        """快速查询（供消费者扫码）"""
        trace_result = self.trace_product(trace_code)
        if not trace_result:
            return {"error": "Product not found"}
        
        product = trace_result["product"]
        events = trace_result["trace_history"]
        
        # 提取关键信息
        stages = list(set(e["stage"] for e in events))
        latest_event = events[-1] if events else None
        
        return {
            "product_name": product["name"],
            "producer": product["producer"]["name"],
            "production_date": product["production_date"],
            "trace_stages": stages,
            "stage_count": len(stages),
            "blockchain_verified": trace_result["blockchain_verified"],
            "latest_status": latest_event["operation"] if latest_event else "Unknown"
        }
    
    def recall_products(self, batch_number: str, reason: str) -> List[str]:
        """召回产品"""
        affected_products = [
            p.product_id for p in self.products.values() 
            if p.batch_number == batch_number
        ]
        
        for product_id in affected_products:
            event = TraceabilityEvent(
                event_id=str(uuid.uuid4()),
                product_id=product_id,
                stage=TraceabilityStage.RETAIL,
                timestamp=datetime.now(),
                location="召回中心",
                operator="系统",
                operation="产品召回",
                details={"reason": reason, "batch": batch_number}
            )
            self.record_event(event)
        
        logger.info(f"Recalled {len(affected_products)} products from batch {batch_number}")
        return affected_products
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "total_products": len(self.products),
            "total_events": sum(len(e) for e in self.events.values()),
            "total_tests": sum(len(t) for t in self.quality_tests.values()),
            "blockchain_blocks": len(self.blockchain.blocks),
            "chain_integrity": self.blockchain.verify_chain(),
            "producers": len(self.producers)
        }


def create_demo_traceability():
    """创建演示溯源系统"""
    system = TraceabilitySystem()
    
    # 注册生产者
    producer = Producer(
        producer_id="PROD-001",
        name="绿源生态农场",
        type="农业合作社",
        address="江苏省南京市溧水区",
        contact="025-12345678",
        license_number="SC12345678901234",
        certification=["有机认证", "绿色食品"]
    )
    system.register_producer(producer)
    
    # 注册产品
    product = Product(
        product_id="PROD-2025-001",
        trace_code="TR20250615001",
        name="有机小番茄",
        category=ProductCategory.VEGETABLES,
        batch_number="B20250615-A",
        production_date=date(2025, 6, 15),
        shelf_life_days=7,
        producer=producer,
        specifications="500g/盒",
        storage_conditions="0-4°C冷藏"
    )
    system.register_product(product)
    
    # 记录溯源事件
    events = [
        TraceabilityEvent(
            event_id=str(uuid.uuid4()),
            product_id=product.product_id,
            stage=TraceabilityStage.PLANTING,
            timestamp=datetime(2025, 3, 1, 8, 0),
            location="1号大棚",
            operator="王农艺师",
            operation="播种定植",
            details={"seed_batch": "S2025-001", "quantity": 500}
        ),
        TraceabilityEvent(
            event_id=str(uuid.uuid4()),
            product_id=product.product_id,
            stage=TraceabilityStage.PLANTING,
            timestamp=datetime(2025, 3, 15, 10, 0),
            location="1号大棚",
            operator="李技术员",
            operation="施肥",
            details={"fertilizer": "有机肥", "amount": "10kg"}
        ),
        TraceabilityEvent(
            event_id=str(uuid.uuid4()),
            product_id=product.product_id,
            stage=TraceabilityStage.HARVESTING,
            timestamp=datetime(2025, 6, 15, 6, 0),
            location="1号大棚",
            operator="张采收员",
            operation="手工采收",
            details={"harvest_weight": 1000, "quality_grade": "一级"}
        ),
        TraceabilityEvent(
            event_id=str(uuid.uuid4()),
            product_id=product.product_id,
            stage=TraceabilityStage.PACKAGING,
            timestamp=datetime(2025, 6, 15, 14, 0),
            location="包装车间",
            operator="刘包装工",
            operation="分拣包装",
            details={"package_type": "精品盒", "weight": 500}
        ),
        TraceabilityEvent(
            event_id=str(uuid.uuid4()),
            product_id=product.product_id,
            stage=TraceabilityStage.TRANSPORT,
            timestamp=datetime(2025, 6, 15, 16, 0),
            location="物流中心",
            operator="陈司机",
            operation="冷链运输",
            details={"vehicle": "沪A12345", "temperature": "4°C"}
        )
    ]
    
    for event in events:
        system.record_event(event)
    
    # 添加质检记录
    test = QualityTest(
        test_id="QT-2025-001",
        product_id=product.product_id,
        test_type="农残检测",
        test_date=date(2025, 6, 15),
        test_items=[
            {"item": "敌敌畏", "result": "未检出", "limit": "0.01mg/kg"},
            {"item": "乐果", "result": "未检出", "limit": "0.01mg/kg"},
            {"item": "氯氰菊酯", "result": "0.002mg/kg", "limit": "0.05mg/kg"}
        ],
        overall_result="合格",
        tester="质检员赵明",
        certificate_url="https://cert.example.com/QT-2025-001"
    )
    system.add_quality_test(test)
    
    return system, product.trace_code


def main():
    """主函数"""
    print("=" * 80)
    print("食品溯源Schema实践案例 - 食安链溯源科技")
    print("=" * 80)
    
    # 创建系统
    print("\n【步骤1】创建溯源系统...")
    system, trace_code = create_demo_traceability()
    print(f"  追溯码: {trace_code}")
    
    # 完整追溯
    print("\n【步骤2】产品全链路追溯...")
    trace_result = system.trace_product(trace_code)
    if trace_result:
        print(f"  产品名称: {trace_result['product']['name']}")
        print(f"  生产者: {trace_result['product']['producer']['name']}")
        print(f"  溯源事件数: {trace_result['total_events']}")
        print(f"  区块链验证: {'通过' if trace_result['blockchain_verified'] else '失败'}")
        print("\n  追溯历程:")
        for event in trace_result['trace_history']:
            print(f"    [{event['stage']}] {event['operation']} - {event['location']}")
    
    # 快速查询（扫码查询）
    print("\n【步骤3】消费者扫码查询...")
    quick_info = system.quick_query(trace_code)
    print(f"  产品: {quick_info['product_name']}")
    print(f"  溯源环节: {quick_info['stage_count']} 个")
    print(f"  当前状态: {quick_info['latest_status']}")
    
    # 质检报告
    print("\n【步骤4】质检报告...")
    if trace_result and trace_result['quality_tests']:
        test = trace_result['quality_tests'][0]
        print(f"  检测类型: {test['test_type']}")
        print(f"  检测结果: {test['overall_result']}")
        print(f"  检测项:")
        for item in test['test_items']:
            print(f"    - {item['item']}: {item['result']} (限值: {item['limit']})")
    
    # 系统统计
    print("\n【步骤5】系统统计...")
    stats = system.get_statistics()
    print(f"  注册产品: {stats['total_products']}")
    print(f"  溯源事件: {stats['total_events']}")
    print(f"  质检记录: {stats['total_tests']}")
    print(f"  区块链区块: {stats['blockchain_blocks']}")
    
    print("\n" + "=" * 80)
    print("食品溯源Schema实践案例执行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
```

---

## 7. 效果评估与ROI分析

### 7.1 关键绩效指标

| 指标 | 实施前 | 实施后 | 改善 |
|------|--------|--------|------|
| 查询响应时间 | 10秒 | 2秒 | -80% |
| 召回范围 | 整批 | 精准到单品 | -90% |
| 消费者信任度 | 60% | 90% | +50% |
| 数据可信度 | 低 | 100%（区块链） | 质变 |

### 7.2 ROI分析

**投资**：¥150万  
**年收益**：¥280万  
**ROI**：187%（3年）

---

**创建时间**：2026-02-15  
**版本**：1.0.0
