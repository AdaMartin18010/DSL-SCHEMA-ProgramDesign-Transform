# DSL Schema 部署指南
## Deployment Guide

**版本**: 2.1.0  
**日期**: 2026-02-17

---

## 部署选项

| 方式 | 适用场景 | 复杂度 |
|------|---------|--------|
| Docker Compose | 开发/测试 | ⭐⭐ |
| Kubernetes | 生产环境 | ⭐⭐⭐⭐ |
| AWS ECS | 云原生 | ⭐⭐⭐ |

---

## Docker部署

```bash
cd themes/00_Meta/Deployment
docker-compose up -d
docker-compose ps
```

---

## Kubernetes部署

```bash
kubectl apply -f k8s-deployment.yaml
kubectl get pods -n dsl-schema
```

---

## 云平台部署

### AWS (Terraform)

```bash
cd terraform
terraform init
terraform apply
```

---

## 监控配置

### Prometheus指标

- 请求延迟 (P50, P95, P99)
- 错误率
- 资源使用

---

**维护者**: DSL Schema运维团队
