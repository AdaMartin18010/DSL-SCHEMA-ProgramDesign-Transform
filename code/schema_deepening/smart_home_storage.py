"""
智慧家居PostgreSQL存储

专注于设备管理、场景管理、事件记录的PostgreSQL存储
"""

import psycopg2
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from functools import lru_cache

from .logger import logger
from .exceptions import StorageError, ValidationError


class SmartHomeStorage:
    """
    智慧家居PostgreSQL存储
    
    专注于设备管理、场景管理、事件记录的PostgreSQL存储
    """
    
    def __init__(self, connection_string: str):
        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor()
            self._create_tables()
            logger.info("SmartHomeStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {str(e)}", exc_info=True)
            raise StorageError(f"数据库连接失败: {str(e)}") from e
    
    def _create_tables(self):
        """创建智慧家居数据表"""
        # 设备表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS smart_home_devices (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                device_type VARCHAR(50) NOT NULL,
                protocol VARCHAR(20) NOT NULL,
                state JSONB,
                capabilities JSONB,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 设备状态历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS device_state_history (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(50) NOT NULL,
                state JSONB NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES smart_home_devices(device_id)
            )
        """)
        
        # 场景表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS smart_home_scenes (
                id BIGSERIAL PRIMARY KEY,
                scene_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                triggers JSONB,
                actions JSONB,
                conditions JSONB,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 场景执行历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS scene_execution_history (
                id BIGSERIAL PRIMARY KEY,
                scene_id VARCHAR(50) NOT NULL,
                execution_id VARCHAR(50) UNIQUE NOT NULL,
                success BOOLEAN NOT NULL,
                results JSONB,
                error_message TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scene_id) REFERENCES smart_home_scenes(scene_id)
            )
        """)
        
        # 设备事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS device_events (
                id BIGSERIAL PRIMARY KEY,
                event_id VARCHAR(50) UNIQUE NOT NULL,
                device_id VARCHAR(50) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB,
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES smart_home_devices(device_id)
            )
        """)
        
        # 创建索引（优化查询性能）
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_device_state_history_device_id ON device_state_history(device_id, changed_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_scene_execution_history_scene_id ON scene_execution_history(scene_id, executed_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_device_events_device_id ON device_events(device_id, occurred_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_device_events_type ON device_events(event_type, occurred_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_smart_home_devices_type ON smart_home_devices(device_type)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_smart_home_devices_protocol ON smart_home_devices(protocol)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_smart_home_scenes_enabled ON smart_home_scenes(enabled) WHERE enabled = TRUE")
        
        self.conn.commit()
    
    def store_device(self, device: Dict[str, Any]) -> bool:
        """
        存储设备
        
        Args:
            device: 设备数据
            
        Returns:
            是否成功
            
        Raises:
            StorageError: 存储失败时抛出
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证输入
            if not device:
                raise ValidationError("设备数据不能为空")
            
            device_id = device.get('device_id')
            if not device_id:
                raise ValidationError("设备ID不能为空")
            
            logger.debug(f"存储设备: {device_id}")
            
            self.cur.execute("""
                INSERT INTO smart_home_devices 
                (device_id, name, device_type, protocol, state, capabilities, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (device_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    device_type = EXCLUDED.device_type,
                    protocol = EXCLUDED.protocol,
                    state = EXCLUDED.state,
                    capabilities = EXCLUDED.capabilities,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                device_id,
                device.get('name', ''),
                device.get('device_type', ''),
                device.get('protocol', ''),
                json.dumps(device.get('state', {})),
                json.dumps(device.get('capabilities', [])),
                json.dumps(device.get('metadata', {}))
            ))
            
            # 记录状态历史
            if 'state' in device and device['state']:
                self.cur.execute("""
                    INSERT INTO device_state_history (device_id, state)
                    VALUES (%s, %s)
                """, (
                    device_id,
                    json.dumps(device['state'])
                ))
            
            self.conn.commit()
            logger.info(f"设备存储成功: {device_id}")
            return True
            
        except ValidationError:
            self.conn.rollback()
            raise
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"设备存储失败: {str(e)}", exc_info=True)
            raise StorageError(f"设备存储失败: {str(e)}") from e
        except Exception as e:
            self.conn.rollback()
            logger.error(f"设备存储时发生未知错误: {str(e)}", exc_info=True)
            raise StorageError(f"设备存储失败: {str(e)}") from e
    
    def store_scene(self, scene: Dict[str, Any]) -> bool:
        """
        存储场景
        
        Args:
            scene: 场景数据
            
        Returns:
            是否成功
            
        Raises:
            StorageError: 存储失败时抛出
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证输入
            if not scene:
                raise ValidationError("场景数据不能为空")
            
            scene_id = scene.get('scene_id')
            if not scene_id:
                raise ValidationError("场景ID不能为空")
            
            logger.debug(f"存储场景: {scene_id}")
            
            self.cur.execute("""
                INSERT INTO smart_home_scenes 
                (scene_id, name, description, triggers, actions, conditions, enabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (scene_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    triggers = EXCLUDED.triggers,
                    actions = EXCLUDED.actions,
                    conditions = EXCLUDED.conditions,
                    enabled = EXCLUDED.enabled,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                scene_id,
                scene.get('name', ''),
                scene.get('description'),
                json.dumps(scene.get('triggers', [])),
                json.dumps(scene.get('actions', [])),
                json.dumps(scene.get('conditions', [])),
                scene.get('enabled', True)
            ))
            
            self.conn.commit()
            logger.info(f"场景存储成功: {scene_id}")
            return True
            
        except ValidationError:
            self.conn.rollback()
            raise
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"场景存储失败: {str(e)}", exc_info=True)
            raise StorageError(f"场景存储失败: {str(e)}") from e
        except Exception as e:
            self.conn.rollback()
            logger.error(f"场景存储时发生未知错误: {str(e)}", exc_info=True)
            raise StorageError(f"场景存储失败: {str(e)}") from e
    
    def store_scene_execution(self, execution: Dict[str, Any]) -> bool:
        """存储场景执行记录"""
        try:
            self.cur.execute("""
                INSERT INTO scene_execution_history 
                (scene_id, execution_id, success, results, error_message)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                execution['scene_id'],
                execution.get('execution_id', f"exec_{datetime.utcnow().timestamp()}"),
                execution.get('success', False),
                json.dumps(execution.get('results', [])),
                execution.get('error_message')
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def store_device_event(self, event: Dict[str, Any]) -> bool:
        """存储设备事件"""
        try:
            self.cur.execute("""
                INSERT INTO device_events 
                (event_id, device_id, event_type, event_data)
                VALUES (%s, %s, %s, %s)
            """, (
                event.get('event_id', f"event_{datetime.utcnow().timestamp()}"),
                event['device_id'],
                event['event_type'],
                json.dumps(event.get('event_data', {}))
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def query_device_state_history(self, device_id: str, start_time: Optional[datetime] = None,
                                  end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        查询设备状态历史
        
        Args:
            device_id: 设备ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            状态历史列表
            
        Raises:
            StorageError: 查询失败时抛出
            ValidationError: 设备ID为空时抛出
        """
        try:
            if not device_id:
                raise ValidationError("设备ID不能为空")
            
            logger.debug(f"查询设备状态历史: {device_id}")
            
            query = """
                SELECT state, changed_at
                FROM device_state_history
                WHERE device_id = %s
            """
            params = [device_id]
            
            if start_time:
                query += " AND changed_at >= %s"
                params.append(start_time)
            
            if end_time:
                query += " AND changed_at <= %s"
                params.append(end_time)
            
            query += " ORDER BY changed_at DESC"
            
            self.cur.execute(query, params)
            results = []
            
            for row in self.cur.fetchall():
                results.append({
                    'state': json.loads(row[0]) if isinstance(row[0], str) else row[0],
                    'changed_at': row[1].isoformat() if isinstance(row[1], datetime) else row[1]
                })
            
            logger.debug(f"查询到 {len(results)} 条状态历史记录")
            return results
            
        except ValidationError:
            raise
        except psycopg2.Error as e:
            logger.error(f"查询设备状态历史失败: {str(e)}", exc_info=True)
            raise StorageError(f"查询失败: {str(e)}") from e
        except Exception as e:
            logger.error(f"查询时发生未知错误: {str(e)}", exc_info=True)
            raise StorageError(f"查询失败: {str(e)}") from e
    
    def query_scene_executions(self, scene_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """查询场景执行历史"""
        self.cur.execute("""
            SELECT execution_id, success, results, error_message, executed_at
            FROM scene_execution_history
            WHERE scene_id = %s
            ORDER BY executed_at DESC
            LIMIT %s
        """, (scene_id, limit))
        
        results = []
        for row in self.cur.fetchall():
            results.append({
                'execution_id': row[0],
                'success': row[1],
                'results': json.loads(row[2]) if isinstance(row[2], str) else row[2],
                'error_message': row[3],
                'executed_at': row[4].isoformat() if isinstance(row[4], datetime) else row[4]
            })
        
        return results


def main():
    """主函数 - 示例用法"""
    storage = SmartHomeStorage("postgresql://localhost/smart_home_db")
    
    # 存储设备
    device = {
        'device_id': 'device_1',
        'name': '客厅灯',
        'device_type': 'light',
        'protocol': 'matter',
        'state': {'power': True, 'brightness': 80},
        'capabilities': ['on_off', 'dimming']
    }
    
    storage.store_device(device)
    print("设备已存储")
    
    # 存储场景
    scene = {
        'scene_id': 'scene_1',
        'name': '回家场景',
        'triggers': [{'type': 'manual'}],
        'actions': [{'type': 'set_state', 'device_id': 'device_1', 'attribute': 'power', 'value': True}]
    }
    
    storage.store_scene(scene)
    print("场景已存储")


if __name__ == '__main__':
    main()
