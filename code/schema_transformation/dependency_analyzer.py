"""
依赖分析模块 (Dependency Analyzer Module)

该模块提供Schema依赖分析功能，构建依赖图并分析字段之间的关系，
支持循环依赖检测、影响分析和关键路径识别。

核心功能：
- 依赖图构建
- 循环依赖检测
- 影响范围分析
- 关键路径识别
- 拓扑排序
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
import json


class DependencyType(Enum):
    """依赖类型枚举"""
    DIRECT = auto()          # 直接依赖
    INDIRECT = auto()        # 间接依赖
    REFERENCE = auto()       # 引用依赖
    COMPOSITION = auto()     # 组合依赖
    INHERITANCE = auto()     # 继承依赖
    CONSTRAINT = auto()      # 约束依赖
    VALIDATION = auto()      # 验证依赖


@dataclass
class DependencyNode:
    """
    依赖图节点
    
    Attributes:
        path: 字段路径
        schema_type: Schema类型
        dependencies: 依赖的路径集合
        dependents: 被依赖的路径集合
        metadata: 节点元数据
    """
    path: str
    schema_type: str = "unknown"
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_dependency(self, path: str, dep_type: DependencyType = DependencyType.DIRECT) -> None:
        """添加依赖"""
        self.dependencies.add(path)
    
    def add_dependent(self, path: str) -> None:
        """添加被依赖关系"""
        self.dependents.add(path)
    
    def remove_dependency(self, path: str) -> None:
        """移除依赖"""
        self.dependencies.discard(path)
    
    def remove_dependent(self, path: str) -> None:
        """移除被依赖关系"""
        self.dependents.discard(path)
    
    @property
    def in_degree(self) -> int:
        """入度（依赖数）"""
        return len(self.dependencies)
    
    @property
    def out_degree(self) -> int:
        """出度（被依赖数）"""
        return len(self.dependents)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "path": self.path,
            "schema_type": self.schema_type,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "metadata": self.metadata
        }


@dataclass
class DependencyGraph:
    """
    依赖图
    
    管理Schema中所有字段的依赖关系
    
    Attributes:
        nodes: 节点字典，键为路径
        edges: 边列表
    """
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: List[Tuple[str, str, DependencyType]] = field(default_factory=list)
    
    def add_node(self, path: str, schema_type: str = "unknown", metadata: Optional[Dict] = None) -> DependencyNode:
        """添加节点"""
        if path not in self.nodes:
            self.nodes[path] = DependencyNode(
                path=path,
                schema_type=schema_type,
                metadata=metadata or {}
            )
        return self.nodes[path]
    
    def add_edge(
        self,
        from_path: str,
        to_path: str,
        dep_type: DependencyType = DependencyType.DIRECT
    ) -> None:
        """添加边"""
        # 确保节点存在
        if from_path not in self.nodes:
            self.add_node(from_path)
        if to_path not in self.nodes:
            self.add_node(to_path)
        
        # 添加依赖关系
        self.nodes[from_path].add_dependency(to_path, dep_type)
        self.nodes[to_path].add_dependent(from_path)
        self.edges.append((from_path, to_path, dep_type))
    
    def get_node(self, path: str) -> Optional[DependencyNode]:
        """获取节点"""
        return self.nodes.get(path)
    
    def remove_node(self, path: str) -> None:
        """移除节点及其所有关系"""
        if path not in self.nodes:
            return
        
        node = self.nodes[path]
        
        # 移除依赖关系
        for dep in list(node.dependencies):
            if dep in self.nodes:
                self.nodes[dep].remove_dependent(path)
        
        # 移除被依赖关系
        for dep in list(node.dependents):
            if dep in self.nodes:
                self.nodes[dep].remove_dependency(path)
        
        # 移除边
        self.edges = [
            e for e in self.edges
            if e[0] != path and e[1] != path
        ]
        
        # 移除节点
        del self.nodes[path]
    
    def get_all_dependencies(self, path: str, include_indirect: bool = True) -> Set[str]:
        """
        获取所有依赖
        
        Args:
            path: 节点路径
            include_indirect: 是否包含间接依赖
            
        Returns:
            依赖路径集合
        """
        if path not in self.nodes:
            return set()
        
        dependencies = set(self.nodes[path].dependencies)
        
        if include_indirect:
            # BFS遍历间接依赖
            queue = deque(dependencies)
            visited = dependencies.copy()
            
            while queue:
                current = queue.popleft()
                if current in self.nodes:
                    for dep in self.nodes[current].dependencies:
                        if dep not in visited:
                            visited.add(dep)
                            queue.append(dep)
            
            dependencies = visited
        
        return dependencies
    
    def get_all_dependents(self, path: str, include_indirect: bool = True) -> Set[str]:
        """
        获取所有被依赖
        
        Args:
            path: 节点路径
            include_indirect: 是否包含间接被依赖
            
        Returns:
            被依赖路径集合
        """
        if path not in self.nodes:
            return set()
        
        dependents = set(self.nodes[path].dependents)
        
        if include_indirect:
            # BFS遍历间接被依赖
            queue = deque(dependents)
            visited = dependents.copy()
            
            while queue:
                current = queue.popleft()
                if current in self.nodes:
                    for dep in self.nodes[current].dependents:
                        if dep not in visited:
                            visited.add(dep)
                            queue.append(dep)
            
            dependents = visited
        
        return dependents
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [
                {"from": e[0], "to": e[1], "type": e[2].name}
                for e in self.edges
            ]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class DependencyAnalyzer:
    """
    Schema依赖分析器
    
    分析Schema中的字段依赖关系，构建依赖图，并提供各种分析功能。
    
    Attributes:
        graph: 依赖图
        detect_cycles: 是否检测循环依赖
        track_metadata: 是否追踪元数据
    """
    
    def __init__(
        self,
        detect_cycles: bool = True,
        track_metadata: bool = True
    ):
        self.graph = DependencyGraph()
        self.detect_cycles = detect_cycles
        self.track_metadata = track_metadata
        self._reference_keywords = {'$ref', 'ref', 'reference', 'dependsOn'}
    
    def analyze(self, schema: Dict[str, Any], root_path: str = "") -> DependencyGraph:
        """
        分析Schema构建依赖图
        
        Args:
            schema: Schema字典
            root_path: 根路径
            
        Returns:
            依赖图
        """
        self.graph = DependencyGraph()
        self._analyze_recursive(schema, root_path)
        
        if self.detect_cycles:
            cycles = self.find_cycles()
            if cycles:
                # 记录循环依赖信息到元数据
                for cycle in cycles:
                    for path in cycle:
                        node = self.graph.get_node(path)
                        if node:
                            node.metadata["in_cycle"] = True
                            node.metadata["cycle_paths"] = cycle
        
        return self.graph
    
    def _analyze_recursive(
        self,
        schema: Any,
        current_path: str
    ) -> None:
        """递归分析Schema"""
        if isinstance(schema, dict):
            # 添加当前节点
            schema_type = schema.get('type', 'object')
            metadata = {k: v for k, v in schema.items() if k not in ['properties', 'items']}
            
            self.graph.add_node(current_path, schema_type, metadata if self.track_metadata else {})
            
            # 检查引用
            for keyword in self._reference_keywords:
                if keyword in schema:
                    ref_path = schema[keyword]
                    if isinstance(ref_path, str):
                        self.graph.add_edge(
                            current_path,
                            ref_path,
                            DependencyType.REFERENCE
                        )
            
            # 分析属性
            if 'properties' in schema:
                for prop_name, prop_schema in schema['properties'].items():
                    prop_path = f"{current_path}.{prop_name}" if current_path else prop_name
                    self._analyze_recursive(prop_schema, prop_path)
                    # 属性依赖于父对象
                    if current_path:
                        self.graph.add_edge(
                            prop_path,
                            current_path,
                            DependencyType.COMPOSITION
                        )
            
            # 分析数组项
            if 'items' in schema:
                items_path = f"{current_path}[]"
                self._analyze_recursive(schema['items'], items_path)
                if current_path:
                    self.graph.add_edge(
                        items_path,
                        current_path,
                        DependencyType.COMPOSITION
                    )
            
            # 分析allOf, anyOf, oneOf
            for keyword in ['allOf', 'anyOf', 'oneOf']:
                if keyword in schema:
                    for i, sub_schema in enumerate(schema[keyword]):
                        sub_path = f"{current_path}#{keyword}[{i}]"
                        self._analyze_recursive(sub_schema, sub_path)
                        if current_path:
                            self.graph.add_edge(
                                sub_path,
                                current_path,
                                DependencyType.INHERITANCE if keyword == 'allOf' else DependencyType.REFERENCE
                            )
        
        elif isinstance(schema, list):
            for i, item in enumerate(schema):
                item_path = f"{current_path}[{i}]"
                self._analyze_recursive(item, item_path)
    
    def find_cycles(self) -> List[List[str]]:
        """
        查找所有循环依赖
        
        Returns:
            循环路径列表
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node_path: str) -> None:
            visited.add(node_path)
            rec_stack.add(node_path)
            path.append(node_path)
            
            node = self.graph.get_node(node_path)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        dfs(dep)
                    elif dep in rec_stack:
                        # 发现循环
                        cycle_start = path.index(dep)
                        cycle = path[cycle_start:] + [dep]
                        # 避免重复循环
                        if cycle not in cycles and list(reversed(cycle)) not in cycles:
                            cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node_path)
        
        for node_path in self.graph.nodes:
            if node_path not in visited:
                dfs(node_path)
        
        return cycles
    
    def analyze_impact(self, changed_paths: List[str]) -> Dict[str, Any]:
        """
        分析变更影响范围
        
        Args:
            changed_paths: 变更的路径列表
            
        Returns:
            影响分析结果
        """
        directly_affected = set()
        indirectly_affected = set()
        critical_paths = []
        
        for path in changed_paths:
            if path not in self.graph.nodes:
                continue
            
            # 直接依赖此路径的
            direct_deps = self.graph.get_node(path).dependents
            directly_affected.update(direct_deps)
            
            # 间接依赖此路径的
            indirect_deps = self.get_all_dependents(path)
            indirectly_affected.update(indirect_deps - direct_deps - {path})
            
            # 关键路径
            critical_path = self.find_critical_path(path)
            if critical_path:
                critical_paths.append(critical_path)
        
        return {
            "changed_paths": changed_paths,
            "directly_affected": list(directly_affected),
            "indirectly_affected": list(indirectly_affected),
            "total_affected": len(directly_affected | indirectly_affected),
            "critical_paths": critical_paths,
            "risk_score": self._calculate_risk_score(
                changed_paths,
                directly_affected,
                indirectly_affected
            )
        }
    
    def get_all_dependents(self, path: str, include_indirect: bool = True) -> Set[str]:
        """获取所有被依赖的节点"""
        return self.graph.get_all_dependents(path, include_indirect)
    
    def get_all_dependencies(self, path: str, include_indirect: bool = True) -> Set[str]:
        """获取所有依赖的节点"""
        return self.graph.get_all_dependencies(path, include_indirect)
    
    def find_critical_path(self, start_path: str) -> Optional[List[str]]:
        """
        查找从指定路径出发的最长依赖链（关键路径）
        
        Args:
            start_path: 起始路径
            
        Returns:
            关键路径
        """
        if start_path not in self.graph.nodes:
            return None
        
        # DFS找最长路径
        longest_path = []
        
        def dfs(current: str, path: List[str]) -> None:
            nonlocal longest_path
            
            if len(path) > len(longest_path):
                longest_path = path.copy()
            
            node = self.graph.get_node(current)
            if node:
                for dep in node.dependents:
                    if dep not in path:  # 避免循环
                        path.append(dep)
                        dfs(dep, path)
                        path.pop()
        
        dfs(start_path, [start_path])
        return longest_path if len(longest_path) > 1 else None
    
    def topological_sort(self) -> Optional[List[str]]:
        """
        拓扑排序
        
        Returns:
            排序后的路径列表，如果存在循环依赖则返回None
        """
        # Kahn算法
        in_degree = {path: node.in_degree for path, node in self.graph.nodes.items()}
        queue = deque([path for path, deg in in_degree.items() if deg == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            node = self.graph.get_node(current)
            if node:
                for dependent in node.dependents:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # 检查是否有剩余节点（循环依赖）
        if len(result) != len(self.graph.nodes):
            return None
        
        return result
    
    def find_entry_points(self) -> List[str]:
        """
        查找入口点（没有依赖的节点）
        
        Returns:
            入口点路径列表
        """
        return [
            path for path, node in self.graph.nodes.items()
            if node.in_degree == 0
        ]
    
    def find_exit_points(self) -> List[str]:
        """
        查找出口点（没有依赖者的节点）
        
        Returns:
            出口点路径列表
        """
        return [
            path for path, node in self.graph.nodes.items()
            if node.out_degree == 0
        ]
    
    def _calculate_risk_score(
        self,
        changed: List[str],
        direct: Set[str],
        indirect: Set[str]
    ) -> float:
        """计算风险评分"""
        score = 0.0
        
        # 基于受影响节点数量
        total_affected = len(direct | indirect)
        total_nodes = len(self.graph.nodes)
        if total_nodes > 0:
            score += (total_affected / total_nodes) * 50
        
        # 基于变更数量
        score += len(changed) * 5
        
        # 检查循环依赖
        if self.find_cycles():
            score += 20
        
        return min(score, 100)
    
    def get_dependency_stats(self) -> Dict[str, Any]:
        """获取依赖统计信息"""
        if not self.graph.nodes:
            return {}
        
        in_degrees = [node.in_degree for node in self.graph.nodes.values()]
        out_degrees = [node.out_degree for node in self.graph.nodes.values()]
        
        return {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "avg_in_degree": sum(in_degrees) / len(in_degrees) if in_degrees else 0,
            "avg_out_degree": sum(out_degrees) / len(out_degrees) if out_degrees else 0,
            "max_in_degree": max(in_degrees) if in_degrees else 0,
            "max_out_degree": max(out_degrees) if out_degrees else 0,
            "entry_points": len(self.find_entry_points()),
            "exit_points": len(self.find_exit_points()),
            "cycles": len(self.find_cycles())
        }
