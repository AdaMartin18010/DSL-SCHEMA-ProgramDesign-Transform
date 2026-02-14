#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子计算Schema QASM集成模块

该模块提供量子计算Schema与QASM（Quantum Assembly Language）之间的
转换、解析和生成功能，支持OpenQASM 2.0和3.0标准。

功能：
- QASM解析和生成
- 量子电路转换
- 算法模板
- 噪声模型支持

作者: DSL Schema研究团队
版本: 1.0.0
日期: 2025-02-14
"""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
from numpy import ndarray


# ============================================================================
# 基础类型定义
# ============================================================================

class GateType(Enum):
    """量子门类型枚举"""
    # 单量子比特门
    PAULI_X = "x"
    PAULI_Y = "y"
    PAULI_Z = "z"
    HADAMARD = "h"
    PHASE = "s"
    T_GATE = "t"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    U1 = "u1"
    U2 = "u2"
    U3 = "u3"
    IDENTITY = "id"
    
    # 双量子比特门
    CNOT = "cx"
    CZ = "cz"
    SWAP = "swap"
    ISWAP = "iswap"
    SQRT_SWAP = "sqrt_swap"
    CONTROLLED_RX = "crx"
    CONTROLLED_RY = "cry"
    CONTROLLED_RZ = "crz"
    CONTROLLED_U = "cu"
    
    # 三量子比特门
    TOFFOLI = "ccx"
    FREDKIN = "cswap"
    
    # 测量门
    MEASURE = "measure"
    RESET = "reset"
    BARRIER = "barrier"


class NoiseType(Enum):
    """噪声类型枚举"""
    DEPOLARIZING = "depolarizing"
    AMPLITUDE_DAMPING = "amplitude_damping"
    PHASE_DAMPING = "phase_damping"
    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    BIT_PHASE_FLIP = "bit_phase_flip"
    THERMAL_RELAXATION = "thermal_relaxation"
    READOUT_ERROR = "readout_error"


@dataclass
class Qubit:
    """量子比特定义"""
    index: int
    name: str = ""
    register: str = "q"
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.register}[{self.index}]"
    
    def to_qasm(self) -> str:
        """转换为QASM表示"""
        return f"{self.register}[{self.index}]"


@dataclass
class ClassicalBit:
    """经典比特定义"""
    index: int
    name: str = ""
    register: str = "c"
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.register}[{self.index}]"
    
    def to_qasm(self) -> str:
        """转换为QASM表示"""
        return f"{self.register}[{self.index}]"


@dataclass
class GateParameter:
    """量子门参数"""
    name: str
    value: Union[float, str]
    unit: str = "rad"  # rad, deg
    
    def to_qasm(self) -> str:
        """转换为QASM参数表示"""
        if isinstance(self.value, str):
            return self.value
        if self.unit == "deg":
            return f"{np.radians(self.value):.10f}"
        return f"{self.value:.10f}"


@dataclass
class QuantumGate:
    """量子门定义"""
    gate_type: GateType
    qubits: List[Qubit]
    parameters: List[GateParameter] = field(default_factory=list)
    classical_bits: List[ClassicalBit] = field(default_factory=list)
    
    def to_qasm(self) -> str:
        """转换为QASM门指令"""
        gate_name = self.gate_type.value
        
        # 处理参数
        params_str = ""
        if self.parameters:
            params = [p.to_qasm() for p in self.parameters]
            params_str = f"({', '.join(params)})"
        
        # 处理测量门
        if self.gate_type == GateType.MEASURE:
            if self.classical_bits:
                return f"measure {self.qubits[0].to_qasm()} -> {self.classical_bits[0].to_qasm()};"
            return f"measure {self.qubits[0].to_qasm()};"
        
        # 处理重置和屏障
        if self.gate_type == GateType.RESET:
            return f"reset {self.qubits[0].to_qasm()};"
        if self.gate_type == GateType.BARRIER:
            qubits_str = ", ".join([q.to_qasm() for q in self.qubits])
            return f"barrier {qubits_str};"
        
        # 处理普通门
        qubits_str = ", ".join([q.to_qasm() for q in self.qubits])
        return f"{gate_name}{params_str} {qubits_str};"


@dataclass
class NoiseModel:
    """噪声模型定义"""
    noise_type: NoiseType
    target_qubits: List[int]
    probability: float
    parameters: Dict[str, float] = field(default_factory=dict)
    
    def to_qasm(self) -> str:
        """转换为QASM噪声指令（OpenQASM 3.0扩展）"""
        qubits_str = ", ".join([f"q[{i}]" for i in self.target_qubits])
        params = [f"{self.probability:.10f}"]
        for key, value in self.parameters.items():
            params.append(f"{key}={value:.10f}")
        params_str = ", ".join(params)
        return f"// noise {self.noise_type.value}({params_str}) {qubits_str};"


# ============================================================================
# 量子电路定义
# ============================================================================

class QuantumCircuit:
    """
    量子电路类
    
    表示一个完整的量子电路，包含量子比特、经典比特、量子门和测量操作。
    """
    
    def __init__(self, num_qubits: int, num_classical_bits: int = 0, name: str = "circuit"):
        """
        初始化量子电路
        
        Args:
            num_qubits: 量子比特数量
            num_classical_bits: 经典比特数量
            name: 电路名称
        """
        self.name = name
        self.num_qubits = num_qubits
        self.num_classical_bits = num_classical_bits
        
        # 创建量子比特
        self.qubits = [Qubit(i, register="q") for i in range(num_qubits)]
        
        # 创建经典比特
        self.classical_bits = [ClassicalBit(i, register="c") for i in range(num_classical_bits)]
        
        # 门操作列表
        self.gates: List[QuantumGate] = []
        
        # 噪声模型
        self.noise_models: List[NoiseModel] = []
        
        # 元数据
        self.metadata: Dict[str, Any] = {}
    
    def add_gate(self, gate: QuantumGate) -> None:
        """添加量子门"""
        self.gates.append(gate)
    
    def x(self, qubit_index: int) -> None:
        """应用Pauli-X门"""
        self.add_gate(QuantumGate(GateType.PAULI_X, [self.qubits[qubit_index]]))
    
    def y(self, qubit_index: int) -> None:
        """应用Pauli-Y门"""
        self.add_gate(QuantumGate(GateType.PAULI_Y, [self.qubits[qubit_index]]))
    
    def z(self, qubit_index: int) -> None:
        """应用Pauli-Z门"""
        self.add_gate(QuantumGate(GateType.PAULI_Z, [self.qubits[qubit_index]]))
    
    def h(self, qubit_index: int) -> None:
        """应用Hadamard门"""
        self.add_gate(QuantumGate(GateType.HADAMARD, [self.qubits[qubit_index]]))
    
    def s(self, qubit_index: int) -> None:
        """应用Phase门（S门）"""
        self.add_gate(QuantumGate(GateType.PHASE, [self.qubits[qubit_index]]))
    
    def t(self, qubit_index: int) -> None:
        """应用T门"""
        self.add_gate(QuantumGate(GateType.T_GATE, [self.qubits[qubit_index]]))
    
    def rx(self, qubit_index: int, theta: float) -> None:
        """应用绕X轴旋转门"""
        param = GateParameter("theta", theta)
        self.add_gate(QuantumGate(GateType.RX, [self.qubits[qubit_index]], [param]))
    
    def ry(self, qubit_index: int, theta: float) -> None:
        """应用绕Y轴旋转门"""
        param = GateParameter("theta", theta)
        self.add_gate(QuantumGate(GateType.RY, [self.qubits[qubit_index]], [param]))
    
    def rz(self, qubit_index: int, phi: float) -> None:
        """应用绕Z轴旋转门"""
        param = GateParameter("phi", phi)
        self.add_gate(QuantumGate(GateType.RZ, [self.qubits[qubit_index]], [param]))
    
    def cx(self, control: int, target: int) -> None:
        """应用CNOT门（受控非门）"""
        self.add_gate(QuantumGate(
            GateType.CNOT, 
            [self.qubits[control], self.qubits[target]]
        ))
    
    def cz(self, control: int, target: int) -> None:
        """应用CZ门（受控Z门）"""
        self.add_gate(QuantumGate(
            GateType.CZ,
            [self.qubits[control], self.qubits[target]]
        ))
    
    def swap(self, qubit1: int, qubit2: int) -> None:
        """应用SWAP门"""
        self.add_gate(QuantumGate(
            GateType.SWAP,
            [self.qubits[qubit1], self.qubits[qubit2]]
        ))
    
    def ccx(self, control1: int, control2: int, target: int) -> None:
        """应用Toffoli门（CCX门）"""
        self.add_gate(QuantumGate(
            GateType.TOFFOLI,
            [self.qubits[control1], self.qubits[control2], self.qubits[target]]
        ))
    
    def measure(self, qubit_index: int, classical_index: Optional[int] = None) -> None:
        """
        测量量子比特
        
        Args:
            qubit_index: 要测量的量子比特索引
            classical_index: 存储结果的经典比特索引，默认为相同索引
        """
        if classical_index is None:
            classical_index = qubit_index
        
        if classical_index >= self.num_classical_bits:
            raise ValueError(f"经典比特索引 {classical_index} 超出范围")
        
        self.add_gate(QuantumGate(
            GateType.MEASURE,
            [self.qubits[qubit_index]],
            classical_bits=[self.classical_bits[classical_index]]
        ))
    
    def measure_all(self) -> None:
        """测量所有量子比特"""
        for i in range(min(self.num_qubits, self.num_classical_bits)):
            self.measure(i, i)
    
    def barrier(self, qubit_indices: Optional[List[int]] = None) -> None:
        """添加屏障"""
        if qubit_indices is None:
            qubit_indices = list(range(self.num_qubits))
        qubits = [self.qubits[i] for i in qubit_indices]
        self.add_gate(QuantumGate(GateType.BARRIER, qubits))
    
    def reset(self, qubit_index: int) -> None:
        """重置量子比特"""
        self.add_gate(QuantumGate(GateType.RESET, [self.qubits[qubit_index]]))
    
    def add_noise(self, noise_model: NoiseModel) -> None:
        """添加噪声模型"""
        self.noise_models.append(noise_model)
    
    def to_qasm2(self) -> str:
        """
        转换为OpenQASM 2.0格式
        
        Returns:
            QASM 2.0格式的字符串
        """
        lines = [
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            "",
            f"// Circuit: {self.name}",
            f"// Qubits: {self.num_qubits}",
            f"// Classical bits: {self.num_classical_bits}",
            "",
            f"qreg q[{self.num_qubits}];",
        ]
        
        if self.num_classical_bits > 0:
            lines.append(f"creg c[{self.num_classical_bits}];")
        
        lines.append("")
        
        # 添加噪声模型注释
        if self.noise_models:
            lines.append("// Noise models")
            for noise in self.noise_models:
                lines.append(noise.to_qasm())
            lines.append("")
        
        # 添加门操作
        for gate in self.gates:
            lines.append(gate.to_qasm())
        
        return "\n".join(lines)
    
    def to_qasm3(self) -> str:
        """
        转换为OpenQASM 3.0格式
        
        Returns:
            QASM 3.0格式的字符串
        """
        lines = [
            "OPENQASM 3.0;",
            'include "stdgates.inc";',
            "",
            f"// Circuit: {self.name}",
            f"// Qubits: {self.num_qubits}",
            f"// Classical bits: {self.num_classical_bits}",
            "",
            f"qubit[{self.num_qubits}] q;",
        ]
        
        if self.num_classical_bits > 0:
            lines.append(f"bit[{self.num_classical_bits}] c;")
        
        lines.append("")
        
        # 添加噪声模型
        if self.noise_models:
            lines.append("// Noise models")
            for noise in self.noise_models:
                lines.append(noise.to_qasm())
            lines.append("")
        
        # 添加门操作
        for gate in self.gates:
            qasm_line = gate.to_qasm()
            # 转换测量指令格式为OpenQASM 3.0
            if gate.gate_type == GateType.MEASURE:
                if gate.classical_bits:
                    qubit_str = gate.qubits[0].to_qasm().replace("q[", "q[")
                    cbit_str = gate.classical_bits[0].to_qasm()
                    qasm_line = f"{cbit_str} = measure {qubit_str};"
            lines.append(qasm_line)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "num_qubits": self.num_qubits,
            "num_classical_bits": self.num_classical_bits,
            "gates": [
                {
                    "type": g.gate_type.value,
                    "qubits": [q.index for q in g.qubits],
                    "parameters": [{"name": p.name, "value": p.value} for p in g.parameters],
                    "classical_bits": [c.index for c in g.classical_bits] if g.classical_bits else []
                }
                for g in self.gates
            ],
            "noise_models": [
                {
                    "type": n.noise_type.value,
                    "qubits": n.target_qubits,
                    "probability": n.probability,
                    "parameters": n.parameters
                }
                for n in self.noise_models
            ],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuantumCircuit':
        """从字典创建量子电路"""
        circuit = cls(
            num_qubits=data["num_qubits"],
            num_classical_bits=data.get("num_classical_bits", 0),
            name=data.get("name", "circuit")
        )
        
        # 重建门操作
        for gate_data in data.get("gates", []):
            gate_type = GateType(gate_data["type"])
            qubits = [circuit.qubits[i] for i in gate_data["qubits"]]
            parameters = [
                GateParameter(p["name"], p["value"])
                for p in gate_data.get("parameters", [])
            ]
            classical_bits = [
                circuit.classical_bits[i]
                for i in gate_data.get("classical_bits", [])
            ]
            
            gate = QuantumGate(gate_type, qubits, parameters, classical_bits)
            circuit.add_gate(gate)
        
        # 重建噪声模型
        for noise_data in data.get("noise_models", []):
            noise = NoiseModel(
                noise_type=NoiseType(noise_data["type"]),
                target_qubits=noise_data["qubits"],
                probability=noise_data["probability"],
                parameters=noise_data.get("parameters", {})
            )
            circuit.add_noise(noise)
        
        circuit.metadata = data.get("metadata", {})
        return circuit


# ============================================================================
# QASM解析器
# ============================================================================

class QASMParser:
    """
    QASM解析器
    
    解析OpenQASM 2.0和3.0格式的量子电路代码。
    """
    
    def __init__(self):
        self.version: str = "2.0"
        self.includes: List[str] = []
        self.num_qubits: int = 0
        self.num_classical_bits: int = 0
    
    def parse(self, qasm_string: str) -> QuantumCircuit:
        """
        解析QASM字符串
        
        Args:
            qasm_string: QASM格式的字符串
            
        Returns:
            解析后的QuantumCircuit对象
        """
        lines = qasm_string.strip().split('\n')
        
        # 解析版本
        version_match = re.search(r'OPENQASM\s+(\d+\.\d+)', qasm_string)
        if version_match:
            self.version = version_match.group(1)
        
        # 解析include
        self.includes = re.findall(r'include\s+"([^"]+)"', qasm_string)
        
        # 解析寄存器定义
        qreg_match = re.search(r'qreg\s+q\[(\d+)\]', qasm_string)
        creg_match = re.search(r'creg\s+c\[(\d+)\]', qasm_string)
        
        qubit_array_match = re.search(r'qubit\[(\d+)\]\s+q', qasm_string)
        bit_array_match = re.search(r'bit\[(\d+)\]\s+c', qasm_string)
        
        if qreg_match:
            self.num_qubits = int(qreg_match.group(1))
        elif qubit_array_match:
            self.num_qubits = int(qubit_array_match.group(1))
        
        if creg_match:
            self.num_classical_bits = int(creg_match.group(1))
        elif bit_array_match:
            self.num_classical_bits = int(bit_array_match.group(1))
        
        # 创建电路
        circuit = QuantumCircuit(self.num_qubits, self.num_classical_bits)
        
        # 解析门操作
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('OPENQASM'):
                continue
            if line.startswith('include') or line.startswith('qreg') or line.startswith('creg'):
                continue
            if line.startswith('qubit') or line.startswith('bit'):
                continue
            
            self._parse_gate_line(line, circuit)
        
        return circuit
    
    def _parse_gate_line(self, line: str, circuit: QuantumCircuit) -> None:
        """解析单条门指令"""
        # 移除分号
        line = line.rstrip(';')
        
        # 解析测量指令 (OpenQASM 2.0)
        measure_match = re.match(r'measure\s+q\[(\d+)\]\s*->\s*c\[(\d+)\]', line)
        if measure_match:
            qubit_idx = int(measure_match.group(1))
            cbit_idx = int(measure_match.group(2))
            circuit.measure(qubit_idx, cbit_idx)
            return
        
        # 解析测量指令 (OpenQASM 3.0)
        measure3_match = re.match(r'c\[(\d+)\]\s*=\s*measure\s+q\[(\d+)\]', line)
        if measure3_match:
            cbit_idx = int(measure3_match.group(1))
            qubit_idx = int(measure3_match.group(2))
            circuit.measure(qubit_idx, cbit_idx)
            return
        
        # 解析reset
        reset_match = re.match(r'reset\s+q\[(\d+)\]', line)
        if reset_match:
            circuit.reset(int(reset_match.group(1)))
            return
        
        # 解析barrier
        barrier_match = re.match(r'barrier\s+(.+)', line)
        if barrier_match:
            qubits_str = barrier_match.group(1)
            qubit_indices = re.findall(r'q\[(\d+)\]', qubits_str)
            circuit.barrier([int(i) for i in qubit_indices])
            return
        
        # 解析带参数的门
        param_gate_match = re.match(r'(\w+)\(([^)]+)\)\s+q\[(\d+)\](?:\s*,\s*q\[(\d+)\])?', line)
        if param_gate_match:
            gate_name = param_gate_match.group(1)
            params_str = param_gate_match.group(2)
            qubit1 = int(param_gate_match.group(3))
            qubit2 = param_gate_match.group(4)
            
            params = [float(p.strip()) for p in params_str.split(',')]
            
            self._apply_param_gate(circuit, gate_name, qubit1, qubit2, params)
            return
        
        # 解析不带参数的门
        simple_gate_match = re.match(r'(\w+)\s+q\[(\d+)\](?:\s*,\s*q\[(\d+)\])?(?:\s*,\s*q\[(\d+)\])?', line)
        if simple_gate_match:
            gate_name = simple_gate_match.group(1)
            qubits = [int(simple_gate_match.group(i)) for i in range(2, 5) if simple_gate_match.group(i)]
            
            self._apply_simple_gate(circuit, gate_name, qubits)
    
    def _apply_simple_gate(self, circuit: QuantumCircuit, gate_name: str, qubits: List[int]) -> None:
        """应用简单门"""
        gate_map = {
            'x': GateType.PAULI_X,
            'y': GateType.PAULI_Y,
            'z': GateType.PAULI_Z,
            'h': GateType.HADAMARD,
            's': GateType.PHASE,
            't': GateType.T_GATE,
            'id': GateType.IDENTITY,
            'cx': GateType.CNOT,
            'cz': GateType.CZ,
            'swap': GateType.SWAP,
            'iswap': GateType.ISWAP,
            'ccx': GateType.TOFFOLI,
            'cswap': GateType.FREDKIN,
        }
        
        if gate_name in gate_map:
            gate_type = gate_map[gate_name]
            qubit_objs = [circuit.qubits[i] for i in qubits]
            circuit.add_gate(QuantumGate(gate_type, qubit_objs))
    
    def _apply_param_gate(self, circuit: QuantumCircuit, gate_name: str, 
                          qubit1: int, qubit2: Optional[str], params: List[float]) -> None:
        """应用带参数的门"""
        param = GateParameter("theta", params[0]) if params else None
        
        if gate_name == 'rx' and param:
            circuit.rx(qubit1, params[0])
        elif gate_name == 'ry' and param:
            circuit.ry(qubit1, params[0])
        elif gate_name == 'rz' and param:
            circuit.rz(qubit1, params[0])


# ============================================================================
# 算法模板
# ============================================================================

class AlgorithmTemplate(ABC):
    """量子算法模板基类"""
    
    @abstractmethod
    def generate_circuit(self, **kwargs) -> QuantumCircuit:
        """生成量子电路"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取算法名称"""
        pass


