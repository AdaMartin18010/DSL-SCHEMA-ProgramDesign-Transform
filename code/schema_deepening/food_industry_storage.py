"""
食品行业PostgreSQL存储

专注于EPCIS事件、追溯链、质量监控的PostgreSQL存储
"""

import psycopg2
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .logger import logger
from .exceptions import StorageError, ValidationError


class FoodIndustryStorage:
    """
    食品行业PostgreSQL存储
    
    专注于EPCIS事件、追溯链、质量监控的PostgreSQL存储
    """
    
    def __init__(self, connection_string: str):
        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor()
            self._create_tables()
            logger.info("FoodIndustryStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {str(e)}", exc_info=True)
            raise StorageError(f"数据库连接失败: {str(e)}") from e
    
    def _create_tables(self):
        """创建食品行业数据表"""
        # EPCIS事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS epcis_events (
                id BIGSERIAL PRIMARY KEY,
                event_id VARCHAR(50) UNIQUE NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                epc VARCHAR(100),
                parent_id VARCHAR(100),
                child_epcs JSONB,
                input_epcs JSONB,
                output_epcs JSONB,
                transaction_id VARCHAR(50),
                action VARCHAR(20),
                biz_step VARCHAR(50),
                disposition VARCHAR(50),
                event_time TIMESTAMP NOT NULL,
                read_point VARCHAR(200),
                biz_location VARCHAR(200),
                event_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 追溯链表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS traceability_chains (
                id BIGSERIAL PRIMARY KEY,
                chain_id VARCHAR(50) UNIQUE NOT NULL,
                epc VARCHAR(100) NOT NULL,
                direction VARCHAR(20) NOT NULL,
                events JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 质量检测表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_checks (
                id BIGSERIAL PRIMARY KEY,
                check_id VARCHAR(50) UNIQUE NOT NULL,
                epc VARCHAR(100),
                batch_number VARCHAR(50),
                quality_score DECIMAL(5, 2) NOT NULL,
                passed_rules INTEGER DEFAULT 0,
                failed_rules INTEGER DEFAULT 0,
                total_rules INTEGER DEFAULT 0,
                issues JSONB,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 质量规则表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_rules (
                id BIGSERIAL PRIMARY KEY,
                rule_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                field VARCHAR(100) NOT NULL,
                rule_type VARCHAR(50) NOT NULL,
                rule_config JSONB NOT NULL,
                threshold DECIMAL(5, 2) DEFAULT 0.95,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 质量预警表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS quality_alerts (
                id BIGSERIAL PRIMARY KEY,
                alert_id VARCHAR(50) UNIQUE NOT NULL,
                epc VARCHAR(100),
                batch_number VARCHAR(50),
                rule_id VARCHAR(50),
                alert_type VARCHAR(50) NOT NULL,
                alert_message TEXT NOT NULL,
                severity VARCHAR(20) NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (rule_id) REFERENCES quality_rules(rule_id)
            )
        """)
        
        # 创建索引（优化查询性能）
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_epcis_events_epc ON epcis_events(epc, event_time DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_epcis_events_parent_id ON epcis_events(parent_id)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_epcis_events_type_time ON epcis_events(event_type, event_time DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_epcis_events_biz_step ON epcis_events(biz_step, event_time DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_traceability_chains_epc ON traceability_chains(epc, created_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_traceability_chains_direction ON traceability_chains(direction, created_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_quality_checks_epc ON quality_checks(epc, checked_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_quality_checks_batch ON quality_checks(batch_number, checked_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_quality_checks_score ON quality_checks(quality_score, checked_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_quality_alerts_epc ON quality_alerts(epc, resolved, created_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_quality_alerts_severity ON quality_alerts(severity, resolved, created_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_quality_rules_enabled ON quality_rules(enabled, updated_at DESC) WHERE enabled = TRUE")
        
        self.conn.commit()
    
    def store_epcis_event(self, event: Dict[str, Any]) -> bool:
        """
        存储EPCIS事件
        
        Args:
            event: 事件数据
            
        Returns:
            是否成功
            
        Raises:
            StorageError: 存储失败时抛出
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证输入
            if not event:
                raise ValidationError("事件数据不能为空")
            
            event_id = event.get('event_id')
            if not event_id:
                raise ValidationError("事件ID不能为空")
            
            logger.debug(f"存储EPCIS事件: {event_id}")
            
            self.cur.execute("""
                INSERT INTO epcis_events 
                (event_id, event_type, epc, parent_id, child_epcs, input_epcs, output_epcs,
                 transaction_id, action, biz_step, disposition, event_time, read_point, biz_location, event_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_id,
                event.get('event_type', ''),
                event.get('epc'),
                event.get('parent_id'),
                json.dumps(event.get('child_epcs', [])),
                json.dumps(event.get('input_epcs', [])),
                json.dumps(event.get('output_epcs', [])),
                event.get('transaction_id'),
                event.get('action'),
                event.get('biz_step'),
                event.get('disposition'),
                event.get('event_time', datetime.utcnow()),
                event.get('read_point'),
                event.get('biz_location'),
                json.dumps(event.get('event_data', {}))
            ))
            
            self.conn.commit()
            logger.info(f"EPCIS事件存储成功: {event_id}")
            return True
            
        except ValidationError:
            self.conn.rollback()
            raise
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"EPCIS事件存储失败: {str(e)}", exc_info=True)
            raise StorageError(f"事件存储失败: {str(e)}") from e
        except Exception as e:
            self.conn.rollback()
            logger.error(f"EPCIS事件存储时发生未知错误: {str(e)}", exc_info=True)
            raise StorageError(f"事件存储失败: {str(e)}") from e
    
    def store_traceability_chain(self, chain: Dict[str, Any]) -> bool:
        """存储追溯链"""
        try:
            self.cur.execute("""
                INSERT INTO traceability_chains 
                (chain_id, epc, direction, events)
                VALUES (%s, %s, %s, %s)
            """, (
                chain['chain_id'],
                chain['epc'],
                chain['direction'],
                json.dumps(chain.get('events', []))
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def store_quality_check(self, check: Dict[str, Any]) -> bool:
        """存储质量检测结果"""
        try:
            self.cur.execute("""
                INSERT INTO quality_checks 
                (check_id, epc, batch_number, quality_score, passed_rules, failed_rules, total_rules, issues)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                check.get('check_id', f"check_{datetime.utcnow().timestamp()}"),
                check.get('epc'),
                check.get('batch_number'),
                check['quality_score'],
                check.get('passed', 0),
                check.get('failed', 0),
                check.get('total', 0),
                json.dumps(check.get('issues', []))
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def store_quality_rule(self, rule: Dict[str, Any]) -> bool:
        """存储质量规则"""
        try:
            self.cur.execute("""
                INSERT INTO quality_rules 
                (rule_id, name, field, rule_type, rule_config, threshold, enabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (rule_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    field = EXCLUDED.field,
                    rule_type = EXCLUDED.rule_type,
                    rule_config = EXCLUDED.rule_config,
                    threshold = EXCLUDED.threshold,
                    enabled = EXCLUDED.enabled,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                rule['rule_id'],
                rule['name'],
                rule['field'],
                rule['rule_type'],
                json.dumps(rule.get('rule_config', {})),
                rule.get('threshold', 0.95),
                rule.get('enabled', True)
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def store_quality_alert(self, alert: Dict[str, Any]) -> bool:
        """存储质量预警"""
        try:
            self.cur.execute("""
                INSERT INTO quality_alerts 
                (alert_id, epc, batch_number, rule_id, alert_type, alert_message, severity)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                alert.get('alert_id', f"alert_{datetime.utcnow().timestamp()}"),
                alert.get('epc'),
                alert.get('batch_number'),
                alert.get('rule_id'),
                alert['alert_type'],
                alert['alert_message'],
                alert.get('severity', 'medium')
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def query_traceability_chain(self, epc: str, direction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询追溯链"""
        query = "SELECT chain_id, epc, direction, events, created_at FROM traceability_chains WHERE epc = %s"
        params = [epc]
        
        if direction:
            query += " AND direction = %s"
            params.append(direction)
        
        query += " ORDER BY created_at DESC LIMIT 1"
        
        self.cur.execute(query, params)
        row = self.cur.fetchone()
        
        if row:
            return {
                'chain_id': row[0],
                'epc': row[1],
                'direction': row[2],
                'events': json.loads(row[3]) if isinstance(row[3], str) else row[3],
                'created_at': row[4].isoformat() if isinstance(row[4], datetime) else row[4]
            }
        
        return None


def main():
    """主函数 - 示例用法"""
    storage = FoodIndustryStorage("postgresql://localhost/food_industry_db")
    
    # 存储EPCIS事件
    event = {
        'event_id': 'event_1',
        'event_type': 'ObjectEvent',
        'epc': 'urn:epc:id:sgtin:0614141.107346.20240121',
        'action': 'OBSERVE',
        'biz_step': 'shipping',
        'event_time': datetime.utcnow()
    }
    
    storage.store_epcis_event(event)
    print("EPCIS事件已存储")


if __name__ == '__main__':
    main()
