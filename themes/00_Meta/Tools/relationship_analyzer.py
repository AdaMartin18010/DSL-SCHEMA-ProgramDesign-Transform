#!/usr/bin/env python3
"""
Model Relationship Analyzer
===========================

模型关联分析器，用于：
- 发现模型间的关系
- 计算关联强度
- 验证层次映射
- 生成关联图谱

Version: 2.2.0
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import numpy as np


@dataclass
class ModelEntity:
    """模型实体"""
    id: str
    name: str
    type: str  # concept, standard, tool, schema
    attributes: Dict = field(default_factory=dict)
    source_file: Optional[str] = None


@dataclass
class Relationship:
    """模型关系"""
    source: str
    target: str
    rel_type: str  # specialization, composition, reference, etc.
    strength: float  # 0-1
    confidence: float  # 0-1
    evidence: List[str] = field(default_factory=list)


@dataclass
class HierarchyLevel:
    """层次级别"""
    level: int
    name: str
    description: str
    entities: List[ModelEntity] = field(default_factory=list)


class ModelRelationshipAnalyzer:
    """模型关联分析器"""
    
    RELATIONSHIP_TYPES = {
        "specialization": {"symbol": "⊑", "transitive": True, "symmetric": False},
        "composition": {"symbol": "◦", "transitive": True, "symmetric": False},
        "reference": {"symbol": "→ᵣ", "transitive": False, "symmetric": False},
        "association": {"symbol": "~", "transitive": False, "symmetric": True},
        "mapping": {"symbol": "→", "transitive": True, "symmetric": False},
        "equivalence": {"symbol": "≡", "transitive": True, "symmetric": True}
    }
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.themes_dir = self.project_root / "themes"
        self.entities: Dict[str, ModelEntity] = {}
        self.relationships: List[Relationship] = []
        self.hierarchy: Dict[int, HierarchyLevel] = {}
    
    def analyze_all_themes(self) -> Dict:
        """分析所有主题的关联"""
        print("🔍 分析主题模型关联...")
        
        # 1. 提取所有实体
        self._extract_entities()
        
        # 2. 发现关系
        self._discover_relationships()
        
        # 3. 构建层次结构
        self._build_hierarchy()
        
        # 4. 生成报告
        return self._generate_analysis_report()
    
    def _extract_entities(self):
        """从主题中提取实体"""
        if not self.themes_dir.exists():
            return
        
        for theme_dir in self.themes_dir.iterdir():
            if not theme_dir.is_dir() or not theme_dir.name[0].isdigit():
                continue
            
            theme_name = theme_dir.name
            
            # 提取概念
            concepts_dir = theme_dir / "Concepts"
            if concepts_dir.exists():
                for md_file in concepts_dir.glob("*.md"):
                    entity = ModelEntity(
                        id=f"{theme_name}_concept_{md_file.stem}",
                        name=md_file.stem,
                        type="concept",
                        source_file=str(md_file.relative_to(self.project_root))
                    )
                    self.entities[entity.id] = entity
            
            # 提取标准
            standards_dir = theme_dir / "Standards"
            if standards_dir.exists():
                for md_file in standards_dir.glob("*.md"):
                    entity = ModelEntity(
                        id=f"{theme_name}_std_{md_file.stem}",
                        name=md_file.stem,
                        type="standard",
                        source_file=str(md_file.relative_to(self.project_root))
                    )
                    self.entities[entity.id] = entity
            
            # 提取工具
            tools_dir = theme_dir / "Tools"
            if tools_dir.exists():
                for py_file in tools_dir.glob("*.py"):
                    if py_file.name.startswith("__"):
                        continue
                    entity = ModelEntity(
                        id=f"{theme_name}_tool_{py_file.stem}",
                        name=py_file.stem,
                        type="tool",
                        source_file=str(py_file.relative_to(self.project_root))
                    )
                    self.entities[entity.id] = entity
        
        print(f"  ✓ 提取了 {len(self.entities)} 个实体")
    
    def _discover_relationships(self):
        """发现实体间的关系"""
        entities_list = list(self.entities.values())
        
        for i, e1 in enumerate(entities_list):
            for e2 in entities_list[i+1:]:
                # 计算相似度
                similarity = self._calculate_similarity(e1, e2)
                
                if similarity > 0.5:
                    rel_type = self._determine_relationship_type(e1, e2)
                    
                    rel = Relationship(
                        source=e1.id,
                        target=e2.id,
                        rel_type=rel_type,
                        strength=similarity,
                        confidence=min(1.0, similarity * 1.2),
                        evidence=self._find_evidence(e1, e2)
                    )
                    self.relationships.append(rel)
        
        print(f"  ✓ 发现了 {len(self.relationships)} 个关系")
    
    def _calculate_similarity(self, e1: ModelEntity, e2: ModelEntity) -> float:
        """计算两个实体的相似度"""
        scores = []
        
        # 1. 名称相似度
        name_sim = self._string_similarity(e1.name.lower(), e2.name.lower())
        scores.append(name_sim * 0.4)
        
        # 2. 类型相同加分
        if e1.type == e2.type:
            scores.append(0.2)
        
        # 3. 文件路径相似度
        if e1.source_file and e2.source_file:
            path_sim = self._path_similarity(e1.source_file, e2.source_file)
            scores.append(path_sim * 0.2)
        
        # 4. 关键词重叠
        keywords1 = set(self._extract_keywords(e1.name))
        keywords2 = set(self._extract_keywords(e2.name))
        if keywords1 and keywords2:
            overlap = len(keywords1 & keywords2) / max(len(keywords1), len(keywords2))
            scores.append(overlap * 0.2)
        
        return sum(scores)
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度 (Jaccard)"""
        if not s1 or not s2:
            return 0.0
        
        # 生成n-gram
        def ngrams(s, n=2):
            return set(s[i:i+n] for i in range(len(s)-n+1))
        
        g1 = ngrams(s1)
        g2 = ngrams(s2)
        
        intersection = len(g1 & g2)
        union = len(g1 | g2)
        
        return intersection / union if union > 0 else 0.0
    
    def _path_similarity(self, p1: str, p2: str) -> float:
        """计算路径相似度"""
        parts1 = set(Path(p1).parts)
        parts2 = set(Path(p2).parts)
        
        intersection = len(parts1 & parts2)
        union = len(parts1 | parts2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'[A-Z][a-z]+|[a-z]+', text)
        return [w.lower() for w in words if len(w) > 2]
    
    def _determine_relationship_type(self, e1: ModelEntity, e2: ModelEntity) -> str:
        """确定关系类型"""
        # 基于命名模式判断
        if e1.name in e2.name or e2.name in e1.name:
            return "specialization"
        
        # 基于文件位置判断
        if e1.source_file and e2.source_file:
            p1 = Path(e1.source_file).parent
            p2 = Path(e2.source_file).parent
            if p1 == p2:
                return "composition"
        
        return "association"
    
    def _find_evidence(self, e1: ModelEntity, e2: ModelEntity) -> List[str]:
        """查找关系证据"""
        evidence = []
        
        # 检查文件内容中的引用
        if e1.source_file:
            try:
                content = (self.project_root / e1.source_file).read_text(
                    encoding='utf-8', errors='ignore'
                )
                if e2.name.lower() in content.lower():
                    evidence.append(f"{e1.name} 引用了 {e2.name}")
            except:
                pass
        
        return evidence
    
    def _build_hierarchy(self):
        """构建层次结构"""
        self.hierarchy = {
            1: HierarchyLevel(1, "Foundation", "基础数学层"),
            2: HierarchyLevel(2, "Meta-Model", "元模型层"),
            3: HierarchyLevel(3, "Data Model", "数据模型层"),
            4: HierarchyLevel(4, "Service Model", "服务模型层"),
            5: HierarchyLevel(5, "Application", "应用模型层")
        }
        
        # 将实体分配到层次
        for entity in self.entities.values():
            level = self._assign_hierarchy_level(entity)
            self.hierarchy[level].entities.append(entity)
    
    def _assign_hierarchy_level(self, entity: ModelEntity) -> int:
        """分配层次级别"""
        # 基于实体类型和路径判断
        path_lower = entity.source_file.lower() if entity.source_file else ""
        
        if "concept" in path_lower or "theory" in path_lower:
            return 2
        elif "api" in path_lower or "service" in path_lower:
            return 4
        elif "tool" in path_lower:
            return 3
        elif "application" in path_lower or "case" in path_lower:
            return 5
        else:
            return 3
    
    def _generate_analysis_report(self) -> Dict:
        """生成分析报告"""
        report = {
            "summary": {
                "total_entities": len(self.entities),
                "total_relationships": len(self.relationships),
                "relationship_types": defaultdict(int),
                "avg_relationship_strength": 0.0
            },
            "hierarchy": {},
            "relationships": [],
            "entity_clusters": []
        }
        
        # 统计关系类型
        strengths = []
        for rel in self.relationships:
            report["summary"]["relationship_types"][rel.rel_type] += 1
            strengths.append(rel.strength)
        
        if strengths:
            report["summary"]["avg_relationship_strength"] = sum(strengths) / len(strengths)
        
        # 层次统计
        for level, hl in self.hierarchy.items():
            report["hierarchy"][f"L{level}"] = {
                "name": hl.name,
                "entity_count": len(hl.entities)
            }
        
        # 关系详情
        for rel in self.relationships:
            report["relationships"].append({
                "source": self.entities[rel.source].name if rel.source in self.entities else rel.source,
                "target": self.entities[rel.target].name if rel.target in self.entities else rel.target,
                "type": rel.rel_type,
                "symbol": self.RELATIONSHIP_TYPES.get(rel.rel_type, {}).get("symbol", "~"),
                "strength": round(rel.strength, 3),
                "confidence": round(rel.confidence, 3)
            })
        
        # 聚类
        report["entity_clusters"] = self._cluster_entities()
        
        return report
    
    def _cluster_entities(self) -> List[Dict]:
        """对实体进行聚类"""
        # 简单的基于主题的聚类
        clusters = defaultdict(list)
        
        for entity in self.entities.values():
            theme = entity.id.split("_")[0]
            clusters[theme].append(entity.name)
        
        return [
            {"theme": theme, "entities": entities}
            for theme, entities in sorted(clusters.items())
        ]
    
    def export_to_graph_json(self, filepath: str):
        """导出为图JSON (用于D3.js)"""
        graph = {
            "nodes": [],
            "links": []
        }
        
        # 添加节点
        for entity_id, entity in self.entities.items():
            graph["nodes"].append({
                "id": entity_id,
                "name": entity.name,
                "type": entity.type,
                "group": self._assign_hierarchy_level(entity)
            })
        
        # 添加边
        for rel in self.relationships:
            graph["links"].append({
                "source": rel.source,
                "target": rel.target,
                "type": rel.rel_type,
                "value": rel.strength
            })
        
        Path(filepath).write_text(
            json.dumps(graph, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        return graph
    
    def export_to_mermaid(self) -> str:
        """导出为Mermaid图"""
        lines = ["graph TB"]
        
        # 按层次分组
        for level, hl in sorted(self.hierarchy.items()):
            if hl.entities:
                lines.append(f"    subgraph L{level} [{hl.name}]")
                for entity in hl.entities:
                    lines.append(f"        {entity.id}[{entity.name}]")
                lines.append("    end")
        
        # 添加关系
        for rel in self.relationships:
            symbol = self.RELATIONSHIP_TYPES.get(rel.rel_type, {}).get("symbol", "--")
            lines.append(f"    {rel.source} -->|{symbol}| {rel.target}")
        
        return "\n".join(lines)
    
    def find_mapping_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """查找两个实体间的映射路径"""
        # BFS查找路径
        if source_id not in self.entities or target_id not in self.entities:
            return None
        
        visited = {source_id}
        queue = [(source_id, [source_id])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target_id:
                return path
            
            for rel in self.relationships:
                if rel.source == current and rel.target not in visited:
                    visited.add(rel.target)
                    queue.append((rel.target, path + [rel.target]))
                elif rel.target == current and rel.source not in visited:
                    visited.add(rel.source)
                    queue.append((rel.source, path + [rel.source]))
        
        return None


def main():
    """主函数"""
    analyzer = ModelRelationshipAnalyzer()
    report = analyzer.analyze_all_themes()
    
    print("\n📊 关联分析报告")
    print("=" * 60)
    print(f"实体总数: {report['summary']['total_entities']}")
    print(f"关系总数: {report['summary']['total_relationships']}")
    print(f"平均关系强度: {report['summary']['avg_relationship_strength']:.3f}")
    
    print("\n📐 层次分布:")
    for level, info in sorted(report['hierarchy'].items()):
        print(f"  L{level} {info['name']}: {info['entity_count']} 实体")
    
    print("\n🔗 关系类型分布:")
    for rel_type, count in report['summary']['relationship_types'].items():
        print(f"  {rel_type}: {count}")
    
    # 导出
    analyzer.export_to_graph_json("model_relationship_graph.json")
    mermaid = analyzer.export_to_mermaid()
    Path("model_relationship.mmd").write_text(mermaid, encoding='utf-8')
    
    print("\n✅ 已导出:")
    print("  - model_relationship_graph.json")
    print("  - model_relationship.mmd")


if __name__ == "__main__":
    main()
