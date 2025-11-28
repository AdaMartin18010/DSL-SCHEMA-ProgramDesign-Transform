# Helm Schema转换体系

## 📑 目录

- [Helm Schema转换体系](#helm-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Helm到Kubernetes转换](#2-helm到kubernetes转换)
    - [2.1 转换规则](#21-转换规则)
    - [2.2 完整转换实现](#22-完整转换实现)
  - [3. Kubernetes到Helm转换](#3-kubernetes到helm转换)
    - [3.1 转换规则](#31-转换规则)
    - [3.2 转换实现](#32-转换实现)
  - [4. Helm到Terraform转换](#4-helm到terraform转换)
    - [4.1 转换规则](#41-转换规则)
    - [4.2 完整转换实现](#42-完整转换实现)
  - [5. 转换验证](#5-转换验证)
    - [5.1 验证规则](#51-验证规则)
    - [5.2 验证实现](#52-验证实现)
  - [6. Helm数据存储与分析](#6-helm数据存储与分析)
    - [6.1 PostgreSQL Helm数据存储](#61-postgresql-helm数据存储)
    - [6.2 Helm数据分析查询](#62-helm数据分析查询)
  - [7. 转换最佳实践](#7-转换最佳实践)
    - [7.1 转换前准备](#71-转换前准备)
    - [7.2 转换过程](#72-转换过程)
    - [7.3 转换后优化](#73-转换后优化)
  - [8. 转换工具和资源](#8-转换工具和资源)
    - [8.1 转换工具](#81-转换工具)
    - [8.2 参考资源](#82-参考资源)

---

## 1. 转换体系概述

Helm Schema转换体系支持Helm Chart与其他配置格式之间的转换。

### 1.1 转换目标

1. **Helm到Kubernetes转换**：Helm Chart渲染为Kubernetes资源
2. **Kubernetes到Helm转换**：Kubernetes资源转换为Helm Chart
3. **Helm到Terraform转换**：Helm Chart转换为Terraform配置
4. **Schema到数据库转换**：Helm Schema定义到PostgreSQL存储

---

## 2. Helm到Kubernetes转换

### 2.1 转换规则

**资源映射规则**：

- Helm模板 + Values → Kubernetes资源（通过渲染）
- Helm Chart → Kubernetes资源集合
- Helm依赖 → Kubernetes资源依赖

### 2.2 完整转换实现

**Helm到Kubernetes转换器**：

```python
#!/usr/bin/env python3
"""
Helm到Kubernetes转换器
"""

import yaml
import json
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class HelmToKubernetesConverter:
    """Helm到Kubernetes转换器"""

    def __init__(self):
        self.k8s_resources = []

    def convert(self, chart_path: str, values: Optional[Dict] = None,
                release_name: str = 'release') -> List[Dict]:
        """将Helm Chart渲染为Kubernetes资源"""
        # 方法1：使用helm template命令（推荐）
        if self._helm_available():
            return self._convert_with_helm(chart_path, values, release_name)
        else:
            # 方法2：手动解析和渲染
            return self._convert_manually(chart_path, values)

    def _helm_available(self) -> bool:
        """检查helm命令是否可用"""
        try:
            subprocess.run(['helm', 'version'],
                         capture_output=True, check=True)
            return True
        except:
            return False

    def _convert_with_helm(self, chart_path: str, values: Optional[Dict],
                          release_name: str) -> List[Dict]:
        """使用helm template命令转换"""
        cmd = ['helm', 'template', release_name, chart_path]

        # 如果有values，写入临时文件
        if values:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                           delete=False) as f:
                yaml.dump(values, f)
                values_file = f.name
                cmd.extend(['--values', values_file])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            resources = list(yaml.safe_load_all(result.stdout))
            return [r for r in resources if r is not None]
        except subprocess.CalledProcessError as e:
            raise Exception(f"Helm template failed: {e.stderr}")
        finally:
            if values and os.path.exists(values_file):
                os.unlink(values_file)

    def _convert_manually(self, chart_path: str, values: Optional[Dict]) -> List[Dict]:
        """手动解析和渲染Helm Chart"""
        chart_dir = Path(chart_path)

        # 读取Chart.yaml
        chart_yaml = self._read_chart_yaml(chart_dir)

        # 读取values.yaml
        default_values = self._read_values_yaml(chart_dir)

        # 合并values
        merged_values = {**default_values, **(values or {})}

        # 读取模板文件
        templates_dir = chart_dir / 'templates'
        if templates_dir.exists():
            for template_file in templates_dir.glob('*.yaml'):
                template_content = template_file.read_text()
                rendered = self._render_template(template_content, merged_values, chart_yaml)
                if rendered:
                    self.k8s_resources.append(rendered)

        return self.k8s_resources

    def _read_chart_yaml(self, chart_dir: Path) -> Dict:
        """读取Chart.yaml"""
        chart_file = chart_dir / 'Chart.yaml'
        if chart_file.exists():
            return yaml.safe_load(chart_file.read_text())
        return {}

    def _read_values_yaml(self, chart_dir: Path) -> Dict:
        """读取values.yaml"""
        values_file = chart_dir / 'values.yaml'
        if values_file.exists():
            return yaml.safe_load(values_file.read_text())
        return {}

    def _render_template(self, template_content: str, values: Dict,
                        chart: Dict) -> Optional[Dict]:
        """渲染Helm模板（简化版）"""
        # 这里应该使用Go模板引擎，简化实现
        # 实际应该使用helm的模板引擎
        try:
            # 简单的变量替换
            rendered = template_content
            for key, value in values.items():
                rendered = rendered.replace(f'{{{{ .Values.{key} }}}}', str(value))

            # 移除未替换的模板语法
            import re
            rendered = re.sub(r'\{\{.*?\}\}', '', rendered)

            return yaml.safe_load(rendered)
        except Exception as e:
            print(f"Error rendering template: {e}")
            return None

# 使用示例
if __name__ == '__main__':
    converter = HelmToKubernetesConverter()

    # 转换Helm Chart
    chart_path = './my-chart'
    values = {
        'replicaCount': 3,
        'image': {
            'repository': 'nginx',
            'tag': '1.21'
        }
    }

    k8s_resources = converter.convert(chart_path, values)

    # 输出YAML
    for resource in k8s_resources:
        print(yaml.dump(resource, default_flow_style=False))
        print('---')
```

---

## 3. Kubernetes到Helm转换

### 3.1 转换规则

**资源映射规则**：

- Kubernetes资源 → Helm模板文件
- 硬编码值 → Helm Values变量
- 资源名称 → Helm模板函数

### 3.2 转换实现

**Kubernetes到Helm转换器**（已在Kubernetes Schema转换体系中详细说明）：

参考 `Kubernetes_Schema/04_Transformation.md` 中的 `KubernetesToHelmConverter` 实现。

---

## 4. Helm到Terraform转换

### 4.1 转换规则

**资源映射规则**：

- Helm Chart → Terraform `helm_release`资源
- Helm Values → Terraform变量
- Helm依赖 → Terraform依赖

### 4.2 完整转换实现

**Helm到Terraform转换器**：

```python
class HelmToTerraformConverter:
    """Helm到Terraform转换器"""

    def convert(self, chart_path: str, release_name: str,
                namespace: str = 'default', values: Optional[Dict] = None) -> str:
        """转换Helm Chart为Terraform配置"""
        chart_dir = Path(chart_path)

        # 读取Chart.yaml
        chart_yaml = self._read_chart_yaml(chart_dir)
        chart_name = chart_yaml.get('name', 'chart')
        chart_version = chart_yaml.get('version', '0.1.0')

        # 读取values.yaml
        default_values = self._read_values_yaml(chart_dir)
        merged_values = {**default_values, **(values or {})}

        # 生成Terraform配置
        tf_config = f"""
# Helm Release: {release_name}
resource "helm_release" "{release_name}" {{
  name       = "{release_name}"
  repository = "https://charts.example.com"  # 根据实际情况修改
  chart      = "{chart_name}"
  version    = "{chart_version}"
  namespace  = "{namespace}"

  values = [
    yamlencode({{
{self._format_values_for_tf(merged_values)}
    }})
  ]

  # 依赖项
  depends_on = [
    # 添加依赖资源
  ]
}}

# 输出
output "{release_name}_status" {{
  value = helm_release.{release_name}.status
}}
"""
        return tf_config

    def _format_values_for_tf(self, values: Dict, indent: int = 2) -> str:
        """格式化values为Terraform格式"""
        lines = []
        for key, value in values.items():
            if isinstance(value, dict):
                lines.append(' ' * indent + f'{key} = {{')
                lines.append(self._format_values_for_tf(value, indent + 2))
                lines.append(' ' * indent + '}')
            elif isinstance(value, list):
                lines.append(' ' * indent + f'{key} = [')
                for item in value:
                    if isinstance(item, dict):
                        lines.append(' ' * (indent + 2) + '{')
                        lines.append(self._format_values_for_tf(item, indent + 4))
                        lines.append(' ' * (indent + 2) + '},')
                    else:
                        lines.append(' ' * (indent + 2) + f'"{item}",')
                lines.append(' ' * indent + ']')
            else:
                if isinstance(value, str):
                    value_str = f'"{value}"'
                else:
                    value_str = str(value)
                lines.append(' ' * indent + f'{key} = {value_str}')
        return '\n'.join(lines)
```

---

## 5. 转换验证

### 5.1 验证规则

**完整性验证**：

- 所有Chart文件都已处理
- 所有模板都已渲染
- 所有依赖都已解析

**一致性验证**：

- Values配置一致性
- 模板语法正确性
- 资源定义一致性

**功能等价性验证**：

- 转换后的配置功能等价
- 资源行为一致
- 配置值一致

### 5.2 验证实现

**转换验证器**：

```python
class HelmConversionValidator:
    """Helm转换验证器"""

    def validate_chart(self, chart_path: str) -> Dict:
        """验证Helm Chart"""
        results = {
            'chart_valid': self._validate_chart_structure(chart_path),
            'templates_valid': self._validate_templates(chart_path),
            'values_valid': self._validate_values(chart_path)
        }
        return results

    def validate_conversion(self, chart_path: str,
                          k8s_resources: List[Dict]) -> Dict:
        """验证转换结果"""
        results = {
            'completeness': self._validate_completeness(chart_path, k8s_resources),
            'consistency': self._validate_consistency(chart_path, k8s_resources),
            'equivalence': self._validate_equivalence(chart_path, k8s_resources)
        }
        return results
```

---

## 6. Helm数据存储与分析

### 6.1 PostgreSQL Helm数据存储

**Helm数据存储方案**：

```python
import psycopg2
import json

class HelmDataStore:
    """Helm数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建Helm数据存储表"""
        with self.conn.cursor() as cur:
            # Chart定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS helm_charts (
                    id SERIAL PRIMARY KEY,
                    chart_name VARCHAR(255) NOT NULL UNIQUE,
                    chart_version VARCHAR(50) NOT NULL,
                    chart_metadata JSONB NOT NULL,
                    chart_path VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chart_name, chart_version)
                )
            """)

            # Values定义表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS helm_values (
                    id SERIAL PRIMARY KEY,
                    chart_id INTEGER REFERENCES helm_charts(id),
                    values_name VARCHAR(255),
                    values_definition JSONB NOT NULL,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Release表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS helm_releases (
                    id SERIAL PRIMARY KEY,
                    chart_id INTEGER REFERENCES helm_charts(id),
                    release_name VARCHAR(255) NOT NULL,
                    namespace VARCHAR(255),
                    values_id INTEGER REFERENCES helm_values(id),
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(release_name, namespace)
                )
            """)

            self.conn.commit()
```

### 6.2 Helm数据分析查询

**分析查询示例**：

```python
def analyze_helm_usage(db_config: Dict):
    """分析Helm使用情况"""
    store = HelmDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询Chart使用统计
        cur.execute("""
            SELECT
                hc.chart_name,
                hc.chart_version,
                COUNT(hr.id) as release_count
            FROM helm_charts hc
            LEFT JOIN helm_releases hr ON hc.id = hr.chart_id
            GROUP BY hc.id, hc.chart_name, hc.chart_version
            ORDER BY release_count DESC
        """)

        return cur.fetchall()
```

## 7. 转换最佳实践

### 7.1 转换前准备

1. **清理Helm Chart**：
   - 移除未使用的模板
   - 标准化命名
   - 验证Chart正确性

2. **备份数据**：
   - 备份Helm Chart
   - 创建回滚计划

### 7.2 转换过程

1. **分阶段转换**：
   - 先转换核心资源
   - 再转换依赖资源
   - 最后转换配置

2. **验证转换结果**：
   - 检查资源完整性
   - 验证模板渲染
   - 测试功能等价性

### 7.3 转换后优化

1. **优化配置**：
   - 参数化配置值
   - 优化资源组织
   - 添加文档

2. **测试和验证**：
   - 在测试环境验证
   - 逐步迁移生产环境
   - 监控资源状态

## 8. 转换工具和资源

### 8.1 转换工具

- **helm template**：Helm Chart渲染工具
- **helmify**：Kubernetes到Helm转换工具

### 8.2 参考资源

- [Helm文档](https://helm.sh/docs/)
- [Kubernetes文档](https://kubernetes.io/docs/)
- [Terraform Helm Provider](https://registry.terraform.io/providers/hashicorp/helm)

---

**文档创建时间**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
**最后更新**：2025-01-21
**下次审查时间**：2025-02-21
