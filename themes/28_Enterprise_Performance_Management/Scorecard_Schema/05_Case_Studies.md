# 平衡计分卡Schema实践案例

## 📑 目录

- [平衡计分卡Schema实践案例](#平衡计分卡schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例：集团企业平衡计分卡战略执行平台](#2-案例集团企业平衡计分卡战略执行平台)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 解决方案](#25-解决方案)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估](#27-效果评估)

---

## 1. 案例概述

本文档提供平衡计分卡（Balanced Scorecard）Schema在实际企业战略管理中的应用案例，涵盖战略地图、指标设计、战略执行、绩效评估等真实场景。

**案例类型**：

1. **集团企业平衡计分卡战略执行平台**：战略地图、指标体系、战略协同
2. **事业部计分卡系统**：财务、客户、流程、学习成长维度
3. **职能部门计分卡**：支撑战略、服务内部、能力建设
4. **战略回顾与调整**：战略会议、偏差分析、战略调整

---

## 2. 案例：集团企业平衡计分卡战略执行平台

### 2.1 企业背景

**企业名称**：华能能源集团有限公司

**企业规模**：
- 主营业务：清洁能源发电、能源技术服务
- 员工总数：15,000+人
- 业务单元：8个发电事业部、3个技术公司
- 年营收：280亿元人民币
- 上市公司：上交所主板上市

**组织架构**：
- 集团总部：战略、投资、财务、人力
- 发电事业部：风电、光伏、水电、储能
- 技术公司：设计院、研究院、工程公司
- 区域公司：华北、华东、华南、西南

**现有战略管理状况**：
- 战略制定后缺乏有效分解和跟踪
- 各部门绩效指标孤立，缺乏协同
- 财务指标独大，忽视非财务指标
- 战略回顾会议流于形式，缺乏数据支撑

### 2.2 业务痛点

1. **战略落地困难**：集团五年战略制定后，缺乏有效分解机制，战略目标停留在纸面，各事业部各自为政，战略执行偏差大，年目标达成率仅60%。

2. **指标体系失衡**：过度关注财务指标（占比80%），忽视客户满意度、内部流程、员工成长等非财务指标，短期行为多，长期竞争力受损。

3. **战略协同缺失**：各业务单元、职能部门目标孤立，缺乏横向协同机制，跨部门项目推进困难，内耗严重，协同效率低。

4. **战略执行不可见**：战略执行进度无法实时掌握，问题和风险发现滞后，只能事后补救，无法事前预防，战略调整响应慢。

5. **战略与预算脱节**：战略目标与年度预算、绩效考核割裂，预算编制不以战略为导向，资源配置不合理，战略投入不足。

### 2.3 业务目标

1. **构建完整战略地图**：建立涵盖财务、客户、流程、学习成长四个维度的战略地图，战略目标覆盖率100%，战略路径清晰可见。

2. **建立平衡指标体系**：四个维度指标均衡发展，财务指标占比降至50%以下，非财务指标量化可考核，指标协同度提升60%。

3. **实现战略纵向协同**：战略目标层层分解至事业部、部门、岗位，纵向对齐率95%以上，确保战略意图有效传递。

4. **建立战略执行监控**：战略执行进度实时可视化，关键指标偏离目标5%自动预警，战略会议有数据支撑，决策响应速度提升3倍。

5. **打通战略-预算-绩效闭环**：战略目标与年度预算、绩效考核紧密衔接，战略投入占比提升至30%，资源配置与战略一致。

### 2.4 技术挑战

1. **复杂战略关系建模**：战略地图涉及因果关系链、指标关联关系，需要灵活的数据模型支持复杂网络关系。

2. **多维度指标计算**：四个维度指标计算逻辑不同，需要支持累计、平均、同比环比、阈值等多种计算方式。

3. **多层级数据汇总**：集团-事业部-部门-岗位四级架构，数据需要向上汇总、向下分解，需要强大的聚合计算能力。

4. **实时战略仪表盘**：高管需要随时掌握战略执行情况，需要高性能数据刷新和移动端适配。

5. **与现有系统集成**：需要与ERP、BI、预算系统、HR系统集成，实现数据自动采集。

### 2.5 解决方案

**使用Schema定义平衡计分卡战略执行平台**：

- **战略地图Schema**：定义战略目标、因果关系、战略主题
- **计分卡Schema**：定义四个维度、指标、目标值
- **战略行动Schema**：定义战略举措、责任人、里程碑
- **战略会议Schema**：定义会议模板、议程、决议
- **战略分析Schema**：定义偏差分析、根因分析、预测

### 2.6 完整代码实现

**平衡计分卡战略执行平台Schema实现**：

```python
#!/usr/bin/env python3
"""
平衡计分卡战略执行平台Schema实现
Balanced Scorecard Strategy Execution Platform Schema Implementation
"""

from typing import Dict, List, Optional, Set
from datetime import date, datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict


class Perspective(str, Enum):
    """计分卡维度"""
    FINANCIAL = "财务"
    CUSTOMER = "客户"
    INTERNAL_PROCESS = "内部流程"
    LEARNING_GROWTH = "学习成长"


class StrategyTheme(str, Enum):
    """战略主题"""
    PROFITABILITY = "盈利增长"
    CUSTOMER_EXCELLENCE = "客户卓越"
    OPERATIONAL_EXCELLENCE = "运营卓越"
    INNOVATION = "创新驱动"
    PEOPLE_DEVELOPMENT = "人才发展"


class ObjectiveType(str, Enum):
    """目标类型"""
    OUTCOME = "结果型"
    DRIVER = "驱动型"
    SUPPORT = "支撑型"


class MeasureType(str, Enum):
    """指标类型"""
    LEADING = "领先指标"
    LAGGING = "滞后指标"


class Status(str, Enum):
    """状态"""
    NOT_STARTED = "未开始"
    IN_PROGRESS = "进行中"
    AT_RISK = "有风险"
    DELAYED = "延期"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


@dataclass
class StrategicObjective:
    """战略目标"""
    objective_id: str
    objective_code: str
    name: str
    description: str
    perspective: Perspective
    theme: StrategyTheme
    objective_type: ObjectiveType = ObjectiveType.OUTCOME
    owner_id: str = ""
    parent_id: Optional[str] = None
    level: int = 1
    sequence: int = 1
    is_key: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_full_code(self, obj_map: Dict[str, 'StrategicObjective']) -> str:
        """获取完整编码"""
        codes = [self.objective_code]
        current = self
        while current.parent_id and current.parent_id in obj_map:
            current = obj_map[current.parent_id]
            codes.insert(0, current.objective_code)
        return '.'.join(codes)


@dataclass
class CausalLink:
    """因果关系"""
    link_id: str
    from_objective_id: str
    to_objective_id: str
    link_type: str = "因果"
    description: Optional[str] = None
    strength: int = 5


@dataclass
class PerformanceMeasure:
    """绩效指标"""
    measure_id: str
    measure_code: str
    name: str
    description: str
    objective_id: str
    measure_type: MeasureType
    unit: str
    calculation_formula: Optional[str] = None
    data_source: Optional[str] = None
    frequency: str = "月度"
    is_key: bool = False
    benchmark_internal: Optional[Decimal] = None
    benchmark_external: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Target:
    """目标值"""
    target_id: str
    measure_id: str
    period_year: int
    period_type: str
    period_month: Optional[int] = None
    target_value: Decimal
    warning_threshold: Optional[Decimal] = None
    stretch_target: Optional[Decimal] = None
    baseline: Optional[Decimal] = None


@dataclass
class Actual:
    """实际值"""
    actual_id: str
    measure_id: str
    period_year: int
    period_type: str
    period_month: Optional[int] = None
    actual_value: Decimal
    input_date: datetime = field(default_factory=datetime.now)
    input_by: Optional[str] = None


@dataclass
class Score:
    """得分"""
    score_id: str
    measure_id: str
    target_id: str
    period_year: int
    period_type: str
    period_month: Optional[int] = None
    target_value: Decimal
    actual_value: Decimal
    achievement_rate: Decimal = Decimal('0')
    score: Decimal = Decimal('0')
    status: str = "正常"


@dataclass
class StrategicInitiative:
    """战略举措"""
    initiative_id: str
    initiative_code: str
    name: str
    description: str
    objective_id: str
    owner_id: str
    start_date: date
    end_date: date
    budget: Decimal = Decimal('0')
    status: Status = Status.NOT_STARTED
    progress: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_remaining_days(self) -> int:
        """获取剩余天数"""
        if self.end_date < date.today():
            return 0
        return (self.end_date - date.today()).days
    
    def is_overdue(self) -> bool:
        """是否逾期"""
        return self.end_date < date.today() and self.status != Status.COMPLETED


@dataclass
class Milestone:
    """里程碑"""
    milestone_id: str
    initiative_id: str
    name: str
    due_date: date
    status: Status = Status.NOT_STARTED
    completion_date: Optional[date] = None


@dataclass
class Scorecard:
    """计分卡"""
    scorecard_id: str
    scorecard_name: str
    owner_id: str
    owner_type: str
    period_year: int
    objectives: List[str] = field(default_factory=list)
    measures: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyMap:
    """战略地图"""
    map_id: str
    map_name: str
    period_year: int
    objectives: List[StrategicObjective] = field(default_factory=list)
    links: List[CausalLink] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_perspective_objectives(self, perspective: Perspective) -> List[StrategicObjective]:
        """获取某维度的目标"""
        return [obj for obj in self.objectives if obj.perspective == perspective]
    
    def get_objective_drivers(self, objective_id: str) -> List[StrategicObjective]:
        """获取目标的驱动因素"""
        drivers = []
        for link in self.links:
            if link.to_objective_id == objective_id:
                obj = next((o for o in self.objectives if o.objective_id == link.from_objective_id), None)
                if obj:
                    drivers.append(obj)
        return drivers


@dataclass
class BSCSystem:
    """平衡计分卡系统"""
    strategy_maps: Dict[str, StrategyMap] = field(default_factory=dict)
    objectives: Dict[str, StrategicObjective] = field(default_factory=dict)
    causal_links: Dict[str, CausalLink] = field(default_factory=dict)
    measures: Dict[str, PerformanceMeasure] = field(default_factory=dict)
    targets: Dict[str, Target] = field(default_factory=dict)
    actuals: Dict[str, Actual] = field(default_factory=dict)
    scores: Dict[str, Score] = field(default_factory=dict)
    initiatives: Dict[str, StrategicInitiative] = field(default_factory=dict)
    milestones: Dict[str, Milestone] = field(default_factory=dict)
    scorecards: Dict[str, Scorecard] = field(default_factory=dict)
    
    def create_strategy_map(self, strategy_map: StrategyMap) -> str:
        """创建战略地图"""
        if not strategy_map.map_id:
            strategy_map.map_id = str(uuid.uuid4())
        self.strategy_maps[strategy_map.map_id] = strategy_map
        return strategy_map.map_id
    
    def add_objective(self, objective: StrategicObjective) -> str:
        """添加战略目标"""
        if not objective.objective_id:
            objective.objective_id = str(uuid.uuid4())
        self.objectives[objective.objective_id] = objective
        return objective.objective_id
    
    def add_causal_link(self, link: CausalLink) -> str:
        """添加因果关系"""
        if not link.link_id:
            link.link_id = str(uuid.uuid4())
        self.causal_links[link.link_id] = link
        return link.link_id
    
    def add_measure(self, measure: PerformanceMeasure) -> str:
        """添加绩效指标"""
        if not measure.measure_id:
            measure.measure_id = str(uuid.uuid4())
        self.measures[measure.measure_id] = measure
        return measure.measure_id
    
    def add_initiative(self, initiative: StrategicInitiative) -> str:
        """添加战略举措"""
        if not initiative.initiative_id:
            initiative.initiative_id = str(uuid.uuid4())
        self.initiatives[initiative.initiative_id] = initiative
        return initiative.initiative_id
    
    def calculate_score(self, measure_id: str, year: int, month: int) -> Optional[Score]:
        """计算得分"""
        # 查找目标
        target = None
        for t in self.targets.values():
            if t.measure_id == measure_id and t.period_year == year and t.period_month == month:
                target = t
                break
        
        if not target:
            return None
        
        # 查找实际值
        actual = None
        for a in self.actuals.values():
            if a.measure_id == measure_id and a.period_year == year and a.period_month == month:
                actual = a
                break
        
        if not actual:
            return None
        
        # 计算达成率
        if target.target_value != 0:
            achievement = actual.actual_value / target.target_value * 100
        else:
            achievement = Decimal('0')
        
        # 计算得分（封顶110分）
        score_value = min(Decimal('110'), achievement)
        
        score = Score(
            score_id=str(uuid.uuid4()),
            measure_id=measure_id,
            target_id=target.target_id,
            period_year=year,
            period_type='月度',
            period_month=month,
            target_value=target.target_value,
            actual_value=actual.actual_value,
            achievement_rate=achievement,
            score=score_value
        )
        
        # 判断状态
        if target.warning_threshold and achievement < target.warning_threshold:
            score.status = "预警"
        
        self.scores[score.score_id] = score
        return score
    
    def get_scorecard_summary(self, scorecard_id: str, year: int, month: int) -> Dict:
        """获取计分卡汇总"""
        scorecard = self.scorecards.get(scorecard_id)
        if not scorecard:
            return {}
        
        perspective_scores = defaultdict(lambda: {'count': 0, 'score': Decimal('0')})
        
        for measure_id in scorecard.measures:
            # 计算得分
            score = self.calculate_score(measure_id, year, month)
            if score:
                measure = self.measures.get(measure_id)
                if measure:
                    obj = self.objectives.get(measure.objective_id)
                    if obj:
                        perspective_scores[obj.perspective.value]['count'] += 1
                        perspective_scores[obj.perspective.value]['score'] += score.score
        
        return {
            'scorecard_id': scorecard_id,
            'scorecard_name': scorecard.scorecard_name,
            'period': f"{year}-{month:02d}",
            'perspectives': {
                persp: {
                    'count': data['count'],
                    'avg_score': float(data['score'] / data['count']) if data['count'] > 0 else 0
                }
                for persp, data in perspective_scores.items()
            }
        }
    
    def get_initiative_summary(self, objective_id: Optional[str] = None) -> Dict:
        """获取战略举措汇总"""
        initiatives = list(self.initiatives.values())
        if objective_id:
            initiatives = [i for i in initiatives if i.objective_id == objective_id]
        
        total = len(initiatives)
        if total == 0:
            return {}
        
        by_status = defaultdict(int)
        for i in initiatives:
            by_status[i.status.value] += 1
        
        return {
            'total': total,
            'by_status': dict(by_status),
            'completed': by_status[Status.COMPLETED.value],
            'in_progress': by_status[Status.IN_PROGRESS.value],
            'at_risk': by_status[Status.AT_RISK.value],
            'overdue': len([i for i in initiatives if i.is_overdue()]),
            'avg_progress': sum(i.progress for i in initiatives) / total if total > 0 else 0
        }


# 使用示例
if __name__ == '__main__':
    bsc = BSCSystem()
    
    # 创建战略地图
    strategy_map = StrategyMap(
        map_id='MAP001',
        map_name='华能能源2025战略地图',
        period_year=2025
    )
    bsc.create_strategy_map(strategy_map)
    
    # 添加战略目标 - 财务维度
    fin_obj1 = StrategicObjective(
        objective_id='OBJ001',
        objective_code='F1',
        name='提升股东回报',
        description='通过盈利增长提升股东价值',
        perspective=Perspective.FINANCIAL,
        theme=StrategyTheme.PROFITABILITY,
        objective_type=ObjectiveType.OUTCOME,
        is_key=True
    )
    bsc.add_objective(fin_obj1)
    
    # 添加战略目标 - 客户维度
    cust_obj1 = StrategicObjective(
        objective_id='OBJ002',
        objective_code='C1',
        name='提升客户满意度',
        description='提供优质能源服务，提高客户满意度',
        perspective=Perspective.CUSTOMER,
        theme=StrategyTheme.CUSTOMER_EXCELLENCE,
        objective_type=ObjectiveType.DRIVER
    )
    bsc.add_objective(cust_obj1)
    
    # 添加因果关系
    link = CausalLink(
        link_id='LINK001',
        from_objective_id='OBJ002',
        to_objective_id='OBJ001',
        description='客户满意度提升带动收入增长'
    )
    bsc.add_causal_link(link)
    
    # 添加绩效指标
    measure1 = PerformanceMeasure(
        measure_id='M001',
        measure_code='F1.1',
        name='净资产收益率',
        description='净利润/平均净资产',
        objective_id='OBJ001',
        measure_type=MeasureType.LAGGING,
        unit='%',
        frequency='季度',
        is_key=True
    )
    bsc.add_measure(measure1)
    
    measure2 = PerformanceMeasure(
        measure_id='M002',
        measure_code='C1.1',
        name='客户满意度评分',
        description='年度客户满意度调查评分',
        objective_id='OBJ002',
        measure_type=MeasureType.LAGGING,
        unit='分',
        frequency='年度'
    )
    bsc.add_measure(measure2)
    
    # 添加目标值
    target1 = Target(
        target_id='TGT001',
        measure_id='M001',
        period_year=2025,
        period_type='年度',
        target_value=Decimal('12'),
        warning_threshold=Decimal('10')
    )
    bsc.targets[target1.target_id] = target1
    
    target2 = Target(
        target_id='TGT002',
        measure_id='M002',
        period_year=2025,
        period_type='年度',
        target_value=Decimal('85'),
        warning_threshold=Decimal('80')
    )
    bsc.targets[target2.target_id] = target2
    
    # 添加实际值
    actual1 = Actual(
        actual_id='ACT001',
        measure_id='M001',
        period_year=2025,
        period_type='月度',
        period_month=1,
        actual_value=Decimal('11.5')
    )
    bsc.actuals[actual1.actual_id] = actual1
    
    # 添加战略举措
    initiative = StrategicInitiative(
        initiative_id='INIT001',
        initiative_code='S1',
        name='新能源产能扩张计划',
        description='新增500MW风电和300MW光伏产能',
        objective_id='OBJ001',
        owner_id='VP001',
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        budget=Decimal('2000000000'),
        status=Status.IN_PROGRESS,
        progress=35
    )
    bsc.add_initiative(initiative)
    
    # 打印统计
    print("=" * 70)
    print("平衡计分卡战略执行平台统计报告")
    print("=" * 70)
    
    print(f"\n战略地图: {strategy_map.map_name}")
    print(f"  战略目标数: {len(bsc.objectives)}")
    print(f"  因果关系数: {len(bsc.causal_links)}")
    
    # 按维度统计目标
    by_perspective = defaultdict(list)
    for obj in bsc.objectives.values():
        by_perspective[obj.perspective.value].append(obj)
    
    print(f"\n战略目标分布:")
    for persp, objs in by_perspective.items():
        print(f"  {persp}: {len(objs)}个")
    
    print(f"\n绩效指标数: {len(bsc.measures)}")
    print(f"  关键指标: {len([m for m in bsc.measures.values() if m.is_key])}")
    
    # 战略举措统计
    init_summary = bsc.get_initiative_summary()
    print(f"\n战略举措统计:")
    print(f"  总举措数: {init_summary['total']}")
    print(f"  已完成: {init_summary['completed']}")
    print(f"  进行中: {init_summary['in_progress']}")
    print(f"  有风险: {init_summary['at_risk']}")
    print(f"  逾期: {init_summary['overdue']}")
    print(f"  平均进度: {init_summary['avg_progress']:.1f}%")
    
    # 计算得分
    score = bsc.calculate_score('M001', 2025, 1)
    if score:
        print(f"\n指标得分:")
        print(f"  指标: {bsc.measures['M001'].name}")
        print(f"  目标值: {score.target_value}%")
        print(f"  实际值: {score.actual_value}%")
        print(f"  达成率: {score.achievement_rate:.1f}%")
        print(f"  得分: {score.score:.1f}")
        print(f"  状态: {score.status}")
```

### 2.7 效果评估

**关键绩效指标（KPI）对比**：

| 指标 | 改进前 | 改进后（18个月） | 提升幅度 |
|------|--------|-----------------|----------|
| 战略目标达成率 | 60% | 87% | +27% |
| 战略透明度 | 20% | 95% | +75pp |
| 战略对齐度 | 35% | 92% | +57pp |
| 战略调整响应时间 | 6个月 | 1个月 | -83% |
| 跨部门协作效率 | 基准 | +60% | +60% |
| 非财务指标占比 | 20% | 55% | +35pp |
| 战略会议效率 | - | +3倍 | +3倍 |
| 战略投入占比 | 15% | 32% | +17pp |

**投资回报分析（ROI）**：

| 投资/收益项目 | 金额（万元） | 说明 |
|--------------|-------------|------|
| **总投资** | **850** | |
| 平台软件费用 | 350 | BSC平台+定制开发 |
| 战略咨询费用 | 280 | 战略梳理、指标设计 |
| 培训实施费用 | 150 | 全员培训、上线支持 |
| 运维费用 | 70 | 技术支持 |
| **年度收益** | **3,200** | |
| 战略达成提升 | 1,500 | 目标达成率提升收益 |
| 资源配置优化 | 800 | 战略投入效率提升 |
| 管理效率提升 | 500 | 会议、决策效率提升 |
| 协同效率提升 | 400 | 跨部门协作节约 |
| **首年净收益** | **2,350** | |
| **投资回报率（ROI）** | **276.5%** | 首年 |
| **投资回收期** | **3.2个月** | |

**业务价值**：

1. **战略落地能力显著增强**：战略目标从纸面走向执行，目标达成率从60%提升至87%，五年战略规划的可实现性大幅提高。

2. **战略视野更加平衡**：非财务指标占比从20%提升至55%，企业在追求短期利润的同时，更加注重客户、流程、人才等长期竞争力建设。

3. **战略协同效果明显**：各业务单元、职能部门目标清晰可见，横向协同效率提升60%，重大项目按期交付率提升40%。

4. **战略决策科学高效**：战略执行进度实时可见，偏差及时发现及时调整，战略调整响应时间从6个月缩短至1个月。

5. **组织能力持续提升**：战略-预算-绩效闭环打通，资源配置与战略一致，战略投入占比从15%提升至32%，战略执行成为组织习惯。

**成功经验**：

1. **高层亲自推动**：董事长和总裁亲自参与战略地图设计，各事业部总经理担任维度Owner，确保战略重视度。
2. **战略梳理先行**：聘请专业咨询公司梳理战略，确保战略地图设计的科学性和完整性。
3. **分步试点推广**：先在集团总部和2个事业部试点，积累经验后全面推广。
4. **持续培训辅导**：定期开展BSC方法培训和最佳实践分享，让战略管理成为组织能力。

---

**参考案例**：

- [平衡计分卡协会案例](https://www.balancedscorecard.org/)
- [卡普兰与诺顿战略管理](https://www.whatmatters.com/)
