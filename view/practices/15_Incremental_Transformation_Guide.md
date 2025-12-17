# 增量转换实施指南

## 📑 目录

- [增量转换实施指南](#增量转换实施指南)
  - [📑 目录](#-目录)
  - [1. 实施概述](#1-实施概述)
    - [1.1 实施目标](#11-实施目标)
    - [1.2 实施步骤](#12-实施步骤)
  - [2. 变更检测实现](#2-变更检测实现)
    - [2.1 哈希比较实现](#21-哈希比较实现)
    - [2.2 差异算法实现](#22-差异算法实现)
    - [2.3 事件驱动实现](#23-事件驱动实现)
  - [3. 增量更新实现](#3-增量更新实现)
    - [3.1 更新策略实现](#31-更新策略实现)
    - [3.2 增量转换引擎](#32-增量转换引擎)
    - [3.3 结果合并机制](#33-结果合并机制)
  - [4. 依赖分析实现](#4-依赖分析实现)
    - [4.1 依赖图构建](#41-依赖图构建)
    - [4.2 依赖传播实现](#42-依赖传播实现)
    - [4.3 依赖优化实现](#43-依赖优化实现)
  - [5. 冲突处理实现](#5-冲突处理实现)
    - [5.1 冲突检测](#51-冲突检测)
    - [5.2 冲突解决策略](#52-冲突解决策略)
    - [5.3 冲突合并算法](#53-冲突合并算法)
  - [6. 性能优化实现](#6-性能优化实现)
    - [6.1 缓存机制](#61-缓存机制)
    - [6.2 并行处理](#62-并行处理)
    - [6.3 延迟计算](#63-延迟计算)
  - [7. 测试与验证](#7-测试与验证)
    - [7.1 单元测试](#71-单元测试)
    - [7.2 集成测试](#72-集成测试)
    - [7.3 性能测试](#73-性能测试)
  - [8. 部署与运维](#8-部署与运维)
    - [8.1 部署配置](#81-部署配置)
    - [8.2 监控告警](#82-监控告警)
    - [8.3 故障处理](#83-故障处理)
  - [9. 增量转换综合应用实际示例](#9-增量转换综合应用实际示例)
  - [10. 参考文档](#10-参考文档)
    - [算法文档](#算法文档)
    - [模式文档 ⭐新增](#模式文档-新增)
  - [📝 版本历史](#-版本历史)

---

## 1. 实施概述

### 1.1 实施目标

**实施目标**：

1. **变更检测准确率**：≥ 95%
2. **增量更新效率**：提升70%以上
3. **依赖分析完整性**：100%
4. **冲突处理正确性**：100%

### 1.2 实施步骤

**实施阶段**：

1. **阶段1**：变更检测实现（Week 1）
2. **阶段2**：增量更新实现（Week 1-2）
3. **阶段3**：依赖分析实现（Week 2）
4. **阶段4**：冲突处理实现（Week 2-3）
5. **阶段5**：性能优化（Week 3）
6. **阶段6**：测试验证（Week 3-4）

---

## 2. 变更检测实现

### 2.1 哈希比较实现

**实现代码**：

```typescript
// src/transformers/incremental/change-detector.ts
import { createHash } from 'crypto';

export class ChangeDetector {
  private hashCache: Map<string, string> = new Map();

  computeHash(schema: Schema): string {
    const key = schema.id;
    if (this.hashCache.has(key)) {
      return this.hashCache.get(key)!;
    }

    const hash = createHash('sha256')
      .update(JSON.stringify(schema))
      .digest('hex');

    this.hashCache.set(key, hash);
    return hash;
  }

  detectChanges(
    oldSchema: Schema,
    newSchema: Schema
  ): Change[] {
    const oldHash = this.computeHash(oldSchema);
    const newHash = this.computeHash(newSchema);

    if (oldHash === newHash) {
      return []; // 无变更
    }

    // 使用差异算法检测详细变更
    return this.detectDetailedChanges(oldSchema, newSchema);
  }

  private detectDetailedChanges(
    oldSchema: Schema,
    newSchema: Schema
  ): Change[] {
    const changes: Change[] = [];

    // 检测字段变更
    changes.push(...this.detectFieldChanges(oldSchema, newSchema));

    // 检测类型变更
    changes.push(...this.detectTypeChanges(oldSchema, newSchema));

    // 检测操作变更
    changes.push(...this.detectOperationChanges(oldSchema, newSchema));

    return changes;
  }
}
```

### 2.2 差异算法实现

**Myers算法实现**：

```typescript
// src/transformers/incremental/diff-algorithm.ts
export class DiffAlgorithm {
  computeDiff(oldSchema: Schema, newSchema: Schema): Change[] {
    const oldPaths = this.extractPaths(oldSchema);
    const newPaths = this.extractPaths(newSchema);

    return this.myersDiff(oldPaths, newPaths);
  }

  private myersDiff(
    oldPaths: string[],
    newPaths: string[]
  ): Change[] {
    // Myers差异算法实现
    const changes: Change[] = [];
    const n = oldPaths.length;
    const m = newPaths.length;

    // 实现Myers算法核心逻辑
    // ...

    return changes;
  }
}
```

### 2.3 事件驱动实现

**事件监听**：

```typescript
// src/transformers/incremental/event-driven.ts
import { EventEmitter } from 'events';

export class SchemaChangeEmitter extends EventEmitter {
  watch(schema: Schema): void {
    // 监听Schema变更事件
    this.on('schema-change', (change: Change) => {
      this.handleChange(change);
    });
  }

  private handleChange(change: Change): void {
    // 处理变更事件
    this.emit('change-detected', change);
  }
}
```

---

## 3. 增量更新实现

### 3.1 更新策略实现

**策略实现**：

```typescript
// src/transformers/incremental/update-strategy.ts
export class UpdateStrategy {
  async update(
    changes: Change[],
    strategy: 'immediate' | 'batch' | 'delayed' | 'smart'
  ): Promise<void> {
    switch (strategy) {
      case 'immediate':
        return this.immediateUpdate(changes);
      case 'batch':
        return this.batchUpdate(changes);
      case 'delayed':
        return this.delayedUpdate(changes);
      case 'smart':
        return this.smartUpdate(changes);
    }
  }

  private async immediateUpdate(changes: Change[]): Promise<void> {
    for (const change of changes) {
      await this.processChange(change);
    }
  }

  private async batchUpdate(changes: Change[]): Promise<void> {
    // 批量处理变更
    await this.processBatch(changes);
  }

  private async smartUpdate(changes: Change[]): Promise<void> {
    // 根据变更类型选择策略
    const critical = changes.filter(c => c.priority === 'high');
    const normal = changes.filter(c => c.priority === 'normal');

    await this.immediateUpdate(critical);
    await this.batchUpdate(normal);
  }
}
```

### 3.2 增量转换引擎

**转换引擎**：

```typescript
// src/transformers/incremental/incremental-transformer.ts
export class IncrementalTransformer {
  async transformIncremental(
    oldSchema: Schema,
    newSchema: Schema,
    changes: Change[]
  ): Promise<TransformationResult> {
    const result: TransformationResult = {
      changed: [],
      unchanged: [],
      deleted: [],
    };

    for (const change of changes) {
      switch (change.type) {
        case 'add':
          result.changed.push(await this.transformAdded(change));
          break;
        case 'modify':
          result.changed.push(await this.transformModified(change));
          break;
        case 'delete':
          result.deleted.push(await this.transformDeleted(change));
          break;
      }
    }

    return result;
  }

  private async transformAdded(change: Change): Promise<TransformedNode> {
    // 转换新增节点
    return this.transform(change.newValue);
  }

  private async transformModified(change: Change): Promise<TransformedNode> {
    // 转换修改节点
    const oldResult = this.getCachedResult(change.path);
    const newResult = await this.transform(change.newValue);

    // 合并结果
    return this.mergeResults(oldResult, newResult);
  }

  private async transformDeleted(change: Change): Promise<void> {
    // 清理删除节点
    this.removeCachedResult(change.path);
  }
}
```

### 3.3 结果合并机制

**合并算法**：

```typescript
// src/transformers/incremental/result-merger.ts
export class ResultMerger {
  merge(
    oldResult: TransformationResult,
    newResult: TransformationResult
  ): TransformationResult {
    return {
      changed: this.mergeChanged(oldResult.changed, newResult.changed),
      unchanged: this.mergeUnchanged(oldResult.unchanged, newResult.unchanged),
      deleted: this.mergeDeleted(oldResult.deleted, newResult.deleted),
    };
  }

  private mergeChanged(
    old: TransformedNode[],
    new_: TransformedNode[]
  ): TransformedNode[] {
    // 合并变更结果
    const merged = new Map<string, TransformedNode>();

    old.forEach(node => merged.set(node.id, node));
    new_.forEach(node => {
      const existing = merged.get(node.id);
      if (existing) {
        merged.set(node.id, this.mergeNode(existing, node));
      } else {
        merged.set(node.id, node);
      }
    });

    return Array.from(merged.values());
  }
}
```

---

## 4. 依赖分析实现

### 4.1 依赖图构建

**构建实现**：

```typescript
// src/transformers/incremental/dependency-graph.ts
export class DependencyGraphBuilder {
  buildGraph(schemas: Schema[]): DependencyGraph {
    const graph: DependencyGraph = {
      nodes: new Map(),
      edges: new Map(),
    };

    // 构建节点
    schemas.forEach(schema => {
      graph.nodes.set(schema.id, {
        id: schema.id,
        schema,
        dependencies: [],
        dependents: [],
      });
    });

    // 构建边
    schemas.forEach(schema => {
      const dependencies = this.extractDependencies(schema);
      dependencies.forEach(depId => {
        this.addEdge(graph, schema.id, depId);
      });
    });

    return graph;
  }

  private extractDependencies(schema: Schema): string[] {
    const dependencies: string[] = [];

    // 提取引用依赖
    this.traverseSchema(schema, (node) => {
      if (node.$ref) {
        dependencies.push(this.resolveRef(node.$ref));
      }
    });

    return dependencies;
  }

  private addEdge(
    graph: DependencyGraph,
    from: string,
    to: string
  ): void {
    const fromNode = graph.nodes.get(from);
    const toNode = graph.nodes.get(to);

    if (fromNode && toNode) {
      fromNode.dependencies.push(to);
      toNode.dependents.push(from);

      if (!graph.edges.has(from)) {
        graph.edges.set(from, []);
      }
      graph.edges.get(from)!.push({
        from,
        to,
        type: 'direct',
        weight: 1,
      });
    }
  }
}
```

### 4.2 依赖传播实现

**传播实现**：

```typescript
// src/transformers/incremental/dependency-propagator.ts
export class DependencyPropagator {
  propagate(
    graph: DependencyGraph,
    changedNode: string
  ): Set<string> {
    const affected: Set<string> = new Set();
    const queue: string[] = [changedNode];
    const visited: Set<string> = new Set();

    while (queue.length > 0) {
      const nodeId = queue.shift()!;

      if (visited.has(nodeId)) continue;
      visited.add(nodeId);
      affected.add(nodeId);

      const node = graph.nodes.get(nodeId);
      if (node) {
        // 传播到依赖节点
        node.dependents.forEach(dependentId => {
          if (!visited.has(dependentId)) {
            queue.push(dependentId);
          }
        });
      }
    }

    return affected;
  }

  getTopologicalOrder(graph: DependencyGraph): string[] {
    // 拓扑排序
    const inDegree = new Map<string, number>();
    const queue: string[] = [];
    const result: string[] = [];

    // 计算入度
    graph.nodes.forEach((node, id) => {
      inDegree.set(id, node.dependencies.length);
      if (node.dependencies.length === 0) {
        queue.push(id);
      }
    });

    // 拓扑排序
    while (queue.length > 0) {
      const nodeId = queue.shift()!;
      result.push(nodeId);

      const node = graph.nodes.get(nodeId);
      if (node) {
        node.dependents.forEach(dependentId => {
          const degree = inDegree.get(dependentId)! - 1;
          inDegree.set(dependentId, degree);
          if (degree === 0) {
            queue.push(dependentId);
          }
        });
      }
    }

    return result;
  }
}
```

### 4.3 依赖优化实现

**优化实现**：

```typescript
// src/transformers/incremental/dependency-optimizer.ts
export class DependencyOptimizer {
  optimize(graph: DependencyGraph): DependencyGraph {
    // 压缩传递依赖
    const optimized = this.compressTransitive(graph);

    // 缓存依赖关系
    this.cacheDependencies(optimized);

    return optimized;
  }

  private compressTransitive(
    graph: DependencyGraph
  ): DependencyGraph {
    // 压缩传递依赖
    const compressed = this.cloneGraph(graph);

    // 移除传递边
    compressed.nodes.forEach((node, id) => {
      const directDeps = new Set(node.dependencies);
      const transitiveDeps = this.getTransitiveDependencies(graph, id);

      transitiveDeps.forEach(transDep => {
        if (directDeps.has(transDep)) {
          // 移除传递依赖
          this.removeEdge(compressed, id, transDep);
        }
      });
    });

    return compressed;
  }

  private getTransitiveDependencies(
    graph: DependencyGraph,
    nodeId: string
  ): Set<string> {
    const transitive = new Set<string>();
    const visited = new Set<string>();

    const dfs = (id: string) => {
      if (visited.has(id)) return;
      visited.add(id);

      const node = graph.nodes.get(id);
      if (node) {
        node.dependencies.forEach(depId => {
          transitive.add(depId);
          dfs(depId);
        });
      }
    };

    const node = graph.nodes.get(nodeId);
    if (node) {
      node.dependencies.forEach(depId => {
        dfs(depId);
      });
    }

    return transitive;
  }
}
```

---

## 5. 冲突处理实现

### 5.1 冲突检测

**检测实现**：

```typescript
// src/transformers/incremental/conflict-detector.ts
export class ConflictDetector {
  detectConflicts(changes: Change[]): Conflict[] {
    const conflicts: Conflict[] = [];

    // 检测并发修改冲突
    conflicts.push(...this.detectConcurrentModifications(changes));

    // 检测依赖冲突
    conflicts.push(...this.detectDependencyConflicts(changes));

    // 检测转换冲突
    conflicts.push(...this.detectTransformationConflicts(changes));

    return conflicts;
  }

  private detectConcurrentModifications(
    changes: Change[]
  ): Conflict[] {
    const conflicts: Conflict[] = [];
    const pathChanges = new Map<string, Change[]>();

    // 按路径分组变更
    changes.forEach(change => {
      const path = change.path.join('.');
      if (!pathChanges.has(path)) {
        pathChanges.set(path, []);
      }
      pathChanges.get(path)!.push(change);
    });

    // 检测同一路径的多个变更
    pathChanges.forEach((changesForPath, path) => {
      if (changesForPath.length > 1) {
        conflicts.push({
          type: 'concurrent-modification',
          path,
          changes: changesForPath,
          resolution: 'merge',
        });
      }
    });

    return conflicts;
  }
}
```

### 5.2 冲突解决策略

**解决策略**：

```typescript
// src/transformers/incremental/conflict-resolver.ts
export class ConflictResolver {
  async resolve(conflict: Conflict): Promise<Resolution> {
    switch (conflict.type) {
      case 'concurrent-modification':
        return this.resolveConcurrentModification(conflict);
      case 'dependency':
        return this.resolveDependency(conflict);
      case 'transformation':
        return this.resolveTransformation(conflict);
    }
  }

  private async resolveConcurrentModification(
    conflict: Conflict
  ): Promise<Resolution> {
    // 合并策略
    if (conflict.resolution === 'merge') {
      return this.mergeChanges(conflict.changes);
    }

    // 最后写入获胜
    if (conflict.resolution === 'last-write-wins') {
      return this.lastWriteWins(conflict.changes);
    }

    // 手动解决
    return this.manualResolution(conflict);
  }
}
```

### 5.3 冲突合并算法

**合并算法**：

```typescript
// src/transformers/incremental/conflict-merger.ts
export class ConflictMerger {
  merge(changes: Change[]): Change {
    // 三路合并算法
    const base = this.getBaseVersion(changes[0].path);
    const change1 = changes[0];
    const change2 = changes[1];

    return this.threeWayMerge(base, change1, change2);
  }

  private threeWayMerge(
    base: any,
    change1: Change,
    change2: Change
  ): Change {
    // 三路合并逻辑
    // 1. 如果两个变更相同，返回任一
    if (this.isEqual(change1.newValue, change2.newValue)) {
      return change1;
    }

    // 2. 如果一个变更与base相同，返回另一个
    if (this.isEqual(change1.newValue, base)) {
      return change2;
    }
    if (this.isEqual(change2.newValue, base)) {
      return change1;
    }

    // 3. 否则需要手动合并
    return this.manualMerge(change1, change2);
  }
}
```

---

## 6. 性能优化实现

### 6.1 缓存机制

**缓存实现**：

```typescript
// src/transformers/incremental/transformation-cache.ts
export class TransformationCache {
  private cache: Map<string, CachedResult> = new Map();

  get(key: string): CachedResult | null {
    const cached = this.cache.get(key);
    if (cached && !this.isExpired(cached)) {
      return cached;
    }
    return null;
  }

  set(key: string, result: TransformationResult): void {
    this.cache.set(key, {
      result,
      timestamp: Date.now(),
      ttl: 3600000, // 1小时
    });
  }

  invalidate(pattern: string): void {
    // 失效匹配的缓存
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}
```

### 6.2 并行处理

**并行实现**：

```typescript
// src/transformers/incremental/parallel-processor.ts
export class ParallelProcessor {
  async processParallel(
    tasks: Task[],
    concurrency: number = 5
  ): Promise<Result[]> {
    const results: Result[] = [];
    const executing: Promise<void>[] = [];

    for (const task of tasks) {
      const promise = this.processTask(task).then(result => {
        results.push(result);
      });

      executing.push(promise);

      if (executing.length >= concurrency) {
        await Promise.race(executing);
        executing.splice(
          executing.findIndex(p => p === promise),
          1
        );
      }
    }

    await Promise.all(executing);
    return results;
  }
}
```

### 6.3 延迟计算

**延迟实现**：

```typescript
// src/transformers/incremental/lazy-evaluator.ts
export class LazyEvaluator {
  private lazyResults: Map<string, () => Promise<any>> = new Map();

  lazyTransform(path: string, transformer: () => Promise<any>): void {
    this.lazyResults.set(path, transformer);
  }

  async evaluate(path: string): Promise<any> {
    const transformer = this.lazyResults.get(path);
    if (transformer) {
      return await transformer();
    }
    return null;
  }

  async evaluateAll(): Promise<Map<string, any>> {
    const results = new Map<string, any>();

    for (const [path, transformer] of this.lazyResults.entries()) {
      results.set(path, await transformer());
    }

    return results;
  }
}
```

---

## 7. 测试与验证

### 7.1 单元测试

**测试用例**：

```typescript
// tests/incremental/change-detector.test.ts
describe('ChangeDetector', () => {
  it('should detect schema changes', () => {
    const detector = new ChangeDetector();
    const oldSchema = loadSchema('old.json');
    const newSchema = loadSchema('new.json');

    const changes = detector.detectChanges(oldSchema, newSchema);
    expect(changes.length).toBeGreaterThan(0);
  });
});
```

### 7.2 集成测试

**集成测试**：

```typescript
// tests/incremental/integration.test.ts
describe('Incremental Transformation Integration', () => {
  it('should transform incrementally', async () => {
    const transformer = new IncrementalTransformer();
    const oldSchema = loadSchema('v1.json');
    const newSchema = loadSchema('v2.json');

    const result = await transformer.transform(oldSchema, newSchema);
    expect(result.changed.length).toBeGreaterThan(0);
  });
});
```

### 7.3 性能测试

**性能测试**：

```typescript
// tests/incremental/performance.test.ts
describe('Performance Tests', () => {
  it('should be faster than full transformation', async () => {
    const transformer = new IncrementalTransformer();
    const oldSchema = loadLargeSchema('large-v1.json');
    const newSchema = loadLargeSchema('large-v2.json');

    const start = Date.now();
    await transformer.transform(oldSchema, newSchema);
    const incrementalTime = Date.now() - start;

    const start2 = Date.now();
    await fullTransform(newSchema);
    const fullTime = Date.now() - start2;

    expect(incrementalTime).toBeLessThan(fullTime * 0.3);
  });
});
```

---

## 8. 部署与运维

### 8.1 部署配置

**配置示例**：

```yaml
# config/incremental.yaml
changeDetection:
  method: hash
  hashAlgorithm: sha256
  cacheEnabled: true

updateStrategy:
  default: smart
  critical: immediate
  normal: batch

dependencyAnalysis:
  enabled: true
  cacheEnabled: true
  optimizationEnabled: true

conflictResolution:
  default: merge
  concurrent: last-write-wins
```

### 8.2 监控告警

**监控指标**：

- 变更检测时间
- 增量转换时间
- 依赖分析时间
- 冲突处理时间
- 缓存命中率

### 8.3 故障处理

**故障处理**：

1. 变更检测失败：回退到全量转换
2. 依赖分析失败：使用保守策略
3. 冲突处理失败：标记为手动处理

---

## 9. 增量转换综合应用实际示例

**示例：实现增量Schema转换综合框架**

```python
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from collections import defaultdict

class ChangeType(Enum):
    """变更类型"""
    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"

class ConflictResolution(Enum):
    """冲突解决策略"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    MANUAL = "manual"

@dataclass
class SchemaChange:
    """Schema变更"""
    path: str
    change_type: ChangeType
    old_value: Any = None
    new_value: Any = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class DependencyNode:
    """依赖节点"""
    schema_id: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)

@dataclass
class ConflictInfo:
    """冲突信息"""
    path: str
    conflicting_changes: List[SchemaChange]
    resolution: Optional[str] = None

class IncrementalTransformationFramework:
    """增量转换综合框架"""

    def __init__(self):
        # 变更检测（基于第2章）
        self.schema_hashes: Dict[str, str] = {}
        self.change_history: Dict[str, List[SchemaChange]] = defaultdict(list)

        # 依赖分析（基于第4章）
        self.dependency_graph: Dict[str, DependencyNode] = {}

        # 缓存（基于第6章）
        self.transform_cache: Dict[str, Dict] = {}
        self.cache_timestamps: Dict[str, float] = {}

        # 冲突处理（基于第5章）
        self.conflicts: List[ConflictInfo] = []
        self.default_resolution = ConflictResolution.MERGE

    # ===== 变更检测（基于第2章）=====
    def compute_hash(self, schema: Dict) -> str:
        """计算Schema哈希（基于第2.1章）"""
        normalized = self._normalize_schema(schema)
        return hashlib.sha256(str(normalized).encode()).hexdigest()

    def detect_changes(self, schema_id: str, old_schema: Dict, new_schema: Dict) -> List[SchemaChange]:
        """检测变更（基于第2.2章）"""
        changes = []
        self._diff_schemas(old_schema, new_schema, "", changes)

        # 记录变更历史
        self.change_history[schema_id].extend(changes)

        # 更新哈希
        self.schema_hashes[schema_id] = self.compute_hash(new_schema)

        return changes

    def _diff_schemas(self, old: Any, new: Any, path: str, changes: List[SchemaChange]):
        """递归比较Schema"""
        if old is None and new is not None:
            changes.append(SchemaChange(path=path, change_type=ChangeType.ADD, new_value=new))
        elif old is not None and new is None:
            changes.append(SchemaChange(path=path, change_type=ChangeType.DELETE, old_value=old))
        elif isinstance(old, dict) and isinstance(new, dict):
            all_keys = set(old.keys()) | set(new.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                self._diff_schemas(old.get(key), new.get(key), new_path, changes)
        elif old != new:
            changes.append(SchemaChange(
                path=path, change_type=ChangeType.MODIFY,
                old_value=old, new_value=new
            ))

    def _normalize_schema(self, schema: Any) -> Any:
        """规范化Schema用于哈希计算"""
        if isinstance(schema, dict):
            return tuple(sorted((k, self._normalize_schema(v)) for k, v in schema.items()))
        elif isinstance(schema, list):
            return tuple(self._normalize_schema(item) for item in schema)
        return schema

    # ===== 增量更新（基于第3章）=====
    def incremental_transform(self, schema_id: str, changes: List[SchemaChange],
                               base_result: Dict, transformer: callable) -> Dict:
        """增量转换（基于第3.1章）"""
        if not changes:
            return base_result

        result = base_result.copy()

        # 分析影响范围
        affected_paths = self._analyze_affected_paths(changes)

        # 按变更类型处理
        for change in changes:
            if change.change_type == ChangeType.ADD:
                self._apply_add_change(result, change, transformer)
            elif change.change_type == ChangeType.MODIFY:
                self._apply_modify_change(result, change, transformer)
            elif change.change_type == ChangeType.DELETE:
                self._apply_delete_change(result, change)

        # 更新缓存
        self.transform_cache[schema_id] = result
        self.cache_timestamps[schema_id] = time.time()

        return result

    def _analyze_affected_paths(self, changes: List[SchemaChange]) -> Set[str]:
        """分析受影响的路径"""
        affected = set()
        for change in changes:
            affected.add(change.path)
            # 添加父路径
            parts = change.path.split('.')
            for i in range(len(parts)):
                affected.add('.'.join(parts[:i+1]))
        return affected

    def _apply_add_change(self, result: Dict, change: SchemaChange, transformer: callable):
        """应用添加变更"""
        path_parts = change.path.split('.') if change.path else []
        current = result

        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        if path_parts:
            transformed = transformer({path_parts[-1]: change.new_value})
            current[path_parts[-1]] = transformed.get(path_parts[-1], change.new_value)

    def _apply_modify_change(self, result: Dict, change: SchemaChange, transformer: callable):
        """应用修改变更"""
        self._apply_add_change(result, change, transformer)

    def _apply_delete_change(self, result: Dict, change: SchemaChange):
        """应用删除变更"""
        path_parts = change.path.split('.') if change.path else []
        current = result

        for part in path_parts[:-1]:
            if part not in current:
                return
            current = current[part]

        if path_parts and path_parts[-1] in current:
            del current[path_parts[-1]]

    # ===== 依赖分析（基于第4章）=====
    def build_dependency_graph(self, schemas: Dict[str, Dict]):
        """构建依赖图（基于第4.1章）"""
        self.dependency_graph.clear()

        for schema_id, schema in schemas.items():
            node = DependencyNode(schema_id=schema_id)
            self.dependency_graph[schema_id] = node

        # 分析依赖关系
        for schema_id, schema in schemas.items():
            refs = self._extract_references(schema)
            for ref in refs:
                if ref in self.dependency_graph:
                    self.dependency_graph[schema_id].dependencies.add(ref)
                    self.dependency_graph[ref].dependents.add(schema_id)

    def _extract_references(self, schema: Any, refs: Set[str] = None) -> Set[str]:
        """提取Schema引用"""
        if refs is None:
            refs = set()

        if isinstance(schema, dict):
            if '$ref' in schema:
                ref = schema['$ref']
                # 提取引用的Schema ID
                if ref.startswith('#/components/schemas/'):
                    refs.add(ref.split('/')[-1])
            for value in schema.values():
                self._extract_references(value, refs)
        elif isinstance(schema, list):
            for item in schema:
                self._extract_references(item, refs)

        return refs

    def get_affected_schemas(self, schema_id: str) -> Set[str]:
        """获取受影响的Schema（基于第4.2章）"""
        affected = set()
        self._propagate_dependencies(schema_id, affected)
        return affected

    def _propagate_dependencies(self, schema_id: str, affected: Set[str]):
        """传播依赖"""
        if schema_id in affected:
            return

        affected.add(schema_id)

        if schema_id in self.dependency_graph:
            for dependent in self.dependency_graph[schema_id].dependents:
                self._propagate_dependencies(dependent, affected)

    def get_transform_order(self) -> List[str]:
        """获取转换顺序（拓扑排序）"""
        visited = set()
        order = []

        def visit(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)

            if node_id in self.dependency_graph:
                for dep in self.dependency_graph[node_id].dependencies:
                    visit(dep)

            order.append(node_id)

        for node_id in self.dependency_graph:
            visit(node_id)

        return order

    # ===== 冲突处理（基于第5章）=====
    def detect_conflicts(self, changes1: List[SchemaChange],
                          changes2: List[SchemaChange]) -> List[ConflictInfo]:
        """检测冲突（基于第5.1章）"""
        conflicts = []

        # 按路径分组
        changes1_by_path = {c.path: c for c in changes1}
        changes2_by_path = {c.path: c for c in changes2}

        # 检测同一路径的冲突
        common_paths = set(changes1_by_path.keys()) & set(changes2_by_path.keys())

        for path in common_paths:
            c1 = changes1_by_path[path]
            c2 = changes2_by_path[path]

            if c1.new_value != c2.new_value:
                conflicts.append(ConflictInfo(
                    path=path,
                    conflicting_changes=[c1, c2]
                ))

        self.conflicts.extend(conflicts)
        return conflicts

    def resolve_conflict(self, conflict: ConflictInfo,
                          strategy: ConflictResolution = None) -> SchemaChange:
        """解决冲突（基于第5.2章）"""
        strategy = strategy or self.default_resolution
        changes = conflict.conflicting_changes

        if strategy == ConflictResolution.LAST_WRITE_WINS:
            # 最后写入胜出
            latest = max(changes, key=lambda c: c.timestamp)
            conflict.resolution = f"last_write_wins: {latest.timestamp}"
            return latest

        elif strategy == ConflictResolution.FIRST_WRITE_WINS:
            # 最先写入胜出
            earliest = min(changes, key=lambda c: c.timestamp)
            conflict.resolution = f"first_write_wins: {earliest.timestamp}"
            return earliest

        elif strategy == ConflictResolution.MERGE:
            # 合并策略
            merged = self._merge_changes(changes)
            conflict.resolution = "merged"
            return merged

        else:
            # 手动处理
            conflict.resolution = "manual"
            return changes[0]

    def _merge_changes(self, changes: List[SchemaChange]) -> SchemaChange:
        """合并变更"""
        # 简单合并：使用最新的非空值
        latest = max(changes, key=lambda c: c.timestamp)

        if all(isinstance(c.new_value, dict) for c in changes if c.new_value):
            merged_value = {}
            for change in sorted(changes, key=lambda c: c.timestamp):
                if isinstance(change.new_value, dict):
                    merged_value.update(change.new_value)
            return SchemaChange(
                path=latest.path,
                change_type=ChangeType.MODIFY,
                new_value=merged_value
            )

        return latest

    # ===== 性能优化（基于第6章）=====
    def get_cached_result(self, schema_id: str) -> Optional[Dict]:
        """获取缓存结果（基于第6.1章）"""
        if schema_id in self.transform_cache:
            return self.transform_cache[schema_id]
        return None

    def invalidate_cache(self, schema_id: str):
        """失效缓存"""
        if schema_id in self.transform_cache:
            del self.transform_cache[schema_id]
            del self.cache_timestamps[schema_id]

        # 级联失效依赖的Schema
        affected = self.get_affected_schemas(schema_id)
        for affected_id in affected:
            if affected_id in self.transform_cache:
                del self.transform_cache[affected_id]

    def get_transformation_stats(self) -> Dict:
        """获取转换统计"""
        return {
            'total_schemas': len(self.dependency_graph),
            'cached_results': len(self.transform_cache),
            'total_changes': sum(len(changes) for changes in self.change_history.values()),
            'unresolved_conflicts': len([c for c in self.conflicts if not c.resolution]),
            'dependency_stats': {
                'max_depth': self._calculate_max_depth(),
                'avg_dependencies': self._calculate_avg_dependencies()
            }
        }

    def _calculate_max_depth(self) -> int:
        """计算最大依赖深度"""
        def depth(node_id: str, visited: Set[str]) -> int:
            if node_id in visited or node_id not in self.dependency_graph:
                return 0
            visited.add(node_id)
            deps = self.dependency_graph[node_id].dependencies
            if not deps:
                return 1
            return 1 + max(depth(d, visited) for d in deps)

        if not self.dependency_graph:
            return 0
        return max(depth(n, set()) for n in self.dependency_graph)

    def _calculate_avg_dependencies(self) -> float:
        """计算平均依赖数"""
        if not self.dependency_graph:
            return 0
        total_deps = sum(len(n.dependencies) for n in self.dependency_graph.values())
        return total_deps / len(self.dependency_graph)

# 实际应用示例
framework = IncrementalTransformationFramework()

# 示例1：变更检测
print("=== 示例1：变更检测 ===")
old_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'age': {'type': 'integer'}
    }
}
new_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string', 'maxLength': 100},
        'email': {'type': 'string'}
    }
}
changes = framework.detect_changes('user_schema', old_schema, new_schema)
print(f"检测到 {len(changes)} 个变更:")
for change in changes:
    print(f"  [{change.change_type.value}] {change.path}")

# 示例2：依赖分析
print("\n=== 示例2：依赖分析 ===")
schemas = {
    'User': {'type': 'object', 'properties': {}},
    'Order': {
        'type': 'object',
        'properties': {
            'user': {'$ref': '#/components/schemas/User'}
        }
    },
    'Invoice': {
        'type': 'object',
        'properties': {
            'order': {'$ref': '#/components/schemas/Order'}
        }
    }
}
framework.build_dependency_graph(schemas)
print(f"转换顺序: {framework.get_transform_order()}")

affected = framework.get_affected_schemas('User')
print(f"User变更影响: {affected}")

# 示例3：冲突检测与解决
print("\n=== 示例3：冲突检测与解决 ===")
changes1 = [SchemaChange(path='properties.name', change_type=ChangeType.MODIFY,
                          new_value={'type': 'string', 'maxLength': 50})]
changes2 = [SchemaChange(path='properties.name', change_type=ChangeType.MODIFY,
                          new_value={'type': 'string', 'maxLength': 100})]
conflicts = framework.detect_conflicts(changes1, changes2)
print(f"检测到 {len(conflicts)} 个冲突")
if conflicts:
    resolved = framework.resolve_conflict(conflicts[0], ConflictResolution.MERGE)
    print(f"解决方案: {resolved.new_value}")

# 示例4：统计信息
print("\n=== 转换统计 ===")
stats = framework.get_transformation_stats()
for key, value in stats.items():
    print(f"  {key}: {value}")
```

---

## 10. 参考文档

### 算法文档

- `analysis/12_Incremental_Transformation_Algorithm.md` - 增量转换算法分析
- `src/transformers/incremental/` - 增量转换代码实现

### 模式文档 ⭐新增

- `docs/structure/INFORMATION_PROCESSING_PATTERNS_SUMMARY.md`：信息处理模式总结（12个模式）
  - 在增量转换中，可以参考流处理模式、实时处理模式、批处理模式等
- `docs/structure/ARCHITECTURE_PATTERNS_SUMMARY.md`：架构模式总结（12个模式）
  - 在增量转换系统架构设计中，可以参考事件驱动架构、微服务架构等
- `docs/structure/DESIGN_PATTERNS_SUMMARY.md`：设计模式总结（15个模式）
  - 在增量转换实现中，可以参考观察者模式、策略模式、状态模式等
- `docs/structure/PATTERNS_QUICK_REFERENCE.md`：模式快速参考指南 ⭐推荐

---

## 📝 版本历史

### v1.2 (2025-01-21) - 实际应用示例增强版

- ✅ 扩展第9章：为增量转换添加综合应用实际示例（包含增量转换综合框架实现、变更检测、依赖图构建、依赖传播、冲突检测、冲突解决、缓存管理、统计分析）
- ✅ 添加版本历史章节
- ✅ 更新文档版本号至v1.2

### v1.1 (2025-01-27) - 初始版本

- ✅ 创建文档：增量转换实施指南
- ✅ 添加变更检测实现
- ✅ 添加增量更新实现
- ✅ 添加依赖分析实现
- ✅ 添加冲突处理实现
- ✅ 添加性能优化实现
- ✅ 添加测试与验证
- ✅ 添加部署与运维

---

**文档版本**：1.2（实际应用示例增强版）
**创建时间**：2025-01-21
**最后更新**：2025-01-21
