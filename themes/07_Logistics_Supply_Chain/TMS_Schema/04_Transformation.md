# TMS Schema转换体系

## 📑 目录

- [TMS Schema转换体系](#tms-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
    - [1.2 转换架构](#12-转换架构)
  - [2. 运输数据转换](#2-运输数据转换)
    - [2.1 订单数据转换](#21-订单数据转换)
    - [2.2 车辆数据转换](#22-车辆数据转换)
    - [2.3 路线数据转换](#23-路线数据转换)
    - [2.4 运费数据转换](#24-运费数据转换)
  - [3. 供应链协同转换](#3-供应链协同转换)
    - [3.1 与WMS协同](#31-与wms协同)
    - [3.2 与ERP协同](#32-与erp协同)
    - [3.3 与电商平台协同](#33-与电商平台协同)
  - [4. EDI数据转换](#4-edi数据转换)
    - [4.1 X12 214转换](#41-x12-214转换)
    - [4.2 EDIFACT IFTSTA转换](#42-edifact-iftsta转换)
    - [4.3 数据验证与清洗](#43-数据验证与清洗)
  - [5. 数据库存储转换](#5-数据库存储转换)
    - [5.1 PostgreSQL数据模型](#51-postgresql数据模型)
    - [5.2 数据导入导出](#52-数据导入导出)
    - [5.3 数据同步机制](#53-数据同步机制)
  - [6. Python实现](#6-python实现)
    - [6.1 数据转换引擎](#61-数据转换引擎)
    - [6.2 EDI解析器](#62-edi解析器)
    - [6.3 数据库适配器](#63-数据库适配器)
  - [7. 转换规则引擎](#7-转换规则引擎)
    - [7.1 规则定义](#71-规则定义)
    - [7.2 规则执行](#72-规则执行)
  - [8. 性能优化](#8-性能优化)
    - [8.1 批量处理](#81-批量处理)
    - [8.2 缓存策略](#82-缓存策略)
    - [8.3 异步处理](#83-异步处理)

---

## 1. 转换体系概述

### 1.1 转换目标

TMS Schema转换体系支持以下转换场景：

1. **内部数据转换**：TMS内部各模块间数据格式转换
2. **供应链协同转换**：与WMS、ERP、电商平台的数据交换
3. **EDI数据转换**：EDI X12、EDIFACT消息的解析与生成
4. **数据库存储转换**：数据持久化和查询优化
5. **外部系统对接**：与第三方物流平台、GPS系统对接

### 1.2 转换架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        TMS转换架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  订单数据  │  │  车辆数据  │  │  路线数据  │  │  运费数据  │        │
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
│  │ X12/EDIF │◄──►│  WMS/ERP  │    │ PostgreSQL│                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 运输数据转换

### 2.1 订单数据转换

**内部格式到EDI格式**：

```python
class OrderDataTransformer:
    """订单数据转换器"""
    
    def __init__(self):
        self.field_mappings = {
            # 内部字段 -> X12字段
            "order_id": "B10.pro_number",
            "bol_number": "L11.reference_number",
            "shipper_name": "N1.N1_02",
            "shipper_address": "N3.N3_01",
            "shipper_city": "N4.N4_01",
            "shipper_state": "N4.N4_02",
            "shipper_zip": "N4.N4_03",
            "consignee_name": "N1.N1_02",
            "weight": "AT8.AT8_03",
            "pieces": "AT8.AT8_05",
        }
    
    def to_x12_214(self, order: TransportationOrder) -> dict:
        """转换为X12 214格式"""
        x12_data = {
            "transaction_set_id": "214",
            "segments": []
        }
        
        # ST段 - 交易集头
        x12_data["segments"].append({
            "segment_id": "ST",
            "elements": ["214", self.generate_control_number()]
        })
        
        # B10段 - 运输起始
        x12_data["segments"].append({
            "segment_id": "B10",
            "elements": [
                order.pro_number or order.order_id,
                order.shipment_id or "",
                "CC"  # 标准承运人Alpha代码
            ]
        })
        
        # L11段 - 参考编号
        if order.bol_number:
            x12_data["segments"].append({
                "segment_id": "L11",
                "elements": [order.bol_number, "BM"]  # BM = Bill of Lading
            })
        
        # N1段 - 发货方
        if order.shipper:
            x12_data["segments"].extend([
                {
                    "segment_id": "N1",
                    "elements": ["SH", order.shipper.name]
                },
                {
                    "segment_id": "N3",
                    "elements": [order.shipper.address.street_address]
                },
                {
                    "segment_id": "N4",
                    "elements": [
                        order.shipper.address.city,
                        order.shipper.address.state_province,
                        order.shipper.address.postal_code,
                        order.shipper.address.country
                    ]
                }
            ])
        
        # N1段 - 收货方
        if order.consignee:
            x12_data["segments"].extend([
                {
                    "segment_id": "N1",
                    "elements": ["CN", order.consignee.name]
                },
                {
                    "segment_id": "N3",
                    "elements": [order.consignee.address.street_address]
                },
                {
                    "segment_id": "N4",
                    "elements": [
                        order.consignee.address.city,
                        order.consignee.address.state_province,
                        order.consignee.address.postal_code,
                        order.consignee.address.country
                    ]
                }
            ])
        
        # AT7段 - 运输状态详情
        status_code = self.map_status_to_x12(order.status)
        x12_data["segments"].append({
            "segment_id": "AT7",
            "elements": [
                status_code,
                "NS",  # 正常状态
                "", "",  # 原因和描述
                datetime.now().strftime("%Y%m%d"),
                datetime.now().strftime("%H%M"),
                "LT"  # 当地时间
            ]
        })
        
        # AT8段 - 重量和数量
        if order.cargo:
            x12_data["segments"].append({
                "segment_id": "AT8",
                "elements": [
                    "G",  # 毛重
                    "L",  # 磅（默认）
                    str(order.cargo.weight.actual_weight),
                    "", "",  # 体积
                    str(order.cargo.total_packages)
                ]
            })
        
        # SE段 - 交易集尾
        segment_count = len(x12_data["segments"]) + 1  # 包含SE段
        x12_data["segments"].append({
            "segment_id": "SE",
            "elements": [str(segment_count), x12_data["segments"][0]["elements"][1]]
        })
        
        return x12_data
    
    def map_status_to_x12(self, status: OrderStatus) -> str:
        """映射订单状态到X12状态代码"""
        status_map = {
            OrderStatus.CREATED: "AA",
            OrderStatus.CONFIRMED: "AB",
            OrderStatus.PENDING_PICKUP: "X1",
            OrderStatus.PICKED_UP: "AF",
            OrderStatus.IN_TRANSIT: "X6",
            OrderStatus.AT_HUB: "X2",
            OrderStatus.OUT_FOR_DELIVERY: "X6",
            OrderStatus.DELIVERED: "D1",
            OrderStatus.COMPLETED: "D1",
            OrderStatus.EXCEPTION: "X9"
        }
        return status_map.get(status, "NS")
    
    def generate_control_number(self) -> str:
        """生成控制编号"""
        return str(random.randint(1000, 9999))
```

### 2.2 车辆数据转换

**车辆状态转换**：

```python
class VehicleDataTransformer:
    """车辆数据转换器"""
    
    def to_gps_format(self, vehicle: Vehicle) -> dict:
        """转换为GPS追踪格式"""
        return {
            "device_id": vehicle.vehicle_id,
            "vehicle_number": vehicle.vehicle_number,
            "timestamp": datetime.now().isoformat(),
            "latitude": vehicle.current_status.current_coordinates[0] if vehicle.current_status.current_coordinates else None,
            "longitude": vehicle.current_status.current_coordinates[1] if vehicle.current_status.current_coordinates else None,
            "speed": vehicle.current_status.speed,
            "heading": vehicle.current_status.heading,
            "status": vehicle.current_status.status.value,
            "odometer": vehicle.current_status.odometer_reading,
            "fuel_level": vehicle.current_status.fuel_level
        }
    
    def to_telematics_format(self, vehicle: Vehicle) -> dict:
        """转换为车队管理系统格式"""
        return {
            "vehicle": {
                "id": vehicle.vehicle_id,
                "number": vehicle.vehicle_number,
                "type": vehicle.vehicle_classification.vehicle_type.value,
                "make": vehicle.specifications.make,
                "model": vehicle.specifications.model,
                "year": vehicle.specifications.year
            },
            "driver": {
                "id": vehicle.operational_info.driver_id,
                "name": vehicle.operational_info.driver_name
            },
            "capacity": {
                "weight_kg": vehicle.specifications.capacity.max_weight,
                "volume_cbm": vehicle.specifications.capacity.max_volume,
                "pallet_positions": vehicle.specifications.capacity.pallet_positions
            },
            "location": {
                "lat": vehicle.current_status.current_coordinates[0] if vehicle.current_status.current_coordinates else None,
                "lng": vehicle.current_status.current_coordinates[1] if vehicle.current_status.current_coordinates else None,
                "address": vehicle.current_status.current_location.address if vehicle.current_status.current_location else None
            },
            "hours_of_service": {
                "driving_hours": vehicle.current_status.hours_of_service.driving_hours_today,
                "on_duty_hours": vehicle.current_status.hours_of_service.on_duty_hours_today,
                "available_hours": vehicle.current_status.hours_of_service.available_driving_hours
            }
        }
```

### 2.3 路线数据转换

**路线优化结果转换**：

```python
class RouteDataTransformer:
    """路线数据转换器"""
    
    def to_navigation_format(self, route: Route) -> dict:
        """转换为导航系统格式"""
        waypoints = []
        
        for leg in route.legs:
            waypoints.append({
                "lat": leg.from_point.coordinates[0],
                "lng": leg.from_point.coordinates[1],
                "name": leg.from_point.name,
                "address": leg.from_point.address
            })
        
        # 添加最后一个点
        last_leg = route.legs[-1]
        waypoints.append({
            "lat": last_leg.to_point.coordinates[0],
            "lng": last_leg.to_point.coordinates[1],
            "name": last_leg.to_point.name,
            "address": last_leg.to_point.address
        })
        
        return {
            "route_id": route.route_id,
            "route_name": route.route_name,
            "total_distance_km": route.totals.total_distance,
            "total_duration_min": route.totals.total_duration,
            "waypoints": waypoints,
            "polyline": self.encode_polyline(route),
            "turn_by_turn": self.generate_turn_instructions(route)
        }
    
    def to_dispatch_format(self, route: Route) -> dict:
        """转换为调度系统格式"""
        stops = []
        
        for idx, leg in enumerate(route.legs):
            stops.append({
                "stop_sequence": idx + 1,
                "stop_type": "PICKUP" if idx == 0 else ("DELIVERY" if idx == len(route.legs) - 1 else "WAYPOINT"),
                "location": {
                    "name": leg.from_point.name,
                    "address": leg.from_point.address.to_dict(),
                    "coordinates": leg.from_point.coordinates
                },
                "time_window": {
                    "earliest": leg.from_point.time_window_start.isoformat() if leg.from_point.time_window_start else None,
                    "latest": leg.from_point.time_window_end.isoformat() if leg.from_point.time_window_end else None
                },
                "service_duration_min": leg.from_point.service_duration,
                "estimated_arrival": None,  # 由调度系统计算
                "estimated_departure": None
            })
        
        return {
            "route_id": route.route_id,
            "stops": stops,
            "total_stops": len(stops),
            "constraints": {
                "max_driving_hours": route.constraints.driver_constraints.max_driving_hours,
                "max_duty_hours": route.constraints.driver_constraints.max_duty_hours,
                "required_breaks": route.constraints.time_constraints.required_breaks
            }
        }
    
    def encode_polyline(self, route: Route) -> str:
        """将路线编码为Google Polyline格式"""
        coordinates = []
        for leg in route.legs:
            if leg.path:
                coordinates.extend(leg.path)
        return self._encode_polyline_algorithm(coordinates)
    
    def _encode_polyline_algorithm(self, coordinates: List[Tuple[float, float]]) -> str:
        """Google Polyline编码算法"""
        result = []
        prev_lat = 0
        prev_lng = 0
        
        for lat, lng in coordinates:
            # 转换为整数
            lat_int = int(round(lat * 1e5))
            lng_int = int(round(lng * 1e5))
            
            # 计算差值
            d_lat = lat_int - prev_lat
            d_lng = lng_int - prev_lng
            
            # 编码差值
            result.append(self._encode_number(d_lat))
            result.append(self._encode_number(d_lng))
            
            prev_lat = lat_int
            prev_lng = lng_int
        
        return ''.join(result)
    
    def _encode_number(self, num: int) -> str:
        """编码单个数字"""
        # 左移1位，如果为负数则取反
        num = ~(num << 1) if num < 0 else num << 1
        
        chunks = []
        while num >= 0x20:
            chunks.append(chr((0x20 | (num & 0x1f)) + 63))
            num >>= 5
        chunks.append(chr(num + 63))
        
        return ''.join(chunks)
    
    def generate_turn_instructions(self, route: Route) -> List[dict]:
        """生成转向指示"""
        instructions = []
        
        for idx, leg in enumerate(route.legs):
            instructions.append({
                "step": idx + 1,
                "instruction": f"Proceed to {leg.to_point.name}",
                "distance_km": leg.distance,
                "duration_min": leg.duration,
                "start_location": {"lat": leg.from_point.coordinates[0], "lng": leg.from_point.coordinates[1]},
                "end_location": {"lat": leg.to_point.coordinates[0], "lng": leg.to_point.coordinates[1]}
            })
        
        return instructions
```

### 2.4 运费数据转换

**运费计算结果转换**：

```python
class FreightDataTransformer:
    """运费数据转换器"""
    
    def to_invoice_format(self, freight_charge: FreightCharge, order: TransportationOrder) -> dict:
        """转换为发票格式"""
        return {
            "invoice_number": f"INV-{order.order_number}",
            "invoice_date": datetime.now().date().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
            "customer": {
                "name": order.customer.customer_name if order.customer else "",
                "address": order.customer.customer_address if hasattr(order.customer, 'customer_address') else {}
            },
            "reference": {
                "order_number": order.order_number,
                "pro_number": order.pro_number if hasattr(order, 'pro_number') else "",
                "bol_number": order.bol_number if hasattr(order, 'bol_number') else ""
            },
            "line_items": [
                {
                    "description": "Freight Charge",
                    "quantity": 1,
                    "unit_price": freight_charge.base_charge,
                    "amount": freight_charge.base_charge
                }
            ] + [
                {
                    "description": surcharge.name,
                    "quantity": 1,
                    "unit_price": surcharge.amount,
                    "amount": surcharge.amount
                }
                for surcharge in freight_charge.surcharges
            ],
            "subtotal": freight_charge.subtotal,
            "discount": sum(d.amount for d in freight_charge.discounts),
            "tax": freight_charge.tax,
            "total": freight_charge.total,
            "currency": freight_charge.currency
        }
    
    def to_gl_format(self, freight_charge: FreightCharge, order: TransportationOrder) -> List[dict]:
        """转换为总账分录格式"""
        entries = []
        
        # 应收账款分录
        entries.append({
            "account_code": "1200",  # 应收账款
            "account_name": "Accounts Receivable",
            "debit": freight_charge.total,
            "credit": 0,
            "reference": order.order_number,
            "description": f"Freight revenue for order {order.order_number}"
        })
        
        # 运输收入分录
        entries.append({
            "account_code": "4100",  # 运输收入
            "account_name": "Freight Revenue",
            "debit": 0,
            "credit": freight_charge.base_charge,
            "reference": order.order_number,
            "description": "Base freight revenue"
        })
        
        # 燃油附加费收入分录
        fuel_surcharge = next((s for s in freight_charge.surcharges if "Fuel" in s.name), None)
        if fuel_surcharge:
            entries.append({
                "account_code": "4110",
                "account_name": "Fuel Surcharge Revenue",
                "debit": 0,
                "credit": fuel_surcharge.amount,
                "reference": order.order_number,
                "description": "Fuel surcharge"
            })
        
        return entries
```

---

## 3. 供应链协同转换

### 3.1 与WMS协同

**WMS-TMS数据交换**：

```python
class WMSTMSIntegration:
    """WMS与TMS集成"""
    
    def convert_wms_shipment_to_tms_order(self, wms_shipment: dict) -> TransportationOrder:
        """将WMS发货单转换为TMS运输订单"""
        order = TransportationOrder()
        
        # 基本信息
        order.order_number = f"TMS-{wms_shipment['shipment_id']}"
        order.order_type = "LTL" if wms_shipment.get('is_ltl') else "FTL"
        
        # 收发货人信息
        order.shipper = PartyInfo(
            name=wms_shipment['from_location']['name'],
            address=Address(
                street_address=wms_shipment['from_location']['address'],
                city=wms_shipment['from_location']['city'],
                state_province=wms_shipment['from_location']['state'],
                postal_code=wms_shipment['from_location']['zip'],
                country=wms_shipment['from_location']['country']
            ),
            contact=ContactInfo(
                contact_name=wms_shipment['from_location'].get('contact_name', ''),
                phone=wms_shipment['from_location'].get('contact_phone', '')
            ),
            location_code=wms_shipment['from_location']['location_code']
        )
        
        order.consignee = PartyInfo(
            name=wms_shipment['to_location']['name'],
            address=Address(
                street_address=wms_shipment['to_location']['address'],
                city=wms_shipment['to_location']['city'],
                state_province=wms_shipment['to_location']['state'],
                postal_code=wms_shipment['to_location']['zip'],
                country=wms_shipment['to_location']['country']
            ),
            contact=ContactInfo(
                contact_name=wms_shipment['to_location'].get('contact_name', ''),
                phone=wms_shipment['to_location'].get('contact_phone', '')
            ),
            location_code=wms_shipment['to_location']['location_code']
        )
        
        # 货物信息
        order.cargo = CargoInfo(
            description=wms_shipment.get('cargo_description', 'General Merchandise'),
            commodity_type=wms_shipment.get('commodity_type', 'General'),
            packaging_type=wms_shipment.get('packaging_type', 'Carton'),
            total_packages=wms_shipment['total_packages'],
            weight=WeightInfo(
                actual_weight=Decimal(str(wms_shipment['total_weight'])),
                chargeable_weight=Decimal(str(wms_shipment['total_weight'])),
                weight_unit=wms_shipment.get('weight_unit', 'KG')
            ),
            dimensions=Dimensions(
                length=Decimal(str(wms_shipment.get('length', 0))),
                width=Decimal(str(wms_shipment.get('width', 0))),
                height=Decimal(str(wms_shipment.get('height', 0))),
                unit=wms_shipment.get('dimension_unit', 'CM')
            ),
            total_volume=Decimal(str(wms_shipment.get('total_volume', 0)))
        )
        
        # 服务要求
        order.scheduled_pickup = datetime.fromisoformat(wms_shipment['requested_ship_date'])
        order.scheduled_delivery = datetime.fromisoformat(wms_shipment['requested_delivery_date'])
        
        return order
    
    def convert_tms_status_to_wms(self, tms_status: dict) -> dict:
        """将TMS状态转换为WMS更新"""
        wms_status_map = {
            "PICKED_UP": "IN_TRANSIT",
            "IN_TRANSIT": "IN_TRANSIT",
            "AT_HUB": "IN_TRANSIT",
            "OUT_FOR_DELIVERY": "OUT_FOR_DELIVERY",
            "DELIVERED": "DELIVERED",
            "COMPLETED": "DELIVERED"
        }
        
        return {
            "shipment_id": tms_status['order_id'],
            "status": wms_status_map.get(tms_status['status'], tms_status['status']),
            "status_timestamp": tms_status['timestamp'],
            "carrier": tms_status.get('carrier_name'),
            "tracking_number": tms_status.get('tracking_number'),
            "estimated_delivery": tms_status.get('estimated_delivery'),
            "actual_delivery": tms_status.get('actual_delivery'),
            "pod_signature": tms_status.get('pod_signature'),
            "pod_image_url": tms_status.get('pod_image_url')
        }
```

### 3.2 与ERP协同

**ERP-TMS集成**：

```python
class ERPTMSIntegration:
    """ERP与TMS集成"""
    
    def convert_erp_sales_order_to_tms(self, erp_order: dict) -> List[TransportationOrder]:
        """将ERP销售订单转换为TMS运输订单"""
        orders = []
        
        # 按发货地分组
        shipments_by_origin = self.group_by_origin(erp_order['line_items'])
        
        for origin, items in shipments_by_origin.items():
            order = TransportationOrder()
            
            order.order_number = f"TMS-{erp_order['order_number']}-{origin}"
            order.customer = CustomerInfo(
                customer_id=erp_order['customer_id'],
                customer_name=erp_order['customer_name'],
                customer_type="B2B"
            )
            
            # 合并货物信息
            total_weight = sum(item['weight'] for item in items)
            total_volume = sum(item['volume'] for item in items)
            total_packages = sum(item['quantity'] for item in items)
            
            order.cargo = CargoInfo(
                description=f"Order {erp_order['order_number']}",
                commodity_type="General",
                packaging_type="Carton",
                total_packages=total_packages,
                weight=WeightInfo(
                    actual_weight=Decimal(str(total_weight)),
                    chargeable_weight=Decimal(str(total_weight))
                ),
                total_volume=Decimal(str(total_volume))
            )
            
            # 使用第一个产品的发货地址
            first_item = items[0]
            order.shipper = PartyInfo(
                name=first_item['ship_from_name'],
                address=Address(
                    street_address=first_item['ship_from_address'],
                    city=first_item['ship_from_city'],
                    state_province=first_item['ship_from_state'],
                    postal_code=first_item['ship_from_zip'],
                    country=first_item['ship_from_country']
                ),
                contact=ContactInfo(
                    contact_name=first_item['ship_from_contact'],
                    phone=first_item['ship_from_phone']
                )
            )
            
            # 收货地址（客户地址）
            order.consignee = PartyInfo(
                name=erp_order['ship_to_name'],
                address=Address(
                    street_address=erp_order['ship_to_address'],
                    city=erp_order['ship_to_city'],
                    state_province=erp_order['ship_to_state'],
                    postal_code=erp_order['ship_to_zip'],
                    country=erp_order['ship_to_country']
                ),
                contact=ContactInfo(
                    contact_name=erp_order['ship_to_contact'],
                    phone=erp_order['ship_to_phone']
                )
            )
            
            # 交货日期
            order.scheduled_delivery = datetime.fromisoformat(erp_order['requested_delivery_date'])
            order.scheduled_pickup = datetime.fromisoformat(erp_order['requested_ship_date'])
            
            orders.append(order)
        
        return orders
    
    def convert_tms_invoice_to_erp(self, tms_invoice: dict) -> dict:
        """将TMS发票转换为ERP应收凭证"""
        return {
            "document_type": "AR_INVOICE",
            "customer_code": tms_invoice['customer']['customer_code'],
            "invoice_date": tms_invoice['invoice_date'],
            "due_date": tms_invoice['due_date'],
            "reference": tms_invoice['reference']['order_number'],
            "lines": [
                {
                    "account_code": "4100",  # 运输收入
                    "description": item['description'],
                    "amount": float(item['amount']),
                    "tax_code": "OUTPUT_VAT"
                }
                for item in tms_invoice['line_items']
            ],
            "total_amount": float(tms_invoice['total']),
            "currency": tms_invoice['currency']
        }
```

### 3.3 与电商平台协同

**电商-TMS集成**：

```python
class EcommerceTMSIntegration:
    """电商平台与TMS集成"""
    
    SUPPORTED_PLATFORMS = ["shopify", "amazon", "ebay", "woocommerce", "magento"]
    
    def convert_shopify_order(self, shopify_order: dict) -> TransportationOrder:
        """将Shopify订单转换为TMS订单"""
        order = TransportationOrder()
        
        order.order_number = f"SH-{shopify_order['order_number']}"
        order.order_type = "EXPRESS"
        order.service_level = ServiceLevel.STANDARD
        
        # 发货方（商家）
        order.shipper = PartyInfo(
            name=shopify_order['shop_name'],
            address=Address(
                street_address=shopify_order['shipping_address']['address1'],
                city=shopify_order['shipping_address']['city'],
                state_province=shopify_order['shipping_address']['province'],
                postal_code=shopify_order['shipping_address']['zip'],
                country=shopify_order['shipping_address']['country_code']
            ),
            contact=ContactInfo(
                contact_name=shopify_order['shop_name'],
                phone=shopify_order.get('shop_phone', '')
            )
        )
        
        # 收货方（消费者）
        shipping = shopify_order['shipping_address']
        order.consignee = PartyInfo(
            name=f"{shipping['first_name']} {shipping['last_name']}",
            address=Address(
                street_address=f"{shipping['address1']} {shipping.get('address2', '')}".strip(),
                city=shipping['city'],
                state_province=shipping['province'],
                postal_code=shipping['zip'],
                country=shipping['country_code']
            ),
            contact=ContactInfo(
                contact_name=f"{shipping['first_name']} {shipping['last_name']}",
                phone=shipping.get('phone', '')
            ),
            delivery_instructions=shipping.get('delivery_instructions', '')
        )
        
        # 货物信息
        total_weight = sum(
            float(item.get('grams', 0)) / 1000  # 转换为kg
            for item in shopify_order['line_items']
        )
        
        order.cargo = CargoInfo(
            description=f"E-commerce order with {len(shopify_order['line_items'])} items",
            commodity_type="E-commerce",
            packaging_type="Carton",
            total_packages=len(shopify_order['line_items']),
            weight=WeightInfo(
                actual_weight=Decimal(str(total_weight)),
                chargeable_weight=Decimal(str(max(total_weight, 0.5)))  # 最小0.5kg
            ),
            declared_value=Decimal(str(shopify_order['total_price']))
        )
        
        # 服务要求
        if shopify_order.get('shipping_lines'):
            shipping_method = shopify_order['shipping_lines'][0]['title'].lower()
            if 'expedited' in shipping_method or 'express' in shipping_method:
                order.service_level = ServiceLevel.EXPEDITED
            elif 'overnight' in shipping_method:
                order.service_level = ServiceLevel.GUARANTEED
        
        # 时间要求
        order.scheduled_delivery = datetime.fromisoformat(shopify_order['created_at']) + timedelta(days=3)
        
        return order
    
    def convert_amazon_order(self, amazon_order: dict) -> TransportationOrder:
        """将Amazon订单转换为TMS订单"""
        order = TransportationOrder()
        
        order.order_number = f"AMZ-{amazon_order['AmazonOrderId']}"
        order.order_type = "EXPRESS"
        
        # 收货地址
        shipping = amazon_order['ShippingAddress']
        order.consignee = PartyInfo(
            name=shipping.get('Name', ''),
            address=Address(
                street_address=shipping.get('AddressLine1', ''),
                city=shipping.get('City', ''),
                state_province=shipping.get('StateOrRegion', ''),
                postal_code=shipping.get('PostalCode', ''),
                country=shipping.get('CountryCode', '')
            ),
            contact=ContactInfo(
                contact_name=shipping.get('Name', ''),
                phone=shipping.get('Phone', '')
            )
        )
        
        # Amazon特定服务级别映射
        ship_level = amazon_order.get('ShipServiceLevel', '')
        if 'Expedited' in ship_level:
            order.service_level = ServiceLevel.EXPEDITED
        elif 'NextDay' in ship_level or 'SecondDay' in ship_level:
            order.service_level = ServiceLevel.GUARANTEED
        
        return order
    
    def send_tracking_to_platform(self, platform: str, order_id: str, tracking_info: dict) -> bool:
        """将跟踪信息发送回电商平台"""
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # 各平台特定的API调用
        if platform == "shopify":
            return self._send_shopify_tracking(order_id, tracking_info)
        elif platform == "amazon":
            return self._send_amazon_tracking(order_id, tracking_info)
        # ... 其他平台
        
        return False
```

---

## 4. EDI数据转换

### 4.1 X12 214转换

```python
class X12214Transformer:
    """X12 214 运输状态消息转换器"""
    
    def parse(self, x12_message: str) -> dict:
        """解析X12 214消息"""
        segments = x12_message.split('~')
        data = {
            "transaction_set": "214",
            "segments": []
        }
        
        for segment in segments:
            if not segment.strip():
                continue
            
            elements = segment.split('*')
            segment_id = elements[0]
            
            if segment_id == "ST":
                data["control_number"] = elements[2] if len(elements) > 2 else ""
            elif segment_id == "B10":
                data["shipment_id"] = elements[1] if len(elements) > 1 else ""
                data["reference_number"] = elements[2] if len(elements) > 2 else ""
            elif segment_id == "L11":
                if "references" not in data:
                    data["references"] = []
                data["references"].append({
                    "number": elements[1] if len(elements) > 1 else "",
                    "qualifier": elements[2] if len(elements) > 2 else ""
                })
            elif segment_id == "AT7":
                data["status"] = {
                    "code": elements[1] if len(elements) > 1 else "",
                    "reason": elements[2] if len(elements) > 2 else "",
                    "date": elements[5] if len(elements) > 5 else "",
                    "time": elements[6] if len(elements) > 6 else "",
                    "timezone": elements[7] if len(elements) > 7 else ""
                }
            elif segment_id == "MS1":
                data["location"] = {
                    "city": elements[1] if len(elements) > 1 else "",
                    "state": elements[2] if len(elements) > 2 else "",
                    "country": elements[3] if len(elements) > 3 else ""
                }
            elif segment_id == "AT8":
                data["weight"] = {
                    "type": elements[1] if len(elements) > 1 else "",
                    "unit": elements[2] if len(elements) > 2 else "",
                    "value": elements[3] if len(elements) > 3 else ""
                }
        
        return data
    
    def generate(self, data: dict) -> str:
        """生成X12 214消息"""
        segments = []
        
        # ST段
        control_num = data.get("control_number", str(random.randint(1000, 9999)))
        segments.append(f"ST*214*{control_num}")
        
        # B10段
        b10 = f"B10*{data.get('shipment_id', '')}*{data.get('reference_number', '')}*CC"
        segments.append(b10)
        
        # L11段
        for ref in data.get("references", []):
            segments.append(f"L11*{ref.get('number', '')}*{ref.get('qualifier', '')}")
        
        # AT7段 - 状态
        status = data.get("status", {})
        at7 = f"AT7*{status.get('code', '')}*{status.get('reason', '')}***{status.get('date', '')}*{status.get('time', '')}*{status.get('timezone', 'LT')}"
        segments.append(at7)
        
        # MS1段 - 位置
        location = data.get("location", {})
        if location:
            segments.append(f"MS1*{location.get('city', '')}*{location.get('state', '')}*{location.get('country', '')}")
        
        # SE段
        segment_count = len(segments) + 1
        segments.append(f"SE*{segment_count}*{control_num}")
        
        return "~".join(segments) + "~"
```

### 4.2 EDIFACT IFTSTA转换

```python
class EDIFACTIFTSTATransformer:
    """EDIFACT IFTSTA 运输状态消息转换器"""
    
    SEGMENT_TERMINATOR = "'"
    ELEMENT_SEPARATOR = "+"
    
    def parse(self, edifact_message: str) -> dict:
        """解析EDIFACT IFTSTA消息"""
        segments = edifact_message.split(self.SEGMENT_TERMINATOR)
        data = {
            "message_type": "IFTSTA",
            "segments": []
        }
        
        for segment in segments:
            if not segment.strip():
                continue
            
            elements = segment.split(self.ELEMENT_SEPARATOR)
            segment_tag = elements[0]
            
            if segment_tag == "UNH":
                data["message_reference"] = elements[1] if len(elements) > 1 else ""
            elif segment_tag == "BGM":
                data["document_type"] = elements[1] if len(elements) > 1 else ""
                data["document_number"] = elements[2] if len(elements) > 2 else ""
            elif segment_tag == "DTM":
                if "datetime" not in data:
                    data["datetime"] = []
                dtm_elements = elements[1].split(":") if len(elements) > 1 else []
                data["datetime"].append({
                    "qualifier": dtm_elements[0] if len(dtm_elements) > 0 else "",
                    "value": dtm_elements[1] if len(dtm_elements) > 1 else "",
                    "format": dtm_elements[2] if len(dtm_elements) > 2 else ""
                })
            elif segment_tag == "STS":
                status_elements = elements[2].split(":") if len(elements) > 2 else []
                data["status"] = {
                    "category": elements[1] if len(elements) > 1 else "",
                    "code": status_elements[0] if len(status_elements) > 0 else "",
                    "description": status_elements[1] if len(status_elements) > 1 else ""
                }
            elif segment_tag == "LOC":
                if "locations" not in data:
                    data["locations"] = []
                data["locations"].append({
                    "qualifier": elements[1] if len(elements) > 1 else "",
                    "code": elements[2] if len(elements) > 2 else ""
                })
            elif segment_tag == "RFF":
                if "references" not in data:
                    data["references"] = []
                ref_elements = elements[1].split(":") if len(elements) > 1 else []
                data["references"].append({
                    "qualifier": ref_elements[0] if len(ref_elements) > 0 else "",
                    "number": ref_elements[1] if len(ref_elements) > 1 else ""
                })
        
        return data
    
    def generate(self, data: dict) -> str:
        """生成EDIFACT IFTSTA消息"""
        segments = []
        
        # UNB段 - 交换头
        sender = data.get("sender", "SENDER")
        receiver = data.get("receiver", "RECEIVER")
        timestamp = datetime.now()
        interchange_ref = str(random.randint(1000000, 9999999))
        segments.append(
            f"UNB+UNOA:3+{sender}+{receiver}+{timestamp.strftime('%y%m%d')}:{timestamp.strftime('%H%M')}+{interchange_ref}"
        )
        
        # UNH段 - 消息头
        msg_ref = data.get("message_reference", "1")
        segments.append(f"UNH+{msg_ref}+IFTSTA:D:21A:UN")
        
        # BGM段
        doc_type = data.get("document_type", "23")
        doc_num = data.get("document_number", "")
        segments.append(f"BGM+{doc_type}+{doc_num}+9")
        
        # DTM段
        for dtm in data.get("datetime", []):
            segments.append(f"DTM+{dtm.get('qualifier', '')}:{dtm.get('value', '')}:{dtm.get('format', '')}")
        
        # STS段 - 状态
        status = data.get("status", {})
        segments.append(f"STS++{status.get('category', '')}+{status.get('code', '')}:{status.get('description', '')}")
        
        # LOC段
        for loc in data.get("locations", []):
            segments.append(f"LOC+{loc.get('qualifier', '')}+{loc.get('code', '')}")
        
        # RFF段
        for ref in data.get("references", []):
            segments.append(f"RFF+{ref.get('qualifier', '')}:{ref.get('number', '')}")
        
        # UNT段 - 消息尾
        segment_count = len(segments)  # 不包括UNB
        segments.append(f"UNT+{segment_count}+{msg_ref}")
        
        # UNZ段 - 交换尾
        segments.append(f"UNZ+1+{interchange_ref}")
        
        return self.SEGMENT_TERMINATOR.join(segments) + self.SEGMENT_TERMINATOR
```

### 4.3 数据验证与清洗

```python
class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.validation_rules = {
            "order_number": ["required", "max_length:50"],
            "shipper.name": ["required", "max_length:100"],
            "shipper.address.postal_code": ["required", "postal_code"],
            "consignee.name": ["required", "max_length:100"],
            "cargo.weight.actual_weight": ["required", "positive_number"],
            "scheduled_pickup": ["required", "future_date"],
            "scheduled_delivery": ["required", "future_date"]
        }
    
    def validate_order(self, order: dict) -> List[dict]:
        """验证订单数据"""
        errors = []
        
        for field_path, rules in self.validation_rules.items():
            value = self._get_nested_value(order, field_path)
            
            for rule in rules:
                if rule == "required" and not value:
                    errors.append({
                        "field": field_path,
                        "rule": rule,
                        "message": f"{field_path} is required"
                    })
                elif rule == "max_length:50" and value and len(str(value)) > 50:
                    errors.append({
                        "field": field_path,
                        "rule": rule,
                        "message": f"{field_path} exceeds maximum length of 50"
                    })
                elif rule == "postal_code" and value:
                    if not self._is_valid_postal_code(str(value)):
                        errors.append({
                            "field": field_path,
                            "rule": rule,
                            "message": f"{field_path} is not a valid postal code"
                        })
                elif rule == "positive_number" and value is not None:
                    try:
                        if Decimal(str(value)) <= 0:
                            errors.append({
                                "field": field_path,
                                "rule": rule,
                                "message": f"{field_path} must be a positive number"
                            })
                    except:
                        errors.append({
                            "field": field_path,
                            "rule": rule,
                            "message": f"{field_path} must be a valid number"
                        })
        
        return errors
    
    def _get_nested_value(self, data: dict, path: str) -> any:
        """获取嵌套字典值"""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _is_valid_postal_code(self, postal_code: str) -> bool:
        """验证邮编格式"""
        # 美国邮编: 12345 或 12345-6789
        # 中国邮编: 6位数字
        import re
        us_pattern = r'^\d{5}(-\d{4})?$'
        cn_pattern = r'^\d{6}$'
        return bool(re.match(us_pattern, postal_code) or re.match(cn_pattern, postal_code))
    
    def sanitize_data(self, data: dict) -> dict:
        """清洗数据"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # 去除首尾空格
                sanitized[key] = value.strip()
                # 转换为大写（特定字段）
                if key in ["country", "state", "postal_code"]:
                    sanitized[key] = sanitized[key].upper()
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
```

---

## 5. 数据库存储转换

### 5.1 PostgreSQL数据模型

```sql
-- 运输订单表
CREATE TABLE transportation_orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    service_level VARCHAR(20),
    status VARCHAR(20) NOT NULL,
    
    -- 客户信息
    customer_id VARCHAR(50),
    customer_name VARCHAR(100),
    
    -- 发货方
    shipper_name VARCHAR(100),
    shipper_address JSONB,
    shipper_contact JSONB,
    shipper_location_code VARCHAR(50),
    
    -- 收货方
    consignee_name VARCHAR(100),
    consignee_address JSONB,
    consignee_contact JSONB,
    consignee_location_code VARCHAR(50),
    
    -- 货物信息
    cargo_description TEXT,
    cargo_weight_kg DECIMAL(10,2),
    cargo_volume_cbm DECIMAL(10,2),
    total_packages INTEGER,
    declared_value DECIMAL(12,2),
    currency VARCHAR(3),
    
    -- 时间
    scheduled_pickup TIMESTAMP,
    scheduled_delivery TIMESTAMP,
    actual_pickup TIMESTAMP,
    actual_delivery TIMESTAMP,
    
    -- 分配
    assigned_carrier_id VARCHAR(50),
    assigned_vehicle_id VARCHAR(50),
    pro_number VARCHAR(50),
    bol_number VARCHAR(50),
    
    -- 费用
    freight_charge DECIMAL(12,2),
    fuel_surcharge DECIMAL(12,2),
    total_charge DECIMAL(12,2),
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    source_system VARCHAR(50),
    external_reference VARCHAR(100)
);

-- 车辆表
CREATE TABLE vehicles (
    vehicle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(30),
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    vin VARCHAR(17) UNIQUE,
    
    -- 容量
    max_weight_kg DECIMAL(10,2),
    max_volume_cbm DECIMAL(10,2),
    pallet_positions INTEGER,
    
    -- 运营
    carrier_id VARCHAR(50),
    driver_id VARCHAR(50),
    status VARCHAR(20),
    
    -- 位置
    current_lat DECIMAL(10, 8),
    current_lng DECIMAL(11, 8),
    current_address JSONB,
    last_location_update TIMESTAMP,
    
    -- 文档
    registration_expiry DATE,
    insurance_expiry DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 路线表
CREATE TABLE routes (
    route_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_number VARCHAR(50) UNIQUE NOT NULL,
    route_name VARCHAR(100),
    route_type VARCHAR(30),
    
    -- 起止点
    origin JSONB NOT NULL,
    destination JSONB NOT NULL,
    waypoints JSONB,
    
    -- 距离和时间
    total_distance_km DECIMAL(10,2),
    total_duration_min INTEGER,
    
    -- 优化
    optimization_objective VARCHAR(30),
    is_optimized BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 承运人表
CREATE TABLE carriers (
    carrier_id VARCHAR(50) PRIMARY KEY,
    carrier_code VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    legal_name VARCHAR(100),
    
    -- 联系
    headquarters_address JSONB,
    primary_contact JSONB,
    
    -- 资质
    dot_number VARCHAR(20),
    mc_number VARCHAR(20),
    scac_code VARCHAR(4),
    authority_status VARCHAR(20),
    
    -- 能力
    service_types TEXT[],
    equipment_types TEXT[],
    
    -- 保险
    insurance_expiry DATE,
    
    -- 评级
    overall_rating DECIMAL(3,1),
    rating_tier VARCHAR(5),
    
    -- 状态
    active BOOLEAN DEFAULT TRUE,
    approved BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 运费率表
CREATE TABLE freight_rates (
    rate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rate_name VARCHAR(100) NOT NULL,
    rate_type VARCHAR(30) NOT NULL,
    
    -- 适用性
    carrier_id VARCHAR(50),
    customer_id VARCHAR(50),
    effective_date DATE NOT NULL,
    expiry_date DATE,
    
    -- 地理范围
    origin_country VARCHAR(2),
    origin_state VARCHAR(50),
    destination_country VARCHAR(2),
    destination_state VARCHAR(50),
    
    -- 费率
    base_rate_amount DECIMAL(12,4),
    base_rate_unit VARCHAR(20),
    minimum_charge DECIMAL(12,2),
    
    -- 燃油附加费
    fuel_surcharge_enabled BOOLEAN DEFAULT TRUE,
    fuel_surcharge_percentage DECIMAL(5,2),
    
    -- 货币
    currency VARCHAR(3) DEFAULT 'USD',
    
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 运输状态历史表
CREATE TABLE shipment_status_history (
    status_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES transportation_orders(order_id),
    status VARCHAR(20) NOT NULL,
    status_code VARCHAR(10),
    location JSONB,
    
    -- 详细信息
    description TEXT,
    exception_reason VARCHAR(100),
    
    -- 时间
    status_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 来源
    source_system VARCHAR(50),
    edi_message_id VARCHAR(100)
);

-- 创建索引
CREATE INDEX idx_orders_status ON transportation_orders(status);
CREATE INDEX idx_orders_customer ON transportation_orders(customer_id);
CREATE INDEX idx_orders_carrier ON transportation_orders(assigned_carrier_id);
CREATE INDEX idx_orders_created ON transportation_orders(created_at);
CREATE INDEX idx_status_history_order ON shipment_status_history(order_id);
CREATE INDEX idx_vehicles_carrier ON vehicles(carrier_id);
CREATE INDEX idx_vehicles_status ON vehicles(status);
```

### 5.2 数据导入导出

```python
class DatabaseImporter:
    """数据库导入器"""
    
    def __init__(self, db_connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(db_connection_string)
    
    def import_orders_from_csv(self, csv_file_path: str, batch_size: int = 1000) -> dict:
        """从CSV导入订单"""
        import csv
        
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        cursor = self.conn.cursor()
        
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            
            for row in reader:
                results["total"] += 1
                
                try:
                    # 转换数据
                    order_data = self._convert_csv_row_to_order(row)
                    batch.append(order_data)
                    
                    if len(batch) >= batch_size:
                        self._insert_batch(cursor, batch)
                        results["success"] += len(batch)
                        batch = []
                
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "row": results["total"],
                        "error": str(e)
                    })
            
            # 插入剩余批次
            if batch:
                self._insert_batch(cursor, batch)
                results["success"] += len(batch)
        
        self.conn.commit()
        return results
    
    def _convert_csv_row_to_order(self, row: dict) -> dict:
        """转换CSV行到订单数据"""
        return {
            "order_number": row.get("order_number"),
            "order_type": row.get("order_type", "FTL"),
            "status": row.get("status", "Created"),
            "customer_id": row.get("customer_id"),
            "customer_name": row.get("customer_name"),
            "shipper_name": row.get("shipper_name"),
            "shipper_address": json.dumps({
                "street": row.get("shipper_address"),
                "city": row.get("shipper_city"),
                "state": row.get("shipper_state"),
                "zip": row.get("shipper_zip")
            }),
            "cargo_weight_kg": Decimal(row.get("weight", 0)),
            "scheduled_pickup": row.get("pickup_date"),
            "scheduled_delivery": row.get("delivery_date")
        }
    
    def _insert_batch(self, cursor, batch: List[dict]):
        """批量插入"""
        columns = batch[0].keys()
        
        query = f"""
            INSERT INTO transportation_orders ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
        """
        
        values = [
            tuple(order.get(col) for col in columns)
            for order in batch
        ]
        
        cursor.executemany(query, values)


class DatabaseExporter:
    """数据库导出器"""
    
    def __init__(self, db_connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(db_connection_string)
    
    def export_orders_to_csv(
        self, 
        csv_file_path: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ):
        """导出订单到CSV"""
        import csv
        
        # 构建查询
        query = "SELECT * FROM transportation_orders WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND created_at <= %s"
            params.append(end_date)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        # 获取列名
        columns = [desc[0] for desc in cursor.description]
        
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            
            for row in cursor.fetchall():
                writer.writerow(row)
```

### 5.3 数据同步机制

```python
class DataSynchronizer:
    """数据同步器"""
    
    def __init__(self, source_db: str, target_db: str):
        import psycopg2
        self.source_conn = psycopg2.connect(source_db)
        self.target_conn = psycopg2.connect(target_db)
        self.last_sync_time = None
    
    def sync_orders(self, incremental: bool = True) -> dict:
        """同步订单数据"""
        results = {
            "inserted": 0,
            "updated": 0,
            "deleted": 0,
            "errors": []
        }
        
        # 从源数据库读取数据
        source_cursor = self.source_conn.cursor()
        
        query = "SELECT * FROM transportation_orders"
        if incremental and self.last_sync_time:
            query += f" WHERE updated_at > '{self.last_sync_time}'"
        
        source_cursor.execute(query)
        
        # 同步到目标数据库
        target_cursor = self.target_conn.cursor()
        
        for row in source_cursor.fetchall():
            try:
                # 检查记录是否存在
                target_cursor.execute(
                    "SELECT order_id FROM transportation_orders WHERE order_id = %s",
                    (row[0],)
                )
                
                if target_cursor.fetchone():
                    # 更新
                    self._update_order(target_cursor, row)
                    results["updated"] += 1
                else:
                    # 插入
                    self._insert_order(target_cursor, row)
                    results["inserted"] += 1
            
            except Exception as e:
                results["errors"].append({
                    "order_id": row[0],
                    "error": str(e)
                })
        
        self.target_conn.commit()
        self.last_sync_time = datetime.now()
        
        return results
    
    def _insert_order(self, cursor, row: tuple):
        """插入订单"""
        cursor.execute("""
            INSERT INTO transportation_orders 
            (order_id, order_number, order_type, status, customer_id, customer_name,
             shipper_name, shipper_address, consignee_name, consignee_address,
             cargo_weight_kg, scheduled_pickup, scheduled_delivery, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, row[:14])
    
    def _update_order(self, cursor, row: tuple):
        """更新订单"""
        cursor.execute("""
            UPDATE transportation_orders SET
                order_number = %s,
                order_type = %s,
                status = %s,
                customer_id = %s,
                customer_name = %s,
                shipper_name = %s,
                shipper_address = %s,
                consignee_name = %s,
                consignee_address = %s,
                cargo_weight_kg = %s,
                scheduled_pickup = %s,
                scheduled_delivery = %s,
                updated_at = %s
            WHERE order_id = %s
        """, row[1:14] + (row[0],))
```

---

## 6. Python实现

### 6.1 数据转换引擎

```python
class DataTransformationEngine:
    """数据转换引擎"""
    
    def __init__(self):
        self.transformers = {}
        self.register_default_transformers()
    
    def register_transformer(self, source_format: str, target_format: str, transformer):
        """注册转换器"""
        key = f"{source_format}_to_{target_format}"
        self.transformers[key] = transformer
    
    def register_default_transformers(self):
        """注册默认转换器"""
        # 订单转换
        self.register_transformer("internal", "x12_214", OrderDataTransformer())
        self.register_transformer("internal", "edifact_iftsta", OrderDataTransformer())
        
        # 车辆转换
        self.register_transformer("internal", "gps", VehicleDataTransformer())
        
        # 路线转换
        self.register_transformer("internal", "navigation", RouteDataTransformer())
        
        # 运费转换
        self.register_transformer("internal", "invoice", FreightDataTransformer())
    
    def transform(self, data: any, source_format: str, target_format: str, **options) -> any:
        """执行数据转换"""
        key = f"{source_format}_to_{target_format}"
        
        if key not in self.transformers:
            raise ValueError(f"No transformer found for {source_format} to {target_format}")
        
        transformer = self.transformers[key]
        
        # 根据数据类型调用相应方法
        if isinstance(data, TransportationOrder):
            if target_format == "x12_214":
                return transformer.to_x12_214(data)
            elif target_format == "edifact_iftsta":
                return transformer.to_edifact_iftsta(data)
        elif isinstance(data, Vehicle):
            if target_format == "gps":
                return transformer.to_gps_format(data)
        elif isinstance(data, Route):
            if target_format == "navigation":
                return transformer.to_navigation_format(data)
        elif isinstance(data, FreightCharge):
            if target_format == "invoice":
                return transformer.to_invoice_format(data, options.get('order'))
        
        raise ValueError(f"Unsupported data type or target format")
```

### 6.2 EDI解析器

```python
class EDIParser:
    """通用EDI解析器"""
    
    def __init__(self):
        self.x12_parser = X12Parser()
        self.edifact_parser = EDIFACTParser()
    
    def detect_format(self, message: str) -> str:
        """检测EDI格式"""
        message = message.strip()
        
        if message.startswith("ISA"):
            return "X12"
        elif message.startswith("UNB"):
            return "EDIFACT"
        else:
            raise ValueError("Unknown EDI format")
    
    def parse(self, message: str) -> dict:
        """解析EDI消息"""
        format_type = self.detect_format(message)
        
        if format_type == "X12":
            return self.x12_parser.parse(message)
        elif format_type == "EDIFACT":
            return self.edifact_parser.parse(message)
    
    def validate(self, message: str, format_type: Optional[str] = None) -> tuple:
        """验证EDI消息"""
        if format_type is None:
            format_type = self.detect_format(message)
        
        if format_type == "X12":
            return self.x12_parser.validate(message)
        elif format_type == "EDIFACT":
            return self.edifact_parser.validate(message)


class X12Parser:
    """X12解析器"""
    
    def parse(self, message: str) -> dict:
        """解析X12消息"""
        # 检测分隔符
        isa_line = message[:106]
        element_sep = isa_line[3]
        segment_sep = isa_line[105]
        
        segments = message.split(segment_sep)
        parsed = {
            "format": "X12",
            "element_separator": element_sep,
            "segment_separator": segment_sep,
            "segments": []
        }
        
        for segment in segments:
            if not segment.strip():
                continue
            
            elements = segment.split(element_sep)
            parsed["segments"].append({
                "id": elements[0],
                "elements": elements[1:]
            })
            
            # 解析关键段
            if elements[0] == "ISA":
                parsed["isa"] = self._parse_isa(elements)
            elif elements[0] == "GS":
                parsed["gs"] = self._parse_gs(elements)
            elif elements[0] == "ST":
                parsed["st"] = self._parse_st(elements)
        
        return parsed
    
    def _parse_isa(self, elements: list) -> dict:
        """解析ISA段"""
        return {
            "authorization_info_qualifier": elements[1] if len(elements) > 1 else "",
            "authorization_info": elements[2] if len(elements) > 2 else "",
            "security_info_qualifier": elements[3] if len(elements) > 3 else "",
            "security_info": elements[4] if len(elements) > 4 else "",
            "sender_id_qualifier": elements[5] if len(elements) > 5 else "",
            "sender_id": elements[6].strip() if len(elements) > 6 else "",
            "receiver_id_qualifier": elements[7] if len(elements) > 7 else "",
            "receiver_id": elements[8].strip() if len(elements) > 8 else "",
            "date": elements[9] if len(elements) > 9 else "",
            "time": elements[10] if len(elements) > 10 else "",
            "control_number": elements[13] if len(elements) > 13 else ""
        }
    
    def validate(self, message: str) -> tuple:
        """验证X12消息"""
        errors = []
        
        # 基本验证
        if not message.startswith("ISA"):
            errors.append("Message must start with ISA segment")
        
        if "GS" not in message:
            errors.append("Missing GS segment")
        
        if "ST" not in message:
            errors.append("Missing ST segment")
        
        if "SE" not in message:
            errors.append("Missing SE segment")
        
        if "GE" not in message:
            errors.append("Missing GE segment")
        
        if "IEA" not in message:
            errors.append("Missing IEA segment")
        
        return len(errors) == 0, errors
```

### 6.3 数据库适配器

```python
class PostgreSQLAdapter:
    """PostgreSQL数据库适配器"""
    
    def __init__(self, connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(connection_string)
    
    def insert_order(self, order: TransportationOrder) -> str:
        """插入订单"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO transportation_orders 
            (order_id, order_number, order_type, service_level, status,
             customer_id, customer_name, shipper_name, shipper_address,
             consignee_name, consignee_address, cargo_weight_kg,
             scheduled_pickup, scheduled_delivery)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING order_id
        """, (
            order.order_id,
            order.order_number,
            order.order_type,
            order.service_level.value if order.service_level else None,
            order.status.value,
            order.customer.customer_id if order.customer else None,
            order.customer.customer_name if order.customer else None,
            order.shipper.name if order.shipper else None,
            json.dumps(order.shipper.address.__dict__) if order.shipper else None,
            order.consignee.name if order.consignee else None,
            json.dumps(order.consignee.address.__dict__) if order.consignee else None,
            float(order.cargo.weight.actual_weight) if order.cargo else None,
            order.scheduled_pickup,
            order.scheduled_delivery
        ))
        
        order_id = cursor.fetchone()[0]
        self.conn.commit()
        
        return order_id
    
    def get_order_by_id(self, order_id: str) -> Optional[TransportationOrder]:
        """根据ID获取订单"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM transportation_orders WHERE order_id = %s
        """, (order_id,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_order(row)
        return None
    
    def _row_to_order(self, row: tuple) -> TransportationOrder:
        """数据库行转换为订单对象"""
        # 简化实现
        order = TransportationOrder()
        order.order_id = row[0]
        order.order_number = row[1]
        # ... 其他字段映射
        return order
```

---

## 7. 转换规则引擎

### 7.1 规则定义

```python
@dataclass
class TransformationRule:
    """转换规则"""
    rule_id: str
    rule_name: str
    source_format: str
    target_format: str
    conditions: List[dict]
    mappings: List[dict]
    transformations: List[dict]
    priority: int = 0
    active: bool = True

class RuleRepository:
    """规则仓库"""
    
    def __init__(self):
        self.rules = []
        self.load_default_rules()
    
    def load_default_rules(self):
        """加载默认规则"""
        # X12 214转换规则
        self.rules.append(TransformationRule(
            rule_id="x12_214_basic",
            rule_name="Basic X12 214 Conversion",
            source_format="internal",
            target_format="x12_214",
            conditions=[],
            mappings=[
                {"source": "order_id", "target": "B10.elements[0]"},
                {"source": "shipper.name", "target": "N1.elements[1]", "condition": "N1.elements[0] == 'SH'"},
                {"source": "consignee.name", "target": "N1.elements[1]", "condition": "N1.elements[0] == 'CN'"},
            ],
            transformations=[
                {"field": "status", "operation": "map", "mapping": "status_to_x12"}
            ]
        ))
    
    def get_rules(self, source_format: str, target_format: str) -> List[TransformationRule]:
        """获取适用的规则"""
        return [
            rule for rule in self.rules
            if rule.source_format == source_format
            and rule.target_format == target_format
            and rule.active
        ]
```

### 7.2 规则执行

```python
class RuleEngine:
    """规则执行引擎"""
    
    def __init__(self, rule_repository: RuleRepository):
        self.rule_repository = rule_repository
    
    def execute(self, data: any, source_format: str, target_format: str) -> any:
        """执行转换规则"""
        # 获取适用的规则
        rules = self.rule_repository.get_rules(source_format, target_format)
        rules.sort(key=lambda r: r.priority, reverse=True)
        
        result = data
        
        for rule in rules:
            # 检查条件
            if self._check_conditions(result, rule.conditions):
                # 应用映射
                result = self._apply_mappings(result, rule.mappings)
                # 应用转换
                result = self._apply_transformations(result, rule.transformations)
        
        return result
    
    def _check_conditions(self, data: any, conditions: List[dict]) -> bool:
        """检查条件"""
        for condition in conditions:
            field_value = self._get_field_value(data, condition.get("field"))
            operator = condition.get("operator")
            expected_value = condition.get("value")
            
            if operator == "equals" and field_value != expected_value:
                return False
            elif operator == "not_equals" and field_value == expected_value:
                return False
            elif operator == "in" and field_value not in expected_value:
                return False
        
        return True
    
    def _apply_mappings(self, data: any, mappings: List[dict]) -> any:
        """应用字段映射"""
        result = {}
        
        for mapping in mappings:
            source_field = mapping.get("source")
            target_field = mapping.get("target")
            
            value = self._get_field_value(data, source_field)
            self._set_field_value(result, target_field, value)
        
        return result
    
    def _apply_transformations(self, data: any, transformations: List[dict]) -> any:
        """应用数据转换"""
        for transformation in transformations:
            field = transformation.get("field")
            operation = transformation.get("operation")
            
            if operation == "map":
                mapping_name = transformation.get("mapping")
                current_value = self._get_field_value(data, field)
                new_value = self._apply_mapping(current_value, mapping_name)
                self._set_field_value(data, field, new_value)
            elif operation == "format_date":
                current_value = self._get_field_value(data, field)
                new_value = self._format_date(current_value, transformation.get("format"))
                self._set_field_value(data, field, new_value)
        
        return data
    
    def _get_field_value(self, data: any, field_path: str) -> any:
        """获取字段值"""
        keys = field_path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif hasattr(value, key):
                value = getattr(value, key)
            else:
                return None
        
        return value
    
    def _set_field_value(self, data: dict, field_path: str, value: any):
        """设置字段值"""
        keys = field_path.split(".")
        target = data
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
    
    def _apply_mapping(self, value: any, mapping_name: str) -> any:
        """应用值映射"""
        mappings = {
            "status_to_x12": {
                "CREATED": "AA",
                "CONFIRMED": "AB",
                "IN_TRANSIT": "X6",
                "DELIVERED": "D1"
            }
        }
        
        mapping = mappings.get(mapping_name, {})
        return mapping.get(value, value)
    
    def _format_date(self, value: any, format_str: str) -> str:
        """格式化日期"""
        if isinstance(value, datetime):
            return value.strftime(format_str)
        return value
```

---

## 8. 性能优化

### 8.1 批量处理

```python
class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
    
    def process(self, items: List[any], processor: callable) -> dict:
        """批量处理"""
        results = {
            "total": len(items),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        batches = [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]
        
        for batch in batches:
            for item in batch:
                try:
                    processor(item)
                    results["successful"] += 1
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "item": item,
                        "error": str(e)
                    })
                
                results["processed"] += 1
        
        return results
```

### 8.2 缓存策略

```python
import functools
import hashlib
import json

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client=None):
        self.cache = {}
        self.redis = redis_client
    
    def cache_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> any:
        """获取缓存"""
        if self.redis:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        return self.cache.get(key)
    
    def set(self, key: str, value: any, ttl: int = 3600):
        """设置缓存"""
        serialized = json.dumps(value)
        if self.redis:
            self.redis.setex(key, ttl, serialized)
        else:
            self.cache[key] = value
    
    def cached(self, ttl: int = 3600):
        """缓存装饰器"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.cache_key(func.__name__, *args, **kwargs)
                
                # 尝试从缓存获取
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 存入缓存
                self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
```

### 8.3 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncTransformer:
    """异步转换器"""
    
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def transform_batch(
        self,
        items: List[any],
        transform_func: callable,
        *args,
        **kwargs
    ) -> List[any]:
        """异步批量转换"""
        loop = asyncio.get_event_loop()
        
        # 创建任务
        tasks = [
            loop.run_in_executor(
                self.executor,
                transform_func,
                item,
                *args,
                **kwargs
            )
            for item in items
        ]
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed = []
        for item, result in zip(items, results):
            if isinstance(result, Exception):
                processed.append({
                    "success": False,
                    "item": item,
                    "error": str(result)
                })
            else:
                processed.append({
                    "success": True,
                    "item": item,
                    "result": result
                })
        
        return processed
    
    async def transform_with_semaphore(
        self,
        items: List[any],
        transform_func: callable,
        max_concurrent: int = 5,
        *args,
        **kwargs
    ) -> List[any]:
        """使用信号量限制并发"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def transform_with_limit(item):
            async with semaphore:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    self.executor,
                    transform_func,
                    item,
                    *args,
                    **kwargs
                )
        
        tasks = [transform_with_limit(item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
