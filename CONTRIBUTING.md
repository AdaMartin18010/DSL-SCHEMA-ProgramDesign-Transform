# 贡献指南

## 📋 欢迎贡献

感谢您对DSL Schema项目的关注！我们欢迎所有形式的贡献。

---

## 🤝 如何贡献

### 1. 报告问题

如果您发现了bug或有功能建议，请：

1. 检查[现有Issues](https://github.com/your-repo/issues)是否已有相关讨论
2. 创建新Issue，提供：
   - 问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息

### 2. 提交代码

#### 开发流程

1. **Fork项目**
   ```bash
   git clone https://github.com/your-username/DSL-SCHEMA-ProgramDesign-Transform.git
   cd DSL-SCHEMA-ProgramDesign-Transform
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **开发代码**
   - 遵循代码规范
   - 编写测试
   - 更新文档

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/your-feature-name
   ```

5. **创建Pull Request**
   - 填写PR描述
   - 关联相关Issue
   - 等待代码审查

#### 提交信息规范

使用[Conventional Commits](https://www.conventionalcommits.org/)格式：

- `feat:` - 新功能
- `fix:` - 修复bug
- `docs:` - 文档更新
- `style:` - 代码格式
- `refactor:` - 重构
- `test:` - 测试
- `chore:` - 构建/工具

示例：
```
feat: add multimodal knowledge graph support
fix: resolve database connection issue
docs: update API documentation
```

---

## 📝 代码规范

### Python代码

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 使用类型提示
- 编写文档字符串
- 行长度不超过120字符

### TypeScript代码

- 遵循[TypeScript风格指南](https://typescript-eslint.io/)
- 使用ESLint检查
- 使用Prettier格式化

### 测试

- 为新功能编写测试
- 测试覆盖率目标：80%+
- 运行所有测试确保通过

```bash
# 运行测试
pytest code/tests/ -v

# 检查覆盖率
pytest code/tests/ --cov=code --cov-report=html
```

---

## 📚 文档规范

### Markdown文档

- 使用标准Markdown格式
- 添加目录（如果文档较长）
- 使用代码块时指定语言
- 添加适当的标题层级

### 代码文档

- 使用Google风格的文档字符串
- 为所有公共函数/类添加文档
- 包含参数说明和返回值说明

示例：
```python
def add_entity(entity_id: str, entity_type: str, properties: dict) -> bool:
    """
    添加实体到知识图谱

    Args:
        entity_id: 实体ID
        entity_type: 实体类型
        properties: 实体属性

    Returns:
        是否添加成功

    Raises:
        ValueError: 如果实体ID已存在
    """
    pass
```

---

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
pytest code/tests/

# 运行特定测试
pytest code/tests/test_multimodal_kg.py

# 运行性能测试
pytest code/tests/test_performance.py
```

### 编写测试

```python
def test_add_entity():
    """测试添加实体"""
    storage = MultimodalKGStorage()
    result = storage.add_entity(
        entity_id="test_001",
        entity_type="schema",
        properties={}
    )
    assert result == True
```

---

## 🔍 代码审查

### 审查清单

- [ ] 代码符合规范
- [ ] 测试通过
- [ ] 文档更新
- [ ] 无安全漏洞
- [ ] 性能可接受

---

## 📞 获取帮助

- 查看[文档](docs/)
- 查看[FAQ](FAQ.md)
- 创建[Issue](https://github.com/your-repo/issues)
- 联系维护者

---

**感谢您的贡献！** 🎉
