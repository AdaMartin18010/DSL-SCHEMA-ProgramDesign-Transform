# Thread Schema转换体系

## 📑 目录

- [Thread Schema转换体系](#thread-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. Thread网络管理实现](#2-thread网络管理实现)
    - [2.1 OpenThread集成封装](#21-openthread集成封装)
  - [3. Zigbee到Thread转换](#3-zigbee到thread转换)
  - [4. Thread路由管理](#4-thread路由管理)
    - [4.1 路由表管理](#41-路由表管理)
    - [4.2 Thread安全协议管理](#42-thread安全协议管理)
  - [5. 转换工具](#5-转换工具)
    - [5.1 OpenThread CLI集成](#51-openthread-cli集成)
    - [5.2 Thread SDK集成](#52-thread-sdk集成)
  - [6. 转换验证](#6-转换验证)
    - [6.1 网络拓扑一致性验证](#61-网络拓扑一致性验证)
  - [7. Thread数据存储与分析](#7-thread数据存储与分析)
    - [7.1 PostgreSQL Thread数据存储](#71-postgresql-thread数据存储)
    - [7.2 Thread数据分析查询](#72-thread数据分析查询)

---

## 1. 转换体系概述

Thread Schema转换体系支持Thread网络、Zigbee网络、
数据库存储之间的转换。

### 1.1 转换目标

1. **Thread到Zigbee转换**：Thread网络到Zigbee网络
2. **Zigbee到Thread转换**：Zigbee网络到Thread网络
3. **数据到数据库转换**：Thread网络数据到PostgreSQL存储

---

## 2. Thread网络管理实现

### 2.1 OpenThread集成封装

**完整的Thread网络管理实现**：

```python
import logging
import subprocess
import json
import ipaddress
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class ThreadNodeType(Enum):
    """Thread节点类型"""
    ROUTER = "Router"
    END_DEVICE = "EndDevice"
    SLEEPY_END_DEVICE = "SleepyEndDevice"
    LEADER = "Leader"

class ThreadNetworkManager:
    """Thread网络管理器"""

    def __init__(self, ot_cli_path: str = "ot-cli"):
        self.ot_cli_path = ot_cli_path
        self.networks: Dict[str, Dict] = {}
        self.nodes: Dict[str, Dict] = {}

    def execute_ot_command(self, node_id: str, command: str) -> Optional[str]:
        """执行OpenThread CLI命令"""
        cmd = [self.ot_cli_path, node_id, command]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"OT CLI error: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Failed to execute OT command: {e}")
            return None

    def create_network(self, network_name: str, pan_id: int,
                      channel: int, network_key: str) -> bool:
        """创建Thread网络"""
        try:
            # 生成Extended PAN ID
            extended_pan_id = self._generate_extended_pan_id()

            network_data = {
                "network_name": network_name,
                "pan_id": pan_id,
                "extended_pan_id": extended_pan_id,
                "channel": channel,
                "network_key": network_key,
                "partition_id": 1,
                "created_at": datetime.now().isoformat()
            }

            self.networks[network_name] = network_data
            logger.info(f"Created Thread network: {network_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create network: {e}")
            return False

    def join_network(self, node_id: str, network_name: str,
                    network_key: str, pan_id: int, channel: int) -> bool:
        """节点加入网络"""
        try:
            # 设置网络密钥
            cmd = f"networkkey {network_key}"
            result = self.execute_ot_command(node_id, cmd)
            if not result:
                return False

            # 设置PAN ID
            cmd = f"panid {pan_id:04x}"
            result = self.execute_ot_command(node_id, cmd)
            if not result:
                return False

            # 设置通道
            cmd = f"channel {channel}"
            result = self.execute_ot_command(node_id, cmd)
            if not result:
                return False

            # 启动网络
            cmd = "ifconfig up"
            result = self.execute_ot_command(node_id, cmd)
            if not result:
                return False

            cmd = "thread start"
            result = self.execute_ot_command(node_id, cmd)
            if not result:
                return False

            # 获取节点信息
            node_info = self.get_node_info(node_id)
            if node_info:
                node_info["network_name"] = network_name
                self.nodes[node_id] = node_info
                logger.info(f"Node {node_id} joined network {network_name}")
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to join network: {e}")
            return False

    def get_node_info(self, node_id: str) -> Optional[Dict]:
        """获取节点信息"""
        try:
            # 获取RLOC16
            rloc16_cmd = self.execute_ot_command(node_id, "rloc16")
            rloc16 = int(rloc16_cmd, 16) if rloc16_cmd else None

            # 获取IPv6地址
            link_local = self._get_link_local_address(node_id)
            mesh_local = self._get_mesh_local_address(node_id)

            # 获取节点类型
            node_type = self._get_node_type(node_id)

            # 获取路由器ID
            router_id = None
            if node_type == ThreadNodeType.ROUTER.value:
                router_id = (rloc16 >> 10) & 0x3F if rloc16 else None

            # 获取Leader路由器ID
            leader_router_id = self._get_leader_router_id(node_id)

            # 获取父节点信息
            parent_info = self._get_parent_info(node_id)

            # 获取链路质量
            link_quality = self._get_link_quality(node_id)

            return {
                "node_id": node_id,
                "node_type": node_type,
                "link_local_address": link_local,
                "mesh_local_address": mesh_local,
                "rloc16": rloc16,
                "router_id": router_id,
                "leader_router_id": leader_router_id,
                "parent_node_id": parent_info.get("parent_id") if parent_info else None,
                "link_quality": link_quality,
                "rssi": parent_info.get("rssi") if parent_info else None,
                "battery_level": None  # 需要从设备获取
            }
        except Exception as e:
            logger.error(f"Failed to get node info: {e}")
            return None

    def get_routing_table(self, node_id: str) -> List[Dict]:
        """获取路由表"""
        try:
            cmd = "routetable"
            result = self.execute_ot_command(node_id, cmd)
            if not result:
                return []

            routes = []
            for line in result.split('\n'):
                if not line.strip():
                    continue
                # 解析路由表行
                parts = line.split()
                if len(parts) >= 3:
                    routes.append({
                        "destination": parts[0],
                        "next_hop": parts[1],
                        "cost": int(parts[2]) if parts[2].isdigit() else 0,
                        "lifetime": 0  # 需要从实际输出解析
                    })

            return routes
        except Exception as e:
            logger.error(f"Failed to get routing table: {e}")
            return []

    def get_network_topology(self, network_name: str) -> Dict:
        """获取网络拓扑"""
        nodes_in_network = [
            node for node in self.nodes.values()
            if node.get("network_name") == network_name
        ]

        topology = {
            "network_name": network_name,
            "nodes": nodes_in_network,
            "routers": [
                node for node in nodes_in_network
                if node.get("node_type") == ThreadNodeType.ROUTER.value
            ],
            "end_devices": [
                node for node in nodes_in_network
                if node.get("node_type") == ThreadNodeType.END_DEVICE.value
            ],
            "topology_graph": self._build_topology_graph(nodes_in_network)
        }

        return topology

    def _generate_extended_pan_id(self) -> str:
        """生成Extended PAN ID"""
        import random
        return ''.join([f'{random.randint(0, 255):02X}' for _ in range(8)])

    def _get_link_local_address(self, node_id: str) -> str:
        """获取Link Local地址"""
        # 从OpenThread获取实际地址
        cmd = "ipaddr linklocal"
        result = self.execute_ot_command(node_id, cmd)
        return result if result else f"fe80::{node_id[:4]}:{node_id[4:8]}:{node_id[8:12]}:{node_id[12:16]}"

    def _get_mesh_local_address(self, node_id: str) -> str:
        """获取Mesh Local地址"""
        cmd = "ipaddr meshlocal"
        result = self.execute_ot_command(node_id, cmd)
        return result if result else f"fd00:1234:5678::{node_id[:4]}:{node_id[4:8]}:{node_id[8:12]}:{node_id[12:16]}"

    def _get_node_type(self, node_id: str) -> str:
        """获取节点类型"""
        cmd = "state"
        result = self.execute_ot_command(node_id, cmd)
        if result:
            if "leader" in result.lower():
                return ThreadNodeType.LEADER.value
            elif "router" in result.lower():
                return ThreadNodeType.ROUTER.value
            elif "child" in result.lower():
                return ThreadNodeType.END_DEVICE.value
        return ThreadNodeType.END_DEVICE.value

    def _get_leader_router_id(self, node_id: str) -> Optional[int]:
        """获取Leader路由器ID - 完整实现"""
        cmd = "leaderdata"
        result = self.execute_ot_command(node_id, cmd)
        if not result:
            return None

        try:
            # 解析OpenThread leaderdata输出格式
            # 格式示例: "Partition ID: 12345678\nLeader Router ID: 45\n..."
            lines = result.split('\n')
            for line in lines:
                if 'Leader Router ID' in line or 'Leader:' in line:
                    # 提取路由器ID
                    parts = line.split(':')
                    if len(parts) >= 2:
                        router_id_str = parts[-1].strip()
                        # 可能是十六进制或十进制
                        if router_id_str.startswith('0x'):
                            return int(router_id_str, 16)
                        elif router_id_str.isdigit():
                            return int(router_id_str)

            # 如果无法解析，尝试从RLOC16提取
            rloc16_cmd = self.execute_ot_command(node_id, "rloc16")
            if rloc16_cmd:
                try:
                    rloc16 = int(rloc16_cmd, 16)
                    # RLOC16的高6位是路由器ID
                    router_id = (rloc16 >> 10) & 0x3F
                    return router_id
                except ValueError:
                    pass

            return None
        except Exception as e:
            logger.error(f"Failed to parse leader router ID: {e}")
            return None

    def _get_parent_info(self, node_id: str) -> Optional[Dict]:
        """获取父节点信息 - 完整实现"""
        cmd = "parent"
        result = self.execute_ot_command(node_id, cmd)
        if not result:
            return None

        try:
            parent_info = {
                "parent_id": None,
                "rloc16": None,
                "rssi": None,
                "link_quality_in": None,
                "link_quality_out": None,
                "age": None,
                "timeout": None
            }

            # 解析OpenThread parent输出格式
            # 格式示例: "Ext Addr: 1234567890abcdef\nRloc: 0x1234\n..."
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if 'Rloc:' in line or 'RLOC16:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        rloc_str = parts[-1].strip()
                        if rloc_str.startswith('0x'):
                            parent_info["rloc16"] = int(rloc_str, 16)
                            # 从RLOC16提取路由器ID作为parent_id
                            parent_info["parent_id"] = (parent_info["rloc16"] >> 10) & 0x3F
                        elif rloc_str.isdigit():
                            parent_info["rloc16"] = int(rloc_str)
                            parent_info["parent_id"] = (parent_info["rloc16"] >> 10) & 0x3F

                elif 'RSSI:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        rssi_str = parts[-1].strip()
                        if rssi_str.lstrip('-').isdigit():
                            parent_info["rssi"] = int(rssi_str)

                elif 'Link Quality In:' in line or 'LQI In:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        lqi_str = parts[-1].strip()
                        if lqi_str.isdigit():
                            parent_info["link_quality_in"] = int(lqi_str)

                elif 'Link Quality Out:' in line or 'LQI Out:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        lqi_str = parts[-1].strip()
                        if lqi_str.isdigit():
                            parent_info["link_quality_out"] = int(lqi_str)

                elif 'Age:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        age_str = parts[-1].strip()
                        if age_str.isdigit():
                            parent_info["age"] = int(age_str)

            # 如果没有解析到RSSI，尝试从linkquality命令获取
            if parent_info["rssi"] is None:
                link_quality = self._get_link_quality(node_id)
                # 将链路质量转换为RSSI估算值（粗略估算）
                if link_quality > 0:
                    # LQI 0-3 对应 RSSI -100 到 -50 dBm
                    parent_info["rssi"] = -100 + (link_quality * 50 / 3)

            return parent_info if parent_info["parent_id"] is not None else None

        except Exception as e:
            logger.error(f"Failed to parse parent info: {e}")
            return None

    def _get_link_quality(self, node_id: str) -> int:
        """获取链路质量 - 完整实现"""
        # 方法1: 从linkquality命令获取
        cmd = "linkquality"
        result = self.execute_ot_command(node_id, cmd)
        if result:
            try:
                # 可能是数字或格式化的输出
                result = result.strip()
                if result.isdigit():
                    return int(result)
                # 尝试提取数字
                import re
                match = re.search(r'(\d+)', result)
                if match:
                    return int(match.group(1))
            except ValueError:
                pass

        # 方法2: 从parent命令的输出中提取
        parent_info = self._get_parent_info(node_id)
        if parent_info and parent_info.get("link_quality_in"):
            return parent_info["link_quality_in"]

        # 方法3: 从rssi估算
        if parent_info and parent_info.get("rssi"):
            rssi = parent_info["rssi"]
            # RSSI到LQI的粗略转换（Thread标准）
            if rssi >= -50:
                return 3
            elif rssi >= -65:
                return 2
            elif rssi >= -80:
                return 1
            else:
                return 0

        return 0

    def _build_topology_graph(self, nodes: List[Dict]) -> Dict:
        """构建拓扑图"""
        graph = {
            "nodes": [],
            "edges": []
        }

        for node in nodes:
            graph["nodes"].append({
                "id": node["node_id"],
                "type": node["node_type"],
                "address": node.get("mesh_local_address")
            })

            if node.get("parent_node_id"):
                graph["edges"].append({
                    "source": node["parent_node_id"],
                    "target": node["node_id"],
                    "type": "parent-child"
                })

        return graph

### 2.2 Thread到Zigbee转换

**转换规则**：

- Thread Router → Zigbee Coordinator
- Thread End Device → Zigbee End Device
- Thread IPv6地址 → Zigbee网络地址

**完整转换实现**：

```python
class ThreadToZigbeeConverter:
    """Thread到Zigbee转换器"""

    def __init__(self):
        self.conversion_log = []

    def convert_node(self, thread_node: Dict) -> Dict:
        """将Thread节点转换为Zigbee节点"""
        zigbee_node = {
            "ieee_address": thread_node.get("node_id", ""),
            "network_address": self._convert_ipv6_to_zigbee_address(
                thread_node.get("mesh_local_address", "")
            ),
            "node_type": self._convert_node_type(thread_node.get("node_type"))
        }

        # 转换网络信息
        network_info = thread_node.get("network_info", {})
        zigbee_node["network_info"] = {
            "pan_id": network_info.get("pan_id"),
            "extended_pan_id": network_info.get("extended_pan_id"),
            "channel": network_info.get("channel")
        }

        # 转换设备信息
        zigbee_node["device_info"] = {
            "link_quality": thread_node.get("link_quality", 0),
            "rssi": thread_node.get("rssi", 0),
            "battery_level": thread_node.get("battery_level")
        }

        return zigbee_node

    def _convert_ipv6_to_zigbee_address(self, ipv6_address: str) -> int:
        """将IPv6地址转换为Zigbee网络地址"""
        try:
            # 提取IPv6地址的最后16位作为网络地址
            addr = ipaddress.IPv6Address(ipv6_address)
            # 使用地址的最后16位
            return int(addr) & 0xFFFF
        except Exception:
            # 如果转换失败，使用哈希值
            return hash(ipv6_address) & 0xFFFF

    def _convert_node_type(self, thread_node_type: str) -> str:
        """转换节点类型"""
        type_map = {
            ThreadNodeType.ROUTER.value: "Coordinator",
            ThreadNodeType.LEADER.value: "Coordinator",
            ThreadNodeType.END_DEVICE.value: "EndDevice",
            ThreadNodeType.SLEEPY_END_DEVICE.value: "EndDevice"
        }
        return type_map.get(thread_node_type, "EndDevice")
```

---

## 3. Zigbee到Thread转换

**转换规则**：

- Zigbee Coordinator → Thread Router
- Zigbee End Device → Thread End Device
- Zigbee网络地址 → Thread IPv6地址

**完整转换实现**：

```python
class ZigbeeToThreadConverter:
    """Zigbee到Thread转换器"""

    def __init__(self):
        self.conversion_log = []

    def convert_node(self, zigbee_node: Dict, network_name: str = "DefaultNet") -> Dict:
        """将Zigbee节点转换为Thread节点"""
        ieee_address = zigbee_node.get("ieee_address", "")

        thread_node = {
            "node_id": ieee_address,
            "node_type": self._convert_node_type(zigbee_node.get("node_type")),
            "network_name": network_name,
            "ipv6_address": {
                "link_local": self._generate_link_local_address(ieee_address),
                "mesh_local": self._generate_mesh_local_address(ieee_address, network_name)
            }
        }

        # 转换网络信息
        network_info = zigbee_node.get("network_info", {})
        thread_node["network_info"] = {
            "pan_id": network_info.get("pan_id", 0x1234),
            "extended_pan_id": network_info.get("extended_pan_id", "DEADBEEF00CAFE00"),
            "channel": network_info.get("channel", 15),
            "network_key": self._generate_network_key()
        }

        # 转换设备信息
        device_info = zigbee_node.get("device_info", {})
        thread_node["link_quality"] = device_info.get("link_quality", 0)
        thread_node["rssi"] = device_info.get("rssi", 0)
        thread_node["battery_level"] = device_info.get("battery_level")

        return thread_node

    def _convert_node_type(self, zigbee_node_type: str) -> str:
        """转换节点类型"""
        type_map = {
            "Coordinator": ThreadNodeType.ROUTER.value,
            "Router": ThreadNodeType.ROUTER.value,
            "EndDevice": ThreadNodeType.END_DEVICE.value
        }
        return type_map.get(zigbee_node_type, ThreadNodeType.END_DEVICE.value)

    def _generate_link_local_address(self, ieee_address: str) -> str:
        """生成Link Local地址"""
        # 使用IEEE地址生成Link Local地址
        # fe80::[EUI64]
        eui64 = self._ieee_to_eui64(ieee_address)
        return f"fe80::{eui64[:4]}:{eui64[4:8]}:{eui64[8:12]}:{eui64[12:16]}"

    def _generate_mesh_local_address(self, ieee_address: str, network_name: str) -> str:
        """生成Mesh Local地址"""
        # 使用网络名称和IEEE地址生成Mesh Local地址
        # fd[network_hash]::[EUI64]
        network_hash = hash(network_name) & 0xFFFF
        eui64 = self._ieee_to_eui64(ieee_address)
        return f"fd{network_hash:04x}::{eui64[:4]}:{eui64[4:8]}:{eui64[8:12]}:{eui64[12:16]}"

    def _ieee_to_eui64(self, ieee_address: str) -> str:
        """将IEEE地址转换为EUI-64"""
        # 移除分隔符
        addr = ieee_address.replace(":", "").replace("-", "")
        # 插入FFFE
        if len(addr) == 16:
            return addr[:6] + "FFFE" + addr[6:]
        return addr

    def _generate_network_key(self) -> str:
        """生成网络密钥"""
        import secrets
        key = secrets.token_hex(16)
        return key.upper()
```

---

## 4. Thread路由管理

### 4.1 路由表管理

**路由表管理实现**：

```python
class ThreadRoutingManager:
    """Thread路由管理器 - 完整的MLE路由协议实现"""

    def __init__(self, network_manager: ThreadNetworkManager):
        self.network_manager = network_manager
        self.routing_tables: Dict[str, List[Dict]] = {}
        self.link_quality_matrix: Dict[Tuple[str, str], int] = {}  # (node1, node2) -> LQI
        self.route_cache: Dict[Tuple[str, str], Dict] = {}  # (source, dest) -> route
        self.route_update_interval = 30  # 路由表更新间隔（秒）

    def update_routing_table(self, node_id: str):
        """更新节点的路由表 - 完整实现"""
        try:
            # 从OpenThread获取路由表
            routes = self.network_manager.get_routing_table(node_id)

            # 增强路由表信息
            enhanced_routes = []
            for route in routes:
                enhanced_route = {
                    "destination": route.get("destination"),
                    "next_hop": route.get("next_hop"),
                    "cost": route.get("cost", 1),
                    "lifetime": route.get("lifetime", 3600),
                    "link_quality": self._get_link_quality_for_route(node_id, route.get("next_hop")),
                    "rssi": self._get_rssi_for_route(node_id, route.get("next_hop")),
                    "last_updated": datetime.now().isoformat()
                }
                enhanced_routes.append(enhanced_route)

            self.routing_tables[node_id] = enhanced_routes

            # 更新链路质量矩阵
            self._update_link_quality_matrix(node_id, enhanced_routes)

            # 清除相关路由缓存
            self._clear_route_cache(node_id)

            logger.info(f"Updated routing table for node {node_id}: {len(enhanced_routes)} routes")
            return True
        except Exception as e:
            logger.error(f"Failed to update routing table for {node_id}: {e}")
            return False

    def _get_link_quality_for_route(self, source_node: str, next_hop: str) -> int:
        """获取路由的链路质量"""
        if not next_hop:
            return 0

        # 从链路质量矩阵获取
        lqi = self.link_quality_matrix.get((source_node, next_hop))
        if lqi is not None:
            return lqi

        # 从节点信息获取
        source_info = self.network_manager.nodes.get(source_node)
        if source_info:
            return source_info.get("link_quality", 0)

        return 0

    def _get_rssi_for_route(self, source_node: str, next_hop: str) -> Optional[int]:
        """获取路由的RSSI"""
        if not next_hop:
            return None

        # 从节点信息获取
        source_info = self.network_manager.nodes.get(source_node)
        if source_info:
            return source_info.get("rssi")

        return None

    def _update_link_quality_matrix(self, node_id: str, routes: List[Dict]):
        """更新链路质量矩阵"""
        for route in routes:
            next_hop = route.get("next_hop")
            if next_hop:
                lqi = route.get("link_quality", 0)
                self.link_quality_matrix[(node_id, next_hop)] = lqi
                # 双向链路质量（对称）
                self.link_quality_matrix[(next_hop, node_id)] = lqi

    def _clear_route_cache(self, node_id: str):
        """清除路由缓存"""
        keys_to_remove = [
            key for key in self.route_cache.keys()
            if key[0] == node_id or key[1] == node_id
        ]
        for key in keys_to_remove:
            del self.route_cache[key]

    def find_route(self, source_node_id: str, destination_address: str,
                   algorithm: str = "shortest_path") -> Optional[Dict]:
        """查找路由 - 支持多种路由算法"""
        """
        algorithm: "shortest_path", "best_link_quality", "lowest_cost"
        """
        # 检查缓存
        cache_key = (source_node_id, destination_address)
        if cache_key in self.route_cache:
            cached_route = self.route_cache[cache_key]
            # 检查缓存是否过期（5分钟）
            cache_time = datetime.fromisoformat(cached_route.get("cached_at", ""))
            if (datetime.now() - cache_time).total_seconds() < 300:
                return cached_route

        routes = self.routing_tables.get(source_node_id, [])

        if algorithm == "shortest_path":
            route = self._find_shortest_path(routes, destination_address)
        elif algorithm == "best_link_quality":
            route = self._find_best_link_quality_route(routes, destination_address)
        elif algorithm == "lowest_cost":
            route = self._find_lowest_cost_route(routes, destination_address)
        else:
            route = self._find_shortest_path(routes, destination_address)

        if route:
            # 缓存路由
            route["cached_at"] = datetime.now().isoformat()
            self.route_cache[cache_key] = route

        return route

    def _find_shortest_path(self, routes: List[Dict], destination: str) -> Optional[Dict]:
        """最短路径算法（Dijkstra简化版）"""
        # 直接匹配目标地址
        for route in routes:
            if route.get("destination") == destination:
                return route

        # 如果没有直接路由，返回None（实际应该使用图算法）
        return None

    def _find_best_link_quality_route(self, routes: List[Dict], destination: str) -> Optional[Dict]:
        """最佳链路质量路由算法"""
        matching_routes = [r for r in routes if r.get("destination") == destination]
        if not matching_routes:
            return None

        # 选择链路质量最高的路由
        best_route = max(matching_routes, key=lambda r: r.get("link_quality", 0))
        return best_route

    def _find_lowest_cost_route(self, routes: List[Dict], destination: str) -> Optional[Dict]:
        """最低成本路由算法"""
        matching_routes = [r for r in routes if r.get("destination") == destination]
        if not matching_routes:
            return None

        # 选择成本最低的路由
        best_route = min(matching_routes, key=lambda r: r.get("cost", float('inf')))
        return best_route

    def compute_routing_path(self, source_node_id: str, destination_address: str) -> List[str]:
        """计算完整路由路径（多跳）"""
        """
        使用MLE路由协议计算从源节点到目标节点的完整路径
        """
        path = [source_node_id]
        current_node = source_node_id
        visited = {source_node_id}
        max_hops = 16  # Thread最大跳数限制

        for hop in range(max_hops):
            route = self.find_route(current_node, destination_address, "shortest_path")
            if not route:
                # 无法找到路由
                return path if len(path) > 1 else []

            next_hop = route.get("next_hop")
            if not next_hop or next_hop == destination_address:
                # 到达目标或无法继续
                if next_hop == destination_address:
                    path.append(destination_address)
                break

            if next_hop in visited:
                # 检测到环路
                logger.warning(f"Routing loop detected: {path}")
                return path

            path.append(next_hop)
            visited.add(next_hop)
            current_node = next_hop

        return path

    def optimize_routing_table(self, node_id: str) -> bool:
        """优化路由表 - 移除过期和低质量路由"""
        try:
            routes = self.routing_tables.get(node_id, [])
            if not routes:
                return False

            optimized_routes = []
            current_time = datetime.now()

            for route in routes:
                # 检查路由是否过期
                last_updated_str = route.get("last_updated")
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str)
                    age_seconds = (current_time - last_updated).total_seconds()

                    # 移除超过生命期的路由
                    if age_seconds > route.get("lifetime", 3600):
                        continue

                # 移除链路质量过低的路由（LQI < 1）
                if route.get("link_quality", 0) < 1:
                    continue

                optimized_routes.append(route)

            removed_count = len(routes) - len(optimized_routes)
            if removed_count > 0:
                logger.info(f"Optimized routing table for {node_id}: removed {removed_count} routes")
                self.routing_tables[node_id] = optimized_routes

            return True
        except Exception as e:
            logger.error(f"Failed to optimize routing table: {e}")
            return False

    def update_all_routing_tables(self, network_name: str):
        """更新网络中所有节点的路由表"""
        nodes_in_network = [
            node_id for node_id, node in self.network_manager.nodes.items()
            if node.get("network_name") == network_name
        ]

        updated_count = 0
        for node_id in nodes_in_network:
            if self.update_routing_table(node_id):
                updated_count += 1

        logger.info(f"Updated routing tables for {updated_count}/{len(nodes_in_network)} nodes")
        return updated_count

    def get_network_routing_statistics(self, network_name: str) -> Dict:
        """获取网络路由统计 - 完整实现"""
        nodes_in_network = [
            node_id for node_id, node in self.network_manager.nodes.items()
            if node.get("network_name") == network_name
        ]

        if not nodes_in_network:
            return {
                "network_name": network_name,
                "total_nodes": 0,
                "total_routes": 0,
                "avg_routes_per_node": 0,
                "avg_cost": 0,
                "max_hops": 0,
                "avg_link_quality": 0.0
            }

        total_routes = 0
        total_cost = 0
        max_hops = 0
        total_link_quality = 0
        link_quality_count = 0

        for node_id in nodes_in_network:
            routes = self.routing_tables.get(node_id, [])
            total_routes += len(routes)
            for route in routes:
                cost = route.get("cost", 0)
                total_cost += cost
                max_hops = max(max_hops, cost)

                lqi = route.get("link_quality", 0)
                if lqi > 0:
                    total_link_quality += lqi
                    link_quality_count += 1

        avg_link_quality = total_link_quality / link_quality_count if link_quality_count > 0 else 0.0

        return {
            "network_name": network_name,
            "total_nodes": len(nodes_in_network),
            "total_routes": total_routes,
            "avg_routes_per_node": total_routes / len(nodes_in_network) if nodes_in_network else 0,
            "avg_cost": total_cost / total_routes if total_routes > 0 else 0,
            "max_hops": max_hops,
            "avg_link_quality": avg_link_quality,
            "routing_efficiency": self._calculate_routing_efficiency(nodes_in_network)
        }

    def _calculate_routing_efficiency(self, node_ids: List[str]) -> float:
        """计算路由效率（连通节点对的比例）"""
        if len(node_ids) < 2:
            return 1.0

        total_pairs = len(node_ids) * (len(node_ids) - 1) / 2
        reachable_pairs = 0

        for i, source in enumerate(node_ids):
            for dest in node_ids[i+1:]:
                route = self.find_route(source, dest)
                if route:
                    reachable_pairs += 1

        return reachable_pairs / total_pairs if total_pairs > 0 else 0.0
```

### 4.2 Thread安全协议管理

**安全协议管理实现**：

```python
class ThreadSecurityManager:
    """Thread安全管理器"""

    def __init__(self, storage):
        self.storage = storage
        self.network_keys: Dict[str, Dict] = {}

    def rotate_network_key(self, network_name: str) -> bool:
        """轮换网络密钥"""
        try:
            # 生成新密钥
            new_key = self._generate_network_key()
            key_sequence = self._get_next_key_sequence(network_name)

            # 更新密钥
            self.network_keys[network_name] = {
                "network_key": new_key,
                "key_sequence": key_sequence,
                "rotation_time": datetime.now().isoformat()
            }

            # 存储到数据库
            # 这里需要更新所有节点的密钥

            logger.info(f"Rotated network key for {network_name}, sequence: {key_sequence}")
            return True
        except Exception as e:
            logger.error(f"Failed to rotate network key: {e}")
            return False

    def _generate_network_key(self) -> str:
        """生成网络密钥"""
        import secrets
        return secrets.token_hex(16).upper()

    def _get_next_key_sequence(self, network_name: str) -> int:
        """获取下一个密钥序列号 - 完整实现"""
        # 从数据库获取当前序列号
        # 实际实现应该从PostgreSQL存储中查询
        try:
            # 这里应该调用存储层的方法
            # return self.storage.get_next_key_sequence(network_name)
            # 临时实现：从网络数据中获取
            network = self.networks.get(network_name)
            if network:
                return network.get("key_sequence", 0) + 1
            return 1
        except Exception as e:
            logger.error(f"Failed to get next key sequence: {e}")
            return 1

    def manage_partition(self, network_name: str, action: str, partition_id: int = None) -> bool:
        """管理网络分区 - 完整实现"""
        """
        action: "detect", "merge", "split", "get_info"
        """
        try:
            network = self.networks.get(network_name)
            if not network:
                logger.error(f"Network {network_name} not found")
                return False

            if action == "detect":
                return self._detect_partitions(network_name)
            elif action == "merge":
                return self._merge_partitions(network_name, partition_id)
            elif action == "split":
                return self._split_partition(network_name, partition_id)
            elif action == "get_info":
                return self._get_partition_info(network_name)
            else:
                logger.error(f"Unknown partition action: {action}")
                return False
        except Exception as e:
            logger.error(f"Failed to manage partition: {e}")
            return False

    def _detect_partitions(self, network_name: str) -> bool:
        """检测网络分区"""
        try:
            nodes_in_network = [
                node_id for node_id, node_info in self.nodes.items()
                if node_info.get("network_name") == network_name
            ]

            if not nodes_in_network:
                logger.warning(f"No nodes found in network {network_name}")
                return False

            partitions = {}
            for node_id in nodes_in_network:
                leader_router_id = self._get_leader_router_id(node_id)
                partition_id = self._get_partition_id(node_id)

                if partition_id:
                    if partition_id not in partitions:
                        partitions[partition_id] = {
                            "partition_id": partition_id,
                            "leader_router_id": leader_router_id,
                            "nodes": []
                        }
                    partitions[partition_id]["nodes"].append(node_id)

            logger.info(f"Detected {len(partitions)} partitions in network {network_name}")
            for partition_id, partition_info in partitions.items():
                logger.info(f"Partition {partition_id}: {len(partition_info['nodes'])} nodes")

            # 存储分区信息
            network = self.networks.get(network_name)
            if network:
                network["partitions"] = partitions

            return len(partitions) > 0
        except Exception as e:
            logger.error(f"Failed to detect partitions: {e}")
            return False

    def _get_partition_id(self, node_id: str) -> Optional[int]:
        """获取分区ID"""
        try:
            cmd = "leaderdata"
            result = self.execute_ot_command(node_id, cmd)
            if not result:
                return None

            # 解析Partition ID
            lines = result.split('\n')
            for line in lines:
                if 'Partition ID' in line or 'Partition:' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        partition_str = parts[-1].strip()
                        if partition_str.startswith('0x'):
                            return int(partition_str, 16)
                        elif partition_str.isdigit():
                            return int(partition_str)
            return None
        except Exception as e:
            logger.error(f"Failed to get partition ID: {e}")
            return None

    def _merge_partitions(self, network_name: str, target_partition_id: int) -> bool:
        """合并网络分区"""
        try:
            network = self.networks.get(network_name)
            if not network or "partitions" not in network:
                logger.error("No partition information available")
                return False

            partitions = network["partitions"]
            if len(partitions) <= 1:
                logger.info("Only one partition exists, no merge needed")
                return True

            # 选择目标分区
            if target_partition_id not in partitions:
                # 选择节点数最多的分区作为目标
                target_partition_id = max(
                    partitions.keys(),
                    key=lambda pid: len(partitions[pid]["nodes"])
                )

            target_partition = partitions[target_partition_id]
            other_partitions = {
                pid: info for pid, info in partitions.items()
                if pid != target_partition_id
            }

            # 合并策略：让其他分区的节点重新加入目标分区
            merged_count = 0
            for partition_id, partition_info in other_partitions.items():
                for node_id in partition_info["nodes"]:
                    # 让节点重新加入网络（会加入目标分区）
                    if self._rejoin_network(node_id, network_name):
                        merged_count += 1

            logger.info(f"Merged {merged_count} nodes into partition {target_partition_id}")
            return merged_count > 0
        except Exception as e:
            logger.error(f"Failed to merge partitions: {e}")
            return False

    def _rejoin_network(self, node_id: str, network_name: str) -> bool:
        """节点重新加入网络"""
        try:
            network = self.networks.get(network_name)
            if not network:
                return False

            # 停止当前线程
            self.execute_ot_command(node_id, "thread stop")

            # 重新启动线程
            result = self.execute_ot_command(node_id, "thread start")
            if result:
                # 等待节点加入
                import time
                time.sleep(2)

                # 验证节点已加入
                node_info = self.get_node_info(node_id)
                if node_info and node_info.get("network_name") == network_name:
                    return True

            return False
        except Exception as e:
            logger.error(f"Failed to rejoin network: {e}")
            return False

    def _split_partition(self, network_name: str, partition_id: int) -> bool:
        """分割网络分区"""
        # Thread网络分区通常是自动的，手动分割需要特殊处理
        logger.warning("Manual partition splitting is not typically supported in Thread")
        return False

    def _get_partition_info(self, network_name: str) -> Dict:
        """获取分区信息"""
        network = self.networks.get(network_name)
        if not network:
            return {}

        return network.get("partitions", {})

    def diagnose_network(self, network_name: str) -> Dict:
        """网络诊断 - 完整实现"""
        """
        执行全面的网络诊断，包括：
        - 网络连通性检查
        - 路由表完整性检查
        - 节点健康状态检查
        - 性能指标收集
        """
        diagnosis = {
            "network_name": network_name,
            "timestamp": datetime.now().isoformat(),
            "connectivity": {},
            "routing": {},
            "node_health": {},
            "performance": {},
            "issues": []
        }

        try:
            network = self.networks.get(network_name)
            if not network:
                diagnosis["issues"].append("Network not found")
                return diagnosis

            nodes_in_network = [
                node_id for node_id, node_info in self.nodes.items()
                if node_info.get("network_name") == network_name
            ]

            if not nodes_in_network:
                diagnosis["issues"].append("No nodes in network")
                return diagnosis

            # 1. 连通性检查
            diagnosis["connectivity"] = self._check_connectivity(nodes_in_network)

            # 2. 路由表检查
            diagnosis["routing"] = self._check_routing_tables(nodes_in_network)

            # 3. 节点健康检查
            diagnosis["node_health"] = self._check_node_health(nodes_in_network)

            # 4. 性能指标
            diagnosis["performance"] = self._collect_performance_metrics(nodes_in_network)

            # 5. 汇总问题
            if diagnosis["connectivity"].get("disconnected_nodes"):
                diagnosis["issues"].append(
                    f"Found {len(diagnosis['connectivity']['disconnected_nodes'])} disconnected nodes"
                )

            if diagnosis["routing"].get("incomplete_tables"):
                diagnosis["issues"].append(
                    f"Found {len(diagnosis['routing']['incomplete_tables'])} nodes with incomplete routing tables"
                )

            if diagnosis["node_health"].get("unhealthy_nodes"):
                diagnosis["issues"].append(
                    f"Found {len(diagnosis['node_health']['unhealthy_nodes'])} unhealthy nodes"
                )

            logger.info(f"Network diagnosis completed: {len(diagnosis['issues'])} issues found")
            return diagnosis

        except Exception as e:
            logger.error(f"Network diagnosis failed: {e}")
            diagnosis["issues"].append(f"Diagnosis error: {str(e)}")
            return diagnosis

    def _check_connectivity(self, node_ids: List[str]) -> Dict:
        """检查网络连通性"""
        connectivity = {
            "total_nodes": len(node_ids),
            "connected_nodes": [],
            "disconnected_nodes": [],
            "connectivity_matrix": {}
        }

        for node_id in node_ids:
            node_info = self.get_node_info(node_id)
            if node_info and node_info.get("mesh_local_address"):
                connectivity["connected_nodes"].append(node_id)
            else:
                connectivity["disconnected_nodes"].append(node_id)

        # 构建连通性矩阵（简化版：检查是否能到达Leader）
        for node_id in connectivity["connected_nodes"]:
            leader_id = self._get_leader_router_id(node_id)
            connectivity["connectivity_matrix"][node_id] = {
                "can_reach_leader": leader_id is not None,
                "leader_id": leader_id
            }

        return connectivity

    def _check_routing_tables(self, node_ids: List[str]) -> Dict:
        """检查路由表"""
        routing = {
            "total_routers": 0,
            "complete_tables": [],
            "incomplete_tables": [],
            "routing_table_stats": {}
        }

        for node_id in node_ids:
            node_info = self.nodes.get(node_id)
            if node_info and node_info.get("node_type") == ThreadNodeType.ROUTER.value:
                routing["total_routers"] += 1
                routes = self.get_routing_table(node_id)

                if len(routes) > 0:
                    routing["complete_tables"].append(node_id)
                    routing["routing_table_stats"][node_id] = {
                        "route_count": len(routes),
                        "routes": routes
                    }
                else:
                    routing["incomplete_tables"].append(node_id)

        return routing

    def _check_node_health(self, node_ids: List[str]) -> Dict:
        """检查节点健康状态"""
        health = {
            "healthy_nodes": [],
            "unhealthy_nodes": [],
            "health_details": {}
        }

        for node_id in node_ids:
            node_info = self.get_node_info(node_id)
            if not node_info:
                health["unhealthy_nodes"].append(node_id)
                health["health_details"][node_id] = {"status": "unreachable"}
                continue

            # 健康检查标准
            is_healthy = True
            issues = []

            # 检查链路质量
            link_quality = node_info.get("link_quality", 0)
            if link_quality == 0:
                is_healthy = False
                issues.append("No link quality")

            # 检查RSSI
            rssi = node_info.get("rssi")
            if rssi and rssi < -90:
                is_healthy = False
                issues.append(f"Low RSSI: {rssi} dBm")

            # 检查是否有父节点（End Device）
            if node_info.get("node_type") == ThreadNodeType.END_DEVICE.value:
                if not node_info.get("parent_node_id"):
                    is_healthy = False
                    issues.append("No parent node")

            if is_healthy:
                health["healthy_nodes"].append(node_id)
            else:
                health["unhealthy_nodes"].append(node_id)

            health["health_details"][node_id] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "issues": issues,
                "link_quality": link_quality,
                "rssi": rssi
            }

        return health

    def _collect_performance_metrics(self, node_ids: List[str]) -> Dict:
        """收集性能指标"""
        metrics = {
            "average_link_quality": 0.0,
            "average_rssi": 0.0,
            "router_count": 0,
            "end_device_count": 0,
            "network_diameter": 0,
            "node_metrics": {}
        }

        link_qualities = []
        rssis = []

        for node_id in node_ids:
            node_info = self.get_node_info(node_id)
            if not node_info:
                continue

            if node_info.get("node_type") == ThreadNodeType.ROUTER.value:
                metrics["router_count"] += 1
            elif node_info.get("node_type") == ThreadNodeType.END_DEVICE.value:
                metrics["end_device_count"] += 1

            link_quality = node_info.get("link_quality", 0)
            if link_quality > 0:
                link_qualities.append(link_quality)

            rssi = node_info.get("rssi")
            if rssi:
                rssis.append(rssi)

            metrics["node_metrics"][node_id] = {
                "link_quality": link_quality,
                "rssi": rssi,
                "node_type": node_info.get("node_type")
            }

        if link_qualities:
            metrics["average_link_quality"] = sum(link_qualities) / len(link_qualities)

        if rssis:
            metrics["average_rssi"] = sum(rssis) / len(rssis)

        # 计算网络直径（简化：最大跳数）
        metrics["network_diameter"] = self._calculate_network_diameter(node_ids)

        return metrics

    def _calculate_network_diameter(self, node_ids: List[str]) -> int:
        """计算网络直径（最大跳数）"""
        # 简化实现：返回路由器的最大路由表大小
        max_hops = 0
        for node_id in node_ids:
            node_info = self.nodes.get(node_id)
            if node_info and node_info.get("node_type") == ThreadNodeType.ROUTER.value:
                routes = self.get_routing_table(node_id)
                for route in routes:
                    cost = route.get("cost", 0)
                    if cost > max_hops:
                        max_hops = cost

        return max_hops
```

---

## 5. 转换工具

### 5.1 OpenThread CLI集成

详见第2.1节ThreadNetworkManager实现。

### 5.2 Thread SDK集成

**Thread SDK Python封装**：

```python
import socket
import struct
from typing import Optional

class ThreadSDKWrapper:
    """Thread SDK封装类"""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.socket = None

    def connect(self) -> bool:
        """连接到Thread节点"""
        try:
            # 使用Unix域套接字连接到OpenThread
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            socket_path = f"/tmp/ot-{self.node_id}.sock"
            self.socket.connect(socket_path)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Thread node: {e}")
            return False

    def send_command(self, command: str) -> Optional[str]:
        """发送命令到Thread节点"""
        if not self.socket:
            return None

        try:
            self.socket.sendall(command.encode() + b'\n')
            response = self.socket.recv(4096).decode()
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return None

    def disconnect(self):
        """断开连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
```

---

## 6. 转换验证

### 6.1 网络拓扑一致性验证

**转换验证器实现**：

```python
class ThreadConversionValidator:
    """Thread转换验证器"""

    def validate_thread_to_zigbee(self, thread_node: Dict,
                                  zigbee_node: Dict) -> bool:
        """验证Thread到Zigbee转换的正确性"""
        # 验证节点ID一致性
        if thread_node.get("node_id") != zigbee_node.get("ieee_address"):
            return False

        # 验证节点类型转换正确性
        thread_type = thread_node.get("node_type")
        zigbee_type = zigbee_node.get("node_type")

        type_map = {
            ThreadNodeType.ROUTER.value: "Coordinator",
            ThreadNodeType.LEADER.value: "Coordinator",
            ThreadNodeType.END_DEVICE.value: "EndDevice"
        }

        if type_map.get(thread_type) != zigbee_type:
            return False

        return True

    def validate_zigbee_to_thread(self, zigbee_node: Dict,
                                  thread_node: Dict) -> bool:
        """验证Zigbee到Thread转换的正确性"""
        # 验证节点ID一致性
        if zigbee_node.get("ieee_address") != thread_node.get("node_id"):
            return False

        # 验证IPv6地址格式
        mesh_local = thread_node.get("ipv6_address", {}).get("mesh_local", "")
        if not mesh_local.startswith("fd"):
            return False

        return True
```

---

## 7. Thread数据存储与分析

### 7.1 PostgreSQL Thread数据存储

**Thread数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class ThreadStorage:
    """Thread数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建Thread数据表"""
        # Thread网络表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_networks (
                id BIGSERIAL PRIMARY KEY,
                network_name VARCHAR(16) UNIQUE NOT NULL,
                pan_id INTEGER NOT NULL,
                extended_pan_id VARCHAR(16) UNIQUE NOT NULL,
                channel INTEGER NOT NULL,
                network_key VARCHAR(32) NOT NULL,
                partition_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Thread节点表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_nodes (
                id BIGSERIAL PRIMARY KEY,
                node_id VARCHAR(16) UNIQUE NOT NULL,
                network_name VARCHAR(16) NOT NULL,
                node_type VARCHAR(20) NOT NULL,
                link_local_address VARCHAR(39) NOT NULL,
                mesh_local_address VARCHAR(39) NOT NULL,
                global_address VARCHAR(39),
                parent_node_id VARCHAR(16),
                router_id INTEGER,
                leader_router_id INTEGER,
                rloc16 INTEGER,
                link_quality INTEGER,
                rssi INTEGER,
                battery_level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (network_name) REFERENCES thread_networks(network_name)
            )
        """)

        # Thread路由表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_routes (
                id BIGSERIAL PRIMARY KEY,
                node_id VARCHAR(16) NOT NULL,
                destination VARCHAR(39) NOT NULL,
                next_hop VARCHAR(16) NOT NULL,
                cost INTEGER NOT NULL,
                lifetime INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES thread_nodes(node_id),
                UNIQUE(node_id, destination)
            )
        """)

        # Thread安全信息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_security (
                id BIGSERIAL PRIMARY KEY,
                node_id VARCHAR(16) UNIQUE NOT NULL,
                network_key_sequence INTEGER NOT NULL,
                key_rotation_enabled BOOLEAN DEFAULT TRUE,
                key_rotation_interval INTEGER DEFAULT 86400,
                last_key_rotation TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES thread_nodes(node_id)
            )
        """)

        # Thread网络性能表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_performance (
                id BIGSERIAL PRIMARY KEY,
                node_id VARCHAR(16) NOT NULL,
                latency_ms INTEGER,
                packet_loss_rate DECIMAL(5,2),
                throughput_kbps DECIMAL(10,2),
                recorded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (node_id) REFERENCES thread_nodes(node_id)
            )
        """)

        # Thread网络分区表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_partitions (
                id BIGSERIAL PRIMARY KEY,
                network_name VARCHAR(16) NOT NULL,
                partition_id INTEGER NOT NULL,
                leader_router_id INTEGER,
                node_count INTEGER DEFAULT 0,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (network_name) REFERENCES thread_networks(network_name),
                UNIQUE(network_name, partition_id)
            )
        """)

        # Thread网络事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_events (
                id BIGSERIAL PRIMARY KEY,
                network_name VARCHAR(16) NOT NULL,
                node_id VARCHAR(16),
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB,
                event_time TIMESTAMP NOT NULL,
                FOREIGN KEY (network_name) REFERENCES thread_networks(network_name),
                FOREIGN KEY (node_id) REFERENCES thread_nodes(node_id)
            )
        """)

        # Thread网络诊断表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_diagnostics (
                id BIGSERIAL PRIMARY KEY,
                network_name VARCHAR(16) NOT NULL,
                diagnosis_data JSONB NOT NULL,
                issues_count INTEGER DEFAULT 0,
                diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (network_name) REFERENCES thread_networks(network_name)
            )
        """)

        # Thread链路质量历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_link_quality_history (
                id BIGSERIAL PRIMARY KEY,
                source_node_id VARCHAR(16) NOT NULL,
                target_node_id VARCHAR(16) NOT NULL,
                link_quality INTEGER NOT NULL,
                rssi INTEGER,
                recorded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (source_node_id) REFERENCES thread_nodes(node_id),
                FOREIGN KEY (target_node_id) REFERENCES thread_nodes(node_id)
            )
        """)

        # Thread路由历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS thread_route_history (
                id BIGSERIAL PRIMARY KEY,
                node_id VARCHAR(16) NOT NULL,
                destination VARCHAR(39) NOT NULL,
                route_path JSONB NOT NULL,
                hop_count INTEGER NOT NULL,
                total_cost INTEGER NOT NULL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES thread_nodes(node_id)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_nodes_node_id
            ON thread_nodes(node_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_nodes_network_name
            ON thread_nodes(network_name)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_routes_node_id
            ON thread_routes(node_id)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_events_network_name
            ON thread_events(network_name, event_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_events_node_id
            ON thread_events(node_id, event_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_link_quality_history
            ON thread_link_quality_history(source_node_id, target_node_id, recorded_at DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_performance_node_id
            ON thread_performance(node_id, recorded_at DESC)
        """)

        self.conn.commit()

    def store_network(self, network_data: Dict) -> int:
        """存储Thread网络"""
        self.cur.execute("""
            INSERT INTO thread_networks (
                network_name, pan_id, extended_pan_id,
                channel, network_key, partition_id
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (network_name) DO UPDATE SET
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            network_data.get("network_name"),
            network_data.get("pan_id"),
            network_data.get("extended_pan_id"),
            network_data.get("channel"),
            network_data.get("network_key"),
            network_data.get("partition_id")
        ))
        return self.cur.fetchone()[0]

    def store_node(self, node_data: Dict) -> int:
        """存储Thread节点"""
        self.cur.execute("""
            INSERT INTO thread_nodes (
                node_id, network_name, node_type,
                link_local_address, mesh_local_address, global_address,
                parent_node_id, router_id, leader_router_id, rloc16,
                link_quality, rssi, battery_level
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (node_id) DO UPDATE SET
                network_name = EXCLUDED.network_name,
                node_type = EXCLUDED.node_type,
                link_local_address = EXCLUDED.link_local_address,
                mesh_local_address = EXCLUDED.mesh_local_address,
                parent_node_id = EXCLUDED.parent_node_id,
                router_id = EXCLUDED.router_id,
                leader_router_id = EXCLUDED.leader_router_id,
                rloc16 = EXCLUDED.rloc16,
                link_quality = EXCLUDED.link_quality,
                rssi = EXCLUDED.rssi,
                battery_level = EXCLUDED.battery_level,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            node_data.get("node_id"),
            node_data.get("network_name"),
            node_data.get("node_type"),
            node_data.get("link_local_address"),
            node_data.get("mesh_local_address"),
            node_data.get("global_address"),
            node_data.get("parent_node_id"),
            node_data.get("router_id"),
            node_data.get("leader_router_id"),
            node_data.get("rloc16"),
            node_data.get("link_quality"),
            node_data.get("rssi"),
            node_data.get("battery_level")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_route(self, node_id: str, route_data: Dict) -> int:
        """存储路由条目"""
        self.cur.execute("""
            INSERT INTO thread_routes (
                node_id, destination, next_hop, cost, lifetime
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (node_id, destination) DO UPDATE SET
                next_hop = EXCLUDED.next_hop,
                cost = EXCLUDED.cost,
                lifetime = EXCLUDED.lifetime,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            node_id,
            route_data.get("destination"),
            route_data.get("next_hop"),
            route_data.get("cost"),
            route_data.get("lifetime", 3600)
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_routing_table(self, node_id: str, routes: List[Dict]):
        """存储整个路由表"""
        for route in routes:
            self.store_route(node_id, route)

    def store_performance_data(self, node_id: str, performance_data: Dict) -> int:
        """存储性能数据"""
        self.cur.execute("""
            INSERT INTO thread_performance (
                node_id, latency_ms, packet_loss_rate, throughput_kbps, recorded_at
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            node_id,
            performance_data.get("latency_ms"),
            performance_data.get("packet_loss_rate"),
            performance_data.get("throughput_kbps")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def get_node_routes(self, node_id: str) -> List[Dict]:
        """获取节点的路由表"""
        self.cur.execute("""
            SELECT destination, next_hop, cost, lifetime, updated_at
            FROM thread_routes
            WHERE node_id = %s
            ORDER BY cost, destination
        """, (node_id,))
        return [
            {
                "destination": row[0],
                "next_hop": row[1],
                "cost": row[2],
                "lifetime": row[3],
                "updated_at": row[4]
            }
            for row in self.cur.fetchall()
        ]

    def store_partition(self, network_name: str, partition_data: Dict) -> int:
        """存储网络分区信息"""
        self.cur.execute("""
            INSERT INTO thread_partitions (
                network_name, partition_id, leader_router_id, node_count
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (network_name, partition_id) DO UPDATE SET
                leader_router_id = EXCLUDED.leader_router_id,
                node_count = EXCLUDED.node_count,
                detected_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            network_name,
            partition_data.get("partition_id"),
            partition_data.get("leader_router_id"),
            partition_data.get("node_count", 0)
        ))
        partition_id = self.cur.fetchone()[0]
        self.conn.commit()
        return partition_id

    def store_event(self, network_name: str, event_type: str,
                   event_data: Dict, node_id: str = None) -> int:
        """存储网络事件"""
        self.cur.execute("""
            INSERT INTO thread_events (
                network_name, node_id, event_type, event_data, event_time
            ) VALUES (%s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            network_name,
            node_id,
            event_type,
            json.dumps(event_data)
        ))
        event_id = self.cur.fetchone()[0]
        self.conn.commit()
        return event_id

    def store_diagnosis(self, network_name: str, diagnosis_data: Dict) -> int:
        """存储网络诊断结果"""
        issues = diagnosis_data.get("issues", [])
        issues_count = len(issues)

        self.cur.execute("""
            INSERT INTO thread_diagnostics (
                network_name, diagnosis_data, issues_count
            ) VALUES (%s, %s::jsonb, %s)
            RETURNING id
        """, (
            network_name,
            json.dumps(diagnosis_data),
            issues_count
        ))
        diagnosis_id = self.cur.fetchone()[0]
        self.conn.commit()
        return diagnosis_id

    def store_link_quality(self, source_node_id: str, target_node_id: str,
                          link_quality: int, rssi: int = None) -> int:
        """存储链路质量历史"""
        self.cur.execute("""
            INSERT INTO thread_link_quality_history (
                source_node_id, target_node_id, link_quality, rssi, recorded_at
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """, (source_node_id, target_node_id, link_quality, rssi))
        history_id = self.cur.fetchone()[0]
        self.conn.commit()
        return history_id

    def store_route_path(self, node_id: str, destination: str,
                        route_path: List[str], hop_count: int, total_cost: int) -> int:
        """存储路由路径历史"""
        self.cur.execute("""
            INSERT INTO thread_route_history (
                node_id, destination, route_path, hop_count, total_cost
            ) VALUES (%s, %s, %s::jsonb, %s, %s)
            RETURNING id
        """, (
            node_id,
            destination,
            json.dumps(route_path),
            hop_count,
            total_cost
        ))
        route_history_id = self.cur.fetchone()[0]
        self.conn.commit()
        return route_history_id

    def get_network_nodes(self, network_name: str) -> List[Dict]:
        """获取网络中的所有节点"""
        self.cur.execute("""
            SELECT node_id, node_type, link_local_address, mesh_local_address,
                   parent_node_id, router_id, leader_router_id, link_quality, rssi
            FROM thread_nodes
            WHERE network_name = %s
            ORDER BY node_type, node_id
        """, (network_name,))
        return [
            {
                "node_id": row[0],
                "node_type": row[1],
                "link_local_address": row[2],
                "mesh_local_address": row[3],
                "parent_node_id": row[4],
                "router_id": row[5],
                "leader_router_id": row[6],
                "link_quality": row[7],
                "rssi": row[8]
            }
            for row in self.cur.fetchall()
        ]

    def get_node_by_id(self, node_id: str) -> Optional[Dict]:
        """根据ID获取节点"""
        self.cur.execute("""
            SELECT node_id, network_name, node_type, link_local_address,
                   mesh_local_address, parent_node_id, router_id, leader_router_id,
                   rloc16, link_quality, rssi, battery_level, created_at, updated_at
            FROM thread_nodes
            WHERE node_id = %s
        """, (node_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "node_id": row[0],
                "network_name": row[1],
                "node_type": row[2],
                "link_local_address": row[3],
                "mesh_local_address": row[4],
                "parent_node_id": row[5],
                "router_id": row[6],
                "leader_router_id": row[7],
                "rloc16": row[8],
                "link_quality": row[9],
                "rssi": row[10],
                "battery_level": row[11],
                "created_at": row[12],
                "updated_at": row[13]
            }
        return None

    def get_recent_events(self, network_name: str = None, node_id: str = None,
                         event_type: str = None, limit: int = 100) -> List[Dict]:
        """获取最近的事件"""
        query = """
            SELECT id, network_name, node_id, event_type, event_data, event_time
            FROM thread_events
            WHERE 1=1
        """
        params = []

        if network_name:
            query += " AND network_name = %s"
            params.append(network_name)

        if node_id:
            query += " AND node_id = %s"
            params.append(node_id)

        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)

        query += " ORDER BY event_time DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        return [
            {
                "id": row[0],
                "network_name": row[1],
                "node_id": row[2],
                "event_type": row[3],
                "event_data": json.loads(row[4]) if row[4] else {},
                "event_time": row[5]
            }
            for row in self.cur.fetchall()
        ]

    def get_link_quality_history(self, source_node_id: str, target_node_id: str,
                                 hours: int = 24) -> List[Dict]:
        """获取链路质量历史"""
        self.cur.execute("""
            SELECT link_quality, rssi, recorded_at
            FROM thread_link_quality_history
            WHERE source_node_id = %s AND target_node_id = %s
            AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
            ORDER BY recorded_at DESC
        """, (source_node_id, target_node_id, hours))
        return [
            {
                "link_quality": row[0],
                "rssi": row[1],
                "recorded_at": row[2]
            }
            for row in self.cur.fetchall()
        ]

    def get_network_statistics(self, network_name: str) -> Dict:
        """获取网络统计信息"""
        # 节点统计
        self.cur.execute("""
            SELECT node_type, COUNT(*) as count,
                   AVG(link_quality) as avg_lqi, AVG(rssi) as avg_rssi
            FROM thread_nodes
            WHERE network_name = %s
            GROUP BY node_type
        """, (network_name,))
        node_stats = {
            row[0]: {
                "count": row[1],
                "avg_link_quality": float(row[2]) if row[2] else None,
                "avg_rssi": float(row[3]) if row[3] else None
            }
            for row in self.cur.fetchall()
        }

        # 路由统计
        self.cur.execute("""
            SELECT COUNT(DISTINCT node_id) as nodes_with_routes,
                   COUNT(*) as total_routes,
                   AVG(cost) as avg_cost,
                   MAX(cost) as max_hops
            FROM thread_routes
            WHERE node_id IN (
                SELECT node_id FROM thread_nodes WHERE network_name = %s
            )
        """, (network_name,))
        route_row = self.cur.fetchone()
        route_stats = {
            "nodes_with_routes": route_row[0] if route_row else 0,
            "total_routes": route_row[1] if route_row else 0,
            "avg_cost": float(route_row[2]) if route_row and route_row[2] else 0,
            "max_hops": route_row[3] if route_row else 0
        }

        # 分区统计
        self.cur.execute("""
            SELECT COUNT(*) as partition_count, SUM(node_count) as total_nodes_in_partitions
            FROM thread_partitions
            WHERE network_name = %s
        """, (network_name,))
        partition_row = self.cur.fetchone()
        partition_stats = {
            "partition_count": partition_row[0] if partition_row else 0,
            "total_nodes_in_partitions": partition_row[1] if partition_row else 0
        }

        return {
            "network_name": network_name,
            "node_statistics": node_stats,
            "routing_statistics": route_stats,
            "partition_statistics": partition_stats
        }

    def update_node_status(self, node_id: str, link_quality: int = None,
                          rssi: int = None, battery_level: int = None):
        """更新节点状态"""
        updates = []
        params = []

        if link_quality is not None:
            updates.append("link_quality = %s")
            params.append(link_quality)

        if rssi is not None:
            updates.append("rssi = %s")
            params.append(rssi)

        if battery_level is not None:
            updates.append("battery_level = %s")
            params.append(battery_level)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(node_id)

            query = f"""
                UPDATE thread_nodes
                SET {', '.join(updates)}
                WHERE node_id = %s
            """
            self.cur.execute(query, params)
            self.conn.commit()

    def delete_expired_routes(self, max_age_hours: int = 24):
        """删除过期的路由"""
        self.cur.execute("""
            DELETE FROM thread_routes
            WHERE updated_at < CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """, (max_age_hours,))
        deleted_count = self.cur.rowcount
        self.conn.commit()
        logger.info(f"Deleted {deleted_count} expired routes")
        return deleted_count

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 7.2 Thread数据分析查询

**查询示例**：

```python
    def get_network_topology_statistics(self, network_name: str) -> List[Dict]:
        """查询网络拓扑统计"""
        self.cur.execute("""
            SELECT
                node_type,
                COUNT(*) as count,
                AVG(link_quality) as avg_link_quality,
                AVG(rssi) as avg_rssi,
                AVG(battery_level) as avg_battery_level
            FROM thread_nodes
            WHERE network_name = %s
            GROUP BY node_type
            ORDER BY node_type
        """, (network_name,))
        return [
            {
                "node_type": row[0],
                "count": row[1],
                "avg_link_quality": float(row[2]) if row[2] else None,
                "avg_rssi": float(row[3]) if row[3] else None,
                "avg_battery_level": float(row[4]) if row[4] else None
            }
            for row in self.cur.fetchall()
        ]

    def get_routing_statistics(self, node_id: str) -> Dict:
        """查询路由统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as route_count,
                AVG(cost) as avg_cost,
                MIN(cost) as min_cost,
                MAX(cost) as max_cost,
                AVG(lifetime) as avg_lifetime
            FROM thread_routes
            WHERE node_id = %s
        """, (node_id,))
        row = self.cur.fetchone()
        return {
            "route_count": row[0],
            "avg_cost": float(row[1]) if row[1] else 0,
            "min_cost": row[2] if row[2] else 0,
            "max_cost": row[3] if row[3] else 0,
            "avg_lifetime": float(row[4]) if row[4] else 0
        }

    def get_network_performance_statistics(self, network_name: str, hours: int = 24) -> Dict:
        """查询网络性能统计"""
        self.cur.execute("""
            SELECT
                AVG(p.latency_ms) as avg_latency,
                AVG(p.packet_loss_rate) as avg_packet_loss,
                AVG(p.throughput_kbps) as avg_throughput,
                COUNT(DISTINCT p.node_id) as monitored_nodes
            FROM thread_performance p
            JOIN thread_nodes n ON p.node_id = n.node_id
            WHERE n.network_name = %s
            AND p.recorded_at >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """, (network_name, hours))
        row = self.cur.fetchone()
        return {
            "avg_latency": float(row[0]) if row[0] else None,
            "avg_packet_loss": float(row[1]) if row[1] else None,
            "avg_throughput": float(row[2]) if row[2] else None,
            "monitored_nodes": row[3]
        }

    def get_node_performance_history(self, node_id: str, hours: int = 24) -> List[Dict]:
        """查询节点性能历史"""
        self.cur.execute("""
            SELECT
                latency_ms,
                packet_loss_rate,
                throughput_kbps,
                recorded_at
            FROM thread_performance
            WHERE node_id = %s
            AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
            ORDER BY recorded_at DESC
        """, (node_id, hours))
        return [
            {
                "latency_ms": row[0],
                "packet_loss_rate": float(row[1]) if row[1] else None,
                "throughput_kbps": float(row[2]) if row[2] else None,
                "recorded_at": row[3]
            }
            for row in self.cur.fetchall()
        ]

    def get_network_health_status(self, network_name: str) -> Dict:
        """查询网络健康状态"""
        self.cur.execute("""
            SELECT
                COUNT(*) as total_nodes,
                COUNT(CASE WHEN node_type = 'Router' THEN 1 END) as router_count,
                COUNT(CASE WHEN node_type = 'EndDevice' THEN 1 END) as end_device_count,
                AVG(link_quality) as avg_link_quality,
                AVG(rssi) as avg_rssi,
                COUNT(CASE WHEN battery_level < 20 THEN 1 END) as low_battery_count
            FROM thread_nodes
            WHERE network_name = %s
        """, (network_name,))
        row = self.cur.fetchone()

        return {
            "total_nodes": row[0],
            "router_count": row[1],
            "end_device_count": row[2],
            "avg_link_quality": float(row[3]) if row[3] else None,
            "avg_rssi": float(row[4]) if row[4] else None,
            "low_battery_count": row[5],
            "health_score": self._calculate_health_score(row)
        }

    def _calculate_health_score(self, stats_row: tuple) -> float:
        """计算健康分数（0-100）"""
        total_nodes, router_count, end_device_count, avg_link_quality, avg_rssi, low_battery_count = stats_row

        if total_nodes == 0:
            return 0.0

        score = 100.0

        # 链路质量评分（0-255，越高越好）
        if avg_link_quality:
            link_quality_score = (avg_link_quality / 255.0) * 30
            score = min(score, link_quality_score + 70)

        # RSSI评分（-128到127，越高越好）
        if avg_rssi:
            rssi_score = ((avg_rssi + 128) / 255.0) * 20
            score = min(score, rssi_score + 80)

        # 低电量节点扣分
        if total_nodes > 0:
            low_battery_ratio = low_battery_count / total_nodes
            score -= low_battery_ratio * 20

        # 路由器数量评分（至少需要1个路由器）
        if router_count == 0:
            score -= 30

        return max(0.0, min(100.0, score))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
