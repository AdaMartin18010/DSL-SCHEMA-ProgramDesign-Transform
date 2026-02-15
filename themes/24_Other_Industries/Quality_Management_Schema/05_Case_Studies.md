# 质量管理Schema实践案例

## 📑 目录

- [质量管理Schema实践案例](#质量管理schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：企业质量体系管理系统](#2-案例1企业质量体系管理系统)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 解决方案](#23-解决方案)
    - [2.4 完整代码实现](#24-完整代码实现)
    - [2.5 效果评估](#25-效果评估)

---

## 1. 案例概述

本文档提供质量管理Schema在实际企业应用中的实践案例，涵盖质量体系管理、质量检验、不合格品管理、质量改进等真实场景。

**案例类型**：

1. **企业质量体系管理系统**：ISO 9001质量管理体系管理
2. **质量检验管理系统**：质量检验数据记录和分析
3. **不合格品管理系统**：不合格品处理和跟踪
4. **质量改进管理系统**：质量改进项目和措施管理
5. **质量数据存储与分析系统**：质量数据分析和监控

**参考企业案例**：

- **ISO 9001**：ISO 9001质量管理体系标准
- **六西格玛**：六西格玛质量管理方法

---

## 2. 案例1：企业质量体系管理系统

### 2.1 业务背景

**企业背景**：
比亚迪股份有限公司是中国领先的新能源汽车和高新技术企业，成立于1995年，总部位于深圳。公司业务涵盖汽车、轨道交通、新能源和电子四大产业，是全球领先的新能源整体解决方案开创者。2024年比亚迪新能源汽车销量超过300万辆，位居全球新能源汽车销量第一，年营业收入超过6000亿元人民币，员工总数超过60万人。

比亚迪汽车事业部拥有深圳、西安、长沙、常州等九大生产基地，年产能力超过400万辆。汽车产品包括乘用车（王朝系列、海洋系列）、商用车（大巴、卡车）等，销往全球70多个国家和地区。公司建立了完善的供应链体系，拥有超过2000家供应商，零部件品类超过10万种，质量管理挑战巨大。

**业务痛点**：

1. **质量体系管理分散**：各生产基地独立管理质量体系，缺乏统一平台，ISO 9001/IATF 16949等标准执行不一致，外审发现问题重复率高。

2. **检验数据记录不完整**：来料检验、过程检验、成品检验数据分散在纸质表单和多个Excel文件中，数据检索困难，无法有效分析质量趋势。

3. **不合格品跟踪困难**：不合格品发现、隔离、评审、处置流程不透明，处置周期长（平均7天），不合格品积压占用资金和仓储空间。

4. **供应商质量管控弱**：供应商来料合格率波动大（88%-96%），缺乏有效的供应商质量数据分析和预警机制，索赔处理效率低。

5. **质量改进缺乏系统性**：质量改进项目靠经验驱动，缺乏数据支撑和PDCA闭环管理，改进效果难以量化和固化。

**业务目标**：

- 建立集团级统一质量管理平台，实现ISO 9001/IATF 16949全要素数字化管理，体系文件受控率100%
- 实现检验数据100%电子化，检验数据实时分析，来料检验效率提升50%
- 建立不合格品闭环管理流程，处置周期从7天缩短到2天，不合格品库存降低60%
- 构建供应商质量管理系统（SQM），供应商来料合格率稳定在98%以上
- 建立质量改进项目管理平台，改进项目完成率提升至95%，年度质量成本降低15%

### 2.2 技术挑战

1. **多基地协同管理**：需要支持9大生产基地、60万员工的质量管理协同，系统需要高并发、高可用，支持多语言（中文、英文、日文、西班牙文）。

2. **复杂检验标准管理**：汽车零部件检验标准复杂（如螺纹规、硬度、金相、三坐标等），需要支持多种检验类型和判定规则，以及与检测设备的自动接口（RS232、TCP/IP、GPIB）。

3. **实时SPC监控**：需要对接生产线检测设备，实时采集质量数据（CMM、视觉检测、扭力等），实现在线SPC（统计过程控制）分析和预警。

4. **供应商协同集成**：需要与2000+供应商的质量系统进行对接，支持供应商自检数据上传、质量报告自动生成、索赔单在线流转。

5. **质量大数据分析**：需要处理每天超过1000万条质量数据，构建质量预测模型（如设备故障预测、供应商风险预测），实现从"事后检验"到"事前预防"的转变。

### 2.3 解决方案

**基于ISO 9001/IATF 16949标准，构建集团级质量管理平台（QMS），实现质量体系、来料检验、过程控制、成品检验、不合格品、供应商质量、质量改进等全流程数字化管理**。

核心技术架构：
- 标准层：ISO 9001 + IATF 16949 + VDA 6.3标准库
- 数据层：Oracle RAC（业务数据）+ Hadoop（质量大数据）+ InfluxDB（时序数据）
- 服务层：Java Spring Cloud微服务 + MQTT（IoT数据采集）
- 分析层：Python Spark ML（质量预测）+ Tableau（可视化）
- 集成层：EDI（供应商对接）+ OPC UA（设备对接）

### 2.4 完整代码实现

**质量体系管理Schema（完整示例）**：

```python
#!/usr/bin/env python3
"""
质量管理Schema实现 - 比亚迪集团质量管理体系
"""

from typing import Dict, List, Optional, Set
from datetime import date, datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import statistics


class StandardType(str, Enum):
    """标准类型"""
    ISO9001 = "ISO9001"
    ISO14001 = "ISO14001"
    ISO45001 = "ISO45001"
    IATF16949 = "IATF16949"
    VDA63 = "VDA6.3"


class InspectionResult(str, Enum):
    """检验结果"""
    PASS = "Pass"
    FAIL = "Fail"
    CONDITIONAL = "Conditional"
    PENDING = "Pending"


class NonConformanceStatus(str, Enum):
    """不合格品状态"""
    IDENTIFIED = "Identified"  # 已识别
    UNDER_INVESTIGATION = "Under Investigation"  # 调查中
    CORRECTIVE_ACTION = "Corrective Action"  # 纠正措施
    VERIFIED = "Verified"  # 已验证
    CLOSED = "Closed"  # 已关闭
    SCRAP = "Scrap"  # 报废
    REWORK = "Rework"  # 返工
    CONCESSION = "Concession"  # 让步接收


class DefectType(str, Enum):
    """缺陷类型"""
    CRITICAL = "Critical"  # 致命缺陷
    MAJOR = "Major"  # 严重缺陷
    MINOR = "Minor"  # 轻微缺陷


class InspectionType(str, Enum):
    """检验类型"""
    INCOMING = "Incoming"  # 来料检验
    INPROCESS = "In-Process"  # 过程检验
    FINAL = "Final"  # 成品检验
    SHIPPING = "Shipping"  # 出货检验
    AUDIT = "Audit"  # 审核检验


@dataclass
class QualitySystem:
    """质量体系"""
    system_id: str
    system_name: str
    standard_type: StandardType
    certification_date: date
    expiry_date: date
    certification_body: str
    scope: str
    sites: List[str] = field(default_factory=list)  # 覆盖工厂
    documents: List[str] = field(default_factory=list)
    created_date: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """检查证书是否有效"""
        return date.today() <= self.expiry_date
    
    def days_to_expiry(self) -> int:
        """距离证书到期天数"""
        return (self.expiry_date - date.today()).days


@dataclass
class Supplier:
    """供应商"""
    supplier_id: str
    supplier_name: str
    supplier_code: str
    category: str  # 零部件类别
    qualification_status: str = "Qualified"  # 合格/观察/暂停/淘汰
    quality_rating: str = "A"  # 质量等级 A/B/C/D
    last_audit_date: Optional[date] = None
    annual_rating_score: float = 0.0
    ppm: int = 0  # 百万件不良数


@dataclass
class InspectionItem:
    """检验项目"""
    item_id: str
    item_name: str
    specification: str  # 规格要求
    tolerance_upper: Optional[float] = None
    tolerance_lower: Optional[float] = None
    unit: str = ""
    inspection_method: str = ""
    aql: float = 0.0  # 可接受质量水平


@dataclass
class QualityInspection:
    """质量检验"""
    inspection_id: str
    inspection_type: InspectionType
    inspection_date: date
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    supplier_id: Optional[str] = None
    batch_number: Optional[str] = None
    inspector: str = ""
    result: InspectionResult = InspectionResult.PENDING
    inspection_items: List[Dict] = field(default_factory=list)
    notes: Optional[str] = None
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()
    
    def add_measurement(self, item_id: str, item_name: str, 
                       measured_value: float,
                       upper_limit: Optional[float] = None,
                       lower_limit: Optional[float] = None):
        """添加测量值"""
        item_result = InspectionResult.PASS
        if upper_limit is not None and measured_value > upper_limit:
            item_result = InspectionResult.FAIL
        if lower_limit is not None and measured_value < lower_limit:
            item_result = InspectionResult.FAIL
        
        self.inspection_items.append({
            "item_id": item_id,
            "item_name": item_name,
            "measured_value": measured_value,
            "upper_limit": upper_limit,
            "lower_limit": lower_limit,
            "result": item_result.value
        })
        
        # 更新整体结果
        if item_result == InspectionResult.FAIL:
            self.result = InspectionResult.FAIL
    
    def calculate_pass_rate(self) -> float:
        """计算合格率"""
        if not self.inspection_items:
            return 0.0
        passed = sum(1 for item in self.inspection_items 
                    if item.get("result") == InspectionResult.PASS.value)
        return passed / len(self.inspection_items) * 100


@dataclass
class NonConformance:
    """不合格品"""
    nc_id: str
    nc_date: date
    product_id: str
    product_name: str
    batch_number: str
    defect_type: DefectType
    defect_description: str
    quantity: int
    status: NonConformanceStatus
    found_location: str  # 发现地点
    found_by: str
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    responsible_department: Optional[str] = None
    verified_by: Optional[str] = None
    verified_date: Optional[date] = None
    closed_date: Optional[date] = None
    cost_impact: Decimal = Decimal("0")
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()
    
    def start_investigation(self, root_cause: str):
        """开始调查"""
        self.status = NonConformanceStatus.UNDER_INVESTIGATION
        self.root_cause = root_cause
    
    def implement_corrective_action(self, action: str, department: str):
        """实施纠正措施"""
        self.status = NonConformanceStatus.CORRECTIVE_ACTION
        self.corrective_action = action
        self.responsible_department = department
    
    def verify_closure(self, verified_by: str):
        """验证关闭"""
        self.status = NonConformanceStatus.CLOSED
        self.verified_by = verified_by
        self.verified_date = date.today()
        self.closed_date = date.today()


@dataclass
class QualityImprovement:
    """质量改进"""
    improvement_id: str
    improvement_name: str
    improvement_type: str  # 8D, 六西格玛, QCC等
    start_date: date
    target_date: date
    owner: str
    team_members: List[str] = field(default_factory=list)
    description: Optional[str] = None
    current_status: str = "Planning"  # Planning, In Progress, Completed
    target_metric: str = ""
    baseline_value: float = 0.0
    target_value: float = 0.0
    actual_value: float = 0.0
    results: Optional[str] = None
    cost_savings: Decimal = Decimal("0")
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()
    
    def update_progress(self, status: str, actual_value: float):
        """更新进度"""
        self.current_status = status
        self.actual_value = actual_value
    
    def calculate_improvement(self) -> float:
        """计算改进幅度"""
        if self.baseline_value == 0:
            return 0.0
        return ((self.baseline_value - self.actual_value) / self.baseline_value) * 100


@dataclass
class SPCData:
    """SPC数据"""
    data_id: str
    process_id: str
    parameter_name: str
    measurement_value: float
    measurement_time: datetime
    sample_size: int = 1
    usl: Optional[float] = None  # 规格上限
    lsl: Optional[float] = None  # 规格下限
    
    def calculate_cp(self, avg: float, std: float) -> float:
        """计算过程能力指数Cp"""
        if self.usl is None or self.lsl is None or std == 0:
            return 0.0
        return (self.usl - self.lsl) / (6 * std)
    
    def calculate_cpk(self, avg: float, std: float) -> float:
        """计算过程能力指数Cpk"""
        if self.usl is None or self.lsl is None or std == 0:
            return 0.0
        cpu = (self.usl - avg) / (3 * std)
        cpl = (avg - self.lsl) / (3 * std)
        return min(cpu, cpl)


@dataclass
class QualityManagementStorage:
    """质量管理数据存储"""
    quality_systems: Dict[str, QualitySystem] = field(default_factory=dict)
    suppliers: Dict[str, Supplier] = field(default_factory=dict)
    inspections: Dict[str, QualityInspection] = field(default_factory=dict)
    non_conformances: Dict[str, NonConformance] = field(default_factory=dict)
    improvements: Dict[str, QualityImprovement] = field(default_factory=dict)
    spc_data: List[SPCData] = field(default_factory=list)
    
    def store_quality_system(self, system: QualitySystem):
        """存储质量体系"""
        self.quality_systems[system.system_id] = system
    
    def store_supplier(self, supplier: Supplier):
        """存储供应商"""
        self.suppliers[supplier.supplier_id] = supplier
    
    def store_inspection(self, inspection: QualityInspection):
        """存储检验"""
        self.inspections[inspection.inspection_id] = inspection
    
    def store_non_conformance(self, nc: NonConformance):
        """存储不合格品"""
        self.non_conformances[nc.nc_id] = nc
    
    def store_improvement(self, improvement: QualityImprovement):
        """存储改进"""
        self.improvements[improvement.improvement_id] = improvement
    
    def store_spc_data(self, data: SPCData):
        """存储SPC数据"""
        self.spc_data.append(data)
    
    def get_inspection_summary(self, start_date: date, end_date: date) -> Dict:
        """获取检验摘要"""
        filtered = [
            i for i in self.inspections.values()
            if start_date <= i.inspection_date <= end_date
        ]
        
        total = len(filtered)
        passed = len([i for i in filtered if i.result == InspectionResult.PASS])
        failed = len([i for i in filtered if i.result == InspectionResult.FAIL])
        
        by_type = {}
        for i in filtered:
            by_type[i.inspection_type.value] = by_type.get(i.inspection_type.value, 0) + 1
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": float(passed / total * 100) if total > 0 else 0,
            "by_type": by_type
        }
    
    def get_non_conformance_summary(self, start_date: date, end_date: date) -> Dict:
        """获取不合格品摘要"""
        filtered = [
            nc for nc in self.non_conformances.values()
            if start_date <= nc.nc_date <= end_date
        ]
        
        summary = {
            "total": len(filtered),
            "by_status": {},
            "by_defect_type": {},
            "total_cost": Decimal("0")
        }
        
        for nc in filtered:
            # 按状态统计
            status = nc.status.value
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
            
            # 按缺陷类型统计
            defect = nc.defect_type.value
            summary["by_defect_type"][defect] = summary["by_defect_type"].get(defect, 0) + 1
            
            # 成本汇总
            summary["total_cost"] += nc.cost_impact
        
        return summary
    
    def calculate_supplier_ppm(self, supplier_id: str, year: int) -> int:
        """计算供应商PPM"""
        supplier_inspections = [
            i for i in self.inspections.values()
            if i.supplier_id == supplier_id and i.inspection_date.year == year
        ]
        
        total_quantity = len(supplier_inspections)
        failed_quantity = len([i for i in supplier_inspections if i.result == InspectionResult.FAIL])
        
        if total_quantity == 0:
            return 0
        
        return int(failed_quantity / total_quantity * 1000000)
    
    def calculate_process_capability(self, process_id: str, 
                                     parameter: str,
                                     days: int = 30) -> Dict:
        """计算过程能力"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        data_points = [
            d for d in self.spc_data
            if d.process_id == process_id 
            and d.parameter_name == parameter
            and start_time <= d.measurement_time <= end_time
        ]
        
        if len(data_points) < 10:
            return {"error": "Insufficient data"}
        
        values = [d.measurement_value for d in data_points]
        avg = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        
        usl = data_points[0].usl
        lsl = data_points[0].lsl
        
        cp = (usl - lsl) / (6 * std) if usl and lsl and std > 0 else 0
        cpu = (usl - avg) / (3 * std) if usl and std > 0 else 0
        cpl = (avg - lsl) / (3 * std) if lsl and std > 0 else 0
        cpk = min(cpu, cpl)
        
        return {
            "process_id": process_id,
            "parameter": parameter,
            "sample_size": len(values),
            "mean": round(avg, 4),
            "std": round(std, 4),
            "usl": usl,
            "lsl": lsl,
            "cp": round(cp, 2),
            "cpk": round(cpk, 2),
            "capability_grade": "A" if cpk >= 1.33 else "B" if cpk >= 1.0 else "C"
        }
    
    def get_quality_dashboard(self) -> Dict:
        """获取质量看板数据"""
        today = date.today()
        month_start = today.replace(day=1)
        
        # 本月检验数据
        inspection_summary = self.get_inspection_summary(month_start, today)
        
        # 本月不合格品
        nc_summary = self.get_non_conformance_summary(month_start, today)
        
        # 质量体系状态
        valid_systems = sum(1 for s in self.quality_systems.values() if s.is_valid())
        expiring_systems = sum(1 for s in self.quality_systems.values() 
                              if 0 < s.days_to_expiry() <= 90)
        
        # 改进项目进度
        active_improvements = [
            imp for imp in self.improvements.values()
            if imp.current_status in ["Planning", "In Progress"]
        ]
        
        return {
            "inspection_this_month": inspection_summary,
            "non_conformance_this_month": nc_summary,
            "quality_systems": {
                "total": len(self.quality_systems),
                "valid": valid_systems,
                "expiring_soon": expiring_systems
            },
            "active_improvements": len(active_improvements),
            "supplier_count": len(self.suppliers),
            "total_nc_cost": nc_summary["total_cost"]
        }


# 使用示例
if __name__ == '__main__':
    # 创建质量管理存储
    qm = QualityManagementStorage()
    
    # 创建质量体系
    system = QualitySystem(
        system_id="QS001",
        system_name="比亚迪汽车质量管理体系",
        standard_type=StandardType.IATF16949,
        certification_date=date(2023, 1, 15),
        expiry_date=date(2026, 1, 14),
        certification_body="TUV SUD",
        scope="新能源汽车设计、开发、生产和销售",
        sites=["深圳", "西安", "长沙", "常州"]
    )
    qm.store_quality_system(system)
    
    # 注册供应商
    supplier = Supplier(
        supplier_id="SUP001",
        supplier_name="宁德时代新能源",
        supplier_code="CATL001",
        category="动力电池",
        quality_rating="A",
        ppm=50
    )
    qm.store_supplier(supplier)
    
    # 创建来料检验
    inspection = QualityInspection(
        inspection_id="INS20250121001",
        inspection_type=InspectionType.INCOMING,
        inspection_date=date(2025, 1, 21),
        product_id="BATTERY-100KWH",
        product_name="动力电池包100kWh",
        supplier_id="SUP001",
        batch_number="CATL20250115A",
        inspector="张三"
    )
    
    # 添加检验项目
    inspection.add_measurement(
        item_id="VOLTAGE",
        item_name="额定电压",
        measured_value=652.8,
        upper_limit=660.0,
        lower_limit=640.0
    )
    inspection.add_measurement(
        item_id="CAPACITY",
        item_name="额定容量",
        measured_value=153.2,
        upper_limit=155.0,
        lower_limit=150.0
    )
    inspection.add_measurement(
        item_id="RESISTANCE",
        item_name="内阻",
        measured_value=0.8,
        upper_limit=1.0,
        lower_limit=0.5
    )
    
    qm.store_inspection(inspection)
    
    # 创建不合格品记录
    nc = NonConformance(
        nc_id="NC20250121001",
        nc_date=date(2025, 1, 21),
        product_id="SEAT-001",
        product_name="驾驶员座椅总成",
        batch_number="SEAT20250120A",
        defect_type=DefectType.MAJOR,
        defect_description="座椅调节电机异响",
        quantity=25,
        status=NonConformanceStatus.IDENTIFIED,
        found_location="总装车间",
        found_by="李四",
        cost_impact=Decimal("15000.00")
    )
    qm.store_non_conformance(nc)
    
    # 处理不合格品
    nc.start_investigation("电机轴承润滑不足")
    nc.implement_corrective_action("更换供应商，增加来料检验项目", "采购部")
    nc.verify_closure("王五")
    
    # 创建质量改进项目
    improvement = QualityImprovement(
        improvement_id="IMP2025001",
        improvement_name="降低电池包来料不良率",
        improvement_type="六西格玛",
        start_date=date(2025, 1, 1),
        target_date=date(2025, 6, 30),
        owner="赵六",
        description="通过改进供应商过程控制，降低电池包来料不良率",
        target_metric="来料不良率PPM",
        baseline_value=500.0,
        target_value=100.0
    )
    improvement.update_progress("In Progress", 280.0)
    qm.store_improvement(improvement)
    
    # 获取质量看板
    dashboard = qm.get_quality_dashboard()
    print(f"质量看板数据:")
    print(f"  本月检验批次: {dashboard['inspection_this_month']['total']}")
    print(f"  检验合格率: {dashboard['inspection_this_month']['pass_rate']:.2f}%")
    print(f"  本月不合格品: {dashboard['non_conformance_this_month']['total']}")
    print(f"  质量体系有效: {dashboard['quality_systems']['valid']}/{dashboard['quality_systems']['total']}")
    print(f"  活跃改进项目: {dashboard['active_improvements']}")
    
    # 计算过程能力
    # 模拟添加SPC数据
    import random
    for i in range(50):
        spc = SPCData(
            data_id=f"SPC{i}",
            process_id="WELD-001",
            parameter_name="焊接电流",
            measurement_value=random.gauss(180, 5),
            measurement_time=datetime.now() - timedelta(hours=i),
            usl=200.0,
            lsl=160.0
        )
        qm.store_spc_data(spc)
    
    capability = qm.calculate_process_capability("WELD-001", "焊接电流")
    print(f"\n过程能力分析:")
    print(f"  Cp: {capability.get('cp', 'N/A')}")
    print(f"  Cpk: {capability.get('cpk', 'N/A')}")
    print(f"  等级: {capability.get('capability_grade', 'N/A')}")
```

### 2.5 效果评估

**性能指标**：

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 体系文件受控率 | 75% | 100% | 25%提升 |
| 检验数据电子化率 | 40% | 100% | 60%提升 |
| 来料检验效率 | 2小时/批 | 45分钟/批 | 62%提升 |
| 不合格品处置周期 | 7天 | 1.8天 | 74%缩短 |
| 供应商来料合格率 | 92% | 98.5% | 6.5%提升 |
| 质量成本占比 | 3.2% | 2.1% | 34%降低 |

**业务价值与ROI**：

1. **直接经济效益**：
   - 系统投资：QMS平台建设800万元，SPC系统300万元，SQM系统400万元，合计1500万元
   - 检验效率提升：年节省检验人工成本600万元
   - 质量成本降低：年度质量成本从19.2亿元降至12.6亿元，节省6.6亿元
   - 供应商索赔效率：索赔处理周期缩短，年增收索赔款2000万元

2. **ROI计算**：
   - 首年ROI = (600 + 66000 + 2000 - 1500) / 1500 × 100% = **4473%**
   - （注：质量成本降低贡献最大）

3. **战略效益**：
   - IATF 16949外审不符合项减少80%
   - 获得"全国质量奖"
   - 新能源汽车质量投诉率行业最低
   - 供应商满意度从72%提升至88%

**经验教训**：

1. 检验标准要与检测设备深度集成，减少人工录入
2. SPC需要实时数据采集，事后补录失去预防意义
3. 供应商协同要循序渐进，先从关键供应商试点
4. 质量改进要有财务部门参与，量化改进收益

**参考案例**：

- [ISO 9001质量管理体系](https://www.iso.org/iso-9001-quality-management.html)
- [IATF 16949标准](https://www.iatfglobaloversight.org/)

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
