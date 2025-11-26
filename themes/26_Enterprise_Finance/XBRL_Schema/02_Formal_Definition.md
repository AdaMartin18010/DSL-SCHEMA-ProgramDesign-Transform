# XBRL Schema形式化定义

## 📑 目录

- [XBRL Schema形式化定义](#xbrl-schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. XBRL分类标准Schema](#2-xbrl分类标准schema)
  - [3. XBRL实例文档Schema](#3-xbrl实例文档schema)
  - [4. XBRL链接库Schema](#4-xbrl链接库schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)

---

## 1. 形式化模型

**定义1（XBRL Schema）**：
XBRL Schema是一个三元组：

```text
XBRL_Schema = (Taxonomy, Instance_Document, Linkbases)
```

其中：

- `Taxonomy`：XBRL分类标准Schema
- `Instance_Document`：XBRL实例文档Schema
- `Linkbases`：XBRL链接库Schema

---

## 2. XBRL分类标准Schema

**定义2（XBRL分类标准Schema）**：

```text
Taxonomy_Schema = (Taxonomy_Element, Taxonomy_Linkbase,
                  Taxonomy_Label, Taxonomy_Reference)
```

**形式化DSL定义**：

```dsl
schema Taxonomy {
  taxonomy_elements: List<TaxonomyElement> {
    element_id: String @required @unique
    element_name: String @required
    element_type: Enum { Item, Tuple } @required
    data_type: Enum { Monetary, Decimal, String, Date } @required
    period_type: Enum { Instant, Duration } @required
    balance_type: Enum { Debit, Credit } @optional
    substitution_group: String @optional
  }

  taxonomy_linkbases: List<TaxonomyLinkbase> {
    linkbase_type: Enum { Label, Reference, Calculation, Definition, Presentation } @required
    linkbase_location: String @required
    linkbase_role: String @optional
  }

  taxonomy_labels: List<TaxonomyLabel> {
    label_id: String @required @unique
    element_id: String @required
    label_text: String @required
    label_language: String @required @default("en")
    label_role: String @required @default("http://www.xbrl.org/role/label")
  }

  taxonomy_references: List<TaxonomyReference> {
    reference_id: String @required @unique
    element_id: String @required
    reference_standard: String @required
    reference_section: String @required
    reference_paragraph: String @optional
  }
} @standard("XBRL 2.1")
```

---

## 3. XBRL实例文档Schema

**定义3（XBRL实例文档Schema）**：

```text
Instance_Document_Schema = (Context_Element, Unit_Element,
                           Fact_Element, Footnote_Element)
```

**形式化DSL定义**：

```dsl
schema InstanceDocument {
  context_elements: List<ContextElement> {
    context_id: String @required @unique
    entity_identifier: String @required
    entity_scheme: String @required
    period_type: Enum { Instant, Duration } @required
    period_start: Optional<Date>
    period_end: Optional<Date>
    scenario: Optional<String>
  }

  unit_elements: List<UnitElement> {
    unit_id: String @required @unique
    measure_type: Enum { Monetary, Share, Pure } @required
    measure: String @required
    numerator_measures: List<String> @optional
    denominator_measures: List<String> @optional
  }

  fact_elements: List<FactElement> {
    fact_id: String @required @unique
    element_id: String @required
    context_ref: String @required
    unit_ref: String @required
    fact_value: String @required
    decimals: String @optional
    precision: String @optional
  }

  footnote_elements: List<FootnoteElement> {
    footnote_id: String @required @unique
    footnote_text: String @required
    footnote_language: String @required @default("en")
    fact_refs: List<String> @required
  }
} @standard("XBRL 2.1")
```

---

## 4. XBRL链接库Schema

**定义4（XBRL链接库Schema）**：

```text
Linkbases_Schema = (Label_Linkbase, Reference_Linkbase,
                   Calculation_Linkbase, Definition_Linkbase,
                   Presentation_Linkbase)
```

**形式化DSL定义**：

```dsl
schema Linkbases {
  label_linkbase: LabelLinkbase {
    labels: List<LabelArc> {
      from_element: String @required
      to_label: String @required
      arc_role: String @required @default("http://www.xbrl.org/2003/arcrole/concept-label")
      label_role: String @required
      label_language: String @required
    }
  }

  reference_linkbase: ReferenceLinkbase {
    references: List<ReferenceArc> {
      from_element: String @required
      to_reference: String @required
      arc_role: String @required @default("http://www.xbrl.org/2003/arcrole/concept-reference")
    }
  }

  calculation_linkbase: CalculationLinkbase {
    calculations: List<CalculationArc> {
      from_element: String @required
      to_element: String @required
      arc_role: String @required @default("http://www.xbrl.org/2003/arcrole/summation-item")
      weight: Decimal @required
      order: Int @required
    }
  }

  definition_linkbase: DefinitionLinkbase {
    definitions: List<DefinitionArc> {
      from_element: String @required
      to_element: String @required
      arc_role: String @required
      order: Int @required
    }
  }

  presentation_linkbase: PresentationLinkbase {
    presentations: List<PresentationArc> {
      from_element: String @required
      to_element: String @required
      arc_role: String @required @default("http://www.xbrl.org/2003/arcrole/parent-child")
      order: Int @required
      preferred_label: String @optional
    }
  }
} @standard("XBRL 2.1")
```

---

## 5. 类型系统

**定义5（类型系统）**：

```text
Type_System = {String, Integer, Decimal, Boolean, DateTime, Date,
               Enum, List, Map, Object, Optional}
```

---

## 6. 约束规则

**定义6（约束规则）**：

1. **唯一性约束**：`element_id`、`context_id`、`unit_id`等必须唯一
2. **必填约束**：标记为`@required`的字段必须提供值
3. **引用约束**：`context_ref`、`unit_ref`必须引用有效的上下文和单位
4. **计算约束**：计算链接库中的权重和必须正确
5. **展示约束**：展示链接库中的顺序必须正确

---

## 7. 转换函数

**定义7（转换函数）**：

```text
转换函数集合 = {
  convert_accounting_to_xbrl: Accounting_Schema → XBRL_Schema,
  convert_financial_report_to_xbrl: Financial_Reporting_Schema → XBRL_Schema,
  convert_xbrl_to_database: XBRL_Schema → PostgreSQL_Schema
}
```

---

## 8. 形式化定理

### 8.1 XBRL实例文档完整性定理

**定理1（XBRL实例文档完整性）**：
XBRL实例文档中的所有事实元素必须引用有效的上下文和单位：

```text
∀fact ∈ Fact_Elements: ∃context ∈ Context_Elements ∧ ∃unit ∈ Unit_Elements
                       such that fact.context_ref == context.context_id
                       fact.unit_ref == unit.unit_id
```

### 8.2 XBRL计算链接库一致性定理

**定理2（XBRL计算链接库一致性）**：
计算链接库中的权重和必须等于1或-1：

```text
∀calculation ∈ Calculation_Linkbase: |∑calculation.weight| == 1
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
