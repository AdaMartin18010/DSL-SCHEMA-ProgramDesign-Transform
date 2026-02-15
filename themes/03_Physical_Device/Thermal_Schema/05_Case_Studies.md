# 热学Schema实践案例

## 📑 目录

- [热学Schema实践案例](#热学schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：数据中心CPU散热系统热学设计](#2-案例1数据中心cpu散热系统热学设计)
    - [2.1 业务背景](#21-业务背景)
    - [2.2 技术挑战](#22-技术挑战)
    - [2.3 Schema定义](#23-schema定义)
    - [2.4 Python代码实现](#24-python代码实现)
    - [2.5 效果评估](#25-效果评估)
  - [3. 案例2：工业LED灯具热管理](#3-案例2工业led灯具热管理)
    - [3.1 业务背景](#31-业务背景)
    - [3.2 技术挑战](#32-技术挑战)
    - [3.3 Schema定义](#33-schema定义)
    - [3.4 Python代码实现](#34-python代码实现)
    - [3.5 效果评估](#35-效果评估)
  - [4. 案例3：智能建筑热工设计](#4-案例3智能建筑热工设计)
    - [4.1 业务背景](#41-业务背景)
    - [4.2 技术挑战](#42-技术挑战)
    - [4.3 Schema定义](#43-schema定义)
    - [4.4 Python代码实现](#44-python代码实现)
    - [4.5 效果评估](#45-效果评估)
  - [5. 案例4：制造业热学数据存储与分析系统](#5-案例4制造业热学数据存储与分析系统)
    - [5.1 业务背景](#51-业务背景)
    - [5.2 技术挑战](#52-技术挑战)
    - [5.3 Schema定义](#53-schema定义)
    - [5.4 Python代码实现](#54-python代码实现)
    - [5.5 效果评估](#55-效果评估)

---

## 1. 案例概述

本文档提供热学Schema在实际应用中的实践案例，涵盖数据中心、工业照明、智能建筑和制造业四大领域。每个案例包含完整的业务背景分析、技术挑战解析、Schema定义、Python代码实现以及效果评估，为工程师提供从理论到实践的全方位参考。

---

## 2. 案例1：数据中心CPU散热系统热学设计

### 2.1 业务背景

**企业背景**：

- **公司名称**：华云数据科技有限公司
- **行业领域**：云计算与数据中心服务
- **业务规模**：运营3个大型数据中心，共计15,000台服务器
- **地理位置**：华东地区，夏季最高温度达40°C

**业务痛点**：

1. **散热成本激增**：数据中心PUE（能源使用效率）高达1.6，其中40%能耗用于散热，年电费超过8000万元
2. **服务器过热宕机**：夏季高温期间，每月平均发生12次CPU过热保护性关机，导致服务中断
3. **散热设计缺乏标准化**：不同批次服务器散热方案各异，维护成本高昂
4. **热仿真精度不足**：现有CFD仿真与实际温差达8-12°C，导致设计余量过大，材料浪费严重

**业务目标**：

- 将数据中心PUE从1.6降低至1.4以下
- 减少CPU过热事件90%以上
- 建立标准化的热学设计流程，缩短新服务器散热设计周期50%
- 提高热仿真精度，仿真误差控制在±3°C以内

### 2.2 技术挑战

1. **多物理场耦合复杂性**：CPU散热涉及导热、对流、辐射三种传热方式，且与电磁场、流场强耦合，传统单一物理场仿真无法准确预测温度分布
2. **瞬态热负载波动**：云计算负载呈明显波峰波谷特征，CPU功耗在30%-100% TDP间快速波动，传统稳态热设计方法导致散热器过度设计
3. **多尺度热阻网络建模**：从芯片级（μm级）到机架级（m级）跨越6个数量级，需要建立有效的多尺度热阻网络模型
4. **冷却系统优化难题**：需在散热性能、噪音控制、能耗之间取得平衡，传统试错法优化效率低下
5. **实时热监控与预警**：现有监控系统粒度粗（分钟级），无法捕捉秒级温度突变，缺乏预测性维护能力

### 2.3 Schema定义

**CPU散热系统热学Schema**：

```dsl
schema CPUThermalSystem {
  cpu: {
    tdp: Float64 @value(95.0) @unit("W")
    max_temperature: Float64 @value(100.0) @unit("°C")
    operating_temperature: Range {
      min: Float64 @value(0.0) @unit("°C")
      max: Float64 @value(85.0) @unit("°C")
    }
  }

  heatsink: {
    material: Enum { Aluminum, Copper }
    thermal_conductivity: Float64 @value(205.0) @unit("W/(m·K)")
    thermal_resistance: Float64 @value(0.3) @unit("K/W")
    surface_area: Float64 @value(0.05) @unit("m²")
  }

  fan: {
    airflow: Float64 @value(50.0) @unit("CFM")
    static_pressure: Float64 @value(2.5) @unit("mmH₂O")
    noise_level: Float64 @value(25.0) @unit("dBA")
  }

  thermal_interface: {
    material: Enum { Thermal_Paste, Thermal_Pad }
    thermal_conductivity: Float64 @value(8.0) @unit("W/(m·K)")
    thickness: Float64 @value(0.1) @unit("mm")
  }
} @standard("IEC_60335-1")
```

### 2.4 Python代码实现

```python
"""
数据中心CPU散热系统热学设计与分析模块
包含：热阻计算、CFD数据解析、散热器设计优化、温度监控预警
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json
from datetime import datetime, timedelta
import warnings


class Material(Enum):
    """散热器材料枚举"""
    ALUMINUM = "Aluminum"
    COPPER = "Copper"


class TIMMaterial(Enum):
    """热界面材料枚举"""
    THERMAL_PASTE = "Thermal_Paste"
    THERMAL_PAD = "Thermal_Pad"


@dataclass
class CPU:
    """CPU热学参数"""
    tdp: float = 95.0                    # 热设计功耗 (W)
    max_temp: float = 100.0              # 最高允许温度 (°C)
    junction_temp: float = 85.0          # 目标结温 (°C)
    thermal_resistance_jc: float = 0.5   # 结壳热阻 (K/W)
    die_size: float = 20e-6              # 芯片尺寸 (m²)

    def get_max_power(self, ambient_temp: float) -> float:
        """计算给定环境温度下的最大允许功耗"""
        delta_t = self.max_temp - ambient_temp
        return delta_t / self.thermal_resistance_jc


@dataclass
class Heatsink:
    """散热器热学参数"""
    material: Material = Material.ALUMINUM
    thermal_conductivity: float = 205.0   # W/(m·K)
    base_thickness: float = 5e-3          # m
    fin_height: float = 40e-3             # m
    fin_thickness: float = 1e-3           # m
    fin_count: int = 50
    base_area: float = 0.008              # m²

    def calculate_thermal_resistance(self, airflow: float) -> float:
        """计算散热器热阻 (基于翅片效率理论)"""
        # 翅片参数
        fin_spacing = self.base_area**0.5 / self.fin_count
        fin_efficiency = np.tanh(
            (2 * self.thermal_conductivity * fin_spacing /
             (self.fin_thickness * 25))**0.5 * self.fin_height
        ) / ((2 * self.thermal_conductivity * fin_spacing /
              (self.fin_thickness * 25))**0.5 * self.fin_height)

        # 对流换热系数 (简化模型)
        h = 10 + airflow * 0.5  # W/(m²·K)

        # 总表面积
        fin_area = 2 * self.fin_height * (self.base_area**0.5) * self.fin_count
        base_exposed = self.base_area - self.fin_count * self.fin_thickness * (self.base_area**0.5)
        total_area = fin_area * fin_efficiency + base_exposed

        # 热阻
        r_conv = 1 / (h * total_area)
        r_cond = self.base_thickness / (self.thermal_conductivity * self.base_area)

        return r_cond + r_conv


@dataclass
class ThermalInterface:
    """热界面材料参数"""
    material: TIMMaterial = TIMMaterial.THERMAL_PASTE
    thermal_conductivity: float = 8.0    # W/(m·K)
    thickness: float = 0.1e-3            # m
    area: float = 0.002                  # m²

    def calculate_resistance(self) -> float:
        """计算界面热阻"""
        return self.thickness / (self.thermal_conductivity * self.area)


@dataclass
class Fan:
    """风扇参数"""
    airflow: float = 50.0               # CFM
    static_pressure: float = 2.5        # mmH₂O
    noise_level: float = 25.0           # dBA
    pwm_duty: float = 100.0             # %

    def get_actual_airflow(self, system_pressure: float) -> float:
        """根据系统阻力计算实际风量"""
        # 简化风扇曲线模型
        max_pressure = self.static_pressure * 9.81 * 1000  # Pa
        pressure_drop = system_pressure

        if pressure_drop >= max_pressure:
            return 0.0

        flow_factor = (1 - pressure_drop / max_pressure) ** 0.5
        return self.airflow * flow_factor * (self.pwm_duty / 100)


class CPUThermalSystem:
    """CPU散热系统综合模型"""

    def __init__(self, cpu: CPU, heatsink: Heatsink,
                 tim: ThermalInterface, fan: Fan):
        self.cpu = cpu
        self.heatsink = heatsink
        self.tim = tim
        self.fan = fan
        self.ambient_temp = 25.0

    def calculate_thermal_resistance_network(self) -> Dict[str, float]:
        """计算热阻网络"""
        r_jc = self.cpu.thermal_resistance_jc
        r_tim = self.tim.calculate_resistance()
        r_hs = self.heatsink.calculate_thermal_resistance(self.fan.airflow)

        r_total = r_jc + r_tim + r_hs

        return {
            'junction_to_case': r_jc,
            'thermal_interface': r_tim,
            'heatsink': r_hs,
            'total': r_total
        }

    def calculate_temperature(self, power: float, ambient: float) -> Dict[str, float]:
        """计算温度分布"""
        r_network = self.calculate_thermal_resistance_network()

        delta_t = power * r_network['total']
        case_temp = ambient + power * (r_network['thermal_interface'] + r_network['heatsink'])
        junction_temp = case_temp + power * r_network['junction_to_case']

        return {
            'ambient': ambient,
            'case': case_temp,
            'junction': junction_temp,
            'delta_t': delta_t
        }

    def check_design(self, power: float, ambient: float) -> Dict:
        """检查设计是否满足要求"""
        temps = self.calculate_temperature(power, ambient)
        margin = self.cpu.max_temp - temps['junction']

        return {
            'is_valid': temps['junction'] < self.cpu.max_temp,
            'junction_temp': temps['junction'],
            'safety_margin': margin,
            'recommendations': self._get_recommendations(temps['junction'], margin)
        }

    def _get_recommendations(self, temp: float, margin: float) -> List[str]:
        """生成设计建议"""
        recs = []
        if margin < 5:
            recs.append("警告：温度余量不足，建议增强散热")
        if margin < 0:
            recs.append("危险：设计不满足要求，必须改进散热方案")
        if temp > 90:
            recs.append("建议：考虑增加风扇转速或更换更大散热器")
        return recs


class CFDDataParser:
    """CFD仿真数据解析器"""

    def __init__(self, cfd_file: Optional[str] = None):
        self.data = None
        self.mesh_info = {}

    def parse_csv(self, file_path: str) -> pd.DataFrame:
        """解析CFD导出的CSV数据"""
        df = pd.read_csv(file_path)

        # 验证必要列
        required_cols = ['x', 'y', 'z', 'temperature', 'velocity']
        for col in required_cols:
            if col not in df.columns:
                warnings.warn(f"缺少列: {col}")

        self.data = df
        return df

    def calculate_statistics(self) -> Dict:
        """计算温度场统计信息"""
        if self.data is None:
            return {}

        temps = self.data['temperature']
        return {
            'max_temp': temps.max(),
            'min_temp': temps.min(),
            'mean_temp': temps.mean(),
            'std_temp': temps.std(),
            'hotspot_count': (temps > 85).sum()
        }

    def compare_with_simulation(self, measured_temps: np.ndarray) -> Dict:
        """对比仿真与实测数据"""
        if self.data is None:
            return {}

        sim_temps = self.data['temperature'].values[:len(measured_temps)]

        error = sim_temps - measured_temps
        mae = np.mean(np.abs(error))
        rmse = np.sqrt(np.mean(error ** 2))
        max_error = np.max(np.abs(error))

        return {
            'mae': mae,
            'rmse': rmse,
            'max_error': max_error,
            'correlation': np.corrcoef(sim_temps, measured_temps)[0,1]
        }


class TemperatureMonitor:
    """温度监控与预警系统"""

    def __init__(self, warning_threshold: float = 80.0,
                 critical_threshold: float = 95.0):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.history: List[Dict] = []
        self.max_history = 1000

    def add_reading(self, timestamp: datetime, temp: float,
                    power: float, fan_speed: float):
        """添加温度读数"""
        reading = {
            'timestamp': timestamp,
            'temperature': temp,
            'power': power,
            'fan_speed': fan_speed,
            'alert_level': self._determine_alert_level(temp)
        }

        self.history.append(reading)

        # 限制历史记录数量
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def _determine_alert_level(self, temp: float) -> str:
        """确定告警级别"""
        if temp >= self.critical_threshold:
            return "CRITICAL"
        elif temp >= self.warning_threshold:
            return "WARNING"
        return "NORMAL"

    def predict_temperature(self, future_minutes: int = 5) -> float:
        """基于历史数据预测未来温度（简单线性外推）"""
        if len(self.history) < 10:
            return self.history[-1]['temperature'] if self.history else 25.0

        recent = self.history[-10:]
        temps = [r['temperature'] for r in recent]
        times = list(range(len(temps)))

        # 线性回归
        slope, intercept = np.polyfit(times, temps, 1)
        prediction = intercept + slope * (len(temps) + future_minutes)

        return min(prediction, 110.0)  # 上限保护

    def get_thermal_report(self) -> Dict:
        """生成热管理报告"""
        if not self.history:
            return {}

        temps = [h['temperature'] for h in self.history]

        return {
            'max_temp': max(temps),
            'avg_temp': np.mean(temps),
            'temp_stability': np.std(temps),
            'warning_count': sum(1 for h in self.history if h['alert_level'] == 'WARNING'),
            'critical_count': sum(1 for h in self.history if h['alert_level'] == 'CRITICAL'),
            'uptime_hours': len(self.history) / 60  # 假设每分钟一个数据点
        }


def optimize_heatsink(cpu: CPU, constraints: Dict) -> Heatsink:
    """散热器优化设计"""
    best_design = None
    best_score = float('inf')

    # 参数搜索空间
    fin_heights = [30e-3, 40e-3, 50e-3]
    fin_counts = [40, 50, 60]
    materials = [Material.ALUMINUM, Material.COPPER]

    for material in materials:
        for fin_h in fin_heights:
            for fin_n in fin_counts:
                hs = Heatsink(
                    material=material,
                    fin_height=fin_h,
                    fin_count=fin_n,
                    thermal_conductivity=400 if material == Material.COPPER else 205
                )

                system = CPUThermalSystem(
                    cpu=cpu,
                    heatsink=hs,
                    tim=ThermalInterface(),
                    fan=Fan()
                )

                result = system.check_design(cpu.tdp, constraints['ambient_max'])

                if result['is_valid']:
                    # 评分：热阻 + 成本惩罚
                    r_network = system.calculate_thermal_resistance_network()
                    cost_penalty = 1.5 if material == Material.COPPER else 1.0
                    score = r_network['total'] * cost_penalty

                    if score < best_score:
                        best_score = score
                        best_design = hs

    return best_design


# 使用示例
if __name__ == "__main__":
    # 创建系统组件
    cpu = CPU(tdp=95.0, max_temp=100.0)
    heatsink = Heatsink(material=Material.ALUMINUM)
    tim = ThermalInterface()
    fan = Fan(airflow=50.0)

    # 构建散热系统
    system = CPUThermalSystem(cpu, heatsink, tim, fan)

    # 设计验证
    design_check = system.check_design(power=95.0, ambient=35.0)
    print("设计验证结果:", json.dumps(design_check, indent=2))

    # 热阻网络分析
    r_network = system.calculate_thermal_resistance_network()
    print("\n热阻网络:", json.dumps(r_network, indent=2))

    # 温度监控
    monitor = TemperatureMonitor()
    for i in range(60):
        temp = 65 + 10 * np.sin(i / 10) + np.random.normal(0, 2)
        monitor.add_reading(
            timestamp=datetime.now() + timedelta(minutes=i),
            temp=temp,
            power=80 + np.random.normal(0, 5),
            fan_speed=2000
        )

    report = monitor.get_thermal_report()
    print("\n热管理报告:", json.dumps(report, indent=2, default=str))
```

### 2.5 效果评估

**性能指标**：

| 指标              | 改进前      | 改进后     | 提升幅度  |
| ----------------- | ----------- | ---------- | --------- |
| 热仿真精度（MAE） | 8-12°C     | ±2.3°C   | 提升80%   |
| CFD计算效率       | 48小时/模型 | 6小时/模型 | 提升87%   |
| 温度预测准确率    | 75%         | 96.5%      | 提升21.5% |
| CPU结温           | 92°C       | 76°C      | 降低16°C |
| 散热器设计周期    | 4周         | 1.5周      | 缩短62%   |

**业务价值**：

1. **能耗成本节约**：PUE从1.6降至1.38，年节约电费约 **1,760万元**（按0.6元/kWh计算）
2. **运维效率提升**：

   - CPU过热事件从月均12次降至0.8次，降幅93%
   - 散热相关故障工单减少85%
   - 运维人力成本节约约 **120万元/年**
3. **标准化收益**：

   - 新服务器上架时间从7天缩短至2天
   - 备件库存种类减少60%，库存成本降低 **200万元**
4. **投资回报**：

   - 项目总投资：380万元（含软件开发、硬件升级、人员培训）
   - 年度节约：2,080万元
   - **ROI = 447%，投资回收期2.2个月**

**经验教训**：

1. **技术层面**：

   - 多尺度建模时，芯片级热阻对整体预测精度影响最大，需优先保证该参数准确性
   - 瞬态热仿真计算量大，建议采用降阶模型（ROM）进行实时预测
   - 热界面材料的热阻在实际工况下会随时间退化，需引入老化模型
2. **管理层面**：

   - 跨部门协作至关重要，热设计团队需与硬件、软件、运维团队建立常态化沟通机制
   - 建立热学知识库，积累历史设计案例和故障数据，持续优化设计规则
3. **改进方向**：

   - 引入AI辅助设计，利用历史数据训练热阻预测模型
   - 探索液冷等新型散热技术，目标PUE < 1.2
   - 建立数字孪生平台，实现物理设备与虚拟模型的实时同步

---

## 3. 案例2：工业LED灯具热管理

### 3.1 业务背景

**企业背景**：

- **公司名称**：明辉照明科技有限公司
- **行业领域**：工业LED照明设备制造
- **业务规模**：年产LED工矿灯50万套，出口欧美、东南亚市场
- **产品定位**：高端工业照明，主打高光效、长寿命、低光衰

**业务痛点**：

1. **光衰过快**：产品质保5年光通量维持率>90%，但实际运行2年即出现15%光衰，客户投诉率高达8%
2. **结温控制困难**：高功率LED（100W-300W）结温设计余量不足，夏季高温环境下频繁触发过热保护
3. **散热器重量过大**：为满足散热需求，散热器重量占整灯60%，增加运输成本和安装难度
4. **热测试周期长**：每款新产品需进行2000小时老化测试，导致新产品上市周期长达6个月

**业务目标**：

- 将LED结温控制在85°C以下（原设计100°C）
- 将5年光通量维持率提升至95%以上
- 散热器减重30%，同时保证散热性能
- 建立热仿真-测试闭环，将新产品开发周期缩短至3个月

### 3.2 技术挑战

1. **LED热-光-电耦合特性**：LED的光效、色温、寿命均与结温强相关，且存在负反馈效应（温度升高→光效下降→热流密度增加），传统分离式设计方法难以处理
2. **复杂边界条件**：工业灯具安装环境多变（工厂、仓库、矿井），自然对流受限情况下的热设计极具挑战
3. **材料与成本约束**：高端导热材料（如石墨烯、热管）成本高昂，需在性能与成本间取得平衡
4. **多热源协同散热**：COB（板上芯片）封装中多颗LED芯片近距离排布，热流密度叠加效应显著
5. **可靠性验证困难**：加速寿命测试与实际工况对应关系不明确，难以通过短期测试预测长期性能

### 3.3 Schema定义

**LED灯具热学Schema**：

```dsl
schema LEDThermalManagement {
  led: {
    power: Float64 @value(10.0) @unit("W")
    max_junction_temperature: Float64 @value(120.0) @unit("°C")
    thermal_resistance_junction_case: Float64 @value(2.5) @unit("K/W")
  }

  heatsink: {
    material: Enum { Aluminum }
    thermal_resistance: Float64 @value(5.0) @unit("K/W")
    surface_area: Float64 @value(0.1) @unit("m²")
    emissivity: Float64 @value(0.8)
  }

  ambient_temperature: Float64 @value(25.0) @unit("°C")
} @standard("IEC_60335-1")
```

### 3.4 Python代码实现

```python
"""
工业LED灯具热管理与光衰预测模块
包含：LED热-光-电耦合模型、散热器优化、光衰预测、寿命评估
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


@dataclass
class LEDChip:
    """LED芯片热学与光学参数"""
    power: float = 100.0                  # 额定功率 (W)
    max_junction_temp: float = 150.0      # 最高结温 (°C)
    target_junction_temp: float = 85.0    # 目标结温 (°C)
    thermal_resistance_jc: float = 2.5    # 结壳热阻 (K/W)
    luminous_efficacy: float = 130.0      # 光效 (lm/W) @25°C
    temp_coefficient: float = -0.003      # 光效温度系数 (/°C)

    def get_luminous_flux(self, junction_temp: float) -> float:
        """计算给定结温下的光通量"""
        efficacy = self.luminous_efficacy * (1 + self.temp_coefficient *
                                             (junction_temp - 25))
        return efficacy * self.power

    def get_actual_power(self, junction_temp: float,
                         driver_efficiency: float = 0.92) -> float:
        """计算实际热功耗（光输出功率已从电功率中扣除）"""
        efficacy = self.luminous_efficacy * (1 + self.temp_coefficient *
                                             (junction_temp - 25))
        optical_power = self.power * efficacy / 350  # 光功率 (W, 350 lm/W为理论极限)
        electrical_power = self.power / driver_efficiency
        return electrical_power - optical_power


@dataclass
class HeatsinkLED:
    """LED散热器参数"""
    material: str = "Aluminum_6063"
    thermal_conductivity: float = 200.0   # W/(m·K)
    weight: float = 2.5                   # kg
    surface_area: float = 0.5             # m²
    fin_efficiency: float = 0.75
    emissivity: float = 0.85
    thermal_resistance: float = 2.0       # K/W (典型值)

    def calculate_natural_convection(self, delta_t: float) -> float:
        """计算自然对流换热系数"""
        # 简化Grashof数计算，假设特征长度0.1m
        beta = 1 / 300  # 1/K (体积膨胀系数)
        nu = 1.5e-5     # m²/s (运动粘度)
        alpha = 2.2e-5  # m²/s (热扩散系数)
        L = 0.1         # m (特征长度)
        g = 9.81

        Gr = g * beta * delta_t * L**3 / nu**2
        Pr = nu / alpha
        Ra = Gr * Pr

        # 垂直平板自然对流关联式
        Nu = 0.59 * Ra**0.25  # 层流假设
        k_air = 0.026  # W/(m·K)
        h_conv = Nu * k_air / L

        return h_conv

    def calculate_radiation(self, surface_temp: float, ambient: float) -> float:
        """计算辐射换热系数"""
        sigma = 5.67e-8  # Stefan-Boltzmann常数
        Ts = surface_temp + 273.15
        Ta = ambient + 273.15

        h_rad = self.emissivity * sigma * (Ts**2 + Ta**2) * (Ts + Ta)
        return h_rad

    def calculate_thermal_resistance_detailed(self, power: float,
                                              ambient: float) -> float:
        """详细计算散热器热阻（考虑温度依赖性）"""
        # 迭代求解表面温度
        def equation(surface_temp):
            delta_t = surface_temp - ambient
            h_conv = self.calculate_natural_convection(delta_t)
            h_rad = self.calculate_radiation(surface_temp, ambient)
            h_total = h_conv + h_rad

            q = h_total * self.surface_area * delta_t
            return q - power

        # 简化解法
        from scipy.optimize import brentq
        try:
            t_surface = brentq(equation, ambient, ambient + 100)
        except:
            t_surface = ambient + power / (10 * self.surface_area)  # fallback

        delta_t = t_surface - ambient
        r_hs = delta_t / power

        return r_hs


@dataclass
class LEDDriver:
    """LED驱动电源参数"""
    output_power: float = 100.0           # W
    efficiency: float = 0.92              # %
    max_case_temp: float = 85.0           # °C
    thermal_resistance: float = 15.0      # K/W


class LumenDepreciationModel:
    """LED光衰预测模型（基于TM-21标准）"""

    def __init__(self, led: LEDChip):
        self.led = led
        # 光衰系数，与结温相关 (基于Arrhenius方程)
        self.activation_energy = 0.45  # eV
        self.prefactor = 1e6           # 小时

    def get_l70_lifetime(self, junction_temp: float) -> float:
        """计算L70寿命（光通量维持70%的时间）"""
        k_b = 8.617e-5  # Boltzmann常数 (eV/K)
        T_k = junction_temp + 273.15

        # Arrhenius方程
        lifetime = self.prefactor * np.exp(self.activation_energy /
                                           (k_b * T_k))
        return lifetime

    def predict_lumen_maintenance(self, hours: float,
                                   junction_temp: float) -> float:
        """预测运行hours小时后的光通量维持率"""
        l70 = self.get_l70_lifetime(junction_temp)
        # 指数衰减模型
        beta = -np.log(0.7) / l70
        maintenance = np.exp(beta * hours)
        return maintenance * 100  # 百分比

    def get_warranty_compliance(self, warranty_years: int,
                                hours_per_year: float,
                                junction_temps: List[float]) -> Dict:
        """检查是否符合质保要求"""
        total_hours = warranty_years * hours_per_year
        avg_temp = np.mean(junction_temps)

        maintenance = self.predict_lumen_maintenance(total_hours, avg_temp)

        return {
            'warranty_years': warranty_years,
            'total_hours': total_hours,
            'avg_junction_temp': avg_temp,
            'predicted_maintenance': maintenance,
            'compliant': maintenance >= 90,  # 假设质保要求90%
            'margin': maintenance - 90
        }


class LEDThermalSystem:
    """LED灯具热管理系统"""

    def __init__(self, led: LEDChip, heatsink: HeatsinkLED,
                 driver: LEDDriver):
        self.led = led
        self.heatsink = heatsink
        self.driver = driver
        self.ambient_temp = 25.0

    def solve_steady_state(self, ambient: float) -> Dict:
        """求解稳态热平衡"""
        # 迭代求解结温
        tj = ambient + 50  # 初始猜测

        for _ in range(20):  # 最大迭代次数
            # 计算实际热功耗
            p_thermal = self.led.get_actual_power(tj)

            # 驱动损耗
            p_driver_loss = self.driver.output_power * (1 / self.driver.efficiency - 1)

            # 总热流
            p_total = p_thermal + p_driver_loss

            # 计算热阻
            r_hs = self.heatsink.calculate_thermal_resistance_detailed(
                p_total, ambient
            )

            # 计算新的结温
            tj_new = ambient + p_thermal * (self.led.thermal_resistance_jc + r_hs)

            if abs(tj_new - tj) < 0.1:
                break
            tj = tj_new

        return {
            'junction_temp': tj,
            'heatsink_temp': tj - p_thermal * self.led.thermal_resistance_jc,
            'thermal_power': p_total,
            'luminous_flux': self.led.get_luminous_flux(tj),
            'light_output': self.led.get_luminous_flux(tj) / self.led.power / \
                          self.led.luminous_efficacy * 100  # 相对光输出%
        }

    def optimize_heatsink_weight(self, target_temp: float,
                                  ambient_max: float) -> Dict:
        """在给定结温约束下优化散热器重量"""
        def objective(weight_factor):
            # 假设表面积与重量的2/3次方成正比
            hs = HeatsinkLED(
                weight=self.heatsink.weight * weight_factor,
                surface_area=self.heatsink.surface_area * weight_factor**0.67
            )

            system = LEDThermalSystem(self.led, hs, self.driver)
            result = system.solve_steady_state(ambient_max)

            # 惩罚项：如果温度超标
            temp_penalty = max(0, result['junction_temp'] - target_temp) * 100

            return weight_factor + temp_penalty

        result = minimize_scalar(objective, bounds=(0.5, 2.0), method='bounded')

        optimal_weight = self.heatsink.weight * result.x
        weight_reduction = (1 - result.x) * 100

        return {
            'optimal_weight': optimal_weight,
            'weight_reduction': weight_reduction,
            'original_weight': self.heatsink.weight
        }

    def thermal_analysis_report(self, ambient_range: Tuple[float, float] = (25, 45)) -> pd.DataFrame:
        """生成不同环境温度下的热分析报表"""
        ambients = np.linspace(ambient_range[0], ambient_range[1], 5)

        results = []
        lumen_model = LumenDepreciationModel(self.led)

        for amb in ambients:
            state = self.solve_steady_state(amb)
            lifetime = lumen_model.get_l70_lifetime(state['junction_temp'])

            results.append({
                'ambient_temp': amb,
                'junction_temp': state['junction_temp'],
                'thermal_power': state['thermal_power'],
                'luminous_flux': state['luminous_flux'],
                'light_output_pct': state['light_output'],
                'l70_lifetime_hours': lifetime,
                'l70_lifetime_years': lifetime / 8760
            })

        return pd.DataFrame(results)


class AcceleratedLifeTest:
    """加速寿命测试分析"""

    def __init__(self, led: LEDChip):
        self.led = led
        self.test_data: List[Dict] = []

    def simulate_alt(self, test_temp: float, test_duration: int,
                     sample_size: int = 20) -> Dict:
        """模拟加速寿命测试"""
        # 基于Arrhenius模型计算加速因子
        k_b = 8.617e-5
        e_a = 0.45  # eV

        t_use = self.led.target_junction_temp + 273.15
        t_test = test_temp + 273.15

        af = np.exp(e_a / k_b * (1/t_use - 1/t_test))

        # 模拟测试数据（加入随机噪声）
        lumen_data = []
        for _ in range(sample_size):
            # 指数衰减 + 噪声
            l70_actual = np.random.lognormal(np.log(50000/af), 0.2)
            maintenance = np.exp(-test_duration * np.log(0.7) / l70_actual)
            lumen_data.append(maintenance * 100)

        self.test_data = lumen_data

        return {
            'acceleration_factor': af,
            'equivalent_use_hours': test_duration * af,
            'sample_mean': np.mean(lumen_data),
            'sample_std': np.std(lumen_data),
            'min_95_ci': np.mean(lumen_data) - 1.96 * np.std(lumen_data) / np.sqrt(sample_size),
            'test_temperature': test_temp,
            'test_duration': test_duration
        }

    def project_lifetime(self, target_maintenance: float = 70.0) -> float:
        """基于测试数据投影寿命"""
        if not self.test_data:
            return 0.0

        # 使用最后的数据点进行线性外推（简化模型）
        current_maintenance = np.mean(self.test_data)
        degradation_rate = (100 - current_maintenance) / len(self.test_data)

        if degradation_rate <= 0:
            return float('inf')

        hours_to_target = (100 - target_maintenance) / degradation_rate
        return hours_to_target


def design_comparison(led_powers: List[float]) -> pd.DataFrame:
    """不同功率LED的热设计对比"""
    results = []

    for power in led_powers:
        led = LEDChip(power=power)

        # 基于经验公式估算所需散热器
        required_area = power * 0.005  # m² (经验值: 200W/m²)
        weight = required_area * 5     # kg/m²

        heatsink = HeatsinkLED(
            surface_area=required_area,
            weight=weight
        )

        driver = LEDDriver(output_power=power)
        system = LEDThermalSystem(led, heatsink, driver)

        state = system.solve_steady_state(ambient=35)

        results.append({
            'led_power': power,
            'heatsink_weight': weight,
            'surface_area': required_area,
            'junction_temp': state['junction_temp'],
            'luminous_flux': state['luminous_flux'],
            'system_efficiency': state['luminous_flux'] / (power * 130) * 100
        })

    return pd.DataFrame(results)


# 使用示例
if __name__ == "__main__":
    # 创建100W LED工矿灯系统
    led = LEDChip(power=100.0, target_junction_temp=85.0)
    heatsink = HeatsinkLED(weight=2.5, surface_area=0.6)
    driver = LEDDriver(output_power=100.0, efficiency=0.93)

    system = LEDThermalSystem(led, heatsink, driver)

    # 稳态分析
    print("=== 稳态热分析 ===")
    for amb in [25, 35, 45]:
        state = system.solve_steady_state(amb)
        print(f"环境温度 {amb}°C: 结温={state['junction_temp']:.1f}°C, "
              f"光通量={state['luminous_flux']:.0f}lm")

    # 热分析报告
    print("\n=== 热分析报表 ===")
    report = system.thermal_analysis_report()
    print(report.to_string(index=False))

    # 重量优化
    print("\n=== 散热器重量优化 ===")
    opt_result = system.optimize_heatsink_weight(target_temp=85.0, ambient_max=40)
    print(f"原始重量: {opt_result['original_weight']:.2f}kg")
    print(f"优化后重量: {opt_result['optimal_weight']:.2f}kg")
    print(f"减重比例: {opt_result['weight_reduction']:.1f}%")

    # 光衰预测
    print("\n=== 光衰预测 ===")
    lumen_model = LumenDepreciationModel(led)
    warranty = lumen_model.get_warranty_compliance(
        warranty_years=5,
        hours_per_year=4000,
        junction_temps=[75, 80, 85]
    )
    print(f"质保5年预测维持率: {warranty['predicted_maintenance']:.1f}%")
    print(f"符合质保要求: {warranty['compliant']}")

    # 加速寿命测试
    print("\n=== 加速寿命测试分析 ===")
    alt = AcceleratedLifeTest(led)
    alt_result = alt.simulate_alt(test_temp=85, test_duration=3000)
    print(f"加速因子: {alt_result['acceleration_factor']:.1f}x")
    print(f"等效使用小时: {alt_result['equivalent_use_hours']:.0f}h")
```

### 3.5 效果评估

**性能指标**：

| 指标            | 改进前 | 改进后   | 提升幅度  |
| --------------- | ------ | -------- | --------- |
| LED结温         | 105°C | 78°C    | 降低27°C |
| 5年光通量维持率 | 85%    | 96.2%    | 提升11.2% |
| 散热器重量      | 3.2kg  | 2.1kg    | 减重34%   |
| 热仿真误差      | ±8°C | ±2.5°C | 提升69%   |
| 新产品开发周期  | 6个月  | 2.8个月  | 缩短53%   |

**业务价值**：

1. **质量成本降低**：

   - 客户投诉率从8%降至0.5%，年节约售后成本 **320万元**
   - 产品退货率降低90%，挽回收入损失 **580万元/年**
2. **设计效率提升**：

   - 热仿真替代50%的物理样机测试，节约样机成本 **120万元/年**
   - 新产品上市时间缩短3.2个月，抢占市场先机，增收约 **800万元**
3. **材料成本节约**：

   - 散热器减重34%，年节约铝材成本 **150万元**
   - 运输成本降低20%，年节约 **80万元**
4. **投资回报**：

   - 项目总投资：180万元（热仿真软件、测试设备、人员培训）
   - 年度综合收益：2,050万元
   - **ROI = 1,039%，投资回收期1.1个月**

**经验教训**：

1. **技术层面**：

   - LED结温每降低10°C，寿命约延长2倍，严格控制结温是提升可靠性的关键
   - 自然对流散热对散热器表面纹理敏感，阳极氧化处理可提升辐射散热15%
   - 热-光-电耦合模型中，光效温度系数的准确测量至关重要
2. **管理层面**：

   - 建立热设计与光学设计协同流程，避免两个团队目标冲突
   - 引入供应商参与热设计，确保LED芯片热阻数据准确可靠
3. **改进方向**：

   - 开发自适应散热系统，根据环境温度自动调节功率或风量
   - 研究相变材料（PCM）在LED热管理中的应用，应对峰值热负载
   - 建立产品全生命周期热管理平台，实现远程监控与预测性维护

---

## 4. 案例3：智能建筑热工设计

### 4.1 业务背景

**企业背景**：

- **项目名称**：绿地智慧商务中心
- **项目类型**：5A级智能写字楼，建筑面积8万平方米
- **地理位置**：华东地区，夏季湿热、冬季湿冷
- **建设目标**：申请LEED铂金级认证、中国绿色建筑三星级认证

**业务痛点**：

1. **能耗过高**：同类建筑年均电耗150kWh/m²，业主期望降至100kWh/m²以下
2. **热舒适度差**：传统空调系统温度波动大（±3°C），员工满意度仅65%
3. **热桥效应严重**：幕墙与主体结构连接处冬季结露，影响建筑美观与结构安全
4. **缺乏动态优化能力**：HVAC系统按固定时间表运行，无法根据实际 occupancy 调整

**业务目标**：

- 建筑综合能耗降低30%，达到100kWh/m²·年以下
- 室内热舒适度PMV（预测平均投票）指数保持在-0.5~+0.5范围内
- 消除热桥结露风险，表面温度高于露点温度2°C以上
- 建立建筑能源管理系统（BEMS），实现能耗实时监控与优化

### 4.2 技术挑战

1. **多区域热负荷差异大**：南向玻璃幕墙区域与北向核心区热负荷差异可达3:1，传统单一控制策略无法满足各区域需求
2. **热惰性动态响应**：混凝土结构热惰性大，空调调节存在2-4小时延迟，需建立预测控制模型
3. **复杂热桥网络**：超高层建筑中存在数千处热桥，逐一建模计算量巨大，需开发热桥快速评估方法
4. **可再生能源集成**：地源热泵、太阳能热水系统与主HVAC系统的耦合控制复杂
5. **数据融合与预测**：需融合气象数据、 occupancy 数据、设备运行数据，建立负荷预测模型

### 4.3 Schema定义

**建筑热工Schema**：

```dsl
schema BuildingThermalDesign {
  wall: {
    material: Enum { Concrete, Brick, Insulation }
    thermal_resistance: Float64 @value(2.5) @unit("m²·K/W")
    thermal_capacity: Float64 @value(200000.0) @unit("J/(m²·K)")
    u_value: Float64 @value(0.4) @unit("W/(m²·K)")
  }

  window: {
    glazing_type: Enum { Single, Double, Triple }
    u_value: Float64 @value(1.2) @unit("W/(m²·K)")
    solar_heat_gain_coefficient: Float64 @value(0.5)
  }

  thermal_bridge: {
    psi_value: Float64 @value(0.1) @unit("W/(m·K)")
    length: Float64 @unit("m")
  }
} @standard("ISO_13786")
```

### 4.4 Python代码实现

```python
"""
智能建筑热工设计与能源管理系统
包含：建筑热负荷计算、热桥分析、HVAC优化控制、能耗预测
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from scipy.integrate import odeint
import json


@dataclass
class BuildingEnvelope:
    """建筑围护结构热工参数"""
    # 墙体参数
    wall_area: float = 5000.0            # m²
    wall_u_value: float = 0.35           # W/(m²·K)
    wall_thermal_capacity: float = 150000.0  # J/(m²·K)

    # 窗户参数
    window_area: float = 2500.0          # m²
    window_u_value: float = 1.2          # W/(m²·K)
    shgc: float = 0.4                    # 太阳得热系数

    # 屋顶参数
    roof_area: float = 8000.0            # m²
    roof_u_value: float = 0.25           # W/(m²·K)

    # 地板参数
    floor_area: float = 8000.0           # m²
    floor_u_value: float = 0.30          # W/(m²·K)

    # 热桥
    thermal_bridge_coeff: float = 0.08   # W/(m·K)
    thermal_bridge_length: float = 2000.0  # m

    def calculate_total_uA(self) -> float:
        """计算总传热系数×面积 (W/K)"""
        return (self.wall_area * self.wall_u_value +
                self.window_area * self.window_u_value +
                self.roof_area * self.roof_u_value +
                self.floor_area * self.floor_u_value +
                self.thermal_bridge_coeff * self.thermal_bridge_length)

    def calculate_total_thermal_capacity(self) -> float:
        """计算总热容 (J/K)"""
        return self.wall_area * self.wall_thermal_capacity


@dataclass
class ThermalBridge:
    """热桥详细参数"""
    name: str
    psi_value: float                     # W/(m·K) - 线性传热系数
    length: float                        # m
    surface_temp_factor: float = 0.7     # 表面温度降低系数

    def calculate_heat_loss(self, indoor_temp: float,
                           outdoor_temp: float) -> float:
        """计算热桥热损失"""
        return self.psi_value * self.length * (indoor_temp - outdoor_temp)

    def calculate_surface_temp(self, indoor_temp: float,
                               outdoor_temp: float) -> float:
        """计算热桥处表面温度"""
        return indoor_temp - self.surface_temp_factor * (indoor_temp - outdoor_temp)

    def check_condensation_risk(self, indoor_temp: float,
                                 outdoor_temp: float,
                                 relative_humidity: float) -> Dict:
        """检查结露风险"""
        # 计算露点温度 (简化Magnus公式)
        gamma = 17.27 * indoor_temp / (237.7 + indoor_temp) + np.log(relative_humidity/100)
        dew_point = 237.7 * gamma / (17.27 - gamma)

        surface_temp = self.calculate_surface_temp(indoor_temp, outdoor_temp)
        margin = surface_temp - dew_point

        return {
            'dew_point': dew_point,
            'surface_temp': surface_temp,
            'margin': margin,
            'risk_level': 'HIGH' if margin < 0 else 'MEDIUM' if margin < 2 else 'LOW'
        }


@dataclass
class HVACSystem:
    """暖通空调系统参数"""
    cooling_capacity: float = 1000.0     # kW
    heating_capacity: float = 800.0      # kW
    cop_cooling: float = 5.0             # 制冷能效比
    cop_heating: float = 4.0             # 制热能效比
    supply_air_temp: float = 14.0        # °C (制冷)
    supply_air_temp_heating: float = 35.0  # °C (制热)
    airflow_rate: float = 50.0           # m³/s

    def calculate_cooling_power(self, load: float) -> float:
        """计算制冷耗电量"""
        return load / self.cop_cooling

    def calculate_heating_power(self, load: float) -> float:
        """计算制热耗电量"""
        return load / self.cop_heating

    def calculate_sensible_heat_ratio(self, space_load: float,
                                       latent_load: float) -> float:
        """计算显热比"""
        total = space_load + latent_load
        return space_load / total if total > 0 else 1.0


class ThermalLoadCalculator:
    """建筑热负荷计算器"""

    def __init__(self, envelope: BuildingEnvelope):
        self.envelope = envelope
        self.solar_gain_coeff = 0.7  # 遮阳系数

    def calculate_conduction_load(self, outdoor_temp: float,
                                  indoor_temp: float) -> float:
        """计算传导热负荷 (W)"""
        uA = self.envelope.calculate_total_uA()
        return uA * (outdoor_temp - indoor_temp)

    def calculate_solar_gain(self, solar_radiation: float,
                            orientation: str = 'south') -> float:
        """计算太阳辐射得热 (W)"""
        # 不同朝向修正系数
        orientation_factors = {
            'south': 1.0, 'north': 0.4, 'east': 0.8, 'west': 0.9, 'horizontal': 1.2
        }
        factor = orientation_factors.get(orientation, 1.0)

        return (self.envelope.window_area * self.envelope.shgc *
                self.solar_gain_coeff * solar_radiation * factor)

    def calculate_internal_gain(self, occupancy: int,
                                equipment_power: float = 15.0) -> float:
        """计算内部得热 (W)"""
        person_heat = 130.0  # W/人
        return occupancy * person_heat + self.envelope.floor_area * equipment_power

    def calculate_ventilation_load(self, outdoor_temp: float,
                                   indoor_temp: float,
                                   ventilation_rate: float = 0.5) -> float:
        """计算新风负荷 (W)"""
        # ventilation_rate: 换气次数 (次/小时)
        air_density = 1.2  # kg/m³
        cp = 1005  # J/(kg·K)
        volume = self.envelope.floor_area * 3  # 假设层高3m

        mass_flow = volume * ventilation_rate * air_density / 3600  # kg/s
        return mass_flow * cp * (outdoor_temp - indoor_temp)

    def calculate_hourly_load(self, hour: int, outdoor_temps: List[float],
                              solar_data: Dict, occupancy: int) -> Dict:
        """计算逐时热负荷"""
        temp = outdoor_temps[hour % 24]
        indoor_setpoint = 26.0  # 夏季设定温度

        # 各项负荷
        conduction = self.calculate_conduction_load(temp, indoor_setpoint)
        solar = self.calculate_solar_gain(solar_data.get(hour, 0))
        internal = self.calculate_internal_gain(occupancy)
        ventilation = self.calculate_ventilation_load(temp, indoor_setpoint)

        cooling_load = max(0, conduction + solar + internal + ventilation)
        heating_load = min(0, conduction + internal + ventilation)

        return {
            'hour': hour,
            'outdoor_temp': temp,
            'cooling_load': cooling_load / 1000,  # kW
            'heating_load': abs(heating_load) / 1000,  # kW
            'solar_gain': solar / 1000,
            'internal_gain': internal / 1000
        }


class BuildingThermalModel:
    """建筑动态热过程模型"""

    def __init__(self, envelope: BuildingEnvelope, hvac: HVACSystem,
                 indoor_volume: float = 24000.0):
        self.envelope = envelope
        self.hvac = hvac
        self.volume = indoor_volume
        self.air_density = 1.2
        self.air_cp = 1005
        self.wall_cp = envelope.wall_thermal_capacity

    def thermal_equations(self, state, t, outdoor_temp_func,
                          solar_gain_func, occupancy_func):
        """建筑热平衡微分方程"""
        indoor_temp, wall_temp = state

        outdoor_temp = outdoor_temp_func(t)
        solar_gain = solar_gain_func(t)
        occupancy = occupancy_func(t)

        # 内部得热
        internal_gain = occupancy * 130 + self.envelope.floor_area * 15

        # 围护结构传热
        uA = self.envelope.calculate_total_uA()
        heat_loss_wall = uA * (outdoor_temp - indoor_temp) * 0.7
        heat_storage = (wall_temp - indoor_temp) * self.envelope.wall_area * 50

        # HVAC调节
        hvac_cooling = 0
        setpoint = 26.0
        if indoor_temp > setpoint + 0.5:
            hvac_cooling = min(self.hvac.cooling_capacity * 1000,
                              (indoor_temp - setpoint) * 5000)

        # 室内空气热平衡
        dT_air = (heat_loss_wall + heat_storage + solar_gain + internal_gain -
                 hvac_cooling) / (self.volume * self.air_density * self.air_cp)

        # 墙体热平衡 (简化)
        dT_wall = (outdoor_temp - wall_temp) / 7200  # 2小时时间常数

        return [dT_air, dT_wall]

    def simulate_day(self, outdoor_temps: List[float],
                    solar_gains: List[float],
                    occupancy: List[int]) -> pd.DataFrame:
        """模拟一天的热过程"""
        t = np.linspace(0, 24, 48)  # 每30分钟一个点

        # 插值函数
        def temp_func(t):
            idx = min(int(t) % 24, 23)
            return outdoor_temps[idx]
        def solar_func(t):
            idx = min(int(t) % 24, 23)
            return solar_gains[idx]
        def occ_func(t):
            idx = min(int(t) % 24, 23)
            return occupancy[idx]

        # 初始条件
        initial = [22.0, 20.0]

        # 求解ODE
        solution = odeint(self.thermal_equations, initial, t,
                         args=(temp_func, solar_func, occ_func))

        results = []
        for i, time in enumerate(t):
            hour = int(time)
            results.append({
                'hour': time,
                'indoor_temp': solution[i][0],
                'wall_temp': solution[i][1],
                'outdoor_temp': temp_func(time),
                'solar_gain': solar_func(time),
                'occupancy': occ_func(time)
            })

        return pd.DataFrame(results)


class EnergyManagementSystem:
    """建筑能源管理系统"""

    def __init__(self, building_model: BuildingThermalModel):
        self.model = building_model
        self.energy_data: List[Dict] = []

    def optimize_hvac_schedule(self, occupancy_schedule: Dict,
                               electricity_prices: Dict) -> Dict:
        """优化HVAC运行时间表"""
        # 简化优化：基于occupancy和价格进行预冷/预热策略
        schedule = {}

        for hour in range(24):
            occ = occupancy_schedule.get(hour, 0)
            price = electricity_prices.get(hour, 1.0)

            if occ > 0:
                # 有人时保持舒适温度
                schedule[hour] = {'mode': 'occupied', 'setpoint': 26.0}
            else:
                # 无人时利用热惰性进行负荷转移
                if price < 0.6:  # 低谷电价
                    schedule[hour] = {'mode': 'precool', 'setpoint': 24.0}
                else:
                    schedule[hour] = {'mode': 'setback', 'setpoint': 28.0}

        return schedule

    def calculate_pmv(self, air_temp: float, mean_radiant_temp: float,
                      air_velocity: float = 0.1,
                      relative_humidity: float = 50.0,
                      metabolic_rate: float = 1.2,
                      clothing_insulation: float = 0.5) -> float:
        """计算预测平均投票PMV指数"""
        # 简化PMV计算 (ISO 7730)
        pa = relative_humidity / 100 * 10 * np.exp(16.6536 - 4030.183 / (air_temp + 235))

        icl = clothing_insulation
        m = metabolic_rate * 58.15  # 转换为W/m²

        # 服装表面温度
        fcl = 1.05 + 0.645 * icl
        tcl = (35.7 - 0.028 * m) / fcl - icl * (3.96e-8 * fcl *
              ((mean_radiant_temp + 273)**4 - (air_temp + 273)**4) +
              fcl * air_velocity * 12.1 * np.sqrt(air_velocity) * (35 - air_temp))

        # 热损失计算
        hl1 = 3.05 * 0.001 * (5733 - 6.99 * m - pa)
        hl2 = 0.42 * (m - 58.15)
        hl3 = 1.7e-5 * m * (5867 - pa)
        hl4 = 0.0014 * m * (34 - air_temp)
        hl5 = 3.96e-8 * fcl * ((tcl + 273)**4 - (mean_radiant_temp + 273)**4)
        hl6 = fcl * air_velocity * 12.1 * np.sqrt(air_velocity) * (tcl - air_temp)

        ts = 0.303 * np.exp(-0.036 * m) + 0.028
        pmv = ts * (m - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)

        return pmv

    def generate_daily_report(self, simulation_results: pd.DataFrame) -> Dict:
        """生成每日能耗与舒适度报告"""
        temps = simulation_results['indoor_temp'].values

        # 计算舒适度
        pmv_values = [self.calculate_pmv(t, t) for t in temps]

        # 计算HVAC能耗 (简化)
        cooling_hours = sum(1 for t in temps if t > 26.5)
        hvac_energy = cooling_hours * self.model.hvac.cooling_capacity * 0.5

        return {
            'avg_indoor_temp': np.mean(temps),
            'max_indoor_temp': np.max(temps),
            'min_indoor_temp': np.min(temps),
            'temp_stability': np.std(temps),
            'comfort_hours': sum(1 for pmv in pmv_values if -0.5 <= pmv <= 0.5),
            'avg_pmv': np.mean(pmv_values),
            'hvac_energy_kwh': hvac_energy,
            'compliance_rate': sum(1 for pmv in pmv_values if -0.5 <= pmv <= 0.5) / len(pmv_values) * 100
        }


def analyze_thermal_bridges(bridges: List[ThermalBridge],
                           design_conditions: Dict) -> pd.DataFrame:
    """分析热桥结露风险"""
    results = []

    for bridge in bridges:
        risk = bridge.check_condensation_risk(
            design_conditions['indoor_temp'],
            design_conditions['outdoor_temp'],
            design_conditions['relative_humidity']
        )

        results.append({
            'name': bridge.name,
            'psi_value': bridge.psi_value,
            'surface_temp': risk['surface_temp'],
            'dew_point': risk['dew_point'],
            'margin': risk['margin'],
            'risk_level': risk['risk_level']
        })

    return pd.DataFrame(results)


# 使用示例
if __name__ == "__main__":
    # 创建建筑模型
    envelope = BuildingEnvelope()
    hvac = HVACSystem()
    building = BuildingThermalModel(envelope, hvac)

    # 模拟一天
    outdoor_temps = [22, 21, 20, 19, 19, 20, 22, 25, 28, 30,
                     32, 33, 34, 33, 32, 31, 30, 28, 26, 25, 24, 23, 22, 22]
    solar_gains = [0, 0, 0, 0, 0, 100, 500, 2000, 4000, 6000,
                   8000, 10000, 9000, 7000, 5000, 3000, 1500, 500, 100, 0, 0, 0, 0, 0]
    occupancy = [0, 0, 0, 0, 0, 0, 10, 50, 200, 300,
                400, 450, 400, 400, 380, 350, 200, 100, 50, 20, 10, 5, 0, 0]

    results = building.simulate_day(outdoor_temps, solar_gains, occupancy)

    print("=== 建筑热过程模拟结果 ===")
    print(results[['hour', 'indoor_temp', 'outdoor_temp']].to_string(index=False))

    # 能源管理系统
    ems = EnergyManagementSystem(building)
    report = ems.generate_daily_report(results)

    print("\n=== 每日能耗与舒适度报告 ===")
    for key, value in report.items():
        print(f"{key}: {value:.2f}")

    # 热桥分析
    print("\n=== 热桥结露风险分析 ===")
    bridges = [
        ThermalBridge("幕墙连接", 0.12, 500),
        ThermalBridge("窗框", 0.08, 800),
        ThermalBridge("阳台板", 0.15, 200)
    ]

    design_conditions = {
        'indoor_temp': 20.0,
        'outdoor_temp': -5.0,
        'relative_humidity': 50.0
    }

    bridge_analysis = analyze_thermal_bridges(bridges, design_conditions)
    print(bridge_analysis.to_string(index=False))
```

### 4.5 效果评估

**性能指标**：

| 指标             | 设计目标     | 实际达成   | 达标情况 |
| ---------------- | ------------ | ---------- | -------- |
| 年均能耗         | <100 kWh/m² | 88 kWh/m² | ✅ 达标  |
| PMV舒适度        | -0.5~+0.5    | -0.3~+0.4  | ✅ 达标  |
| 热桥表面温度裕量 | >2°C        | 4.5°C     | ✅ 达标  |
| 空调系统COP      | >4.5         | 5.2        | ✅ 达标  |
| 负荷预测准确率   | >90%         | 93%        | ✅ 达标  |

**业务价值**：

1. **能耗成本节约**：

   - 较同类建筑节能41%，年节约电费 **285万元**
   - 获得LEED铂金级认证，物业溢价15%，租金收入增加 **420万元/年**
   - 政府节能补贴 **180万元**
2. **运营效率提升**：

   - 热舒适度投诉减少85%，物业满意度提升至92%
   - 预测性维护降低设备故障率60%，维护成本节约 **60万元/年**
   - HVAC系统自动优化，运维人力减少30%
3. **环境价值**：

   - 年减少CO₂排放 **1,850吨**
   - 获得绿色建筑三星认证，品牌价值提升
4. **投资回报**：

   - 增量投资：450万元（高性能围护结构、智能控制系统）
   - 年度综合收益：945万元
   - **ROI = 110%，投资回收期4.8年**

**经验教训**：

1. **技术层面**：

   - 建筑热惰性是双刃剑，合理利用可实现负荷削峰填谷，但控制不当会导致温度波动
   - 热桥分析应在设计初期进行，后期改造困难且成本高昂
   - occupants 行为对能耗影响巨大，需加强用户教育与系统自适应
2. **管理层面**：

   - 建立设计-施工-运维闭环反馈机制，实际运行数据反哺设计优化
   - 与物业运营团队紧密配合，确保节能策略落地执行
3. **改进方向**：

   - 引入数字孪生技术，实现建筑能源系统实时仿真与优化
   - 探索需求响应，参与电网调峰获得额外收益
   - 集成可再生能源，目标实现近零能耗建筑

---

## 5. 案例4：制造业热学数据存储与分析系统

### 5.1 业务背景

**企业背景**：

- **公司名称**：精工电子制造股份有限公司
- **行业领域**：消费电子代工制造（SMT、半导体封装）
- **生产规模**：12条SMT产线，日产PCBA 50万片
- **热管理需求**：回流焊、波峰焊、老化测试等环节温度控制严格

**业务痛点**：

1. **数据孤岛严重**：各生产设备温度数据分散存储，格式不一，难以统一分析
2. **质量追溯困难**：产品热历史无法完整追溯，质量问题根因分析耗时数周
3. **工艺优化滞后**：缺乏热过程大数据分析能力，工艺参数优化依赖经验
4. **设备预测性维护缺失**：加热设备故障多为突发，平均停机时间4小时/次

**业务目标**：

- 建立统一热学数据平台，整合全厂温度相关数据
- 实现产品热历史全追溯，质量根因分析时间缩短至2小时
- 基于大数据分析优化回流焊温度曲线，提升一次通过率3%
- 建立设备热状态预测模型，将计划外停机减少70%

### 5.2 技术挑战

1. **海量时序数据处理**：单条SMT产线每天产生10GB温度数据，需高效存储与查询
2. **多源异构数据融合**：PLC、温度记录仪、红外热像仪、MES系统数据格式各异
3. **实时流处理需求**：关键工艺参数需实时监控，延迟需<1秒
4. **复杂关联分析**：需关联温度数据与质量数据、设备参数、环境条件
5. **边缘计算与云端协同**：产线级实时控制需边缘计算，全局优化需云端分析

### 5.3 Schema定义

**热学数据存储Schema**：

```dsl
schema ThermalDataStorage {
  measurement: {
    timestamp: DateTime
    device_id: String
    sensor_id: String
    temperature: Float64 @unit("°C")
    temperature_unit: Enum { Celsius, Fahrenheit, Kelvin }
    quality_code: Enum { Good, Uncertain, Bad }
  }

  equipment: {
    equipment_id: String
    equipment_type: Enum { Reflow_Oven, Wave_Soldering, Tester }
    location: String
    installed_date: Date
  }

  process_context: {
    product_id: String
    lot_number: String
    process_step: String
    recipe_id: String
    ambient_temperature: Float64 @unit("°C")
    ambient_humidity: Float64 @unit("%RH")
  }
} @standard("IEC_60335-1")
```

### 5.4 Python代码实现

```python
"""
制造业热学数据存储与分析系统
包含：时序数据库存储、数据ETL、热过程分析、质量追溯、设备预测维护
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import sqlite3
from pathlib import Path
import hashlib
from collections import defaultdict


class QualityCode(Enum):
    """数据质量代码"""
    GOOD = "Good"
    UNCERTAIN = "Uncertain"
    BAD = "Bad"


class EquipmentType(Enum):
    """设备类型"""
    REFLOW_OVEN = "Reflow_Oven"
    WAVE_SOLDERING = "Wave_Soldering"
    TESTER = "Tester"
    THERMAL_CHAMBER = "Thermal_Chamber"


@dataclass
class ThermalMeasurement:
    """温度测量数据点"""
    timestamp: datetime
    device_id: str
    sensor_id: str
    temperature: float
    unit: str = "Celsius"
    quality: QualityCode = QualityCode.GOOD

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'device_id': self.device_id,
            'sensor_id': self.sensor_id,
            'temperature': self.temperature,
            'unit': self.unit,
            'quality': self.quality.value
        }


@dataclass
class ProcessContext:
    """工艺上下文信息"""
    product_id: str
    lot_number: str
    process_step: str
    recipe_id: str
    ambient_temp: float = 25.0
    ambient_humidity: float = 50.0
    operator_id: str = ""

    def generate_trace_id(self) -> str:
        """生成唯一追溯ID"""
        content = f"{self.lot_number}_{self.process_step}_{self.product_id}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


class ThermalDatabase:
    """热学数据存储管理"""

    def __init__(self, db_path: str = "thermal_data.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()

    def _init_database(self):
        """初始化数据库表结构"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # 温度测量数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                device_id TEXT NOT NULL,
                sensor_id TEXT NOT NULL,
                temperature REAL NOT NULL,
                unit TEXT DEFAULT 'Celsius',
                quality TEXT DEFAULT 'Good',
                trace_id TEXT,
                INDEX idx_timestamp (timestamp),
                INDEX idx_device (device_id),
                INDEX idx_trace (trace_id)
            )
        ''')

        # 工艺上下文表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_context (
                trace_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                lot_number TEXT NOT NULL,
                process_step TEXT NOT NULL,
                recipe_id TEXT,
                ambient_temp REAL,
                ambient_humidity REAL,
                operator_id TEXT,
                start_time TEXT,
                end_time TEXT
            )
        ''')

        # 设备信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                device_id TEXT PRIMARY KEY,
                device_name TEXT,
                equipment_type TEXT,
                location TEXT,
                installed_date TEXT,
                max_temp REAL,
                min_temp REAL
            )
        ''')

        self.conn.commit()

    def insert_measurement(self, measurement: ThermalMeasurement,
                          trace_id: Optional[str] = None):
        """插入温度测量数据"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO measurements
            (timestamp, device_id, sensor_id, temperature, unit, quality, trace_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            measurement.timestamp.isoformat(),
            measurement.device_id,
            measurement.sensor_id,
            measurement.temperature,
            measurement.unit,
            measurement.quality.value,
            trace_id
        ))
        self.conn.commit()

    def insert_process_context(self, context: ProcessContext) -> str:
        """插入工艺上下文，返回trace_id"""
        trace_id = context.generate_trace_id()
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO process_context
            (trace_id, product_id, lot_number, process_step, recipe_id,
             ambient_temp, ambient_humidity, operator_id, start_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trace_id, context.product_id, context.lot_number,
            context.process_step, context.recipe_id,
            context.ambient_temp, context.ambient_humidity,
            context.operator_id, datetime.now().isoformat()
        ))
        self.conn.commit()
        return trace_id

    def query_temperature_history(self, device_id: str,
                                  start: datetime,
                                  end: datetime) -> pd.DataFrame:
        """查询设备温度历史"""
        query = '''
            SELECT timestamp, sensor_id, temperature, quality
            FROM measurements
            WHERE device_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        '''
        df = pd.read_sql_query(query, self.conn,
                               params=(device_id, start.isoformat(), end.isoformat()))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def query_by_trace_id(self, trace_id: str) -> pd.DataFrame:
        """通过追溯ID查询完整热历史"""
        query = '''
            SELECT m.*, p.product_id, p.lot_number, p.process_step
            FROM measurements m
            JOIN process_context p ON m.trace_id = p.trace_id
            WHERE m.trace_id = ?
            ORDER BY m.timestamp
        '''
        return pd.read_sql_query(query, self.conn, params=(trace_id,))


class ReflowProfileAnalyzer:
    """回流焊温度曲线分析器"""

    def __init__(self):
        # 典型无铅回流焊规格
        self.spec = {
            'preheat_rate': (1.0, 3.0),      # °C/s
            'soak_temp': (150, 180),          # °C
            'soak_time': (60, 120),           # s
            'peak_temp': (235, 245),          # °C
            'peak_time': (20, 40),            # s above 220°C
            'cooling_rate': (1.0, 4.0)        # °C/s
        }

    def analyze_profile(self, times: np.ndarray,
                       temperatures: np.ndarray) -> Dict:
        """分析回流焊温度曲线"""
        results = {}

        # 1. 预热斜率 (室温到150°C)
        preheat_idx = np.where(temperatures >= 150)[0]
        if len(preheat_idx) > 0:
            t_start = times[0]
            t_150 = times[preheat_idx[0]]
            temp_diff = 150 - temperatures[0]
            time_diff = t_150 - t_start
            results['preheat_rate'] = temp_diff / time_diff if time_diff > 0 else 0

        # 2. 浸泡区
        soak_idx = np.where((temperatures >= 150) & (temperatures <= 180))[0]
        if len(soak_idx) > 0:
            results['soak_time'] = times[soak_idx[-1]] - times[soak_idx[0]]
            results['soak_temp_avg'] = np.mean(temperatures[soak_idx])

        # 3. 峰值温度和液相线以上时间
        peak_idx = np.argmax(temperatures)
        results['peak_temp'] = temperatures[peak_idx]
        results['peak_time'] = times[peak_idx]

        above_liquidus = np.where(temperatures >= 220)[0]
        if len(above_liquidus) > 0:
            results['time_above_liquidus'] = (times[above_liquidus[-1]] -
                                              times[above_liquidus[0]])

        # 4. 冷却斜率
        cooling_idx = np.where(temperatures < temperatures[peak_idx] - 10)[0]
        if len(cooling_idx) > 0 and cooling_idx[-1] > peak_idx:
            cool_start = peak_idx
            cool_end = cooling_idx[-1]
            temp_drop = temperatures[cool_start] - temperatures[cool_end]
            time_span = times[cool_end] - times[cool_start]
            results['cooling_rate'] = temp_drop / time_span if time_span > 0 else 0

        # 规格符合性检查
        results['compliance'] = self._check_compliance(results)

        return results

    def _check_compliance(self, results: Dict) -> Dict[str, Any]:
        """检查是否符合规格"""
        compliance = {}

        if 'preheat_rate' in results:
            rate = results['preheat_rate']
            compliance['preheat_rate'] = {
                'value': rate,
                'pass': self.spec['preheat_rate'][0] <= rate <= self.spec['preheat_rate'][1]
            }

        if 'peak_temp' in results:
            temp = results['peak_temp']
            compliance['peak_temp'] = {
                'value': temp,
                'pass': self.spec['peak_temp'][0] <= temp <= self.spec['peak_temp'][1]
            }

        if 'time_above_liquidus' in results:
            t = results['time_above_liquidus']
            compliance['time_above_liquidus'] = {
                'value': t,
                'pass': self.spec['peak_time'][0] <= t <= self.spec['peak_time'][1]
            }

        compliance['overall'] = all(c.get('pass', True) for c in compliance.values())
        return compliance


class ThermalQualityTraceability:
    """热质量追溯系统"""

    def __init__(self, db: ThermalDatabase):
        self.db = db

    def trace_product_thermal_history(self, product_id: str) -> Dict:
        """追溯产品完整热历史"""
        # 查询所有相关批次
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT trace_id, lot_number, process_step, start_time
            FROM process_context
            WHERE product_id = ?
            ORDER BY start_time
        ''', (product_id,))

        processes = cursor.fetchall()

        thermal_history = []
        for trace_id, lot, step, start in processes:
            # 获取该工序的温度数据
            df = self.db.query_by_trace_id(trace_id)

            if not df.empty:
                thermal_history.append({
                    'process_step': step,
                    'lot_number': lot,
                    'start_time': start,
                    'sensor_count': df['sensor_id'].nunique(),
                    'temp_min': df['temperature'].min(),
                    'temp_max': df['temperature'].max(),
                    'temp_mean': df['temperature'].mean(),
                    'temp_std': df['temperature'].std(),
                    'quality_issues': len(df[df['quality'] != 'Good'])
                })

        return {
            'product_id': product_id,
            'process_count': len(thermal_history),
            'thermal_history': thermal_history
        }

    def analyze_quality_correlation(self, defect_product_ids: List[str],
                                    good_product_ids: List[str]) -> Dict:
        """分析温度与质量缺陷相关性"""
        defect_profiles = []
        good_profiles = []

        analyzer = ReflowProfileAnalyzer()

        for pid in defect_product_ids[:50]:  # 限制样本量
            history = self.trace_product_thermal_history(pid)
            for process in history['thermal_history']:
                if process['process_step'] == 'Reflow':
                    defect_profiles.append(process)

        for pid in good_product_ids[:50]:
            history = self.trace_product_thermal_history(pid)
            for process in history['thermal_history']:
                if process['process_step'] == 'Reflow':
                    good_profiles.append(process)

        # 统计分析
        defect_peak_temps = [p['temp_max'] for p in defect_profiles if 'temp_max' in p]
        good_peak_temps = [p['temp_max'] for p in good_profiles if 'temp_max' in p]

        return {
            'defect_sample_count': len(defect_profiles),
            'good_sample_count': len(good_profiles),
            'defect_avg_peak_temp': np.mean(defect_peak_temps) if defect_peak_temps else 0,
            'good_avg_peak_temp': np.mean(good_peak_temps) if good_peak_temps else 0,
            'correlation_detected': abs(np.mean(defect_peak_temps) - np.mean(good_peak_temps)) > 5 if defect_peak_temps and good_peak_temps else False
        }


class EquipmentHealthMonitor:
    """设备热健康状态监测"""

    def __init__(self, db: ThermalDatabase):
        self.db = db
        self.baseline_stats = {}

    def establish_baseline(self, device_id: str,
                          days_of_history: int = 30):
        """建立设备热特性基线"""
        end = datetime.now()
        start = end - timedelta(days=days_of_history)

        df = self.db.query_temperature_history(device_id, start, end)

        if df.empty:
            return

        # 按传感器分组统计
        for sensor_id, group in df.groupby('sensor_id'):
            self.baseline_stats[f"{device_id}_{sensor_id}"] = {
                'mean': group['temperature'].mean(),
                'std': group['temperature'].std(),
                'max': group['temperature'].max(),
                'min': group['temperature'].min(),
                'q99': group['temperature'].quantile(0.99)
            }

    def detect_anomalies(self, device_id: str,
                        recent_data: pd.DataFrame) -> List[Dict]:
        """检测热异常"""
        anomalies = []

        for sensor_id, group in recent_data.groupby('sensor_id'):
            key = f"{device_id}_{sensor_id}"
            if key not in self.baseline_stats:
                continue

            baseline = self.baseline_stats[key]
            recent_mean = group['temperature'].mean()
            recent_max = group['temperature'].max()

            # 规则1: 平均温度超过基线2个标准差
            if abs(recent_mean - baseline['mean']) > 2 * baseline['std']:
                anomalies.append({
                    'sensor_id': sensor_id,
                    'type': 'TEMPERATURE_DRIFT',
                    'severity': 'WARNING' if abs(recent_mean - baseline['mean']) < 3 * baseline['std'] else 'CRITICAL',
                    'value': recent_mean,
                    'expected': baseline['mean'],
                    'deviation': recent_mean - baseline['mean']
                })

            # 规则2: 温度超过历史最大值
            if recent_max > baseline['max'] * 1.05:
                anomalies.append({
                    'sensor_id': sensor_id,
                    'type': 'OVERTEMPERATURE',
                    'severity': 'CRITICAL',
                    'value': recent_max,
                    'threshold': baseline['max']
                })

            # 规则3: 温度波动异常增大
            recent_std = group['temperature'].std()
            if recent_std > baseline['std'] * 2:
                anomalies.append({
                    'sensor_id': sensor_id,
                    'type': 'INSTABILITY',
                    'severity': 'WARNING',
                    'value': recent_std,
                    'expected': baseline['std']
                })

        return anomalies

    def predict_maintenance(self, device_id: str) -> Dict:
        """预测性维护建议"""
        # 获取最近一周数据
        end = datetime.now()
        start = end - timedelta(days=7)
        df = self.db.query_temperature_history(device_id, start, end)

        if df.empty:
            return {'status': 'NO_DATA'}

        anomalies = self.detect_anomalies(device_id, df)

        # 简单规则：如果检测到多个传感器异常，建议维护
        critical_count = sum(1 for a in anomalies if a['severity'] == 'CRITICAL')
        warning_count = len(anomalies) - critical_count

        if critical_count >= 2:
            status = 'MAINTENANCE_REQUIRED'
            urgency = 'HIGH'
        elif critical_count >= 1 or warning_count >= 3:
            status = 'MONITOR_CLOSELY'
            urgency = 'MEDIUM'
        elif warning_count >= 1:
            status = 'NORMAL'
            urgency = 'LOW'
        else:
            status = 'HEALTHY'
            urgency = 'NONE'

        return {
            'device_id': device_id,
            'status': status,
            'urgency': urgency,
            'anomaly_count': len(anomalies),
            'anomalies': anomalies[:5],  # 只返回前5个
            'recommended_action': self._get_recommendation(status)
        }

    def _get_recommendation(self, status: str) -> str:
        """生成维护建议"""
        recommendations = {
            'MAINTENANCE_REQUIRED': '建议立即安排停机检修，检查加热元件和传感器',
            'MONITOR_CLOSELY': '加强监测频率，建议下次计划维护时重点检查',
            'NORMAL': '正常运行，按常规计划维护',
            'HEALTHY': '设备状态良好，无需特别处理'
        }
        return recommendations.get(status, '未知状态')


class ThermalETL:
    """热学数据ETL处理器"""

    def __init__(self, db: ThermalDatabase):
        self.db = db

    def parse_plc_data(self, raw_data: bytes, device_id: str) -> List[ThermalMeasurement]:
        """解析PLC原始数据（简化示例）"""
        measurements = []

        # 假设数据格式: timestamp(8bytes) + sensor_id(2bytes) + temp(4bytes)
        # 实际实现需根据具体PLC协议
        chunk_size = 14
        for i in range(0, len(raw_data), chunk_size):
            chunk = raw_data[i:i+chunk_size]
            if len(chunk) < chunk_size:
                break

            # 解析（示例）
            timestamp = datetime.fromtimestamp(int.from_bytes(chunk[0:8], 'big') / 1000)
            sensor_id = f"S{int.from_bytes(chunk[8:10], 'big')}"
            temp = int.from_bytes(chunk[10:14], 'big') / 100.0

            measurements.append(ThermalMeasurement(
                timestamp=timestamp,
                device_id=device_id,
                sensor_id=sensor_id,
                temperature=temp
            ))

        return measurements

    def transform_and_load(self, measurements: List[ThermalMeasurement],
                          context: Optional[ProcessContext] = None):
        """转换并加载数据"""
        trace_id = None
        if context:
            trace_id = self.db.insert_process_context(context)

        for m in measurements:
            # 数据清洗
            if m.temperature < -50 or m.temperature > 500:
                m.quality = QualityCode.BAD
            elif abs(m.temperature - 25) > 200:
                m.quality = QualityCode.UNCERTAIN

            self.db.insert_measurement(m, trace_id)


# 使用示例
if __name__ == "__main__":
    # 初始化数据库
    db = ThermalDatabase("manufacturing_thermal.db")

    # 创建设备
    cursor = db.conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO equipment
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   ('REFLOW_01', '回流焊炉1号', 'Reflow_Oven', 'SMT_A线',
                    '2023-01-15', 280, 20))
    db.conn.commit()

    # 生成模拟数据
    etl = ThermalETL(db)
    context = ProcessContext(
        product_id='PCBA_001',
        lot_number='LOT2024021501',
        process_step='Reflow',
        recipe_id='RECIPE_LF_01'
    )

    # 模拟回流焊温度曲线
    times = np.linspace(0, 300, 300)  # 5分钟，每秒一个点
    temperatures = (25 + 1.5 * np.clip(times, 0, 100) +  # 预热
                   20 * np.sin(np.clip(times - 100, 0, 60) * np.pi / 60) +  # 浸泡
                   80 * np.exp(-((times - 180)**2) / 800) +  # 峰值
                   np.random.normal(0, 1, 300))

    measurements = []
    base_time = datetime.now() - timedelta(minutes=5)
    for i, (t, temp) in enumerate(zip(times, temperatures)):
        measurements.append(ThermalMeasurement(
            timestamp=base_time + timedelta(seconds=i),
            device_id='REFLOW_01',
            sensor_id='ZONE_1',
            temperature=temp
        ))

    etl.transform_and_load(measurements, context)

    # 分析回流焊曲线
    analyzer = ReflowProfileAnalyzer()
    profile = analyzer.analyze_profile(times, temperatures)
    print("=== 回流焊曲线分析 ===")
    print(json.dumps(profile, indent=2, default=str))

    # 质量追溯
    tracer = ThermalQualityTraceability(db)
    history = tracer.trace_product_thermal_history('PCBA_001')
    print("\n=== 产品热历史追溯 ===")
    print(json.dumps(history, indent=2, default=str))

    # 设备健康监测
    monitor = EquipmentHealthMonitor(db)
    monitor.establish_baseline('REFLOW_01', days_of_history=7)

    # 生成最近数据用于异常检测
    recent_df = db.query_temperature_history(
        'REFLOW_01',
        datetime.now() - timedelta(hours=1),
        datetime.now()
    )

    if not recent_df.empty:
        anomalies = monitor.detect_anomalies('REFLOW_01', recent_df)
        print(f"\n=== 异常检测结果 ===")
        print(f"发现 {len(anomalies)} 个异常")

        # 维护预测
        maintenance = monitor.predict_maintenance('REFLOW_01')
        print(f"\n=== 维护预测 ===")
        print(json.dumps(maintenance, indent=2, default=str))
```

### 5.5 效果评估

**性能指标**：

| 指标             | 改进前   | 改进后     | 提升幅度 |
| ---------------- | -------- | ---------- | -------- |
| 数据查询响应时间 | 30-60秒  | <2秒       | 提升97%  |
| 质量追溯时间     | 2-3周    | 1.5小时    | 提升99%  |
| 回流焊一次通过率 | 96.5%    | 99.2%      | 提升2.7% |
| 设备计划外停机   | 4小时/月 | 0.9小时/月 | 降低78%  |
| 温度异常检出率   | 65%      | 94%        | 提升45%  |

**业务价值**：

1. **质量成本节约**：

   - 一次通过率提升2.7%，年减少返工成本 **420万元**
   - 质量追溯效率提升，客户投诉处理成本降低 **80万元/年**
   - 热过程数据支撑质量改进，客户退货率降低60%
2. **生产效率提升**：

   - 设备停机时间减少78%，产能损失减少 **350万元/年**
   - 温度曲线优化缩短工艺调试时间50%，新产品导入加速
   - 自动化数据收集节约人工记录成本 **40万元/年**
3. **管理决策支持**：

   - 建立热学知识库，工艺参数优化有据可依
   - 设备健康度量化，维修计划科学制定
   - 支持质量审计，客户审核通过率100%
4. **投资回报**：

   - 项目总投资：280万元（数据库、软件开发、硬件升级）
   - 年度综合收益：890万元
   - **ROI = 218%，投资回收期3.8个月**

**经验教训**：

1. **技术层面**：

   - 时序数据库选型至关重要，InfluxDB/TimescaleDB在高写入场景下性能优于传统关系型数据库
   - 边缘计算节点需具备数据缓存能力，防止网络中断导致数据丢失
   - 数据质量治理需前置，垃圾数据输入会导致分析结果严重偏差
2. **管理层面**：

   - 数据标准化是项目成功的基础，需统一传感器命名、单位、时间戳格式
   - 跨部门协作机制：IT、生产、质量部门需共同参与系统设计与验收
   - 用户培训不可忽视，一线操作工需理解数据的重要性
3. **改进方向**：

   - 引入机器学习进行温度曲线智能优化
   - 探索数字孪生，实现虚拟调试与预测性仿真
   - 与供应链系统对接，实现从原材料到成品的全链条热追溯

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2026-02-15
