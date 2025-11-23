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
  - [8. 案例7：Thread网络扩展（添加新节点）](#8-案例7thread网络扩展添加新节点)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：Thread网络故障恢复](#9-案例8thread网络故障恢复)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 Schema定义](#92-schema定义)
    - [9.3 实现代码](#93-实现代码)

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

## 8. 案例7：Thread网络扩展（添加新节点）

### 8.1 场景描述

**业务背景**：
用户需要在现有的Thread网络中动态添加新的智能设备，包括新的Router和End Device，
确保新节点能够顺利加入网络并建立正确的路由关系。

**技术挑战**：

- 需要检测新节点并引导其加入网络
- 需要为新节点分配网络地址和路由信息
- 需要更新现有节点的路由表
- 需要处理节点加入失败的情况
- 需要优化网络拓扑以适应新节点

**解决方案**：
使用ThreadNetworkManager的节点加入功能，结合路由管理器的自动路由更新，
实现新节点的无缝加入和网络扩展。

### 8.2 Schema定义

**网络扩展Schema**：

```json
{
  "network_name": "SmartHomeNet",
  "new_nodes": [
    {
      "node_id": "000D6F0000ABCDEF",
      "node_type": "Router",
      "expected_role": "Router",
      "join_credentials": {
        "network_key": "00112233445566778899AABBCCDDEEFF",
        "pan_id": 4660,
        "channel": 15
      }
    },
    {
      "node_id": "000D6F0000FEDCBA",
      "node_type": "EndDevice",
      "expected_role": "EndDevice",
      "join_credentials": {
        "network_key": "00112233445566778899AABBCCDDEEFF",
        "pan_id": 4660,
        "channel": 15
      }
    }
  ],
  "expansion_strategy": {
    "update_routing_tables": true,
    "optimize_topology": true,
    "verify_connectivity": true
  }
}
```

### 8.3 实现代码

**完整的网络扩展实现**：

```python
import logging
from datetime import datetime
from thread_network_manager import ThreadNetworkManager
from thread_routing_manager import ThreadRoutingManager
from thread_storage import ThreadStorage
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化组件
storage = ThreadStorage("postgresql://user:pass@localhost/thread")
network_manager = ThreadNetworkManager()
routing_manager = ThreadRoutingManager(network_manager)

def expand_thread_network(network_name: str, new_nodes: List[Dict]) -> Dict:
    """扩展Thread网络 - 添加新节点"""
    results = {
        "network_name": network_name,
        "timestamp": datetime.now().isoformat(),
        "successful_joins": [],
        "failed_joins": [],
        "routing_updates": [],
        "topology_changes": {}
    }

    try:
        # 1. 获取当前网络状态
        current_topology = network_manager.get_network_topology(network_name)
        initial_node_count = len(current_topology["nodes"])
        logger.info(f"Current network has {initial_node_count} nodes")

        # 2. 添加新节点
        for new_node in new_nodes:
            node_id = new_node["node_id"]
            node_type = new_node.get("node_type", "EndDevice")
            credentials = new_node.get("join_credentials", {})

            logger.info(f"Adding new node {node_id} (type: {node_type})...")

            try:
                # 加入网络
                success = network_manager.join_network(
                    node_id,
                    network_name,
                    credentials.get("network_key"),
                    credentials.get("pan_id"),
                    credentials.get("channel")
                )

                if success:
                    # 获取节点信息
                    node_info = network_manager.get_node_info(node_id)
                    if node_info:
                        # 存储节点信息
                        storage.store_node(node_info)

                        # 记录事件
                        storage.store_event(
                            network_name,
                            "node_joined",
                            {
                                "node_id": node_id,
                                "node_type": node_type,
                                "mesh_local_address": node_info.get("mesh_local_address")
                            },
                            node_id
                        )

                        results["successful_joins"].append({
                            "node_id": node_id,
                            "node_type": node_type,
                            "mesh_local_address": node_info.get("mesh_local_address"),
                            "parent_node_id": node_info.get("parent_node_id"),
                            "router_id": node_info.get("router_id")
                        })

                        logger.info(f"Node {node_id} joined successfully")

                        # 等待节点稳定
                        time.sleep(2)
                    else:
                        raise Exception("Failed to get node info after join")
                else:
                    raise Exception("Failed to join network")

            except Exception as e:
                logger.error(f"Failed to add node {node_id}: {e}")
                results["failed_joins"].append({
                    "node_id": node_id,
                    "error": str(e)
                })

        # 3. 更新路由表
        logger.info("Updating routing tables...")
        updated_count = routing_manager.update_all_routing_tables(network_name)
        results["routing_updates"] = {
            "updated_nodes": updated_count,
            "timestamp": datetime.now().isoformat()
        }

        # 4. 优化路由表
        logger.info("Optimizing routing tables...")
        topology = network_manager.get_network_topology(network_name)
        optimized_count = 0
        for node in topology["nodes"]:
            node_id = node["node_id"]
            if routing_manager.optimize_routing_table(node_id):
                optimized_count += 1

        results["routing_updates"]["optimized_nodes"] = optimized_count

        # 5. 验证连通性
        logger.info("Verifying network connectivity...")
        final_topology = network_manager.get_network_topology(network_name)
        final_node_count = len(final_topology["nodes"])

        results["topology_changes"] = {
            "initial_node_count": initial_node_count,
            "final_node_count": final_node_count,
            "added_nodes": final_node_count - initial_node_count,
            "router_count": len(final_topology["routers"]),
            "end_device_count": len(final_topology["end_devices"])
        }

        # 6. 网络诊断
        logger.info("Running network diagnosis...")
        diagnosis = network_manager.diagnose_network(network_name)
        storage.store_diagnosis(network_name, diagnosis)

        results["diagnosis"] = {
            "issues_count": len(diagnosis.get("issues", [])),
            "connectivity_score": len(diagnosis["connectivity"]["connected_nodes"]) / final_node_count if final_node_count > 0 else 0,
            "routing_efficiency": diagnosis["routing"].get("complete_tables", [])
        }

        logger.info(f"Network expansion completed: {len(results['successful_joins'])} nodes added")
        return results

    except Exception as e:
        logger.error(f"Network expansion failed: {e}")
        results["error"] = str(e)
        return results

# 测试用例
def test_network_expansion():
    """测试网络扩展"""
    network_name = "SmartHomeNet"

    new_nodes = [
        {
            "node_id": "000D6F0000ABCDEF",
            "node_type": "Router",
            "join_credentials": {
                "network_key": "00112233445566778899AABBCCDDEEFF",
                "pan_id": 4660,
                "channel": 15
            }
        },
        {
            "node_id": "000D6F0000FEDCBA",
            "node_type": "EndDevice",
            "join_credentials": {
                "network_key": "00112233445566778899AABBCCDDEEFF",
                "pan_id": 4660,
                "channel": 15
            }
        }
    ]

    results = expand_thread_network(network_name, new_nodes)

    print(f"\nNetwork Expansion Results:")
    print(f"  Successful joins: {len(results['successful_joins'])}")
    print(f"  Failed joins: {len(results['failed_joins'])}")
    print(f"  Initial nodes: {results['topology_changes']['initial_node_count']}")
    print(f"  Final nodes: {results['topology_changes']['final_node_count']}")
    print(f"  Added nodes: {results['topology_changes']['added_nodes']}")

    if results.get("diagnosis"):
        print(f"  Connectivity score: {results['diagnosis']['connectivity_score']:.2%}")
        print(f"  Issues found: {results['diagnosis']['issues_count']}")

if __name__ == "__main__":
    test_network_expansion()
```

**运行结果示例**：

```text
INFO:__main__:Current network has 3 nodes
INFO:__main__:Adding new node 000D6F0000ABCDEF (type: Router)...
INFO:__main__:Node 000D6F0000ABCDEF joined successfully
INFO:__main__:Adding new node 000D6F0000FEDCBA (type: EndDevice)...
INFO:__main__:Node 000D6F0000FEDCBA joined successfully
INFO:__main__:Updating routing tables...
INFO:__main__:Updated routing tables for 5/5 nodes
INFO:__main__:Optimizing routing tables...
INFO:__main__:Running network diagnosis...
INFO:__main__:Network expansion completed: 2 nodes added

Network Expansion Results:
  Successful joins: 2
  Failed joins: 0
  Initial nodes: 3
  Final nodes: 5
  Added nodes: 2
  Connectivity score: 100.00%
  Issues found: 0
```

---

## 9. 案例8：Thread网络故障恢复

### 9.1 场景描述

**业务背景**：
Thread网络中的某些节点可能出现故障（如断电、信号丢失、硬件故障），
系统需要自动检测故障，执行故障恢复流程，包括节点重新加入、路由重建、
网络分区合并等操作。

**技术挑战**：

- 需要实时检测节点故障
- 需要区分临时故障和永久故障
- 需要自动执行恢复流程
- 需要处理网络分区情况
- 需要恢复路由表完整性

**解决方案**：
使用网络诊断功能检测故障，结合分区管理和路由重建功能，
实现自动化的故障检测和恢复流程。

### 9.2 Schema定义

**故障恢复Schema**：

```json
{
  "network_name": "SmartHomeNet",
  "fault_detection": {
    "check_interval_seconds": 30,
    "fault_threshold": {
      "no_response_count": 3,
      "low_link_quality": 1,
      "low_rssi": -90
    }
  },
  "recovery_strategy": {
    "auto_rejoin": true,
    "rebuild_routes": true,
    "merge_partitions": true,
    "notify_administrator": true
  },
  "fault_types": [
    "node_unreachable",
    "low_link_quality",
    "routing_failure",
    "partition_detected"
  ]
}
```

### 9.3 实现代码

**完整的故障恢复实现**：

```python
import logging
from datetime import datetime, timedelta
from thread_network_manager import ThreadNetworkManager
from thread_routing_manager import ThreadRoutingManager
from thread_storage import ThreadStorage
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化组件
storage = ThreadStorage("postgresql://user:pass@localhost/thread")
network_manager = ThreadNetworkManager()
routing_manager = ThreadRoutingManager(network_manager)

class ThreadFaultRecovery:
    """Thread网络故障恢复管理器"""

    def __init__(self, network_name: str, check_interval: int = 30):
        self.network_name = network_name
        self.check_interval = check_interval
        self.fault_history = {}
        self.recovery_actions = []

    def detect_faults(self) -> List[Dict]:
        """检测网络故障"""
        faults = []

        try:
            # 执行网络诊断
            diagnosis = network_manager.diagnose_network(self.network_name)

            # 1. 检测断开连接的节点
            disconnected_nodes = diagnosis["connectivity"].get("disconnected_nodes", [])
            for node_id in disconnected_nodes:
                fault = {
                    "node_id": node_id,
                    "fault_type": "node_unreachable",
                    "severity": "high",
                    "detected_at": datetime.now().isoformat(),
                    "details": "Node is not responding"
                }
                faults.append(fault)

            # 2. 检测不健康节点
            unhealthy_nodes = diagnosis["node_health"].get("unhealthy_nodes", [])
            for node_id in unhealthy_nodes:
                health_details = diagnosis["node_health"]["health_details"].get(node_id, {})
                issues = health_details.get("issues", [])

                fault = {
                    "node_id": node_id,
                    "fault_type": "node_unhealthy",
                    "severity": "medium",
                    "detected_at": datetime.now().isoformat(),
                    "details": "; ".join(issues)
                }
                faults.append(fault)

            # 3. 检测路由表不完整
            incomplete_tables = diagnosis["routing"].get("incomplete_tables", [])
            for node_id in incomplete_tables:
                fault = {
                    "node_id": node_id,
                    "fault_type": "routing_failure",
                    "severity": "medium",
                    "detected_at": datetime.now().isoformat(),
                    "details": "Routing table is incomplete"
                }
                faults.append(fault)

            # 4. 检测网络分区
            network = network_manager.networks.get(self.network_name)
            if network and "partitions" in network:
                partitions = network["partitions"]
                if len(partitions) > 1:
                    fault = {
                        "node_id": None,
                        "fault_type": "partition_detected",
                        "severity": "high",
                        "detected_at": datetime.now().isoformat(),
                        "details": f"Network partitioned into {len(partitions)} partitions",
                        "partition_count": len(partitions)
                    }
                    faults.append(fault)

            logger.info(f"Detected {len(faults)} faults in network {self.network_name}")
            return faults

        except Exception as e:
            logger.error(f"Fault detection failed: {e}")
            return []

    def recover_from_fault(self, fault: Dict) -> bool:
        """从故障中恢复"""
        fault_type = fault["fault_type"]
        node_id = fault.get("node_id")

        logger.info(f"Recovering from fault: {fault_type} (node: {node_id})")

        try:
            if fault_type == "node_unreachable":
                return self._recover_unreachable_node(node_id)
            elif fault_type == "node_unhealthy":
                return self._recover_unhealthy_node(node_id)
            elif fault_type == "routing_failure":
                return self._recover_routing_failure(node_id)
            elif fault_type == "partition_detected":
                return self._recover_partition()
            else:
                logger.warning(f"Unknown fault type: {fault_type}")
                return False
        except Exception as e:
            logger.error(f"Recovery failed for fault {fault_type}: {e}")
            return False

    def _recover_unreachable_node(self, node_id: str) -> bool:
        """恢复不可达节点"""
        try:
            # 尝试重新加入网络
            network = network_manager.networks.get(self.network_name)
            if not network:
                return False

            logger.info(f"Attempting to rejoin node {node_id}...")
            success = network_manager._rejoin_network(node_id, self.network_name)

            if success:
                # 更新节点信息
                node_info = network_manager.get_node_info(node_id)
                if node_info:
                    storage.store_node(node_info)

                    # 记录恢复事件
                    storage.store_event(
                        self.network_name,
                        "node_recovered",
                        {
                            "node_id": node_id,
                            "recovery_type": "rejoin",
                            "mesh_local_address": node_info.get("mesh_local_address")
                        },
                        node_id
                    )

                    logger.info(f"Node {node_id} recovered successfully")
                    return True

            return False
        except Exception as e:
            logger.error(f"Failed to recover unreachable node {node_id}: {e}")
            return False

    def _recover_unhealthy_node(self, node_id: str) -> bool:
        """恢复不健康节点"""
        try:
            # 获取节点信息
            node_info = network_manager.get_node_info(node_id)
            if not node_info:
                return False

            # 如果节点有父节点，尝试重新选择父节点
            if node_info.get("node_type") == "EndDevice":
                # 让节点重新加入以选择更好的父节点
                return self._recover_unreachable_node(node_id)

            # 对于Router节点，更新路由表
            routing_manager.update_routing_table(node_id)
            routing_manager.optimize_routing_table(node_id)

            # 记录恢复事件
            storage.store_event(
                self.network_name,
                "node_health_improved",
                {"node_id": node_id},
                node_id
            )

            return True
        except Exception as e:
            logger.error(f"Failed to recover unhealthy node {node_id}: {e}")
            return False

    def _recover_routing_failure(self, node_id: str) -> bool:
        """恢复路由故障"""
        try:
            # 更新路由表
            routing_manager.update_routing_table(node_id)

            # 优化路由表
            routing_manager.optimize_routing_table(node_id)

            # 验证路由表
            routes = routing_manager.routing_tables.get(node_id, [])
            if len(routes) > 0:
                # 存储路由表
                storage.store_routing_table(node_id, routes)

                # 记录恢复事件
                storage.store_event(
                    self.network_name,
                    "routing_recovered",
                    {
                        "node_id": node_id,
                        "route_count": len(routes)
                    },
                    node_id
                )

                logger.info(f"Routing recovered for node {node_id}: {len(routes)} routes")
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to recover routing for node {node_id}: {e}")
            return False

    def _recover_partition(self) -> bool:
        """恢复网络分区"""
        try:
            logger.info("Attempting to merge network partitions...")

            # 检测分区
            network_manager.manage_partition(self.network_name, "detect")

            # 合并分区
            success = network_manager.manage_partition(self.network_name, "merge")

            if success:
                # 更新所有路由表
                routing_manager.update_all_routing_tables(self.network_name)

                # 记录恢复事件
                storage.store_event(
                    self.network_name,
                    "partition_merged",
                    {"recovery_type": "automatic"}
                )

                logger.info("Network partitions merged successfully")
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to recover partition: {e}")
            return False

    def run_continuous_monitoring(self):
        """持续监控和恢复"""
        logger.info(f"Starting continuous fault monitoring for {self.network_name}")

        while True:
            try:
                # 检测故障
                faults = self.detect_faults()

                # 处理每个故障
                for fault in faults:
                    # 检查故障历史，避免重复处理
                    fault_key = f"{fault['fault_type']}_{fault.get('node_id', 'network')}"
                    last_handled = self.fault_history.get(fault_key)

                    if last_handled:
                        # 如果最近处理过，跳过
                        time_since_handled = datetime.now() - datetime.fromisoformat(last_handled)
                        if time_since_handled.total_seconds() < 300:  # 5分钟内不重复处理
                            continue

                    # 执行恢复
                    recovery_success = self.recover_from_fault(fault)

                    # 记录恢复操作
                    self.recovery_actions.append({
                        "fault": fault,
                        "recovery_success": recovery_success,
                        "timestamp": datetime.now().isoformat()
                    })

                    # 更新故障历史
                    if recovery_success:
                        self.fault_history[fault_key] = datetime.now().isoformat()

                # 等待下次检查
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Stopping fault monitoring...")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(self.check_interval)

# 测试用例
def test_fault_recovery():
    """测试故障恢复"""
    recovery_manager = ThreadFaultRecovery("SmartHomeNet", check_interval=30)

    # 单次故障检测和恢复
    faults = recovery_manager.detect_faults()
    print(f"\nDetected {len(faults)} faults:")

    for fault in faults:
        print(f"  - {fault['fault_type']}: {fault.get('node_id', 'N/A')} ({fault['severity']})")
        recovery_success = recovery_manager.recover_from_fault(fault)
        print(f"    Recovery: {'Success' if recovery_success else 'Failed'}")

if __name__ == "__main__":
    test_fault_recovery()
    # 取消注释以运行持续监控
    # recovery_manager = ThreadFaultRecovery("SmartHomeNet")
    # recovery_manager.run_continuous_monitoring()
```

**运行结果示例**：

```text
INFO:__main__:Detected 2 faults in network SmartHomeNet
  - node_unreachable: 000D6F0000123456 (high)
    Recovery: Success
INFO:__main__:Attempting to rejoin node 000D6F0000123456...
INFO:__main__:Node 000D6F0000123456 recovered successfully
  - routing_failure: 000D6F0000654321 (medium)
    Recovery: Success
INFO:__main__:Routing recovered for node 000D6F0000654321: 5 routes
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
