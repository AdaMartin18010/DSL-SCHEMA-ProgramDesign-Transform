# IEC61850 Schema形式化定义

## 📑 目录

- [IEC61850 Schema形式化定义](#iec61850-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 逻辑节点Schema](#2-逻辑节点schema)
  - [3. 数据对象Schema](#3-数据对象schema)
  - [4. 服务Schema](#4-服务schema)
  - [5. SCL Schema](#5-scl-schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 逻辑节点完整性定理](#91-逻辑节点完整性定理)
    - [9.2 数据对象一致性定理](#92-数据对象一致性定理)

---

## 1. 形式化模型

**定义1（IEC61850 Schema）**：
IEC61850 Schema是一个四元组：

```text
IEC61850_Schema = (Logical_Node_Schema, Data_Object_Schema,
                  Service_Schema, SCL_Schema)
```

其中：

- `Logical_Node_Schema`：逻辑节点Schema
- `Data_Object_Schema`：数据对象Schema
- `Service_Schema`：服务Schema
- `SCL_Schema`：系统配置语言Schema

---

## 2. 逻辑节点Schema

**定义2（逻辑节点Schema）**：

```text
Logical_Node_Schema = (LNClass, LNInstance, LNName, LNData)
```

**形式化DSL定义**：

```dsl
schema LogicalNode {
  ln_class: String @pattern("^[A-Z]{4}$") @required
  ln_instance: Integer @range(1, 99) @required
  ln_name: String @pattern("^[A-Z]{4}[0-9]{1,2}$") @required @unique
  ln_desc: String @max_length(200)
  ln_prefix: String @max_length(10)

  ln_data: {
    data_objects: List<DataObject> @required
    data_attributes: List<DataAttribute> @required
  } @required
} @standard("IEC61850")
```

**标准逻辑节点类**：

- **XCBR**：断路器逻辑节点
- **XSWI**：开关逻辑节点
- **MMXU**：测量单元逻辑节点
- **PTRC**：保护跳闸条件逻辑节点
- **TCTR**：电流互感器逻辑节点
- **TVTR**：电压互感器逻辑节点

---

## 3. 数据对象Schema

**定义3（数据对象Schema）**：

```text
Data_Object_Schema = (DOClass, DOInstance, DOData, DOType)
```

**形式化DSL定义**：

```dsl
schema DataObject {
  do_class: String @pattern("^[A-Z][a-zA-Z0-9]*$") @required
  do_instance: String @max_length(50)
  do_name: String @max_length(100) @required @unique
  do_desc: String @max_length(200)
  do_type: String @required

  do_data: {
    data_attributes: List<DataAttribute> @required
    data_structures: List<DataStructure>
  } @required
} @standard("IEC61850")
```

**标准数据对象类**：

- **Pos**：位置（Position）
- **St**：状态（Status）
- **Op**：操作（Operate）
- **Mod**：模式（Mode）
- **Beh**：行为（Behaviour）
- **Health**：健康状态（Health）

---

## 4. 服务Schema

**定义4（服务Schema）**：

```text
Service_Schema = (MMS_Service, GOOSE_Service, SMV_Service)
```

**形式化DSL定义**：

```dsl
schema MMSService {
  service_name: String @required
  service_type: Enum { GetDirectory, Read, Write, GetNameList,
                       GetVariableAccessAttributes, DefineNamedVariable,
                       DeleteNamedVariable, GetNamedVariableListAttributes } @required
  service_parameters: Map<String, Any>
  service_result: Map<String, Any>
  service_timestamp: DateTime @required
} @standard("IEC61850")

schema GOOSEService {
  go_cb_ref: String @required @unique
  go_id: String @required
  go_dst_address: String @pattern("^[0-9A-F]{12}$") @required
  go_app_id: Integer @range(0, 16383) @required
  go_data_set: String @required
  go_t: Integer @range(0, 4294967295) @required
  go_nds_com: Boolean @required
  go_num_dat_set_entries: Integer @range(0, 65535) @required
  go_all_data: List<DataObject> @required
} @standard("IEC61850")

schema SMVService {
  sv_cb_ref: String @required @unique
  sv_id: String @required
  sv_dst_address: String @pattern("^[0-9A-F]{12}$") @required
  sv_app_id: Integer @range(0, 16383) @required
  sv_data_set: String @required
  sv_smp_rate: Integer @range(80, 14400) @required
  sv_no_asdu: Integer @range(1, 65535) @required
  sv_smp_synch: Boolean @required
  sv_all_data: List<DataObject> @required
} @standard("IEC61850")
```

---

## 5. SCL Schema

**定义5（SCL Schema）**：

```text
SCL_Schema = (IED_Config, Communication_Config, Data_Model_Config)
```

**形式化DSL定义**：

```dsl
schema SCLConfig {
  scl_version: String @pattern("^[0-9]+\\.[0-9]+$") @required
  scl_revision: String @max_length(50)
  scl_release: String @max_length(50)

  header: {
    id: String @required @unique
    version: String @required
    revision: String
    tool_id: String
    name_structure: Enum { IEDName, FixedName } @required
  } @required

  ied_config: {
    ied_list: List<IEDConfig> @required
  } @required

  communication_config: {
    subnetworks: List<Subnetwork> @required
    connected_aps: List<ConnectedAP> @required
  } @required

  data_model_config: {
    data_type_templates: List<DataTypeTemplate> @required
  } @required
} @standard("IEC61850")

schema IEDConfig {
  ied_name: String @required @unique
  ied_desc: String @max_length(200)
  ied_type: String @max_length(100)
  ied_manufacturer: String @max_length(200)
  ied_config_version: String @max_length(50)

  access_points: List<AccessPoint> @required
  services: {
    dyn_association: Boolean
    get_directory: Boolean
    get_data_object_definition: Boolean
    data_object_directory: Boolean
    get_data_set_value: Boolean
    set_data_set_value: Boolean
    get_data_set_directory: Boolean
    read_write: Boolean
    timer_activated_control: Boolean
    get_cb_values: Boolean
    gse_dir: Boolean
    file_handling: Boolean
  }

  server: {
    server_instances: List<ServerInstance> @required
  } @required
} @standard("IEC61850")

schema ServerInstance {
  server_instance_name: String @required
  server_instance_desc: String @max_length(200)

  logical_devices: List<LogicalDevice> @required
} @standard("IEC61850")

schema LogicalDevice {
  ld_inst: String @required @unique
  ld_desc: String @max_length(200)

  logical_nodes: List<LogicalNode> @required
} @standard("IEC61850")
```

---

## 6. 类型系统

**定义6（IEC61850类型系统）**：

```text
IEC61850_Type_System = (Common_Data_Classes, Basic_Data_Types,
                       Constructed_Data_Types)
```

**基本数据类型**：

- **BOOLEAN**：布尔类型
- **INT8/INT16/INT32/INT64**：整数类型
- **UINT8/UINT16/UINT32/UINT64**：无符号整数类型
- **FLOAT32/FLOAT64**：浮点数类型
- **VISIBLE_STRING**：可见字符串类型
- **OCTET_STRING**：八位字节字符串类型
- **BITSTRING**：位字符串类型
- **TIMESTAMP**：时间戳类型
- **QUALITY**：质量类型
- **CODEDENUM**：编码枚举类型

**公共数据类（CDC）**：

- **SPS**：单点状态（Single Point Status）
- **DPS**：双点状态（Double Point Status）
- **INS**：整数状态（Integer Status）
- **ACT**：控制动作（Act）
- **ACD**：带描述的控制动作（Act with Description）
- **SEC**：安全控制（Security Control）
- **BCR**：二进制计数器读数（Binary Counter Reading）
- **MV**：测量值（Measured Value）
- **CMV**：复数测量值（Complex Measured Value）
- **SAV**：采样模拟值（Sampled Analog Value）
- **WYE**：WYE测量值（WYE Measured Value）
- **DEL**：DEL测量值（DEL Measured Value）

---

## 7. 约束规则

**规则1（逻辑节点命名规则）**：

```text
LNName = LNClass + LNInstance
LNClass ∈ {XCBR, XSWI, MMXU, PTRC, TCTR, TVTR, ...}
LNInstance ∈ [1, 99]
```

**规则2（数据对象命名规则）**：

```text
DOName = DOClass + DOInstance
DOClass ∈ {Pos, St, Op, Mod, Beh, Health, ...}
DOInstance ∈ String
```

**规则3（数据属性命名规则）**：

```text
DAName = DAClass + DAInstance
DAClass ∈ {stVal, q, t, ctlVal, ...}
DAInstance ∈ String
```

**规则4（服务调用规则）**：

```text
∀ service ∈ Service_Schema:
  service.service_timestamp ≤ CurrentTime
  service.service_result ≠ null → service.service_type ∈ ValidServiceTypes
```

---

## 8. 转换函数

**函数1（SCL到数据库转换）**：

```text
Convert_SCL_to_DB: SCL_Schema → Database_Schema
Convert_SCL_to_DB(scl) = {
  IEDs: map(Convert_IED_to_DB, scl.ied_config.ied_list),
  LogicalNodes: map(Convert_LN_to_DB, Extract_LNs(scl)),
  DataObjects: map(Convert_DO_to_DB, Extract_DOs(scl)),
  Services: map(Convert_Service_to_DB, Extract_Services(scl))
}
```

**函数2（MMS到数据库转换）**：

```text
Convert_MMS_to_DB: MMS_Service → Database_Schema
Convert_MMS_to_DB(mms) = {
  ServiceCall: {
    service_name: mms.service_name,
    service_type: mms.service_type,
    service_timestamp: mms.service_timestamp,
    service_parameters: JSON(mms.service_parameters),
    service_result: JSON(mms.service_result)
  }
}
```

---

## 9. 形式化定理

### 9.1 逻辑节点完整性定理

**定理1（逻辑节点完整性）**：

对于任意逻辑节点LN，如果LN的所有必需数据对象都存在，
则LN是完整的：

```text
∀ ln ∈ Logical_Node_Schema:
  Complete(ln) ↔ ∀ do ∈ RequiredDOs(ln): ∃ do_instance ∈ ln.ln_data.data_objects
```

**证明**：

根据IEC61850标准，逻辑节点的完整性定义为所有
必需数据对象都存在。因此，如果所有必需数据对象
都存在，则逻辑节点是完整的。

### 9.2 数据对象一致性定理

**定理2（数据对象一致性）**：

对于任意数据对象DO，如果DO的所有数据属性都符合
其数据类型定义，则DO是一致的：

```text
∀ do ∈ Data_Object_Schema:
  Consistent(do) ↔ ∀ da ∈ do.do_data.data_attributes:
    Type(da) = ExpectedType(do.do_type, da.da_class)
```

**证明**：

根据IEC61850标准，数据对象的一致性定义为所有
数据属性都符合其数据类型定义。因此，如果所有
数据属性都符合定义，则数据对象是一致的。

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
