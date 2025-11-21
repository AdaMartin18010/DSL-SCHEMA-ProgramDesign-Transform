# 物理设备电气Schema转换体系

## 📑 目录

- [物理设备电气Schema转换体系](#物理设备电气schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 电气特性转换](#2-电气特性转换)
    - [2.1 电压特性转换](#21-电压特性转换)
    - [2.2 电流特性转换](#22-电流特性转换)
    - [2.3 功率特性转换](#23-功率特性转换)
    - [2.4 绝缘特性转换](#24-绝缘特性转换)
  - [3. 转换实例](#3-转换实例)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 参考文献](#6-参考文献)
    - [6.1 标准文档](#61-标准文档)
    - [6.2 技术文档](#62-技术文档)

---

## 1. 转换体系概述

物理设备电气Schema转换体系支持将电气Schema
转换为多种编程语言的电气特性监测和控制代码。

**转换目标**：

1. **Python**：电气特性监测代码
2. **C/C++**：嵌入式电气监测代码
3. **PLC代码**：IEC 61131-3代码
4. **数字孪生模型**：数字孪生电气模型

---

## 2. 电气特性转换

### 2.1 电压特性转换

**Schema到Python转换**：

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class ProtectionType(Enum):
    SHUTDOWN = "shutdown"
    CURRENT_LIMIT = "current_limit"
    VOLTAGE_CLAMP = "voltage_clamp"

@dataclass
class VoltageCharacteristics:
    """电压特性"""
    rated_voltage: float  # V
    voltage_range_min: float  # V
    voltage_range_max: float  # V
    tolerance: float = 5.0  # %
    overvoltage_threshold: Optional[float] = None  # V
    overvoltage_response_time: Optional[float] = None  # ms
    overvoltage_protection_type: Optional[ProtectionType] = None

    def check_voltage(self, voltage: float) -> tuple[bool, Optional[str]]:
        """检查电压是否在范围内"""
        min_voltage = self.rated_voltage * (1 - self.tolerance / 100)
        max_voltage = self.rated_voltage * (1 + self.tolerance / 100)

        if voltage < min_voltage:
            return False, f"电压过低: {voltage}V < {min_voltage}V"
        elif voltage > max_voltage:
            return False, f"电压过高: {voltage}V > {max_voltage}V"

        # 检查过压保护
        if self.overvoltage_threshold and voltage > self.overvoltage_threshold:
            return False, f"触发过压保护: {voltage}V > {self.overvoltage_threshold}V"

        return True, None

    def apply_protection(self, voltage: float) -> float:
        """应用过压保护"""
        if self.overvoltage_protection_type == ProtectionType.VOLTAGE_CLAMP:
            if self.overvoltage_threshold:
                return min(voltage, self.overvoltage_threshold)
        return voltage
```

### 2.2 电流特性转换

**Schema到Python转换**：

```python
@dataclass
class CurrentCharacteristics:
    """电流特性"""
    rated_current: float  # A
    current_range_min: float  # A
    current_range_max: float  # A
    overcurrent_threshold: Optional[float] = None  # A
    overcurrent_response_time: Optional[float] = None  # ms
    max_leakage_current: float = 0.5  # mA

    def check_current(self, current: float) -> tuple[bool, Optional[str]]:
        """检查电流是否在范围内"""
        if current < self.current_range_min:
            return False, f"电流过低: {current}A < {self.current_range_min}A"
        elif current > self.current_range_max:
            return False, f"电流过高: {current}A > {self.current_range_max}A"

        # 检查过流保护
        if self.overcurrent_threshold and current > self.overcurrent_threshold:
            return False, f"触发过流保护: {current}A > {self.overcurrent_threshold}A"

        return True, None

    def check_leakage_current(self, leakage: float) -> tuple[bool, Optional[str]]:
        """检查漏电流"""
        if leakage > self.max_leakage_current:
            return False, f"漏电流超标: {leakage}mA > {self.max_leakage_current}mA"
        return True, None
```

### 2.3 功率特性转换

**Schema到Python转换**：

```python
@dataclass
class PowerCharacteristics:
    """功率特性"""
    rated_power: float  # W
    power_range_min: float  # W
    power_range_max: float  # W
    nominal_efficiency: float  # %
    power_factor: float = 1.0

    def calculate_power(self, voltage: float, current: float) -> float:
        """计算功率"""
        return voltage * current * self.power_factor

    def calculate_efficiency(self, input_power: float, output_power: float) -> float:
        """计算效率"""
        if input_power == 0:
            return 0.0
        return (output_power / input_power) * 100

    def check_power(self, power: float) -> tuple[bool, Optional[str]]:
        """检查功率是否在范围内"""
        if power < self.power_range_min:
            return False, f"功率过低: {power}W < {self.power_range_min}W"
        elif power > self.power_range_max:
            return False, f"功率过高: {power}W > {self.power_range_max}W"
        return True, None
```

### 2.4 绝缘特性转换

**Schema到Python转换**：

```python
from enum import Enum

class InsulationClass(Enum):
    CLASS_I = "Class_I"
    CLASS_II = "Class_II"
    CLASS_III = "Class_III"

@dataclass
class InsulationCharacteristics:
    """绝缘特性"""
    insulation_class: InsulationClass
    min_insulation_resistance: float  # MΩ
    dielectric_withstand_voltage: float  # V
    min_creepage_distance: float  # mm
    min_clearance_distance: float  # mm

    def check_insulation_resistance(self, resistance: float) -> tuple[bool, Optional[str]]:
        """检查绝缘电阻"""
        if resistance < self.min_insulation_resistance:
            return False, f"绝缘电阻不足: {resistance}MΩ < {self.min_insulation_resistance}MΩ"
        return True, None

    def perform_dielectric_test(self, test_voltage: float) -> tuple[bool, Optional[str]]:
        """执行耐压测试"""
        if test_voltage < self.dielectric_withstand_voltage:
            return False, f"测试电压不足: {test_voltage}V < {self.dielectric_withstand_voltage}V"
        return True, None
```

---

## 3. 转换实例

**完整电气Schema转换示例**：

```python
# Schema定义的电气特性转换为Python代码
class ElectricalDeviceMonitor:
    """电气设备监测器"""

    def __init__(self, voltage_spec: VoltageCharacteristics,
                 current_spec: CurrentCharacteristics,
                 power_spec: PowerCharacteristics,
                 insulation_spec: InsulationCharacteristics):
        self.voltage_spec = voltage_spec
        self.current_spec = current_spec
        self.power_spec = power_spec
        self.insulation_spec = insulation_spec

    def monitor(self, voltage: float, current: float) -> dict:
        """监测电气参数"""
        results = {}

        # 检查电压
        voltage_ok, voltage_msg = self.voltage_spec.check_voltage(voltage)
        results['voltage'] = {'ok': voltage_ok, 'message': voltage_msg}

        # 检查电流
        current_ok, current_msg = self.current_spec.check_current(current)
        results['current'] = {'ok': current_ok, 'message': current_msg}

        # 计算功率
        power = self.power_spec.calculate_power(voltage, current)
        power_ok, power_msg = self.power_spec.check_power(power)
        results['power'] = {'value': power, 'ok': power_ok, 'message': power_msg}

        return results
```

---

## 4. 转换工具

**工具列表**：

1. **代码生成器**：从Schema生成电气监测代码
2. **验证工具**：验证电气特性正确性
3. **测试工具**：电气特性测试工具

---

## 5. 转换验证

**验证方法**：

1. **语法验证**：验证代码语法
2. **语义验证**：验证电气逻辑语义
3. **标准合规性验证**：验证符合电气标准

---

## 6. 参考文献

### 6.1 标准文档

- IEC 60335-1:2020 Household and similar electrical appliances
- GB/T 19903 工业设备控制标准

### 6.2 技术文档

- 电气特性监测代码实现最佳实践

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
