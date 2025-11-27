# KPI管理Schema实践案例

## 📑 目录

- [KPI管理Schema实践案例](#kpi管理schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：销售KPI管理](#2-案例1销售kpi管理)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：KPI到OLAP Cube转换](#3-案例2kpi到olap-cube转换)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 实现代码](#32-实现代码)
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

本文档提供KPI管理Schema在实际应用中的实践案例。

---

## 2. 案例1：销售KPI管理

### 2.1 场景描述

**应用场景**：
构建销售KPI管理系统，包括销售KPI定义、监控、分析和报告。

**业务需求**：

- 支持销售KPI定义
- 支持销售KPI实时监控
- 支持销售KPI分析和报告

### 2.2 Schema定义

**销售KPI管理Schema**：

```dsl
schema SalesKPIManagement {
  kpi_definition: KPIDef {
    kpi_id: String @value("KPI-SALES-001")
    kpi_name: String @value("月度销售额")
    kpi_type: Enum @value("Financial")
    kpi_category: String @value("销售")
    calculation_formula: String @value("SUM(sales_amount)")
    data_source: String @value("sales_transactions")
    measurement_unit: String @value("元")
    calculation_frequency: Enum @value("Monthly")
    owner: String @value("销售部")
  }

  kpi_target: KPITarget {
    target_id: String @value("TGT-SALES-001")
    kpi_id: String @value("KPI-SALES-001")
    target_type: Enum @value("Absolute")
    target_value: Decimal @value(1000000)
    target_period: DateRange {
      start_date: Date @value("2025-01-01")
      end_date: Date @value("2025-12-31")
    }
    target_owner: String @value("销售部")
  }

  kpi_value: KPIValue {
    value_id: String @value("VAL-SALES-001")
    kpi_id: String @value("KPI-SALES-001")
    value: Decimal @value(950000)
    measurement_date: Date @value("2025-01-31")
    completion_rate: Decimal @value(95.0)
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
