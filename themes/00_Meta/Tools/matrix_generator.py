#!/usr/bin/env python3
"""
概念矩阵生成工具
自动生成和分析主题属性矩阵
"""

import json
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ThemeAttribute:
    """主题属性"""
    name: str
    value: str
    dimension: str


class MatrixGenerator:
    """矩阵生成器"""
    
    def __init__(self):
        self.themes = {}
        self.dimensions = ['theory', 'application', 'standard', 'tool', 'industry']
    
    def add_theme(self, theme_id: str, name: str, attributes: Dict):
        """添加主题"""
        self.themes[theme_id] = {
            'name': name,
            'attributes': attributes
        }
    
    def generate_matrix(self, dimension: str = None) -> Dict:
        """生成矩阵"""
        matrix = {
            'headers': ['Theme ID', 'Theme Name'] + (self.dimensions if dimension is None else [dimension]),
            'rows': []
        }
        
        for theme_id, theme_data in self.themes.items():
            row = [theme_id, theme_data['name']]
            
            attrs = theme_data['attributes']
            if dimension:
                row.append(attrs.get(dimension, 'N/A'))
            else:
                for dim in self.dimensions:
                    row.append(attrs.get(dim, 'N/A'))
            
            matrix['rows'].append(row)
        
        return matrix
    
    def export_markdown(self, matrix: Dict, output_file: str):
        """导出为Markdown表格"""
        lines = []
        
        # 表头
        headers = '| ' + ' | '.join(matrix['headers']) + ' |'
        lines.append(headers)
        lines.append('|' + '|'.join(['---' for _ in matrix['headers']]) + '|')
        
        # 数据行
        for row in matrix['rows']:
            lines.append('| ' + ' | '.join(str(cell) for cell in row) + ' |')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def analyze_similarity(self, theme_id1: str, theme_id2: str) -> float:
        """分析两个主题的相似度"""
        if theme_id1 not in self.themes or theme_id2 not in self.themes:
            return 0.0
        
        attrs1 = self.themes[theme_id1]['attributes']
        attrs2 = self.themes[theme_id2]['attributes']
        
        matches = 0
        total = 0
        
        for dim in self.dimensions:
            if dim in attrs1 and dim in attrs2:
                total += 1
                if attrs1[dim] == attrs2[dim]:
                    matches += 1
        
        return matches / total if total > 0 else 0.0
    
    def find_related_themes(self, theme_id: str, threshold: float = 0.5) -> List[str]:
        """查找相关主题"""
        related = []
        for other_id in self.themes:
            if other_id != theme_id:
                similarity = self.analyze_similarity(theme_id, other_id)
                if similarity >= threshold:
                    related.append((other_id, similarity))
        
        return sorted(related, key=lambda x: x[1], reverse=True)


# 示例使用
if __name__ == '__main__':
    generator = MatrixGenerator()
    
    # 添加示例主题
    generator.add_theme('01', 'Industrial_Automation', {
        'theory': 'Formal Language',
        'application': 'Real-time Control',
        'standard': 'IEC 61131-3',
        'tool': 'PLC Tools',
        'industry': 'Manufacturing'
    })
    
    generator.add_theme('02', 'IoT_Schema', {
        'theory': 'Knowledge Graph',
        'application': 'Device Interconnect',
        'standard': 'MQTT/CoAP',
        'tool': 'IoT Platform',
        'industry': 'IoT'
    })
    
    # 生成矩阵
    matrix = generator.generate_matrix()
    generator.export_markdown(matrix, 'matrix_output.md')
    
    print("Matrix generated: matrix_output.md")
