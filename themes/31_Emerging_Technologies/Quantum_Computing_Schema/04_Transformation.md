# 量子计算Schema转换体系

## 📑 目录

- [量子计算Schema转换体系](#量子计算schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 转换方向](#2-转换方向)
  - [3. QASM转换](#3-qasm转换)
    - [3.1 Quantum_Computing → QASM 2.0转换](#31-quantum_computing--qasm-20转换)
    - [3.2 Quantum_Computing → OpenQASM 3.0转换](#32-quantum_computing--openqasm-30转换)
    - [3.3 QASM解析与验证](#33-qasm解析与验证)
  - [4. Qiskit转换](#4-qiskit转换)
    - [4.1 生成Qiskit代码](#41-生成qiskit代码)
    - [4.2 从Qiskit导入](#42-从qiskit导入)
  - [5. Cirq转换](#5-cirq转换)
  - [6. Q#转换](#6-q转换)
  - [7. PostgreSQL存储](#7-postgresql存储)
  - [8. JSON转换](#8-json转换)
  - [9. 噪声模型转换](#9-噪声模型转换)
  - [10. 算法模板系统](#10-算法模板系统)
    - [10.1 Bell态模板](#101-bell态模板)
    - [10.2 GHZ态模板](#102-ghz态模板)
    - [10.3 Grover搜索模板](#103-grover搜索模板)
    - [10.4 Shor算法模板](#104-shor算法模板)
    - [10.5 QAOA模板](#105-qaoa模板)
    - [10.6 VQE模板](#106-vqe模板)
  - [11. 转换工具与API](#11-转换工具与api)
  - [12. 转换验证](#12-转换验证)

---

## 1. 转换体系概述

量子计算Schema转换体系支持**量子计算Schema到各种格式的转换**，包括QASM、Qiskit、Cirq、Q#等格式，以及PostgreSQL数据库存储和JSON序列化。

**转换目标**：

- **QASM/OpenQASM格式**：量子汇编语言标准
- **Qiskit Python代码**：IBM量子计算框架
- **Cirq Python代码**：Google量子计算框架
- **Q#代码**：Microsoft量子编程语言
- **PostgreSQL数据库**：持久化存储
- **JSON格式**：数据交换与序列化

**转换架构**：

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Quantum_Computing_Schema                     │
│                         (DSL Schema)                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┬────────────┐
        ▼            ▼            ▼            ▼            ▼
   ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
   │  QASM   │ │  Qiskit  │ │   Cirq   │ │    Q#    │ │   JSON   │
   │2.0 / 3.0│ │  Python  │ │  Python  │ │   Code   │ │  Schema  │
   └─────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## 2. 转换方向

### 2.1 转换矩阵

| 转换方向 | 源格式 | 目标格式 | 转换复杂度 | 工具支持 | 数据完整性 | 推荐工具 |
|---------|--------|----------|------------|----------|------------|----------|
| **Quantum_Computing → QASM** | Quantum_Computing_Schema | QASM 2.0 | ⭐⭐⭐ | ✅ 良好 | 高 | schema_qasm_integration.py |
| **Quantum_Computing → OpenQASM** | Quantum_Computing_Schema | OpenQASM 3.0 | ⭐⭐⭐ | ✅ 良好 | 高 | schema_qasm_integration.py |
| **QASM → Quantum_Computing** | QASM 2.0/3.0 | Quantum_Computing_Schema | ⭐⭐⭐⭐ | ✅ 良好 | 高 | QASMParser |
| **Quantum_Computing → Qiskit** | Quantum_Computing_Schema | Qiskit Python | ⭐⭐⭐ | ✅ 良好 | 高 | CircuitConverter |
| **Quantum_Computing → Cirq** | Quantum_Computing_Schema | Cirq Python | ⭐⭐⭐ | ✅ 良好 | 高 | CircuitConverter |
| **Quantum_Computing → Q#** | Quantum_Computing_Schema | Q#代码 | ⭐⭐⭐⭐ | ⚠️ 有限 | 中 | 手动转换 |
| **Quantum_Computing → PostgreSQL** | Quantum_Computing_Schema | SQL DDL | ⭐⭐⭐ | ✅ 良好 | 高 | 自定义转换器 |
| **Quantum_Computing → JSON** | Quantum_Computing_Schema | JSON Schema | ⭐⭐ | ✅ 良好 | 高 | CircuitConverter |
| **JSON → Quantum_Computing** | JSON Schema | Quantum_Computing_Schema | ⭐⭐ | ✅ 良好 | 高 | CircuitConverter |

### 2.2 转换流程

```text
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Schema解析                                          │
│  - 解析Quantum_Computing_Schema DSL                          │
│  - 提取量子比特、门操作、测量信息                              │
└─────────────────────────────────┬───────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 语义分析                                            │
│  - 验证电路有效性                                             │
│  - 检查量子门兼容性                                           │
│  - 分析依赖关系                                               │
└─────────────────────────────────┬───────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 目标代码生成                                         │
│  - 生成目标格式代码                                           │
│  - 添加必要的头文件和导入                                       │
│  - 优化输出格式                                               │
└─────────────────────────────────┬───────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 验证与测试                                          │
│  - 语法验证                                                   │
│  - 语义等价性验证                                             │
│  - 模拟执行对比                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. QASM转换

### 3.1 Quantum_Computing → QASM 2.0转换

**转换函数定义**：

```text
to_qasm2: Quantum_Computing_Schema → QASM2_String
```

**转换规则**：

```text
to_qasm2(schema) =
  "OPENQASM 2.0;\n" +
  "include \"qelib1.inc\";\n" +
  to_qasm_qubits(schema.qubits) +
  to_qasm_classical_bits(schema.classical_bits) +
  concat(to_qasm_gate(gate) for gate in schema.gates) +
  concat(to_qasm_measurement(m) for m in schema.measurements) +
  concat(to_qasm_noise(n) for n in schema.noise_models)
```

**转换示例**：

**输入（Quantum_Computing_Schema）**：

```dsl
circuit Bell_State {
  qubits: [q0, q1]
  classical_bits: [c0, c1]
  gates: [
    Hadamard(q0),
    CNOT(q0, q1)
  ]
  measurements: [Measure(q0, c0), Measure(q1, c1)]
}
```

**输出（QASM 2.0）**：

```qasm
OPENQASM 2.0;
include "qelib1.inc";

// Circuit: Bell_State
// Qubits: 2
// Classical bits: 2

qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

**单量子比特门映射**：

| Schema门类型 | QASM 2.0 | 矩阵表示 |
|-------------|----------|----------|
| Pauli_X | `x q[i];` | [[0,1],[1,0]] |
| Pauli_Y | `y q[i];` | [[0,-i],[i,0]] |
| Pauli_Z | `z q[i];` | [[1,0],[0,-1]] |
| Hadamard | `h q[i];` | 1/√2 [[1,1],[1,-1]] |
| Phase (S) | `s q[i];` | [[1,0],[0,i]] |
| T_Gate | `t q[i];` | [[1,0],[0,e^(iπ/4)]] |
| RX(θ) | `rx(θ) q[i];` | 旋转矩阵 |
| RY(θ) | `ry(θ) q[i];` | 旋转矩阵 |
| RZ(φ) | `rz(φ) q[i];` | 旋转矩阵 |

**多量子比特门映射**：

| Schema门类型 | QASM 2.0 | 描述 |
|-------------|----------|------|
| CNOT | `cx q[c], q[t];` | 受控非门 |
| CZ | `cz q[c], q[t];` | 受控Z门 |
| SWAP | `swap q[i], q[j];` | 交换门 |
| CCX (Toffoli) | `ccx q[c1], q[c2], q[t];` | 双控非门 |
| CSWAP (Fredkin) | `cswap q[c], q[i], q[j];` | 受控交换门 |

### 3.2 Quantum_Computing → OpenQASM 3.0转换

**转换函数定义**：

```text
to_qasm3: Quantum_Computing_Schema → OpenQASM3_String
```

**转换规则**：

```text
to_qasm3(schema) =
  "OPENQASM 3.0;\n" +
  "include \"stdgates.inc\";\n" +
  to_openqasm3_qubits(schema.qubits) +
  to_openqasm3_classical_bits(schema.classical_bits) +
  concat(to_openqasm3_gate(gate) for gate in schema.gates) +
  concat(to_openqasm3_measurement(m) for m in schema.measurements)
```

**OpenQASM 3.0特性支持**：

- **类型系统**：`qubit`, `bit`, `angle`, `duration`
- **经典控制**：`if`语句、`for`循环
- **自定义门**：`gate`定义
- **延迟指令**：`delay`, `barrier`
- **脉冲级指令**：`play`, `capture`

**转换示例**：

**输出（OpenQASM 3.0）**：

```qasm
OPENQASM 3.0;
include "stdgates.inc";

// Circuit: Bell_State
// Qubits: 2
// Classical bits: 2

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];
```

**寄存器声明对比**：

| 版本 | 量子寄存器 | 经典寄存器 |
|------|-----------|-----------|
| QASM 2.0 | `qreg q[n];` | `creg c[n];` |
| OpenQASM 3.0 | `qubit[n] q;` | `bit[n] c;` |

**测量指令对比**：

| 版本 | 语法 |
|------|------|
| QASM 2.0 | `measure q[i] -> c[j];` |
| OpenQASM 3.0 | `c[j] = measure q[i];` |

### 3.3 QASM解析与验证

**解析器架构**：

```python
class QASMParser:
    """QASM解析器"""
    
    def parse(self, qasm_string: str) -> QuantumCircuit:
        # 1. 词法分析
        tokens = self._tokenize(qasm_string)
        
        # 2. 语法分析
        ast = self._parse_tokens(tokens)
        
        # 3. 语义分析
        circuit = self._build_circuit(ast)
        
        # 4. 验证
        self._validate(circuit)
        
        return circuit
```

**解析步骤**：

```text
输入QASM代码
     │
     ▼
┌─────────────────┐
│   词法分析器     │  → 生成Token序列
│   (Tokenizer)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   语法分析器     │  → 生成AST
│    (Parser)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   语义分析器     │  → 构建电路对象
│  (Semantic)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   验证器         │  → 有效性检查
│  (Validator)    │
└────────┬────────┘
         │
         ▼
   QuantumCircuit对象
```

**验证规则**：

```dsl
constraint valid_qasm(qasm: String): Boolean {
  // 1. 版本声明检查
  require: qasm.contains("OPENQASM")
  
  // 2. 寄存器定义检查
  require: all_registers_defined_before_use(qasm)
  
  // 3. 量子比特索引检查
  require: all_qubit_indices_in_range(qasm)
  
  // 4. 门操作有效性检查
  require: all_gates_valid(qasm)
  
  // 5. 测量操作检查
  require: measurements_valid(qasm)
  
  return true
}
```

---

## 4. Qiskit转换

### 4.1 生成Qiskit代码

**转换函数定义**：

```text
to_qiskit: Quantum_Computing_Schema → Qiskit_Python_Code
```

**转换规则**：

```text
to_qiskit(schema) =
  "from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister\n" +
  "from qiskit import execute, Aer\n\n" +
  "qc = QuantumCircuit(" + schema.num_qubits + ", " + schema.num_classical_bits + ")\n" +
  concat(to_qiskit_gate(gate) for gate in schema.gates) +
  "\nsimulator = Aer.get_backend('qasm_simulator')\n" +
  "result = execute(qc, simulator).result()\n" +
  "print(result.get_counts(qc))\n"
```

**门映射表**：

| Schema门 | Qiskit方法 | 参数 |
|---------|-----------|------|
| Pauli_X | `qc.x(qubit)` | - |
| Pauli_Y | `qc.y(qubit)` | - |
| Pauli_Z | `qc.z(qubit)` | - |
| Hadamard | `qc.h(qubit)` | - |
| RX(θ) | `qc.rx(theta, qubit)` | theta: float |
| RY(θ) | `qc.ry(theta, qubit)` | theta: float |
| RZ(φ) | `qc.rz(phi, qubit)` | phi: float |
| CNOT | `qc.cx(control, target)` | - |
| CZ | `qc.cz(control, target)` | - |
| SWAP | `qc.swap(qubit1, qubit2)` | - |
| CCX | `qc.ccx(c1, c2, target)` | - |
| Measure | `qc.measure(qubit, cbit)` | - |

**转换示例**：

**输入**：

```dsl
circuit GHZ_State {
  qubits: [q0, q1, q2]
  classical_bits: [c0, c1, c2]
  gates: [
    Hadamard(q0),
    CNOT(q0, q1),
    CNOT(q1, q2)
  ]
}
```

**输出**：

```python
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer

# Create circuit: GHZ_State
qc = QuantumCircuit(3, 3)

qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure([0, 1, 2], [0, 1, 2])

# Execute
simulator = Aer.get_backend('qasm_simulator')
result = execute(qc, simulator).result()
counts = result.get_counts(qc)
print(counts)
```

### 4.2 从Qiskit导入

**转换函数定义**：

```text
from_qiskit: Qiskit_QuantumCircuit → Quantum_Computing_Schema
```

**提取规则**：

```python
def from_qiskit(qc: QuantumCircuit) -> QuantumCircuitSchema:
    schema = QuantumCircuitSchema()
    
    # 提取量子比特数量
    schema.num_qubits = qc.num_qubits
    
    # 提取经典比特数量
    schema.num_classical_bits = qc.num_clbits
    
    # 提取门操作
    for instruction in qc.data:
        gate = extract_gate(instruction)
        schema.gates.append(gate)
    
    return schema
```

---

## 5. Cirq转换

**转换函数定义**：

```text
to_cirq: Quantum_Computing_Schema → Cirq_Python_Code
```

**转换规则**：

```text
to_cirq(schema) =
  "import cirq\n\n" +
  "qubits = [cirq.GridQubit(0, i) for i in range(" + schema.num_qubits + ")]\n" +
  "circuit = cirq.Circuit()\n" +
  concat(to_cirq_operation(gate) for gate in schema.gates) +
  "\nsimulator = cirq.Simulator()\n" +
  "result = simulator.run(circuit)\n" +
  "print(result)\n"
```

**门映射表**：

| Schema门 | Cirq操作 |
|---------|---------|
| Pauli_X | `cirq.X(qubit)` |
| Pauli_Y | `cirq.Y(qubit)` |
| Pauli_Z | `cirq.Z(qubit)` |
| Hadamard | `cirq.H(qubit)` |
| RX(θ) | `cirq.rx(theta)(qubit)` |
| CNOT | `cirq.CNOT(control, target)` |
| CZ | `cirq.CZ(qubit1, qubit2)` |
| SWAP | `cirq.SWAP(qubit1, qubit2)` |

**转换示例**：

```python
import cirq

# Create circuit: Bell_State
qubits = [cirq.GridQubit(0, i) for i in range(2)]
circuit = cirq.Circuit()

circuit.append(cirq.H(qubits[0]))
circuit.append(cirq.CNOT(qubits[0], qubits[1]))
circuit.append(cirq.measure(qubits[0], key='q0'))
circuit.append(cirq.measure(qubits[1], key='q1'))

# Execute
simulator = cirq.Simulator()
result = simulator.run(circuit)
print(result)
```

---

## 6. Q#转换

**转换函数定义**：

```text
to_qsharp: Quantum_Computing_Schema → QSharp_Code
```

**转换规则**：

Q#转换相对复杂，因为Q#使用不同的编程范式。主要转换策略：

```text
to_qsharp(schema) =
  "namespace Quantum.Circuit {\n" +
  "  open Microsoft.Quantum.Canon;\n" +
  "  open Microsoft.Quantum.Intrinsic;\n\n" +
  "  operation " + schema.name + "() : Result[] {\n" +
  "    use qubits = Qubit[" + schema.num_qubits + "];\n" +
  "    mutable results = new Result[" + schema.num_qubits + "];\n" +
  concat(to_qsharp_operation(gate) for gate in schema.gates) +
  "    return results;\n" +
  "  }\n" +
  "}\n"
```

**门映射表**：

| Schema门 | Q#操作 |
|---------|--------|
| Pauli_X | `X(qubits[i])` |
| Pauli_Y | `Y(qubits[i])` |
| Pauli_Z | `Z(qubits[i])` |
| Hadamard | `H(qubits[i])` |
| RX(θ) | `Rx(theta, qubits[i])` |
| CNOT | `CNOT(qubits[c], qubits[t])` |
| Measure | `M(qubits[i])` |

**转换示例**：

```qsharp
namespace Quantum.Circuit {
  open Microsoft.Quantum.Canon;
  open Microsoft.Quantum.Intrinsic;
  open Microsoft.Quantum.Measurement;

  operation BellState() : Result[] {
    use qubits = Qubit[2];
    mutable results = new Result[2];
    
    // Apply gates
    H(qubits[0]);
    CNOT(qubits[0], qubits[1]);
    
    // Measure
    set results w/= 0 <- M(qubits[0]);
    set results w/= 1 <- M(qubits[1]);
    
    // Reset
    ResetAll(qubits);
    
    return results;
  }
}
```

---

## 7. PostgreSQL存储

### 7.1 数据库Schema设计

**量子电路表**：

```sql
CREATE TABLE quantum_circuits (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    qubit_count INTEGER NOT NULL,
    gate_count INTEGER NOT NULL,
    depth INTEGER,
    circuit_json JSONB NOT NULL,
    qasm_text TEXT,
    openqasm3_text TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quantum_circuits_name ON quantum_circuits(name);
CREATE INDEX idx_quantum_circuits_qubit_count ON quantum_circuits(qubit_count);
CREATE INDEX idx_quantum_circuits_metadata ON quantum_circuits USING GIN (metadata);
```

**量子门表**：

```sql
CREATE TABLE quantum_gates (
    id VARCHAR(50) PRIMARY KEY,
    circuit_id VARCHAR(50) REFERENCES quantum_circuits(id) ON DELETE CASCADE,
    gate_type VARCHAR(50) NOT NULL,
    qubits INTEGER[] NOT NULL,
    parameters JSONB,
    gate_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quantum_gates_circuit_id ON quantum_gates(circuit_id);
CREATE INDEX idx_quantum_gates_type ON quantum_gates(gate_type);
```

**量子算法表**：

```sql
CREATE TABLE quantum_algorithms (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    algorithm_type VARCHAR(50) NOT NULL,  -- grover, shor, qaoa, vqe
    description TEXT,
    input_qubits INTEGER NOT NULL,
    output_qubits INTEGER NOT NULL,
    complexity_time VARCHAR(50),
    complexity_space VARCHAR(50),
    circuit_id VARCHAR(50) REFERENCES quantum_circuits(id),
    algorithm_json JSONB NOT NULL,
    reference_implementation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quantum_algorithms_name ON quantum_algorithms(name);
CREATE INDEX idx_quantum_algorithms_type ON quantum_algorithms(algorithm_type);
```

**噪声模型表**：

```sql
CREATE TABLE noise_models (
    id VARCHAR(50) PRIMARY KEY,
    circuit_id VARCHAR(50) REFERENCES quantum_circuits(id) ON DELETE CASCADE,
    noise_type VARCHAR(50) NOT NULL,
    target_qubits INTEGER[] NOT NULL,
    probability FLOAT NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_noise_models_circuit_id ON noise_models(circuit_id);
```

### 7.2 数据存储示例

**存储量子电路**：

```sql
INSERT INTO quantum_circuits (
    id, name, description, qubit_count, gate_count, depth,
    circuit_json, qasm_text, metadata
) VALUES (
    'bell_state_001',
    'Bell State Circuit',
    '生成贝尔态的标准量子电路',
    2,
    3,
    2,
    '{
        "name": "Bell_State",
        "num_qubits": 2,
        "num_classical_bits": 2,
        "gates": [
            {"type": "h", "qubits": [0]},
            {"type": "cx", "qubits": [0, 1]},
            {"type": "measure", "qubits": [0], "classical_bits": [0]},
            {"type": "measure", "qubits": [1], "classical_bits": [1]}
        ]
    }',
    'OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];',
    '{"category": "basic", "tags": ["entanglement", "bell-state"]}'
);
```

**存储Grover算法**：

```sql
INSERT INTO quantum_algorithms (
    id, name, algorithm_type, description,
    input_qubits, output_qubits,
    complexity_time, complexity_space,
    algorithm_json
) VALUES (
    'grover_search_001',
    'Grover Search Algorithm',
    'grover',
    '在未排序数据库中搜索目标元素的量子算法',
    4,
    4,
    'O(√N)',
    'O(n)',
    '{
        "target": 5,
        "iterations": 4,
        "steps": [
            "Initialize |+⟩^⊗n",
            "Repeat √N times { Oracle, Diffusion }",
            "Measure"
        ]
    }'
);
```

---

## 8. JSON转换

### 8.1 JSON Schema定义

**量子电路JSON Schema**：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Quantum Circuit",
  "type": "object",
  "required": ["name", "num_qubits", "gates"],
  "properties": {
    "name": {
      "type": "string",
      "description": "电路名称"
    },
    "num_qubits": {
      "type": "integer",
      "minimum": 1,
      "description": "量子比特数量"
    },
    "num_classical_bits": {
      "type": "integer",
      "minimum": 0,
      "description": "经典比特数量"
    },
    "gates": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/quantum_gate"
      }
    },
    "noise_models": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/noise_model"
      }
    },
    "metadata": {
      "type": "object"
    }
  },
  "definitions": {
    "quantum_gate": {
      "type": "object",
      "required": ["type", "qubits"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["x", "y", "z", "h", "s", "t", "rx", "ry", "rz", "cx", "cz", "swap", "measure"]
        },
        "qubits": {
          "type": "array",
          "items": {"type": "integer"}
        },
        "parameters": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "value": {"type": "number"}
            }
          }
        },
        "classical_bits": {
          "type": "array",
          "items": {"type": "integer"}
        }
      }
    },
    "noise_model": {
      "type": "object",
      "required": ["type", "qubits", "probability"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["depolarizing", "amplitude_damping", "phase_damping", "bit_flip", "phase_flip"]
        },
        "qubits": {
          "type": "array",
          "items": {"type": "integer"}
        },
        "probability": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        }
      }
    }
  }
}
```

### 8.2 转换示例

**Bell态JSON表示**：

```json
{
  "name": "Bell_State",
  "num_qubits": 2,
  "num_classical_bits": 2,
  "gates": [
    {
      "type": "h",
      "qubits": [0],
      "parameters": [],
      "classical_bits": []
    },
    {
      "type": "cx",
      "qubits": [0, 1],
      "parameters": [],
      "classical_bits": []
    },
    {
      "type": "measure",
      "qubits": [0],
      "parameters": [],
      "classical_bits": [0]
    },
    {
      "type": "measure",
      "qubits": [1],
      "parameters": [],
      "classical_bits": [1]
    }
  ],
  "noise_models": [],
  "metadata": {
    "category": "basic",
    "tags": ["entanglement", "bell-state"]
  }
}
```

---

## 9. 噪声模型转换

### 9.1 噪声模型类型

**支持的噪声类型**：

| 噪声类型 | 描述 | 参数 |
|---------|------|------|
| Depolarizing | 退极化噪声 | probability |
| Amplitude Damping | 幅度阻尼 | gamma |
| Phase Damping | 相位阻尼 | lambda |
| Bit Flip | 比特翻转 | probability |
| Phase Flip | 相位翻转 | probability |
| Bit-Phase Flip | 比特相位翻转 | probability |
| Thermal Relaxation | 热弛豫 | T1, T2, time |
| Readout Error | 读出误差 | p0given1, p1given0 |

### 9.2 QASM噪声表示

**注释形式**（OpenQASM 2.0）：

```qasm
// noise depolarizing(0.01) q[0];
h q[0];
// noise bit_flip(0.02) q[1];
cx q[0], q[1];
```

**原生形式**（OpenQASM 3.0扩展）：

```qasm
#pragma noise depolarizing(0.01) on q[0]
h q[0];
```

### 9.3 Qiskit噪声模型转换

```python
from qiskit.providers.aer.noise import NoiseModel, depolarizing_error

# 创建噪声模型
noise_model = NoiseModel()

# 添加退极化噪声
dep_error = depolarizing_error(0.01, 1)
noise_model.add_all_qubit_quantum_error(dep_error, ['x', 'h'])

# 添加到电路
result = execute(circuit, simulator, noise_model=noise_model).result()
```

---

## 10. 算法模板系统

### 10.1 Bell态模板

**算法描述**：

```dsl
algorithm Bell_State {
  name: "Bell State Generation"
  input: Quantum_State[2]  // |00⟩
  output: Quantum_State[2]  // (|00⟩ + |11⟩)/√2
  
  steps: [
    Apply Hadamard to q[0],
    Apply CNOT(q[0], q[1]),
    Measure both qubits
  ]
}
```

**生成电路**：

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

### 10.2 GHZ态模板

**算法描述**：

```dsl
algorithm GHZ_State {
  name: "GHZ State Generation"
  input: Quantum_State[n]  // |0⟩^⊗n
  output: Quantum_State[n]  // (|0⟩^⊗n + |1⟩^⊗n)/√2
  
  steps: [
    Apply Hadamard to q[0],
    For i in 0..n-2:
      Apply CNOT(q[i], q[i+1]),
    Measure all qubits
  ]
}
```

### 10.3 Grover搜索模板

**算法描述**：

```dsl
algorithm Grover_Search {
  name: "Grover Search Algorithm"
  input: Quantum_State[n], target: Integer
  output: Quantum_State[n]
  
  steps: [
    Initialize |+⟩^⊗n,
    Repeat ⌈π/4·√N⌉ times:
      Apply Oracle(target),
      Apply Diffusion,
    Measure
  ]
  
  complexity: {
    time: O(√N)  // N = 2^n
    space: O(n)
  }
}
```

**Oracle实现**：

```qasm
// Oracle for target = |101⟩ (5)
x q[1];  // Flip q[1] (0 → 1)
h q[2];
ccx q[0], q[1], q[2];  // Mark target
h q[2];
x q[1];  // Restore
```

**Diffusion实现**：

```qasm
// Diffusion operator
h q[0]; h q[1]; h q[2];
x q[0]; x q[1]; x q[2];
h q[2];
ccx q[0], q[1], q[2];
h q[2];
x q[0]; x q[1]; x q[2];
h q[0]; h q[1]; h q[2];
```

### 10.4 Shor算法模板

**算法描述**：

```dsl
algorithm Shor {
  name: "Shor's Factoring Algorithm"
  input: Integer N, Integer a  // a random, gcd(a,N)=1
  output: Integer factor
  
  steps: [
    // 周期查找
    Prepare superposition on counting register,
    Apply modular exponentiation: |x⟩|0⟩ → |x⟩|a^x mod N⟩,
    Apply inverse QFT on counting register,
    Measure to obtain period r,
    
    // 因子计算
    If r is even and a^(r/2) ≢ -1 (mod N):
      factor = gcd(a^(r/2) ± 1, N)
  ]
  
  complexity: {
    time: O((log N)^3)
    space: O(log N)
  }
}
```

### 10.5 QAOA模板

**算法描述**：

```dsl
algorithm QAOA {
  name: "Quantum Approximate Optimization Algorithm"
  input: Optimization_Problem, Integer p
  output: Approximate_Solution
  
  parameters: {
    gamma: Array[p],  // Cost Hamiltonian parameters
    beta: Array[p]    // Mixer Hamiltonian parameters
  }
  
  steps: [
    Initialize |+⟩^⊗n,
    For i in 0..p-1:
      Apply e^(-i·γ[i]·H_C),  // Cost Hamiltonian
      Apply e^(-i·β[i]·H_M),  // Mixer Hamiltonian
    Measure and optimize parameters classically
  ]
}
```

**Max-Cut哈密顿量**：

```qasm
// Cost Hamiltonian for edge (i,j)
cx q[i], q[j];
rz(2*gamma) q[j];
cx q[i], q[j];
```

**Mixer哈密顿量**：

```qasm
// Mixer Hamiltonian
rx(2*beta) q[0];
rx(2*beta) q[1];
rx(2*beta) q[2];
```

### 10.6 VQE模板

**算法描述**：

```dsl
algorithm VQE {
  name: "Variational Quantum Eigensolver"
  input: Hamiltonian H, Ansatz U(θ)
  output: Ground_State_Energy
  
  steps: [
    Initialize |0⟩^⊗n,
    Prepare trial state: |ψ(θ)⟩ = U(θ)|0⟩,
    Measure ⟨ψ(θ)|H|ψ(θ)⟩,
    Classically optimize θ to minimize energy,
    Return minimum energy
  ]
}
```

**UCCSD Ansatz**（简化）：

```qasm
// Single excitation
ry(theta[0]) q[0];
rz(theta[1]) q[0];
cx q[0], q[1];

// Double excitation
cx q[0], q[2];
cx q[1], q[3];
ry(theta[2]) q[2];
```

---

## 11. 转换工具与API

### 11.1 Python API

```python
from quantum_computing.schema_qasm_integration import (
    QuantumCircuit, QASMParser, CircuitConverter,
    BellStateTemplate, GroverSearchTemplate, QAOATemplate,
    VQETemplate, ShorAlgorithmTemplate, NoiseModelGenerator
)

# 创建电路
circuit = QuantumCircuit(2, 2, "Bell_State")
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

# 转换为QASM
qasm2_code = circuit.to_qasm2()
qasm3_code = circuit.to_qasm3()

# 转换为Qiskit代码
qiskit_code = CircuitConverter.to_qiskit_code(circuit)

# 转换为Cirq代码
cirq_code = CircuitConverter.to_cirq_code(circuit)

# 转换为JSON
json_str = CircuitConverter.to_json(circuit)

# 从QASM解析
parser = QASMParser()
parsed_circuit = parser.parse(qasm2_code)

# 使用算法模板
template = GroverSearchTemplate()
grover_circuit = template.generate_circuit(num_qubits=3, target=5)

# 添加噪声
noise = NoiseModelGenerator.create_depolarizing_noise([0], 0.01)
circuit.add_noise(noise)
```

### 11.2 命令行工具

```bash
# QASM转换
python -m quantum_computing.schema_qasm_integration \
    --input circuit.json \
    --output circuit.qasm \
    --format qasm2

# Qiskit代码生成
python -m quantum_computing.schema_qasm_integration \
    --input circuit.json \
    --output circuit_qiskit.py \
    --format qiskit

# 从QASM导入
python -m quantum_computing.schema_qasm_integration \
    --input circuit.qasm \
    --output circuit.json \
    --parse
```

---

## 12. 转换验证

### 12.1 验证策略

**语义等价性验证**：

```python
def verify_semantic_equivalence(circuit1, circuit2):
    """验证两个电路的语义等价性"""
    # 1. 状态向量比较
    state1 = simulate(circuit1)
    state2 = simulate(circuit2)
    fidelity = state_fidelity(state1, state2)
    
    # 2. 测量统计比较
    counts1 = run(circuit1, shots=10000)
    counts2 = run(circuit2, shots=10000)
    distance = total_variation_distance(counts1, counts2)
    
    return fidelity > 0.99 and distance < 0.01
```

**功能验证**：

```python
def verify_functional_correctness(circuit, expected_outputs):
    """验证电路功能正确性"""
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(circuit, simulator, shots=10000).result()
    counts = result.get_counts()
    
    for output, probability in expected_outputs.items():
        measured_prob = counts.get(output, 0) / 10000
        if abs(measured_prob - probability) > 0.05:
            return False
    return True
```

### 12.2 验证示例

**验证Bell态电路**：

```python
# 验证贝尔态电路产生正确的纠缠态
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

# 执行验证
result = execute(circuit, simulator, shots=10000).result()
counts = result.get_counts()

# 期望结果：约50% '00' 和 50% '11'
assert abs(counts.get('00', 0) - 5000) < 500
assert abs(counts.get('11', 0) - 5000) < 500
assert counts.get('01', 0) < 100
assert counts.get('10', 0) < 100
```

---

**创建时间**：2025-01-21  
**最后更新**：2025-02-14  
**文档版本**：v2.0  
**维护者**：DSL Schema研究团队
