#!/usr/bin/env python3
"""
Schema推荐系统
使用机器学习推荐最适合的Schema类型
"""

import json
import numpy as np
from typing import Dict, List, Tuple


class SchemaRecommender:
    """基于机器学习的Schema推荐器"""
    
    def __init__(self):
        self.schema_types = [
            'json_schema',
            'xml_schema',
            'openapi',
            'protobuf',
            'avro',
            'graphql'
        ]
        
        # 特征权重（简化版本）
        self.weights = {
            'web_api': {'openapi': 0.9, 'graphql': 0.8, 'json_schema': 0.6},
            'data_storage': {'avro': 0.9, 'protobuf': 0.8, 'json_schema': 0.5},
            'config': {'json_schema': 0.9, 'xml_schema': 0.6},
            'messaging': {'protobuf': 0.9, 'avro': 0.8, 'json_schema': 0.5}
        }
    
    def analyze_requirements(self, requirements: Dict) -> Dict:
        """
        分析需求并推荐Schema类型
        
        Args:
            requirements: 需求字典
                - use_case: 使用场景
                - performance_priority: 性能优先级 (high/medium/low)
                - human_readable: 是否需要人类可读
                - schema_evolution: 是否需要Schema演进
        
        Returns:
            推荐结果
        """
        use_case = requirements.get('use_case', 'general')
        performance = requirements.get('performance_priority', 'medium')
        readable = requirements.get('human_readable', True)
        evolution = requirements.get('schema_evolution', False)
        
        scores = {}
        
        for schema_type in self.schema_types:
            score = 0.0
            
            # 基于使用场景
            if use_case in self.weights:
                score += self.weights[use_case].get(schema_type, 0.3)
            
            # 基于性能需求
            if performance == 'high':
                if schema_type in ['protobuf', 'avro']:
                    score += 0.3
            
            # 基于可读性
            if readable:
                if schema_type in ['json_schema', 'openapi', 'graphql']:
                    score += 0.2
            
            # 基于Schema演进
            if evolution:
                if schema_type in ['avro', 'protobuf']:
                    score += 0.2
            
            scores[schema_type] = score
        
        # 排序并返回Top 3
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'recommendations': [
                {
                    'schema_type': schema,
                    'score': round(score, 2),
                    'confidence': self._get_confidence(score)
                }
                for schema, score in sorted_scores[:3]
            ],
            'analysis': self._generate_analysis(requirements, sorted_scores[0][0])
        }
    
    def _get_confidence(self, score: float) -> str:
        """获取置信度级别"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_analysis(self, requirements: Dict, recommendation: str) -> str:
        """生成分析说明"""
        use_case = requirements.get('use_case', 'general')
        
        analysis_map = {
            'web_api': f"推荐使用 {recommendation}，因为它提供了良好的API文档和类型安全",
            'data_storage': f"推荐使用 {recommendation}，因为它支持高效的序列化和压缩",
            'config': f"推荐使用 {recommendation}，因为它易于人类阅读和编辑",
            'messaging': f"推荐使用 {recommendation}，因为它在消息传递中性能优异"
        }
        
        return analysis_map.get(use_case, f"基于您的需求，推荐使用 {recommendation}")


class SchemaAnomalyDetector:
    """Schema异常检测器"""
    
    def __init__(self):
        self.baseline_stats = {}
    
    def learn_normal_patterns(self, schemas: List[Dict]):
        """学习正常Schema模式"""
        depths = []
        property_counts = []
        
        for schema in schemas:
            depths.append(self._calculate_depth(schema))
            property_counts.append(self._count_properties(schema))
        
        self.baseline_stats = {
            'avg_depth': np.mean(depths),
            'std_depth': np.std(depths),
            'avg_properties': np.mean(property_counts),
            'std_properties': np.std(property_counts)
        }
    
    def detect_anomalies(self, schema: Dict) -> List[Dict]:
        """检测Schema异常"""
        if not self.baseline_stats:
            return [{'warning': 'No baseline established'}]
        
        anomalies = []
        
        depth = self._calculate_depth(schema)
        prop_count = self._count_properties(schema)
        
        # 检测深度异常
        if depth > self.baseline_stats['avg_depth'] + 2 * self.baseline_stats['std_depth']:
            anomalies.append({
                'type': 'deep_nesting',
                'severity': 'warning',
                'message': f'Schema nesting depth ({depth}) exceeds normal range'
            })
        
        # 检测属性数量异常
        if prop_count > self.baseline_stats['avg_properties'] + 2 * self.baseline_stats['std_properties']:
            anomalies.append({
                'type': 'too_many_properties',
                'severity': 'warning',
                'message': f'Property count ({prop_count}) exceeds normal range'
            })
        
        return anomalies
    
    def _calculate_depth(self, obj, current_depth=0) -> int:
        """计算对象深度"""
        if not isinstance(obj, dict):
            return current_depth
        
        max_depth = current_depth
        for value in obj.values():
            if isinstance(value, dict):
                max_depth = max(max_depth, self._calculate_depth(value, current_depth + 1))
        
        return max_depth
    
    def _count_properties(self, schema: Dict) -> int:
        """计算属性数量"""
        if 'properties' not in schema:
            return 0
        return len(schema['properties'])


def main():
    """示例用法"""
    recommender = SchemaRecommender()
    
    # 测试推荐
    requirements = {
        'use_case': 'web_api',
        'performance_priority': 'high',
        'human_readable': True,
        'schema_evolution': True
    }
    
    result = recommender.analyze_requirements(requirements)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
