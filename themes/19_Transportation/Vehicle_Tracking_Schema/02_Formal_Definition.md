# 车辆跟踪Schema形式化定义

## 📑 目录

- [车辆跟踪Schema形式化定义](#车辆跟踪schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
    - [1.1 基本定义](#11-基本定义)
    - [1.2 Schema结构](#12-schema结构)
  - [2. GPS定位Schema](#2-gps定位schema)
  - [3. 北斗定位Schema](#3-北斗定位schema)
  - [4. AIS船舶跟踪Schema](#4-ais船舶跟踪schema)
  - [5. 轨迹分析Schema](#5-轨迹分析schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
    - [7.1 数据完整性约束](#71-数据完整性约束)
    - [7.2 业务规则约束](#72-业务规则约束)
    - [7.3 标准合规约束](#73-标准合规约束)
  - [8. 转换函数](#8-转换函数)
    - [8.1 GPS到位置转换](#81-gps到位置转换)
    - [8.2 位置到轨迹转换](#82-位置到轨迹转换)
    - [8.3 GPS到北斗转换](#83-gps到北斗转换)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 数据完整性定理](#91-数据完整性定理)
    - [9.2 位置一致性定理](#92-位置一致性定理)
    - [9.3 轨迹连续性定理](#93-轨迹连续性定理)

---

## 1. 形式化模型

### 1.1 基本定义

设 `Vehicle_Tracking_Schema` 为车辆跟踪Schema的集合，
`GPS_Tracking_Schema` 为GPS定位Schema的集合，
`Beidou_Tracking_Schema` 为北斗定位Schema的集合，
`AIS_Tracking_Schema` 为AIS船舶跟踪Schema的集合，
`Trajectory_Analysis_Schema` 为轨迹分析Schema的集合。

**定义1（Vehicle Tracking Schema）**：
Vehicle Tracking Schema是一个四元组：

```text
Vehicle_Tracking_Schema = (GPS_Tracking_Schema, Beidou_Tracking_Schema,
                          AIS_Tracking_Schema, Trajectory_Analysis_Schema)
```

其中：

- `GPS_Tracking_Schema`：GPS定位Schema
- `Beidou_Tracking_Schema`：北斗定位Schema
- `AIS_Tracking_Schema`：AIS船舶跟踪Schema
- `Trajectory_Analysis_Schema`：轨迹分析Schema

### 1.2 Schema结构

**定义2（Vehicle Tracking Schema结构）**：

```text
Vehicle_Tracking_Schema = (GPS_Tracking_Schema ⊕ Beidou_Tracking_Schema
                          ⊕ AIS_Tracking_Schema ⊕ Trajectory_Analysis_Schema)
                          × Tracking_Profile
```

其中 `Tracking_Profile` 是跟踪配置参数。

---

## 2. GPS定位Schema

**定义3（GPS定位Schema）**：

```text
GPS_Tracking_Schema = (NMEA_Message_Schema ⊕ GPS_Position_Schema ⊕ GPS_Quality_Schema)
```

**形式化DSL定义**：

```dsl
schema GPSTracking {
  vehicle_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  vehicle_type: Enum { Car, Truck, Bus, Motorcycle, Ship, Aircraft } @required

  nmea_messages: List<NMEAMessage> {
    message_type: Enum { GPGGA, GPRMC, GPGSV, GPGSA } @required
    timestamp: DateTime @required
    raw_message: String @max_length(200) @required

    gga_data: Optional<GGAData> {
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      altitude: Decimal @range(-500, 10000) @unit("meters") @precision(2)
      fix_quality: Integer @range(0, 8) @required
      num_satellites: Integer @range(0, 20) @required
      hdop: Decimal @range(0, 99.9) @precision(2)
      geoid_height: Decimal @precision(2)
    }

    rmc_data: Optional<RMCData> {
      status: Enum { A, V } @required
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      speed_knots: Decimal @range(0, 100) @unit("knots") @precision(2)
      speed_kmh: Decimal @range(0, 200) @unit("km/h") @precision(2)
      course: Decimal @range(0, 360) @unit("degrees") @precision(2)
      magnetic_variation: Decimal @range(-180, 180) @unit("degrees") @precision(2)
    }

    gsv_data: Optional<GSVData> {
      total_messages: Integer @range(1, 9) @required
      message_number: Integer @range(1, 9) @required
      total_satellites: Integer @range(0, 20) @required
      satellites: List<SatelliteInfo> {
        prn: Integer @range(1, 32) @required
        elevation: Integer @range(0, 90) @unit("degrees") @required
        azimuth: Integer @range(0, 360) @unit("degrees") @required
        snr: Integer @range(0, 99) @unit("dB") @required
      }
    }

    gsa_data: Optional<GSAData> {
      selection_mode: Enum { A, M } @required
      fix_mode: Integer @range(1, 3) @required
      satellites_used: List<Integer> @max_size(12)
      pdop: Decimal @range(0, 99.9) @precision(2)
      hdop: Decimal @range(0, 99.9) @precision(2)
      vdop: Decimal @range(0, 99.9) @precision(2)
    }
  } @required

  gps_positions: List<GPSPosition> {
    timestamp: DateTime @required
    latitude: Decimal @range(-90, 90) @required @precision(7)
    longitude: Decimal @range(-180, 180) @required @precision(7)
    altitude: Decimal @range(-500, 10000) @unit("meters") @precision(2)
    speed: Decimal @range(0, 200) @unit("km/h") @precision(2)
    course: Decimal @range(0, 360) @unit("degrees") @precision(2)
    fix_quality: Integer @range(0, 8) @required
    num_satellites: Integer @range(0, 20) @required
    hdop: Decimal @range(0, 99.9) @precision(2)
    source: Enum { GPS, DGPS, RTK } @default(GPS)
  } @required

  gps_quality: GPSQuality {
    average_hdop: Decimal @range(0, 99.9) @precision(2)
    average_satellites: Decimal @range(0, 20) @precision(2)
    fix_percentage: Decimal @range(0, 100) @unit("%") @precision(2)
    accuracy_meters: Decimal @range(0, 1000) @unit("meters") @precision(2)
  }
} @standard("NMEA0183")
```

---

## 3. 北斗定位Schema

**定义4（北斗定位Schema）**：

```text
Beidou_Tracking_Schema = (BDS_Message_Schema ⊕ Beidou_Position_Schema ⊕ Beidou_Quality_Schema)
```

**形式化DSL定义**：

```dsl
schema BeidouTracking {
  vehicle_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  vehicle_type: Enum { Car, Truck, Bus, Motorcycle, Ship, Aircraft } @required

  bds_messages: List<BDSMessage> {
    message_type: Enum { BDGGA, BDRMC, BDGSV, BDGSA } @required
    timestamp: DateTime @required
    raw_message: String @max_length(200) @required

    bds_gga_data: Optional<BDSGGAData> {
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      altitude: Decimal @range(-500, 10000) @unit("meters") @precision(2)
      fix_quality: Integer @range(0, 8) @required
      num_satellites: Integer @range(0, 50) @required
      hdop: Decimal @range(0, 99.9) @precision(2)
    }

    bds_rmc_data: Optional<BDSRMCData> {
      status: Enum { A, V } @required
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      speed_knots: Decimal @range(0, 100) @unit("knots") @precision(2)
      speed_kmh: Decimal @range(0, 200) @unit("km/h") @precision(2)
      course: Decimal @range(0, 360) @unit("degrees") @precision(2)
    }
  } @required

  beidou_positions: List<BeidouPosition> {
    timestamp: DateTime @required
    latitude: Decimal @range(-90, 90) @required @precision(7)
    longitude: Decimal @range(-180, 180) @required @precision(7)
    altitude: Decimal @range(-500, 10000) @unit("meters") @precision(2)
    speed: Decimal @range(0, 200) @unit("km/h") @precision(2)
    course: Decimal @range(0, 360) @unit("degrees") @precision(2)
    fix_quality: Integer @range(0, 8) @required
    num_satellites: Integer @range(0, 50) @required
    hdop: Decimal @range(0, 99.9) @precision(2)
    source: Enum { BDS, BDS_DGPS, BDS_RTK } @default(BDS)
  } @required

  beidou_quality: BeidouQuality {
    average_hdop: Decimal @range(0, 99.9) @precision(2)
    average_satellites: Decimal @range(0, 50) @precision(2)
    fix_percentage: Decimal @range(0, 100) @unit("%") @precision(2)
    accuracy_meters: Decimal @range(0, 1000) @unit("meters") @precision(2)
  }
} @standard("BDS")
```

---

## 4. AIS船舶跟踪Schema

**定义5（AIS船舶跟踪Schema）**：

```text
AIS_Tracking_Schema = (AIS_Message_Schema ⊕ Vessel_Position_Schema ⊕ Vessel_Info_Schema)
```

**形式化DSL定义**：

```dsl
schema AISTracking {
  vessel_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  mmsi: String @pattern("^[0-9]{9}$") @required @unique

  ais_messages: List<AISMessage> {
    message_type: Integer @range(1, 27) @required
    message_type_name: String @required
    timestamp: DateTime @required
    fragment_count: Integer @range(1, 9) @default(1)
    fragment_number: Integer @range(1, 9) @default(1)
    channel: Enum { A, B } @required

    position_report: Optional<PositionReport> {
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      course_over_ground: Decimal @range(0, 360) @unit("degrees") @precision(2)
      speed_over_ground: Decimal @range(0, 102.2) @unit("knots") @precision(2)
      heading: Integer @range(0, 359) @unit("degrees")
      navigation_status: Integer @range(0, 15) @required
      rate_of_turn: Integer @range(-128, 127)
      timestamp_seconds: Integer @range(0, 59)
    }

    static_voyage_data: Optional<StaticVoyageData> {
      imo_number: String @pattern("^[0-9]{7}$")
      call_sign: String @max_length(7)
      vessel_name: String @max_length(20) @required
      vessel_type: Integer @range(0, 99) @required
      dimension_to_bow: Integer @range(0, 511) @unit("meters")
      dimension_to_stern: Integer @range(0, 511) @unit("meters")
      dimension_to_port: Integer @range(0, 63) @unit("meters")
      dimension_to_starboard: Integer @range(0, 63) @unit("meters")
      eta_month: Integer @range(1, 12)
      eta_day: Integer @range(1, 31)
      eta_hour: Integer @range(0, 23)
      eta_minute: Integer @range(0, 59)
      draught: Decimal @range(0, 25.5) @unit("meters") @precision(1)
      destination: String @max_length(20)
    }
  } @required

  vessel_positions: List<VesselPosition> {
    timestamp: DateTime @required
    latitude: Decimal @range(-90, 90) @required @precision(7)
    longitude: Decimal @range(-180, 180) @required @precision(7)
    course: Decimal @range(0, 360) @unit("degrees") @precision(2)
    speed: Decimal @range(0, 102.2) @unit("knots") @precision(2)
    heading: Integer @range(0, 359) @unit("degrees")
    navigation_status: Integer @range(0, 15) @required
  } @required

  vessel_info: VesselInfo {
    mmsi: String @pattern("^[0-9]{9}$") @required @unique
    imo_number: String @pattern("^[0-9]{7}$")
    call_sign: String @max_length(7)
    vessel_name: String @max_length(20) @required
    vessel_type: Integer @range(0, 99) @required
    length: Decimal @range(0, 1022) @unit("meters") @precision(2)
    width: Decimal @range(0, 126) @unit("meters") @precision(2)
    draught: Decimal @range(0, 25.5) @unit("meters") @precision(1)
  } @required
} @standard("ITU-R M.1371")
```

---

## 5. 轨迹分析Schema

**定义6（轨迹分析Schema）**：

```text
Trajectory_Analysis_Schema = (Trajectory_Points_Schema ⊕ Path_Analysis_Schema
                             ⊕ Speed_Analysis_Schema ⊕ Stop_Analysis_Schema
                             ⊕ Geofence_Schema)
```

**形式化DSL定义**：

```dsl
schema TrajectoryAnalysis {
  vehicle_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
  trajectory_id: String @pattern("^[A-Z0-9]{20}$") @required @unique

  trajectory_points: List<TrajectoryPoint> {
    sequence_number: Integer @range(1, 1000000) @required
    timestamp: DateTime @required
    latitude: Decimal @range(-90, 90) @required @precision(7)
    longitude: Decimal @range(-180, 180) @required @precision(7)
    altitude: Decimal @range(-500, 10000) @unit("meters") @precision(2)
    speed: Decimal @range(0, 200) @unit("km/h") @precision(2)
    course: Decimal @range(0, 360) @unit("degrees") @precision(2)
    accuracy: Decimal @range(0, 1000) @unit("meters") @precision(2)
  } @required @min_size(2)

  path_analysis: PathAnalysis {
    total_distance: Decimal @range(0, 100000) @unit("kilometers") @precision(2) @required
    total_duration: Decimal @range(0, 86400) @unit("seconds") @precision(2) @required
    start_position: Position {
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      timestamp: DateTime @required
    } @required
    end_position: Position {
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      timestamp: DateTime @required
    } @required
    straight_line_distance: Decimal @range(0, 100000) @unit("kilometers") @precision(2)
    path_efficiency: Decimal @range(0, 1) @precision(3)
  } @required

  speed_analysis: SpeedAnalysis {
    average_speed: Decimal @range(0, 200) @unit("km/h") @precision(2) @required
    max_speed: Decimal @range(0, 200) @unit("km/h") @precision(2) @required
    min_speed: Decimal @range(0, 200) @unit("km/h") @precision(2) @required
    speed_variance: Decimal @range(0, 10000) @precision(2)
    speed_distribution: Map<String, Integer>
  } @required

  stop_analysis: StopAnalysis {
    stops: List<StopPoint> {
      stop_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      position: Position @required
      start_time: DateTime @required
      end_time: DateTime @required
      duration: Decimal @range(0, 86400) @unit("seconds") @precision(2) @required
      stop_reason: Enum { Parking, Traffic, Loading, Other } @default(Other)
    }
    total_stop_time: Decimal @range(0, 86400) @unit("seconds") @precision(2)
    num_stops: Integer @range(0, 1000) @required
  } @required

  geofences: List<Geofence> {
    geofence_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
    geofence_name: String @max_length(200) @required
    geofence_type: Enum { Circle, Polygon, Rectangle } @required
    coordinates: GeofenceCoordinates @required
    events: List<GeofenceEvent> {
      event_id: String @pattern("^[A-Z0-9]{20}$") @required @unique
      event_type: Enum { ENTER, EXIT } @required
      timestamp: DateTime @required
      position: Position @required
    }
  }
} @standard("Custom")
```

---

## 6. 类型系统

**定义7（类型系统）**：

Vehicle Tracking Schema的类型系统包括以下基本类型：

- **String**：字符串类型，支持最大长度限制和模式匹配
- **Integer**：整数类型，支持范围限制
- **Decimal**：小数类型，支持精度和范围限制
- **Boolean**：布尔类型
- **DateTime**：日期时间类型，格式为 `YYYY-MM-DDTHH:mm:ss`
- **Enum**：枚举类型，定义有限的值集合
- **List<T>**：列表类型，元素类型为T
- **Map<K, V>**：映射类型，键类型为K，值类型为V
- **Optional<T>**：可选类型，值可以为空
- **Position**：位置类型（纬度、经度）
- **TrajectoryPoint**：轨迹点类型

**类型约束**：

- 所有ID字段必须唯一
- 所有必需字段不能为空
- 数值字段必须满足范围约束
- 字符串字段必须满足长度和模式约束
- 日期时间字段必须满足格式约束
- 位置字段必须满足地理坐标范围约束

---

## 7. 约束规则

**定义8（约束规则）**：

### 7.1 数据完整性约束

1. **实体唯一性**：每个实体必须有唯一的ID
2. **位置有效性**：纬度必须在-90到90之间，经度必须在-180到180之间
3. **时间顺序性**：轨迹点必须按时间顺序排列
4. **速度合理性**：速度必须为非负数，且不超过合理范围

### 7.2 业务规则约束

1. **GPS质量约束**：GPS定位质量必须满足应用要求
2. **轨迹连续性**：轨迹点之间距离不能过大
3. **速度变化约束**：速度变化不能过于剧烈
4. **地理围栏约束**：地理围栏坐标必须有效

### 7.3 标准合规约束

1. **NMEA标准约束**：NMEA消息必须符合NMEA 0183标准
2. **AIS标准约束**：AIS消息必须符合ITU-R M.1371标准
3. **BDS标准约束**：BDS消息必须符合北斗标准

---

## 8. 转换函数

**定义9（转换函数）**：

### 8.1 GPS到位置转换

```text
convert_gps_to_position: GPS_Tracking_Schema → Position_Schema
```

转换规则：

- NMEA消息提取位置信息
- 计算位置精度
- 验证位置有效性

### 8.2 位置到轨迹转换

```text
convert_positions_to_trajectory: List<Position_Schema> → Trajectory_Analysis_Schema
```

转换规则：

- 位置序列转换为轨迹点序列
- 计算轨迹统计信息（距离、速度等）
- 检测停留点

### 8.3 GPS到北斗转换

```text
convert_gps_to_beidou: GPS_Tracking_Schema → Beidou_Tracking_Schema
```

转换规则：

- GPS位置映射到北斗位置
- GPS消息格式转换为BDS消息格式
- 保持位置精度

---

## 9. 形式化定理

### 9.1 数据完整性定理

**定理1（数据完整性）**：

对于任意Vehicle Tracking Schema实例 `tracking`，如果满足以下条件：

1. 所有实体ID唯一
2. 所有位置数据有效（纬度在-90到90之间，经度在-180到180之间）
3. 所有必需字段非空
4. 所有数值字段满足范围约束

则 `tracking` 是数据完整的。

**证明**：

根据定义8（约束规则），数据完整性约束包括实体唯一性、位置有效性、必需字段非空和数值范围约束。如果Vehicle Tracking Schema实例满足所有这些约束，则它是数据完整的。

### 9.2 位置一致性定理

**定理2（位置一致性）**：

对于任意Vehicle Tracking Schema实例 `tracking`，如果满足以下条件：

1. 所有位置数据的地理坐标在有效范围内
2. 轨迹点按时间顺序排列
3. 相邻轨迹点之间的距离不超过阈值

则 `tracking` 的位置数据是一致的。

**证明**：

根据定义8（约束规则），位置一致性要求位置数据有效、时间顺序正确、轨迹连续。如果Vehicle Tracking Schema实例满足这些约束，则它的位置数据是一致的。

### 9.3 轨迹连续性定理

**定理3（轨迹连续性）**：

对于任意轨迹 `trajectory`，如果：

1. 轨迹点数量 ≥ 2
2. 相邻轨迹点之间的时间间隔 > 0
3. 相邻轨迹点之间的距离不超过最大速度 × 时间间隔

则轨迹是连续的。

**证明**：

根据定义6（轨迹分析Schema），轨迹连续性要求轨迹点按时间顺序排列，且相邻点之间的距离合理。如果轨迹满足这些条件，则它是连续的。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
