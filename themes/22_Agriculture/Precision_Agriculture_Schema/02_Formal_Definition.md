# 精准农业Schema形式化定义

## 📑 目录

- [精准农业Schema形式化定义](#精准农业schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 农田信息Schema](#2-农田信息schema)
  - [3. 传感器数据Schema](#3-传感器数据schema)
  - [4. 农机作业Schema](#4-农机作业schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)

---

## 1. 形式化模型

**定义1（精准农业Schema）**：
精准农业Schema是一个五元组：

```text
Precision_Agriculture_Schema = (Field_Info, Sensor_Data,
                               Machinery_Operation, Crop_Management,
                               Weather_Data)
```

其中：

- `Field_Info`：农田信息Schema
- `Sensor_Data`：传感器数据Schema
- `Machinery_Operation`：农机作业Schema
- `Crop_Management`：作物管理Schema
- `Weather_Data`：气象数据Schema

---

## 2. 农田信息Schema

**定义2（农田信息Schema）**：

```text
Field_Info_Schema = (Basic_Info, Geographic_Info,
                    Soil_Info, Field_Boundary)
```

**形式化DSL定义**：

```dsl
schema FieldInfo {
  field_id: String @pattern("^[A-Z0-9]{10}$") @required @unique

  basic_info: {
    field_name: String @max_length(200) @required
    field_area: Decimal @min(0) @unit("hectares") @required
    field_type: Enum { Crop, Pasture, Orchard, Forest } @required
    ownership: String @max_length(100)
  } @required

  geographic_info: {
    latitude: Decimal @range(-90.0, 90.0) @required
    longitude: Decimal @range(-180.0, 180.0) @required
    altitude: Decimal @unit("meters")
    terrain_type: Enum { Plain, Hill, Mountain, Valley }
  } @required

  soil_info: {
    soil_type: String @max_length(100)
    ph_value: Decimal @range(0.0, 14.0)
    organic_matter: Decimal @range(0.0, 100.0) @unit("percentage")
    nitrogen_content: Decimal @min(0) @unit("mg/kg")
    phosphorus_content: Decimal @min(0) @unit("mg/kg")
    potassium_content: Decimal @min(0) @unit("mg/kg")
  }

  field_boundary: {
    boundary_coordinates: List<Coordinate> {
      latitude: Decimal @range(-90.0, 90.0) @required
      longitude: Decimal @range(-180.0, 180.0) @required
    } @required
    boundary_type: Enum { GPS, Manual, Satellite } @required
  } @required
} @standard("ISO_11783")
```

---

## 3. 传感器数据Schema

**定义3（传感器数据Schema）**：

```text
Sensor_Data_Schema = (Soil_Sensor, Weather_Sensor,
                     Crop_Sensor, Sensor_Location)
```

**形式化DSL定义**：

```dsl
schema SensorData {
  sensor_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  field_id: String @required
  timestamp: DateTime @format("ISO8601") @required

  soil_sensor: {
    soil_moisture: Decimal @range(0.0, 100.0) @unit("percentage")
    soil_temperature: Decimal @range(-50.0, 50.0) @unit("Celsius")
    soil_ph: Decimal @range(0.0, 14.0)
    soil_conductivity: Decimal @min(0) @unit("mS/cm")
  }

  weather_sensor: {
    air_temperature: Decimal @range(-50.0, 50.0) @unit("Celsius")
    air_humidity: Decimal @range(0.0, 100.0) @unit("percentage")
    rainfall: Decimal @min(0) @unit("mm")
    wind_speed: Decimal @min(0) @unit("m/s")
    wind_direction: Decimal @range(0.0, 360.0) @unit("degrees")
    solar_radiation: Decimal @min(0) @unit("W/m²")
  }

  crop_sensor: {
    crop_height: Decimal @min(0) @unit("cm")
    leaf_area_index: Decimal @min(0)
    ndvi: Decimal @range(-1.0, 1.0)
    crop_density: Decimal @min(0) @unit("plants/m²")
  }

  sensor_location: {
    latitude: Decimal @range(-90.0, 90.0) @required
    longitude: Decimal @range(-180.0, 180.0) @required
    altitude: Decimal @unit("meters")
  } @required
} @standard("OGC_SensorThings")
```

---

## 4. 农机作业Schema

**定义4（农机作业Schema）**：

```text
Machinery_Operation_Schema = (Operation_Type, Operation_Parameters,
                             Operation_Location, Operation_Time)
```

**形式化DSL定义**：

```dsl
schema MachineryOperation {
  operation_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  field_id: String @required
  machinery_id: String @required

  operation_type: Enum {
    Seeding,
    Fertilizing,
    Spraying,
    Harvesting,
    Tillage
  } @required

  operation_parameters: {
    operation_speed: Decimal @min(0) @unit("km/h")
    operation_depth: Decimal @min(0) @unit("cm")
    operation_width: Decimal @min(0) @unit("m")
    application_rate: Decimal @min(0) @unit("kg/ha")
    seed_rate: Decimal @min(0) @unit("kg/ha")
  } @required

  operation_location: {
    start_coordinate: {
      latitude: Decimal @range(-90.0, 90.0) @required
      longitude: Decimal @range(-180.0, 180.0) @required
    } @required
    end_coordinate: {
      latitude: Decimal @range(-90.0, 90.0) @required
      longitude: Decimal @range(-180.0, 180.0) @required
    } @required
    operation_track: List<Coordinate> {
      latitude: Decimal @range(-90.0, 90.0) @required
      longitude: Decimal @range(-180.0, 180.0) @required
      timestamp: DateTime @format("ISO8601") @required
    }
  } @required

  operation_time: {
    start_time: DateTime @format("ISO8601") @required
    end_time: DateTime @format("ISO8601") @required
    duration: Decimal @min(0) @unit("hours")
  } @required
} @standard("ISO_11783")
```

---

## 5. 类型系统

**定义5（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime,
              Date, Enum, List, Map, Object, Coordinate}
```

---

## 6. 约束规则

**定义6（约束规则）**：

1. **唯一性约束**：`field_id`、`sensor_id`、`operation_id`必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **范围约束**：数值类型支持`@min`、`@max`、`@range`约束
4. **地理坐标约束**：经纬度必须在有效范围内

---

## 7. 转换函数

**定义7（转换函数）**：

### 7.1 ISO 11783到AgGateway转换

```text
convert_ISO11783_to_AgGateway: ISO11783_Data → AgGateway_Data
```

### 7.2 OGC SensorThings到ISO 11783转换

```text
convert_SensorThings_to_ISO11783: SensorThings_Data → ISO11783_Data
```

---

## 8. 形式化定理

### 8.1 数据完整性定理

**定理1（数据完整性）**：
对于任意传感器数据`s`，如果`s.field_id`存在，
则传感器数据的数据完整性得到保证。

### 8.2 地理坐标一致性定理

**定理2（地理坐标一致性）**：
对于任意农田`f`，边界坐标满足：
`-90 ≤ coordinate.latitude ≤ 90`且`-180 ≤ coordinate.longitude ≤ 180`

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21

