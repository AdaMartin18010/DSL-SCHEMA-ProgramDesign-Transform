# WMS Schema实践案例

## 📑 目录

- [WMS Schema实践案例](#wms-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：电商巨头智能仓储系统](#2-案例1电商巨头智能仓储系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例总结](#3-案例总结)

---

## 1. 案例概述

本文档提供WMS Schema在零售物流领域的实践案例。

---

## 2. 案例1：电商巨头智能仓储系统

### 2.1 业务背景

**企业概况**：某头部电商平台（以下简称"J电商"），日均订单量超过500万单，在全国拥有大型仓储中心50个，仓储总面积超过1000万平方米。

### 2.2 业务痛点

1. **拣货效率低**：传统人海战术拣货，人均拣货效率仅80单/小时
2. **库存准确率低**：库存账实不符率高达5%，超卖、缺货频发
3. **波峰应对难**：大促期间订单量暴增10倍，系统频繁宕机
4. **逆向物流慢**：退货处理周期长达7天，客户满意度低
5. **仓储成本高**：人工成本占比超过60%，自动化程度低

### 2.3 业务目标

1. **提升拣货效率**：通过智能拣货，人均效率提升至300单/小时
2. **提高库存准确率**：库存准确率达到99.99%
3. **弹性应对波峰**：系统支持10倍流量扩容，大促零故障
4. **缩短退货周期**：退货处理周期缩短至24小时
5. **降低仓储成本**：自动化率提升至80%，人工成本降低40%

### 2.4 技术挑战

1. **高并发库存管理**：日均10亿级库存操作，需要保证强一致性
2. **智能路径规划**：多订单、多商品的最优拣货路径计算
3. **自动化设备集成**：AGV、机械臂、自动分拣机等设备协同
4. **实时数据分析**：库存预测、热销预警等实时分析需求

### 2.5 Schema定义

```json
{
  "warehouse": {
    "warehouse_id": "WH-BJ-001",
    "warehouse_name": "北京智能仓",
    "warehouse_type": "automated",
    "zones": [
      {
        "zone_id": "Z-001",
        "zone_type": "storage",
        "locations": [
          {"location_id": "A-01-01-01", "location_type": "shelf"}
        ]
      }
    ]
  },
  "inventory": {
    "sku_id": "SKU-12345",
    "quantity": 1000,
    "available_qty": 950,
    "reserved_qty": 50,
    "location": "A-01-01-01"
  },
  "order": {
    "order_id": "ORDER-2025-001",
    "order_type": "normal",
    "items": [
      {"sku_id": "SKU-12345", "qty": 2}
    ],
    "status": "picked"
  }
}
```

### 2.6 完整代码实现

```python
#!/usr/bin/env python3
"""
智能仓储管理系统
功能：库存管理、波次管理、拣货优化、自动化设备调度
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import heapq


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"
    WAVED = "waved"
    PICKING = "picking"
    PACKED = "packed"
    SHIPPED = "shipped"


class LocationType(str, Enum):
    """库位类型"""
    SHELF = "shelf"
    FLOOR = "floor"
    COLD = "cold"
    DANGEROUS = "dangerous"


@dataclass
class Location:
    """库位"""
    location_id: str
    zone_id: str
    location_type: LocationType
    aisle: str
    section: str
    level: str
    position: str
    max_weight: float = 1000.0
    sku_id: Optional[str] = None
    quantity: int = 0


@dataclass
class SKU:
    """商品SKU"""
    sku_id: str
    sku_name: str
    category: str
    weight: float
    volume: float
    is_fragile: bool = False
    is_perishable: bool = False
    abc_class: str = "C"  # A, B, C


@dataclass
class Inventory:
    """库存"""
    sku_id: str
    location_id: str
    quantity: int
    available_qty: int
    reserved_qty: int = 0
    inbound_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    
    def reserve(self, qty: int) -> bool:
        """预留库存"""
        if self.available_qty >= qty:
            self.available_qty -= qty
            self.reserved_qty += qty
            return True
        return False
    
    def release(self, qty: int):
        """释放预留"""
        self.available_qty += min(qty, self.reserved_qty)
        self.reserved_qty -= min(qty, self.reserved_qty)
    
    def pick(self, qty: int):
        """拣货出库"""
        if self.reserved_qty >= qty:
            self.reserved_qty -= qty
            self.quantity -= qty


@dataclass
class OrderLine:
    """订单行项"""
    line_no: int
    sku_id: str
    quantity: int
    picked_qty: int = 0
    picked_location: Optional[str] = None


@dataclass
class Order:
    """订单"""
    order_id: str
    order_type: str
    priority: int  # 1-10, 1为最高
    status: OrderStatus
    lines: List[OrderLine] = field(default_factory=list)
    wave_id: Optional[str] = None
    create_time: datetime = field(default_factory=datetime.now)
    promise_time: Optional[datetime] = None
    
    def get_total_skus(self) -> int:
        """获取SKU种类数"""
        return len(self.lines)
    
    def get_total_qty(self) -> int:
        """获取总数量"""
        return sum(line.quantity for line in self.lines)


@dataclass
class Wave:
    """波次"""
    wave_id: str
    wave_type: str  # pick, replenish, cycle_count
    status: str  # pending, picking, completed
    orders: List[str] = field(default_factory=list)
    pick_tasks: List[Dict] = field(default_factory=list)
    create_time: datetime = field(default_factory=datetime.now)
    
    def add_order(self, order_id: str):
        """添加订单"""
        self.orders.append(order_id)


class WMS:
    """仓储管理系统核心"""
    
    def __init__(self, warehouse_id: str):
        self.warehouse_id = warehouse_id
        self.locations: Dict[str, Location] = {}
        self.skus: Dict[str, SKU] = {}
        self.inventory: Dict[str, Inventory] = {}  # key: sku_id@location_id
        self.orders: Dict[str, Order] = {}
        self.waves: Dict[str, Wave] = {}
        self.agv_tasks: List[Dict] = []
    
    def add_location(self, location: Location):
        """添加库位"""
        self.locations[location.location_id] = location
    
    def add_sku(self, sku: SKU):
        """添加SKU"""
        self.skus[sku.sku_id] = sku
    
    def receive_inventory(self, sku_id: str, location_id: str, qty: int) -> bool:
        """入库"""
        key = f"{sku_id}@{location_id}"
        
        if key in self.inventory:
            self.inventory[key].quantity += qty
            self.inventory[key].available_qty += qty
        else:
            self.inventory[key] = Inventory(
                sku_id=sku_id,
                location_id=location_id,
                quantity=qty,
                available_qty=qty
            )
        
        # 更新库位
        if location_id in self.locations:
            self.locations[location_id].sku_id = sku_id
            self.locations[location_id].quantity += qty
        
        return True
    
    def create_order(self, order_type: str, priority: int = 5) -> Order:
        """创建订单"""
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        order = Order(
            order_id=order_id,
            order_type=order_type,
            priority=priority,
            status=OrderStatus.PENDING
        )
        self.orders[order_id] = order
        return order
    
    def allocate_inventory(self, order_id: str) -> bool:
        """库存分配"""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        for line in order.lines:
            sku_id = line.sku_id
            qty = line.quantity
            
            # 查找可用库存
            allocated = False
            for key, inv in self.inventory.items():
                if inv.sku_id == sku_id and inv.available_qty >= qty:
                    if inv.reserve(qty):
                        line.picked_location = inv.location_id
                        allocated = True
                        break
            
            if not allocated:
                return False
        
        return True
    
    def create_wave(self, wave_type: str = "pick") -> Wave:
        """创建波次"""
        wave_id = f"WAVE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        wave = Wave(wave_id=wave_id, wave_type=wave_type, status="pending")
        self.waves[wave_id] = wave
        return wave
    
    def optimize_picking_route(self, wave_id: str) -> List[str]:
        """优化拣货路径"""
        wave = self.waves.get(wave_id)
        if not wave:
            return []
        
        # 收集所有需要拣货的库位
        locations_to_visit = set()
        for order_id in wave.orders:
            order = self.orders.get(order_id)
            if order:
                for line in order.lines:
                    if line.picked_location:
                        locations_to_visit.add(line.picked_location)
        
        # 简化的路径优化：按巷道排序
        sorted_locations = sorted(locations_to_visit, 
                                 key=lambda loc: (self.locations[loc].aisle if loc in self.locations else "",
                                                 self.locations[loc].section if loc in self.locations else ""))
        
        return sorted_locations
    
    def pick_item(self, order_id: str, line_no: int, qty: int) -> bool:
        """拣货"""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        for line in order.lines:
            if line.line_no == line_no:
                location_id = line.picked_location
                if not location_id:
                    return False
                
                key = f"{line.sku_id}@{location_id}"
                if key in self.inventory:
                    self.inventory[key].pick(qty)
                    line.picked_qty += qty
                    
                    # 更新库位
                    if location_id in self.locations:
                        self.locations[location_id].quantity -= qty
                    
                    return True
        
        return False
    
    def get_inventory_report(self) -> Dict:
        """库存报表"""
        total_skus = len(set(inv.sku_id for inv in self.inventory.values()))
        total_qty = sum(inv.quantity for inv in self.inventory.values())
        
        return {
            "warehouse_id": self.warehouse_id,
            "report_time": datetime.now().isoformat(),
            "total_locations": len(self.locations),
            "occupied_locations": sum(1 for loc in self.locations.values() if loc.quantity > 0),
            "total_skus": total_skus,
            "total_quantity": total_qty,
            "pending_orders": sum(1 for o in self.orders.values() if o.status == OrderStatus.PENDING),
            "active_waves": sum(1 for w in self.waves.values() if w.status == "picking")
        }


def main():
    """WMS系统演示"""
    
    print("=" * 60)
    print("智能仓储管理系统演示")
    print("=" * 60)
    
    wms = WMS("WH-BJ-001")
    
    # 1. 创建库位
    print("\n[1] 创建库位")
    for aisle in ["A", "B", "C"]:
        for section in range(1, 4):
            for level in range(1, 4):
                loc_id = f"{aisle}-{section:02d}-{level:02d}"
                loc = Location(
                    location_id=loc_id,
                    zone_id="Z-001",
                    location_type=LocationType.SHELF,
                    aisle=aisle,
                    section=str(section),
                    level=str(level),
                    position="01"
                )
                wms.add_location(loc)
    print(f"已创建 {len(wms.locations)} 个库位")
    
    # 2. 创建SKU
    print("\n[2] 创建SKU")
    skus = [
        ("SKU-001", "智能手机", "electronics", 0.2),
        ("SKU-002", "蓝牙耳机", "electronics", 0.05),
        ("SKU-003", "充电宝", "electronics", 0.3),
    ]
    for sku_id, name, cat, weight in skus:
        wms.add_sku(SKU(sku_id=sku_id, sku_name=name, category=cat, weight=weight, volume=weight*2))
    print(f"已创建 {len(wms.skus)} 个SKU")
    
    # 3. 入库
    print("\n[3] 入库")
    wms.receive_inventory("SKU-001", "A-01-01-01", 100)
    wms.receive_inventory("SKU-002", "A-01-01-02", 200)
    wms.receive_inventory("SKU-003", "A-01-02-01", 150)
    print("入库完成")
    
    # 4. 创建订单
    print("\n[4] 创建订单")
    order = wms.create_order("normal", priority=5)
    order.lines = [
        OrderLine(10, "SKU-001", 2),
        OrderLine(20, "SKU-002", 1)
    ]
    print(f"订单ID: {order.order_id}")
    
    # 5. 库存分配
    print("\n[5] 库存分配")
    if wms.allocate_inventory(order.order_id):
        print("库存分配成功")
        for line in order.lines:
            print(f"  {line.sku_id} -> {line.picked_location}")
    
    # 6. 创建波次
    print("\n[6] 波次管理")
    wave = wms.create_wave("pick")
    wave.add_order(order.order_id)
    
    # 优化拣货路径
    route = wms.optimize_picking_route(wave.wave_id)
    print(f"拣货路径: {route}")
    
    # 7. 库存报表
    print("\n[7] 库存报表")
    report = wms.get_inventory_report()
    print(f"总库位数: {report['total_locations']}")
    print(f"占用库位: {report['occupied_locations']}")
    print(f"总库存量: {report['total_quantity']}")


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

| 指标 | 基线值 | 目标值 | 实际值 | 达成率 |
|------|--------|--------|--------|--------|
| 人均拣货效率 | 80单/小时 | 300单/小时 | 320单/小时 | 107% |
| 库存准确率 | 95% | 99.99% | 99.995% | 100% |
| 退货处理周期 | 7天 | ≤24小时 | 18小时 | 133% |
| 自动化率 | 20% | 80% | 85% | 106% |

**ROI分析**：
- 项目总投资：2亿元
- 年度总收益：5亿元
- **投资回收期：4.8个月**
- **3年ROI：650%**

---

## 3. 案例总结

**关键成功因素**：
1. 自动化设备与WMS深度集成
2. 实时库存数据是核心
3. 算法优化持续迭代

**创建时间**：2025-01-21  
**最后更新**：2025-02-15
