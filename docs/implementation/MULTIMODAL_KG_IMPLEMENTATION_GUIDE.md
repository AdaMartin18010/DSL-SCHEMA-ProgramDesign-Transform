# 多模态知识图谱实现指南

## 📑 目录

- [多模态知识图谱实现指南](#多模态知识图谱实现指南)
  - [📑 目录](#-目录)
  - [1. 实现概述](#1-实现概述)
    - [1.1 实现目标](#11-实现目标)
    - [1.2 实现架构](#12-实现架构)
  - [2. 技术栈选择](#2-技术栈选择)
    - [2.1 数据库](#21-数据库)
    - [2.2 嵌入模型](#22-嵌入模型)
    - [2.3 框架](#23-框架)
  - [3. 文本模态实现](#3-文本模态实现)
    - [3.1 数据库Schema](#31-数据库schema)
    - [3.2 Python实现](#32-python实现)
  - [4. 图像模态实现](#4-图像模态实现)
    - [4.1 数据库Schema](#41-数据库schema)
    - [4.2 Python实现](#42-python实现)
  - [5. 多模态融合实现](#5-多模态融合实现)
    - [5.1 融合算法](#51-融合算法)
  - [6. 查询接口实现](#6-查询接口实现)
    - [6.1 REST API](#61-rest-api)
  - [7. PostgreSQL存储设计](#7-postgresql存储设计)
    - [7.1 完整数据库Schema](#71-完整数据库schema)
  - [8. 测试与验证](#8-测试与验证)
    - [8.1 单元测试](#81-单元测试)

---

## 1. 实现概述

### 1.1 实现目标

- ✅ 支持文本模态存储和检索
- ✅ 支持图像模态存储和检索
- ✅ 实现多模态融合算法
- ✅ 实现多模态查询接口

### 1.2 实现架构

```
多模态知识图谱系统
├── 数据层
│   ├── 文本存储（PostgreSQL + 向量数据库）
│   ├── 图像存储（PostgreSQL + 对象存储）
│   └── 元数据存储（PostgreSQL）
├── 处理层
│   ├── 文本嵌入（BERT/GPT）
│   ├── 图像嵌入（CLIP/ResNet）
│   └── 多模态融合
├── 查询层
│   ├── 文本查询
│   ├── 图像查询
│   └── 多模态查询
└── API层
    ├── REST API
    └── GraphQL API
```

---

## 2. 技术栈选择

### 2.1 数据库

- **PostgreSQL**：主数据库，存储结构化数据
- **pgvector**：PostgreSQL向量扩展，支持向量相似度搜索
- **MinIO/S3**：对象存储，存储图像文件

### 2.2 嵌入模型

- **文本嵌入**：sentence-transformers（all-MiniLM-L6-v2）
- **图像嵌入**：CLIP（openai/clip-vit-base-patch32）

### 2.3 框架

- **Python 3.10+**
- **FastAPI**：REST API框架
- **SQLAlchemy**：ORM框架
- **LangChain**：LLM集成框架

---

## 3. 文本模态实现

### 3.1 数据库Schema

```sql
-- 文本实体表
CREATE TABLE text_entities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50),  -- 'schema_doc', 'annotation', 'metadata'
    embedding vector(384),  -- all-MiniLM-L6-v2维度
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX ON text_entities USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 全文搜索索引
CREATE INDEX ON text_entities USING GIN (to_tsvector('english', content));
```

### 3.2 Python实现

```python
from sentence_transformers import SentenceTransformer
import pgvector
from sqlalchemy import create_engine, Column, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np

Base = declarative_base()

class TextEntity(Base):
    __tablename__ = 'text_entities'

    id = Column(Integer, primary_key=True)
    entity_id = Column(String(50), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50))
    embedding = Column(pgvector.sqlalchemy.Vector(384))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class TextModalityProcessor:
    """文本模态处理器"""

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.engine = create_engine('postgresql://user:pass@localhost/db')
        self.Session = sessionmaker(bind=self.engine)

    def process_text(self, entity_id: str, content: str,
                    content_type: str, metadata: dict = None):
        """处理文本并存储"""
        # 生成嵌入向量
        embedding = self.model.encode(content)

        # 存储到数据库
        session = self.Session()
        entity = TextEntity(
            entity_id=entity_id,
            content=content,
            content_type=content_type,
            embedding=embedding.tolist(),
            metadata=metadata or {}
        )
        session.add(entity)
        session.commit()
        session.close()

    def search_similar(self, query_text: str, top_k: int = 10):
        """语义相似度搜索"""
        # 生成查询向量
        query_embedding = self.model.encode(query_text)

        # 向量相似度搜索
        session = self.Session()
        results = session.query(TextEntity).order_by(
            TextEntity.embedding.cosine_distance(query_embedding.tolist())
        ).limit(top_k).all()
        session.close()

        return results
```

---

## 4. 图像模态实现

### 4.1 数据库Schema

```sql
-- 图像实体表
CREATE TABLE image_entities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) UNIQUE NOT NULL,
    image_url TEXT NOT NULL,
    image_type VARCHAR(50),  -- 'schema_diagram', 'architecture', 'flowchart'
    embedding vector(512),  -- CLIP维度
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX ON image_entities USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 4.2 Python实现

```python
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import requests
from io import BytesIO

class ImageModalityProcessor:
    """图像模态处理器"""

    def __init__(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def process_image(self, entity_id: str, image_url: str,
                     image_type: str, metadata: dict = None):
        """处理图像并存储"""
        # 加载图像
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # 生成嵌入向量
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            embedding = self.model.get_image_features(**inputs)
        embedding = embedding.cpu().numpy()[0]

        # 存储到数据库
        session = self.Session()
        entity = ImageEntity(
            entity_id=entity_id,
            image_url=image_url,
            image_type=image_type,
            embedding=embedding.tolist(),
            metadata=metadata or {}
        )
        session.add(entity)
        session.commit()
        session.close()

    def search_similar(self, query_image_url: str, top_k: int = 10):
        """图像相似度搜索"""
        # 加载查询图像
        response = requests.get(query_image_url)
        query_image = Image.open(BytesIO(response.content))

        # 生成查询向量
        inputs = self.processor(images=query_image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            query_embedding = self.model.get_image_features(**inputs)
        query_embedding = query_embedding.cpu().numpy()[0]

        # 向量相似度搜索
        session = self.Session()
        results = session.query(ImageEntity).order_by(
            ImageEntity.embedding.cosine_distance(query_embedding.tolist())
        ).limit(top_k).all()
        session.close()

        return results
```

---

## 5. 多模态融合实现

### 5.1 融合算法

```python
import numpy as np
from sklearn.decomposition import PCA

class MultimodalFusion:
    """多模态融合算法"""

    def __init__(self, fusion_method='weighted_average'):
        self.fusion_method = fusion_method

    def fuse(self, text_embedding: np.ndarray,
            image_embedding: np.ndarray,
            text_weight: float = 0.5,
            image_weight: float = 0.5):
        """融合文本和图像嵌入"""
        if self.fusion_method == 'weighted_average':
            # 对齐维度
            if text_embedding.shape[0] != image_embedding.shape[0]:
                # 使用PCA降维对齐
                min_dim = min(text_embedding.shape[0], image_embedding.shape[0])
                if text_embedding.shape[0] > min_dim:
                    pca = PCA(n_components=min_dim)
                    text_embedding = pca.fit_transform(text_embedding.reshape(1, -1))[0]
                if image_embedding.shape[0] > min_dim:
                    pca = PCA(n_components=min_dim)
                    image_embedding = pca.fit_transform(image_embedding.reshape(1, -1))[0]

            # 加权平均
            fused = text_weight * text_embedding + image_weight * image_embedding
            return fused

        elif self.fusion_method == 'concatenation':
            # 拼接
            fused = np.concatenate([text_embedding, image_embedding])
            return fused

        elif self.fusion_method == 'attention':
            # 注意力机制融合
            # 简化实现：使用可学习的权重
            attention_weights = self.compute_attention_weights(
                text_embedding, image_embedding
            )
            fused = (attention_weights[0] * text_embedding +
                    attention_weights[1] * image_embedding)
            return fused

    def compute_attention_weights(self, text_emb, image_emb):
        """计算注意力权重"""
        # 简化实现：基于嵌入的相似度
        text_norm = np.linalg.norm(text_emb)
        image_norm = np.linalg.norm(image_emb)

        text_weight = text_norm / (text_norm + image_norm)
        image_weight = image_norm / (text_norm + image_norm)

        return [text_weight, image_weight]
```

---

## 6. 查询接口实现

### 6.1 REST API

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class MultimodalQueryRequest(BaseModel):
    query_text: Optional[str] = None
    query_image_url: Optional[str] = None
    modality: str = "multimodal"  # 'text', 'image', 'multimodal'
    top_k: int = 10
    fusion_weights: Optional[dict] = None

class MultimodalQueryResponse(BaseModel):
    results: List[dict]
    query_time: float

@app.post("/api/v1/multimodal/search", response_model=MultimodalQueryResponse)
async def multimodal_search(request: MultimodalQueryRequest):
    """多模态查询接口"""
    import time
    start_time = time.time()

    text_processor = TextModalityProcessor()
    image_processor = ImageModalityProcessor()
    fusion = MultimodalFusion()

    results = []

    if request.modality == 'text' and request.query_text:
        # 文本查询
        text_results = text_processor.search_similar(
            request.query_text, request.top_k
        )
        results = [{
            'entity_id': r.entity_id,
            'content': r.content,
            'modality': 'text',
            'similarity': 1.0 - r.embedding.cosine_distance(...)
        } for r in text_results]

    elif request.modality == 'image' and request.query_image_url:
        # 图像查询
        image_results = image_processor.search_similar(
            request.query_image_url, request.top_k
        )
        results = [{
            'entity_id': r.entity_id,
            'image_url': r.image_url,
            'modality': 'image',
            'similarity': 1.0 - r.embedding.cosine_distance(...)
        } for r in image_results]

    elif request.modality == 'multimodal':
        # 多模态融合查询
        if request.query_text and request.query_image_url:
            text_emb = text_processor.model.encode(request.query_text)
            image_emb = image_processor.get_embedding(request.query_image_url)

            weights = request.fusion_weights or {'text': 0.5, 'image': 0.5}
            fused_emb = fusion.fuse(
                text_emb, image_emb,
                weights['text'], weights['image']
            )

            # 使用融合向量查询
            results = search_with_fused_embedding(fused_emb, request.top_k)

    query_time = time.time() - start_time

    return MultimodalQueryResponse(
        results=results,
        query_time=query_time
    )
```

---

## 7. PostgreSQL存储设计

### 7.1 完整数据库Schema

```sql
-- 多模态实体表（主表）
CREATE TABLE multimodal_entities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) UNIQUE NOT NULL,
    entity_type VARCHAR(50),  -- 'schema', 'concept', 'relationship'
    text_content TEXT,
    image_url TEXT,
    fused_embedding vector(512),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 文本模态表
CREATE TABLE text_modalities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES multimodal_entities(entity_id),
    content TEXT NOT NULL,
    content_type VARCHAR(50),
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 图像模态表
CREATE TABLE image_modalities (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES multimodal_entities(entity_id),
    image_url TEXT NOT NULL,
    image_type VARCHAR(50),
    embedding vector(512),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 多模态关系表
CREATE TABLE multimodal_relations (
    id SERIAL PRIMARY KEY,
    source_entity_id VARCHAR(50) REFERENCES multimodal_entities(entity_id),
    target_entity_id VARCHAR(50) REFERENCES multimodal_entities(entity_id),
    relation_type VARCHAR(50),
    confidence FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_multimodal_entities_fused_embedding
  ON multimodal_entities USING ivfflat (fused_embedding vector_cosine_ops);
CREATE INDEX idx_text_modalities_embedding
  ON text_modalities USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_image_modalities_embedding
  ON image_modalities USING ivfflat (embedding vector_cosine_ops);
```

---

## 8. 测试与验证

### 8.1 单元测试

```python
import pytest
from multimodal_kg import TextModalityProcessor, ImageModalityProcessor, MultimodalFusion

def test_text_processing():
    """测试文本处理"""
    processor = TextModalityProcessor()
    processor.process_text(
        entity_id="test_001",
        content="This is a test schema document",
        content_type="schema_doc"
    )

    results = processor.search_similar("schema document", top_k=5)
    assert len(results) > 0
    assert results[0].entity_id == "test_001"

def test_image_processing():
    """测试图像处理"""
    processor = ImageModalityProcessor()
    processor.process_image(
        entity_id="test_002",
        image_url="https://example.com/schema_diagram.png",
        image_type="schema_diagram"
    )

    results = processor.search_similar(
        "https://example.com/query_diagram.png", top_k=5
    )
    assert len(results) > 0

def test_multimodal_fusion():
    """测试多模态融合"""
    fusion = MultimodalFusion()
    text_emb = np.random.rand(384)
    image_emb = np.random.rand(512)

    fused = fusion.fuse(text_emb, image_emb)
    assert fused.shape[0] > 0
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

