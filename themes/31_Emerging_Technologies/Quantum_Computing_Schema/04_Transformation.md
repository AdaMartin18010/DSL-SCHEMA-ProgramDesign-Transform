# 量子计算Schema转换体系

## 📑 目录

- [量子计算Schema转换体系](#量子计算schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 转换方向](#2-转换方向)
  - [3. QASM转换](#3-qasm转换)
  - [4. Qiskit转换](#4-qiskit转换)
  - [5. PostgreSQL存储](#5-postgresql存储)
  - [6. 转换工具](#6-转换工具)
  - [7. 转换验证](#7-转换验证)

---

## 1. 转换体系概述

量子计算Schema转换体系支持**量子计算Schema到各种格式的转换**，包括QASM、Qiskit、Cirq、Q#等格式，以及PostgreSQL数据库存储。

**转换目标**：

- QASM/OpenQASM格式
- Qiskit Python代码
- Cirq Python代码
- Q#代码
- PostgreSQL数据库
- JSON格式

---

## 2. 转换方向

### 2.1 转换矩阵

| 转换方向 | 源格式 | 目标格式 | 转换复杂度 | 工具支持 | 数据完整性 | 推荐工具 |
|---------|--------|----------|------------|----------|------------|----------|
| **Quantum_Computing → QASM** | Quantum_Computing_Schema | QASM 2.0 | ⭐⭐⭐ | ✅ 良好 | 高 | 自定义转换器 |
| **Quantum_Computing → OpenQASM** | Quantum_Computing_Schema | OpenQASM 3.0 | ⭐⭐⭐ | ✅ 良好 | 高 | 自定义转换器 |
| **Quantum_Computing → Qiskit** | Quantum_Computing_Schema | Qiskit Python | ⭐⭐⭐ | ✅ 良好 | 高 | Qiskit工具 |
| **Quantum_Computing → Cirq** | Quantum_Computing_Schema | Cirq Python | ⭐⭐⭐ | ✅ 良好 | 高 | Cirq工具 |
| **Quantum_Computing → Q#** | Quantum_Computing_Schema | Q#代码 | ⭐⭐⭐⭐ | ⚠️ 有限 | 中 | 手动转换 |
| **Quantum_Computing → PostgreSQL** | Quantum_Computing_Schema | SQL DDL | ⭐⭐⭐ | ✅ 良好 | 高 | PostgreSQL转换器 |
| **Quantum_Computing → JSON** | Quantum_Computing_Schema | JSON Schema | ⭐⭐ | ✅ 良好 | 高 | JSON转换器 |

---

## 3. QASM转换

### 3.1 Quantum_Computing → QASM转换

**转换函数**：

```text
to_qasm: Quantum_Computing_Schema → QASM_String
```

**转换规则**：

```text
to_qasm(schema) =
  "OPENQASM 2.0;\n" +
  "include \"qelib1.inc\";\n" +
  to_qasm_qubits(schema.qubits) +
  to_qasm_gates(schema.gates) +
  to_qasm_measurements(schema.measurements)
```

**转换示例**：

**输入（Quantum_Computing_Schema）**：

```dsl
circuit Bell_State {
  qubits: [q0, q1]
  gates: [
    Hadamard(q0),
    CNOT(q0, q1)
  ]
  measurements: [Measure(q0), Measure(q1)]
}
```

**输出（QASM 2.0）**：

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

### 3.2 Quantum_Computing → OpenQASM 3.0转换

**转换函数**：

```text
to_openqasm3: Quantum_Computing_Schema → OpenQASM3_String
```

**转换规则**：

```text
to_openqasm3(schema) =
  "OPENQASM 3.0;\n" +
  "include \"stdgates.inc\";\n" +
  to_openqasm3_qubits(schema.qubits) +
  to_openqasm3_gates(schema.gates) +
  to_openqasm3_measurements(schema.measurements)
```

**转换示例**：

**输出（OpenQASM 3.0）**：

```qasm
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];
```

---

## 4. Qiskit转换

### 4.1 Quantum_Computing → Qiskit转换

**转换函数**：

```text
to_qiskit: Quantum_Computing_Schema → Qiskit_Python_Code
```

**转换规则**：

```text
to_qiskit(schema) =
  "from qiskit import QuantumCircuit\n" +
  "qc = QuantumCircuit(" + len(schema.qubits) + ")\n" +
  to_qiskit_gates(schema.gates) +
  to_qiskit_measurements(schema.measurements)
```

**转换示例**：

**输出（Qiskit Python）**：

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()
```

### 4.2 Qiskit → Quantum_Computing转换

**转换函数**：

```text
from_qiskit: Qiskit_QuantumCircuit → Quantum_Computing_Schema
```

**转换规则**：

```text
from_qiskit(qc) =
  extract_qubits(qc) +
  extract_gates(qc) +
  extract_measurements(qc)
```

---

## 5. PostgreSQL存储

### 5.1 数据库Schema设计

**量子电路表**：

```sql
CREATE TABLE quantum_circuits (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    qubit_count INTEGER NOT NULL,
    gate_count INTEGER NOT NULL,
    circuit_json JSONB,
    qasm_text TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quantum_circuits_name ON quantum_circuits(name);
CREATE INDEX idx_quantum_circuits_qubit_count ON quantum_circuits(qubit_count);
```

**量子门表**：

```sql
CREATE TABLE quantum_gates (
    id VARCHAR(50) PRIMARY KEY,
    circuit_id VARCHAR(50) REFERENCES quantum_circuits(id),
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
    algorithm_type VARCHAR(50),
    input_qubits INTEGER NOT NULL,
    output_qubits INTEGER NOT NULL,
    complexity_time VARCHAR(50),
    complexity_space VARCHAR(50),
    algorithm_json JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quantum_algorithms_name ON quantum_algorithms(name);
CREATE INDEX idx_quantum_algorithms_type ON quantum_algorithms(algorithm_type);
```

### 5.2 数据存储示例

**存储量子电路**：

```sql
INSERT INTO quantum_circuits (id, name, qubit_count, gate_count, circuit_json, qasm_text)
VALUES (
    'bell_state_001',
    'Bell State Circuit',
    2,
    2,
    '{"qubits": [0, 1], "gates": [{"type": "Hadamard", "qubits": [0]}, {"type": "CNOT", "qubits": [0, 1]}]}',
    'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\nh q[0];\ncx q[0], q[1];'
);
```

---

## 6. 转换工具

### 6.1 开源工具

**Qiskit工具**：

- `qiskit.circuit.QuantumCircuit`：量子电路构建
- `qiskit.qasm2`：QASM解析和转换
- `qiskit.qasm3`：OpenQASM 3.0支持

**Cirq工具**：

- `cirq.Circuit`：量子电路构建
- `cirq.qasm`：QASM支持

### 6.2 自定义转换器

**转换器实现**：

```python
class QuantumComputingTransformer:
    def to_qasm(self, schema: QuantumComputingSchema) -> str:
        """转换为QASM格式"""
        qasm = "OPENQASM 2.0;\n"
        qasm += "include \"qelib1.inc\";\n"
        qasm += f"qreg q[{len(schema.qubits)}];\n"

        for gate in schema.gates:
            qasm += self.gate_to_qasm(gate)

        return qasm

    def to_qiskit(self, schema: QuantumComputingSchema) -> str:
        """转换为Qiskit代码"""
        code = "from qiskit import QuantumCircuit\n\n"
        code += f"qc = QuantumCircuit({len(schema.qubits)})\n"

        for gate in schema.gates:
            code += self.gate_to_qiskit(gate)

        return code
```

---

## 7. 转换验证

### 7.1 转换正确性验证

**验证方法**：

1. **语义等价性验证**：
   - 验证转换前后的语义等价性
   - 使用量子模拟器验证

2. **功能等价性验证**：
   - 验证转换前后的功能等价性
   - 比较输出结果

3. **性能验证**：
   - 验证转换后的性能
   - 比较执行时间

### 7.2 验证工具

**Qiskit验证**：

```python
from qiskit import QuantumCircuit, execute, Aer

def verify_conversion(original_schema, converted_circuit):
    """验证转换正确性"""
    # 构建原始电路
    original_circuit = build_circuit(original_schema)

    # 执行两个电路
    simulator = Aer.get_backend('statevector_simulator')
    result1 = execute(original_circuit, simulator).result()
    result2 = execute(converted_circuit, simulator).result()

    # 比较结果
    return result1.get_statevector() == result2.get_statevector()
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
