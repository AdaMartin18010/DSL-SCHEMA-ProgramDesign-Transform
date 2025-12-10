"""
海运与航运PostgreSQL存储

专注于AIS数据、航线优化、港口效率的PostgreSQL存储
"""

import psycopg2
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .logger import logger
from .exceptions import StorageError, ValidationError


class MaritimeStorage:
    """
    海运与航运PostgreSQL存储
    
    专注于AIS数据、航线优化、港口效率的PostgreSQL存储
    """
    
    def __init__(self, connection_string: str):
        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor()
            self._create_tables()
            logger.info("MaritimeStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {str(e)}", exc_info=True)
            raise StorageError(f"数据库连接失败: {str(e)}") from e
    
    def _create_tables(self):
        """创建海运航运数据表"""
        # AIS数据表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS ais_data (
                id BIGSERIAL PRIMARY KEY,
                message_id VARCHAR(50) UNIQUE NOT NULL,
                mmsi VARCHAR(9) NOT NULL,
                message_type INTEGER NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                speed DECIMAL(5, 2),
                course DECIMAL(5, 2),
                heading DECIMAL(5, 2),
                timestamp TIMESTAMP NOT NULL,
                raw_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 船舶信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vessels (
                id BIGSERIAL PRIMARY KEY,
                vessel_id VARCHAR(50) UNIQUE NOT NULL,
                mmsi VARCHAR(9) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                vessel_type VARCHAR(50),
                imo_number VARCHAR(10),
                call_sign VARCHAR(10),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 航线优化表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS route_optimizations (
                id BIGSERIAL PRIMARY KEY,
                optimization_id VARCHAR(50) UNIQUE NOT NULL,
                vessel_id VARCHAR(50) NOT NULL,
                origin_port VARCHAR(100) NOT NULL,
                destination_port VARCHAR(100) NOT NULL,
                optimization_type VARCHAR(50) NOT NULL,
                route_data JSONB NOT NULL,
                cost DECIMAL(12, 2),
                duration_hours DECIMAL(8, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
            )
        """)
        
        # 港口效率表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS port_efficiency (
                id BIGSERIAL PRIMARY KEY,
                port_code VARCHAR(10) NOT NULL,
                port_name VARCHAR(200) NOT NULL,
                date DATE NOT NULL,
                total_vessels INTEGER DEFAULT 0,
                average_wait_time DECIMAL(8, 2),
                average_processing_time DECIMAL(8, 2),
                efficiency_score DECIMAL(5, 2),
                metrics JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(port_code, date)
            )
        """)
        
        # 异常事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS maritime_events (
                id BIGSERIAL PRIMARY KEY,
                event_id VARCHAR(50) UNIQUE NOT NULL,
                vessel_id VARCHAR(50),
                event_type VARCHAR(50) NOT NULL,
                event_description TEXT,
                event_data JSONB,
                severity VARCHAR(20),
                occurred_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
            )
        """)
        
        # 创建索引（优化查询性能）
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_ais_data_mmsi_timestamp ON ais_data(mmsi, timestamp DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_ais_data_message_type ON ais_data(message_type, timestamp DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_ais_data_location ON ais_data USING gist(ST_MakePoint(longitude, latitude))")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_ais_data_timestamp ON ais_data(timestamp DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_vessels_mmsi ON vessels(mmsi)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_route_optimizations_vessel_id ON route_optimizations(vessel_id, created_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_route_optimizations_status ON route_optimizations(status, created_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_maritime_events_vessel_id ON maritime_events(vessel_id, occurred_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_maritime_events_type_severity ON maritime_events(event_type, severity, occurred_at DESC)")
        
        self.conn.commit()
    
    def store_ais_data(self, ais_data: Dict[str, Any]) -> bool:
        """
        存储AIS数据
        
        Args:
            ais_data: AIS数据
            
        Returns:
            是否成功
            
        Raises:
            StorageError: 存储失败时抛出
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证输入
            if not ais_data:
                raise ValidationError("AIS数据不能为空")
            
            mmsi = ais_data.get('mmsi')
            if not mmsi:
                raise ValidationError("MMSI不能为空")
            
            if 'latitude' not in ais_data or 'longitude' not in ais_data:
                raise ValidationError("经纬度不能为空")
            
            message_id = ais_data.get('message_id', f"ais_{datetime.utcnow().timestamp()}")
            logger.debug(f"存储AIS数据: {message_id} (MMSI: {mmsi})")
            
            self.cur.execute("""
                INSERT INTO ais_data 
                (message_id, mmsi, message_type, latitude, longitude, speed, course, heading, timestamp, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                message_id,
                mmsi,
                ais_data.get('message_type', 1),
                ais_data['latitude'],
                ais_data['longitude'],
                ais_data.get('speed'),
                ais_data.get('course'),
                ais_data.get('heading'),
                ais_data.get('timestamp', datetime.utcnow()),
                json.dumps(ais_data.get('raw_data', {}))
            ))
            
            self.conn.commit()
            logger.info(f"AIS数据存储成功: {message_id}")
            return True
            
        except ValidationError:
            self.conn.rollback()
            raise
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"AIS数据存储失败: {str(e)}", exc_info=True)
            raise StorageError(f"AIS数据存储失败: {str(e)}") from e
        except Exception as e:
            self.conn.rollback()
            logger.error(f"AIS数据存储时发生未知错误: {str(e)}", exc_info=True)
            raise StorageError(f"AIS数据存储失败: {str(e)}") from e
    
    def store_vessel(self, vessel: Dict[str, Any]) -> bool:
        """存储船舶信息"""
        try:
            self.cur.execute("""
                INSERT INTO vessels 
                (vessel_id, mmsi, name, vessel_type, imo_number, call_sign, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vessel_id) 
                DO UPDATE SET 
                    mmsi = EXCLUDED.mmsi,
                    name = EXCLUDED.name,
                    vessel_type = EXCLUDED.vessel_type,
                    imo_number = EXCLUDED.imo_number,
                    call_sign = EXCLUDED.call_sign,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                vessel['vessel_id'],
                vessel['mmsi'],
                vessel['name'],
                vessel.get('vessel_type'),
                vessel.get('imo_number'),
                vessel.get('call_sign'),
                json.dumps(vessel.get('metadata', {}))
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def store_route_optimization(self, optimization: Dict[str, Any]) -> bool:
        """存储航线优化结果"""
        try:
            self.cur.execute("""
                INSERT INTO route_optimizations 
                (optimization_id, vessel_id, origin_port, destination_port, optimization_type, route_data, cost, duration_hours)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                optimization.get('optimization_id', f"opt_{datetime.utcnow().timestamp()}"),
                optimization['vessel_id'],
                optimization['origin_port'],
                optimization['destination_port'],
                optimization['optimization_type'],
                json.dumps(optimization.get('route_data', {})),
                optimization.get('cost'),
                optimization.get('duration_hours')
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def query_vessel_trajectory(self, mmsi: str, start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """查询船舶轨迹"""
        query = """
            SELECT latitude, longitude, speed, course, timestamp
            FROM ais_data
            WHERE mmsi = %s
        """
        params = [mmsi]
        
        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)
        
        query += " ORDER BY timestamp ASC"
        
        self.cur.execute(query, params)
        results = []
        
        for row in self.cur.fetchall():
            results.append({
                'latitude': float(row[0]),
                'longitude': float(row[1]),
                'speed': float(row[2]) if row[2] else None,
                'course': float(row[3]) if row[3] else None,
                'timestamp': row[4].isoformat() if isinstance(row[4], datetime) else row[4]
            })
        
        return results


def main():
    """主函数 - 示例用法"""
    storage = MaritimeStorage("postgresql://localhost/maritime_db")
    
    # 存储AIS数据
    ais_data = {
        'mmsi': '123456789',
        'message_type': 1,
        'latitude': 31.2304,
        'longitude': 121.4737,
        'speed': 12.5,
        'course': 45.0,
        'timestamp': datetime.utcnow()
    }
    
    storage.store_ais_data(ais_data)
    print("AIS数据已存储")


if __name__ == '__main__':
    main()
