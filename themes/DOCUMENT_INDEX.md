# 文档索引

## 📑 目录

- [文档索引](#文档索引)
  - [📑 目录](#-目录)
  - [1. 按主题索引](#1-按主题索引)
    - [1.1 工业自动化（01\_Industrial\_Automation）](#11-工业自动化01_industrial_automation)
      - [PLC Schema](#plc-schema)
      - [CAN Schema](#can-schema)
      - [跨主题文档](#跨主题文档)
    - [1.2 物联网Schema（02\_IoT\_Schema）](#12-物联网schema02_iot_schema)
      - [传感器Schema](#传感器schema)
      - [通信Schema](#通信schema)
      - [控制Schema](#控制schema)
      - [安全Schema](#安全schema)
      - [消息队列Schema](#消息队列schema)
      - [可观测性Schema](#可观测性schema)
      - [跨主题文档](#跨主题文档-1)
    - [1.3 物理设备Schema（03\_Physical\_Device）](#13-物理设备schema03_physical_device)
      - [电气Schema](#电气schema)
      - [机械Schema](#机械schema)
      - [CAD Schema](#cad-schema)
      - [热学Schema](#热学schema)
      - [安全Schema](#安全schema-1)
      - [数字孪生](#数字孪生)
      - [跨主题文档](#跨主题文档-2)
    - [1.4 编程语言转换（04\_Programming\_Conversion）](#14-编程语言转换04_programming_conversion)
      - [形式化模型](#形式化模型)
      - [语言映射](#语言映射)
      - [代码生成](#代码生成)
      - [数据库Schema](#数据库schema)
      - [序列化Schema](#序列化schema)
      - [跨主题文档](#跨主题文档-3)
    - [1.5 DSL转换理论（05\_DSL\_Theory）](#15-dsl转换理论05_dsl_theory)
      - [信息论分析](#信息论分析)
      - [形式语言理论](#形式语言理论)
      - [知识图谱](#知识图谱)
      - [跨主题文档](#跨主题文档-4)
    - [1.6 金融服务Schema（06\_Financial\_Services）](#16-金融服务schema06_financial_services)
      - [SWIFT Schema](#swift-schema)
      - [ISO 20022 Schema](#iso-20022-schema)
      - [Payment Schema](#payment-schema)
    - [1.7 物流与供应链Schema（07\_Logistics\_Supply\_Chain）](#17-物流与供应链schema07_logistics_supply_chain)
      - [GS1 Schema](#gs1-schema)
      - [EDI Schema](#edi-schema)
    - [1.8 智慧城市Schema（08\_Smart\_City）](#18-智慧城市schema08_smart_city)
      - [Smart City Schema](#smart-city-schema)
    - [1.9 工作流与BPM Schema（14\_Workflow\_BPM）](#19-工作流与bpm-schema14_workflow_bpm)
      - [BPMN Schema](#bpmn-schema)
      - [BPEL Schema](#bpel-schema)
      - [Workflow Engine Schema](#workflow-engine-schema)
    - [1.9 医疗Schema（10\_Healthcare）](#19-医疗schema10_healthcare)
      - [Healthcare Schema](#healthcare-schema)
      - [FHIR Schema](#fhir-schema)
      - [HL7 Schema](#hl7-schema)
    - [1.10 食品行业Schema（11\_Food\_Industry）](#110-食品行业schema11_food_industry)
      - [Food Industry Schema](#food-industry-schema)
    - [1.11 智慧家居Schema（12\_Smart\_Home）](#111-智慧家居schema12_smart_home)
      - [Smart Home Schema](#smart-home-schema)
      - [Matter Schema](#matter-schema)
      - [Thread Schema](#thread-schema)
    - [1.12 办公自动化Schema（13\_OA\_Office\_Automation）](#112-办公自动化schema13_oa_office_automation)
      - [OA Schema](#oa-schema)
    - [1.13 工作流与BPM Schema（14\_Workflow\_BPM）](#113-工作流与bpm-schema14_workflow_bpm)
      - [BPMN Schema](#bpmn-schema-1)
      - [BPEL Schema](#bpel-schema-1)
      - [Workflow Engine Schema](#workflow-engine-schema-1)
    - [1.14 ERP系统Schema（15\_ERP\_Systems）](#114-erp系统schema15_erp_systems)
      - [ERP Schema](#erp-schema)
    - [1.15 海运与航运Schema（08\_Maritime\_Shipping）](#115-海运与航运schema08_maritime_shipping)
      - [Maritime Schema](#maritime-schema)
    - [1.29 API和协议Schema（29\_API\_Protocol\_Schemas）⭐新增](#129-api和协议schema29_api_protocol_schemas新增)
      - [GraphQL Schema](#graphql-schema)
      - [gRPC Schema](#grpc-schema)
      - [Protocol Buffers Schema](#protocol-buffers-schema)
      - [Avro Schema](#avro-schema)
      - [JSON Schema](#json-schema)
      - [AsyncAPI Schema](#asyncapi-schema)
  - [2. 按文档类型索引](#2-按文档类型索引)
    - [2.1 概述文档（01\_Overview.md）](#21-概述文档01_overviewmd)
    - [2.2 形式化定义（02\_Formal\_Definition.md）](#22-形式化定义02_formal_definitionmd)
    - [2.3 标准对标（03\_Standards.md）](#23-标准对标03_standardsmd)
    - [2.4 转换体系（04\_Transformation.md）](#24-转换体系04_transformationmd)
    - [2.5 实践案例（05\_Case\_Studies.md）](#25-实践案例05_case_studiesmd)
  - [3. 按标准索引](#3-按标准索引)
    - [3.1 IEC标准](#31-iec标准)
    - [3.2 ISO标准](#32-iso标准)
    - [3.3 W3C标准](#33-w3c标准)
    - [3.4 国家标准](#34-国家标准)
  - [4. 按应用场景索引](#4-按应用场景索引)
    - [4.1 工业自动化场景](#41-工业自动化场景)
    - [4.2 物联网场景](#42-物联网场景)
    - [4.3 数字孪生场景](#43-数字孪生场景)
    - [4.4 代码生成场景](#44-代码生成场景)
  - [5. 跨主题关联](#5-跨主题关联)
    - [5.1 相关主题链接](#51-相关主题链接)
    - [5.2 标准关联](#52-标准关联)

---

## 1. 按主题索引

### 1.1 工业自动化（01_Industrial_Automation）

#### PLC Schema

- [概述](./01_Industrial_Automation/PLC_Schema/01_Overview.md)
- [形式化定义](./01_Industrial_Automation/PLC_Schema/02_Formal_Definition.md)
- [标准对标](./01_Industrial_Automation/PLC_Schema/03_Standards.md)
- [转换体系](./01_Industrial_Automation/PLC_Schema/04_Transformation.md)
- [实践案例](./01_Industrial_Automation/PLC_Schema/05_Case_Studies.md)

#### CAN Schema

- [概述](./01_Industrial_Automation/CAN_Schema/01_Overview.md)
- [形式化定义](./01_Industrial_Automation/CAN_Schema/02_Formal_Definition.md)
- [标准对标](./01_Industrial_Automation/CAN_Schema/03_Standards.md)
- [转换体系](./01_Industrial_Automation/CAN_Schema/04_Transformation.md)
- [实践案例](./01_Industrial_Automation/CAN_Schema/05_Case_Studies.md)

#### 跨主题文档

- [思维导图](./01_Industrial_Automation/Mind_Map.md)
- [知识矩阵](./01_Industrial_Automation/Knowledge_Matrix.md)
- [形式化证明](./01_Industrial_Automation/Formal_Proofs.md)

### 1.2 物联网Schema（02_IoT_Schema）

#### 传感器Schema

- [概述](./02_IoT_Schema/Sensor_Schema/01_Overview.md)
- [形式化定义](./02_IoT_Schema/Sensor_Schema/02_Formal_Definition.md)
- [标准对标](./02_IoT_Schema/Sensor_Schema/03_Standards.md)
- [转换体系](./02_IoT_Schema/Sensor_Schema/04_Transformation.md)
- [实践案例](./02_IoT_Schema/Sensor_Schema/05_Case_Studies.md)

#### 通信Schema

- [概述](./02_IoT_Schema/Communication_Schema/01_Overview.md)
- [形式化定义](./02_IoT_Schema/Communication_Schema/02_Formal_Definition.md)
- [标准对标](./02_IoT_Schema/Communication_Schema/03_Standards.md)
- [转换体系](./02_IoT_Schema/Communication_Schema/04_Transformation.md)
- [实践案例](./02_IoT_Schema/Communication_Schema/05_Case_Studies.md)

#### 控制Schema

- [概述](./02_IoT_Schema/Control_Schema/01_Overview.md)
- [形式化定义](./02_IoT_Schema/Control_Schema/02_Formal_Definition.md)
- [标准对标](./02_IoT_Schema/Control_Schema/03_Standards.md)
- [转换体系](./02_IoT_Schema/Control_Schema/04_Transformation.md)
- [实践案例](./02_IoT_Schema/Control_Schema/05_Case_Studies.md)

#### 安全Schema

- [概述](./02_IoT_Schema/Security_Schema/01_Overview.md)
- [形式化定义](./02_IoT_Schema/Security_Schema/02_Formal_Definition.md)
- [标准对标](./02_IoT_Schema/Security_Schema/03_Standards.md)
- [转换体系](./02_IoT_Schema/Security_Schema/04_Transformation.md)
- [实践案例](./02_IoT_Schema/Security_Schema/05_Case_Studies.md)

#### 消息队列Schema

- [概述](./02_IoT_Schema/Message_Queue_Schema/01_Overview.md)
- [形式化定义](./02_IoT_Schema/Message_Queue_Schema/02_Formal_Definition.md)
- [标准对标](./02_IoT_Schema/Message_Queue_Schema/03_Standards.md)
- [转换体系](./02_IoT_Schema/Message_Queue_Schema/04_Transformation.md)
- [实践案例](./02_IoT_Schema/Message_Queue_Schema/05_Case_Studies.md)

#### 可观测性Schema

- [概述](./02_IoT_Schema/Observability_Schema/01_Overview.md)
- [形式化定义](./02_IoT_Schema/Observability_Schema/02_Formal_Definition.md)
- [标准对标](./02_IoT_Schema/Observability_Schema/03_Standards.md)
- [转换体系](./02_IoT_Schema/Observability_Schema/04_Transformation.md)
- [实践案例](./02_IoT_Schema/Observability_Schema/05_Case_Studies.md)

#### 跨主题文档

- [思维导图](./02_IoT_Schema/Mind_Map.md)
- [知识矩阵](./02_IoT_Schema/Knowledge_Matrix.md)
- [形式化证明](./02_IoT_Schema/Formal_Proofs.md)

### 1.3 物理设备Schema（03_Physical_Device）

#### 电气Schema

- [概述](./03_Physical_Device/Electrical_Schema/01_Overview.md)
- [形式化定义](./03_Physical_Device/Electrical_Schema/02_Formal_Definition.md)
- [标准对标](./03_Physical_Device/Electrical_Schema/03_Standards.md)
- [转换体系](./03_Physical_Device/Electrical_Schema/04_Transformation.md)
- [实践案例](./03_Physical_Device/Electrical_Schema/05_Case_Studies.md)

#### 机械Schema

- [概述](./03_Physical_Device/Mechanical_Schema/01_Overview.md)
- [形式化定义](./03_Physical_Device/Mechanical_Schema/02_Formal_Definition.md)
- [标准对标](./03_Physical_Device/Mechanical_Schema/03_Standards.md)
- [转换体系](./03_Physical_Device/Mechanical_Schema/04_Transformation.md)
- [实践案例](./03_Physical_Device/Mechanical_Schema/05_Case_Studies.md)

#### CAD Schema

- [概述](./03_Physical_Device/CAD_Schema/01_Overview.md)
- [形式化定义](./03_Physical_Device/CAD_Schema/02_Formal_Definition.md)
- [标准对标](./03_Physical_Device/CAD_Schema/03_Standards.md)
- [转换体系](./03_Physical_Device/CAD_Schema/04_Transformation.md)
- [实践案例](./03_Physical_Device/CAD_Schema/05_Case_Studies.md)

#### 热学Schema

- [概述](./03_Physical_Device/Thermal_Schema/01_Overview.md)
- [形式化定义](./03_Physical_Device/Thermal_Schema/02_Formal_Definition.md)
- [标准对标](./03_Physical_Device/Thermal_Schema/03_Standards.md)
- [转换体系](./03_Physical_Device/Thermal_Schema/04_Transformation.md)
- [实践案例](./03_Physical_Device/Thermal_Schema/05_Case_Studies.md)

#### 安全Schema

- [概述](./03_Physical_Device/Safety_Schema/01_Overview.md)
- [形式化定义](./03_Physical_Device/Safety_Schema/02_Formal_Definition.md)
- [标准对标](./03_Physical_Device/Safety_Schema/03_Standards.md)
- [转换体系](./03_Physical_Device/Safety_Schema/04_Transformation.md)
- [实践案例](./03_Physical_Device/Safety_Schema/05_Case_Studies.md)

#### 数字孪生

- [README](./03_Physical_Device/Digital_Twin/README.md)
- [概述](./03_Physical_Device/Digital_Twin/01_Overview.md)
- [形式化定义](./03_Physical_Device/Digital_Twin/02_Formal_Definition.md)
- [标准对标](./03_Physical_Device/Digital_Twin/03_Standards.md)
- [转换体系](./03_Physical_Device/Digital_Twin/04_Transformation.md)
- [实践案例](./03_Physical_Device/Digital_Twin/05_Case_Studies.md)

#### 跨主题文档

- [思维导图](./03_Physical_Device/Mind_Map.md)
- [知识矩阵](./03_Physical_Device/Knowledge_Matrix.md)
- [形式化证明](./03_Physical_Device/Formal_Proofs.md)

### 1.4 编程语言转换（04_Programming_Conversion）

#### 形式化模型

- [概述](./04_Programming_Conversion/Formal_Model/01_Overview.md)
- [形式化定义](./04_Programming_Conversion/Formal_Model/02_Formal_Definition.md)
- [标准对标](./04_Programming_Conversion/Formal_Model/03_Standards.md)
- [转换体系](./04_Programming_Conversion/Formal_Model/04_Transformation.md)
- [实践案例](./04_Programming_Conversion/Formal_Model/05_Case_Studies.md)

#### 语言映射

- [概述](./04_Programming_Conversion/Language_Mapping/01_Overview.md)
- [形式化定义](./04_Programming_Conversion/Language_Mapping/02_Formal_Definition.md)
- [标准对标](./04_Programming_Conversion/Language_Mapping/03_Standards.md)
- [转换体系](./04_Programming_Conversion/Language_Mapping/04_Transformation.md)
- [实践案例](./04_Programming_Conversion/Language_Mapping/05_Case_Studies.md)

#### 代码生成

- [概述](./04_Programming_Conversion/Code_Generation/01_Overview.md)
- [形式化定义](./04_Programming_Conversion/Code_Generation/02_Formal_Definition.md)
- [标准对标](./04_Programming_Conversion/Code_Generation/03_Standards.md)
- [转换体系](./04_Programming_Conversion/Code_Generation/04_Transformation.md)
- [实践案例](./04_Programming_Conversion/Code_Generation/05_Case_Studies.md)

#### 数据库Schema

- [概述](./04_Programming_Conversion/Database_Schema/01_Overview.md)
- [形式化定义](./04_Programming_Conversion/Database_Schema/02_Formal_Definition.md)
- [标准对标](./04_Programming_Conversion/Database_Schema/03_Standards.md)
- [转换体系](./04_Programming_Conversion/Database_Schema/04_Transformation.md)
- [实践案例](./04_Programming_Conversion/Database_Schema/05_Case_Studies.md)

#### 序列化Schema

- [概述](./04_Programming_Conversion/Serialization_Schema/01_Overview.md)
- [形式化定义](./04_Programming_Conversion/Serialization_Schema/02_Formal_Definition.md)
- [标准对标](./04_Programming_Conversion/Serialization_Schema/03_Standards.md)
- [转换体系](./04_Programming_Conversion/Serialization_Schema/04_Transformation.md)
- [实践案例](./04_Programming_Conversion/Serialization_Schema/05_Case_Studies.md)

#### 跨主题文档

- [思维导图](./04_Programming_Conversion/Mind_Map.md)
- [知识矩阵](./04_Programming_Conversion/Knowledge_Matrix.md)
- [形式化证明](./04_Programming_Conversion/Formal_Proofs.md)

### 1.5 DSL转换理论（05_DSL_Theory）

#### 信息论分析

- [概述](./05_DSL_Theory/Information_Theory/01_Overview.md)
- [形式化定义](./05_DSL_Theory/Information_Theory/02_Formal_Definition.md)
- [标准对标](./05_DSL_Theory/Information_Theory/03_Standards.md)
- [转换体系](./05_DSL_Theory/Information_Theory/04_Transformation.md)
- [实践案例](./05_DSL_Theory/Information_Theory/05_Case_Studies.md)

#### 形式语言理论

- [概述](./05_DSL_Theory/Formal_Language_Theory/01_Overview.md)
- [形式化定义](./05_DSL_Theory/Formal_Language_Theory/02_Formal_Definition.md)
- [标准对标](./05_DSL_Theory/Formal_Language_Theory/03_Standards.md)
- [转换体系](./05_DSL_Theory/Formal_Language_Theory/04_Transformation.md)
- [实践案例](./05_DSL_Theory/Formal_Language_Theory/05_Case_Studies.md)

#### 知识图谱

- [README](./05_DSL_Theory/Knowledge_Graph/README.md)
- [概述](./05_DSL_Theory/Knowledge_Graph/01_Overview.md)
- [形式化定义](./05_DSL_Theory/Knowledge_Graph/02_Formal_Definition.md)
- [标准对标](./05_DSL_Theory/Knowledge_Graph/03_Standards.md)
- [转换体系](./05_DSL_Theory/Knowledge_Graph/04_Transformation.md)
- [实践案例](./05_DSL_Theory/Knowledge_Graph/05_Case_Studies.md)

#### 跨主题文档

- [思维导图](./05_DSL_Theory/Mind_Map.md)
- [知识矩阵](./05_DSL_Theory/Knowledge_Matrix.md)
- [形式化证明](./05_DSL_Theory/Formal_Proofs.md)

### 1.6 金融服务Schema（06_Financial_Services）

#### SWIFT Schema

- [概述](./06_Financial_Services/SWIFT_Schema/01_Overview.md)
- [形式化定义](./06_Financial_Services/SWIFT_Schema/02_Formal_Definition.md)
- [标准对标](./06_Financial_Services/SWIFT_Schema/03_Standards.md)
- [转换体系](./06_Financial_Services/SWIFT_Schema/04_Transformation.md)
- [实践案例](./06_Financial_Services/SWIFT_Schema/05_Case_Studies.md)

#### ISO 20022 Schema

- [概述](./06_Financial_Services/ISO20022_Schema/01_Overview.md)
- [形式化定义](./06_Financial_Services/ISO20022_Schema/02_Formal_Definition.md)
- [标准对标](./06_Financial_Services/ISO20022_Schema/03_Standards.md)
- [转换体系](./06_Financial_Services/ISO20022_Schema/04_Transformation.md)
- [实践案例](./06_Financial_Services/ISO20022_Schema/05_Case_Studies.md)

#### Payment Schema

- [概述](./06_Financial_Services/Payment_Schema/01_Overview.md)
- [形式化定义](./06_Financial_Services/Payment_Schema/02_Formal_Definition.md)
- [标准对标](./06_Financial_Services/Payment_Schema/03_Standards.md)
- [转换体系](./06_Financial_Services/Payment_Schema/04_Transformation.md)
- [实践案例](./06_Financial_Services/Payment_Schema/05_Case_Studies.md)

### 1.7 物流与供应链Schema（07_Logistics_Supply_Chain）

#### GS1 Schema

- [概述](./07_Logistics_Supply_Chain/GS1_Schema/01_Overview.md)
- [形式化定义](./07_Logistics_Supply_Chain/GS1_Schema/02_Formal_Definition.md)
- [标准对标](./07_Logistics_Supply_Chain/GS1_Schema/03_Standards.md)
- [转换体系](./07_Logistics_Supply_Chain/GS1_Schema/04_Transformation.md)
- [实践案例](./07_Logistics_Supply_Chain/GS1_Schema/05_Case_Studies.md)

#### EDI Schema

- [概述](./07_Logistics_Supply_Chain/EDI_Schema/01_Overview.md)
- [形式化定义](./07_Logistics_Supply_Chain/EDI_Schema/02_Formal_Definition.md)
- [标准对标](./07_Logistics_Supply_Chain/EDI_Schema/03_Standards.md)
- [转换体系](./07_Logistics_Supply_Chain/EDI_Schema/04_Transformation.md)
- [实践案例](./07_Logistics_Supply_Chain/EDI_Schema/05_Case_Studies.md)

### 1.8 智慧城市Schema（08_Smart_City）

#### Smart City Schema

- [概述](./08_Smart_City/Smart_City_Schema/01_Overview.md)
- [形式化定义](./08_Smart_City/Smart_City_Schema/02_Formal_Definition.md)
- [标准对标](./08_Smart_City/Smart_City_Schema/03_Standards.md)
- [转换体系](./08_Smart_City/Smart_City_Schema/04_Transformation.md)
- [实践案例](./08_Smart_City/Smart_City_Schema/05_Case_Studies.md)

### 1.9 工作流与BPM Schema（14_Workflow_BPM）

#### BPMN Schema

- [概述](./14_Workflow_BPM/BPMN_Schema/01_Overview.md)
- [形式化定义](./14_Workflow_BPM/BPMN_Schema/02_Formal_Definition.md)
- [标准对标](./14_Workflow_BPM/BPMN_Schema/03_Standards.md)
- [转换体系](./14_Workflow_BPM/BPMN_Schema/04_Transformation.md)
- [实践案例](./14_Workflow_BPM/BPMN_Schema/05_Case_Studies.md)

#### BPEL Schema

- [概述](./14_Workflow_BPM/BPEL_Schema/01_Overview.md)
- [形式化定义](./14_Workflow_BPM/BPEL_Schema/02_Formal_Definition.md)
- [标准对标](./14_Workflow_BPM/BPEL_Schema/03_Standards.md)
- [转换体系](./14_Workflow_BPM/BPEL_Schema/04_Transformation.md)
- [实践案例](./14_Workflow_BPM/BPEL_Schema/05_Case_Studies.md)

#### Workflow Engine Schema

- [概述](./14_Workflow_BPM/Workflow_Engine_Schema/01_Overview.md)
- [形式化定义](./14_Workflow_BPM/Workflow_Engine_Schema/02_Formal_Definition.md)
- [标准对标](./14_Workflow_BPM/Workflow_Engine_Schema/03_Standards.md)
- [转换体系](./14_Workflow_BPM/Workflow_Engine_Schema/04_Transformation.md)
- [实践案例](./14_Workflow_BPM/Workflow_Engine_Schema/05_Case_Studies.md)

### 1.9 医疗Schema（10_Healthcare）

#### Healthcare Schema

- [概述](./10_Healthcare/Healthcare_Schema/01_Overview.md)
- [形式化定义](./10_Healthcare/Healthcare_Schema/02_Formal_Definition.md)
- [标准对标](./10_Healthcare/Healthcare_Schema/03_Standards.md)
- [转换体系](./10_Healthcare/Healthcare_Schema/04_Transformation.md)
- [实践案例](./10_Healthcare/Healthcare_Schema/05_Case_Studies.md)

#### FHIR Schema

- [概述](./10_Healthcare/FHIR_Schema/01_Overview.md)
- [形式化定义](./10_Healthcare/FHIR_Schema/02_Formal_Definition.md)
- [标准对标](./10_Healthcare/FHIR_Schema/03_Standards.md)
- [转换体系](./10_Healthcare/FHIR_Schema/04_Transformation.md)
- [实践案例](./10_Healthcare/FHIR_Schema/05_Case_Studies.md)

#### HL7 Schema

- [概述](./10_Healthcare/HL7_Schema/01_Overview.md)
- [形式化定义](./10_Healthcare/HL7_Schema/02_Formal_Definition.md)
- [标准对标](./10_Healthcare/HL7_Schema/03_Standards.md)
- [转换体系](./10_Healthcare/HL7_Schema/04_Transformation.md)
- [实践案例](./10_Healthcare/HL7_Schema/05_Case_Studies.md)

### 1.10 食品行业Schema（11_Food_Industry）

#### Food Industry Schema

- [概述](./11_Food_Industry/Food_Industry_Schema/01_Overview.md)
- [形式化定义](./11_Food_Industry/Food_Industry_Schema/02_Formal_Definition.md)
- [标准对标](./11_Food_Industry/Food_Industry_Schema/03_Standards.md)
- [转换体系](./11_Food_Industry/Food_Industry_Schema/04_Transformation.md)
- [实践案例](./11_Food_Industry/Food_Industry_Schema/05_Case_Studies.md)

### 1.11 智慧家居Schema（12_Smart_Home）

#### Smart Home Schema

- [概述](./12_Smart_Home/Smart_Home_Schema/01_Overview.md)
- [形式化定义](./12_Smart_Home/Smart_Home_Schema/02_Formal_Definition.md)
- [标准对标](./12_Smart_Home/Smart_Home_Schema/03_Standards.md)
- [转换体系](./12_Smart_Home/Smart_Home_Schema/04_Transformation.md)
- [实践案例](./12_Smart_Home/Smart_Home_Schema/05_Case_Studies.md)

#### Matter Schema

- [概述](./12_Smart_Home/Matter_Schema/01_Overview.md)
- [形式化定义](./12_Smart_Home/Matter_Schema/02_Formal_Definition.md)
- [标准对标](./12_Smart_Home/Matter_Schema/03_Standards.md)
- [转换体系](./12_Smart_Home/Matter_Schema/04_Transformation.md)
- [实践案例](./12_Smart_Home/Matter_Schema/05_Case_Studies.md)

#### Thread Schema

- [概述](./12_Smart_Home/Thread_Schema/01_Overview.md)
- [形式化定义](./12_Smart_Home/Thread_Schema/02_Formal_Definition.md)
- [标准对标](./12_Smart_Home/Thread_Schema/03_Standards.md)
- [转换体系](./12_Smart_Home/Thread_Schema/04_Transformation.md)
- [实践案例](./12_Smart_Home/Thread_Schema/05_Case_Studies.md)

### 1.12 办公自动化Schema（13_OA_Office_Automation）

#### OA Schema

- [概述](./13_OA_Office_Automation/OA_Schema/01_Overview.md)
- [形式化定义](./13_OA_Office_Automation/OA_Schema/02_Formal_Definition.md)
- [标准对标](./13_OA_Office_Automation/OA_Schema/03_Standards.md)
- [转换体系](./13_OA_Office_Automation/OA_Schema/04_Transformation.md)
- [实践案例](./13_OA_Office_Automation/OA_Schema/05_Case_Studies.md)

### 1.13 工作流与BPM Schema（14_Workflow_BPM）

#### BPMN Schema

- [概述](./14_Workflow_BPM/BPMN_Schema/01_Overview.md)
- [形式化定义](./14_Workflow_BPM/BPMN_Schema/02_Formal_Definition.md)
- [标准对标](./14_Workflow_BPM/BPMN_Schema/03_Standards.md)
- [转换体系](./14_Workflow_BPM/BPMN_Schema/04_Transformation.md)
- [实践案例](./14_Workflow_BPM/BPMN_Schema/05_Case_Studies.md)

#### BPEL Schema

- [概述](./14_Workflow_BPM/BPEL_Schema/01_Overview.md)
- [形式化定义](./14_Workflow_BPM/BPEL_Schema/02_Formal_Definition.md)
- [标准对标](./14_Workflow_BPM/BPEL_Schema/03_Standards.md)
- [转换体系](./14_Workflow_BPM/BPEL_Schema/04_Transformation.md)
- [实践案例](./14_Workflow_BPM/BPEL_Schema/05_Case_Studies.md)

#### Workflow Engine Schema

- [概述](./14_Workflow_BPM/Workflow_Engine_Schema/01_Overview.md)
- [形式化定义](./14_Workflow_BPM/Workflow_Engine_Schema/02_Formal_Definition.md)
- [标准对标](./14_Workflow_BPM/Workflow_Engine_Schema/03_Standards.md)
- [转换体系](./14_Workflow_BPM/Workflow_Engine_Schema/04_Transformation.md)
- [实践案例](./14_Workflow_BPM/Workflow_Engine_Schema/05_Case_Studies.md)

### 1.14 ERP系统Schema（15_ERP_Systems）

#### ERP Schema

- [概述](./15_ERP_Systems/ERP_Schema/01_Overview.md)
- [形式化定义](./15_ERP_Systems/ERP_Schema/02_Formal_Definition.md)
- [标准对标](./15_ERP_Systems/ERP_Schema/03_Standards.md)
- [转换体系](./15_ERP_Systems/ERP_Schema/04_Transformation.md)
- [实践案例](./15_ERP_Systems/ERP_Schema/05_Case_Studies.md)

### 1.15 海运与航运Schema（08_Maritime_Shipping）

#### Maritime Schema

- [概述](./08_Maritime_Shipping/Maritime_Schema/01_Overview.md)
- [形式化定义](./08_Maritime_Shipping/Maritime_Schema/02_Formal_Definition.md)
- [标准对标](./08_Maritime_Shipping/Maritime_Schema/03_Standards.md)
- [转换体系](./08_Maritime_Shipping/Maritime_Schema/04_Transformation.md)
- [实践案例](./08_Maritime_Shipping/Maritime_Schema/05_Case_Studies.md)

### 1.29 API和协议Schema（29_API_Protocol_Schemas）⭐新增

#### GraphQL Schema

- [概述](./29_API_Protocol_Schemas/GraphQL_Schema/01_Overview.md)
- [形式化定义](./29_API_Protocol_Schemas/GraphQL_Schema/02_Formal_Definition.md)
- [标准对标](./29_API_Protocol_Schemas/GraphQL_Schema/03_Standards.md)
- [转换体系](./29_API_Protocol_Schemas/GraphQL_Schema/04_Transformation.md)
- [实践案例](./29_API_Protocol_Schemas/GraphQL_Schema/05_Case_Studies.md)

#### gRPC Schema

- [概述](./29_API_Protocol_Schemas/gRPC_Schema/01_Overview.md)
- [形式化定义](./29_API_Protocol_Schemas/gRPC_Schema/02_Formal_Definition.md)
- [标准对标](./29_API_Protocol_Schemas/gRPC_Schema/03_Standards.md)
- [转换体系](./29_API_Protocol_Schemas/gRPC_Schema/04_Transformation.md)
- [实践案例](./29_API_Protocol_Schemas/gRPC_Schema/05_Case_Studies.md)

#### Protocol Buffers Schema

- [概述](./29_API_Protocol_Schemas/Protocol_Buffers_Schema/01_Overview.md)
- [形式化定义](./29_API_Protocol_Schemas/Protocol_Buffers_Schema/02_Formal_Definition.md)
- [标准对标](./29_API_Protocol_Schemas/Protocol_Buffers_Schema/03_Standards.md)
- [转换体系](./29_API_Protocol_Schemas/Protocol_Buffers_Schema/04_Transformation.md)
- [实践案例](./29_API_Protocol_Schemas/Protocol_Buffers_Schema/05_Case_Studies.md)

#### Avro Schema

- [概述](./29_API_Protocol_Schemas/Avro_Schema/01_Overview.md)
- [形式化定义](./29_API_Protocol_Schemas/Avro_Schema/02_Formal_Definition.md)
- [标准对标](./29_API_Protocol_Schemas/Avro_Schema/03_Standards.md)
- [转换体系](./29_API_Protocol_Schemas/Avro_Schema/04_Transformation.md)
- [实践案例](./29_API_Protocol_Schemas/Avro_Schema/05_Case_Studies.md)

#### JSON Schema

- [概述](./29_API_Protocol_Schemas/JSON_Schema/01_Overview.md)
- [形式化定义](./29_API_Protocol_Schemas/JSON_Schema/02_Formal_Definition.md)
- [标准对标](./29_API_Protocol_Schemas/JSON_Schema/03_Standards.md)
- [转换体系](./29_API_Protocol_Schemas/JSON_Schema/04_Transformation.md)
- [实践案例](./29_API_Protocol_Schemas/JSON_Schema/05_Case_Studies.md)

#### AsyncAPI Schema

- [概述](./29_API_Protocol_Schemas/AsyncAPI_Schema/01_Overview.md)
- [形式化定义](./29_API_Protocol_Schemas/AsyncAPI_Schema/02_Formal_Definition.md)
- [标准对标](./29_API_Protocol_Schemas/AsyncAPI_Schema/03_Standards.md)
- [转换体系](./29_API_Protocol_Schemas/AsyncAPI_Schema/04_Transformation.md)
- [实践案例](./29_API_Protocol_Schemas/AsyncAPI_Schema/05_Case_Studies.md)

---

## 2. 按文档类型索引

### 2.1 概述文档（01_Overview.md）

所有子主题的概述文档：

- [PLC Schema概述](./01_Industrial_Automation/PLC_Schema/01_Overview.md)
- [CAN Schema概述](./01_Industrial_Automation/CAN_Schema/01_Overview.md)
- [传感器Schema概述](./02_IoT_Schema/Sensor_Schema/01_Overview.md)
- [通信Schema概述](./02_IoT_Schema/Communication_Schema/01_Overview.md)
- [控制Schema概述](./02_IoT_Schema/Control_Schema/01_Overview.md)
- [安全Schema概述](./02_IoT_Schema/Security_Schema/01_Overview.md)
- [消息队列Schema概述](./02_IoT_Schema/Message_Queue_Schema/01_Overview.md)
- [可观测性Schema概述](./02_IoT_Schema/Observability_Schema/01_Overview.md)
- [电气Schema概述](./03_Physical_Device/Electrical_Schema/01_Overview.md)
- [机械Schema概述](./03_Physical_Device/Mechanical_Schema/01_Overview.md)
- [CAD Schema概述](./03_Physical_Device/CAD_Schema/01_Overview.md)
- [热学Schema概述](./03_Physical_Device/Thermal_Schema/01_Overview.md)
- [安全Schema概述](./03_Physical_Device/Safety_Schema/01_Overview.md)
- [数字孪生Schema概述](./03_Physical_Device/Digital_Twin/01_Overview.md)
- [形式化模型概述](./04_Programming_Conversion/Formal_Model/01_Overview.md)
- [语言映射概述](./04_Programming_Conversion/Language_Mapping/01_Overview.md)
- [代码生成概述](./04_Programming_Conversion/Code_Generation/01_Overview.md)
- [信息论分析概述](./05_DSL_Theory/Information_Theory/01_Overview.md)
- [形式语言理论概述](./05_DSL_Theory/Formal_Language_Theory/01_Overview.md)
- [知识图谱Schema概述](./05_DSL_Theory/Knowledge_Graph/01_Overview.md)
- [SWIFT Schema概述](./06_Financial_Services/SWIFT_Schema/01_Overview.md)
- [ISO 20022 Schema概述](./06_Financial_Services/ISO20022_Schema/01_Overview.md)
- [Payment Schema概述](./06_Financial_Services/Payment_Schema/01_Overview.md)
- [GS1 Schema概述](./07_Logistics_Supply_Chain/GS1_Schema/01_Overview.md)
- [EDI Schema概述](./07_Logistics_Supply_Chain/EDI_Schema/01_Overview.md)
- [Smart City Schema概述](./08_Smart_City/Smart_City_Schema/01_Overview.md)
- [Healthcare Schema概述](./10_Healthcare/Healthcare_Schema/01_Overview.md)
- [FHIR Schema概述](./10_Healthcare/FHIR_Schema/01_Overview.md)
- [HL7 Schema概述](./10_Healthcare/HL7_Schema/01_Overview.md)
- [Food Industry Schema概述](./11_Food_Industry/Food_Industry_Schema/01_Overview.md)
- [Smart Home Schema概述](./12_Smart_Home/Smart_Home_Schema/01_Overview.md)
- [Matter Schema概述](./12_Smart_Home/Matter_Schema/01_Overview.md)
- [Thread Schema概述](./12_Smart_Home/Thread_Schema/01_Overview.md)
- [OA Schema概述](./13_OA_Office_Automation/OA_Schema/01_Overview.md)
- [BPMN Schema概述](./14_Workflow_BPM/BPMN_Schema/01_Overview.md)
- [BPEL Schema概述](./14_Workflow_BPM/BPEL_Schema/01_Overview.md)
- [Workflow Engine Schema概述](./14_Workflow_BPM/Workflow_Engine_Schema/01_Overview.md)
- [ERP Schema概述](./15_ERP_Systems/ERP_Schema/01_Overview.md)
- [Maritime Schema概述](./08_Maritime_Shipping/Maritime_Schema/01_Overview.md)

### 2.2 形式化定义（02_Formal_Definition.md）

所有子主题的形式化定义文档：

- [PLC Schema形式化定义](./01_Industrial_Automation/PLC_Schema/02_Formal_Definition.md)
- [CAN Schema形式化定义](./01_Industrial_Automation/CAN_Schema/02_Formal_Definition.md)
- [传感器Schema形式化定义](./02_IoT_Schema/Sensor_Schema/02_Formal_Definition.md)
- [通信Schema形式化定义](./02_IoT_Schema/Communication_Schema/02_Formal_Definition.md)
- [控制Schema形式化定义](./02_IoT_Schema/Control_Schema/02_Formal_Definition.md)
- [安全Schema形式化定义](./02_IoT_Schema/Security_Schema/02_Formal_Definition.md)
- [电气Schema形式化定义](./03_Physical_Device/Electrical_Schema/02_Formal_Definition.md)
- [机械Schema形式化定义](./03_Physical_Device/Mechanical_Schema/02_Formal_Definition.md)
- [CAD Schema形式化定义](./03_Physical_Device/CAD_Schema/02_Formal_Definition.md)
- [热学Schema形式化定义](./03_Physical_Device/Thermal_Schema/02_Formal_Definition.md)
- [安全Schema形式化定义](./03_Physical_Device/Safety_Schema/02_Formal_Definition.md)
- [数字孪生Schema形式化定义](./03_Physical_Device/Digital_Twin/02_Formal_Definition.md)
- [形式化模型形式化定义](./04_Programming_Conversion/Formal_Model/02_Formal_Definition.md)
- [语言映射形式化定义](./04_Programming_Conversion/Language_Mapping/02_Formal_Definition.md)
- [代码生成形式化定义](./04_Programming_Conversion/Code_Generation/02_Formal_Definition.md)
- [信息论分析形式化定义](./05_DSL_Theory/Information_Theory/02_Formal_Definition.md)
- [形式语言理论形式化定义](./05_DSL_Theory/Formal_Language_Theory/02_Formal_Definition.md)
- [知识图谱Schema形式化定义](./05_DSL_Theory/Knowledge_Graph/02_Formal_Definition.md)
- [SWIFT Schema形式化定义](./06_Financial_Services/SWIFT_Schema/02_Formal_Definition.md)
- [ISO 20022 Schema形式化定义](./06_Financial_Services/ISO20022_Schema/02_Formal_Definition.md)
- [Payment Schema形式化定义](./06_Financial_Services/Payment_Schema/02_Formal_Definition.md)
- [GS1 Schema形式化定义](./07_Logistics_Supply_Chain/GS1_Schema/02_Formal_Definition.md)
- [EDI Schema形式化定义](./07_Logistics_Supply_Chain/EDI_Schema/02_Formal_Definition.md)
- [Smart City Schema形式化定义](./08_Smart_City/Smart_City_Schema/02_Formal_Definition.md)
- [Healthcare Schema形式化定义](./10_Healthcare/Healthcare_Schema/02_Formal_Definition.md)
- [FHIR Schema形式化定义](./10_Healthcare/FHIR_Schema/02_Formal_Definition.md)
- [HL7 Schema形式化定义](./10_Healthcare/HL7_Schema/02_Formal_Definition.md)
- [Food Industry Schema形式化定义](./11_Food_Industry/Food_Industry_Schema/02_Formal_Definition.md)
- [Smart Home Schema形式化定义](./12_Smart_Home/Smart_Home_Schema/02_Formal_Definition.md)
- [Matter Schema形式化定义](./12_Smart_Home/Matter_Schema/02_Formal_Definition.md)
- [Thread Schema形式化定义](./12_Smart_Home/Thread_Schema/02_Formal_Definition.md)
- [OA Schema形式化定义](./13_OA_Office_Automation/OA_Schema/02_Formal_Definition.md)
- [BPMN Schema形式化定义](./14_Workflow_BPM/BPMN_Schema/02_Formal_Definition.md)
- [BPEL Schema形式化定义](./14_Workflow_BPM/BPEL_Schema/02_Formal_Definition.md)
- [Workflow Engine Schema形式化定义](./14_Workflow_BPM/Workflow_Engine_Schema/02_Formal_Definition.md)
- [ERP Schema形式化定义](./15_ERP_Systems/ERP_Schema/02_Formal_Definition.md)
- [Maritime Schema形式化定义](./08_Maritime_Shipping/Maritime_Schema/02_Formal_Definition.md)

### 2.3 标准对标（03_Standards.md）

所有子主题的标准对标文档：

- [PLC Schema标准对标](./01_Industrial_Automation/PLC_Schema/03_Standards.md)
- [CAN Schema标准对标](./01_Industrial_Automation/CAN_Schema/03_Standards.md)
- [传感器Schema标准对标](./02_IoT_Schema/Sensor_Schema/03_Standards.md)
- [通信Schema标准对标](./02_IoT_Schema/Communication_Schema/03_Standards.md)
- [控制Schema标准对标](./02_IoT_Schema/Control_Schema/03_Standards.md)
- [安全Schema标准对标](./02_IoT_Schema/Security_Schema/03_Standards.md)
- [电气Schema标准对标](./03_Physical_Device/Electrical_Schema/03_Standards.md)
- [机械Schema标准对标](./03_Physical_Device/Mechanical_Schema/03_Standards.md)
- [CAD Schema标准对标](./03_Physical_Device/CAD_Schema/03_Standards.md)
- [热学Schema标准对标](./03_Physical_Device/Thermal_Schema/03_Standards.md)
- [安全Schema标准对标](./03_Physical_Device/Safety_Schema/03_Standards.md)
- [数字孪生Schema标准对标](./03_Physical_Device/Digital_Twin/03_Standards.md)
- [形式化模型标准对标](./04_Programming_Conversion/Formal_Model/03_Standards.md)
- [语言映射标准对标](./04_Programming_Conversion/Language_Mapping/03_Standards.md)
- [代码生成标准对标](./04_Programming_Conversion/Code_Generation/03_Standards.md)
- [信息论分析标准对标](./05_DSL_Theory/Information_Theory/03_Standards.md)
- [形式语言理论标准对标](./05_DSL_Theory/Formal_Language_Theory/03_Standards.md)
- [知识图谱Schema标准对标](./05_DSL_Theory/Knowledge_Graph/03_Standards.md)
- [SWIFT Schema标准对标](./06_Financial_Services/SWIFT_Schema/03_Standards.md)
- [ISO 20022 Schema标准对标](./06_Financial_Services/ISO20022_Schema/03_Standards.md)
- [Payment Schema标准对标](./06_Financial_Services/Payment_Schema/03_Standards.md)
- [GS1 Schema标准对标](./07_Logistics_Supply_Chain/GS1_Schema/03_Standards.md)
- [EDI Schema标准对标](./07_Logistics_Supply_Chain/EDI_Schema/03_Standards.md)
- [Smart City Schema标准对标](./08_Smart_City/Smart_City_Schema/03_Standards.md)
- [Healthcare Schema标准对标](./10_Healthcare/Healthcare_Schema/03_Standards.md)
- [FHIR Schema标准对标](./10_Healthcare/FHIR_Schema/03_Standards.md)
- [HL7 Schema标准对标](./10_Healthcare/HL7_Schema/03_Standards.md)
- [Food Industry Schema标准对标](./11_Food_Industry/Food_Industry_Schema/03_Standards.md)
- [Smart Home Schema标准对标](./12_Smart_Home/Smart_Home_Schema/03_Standards.md)
- [Matter Schema标准对标](./12_Smart_Home/Matter_Schema/03_Standards.md)
- [Thread Schema标准对标](./12_Smart_Home/Thread_Schema/03_Standards.md)
- [OA Schema标准对标](./13_OA_Office_Automation/OA_Schema/03_Standards.md)
- [BPMN Schema标准对标](./14_Workflow_BPM/BPMN_Schema/03_Standards.md)
- [BPEL Schema标准对标](./14_Workflow_BPM/BPEL_Schema/03_Standards.md)
- [Workflow Engine Schema标准对标](./14_Workflow_BPM/Workflow_Engine_Schema/03_Standards.md)
- [ERP Schema标准对标](./15_ERP_Systems/ERP_Schema/03_Standards.md)
- [Maritime Schema标准对标](./08_Maritime_Shipping/Maritime_Schema/03_Standards.md)

### 2.4 转换体系（04_Transformation.md）

所有子主题的转换体系文档：

- [PLC Schema转换体系](./01_Industrial_Automation/PLC_Schema/04_Transformation.md)
- [CAN Schema转换体系](./01_Industrial_Automation/CAN_Schema/04_Transformation.md)
- [传感器Schema转换体系](./02_IoT_Schema/Sensor_Schema/04_Transformation.md)
- [通信Schema转换体系](./02_IoT_Schema/Communication_Schema/04_Transformation.md)
- [控制Schema转换体系](./02_IoT_Schema/Control_Schema/04_Transformation.md)
- [安全Schema转换体系](./02_IoT_Schema/Security_Schema/04_Transformation.md)
- [电气Schema转换体系](./03_Physical_Device/Electrical_Schema/04_Transformation.md)
- [机械Schema转换体系](./03_Physical_Device/Mechanical_Schema/04_Transformation.md)
- [CAD Schema转换体系](./03_Physical_Device/CAD_Schema/04_Transformation.md)
- [热学Schema转换体系](./03_Physical_Device/Thermal_Schema/04_Transformation.md)
- [安全Schema转换体系](./03_Physical_Device/Safety_Schema/04_Transformation.md)
- [数字孪生Schema转换体系](./03_Physical_Device/Digital_Twin/04_Transformation.md)
- [形式化模型转换体系](./04_Programming_Conversion/Formal_Model/04_Transformation.md)
- [语言映射转换体系](./04_Programming_Conversion/Language_Mapping/04_Transformation.md)
- [代码生成转换体系](./04_Programming_Conversion/Code_Generation/04_Transformation.md)
- [信息论分析转换体系](./05_DSL_Theory/Information_Theory/04_Transformation.md)
- [形式语言理论转换体系](./05_DSL_Theory/Formal_Language_Theory/04_Transformation.md)
- [知识图谱Schema转换体系](./05_DSL_Theory/Knowledge_Graph/04_Transformation.md)
- [SWIFT Schema转换体系](./06_Financial_Services/SWIFT_Schema/04_Transformation.md)
- [ISO 20022 Schema转换体系](./06_Financial_Services/ISO20022_Schema/04_Transformation.md)
- [Payment Schema转换体系](./06_Financial_Services/Payment_Schema/04_Transformation.md)
- [GS1 Schema转换体系](./07_Logistics_Supply_Chain/GS1_Schema/04_Transformation.md)
- [EDI Schema转换体系](./07_Logistics_Supply_Chain/EDI_Schema/04_Transformation.md)
- [Smart City Schema转换体系](./08_Smart_City/Smart_City_Schema/04_Transformation.md)
- [Healthcare Schema转换体系](./10_Healthcare/Healthcare_Schema/04_Transformation.md)
- [FHIR Schema转换体系](./10_Healthcare/FHIR_Schema/04_Transformation.md)
- [HL7 Schema转换体系](./10_Healthcare/HL7_Schema/04_Transformation.md)
- [Food Industry Schema转换体系](./11_Food_Industry/Food_Industry_Schema/04_Transformation.md)
- [Smart Home Schema转换体系](./12_Smart_Home/Smart_Home_Schema/04_Transformation.md)
- [Matter Schema转换体系](./12_Smart_Home/Matter_Schema/04_Transformation.md)
- [Thread Schema转换体系](./12_Smart_Home/Thread_Schema/04_Transformation.md)
- [OA Schema转换体系](./13_OA_Office_Automation/OA_Schema/04_Transformation.md)
- [BPMN Schema转换体系](./14_Workflow_BPM/BPMN_Schema/04_Transformation.md)
- [BPEL Schema转换体系](./14_Workflow_BPM/BPEL_Schema/04_Transformation.md)
- [Workflow Engine Schema转换体系](./14_Workflow_BPM/Workflow_Engine_Schema/04_Transformation.md)
- [ERP Schema转换体系](./15_ERP_Systems/ERP_Schema/04_Transformation.md)
- [Maritime Schema转换体系](./08_Maritime_Shipping/Maritime_Schema/04_Transformation.md)

### 2.5 实践案例（05_Case_Studies.md）

所有子主题的实践案例文档：

- [PLC Schema实践案例](./01_Industrial_Automation/PLC_Schema/05_Case_Studies.md)
- [CAN Schema实践案例](./01_Industrial_Automation/CAN_Schema/05_Case_Studies.md)
- [传感器Schema实践案例](./02_IoT_Schema/Sensor_Schema/05_Case_Studies.md)
- [通信Schema实践案例](./02_IoT_Schema/Communication_Schema/05_Case_Studies.md)
- [控制Schema实践案例](./02_IoT_Schema/Control_Schema/05_Case_Studies.md)
- [安全Schema实践案例](./02_IoT_Schema/Security_Schema/05_Case_Studies.md)
- [电气Schema实践案例](./03_Physical_Device/Electrical_Schema/05_Case_Studies.md)
- [机械Schema实践案例](./03_Physical_Device/Mechanical_Schema/05_Case_Studies.md)
- [CAD Schema实践案例](./03_Physical_Device/CAD_Schema/05_Case_Studies.md)
- [热学Schema实践案例](./03_Physical_Device/Thermal_Schema/05_Case_Studies.md)
- [安全Schema实践案例](./03_Physical_Device/Safety_Schema/05_Case_Studies.md)
- [数字孪生Schema实践案例](./03_Physical_Device/Digital_Twin/05_Case_Studies.md)
- [形式化模型实践案例](./04_Programming_Conversion/Formal_Model/05_Case_Studies.md)
- [语言映射实践案例](./04_Programming_Conversion/Language_Mapping/05_Case_Studies.md)
- [代码生成实践案例](./04_Programming_Conversion/Code_Generation/05_Case_Studies.md)
- [信息论分析实践案例](./05_DSL_Theory/Information_Theory/05_Case_Studies.md)
- [形式语言理论实践案例](./05_DSL_Theory/Formal_Language_Theory/05_Case_Studies.md)
- [知识图谱Schema实践案例](./05_DSL_Theory/Knowledge_Graph/05_Case_Studies.md)
- [SWIFT Schema实践案例](./06_Financial_Services/SWIFT_Schema/05_Case_Studies.md)
- [ISO 20022 Schema实践案例](./06_Financial_Services/ISO20022_Schema/05_Case_Studies.md)
- [Payment Schema实践案例](./06_Financial_Services/Payment_Schema/05_Case_Studies.md)
- [GS1 Schema实践案例](./07_Logistics_Supply_Chain/GS1_Schema/05_Case_Studies.md)
- [EDI Schema实践案例](./07_Logistics_Supply_Chain/EDI_Schema/05_Case_Studies.md)
- [Smart City Schema实践案例](./08_Smart_City/Smart_City_Schema/05_Case_Studies.md)
- [Healthcare Schema实践案例](./10_Healthcare/Healthcare_Schema/05_Case_Studies.md)
- [FHIR Schema实践案例](./10_Healthcare/FHIR_Schema/05_Case_Studies.md)
- [HL7 Schema实践案例](./10_Healthcare/HL7_Schema/05_Case_Studies.md)
- [Food Industry Schema实践案例](./11_Food_Industry/Food_Industry_Schema/05_Case_Studies.md)
- [Smart Home Schema实践案例](./12_Smart_Home/Smart_Home_Schema/05_Case_Studies.md)
- [Matter Schema实践案例](./12_Smart_Home/Matter_Schema/05_Case_Studies.md)
- [Thread Schema实践案例](./12_Smart_Home/Thread_Schema/05_Case_Studies.md)
- [OA Schema实践案例](./13_OA_Office_Automation/OA_Schema/05_Case_Studies.md)
- [BPMN Schema实践案例](./14_Workflow_BPM/BPMN_Schema/05_Case_Studies.md)
- [BPEL Schema实践案例](./14_Workflow_BPM/BPEL_Schema/05_Case_Studies.md)
- [Workflow Engine Schema实践案例](./14_Workflow_BPM/Workflow_Engine_Schema/05_Case_Studies.md)
- [ERP Schema实践案例](./15_ERP_Systems/ERP_Schema/05_Case_Studies.md)
- [Maritime Schema实践案例](./08_Maritime_Shipping/Maritime_Schema/05_Case_Studies.md)

---

## 3. 按标准索引

### 3.1 IEC标准

- **IEC 61131-3**：[PLC Schema标准对标](./01_Industrial_Automation/PLC_Schema/03_Standards.md#21-iec-61131-3)
- **IEC 61850**：[通信Schema标准对标](./02_IoT_Schema/Communication_Schema/03_Standards.md)
- **IEC 60335-1**：[电气Schema标准对标](./03_Physical_Device/Electrical_Schema/03_Standards.md#21-iec-60335-1)
- **IEC 63278**：[数字孪生标准对标](./03_Physical_Device/Digital_Twin/03_Standards.md#22-iec-63278)

### 3.2 ISO标准

- **ISO 11898**：[CAN Schema标准对标](./01_Industrial_Automation/CAN_Schema/03_Standards.md)
- **ISO/IEC 23247**：[数字孪生标准对标](./03_Physical_Device/Digital_Twin/03_Standards.md#21-isoiec-23247)
- **ISO/IEC 21838**：[知识图谱标准对标](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#23-isoiec-21838)

### 3.3 W3C标准

- **W3C RDF**：[知识图谱标准对标](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#21-w3c-rdf)
- **W3C OWL**：[知识图谱标准对标](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#22-w3c-owl)
- **W3C JSON-LD**：[知识图谱标准对标](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#32-json-ld)

### 3.4 国家标准

- **GB/T 33008.1-2016**：[PLC Schema标准对标](./01_Industrial_Automation/PLC_Schema/03_Standards.md#32-gbt-330081-2016)
- **GB/T 34068-2017**：[传感器Schema标准对标](./02_IoT_Schema/Sensor_Schema/03_Standards.md)
- **GB/T 41479-2022**：[数字孪生标准对标](./03_Physical_Device/Digital_Twin/03_Standards.md#31-gbt-41479-2022)

---

## 4. 按应用场景索引

### 4.1 工业自动化场景

- **PLC编程**：[PLC Schema概述](./01_Industrial_Automation/PLC_Schema/01_Overview.md)
- **CAN通信**：[CAN Schema概述](./01_Industrial_Automation/CAN_Schema/01_Overview.md)
- **智能制造**：[数字孪生实践案例](./03_Physical_Device/Digital_Twin/05_Case_Studies.md#2-案例1智能制造数字孪生)

### 4.2 物联网场景

- **传感器应用**：[传感器Schema概述](./02_IoT_Schema/Sensor_Schema/01_Overview.md)
- **通信协议**：[通信Schema概述](./02_IoT_Schema/Communication_Schema/01_Overview.md)
- **设备控制**：[控制Schema概述](./02_IoT_Schema/Control_Schema/01_Overview.md)
- **安全防护**：[安全Schema概述](./02_IoT_Schema/Security_Schema/01_Overview.md)

### 4.3 数字孪生场景

- **智能制造**：[数字孪生实践案例 - 智能制造](./03_Physical_Device/Digital_Twin/05_Case_Studies.md#2-案例1智能制造数字孪生)
- **预测维护**：[数字孪生实践案例 - 预测维护](./03_Physical_Device/Digital_Twin/05_Case_Studies.md#3-案例2预测维护数字孪生)
- **产品设计**：[数字孪生实践案例 - 产品设计](./03_Physical_Device/Digital_Twin/05_Case_Studies.md#4-案例3产品设计数字孪生)

### 4.4 代码生成场景

- **多语言生成**：[代码生成概述](./04_Programming_Conversion/Code_Generation/01_Overview.md)
- **语言映射**：[语言映射概述](./04_Programming_Conversion/Language_Mapping/01_Overview.md)
- **形式化模型**：[形式化模型概述](./04_Programming_Conversion/Formal_Model/01_Overview.md)

---

## 5. 跨主题关联

### 5.1 相关主题链接

**数字孪生相关**：

- [电气Schema](./03_Physical_Device/Electrical_Schema/01_Overview.md) - 数字孪生的电气映射
- [机械Schema](./03_Physical_Device/Mechanical_Schema/01_Overview.md) - 数字孪生的机械映射
- [传感器Schema](./02_IoT_Schema/Sensor_Schema/01_Overview.md) - 数字孪生的数据源

**知识图谱相关**：

- [信息论分析](./05_DSL_Theory/Information_Theory/01_Overview.md) - 知识图谱的信息论基础
- [形式语言理论](./05_DSL_Theory/Formal_Language_Theory/01_Overview.md) - 知识图谱的形式化基础
- [代码生成](./04_Programming_Conversion/Code_Generation/01_Overview.md) - 知识图谱的代码生成

**转换相关**：

- [形式化模型](./04_Programming_Conversion/Formal_Model/01_Overview.md) - 转换的形式化基础
- [语言映射](./04_Programming_Conversion/Language_Mapping/01_Overview.md) - 转换的语言映射
- [信息论分析](./05_DSL_Theory/Information_Theory/01_Overview.md) - 转换的信息论分析

### 5.2 标准关联

**IEC标准系列**：

- [IEC 61131-3](./01_Industrial_Automation/PLC_Schema/03_Standards.md#21-iec-61131-3) - PLC编程
- [IEC 61850](./02_IoT_Schema/Communication_Schema/03_Standards.md) - 通信协议
- [IEC 63278](./03_Physical_Device/Digital_Twin/03_Standards.md#22-iec-63278) - 数字孪生

**ISO标准系列**：

- [ISO 11898](./01_Industrial_Automation/CAN_Schema/03_Standards.md) - CAN协议
- [ISO/IEC 23247](./03_Physical_Device/Digital_Twin/03_Standards.md#21-isoiec-23247) - 数字孪生
- [ISO/IEC 21838](./05_DSL_Theory/Knowledge_Graph/03_Standards.md#23-isoiec-21838) - 知识图谱

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21（新增29_API_Protocol_Schemas主题）

**相关文档**：

- [项目总览](./README.md)
- [快速参考指南](./QUICK_REFERENCE.md)
- [术语表和缩写表](./GLOSSARY.md)
- [行业覆盖分析报告](./INDUSTRY_COVERAGE_ANALYSIS.md)
- [项目完成总结](./PROJECT_COMPLETION_SUMMARY.md)
- [文档扩展和深化计划](./DOCUMENT_EXPANSION_PLAN.md)
