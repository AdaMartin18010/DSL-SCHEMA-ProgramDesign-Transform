# 安全最佳实践指南

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🔒 安全原则

### 1. 最小权限原则

- 只授予必要的权限
- 使用最小权限运行服务
- 定期审查权限设置

### 2. 深度防御

- 多层安全防护
- 不依赖单一安全措施
- 全面安全考虑

### 3. 安全默认值

- 默认安全配置
- 明确的安全策略
- 安全配置文档

---

## 🛡️ 安全措施

### 1. API安全

#### API密钥管理

```python
# 使用环境变量存储API密钥
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set")

# 不要在代码中硬编码密钥
# ❌ 错误示例
# OPENAI_API_KEY = "sk-xxxxx"
```

#### API认证

```python
# 使用API密钥认证
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/api/v1/protected")
async def protected_endpoint(api_key: str = Security(verify_api_key)):
    return {"message": "Access granted"}
```

#### 请求限流

```python
# 使用限流中间件
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/entities")
@limiter.limit("10/minute")
async def list_entities(request: Request):
    return storage.list_entities()
```

### 2. 数据库安全

#### 连接加密

```python
# 使用SSL连接
database_url = "postgresql://user:pass@host:5432/db?sslmode=require"
```

#### SQL注入防护

```python
# ✅ 使用参数化查询
def get_entity(entity_id: str):
    query = "SELECT * FROM entities WHERE entity_id = :entity_id"
    result = session.execute(query, {"entity_id": entity_id})
    return result.fetchone()

# ❌ 避免字符串拼接
# query = f"SELECT * FROM entities WHERE entity_id = '{entity_id}'"
```

#### 访问控制

```sql
-- 创建只读用户
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- 创建应用用户（有限权限）
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
```

### 3. 数据安全

#### 敏感数据加密

```python
# 加密敏感字段
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(data: str) -> bytes:
    return cipher.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes) -> str:
    return cipher.decrypt(encrypted_data).decode()
```

#### 数据脱敏

```python
# 日志中脱敏敏感信息
def mask_sensitive_data(data: dict) -> dict:
    masked = data.copy()
    if "api_key" in masked:
        masked["api_key"] = "***"
    if "password" in masked:
        masked["password"] = "***"
    return masked
```

### 4. 输入验证

#### 数据验证

```python
# 使用Pydantic验证输入
from pydantic import BaseModel, validator

class EntityCreate(BaseModel):
    entity_id: str
    entity_type: str
    properties: dict

    @validator('entity_id')
    def validate_entity_id(cls, v):
        if not v or len(v) > 100:
            raise ValueError('entity_id must be 1-100 characters')
        return v

    @validator('entity_type')
    def validate_entity_type(cls, v):
        allowed_types = ['schema', 'instance', 'pattern']
        if v not in allowed_types:
            raise ValueError(f'entity_type must be one of {allowed_types}')
        return v
```

#### 输入清理

```python
# 清理用户输入
import html

def sanitize_input(text: str) -> str:
    # HTML转义
    text = html.escape(text)
    # 移除危险字符
    text = text.replace('<script>', '').replace('</script>', '')
    return text
```

---

## 🔐 安全配置

### 1. 环境变量

```bash
# .env文件示例
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/db

# API密钥（不要提交到版本控制）
OPENAI_API_KEY=sk-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 应用密钥
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
```

### 2. Docker安全

```yaml
# docker-compose.yml
services:
  api:
    # 使用非root用户运行
    user: "1000:1000"

    # 只读文件系统（如果可能）
    read_only: true

    # 限制资源
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### 3. 网络安全

```python
# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 限制来源
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # 限制方法
    allow_headers=["Content-Type", "Authorization"],  # 限制头部
)
```

---

## 📋 安全检查清单

### 部署前检查

- [ ] 所有API密钥使用环境变量
- [ ] 数据库连接使用SSL
- [ ] 启用API认证
- [ ] 配置请求限流
- [ ] 启用日志记录
- [ ] 配置错误处理
- [ ] 移除调试信息
- [ ] 更新依赖包
- [ ] 扫描安全漏洞

### 运行时检查

- [ ] 监控异常请求
- [ ] 检查日志异常
- [ ] 监控资源使用
- [ ] 定期备份数据
- [ ] 更新安全补丁

---

## 🚨 安全事件响应

### 1. 发现安全漏洞

1. 立即隔离受影响系统
2. 评估影响范围
3. 修复漏洞
4. 通知相关用户
5. 更新安全策略

### 2. 数据泄露

1. 立即停止数据访问
2. 评估泄露范围
3. 通知受影响用户
4. 报告相关机构
5. 加强安全措施

---

## 📝 相关文档

- [部署指南](DEPLOYMENT_GUIDE.md)
- [开发指南](DEVELOPMENT_GUIDE.md)
- [故障排查](TROUBLESHOOTING.md)

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
