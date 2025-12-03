"""
可视化展示

生成推理过程的可视化
"""

from typing import Dict, Any, List, Optional
import json


class ReasoningVisualization:
    """推理可视化器"""
    
    def generate_graph_data(self, reasoning_path: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成图数据（用于可视化）
        
        Args:
            reasoning_path: 推理路径
            
        Returns:
            图数据字典（节点和边）
        """
        nodes = []
        edges = []
        
        # 添加查询节点
        nodes.append({
            'id': 'query',
            'label': reasoning_path.get('query', 'Query'),
            'type': 'query',
            'level': 0
        })
        
        # 添加推理步骤节点
        steps = reasoning_path.get('steps', [])
        for i, step in enumerate(steps):
            node_id = f"step_{i+1}"
            nodes.append({
                'id': node_id,
                'label': f"步骤{i+1}",
                'type': step.get('type', 'inference'),
                'level': i + 1,
                'data': step
            })
            
            # 添加边
            if i == 0:
                edges.append({
                    'source': 'query',
                    'target': node_id,
                    'type': 'reasoning'
                })
            else:
                edges.append({
                    'source': f"step_{i}",
                    'target': node_id,
                    'type': 'reasoning'
                })
        
        # 添加结果节点
        result = reasoning_path.get('result', {})
        result_id = 'result'
        nodes.append({
            'id': result_id,
            'label': '推理结果',
            'type': 'result',
            'level': len(steps) + 1,
            'data': result
        })
        
        if steps:
            edges.append({
                'source': f"step_{len(steps)}",
                'target': result_id,
                'type': 'conclusion'
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'layout': 'hierarchical'
        }
    
    def generate_text_explanation(self, reasoning_path: Dict[str, Any]) -> str:
        """
        生成文本解释
        
        Args:
            reasoning_path: 推理路径
            
        Returns:
            文本解释
        """
        lines = []
        
        lines.append(f"查询：{reasoning_path.get('query', '')}")
        lines.append("")
        lines.append("推理过程：")
        
        steps = reasoning_path.get('steps', [])
        for i, step in enumerate(steps, 1):
            lines.append(f"  步骤{i}：{step.get('explanation', '执行推理')}")
        
        lines.append("")
        result = reasoning_path.get('result', {})
        lines.append(f"结论：{json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return "\n".join(lines)
    
    def generate_json_output(self, reasoning_path: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成JSON输出
        
        Args:
            reasoning_path: 推理路径
            
        Returns:
            JSON格式的输出
        """
        return {
            'query': reasoning_path.get('query'),
            'steps': reasoning_path.get('steps', []),
            'result': reasoning_path.get('result', {}),
            'rules_applied': reasoning_path.get('rules_applied', []),
            'confidence': reasoning_path.get('confidence', 0),
            'graph_data': self.generate_graph_data(reasoning_path)
        }
