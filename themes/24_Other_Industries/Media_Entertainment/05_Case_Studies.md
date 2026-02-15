# 媒体娱乐Schema实践案例

## 📑 目录

- [1. 案例概述](#1-案例概述)
- [2. 企业背景](#2-企业背景)
- [3. 业务痛点与目标](#3-业务痛点与目标)
- [4. 技术挑战](#4-技术挑战)
- [5. 解决方案架构](#5-解决方案架构)
- [6. 完整实现代码](#6-完整实现代码)
- [7. 效果评估与ROI分析](#7-效果评估与roi分析)

---

## 1. 案例概述

本文档提供媒体娱乐行业Schema在实际应用中的完整实践案例，涵盖内容管理、用户画像、推荐系统、版权管理、广告投放等核心场景。

---

## 2. 企业背景

### 2.1 企业概况

**企业名称**：星辰传媒娱乐集团（虚构案例企业）

**企业规模**：
- 月活跃用户：1.5亿
- 内容库存：200万+小时
- 合作内容方：500+家
- 年营业额：85亿元人民币

---

## 3. 业务痛点与目标

### 3.1 五大业务痛点

| 序号 | 痛点 | 具体表现 | 影响程度 |
|------|------|----------|----------|
| 1 | **内容发现难** | 长尾内容曝光率低 | 高 |
| 2 | **版权管理乱** | 授权到期未及时发现 | 高 |
| 3 | **用户流失快** | 月流失率8% | 高 |
| 4 | **广告效果差** | 点击率低于1% | 中 |
| 5 | **内容审核慢** | 人工审核效率低 | 中 |

### 3.2 五大业务目标

| 序号 | 目标 | 具体指标 | 完成期限 |
|------|------|----------|----------|
| 1 | **个性化推荐** | 推荐点击率>15% | 12个月 |
| 2 | **版权自动化** | 100%授权自动管理 | 9个月 |
| 3 | **降低流失率** | 月流失率<5% | 12个月 |
| 4 | **精准投放** | 广告ROI提升100% | 12个月 |
| 5 | **智能审核** | 90%内容自动过审 | 9个月 |

---

## 4. 技术挑战

1. **海量内容处理**：百万小时内容的存储和检索
2. **实时推荐**：毫秒级个性化推荐
3. **多模态理解**：视频、音频、文本的联合理解
4. **版权追踪**：内容的版权状态和传播追踪
5. **AIGC管理**：AI生成内容的识别和管理

---

## 5. 解决方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层                                    │
│  视频APP  音乐APP  游戏平台  社交社区  广告平台              │
├─────────────────────────────────────────────────────────────┤
│                    服务层                                    │
│  推荐引擎  搜索服务  内容理解  版权管理  用户画像            │
├─────────────────────────────────────────────────────────────┤
│                    数据层                                    │
│  内容库  用户库  行为库  知识图谱  特征库                    │
├─────────────────────────────────────────────────────────────┤
│                    基础设施层                                │
│  CDN  对象存储  流媒体  AI计算  大数据                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 完整实现代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
媒体娱乐Schema实践案例
企业：星辰传媒娱乐集团
"""

import json
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """内容类型"""
    VIDEO = "视频"
    MUSIC = "音乐"
    GAME = "游戏"
    LIVE = "直播"
    SHORT_VIDEO = "短视频"


class ContentGenre(Enum):
    """内容题材"""
    ACTION = "动作"
    COMEDY = "喜剧"
    DRAMA = "剧情"
    ROMANCE = "爱情"
    SCIFI = "科幻"
    DOCUMENTARY = "纪录片"
    MUSIC_POP = "流行"
    MUSIC_ROCK = "摇滚"
    MUSIC_CLASSICAL = "古典"


class UserTier(Enum):
    """用户等级"""
    FREE = "免费"
    VIP = "VIP"
    SVIP = "超级VIP"


class AdType(Enum):
    """广告类型"""
    PRE_ROLL = "前贴片"
    MID_ROLL = "中插"
    POST_ROLL = "后贴片"
    BANNER = "横幅"
    NATIVE = "原生"


@dataclass
class ContentItem:
    """内容项"""
    content_id: str
    title: str
    content_type: ContentType
    genres: List[ContentGenre] = field(default_factory=list)
    duration_seconds: int = 0
    release_date: date = field(default_factory=date.today)
    rating: float = 0.0  # 评分 0-10
    view_count: int = 0
    like_count: int = 0
    
    # 内容属性
    cast: List[str] = field(default_factory=list)
    director: str = ""
    tags: List[str] = field(default_factory=list)
    
    # 版权信息
    copyright_holder: str = ""
    license_start: Optional[date] = None
    license_end: Optional[date] = None
    
    def is_available(self) -> bool:
        """检查内容是否可用"""
        today = date.today()
        if self.license_start and today < self.license_start:
            return False
        if self.license_end and today > self.license_end:
            return False
        return True
    
    def to_dict(self) -> Dict:
        return {
            "content_id": self.content_id,
            "title": self.title,
            "content_type": self.content_type.value,
            "genres": [g.value for g in self.genres],
            "duration": f"{self.duration_seconds // 60}分{self.duration_seconds % 60}秒",
            "rating": self.rating,
            "view_count": self.view_count,
            "is_available": self.is_available()
        }


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    username: str
    tier: UserTier = UserTier.FREE
    registration_date: date = field(default_factory=date.today)
    
    # 兴趣标签
    preferred_genres: List[ContentGenre] = field(default_factory=list)
    preferred_content_types: List[ContentType] = field(default_factory=list)
    
    # 行为统计
    total_watch_time: int = 0  # 分钟
    favorite_cast: List[str] = field(default_factory=list)
    watch_history: List[str] = field(default_factory=list)
    
    # 价值指标
    lifetime_value: float = 0.0
    churn_risk: float = 0.0
    
    def update_churn_risk(self, days_since_last_active: int):
        """更新流失风险"""
        if days_since_last_active > 30:
            self.churn_risk = 0.8
        elif days_since_last_active > 14:
            self.churn_risk = 0.5
        elif days_since_last_active > 7:
            self.churn_risk = 0.2
        else:
            self.churn_risk = 0.05
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "tier": self.tier.value,
            "preferred_genres": [g.value for g in self.preferred_genres],
            "total_watch_time": self.total_watch_time,
            "churn_risk": round(self.churn_risk, 2)
        }


@dataclass
class UserEvent:
    """用户行为事件"""
    event_id: str
    user_id: str
    content_id: str
    event_type: str  # play, pause, like, share, complete
    timestamp: datetime
    duration_watched: int = 0  # 观看时长（秒）
    device_type: str = ""
    location: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Copyright:
    """版权信息"""
    copyright_id: str
    content_id: str
    holder_name: str
    license_type: str  # exclusive, non-exclusive
    territory: List[str] = field(default_factory=list)
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=lambda: date.today() + timedelta(days=365))
    usage_rights: List[str] = field(default_factory=list)
    
    def days_until_expiry(self) -> int:
        """距离到期天数"""
        return (self.end_date - date.today()).days
    
    def is_expiring_soon(self, days: int = 30) -> bool:
        """是否即将到期"""
        return 0 < self.days_until_expiry() <= days
    
    def to_dict(self) -> Dict:
        return {
            "copyright_id": self.copyright_id,
            "content_id": self.content_id,
            "holder_name": self.holder_name,
            "license_type": self.license_type,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "days_until_expiry": self.days_until_expiry(),
            "is_expiring_soon": self.is_expiring_soon()
        }


@dataclass
class Ad:
    """广告"""
    ad_id: str
    ad_type: AdType
    title: str
    advertiser: str
    target_audience: Dict[str, Any] = field(default_factory=dict)
    budget: float = 0.0
    cpm: float = 0.0  # 千次展示成本
    ctr_target: float = 0.01  # 目标点击率
    
    # 投放数据
    impressions: int = 0
    clicks: int = 0
    
    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions > 0 else 0
    
    @property
    def spend(self) -> float:
        return self.impressions / 1000 * self.cpm
    
    def to_dict(self) -> Dict:
        return {
            "ad_id": self.ad_id,
            "ad_type": self.ad_type.value,
            "title": self.title,
            "advertiser": self.advertiser,
            "ctr": round(self.ctr, 4),
            "spend": round(self.spend, 2)
        }


class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self):
        self.content_pool: Dict[str, ContentItem] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_features: Dict[str, Dict] = {}
        self.similarity_matrix: Dict[str, Dict[str, float]] = {}
    
    def add_content(self, content: ContentItem):
        """添加内容"""
        self.content_pool[content.content_id] = content
        # 提取内容特征
        self.content_features[content.content_id] = {
            "genres": [g.value for g in content.genres],
            "type": content.content_type.value,
            "rating": content.rating,
            "popularity": content.view_count
        }
    
    def add_user(self, user: UserProfile):
        """添加用户"""
        self.user_profiles[user.user_id] = user
    
    def calculate_similarity(self, content1_id: str, content2_id: str) -> float:
        """计算内容相似度"""
        c1 = self.content_pool.get(content1_id)
        c2 = self.content_pool.get(content2_id)
        
        if not c1 or not c2:
            return 0.0
        
        # 基于类型的相似度
        if c1.content_type != c2.content_type:
            return 0.1
        
        # 基于题材的相似度
        genre_overlap = len(set(c1.genres) & set(c2.genres))
        genre_sim = genre_overlap / max(len(c1.genres), len(c2.genres), 1)
        
        # 综合相似度
        return 0.3 + 0.5 * genre_sim + 0.2 * (min(c1.rating, c2.rating) / 10)
    
    def recommend(self, user_id: str, top_k: int = 10) -> List[Dict]:
        """为用户推荐内容"""
        user = self.user_profiles.get(user_id)
        if not user:
            return []
        
        scores = {}
        
        for content_id, content in self.content_pool.items():
            if not content.is_available():
                continue
            
            score = 0.0
            
            # 1. 基于用户偏好的匹配度
            genre_match = len(set(user.preferred_genres) & set(content.genres))
            score += genre_match * 0.3
            
            type_match = content.content_type in user.preferred_content_types
            score += 0.2 if type_match else 0
            
            # 2. 基于热门度
            score += min(content.view_count / 1000000, 0.2)
            
            # 3. 基于评分
            score += content.rating / 10 * 0.2
            
            # 4. 基于观看历史（协同过滤简化版）
            for watched_id in user.watch_history[-5:]:
                sim = self.calculate_similarity(content_id, watched_id)
                score += sim * 0.3
            
            # 5. 去重惩罚
            if content_id in user.watch_history:
                score *= 0.3
            
            scores[content_id] = score
        
        # 排序取TopK
        sorted_content = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for content_id, score in sorted_content[:top_k]:
            content = self.content_pool[content_id]
            recommendations.append({
                "content_id": content_id,
                "title": content.title,
                "type": content.content_type.value,
                "score": round(score, 3),
                "reason": self._generate_reason(user, content)
            })
        
        return recommendations
    
    def _generate_reason(self, user: UserProfile, content: ContentItem) -> str:
        """生成推荐理由"""
        if user.preferred_genres and content.genres:
            overlap = set(user.preferred_genres) & set(content.genres)
            if overlap:
                return f"因为你喜欢{list(overlap)[0].value}"
        
        if content.view_count > 1000000:
            return "近期热门"
        
        if content.rating > 8:
            return "高分推荐"
        
        return "猜你喜欢"


class CopyrightManager:
    """版权管理器"""
    
    def __init__(self):
        self.copyrights: Dict[str, Copyright] = {}
        self.alerts: List[Dict] = []
    
    def register_copyright(self, copyright: Copyright):
        """注册版权"""
        self.copyrights[copyright.copyright_id] = copyright
        logger.info(f"Registered copyright: {copyright.copyright_id}")
    
    def check_expiring_copyrights(self, days: int = 30) -> List[Copyright]:
        """检查即将到期的版权"""
        expiring = []
        for cp in self.copyrights.values():
            if cp.is_expiring_soon(days):
                expiring.append(cp)
                self.alerts.append({
                    "type": "copyright_expiring",
                    "copyright_id": cp.copyright_id,
                    "content_id": cp.content_id,
                    "days_left": cp.days_until_expiry(),
                    "timestamp": datetime.now().isoformat()
                })
        return expiring
    
    def get_copyright_summary(self) -> Dict:
        """获取版权摘要"""
        total = len(self.copyrights)
        active = sum(1 for cp in self.copyrights.values() if cp.days_until_expiry() > 0)
        expiring_soon = len(self.check_expiring_copyrights(30))
        expired = sum(1 for cp in self.copyrights.values() if cp.days_until_expiry() <= 0)
        
        return {
            "total_copyrights": total,
            "active": active,
            "expiring_soon": expiring_soon,
            "expired": expired
        }


class AdPlatform:
    """广告平台"""
    
    def __init__(self):
        self.ads: Dict[str, Ad] = {}
        self.delivery_log: List[Dict] = []
    
    def create_ad(self, ad: Ad):
        """创建广告"""
        self.ads[ad.ad_id] = ad
    
    def select_ad(self, user: UserProfile, content: ContentItem) -> Optional[Ad]:
        """为用户和内容选择广告"""
        # 基于用户等级的策略
        if user.tier == UserTier.SVIP:
            return None  # SVIP免广告
        
        # 基于内容的广告匹配
        available_ads = [ad for ad in self.ads.values() if ad.budget > ad.spend]
        
        if not available_ads:
            return None
        
        # 选择最匹配的广告（简化版）
        return random.choice(available_ads)
    
    def deliver_ad(self, ad_id: str, user_id: str, content_id: str) -> bool:
        """投放广告"""
        ad = self.ads.get(ad_id)
        if not ad:
            return False
        
        ad.impressions += 1
        
        self.delivery_log.append({
            "ad_id": ad_id,
            "user_id": user_id,
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "impression": True
        })
        
        return True
    
    def record_click(self, ad_id: str, user_id: str):
        """记录点击"""
        ad = self.ads.get(ad_id)
        if ad:
            ad.clicks += 1
            
            self.delivery_log.append({
                "ad_id": ad_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "click": True
            })
    
    def get_ad_report(self, ad_id: str) -> Dict:
        """获取广告报告"""
        ad = self.ads.get(ad_id)
        if not ad:
            return {}
        
        return {
            "ad_id": ad_id,
            "impressions": ad.impressions,
            "clicks": ad.clicks,
            "ctr": round(ad.ctr * 100, 2),
            "spend": round(ad.spend, 2),
            "budget_left": round(ad.budget - ad.spend, 2)
        }


class MediaPlatform:
    """媒体平台"""
    
    def __init__(self):
        self.recommendation_engine = RecommendationEngine()
        self.copyright_manager = CopyrightManager()
        self.ad_platform = AdPlatform()
        self.events: List[UserEvent] = []
    
    def record_event(self, event: UserEvent):
        """记录用户事件"""
        self.events.append(event)
        
        # 更新用户画像
        user = self.recommendation_engine.user_profiles.get(event.user_id)
        if user:
            if event.event_type == "complete":
                content = self.recommendation_engine.content_pool.get(event.content_id)
                if content:
                    user.watch_history.append(event.content_id)
                    user.total_watch_time += event.duration_watched // 60
    
    def get_user_dashboard(self, user_id: str) -> Dict:
        """获取用户仪表板"""
        user = self.recommendation_engine.user_profiles.get(user_id)
        if not user:
            return {}
        
        # 获取推荐
        recommendations = self.recommendation_engine.recommend(user_id, top_k=6)
        
        # 检查广告
        content = random.choice(list(self.recommendation_engine.content_pool.values()))
        ad = self.ad_platform.select_ad(user, content)
        
        return {
            "user": user.to_dict(),
            "recommendations": recommendations,
            "ad": ad.to_dict() if ad else None,
            "watch_history_count": len(user.watch_history)
        }


def create_demo_platform():
    """创建演示平台"""
    platform = MediaPlatform()
    
    # 添加内容
    contents = [
        ContentItem("MOV-001", "星际穿越", ContentType.VIDEO, 
                   [ContentGenre.SCIFI, ContentGenre.DRAMA], 10800, rating=9.3,
                   view_count=5000000, cast=["马修·麦康纳", "安妮·海瑟薇"]),
        ContentItem("MOV-002", "肖申克的救赎", ContentType.VIDEO,
                   [ContentGenre.DRAMA], 8400, rating=9.7,
                   view_count=8000000),
        ContentItem("MUS-001", "晴天", ContentType.MUSIC,
                   [ContentGenre.MUSIC_POP], 240, rating=9.0,
                   view_count=10000000),
        ContentItem("MUS-002", "贝多芬第九交响曲", ContentType.MUSIC,
                   [ContentGenre.MUSIC_CLASSICAL], 3600, rating=9.5,
                   view_count=500000),
        ContentItem("SV-001", "搞笑合集", ContentType.SHORT_VIDEO,
                   [ContentGenre.COMEDY], 180, rating=8.5,
                   view_count=20000000),
    ]
    
    for content in contents:
        platform.recommendation_engine.add_content(content)
    
    # 添加用户
    users = [
        UserProfile("U001", "用户A", UserTier.VIP, preferred_genres=[ContentGenre.SCIFI, ContentGenre.ACTION]),
        UserProfile("U002", "用户B", UserTier.SVIP, preferred_genres=[ContentGenre.MUSIC_POP]),
        UserProfile("U003", "用户C", UserTier.FREE),
    ]
    
    for user in users:
        platform.recommendation_engine.add_user(user)
    
    # 添加版权
    copyrights = [
        Copyright("CP-001", "MOV-001", "派拉蒙影业", "non-exclusive",
                 end_date=date(2025, 12, 31)),
        Copyright("CP-002", "MOV-002", "华纳兄弟", "non-exclusive",
                 end_date=date(2025, 6, 30)),
    ]
    
    for cp in copyrights:
        platform.copyright_manager.register_copyright(cp)
    
    # 添加广告
    ads = [
        Ad("AD-001", AdType.PRE_ROLL, "新片预告", "影业公司A", cpm=50, budget=100000),
        Ad("AD-002", AdType.NATIVE, "游戏推广", "游戏公司B", cpm=30, budget=50000),
    ]
    
    for ad in ads:
        platform.ad_platform.create_ad(ad)
    
    return platform


def main():
    """主函数"""
    print("=" * 80)
    print("媒体娱乐Schema实践案例 - 星辰传媒")
    print("=" * 80)
    
    # 创建平台
    print("\n【步骤1】初始化媒体平台...")
    platform = create_demo_platform()
    print(f"  内容数量: {len(platform.recommendation_engine.content_pool)}")
    print(f"  用户数: {len(platform.recommendation_engine.user_profiles)}")
    print(f"  广告数: {len(platform.ad_platform.ads)}")
    
    # 个性化推荐
    print("\n【步骤2】个性化内容推荐...")
    for user_id in ["U001", "U002"]:
        recommendations = platform.recommendation_engine.recommend(user_id, top_k=3)
        user = platform.recommendation_engine.user_profiles[user_id]
        print(f"\n  {user.username} (等级: {user.tier.value}):")
        for rec in recommendations:
            print(f"    - {rec['title']} ({rec['type']}) [{rec['reason']}]")
    
    # 版权管理
    print("\n【步骤3】版权到期检查...")
    expiring = platform.copyright_manager.check_expiring_copyrights(30)
    summary = platform.copyright_manager.get_copyright_summary()
    print(f"  版权总数: {summary['total_copyrights']}")
    print(f"  即将到期: {summary['expiring_soon']}")
    for cp in expiring:
        print(f"    - 内容ID: {cp.content_id}, 剩余{cp.days_until_expiry()}天")
    
    # 广告投放
    print("\n【步骤4】广告投放演示...")
    user = platform.recommendation_engine.user_profiles["U001"]
    content = platform.recommendation_engine.content_pool["MOV-001"]
    ad = platform.ad_platform.select_ad(user, content)
    if ad:
        platform.ad_platform.deliver_ad(ad.ad_id, user.user_id, content.content_id)
        print(f"  为用户 {user.username} 投放广告: {ad.title}")
        print(f"  广告类型: {ad.ad_type.value}")
    else:
        print(f"  用户 {user.username} 免广告")
    
    # 广告报告
    print("\n【步骤5】广告效果报告...")
    for ad_id in ["AD-001"]:
        report = platform.ad_platform.get_ad_report(ad_id)
        print(f"  广告: {ad_id}")
        print(f"    展示: {report['impressions']}, 点击: {report['clicks']}")
        print(f"    CTR: {report['ctr']}%")
        print(f"    消耗: ¥{report['spend']}")
    
    # 用户仪表板
    print("\n【步骤6】用户仪表板...")
    dashboard = platform.get_user_dashboard("U001")
    print(f"  用户: {dashboard['user']['username']}")
    print(f"  流失风险: {dashboard['user']['churn_risk']}")
    print(f"  推荐数: {len(dashboard['recommendations'])}")
    
    print("\n" + "=" * 80)
    print("媒体娱乐Schema实践案例执行完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
```

---

## 7. 效果评估与ROI分析

### 7.1 关键绩效指标

| 指标 | 实施前 | 实施后 | 改善 |
|------|--------|--------|------|
| 推荐点击率 | 3% | 18% | +500% |
| 版权到期遗漏 | 20起/年 | 0起 | -100% |
| 月流失率 | 8% | 4.5% | -44% |
| 广告CTR | 0.5% | 2.5% | +400% |
| 审核效率 | 100条/人天 | 1000条/人天 | +900% |

### 7.2 ROI分析

**投资**：¥800万  
**年收益**：¥3200万  
**ROI**：300%（3年）

---

**创建时间**：2026-02-15  
**版本**：1.0.0
