# 身份认证Schema实践案例

## 📑 目录

- [身份认证Schema实践案例](#身份认证schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：OAuth 2.0 API授权](#2-案例1oauth-20-api授权)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
  - [3. 案例2：OpenID Connect单点登录](#3-案例2openid-connect单点登录)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
  - [4. 案例3：SAML企业SSO](#4-案例3saml企业sso)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：OAuth 2.0到OpenID Connect转换](#5-案例4oauth-20到openid-connect转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：身份认证数据存储与分析系统](#6-案例5身份认证数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供身份认证Schema在实际应用中的实践案例。

---

## 2. 案例1：OAuth 2.0 API授权

### 2.1 场景描述

**应用场景**：
API服务使用OAuth 2.0进行授权。

### 2.2 Schema定义

**OAuth 2.0 API授权Schema**：

```dsl
schema OAuth2APIAuthorization {
  authorization_server: {
    server_url: "https://auth.example.com"
    token_endpoint: "https://auth.example.com/oauth/token"
    authorization_endpoint: "https://auth.example.com/oauth/authorize"
    supported_grant_types: [AuthorizationCode, ClientCredentials]
  }

  client: {
    client_id: "api-client-123"
    client_type: Confidential
    redirect_uris: ["https://api.example.com/callback"]
    scopes: ["read", "write"]
  }
} @standard("OAuth_2.0")
```

---

## 3. 案例2：OpenID Connect单点登录

### 3.1 场景描述

**应用场景**：
企业实施OpenID Connect单点登录。

### 3.2 Schema定义

**OpenID Connect单点登录Schema**：

```dsl
schema OIDCSSO {
  identity_provider: {
    issuer: "https://idp.example.com"
    authorization_endpoint: "https://idp.example.com/authorize"
    token_endpoint: "https://idp.example.com/token"
    userinfo_endpoint: "https://idp.example.com/userinfo"
    supported_scopes: ["openid", "profile", "email"]
  }

  relying_party: {
    client_id: "web-app-456"
    redirect_uri: "https://app.example.com/callback"
    response_type: "code"
    scope: "openid profile email"
  }
} @standard("OpenID_Connect_1.0")
```

---

## 4. 案例3：SAML企业SSO

### 4.1 场景描述

**应用场景**：
企业实施SAML单点登录。

### 4.2 Schema定义

**SAML企业SSO Schema**：

```dsl
schema SAMLSSO {
  identity_provider: {
    entity_id: "https://idp.company.com"
    sso_url: "https://idp.company.com/sso"
    certificate: "<X.509证书>"
  }

  service_provider: {
    entity_id: "https://app.company.com"
    acs_url: "https://app.company.com/saml/acs"
    certificate: "<X.509证书>"
  }
} @standard("SAML_2.0")
```

---

## 5. 案例4：OAuth 2.0到OpenID Connect转换

### 5.1 场景描述

**应用场景**：
将OAuth 2.0配置转换为OpenID Connect配置。

### 5.2 实现代码

**转换实现**：

```python
def oauth2_to_oidc(oauth2_config: dict) -> dict:
    return convert_oauth2_to_oidc_config(oauth2_config)
```

---

## 6. 案例5：身份认证数据存储与分析系统

### 6.1 场景描述

**应用场景**：
存储身份认证配置和认证日志。

### 6.2 实现代码

**数据存储实现**：

```python
from identity_authentication_data_store import IdentityAuthenticationDataStore

store = IdentityAuthenticationDataStore(db_config)
store.store_oauth2_config("api-auth", oauth2_config)
store.log_authentication(user_id, "OAuth2", success, ip_address)
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
