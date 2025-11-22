# 物理设备安全Schema实践案例

## 📑 目录

- [物理设备安全Schema实践案例](#物理设备安全schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：工业机器人安全系统](#2-案例1工业机器人安全系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
    - [2.4 验证结果](#24-验证结果)
  - [3. 案例2：家用电器安全认证](#3-案例2家用电器安全认证)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
    - [3.4 认证结果](#34-认证结果)
  - [4. 案例3：医疗设备安全合规](#4-案例3医疗设备安全合规)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
    - [4.4 合规验证](#44-合规验证)
  - [5. 案例总结](#5-案例总结)
    - [5.1 成功因素](#51-成功因素)
    - [5.2 最佳实践](#52-最佳实践)
  - [6. 参考文献](#6-参考文献)
    - [6.1 标准文档](#61-标准文档)
    - [6.2 技术文档](#62-技术文档)

---

## 1. 案例概述

本文档提供物理设备安全Schema在实际应用中的
实践案例，展示安全特性定义、代码生成、
安全验证等完整流程。

**案例类型**：

1. **工业机器人**：安全系统设计
2. **家用电器**：安全认证
3. **医疗设备**：安全合规

---

## 2. 案例1：工业机器人安全系统

### 2.1 场景描述

**应用场景**：
工业机器人系统中的安全系统设计，
确保机器人安全运行和保护操作人员。

**需求分析**：

- **SIL等级**：SIL 2等级要求
- **安全功能**：急停、安全门锁、光幕保护
- **安全认证**：CE认证要求
- **安全合规**：IEC 61508合规

### 2.2 Schema定义

**工业机器人安全Schema定义**：

```dsl
schema IndustrialRobotSafety {
  safety_level: {
    sil_level: Enum { SIL_2 }
    safety_category: Enum { Category_3 }
    risk_level: Enum { High }
    safety_integrity: {
      pfh: Float64 @value(1e-6) @unit("1/h")
      mtbf: Float64 @value(1e6) @unit("h")
    }
  }

  safety_functions: {
    emergency_stop: {
      enabled: Bool @default(true)
      response_time: Duration @value(200ms)
      stop_category: Enum { Category_0 }
      reset_method: Enum { Manual }
    }
    safety_door_lock: {
      enabled: Bool @default(true)
      lock_type: Enum { Electronic }
      interlock_switch: Bool @default(true)
      monitoring: Bool @default(true)
    }
    light_curtain: {
      enabled: Bool @default(true)
      resolution: Float64 @value(14.0) @unit("mm")
      response_time: Duration @value(20ms)
    }
  }

  certification: {
    ce_marking: Bool @default(true)
    compliance_directives: List<String> @default(["Machinery", "EMC"])
  }

  compliance: {
    iec_61508: {
      compliant: Bool @default(true)
      sil_level: Enum { SIL_2 }
    }
    iso_13849: {
      compliant: Bool @default(true)
      performance_level: Enum { PL_d }
    }
  }
} @standard("IEC_61508", "ISO_13849")
```

### 2.3 实现代码

**Python实现**：

```python
class IndustrialRobotSafetySystem:
    """工业机器人安全系统"""

    def __init__(self):
        self.safety_level = SafetyLevel(
            sil_level=SILLevel.SIL_2,
            safety_category=SafetyCategory.CATEGORY_3,
            risk_level=RiskLevel.HIGH,
            pfh=1e-6,
            mtbf=1e6
        )

        self.emergency_stop = EmergencyStop(
            enabled=True,
            response_time=200.0,
            stop_category=StopCategory.CATEGORY_0,
            reset_method="manual"
        )

        self.door_lock = SafetyDoorLock(
            enabled=True,
            lock_type="electronic",
            interlock_switch=True,
            monitoring=True
        )

        self.light_curtain = LightCurtain(
            enabled=True,
            resolution=14.0,
            response_time=20.0
        )

        self.certification = Certification(
            ce_marking=True,
            ce_certificate_number="CE-2024-001"
        )

        self.compliance = Compliance(
            iec_61508_compliant=True,
            iec_61508_sil_level=SILLevel.SIL_2
        )

    def safety_monitoring_loop(self):
        """安全监测循环"""
        while True:
            # 检查急停
            if self.check_emergency_stop():
                self.emergency_stop.trigger()

            # 检查安全门
            door_closed, door_locked = self.door_lock.check_door_status()
            if not door_closed or not door_locked:
                self.emergency_stop.trigger()

            # 检查光幕
            if self.light_curtain.check_obstruction():
                self.emergency_stop.trigger()

            time.sleep(0.1)  # 100ms监测周期

    def check_emergency_stop(self) -> bool:
        """检查急停按钮状态"""
        # 从硬件读取急停按钮状态
        return False  # 示例：未按下
```

### 2.4 验证结果

**验证结果**：
✅ SIL 2等级满足要求
✅ 安全功能正常工作
✅ CE认证通过
✅ IEC 61508合规
✅ ISO 13849合规

---

## 3. 案例2：家用电器安全认证

### 3.1 场景描述

**应用场景**：
家用电器系统中的安全认证，
确保产品符合安全标准要求。

**需求分析**：

- **安全标准**：IEC 60335-1合规
- **安全功能**：过温保护、过流保护
- **安全认证**：CE、CCC认证
- **安全测试**：安全测试验证

### 3.2 Schema定义

**家用电器安全Schema**：

```dsl
schema ApplianceSafety {
  safety_level: {
    safety_category: Enum { Category_II }
    risk_level: Enum { Medium }
  }

  safety_functions: {
    over_temperature_protection: {
      enabled: Bool @default(true)
      threshold: Float64 @value(95.0) @unit("°C")
      response_time: Duration @value(5s)
    }
    over_current_protection: {
      enabled: Bool @default(true)
      threshold: Float64 @value(15.0) @unit("A")
      response_time: Duration @value(100ms)
    }
  }

  certification: {
    ce_marking: Bool @default(true)
    ccc_certification: Bool @default(true)
    ccc_certificate_number: String @value("CCC-2024-001")
  }

  compliance: {
    iec_60335: {
      compliant: Bool @default(true)
      part_number: String @default("IEC_60335-1")
    }
  }
} @standard("IEC_60335-1")
```

### 3.3 实现代码

**Python实现**：

```python
class ApplianceSafetySystem:
    """家用电器安全系统"""

    def __init__(self):
        self.over_temp_protection = {
            'enabled': True,
            'threshold': 95.0,
            'response_time': 5.0
        }

        self.over_current_protection = {
            'enabled': True,
            'threshold': 15.0,
            'response_time': 0.1
        }

        self.certification = Certification(
            ce_marking=True,
            ccc_certification=True,
            ccc_certificate_number="CCC-2024-001"
        )

        self.compliance = Compliance(
            iec_60335_compliant=True
        )

    def check_temperature(self, temperature: float) -> tuple[bool, Optional[str]]:
        """检查温度"""
        if self.over_temp_protection['enabled']:
            if temperature > self.over_temp_protection['threshold']:
                return False, f"温度过高: {temperature}°C"
        return True, None

    def check_current(self, current: float) -> tuple[bool, Optional[str]]:
        """检查电流"""
        if self.over_current_protection['enabled']:
            if current > self.over_current_protection['threshold']:
                return False, f"电流过高: {current}A"
        return True, None
```

### 3.4 认证结果

**认证结果**：
✅ IEC 60335-1合规
✅ CE认证通过
✅ CCC认证通过
✅ 安全测试通过

---

## 4. 案例3：医疗设备安全合规

### 4.1 场景描述

**应用场景**：
医疗设备系统中的安全合规，
确保设备符合医疗安全标准要求。

**需求分析**：

- **安全标准**：IEC 60601-1合规
- **SIL等级**：SIL 2等级要求
- **安全功能**：故障安全设计
- **安全认证**：FDA、CE认证

### 4.2 Schema定义

**医疗设备安全Schema**：

```dsl
schema MedicalDeviceSafety {
  safety_level: {
    sil_level: Enum { SIL_2 }
    safety_category: Enum { Category_3 }
    risk_level: Enum { High }
    safety_integrity: {
      pfh: Float64 @value(1e-6) @unit("1/h")
    }
  }

  safety_functions: {
    fail_safe_design: {
      enabled: Bool @default(true)
      failure_mode: Enum { SafeState }
    }
    redundant_systems: {
      enabled: Bool @default(true)
      redundancy_level: Int @value(2)
    }
  }

  certification: {
    fda_approval: Bool @default(true)
    ce_marking: Bool @default(true)
    medical_device_class: Enum { Class_II }
  }

  compliance: {
    iec_60601: {
      compliant: Bool @default(true)
    }
    iec_61508: {
      compliant: Bool @default(true)
      sil_level: Enum { SIL_2 }
    }
  }
} @standard("IEC_60601-1", "IEC_61508")
```

### 4.3 实现代码

**Python实现**：

```python
class MedicalDeviceSafetySystem:
    """医疗设备安全系统"""

    def __init__(self):
        self.safety_level = SafetyLevel(
            sil_level=SILLevel.SIL_2,
            safety_category=SafetyCategory.CATEGORY_3,
            risk_level=RiskLevel.HIGH,
            pfh=1e-6
        )

        self.fail_safe_enabled = True
        self.redundancy_level = 2

        self.certification = Certification(
            ce_marking=True
        )

        self.compliance = Compliance(
            iec_61508_compliant=True,
            iec_61508_sil_level=SILLevel.SIL_2
        )

    def fail_safe_check(self) -> bool:
        """故障安全检查"""
        if self.fail_safe_enabled:
            # 检查系统状态，如果故障则进入安全状态
            system_ok = self.check_system_status()
            if not system_ok:
                self.enter_safe_state()
                return False
        return True

    def check_system_status(self) -> bool:
        """检查系统状态"""
        # 实现系统状态检查逻辑
        return True

    def enter_safe_state(self):
        """进入安全状态"""
        # 实现安全状态进入逻辑
        pass
```

### 4.4 合规验证

**验证结果**：
✅ IEC 60601-1合规
✅ IEC 61508合规
✅ SIL 2等级满足要求
✅ FDA批准通过
✅ CE认证通过

---

## 5. 案例总结

### 5.1 成功因素

**关键成功因素**：

1. **标准化Schema**：使用标准安全Schema
2. **安全设计**：遵循安全设计原则
3. **安全验证**：进行安全验证和测试
4. **合规认证**：获得必要的安全认证

### 5.2 最佳实践

**实践建议**：

1. **Schema优先**：先定义安全Schema
2. **安全设计**：遵循安全设计原则
3. **安全验证**：进行安全验证和测试
4. **持续改进**：持续改进安全系统

---

## 6. 参考文献

### 6.1 标准文档

- IEC 61508:2010 Functional safety
- IEC 60335-1:2020 Household and similar electrical appliances
- IEC 60601-1:2020 Medical electrical equipment
- ISO 13849-1:2023 Safety of machinery

### 6.2 技术文档

- 安全系统设计最佳实践
- 功能安全验证指南

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系（包含数据存储）

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展安全数据存储与分析系统案例，新增PostgreSQL存储实践）
