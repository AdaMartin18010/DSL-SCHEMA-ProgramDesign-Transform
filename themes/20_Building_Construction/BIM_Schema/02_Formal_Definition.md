# 建筑信息模型Schema形式化定义

## 📑 目录

- [建筑信息模型Schema形式化定义](#建筑信息模型schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
    - [1.1 基本定义](#11-基本定义)
    - [1.2 Schema结构](#12-schema结构)
  - [2. 建筑设计Schema](#2-建筑设计schema)
  - [3. 施工管理Schema](#3-施工管理schema)
  - [4. 运维管理Schema](#4-运维管理schema)
  - [5. IFC数据Schema](#5-ifc数据schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 数据完整性定理](#91-数据完整性定理)
    - [9.2 空间关系一致性定理](#92-空间关系一致性定理)

---

## 1. 形式化模型

### 1.1 基本定义

设 `BIM_Schema` 为建筑信息模型Schema的集合，
`Design_Schema` 为建筑设计Schema的集合，
`Construction_Schema` 为施工管理Schema的集合，
`Operation_Schema` 为运维管理Schema的集合，
`IFC_Data_Schema` 为IFC数据Schema的集合。

**定义1（BIM Schema）**：
BIM Schema是一个四元组：

```text
BIM_Schema = (Design_Schema, Construction_Schema, Operation_Schema, IFC_Data_Schema)
```

其中：

- `Design_Schema`：建筑设计Schema
- `Construction_Schema`：施工管理Schema
- `Operation_Schema`：运维管理Schema
- `IFC_Data_Schema`：IFC数据Schema

### 1.2 Schema结构

**定义2（BIM Schema结构）**：

```text
BIM_Schema = (Design_Schema ⊕ Construction_Schema ⊕ Operation_Schema
            ⊕ IFC_Data_Schema) × BIM_Profile
```

其中 `BIM_Profile` 是BIM配置参数。

---

## 2. 建筑设计Schema

**定义3（建筑设计Schema）**：

```text
Design_Schema = (Building_Element_Schema ⊕ Space_Schema ⊕ Material_Schema ⊕ Geometry_Schema)
```

**形式化DSL定义**：

```dsl
schema BuildingDesign {
  project_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  project_name: String @max_length(200) @required

  building_elements: List<BuildingElement> {
    element_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
    element_type: Enum { Wall, Column, Beam, Slab, Door, Window, Roof, Stair } @required
    global_id: String @pattern("^[A-Z0-9]{22}$") @required @unique
    name: String @max_length(255)
    description: String @max_length(1000)
    tag: String @max_length(100)

    geometry: Geometry {
      placement: Placement {
        location: Point3D {
          x: Decimal @precision(10,3) @unit("meters") @required
          y: Decimal @precision(10,3) @unit("meters") @required
          z: Decimal @precision(10,3) @unit("meters") @required
        } @required
        axis: Vector3D {
          x: Decimal @range(-1, 1) @precision(3) @required
          y: Decimal @range(-1, 1) @precision(3) @required
          z: Decimal @range(-1, 1) @precision(3) @required
        }
        ref_direction: Vector3D {
          x: Decimal @range(-1, 1) @precision(3)
          y: Decimal @range(-1, 1) @precision(3)
          z: Decimal @range(-1, 1) @precision(3)
        }
      } @required

      representation: Representation {
        representation_type: Enum { SweptSolid, BRep, CSG, Surface } @required
        shape: Shape {
          dimensions: Map<String, Decimal> @required
          volume: Decimal @precision(10,3) @unit("cubic meters") @range(0, 1000000)
          area: Decimal @precision(10,3) @unit("square meters") @range(0, 100000)
        } @required
      } @required
    } @required

    material: Material {
      material_id: String @required @unique
      material_name: String @max_length(200) @required
      material_type: Enum { Concrete, Steel, Wood, Glass, Plastic, Other } @required
      properties: MaterialProperties {
        density: Decimal @precision(10,2) @unit("kg/m³") @range(0, 10000)
        thermal_conductivity: Decimal @precision(10,4) @unit("W/(m·K)") @range(0, 1000)
        specific_heat: Decimal @precision(10,2) @unit("J/(kg·K)") @range(0, 10000)
        strength: Decimal @precision(10,2) @unit("MPa") @range(0, 10000)
      }
    }

    properties: PropertySet {
      property_set_name: String @max_length(100) @required
      properties: Map<String, Any> @required
    }
  } @required

  spaces: List<Space> {
    space_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
    global_id: String @pattern("^[A-Z0-9]{22}$") @required @unique
    space_name: String @max_length(255) @required
    space_type: Enum { Room, Corridor, Stairwell, Elevator, Other } @required
    long_name: String @max_length(500)
    description: String @max_length(1000)

    geometry: Geometry {
      placement: Placement @required
      representation: Representation {
        representation_type: Enum { BRep, Surface } @required
        shape: Shape {
          volume: Decimal @precision(10,3) @unit("cubic meters") @range(0, 1000000) @required
          area: Decimal @precision(10,3) @unit("square meters") @range(0, 100000) @required
        } @required
      } @required
    } @required

    floor: String @max_length(100) @required
    elevation: Decimal @precision(10,3) @unit("meters") @required
    height: Decimal @precision(10,3) @unit("meters") @range(0, 100) @required
  } @required

  floors: List<Floor> {
    floor_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
    global_id: String @pattern("^[A-Z0-9]{22}$") @required @unique
    floor_name: String @max_length(255) @required
    elevation: Decimal @precision(10,3) @unit("meters") @required
    height: Decimal @precision(10,3) @unit("meters") @range(0, 100)
  } @required
} @standard("ISO16739")
```

---

## 3. 施工管理Schema

**定义4（施工管理Schema）**：

```text
Construction_Schema = (Schedule_Schema ⊕ Progress_Schema ⊕ Quality_Schema ⊕ Safety_Schema)
```

**形式化DSL定义**：

```dsl
schema ConstructionManagement {
  project_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  project_name: String @max_length(200) @required

  schedule: Schedule {
    schedule_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
    schedule_name: String @max_length(200) @required
    start_date: Date @format("YYYY-MM-DD") @required
    end_date: Date @format("YYYY-MM-DD") @required

    tasks: List<Task> {
      task_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      task_name: String @max_length(200) @required
      task_type: Enum { Foundation, Structure, MEP, Finishing, Other } @required
      planned_start: Date @format("YYYY-MM-DD") @required
      planned_end: Date @format("YYYY-MM-DD") @required
      planned_duration: Integer @range(1, 3650) @unit("days") @required
      actual_start: Date @format("YYYY-MM-DD")
      actual_end: Date @format("YYYY-MM-DD")
      actual_duration: Integer @range(0, 3650) @unit("days")
      progress: Decimal @range(0, 100) @unit("%") @precision(2) @default(0)
      status: Enum { NotStarted, InProgress, Completed, Delayed, Cancelled } @default("NotStarted")
      predecessor_tasks: List<String>
      assigned_resources: List<Resource> {
        resource_id: String @required @unique
        resource_type: Enum { Labor, Equipment, Material } @required
        resource_name: String @max_length(200) @required
        quantity: Decimal @precision(10,2) @range(0, 1000000) @required
        unit: String @max_length(50) @required
      }
      related_elements: List<String> @required
    } @required
  } @required

  progress: Progress {
    progress_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
    report_date: Date @format("YYYY-MM-DD") @required

    overall_progress: Decimal @range(0, 100) @unit("%") @precision(2) @required
    planned_progress: Decimal @range(0, 100) @unit("%") @precision(2) @required
    progress_deviation: Decimal @precision(2) @unit("%")

    task_progress: List<TaskProgress> {
      task_id: String @required
      progress: Decimal @range(0, 100) @unit("%") @precision(2) @required
      completion_date: Date @format("YYYY-MM-DD")
    } @required
  } @required

  quality: Quality {
    quality_id: String @pattern("^[A-Z0-9]{20}$") @required @unique

    inspections: List<Inspection> {
      inspection_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      inspection_type: Enum { Material, Structure, MEP, Finishing, Safety } @required
      inspection_date: Date @format("YYYY-MM-DD") @required
      inspector: String @max_length(100) @required
      inspected_element: String @required
      inspection_result: Enum { Pass, Fail, Conditional } @required
      inspection_notes: String @max_length(1000)
      defects: List<Defect> {
        defect_id: String @required @unique
        defect_type: String @max_length(100) @required
        defect_description: String @max_length(500) @required
        severity: Enum { Low, Medium, High, Critical } @required
        status: Enum { Open, InProgress, Resolved, Closed } @default("Open")
        resolution_date: Date @format("YYYY-MM-DD")
      }
    } @required
  } @required

  safety: Safety {
    safety_id: String @pattern("^[A-Z0-9]{20}$") @required @unique

    hazards: List<Hazard> {
      hazard_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      hazard_type: Enum { Fall, Electrical, Fire, Chemical, Mechanical, Other } @required
      hazard_location: String @max_length(200) @required
      hazard_description: String @max_length(500) @required
      risk_level: Enum { Low, Medium, High, Critical } @required
      mitigation_measures: String @max_length(1000) @required
      status: Enum { Open, Mitigated, Closed } @default("Open")
    } @required

    incidents: List<Incident> {
      incident_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      incident_type: Enum { Injury, NearMiss, PropertyDamage, Other } @required
      incident_date: DateTime @required
      incident_location: String @max_length(200) @required
      incident_description: String @max_length(1000) @required
      severity: Enum { Minor, Moderate, Major, Critical } @required
      root_cause: String @max_length(500)
      corrective_actions: String @max_length(1000)
    } @required
  } @required
} @standard("ISO19650")
```

---

## 4. 运维管理Schema

**定义5（运维管理Schema）**：

```text
Operation_Schema = (Equipment_Schema ⊕ Maintenance_Schema ⊕ Energy_Schema ⊕ Space_Management_Schema)
```

**形式化DSL定义**：

```dsl
schema OperationManagement {
  facility_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  facility_name: String @max_length(200) @required

  equipment: List<Equipment> {
    equipment_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
    equipment_name: String @max_length(200) @required
    equipment_type: Enum { HVAC, Electrical, Plumbing, FireSafety, Elevator, Other } @required
    manufacturer: String @max_length(200)
    model_number: String @max_length(100)
    serial_number: String @max_length(100) @unique
    installation_date: Date @format("YYYY-MM-DD")
    warranty_start_date: Date @format("YYYY-MM-DD")
    warranty_duration: Integer @range(0, 20) @unit("years")
    location: Location {
      space_id: String @required
      space_name: String @max_length(255) @required
      coordinates: Point3D {
        x: Decimal @precision(10,3) @unit("meters") @required
        y: Decimal @precision(10,3) @unit("meters") @required
        z: Decimal @precision(10,3) @unit("meters") @required
      } @required
    } @required
    status: Enum { Operational, Maintenance, OutOfService, Retired } @default("Operational")
    properties: Map<String, Any>
  } @required

  maintenance: Maintenance {
    maintenance_id: String @pattern("^[A-Z0-9]{20}$") @required @unique

    maintenance_plans: List<MaintenancePlan> {
      plan_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      plan_name: String @max_length(200) @required
      equipment_id: String @required
      maintenance_type: Enum { Preventive, Corrective, Predictive, Emergency } @required
      frequency: Enum { Daily, Weekly, Monthly, Quarterly, SemiAnnual, Annual, AsNeeded } @required
      frequency_value: Integer @range(1, 365) @unit("days")
      estimated_duration: Integer @range(1, 168) @unit("hours")
      estimated_cost: Decimal @precision(10,2) @unit("currency") @range(0, 1000000)
      required_resources: List<String>
      maintenance_procedures: String @max_length(2000) @required
    } @required

    maintenance_history: List<MaintenanceRecord> {
      record_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      plan_id: String
      equipment_id: String @required
      maintenance_date: Date @format("YYYY-MM-DD") @required
      maintenance_type: Enum { Preventive, Corrective, Predictive, Emergency } @required
      performed_by: String @max_length(100) @required
      duration: Integer @range(1, 168) @unit("hours") @required
      cost: Decimal @precision(10,2) @unit("currency") @range(0, 1000000) @required
      description: String @max_length(1000)
      parts_replaced: List<String>
      next_maintenance_date: Date @format("YYYY-MM-DD")
      status: Enum { Completed, InProgress, Cancelled } @default("Completed")
    } @required
  } @required

  energy: Energy {
    energy_id: String @pattern("^[A-Z0-9]{20}$") @required @unique

    energy_monitoring: List<EnergyData> {
      data_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      timestamp: DateTime @required
      energy_type: Enum { Electricity, Gas, Water, Steam, Other } @required
      consumption: Decimal @precision(10,2) @unit("kWh") @range(0, 1000000) @required
      cost: Decimal @precision(10,2) @unit("currency") @range(0, 1000000)
      source: String @max_length(200)
      location: String @max_length(200)
    } @required

    energy_analysis: EnergyAnalysis {
      analysis_period: Period {
        start_date: Date @format("YYYY-MM-DD") @required
        end_date: Date @format("YYYY-MM-DD") @required
      } @required
      total_consumption: Decimal @precision(10,2) @unit("kWh") @range(0, 100000000) @required
      total_cost: Decimal @precision(10,2) @unit("currency") @range(0, 10000000) @required
      average_daily_consumption: Decimal @precision(10,2) @unit("kWh") @range(0, 100000)
      peak_consumption: Decimal @precision(10,2) @unit("kWh") @range(0, 1000000)
      peak_consumption_date: Date @format("YYYY-MM-DD")
      efficiency_score: Decimal @range(0, 100) @unit("%") @precision(2)
    }
  } @required

  space_management: SpaceManagement {
    space_management_id: String @pattern("^[A-Z0-9]{20}$") @required @unique

    space_usage: List<SpaceUsage> {
      usage_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      space_id: String @required
      space_name: String @max_length(255) @required
      usage_type: Enum { Office, Meeting, Storage, Retail, Residential, Other } @required
      occupant_count: Integer @range(0, 10000) @default(0)
      area: Decimal @precision(10,3) @unit("square meters") @range(0, 100000) @required
      utilization_rate: Decimal @range(0, 100) @unit("%") @precision(2)
      lease_info: LeaseInfo {
        tenant_name: String @max_length(200)
        lease_start: Date @format("YYYY-MM-DD")
        lease_end: Date @format("YYYY-MM-DD")
        monthly_rent: Decimal @precision(10,2) @unit("currency") @range(0, 1000000)
      }
    } @required
  } @required
} @standard("COBie")
```

---

## 5. IFC数据Schema

**定义6（IFC数据Schema）**：

```text
IFC_Data_Schema = (IFC_File_Schema ⊕ IFC_Entity_Schema ⊕ IFC_Relationship_Schema ⊕ IFC_PropertySet_Schema)
```

**形式化DSL定义**：

```dsl
schema IFCData {
  ifc_file: IFCFile {
    file_path: String @max_length(500) @required
    file_name: String @max_length(255) @required
    file_size: Integer @range(0, 2147483647) @unit("bytes") @required
    file_schema: String @max_length(100) @required
    file_author: String @max_length(255)
    file_organization: String @max_length(255)
    preprocessor_version: String @max_length(100)
    originating_system: String @max_length(255)
    authorization: String @max_length(255)
    creation_date: DateTime
  } @required

  ifc_entities: List<IFCEntity> {
    entity_id: Integer @range(1, 2147483647) @required @unique
    entity_type: String @max_length(100) @required
    global_id: String @pattern("^[A-Z0-9]{22}$")
    owner_history: Integer
    name: String @max_length(255)
    description: String @max_length(1000)
    object_type: String @max_length(255)
    object_placement: Integer
    representation: Integer
    tag: String @max_length(100)
    parameters: List<Any> @required
  } @required

  ifc_relationships: List<IFCRelationship> {
    relationship_id: Integer @range(1, 2147483647) @required @unique
    relationship_type: Enum {
      RelContainedInSpatialStructure,
      RelFillsElement,
      RelVoidsElement,
      RelConnectsElements,
      RelAssociatesMaterial,
      RelAssociatesClassification,
      Other
    } @required
    global_id: String @pattern("^[A-Z0-9]{22}$")
    owner_history: Integer
    name: String @max_length(255)
    description: String @max_length(1000)
    relating_object: Integer @required
    related_objects: List<Integer> @required
  } @required

  ifc_property_sets: List<IFCPropertySet> {
    property_set_id: Integer @range(1, 2147483647) @required @unique
    global_id: String @pattern("^[A-Z0-9]{22}$")
    owner_history: Integer
    name: String @max_length(255) @required
    description: String @max_length(1000)
    has_properties: List<IFCProperty> {
      property_id: Integer @required @unique
      property_name: String @max_length(255) @required
      property_type: Enum { PropertySingleValue, PropertyBoundedValue, PropertyListValue, PropertyTableValue } @required
      nominal_value: Any
      unit: String @max_length(50)
    } @required
    relating_object: Integer @required
  } @required
} @standard("ISO16739")
```

---

## 6. 类型系统

**定义7（类型系统）**：

BIM Schema的类型系统包括以下基本类型：

- **String**：字符串类型，支持最大长度限制和模式匹配
- **Integer**：整数类型，支持范围限制
- **Decimal**：小数类型，支持精度和范围限制
- **Boolean**：布尔类型
- **Date**：日期类型，格式为 `YYYY-MM-DD`
- **DateTime**：日期时间类型，格式为 `YYYY-MM-DDTHH:mm:ss`
- **Enum**：枚举类型，定义有限的值集合
- **List<T>**：列表类型，元素类型为T
- **Map<K, V>**：映射类型，键类型为K，值类型为V
- **Optional<T>**：可选类型，值可以为空
- **Point3D**：三维点类型
- **Vector3D**：三维向量类型
- **Geometry**：几何类型
- **Placement**：位置类型
- **Shape**：形状类型

**类型约束**：

- 所有ID字段必须唯一
- 所有必需字段不能为空
- 数值字段必须满足范围约束
- 字符串字段必须满足长度和模式约束
- 日期字段必须满足格式约束

---

## 7. 约束规则

**定义8（约束规则）**：

### 7.1 数据完整性约束

1. **实体唯一性**：每个实体必须有唯一的ID
2. **引用完整性**：所有引用必须指向存在的实体
3. **空间关系一致性**：空间元素必须包含在楼层中
4. **元素关系一致性**：建筑元素必须包含在空间中

### 7.2 业务规则约束

1. **进度约束**：任务进度必须在0-100%之间
2. **日期约束**：任务结束日期必须晚于开始日期
3. **几何约束**：几何尺寸必须为正数
4. **能耗约束**：能耗数据必须为非负数

### 7.3 标准合规约束

1. **IFC标准约束**：IFC实体必须符合ISO 16739标准
2. **COBie标准约束**：COBie数据必须符合COBie 2.4标准
3. **gbXML标准约束**：gbXML数据必须符合gbXML 6.01标准

---

## 8. 转换函数

**定义9（转换函数）**：

### 8.1 IFC到COBie转换

```text
convert_ifc_to_cobie: IFC_Data_Schema → COBie_Schema
```

转换规则：

- IFC实体映射到COBie Component
- IFC空间映射到COBie Space
- IFC楼层映射到COBie Floor
- IFC属性集映射到COBie Attribute

### 8.2 IFC到gbXML转换

```text
convert_ifc_to_gbxml: IFC_Data_Schema → gbXML_Schema
```

转换规则：

- IFC建筑映射到gbXML Building
- IFC空间映射到gbXML Space
- IFC表面映射到gbXML Surface
- IFC材料映射到gbXML Material

### 8.3 COBie到IFC转换

```text
convert_cobie_to_ifc: COBie_Schema → IFC_Data_Schema
```

转换规则：

- COBie Component映射到IFC实体
- COBie Space映射到IFC空间
- COBie Floor映射到IFC楼层
- COBie Attribute映射到IFC属性集

---

## 9. 形式化定理

### 9.1 数据完整性定理

**定理1（数据完整性）**：

对于任意BIM Schema实例 `bim`，如果满足以下条件：

1. 所有实体ID唯一
2. 所有引用指向存在的实体
3. 所有必需字段非空
4. 所有数值字段满足范围约束

则 `bim` 是数据完整的。

**证明**：

根据定义8（约束规则），数据完整性约束包括实体唯一性、引用完整性、必需字段非空和数值范围约束。如果BIM Schema实例满足所有这些约束，则它是数据完整的。

### 9.2 空间关系一致性定理

**定理2（空间关系一致性）**：

对于任意BIM Schema实例 `bim`，如果满足以下条件：

1. 所有空间元素都包含在楼层中
2. 所有建筑元素都包含在空间中
3. 空间元素的几何不重叠（可选约束）

则 `bim` 的空间关系是一致的。

**证明**：

根据定义8（约束规则），空间关系一致性要求空间元素包含在楼层中，建筑元素包含在空间中。如果BIM Schema实例满足这些约束，则它的空间关系是一致的。

### 9.3 转换保真度定理

**定理3（转换保真度）**：

对于任意IFC数据 `ifc` 和转换函数 `convert_ifc_to_cobie`，如果：

1. `ifc` 是数据完整的
2. `cobie = convert_ifc_to_cobie(ifc)`
3. `cobie` 满足COBie标准约束

则转换是保真的，即 `cobie` 包含 `ifc` 的所有相关信息。

**证明**：

根据定义9（转换函数），IFC到COBie的转换规则定义了实体、空间、楼层和属性集的映射关系。如果IFC数据是完整的，且转换后的COBie数据满足COBie标准约束，则转换是保真的。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
