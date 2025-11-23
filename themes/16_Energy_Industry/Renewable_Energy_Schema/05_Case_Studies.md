# 可再生能源Schema实践案例

## 📑 目录

- [可再生能源Schema实践案例](#可再生能源schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：风电场监控系统](#2-案例1风电场监控系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：光伏电站管理系统](#3-案例2光伏电站管理系统)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：储能系统管理](#4-案例3储能系统管理)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：可再生能源数据分析和报表](#5-案例4可再生能源数据分析和报表)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)

---

## 1. 案例概述

本文档提供可再生能源Schema在实际应用中的实践案例。

---

## 2. 案例1：风电场监控系统

### 2.1 场景描述

**业务背景**：
风电场需要实时监控所有风力发电机组的运行状态，
采集性能数据，进行故障预警和性能分析。

**技术挑战**：

- 需要连接多个风机控制器
- 需要实时数据采集
- 需要故障检测和预警
- 需要性能分析和优化

**解决方案**：
使用WindTurbineDataCollector采集风机数据，
使用RenewableEnergyStorage存储数据，实现
实时监控和数据分析。

### 2.2 Schema定义

**风电场监控Schema**：

```json
{
  "wind_farm_id": "WF001",
  "wind_farm_name": "风电场A",
  "turbines": [
    {
      "turbine_id": "WT001",
      "turbine_name": "1号风机",
      "turbine_info": {
        "turbine_model": "WTG-2000",
        "manufacturer": "风机制造商",
        "rated_power": 2000.00,
        "rotor_diameter": 120.00,
        "hub_height": 100.00
      },
      "turbine_status": {
        "operational_status": "Running",
        "fault_status": "None",
        "maintenance_status": "None"
      },
      "turbine_performance": {
        "current_power": 1500.00,
        "wind_speed": 8.5,
        "rotor_speed": 15.2,
        "efficiency": 85.5
      }
    }
  ]
}
```

### 2.3 实现代码

**完整的风电场监控实现**：

```python
from wind_turbine_collector import WindTurbineDataCollector, WindTurbineDataConverter
from renewable_energy_storage import RenewableEnergyStorage
import time
from datetime import datetime

# 初始化存储
storage = RenewableEnergyStorage("postgresql://user:pass@localhost/renewable_energy")

# 配置风机列表
turbines_config = [
    {
        "turbine_id": "WT001",
        "turbine_name": "1号风机",
        "host": "192.168.1.101",
        "port": 502
    },
    {
        "turbine_id": "WT002",
        "turbine_name": "2号风机",
        "host": "192.168.1.102",
        "port": 502
    }
]

# 创建数据采集器和转换器
collectors = {}
converter = WindTurbineDataConverter()

# 连接所有风机
for turbine_config in turbines_config:
    collector = WindTurbineDataCollector(
        turbine_config["turbine_id"],
        turbine_config["host"],
        turbine_config["port"]
    )
    if collector.connect():
        collectors[turbine_config["turbine_id"]] = collector
        print(f"Connected to {turbine_config['turbine_name']}")

# 存储风机基本信息
for turbine_config in turbines_config:
    storage.store_wind_turbine({
        "turbine_id": turbine_config["turbine_id"],
        "turbine_name": turbine_config["turbine_name"],
        "turbine_model": "WTG-2000",
        "manufacturer": "风机制造商",
        "rated_power": 2000.00,
        "rotor_diameter": 120.00,
        "hub_height": 100.00,
        "installation_date": datetime.now().date()
    })

# 周期性数据采集
collection_interval = 5  # 秒
collection_duration = 300  # 秒

start_time = time.time()
while time.time() - start_time < collection_duration:
    for turbine_id, collector in collectors.items():
        # 读取状态
        status = collector.read_turbine_status()
        if status:
            storage.store_wind_turbine_status({
                "turbine_id": turbine_id,
                **status
            })

        # 读取性能数据
        performance = collector.read_turbine_performance()
        if performance:
            storage.store_wind_turbine_performance({
                "turbine_id": turbine_id,
                **performance
            })
            print(f"{datetime.now()}: {turbine_id} - Power: {performance['current_power']:.2f} kW, "
                  f"Wind: {performance['wind_speed']:.2f} m/s")

    time.sleep(collection_interval)

# 查询统计信息
for turbine_config in turbines_config:
    stats = storage.get_wind_turbine_statistics(turbine_config["turbine_id"], hours=1)
    print(f"\n{turbine_config['turbine_name']} Statistics (last hour):")
    print(f"  Data points: {stats['data_count']}")
    print(f"  Avg power: {stats['avg_power']:.2f} kW")
    print(f"  Max power: {stats['max_power']:.2f} kW")
    print(f"  Avg efficiency: {stats['avg_efficiency']:.2f}%")
```

---

## 3. 案例2：光伏电站管理系统

### 3.1 场景描述

**业务背景**：
光伏电站需要管理多个逆变器，监控发电量，
分析系统效率，优化发电性能。

**技术挑战**：

- 需要连接多个逆变器
- 需要实时发电数据采集
- 需要环境数据采集
- 需要效率分析和优化

**解决方案**：
使用SolarSystemDataCollector采集光伏数据，
使用RenewableEnergyStorage存储数据，实现
发电量统计和效率分析。

### 3.2 Schema定义

**光伏电站管理Schema**：

```json
{
  "solar_farm_id": "SF001",
  "solar_farm_name": "光伏电站A",
  "systems": [
    {
      "system_id": "PV001",
      "system_name": "1号光伏系统",
      "pv_component_info": {
        "total_modules": 1000,
        "module_type": "Monocrystalline",
        "total_capacity": 500.00
      },
      "generation_data": {
        "dc_power": 450.00,
        "ac_power": 427.50,
        "system_efficiency": 95.00
      },
      "environmental_data": {
        "irradiance": 800.00,
        "ambient_temperature": 25.00,
        "module_temperature": 45.00
      }
    }
  ]
}
```

### 3.3 实现代码

**完整的光伏电站管理实现**：

```python
from solar_system_collector import SolarSystemDataCollector, SolarSystemDataConverter
from renewable_energy_storage import RenewableEnergyStorage
import time
from datetime import datetime

# 初始化存储
storage = RenewableEnergyStorage("postgresql://user:pass@localhost/renewable_energy")

# 配置光伏系统
systems_config = [
    {
        "system_id": "PV001",
        "system_name": "1号光伏系统",
        "inverter_hosts": ["192.168.2.101", "192.168.2.102"]
    },
    {
        "system_id": "PV002",
        "system_name": "2号光伏系统",
        "inverter_hosts": ["192.168.2.103", "192.168.2.104"]
    }
]

# 创建数据采集器
collectors = {}
converter = SolarSystemDataConverter()

# 连接所有系统
for system_config in systems_config:
    collector = SolarSystemDataCollector(
        system_config["system_id"],
        system_config["inverter_hosts"]
    )
    if collector.connect_all():
        collectors[system_config["system_id"]] = collector
        print(f"Connected to {system_config['system_name']}")

# 存储系统基本信息
for system_config in systems_config:
    storage.store_solar_system({
        "system_id": system_config["system_id"],
        "system_name": system_config["system_name"],
        "total_modules": 1000,
        "module_type": "Monocrystalline",
        "total_capacity": 500.00,
        "installation_date": datetime.now().date()
    })

# 周期性数据采集
collection_interval = 10  # 秒
collection_duration = 600  # 秒

start_time = time.time()
daily_generation = {}

while time.time() - start_time < collection_duration:
    for system_id, collector in collectors.items():
        # 读取发电数据
        generation = collector.read_generation_data()
        if generation:
            # 读取环境数据
            environmental = collector.read_environmental_data()

            # 计算日发电量（简化计算）
            if system_id not in daily_generation:
                daily_generation[system_id] = 0.0
            daily_generation[system_id] += generation["ac_power"] * (collection_interval / 3600.0)

            # 存储发电数据
            storage.store_solar_generation({
                "system_id": system_id,
                "dc_power": generation["dc_power"],
                "ac_power": generation["ac_power"],
                "daily_generation": daily_generation[system_id],
                "system_efficiency": generation["system_efficiency"],
                "irradiance": environmental["irradiance"] if environmental else None,
                "ambient_temperature": environmental["ambient_temperature"] if environmental else None
            })

            print(f"{datetime.now()}: {system_id} - AC Power: {generation['ac_power']:.2f} kW, "
                  f"Efficiency: {generation['system_efficiency']:.2f}%")

    time.sleep(collection_interval)

# 查询统计信息
for system_config in systems_config:
    stats = storage.get_solar_generation_statistics(system_config["system_id"], days=1)
    print(f"\n{system_config['system_name']} Statistics (last day):")
    print(f"  Data points: {stats['data_count']}")
    print(f"  Total generation: {stats['total_generation']:.2f} kWh")
    print(f"  Avg power: {stats['avg_power']:.2f} kW")
    print(f"  Avg efficiency: {stats['avg_efficiency']:.2f}%")
```

---

## 4. 案例3：储能系统管理

### 4.1 场景描述

**业务背景**：
储能系统需要实时监控电池状态，管理充放电过程，
确保系统安全和电池寿命。

**技术挑战**：

- 需要实时电池状态监测
- 需要充放电控制
- 需要安全保护
- 需要电池寿命管理

**解决方案**：
使用EnergyStorageDataCollector采集储能数据，
使用RenewableEnergyStorage存储数据，实现
状态监控和安全保护。

### 4.2 实现代码

**完整的储能系统管理实现**：

```python
from energy_storage_collector import EnergyStorageDataCollector
from renewable_energy_storage import RenewableEnergyStorage
import time
from datetime import datetime

# 初始化存储
storage = RenewableEnergyStorage("postgresql://user:pass@localhost/renewable_energy")

# 配置储能系统
storage_config = {
    "storage_id": "ESS001",
    "storage_name": "1号储能系统",
    "bms_host": "192.168.3.101",
    "port": 502
}

# 创建数据采集器
collector = EnergyStorageDataCollector(
    storage_config["storage_id"],
    storage_config["bms_host"],
    storage_config["port"]
)

if collector.connect():
    print(f"Connected to {storage_config['storage_name']}")

# 存储系统基本信息
storage.store_energy_storage({
    "storage_id": storage_config["storage_id"],
    "storage_name": storage_config["storage_name"],
    "battery_type": "LithiumIon",
    "battery_capacity": 1000.00,
    "rated_voltage": 400.00,
    "installation_date": datetime.now().date()
})

# 周期性数据采集
collection_interval = 5  # 秒
collection_duration = 300  # 秒

start_time = time.time()
while time.time() - start_time < collection_duration:
    # 读取电池状态
    battery_status = collector.read_battery_status()
    if battery_status:
        storage.store_storage_status({
            "storage_id": storage_config["storage_id"],
            **battery_status
        })

        print(f"{datetime.now()}: SOC: {battery_status['soc']:.2f}%, "
              f"SOH: {battery_status['soh']:.2f}%, "
              f"Voltage: {battery_status['voltage']:.2f}V")

        # 安全保护检查
        if battery_status["soc"] < 10:
            print("WARNING: Battery SOC is low!")
        if battery_status["temperature"] > 45:
            print("WARNING: Battery temperature is high!")

    # 读取充放电数据
    cd_data = collector.read_charge_discharge_data()
    if cd_data:
        print(f"  Charge: {cd_data['charge_power']:.2f} kW, "
              f"Discharge: {cd_data['discharge_power']:.2f} kW")

    # 读取BMS数据
    bms_data = collector.read_bms_data()
    if bms_data:
        if bms_data["protection_status"] != "Normal":
            print(f"WARNING: Protection status: {bms_data['protection_status']}")

    time.sleep(collection_interval)

# 查询统计信息
stats = storage.get_storage_statistics(storage_config["storage_id"], hours=1)
print(f"\n{storage_config['storage_name']} Statistics (last hour):")
print(f"  Data points: {stats['data_count']}")
print(f"  Avg SOC: {stats['avg_soc']:.2f}%")
print(f"  Avg SOH: {stats['avg_soh']:.2f}%")
print(f"  SOC range: {stats['min_soc']:.2f}% - {stats['max_soc']:.2f}%")
```

---

## 5. 案例4：可再生能源数据分析和报表

### 5.1 场景描述

**应用场景**：
使用PostgreSQL存储可再生能源数据，支持数据查询、
分析和报表生成。

### 5.2 实现代码

**完整的数据分析实现**：

```python
from renewable_energy_storage import RenewableEnergyStorage
from datetime import datetime, timedelta

storage = RenewableEnergyStorage("postgresql://user:pass@localhost/renewable_energy")

# 查询风机统计
turbine_id = "WT001"
wind_stats = storage.get_wind_turbine_statistics(turbine_id, hours=24)
print(f"Wind Turbine {turbine_id} Statistics (24h):")
print(f"  Avg power: {wind_stats['avg_power']:.2f} kW")
print(f"  Max power: {wind_stats['max_power']:.2f} kW")
print(f"  Avg efficiency: {wind_stats['avg_efficiency']:.2f}%")

# 查询光伏统计
system_id = "PV001"
solar_stats = storage.get_solar_generation_statistics(system_id, days=30)
print(f"\nSolar System {system_id} Statistics (30 days):")
print(f"  Total generation: {solar_stats['total_generation']:.2f} kWh")
print(f"  Avg power: {solar_stats['avg_power']:.2f} kW")
print(f"  Avg efficiency: {solar_stats['avg_efficiency']:.2f}%")

# 查询储能统计
storage_id = "ESS001"
storage_stats = storage.get_storage_statistics(storage_id, hours=24)
print(f"\nEnergy Storage {storage_id} Statistics (24h):")
print(f"  Avg SOC: {storage_stats['avg_soc']:.2f}%")
print(f"  Avg SOH: {storage_stats['avg_soh']:.2f}%")
print(f"  SOC range: {storage_stats['min_soc']:.2f}% - {storage_stats['max_soc']:.2f}%")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
