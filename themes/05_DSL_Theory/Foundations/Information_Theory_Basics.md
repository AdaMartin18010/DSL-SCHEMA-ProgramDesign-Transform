# 信息论基础理论

## 概述

信息论是研究信息的量化、存储和传输的数学理论。在DSL Schema转换中，信息论提供了量化转换质量和信息损失的理论基础。

---

## 核心概念

### 1. 信息熵 (Information Entropy)

**定义**：
信息熵度量随机变量的不确定性，由克劳德·香农于1948年提出。

**数学公式**：
```
H(X) = -Σ P(x) log₂ P(x)

其中：
- X: 离散随机变量
- P(x): 事件x发生的概率
- H(X): X的信息熵（单位：比特 bits）
```

**直观解释**：
- 熵越高，不确定性越大，信息量越大
- 熵越低，不确定性越小，信息量越小
- 确定事件的熵为0

**在Schema转换中的应用**：
```python
# 计算Schema的信息熵
def calculate_schema_entropy(schema):
    """
    计算Schema的信息熵
    
    参数:
        schema: Schema对象，包含属性和类型分布
    
    返回:
        信息熵值（比特）
    """
    from collections import Counter
    import math
    
    # 统计类型分布
    type_counts = Counter(prop.type for prop in schema.properties)
    total = len(schema.properties)
    
    # 计算熵
    entropy = 0
    for count in type_counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    
    return entropy
```

---

### 2. 联合熵与条件熵

**联合熵 (Joint Entropy)**：
```
H(X, Y) = -ΣΣ P(x, y) log₂ P(x, y)

度量两个随机变量共同的不确定性
```

**条件熵 (Conditional Entropy)**：
```
H(Y|X) = Σ P(x) H(Y|X=x)
       = -ΣΣ P(x, y) log₂ P(y|x)

度量已知X时Y的不确定性
```

**链式法则**：
```
H(X, Y) = H(X) + H(Y|X)
        = H(Y) + H(X|Y)
```

**在Schema转换中的应用**：
```python
def calculate_conditional_entropy(source_schema, target_schema, mapping):
    """
    计算条件熵，评估转换的信息损失
    """
    # 计算源Schema和目标Schema的联合分布
    joint_distribution = compute_joint_distribution(source_schema, target_schema, mapping)
    
    # 计算条件熵 H(Target|Source)
    conditional_entropy = 0
    for s_val, t_val, prob in joint_distribution:
        conditional_prob = compute_conditional_probability(t_val, s_val, mapping)
        if conditional_prob > 0:
            conditional_entropy -= prob * math.log2(conditional_prob)
    
    return conditional_entropy
```

---

### 3. 互信息 (Mutual Information)

**定义**：
互信息度量两个随机变量之间的相互依赖程度，即知道一个变量后另一个变量的不确定性减少量。

**数学公式**：
```
I(X; Y) = H(X) - H(X|Y)
        = H(Y) - H(Y|X)
        = H(X) + H(Y) - H(X, Y)
        = ΣΣ P(x, y) log₂ [P(x, y) / (P(x)P(y))]
```

**性质**：
- I(X; Y) ≥ 0（非负性）
- I(X; Y) = I(Y; X)（对称性）
- I(X; Y) ≤ min(H(X), H(Y))（上界）
- I(X; Y) = 0 当且仅当 X 和 Y 独立

**在Schema转换中的应用**：
```python
def calculate_mutual_information(source_schema, target_schema):
    """
    计算源Schema和目标Schema之间的互信息
    用于评估转换质量
    """
    h_source = calculate_schema_entropy(source_schema)
    h_target = calculate_schema_entropy(target_schema)
    
    # 计算条件熵
    h_target_given_source = calculate_conditional_entropy(source_schema, target_schema)
    
    # 互信息 I(Source; Target)
    mutual_info = h_target - h_target_given_source
    
    return mutual_info


def evaluate_transformation_quality(source, target, mapping):
    """
    评估Schema转换质量
    
    返回质量评分 (0-1)，越接近1表示转换质量越好
    """
    h_source = calculate_schema_entropy(source)
    mutual_info = calculate_mutual_information(source, target)
    
    # 归一化互信息
    if h_source > 0:
        quality = mutual_info / h_source
    else:
        quality = 1.0
    
    return quality
```

