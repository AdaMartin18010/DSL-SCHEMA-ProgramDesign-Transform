# DSL转换方案实践案例

## 📑 目录

- [DSL转换方案实践案例](#dsl转换方案实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：OpenAPI到AsyncAPI转换](#2-案例1openapi到asyncapi转换)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 实现代码](#22-实现代码)
  - [3. 案例2：EDIFACT到XML转换](#3-案例2edifact到xml转换)
    - [3.1 场景描述](#31-场景描述)

---

## 1. 案例概述

本文档提供DSL转换方案在实际应用中的实践案例。

---

## 2. 案例1：OpenAPI到AsyncAPI转换

### 2.1 场景描述

**业务背景**：
将RESTful API转换为异步消息队列接口。

**解决方案**：
使用AST转换算法，将OpenAPI规范转换为AsyncAPI规范。

### 2.2 实现代码

```python
class OpenAPIToAsyncAPIConverter:
    """OpenAPI到AsyncAPI转换器"""

    def convert(self, openapi_spec: Dict) -> Dict:
        """转换OpenAPI规范为AsyncAPI规范"""
        asyncapi_spec = {
            "asyncapi": "2.6.0",
            "info": openapi_spec["info"],
            "channels": {}
        }

        # 转换路径为通道
        for path, methods in openapi_spec.get("paths", {}).items():
            channel_name = path.replace("/", ".")
            asyncapi_spec["channels"][channel_name] = {
                "publish": self._convert_method(methods.get("post", {})),
                "subscribe": self._convert_method(methods.get("get", {}))
            }

        return asyncapi_spec
```

---

## 3. 案例2：EDIFACT到XML转换

### 3.1 场景描述

**业务背景**：
将EDIFACT消息转换为XML格式。

**解决方案**：
使用语法树转换算法，将EDIFACT段转换为XML元素。

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Transformation_Algorithms.md` - 转换算法
- `03_Transformation_Rules.md` - 转换规则
- `04_Transformation_Tools.md` - 转换工具

**创建时间**：2025-01-21
**最后更新**：2025-01-21
