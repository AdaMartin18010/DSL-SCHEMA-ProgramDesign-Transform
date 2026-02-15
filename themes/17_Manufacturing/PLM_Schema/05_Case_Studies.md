# PLM Schema实践案例

## 📑 目录

- [PLM Schema实践案例](#plm-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：汽车制造企业PLM数字化项目](#2-案例1汽车制造企业plm数字化项目)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 Schema定义](#25-schema定义)
    - [2.6 完整代码实现](#26-完整代码实现)
    - [2.7 效果评估](#27-效果评估)
  - [3. 案例2：电子制造企业研发协同平台](#3-案例2电子制造企业研发协同平台)
    - [3.1-3.6 概要](#31-36-概要)
  - [4. 案例总结](#4-案例总结)

---

## 1. 案例概述

本文档提供PLM Schema在制造行业的实践案例。

---

## 2. 案例1：汽车制造企业PLM数字化项目

### 2.1 业务背景

**企业概况**：某汽车制造企业（以下简称"I汽车"），年产能50万辆，拥有研发人员3000人，年研发投入超过30亿元。

### 2.2 业务痛点

1. **数据孤岛严重**：CAD、CAE、BOM数据分散，工程师每天花费2小时查找数据
2. **变更管理混乱**：工程变更审批周期长，平均需要15天，变更错误率高
3. **协同效率低**：跨部门协作依赖邮件，设计评审效率低
4. **知识流失严重**：专家经验缺乏沉淀，新员工培养周期长
5. **项目管理粗放**：项目进度不透明，延期率高达40%

### 2.3 业务目标

1. **统一数据管理**：建立单一数据源，数据查找时间减少80%
2. **优化变更流程**：变更周期缩短至3天，变更错误率降低至1%
3. **提升协同效率**：实现并行工程，研发周期缩短20%
4. **沉淀知识资产**：建立知识库，新员工培养周期缩短50%
5. **精细化项目管理**：实现项目进度实时监控，延期率降低至10%

### 2.4 技术挑战

1. **多CAD系统集成**：支持CATIA、UG、Pro/E等多种CAD格式
2. **大数据量处理**：单个车型数据量超过10TB
3. **复杂BOM管理**：支持超级BOM、可配置BOM
4. **全球化协同**：支持多地域、多时区协同研发

### 2.5 Schema定义

```json
{
  "product": {
    "product_id": "PROD-2025-001",
    "product_name": "新能源SUV车型A",
    "product_line": "SUV",
    "platform": "P2",
    "lifecycle_status": "development",
    "bom": {
      "bom_id": "BOM-2025-001",
      "bom_structure": [
        {
          "level": 1,
          "part_number": "ASSY-001",
          "part_name": "车身总成",
          "quantity": 1,
          "children": [
            {"part_number": "PRT-001", "part_name": "前地板", "quantity": 1}
          ]
        }
      ]
    }
  }
}
```

### 2.6 完整代码实现

```python
#!/usr/bin/env python3
"""
PLM产品生命周期管理系统
功能：产品管理、BOM管理、变更管理、项目管理
"""

from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid


class LifecycleStatus(str, Enum):
    """生命周期状态"""
    CONCEPT = "concept"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    PHASE_OUT = "phase_out"
    OBSOLETE = "obsolete"


class ChangeStatus(str, Enum):
    """变更状态"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


@dataclass
class Part:
    """零部件"""
    part_number: str
    part_name: str
    part_type: str  # assembly, component, raw_material
    revision: str = "A"
    description: str = ""
    material: str = ""
    weight: float = 0.0
    unit: str = "EA"
    lifecycle_status: LifecycleStatus = LifecycleStatus.DEVELOPMENT
    owner: str = ""
    create_date: date = field(default_factory=date.today)
    cad_files: List[str] = field(default_factory=list)


@dataclass
class BOMItem:
    """BOM行项"""
    line_no: int
    child_part: Part
    quantity: float
    reference_designators: str = ""  # 位号
    alternative_parts: List[Part] = field(default_factory=list)


@dataclass
class BOM:
    """物料清单"""
    bom_id: str
    parent_part: Part
    revision: str
    bom_type: str  # engineering, manufacturing
    items: List[BOMItem] = field(default_factory=list)
    create_date: date = field(default_factory=date.today)
    effective_date: Optional[date] = None
    obsolete_date: Optional[date] = None
    
    def add_item(self, item: BOMItem):
        """添加BOM行项"""
        self.items.append(item)
    
    def get_total_parts(self) -> int:
        """获取总零部件数"""
        return len(self.items)
    
    def export_to_dict(self) -> Dict:
        """导出为字典"""
        return {
            "bom_id": self.bom_id,
            "parent_part": self.parent_part.part_number,
            "revision": self.revision,
            "items": [
                {
                    "line_no": item.line_no,
                    "part_number": item.child_part.part_number,
                    "part_name": item.child_part.part_name,
                    "quantity": item.quantity
                }
                for item in self.items
            ]
        }


@dataclass
class EngineeringChange:
    """工程变更"""
    ec_number: str
    ec_type: str  # design_change, process_change
    description: str
    reason: str
    status: ChangeStatus
    requestor: str
    create_date: date = field(default_factory=date.today)
    affected_parts: List[Part] = field(default_factory=list)
    approvers: List[str] = field(default_factory=list)
    implementation_date: Optional[date] = None
    
    def submit(self):
        """提交变更"""
        self.status = ChangeStatus.PENDING
    
    def approve(self, approver: str):
        """审批通过"""
        self.status = ChangeStatus.APPROVED
    
    def implement(self):
        """实施变更"""
        self.status = ChangeStatus.IMPLEMENTED
        self.implementation_date = date.today()


@dataclass
class Project:
    """研发项目"""
    project_id: str
    project_name: str
    project_type: str  # new_product, improvement
    start_date: date
    planned_end_date: date
    actual_end_date: Optional[date] = None
    status: str = "planning"  # planning, active, completed, cancelled
    budget: float = 0.0
    actual_cost: float = 0.0
    manager: str = ""
    team_members: List[str] = field(default_factory=list)
    milestones: List[Dict] = field(default_factory=list)
    
    def add_milestone(self, name: str, planned_date: date):
        """添加里程碑"""
        self.milestones.append({
            "name": name,
            "planned_date": planned_date,
            "actual_date": None,
            "status": "pending"
        })
    
    def complete_milestone(self, name: str):
        """完成里程碑"""
        for ms in self.milestones:
            if ms["name"] == name:
                ms["actual_date"] = date.today()
                ms["status"] = "completed"
    
    def get_progress(self) -> float:
        """获取项目进度"""
        if not self.milestones:
            return 0.0
        completed = sum(1 for ms in self.milestones if ms["status"] == "completed")
        return completed / len(self.milestones)


class PLMSystem:
    """PLM系统核心"""
    
    def __init__(self):
        self.parts: Dict[str, Part] = {}
        self.boms: Dict[str, BOM] = {}
        self.changes: Dict[str, EngineeringChange] = {}
        self.projects: Dict[str, Project] = {}
        self.documents: Dict[str, Dict] = {}
    
    def create_part(self, part_number: str, part_name: str, part_type: str,
                   owner: str, **kwargs) -> Part:
        """创建零部件"""
        part = Part(
            part_number=part_number,
            part_name=part_name,
            part_type=part_type,
            owner=owner,
            **kwargs
        )
        self.parts[part_number] = part
        return part
    
    def create_bom(self, parent_part_number: str, revision: str = "A") -> BOM:
        """创建BOM"""
        parent = self.parts.get(parent_part_number)
        if not parent:
            raise ValueError(f"Parent part not found: {parent_part_number}")
        
        bom_id = f"BOM-{parent_part_number}-{revision}"
        bom = BOM(
            bom_id=bom_id,
            parent_part=parent,
            revision=revision,
            bom_type="engineering"
        )
        self.boms[bom_id] = bom
        return bom
    
    def create_change(self, ec_type: str, description: str, reason: str,
                     requestor: str) -> EngineeringChange:
        """创建工程变更"""
        ec_number = f"EC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        change = EngineeringChange(
            ec_number=ec_number,
            ec_type=ec_type,
            description=description,
            reason=reason,
            status=ChangeStatus.DRAFT,
            requestor=requestor
        )
        self.changes[ec_number] = change
        return change
    
    def create_project(self, project_name: str, project_type: str,
                      start_date: date, planned_end_date: date,
                      manager: str, budget: float) -> Project:
        """创建项目"""
        project_id = f"PRJ-{uuid.uuid4().hex[:8].upper()}"
        project = Project(
            project_id=project_id,
            project_name=project_name,
            project_type=project_type,
            start_date=start_date,
            planned_end_date=planned_end_date,
            manager=manager,
            budget=budget
        )
        self.projects[project_id] = project
        return project
    
    def where_used(self, part_number: str) -> List[str]:
        """反查零部件使用情况"""
        used_in = []
        for bom in self.boms.values():
            for item in bom.items:
                if item.child_part.part_number == part_number:
                    used_in.append(bom.parent_part.part_number)
        return used_in
    
    def get_bom_cost(self, bom_id: str) -> float:
        """计算BOM成本"""
        # 简化的成本计算
        bom = self.boms.get(bom_id)
        if not bom:
            return 0.0
        
        total_cost = 0.0
        for item in bom.items:
            # 模拟成本数据
            cost_per_unit = 100.0  # 假设单位成本100元
            total_cost += cost_per_unit * item.quantity
        
        return total_cost
    
    def generate_project_report(self, project_id: str) -> Dict:
        """生成项目报告"""
        project = self.projects.get(project_id)
        if not project:
            return {}
        
        return {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "status": project.status,
            "progress": f"{project.get_progress():.1%}",
            "budget": project.budget,
            "actual_cost": project.actual_cost,
            "variance": project.budget - project.actual_cost,
            "milestones": project.milestones
        }


def main():
    """PLM系统演示"""
    
    print("=" * 60)
    print("PLM产品生命周期管理系统演示")
    print("=" * 60)
    
    plm = PLMSystem()
    
    # 1. 创建零部件
    print("\n[1] 创建零部件")
    part1 = plm.create_part(
        "PRT-001", "前地板", "component",
        "张三", material="高强度钢", weight=15.5
    )
    part2 = plm.create_part(
        "PRT-002", "后地板", "component",
        "李四", material="高强度钢", weight=12.3
    )
    part3 = plm.create_part(
        "ASSY-001", "车身总成", "assembly",
        "王五"
    )
    print(f"已创建 {len(plm.parts)} 个零部件")
    
    # 2. 创建BOM
    print("\n[2] 创建BOM")
    bom = plm.create_bom("ASSY-001", "A")
    bom.add_item(BOMItem(10, part1, 1))
    bom.add_item(BOMItem(20, part2, 1))
    print(f"BOM ID: {bom.bom_id}")
    print(f"子件数量: {bom.get_total_parts()}")
    print(f"BOM结构: {bom.export_to_dict()}")
    
    # 3. 创建工程变更
    print("\n[3] 工程变更管理")
    change = plm.create_change(
        "design_change",
        "优化前地板结构以减轻重量",
        "减重目标",
        "张三"
    )
    change.submit()
    change.approve("赵经理")
    change.implement()
    print(f"变更单号: {change.ec_number}")
    print(f"变更状态: {change.status.value}")
    
    # 4. 创建项目
    print("\n[4] 项目管理")
    project = plm.create_project(
        "新能源SUV车型A研发",
        "new_product",
        date(2025, 1, 1),
        date(2026, 6, 30),
        "刘总监",
        500000000  # 5亿预算
    )
    project.add_milestone("概念设计完成", date(2025, 3, 31))
    project.add_milestone("工程设计完成", date(2025, 9, 30))
    project.add_milestone("样车试制完成", date(2025, 12, 31))
    
    project.complete_milestone("概念设计完成")
    
    report = plm.generate_project_report(project.project_id)
    print(f"项目: {report['project_name']}")
    print(f"进度: {report['progress']}")
    print(f"预算: {report['budget']:,}元")
    
    # 5. 反查
    print("\n[5] 反查查询")
    used_in = plm.where_used("PRT-001")
    print(f"PRT-001 被使用在: {used_in}")


if __name__ == "__main__":
    main()
```

### 2.7 效果评估

| 指标 | 基线值 | 目标值 | 实际值 | 达成率 |
|------|--------|--------|--------|--------|
| 数据查找时间 | 2小时/天 | 减少80% | 减少85% | 106% |
| 变更周期 | 15天 | ≤3天 | 2.5天 | 120% |
| 研发周期 | 48个月 | 缩短20% | 缩短25% | 125% |
| 项目延期率 | 40% | ≤10% | 8% | 125% |

**ROI分析**：
- 项目总投资：8000万元
- 年度总收益：1.5亿元
- **投资回收期：6.4个月**
- **3年ROI：463%**

---

## 3. 案例2：电子制造企业研发协同平台

### 3.1-3.6 概要

**企业概况**：某电子制造企业，年研发投入10亿元，研发人员2000人。

**业务痛点**：
1. 跨地域协同困难
2. 版本管理混乱
3. 设计复用率低

**解决方案**：基于PLM Schema构建协同研发平台，实现全球研发协同。

**效果评估**：
- 协同效率提升60%
- 设计复用率提升至45%
- 研发周期缩短30%

---

## 4. 案例总结

**关键成功因素**：
1. 数据标准化是基础
2. 流程自动化是核心
3. 知识沉淀是长期价值

**创建时间**：2025-01-21  
**最后更新**：2025-02-15
