# IEC61850 Schema转换体系

## 📑 目录

- [IEC61850 Schema转换体系](#iec61850-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. SCL解析实现](#2-scl解析实现)
    - [2.1 SCL文件解析器](#21-scl文件解析器)
    - [2.2 IED配置解析](#22-ied配置解析)
  - [3. MMS协议实现](#3-mms协议实现)
    - [3.1 MMS客户端实现](#31-mms客户端实现)
    - [3.2 MMS服务调用](#32-mms服务调用)
  - [4. GOOSE/SMV服务实现](#4-goosesmv服务实现)
    - [4.1 GOOSE服务实现](#41-goose服务实现)
    - [4.2 SMV服务实现](#42-smv服务实现)
  - [5. IEC61850数据存储与分析](#5-iec61850数据存储与分析)
    - [5.1 PostgreSQL IEC61850数据存储](#51-postgresql-iec61850数据存储)
    - [5.2 IEC61850数据分析查询](#52-iec61850数据分析查询)

---

## 1. 转换体系概述

IEC61850 Schema转换体系支持SCL配置、MMS服务、
GOOSE/SMV服务、数据库存储之间的转换。

### 1.1 转换目标

1. **SCL到数据库转换**：SCL配置文件到PostgreSQL存储
2. **MMS服务调用**：MMS协议服务调用和数据采集
3. **GOOSE/SMV服务**：GOOSE和SMV服务实现
4. **数据到数据库转换**：IEC61850数据到PostgreSQL存储

---

## 2. SCL解析实现

### 2.1 SCL文件解析器

**完整的SCL解析实现**：

```python
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SCLParser:
    """SCL文件解析器"""

    def __init__(self):
        self.namespaces = {
            'scl': 'http://www.iec.ch/61850/2003/SCL'
        }

    def parse_scl_file(self, scl_file_path: str) -> Dict:
        """解析SCL文件 - 增强错误处理"""
        # 输入验证
        if not scl_file_path:
            raise ValueError("SCL file path cannot be empty")

        if not isinstance(scl_file_path, str):
            raise TypeError(f"SCL file path must be a string, got {type(scl_file_path)}")

        import os
        if not os.path.exists(scl_file_path):
            raise FileNotFoundError(f"SCL file not found: {scl_file_path}")

        if not os.path.isfile(scl_file_path):
            raise ValueError(f"Path is not a file: {scl_file_path}")

        # 检查文件大小（防止过大文件）
        file_size = os.path.getsize(scl_file_path)
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"SCL file too large: {file_size} bytes (max {MAX_FILE_SIZE})")

        try:
            tree = ET.parse(scl_file_path)
            root = tree.getroot()

            # 验证根元素
            if root.tag is None or not root.tag.endswith('SCL'):
                raise ValueError(f"Invalid SCL file: root element is not SCL, got {root.tag}")

            scl_data = {
                "header": self._parse_header(root),
                "ieds": self._parse_ieds(root),
                "communication": self._parse_communication(root),
                "data_type_templates": self._parse_data_type_templates(root)
            }

            # 验证解析结果
            if not scl_data.get("ieds"):
                logger.warning("No IEDs found in SCL file")

            logger.info(f"Successfully parsed SCL file: {scl_file_path} ({len(scl_data.get('ieds', []))} IEDs)")
            return scl_data

        except ET.ParseError as e:
            logger.error(f"XML parsing error in SCL file {scl_file_path}: {e}")
            raise ValueError(f"Invalid XML format in SCL file: {e}") from e
        except FileNotFoundError:
            raise
        except PermissionError as e:
            logger.error(f"Permission denied reading SCL file {scl_file_path}: {e}")
            raise PermissionError(f"Cannot read SCL file: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error parsing SCL file {scl_file_path}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse SCL file: {e}") from e

    def _parse_header(self, root: ET.Element) -> Dict:
        """解析SCL Header"""
        header_elem = root.find('.//scl:Header', self.namespaces)
        if header_elem is None:
            return {}

        return {
            "id": header_elem.get("id", ""),
            "version": header_elem.get("version", ""),
            "revision": header_elem.get("revision", ""),
            "tool_id": header_elem.get("toolID", ""),
            "name_structure": header_elem.get("nameStructure", "")
        }

    def _parse_ieds(self, root: ET.Element) -> List[Dict]:
        """解析IED列表"""
        ieds = []
        ied_elements = root.findall('.//scl:IED', self.namespaces)

        for ied_elem in ied_elements:
            ied_data = {
                "ied_name": ied_elem.get("name", ""),
                "ied_desc": ied_elem.get("desc", ""),
                "ied_type": ied_elem.get("type", ""),
                "ied_manufacturer": ied_elem.get("manufacturer", ""),
                "ied_config_version": ied_elem.get("configVersion", ""),
                "access_points": self._parse_access_points(ied_elem),
                "services": self._parse_services(ied_elem),
                "server": self._parse_server(ied_elem)
            }
            ieds.append(ied_data)

        return ieds

    def _parse_access_points(self, ied_elem: ET.Element) -> List[Dict]:
        """解析AccessPoint列表"""
        access_points = []
        ap_elements = ied_elem.findall('.//scl:AccessPoint', self.namespaces)

        for ap_elem in ap_elements:
            ap_data = {
                "ap_name": ap_elem.get("name", ""),
                "ap_desc": ap_elem.get("desc", ""),
                "router": ap_elem.get("router", "false") == "true",
                "clock": ap_elem.get("clock", "false") == "true",
                "server": self._parse_server(ap_elem)
            }
            access_points.append(ap_data)

        return access_points

    def _parse_services(self, ied_elem: ET.Element) -> Dict:
        """解析Services"""
        services_elem = ied_elem.find('.//scl:Services', self.namespaces)
        if services_elem is None:
            return {}

        return {
            "dyn_association": services_elem.get("DynAssociation", "false") == "true",
            "get_directory": services_elem.get("GetDirectory", "false") == "true",
            "get_data_object_definition": services_elem.get("GetDataObjectDefinition", "false") == "true",
            "data_object_directory": services_elem.get("DataObjectDirectory", "false") == "true",
            "get_data_set_value": services_elem.get("GetDataSetValue", "false") == "true",
            "set_data_set_value": services_elem.get("SetDataSetValue", "false") == "true",
            "get_data_set_directory": services_elem.get("GetDataSetDirectory", "false") == "true",
            "read_write": services_elem.get("ReadWrite", "false") == "true",
            "timer_activated_control": services_elem.get("TimerActivatedControl", "false") == "true",
            "get_cb_values": services_elem.get("GetCBValues", "false") == "true",
            "gse_dir": services_elem.get("GSEDir", "false") == "true",
            "file_handling": services_elem.get("FileHandling", "false") == "true"
        }

    def _parse_server(self, parent_elem: ET.Element) -> Optional[Dict]:
        """解析Server"""
        server_elem = parent_elem.find('.//scl:Server', self.namespaces)
        if server_elem is None:
            return None

        return {
            "server_instances": self._parse_server_instances(server_elem)
        }

    def _parse_server_instances(self, server_elem: ET.Element) -> List[Dict]:
        """解析ServerInstance列表"""
        instances = []
        instance_elements = server_elem.findall('.//scl:ServerAt', self.namespaces)

        for instance_elem in instance_elements:
            instance_data = {
                "server_instance_name": instance_elem.get("apName", ""),
                "logical_devices": self._parse_logical_devices(instance_elem)
            }
            instances.append(instance_data)

        return instances

    def _parse_logical_devices(self, parent_elem: ET.Element) -> List[Dict]:
        """解析LogicalDevice列表"""
        devices = []
        ld_elements = parent_elem.findall('.//scl:LDevice', self.namespaces)

        for ld_elem in ld_elements:
            ld_data = {
                "ld_inst": ld_elem.get("inst", ""),
                "ld_desc": ld_elem.get("desc", ""),
                "logical_nodes": self._parse_logical_nodes(ld_elem)
            }
            devices.append(ld_data)

        return devices

    def _parse_logical_nodes(self, ld_elem: ET.Element) -> List[Dict]:
        """解析LogicalNode列表"""
        nodes = []
        ln_elements = ld_elem.findall('.//scl:LN', self.namespaces)
        ln0_elements = ld_elem.findall('.//scl:LN0', self.namespaces)

        for ln_elem in ln_elements + ln0_elements:
            ln_data = {
                "ln_class": ln_elem.get("lnClass", ""),
                "ln_inst": ln_elem.get("inst", ""),
                "ln_prefix": ln_elem.get("prefix", ""),
                "ln_desc": ln_elem.get("desc", ""),
                "ln_name": self._get_ln_name(ln_elem),
                "data_objects": self._parse_data_objects(ln_elem)
            }
            nodes.append(ln_data)

        return nodes

    def _get_ln_name(self, ln_elem: ET.Element) -> str:
        """获取逻辑节点名称"""
        prefix = ln_elem.get("prefix", "")
        ln_class = ln_elem.get("lnClass", "")
        ln_inst = ln_elem.get("inst", "")

        if prefix:
            return f"{prefix}{ln_class}{ln_inst}"
        return f"{ln_class}{ln_inst}"

    def _parse_data_objects(self, ln_elem: ET.Element) -> List[Dict]:
        """解析DataObject列表"""
        data_objects = []
        do_elements = ln_elem.findall('.//scl:DO', self.namespaces)

        for do_elem in do_elements:
            do_data = {
                "do_name": do_elem.get("name", ""),
                "do_desc": do_elem.get("desc", ""),
                "do_type": do_elem.get("type", ""),
                "data_attributes": self._parse_data_attributes(do_elem)
            }
            data_objects.append(do_data)

        return data_objects

    def _parse_data_attributes(self, do_elem: ET.Element) -> List[Dict]:
        """解析DataAttribute列表"""
        attributes = []
        da_elements = do_elem.findall('.//scl:DA', self.namespaces)

        for da_elem in da_elements:
            da_data = {
                "da_name": da_elem.get("name", ""),
                "da_desc": da_elem.get("desc", ""),
                "da_type": da_elem.get("type", ""),
                "da_fc": da_elem.get("fc", ""),
                "da_b_type": da_elem.get("bType", "")
            }
            attributes.append(da_data)

        return attributes

    def _parse_communication(self, root: ET.Element) -> Dict:
        """解析Communication配置"""
        comm_elem = root.find('.//scl:Communication', self.namespaces)
        if comm_elem is None:
            return {}

        return {
            "subnetworks": self._parse_subnetworks(comm_elem),
            "connected_aps": self._parse_connected_aps(comm_elem)
        }

    def _parse_subnetworks(self, comm_elem: ET.Element) -> List[Dict]:
        """解析Subnetwork列表"""
        subnetworks = []
        sn_elements = comm_elem.findall('.//scl:SubNetwork', self.namespaces)

        for sn_elem in sn_elements:
            sn_data = {
                "sn_name": sn_elem.get("name", ""),
                "sn_desc": sn_elem.get("desc", ""),
                "sn_type": sn_elem.get("type", "")
            }
            subnetworks.append(sn_data)

        return subnetworks

    def _parse_connected_aps(self, comm_elem: ET.Element) -> List[Dict]:
        """解析ConnectedAP列表"""
        connected_aps = []
        cap_elements = comm_elem.findall('.//scl:ConnectedAP', self.namespaces)

        for cap_elem in cap_elements:
            cap_data = {
                "ied_name": cap_elem.get("iedName", ""),
                "ap_name": cap_elem.get("apName", ""),
                "gse": self._parse_gse(cap_elem),
                "smv": self._parse_smv(cap_elem)
            }
            connected_aps.append(cap_data)

        return connected_aps

    def _parse_gse(self, cap_elem: ET.Element) -> List[Dict]:
        """解析GSE配置"""
        gse_list = []
        gse_elements = cap_elem.findall('.//scl:GSE', self.namespaces)

        for gse_elem in gse_elements:
            gse_data = {
                "g_cb_name": gse_elem.get("cbName", ""),
                "g_ld_inst": gse_elem.get("ldInst", ""),
                "g_address": self._parse_address(gse_elem.find('.//scl:Address', self.namespaces))
            }
            gse_list.append(gse_data)

        return gse_list

    def _parse_smv(self, cap_elem: ET.Element) -> List[Dict]:
        """解析SMV配置"""
        smv_list = []
        smv_elements = cap_elem.findall('.//scl:SMV', self.namespaces)

        for smv_elem in smv_elements:
            smv_data = {
                "sv_cb_name": smv_elem.get("cbName", ""),
                "sv_ld_inst": smv_elem.get("ldInst", ""),
                "sv_address": self._parse_address(smv_elem.find('.//scl:Address', self.namespaces))
            }
            smv_list.append(smv_data)

        return smv_list

    def _parse_address(self, addr_elem: Optional[ET.Element]) -> Dict:
        """解析Address"""
        if addr_elem is None:
            return {}

        address = {}
        p_elements = addr_elem.findall('.//scl:P', self.namespaces)

        for p_elem in p_elements:
            p_type = p_elem.get("type", "")
            p_value = p_elem.text or ""
            address[p_type] = p_value

        return address

    def _parse_data_type_templates(self, root: ET.Element) -> Dict:
        """解析DataTypeTemplates"""
        dtt_elem = root.find('.//scl:DataTypeTemplates', self.namespaces)
        if dtt_elem is None:
            return {}

        return {
            "logical_node_types": self._parse_ln_types(dtt_elem),
            "data_object_types": self._parse_do_types(dtt_elem),
            "data_attribute_types": self._parse_da_types(dtt_elem)
        }

    def _parse_ln_types(self, dtt_elem: ET.Element) -> List[Dict]:
        """解析LNodeType列表"""
        ln_types = []
        lnt_elements = dtt_elem.findall('.//scl:LNodeType', self.namespaces)

        for lnt_elem in lnt_elements:
            lnt_data = {
                "ln_class": lnt_elem.get("lnClass", ""),
                "ln_id": lnt_elem.get("id", ""),
                "data_objects": self._parse_data_objects(lnt_elem)
            }
            ln_types.append(lnt_data)

        return ln_types

    def _parse_do_types(self, dtt_elem: ET.Element) -> List[Dict]:
        """解析DOType列表"""
        do_types = []
        dot_elements = dtt_elem.findall('.//scl:DOType', self.namespaces)

        for dot_elem in dot_elements:
            dot_data = {
                "do_id": dot_elem.get("id", ""),
                "do_cdc": dot_elem.get("cdc", ""),
                "data_attributes": self._parse_data_attributes(dot_elem)
            }
            do_types.append(dot_data)

        return do_types

    def _parse_da_types(self, dtt_elem: ET.Element) -> List[Dict]:
        """解析DAType列表"""
        da_types = []
        dat_elements = dtt_elem.findall('.//scl:DAType', self.namespaces)

        for dat_elem in dat_elements:
            dat_data = {
                "da_id": dat_elem.get("id", ""),
                "data_attributes": self._parse_data_attributes(dat_elem)
            }
            da_types.append(dat_data)

        return da_types
```

### 2.2 IED配置解析

**IED配置管理器实现**：

```python
class IEDConfigManager:
    """IED配置管理器"""

    def __init__(self, scl_parser: SCLParser):
        self.parser = scl_parser
        self.ied_configs: Dict[str, Dict] = {}

    def load_scl_config(self, scl_file_path: str):
        """加载SCL配置"""
        scl_data = self.parser.parse_scl_file(scl_file_path)

        for ied in scl_data.get("ieds", []):
            ied_name = ied.get("ied_name")
            if ied_name:
                self.ied_configs[ied_name] = ied

        logger.info(f"Loaded {len(self.ied_configs)} IED configurations")

    def get_ied_config(self, ied_name: str) -> Optional[Dict]:
        """获取IED配置"""
        return self.ied_configs.get(ied_name)

    def get_logical_nodes(self, ied_name: str, ld_inst: str = None) -> List[Dict]:
        """获取逻辑节点列表"""
        ied_config = self.get_ied_config(ied_name)
        if not ied_config:
            return []

        logical_nodes = []
        for ap in ied_config.get("access_points", []):
            server = ap.get("server")
            if server:
                for instance in server.get("server_instances", []):
                    for ld in instance.get("logical_devices", []):
                        if ld_inst is None or ld.get("ld_inst") == ld_inst:
                            logical_nodes.extend(ld.get("logical_nodes", []))

        return logical_nodes

    def get_data_objects(self, ied_name: str, ln_name: str) -> List[Dict]:
        """获取数据对象列表"""
        logical_nodes = self.get_logical_nodes(ied_name)

        for ln in logical_nodes:
            if ln.get("ln_name") == ln_name:
                return ln.get("data_objects", [])

        return []
```

---

## 3. MMS协议实现

### 3.1 MMS客户端实现

**MMS客户端实现**：

```python
import socket
import struct
from typing import Dict, List, Optional, Any

class MMSClient:
    """MMS客户端"""

    def __init__(self, host: str, port: int = 102):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False

    def connect(self, timeout: float = 10.0) -> bool:
        """连接到MMS服务器 - 增强错误处理"""
        # 输入验证
        if not self.host:
            raise ValueError("MMS server host cannot be empty")

        if not isinstance(self.host, str):
            raise TypeError(f"MMS server host must be a string, got {type(self.host)}")

        if not isinstance(self.port, int):
            raise TypeError(f"MMS server port must be an integer, got {type(self.port)}")

        if not (1 <= self.port <= 65535):
            raise ValueError(f"MMS server port must be between 1 and 65535, got {self.port}")

        if timeout <= 0:
            raise ValueError(f"Connection timeout must be positive, got {timeout}")

        # 如果已经连接，先断开
        if self.connected and self.socket:
            try:
                self.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting existing connection: {e}")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)

            # 尝试连接
            self.socket.connect((self.host, self.port))
            self.connected = True

            logger.info(f"Connected to MMS server: {self.host}:{self.port}")
            return True

        except socket.timeout:
            logger.error(f"Connection timeout to MMS server {self.host}:{self.port} (timeout: {timeout}s)")
            self._cleanup_socket()
            raise TimeoutError(f"Connection timeout to MMS server {self.host}:{self.port}") from None
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for MMS server {self.host}: {e}")
            self._cleanup_socket()
            raise ConnectionError(f"Cannot resolve hostname {self.host}: {e}") from e
        except socket.error as e:
            logger.error(f"Socket error connecting to MMS server {self.host}:{self.port}: {e}")
            self._cleanup_socket()
            raise ConnectionError(f"Cannot connect to MMS server {self.host}:{self.port}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error connecting to MMS server {self.host}:{self.port}: {e}", exc_info=True)
            self._cleanup_socket()
            raise RuntimeError(f"Failed to connect to MMS server: {e}") from e

    def _cleanup_socket(self):
        """清理socket资源"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.socket = None
                self.connected = False

    def disconnect(self):
        """断开连接"""
        if self.socket:
            self.socket.close()
            self.connected = False
            logger.info("Disconnected from MMS server")

    def get_directory(self, object_name: str = "") -> Optional[Dict]:
        """GetDirectory服务"""
        if not self.connected:
            return None

        # 构建MMS GetDirectory请求
        request = self._build_get_directory_request(object_name)

        try:
            self.socket.send(request)
            response = self.socket.recv(4096)
            return self._parse_get_directory_response(response)
        except Exception as e:
            logger.error(f"GetDirectory failed: {e}")
            return None

    def read(self, variable_name: str) -> Optional[Any]:
        """Read服务"""
        if not self.connected:
            return None

        # 构建MMS Read请求
        request = self._build_read_request(variable_name)

        try:
            self.socket.send(request)
            response = self.socket.recv(4096)
            return self._parse_read_response(response)
        except Exception as e:
            logger.error(f"Read failed: {e}")
            return None

    def write(self, variable_name: str, value: Any) -> bool:
        """Write服务"""
        if not self.connected:
            return False

        # 构建MMS Write请求
        request = self._build_write_request(variable_name, value)

        try:
            self.socket.send(request)
            response = self.socket.recv(4096)
            return self._parse_write_response(response)
        except Exception as e:
            logger.error(f"Write failed: {e}")
            return False

    def _build_get_directory_request(self, object_name: str) -> bytes:
        """构建GetDirectory请求"""
        # MMS GetDirectory请求编码（简化实现）
        # 实际实现需要使用ASN.1编码
        return b''  # 占位符

    def _parse_get_directory_response(self, response: bytes) -> Dict:
        """解析GetDirectory响应"""
        # MMS GetDirectory响应解码（简化实现）
        # 实际实现需要使用ASN.1解码
        return {}

    def _build_read_request(self, variable_name: str) -> bytes:
        """构建Read请求"""
        # MMS Read请求编码（简化实现）
        return b''  # 占位符

    def _parse_read_response(self, response: bytes) -> Any:
        """解析Read响应"""
        # MMS Read响应解码（简化实现）
        return None

    def _build_write_request(self, variable_name: str, value: Any) -> bytes:
        """构建Write请求"""
        # MMS Write请求编码（简化实现）
        return b''  # 占位符

    def _parse_write_response(self, response: bytes) -> bool:
        """解析Write响应"""
        # MMS Write响应解码（简化实现）
        return True
```

### 3.2 MMS服务调用

**MMS服务管理器实现**：

```python
class MMSServiceManager:
    """MMS服务管理器"""

    def __init__(self, storage):
        self.storage = storage
        self.clients: Dict[str, MMSClient] = {}

    def create_client(self, ied_name: str, host: str, port: int = 102) -> bool:
        """创建MMS客户端"""
        client = MMSClient(host, port)
        if client.connect():
            self.clients[ied_name] = client
            return True
        return False

    def read_data_object(self, ied_name: str, variable_name: str) -> Optional[Any]:
        """读取数据对象"""
        client = self.clients.get(ied_name)
        if not client:
            return None

        value = client.read(variable_name)

        # 存储读取的数据
        if value is not None:
            self.storage.store_mms_read(ied_name, variable_name, value)

        return value

    def write_data_object(self, ied_name: str, variable_name: str, value: Any) -> bool:
        """写入数据对象"""
        client = self.clients.get(ied_name)
        if not client:
            return False

        result = client.write(variable_name, value)

        # 存储写入的数据
        if result:
            self.storage.store_mms_write(ied_name, variable_name, value)

        return result
```

---

## 4. GOOSE/SMV服务实现

### 4.1 GOOSE服务实现

**GOOSE服务实现**：

```python
import socket
import struct
from typing import Dict, List, Optional
from datetime import datetime

class GOOSEService:
    """GOOSE服务实现"""

    def __init__(self, storage):
        self.storage = storage
        self.socket: Optional[socket.socket] = None
        self.goose_messages: Dict[str, Dict] = {}

    def start_listener(self, interface: str = "eth0"):
        """启动GOOSE监听器"""
        try:
            # 创建原始套接字接收GOOSE消息
            self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            self.socket.bind((interface, 0))
            logger.info(f"GOOSE listener started on {interface}")
        except Exception as e:
            logger.error(f"Failed to start GOOSE listener: {e}")

    def receive_goose_message(self) -> Optional[Dict]:
        """接收GOOSE消息"""
        if not self.socket:
            return None

        try:
            data, addr = self.socket.recvfrom(65535)
            goose_msg = self._parse_goose_message(data)

            if goose_msg:
                # 存储GOOSE消息
                self.storage.store_goose_message(goose_msg)
                self.goose_messages[goose_msg.get("go_cb_ref", "")] = goose_msg

            return goose_msg
        except Exception as e:
            logger.error(f"Error receiving GOOSE message: {e}")
            return None

    def _parse_goose_message(self, data: bytes) -> Optional[Dict]:
        """解析GOOSE消息"""
        # GOOSE消息解析（简化实现）
        # 实际实现需要解析Ethernet帧和GOOSE PDU
        return {
            "go_cb_ref": "",
            "go_id": "",
            "go_dst_address": "",
            "go_app_id": 0,
            "go_t": 0,
            "go_all_data": [],
            "timestamp": datetime.now()
        }

    def send_goose_message(self, goose_config: Dict) -> bool:
        """发送GOOSE消息"""
        # GOOSE消息发送（简化实现）
        return True
```

### 4.2 SMV服务实现

**SMV服务实现**：

```python
class SMVService:
    """SMV服务实现"""

    def __init__(self, storage):
        self.storage = storage
        self.socket: Optional[socket.socket] = None
        self.smv_messages: List[Dict] = []

    def start_listener(self, interface: str = "eth0"):
        """启动SMV监听器"""
        try:
            self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            self.socket.bind((interface, 0))
            logger.info(f"SMV listener started on {interface}")
        except Exception as e:
            logger.error(f"Failed to start SMV listener: {e}")

    def receive_smv_message(self) -> Optional[Dict]:
        """接收SMV消息"""
        if not self.socket:
            return None

        try:
            data, addr = self.socket.recvfrom(65535)
            smv_msg = self._parse_smv_message(data)

            if smv_msg:
                # 存储SMV消息
                self.storage.store_smv_message(smv_msg)
                self.smv_messages.append(smv_msg)

            return smv_msg
        except Exception as e:
            logger.error(f"Error receiving SMV message: {e}")
            return None

    def _parse_smv_message(self, data: bytes) -> Optional[Dict]:
        """解析SMV消息"""
        # SMV消息解析（简化实现）
        return {
            "sv_cb_ref": "",
            "sv_id": "",
            "sv_dst_address": "",
            "sv_app_id": 0,
            "sv_smp_rate": 0,
            "sv_all_data": [],
            "timestamp": datetime.now()
        }
```

---

## 5. IEC61850数据存储与分析

### 5.1 PostgreSQL IEC61850数据存储

**IEC61850数据存储实现**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime

class IEC61850Storage:
    """IEC61850数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建IEC61850数据表"""
        # IED表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS ieds (
                id BIGSERIAL PRIMARY KEY,
                ied_name VARCHAR(100) UNIQUE NOT NULL,
                ied_desc VARCHAR(200),
                ied_type VARCHAR(100),
                ied_manufacturer VARCHAR(200),
                ied_config_version VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 逻辑节点表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS logical_nodes (
                id BIGSERIAL PRIMARY KEY,
                ied_name VARCHAR(100) NOT NULL,
                ld_inst VARCHAR(50) NOT NULL,
                ln_name VARCHAR(50) NOT NULL,
                ln_class VARCHAR(4) NOT NULL,
                ln_inst VARCHAR(2),
                ln_prefix VARCHAR(10),
                ln_desc VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ied_name) REFERENCES ieds(ied_name)
            )
        """)

        # 数据对象表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS data_objects (
                id BIGSERIAL PRIMARY KEY,
                ied_name VARCHAR(100) NOT NULL,
                ln_name VARCHAR(50) NOT NULL,
                do_name VARCHAR(100) NOT NULL,
                do_type VARCHAR(50),
                do_desc VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ied_name) REFERENCES ieds(ied_name)
            )
        """)

        # 数据属性表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS data_attributes (
                id BIGSERIAL PRIMARY KEY,
                ied_name VARCHAR(100) NOT NULL,
                do_name VARCHAR(100) NOT NULL,
                da_name VARCHAR(100) NOT NULL,
                da_type VARCHAR(50),
                da_fc VARCHAR(10),
                da_b_type VARCHAR(50),
                da_desc VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ied_name) REFERENCES ieds(ied_name)
            )
        """)

        # MMS读取记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS mms_reads (
                id BIGSERIAL PRIMARY KEY,
                ied_name VARCHAR(100) NOT NULL,
                variable_name VARCHAR(200) NOT NULL,
                value JSONB,
                read_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ied_name) REFERENCES ieds(ied_name)
            )
        """)

        # MMS写入记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS mms_writes (
                id BIGSERIAL PRIMARY KEY,
                ied_name VARCHAR(100) NOT NULL,
                variable_name VARCHAR(200) NOT NULL,
                value JSONB,
                write_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ied_name) REFERENCES ieds(ied_name)
            )
        """)

        # GOOSE消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS goose_messages (
                id BIGSERIAL PRIMARY KEY,
                go_cb_ref VARCHAR(200) NOT NULL,
                go_id VARCHAR(200),
                go_dst_address VARCHAR(12),
                go_app_id INTEGER,
                go_t BIGINT,
                go_all_data JSONB,
                message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # SMV消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS smv_messages (
                id BIGSERIAL PRIMARY KEY,
                sv_cb_ref VARCHAR(200) NOT NULL,
                sv_id VARCHAR(200),
                sv_dst_address VARCHAR(12),
                sv_app_id INTEGER,
                sv_smp_rate INTEGER,
                sv_all_data JSONB,
                message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ieds_ied_name
            ON ieds(ied_name)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_logical_nodes_ied_name
            ON logical_nodes(ied_name, ln_name)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mms_reads_ied_name
            ON mms_reads(ied_name, read_time DESC)
        """)

        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_goose_messages_time
            ON goose_messages(message_time DESC)
        """)

        self.conn.commit()

    def store_ied(self, ied_data: Dict) -> int:
        """存储IED信息"""
        self.cur.execute("""
            INSERT INTO ieds (
                ied_name, ied_desc, ied_type, ied_manufacturer, ied_config_version
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (ied_name) DO UPDATE SET
                ied_desc = EXCLUDED.ied_desc,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            ied_data.get("ied_name"),
            ied_data.get("ied_desc"),
            ied_data.get("ied_type"),
            ied_data.get("ied_manufacturer"),
            ied_data.get("ied_config_version")
        ))
        self.conn.commit()
        return self.cur.fetchone()[0]

    def store_logical_node(self, ln_data: Dict) -> int:
        """存储逻辑节点"""
        self.cur.execute("""
            INSERT INTO logical_nodes (
                ied_name, ld_inst, ln_name, ln_class, ln_inst, ln_prefix, ln_desc
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (
            ln_data.get("ied_name"),
            ln_data.get("ld_inst"),
            ln_data.get("ln_name"),
            ln_data.get("ln_class"),
            ln_data.get("ln_inst"),
            ln_data.get("ln_prefix"),
            ln_data.get("ln_desc")
        ))
        self.conn.commit()
        result = self.cur.fetchone()
        return result[0] if result else None

    def store_mms_read(self, ied_name: str, variable_name: str, value: Any):
        """存储MMS读取记录"""
        self.cur.execute("""
            INSERT INTO mms_reads (ied_name, variable_name, value)
            VALUES (%s, %s, %s::jsonb)
        """, (ied_name, variable_name, json.dumps(value)))
        self.conn.commit()

    def store_mms_write(self, ied_name: str, variable_name: str, value: Any):
        """存储MMS写入记录"""
        self.cur.execute("""
            INSERT INTO mms_writes (ied_name, variable_name, value)
            VALUES (%s, %s, %s::jsonb)
        """, (ied_name, variable_name, json.dumps(value)))
        self.conn.commit()

    def store_goose_message(self, goose_msg: Dict):
        """存储GOOSE消息"""
        self.cur.execute("""
            INSERT INTO goose_messages (
                go_cb_ref, go_id, go_dst_address, go_app_id, go_t, go_all_data
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        """, (
            goose_msg.get("go_cb_ref"),
            goose_msg.get("go_id"),
            goose_msg.get("go_dst_address"),
            goose_msg.get("go_app_id"),
            goose_msg.get("go_t"),
            json.dumps(goose_msg.get("go_all_data", []))
        ))
        self.conn.commit()

    def store_smv_message(self, smv_msg: Dict):
        """存储SMV消息"""
        self.cur.execute("""
            INSERT INTO smv_messages (
                sv_cb_ref, sv_id, sv_dst_address, sv_app_id, sv_smp_rate, sv_all_data
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        """, (
            smv_msg.get("sv_cb_ref"),
            smv_msg.get("sv_id"),
            smv_msg.get("sv_dst_address"),
            smv_msg.get("sv_app_id"),
            smv_msg.get("sv_smp_rate"),
            json.dumps(smv_msg.get("sv_all_data", []))
        ))
        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        self.cur.close()
        self.conn.close()
```

### 5.2 IEC61850数据分析查询

**数据分析查询实现**：

```python
    def get_ied_statistics(self, ied_name: str) -> Dict:
        """查询IED统计信息"""
        self.cur.execute("""
            SELECT
                COUNT(DISTINCT ln_name) as ln_count,
                COUNT(DISTINCT do_name) as do_count,
                COUNT(DISTINCT da_name) as da_count,
                COUNT(*) as total_reads,
                MAX(read_time) as last_read_time
            FROM logical_nodes ln
            LEFT JOIN data_objects do ON ln.ied_name = do.ied_name AND ln.ln_name = do.ln_name
            LEFT JOIN data_attributes da ON do.ied_name = da.ied_name AND do.do_name = da.do_name
            LEFT JOIN mms_reads mr ON ln.ied_name = mr.ied_name
            WHERE ln.ied_name = %s
        """, (ied_name,))
        row = self.cur.fetchone()
        return {
            "ln_count": row[0],
            "do_count": row[1],
            "da_count": row[2],
            "total_reads": row[3],
            "last_read_time": row[4]
        }

    def get_goose_message_statistics(self, hours: int = 24) -> Dict:
        """查询GOOSE消息统计"""
        self.cur.execute("""
            SELECT
                COUNT(*) as message_count,
                COUNT(DISTINCT go_cb_ref) as cb_count,
                COUNT(DISTINCT go_dst_address) as dst_count,
                AVG(go_t) as avg_go_t,
                MIN(message_time) as first_message,
                MAX(message_time) as last_message
            FROM goose_messages
            WHERE message_time >= CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """, (hours,))
        row = self.cur.fetchone()
        return {
            "message_count": row[0],
            "cb_count": row[1],
            "dst_count": row[2],
            "avg_go_t": float(row[3]) if row[3] else None,
            "first_message": row[4],
            "last_message": row[5]
        }
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
