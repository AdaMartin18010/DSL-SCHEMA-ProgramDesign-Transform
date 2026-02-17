# DSL Schema API 完整参考
## DSL Schema API Complete Reference

**版本**: 2.2.0  
**基础URL**: `https://api.dsl-schema.io/v2`

---

## 认证

所有API请求需要包含API Key：
```
Authorization: Bearer YOUR_API_KEY
```

---

## 端点列表

### 1. Schema验证

#### POST /schemas/validate
验证Schema结构和合规性。

**请求体**:
```json
{
  "schema": {...},
  "schemaType": "json_schema",
  "standards": ["iso20022", "fhir"],
  "options": {
    "strictMode": true
  }
}
```

**响应**:
```json
{
  "valid": true,
  "validationId": "uuid",
  "errors": [],
  "warnings": [],
  "compliance": {
    "iso20022": {"compliant": true, "score": 95}
  }
}
```

### 2. 矩阵生成

#### POST /matrix/generate
生成概念-属性矩阵。

**请求体**:
```json
{
  "themes": ["01_Industrial_Automation", "06_Financial_Services"],
  "dimensions": ["theory", "application", "standards"],
  "includeSimilarity": true
}
```

### 3. 模型关联分析

#### POST /relationships/analyze
分析模型间的关系。

**请求体**:
```json
{
  "sourceModel": {...},
  "targetModel": {...},
  "analysisType": "similarity"
}
```

### 4. 层次映射

#### POST /mapping/transform
执行层次间模型转换。

**请求体**:
```json
{
  "model": {...},
  "sourceLevel": "L2",
  "targetLevel": "L4"
}
```

### 5. Schema差异比较

#### POST /diff/compare
比较两个Schema的差异。

**请求体**:
```json
{
  "source": {...},
  "target": {...},
  "options": {
    "ignoreDescriptions": false
  }
}
```

---

## 错误代码

| 代码 | 描述 |
|------|------|
| 400 | 无效请求 |
| 401 | 未授权 |
| 422 | 验证失败 |
| 429 | 请求过多 |
| 500 | 服务器错误 |

---

**最后更新**: 2026-02-17
