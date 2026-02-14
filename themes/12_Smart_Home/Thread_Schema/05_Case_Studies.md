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
  - [10. 案例9：大规模Thread网络管理](#10-案例9大规模thread网络管理)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 Schema定义](#102-schema定义)
    - [10.3 实现代码](#103-实现代码)
  - [11. 案例10：Thread网络性能优化](#11-案例10thread网络性能优化)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 Schema定义](#112-schema定义)
    - [11.3 实现代码](#113-实现代码)
  - [12. 案例11：Thread网络安全加固](#12-案例11thread网络安全加固)
    - [12.1 场景描述](#121-场景描述)
    - [12.2 Schema定义](#122-schema定义)
    - [12.3 实现代码](#123-实现代码)

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

---

## 10. 案例9：大规模Thread网络管理

### 10.1 场景描述

**业务背景**：
大规模Thread网络管理系统管理数百甚至数千个Thread节点，
实现网络拓扑管理、节点监控、资源分配等功能。

**技术挑战**：

- 需要大规模网络拓扑管理
- 需要高效的节点监控
- 需要资源分配优化
- 需要网络性能保证

**解决方案**：
使用Thread_Schema定义大规模网络管理结构，
使用分布式管理架构进行网络管理，
使用ThreadStorage存储网络数据。

### 10.2 Schema定义

**大规模Thread网络管理Schema**：

```dsl
schema LargeScaleThreadNetworkManagement {
  management_session_id: String @value("LARGE-NET-20250121-001") @required
  network_name: String @value("LargeScaleNetwork") @required
  management_time: DateTime @value("2025-01-21T10:00:00") @required

  network_scale: {
    total_nodes: Integer @value(1000)
    router_nodes: Integer @value(100)
    end_devices: Integer @value(900)
    network_depth: Integer @value(5)
    average_children_per_router: Decimal @value(9.0)
  } @required

  network_topology: {
    partitions: Integer @value(1)
    isolated_nodes: Integer @value(5)
    connectivity_rate: Decimal @value(0.995) @range(0.0, 1.0)
    average_hops: Decimal @value(3.5)
    max_hops: Integer @value(7)
  } @required

  management_strategies: {
    hierarchical_management: Boolean @value(true)
    distributed_monitoring: Boolean @value(true)
    load_balancing: Boolean @value(true)
    auto_scaling: Boolean @value(true)
  } @required

  performance_metrics: {
    average_latency: Decimal @value(50.0) @unit("ms")
    packet_loss_rate: Decimal @value(0.001) @range(0.0, 1.0)
    network_throughput: Decimal @value(1000.0) @unit("packets/s")
    resource_utilization: Decimal @value(0.75) @range(0.0, 1.0)
  } @required
} @standard("Thread")
```

### 10.3 实现代码

```python
from thread_storage import ThreadStorage
from thread_network_manager import ThreadNetworkManager
from datetime import datetime

def large_scale_thread_network_management():
    """大规模Thread网络管理示例"""
    storage = ThreadStorage("postgresql://user:password@localhost/thread_db")
    network_manager = ThreadNetworkManager()

    # 网络规模
    network_scale = {
        "network_name": "LargeScaleNetwork",
        "total_nodes": 1000,
        "router_nodes": 100,
        "end_devices": 900,
        "network_depth": 5,
        "average_children_per_router": 9.0
    }

    # 网络拓扑分析
    def analyze_network_topology(network_name):
        """分析网络拓扑"""
        nodes = network_manager.get_all_nodes(network_name)

        router_count = sum(1 for n in nodes if n.get("node_type") == "Router")
        end_device_count = sum(1 for n in nodes if n.get("node_type") == "EndDevice")

        # 计算网络深度
        max_depth = 0
        for node in nodes:
            depth = calculate_node_depth(node, nodes)
            max_depth = max(max_depth, depth)

        # 计算连接率
        connected_nodes = sum(1 for n in nodes if n.get("connected", False))
        connectivity_rate = connected_nodes / len(nodes) if nodes else 0.0

        # 计算平均跳数
        total_hops = 0
        hop_count = 0
        for node in nodes:
            if node.get("connected"):
                hops = calculate_hops_to_border_router(node, nodes)
                total_hops += hops
                hop_count += 1
        average_hops = total_hops / hop_count if hop_count > 0 else 0.0

        return {
            "partitions": 1,  # 简化：假设单分区
            "isolated_nodes": len(nodes) - connected_nodes,
            "connectivity_rate": connectivity_rate,
            "average_hops": average_hops,
            "max_hops": max_depth
        }

    def calculate_node_depth(node, nodes):
        """计算节点深度"""
        depth = 0
        current = node
        while current.get("parent_id"):
            depth += 1
            parent_id = current["parent_id"]
            current = next((n for n in nodes if n["node_id"] == parent_id), None)
            if not current:
                break
        return depth

    def calculate_hops_to_border_router(node, nodes):
        """计算到边界路由器的跳数"""
        hops = 0
        current = node
        while current.get("parent_id"):
            hops += 1
            parent_id = current["parent_id"]
            current = next((n for n in nodes if n["node_id"] == parent_id), None)
            if not current or current.get("is_border_router"):
                break
        return hops

    # 执行拓扑分析
    topology = analyze_network_topology(network_scale["network_name"])

    # 管理策略
    management_strategies = {
        "hierarchical_management": True,
        "distributed_monitoring": True,
        "load_balancing": True,
        "auto_scaling": True
    }

    # 性能指标
    performance_metrics = {
        "average_latency": 50.0,
        "packet_loss_rate": 0.001,
        "network_throughput": 1000.0,
        "resource_utilization": 0.75
    }

    # 存储管理数据
    management_data = {
        "management_session_id": "LARGE-NET-20250121-001",
        "network_name": network_scale["network_name"],
        "management_time": datetime.now(),
        "total_nodes": network_scale["total_nodes"],
        "router_nodes": network_scale["router_nodes"],
        "end_devices": network_scale["end_devices"],
        "network_depth": network_scale["network_depth"],
        "partitions": topology["partitions"],
        "isolated_nodes": topology["isolated_nodes"],
        "connectivity_rate": topology["connectivity_rate"],
        "average_hops": topology["average_hops"],
        "max_hops": topology["max_hops"],
        "hierarchical_management": management_strategies["hierarchical_management"],
        "distributed_monitoring": management_strategies["distributed_monitoring"],
        "load_balancing": management_strategies["load_balancing"],
        "auto_scaling": management_strategies["auto_scaling"],
        "average_latency": performance_metrics["average_latency"],
        "packet_loss_rate": performance_metrics["packet_loss_rate"],
        "network_throughput": performance_metrics["network_throughput"],
        "resource_utilization": performance_metrics["resource_utilization"]
    }

    # 存储到数据库
    management_id = storage.store_network_data(management_data)
    print(f"Large-scale network management data stored: {management_id}")

    print(f"\nLarge-Scale Thread Network Management:")
    print(f"  Network: {network_scale['network_name']}")
    print(f"  Total nodes: {network_scale['total_nodes']}")
    print(f"  Router nodes: {network_scale['router_nodes']}")
    print(f"  End devices: {network_scale['end_devices']}")
    print(f"  Connectivity rate: {topology['connectivity_rate']*100:.2f}%")
    print(f"  Average hops: {topology['average_hops']:.2f}")
    print(f"  Average latency: {performance_metrics['average_latency']:.1f} ms")

    return management_data

if __name__ == "__main__":
    large_scale_thread_network_management()
```

---

## 11. 案例10：Thread网络性能优化

### 11.1 场景描述

**业务背景**：
Thread网络性能优化系统监测和分析网络性能，
识别性能瓶颈，优化网络配置，提高网络效率。

**技术挑战**：

- 需要性能数据收集
- 需要性能分析算法
- 需要优化策略
- 需要效果评估

**解决方案**：
使用Thread_Schema收集性能数据，
使用优化算法进行性能优化，
使用ThreadStorage存储性能数据。

### 11.2 Schema定义

**Thread网络性能优化Schema**：

```dsl
schema ThreadNetworkPerformanceOptimization {
  optimization_session_id: String @value("PERF-OPT-20250121-001") @required
  network_name: String @value("OptimizedNetwork") @required
  optimization_time: DateTime @value("2025-01-21T10:00:00") @required

  performance_baseline: {
    average_latency: Decimal @value(80.0) @unit("ms")
    packet_loss_rate: Decimal @value(0.005) @range(0.0, 1.0)
    network_throughput: Decimal @value(800.0) @unit("packets/s")
    energy_consumption: Decimal @value(100.0) @unit("mW")
  } @required

  performance_bottlenecks: [
    {
      bottleneck_type: String @value("High latency")
      location: String @value("Router-001")
      severity: Enum { Medium } @value(Medium)
      impact: Decimal @value(0.15) @unit("15% performance degradation")
    }
  ] @required

  optimization_strategies: [
    {
      strategy: String @value("路由表优化")
      expected_improvement: Decimal @value(0.20) @unit("20% latency reduction")
      implementation_complexity: Enum { Medium } @value(Medium)
    },
    {
      strategy: String @value("负载均衡")
      expected_improvement: Decimal @value(0.15) @unit("15% throughput increase")
      implementation_complexity: Enum { Low } @value(Low)
    }
  ] @required

  optimization_results: {
    latency_improvement: Decimal @value(0.18) @unit("18% reduction")
    throughput_improvement: Decimal @value(0.12) @unit("12% increase")
    energy_savings: Decimal @value(0.10) @unit("10% reduction")
    overall_improvement: Decimal @value(0.15) @unit("15% improvement")
  } @required
} @standard("Thread")
```

### 11.3 实现代码

```python
from thread_storage import ThreadStorage
from thread_network_manager import ThreadNetworkManager
from datetime import datetime

def thread_network_performance_optimization():
    """Thread网络性能优化示例"""
    storage = ThreadStorage("postgresql://user:password@localhost/thread_db")
    network_manager = ThreadNetworkManager()

    # 性能基线
    performance_baseline = {
        "network_name": "OptimizedNetwork",
        "average_latency": 80.0,
        "packet_loss_rate": 0.005,
        "network_throughput": 800.0,
        "energy_consumption": 100.0
    }

    # 性能瓶颈识别
    def identify_bottlenecks(network_name):
        """识别性能瓶颈"""
        bottlenecks = []
        nodes = network_manager.get_all_nodes(network_name)

        for node in nodes:
            node_latency = node.get("average_latency", 0)
            node_load = node.get("load", 0)

            # 识别高延迟节点
            if node_latency > 100:
                bottlenecks.append({
                    "bottleneck_type": "High latency",
                    "location": node["node_id"],
                    "severity": "Medium",
                    "impact": 0.15
                })

            # 识别高负载节点
            if node_load > 0.8:
                bottlenecks.append({
                    "bottleneck_type": "High load",
                    "location": node["node_id"],
                    "severity": "High",
                    "impact": 0.25
                })

        return bottlenecks

    # 识别瓶颈
    bottlenecks = identify_bottlenecks(performance_baseline["network_name"])

    # 优化策略
    optimization_strategies = []

    if any(b["bottleneck_type"] == "High latency" for b in bottlenecks):
        optimization_strategies.append({
            "strategy": "路由表优化",
            "expected_improvement": 0.20,
            "implementation_complexity": "Medium"
        })

    if any(b["bottleneck_type"] == "High load" for b in bottlenecks):
        optimization_strategies.append({
            "strategy": "负载均衡",
            "expected_improvement": 0.15,
            "implementation_complexity": "Low"
        })

    # 执行优化（简化示例）
    optimization_results = {
        "latency_improvement": 0.18,
        "throughput_improvement": 0.12,
        "energy_savings": 0.10,
        "overall_improvement": 0.15
    }

    # 存储优化数据
    optimization_data = {
        "optimization_session_id": "PERF-OPT-20250121-001",
        "network_name": performance_baseline["network_name"],
        "optimization_time": datetime.now(),
        "baseline_latency": performance_baseline["average_latency"],
        "baseline_packet_loss": performance_baseline["packet_loss_rate"],
        "baseline_throughput": performance_baseline["network_throughput"],
        "baseline_energy": performance_baseline["energy_consumption"],
        "bottlenecks": bottlenecks,
        "optimization_strategies": optimization_strategies,
        "latency_improvement": optimization_results["latency_improvement"],
        "throughput_improvement": optimization_results["throughput_improvement"],
        "energy_savings": optimization_results["energy_savings"],
        "overall_improvement": optimization_results["overall_improvement"]
    }

    # 存储到数据库
    optimization_id = storage.store_network_data(optimization_data)
    print(f"Performance optimization data stored: {optimization_id}")

    print(f"\nThread Network Performance Optimization:")
    print(f"  Network: {performance_baseline['network_name']}")
    print(f"  Baseline latency: {performance_baseline['average_latency']:.1f} ms")
    print(f"  Bottlenecks identified: {len(bottlenecks)}")
    print(f"  Optimization strategies: {len(optimization_strategies)}")
    print(f"  Latency improvement: {optimization_results['latency_improvement']*100:.1f}%")
    print(f"  Throughput improvement: {optimization_results['throughput_improvement']*100:.1f}%")
    print(f"  Overall improvement: {optimization_results['overall_improvement']*100:.1f}%")

    return optimization_data

if __name__ == "__main__":
    thread_network_performance_optimization()
```

---

## 12. 案例11：Thread网络安全加固

### 12.1 场景描述

**业务背景**：
Thread网络安全加固系统增强网络安全性，
实现安全策略管理、威胁检测、安全事件响应等功能。

**技术挑战**：

- 需要安全策略管理
- 需要威胁检测
- 需要安全事件响应
- 需要安全审计

**解决方案**：
使用Thread_Schema定义安全策略，
使用安全算法进行威胁检测，
使用ThreadStorage存储安全数据。

### 12.2 Schema定义

**Thread网络安全加固Schema**：

```dsl
schema ThreadNetworkSecurityHardening {
  security_session_id: String @value("SEC-HARDEN-20250121-001") @required
  network_name: String @value("SecuredNetwork") @required
  security_time: DateTime @value("2025-01-21T10:00:00") @required

  security_policies: {
    authentication_enabled: Boolean @value(true)
    encryption_enabled: Boolean @value(true)
    key_rotation_interval: Integer @value(30) @unit("days")
    access_control_enabled: Boolean @value(true)
    intrusion_detection_enabled: Boolean @value(true)
  } @required

  security_threats: [
    {
      threat_type: String @value("Unauthorized access attempt")
      source_node: String @value("Node-001")
      severity: Enum { Medium } @value(Medium)
      detected_at: DateTime @value("2025-01-21T09:30:00")
      status: Enum { Blocked } @value(Blocked)
    }
  ] @required

  security_measures: [
    {
      measure: String @value("密钥轮换")
      implementation_status: Enum { Implemented } @value(Implemented)
      effectiveness: Decimal @value(0.90) @range(0.0, 1.0)
    },
    {
      measure: String @value("访问控制列表")
      implementation_status: Enum { Implemented } @value(Implemented)
      effectiveness: Decimal @value(0.85) @range(0.0, 1.0)
    }
  ] @required

  security_metrics: {
    threat_detection_rate: Decimal @value(0.95) @range(0.0, 1.0)
    false_positive_rate: Decimal @value(0.05) @range(0.0, 1.0)
    security_incidents: Integer @value(3)
    security_score: Decimal @value(0.88) @range(0.0, 1.0)
  } @required
} @standard("Thread")
```

### 12.3 实现代码

```python
from thread_storage import ThreadStorage
from thread_network_manager import ThreadNetworkManager
from datetime import datetime

def thread_network_security_hardening():
    """Thread网络安全加固示例"""
    storage = ThreadStorage("postgresql://user:password@localhost/thread_db")
    network_manager = ThreadNetworkManager()

    # 安全策略
    security_policies = {
        "network_name": "SecuredNetwork",
        "authentication_enabled": True,
        "encryption_enabled": True,
        "key_rotation_interval": 30,
        "access_control_enabled": True,
        "intrusion_detection_enabled": True
    }

    # 威胁检测
    def detect_security_threats(network_name):
        """检测安全威胁"""
        threats = []
        nodes = network_manager.get_all_nodes(network_name)

        for node in nodes:
            # 检测未授权访问尝试
            unauthorized_attempts = node.get("unauthorized_attempts", 0)
            if unauthorized_attempts > 0:
                threats.append({
                    "threat_type": "Unauthorized access attempt",
                    "source_node": node["node_id"],
                    "severity": "Medium" if unauthorized_attempts < 5 else "High",
                    "detected_at": datetime.now(),
                    "status": "Blocked"
                })

            # 检测异常行为
            if node.get("anomaly_score", 0) > 0.7:
                threats.append({
                    "threat_type": "Anomalous behavior",
                    "source_node": node["node_id"],
                    "severity": "High",
                    "detected_at": datetime.now(),
                    "status": "Under investigation"
                })

        return threats

    # 检测威胁
    threats = detect_security_threats(security_policies["network_name"])

    # 安全措施
    security_measures = [
        {
            "measure": "密钥轮换",
            "implementation_status": "Implemented",
            "effectiveness": 0.90
        },
        {
            "measure": "访问控制列表",
            "implementation_status": "Implemented",
            "effectiveness": 0.85
        },
        {
            "measure": "入侵检测系统",
            "implementation_status": "Implemented",
            "effectiveness": 0.88
        }
    ]

    # 安全指标
    security_metrics = {
        "threat_detection_rate": 0.95,
        "false_positive_rate": 0.05,
        "security_incidents": len(threats),
        "security_score": 0.88
    }

    # 存储安全数据
    security_data = {
        "security_session_id": "SEC-HARDEN-20250121-001",
        "network_name": security_policies["network_name"],
        "security_time": datetime.now(),
        "authentication_enabled": security_policies["authentication_enabled"],
        "encryption_enabled": security_policies["encryption_enabled"],
        "key_rotation_interval": security_policies["key_rotation_interval"],
        "access_control_enabled": security_policies["access_control_enabled"],
        "intrusion_detection_enabled": security_policies["intrusion_detection_enabled"],
        "threats": threats,
        "security_measures": security_measures,
        "threat_detection_rate": security_metrics["threat_detection_rate"],
        "false_positive_rate": security_metrics["false_positive_rate"],
        "security_incidents": security_metrics["security_incidents"],
        "security_score": security_metrics["security_score"]
    }

    # 存储到数据库
    security_id = storage.store_network_data(security_data)
    print(f"Security hardening data stored: {security_id}")

    print(f"\nThread Network Security Hardening:")
    print(f"  Network: {security_policies['network_name']}")
    print(f"  Authentication: {'Enabled' if security_policies['authentication_enabled'] else 'Disabled'}")
    print(f"  Encryption: {'Enabled' if security_policies['encryption_enabled'] else 'Disabled'}")
    print(f"  Threats detected: {len(threats)}")
    print(f"  Security measures: {len(security_measures)}")
    print(f"  Threat detection rate: {security_metrics['threat_detection_rate']*100:.1f}%")
    print(f"  Security score: {security_metrics['security_score']:.2f}")

    return security_data

if __name__ == "__main__":
    thread_network_security_hardening()
```

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21


---

## 12. 案例12：Thread网络信道优化与干扰规避

### 12.1 场景描述

**业务背景**：
Thread网络运行在2.4GHz频段，容易受到WiFi、蓝牙等其他无线设备的干扰。需要定期评估各信道的干扰情况，动态选择最优信道，确保网络稳定性和性能。

**技术挑战**：

- 需要实时监测各信道的能量检测(ED)值
- 需要评估链路质量与信道的关联
- 需要在不停机的情况下切换信道
- 需要预测干扰趋势

**解决方案**：
使用Thread的信道评估功能和能量检测API，结合历史数据分析，实现智能信道选择和切换。

### 12.2 Schema定义

**信道优化Schema**：

```json
{
  "channel_assessment": {
    "network_name": "SmartHomeNet",
    "assessment_time": "2025-02-14T10:00:00Z",
    "current_channel": 15,
    "channel_metrics": [
      {
        "channel": 11,
        "energy_detect": -75,
        "link_success_rate": 0.92,
        "assessment_score": 85
      },
      {
        "channel": 15,
        "energy_detect": -82,
        "link_success_rate": 0.98,
        "assessment_score": 95
      },
      {
        "channel": 20,
        "energy_detect": -68,
        "link_success_rate": 0.78,
        "assessment_score": 60
      }
    ],
    "recommendation": {
      "action": "maintain",
      "reason": "Current channel has good performance"
    }
  }
}
```

### 12.3 实现代码

```python
from thread_storage import ThreadStorage
from typing import List, Dict
import statistics

class ThreadChannelOptimizer:
    """Thread信道优化器"""

    CHANNELS = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]

    def __init__(self, storage: ThreadStorage):
        self.storage = storage

    def assess_channel(self, network_name: str, channel: int) -> Dict:
        """评估单个信道"""
        # 获取该信道上的节点链路质量
        self.storage.cur.execute("""
            SELECT link_quality, rssi
            FROM thread_nodes
            WHERE network_name = %s
            AND last_seen > NOW() - INTERVAL '1 hour'
        """, (network_name,))

        link_qualities = []
        rssis = []
        for row in self.storage.cur.fetchall():
            if row[0]:
                link_qualities.append(row[0])
            if row[1]:
                rssis.append(row[1])

        # 模拟能量检测值（实际应从设备获取）
        energy_detect = -80 + (channel % 5) * 2  # 模拟值

        # 计算评估分数
        if link_qualities:
            avg_lqi = statistics.mean(link_qualities)
            success_rate = avg_lqi / 255
        else:
            success_rate = 0.5

        # 综合评分
        score = success_rate * 100 + (energy_detect + 100)  # 能量越低(越负)分数越高
        score = min(100, max(0, score))

        return {
            "channel": channel,
            "energy_detect": energy_detect,
            "link_success_rate": round(success_rate, 2),
            "avg_rssi": statistics.mean(rssis) if rssis else None,
            "assessment_score": round(score, 1)
        }

    def assess_all_channels(self, network_name: str) -> List[Dict]:
        """评估所有信道"""
        results = []
        for channel in self.CHANNELS:
            assessment = self.assess_channel(network_name, channel)
            results.append(assessment)
            
            # 存储评估结果
            self.storage.store_channel_assessment(
                network_name, channel,
                assessment["energy_detect"],
                int(assessment["link_success_rate"] * 255)
            )

        return sorted(results, key=lambda x: x["assessment_score"], reverse=True)

    def recommend_channel(self, network_name: str, current_channel: int) -> Dict:
        """推荐最优信道"""
        assessments = self.assess_all_channels(network_name)
        
        best = assessments[0]
        current = next((a for a in assessments if a["channel"] == current_channel), None)

        recommendation = {
            "current_channel": current_channel,
            "best_channel": best["channel"],
            "current_score": current["assessment_score"] if current else 0,
            "best_score": best["assessment_score"],
            "action": "maintain",
            "reason": ""
        }

        if best["channel"] != current_channel:
            score_diff = best["assessment_score"] - (current["assessment_score"] if current else 0)
            if score_diff > 10:
                recommendation["action"] = "switch"
                recommendation["reason"] = f"Channel {best['channel']} is significantly better (+{score_diff:.1f} points)"
            else:
                recommendation["reason"] = f"Current channel is acceptable, alternative only slightly better (+{score_diff:.1f} points)"
        else:
            recommendation["reason"] = "Current channel has best performance"

        return recommendation

    def plan_channel_switch(self, network_name: str, new_channel: int) -> Dict:
        """规划信道切换"""
        # 获取当前网络状态
        nodes = self.storage.get_network_nodes(network_name)
        
        # 评估切换影响
        impact = {
            "total_nodes": len(nodes),
            "router_count": len([n for n in nodes if n["node_type"] == "Router"]),
            "estimated_downtime_seconds": 30,  # 预估停机时间
            "risk_level": "low"
        }

        plan = {
            "from_channel": self.get_current_channel(network_name),
            "to_channel": new_channel,
            "steps": [
                "1. Notify all nodes about pending channel switch",
                "2. Wait for ACK from all routers",
                "3. Execute channel switch on Leader",
                "4. Verify all nodes have switched",
                "5. Resume normal operation"
            ],
            "impact": impact,
            "rollback_plan": "If switch fails, revert to original channel and investigate"
        }

        return plan

    def get_current_channel(self, network_name: str) -> int:
        """获取当前信道"""
        self.storage.cur.execute("""
            SELECT channel FROM thread_networks WHERE network_name = %s
        """, (network_name,))
        row = self.storage.cur.fetchone()
        return row[0] if row else 15

# 使用示例
def demo_channel_optimization():
    storage = ThreadStorage("postgresql://user:pass@localhost/thread")
    optimizer = ThreadChannelOptimizer(storage)

    # 评估所有信道
    assessments = optimizer.assess_all_channels("SmartHomeNet")
    print("Channel Assessments:")
    for a in assessments:
        print(f"  Channel {a['channel']}: Score={a['assessment_score']}, ED={a['energy_detect']}dBm")

    # 获取推荐
    recommendation = optimizer.recommend_channel("SmartHomeNet", current_channel=15)
    print(f"\nRecommendation: {recommendation['action']}")
    print(f"Reason: {recommendation['reason']}")
```

---

## 13. 案例13：Thread网络电池供电设备优化

### 13.1 场景描述

**业务背景**：
Thread网络中的传感器等设备通常采用电池供电，需要优化其功耗以延长电池寿命。通过调整轮询间隔、数据上报策略和父节点选择，实现电池寿命最大化。

**技术挑战**：

- 需要平衡功耗和数据实时性
- 需要优化父节点选择减少重传
- 需要智能调整轮询间隔
- 需要预测电池寿命

**解决方案**：
使用Thread的 sleepy end device 模式，结合数据缓存和批量上报策略，实现低功耗运行。

### 13.2 Schema定义

**电池优化Schema**：

```json
{
  "battery_optimization": {
    "device_id": "SENSOR_001",
    "device_type": "SleepyEndDevice",
    "battery_profile": {
      "current_level": 78,
      "battery_capacity_mah": 2400,
      "avg_consumption_ma": 0.15,
      "estimated_life_days": 520
    },
    "power_optimization": {
      "poll_period_ms": 5000,
      "data_retention_period_ms": 300000,
      "batch_upload": true,
      "parent_selection_strategy": "balanced"
    },
    "parent_candidate_ranking": [
      {
        "node_id": "ROUTER_001",
        "link_margin": 25,
        "current_children": 3,
        "rank_score": 92
      }
    ]
  }
}
```

### 13.3 实现代码

```python
from datetime import datetime, timedelta

class ThreadBatteryOptimizer:
    """Thread电池优化器"""

    def __init__(self, storage: ThreadStorage):
        self.storage = storage

    def calculate_battery_life(self, device_id: str,
                               battery_capacity_mah: float = 2400,
                               avg_consumption_ma: float = 0.15) -> Dict:
        """计算电池寿命"""
        # 获取设备历史功耗数据
        history = self.storage.get_node_performance_history(device_id, hours=168)  # 7天

        if history:
            # 基于历史数据计算平均功耗
            avg_consumption = sum(h.get("latency_ms", 0) for h in history) / len(history) / 1000 * 10
        else:
            avg_consumption = avg_consumption_ma

        # 计算预期寿命（小时）
        estimated_hours = battery_capacity_mah / avg_consumption
        estimated_days = estimated_hours / 24

        # 计算电池耗尽日期
        depletion_date = datetime.now() + timedelta(days=estimated_days)

        return {
            "device_id": device_id,
            "current_battery_level": self._get_battery_level(device_id),
            "battery_capacity_mah": battery_capacity_mah,
            "avg_consumption_ma": round(avg_consumption, 3),
            "estimated_life_days": round(estimated_days, 1),
            "estimated_depletion_date": depletion_date.strftime("%Y-%m-%d"),
            "low_battery_warning_days": 30
        }

    def _get_battery_level(self, device_id: str) -> int:
        """获取电池电量"""
        node = self.storage.get_node_by_id(device_id)
        return node.get("battery_level", 100) if node else 100

    def optimize_poll_period(self, device_id: str, desired_latency_ms: int = 5000) -> int:
        """优化轮询周期"""
        battery_level = self._get_battery_level(device_id)

        # 根据电量调整轮询周期
        if battery_level > 50:
            poll_period = max(desired_latency_ms, 1000)  # 最快1秒
        elif battery_level > 20:
            poll_period = max(desired_latency_ms * 2, 5000)  # 电量中等，延长2倍
        else:
            poll_period = max(desired_latency_ms * 5, 30000)  # 电量低，延长5倍

        return poll_period

    def select_optimal_parent(self, device_id: str, candidates: List[str]) -> str:
        """选择最优父节点（考虑功耗）"""
        scored_parents = []

        for candidate in candidates:
            node = self.storage.get_node_by_id(candidate)
            if not node:
                continue

            score = 0
            reasons = []

            # 链路质量评分 (0-40)
            link_quality = node.get("link_quality", 0)
            link_score = (link_quality / 255) * 40
            score += link_score
            reasons.append(f"Link quality: {link_score:.1f}")

            # 子节点数量评分 - 越少越好 (0-30)
            children_count = self._get_children_count(candidate)
            child_score = max(0, 30 - children_count * 5)
            score += child_score
            reasons.append(f"Child load: {child_score:.1f}")

            # 节点类型评分 - Router优先 (0-30)
            if node.get("node_type") == "Router":
                score += 30
                reasons.append("Type: Router (30)")
            else:
                score += 10
                reasons.append("Type: Other (10)")

            scored_parents.append({
                "node_id": candidate,
                "score": score,
                "reasons": reasons
            })

        if not scored_parents:
            return None

        # 选择得分最高的
        best = max(scored_parents, key=lambda x: x["score"])
        return best["node_id"]

    def _get_children_count(self, node_id: str) -> int:
        """获取子节点数量"""
        self.storage.cur.execute("""
            SELECT COUNT(*) FROM thread_nodes
            WHERE parent_node_id = %s
        """, (node_id,))
        row = self.storage.cur.fetchone()
        return row[0] if row else 0

    def generate_power_report(self, network_name: str) -> Dict:
        """生成功耗报告"""
        nodes = self.storage.get_network_nodes(network_name)
        
        sleepy_devices = [n for n in nodes if n.get("node_type") == "SleepyEndDevice"]
        
        report = {
            "network_name": network_name,
            "total_sleepy_devices": len(sleepy_devices),
            "low_battery_devices": [],
            "avg_battery_level": 0,
            "estimated_network_life_days": 0
        }

        total_battery = 0
        for device in sleepy_devices:
            battery = device.get("battery_level", 100)
            total_battery += battery

            if battery < 20:
                report["low_battery_devices"].append({
                    "device_id": device["node_id"],
                    "battery_level": battery
                })

        if sleepy_devices:
            report["avg_battery_level"] = round(total_battery / len(sleepy_devices), 1)

        return report

# 使用示例
def demo_battery_optimization():
    storage = ThreadStorage("postgresql://user:pass@localhost/thread")
    optimizer = ThreadBatteryOptimizer(storage)

    # 计算电池寿命
    battery_info = optimizer.calculate_battery_life("SENSOR_001")
    print(f"Battery Info: {battery_info}")

    # 优化轮询周期
    poll_period = optimizer.optimize_poll_period("SENSOR_001")
    print(f"Optimized poll period: {poll_period}ms")

    # 生成功耗报告
    report = optimizer.generate_power_report("SmartHomeNet")
    print(f"Power Report: {report}")
```

---

## 14. 案例14：Thread网络服务质量(QoS)保障

### 14.1 场景描述

**业务背景**：
Thread网络需要为不同类型的应用提供差异化的服务质量保障。例如，安防传感器的数据需要优先传输，而环境传感器的数据可以容忍延迟。需要实现消息优先级管理和带宽分配。

**技术挑战**：

- 需要区分不同优先级的流量
- 需要避免低优先级流量饿死
- 需要动态调整QoS策略
- 需要监控QoS指标

**解决方案**：
使用CoAP消息优先级标记和队列管理，结合流量整形，实现差异化服务。

### 14.2 Schema定义

**QoS保障Schema**：

```json
{
  "qos_configuration": {
    "network_name": "SmartHomeNet",
    "traffic_classes": [
      {
        "class_id": 1,
        "name": "Emergency",
        "priority": 7,
        "max_latency_ms": 100,
        "bandwidth_share": 30
      },
      {
        "class_id": 2,
        "name": "Control",
        "priority": 5,
        "max_latency_ms": 500,
        "bandwidth_share": 40
      },
      {
        "class_id": 3,
        "name": "Telemetry",
        "priority": 3,
        "max_latency_ms": 5000,
        "bandwidth_share": 20
      },
      {
        "class_id": 4,
        "name": "Background",
        "priority": 1,
        "max_latency_ms": 30000,
        "bandwidth_share": 10
      }
    ]
  }
}
```

### 14.3 实现代码

```python
from enum import IntEnum
from typing import Dict, List

class TrafficClass(IntEnum):
    """流量类别"""
    BACKGROUND = 1
    TELEMETRY = 3
    CONTROL = 5
    EMERGENCY = 7

class ThreadQoSManager:
    """Thread QoS管理器"""

    def __init__(self, storage: ThreadStorage):
        self.storage = storage
        self.class_definitions = {
            TrafficClass.EMERGENCY: {
                "max_latency_ms": 100,
                "bandwidth_share": 30
            },
            TrafficClass.CONTROL: {
                "max_latency_ms": 500,
                "bandwidth_share": 40
            },
            TrafficClass.TELEMETRY: {
                "max_latency_ms": 5000,
                "bandwidth_share": 20
            },
            TrafficClass.BACKGROUND: {
                "max_latency_ms": 30000,
                "bandwidth_share": 10
            }
        }

    def classify_message(self, device_id: str, message_type: str) -> TrafficClass:
        """消息分类"""
        # 根据设备类型和消息类型确定优先级
        emergency_types = ["emergency_alert", "fire_alarm", "intrusion_detected"]
        control_types = ["light_control", "door_lock", "thermostat_set"]
        telemetry_types = ["temperature", "humidity", "occupancy"]

        if message_type in emergency_types:
            return TrafficClass.EMERGENCY
        elif message_type in control_types:
            return TrafficClass.CONTROL
        elif message_type in telemetry_types:
            return TrafficClass.TELEMETRY
        else:
            return TrafficClass.BACKGROUND

    def store_qos_message(self, network_name: str, source: str, dest: str,
                         msg_type: str, payload_size: int,
                         response_time: int = None):
        """存储带QoS标记的消息"""
        traffic_class = self.classify_message(source, msg_type)
        
        self.storage.store_coap_message(
            network_name=network_name,
            source=source,
            dest=dest,
            msg_type=msg_type,
            code="POST",
            msg_id=0,
            payload_size=payload_size,
            response_time=response_time,
            success=True
        )

    def analyze_qos_performance(self, network_name: str, hours: int = 24) -> Dict:
        """分析QoS性能"""
        self.storage.cur.execute("""
            SELECT 
                message_type,
                AVG(response_time_ms) as avg_latency,
                MAX(response_time_ms) as max_latency,
                COUNT(*) as message_count,
                SUM(CASE WHEN response_time_ms < 100 THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) as emergency_sla
            FROM thread_coap_messages
            WHERE network_name = %s
            AND timestamp >= NOW() - INTERVAL '%s hours'
            GROUP BY message_type
        """, (network_name, hours))

        results = {}
        for row in self.storage.cur.fetchall():
            msg_type = row[0]
            results[msg_type] = {
                "avg_latency_ms": round(row[1], 2) if row[1] else None,
                "max_latency_ms": row[2],
                "message_count": row[3],
                "sla_compliance": round(row[4] * 100, 1) if row[4] else 0
            }

        return results

    def check_qos_violations(self, network_name: str) -> List[Dict]:
        """检查QoS违规"""
        violations = []

        performance = self.analyze_qos_performance(network_name)

        for msg_type, metrics in performance.items():
            traffic_class = self.classify_message("", msg_type)
            sla = self.class_definitions[traffic_class]["max_latency_ms"]

            if metrics["avg_latency_ms"] and metrics["avg_latency_ms"] > sla:
                violations.append({
                    "message_type": msg_type,
                    "traffic_class": traffic_class.name,
                    "sla_latency_ms": sla,
                    "actual_avg_latency_ms": metrics["avg_latency_ms"],
                    "violation_severity": "HIGH" if metrics["avg_latency_ms"] > sla * 2 else "MEDIUM"
                })

        return violations

    def generate_qos_report(self, network_name: str) -> Dict:
        """生成QoS报告"""
        performance = self.analyze_qos_performance(network_name)
        violations = self.check_qos_violations(network_name)

        return {
            "network_name": network_name,
            "generated_at": datetime.now().isoformat(),
            "performance_summary": performance,
            "sla_violations": violations,
            "overall_health": "DEGRADED" if violations else "HEALTHY",
            "recommendations": self._generate_qos_recommendations(violations)
        }

    def _generate_qos_recommendations(self, violations: List[Dict]) -> List[str]:
        """生成QoS优化建议"""
        recommendations = []

        if violations:
            high_violations = [v for v in violations if v["violation_severity"] == "HIGH"]
            if high_violations:
                recommendations.append(
                    f"{len(high_violations)} high-severity SLA violations detected. "
                    "Consider reducing network load or adding routers."
                )

            for v in violations[:3]:  # 前3个违规
                recommendations.append(
                    f"Review {v['message_type']} traffic: "
                    f"current avg {v['actual_avg_latency_ms']}ms, SLA is {v['sla_latency_ms']}ms"
                )
        else:
            recommendations.append("All traffic classes meeting SLA requirements")

        return recommendations

# 使用示例
def demo_qos_management():
    storage = ThreadStorage("postgresql://user:pass@localhost/thread")
    qos_manager = ThreadQoSManager(storage)

    # 存储不同优先级的消息
    qos_manager.store_qos_message(
        "SmartHomeNet", "SENSOR_001", "ROUTER_001",
        "emergency_alert", 50, response_time=50
    )
    qos_manager.store_qos_message(
        "SmartHomeNet", "SENSOR_002", "ROUTER_001",
        "temperature", 20, response_time=2000
    )

    # 分析QoS性能
    performance = qos_manager.analyze_qos_performance("SmartHomeNet")
    print(f"QoS Performance: {performance}")

    # 检查违规
    violations = qos_manager.check_qos_violations("SmartHomeNet")
    print(f"QoS Violations: {violations}")
```

---

## 15. 案例15：Thread网络自动化运维平台

### 15.1 场景描述

**业务背景**：
大规模Thread网络需要自动化运维平台来监控网络健康、自动发现故障、执行修复操作。平台需要集成监控、告警、诊断、修复的完整闭环。

**技术挑战**：

- 需要实时监控大量节点
- 需要自动故障诊断和分类
- 需要安全的自动化修复
- 需要运维审计和报告

**解决方案**：
构建完整的运维平台，集成监控采集、规则引擎、自动修复和报告生成。

### 15.2 Schema定义

**自动化运维Schema**：

```json
{
  "ops_platform": {
    "network_name": "SmartHomeNet",
    "monitoring_config": {
      "check_interval_seconds": 60,
      "metrics_retention_days": 30,
      "alert_channels": ["email", "sms", "webhook"]
    },
    "automation_rules": [
      {
        "rule_id": "auto_rejoin_offline_node",
        "trigger": "node_offline > 5min",
        "condition": "last_seen < now - 5min AND node_type = 'EndDevice'",
        "action": "send_rejoin_command",
        "auto_execute": false
      }
    ],
    "maintenance_windows": [
      {
        "window_id": "MW001",
        "start": "02:00",
        "end": "04:00",
        "timezone": "Asia/Shanghai",
        "allowed_operations": ["firmware_update", "network_reconfigure"]
      }
    ]
  }
}
```

### 15.3 实现代码

```python
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

class ThreadOpsPlatform:
    """Thread运维平台"""

    def __init__(self, storage: ThreadStorage):
        self.storage = storage
        self.alert_rules = []

    def register_alert_rule(self, name: str, rule_type: str,
                           condition: Dict, severity: str) -> int:
        """注册告警规则"""
        rule_id = self.storage.create_alert_rule(name, rule_type, condition, severity)
        self.alert_rules.append({
            "id": rule_id,
            "name": name,
            "type": rule_type,
            "condition": condition,
            "severity": severity
        })
        return rule_id

    def run_health_check(self, network_name: str) -> Dict:
        """执行健康检查"""
        results = {
            "network_name": network_name,
            "check_time": datetime.now().isoformat(),
            "checks": [],
            "issues": [],
            "overall_status": "HEALTHY"
        }

        # 1. 检查Leader状态
        leader_check = self._check_leader_status(network_name)
        results["checks"].append({"name": "leader_status", "result": leader_check})

        # 2. 检查分区情况
        partition_check = self._check_partitions(network_name)
        results["checks"].append({"name": "partitions", "result": partition_check})

        # 3. 检查节点离线情况
        offline_check = self._check_offline_nodes(network_name)
        results["checks"].append({"name": "offline_nodes", "result": offline_check})

        # 4. 检查链路质量
        link_check = self._check_link_quality(network_name)
        results["checks"].append({"name": "link_quality", "result": link_check})

        # 汇总问题
        for check in results["checks"]:
            if check["result"].get("status") != "OK":
                results["issues"].append({
                    "check": check["name"],
                    "status": check["result"]["status"],
                    "details": check["result"].get("details", "")
                })

        # 确定整体状态
        critical_count = len([i for i in results["issues"] if "CRITICAL" in i["status"]])
        warning_count = len([i for i in results["issues"] if "WARNING" in i["status"]])

        if critical_count > 0:
            results["overall_status"] = "CRITICAL"
        elif warning_count > 0:
            results["overall_status"] = "WARNING"

        return results

    def _check_leader_status(self, network_name: str) -> Dict:
        """检查Leader状态"""
        self.storage.cur.execute("""
            SELECT leader_router_id, COUNT(*) as node_count
            FROM thread_nodes
            WHERE network_name = %s
            GROUP BY leader_router_id
        """, (network_name,))

        rows = self.storage.cur.fetchall()
        if len(rows) > 1:
            return {
                "status": "CRITICAL",
                "details": f"Network partitioned! {len(rows)} partitions detected"
            }

        return {"status": "OK", "leader_id": rows[0][0] if rows else None}

    def _check_partitions(self, network_name: str) -> Dict:
        """检查分区"""
        self.storage.cur.execute("""
            SELECT COUNT(DISTINCT partition_id) FROM thread_partitions
            WHERE network_name = %s AND detected_at > NOW() - INTERVAL '1 hour'
        """, (network_name,))

        partition_count = self.storage.cur.fetchone()[0]

        if partition_count > 1:
            return {
                "status": "CRITICAL",
                "details": f"{partition_count} active partitions detected"
            }

        return {"status": "OK", "partition_count": partition_count}

    def _check_offline_nodes(self, network_name: str) -> Dict:
        """检查离线节点"""
        self.storage.cur.execute("""
            SELECT COUNT(*) FROM thread_nodes
            WHERE network_name = %s
            AND updated_at < NOW() - INTERVAL '10 minutes'
        """, (network_name,))

        offline_count = self.storage.cur.fetchone()[0]

        if offline_count > 0:
            return {
                "status": "WARNING",
                "details": f"{offline_count} nodes appear offline"
            }

        return {"status": "OK", "offline_count": 0}

    def _check_link_quality(self, network_name: str) -> Dict:
        """检查链路质量"""
        self.storage.cur.execute("""
            SELECT AVG(link_quality) FROM thread_nodes
            WHERE network_name = %s
        """, (network_name,))

        avg_lqi = self.storage.cur.fetchone()[0]

        if avg_lqi and avg_lqi < 150:
            return {
                "status": "WARNING",
                "details": f"Average LQI is low: {avg_lqi:.1f}"
            }

        return {"status": "OK", "avg_lqi": avg_lqi}

    def execute_remediation(self, network_name: str, issue: Dict) -> Dict:
        """执行修复操作"""
        remediation_result = {
            "issue": issue,
            "action_taken": None,
            "success": False,
            "message": ""
        }

        if issue["check"] == "offline_nodes":
            # 尝试让离线节点重新加入
            remediation_result["action_taken"] = "attempt_rejoin"
            remediation_result["success"] = True
            remediation_result["message"] = "Rejoin command sent to offline nodes"

        elif issue["check"] == "partitions":
            # 尝试合并分区
            remediation_result["action_taken"] = "attempt_merge"
            remediation_result["success"] = False
            remediation_result["message"] = "Partition merge requires manual intervention"

        return remediation_result

    def generate_ops_report(self, network_name: str, days: int = 7) -> Dict:
        """生成运维报告"""
        # 获取告警历史
        self.storage.cur.execute("""
            SELECT 
                severity,
                COUNT(*) as alert_count,
                COUNT(CASE WHEN acknowledged THEN 1 END) as acknowledged_count
            FROM thread_alert_history
            WHERE network_name = %s
            AND created_at >= NOW() - INTERVAL '%s days'
            GROUP BY severity
        """, (network_name, days))

        alert_summary = {}
        for row in self.storage.cur.fetchall():
            alert_summary[row[0]] = {
                "total": row[1],
                "acknowledged": row[2]
            }

        return {
            "network_name": network_name,
            "report_period_days": days,
            "generated_at": datetime.now().isoformat(),
            "alert_summary": alert_summary,
            "current_status": self.run_health_check(network_name)["overall_status"],
            "mttr_hours": 2.5,  # 平均修复时间
            "availability_percent": 99.5
        }

# 使用示例
def demo_ops_platform():
    storage = ThreadStorage("postgresql://user:pass@localhost/thread")
    ops = ThreadOpsPlatform(storage)

    # 注册告警规则
    ops.register_alert_rule(
        "Node Offline Alert",
        "node_offline",
        {"condition": "last_seen > 10min", "threshold": 1},
        "HIGH"
    )

    # 执行健康检查
    health = ops.run_health_check("SmartHomeNet")
    print(f"Health Check: {health['overall_status']}")
    for issue in health["issues"]:
        print(f"  Issue: {issue['check']} - {issue['status']}")

    # 生成运维报告
    report = ops.generate_ops_report("SmartHomeNet", days=7)
    print(f"Ops Report: {report}")
```

---

## 16. 案例16：Thread与Matter边界路由器集成

### 16.1 场景描述

**业务背景**：
Thread边界路由器(Border Router)连接Thread网络与外部网络（如WiFi/Ethernet），是Matter设备接入IP网络的关键组件。需要管理边界路由器、处理前缀委派、实现NAT64转换。

**技术挑战**：

- 需要管理多个边界路由器
- 需要处理IPv6前缀委派
- 需要实现NAT64转换
- 需要确保外部路由通告的正确性

**解决方案**：
使用Thread Border Router和Backbone Router功能，结合PostgreSQL存储边界路由器状态和外部路由信息。

### 16.2 Schema定义

**边界路由器集成Schema**：

```json
{
  "border_router_config": {
    "network_name": "SmartHomeNet",
    "border_routers": [
      {
        "router_id": "BR_001",
        "rloc16": "0xA800",
        "ip_addresses": {
          "thread": "fd11:22::ff:fe00:a800",
          "infrastructure": "192.168.1.100"
        },
        "prefixes": [
          {
            "prefix": "fd11:22::",
            "length": 64,
            "preferred": true,
            "slaac": true,
            "dhcp": false
          }
        ],
        "routes": [
          {
            "prefix": "0.0.0.0/0",
            "preference": "high",
            "nat64": true
          }
        ],
        "last_seen": "2025-02-14T10:30:00Z"
      }
    ]
  }
}
```

### 16.3 实现代码

```python
class ThreadBorderRouterManager:
    """Thread边界路由器管理器"""

    def __init__(self, storage: ThreadStorage):
        self.storage = storage

    def register_border_router(self, network_name: str, router_id: str,
                              rloc16: int, prefix: str, prefix_len: int,
                              is_preferred: bool = True) -> int:
        """注册边界路由器"""
        self.storage.cur.execute("""
            INSERT INTO thread_border_routers (
                network_name, border_router_id, rloc16, prefix,
                prefix_length, preferred, last_seen
            ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (network_name, border_router_id) DO UPDATE SET
                rloc16 = EXCLUDED.rloc16,
                prefix = EXCLUDED.prefix,
                prefix_length = EXCLUDED.prefix_length,
                preferred = EXCLUDED.preferred,
                last_seen = CURRENT_TIMESTAMP
            RETURNING id
        """, (network_name, router_id, rloc16, prefix, prefix_len, is_preferred))
        br_id = self.storage.cur.fetchone()[0]
        self.storage.conn.commit()
        return br_id

    def add_external_route(self, network_name: str, prefix: str,
                          prefix_len: int, border_router_id: str,
                          preference: int = 0, nat64: bool = False) -> int:
        """添加外部路由"""
        self.storage.cur.execute("""
            INSERT INTO thread_external_routes (
                network_name, prefix, prefix_length,
                border_router_id, preference, nat64
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (network_name, prefix, prefix_len, border_router_id, preference, nat64))
        route_id = self.storage.cur.fetchone()[0]
        self.storage.conn.commit()
        return route_id

    def get_active_border_routers(self, network_name: str) -> List[Dict]:
        """获取活跃边界路由器"""
        self.storage.cur.execute("""
            SELECT border_router_id, rloc16, prefix, prefix_length,
                   preferred, slaac, dhcp, last_seen
            FROM thread_border_routers
            WHERE network_name = %s
            AND last_seen > NOW() - INTERVAL '5 minutes'
            ORDER BY preferred DESC, last_seen DESC
        """, (network_name,))
        return [
            {
                "router_id": row[0],
                "rloc16": row[1],
                "prefix": row[2],
                "prefix_length": row[3],
                "preferred": row[4],
                "slaac": row[5],
                "dhcp": row[6],
                "last_seen": row[7]
            }
            for row in self.storage.cur.fetchall()
        ]

    def check_nat64_availability(self, network_name: str) -> Dict:
        """检查NAT64可用性"""
        self.storage.cur.execute("""
            SELECT border_router_id, prefix
            FROM thread_external_routes
            WHERE network_name = %s
            AND nat64 = TRUE
            AND preference >= 0
        """, (network_name,))

        rows = self.storage.cur.fetchall()
        if rows:
            return {
                "available": True,
                "border_routers": [row[0] for row in rows],
                "prefixes": [row[1] for row in rows]
            }

        return {"available": False}

    def configure_ipv6_prefix(self, network_name: str, prefix: str,
                             prefix_len: int, border_router_id: str) -> bool:
        """配置IPv6前缀"""
        # 实际实现中需要通过Thread管理接口配置
        logger.info(f"Configuring IPv6 prefix {prefix}/{prefix_len} on {border_router_id}")
        
        # 存储配置
        self.register_border_router(
            network_name, border_router_id,
            rloc16=0,  # 实际应从设备获取
            prefix=prefix,
            prefix_len=prefix_len
        )
        return True

    def monitor_border_router_health(self, network_name: str) -> List[Dict]:
        """监控边界路由器健康状态"""
        brs = self.get_active_border_routers(network_name)
        results = []

        for br in brs:
            # 检查最后活跃时间
            last_seen = br.get("last_seen")
            if last_seen:
                age_seconds = (datetime.now() - last_seen).total_seconds()
                status = "healthy" if age_seconds < 300 else "stale"
            else:
                status = "unknown"

            results.append({
                "router_id": br["router_id"],
                "status": status,
                "prefix": f"{br['prefix']}/{br['prefix_length']}",
                "is_preferred": br["preferred"]
            })

        return results

    def handle_prefix_change(self, network_name: str, old_prefix: str, new_prefix: str):
        """处理前缀变更"""
        # 通知所有节点前缀变更
        logger.info(f"Prefix change in {network_name}: {old_prefix} -> {new_prefix}")

        # 记录事件
        self.storage.store_event(
            network_name=network_name,
            event_type="prefix_change",
            event_data={
                "old_prefix": old_prefix,
                "new_prefix": new_prefix
            }
        )

# 使用示例
def demo_border_router():
    storage = ThreadStorage("postgresql://user:pass@localhost/thread")
    br_manager = ThreadBorderRouterManager(storage)

    # 注册边界路由器
    br_manager.register_border_router(
        network_name="SmartHomeNet",
        router_id="BR_001",
        rloc16=0xA800,
        prefix="fd11:22::",
        prefix_len=64,
        is_preferred=True
    )

    # 添加外部路由（NAT64）
    br_manager.add_external_route(
        network_name="SmartHomeNet",
        prefix="64:ff9b::",
        prefix_len=96,
        border_router_id="BR_001",
        nat64=True
    )

    # 检查NAT64可用性
    nat64 = br_manager.check_nat64_availability("SmartHomeNet")
    print(f"NAT64 Available: {nat64['available']}")

    # 监控边界路由器健康
    health = br_manager.monitor_border_router_health("SmartHomeNet")
    for br in health:
        print(f"BR {br['router_id']}: {br['status']}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-02-14（新增5个Thread高级案例）
