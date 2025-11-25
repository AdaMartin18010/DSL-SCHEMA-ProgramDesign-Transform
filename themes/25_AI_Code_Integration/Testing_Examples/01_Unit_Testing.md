# 单元测试示例

## 📑 目录

- [单元测试示例](#单元测试示例)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 类型系统转换测试](#2-类型系统转换测试)
  - [3. Schema转换测试](#3-schema转换测试)
  - [4. 多维模型转换测试](#4-多维模型转换测试)
  - [5. 行业Schema转换测试](#5-行业schema转换测试)

---

## 1. 概述

本文档提供Schema转换相关的单元测试示例，包括类型系统转换、Schema转换、多维模型转换和行业Schema转换的测试用例。

**测试框架**：pytest

**覆盖率目标**：≥80%

---

## 2. 类型系统转换测试

### 2.1 TypeSafeConverter测试

```python
import pytest
from typing import TypeVar, Generic
from programming_language_type_system import TypeSafeConverter, StringToIntConverter, DictToJSONConverter

class TestTypeSafeConverter:
    """TypeSafeConverter单元测试"""

    def test_string_to_int_conversion_success(self):
        """测试字符串到整数转换成功"""
        converter = StringToIntConverter()
        result = converter.convert("123")
        assert result == 123
        assert isinstance(result, int)

    def test_string_to_int_conversion_failure(self):
        """测试字符串到整数转换失败"""
        converter = StringToIntConverter()
        with pytest.raises(ValueError, match="无法将字符串"):
            converter.convert("abc")

    def test_string_to_int_conversion_empty(self):
        """测试空字符串转换"""
        converter = StringToIntConverter()
        with pytest.raises(ValueError):
            converter.convert("")

    def test_dict_to_json_conversion_success(self):
        """测试字典到JSON转换成功"""
        converter = DictToJSONConverter()
        source = {"name": "John", "age": 30}
        result = converter.convert(source)
        assert isinstance(result, str)
        assert "name" in result
        assert "John" in result

    def test_dict_to_json_conversion_invalid(self):
        """测试无效字典转换"""
        converter = DictToJSONConverter()
        # 包含不可序列化的对象
        source = {"func": lambda x: x}
        with pytest.raises(ValueError):
            converter.convert(source)
```

### 2.2 TypeInferenceEngine测试

```python
import pytest
from programming_language_type_system import TypeInferenceEngine, TypeInferenceResult

class TestTypeInferenceEngine:
    """TypeInferenceEngine单元测试"""

    def test_infer_int_type(self):
        """测试推断整数类型"""
        engine = TypeInferenceEngine()
        result = engine.infer_type(42)
        assert result.inferred_type == int
        assert result.confidence == 1.0
        assert len(result.validation_errors) == 0

    def test_infer_string_type(self):
        """测试推断字符串类型"""
        engine = TypeInferenceEngine()
        result = engine.infer_type("hello")
        assert result.inferred_type == str
        assert result.confidence == 1.0

    def test_infer_list_type(self):
        """测试推断列表类型"""
        engine = TypeInferenceEngine()
        result = engine.infer_type([1, 2, 3])
        assert result.inferred_type == list
        assert result.confidence >= 0.9

    def test_infer_dict_type(self):
        """测试推断字典类型"""
        engine = TypeInferenceEngine()
        result = engine.infer_type({"key": "value"})
        assert result.inferred_type == dict
        assert result.confidence == 1.0

    def test_validate_type_success(self):
        """测试类型验证成功"""
        engine = TypeInferenceEngine()
        errors = engine.validate_type(42, int)
        assert len(errors) == 0

    def test_validate_type_failure(self):
        """测试类型验证失败"""
        engine = TypeInferenceEngine()
        errors = engine.validate_type("42", int)
        assert len(errors) > 0
```

---

## 3. Schema转换测试

### 3.1 OpenAPI到AsyncAPI转换测试

```python
import pytest
from domain_language_conversion import OpenAPIToAsyncAPIConverter

class TestOpenAPIToAsyncAPIConverter:
    """OpenAPI到AsyncAPI转换器测试"""

    @pytest.fixture
    def sample_openapi(self):
        """示例OpenAPI规范"""
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/users": {
                    "post": {
                        "operationId": "createUser",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    def test_convert_basic_openapi(self, sample_openapi):
        """测试基本OpenAPI转换"""
        converter = OpenAPIToAsyncAPIConverter()
        result = converter.convert(sample_openapi)

        assert "asyncapi" in result
        assert result["asyncapi"] == "2.6.0"
        assert "info" in result
        assert result["info"]["title"] == "Test API"
        assert "channels" in result

    def test_convert_paths_to_channels(self, sample_openapi):
        """测试路径到通道转换"""
        converter = OpenAPIToAsyncAPIConverter()
        result = converter.convert(sample_openapi)

        assert "users" in result["channels"]
        assert "publish" in result["channels"]["users"]

    def test_convert_empty_openapi(self):
        """测试空OpenAPI转换"""
        converter = OpenAPIToAsyncAPIConverter()
        empty_spec = {"openapi": "3.1.0", "info": {}}
        result = converter.convert(empty_spec)
        assert result is not None
```

### 3.2 DSL转换测试

```python
import pytest
from dsl_transformation import ASTTransformer, Node, Schema

class TestASTTransformer:
    """AST转换器测试"""

    @pytest.fixture
    def sample_node(self):
        """示例节点"""
        return Node(
            name="test",
            node_type="object",
            attributes={"key": "value"},
            children=[]
        )

    @pytest.fixture
    def target_schema(self):
        """目标Schema"""
        schema = Schema()
        schema.type_mapping = {"object": "record"}
        schema.attribute_mapping = {"key": "field"}
        return schema

    def test_transform_node(self, sample_node, target_schema):
        """测试节点转换"""
        transformer = ASTTransformer()
        result = transformer.transform_node(sample_node, target_schema)

        assert result.name == "test"
        assert result.node_type == "record"
        assert "field" in result.attributes

    def test_transform_node_with_children(self, target_schema):
        """测试带子节点的转换"""
        parent = Node(
            name="parent",
            node_type="object",
            attributes={},
            children=[
                Node(name="child", node_type="string", attributes={}, children=[])
            ]
        )
        transformer = ASTTransformer()
        result = transformer.transform_node(parent, target_schema)

        assert len(result.children) == 1
        assert result.children[0].node_type == "string"
```

---

## 4. 多维模型转换测试

### 4.1 时间维度转换测试

```python
import pytest
from datetime import datetime
from multi_dimensional_model_conversion import TimeDimensionConverter

class TestTimeDimensionConverter:
    """时间维度转换器测试"""

    def test_convert_timezone(self):
        """测试时区转换"""
        converter = TimeDimensionConverter()
        utc_time = datetime(2025, 1, 21, 12, 0, 0)
        beijing_time = converter.convert_timezone(utc_time, "Asia/Shanghai")

        assert beijing_time.hour == 20  # UTC+8

    def test_convert_time_format(self):
        """测试时间格式转换"""
        converter = TimeDimensionConverter()
        iso_time = "2025-01-21T12:00:00Z"
        unix_timestamp = converter.convert_to_unix_timestamp(iso_time)

        assert isinstance(unix_timestamp, int)
        assert unix_timestamp > 0

    def test_convert_time_roundtrip(self):
        """测试时间转换往返"""
        converter = TimeDimensionConverter()
        original_time = datetime(2025, 1, 21, 12, 0, 0)

        converted = converter.convert_timezone(original_time, "Asia/Shanghai")
        back_converted = converter.convert_timezone(converted, "UTC")

        assert back_converted.hour == original_time.hour
```

### 4.2 空间维度转换测试

```python
import pytest
from multi_dimensional_model_conversion import SpatialDimensionConverter

class TestSpatialDimensionConverter:
    """空间维度转换器测试"""

    def test_wgs84_to_utm(self):
        """测试WGS84到UTM转换"""
        converter = SpatialDimensionConverter()
        lat, lon = 39.9042, 116.4074  # 北京坐标
        zone = 50
        x, y = converter.wgs84_to_utm(lat, lon, zone)

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert x > 0
        assert y > 0

    def test_utm_to_wgs84(self):
        """测试UTM到WGS84转换"""
        converter = SpatialDimensionConverter()
        x, y = 500000.0, 4410000.0
        zone = 50
        lat, lon = converter.utm_to_wgs84(x, y, zone)

        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180

    def test_coordinate_roundtrip(self):
        """测试坐标转换往返"""
        converter = SpatialDimensionConverter()
        original_lat, original_lon = 39.9042, 116.4074
        zone = 50

        x, y = converter.wgs84_to_utm(original_lat, original_lon, zone)
        lat, lon = converter.utm_to_wgs84(x, y, zone)

        assert abs(lat - original_lat) < 0.0001
        assert abs(lon - original_lon) < 0.0001
```

---

## 5. 行业Schema转换测试

### 5.1 EDI到GS1转换测试

```python
import pytest
from industry_schema_analysis import EDIToGS1Converter

class TestEDIToGS1Converter:
    """EDI到GS1转换器测试"""

    @pytest.fixture
    def sample_edi_message(self):
        """示例EDI消息"""
        return """
        UNA:+.? '
        UNB+UNOA:2+1234567890123:14+9876543210987:14+250121:1200+12345'
        UNH+1+ORDERS:D:96A:UN'
        BGM+220+12345+9'
        """

    def test_convert_edi_to_gs1(self, sample_edi_message):
        """测试EDI到GS1转换"""
        converter = EDIToGS1Converter()
        result = converter.convert(sample_edi_message)

        assert "gtin" in result or "gln" in result or "sscc" in result

    def test_parse_edi_message(self, sample_edi_message):
        """测试EDI消息解析"""
        converter = EDIToGS1Converter()
        edi_data = converter.parse_edi(sample_edi_message)

        assert edi_data is not None
        assert isinstance(edi_data, dict)
```

### 5.2 HL7到FHIR转换测试

```python
import pytest
from industry_schema_analysis import HL7ToFHIRConverter

class TestHL7ToFHIRConverter:
    """HL7到FHIR转换器测试"""

    @pytest.fixture
    def sample_hl7_message(self):
        """示例HL7消息"""
        return """
        MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|20250121120000||ADT^A01|12345|P|2.5
        PID|1||123456^^^MRN||Doe^John||19900101|M|||123 Main St^^City^ST^12345
        """

    def test_convert_patient(self, sample_hl7_message):
        """测试患者信息转换"""
        converter = HL7ToFHIRConverter()
        result = converter.convert_patient(sample_hl7_message)

        assert result["resourceType"] == "Patient"
        assert "id" in result
        assert "name" in result

    def test_convert_observation(self, sample_hl7_message):
        """测试观察结果转换"""
        converter = HL7ToFHIRConverter()
        # 添加OBX段
        hl7_with_obx = sample_hl7_message + "\nOBX|1|NM|8480-6^Systolic BP^LN||120|mm[Hg]"
        result = converter.convert_observation(hl7_with_obx)

        assert result["resourceType"] == "Observation"
        assert "code" in result
        assert "valueQuantity" in result
```

---

## 6. 测试运行

### 6.1 运行所有测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_type_system.py

# 运行特定测试类
pytest tests/test_type_system.py::TestTypeSafeConverter

# 运行特定测试方法
pytest tests/test_type_system.py::TestTypeSafeConverter::test_string_to_int_conversion_success
```

### 6.2 生成覆盖率报告

```bash
# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 6.3 持续集成配置

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

**参考文档**：

- `02_Integration_Testing.md` - 集成测试示例
- `03_Performance_Testing.md` - 性能测试示例
- `04_Test_Coverage.md` - 测试覆盖率报告

**创建时间**：2025-01-21
**最后更新**：2025-01-21
