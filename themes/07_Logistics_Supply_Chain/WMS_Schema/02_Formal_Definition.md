# WMS Schema形式化定义

## 📑 目录

- [WMS Schema形式化定义](#wms-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 库存Schema](#2-库存schema)
  - [3. 货位Schema](#3-货位schema)
  - [4. 作业任务Schema](#4-作业任务schema)
  - [5. 入库Schema](#5-入库schema)
  - [6. 出库Schema](#6-出库schema)
  - [7. 盘点Schema](#7-盘点schema)
  - [8. 类型系统](#8-类型系统)
  - [9. 约束规则](#9-约束规则)
  - [10. 转换函数](#10-转换函数)
  - [11. 形式化定理](#11-形式化定理)
  - [12. Python实现示例](#12-python实现示例)

---

## 1. 形式化模型

**定义1（WMS Schema）**：
WMS Schema是一个七元组：

```
WMS_Schema = (Inventory, Location, Task, Inbound, Outbound, Cycle_Count, Movement)
```

其中：

- `Inventory`：库存Schema
- `Location`：货位Schema
- `Task`：作业任务Schema
- `Inbound`：入库Schema
- `Outbound`：出库Schema
- `Cycle_Count`：盘点Schema
- `Movement`：库存移动Schema

---

## 2. 库存Schema

**定义2（Inventory Schema）**：

```
Inventory_Schema = (
  Inventory_ID, SKU_Info, Quantity,
  Location, Status, Attributes, Tracking
)
```

**形式化DSL定义**：

```dsl
schema Inventory {
  // 库存唯一标识
  inventory_id: UUID @required @unique @default("gen_random_uuid()")

  // SKU信息
  sku: SKUInfo {
    sku_code: String @required @max_length(50)
    sku_name: String @required @max_length(200)
    gtin: Optional[String] @pattern("^[0-9]{8,14}$")
    upc: Optional[String] @pattern("^[0-9]{12}$")
    ean: Optional[String] @pattern("^[0-9]{13}$")

    // 分类
    category: Optional[String]
    brand: Optional[String]
    commodity_code: Optional[String]

    // 物理属性
    unit_weight: Decimal @unit("KG") @min(0)
    unit_volume: Decimal @unit("CBM") @min(0)
    unit_length: Decimal @unit("CM") @min(0)
    unit_width: Decimal @unit("CM") @min(0)
    unit_height: Decimal @unit("CM") @min(0)

    // 包装
    units_per_carton: Optional[Int] @min(1)
    cartons_per_pallet: Optional[Int] @min(1)
    units_per_pallet: Optional[Int] @computed("units_per_carton * cartons_per_pallet")

    // 存储要求
    storage_condition: Enum { Ambient, Refrigerated, Frozen, Climate_Controlled }
    temperature_min: Optional[Decimal] @unit("CELSIUS")
    temperature_max: Optional[Decimal] @unit("CELSIUS")
    humidity_min: Optional[Decimal] @range(0, 100)
    humidity_max: Optional[Decimal] @range(0, 100)

    // 特殊属性
    fragile: Boolean @default(false)
    stackable: Boolean @default(true)
    hazardous: Boolean @default(false)
    hazardous_class: Optional[String]

    // ABC分类
    abc_class: Enum { A, B, C } @default("C")
    velocity_class: Enum { Fast, Medium, Slow } @default("Slow")
  }

  // 批次信息
  batch: Optional[BatchInfo] {
    batch_number: String @required
    lot_number: Optional[String]
    manufacturing_date: Optional[Date]
    expiration_date: Optional[Date]
    shelf_life_days: Optional[Int] @computed("expiration_date - manufacturing_date")

    // 供应商批次
    supplier_batch: Optional[String]
    po_number: Optional[String]

    // 质量状态
    quality_status: Enum { Good, Damaged, Expired, Hold, Quarantine } @default("Good")
    quarantine_reason: Optional[String]
    release_date: Optional[Date]
  }

  // 序列号（高价值/追踪商品）
  serial_numbers: List<String]

  // 货位信息
  location: LocationRef {
    location_code: String @required
    zone_code: String
    area_code: String
    aisle: String
    bay: String
    level: String
    position: String

    // 位置坐标（用于导航）
    coordinates: Optional[Coordinates]
  }

  // 数量信息
  quantity: QuantityInfo {
    on_hand: Int @required @min(0)
    allocated: Int @required @min(0) @default(0)
    picked: Int @required @min(0) @default(0)
    available: Int @computed("on_hand - allocated - picked")
    reserved: Int @required @min(0) @default(0)
    in_transit: Int @required @min(0) @default(0)
  }

  // 库存状态
  inventory_status: Enum {
    Available,    // 可用
    Frozen,       // 冻结
    Blocked,      // 锁定
    Quarantine,   // 隔离
    Damaged,      // 残次
    Expired       // 过期
  } @default("Available")

  // 冻结信息
  freeze_info: Optional[FreezeInfo] {
    freeze_type: Enum { Quality_Check, Cycle_Count, Customer_Hold, Recall }
    freeze_reason: String
    frozen_by: String
    frozen_at: DateTime
    expected_release: Optional[DateTime]
    released_at: Optional[DateTime]
    released_by: Optional[String]
  }

  // 所有者信息
  ownership: OwnershipInfo {
    owner_code: String @required @default("OWN")
    owner_name: String
    supplier_code: Optional[String]
    supplier_name: Optional[String]
    consignment: Boolean @default(false)
  }

  // 成本信息
  costing: CostingInfo {
    unit_cost: Optional[Decimal]
    currency: Optional[String] @length(3)
    cost_method: Enum { FIFO, LIFO, Average, Standard, Specific }

    // 追溯成本
    po_cost: Optional[Decimal]
    freight_cost: Optional[Decimal]
    duty_cost: Optional[Decimal]
    total_landed_cost: Optional[Decimal]
  }

  // 接收信息
  receipt_info: ReceiptInfo {
    receipt_id: String
    receipt_number: String
    receipt_date: Date
    asn_number: Optional[String]
    carrier_code: Optional[String]
    tracking_number: Optional[String]
  }

  // 时间戳
  timestamps: InventoryTimestamps {
    received_at: DateTime @required
    putaway_at: DateTime
    last_movement_at: Optional[DateTime]
    last_counted_at: Optional[DateTime]
    expiration_warning_at: Optional[DateTime]
    created_at: DateTime @default("CURRENT_TIMESTAMP")
    updated_at: DateTime @default("CURRENT_TIMESTAMP")
  }

  // 元数据
  metadata: Metadata {
    source_system: String
    reference_documents: List[String]
    custom_attributes: Map<String, String>
    notes: Optional[String]
  }
} @standard("WMS")

// 辅助类型
type QuantityInfo {
  on_hand: Int
  allocated: Int
  picked: Int
  reserved: Int
  in_transit: Int
}

type FreezeInfo {
  freeze_type: Enum { Quality_Check, Cycle_Count, Customer_Hold, Recall }
  freeze_reason: String
  frozen_by: String
  frozen_at: DateTime
  expected_release: Optional[DateTime]
}
```

---

## 3. 货位Schema

**定义3（Location Schema）**：

```
Location_Schema = (
  Location_Code, Hierarchy, Type,
  Capacity, Attributes, Status, Coordinates
)
```

**形式化DSL定义**：

```dsl
schema Location {
  // 货位编码
  location_code: String @required @unique @max_length(50)
  location_name: String @max_length(100)
  location_barcode: Optional[String]

  // 层级结构
  hierarchy: LocationHierarchy {
    warehouse_code: String @required
    zone: ZoneInfo {
      zone_code: String @required
      zone_name: String
      zone_type: Enum {
        Receiving,    // 收货区
        Putaway,      // 上架区
        Bulk,         // 存储区
        Picking,      // 拣货区
        Packing,      // 包装区
        Shipping,     // 发货区
        Cross_Dock,   // 越库区
        Returns,      // 退货区
        Quarantine    // 隔离区
      }
    }

    area: AreaInfo {
      area_code: String
      area_name: String
      area_function: Enum { Normal, Cold, Frozen, Hazardous, Valuable, Oversize }
    }

    aisle: AisleInfo {
      aisle_code: String
      aisle_name: String
      aisle_direction: Enum { One_Way, Two_Way }
      aisle_type: Enum { Wide, Narrow, Very_Narrow }
    }

    bay: BayInfo {
      bay_code: String
      bay_number: Int
    }

    level: LevelInfo {
      level_code: String
      level_number: Int @min(0)
      level_height: Decimal @unit("M")
    }

    position: PositionInfo {
      position_code: String
      position_number: Int
    }

    // 完整路径
    location_path: String @computed("zone_code/area_code/aisle_code/bay_code/level_code/position_code")
  }

  // 货位类型
  location_type: LocationType {
    primary_type: Enum {
      Floor,           // 地面
      Pallet_Rack,     // 托盘货架
      Shelving,        // 层架
      Cantilever,      // 悬臂架
      Flow_Rack,       // 流利架
      Drive_In,        // 驶入式货架
      Mezzanine,       // 阁楼
      Bin,             // 料箱
      Cage,            // 笼
      Floor_Stack      // 地面堆垛
    }

    function_type: Enum {
      Reserve,         // 存储货位
      Forward_Pick,    // 拣货货位
      Dynamic,         // 动态货位
      Consolidation,   // 集货货位
      Staging,         // 暂存货位
      Dock,            // 月台
      Office           // 办公
    }

    size_type: Enum { Small, Medium, Large, Extra_Large }
  }

  // 容量规格
  capacity: LocationCapacity {
    max_weight: Decimal @required @unit("KG") @min(0)
    max_volume: Decimal @required @unit("CBM") @min(0)
    max_pallets: Int @min(0) @default(1)
    max_cartons: Optional[Int]
    max_units: Optional[Int]

    // 尺寸
    dimensions: Dimensions {
      length: Decimal @required @unit("M") @min(0)
      width: Decimal @required @unit("M") @min(0)
      height: Decimal @required @unit("M") @min(0)

      // 开口尺寸
      opening_width: Optional[Decimal]
      opening_height: Optional[Decimal]

      // 托盘尺寸要求
      required_pallet_type: Optional[Enum { Euro, Standard, Custom }]
      max_pallet_height: Optional[Decimal]
    }

    // 利用率
    current_occupancy: QuantityInfo
    utilization_rate: Decimal @computed("current_occupancy.on_hand / max_units")
    fill_percentage: Decimal @computed("current_weight / max_weight * 100")
  }

  // 货位属性
  attributes: LocationAttributes {
    // ABC分类
    abc_class: Enum { A, B, C }
    velocity_class: Enum { Fast, Medium, Slow }

    // 物理属性
    temperature_zone: Enum { Ambient, Cool, Cold, Frozen, Ultra_Low }
    humidity_controlled: Boolean @default(false)

    // 特殊属性
    hazardous_compatible: Boolean @default(false)
    hazardous_classes: List[String]

    fragile_compatible: Boolean @default(true)
    stackable_required: Boolean @default(true)

    // 设备要求
    forklift_required: Boolean @default(false)
    equipment_type: Optional[Enum { Forklift, Reach_Truck, Order_Picker, Crane }]

    // 安全
    fire_sprinkler: Boolean @default(true)
    security_level: Enum { Standard, High, Maximum }
  }

  // 坐标（用于导航和可视化）
  coordinates: Optional[LocationCoordinates] {
    x: Decimal @unit("M")
    y: Decimal @unit("M")
    z: Decimal @unit("M")

    latitude: Optional[Decimal]
    longitude: Optional[Decimal]

    // 相邻货位
    adjacent_locations: List[String]
    distance_to_packing: Decimal @unit("M")
    distance_to_shipping: Decimal @unit("M")
  }

  // 状态
  status: LocationStatus {
    operational_status: Enum {
      Active,      // 可用
      Inactive,    // 停用
      Maintenance, // 维护中
      Full,        // 已满
      Blocked      // 锁定
    } @default("Active")

    physical_status: Enum {
      Empty,       // 空
      Occupied,    // 占用
      Partial      // 部分占用
    } @default("Empty")

    // 状态变更历史
    status_history: List[StatusChange]
  }

  // 当前存储
  current_inventory: Optional[CurrentInventory] {
    sku_code: String
    sku_name: String
    quantity: Int
    batch_number: Optional[String]
    received_date: Optional[Date]
  }

  // 限制
  restrictions: Optional[LocationRestrictions] {
    sku_restrictions: List[String]  // 仅限特定SKU
    sku_exclusions: List[String]    // 排除特定SKU
    category_restrictions: List[String]

    max_sku_count: Optional[Int]    // 最大SKU种类数
    single_sku_only: Boolean @default(false)

    fifo_required: Boolean @default(true)
    lot_segregation: Boolean @default(false)
  }

  // 审计
  audit: LocationAudit {
    created_at: DateTime @default("CURRENT_TIMESTAMP")
    created_by: String
    last_updated_at: DateTime
    last_updated_by: String
    last_counted_at: Optional[DateTime]
    cycle_count_frequency: Enum { Daily, Weekly, Monthly, Quarterly, Annually }
  }
} @standard("WMS")

type LocationHierarchy {
  warehouse_code: String
  zone: ZoneInfo
  area: AreaInfo
  aisle: AisleInfo
  bay: BayInfo
  level: LevelInfo
  position: PositionInfo
}

type StatusChange {
  from_status: String
  to_status: String
  changed_at: DateTime
  changed_by: String
  reason: Optional[String]
}
```

---

## 4. 作业任务Schema

**定义4（Task Schema）**：

```
Task_Schema = (
  Task_ID, Task_Type, Priority,
  Assignment, Status, Instructions, Execution
)
```

**形式化DSL定义**：

```dsl
schema Task {
  // 任务标识
  task_id: UUID @required @unique @default("gen_random_uuid()")
  task_number: String @required @unique @max_length(50)
  task_type: Enum {
    Receive,         // 收货
    Putaway,         // 上架
    Replenish,       // 补货
    Pick,            // 拣货
    Pack,            // 包装
    Move,            // 移库
    Cycle_Count,     // 盘点
    Load,            // 装车
    Audit            // 审核
  } @required

  // 任务分类
  task_category: Enum {
    Inbound,         // 入库类
    Inventory,       // 库存类
    Outbound,        // 出库类
    Maintenance      // 维护类
  }

  // 优先级
  priority: PriorityInfo {
    priority_level: Int @range(1, 10) @default(5)
    priority_code: Enum { Critical, High, Normal, Low }

    // 动态优先级计算
    dynamic_priority: Int @computed
    escalation_level: Int @range(0, 3) @default(0)

    // 截止时间
    due_date: DateTime
    sla_deadline: DateTime
    time_remaining: Duration @computed("sla_deadline - NOW()")
  }

  // 关联文档
  references: TaskReferences {
    // 入库相关
    asn_id: Optional[String]
    asn_number: Optional[String]
    receipt_id: Optional[String]
    receipt_number: Optional[String]

    // 出库相关
    order_id: Optional[String]
    order_number: Optional[String]
    wave_id: Optional[String]
    wave_number: Optional[String]

    // 库存相关
    inventory_id: Optional[String]
    location_code: Optional[String]

    // 盘点相关
    cycle_count_id: Optional[String]
  }

  // 任务分配
  assignment: TaskAssignment {
    assigned_to: Optional[String]  // 人员ID
    assigned_to_name: Optional[String]
    assigned_by: Optional[String]
    assigned_at: Optional[DateTime]

    // 人员要求
    required_skills: List[String]
    required_certifications: List[String]
    equipment_required: List[String]

    // 自动分配
    auto_assigned: Boolean @default(false)
    assignment_algorithm: Optional[String]
  }

  // 任务状态
  status: TaskStatus {
    current_status: Enum {
      Pending,       // 待处理
      Ready,         // 就绪
      Assigned,      // 已分配
      In_Progress,   // 进行中
      Paused,        // 暂停
      Completed,     // 已完成
      Cancelled,     // 已取消
      Exception      // 异常
    } @default("Pending")

    status_history: List[StatusHistory]

    // 进度
    progress_percentage: Decimal @range(0, 100) @default(0)
    estimated_completion: Optional[DateTime]
  }

  // 作业指令
  instructions: TaskInstructions {
    // 源位置
    source: Optional[LocationInfo] {
      location_code: String
      location_name: String
      zone_code: String
      coordinates: Optional[Coordinates]
    }

    // 目标位置
    destination: Optional[LocationInfo]

    // 作业明细
    lines: List<TaskLine] {
      line_number: Int @required

      sku: String @required
      sku_name: String
      sku_description: String

      batch_number: Optional[String]
      lot_number: Optional[String]
      expiration_date: Optional[Date]

      // 数量
      requested_quantity: Int @required @min(1)
      uom: String @required @default("EA")

      picked_quantity: Int @default(0)
      picked_from: Optional[String]
      picked_by: Optional[String]
      picked_at: Optional[DateTime]

      // 序列号
      serial_numbers: List[String]

      // 特殊指令
      special_instructions: Optional[String]

      // 验证
      requires_verification: Boolean @default(false)
      verification_method: Optional[Enum { Scan, Voice, Visual, Weight }]
    }

    // 路径优化
    suggested_route: Optional[List[String]]  // 建议的货位访问顺序
    estimated_travel_distance: Optional[Decimal] @unit("M")
    estimated_travel_time: Optional[Int] @unit("MINUTES")

    // 特殊要求
    temperature_requirement: Optional[TemperatureRange]
    handling_requirements: List[String]
    safety_requirements: List[String]
  }

  // 执行记录
  execution: TaskExecution {
    started_at: Optional[DateTime]
    started_by: Optional[String]

    completed_at: Optional[DateTime]
    completed_by: Optional[String]

    // 实际执行
    actual_travel_distance: Optional[Decimal]
    actual_travel_time: Optional[Int]
    actual_work_time: Optional[Int]

    // 设备使用
    equipment_used: List[EquipmentUsage]

    // 扫描记录
    scan_events: List[ScanEvent]

    // 异常记录
    exceptions: List[ExceptionRecord]

    // 备注
    notes: Optional[String]
    attachments: List[String]
  }

  // 绩效指标
  performance: TaskPerformance {
    planned_duration: Optional[Int] @unit("MINUTES")
    actual_duration: Optional[Int] @unit("MINUTES")
    variance: Optional[Int] @computed("actual_duration - planned_duration")
    efficiency: Optional[Decimal] @computed("planned_duration / actual_duration * 100")

    accuracy: Optional[Decimal] @range(0, 100)
    lines_completed: Int @default(0)
    lines_total: Int @required
  }

  // 依赖关系
  dependencies: TaskDependencies {
    depends_on: List[String]  // 前置任务ID
    blocks: List[String]      // 阻塞的任务ID
    related_tasks: List[String]
  }

  // 时间戳
  timestamps: TaskTimestamps {
    created_at: DateTime @required
    created_by: String @required
    released_at: Optional[DateTime]
    claimed_at: Optional[DateTime]
    started_at: Optional[DateTime]
    completed_at: Optional[DateTime]
  }
} @standard("WMS")

type TaskLine {
  line_number: Int
  sku: String
  sku_name: String
  requested_quantity: Int
  picked_quantity: Int
  uom: String
}

type ScanEvent {
  event_type: Enum { Location_Scan, SKU_Scan, Batch_Scan, Serial_Scan, Container_Scan }
  scanned_value: String
  scanned_at: DateTime
  scanned_by: String
  location: Optional[String]
}

type ExceptionRecord {
  exception_type: Enum { Shortage, Damage, Wrong_Item, Wrong_Location, System_Error, Other }
  description: String
  reported_at: DateTime
  reported_by: String
  resolved_at: Optional[DateTime]
  resolution: Optional[String]
}
```

---

## 5. 入库Schema

**定义5（Inbound Schema）**：

```
Inbound_Schema = (
  ASN, Receipt, Quality_Check, Putaway
)
```

**形式化DSL定义**：

```dsl
schema ASN {
  // ASN标识
  asn_id: UUID @required @unique @default("gen_random_uuid()")
  asn_number: String @required @unique
  external_asn_number: Optional[String]

  // 来源信息
  source: SourceInfo {
    supplier: PartyInfo {
      supplier_code: String @required
      supplier_name: String @required
      supplier_gln: Optional[String]
      vendor_number: Optional[String]
    }

    purchase_order: Optional[POInfo] {
      po_number: String
      po_date: Optional[Date]
      po_line_count: Int
    }

    delivery_note: Optional[String]
    invoice_number: Optional[String]
  }

  // 运输信息
  shipment: ShipmentInfo {
    carrier_code: Optional[String]
    carrier_name: Optional[String]
    carrier_scac: Optional[String]

    mode_of_transport: Enum { Truck, Rail, Air, Ocean, Parcel, Courier }
    service_level: Optional[String]

    bill_of_lading: Optional[String]
    pro_number: Optional[String]
    tracking_number: Optional[String]

    container_number: Optional[String]
    seal_number: Optional[String]

    vehicle_info: Optional[VehicleInfo] {
      vehicle_type: Optional[String]
      vehicle_number: Optional[String]
      trailer_number: Optional[String]
      driver_name: Optional[String]
      driver_phone: Optional[String]
    }
  }

  // 预约信息
  appointment: AppointmentInfo {
    appointment_required: Boolean @default(false)
    appointment_number: Optional[String]
    appointment_date: Optional[Date]
    appointment_time_slot: Optional[TimeSlot]

    dock_assigned: Optional[String]
    door_number: Optional[String]

    checked_in_at: Optional[DateTime]
    checked_in_by: Optional[String]

    unloading_started_at: Optional[DateTime]
    unloading_completed_at: Optional[DateTime]
  }

  // ASN明细
  lines: List[ASNLine] {
    line_number: Int @required

    sku: String @required
    sku_name: String
    sku_description: String

    expected_quantity: Int @required @min(1)
    uom: String @required @default("EA")

    batch_expected: Boolean @default(false)
    batch_number: Optional[String]
    lot_number: Optional[String]

    manufacturing_date: Optional[Date]
    expiration_date: Optional[Date]
    shelf_life_days: Optional[Int]

    // 包装
    units_per_carton: Optional[Int]
    cartons_per_pallet: Optional[Int]
    expected_cartons: Optional[Int]
    expected_pallets: Optional[Int]

    // 成本
    unit_cost: Optional[Decimal]
    currency: Optional[String]
    line_total: Optional[Decimal]

    // PO关联
    po_number: Optional[String]
    po_line_number: Optional[Int]
  }

  // 汇总
  summary: ASNSummary {
    total_lines: Int @computed
    total_quantity: Int @computed
    total_cartons: Optional[Int]
    total_pallets: Optional[Int]
    total_weight: Optional[Decimal]
    total_volume: Optional[Decimal]
  }

  // 状态
  status: ASNStatus {
    asn_status: Enum {
      Draft,
      Sent,
      Acknowledged,
      In_Transit,
      Arrived,
      Receiving,
      Received,
      Cancelled
    } @default("Draft")

    status_history: List[StatusChange]
  }

  // 时间
  timing: ASNTiming {
    created_at: DateTime @required
    sent_at: Optional[DateTime]
    expected_arrival: DateTime @required
    actual_arrival: Optional[DateTime]
    receipt_completed_at: Optional[DateTime]
  }

  // EDI信息
  edi: ASNEDI {
    edi_message_id: Optional[String]
    edi_message_type: Optional[Enum { X12_856, EDIFACT_DESADV, GS1_DESADV }]
    edi_sender: Optional[String]
    edi_receiver: Optional[String]
    edi_timestamp: Optional[DateTime]
  }
} @standard("WMS")

schema Receipt {
  // 收货单标识
  receipt_id: UUID @required @unique
  receipt_number: String @required @unique

  // 关联ASN
  asn_id: Optional[String]
  asn_number: Optional[String]

  // 来源
  source: SourceInfo {
    supplier_code: String @required
    supplier_name: String
    po_number: Optional[String]
  }

  // 运输
  carrier_code: Optional[String]
  carrier_name: Optional[String]
  tracking_number: Optional[String]

  // 到货信息
  arrival: ArrivalInfo {
    arrival_date: Date @required
    arrival_time: Time
    dock_door: Optional[String]
    vehicle_number: Optional[String]

    // 到货检查
    seal_intact: Optional[Boolean]
    seal_number: Optional[String]
    temperature_check: Optional[TemperatureCheck]
    packaging_condition: Optional[Enum { Good, Damaged, Wet, Crushed }]
  }

  // 收货明细
  lines: List[ReceiptLine] {
    line_number: Int @required

    asn_line_number: Optional[Int]

    sku: String @required
    sku_name: String

    // 数量
    expected_quantity: Int
    received_quantity: Int @required @min(0)
    accepted_quantity: Int @required @min(0)
    rejected_quantity: Int @required @min(0)

    // 批次
    batch_number: Optional[String]
    lot_number: Optional[String]
    manufacturing_date: Optional[Date]
    expiration_date: Optional[Date]

    // 质量
    quality_status: Enum { Accept, Reject, Hold, Sample }
    rejection_reason: Optional[String]

    // 上架
    putaway_location: Optional[String]
    putaway_quantity: Int @default(0)
  }

  // 汇总
  summary: ReceiptSummary {
    total_expected: Int
    total_received: Int
    total_accepted: Int
    total_rejected: Int
    lines_count: Int
    lines_complete: Int
  }

  // 状态
  status: ReceiptStatus {
    receipt_status: Enum { Pending, Receiving, Received, Putaway, Completed }
    putaway_status: Enum { Pending, In_Progress, Completed, Partial }
  }

  // 执行
  execution: ReceiptExecution {
    received_by: String
    received_at: DateTime
    putaway_completed_by: Optional[String]
    putaway_completed_at: Optional[DateTime]
  }
} @standard("WMS")
```

---

## 6. 出库Schema

**定义6（Outbound Schema）**：

```
Outbound_Schema = (
  Order, Wave, Pick, Pack, Ship
)
```

**形式化DSL定义**：

```dsl
schema OutboundOrder {
  // 订单标识
  order_id: UUID @required @unique
  order_number: String @required @unique

  // 订单类型
  order_type: Enum {
    Customer,        // 客户订单
    Transfer,        // 调拨订单
    Return,          // 退货订单
    Sample,          // 样品订单
    Replacement,     // 换货订单
    Work_Order       // 生产工单
  } @required

  // 优先级
  priority: PriorityInfo {
    priority_level: Int @range(1, 10) @default(5)
    priority_reason: Optional[String]
    rush_order: Boolean @default(false)
  }

  // 客户信息
  customer: CustomerInfo {
    customer_code: String @required
    customer_name: String @required
    customer_type: Enum { B2B, B2C, Internal }

    shipping_address: Address @required
    billing_address: Optional[Address]

    contact_name: Optional[String]
    contact_phone: Optional[String]
    contact_email: Optional[String]

    delivery_instructions: Optional[String]

    // 承运商偏好
    preferred_carrier: Optional[String]
    ship_complete: Boolean @default(false)
    allow_partial_ship: Boolean @default(true)
  }

  // 时间要求
  timing: OrderTiming {
    order_date: DateTime @required
    requested_ship_date: Date @required
    promised_ship_date: Date
    latest_ship_date: Date

    required_delivery_date: Optional[Date]
    delivery_time_window: Optional[TimeWindow]

    sla_commitment: Optional[String]
    service_level: Enum { Standard, Expedited, Same_Day, Next_Day, Two_Day }
  }

  // 订单明细
  lines: List[OrderLine] {
    line_number: Int @required

    sku: String @required
    sku_name: String
    sku_description: String

    ordered_quantity: Int @required @min(1)
    uom: String @required @default("EA")

    // 分配
    allocated_quantity: Int @default(0)
    allocated_from: List[AllocationDetail]

    // 拣货
    picked_quantity: Int @default(0)
    picked_by: Optional[String]
    picked_at: Optional[DateTime]

    // 包装
    packed_quantity: Int @default(0)
    package_id: Optional[String]

    // 发运
    shipped_quantity: Int @default(0)
    backordered_quantity: Int @default(0)
    cancelled_quantity: Int @default(0)

    // 价格
    unit_price: Optional[Decimal]
    line_total: Optional[Decimal]
    currency: Optional[String]

    // 特殊要求
    gift_wrap: Boolean @default(false)
    gift_message: Optional[String]
    serial_number_required: Boolean @default(false)
    expiration_date_required: Optional[Date]
  }

  // 分配信息
  allocation: AllocationInfo {
    allocation_status: Enum { Unallocated, Partial, Allocated, Shortage }
    allocated_at: Optional[DateTime]
    allocated_by: Optional[String]
    allocation_rule: Optional[String]

    shortages: List[ShortageDetail]
    substitutions: List[SubstitutionDetail]
  }

  // 波次
  wave: WaveInfo {
    wave_id: Optional[String]
    wave_number: Optional[String]
    wave_sequence: Optional[Int]
    added_to_wave_at: Optional[DateTime]
  }

  // 包装
  packing: PackingInfo {
    packages: List[PackageInfo] {
      package_id: String
      package_number: String
      package_type: Enum { Box, Envelope, Pallet, Bag, Tube, Custom }

      dimensions: Dimensions
      weight: Decimal

      contents: List[PackageContent]

      tracking_number: Optional[String]
      label_printed: Boolean @default(false)
    }

    total_packages: Int @computed
    total_weight: Decimal
    total_volume: Decimal

    packing_completed_at: Optional[DateTime]
    packed_by: Optional[String]
  }

  // 发运
  shipment: ShipmentInfo {
    carrier_code: Optional[String]
    carrier_name: Optional[String]
    service_level: Optional[String]

    tracking_numbers: List[String]
    pro_number: Optional[String]
    bol_number: Optional[String]

    freight_terms: Enum { Prepaid, Collect, Third_Party }
    freight_charge: Optional[Decimal]

    ship_date: Optional[Date]
    estimated_delivery: Optional[Date]

    shipping_labels: List[LabelInfo]
    customs_documents: List[DocumentInfo]
  }

  // 订单状态
  status: OrderStatus {
    order_status: Enum {
      New,           // 新建
      Allocated,     // 已分配
      Released,      // 已释放
      Picking,       // 拣货中
      Picked,        // 已拣货
      Packing,       // 包装中
      Packed,        // 已包装
      Staged,        // 已集货
      Shipped,       // 已发运
      Delivered,     // 已送达
      Cancelled,     // 已取消
      On_Hold        // 暂停
    }

    status_history: List[StatusChange]
    is_complete: Boolean @computed
  }

  // 来源
  source: OrderSource {
    source_system: String
    source_order_id: Optional[String]
    channel: Optional[Enum { Web, Mobile, EDI, API, Phone, Manual }]
    reference_numbers: List[String]
  }

  // 财务
  financial: OrderFinancial {
    subtotal: Decimal
    discount: Decimal
    shipping_cost: Decimal
    tax: Decimal
    total: Decimal
    currency: String

    payment_status: Enum { Pending, Authorized, Paid, Refunded }
    payment_method: Optional[String]
  }

  // 时间戳
  timestamps: OrderTimestamps {
    created_at: DateTime
    modified_at: DateTime
    released_at: Optional[DateTime]
    picked_at: Optional[DateTime]
    packed_at: Optional[DateTime]
    shipped_at: Optional[DateTime]
    delivered_at: Optional[DateTime]
  }
} @standard("WMS")

schema Wave {
  // 波次标识
  wave_id: UUID @required @unique
  wave_number: String @required @unique
  wave_type: Enum { Pick, Pack, Ship }

  // 波次属性
  attributes: WaveAttributes {
    wave_template: Optional[String]
    wave_rule: Optional[String]

    // 筛选条件
    criteria: WaveCriteria {
      order_types: List[String]
      priorities: List[Int]
      carriers: List[String]
      ship_dates: DateRange
      required_ship_methods: List[String]
      zones: List[String]
    }
  }

  // 包含订单
  orders: List[WaveOrder] {
    order_id: String
    order_number: String
    sequence: Int
    added_at: DateTime
  }

  // 作业任务
  tasks: List[WaveTask] {
    task_id: String
    task_type: Enum { Pick, Replenish, Move }
    zone: String
    assigned_to: Optional[String]
    status: String
  }

  // 汇总
  summary: WaveSummary {
    total_orders: Int
    total_lines: Int
    total_skus: Int
    total_quantity: Int
    total_weight: Decimal
    total_volume: Decimal
  }

  // 状态
  status: WaveStatus {
    wave_status: Enum { Planned, Released, Picking, Picking_Complete, Packing, Shipped, Cancelled }
    progress_percentage: Decimal
  }

  // 时间
  timing: WaveTiming {
    created_at: DateTime
    released_at: Optional[DateTime]
    picking_completed_at: Optional[DateTime]
    packing_completed_at: Optional[DateTime]
    shipped_at: Optional[DateTime]
  }
} @standard("WMS")
```

---

## 7. 盘点Schema

**定义7（Cycle Count Schema）**：

```
Cycle_Count_Schema = (
  Count_ID, Schedule, Execution, Variance, Adjustment
)
```

**形式化DSL定义**：

```dsl
schema CycleCount {
  // 盘点单标识
  count_id: UUID @required @unique
  count_number: String @required @unique
  count_type: Enum {
    Cycle,           // 周期盘点
    Physical,        // 全面盘点
    Ad_Hoc,          // 临时盘点
    Blind,           // 盲盘
    System_Driven    // 系统驱动盘点
  }

  // 触发原因
  trigger: CountTrigger {
    trigger_type: Enum { Scheduled, Threshold, Discrepancy, Audit, Manual }
    reason: Optional[String]
    triggered_by: Optional[String]
    triggered_at: DateTime
  }

  // 盘点范围
  scope: CountScope {
    // 按SKU
    sku_list: List[String]
    sku_category: Optional[String]
    abc_class: Optional[Enum { A, B, C }]

    // 按货位
    location_list: List[String]
    zone_list: List[String]
    area_list: List[String]

    // 按属性
    batch_numbers: List[String]
    owner_list: List[String]

    // 按时间
    not_counted_since: Optional[Date]
    received_since: Optional[Date]

    // 按价值
    min_value: Optional[Decimal]
    max_value: Optional[Decimal]
  }

  // 盘点明细
  lines: List[CountLine] {
    line_number: Int @required

    sku: String @required
    sku_name: String
    location_code: String @required

    // 系统数据
    system_quantity: Int @required
    system_batch: Optional[String]
    system_lot: Optional[String]

    // 盘点数据
    counted_quantity: Optional[Int]
    counted_by: Optional[String]
    counted_at: Optional[DateTime]

    count_batch: Optional[String]
    count_lot: Optional[String]

    // 差异
    variance: Optional[Int] @computed("counted_quantity - system_quantity")
    variance_percentage: Optional[Decimal] @computed("variance / system_quantity * 100")

    // 状态
    count_status: Enum { Pending, Counted, Recount, Approved, Adjusted }

    // 备注
    notes: Optional[String]
    images: List[String]
  }

  // 差异汇总
  variance_summary: VarianceSummary {
    total_lines: Int
    counted_lines: Int
    variance_lines: Int
    positive_variances: Int
    negative_variances: Int
    total_variance_value: Decimal

    accuracy_rate: Optional[Decimal] @computed("(1 - variance_lines / total_lines) * 100")
  }

  // 差异审批
  approval: CountApproval {
    approval_required: Boolean @default(true)
    approval_threshold: Decimal @default(100.00)

    approved_by: Optional[String]
    approved_at: Optional[DateTime]
    approval_notes: Optional[String]

    auto_approved: Boolean @default(false)
  }

  // 库存调整
  adjustment: CountAdjustment {
    adjustment_status: Enum { Pending, Approved, Posted, Rejected }
    adjustment_number: Optional[String]

    adjustments: List[AdjustmentDetail] {
      inventory_id: String
      adjustment_type: Enum { Increase, Decrease }
      adjustment_quantity: Int
      reason_code: String
      gl_account: String
    }

    posted_at: Optional[DateTime]
    posted_by: Optional[String]
  }

  // 状态
  status: CountStatus {
    count_status: Enum { Planned, In_Progress, Completed, Approved, Posted, Cancelled }
    progress_percentage: Decimal @computed("counted_lines / total_lines * 100")
  }

  // 时间
  timing: CountTiming {
    scheduled_date: Date
    started_at: Optional[DateTime]
    completed_at: Optional[DateTime]
    approved_at: Optional[DateTime]
    posted_at: Optional[DateTime]
  }

  // 执行
  execution: CountExecution {
    assigned_to: Optional[String]
    equipment_used: List[String]
    count_method: Enum { Paper, RF, Voice, RFID }

    recount_required: Boolean @default(false)
    recount_trigger: Optional[String]
  }
} @standard("WMS")
```

---

## 8. 类型系统

**定义8（WMS数据类型）**：

```
WMS_Data_Type = Inventory | Location | Task | Inbound | Outbound | Cycle_Count | Movement
```

**基本类型定义**：

```dsl
type Address {
  name: String
  company: Optional[String]
  street_address: String @required
  address_line2: Optional[String]
  city: String @required
  state_province: String @required
  postal_code: String @required
  country: String @required @length(2)

  contact_name: Optional[String]
  contact_phone: Optional[String]
  contact_email: Optional[String]
}

type TimeWindow {
  start_time: Time
  end_time: Time
}

type DateRange {
  start_date: Date
  end_date: Date
}

type Dimensions {
  length: Decimal @unit("M")
  width: Decimal @unit("M")
  height: Decimal @unit("M")
  unit: Enum { MM, CM, M, IN, FT }
}

type PartyInfo {
  code: String @required
  name: String @required
  gln: Optional[String]
  address: Optional[Address]
  contact: Optional[ContactInfo]
}

type ContactInfo {
  name: String
  phone: String
  email: Optional[String]
  department: Optional[String]
}

type Coordinates {
  x: Decimal
  y: Decimal
  z: Optional[Decimal]
}

type AllocationDetail {
  inventory_id: String
  location_code: String
  batch_number: Optional[String]
  allocated_quantity: Int
}

type ShortageDetail {
  sku: String
  ordered_quantity: Int
  available_quantity: Int
  shortage_quantity: Int
  expected_receipt_date: Optional[Date]
}

type SubstitutionDetail {
  original_sku: String
  substituted_sku: String
  original_quantity: Int
  substituted_quantity: Int
  reason: String
  approved_by: String
}

type StatusHistory {
  from_status: String
  to_status: String
  changed_at: DateTime
  changed_by: String
  reason: Optional[String]
}

type EquipmentUsage {
  equipment_id: String
  equipment_type: String
  start_time: DateTime
  end_time: DateTime
  duration: Int
}

type TemperatureCheck {
  temperature: Decimal
  unit: Enum { Celsius, Fahrenheit }
  within_range: Boolean
  min_acceptable: Decimal
  max_acceptable: Decimal
}
```

---

## 9. 约束规则

**约束1（库存数量一致性）**：

```
∀ inventory ∈ Inventory:
  inventory.quantity.on_hand >= 0
  ∧ inventory.quantity.allocated >= 0
  ∧ inventory.quantity.picked >= 0
  ∧ inventory.quantity.available = inventory.quantity.on_hand - inventory.quantity.allocated - inventory.quantity.picked
  → inventory_quantity_valid(inventory)
```

**约束2（货位容量限制）**：

```
∀ location ∈ Location:
  location.current_occupancy.on_hand <= location.capacity.max_units
  ∧ location.current_occupancy.weight <= location.capacity.max_weight
  → location_capacity_valid(location)
```

**约束3（任务状态流转）**：

```
∀ task ∈ Task:
  valid_task_transition(task.status_from, task.status_to)
  → task_status_valid(task)

状态转换规则：
Pending → Ready → Assigned → In_Progress → Completed
           ↓          ↓            ↓
        Cancelled   Reassigned   Exception
```

**约束4（库存效期管理）**：

```
∀ inventory ∈ Inventory:
  inventory.batch.expiration_date = null
  ∨ inventory.batch.expiration_date > today
  ∨ inventory.inventory_status = "Expired"
  → inventory_expiration_valid(inventory)
```

**约束5（盘点差异规则）**：

```
∀ count ∈ CycleCount:
  count.variance_summary.total_variance_value < count.approval.approval_threshold
  ∨ count.approval.approved_by != null
  → count_approved(count)
```

---

## 10. 转换函数

**函数1（库存分配）**：

```
allocate_inventory: OutboundOrder × List<Inventory> × AllocationRules → AllocationResult
```

**函数2（波次创建）**：

```
create_wave: List<OutboundOrder> × WaveCriteria × WaveRules → Wave
```

**函数3（库位推荐）**：

```
suggest_location: Inventory × LocationConstraints × OptimizationRules → RecommendedLocation
```

**函数4（任务生成）**：

```
generate_tasks: Wave × TaskRules × ResourceAvailability → List<Task>
```

**函数5（库存调整）**：

```
adjust_inventory: CycleCount × ApprovalInfo → AdjustmentResult
```

---

## 11. 形式化定理

**定理1（库存守恒定律）**：

```
∀ inventory_movement ∈ InventoryMovement:
  inventory_movement.quantity_in - inventory_movement.quantity_out = inventory_movement.quantity_change
  ∧ sum(inventory_movements.quantity_change) = current_inventory - initial_inventory
  → inventory_conservation_holds(inventory_movement)
```

**定理2（任务完成完整性）**：

```
∀ task ∈ Task:
  task.status = "Completed"
  → ∀ line ∈ task.instructions.lines: line.picked_quantity = line.requested_quantity
  → task_completion_integrity(task)
```

**定理3（盘点准确性）**：

```
∀ count ∈ CycleCount:
  count.status = "Posted"
  → ∀ line ∈ count.lines: line.counted_quantity != null
  → count_completion_valid(count)
```

---

## 12. Python实现示例

```python
# 库存模型
class Inventory(BaseModel):
    inventory_id: UUID = Field(default_factory=uuid4)
    sku: str
    sku_name: str
    location_code: str

    on_hand: int = Field(ge=0)
    allocated: int = Field(default=0, ge=0)
    picked: int = Field(default=0, ge=0)

    @property
    def available(self) -> int:
        return self.on_hand - self.allocated - self.picked

    batch_number: Optional[str] = None
    expiration_date: Optional[date] = None
    inventory_status: str = "Available"

# 库存分配算法
class InventoryAllocator:
    def allocate(self, order: OutboundOrder, inventory_list: List[Inventory]) -> AllocationResult:
        allocations = []

        for line in order.lines:
            remaining = line.ordered_quantity

            # 按效期排序（FIFO）
            eligible_inventory = [
                inv for inv in inventory_list
                if inv.sku == line.sku and inv.available > 0
            ]
            eligible_inventory.sort(key=lambda x: x.expiration_date or date.max)

            for inv in eligible_inventory:
                if remaining <= 0:
                    break

                allocate_qty = min(remaining, inv.available)
                allocations.append(AllocationDetail(
                    inventory_id=str(inv.inventory_id),
                    location_code=inv.location_code,
                    batch_number=inv.batch_number,
                    allocated_quantity=allocate_qty
                ))

                inv.allocated += allocate_qty
                remaining -= allocate_qty

            if remaining > 0:
                # 记录缺货
                pass

        return AllocationResult(allocations=allocations)

# 波次创建
class WaveBuilder:
    def build_wave(self, orders: List[OutboundOrder], criteria: WaveCriteria) -> Wave:
        wave = Wave(
            wave_id=uuid4(),
            wave_number=f"W{datetime.now().strftime('%Y%m%d%H%M%S')}",
            wave_type="Pick"
        )

        # 筛选订单
        eligible_orders = [
            order for order in orders
            if self.matches_criteria(order, criteria)
        ]

        # 按优先级排序
        eligible_orders.sort(key=lambda x: x.priority.priority_level)

        # 限制波次大小
        max_orders = 200
        wave.orders = eligible_orders[:max_orders]

        # 生成任务
        wave.tasks = self.generate_tasks(wave)

        return wave

    def matches_criteria(self, order: OutboundOrder, criteria: WaveCriteria) -> bool:
        if criteria.carriers and order.shipment.carrier_code not in criteria.carriers:
            return False
        if criteria.priorities and order.priority.priority_level not in criteria.priorities:
            return False
        return True

# 库位推荐
class LocationSuggestor:
    def suggest_putaway_location(self, inventory: Inventory, locations: List[Location]) -> Optional[Location]:
        # 过滤不可用货位
        available_locations = [
            loc for loc in locations
            if loc.status.operational_status == "Active"
            and loc.status.physical_status in ["Empty", "Partial"]
        ]

        # 评分
        scored_locations = []
        for loc in available_locations:
            score = self.calculate_location_score(inventory, loc)
            scored_locations.append((loc, score))

        # 返回得分最高
        if scored_locations:
            scored_locations.sort(key=lambda x: x[1], reverse=True)
            return scored_locations[0][0]

        return None

    def calculate_location_score(self, inventory: Inventory, location: Location) -> float:
        score = 100.0

        # ABC匹配
        if inventory.sku.abc_class == location.attributes.abc_class:
            score += 20

        # 相似SKU聚合
        if location.current_inventory and location.current_inventory.sku_code == inventory.sku.sku_code:
            score += 30

        # 距离出入口
        if location.coordinates:
            score -= location.coordinates.distance_to_packing * 0.5

        return score
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
