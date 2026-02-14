# PostgreSQL OA数据存储完整实现

## 概述

本文档提供完整的PostgreSQL办公自动化数据存储实现，包括数据库设计、数据访问层、查询优化和数据分析功能。

---

## 1. 数据库存储完整实现

```python
"""
OA PostgreSQL存储实现
完整的数据库访问层和数据管理功能
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

logger = logging.getLogger(__name__)


@dataclass
class DocumentRecord:
    """文档记录"""
    document_id: str
    document_title: str
    document_type: str
    author: str
    file_path: str
    file_size: int = 0
    mime_type: str = ""
    current_version: int = 1
    department: str = ""
    security_level: str = "Normal"
    tags: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class ProcessInstanceRecord:
    """流程实例记录"""
    instance_id: str
    process_id: str
    process_name: str
    process_type: str
    submitter: str
    current_status: str
    current_node: str
    submit_time: datetime
    complete_time: Optional[datetime] = None
    process_data: Dict[str, Any] = None
    priority: str = "Medium"
    
    def __post_init__(self):
        if self.process_data is None:
            self.process_data = {}


@dataclass
class TaskRecord:
    """任务记录"""
    task_id: str
    task_title: str
    task_description: str
    assignee: str
    assigner: str
    task_status: str = "Todo"
    priority: str = "Medium"
    due_date: Optional[datetime] = None
    process_id: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class PostgreSQLConnectionPool:
    """PostgreSQL连接池"""
    
    def __init__(self, min_conn: int = 1, max_conn: int = 10, **conn_kwargs):
        self.conn_kwargs = conn_kwargs
        self.pool = ThreadedConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            **conn_kwargs
        )
    
    @contextmanager
    def get_connection(self):
        """获取连接上下文管理器"""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=None):
        """获取游标上下文管理器"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def close(self):
        """关闭连接池"""
        self.pool.closeall()


class OAStorageManager:
    """OA存储管理器 - 完整实现"""
    
    def __init__(self, connection_string: str = None, pool: PostgreSQLConnectionPool = None):
        """初始化存储管理器"""
        if pool:
            self.pool = pool
        elif connection_string:
            self.pool = PostgreSQLConnectionPool(
                dsn=connection_string
            )
        else:
            raise ValueError("Must provide either connection_string or pool")
        
        self._init_database()
    
    def _init_database(self):
        """初始化数据库结构和索引"""
        with self.pool.get_cursor() as cur:
            # 创建文档表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_documents (
                    id BIGSERIAL PRIMARY KEY,
                    document_id VARCHAR(50) UNIQUE NOT NULL,
                    document_title VARCHAR(500) NOT NULL,
                    document_type VARCHAR(50) NOT NULL,
                    author VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    file_path VARCHAR(1000) NOT NULL,
                    file_size BIGINT DEFAULT 0,
                    mime_type VARCHAR(100),
                    current_version INTEGER DEFAULT 1,
                    security_level VARCHAR(20) DEFAULT 'Normal',
                    tags JSONB DEFAULT '[]',
                    is_deleted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建文档版本表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_document_versions (
                    id BIGSERIAL PRIMARY KEY,
                    document_id VARCHAR(50) NOT NULL,
                    version_number INTEGER NOT NULL,
                    version_author VARCHAR(100) NOT NULL,
                    version_comment TEXT,
                    version_file_path VARCHAR(1000) NOT NULL,
                    file_size BIGINT,
                    checksum VARCHAR(64),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES oa_documents(document_id) ON DELETE CASCADE,
                    UNIQUE(document_id, version_number)
                )
            """)
            
            # 创建流程实例表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_process_instances (
                    id BIGSERIAL PRIMARY KEY,
                    instance_id VARCHAR(50) UNIQUE NOT NULL,
                    process_id VARCHAR(50) NOT NULL,
                    process_name VARCHAR(200) NOT NULL,
                    process_type VARCHAR(50) NOT NULL,
                    submitter VARCHAR(100) NOT NULL,
                    current_status VARCHAR(50) NOT NULL,
                    current_node VARCHAR(50),
                    priority VARCHAR(20) DEFAULT 'Medium',
                    submit_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    complete_time TIMESTAMP WITH TIME ZONE,
                    duration_seconds INTEGER,
                    process_data JSONB DEFAULT '{}',
                    tenant_id VARCHAR(50),
                    business_key VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建审批记录表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_approval_records (
                    id BIGSERIAL PRIMARY KEY,
                    record_id VARCHAR(50) UNIQUE NOT NULL,
                    instance_id VARCHAR(50) NOT NULL,
                    node_id VARCHAR(50) NOT NULL,
                    node_name VARCHAR(200),
                    approver VARCHAR(100) NOT NULL,
                    approval_result VARCHAR(50) NOT NULL,
                    approval_comment TEXT,
                    approval_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    next_node_id VARCHAR(50),
                    FOREIGN KEY (instance_id) REFERENCES oa_process_instances(instance_id) ON DELETE CASCADE
                )
            """)
            
            # 创建任务表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_tasks (
                    id BIGSERIAL PRIMARY KEY,
                    task_id VARCHAR(50) UNIQUE NOT NULL,
                    task_title VARCHAR(500) NOT NULL,
                    task_description TEXT,
                    assignee VARCHAR(100) NOT NULL,
                    assigner VARCHAR(100) NOT NULL,
                    task_status VARCHAR(50) DEFAULT 'Todo',
                    priority VARCHAR(20) DEFAULT 'Medium',
                    due_date TIMESTAMP WITH TIME ZONE,
                    completed_date TIMESTAMP WITH TIME ZONE,
                    process_id VARCHAR(50),
                    process_instance_id VARCHAR(50),
                    estimated_hours DECIMAL(8,2),
                    actual_hours DECIMAL(8,2),
                    tags JSONB DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (process_instance_id) REFERENCES oa_process_instances(instance_id) ON DELETE SET NULL
                )
            """)
            
            # 创建文档内容表（全文检索）
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_document_contents (
                    id BIGSERIAL PRIMARY KEY,
                    document_id VARCHAR(50) NOT NULL,
                    version_number INTEGER NOT NULL,
                    content_text TEXT,
                    content_html TEXT,
                    extracted_metadata JSONB DEFAULT '{}',
                    word_count INTEGER DEFAULT 0,
                    page_count INTEGER DEFAULT 0,
                    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES oa_documents(document_id) ON DELETE CASCADE,
                    UNIQUE(document_id, version_number)
                )
            """)
            
            # 创建协作记录表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_collaboration_records (
                    id BIGSERIAL PRIMARY KEY,
                    record_id VARCHAR(50) UNIQUE NOT NULL,
                    document_id VARCHAR(50) NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    action_description TEXT,
                    action_data JSONB DEFAULT '{}',
                    session_id VARCHAR(100),
                    action_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES oa_documents(document_id) ON DELETE CASCADE
                )
            """)
            
            # 创建文档权限表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_document_permissions (
                    id BIGSERIAL PRIMARY KEY,
                    document_id VARCHAR(50) NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    permission_type VARCHAR(20) NOT NULL,
                    granted_by VARCHAR(100),
                    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    valid_until TIMESTAMP WITH TIME ZONE,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (document_id) REFERENCES oa_documents(document_id) ON DELETE CASCADE,
                    UNIQUE(document_id, user_id, permission_type)
                )
            """)
            
            # 创建流程变量表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oa_process_variables (
                    id BIGSERIAL PRIMARY KEY,
                    instance_id VARCHAR(50) NOT NULL,
                    variable_name VARCHAR(100) NOT NULL,
                    variable_value JSONB NOT NULL,
                    variable_type VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (instance_id) REFERENCES oa_process_instances(instance_id) ON DELETE CASCADE,
                    UNIQUE(instance_id, variable_name)
                )
            """)
            
            # 创建索引
            self._create_indexes(cur)
            
            logger.info("Database initialized successfully")
    
    def _create_indexes(self, cur):
        """创建数据库索引"""
        # 文档表索引
        indexes = [
            ("idx_oa_documents_author", "oa_documents(author)"),
            ("idx_oa_documents_type", "oa_documents(document_type)"),
            ("idx_oa_documents_department", "oa_documents(department)"),
            ("idx_oa_documents_created", "oa_documents(created_at DESC)"),
            ("idx_oa_documents_tags", "oa_documents USING GIN(tags)"),
            ("idx_oa_documents_deleted", "oa_documents(is_deleted)"),
            
            # 文档版本表索引
            ("idx_doc_versions_doc_id", "oa_document_versions(document_id, version_number DESC)"),
            
            # 流程实例表索引
            ("idx_process_instances_id", "oa_process_instances(instance_id)"),
            ("idx_process_instances_status", "oa_process_instances(current_status)"),
            ("idx_process_instances_submitter", "oa_process_instances(submitter)"),
            ("idx_process_instances_type", "oa_process_instances(process_type)"),
            ("idx_process_instances_submit_time", "oa_process_instances(submit_time DESC)"),
            ("idx_process_instances_data", "oa_process_instances USING GIN(process_data)"),
            
            # 审批记录表索引
            ("idx_approval_records_instance", "oa_approval_records(instance_id, approval_time DESC)"),
            ("idx_approval_records_approver", "oa_approval_records(approver)"),
            
            # 任务表索引
            ("idx_tasks_assignee", "oa_tasks(assignee, task_status)"),
            ("idx_tasks_status", "oa_tasks(task_status)"),
            ("idx_tasks_due_date", "oa_tasks(due_date)"),
            ("idx_tasks_created", "oa_tasks(created_at DESC)"),
            
            # 文档内容全文索引
            ("idx_doc_contents_fulltext", "oa_document_contents USING GIN(to_tsvector('english', content_text))"),
            
            # 协作记录索引
            ("idx_collab_records_doc", "oa_collaboration_records(document_id, action_time DESC)"),
            
            # 权限表索引
            ("idx_doc_permissions_user", "oa_document_permissions(user_id, is_active)"),
        ]
        
        for index_name, index_def in indexes:
            try:
                cur.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
            except Exception as e:
                logger.warning(f"Failed to create index {index_name}: {e}")
    
    # ============== 文档操作 ==============
    
    def store_document(self, document: DocumentRecord) -> bool:
        """存储文档"""
        try:
            with self.pool.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO oa_documents (
                        document_id, document_title, document_type, author, department,
                        file_path, file_size, mime_type, current_version, security_level,
                        tags, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (document_id) DO UPDATE SET
                        document_title = EXCLUDED.document_title,
                        current_version = EXCLUDED.current_version,
                        file_path = EXCLUDED.file_path,
                        file_size = EXCLUDED.file_size,
                        updated_at = EXCLUDED.updated_at
                """, (
                    document.document_id, document.document_title, document.document_type,
                    document.author, document.department, document.file_path,
                    document.file_size, document.mime_type, document.current_version,
                    document.security_level, json.dumps(document.tags),
                    document.created_at, document.updated_at
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to store document: {e}")
            return False
    
    def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        """获取文档"""
        try:
            with self.pool.get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM oa_documents 
                    WHERE document_id = %s AND is_deleted = FALSE
                """, (document_id,))
                
                row = cur.fetchone()
                if row:
                    return DocumentRecord(
                        document_id=row['document_id'],
                        document_title=row['document_title'],
                        document_type=row['document_type'],
                        author=row['author'],
                        file_path=row['file_path'],
                        file_size=row['file_size'],
                        mime_type=row['mime_type'],
                        current_version=row['current_version'],
                        department=row['department'],
                        security_level=row['security_level'],
                        tags=row['tags'] if row['tags'] else [],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None
    
    def search_documents(self, query: str, filters: Dict[str, Any] = None,
                        limit: int = 50, offset: int = 0) -> Tuple[List[DocumentRecord], int]:
        """搜索文档"""
        try:
            with self.pool.get_cursor(cursor_factory=RealDictCursor) as cur:
                # 构建查询条件
                conditions = ["is_deleted = FALSE"]
                params = []
                
                if query:
                    # 全文搜索
                    cur.execute("""
                        SELECT DISTINCT dc.document_id
                        FROM oa_document_contents dc
                        WHERE to_tsvector('english', dc.content_text) @@ plainto_tsquery('english', %s)
                    """, (query,))
                    doc_ids = [r['document_id'] for r in cur.fetchall()]
                    
                    if doc_ids:
                        conditions.append(f"document_id = ANY(%s)")
                        params.append(doc_ids)
                    else:
                        # 回退到标题搜索
                        conditions.append("document_title ILIKE %s")
                        params.append(f"%{query}%")
                
                if filters:
                    if 'author' in filters:
                        conditions.append("author = %s")
                        params.append(filters['author'])
                    if 'document_type' in filters:
                        conditions.append("document_type = %s")
                        params.append(filters['document_type'])
                    if 'department' in filters:
                        conditions.append("department = %s")
                        params.append(filters['department'])
                
                where_clause = " AND ".join(conditions)
                
                # 获取总数
                cur.execute(f"""
                    SELECT COUNT(*) as total FROM oa_documents WHERE {where_clause}
                """, params)
                total = cur.fetchone()['total']
                
                # 获取结果
                cur.execute(f"""
                    SELECT * FROM oa_documents 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, params + [limit, offset])
                
                documents = []
                for row in cur.fetchall():
                    documents.append(DocumentRecord(
                        document_id=row['document_id'],
                        document_title=row['document_title'],
                        document_type=row['document_type'],
                        author=row['author'],
                        file_path=row['file_path'],
                        department=row['department'],
                        created_at=row['created_at']
                    ))
                
                return documents, total
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return [], 0
    
    # ============== 流程操作 ==============
    
    def store_process_instance(self, instance: ProcessInstanceRecord) -> bool:
        """存储流程实例"""
        try:
            with self.pool.get_cursor() as cur:
                # 计算持续时间
                duration = None
                if instance.complete_time and instance.submit_time:
                    duration = int((instance.complete_time - instance.submit_time).total_seconds())
                
                cur.execute("""
                    INSERT INTO oa_process_instances (
                        instance_id, process_id, process_name, process_type, submitter,
                        current_status, current_node, priority, submit_time, complete_time,
                        duration_seconds, process_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (instance_id) DO UPDATE SET
                        current_status = EXCLUDED.current_status,
                        current_node = EXCLUDED.current_node,
                        complete_time = EXCLUDED.complete_time,
                        duration_seconds = EXCLUDED.duration_seconds,
                        process_data = EXCLUDED.process_data,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    instance.instance_id, instance.process_id, instance.process_name,
                    instance.process_type, instance.submitter, instance.current_status,
                    instance.current_node, instance.priority, instance.submit_time,
                    instance.complete_time, duration, json.dumps(instance.process_data)
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to store process instance: {e}")
            return False
    
    def get_process_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取流程统计"""
        try:
            with self.pool.get_cursor(cursor_factory=RealDictCursor) as cur:
                start_date = datetime.now() - timedelta(days=days)
                
                # 总体统计
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_instances,
                        COUNT(*) FILTER (WHERE current_status = 'Completed') as completed,
                        COUNT(*) FILTER (WHERE current_status = 'Running') as running,
                        COUNT(*) FILTER (WHERE current_status = 'Error') as error,
                        AVG(duration_seconds) FILTER (WHERE duration_seconds IS NOT NULL) as avg_duration,
                        AVG(duration_seconds) FILTER (WHERE duration_seconds IS NOT NULL AND current_status = 'Completed') as avg_completed_duration
                    FROM oa_process_instances
                    WHERE submit_time >= %s
                """, (start_date,))
                
                stats = dict(cur.fetchone())
                
                # 按流程类型统计
                cur.execute("""
                    SELECT 
                        process_type,
                        COUNT(*) as count,
                        AVG(duration_seconds) FILTER (WHERE duration_seconds IS NOT NULL) as avg_duration
                    FROM oa_process_instances
                    WHERE submit_time >= %s
                    GROUP BY process_type
                    ORDER BY count DESC
                """, (start_date,))
                
                stats['by_type'] = [dict(r) for r in cur.fetchall()]
                
                # 每日趋势
                cur.execute("""
                    SELECT 
                        DATE(submit_time) as date,
                        COUNT(*) as new_instances,
                        COUNT(*) FILTER (WHERE current_status = 'Completed') as completed_instances
                    FROM oa_process_instances
                    WHERE submit_time >= %s
                    GROUP BY DATE(submit_time)
                    ORDER BY date
                """, (start_date,))
                
                stats['daily_trend'] = [dict(r) for r in cur.fetchall()]
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get process statistics: {e}")
            return {}
    
    # ============== 任务操作 ==============
    
    def store_task(self, task: TaskRecord) -> bool:
        """存储任务"""
        try:
            with self.pool.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO oa_tasks (
                        task_id, task_title, task_description, assignee, assigner,
                        task_status, priority, due_date, process_id, process_instance_id,
                        estimated_hours, tags, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (task_id) DO UPDATE SET
                        task_status = EXCLUDED.task_status,
                        completed_date = EXCLUDED.completed_date,
                        actual_hours = EXCLUDED.actual_hours,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    task.task_id, task.task_title, task.task_description,
                    task.assignee, task.assigner, task.task_status, task.priority,
                    task.due_date, task.process_id, task.process_instance_id,
                    task.estimated_hours, json.dumps([]), task.created_at
                ))
                return True
        except Exception as e:
            logger.error(f"Failed to store task: {e}")
            return False
    
    def get_user_tasks(self, assignee: str, status: str = None,
                      priority: str = None, limit: int = 50) -> List[TaskRecord]:
        """获取用户任务"""
        try:
            with self.pool.get_cursor(cursor_factory=RealDictCursor) as cur:
                conditions = ["assignee = %s"]
                params = [assignee]
                
                if status:
                    conditions.append("task_status = %s")
                    params.append(status)
                if priority:
                    conditions.append("priority = %s")
                    params.append(priority)
                
                where_clause = " AND ".join(conditions)
                
                cur.execute(f"""
                    SELECT * FROM oa_tasks 
                    WHERE {where_clause}
                    ORDER BY 
                        CASE priority 
                            WHEN 'High' THEN 1 
                            WHEN 'Medium' THEN 2 
                            ELSE 3 
                        END,
                        due_date ASC NULLS LAST,
                        created_at DESC
                    LIMIT %s
                """, params + [limit])
                
                tasks = []
                for row in cur.fetchall():
                    tasks.append(TaskRecord(
                        task_id=row['task_id'],
                        task_title=row['task_title'],
                        task_description=row['task_description'],
                        assignee=row['assignee'],
                        assigner=row['assigner'],
                        task_status=row['task_status'],
                        priority=row['priority'],
                        due_date=row['due_date']
                    ))
                return tasks
        except Exception as e:
            logger.error(f"Failed to get user tasks: {e}")
            return []
    
    def get_task_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取任务统计"""
        try:
            with self.pool.get_cursor(cursor_factory=RealDictCursor) as cur:
                start_date = datetime.now() - timedelta(days=days)
                
                cur.execute("""
                    SELECT 
                        task_status,
                        priority,
                        COUNT(*) as count,
                        AVG(actual_hours) as avg_actual_hours
                    FROM oa_tasks
                    WHERE created_at >= %s
                    GROUP BY task_status, priority
                    ORDER BY task_status, priority
                """, (start_date,))
                
                stats = {'by_status_priority': [dict(r) for r in cur.fetchall()]}
                
                # 过期任务
                cur.execute("""
                    SELECT COUNT(*) as overdue_count
                    FROM oa_tasks
                    WHERE task_status IN ('Todo', 'InProgress')
                    AND due_date < CURRENT_TIMESTAMP
                """)
                stats['overdue_count'] = cur.fetchone()['overdue_count']
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get task statistics: {e}")
            return {}
    
    # ============== 高级查询 ==============
    
    def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """获取仪表板数据"""
        try:
            dashboard = {
                'pending_tasks': [],
                'recent_documents': [],
                'process_summary': {},
                'notifications': []
            }
            
            with self.pool.get_cursor(cursor_factory=RealDictCursor) as cur:
                # 待办任务
                cur.execute("""
                    SELECT * FROM oa_tasks 
                    WHERE assignee = %s AND task_status IN ('Todo', 'InProgress')
                    ORDER BY due_date ASC NULLS LAST
                    LIMIT 10
                """, (user_id,))
                dashboard['pending_tasks'] = [dict(r) for r in cur.fetchall()]
                
                # 最近文档
                cur.execute("""
                    SELECT document_id, document_title, author, created_at
                    FROM oa_documents
                    WHERE is_deleted = FALSE
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                dashboard['recent_documents'] = [dict(r) for r in cur.fetchall()]
                
                # 流程摘要
                cur.execute("""
                    SELECT 
                        current_status,
                        COUNT(*) as count
                    FROM oa_process_instances
                    WHERE submitter = %s
                    AND submit_time >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY current_status
                """, (user_id,))
                dashboard['process_summary'] = {r['current_status']: r['count'] for r in cur.fetchall()}
                
                return dashboard
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {}
    
    def execute_custom_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行自定义查询"""
        try:
            with self.pool.get_cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params or ())
                return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to execute custom query: {e}")
            return []
    
    def close(self):
        """关闭连接"""
        self.pool.close()


# 使用示例
if __name__ == "__main__":
    # 初始化存储管理器
    storage = OAStorageManager(
        connection_string="postgresql://user:password@localhost:5432/oa_db"
    )
    
    # 存储文档
    doc = DocumentRecord(
        document_id="DOC-001",
        document_title="项目计划书",
        document_type="Word",
        author="张三",
        file_path="/docs/project_plan.docx",
        department="研发部",
        tags=["项目", "计划", "2025"]
    )
    storage.store_document(doc)
    
    # 搜索文档
    results, total = storage.search_documents("计划")
    print(f"Found {total} documents")
    
    # 获取仪表板数据
    dashboard = storage.get_dashboard_data("张三")
    print(f"Pending tasks: {len(dashboard['pending_tasks'])}")
```

---

**创建时间**: 2025-01-21
**代码行数**: 800+行
