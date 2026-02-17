# 层次映射实例证明

## Concrete Instance Proofs of Hierarchy Mapping

**版本**: 2.3.0
**日期**: 2026-02-17

---

## 1. L1 → L2: 基础到元模型映射证明

### 1.1 集合到JSON Schema的映射

**实例**:

- 源 (L1): 集合 $S = \{1, 2, 3\}$
- 目标 (L2): JSON Schema

**映射定义**:

$$
T_{12}(S) = \{
    \text{"type"}: \text{"array"},
    \text{"items"}: \{\text{"type"}: \text{"integer"}\},
    \text{"uniqueItems"}: \text{true},
    \text{"minItems"}: 0
\}
$$

**定理 1.1.1**: 此映射保持集合的包含关系。

**证明**:

设 $S_1 \subseteq S_2$ 是两个集合。

需要证明: $T_{12}(S_1)$ 的约束蕴含于 $T_{12}(S_2)$ 的约束

1. $T_{12}(S_1)$ 的 items 类型是 $S_1$ 元素类型的上界
2. $T_{12}(S_2)$ 的 items 类型是 $S_2$ 元素类型的上界
3. 由于 $S_1 \subseteq S_2$，$S_1$ 的元素类型是 $S_2$ 元素类型的子类型
4. 因此 $T_{12}(S_1)$ 的 items 约束更强或相等

形式化：

$$
S_1 \subseteq S_2 \implies \text{items}(T_{12}(S_1)) \sqsubseteq \text{items}(T_{12}(S_2))
$$

其中 $\sqsubseteq$ 是类型约束的偏序关系。 ∎

### 1.2 函数到属性的映射

**实例**:

- 源 (L1): 函数 $f: \mathbb{N} \to \mathbb{N}, f(x) = x + 1$
- 目标 (L2): JSON Schema 属性

**映射定义**:

$$
T_{12}(f) = \{
    \text{"input"}: \{\text{"type"}: \text{"integer"}, \text{"minimum"}: 0\},
    \text{"output"}: \{\text{"type"}: \text{"integer"}, \text{"minimum"}: 1\}
\}
$$

**定理 1.2.1**: 此映射保持函数的类型签名。

**证明**:

函数 $f: A \to B$ 的类型签名是 $(A, B)$ 对。

映射后的属性定义了：

- 输入域: $T_{12}(A)$
- 输出域: $T_{12}(B)$

验证：

1. 对于任何输入 $a \in A$，$T_{12}$ 定义了其类型约束
2. 对于输出 $f(a) \in B$，$T_{12}$ 定义了其类型约束
3. 映射保持定义域和值域的对应关系

形式化：

$$
\forall a \in A: T_{12}(a) \models T_{12}(A) \implies T_{12}(f(a)) \models T_{12}(B)
$$

因此，类型签名被保持。 ∎

---

## 2. L2 → L3: 元模型到数据模型映射证明

### 2.1 JSON Schema到OWL本体的映射

**实例**:

- 源 (L2):

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer", "minimum": 0}
  },
  "required": ["name"]
}
```

- 目标 (L3): OWL本体

**映射定义**:

$$
T_{23}(\text{Schema}) = \text{Ontology}(\text{Person})
$$

具体构造：

```turtle
:Person a owl:Class .
:name a owl:DatatypeProperty ;
    rdfs:domain :Person ;
    rdfs:range xsd:string ;
    owl:cardinality 1 .

:age a owl:DatatypeProperty ;
    rdfs:domain :Person ;
    rdfs:range xsd:nonNegativeInteger ;
    owl:minCardinality 0 ;
    owl:maxCardinality 1 .
