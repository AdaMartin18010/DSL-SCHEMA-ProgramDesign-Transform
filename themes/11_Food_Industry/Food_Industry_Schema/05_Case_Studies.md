# 食品行业Schema实践案例

## 📑 目录

- [食品行业Schema实践案例](#食品行业schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：FreshFood集团食品安全追溯系统](#2-案例1freshfood集团食品安全追溯系统)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整实现代码](#26-完整实现代码)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：食品安全全程追溯](#3-案例2食品安全全程追溯)
  - [4. 案例3：食品质量监控](#4-案例3食品质量监控)
  - [5. 案例4：GS1到EPCIS消息转换](#5-案例4gs1到epcis消息转换)
  - [6. 案例5：食品行业数据分析和报表](#6-案例5食品行业数据分析和报表)

---

## 1. 案例概述

本文档提供食品行业Schema在实际应用中的实践案例，涵盖食品追溯、质量监控、召回管理等核心场景。

---

## 2. 案例1：FreshFood集团食品安全追溯系统

### 2.1 企业背景

**FreshFood集团**是全球领先的食品生产和分销企业，年营业额80亿美元，拥有120个生产基地、45个配送中心，产品销往80+国家，SKU超过5,000个。

- **成立时间**：1985年
- **员工规模**：35,000人
- **年产量**：200万吨食品
- **供应商数量**：3,500+原料供应商
- **客户覆盖**：超市、餐饮、电商等20万+客户
- **原系统**：纸质记录为主，电子数据分散，追溯困难

### 2.2 业务痛点

| 序号 | 痛点 | 影响程度 | 业务影响 |
|------|------|----------|----------|
| 1 | **追溯响应慢** | 严重 | 食品安全事件追溯平均需48小时，面临监管处罚 |
| 2 | **召回效率低** | 高 | 产品召回需3-5天，召回率仅60%，剩余40%流入市场 |
| 3 | **质量数据分散** | 高 | 质检数据分散在Excel和纸质记录，无法分析趋势 |
| 4 | **供应商管理难** | 高 | 3,500+供应商资质管理困难，合规风险高 |
| 5 | **保质期管理差** | 中 | 过期损耗率3%，年损失2,400万美元 |

### 2.3 业务目标

| 序号 | 目标 | 当前值 | 目标值 | 时间框架 |
|------|------|--------|--------|----------|
| 1 | 追溯响应时间 | 48小时 | <2小时 | 12个月 |
| 2 | 产品召回率 | 60% | 95% | 12个月 |
| 3 | 质量数据数字化率 | 20% | 95% | 9个月 |
| 4 | 供应商合规率 | 70% | 98% | 12个月 |
| 5 | 过期损耗率 | 3% | <0.5% | 9个月 |

### 2.4 技术挑战

1. **大规模追溯网络**：需追踪5,000+ SKU从农场到餐桌的全链路

2. **多标准兼容**：需支持GS1、EPCIS、GFSI、FSMA等国内外标准

3. **实时数据处理**：日均500万条追溯事件，峰值50万条/小时

4. **全球供应链**：需覆盖35个国家的生产基地和供应商

5. **多语言多币种**：需支持8种语言和15种货币的全球化运营

### 2.5 Schema定义

**食品追溯Schema**：

```dsl
schema FoodTraceability {
  food_product: {
    gtin: String @value("12345678901234") @length(14)
    batch_lot: String @value("LOT-2025-A001")
    serial_number: Optional[String]
    product_name: String @value("Organic Milk 1L")
    category: String @value("Dairy")
    brand: String @value("FreshFood")
    
    production: {
      production_date: Date @value("2025-01-15")
      expiry_date: Date @value("2025-02-15")
      production_facility: {
        gln: String @value("1234567890123")
        name: String @value("Farm A Dairy Plant")
        country: String @value("CN")
      }
      production_line: String @value("LINE-A01")
    }
    
    ingredients: List[Ingredient] {
      ingredient1: {
        name: String @value("Fresh Milk")
        percentage: Decimal @value(98.5)
        supplier: {
          gln: String @value("9876543210987")
          name: String @value("Farm A")
        }
        origin: String @value("CN-Hebei")
      }
      ingredient2: {
        name: String @value("Vitamin D")
        percentage: Decimal @value(1.5)
        supplier: {
          gln: String @value("1111111111111")
          name: String @value("NutriSupp Inc")
        }
      }
    }
  }
  
  trace_events: List[TraceEvent] {
    event1: {
      event_type: Enum { Production, Processing, Packaging, Shipping, Receiving, Retail }
      event_time: DateTime @value("2025-01-15T06:00:00Z")
      location: {
        gln: String @value("1234567890123")
        name: String @value("Farm A Dairy Plant")
      }
      actor: {
        id: String @value("OPER-001")
        name: String @value("张三")
        role: String @value("Production Operator")
      }
      certifications: List[String] @value(["ISO22000", "HACCP"])
    }
    event2: {
      event_type: Enum { QualityCheck }
      event_time: DateTime @value("2025-01-15T08:00:00Z")
      location: {
        gln: String @value("1234567890123")
        name: String @value("Quality Lab")
      }
      quality_data: {
        temperature: Decimal @value(4.0)
        ph_value: Decimal @value(6.7)
        fat_content: Decimal @value(3.5)
        test_result: Enum { Pass, Fail } @value(Pass)
      }
    }
  }
  
  logistics: {
    sscc: String @value("012345678901234567")
    shipper: {
      gln: String @value("1234567890123")
      name: String @value("Farm A Distribution")
    }
    receiver: {
      gln: String @value("2222222222222")
      name: String @value("Metro Supermarket")
    }
    transport: {
      mode: Enum { Truck, Rail, Air, Sea } @value(Truck)
      vehicle_id: String @value("TRUCK-001")
      temperature_controlled: Boolean @value(true)
      temperature_range: {
        min: Decimal @value(2.0)
        max: Decimal @value(6.0)
      }
    }
  }
} @standard("GS1_EPCIS_ISO22005")
```

### 2.6 完整实现代码

```python
"""
FreshFood集团食品安全追溯系统
支持全链路追溯、质量监控、召回管理
"""

import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict


class EventType(Enum):
    """追溯事件类型"""
    PRODUCTION = "production"
    PROCESSING = "processing"
    QUALITY_CHECK = "quality_check"
    PACKAGING = "packaging"
    SHIPPING = "shipping"
    RECEIVING = "receiving"
    STORAGE = "storage"
    RETAIL = "retail"
    SALE = "sale"
    CONSUMPTION = "consumption"


class QualityStatus(Enum):
    """质量状态"""
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"
    QUARANTINE = "QUARANTINE"


class RecallStatus(Enum):
    """召回状态"""
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Location:
    """位置信息"""
    gln: str
    name: str
    address: str = ""
    country: str = ""
    location_type: str = ""  # production, warehouse, retail
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "gln": self.gln,
            "name": self.name,
            "address": self.address,
            "country": self.country,
            "type": self.location_type
        }


@dataclass
class Actor:
    """操作者"""
    actor_id: str
    name: str
    role: str
    organization: str = ""
    certifications: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.actor_id,
            "name": self.name,
            "role": self.role,
            "organization": self.organization,
            "certifications": self.certifications
        }


@dataclass
class QualityData:
    """质量数据"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    ph_value: Optional[float] = None
    fat_content: Optional[float] = None
    protein_content: Optional[float] = None
    bacteria_count: Optional[int] = None
    test_result: QualityStatus = QualityStatus.PENDING
    tester: str = ""
    test_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "ph_value": self.ph_value,
            "fat_content": self.fat_content,
            "protein_content": self.protein_content,
            "bacteria_count": self.bacteria_count,
            "test_result": self.test_result.value,
            "tester": self.tester,
            "test_time": self.test_time.isoformat()
        }
    
    def is_compliant(self) -> bool:
        """检查是否符合标准"""
        if self.test_result == QualityStatus.FAIL:
            return False
        if self.ph_value and not (6.0 <= self.ph_value <= 7.0):
            return False
        if self.bacteria_count and self.bacteria_count > 10000:
            return False
        return True


@dataclass
class TraceEvent:
    """追溯事件"""
    event_id: str
    event_type: EventType
    event_time: datetime
    location: Location
    actor: Actor
    gtin: str
    batch_lot: str
    quantity: int = 1
    unit: str = "EA"
    quality_data: Optional[QualityData] = None
    parent_events: List[str] = field(default_factory=list)
    child_events: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "event_time": self.event_time.isoformat(),
            "location": self.location.to_dict(),
            "actor": self.actor.to_dict(),
            "gtin": self.gtin,
            "batch_lot": self.batch_lot,
            "quantity": self.quantity,
            "unit": self.unit,
            "quality_data": self.quality_data.to_dict() if self.quality_data else None,
            "certifications": self.certifications,
            "notes": self.notes
        }


@dataclass
class FoodProduct:
    """食品产品"""
    gtin: str
    batch_lot: str
    product_name: str
    category: str
    brand: str
    production_date: date
    expiry_date: date
    production_location: Location
    ingredients: List[Dict[str, Any]] = field(default_factory=list)
    
    def days_until_expiry(self) -> int:
        """计算距离过期天数"""
        return (self.expiry_date - date.today()).days
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return date.today() > self.expiry_date
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gtin": self.gtin,
            "batch_lot": self.batch_lot,
            "product_name": self.product_name,
            "category": self.category,
            "brand": self.brand,
            "production_date": self.production_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
            "days_until_expiry": self.days_until_expiry(),
            "is_expired": self.is_expired(),
            "production_location": self.production_location.to_dict(),
            "ingredients": self.ingredients
        }


@dataclass
class Recall:
    """召回记录"""
    recall_id: str
    gtin: str
    batch_lot: str
    reason: str
    status: RecallStatus
    initiated_at: datetime
    initiated_by: str
    affected_quantity: int = 0
    recalled_quantity: int = 0
    trace_events: List[str] = field(default_factory=list)
    
    def get_recall_rate(self) -> float:
        """获取召回率"""
        if self.affected_quantity == 0:
            return 0.0
        return (self.recalled_quantity / self.affected_quantity) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recall_id": self.recall_id,
            "gtin": self.gtin,
            "batch_lot": self.batch_lot,
            "reason": self.reason,
            "status": self.status.value,
            "initiated_at": self.initiated_at.isoformat(),
            "initiated_by": self.initiated_by,
            "affected_quantity": self.affected_quantity,
            "recalled_quantity": self.recalled_quantity,
            "recall_rate": self.get_recall_rate()
        }


class FoodTraceabilitySystem:
    """食品追溯系统"""
    
    def __init__(self):
        self.products: Dict[str, FoodProduct] = {}
        self.events: Dict[str, TraceEvent] = {}
        self.product_events: Dict[str, List[str]] = defaultdict(list)
        self.batch_events: Dict[str, List[str]] = defaultdict(list)
        self.recalls: Dict[str, Recall] = {}
        self.locations: Dict[str, Location] = {}
        
        # 统计
        self.metrics = {
            "total_products": 0,
            "total_events": 0,
            "active_recalls": 0,
            "trace_queries": 0
        }
    
    def register_product(self, product: FoodProduct) -> str:
        """注册产品"""
        product_key = f"{product.gtin}:{product.batch_lot}"
        self.products[product_key] = product
        self.metrics["total_products"] += 1
        return product_key
    
    def add_event(self, event: TraceEvent) -> str:
        """添加追溯事件"""
        if not event.event_id:
            event.event_id = f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        self.events[event.event_id] = event
        
        # 索引
        product_key = f"{event.gtin}:{event.batch_lot}"
        self.product_events[product_key].append(event.event_id)
        self.batch_events[event.batch_lot].append(event.event_id)
        
        self.metrics["total_events"] += 1
        return event.event_id
    
    def get_product_trace(self, gtin: str, batch_lot: str) -> List[TraceEvent]:
        """获取产品追溯链"""
        product_key = f"{gtin}:{batch_lot}"
        event_ids = self.product_events.get(product_key, [])
        events = [self.events[eid] for eid in event_ids]
        events.sort(key=lambda e: e.event_time)
        self.metrics["trace_queries"] += 1
        return events
    
    def trace_forward(self, gtin: str, batch_lot: str) -> Dict[str, Any]:
        """正向追溯"""
        events = self.get_product_trace(gtin, batch_lot)
        
        origin = events[0] if events else None
        current = events[-1] if events else None
        
        return {
            "trace_type": "forward",
            "gtin": gtin,
            "batch_lot": batch_lot,
            "total_events": len(events),
            "origin": origin.to_dict() if origin else None,
            "current_location": current.location.to_dict() if current else None,
            "trace_path": [e.to_dict() for e in events]
        }
    
    def trace_backward(self, gtin: str, batch_lot: str) -> Dict[str, Any]:
        """反向追溯"""
        events = self.get_product_trace(gtin, batch_lot)
        events.reverse()
        
        current = events[0] if events else None
        origin = events[-1] if events else None
        
        return {
            "trace_type": "backward",
            "gtin": gtin,
            "batch_lot": batch_lot,
            "total_events": len(events),
            "current_location": current.location.to_dict() if current else None,
            "origin": origin.to_dict() if origin else None,
            "trace_path": [e.to_dict() for e in events]
        }
    
    def get_expiring_products(self, days: int = 7) -> List[FoodProduct]:
        """获取即将过期产品"""
        expiring = []
        for product in self.products.values():
            if 0 < product.days_until_expiry() <= days:
                expiring.append(product)
        return sorted(expiring, key=lambda p: p.days_until_expiry())
    
    def initiate_recall(self, gtin: str, batch_lot: str, reason: str, 
                       initiated_by: str) -> str:
        """发起召回"""
        recall = Recall(
            recall_id=f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            gtin=gtin,
            batch_lot=batch_lot,
            reason=reason,
            status=RecallStatus.INITIATED,
            initiated_at=datetime.now(),
            initiated_by=initiated_by
        )
        
        # 计算受影响数量
        events = self.get_product_trace(gtin, batch_lot)
        recall.affected_quantity = sum(e.quantity for e in events)
        recall.trace_events = [e.event_id for e in events]
        
        self.recalls[recall.recall_id] = recall
        self.metrics["active_recalls"] += 1
        
        return recall.recall_id
    
    def update_recall_status(self, recall_id: str, status: RecallStatus,
                            recalled_quantity: int = None):
        """更新召回状态"""
        if recall_id in self.recalls:
            recall = self.recalls[recall_id]
            recall.status = status
            if recalled_quantity is not None:
                recall.recalled_quantity = recalled_quantity
            
            if status == RecallStatus.COMPLETED:
                self.metrics["active_recalls"] -= 1
    
    def find_affected_products(self, ingredient_supplier: str, 
                              ingredient_batch: str) -> List[str]:
        """查找受影响产品（原料问题场景）"""
        affected = []
        for product_key, product in self.products.items():
            for ingredient in product.ingredients:
                if (ingredient.get("supplier", {}).get("gln") == ingredient_supplier and
                    ingredient.get("batch") == ingredient_batch):
                    affected.append(product_key)
        return affected
    
    def get_quality_summary(self, gtin: str, batch_lot: str) -> Dict[str, Any]:
        """获取质量摘要"""
        events = self.get_product_trace(gtin, batch_lot)
        
        quality_checks = [e for e in events if e.quality_data]
        passed = sum(1 for e in quality_checks 
                    if e.quality_data.test_result == QualityStatus.PASS)
        failed = sum(1 for e in quality_checks 
                    if e.quality_data.test_result == QualityStatus.FAIL)
        
        avg_temp = None
        temps = [e.quality_data.temperature for e in quality_checks 
                if e.quality_data and e.quality_data.temperature is not None]
        if temps:
            avg_temp = sum(temps) / len(temps)
        
        return {
            "gtin": gtin,
            "batch_lot": batch_lot,
            "total_quality_checks": len(quality_checks),
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(quality_checks) * 100) if quality_checks else 0,
            "average_temperature": avg_temp,
            "all_checks_passed": failed == 0
        }
    
    def get_metrics_report(self) -> Dict[str, Any]:
        """获取指标报告"""
        return {
            **self.metrics,
            "total_products": len(self.products),
            "total_events": len(self.events),
            "total_recalls": len(self.recalls),
            "expiring_7d": len(self.get_expiring_products(7)),
            "expiring_30d": len(self.get_expiring_products(30))
        }


def main():
    """主函数 - 演示"""
    # 创建追溯系统
    system = FoodTraceabilitySystem()
    
    # 创建产品
    production_location = Location(
        gln="1234567890123",
        name="FreshFood Dairy Plant",
        address="Industrial Zone A, Beijing",
        country="CN",
        location_type="production"
    )
    
    product = FoodProduct(
        gtin="12345678901234",
        batch_lot="LOT-2025-A001",
        product_name="Organic Milk 1L",
        category="Dairy",
        brand="FreshFood",
        production_date=date(2025, 1, 15),
        expiry_date=date(2025, 2, 15),
        production_location=production_location,
        ingredients=[
            {
                "name": "Fresh Milk",
                "percentage": 98.5,
                "supplier": {"gln": "9876543210987", "name": "Farm A"},
                "batch": "FARM-001"
            },
            {
                "name": "Vitamin D",
                "percentage": 1.5,
                "supplier": {"gln": "1111111111111", "name": "NutriSupp Inc"}
            }
        ]
    )
    
    product_key = system.register_product(product)
    print(f"注册产品: {product_key}")
    
    # 添加追溯事件
    operator = Actor("OPER-001", "张三", "Production Operator", 
                    "FreshFood Dairy Plant", ["HACCP Certified"])
    
    events = [
        TraceEvent(
            event_id="",
            event_type=EventType.PRODUCTION,
            event_time=datetime(2025, 1, 15, 6, 0, 0),
            location=production_location,
            actor=operator,
            gtin=product.gtin,
            batch_lot=product.batch_lot,
            quantity=1000,
            certifications=["ISO22000", "HACCP"]
        ),
        TraceEvent(
            event_id="",
            event_type=EventType.QUALITY_CHECK,
            event_time=datetime(2025, 1, 15, 8, 0, 0),
            location=production_location,
            actor=Actor("QC-001", "李四", "Quality Inspector"),
            gtin=product.gtin,
            batch_lot=product.batch_lot,
            quality_data=QualityData(
                temperature=4.0,
                ph_value=6.7,
                fat_content=3.5,
                protein_content=3.3,
                bacteria_count=5000,
                test_result=QualityStatus.PASS,
                tester="李四"
            )
        ),
        TraceEvent(
            event_id="",
            event_type=EventType.PACKAGING,
            event_time=datetime(2025, 1, 15, 10, 0, 0),
            location=production_location,
            actor=operator,
            gtin=product.gtin,
            batch_lot=product.batch_lot,
            quantity=1000
        ),
        TraceEvent(
            event_id="",
            event_type=EventType.SHIPPING,
            event_time=datetime(2025, 1, 15, 14, 0, 0),
            location=production_location,
            actor=Actor("LOG-001", "王五", "Logistics Coordinator"),
            gtin=product.gtin,
            batch_lot=product.batch_lot,
            quantity=1000
        )
    ]
    
    for event in events:
        event_id = system.add_event(event)
        print(f"添加事件: {event.event_type.value} - {event_id}")
    
    # 正向追溯
    print("\n=== 正向追溯 ===")
    forward = system.trace_forward(product.gtin, product.batch_lot)
    print(f"总事件数: {forward['total_events']}")
    print(f"当前位置: {forward['current_location']['name']}")
    
    # 质量摘要
    print("\n=== 质量摘要 ===")
    quality = system.get_quality_summary(product.gtin, product.batch_lot)
    print(json.dumps(quality, indent=2))
    
    # 发起召回（模拟）
    recall_id = system.initiate_recall(
        product.gtin,
        product.batch_lot,
        "Detected bacteria above threshold in quality check",
        "Quality Manager"
    )
    print(f"\n发起召回: {recall_id}")
    
    recall = system.recalls[recall_id]
    print(f"受影响数量: {recall.affected_quantity}")
    
    # 系统指标
    print("\n=== 系统指标 ===")
    metrics = system.get_metrics_report()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

#### 性能指标对比

| 指标 | 改造前 | 改造后 | 改善幅度 |
|------|--------|--------|----------|
| 追溯响应时间 | 48小时 | 1.5小时 | -97% |
| 产品召回率 | 60% | 94% | +57% |
| 质量数据数字化率 | 20% | 96% | +76% |
| 供应商合规率 | 70% | 97% | +39% |
| 过期损耗率 | 3% | 0.4% | -87% |

#### ROI计算

**投资成本**（18个月项目周期）：
- 追溯系统开发：1,200万美元
- 硬件基础设施：600万美元
- 供应商培训：200万美元
- **总投资**：2,000万美元

**年度收益**：
- 过期损耗减少：2,000万美元
- 召回效率提升：800万美元
- 监管合规避免：500万美元
- **年度总收益**：3,300万美元

**ROI分析**：
- 投资回收期：7.3个月
- 3年ROI：395%

#### 经验教训

**成功因素**：
1. **供应商协同**：建立供应商门户，自助完成数据录入
2. **自动化采集**：IoT设备自动采集温湿度等数据
3. **区块链存证**：关键数据上链，增强可信度

**挑战与应对**：
1. **中小供应商技术能力**：提供手机APP简化操作
2. **全球标准差异**：建立标准映射库，自动转换
3. **数据量大**：采用分层存储，热点数据SSD，历史数据归档

---

## 3. 案例2：食品安全全程追溯

详见 `04_Transformation.md` 第3章。

## 4. 案例3：食品质量监控

详见 `04_Transformation.md` 第4章。

## 5. 案例4：GS1到EPCIS消息转换

详见 `04_Transformation.md` 第2章。

## 6. 案例5：食品行业数据分析和报表

详见 `04_Transformation.md` 第6章。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
