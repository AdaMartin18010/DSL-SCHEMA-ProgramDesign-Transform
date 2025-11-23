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
        """获取Leader路由器ID"""
        cmd = "leaderdata"
        result = self.execute_ot_command(node_id, cmd)
        if result:
            # 解析Leader数据
            # 实际实现需要解析OpenThread输出格式
            return 1  # 简化实现
        return None

    def _get_parent_info(self, node_id: str) -> Optional[Dict]:
        """获取父节点信息"""
        cmd = "parent"
        result = self.execute_ot_command(node_id, cmd)
        if result:
            # 解析父节点信息
            return {
                "parent_id": None,  # 需要从输出解析
                "rssi": -70  # 需要从输出解析
            }
        return None

    def _get_link_quality(self, node_id: str) -> int:
        """获取链路质量"""
        cmd = "linkquality"
        result = self.execute_ot_command(node_id, cmd)
        if result and result.isdigit():
            return int(result)
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
    """Thread路由管理器"""

    def __init__(self, network_manager: ThreadNetworkManager):
        self.network_manager = network_manager
        self.routing_tables: Dict[str, List[Dict]] = {}

    def update_routing_table(self, node_id: str):
        """更新节点的路由表"""
        routes = self.network_manager.get_routing_table(node_id)
        self.routing_tables[node_id] = routes
        logger.info(f"Updated routing table for node {node_id}: {len(routes)} routes")

    def find_route(self, source_node_id: str, destination_address: str) -> Optional[Dict]:
        """查找路由"""
        routes = self.routing_tables.get(source_node_id, [])
        for route in routes:
            if route["destination"] == destination_address:
                return route
        return None

    def get_network_routing_statistics(self, network_name: str) -> Dict:
        """获取网络路由统计"""
        nodes_in_network = [
            node_id for node_id, node in self.network_manager.nodes.items()
            if node.get("network_name") == network_name
        ]

        total_routes = 0
        total_cost = 0
        max_hops = 0

        for node_id in nodes_in_network:
            routes = self.routing_tables.get(node_id, [])
            total_routes += len(routes)
            for route in routes:
                total_cost += route.get("cost", 0)
                max_hops = max(max_hops, route.get("cost", 0))

        return {
            "network_name": network_name,
            "total_nodes": len(nodes_in_network),
            "total_routes": total_routes,
            "avg_routes_per_node": total_routes / len(nodes_in_network) if nodes_in_network else 0,
            "avg_cost": total_cost / total_routes if total_routes > 0 else 0,
            "max_hops": max_hops
        }
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
        """获取下一个密钥序列号"""
        # 从数据库获取当前序列号
        return 1  # 简化实现
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