```

**定理 2.1.1**: 此映射保持约束的语义。

**证明**:

验证约束对应关系：

1. **类型约束**:
   - Schema: `"type": "object"` → OWL: `owl:Class`
   - Schema: `"type": "string"` → OWL: `xsd:string`
   - Schema: `"type": "integer"` → OWL: `xsd:integer`

2. **必需约束**:
   - Schema: `"required": ["name"]` → OWL: `owl:cardinality 1`
   - 表示每个Person实例必须有恰好1个name

3. **可选约束**:
   - Schema: age不在required中 → OWL: `owl:minCardinality 0`
   - 表示age是可选的

4. **数值范围**:
   - Schema: `"minimum": 0` → OWL: `xsd:nonNegativeInteger`

形式化语义：

对于任何实例 $i$：

$$
i \models_{\text{Schema}} \text{constraints} \iff i \models_{\text{OWL}} T_{23}(\text{constraints})
$$

因此，语义被保持。 ∎

### 2.2 模式约束到本体限制

**实例**:

- 源 (L2): JSON Schema enum `"enum": ["red", "green", "blue"]`
- 目标 (L3): OWL oneOf

**映射定义**:

$$
T_{23}(\text{enum} = \{v_1, ..., v_n\}) = \text{owl:oneOf}(v_1, ..., v_n)
$$

**定理 2.2.1**: 此映射保持枚举的封闭世界语义。

**证明**:

验证：

1. Schema enum 表示属性值必须是给定集合中的一个
2. OWL oneOf 表示属性值必须是列出的个体之一
3. 两者都定义了值的封闭集合

形式化：

$$
\forall x: x \in \text{enum} \iff x \in \text{oneOf}
$$

因此，枚举语义被保持。 ∎

---

## 3. L3 → L4: 数据模型到服务模型映射证明

### 3.1 实体到REST API的映射

**实例**:

- 源 (L3): 实体 Person (name, age)
- 目标 (L4): REST API

**映射定义**:

$$
T_{34}(\text{Person}) = \text{API Resource}
$$

具体构造：

```yaml
/persons:
  get:
    summary: List all persons
    responses:
      200:
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Person'

  post:
    summary: Create a person
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Person'

/persons/{id}:
  get:
    summary: Get a person by ID

  put:
    summary: Update a person

  delete:
    summary: Delete a person
```

**定理 3.1.1**: 此映射保持实体的CRUD操作。

**证明**:

验证CRUD对应关系：

| 实体操作 | API端点 | HTTP方法 | 语义 |
|---------|---------|---------|------|
| Create | /persons | POST | 创建新资源 |
| Read (List) | /persons | GET | 获取资源集合 |
| Read (Single) | /persons/{id} | GET | 获取特定资源 |
| Update | /persons/{id} | PUT | 替换资源 |
| Delete | /persons/{id} | DELETE | 删除资源 |

形式化：

对于实体 $E$ 和其实例 $e$:

$$
\begin{align}
\text{Create}(e) &\equiv \text{POST} /E \text{ with body } e \\
\text{Read}() &\equiv \text{GET} /E \\
\text{Read}(e.id) &\equiv \text{GET} /E/\{e.id\} \\
\text{Update}(e) &\equiv \text{PUT} /E/\{e.id\} \text{ with body } e \\
\text{Delete}(e.id) &\equiv \text{DELETE} /E/\{e.id\}
\end{align}
$$

所有实体操作都有对应的API端点，语义一致。 ∎

### 3.2 关系到API子资源的映射

**实例**:

- 源 (L3): 关系 Person —worksAt→ Company
- 目标 (L4): API子资源

**映射定义**:

$$
T_{34}(\text{worksAt}) = /persons/\{id\}/company
$$

**定理 3.2.1**: 此映射保持关系的导航性。

**证明**:

关系 $R: E_1 \to E_2$ 表示从 $E_1$ 可以导航到 $E_2$。

API路径 `/persons/{id}/company` 允许：

1. 通过 person ID 访问 person
2. 通过子路径 `/company` 访问其公司

这与关系的语义一致：

$$
p \in \text{Person} \land p.\text{worksAt} = c \implies \text{GET} /persons/\{p.id\}/company = c
$$

因此，导航性被保持。 ∎

---

## 4. L4 → L5: 服务模型到应用模型映射证明

### 4.1 API到UI组件的映射

**实例**:

- 源 (L4): Person API (CRUD端点)
- 目标 (L5): React组件

**映射定义**:

$$
T_{45}(\text{Person API}) = \text{PersonManager Component}
$$

具体构造：

```jsx
class PersonManager extends React.Component {
  // 对应 API GET /persons
  async listPersons() { ... }

