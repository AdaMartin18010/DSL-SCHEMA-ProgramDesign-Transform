# 数字人文Schema形式化定义

## 📑 目录

- [数字人文Schema形式化定义](#数字人文schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
    - [1.1 基本定义](#11-基本定义)
    - [1.2 数字人文要素](#12-数字人文要素)
  - [2. 文本数据Schema形式化定义](#2-文本数据schema形式化定义)
    - [2.1 文本数据定义](#21-文本数据定义)
    - [2.2 文本标注定义](#22-文本标注定义)
  - [3. 图像数据Schema形式化定义](#3-图像数据schema形式化定义)
    - [3.1 图像数据定义](#31-图像数据定义)
    - [3.2 图像元数据定义](#32-图像元数据定义)
  - [4. 时空数据Schema形式化定义](#4-时空数据schema形式化定义)
    - [4.1 时空数据定义](#41-时空数据定义)
    - [4.2 时空关系定义](#42-时空关系定义)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)

---

## 1. 形式化模型

### 1.1 基本定义

设 `Digital_Humanities_Schema` 为数字人文Schema的集合，
`Text_Data` 为文本数据的集合，
`Image_Data` 为图像数据的集合。

**定义1（数字人文Schema）**：

数字人文Schema是一个四元组：

```text
Digital_Humanities_Schema = (Text_Data, Image_Data, Spatiotemporal_Data, Metadata)
```

其中：

- `Text_Data`：文本数据Schema
- `Image_Data`：图像数据Schema
- `Spatiotemporal_Data`：时空数据Schema
- `Metadata`：元数据Schema

### 1.2 数字人文要素

**定义2（数字人文要素组合）**：

数字人文要素组合运算 `⊕` 定义为：

```text
Text_Data ⊕ Image_Data ⊕ Spatiotemporal_Data ⊕ Metadata = {
  (t, i, s, m) | t ∈ Text_Data, i ∈ Image_Data,
                s ∈ Spatiotemporal_Data, m ∈ Metadata,
                dh_constraints(t, i, s, m)
}
```

---

## 2. 文本数据Schema形式化定义

### 2.1 文本数据定义

**定义3（文本数据Schema）**：

```text
Text_Data_Schema = (ID, Content, Structure, Annotation)
```

其中：

- `ID`：文本标识符
- `Content`：文本内容
- `Structure`：文本结构
- `Annotation`：文本标注

**形式化DSL定义**：

```dsl
schema Text_Data {
  id: String @unique
  text_type: Text_Type @enum(
    Literary_Text,
    Historical_Document,
    Manuscript,
    Inscription
  )
  content: Text_Content {
    text: String
    language: Language @enum(zh, en, la, gr, ...)
    encoding: Encoding @default("UTF-8")
    structure: Text_Structure {
      paragraphs: Paragraph[]
      sentences: Sentence[]
      words: Word[]
    }
  }

  annotation: Text_Annotation {
    author: Optional[String]
    date: Optional[Date]
    source: Optional[String]
    semantic_annotation: Semantic_Annotation[] {
      entity: Entity
      entity_type: Entity_Type @enum(Person, Place, Event, Concept)
      start: Integer
      end: Integer
    }
  }

  metadata: Text_Metadata {
    title: Optional[String]
    genre: Optional[Genre]
    period: Optional[Period]
    provenance: Optional[String]
  }
}
```

---

## 3. 图像数据Schema形式化定义

### 3.1 图像数据定义

**定义4（图像数据Schema）**：

```text
Image_Data_Schema = (ID, Image, Metadata, Annotation)
```

其中：

- `ID`：图像标识符
- `Image`：图像数据
- `Metadata`：图像元数据
- `Annotation`：图像标注

**形式化DSL定义**：

```dsl
schema Image_Data {
  id: String @unique
  image_type: Image_Type @enum(
    Painting,
    Photograph,
    Manuscript_Image,
    Artifact_Image
  )
  image: Image_Content {
    url: String
    format: Image_Format @enum(PNG, JPEG, TIFF, WebP)
    width: Integer
    height: Integer
    resolution: Float @unit("dpi")
    color_space: Color_Space @enum(RGB, CMYK, Grayscale)
  }

  metadata: Image_Metadata {
    creator: Optional[String]
    date: Optional[Date]
    source: Optional[String]
    copyright: Optional[String]
    iiif_manifest: Optional[String]  # IIIF支持
  }

  annotation: Image_Annotation {
    regions: Region[] {
      region_id: String
      coordinates: Bounding_Box {
        x: Integer
        y: Integer
        width: Integer
        height: Integer
      }
      label: String
      description: Optional[String]
    }
  }
}
```

---

## 4. 时空数据Schema形式化定义

### 4.1 时空数据定义

**定义5（时空数据Schema）**：

```text
Spatiotemporal_Data_Schema = (Time, Space, Event, Relationship)
```

其中：

- `Time`：时间信息
- `Space`：空间信息
- `Event`：事件信息
- `Relationship`：时空关系

**形式化DSL定义**：

```dsl
schema Spatiotemporal_Data {
  id: String @unique
  time: Time_Info {
    time_point: Optional[Timestamp]
    time_interval: Optional[Time_Interval] {
      start: Timestamp
      end: Timestamp
    }
    time_period: Optional[Time_Period] @enum(
      Ancient,
      Medieval,
      Modern,
      Contemporary
    )
    calendar: Optional[Calendar] @enum(Gregorian, Julian, Lunar)
  }

  space: Space_Info {
    location: Location {
      latitude: Float @range(-90, 90)
      longitude: Float @range(-180, 180)
      altitude: Optional[Float]
    }
    place_name: Optional[String]
    administrative_region: Optional[Administrative_Region] {
      country: String
      province: Optional[String]
      city: Optional[String]
    }
    coordinate_system: String @default("WGS84")
  }

  event: Optional[Event] {
    event_type: Event_Type
    event_description: String
    participants: String[]
  }

  relationship: Spatiotemporal_Relationship {
    temporal_relations: Temporal_Relation[] @enum(
      before, after, during, overlaps, meets
    )
    spatial_relations: Spatial_Relation[] @enum(
      near, far, inside, outside, adjacent
    )
  }
}
```

---

## 5. 类型系统

```dsl
type Text_Data: Object {
  content: Text_Content
  annotation: Text_Annotation
  metadata: Text_Metadata
}

type Image_Data: Object {
  image: Image_Content
  metadata: Image_Metadata
  annotation: Image_Annotation
}

type Spatiotemporal_Data: Object {
  time: Time_Info
  space: Space_Info
  event: Optional[Event]
}
```

---

## 6. 约束规则

### 6.1 文本完整性约束

**定义6（文本完整性）**：

```text
text_complete(text) ⟺
  text.content.text.length > 0 ∧
  text.content.language ∈ valid_languages
```

### 6.2 时空一致性约束

**定义7（时空一致性）**：

```text
spatiotemporal_consistent(data) ⟺
  data.time.time_point ≠ null ∨
  data.time.time_interval ≠ null ∨
  data.space.location ≠ null
```

---

## 7. 转换函数

### 7.1 TEI转换

**定义8（TEI转换函数）**：

```text
to_tei: Text_Data → TEI_XML
```

### 7.2 IIIF转换

**定义9（IIIF转换函数）**：

```text
to_iiif: Image_Data → IIIF_Manifest
```

---

## 8. 形式化定理

### 8.1 文本标注一致性定理

**定理1（文本标注一致性）**：

对于文本标注，如果：

1. 标注规则一致
2. 标注覆盖完整
3. 标注验证通过

则标注结果满足：

```text
∀annotation ∈ text.annotations:
  annotation.start < annotation.end ≤ text.content.length
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
