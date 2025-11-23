# FHIR Schema形式化定义

## 📑 目录

- [FHIR Schema形式化定义](#fhir-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. Patient资源Schema](#2-patient资源schema)
  - [3. Condition资源Schema](#3-condition资源schema)
  - [4. Observation资源Schema](#4-observation资源schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)
    - [8.1 资源完整性定理](#81-资源完整性定理)
    - [8.2 API一致性定理](#82-api一致性定理)

---

## 1. 形式化模型

**定义1（FHIR Schema）**：
FHIR Schema是一个四元组：

```text
FHIR_Schema = (Resource_Definition, RESTful_API,
              JSON_XML_Format, Extension_Mechanism)
```

其中：

- `Resource_Definition`：FHIR资源定义Schema
- `RESTful_API`：RESTful API接口Schema
- `JSON_XML_Format`：JSON/XML格式Schema
- `Extension_Mechanism`：扩展机制Schema

---

## 2. Patient资源Schema

**定义2（Patient资源Schema）**：

```text
Patient_Resource_Schema = (Identifier, Name, Gender,
                          BirthDate, Telecom, Address, Contact)
```

**形式化DSL定义**：

```dsl
schema Patient {
  resourceType: String @value("Patient") @required

  id: String @pattern("^[A-Za-z0-9\\-]{1,64}$")
  meta: Meta {
    versionId: String
    lastUpdated: DateTime
    profile: List<String>
  }

  identifier: List<Identifier> {
    use: Enum { usual, official, temp, secondary }
    type: CodeableConcept {
      coding: List<Coding> {
        system: String
        code: String
        display: String
      }
    }
    system: String @required
    value: String @required
    period: Period {
      start: DateTime
      end: DateTime
    }
  }

  active: Boolean @default(true)

  name: List<HumanName> {
    use: Enum { usual, official, temp, nickname, anonymous, old, maiden }
    family: String
    given: List<String>
    prefix: List<String>
    suffix: List<String>
    period: Period
  }

  telecom: List<ContactPoint> {
    system: Enum { phone, fax, email, pager, url, sms, other }
    value: String
    use: Enum { home, work, temp, old, mobile }
    rank: Integer
    period: Period
  }

  gender: Enum { male, female, other, unknown }

  birthDate: Date @format("YYYY-MM-DD")

  address: List<Address> {
    use: Enum { home, work, temp, old, billing }
    type: Enum { postal, physical, both }
    text: String
    line: List<String>
    city: String
    district: String
    state: String
    postalCode: String
    country: String
    period: Period
  }

  maritalStatus: CodeableConcept

  contact: List<PatientContact> {
    relationship: List<CodeableConcept>
    name: HumanName
    telecom: List<ContactPoint>
    address: Address
    gender: Enum { male, female, other, unknown }
    organization: Reference
    period: Period
  }
} @standard("FHIR_R4")
```

---

## 3. Condition资源Schema

**定义3（Condition资源Schema）**：

```text
Condition_Resource_Schema = (Code, OnsetDateTime, Severity,
                            ClinicalStatus, VerificationStatus)
```

**形式化DSL定义**：

```dsl
schema Condition {
  resourceType: String @value("Condition") @required

  id: String @pattern("^[A-Za-z0-9\\-]{1,64}$")

  identifier: List<Identifier>

  clinicalStatus: CodeableConcept {
    coding: List<Coding> {
      system: String @value("http://terminology.hl7.org/CodeSystem/condition-clinical")
      code: Enum { active, recurrence, relapse, inactive, remission, resolved }
    }
  }

  verificationStatus: CodeableConcept {
    coding: List<Coding> {
      system: String @value("http://terminology.hl7.org/CodeSystem/condition-ver-status")
      code: Enum { unconfirmed, provisional, differential, confirmed, refuted, entered-in-error }
    }
  }

  category: List<CodeableConcept>

  severity: CodeableConcept {
    coding: List<Coding> {
      system: String
      code: Enum { mild, moderate, severe }
    }
  }

  code: CodeableConcept {
    coding: List<Coding> {
      system: String @pattern("^http://.*$")
      code: String @required
      display: String
    }
    text: String
  } @required

  bodySite: List<CodeableConcept>

  subject: Reference {
    reference: String @pattern("^Patient/[A-Za-z0-9\\-]+$")
  } @required

  encounter: Reference {
    reference: String @pattern("^Encounter/[A-Za-z0-9\\-]+$")
  }

  onsetDateTime: DateTime
  onsetAge: Age
  onsetPeriod: Period
  onsetRange: Range
  onsetString: String

  abatementDateTime: DateTime
  abatementAge: Age
  abatementPeriod: Period
  abatementRange: Range
  abatementString: String

  recordedDate: DateTime

  recorder: Reference {
    reference: String @pattern("^Practitioner/[A-Za-z0-9\\-]+$")
  }

  asserter: Reference {
    reference: String @pattern("^Practitioner/[A-Za-z0-9\\-]+$")
  }
} @standard("FHIR_R4")
```

---

## 4. Observation资源Schema

**定义4（Observation资源Schema）**：

```text
Observation_Resource_Schema = (Code, Value, EffectiveDateTime,
                              Status, Unit, ReferenceRange)
```

**形式化DSL定义**：

```dsl
schema Observation {
  resourceType: String @value("Observation") @required

  id: String @pattern("^[A-Za-z0-9\\-]{1,64}$")

  identifier: List<Identifier>

  status: Enum {
    registered, preliminary, final, amended,
    corrected, cancelled, entered-in-error, unknown
  } @required

  category: List<CodeableConcept> {
    coding: List<Coding> {
      system: String @value("http://terminology.hl7.org/CodeSystem/observation-category")
      code: Enum { vital-signs, imaging, laboratory, procedure, survey, exam, therapy }
    }
  }

  code: CodeableConcept {
    coding: List<Coding> {
      system: String @required
      code: String @required
      display: String
    }
    text: String
  } @required

  subject: Reference {
    reference: String @pattern("^Patient/[A-Za-z0-9\\-]+$")
  } @required

  encounter: Reference {
    reference: String @pattern("^Encounter/[A-Za-z0-9\\-]+$")
  }

  effectiveDateTime: DateTime
  effectivePeriod: Period
  effectiveTiming: Timing
  effectiveInstant: Instant

  issued: Instant

  performer: List<Reference> {
    reference: String @pattern("^(Practitioner|PractitionerRole|Organization|CareTeam|Patient|RelatedPerson)/[A-Za-z0-9\\-]+$")
  }

  valueQuantity: Quantity {
    value: Decimal
    unit: String
    system: String @pattern("^http://.*$")
    code: String
  }

  valueCodeableConcept: CodeableConcept

  valueString: String

  valueBoolean: Boolean

  valueInteger: Integer

  valueRange: Range {
    low: Quantity
    high: Quantity
  }

  valueRatio: Ratio {
    numerator: Quantity
    denominator: Quantity
  }

  valueSampledData: SampledData {
    origin: Quantity @required
    period: Decimal @required
    factor: Decimal
    lowerLimit: Decimal
    upperLimit: Decimal
    dimensions: Integer @required
    data: String
  }

  valueTime: Time

  valueDateTime: DateTime

  valuePeriod: Period

  dataAbsentReason: CodeableConcept

  interpretation: List<CodeableConcept>

  note: List<Annotation> {
    authorReference: Reference
    authorString: String
    time: DateTime
    text: String @required
  }

  bodySite: CodeableConcept

  method: CodeableConcept

  specimen: Reference {
    reference: String @pattern("^Specimen/[A-Za-z0-9\\-]+$")
  }

  device: Reference {
    reference: String @pattern("^(Device|DeviceMetric)/[A-Za-z0-9\\-]+$")
  }

  referenceRange: List<ObservationReferenceRange> {
    low: Quantity
    high: Quantity
    type: CodeableConcept
    appliesTo: List<CodeableConcept>
    age: Range
    text: String
  }

  hasMember: List<Reference> {
    reference: String @pattern("^Observation/[A-Za-z0-9\\-]+$")
  }

  component: List<ObservationComponent> {
    code: CodeableConcept @required
    valueQuantity: Quantity
    valueCodeableConcept: CodeableConcept
    valueString: String
    valueBoolean: Boolean
    valueInteger: Integer
    valueRange: Range
    valueRatio: Ratio
    valueSampledData: SampledData
    valueTime: Time
    valueDateTime: DateTime
    valuePeriod: Period
    dataAbsentReason: CodeableConcept
    interpretation: List<CodeableConcept>
    referenceRange: List<ObservationReferenceRange>
  }
} @standard("FHIR_R4")
```

---

## 5. 类型系统

**定义5（FHIR数据类型）**：

```text
FHIR_Data_Type = Resource | Identifier | CodeableConcept |
                Reference | Quantity | Period | Range |
                HumanName | Address | ContactPoint
```

**基本类型定义**：

```dsl
type Identifier {
  use: Enum { usual, official, temp, secondary }
  type: CodeableConcept
  system: String @required
  value: String @required
  period: Period
}

type CodeableConcept {
  coding: List<Coding>
  text: String
}

type Reference {
  reference: String @pattern("^[A-Z][A-Za-z]*/[A-Za-z0-9\\-]+$")
  type: String
  identifier: Identifier
  display: String
}

type Quantity {
  value: Decimal
  unit: String
  system: String @pattern("^http://.*$")
  code: String
}
```

---

## 6. 约束规则

**约束1（Patient资源完整性）**：

```text
∀ patient ∈ Patient:
  patient.resourceType = "Patient"
  ∧ (patient.name ≠ ∅ ∨ patient.identifier ≠ ∅)
  ∧ validate_identifier(patient.identifier)
```

**约束2（Condition资源有效性）**：

```text
∀ condition ∈ Condition:
  condition.resourceType = "Condition"
  ∧ condition.code ≠ ∅
  ∧ condition.subject ≠ ∅
  ∧ condition.clinicalStatus ≠ ∅
```

**约束3（Observation资源有效性）**：

```text
∀ observation ∈ Observation:
  observation.resourceType = "Observation"
  ∧ observation.status ∈ {registered, preliminary, final, ...}
  ∧ observation.code ≠ ∅
  ∧ observation.subject ≠ ∅
  ∧ (observation.valueQuantity ≠ ∅ ∨ observation.valueCodeableConcept ≠ ∅)
```

---

## 7. 转换函数

**函数1（FHIR到HL7转换）**：

```text
convert_FHIR_Patient_to_HL7: FHIR_Patient → HL7_ADT
```

**函数2（HL7到FHIR转换）**：

```text
convert_HL7_to_FHIR_Patient: HL7_ADT → FHIR_Patient
```

**函数3（资源验证）**：

```text
validate_fhir_resource: FHIR_Resource → Bool
```

---

## 8. 形式化定理

### 8.1 资源完整性定理

**定理1（FHIR资源完整性）**：

```text
∀ resource ∈ FHIR_Resource:
  validate_fhir_resource(resource)
  → resource_integrity(resource)
  ∧ referential_integrity(resource)
```

### 8.2 API一致性定理

**定理2（RESTful API一致性）**：

```text
∀ api_call ∈ RESTful_API:
  validate_api_request(api_call)
  → api_consistency(api_call)
  ∧ resource_consistency(api_call.response)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
