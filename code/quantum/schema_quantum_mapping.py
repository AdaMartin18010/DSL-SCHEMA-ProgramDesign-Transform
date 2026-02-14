"""
量子信息论扩展 - Schema转换的量子视角
Quantum Information Theory Extension for Schema Transformation

本模块提供量子信息熵计算、量子信道模拟以及Schema到量子态的映射功能。

作者: DSL-SCHEMA-ProgramDesign-Transform Project
版本: 1.0
日期: 2026-02-14
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict


# ============================================================================
# 基础量子工具函数
# ============================================================================

def normalize_state(state: np.ndarray) -> np.ndarray:
    """归一化量子态"""
    return state / np.linalg.norm(state)


def is_valid_density_matrix(rho: np.ndarray, tol: float = 1e-10) -> bool:
    """
    验证密度矩阵的有效性
    
    检查：
    1. 厄米性（Hermiticity）
    2. 半正定性（Positive semi-definite）
    3. 迹为1（Unit trace）
    """
    # 厄米性检查
    if not np.allclose(rho, rho.conj().T, atol=tol):
        return False
    # 半正定性检查
    eigenvalues = np.linalg.eigvalsh(rho)
    if np.any(eigenvalues < -tol):
        return False
    # 迹为1检查
    if not np.isclose(np.trace(rho), 1.0, atol=tol):
        return False
    return True


def partial_trace(rho: np.ndarray, dims: List[int], trace_over: int) -> np.ndarray:
    """
    计算部分迹（Partial Trace）
    
    对于复合系统 AB，计算 Tr_B(ρ_AB) 或 Tr_A(ρ_AB)
    
    Args:
        rho: 复合系统的密度矩阵
        dims: 子系统维度列表 [dim_A, dim_B, ...]
        trace_over: 要迹掉的子系统索引 (0-based)
    
    Returns:
        约化密度矩阵
    """
    n_subsystems = len(dims)
    total_dim = np.prod(dims)
    
    # 重塑为张量形式
    shape = list(dims) * 2  # 每个维度出现两次（bra和ket）
    rho_tensor = rho.reshape(shape)
    
    # 计算迹的轴
    axes = (trace_over, trace_over + n_subsystems)
    
    # 执行迹操作
    reduced = np.trace(rho_tensor, axis1=axes[0], axis2=axes[1])
    
    # 重塑回矩阵形式
    remaining_dims = [dims[i] for i in range(n_subsystems) if i != trace_over]
    if len(remaining_dims) == 0:
        return reduced.reshape(1, 1)
    new_dim = np.prod(remaining_dims)
    return reduced.reshape(new_dim, new_dim)


def tensor_product(*matrices: np.ndarray) -> np.ndarray:
    """计算多个矩阵的张量积（Kronecker积）"""
    result = matrices[0]
    for mat in matrices[1:]:
        result = np.kron(result, mat)
    return result


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """计算对易子 [A, B] = AB - BA"""
    return A @ B - B @ A


def anti_commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """计算反对易子 {A, B} = AB + BA"""
    return A @ B + B @ A


# ============================================================================
# 量子信息熵计算
# ============================================================================

def von_neumann_entropy(rho: np.ndarray, base: float = 2) -> float:
    """
    计算Von Neumann熵
    
    S(ρ) = -Tr(ρ log ρ) = -Σ λ_i log(λ_i)
    
    Von Neumann熵是香农熵在量子领域的推广，度量量子态的不确定性。
    
    Args:
        rho: 密度矩阵 (d x d)
        base: 对数的底（默认2，单位为bit；设为e则单位为nat）
    
    Returns:
        Von Neumann熵值（非负）
    
    Example:
        >>> rho = np.array([[0.5, 0], [0, 0.5]])  # 最大混合态
        >>> von_neumann_entropy(rho)
        1.0
    """
    if not is_valid_density_matrix(rho):
        raise ValueError("输入必须是有效的密度矩阵")
    
    # 计算特征值
    eigenvalues = np.linalg.eigvalsh(rho)
    
    # 过滤接近零的特征值避免log(0)
    eigenvalues = eigenvalues[eigenvalues > 1e-12]
    
    # 计算熵
    log_base = np.log(base)
    entropy = -np.sum(eigenvalues * np.log(eigenvalues) / log_base)
    
    return max(0.0, entropy)


def quantum_relative_entropy(rho: np.ndarray, sigma: np.ndarray, 
                             base: float = 2) -> float:
    """
    计算量子相对熵（Umegaki相对熵）
    
    D(ρ||σ) = Tr(ρ log ρ) - Tr(ρ log σ)
    
    量子相对熵度量两个量子态之间的差异，类似于经典相对熵。
    满足Klein不等式：D(ρ||σ) ≥ 0
    
    Args:
        rho: 第一个密度矩阵
        sigma: 第二个密度矩阵
        base: 对数的底
    
    Returns:
        相对熵值（非负）
    
    Note:
        这是非对称度量：D(ρ||σ) ≠ D(σ||ρ)
    """
    if not is_valid_density_matrix(rho) or not is_valid_density_matrix(sigma):
        raise ValueError("输入必须是有效的密度矩阵")
    
    # 计算特征值和特征向量
    eigvals_rho, eigvecs_rho = np.linalg.eigh(rho)
    eigvals_sigma, eigvecs_sigma = np.linalg.eigh(sigma)
    
    log_base = np.log(base)
    
    # 计算 Tr(ρ log ρ)
    valid_rho = eigvals_rho > 1e-12
    term1 = np.sum(eigvals_rho[valid_rho] * 
                   np.log(eigvals_rho[valid_rho]) / log_base)
    
    # 计算 Tr(ρ log σ)
    # 使用谱分解: log σ = Σ log(λ_i) |i⟩⟨i|
    log_sigma_eigvals = np.log(np.maximum(eigvals_sigma, 1e-12)) / log_base
    log_sigma = eigvecs_sigma @ np.diag(log_sigma_eigvals) @ eigvecs_sigma.conj().T
    term2 = np.trace(rho @ log_sigma).real
    
    return max(0.0, term1 - term2)


def quantum_mutual_information(rho_ab: np.ndarray, 
                               dim_a: int, dim_b: int) -> float:
    """
    计算量子互信息
    
    I(A:B) = S(ρ_A) + S(ρ_B) - S(ρ_AB)
    
    量子互信息度量两个子系统之间的总相关性（经典+量子）。
    
    Args:
        rho_ab: 复合系统AB的密度矩阵 (dim_a*dim_b x dim_a*dim_b)
        dim_a: 子系统A的维度
        dim_b: 子系统B的维度
    
    Returns:
        量子互信息值
    """
    # 计算约化密度矩阵
    rho_a = partial_trace(rho_ab, [dim_a, dim_b], 1)
    rho_b = partial_trace(rho_ab, [dim_a, dim_b], 0)
    
    # 计算熵
    s_a = von_neumann_entropy(rho_a)
    s_b = von_neumann_entropy(rho_b)
    s_ab = von_neumann_entropy(rho_ab)
    
    return s_a + s_b - s_ab


def entanglement_entropy(rho_ab: np.ndarray, 
                         dim_a: int, dim_b: int, 
                         subsystem: str = 'A') -> float:
    """
    计算纠缠熵（Entanglement Entropy）
    
    纠缠熵是约化密度矩阵的Von Neumann熵，用于度量纠缠程度。
    
    Args:
        rho_ab: 复合系统的密度矩阵
        dim_a: 子系统A的维度
        dim_b: 子系统B的维度
        subsystem: 要计算熵的子系统（'A'或'B'）
    
    Returns:
        纠缠熵值
    
    Note:
        对于纯态，纠缠熵在A和B上相等。
        对于可分离态，纠缠熵为零。
        对于最大纠缠态（如Bell态），纠缠熵为log(min(dim_a, dim_b))。
    """
    trace_idx = 1 if subsystem == 'A' else 0
    reduced_rho = partial_trace(rho_ab, [dim_a, dim_b], trace_idx)
    return von_neumann_entropy(reduced_rho)


def renyi_entropy(rho: np.ndarray, alpha: float, base: float = 2) -> float:
    """
    计算Renyi熵
    
    S_α(ρ) = (1/(1-α)) log Tr(ρ^α)
    
    Renyi熵是一族由参数α参数化的熵度量。
    - α → 1: 趋近于Von Neumann熵
    - α = 0: Hartley熵（秩的对数）
    - α = 2: 碰撞熵
    - α → ∞: 最小熵
    
    Args:
        rho: 密度矩阵
        alpha: Renyi指数（α > 0, α ≠ 1）
        base: 对数的底
    
    Returns:
        Renyi熵值
    """
    if alpha <= 0:
        raise ValueError("Renyi指数必须为正")
    
    if abs(alpha - 1) < 1e-10:
        return von_neumann_entropy(rho, base)
    
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = eigenvalues[eigenvalues > 1e-12]
    
    log_base = np.log(base)
    tr_rho_alpha = np.sum(eigenvalues ** alpha)
    
    return np.log(tr_rho_alpha) / ((1 - alpha) * log_base)


def quantum_fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """
    计算量子保真度（Uhlmann-Jozsa保真度）
    
    F(ρ, σ) = (Tr√(√ρ σ √ρ))²
    
    保真度度量两个量子态的相似程度，取值范围[0, 1]。
    - F = 1: 两个态完全相同
    - F = 0: 两个态正交（可区分）
    
    Args:
        rho: 第一个密度矩阵
        sigma: 第二个密度矩阵
    
    Returns:
        保真度值（0到1之间）
    """
    # 计算 √ρ
    eigvals_rho, eigvecs_rho = np.linalg.eigh(rho)
    sqrt_rho = eigvecs_rho @ np.diag(np.sqrt(np.maximum(eigvals_rho, 0))) @ \
               eigvecs_rho.conj().T
    
    # 计算 √(√ρ σ √ρ)
    matrix = sqrt_rho @ sigma @ sqrt_rho
    eigvals = np.linalg.eigvalsh(matrix)
    
    fidelity = np.sum(np.sqrt(np.maximum(eigvals, 0))) ** 2
    return min(1.0, max(0.0, fidelity.real))


def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    """
    计算迹距离（Trace Distance）
    
    T(ρ, σ) = (1/2) ||ρ - σ||_1 = (1/2) Tr|ρ - σ|
    
    迹距离是两个量子态之间的度量距离，满足三角不等式。
    取值范围[0, 1]。
    
    Args:
        rho: 第一个密度矩阵
        sigma: 第二个密度矩阵
    
    Returns:
        迹距离值
    """
    diff = rho - sigma
    # 计算 |A| = √(A†A) 的特征值（即奇异值）
    abs_eigvals = np.linalg.svd(diff, compute_uv=False)
    return 0.5 * np.sum(abs_eigvals)


# ============================================================================
# 量子信道模拟
# ============================================================================

class QuantumChannel:
    """
    量子信道基类
    
    量子信道是描述量子系统演化的完全正定保迹（CPTP）映射。
    使用Kraus算子表示：E(ρ) = Σ E_k ρ E_k†
    """
    
    def __init__(self, kraus_operators: List[np.ndarray], name: str = "QuantumChannel"):
        """
        使用Kraus算子初始化量子信道
        
        Args:
            kraus_operators: Kraus算子列表 {E_k}
            name: 信道名称
        """
        self.kraus_ops = [np.array(E, dtype=complex) for E in kraus_operators]
        self.name = name
        self._validate_kraus_operators()
    
    def _validate_kraus_operators(self):
        """验证Kraus算子满足完全正定和保迹条件"""
        dim = self.kraus_ops[0].shape[0]
        
        # 检查保迹条件: Σ E_k† E_k = I
        sum_op = sum(E.conj().T @ E for E in self.kraus_ops)
        if not np.allclose(sum_op, np.eye(dim)):
            raise ValueError(f"Kraus算子不满足保迹条件: Σ E_k† E_k ≠ I")
    
    def apply(self, rho: np.ndarray) -> np.ndarray:
        """
        应用量子信道
        
        E(ρ) = Σ E_k ρ E_k†
        
        Args:
            rho: 输入密度矩阵
        
        Returns:
            输出密度矩阵
        """
        return sum(E @ rho @ E.conj().T for E in self.kraus_ops)
    
    def is_unital(self) -> bool:
        """
        检查信道是否保单位（Unital）
        
        Unital信道满足：E(I) = I
        """
        dim = self.kraus_ops[0].shape[0]
        identity = np.eye(dim, dtype=complex)
        return np.allclose(self.apply(identity), identity)
    
    def complementary_channel(self, rho: np.ndarray) -> np.ndarray:
        """
        计算互补信道（Complementary Channel）
        
        返回环境系统的状态，用于分析信息流向环境的过程。
        
        Args:
            rho: 输入密度矩阵
        
        Returns:
            环境的密度矩阵
        """
        dim_in = self.kraus_ops[0].shape[1]
        dim_out = self.kraus_ops[0].shape[0]
        dim_env = len(self.kraus_ops)
        
        # 构建等距映射 V = Σ E_k ⊗ |k⟩
        v_matrix = np.zeros((dim_out * dim_env, dim_in), dtype=complex)
        for k, E_k in enumerate(self.kraus_ops):
            v_matrix[k * dim_out:(k + 1) * dim_out, :] = E_k
        
        # 环境状态 = Tr_output(V ρ V†)
        total = v_matrix @ rho @ v_matrix.conj().T
        
        # 迹掉输出空间得到环境状态
        return partial_trace(total, [dim_out, dim_env], 0)
    
    def __repr__(self):
        return f"{self.name}(kraus_ops={len(self.kraus_ops)})"


class DepolarizingChannel(QuantumChannel):
    """
    退极化信道（Depolarizing Channel）
    
    模拟量子比特以概率p被完全随机化的过程：
    E(ρ) = (1-p)ρ + p(I/d)
    
    这是最常见的噪声模型之一。
    """
    
    def __init__(self, p: float, dim: int = 2):
        """
        初始化退极化信道
        
        Args:
            p: 退极化概率 (0 ≤ p ≤ 1)
            dim: 系统维度（默认为2，即qubit）
        """
        if not 0 <= p <= 1:
            raise ValueError("退极化概率p必须在[0, 1]范围内")
        
        self.p = p
        self.dim = dim
        
        # Kraus算子
        kraus_ops = []
        
        # 主要项
        E0 = np.sqrt(1 - p + p/dim**2) * np.eye(dim, dtype=complex)
        kraus_ops.append(E0)
        
        # 对于qubit，使用Pauli矩阵作为噪声基
        if dim == 2:
            pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
            pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
            pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
            
            kraus_ops.extend([
                np.sqrt(p/3) * pauli_x,
                np.sqrt(p/3) * pauli_y,
                np.sqrt(p/3) * pauli_z
            ])
        
        super().__init__(kraus_ops, name=f"Depolarizing(p={p})")


class AmplitudeDampingChannel(QuantumChannel):
    """
    振幅阻尼信道（Amplitude Damping Channel）
    
    模拟能量耗散过程，如量子系统与热库的相互作用。
    描述从|1⟩到|0⟩的衰减过程。
    """
    
    def __init__(self, gamma: float):
        """
        初始化振幅阻尼信道
        
        Args:
            gamma: 阻尼系数 (0 ≤ γ ≤ 1)
        """
        if not 0 <= gamma <= 1:
            raise ValueError("阻尼系数γ必须在[0, 1]范围内")
        
        self.gamma = gamma
        
        E0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
        E1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
        
        super().__init__([E0, E1], name=f"AmplitudeDamping(γ={gamma})")


class PhaseDampingChannel(QuantumChannel):
    """
    相位阻尼信道（Phase Damping Channel）
    
    模拟相位信息丢失过程，不交换能量但丢失相对相位信息。
    描述量子叠加态退相干为经典混合态的过程。
    """
    
    def __init__(self, lambda_: float):
        """
        初始化相位阻尼信道
        
        Args:
            lambda_: 阻尼系数 (0 ≤ λ ≤ 1)
        """
        if not 0 <= lambda_ <= 1:
            raise ValueError("阻尼系数λ必须在[0, 1]范围内")
        
        self.lambda_ = lambda_
        
        E0 = np.array([[1, 0], [0, np.sqrt(1 - lambda_)]], dtype=complex)
        E1 = np.array([[0, 0], [0, np.sqrt(lambda_)]], dtype=complex)
        
        super().__init__([E0, E1], name=f"PhaseDamping(λ={lambda_})")


class BitFlipChannel(QuantumChannel):
    """
    比特翻转信道（Bit Flip Channel）
    
    模拟以概率p翻转量子比特（|0⟩ ↔ |1⟩）的过程。
    """
    
    def __init__(self, p: float):
        """
        初始化比特翻转信道
        
        Args:
            p: 翻转概率 (0 ≤ p ≤ 1)
        """
        if not 0 <= p <= 1:
            raise ValueError("翻转概率p必须在[0, 1]范围内")
        
        self.p = p
        
        E0 = np.sqrt(1 - p) * np.eye(2, dtype=complex)
        E1 = np.sqrt(p) * np.array([[0, 1], [1, 0]], dtype=complex)
        
        super().__init__([E0, E1], name=f"BitFlip(p={p})")


class PhaseFlipChannel(QuantumChannel):
    """
    相位翻转信道（Phase Flip Channel / Z-Channel）
    
    模拟以概率p翻转量子比特相位（|1⟩ → -|1⟩）的过程。
    """
    
    def __init__(self, p: float):
        """
        初始化相位翻转信道
        
        Args:
            p: 翻转概率 (0 ≤ p ≤ 1)
        """
        if not 0 <= p <= 1:
            raise ValueError("翻转概率p必须在[0, 1]范围内")
        
        self.p = p
        
        E0 = np.sqrt(1 - p) * np.eye(2, dtype=complex)
        E1 = np.sqrt(p) * np.array([[1, 0], [0, -1]], dtype=complex)
        
        super().__init__([E0, E1], name=f"PhaseFlip(p={p})")


class UnitaryChannel(QuantumChannel):
    """
    酉信道（Unitary Channel）
    
    描述幺正演化：E(ρ) = U ρ U†
    这是可逆的量子操作。
    """
    
    def __init__(self, U: np.ndarray):
        """
        初始化酉信道
        
        Args:
            U: 酉矩阵（满足 U†U = I）
        """
        U = np.array(U, dtype=complex)
        
        # 验证酉性: U†U = I
        if not np.allclose(U @ U.conj().T, np.eye(U.shape[0])):
            raise ValueError("矩阵必须是酉矩阵")
        
        self.U = U
        super().__init__([U], name="Unitary")


class CompositeChannel(QuantumChannel):
    """
    复合信道
    
    组合多个量子信道：E = E_n ∘ ... ∘ E_2 ∘ E_1
    """
    
    def __init__(self, channels: List[QuantumChannel]):
        """
        初始化复合信道
        
        Args:
            channels: 信道列表（按应用顺序）
        """
        self.channels = channels
        
        # 复合信道的Kraus算子是所有可能的乘积
        # 这里我们存储原始信道并在apply中顺序应用
        dim = channels[0].kraus_ops[0].shape[0]
        identity = np.eye(dim, dtype=complex)
        super().__init__([identity], name="Composite")
    
    def apply(self, rho: np.ndarray) -> np.ndarray:
        """顺序应用所有信道"""
        result = rho
        for channel in self.channels:
            result = channel.apply(result)
        return result


# ============================================================================
# Schema定义
# ============================================================================

@dataclass
class SchemaField:
    """Schema字段定义"""
    name: str
    field_type: str
    constraints: Dict = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.name, self.field_type))


@dataclass
class Schema:
    """
    Schema定义
    
    表示数据结构模式，可映射为量子态。
    """
    name: str
    fields: List[SchemaField]
    metadata: Dict = field(default_factory=dict)
    
    def get_dimension(self) -> int:
        """
        计算Schema对应的量子态维度
        
        每个字段对应一个qubit，维度为 2^n_fields
        """
        return 2 ** len(self.fields)
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            'name': self.name,
            'fields': [
                {
                    'name': f.name,
                    'type': f.field_type,
                    'constraints': f.constraints
                } for f in self.fields
            ],
            'metadata': self.metadata
        }
    
    def __hash__(self):
        return hash(self.name)


# ============================================================================
# Schema到量子态的映射
# ============================================================================

class SchemaEncoding(Enum):
    """Schema编码方法"""
    BASIS = "basis"           # 基态编码
    SUPERPOSITION = "superposition"  # 叠加态编码
    AMPLITUDE = "amplitude"   # 振幅编码
    FEATURE = "feature"       # 特征编码


class SchemaToQuantumMapper:
    """
    Schema到量子态的映射器
    
    提供多种策略将Schema结构映射为量子态。
    """
    
    def __init__(self, encoding_method: SchemaEncoding = SchemaEncoding.BASIS):
        """
        初始化映射器
        
        Args:
            encoding_method: 编码方法
        """
        self.encoding_method = encoding_method
    
    def schema_to_pure_state(self, schema: Schema) -> np.ndarray:
        """
        将Schema映射为纯量子态
        
        Args:
            schema: Schema定义
        
        Returns:
            量子态向量（归一化）
        """
        n_qubits = len(schema.fields)
        dim = 2 ** n_qubits
        
        if self.encoding_method == SchemaEncoding.BASIS:
            # 计算Schema的确定性哈希作为状态索引
            hash_val = hash(schema.name) & 0xFFFFFFFF
            for field in schema.fields:
                hash_val ^= (hash(field.name) ^ hash(field.field_type)) & 0xFFFFFFFF
            
            state_idx = hash_val % dim
            state = np.zeros(dim, dtype=complex)
            state[state_idx] = 1.0
            
        elif self.encoding_method == SchemaEncoding.SUPERPOSITION:
            # 创建等权重的叠加态
            state = np.ones(dim, dtype=complex) / np.sqrt(dim)
            
        elif self.encoding_method == SchemaEncoding.AMPLITUDE:
            # 使用字段特征作为振幅
            features = self._extract_schema_features(schema)
            state = self.amplitude_encoding(features, dim)
            
        else:
            raise ValueError(f"未知的编码方法: {self.encoding_method}")
        
        return state
    
    def _extract_schema_features(self, schema: Schema) -> np.ndarray:
        """提取Schema的特征向量"""
        features = []
        
        # 字段数量
        features.append(float(len(schema.fields)))
        
        # 类型多样性
        type_set = set(f.field_type for f in schema.fields)
        features.append(float(len(type_set)))
        
        # 约束复杂度
        constraint_count = sum(
            len(f.constraints) for f in schema.fields
        )
        features.append(float(constraint_count))
        
        # 元数据数量
        features.append(float(len(schema.metadata)))
        
        return np.array(features)
    
    def amplitude_encoding(self, features: np.ndarray, target_dim: int) -> np.ndarray:
        """
        振幅编码：将特征向量编码为量子态振幅
        
        |ψ⟩ = Σ x_i |i⟩
        
        Args:
            features: 特征向量
            target_dim: 目标维度
        
        Returns:
            编码后的量子态
        """
        # 扩展到目标维度
        if len(features) < target_dim:
            # 填充零
            extended = np.zeros(target_dim)
            extended[:len(features)] = features
        else:
            extended = features[:target_dim]
        
        # 归一化
        norm = np.linalg.norm(extended)
        if norm < 1e-10:
            # 如果特征全为零，使用均匀分布
            extended = np.ones(target_dim) / np.sqrt(target_dim)
        else:
            extended = extended / norm
        
        return extended.astype(complex)
    
    def schemas_to_density_matrix(self, schemas: List[Schema], 
                                   probabilities: List[float] = None) -> np.ndarray:
        """
        将Schema集合映射为混合态密度矩阵
        
        ρ = Σ p_i |ψ_i⟩⟨ψ_i|
        
        Args:
            schemas: Schema列表
            probabilities: 每个Schema的概率（默认为均匀分布）
        
        Returns:
            混合态密度矩阵
        """
        if not schemas:
            raise ValueError("Schema列表不能为空")
        
        if probabilities is None:
            probabilities = [1.0 / len(schemas)] * len(schemas)
        
        if len(schemas) != len(probabilities):
            raise ValueError("Schema数量和概率数量必须相等")
        
        if not np.isclose(sum(probabilities), 1.0):
            raise ValueError("概率之和必须等于1")
        
        dim = schemas[0].get_dimension()
        rho = np.zeros((dim, dim), dtype=complex)
        
        for schema, p in zip(schemas, probabilities):
            state = self.schema_to_pure_state(schema)
            rho += p * np.outer(state, state.conj())
        
        return rho
    
    def create_entangled_schema_state(self, schema_a: Schema, 
                                       schema_b: Schema,
                                       bell_type: str = "phi+") -> np.ndarray:
        """
        创建两个Schema之间的纠缠态
        
        Args:
            schema_a: 第一个Schema
            schema_b: 第二个Schema
            bell_type: Bell态类型 ("phi+", "phi-", "psi+", "psi-")
        
        Returns:
            纠缠态向量
        """
        basis_0 = np.array([1, 0], dtype=complex)
        basis_1 = np.array([0, 1], dtype=complex)
        
        if bell_type == "phi+":
            # |Φ+⟩ = (|00⟩ + |11⟩)/√2
            state = (np.kron(basis_0, basis_0) + 
                    np.kron(basis_1, basis_1)) / np.sqrt(2)
        elif bell_type == "phi-":
            # |Φ-⟩ = (|00⟩ - |11⟩)/√2
            state = (np.kron(basis_0, basis_0) - 
                    np.kron(basis_1, basis_1)) / np.sqrt(2)
        elif bell_type == "psi+":
            # |Ψ+⟩ = (|01⟩ + |10⟩)/√2
            state = (np.kron(basis_0, basis_1) + 
                    np.kron(basis_1, basis_0)) / np.sqrt(2)
        elif bell_type == "psi-":
            # |Ψ-⟩ = (|01⟩ - |10⟩)/√2
            state = (np.kron(basis_0, basis_1) - 
                    np.kron(basis_1, basis_0)) / np.sqrt(2)
        else:
            raise ValueError(f"未知的Bell态类型: {bell_type}")
        
        return state


# ============================================================================
# Schema相似度与距离度量
# ============================================================================

class SchemaQuantumMetrics:
    """
    基于量子信息的Schema度量
    
    提供多种基于量子理论的相似度和距离度量方法。
    """
    
    @staticmethod
    def entropy_similarity(rho1: np.ndarray, rho2: np.ndarray) -> float:
        """
        基于熵的相似度度量
        
        相似度 = exp(-|S(ρ1) - S(ρ2)|)
        
        Returns:
            相似度值（0到1之间，1表示最相似）
        """
        s1 = von_neumann_entropy(rho1)
        s2 = von_neumann_entropy(rho2)
        return np.exp(-abs(s1 - s2))
    
    @staticmethod
    def relative_entropy_dissimilarity(rho1: np.ndarray, 
                                        rho2: np.ndarray) -> float:
        """
        基于相对熵的不相似度
        
        注意：这是不对称的度量
        
        Returns:
            不相似度值（0到1之间）
        """
        try:
            d = quantum_relative_entropy(rho1, rho2)
            # 归一化到[0, 1]
            return 1 - np.exp(-d)
        except:
            return 1.0
    
    @staticmethod
    def fidelity_similarity(rho1: np.ndarray, rho2: np.ndarray) -> float:
        """
        基于保真度的相似度
        
        Returns:
            保真度值（0到1之间）
        """
        return quantum_fidelity(rho1, rho2)
    
    @staticmethod
    def trace_distance_metric(rho1: np.ndarray, rho2: np.ndarray) -> float:
        """
        基于迹距离的度量
        
        Returns:
            迹距离值（0到1之间）
        """
        return trace_distance(rho1, rho2)
    
    @staticmethod
    def quantum_js_divergence(rho1: np.ndarray, rho2: np.ndarray) -> float:
        """
        量子Jensen-Shannon散度
        
        对称化的相对熵度量。
        """
        rho_mix = 0.5 * (rho1 + rho2)
        
        d1 = quantum_relative_entropy(rho1, rho_mix)
        d2 = quantum_relative_entropy(rho2, rho_mix)
        
        return 0.5 * (d1 + d2)


# ============================================================================
# 量子Schema转换
# ============================================================================

class QuantumSchemaTransformer:
    """
    量子Schema转换器
    
    使用量子信道对Schema进行转换和分析。
    """
    
    def __init__(self, mapper: Optional[SchemaToQuantumMapper] = None):
        """
        初始化转换器
        
        Args:
            mapper: Schema到量子态的映射器（默认创建新的）
        """
        self.mapper = mapper or SchemaToQuantumMapper()
    
    def apply_channel_to_schema(self, schema: Schema, 
                                 channel: QuantumChannel) -> np.ndarray:
        """
        将量子信道应用于Schema
        
        流程：Schema → 量子态 → 应用信道 → 输出态
        
        Args:
            schema: 输入Schema
            channel: 量子信道
        
        Returns:
            转换后的密度矩阵
        """
        # Schema → 量子态
        state = self.mapper.schema_to_pure_state(schema)
        rho = np.outer(state, state.conj())
        
        # 应用信道
        transformed_rho = channel.apply(rho)
        
        return transformed_rho
    
    def transform_schema_ensemble(self, 
                                   schemas: List[Schema],
                                   channel: QuantumChannel,
                                   probs: List[float] = None) -> np.ndarray:
        """
        转换Schema集合
        
        Args:
            schemas: Schema列表
            channel: 量子信道
            probs: 概率分布
        
        Returns:
            转换后的密度矩阵
        """
        rho = self.mapper.schemas_to_density_matrix(schemas, probs)
        return channel.apply(rho)
    
    def compute_transformation_entropy(self, 
                                        input_schema: Schema,
                                        channel: QuantumChannel) -> float:
        """
        计算Schema转换的熵变
        
        ΔS = S(E(ρ)) - S(ρ)
        
        正值表示信息丢失，负值表示信息增益。
        
        Args:
            input_schema: 输入Schema
            channel: 量子信道
        
        Returns:
            熵变值
        """
        state = self.mapper.schema_to_pure_state(input_schema)
        rho = np.outer(state, state.conj())
        
        s_in = von_neumann_entropy(rho)
        s_out = von_neumann_entropy(channel.apply(rho))
        
        return s_out - s_in
    
    def compute_channel_capacity(self, 
                                  schemas: List[Schema],
                                  channel: QuantumChannel) -> float:
        """
        计算信道容量（Holevo信息）
        
        χ = S(Σ p_i E(ρ_i)) - Σ p_i S(E(ρ_i))
        
        Args:
            schemas: 输入Schema集合
            channel: 量子信道
        
        Returns:
            Holevo信息量
        """
        probs = [1.0 / len(schemas)] * len(schemas)
        
        # 计算平均输出态
        output_states = []
        for schema in schemas:
            state = self.mapper.schema_to_pure_state(schema)
            rho = np.outer(state, state.conj())
            output_states.append(channel.apply(rho))
        
        avg_output = sum(p * rho for p, rho in zip(probs, output_states))
        
        # Holevo信息
        term1 = von_neumann_entropy(avg_output)
        term2 = sum(p * von_neumann_entropy(rho) 
                   for p, rho in zip(probs, output_states))
        
        return term1 - term2


# ============================================================================
# 实用工具函数
# ============================================================================

def create_bell_state(bell_type: str = "phi+") -> np.ndarray:
    """
    创建标准Bell态
    
    Args:
        bell_type: Bell态类型
    
    Returns:
        Bell态向量
    """
    mapper = SchemaToQuantumMapper()
    dummy_schema = Schema("dummy", [SchemaField("a", "int"), SchemaField("b", "int")])
    return mapper.create_entangled_schema_state(dummy_schema, dummy_schema, bell_type)


def create_ghz_state(n_qubits: int) -> np.ndarray:
    """
    创建GHZ态（Greenberger-Horne-Zeilinger态）
    
    |GHZ⟩ = (|0...0⟩ + |1...1⟩)/√2
    
    Args:
        n_qubits: 量子比特数
    
    Returns:
        GHZ态向量
    """
    dim = 2 ** n_qubits
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0 / np.sqrt(2)
    state[dim - 1] = 1.0 / np.sqrt(2)
    return state


def create_w_state(n_qubits: int) -> np.ndarray:
    """
    创建W态
    
    |W⟩ = (|100...0⟩ + |010...0⟩ + ... + |00...01⟩)/√n
    
    Args:
        n_qubits: 量子比特数
    
    Returns:
        W态向量
    """
    dim = 2 ** n_qubits
    state = np.zeros(dim, dtype=complex)
    
    for i in range(n_qubits):
        idx = 2 ** (n_qubits - 1 - i)
        state[idx] = 1.0 / np.sqrt(n_qubits)
    
    return state


def measure_in_basis(state: np.ndarray, basis: np.ndarray) -> Tuple[float, np.ndarray]:
    """
    在指定基矢下测量量子态
    
    Args:
        state: 量子态向量
        basis: 测量基（酉矩阵）
    
    Returns:
        (测量结果概率列表, 投影后的态)
    """
    # 变换到测量基
    transformed = basis.conj().T @ state
    
    # 计算概率
    probabilities = np.abs(transformed) ** 2
    
    return probabilities, transformed


# ============================================================================
# 示例与演示
# ============================================================================

def demo_quantum_entropy():
    """演示量子熵计算"""
    print("=" * 60)
    print("量子熵计算演示")
    print("=" * 60)
    
    # 纯态（零熵）
    pure_state = np.array([1, 0], dtype=complex)
    rho_pure = np.outer(pure_state, pure_state)
    print(f"纯态 |0⟩ 熵: {von_neumann_entropy(rho_pure):.6f}")
    
    # 最大混合态（最大熵）
    rho_max_mixed = np.eye(2, dtype=complex) / 2
    print(f"最大混合态熵: {von_neumann_entropy(rho_max_mixed):.6f} (理论值: 1.0)")
    
    # 部分混合态
    for p in [0.9, 0.8, 0.5, 0.2]:
        rho_mixed = p * rho_pure + (1 - p) * rho_max_mixed
        entropy = von_neumann_entropy(rho_mixed)
        print(f"混合态 (p={p:.1f}) 熵: {entropy:.6f}")
    
    # Renyi熵
    print(f"\nRenyi熵 (α=0, Hartley熵): {renyi_entropy(rho_max_mixed, 0.01):.6f}")
    print(f"Renyi熵 (α=1, 趋近Von Neumann): {renyi_entropy(rho_max_mixed, 1.001):.6f}")
    print(f"Renyi熵 (α=2, 碰撞熵): {renyi_entropy(rho_max_mixed, 2):.6f}")


def demo_quantum_channels():
    """演示量子信道"""
    print("\n" + "=" * 60)
    print("量子信道演示")
    print("=" * 60)
    
    # 初始态: |+⟩ = (|0⟩ + |1⟩)/√2
    plus_state = np.array([1, 1], dtype=complex) / np.sqrt(2)
    rho = np.outer(plus_state, plus_state)
    
    print(f"初始态 |+⟩ 熵: {von_neumann_entropy(rho):.6f}")
    
    # 退极化信道
    print("\n--- 退极化信道 ---")
    for p in [0.1, 0.3, 0.5, 0.9]:
        depol = DepolarizingChannel(p=p)
        rho_depol = depol.apply(rho)
        print(f"p={p:.1f}: 输出熵={von_neumann_entropy(rho_depol):.6f}")
    
    # 振幅阻尼信道
    print("\n--- 振幅阻尼信道 ---")
    for gamma in [0.1, 0.3, 0.5, 0.9]:
        damping = AmplitudeDampingChannel(gamma=gamma)
        rho_damp = damping.apply(rho)
        print(f"γ={gamma:.1f}: 输出熵={von_neumann_entropy(rho_damp):.6f}")
    
    # 相位阻尼信道
    print("\n--- 相位阻尼信道 ---")
    for lambda_ in [0.1, 0.3, 0.5, 0.9]:
        phase_damp = PhaseDampingChannel(lambda_=lambda_)
        rho_phase = phase_damp.apply(rho)
        print(f"λ={lambda_:.1f}: 输出熵={von_neumann_entropy(rho_phase):.6f}")


def demo_schema_mapping():
    """演示Schema到量子态的映射"""
    print("\n" + "=" * 60)
    print("Schema到量子态映射演示")
    print("=" * 60)
    
    # 定义Schema
    user_schema = Schema(
        name="User",
        fields=[
            SchemaField("id", "UUID", {"required": True}),
            SchemaField("name", "String", {"maxLength": 100}),
            SchemaField("email", "String", {"format": "email"}),
            SchemaField("active", "Boolean", {"default": True})
        ],
        metadata={"version": "1.0", "domain": "auth"}
    )
    
    product_schema = Schema(
        name="Product",
        fields=[
            SchemaField("id", "UUID"),
            SchemaField("name", "String"),
            SchemaField("price", "Decimal", {"precision": 10, "scale": 2}),
            SchemaField("category", "String"),
            SchemaField("in_stock", "Boolean")
        ],
        metadata={"version": "2.0", "domain": "inventory"}
    )
    
    print(f"User Schema: {len(user_schema.fields)} 字段, 维度={user_schema.get_dimension()}")
    print(f"Product Schema: {len(product_schema.fields)} 字段, 维度={product_schema.get_dimension()}")
    
    # 映射为量子态
    mapper = SchemaToQuantumMapper(encoding_method=SchemaEncoding.BASIS)
    
    user_state = mapper.schema_to_pure_state(user_schema)
    product_state = mapper.schema_to_pure_state(product_schema)
    
    print(f"\nUser State: {len(user_state)} 维")
    print(f"Product State: {len(product_state)} 维")
    
    # 构建密度矩阵
    rho_user = np.outer(user_state, user_state.conj())
    rho_product = np.outer(product_state, product_state.conj())
    
    print(f"\nUser Schema熵: {von_neumann_entropy(rho_user):.6f}")
    print(f"Product Schema熵: {von_neumann_entropy(rho_product):.6f}")
    
    # 计算相似度
    fidelity = quantum_fidelity(rho_user, rho_product)
    trace_dist = trace_distance(rho_user, rho_product)
    
    print(f"\nSchema保真度: {fidelity:.6f}")
    print(f"Schema迹距离: {trace_dist:.6f}")
    
    # 创建混合系综
    rho_ensemble = mapper.schemas_to_density_matrix(
        [user_schema, product_schema],
        [0.6, 0.4]
    )
    print(f"混合系综熵: {von_neumann_entropy(rho_ensemble):.6f}")


def demo_entanglement():
    """演示纠缠和纠缠熵"""
    print("\n" + "=" * 60)
    print("量子纠缠演示")
    print("=" * 60)
    
    bell_types = ["phi+", "phi-", "psi+", "psi-"]
    
    for bell_type in bell_types:
        # Bell态
        bell_state = create_bell_state(bell_type)
        rho_bell = np.outer(bell_state, bell_state)
        
        # 纠缠熵
        s_a = entanglement_entropy(rho_bell, 2, 2, 'A')
        s_b = entanglement_entropy(rho_bell, 2, 2, 'B')
        mi = quantum_mutual_information(rho_bell, 2, 2)
        
        print(f"|{bell_type}⟩: S_A={s_a:.4f}, S_B={s_b:.4f}, I(A:B)={mi:.4f}")
    
    # GHZ态
    print("\n--- GHZ态 ---")
    for n in [3, 4, 5]:
        ghz = create_ghz_state(n)
        rho_ghz = np.outer(ghz, ghz)
        
        # 对第一个qubit计算纠缠熵
        dims = [2] * n
        reduced = partial_trace(rho_ghz, dims, list(range(1, n)))
        s = von_neumann_entropy(reduced)
        print(f"GHZ({n}): 单比特纠缠熵={s:.4f}")
    
    # W态
    print("\n--- W态 ---")
    for n in [3, 4, 5]:
        w = create_w_state(n)
        rho_w = np.outer(w, w)
        
        dims = [2] * n
        reduced = partial_trace(rho_w, dims, list(range(1, n)))
        s = von_neumann_entropy(reduced)
        print(f"W({n}): 单比特纠缠熵={s:.4f}")


def demo_relative_entropy():
    """演示相对熵"""
    print("\n" + "=" * 60)
    print("量子相对熵演示")
    print("=" * 60)
    
    # 定义不同的量子态
    states = {
        "|0⟩": np.array([[1, 0], [0, 0]], dtype=complex),
        "|1⟩": np.array([[0, 0], [0, 1]], dtype=complex),
        "|+⟩": np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex),
        "混合(0.7)": np.array([[0.7, 0], [0, 0.3]], dtype=complex),
        "最大混合": np.eye(2, dtype=complex) / 2
    }
    
    print("相对熵矩阵 D(行||列):")
    print("-" * 60)
    
    names = list(states.keys())
    for name1 in names:
        row = []
        for name2 in names:
            rho1 = states[name1]
            rho2 = states[name2]
            try:
                d = quantum_relative_entropy(rho1, rho2)
                row.append(f"{d:.3f}")
            except:
                row.append("∞")
        print(f"{name1:12}: {' | '.join(row)}")
    
    print("\n注: 相对熵非对称，D(ρ||σ) ≠ D(σ||ρ)")


def demo_schema_transformation():
    """演示Schema的量子转换"""
    print("\n" + "=" * 60)
    print("Schema量子转换演示")
    print("=" * 60)
    
    # 定义Schema
    schema = Schema(
        name="Document",
        fields=[
            SchemaField("id", "UUID", {"required": True}),
            SchemaField("title", "String", {"maxLength": 200}),
            SchemaField("content", "Text"),
            SchemaField("author", "Reference"),
            SchemaField("tags", "Array")
        ]
    )
    
    transformer = QuantumSchemaTransformer()
    
    print(f"原始Schema: {schema.name}")
    print(f"字段数: {len(schema.fields)}")
    
    # 应用不同信道
    channels = {
        "退极化(p=0.1)": DepolarizingChannel(p=0.1),
        "退极化(p=0.3)": DepolarizingChannel(p=0.3),
        "振幅阻尼(γ=0.15)": AmplitudeDampingChannel(gamma=0.15),
        "相位阻尼(λ=0.25)": PhaseDampingChannel(lambda_=0.25)
    }
    
    print("\n信道对Schema的影响:")
    for name, channel in channels.items():
        entropy_change = transformer.compute_transformation_entropy(schema, channel)
        print(f"  {name}: 熵变 = {entropy_change:+.6f}")


def demo_complete_workflow():
    """完整工作流演示"""
    print("\n" + "=" * 60)
    print("完整工作流演示：量子加密Schema分析")
    print("=" * 60)
    
    # 定义量子加密消息Schema
    qkd_schema = Schema(
        name="QKDMessage",
        fields=[
            SchemaField("protocol", "Enum", {"values": ["BB84", "E91", "B92"]}),
            SchemaField("basis", "Array", {"itemType": "Basis"}),
            SchemaField("ciphertext", "BitString", {"encrypted": True}),
            SchemaField("auth_tag", "Hash", {"algorithm": "SHA256"})
        ],
        metadata={
            "protocol": "BB84",
            "security_level": "high",
            "qubit_count": 1024
        }
    )
    
    # 映射为量子态
    mapper = SchemaToQuantumMapper()
    state = mapper.schema_to_pure_state(qkd_schema)
    rho = np.outer(state, state.conj())
    
    print(f"Schema: {qkd_schema.name}")
    print(f"协议: {qkd_schema.metadata.get('protocol')}")
    print(f"安全级别: {qkd_schema.metadata.get('security_level')}")
    print(f"\n初始态Von Neumann熵: {von_neumann_entropy(rho):.6f}")
    
    # 模拟不同强度的噪声信道（模拟不同程度的窃听攻击）
    print("\n--- 安全性分析（模拟噪声信道） ---")
    
    attack_scenarios = [
        ("无攻击", 0.0),
        ("弱攻击", 0.05),
        ("中等攻击", 0.15),
        ("强攻击", 0.30)
    ]
    
    for scenario, noise in attack_scenarios:
        eavesdrop_channel = DepolarizingChannel(p=noise)
        rho_noisy = eavesdrop_channel.apply(rho)
        
        fidelity = quantum_fidelity(rho, rho_noisy)
        info_loss = 1 - fidelity
        
        print(f"\n{scenario} (噪声={noise:.0%}):")
        print(f"  保真度: {fidelity:.6f}")
        print(f"  信息损失: {info_loss:.6f}")
        
        # 安全评估
        if fidelity > 0.95:
            status = "✓ 安全"
        elif fidelity > 0.85:
            status = "⚠ 警告"
        else:
            status = "✗ 危险"
        print(f"  状态: {status}")
    
    # 纠缠分析
    print("\n--- 纠缠安全性分析 ---")
    
    # 创建两个QKD消息的纠缠态（模拟量子密钥分发中的纠缠对）
    bell_state = mapper.create_entangled_schema_state(
        qkd_schema, qkd_schema, "phi+"
    )
    rho_entangled = np.outer(bell_state, bell_state.conj())
    
    s_entangled = entanglement_entropy(rho_entangled, 2, 2, 'A')
    print(f"纠缠对纠缠熵: {s_entangled:.6f}")
    print(f"最大可能纠缠熵: 1.0 (log₂(2))")
    print(f"纠缠纯度: {s_entangled:.2%}")


def demo_metrics_comparison():
    """比较不同的Schema相似度度量"""
    print("\n" + "=" * 60)
    print("Schema相似度度量比较")
    print("=" * 60)
    
    # 创建三个不同的Schema
    schemas = [
        Schema("Simple", [
            SchemaField("id", "UUID"),
            SchemaField("name", "String")
        ]),
        Schema("Medium", [
            SchemaField("id", "UUID"),
            SchemaField("name", "String"),
            SchemaField("email", "String"),
            SchemaField("active", "Boolean")
        ]),
        Schema("Complex", [
            SchemaField("id", "UUID"),
            SchemaField("name", "String"),
            SchemaField("email", "String"),
            SchemaField("active", "Boolean"),
            SchemaField("roles", "Array"),
            SchemaField("metadata", "Object")
        ])
    ]
    
    names = ["Simple", "Medium", "Complex"]
    
    mapper = SchemaToQuantumMapper()
    states = []
    rhos = []
    
    for schema in schemas:
        state = mapper.schema_to_pure_state(schema)
        rho = np.outer(state, state.conj())
        states.append(state)
        rhos.append(rho)
    
    metrics = SchemaQuantumMetrics()
    
    # 计算各种度量
    print("\n保真度相似度矩阵:")
    print("-" * 40)
    for i, name1 in enumerate(names):
        row = []
        for j, name2 in enumerate(names):
            fid = metrics.fidelity_similarity(rhos[i], rhos[j])
            row.append(f"{fid:.4f}")
        print(f"{name1:8}: {' | '.join(row)}")
    
    print("\n迹距离矩阵:")
    print("-" * 40)
    for i, name1 in enumerate(names):
        row = []
        for j, name2 in enumerate(names):
            dist = metrics.trace_distance_metric(rhos[i], rhos[j])
            row.append(f"{dist:.4f}")
        print(f"{name1:8}: {' | '.join(row)}")


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    # 运行所有演示
    demo_quantum_entropy()
    demo_quantum_channels()
    demo_schema_mapping()
    demo_entanglement()
    demo_relative_entropy()
    demo_schema_transformation()
    demo_complete_workflow()
    demo_metrics_comparison()
    
    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)
