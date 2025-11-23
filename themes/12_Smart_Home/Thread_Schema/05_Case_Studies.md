# Thread Schema实践案例

## 📑 目录

- [Thread Schema实践案例](#thread-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：Thread Mesh网络构建](#2-案例1thread-mesh网络构建)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：Thread路由管理和优化](#3-案例2thread路由管理和优化)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：Thread网络安全和密钥管理](#4-案例3thread网络安全和密钥管理)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：Thread网络性能监控](#5-案例4thread网络性能监控)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：Thread到Zigbee网络转换](#6-案例5thread到zigbee网络转换)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)
  - [7. 案例6：Thread数据存储和分析系统](#7-案例6thread数据存储和分析系统)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 实现代码](#72-实现代码)
    - [7.3 数据分析示例](#73-数据分析示例)

---

## 1. 案例概述

本文档提供Thread Schema在实际应用中的实践案例。

---

## 2. 案例1：Thread Mesh网络构建

### 2.1 场景描述

**业务背景**：
用户需要构建一个Thread Mesh网络，连接多个智能家居设备，
包括智能灯、传感器、门锁等，实现设备间的Mesh通信。

**技术挑战**：

- 需要创建Thread网络并配置网络参数
- 需要将多个设备加入网络
- 需要管理网络拓扑
- 需要监控网络状态

**解决方案**：
使用ThreadNetworkManager创建和管理Thread网络，实现设备的
自动发现和加入网络功能。

### 2.2 Schema定义

详见第2.2节原始定义。

### 2.3 实现代码

**完整的Thread Mesh网络构建实现**：

```python
import asyncio
from thread_network_manager import ThreadNetworkManager
from thread_storage import ThreadStorage

# 初始化存储和管理器
storage = ThreadStorage("postgresql://user:pass@localhost/thread")
network_manager = ThreadNetworkManager()

async def build_thread_mesh_network():
    """构建Thread Mesh网络"""
    try:
        # 创建Thread网络
        network_name = "SmartHomeNet"
        pan_id = 0x1234
        channel = 15
        network_key = "00112233445566778899AABBCCDDEEFF"

        print(f"Creating Thread network: {network_name}")
        success = network_manager.create_network(
            network_name, pan_id, channel, network_key
        )

        if not success:
            print("Failed to create network")
            return

        # 存储网络信息
        network_data = {
            "network_name": network_name,
            "pan_id": pan_id,
            "extended_pan_id": "DEADBEEF00CAFE00",
            "channel": channel,
            "network_key": network_key,
            "partition_id": 1
        }
        storage.store_network(network_data)

        # 节点列表
        nodes = [
            {"node_id": "000D6F0000123456", "type": "Router"},
            {"node_id": "000D6F0000654321", "type": "EndDevice"},
            {"node_id": "000D6F0000789012", "type": "EndDevice"}
        ]

        # 将节点加入网络
        for node in nodes:
            print(f"Joining node {node['node_id']} to network...")
            success = network_manager.join_network(
                node["node_id"],
                network_name,
                network_key,
                pan_id,
                channel
            )

            if success:
                # 获取节点信息
                node_info = network_manager.get_node_info(node["node_id"])
                if node_info:
                    # 存储节点信息
                    storage.store_node(node_info)
                    print(f"Node {node['node_id']} joined successfully")
                    print(f"  Type: {node_info['node_type']}")
                    print(f"  Mesh Local: {node_info['mesh_local_address']}")
            else:
                print(f"Failed to join node {node['node_id']}")

        # 获取网络拓扑
        topology = network_manager.get_network_topology(network_name)
        print(f"\nNetwork Topology:")
        print(f"  Total nodes: {len(topology['nodes'])}")
        print(f"  Routers: {len(topology['routers'])}")
        print(f"  End Devices: {len(topology['end_devices'])}")

        # 查询网络健康状态
        health = storage.get_network_health_status(network_name)
        print(f"\nNetwork Health:")
        print(f"  Health Score: {health['health_score']:.1f}/100")
        print(f"  Avg Link Quality: {health['avg_link_quality']:.1f}")
        print(f"  Low Battery Nodes: {health['low_battery_count']}")

    except Exception as e:
        print(f"Error building network: {e}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(build_thread_mesh_network())
```

---

## 3. 案例2：Thread路由管理和优化

### 3.1 场景描述

**业务背景**：
系统需要管理Thread网络的路由表，监控路由性能，
并在路由失效时自动更新路由表，确保网络连通性。

**技术挑战**：

- 需要定期更新路由表
- 需要监控路由性能
- 需要检测路由失效
- 需要优化路由路径

**解决方案**：
使用ThreadRoutingManager管理路由表，定期更新路由信息
并监控路由性能。

### 3.2 Schema定义

详见第3.2节原始定义。

### 3.3 实现代码

**完整的路由管理实现**：

```python
import asyncio
from thread_network_manager import ThreadNetworkManager
from thread_routing_manager import ThreadRoutingManager
from thread_storage import ThreadStorage
import time

# 初始化组件
storage = ThreadStorage("postgresql://user:pass@localhost/thread")
network_manager = ThreadNetworkManager()
routing_manager = ThreadRoutingManager(network_manager)

async def manage_thread_routing():
    """管理Thread路由"""
    try:
        network_name = "SmartHomeNet"

        # 获取网络中的所有节点
        topology = network_manager.get_network_topology(network_name)
        nodes = topology["nodes"]

        print(f"Managing routing for {len(nodes)} nodes")

        # 更新所有节点的路由表
        for node in nodes:
            node_id = node["node_id"]
            print(f"Updating routing table for node {node_id}...")

            # 更新路由表
            routing_manager.update_routing_table(node_id)

            # 获取路由表
            routes = routing_manager.get_node_routes(node_id)
            print(f"  Found {len(routes)} routes")

            # 存储路由表到数据库
            storage.store_routing_table(node_id, routes)

            # 显示路由统计
            route_stats = storage.get_routing_statistics(node_id)
            print(f"  Route count: {route_stats['route_count']}")
            print(f"  Avg cost: {route_stats['avg_cost']:.2f}")
            print(f"  Max hops: {route_stats['max_cost']}")

        # 获取网络路由统计
        network_stats = routing_manager.get_network_routing_statistics(network_name)
        print(f"\nNetwork Routing Statistics:")
        print(f"  Total nodes: {network_stats['total_nodes']}")
        print(f"  Total routes: {network_stats['total_routes']}")
        print(f"  Avg routes per node: {network_stats['avg_routes_per_node']:.2f}")
        print(f"  Avg cost: {network_stats['avg_cost']:.2f}")
        print(f"  Max hops: {network_stats['max_hops']}")

        # 测试路由查找
        if len(nodes) >= 2:
            source_node = nodes[0]["node_id"]
            dest_address = nodes[1].get("mesh_local_address")

            if dest_address:
                route = routing_manager.find_route(source_node, dest_address)
                if route:
                    print(f"\nRoute from {source_node} to {dest_address}:")
                    print(f"  Next hop: {route['next_hop']}")
                    print(f"  Cost: {route['cost']}")
                else:
                    print(f"\nNo route found from {source_node} to {dest_address}")

    except Exception as e:
        print(f"Error managing routing: {e}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(manage_thread_routing())
```

---

## 4. 案例3：Thread网络安全和密钥管理

### 4.1 场景描述

**业务背景**：
系统需要管理Thread网络的安全密钥，定期轮换网络密钥，
确保网络安全，并监控安全事件。

**技术挑战**：

- 需要定期轮换网络密钥
- 需要同步密钥到所有节点
- 需要监控安全事件
- 需要处理密钥轮换失败的情况

**解决方案**：
使用ThreadSecurityManager管理网络密钥，实现密钥轮换
和安全监控功能。

### 4.2 Schema定义

详见第4.2节原始定义。

### 4.3 实现代码

**完整的安全管理实现**：

```python
import asyncio
from thread_security_manager import ThreadSecurityManager
from thread_storage import ThreadStorage
from datetime import datetime, timedelta

# 初始化组件
storage = ThreadStorage("postgresql://user:pass@localhost/thread")
security_manager = ThreadSecurityManager(storage)

async def manage_thread_security():
    """管理Thread网络安全"""
    try:
        network_name = "SmartHomeNet"

        # 检查是否需要轮换密钥
        # 这里应该从数据库查询上次轮换时间
        last_rotation_time = datetime.now() - timedelta(days=2)
        rotation_interval = timedelta(days=1)

        if datetime.now() - last_rotation_time > rotation_interval:
            print("Rotating network key...")
            success = security_manager.rotate_network_key(network_name)

            if success:
                print("Network key rotated successfully")
                # 这里需要通知所有节点更新密钥
                # 实际实现需要调用OpenThread API更新所有节点
            else:
                print("Failed to rotate network key")
        else:
            print("Network key is still valid, no rotation needed")

        # 查询安全统计
        # 这里可以查询安全事件、密钥使用情况等

    except Exception as e:
        print(f"Error managing security: {e}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(manage_thread_security())
```

---

## 5. 案例4：Thread网络性能监控

### 5.1 场景描述

**业务背景**：
系统需要监控Thread网络的性能指标，包括延迟、丢包率、
吞吐量等，及时发现网络问题并优化网络性能。

**技术挑战**：

- 需要实时收集性能数据
- 需要分析性能趋势
- 需要识别性能瓶颈
- 需要生成性能报告

**解决方案**：
使用ThreadStorage存储性能数据，定期收集和分析网络性能。

### 5.2 实现代码

**完整的性能监控实现**：

```python
import asyncio
from thread_network_manager import ThreadNetworkManager
from thread_storage import ThreadStorage
import time

# 初始化组件
storage = ThreadStorage("postgresql://user:pass@localhost/thread")
network_manager = ThreadNetworkManager()

async def monitor_thread_performance():
    """监控Thread网络性能"""
    try:
        network_name = "SmartHomeNet"

        # 获取网络中的所有节点
        topology = network_manager.get_network_topology(network_name)
        nodes = topology["nodes"]

        print(f"Monitoring performance for {len(nodes)} nodes")

        # 收集性能数据
        for node in nodes:
            node_id = node["node_id"]

            # 模拟性能数据收集
            # 实际实现需要从OpenThread获取真实数据
            performance_data = {
                "latency_ms": 50 + (hash(node_id) % 50),  # 模拟延迟
                "packet_loss_rate": (hash(node_id) % 5) / 100.0,  # 模拟丢包率
                "throughput_kbps": 100 + (hash(node_id) % 200)  # 模拟吞吐量
            }

            # 存储性能数据
            storage.store_performance_data(node_id, performance_data)

            print(f"Node {node_id}:")
            print(f"  Latency: {performance_data['latency_ms']}ms")
            print(f"  Packet Loss: {performance_data['packet_loss_rate']*100:.2f}%")
            print(f"  Throughput: {performance_data['throughput_kbps']}kbps")

        # 查询网络性能统计
        perf_stats = storage.get_network_performance_statistics(network_name, hours=24)
        print(f"\nNetwork Performance Statistics (24h):")
        print(f"  Avg Latency: {perf_stats['avg_latency']:.2f}ms")
        print(f"  Avg Packet Loss: {perf_stats['avg_packet_loss']*100:.2f}%")
        print(f"  Avg Throughput: {perf_stats['avg_throughput']:.2f}kbps")
        print(f"  Monitored Nodes: {perf_stats['monitored_nodes']}")

        # 查询节点性能历史
        if nodes:
            node_id = nodes[0]["node_id"]
            history = storage.get_node_performance_history(node_id, hours=1)
            print(f"\nPerformance History for {node_id} (1h):")
            print(f"  Data points: {len(history)}")
            if history:
                print(f"  Latest latency: {history[0]['latency_ms']}ms")

    except Exception as e:
        print(f"Error monitoring performance: {e}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(monitor_thread_performance())
```

---

## 6. 案例5：Thread到Zigbee网络转换

### 6.1 场景描述

**业务背景**：
需要将Thread网络转换为Zigbee网络，以便与现有的Zigbee系统集成，
实现跨协议设备通信。

**技术挑战**：

- 需要转换节点类型
- 需要转换网络地址
- 需要保持网络拓扑一致性
- 需要处理协议差异

**解决方案**：
使用ThreadToZigbeeConverter实现Thread到Zigbee的转换。

### 6.2 实现代码

详见 `04_Transformation.md` 第2.2章。

---

## 7. 案例6：Thread数据存储和分析系统

### 7.1 场景描述

**应用场景**：
使用PostgreSQL存储Thread网络数据，支持网络拓扑分析、
性能监控和健康状态评估。

### 7.2 实现代码

详见 `04_Transformation.md` 第6章。

### 7.3 数据分析示例

**网络健康状态查询**：

```python
from thread_storage import ThreadStorage

storage = ThreadStorage("postgresql://user:pass@localhost/thread")

# 查询网络健康状态
health = storage.get_network_health_status("SmartHomeNet")
print("Network Health Status:")
print(f"  Total Nodes: {health['total_nodes']}")
print(f"  Routers: {health['router_count']}")
print(f"  End Devices: {health['end_device_count']}")
print(f"  Avg Link Quality: {health['avg_link_quality']:.1f}")
print(f"  Avg RSSI: {health['avg_rssi']:.1f}dBm")
print(f"  Low Battery Nodes: {health['low_battery_count']}")
print(f"  Health Score: {health['health_score']:.1f}/100")

# 查询网络拓扑统计
topology_stats = storage.get_network_topology_statistics("SmartHomeNet")
print("\nTopology Statistics:")
for stat in topology_stats:
    print(f"  {stat['node_type']}: {stat['count']} nodes")
    print(f"    Avg Link Quality: {stat['avg_link_quality']:.1f}")
    print(f"    Avg RSSI: {stat['avg_rssi']:.1f}dBm")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
