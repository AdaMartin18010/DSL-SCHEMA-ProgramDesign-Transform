# 物理设备机械Schema转换体系

## 📑 目录

- [物理设备机械Schema转换体系](#物理设备机械schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 机械特性转换](#2-机械特性转换)
    - [2.1 结构特性转换](#21-结构特性转换)
    - [2.2 运动特性转换](#22-运动特性转换)
    - [2.3 材料特性转换](#23-材料特性转换)
    - [2.4 精度特性转换](#24-精度特性转换)
  - [3. 转换实例](#3-转换实例)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 参考文献](#6-参考文献)
    - [6.1 标准文档](#61-标准文档)
    - [6.2 技术文档](#62-技术文档)

---

## 1. 转换体系概述

物理设备机械Schema转换体系支持将机械Schema
转换为多种格式的机械设计代码和模型。

**转换目标**：

1. **CAD模型**：3D CAD模型文件
2. **运动控制代码**：运动控制程序代码
3. **有限元模型**：有限元分析模型
4. **数字孪生模型**：数字孪生机械模型

---

## 2. 机械特性转换

### 2.1 结构特性转换

**Schema到Python转换**：

```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class ConnectionType(Enum):
    THREADED = "threaded"
    WELDED = "welded"
    BOLTED = "bolted"
    SNAP_FIT = "snap_fit"

@dataclass
class Point3D:
    """三维点"""
    x: float
    y: float
    z: float

@dataclass
class Dimensions:
    """尺寸规格"""
    length: float  # mm
    width: float  # mm
    height: float  # mm
    tolerance: float = 0.1  # mm

@dataclass
class StructureCharacteristics:
    """结构特性"""
    dimensions: Dimensions
    max_weight: float  # kg
    center_of_gravity: Optional[Point3D] = None
    max_load: float  # N
    safety_factor: float = 2.0
    material_yield_strength: float  # MPa
    connection_type: ConnectionType = ConnectionType.BOLTED

    def calculate_safety_load(self) -> float:
        """计算安全载荷"""
        return self.max_load / self.safety_factor

    def check_dimensions(self, length: float, width: float, height: float) -> tuple[bool, Optional[str]]:
        """检查尺寸是否在范围内"""
        if abs(length - self.dimensions.length) > self.dimensions.tolerance:
            return False, f"长度超出公差: {length}mm"
        if abs(width - self.dimensions.width) > self.dimensions.tolerance:
            return False, f"宽度超出公差: {width}mm"
        if abs(height - self.dimensions.height) > self.dimensions.tolerance:
            return False, f"高度超出公差: {height}mm"
        return True, None
```

### 2.2 运动特性转换

**Schema到Python转换**：

```python
@dataclass
class MotionRange:
    """运动范围"""
    min_value: float  # mm
    max_value: float  # mm

@dataclass
class MotionCharacteristics:
    """运动特性"""
    x_range: MotionRange
    y_range: Optional[MotionRange] = None
    z_range: Optional[MotionRange] = None
    max_velocity: float  # mm/s
    acceleration: float  # mm/s²
    deceleration: float  # mm/s²
    positioning_accuracy: float  # mm
    repeatability: float  # mm
    resolution: float  # mm

    def check_position(self, x: float, y: Optional[float] = None,
                      z: Optional[float] = None) -> tuple[bool, Optional[str]]:
        """检查位置是否在范围内"""
        if x < self.x_range.min_value or x > self.x_range.max_value:
            return False, f"X轴位置超出范围: {x}mm"

        if y is not None and self.y_range:
            if y < self.y_range.min_value or y > self.y_range.max_value:
                return False, f"Y轴位置超出范围: {y}mm"

        if z is not None and self.z_range:
            if z < self.z_range.min_value or z > self.z_range.max_value:
                return False, f"Z轴位置超出范围: {z}mm"

        return True, None

    def calculate_move_time(self, distance: float) -> float:
        """计算移动时间"""
        # 简化的时间计算：加速+匀速+减速
        t_accel = self.max_velocity / self.acceleration
        t_decel = self.max_velocity / self.deceleration
        s_accel = 0.5 * self.acceleration * t_accel ** 2
        s_decel = 0.5 * self.deceleration * t_decel ** 2

        if s_accel + s_decel >= distance:
            # 三角形速度曲线
            t_total = (2 * distance / self.acceleration) ** 0.5
        else:
            # 梯形速度曲线
            s_const = distance - s_accel - s_decel
            t_const = s_const / self.max_velocity
            t_total = t_accel + t_const + t_decel

        return t_total
```

### 2.3 材料特性转换

**Schema到Python转换**：

```python
from enum import Enum

class MaterialType(Enum):
    STEEL = "steel"
    ALUMINUM = "aluminum"
    PLASTIC = "plastic"
    COMPOSITE = "composite"

class CorrosionRating(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class MaterialCharacteristics:
    """材料特性"""
    material_type: MaterialType
    yield_strength: float  # MPa
    tensile_strength: float  # MPa
    hardness: Optional[float] = None  # HRC
    corrosion_rating: CorrosionRating = CorrosionRating.GOOD
    min_temperature: float  # °C
    max_temperature: float  # °C
    density: float  # g/cm³

    def check_temperature(self, temperature: float) -> tuple[bool, Optional[str]]:
        """检查温度是否在范围内"""
        if temperature < self.min_temperature:
            return False, f"温度过低: {temperature}°C < {self.min_temperature}°C"
        elif temperature > self.max_temperature:
            return False, f"温度过高: {temperature}°C > {self.max_temperature}°C"
        return True, None

    def calculate_weight(self, volume: float) -> float:
        """计算重量"""
        return volume * self.density / 1000  # kg
```

### 2.4 精度特性转换

**Schema到Python转换**：

```python
@dataclass
class PrecisionCharacteristics:
    """精度特性"""
    positioning_accuracy: float  # mm
    repeatability: float  # mm
    resolution: float  # mm
    dimensional_tolerance: float = 0.1  # mm

    def check_accuracy(self, target_position: float,
                      actual_position: float) -> tuple[bool, float]:
        """检查定位精度"""
        error = abs(actual_position - target_position)
        is_accurate = error <= self.positioning_accuracy
        return is_accurate, error

    def check_repeatability(self, positions: List[float]) -> tuple[bool, float]:
        """检查重复精度"""
        if len(positions) < 2:
            return True, 0.0

        max_pos = max(positions)
        min_pos = min(positions)
        variation = max_pos - min_pos
        is_repeatable = variation <= self.repeatability
        return is_repeatable, variation
```

---

## 3. 转换实例

**完整机械Schema转换示例**：

```python
# Schema定义的机械特性转换为Python代码
class MechanicalDeviceModel:
    """机械设备模型"""

    def __init__(self, structure: StructureCharacteristics,
                 motion: MotionCharacteristics,
                 material: MaterialCharacteristics,
                 precision: PrecisionCharacteristics):
        self.structure = structure
        self.motion = motion
        self.material = material
        self.precision = precision

    def validate_design(self) -> dict:
        """验证设计"""
        results = {}

        # 验证结构强度
        safety_load = self.structure.calculate_safety_load()
        results['safety_load'] = safety_load

        # 验证运动范围
        motion_ok, motion_msg = self.motion.check_position(0, 0, 0)
        results['motion'] = {'ok': motion_ok, 'message': motion_msg}

        # 验证材料温度范围
        temp_ok, temp_msg = self.material.check_temperature(25.0)
        results['temperature'] = {'ok': temp_ok, 'message': temp_msg}

        return results
```

---

## 4. 转换工具

**工具列表**：

1. **CAD转换器**：从Schema生成CAD模型
2. **运动控制代码生成器**：生成运动控制代码
3. **有限元模型生成器**：生成有限元分析模型
4. **数字孪生模型生成器**：生成数字孪生模型

---

## 5. 转换验证

**验证方法**：

1. **语法验证**：验证代码语法
2. **语义验证**：验证机械逻辑语义
3. **标准合规性验证**：验证符合机械标准

---

## 6. 参考文献

### 6.1 标准文档

- ISO 9001:2015 Quality management systems
- GB/T 19903 工业设备控制标准

### 6.2 技术文档

- 机械特性设计代码实现最佳实践

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
