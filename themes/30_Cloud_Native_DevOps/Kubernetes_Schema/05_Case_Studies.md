# Kubernetes Schema实践案例

## 📑 目录

- [Kubernetes Schema实践案例](#kubernetes-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：大型电商平台K8s生产部署](#2-案例1大型电商平台k8s生产部署)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 完整代码实现](#25-完整代码实现)
    - [2.6 效果评估与ROI](#26-效果评估与roi)

---

## 2. 案例1：大型电商平台K8s生产部署

### 2.1 企业背景

**企业概况**：
"云商网"（化名）是领先的B2B电商平台，服务超过100万企业客户，日均订单量超过50万单，系统峰值QPS达到20万。

### 2.2 业务痛点

1. **部署效率低**：传统部署需要2-4小时，无法满足快速迭代需求
2. **资源利用率低**：虚拟机平均利用率仅30%，资源浪费严重
3. **故障恢复慢**：服务故障需要15分钟恢复，影响用户体验
4. **扩展困难**：大促期间扩容需要数小时，无法应对流量突发
5. **环境不一致**：开发、测试、生产环境配置不一致

### 2.3 业务目标

1. 实现快速部署（<10分钟）
2. 提高资源利用率至70%以上
3. 故障恢复时间<2分钟
4. 支持秒级自动扩展
5. 确保环境一致性100%

### 2.4 技术挑战

1. **高可用架构设计**：多可用区部署、故障自动转移
2. **大规模集群管理**：1000+节点集群运维
3. **有状态服务管理**：数据库、缓存的K8s化
4. **服务网格集成**：Istio服务治理
5. **可观测性建设**：日志、监控、链路追踪

### 2.5 完整代码实现

```python
#!/usr/bin/env python3
"""
Kubernetes Schema完整实现
云商网K8s生产部署平台
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json


class K8sResourceType(str, Enum):
    """K8s资源类型"""
    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    HPA = "HorizontalPodAutoscaler"
    STATEFULSET = "StatefulSet"
    DAEMONSET = "DaemonSet"
    JOB = "Job"
    CRONJOB = "CronJob"


@dataclass
class ContainerSpec:
    """容器规格"""
    name: str
    image: str
    ports: List[Dict] = field(default_factory=list)
    env: List[Dict] = field(default_factory=list)
    resources: Dict = field(default_factory=dict)
    liveness_probe: Optional[Dict] = None
    readiness_probe: Optional[Dict] = None
    volume_mounts: List[Dict] = field(default_factory=list)


@dataclass
class K8sDeployment:
    """K8s Deployment定义"""
    name: str
    namespace: str = "default"
    replicas: int = 3
    containers: List[ContainerSpec] = field(default_factory=list)
    labels: Dict = field(default_factory=dict)
    strategy: Dict = field(default_factory=lambda: {
        "type": "RollingUpdate",
        "rollingUpdate": {"maxSurge": 1, "maxUnavailable": 0}
    })
    affinity: Optional[Dict] = None
    tolerations: List[Dict] = field(default_factory=list)
    
    def to_yaml(self) -> str:
        """转换为YAML"""
        spec = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace,
                "labels": self.labels
            },
            "spec": {
                "replicas": self.replicas,
                "strategy": self.strategy,
                "selector": {
                    "matchLabels": {"app": self.name}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": self.name}
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": c.name,
                                "image": c.image,
                                "ports": c.ports,
                                "env": c.env,
                                "resources": c.resources,
                                "volumeMounts": c.volume_mounts
                            }
                            for c in self.containers
                        ],
                        "affinity": self.affinity,
                        "tolerations": self.tolerations
                    }
                }
            }
        }
        return yaml.dump(spec, default_flow_style=False)


@dataclass
class K8sService:
    """K8s Service定义"""
    name: str
    namespace: str = "default"
    selector: Dict = field(default_factory=dict)
    ports: List[Dict] = field(default_factory=list)
    service_type: str = "ClusterIP"
    
    def to_yaml(self) -> str:
        """转换为YAML"""
        spec = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace
            },
            "spec": {
                "type": self.service_type,
                "selector": self.selector,
                "ports": self.ports
            }
        }
        return yaml.dump(spec, default_flow_style=False)


@dataclass
class K8sHPA:
    """K8s HPA定义"""
    name: str
    namespace: str = "default"
    target_deployment: str = ""
    min_replicas: int = 3
    max_replicas: int = 100
    cpu_target: int = 70
    memory_target: Optional[int] = None
    
    def to_yaml(self) -> str:
        """转换为YAML"""
        metrics = [
            {
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": self.cpu_target
                    }
                }
            }
        ]
        
        if self.memory_target:
            metrics.append({
                "type": "Resource",
                "resource": {
                    "name": "memory",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": self.memory_target
                    }
                }
            })
        
        spec = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": self.name,
                "namespace": self.namespace
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": self.target_deployment
                },
                "minReplicas": self.min_replicas,
                "maxReplicas": self.max_replicas,
                "metrics": metrics
            }
        }
        return yaml.dump(spec, default_flow_style=False)


class K8sManifestGenerator:
    """K8s Manifest生成器"""
    
    def __init__(self, app_name: str, namespace: str = "production"):
        self.app_name = app_name
        self.namespace = namespace
        self.resources: List[Any] = []
    
    def add_deployment(self, image: str, replicas: int = 3, 
                      port: int = 8080, resources: Optional[Dict] = None):
        """添加Deployment"""
        container = ContainerSpec(
            name=self.app_name,
            image=image,
            ports=[{"containerPort": port}],
            resources=resources or {
                "requests": {"cpu": "200m", "memory": "512Mi"},
                "limits": {"cpu": "1000m", "memory": "1Gi"}
            },
            liveness_probe={
                "httpGet": {"path": "/health", "port": port},
                "initialDelaySeconds": 30,
                "periodSeconds": 10
            },
            readiness_probe={
                "httpGet": {"path": "/ready", "port": port},
                "initialDelaySeconds": 5,
                "periodSeconds": 5
            }
        )
        
        deployment = K8sDeployment(
            name=self.app_name,
            namespace=self.namespace,
            replicas=replicas,
            containers=[container],
            labels={"app": self.app_name, "version": "v1"},
            affinity={
                "podAntiAffinity": {
                    "preferredDuringSchedulingIgnoredDuringExecution": [
                        {
                            "weight": 100,
                            "podAffinityTerm": {
                                "labelSelector": {
                                    "matchExpressions": [
                                        {"key": "app", "operator": "In", "values": [self.app_name]}
                                    ]
                                },
                                "topologyKey": "kubernetes.io/hostname"
                            }
                        }
                    ]
                }
            }
        )
        self.resources.append(deployment)
        return self
    
    def add_service(self, port: int = 8080):
        """添加Service"""
        service = K8sService(
            name=self.app_name,
            namespace=self.namespace,
            selector={"app": self.app_name},
            ports=[{"port": 80, "targetPort": port}]
        )
        self.resources.append(service)
        return self
    
    def add_hpa(self, min_replicas: int = 3, max_replicas: int = 100):
        """添加HPA"""
        hpa = K8sHPA(
            name=f"{self.app_name}-hpa",
            namespace=self.namespace,
            target_deployment=self.app_name,
            min_replicas=min_replicas,
            max_replicas=max_replicas
        )
        self.resources.append(hpa)
        return self
    
    def generate(self) -> str:
        """生成完整Manifest"""
        manifests = []
        for resource in self.resources:
            manifests.append(resource.to_yaml())
            manifests.append("---")
        return "\n".join(manifests)


# 使用示例
def main():
    print("=" * 60)
    print("【云商网Kubernetes生产部署】")
    print("=" * 60)
    
    # 生成订单服务K8s配置
    generator = K8sManifestGenerator("order-service", "production")
    generator.add_deployment(
        image="registry.yunshang.com/order-service:v1.2.0",
        replicas=5,
        resources={
            "requests": {"cpu": "500m", "memory": "1Gi"},
            "limits": {"cpu": "2000m", "memory": "2Gi"}
        }
    ).add_service().add_hpa(min_replicas=5, max_replicas=50)
    
    manifest = generator.generate()
    
    print("\n📄 生成的K8s Manifest:")
    print("-" * 40)
    print(manifest)
    
    print("\n📊 部署效果对比:")
    print("-" * 40)
    print("指标          | 部署前    | 部署后    | 提升")
    print("-" * 40)
    print("部署时间      | 2-4小时   | 5-10分钟  | 95%")
    print("资源利用率    | 30%       | 75%       | 150%")
    print("故障恢复时间  | 15分钟    | 1-2分钟   | 90%")
    print("扩展时间      | 数小时    | <1分钟    | 99%")
    print("可用性        | 99.5%     | 99.99%    | +0.49%")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
```

### 2.6 效果评估与ROI

| 指标 | 改进前 | 改进后 | 提升幅度 |
|------|--------|--------|----------|
| 部署时间 | 2-4小时 | 5-10分钟 | 95%提升 |
| 资源利用率 | 30% | 75% | 150%提升 |
| 故障恢复时间 | 15分钟 | 1-2分钟 | 90%降低 |
| 扩展时间 | 数小时 | <1分钟 | 99%提升 |
| 系统可用性 | 99.5% | 99.99% | +0.49% |

**ROI计算**：

```
项目投资：520万元
年度收益：2,350万元
  - 资源成本节省：1,200万元
  - 效率提升：650万元
  - 可用性提升收益：500万元

第一年ROI = (2,350 - 520) / 520 = 352%
```

---

**创建时间**：2025-01-21
**最后更新**：2025-02-15
