"""
办公自动化PostgreSQL存储

专注于文档管理、流程管理、协作记录的PostgreSQL存储
"""

import psycopg2
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .logger import logger
from .exceptions import StorageError, ValidationError


class OAStorage:
    """
    办公自动化PostgreSQL存储
    
    专注于文档管理、流程管理、协作记录的PostgreSQL存储
    """
    
    def __init__(self, connection_string: str):
        try:
            self.conn = psycopg2.connect(connection_string)
            self.cur = self.conn.cursor()
            self._create_tables()
            logger.info("OAStorage initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {str(e)}", exc_info=True)
            raise StorageError(f"数据库连接失败: {str(e)}") from e
    
    def _create_tables(self):
        """创建办公自动化数据表"""
        # 文档表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS oa_documents (
                id BIGSERIAL PRIMARY KEY,
                document_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                document_type VARCHAR(50) NOT NULL,
                format VARCHAR(20) NOT NULL,
                content_path TEXT,
                metadata JSONB,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 文档版本表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                id BIGSERIAL PRIMARY KEY,
                document_id VARCHAR(50) NOT NULL,
                version INTEGER NOT NULL,
                content_path TEXT,
                changes JSONB,
                created_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(document_id, version),
                FOREIGN KEY (document_id) REFERENCES oa_documents(document_id)
            )
        """)
        
        # 流程实例表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_instances (
                id BIGSERIAL PRIMARY KEY,
                instance_id VARCHAR(50) UNIQUE NOT NULL,
                workflow_id VARCHAR(50) NOT NULL,
                workflow_name VARCHAR(200) NOT NULL,
                status VARCHAR(50) NOT NULL,
                current_step VARCHAR(100),
                variables JSONB,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                created_by VARCHAR(100)
            )
        """)
        
        # 任务表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS workflow_tasks (
                id BIGSERIAL PRIMARY KEY,
                task_id VARCHAR(50) UNIQUE NOT NULL,
                instance_id VARCHAR(50) NOT NULL,
                task_name VARCHAR(200) NOT NULL,
                assignee VARCHAR(100),
                status VARCHAR(50) NOT NULL,
                due_date TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instance_id) REFERENCES workflow_instances(instance_id)
            )
        """)
        
        # 协作记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS collaboration_records (
                id BIGSERIAL PRIMARY KEY,
                record_id VARCHAR(50) UNIQUE NOT NULL,
                document_id VARCHAR(50) NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                action VARCHAR(50) NOT NULL,
                action_data JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES oa_documents(document_id)
            )
        """)
        
        # 创建索引（优化查询性能）
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON document_versions(document_id, version DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_workflow_tasks_instance_id ON workflow_tasks(instance_id, status)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_workflow_tasks_assignee ON workflow_tasks(assignee, status) WHERE assignee IS NOT NULL")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_workflow_tasks_due_date ON workflow_tasks(due_date) WHERE due_date IS NOT NULL")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_collaboration_records_document_id ON collaboration_records(document_id, timestamp DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_collaboration_records_user_id ON collaboration_records(user_id, timestamp DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_workflow_instances_status ON workflow_instances(status, started_at DESC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_oa_documents_type_format ON oa_documents(document_type, format)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_oa_documents_updated_at ON oa_documents(updated_at DESC)")
        
        # 创建全文搜索索引
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_oa_documents_name_fts ON oa_documents USING gin(to_tsvector('english', name))")
        
        self.conn.commit()
    
    def store_document(self, document: Dict[str, Any]) -> bool:
        """
        存储文档
        
        Args:
            document: 文档数据
            
        Returns:
            是否成功
            
        Raises:
            StorageError: 存储失败时抛出
            ValidationError: 数据验证失败时抛出
        """
        try:
            # 验证输入
            if not document:
                raise ValidationError("文档数据不能为空")
            
            document_id = document.get('document_id')
            if not document_id:
                raise ValidationError("文档ID不能为空")
            
            logger.debug(f"存储文档: {document_id}")
            
            self.cur.execute("""
                INSERT INTO oa_documents 
                (document_id, name, document_type, format, content_path, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    document_type = EXCLUDED.document_type,
                    format = EXCLUDED.format,
                    content_path = EXCLUDED.content_path,
                    metadata = EXCLUDED.metadata,
                    version = oa_documents.version + 1,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                document_id,
                document.get('name', ''),
                document.get('document_type', ''),
                document.get('format', ''),
                document.get('content_path'),
                json.dumps(document.get('metadata', {}))
            ))
            
            # 记录版本
            self.cur.execute("""
                SELECT version FROM oa_documents WHERE document_id = %s
            """, (document_id,))
            
            version_result = self.cur.fetchone()
            if version_result:
                version = version_result[0]
                
                self.cur.execute("""
                    INSERT INTO document_versions 
                    (document_id, version, content_path, changes, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    document_id,
                    version,
                    document.get('content_path'),
                    json.dumps(document.get('changes', {})),
                    document.get('created_by')
                ))
            
            self.conn.commit()
            logger.info(f"文档存储成功: {document_id}")
            return True
            
        except ValidationError:
            self.conn.rollback()
            raise
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"文档存储失败: {str(e)}", exc_info=True)
            raise StorageError(f"文档存储失败: {str(e)}") from e
        except Exception as e:
            self.conn.rollback()
            logger.error(f"文档存储时发生未知错误: {str(e)}", exc_info=True)
            raise StorageError(f"文档存储失败: {str(e)}") from e
    
    def store_workflow_instance(self, instance: Dict[str, Any]) -> bool:
        """存储流程实例"""
        try:
            self.cur.execute("""
                INSERT INTO workflow_instances 
                (instance_id, workflow_id, workflow_name, status, current_step, variables, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                instance['instance_id'],
                instance['workflow_id'],
                instance['workflow_name'],
                instance.get('status', 'running'),
                instance.get('current_step'),
                json.dumps(instance.get('variables', {})),
                instance.get('created_by')
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def store_task(self, task: Dict[str, Any]) -> bool:
        """存储任务"""
        try:
            self.cur.execute("""
                INSERT INTO workflow_tasks 
                (task_id, instance_id, task_name, assignee, status, due_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                task['task_id'],
                task['instance_id'],
                task['task_name'],
                task.get('assignee'),
                task.get('status', 'pending'),
                task.get('due_date')
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def store_collaboration_record(self, record: Dict[str, Any]) -> bool:
        """存储协作记录"""
        try:
            self.cur.execute("""
                INSERT INTO collaboration_records 
                (record_id, document_id, user_id, action, action_data)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                record.get('record_id', f"record_{datetime.utcnow().timestamp()}"),
                record['document_id'],
                record['user_id'],
                record['action'],
                json.dumps(record.get('action_data', {}))
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def search_documents(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """搜索文档"""
        self.cur.execute("""
            SELECT document_id, name, document_type, format, metadata, created_at
            FROM oa_documents
            WHERE to_tsvector('english', name) @@ plainto_tsquery('english', %s)
            ORDER BY created_at DESC
            LIMIT %s
        """, (query, limit))
        
        results = []
        for row in self.cur.fetchall():
            results.append({
                'document_id': row[0],
                'name': row[1],
                'document_type': row[2],
                'format': row[3],
                'metadata': json.loads(row[4]) if isinstance(row[4], str) else row[4],
                'created_at': row[5].isoformat() if isinstance(row[5], datetime) else row[5]
            })
        
        return results


def main():
    """主函数 - 示例用法"""
    storage = OAStorage("postgresql://localhost/oa_db")
    
    # 存储文档
    document = {
        'document_id': 'doc_1',
        'name': '项目计划书',
        'document_type': 'text',
        'format': 'odf',
        'content_path': '/documents/doc_1.odt',
        'metadata': {'author': 'John Doe', 'tags': ['project', 'planning']}
    }
    
    storage.store_document(document)
    print("文档已存储")


if __name__ == '__main__':
    main()
