# 时序知识图谱实现指南

## 📑 目录

- [时序知识图谱实现指南](#时序知识图谱实现指南)
  - [📑 目录](#-目录)
  - [1. 实现概述](#1-实现概述)
    - [1.1 实现目标](#11-实现目标)
    - [1.2 实现架构](#12-实现架构)
  - [2. 技术栈选择](#2-技术栈选择)
    - [2.1 数据库](#21-数据库)
    - [2.2 框架](#22-框架)
  - [3. 时间戳存储实现](#3-时间戳存储实现)
    - [3.1 数据库Schema](#31-数据库schema)
    - [3.2 Python实现](#32-python实现)
  - [4. 时间演化追踪实现](#4-时间演化追踪实现)
    - [4.1 演化追踪算法](#41-演化追踪算法)
  - [5. 时间推理算法实现](#5-时间推理算法实现)
    - [5.1 时间推理规则](#51-时间推理规则)
  - [6. 时间查询接口实现](#6-时间查询接口实现)
    - [6.1 REST API](#61-rest-api)
  - [7. PostgreSQL存储设计](#7-postgresql存储设计)
    - [7.1 完整数据库Schema](#71-完整数据库schema)
  - [8. 测试与验证](#8-测试与验证)
    - [8.1 单元测试](#81-单元测试)

---

## 1. 实现概述

### 1.1 实现目标

- ✅ 支持时间戳和时间区间存储
- ✅ 实现时间演化追踪
- ✅ 实现时间推理算法
- ✅ 实现时间查询接口

### 1.2 实现架构

```
时序知识图谱系统
├── 数据层
│   ├── 实体时间表（PostgreSQL）
│   ├── 关系时间表（PostgreSQL）
│   └── 历史快照表（PostgreSQL）
├── 处理层
│   ├── 时间戳处理
│   ├── 演化追踪
│   └── 时间推理
├── 查询层
│   ├── 时间点查询
│   ├── 时间区间查询
│   └── 演化查询
└── API层
    └── REST API
```

---

## 2. 技术栈选择

### 2.1 数据库

- **PostgreSQL**：主数据库，支持时间类型和范围类型
- **PostgreSQL Range Types**：时间区间支持

### 2.2 框架

- **Python 3.10+**
- **FastAPI**：REST API框架
- **SQLAlchemy**：ORM框架
- **pandas**：时间序列处理

---

## 3. 时间戳存储实现

### 3.1 数据库Schema

```sql
-- 时序实体表
CREATE TABLE temporal_entities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,  -- NULL表示持续有效
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(entity_id, valid_from)
);

-- 时序关系表
CREATE TABLE temporal_relations (
    id SERIAL PRIMARY KEY,
    source_entity_id VARCHAR(50) NOT NULL,
    target_entity_id VARCHAR(50) NOT NULL,
    relation_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (source_entity_id, valid_from)
      REFERENCES temporal_entities(entity_id, valid_from),
    FOREIGN KEY (target_entity_id, valid_from)
      REFERENCES temporal_entities(entity_id, valid_from)
);

-- 时间索引
CREATE INDEX idx_temporal_entities_time
  ON temporal_entities(valid_from, valid_to);
CREATE INDEX idx_temporal_entities_entity_time
  ON temporal_entities(entity_id, valid_from);
CREATE INDEX idx_temporal_relations_time
  ON temporal_relations(valid_from, valid_to);
```

### 3.2 Python实现

```python
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()

class TemporalEntity(Base):
    __tablename__ = 'temporal_entities'

    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime)  # None表示持续有效
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class TemporalRelation(Base):
    __tablename__ = 'temporal_relations'

    id = Column(Integer, primary_key=True)
    source_entity_id = Column(String(50), nullable=False)
    target_entity_id = Column(String(50), nullable=False)
    relation_type = Column(String(50), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime)
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)

class TemporalKGProcessor:
    """时序知识图谱处理器"""

    def __init__(self):
        self.engine = create_engine('postgresql://user:pass@localhost/db')
        self.Session = sessionmaker(bind=self.engine)

    def add_entity(self, entity_id: str, entity_type: str,
                   valid_from: datetime, valid_to: Optional[datetime] = None,
                   properties: dict = None):
        """添加时序实体"""
        session = self.Session()
        entity = TemporalEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            valid_from=valid_from,
            valid_to=valid_to,
            properties=properties or {}
        )
        session.add(entity)
        session.commit()
        session.close()

    def update_entity(self, entity_id: str, new_properties: dict,
                     update_time: datetime):
        """更新实体（创建新版本）"""
        # 结束旧版本
        session = self.Session()
        old_entity = session.query(TemporalEntity).filter(
            TemporalEntity.entity_id == entity_id,
            TemporalEntity.valid_to.is_(None)
        ).first()

        if old_entity:
            old_entity.valid_to = update_time

        # 创建新版本
        new_entity = TemporalEntity(
            entity_id=entity_id,
            entity_type=old_entity.entity_type if old_entity else None,
            valid_from=update_time,
            valid_to=None,
            properties=new_properties
        )
        session.add(new_entity)
        session.commit()
        session.close()
```

---

## 4. 时间演化追踪实现

### 4.1 演化追踪算法

```python
class TemporalEvolutionTracker:
    """时间演化追踪器"""

    def __init__(self):
        self.kg_processor = TemporalKGProcessor()

    def track_entity_evolution(self, entity_id: str,
                              start_time: datetime,
                              end_time: datetime):
        """追踪实体演化"""
        session = self.kg_processor.Session()

        # 获取时间区间内的所有版本
        versions = session.query(TemporalEntity).filter(
            TemporalEntity.entity_id == entity_id,
            TemporalEntity.valid_from <= end_time,
            or_(
                TemporalEntity.valid_to >= start_time,
                TemporalEntity.valid_to.is_(None)
            )
        ).order_by(TemporalEntity.valid_from).all()

        evolution = []
        for i, version in enumerate(versions):
            evolution.append({
                'version': i + 1,
                'valid_from': version.valid_from,
                'valid_to': version.valid_to,
                'properties': version.properties,
                'changes': self.compute_changes(
                    versions[i-1].properties if i > 0 else {},
                    version.properties
                )
            })

        session.close()
        return evolution

    def compute_changes(self, old_props: dict, new_props: dict):
        """计算属性变化"""
        changes = {
            'added': {},
            'removed': {},
            'modified': {}
        }

        # 新增和修改的属性
        for key, value in new_props.items():
            if key not in old_props:
                changes['added'][key] = value
            elif old_props[key] != value:
                changes['modified'][key] = {
                    'old': old_props[key],
                    'new': value
                }

        # 删除的属性
        for key in old_props:
            if key not in new_props:
                changes['removed'][key] = old_props[key]

        return changes
```

---

## 5. 时间推理算法实现

### 5.1 时间推理规则

```python
class TemporalReasoning:
    """时间推理算法"""

    def __init__(self):
        self.kg_processor = TemporalKGProcessor()

    def infer_temporal_relations(self, entity1_id: str, entity2_id: str,
                                query_time: datetime):
        """推理时间关系"""
        # 获取实体在查询时间点的状态
        entity1 = self.get_entity_at_time(entity1_id, query_time)
        entity2 = self.get_entity_at_time(entity2_id, query_time)

        if not entity1 or not entity2:
            return None

        # 推理时间关系
        relations = []

        # 1. 时间顺序关系
        if entity1.valid_from < entity2.valid_from:
            relations.append({
                'type': 'before',
                'entity1': entity1_id,
                'entity2': entity2_id,
                'confidence': 1.0
            })

        # 2. 时间重叠关系
        if self.time_overlap(entity1, entity2):
            relations.append({
                'type': 'overlaps',
                'entity1': entity1_id,
                'entity2': entity2_id,
                'confidence': 0.9
            })

        # 3. 时间包含关系
        if self.time_contains(entity1, entity2):
            relations.append({
                'type': 'contains',
                'entity1': entity1_id,
                'entity2': entity2_id,
                'confidence': 0.8
            })

        return relations

    def get_entity_at_time(self, entity_id: str, query_time: datetime):
        """获取时间点的实体状态"""
        session = self.kg_processor.Session()
        entity = session.query(TemporalEntity).filter(
            TemporalEntity.entity_id == entity_id,
            TemporalEntity.valid_from <= query_time,
            or_(
                TemporalEntity.valid_to >= query_time,
                TemporalEntity.valid_to.is_(None)
            )
        ).first()
        session.close()
        return entity

    def time_overlap(self, entity1: TemporalEntity, entity2: TemporalEntity):
        """判断时间是否重叠"""
        e1_end = entity1.valid_to or datetime.max
        e2_end = entity2.valid_to or datetime.max

        return (entity1.valid_from < e2_end and entity2.valid_from < e1_end)

    def time_contains(self, entity1: TemporalEntity, entity2: TemporalEntity):
        """判断entity1是否包含entity2的时间区间"""
        e1_end = entity1.valid_to or datetime.max
        e2_end = entity2.valid_to or datetime.max

        return (entity1.valid_from <= entity2.valid_from and
                e1_end >= e2_end)
```

---

## 6. 时间查询接口实现

### 6.1 REST API

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI()

class TemporalQueryRequest(BaseModel):
    entity_id: Optional[str] = None
    query_time: datetime
    relation_type: Optional[str] = None
    time_range: Optional[dict] = None  # {'start': datetime, 'end': datetime}

class TemporalQueryResponse(BaseModel):
    entities: List[dict]
    relations: List[dict]
    query_time: float

@app.post("/api/v1/temporal/query", response_model=TemporalQueryResponse)
async def temporal_query(request: TemporalQueryRequest):
    """时间查询接口"""
    import time
    start_time = time.time()

    processor = TemporalKGProcessor()
    reasoning = TemporalReasoning()

    entities = []
    relations = []

    if request.entity_id:
        # 查询特定实体在时间点的状态
        entity = reasoning.get_entity_at_time(
            request.entity_id, request.query_time
        )
        if entity:
            entities.append({
                'entity_id': entity.entity_id,
                'entity_type': entity.entity_type,
                'properties': entity.properties,
                'valid_from': entity.valid_from.isoformat(),
                'valid_to': entity.valid_to.isoformat() if entity.valid_to else None
            })

    if request.time_range:
        # 时间区间查询
        entities_list = processor.query_entities_in_range(
            request.time_range['start'],
            request.time_range['end']
        )
        entities.extend([{
            'entity_id': e.entity_id,
            'entity_type': e.entity_type,
            'properties': e.properties,
            'valid_from': e.valid_from.isoformat(),
            'valid_to': e.valid_to.isoformat() if e.valid_to else None
        } for e in entities_list])

    query_time = time.time() - start_time

    return TemporalQueryResponse(
        entities=entities,
        relations=relations,
        query_time=query_time
    )
```

---

## 7. PostgreSQL存储设计

### 7.1 完整数据库Schema

```sql
-- 时序实体表
CREATE TABLE temporal_entities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(entity_id, valid_from)
);

-- 时序关系表
CREATE TABLE temporal_relations (
    id SERIAL PRIMARY KEY,
    source_entity_id VARCHAR(50) NOT NULL,
    target_entity_id VARCHAR(50) NOT NULL,
    relation_type VARCHAR(50) NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 历史快照表（用于快速查询历史状态）
CREATE TABLE entity_snapshots (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) NOT NULL,
    snapshot_time TIMESTAMP NOT NULL,
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(entity_id, snapshot_time)
);

-- 索引
CREATE INDEX idx_temporal_entities_time
  ON temporal_entities(valid_from, valid_to);
CREATE INDEX idx_temporal_entities_entity_time
  ON temporal_entities(entity_id, valid_from);
CREATE INDEX idx_temporal_relations_time
  ON temporal_relations(valid_from, valid_to);
CREATE INDEX idx_entity_snapshots_time
  ON entity_snapshots(entity_id, snapshot_time);
```

---

## 8. 测试与验证

### 8.1 单元测试

```python
import pytest
from datetime import datetime, timedelta
from temporal_kg import TemporalKGProcessor, TemporalReasoning

def test_temporal_entity_storage():
    """测试时序实体存储"""
    processor = TemporalKGProcessor()
    now = datetime.now()

    processor.add_entity(
        entity_id="schema_001",
        entity_type="schema",
        valid_from=now,
        properties={"version": "1.0"}
    )

    # 更新实体
    processor.update_entity(
        entity_id="schema_001",
        new_properties={"version": "2.0"},
        update_time=now + timedelta(days=1)
    )

    # 查询历史版本
    entity = processor.get_entity_at_time("schema_001", now)
    assert entity.properties["version"] == "1.0"

    entity = processor.get_entity_at_time("schema_001", now + timedelta(days=1))
    assert entity.properties["version"] == "2.0"

def test_temporal_reasoning():
    """测试时间推理"""
    reasoning = TemporalReasoning()

    # 添加两个实体
    processor = TemporalKGProcessor()
    now = datetime.now()
    processor.add_entity("entity_001", "schema", now)
    processor.add_entity("entity_002", "schema", now + timedelta(days=1))

    # 推理时间关系
    relations = reasoning.infer_temporal_relations(
        "entity_001", "entity_002", now + timedelta(days=2)
    )

    assert len(relations) > 0
    assert any(r['type'] == 'before' for r in relations)
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

