# 数字人文Schema转换体系

## 📑 目录

- [数字人文Schema转换体系](#数字人文schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 转换方向](#2-转换方向)
  - [3. TEI转换](#3-tei转换)
  - [4. IIIF转换](#4-iiif转换)
  - [5. PostgreSQL存储](#5-postgresql存储)
  - [6. 转换工具](#6-转换工具)
  - [7. 转换验证](#7-转换验证)

---

## 1. 转换体系概述

数字人文Schema转换体系支持**数字人文数据到各种格式的转换**，包括TEI、IIIF、PostgreSQL等格式。

**转换目标**：

- TEI XML格式
- IIIF Manifest格式
- PostgreSQL数据库
- JSON格式

---

## 2. 转换方向

### 2.1 转换矩阵

| 转换方向 | 源格式 | 目标格式 | 转换复杂度 | 工具支持 | 数据完整性 |
|---------|--------|----------|------------|----------|------------|
| **DH → TEI** | Digital_Humanities_Schema | TEI XML | ⭐⭐⭐ | ✅ 良好 | 高 |
| **DH → IIIF** | Digital_Humanities_Schema | IIIF Manifest | ⭐⭐⭐ | ✅ 良好 | 高 |
| **DH → PostgreSQL** | Digital_Humanities_Schema | SQL DDL | ⭐⭐⭐ | ✅ 良好 | 高 |
| **DH → JSON** | Digital_Humanities_Schema | JSON Schema | ⭐⭐ | ✅ 良好 | 高 |

---

## 3. TEI转换

### 3.1 Digital_Humanities → TEI转换

**转换函数**：

```text
to_tei: Text_Data → TEI_XML
```

**转换示例**：

**输入（Digital_Humanities_Schema）**：

```dsl
text_data Literary_Text {
  id: "text_001"
  content: {
    text: "昔人已乘黄鹤去，此地空余黄鹤楼。"
    language: zh
  }
  annotation: {
    author: "崔颢"
    date: "唐代"
  }
}
```

**输出（TEI XML）**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>黄鹤楼</title>
        <author>崔颢</author>
      </titleStmt>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
      <p>昔人已乘黄鹤去，此地空余黄鹤楼。</p>
    </body>
  </text>
</TEI>
```

---

## 4. IIIF转换

### 4.1 Digital_Humanities → IIIF转换

**转换函数**：

```text
to_iiif: Image_Data → IIIF_Manifest
```

**转换示例**：

```json
{
  "@context": "http://iiif.io/api/presentation/3/context.json",
  "id": "https://example.org/manifest.json",
  "type": "Manifest",
  "label": {"en": ["Manuscript Image"]},
  "items": [{
    "id": "https://example.org/canvas/1",
    "type": "Canvas",
    "width": 2000,
    "height": 3000,
    "items": [{
      "id": "https://example.org/image/1",
      "type": "Image",
      "resource": {
        "id": "https://example.org/image.jpg",
        "type": "Image",
        "format": "image/jpeg",
        "width": 2000,
        "height": 3000,
        "service": [{
          "@id": "https://example.org/image-service",
          "@type": "ImageService2",
          "profile": "http://iiif.io/api/image/2/level2.json"
        }]
      }
    }]
  }]
}
```

---

## 5. PostgreSQL存储

### 5.1 数据库Schema设计

```sql
CREATE TABLE text_data (
    id VARCHAR(50) PRIMARY KEY,
    text_type VARCHAR(50),
    content TEXT,
    language VARCHAR(10),
    annotation JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE image_data (
    id VARCHAR(50) PRIMARY KEY,
    image_type VARCHAR(50),
    url TEXT,
    format VARCHAR(10),
    width INTEGER,
    height INTEGER,
    metadata JSONB,
    annotation JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE spatiotemporal_data (
    id VARCHAR(50) PRIMARY KEY,
    time_info JSONB,
    space_info JSONB,
    event JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. 转换工具

### 6.1 开源工具

- **TEI Tools**：TEI处理工具
- **IIIF Tools**：IIIF工具集
- **Digital Humanities Tools**：数字人文工具

---

## 7. 转换验证

### 7.1 TEI验证

**验证方法**：

1. 验证TEI XML语法
2. 验证TEI Schema合规性
3. 验证文本结构完整性

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
