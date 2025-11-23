# 海运与航运Schema形式化定义

## 📑 目录

- [海运与航运Schema形式化定义](#海运与航运schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 船舶信息Schema](#2-船舶信息schema)
  - [3. 货物信息Schema](#3-货物信息schema)
  - [4. 航线信息Schema](#4-航线信息schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)
    - [8.1 船舶信息完整性定理](#81-船舶信息完整性定理)
    - [8.2 货物追踪正确性定理](#82-货物追踪正确性定理)

---

## 1. 形式化模型

**定义1（海运与航运Schema）**：
海运与航运Schema是一个四元组：

```text
Maritime_Schema = (Vessel_Info, Cargo_Info,
                  Route_Info, Port_Info)
```

其中：

- `Vessel_Info`：船舶信息Schema
- `Cargo_Info`：货物信息Schema
- `Route_Info`：航线信息Schema
- `Port_Info`：港口信息Schema

---

## 2. 船舶信息Schema

**定义2（船舶信息Schema）**：

```text
Vessel_Info_Schema = (Vessel_Basic_Info, Vessel_Certificate,
                     Vessel_Position, Vessel_Status)
```

**形式化DSL定义**：

```dsl
schema VesselInfo {
  vessel_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  imo_number: String @pattern("^[0-9]{7}$") @required @unique
  vessel_name: String @max_length(200) @required

  vessel_basic_info: {
    vessel_type: Enum { ContainerShip, BulkCarrier, Tanker, GeneralCargo, Other } @required
    flag_state: String @length(2) @pattern("^[A-Z]{2}$") @required
    call_sign: String @max_length(10)
    mmsi: String @pattern("^[0-9]{9}$")
    gross_tonnage: Decimal @precision(10,2) @unit("tons")
    net_tonnage: Decimal @precision(10,2) @unit("tons")
    deadweight_tonnage: Decimal @precision(10,2) @unit("tons")
    length_overall: Decimal @precision(8,2) @unit("meters")
    breadth: Decimal @precision(8,2) @unit("meters")
    draft: Decimal @precision(6,2) @unit("meters")
    year_built: Integer @range(1900, 2100)
    builder: String @max_length(200)
  } @required

  vessel_certificate: {
    registration_certificate: {
      certificate_number: String @max_length(50)
      issue_date: Date @format("YYYY-MM-DD")
      expiry_date: Date @format("YYYY-MM-DD")
      issuing_authority: String @max_length(200)
    }
    safety_certificate: {
      certificate_number: String @max_length(50)
      issue_date: Date @format("YYYY-MM-DD")
      expiry_date: Date @format("YYYY-MM-DD")
      issuing_authority: String @max_length(200)
    }
    pollution_prevention_certificate: {
      certificate_number: String @max_length(50)
      issue_date: Date @format("YYYY-MM-DD")
      expiry_date: Date @format("YYYY-MM-DD")
      issuing_authority: String @max_length(200)
    }
  }

  vessel_position: {
    latitude: Decimal @precision(8,6) @range(-90.0, 90.0) @required
    longitude: Decimal @precision(9,6) @range(-180.0, 180.0) @required
    course: Decimal @precision(5,2) @range(0.0, 360.0) @unit("degrees")
    speed: Decimal @precision(5,2) @range(0.0, 50.0) @unit("knots")
    heading: Decimal @precision(5,2) @range(0.0, 360.0) @unit("degrees")
    position_time: DateTime @required
  } @required

  vessel_status: {
    status: Enum { AtPort, Underway, Anchored, Moored, Aground } @required
    port_name: String @max_length(100)
    port_code: String @pattern("^[A-Z]{5}$")
    next_port: String @max_length(100)
    next_port_code: String @pattern("^[A-Z]{5}$")
    eta: DateTime
  } @required
} @standard("IMO")
```

---

## 3. 货物信息Schema

**定义3（货物信息Schema）**：

```text
Cargo_Info_Schema = (Cargo_Basic_Info, Cargo_Status,
                    Cargo_Position, Cargo_Tracking)
```

**形式化DSL定义**：

```dsl
schema CargoInfo {
  cargo_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  cargo_name: String @max_length(200) @required
  cargo_type: Enum { Container, Bulk, BreakBulk, Liquid, Other } @required

  cargo_basic_info: {
    shipper: String @max_length(200) @required
    consignee: String @max_length(200) @required
    weight: Decimal @precision(10,2) @unit("kg") @required
    volume: Decimal @precision(10,2) @unit("cubic meters")
    quantity: Integer @range(1, 999999)
    unit: String @max_length(20)
    hs_code: String @pattern("^[0-9]{6,10}$")
    value: Decimal @precision(12,2) @unit("USD")
    currency: String @length(3) @pattern("^[A-Z]{3}$") @default("USD")
  } @required

  cargo_status: {
    status: Enum { Booked, Loaded, InTransit, Discharged, Delivered } @required
    loading_port: String @max_length(100)
    loading_port_code: String @pattern("^[A-Z]{5}$")
    discharge_port: String @max_length(100)
    discharge_port_code: String @pattern("^[A-Z]{5}$")
    loading_date: DateTime
    discharge_date: DateTime
  } @required

  cargo_position: {
    current_location: Enum { AtPort, OnVessel, InTransit, AtWarehouse } @required
    vessel_id: Optional<String> @pattern("^[A-Z0-9]{10}$")
    port_name: String @max_length(100)
    port_code: String @pattern("^[A-Z]{5}$")
    container_number: String @pattern("^[A-Z]{4}[0-9]{7}$")
    warehouse_location: String @max_length(200)
  } @required

  cargo_tracking: List<TrackingEvent> {
    event_type: Enum { Booked, Loaded, Departed, Arrived, Discharged, Delivered } @required
    event_time: DateTime @required
    event_location: String @max_length(200)
    event_description: String @max_length(500)
  } @required
} @standard("EDIFACT")
```

---

## 4. 航线信息Schema

**定义4（航线信息Schema）**：

```text
Route_Info_Schema = (Route_Plan, Route_Execution,
                    Route_Change, Route_Statistics)
```

**形式化DSL定义**：

```dsl
schema RouteInfo {
  route_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  vessel_id: String @pattern("^[A-Z0-9]{10}$") @required
  voyage_number: String @max_length(20) @required

  route_plan: {
    origin_port: String @max_length(100) @required
    origin_port_code: String @pattern("^[A-Z]{5}$") @required
    destination_port: String @max_length(100) @required
    destination_port_code: String @pattern("^[A-Z]{5}$") @required
    intermediate_ports: List<Port> {
      port_name: String @max_length(100) @required
      port_code: String @pattern("^[A-Z]{5}$") @required
      port_order: Integer @required
      eta: DateTime
      etd: DateTime
    }
    planned_departure: DateTime @required
    planned_arrival: DateTime @required
    planned_distance: Decimal @precision(10,2) @unit("nautical miles")
    planned_duration: Integer @range(1, 365) @unit("days")
  } @required

  route_execution: {
    actual_departure: DateTime
    actual_arrival: DateTime
    actual_distance: Decimal @precision(10,2) @unit("nautical miles")
    actual_duration: Integer @range(1, 365) @unit("days")
    average_speed: Decimal @precision(5,2) @unit("knots")
    fuel_consumption: Decimal @precision(10,2) @unit("tons")
  }

  route_change: List<RouteChange> {
    change_reason: String @max_length(500) @required
    change_time: DateTime @required
    original_route: RoutePlan
    new_route: RoutePlan @required
    approved_by: String @max_length(100)
  }

  route_statistics: {
    total_voyages: Integer @range(0, 999999)
    on_time_arrival_rate: Decimal @precision(5,2) @range(0.0, 100.0) @unit("%")
    average_delay_hours: Decimal @precision(6,2) @unit("hours")
    fuel_efficiency: Decimal @precision(8,2) @unit("tons/nautical mile")
  }
} @standard("IMO")
```

---

## 5. 类型系统

**定义5（海运与航运数据类型）**：

```text
Maritime_Data_Type = Vessel_Info | Cargo_Info | Route_Info |
                    Port_Info | Tracking_Event | Route_Change
```

**基本类型定义**：

```dsl
type VesselPosition {
  latitude: Decimal @precision(8,6) @range(-90.0, 90.0) @required
  longitude: Decimal @precision(9,6) @range(-180.0, 180.0) @required
  timestamp: DateTime @required
}

type CargoTracking {
  event_type: Enum { Booked, Loaded, Departed, Arrived, Discharged, Delivered } @required
  event_time: DateTime @required
  event_location: String @required
}

type RoutePlan {
  origin_port: String @required
  destination_port: String @required
  planned_departure: DateTime @required
  planned_arrival: DateTime @required
}
```

---

## 6. 约束规则

**约束1（船舶信息完整性）**：

```text
∀ vessel ∈ Vessel_Info:
  vessel.vessel_id ≠ ∅
  ∧ vessel.imo_number ≠ ∅
  ∧ vessel.vessel_name ≠ ∅
  ∧ validate_imo_number(vessel.imo_number)
```

**约束2（货物信息完整性）**：

```text
∀ cargo ∈ Cargo_Info:
  cargo.cargo_id ≠ ∅
  ∧ cargo.cargo_name ≠ ∅
  ∧ cargo.cargo_status.status ∈ {Booked, Loaded, InTransit, Discharged, Delivered}
  ∧ validate_cargo_tracking(cargo.cargo_tracking)
```

**约束3（航线信息有效性）**：

```text
∀ route ∈ Route_Info:
  route.route_id ≠ ∅
  ∧ route.vessel_id ≠ ∅
  ∧ route.route_plan.origin_port ≠ ∅
  ∧ route.route_plan.destination_port ≠ ∅
  ∧ route.route_plan.planned_departure < route.route_plan.planned_arrival
```

---

## 7. 转换函数

**函数1（EDIFACT到XML转换）**：

```text
convert_EDIFACT_to_XML: EDIFACT_Message → XML_Document
```

**函数2（XML到EDIFACT转换）**：

```text
convert_XML_to_EDIFACT: XML_Document → EDIFACT_Message
```

**函数3（货物追踪验证）**：

```text
validate_cargo_tracking: Cargo_Info → Bool
```

---

## 8. 形式化定理

### 8.1 船舶信息完整性定理

**定理1（船舶信息完整性）**：

```text
∀ vessel ∈ Vessel_Info:
  validate_vessel_info(vessel)
  → vessel_info_integrity(vessel)
  ∧ certificate_validity(vessel.vessel_certificate)
```

### 8.2 货物追踪正确性定理

**定理2（货物追踪正确性）**：

```text
∀ cargo ∈ Cargo_Info:
  validate_cargo_tracking(cargo.cargo_tracking)
  → cargo_tracking_correctness(cargo)
  ∧ status_consistency(cargo.cargo_status, cargo.cargo_tracking)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
