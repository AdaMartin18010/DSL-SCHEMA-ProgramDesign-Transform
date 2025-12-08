# 故障排查指南

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🔍 常见问题

### 数据库连接问题

#### 问题：无法连接到PostgreSQL数据库

**症状**：

- 错误信息：`could not connect to server`
- 服务启动失败

**解决方案**：

1. **检查PostgreSQL是否运行**

   ```bash
   # Windows
   Get-Service postgresql*

   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. **检查数据库URL配置**

   ```bash
   # 检查.env文件中的数据库URL
   cat .env | grep DB_URL
   ```

3. **检查端口是否被占用**

   ```bash
   # Windows
   netstat -ano | findstr :5432

   # Linux/Mac
   lsof -i :5432
   ```

4. **检查pgvector扩展是否安装**

   ```sql
   -- 连接到数据库
   psql -U your_user -d your_database

   -- 检查扩展
   \dx

   -- 如果未安装，安装扩展
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

### API服务启动失败

#### 问题：API服务无法启动

**症状**：

- 端口已被占用
- 模块导入错误
- 依赖缺失

**解决方案**：

1. **检查端口占用**

   ```bash
   # Windows
   netstat -ano | findstr :8000

   # Linux/Mac
   lsof -i :8000
   ```

2. **检查Python路径**

   ```bash
   # 确保code目录在Python路径中
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/code"
   ```

3. **检查依赖安装**

   ```bash
   pip install -r code/requirements.txt
   ```

4. **检查模块导入**

   ```bash
   # 测试导入
   python -c "from multimodal_kg import MultimodalKGStorage"
   ```

---

### Docker部署问题

#### 问题：Docker容器无法启动

**症状**：

- 容器启动后立即退出
- 无法连接到服务

**解决方案**：

1. **检查Docker日志**

   ```bash
   cd docker
   docker-compose logs -f [service_name]
   ```

2. **检查docker-compose.yml配置**

   ```bash
   # 验证配置
   docker-compose config
   ```

3. **检查构建上下文**

   ```bash
   # 确保在项目根目录
   cd docker
   docker-compose build
   ```

4. **检查环境变量**

   ```bash
   # 检查.env文件
   cat .env
   ```

---

### LLM API调用失败

#### 问题：LLM推理API调用失败

**症状**：

- API密钥错误
- 请求超时
- 配额不足

**解决方案**：

1. **检查API密钥**

   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. **检查网络连接**

   ```bash
   # 测试连接
   curl https://api.openai.com/v1/models
   ```

3. **检查API配额**
   - 登录OpenAI/Anthropic控制台
   - 检查API使用量和配额

---

### 测试失败

#### 问题：单元测试或集成测试失败

**症状**：

- 测试用例失败
- 数据库连接错误
- 模块导入错误

**解决方案**：

1. **检查测试数据库配置**

   ```bash
   # 检查测试数据库URL
   echo $TEST_DATABASE_URL
   ```

2. **运行单个测试**

   ```bash
   pytest code/tests/test_multimodal_kg.py::test_add_entity -v
   ```

3. **检查测试数据**

   ```bash
   # 清理测试数据
   pytest --cache-clear
   ```

---

## 🛠️ 调试技巧

### 1. 启用调试模式

```bash
# 设置环境变量
export DEBUG=True

# 或修改.env文件
DEBUG=True
```

### 2. 查看详细日志

```python
# 在代码中添加日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. 使用交互式调试

```python
# 在代码中添加断点
import pdb
pdb.set_trace()
```

---

## 📞 获取帮助

如果以上解决方案无法解决问题，请：

1. 查看[部署指南](DEPLOYMENT_GUIDE.md)
2. 查看[开发指南](DEVELOPMENT_GUIDE.md)
3. 查看项目[GitHub Issues](https://github.com/your-repo/issues)

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
