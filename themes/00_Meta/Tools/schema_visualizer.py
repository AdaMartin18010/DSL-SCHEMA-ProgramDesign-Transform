#!/usr/bin/env python3
"""
Schema Visualizer
=================

Schema可视化工具，支持：
- ER图生成
- 类图生成
- 关系图生成
- 交互式图表
- Mermaid/PlantUML导出

Version: 2.1.0
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import html


@dataclass
class GraphNode:
    """图节点"""
    id: str
    label: str
    type: str  # entity, attribute, relationship
    properties: Dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    """图边"""
    source: str
    target: str
    label: str
    type: str  # one_to_one, one_to_many, many_to_many


class SchemaGraphBuilder:
    """Schema图构建器"""
    
    def __init__(self):
        self.nodes: List[GraphNode] = []
        self.edges: List[GraphEdge] = []
    
    def build_from_json_schema(self, schema: Dict, root_name: str = "Root"):
        """从JSON Schema构建图"""
        self._parse_schema_node(root_name, schema, None)
        return self
    
    def _parse_schema_node(self, name: str, schema: Dict, parent: Optional[str]):
        """递归解析Schema节点"""
        node_id = name.lower().replace(" ", "_")
        
        # 创建节点
        node_type = "entity" if schema.get("type") == "object" else "type"
        node = GraphNode(
            id=node_id,
            label=name,
            type=node_type,
            properties=schema
        )
        self.nodes.append(node)
        
        # 如果有父节点，创建关系
        if parent:
            self.edges.append(GraphEdge(
                source=parent,
                target=node_id,
                label="has",
                type="one_to_many"
            ))
        
        # 解析属性
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_schema.get("type") == "object":
                    # 嵌套对象
                    self._parse_schema_node(prop_name, prop_schema, node_id)
                elif prop_schema.get("type") == "array" and "items" in prop_schema:
                    # 数组
                    item_schema = prop_schema["items"]
                    if item_schema.get("type") == "object":
                        self._parse_schema_node(f"{name}.{prop_name}", item_schema, node_id)
                else:
                    # 普通属性
                    attr_id = f"{node_id}_{prop_name}"
                    attr_node = GraphNode(
                        id=attr_id,
                        label=prop_name,
                        type="attribute",
                        properties=prop_schema
                    )
                    self.nodes.append(attr_node)
                    
                    self.edges.append(GraphEdge(
                        source=node_id,
                        target=attr_id,
                        label="attribute",
                        type="one_to_one"
                    ))
    
    def to_mermaid(self) -> str:
        """生成Mermaid图"""
        lines = ["erDiagram"]
        
        # 实体定义
        entities = {}
        for node in self.nodes:
            if node.type == "entity":
                attrs = []
                for edge in self.edges:
                    if edge.source == node.id and edge.label == "attribute":
                        attr_node = next((n for n in self.nodes if n.id == edge.target), None)
                        if attr_node:
                            data_type = attr_node.properties.get("type", "string")
                            attrs.append(f"    {data_type} {attr_node.label}")
                entities[node.id] = attrs
        
        # 输出实体
        for entity_id, attrs in entities.items():
            entity_name = next(n.label for n in self.nodes if n.id == entity_id)
            lines.append(f"    {entity_id} {{")
            for attr in attrs:
                lines.append(attr)
            lines.append("    }")
        
        # 关系
        for edge in self.edges:
            if edge.label != "attribute":
                source_label = next((n.label for n in self.nodes if n.id == edge.source), edge.source)
                target_label = next((n.label for n in self.nodes if n.id == edge.target), edge.target)
                lines.append(f"    {edge.source} ||--o{{ {edge.target} : {edge.label}")
        
        return "\n".join(lines)
    
    def to_plantuml(self) -> str:
        """生成PlantUML图"""
        lines = ["@startuml", "skinparam classAttributeIconSize 0"]
        
        # 类定义
        for node in self.nodes:
            if node.type == "entity":
                lines.append(f"class {node.id} {{")
                
                # 属性
                for edge in self.edges:
                    if edge.source == node.id and edge.label == "attribute":
                        attr_node = next((n for n in self.nodes if n.id == edge.target), None)
                        if attr_node:
                            data_type = attr_node.properties.get("type", "string")
                            lines.append(f"  +{attr_node.label}: {data_type}")
                
                lines.append("}")
        
        # 关系
        for edge in self.edges:
            if edge.label != "attribute":
                lines.append(f"{edge.source} --> {edge.target}")
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def to_d3_json(self) -> Dict:
        """生成D3.js可用的JSON"""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "type": n.type,
                    "properties": n.properties
                }
                for n in self.nodes
            ],
            "links": [
                {
                    "source": e.source,
                    "target": e.target,
                    "label": e.label,
                    "type": e.type
                }
                for e in self.edges
            ]
        }
    
    def to_html_visualization(self, title: str = "Schema Visualization") -> str:
        """生成HTML可视化页面"""
        d3_data = self.to_d3_json()
        
        html_template = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        #graph {{ width: 100%; height: 800px; border: 1px solid #ddd; }}
        .node {{ cursor: pointer; }}
        .node circle {{ fill: #69b3a2; stroke: #fff; stroke-width: 2px; }}
        .node text {{ font-size: 12px; fill: #333; }}
        .link {{ stroke: #999; stroke-opacity: 0.6; stroke-width: 2px; }}
        .link-label {{ font-size: 10px; fill: #666; }}
        #info {{ position: absolute; top: 20px; right: 20px; background: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; max-width: 300px; }}
    </style>
</head>
<body>
    <h1>{{title}}</h1>
    <div id="graph"></div>
    <div id="info">
        <h3>节点信息</h3>
        <p>点击节点查看详情</p>
    </div>
    
    <script>
        const data = {json.dumps(d3_data, ensure_ascii=False, indent=2)};
        
        const width = document.getElementById('graph').clientWidth;
        const height = 800;
        
        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .enter().append("line")
            .attr("class", "link");
        
        const node = svg.append("g")
            .selectAll("g")
            .data(data.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("r", d => d.type === 'entity' ? 20 : 10)
            .attr("fill", d => d.type === 'entity' ? '#69b3a2' : '#ff7f0e');
        
        node.append("text")
            .attr("dx", 25)
            .attr("dy", 5)
            .text(d => d.label);
        
        node.on("click", function(event, d) {{
            const info = document.getElementById('info');
            info.innerHTML = `
                <h3>${{d.label}}</h3>
                <p><strong>类型:</strong> ${{d.type}}</p>
                <p><strong>ID:</strong> ${{d.id}}</p>
                <pre>${{JSON.stringify(d.properties, null, 2)}}</pre>
            `;
        }});
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>'''
        
        return html_template.format(title=title)


class SchemaComparisonVisualizer:
    """Schema对比可视化器"""
    
    def generate_diff_html(self, schema1: Dict, schema2: Dict, title: str = "Schema Diff") -> str:
        """生成Schema差异对比HTML"""
        diff = self._compare_schemas(schema1, schema2)
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: monospace; margin: 20px; background: #f5f5f5; }}
        .container {{ display: flex; gap: 20px; }}
        .panel {{ flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .added {{ background: #d4edda; color: #155724; }}
        .removed {{ background: #f8d7da; color: #721c24; }}
        .modified {{ background: #fff3cd; color: #856404; }}
        .unchanged {{ color: #666; }}
        h2 {{ margin-top: 0; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="container">
        <div class="panel">
            <h2>Schema A</h2>
            <pre>{html.escape(json.dumps(schema1, indent=2, ensure_ascii=False))}</pre>
        </div>
        <div class="panel">
            <h2>Schema B</h2>
            <pre>{html.escape(json.dumps(schema2, indent=2, ensure_ascii=False))}</pre>
        </div>
    </div>
</body>
</html>'''
        return html_content
    
    def _compare_schemas(self, s1: Dict, s2: Dict, path: str = "") -> List[Dict]:
        """递归比较两个Schema"""
        differences = []
        
        all_keys = set(s1.keys()) | set(s2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            if key not in s1:
                differences.append({"path": current_path, "type": "added", "value": s2[key]})
            elif key not in s2:
                differences.append({"path": current_path, "type": "removed", "value": s1[key]})
            elif isinstance(s1[key], dict) and isinstance(s2[key], dict):
                differences.extend(self._compare_schemas(s1[key], s2[key], current_path))
            elif s1[key] != s2[key]:
                differences.append({
                    "path": current_path,
                    "type": "modified",
                    "old": s1[key],
                    "new": s2[key]
                })
        
        return differences


def main():
    """示例用法"""
    # 示例Schema
    schema = {
        "type": "object",
        "title": "Product",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "price": {"type": "number"},
            "category": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"}
                }
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["id", "name"]
    }
    
    # 构建图
    builder = SchemaGraphBuilder()
    builder.build_from_json_schema(schema, "Product")
    
    # 输出Mermaid
    print("=== Mermaid ER Diagram ===")
    print(builder.to_mermaid())
    
    print("\n=== PlantUML ===")
    print(builder.to_plantuml())
    
    # 生成HTML
    html_output = builder.to_html_visualization("Product Schema")
    Path("schema_visualization.html").write_text(html_output, encoding='utf-8')
    print("\n✅ HTML可视化已保存到: schema_visualization.html")


if __name__ == "__main__":
    main()
