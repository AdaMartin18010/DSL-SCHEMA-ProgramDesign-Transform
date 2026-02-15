"""
智慧家居Schema转换器

专注于Matter/Zigbee转换、场景联动、PostgreSQL存储
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import lru_cache

from .logger import logger
from .exceptions import (
    ConversionError,
    DeviceNotFoundError,
    SceneNotFoundError,
    ValidationError
)


class DeviceProtocol(Enum):
    """设备协议"""
    MATTER = "matter"
    ZIGBEE = "zigbee"
    Z_WAVE = "zwave"
    THREAD = "thread"


class DeviceType(Enum):
    """设备类型"""
    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    THERMOSTAT = "thermostat"
    DOOR_LOCK = "door_lock"
    CAMERA = "camera"


@dataclass
class Device:
    """设备"""
    device_id: str
    name: str
    device_type: DeviceType
    protocol: DeviceProtocol
    state: Dict[str, Any]
    capabilities: List[str]
    metadata: Dict[str, Any] = None


@dataclass
class Scene:
    """场景"""
    scene_id: str
    name: str
    description: Optional[str] = None
    triggers: List[Dict[str, Any]] = None
    actions: List[Dict[str, Any]] = None
    conditions: List[Dict[str, Any]] = None
    enabled: bool = True


class SmartHomeConverter:
    """
    智慧家居转换器
    
    专注于Matter/Zigbee转换、场景联动、PostgreSQL存储
    """
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.scenes: Dict[str, Scene] = {}
        self.conversion_rules: Dict[str, Dict[str, Any]] = {}
        self._init_conversion_rules()
        logger.info("SmartHomeConverter initialized")
    
    def _init_conversion_rules(self):
        """初始化转换规则"""
        # Matter到Zigbee转换规则
        self.conversion_rules['matter_to_zigbee'] = {
            'OnOff': {
                'cluster': 'OnOff',
                'attribute_mapping': {
                    'OnOff': 'OnOff'
                }
            },
            'LevelControl': {
                'cluster': 'LevelControl',
                'attribute_mapping': {
                    'CurrentLevel': 'CurrentLevel'
                }
            },
            'ColorControl': {
                'cluster': 'ColorControl',
                'attribute_mapping': {
                    'CurrentHue': 'CurrentHue',
                    'CurrentSaturation': 'CurrentSaturation',
                    'CurrentX': 'CurrentX',
                    'CurrentY': 'CurrentY'
                }
            }
        }
        
        # Zigbee到Matter转换规则
        self.conversion_rules['zigbee_to_matter'] = {
            'OnOff': {
                'cluster': 'OnOff',
                'attribute_mapping': {
                    'OnOff': 'OnOff'
                }
            },
            'LevelControl': {
                'cluster': 'LevelControl',
                'attribute_mapping': {
                    'CurrentLevel': 'CurrentLevel'
                }
            },
            'ColorControl': {
                'cluster': 'ColorControl',
                'attribute_mapping': {
                    'CurrentHue': 'CurrentHue',
                    'CurrentSaturation': 'CurrentSaturation',
                    'CurrentX': 'CurrentX',
                    'CurrentY': 'CurrentY'
                }
            }
        }
    
    def convert_matter_to_zigbee(self, matter_device: Dict[str, Any]) -> Dict[str, Any]:
        """
        Matter到Zigbee转换
        
        Args:
            matter_device: Matter设备数据
            
        Returns:
            Zigbee设备数据
            
        Raises:
            ConversionError: 转换失败时抛出
            ValidationError: 输入验证失败时抛出
        """
        try:
            # 验证输入
            if not matter_device:
                raise ValidationError("Matter设备数据不能为空")
            
            device_id = matter_device.get('device_id')
            if not device_id:
                raise ValidationError("设备ID不能为空")
            
            logger.debug(f"Converting Matter device {device_id} to Zigbee")
            
            zigbee_device = {
                'ieee_address': device_id,
                'friendly_name': matter_device.get('name', ''),
                'type': self._map_device_type(matter_device.get('device_type')),
                'clusters': []
            }
            
            # 转换集群
            matter_clusters = matter_device.get('clusters', [])
            converted_clusters = 0
            
            for cluster in matter_clusters:
                cluster_id = cluster.get('cluster_id')
                cluster_name = cluster.get('cluster_name')
                
                if cluster_name in self.conversion_rules['matter_to_zigbee']:
                    rule = self.conversion_rules['matter_to_zigbee'][cluster_name]
                    zigbee_cluster = {
                        'cluster': rule['cluster'],
                        'attributes': {}
                    }
                    
                    # 转换属性
                    matter_attributes = cluster.get('attributes', {})
                    attribute_mapping = rule['attribute_mapping']
                    
                    for matter_attr, zigbee_attr in attribute_mapping.items():
                        if matter_attr in matter_attributes:
                            zigbee_cluster['attributes'][zigbee_attr] = matter_attributes[matter_attr]
                    
                    zigbee_device['clusters'].append(zigbee_cluster)
                    converted_clusters += 1
                else:
                    logger.warning(f"未找到集群 {cluster_name} 的转换规则")
            
            logger.info(f"成功转换设备 {device_id}，转换了 {converted_clusters} 个集群")
            return zigbee_device
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Matter到Zigbee转换失败: {str(e)}", exc_info=True)
            raise ConversionError(f"转换失败: {str(e)}") from e
    
    def convert_zigbee_to_matter(self, zigbee_device: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zigbee到Matter转换
        
        Args:
            zigbee_device: Zigbee设备数据
            
        Returns:
            Matter设备数据
        """
        matter_device = {
            'device_id': zigbee_device.get('ieee_address', ''),
            'name': zigbee_device.get('friendly_name', ''),
            'device_type': self._map_device_type(zigbee_device.get('type')),
            'clusters': []
        }
        
        # 转换集群
        zigbee_clusters = zigbee_device.get('clusters', [])
        for cluster in zigbee_clusters:
            cluster_name = cluster.get('cluster')
            
            if cluster_name in self.conversion_rules['zigbee_to_matter']:
                rule = self.conversion_rules['zigbee_to_matter'][cluster_name]
                matter_cluster = {
                    'cluster_id': self._get_cluster_id(cluster_name),
                    'cluster_name': cluster_name,
                    'attributes': {}
                }
                
                # 转换属性
                zigbee_attributes = cluster.get('attributes', {})
                attribute_mapping = rule['attribute_mapping']
                
                for zigbee_attr, matter_attr in attribute_mapping.items():
                    if zigbee_attr in zigbee_attributes:
                        matter_cluster['attributes'][matter_attr] = zigbee_attributes[zigbee_attr]
                
                matter_device['clusters'].append(matter_cluster)
        
        return matter_device
    
    @lru_cache(maxsize=128)
    def _map_device_type(self, device_type: str) -> str:
        """映射设备类型（带缓存）"""
        type_mapping = {
            'OnOffLight': 'light',
            'DimmableLight': 'light',
            'ColorLight': 'light',
            'OnOffSwitch': 'switch',
            'DoorLock': 'door_lock',
            'Thermostat': 'thermostat'
        }
        return type_mapping.get(device_type, device_type)
    
    def _get_cluster_id(self, cluster_name: str) -> int:
        """获取集群ID"""
        cluster_ids = {
            'OnOff': 0x0006,
            'LevelControl': 0x0008,
            'ColorControl': 0x0300,
            'DoorLock': 0x0101,
            'Thermostat': 0x0201
        }
        return cluster_ids.get(cluster_name, 0)
    
    def create_scene(self, scene_config: Dict[str, Any]) -> Scene:
        """
        创建场景
        
        Args:
            scene_config: 场景配置
            
        Returns:
            场景对象
        """
        scene_id = scene_config.get('scene_id', f"scene_{datetime.utcnow().timestamp()}")
        
        scene = Scene(
            scene_id=scene_id,
            name=scene_config.get('name', ''),
            description=scene_config.get('description'),
            triggers=scene_config.get('triggers', []),
            actions=scene_config.get('actions', []),
            conditions=scene_config.get('conditions', []),
            enabled=scene_config.get('enabled', True)
        )
        
        self.scenes[scene_id] = scene
        return scene
    
    def execute_scene(self, scene_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行场景
        
        Args:
            scene_id: 场景ID
            context: 执行上下文
            
        Returns:
            执行结果
            
        Raises:
            SceneNotFoundError: 场景不存在时抛出
        """
        if scene_id not in self.scenes:
            error_msg = f'场景不存在: {scene_id}'
            logger.error(error_msg)
            raise SceneNotFoundError(error_msg)
        
        scene = self.scenes[scene_id]
        logger.info(f"执行场景: {scene_id} ({scene.name})")
        
        if not scene.enabled:
            error_msg = f'场景已禁用: {scene_id}'
            logger.warning(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        
        # 检查条件
        if scene.conditions:
            if not self._check_conditions(scene.conditions, context):
                error_msg = f'场景条件不满足: {scene_id}'
                logger.warning(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
        
        # 执行动作
        results = []
        for action in scene.actions:
            try:
                result = self._execute_action(action, context)
                results.append(result)
                if not result.get('success', False):
                    logger.warning(f"动作执行失败: {action.get('type')}")
            except (DeviceNotFoundError, SceneNotFoundError):
                # 重新抛出特定异常，让调用者处理
                raise
            except Exception as e:
                logger.error(f"动作执行异常: {str(e)}", exc_info=True)
                results.append({
                    'success': False,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r.get('success', False))
        logger.info(f"场景 {scene_id} 执行完成，成功 {success_count}/{len(results)} 个动作")
        
        return {
            'success': True,
            'scene_id': scene_id,
            'results': results
        }
    
    def _check_conditions(self, conditions: List[Dict[str, Any]],
                         context: Optional[Dict[str, Any]]) -> bool:
        """检查条件"""
        for condition in conditions:
            condition_type = condition.get('type')
            
            if condition_type == 'time':
                # 时间条件
                current_time = datetime.now().time()
                start_time = condition.get('start_time')
                end_time = condition.get('end_time')
                
                if start_time and end_time:
                    if not (start_time <= current_time <= end_time):
                        return False
            
            elif condition_type == 'device_state':
                # 设备状态条件
                device_id = condition.get('device_id')
                expected_state = condition.get('state')
                
                if device_id in self.devices:
                    device = self.devices[device_id]
                    actual_state = device.state.get(condition.get('attribute'))
                    
                    if actual_state != expected_state:
                        return False
            
            elif condition_type == 'sensor_value':
                # 传感器值条件
                sensor_id = condition.get('sensor_id')
                operator = condition.get('operator', '==')
                threshold = condition.get('threshold')
                
                if sensor_id in self.devices:
                    device = self.devices[sensor_id]
                    value = device.state.get(condition.get('attribute'))
                    
                    if operator == '>' and value <= threshold:
                        return False
                    elif operator == '<' and value >= threshold:
                        return False
                    elif operator == '==' and value != threshold:
                        return False
        
        return True
    
    def _execute_action(self, action: Dict[str, Any],
                       context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """执行动作"""
        action_type = action.get('type')
        device_id = action.get('device_id')
        
        if device_id not in self.devices:
            error_msg = f'设备不存在: {device_id}'
            logger.error(error_msg)
            raise DeviceNotFoundError(error_msg)
        
        device = self.devices[device_id]
        logger.debug(f"执行动作: {action_type} on device {device_id}")
        
        try:
            if action_type == 'set_state':
                # 设置设备状态
                attribute = action.get('attribute')
                value = action.get('value')
                
                if attribute is None:
                    raise ValidationError("动作缺少属性名")
                
                device.state[attribute] = value
                logger.debug(f"设备 {device_id} 属性 {attribute} 设置为 {value}")
                
                return {
                    'success': True,
                    'device_id': device_id,
                    'attribute': attribute,
                    'value': value
                }
            
            elif action_type == 'toggle':
                # 切换设备状态
                attribute = action.get('attribute', 'power')
                current_value = device.state.get(attribute, False)
                device.state[attribute] = not current_value
                
                logger.debug(f"设备 {device_id} 属性 {attribute} 切换为 {device.state[attribute]}")
                
                return {
                    'success': True,
                    'device_id': device_id,
                    'attribute': attribute,
                    'value': device.state[attribute]
                }
            
            else:
                error_msg = f'不支持的动作类型: {action_type}'
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
        except Exception as e:
            logger.error(f"执行动作时发生异常: {str(e)}", exc_info=True)
            raise
    
    def register_device(self, device_config: Dict[str, Any]) -> Device:
        """
        注册设备
        
        Args:
            device_config: 设备配置
            
        Returns:
            设备对象
            
        Raises:
            ValidationError: 配置验证失败时抛出
        """
        try:
            device_id = device_config.get('device_id', f"device_{datetime.utcnow().timestamp()}")
            
            if device_id in self.devices:
                logger.warning(f"设备 {device_id} 已存在，将更新")
            
            # 验证设备类型
            device_type_str = device_config.get('device_type', 'light')
            try:
                device_type = DeviceType(device_type_str)
            except ValueError:
                raise ValidationError(f"无效的设备类型: {device_type_str}")
            
            # 验证协议
            protocol_str = device_config.get('protocol', 'matter')
            try:
                protocol = DeviceProtocol(protocol_str)
            except ValueError:
                raise ValidationError(f"无效的协议类型: {protocol_str}")
            
            device = Device(
                device_id=device_id,
                name=device_config.get('name', ''),
                device_type=device_type,
                protocol=protocol,
                state=device_config.get('state', {}),
                capabilities=device_config.get('capabilities', []),
                metadata=device_config.get('metadata', {})
            )
            
            self.devices[device_id] = device
            logger.info(f"设备注册成功: {device_id} ({device.name})")
            return device
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"设备注册失败: {str(e)}", exc_info=True)
            raise ValidationError(f"设备注册失败: {str(e)}") from e


def main():
    """主函数 - 示例用法"""
    converter = SmartHomeConverter()
    
    # 注册Matter设备
    matter_device_config = {
        'device_id': 'matter_light_1',
        'name': '客厅灯',
        'device_type': 'light',
        'protocol': 'matter',
        'clusters': [{
            'cluster_id': 0x0006,
            'cluster_name': 'OnOff',
            'attributes': {
                'OnOff': True
            }
        }]
    }
    
    # 转换为Zigbee
    zigbee_device = converter.convert_matter_to_zigbee(matter_device_config)
    print(f"Zigbee设备: {zigbee_device}")
    
    # 创建场景
    scene_config = {
        'name': '回家场景',
        'triggers': [{'type': 'manual'}],
        'actions': [
            {
                'type': 'set_state',
                'device_id': 'matter_light_1',
                'attribute': 'power',
                'value': True
            }
        ],
        'conditions': [
            {
                'type': 'time',
                'start_time': '18:00:00',
                'end_time': '23:00:00'
            }
        ]
    }
    
    scene = converter.create_scene(scene_config)
    print(f"创建场景: {scene.scene_id}")
    
    # 执行场景
    result = converter.execute_scene(scene.scene_id)
    print(f"执行结果: {result}")


if __name__ == '__main__':
    main()
