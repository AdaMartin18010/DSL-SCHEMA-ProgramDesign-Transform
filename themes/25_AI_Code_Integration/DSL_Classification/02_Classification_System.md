# DSL分类体系

## 📑 目录

- [DSL分类体系](#dsl分类体系)
  - [📑 目录](#-目录)
  - [1. 分类维度](#1-分类维度)
  - [2. 按应用领域分类](#2-按应用领域分类)
    - [2.1 领域特定语言（Domain-Specific Language）](#21-领域特定语言domain-specific-language)
    - [2.2 配置语言（Configuration Language）](#22-配置语言configuration-language)
    - [2.3 查询语言（Query Language）](#23-查询语言query-language)
    - [2.4 建模语言（Modeling Language）](#24-建模语言modeling-language)
  - [3. 按实现方式分类](#3-按实现方式分类)
    - [3.1 外部DSL（External DSL）](#31-外部dslexternal-dsl)
    - [3.2 内部DSL（Internal DSL）](#32-内部dslinternal-dsl)
    - [3.3 混合DSL（Hybrid DSL）](#33-混合dslhybrid-dsl)
  - [4. 按语法形式分类](#4-按语法形式分类)
    - [4.1 文本DSL](#41-文本dsl)
    - [4.2 图形DSL](#42-图形dsl)
    - [4.3 表格DSL](#43-表格dsl)
  - [5. 分类矩阵](#5-分类矩阵)

---

## 1. 分类维度

DSL可以从三个维度进行分类：

1. **应用领域**：领域特定语言、配置语言、查询语言、建模语言
2. **实现方式**：外部DSL、内部DSL、混合DSL
3. **语法形式**：文本DSL、图形DSL、表格DSL

---

## 2. 按应用领域分类

### 2.1 领域特定语言（Domain-Specific Language）

**定义**：针对特定领域的语言。

**典型示例**：

- **EDIFACT**：电子数据交换标准
- **HL7**：医疗信息交换标准
- **SWIFT**：金融报文标准
- **ISO 11783**：农业机械电子数据交换标准

**特征**：

- 针对特定业务领域
- 高度专业化
- 符合行业标准

### 2.2 配置语言（Configuration Language）

**定义**：用于配置系统的语言。

**典型示例**：

- **YAML**：YAML Ain't Markup Language
- **JSON Schema**：JSON数据验证规范
- **TOML**：Tom's Obvious Minimal Language
- **INI**：初始化文件格式

**特征**：

- 易于读写
- 结构化数据表示
- 支持嵌套和引用

### 2.3 查询语言（Query Language）

**定义**：用于数据查询的语言。

**典型示例**：

- **SQL**：结构化查询语言
- **GraphQL**：Graph查询语言
- **SPARQL**：SPARQL Protocol and RDF Query Language
- **XPath**：XML路径语言

**特征**：

- 声明式语法
- 支持复杂查询
- 优化查询性能

### 2.4 建模语言（Modeling Language）

**定义**：用于系统建模的语言。

**典型示例**：

- **UML**：统一建模语言
- **BPMN**：业务流程建模符号
- **SysML**：系统建模语言
- **ER图**：实体关系图

**特征**：

- 图形化表示
- 支持多视图
- 可转换为代码

---

## 3. 按实现方式分类

### 3.1 外部DSL（External DSL）

**定义**：独立于宿主语言的DSL。

**典型示例**：

- SQL、YAML、XML、JSON

**特征**：

- 独立语法
- 需要解析器
- 灵活性高

### 3.2 内部DSL（Internal DSL）

**定义**：嵌入在宿主语言中的DSL。

**典型示例**：

- Ruby的Rake、RSpec
- Python的SQLAlchemy
- JavaScript的jQuery

**特征**：

- 使用宿主语言语法
- 无需额外解析器
- 类型安全

### 3.3 混合DSL（Hybrid DSL）

**定义**：结合外部和内部DSL的特点。

**典型示例**：

- GraphQL（外部语法，内部实现）
- Terraform（外部配置，内部执行）

**特征**：

- 结合两者优点
- 灵活性和类型安全

---

## 4. 按语法形式分类

### 4.1 文本DSL

**定义**：基于文本的DSL。

**典型示例**：

- SQL、YAML、JSON、XML

**特征**：

- 易于编辑
- 版本控制友好
- 工具支持丰富

### 4.2 图形DSL

**定义**：基于图形的DSL。

**典型示例**：

- UML、BPMN、流程图

**特征**：

- 直观可视化
- 易于理解
- 需要图形编辑器

### 4.3 表格DSL

**定义**：基于表格的DSL。

**典型示例**：

- Excel公式、CSV配置

**特征**：

- 结构化数据
- 易于批量处理
- 适合数据密集型场景

---

## 5. 分类矩阵

| DSL类型 | 应用领域 | 实现方式 | 语法形式 | 典型示例 |
|---------|---------|---------|---------|---------|
| **SQL** | 查询语言 | 外部DSL | 文本DSL | 数据库查询 |
| **YAML** | 配置语言 | 外部DSL | 文本DSL | 配置文件 |
| **UML** | 建模语言 | 外部DSL | 图形DSL | 系统建模 |
| **GraphQL** | 查询语言 | 混合DSL | 文本DSL | API查询 |
| **EDIFACT** | 领域DSL | 外部DSL | 文本DSL | 电子数据交换 |

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Typical_Examples.md` - 典型示例
- `04_Best_Practices.md` - 最佳实践
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
