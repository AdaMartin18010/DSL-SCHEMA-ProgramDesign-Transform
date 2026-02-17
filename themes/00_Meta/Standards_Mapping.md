# Themes 国际标准映射文档

## 概述

本文档建立35个主题与国际标准之间的映射关系，提供完整的标准链接和参考信息。

---

## 国际标准机构概览

### 1. W3C (World Wide Web Consortium)
- **官网**: https://www.w3.org/
- **性质**: Web技术标准组织
- **成立时间**: 1994年
- **总部**: MIT, 美国

### 2. ISO (International Organization for Standardization)
- **官网**: https://www.iso.org/
- **性质**: 国际标准化组织
- **成立时间**: 1947年
- **总部**: 日内瓦, 瑞士

### 3. IEC (International Electrotechnical Commission)
- **官网**: https://www.iec.ch/
- **性质**: 国际电工委员会
- **成立时间**: 1906年
- **总部**: 日内瓦, 瑞士

### 4. OMG (Object Management Group)
- **官网**: https://www.omg.org/
- **性质**: 对象管理组织
- **成立时间**: 1989年
- **总部**: 马萨诸塞州, 美国

### 5. IEEE (Institute of Electrical and Electronics Engineers)
- **官网**: https://www.ieee.org/
- **性质**: 电气电子工程师学会
- **成立时间**: 1963年
- **总部**: 纽约, 美国

### 6. IETF (Internet Engineering Task Force)
- **官网**: https://www.ietf.org/
- **性质**: 互联网工程任务组
- **成立时间**: 1986年
- **运作方式**: 开放标准组织

---

## 标准分类体系

### 知识表示与语义网标准

| 标准 | 机构 | 版本 | 状态 | 官网链接 |
|------|------|------|------|----------|
| RDF | W3C | 1.2 | Working Draft | https://www.w3.org/TR/rdf12-concepts/ |
| OWL | W3C | 2 | 推荐标准 | https://www.w3.org/TR/owl2-overview/ |
| JSON-LD | W3C | 1.1 | 推荐标准 | https://www.w3.org/TR/json-ld11/ |
| RDF Schema | W3C | 1.2 | 开发中 | https://www.w3.org/TR/rdf-schema/ |
| SPARQL | W3C | 1.1 | 推荐标准 | https://www.w3.org/TR/sparql11-overview/ |
| SHACL | W3C | 1.0 | 推荐标准 | https://www.w3.org/TR/shacl/ |
| SKOS | W3C | 1.1 | 推荐标准 | https://www.w3.org/TR/skos-reference/ |

**主题映射**:
- `05_DSL_Theory` - 理论基础
- `25_AI_Code_Integration` - 知识表示
- `33_Industry_Deepening` - 行业本体

---

### 顶层本体标准 (ISO/IEC 21838)

| 部分 | 标准名称 | 版本 | 状态 | 链接 |
|------|----------|------|------|------|
| Part 1 | Requirements | 2021 | 已发布 | https://www.iso.org/standard/74387.html |
| Part 2 | BFO | 2021 | 已发布 | https://www.iso.org/standard/74388.html |
| Part 3 | DOLCE | 2023 | 已发布 | https://www.iso.org/standard/78927.html |
| Part 4 | TUpper | 2023 | 已发布 | https://www.iso.org/standard/74390.html |
| Part 5 | UFO | 开发中 | 草案 | - |

**主题映射**:
- `05_DSL_Theory` - 形式化基础
- `32_Cross_Disciplinary` - 跨学科本体

---

### 工业自动化标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| IEC 61131-3 | IEC | 3.0 (2013) | PLC编程 | https://webstore.iec.ch/publication/66912 |
| IEC 61499 | IEC | 2.0 (2012) | 功能块 | https://webstore.iec.ch/publication/66926 |
| OPC UA | OPC Foundation | 1.05 | 统一架构 | https://opcfoundation.org/about/opc-technologies/opc-ua/ |
| ISA-95 | ISA/IEC | 2018 | 企业控制集成 | https://www.isa.org/standards-and-publications/isa-standards/isa-95/ |