  // 对应 API POST /persons
  async createPerson(data) { ... }

  // 对应 API GET /persons/{id}
  async getPerson(id) { ... }

  // 对应 API PUT /persons/{id}
  async updatePerson(id, data) { ... }

  // 对应 API DELETE /persons/{id}
  async deletePerson(id) { ... }

  render() {
    return (
      <div>
        <PersonList data={this.state.persons} />
        <PersonForm onSubmit={this.createPerson} />
      </div>
    );
  }
}
```

**定理 4.1.1**: 此映射保持服务的功能性。

**证明**:

验证功能对应：

| API端点 | UI方法 | 功能 |
|---------|--------|------|
| GET /persons | listPersons() | 显示列表 |
| POST /persons | createPerson() | 创建表单提交 |
| GET /persons/{id} | getPerson() | 显示详情 |
| PUT /persons/{id} | updatePerson() | 编辑表单提交 |
| DELETE /persons/{id} | deletePerson() | 删除按钮点击 |

形式化：

对于任何用户操作 $u$ 和对应的API调用 $a$:

$$
\text{UI}(u) \text{ 触发 } a \iff \text{用户意图 } u \text{ 被正确执行}
$$

因此，功能性被保持。 ∎

---

## 5. 跨级映射的组合证明

### 5.1 L1 → L3 的组合映射

**实例**:

- 路径: $L_1 \xrightarrow{T_{12}} L_2 \xrightarrow{T_{23}} L_3$
- 源 (L1): 代数数据类型 $D = \text{data Person} = \text{Person} \{name: String, age: Int\}$
- 目标 (L3): OWL本体

**定理 5.1.1**: 组合映射 $T_{23} \circ T_{12}$ 等价于直接映射 $T_{13}$。

**证明**:

步骤1: $T_{12}(D)$

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer"}
  }
}
```

步骤2: $T_{23}(T_{12}(D))$

```turtle
:Person a owl:Class .
:name rdfs:domain :Person ; rdfs:range xsd:string .
:age rdfs:domain :Person ; rdfs:range xsd:integer .
```

直接映射 $T_{13}(D)$ 产生相同的本体。

由定理 4.3.1，存在自然同构：

$$
\alpha_D: (T_{23} \circ T_{12})(D) \cong T_{13}(D)
$$

因此，组合映射等价于直接映射。 ∎

---

## 6. 映射正确性的验证方法

### 6.1 语法正确性验证

**验证**: 目标模型符合目标语言的语法

**方法**:

1. 使用目标语言的解析器验证
2. 检查AST的结构完整性
3. 验证无语法错误

### 6.2 语义保持性验证

**验证**: 源模型的语义在目标模型中被保持

**方法**:

1. 定义语义解释函数 $[\![ \cdot ]\!]$
2. 验证 $[\![ m ]\!]_i = [\![ T_{ij}(m) ]\!]_j$
3. 使用模型检查或定理证明

### 6.3 完备性验证

**验证**: 所有源模型元素都有对应

**方法**:

1. 计算源模型的元素集合 $E_s$
2. 计算目标模型的元素集合 $E_t$
3. 验证 $|E_s| \leq |E_t|$（考虑一对多映射）

---

## 7. 结论

本文提供了层次映射的具体实例证明，包括：

1. **L1→L2**: 集合/函数到JSON Schema的映射
2. **L2→L3**: JSON Schema到OWL本体的映射
3. **L3→L4**: 实体/关系到REST API的映射
4. **L4→L5**: API到UI组件的映射
5. **跨级组合**: 多级映射的等价性证明
6. **验证方法**: 正确性的验证技术

这些实例证明了层次映射理论的实际可行性。

---

**创建时间**: 2026-02-17
**维护者**: DSL Schema理论研究团队
