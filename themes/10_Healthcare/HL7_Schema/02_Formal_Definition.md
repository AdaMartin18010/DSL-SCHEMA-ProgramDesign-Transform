# HL7 Schema形式化定义

## 📑 目录

- [HL7 Schema形式化定义](#hl7-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. ADT消息Schema](#2-adt消息schema)
  - [3. ORU消息Schema](#3-oru消息schema)
  - [4. ORM消息Schema](#4-orm消息schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)
    - [8.1 消息完整性定理](#81-消息完整性定理)
    - [8.2 段结构一致性定理](#82-段结构一致性定理)

---

## 1. 形式化模型

**定义1（HL7 Schema）**：
HL7 Schema是一个四元组：

```text
HL7_Schema = (Message_Type, Segment_Structure,
              Field_Definition, Encoding_Rules)
```

其中：

- `Message_Type`：HL7消息类型Schema
- `Segment_Structure`：HL7段结构Schema
- `Field_Definition`：HL7字段定义Schema
- `Encoding_Rules`：HL7编码规则Schema

---

## 2. ADT消息Schema

**定义2（ADT消息Schema）**：

```text
ADT_Message_Schema = (MSH_Segment, EVN_Segment,
                     PID_Segment, PV1_Segment)
```

**形式化DSL定义**：

```dsl
schema ADTMessage {
  msh_segment: {
    segment_id: String @value("MSH") @required
    field_separator: String @value("|") @required
    encoding_characters: String @value("^~\\&") @required
    sending_application: String @max_length(180)
    sending_facility: String @max_length(180)
    receiving_application: String @max_length(180)
    receiving_facility: String @max_length(180)
    date_time: DateTime @format("YYYYMMDDHHMMSS") @required
    security: String
    message_type: String @pattern("^ADT\\^[A-Z0-9]{2}\\^ADT_[A-Z0-9]{2}$") @required
    message_control_id: String @max_length(20) @required @unique
    processing_id: Enum { P, D, T } @required
    version_id: String @value("2.5") @required
  } @required

  evn_segment: {
    segment_id: String @value("EVN") @required
    event_type_code: String @max_length(3)
    recorded_date_time: DateTime @format("YYYYMMDDHHMMSS")
    date_time_planned_event: DateTime @format("YYYYMMDDHHMMSS")
    event_reason_code: String @max_length(3)
    operator_id: String @max_length(250)
    event_occurred: DateTime @format("YYYYMMDDHHMMSS")
  }

  pid_segment: {
    segment_id: String @value("PID") @required
    set_id: String @value("1")
    patient_id: String @max_length(20)
    patient_identifier_list: List<Identifier> {
      id: String @max_length(20)
      check_digit: String @max_length(1)
      code_identifying_check_digit: String @max_length(1)
      assigning_authority: String @max_length(227)
      identifier_type_code: String @max_length(5)
      assigning_facility: String @max_length(227)
    }
    alternate_patient_id: String @max_length(20)
    patient_name: String @max_length(250) @required
    mother_maiden_name: String @max_length(250)
    date_time_of_birth: Date @format("YYYYMMDD")
    administrative_sex: Enum { M, F, O, U, A, N }
    patient_alias: String @max_length(250)
    race: String @max_length(250)
    patient_address: String @max_length(250)
    county_code: String @max_length(4)
    phone_number_home: String @max_length(250)
    phone_number_business: String @max_length(250)
    primary_language: String @max_length(250)
    marital_status: String @max_length(1)
    religion: String @max_length(250)
    patient_account_number: String @max_length(20)
    ssn_number: String @max_length(11)
    driver_license_number: String @max_length(25)
    mother_identifier: String @max_length(20)
    ethnic_group: String @max_length(250)
    birth_place: String @max_length(250)
    multiple_birth_indicator: Enum { Y, N }
    birth_order: Integer
    citizenship: String @max_length(250)
    veterans_military_status: String @max_length(250)
    nationality: String @max_length(250)
    patient_death_date_and_time: DateTime @format("YYYYMMDDHHMMSS")
    patient_death_indicator: Enum { Y, N }
    identity_unknown_indicator: Enum { Y, N }
    identity_reliability_code: String @max_length(1)
    last_update_date_time: DateTime @format("YYYYMMDDHHMMSS")
    last_update_facility: String @max_length(227)
    species_code: String @max_length(250)
    breed_code: String @max_length(250)
    strain: String @max_length(250)
    production_class_code: String @max_length(250)
    tribal_citizenship: String @max_length(250)
  } @required

  pv1_segment: {
    segment_id: String @value("PV1") @required
    set_id: String @value("1")
    patient_class: Enum { E, I, O, P, R, B } @required
    assigned_patient_location: String @max_length(12)
    admission_type: String @max_length(2)
    pre_admit_number: String @max_length(20)
    prior_patient_location: String @max_length(12)
    attending_doctor: String @max_length(250)
    referring_doctor: String @max_length(250)
    consulting_doctor: String @max_length(250)
    hospital_service: String @max_length(3)
    temporary_location: String @max_length(12)
    pre_admit_test_indicator: Enum { Y, N }
    re_admission_indicator: String @max_length(2)
    admit_source: String @max_length(6)
    ambulatory_status: String @max_length(2)
    vip_indicator: Enum { Y, N }
    admitting_doctor: String @max_length(250)
    patient_type: String @max_length(2)
    visit_number: String @max_length(20)
    financial_class: String @max_length(50)
    charge_price_indicator: Enum { Y, N }
    courtesy_code: String @max_length(2)
    credit_rating: String @max_length(2)
    contract_code: String @max_length(2)
    contract_effective_date: Date @format("YYYYMMDD")
    contract_amount: Decimal @precision(12,2)
    contract_period: Integer
    interest_code: String @max_length(2)
    transfer_to_bad_debt_code: String @max_length(1)
    transfer_to_bad_debt_date: Date @format("YYYYMMDD")
    bad_debt_agency_code: String @max_length(10)
    bad_debt_transfer_amount: Decimal @precision(12,2)
    bad_debt_recovery_amount: Decimal @precision(12,2)
    delete_account_indicator: Enum { Y, N }
    delete_account_date: Date @format("YYYYMMDD")
    discharge_disposition: String @max_length(3)
    discharged_to_location: String @max_length(47)
    diet_type: String @max_length(250)
    servicing_facility: String @max_length(2)
    bed_status: Enum { C, O, U }
    account_status: String @max_length(50)
    pending_location: String @max_length(12)
    prior_temporary_location: String @max_length(12)
    admit_date_time: DateTime @format("YYYYMMDDHHMMSS")
    discharge_date_time: DateTime @format("YYYYMMDDHHMMSS")
    current_patient_balance: Decimal @precision(12,2)
    total_charges: Decimal @precision(12,2)
    total_adjustments: Decimal @precision(12,2)
    total_payments: Decimal @precision(12,2)
    alternate_visit_id: String @max_length(20)
    visit_indicator: Enum { V, T }
    other_healthcare_provider: String @max_length(250)
  }
} @standard("HL7_v2")
```

---

## 3. ORU消息Schema

**定义3（ORU消息Schema）**：

```text
ORU_Message_Schema = (MSH_Segment, PID_Segment,
                    OBR_Segment, OBX_Segment)
```

**形式化DSL定义**：

```dsl
schema ORUMessage {
  msh_segment: MSH_Segment @required

  pid_segment: PID_Segment @required

  obr_segment: {
    segment_id: String @value("OBR") @required
    set_id: String @required
    placer_order_number: String @max_length(22)
    filler_order_number: String @max_length(22)
    universal_service_identifier: String @max_length(250) @required
    priority: String @max_length(2)
    requested_date_time: DateTime @format("YYYYMMDDHHMMSS")
    observation_date_time: DateTime @format("YYYYMMDDHHMMSS")
    observation_end_date_time: DateTime @format("YYYYMMDDHHMMSS")
    collection_volume: String @max_length(20)
    collector_identifier: String @max_length(250)
    specimen_action_code: Enum { A, G, L, O, P, R, S }
    danger_code: String @max_length(250)
    relevant_clinical_information: String @max_length(300)
    specimen_received_date_time: DateTime @format("YYYYMMDDHHMMSS")
    specimen_source: String @max_length(250)
    ordering_provider: String @max_length(250)
    order_callback_phone_number: String @max_length(250)
    placer_field_1: String @max_length(60)
    placer_field_2: String @max_length(60)
    filler_field_1: String @max_length(60)
    filler_field_2: String @max_length(60)
    results_rpt_status_chng_date_time: DateTime @format("YYYYMMDDHHMMSS")
    charge_to_practice: String @max_length(100)
    diagnostic_serv_sect_id: String @max_length(10)
    result_status: Enum { C, F, I, O, P, R, S, X }
    parent_result: String @max_length(200)
    quantity_timing: String @max_length(200)
    result_copies_to: String @max_length(250)
    parent: String @max_length(200)
    transportation_mode: String @max_length(20)
    reason_for_study: String @max_length(300)
    principal_result_interpreter: String @max_length(250)
    assistant_result_interpreter: String @max_length(250)
    technician: String @max_length(250)
    transcriptionist: String @max_length(250)
    scheduled_date_time: DateTime @format("YYYYMMDDHHMMSS")
    number_of_sample_containers: Integer
    transport_logistics_of_collected_sample: String @max_length(60)
    collector_s_comment: String @max_length(200)
    transport_arrangement_responsibility: String @max_length(60)
    transport_arranged: Enum { I, O }
    escort_required: Enum { R, N }
    planned_patient_transport_comment: String @max_length(200)
    procedure_code: String @max_length(250)
    procedure_code_modifier: String @max_length(250)
    placer_supplemental_service_information: String @max_length(250)
    filler_supplemental_service_information: String @max_length(250)
    medically_necessary_duplicate_procedure_reason: String @max_length(250)
    result_handling: Enum { F, N }
    parent_universal_service_identifier: String @max_length(250)
  } @required

  obx_segment: List<OBX_Segment> {
    segment_id: String @value("OBX") @required
    set_id: String @required
    value_type: Enum { AD, CE, CF, CK, CN, CP, CX, DT, ED, FT, ID, IS, MO, NM, PN, RP, SN, ST, TM, TN, TS, TX, XAD, XCN, XON, XPN, XTN } @required
    observation_identifier: String @max_length(250) @required
    observation_sub_id: String @max_length(20)
    observation_value: String @max_length(65536)
    units: String @max_length(250)
    references_range: String @max_length(60)
    abnormal_flags: Enum { L, H, LL, HH, <, >, N, A, AA, null, S, VS, W, R, I, E, B }
    probability: Decimal @precision(5,2)
    nature_of_abnormal_test: Enum { A, N, R, S }
    observation_result_status: Enum { C, D, F, I, P, R, S, U, W, X } @required
    date_last_observed_normal_values: Date @format("YYYYMMDD")
    user_defined_access_checks: String @max_length(20)
    date_time_of_the_observation: DateTime @format("YYYYMMDDHHMMSS")
    producer_s_id: String @max_length(250)
    responsible_observer: String @max_length(250)
    observation_method: String @max_length(250)
    equipment_instance_identifier: String @max_length(22)
    date_time_of_the_analysis: DateTime @format("YYYYMMDDHHMMSS")
    observation_site: String @max_length(250)
    observation_instance_identifier: String @max_length(22)
    mood_code: Enum { DEF, EVN, EVN.CRT }
    performing_organization_name: String @max_length(250)
    performing_organization_address: String @max_length(250)
    performing_organization_medical_director: String @max_length(250)
    patient_results_release_category: Enum { O, P, R, W }
    root_cause: String @max_length(250)
    local_process_control: String @max_length(250)
  } @required
} @standard("HL7_v2")
```

---

## 4. ORM消息Schema

**定义4（ORM消息Schema）**：

```text
ORM_Message_Schema = (MSH_Segment, PID_Segment,
                     ORC_Segment, OBR_Segment)
```

**形式化DSL定义**：

```dsl
schema ORMMessage {
  msh_segment: MSH_Segment @required

  pid_segment: PID_Segment @required

  orc_segment: {
    segment_id: String @value("ORC") @required
    order_control: Enum { NW, CA, CN, CR, RF, RO, RP, RQ, SA, SN, SR, SS, UA, UC, UD, UF, UH, UM, UN, UR, UX, XO, XX } @required
    placer_order_number: String @max_length(22)
    filler_order_number: String @max_length(22)
    placer_group_number: String @max_length(22)
    order_status: Enum { A, CA, CM, DC, ER, HD, IP, RP, SC }
    response_flag: Enum { D, E, F, N, R }
    quantity_timing: String @max_length(200)
    parent: String @max_length(200)
    date_time_of_transaction: DateTime @format("YYYYMMDDHHMMSS")
    entered_by: String @max_length(250)
    verified_by: String @max_length(250)
    ordering_provider: String @max_length(250)
    enterer_s_location: String @max_length(20)
    call_back_phone_number: String @max_length(250)
    order_effective_date_time: DateTime @format("YYYYMMDDHHMMSS")
    order_control_code_reason: String @max_length(250)
    entering_organization: String @max_length(250)
    entering_device: String @max_length(250)
    action_by: String @max_length(250)
    advanced_beneficiary_notice_code: String @max_length(2)
    ordering_facility_name: String @max_length(250)
    ordering_facility_address: String @max_length(250)
    ordering_facility_phone_number: String @max_length(250)
    ordering_provider_address: String @max_length(250)
    order_status_modifier: String @max_length(250)
    advanced_beneficiary_notice_override_reason: String @max_length(250)
    filler_s_expected_availability_date_time: DateTime @format("YYYYMMDDHHMMSS")
    confidentiality_code: String @max_length(250)
    order_type: String @max_length(250)
    enterer_authorization_mode: String @max_length(250)
    parent_universal_service_identifier: String @max_length(250)
  } @required

  obr_segment: OBR_Segment
} @standard("HL7_v2")
```

---

## 5. 类型系统

**定义5（HL7数据类型）**：

```text
HL7_Data_Type = Message | Segment | Field | Component |
               SubComponent | Encoding_Character
```

**基本类型定义**：

```dsl
type Segment {
  segment_id: String @required
  fields: List<Field>
}

type Field {
  field_id: String
  components: List<Component>
  value: String
}

type Component {
  sub_components: List<SubComponent>
  value: String
}
```

---

## 6. 约束规则

**约束1（HL7消息完整性）**：

```text
∀ message ∈ HL7_Message:
  message.msh_segment ≠ ∅
  ∧ message.msh_segment.message_control_id ≠ ∅
  ∧ validate_segments(message.segments)
```

**约束2（ADT消息有效性）**：

```text
∀ adt ∈ ADT_Message:
  adt.msh_segment.message_type = "ADT^A08^ADT_A01"
  ∧ adt.pid_segment ≠ ∅
  ∧ adt.pid_segment.patient_name ≠ ∅
```

**约束3（ORU消息有效性）**：

```text
∀ oru ∈ ORU_Message:
  oru.msh_segment.message_type = "ORU^R01"
  ∧ oru.pid_segment ≠ ∅
  ∧ oru.obr_segment ≠ ∅
  ∧ oru.obx_segment ≠ ∅
```

---

## 7. 转换函数

**函数1（HL7到FHIR转换）**：

```text
convert_HL7_ADT_to_FHIR_Patient: HL7_ADT → FHIR_Patient
```

**函数2（FHIR到HL7转换）**：

```text
convert_FHIR_Patient_to_HL7_ADT: FHIR_Patient → HL7_ADT
```

**函数3（消息验证）**：

```text
validate_hl7_message: HL7_Message → Bool
```

---

## 8. 形式化定理

### 8.1 消息完整性定理

**定理1（HL7消息完整性）**：

```text
∀ message ∈ HL7_Message:
  validate_hl7_message(message)
  → message_integrity(message)
  ∧ segment_consistency(message)
```

### 8.2 段结构一致性定理

**定理2（段结构一致性）**：

```text
∀ segment ∈ HL7_Segment:
  validate_segment_structure(segment)
  → segment_structure_consistency(segment)
  ∧ field_consistency(segment.fields)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
