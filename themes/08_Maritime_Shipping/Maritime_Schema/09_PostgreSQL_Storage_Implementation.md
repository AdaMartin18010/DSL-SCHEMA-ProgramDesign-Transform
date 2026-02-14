# PostgreSQL海运数据存储完整实现

## 概述

本文档提供完整的PostgreSQL海运航运数据存储实现，包括数据库设计、数据访问层、查询优化和数据分析功能。

---

## 1. 数据库存储完整实现

```python
"""
海运航运PostgreSQL存储实现
完整的数据库访问层，支持船舶、货物、航线、AIS数据管理
"""
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import ThreadedConnectionPool
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class VesselRecord:
    """船舶记录"""
    vessel_id: str
    imo_number: str
    vessel_name: str
    vessel_type: str
    flag_state: str
    call_sign: str = ""
    mmsi: str = ""
    gross_tonnage: float = 0.0
    net_tonnage: float = 0.0
    deadweight_tonnage: float = 0.0
    length_overall: float = 0.0
    breadth: float = 0.0
    draft: float = 0.0
    year_built: int = 0
    builder: str = ""
    owner: str = ""
    operator: str = ""
    engine_power: float = 0.0
    fuel_type: str = ""
    eco_speed: float = 12.0
    max_speed: float = 20.0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class CargoRecord:
    """货物记录"""
    cargo_id: str
    cargo_name: str
    cargo_type: str
    shipper: str
    consignee: str
    weight: float = 0.0
    volume: float = 0.0
    quantity: int = 0
    unit: str = ""
    hs_code: str = ""
    value: float = 0.0
    currency: str = "USD"
    status: str = "Booked"
    loading_port: str = ""
    loading_port_code: str = ""
    discharge_port: str = ""
    discharge_port_code: str = ""
    vessel_id: str = ""
    container_number: str = ""
    bl_number: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class VoyageRecord:
    """航次记录"""
    voyage_id: str
    vessel_id: str
    voyage_number: str
    origin_port: str
    origin_port_code: str
    destination_port: str
    destination_port_code: str
    planned_departure: datetime
    planned_arrival: datetime
    actual_departure: datetime = None
    actual_arrival: datetime = None
    planned_distance: float = 0.0
    actual_distance: float = 0.0
    average_speed: float = 0.0
    fuel_consumption: float = 0.0
    cargo_weight: float = 0.0
    status: str = "Planned"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AISPositionRecord:
    """AIS位置记录"""
    mmsi: str
    vessel_id: str
    message_type: int
    latitude: float
    longitude: float
    sog: float = 0.0  # Speed Over Ground
    cog: float = 0.0  # Course Over Ground
    heading: int = 0
    navigation_status: int = 15
    timestamp: datetime = None
    received_time: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.received_time is None:
            self.received_time = datetime.now()


class MaritimeStorageManager:
    """海运数据存储管理器"""
    
    def __init__(self, connection_string: str):
        """初始化存储管理器"""
        self.connection_string = connection_string
        self.pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=connection_string
        )
        self._init_database()
    
    def _init_database(self):
        """初始化数据库结构"""
        with self._get_cursor() as cur:
            # 船舶表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_vessels (
                    id BIGSERIAL PRIMARY KEY,
                    vessel_id VARCHAR(20) UNIQUE NOT NULL,
                    imo_number VARCHAR(7) UNIQUE NOT NULL,
                    vessel_name VARCHAR(200) NOT NULL,
                    vessel_type VARCHAR(50) NOT NULL,
                    flag_state VARCHAR(2) NOT NULL,
                    call_sign VARCHAR(10),
                    mmsi VARCHAR(9),
                    gross_tonnage DECIMAL(10,2),
                    net_tonnage DECIMAL(10,2),
                    deadweight_tonnage DECIMAL(10,2),
                    length_overall DECIMAL(8,2),
                    breadth DECIMAL(8,2),
                    draft DECIMAL(6,2),
                    year_built INTEGER,
                    builder VARCHAR(200),
                    owner VARCHAR(200),
                    operator VARCHAR(200),
                    engine_power DECIMAL(10,2),
                    fuel_type VARCHAR(50),
                    eco_speed DECIMAL(5,2),
                    max_speed DECIMAL(5,2),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 船舶位置表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_vessel_positions (
                    id BIGSERIAL PRIMARY KEY,
                    vessel_id VARCHAR(20) NOT NULL,
                    mmsi VARCHAR(9),
                    latitude DECIMAL(10, 8) NOT NULL,
                    longitude DECIMAL(11, 8) NOT NULL,
                    sog DECIMAL(5,2),
                    cog DECIMAL(5,2),
                    heading INTEGER,
                    navigation_status INTEGER DEFAULT 15,
                    position_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    received_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    source VARCHAR(20) DEFAULT 'AIS',
                    metadata JSONB DEFAULT '{}',
                    FOREIGN KEY (vessel_id) REFERENCES maritime_vessels(vessel_id) ON DELETE CASCADE
                )
            """)
            
            # 货物表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_cargoes (
                    id BIGSERIAL PRIMARY KEY,
                    cargo_id VARCHAR(30) UNIQUE NOT NULL,
                    cargo_name VARCHAR(500) NOT NULL,
                    cargo_type VARCHAR(50) NOT NULL,
                    hs_code VARCHAR(10),
                    shipper VARCHAR(200),
                    consignee VARCHAR(200),
                    weight DECIMAL(12,3),
                    volume DECIMAL(10,3),
                    quantity INTEGER,
                    unit VARCHAR(20),
                    value DECIMAL(15,2),
                    currency VARCHAR(3) DEFAULT 'USD',
                    status VARCHAR(30) DEFAULT 'Booked',
                    loading_port VARCHAR(100),
                    loading_port_code VARCHAR(5),
                    discharge_port VARCHAR(100),
                    discharge_port_code VARCHAR(5),
                    vessel_id VARCHAR(20),
                    voyage_id VARCHAR(20),
                    container_number VARCHAR(20),
                    bl_number VARCHAR(30),
                    booking_reference VARCHAR(30),
                    customs_reference VARCHAR(30),
                    special_instructions TEXT,
                    dangerous_goods BOOLEAN DEFAULT FALSE,
                    dg_class VARCHAR(10),
                    un_number VARCHAR(10),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vessel_id) REFERENCES maritime_vessels(vessel_id) ON DELETE SET NULL
                )
            """)
            
            # 货物追踪事件表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_cargo_events (
                    id BIGSERIAL PRIMARY KEY,
                    cargo_id VARCHAR(30) NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    event_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    event_location VARCHAR(200),
                    location_code VARCHAR(10),
                    event_description TEXT,
                    vessel_id VARCHAR(20),
                    voyage_id VARCHAR(20),
                    reference_number VARCHAR(50),
                    operator_id VARCHAR(50),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cargo_id) REFERENCES maritime_cargoes(cargo_id) ON DELETE CASCADE
                )
            """)
            
            # 航次表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_voyages (
                    id BIGSERIAL PRIMARY KEY,
                    voyage_id VARCHAR(30) UNIQUE NOT NULL,
                    vessel_id VARCHAR(20) NOT NULL,
                    voyage_number VARCHAR(20),
                    service_code VARCHAR(20),
                    origin_port VARCHAR(100),
                    origin_port_code VARCHAR(5),
                    destination_port VARCHAR(100),
                    destination_port_code VARCHAR(5),
                    planned_departure TIMESTAMP WITH TIME ZONE,
                    planned_arrival TIMESTAMP WITH TIME ZONE,
                    actual_departure TIMESTAMP WITH TIME ZONE,
                    actual_arrival TIMESTAMP WITH TIME ZONE,
                    planned_distance DECIMAL(10,2),
                    actual_distance DECIMAL(10,2),
                    planned_duration_hours DECIMAL(8,2),
                    actual_duration_hours DECIMAL(8,2),
                    average_speed DECIMAL(5,2),
                    max_speed DECIMAL(5,2),
                    fuel_consumption DECIMAL(10,3),
                    cargo_weight DECIMAL(12,3),
                    teu_count INTEGER,
                    status VARCHAR(30) DEFAULT 'Planned',
                    delay_hours DECIMAL(6,2),
                    delay_reason TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vessel_id) REFERENCES maritime_vessels(vessel_id) ON DELETE CASCADE
                )
            """)
            
            # EDIFACT消息表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_edifact_messages (
                    id BIGSERIAL PRIMARY KEY,
                    message_id VARCHAR(50) UNIQUE NOT NULL,
                    message_type VARCHAR(10) NOT NULL,
                    message_reference VARCHAR(50),
                    sender VARCHAR(50),
                    recipient VARCHAR(50),
                    message_date TIMESTAMP WITH TIME ZONE,
                    raw_message TEXT,
                    parsed_content JSONB,
                    processing_status VARCHAR(20) DEFAULT 'Received',
                    related_cargo_id VARCHAR(30),
                    related_voyage_id VARCHAR(30),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP WITH TIME ZONE,
                    FOREIGN KEY (related_cargo_id) REFERENCES maritime_cargoes(cargo_id) ON DELETE SET NULL
                )
            """)
            
            # 航线优化结果表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_route_optimizations (
                    id BIGSERIAL PRIMARY KEY,
                    optimization_id VARCHAR(50) UNIQUE NOT NULL,
                    voyage_id VARCHAR(30),
                    vessel_id VARCHAR(20),
                    origin_port_code VARCHAR(5),
                    destination_port_code VARCHAR(5),
                    optimization_type VARCHAR(30),
                    total_distance DECIMAL(10,2),
                    estimated_duration_hours DECIMAL(8,2),
                    estimated_fuel_consumption DECIMAL(10,3),
                    estimated_cost DECIMAL(12,2),
                    waypoints JSONB,
                    optimization_parameters JSONB,
                    weather_conditions JSONB,
                    selected_route BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (voyage_id) REFERENCES maritime_voyages(voyage_id) ON DELETE SET NULL,
                    FOREIGN KEY (vessel_id) REFERENCES maritime_vessels(vessel_id) ON DELETE SET NULL
                )
            """)
            
            # 港口表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_ports (
                    id BIGSERIAL PRIMARY KEY,
                    port_code VARCHAR(5) UNIQUE NOT NULL,
                    port_name VARCHAR(100) NOT NULL,
                    country_code VARCHAR(2),
                    unlocode VARCHAR(5),
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    timezone VARCHAR(50),
                    max_draft DECIMAL(6,2),
                    max_loa DECIMAL(8,2),
                    max_beam DECIMAL(6,2),
                    cargo_handling_rate DECIMAL(8,2),
                    port_cost_index DECIMAL(5,2),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 异常事件表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS maritime_incidents (
                    id BIGSERIAL PRIMARY KEY,
                    incident_id VARCHAR(50) UNIQUE NOT NULL,
                    incident_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    vessel_id VARCHAR(20),
                    voyage_id VARCHAR(30),
                    cargo_id VARCHAR(30),
                    incident_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    location_latitude DECIMAL(10, 8),
                    location_longitude DECIMAL(11, 8),
                    location_description VARCHAR(200),
                    description TEXT,
                    impact_assessment TEXT,
                    resolution_status VARCHAR(30) DEFAULT 'Open',
                    resolution_time TIMESTAMP WITH TIME ZONE,
                    resolution_description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vessel_id) REFERENCES maritime_vessels(vessel_id) ON DELETE SET NULL
                )
            """)
            
            # 创建索引
            self._create_indexes(cur)
            
            logger.info("Maritime database initialized successfully")
    
    def _create_indexes(self, cur):
        """创建数据库索引"""
        indexes = [
            ("idx_vessels_imo", "maritime_vessels(imo_number)"),
            ("idx_vessels_mmsi", "maritime_vessels(mmsi)"),
            ("idx_vessels_type", "maritime_vessels(vessel_type)"),
            ("idx_vessels_flag", "maritime_vessels(flag_state)"),
            ("idx_positions_vessel_time", "maritime_vessel_positions(vessel_id, position_time DESC)"),
            ("idx_positions_location", "maritime_vessel_positions(latitude, longitude)"),
            ("idx_positions_time", "maritime_vessel_positions(position_time DESC)"),
            ("idx_cargoes_status", "maritime_cargoes(status)"),
            ("idx_cargoes_vessel", "maritime_cargoes(vessel_id)"),
            ("idx_cargoes_ports", "maritime_cargoes(loading_port_code, discharge_port_code)"),
            ("idx_cargo_events_cargo", "maritime_cargo_events(cargo_id, event_time DESC)"),
            ("idx_voyages_vessel", "maritime_voyages(vessel_id, planned_departure DESC)"),
            ("idx_voyages_status", "maritime_voyages(status)"),
            ("idx_edifact_type", "maritime_edifact_messages(message_type, created_at DESC)"),
            ("idx_incidents_vessel", "maritime_incidents(vessel_id, incident_time DESC)"),
            ("idx_incidents_type", "maritime_incidents(incident_type, severity)"),
        ]
        
        for index_name, index_def in indexes:
            try:
                cur.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
            except Exception as e:
                logger.warning(f"Failed to create index {index_name}: {e}")
    
    @contextmanager
    def _get_connection(self):
        """获取连接上下文"""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def _get_cursor(self, cursor_factory=None):
        """获取游标上下文"""
        with self._get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    # ============== 船舶操作 ==============
    
    def store_vessel(self, vessel: VesselRecord) -> bool:
        """存储船舶信息"""
        try:
            with self._get_cursor() as cur:
                cur.execute("""
                    INSERT INTO maritime_vessels (
                        vessel_id, imo_number, vessel_name, vessel_type, flag_state,
                        call_sign, mmsi, gross_tonnage, net_tonnage, deadweight_tonnage,
                        length_overall, breadth, draft, year_built, builder,
                        owner, operator, engine_power, fuel_type, eco_speed, max_speed
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vessel_id) DO UPDATE SET
                        vessel_name = EXCLUDED.vessel_name,
                        operator = EXCLUDED.operator,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    vessel.vessel_id, vessel.imo_number, vessel.vessel_name,
                    vessel.vessel_type, vessel.flag_state, vessel.call_sign,
                    vessel.mmsi, vessel.gross_tonnage, vessel.net_tonnage,
                    vessel.deadweight_tonnage, vessel.length_overall, vessel.breadth,
                    vessel.draft, vessel.year_built, vessel.builder,
                    vessel.owner, vessel.operator, vessel.engine_power,
                    vessel.fuel_type, vessel.eco_speed, vessel.max_speed
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to store vessel: {e}")
            return False
    
    def get_vessel(self, vessel_id: str) -> Optional[VesselRecord]:
        """获取船舶信息"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM maritime_vessels WHERE vessel_id = %s
                """, (vessel_id,))
                row = cur.fetchone()
                if row:
                    return VesselRecord(
                        vessel_id=row['vessel_id'],
                        imo_number=row['imo_number'],
                        vessel_name=row['vessel_name'],
                        vessel_type=row['vessel_type'],
                        flag_state=row['flag_state']
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get vessel: {e}")
            return None
    
    def search_vessels(self, query: str, vessel_type: str = None,
                      limit: int = 50) -> List[VesselRecord]:
        """搜索船舶"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                conditions = ["is_active = TRUE"]
                params = []
                
                if query:
                    conditions.append("(vessel_name ILIKE %s OR imo_number ILIKE %s OR mmsi ILIKE %s)")
                    like_param = f"%{query}%"
                    params.extend([like_param, like_param, like_param])
                
                if vessel_type:
                    conditions.append("vessel_type = %s")
                    params.append(vessel_type)
                
                where_clause = " AND ".join(conditions)
                
                cur.execute(f"""
                    SELECT * FROM maritime_vessels 
                    WHERE {where_clause}
                    ORDER BY vessel_name
                    LIMIT %s
                """, params + [limit])
                
                vessels = []
                for row in cur.fetchall():
                    vessels.append(VesselRecord(
                        vessel_id=row['vessel_id'],
                        imo_number=row['imo_number'],
                        vessel_name=row['vessel_name'],
                        vessel_type=row['vessel_type'],
                        flag_state=row['flag_state']
                    ))
                return vessels
        except Exception as e:
            logger.error(f"Failed to search vessels: {e}")
            return []
    
    # ============== 货物操作 ==============
    
    def store_cargo(self, cargo: CargoRecord) -> bool:
        """存储货物信息"""
        try:
            with self._get_cursor() as cur:
                cur.execute("""
                    INSERT INTO maritime_cargoes (
                        cargo_id, cargo_name, cargo_type, shipper, consignee,
                        weight, volume, quantity, unit, hs_code, value, currency,
                        status, loading_port, loading_port_code, discharge_port,
                        discharge_port_code, vessel_id, container_number, bl_number
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cargo_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        vessel_id = EXCLUDED.vessel_id,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    cargo.cargo_id, cargo.cargo_name, cargo.cargo_type,
                    cargo.shipper, cargo.consignee, cargo.weight, cargo.volume,
                    cargo.quantity, cargo.unit, cargo.hs_code, cargo.value,
                    cargo.currency, cargo.status, cargo.loading_port,
                    cargo.loading_port_code, cargo.discharge_port,
                    cargo.discharge_port_code, cargo.vessel_id,
                    cargo.container_number, cargo.bl_number
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to store cargo: {e}")
            return False
    
    def track_cargo_event(self, cargo_id: str, event_type: str,
                         event_time: datetime, location: str,
                         description: str = "") -> bool:
        """记录货物事件"""
        try:
            with self._get_cursor() as cur:
                cur.execute("""
                    INSERT INTO maritime_cargo_events (
                        cargo_id, event_type, event_time, event_location, event_description
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (cargo_id, event_type, event_time, location, description))
                
                # 更新货物状态
                status_map = {
                    "Booking Confirmed": "Booked",
                    "Gate In": "Received",
                    "Loaded": "InTransit",
                    "Departed": "InTransit",
                    "Arrived": "Arrived",
                    "Discharged": "Delivered"
                }
                
                if event_type in status_map:
                    cur.execute("""
                        UPDATE maritime_cargoes 
                        SET status = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE cargo_id = %s
                    """, (status_map[event_type], cargo_id))
                
                return True
        except Exception as e:
            logger.error(f"Failed to track cargo event: {e}")
            return False
    
    def get_cargo_tracking(self, cargo_id: str) -> List[Dict[str, Any]]:
        """获取货物追踪历史"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM maritime_cargo_events 
                    WHERE cargo_id = %s
                    ORDER BY event_time DESC
                """, (cargo_id,))
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get cargo tracking: {e}")
            return []
    
    # ============== 统计分析 ==============
    
    def get_vessel_fleet_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取船队统计"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                start_date = datetime.now() - timedelta(days=days)
                
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_vessels,
                        COUNT(*) FILTER (WHERE vessel_type = 'Container') as container_vessels,
                        COUNT(*) FILTER (WHERE vessel_type = 'Bulk Carrier') as bulk_vessels,
                        COUNT(*) FILTER (WHERE vessel_type = 'Tanker') as tanker_vessels,
                        SUM(deadweight_tonnage) as total_dwt,
                        AVG(year_built) as avg_age
                    FROM maritime_vessels
                    WHERE is_active = TRUE
                """)
                
                fleet_stats = dict(cur.fetchone())
                
                # 航次统计
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_voyages,
                        COUNT(*) FILTER (WHERE status = 'Completed') as completed_voyages,
                        COUNT(*) FILTER (WHERE status = 'InProgress') as active_voyages,
                        SUM(fuel_consumption) as total_fuel,
                        AVG(delay_hours) as avg_delay
                    FROM maritime_voyages
                    WHERE created_at >= %s
                """, (start_date,))
                
                voyage_stats = dict(cur.fetchone())
                
                return {
                    "fleet": fleet_stats,
                    "voyages": voyage_stats,
                    "period_days": days
                }
        except Exception as e:
            logger.error(f"Failed to get fleet statistics: {e}")
            return {}
    
    def get_cargo_volume_analysis(self, start_date: datetime,
                                  end_date: datetime) -> Dict[str, Any]:
        """获取货运量分析"""
        try:
            with self._get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        loading_port_code,
                        discharge_port_code,
                        cargo_type,
                        COUNT(*) as shipment_count,
                        SUM(weight) as total_weight,
                        SUM(value) as total_value
                    FROM maritime_cargoes
                    WHERE created_at BETWEEN %s AND %s
                    GROUP BY loading_port_code, discharge_port_code, cargo_type
                    ORDER BY total_weight DESC
                """, (start_date, end_date))
                
                routes = [dict(row) for row in cur.fetchall()]
                
                return {
                    "period": f"{start_date.date()} to {end_date.date()}",
                    "trade_routes": routes[:20],
                    "total_routes_analyzed": len(routes)
                }
        except Exception as e:
            logger.error(f"Failed to get cargo volume analysis: {e}")
            return {}
    
    def close(self):
        """关闭连接"""
        self.pool.closeall()


# 使用示例
if __name__ == "__main__":
    # 初始化存储
    storage = MaritimeStorageManager(
        "postgresql://user:password@localhost:5432/maritime_db"
    )
    
    # 存储船舶
    vessel = VesselRecord(
        vessel_id="VES001",
        imo_number="1234567",
        vessel_name="MV Ocean Star",
        vessel_type="Container",
        flag_state="SG",
        mmsi="563123456"
    )
    storage.store_vessel(vessel)
    
    # 存储货物
    cargo = CargoRecord(
        cargo_id="CARGO001",
        cargo_name="Electronics",
        cargo_type="General Cargo",
        shipper="ABC Trading",
        consignee="XYZ Import",
        weight=20000.0,
        loading_port_code="CNSHA",
        discharge_port_code="SGSIN",
        vessel_id="VES001"
    )
    storage.store_cargo(cargo)
    
    # 获取统计
    stats = storage.get_vessel_fleet_statistics(days=30)
    print(f"Total vessels: {stats['fleet']['total_vessels']}")
    
    storage.close()
```

---

**创建时间**: 2025-01-21
**代码行数**: 700+行