---

### 4. 相对熵 (Kullback-Leibler Divergence)

**定义**：
相对熵度量两个概率分布之间的差异，也称为KL散度。

**数学公式**：
```
D_KL(P || Q) = Σ P(x) log₂ [P(x) / Q(x)]

其中：
- P: 真实分布
- Q: 近似分布
```

**性质**：
- D_KL(P || Q) ≥ 0（非负性）
- D_KL(P || Q) = 0 当且仅当 P = Q
- 不对称：D_KL(P || Q) ≠ D_KL(Q || P)

**在Schema转换中的应用**：
```python
def calculate_kl_divergence(source_distribution, target_distribution):
    """
    计算Schema转换前后的分布差异
    用于量化转换带来的信息损失
    """
    kl_div = 0
    for x in source_distribution.support():
        p = source_distribution.prob(x)
        q = target_distribution.prob(x)
        if p > 0 and q > 0:
            kl_div += p * math.log2(p / q)
    
    return kl_div


def calculate_information_loss(source_schema, target_schema):
    """
    计算Schema转换的信息损失
    """
    # 获取类型分布
    source_dist = get_type_distribution(source_schema)
    target_dist = get_type_distribution(target_schema)
    
    # 计算KL散度作为信息损失
    info_loss = calculate_kl_divergence(source_dist, target_dist)
    
    return info_loss
```

---

### 5. 信道容量 (Channel Capacity)

**定义**：
信道容量是信息可以通过信道传输的最大速率，同时保持任意低的错误概率。

**数学公式**：
```
C = max_{P(X)} I(X; Y)

其中：
- C: 信道容量（比特/符号）
- I(X; Y): 输入X和输出Y之间的互信息
- max: 对所有可能的输入分布取最大值
```

**香农-哈特利定理**（对于高斯信道）：
```
C = B log₂(1 + S/N)

其中：
- B: 信道带宽 (Hz)
- S/N: 信噪比
```

**在Schema转换中的应用**：
```python
def calculate_schema_channel_capacity(source_schema, target_schema, noise_model):
    """
    计算Schema转换信道的容量
    
    用于评估转换系统的最大 throughput
    """
    # 计算在不同输入分布下的互信息
    max_mutual_info = 0
    
    for input_distribution in generate_possible_distributions(source_schema):
        output_distribution = apply_channel(input_distribution, noise_model)
        mutual_info = calculate_mutual_info(input_distribution, output_distribution)
        
        if mutual_info > max_mutual_info:
            max_mutual_info = mutual_info
    
    return max_mutual_info
```

---

## 信息论在Schema转换中的应用

### 应用1: 转换质量评估

```
信息损失 = H(Source) - I(Source; Target)

解释:
- H(Source): 源Schema的信息量
- I(Source; Target): 源和目标之间的互信息
- 信息损失越小，转换质量越高
```

### 应用2: 最优编码设计

```
目标: 找到编码方案 E，使得
- H(E(Source)) 最小化（压缩）
- I(Source; D(E(Source))) 最大化（保真）

其中 D 是解码函数
```

### 应用3: 压缩与简化

```python
def optimal_schema_compression(schema, target_entropy):
    """
    在给定目标熵的条件下，找到最优的Schema压缩方案
    """
    current_entropy = calculate_schema_entropy(schema)
    
    while current_entropy > target_entropy:
        # 找到可以合并的最相似属性
        attr1, attr2 = find_most_similar_attributes(schema)
        
        # 合并属性
        schema = merge_attributes(schema, attr1, attr2)
        
        current_entropy = calculate_schema_entropy(schema)
    
    return schema
```

---

## 七维信息熵模型

在DSL Schema转换中，我们扩展了传统的信息熵概念，提出七维信息熵模型：

### 维度定义

