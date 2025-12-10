"""
数据转换配置模块

专注于数据转换配置、配置管理、配置验证
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """配置类型"""
    TRANSFORMATION = "transformation"  # 转换配置
    VALIDATION = "validation"  # 验证配置
    MAPPING = "mapping"  # 映射配置
    ROUTING = "routing"  # 路由配置
    CACHING = "caching"  # 缓存配置
    SCHEDULING = "scheduling"  # 调度配置


@dataclass
class TransformationConfig:
    """转换配置"""
    config_id: str
    config_name: str
    config_type: ConfigType
    config_data: Dict[str, Any]
    version: str
    created_at: datetime
    updated_at: datetime


class DataTransformationConfig:
    """
    数据转换配置器
    
    专注于数据转换配置、配置管理、配置验证
    """
    
    def __init__(self):
        self.configs: Dict[str, TransformationConfig] = {}
        self.config_versions: Dict[str, List[str]] = {}  # config_id -> versions
    
    def create_config(self, config_data: Dict[str, Any]) -> TransformationConfig:
        """
        创建配置
        
        Args:
            config_data: 配置数据
            
        Returns:
            转换配置对象
        """
        config_id = config_data.get('config_id', f"config_{datetime.utcnow().timestamp()}")
        version = config_data.get('version', '1.0.0')
        
        config = TransformationConfig(
            config_id=config_id,
            config_name=config_data.get('config_name', ''),
            config_type=ConfigType(config_data.get('config_type', 'transformation')),
            config_data=config_data.get('config_data', {}),
            version=version,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.configs[config_id] = config
        
        # 记录版本
        if config_id not in self.config_versions:
            self.config_versions[config_id] = []
        self.config_versions[config_id].append(version)
        
        return config
    
    def update_config(self, config_id: str, config_data: Dict[str, Any]) -> TransformationConfig:
        """
        更新配置
        
        Args:
            config_id: 配置ID
            config_data: 配置数据
            
        Returns:
            更新后的配置对象
        """
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"配置不存在: {config_id}")
        
        # 更新配置数据
        if 'config_data' in config_data:
            config.config_data.update(config_data['config_data'])
        
        if 'config_name' in config_data:
            config.config_name = config_data['config_name']
        
        # 更新版本
        if 'version' in config_data:
            new_version = config_data['version']
            if new_version not in self.config_versions[config_id]:
                self.config_versions[config_id].append(new_version)
            config.version = new_version
        
        config.updated_at = datetime.utcnow()
        
        return config
    
    def get_config(self, config_id: str, version: Optional[str] = None) -> Optional[TransformationConfig]:
        """
        获取配置
        
        Args:
            config_id: 配置ID
            version: 版本（可选）
            
        Returns:
            配置对象
        """
        config = self.configs.get(config_id)
        if not config:
            return None
        
        if version and config.version != version:
            # 这里简化处理，实际应该支持多版本存储
            return None
        
        return config
    
    def validate_config(self, config_id: str) -> Dict[str, Any]:
        """
        验证配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            验证结果
        """
        config = self.configs.get(config_id)
        if not config:
            return {
                'valid': False,
                'errors': [f"配置不存在: {config_id}"]
            }
        
        errors = []
        
        # 验证配置类型
        if not config.config_type:
            errors.append("配置类型不能为空")
        
        # 验证配置数据
        if not config.config_data:
            errors.append("配置数据不能为空")
        
        # 根据配置类型进行特定验证
        if config.config_type == ConfigType.TRANSFORMATION:
            if 'transformation_rules' not in config.config_data:
                errors.append("转换配置缺少转换规则")
        
        elif config.config_type == ConfigType.VALIDATION:
            if 'validation_rules' not in config.config_data:
                errors.append("验证配置缺少验证规则")
        
        elif config.config_type == ConfigType.MAPPING:
            if 'field_mapping' not in config.config_data:
                errors.append("映射配置缺少字段映射")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def export_config(self, config_id: str, file_path: str) -> bool:
        """
        导出配置
        
        Args:
            config_id: 配置ID
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        config = self.configs.get(config_id)
        if not config:
            return False
        
        try:
            config_dict = asdict(config)
            # 转换datetime为字符串
            config_dict['created_at'] = config.created_at.isoformat()
            config_dict['updated_at'] = config.updated_at.isoformat()
            config_dict['config_type'] = config.config_type.value
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, file_path: str) -> Optional[TransformationConfig]:
        """
        导入配置
        
        Args:
            file_path: 文件路径
            
        Returns:
            配置对象
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 转换字符串为datetime
            config_dict['created_at'] = datetime.fromisoformat(config_dict['created_at'])
            config_dict['updated_at'] = datetime.fromisoformat(config_dict['updated_at'])
            config_dict['config_type'] = ConfigType(config_dict['config_type'])
            
            config = TransformationConfig(**config_dict)
            self.configs[config.config_id] = config
            
            # 记录版本
            if config.config_id not in self.config_versions:
                self.config_versions[config.config_id] = []
            if config.version not in self.config_versions[config.config_id]:
                self.config_versions[config.config_id].append(config.version)
            
            return config
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return None
    
    def get_config_list(self) -> List[Dict[str, Any]]:
        """
        获取配置列表
        
        Returns:
            配置列表
        """
        return [
            {
                'config_id': c.config_id,
                'config_name': c.config_name,
                'config_type': c.config_type.value,
                'version': c.version,
                'created_at': c.created_at.isoformat(),
                'updated_at': c.updated_at.isoformat()
            }
            for c in self.configs.values()
        ]


def main():
    """主函数 - 示例用法"""
    config_manager = DataTransformationConfig()
    
    # 创建配置
    config = config_manager.create_config({
        'config_name': '示例配置',
        'config_type': 'transformation',
        'config_data': {
            'transformation_rules': []
        }
    })
    
    print(f"配置已创建: {config.config_id}")


if __name__ == '__main__':
    main()
