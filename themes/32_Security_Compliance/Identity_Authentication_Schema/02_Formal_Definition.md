# 身份认证Schema形式化定义

## 📑 目录

- [身份认证Schema形式化定义](#身份认证schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. OAuth 2.0 Schema](#2-oauth-20-schema)
  - [3. OpenID Connect Schema](#3-openid-connect-schema)
  - [4. SAML Schema](#4-saml-schema)
  - [5. 类型系统](#5-类型系统)
  - [6. 约束规则](#6-约束规则)
  - [7. 转换函数](#7-转换函数)
  - [8. 形式化定理](#8-形式化定理)

---

## 1. 形式化模型

**定义1（身份认证Schema）**：
身份认证Schema是一个三元组：

```text
Identity_Authentication_Schema = (OAuth2_Schema, OIDC_Schema, SAML_Schema)
```

---

## 2. OAuth 2.0 Schema

**定义2（OAuth 2.0 Schema）**：

```text
OAuth2_Schema = (Authorization_Server_Schema, Resource_Server_Schema,
                Client_Schema, Authorization_Grant_Schema)
```

**形式化DSL定义**：

```dsl
schema OAuth2 {
  authorization_server: AuthorizationServer {
    server_url: String @required
    token_endpoint: String @required
    authorization_endpoint: String @required
    supported_grant_types: List<GrantType> @required {
      grant_type: Enum {
        AuthorizationCode,
        ClientCredentials,
        RefreshToken,
        Password,
        Implicit
      } @required
    }
  }

  resource_server: ResourceServer {
    server_url: String @required
    introspection_endpoint: Optional<String>
    revocation_endpoint: Optional<String>
  }

  client: Client {
    client_id: String @required @unique
    client_secret: Optional<String>
    client_type: Enum { Public, Confidential } @required
    redirect_uris: List<String> @required
    scopes: List<String>
  }

  authorization_grant: AuthorizationGrant {
    grant_type: GrantType @required
    authorization_code: Optional<String>
    access_token: Optional<String>
    refresh_token: Optional<String>
    token_type: Enum { Bearer } @default(Bearer)
    expires_in: Int @range(0, null)
  }
} @standard("OAuth_2.0")
```

---

## 3. OpenID Connect Schema

**定义3（OpenID Connect Schema）**：

```text
OIDC_Schema = (IdP_Schema, RP_Schema, ID_Token_Schema, User_Info_Schema)
```

**形式化DSL定义**：

```dsl
schema OpenIDConnect {
  identity_provider: IdentityProvider {
    issuer: String @required
    authorization_endpoint: String @required
    token_endpoint: String @required
    userinfo_endpoint: String @required
    jwks_uri: String @required
    supported_scopes: List<String> @required
    supported_response_types: List<String> @required
  }

  relying_party: RelyingParty {
    client_id: String @required
    client_secret: Optional<String>
    redirect_uri: String @required
    response_type: String @required
    scope: String @required
  }

  id_token: IDToken {
    iss: String @required
    sub: String @required
    aud: String @required
    exp: Int @required
    iat: Int @required
    nonce: Optional<String>
    claims: Map<String, Any>
  }

  user_info: UserInfo {
    sub: String @required
    name: Optional<String>
    email: Optional<String>
    email_verified: Optional<Boolean>
    claims: Map<String, Any>
  }
} @standard("OpenID_Connect_1.0")
```

---

## 4. SAML Schema

**定义4（SAML Schema）**：

```text
SAML_Schema = (SAML_Assertion_Schema, SAML_Protocol_Schema, SAML_Binding_Schema)
```

**形式化DSL定义**：

```dsl
schema SAML {
  assertion: SAMLAssertion {
    issuer: String @required
    subject: Subject {
      name_id: String @required
      subject_confirmation: SubjectConfirmation {
        method: Enum { Bearer, HolderOfKey } @required
        recipient: String @required
        not_on_or_after: DateTime @required
      }
    }
    conditions: Conditions {
      not_before: DateTime @required
      not_on_or_after: DateTime @required
      audience_restriction: Optional<List<String>>
    }
    attributes: List<Attribute>
  }

  protocol: SAMLProtocol {
    protocol_type: Enum { AuthnRequest, Response, LogoutRequest, LogoutResponse } @required
    destination: String @required
    issuer: String @required
  }

  binding: SAMLBinding {
    binding_type: Enum { HTTPRedirect, HTTPPost, HTTPArtifact, SOAP } @required
    binding_url: String @required
  }
} @standard("SAML_2.0")
```

---

## 5. 类型系统

### 5.1 身份认证类型

```dsl
type IdentityAuthenticationType {
  oauth2: OAuth2Type
  oidc: OIDCType
  saml: SAMLType
}
```

---

## 6. 约束规则

### 6.1 OAuth 2.0约束

```dsl
constraint OAuth2Constraint {
  client_secret: {
    required_for_confidential: true
    optional_for_public: true
  }

  redirect_uri: {
    must_be_registered: true
    must_match_exactly: true
  }

  token_expiry: {
    access_token_min_seconds: 300
    refresh_token_min_seconds: 86400
  }
}
```

---

## 7. 转换函数

### 7.1 OAuth 2.0到OIDC转换

```dsl
function OAuth2ToOIDC(oauth2: OAuth2): OpenIDConnect {
  return {
    "identity_provider": convert_authorization_server_to_idp(oauth2.authorization_server),
    "relying_party": convert_client_to_rp(oauth2.client)
  }
}
```

---

## 8. 形式化定理

### 8.1 身份认证安全性定理

**定理1（身份认证安全性）**：
对于任意身份认证Schema A，如果A通过Schema验证，则A的所有认证流程安全且符合OAuth 2.0、OIDC或SAML规范。

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
