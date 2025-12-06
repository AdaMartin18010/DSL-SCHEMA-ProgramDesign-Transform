"""
数据目录管理器

专注于数据目录、元数据管理和数据血缘追踪
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DataAssetType(Enum):
    """数据资产类型"""
    TABLE = "table"
    VIEW = "view"
    COLUMN = "column"
    SCHEMA = "schema"
    DATABASE = "database"
    PIPELINE = "pipeline"
    REPORT = "report"


class LineageType(Enum):
    """血缘类型"""
    DIRECT = "direct"  # 直接血缘
    INDIRECT = "indirect"  # 间接血缘
    TRANSFORM = "transform"  # 转换血缘


@dataclass
class DataAsset:
    """数据资产"""
    asset_id: str
    name: str
    asset_type: DataAssetType
    schema_id: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class DataLineage:
    """数据血缘"""
    lineage_id: str
    source_asset_id: str
    target_asset_id: str
    lineage_type: LineageType
    transformation: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class Metadata:
    """元数据"""
    metadata_id: str
    asset_id: str
    key: str
    value: Any
    data_type: str
    description: Optional[str] = None


class DataCatalogManager:
    """
    数据目录管理器
    
    专注于数据目录、元数据管理和数据血缘追踪
    """
    
    def __init__(self):
        self.assets: Dict[str, DataAsset] = {}
        self.lineages: Dict[str, DataLineage] = {}
        self.metadata_store: Dict[str, List[Metadata]] = {}
    
    def register_asset(self, asset_config: Dict[str, Any]) -> DataAsset:
        """
        注册数据资产
        
        Args:
            asset_config: 资产配置
            
        Returns:
            数据资产对象
        """
        asset_id = asset_config.get('asset_id', f"asset_{datetime.utcnow().timestamp()}")
        
        asset = DataAsset(
            asset_id=asset_id,
            name=asset_config.get('name', ''),
            asset_type=DataAssetType(asset_config.get('asset_type', 'table')),
            schema_id=asset_config.get('schema_id'),
            description=asset_config.get('description'),
            tags=asset_config.get('tags', []),
            metadata=asset_config.get('metadata', {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.assets[asset_id] = asset
        return asset
    
    def add_lineage(self, lineage_config: Dict[str, Any]) -> DataLineage:
        """
        添加数据血缘
        
        Args:
            lineage_config: 血缘配置
            
        Returns:
            数据血缘对象
        """
        lineage_id = lineage_config.get('lineage_id', f"lineage_{datetime.utcnow().timestamp()}")
        source_asset_id = lineage_config.get('source_asset_id')
        target_asset_id = lineage_config.get('target_asset_id')
        
        # 验证资产存在
        if source_asset_id not in self.assets:
            raise ValueError(f"源资产不存在: {source_asset_id}")
        
        if target_asset_id not in self.assets:
            raise ValueError(f"目标资产不存在: {target_asset_id}")
        
        lineage = DataLineage(
            lineage_id=lineage_id,
            source_asset_id=source_asset_id,
            target_asset_id=target_asset_id,
            lineage_type=LineageType(lineage_config.get('lineage_type', 'direct')),
            transformation=lineage_config.get('transformation'),
            metadata=lineage_config.get('metadata', {})
        )
        
        self.lineages[lineage_id] = lineage
        return lineage
    
    def get_lineage(self, asset_id: str, direction: str = 'downstream') -> List[DataLineage]:
        """
        获取数据血缘
        
        Args:
            asset_id: 资产ID
            direction: 方向（downstream下游，upstream上游）
            
        Returns:
            血缘列表
        """
        if direction == 'downstream':
            # 下游血缘（该资产作为源）
            return [l for l in self.lineages.values() if l.source_asset_id == asset_id]
        else:
            # 上游血缘（该资产作为目标）
            return [l for l in self.lineages.values() if l.target_asset_id == asset_id]
    
    def get_full_lineage(self, asset_id: str) -> Dict[str, Any]:
        """
        获取完整血缘（包括上游和下游）
        
        Args:
            asset_id: 资产ID
            
        Returns:
            完整血缘信息
        """
        upstream = self.get_lineage(asset_id, 'upstream')
        downstream = self.get_lineage(asset_id, 'downstream')
        
        return {
            'asset_id': asset_id,
            'upstream': [self._lineage_to_dict(l) for l in upstream],
            'downstream': [self._lineage_to_dict(l) for l in downstream]
        }
    
    def _lineage_to_dict(self, lineage: DataLineage) -> Dict[str, Any]:
        """转换血缘为字典"""
        return {
            'lineage_id': lineage.lineage_id,
            'source_asset_id': lineage.source_asset_id,
            'target_asset_id': lineage.target_asset_id,
            'lineage_type': lineage.lineage_type.value,
            'transformation': lineage.transformation
        }
    
    def add_metadata(self, asset_id: str, key: str, value: Any,
                     data_type: str = 'string', description: Optional[str] = None):
        """
        添加元数据
        
        Args:
            asset_id: 资产ID
            key: 元数据键
            value: 元数据值
            data_type: 数据类型
            description: 描述
        """
        if asset_id not in self.assets:
            raise ValueError(f"资产不存在: {asset_id}")
        
        metadata = Metadata(
            metadata_id=f"metadata_{datetime.utcnow().timestamp()}",
            asset_id=asset_id,
            key=key,
            value=value,
            data_type=data_type,
            description=description
        )
        
        if asset_id not in self.metadata_store:
            self.metadata_store[asset_id] = []
        
        self.metadata_store[asset_id].append(metadata)
    
    def get_metadata(self, asset_id: str) -> Dict[str, Any]:
        """
        获取元数据
        
        Args:
            asset_id: 资产ID
            
        Returns:
            元数据字典
        """
        if asset_id not in self.metadata_store:
            return {}
        
        metadata_list = self.metadata_store[asset_id]
        return {m.key: m.value for m in metadata_list}
    
    def search_assets(self, query: str, asset_type: Optional[DataAssetType] = None) -> List[DataAsset]:
        """
        搜索数据资产
        
        Args:
            query: 搜索查询
            asset_type: 资产类型（可选）
            
        Returns:
            匹配的资产列表
        """
        results = []
        
        for asset in self.assets.values():
            if asset_type and asset.asset_type != asset_type:
                continue
            
            # 搜索名称和描述
            if query.lower() in asset.name.lower():
                results.append(asset)
            elif asset.description and query.lower() in asset.description.lower():
                results.append(asset)
            elif asset.tags and any(query.lower() in tag.lower() for tag in asset.tags):
                results.append(asset)
        
        return results
    
    def get_asset_dependencies(self, asset_id: str) -> Dict[str, Any]:
        """
        获取资产依赖关系
        
        Args:
            asset_id: 资产ID
            
        Returns:
            依赖关系信息
        """
        if asset_id not in self.assets:
            return {}
        
        upstream_lineages = self.get_lineage(asset_id, 'upstream')
        downstream_lineages = self.get_lineage(asset_id, 'downstream')
        
        dependencies = {
            'asset_id': asset_id,
            'depends_on': [l.source_asset_id for l in upstream_lineages],
            'used_by': [l.target_asset_id for l in downstream_lineages],
            'total_dependencies': len(upstream_lineages),
            'total_dependents': len(downstream_lineages)
        }
        
        return dependencies


def main():
    """主函数 - 示例用法"""
    catalog = DataCatalogManager()
    
    # 注册数据资产
    table_asset = catalog.register_asset({
        'name': 'sales_fact',
        'asset_type': 'table',
        'description': '销售事实表',
        'tags': ['sales', 'fact', 'warehouse']
    })
    
    view_asset = catalog.register_asset({
        'name': 'sales_summary',
        'asset_type': 'view',
        'description': '销售汇总视图',
        'tags': ['sales', 'summary']
    })
    
    print(f"注册资产: {table_asset.asset_id}")
    
    # 添加血缘
    lineage = catalog.add_lineage({
        'source_asset_id': table_asset.asset_id,
        'target_asset_id': view_asset.asset_id,
        'lineage_type': 'transform',
        'transformation': 'SELECT SUM(amount) FROM sales_fact GROUP BY region'
    })
    
    print(f"添加血缘: {lineage.lineage_id}")
    
    # 获取完整血缘
    full_lineage = catalog.get_full_lineage(table_asset.asset_id)
    print(f"完整血缘: {full_lineage}")


if __name__ == '__main__':
    main()
