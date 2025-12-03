"""
知识抽象算法

实现实例到模式、模式到概念的抽象
"""

from typing import List, Dict, Any, Optional
from .storage import HierarchicalKGStorage


class KnowledgeAbstraction:
    """知识抽象器"""
    
    def __init__(self, storage: HierarchicalKGStorage):
        """
        初始化知识抽象器
        
        Args:
            storage: 层次化知识图谱存储管理器
        """
        self.storage = storage
    
    def abstract_instances_to_pattern(self, instance_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        将实例抽象为模式（L₁ → L₂）
        
        Args:
            instance_ids: 实例实体ID列表
            
        Returns:
            模式实体字典（如果成功）
        """
        # 1. 提取共同特征
        common_features = self._extract_common_features(instance_ids)
        
        # 2. 识别变化点
        variation_points = self._identify_variation_points(instance_ids)
        
        # 3. 构建模式
        pattern = self._build_pattern(common_features, variation_points)
        
        # 4. 存储模式实体
        pattern_id = f"pattern_{len(instance_ids)}_{hash(str(instance_ids))}"
        success = self.storage.add_entity(
            entity_id=pattern_id,
            name=pattern.get('name', 'Pattern'),
            level=2,  # 模式层
            content=pattern,
            properties={'instance_ids': instance_ids}
        )
        
        # 5. 建立抽象关系
        if success:
            for instance_id in instance_ids:
                self._create_abstraction_relation(
                    source_id=instance_id,
                    target_id=pattern_id,
                    abstraction_type='instance_to_pattern'
                )
        
        return pattern if success else None
    
    def abstract_patterns_to_concept(self, pattern_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        将模式抽象为概念（L₂ → L₃）
        
        Args:
            pattern_ids: 模式实体ID列表
            
        Returns:
            概念实体字典（如果成功）
        """
        # 1. 提取模式共性
        commonality = self._extract_commonality(pattern_ids)
        
        # 2. 识别模式差异
        differences = self._identify_differences(pattern_ids)
        
        # 3. 构建概念
        concept = self._build_concept(commonality, differences)
        
        # 4. 存储概念实体
        concept_id = f"concept_{len(pattern_ids)}_{hash(str(pattern_ids))}"
        success = self.storage.add_entity(
            entity_id=concept_id,
            name=concept.get('name', 'Concept'),
            level=3,  # 概念层
            content=concept,
            properties={'pattern_ids': pattern_ids}
        )
        
        # 5. 建立抽象关系
        if success:
            for pattern_id in pattern_ids:
                self._create_abstraction_relation(
                    source_id=pattern_id,
                    target_id=concept_id,
                    abstraction_type='pattern_to_concept'
                )
        
        return concept if success else None
    
    def _extract_common_features(self, instance_ids: List[str]) -> Dict[str, Any]:
        """提取共同特征"""
        # 获取所有实例
        instances = []
        for instance_id in instance_ids:
            entities = self.storage.get_entities_by_level(1)
            instance = next((e for e in entities if e['entity_id'] == instance_id), None)
            if instance:
                instances.append(instance)
        
        if not instances:
            return {}
        
        # 提取共同特征（简化实现）
        common_features = {
            'common_properties': {},
            'common_structure': {}
        }
        
        # 比较属性
        if instances:
            first_props = instances[0].get('properties', {})
            for key, value in first_props.items():
                if all(inst.get('properties', {}).get(key) == value for inst in instances):
                    common_features['common_properties'][key] = value
        
        return common_features
    
    def _identify_variation_points(self, instance_ids: List[str]) -> List[str]:
        """识别变化点"""
        # 获取所有实例
        instances = []
        for instance_id in instance_ids:
            entities = self.storage.get_entities_by_level(1)
            instance = next((e for e in entities if e['entity_id'] == instance_id), None)
            if instance:
                instances.append(instance)
        
        variation_points = []
        
        # 识别变化的属性
        if instances:
            first_props = instances[0].get('properties', {})
            for key in first_props.keys():
                values = [inst.get('properties', {}).get(key) for inst in instances]
                if len(set(values)) > 1:  # 有变化
                    variation_points.append(key)
        
        return variation_points
    
    def _build_pattern(self, common_features: Dict[str, Any],
                      variation_points: List[str]) -> Dict[str, Any]:
        """构建模式"""
        return {
            'name': 'Abstracted Pattern',
            'common_features': common_features,
            'variation_points': variation_points,
            'type': 'pattern'
        }
    
    def _extract_commonality(self, pattern_ids: List[str]) -> Dict[str, Any]:
        """提取模式共性"""
        # 获取所有模式
        patterns = []
        for pattern_id in pattern_ids:
            entities = self.storage.get_entities_by_level(2)
            pattern = next((e for e in entities if e['entity_id'] == pattern_id), None)
            if pattern:
                patterns.append(pattern)
        
        if not patterns:
            return {}
        
        # 提取共性（简化实现）
        commonality = {
            'common_structure': {},
            'common_principles': []
        }
        
        return commonality
    
    def _identify_differences(self, pattern_ids: List[str]) -> List[str]:
        """识别模式差异"""
        # 简化实现
        return []
    
    def _build_concept(self, commonality: Dict[str, Any],
                      differences: List[str]) -> Dict[str, Any]:
        """构建概念"""
        return {
            'name': 'Abstracted Concept',
            'commonality': commonality,
            'differences': differences,
            'type': 'concept'
        }
    
    def _create_abstraction_relation(self, source_id: str, target_id: str,
                                    abstraction_type: str) -> bool:
        """创建抽象关系"""
        # 更新源实体的抽象ID
        # 更新目标实体的具体化列表
        # 创建抽象关系记录
        # （简化实现，实际需要更复杂的逻辑）
        return True