class BellStateTemplate(AlgorithmTemplate):
    """贝尔态生成算法模板"""
    
    def get_name(self) -> str:
        return "Bell State"
    
    def generate_circuit(self, **kwargs) -> QuantumCircuit:
        """生成贝尔态电路"""
        circuit = QuantumCircuit(2, 2, "Bell_State")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
        return circuit


class GHZStateTemplate(AlgorithmTemplate):
    """GHZ态生成算法模板"""
    
    def get_name(self) -> str:
        return "GHZ State"
    
    def generate_circuit(self, num_qubits: int = 3, **kwargs) -> QuantumCircuit:
        """生成GHZ态电路"""
        circuit = QuantumCircuit(num_qubits, num_qubits, "GHZ_State")
        circuit.h(0)
        for i in range(num_qubits - 1):
            circuit.cx(i, i + 1)
        circuit.measure_all()
        return circuit


class GroverSearchTemplate(AlgorithmTemplate):
    """Grover搜索算法模板"""
    
    def get_name(self) -> str:
        return "Grover Search"
    
    def generate_circuit(self, num_qubits: int = 3, target: int = 0, **kwargs) -> QuantumCircuit:
        """
        生成Grover搜索电路
        
        Args:
            num_qubits: 量子比特数量
            target: 目标状态索引
        """
        circuit = QuantumCircuit(num_qubits, num_qubits, "Grover_Search")
        n = num_qubits
        
        # 初始化：应用Hadamard门到所有量子比特
        for i in range(n):
            circuit.h(i)
        
        # Grover迭代次数
        iterations = int(np.pi / 4 * np.sqrt(2**n))
        
        for _ in range(iterations):
            # Oracle：标记目标状态
            self._apply_oracle(circuit, n, target)
            
            # Diffusion操作
            self._apply_diffusion(circuit, n)
        
        circuit.measure_all()
        return circuit
    
    def _apply_oracle(self, circuit: QuantumCircuit, n: int, target: int) -> None:
        """应用Oracle操作"""
        # 将目标索引转换为二进制
        target_binary = format(target, f'0{n}b')
        
        # 对目标状态为0的位应用X门
        for i, bit in enumerate(reversed(target_binary)):
            if bit == '0':
                circuit.x(i)
        
        # 应用多控制Z门（用CCX和H门模拟）
        if n == 2:
            circuit.h(1)
            circuit.cx(0, 1)
            circuit.h(1)
        elif n == 3:
            circuit.h(2)
            circuit.ccx(0, 1, 2)
            circuit.h(2)
        
        # 还原X门
        for i, bit in enumerate(reversed(target_binary)):
            if bit == '0':
                circuit.x(i)
    
    def _apply_diffusion(self, circuit: QuantumCircuit, n: int) -> None:
        """应用扩散操作"""
        # 应用Hadamard门到所有量子比特
        for i in range(n):
            circuit.h(i)
        
        # 应用X门到所有量子比特
        for i in range(n):
            circuit.x(i)
        
        # 应用多控制Z门
        if n == 2:
            circuit.h(1)
            circuit.cx(0, 1)
            circuit.h(1)
        elif n == 3:
            circuit.h(2)
            circuit.ccx(0, 1, 2)
            circuit.h(2)
        
        # 还原X门
        for i in range(n):
            circuit.x(i)
        
        # 还原Hadamard门
        for i in range(n):
            circuit.h(i)


