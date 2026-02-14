# Unified Schema Language (USL) Specification v1.0

## USL 1.0 语言规范

**规范版本**: 1.0.0  
**规范状态**: Proposed Standard  
**发布日期**: 2026-02-14  
**规范机构**: DSL Schema Standardization Consortium (DSSC)  

---

## 📑 目录

- [1. 引言](#1-引言)
- [2. 语言基础](#2-语言基础)
- [3. 类型系统](#3-类型系统)
- [4. Schema定义](#4-schema定义)
- [5. 约束系统](#5-约束系统)
- [6. 关系系统](#6-关系系统)
- [7. 操作定义](#7-操作定义)
- [8. 标准库](#8-标准库)
- [9. 扩展机制](#9-扩展机制)
- [10. 互操作性](#10-互操作性)

---

## 1. 引言

### 1.1 规范范围

本规范定义统一Schema语言（USL）v1.0的语法、语义和标准库。USL是一种用于定义数据Schema的通用领域特定语言（DSL），支持：

- 类型安全的Schema定义
- 丰富的约束表达
- 关系数据建模
- 多格式代码生成
- 形式化验证

### 1.2 符合性要求

本文档中的关键词 "MUST"（必须）、"MUST NOT"（禁止）、"REQUIRED"（要求）、"SHALL"（应当）、"SHALL NOT"（不应当）、"SHOULD"（建议）、"SHOULD NOT"（不建议）、"RECOMMENDED"（推荐）、"MAY"（可以）、"OPTIONAL"（可选）按照RFC 2119的解释。

### 1.3 文档约定

- 语法定义使用扩展巴科斯-瑙尔范式（EBNF）
- 代码示例使用语法高亮
- 规范要求分为三个级别：
  - **Level 1**: 核心功能（必须实现）
  - **Level 2**: 推荐功能（建议实现）
  - **Level 3**: 扩展功能（可选实现）

---

## 2. 语言基础

### 2.1 字符集

USL源文件**必须**使用UTF-8编码。

```ebnf
USL_Character ::= Unicode_Character
Unicode_Character ::= [#x0000-#x10FFFF]
```

### 2.2 词法单元

#### 2.2.1 空白字符

```ebnf
Whitespace ::= Space | Tab | Newline | Carriage_Return | Form_Feed
Space ::= #x0020
Tab ::= #x0009
Newline ::= #x000A
Carriage_Return ::= #x000D
Form_Feed ::= #x000C
```

空白字符用于分隔词法单元，本身无语义意义。

#### 2.2.2 注释

```ebnf
Comment ::= Line_Comment | Block_Comment | Doc_Comment

Line_Comment ::= "//" Any_Character_Except_Newline*

Block_Comment ::= "/*" Any_Character_Except_Star_Slash* "*/"

Doc_Comment ::= "///" Any_Character_Except_Newline*
              | "/**" Any_Character_Except_Star_Slash* "*/"
```

文档注释（Doc_Comment）用于生成API文档。

#### 2.2.3 标识符

```ebnf
Identifier ::= [a-zA-Z_] [a-zA-Z0-9_-]*
             | "`" Escaped_Identifier "`"

Escaped_Identifier ::= [^`]+
```

标识符区分大小写。使用反引号可以定义包含特殊字符的标识符。

**示例**:
```usl
schema User          // 普通标识符
field first_name     // 下划线
field `order-id`     // 特殊字符需要转义
```

#### 2.2.4 关键字

以下标识符为保留关键字，不能用于自定义名称：

```
// 定义关键字
schema, type, newtype, enum, union, interface, struct, entity, value

// 字段关键字
field, readonly, mutable, private, protected, public, static, abstract

// 类型关键字
String, Text, Char, Integer, Int8, Int16, Int32, Int64, Int128
Unsigned, UInt8, UInt16, UInt32, UInt64, UInt128
Float, Float32, Float64, Float128, Decimal, Boolean, Bool
Date, Time, DateTime, Timestamp, Duration
UUID, URI, URL, Email, IPv4, IPv6, CIDR
Binary, Bytes, Base64, Hex, Any, Never, Unknown

// 约束关键字
constraint, validate, required, min, max, pattern, format, enum

// 关系关键字
relation, one_to_one, one_to_many, many_to_one, many_to_many
belongs_to, has_one, has_many, embedded, references

// 操作关键字
query, mutation, subscription, rpc

// 控制流关键字
if, then, else, for, in, while, match, return, let, var

// 模块关键字
import, export, module, library, namespace, extends, as

// 其他关键字
true, false, null, nil, undefined, metadata, this, self
```

### 2.3 字面量

#### 2.3.1 字符串字面量

```ebnf
String_Literal ::= Single_Quoted_String
                 | Double_Quoted_String
                 | Triple_Single_Quoted_String
                 | Triple_Double_Quoted_String

Single_Quoted_String ::= "'" String_Char* "'"
Double_Quoted_String ::= '"' String_Char* '"'
Triple_Single_Quoted_String ::= "'''" Any_Char_Except_Triple_Single* "'''"
Triple_Double_Quoted_String ::= "\"\"\"" Any_Char_Except_Triple_Double* "\"\"\""

String_Char ::= Source_Character_Except_Quote_Backslash
              | Escape_Sequence

Escape_Sequence ::= "\\" ("\"" | "'" | "\\" | "n" | "r" | "t" | "b" | "f" | "v" | "0" | Unicode_Escape)

Unicode_Escape ::= "u" Hex_Digit{4} | "U" Hex_Digit{8}
```

**示例**:
```usl
field name: String { default: "Anonymous" }
field description: String { default: 'No description' }
field content: String { default: '''
  Multi-line
  string content
''' }
```

#### 2.3.2 数字字面量

```ebnf
Numeric_Literal ::= Integer_Literal
                  | Decimal_Literal
                  | Scientific_Literal
                  | Hexadecimal_Literal
                  | Binary_Literal
                  | Octal_Literal

Integer_Literal ::= ["-"] Digit+
Decimal_Literal ::= ["-"] Digit+ "." Digit+
Scientific_Literal ::= (Integer_Literal | Decimal_Literal) ("e" | "E") ["+" | "-"]? Digit+
Hexadecimal_Literal ::= "0x" Hex_Digit+
Binary_Literal ::= "0b" ["0" | "1"]+
Octal_Literal ::= "0o" [0-7]+

Digit ::= [0-9]
Hex_Digit ::= Digit | [a-fA-F]
```

**示例**:
```usl
field count: Integer { default: 42 }
field price: Decimal { default: 19.99 }
field bigNumber: Int64 { default: 1e10 }
field flags: Integer { default: 0xFF }
field mask: Integer { default: 0b1010 }
field mode: Integer { default: 0o755 }
```

#### 2.3.3 布尔字面量

```ebnf
Boolean_Literal ::= "true" | "false"
```

#### 2.3.4 空值字面量

```ebnf
Null_Literal ::= "null" | "nil" | "undefined"
```

---

## 3. 类型系统

### 3.1 类型系统概述

USL采用**静态类型系统**，支持：

- 渐进式类型（从Any到精确类型）
- 子类型多态
- 参数多态（泛型）
- 名义子类型 + 结构化子类型
- 类型推断

### 3.2 原始类型

#### 3.2.1 字符串类型

```ebnf
String_Type ::= "String" | "Text" | "Char"
```

| 类型 | 说明 | 编码 | Level |
|------|------|------|-------|
| `String` | 可变长字符串 | UTF-8 | 1 |
| `Text` | 长文本，可存储大量内容 | UTF-8 | 2 |
| `Char` | 单个Unicode字符 | UTF-8 | 2 |

#### 3.2.2 整数类型

```ebnf
Integer_Type ::= "Integer"
               | "Int8" | "Int16" | "Int32" | "Int64" | "Int128"
               | "Unsigned" | "UInt8" | "UInt16" | "UInt32" | "UInt64" | "UInt128"
```

| 类型 | 范围 | 存储 | Level |
|------|------|------|-------|
| `Int8` | -128 ~ 127 | 8-bit | 2 |
| `Int16` | -32768 ~ 32767 | 16-bit | 2 |
| `Int32` | -2^31 ~ 2^31-1 | 32-bit | 1 |
| `Int64` | -2^63 ~ 2^63-1 | 64-bit | 1 |
| `Int128` | -2^127 ~ 2^127-1 | 128-bit | 3 |
| `UInt8` | 0 ~ 255 | 8-bit | 2 |
| `UInt16` | 0 ~ 65535 | 16-bit | 2 |
| `UInt32` | 0 ~ 2^32-1 | 32-bit | 2 |
| `UInt64` | 0 ~ 2^64-1 | 64-bit | 2 |
| `UInt128` | 0 ~ 2^128-1 | 128-bit | 3 |
| `Integer` | 平台相关，通常为Int64 | 64-bit | 1 |
| `Unsigned` | 平台相关，通常为UInt64 | 64-bit | 2 |

#### 3.2.3 浮点类型

```ebnf
Float_Type ::= "Float" | "Float32" | "Float64" | "Float128"
```

| 类型 | 说明 | 精度 | Level |
|------|------|------|-------|
| `Float32` | IEEE 754单精度 | ~7位十进制 | 2 |
| `Float64` | IEEE 754双精度 | ~15位十进制 | 1 |
| `Float128` | IEEE 754四精度 | ~34位十进制 | 3 |
| `Float` | 平台相关，通常为Float64 | ~15位十进制 | 1 |

#### 3.2.4 定点类型

```ebnf
Decimal_Type ::= "Decimal" ("(" Precision "," Scale ")")?
Precision ::= Digit+
Scale ::= Digit+
```

`Decimal`用于精确十进制计算，如金融数据。

**示例**:
```usl
field price: Decimal(19, 4)  // 19位精度，4位小数
field amount: Decimal(38, 18)  // 高精度
```

#### 3.2.5 布尔类型

```ebnf
Boolean_Type ::= "Boolean" | "Bool"
```

取值: `true` | `false`

#### 3.2.6 日期时间类型

```ebnf
DateTime_Type ::= "Date" | "Time" | "DateTime" | "Timestamp" | "Duration"
```

| 类型 | 说明 | 格式 | Level |
|------|------|------|-------|
| `Date` | 日期（无时区） | ISO 8601 | 1 |
| `Time` | 时间（无时区） | ISO 8601 | 2 |
| `DateTime` | 日期时间（有时区） | ISO 8601 | 1 |
| `Timestamp` | Unix时间戳 | 整数/浮点数 | 2 |
| `Duration` | 时间间隔 | ISO 8601 Duration | 2 |

#### 3.2.7 特殊字符串类型

```ebnf
Special_String_Type ::= "UUID" | "URI" | "URL" | "Email" | "IPv4" | "IPv6" | "CIDR"
```

这些类型继承自`String`，但带有格式验证。

**示例**:
```usl
field id: UUID           // 自动验证UUID格式
field link: URL          // 自动验证URL格式
field contact: Email     // 自动验证Email格式
field serverIP: IPv4     // 自动验证IPv4格式
```

#### 3.2.8 二进制类型

```ebnf
Binary_Type ::= "Binary" | "Bytes" | "Base64" | "Hex"
```

| 类型 | 说明 | 编码 | Level |
|------|------|------|-------|
| `Binary` | 原始二进制数据 | 字节数组 | 1 |
| `Bytes` | 二进制数据（别名） | 字节数组 | 1 |
| `Base64` | Base64编码的字符串 | Base64 | 2 |
| `Hex` | 十六进制编码的字符串 | Hex | 2 |

#### 3.2.9 特殊类型

```ebnf
Special_Type ::= "Any" | "Never" | "Unknown"
```

| 类型 | 说明 | Level |
|------|------|-------|
| `Any` | 任意类型（顶层类型） | 1 |
| `Never` | 永不可达类型（底类型） | 2 |
| `Unknown` | 未知类型（需要类型检查） | 2 |

### 3.3 复合类型

#### 3.3.1 数组类型

```ebnf
Array_Type ::= "Array" "<" Type_Expression ">"
             | "List" "<" Type_Expression ">"
             | "Vector" "<" Type_Expression ">"
             | Type_Expression "[]"
```

**示例**:
```usl
field tags: Array<String>
field scores: List<Int32>
field matrix: Array<Array<Float64>>
field names: String[]  // 语法糖
```

#### 3.3.2 映射类型

```ebnf
Map_Type ::= "Map" "<" Key_Type "," Value_Type ">"
           | "Dict" "<" Key_Type "," Value_Type ">"
           | "HashMap" "<" Key_Type "," Value_Type ">"

Key_Type ::= String_Type | Integer_Type | Enum_Type
```

**示例**:
```usl
field attributes: Map<String, Any>
field lookup: Dict<String, User>
field counts: Map<Int32, Int64>
```

#### 3.3.3 集合类型

```ebnf
Set_Type ::= "Set" "<" Type_Expression ">"
           | "HashSet" "<" Type_Expression ">"
```

**示例**:
```usl
field uniqueTags: Set<String>
field ids: HashSet<UUID>
```

#### 3.3.4 记录类型

```ebnf
Record_Type ::= "Record" "<" Value_Type ">"
              | "{" "[" String_Literal "]" ":" Type_Expression ("," "[" String_Literal "]" ":" Type_Expression)* "}"
```

记录类型表示键类型为字符串、值类型统一的映射。

**示例**:
```usl
field translations: Record<String>  // { [key: string]: string }
field config: {
  ["host"]: String,
  ["port"]: Integer,
  ["ssl"]: Boolean
}
```

#### 3.3.5 函数类型

```ebnf
Function_Type ::= "(" Parameter_Types? ")" "=>" Return_Type
                | "Function" "<" Parameter_Types "," Return_Type ">"

Parameter_Types ::= Type_Expression ("," Type_Expression)*
Return_Type ::= Type_Expression
```

**示例**:
```usl
// 用于高阶函数定义
type Predicate<T>: Function<T, Boolean>
type Transform<T, R>: Function<T, R>
type Reducer<T, Acc>: (Acc, T) => Acc
```

### 3.4 类型修饰符

#### 3.4.1 可选类型

```ebnf
Optional_Type ::= Type_Expression "?"
```

`T?`等价于`T | null`。

**示例**:
```usl
field nickname: String?  // 可为null
field age: Integer?      // 可为null
```

#### 3.4.2 可空类型

```ebnf
Nullable_Type ::= Type_Expression "|" "null"
                | Type_Expression "|" "nil"
                | Type_Expression "|" "undefined"
```

**示例**:
```usl
field data: String | null
field config: Config | undefined
```

### 3.5 用户定义类型

#### 3.5.1 类型别名

```ebnf
Type_Alias ::= "type" Identifier Generic_Params? "=" Type_Expression
```

类型别名是现有类型的同义词。

**示例**:
```usl
type UserID = UUID
type Money = Decimal(19, 4)
type JSONValue = String | Integer | Float | Boolean | null | Array<JSONValue> | Map<String, JSONValue>
```

#### 3.5.2 新类型

```ebnf
NewType ::= "newtype" Identifier Generic_Params? "=" Type_Expression
```

新类型创建与基础类型不同的独立类型。

**示例**:
```usl
newtype EmailAddress = String  // EmailAddress ≠ String
newtype PhoneNumber = String
```

#### 3.5.3 枚举类型

```ebnf
Enum_Type ::= "enum" Identifier "{" Enum_Member+ "}"

Enum_Member ::= Identifier ("=" Primitive_Value)?
```

**示例**:
```usl
enum OrderStatus {
  pending
  processing
  shipped
  delivered
  cancelled
}

enum Priority {
  low = 1
  medium = 2
  high = 3
  critical = 4
}
```

#### 3.5.4 联合类型

```ebnf
Union_Type ::= "union" Identifier Generic_Params? "=" Union_Member ("|" Union_Member)+

Union_Member ::= Type_Expression
```

**示例**:
```usl
union Result<T, E> = Success<T> | Error<E>
union PaymentMethod = CreditCard | PayPal | BankTransfer
union Number = Integer | Float | Decimal
```

#### 3.5.5 接口类型

```ebnf
Interface_Type ::= "interface" Identifier Generic_Params? ("extends" Type_List)? "{" Interface_Body "}"

Interface_Body ::= (Field_Definition | Method_Signature)*

Method_Signature ::= Identifier "(" Parameter_List? ")" (":" Type_Expression)?
```

**示例**:
```usl
interface Identifiable {
  field id: UUID
}

interface Timestamped {
  field createdAt: DateTime
  field updatedAt: DateTime
}

interface Auditable extends Identifiable, Timestamped {
  field createdBy: User
  field updatedBy: User
}
```

### 3.6 泛型

#### 3.6.1 泛型参数

```ebnf
Generic_Params ::= "<" Generic_Param ("," Generic_Param)* ">"

Generic_Param ::= Identifier ("extends" Type_Expression)? ("=" Type_Expression)?
```

**示例**:
```usl
// 带约束的泛型
type Container<T extends Comparable> {
  field value: T
}

// 带默认值的泛型
type Response<T = Any> {
  field data: T
  field success: Boolean
}

// 多个泛型参数
type Either<L, R> = Left<L> | Right<R>
```

#### 3.6.2 泛型约束

```ebnf
Type_Constraint ::= "extends" Type_Expression
```

**示例**:
```usl
interface Comparable {
  method compareTo(other: This): Integer
}

// T必须是Comparable的子类型
function sort<T extends Comparable>(items: Array<T>): Array<T>
```

### 3.7 子类型关系

#### 3.7.1 子类型规则

```
自反性:
─────────
T <: T

传递性:
T₁ <: T₂    T₂ <: T₃
────────────────────
T₁ <: T₃

Top类型:
────────
T <: Any

Bottom类型:
───────────
Never <: T
```

#### 3.7.2 协变与逆变

```usl
// 数组是协变的
Array<Cat> <: Array<Animal> if Cat <: Animal

// 函数参数是逆变的
(Animal) => Void <: (Cat) => Void if Cat <: Animal

// 函数返回是协变的
() => Cat <: () => Animal if Cat <: Animal
```

---

## 4. Schema定义

### 4.1 Schema声明

```ebnf
Schema_Declaration ::= Schema_Header Schema_Body Schema_Footer?

Schema_Header ::= "schema" Identifier (Schema_Version)? (Schema_Extends)? "{"

Schema_Version ::= "v" Version_Number

Version_Number ::= Digit+ ("." Digit+)*

Schema_Extends ::= "extends" Identifier ("," Identifier)*

Schema_Body ::= Schema_Element*

Schema_Footer ::= "}"
```

### 4.2 Schema元素

```ebnf
Schema_Element ::= Import_Statement
                 | Namespace_Definition
                 | Documentation_Block
                 | Annotation_List
                 | Type_Definition
                 | Field_Definition
                 | Constraint_Definition
                 | Relation_Definition
                 | Operation_Definition
                 | Metadata_Definition
                 | Extension_Block
```

### 4.3 字段定义

```ebnf
Field_Definition ::= Field_Modifier* "field" Identifier ":" Type_Expression Field_Attributes?

Field_Modifier ::= "readonly" | "mutable" | "private" | "protected" | "public" | "static" | "abstract"

Field_Attributes ::= "{" Field_Attribute ("," Field_Attribute)* "}"

Field_Attribute ::= Field_Constraint
                  | Field_Default
                  | Field_Description
                  | Field_Example
                  | Field_Mapping
```

**示例**:
```usl
schema Product {
  // 基础字段
  field id: UUID
  
  // 带约束的字段
  field name: String {
    constraint: { minLength: 1, maxLength: 200 }
  }
  
  // 可选字段
  field description: String? {
    description: "产品详细描述"
  }
  
  // 只读字段
  readonly field createdAt: DateTime
  
  // 私有字段
  private field internalCode: String
  
  // 带默认值的字段
  field status: ProductStatus {
    default: active
  }
  
  // 带示例的字段
  field price: Decimal(19, 4) {
    example: 99.99
    constraint: { min: 0 }
  }
}
```

### 4.4 结构类型

```ebnf
Struct_Type ::= "struct" Identifier Generic_Params? "{" Struct_Body "}"
Struct_Body ::= Field_Definition*
```

结构类型用于纯数据传输对象。

**示例**:
```usl
struct Address {
  field street: String
  field city: String
  field country: String
  field postalCode: String
}

struct GeoLocation {
  field latitude: Float64
  field longitude: Float64
  
  constraint: latitude >= -90 and latitude <= 90
  constraint: longitude >= -180 and longitude <= 180
}
```

### 4.5 实体类型

```ebnf
Entity_Type ::= "entity" Identifier Generic_Params? "{" Entity_Body "}"
Entity_Body ::= (Field_Definition | Identifier_Definition | Relation_Definition)*

Identifier_Definition ::= "identifier" Identifier ("," Identifier)*
```

实体类型用于领域模型，支持关系和标识符定义。

**示例**:
```usl
entity User {
  identifier id: UUID
  
  field email: Email { unique: true }
  field name: String
  field profile: Profile?
  
  // 关系
  relation orders: has_many(Order)
  relation addresses: has_many(Address) { through: UserAddress }
}

entity Order {
  identifier id: UUID
  identifier orderNumber: String
  
  field total: Decimal(19, 4)
  field status: OrderStatus
  
  relation user: belongs_to(User)
  relation items: has_many(OrderItem)
}
```

### 4.6 值类型

```ebnf
Value_Type_Def ::= "value" Identifier Generic_Params? "{" Value_Body "}"
Value_Body ::= Field_Definition*
```

值类型用于不可变值对象。

**示例**:
```usl
value Money {
  field amount: Decimal(19, 4)
  field currency: CurrencyCode
  
  constraint: amount >= 0
}

value DateRange {
  field start: Date
  field end: Date
  
  constraint: start <= end
}
```

---

## 5. 约束系统

### 5.1 约束概述

USL约束系统支持：

- 值约束（范围、格式、枚举等）
- 结构约束（字段依赖、互斥等）
- 逻辑约束（蕴含、等价等）
- 自定义约束（函数表达式）

### 5.2 约束表达式

```ebnf
Constraint_Expression ::= Logical_Expression

Logical_Expression ::= Comparison_Expression (("and" | "or" | "xor" | "implies") Comparison_Expression)*
                     | "not" Comparison_Expression

Comparison_Expression ::= Additive_Expression (("=" | "!=" | "<" | ">" | "<=" | ">=" | "in") Additive_Expression)*

Additive_Expression ::= Multiplicative_Expression (("+" | "-") Multiplicative_Expression)*

Multiplicative_Expression ::= Unary_Expression (("*" | "/" | "%") Unary_Expression)*

Unary_Expression ::= ("+" | "-" | "!")? Primary_Expression

Primary_Expression ::= Literal
                     | Identifier
                     | "this"
                     | "self"
                     | Parenthesized_Expression
                     | Function_Call
                     | Path_Expression
                     | Conditional_Expression
```

### 5.3 标准约束

#### 5.3.1 数值约束

```ebnf
Numeric_Constraint ::= "min" ":" Number
                     | "max" ":" Number
                     | "exclusiveMin" ":" Number
                     | "exclusiveMax" ":" Number
                     | "multipleOf" ":" Number
```

**示例**:
```usl
field age: Integer {
  constraint: { min: 0, max: 150 }
}

field price: Decimal {
  constraint: { min: 0, exclusiveMax: 1000000 }
}

field evenNumber: Integer {
  constraint: { multipleOf: 2 }
}
```

#### 5.3.2 字符串约束

```ebnf
String_Constraint ::= "minLength" ":" Integer
                    | "maxLength" ":" Integer
                    | "pattern" ":" String
                    | "format" ":" String
                    | "enum" ":" Array_Literal
```

**示例**:
```usl
field username: String {
  constraint: {
    minLength: 3
    maxLength: 20
    pattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
  }
}

field email: String {
  constraint: {
    format: "email"
  }
}

field status: String {
  constraint: {
    enum: ["active", "inactive", "suspended"]
  }
}
```

#### 5.3.3 数组约束

```ebnf
Array_Constraint ::= "minItems" ":" Integer
                   | "maxItems" ":" Integer
                   | "uniqueItems" ":" Boolean
                   | "contains" ":" Constraint_Expression
```

**示例**:
```usl
field tags: Array<String> {
  constraint: {
    minItems: 1
    maxItems: 10
    uniqueItems: true
  }
}

field scores: Array<Integer> {
  constraint: {
    minItems: 3
    contains: { min: 100 }  // 至少有一个>=100
  }
}
```

#### 5.3.4 对象约束

```ebnf
Object_Constraint ::= "required" ":" Array_Literal
                    | "propertyNames" ":" Constraint_Expression
                    | "additionalProperties" ":" Boolean | Type_Expression
```

**示例**:
```usl
field config: Map<String, Any> {
  constraint: {
    required: ["host", "port"]
    propertyNames: { pattern: "^[a-z][a-zA-Z0-9]*$" }
  }
}
```

### 5.4 组合约束

```ebnf
Composite_Constraint ::= "allOf" ":" "[" Constraint_Expression ("," Constraint_Expression)* "]"
                       | "anyOf" ":" "[" Constraint_Expression ("," Constraint_Expression)* "]"
                       | "oneOf" ":" "[" Constraint_Expression ("," Constraint_Expression)* "]"
                       | "not" ":" Constraint_Expression
```

**示例**:
```usl
field password: String {
  constraint: {
    allOf: [
      { minLength: 8 }
      { pattern: ".*[A-Z].*" }  // 至少一个大写
      { pattern: ".*[a-z].*" }  // 至少一个小写
      { pattern: ".*[0-9].*" }  // 至少一个数字
    ]
  }
}
```

### 5.5 条件约束

```ebnf
Conditional_Constraint ::= "if" ":" Constraint_Expression
                           "then" ":" Constraint_Expression
                           ("else" ":" Constraint_Expression)?
```

**示例**:
```usl
schema Payment {
  field method: PaymentMethod
  field cardNumber: String?
  field paypalEmail: Email?
  
  constraint: {
    if: { method = "credit_card" }
    then: {
      cardNumber: { required: true, pattern: "^[0-9]{13,19}$" }
    }
    else: {
      if: { method = "paypal" }
      then: {
        paypalEmail: { required: true }
      }
    }
  }
}
```

### 5.6 自定义约束

```usl
constraint validateAge {
  expression: this.birthDate <= today().subYears(18)
  message: "Must be at least 18 years old"
  severity: "error"
}

constraint passwordStrength {
  expression: this.password.length >= 12 and 
              this.password.matches(".*[!@#$%^&*].*")
  message: "Password must be at least 12 characters with special symbols"
}

entity User {
  field birthDate: Date
  field password: String
  
  validateAge
  passwordStrength
}
```

---

## 6. 关系系统

### 6.1 关系定义

```ebnf
Relation_Definition ::= "relation" Identifier ":" Relation_Signature Relation_Attributes?

Relation_Signature ::= Relation_Type "(" Identifier "," Identifier ")"
                     | Identifier Relation_Operator Identifier

Relation_Type ::= "one_to_one" | "1:1"
                | "one_to_many" | "1:N" | "1:*"
                | "many_to_one" | "N:1" | "*:1"
                | "many_to_many" | "N:M" | "*:*"
                | "belongs_to"
                | "has_one"
                | "has_many"
                | "embedded"
                | "references"

Relation_Operator ::= "->" | "<-" | "<->" | "~>" | "<~"
```

### 6.2 关系类型

| 关系类型 | 说明 | 示例 |
|----------|------|------|
| `one_to_one` / `1:1` | 一对一 | 用户-用户详情 |
| `one_to_many` / `1:N` | 一对多 | 用户-订单 |
| `many_to_one` / `N:1` | 多对一 | 订单-用户 |
| `many_to_many` / `N:M` | 多对多 | 学生-课程 |
| `belongs_to` | 属于 | 订单属于用户 |
| `has_one` | 有一个 | 用户有一个档案 |
| `has_many` | 有多个 | 用户有多个订单 |
| `embedded` | 嵌入 | 地址嵌入用户 |
| `references` | 引用 | 外键引用 |

### 6.3 关系属性

```ebnf
Relation_Attributes ::= "{" Relation_Attribute ("," Relation_Attribute)* "}"

Relation_Attribute ::= "onDelete" ":" Cascade_Action
                     | "onUpdate" ":" Cascade_Action
                     | "through" ":" Identifier
                     | "as" ":" Identifier
                     | "orderBy" ":" Order_Specification
                     | "where" ":" Constraint_Expression
                     | "indexed" ":" Boolean

Cascade_Action ::= "CASCADE" | "SET_NULL" | "SET_DEFAULT" | "RESTRICT" | "NO_ACTION"
```

**示例**:
```usl
entity User {
  field id: UUID
  field name: String
  
  // 一对多关系
  relation orders: has_many(Order) {
    orderBy: createdAt desc
    where: { status != "deleted" }
  }
  
  // 一对一关系
  relation profile: has_one(Profile) {
    onDelete: CASCADE
  }
}

entity Order {
  field id: UUID
  field total: Decimal(19, 4)
  
  // 多对一关系
  relation user: belongs_to(User) {
    onDelete: RESTRICT
    indexed: true
  }
  
  // 多对多关系
  relation products: many_to_many(Product) {
    through: OrderProduct
  }
}

entity Product {
  field id: UUID
  field name: String
  
  relation orders: many_to_many(Order) {
    through: OrderProduct
  }
}

// 连接表
entity OrderProduct {
  relation order: belongs_to(Order)
  relation product: belongs_to(Product)
  field quantity: Integer
  field price: Decimal(19, 4)
}
```

### 6.4 关系约束

```usl
entity Order {
  field items: Array<OrderItem>
  field total: Decimal(19, 4)
  
  // 关系约束：总和必须等于各项之和
  constraint: total == items.sum(item => item.price * item.quantity)
}

entity Project {
  field startDate: Date
  field endDate: Date?
  relation tasks: has_many(Task)
  
  // 关系约束：所有任务日期必须在项目日期范围内
  constraint: tasks.all(task => 
    task.startDate >= this.startDate and
    (this.endDate == null or task.endDate <= this.endDate)
  )
}
```

---

## 7. 操作定义

### 7.1 操作类型

```ebnf
Operation_Definition ::= Query_Definition | Mutation_Definition | Subscription_Definition | RPC_Definition

Query_Definition ::= "query" Identifier Generic_Params? "(" Parameter_List? ")" (":" Type_Expression)? Operation_Body?

Mutation_Definition ::= "mutation" Identifier Generic_Params? "(" Parameter_List? ")" (":" Type_Expression)? Operation_Body?

Subscription_Definition ::= "subscription" Identifier Generic_Params? "(" Parameter_List? ")" (":" Type_Expression)? Operation_Body?

RPC_Definition ::= "rpc" Identifier Generic_Params? "(" Parameter_List? ")" (":" Type_Expression)? Operation_Body?
```

### 7.2 参数定义

```ebnf
Parameter_List ::= Parameter ("," Parameter)*

Parameter ::= Identifier ":" Type_Expression ("=" Value)?
            | Identifier "?" ":" Type_Expression
```

### 7.3 查询操作

```usl
schema UserAPI {
  // 简单查询
  query getUser(id: UUID): User
  
  // 带可选参数的查询
  query listUsers(
    page: Integer = 1,
    pageSize: Integer = 20,
    sortBy: String = "createdAt"
  ): PaginatedResult<User>
  
  // 带过滤的查询
  query searchUsers(
    keyword: String,
    filters: UserFilters?
  ): Array<User>
  
  // 复杂查询
  query getUserStats(userId: UUID, period: DateRange): UserStatistics
}
```

### 7.4 变更操作

```usl
schema OrderAPI {
  // 创建操作
  mutation createOrder(input: CreateOrderInput): Order
    throws ValidationError, PaymentError
  
  // 更新操作
  mutation updateOrder(
    id: UUID,
    input: UpdateOrderInput
  ): Order
    throws NotFoundError, ValidationError
  
  // 删除操作
  mutation deleteOrder(id: UUID): Boolean
    throws NotFoundError
  
  // 批量操作
  mutation batchUpdateOrders(
    ids: Array<UUID>,
    update: OrderUpdate
  ): BatchResult<Order>
}
```

### 7.5 订阅操作

```usl
schema RealTimeAPI {
  // 实时通知
  subscription orderUpdates(userId: UUID): OrderEvent
  
  // 带过滤的订阅
  subscription priceAlerts(
    productIds: Array<UUID>,
    threshold: Decimal
  ): PriceChangeEvent
}
```

### 7.6 RPC操作

```usl
schema AnalyticsAPI {
  // 计算型操作
  rpc calculateRevenue(period: DateRange): RevenueReport
  
  // 导出操作
  rpc exportReport(request: ExportRequest): ExportResult
    async: true
}
```

---

## 8. 标准库

### 8.1 数学函数

```usl
library Math {
  // 基础运算
  function abs(x: Number): Number
  function min(a: Number, b: Number): Number
  function max(a: Number, b: Number): Number
  function clamp(x: Number, min: Number, max: Number): Number
  
  // 幂运算
  function pow(base: Number, exp: Number): Number
  function sqrt(x: Number): Number
  function cbrt(x: Number): Number
  
  // 对数
  function log(x: Number): Number
  function log10(x: Number): Number
  function log2(x: Number): Number
  
  // 三角函数
  function sin(x: Number): Number
  function cos(x: Number): Number
  function tan(x: Number): Number
  function asin(x: Number): Number
  function acos(x: Number): Number
  function atan(x: Number): Number
  
  // 常量
  constant PI: Float64 = 3.141592653589793
  constant E: Float64 = 2.718281828459045
}
```

### 8.2 字符串函数

```usl
library String {
  // 查询
  function length(s: String): Integer
  function isEmpty(s: String): Boolean
  function contains(s: String, substr: String): Boolean
  function startsWith(s: String, prefix: String): Boolean
  function endsWith(s: String, suffix: String): Boolean
  function indexOf(s: String, substr: String): Integer
  function lastIndexOf(s: String, substr: String): Integer
  
  // 变换
  function toUpperCase(s: String): String
  function toLowerCase(s: String): String
  function trim(s: String): String
  function substring(s: String, start: Integer, end?: Integer): String
  function replace(s: String, pattern: String, replacement: String): String
  function replaceAll(s: String, pattern: String, replacement: String): String
  
  // 分割与连接
  function split(s: String, delimiter: String): Array<String>
  function join(parts: Array<String>, delimiter: String): String
  
  // 验证
  function matches(s: String, regex: String): Boolean
}
```

### 8.3 数组函数

```usl
library Array {
  // 查询
  function length<T>(arr: Array<T>): Integer
  function isEmpty<T>(arr: Array<T>): Boolean
  function contains<T>(arr: Array<T>, item: T): Boolean
  function indexOf<T>(arr: Array<T>, item: T): Integer
  function find<T>(arr: Array<T>, predicate: (T) => Boolean): T?
  function filter<T>(arr: Array<T>, predicate: (T) => Boolean): Array<T>
  
  // 变换
  function map<T, R>(arr: Array<T>, transform: (T) => R): Array<R>
  function flatMap<T, R>(arr: Array<T>, transform: (T) => Array<R>): Array<R>
  function reduce<T, Acc>(arr: Array<T>, initial: Acc, reducer: (Acc, T) => Acc): Acc
  function sort<T>(arr: Array<T>, comparator?: (T, T) => Integer): Array<T>
  function reverse<T>(arr: Array<T>): Array<T>
  function distinct<T>(arr: Array<T>): Array<T>
  
  // 聚合
  function sum<T extends Number>(arr: Array<T>): T
  function avg<T extends Number>(arr: Array<T>): Float64
  function min<T>(arr: Array<T>): T?
  function max<T>(arr: Array<T>): T?
  function groupBy<T, K>(arr: Array<T>, keySelector: (T) => K): Map<K, Array<T>>
}
```

### 8.4 日期时间函数

```usl
library DateTime {
  // 创建
  function now(): DateTime
  function today(): Date
  
  // 查询
  function year(dt: DateTime): Integer
  function month(dt: DateTime): Integer
  function day(dt: DateTime): Integer
  function hour(dt: DateTime): Integer
  function minute(dt: DateTime): Integer
  function second(dt: DateTime): Integer
  function dayOfWeek(dt: DateTime): Integer
  function dayOfYear(dt: DateTime): Integer
  
  // 运算
  function addDays(dt: DateTime, days: Integer): DateTime
  function addMonths(dt: DateTime, months: Integer): DateTime
  function addYears(dt: DateTime, years: Integer): DateTime
  function diff(dt1: DateTime, dt2: DateTime): Duration
  
  // 格式化
  function format(dt: DateTime, pattern: String): String
  function parse(text: String, pattern: String): DateTime
}
```

### 8.5 验证函数

```usl
library Validate {
  // 字符串验证
  function isEmail(s: String): Boolean
  function isURL(s: String): Boolean
  function isUUID(s: String): Boolean
  function isIPv4(s: String): Boolean
  function isIPv6(s: String): Boolean
  function isBase64(s: String): Boolean
  function isHex(s: String): Boolean
  
  // 数值验证
  function isInteger(s: String): Boolean
  function isFloat(s: String): Boolean
  function isPositive(n: Number): Boolean
  function isNegative(n: Number): Boolean
  
  // 类型验证
  function isNull(value: Any): Boolean
  function isDefined(value: Any): Boolean
  function isArray(value: Any): Boolean
  function isObject(value: Any): Boolean
  function isString(value: Any): Boolean
  function isNumber(value: Any): Boolean
}
```

---

## 9. 扩展机制

### 9.1 注解系统

```ebnf
Annotation_List ::= Annotation+

Annotation ::= "@" Annotation_Name ("(" Annotation_Params? ")")?

Annotation_Name ::= Identifier

Annotation_Params ::= Annotation_Param ("," Annotation_Param)*

Annotation_Param ::= Identifier "=" Value
```

**标准注解**:
```usl
@deprecated("Use newField instead")
@since("2.0.0")
@experimental
@readonly
@nullable
@required
@unique
@indexed
@sensitive  // 敏感数据，日志中脱敏
@computed   // 计算字段
@transient  // 不持久化
```

**自定义注解**:
```usl
// 定义注解
annotation auditLog {
  enabled: Boolean = true
  level: String = "info"
}

// 使用注解
@auditLog(enabled: true, level: "warn")
entity FinancialTransaction {
  field amount: Decimal
}
```

### 9.2 扩展块

```ebnf
Extension_Block ::= "extend" Extension_Target "{" Schema_Element* "}"

Extension_Target ::= "schema" Identifier
                   | "type" Identifier
                   | "enum" Identifier
                   | Identifier
```

**示例**:
```usl
// 扩展已有Schema
extend schema User {
  field avatar: URL?
  field bio: Text?
}

// 扩展现有类型
extend type String {
  constraint: {
    // 为所有String添加默认约束
  }
}
```

### 9.3 插件系统

```usl
// 插件声明
plugin "openapi-extensions" version "1.0.0"

// 使用插件扩展
@openapi.tag("User Management")
@openapi.operationId("getUserById")
query getUser(id: UUID): User
```

---

## 10. 互操作性

### 10.1 与JSON Schema互操作

USL可以完整表示JSON Schema的所有特性：

```usl
// USL
schema User {
  field name: String {
    constraint: {
      minLength: 1
      maxLength: 100
    }
  }
  field age: Integer? {
    constraint: { min: 0, max: 150 }
  }
}

// 等价JSON Schema
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 150
    }
  },
  "required": ["name"]
}
```

### 10.2 与OpenAPI互操作

```usl
// USL定义
schema PetAPI v1.0 {
  metadata {
    title: "Pet Store API"
    version: "1.0.0"
  }
  
  entity Pet {
    field id: UUID
    field name: String
    field status: PetStatus
  }
  
  enum PetStatus { available, pending, sold }
  
  query getPet(id: UUID): Pet
  mutation createPet(pet: Pet): Pet
}
```

### 10.3 与GraphQL互操作

USL支持GraphQL Schema的完整表达，并添加类型约束：

```usl
// USL
entity User {
  field id: ID!
  field email: String! { constraint: { format: "email" } }
  field name: String!
  field posts: Array<Post>!
}

entity Post {
  field id: ID!
  field title: String! { constraint: { maxLength: 200 } }
  field content: String!
  field author: User!
}

type Query {
  user(id: ID!): User
  users: Array<User>!
}
```

### 10.4 与Protocol Buffers互操作

```usl
// USL
entity User {
  field id: UUID  // -> string id = 1;
  field name: String  // -> string name = 2;
  field email: String  // -> string email = 3;
  field age: Int32  // -> int32 age = 4;
}

// 生成Protobuf
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int32 age = 4;
}
```

---

## 附录A：符合性测试套件

符合性测试分为三个级别：

- **Level 1**: 核心功能测试
- **Level 2**: 推荐功能测试
- **Level 3**: 扩展功能测试

## 附录B：变更日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-14 | 初始规范发布 |

---

**文档版本**: 1.0.0  
**最后更新**: 2026-02-14  
**维护者**: DSL Schema Standardization Consortium  
**许可证**: Apache 2.0
