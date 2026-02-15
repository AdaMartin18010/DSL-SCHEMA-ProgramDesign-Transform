# 商业智能Schema实践案例

## 📑 目录

- [商业智能Schema实践案例](#商业智能schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：跨国制造企业全球运营分析平台](#2-案例1跨国制造企业全球运营分析平台)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估与ROI分析](#27-效果评估与roi分析)
  - [3. 案例2：自助式分析平台](#3-案例2自助式分析平台)
  - [4. 案例3：移动端管理驾驶舱](#4-案例3移动端管理驾驶舱)

---

## 1. 案例概述

本文档提供商业智能Schema在实际企业应用中的深度实践案例，涵盖全球运营分析、自助式BI、移动驾驶舱等企业级场景。

---

## 2. 案例1：跨国制造企业全球运营分析平台

### 2.1 企业背景

**企业简介**：
某跨国制造集团（以下简称"华智制造"）成立于1985年，是全球领先的智能制造解决方案提供商。集团在全球拥有12个生产基地、50个销售子公司，员工总数超过8万人，年营收超过800亿元人民币。

**业务规模**：

| 指标 | 数值 |
|------|------|
| 生产基地 | 12个（6个国家） |
| 销售子公司 | 50个（30个国家） |
| 年营收 | 800亿+ RMB |
| 产品SKU | 5000+ |
| 年订单量 | 200万+ |
| 供应商 | 2000+ |
| 客户数 | 10万+ |

### 2.2 业务痛点

**痛点1：数据孤岛严重**
各区域、各业务系统数据分散，全球运营数据无法统一视图，总部难以实时掌握整体运营状况。

**痛点2：报表滞后**
月度经营分析报告需要15个工作日才能出具，决策严重滞后，错失市场机会。

**痛点3：多币种多语言**
涉及30个国家、20种货币、10种语言，数据整合和展示复杂度高。

**痛点4：缺乏预警机制**
关键指标异常无法及时发现，供应链中断、质量问题等风险响应迟缓。

**痛点5：决策支持不足**
管理层需要综合分析多维度数据，但现有工具无法提供深度洞察和智能建议。

### 2.3 业务目标

- 建立全球统一数据视图，支持多币种多语言
- 实现T+1的报表出具时效
- 建立智能预警体系，风险响应时间缩短80%
- 支持多维度自助分析，降低IT依赖

### 2.4 技术挑战

1. 多源异构数据整合（ERP、MES、CRM、SCM等）
2. 全球网络延迟和数据同步
3. 大数据量高性能查询
4. 复杂权限管理（数据隔离）
5. 多终端适配（PC、平板、手机）

### 2.5 解决方案

采用云原生BI架构，核心组件：
- 数据层：Snowflake云数据仓库
- 建模层：dbt数据转换
- BI引擎：Power BI + 自研分析引擎
- 移动端：自研管理驾驶舱App

### 2.6 完整代码实现

```python
#!/usr/bin/env python3
"""
跨国制造企业全球运营分析平台
支持多币种、多语言、多组织的企业级BI系统
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime
import json


class ChartType(str, Enum):
    """图表类型"""
    KPI_CARD = "KPICard"
    LINE_CHART = "LineChart"
    BAR_CHART = "BarChart"
    PIE_CHART = "PieChart"
    TABLE = "Table"
    MAP = "Map"
    GAUGE = "Gauge"
    TREEMAP = "Treemap"
    WATERFALL = "Waterfall"


class CurrencyCode(str, Enum):
    """货币代码"""
    CNY = "CNY"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    GBP = "GBP"


@dataclass
class CurrencyRate:
    """汇率"""
    from_currency: CurrencyCode
    to_currency: CurrencyCode
    rate: Decimal
    effective_date: datetime


@dataclass
class KPIIndicator:
    """KPI指标"""
    kpi_id: str
    kpi_name: str
    kpi_name_localized: Dict[str, str]  # 多语言名称
    value: Decimal
    target: Decimal
    unit: str
    currency: Optional[CurrencyCode] = None
    comparison_value: Optional[Decimal] = None  # 对比值（如同比）
    trend: str = "up"  # up, down, flat
    
    def get_achievement_rate(self) -> Decimal:
        """达成率"""
        if self.target == 0:
            return Decimal('0')
        return (self.value / self.target * 100).quantize(Decimal('0.01'))
    
    def get_change_rate(self) -> Decimal:
        """变化率"""
        if not self.comparison_value or self.comparison_value == 0:
            return Decimal('0')
        return ((self.value - self.comparison_value) / self.comparison_value * 100).quantize(Decimal('0.01'))


@dataclass
class ChartConfig:
    """图表配置"""
    chart_id: str
    chart_type: ChartType
    chart_title: str
    data_source: str
    x_axis_field: Optional[str] = None
    y_axis_field: Optional[str] = None
    series_fields: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    drill_down_enabled: bool = True


@dataclass
class DashboardPanel:
    """仪表板面板"""
    panel_id: str
    panel_title: str
    position_x: int
    position_y: int
    width: int
    height: int
    kpi_indicators: List[KPIIndicator] = field(default_factory=list)
    charts: List[ChartConfig] = field(default_factory=list)


@dataclass
class GlobalBIReport:
    """全球BI报表"""
    report_id: str
    report_name: str
    report_name_localized: Dict[str, str]
    description: str
    panels: List[DashboardPanel] = field(default_factory=list)
    supported_currencies: List[CurrencyCode] = field(default_factory=list)
    supported_languages: List[str] = field(default_factory=list)
    
    def add_panel(self, panel: DashboardPanel):
        """添加面板"""
        self.panels.append(panel)


@dataclass
class ManufacturingBIPlatform:
    """制造业BI平台"""
    platform_id: str
    platform_name: str
    reports: Dict[str, GlobalBIReport] = field(default_factory=dict)
    currency_rates: Dict[str, CurrencyRate] = field(default_factory=dict)
    
    def create_global_operations_report(self) -> GlobalBIReport:
        """创建全球运营分析报表"""
        report = GlobalBIReport(
            report_id="RPT-GLOBAL-OPS-001",
            report_name="Global Operations Dashboard",
            report_name_localized={
                "en": "Global Operations Dashboard",
                "zh": "全球运营分析",
                "ja": "グローバル運営分析",
                "de": "Globale Betriebsanalyse"
            },
            description="Global manufacturing operations overview",
            supported_currencies=[CurrencyCode.CNY, CurrencyCode.USD, CurrencyCode.EUR],
            supported_languages=["en", "zh", "ja", "de"]
        )
        
        # KPI面板
        kpi_panel = DashboardPanel(
            panel_id="PANEL-KPI-001",
            panel_title="Key Performance Indicators",
            position_x=0,
            position_y=0,
            width=12,
            height=2
        )
        
        # 核心KPI
        kpis = [
            KPIIndicator(
                kpi_id="KPI-REVENUE",
                kpi_name="Total Revenue",
                kpi_name_localized={"en": "Total Revenue", "zh": "总营收"},
                value=Decimal('8000000000'),
                target=Decimal('8500000000'),
                unit="Million",
                currency=CurrencyCode.CNY,
                comparison_value=Decimal('7500000000'),
                trend="up"
            ),
            KPIIndicator(
                kpi_id="KPI-ORDERS",
                kpi_name="Order Volume",
                kpi_name_localized={"en": "Order Volume", "zh": "订单量"},
                value=Decimal('2000000'),
                target=Decimal('2200000'),
                unit="Orders",
                comparison_value=Decimal('1850000'),
                trend="up"
            ),
            KPIIndicator(
                kpi_id="KPI-OTD",
                kpi_name="On-Time Delivery",
                kpi_name_localized={"en": "On-Time Delivery", "zh": "准时交付率"},
                value=Decimal('94.5'),
                target=Decimal('95.0'),
                unit="%",
                comparison_value=Decimal('92.0'),
                trend="up"
            ),
            KPIIndicator(
                kpi_id="KPI-QUALITY",
                kpi_name="Quality Rate",
                kpi_name_localized={"en": "Quality Rate", "zh": "合格率"},
                value=Decimal('99.2'),
                target=Decimal('99.5'),
                unit="%",
                comparison_value=Decimal('98.8'),
                trend="up"
            )
        ]
        kpi_panel.kpi_indicators = kpis
        report.add_panel(kpi_panel)
        
        # 营收趋势图表
        trend_chart = ChartConfig(
            chart_id="CHART-REVENUE-TREND",
            chart_type=ChartType.LINE_CHART,
            chart_title="Revenue Trend by Region",
            data_source="revenue_by_region_monthly",
            x_axis_field="month",
            y_axis_field="revenue",
            series_fields=["APAC", "EMEA", "Americas"]
        )
        trend_panel = DashboardPanel(
            panel_id="PANEL-TREND-001",
            panel_title="Regional Revenue Trend",
            position_x=0,
            position_y=2,
            width=6,
            height=4
        )
        trend_panel.charts.append(trend_chart)
        report.add_panel(trend_panel)
        
        # 产品类别占比
        product_chart = ChartConfig(
            chart_id="CHART-PRODUCT-SHARE",
            chart_type=ChartType.PIE_CHART,
            chart_title="Revenue by Product Category",
            data_source="revenue_by_product",
            series_fields=["category", "revenue"]
        )
        product_panel = DashboardPanel(
            panel_id="PANEL-PRODUCT-001",
            panel_title="Product Mix",
            position_x=6,
            position_y=2,
            width=6,
            height=4
        )
        product_panel.charts.append(product_chart)
        report.add_panel(product_panel)
        
        self.reports[report.report_id] = report
        return report
    
    def convert_currency(self, amount: Decimal, from_curr: CurrencyCode, to_curr: CurrencyCode) -> Decimal:
        """货币转换"""
        if from_curr == to_curr:
            return amount
        # 简化计算，实际应查询实时汇率
        rates = {
            (CurrencyCode.CNY, CurrencyCode.USD): Decimal('0.14'),
            (CurrencyCode.USD, CurrencyCode.CNY): Decimal('7.20'),
            (CurrencyCode.CNY, CurrencyCode.EUR): Decimal('0.13'),
            (CurrencyCode.EUR, CurrencyCode.CNY): Decimal('7.80'),
        }
        rate = rates.get((from_curr, to_curr), Decimal('1'))
        return (amount * rate).quantize(Decimal('0.01'))
    
    def generate_executive_summary(self, report_id: str) -> Dict:
        """生成高管摘要"""
        report = self.reports.get(report_id)
        if not report:
            return {}
        
        summary = {
            "report_name": report.report_name,
            "generated_at": datetime.now().isoformat(),
            "kpis": [],
            "alerts": []
        }
        
        for panel in report.panels:
            for kpi in panel.kpi_indicators:
                achievement = kpi.get_achievement_rate()
                change = kpi.get_change_rate()
                
                kpi_summary = {
                    "name": kpi.kpi_name,
                    "value": float(kpi.value),
                    "target": float(kpi.target),
                    "achievement": float(achievement),
                    "change": float(change),
                    "trend": kpi.trend
                }
                summary["kpis"].append(kpi_summary)
                
                # 生成预警
                if achievement < 90:
                    summary["alerts"].append({
                        "type": "warning",
                        "message": f"{kpi.kpi_name}达成率低于90%"
                    })
        
        return summary


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("华智制造 - 全球运营分析平台")
    print("=" * 70)
    
    # 创建平台
    platform = ManufacturingBIPlatform(
        platform_id="BI-HUazHI-001",
        platform_name="华智制造全球BI平台"
    )
    
    # 创建全球运营报表
    print("\n[1] 创建全球运营分析报表...")
    report = platform.create_global_operations_report()
    print(f"报表ID: {report.report_id}")
    print(f"报表名称: {report.report_name}")
    print(f"支持货币: {[c.value for c in report.supported_currencies]}")
    print(f"支持语言: {report.supported_languages}")
    print(f"面板数量: {len(report.panels)}")
    
    # 显示KPI详情
    print("\n[2] 核心KPI指标...")
    for panel in report.panels:
        for kpi in panel.kpi_indicators:
            print(f"\n  {kpi.kpi_name}:")
            print(f"    当前值: {kpi.value} {kpi.unit}")
            print(f"    目标值: {kpi.target} {kpi.unit}")
            print(f"    达成率: {kpi.get_achievement_rate()}%")
            print(f"    同比变化: {kpi.get_change_rate()}%")
    
    # 货币转换示例
    print("\n[3] 货币转换示例...")
    cny_amount = Decimal('100000000')
    usd_amount = platform.convert_currency(cny_amount, CurrencyCode.CNY, CurrencyCode.USD)
    print(f"  {cny_amount} CNY = {usd_amount} USD")
    
    # 生成高管摘要
    print("\n[4] 生成高管摘要...")
    summary = platform.generate_executive_summary(report.report_id)
    print(f"  生成时间: {summary['generated_at']}")
    print(f"  KPI数量: {len(summary['kpis'])}")
    print(f"  预警数量: {len(summary['alerts'])}")
    
    if summary['alerts']:
        print("\n  预警信息:")
        for alert in summary['alerts']:
            print(f"    - {alert['message']}")
```

### 2.7 效果评估与ROI分析

**项目投入**：

| 投入类别 | 金额（万元） |
|---------|------------|
| 软件平台 | 500 |
| 云服务 | 400 |
| 开发实施 | 600 |
| 培训 | 100 |
| **总投资** | **1600** |

**量化收益**：

| 收益类别 | 年收益（万元） |
|---------|--------------|
| 决策效率提升 | 1000 |
| 库存优化 | 1200 |
| 运营成本降低 | 800 |
| **年总收益** | **3000** |

**ROI计算**：
```
ROI = (3000 - 200) / 1600 × 100% = 175%
投资回收期 = 1600 / 2800 = 0.57年（约7个月）
```

---

**创建时间**：2025-01-21
**最后更新**：2025-02-15
