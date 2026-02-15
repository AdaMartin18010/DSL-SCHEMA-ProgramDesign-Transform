# 数据挖掘Schema实践案例

## 📑 目录

- [数据挖掘Schema实践案例](#数据挖掘schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：电信运营商客户流失预警与挽留系统](#2-案例1电信运营商客户流失预警与挽留系统)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估与ROI分析](#27-效果评估与roi分析)
  - [3. 案例2：金融欺诈检测系统](#3-案例2金融欺诈检测系统)
  - [4. 案例3：零售客户细分与精准营销系统](#4-案例3零售客户细分与精准营销系统)

---

## 1. 案例概述

本文档提供数据挖掘Schema在实际企业应用中的深度实践案例，涵盖客户流失预测、欺诈检测、客户细分等核心业务场景。

**案例类型**：

1. **电信运营商客户流失预警与挽留系统**：基于机器学习的客户流失预测
2. **金融欺诈检测系统**：实时欺诈行为识别
3. **零售客户细分与精准营销系统**：客户价值分析与营销策略优化

---

## 2. 案例1：电信运营商客户流失预警与挽留系统

### 2.1 企业背景

**企业简介**：
某省级电信运营商（以下简称"华通电信"）成立于2000年，是中国领先的综合性电信服务提供商。公司业务涵盖移动通信、固网宽带、物联网、云计算等领域，服务用户超过5000万，年营收超过300亿元人民币。

**业务规模**：

| 指标 | 数值 |
|------|------|
| 移动用户 | 4500万+ |
| 宽带用户 | 800万+ |
| 基站数量 | 10万+ |
| 年营收 | 300亿+ RMB |
| 日均通话记录 | 5亿+ |
| 日均流量数据 | 500TB+ |
| 客服中心日工单 | 10万+ |

**IT基础设施**：
- 计费系统：自研分布式系统
- CRM系统：Salesforce + 自研
- 网络管理系统：华为/爱立信
- 大数据平台：Hadoop + Spark
- 数据仓库：Teradata

### 2.2 业务痛点

**痛点1：客户流失率高**
年度客户流失率高达18%，其中高价值客户流失率更是达到25%。每流失一个客户，平均需要投入300元获取一个新客户来替代，年度客户获取成本超过10亿元。

**痛点2：流失预警滞后**
传统的客户流失判断主要依赖经验规则（如连续欠费3个月），发现时客户已基本决定离网，挽留成功率低。被动挽留成功率仅为15%，而主动预警挽留成功率可达45%。

**痛点3：缺乏精准画像**
对客户的理解停留在基础属性层面，缺乏对行为特征、使用习惯、偏好需求的深度洞察，无法制定差异化的挽留策略。

**痛点4：挽留资源浪费**
现有的"广撒网"式挽留活动覆盖所有疑似流失客户，成本高且效果差。营销资源分配缺乏数据支撑，ROI难以衡量。

**痛点5：竞争应对被动**
竞争对手的针对性营销活动（如携号转网优惠）往往导致大量客户批量流失，缺乏提前预警和快速响应机制。

### 2.3 业务目标

**目标1：建立流失预警模型**
构建基于机器学习的客户流失预测模型，提前30-60天识别高流失风险客户，预测准确率达到85%以上。

**目标2：构建客户画像体系**
建立360度客户画像，整合通信行为、消费特征、服务交互、网络体验等多维数据，支持精细化客户分群。

**目标3：优化挽留策略**
基于客户流失原因和偏好，设计差异化挽留策略（如套餐调整、积分赠送、专属服务），提升挽留成功率至40%以上。

**目标4：提升客户生命周期价值**
通过主动关怀和服务优化，延长客户在网时长，提升ARPU值，年度客户生命周期价值（CLV）提升10%以上。

**目标5：建立闭环运营体系**
构建"预警-触达-挽留-评估"的完整闭环，实现挽留活动的自动化、智能化、可衡量化。

### 2.4 技术挑战

**挑战1：海量特征工程**
需要处理来自计费、CRM、网络、客服等20多个系统的数据，原始字段超过1000个，如何有效提取和选择特征是关键挑战。

**挑战2：样本不平衡**
实际流失客户占总客户的比例仅约2%，正负样本严重不平衡，需要采用SMOTE、代价敏感学习等技术处理。

**挑战3：模型可解释性**
业务部门需要理解模型预测依据，以便制定针对性挽留策略，需要在模型精度和可解释性之间取得平衡。

**挑战4：实时预测能力**
需要支持每日千万级客户的批量评分，同时支持实时场景（如客户投诉）的即时预测，对系统性能要求高。

**挑战5：模型持续优化**
市场环境、竞争态势、客户行为持续变化，需要建立模型监控和自动更新机制，确保模型长期有效。

### 2.5 解决方案

**整体架构**：
- **数据层**：整合多源数据，构建客户统一视图
- **特征层**：构建客户行为特征、消费特征、服务特征等
- **模型层**：采用XGBoost为主模型，结合逻辑回归做可解释补充
- **应用层**：预警推送、策略匹配、效果评估

**技术路线**：
- 特征工程：基于RFM模型扩展，构建200+客户特征
- 算法选择：XGBoost（主模型）+ SHAP（可解释）+ 规则引擎（补充）
- 部署方式：批处理（每日全量评分）+ 实时API（关键事件触发）

### 2.6 完整代码实现

**客户流失预警系统完整实现**：

```python
#!/usr/bin/env python3
"""
电信运营商客户流失预警与挽留系统
基于XGBoost和SHAP的企业级客户流失预测解决方案
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class ModelType(str, Enum):
    """模型类型"""
    XGBOOST = "XGBoost"
    LIGHTGBM = "LightGBM"
    RANDOM_FOREST = "RandomForest"
    LOGISTIC_REGRESSION = "LogisticRegression"
    NEURAL_NETWORK = "NeuralNetwork"


class FeatureType(str, Enum):
    """特征类型"""
    DEMOGRAPHIC = "Demographic"      # 人口统计
    BEHAVIORAL = "Behavioral"        # 行为特征
    CONSUMPTION = "Consumption"      # 消费特征
    SERVICE = "Service"              # 服务特征
    NETWORK = "Network"              # 网络特征
    ENGAGEMENT = "Engagement"        # 参与度特征


class ChurnRiskLevel(str, Enum):
    """流失风险等级"""
    CRITICAL = "Critical"      # 极高风险（>80%）
    HIGH = "High"              # 高风险（60-80%）
    MEDIUM = "Medium"          # 中风险（40-60%）
    LOW = "Low"                # 低风险（20-40%）
    SAFE = "Safe"              # 安全（<20%）


class RetentionStrategy(str, Enum):
    """挽留策略"""
    PREMIUM_SERVICE = "PremiumService"    # 专属服务
    DISCOUNT_OFFER = "DiscountOffer"      # 优惠套餐
    DATA_BONUS = "DataBonus"              # 流量赠送
    DEVICE_SUBSIDY = "DeviceSubsidy"      # 终端补贴
    POINTS_REWARD = "PointsReward"        # 积分奖励
    SERVICE_CALL = "ServiceCall"          # 关怀回访


@dataclass
class CustomerFeature:
    """客户特征"""
    feature_id: str
    feature_name: str
    feature_type: FeatureType
    feature_value: Any
    feature_importance: float = 0.0
    description: Optional[str] = None


@dataclass
class RFMFeatures:
    """RFM特征"""
    recency_days: int           # 最近一次消费距今天数
    frequency_monthly: int      # 月均消费次数
    monetary_monthly: Decimal   # 月均消费金额
    rfm_score: int = 0          # RFM综合评分
    
    def calculate_score(self):
        """计算RFM评分"""
        # R评分（越小越好，1-5分）
        if self.recency_days <= 7:
            r_score = 5
        elif self.recency_days <= 30:
            r_score = 4
        elif self.recency_days <= 60:
            r_score = 3
        elif self.recency_days <= 90:
            r_score = 2
        else:
            r_score = 1
        
        # F评分（越大越好，1-5分）
        if self.frequency_monthly >= 20:
            f_score = 5
        elif self.frequency_monthly >= 15:
            f_score = 4
        elif self.frequency_monthly >= 10:
            f_score = 3
        elif self.frequency_monthly >= 5:
            f_score = 2
        else:
            f_score = 1
        
        # M评分（基于金额，1-5分）
        monthly_amount = float(self.monetary_monthly)
        if monthly_amount >= 200:
            m_score = 5
        elif monthly_amount >= 150:
            m_score = 4
        elif monthly_amount >= 100:
            m_score = 3
        elif monthly_amount >= 50:
            m_score = 2
        else:
            m_score = 1
        
        self.rfm_score = r_score * 100 + f_score * 10 + m_score
        return self.rfm_score


@dataclass
class CustomerProfile:
    """客户画像"""
    customer_id: str
    phone_number: str
    customer_name: Optional[str] = None
    
    # 基础属性
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    registration_date: Optional[datetime] = None
    customer_tier: str = "Regular"  # Regular, Silver, Gold, Platinum
    
    # RFM特征
    rfm_features: Optional[RFMFeatures] = None
    
    # 行为特征
    total_calls_monthly: int = 0
    total_duration_monthly: int = 0  # 分钟
    total_data_usage_gb: float = 0.0
    avg_daily_sessions: float = 0.0
    
    # 消费特征
    monthly_arpu: Decimal = Decimal('0')
    plan_type: str = ""
    contract_status: str = "InContract"  # InContract, Expired
    contract_expiry_date: Optional[datetime] = None
    outstanding_balance: Decimal = Decimal('0')
    
    # 服务特征
    complaint_count_3m: int = 0
    service_call_count_3m: int = 0
    payment_delay_days_avg: float = 0.0
    
    # 网络特征
    avg_signal_strength: float = 0.0
    network_drop_rate: float = 0.0
    roaming_usage_ratio: float = 0.0
    
    # 参与度特征
    app_login_frequency: int = 0
    self_service_usage: int = 0
    social_media_engagement: int = 0
    
    # 流失相关
    is_churned: bool = False
    churn_date: Optional[datetime] = None
    
    def get_feature_vector(self) -> Dict[str, Any]:
        """获取特征向量用于模型预测"""
        features = {
            # 基础特征
            'age': self.age or 35,
            'customer_tenure_days': (datetime.now() - self.registration_date).days if self.registration_date else 365,
            'is_premium_tier': 1 if self.customer_tier in ['Gold', 'Platinum'] else 0,
            
            # RFM特征
            'rfm_score': self.rfm_features.rfm_score if self.rfm_features else 333,
            'recency_days': self.rfm_features.recency_days if self.rfm_features else 30,
            'frequency_monthly': self.rfm_features.frequency_monthly if self.rfm_features else 10,
            'monetary_monthly': float(self.rfm_features.monetary_monthly) if self.rfm_features else 100.0,
            
            # 行为特征
            'total_calls_monthly': self.total_calls_monthly,
            'total_duration_monthly': self.total_duration_monthly,
            'total_data_usage_gb': self.total_data_usage_gb,
            'avg_daily_sessions': self.avg_daily_sessions,
            
            # 消费特征
            'monthly_arpu': float(self.monthly_arpu),
            'is_in_contract': 1 if self.contract_status == "InContract" else 0,
            'days_to_contract_expiry': max(0, (self.contract_expiry_date - datetime.now()).days) if self.contract_expiry_date else 365,
            'outstanding_balance': float(self.outstanding_balance),
            
            # 服务特征
            'complaint_count_3m': self.complaint_count_3m,
            'service_call_count_3m': self.service_call_count_3m,
            'payment_delay_days_avg': self.payment_delay_days_avg,
            
            # 网络特征
            'avg_signal_strength': self.avg_signal_strength,
            'network_drop_rate': self.network_drop_rate,
            'roaming_usage_ratio': self.roaming_usage_ratio,
            
            # 参与度特征
            'app_login_frequency': self.app_login_frequency,
            'self_service_usage': self.self_service_usage,
            'social_media_engagement': self.social_media_engagement
        }
        return features


@dataclass
class ChurnPrediction:
    """流失预测结果"""
    prediction_id: str
    customer_id: str
    churn_probability: float
    risk_level: ChurnRiskLevel
    prediction_date: datetime
    
    # 特征贡献（SHAP值）
    top_contributing_features: List[Dict[str, Any]] = field(default_factory=list)
    
    # 预测解释
    explanation: Optional[str] = None
    
    # 推荐挽留策略
    recommended_strategy: Optional[RetentionStrategy] = None
    strategy_confidence: float = 0.0


@dataclass
class ChurnPredictionModel:
    """流失预测模型"""
    model_id: str
    model_name: str
    model_type: ModelType
    model_version: str = "1.0"
    feature_importance: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def predict(self, customer: CustomerProfile) -> ChurnPrediction:
        """预测客户流失概率（模拟）"""
        features = customer.get_feature_vector()
        
        # 模拟预测逻辑（实际应调用训练好的模型）
        churn_prob = self._calculate_churn_probability(features)
        
        # 确定风险等级
        risk_level = self._get_risk_level(churn_prob)
        
        # 计算特征贡献
        top_features = self._get_top_features(features)
        
        # 生成解释
        explanation = self._generate_explanation(customer, top_features)
        
        # 推荐策略
        strategy, confidence = self._recommend_strategy(customer, risk_level)
        
        return ChurnPrediction(
            prediction_id=f"PRED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{customer.customer_id}",
            customer_id=customer.customer_id,
            churn_probability=churn_prob,
            risk_level=risk_level,
            prediction_date=datetime.now(),
            top_contributing_features=top_features,
            explanation=explanation,
            recommended_strategy=strategy,
            strategy_confidence=confidence
        )
    
    def _calculate_churn_probability(self, features: Dict) -> float:
        """计算流失概率（简化模拟）"""
        prob = 0.0
        
        # RFM相关
        if features['rfm_score'] < 200:
            prob += 0.25
        elif features['rfm_score'] < 300:
            prob += 0.15
        
        if features['recency_days'] > 60:
            prob += 0.20
        
        # 合约状态
        if features['is_in_contract'] == 0:
            prob += 0.15
        
        if features['days_to_contract_expiry'] < 30:
            prob += 0.10
        
        # 投诉和服务
        if features['complaint_count_3m'] > 2:
            prob += 0.15
        
        if features['payment_delay_days_avg'] > 7:
            prob += 0.10
        
        # ARPU下降
        if features['monthly_arpu'] < 50:
            prob += 0.10
        
        # 网络质量
        if features['network_drop_rate'] > 0.05:
            prob += 0.10
        
        return min(0.99, prob + np.random.uniform(-0.05, 0.05))
    
    def _get_risk_level(self, probability: float) -> ChurnRiskLevel:
        """获取风险等级"""
        if probability >= 0.80:
            return ChurnRiskLevel.CRITICAL
        elif probability >= 0.60:
            return ChurnRiskLevel.HIGH
        elif probability >= 0.40:
            return ChurnRiskLevel.MEDIUM
        elif probability >= 0.20:
            return ChurnRiskLevel.LOW
        else:
            return ChurnRiskLevel.SAFE
    
    def _get_top_features(self, features: Dict) -> List[Dict[str, Any]]:
        """获取Top特征贡献"""
        # 模拟特征重要性
        importance_map = {
            'rfm_score': 0.18,
            'recency_days': 0.15,
            'complaint_count_3m': 0.12,
            'is_in_contract': 0.10,
            'monthly_arpu': 0.09,
            'payment_delay_days_avg': 0.08,
            'network_drop_rate': 0.07,
            'days_to_contract_expiry': 0.06,
            'total_data_usage_gb': 0.05,
            'app_login_frequency': 0.04
        }
        
        top_features = []
        for feature_name, importance in importance_map.items():
            top_features.append({
                'feature_name': feature_name,
                'feature_value': features.get(feature_name),
                'importance': importance,
                'direction': 'positive' if features.get(feature_name, 0) > 0 else 'negative'
            })
        
        return sorted(top_features, key=lambda x: x['importance'], reverse=True)[:5]
    
    def _generate_explanation(self, customer: CustomerProfile, top_features: List) -> str:
        """生成预测解释"""
        explanations = []
        
        if customer.rfm_features and customer.rfm_features.recency_days > 60:
            explanations.append(f"近{customer.rfm_features.recency_days}天无活跃记录")
        
        if customer.complaint_count_3m > 2:
            explanations.append(f"近3个月投诉{customer.complaint_count_3m}次")
        
        if customer.contract_status != "InContract":
            explanations.append("合约已到期")
        
        if customer.payment_delay_days_avg > 7:
            explanations.append(f"平均缴费延迟{customer.payment_delay_days_avg:.1f}天")
        
        if customer.network_drop_rate > 0.05:
            explanations.append("网络掉线率较高")
        
        return "；".join(explanations) if explanations else "综合评估存在流失风险"
    
    def _recommend_strategy(self, customer: CustomerProfile, risk_level: ChurnRiskLevel) -> Tuple[RetentionStrategy, float]:
        """推荐挽留策略"""
        if risk_level in [ChurnRiskLevel.CRITICAL, ChurnRiskLevel.HIGH]:
            if customer.customer_tier == "Platinum":
                return RetentionStrategy.PREMIUM_SERVICE, 0.85
            elif customer.complaint_count_3m > 2:
                return RetentionStrategy.SERVICE_CALL, 0.80
            elif customer.contract_status != "InContract":
                return RetentionStrategy.DISCOUNT_OFFER, 0.75
            else:
                return RetentionStrategy.DATA_BONUS, 0.70
        elif risk_level == ChurnRiskLevel.MEDIUM:
            return RetentionStrategy.POINTS_REWARD, 0.60
        else:
            return RetentionStrategy.SERVICE_CALL, 0.50


@dataclass
class RetentionCampaign:
    """挽留活动"""
    campaign_id: str
    campaign_name: str
    target_customers: List[str] = field(default_factory=list)
    strategy: RetentionStrategy = RetentionStrategy.SERVICE_CALL
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    budget: Decimal = Decimal('0')
    
    # 执行结果
    customers_contacted: int = 0
    customers_retained: int = 0
    total_cost: Decimal = Decimal('0')
    
    def calculate_roi(self) -> Dict[str, Any]:
        """计算ROI"""
        if not self.customers_contacted:
            return {'roi': 0, 'retention_rate': 0}
        
        retention_rate = self.customers_retained / self.customers_contacted
        
        # 假设平均客户年价值
        avg_customer_value = 1200  # 元
        retained_value = self.customers_retained * avg_customer_value
        
        roi = (retained_value - float(self.total_cost)) / float(self.total_cost) if self.total_cost else 0
        
        return {
            'roi': roi,
            'retention_rate': retention_rate,
            'retained_value': retained_value,
            'total_cost': float(self.total_cost)
        }


@dataclass
class ChurnPredictionSystem:
    """流失预测系统"""
    system_id: str
    system_name: str
    model: Optional[ChurnPredictionModel] = None
    predictions: Dict[str, ChurnPrediction] = field(default_factory=dict)
    campaigns: Dict[str, RetentionCampaign] = field(default_factory=dict)
    
    def deploy_model(self, model: ChurnPredictionModel):
        """部署模型"""
        self.model = model
        print(f"模型 {model.model_name} 已部署")
    
    def batch_predict(self, customers: List[CustomerProfile]) -> List[ChurnPrediction]:
        """批量预测"""
        if not self.model:
            raise ValueError("Model not deployed")
        
        results = []
        for customer in customers:
            prediction = self.model.predict(customer)
            self.predictions[prediction.prediction_id] = prediction
            results.append(prediction)
        
        return results
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """生成日报"""
        today_predictions = [p for p in self.predictions.values() 
                           if p.prediction_date.date() == datetime.now().date()]
        
        risk_distribution = {
            'Critical': len([p for p in today_predictions if p.risk_level == ChurnRiskLevel.CRITICAL]),
            'High': len([p for p in today_predictions if p.risk_level == ChurnRiskLevel.HIGH]),
            'Medium': len([p for p in today_predictions if p.risk_level == ChurnRiskLevel.MEDIUM]),
            'Low': len([p for p in today_predictions if p.risk_level == ChurnRiskLevel.LOW]),
            'Safe': len([p for p in today_predictions if p.risk_level == ChurnRiskLevel.SAFE])
        }
        
        avg_probability = np.mean([p.churn_probability for p in today_predictions]) if today_predictions else 0
        
        return {
            'prediction_date': datetime.now().strftime('%Y-%m-%d'),
            'total_predicted': len(today_predictions),
            'risk_distribution': risk_distribution,
            'average_churn_probability': round(avg_probability, 4),
            'high_risk_customers': risk_distribution['Critical'] + risk_distribution['High']
        }


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("华通电信 - 客户流失预警与挽留系统")
    print("=" * 70)
    
    # 1. 创建系统
    system = ChurnPredictionSystem(
        system_id="CHURN-SYS-001",
        system_name="华通电信客户流失预警系统"
    )
    
    # 2. 创建并部署模型
    model = ChurnPredictionModel(
        model_id="MODEL-XGB-001",
        model_name="客户流失预测XGBoost模型",
        model_type=ModelType.XGBOOST,
        model_version="2.1",
        performance_metrics={
            'auc': 0.89,
            'precision': 0.86,
            'recall': 0.82,
            'f1': 0.84
        }
    )
    system.deploy_model(model)
    
    # 3. 创建模拟客户数据
    print("\n[1] 加载客户数据...")
    customers = []
    
    # 高风险客户1 - 即将流失
    high_risk_customer = CustomerProfile(
        customer_id="CUST-001",
        phone_number="13800138000",
        customer_name="张三",
        age=28,
        gender="M",
        city="上海",
        registration_date=datetime.now() - timedelta(days=730),
        customer_tier="Gold",
        rfm_features=RFMFeatures(
            recency_days=75,
            frequency_monthly=3,
            monetary_monthly=Decimal('45')
        ),
        total_calls_monthly=5,
        total_duration_monthly=30,
        total_data_usage_gb=2.5,
        monthly_arpu=Decimal('45'),
        plan_type="4G畅享套餐",
        contract_status="Expired",
        complaint_count_3m=3,
        service_call_count_3m=5,
        payment_delay_days_avg=12.5,
        network_drop_rate=0.08,
        app_login_frequency=1
    )
    high_risk_customer.rfm_features.calculate_score()
    customers.append(high_risk_customer)
    
    # 中风险客户2
    medium_risk_customer = CustomerProfile(
        customer_id="CUST-002",
        phone_number="13900139000",
        customer_name="李四",
        age=35,
        gender="F",
        city="北京",
        registration_date=datetime.now() - timedelta(days=365),
        customer_tier="Silver",
        rfm_features=RFMFeatures(
            recency_days=35,
            frequency_monthly=12,
            monetary_monthly=Decimal('88')
        ),
        total_calls_monthly=45,
        total_duration_monthly=180,
        total_data_usage_gb=8.5,
        monthly_arpu=Decimal('88'),
        plan_type="5G畅享套餐",
        contract_status="InContract",
        contract_expiry_date=datetime.now() + timedelta(days=45),
        complaint_count_3m=1,
        service_call_count_3m=2,
        payment_delay_days_avg=3.0,
        network_drop_rate=0.02,
        app_login_frequency=8
    )
    medium_risk_customer.rfm_features.calculate_score()
    customers.append(medium_risk_customer)
    
    # 安全客户3
    safe_customer = CustomerProfile(
        customer_id="CUST-003",
        phone_number="13700137000",
        customer_name="王五",
        age=42,
        gender="M",
        city="深圳",
        registration_date=datetime.now() - timedelta(days=1825),
        customer_tier="Platinum",
        rfm_features=RFMFeatures(
            recency_days=2,
            frequency_monthly=25,
            monetary_monthly=Decimal('288')
        ),
        total_calls_monthly=120,
        total_duration_monthly=450,
        total_data_usage_gb=25.0,
        monthly_arpu=Decimal('288'),
        plan_type="5G尊享套餐",
        contract_status="InContract",
        contract_expiry_date=datetime.now() + timedelta(days=300),
        complaint_count_3m=0,
        service_call_count_3m=1,
        payment_delay_days_avg=0,
        network_drop_rate=0.005,
        app_login_frequency=25
    )
    safe_customer.rfm_features.calculate_score()
    customers.append(safe_customer)
    
    print(f"加载客户数: {len(customers)}")
    
    # 4. 批量预测
    print("\n[2] 执行流失预测...")
    predictions = system.batch_predict(customers)
    
    # 5. 输出预测结果
    print("\n" + "=" * 70)
    print("预测结果详情")
    print("=" * 70)
    
    for pred in predictions:
        print(f"\n客户ID: {pred.customer_id}")
        print(f"流失概率: {pred.churn_probability:.2%}")
        print(f"风险等级: {pred.risk_level.value}")
        print(f"主要原因: {pred.explanation}")
        print("\nTop 5 影响因子:")
        for i, feature in enumerate(pred.top_contributing_features, 1):
            print(f"  {i}. {feature['feature_name']}: {feature['feature_value']} (重要性: {feature['importance']:.2%})")
        print(f"\n推荐策略: {pred.recommended_strategy.value if pred.recommended_strategy else 'None'}")
        print(f"策略置信度: {pred.strategy_confidence:.1%}")
        print("-" * 70)
    
    # 6. 生成日报
    print("\n[3] 生成每日预测报告...")
    daily_report = system.generate_daily_report()
    print(f"\n预测日期: {daily_report['prediction_date']}")
    print(f"总预测客户数: {daily_report['total_predicted']}")
    print(f"平均流失概率: {daily_report['average_churn_probability']:.2%}")
    print(f"高风险客户数: {daily_report['high_risk_customers']}")
    print("\n风险分布:")
    for level, count in daily_report['risk_distribution'].items():
        print(f"  {level}: {count}人")
    
    # 7. 创建挽留活动
    print("\n[4] 创建挽留活动...")
    campaign = RetentionCampaign(
        campaign_id="CAMP-202502-001",
        campaign_name="2月高风险客户挽留活动",
        target_customers=[p.customer_id for p in predictions if p.risk_level in [ChurnRiskLevel.CRITICAL, ChurnRiskLevel.HIGH]],
        strategy=RetentionStrategy.DISCOUNT_OFFER,
        budget=Decimal('50000'),
        customers_contacted=1500,
        customers_retained=675,
        total_cost=Decimal('35000')
    )
    
    roi_result = campaign.calculate_roi()
    print(f"\n活动ID: {campaign.campaign_id}")
    print(f"活动名称: {campaign.campaign_name}")
    print(f"触达客户数: {campaign.customers_contacted}")
    print(f"成功挽留数: {campaign.customers_retained}")
    print(f"挽留成功率: {roi_result['retention_rate']:.1%}")
    print(f"活动成本: ¥{roi_result['total_cost']:,.2f}")
    print(f"挽回价值: ¥{roi_result['retained_value']:,.2f}")
    print(f"活动ROI: {roi_result['roi']:.2f}x")
```

### 2.7 效果评估与ROI分析

**项目投入**：

| 投入类别 | 金额（万元） | 说明 |
|---------|------------|------|
| 软件平台 | 400 | 机器学习平台、大数据组件 |
| 算力资源 | 300 | GPU服务器、存储扩容 |
| 开发实施 | 350 | 模型开发、系统集成、测试 |
| 数据治理 | 150 | 数据清洗、特征工程 |
| 运维成本（年） | 120 | 年度运维费用 |
| **总投资** | **1320** | 首年总投资 |

**量化收益**：

| 收益类别 | 年收益（万元） | 计算依据 |
|---------|--------------|---------|
| 减少客户流失 | 3500 | 流失率从18%降至14%，减少流失客户18万，单客户价值350元/年 |
| 挽留成本节约 | 800 | 精准挽留减少无效触达，节约营销成本 |
| ARPU提升 | 600 | 流失预警客户针对性运营，ARPU提升5% |
| 客服效率提升 | 300 | 预警工单前置，减少投诉处理成本 |
| **年总收益** | **5200** | 保守估计 |

**ROI计算**：

```
投资回报率(ROI) = (年收益 - 年成本) / 总投资 × 100%
               = (5200 - 120) / 1320 × 100%
               = 384.8%

投资回收期 = 总投资 / 年净收益
         = 1320 / 5080
         = 0.26 年（约3.1个月）
```

**性能指标对比**：

| 指标 | 改进前 | 改进后 | 提升幅度 |
|------|--------|--------|---------|
| 年度流失率 | 18% | 14% | -22% |
| 流失预警提前期 | 0天 | 45天 | +45天 |
| 挽留成功率 | 15% | 45% | 3倍 |
| 预测准确率 | N/A | 85% | - |
| 模型更新周期 | N/A | 周级 | - |
| 挽留活动ROI | 1.5x | 4.2x | 2.8倍 |

---

## 3. 案例2：金融欺诈检测系统

（保留原有模型部署与监控相关内容...）

## 4. 案例3：零售客户细分与精准营销系统

（保留原有CRISP-DM流程相关内容...）

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-15
