"""
树形模型与AI/ML集成实现
Tree Models AI/ML Integration Implementation

本模块提供：
1. 决策树到Schema的转换
2. 树形神经网络实现
3. 可视化代码
4. 性能对比分析

作者: AI Assistant
版本: 1.0.0
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
from collections import defaultdict

# 尝试导入可选依赖
try:
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.datasets import make_classification, make_regression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. Some features will be limited.")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Neural tree features will be limited.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


# =============================================================================
# 1. 决策树Schema表示
# =============================================================================

class NodeType(Enum):
    """节点类型枚举"""
    ROOT = "root"
    DECISION = "decision"
    LEAF = "leaf"
    BRANCH = "branch"


@dataclass
class TreeNodeSchema:
    """
    树节点Schema定义
    
    用于统一表示决策树节点的结构
    """
    node_id: int
    node_type: NodeType
    feature: Optional[str] = None
    threshold: Optional[float] = None
    operator: Optional[str] = None  # '<=', '>', '==', etc.
    value: Optional[Any] = None  # 叶子节点的值
    class_distribution: Optional[Dict[str, float]] = None
    samples: int = 0
    impurity: float = 0.0
    children: List['TreeNodeSchema'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "feature": self.feature,
            "threshold": self.threshold,
            "operator": self.operator,
            "value": self.value,
            "class_distribution": self.class_distribution,
            "samples": self.samples,
            "impurity": self.impurity,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeNodeSchema':
        """从字典创建节点"""
        children = [cls.from_dict(child) for child in data.get("children", [])]
        return cls(
            node_id=data["node_id"],
            node_type=NodeType(data["node_type"]),
            feature=data.get("feature"),
            threshold=data.get("threshold"),
            operator=data.get("operator"),
            value=data.get("value"),
            class_distribution=data.get("class_distribution"),
            samples=data.get("samples", 0),
            impurity=data.get("impurity", 0.0),
            children=children,
            metadata=data.get("metadata", {})
        )


@dataclass
class DecisionTreeSchema:
    """
    决策树Schema容器
    
    包含完整的决策树结构和元数据
    """
    tree_id: str
    tree_type: str  # 'classifier', 'regressor'
    root: TreeNodeSchema
    feature_names: List[str]
    target_names: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "tree_id": self.tree_id,
            "tree_type": self.tree_type,
            "root": self.root.to_dict(),
            "feature_names": self.feature_names,
            "target_names": self.target_names,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DecisionTreeSchema':
        """从JSON字符串创建"""
        data = json.loads(json_str)
        return cls(
            tree_id=data["tree_id"],
            tree_type=data["tree_type"],
            root=TreeNodeSchema.from_dict(data["root"]),
            feature_names=data["feature_names"],
            target_names=data.get("target_names"),
            metadata=data.get("metadata", {})
        )


# =============================================================================
# 2. 决策树到Schema的转换器
# =============================================================================

class SklearnTreeConverter:
    """
    scikit-learn决策树到Schema的转换器
    """
    
    def __init__(self, model, feature_names: Optional[List[str]] = None,
                 target_names: Optional[List[str]] = None):
        """
        初始化转换器
        
        Args:
            model: sklearn决策树模型
            feature_names: 特征名称列表
            target_names: 目标类别名称列表
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for this converter")
        
        self.model = model
        self.feature_names = feature_names or []
        self.target_names = target_names
        self.tree_ = model.tree_
        
        # 自动生成特征名
        if not self.feature_names:
            n_features = self.tree_.n_features
            self.feature_names = [f"feature_{i}" for i in range(n_features)]
    
    def convert(self, tree_id: str = "tree_0") -> DecisionTreeSchema:
        """
        转换决策树为Schema
        
        Returns:
            DecisionTreeSchema对象
        """
        tree_type = 'classifier' if hasattr(self.model, 'classes_') else 'regressor'
        
        # 递归构建树结构
        root = self._build_node(0, NodeType.ROOT)
        
        return DecisionTreeSchema(
            tree_id=tree_id,
            tree_type=tree_type,
            root=root,
            feature_names=self.feature_names,
            target_names=self.target_names,
            metadata={
                "max_depth": self.model.get_params().get('max_depth'),
                "n_leaves": self.tree_.n_leaves,
                "n_nodes": self.tree_.node_count
            }
        )
    
    def _build_node(self, node_id: int, node_type: NodeType) -> TreeNodeSchema:
        """递归构建节点"""
        tree = self.tree_
        
        # 判断是否为叶子节点
        if tree.children_left[node_id] == tree.children_right[node_id]:
            # 叶子节点
            value = tree.value[node_id]
            
            if self.target_names and len(value.shape) > 1:
                # 分类问题
                class_dist = {
                    self.target_names[i]: float(value[0][i] / value[0].sum())
                    for i in range(len(self.target_names))
                }
                predicted_class = self.target_names[np.argmax(value[0])]
            else:
                # 回归问题
                class_dist = None
                predicted_class = float(value[0][0]) if len(value.shape) > 1 else float(value[0])
            
            return TreeNodeSchema(
                node_id=node_id,
                node_type=NodeType.LEAF,
                value=predicted_class,
                class_distribution=class_dist,
                samples=int(tree.n_node_samples[node_id]),
                impurity=float(tree.impurity[node_id])
            )
        
        # 决策节点
        feature_idx = tree.feature[node_id]
        threshold = float(tree.threshold[node_id])
        
        node = TreeNodeSchema(
            node_id=node_id,
            node_type=node_type,
            feature=self.feature_names[feature_idx],
            threshold=threshold,
            operator="<=",
            samples=int(tree.n_node_samples[node_id]),
            impurity=float(tree.impurity[node_id])
        )
        
        # 递归构建子节点
        left_child = self._build_node(
            tree.children_left[node_id], 
            NodeType.BRANCH
        )
        right_child = self._build_node(
            tree.children_right[node_id],
            NodeType.BRANCH
        )
        
        node.children = [left_child, right_child]
        return node
    
    def export_rules(self) -> List[str]:
        """
        导出决策规则列表
        
        Returns:
            决策规则字符串列表
        """
        rules = []
        self._extract_rules(0, [], rules)
        return rules
    
    def _extract_rules(self, node_id: int, conditions: List[str], 
                       rules: List[str]) -> None:
        """递归提取规则"""
        tree = self.tree_
        
        if tree.children_left[node_id] == tree.children_right[node_id]:
            # 叶子节点
            value = tree.value[node_id]
            if len(value.shape) > 1 and value.shape[1] > 1:
                prediction = np.argmax(value[0])
                rule = f"IF {' AND '.join(conditions)} THEN class={prediction}"
            else:
                prediction = value[0][0]
                rule = f"IF {' AND '.join(conditions)} THEN value={prediction:.4f}"
            rules.append(rule)
            return
        
        # 决策节点
        feature_idx = tree.feature[node_id]
        threshold = tree.threshold[node_id]
        feature_name = self.feature_names[feature_idx]
        
        # 左分支 (<= threshold)
        left_condition = f"{feature_name} <= {threshold:.4f}"
        self._extract_rules(
            tree.children_left[node_id], 
            conditions + [left_condition], 
            rules
        )
        
        # 右分支 (> threshold)
        right_condition = f"{feature_name} > {threshold:.4f}"
        self._extract_rules(
            tree.children_right[node_id],
            conditions + [right_condition],
            rules
        )


