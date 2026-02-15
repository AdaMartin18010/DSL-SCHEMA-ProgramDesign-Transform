# TMS Schema形式化定义

## 📑 目录

- [TMS Schema形式化定义](#tms-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 运输订单Schema](#2-运输订单schema)
  - [3. 车辆Schema](#3-车辆schema)
  - [4. 路线Schema](#4-路线schema)
  - [5. 承运人Schema](#5-承运人schema)
  - [6. 运费Schema](#6-运费schema)
  - [7. 类型系统](#7-类型系统)
  - [8. 约束规则](#8-约束规则)
  - [9. 转换函数](#9-转换函数)
  - [10. 形式化定理](#10-形式化定理)
    - [10.1 订单状态完整性定理](#101-订单状态完整性定理)
    - [10.2 路线可行性定理](#102-路线可行性定理)
    - [10.3 运费计算正确性定理](#103-运费计算正确性定理)
  - [11. Python实现示例](#11-python实现示例)
    - [11.1 运输订单类](#111-运输订单类)
    - [11.2 路线规划类](#112-路线规划类)
    - [11.3 运费计算类](#113-运费计算类)

---

## 1. 形式化模型

**定义1（TMS Schema）**：
TMS Schema是一个六元组：

```text
TMS_Schema = (Transportation_Order, Vehicle, Route, Carrier, Freight, Tracking)
```

其中：

- `Transportation_Order`：运输订单Schema
- `Vehicle`：车辆Schema
- `Route`：路线Schema
- `Carrier`：承运人Schema
- `Freight`：运费Schema
- `Tracking`：跟踪Schema

---

## 2. 运输订单Schema

**定义2（Transportation Order Schema）**：

```text
Transportation_Order_Schema = (
  Order_ID, Customer_Info, Cargo_Info, 
  Pickup_Location, Delivery_Location,
  Service_Requirements, Status, Timeline
)
```

**形式化DSL定义**：

```dsl
schema TransportationOrder {
  // 订单基本信息
  order_id: String @required @pattern("^TMS[0-9]{12}$") @unique
  order_number: String @required @unique
  order_type: Enum { FTL, LTL, Express, Dedicated } @required
  service_level: Enum { Standard, Expedited, Guaranteed, White_Glove } @default("Standard")
  
  // 客户信息
  customer: CustomerInfo {
    customer_id: String @required
    customer_name: String @required
    customer_type: Enum { B2B, B2C, Internal } @required
    account_code: Optional<String]
    contract_reference: Optional<String]
  }
  
  // 收发货人信息
  shipper: PartyInfo {
    name: String @required
    address: Address @required
    contact: ContactInfo @required
    location_code: Optional<String]
  }
  
  consignee: PartyInfo {
    name: String @required
    address: Address @required
    contact: ContactInfo @required
    location_code: Optional<String]
    delivery_instructions: Optional<String]
  }
  
  // 货物信息
  cargo: CargoInfo {
    description: String @required
    commodity_type: String @required
    packaging_type: Enum { Pallet, Carton, Crate, Drum, Bulk, Other } @required
    total_packages: Int @required @min(1)
    
    // 重量信息
    weight: WeightInfo {
      actual_weight: Decimal @required @min(0)
      chargeable_weight: Decimal @required @min(0)
      weight_unit: Enum { KG, LB, TON } @default("KG")
    }
    
    // 尺寸信息
    dimensions: Dimensions {
      length: Decimal @required @min(0)
      width: Decimal @required @min(0)
      height: Decimal @required @min(0)
      unit: Enum { CM, IN, M } @default("CM")
    }
    
    // 体积信息
    volume: VolumeInfo {
      total_volume: Decimal @required @min(0)
      volume_unit: Enum { CBM, CFT } @default("CBM")
    }
    
    // 货物价值
    declared_value: Optional<Money]
    currency: Optional<String] @pattern("^[A-Z]{3}$")
    
    // 特殊要求
    hazardous_material: Boolean @default(false)
    hazmat_class: Optional<String]
    temperature_controlled: Boolean @default(false)
    temperature_range: Optional<TemperatureRange]
    fragile: Boolean @default(false)
    stackable: Boolean @default(true)
    
    // 包装清单
    package_list: List<PackageDetail] @required
  }
  
  // 服务要求
  service_requirements: ServiceRequirements {
    scheduled_pickup: DateTime @required
    pickup_time_window: TimeWindow
    scheduled_delivery: DateTime @required
    delivery_time_window: TimeWindow
    appointment_required: Boolean @default(false)
    inside_delivery: Boolean @default(false)
    liftgate_required: Boolean @default(false)
    residential_delivery: Boolean @default(false)
  }
  
  // 订单状态
  status: Enum { 
    Created, Confirmed, Pending_Pickup, Picked_Up, 
    In_Transit, At_Hub, Out_For_Delivery, Delivered, 
    Completed, Cancelled, Exception 
  } @default("Created")
  
  // 分配信息
  assignment: Optional<AssignmentInfo] {
    carrier_id: String
    carrier_name: String
    driver_id: String
    driver_name: String
    vehicle_id: String
    vehicle_number: String
    pro_number: String
    bill_of_lading: String
  }
  
  // 时间线
  timeline: Timeline {
    created_at: DateTime @required
    confirmed_at: Optional[DateTime]
    assigned_at: Optional[DateTime]
    pickup_scheduled_at: Optional[DateTime]
    actual_pickup_at: Optional[DateTime]
    estimated_delivery: Optional[DateTime]
    actual_delivery: Optional[DateTime]
    completed_at: Optional[DateTime]
  }
  
  // 费用信息
  charges: Optional<ChargeInfo] {
    freight_charge: Decimal
    fuel_surcharge: Decimal
    accessorial_charges: List<AccessorialCharge]
    total_charge: Decimal
    currency: String
  }
  
  // 跟踪信息
  tracking: Optional<TrackingInfo] {
    tracking_number: String
    tracking_url: String
    last_status: String
    last_updated: DateTime
  }
  
  // 元数据
  metadata: Metadata {
    source_system: String
    reference_numbers: List<String]
    notes: Optional[String]
    created_by: String
    updated_by: String
  }
} @standard("TMS")

// 辅助类型定义
type Address {
  street_address: String @required
  city: String @required
  state_province: String @required
  postal_code: String @required
  country: String @required @length(2)
  coordinates: Optional<Coordinates]
}

type ContactInfo {
  contact_name: String @required
  phone: String @required
  email: Optional[String] @pattern("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
  department: Optional[String]
}

type TimeWindow {
  earliest: Time
  latest: Time
}

type PackageDetail {
  package_id: String @required
  package_type: String @required
  quantity: Int @required @min(1)
  weight: Decimal @required
  dimensions: Dimensions
  description: Optional[String]
  sku_list: Optional<List<String>]
}
```

---

## 3. 车辆Schema

**定义3（Vehicle Schema）**：

```text
Vehicle_Schema = (
  Vehicle_ID, Vehicle_Info, Capacity,
  Operational_Status, Location, Assignment
)
```

**形式化DSL定义**：

```dsl
schema Vehicle {
  // 车辆基本信息
  vehicle_id: String @required @unique
  vehicle_number: String @required @unique
  
  vehicle_classification: VehicleClassification {
    vehicle_type: Enum { 
      Truck, Van, Trailer, Container, Railcar, 
      Aircraft, Vessel, Motorcycle, Bicycle 
    } @required
    
    truck_type: Enum {
      Semi_Tractor, Box_Truck, Flatbed, Reefer, 
      Tanker, Dump_Truck, Car_Carrier, Tow_Truck
    }
    
    size_category: Enum {
      Light_Duty, Medium_Duty, Heavy_Duty, Extra_Heavy
    }
    
    body_type: Enum {
      Dry_Van, Refrigerated, Flatbed, Tank, Curtain_Side,
      Container, Car_Transporter, Livestock, Tanker
    }
  }
  
  // 车辆规格
  specifications: VehicleSpecifications {
    make: String @required
    model: String @required
    year: Int @required @range(1980, 2030)
    vin: String @required @pattern("^[A-HJ-NPR-Z0-9]{17}$") @unique
    license_plate: String @required
    registration_state: String @length(2)
    
    // 容量规格
    capacity: CapacityInfo {
      max_weight: Decimal @required @unit("KG")
      max_volume: Decimal @required @unit("CBM")
      payload_weight: Decimal @required @unit("KG")
      pallet_positions: Optional[Int]
      container_size: Optional[Enum { _20ft, _40ft, _45ft }]
    }
    
    // 尺寸规格
    dimensions: VehicleDimensions {
      overall_length: Decimal @unit("M")
      overall_width: Decimal @unit("M")
      overall_height: Decimal @unit("M")
      interior_length: Decimal @unit("M")
      interior_width: Decimal @unit("M")
      interior_height: Decimal @unit("M")
      wheelbase: Decimal @unit("M")
    }
    
    // 发动机与燃油
    engine: EngineInfo {
      fuel_type: Enum { Diesel, Gasoline, Electric, Hybrid, CNG, LNG }
      engine_size: Optional[Decimal]
      horsepower: Optional[Int]
      fuel_tank_capacity: Optional[Decimal]
      fuel_efficiency: Optional[Decimal] @unit("KM/L")
    }
    
    // 特殊设备
    equipment: VehicleEquipment {
      has_liftgate: Boolean @default(false)
      liftgate_capacity: Optional[Decimal] @unit("KG")
      has_pallet_jack: Boolean @default(false)
      has_load_bars: Boolean @default(false)
      has_e_track: Boolean @default(false)
      has_refrigeration: Boolean @default(false)
      temp_control_min: Optional[Decimal]
      temp_control_max: Optional[Decimal]
      has_gps: Boolean @default(true)
      has_elog: Boolean @default(true)
    }
  }
  
  // 运营信息
  operational_info: OperationalInfo {
    carrier_id: String @required
    carrier_name: String @required
    owner_operator: Boolean @default(false)
    driver_id: Optional[String]
    driver_name: Optional[String]
    
    operating_authority: OperatingAuthority {
      dot_number: Optional[String]
      mc_number: Optional[String]
      operating_authority_type: Enum { Interstate, Intrastate, Both }
      authority_status: Enum { Active, Inactive, Pending }
      insurance_expiry: Optional[Date]
      registration_expiry: Optional[Date]
    }
    
    safety_ratings: SafetyRatings {
      safety_rating: Optional[Enum { Satisfactory, Conditional, Unsatisfactory }]
      sms_score: Optional[Int] @range(0, 100)
      inspection_rating: Optional[Decimal]
      last_inspection_date: Optional[Date]
    }
  }
  
  // 当前状态
  current_status: VehicleStatus {
    status: Enum { 
      Available, Assigned, In_Transit, Loading, Unloading,
      Maintenance, Out_Of_Service, Off_Duty 
    } @default("Available")
    
    current_location: Optional<Location]
    current_coordinates: Optional<Coordinates]
    heading: Optional[Decimal] @range(0, 360)
    speed: Optional[Decimal] @unit("KM/H")
    
    current_assignment: Optional[AssignmentRef]
    eta_next_stop: Optional[DateTime]
    
    hours_of_service: HOSInfo {
      driving_hours_today: Decimal @unit("HOURS")
      on_duty_hours_today: Decimal @unit("HOURS")
      cycle_hours: Decimal @unit("HOURS")
      available_driving_hours: Decimal @unit("HOURS")
      reset_due: Optional[DateTime]
    }
    
    fuel_level: Optional[Decimal] @range(0, 100) @unit("PERCENT")
    odometer_reading: Optional[Decimal] @unit("KM")
    last_updated: DateTime @required
  }
  
  // 维护记录
  maintenance: MaintenanceInfo {
    last_service_date: Optional[Date]
    next_service_due: Optional[Date]
    service_interval_km: Optional[Decimal]
    service_interval_months: Optional[Int]
    maintenance_records: List<MaintenanceRecord]
  }
  
  // 文档信息
  documents: VehicleDocuments {
    registration_document: Optional[String]
    insurance_document: Optional[String]
    inspection_certificates: List<DocumentRef]
    permits: List<PermitInfo]
  }
} @standard("TMS")

type Location {
  address: Address
  location_code: Optional[String]
  location_type: Enum { Depot, Hub, Customer, Port, Airport, Other }
}

type AssignmentRef {
  order_id: String
  order_number: String
  pickup_location: String
  delivery_location: String
}

type MaintenanceRecord {
  service_date: Date
  service_type: String
  description: String
  cost: Decimal
  odometer_reading: Decimal
  performed_by: String
  next_service_due: Optional[Date]
}
```

---

## 4. 路线Schema

**定义4（Route Schema）**：

```text
Route_Schema = (
  Route_ID, Origin, Destination, Waypoints,
  Distance, Duration, Constraints, Optimization
)
```

**形式化DSL定义**：

```dsl
schema Route {
  // 路线基本信息
  route_id: String @required @unique
  route_number: String @required @unique
  route_name: Optional[String]
  route_type: Enum { 
    Direct, Hub_And_Spoke, Milk_Run, 
    LTL_Network, Multi_Mode, Dynamic 
  } @required
  
  // 起止点信息
  endpoints: RouteEndpoints {
    origin: Location @required
    destination: Location @required
    via_points: List<ViaPoint]
  }
  
  // 路线段
  legs: List<RouteLeg] @required {
    leg_id: String @required
    sequence: Int @required @min(1)
    
    from_location: Location @required
    to_location: Location @required
    
    distance: DistanceInfo {
      total_distance: Decimal @required @unit("KM")
      highway_distance: Decimal @unit("KM")
      urban_distance: Decimal @unit("KM")
      toll_distance: Decimal @unit("KM")
    }
    
    duration: DurationInfo {
      driving_time: Int @required @unit("MINUTES")
      total_time: Int @required @unit("MINUTES")
      break_time: Int @unit("MINUTES")
      rest_time: Int @unit("MINUTES")
      border_crossing_time: Int @unit("MINUTES")
    }
    
    path: PathInfo {
      geometry: GeoJSON_LineString @required
      waypoints: List<Coordinates]
      snapped_points: List<Coordinates]
    }
    
    road_info: RoadInfo {
      road_types: List<RoadType]
      toll_roads: List<TollInfo]
      border_crossings: List<BorderCrossing]
      restrictions: List<RoadRestriction]
    }
  }
  
  // 路线总计
  totals: RouteTotals {
    total_distance: Decimal @required @unit("KM")
    total_duration: Int @required @unit("MINUTES")
    total_toll_cost: Optional[Money]
    estimated_fuel_cost: Optional[Money]
    estimated_driver_cost: Optional[Money]
    total_estimated_cost: Optional[Money]
  }
  
  // 路线约束
  constraints: RouteConstraints {
    vehicle_restrictions: VehicleRestrictions {
      max_weight: Optional[Decimal] @unit("TON")
      max_height: Optional[Decimal] @unit("M")
      max_width: Optional[Decimal] @unit("M")
      hazardous_materials_allowed: Boolean @default(true)
      temperature_controlled_required: Boolean @default(false)
    }
    
    time_constraints: TimeConstraints {
      departure_time_window: Optional[TimeWindow]
      arrival_time_window: Optional[TimeWindow]
      max_trip_duration: Optional[Int] @unit("HOURS")
      required_breaks: Int @default(0)
      overnight_required: Boolean @default(false)
    }
    
    driver_constraints: DriverConstraints {
      max_driving_hours: Decimal @default(11) @unit("HOURS")
      max_duty_hours: Decimal @default(14) @unit("HOURS")
      min_rest_hours: Decimal @default(10) @unit("HOURS")
      required_break_after: Decimal @default(8) @unit("HOURS")
    }
  }
  
  // 优化信息
  optimization: RouteOptimization {
    optimization_objective: Enum { 
      Minimize_Distance, Minimize_Time, Minimize_Cost, 
      Minimize_Carbon, Balanced 
    } @default("Balanced")
    
    optimization_algorithm: Enum {
      Dijkstra, A_Star, Contraction_Hierarchies,
      Genetic_Algorithm, Simulated_Annealing, Custom
    }
    
    optimization_parameters: OptimizationParams {
      distance_weight: Decimal @default(1.0)
      time_weight: Decimal @default(1.0)
      cost_weight: Decimal @default(1.0)
      carbon_weight: Decimal @default(0.5)
    }
    
    alternatives: List<RouteAlternative]
    is_optimized: Boolean @default(false)
    optimization_timestamp: Optional[DateTime]
  }
  
  // 适用性
  applicability: RouteApplicability {
    effective_from: Optional[Date]
    effective_to: Optional[Date]
    active: Boolean @default(true)
    applicable_days: List<Enum { Mon, Tue, Wed, Thu, Fri, Sat, Sun }>
    applicable_vehicle_types: List<String]
  }
  
  // 性能指标
  performance: RoutePerformance {
    average_speed: Optional[Decimal] @unit("KM/H")
    reliability_score: Optional[Decimal] @range(0, 100)
    historical_transit_time: Optional[Int] @unit("MINUTES")
    usage_count: Int @default(0)
  }
} @standard("TMS")

type ViaPoint {
  location: Location
  sequence: Int
  stop_duration: Int @unit("MINUTES")
  time_window: Optional[TimeWindow]
}

type RoadType {
  type: Enum { Highway, Primary, Secondary, Urban, Rural, Ferry }
  distance: Decimal @unit("KM")
}

type TollInfo {
  toll_road_name: String
  toll_cost: Money
  currency: String
  payment_method: Enum { Cash, Card, Electronic, Tag }
}

type BorderCrossing {
  border_name: String
  crossing_point: String
  estimated_delay: Int @unit("MINUTES")
  required_documents: List<String]
}

type RoadRestriction {
  restriction_type: Enum { Weight, Height, Width, Length, Hazardous, Time }
  value: String
  applies_to: List<String>
}

type RouteAlternative {
  alternative_id: String
  description: String
  total_distance: Decimal @unit("KM")
  total_duration: Int @unit("MINUTES")
  total_cost: Money
  preference_rank: Int
}
```

---

## 5. 承运人Schema

**定义5（Carrier Schema）**：

```text
Carrier_Schema = (
  Carrier_ID, Company_Info, Capabilities,
  Certifications, Performance, Financial
)
```

**形式化DSL定义**：

```dsl
schema Carrier {
  // 承运人基本信息
  carrier_id: String @required @unique
  carrier_code: String @required @unique
  company_name: String @required
  legal_name: Optional[String]
  dba_name: Optional[String]
  
  // 公司信息
  company_info: CompanyInfo {
    tax_id: Optional[String]
    duns_number: Optional[String]
    company_type: Enum { Corporation, LLC, Partnership, Sole_Proprietor }
    year_established: Optional[Int]
    employee_count: Optional[Enum { _1_10, _11_50, _51_200, _201_500, _500plus }]
    annual_revenue: Optional<Money]
  }
  
  // 联系信息
  contact: CarrierContact {
    headquarters_address: Address @required
    billing_address: Optional[Address]
    
    primary_contact: ContactInfo @required
    operations_contact: Optional[ContactInfo]
    sales_contact: Optional[ContactInfo]
    dispatch_contact: Optional[ContactInfo]
    
    website: Optional[String] @pattern("^https?://")
    customer_portal: Optional[String]
    api_endpoint: Optional[String]
  }
  
  // 运营资质
  operating_authority: OperatingAuthority {
    dot_number: Optional[String]
    mc_number: Optional[String]
    scac_code: Optional[String] @length(4)
    
    authority_type: Enum { 
      Common_Carrier, Contract_Carrier, Private_Carrier, Broker 
    }
    
    operating_modes: List<Enum { 
      Interstate, Intrastate, International 
    }]
    
    cargo_authorizations: List<Enum {
      General_Freight, Household_Goods, Metal_Sheet,
      Motor_Vehicles, Drive_Tow_Away, Logs_Poles,
      Building_Materials, Mobile_Homes, Machinery,
      Fresh_Produce, Liquids_Gases, Intermodal_Container,
      Passengers, Oilfield_Equipment, Livestock,
      Grain_Feed, Coal_Coke, Meat, Garbage_Refuse,
      Paper_Products, Utilities, Chemicals,
      Beverages, Construction, Water_Well
    }]
    
    authority_status: Enum { Active, Inactive, Revoked, Pending } @default("Active")
    authority_effective_date: Optional[Date]
    authority_expiry_date: Optional[Date]
  }
  
  // 服务能力
  capabilities: CarrierCapabilities {
    service_types: List<Enum { 
      FTL, LTL, Express, White_Glove, Final_Mile,
      Intermodal, Drayage, Cross_Dock, Warehousing,
      International, Air, Ocean, Rail 
    }]
    
    equipment_types: List<Enum {
      Dry_Van, Reefer, Flatbed, Step_Deck, Tanker,
      Container, Double_Drop, Conestoga, Curtain_Side,
      Lowboy, Car_Hauler, Moving_Van, Box_Truck
    }]
    
    fleet_size: FleetSize {
      total_power_units: Optional[Int]
      total_trailers: Optional[Int]
      driver_count: Optional[Int]
      owner_operators: Optional[Int]
    }
    
    geographic_coverage: GeographicCoverage {
      countries: List<String] @length(2)
      states_provinces: List<String>
      service_areas: List<ServiceArea]
    }
    
    special_services: List<Enum {
      Hazmat, Oversize, Temperature_Controlled, 
      White_Glove, Expedited, Trade_Show, 
      Military, Residential, Liftgate
    }]
    
    technology_capabilities: TechCapabilities {
      edi_capable: Boolean @default(false)
      api_integration: Boolean @default(false)
      tracking_system: Optional[String]
      eld_system: Optional[String]
      tms_integration: Boolean @default(false)
      mobile_app: Boolean @default(false)
    }
  }
  
  // 保险信息
  insurance: InsuranceInfo {
    auto_liability: CoverageInfo {
      carrier: String @required
      policy_number: String @required
      coverage_amount: Money @required
      effective_date: Date @required
      expiry_date: Date @required
    }
    
    cargo_insurance: Optional<CoverageInfo]
    general_liability: Optional<CoverageInfo]
    workers_compensation: Optional<CoverageInfo]
    
    certificates: List<InsuranceCertificate]
  }
  
  // 认证与合规
  certifications: Certifications {
    safety_rating: Enum { Satisfactory, Conditional, Unsatisfactory, None }
    ctpat_certified: Boolean @default(false)
    smartway_partner: Boolean @default(false)
    iso_certifications: List<Enum { ISO9001, ISO14001, ISO45001 }>
    
    additional_certifications: List<CertificationDetail]
    
    compliance_scores: ComplianceScores {
      sms_score: Optional[Int] @range(0, 100)
      driver_oos_rate: Optional[Decimal] @range(0, 100)
      vehicle_oos_rate: Optional[Decimal] @range(0, 100)
      crash_rate: Optional[Decimal]
    }
  }
  
  // 绩效评估
  performance: PerformanceMetrics {
    overall_rating: Decimal @range(0, 100)
    rating_tier: Enum { S, A, B, C, D }
    
    on_time_performance: PerformanceDetail {
      on_time_percentage: Decimal @range(0, 100)
      average_delay: Int @unit("MINUTES")
      early_delivery_rate: Decimal @range(0, 100)
    }
    
    service_quality: ServiceQuality {
      damage_claim_rate: Decimal @range(0, 100)
      loss_rate: Decimal @range(0, 100)
      customer_complaint_rate: Decimal @range(0, 100)
      invoice_accuracy: Decimal @range(0, 100)
    }
    
    operational_metrics: OperationalMetrics {
      acceptance_rate: Decimal @range(0, 100)
      tender_rejection_rate: Decimal @range(0, 100)
      pickup_compliance: Decimal @range(0, 100)
      delivery_compliance: Decimal @range(0, 100)
      detention_incidents: Int
    }
    
    financial_stability: FinancialMetrics {
      days_to_pay: Optional[Int]
      credit_rating: Optional[String]
      payment_history: Enum { Excellent, Good, Fair, Poor }
    }
    
    last_evaluation_date: Optional[Date]
    next_evaluation_due: Optional[Date]
  }
  
  // 合同与费率
  contracts: List<CarrierContract]
  
  // 关系管理
  relationship: RelationshipManagement {
    relationship_type: Enum { Strategic, Preferred, Approved, Spot, DoNotUse }
    relationship_start_date: Optional[Date]
    account_manager: Optional[String]
    volume_commitment: Optional<VolumeCommitment]
    lane_preferences: List<String]
  }
  
  // 状态
  status: CarrierStatus {
    active: Boolean @default(true)
    approved: Boolean @default(false)
    onboarding_status: Enum { Pending, InProgress, Complete, Rejected }
    reason_inactive: Optional[String]
  }
} @standard("TMS")

type ServiceArea {
  area_name: String
  area_type: Enum { Country, State, City, Zip, Radius, Custom }
  coverage_details: String
}

type CoverageInfo {
  carrier: String
  policy_number: String
  coverage_amount: Money
  deductible: Optional[Money]
  effective_date: Date
  expiry_date: Date
}

type CertificationDetail {
  certification_name: String
  issuing_body: String
  certificate_number: String
  issue_date: Date
  expiry_date: Optional[Date]
  status: Enum { Active, Expired, Pending, Suspended }
}

type CarrierContract {
  contract_id: String
  contract_number: String
  contract_type: Enum { Dedicated, Lane_Based, Project, Spot }
  effective_date: Date
  expiry_date: Date
  auto_renew: Boolean
  terms_conditions: String
  rate_schedules: List<RateScheduleRef]
}
```

---

## 6. 运费Schema

**定义6（Freight Schema）**：

```text
Freight_Schema = (
  Rate_ID, Rate_Type, Charge_Components,
  Calculation_Rules, Surcharges, Discounts
)
```

**形式化DSL定义**：

```dsl
schema FreightRate {
  // 费率基本信息
  rate_id: String @required @unique
  rate_name: String @required
  rate_type: Enum { 
    Contract, Spot, Tariff, Matrix, 
    Lane_Based, Zone_Based, Distance_Based 
  } @required
  
  // 适用性
  applicability: RateApplicability {
    carrier_id: Optional[String]
    customer_id: Optional[String]
    effective_date: Date @required
    expiry_date: Optional[Date]
    
    origin_scope: GeographicScope {
      country: Optional[String] @length(2)
      state: Optional[String]
      city: Optional[String]
      zip_range: Optional<ZipRange]
      zone: Optional[String]
    }
    
    destination_scope: GeographicScope
    
    service_types: List<Enum { FTL, LTL, Express, Dedicated }>
    equipment_types: List<String>
    
    cargo_restrictions: CargoRestrictions {
      max_weight: Optional[Decimal]
      max_volume: Optional[Decimal]
      commodity_exclusions: List<String]
      hazmat_allowed: Boolean @default(true)
      temperature_controlled: Boolean @default(false)
    }
  }
  
  // 基础费率
  base_rate: BaseRateStructure {
    rate_calculation_method: Enum {
      Per_Mile, Per_KM, Flat_Rate, Per_Weight, 
      Per_Piece, Per_Pallet, Per_CBM, Minimum
    } @required
    
    rate_amount: Money @required
    rate_unit: Enum { Mile, KM, LB, KG, Piece, Pallet, CBM, Trip }
    
    minimum_charge: Money @default(0)
    maximum_charge: Optional[Money]
    
    // FTL费率
    ftl_rates: Optional<FTLRates]
    
    // LTL费率
    ltl_rates: Optional<LTLRates]
    
    // 区域/距离矩阵
    rate_matrix: Optional<RateMatrix]
  }
  
  // 附加费
  surcharges: List<Surcharge] {
    surcharge_id: String @required
    surcharge_name: String @required
    surcharge_type: Enum {
      Fuel, Security, Peak_Season, Residential, 
      Inside_Delivery, Liftgate, Limited_Access,
      Sort_Segregate, Detention, Layover, 
      Driver_Assist, Stop_Off, Laydown, Redelivery,
      Hazmat, Overweight, Oversize, Trade_Show,
      After_Hours, Weekend, Holiday
    }
    
    calculation_method: Enum {
      Percentage_Of_Freight, Flat_Amount, 
      Per_Unit, Per_Mile, Tiered, Custom_Formula
    }
    
    amount: Money @required
    percentage: Optional[Decimal]
    applies_to: Enum { Base_Rate, Total_Charge, Subtotal }
    
    conditions: Optional[SurchargeConditions]
    effective_date: Date @required
    expiry_date: Optional[Date]
  }
  
  // 燃油附加费
  fuel_surcharge: FuelSurcharge {
    enabled: Boolean @default(true)
    calculation_method: Enum {
      Percentage_Based, Index_Based, Fixed_Rate
    }
    
    percentage_rate: Optional[Decimal]
    index_source: Optional[String]
    base_fuel_price: Optional[Money]
    current_fuel_price: Optional[Money]
    
    adjustment_schedule: Enum { Weekly, Monthly, Quarterly }
    last_updated: Optional[DateTime]
  }
  
  // 折扣
  discounts: List<Discount] {
    discount_id: String @required
    discount_name: String @required
    discount_type: Enum {
      Volume, FAK, Earned, Prepay, Multi_Shipment,
      Lane_Specific, Seasonal, Promotional, Contractual
    }
    
    calculation_method: Enum {
      Percentage, Flat_Amount, Per_Unit, Tiered
    }
    
    amount: Optional[Money]
    percentage: Optional<Decimal] @range(0, 100)
    
    applies_to: Enum { Base_Rate, Total_Charge, Specific_Surcharge }
    target_surcharge: Optional[String]
    
    minimum_threshold: Optional<Money]
    volume_threshold: Optional<Decimal]
    
    effective_date: Date
    expiry_date: Optional[Date]
  }
  
  // 最小计费规则
  minimum_charges: MinimumCharges {
    absolute_minimum: Money @default(0)
    minimum_weight: Decimal @default(0)
    minimum_chargeable_weight: Optional[Decimal]
    density_minimum: Optional<Decimal>
    
    // 轻泡货计算
    dimensional_weight_factor: Decimal @default(5000)
    chargeable_weight_rule: Enum { 
      Actual, Dimensional, Greater_Of_Both, Custom 
    } @default("Greater_Of_Both")
  }
  
  // 货币与税费
  currency: CurrencyInfo {
    currency_code: String @length(3) @default("USD")
    exchange_rate: Optional[Decimal]
    rate_date: Optional[Date]
    
    tax_included: Boolean @default(false)
    tax_rate: Optional[Decimal]
    tax_jurisdiction: Optional[String]
  }
  
  // 计费规则
  rating_rules: RatingRules {
    rounding_rule: Enum { Round_Up, Round_Down, Round_Nearest }
    decimal_places: Int @default(2)
    
    weight_breaks: List<WeightBreak]
    
    accessorial_application_order: List<String]
    discount_application_order: List<String]
    
    billable_weight_calculation: Enum {
      Actual_Weight, Dimensional_Weight, 
      Chargeable_Weight, Greater_Of_Actual_Or_Dim
    }
  }
  
  // 历史版本
  version_history: List<RateVersion]
  
  // 审计信息
  audit: AuditInfo {
    created_by: String
    created_at: DateTime
    last_modified_by: String
    last_modified_at: DateTime
    approved_by: Optional[String]
    approved_at: Optional[DateTime]
  }
} @standard("TMS")

type FTLRates {
  truckload_types: List<TruckloadRate]
  mileage_bands: List<MileageBandRate]
  flat_rates: List<LaneFlatRate]
}

type TruckloadRate {
  equipment_type: String
  rate_per_mile: Money
  minimum_miles: Optional[Decimal]
  maximum_miles: Optional[Decimal]
}

type LTLRates {
  freight_class: String
  weight_breaks: List<WeightBreakRate]
  rate_per_cwt: List<RatePerCWT]
  minimum_charge: Money
}

type WeightBreakRate {
  min_weight: Decimal
  max_weight: Decimal
  rate: Money
  rate_unit: Enum { Per_CWT, Per_LB, Flat }
}

type SurchargeConditions {
  min_weight: Optional[Decimal]
  max_weight: Optional[Decimal]
  equipment_types: List<String]
  service_types: List<String]
  origin_zones: List<String]
  destination_zones: List<String]
  time_restrictions: Optional[TimeRestrictions]
}
```

---

## 7. 类型系统

**定义7（TMS数据类型）**：

```text
TMS_Data_Type = Transportation_Order | Vehicle | Route | Carrier | Freight_Rate | Tracking_Event
```

**基本类型定义**：

```dsl
type Coordinates {
  latitude: Decimal @range(-90, 90)
  longitude: Decimal @range(-180, 180)
  accuracy: Optional[Decimal] @unit("METERS")
  altitude: Optional[Decimal] @unit("METERS")
}

type Money {
  amount: Decimal @required @min(0)
  currency: String @required @length(3)
}

type TemperatureRange {
  min_temp: Decimal @unit("CELSIUS")
  max_temp: Decimal @unit("CELSIUS")
  unit: Enum { Celsius, Fahrenheit, Kelvin } @default("Celsius")
}

type GeoJSON_Point {
  type: String @default("Point")
  coordinates: List<Decimal] @length(2)
}

type GeoJSON_LineString {
  type: String @default("LineString")
  coordinates: List<List<Decimal>>
}

type DocumentRef {
  document_type: String
  document_number: String
  issue_date: Date
  expiry_date: Optional[Date]
  issuing_authority: String
  document_url: Optional[String]
}

type PermitInfo {
  permit_type: String
  permit_number: String
  issuing_state: String
  effective_date: Date
  expiry_date: Date
  restrictions: Optional[String]
}

type VolumeCommitment {
  period: Enum { Monthly, Quarterly, Annual }
  minimum_shipments: Int
  minimum_volume: Decimal
  volume_unit: Enum { Shipments, Weight, Revenue }
}

type TimeRestrictions {
  days_of_week: List<Enum { Mon, Tue, Wed, Thu, Fri, Sat, Sun }>
  time_of_day_start: Optional[Time]
  time_of_day_end: Optional[Time]
  seasonal: Optional<String>
}
```

---

## 8. 约束规则

**约束1（订单状态转换规则）**：

```text
∀ order ∈ TransportationOrder:
  valid_status_transition(order.status_from, order.status_to)
  → order_status_valid(order)

状态转换规则：
Created → {Confirmed, Cancelled}
Confirmed → {Pending_Pickup, Exception}
Pending_Pickup → {Picked_Up, Exception}
Picked_Up → {In_Transit, At_Hub, Exception}
In_Transit → {At_Hub, Out_For_Delivery, Exception}
At_Hub → {Out_For_Delivery, In_Transit, Exception}
Out_For_Delivery → {Delivered, Exception}
Delivered → {Completed, Exception}
Exception → {Previous_Status, Cancelled}
```

**约束2（车辆容量约束）**：

```text
∀ vehicle ∈ Vehicle, ∀ assignment ∈ vehicle.assignments:
  sum(assignment.cargo.weight) ≤ vehicle.capacity.payload_weight
  ∧ sum(assignment.cargo.volume) ≤ vehicle.capacity.max_volume
  → vehicle_capacity_valid(vehicle)
```

**约束3（路线可行性约束）**：

```text
∀ route ∈ Route:
  route.total_distance > 0
  ∧ route.total_duration > 0
  ∧ route.legs.non_empty
  → route_feasible(route)
```

**约束4（运费计算约束）**：

```text
∀ rate ∈ FreightRate:
  rate.base_rate.rate_amount ≥ 0
  ∧ rate.applicability.effective_date ≤ today
  ∧ (rate.applicability.expiry_date = null ∨ rate.applicability.expiry_date ≥ today)
  → rate_valid(rate)
```

**约束5（承运人资质约束）**：

```text
∀ carrier ∈ Carrier:
  carrier.operating_authority.authority_status = "Active"
  ∧ carrier.insurance.auto_liability.expiry_date > today
  ∧ carrier.status.approved = true
  → carrier_qualified(carrier)
```

---

## 9. 转换函数

**函数1（订单到运单转换）**：

```text
convert_order_to_waybill: TransportationOrder → Waybill
```

**函数2（路线优化）**：

```text
optimize_route: Route × OptimizationParams → OptimizedRoute
```

**函数3（运费计算）**：

```text
calculate_freight_charge: TransportationOrder × FreightRate × Surcharges → ChargeDetail
```

**函数4（车辆分配）**：

```text
assign_vehicle: TransportationOrder × List<Vehicle> × Constraints → VehicleAssignment
```

**函数5（承运人选择）**：

```text
select_carrier: TransportationOrder × List<Carrier> × SelectionCriteria → CarrierSelection
```

---

## 10. 形式化定理

### 10.1 订单状态完整性定理

**定理1（订单状态完整性）**：

```text
∀ order ∈ TransportationOrder:
  order.status ∈ ValidStatuses
  ∧ order.timeline.created_at ≤ order.timeline.confirmed_at
  ∧ order.timeline.confirmed_at ≤ order.timeline.actual_pickup_at
  ∧ order.timeline.actual_pickup_at ≤ order.timeline.actual_delivery_at
  ∧ order.timeline.actual_delivery_at ≤ order.timeline.completed_at
  → order_state_integrity(order)
```

### 10.2 路线可行性定理

**定理2（路线可行性）**：

```text
∀ route ∈ Route:
  route.legs[0].from_location = route.endpoints.origin
  ∧ route.legs[-1].to_location = route.endpoints.destination
  ∧ ∀ i ∈ [0, len(route.legs)-2]:
      route.legs[i].to_location = route.legs[i+1].from_location
  → route_continuity_valid(route)
```

### 10.3 运费计算正确性定理

**定理3（运费计算正确性）**：

```text
∀ order ∈ TransportationOrder, ∀ rate ∈ FreightRate:
  chargeable_weight = max(order.cargo.weight.actual_weight, 
                          order.cargo.volume.total_volume × rate.minimum_charges.dimensional_weight_factor)
  ∧ base_charge = chargeable_weight × rate.base_rate.rate_amount
  ∧ total_surcharges = sum(surcharge.amount for surcharge in rate.surcharges if applicable)
  ∧ total_discounts = sum(discount.amount for discount in rate.discounts if applicable)
  ∧ total_charge = base_charge + total_surcharges - total_discounts
  ∧ total_charge ≥ rate.base_rate.minimum_charge
  → freight_calculation_correct(order, rate, total_charge)
```

---

## 11. Python实现示例

### 11.1 运输订单类

```python
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
import uuid

class OrderStatus(Enum):
    CREATED = "Created"
    CONFIRMED = "Confirmed"
    PENDING_PICKUP = "Pending_Pickup"
    PICKED_UP = "Picked_Up"
    IN_TRANSIT = "In_Transit"
    AT_HUB = "At_Hub"
    OUT_FOR_DELIVERY = "Out_For_Delivery"
    DELIVERED = "Delivered"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    EXCEPTION = "Exception"

class ServiceLevel(Enum):
    STANDARD = "Standard"
    EXPEDITED = "Expedited"
    GUARANTEED = "Guaranteed"
    WHITE_GLOVE = "White_Glove"

@dataclass
class Address:
    street_address: str
    city: str
    state_province: str
    postal_code: str
    country: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

@dataclass
class ContactInfo:
    contact_name: str
    phone: str
    email: Optional[str] = None
    department: Optional[str] = None

@dataclass
class PartyInfo:
    name: str
    address: Address
    contact: ContactInfo
    location_code: Optional[str] = None
    delivery_instructions: Optional[str] = None

@dataclass
class WeightInfo:
    actual_weight: Decimal
    chargeable_weight: Decimal
    weight_unit: str = "KG"

@dataclass
class Dimensions:
    length: Decimal
    width: Decimal
    height: Decimal
    unit: str = "CM"

@dataclass
class CargoInfo:
    description: str
    commodity_type: str
    packaging_type: str
    total_packages: int
    weight: WeightInfo
    dimensions: Dimensions
    total_volume: Decimal
    volume_unit: str = "CBM"
    declared_value: Optional[Decimal] = None
    currency: Optional[str] = None
    hazardous_material: bool = False
    temperature_controlled: bool = False
    fragile: bool = False

@dataclass
class TransportationOrder:
    """运输订单模型 - 完整实现"""
    
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str = ""
    order_type: str = "FTL"
    service_level: ServiceLevel = ServiceLevel.STANDARD
    
    # 收发货人
    shipper: Optional[PartyInfo] = None
    consignee: Optional[PartyInfo] = None
    
    # 货物信息
    cargo: Optional[CargoInfo] = None
    
    # 服务要求
    scheduled_pickup: Optional[datetime] = None
    scheduled_delivery: Optional[datetime] = None
    
    # 状态
    status: OrderStatus = OrderStatus.CREATED
    
    # 分配信息
    assigned_carrier_id: Optional[str] = None
    assigned_vehicle_id: Optional[str] = None
    
    # 时间线
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    actual_pickup_at: Optional[datetime] = None
    actual_delivery_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 费用
    freight_charge: Optional[Decimal] = None
    total_charge: Optional[Decimal] = None
    
    def validate(self) -> List[str]:
        """验证订单数据完整性"""
        errors = []
        
        if not self.order_number:
            errors.append("订单号不能为空")
        
        if not self.shipper:
            errors.append("发货人信息不能为空")
        
        if not self.consignee:
            errors.append("收货人信息不能为空")
        
        if not self.cargo:
            errors.append("货物信息不能为空")
        
        if self.cargo and self.cargo.weight.actual_weight <= 0:
            errors.append("货物重量必须大于0")
        
        if not self.scheduled_pickup:
            errors.append("计划取货时间不能为空")
        
        if not self.scheduled_delivery:
            errors.append("计划配送时间不能为空")
        
        if self.scheduled_pickup and self.scheduled_delivery:
            if self.scheduled_pickup >= self.scheduled_delivery:
                errors.append("计划取货时间必须早于计划配送时间")
        
        return errors
    
    def update_status(self, new_status: OrderStatus, timestamp: Optional[datetime] = None) -> bool:
        """更新订单状态，带状态转换验证"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 定义允许的状态转换
        valid_transitions = {
            OrderStatus.CREATED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PENDING_PICKUP, OrderStatus.EXCEPTION],
            OrderStatus.PENDING_PICKUP: [OrderStatus.PICKED_UP, OrderStatus.EXCEPTION],
            OrderStatus.PICKED_UP: [OrderStatus.IN_TRANSIT, OrderStatus.AT_HUB, OrderStatus.EXCEPTION],
            OrderStatus.IN_TRANSIT: [OrderStatus.AT_HUB, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.EXCEPTION],
            OrderStatus.AT_HUB: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.IN_TRANSIT, OrderStatus.EXCEPTION],
            OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.EXCEPTION],
            OrderStatus.DELIVERED: [OrderStatus.COMPLETED, OrderStatus.EXCEPTION],
            OrderStatus.EXCEPTION: [OrderStatus.CANCELLED]  # 从异常状态可以取消
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            return False
        
        self.status = new_status
        
        # 更新时间线
        if new_status == OrderStatus.CONFIRMED:
            self.confirmed_at = timestamp
        elif new_status == OrderStatus.PICKED_UP:
            self.actual_pickup_at = timestamp
        elif new_status == OrderStatus.DELIVERED:
            self.actual_delivery_at = timestamp
        elif new_status == OrderStatus.COMPLETED:
            self.completed_at = timestamp
        
        return True
    
    def calculate_transit_time(self) -> Optional[int]:
        """计算实际运输时间（分钟）"""
        if self.actual_pickup_at and self.actual_delivery_at:
            delta = self.actual_delivery_at - self.actual_pickup_at
            return int(delta.total_seconds() / 60)
        return None
    
    def is_delayed(self) -> bool:
        """检查是否延误"""
        if self.status in [OrderStatus.DELIVERED, OrderStatus.COMPLETED]:
            if self.actual_delivery_at and self.scheduled_delivery:
                return self.actual_delivery_at > self.scheduled_delivery
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "order_number": self.order_number,
            "order_type": self.order_type,
            "service_level": self.service_level.value,
            "status": self.status.value,
            "scheduled_pickup": self.scheduled_pickup.isoformat() if self.scheduled_pickup else None,
            "scheduled_delivery": self.scheduled_delivery.isoformat() if self.scheduled_delivery else None,
            "actual_pickup": self.actual_pickup_at.isoformat() if self.actual_pickup_at else None,
            "actual_delivery": self.actual_delivery_at.isoformat() if self.actual_delivery_at else None,
            "assigned_carrier_id": self.assigned_carrier_id,
            "freight_charge": str(self.freight_charge) if self.freight_charge else None
        }
```

### 11.2 路线规划类

```python
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RoutePoint:
    """路线点"""
    location_id: str
    name: str
    address: Address
    coordinates: Tuple[float, float]  # (latitude, longitude)
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    service_duration: int = 30  # 服务时间（分钟）

@dataclass
class RouteLeg:
    """路线段"""
    from_point: RoutePoint
    to_point: RoutePoint
    distance: Decimal  # 公里
    duration: int  # 分钟
    geometry: List[Tuple[float, float]] = field(default_factory=list)

class RouteOptimizer:
    """路线优化器 - 使用最近邻算法和2-opt改进"""
    
    def __init__(self):
        self.earth_radius = 6371  # 地球半径（公里）
    
    def haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """计算两点间的大圆距离"""
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return self.earth_radius * c
    
    def nearest_neighbor_tsp(self, points: List[RoutePoint], start_idx: int = 0) -> List[int]:
        """最近邻算法求解TSP"""
        n = len(points)
        unvisited = set(range(n))
        unvisited.remove(start_idx)
        
        route = [start_idx]
        current = start_idx
        
        while unvisited:
            nearest = min(unvisited, 
                         key=lambda x: self.haversine_distance(
                             points[current].coordinates, 
                             points[x].coordinates
                         ))
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return route
    
    def two_opt_improvement(self, points: List[RoutePoint], route: List[int]) -> List[int]:
        """2-opt局部搜索改进"""
        improved = True
        n = len(route)
        
        while improved:
            improved = False
            for i in range(1, n - 2):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue
                    
                    # 计算当前路段长度
                    current_dist = (
                        self.haversine_distance(
                            points[route[i-1]].coordinates,
                            points[route[i]].coordinates
                        ) +
                        self.haversine_distance(
                            points[route[j-1]].coordinates,
                            points[route[j]].coordinates
                        )
                    )
                    
                    # 计算交换后的路段长度
                    new_dist = (
                        self.haversine_distance(
                            points[route[i-1]].coordinates,
                            points[route[j-1]].coordinates
                        ) +
                        self.haversine_distance(
                            points[route[i]].coordinates,
                            points[route[j]].coordinates
                        )
                    )
                    
                    if new_dist < current_dist:
                        # 执行2-opt交换
                        route[i:j] = reversed(route[i:j])
                        improved = True
        
        return route
    
    def optimize_route(self, points: List[RoutePoint]) -> Tuple[List[RoutePoint], float, int]:
        """优化路线"""
        if len(points) <= 2:
            total_distance = sum(
                self.haversine_distance(points[i].coordinates, points[i+1].coordinates)
                for i in range(len(points) - 1)
            )
            return points, total_distance, 0
        
        # 使用最近邻算法生成初始解
        initial_route = self.nearest_neighbor_tsp(points)
        
        # 使用2-opt改进
        improved_route = self.two_opt_improvement(points, initial_route)
        
        # 构建优化后的路线
        optimized_points = [points[i] for i in improved_route]
        
        # 计算总距离和总时间
        total_distance = sum(
            self.haversine_distance(
                optimized_points[i].coordinates, 
                optimized_points[i+1].coordinates
            )
            for i in range(len(optimized_points) - 1)
        )
        
        # 估算总时间（假设平均速度60km/h）
        total_time = int(total_distance / 60 * 60)  # 分钟
        total_time += sum(p.service_duration for p in optimized_points)
        
        return optimized_points, total_distance, total_time
```

### 11.3 运费计算类

```python
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class Surcharge:
    """附加费"""
    name: str
    amount: Decimal
    percentage: Optional[Decimal] = None
    applies_to: str = "base"

@dataclass
class Discount:
    """折扣"""
    name: str
    amount: Optional[Decimal] = None
    percentage: Optional[Decimal] = None

@dataclass
class FreightCharge:
    """运费明细"""
    base_charge: Decimal
    surcharges: List[Surcharge]
    discounts: List[Discount]
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    currency: str = "USD"

class FreightCalculator:
    """运费计算器"""
    
    # 体积系数 (CBM to KG)
    CBM_TO_KG_FACTOR = Decimal("1000")
    
    # 燃油附加费率
    FUEL_SURCHARGE_RATE = Decimal("0.18")
    
    def __init__(self):
        pass
    
    def calculate_chargeable_weight(
        self, 
        actual_weight: Decimal, 
        volume: Decimal,
        dim_factor: Optional[Decimal] = None
    ) -> Decimal:
        """计算计费重量"""
        if dim_factor is None:
            dim_factor = self.CBM_TO_KG_FACTOR
        
        # 体积重量 = 体积 × 体积系数
        dimensional_weight = volume * dim_factor
        
        # 计费重量 = max(实际重量, 体积重量)
        chargeable_weight = max(actual_weight, dimensional_weight)
        
        return chargeable_weight.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def calculate_base_charge(
        self,
        chargeable_weight: Decimal,
        rate_per_kg: Decimal,
        minimum_charge: Decimal = Decimal("0")
    ) -> Decimal:
        """计算基础运费"""
        base = chargeable_weight * rate_per_kg
        
        # 应用最低收费
        if minimum_charge > 0 and base < minimum_charge:
            base = minimum_charge
        
        return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def calculate_surcharges(
        self,
        base_charge: Decimal,
        fuel_surcharge: bool = True,
        residential_delivery: bool = False,
        liftgate_required: bool = False,
        inside_delivery: bool = False
    ) -> List[Surcharge]:
        """计算附加费"""
        surcharges = []
        
        # 燃油附加费
        if fuel_surcharge:
            fuel_amount = (base_charge * self.FUEL_SURCHARGE_RATE).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            surcharges.append(Surcharge(
                name="Fuel Surcharge",
                amount=fuel_amount,
                percentage=self.FUEL_SURCHARGE_RATE
            ))
        
        # 住宅配送费
        if residential_delivery:
            surcharges.append(Surcharge(
                name="Residential Delivery",
                amount=Decimal("12.00")
            ))
        
        # 尾板费
        if liftgate_required:
            surcharges.append(Surcharge(
                name="Liftgate Service",
                amount=Decimal("15.00")
            ))
        
        # 室内配送费
        if inside_delivery:
            surcharges.append(Surcharge(
                name="Inside Delivery",
                amount=Decimal("25.00")
            ))
        
        return surcharges
    
    def calculate_total(
        self,
        base_charge: Decimal,
        surcharges: List[Surcharge],
        discounts: List[Discount],
        tax_rate: Decimal = Decimal("0")
    ) -> FreightCharge:
        """计算总运费"""
        # 计算附加费总额
        surcharge_total = sum(s.amount for s in surcharges)
        
        # 计算折扣前小计
        subtotal = base_charge + surcharge_total
        
        # 应用折扣
        discount_total = Decimal("0")
        for discount in discounts:
            if discount.amount:
                discount_total += discount.amount
            elif discount.percentage:
                discount_total += (subtotal * discount.percentage / 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
        
        # 确保折扣不超过小计
        discount_total = min(discount_total, subtotal)
        
        # 计算税费
        taxable_amount = subtotal - discount_total
        tax = (taxable_amount * tax_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # 计算总计
        total = taxable_amount + tax
        
        return FreightCharge(
            base_charge=base_charge,
            surcharges=surcharges,
            discounts=discounts,
            subtotal=subtotal,
            tax=tax,
            total=total
        )
    
    def calculate_freight(
        self,
        actual_weight: Decimal,  # KG
        volume: Decimal,  # CBM
        rate_per_kg: Decimal,
        minimum_charge: Decimal = Decimal("50.00"),
        dim_factor: Optional[Decimal] = None,
        **surcharge_options
    ) -> FreightCharge:
        """完整运费计算"""
        # 计算计费重量
        chargeable_weight = self.calculate_chargeable_weight(
            actual_weight, volume, dim_factor
        )
        
        # 计算基础运费
        base_charge = self.calculate_base_charge(
            chargeable_weight, rate_per_kg, minimum_charge
        )
        
        # 计算附加费
        surcharges = self.calculate_surcharges(base_charge, **surcharge_options)
        
        # 计算总计
        return self.calculate_total(base_charge, surcharges, [])


# 使用示例
if __name__ == "__main__":
    # 运费计算示例
    calculator = FreightCalculator()
    
    result = calculator.calculate_freight(
        actual_weight=Decimal("150"),  # 150kg
        volume=Decimal("2.5"),  # 2.5 CBM
        rate_per_kg=Decimal("0.85"),  # $0.85/kg
        minimum_charge=Decimal("75.00"),
        fuel_surcharge=True,
        residential_delivery=True,
        liftgate_required=False
    )
    
    print(f"基础运费: ${result.base_charge}")
    print(f"附加费: ${sum(s.amount for s in result.surcharges)}")
    print(f"总计: ${result.total}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
