# 身份认证Schema转换体系

## 📑 目录

- [身份认证Schema转换体系](#身份认证schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
  - [2. OAuth 2.0到OpenID Connect转换](#2-oauth-20到openid-connect转换)
  - [3. OpenID Connect到SAML转换](#3-openid-connect到saml转换)
  - [4. SAML到OAuth 2.0转换](#4-saml到oauth-20转换)
  - [5. 转换验证](#5-转换验证)
  - [6. 身份认证数据存储与分析](#6-身份认证数据存储与分析)
    - [6.1 PostgreSQL身份认证数据存储](#61-postgresql身份认证数据存储)
    - [6.2 身份认证数据分析查询](#62-身份认证数据分析查询)

---

## 1. 转换体系概述

身份认证Schema转换体系支持不同身份认证协议之间的转换。

### 1.1 转换目标

1. **OAuth 2.0到OpenID Connect转换**：OAuth 2.0配置转换为OIDC配置
2. **OpenID Connect到SAML转换**：OIDC配置转换为SAML配置
3. **SAML到OAuth 2.0转换**：SAML配置转换为OAuth 2.0配置
4. **Schema到数据库转换**：身份认证Schema定义到PostgreSQL存储

---

## 2. OAuth 2.0到OpenID Connect转换

**转换规则**：

- OAuth 2.0授权服务器 → OIDC身份提供者
- OAuth 2.0客户端 → OIDC依赖方
- OAuth 2.0访问令牌 → OIDC ID Token

**转换示例**：

```python
def oauth2_to_oidc(oauth2_config: dict) -> dict:
    """将OAuth 2.0配置转换为OpenID Connect配置"""
    oidc_config = {
        "identity_provider": {
            "issuer": oauth2_config["authorization_server"]["server_url"],
            "authorization_endpoint": oauth2_config["authorization_server"]["authorization_endpoint"],
            "token_endpoint": oauth2_config["authorization_server"]["token_endpoint"],
            "userinfo_endpoint": f"{oauth2_config['authorization_server']['server_url']}/userinfo",
            "jwks_uri": f"{oauth2_config['authorization_server']['server_url']}/.well-known/jwks.json",
            "supported_scopes": ["openid"] + oauth2_config["client"]["scopes"],
            "supported_response_types": ["code"]
        },
        "relying_party": {
            "client_id": oauth2_config["client"]["client_id"],
            "client_secret": oauth2_config["client"]["client_secret"],
            "redirect_uri": oauth2_config["client"]["redirect_uris"][0],
            "response_type": "code",
            "scope": "openid " + " ".join(oauth2_config["client"]["scopes"])
        }
    }
    return oidc_config
```

---

## 3. OpenID Connect到SAML转换

**转换规则**：

- OIDC身份提供者 → SAML身份提供者
- OIDC依赖方 → SAML服务提供者
- OIDC ID Token → SAML断言

---

## 4. SAML到OAuth 2.0转换

**转换规则**：

- SAML身份提供者 → OAuth 2.0授权服务器
- SAML服务提供者 → OAuth 2.0客户端
- SAML断言 → OAuth 2.0访问令牌

---

## 5. 转换验证

验证转换的配置完整性、协议一致性和安全等价性。

---

## 6. 身份认证数据存储与分析

### 6.1 PostgreSQL身份认证数据存储

**身份认证数据存储方案**：

```python
import psycopg2
import json

class IdentityAuthenticationDataStore:
    """身份认证数据存储类"""

    def __init__(self, db_config: Dict):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """创建身份认证数据存储表"""
        with self.conn.cursor() as cur:
            # OAuth 2.0配置表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oauth2_configs (
                    id SERIAL PRIMARY KEY,
                    config_name VARCHAR(255) NOT NULL UNIQUE,
                    authorization_server JSONB NOT NULL,
                    resource_server JSONB,
                    clients JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # OIDC配置表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS oidc_configs (
                    id SERIAL PRIMARY KEY,
                    config_name VARCHAR(255) NOT NULL UNIQUE,
                    identity_provider JSONB NOT NULL,
                    relying_parties JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # SAML配置表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS saml_configs (
                    id SERIAL PRIMARY KEY,
                    config_name VARCHAR(255) NOT NULL UNIQUE,
                    identity_provider JSONB NOT NULL,
                    service_provider JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 认证日志表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS authentication_logs (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    protocol_type VARCHAR(50) NOT NULL,
                    authentication_method VARCHAR(50),
                    success BOOLEAN NOT NULL,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
```

### 6.2 身份认证数据分析查询

**分析查询示例**：

```python
def analyze_authentication(db_config: Dict):
    """分析身份认证使用情况"""
    store = IdentityAuthenticationDataStore(db_config)

    with store.conn.cursor() as cur:
        # 查询认证协议使用统计
        cur.execute("""
            SELECT
                protocol_type,
                COUNT(*) as auth_count,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failure_count
            FROM authentication_logs
            GROUP BY protocol_type
            ORDER BY auth_count DESC
        """)

        return cur.fetchall()
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