**主题映射**:
- `01_Industrial_Automation` - 工业自动化
- `17_Manufacturing` - 智能制造

---

### 物联网标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| MQTT | OASIS | 5.0 | 消息传输 | https://mqtt.org/mqtt-specification/ |
| CoAP | IETF | RFC 7252 | 约束应用协议 | https://datatracker.ietf.org/doc/html/rfc7252 |
| LwM2M | OMA SpecWorks | 1.2 | 设备管理 | https://omaspecworks.org/what-is-oma-specworks/iot/lightweight-m2m-lwm2m/ |
| Matter | CSA | 1.0 | 智能家居 | https://csa-iot.org/all-solutions/matter/ |
| Zigbee | CSA | 3.0 | 无线传感 | https://csa-iot.org/all-solutions/zigbee/ |
| OneM2M | oneM2M | 2.0 | M2M服务 | https://www.onem2m.org/ |

**主题映射**:
- `02_IoT_Schema` - 物联网
- `12_Smart_Home` - 智能家居

---

### 金融服务标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| ISO 20022 | ISO | 2013-至今 | 金融报文 | https://www.iso20022.org/ |
| FIX | FIX Trading Community | 5.0 | 证券交易 | https://www.fixtrading.org/standards/ |
| XBRL | XBRL International | 2.1 | 财务报告 | https://www.xbrl.org/ |
| PCI DSS | PCI SSC | 4.0 | 支付安全 | https://www.pcisecuritystandards.org/ |
| SWIFT MT/MX | SWIFT | 2023 | 银行报文 | https://www.swift.com/standards |

**主题映射**:
- `06_Financial_Services` - 金融服务
- `26_Enterprise_Finance` - 企业财务

---

### 医疗健康标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| FHIR | HL7 | R5 | 医疗数据交换 | https://www.hl7.org/fhir/ |
| HL7 v2.x | HL7 | 2.9 | 医疗消息 | https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185 |
| DICOM | NEMA | 2023b | 医学影像 | https://www.dicomstandard.org/ |
| ICD-11 | WHO | 2019 | 疾病分类 | https://icd.who.int/browse11/l-m/en |
| SNOMED CT | SNOMED International | 2024 | 临床术语 | https://www.snomed.org/ |

**主题映射**:
- `10_Healthcare` - 医疗健康

---

### 能源电力标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| IEC 61850 | IEC | 2.1 (2023) | 变电站通信 | https://webstore.iec.ch/publication/66912 |
| IEC 61970 | IEC | 600系列 | 能量管理系统 | https://webstore.iec.ch/publication/62112 |
| IEC 61968 | IEC | 5.0 | 配电管理 | https://webstore.iec.ch/publication/62113 |
| CIM | IEC | 17版 | 通用信息模型 | https://www.iec.ch/dyn/www/f?p=103:38:0:::::
| IEEE 1547 | IEEE | 2018 | 分布式能源 | https://standards.ieee.org/standard/1547-2018.html |

**主题映射**:
- `16_Energy_Industry` - 能源行业

---

### API与协议标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| OpenAPI | OpenAPI Initiative | 3.1 | REST API | https://spec.openapis.org/oas/v3.1.0 |
| AsyncAPI | AsyncAPI Initiative | 2.6 | 异步API | https://www.asyncapi.com/docs/reference/specification/v2.6.0 |
| GraphQL | GraphQL Foundation | 2021 | 查询语言 | https://spec.graphql.org/ |
| gRPC | CNCF | 3.21 | RPC框架 | https://grpc.io/docs/ |
| JSON Schema | IETF | Draft 2020-12 | JSON验证 | https://json-schema.org/ |

**主题映射**:
- `29_API_Protocol_Schemas` - API协议
- `30_Cloud_Native_DevOps` - 云原生

---

### 云计算与DevOps标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| Kubernetes | CNCF | 1.29 | 容器编排 | https://kubernetes.io/docs/home/ |
| Terraform | HashiCorp | 1.7 | 基础设施即代码 | https://developer.hashicorp.com/terraform/docs |
| Docker | Docker Inc. | 24.0 | 容器化 | https://docs.docker.com/ |
| OCI | OCI | 1.1 | 容器标准 | https://opencontainers.org/ |
| CloudEvents | CNCF | 1.0 | 事件规范 | https://cloudevents.io/ |

