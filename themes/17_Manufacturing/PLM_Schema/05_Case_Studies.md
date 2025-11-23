# PLM Schema实践案例

## 📑 目录

- [PLM Schema实践案例](#plm-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：产品设计管理系统](#2-案例1产品设计管理系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：变更管理系统](#3-案例2变更管理系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：BOM管理系统](#4-案例3bom管理系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：STEP文件解析和CAD集成](#5-案例4step文件解析和cad集成)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：PLM数据分析和报表](#6-案例5plm数据分析和报表)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供PLM Schema在实际应用中的实践案例。

---

## 2. 案例1：产品设计管理系统

### 2.1 场景描述

**业务背景**：
制造企业需要管理产品设计数据，包括CAD模型、
设计文档、版本控制等，确保设计数据的一致性和
可追溯性。

**技术挑战**：

- 需要管理多种CAD格式文件
- 需要版本控制
- 需要设计文档管理
- 需要设计状态跟踪

**解决方案**：
使用CADFileParser解析CAD文件，使用PLMStorage
存储产品设计数据，实现完整的产品设计管理。

### 2.2 Schema定义

**产品设计管理Schema**：

```json
{
  "product_design": {
    "product_id": "PROD20250121001",
    "product_number": "PRD-2025-001",
    "product_name": "产品A",
    "product_info": {
      "product_type": "Mechanical",
      "design_stage": "Production",
      "design_status": "Released",
      "designer": "设计师A",
      "design_date": "2025-01-21",
      "version": "1.0"
    },
    "cad_models": {
      "models": [
        {
          "model_id": "MODEL001",
          "model_name": "产品A-3D模型",
          "model_type": "Part",
          "file_format": "STEP",
          "file_path": "/cad/models/PROD001.step",
          "model_version": "1.0"
        }
      ]
    }
  }
}
```

### 2.3 实现代码

**完整的产品设计管理实现**：

```python
from cad_file_parser import CADFileParser
from plm_storage import PLMStorage
from datetime import date

# 初始化组件
storage = PLMStorage("postgresql://user:pass@localhost/plm")
cad_parser = CADFileParser()

# 产品设计数据
product_design_data = {
    "product_id": "PROD20250121001",
    "product_number": "PRD-2025-001",
    "product_name": "产品A",
    "product_info": {
        "product_type": "Mechanical",
        "product_category": "Consumer",
        "design_stage": "Production",
        "design_status": "Released",
        "designer": "设计师A",
        "design_date": date(2025, 1, 21),
        "version": "1.0"
    },
    "design_documents": {
        "documents": [
            {
                "document_id": "DOC001",
                "document_name": "产品A设计规范",
                "document_type": "Specification",
                "document_format": "PDF",
                "document_path": "/docs/PROD001_spec.pdf",
                "document_version": "1.0"
            }
        ]
    },
    "cad_models": {
        "models": []
    }
}

# 存储产品设计
design_id = storage.store_product_design(product_design_data)
print(f"Stored product design: {design_id}")

# 解析CAD文件
cad_file_path = "/cad/models/PROD001.step"
try:
    cad_data = cad_parser.parse_cad_file(cad_file_path)
    print(f"Parsed CAD file: {cad_data['file_format']}, Type: {cad_data['model_type']}")

    # 创建CAD模型记录
    cad_model_data = {
        "model_id": "MODEL001",
        "product_id": product_design_data["product_id"],
        "model_name": "产品A-3D模型",
        "model_type": cad_data["model_type"],
        "file_format": cad_data["file_format"],
        "file_path": cad_file_path,
        "model_version": "1.0",
        "created_date": date.today()
    }

    model_id = storage.store_cad_model(cad_model_data)
    print(f"Stored CAD model: {model_id}")

    # 更新产品设计中的CAD模型列表
    product_design_data["cad_models"]["models"].append(cad_model_data)

except Exception as e:
    print(f"Error parsing CAD file: {e}")

# 查询产品设计统计
stats = storage.get_product_design_statistics(days=30)
print(f"\nProduct Design Statistics (30 days):")
print(f"  Total products: {stats['total_products']}")
print(f"  Released products: {stats['released_products']}")
print(f"  Production products: {stats['production_products']}")
print(f"  Total designers: {stats['total_designers']}")
```

---

## 3. 案例2：变更管理系统

### 3.1 场景描述

**业务背景**：
制造企业需要管理产品设计变更，包括变更请求、
变更审批、变更执行等，确保变更过程的可追溯性。

**技术挑战**：

- 需要变更流程管理
- 需要变更影响分析
- 需要变更审批流程
- 需要变更执行跟踪

**解决方案**：
使用PLMStorage存储变更数据，实现完整的变更管理。

### 3.2 Schema定义

**变更管理Schema**：

```json
{
  "change_management": {
    "change_id": "CHG20250121001",
    "change_number": "CHG-2025-001",
    "change_request": {
      "requestor": "工程师A",
      "request_date": "2025-01-21T10:00:00Z",
      "change_type": "Design",
      "change_reason": "优化产品性能",
      "change_description": "修改产品A的尺寸规格",
      "priority": "High",
      "affected_items": ["PROD20250121001"]
    },
    "change_approval": {
      "approval_workflow": [
        {
          "step_number": 1,
          "approver": "部门经理A",
          "approval_status": "Approved",
          "approval_date": "2025-01-21T14:00:00Z"
        }
      ],
      "overall_status": "Approved",
      "approval_date": "2025-01-21T14:00:00Z"
    },
    "change_execution": {
      "executor": "设计师B",
      "execution_status": "InProgress",
      "start_date": "2025-01-22T08:00:00Z"
    }
  }
}
```

### 3.3 实现代码

**完整的变更管理实现**：

```python
from plm_storage import PLMStorage
from datetime import datetime

# 初始化存储
storage = PLMStorage("postgresql://user:pass@localhost/plm")

# 创建变更请求
change_data = {
    "change_id": "CHG20250121001",
    "change_number": "CHG-2025-001",
    "change_request": {
        "requestor": "工程师A",
        "request_date": datetime.now(),
        "change_type": "Design",
        "change_reason": "优化产品性能",
        "change_description": "修改产品A的尺寸规格，提高产品强度",
        "priority": "High",
        "affected_items": ["PROD20250121001"]
    },
    "change_approval": {
        "approval_workflow": [
            {
                "step_number": 1,
                "approver": "部门经理A",
                "approval_status": "Pending",
                "approval_comment": ""
            },
            {
                "step_number": 2,
                "approver": "技术总监",
                "approval_status": "Pending",
                "approval_comment": ""
            }
        ],
        "overall_status": "Pending",
        "approval_date": None
    },
    "change_execution": {
        "executor": None,
        "execution_status": "NotStarted",
        "start_date": None,
        "completion_date": None,
        "execution_notes": ""
    },
    "change_impact": {
        "affected_products": ["PROD20250121001"],
        "affected_boms": ["BOM001"],
        "affected_documents": ["DOC001"],
        "risk_assessment": "中等风险，需要测试验证",
        "cost_impact": 5000.00
    }
}

# 存储变更请求
change_id = storage.store_change_management(change_data)
print(f"Created change request: {change_id}")

# 模拟审批流程
# 第一步审批
change_data["change_approval"]["approval_workflow"][0]["approval_status"] = "Approved"
change_data["change_approval"]["approval_workflow"][0]["approval_date"] = datetime.now()
change_data["change_approval"]["approval_workflow"][0]["approval_comment"] = "同意变更"

# 第二步审批
change_data["change_approval"]["approval_workflow"][1]["approval_status"] = "Approved"
change_data["change_approval"]["approval_workflow"][1]["approval_date"] = datetime.now()
change_data["change_approval"]["approval_workflow"][1]["approval_comment"] = "批准执行"

# 更新整体状态
change_data["change_approval"]["overall_status"] = "Approved"
change_data["change_approval"]["approval_date"] = datetime.now()
change_data["change_execution"]["execution_status"] = "InProgress"
change_data["change_execution"]["executor"] = "设计师B"
change_data["change_execution"]["start_date"] = datetime.now()

# 更新变更记录
storage.store_change_management(change_data)
print(f"Change request approved and execution started")

# 查询变更统计
change_stats = storage.get_change_statistics(days=30)
print(f"\nChange Management Statistics (30 days):")
print(f"  Total changes: {change_stats['total_changes']}")
print(f"  Approved changes: {change_stats['approved_changes']}")
print(f"  Completed changes: {change_stats['completed_changes']}")
print(f"  Urgent changes: {change_stats['urgent_changes']}")
```

---

## 4. 案例3：BOM管理系统

### 4.1 场景描述

**业务背景**：
制造企业需要管理BOM（物料清单），包括BOM创建、
版本管理、结构管理等，确保BOM数据的准确性。

**技术挑战**：

- 需要BOM结构管理
- 需要BOM版本控制
- 需要BOM与ERP集成
- 需要BOM与MES集成

**解决方案**：
使用BOMParser解析BOM数据，使用BOMToERPConverter
转换为ERP格式，使用PLMStorage存储BOM数据。

### 4.2 Schema定义

**BOM管理Schema**：

```json
{
  "bom_management": {
    "bom_id": "BOM20250121001",
    "bom_number": "BOM-2025-001",
    "product_id": "PROD20250121001",
    "bom_info": {
      "bom_type": "Manufacturing",
      "bom_version": "1.0",
      "bom_status": "Active",
      "effective_date": "2025-01-21",
      "creator": "工程师A"
    },
    "bom_structure": {
      "bom_items": [
        {
          "item_id": "ITEM001",
          "material_id": "MAT001",
          "material_name": "原材料A",
          "level": 0,
          "parent_item_id": null,
          "quantity": 1.0,
          "unit": "pieces"
        },
        {
          "item_id": "ITEM002",
          "material_id": "MAT002",
          "material_name": "原材料B",
          "level": 1,
          "parent_item_id": "ITEM001",
          "quantity": 2.0,
          "unit": "pieces"
        }
      ]
    }
  }
}
```

### 4.3 实现代码

**完整的BOM管理实现**：

```python
from bom_parser import BOMParser
from bom_to_erp_converter import BOMToERPConverter
from plm_storage import PLMStorage
from datetime import date

# 初始化组件
storage = PLMStorage("postgresql://user:pass@localhost/plm")
bom_parser = BOMParser()
erp_converter = BOMToERPConverter()

# BOM数据
bom_data = {
    "bom_id": "BOM20250121001",
    "bom_number": "BOM-2025-001",
    "product_id": "PROD20250121001",
    "bom_info": {
        "bom_type": "Manufacturing",
        "bom_version": "1.0",
        "bom_status": "Active",
        "effective_date": date(2025, 1, 21),
        "expiry_date": None,
        "creator": "工程师A",
        "created_date": date(2025, 1, 21)
    },
    "bom_items": [
        {
            "item_id": "ITEM001",
            "material_id": "MAT001",
            "material_name": "原材料A",
            "level": 0,
            "parent_item_id": None,
            "quantity": 1.0,
            "unit": "pieces",
            "usage_type": "Normal",
            "sequence": 1
        },
        {
            "item_id": "ITEM002",
            "material_id": "MAT002",
            "material_name": "原材料B",
            "level": 1,
            "parent_item_id": "ITEM001",
            "quantity": 2.0,
            "unit": "pieces",
            "usage_type": "Normal",
            "sequence": 1
        },
        {
            "item_id": "ITEM003",
            "material_id": "MAT003",
            "material_name": "原材料C",
            "level": 1,
            "parent_item_id": "ITEM001",
            "quantity": 3.0,
            "unit": "pieces",
            "usage_type": "Normal",
            "sequence": 2
        }
    ],
    "materials": [
        {
            "material_id": "MAT001",
            "material_number": "MAT-001",
            "material_name": "原材料A",
            "material_type": "Raw Material",
            "material_specification": "规格A",
            "unit": "pieces"
        },
        {
            "material_id": "MAT002",
            "material_number": "MAT-002",
            "material_name": "原材料B",
            "material_type": "Raw Material",
            "material_specification": "规格B",
            "unit": "pieces"
        },
        {
            "material_id": "MAT003",
            "material_number": "MAT-003",
            "material_name": "原材料C",
            "material_type": "Raw Material",
            "material_specification": "规格C",
            "unit": "pieces"
        }
    ]
}

# 解析BOM数据
parsed_bom = bom_parser.parse_bom_data(bom_data)
print(f"Parsed BOM: {parsed_bom['bom_number']}")

# 存储BOM
bom_id = storage.store_bom(parsed_bom)
print(f"Stored BOM: {bom_id}")

# 转换为ERP格式
erp_bom = erp_converter.convert_bom_to_erp(bom_data)
print(f"\nConverted BOM to ERP format:")
print(f"  BOM Number: {erp_bom['bom_number']}")
print(f"  Product ID: {erp_bom['product_id']}")
print(f"  BOM Items: {len(erp_bom['bom_items'])}")

# 查询BOM统计
bom_stats = storage.get_bom_statistics("PROD20250121001")
print(f"\nBOM Statistics for Product PROD20250121001:")
print(f"  Total BOMs: {bom_stats['total_boms']}")
print(f"  Total Materials: {bom_stats['total_materials']}")
print(f"  Max Level: {bom_stats['max_level']}")
print(f"  Total Quantity: {bom_stats['total_quantity']}")
```

---

## 5. 案例4：STEP文件解析和CAD集成

### 5.1 场景描述

**业务背景**：
制造企业需要解析STEP文件，提取CAD模型数据，
支持多种CAD格式的转换和集成。

**技术挑战**：

- 需要STEP文件解析
- 需要CAD格式转换
- 需要CAD数据存储
- 需要CAD模型管理

**解决方案**：
使用STEPParser解析STEP文件，使用CADFormatConverter
转换CAD格式，使用PLMStorage存储CAD数据。

### 5.2 实现代码

**完整的STEP文件解析和CAD集成实现**：

```python
from step_parser import STEPParser
from cad_file_parser import CADFileParser
from cad_format_converter import CADFormatConverter
from plm_storage import PLMStorage
from datetime import date

# 初始化组件
storage = PLMStorage("postgresql://user:pass@localhost/plm")
step_parser = STEPParser()
cad_parser = CADFileParser()
format_converter = CADFormatConverter()

# STEP文件路径
step_file_path = "/cad/models/PROD001.step"

# 解析STEP文件
try:
    step_data = step_parser.parse_step_file(step_file_path)
    print(f"Parsed STEP file: {step_file_path}")
    print(f"  File Schema: {step_data['step_header'].get('file_schema', 'Unknown')}")
    print(f"  File Name: {step_data['step_header'].get('file_name', 'Unknown')}")
    print(f"  Entities: {len(step_data['step_data']['entities'])}")

    # 解析CAD文件
    cad_data = cad_parser.parse_cad_file(step_file_path)
    print(f"\nParsed CAD file:")
    print(f"  Format: {cad_data['file_format']}")
    print(f"  Model Type: {cad_data['model_type']}")
    print(f"  Entities: {len(cad_data['entities'])}")

    # 存储CAD模型
    cad_model_data = {
        "model_id": "MODEL001",
        "product_id": "PROD20250121001",
        "model_name": "产品A-3D模型",
        "model_type": cad_data["model_type"],
        "file_format": cad_data["file_format"],
        "file_path": step_file_path,
        "model_version": "1.0",
        "created_date": date.today()
    }

    model_id = storage.store_cad_model(cad_model_data)
    print(f"\nStored CAD model: {model_id}")

    # 转换为IGES格式
    iges_file_path = "/cad/models/PROD001.iges"
    if format_converter.convert_cad_file(step_file_path, "IGES", iges_file_path):
        print(f"\nConverted to IGES format: {iges_file_path}")

except Exception as e:
    print(f"Error processing CAD file: {e}")
```

---

## 6. 案例5：PLM数据分析和报表

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储PLM数据，支持数据查询、
分析和报表生成。

### 6.2 实现代码

**完整的数据分析实现**：

```python
from plm_storage import PLMStorage

storage = PLMStorage("postgresql://user:pass@localhost/plm")

# 查询产品设计统计
design_stats = storage.get_product_design_statistics(days=30)
print("Product Design Statistics (30 days):")
print(f"  Total products: {design_stats['total_products']}")
print(f"  Released products: {design_stats['released_products']}")
print(f"  Production products: {design_stats['production_products']}")
print(f"  Total designers: {design_stats['total_designers']}")

# 查询变更统计
change_stats = storage.get_change_statistics(days=30)
print(f"\nChange Management Statistics (30 days):")
print(f"  Total changes: {change_stats['total_changes']}")
print(f"  Approved changes: {change_stats['approved_changes']}")
print(f"  Completed changes: {change_stats['completed_changes']}")
print(f"  Urgent changes: {change_stats['urgent_changes']}")

# 查询BOM统计
product_id = "PROD20250121001"
bom_stats = storage.get_bom_statistics(product_id)
print(f"\nBOM Statistics for Product {product_id}:")
print(f"  Total BOMs: {bom_stats['total_boms']}")
print(f"  Total Materials: {bom_stats['total_materials']}")
print(f"  Max Level: {bom_stats['max_level']}")
print(f"  Total Quantity: {bom_stats['total_quantity']}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
