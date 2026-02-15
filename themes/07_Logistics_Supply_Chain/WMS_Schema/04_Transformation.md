# WMS Schema转换体系

## 📑 目录

- [WMS Schema转换体系](#wms-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
    - [1.2 转换架构](#12-转换架构)
  - [2. 库存同步转换](#2-库存同步转换)
    - [2.1 ERP库存同步](#21-erp库存同步)
    - [2.2 电商平台库存同步](#22-电商平台库存同步)
    - [2.3 多仓库存同步](#23-多仓库存同步)
  - [3. 订单履行转换](#3-订单履行转换)
    - [3.1 电商订单转换](#31-电商订单转换)
    - [3.2 波次分配转换](#32-波次分配转换)
    - [3.3 发货通知转换](#33-发货通知转换)
  - [4. EDI数据转换](#4-edi数据转换)
    - [4.1 940转换](#41-940转换)
    - [4.2 945转换](#42-945转换)
    - [4.3 库存报告转换](#43-库存报告转换)
  - [5. 数据库存储转换](#5-数据库存储转换)
    - [5.1 PostgreSQL数据模型](#51-postgresql数据模型)
    - [5.2 库存事务处理](#52-库存事务处理)
    - [5.3 数据同步机制](#53-数据同步机制)
  - [6. Python实现](#6-python实现)
  - [7. 性能优化](#7-性能优化)

---

## 1. 转换体系概述

### 1.1 转换目标

WMS Schema转换体系支持以下转换场景：

1. **库存同步转换**：与ERP、电商平台、多仓间的库存同步
2. **订单履行转换**：订单导入、波次分配、发货通知
3. **EDI数据转换**：EDI X12、EDIFACT消息的解析与生成
4. **数据库存储转换**：数据持久化和查询优化
5. **条码标签转换**：GS1条码生成和解析

### 1.2 转换架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        WMS转换架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  库存数据  │  │  订单数据  │  │  入库数据  │  │  出库数据  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │              │
│       └─────────────┴─────────────┴─────────────┘              │
│                         │                                       │
│              ┌──────────▼──────────┐                           │
│              │    数据转换引擎      │                           │
│              │   (Data Transformer) │                           │
│              └──────────┬──────────┘                           │
│                         │                                       │
│       ┌─────────────────┼─────────────────┐                    │
│       │                 │                 │                    │
│       ▼                 ▼                 ▼                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │ EDI转换   │    │ 外部系统  │    │ 数据库存储│                 │
│  │ X12/EDIF │◄──►│ ERP/电商  │    │ PostgreSQL│                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 库存同步转换

### 2.1 ERP库存同步

**ERP到WMS库存同步**：

```python
class ERPWMSInventorySync:
    """ERP与WMS库存同步"""
    
    def __init__(self, erp_connection, wms_connection):
        self.erp = erp_connection
        self.wms = wms_connection
    
    def sync_inventory_from_erp(self, sku_list: List[str] = None) -> dict:
        """从ERP同步库存到WMS"""
        results = {
            "synced": 0,
            "created": 0,
            "updated": 0,
            "errors": []
        }
        
        # 从ERP获取库存数据
        erp_inventory = self.erp.get_inventory(sku_list)
        
        for item in erp_inventory:
            try:
                # 转换数据格式
                wms_data = self.convert_erp_to_wms(item)
                
                # 检查WMS中是否已存在
                existing = self.wms.get_inventory_by_sku_location(
                    wms_data["sku"], 
                    wms_data["location_code"]
                )
                
                if existing:
                    # 更新
                    self.wms.update_inventory(existing["inventory_id"], wms_data)
                    results["updated"] += 1
                else:
                    # 新建
                    self.wms.create_inventory(wms_data)
                    results["created"] += 1
                
                results["synced"] += 1
            
            except Exception as e:
                results["errors"].append({
                    "sku": item.get("sku"),
                    "error": str(e)
                })
        
        return results
    
    def convert_erp_to_wms(self, erp_item: dict) -> dict:
        """转换ERP库存格式到WMS格式"""
        return {
            "sku": erp_item["material_code"],
            "sku_name": erp_item["material_name"],
            "location_code": erp_item.get("storage_location", "DEFAULT"),
            "on_hand": erp_item["unrestricted_stock"],
            "allocated": erp_item.get("allocated_stock", 0),
            "quality_status": self.map_quality_status(erp_item.get("stock_status")),
            "batch_number": erp_item.get("batch"),
            "expiration_date": erp_item.get("shelf_life_expiration"),
            "unit_cost": erp_item.get("moving_average_price"),
            "currency": erp_item.get("currency", "USD"),
            "received_date": erp_item.get("goods_receipt_date"),
            "owner_code": erp_item.get("owner", "OWN"),
            "external_reference": erp_item.get("erp_document_number")
        }
    
    def map_quality_status(self, erp_status: str) -> str:
        """映射ERP质量状态到WMS"""
        status_map = {
            " unrestricted": "Good",
            "inspection": "Quarantine",
            "blocked": "Hold",
            "returns": "Damaged"
        }
        return status_map.get(erp_status, "Good")
```

**WMS到ERP库存调整**：

```python
    def sync_adjustments_to_erp(self, adjustments: List[dict]) -> dict:
        """将WMS库存调整同步到ERP"""
        results = {
            "synced": 0,
            "errors": []
        }
        
        for adj in adjustments:
            try:
                # 转换调整数据到ERP格式
                erp_adjustment = {
                    "material_code": adj["sku"],
                    "plant": adj.get("warehouse_code"),
                    "storage_location": adj["location_code"],
                    "movement_type": self.map_movement_type(adj["adjustment_type"]),
                    "quantity": abs(adj["adjustment_quantity"]),
                    "batch": adj.get("batch_number"),
                    "reason": adj.get("reason_code"),
                    "reference": adj["adjustment_number"],
                    "posting_date": datetime.now().date().isoformat()
                }
                
                # 发送到ERP
                self.erp.post_inventory_adjustment(erp_adjustment)
                results["synced"] += 1
            
            except Exception as e:
                results["errors"].append({
                    "adjustment_id": adj.get("adjustment_id"),
                    "error": str(e)
                })
        
        return results
    
    def map_movement_type(self, wms_type: str) -> str:
        """映射WMS移动类型到ERP移动类型"""
        movement_map = {
            "INCREASE": "701",  # 库存差异-增加
            "DECREASE": "702",  # 库存差异-减少
            "DAMAGE": "551",    # 报废
            "SAMPLE": "333",    # 取样
            "SCRAP": "551"      # 报废
        }
        return movement_map.get(wms_type, "701")
```

### 2.2 电商平台库存同步

**多渠道库存同步**：

```python
class EcommerceInventorySync:
    """电商平台库存同步"""
    
    SUPPORTED_PLATFORMS = ["shopify", "amazon", "ebay", "woocommerce", "magento"]
    
    def __init__(self, wms_db):
        self.wms = wms_db
        self.platform_clients = {}
    
    def register_platform(self, platform: str, client):
        """注册平台客户端"""
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        self.platform_clients[platform] = client
    
    def sync_to_all_platforms(self, sku: str) -> dict:
        """同步单个SKU到所有平台"""
        # 获取WMS可用库存
        wms_inventory = self.wms.get_available_inventory(sku)
        available_qty = sum(item["available_quantity"] for item in wms_inventory)
        
        # 计算安全库存
        safety_stock = self.get_safety_stock(sku)
        sellable_qty = max(0, available_qty - safety_stock)
        
        results = {}
        
        for platform, client in self.platform_clients.items():
            try:
                # 获取平台当前库存
                current_qty = client.get_inventory(sku)
                
                if current_qty != sellable_qty:
                    # 更新平台库存
                    client.update_inventory(sku, sellable_qty)
                    results[platform] = {
                        "status": "updated",
                        "old_qty": current_qty,
                        "new_qty": sellable_qty
                    }
                else:
                    results[platform] = {
                        "status": "no_change",
                        "qty": sellable_qty
                    }
            
            except Exception as e:
                results[platform] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def bulk_sync_to_platform(self, platform: str, sku_list: List[str]) -> dict:
        """批量同步到指定平台"""
        if platform not in self.platform_clients:
            raise ValueError(f"Platform not registered: {platform}")
        
        client = self.platform_clients[platform]
        
        # 批量获取WMS库存
        inventory_data = self.wms.get_inventory_for_skus(sku_list)
        
        # 构建批量更新数据
        updates = []
        for sku in sku_list:
            available = sum(
                item["available_quantity"] 
                for item in inventory_data 
                if item["sku"] == sku
            )
            safety = self.get_safety_stock(sku)
            updates.append({
                "sku": sku,
                "quantity": max(0, available - safety)
            })
        
        # 批量更新
        return client.bulk_update_inventory(updates)
    
    def get_safety_stock(self, sku: str) -> int:
        """获取安全库存"""
        # 从配置或算法计算
        return 10  # 默认10件
```

**Shopify库存同步**：

```python
class ShopifyInventoryClient:
    """Shopify库存客户端"""
    
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
    
    def update_inventory(self, sku: str, quantity: int) -> bool:
        """更新Shopify库存"""
        import requests
        
        # 获取inventory_item_id
        product = self._get_product_by_sku(sku)
        if not product:
            return False
        
        inventory_item_id = product["inventory_item_id"]
        location_id = self._get_default_location()
        
        # 更新库存
        url = f"{self.shop_url}/admin/api/2024-01/inventory_levels/set.json"
        payload = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": quantity
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.status_code == 200
    
    def bulk_update_inventory(self, updates: List[dict]) -> dict:
        """批量更新Shopify库存"""
        results = {"success": 0, "failed": 0, "errors": []}
        
        for update in updates:
            try:
                success = self.update_inventory(update["sku"], update["quantity"])
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({"sku": update["sku"], "error": "Update failed"})
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"sku": update["sku"], "error": str(e)})
        
        return results
```

### 2.3 多仓库存同步

**分布式库存同步**：

```python
class MultiWarehouseSync:
    """多仓库库存同步"""
    
    def __init__(self):
        self.warehouses = {}
    
    def register_warehouse(self, warehouse_code: str, connection):
        """注册仓库"""
        self.warehouses[warehouse_code] = connection
    
    def get_network_inventory(self, sku: str) -> dict:
        """获取全网库存"""
        network_inventory = {
            "sku": sku,
            "warehouses": [],
            "total_available": 0,
            "total_on_hand": 0
        }
        
        for code, conn in self.warehouses.items():
            try:
                inventory = conn.get_inventory(sku)
                wh_data = {
                    "warehouse_code": code,
                    "on_hand": inventory["on_hand"],
                    "available": inventory["available"],
                    "allocated": inventory["allocated"],
                    "in_transit_in": inventory.get("in_transit_in", 0),
                    "in_transit_out": inventory.get("in_transit_out", 0)
                }
                network_inventory["warehouses"].append(wh_data)
                network_inventory["total_available"] += wh_data["available"]
                network_inventory["total_on_hand"] += wh_data["on_hand"]
            except Exception as e:
                network_inventory["warehouses"].append({
                    "warehouse_code": code,
                    "error": str(e)
                })
        
        return network_inventory
    
    def transfer_inventory(
        self, 
        sku: str, 
        from_warehouse: str, 
        to_warehouse: str, 
        quantity: int
    ) -> dict:
        """调拨库存"""
        if from_warehouse not in self.warehouses:
            return {"error": f"Source warehouse {from_warehouse} not found"}
        
        if to_warehouse not in self.warehouses:
            return {"error": f"Destination warehouse {to_warehouse} not found"}
        
        source = self.warehouses[from_warehouse]
        dest = self.warehouses[to_warehouse]
        
        # 检查源仓库库存
        source_inv = source.get_inventory(sku)
        if source_inv["available"] < quantity:
            return {"error": "Insufficient inventory at source"}
        
        # 创建调拨单
        transfer = {
            "transfer_number": f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "sku": sku,
            "from_warehouse": from_warehouse,
            "to_warehouse": to_warehouse,
            "quantity": quantity,
            "status": "CREATED"
        }
        
        # 源仓库减库存
        source.reserve_inventory(sku, quantity, transfer["transfer_number"])
        
        # 目标仓库增加在途库存
        dest.add_in_transit(sku, quantity, transfer["transfer_number"])
        
        return transfer
```

---

## 3. 订单履行转换

### 3.1 电商订单转换

**订单格式转换**：

```python
class OrderTransformer:
    """订单转换器"""
    
    def convert_shopify_to_wms(self, shopify_order: dict) -> OutboundOrder:
        """将Shopify订单转换为WMS订单"""
        order = OutboundOrder()
        
        order.order_number = f"SH-{shopify_order['order_number']}"
        order.order_type = "Customer"
        order.priority = PriorityInfo(
            priority_level=5,
            rush_order=shopify_order.get("tags", []).count("rush") > 0
        )
        
        # 客户信息
        shipping = shopify_order["shipping_address"]
        order.customer = CustomerInfo(
            customer_code=f"SHOP-{shopify_order['customer']['id']}",
            customer_name=f"{shipping['first_name']} {shipping['last_name']}",
            customer_type="B2C",
            shipping_address=Address(
                name=f"{shipping['first_name']} {shipping['last_name']}",
                street_address=f"{shipping['address1']} {shipping.get('address2', '')}".strip(),
                city=shipping["city"],
                state_province=shipping["province"],
                postal_code=shipping["zip"],
                country=shipping["country_code"]
            ),
            contact_phone=shipping.get("phone", ""),
            delivery_instructions=shipping.get("delivery_instructions", "")
        )
        
        # 订单明细
        for idx, item in enumerate(shopify_order["line_items"], 1):
            line = OrderLine(
                line_number=idx,
                sku=item["sku"],
                sku_name=item["name"],
                ordered_quantity=item["quantity"],
                uom="EA",
                unit_price=Decimal(str(item["price"])),
                gift_wrap=item.get("gift_wrap", False),
                gift_message=item.get("gift_message", "")
            )
            order.lines.append(line)
        
        # 时间要求
        order.timing = OrderTiming(
            order_date=datetime.fromisoformat(shopify_order["created_at"]),
            requested_ship_date=date.today(),
            service_level=self.map_shipping_method(shopify_order.get("shipping_lines", [{}])[0].get("title", ""))
        )
        
        # 来源
        order.source = OrderSource(
            source_system="Shopify",
            source_order_id=str(shopify_order["id"]),
            channel="Web",
            reference_numbers=[shopify_order.get("name", "")]
        )
        
        return order
    
    def map_shipping_method(self, shipping_title: str) -> str:
        """映射配送方式到服务级别"""
        title_lower = shipping_title.lower()
        if "expedited" in title_lower or "express" in title_lower:
            return "Expedited"
        elif "overnight" in title_lower or "next day" in title_lower:
            return "Next_Day"
        elif "2 day" in title_lower or "two day" in title_lower:
            return "Two_Day"
        return "Standard"
```

### 3.2 波次分配转换

**波次创建与分配**：

```python
class WaveTransformer:
    """波次转换器"""
    
    def create_wave_from_orders(self, orders: List[OutboundOrder], criteria: dict) -> Wave:
        """从订单创建波次"""
        wave = Wave()
        
        wave.wave_number = f"W{datetime.now().strftime('%Y%m%d%H%M%S')}"
        wave.wave_type = "Pick"
        
        # 设置筛选条件
        wave.attributes = WaveAttributes(
            criteria=WaveCriteria(
                order_types=criteria.get("order_types", ["Customer"]),
                priorities=criteria.get("priorities", [3, 4, 5]),
                carriers=criteria.get("carriers", []),
                ship_dates=DateRange(
                    start_date=date.today(),
                    end_date=date.today()
                )
            )
        )
        
        # 添加订单到波次
        for idx, order in enumerate(orders):
            wave_order = WaveOrder(
                order_id=order.order_id,
                order_number=order.order_number,
                sequence=idx + 1,
                added_at=datetime.now()
            )
            wave.orders.append(wave_order)
            
            # 更新订单的波次信息
            order.wave = WaveInfo(
                wave_id=wave.wave_id,
                wave_number=wave.wave_number,
                wave_sequence=idx + 1
            )
        
        # 计算汇总
        wave.summary = WaveSummary(
            total_orders=len(orders),
            total_lines=sum(len(o.lines) for o in orders),
            total_skus=len(set(line.sku for o in orders for line in o.lines)),
            total_quantity=sum(line.ordered_quantity for o in orders for line in o.lines)
        )
        
        # 生成拣货任务
        wave.tasks = self.generate_pick_tasks(wave, orders)
        
        return wave
    
    def generate_pick_tasks(self, wave: Wave, orders: List[OutboundOrder]) -> List[Task]:
        """生成拣货任务"""
        # 按SKU和货位分组
        pick_groups = defaultdict(lambda: {"orders": [], "total_qty": 0})
        
        for order in orders:
            for line in order.lines:
                # 查询库存位置
                inventory = self.get_inventory_locations(line.sku, line.ordered_quantity)
                
                for inv in inventory:
                    key = (line.sku, inv["location_code"])
                    pick_groups[key]["orders"].append({
                        "order_id": order.order_id,
                        "line_number": line.line_number,
                        "quantity": min(line.ordered_quantity, inv["available"])
                    })
                    pick_groups[key]["total_qty"] += min(line.ordered_quantity, inv["available"])
        
        # 创建任务
        tasks = []
        task_num = 1
        
        for (sku, location), data in pick_groups.items():
            task = Task(
                task_number=f"{wave.wave_number}-P{task_num:04d}",
                task_type="Pick",
                priority=PriorityInfo(priority_level=5),
                instructions=TaskInstructions(
                    source=LocationInfo(location_code=location),
                    lines=[
                        TaskLine(
                            line_number=idx + 1,
                            sku=sku,
                            requested_quantity=item["quantity"],
                            uom="EA"
                        )
                        for idx, item in enumerate(data["orders"])
                    ]
                )
            )
            tasks.append(task)
            task_num += 1
        
        return tasks
    
    def get_inventory_locations(self, sku: str, quantity: int) -> List[dict]:
        """获取库存位置"""
        # 查询数据库获取可用库存位置
        return [
            {"location_code": "A-01-01", "available": 100},
            {"location_code": "A-01-02", "available": 50}
        ]
```

### 3.3 发货通知转换

**发货通知生成**：

```python
class ShipmentNotificationTransformer:
    """发货通知转换器"""
    
    def create_shipment_notification(self, order: OutboundOrder) -> dict:
        """创建发货通知"""
        notification = {
            "notification_type": "Shipment",
            "order_number": order.order_number,
            "shipment_number": f"SHP-{order.order_number}",
            "shipment_date": datetime.now().isoformat(),
            
            "carrier": {
                "code": order.shipment.carrier_code,
                "name": order.shipment.carrier_name,
                "service_level": order.shipment.service_level
            },
            
            "tracking": {
                "tracking_numbers": order.shipment.tracking_numbers,
                "tracking_url": self.generate_tracking_url(
                    order.shipment.carrier_code, 
                    order.shipment.tracking_numbers[0] if order.shipment.tracking_numbers else None
                )
            },
            
            "ship_from": {
                "warehouse_code": "WH01",
                "warehouse_name": "Main Distribution Center",
                "address": {
                    "street": "100 Warehouse Blvd",
                    "city": "Distribution City",
                    "state": "DC",
                    "zip": "12345",
                    "country": "US"
                }
            },
            
            "ship_to": {
                "name": order.customer.customer_name,
                "address": order.customer.shipping_address.to_dict()
            },
            
            "packages": [
                {
                    "package_number": pkg.package_number,
                    "tracking_number": pkg.tracking_number,
                    "weight": float(pkg.weight),
                    "dimensions": {
                        "length": pkg.dimensions.length,
                        "width": pkg.dimensions.width,
                        "height": pkg.dimensions.height
                    },
                    "contents": [
                        {
                            "sku": content.sku,
                            "quantity": content.quantity
                        }
                        for content in pkg.contents
                    ]
                }
                for pkg in order.packing.packages
            ],
            
            "items_shipped": [
                {
                    "line_number": line.line_number,
                    "sku": line.sku,
                    "sku_name": line.sku_name,
                    "quantity_shipped": line.shipped_quantity,
                    "quantity_ordered": line.ordered_quantity
                }
                for line in order.lines
            ]
        }
        
        return notification
    
    def generate_tracking_url(self, carrier_code: str, tracking_number: str) -> str:
        """生成追踪URL"""
        carrier_urls = {
            "UPS": "https://www.ups.com/track?tracknum={}",
            "FEDEX": "https://www.fedex.com/apps/fedextrack/?tracknumbers={}",
            "USPS": "https://tools.usps.com/go/TrackConfirmAction?tLabels={}",
            "DHL": "https://www.dhl.com/en/express/tracking.html?AWB={}"
        }
        
        url_template = carrier_urls.get(carrier_code, "")
        return url_template.format(tracking_number) if url_template else ""
```

---

## 4. EDI数据转换

### 4.1 940转换

**940消息解析与生成**：

```python
class X12940Transformer:
    """X12 940转换器"""
    
    def parse(self, x12_message: str) -> WarehouseOrder:
        """解析940消息"""
        segments = x12_message.split('~')
        
        order = WarehouseOrder()
        current_package = None
        
        for segment in segments:
            if not segment.strip():
                continue
            
            elements = segment.split('*')
            segment_id = elements[0]
            
            if segment_id == "W05":
                order.order_number = elements[2] if len(elements) > 2 else ""
                order.reference_number = elements[3] if len(elements) > 3 else ""
            
            elif segment_id == "N1":
                entity_code = elements[1] if len(elements) > 1 else ""
                if entity_code == "ST":
                    order.ship_to = {
                        "name": elements[2] if len(elements) > 2 else "",
                        "code": elements[3] if len(elements) > 3 else ""
                    }
                elif entity_code == "DE":
                    order.sold_to = {
                        "name": elements[2] if len(elements) > 2 else "",
                        "code": elements[3] if len(elements) > 3 else ""
                    }
            
            elif segment_id == "N3":
                if order.ship_to:
                    order.ship_to["address"] = elements[1] if len(elements) > 1 else ""
            
            elif segment_id == "N4":
                if order.ship_to:
                    order.ship_to["city"] = elements[1] if len(elements) > 1 else ""
                    order.ship_to["state"] = elements[2] if len(elements) > 2 else ""
                    order.ship_to["zip"] = elements[3] if len(elements) > 3 else ""
            
            elif segment_id == "G62":
                qualifier = elements[1] if len(elements) > 1 else ""
                if qualifier == "10":  # Requested ship date
                    order.requested_ship_date = elements[2] if len(elements) > 2 else ""
                elif qualifier == "08":  # Requested delivery date
                    order.requested_delivery_date = elements[2] if len(elements) > 2 else ""
            
            elif segment_id == "W01":
                line = OrderLine()
                line.ordered_quantity = int(elements[1]) if len(elements) > 1 else 0
                line.uom = elements[2] if len(elements) > 2 else ""
                line.sku = elements[4] if len(elements) > 4 else ""
                order.lines.append(line)
        
        return order
    
    def generate(self, order: OutboundOrder) -> str:
        """生成940消息"""
        segments = []
        
        # ST段
        control_num = str(random.randint(1000, 9999))
        segments.append(f"ST*940*{control_num}")
        
        # W05段 - 仓库发货单头
        segments.append(f"W05*{order.order_type[0] if order.order_type else 'N'}*{order.order_number}*{order.reference_number or ''}")
        
        # N1段 - 收货方
        if order.customer:
            segments.append(f"N1*ST*{order.customer.customer_name}")
            if order.customer.shipping_address:
                addr = order.customer.shipping_address
                segments.append(f"N3*{addr.street_address}")
                segments.append(f"N4*{addr.city}*{addr.state_province}*{addr.postal_code}*{addr.country}")
        
        # G62段 - 日期
        if order.timing and order.timing.requested_ship_date:
            segments.append(f"G62*10*{order.timing.requested_ship_date.strftime('%Y%m%d')}")
        if order.timing and order.timing.requested_delivery_date:
            segments.append(f"G62*08*{order.timing.requested_delivery_date.strftime('%Y%m%d')}")
        
        # W01段 - 明细
        for line in order.lines:
            segments.append(f"W01*{line.ordered_quantity}*{line.uom}*UP*{line.sku}")
        
        # SE段
        segment_count = len(segments) + 1
        segments.append(f"SE*{segment_count}*{control_num}")
        
        return "~".join(segments) + "~"
```

### 4.2 945转换

**945消息解析与生成**：

```python
class X12945Transformer:
    """X12 945转换器"""
    
    def generate(self, shipment: Shipment) -> str:
        """生成945发货确认"""
        segments = []
        
        # ST段
        control_num = str(random.randint(1000, 9999))
        segments.append(f"ST*945*{control_num}")
        
        # W06段 - 发货信息
        segments.append(
            f"W06*{shipment.shipment_type}*{shipment.shipment_number}*{shipment.order_number}*{shipment.ship_date.strftime('%Y%m%d')}"
        )
        
        # N1段 - 收货方
        segments.append(f"N1*ST*{shipment.ship_to_name}")
        
        # G62段 - 发货日期
        segments.append(f"G62*11*{shipment.ship_date.strftime('%Y%m%d')}")
        
        # W03段 - 汇总
        total_qty = sum(line.shipped_quantity for line in shipment.lines)
        total_weight = shipment.total_weight
        segments.append(f"W03*{total_qty}*EA*G*{total_weight}*LB")
        
        # W04段 - 明细
        for line in shipment.lines:
            segments.append(f"W04*{line.shipped_quantity}*EA*UP*{line.sku}")
        
        # SE段
        segment_count = len(segments) + 1
        segments.append(f"SE*{segment_count}*{control_num}")
        
        return "~".join(segments) + "~"
```

### 4.3 库存报告转换

**库存报告生成**：

```python
class X12846Transformer:
    """X12 846库存报告转换器"""
    
    def generate(self, inventory_list: List[Inventory]) -> str:
        """生成846库存报告"""
        segments = []
        
        # ST段
        control_num = str(random.randint(1000, 9999))
        segments.append(f"ST*846*{control_num}")
        
        # BIA段 - 报告头
        segments.append(f"BIA*00*IB*{datetime.now().strftime('%Y%m%d')}*{control_num}")
        
        # 按SKU分组
        sku_groups = {}
        for inv in inventory_list:
            if inv.sku not in sku_groups:
                sku_groups[inv.sku] = []
            sku_groups[inv.sku].append(inv)
        
        # LIN段 - 明细
        for sku, items in sku_groups.items():
            total_qty = sum(item.available for item in items)
            
            # 商品信息
            segments.append(f"LIN**UP*{sku}")
            
            # 数量
            segments.append(f"QTY*33*{total_qty}")  # 33 = Available quantity
            
            # 货位明细
            for item in items:
                segments.append(f"QTY*97*{item.available}")  # 97 = Quantity in location
                segments.append(f"REF*WH*{item.location_code}")
        
        # CTT段 - 汇总
        segments.append(f"CTT*{len(sku_groups)}")
        
        # SE段
        segment_count = len(segments) + 1
        segments.append(f"SE*{segment_count}*{control_num}")
        
        return "~".join(segments) + "~"
```

---

## 5. 数据库存储转换

### 5.1 PostgreSQL数据模型

```sql
-- 库存事务表
CREATE TABLE inventory_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_number VARCHAR(50) UNIQUE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- RECEIPT, PUTAWAY, PICK, SHIP, ADJUST, MOVE, CYCLE_COUNT
    
    -- 关联单据
    reference_type VARCHAR(20), -- PO, SO, ASN, ORDER, ADJUSTMENT, TRANSFER
    reference_id VARCHAR(50),
    reference_number VARCHAR(50),
    
    -- SKU信息
    sku VARCHAR(50) NOT NULL,
    sku_name VARCHAR(200),
    
    -- 批次信息
    batch_number VARCHAR(50),
    lot_number VARCHAR(50),
    
    -- 数量
    quantity INTEGER NOT NULL,
    uom VARCHAR(10) DEFAULT 'EA',
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('IN', 'OUT')), -- 进出方向
    
    -- 货位
    from_location VARCHAR(50),
    to_location VARCHAR(50),
    
    -- 状态
    transaction_status VARCHAR(20) DEFAULT 'COMPLETED', -- PENDING, COMPLETED, CANCELLED
    
    -- 执行信息
    performed_by VARCHAR(50),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 审计
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- 库存余额历史表
CREATE TABLE inventory_balance_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_date DATE NOT NULL,
    
    sku VARCHAR(50) NOT NULL,
    location_code VARCHAR(50) NOT NULL,
    batch_number VARCHAR(50),
    
    on_hand INTEGER NOT NULL DEFAULT 0,
    allocated INTEGER NOT NULL DEFAULT 0,
    picked INTEGER NOT NULL DEFAULT 0,
    available INTEGER GENERATED ALWAYS AS (on_hand - allocated - picked) STORED,
    
    UNIQUE(snapshot_date, sku, location_code, batch_number)
);

-- 库存移动表
CREATE TABLE inventory_movements (
    movement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    movement_number VARCHAR(50) UNIQUE NOT NULL,
    movement_type VARCHAR(20) NOT NULL, -- REPLENISH, CONSOLIDATE, RELOCATION
    
    sku VARCHAR(50) NOT NULL,
    batch_number VARCHAR(50),
    quantity INTEGER NOT NULL,
    
    from_location VARCHAR(50) NOT NULL,
    to_location VARCHAR(50) NOT NULL,
    
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED
    
    requested_by VARCHAR(50),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_by VARCHAR(50),
    completed_at TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_inv_txn_sku ON inventory_transactions(sku);
CREATE INDEX idx_inv_txn_date ON inventory_transactions(performed_at);
CREATE INDEX idx_inv_txn_ref ON inventory_transactions(reference_type, reference_id);
CREATE INDEX idx_inv_bal_date ON inventory_balance_history(snapshot_date);
CREATE INDEX idx_inv_move_from ON inventory_movements(from_location);
CREATE INDEX idx_inv_move_to ON inventory_movements(to_location);
```

### 5.2 库存事务处理

```python
class InventoryTransactionProcessor:
    """库存事务处理器"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def process_receipt(self, receipt_data: dict) -> dict:
        """处理收货事务"""
        with self.db.transaction():
            # 创建事务记录
            txn = {
                "transaction_number": f"RCPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "transaction_type": "RECEIPT",
                "reference_type": "ASN",
                "reference_id": receipt_data["asn_id"],
                "reference_number": receipt_data["asn_number"],
                "sku": receipt_data["sku"],
                "quantity": receipt_data["quantity"],
                "direction": "IN",
                "to_location": receipt_data["location_code"],
                "performed_by": receipt_data["user_id"]
            }
            
            self.db.insert("inventory_transactions", txn)
            
            # 更新库存
            self._update_inventory(
                sku=receipt_data["sku"],
                location_code=receipt_data["location_code"],
                batch_number=receipt_data.get("batch_number"),
                quantity_change=receipt_data["quantity"]
            )
            
            return {"success": True, "transaction_id": txn["transaction_number"]}
    
    def process_shipment(self, shipment_data: dict) -> dict:
        """处理发货事务"""
        with self.db.transaction():
            for line in shipment_data["lines"]:
                # 创建事务记录
                txn = {
                    "transaction_number": f"SHIP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "transaction_type": "SHIP",
                    "reference_type": "ORDER",
                    "reference_id": shipment_data["order_id"],
                    "reference_number": shipment_data["order_number"],
                    "sku": line["sku"],
                    "quantity": line["quantity"],
                    "direction": "OUT",
                    "from_location": line["location_code"],
                    "performed_by": shipment_data["user_id"]
                }
                
                self.db.insert("inventory_transactions", txn)
                
                # 更新库存
                self._update_inventory(
                    sku=line["sku"],
                    location_code=line["location_code"],
                    batch_number=line.get("batch_number"),
                    quantity_change=-line["quantity"]
                )
            
            return {"success": True}
    
    def _update_inventory(self, sku: str, location_code: str, batch_number: str, quantity_change: int):
        """更新库存"""
        # 查询现有库存
        existing = self.db.query(
            "SELECT * FROM inventory WHERE sku = %s AND location_code = %s AND (batch_number = %s OR (batch_number IS NULL AND %s IS NULL))",
            (sku, location_code, batch_number, batch_number)
        ).fetchone()
        
        if existing:
            # 更新
            new_qty = existing["on_hand"] + quantity_change
            self.db.execute(
                "UPDATE inventory SET on_hand = %s, updated_at = NOW() WHERE inventory_id = %s",
                (new_qty, existing["inventory_id"])
            )
        else:
            # 新建
            self.db.insert("inventory", {
                "sku": sku,
                "location_code": location_code,
                "batch_number": batch_number,
                "on_hand": quantity_change,
                "inventory_status": "Available"
            })
```

### 5.3 数据同步机制

```python
class InventorySyncManager:
    """库存同步管理器"""
    
    def __init__(self):
        self.sync_queue = []
        self.sync_handlers = {}
    
    def register_handler(self, system_type: str, handler):
        """注册同步处理器"""
        self.sync_handlers[system_type] = handler
    
    def queue_sync(self, sync_type: str, data: dict):
        """加入同步队列"""
        self.sync_queue.append({
            "type": sync_type,
            "data": data,
            "created_at": datetime.now(),
            "retry_count": 0
        })
    
    def process_sync_queue(self):
        """处理同步队列"""
        failed_items = []
        
        for item in self.sync_queue:
            try:
                handler = self.sync_handlers.get(item["type"])
                if handler:
                    handler.sync(item["data"])
                else:
                    failed_items.append(item)
            except Exception as e:
                item["error"] = str(e)
                item["retry_count"] += 1
                
                if item["retry_count"] < 3:
                    failed_items.append(item)
                else:
                    # 记录死信
                    self.log_dead_letter(item)
        
        self.sync_queue = failed_items
    
    def log_dead_letter(self, item: dict):
        """记录死信"""
        # 记录到数据库或日志系统
        pass
```

---

## 6. Python实现

```python
# 库存服务类
class InventoryService:
    """库存服务"""
    
    def __init__(self, repository):
        self.repo = repository
    
    def get_available_inventory(self, sku: str) -> int:
        """获取可用库存"""
        inventory = self.repo.get_by_sku(sku)
        return sum(item.available for item in inventory)
    
    def allocate_inventory(self, sku: str, quantity: int, reference: str) -> AllocationResult:
        """分配库存"""
        inventory = self.repo.get_available_by_sku(sku)
        
        allocations = []
        remaining = quantity
        
        for item in inventory:
            if remaining <= 0:
                break
            
            alloc_qty = min(remaining, item.available)
            
            # 更新分配
            item.allocated += alloc_qty
            self.repo.update(item)
            
            allocations.append(AllocationDetail(
                inventory_id=item.inventory_id,
                location_code=item.location_code,
                quantity=alloc_qty
            ))
            
            remaining -= alloc_qty
        
        return AllocationResult(
            allocations=allocations,
            fully_allocated=(remaining == 0),
            shortage=remaining
        )
    
    def deallocate_inventory(self, allocation_id: str):
        """释放分配"""
        allocation = self.repo.get_allocation(allocation_id)
        
        for item in allocation.items:
            inventory = self.repo.get_by_id(item.inventory_id)
            inventory.allocated -= item.quantity
            self.repo.update(inventory)
        
        self.repo.delete_allocation(allocation_id)

# 波次服务类
class WaveService:
    """波次服务"""
    
    def create_wave(self, criteria: WaveCriteria) -> Wave:
        """创建波次"""
        # 查询符合条件的订单
        orders = self.order_repo.get_pending_orders(
            order_types=criteria.order_types,
            priorities=criteria.priorities,
            ship_date_range=(criteria.ship_dates.start_date, criteria.ship_dates.end_date)
        )
        
        # 创建波次
        wave = WaveBuilder().build_wave(orders, criteria)
        
        # 保存
        self.wave_repo.save(wave)
        
        # 更新订单
        for order in orders:
            order.wave_id = wave.wave_id
            order.status = "Released"
            self.order_repo.update(order)
        
        return wave
    
    def release_wave(self, wave_id: str) -> bool:
        """释放波次"""
        wave = self.wave_repo.get_by_id(wave_id)
        
        if wave.status != "Planned":
            return False
        
        # 分配库存
        for order in wave.orders:
            for line in order.lines:
                result = self.inventory_service.allocate_inventory(
                    line.sku, 
                    line.ordered_quantity,
                    f"WAVE-{wave.wave_number}"
                )
                
                if result.fully_allocated:
                    line.allocated_quantity = line.ordered_quantity
                    line.allocated_from = result.allocations
                else:
                    # 处理缺货
                    pass
        
        wave.status = "Released"
        wave.released_at = datetime.now()
        self.wave_repo.update(wave)
        
        return True
```

---

## 7. 性能优化

```python
# 批量处理
class BatchProcessor:
    def process_inventory_updates(self, updates: List[dict], batch_size: int = 1000):
        """批量更新库存"""
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            
            # 构建批量SQL
            values = []
            for update in batch:
                values.append((
                    update["sku"],
                    update["location_code"],
                    update["quantity"]
                ))
            
            # 执行批量更新
            self.db.executemany(
                "UPDATE inventory SET on_hand = on_hand + %s WHERE sku = %s AND location_code = %s",
                values
            )

# 缓存
from functools import lru_cache

class CachedInventoryService:
    @lru_cache(maxsize=1000)
    def get_inventory_by_location(self, location_code: str) -> List[Inventory]:
        """缓存获取库存"""
        return self.repo.get_by_location(location_code)
    
    def invalidate_cache(self, location_code: str):
        """使缓存失效"""
        self.get_inventory_by_location.cache_clear()

# 异步处理
import asyncio

class AsyncInventoryProcessor:
    async def process_async(self, tasks: List[dict]):
        """异步处理库存任务"""
        coroutines = [self.process_task(task) for task in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        return results
    
    async def process_task(self, task: dict):
        """处理单个任务"""
        # 异步处理逻辑
        await asyncio.sleep(0)  # 模拟异步操作
        return {"task_id": task["id"], "status": "completed"}
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