class ShorAlgorithmTemplate(AlgorithmTemplate):
    """Shor算法模板 - 量子因数分解"""
    
    def get_name(self) -> str:
        return "Shor's Algorithm"
    
    def generate_circuit(self, N: int = 15, a: int = 7, **kwargs) -> QuantumCircuit:
        """
        生成Shor算法电路（简化版）
        
        Args:
            N: 要分解的合数
            a: 随机选择的底数（与N互质）
        """
        # 简化的Shor算法电路
        n_count = 8  # 计数寄存器量子比特数
        n_aux = 4    # 辅助寄存器量子比特数
        
        circuit = QuantumCircuit(n_count + n_aux, n_count, f"Shor_N{N}_a{a}")
        
        # 初始化计数寄存器为均匀叠加态
        for i in range(n_count):
            circuit.h(i)
        
        # 模幂运算（简化实现）
        self._modular_exponentiation(circuit, n_count, n_aux, N, a)
        
        # 应用量子傅里叶变换的逆变换
        self._inverse_qft(circuit, n_count)
        
        circuit.measure_all()
        return circuit
    
    def _modular_exponentiation(self, circuit: QuantumCircuit, n_count: int, 
                                 n_aux: int, N: int, a: int) -> None:
        """模幂运算（简化实现）"""
        # 简化的模幂运算实现
        for i in range(n_count):
            # 受控模乘运算
            circuit.cx(i, n_count)  # 简化的控制操作
    
    def _inverse_qft(self, circuit: QuantumCircuit, n: int) -> None:
        """逆量子傅里叶变换"""
        for i in range(n // 2):
            circuit.swap(i, n - i - 1)
        
        for i in range(n):
            circuit.h(i)
            for j in range(i + 1, n):
                # 受控相位门（简化）
                pass


class QAOATemplate(AlgorithmTemplate):
    """QAOA算法模板 - 量子近似优化算法"""
    
    def get_name(self) -> str:
        return "QAOA"
    
    def generate_circuit(self, num_qubits: int = 4, p: int = 2, 
                         gamma: Optional[List[float]] = None,
                         beta: Optional[List[float]] = None, **kwargs) -> QuantumCircuit:
        """
        生成QAOA电路
        
        Args:
            num_qubits: 量子比特数量
            p: QAOA层数
            gamma: 代价哈密顿量参数
            beta: 混合哈密顿量参数
        """
        circuit = QuantumCircuit(num_qubits, num_qubits, f"QAOA_p{p}")
        
        if gamma is None:
            gamma = [0.5] * p
        if beta is None:
            beta = [0.5] * p
        
        # 初始化均匀叠加态
        for i in range(num_qubits):
            circuit.h(i)
        
        # QAOA层
        for i in range(p):
            # 代价哈密顿量演化
            self._apply_cost_hamiltonian(circuit, num_qubits, gamma[i])
            
            # 混合哈密顿量演化
            self._apply_mixer_hamiltonian(circuit, num_qubits, beta[i])
        
        circuit.measure_all()
        return circuit
    
    def _apply_cost_hamiltonian(self, circuit: QuantumCircuit, n: int, gamma: float) -> None:
        """应用代价哈密顿量（Max-Cut问题）"""
        # 简化的Max-Cut代价哈密顿量
        for i in range(n - 1):
            circuit.cx(i, i + 1)
            circuit.rz(i + 1, 2 * gamma)
            circuit.cx(i, i + 1)
    
    def _apply_mixer_hamiltonian(self, circuit: QuantumCircuit, n: int, beta: float) -> None:
        """应用混合哈密顿量"""
        for i in range(n):
            circuit.rx(i, 2 * beta)


class VQETemplate(AlgorithmTemplate):
    """VQE算法模板 - 变分量子本征求解器"""
    
    def get_name(self) -> str:
        return "VQE"
    
    def generate_circuit(self, num_qubits: int = 4, layers: int = 2, 
                         params: Optional[List[float]] = None, **kwargs) -> QuantumCircuit:
        """
        生成VQE电路
        
        Args:
            num_qubits: 量子比特数量
            layers: 变分层数
            params: 变分参数
        """
        circuit = QuantumCircuit(num_qubits, num_qubits, f"VQE_layers{layers}")
        
        if params is None:
            params = [0.1 * i for i in range(num_qubits * layers * 2)]
        
        param_idx = 0
        
        for layer in range(layers):
            # 旋转层
            for i in range(num_qubits):
                circuit.ry(i, params[param_idx])
                circuit.rz(i, params[param_idx + 1])
                param_idx += 2
            
            # 纠缠层
            for i in range(0, num_qubits - 1, 2):
                circuit.cx(i, i + 1)
            
            if num_qubits > 2:
                for i in range(1, num_qubits - 1, 2):
                    circuit.cx(i, i + 1)
        
        circuit.measure_all()
        return circuit


# ============================================================================
# 噪声模型生成器
# ============================================================================

class NoiseModelGenerator:
    """噪声模型生成器"""
    
    @staticmethod
    def create_depolarizing_noise(qubits: List[int], probability: float) -> NoiseModel:
        """创建退极化噪声"""
        return NoiseModel(NoiseType.DEPOLARIZING, qubits, probability)
    
    @staticmethod
    def create_amplitude_damping_noise(qubits: List[int], gamma: float) -> NoiseModel:
        """创建幅度阻尼噪声"""
        return NoiseModel(
            NoiseType.AMPLITUDE_DAMPING,
            qubits,
            gamma,
            {"gamma": gamma}
        )
    
    @staticmethod
    def create_phase_damping_noise(qubits: List[int], lambda_param: float) -> NoiseModel:
        """创建相位阻尼噪声"""
        return NoiseModel(
            NoiseType.PHASE_DAMPING,
            qubits,
            lambda_param,
            {"lambda": lambda_param}
        )
    
    @staticmethod
    def create_bit_flip_noise(qubits: List[int], probability: float) -> NoiseModel:
        """创建比特翻转噪声"""
        return NoiseModel(NoiseType.BIT_FLIP, qubits, probability)
    
    @staticmethod
    def create_phase_flip_noise(qubits: List[int], probability: float) -> NoiseModel:
        """创建相位翻转噪声"""
        return NoiseModel(NoiseType.PHASE_FLIP, qubits, probability)
    
    @staticmethod
    def create_readout_error(qubits: List[int], p0given1: float, p1given0: float) -> NoiseModel:
        """创建读出误差模型"""
        return NoiseModel(
            NoiseType.READOUT_ERROR,
            qubits,
            max(p0given1, p1given0),
            {"p0given1": p0given1, "p1given0": p1given0}
        )


# ============================================================================
# 电路转换器
# ============================================================================

class CircuitConverter:
    """量子电路转换器"""
    
    @staticmethod
    def to_qiskit_code(circuit: QuantumCircuit) -> str:
        """
        转换为Qiskit Python代码
        
        Args:
            circuit: 量子电路
            
        Returns:
            Qiskit格式的Python代码字符串
        """
        lines = [
            "from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister",
            "from qiskit import execute, Aer",
            "",
            f"# Create circuit: {circuit.name}",
            f"qc = QuantumCircuit({circuit.num_qubits}, {circuit.num_classical_bits})",
            ""
        ]
        
        for gate in circuit.gates:
            gate_name = gate.gate_type.value
            qubits = [q.index for q in gate.qubits]
            
            if gate.gate_type == GateType.MEASURE:
                if gate.classical_bits:
                    lines.append(f"qc.measure([{qubits[0]}], [{gate.classical_bits[0].index}])")
                else:
                    lines.append(f"qc.measure({qubits[0]}, {qubits[0]})")
            elif gate.gate_type == GateType.RESET:
                lines.append(f"qc.reset({qubits[0]})")
            elif gate.gate_type == GateType.BARRIER:
                lines.append(f"qc.barrier({qubits})")
            elif gate.parameters:
                params = [f"{p.value:.10f}" for p in gate.parameters]
                lines.append(f"qc.{gate_name}({', '.join(params)}, {qubits[0]})")
            else:
                lines.append(f"qc.{gate_name}({', '.join(map(str, qubits))})")
        
        lines.extend([
            "",
            "# Execute",
            "simulator = Aer.get_backend('qasm_simulator')",
            "result = execute(qc, simulator).result()",
            "counts = result.get_counts(qc)",
            "print(counts)"
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def to_cirq_code(circuit: QuantumCircuit) -> str:
        """
        转换为Cirq Python代码
        
        Args:
            circuit: 量子电路
            
        Returns:
            Cirq格式的Python代码字符串
        """
        lines = [
            "import cirq",
            "",
            f"# Create circuit: {circuit.name}",
            f"qubits = [cirq.GridQubit(0, i) for i in range({circuit.num_qubits})]",
            "circuit = cirq.Circuit()",
            ""
        ]
        
        gate_map = {
            'x': 'cirq.X',
            'y': 'cirq.Y',
            'z': 'cirq.Z',
            'h': 'cirq.H',
            's': 'cirq.S',
            't': 'cirq.T',
            'rx': 'cirq.rx',
            'ry': 'cirq.ry',
            'rz': 'cirq.rz',
            'cx': 'cirq.CNOT',
            'cz': 'cirq.CZ',
            'swap': 'cirq.SWAP',
            'ccx': 'cirq.CCX',
        }
        
        for gate in circuit.gates:
            gate_type = gate.gate_type.value
            qubits = [f"qubits[{q.index}]" for q in gate.qubits]
            
            if gate.gate_type == GateType.MEASURE:
                lines.append(f"circuit.append(cirq.measure({qubits[0]}, key='q{gate.qubits[0].index}'))")
            elif gate_type in gate_map:
                if gate.parameters:
                    params = [f"{p.value:.10f}" for p in gate.parameters]
                    lines.append(f"circuit.append({gate_map[gate_type]}({params[0]})({qubits[0]}))")
                else:
                    lines.append(f"circuit.append({gate_map[gate_type]}({', '.join(qubits)}))")
        
        lines.extend([
            "",
            "# Execute",
            "simulator = cirq.Simulator()",
            "result = simulator.run(circuit)",
            "print(result)"
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def to_json(circuit: QuantumCircuit) -> str:
        """转换为JSON格式"""
        return json.dumps(circuit.to_dict(), indent=2)
    
    @staticmethod
    def from_json(json_str: str) -> QuantumCircuit:
        """从JSON格式创建电路"""
        data = json.loads(json_str)
        return QuantumCircuit.from_dict(data)


# ============================================================================
# 主函数和示例
# ============================================================================

def example_bell_state():
    """贝尔态示例"""
    print("=" * 60)
    print("贝尔态示例")
    print("=" * 60)
    
    template = BellStateTemplate()
    circuit = template.generate_circuit()
    
    print("\nOpenQASM 2.0:")
    print(circuit.to_qasm2())
    
    print("\nOpenQASM 3.0:")
    print(circuit.to_qasm3())
    
    print("\nQiskit代码:")
    print(CircuitConverter.to_qiskit_code(circuit))


def example_grover_search():
    """Grover搜索算法示例"""
    print("\n" + "=" * 60)
    print("Grover搜索算法示例 (3 qubits, target=5)")
    print("=" * 60)
    
    template = GroverSearchTemplate()
    circuit = template.generate_circuit(num_qubits=3, target=5)
    
    print("\nOpenQASM 2.0:")
    print(circuit.to_qasm2())
    
    print("\nJSON表示:")
    print(CircuitConverter.to_json(circuit))


def example_qaoa():
    """QAOA算法示例"""
    print("\n" + "=" * 60)
    print("QAOA算法示例")
    print("=" * 60)
    
    template = QAOATemplate()
    circuit = template.generate_circuit(num_qubits=4, p=1, gamma=[0.5], beta=[0.3])
    
    print("\nOpenQASM 2.0:")
    print(circuit.to_qasm2())


def example_vqe():
    """VQE算法示例"""
    print("\n" + "=" * 60)
    print("VQE算法示例")
    print("=" * 60)
    
    template = VQETemplate()
    circuit = template.generate_circuit(num_qubits=4, layers=2)
    
    print("\nOpenQASM 2.0:")
    print(circuit.to_qasm2())


def example_shor():
    """Shor算法示例"""
    print("\n" + "=" * 60)
    print("Shor算法示例 (N=15, a=7)")
    print("=" * 60)
    
    template = ShorAlgorithmTemplate()
    circuit = template.generate_circuit(N=15, a=7)
    
    print("\nOpenQASM 2.0:")
    print(circuit.to_qasm2())


def example_noise_model():
    """噪声模型示例"""
    print("\n" + "=" * 60)
    print("噪声模型示例")
    print("=" * 60)
    
    circuit = QuantumCircuit(2, 2, "Noisy_Bell_State")
    circuit.h(0)
    circuit.cx(0, 1)
    
    # 添加噪声
    noise1 = NoiseModelGenerator.create_depolarizing_noise([0], 0.01)
    noise2 = NoiseModelGenerator.create_bit_flip_noise([1], 0.02)
    circuit.add_noise(noise1)
    circuit.add_noise(noise2)
    
    circuit.measure_all()
    
    print("\n带噪声的OpenQASM 2.0:")
    print(circuit.to_qasm2())


def example_qasm_parsing():
    """QASM解析示例"""
    print("\n" + "=" * 60)
    print("QASM解析示例")
    print("=" * 60)
    
    qasm_code = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0], q[1];
cx q[1], q[2];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
"""
    
    print("\n输入QASM代码:")
    print(qasm_code)
    
    parser = QASMParser()
    circuit = parser.parse(qasm_code)
    
    print(f"\n解析结果:")
    print(f"  量子比特数: {circuit.num_qubits}")
    print(f"  经典比特数: {circuit.num_classical_bits}")
    print(f"  门操作数: {len(circuit.gates)}")
    
    print("\n重新生成QASM:")
    print(circuit.to_qasm2())


if __name__ == "__main__":
    # 运行所有示例
    example_bell_state()
    example_grover_search()
    example_qaoa()
    example_vqe()
    example_shor()
    example_noise_model()
    example_qasm_parsing()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)
