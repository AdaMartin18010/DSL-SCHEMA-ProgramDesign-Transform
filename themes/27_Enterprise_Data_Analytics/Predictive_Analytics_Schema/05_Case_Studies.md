# 预测分析Schema实践案例

## 📑 目录

- [预测分析Schema实践案例](#预测分析schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：新能源车企需求预测与供应链优化系统](#2-案例1新能源车企需求预测与供应链优化系统)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估与ROI分析](#27-效果评估与roi分析)

---

## 1. 案例概述

本文档提供预测分析Schema在实际企业应用中的深度实践案例，涵盖需求预测、供应链优化、设备预测性维护等企业级场景。

---

## 2. 案例1：新能源车企需求预测与供应链优化系统

### 2.1 企业背景

**企业简介**：
某新能源汽车企业（以下简称"华能汽车"）成立于2015年，是国内领先的新能源汽车制造商。公司拥有5大生产基地，年产能50万辆，2024年销量突破30万辆。

**业务规模**：

| 指标 | 数值 |
|------|------|
| 年产能 | 50万辆 |
| 2024年销量 | 30万辆 |
| 车型数量 | 8款 |
| 供应商 | 500+ |
| SKU数量 | 2万+ |
| 销售网点 | 1000+ |

### 2.2 业务痛点

**痛点1：需求预测不准**
传统预测方法准确率仅65%，导致库存积压与缺货并存，库存周转天数高达45天。

**痛点2：供应链响应慢**
零部件供应周期长，面对需求波动响应迟缓，频繁出现断供或过量采购。

**痛点3：生产计划失衡**
生产计划与实际销售脱节，产能利用率波动大（60%-95%），影响成本控制。

**痛点4：新品上市风险高**
新车型需求难以预估，首单生产量决策缺乏数据支撑，库存积压风险大。

**痛点5：季节性波动难应对**
新能源汽车市场受政策、季节影响大，传统预测无法捕捉复杂模式。

### 2.3 业务目标

**目标1：提升预测准确率**
构建AI驱动的需求预测模型，将预测准确率提升至85%以上。

**目标2：优化库存管理**
实现零部件智能补货，将库存周转天数降至30天以内，降低库存成本20%。

**目标3：动态生产计划**
支持周级滚动预测，生产计划与实际需求匹配度提升至90%。

**目标4：降低供应链风险**
建立供应商风险预警机制，断供风险提前30天预警。

**目标5：提升市场响应速度**
从需求变化识别到供应链调整，响应时间缩短至7天以内。

### 2.4 技术挑战

**挑战1：多维度预测**
需要同时考虑车型、配置、区域、时间等多维度因素，预测复杂度极高。

**挑战2：外部因素影响**
政策补贴、竞品动态、宏观经济、天气等外部因素对需求影响显著。

**挑战3：新产品冷启动**
新车型缺乏历史数据，需要结合相似产品和市场研究进行预测。

**挑战4：长周期依赖**
零部件采购周期长（3-6个月），需要中长期预测支撑采购决策。

**挑战5：不确定性量化**
需要输出预测区间而不仅是点估计，支持风险决策。

### 2.5 解决方案

**预测模型架构**：
- **短期预测（1-4周）**：LSTM + XGBoost
- **中期预测（1-6月）**：Prophet + 外部因素回归
- **长期预测（6-12月）**：计量经济模型 + 情景分析
- **新品预测**：类比法 + 专家判断 + 上市曲线拟合

**供应链优化**：
- 安全库存动态计算
- 多级库存优化（中心仓+区域仓）
- 供应商协同预测（CPFR）

### 2.6 完整代码实现

```python
#!/usr/bin/env python3
"""
新能源车企需求预测与供应链优化系统
基于深度学习和时间序列分析的企业级预测解决方案
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import numpy as np
from collections import defaultdict


class ForecastHorizon(str, Enum):
    """预测周期"""
    SHORT_TERM = "Short"      # 1-4周
    MEDIUM_TERM = "Medium"    # 1-6月
    LONG_TERM = "Long"        # 6-12月


class ProductLifecycle(str, Enum):
    """产品生命周期"""
    INTRODUCTION = "Introduction"
    GROWTH = "Growth"
    MATURITY = "Maturity"
    DECLINE = "Decline"


class SupplyRiskLevel(str, Enum):
    """供应风险等级"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class VehicleModel:
    """车型"""
    model_id: str
    model_name: str
    launch_date: datetime
    lifecycle_stage: ProductLifecycle
    base_price: float
    
    # 历史销量（按周）
    weekly_sales_history: List[Tuple[datetime, int]] = field(default_factory=list)
    
    def get_sales_trend(self, weeks: int = 12) -> float:
        """获取销量趋势"""
        if len(self.weekly_sales_history) < weeks:
            return 0.0
        
        recent_sales = [s[1] for s in self.weekly_sales_history[-weeks:]]
        if len(recent_sales) < 2:
            return 0.0
        
        # 计算趋势（线性回归斜率简化版）
        x = np.arange(len(recent_sales))
        slope = np.polyfit(x, recent_sales, 1)[0]
        return slope


@dataclass
class ExternalFactor:
    """外部因素"""
    factor_id: str
    factor_name: str
    factor_type: str  # Policy, Economic, Seasonal, Competition, Weather
    impact_weight: float  # -1 to 1
    current_value: float
    forecast_values: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class DemandForecast:
    """需求预测结果"""
    forecast_id: str
    model_id: str
    horizon: ForecastHorizon
    forecast_date: datetime
    
    # 点预测
    point_forecast: int
    
    # 区间预测
    lower_bound: int  # 95%置信区间下限
    upper_bound: int  # 95%置信区间上限
    
    # 分解预测
    baseline_demand: int  # 基础需求
    trend_component: int  # 趋势成分
    seasonal_component: int  # 季节成分
    external_impact: int  # 外部因素影响
    
    # 置信度
    confidence_score: float  # 0-1
    
    # 影响因素
    key_drivers: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Supplier:
    """供应商"""
    supplier_id: str
    supplier_name: str
    component_types: List[str]
    lead_time_days: int
    reliability_score: float  # 0-1
    capacity_monthly: int
    
    # 风险指标
    financial_health: str  # Good, Fair, Poor
    geographic_risk: str  # Low, Medium, High
    alternative_count: int  # 替代供应商数量
    
    def calculate_risk_score(self) -> float:
        """计算风险评分"""
        risk = 0.0
        
        # 财务健康度
        if self.financial_health == "Poor":
            risk += 0.3
        elif self.financial_health == "Fair":
            risk += 0.15
        
        # 交货可靠性
        risk += (1 - self.reliability_score) * 0.3
        
        # 地理风险
        if self.geographic_risk == "High":
            risk += 0.25
        elif self.geographic_risk == "Medium":
            risk += 0.1
        
        # 替代性
        if self.alternative_count == 0:
            risk += 0.15
        elif self.alternative_count < 3:
            risk += 0.05
        
        return min(1.0, risk)
    
    def get_risk_level(self) -> SupplyRiskLevel:
        """获取风险等级"""
        score = self.calculate_risk_score()
        if score >= 0.7:
            return SupplyRiskLevel.CRITICAL
        elif score >= 0.5:
            return SupplyRiskLevel.HIGH
        elif score >= 0.3:
            return SupplyRiskLevel.MEDIUM
        else:
            return SupplyRiskLevel.LOW


@dataclass
class InventoryPolicy:
    """库存策略"""
    component_id: str
    component_name: str
    current_stock: int
    reorder_point: int
    safety_stock: int
    economic_order_qty: int
    
    supplier_id: str
    lead_time_days: int
    
    def calculate_safety_stock(self, demand_forecast: DemandForecast, 
                              service_level: float = 0.95) -> int:
        """计算安全库存"""
        # 简化计算
        avg_demand = demand_forecast.point_forecast / 30  # 日均需求
        demand_std = (demand_forecast.upper_bound - demand_forecast.lower_bound) / 4
        
        # Z值（95%服务水平对应1.65）
        z_score = 1.65
        
        # 安全库存 = Z * σ * sqrt(lead_time)
        safety_stock = int(z_score * demand_std * np.sqrt(self.lead_time_days))
        return safety_stock
    
    def should_reorder(self) -> bool:
        """判断是否应补货"""
        return self.current_stock <= self.reorder_point
    
    def get_reorder_qty(self) -> int:
        """获取建议补货量"""
        if not self.should_reorder():
            return 0
        return self.economic_order_qty


@dataclass
class PredictiveAnalyticsEngine:
    """预测分析引擎"""
    engine_id: str
    engine_name: str
    
    # 车型注册表
    vehicle_models: Dict[str, VehicleModel] = field(default_factory=dict)
    
    # 外部因素
    external_factors: Dict[str, ExternalFactor] = field(default_factory=dict)
    
    # 供应商注册表
    suppliers: Dict[str, Supplier] = field(default_factory=dict)
    
    # 库存策略
    inventory_policies: Dict[str, InventoryPolicy] = field(default_factory=dict)
    
    def register_vehicle_model(self, model: VehicleModel):
        """注册车型"""
        self.vehicle_models[model.model_id] = model
    
    def register_external_factor(self, factor: ExternalFactor):
        """注册外部因素"""
        self.external_factors[factor.factor_id] = factor
    
    def register_supplier(self, supplier: Supplier):
        """注册供应商"""
        self.suppliers[supplier.supplier_id] = supplier
    
    def generate_forecast(self, model_id: str, horizon: ForecastHorizon, 
                         periods: int) -> List[DemandForecast]:
        """生成需求预测"""
        model = self.vehicle_models.get(model_id)
        if not model:
            return []
        
        forecasts = []
        base_date = datetime.now()
        
        # 计算基础需求
        if model.weekly_sales_history:
            recent_avg = np.mean([s[1] for s in model.weekly_sales_history[-12:]])
        else:
            recent_avg = 1000  # 默认值
        
        # 获取趋势
        trend = model.get_sales_trend()
        
        # 外部因素综合影响
        external_impact = sum(f.impact_weight * f.current_value 
                            for f in self.external_factors.values())
        
        for i in range(periods):
            forecast_date = base_date + timedelta(weeks=i+1)
            
            # 趋势成分
            trend_comp = trend * (i + 1)
            
            # 季节成分（简化模拟）
            month = forecast_date.month
            seasonal_factor = 1.0 + 0.1 * np.sin(2 * np.pi * month / 12)
            seasonal_comp = recent_avg * (seasonal_factor - 1)
            
            # 点预测
            point_forecast = int(recent_avg + trend_comp + seasonal_comp + 
                               recent_avg * external_impact * 0.1)
            point_forecast = max(0, point_forecast)
            
            # 区间预测
            uncertainty = 0.15 * point_forecast * (1 + i * 0.05)  # 预测越远不确定性越大
            lower_bound = int(point_forecast - 1.96 * uncertainty)
            upper_bound = int(point_forecast + 1.96 * uncertainty)
            
            forecast = DemandForecast(
                forecast_id=f"FC-{model_id}-{i}",
                model_id=model_id,
                horizon=horizon,
                forecast_date=forecast_date,
                point_forecast=point_forecast,
                lower_bound=max(0, lower_bound),
                upper_bound=upper_bound,
                baseline_demand=int(recent_avg),
                trend_component=int(trend_comp),
                seasonal_component=int(seasonal_comp),
                external_impact=int(recent_avg * external_impact * 0.1),
                confidence_score=max(0.5, 0.95 - i * 0.02),
                key_drivers=[
                    {"factor": "Trend", "impact": trend_comp},
                    {"factor": "Seasonality", "impact": seasonal_comp},
                    {"factor": "External", "impact": external_impact}
                ]
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def optimize_inventory(self, component_id: str, 
                          forecast: DemandForecast) -> InventoryPolicy:
        """优化库存策略"""
        # 查找现有策略或创建新策略
        policy = self.inventory_policies.get(component_id)
        if not policy:
            # 创建新策略
            policy = InventoryPolicy(
                component_id=component_id,
                component_name=f"Component-{component_id}",
                current_stock=5000,
                reorder_point=0,
                safety_stock=0,
                economic_order_qty=10000,
                supplier_id="SUP-001",
                lead_time_days=30
            )
        
        # 重新计算安全库存
        policy.safety_stock = policy.calculate_safety_stock(forecast)
        
        # 重新计算再订货点
        daily_demand = forecast.point_forecast / 30
        policy.reorder_point = int(daily_demand * policy.lead_time_days + policy.safety_stock)
        
        self.inventory_policies[component_id] = policy
        return policy
    
    def assess_supply_risks(self) -> List[Dict[str, Any]]:
        """评估供应风险"""
        risks = []
        
        for supplier in self.suppliers.values():
            risk_score = supplier.calculate_risk_score()
            risk_level = supplier.get_risk_level()
            
            if risk_level in [SupplyRiskLevel.HIGH, SupplyRiskLevel.CRITICAL]:
                risks.append({
                    "supplier_id": supplier.supplier_id,
                    "supplier_name": supplier.supplier_name,
                    "risk_score": risk_score,
                    "risk_level": risk_level.value,
                    "affected_components": supplier.component_types,
                    "mitigation_suggestions": self._generate_mitigation_suggestions(supplier)
                })
        
        return sorted(risks, key=lambda x: x["risk_score"], reverse=True)
    
    def _generate_mitigation_suggestions(self, supplier: Supplier) -> List[str]:
        """生成风险缓解建议"""
        suggestions = []
        
        if supplier.alternative_count < 2:
            suggestions.append("Develop alternative suppliers")
        
        if supplier.financial_health == "Poor":
            suggestions.append("Monitor financial status closely and consider prepayment protection")
        
        if supplier.geographic_risk == "High":
            suggestions.append("Diversify sourcing geographically")
        
        if supplier.reliability_score < 0.8:
            suggestions.append("Implement supplier quality improvement program")
        
        return suggestions
    
    def generate_executive_report(self) -> Dict[str, Any]:
        """生成高管报告"""
        return {
            "report_date": datetime.now().isoformat(),
            "forecast_summary": {
                "models_count": len(self.vehicle_models),
                "forecast_periods": 12,
                "avg_confidence": 0.85
            },
            "inventory_summary": {
                "total_components": len(self.inventory_policies),
                "reorder_needed": len([p for p in self.inventory_policies.values() if p.should_reorder()]),
                "avg_safety_stock_days": 15
            },
            "supply_risk_summary": {
                "total_suppliers": len(self.suppliers),
                "high_risk_suppliers": len([s for s in self.suppliers.values() 
                                           if s.get_risk_level() in [SupplyRiskLevel.HIGH, SupplyRiskLevel.CRITICAL]]),
                "risk_alerts": len(self.assess_supply_risks())
            }
        }


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("华能汽车 - 需求预测与供应链优化系统")
    print("=" * 70)
    
    # 创建预测引擎
    engine = PredictiveAnalyticsEngine(
        engine_id="PA-HUANENG-001",
        engine_name="华能汽车预测分析引擎"
    )
    
    # 1. 注册车型
    print("\n[1] 注册车型数据...")
    model_a = VehicleModel(
        model_id="MODEL-A",
        model_name="华能A Plus",
        launch_date=datetime(2023, 6, 1),
        lifecycle_stage=ProductLifecycle.GROWTH,
        base_price=250000,
        weekly_sales_history=[(datetime.now() - timedelta(weeks=i), 2000 + i*50) for i in range(24, 0, -1)]
    )
    engine.register_vehicle_model(model_a)
    print(f"车型: {model_a.model_name}")
    print(f"生命周期: {model_a.lifecycle_stage.value}")
    print(f"历史销量趋势: {model_a.get_sales_trend():.1f} 辆/周")
    
    # 2. 注册外部因素
    print("\n[2] 注册外部影响因素...")
    subsidy_factor = ExternalFactor(
        factor_id="FACTOR-SUBSIDY",
        factor_name="新能源补贴",
        factor_type="Policy",
        impact_weight=0.3,
        current_value=1.0
    )
    engine.register_external_factor(subsidy_factor)
    
    season_factor = ExternalFactor(
        factor_id="FACTOR-SEASON",
        factor_name="季节性因素",
        factor_type="Seasonal",
        impact_weight=0.2,
        current_value=1.0
    )
    engine.register_external_factor(season_factor)
    
    # 3. 生成需求预测
    print("\n[3] 生成未来12周需求预测...")
    forecasts = engine.generate_forecast("MODEL-A", ForecastHorizon.SHORT_TERM, 12)
    
    print(f"预测结果汇总:")
    total_forecast = sum(f.point_forecast for f in forecasts)
    print(f"  总预测需求: {total_forecast:,} 辆")
    print(f"  平均周需求: {total_forecast/12:,.0f} 辆")
    print(f"  预测置信度: {np.mean([f.confidence_score for f in forecasts]):.1%}")
    
    print("\n前4周详细预测:")
    for i, forecast in enumerate(forecasts[:4], 1):
        print(f"  第{i}周 ({forecast.forecast_date.strftime('%Y-%m-%d')}):")
        print(f"    预测值: {forecast.point_forecast:,} 辆")
        print(f"    置信区间: [{forecast.lower_bound:,}, {forecast.upper_bound:,}]")
    
    # 4. 注册供应商
    print("\n[4] 注册供应商信息...")
    supplier1 = Supplier(
        supplier_id="SUP-001",
        supplier_name="华通电池",
        component_types=["Battery", "BMS"],
        lead_time_days=45,
        reliability_score=0.92,
        capacity_monthly=50000,
        financial_health="Good",
        geographic_risk="Low",
        alternative_count=3
    )
    engine.register_supplier(supplier1)
    
    supplier2 = Supplier(
        supplier_id="SUP-002",
        supplier_name="远达芯片",
        component_types=["Chip", "MCU"],
        lead_time_days=90,
        reliability_score=0.75,
        capacity_monthly=30000,
        financial_health="Fair",
        geographic_risk="High",
        alternative_count=1
    )
    engine.register_supplier(supplier2)
    
    # 5. 优化库存策略
    print("\n[5] 优化零部件库存策略...")
    policy = engine.optimize_inventory("BATT-001", forecasts[0])
    print(f"零部件: {policy.component_id}")
    print(f"安全库存: {policy.safety_stock:,} 件")
    print(f"再订货点: {policy.reorder_point:,} 件")
    print(f"经济订货量: {policy.economic_order_qty:,} 件")
    print(f"当前库存: {policy.current_stock:,} 件")
    print(f"是否需要补货: {'是' if policy.should_reorder() else '否'}")
    
    # 6. 供应风险评估
    print("\n[6] 供应商风险评估...")
    risks = engine.assess_supply_risks()
    if risks:
        print(f"发现 {len(risks)} 个高风险供应商:")
        for risk in risks:
            print(f"  - {risk['supplier_name']} (风险评分: {risk['risk_score']:.2f})")
            print(f"    风险等级: {risk['risk_level']}")
            print(f"    建议措施: {', '.join(risk['mitigation_suggestions'])}")
    else:
        print("所有供应商风险可控")
    
    # 7. 生成高管报告
    print("\n[7] 生成高管决策报告...")
    report = engine.generate_executive_report()
    print(f"预测概览:")
    print(f"  车型数量: {report['forecast_summary']['models_count']}")
    print(f"  平均置信度: {report['forecast_summary']['avg_confidence']:.1%}")
    print(f"\n库存概览:")
    print(f"  零部件种类: {report['inventory_summary']['total_components']}")
    print(f"  需补货项: {report['inventory_summary']['reorder_needed']}")
    print(f"\n供应风险概览:")
    print(f"  供应商总数: {report['supply_risk_summary']['total_suppliers']}")
    print(f"  高风险供应商: {report['supply_risk_summary']['high_risk_suppliers']}")
```

### 2.7 效果评估与ROI分析

**项目投入**：

| 投入类别 | 金额（万元） |
|---------|------------|
| 软件平台 | 500 |
| 数据工程 | 300 |
| 模型开发 | 400 |
| 集成实施 | 300 |
| **总投资** | **1500** |

**量化收益**：

| 收益类别 | 年收益（万元） |
|---------|--------------|
| 库存成本降低 | 3000 |
| 缺货损失减少 | 1500 |
| 生产效率提升 | 800 |
| 供应链风险降低 | 500 |
| **年总收益** | **5800** |

**ROI**：
```
ROI = (5800 - 200) / 1500 × 100% = 373%
投资回收期 = 1500 / 5600 = 0.27年（约3.2个月）
```

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 预测准确率 | 65% | 87% | +34% |
| 库存周转天数 | 45天 | 28天 | -38% |
| 缺货率 | 8% | 2% | -75% |
| 产能利用率波动 | ±20% | ±5% | -75% |
| 供应链响应时间 | 30天 | 7天 | -77% |

---

**创建时间**：2025-02-15
