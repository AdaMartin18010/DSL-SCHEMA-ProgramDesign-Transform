# KPI管理Schema实践案例

## 📑 目录

- [KPI管理Schema实践案例](#kpi管理schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：企业销售KPI管理系统](#2-案例1企业销售kpi管理系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 解决方案](#23-解决方案)
    - [2.4 完整代码实现](#24-完整代码实现)
    - [2.5 效果评估](#25-效果评估)
  - [4. 案例3：KPI预警系统](#4-案例3kpi预警系统)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：KPI根因分析系统](#5-案例4kpi根因分析系统)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：KPI数据存储与分析系统](#6-案例5kpi数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供KPI管理Schema在实际企业应用中的实践案例，涵盖销售KPI管理、KPI预警、根因分析等真实场景。

**案例类型**：

1. **企业销售KPI管理系统**：销售KPI定义、监控、分析
2. **KPI到OLAP Cube转换工具**：KPI数据到OLAP转换
3. **KPI预警系统**：KPI预警和通知
4. **KPI根因分析系统**：KPI根因分析
5. **KPI数据存储与分析系统**：KPI数据分析和监控

**参考企业案例**：

- **平衡计分卡**：KPI管理最佳实践
- **绩效管理框架**：绩效管理标准

---

## 2. 案例1：企业销售KPI管理系统

### 2.1 业务背景

**企业背景**：
某零售公司需要构建销售KPI管理系统，实时监控销售KPI，支持KPI分析和报告，为业务决策提供数据支持。

**业务痛点**：

1. **KPI定义不统一**：不同部门KPI定义不一致
2. **监控不及时**：KPI监控不及时
3. **分析能力不足**：缺乏KPI分析能力
4. **报告效率低**：KPI报告生成效率低

**业务目标**：

- 统一KPI定义
- 实时KPI监控
- 增强KPI分析能力
- 提高报告效率

### 2.2 技术挑战

1. **KPI定义**：统一KPI定义标准
2. **实时监控**：实现KPI实时监控
3. **计算引擎**：构建KPI计算引擎
4. **预警机制**：实现KPI预警机制

### 2.3 解决方案

**使用Schema定义销售KPI管理系统**：

### 2.4 完整代码实现

**销售KPI管理Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
KPI管理Schema实现
"""

from typing import Dict, List, Optional
from datetime import date, datetime
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum

class KPIType(str, Enum):
    """KPI类型"""
    FINANCIAL = "Financial"
    OPERATIONAL = "Operational"
    CUSTOMER = "Customer"
    PROCESS = "Process"

class CalculationFrequency(str, Enum):
    """计算频率"""
    REAL_TIME = "RealTime"
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"

class TargetType(str, Enum):
    """目标类型"""
    ABSOLUTE = "Absolute"
    PERCENTAGE = "Percentage"
    GROWTH = "Growth"

@dataclass
class DateRange:
    """日期范围"""
    start_date: date
    end_date: date

@dataclass
class KPIDefinition:
    """KPI定义"""
    kpi_id: str
    kpi_name: str
    kpi_type: KPIType
    kpi_category: str
    calculation_formula: str
    data_source: str
    measurement_unit: str
    calculation_frequency: CalculationFrequency
    owner: str
    description: Optional[str] = None
    enabled: bool = True

    def calculate(self, data: Dict) -> Decimal:
        """计算KPI值"""
        # 这里应该根据calculation_formula计算KPI值
        # 简化示例
        if "SUM" in self.calculation_formula:
            field = self.calculation_formula.split("(")[1].split(")")[0]
            return Decimal(str(sum(data.get(field, []))))
        return Decimal('0')

@dataclass
class KPITarget:
    """KPI目标"""
    target_id: str
    kpi_id: str
    target_type: TargetType
    target_value: Decimal
    target_period: DateRange
    target_owner: str
    created_at: datetime = field(default_factory=datetime.now)

    def is_achieved(self, actual_value: Decimal) -> bool:
        """检查目标是否达成"""
        if self.target_type == TargetType.ABSOLUTE:
            return actual_value >= self.target_value
        elif self.target_type == TargetType.PERCENTAGE:
            return actual_value >= self.target_value
        return False

@dataclass
class KPIValue:
    """KPI值"""
    value_id: str
    kpi_id: str
    value: Decimal
    measurement_date: date
    completion_rate: Decimal = Decimal('0')
    status: str = "Normal"  # Normal, Warning, Critical
    created_at: datetime = field(default_factory=datetime.now)

    def calculate_completion_rate(self, target: KPITarget) -> Decimal:
        """计算完成率"""
        if target.target_value > 0:
            self.completion_rate = (self.value / target.target_value) * Decimal('100')
        return self.completion_rate

    def determine_status(self, target: KPITarget) -> str:
        """确定状态"""
        completion_rate = self.calculate_completion_rate(target)
        if completion_rate >= Decimal('100'):
            self.status = "Normal"
        elif completion_rate >= Decimal('80'):
            self.status = "Warning"
        else:
            self.status = "Critical"
        return self.status

@dataclass
class SalesKPIManagement:
    """销售KPI管理"""
    kpi_definitions: Dict[str, KPIDefinition] = field(default_factory=dict)
    kpi_targets: Dict[str, KPITarget] = field(default_factory=dict)
    kpi_values: List[KPIValue] = field(default_factory=list)

    def add_kpi_definition(self, kpi_def: KPIDefinition):
        """添加KPI定义"""
        self.kpi_definitions[kpi_def.kpi_id] = kpi_def

    def add_kpi_target(self, target: KPITarget):
        """添加KPI目标"""
        self.kpi_targets[target.kpi_id] = target

    def record_kpi_value(self, kpi_value: KPIValue):
        """记录KPI值"""
        # 计算完成率和状态
        if kpi_value.kpi_id in self.kpi_targets:
            target = self.kpi_targets[kpi_value.kpi_id]
            kpi_value.calculate_completion_rate(target)
            kpi_value.determine_status(target)

        self.kpi_values.append(kpi_value)

    def get_kpi_status(self, kpi_id: str) -> Optional[Dict]:
        """获取KPI状态"""
        if kpi_id not in self.kpi_definitions:
            return None

        kpi_def = self.kpi_definitions[kpi_id]
        target = self.kpi_targets.get(kpi_id)

        # 获取最新值
        latest_value = None
        for value in reversed(self.kpi_values):
            if value.kpi_id == kpi_id:
                latest_value = value
                break

        return {
            'kpi_id': kpi_id,
            'kpi_name': kpi_def.kpi_name,
            'current_value': float(latest_value.value) if latest_value else 0,
            'target_value': float(target.target_value) if target else 0,
            'completion_rate': float(latest_value.completion_rate) if latest_value else 0,
            'status': latest_value.status if latest_value else "Unknown"
        }

# 使用示例
if __name__ == '__main__':
    # 创建销售KPI管理系统
    kpi_mgmt = SalesKPIManagement()

    # 定义KPI
    sales_kpi = KPIDefinition(
        kpi_id="KPI-SALES-001",
        kpi_name="月度销售额",
        kpi_type=KPIType.FINANCIAL,
        kpi_category="销售",
        calculation_formula="SUM(sales_amount)",
        data_source="sales_transactions",
        measurement_unit="元",
        calculation_frequency=CalculationFrequency.MONTHLY,
        owner="销售部"
    )
    kpi_mgmt.add_kpi_definition(sales_kpi)

    # 设置KPI目标
    sales_target = KPITarget(
        target_id="TGT-SALES-001",
        kpi_id="KPI-SALES-001",
        target_type=TargetType.ABSOLUTE,
        target_value=Decimal('1000000'),
        target_period=DateRange(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31)
        ),
        target_owner="销售部"
    )
    kpi_mgmt.add_kpi_target(sales_target)

    # 记录KPI值
    sales_value = KPIValue(
        value_id="VAL-SALES-001",
        kpi_id="KPI-SALES-001",
        value=Decimal('950000'),
        measurement_date=date(2025, 1, 31)
    )
    kpi_mgmt.record_kpi_value(sales_value)

    # 获取KPI状态
    status = kpi_mgmt.get_kpi_status("KPI-SALES-001")
    print(f"KPI状态: {status}")
```

### 2.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| KPI定义统一性 | 60% | 100% | 40%提升 |
| 监控及时性 | 延迟1天 | 实时 | 显著提升 |
| 分析能力 | 低 | 高 | 显著提升 |
| 报告效率 | 低 | 高 | 显著提升 |

**业务价值**：

1. **KPI定义统一**：统一KPI定义标准
2. **实时监控**：实现KPI实时监控
3. **分析能力增强**：增强KPI分析能力
4. **报告效率提高**：提高报告效率

**经验教训**：

1. KPI定义需要标准化
2. 实时监控需要优化性能
3. 预警机制需要完善
4. 报告生成需要自动化

**参考案例**：

- [KPI管理最佳实践](https://www.balancedscorecard.org/)
- [绩效管理框架](https://www.ap-institute.com/)
  }
}

```

---

## 3. 案例2：KPI到OLAP Cube转换

### 3.1 场景描述

**应用场景**：
将KPI管理Schema转换为OLAP Cube格式，用于多维分析。

**业务需求**：

- 支持KPI多维分析
- 支持KPI钻取分析
- 支持KPI切片切块

### 3.2 实现代码

```python
def convert_kpi_to_olap_cube_complete(kpi_data: KPIManagementSchema) -> OLAPCube:
    """完整转换KPI管理Schema到OLAP Cube"""
    cube = OLAPCube()
    cube.name = "KPI_Cube"

    # 创建时间维度
    time_dimension = Dimension()
    time_dimension.name = "Time"
    time_dimension.hierarchies = [{
        "name": "Calendar",
        "levels": ["Year", "Quarter", "Month", "Week", "Day"]
    }]
    cube.dimensions.append(time_dimension)

    # 创建KPI分类维度
    category_dimension = Dimension()
    category_dimension.name = "KPI_Category"
    category_dimension.attributes = ["Category", "Type", "Owner", "Department"]
    cube.dimensions.append(category_dimension)

    # 创建组织维度
    org_dimension = Dimension()
    org_dimension.name = "Organization"
    org_dimension.hierarchies = [{
        "name": "Org_Hierarchy",
        "levels": ["Company", "Division", "Department", "Team"]
    }]
    cube.dimensions.append(org_dimension)

    # 转换KPI定义为度量
    for kpi in kpi_data.kpi_definition.kpi_definitions:
        measure = Measure()
        measure.name = kpi.kpi_name
        measure.aggregation_function = determine_aggregation_function(kpi.kpi_type)
        measure.data_type = map_kpi_type_to_measure_type(kpi.kpi_type)
        measure.format_string = f"#,##0.00 {kpi.measurement_unit}"
        cube.measures.append(measure)

        # 添加完成率度量
        completion_measure = Measure()
        completion_measure.name = f"{kpi.kpi_name}_Completion_Rate"
        completion_measure.aggregation_function = "AVG"
        completion_measure.data_type = "Percentage"
        completion_measure.format_string = "#,##0.00%"
        cube.measures.append(completion_measure)

    # 转换KPI值为事实数据
    for value in kpi_data.kpi_monitoring.kpi_values:
        kpi = find_kpi_definition(kpi_data, value.kpi_id)

        fact = Fact()
        fact.dimensions = {
            "Time": {
                "Year": value.measurement_date.year,
                "Quarter": get_quarter(value.measurement_date),
                "Month": value.measurement_date.month,
                "Day": value.measurement_date.day
            },
            "KPI_Category": {
                "Category": kpi.kpi_category,
                "Type": kpi.kpi_type,
                "Owner": kpi.owner
            },
            "Organization": {
                "Department": extract_department(kpi.owner)
            }
        }
        fact.measures = {
            kpi.kpi_name: value.value,
            f"{kpi.kpi_name}_Completion_Rate": value.completion_rate or 0
        }
        cube.facts.append(fact)

    return cube
```

---

## 4. 案例3：KPI预警系统

### 4.1 场景描述

**应用场景**：
构建KPI预警系统，当KPI值超过阈值时触发预警。

**业务需求**：

- 支持预警规则配置
- 支持多级预警
- 支持预警通知

### 4.2 实现代码

```python
def check_kpi_alerts(kpi_data: KPIManagementSchema, kpi_id: str, current_value: Decimal) -> List[KPIAlert]:
    """检查KPI预警"""
    alerts = []

    # 获取KPI定义
    kpi = find_kpi_definition(kpi_data, kpi_id)

    # 获取KPI目标
    target = find_active_target(kpi_data, kpi_id)
    if not target:
        return alerts

    # 获取KPI阈值
    thresholds = find_kpi_thresholds(kpi_data, kpi_id)

    # 计算完成率
    completion_rate = (current_value / target.target_value) * 100 if target.target_value > 0 else 0

    # 检查预警规则
    for alert_rule in kpi_data.kpi_monitoring.kpi_alerts:
        if alert_rule.kpi_id == kpi_id and alert_rule.is_enabled:
            should_alert = False
            alert_level = "Info"

            if alert_rule.alert_condition == "Below":
                if current_value < alert_rule.alert_threshold:
                    should_alert = True
                    alert_level = alert_rule.alert_level
            elif alert_rule.alert_condition == "Above":
                if current_value > alert_rule.alert_threshold:
                    should_alert = True
                    alert_level = alert_rule.alert_level
            elif alert_rule.alert_condition == "Change_Rate":
                # 获取历史值
                historical_value = get_historical_value(kpi_data, kpi_id, days=30)
                if historical_value:
                    change_rate = abs((current_value - historical_value) / historical_value) * 100
                    if change_rate > alert_rule.alert_threshold:
                        should_alert = True
                        alert_level = alert_rule.alert_level

            if should_alert:
                alert = KPIAlert()
                alert.alert_id = f"ALERT-{kpi_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                alert.kpi_id = kpi_id
                alert.alert_level = alert_level
                alert.current_value = current_value
                alert.target_value = target.target_value
                alert.completion_rate = completion_rate
                alert.alert_message = generate_alert_message(kpi, alert_rule, current_value, target.target_value)
                alert.alert_time = datetime.now()

                # 发送通知
                send_alert_notifications(alert, alert_rule.notification_channels)

                alerts.append(alert)

    return alerts
```

---

## 5. 案例4：KPI根因分析系统

### 5.1 场景描述

**应用场景**：
构建KPI根因分析系统，识别KPI异常的根本原因。

**业务需求**：

- 支持根因识别
- 支持根因验证
- 支持解决方案生成

### 5.2 实现代码

```python
def analyze_kpi_root_cause(kpi_data: KPIManagementSchema, kpi_id: str, analysis_period: DateRange) -> KPIRootCause:
    """分析KPI根因"""
    root_cause = KPIRootCause()
    root_cause.root_cause_id = f"RCA-{kpi_id}-{datetime.now().strftime('%Y%m%d')}"
    root_cause.kpi_id = kpi_id
    root_cause.root_cause_analysis_date = datetime.now().date()

    # 获取KPI值
    kpi_values = get_kpi_values_in_period(kpi_data, kpi_id, analysis_period)

    # 识别异常
    anomalies = detect_anomalies(kpi_values)

    # 分析根因
    identified_causes = []

    # 1. 数据质量检查
    data_quality_issues = check_data_quality(kpi_data, kpi_id)
    if data_quality_issues:
        cause = RootCause()
        cause.cause_id = "CAUSE-DATA-QUALITY"
        cause.cause_description = "数据质量问题"
        cause.cause_category = "Technology"
        cause.cause_impact = "High"
        cause.cause_details = data_quality_issues
        identified_causes.append(cause)

    # 2. 流程问题检查
    process_issues = check_process_issues(kpi_data, kpi_id, analysis_period)
    if process_issues:
        cause = RootCause()
        cause.cause_id = "CAUSE-PROCESS"
        cause.cause_description = "流程问题"
        cause.cause_category = "Process"
        cause.cause_impact = "Medium"
        cause.cause_details = process_issues
        identified_causes.append(cause)

    # 3. 外部因素检查
    external_factors = check_external_factors(kpi_data, kpi_id, analysis_period)
    if external_factors:
        cause = RootCause()
        cause.cause_id = "CAUSE-EXTERNAL"
        cause.cause_description = "外部因素影响"
        cause.cause_category = "External"
        cause.cause_impact = "Medium"
        cause.cause_details = external_factors
        identified_causes.append(cause)

    root_cause.identified_causes = identified_causes

    # 生成解决方案
    solutions = []
    for cause in identified_causes:
        solution = Solution()
        solution.solution_id = f"SOL-{cause.cause_id}"
        solution.solution_description = generate_solution_description(cause)
        solution.solution_owner = determine_solution_owner(cause)
        solution.solution_status = "Proposed"
        solutions.append(solution)

    root_cause.solutions = solutions

    return root_cause
```

---

## 6. 案例5：KPI数据存储与分析系统

### 6.1 场景描述

**应用场景**：
KPI数据存储与分析系统，支持KPI元数据存储、查询、分析。

**业务需求**：

- 支持KPI元数据存储
- 支持KPI数据查询和分析
- 支持KPI报告生成

### 6.2 实现代码

```python
def store_kpi_data(kpi_data: KPIManagementSchema, conn):
    """存储KPI数据到PostgreSQL"""
    cursor = conn.cursor()

    # 存储KPI定义
    for kpi in kpi_data.kpi_definition.kpi_definitions:
        cursor.execute("""
            INSERT INTO kpi_definitions
            (kpi_id, kpi_name, kpi_description, kpi_type, kpi_category, calculation_formula,
             data_source, measurement_unit, calculation_frequency, owner, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (kpi_id) DO UPDATE SET
            kpi_name = EXCLUDED.kpi_name,
            kpi_description = EXCLUDED.kpi_description,
            calculation_formula = EXCLUDED.calculation_formula,
            updated_at = CURRENT_TIMESTAMP
        """, (kpi.kpi_id, kpi.kpi_name, kpi.kpi_description, kpi.kpi_type,
              kpi.kpi_category, kpi.calculation_formula, kpi.data_source,
              kpi.measurement_unit, kpi.calculation_frequency, kpi.owner, kpi.is_active))

    # 存储KPI目标
    for target in kpi_data.kpi_definition.kpi_targets:
        cursor.execute("""
            INSERT INTO kpi_targets
            (target_id, kpi_id, target_type, target_value, target_start_date, target_end_date,
             target_owner, target_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (target_id) DO UPDATE SET
            target_value = EXCLUDED.target_value,
            target_status = EXCLUDED.target_status
        """, (target.target_id, target.kpi_id, target.target_type, target.target_value,
              target.target_period.start_date, target.target_period.end_date,
              target.target_owner, target.target_status))

    # 存储KPI值
    for value in kpi_data.kpi_monitoring.kpi_values:
        cursor.execute("""
            INSERT INTO kpi_values
            (value_id, kpi_id, value, measurement_date, measurement_time, data_source,
             is_actual, completion_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (value_id) DO UPDATE SET
            value = EXCLUDED.value,
            completion_rate = EXCLUDED.completion_rate
        """, (value.value_id, value.kpi_id, value.value, value.measurement_date,
              value.measurement_time, value.data_source, value.is_actual, value.completion_rate))

    # 存储KPI趋势
    for trend in kpi_data.kpi_monitoring.kpi_trends:
        cursor.execute("""
            INSERT INTO kpi_trends
            (trend_id, kpi_id, trend_start_date, trend_end_date, trend_direction,
             trend_magnitude, trend_confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (trend_id) DO UPDATE SET
            trend_direction = EXCLUDED.trend_direction,
            trend_magnitude = EXCLUDED.trend_magnitude
        """, (trend.trend_id, trend.kpi_id, trend.trend_period.start_date,
              trend.trend_period.end_date, trend.trend_direction,
              trend.trend_magnitude, trend.trend_confidence))

    conn.commit()

def generate_kpi_report(conn, report_period: DateRange):
    """生成KPI报表"""
    cursor = conn.cursor()

    # 查询KPI完成情况汇总
    cursor.execute("""
        SELECT
            kd.kpi_name,
            kd.kpi_type,
            kt.target_value,
            AVG(kv.value) as avg_value,
            AVG(kv.completion_rate) as avg_completion_rate,
            COUNT(kv.value_id) as measurement_count,
            SUM(CASE WHEN kv.completion_rate >= 100 THEN 1 ELSE 0 END) as achieved_count
        FROM kpi_definitions kd
        LEFT JOIN kpi_targets kt ON kd.kpi_id = kt.kpi_id AND kt.target_status = 'Active'
        LEFT JOIN kpi_values kv ON kd.kpi_id = kv.kpi_id
        WHERE kv.measurement_date BETWEEN %s AND %s
        GROUP BY kd.kpi_id, kd.kpi_name, kd.kpi_type, kt.target_value
        ORDER BY avg_completion_rate DESC
    """, (report_period.start_date, report_period.end_date))

    kpi_summary = cursor.fetchall()

    # 查询KPI趋势分析
    cursor.execute("""
        SELECT
            kd.kpi_name,
            kt.trend_direction,
            kt.trend_magnitude,
            kt.trend_confidence,
            kt.trend_end_date
        FROM kpi_definitions kd
        JOIN kpi_trends kt ON kd.kpi_id = kt.kpi_id
        WHERE kt.trend_end_date >= %s
        ORDER BY kt.trend_end_date DESC, kd.kpi_name
    """, (report_period.start_date,))

    kpi_trends = cursor.fetchall()

    return {
        "kpi_summary": kpi_summary,
        "kpi_trends": kpi_trends,
        "report_period": report_period
    }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
