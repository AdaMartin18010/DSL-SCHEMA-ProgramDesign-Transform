# Schema工具部署指南

## 系统要求

- Python 3.9+
- 内存: 4GB+
- Docker 20.10+ (可选)

## 安装步骤

### 本地安装
```bash
pip install -r requirements.txt
python Tools/schema_validator.py --help
```

### Docker部署
```bash
docker build -f Docker/Dockerfile -t schema-tools:latest .
docker-compose up -d
```

## 配置

```yaml
# config.yml
data_path: /app/data
log_level: INFO
security:
  max_schema_size: 1048576
```

## 监控

```bash
tail -f /var/log/schema-tools/app.log
```

---

**维护者**: DSL Schema研究团队
