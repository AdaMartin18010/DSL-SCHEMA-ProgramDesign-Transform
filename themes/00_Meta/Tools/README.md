# Tools 工具目录

## 概述

本目录包含用于Schema转换、验证和分析的实用工具。

## 工具列表

### 1. schema_validator.py - Schema验证工具

**功能**:
- 验证JSON数据是否符合JSON Schema
- 详细错误报告
- Schema质量检查

**用法**:
```bash
# 基本验证
python schema_validator.py -s schema.json -d data.json

# 质量检查
python schema_validator.py -s schema.json --quality-check

# 详细输出
python schema_validator.py -s schema.json -d data.json -v
```

**输出示例**:
```
Quality Score: 85/100
Suggestions:
  - Add 'description' to improve documentation
  - Property 'name' lacks description
Validation PASSED
```

### 2. matrix_generator.py - 矩阵生成工具

**功能**:
- 自动生成主题属性矩阵
- 主题相似度分析
- 导出Markdown表格

**用法**:
```bash
python matrix_generator.py
```

**输出**: `matrix_output.md`

## 安装依赖

```bash
pip install jsonschema pyyaml
```

## 扩展开发

### 添加新工具

1. 在`Tools/`目录下创建Python文件
2. 添加命令行接口
3. 更新本README文档

### 工具模板

```python
#!/usr/bin/env python3
"""
工具描述
"""

import argparse

def main():
    parser = argparse.ArgumentParser(description='Tool description')
    parser.add_argument('--input', '-i', required=True, help='Input file')
    args = parser.parse_args()
    
    # 工具逻辑
    print(f"Processing {args.input}")

if __name__ == '__main__':
    main()
```

---

**维护者**: DSL Schema研究团队
