"""
数据导出模块

专注于数据导出、格式转换、批量导出
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import csv
import logging

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """导出格式"""
    JSON = "json"  # JSON格式
    CSV = "csv"  # CSV格式
    TSV = "tsv"  # TSV格式
    XML = "xml"  # XML格式
    EXCEL = "excel"  # Excel格式
    PARQUET = "parquet"  # Parquet格式


@dataclass
class ExportConfig:
    """导出配置"""
    format: ExportFormat
    file_path: Optional[str] = None
    fields: Optional[List[str]] = None  # 指定导出的字段
    include_headers: bool = True  # 是否包含表头
    encoding: str = 'utf-8'  # 编码


@dataclass
class ExportResult:
    """导出结果"""
    export_id: str
    file_path: Optional[str]
    records_exported: int
    export_time: float
    success: bool
    errors: List[Dict[str, Any]] = None


class DataExport:
    """
    数据导出器
    
    专注于数据导出、格式转换、批量导出
    """
    
    def __init__(self):
        self.export_history: List[ExportResult] = []
    
    def export_data(self, data: List[Dict[str, Any]], config: ExportConfig) -> ExportResult:
        """
        导出数据
        
        Args:
            data: 数据列表
            config: 导出配置
            
        Returns:
            导出结果
        """
        export_id = f"export_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        try:
            # 选择要导出的字段
            if config.fields:
                data = [{k: record.get(k) for k in config.fields if k in record} for record in data]
            
            # 根据格式导出
            if config.format == ExportFormat.JSON:
                result = self._export_json(data, config)
            elif config.format == ExportFormat.CSV:
                result = self._export_csv(data, config)
            elif config.format == ExportFormat.TSV:
                result = self._export_tsv(data, config)
            elif config.format == ExportFormat.XML:
                result = self._export_xml(data, config)
            else:
                result = self._export_json(data, config)  # 默认JSON
            
            end_time = datetime.utcnow()
            export_time = (end_time - start_time).total_seconds()
            
            export_result = ExportResult(
                export_id=export_id,
                file_path=config.file_path,
                records_exported=len(data),
                export_time=export_time,
                success=True
            )
            
            self.export_history.append(export_result)
            return export_result
        
        except Exception as e:
            logger.error(f"导出失败: {e}")
            end_time = datetime.utcnow()
            export_time = (end_time - start_time).total_seconds()
            
            export_result = ExportResult(
                export_id=export_id,
                file_path=config.file_path,
                records_exported=0,
                export_time=export_time,
                success=False,
                errors=[{'error': str(e)}]
            )
            
            self.export_history.append(export_result)
            return export_result
    
    def _export_json(self, data: List[Dict[str, Any]], config: ExportConfig) -> str:
        """导出为JSON"""
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        if config.file_path:
            with open(config.file_path, 'w', encoding=config.encoding) as f:
                f.write(json_str)
        
        return json_str
    
    def _export_csv(self, data: List[Dict[str, Any]], config: ExportConfig) -> str:
        """导出为CSV"""
        if not data:
            return ""
        
        # 获取所有字段
        fields = config.fields or list(data[0].keys())
        
        csv_lines = []
        
        # 表头
        if config.include_headers:
            csv_lines.append(','.join(fields))
        
        # 数据行
        for record in data:
            row = []
            for field in fields:
                value = record.get(field, '')
                # 处理包含逗号的值
                if isinstance(value, str) and ',' in value:
                    value = f'"{value}"'
                row.append(str(value))
            csv_lines.append(','.join(row))
        
        csv_str = '\n'.join(csv_lines)
        
        if config.file_path:
            with open(config.file_path, 'w', encoding=config.encoding) as f:
                f.write(csv_str)
        
        return csv_str
    
    def _export_tsv(self, data: List[Dict[str, Any]], config: ExportConfig) -> str:
        """导出为TSV"""
        if not data:
            return ""
        
        # 获取所有字段
        fields = config.fields or list(data[0].keys())
        
        tsv_lines = []
        
        # 表头
        if config.include_headers:
            tsv_lines.append('\t'.join(fields))
        
        # 数据行
        for record in data:
            row = [str(record.get(field, '')) for field in fields]
            tsv_lines.append('\t'.join(row))
        
        tsv_str = '\n'.join(tsv_lines)
        
        if config.file_path:
            with open(config.file_path, 'w', encoding=config.encoding) as f:
                f.write(tsv_str)
        
        return tsv_str
    
    def _export_xml(self, data: List[Dict[str, Any]], config: ExportConfig) -> str:
        """导出为XML"""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<data>']
        
        for record in data:
            xml_lines.append('  <record>')
            for key, value in record.items():
                if config.fields is None or key in config.fields:
                    xml_lines.append(f'    <{key}>{value}</{key}>')
            xml_lines.append('  </record>')
        
        xml_lines.append('</data>')
        xml_str = '\n'.join(xml_lines)
        
        if config.file_path:
            with open(config.file_path, 'w', encoding=config.encoding) as f:
                f.write(xml_str)
        
        return xml_str
    
    def export_to_string(self, data: List[Dict[str, Any]], format: ExportFormat) -> str:
        """
        导出为字符串
        
        Args:
            data: 数据列表
            format: 导出格式
            
        Returns:
            导出字符串
        """
        config = ExportConfig(format=format)
        
        if format == ExportFormat.JSON:
            return self._export_json(data, config)
        elif format == ExportFormat.CSV:
            return self._export_csv(data, config)
        elif format == ExportFormat.TSV:
            return self._export_tsv(data, config)
        elif format == ExportFormat.XML:
            return self._export_xml(data, config)
        else:
            return self._export_json(data, config)
    
    def get_export_stats(self) -> Dict[str, Any]:
        """
        获取导出统计
        
        Returns:
            导出统计
        """
        total_exports = len(self.export_history)
        successful_exports = sum(1 for e in self.export_history if e.success)
        total_records = sum(e.records_exported for e in self.export_history)
        
        if total_exports > 0:
            avg_time = sum(e.export_time for e in self.export_history) / total_exports
        else:
            avg_time = 0.0
        
        return {
            'total_exports': total_exports,
            'successful_exports': successful_exports,
            'failed_exports': total_exports - successful_exports,
            'total_records_exported': total_records,
            'success_rate': (successful_exports / total_exports * 100) if total_exports > 0 else 0.0,
            'average_export_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    exporter = DataExport()
    
    # 导出数据
    data = [
        {'id': 1, 'name': 'Alice', 'age': 25},
        {'id': 2, 'name': 'Bob', 'age': 30}
    ]
    
    config = ExportConfig(
        format=ExportFormat.JSON,
        file_path='output.json'
    )
    
    result = exporter.export_data(data, config)
    print(f"导出结果: 成功={result.success}, 导出记录数={result.records_exported}")


if __name__ == '__main__':
    main()
