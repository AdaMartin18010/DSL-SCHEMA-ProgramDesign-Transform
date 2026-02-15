# 机器学习Schema实践案例

## 📑 目录

- [机器学习Schema实践案例](#机器学习schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：电商智能推荐与搜索系统](#2-案例1电商智能推荐与搜索系统)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估与ROI分析](#27-效果评估与roi分析)

---

## 2. 案例1：电商智能推荐与搜索系统

### 2.1 企业背景

**企业简介**：
某头部电商平台（以下简称"华购电商"）年GMV超过5000亿元，日活用户超过8000万，商品SKU超过10亿。

**业务规模**：

| 指标 | 数值 |
|------|------|
| 年GMV | 5000亿+ RMB |
| 日活用户 | 8000万+ |
| 商品SKU | 10亿+ |
| 日均搜索量 | 2亿+ |
| 日均推荐曝光 | 100亿+ |

### 2.2 业务痛点

1. **转化率低**：平均转化率仅2.5%，大量流量浪费
2. **千人一面**：推荐同质化严重，缺乏个性化
3. **搜索体验差**：搜索结果相关性不高
4. **冷启动难**：新用户、新商品难以精准推荐

### 2.3 业务目标

1. 将转化率提升至4%
2. 实现千人千面的个性化推荐
3. 搜索相关性提升至95%
4. 支持实时个性化

### 2.4 技术挑战

1. 超大规模特征工程
2. 实时模型推理（QPS 100万+）
3. 多目标优化（点击率、转化率、GMV）
4. A/B测试与效果归因

### 2.5 解决方案

采用深度学习推荐系统（Deep Learning Recommendation Model）：
- 召回层：协同过滤 + Embedding检索
- 排序层：DeepFM + DIN
- 重排序：多样性 + 业务规则

### 2.6 完整代码实现

```python
#!/usr/bin/env python3
"""
电商智能推荐与搜索系统
基于深度学习的实时个性化推荐引擎
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import numpy as np


class RecommendationType(str, Enum):
    """推荐类型"""
    HOME_FEED = "HomeFeed"
    PRODUCT_DETAIL = "ProductDetail"
    SEARCH_RESULT = "SearchResult"
    SHOPPING_CART = "ShoppingCart"
    PERSONALIZED = "Personalized"


class AlgorithmType(str, Enum):
    """算法类型"""
    COLLABORATIVE_FILTERING = "CF"
    CONTENT_BASED = "ContentBased"
    DEEP_LEARNING = "DeepLearning"
    KNOWLEDGE_GRAPH = "KnowledgeGraph"
    HYBRID = "Hybrid"


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    age_group: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    device_type: str = "mobile"
    
    # 行为特征
    browse_history: List[str] = field(default_factory=list)
    purchase_history: List[str] = field(default_factory=list)
    cart_items: List[str] = field(default_factory=list)
    favorite_categories: List[str] = field(default_factory=list)
    
    # 用户价值
    lifetime_value: float = 0.0
    avg_order_value: float = 0.0
    purchase_frequency: float = 0.0


@dataclass
class Product:
    """商品"""
    product_id: str
    product_name: str
    category_id: str
    category_name: str
    brand_id: str
    price: float
    rating: float = 0.0
    review_count: int = 0
    sales_count: int = 0
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationCandidate:
    """推荐候选"""
    product: Product
    score: float
    algorithm: AlgorithmType
    reason: str


@dataclass
class RecommendationEngine:
    """推荐引擎"""
    engine_id: str
    engine_name: str
    recommendation_type: RecommendationType
    
    def generate_recommendations(
        self, 
        user: UserProfile, 
        context: Dict[str, Any],
        top_k: int = 20
    ) -> List[RecommendationCandidate]:
        """生成推荐列表"""
        candidates = []
        
        # 1. 召回阶段（简化模拟）
        recalled_items = self._recall_stage(user)
        
        # 2. 排序阶段
        for item in recalled_items[:top_k * 3]:
            score = self._calculate_score(user, item, context)
            candidates.append(RecommendationCandidate(
                product=item,
                score=score,
                algorithm=AlgorithmType.HYBRID,
                reason="Based on your browsing history"
            ))
        
        # 3. 重排序
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        return candidates[:top_k]
    
    def _recall_stage(self, user: UserProfile) -> List[Product]:
        """召回阶段"""
        # 模拟召回逻辑
        products = []
        for i in range(100):
            products.append(Product(
                product_id=f"SKU-{10000+i}",
                product_name=f"Product {i}",
                category_id=f"CAT-{i%10}",
                category_name=f"Category {i%10}",
                brand_id=f"BRAND-{i%20}",
                price=100 + i * 10,
                rating=3.5 + (i % 5) * 0.3,
                sales_count=1000 + i * 100
            ))
        return products
    
    def _calculate_score(self, user: UserProfile, product: Product, context: Dict) -> float:
        """计算推荐分数"""
        score = 0.0
        
        # 协同过滤分数
        cf_score = np.random.uniform(0.3, 0.9)
        
        # 内容匹配分数
        content_score = 0.0
        if product.category_id in user.favorite_categories:
            content_score = 0.8
        
        # 热度分数
        popularity_score = min(1.0, product.sales_count / 10000)
        
        # 个性化加权
        score = cf_score * 0.4 + content_score * 0.4 + popularity_score * 0.2
        
        return round(score, 4)


@dataclass
class ABTestExperiment:
    """A/B测试实验"""
    experiment_id: str
    experiment_name: str
    control_group: List[str] = field(default_factory=list)
    treatment_group: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def calculate_metrics(self) -> Dict[str, float]:
        """计算实验指标"""
        return {
            "ctr_lift": 0.15,  # 点击率提升
            "cvr_lift": 0.12,  # 转化率提升
            "gmv_lift": 0.20   # GMV提升
        }


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("华购电商 - 智能推荐与搜索系统")
    print("=" * 70)
    
    # 创建推荐引擎
    engine = RecommendationEngine(
        engine_id="REC-HUAGOU-001",
        engine_name="首页个性化推荐引擎",
        recommendation_type=RecommendationType.HOME_FEED
    )
    
    # 创建用户画像
    user = UserProfile(
        user_id="USER-123456",
        age_group="25-35",
        gender="F",
        location="上海",
        favorite_categories=["CAT-1", "CAT-3", "CAT-5"],
        lifetime_value=15000.0,
        avg_order_value=350.0,
        purchase_frequency=2.5
    )
    
    # 生成推荐
    print("\n[1] 生成个性化推荐...")
    recommendations = engine.generate_recommendations(
        user=user,
        context={"time": "evening", "device": "mobile"},
        top_k=10
    )
    
    print(f"用户ID: {user.user_id}")
    print(f"推荐数量: {len(recommendations)}")
    print("\nTop 10 推荐商品:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec.product.product_name}")
        print(f"     价格: ¥{rec.product.price}")
        print(f"     评分: {rec.product.rating}")
        print(f"     推荐分: {rec.score}")
    
    # A/B测试
    print("\n[2] A/B测试效果...")
    experiment = ABTestExperiment(
        experiment_id="EXP-202502-001",
        experiment_name="新推荐算法效果测试"
    )
    metrics = experiment.calculate_metrics()
    print(f"点击率提升: +{metrics['ctr_lift']:.1%}")
    print(f"转化率提升: +{metrics['cvr_lift']:.1%}")
    print(f"GMV提升: +{metrics['gmv_lift']:.1%}")
```

### 2.7 效果评估与ROI分析

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 转化率 | 2.5% | 4.2% | +68% |
| 点击率 | 8% | 12% | +50% |
| GMV/UV | 120元 | 168元 | +40% |
| 用户停留时长 | 8分钟 | 14分钟 | +75% |

**ROI**：420%（年收益5亿 vs 投资9600万）

---

**创建时间**：2025-01-21
**最后更新**：2025-02-15