| 维度 | 符号 | 描述 | 计算公式 |
|------|------|------|----------|
| **结构熵** | H_s | Schema结构复杂度 | H_s = -Σ P(struct) log₂ P(struct) |
| **语义熵** | H_m | 语义丰富度 | H_m = -Σ P(sem) log₂ P(sem) |
| **约束熵** | H_c | 约束复杂度 | H_c = -Σ P(constraint) log₂ P(constraint) |
| **关系熵** | H_r | 关系复杂度 | H_r = -Σ P(relation) log₂ P(relation) |
| **演化熵** | H_e | 版本变化率 | H_e = -Σ P(change) log₂ P(change) |
| **应用熵** | H_a | 应用场景多样性 | H_a = -Σ P(app) log₂ P(app) |
| **质量熵** | H_q | 质量不确定性 | H_q = -Σ P(quality) log₂ P(quality) |

### 综合信息熵

```
H_total(Schema) = α·H_s + β·H_m + γ·H_c + δ·H_r + ε·H_e + ζ·H_a + η·H_q

其中 α, β, γ, δ, ε, ζ, η 是权重系数，满足 Σ = 1
```

---

## 形式化定理

### 定理1: 信息守恒定理

**陈述**：
在理想的无损Schema转换中，信息是守恒的。

**形式化**：
```
设 T: Schema₁ → Schema₂ 是一个转换函数

如果 T 是无损的，则：
    H(Schema₁) = H(Schema₂)
    
等价地：
    I(Schema₁; Schema₂) = H(Schema₁) = H(Schema₂)
```

**证明**：
```
由互信息定义：
    I(Schema₁; Schema₂) = H(Schema₁) - H(Schema₁|Schema₂)

无损转换意味着：
    H(Schema₁|Schema₂) = 0
    
因此：
    I(Schema₁; Schema₂) = H(Schema₁)
    
同理：
    I(Schema₁; Schema₂) = H(Schema₂)
    
所以：
    H(Schema₁) = H(Schema₂)
```

### 定理2: 信息损失下界定理

**陈述**：
任何有损Schema转换的信息损失都有一个下界。

**形式化**：
```
设 T: Schema₁ → Schema₂ 是一个有损转换

则信息损失 L 满足：
    L = H(Schema₁) - I(Schema₁; Schema₂) ≥ 0
    
且当且仅当转换是可逆的时，L = 0
```

### 定理3: 压缩极限定理

**陈述**：
Schema的无损压缩有一个理论极限。

**形式化**：
```
设 C(Schema) 是Schema的压缩表示

则：
    H(C(Schema)) ≥ H(Schema)
    
且存在一个编码方案 E，使得：
    |E(Schema)| → H(Schema) (当编码长度趋于无穷时)
```

---

## 实践工具

### Python信息论库

```python
# 使用 scipy 计算信息论度量
from scipy.stats import entropy
import numpy as np

# 计算熵
def compute_entropy(prob_distribution):
    """计算概率分布的熵"""
    return entropy(prob_distribution, base=2)

# 计算互信息
def compute_mutual_info(joint_dist, marginal_x, marginal_y):
    """计算互信息"""
    mi = 0
    for i, p_x in enumerate(marginal_x):
        for j, p_y in enumerate(marginal_y):
            if joint_dist[i, j] > 0:
                mi += joint_dist[i, j] * np.log2(
                    joint_dist[i, j] / (p_x * p_y)
                )
    return mi

# 使用 sklearn 的特征选择
from sklearn.feature_selection import mutual_info_classif

# 计算特征与目标变量的互信息
mi_scores = mutual_info_classif(X, y, random_state=42)
```

---

## 参考文献

1. Shannon, C. E. (1948). A Mathematical Theory of Communication. Bell System Technical Journal.
2. Cover, T. M., & Thomas, J. A. (2006). Elements of Information Theory. Wiley.
3. MacKay, D. J. (2003). Information Theory, Inference, and Learning Algorithms. Cambridge University Press.

---

**创建时间**: 2026-02-17  
**最后更新**: 2026-02-17  
**维护者**: DSL Schema研究团队
