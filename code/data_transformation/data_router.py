"""
数据路由模块

专注于数据路由、分发、负载均衡
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import random

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """路由策略"""
    ROUND_ROBIN = "round_robin"  # 轮询
    RANDOM = "random"  # 随机
    WEIGHTED = "weighted"  # 加权
    HASH = "hash"  # 哈希
    LEAST_CONNECTIONS = "least_connections"  # 最少连接


@dataclass
class Route:
    """路由"""
    route_id: str
    source: str
    targets: List[str]
    strategy: RoutingStrategy
    weights: Optional[Dict[str, float]] = None
    enabled: bool = True


@dataclass
class RoutingResult:
    """路由结果"""
    route_id: str
    source: str
    selected_target: str
    routing_time: float
    success: bool


class DataRouter:
    """
    数据路由器
    
    专注于数据路由、分发、负载均衡
    """
    
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.routing_history: List[RoutingResult] = {}
        self.target_connections: Dict[str, int] = {}  # 目标连接数
    
    def create_route(self, route_config: Dict[str, Any]) -> Route:
        """
        创建路由
        
        Args:
            route_config: 路由配置
            
        Returns:
            路由对象
        """
        route_id = route_config.get('route_id', f"route_{datetime.utcnow().timestamp()}")
        
        route = Route(
            route_id=route_id,
            source=route_config['source'],
            targets=route_config['targets'],
            strategy=RoutingStrategy(route_config.get('strategy', 'round_robin')),
            weights=route_config.get('weights'),
            enabled=route_config.get('enabled', True)
        )
        
        self.routes[route_id] = route
        
        # 初始化目标连接数
        for target in route.targets:
            if target not in self.target_connections:
                self.target_connections[target] = 0
        
        return route
    
    def route(self, route_id: str, data: Any, routing_key: Optional[str] = None) -> RoutingResult:
        """
        路由数据
        
        Args:
            route_id: 路由ID
            data: 数据
            routing_key: 路由键（用于哈希路由）
            
        Returns:
            路由结果
        """
        if route_id not in self.routes:
            raise ValueError(f"路由不存在: {route_id}")
        
        route = self.routes[route_id]
        
        if not route.enabled:
            raise ValueError(f"路由已禁用: {route_id}")
        
        if not route.targets:
            raise ValueError(f"路由没有目标: {route_id}")
        
        start_time = datetime.utcnow()
        
        # 选择目标
        selected_target = self._select_target(route, routing_key)
        
        # 更新连接数
        self.target_connections[selected_target] = self.target_connections.get(selected_target, 0) + 1
        
        end_time = datetime.utcnow()
        routing_time = (end_time - start_time).total_seconds()
        
        result = RoutingResult(
            route_id=route_id,
            source=route.source,
            selected_target=selected_target,
            routing_time=routing_time,
            success=True
        )
        
        if route_id not in self.routing_history:
            self.routing_history[route_id] = []
        self.routing_history[route_id].append(result)
        
        return result
    
    def _select_target(self, route: Route, routing_key: Optional[str] = None) -> str:
        """选择目标"""
        strategy = route.strategy
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            # 轮询
            if route.route_id not in DataRouter._round_robin_index:
                DataRouter._round_robin_index[route.route_id] = 0
            
            index = DataRouter._round_robin_index[route.route_id]
            selected = route.targets[index % len(route.targets)]
            DataRouter._round_robin_index[route.route_id] = (index + 1) % len(route.targets)
            return selected
        
        elif strategy == RoutingStrategy.RANDOM:
            # 随机
            return random.choice(route.targets)
        
        elif strategy == RoutingStrategy.WEIGHTED:
            # 加权
            if route.weights:
                targets = list(route.weights.keys())
                weights = list(route.weights.values())
                return random.choices(targets, weights=weights)[0]
            else:
                return random.choice(route.targets)
        
        elif strategy == RoutingStrategy.HASH:
            # 哈希
            if routing_key:
                index = hash(routing_key) % len(route.targets)
                return route.targets[index]
            else:
                return random.choice(route.targets)
        
        elif strategy == RoutingStrategy.LEAST_CONNECTIONS:
            # 最少连接
            target_conns = [
                (target, self.target_connections.get(target, 0))
                for target in route.targets
            ]
            target_conns.sort(key=lambda x: x[1])
            return target_conns[0][0]
        
        else:
            return route.targets[0]
    
    def _round_robin_index: Dict[str, int] = {}  # 类变量，用于轮询索引
    
    def broadcast(self, route_id: str, data: Any) -> List[RoutingResult]:
        """
        广播数据到所有目标
        
        Args:
            route_id: 路由ID
            data: 数据
            
        Returns:
            路由结果列表
        """
        if route_id not in self.routes:
            raise ValueError(f"路由不存在: {route_id}")
        
        route = self.routes[route_id]
        results = []
        
        for target in route.targets:
            # 为每个目标创建临时路由结果
            result = RoutingResult(
                route_id=route_id,
                source=route.source,
                selected_target=target,
                routing_time=0.0,
                success=True
            )
            results.append(result)
        
        return results
    
    def get_routing_stats(self, route_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取路由统计
        
        Args:
            route_id: 路由ID（可选）
            
        Returns:
            路由统计
        """
        if route_id:
            if route_id not in self.routing_history:
                return {'error': '路由不存在或没有历史记录'}
            
            history = self.routing_history[route_id]
            target_counts = {}
            for result in history:
                target = result.selected_target
                target_counts[target] = target_counts.get(target, 0) + 1
            
            return {
                'route_id': route_id,
                'total_routings': len(history),
                'target_distribution': target_counts
            }
        else:
            total_routings = sum(len(h) for h in self.routing_history.values())
            return {
                'total_routes': len(self.routes),
                'total_routings': total_routings,
                'target_connections': self.target_connections.copy()
            }


def main():
    """主函数 - 示例用法"""
    router = DataRouter()
    
    # 创建路由
    route = router.create_route({
        'source': 'input',
        'targets': ['target1', 'target2', 'target3'],
        'strategy': 'round_robin'
    })
    
    # 路由数据
    result = router.route(route.route_id, 'data')
    print(f"路由结果: 目标={result.selected_target}")


if __name__ == '__main__':
    main()
