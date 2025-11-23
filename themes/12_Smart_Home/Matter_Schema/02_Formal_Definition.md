# Matter Schema形式化定义

## 📑 目录

- [Matter Schema形式化定义](#matter-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. On/Off Cluster Schema](#2-onoff-cluster-schema)
  - [3. Level Control Cluster Schema](#3-level-control-cluster-schema)
  - [4. Color Control Cluster Schema](#4-color-control-cluster-schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)
    - [8.1 集群一致性定理](#81-集群一致性定理)
    - [8.2 命令执行有效性定理](#82-命令执行有效性定理)

---

## 1. 形式化模型

**定义1（Matter Schema）**：
Matter Schema是一个四元组：

```text
Matter_Schema = (Device_Cluster, Attribute_Definition,
                Command_Definition, Event_Definition)
```

其中：

- `Device_Cluster`：设备集群Schema
- `Attribute_Definition`：属性定义Schema
- `Command_Definition`：命令定义Schema
- `Event_Definition`：事件定义Schema

---

## 2. On/Off Cluster Schema

**定义2（On/Off Cluster Schema）**：

```text
OnOff_Cluster_Schema = (OnOff_Attribute, On_Command, Off_Command, Toggle_Command)
```

**形式化DSL定义**：

```dsl
schema OnOffCluster {
  cluster_id: Integer @value(0x0006) @required

  attributes: {
    on_off: Boolean @required @default(false)
    global_scene_control: Boolean @default(true)
    on_time: Integer @range(0, 65534) @unit("seconds")
    off_wait_time: Integer @range(0, 65534) @unit("seconds")
    start_up_on_off: Enum { Off, On, Toggle } @default(Off)
  }

  commands: {
    on: {
      command_id: Integer @value(0x00) @required
      parameters: {}
    }
    off: {
      command_id: Integer @value(0x01) @required
      parameters: {}
    }
    toggle: {
      command_id: Integer @value(0x02) @required
      parameters: {}
    }
    off_with_effect: {
      command_id: Integer @value(0x40) @required
      parameters: {
        effect_identifier: Enum { DelayedAllOff, DyingLight }
        effect_variant: Integer @range(0, 255)
      }
    }
    on_with_recall_global_scene: {
      command_id: Integer @value(0x41) @required
      parameters: {}
    }
    on_with_timed_off: {
      command_id: Integer @value(0x42) @required
      parameters: {
        on_off_control: Integer @range(0, 1)
        on_time: Integer @range(0, 65534) @unit("seconds")
        off_wait_time: Integer @range(0, 65534) @unit("seconds")
      }
    }
  }

  events: {
    off_with_effect: {
      event_id: Integer @value(0x00)
      effect_identifier: Enum { DelayedAllOff, DyingLight }
      effect_variant: Integer @range(0, 255)
    }
  }
} @standard("Matter_1.0")
```

---

## 3. Level Control Cluster Schema

**定义3（Level Control Cluster Schema）**：

```text
Level_Control_Cluster_Schema = (Current_Level, Min_Level, Max_Level,
                                Move_Command, Step_Command, Stop_Command)
```

**形式化DSL定义**：

```dsl
schema LevelControlCluster {
  cluster_id: Integer @value(0x0008) @required

  attributes: {
    current_level: Integer @range(0, 254) @required @default(0)
    remaining_time: Integer @range(0, 65534) @unit("seconds")
    min_level: Integer @range(0, 254) @default(1)
    max_level: Integer @range(1, 254) @default(254)
    current_frequency: Integer @range(0, 65534) @unit("Hz")
    min_frequency: Integer @range(0, 65534) @unit("Hz")
    max_frequency: Integer @range(0, 65534) @unit("Hz")
    options: Integer @range(0, 15)
    on_off_transition_time: Integer @range(0, 65534) @unit("seconds")
    on_level: Integer @range(0, 254)
    on_transition_time: Integer @range(0, 65534) @unit("seconds")
    off_transition_time: Integer @range(0, 65534) @unit("seconds")
    default_move_rate: Integer @range(0, 254)
    start_up_current_level: Integer @range(0, 254)
  }

  commands: {
    move_to_level: {
      command_id: Integer @value(0x00) @required
      parameters: {
        level: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        option_mask: Integer @range(0, 15)
        option_override: Integer @range(0, 15)
      }
    }
    move: {
      command_id: Integer @value(0x01) @required
      parameters: {
        move_mode: Enum { Up, Down } @required
        rate: Integer @range(0, 254)
        option_mask: Integer @range(0, 15)
        option_override: Integer @range(0, 15)
      }
    }
    step: {
      command_id: Integer @value(0x02) @required
      parameters: {
        step_mode: Enum { Up, Down } @required
        step_size: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        option_mask: Integer @range(0, 15)
        option_override: Integer @range(0, 15)
      }
    }
    stop: {
      command_id: Integer @value(0x03) @required
      parameters: {
        option_mask: Integer @range(0, 15)
        option_override: Integer @range(0, 15)
      }
    }
    move_to_level_with_on_off: {
      command_id: Integer @value(0x04) @required
      parameters: {
        level: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
      }
    }
    move_with_on_off: {
      command_id: Integer @value(0x05) @required
      parameters: {
        move_mode: Enum { Up, Down } @required
        rate: Integer @range(0, 254)
      }
    }
    step_with_on_off: {
      command_id: Integer @value(0x06) @required
      parameters: {
        step_mode: Enum { Up, Down } @required
        step_size: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
      }
    }
    stop_with_on_off: {
      command_id: Integer @value(0x07) @required
      parameters: {}
    }
  }
} @standard("Matter_1.0")
```

---

## 4. Color Control Cluster Schema

**定义4（Color Control Cluster Schema）**：

```text
Color_Control_Cluster_Schema = (Current_Hue, Current_Saturation,
                                Current_X, Current_Y, Color_Temperature)
```

**形式化DSL定义**：

```dsl
schema ColorControlCluster {
  cluster_id: Integer @value(0x0300) @required

  attributes: {
    current_hue: Integer @range(0, 254) @required @default(0)
    current_saturation: Integer @range(0, 254) @required @default(0)
    remaining_time: Integer @range(0, 65534) @unit("seconds")
    current_x: Integer @range(0, 65279) @required @default(0)
    current_y: Integer @range(0, 65279) @required @default(0)
    drift_compensation: Enum { None, Other, TemperatureMonitoring, OpticalLuminanceMonitoring, OpticalColorMonitoring } @default(None)
    compensation_text: String @max_length(254)
    color_temperature_mireds: Integer @range(0, 65279) @required @default(0)
    color_mode: Enum { CurrentHueAndCurrentSaturation, CurrentXAndCurrentY, ColorTemperatureMireds } @required
    options: Integer @range(0, 15)
    number_of_primaries: Integer @range(0, 6) @default(0)
    primary1_x: Integer @range(0, 65279)
    primary1_y: Integer @range(0, 65279)
    primary1_intensity: Integer @range(0, 254)
    primary2_x: Integer @range(0, 65279)
    primary2_y: Integer @range(0, 65279)
    primary2_intensity: Integer @range(0, 254)
    primary3_x: Integer @range(0, 65279)
    primary3_y: Integer @range(0, 65279)
    primary3_intensity: Integer @range(0, 254)
    primary4_x: Integer @range(0, 65279)
    primary4_y: Integer @range(0, 65279)
    primary4_intensity: Integer @range(0, 254)
    primary5_x: Integer @range(0, 65279)
    primary5_y: Integer @range(0, 65279)
    primary5_intensity: Integer @range(0, 254)
    primary6_x: Integer @range(0, 65279)
    primary6_y: Integer @range(0, 65279)
    primary6_intensity: Integer @range(0, 254)
    white_point_x: Integer @range(0, 65279)
    white_point_y: Integer @range(0, 65279)
    color_point_r_x: Integer @range(0, 65279)
    color_point_r_y: Integer @range(0, 65279)
    color_point_r_intensity: Integer @range(0, 254)
    color_point_g_x: Integer @range(0, 65279)
    color_point_g_y: Integer @range(0, 65279)
    color_point_g_intensity: Integer @range(0, 254)
    color_point_b_x: Integer @range(0, 65279)
    color_point_b_y: Integer @range(0, 65279)
    color_point_b_intensity: Integer @range(0, 254)
    enhanced_current_hue: Integer @range(0, 65535) @required @default(0)
    enhanced_color_mode: Enum { CurrentHueAndCurrentSaturation, CurrentXAndCurrentY, ColorTemperatureMireds, EnhancedCurrentHueAndCurrentSaturation } @required
    color_loop_active: Integer @range(0, 1) @default(0)
    color_loop_direction: Enum { DecrementHue, IncrementHue } @default(DecrementHue)
    color_loop_time: Integer @range(0, 65534) @unit("seconds")
    color_loop_start_enhanced_hue: Integer @range(0, 65535)
    color_loop_stored_enhanced_hue: Integer @range(0, 65535)
    color_capabilities: Integer @range(0, 31)
    color_temp_physical_min_mireds: Integer @range(0, 65279)
    color_temp_physical_max_mireds: Integer @range(0, 65279)
    couple_color_temp_to_level_min_mireds: Integer @range(0, 65279)
    start_up_color_temperature_mireds: Integer @range(0, 65279)
  }

  commands: {
    move_to_hue: {
      command_id: Integer @value(0x00) @required
      parameters: {
        hue: Integer @range(0, 254) @required
        direction: Enum { ShortestDistance, LongestDistance } @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_hue: {
      command_id: Integer @value(0x01) @required
      parameters: {
        move_mode: Enum { Stop, Up, Down } @required
        rate: Integer @range(0, 254) @required
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    step_hue: {
      command_id: Integer @value(0x02) @required
      parameters: {
        step_mode: Enum { Up, Down } @required
        step_size: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_to_saturation: {
      command_id: Integer @value(0x03) @required
      parameters: {
        saturation: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_saturation: {
      command_id: Integer @value(0x04) @required
      parameters: {
        move_mode: Enum { Stop, Up, Down } @required
        rate: Integer @range(0, 254) @required
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    step_saturation: {
      command_id: Integer @value(0x05) @required
      parameters: {
        step_mode: Enum { Up, Down } @required
        step_size: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_to_hue_and_saturation: {
      command_id: Integer @value(0x06) @required
      parameters: {
        hue: Integer @range(0, 254) @required
        saturation: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_to_color: {
      command_id: Integer @value(0x07) @required
      parameters: {
        color_x: Integer @range(0, 65279) @required
        color_y: Integer @range(0, 65279) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_color: {
      command_id: Integer @value(0x08) @required
      parameters: {
        rate_x: Integer @range(-65534, 65534) @required
        rate_y: Integer @range(-65534, 65534) @required
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    step_color: {
      command_id: Integer @value(0x09) @required
      parameters: {
        step_x: Integer @range(-65534, 65534) @required
        step_y: Integer @range(-65534, 65534) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_to_color_temperature: {
      command_id: Integer @value(0x0A) @required
      parameters: {
        color_temperature_mireds: Integer @range(0, 65279) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    enhanced_move_to_hue: {
      command_id: Integer @value(0x40) @required
      parameters: {
        enhanced_hue: Integer @range(0, 65535) @required
        direction: Enum { ShortestDistance, LongestDistance } @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    enhanced_move_hue: {
      command_id: Integer @value(0x41) @required
      parameters: {
        move_mode: Enum { Stop, Up, Down } @required
        rate: Integer @range(0, 65534) @required
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    enhanced_step_hue: {
      command_id: Integer @value(0x42) @required
      parameters: {
        step_mode: Enum { Up, Down } @required
        step_size: Integer @range(0, 65535) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    enhanced_move_to_hue_and_saturation: {
      command_id: Integer @value(0x43) @required
      parameters: {
        enhanced_hue: Integer @range(0, 65535) @required
        saturation: Integer @range(0, 254) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    color_loop_set: {
      command_id: Integer @value(0x44) @required
      parameters: {
        update_flags: Integer @range(0, 15) @required
        action: Enum { DeactivateColorLoop, ActivateColorLoopFromCurrentHue, ActivateColorLoopFromEnhancedCurrentHue, ActivateColorLoopFromColorLoopStartEnhancedHue } @required
        direction: Enum { DecrementHue, IncrementHue } @required
        time: Integer @range(0, 65534) @unit("seconds")
        start_hue: Integer @range(0, 65535)
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    stop_move_step: {
      command_id: Integer @value(0x47) @required
      parameters: {
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    move_color_temperature: {
      command_id: Integer @value(0x4B) @required
      parameters: {
        move_mode: Enum { Stop, Up, Down } @required
        rate: Integer @range(0, 65534) @required
        color_temperature_minimum_mireds: Integer @range(0, 65279) @required
        color_temperature_maximum_mireds: Integer @range(0, 65279) @required
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
    step_color_temperature: {
      command_id: Integer @value(0x4C) @required
      parameters: {
        step_mode: Enum { Up, Down } @required
        step_size: Integer @range(0, 65534) @required
        transition_time: Integer @range(0, 65534) @unit("seconds")
        color_temperature_minimum_mireds: Integer @range(0, 65279) @required
        color_temperature_maximum_mireds: Integer @range(0, 65279) @required
        options_mask: Integer @range(0, 15)
        options_override: Integer @range(0, 15)
      }
    }
  }
} @standard("Matter_1.0")
```

---

## 5. 类型系统

**定义5（Matter数据类型）**：

```text
Matter_Data_Type = Cluster | Attribute | Command | Event |
                  Device_Type | Endpoint | Node
```

**基本类型定义**：

```dsl
type Cluster {
  cluster_id: Integer @required
  attributes: Map<String, Attribute>
  commands: Map<String, Command>
  events: Map<String, Event>
}

type Attribute {
  attribute_id: Integer @required
  data_type: DataType @required
  value: Any
  writable: Boolean @default(false)
}

type Command {
  command_id: Integer @required
  parameters: Map<String, Parameter>
}
```

---

## 6. 约束规则

**约束1（集群属性完整性）**：

```text
∀ cluster ∈ Matter_Cluster:
  cluster.cluster_id ≠ ∅
  ∧ validate_cluster_attributes(cluster.attributes)
  ∧ validate_cluster_commands(cluster.commands)
```

**约束2（命令参数有效性）**：

```text
∀ command ∈ Matter_Command:
  command.command_id ≠ ∅
  ∧ validate_command_parameters(command.parameters)
  ∧ command_executable(command)
```

**约束3（属性值有效性）**：

```text
∀ attribute ∈ Matter_Attribute:
  validate_attribute_value(attribute.value, attribute.data_type)
  ∧ attribute_range_check(attribute.value, attribute.data_type)
```

---

## 7. 转换函数

**函数1（Matter到Zigbee转换）**：

```text
convert_Matter_Cluster_to_Zigbee: Matter_Cluster → Zigbee_Cluster
```

**函数2（Zigbee到Matter转换）**：

```text
convert_Zigbee_to_Matter_Cluster: Zigbee_Cluster → Matter_Cluster
```

**函数3（集群验证）**：

```text
validate_matter_cluster: Matter_Cluster → Bool
```

---

## 8. 形式化定理

### 8.1 集群一致性定理

**定理1（Matter集群一致性）**：

```text
∀ cluster ∈ Matter_Cluster:
  validate_matter_cluster(cluster)
  → cluster_consistency(cluster)
  ∧ attribute_consistency(cluster.attributes)
```

### 8.2 命令执行有效性定理

**定理2（命令执行有效性）**：

```text
∀ command ∈ Matter_Command:
  validate_command_execution(command)
  → command_executability(command)
  ∧ parameter_validity(command.parameters)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
