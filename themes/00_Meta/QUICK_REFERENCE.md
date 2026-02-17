# Themes 快速参考手册

## 常用链接速查

### 国际标准

| 标准 | 链接 | 用途 |
|------|------|------|
| W3C RDF | https://www.w3.org/TR/rdf12-concepts/ | 知识表示 |
| W3C OWL | https://www.w3.org/TR/owl2-overview/ | 本体定义 |
| JSON-LD | https://www.w3.org/TR/json-ld11/ | 链接数据 |
| ISO 20022 | https://www.iso20022.org/ | 金融报文 |
| IEC 61131-3 | https://webstore.iec.ch/ | PLC编程 |
| OPC UA | https://opcfoundation.org/ | 工业通信 |

---

## Schema选型速查表

### 按场景选型

| 场景 | 推荐Schema | 备选 |
|------|-----------|------|
| Web API | OpenAPI 3.0 | AsyncAPI, GraphQL |
| 配置文件 | YAML + JSON Schema | TOML |
| 数据存储 | Avro | Parquet, ORC |
| 消息队列 | Protobuf | Avro, JSON |
| IoT设备 | MQTT + JSON | CoAP + CBOR |
| 金融支付 | ISO 20022 | FIX |
| 医疗健康 | FHIR | HL7 v2 |
| 工业控制 | OPC UA | Modbus |

### 按数据规模选型

| 规模 | 推荐格式 | 理由 |
|------|---------|------|
| < 1MB | JSON | 可读性好 |
| 1MB - 1GB | Avro/Parquet | 压缩+列存 |
| > 1GB | Protobuf + 分片 | 高效序列化 |

---

## 常用公式速查

### 信息论

```
信息熵: H(X) = -Σ P(x) log₂ P(x)
互信息: I(X;Y) = H(X) - H(X|Y)
KL散度: D_KL(P||Q) = Σ P(x) log(P(x)/Q(x))
信道容量: C = max I(X;Y)
```

### Schema转换质量

```
信息损失: L = H(S₁) - I(S₁;S₂)
转换效率: η = I(S₁;S₂) / H(S₁)
压缩比: R = H(S) / L(S)
```

---

## 代码片段速查

### JSON Schema 基础模板

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/schema/v1",
  "title": "Schema Title",
  "description": "Schema description",
  "version": "1.0.0",
  "type": "object",
  "properties": {},
  "required": []
}
```

### Python 验证代码

```python
from jsonschema import validate

def validate_data(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False
```

### 信息熵计算

```python
import math
from collections import Counter

def calculate_entropy(data):
    counts = Counter(data)
    total = len(data)
    entropy = 0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy
```

---

## 常见错误速查

### JSON Schema 错误

| 错误 | 原因 | 解决 |
|------|------|------|
| ValidationError | 数据不符合schema | 检查数据类型和约束 |
| SchemaError | Schema格式错误 | 验证schema语法 |
| RefResolutionError | $ref无法解析 | 检查引用路径 |

### 转换错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 信息损失过高 | 目标schema能力不足 | 扩展目标schema |
| 类型不匹配 | 类型映射错误 | 添加类型转换 |
| 循环引用 | 互相依赖 | 使用延迟加载 |

---

## 工具命令速查

### Schema验证工具

```bash
# 验证JSON Schema
python schema_validator.py -s schema.json -d data.json

# 质量检查
python schema_validator.py -s schema.json --quality-check

# 生成矩阵
python matrix_generator.py
```

### 常用命令

```bash
# 格式化JSON
cat data.json | python -m json.tool

# YAML转JSON
python -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(sys.stdin)))" < input.yaml

# 验证OpenAPI
swagger-codegen validate -i openapi.yaml
```

---

## 决策速查

### Schema选择决策树

```
1. 数据交换? → JSON/XML
2. API定义? → OpenAPI/AsyncAPI
3. 配置管理? → YAML+JSON Schema
4. 二进制高效? → Protobuf/Avro
5. 实时流? → Avro/JSON Lines
6. 工业场景? → OPC UA
7. 物联网? → MQTT+JSON
```

### 标准选择决策

```
金融行业: ISO 20022 > FIX > 自定义
医疗行业: FHIR > HL7 v2 > DICOM
工业场景: OPC UA > IEC 61850 > Modbus
物联网: MQTT > CoAP > HTTP
```

---

## 联系和支持

- **项目主页**: [INDEX.md](./INDEX.md)
- **完整文档**: [THEMES_COMPREHENSIVE_ANALYSIS.md](../THEMES_COMPREHENSIVE_ANALYSIS.md)
- **问题反馈**: DSL Schema研究团队

---

**最后更新**: 2026-02-17
