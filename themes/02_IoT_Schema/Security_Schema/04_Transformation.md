# IoT安全Schema转换体系

## 📑 目录

- [IoT安全Schema转换体系](#iot安全schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 安全机制转换](#2-安全机制转换)
    - [2.1 身份认证转换](#21-身份认证转换)
    - [2.2 访问控制转换](#22-访问控制转换)
    - [2.3 数据加密转换](#23-数据加密转换)
    - [2.4 安全通信转换](#24-安全通信转换)
  - [3. 转换实例](#3-转换实例)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 安全数据存储与分析](#6-安全数据存储与分析)
    - [6.1 PostgreSQL安全数据存储](#61-postgresql安全数据存储)
    - [6.2 安全数据分析查询](#62-安全数据分析查询)
  - [7. 参考文献](#7-参考文献)
    - [7.1 标准文档](#71-标准文档)
    - [7.2 技术文档](#72-技术文档)
    - [7.3 在线资源](#73-在线资源)

---

## 1. 转换体系概述

IoT安全Schema转换体系支持将安全Schema
转换为多种编程语言的安全代码。

**转换目标**：

1. **Python**：安全库集成代码
2. **Rust**：安全系统代码
3. **Go**：安全服务代码
4. **JavaScript**：Web安全代码

---

## 2. 安全机制转换

### 2.1 身份认证转换

**Schema到Python转换**：

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import bcrypt
import jwt

class AuthenticationManager:
    """身份认证管理器"""

    def __init__(self, method: str = "password"):
        self.method = method
        self.max_attempts = 3
        self.lockout_duration = 300  # 5分钟

    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )

    def generate_token(self, user_id: str, secret: str) -> str:
        """生成JWT令牌"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, secret, algorithm="HS256")

    def verify_token(self, token: str, secret: str) -> dict:
        """验证JWT令牌"""
        return jwt.decode(token, secret, algorithms=["HS256"])
```

### 2.2 访问控制转换

**Schema到Python转换**：

```python
from enum import Enum
from typing import List, Set

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"

class Role:
    """角色定义"""

    def __init__(self, name: str, permissions: List[Permission]):
        self.name = name
        self.permissions = set(permissions)
        self.inherited_roles = []

    def add_inherited_role(self, role: 'Role'):
        """添加继承角色"""
        self.inherited_roles.append(role)

    def has_permission(self, permission: Permission) -> bool:
        """检查权限"""
        if permission in self.permissions:
            return True
        for role in self.inherited_roles:
            if role.has_permission(permission):
                return True
        return False

class AccessControlManager:
    """访问控制管理器"""

    def __init__(self):
        self.roles = {}
        self.user_roles = {}

    def create_role(self, name: str, permissions: List[Permission]):
        """创建角色"""
        self.roles[name] = Role(name, permissions)

    def assign_role(self, user_id: str, role_name: str):
        """分配角色"""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        self.user_roles[user_id].append(self.roles[role_name])

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """检查权限"""
        if user_id not in self.user_roles:
            return False
        for role in self.user_roles[user_id]:
            if role.has_permission(permission):
                return True
        return False
```

### 2.3 数据加密转换

**Schema到Python转换**：

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
import os

class EncryptionManager:
    """加密管理器"""

    def __init__(self, algorithm: str = "AES", key_size: int = 256):
        self.algorithm = algorithm
        self.key_size = key_size
        self.mode = "GCM"

    def generate_key(self) -> bytes:
        """生成密钥"""
        return os.urandom(self.key_size // 8)

    def encrypt(self, plaintext: bytes, key: bytes) -> tuple:
        """加密数据"""
        if self.algorithm == "AES" and self.mode == "GCM":
            iv = os.urandom(12)  # GCM推荐12字节IV
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            return (iv, ciphertext, encryptor.tag)
        else:
            raise ValueError(f"Unsupported algorithm/mode: {self.algorithm}/{self.mode}")

    def decrypt(self, iv: bytes, ciphertext: bytes, tag: bytes, key: bytes) -> bytes:
        """解密数据"""
        if self.algorithm == "AES" and self.mode == "GCM":
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
        else:
            raise ValueError(f"Unsupported algorithm/mode: {self.algorithm}/{self.mode}")

    def compute_hmac(self, data: bytes, key: bytes) -> bytes:
        """计算HMAC"""
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        return h.finalize()
```

### 2.4 安全通信转换

**Schema到Python转换**：

```python
import ssl
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class SecureCommunicationManager:
    """安全通信管理器"""

    def __init__(self, protocol: str = "TLS", version: str = "TLS_1.3"):
        self.protocol = protocol
        self.version = version
        self.cipher_suites = [
            "TLS_AES_256_GCM_SHA384",
            "TLS_CHACHA20_POLY1305_SHA256"
        ]

    def create_ssl_context(self, cert_file: str, key_file: str) -> ssl.SSLContext:
        """创建SSL上下文"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # 设置TLS版本
        if self.version == "TLS_1.3":
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.maximum_version = ssl.TLSVersion.TLSv1_3
        elif self.version == "TLS_1.2":
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.maximum_version = ssl.TLSVersion.TLSv1_2

        # 加载证书和密钥
        context.load_cert_chain(cert_file, key_file)

        # 禁用弱密码套件
        context.set_ciphers(':'.join(self.cipher_suites))

        return context

    def create_secure_socket(self, host: str, port: int,
                            cert_file: str, key_file: str) -> ssl.SSLSocket:
        """创建安全套接字"""
        context = self.create_ssl_context(cert_file, key_file)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_sock = context.wrap_socket(sock, server_hostname=host)
        secure_sock.connect((host, port))
        return secure_sock

    def verify_certificate(self, cert_file: str) -> bool:
        """验证证书"""
        with open(cert_file, 'rb') as f:
            cert_data = f.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            # 验证证书有效性
            # 这里可以添加更详细的验证逻辑
            return cert.not_valid_after > datetime.now()
```

---

## 3. 转换实例

**完整安全Schema转换示例**：

```python
# Schema定义的安全机制转换为Python代码
class IoTSecurityManager:
    """IoT安全管理器"""

    def __init__(self):
        self.auth_manager = AuthenticationManager(method="password")
        self.access_control = AccessControlManager()
        self.encryption = EncryptionManager(algorithm="AES", key_size=256)
        self.secure_comm = SecureCommunicationManager(
            protocol="TLS",
            version="TLS_1.3"
        )

    def setup_security(self, config: dict):
        """设置安全配置"""
        # 设置访问控制角色
        self.access_control.create_role(
            "admin",
            [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.DELETE]
        )
        self.access_control.create_role(
            "user",
            [Permission.READ]
        )
```

---

## 4. 转换工具

**工具列表**：

1. **代码生成器**：从Schema生成安全代码
2. **安全验证工具**：验证安全配置正确性
3. **渗透测试工具**：测试安全实现

---

## 5. 转换验证

**验证方法**：

1. **安全属性验证**：验证安全属性满足
2. **标准合规性验证**：验证符合安全标准
3. **渗透测试**：进行安全渗透测试

---

## 6. 安全数据存储与分析

### 6.1 PostgreSQL安全数据存储

**IoT安全事件和日志数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class SecurityEvent:
    """安全事件"""
    device_id: str
    event_type: str
    severity: str
    event_data: Dict
    timestamp: datetime
    source_ip: str = None

@dataclass
class AuthenticationLog:
    """认证日志"""
    device_id: str
    user_id: str
    auth_method: str
    success: bool
    timestamp: datetime
    ip_address: str = None

class IoTSecurityStorage:
    """IoT安全数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建安全数据表"""
        # 安全配置表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS security_configs (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                config_type VARCHAR(50) NOT NULL,
                configuration JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, config_type)
            )
        """)

        # 认证日志表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS authentication_logs (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                user_id VARCHAR(200),
                auth_method VARCHAR(50) NOT NULL,
                success BOOLEAN NOT NULL,
                ip_address INET,
                failure_reason TEXT,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 访问控制日志表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS access_control_logs (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                resource VARCHAR(500) NOT NULL,
                action VARCHAR(50) NOT NULL,
                user_id VARCHAR(200),
                allowed BOOLEAN NOT NULL,
                ip_address INET,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 安全事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                event_data JSONB NOT NULL,
                source_ip INET,
                resolved BOOLEAN DEFAULT FALSE,
                resolution_notes TEXT,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 证书管理表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                cert_type VARCHAR(50) NOT NULL,
                cert_serial VARCHAR(200) NOT NULL,
                issuer VARCHAR(500),
                subject VARCHAR(500),
                valid_from TIMESTAMP NOT NULL,
                valid_to TIMESTAMP NOT NULL,
                cert_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, cert_type, cert_serial)
            )
        """)

        # 安全统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS security_statistics (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_device_time
            ON authentication_logs(device_id, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_success
            ON authentication_logs(success, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_device_severity_time
            ON security_events(device_id, severity, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_resolved
            ON security_events(resolved, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_access_device_time
            ON access_control_logs(device_id, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_certs_valid_to
            ON certificates(valid_to)
        """)

        self.conn.commit()

    def store_security_config(self, device_id: str, config_type: str,
                             configuration: Dict):
        """存储安全配置"""
        self.cur.execute("""
            INSERT INTO security_configs
            (device_id, config_type, configuration)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (device_id, config_type) DO UPDATE
            SET configuration = EXCLUDED.configuration,
                updated_at = CURRENT_TIMESTAMP
        """, (device_id, config_type, json.dumps(configuration)))
        self.conn.commit()

    def store_authentication_log(self, log: AuthenticationLog):
        """存储认证日志"""
        self.cur.execute("""
            INSERT INTO authentication_logs
            (device_id, user_id, auth_method, success, ip_address,
             failure_reason, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (log.device_id, log.user_id, log.auth_method, log.success,
              log.ip_address, None if log.success else "Authentication failed",
              log.timestamp))
        self.conn.commit()

    def store_access_control_log(self, device_id: str, resource: str,
                                 action: str, user_id: str,
                                 allowed: bool, ip_address: str = None,
                                 timestamp: datetime = None):
        """存储访问控制日志"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        self.cur.execute("""
            INSERT INTO access_control_logs
            (device_id, resource, action, user_id, allowed, ip_address, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (device_id, resource, action, user_id, allowed,
              ip_address, timestamp))
        self.conn.commit()

    def store_security_event(self, event: SecurityEvent):
        """存储安全事件"""
        self.cur.execute("""
            INSERT INTO security_events
            (device_id, event_type, severity, event_data, source_ip, timestamp)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s)
        """, (event.device_id, event.event_type, event.severity,
              json.dumps(event.event_data), event.source_ip, event.timestamp))
        self.conn.commit()

    def store_certificate(self, device_id: str, cert_type: str,
                         cert_serial: str, issuer: str, subject: str,
                         valid_from: datetime, valid_to: datetime,
                         cert_data: str = None):
        """存储证书信息"""
        self.cur.execute("""
            INSERT INTO certificates
            (device_id, cert_type, cert_serial, issuer, subject,
             valid_from, valid_to, cert_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_id, cert_type, cert_serial) DO UPDATE
            SET issuer = EXCLUDED.issuer,
                subject = EXCLUDED.subject,
                valid_from = EXCLUDED.valid_from,
                valid_to = EXCLUDED.valid_to,
                cert_data = EXCLUDED.cert_data
        """, (device_id, cert_type, cert_serial, issuer, subject,
              valid_from, valid_to, cert_data))
        self.conn.commit()

    def get_failed_authentications(self, device_id: str = None,
                                   start_time: datetime = None,
                                   end_time: datetime = None,
                                   limit: int = 1000) -> List[Dict]:
        """获取失败认证记录"""
        query = """
            SELECT device_id, user_id, auth_method, ip_address,
                   failure_reason, timestamp
            FROM authentication_logs
            WHERE success = FALSE
        """
        params = []

        if device_id:
            query += " AND device_id = %s"
            params.append(device_id)

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)

        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        results = []
        for row in self.cur.fetchall():
            results.append({
                'device_id': row[0],
                'user_id': row[1],
                'auth_method': row[2],
                'ip_address': row[3],
                'failure_reason': row[4],
                'timestamp': row[5]
            })
        return results

    def get_security_events(self, device_id: str = None,
                           severity: str = None,
                           resolved: bool = None,
                           start_time: datetime = None,
                           end_time: datetime = None,
                           limit: int = 1000) -> List[Dict]:
        """获取安全事件"""
        query = """
            SELECT device_id, event_type, severity, event_data,
                   source_ip, resolved, timestamp
            FROM security_events
            WHERE 1=1
        """
        params = []

        if device_id:
            query += " AND device_id = %s"
            params.append(device_id)

        if severity:
            query += " AND severity = %s"
            params.append(severity)

        if resolved is not None:
            query += " AND resolved = %s"
            params.append(resolved)

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)

        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        results = []
        for row in self.cur.fetchall():
            results.append({
                'device_id': row[0],
                'event_type': row[1],
                'severity': row[2],
                'event_data': row[3],
                'source_ip': row[4],
                'resolved': row[5],
                'timestamp': row[6]
            })
        return results

    def calculate_statistics(self, device_id: str,
                            time_window: timedelta = timedelta(hours=1)) -> Dict:
        """计算安全统计信息"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        # 认证统计
        self.cur.execute("""
            SELECT
                COUNT(*) as total_auths,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failure_count
            FROM authentication_logs
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        auth_stats = self.cur.fetchone()

        # 安全事件统计
        self.cur.execute("""
            SELECT
                COUNT(*) as total_events,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
                COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count,
                COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_count,
                COUNT(CASE WHEN resolved THEN 1 END) as resolved_count
            FROM security_events
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        event_stats = self.cur.fetchone()

        # 访问控制统计
        self.cur.execute("""
            SELECT
                COUNT(*) as total_accesses,
                SUM(CASE WHEN allowed THEN 1 ELSE 0 END) as allowed_count,
                SUM(CASE WHEN NOT allowed THEN 1 ELSE 0 END) as denied_count
            FROM access_control_logs
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        access_stats = self.cur.fetchone()

        statistics = {
            'authentication': {
                'total': auth_stats[0] if auth_stats[0] else 0,
                'success': auth_stats[1] if auth_stats[1] else 0,
                'failure': auth_stats[2] if auth_stats[2] else 0,
                'success_rate': (auth_stats[1] / auth_stats[0] * 100) if auth_stats[0] and auth_stats[0] > 0 else 0
            },
            'security_events': {
                'total': event_stats[0] if event_stats[0] else 0,
                'critical': event_stats[1] if event_stats[1] else 0,
                'high': event_stats[2] if event_stats[2] else 0,
                'medium': event_stats[3] if event_stats[3] else 0,
                'resolved': event_stats[4] if event_stats[4] else 0
            },
            'access_control': {
                'total': access_stats[0] if access_stats[0] else 0,
                'allowed': access_stats[1] if access_stats[1] else 0,
                'denied': access_stats[2] if access_stats[2] else 0,
                'denial_rate': (access_stats[2] / access_stats[0] * 100) if access_stats[0] and access_stats[0] > 0 else 0
            }
        }

        # 存储统计结果
        self.cur.execute("""
            INSERT INTO security_statistics
            (device_id, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id, statistic_type, time_window) DO UPDATE
            SET statistics = EXCLUDED.statistics
        """, (device_id, 'security_statistics', end_time,
              json.dumps(statistics)))
        self.conn.commit()

        return statistics

    def find_expiring_certificates(self, days_ahead: int = 30) -> List[Dict]:
        """查找即将过期的证书"""
        expiry_date = datetime.utcnow() + timedelta(days=days_ahead)

        self.cur.execute("""
            SELECT device_id, cert_type, cert_serial, subject, valid_to
            FROM certificates
            WHERE valid_to <= %s
              AND valid_to > CURRENT_TIMESTAMP
            ORDER BY valid_to ASC
        """, (expiry_date,))

        results = []
        for row in self.cur.fetchall():
            results.append({
                'device_id': row[0],
                'cert_type': row[1],
                'cert_serial': row[2],
                'subject': row[3],
                'valid_to': row[4],
                'days_until_expiry': (row[4] - datetime.utcnow()).days
            })
        return results

    def analyze_security_threats(self, device_id: str,
                                time_window: timedelta = timedelta(hours=24)) -> Dict:
        """分析安全威胁"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        # 分析失败认证模式
        self.cur.execute("""
            SELECT
                ip_address,
                COUNT(*) as failure_count,
                MAX(timestamp) as last_attempt
            FROM authentication_logs
            WHERE device_id = %s
              AND success = FALSE
              AND timestamp >= %s
              AND timestamp <= %s
            GROUP BY ip_address
            HAVING COUNT(*) >= 5
            ORDER BY failure_count DESC
        """, (device_id, start_time, end_time))

        suspicious_ips = []
        for row in self.cur.fetchall():
            suspicious_ips.append({
                'ip_address': row[0],
                'failure_count': row[1],
                'last_attempt': row[2]
            })

        # 分析未解决的安全事件
        self.cur.execute("""
            SELECT
                event_type,
                COUNT(*) as count,
                MAX(severity) as max_severity
            FROM security_events
            WHERE device_id = %s
              AND resolved = FALSE
              AND timestamp >= %s
              AND timestamp <= %s
            GROUP BY event_type
            ORDER BY count DESC
        """, (device_id, start_time, end_time))

        unresolved_events = []
        for row in self.cur.fetchall():
            unresolved_events.append({
                'event_type': row[0],
                'count': row[1],
                'max_severity': row[2]
            })

        return {
            'device_id': device_id,
            'time_window': time_window,
            'suspicious_ips': suspicious_ips,
            'unresolved_events': unresolved_events,
            'threat_level': 'high' if len(suspicious_ips) > 0 or len(unresolved_events) > 0 else 'low'
        }

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    storage = IoTSecurityStorage(
        "postgresql://user:password@localhost/iot_security_db"
    )

    # 存储安全配置
    storage.store_security_config(
        device_id="device_001",
        config_type="authentication",
        configuration={
            "method": "OAuth2",
            "token_expiry": 3600,
            "refresh_token_enabled": True
        }
    )

    # 存储认证日志
    auth_log = AuthenticationLog(
        device_id="device_001",
        user_id="user_001",
        auth_method="OAuth2",
        success=True,
        timestamp=datetime.utcnow(),
        ip_address="192.168.1.100"
    )
    storage.store_authentication_log(auth_log)

    # 存储安全事件
    event = SecurityEvent(
        device_id="device_001",
        event_type="unauthorized_access_attempt",
        severity="high",
        event_data={"resource": "/api/sensors", "method": "GET"},
        timestamp=datetime.utcnow(),
        source_ip="192.168.1.200"
    )
    storage.store_security_event(event)

    # 计算统计信息
    stats = storage.calculate_statistics("device_001")
    print(f"统计信息: {stats}")

    # 查找即将过期的证书
    expiring = storage.find_expiring_certificates(days_ahead=30)
    print(f"即将过期的证书: {len(expiring)} 个")

    # 分析安全威胁
    threats = storage.analyze_security_threats("device_001")
    print(f"安全威胁分析: 威胁级别={threats['threat_level']}")

    storage.close()
```

### 6.2 安全数据分析查询

**高级分析查询**：

```python
class IoTSecurityAnalyzer:
    """IoT安全数据分析器"""

    def __init__(self, storage: IoTSecurityStorage):
        self.storage = storage

    def analyze_security_posture(self, device_id: str,
                                time_window: timedelta = timedelta(hours=24)) -> Dict:
        """分析安全态势"""
        stats = self.storage.calculate_statistics(device_id, time_window)
        threats = self.storage.analyze_security_threats(device_id, time_window)

        # 计算安全评分
        score = 100
        score -= min(20, stats['authentication']['failure'] * 2)
        score -= min(30, stats['security_events']['critical'] * 10)
        score -= min(20, stats['security_events']['high'] * 5)
        score -= min(10, len(threats['suspicious_ips']) * 2)
        score = max(0, score)

        return {
            'device_id': device_id,
            'security_score': score,
            'threat_level': threats['threat_level'],
            'statistics': stats,
            'threats': threats
        }
```

---

## 7. 参考文献

### 7.1 标准文档

- GB/T 37033-2018 信息安全技术 物联网安全参考模型及通用要求
- ISO/IEC 27001:2022 Information security management systems
- ISO/IEC 27002:2013 信息安全控制措施
- NIST Cybersecurity Framework
- OAuth 2.0 RFC 6749
- TLS 1.3 RFC 8446

### 7.2 技术文档

- 安全代码实现最佳实践
- IoT安全设计指南
- PostgreSQL JSONB文档

### 7.3 在线资源

- **OWASP IoT Top 10**：<https://owasp.org/www-project-internet-of-things/>
- **NIST Cybersecurity Framework**：<https://www.nist.gov/cyberframework>
- **PostgreSQL官网**：<https://www.postgresql.org/>

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展安全数据存储和分析功能，新增PostgreSQL存储方案）
