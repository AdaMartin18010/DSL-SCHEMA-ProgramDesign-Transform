# EDI Schema形式化定义

## 📑 目录

- [EDI Schema形式化定义](#edi-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. EDI X12 Schema](#2-edi-x12-schema)
  - [3. EDIFACT Schema](#3-edifact-schema)
  - [4. 类型系统](#4-类型系统)
  - [5. 约束规则](#5-约束规则)
  - [6. 转换函数](#6-转换函数)
  - [7. 形式化定理](#7-形式化定理)
    - [7.1 EDI消息完整性定理](#71-edi消息完整性定理)
    - [7.2 EDI转换保真性定理](#72-edi转换保真性定理)

---

## 1. 形式化模型

**定义1（EDI Schema）**：
EDI Schema是一个二元组：

```text
EDI_Schema = (EDI_X12, EDIFACT)
```

其中：

- `EDI_X12`：EDI X12标准Schema
- `EDIFACT`：EDIFACT标准Schema

---

## 2. EDI X12 Schema

**定义2（EDI X12 Schema）**：

```text
EDI_X12_Schema = (Transaction_Set, Segment, Element)
```

**形式化DSL定义**：

```dsl
schema EDI_X12 {
  interchange: Interchange {
    isa_header: ISA_Header {
      authorization_qualifier: String @length(2) @required
      authorization_information: String @length(10) @required
      security_qualifier: String @length(2) @required
      security_information: String @length(10) @required
      interchange_id_qualifier: String @length(2) @required
      interchange_sender_id: String @length(15) @required
      interchange_id_qualifier_2: String @length(2) @required
      interchange_receiver_id: String @length(15) @required
      interchange_date: Date @format("YYMMDD") @required
      interchange_time: Time @format("HHMM") @required
      interchange_control_standards_id: String @length(1) @default("U")
      interchange_control_version_number: String @length(5) @default("00401")
      interchange_control_number: String @length(9) @required
      acknowledgment_requested: String @length(1) @default("0")
      usage_indicator: String @length(1) @default("P")
      component_element_separator: String @length(1) @default(":")
    }

    functional_groups: List<FunctionalGroup] @required {
      gs_header: GS_Header {
        functional_identifier_code: String @length(2) @required
        application_sender_code: String @length(15) @required
        application_receiver_code: String @length(15) @required
        date: Date @format("CCYYMMDD") @required
        time: Time @format("HHMMSS") @required
        group_control_number: String @length(9) @required
        responsible_agency_code: String @length(2) @default("X")
        version_release_industry_identifier: String @length(12) @default("004010")
      }

      transaction_sets: List<TransactionSet] @required {
        st_header: ST_Header {
          transaction_set_identifier_code: String @length(3) @required
          transaction_set_control_number: String @length(9) @required
        }

        // 850 - Purchase Order
        purchase_order_850: Optional<PurchaseOrder850] {
          beg_segment: BEG_Segment {
            transaction_set_purpose_code: String @length(2) @required
            purchase_order_type_code: String @length(2) @required
            purchase_order_number: String @length(22) @required
            date: Optional<Date] @format("CCYYMMDD")
          }

          n1_segments: List<N1_Segment] {
            entity_identifier_code: String @length(2) @required
            name: Optional<String] @length(60)
            identification_code_qualifier: Optional<String] @length(2)
            identification_code: Optional<String] @length(80)
          }

          po1_segments: List<PO1_Segment] {
            assigned_identification: String @length(20) @required
            quantity_ordered: Decimal @precision(15,2) @required
            unit_of_measure: String @length(2) @required
            unit_price: Optional<Decimal] @precision(15,2)
            product_id_qualifier: Optional<String] @length(2)
            product_id: Optional<String] @length(48)
          }
        }

        // 855 - Purchase Order Acknowledgment
        purchase_order_ack_855: Optional<PurchaseOrderAck855] {
          bak_segment: BAK_Segment {
            transaction_set_purpose_code: String @length(2) @required
            acknowledgment_type: String @length(2) @required
            purchase_order_number: String @length(22) @required
            date: Date @format("CCYYMMDD") @required
          }

          ack_segments: List<ACK_Segment] {
            line_item_ack_code: String @length(2) @required
            quantity: Optional<Decimal] @precision(15,2)
            unit_of_measure: Optional<String] @length(2)
            date: Optional<Date] @format("CCYYMMDD")
          }
        }

        // 856 - Ship Notice/Manifest
        ship_notice_856: Optional<ShipNotice856] {
          bsn_segment: BSN_Segment {
            transaction_set_purpose_code: String @length(2) @required
            shipment_identification: String @length(30) @required
            date: Date @format("CCYYMMDD") @required
            time: Time @format("HHMMSS") @required
          }

          hl_segments: List<HL_Segment] {
            hierarchical_id_number: String @length(12) @required
            hierarchical_parent_id_number: Optional<String] @length(12)
            hierarchical_level_code: String @length(2) @required
            hierarchical_child_code: Optional<String] @length(1)
          }

          lin_segments: List<LIN_Segment] {
            assigned_identification: Optional<String] @length(20)
            product_id_qualifier: Optional<String] @length(2)
            product_id: Optional<String] @length(48)
            quantity: Optional<Decimal] @precision(15,2)
            unit_of_measure: Optional<String] @length(2)
          }
        }

        // 810 - Invoice
        invoice_810: Optional<Invoice810] {
          big_segment: BIG_Segment {
            date: Date @format("CCYYMMDD") @required
            invoice_number: String @length(22) @required
            purchase_order_number: Optional<String] @length(22)
            date2: Optional<Date] @format("CCYYMMDD")
          }

          it1_segments: List<IT1_Segment] {
            assigned_identification: Optional<String] @length(20)
            quantity_invoiced: Decimal @precision(15,2) @required
            unit_of_measure: String @length(2) @required
            unit_price: Decimal @precision(15,2) @required
            product_id_qualifier: Optional<String] @length(2)
            product_id: Optional<String] @length(48)
          }
        }

        st_trailer: ST_Trailer {
          number_of_included_segments: Int @required
          transaction_set_control_number: String @length(9) @required
        }
      }

      ge_trailer: GE_Trailer {
        number_of_transaction_sets_included: Int @required
        group_control_number: String @length(9) @required
      }
    }

    iea_trailer: IEA_Trailer {
      number_of_included_functional_groups: Int @required
      interchange_control_number: String @length(9) @required
    }
  }
} @standard("EDI_X12")
```

---

## 3. EDIFACT Schema

**定义3（EDIFACT Schema）**：

```text
EDIFACT_Schema = (Message, Segment_Group, Segment, Data_Element)
```

**形式化DSL定义**：

```dsl
schema EDIFACT {
  interchange: Interchange {
    unb_header: UNB_Header {
      syntax_identifier: String @length(4) @default("UNOA")
      syntax_version_number: String @length(1) @default("3")
      sender_identification: String @length(35) @required
      sender_partner_qualifier: String @length(4) @required
      recipient_identification: String @length(35) @required
      recipient_partner_qualifier: String @length(4) @required
      date_of_preparation: Date @format("CCYYMMDD") @required
      time_of_preparation: Time @format("HHMM") @required
      interchange_control_reference: String @length(14) @required
    }

    messages: List<Message] @required {
      unh_header: UNH_Header {
        message_reference_number: String @length(14) @required
        message_type: String @length(6) @required
        message_version_number: String @length(3) @required
        message_release_number: String @length(3) @required
        controlling_agency: String @length(2) @default("UN")
        association_assigned_code: Optional<String] @length(6)
      }

      // ORDERS - Purchase Order Message
      orders_message: Optional<ORDERS_Message] {
        bgm_segment: BGM_Segment {
          document_message_name: String @length(3) @required
          document_message_number: String @length(35) @required
          message_function_code: Optional<String] @length(3)
          response_type_code: Optional<String] @length(3)
        }

        dtm_segments: List<DTM_Segment] {
          date_time_period_qualifier: String @length(3) @required
          date_time_period: String @length(35) @required
          date_time_period_format_qualifier: String @length(3) @required
        }

        lin_segments: List<LIN_Segment] {
          line_item_number: Optional<String] @length(6)
          action_request_notification_code: Optional<String] @length(3)
          item_number_identification: Optional<ItemNumberIdentification] {
            item_number_type_code_qualifier: String @length(3) @required
            item_number: String @length(35) @required
          }
          item_description: Optional<String] @length(256)
        }

        qty_segments: List<QTY_Segment] {
          quantity_details: QuantityDetails {
            quantity_type_code_qualifier: String @length(3) @required
            quantity: Decimal @precision(15,2) @required
            measure_unit_code: Optional<String] @length(3)
          }
        }

        pri_segments: List<PRI_Segment] {
          price_information: PriceInformation {
            price_code_qualifier: String @length(3) @required
            price_amount: Decimal @precision(15,2) @required
            price_type_code: Optional<String] @length(3)
          }
        }
      }

      // DESADV - Despatch Advice Message
      desadv_message: Optional<DESADV_Message] {
        bgm_segment: BGM_Segment {
          document_message_name: String @length(3) @required
          document_message_number: String @length(35) @required
          message_function_code: Optional<String] @length(3)
        }

        dtm_segments: List<DTM_Segment] {
          date_time_period_qualifier: String @length(3) @required
          date_time_period: String @length(35) @required
          date_time_period_format_qualifier: String @length(3) @required
        }

        cps_segments: List<CPS_Segment] {
          hierarchical_id_number: String @length(12) @required
          hierarchical_parent_id: Optional<String] @length(12)
          packaging_level_code: String @length(3) @required
        }

        pac_segments: List<PAC_Segment] {
          number_of_packages: Optional<Int]
          package_type_description_code: Optional<String] @length(17)
        }

        lin_segments: List<LIN_Segment] {
          line_item_number: Optional<String] @length(6)
          item_number_identification: Optional<ItemNumberIdentification]
          item_description: Optional<String] @length(256)
        }

        qty_segments: List<QTY_Segment] {
          quantity_details: QuantityDetails {
            quantity_type_code_qualifier: String @length(3) @required
            quantity: Decimal @precision(15,2) @required
            measure_unit_code: Optional<String] @length(3)
          }
        }
      }

      // INVOIC - Invoice Message
      invoic_message: Optional<INVOIC_Message] {
        bgm_segment: BGM_Segment {
          document_message_name: String @length(3) @required
          document_message_number: String @length(35) @required
          message_function_code: Optional<String] @length(3)
        }

        dtm_segments: List<DTM_Segment] {
          date_time_period_qualifier: String @length(3) @required
          date_time_period: String @length(35) @required
          date_time_period_format_qualifier: String @length(3) @required
        }

        lin_segments: List<LIN_Segment] {
          line_item_number: Optional<String] @length(6)
          item_number_identification: Optional<ItemNumberIdentification]
          item_description: Optional<String] @length(256)
        }

        qty_segments: List<QTY_Segment] {
          quantity_details: QuantityDetails {
            quantity_type_code_qualifier: String @length(3) @required
            quantity: Decimal @precision(15,2) @required
            measure_unit_code: Optional<String] @length(3)
          }
        }

        moa_segments: List<MOA_Segment] {
          monetary_amount: MonetaryAmount {
            monetary_amount_type_code_qualifier: String @length(3) @required
            monetary_amount: Decimal @precision(15,2) @required
            currency_identification_code: Optional<String] @length(3)
          }
        }
      }

      unt_trailer: UNT_Trailer {
        number_of_segments_in_message: Int @required
        message_reference_number: String @length(14) @required
      }
    }

    unz_trailer: UNZ_Trailer {
      interchange_control_count: Int @required
      interchange_control_reference: String @length(14) @required
    }
  }
} @standard("EDIFACT")
```

---

## 4. 类型系统

**定义4（EDI数据类型）**：

```text
EDI_Data_Type = EDI_X12_Transaction | EDIFACT_Message | Segment | Element
```

**基本类型定义**：

```dsl
type Segment {
  segment_id: String @required
  elements: List<String] @required
  position: Int @required
}

type Element {
  element_id: String @required
  value: String @required
  format: Optional<String]
  position: Int @required
}

type TransactionSet {
  transaction_set_id: String @required
  segments: List<Segment] @required
}

type Message {
  message_type: String @required
  segments: List<Segment] @required
}
```

---

## 5. 约束规则

**约束1（EDI X12交易集完整性）**：

```text
∀ ts ∈ TransactionSet:
  has_st_header(ts)
  ∧ has_se_trailer(ts)
  → transaction_set_complete(ts)
```

**约束2（EDIFACT消息完整性）**：

```text
∀ msg ∈ Message:
  has_unh_header(msg)
  ∧ has_unt_trailer(msg)
  → message_complete(msg)
```

**约束3（段顺序约束）**：

```text
∀ seg1, seg2 ∈ Segment:
  seg1.position < seg2.position
  → segment_order_valid(seg1, seg2)
```

---

## 6. 转换函数

**函数1（EDI X12到EDIFACT转换）**：

```text
convert_x12_to_edifact: EDI_X12_Transaction → EDIFACT_Message
```

**函数2（EDIFACT到EDI X12转换）**：

```text
convert_edifact_to_x12: EDIFACT_Message → EDI_X12_Transaction
```

**函数3（EDI消息验证）**：

```text
validate_edi_message: EDI_Message → ValidationResult
```

---

## 7. 形式化定理

### 7.1 EDI消息完整性定理

**定理1（EDI消息完整性）**：

```text
∀ msg ∈ EDI_Message:
  has_header(msg)
  ∧ has_trailer(msg)
  ∧ segment_count_matches(msg)
  → message_complete(msg)
```

### 7.2 EDI转换保真性定理

**定理2（EDI转换保真性）**：

```text
∀ x12_msg ∈ EDI_X12_Transaction:
  edifact_msg = convert_x12_to_edifact(x12_msg)
  → data_preserved(x12_msg, edifact_msg)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