**主题映射**:
- `30_Cloud_Native_DevOps` - 云原生DevOps

---

### 安全与合规标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| ISO/IEC 27001 | ISO/IEC | 2022 | 信息安全管理 | https://www.iso.org/standard/27001 |
| ISO/IEC 27002 | ISO/IEC | 2022 | 安全控制 | https://www.iso.org/standard/27002 |
| NIST CSF | NIST | 2.0 | 网络安全框架 | https://www.nist.gov/cyberframework |
| SOC 2 | AICPA | 2017 | 服务组织控制 | https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2 |
| GDPR | EU | 2016 | 数据保护 | https://gdpr.eu/ |

**主题映射**:
- `32_Security_Compliance` - 安全合规

---

### 电信标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| eTOM | TM Forum | 23 | 电信运营 | https://www.tmforum.org/etom/ |
| SID | TM Forum | 23 | 信息框架 | https://www.tmforum.org/sid/ |
| TMF API | TM Forum | ODA | Open API | https://www.tmforum.org/oda/ |
| 3GPP | 3GPP | R18 | 移动通信 | https://www.3gpp.org/ |
| ETSI | ETSI | 多版本 | 欧洲电信 | https://www.etsi.org/ |

**主题映射**:
- `23_Telecommunications` - 电信

---

### 物流供应链标准

| 标准 | 机构 | 版本 | 应用领域 | 链接 |
|------|------|------|----------|------|
| EPCIS | GS1 | 2.0 | 事件捕获 | https://www.gs1.org/standards/epcis |
| GS1 | GS1 | 2024 | 标识系统 | https://www.gs1.org/standards |
| EDIFACT | UN/CEFACT | D22B | 电子数据交换 | https://unece.org/trade/uncefact/introducing-unedifact |
| RosettaNet | GS1 | 2020 | 供应链 | https://www.gs1.org/standards/rosettanet |

**主题映射**:
- `07_Logistics_Supply_Chain` - 物流供应链

---

## 标准关系图

```
                    ┌─────────────────────────────────────────┐
                    │         国际标准体系架构                 │
                    └───────────────────┬─────────────────────┘
                                        │
        ┌───────────────┬───────────────┼───────────────┬───────────────┐
        ▼               ▼               ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
   │  W3C    │    │ ISO/IEC │    │   IEC   │    │   OMG   │    │  行业   │
   │ 语义网  │    │ 通用标准│    │ 工业标准│    │ 建模标准│    │ 特定    │
   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
        │               │               │               │               │
   ┌────┴────┐     ┌────┴────┐     ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
   │RDF/OWL  │     │21838    │     │61131-3  │     │UML/ODM  │     │ISO 20022│
   │JSON-LD  │     │27001    │     │61850    │     │SysML    │     │FHIR     │
   │SPARQL   │     │20022    │     │61499    │     │BPMN     │     │PCI DSS  │
   └─────────┘     └─────────┘     └─────────┘     └─────────┘     └─────────┘
        │               │               │               │               │
        └───────────────┴───────────────┴───────────────┴───────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │         DSL Schema 统一框架              │
                    └─────────────────────────────────────────┘
```

---

## 标准采用指南

### 如何选择标准

1. **识别领域**: 确定所属行业和领域
2. **查找相关**: 使用本映射文档查找相关标准
3. **评估成熟度**: 检查标准版本和状态
4. **验证兼容性**: 确认与现有系统的兼容性
5. **考虑成本**: 评估认证和实施成本

### 标准实施路径

```
阶段1: 标准识别
    ↓
阶段2: 差距分析
    ↓
阶段3: 规划设计
    ↓
阶段4: 试点实施
    ↓
阶段5: 全面推广
    ↓
阶段6: 认证审核 (如需要)
```

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-17 | v1.0 | 初始版本，覆盖主要国际标准 |

---

**创建时间**: 2026-02-17  
**最后更新**: 2026-02-17  
**维护者**: DSL Schema研究团队
