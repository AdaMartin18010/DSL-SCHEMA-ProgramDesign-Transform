"""
数据模型转换器

专注于数据模型之间的转换（星型模式、雪花模式、Data Vault等）
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DataModelType(Enum):
    """数据模型类型"""
    STAR = "star"  # 星型模式
    SNOWFLAKE = "snowflake"  # 雪花模式
    DATA_VAULT = "datavault"  # Data Vault
    NORMALIZED = "normalized"  # 规范化模式
    DIMENSIONAL = "dimensional"  # 维度模式


@dataclass
class FactTable:
    """事实表定义"""
    name: str
    measures: List[Dict[str, Any]]  # 度量
    dimension_keys: List[Dict[str, Any]]  # 维度键
    grain: str  # 粒度


@dataclass
class DimensionTable:
    """维度表定义"""
    name: str
    attributes: List[Dict[str, Any]]  # 属性
    hierarchies: List[Dict[str, Any]]  # 层次结构
    scd_type: int  # 缓慢变化维度类型（1, 2, 3）


@dataclass
class Hub:
    """Hub定义（Data Vault）"""
    name: str
    business_key: str
    load_timestamp: bool = True


@dataclass
class Link:
    """Link定义（Data Vault）"""
    name: str
    hub_references: List[str]  # 引用的Hub
    load_timestamp: bool = True


@dataclass
class Satellite:
    """Satellite定义（Data Vault）"""
    name: str
    parent: str  # 父Hub或Link
    attributes: List[Dict[str, Any]]  # 描述性属性
    load_timestamp: bool = True
    load_end_timestamp: bool = True


class DataModelConverter:
    """
    数据模型转换器
    
    支持多种数据模型之间的转换
    """
    
    def __init__(self):
        self.conversion_rules = {}
        self._init_conversion_rules()
    
    def _init_conversion_rules(self):
        """初始化转换规则"""
        # 星型模式到PostgreSQL
        self.conversion_rules['star_to_postgresql'] = self._star_to_postgresql
        # 雪花模式到PostgreSQL
        self.conversion_rules['snowflake_to_postgresql'] = self._snowflake_to_postgresql
        # Data Vault到PostgreSQL
        self.conversion_rules['datavault_to_postgresql'] = self._datavault_to_postgresql
        # 星型模式到雪花模式
        self.conversion_rules['star_to_snowflake'] = self._star_to_snowflake
        # 雪花模式到星型模式
        self.conversion_rules['snowflake_to_star'] = self._snowflake_to_star
        # 星型模式到Data Vault
        self.conversion_rules['star_to_datavault'] = self._star_to_datavault
        # Data Vault到星型模式
        self.conversion_rules['datavault_to_star'] = self._datavault_to_star
    
    def convert(self, source_model: Dict[str, Any],
                source_type: DataModelType,
                target_type: str) -> Dict[str, Any]:
        """
        转换数据模型
        
        Args:
            source_model: 源数据模型
            source_type: 源模型类型
            target_type: 目标类型（postgresql, star, snowflake, datavault等）
            
        Returns:
            转换后的模型
        """
        rule_key = f"{source_type.value}_to_{target_type}"
        
        if rule_key in self.conversion_rules:
            return self.conversion_rules[rule_key](source_model)
        else:
            raise ValueError(f"不支持的转换规则: {rule_key}")
    
    def _star_to_postgresql(self, star_model: Dict[str, Any]) -> Dict[str, Any]:
        """星型模式到PostgreSQL转换"""
        result = {
            'tables': {},
            'relationships': [],
            'indexes': []
        }
        
        fact_tables = star_model.get('fact_tables', [])
        dimension_tables = star_model.get('dimension_tables', [])
        
        # 转换事实表
        for fact_table in fact_tables:
            table_name = fact_table.get('name', 'fact_table')
            result['tables'][table_name] = {
                'fields': {},
                'indexes': []
            }
            
            # 转换度量
            for measure in fact_table.get('measures', []):
                field_name = measure['name']
                result['tables'][table_name]['fields'][field_name] = {
                    'type': self._map_data_type(measure.get('data_type', 'decimal')),
                    'nullable': measure.get('nullable', False),
                    'description': measure.get('description', '')
                }
            
            # 转换维度键
            for dim_key in fact_table.get('dimension_keys', []):
                field_name = f"{dim_key['name']}_id"
                dim_table = dim_key.get('dimension_table', 'dimension_table')
                
                result['tables'][table_name]['fields'][field_name] = {
                    'type': 'integer',
                    'nullable': False,
                    'foreign_key': {
                        'references_table': dim_table,
                        'references_field': 'id'
                    }
                }
                
                # 添加外键关系
                result['relationships'].append({
                    'from_table': table_name,
                    'from_field': field_name,
                    'to_table': dim_table,
                    'to_field': 'id',
                    'type': 'foreign_key'
                })
                
                # 添加索引
                result['indexes'].append({
                    'table': table_name,
                    'name': f'idx_{table_name}_{field_name}',
                    'fields': [field_name],
                    'type': 'btree'
                })
        
        # 转换维度表
        for dim_table in dimension_tables:
            table_name = dim_table.get('name', 'dimension_table')
            result['tables'][table_name] = {
                'fields': {
                    'id': {
                        'type': 'integer',
                        'nullable': False,
                        'primary_key': True
                    }
                },
                'primary_key': 'id',
                'indexes': []
            }
            
            # 转换属性
            for attr in dim_table.get('attributes', []):
                field_name = attr['name']
                result['tables'][table_name]['fields'][field_name] = {
                    'type': self._map_data_type(attr.get('data_type', 'string')),
                    'nullable': attr.get('nullable', True),
                    'description': attr.get('description', '')
                }
            
            # 添加主键索引
            result['indexes'].append({
                'table': table_name,
                'name': f'idx_{table_name}_pk',
                'fields': ['id'],
                'type': 'btree',
                'unique': True
            })
        
        return result
    
    def _snowflake_to_postgresql(self, snowflake_model: Dict[str, Any]) -> Dict[str, Any]:
        """雪花模式到PostgreSQL转换"""
        # 雪花模式是规范化的维度表，需要处理维度层次
        result = self._star_to_postgresql(snowflake_model)
        
        # 处理维度层次关系
        dimension_tables = snowflake_model.get('dimension_tables', [])
        for dim_table in dimension_tables:
            table_name = dim_table.get('name', 'dimension_table')
            
            # 处理层次结构
            for hierarchy in dim_table.get('hierarchies', []):
                parent_level = hierarchy.get('parent_level')
                child_level = hierarchy.get('child_level')
                
                if parent_level and child_level:
                    # 添加父级外键
                    parent_field = f"{parent_level}_id"
                    result['tables'][table_name]['fields'][parent_field] = {
                        'type': 'integer',
                        'nullable': True,
                        'foreign_key': {
                            'references_table': table_name,
                            'references_field': 'id'
                        }
                    }
        
        return result
    
    def _datavault_to_postgresql(self, datavault_model: Dict[str, Any]) -> Dict[str, Any]:
        """Data Vault到PostgreSQL转换"""
        result = {
            'tables': {},
            'relationships': [],
            'indexes': []
        }
        
        hubs = datavault_model.get('hubs', [])
        links = datavault_model.get('links', [])
        satellites = datavault_model.get('satellites', [])
        
        # 转换Hub
        for hub in hubs:
            hub_name = hub.get('name', 'hub')
            business_key = hub.get('business_key', 'business_key')
            
            result['tables'][hub_name] = {
                'fields': {
                    'hub_key': {
                        'type': 'varchar(255)',
                        'nullable': False,
                        'primary_key': True
                    },
                    business_key: {
                        'type': 'varchar(255)',
                        'nullable': False
                    }
                },
                'primary_key': 'hub_key',
                'indexes': []
            }
            
            if hub.get('load_timestamp', True):
                result['tables'][hub_name]['fields']['load_timestamp'] = {
                    'type': 'timestamp',
                    'nullable': False,
                    'default': 'CURRENT_TIMESTAMP'
                }
            
            # 添加业务键索引
            result['indexes'].append({
                'table': hub_name,
                'name': f'idx_{hub_name}_business_key',
                'fields': [business_key],
                'type': 'btree',
                'unique': True
            })
        
        # 转换Link
        for link in links:
            link_name = link.get('name', 'link')
            result['tables'][link_name] = {
                'fields': {
                    'link_key': {
                        'type': 'varchar(255)',
                        'nullable': False,
                        'primary_key': True
                    }
                },
                'primary_key': 'link_key',
                'indexes': []
            }
            
            if link.get('load_timestamp', True):
                result['tables'][link_name]['fields']['load_timestamp'] = {
                    'type': 'timestamp',
                    'nullable': False,
                    'default': 'CURRENT_TIMESTAMP'
                }
            
            # 添加Hub外键
            for hub_ref in link.get('hub_references', []):
                field_name = f"{hub_ref}_key"
                result['tables'][link_name]['fields'][field_name] = {
                    'type': 'varchar(255)',
                    'nullable': False,
                    'foreign_key': {
                        'references_table': hub_ref,
                        'references_field': 'hub_key'
                    }
                }
                
                result['relationships'].append({
                    'from_table': link_name,
                    'from_field': field_name,
                    'to_table': hub_ref,
                    'to_field': 'hub_key',
                    'type': 'foreign_key'
                })
        
        # 转换Satellite
        for satellite in satellites:
            sat_name = satellite.get('name', 'satellite')
            parent_name = satellite.get('parent', 'hub')
            parent_key = f"{parent_name}_key"
            
            result['tables'][sat_name] = {
                'fields': {
                    parent_key: {
                        'type': 'varchar(255)',
                        'nullable': False
                    }
                },
                'primary_key': f"{parent_key},load_timestamp",
                'indexes': []
            }
            
            if satellite.get('load_timestamp', True):
                result['tables'][sat_name]['fields']['load_timestamp'] = {
                    'type': 'timestamp',
                    'nullable': False,
                    'default': 'CURRENT_TIMESTAMP'
                }
            
            if satellite.get('load_end_timestamp', True):
                result['tables'][sat_name]['fields']['load_end_timestamp'] = {
                    'type': 'timestamp',
                    'nullable': True
                }
            
            # 添加外键关系
            result['relationships'].append({
                'from_table': sat_name,
                'from_field': parent_key,
                'to_table': parent_name,
                'to_field': parent_key if 'link' in parent_name.lower() else 'hub_key',
                'type': 'foreign_key'
            })
            
            # 添加描述性属性
            for attr in satellite.get('attributes', []):
                field_name = attr['name']
                result['tables'][sat_name]['fields'][field_name] = {
                    'type': self._map_data_type(attr.get('data_type', 'string')),
                    'nullable': attr.get('nullable', True),
                    'description': attr.get('description', '')
                }
        
        return result
    
    def _star_to_snowflake(self, star_model: Dict[str, Any]) -> Dict[str, Any]:
        """星型模式到雪花模式转换"""
        # 规范化维度表
        result = star_model.copy()
        
        dimension_tables = result.get('dimension_tables', [])
        
        # 为每个维度表添加层次结构
        for dim_table in dimension_tables:
            # 识别可以规范化的属性
            attributes = dim_table.get('attributes', [])
            
            # 创建子维度表（简化实现）
            hierarchies = []
            for attr in attributes:
                if 'parent' in attr or 'level' in attr:
                    hierarchies.append({
                        'parent_level': attr.get('parent_level', ''),
                        'child_level': attr.get('name', ''),
                        'relationship': 'parent-child'
                    })
            
            dim_table['hierarchies'] = hierarchies
        
        return result
    
    def _snowflake_to_star(self, snowflake_model: Dict[str, Any]) -> Dict[str, Any]:
        """雪花模式到星型模式转换"""
        # 反规范化维度表
        result = snowflake_model.copy()
        
        dimension_tables = result.get('dimension_tables', [])
        
        # 合并层次结构到主维度表
        for dim_table in dimension_tables:
            attributes = dim_table.get('attributes', [])
            hierarchies = dim_table.get('hierarchies', [])
            
            # 将层次结构属性添加到主表
            for hierarchy in hierarchies:
                child_level = hierarchy.get('child_level', '')
                if child_level and child_level not in [attr['name'] for attr in attributes]:
                    attributes.append({
                        'name': child_level,
                        'data_type': 'string',
                        'nullable': True
                    })
            
            dim_table['attributes'] = attributes
            dim_table['hierarchies'] = []  # 清除层次结构
        
        return result
    
    def _star_to_datavault(self, star_model: Dict[str, Any]) -> Dict[str, Any]:
        """星型模式到Data Vault转换"""
        result = {
            'hubs': [],
            'links': [],
            'satellites': []
        }
        
        fact_tables = star_model.get('fact_tables', [])
        dimension_tables = star_model.get('dimension_tables', [])
        
        # 为每个维度表创建Hub
        for dim_table in dimension_tables:
            table_name = dim_table.get('name', 'dimension_table')
            business_key = dim_table.get('business_key', 'id')
            
            result['hubs'].append({
                'name': f"{table_name}_hub",
                'business_key': business_key,
                'load_timestamp': True
            })
            
            # 创建Satellite存储维度属性
            result['satellites'].append({
                'name': f"{table_name}_sat",
                'parent': f"{table_name}_hub",
                'attributes': dim_table.get('attributes', []),
                'load_timestamp': True,
                'load_end_timestamp': True
            })
        
        # 为每个事实表创建Link
        for fact_table in fact_tables:
            table_name = fact_table.get('name', 'fact_table')
            dimension_keys = fact_table.get('dimension_keys', [])
            
            hub_refs = [f"{dk.get('dimension_table', 'dim')}_hub" for dk in dimension_keys]
            
            result['links'].append({
                'name': f"{table_name}_link",
                'hub_references': hub_refs,
                'load_timestamp': True
            })
            
            # 创建Satellite存储度量
            result['satellites'].append({
                'name': f"{table_name}_sat",
                'parent': f"{table_name}_link",
                'attributes': fact_table.get('measures', []),
                'load_timestamp': True,
                'load_end_timestamp': True
            })
        
        return result
    
    def _datavault_to_star(self, datavault_model: Dict[str, Any]) -> Dict[str, Any]:
        """Data Vault到星型模式转换"""
        result = {
            'fact_tables': [],
            'dimension_tables': []
        }
        
        hubs = datavault_model.get('hubs', [])
        links = datavault_model.get('links', [])
        satellites = datavault_model.get('satellites', [])
        
        # 为每个Hub创建维度表
        for hub in hubs:
            hub_name = hub.get('name', 'hub')
            business_key = hub.get('business_key', 'business_key')
            
            # 查找对应的Satellite
            hub_satellites = [s for s in satellites if s.get('parent') == hub_name]
            
            # 合并所有属性
            all_attributes = []
            for sat in hub_satellites:
                all_attributes.extend(sat.get('attributes', []))
            
            result['dimension_tables'].append({
                'name': hub_name.replace('_hub', '_dim'),
                'business_key': business_key,
                'attributes': all_attributes
            })
        
        # 为每个Link创建事实表
        for link in links:
            link_name = link.get('name', 'link')
            hub_refs = link.get('hub_references', [])
            
            # 查找对应的Satellite
            link_satellites = [s for s in satellites if s.get('parent') == link_name]
            
            # 合并所有度量
            all_measures = []
            for sat in link_satellites:
                all_measures.extend(sat.get('attributes', []))
            
            # 创建维度键
            dimension_keys = []
            for hub_ref in hub_refs:
                dim_name = hub_ref.replace('_hub', '_dim')
                dimension_keys.append({
                    'name': dim_name,
                    'dimension_table': dim_name
                })
            
            result['fact_tables'].append({
                'name': link_name.replace('_link', '_fact'),
                'measures': all_measures,
                'dimension_keys': dimension_keys
            })
        
        return result
    
    def _map_data_type(self, data_type: str) -> str:
        """映射数据类型到PostgreSQL类型"""
        type_mapping = {
            'string': 'VARCHAR(255)',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'bigint': 'BIGINT',
            'decimal': 'DECIMAL(18, 2)',
            'numeric': 'NUMERIC(18, 2)',
            'float': 'REAL',
            'double': 'DOUBLE PRECISION',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'timestamp': 'TIMESTAMP',
            'json': 'JSONB',
            'array': 'TEXT[]'
        }
        
        return type_mapping.get(data_type.lower(), 'TEXT')
    
    def generate_sql_ddl(self, converted_model: Dict[str, Any]) -> str:
        """
        生成PostgreSQL DDL语句
        
        Args:
            converted_model: 转换后的模型
            
        Returns:
            DDL语句字符串
        """
        sql_lines = []
        
        tables = converted_model.get('tables', {})
        
        for table_name, table_def in tables.items():
            # CREATE TABLE语句
            sql_lines.append(f"CREATE TABLE {table_name} (")
            
            fields = []
            for field_name, field_def in table_def.get('fields', {}).items():
                field_sql = f"  {field_name} {field_def.get('type', 'TEXT')}"
                
                if not field_def.get('nullable', True):
                    field_sql += " NOT NULL"
                
                if 'default' in field_def:
                    field_sql += f" DEFAULT {field_def['default']}"
                
                fields.append(field_sql)
            
            sql_lines.append(",\n".join(fields))
            
            # 主键
            if 'primary_key' in table_def:
                pk = table_def['primary_key']
                if isinstance(pk, str):
                    sql_lines.append(f",\n  PRIMARY KEY ({pk})")
                elif isinstance(pk, list):
                    sql_lines.append(f",\n  PRIMARY KEY ({', '.join(pk)})")
            
            sql_lines.append("\n);\n")
        
        # 外键约束
        relationships = converted_model.get('relationships', [])
        for rel in relationships:
            sql_lines.append(
                f"ALTER TABLE {rel['from_table']} "
                f"ADD CONSTRAINT fk_{rel['from_table']}_{rel['from_field']} "
                f"FOREIGN KEY ({rel['from_field']}) "
                f"REFERENCES {rel['to_table']} ({rel['to_field']});\n"
            )
        
        # 索引
        indexes = converted_model.get('indexes', [])
        for idx in indexes:
            idx_name = idx.get('name', f"idx_{idx['table']}_{'_'.join(idx['fields'])}")
            idx_type = idx.get('type', 'btree')
            unique = 'UNIQUE ' if idx.get('unique', False) else ''
            
            sql_lines.append(
                f"CREATE {unique}INDEX {idx_name} ON {idx['table']} "
                f"USING {idx_type} ({', '.join(idx['fields'])});\n"
            )
        
        return "".join(sql_lines)


class DataModelValidator:
    """数据模型验证器"""
    
    def validate_star_model(self, star_model: Dict[str, Any]) -> Dict[str, Any]:
        """验证星型模式模型"""
        errors = []
        warnings = []
        
        fact_tables = star_model.get('fact_tables', [])
        dimension_tables = star_model.get('dimension_tables', [])
        
        # 检查事实表
        if not fact_tables:
            errors.append("星型模式必须至少包含一个事实表")
        
        for fact_table in fact_tables:
            if not fact_table.get('measures'):
                warnings.append(f"事实表 {fact_table.get('name')} 没有度量")
            
            if not fact_table.get('dimension_keys'):
                errors.append(f"事实表 {fact_table.get('name')} 没有维度键")
        
        # 检查维度表
        if not dimension_tables:
            errors.append("星型模式必须至少包含一个维度表")
        
        for dim_table in dimension_tables:
            if not dim_table.get('attributes'):
                warnings.append(f"维度表 {dim_table.get('name')} 没有属性")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def validate_datavault_model(self, datavault_model: Dict[str, Any]) -> Dict[str, Any]:
        """验证Data Vault模型"""
        errors = []
        warnings = []
        
        hubs = datavault_model.get('hubs', [])
        links = datavault_model.get('links', [])
        satellites = datavault_model.get('satellites', [])
        
        # 检查Hub
        if not hubs:
            errors.append("Data Vault模型必须至少包含一个Hub")
        
        # 检查Link引用的Hub是否存在
        hub_names = {hub.get('name') for hub in hubs}
        for link in links:
            for hub_ref in link.get('hub_references', []):
                if hub_ref not in hub_names:
                    errors.append(f"Link {link.get('name')} 引用了不存在的Hub: {hub_ref}")
        
        # 检查Satellite的父节点是否存在
        all_parents = hub_names | {link.get('name') for link in links}
        for satellite in satellites:
            parent = satellite.get('parent')
            if parent not in all_parents:
                errors.append(f"Satellite {satellite.get('name')} 引用了不存在的父节点: {parent}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


def main():
    """主函数 - 示例用法"""
    converter = DataModelConverter()
    validator = DataModelValidator()
    
    # 示例：星型模式
    star_model = {
        'fact_tables': [{
            'name': 'sales_fact',
            'measures': [
                {'name': 'amount', 'data_type': 'decimal'},
                {'name': 'quantity', 'data_type': 'integer'}
            ],
            'dimension_keys': [
                {'name': 'customer', 'dimension_table': 'customer_dim'},
                {'name': 'product', 'dimension_table': 'product_dim'}
            ]
        }],
        'dimension_tables': [{
            'name': 'customer_dim',
            'attributes': [
                {'name': 'customer_name', 'data_type': 'string'},
                {'name': 'region', 'data_type': 'string'}
            ]
        }]
    }
    
    # 验证
    validation = validator.validate_star_model(star_model)
    print(f"验证结果: {validation}")
    
    # 转换
    result = converter.convert(star_model, DataModelType.STAR, 'postgresql')
    
    # 生成DDL
    ddl = converter.generate_sql_ddl(result)
    print(ddl)


if __name__ == '__main__':
    main()
