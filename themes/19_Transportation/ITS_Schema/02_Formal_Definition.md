# 智能交通系统Schema形式化定义

## 📑 目录

- [智能交通系统Schema形式化定义](#智能交通系统schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
    - [1.1 基本定义](#11-基本定义)
    - [1.2 Schema结构](#12-schema结构)
  - [2. 交通数据采集Schema](#2-交通数据采集schema)
  - [3. 交通信号控制Schema](#3-交通信号控制schema)
  - [4. 车辆通信Schema](#4-车辆通信schema)
  - [5. 路况分析Schema](#5-路况分析schema)
  - [6. 类型系统](#6-类型系统)
    - [6.1 基本类型](#61-基本类型)
    - [6.2 复合类型](#62-复合类型)
  - [7. 约束规则](#7-约束规则)
    - [7.1 数据完整性约束](#71-数据完整性约束)
    - [7.2 业务逻辑约束](#72-业务逻辑约束)
  - [8. 转换函数](#8-转换函数)
    - [8.1 数据格式转换](#81-数据格式转换)
    - [8.2 协议转换](#82-协议转换)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 数据完整性定理](#91-数据完整性定理)
    - [9.2 信号控制一致性定理](#92-信号控制一致性定理)

---

## 1. 形式化模型

### 1.1 基本定义

设 `ITS_Schema` 为智能交通系统Schema的集合，
`Traffic_Data` 为交通数据的集合，
`Signal_Control` 为信号控制的集合，
`Vehicle_Communication` 为车辆通信的集合，
`Traffic_Analysis` 为路况分析的集合。

**定义1（ITS Schema）**：
ITS Schema是一个四元组：

```text
ITS_Schema = (Traffic_Data, Signal_Control, Vehicle_Communication, Traffic_Analysis)
```

其中：

- `Traffic_Data`：交通数据采集Schema
- `Signal_Control`：交通信号控制Schema
- `Vehicle_Communication`：车辆通信Schema
- `Traffic_Analysis`：路况分析Schema

### 1.2 Schema结构

**定义2（ITS Schema结构）**：

```text
ITS_Schema = (Traffic_Data ⊕ Signal_Control ⊕ Vehicle_Communication
            ⊕ Traffic_Analysis) × ITS_Profile
```

其中 `ITS_Profile` 是ITS配置参数。

---

## 2. 交通数据采集Schema

**定义3（交通数据采集Schema）**：

```text
Traffic_Data_Schema = (Sensor_Data ⊕ Video_Data ⊕ GPS_Data ⊕ Weather_Data)
```

**形式化DSL定义**：

```dsl
schema TrafficData {
  sensor_data: Optional<SensorData> {
    sensor_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
    sensor_type: Enum { Loop, Radar, Infrared, Ultrasonic } @required
    location: Location {
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      road_name: Optional<String> @max_length(100)
      lane_id: Optional<Integer> @range(1, 10)
    } @required

    traffic_metrics: TrafficMetrics {
      vehicle_count: Integer @range(0, 10000) @required
      average_speed: Decimal @range(0, 200) @unit("KMH") @required @precision(2)
      occupancy: Decimal @range(0, 100) @unit("%") @required @precision(2)
      density: Decimal @range(0, 200) @unit("veh/km") @precision(2)
      headway: Decimal @range(0, 300) @unit("seconds") @precision(2)
    } @required

    timestamp: DateTime @required
    data_quality: Enum { Good, Fair, Poor } @default(Good)
  }

  video_data: Optional<VideoData> {
    camera_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
    camera_type: Enum { Fixed, PTZ, Panoramic } @required
    location: Location @required

    detection_results: List<VehicleDetection> {
      vehicle_id: String @required
      vehicle_type: Enum { Car, Truck, Bus, Motorcycle, Bicycle } @required
      bbox: BoundingBox {
        x1: Integer @range(0, 10000) @required
        y1: Integer @range(0, 10000) @required
        x2: Integer @range(0, 10000) @required
        y2: Integer @range(0, 10000) @required
      } @required
      confidence: Decimal @range(0, 1) @required @precision(3)
      license_plate: Optional<String> @pattern("^[A-Z0-9]{1,10}$")
      speed: Optional<Decimal> @range(0, 200) @unit("KMH") @precision(2)
    }

    timestamp: DateTime @required
    frame_id: String @required
    resolution: Enum { HD, FullHD, 4K } @default(FullHD)
  }

  gps_data: Optional<GPSData> {
    vehicle_id: String @required @unique
    location: Location {
      latitude: Decimal @range(-90, 90) @required @precision(7)
      longitude: Decimal @range(-180, 180) @required @precision(7)
      altitude: Optional<Decimal> @range(-500, 10000) @unit("meters") @precision(2)
    } @required

    movement: Movement {
      speed: Decimal @range(0, 200) @unit("KMH") @required @precision(2)
      heading: Decimal @range(0, 360) @unit("degrees") @required @precision(2)
      acceleration: Optional<Decimal> @range(-10, 10) @unit("m/s²") @precision(2)
    } @required

    timestamp: DateTime @required
    satellites: Integer @range(0, 20) @default(0)
    quality: Enum { Fix, DGPS, RTK } @default(Fix)
  }

  weather_data: Optional<WeatherData> {
    station_id: String @required @unique
    location: Location @required

    conditions: WeatherConditions {
      temperature: Decimal @range(-50, 60) @unit("Celsius") @required @precision(1)
      humidity: Decimal @range(0, 100) @unit("%") @required @precision(1)
      visibility: Decimal @range(0, 50000) @unit("meters") @required @precision(0)
      wind_speed: Decimal @range(0, 200) @unit("KMH") @required @precision(1)
      wind_direction: Decimal @range(0, 360) @unit("degrees") @required @precision(1)
      precipitation: Decimal @range(0, 500) @unit("mm/h") @required @precision(2)
      road_condition: Enum { Dry, Wet, Snow, Ice } @required
    } @required

    timestamp: DateTime @required
  }
} @standard("ISO_14813")
```

---

## 3. 交通信号控制Schema

**定义4（交通信号控制Schema）**：

```text
Signal_Control_Schema = (Signal_State ⊕ Phase_Definition ⊕ Timing_Plan ⊕ Coordination)
```

**形式化DSL定义**：

```dsl
schema TrafficSignalControl {
  intersection_id: String @pattern("^[A-Z0-9]{10}$") @required @unique
  intersection_name: String @max_length(100) @required
  location: Location @required

  signal_states: List<SignalState> {
    signal_id: String @required @unique
    direction: Enum { North, South, East, West, Northeast, Northwest, Southeast, Southwest } @required
    current_state: Enum { Red, Yellow, Green, RedYellow } @required
    state_duration: Integer @range(0, 300) @unit("seconds") @required
    next_state: Enum { Red, Yellow, Green } @required
    transition_time: DateTime @required
  } @required

  phases: List<Phase> {
    phase_id: Integer @range(1, 20) @required @unique
    phase_name: String @max_length(50)
    signals: List<String> @required  // signal_id列表
    duration: Integer @range(5, 300) @unit("seconds") @required
    min_duration: Integer @range(5, 60) @unit("seconds") @required
    max_duration: Integer @range(60, 300) @unit("seconds") @required
    yellow_time: Integer @range(3, 10) @unit("seconds") @default(5)
    all_red_time: Integer @range(0, 5) @unit("seconds") @default(2)
  } @required

  timing_plan: TimingPlan {
    cycle_time: Integer @range(60, 600) @unit("seconds") @required
    offset: Integer @range(0, 600) @unit("seconds") @default(0)
    phase_sequence: List<Integer> @required  // phase_id序列
    green_split: List<Decimal> @required  // 各相位绿信比
    coordination: Optional<Coordination> {
      coordination_type: Enum { Isolated, Arterial, Network } @required
      master_intersection: Optional<String>
      coordination_offset: Optional<Integer> @range(0, 600) @unit("seconds")
    }
  } @required

  control_mode: Enum { Fixed, Actuated, Adaptive, Coordinated } @default(Fixed)
  timestamp: DateTime @required
} @standard("ISO_14813")
```

---

## 4. 车辆通信Schema

**定义5（车辆通信Schema）**：

```text
Vehicle_Communication_Schema = (V2V_Message ⊕ V2I_Message ⊕ V2X_Message)
```

**形式化DSL定义**：

```dsl
schema VehicleCommunication {
  v2v_messages: List<V2VMessage> {
    message_type: Enum { BSM, EEBL, BSM_PartII } @required
    vehicle_id: Integer @range(0, 4294967295) @required
    timestamp: DateTime @required

    bsm_core: BSMCore {
      position: Position {
        latitude: Decimal @range(-90, 90) @required @precision(7)
        longitude: Decimal @range(-180, 180) @required @precision(7)
        elevation: Optional<Decimal> @range(-500, 10000) @unit("meters") @precision(2)
      } @required

      accuracy: PositionalAccuracy {
        semi_major: Decimal @range(0, 255) @unit("meters") @required
        semi_minor: Decimal @range(0, 255) @unit("meters") @required
        orientation: Decimal @range(0, 65535) @unit("degrees") @required
      }

      transmission: TransmissionState @required
      speed: Decimal @range(0, 8191) @unit("0.02 m/s") @required
      heading: Decimal @range(0, 28800) @unit("0.0125 degrees") @required
      angle: Decimal @range(-127, 127) @unit("1.5 degrees") @default(0)
      acceleration: AccelerationSet4Way {
        long: Decimal @range(-2000, 2001) @unit("0.01 m/s²") @required
        lat: Decimal @range(-2000, 2001) @unit("0.01 m/s²") @required
        vert: Decimal @range(-127, 127) @unit("0.02 G") @default(0)
        yaw: Decimal @range(-32767, 32767) @unit("0.01 deg/s") @default(0)
      }

      brakes: BrakeSystemStatus @required
      size: VehicleSize {
        width: Integer @range(0, 1023) @unit("0.01 meters") @required
        length: Integer @range(0, 4095) @unit("0.01 meters") @required
      } @required
    } @required

    bsm_part_ii: Optional<BSMPartII> {
      vehicle_safety_extensions: Optional<VehicleSafetyExtensions>
      vehicle_status: Optional<VehicleStatus>
      supplemental_vehicle_data: Optional<SupplementalVehicleData>
    }
  }

  v2i_messages: List<V2IMessage> {
    message_type: Enum { SPAT, MAP, RSI, RSM } @required
    rsu_id: String @required
    intersection_id: Optional<String>
    timestamp: DateTime @required

    spat_data: Optional<SPATData> {
      intersections: List<IntersectionState> {
        intersection_id: Integer @required
        status: IntersectionStatusObject @required
        states: List<MovementState> {
          movement_name: String @required
          signal_group: Integer @range(1, 255) @required
          state_time_speed: List<MovementEvent> {
            event_state: Enum { Unavailable, Dark, Stop_Then_Proceed, Stop_And_Remain,
                               Pre_Movement, Permissive_Movement_Allowed,
                               Protected_Movement_Allowed, Permissive_Clearance,
                               Protected_Clearance, Caution_Conflicting_Traffic } @required
            timing: Optional<Timing> {
              start_time: Integer @range(0, 65535) @unit("0.1 seconds")
              min_end_time: Integer @range(0, 65535) @unit("0.1 seconds")
              max_end_time: Optional<Integer> @range(0, 65535) @unit("0.1 seconds")
              likely_time: Optional<Integer> @range(0, 65535) @unit("0.1 seconds")
              confidence: Optional<Integer> @range(0, 200) @unit("0.5 percent")
            }
            speeds: Optional<List<AdvisorySpeed>>
          } @required
        } @required
      } @required
    }

    map_data: Optional<MAPData> {
      intersections: List<IntersectionGeometry> {
        intersection_id: Integer @required
        name: Optional<String>
        ref_point: Position3D @required
        lane_width: Optional<Integer> @range(0, 32767) @unit("0.01 meters")
        speed_limits: Optional<List<SpeedLimit>>
        lane_set: List<GenericLane> {
          lane_id: Integer @required
          lane_name: Optional<String>
          ingress_approach: Optional<Integer>
          egress_approach: Optional<Integer>
          lane_attributes: LaneAttributes @required
          maneuvers: Optional<List<AllowedManeuvers>>
          node_list: Optional<NodeListXY>
          connects_to: Optional<List<Connection>>
        } @required
      } @required
    }
  }

  v2x_messages: List<V2XMessage> {
    message_type: Enum { CAM, DENM, IVI, CPM } @required
    source_id: String @required
    destination_id: Optional<String>
    timestamp: DateTime @required

    cam_data: Optional<CAMData> {
      generation_delta_time: Integer @range(0, 65535) @unit("0.1 milliseconds") @required
      cam: CAM {
        basic_container: BasicContainer @required
        high_frequency_container: Optional<HighFrequencyContainer>
        low_frequency_container: Optional<LowFrequencyContainer>
        special_vehicle_container: Optional<SpecialVehicleContainer>
      } @required
    }

    denm_data: Optional<DENMData> {
      management: ManagementContainer @required
      situation: Optional<SituationContainer>
      location: Optional<LocationContainer>
      alacarte: Optional<AlacarteContainer>
    }
  }
} @standard("SAE_J2735", "ETSI_ITS")
```

---

## 5. 路况分析Schema

**定义6（路况分析Schema）**：

```text
Traffic_Analysis_Schema = (Flow_Analysis ⊕ Congestion_Detection ⊕ Route_Planning ⊕ Event_Detection)
```

**形式化DSL定义**：

```dsl
schema TrafficAnalysis {
  flow_analysis: Optional<FlowAnalysis> {
    segment_id: String @required @unique
    location: Location @required
    time_period: TimePeriod {
      start_time: DateTime @required
      end_time: DateTime @required
      duration: Integer @range(60, 86400) @unit("seconds") @required
    } @required

    flow_metrics: FlowMetrics {
      total_volume: Integer @range(0, 1000000) @required
      average_volume: Decimal @range(0, 10000) @unit("veh/h") @required @precision(2)
      peak_volume: Integer @range(0, 1000000) @required
      peak_hour: Integer @range(0, 23) @required

      speed_metrics: SpeedMetrics {
        average_speed: Decimal @range(0, 200) @unit("KMH") @required @precision(2)
        median_speed: Decimal @range(0, 200) @unit("KMH") @required @precision(2)
        percentile_85_speed: Decimal @range(0, 200) @unit("KMH") @required @precision(2)
        speed_variance: Decimal @range(0, 10000) @unit("(KMH)²") @precision(2)
      } @required

      density_metrics: DensityMetrics {
        average_density: Decimal @range(0, 200) @unit("veh/km") @required @precision(2)
        peak_density: Decimal @range(0, 200) @unit("veh/km") @required @precision(2)
        jam_density: Optional<Decimal> @range(0, 200) @unit("veh/km") @precision(2)
      } @required

      occupancy_metrics: OccupancyMetrics {
        average_occupancy: Decimal @range(0, 100) @unit("%") @required @precision(2)
        peak_occupancy: Decimal @range(0, 100) @unit("%") @required @precision(2)
      } @required
    } @required

    flow_pattern: Enum { Free_Flow, Stable_Flow, Unstable_Flow, Congested } @required
  }

  congestion_detection: Optional<CongestionDetection> {
    segment_id: String @required
    location: Location @required

    congestion_status: CongestionStatus {
      is_congested: Boolean @required
      congestion_level: Enum { None, Light, Moderate, Severe } @required
      congestion_index: Decimal @range(0, 1) @required @precision(3)

      indicators: CongestionIndicators {
        speed_ratio: Decimal @range(0, 1) @required @precision(3)  // 实际速度/自由流速度
        occupancy_ratio: Decimal @range(0, 2) @required @precision(3)  // 实际占有率/阈值
        density_ratio: Decimal @range(0, 2) @required @precision(3)  // 实际密度/临界密度
        queue_length: Optional<Decimal> @range(0, 10000) @unit("meters") @precision(0)
        delay_time: Optional<Decimal> @range(0, 3600) @unit("seconds") @precision(0)
      } @required

      start_time: Optional<DateTime>
      duration: Optional<Integer> @range(0, 86400) @unit("seconds")
      affected_length: Optional<Decimal> @range(0, 100000) @unit("meters") @precision(0)
    } @required

    timestamp: DateTime @required
  }

  route_planning: Optional<RoutePlanning> {
    route_id: String @required @unique
    origin: Location @required
    destination: Location @required

    route_options: RouteOptions {
      optimization_criteria: Enum { Shortest, Fastest, Most_Economical, Most_Comfortable } @required
      avoid_tolls: Boolean @default(false)
      avoid_highways: Boolean @default(false)
      avoid_ferries: Boolean @default(false)
    } @required

    calculated_route: CalculatedRoute {
      total_distance: Decimal @range(0, 1000000) @unit("meters") @required @precision(0)
      total_duration: Integer @range(0, 86400) @unit("seconds") @required
      estimated_duration: Integer @range(0, 86400) @unit("seconds") @required

      waypoints: List<Waypoint> {
        sequence: Integer @required
        location: Location @required
        distance_from_origin: Decimal @range(0, 1000000) @unit("meters") @required @precision(0)
        estimated_arrival: DateTime @required
        road_name: Optional<String>
        maneuver: Optional<Enum { Straight, Turn_Left, Turn_Right, U_Turn,
                                 Merge, Exit, Enter_Roundabout, Exit_Roundabout }>
      } @required

      segments: List<RouteSegment> {
        segment_id: String @required
        start_location: Location @required
        end_location: Location @required
        distance: Decimal @range(0, 100000) @unit("meters") @required @precision(0)
        duration: Integer @range(0, 3600) @unit("seconds") @required
        average_speed: Decimal @range(0, 200) @unit("KMH") @required @precision(2)
        road_type: Enum { Highway, Arterial, Local, Ramp } @required
        congestion_level: Enum { None, Light, Moderate, Severe } @required
      } @required
    } @required

    timestamp: DateTime @required
  }

  event_detection: Optional<EventDetection> {
    event_id: String @required @unique
    event_type: Enum { Accident, Construction, Congestion, Weather,
                      Road_Closure, Vehicle_Breakdown, Other } @required
    location: Location @required

    event_details: EventDetails {
      severity: Enum { Low, Medium, High, Critical } @required
      description: String @max_length(500)
      start_time: DateTime @required
      end_time: Optional<DateTime>
      affected_lanes: Optional<List<Integer>>
      affected_directions: Optional<List<Enum { North, South, East, West }>>

      impact: EventImpact {
        affected_length: Decimal @range(0, 100000) @unit("meters") @precision(0)
        expected_delay: Integer @range(0, 3600) @unit("seconds")
        speed_reduction: Decimal @range(0, 100) @unit("KMH") @precision(1)
        capacity_reduction: Decimal @range(0, 100) @unit("%") @precision(1)
      }
    } @required

    detection_method: Enum { Manual, Automatic_Sensor, Automatic_Video,
                            V2X_Report, Other } @required
    confidence: Decimal @range(0, 1) @required @precision(3)
    timestamp: DateTime @required
  }
} @standard("ISO_14813")
```

---

## 6. 类型系统

### 6.1 基本类型

**定义7（基本类型）**：

```text
Basic_Types = {String, Integer, Decimal, Boolean, DateTime, Enum}
```

### 6.2 复合类型

**定义8（位置类型）**：

```text
Location = (latitude: Decimal, longitude: Decimal, altitude: Optional<Decimal>)
```

**定义9（时间类型）**：

```text
TimePeriod = (start_time: DateTime, end_time: DateTime, duration: Integer)
```

---

## 7. 约束规则

### 7.1 数据完整性约束

**约束1（位置范围约束）**：

```text
∀ loc: Location, -90 ≤ loc.latitude ≤ 90 ∧ -180 ≤ loc.longitude ≤ 180
```

**约束2（速度范围约束）**：

```text
∀ speed: Decimal, 0 ≤ speed ≤ 200 (单位：KMH)
```

**约束3（时间顺序约束）**：

```text
∀ tp: TimePeriod, tp.start_time < tp.end_time
```

### 7.2 业务逻辑约束

**约束4（信号相位约束）**：

```text
∀ phase: Phase, phase.min_duration ≤ phase.duration ≤ phase.max_duration
```

**约束5（周期时间约束）**：

```text
∀ plan: TimingPlan, Σ(phase.duration for phase in plan.phases) ≤ plan.cycle_time
```

---

## 8. 转换函数

### 8.1 数据格式转换

**定义10（传感器数据到标准格式转换）**：

```text
convert_sensor_to_standard: Sensor_Raw_Data → Traffic_Data_Schema
```

**定义11（BSM消息到标准格式转换）**：

```text
convert_bsm_to_standard: BSM_Bytes → Vehicle_Communication_Schema
```

### 8.2 协议转换

**定义12（SAE J2735到ETSI ITS转换）**：

```text
convert_sae_to_etsi: SAE_J2735_Message → ETSI_ITS_Message
```

---

## 9. 形式化定理

### 9.1 数据完整性定理

**定理1（数据完整性）**：

对于所有交通数据 `td: Traffic_Data`，如果满足以下条件：

1. `td.sensor_data.location.latitude ∈ [-90, 90]`
2. `td.sensor_data.location.longitude ∈ [-180, 180]`
3. `td.sensor_data.traffic_metrics.vehicle_count ≥ 0`
4. `td.sensor_data.traffic_metrics.average_speed ∈ [0, 200]`
5. `td.sensor_data.traffic_metrics.occupancy ∈ [0, 100]`

则 `td` 是完整且有效的。

**证明**：根据约束规则1-3，所有必需字段都在有效范围内，因此数据完整。

### 9.2 信号控制一致性定理

**定理2（信号控制一致性）**：

对于所有信号控制 `sc: Signal_Control`，如果满足以下条件：

1. `sc.timing_plan.cycle_time = Σ(phase.duration for phase in sc.phases)`
2. `∀ phase: Phase, phase.min_duration ≤ phase.duration ≤ phase.max_duration`
3. `sc.signal_states` 与 `sc.phases` 一致

则 `sc` 是一致的。

**证明**：根据约束规则4-5，所有相位时长总和等于周期时间，且每个相位时长在有效范围内，因此信号控制一致。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