# =============================================================================
# 3. 树形神经网络实现
# =============================================================================

if TORCH_AVAILABLE:
    class NeuralDecisionNode(nn.Module):
        """
        神经决策节点
        
        使用神经网络实现可微分的决策节点
        """
        def __init__(self, input_dim: int, hidden_dim: int = 64):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim, 1),
                nn.Sigmoid()
            )
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """
            前向传播
            
            Args:
                x: 输入特征 [batch_size, input_dim]
            
            Returns:
                决策概率 [batch_size, 1]
            """
            return self.network(x)
    
    
    class NeuralLeafNode(nn.Module):
        """
        神经叶子节点
        
        使用神经网络实现叶子节点的输出
        """
        def __init__(self, input_dim: int, output_dim: int, hidden_dim: int = 32):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """
            前向传播
            
            Args:
                x: 输入特征 [batch_size, input_dim]
            
            Returns:
                输出 logits [batch_size, output_dim]
            """
            return self.network(x)
    
    
    class SoftDecisionTree(nn.Module):
        """
        软决策树（可微分决策树）
        
        使用软决策边界实现端到端可训练的决策树
        """
        def __init__(self, input_dim: int, output_dim: int, 
                     depth: int = 3, hidden_dim: int = 64):
            """
            初始化软决策树
            
            Args:
                input_dim: 输入特征维度
                output_dim: 输出类别数
                depth: 树的深度
                hidden_dim: 隐藏层维度
            """
            super().__init__()
            self.input_dim = input_dim
            self.output_dim = output_dim
            self.depth = depth
            self.n_nodes = 2 ** depth - 1
            self.n_leaves = 2 ** depth
            
            # 决策节点
            self.decision_nodes = nn.ModuleList([
                NeuralDecisionNode(input_dim, hidden_dim)
                for _ in range(self.n_nodes)
            ])
            
            # 叶子节点
            self.leaf_nodes = nn.ModuleList([
                NeuralLeafNode(input_dim, output_dim, hidden_dim)
                for _ in range(self.n_leaves)
            ])
            
            # 叶子节点概率分布（可学习）
            self.leaf_probs = nn.Parameter(torch.randn(self.n_leaves, output_dim))
        
        def forward(self, x: torch.Tensor, return_path_probs: bool = False) -> Union[
            torch.Tensor, Tuple[torch.Tensor, torch.Tensor]
        ]:
            """
            前向传播
            
            Args:
                x: 输入特征 [batch_size, input_dim]
                return_path_probs: 是否返回路径概率
            
            Returns:
                输出 logits [batch_size, output_dim]
                如果return_path_probs为True，还返回路径概率
            """
            batch_size = x.size(0)
            
            # 计算所有决策节点的概率
            decisions = torch.stack([
                node(x).squeeze(-1) for node in self.decision_nodes
            ], dim=1)  # [batch_size, n_nodes]
            
            # 计算路径概率
            path_probs = torch.ones(batch_size, self.n_leaves, device=x.device)
            
            for leaf_idx in range(self.n_leaves):
                # 计算到达每个叶子的路径
                node_idx = 0
                path_prob = torch.ones(batch_size, device=x.device)
                
                for d in range(self.depth):
                    # 判断当前层是左分支还是右分支
                    bit = (leaf_idx >> (self.depth - 1 - d)) & 1
                    
                    if bit == 0:
                        # 左分支: 使用 (1 - decision_prob)
                        path_prob = path_prob * (1 - decisions[:, node_idx])
                    else:
                        # 右分支: 使用 decision_prob
                        path_prob = path_prob * decisions[:, node_idx]
                    
                    # 移动到下一层节点
                    node_idx = 2 * node_idx + 1 + bit
                
                path_probs[:, leaf_idx] = path_prob
            
            # 计算叶子输出
            leaf_outputs = torch.stack([
                node(x) for node in self.leaf_nodes
            ], dim=1)  # [batch_size, n_leaves, output_dim]
            
            # 加权聚合
            path_probs = path_probs.unsqueeze(-1)  # [batch_size, n_leaves, 1]
            output = (path_probs * leaf_outputs).sum(dim=1)  # [batch_size, output_dim]
            
            if return_path_probs:
                return output, path_probs.squeeze(-1)
            return output
        
        def get_feature_importance(self) -> np.ndarray:
            """
            获取特征重要性（基于决策节点权重的近似）
            
            Returns:
                特征重要性数组
            """
            importances = np.zeros(self.input_dim)
            
            for node in self.decision_nodes:
                # 获取第一层权重绝对值作为特征重要性指标
                weights = node.network[0].weight.abs().mean(dim=0)
                weights = weights.detach().cpu().numpy()
                importances += weights
            
            # 归一化
            if importances.sum() > 0:
                importances /= importances.sum()
            
            return importances
    
    
    class TreeEnsembleNetwork(nn.Module):
        """
        树形集成神经网络
        
        结合多个软决策树的集成模型
        """
        def __init__(self, input_dim: int, output_dim: int,
                     n_trees: int = 5, tree_depth: int = 3,
                     hidden_dim: int = 64):
            """
            初始化
            
            Args:
                input_dim: 输入特征维度
                output_dim: 输出维度
                n_trees: 树的数量
                tree_depth: 每棵树的深度
                hidden_dim: 隐藏层维度
            """
            super().__init__()
            self.n_trees = n_trees
            
            # 特征提取器
            self.feature_extractor = nn.Sequential(
                nn.Linear(input_dim, hidden_dim * 2),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim * 2),
                nn.Dropout(0.2),
                nn.Linear(hidden_dim * 2, hidden_dim),
                nn.ReLU()
            )
            
            # 树集合
            self.trees = nn.ModuleList([
                SoftDecisionTree(hidden_dim, output_dim, tree_depth, hidden_dim // 2)
                for _ in range(n_trees)
            ])
            
            # 树权重（可学习）
            self.tree_weights = nn.Parameter(torch.ones(n_trees) / n_trees)
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """
            前向传播
            
            Args:
                x: 输入特征
            
            Returns:
                输出 logits
            """
            # 特征提取
            features = self.feature_extractor(x)
            
            # 每棵树的输出
            tree_outputs = torch.stack([
                tree(features) for tree in self.trees
            ], dim=0)  # [n_trees, batch_size, output_dim]
            
            # 加权聚合
            weights = torch.softmax(self.tree_weights, dim=0)
            output = (weights.view(-1, 1, 1) * tree_outputs).sum(dim=0)
            
            return output
        
        def get_tree_outputs(self, x: torch.Tensor) -> torch.Tensor:
            """获取每棵树的单独输出"""
            features = self.feature_extractor(x)
            return torch.stack([tree(features) for tree in self.trees])


# =============================================================================
# 4. 可视化工具
# =============================================================================

class TreeVisualizer:
    """
    树形模型可视化工具
    """
    
    @staticmethod
    def plot_decision_tree_schema(schema: DecisionTreeSchema, 
                                   figsize: Tuple[int, int] = (16, 10),
                                   save_path: Optional[str] = None) -> None:
        """
        绘制决策树Schema
        
        Args:
            schema: 决策树Schema
            figsize: 图像大小
            save_path: 保存路径
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for visualization")
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        ax.set_title(f"Decision Tree: {schema.tree_id}", fontsize=16, fontweight='bold')
        
        # 计算树的最大深度
        max_depth = TreeVisualizer._get_max_depth(schema.root)
        
        # 递归绘制节点
        TreeVisualizer._draw_node(ax, schema.root, 50, 95, 45, 15, max_depth, 0)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def _get_max_depth(node: TreeNodeSchema) -> int:
        """获取树的最大深度"""
        if not node.children:
            return 0
        return 1 + max(TreeVisualizer._get_max_depth(child) for child in node.children)
    
    @staticmethod
    def _draw_node(ax, node: TreeNodeSchema, x: float, y: float,
                   width: float, height: float, max_depth: int, depth: int) -> None:
        """递归绘制节点"""
        
        # 节点颜色
        if node.node_type == NodeType.LEAF:
            color = '#90EE90'  # 浅绿色
            box_style = "round,pad=0.3"
        else:
            color = '#87CEEB'  # 天蓝色
            box_style = "round,pad=0.3"
        
        # 节点文本
        if node.node_type == NodeType.LEAF:
            if isinstance(node.value, (int, float)):
                text = f"Value: {node.value:.3f}\nSamples: {node.samples}"
            else:
                text = f"Class: {node.value}\nSamples: {node.samples}"
        else:
            text = f"{node.feature}\n{node.operator} {node.threshold:.3f}\nSamples: {node.samples}"
        
        # 绘制节点框
        bbox = dict(boxstyle=box_style, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.text(x, y, text, ha='center', va='center', fontsize=9,
                bbox=bbox, fontweight='bold')
        
        # 递归绘制子节点
        if node.children:
            new_width = width * 0.5
            new_y = y - height
            
            for i, child in enumerate(node.children):
                offset = new_width * (0.5 if i == 0 else -0.5)
                new_x = x + offset
                
                # 绘制连接线
                ax.plot([x, new_x], [y - 3, new_y + 3], 
                       'k-', linewidth=1.5, alpha=0.6)
                
                # 添加分支标签
                label = "Yes" if i == 0 else "No"
                mid_x, mid_y = (x + new_x) / 2, (y + new_y) / 2
                ax.text(mid_x, mid_y, label, fontsize=8, 
                       ha='center', va='center',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                
                TreeVisualizer._draw_node(ax, child, new_x, new_y, 
                                         new_width, height, max_depth, depth + 1)
    
    @staticmethod
    def plot_feature_importance(importance_dict: Dict[str, float],
                                 title: str = "Feature Importance",
                                 figsize: Tuple[int, int] = (10, 6),
                                 save_path: Optional[str] = None) -> None:
        """
        绘制特征重要性
        
        Args:
            importance_dict: 特征重要性字典
            title: 图表标题
            figsize: 图像大小
            save_path: 保存路径
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required")
        
        features = list(importance_dict.keys())
        values = list(importance_dict.values())
        
        # 排序
        sorted_idx = np.argsort(values)
        features = [features[i] for i in sorted_idx]
        values = [values[i] for i in sorted_idx]
        
        fig, ax = plt.subplots(figsize=figsize)
        colors = plt.cm.viridis(np.linspace(0, 1, len(features)))
        bars = ax.barh(features, values, color=colors)
        
        ax.set_xlabel('Importance', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlim(0, max(values) * 1.1)
        
        # 添加数值标签
        for bar, val in zip(bars, values):
            ax.text(val + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{val:.3f}', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_tree_comparison(results: Dict[str, Dict[str, float]],
                              metrics: List[str] = ['accuracy', 'training_time'],
                              figsize: Tuple[int, int] = (12, 5),
                              save_path: Optional[str] = None) -> None:
        """
        绘制模型对比图
        
        Args:
            results: 模型结果字典
            metrics: 要对比的指标
            figsize: 图像大小
            save_path: 保存路径
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required")
        
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=figsize)
        
        if n_metrics == 1:
            axes = [axes]
        
        models = list(results.keys())
        x_pos = np.arange(len(models))
        
        for idx, metric in enumerate(metrics):
            values = [results[model].get(metric, 0) for model in models]
            
            colors = plt.cm.Set2(np.linspace(0, 1, len(models)))
            bars = axes[idx].bar(x_pos, values, color=colors, alpha=0.8, edgecolor='black')
            
            axes[idx].set_xlabel('Model', fontsize=11)
            axes[idx].set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
            axes[idx].set_title(f'{metric.replace("_", " ").title()} Comparison', 
                               fontsize=12, fontweight='bold')
            axes[idx].set_xticks(x_pos)
            axes[idx].set_xticklabels(models, rotation=15, ha='right')
            axes[idx].grid(axis='y', alpha=0.3)
            
            # 添加数值标签
            for bar, val in zip(bars, values):
                axes[idx].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                              f'{val:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()


# =============================================================================
# 5. 性能评估与对比
# =============================================================================

class ModelBenchmark:
    """
    模型性能评估工具
    """
    
    def __init__(self, X_train: np.ndarray, X_test: np.ndarray,
                 y_train: np.ndarray, y_test: np.ndarray,
                 task_type: str = 'classification'):
        """
        初始化
        
        Args:
            X_train: 训练特征
            X_test: 测试特征
            y_train: 训练标签
            y_test: 测试标签
            task_type: 任务类型 ('classification' 或 'regression')
        """
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.task_type = task_type
        self.results = {}
    
    def benchmark_sklearn_models(self) -> Dict[str, Dict[str, float]]:
        """
        评估scikit-learn模型
        
        Returns:
            结果字典
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required")
        
        import time
        
        models = {}
        
        if self.task_type == 'classification':
            models = {
                'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
                'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
            }
        
        for name, model in models.items():
            print(f"Training {name}...")
            
            start_time = time.time()
            model.fit(self.X_train, self.y_train)
            train_time = time.time() - start_time
            
            start_time = time.time()
            y_pred = model.predict(self.X_test)
            predict_time = time.time() - start_time
            
            if self.task_type == 'classification':
                score = accuracy_score(self.y_test, y_pred)
                metric_name = 'accuracy'
            else:
                score = -mean_squared_error(self.y_test, y_pred)
                metric_name = 'neg_mse'
            
            self.results[name] = {
                metric_name: score,
                'training_time': train_time,
                'prediction_time': predict_time
            }
            
            print(f"  {metric_name}: {score:.4f}, Training time: {train_time:.3f}s")
        
        return self.results
    
    def benchmark_neural_tree(self, epochs: int = 50, 
                               batch_size: int = 32) -> Dict[str, float]:
        """
        评估神经决策树
        
        Args:
            epochs: 训练轮数
            batch_size: 批次大小
        
        Returns:
            结果字典
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required")
        
        import time
        
        input_dim = self.X_train.shape[1]
        output_dim = len(np.unique(self.y_train))
        
        # 转换为PyTorch张量
        X_train_tensor = torch.FloatTensor(self.X_train)
        y_train_tensor = torch.LongTensor(self.y_train)
        X_test_tensor = torch.FloatTensor(self.X_test)
        y_test_tensor = torch.LongTensor(self.y_test)
        
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # 创建模型
        model = SoftDecisionTree(input_dim, output_dim, depth=3, hidden_dim=64)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        print("Training Neural Decision Tree...")
        
        start_time = time.time()
        model.train()
        
        for epoch in range(epochs):
            total_loss = 0
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}")
        
        train_time = time.time() - start_time
        
        # 评估
        model.eval()
        with torch.no_grad():
            outputs = model(X_test_tensor)
            _, predicted = torch.max(outputs, 1)
            accuracy = (predicted == y_test_tensor).float().mean().item()
        
        self.results['Neural Decision Tree'] = {
            'accuracy': accuracy,
            'training_time': train_time
        }
        
        print(f"  accuracy: {accuracy:.4f}, Training time: {train_time:.3f}s")
        
        return self.results['Neural Decision Tree']
    
    def get_results(self) -> Dict[str, Dict[str, float]]:
        """获取所有结果"""
        return self.results
    
    def print_summary(self) -> None:
        """打印结果摘要"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        for model_name, metrics in self.results.items():
            print(f"\n{model_name}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.4f}")


# =============================================================================
# 6. 演示和测试
# =============================================================================

def demo_decision_tree_conversion():
    """
    演示决策树到Schema的转换
    """
    print("="*60)
    print("DEMO: Decision Tree to Schema Conversion")
    print("="*60)
    
    if not SKLEARN_AVAILABLE:
        print("scikit-learn not available, skipping demo")
        return
    
    # 生成示例数据
    X, y = make_classification(
        n_samples=1000, 
        n_features=4, 
        n_informative=3,
        n_redundant=1,
        n_classes=3,
        random_state=42
    )
    
    feature_names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    target_names = ['setosa', 'versicolor', 'virginica']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 训练决策树
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X_train, y_train)
    
    print(f"\nTrained Decision Tree (depth=3)")
    print(f"Training accuracy: {clf.score(X_train, y_train):.4f}")
    print(f"Test accuracy: {clf.score(X_test, y_test):.4f}")
    
    # 转换为Schema
    converter = SklearnTreeConverter(clf, feature_names, target_names)
    schema = converter.convert(tree_id="iris_decision_tree")
    
    print("\n--- Schema JSON Representation (truncated) ---")
    schema_dict = schema.to_dict()
    print(json.dumps(schema_dict, indent=2)[:1500] + "...")
    
    print("\n--- Decision Rules ---")
    rules = converter.export_rules()
    for i, rule in enumerate(rules[:5], 1):
        print(f"{i}. {rule}")
    
    # 可视化
    if MATPLOTLIB_AVAILABLE:
        print("\nGenerating visualization...")
        TreeVisualizer.plot_decision_tree_schema(schema, figsize=(16, 10))
        
        # 特征重要性
        importance = dict(zip(feature_names, clf.feature_importances_))
        TreeVisualizer.plot_feature_importance(
            importance, 
            title="Decision Tree Feature Importance"
        )
    
    return schema


def demo_neural_tree():
    """
    演示神经决策树
    """
    print("\n" + "="*60)
    print("DEMO: Neural Decision Tree")
    print("="*60)
    
    if not TORCH_AVAILABLE or not SKLEARN_AVAILABLE:
        print("PyTorch or scikit-learn not available, skipping demo")
        return
    
    # 生成数据
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=5,
        n_redundant=2,
        n_classes=3,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 转换为张量
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.LongTensor(y_train)
    X_test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.LongTensor(y_test)
    
    # 创建模型
    input_dim = X.shape[1]
    output_dim = len(np.unique(y))
    
    model = SoftDecisionTree(input_dim, output_dim, depth=3, hidden_dim=64)
    
    print(f"\nNeural Decision Tree Architecture:")
    print(f"  Input dim: {input_dim}")
    print(f"  Output dim: {output_dim}")
    print(f"  Tree depth: 3")
    print(f"  Number of decision nodes: {model.n_nodes}")
    print(f"  Number of leaf nodes: {model.n_leaves}")
    
    # 训练
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    
    print("\nTraining...")
    for epoch in range(30):
        model.train()
        total_loss = 0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            model.eval()
            with torch.no_grad():
                train_outputs = model(X_train_tensor)
                _, train_pred = torch.max(train_outputs, 1)
                train_acc = (train_pred == y_train_tensor).float().mean().item()
                
                test_outputs = model(X_test_tensor)
                _, test_pred = torch.max(test_outputs, 1)
                test_acc = (test_pred == y_test_tensor).float().mean().item()
            
            print(f"  Epoch {epoch+1}: Loss={total_loss/len(train_loader):.4f}, "
                  f"Train Acc={train_acc:.4f}, Test Acc={test_acc:.4f}")
    
    # 特征重要性
    importance = model.get_feature_importance()
    importance_dict = {f"feature_{i}": imp for i, imp in enumerate(importance)}
    
    print("\n--- Feature Importance (from Neural Tree) ---")
    for feat, imp in sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {feat}: {imp:.4f}")
    
    if MATPLOTLIB_AVAILABLE:
        TreeVisualizer.plot_feature_importance(
            importance_dict,
            title="Neural Decision Tree Feature Importance"
        )


def demo_benchmark():
    """
    演示性能对比
    """
    print("\n" + "="*60)
    print("DEMO: Model Benchmark")
    print("="*60)
    
    if not SKLEARN_AVAILABLE:
        print("scikit-learn not available, skipping demo")
        return
    
    # 生成数据
    X, y = make_classification(
        n_samples=2000,
        n_features=20,
        n_informative=10,
        n_redundant=5,
        n_classes=3,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 运行基准测试
    benchmark = ModelBenchmark(X_train, X_test, y_train, y_test)
    benchmark.benchmark_sklearn_models()
    
    if TORCH_AVAILABLE:
        benchmark.benchmark_neural_tree(epochs=30)
    
    benchmark.print_summary()
    
    # 可视化对比
    if MATPLOTLIB_AVAILABLE:
        TreeVisualizer.plot_tree_comparison(
            benchmark.get_results(),
            metrics=['accuracy', 'training_time'],
            figsize=(14, 5)
        )


def main():
    """
    主函数 - 运行所有演示
    """
    print("\n" + "#"*60)
    print("# Tree Models AI/ML Integration Demo")
    print("#"*60)
    
    # 1. 决策树转换演示
    demo_decision_tree_conversion()
    
    # 2. 神经决策树演示
    demo_neural_tree()
    
    # 3. 性能对比演示
    demo_benchmark()
    
    print("\n" + "#"*60)
    print("# All demos completed!")
    print("#"*60)


if __name__ == "__main__":
    main()
