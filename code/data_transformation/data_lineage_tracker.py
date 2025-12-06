"""
数据血缘追踪器

专注于数据血缘关系追踪和分析
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LineageDirection(Enum):
    """血缘方向"""
    UPSTREAM = "upstream"  # 上游
    DOWNSTREAM = "downstream"  # 下游
    BOTH = "both"  # 双向


@dataclass
class LineageNode:
    """血缘节点"""
    node_id: str
    asset_type: str
    asset_name: str
    metadata: Dict[str, Any] = None


@dataclass
class LineageEdge:
    """血缘边"""
    edge_id: str
    source_node_id: str
    target_node_id: str
    transformation: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class LineageGraph:
    """血缘图"""
    graph_id: str
    nodes: Dict[str, LineageNode]
    edges: Dict[str, LineageEdge]
    created_at: datetime


class DataLineageTracker:
    """
    数据血缘追踪器
    
    专注于数据血缘关系追踪和分析
    """
    
    def __init__(self):
        self.graphs: Dict[str, LineageGraph] = {}
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: Dict[str, LineageEdge] = {}
    
    def create_node(self, node_config: Dict[str, Any]) -> LineageNode:
        """
        创建血缘节点
        
        Args:
            node_config: 节点配置
            
        Returns:
            血缘节点对象
        """
        node_id = node_config.get('node_id', f"node_{datetime.utcnow().timestamp()}")
        
        node = LineageNode(
            node_id=node_id,
            asset_type=node_config.get('asset_type', 'table'),
            asset_name=node_config.get('asset_name', ''),
            metadata=node_config.get('metadata', {})
        )
        
        self.nodes[node_id] = node
        return node
    
    def create_edge(self, edge_config: Dict[str, Any]) -> LineageEdge:
        """
        创建血缘边
        
        Args:
            edge_config: 边配置
            
        Returns:
            血缘边对象
        """
        edge_id = edge_config.get('edge_id', f"edge_{datetime.utcnow().timestamp()}")
        source_node_id = edge_config.get('source_node_id')
        target_node_id = edge_config.get('target_node_id')
        
        # 验证节点存在
        if source_node_id not in self.nodes:
            raise ValueError(f"源节点不存在: {source_node_id}")
        
        if target_node_id not in self.nodes:
            raise ValueError(f"目标节点不存在: {target_node_id}")
        
        edge = LineageEdge(
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            transformation=edge_config.get('transformation'),
            metadata=edge_config.get('metadata', {})
        )
        
        self.edges[edge_id] = edge
        return edge
    
    def get_lineage_path(self, node_id: str, direction: LineageDirection = LineageDirection.BOTH,
                        max_depth: int = 10) -> Dict[str, Any]:
        """
        获取血缘路径
        
        Args:
            node_id: 节点ID
            direction: 方向
            max_depth: 最大深度
            
        Returns:
            血缘路径
        """
        if node_id not in self.nodes:
            return {'error': '节点不存在'}
        
        paths = {
            'node_id': node_id,
            'upstream': [],
            'downstream': []
        }
        
        if direction in [LineageDirection.UPSTREAM, LineageDirection.BOTH]:
            upstream_paths = self._find_paths(node_id, 'upstream', max_depth)
            paths['upstream'] = upstream_paths
        
        if direction in [LineageDirection.DOWNSTREAM, LineageDirection.BOTH]:
            downstream_paths = self._find_paths(node_id, 'downstream', max_depth)
            paths['downstream'] = downstream_paths
        
        return paths
    
    def _find_paths(self, start_node_id: str, direction: str, max_depth: int) -> List[List[str]]:
        """查找路径"""
        paths = []
        visited = set()
        
        def dfs(current_node: str, current_path: List[str], depth: int):
            if depth > max_depth or current_node in visited:
                return
            
            visited.add(current_node)
            current_path.append(current_node)
            
            if len(current_path) > 1:
                paths.append(current_path.copy())
            
            # 查找相邻节点
            neighbors = self._get_neighbors(current_node, direction)
            for neighbor in neighbors:
                if neighbor not in visited:
                    dfs(neighbor, current_path, depth + 1)
            
            current_path.pop()
            visited.remove(current_node)
        
        dfs(start_node_id, [], 0)
        return paths
    
    def _get_neighbors(self, node_id: str, direction: str) -> List[str]:
        """获取相邻节点"""
        neighbors = []
        
        if direction == 'upstream':
            # 上游节点（该节点作为目标）
            neighbors = [
                edge.source_node_id
                for edge in self.edges.values()
                if edge.target_node_id == node_id
            ]
        else:
            # 下游节点（该节点作为源）
            neighbors = [
                edge.target_node_id
                for edge in self.edges.values()
                if edge.source_node_id == node_id
            ]
        
        return neighbors
    
    def get_impact_analysis(self, node_id: str) -> Dict[str, Any]:
        """
        获取影响分析
        
        Args:
            node_id: 节点ID
            
        Returns:
            影响分析结果
        """
        if node_id not in self.nodes:
            return {'error': '节点不存在'}
        
        # 获取所有下游节点
        downstream_nodes = set()
        queue = [node_id]
        visited = set()
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            neighbors = self._get_neighbors(current, 'downstream')
            
            for neighbor in neighbors:
                downstream_nodes.add(neighbor)
                if neighbor not in visited:
                    queue.append(neighbor)
        
        # 统计影响
        impact = {
            'node_id': node_id,
            'direct_impact': len(self._get_neighbors(node_id, 'downstream')),
            'total_impact': len(downstream_nodes),
            'affected_nodes': list(downstream_nodes),
            'impact_level': self._calculate_impact_level(len(downstream_nodes))
        }
        
        return impact
    
    def _calculate_impact_level(self, affected_count: int) -> str:
        """计算影响级别"""
        if affected_count == 0:
            return 'none'
        elif affected_count <= 5:
            return 'low'
        elif affected_count <= 20:
            return 'medium'
        else:
            return 'high'
    
    def build_graph(self, graph_id: str) -> LineageGraph:
        """
        构建血缘图
        
        Args:
            graph_id: 图ID
            
        Returns:
            血缘图对象
        """
        graph = LineageGraph(
            graph_id=graph_id,
            nodes=self.nodes.copy(),
            edges=self.edges.copy(),
            created_at=datetime.utcnow()
        )
        
        self.graphs[graph_id] = graph
        return graph


def main():
    """主函数 - 示例用法"""
    tracker = DataLineageTracker()
    
    # 创建节点
    node1 = tracker.create_node({
        'asset_type': 'table',
        'asset_name': 'source_table'
    })
    
    node2 = tracker.create_node({
        'asset_type': 'table',
        'asset_name': 'target_table'
    })
    
    # 创建边
    edge = tracker.create_edge({
        'source_node_id': node1.node_id,
        'target_node_id': node2.node_id,
        'transformation': 'SELECT * FROM source_table'
    })
    
    # 获取血缘路径
    paths = tracker.get_lineage_path(node1.node_id, LineageDirection.DOWNSTREAM)
    print(f"血缘路径: {paths}")
    
    # 影响分析
    impact = tracker.get_impact_analysis(node1.node_id)
    print(f"影响分析: {impact}")


if __name__ == '__main__':
    main()
