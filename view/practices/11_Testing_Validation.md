# 测试与验证方法

## 📑 目录

- [测试与验证方法](#测试与验证方法)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 测试目标](#11-测试目标)
    - [1.2 测试类型](#12-测试类型)
  - [2. 单元测试](#2-单元测试)
    - [2.1 测试方法](#21-测试方法)
      - [2.1.1 测试用例设计](#211-测试用例设计)
      - [2.1.2 测试覆盖率](#212-测试覆盖率)
    - [2.2 测试工具](#22-测试工具)
      - [2.2.1 测试框架](#221-测试框架)
      - [2.2.2 断言库](#222-断言库)
  - [3. 集成测试](#3-集成测试)
    - [3.1 测试方法](#31-测试方法)
      - [3.1.1 端到端测试](#311-端到端测试)
      - [3.1.2 组件集成测试](#312-组件集成测试)
    - [3.2 测试数据](#32-测试数据)
      - [3.2.1 测试数据生成](#321-测试数据生成)
      - [3.2.2 测试数据管理](#322-测试数据管理)
  - [4. 回归测试](#4-回归测试)
    - [4.1 测试方法](#41-测试方法)
      - [4.1.1 回归测试策略](#411-回归测试策略)
      - [4.1.2 测试用例维护](#412-测试用例维护)
    - [4.2 自动化回归](#42-自动化回归)
      - [4.2.1 CI/CD集成](#421-cicd集成)
      - [4.2.2 测试结果分析](#422-测试结果分析)
  - [5. 性能测试](#5-性能测试)
    - [5.1 测试方法](#51-测试方法)
      - [5.1.1 基准测试](#511-基准测试)
      - [5.1.2 压力测试](#512-压力测试)
    - [5.2 性能分析](#52-性能分析)
      - [5.2.1 性能分析工具](#521-性能分析工具)
  - [6. 安全测试](#6-安全测试)
    - [6.1 测试方法](#61-测试方法)
      - [6.1.1 安全漏洞测试](#611-安全漏洞测试)
      - [6.1.2 权限测试](#612-权限测试)
    - [6.2 安全扫描](#62-安全扫描)
      - [6.2.1 代码扫描](#621-代码扫描)
      - [6.2.2 依赖扫描](#622-依赖扫描)
  - [7. 测试最佳实践](#7-测试最佳实践)
    - [7.1 测试策略](#71-测试策略)
      - [7.1.1 测试金字塔](#711-测试金字塔)
      - [7.1.2 测试驱动开发（TDD）](#712-测试驱动开发tdd)
    - [7.2 测试维护](#72-测试维护)
      - [7.2.1 测试文档](#721-测试文档)
      - [7.2.2 测试自动化](#722-测试自动化)
  - [8. 总结](#8-总结)
    - [8.1 关键成果](#81-关键成果)
    - [8.2 测试建议](#82-测试建议)
  - [9. 测试验证综合应用实际示例](#9-测试验证综合应用实际示例)
  - [10. 相关文档](#10-相关文档)
    - [模式文档 ⭐新增](#模式文档-新增)
    - [其他实践文档](#其他实践文档)


---

## 1. 概述

### 1.1 测试目标

Schema转换的测试目标：

- **正确性验证**：验证转换结果的正确性
- **完整性验证**：验证转换的完整性
- **性能验证**：验证转换的性能
- **安全验证**：验证转换的安全性

### 1.2 测试类型

- **单元测试**：测试单个转换函数
- **集成测试**：测试转换流程
- **回归测试**：测试转换的回归
- **性能测试**：测试转换性能
- **安全测试**：测试转换安全性

---

## 2. 单元测试

### 2.1 测试方法

#### 2.1.1 测试用例设计

**测试用例类型**：

- **正常用例**：测试正常转换场景
- **边界用例**：测试边界条件
- **异常用例**：测试异常情况

**示例**：

```python
import unittest

class TestSchemaConversion(unittest.TestCase):
    def test_normal_conversion(self):
        """测试正常转换"""
        source_schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }
        result = convert_schema(source_schema, 'AsyncAPI')
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'object')

    def test_boundary_conditions(self):
        """测试边界条件"""
        # 空Schema
        empty_schema = {}
        result = convert_schema(empty_schema, 'AsyncAPI')
        self.assertIsNotNone(result)

        # 最大嵌套深度
        deep_schema = create_deep_schema(100)
        result = convert_schema(deep_schema, 'AsyncAPI')
        self.assertIsNotNone(result)

    def test_exception_handling(self):
        """测试异常处理"""
        invalid_schema = {'type': 'invalid'}
        with self.assertRaises(ConversionError):
            convert_schema(invalid_schema, 'AsyncAPI')
```

#### 2.1.2 测试覆盖率

**覆盖率目标**：

- **语句覆盖率**：>80%
- **分支覆盖率**：>75%
- **条件覆盖率**：>70%

**示例**：

```python
import coverage

cov = coverage.Coverage()
cov.start()

# 运行测试
unittest.main()

cov.stop()
cov.save()
cov.report()
```

### 2.2 测试工具

#### 2.2.1 测试框架

**框架推荐**：

- **pytest**：Python测试框架
- **unittest**：Python标准测试框架
- **nose2**：Python测试框架

**示例**：

```python
import pytest

@pytest.fixture
def sample_schema():
    return {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'}
        }
    }

def test_conversion(sample_schema):
    result = convert_schema(sample_schema, 'AsyncAPI')
    assert result is not None
```

#### 2.2.2 断言库

**断言库推荐**：

- **assertpy**：流畅的断言库
- **hamcrest**：匹配器库
- **should**：自然语言断言库

---

## 3. 集成测试

### 3.1 测试方法

#### 3.1.1 端到端测试

**测试流程**：

1. **准备数据**：准备测试数据
2. **执行转换**：执行转换流程
3. **验证结果**：验证转换结果
4. **清理数据**：清理测试数据

**示例**：

```python
class TestEndToEndConversion(unittest.TestCase):
    def setUp(self):
        self.source_schema = load_test_schema('openapi_sample.yaml')
        self.expected_schema = load_test_schema('asyncapi_expected.yaml')

    def test_openapi_to_asyncapi(self):
        """测试OpenAPI到AsyncAPI的端到端转换"""
        result = convert_openapi_to_asyncapi(self.source_schema)

        # 验证结构
        self.assertEqual(result['asyncapi'], '2.6.0')
        self.assertIn('channels', result)

        # 验证内容
        self.assertEqual(
            result['channels']['users']['publish']['message']['payload'],
            self.expected_schema['channels']['users']['publish']['message']['payload']
        )

    def tearDown(self):
        cleanup_test_data()
```

#### 3.1.2 组件集成测试

**测试组件**：

- **解析器**：测试Schema解析器
- **转换器**：测试转换器
- **验证器**：测试验证器

**示例**：

```python
def test_component_integration():
    """测试组件集成"""
    # 解析Schema
    parser = SchemaParser()
    parsed = parser.parse(openapi_schema)

    # 转换Schema
    converter = SchemaConverter()
    converted = converter.convert(parsed, 'AsyncAPI')

    # 验证Schema
    validator = SchemaValidator()
    is_valid = validator.validate(converted)

    assert is_valid
```

### 3.2 测试数据

#### 3.2.1 测试数据生成

**生成方法**：

- **手动创建**：手动创建测试数据
- **自动生成**：自动生成测试数据
- **真实数据**：使用真实数据（脱敏后）

**示例**：

```python
def generate_test_schema(schema_type='object', depth=3):
    """生成测试Schema"""
    if depth == 0:
        return {'type': 'string'}

    schema = {'type': schema_type}
    if schema_type == 'object':
        schema['properties'] = {
            f'field_{i}': generate_test_schema('string', depth-1)
            for i in range(3)
        }
    elif schema_type == 'array':
        schema['items'] = generate_test_schema('object', depth-1)

    return schema
```

#### 3.2.2 测试数据管理

**管理方法**：

- **版本控制**：使用版本控制管理测试数据
- **数据分类**：按类型分类管理测试数据
- **数据更新**：定期更新测试数据

---

## 4. 回归测试

### 4.1 测试方法

#### 4.1.1 回归测试策略

**策略类型**：

- **全量回归**：测试所有功能
- **选择性回归**：测试变更相关功能
- **冒烟测试**：快速验证核心功能

**示例**：

```python
class RegressionTestSuite:
    def __init__(self):
        self.test_cases = load_regression_cases()

    def run_full_regression(self):
        """运行全量回归测试"""
        results = []
        for case in self.test_cases:
            result = self.run_test_case(case)
            results.append(result)
        return results

    def run_selective_regression(self, changed_files):
        """运行选择性回归测试"""
        affected_cases = self.get_affected_cases(changed_files)
        results = []
        for case in affected_cases:
            result = self.run_test_case(case)
            results.append(result)
        return results
```

#### 4.1.2 测试用例维护

**维护方法**：

- **用例更新**：及时更新测试用例
- **用例清理**：清理过时测试用例
- **用例优化**：优化测试用例效率

### 4.2 自动化回归

#### 4.2.1 CI/CD集成

**集成方式**：

- **持续集成**：每次提交运行回归测试
- **持续部署**：通过测试后自动部署
- **测试报告**：生成测试报告

**示例**：

```yaml
# .github/workflows/regression.yml
name: Regression Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run regression tests
        run: |
          pytest tests/regression/ --junitxml=junit.xml
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: junit.xml
```

#### 4.2.2 测试结果分析

**分析方法**：

- **结果对比**：对比历史测试结果
- **趋势分析**：分析测试趋势
- **问题定位**：定位测试失败原因

---

## 5. 性能测试

### 5.1 测试方法

#### 5.1.1 基准测试

**测试指标**：

- **转换时间**：单次转换时间
- **吞吐量**：批量转换吞吐量
- **资源占用**：CPU、内存占用

**示例**：

```python
import time
import statistics

class PerformanceBenchmark:
    def benchmark_conversion(self, schemas, iterations=100):
        """性能基准测试"""
        times = []
        for _ in range(iterations):
            start = time.time()
            convert_schemas(schemas)
            end = time.time()
            times.append(end - start)

        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'std': statistics.stdev(times),
            'min': min(times),
            'max': max(times)
        }
```

#### 5.1.2 压力测试

**测试场景**：

- **高并发**：测试高并发转换
- **大数据量**：测试大数据量转换
- **长时间运行**：测试长时间运行稳定性

**示例**：

```python
import concurrent.futures

def stress_test(schemas, concurrent_users=100):
    """压力测试"""
    def convert_task():
        return convert_schemas(schemas)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(convert_task) for _ in range(concurrent_users)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    return results
```

### 5.2 性能分析

#### 5.2.1 性能分析工具

**工具推荐**：

- **cProfile**：Python性能分析
- **py-spy**：Python性能分析
- **memory_profiler**：内存分析

**示例**：

```python
import cProfile
import pstats

def profile_conversion(schemas):
    """性能分析"""
    profiler = cProfile.Profile()
    profiler.enable()

    convert_schemas(schemas)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # 打印前20个最耗时的函数
```

---

## 6. 安全测试

### 6.1 测试方法

#### 6.1.1 安全漏洞测试

**测试类型**：

- **注入攻击**：测试注入攻击防护
- **XSS攻击**：测试XSS攻击防护
- **CSRF攻击**：测试CSRF攻击防护

**示例**：

```python
def test_sql_injection():
    """测试SQL注入防护"""
    malicious_schema = {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'default': "'; DROP TABLE users; --"
            }
        }
    }

    # 应该安全处理，不执行SQL
    result = convert_schema(malicious_schema, 'SQL')
    assert 'DROP TABLE' not in result
```

#### 6.1.2 权限测试

**测试内容**：

- **访问控制**：测试访问控制
- **权限验证**：测试权限验证
- **越权访问**：测试越权访问防护

**示例**：

```python
def test_unauthorized_access():
    """测试未授权访问防护"""
    # 未认证用户
    response = client.post('/convert', json=schema_data)
    assert response.status_code == 401

    # 低权限用户访问高权限资源
    low_privilege_user = create_user(role='readonly')
    response = client.post('/convert',
                          json=schema_data,
                          headers={'Authorization': low_privilege_user.token})
    assert response.status_code == 403
```

### 6.2 安全扫描

#### 6.2.1 代码扫描

**扫描工具**：

- **Bandit**：Python安全扫描
- **Safety**：依赖安全检查
- **Semgrep**：代码安全扫描

**示例**：

```bash
# 使用Bandit扫描代码
bandit -r src/

# 使用Safety检查依赖
safety check

# 使用Semgrep扫描
semgrep --config=auto src/
```

#### 6.2.2 依赖扫描

**扫描内容**：

- **已知漏洞**：扫描已知安全漏洞
- **过期依赖**：检查过期依赖
- **许可证**：检查依赖许可证

---

## 7. 测试最佳实践

### 7.1 测试策略

#### 7.1.1 测试金字塔

**测试层次**：

- **单元测试**：70% - 快速、隔离
- **集成测试**：20% - 组件交互
- **端到端测试**：10% - 完整流程

#### 7.1.2 测试驱动开发（TDD）

**TDD流程**：

1. **编写测试**：先编写测试用例
2. **运行测试**：运行测试（应该失败）
3. **编写代码**：编写实现代码
4. **运行测试**：运行测试（应该通过）
5. **重构**：重构代码

### 7.2 测试维护

#### 7.2.1 测试文档

**文档内容**：

- **测试计划**：测试计划和策略
- **测试用例**：测试用例文档
- **测试报告**：测试结果报告

#### 7.2.2 测试自动化

**自动化内容**：

- **测试执行**：自动化测试执行
- **结果报告**：自动化结果报告
- **问题跟踪**：自动化问题跟踪

---

## 8. 总结

### 8.1 关键成果

1. **测试方法**：建立了完整的测试方法体系
2. **测试工具**：介绍了各种测试工具
3. **最佳实践**：总结了测试最佳实践
4. **自动化**：实现了测试自动化

### 8.2 测试建议

1. **全面覆盖**：确保测试全面覆盖
2. **持续测试**：持续进行测试
3. **及时修复**：及时修复测试发现的问题
4. **持续改进**：持续改进测试方法

---

## 9. 测试验证综合应用实际示例

**示例：实现Schema转换测试框架**

```python
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod

@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    passed: bool
    duration_ms: float
    message: str
    details: Optional[Dict] = None

@dataclass
class TestSuite:
    """测试套件"""
    name: str
    tests: List[TestResult]
    total_duration_ms: float

    @property
    def passed_count(self) -> int:
        return sum(1 for t in self.tests if t.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for t in self.tests if not t.passed)

    @property
    def pass_rate(self) -> float:
        return self.passed_count / len(self.tests) if self.tests else 0

class SchemaTransformationTestFramework:
    """Schema转换测试框架"""

    def __init__(self):
        self.test_suites = []
        self.assertions = TestAssertions()

    # ===== 单元测试（基于第2章）=====
    def run_unit_tests(self, transformer_func: Callable, test_cases: List[Dict]) -> TestSuite:
        """运行单元测试"""
        results = []
        start_time = time.time()

        for case in test_cases:
            test_start = time.time()
            try:
                result = transformer_func(case['input'])

                if case.get('expected_output'):
                    passed = self.assertions.assert_equal(result, case['expected_output'])
                    message = '输出匹配' if passed else '输出不匹配'
                elif case.get('expected_error'):
                    passed = False
                    message = '预期异常但执行成功'
                else:
                    passed = result is not None
                    message = '转换成功' if passed else '转换失败'

                results.append(TestResult(
                    test_name=case.get('name', 'unnamed'),
                    passed=passed,
                    duration_ms=(time.time() - test_start) * 1000,
                    message=message,
                    details={'input': case['input'], 'output': result}
                ))
            except Exception as e:
                expected_error = case.get('expected_error')
                if expected_error and expected_error in str(e):
                    passed = True
                    message = f'预期异常已捕获: {str(e)}'
                else:
                    passed = False
                    message = f'未预期异常: {str(e)}'

                results.append(TestResult(
                    test_name=case.get('name', 'unnamed'),
                    passed=passed,
                    duration_ms=(time.time() - test_start) * 1000,
                    message=message
                ))

        suite = TestSuite(
            name='单元测试套件',
            tests=results,
            total_duration_ms=(time.time() - start_time) * 1000
        )
        self.test_suites.append(suite)
        return suite

    # ===== 集成测试（基于第3章）=====
    def run_integration_tests(self, transformation_pipeline: List[Callable],
                              test_data: Dict) -> TestSuite:
        """运行集成测试"""
        results = []
        start_time = time.time()

        # 端到端测试
        e2e_result = self._run_e2e_test(transformation_pipeline, test_data)
        results.append(e2e_result)

        # 组件集成测试
        for i, transformer in enumerate(transformation_pipeline):
            component_result = self._run_component_test(transformer, test_data, i)
            results.append(component_result)

        suite = TestSuite(
            name='集成测试套件',
            tests=results,
            total_duration_ms=(time.time() - start_time) * 1000
        )
        self.test_suites.append(suite)
        return suite

    # ===== 回归测试（基于第4章）=====
    def run_regression_tests(self, transformer_func: Callable,
                             baseline_results: Dict[str, Any]) -> TestSuite:
        """运行回归测试"""
        results = []
        start_time = time.time()

        for test_name, baseline in baseline_results.items():
            test_start = time.time()
            try:
                current_result = transformer_func(baseline['input'])
                passed = self.assertions.assert_equal(current_result, baseline['expected'])
                message = '结果与基线一致' if passed else '结果与基线不一致'
            except Exception as e:
                passed = False
                message = f'执行异常: {str(e)}'

            results.append(TestResult(
                test_name=f'回归_{test_name}',
                passed=passed,
                duration_ms=(time.time() - test_start) * 1000,
                message=message
            ))

        suite = TestSuite(
            name='回归测试套件',
            tests=results,
            total_duration_ms=(time.time() - start_time) * 1000
        )
        self.test_suites.append(suite)
        return suite

    # ===== 性能测试（基于第5章）=====
    def run_performance_tests(self, transformer_func: Callable,
                              test_input: Dict,
                              iterations: int = 100,
                              target_ms: float = 100) -> TestSuite:
        """运行性能测试"""
        results = []

        # 基准测试
        durations = []
        for _ in range(iterations):
            start = time.time()
            transformer_func(test_input)
            durations.append((time.time() - start) * 1000)

        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)

        # 基准测试结果
        benchmark_passed = avg_duration < target_ms
        results.append(TestResult(
            test_name='基准测试',
            passed=benchmark_passed,
            duration_ms=avg_duration,
            message=f'平均耗时 {avg_duration:.2f}ms（目标: <{target_ms}ms）',
            details={
                'iterations': iterations,
                'avg_ms': avg_duration,
                'max_ms': max_duration,
                'min_ms': min_duration
            }
        ))

        # 压力测试
        stress_start = time.time()
        success_count = 0
        for _ in range(iterations * 10):
            try:
                transformer_func(test_input)
                success_count += 1
            except Exception:
                pass
        stress_duration = (time.time() - stress_start) * 1000

        stress_passed = success_count == iterations * 10
        results.append(TestResult(
            test_name='压力测试',
            passed=stress_passed,
            duration_ms=stress_duration,
            message=f'成功率 {success_count}/{iterations * 10}',
            details={'success_count': success_count, 'total': iterations * 10}
        ))

        suite = TestSuite(
            name='性能测试套件',
            tests=results,
            total_duration_ms=sum(r.duration_ms for r in results)
        )
        self.test_suites.append(suite)
        return suite

    # ===== 安全测试（基于第6章）=====
    def run_security_tests(self, transformer_func: Callable,
                           security_test_cases: List[Dict]) -> TestSuite:
        """运行安全测试"""
        results = []
        start_time = time.time()

        for case in security_test_cases:
            test_start = time.time()
            test_type = case.get('type', 'unknown')

            try:
                if test_type == 'injection':
                    # 注入攻击测试
                    result = transformer_func(case['malicious_input'])
                    passed = case.get('should_reject', True) == (result is None)
                    message = '注入攻击被拦截' if passed else '注入攻击未被拦截'

                elif test_type == 'overflow':
                    # 溢出测试
                    result = transformer_func(case['large_input'])
                    passed = result is not None
                    message = '处理大输入成功' if passed else '大输入处理失败'

                elif test_type == 'permission':
                    # 权限测试
                    result = transformer_func(case['input'])
                    passed = case.get('expected_access', True) == (result is not None)
                    message = '权限检查正确' if passed else '权限检查错误'
                else:
                    passed = False
                    message = f'未知测试类型: {test_type}'

            except Exception as e:
                passed = case.get('should_raise', False)
                message = f'异常: {str(e)}'

            results.append(TestResult(
                test_name=case.get('name', f'security_{test_type}'),
                passed=passed,
                duration_ms=(time.time() - test_start) * 1000,
                message=message
            ))

        suite = TestSuite(
            name='安全测试套件',
            tests=results,
            total_duration_ms=(time.time() - start_time) * 1000
        )
        self.test_suites.append(suite)
        return suite

    def generate_test_report(self) -> Dict:
        """生成测试报告"""
        total_tests = sum(len(suite.tests) for suite in self.test_suites)
        total_passed = sum(suite.passed_count for suite in self.test_suites)
        total_duration = sum(suite.total_duration_ms for suite in self.test_suites)

        return {
            'summary': {
                'total_suites': len(self.test_suites),
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_tests - total_passed,
                'pass_rate': total_passed / total_tests if total_tests > 0 else 0,
                'total_duration_ms': total_duration
            },
            'suites': [
                {
                    'name': suite.name,
                    'tests': len(suite.tests),
                    'passed': suite.passed_count,
                    'failed': suite.failed_count,
                    'pass_rate': suite.pass_rate,
                    'duration_ms': suite.total_duration_ms,
                    'results': [
                        {
                            'name': r.test_name,
                            'passed': r.passed,
                            'duration_ms': r.duration_ms,
                            'message': r.message
                        }
                        for r in suite.tests
                    ]
                }
                for suite in self.test_suites
            ]
        }

    def _run_e2e_test(self, pipeline: List[Callable], test_data: Dict) -> TestResult:
        """端到端测试"""
        start = time.time()
        try:
            result = test_data
            for transformer in pipeline:
                result = transformer(result)
            return TestResult(
                test_name='端到端测试',
                passed=result is not None,
                duration_ms=(time.time() - start) * 1000,
                message='管道执行成功'
            )
        except Exception as e:
            return TestResult(
                test_name='端到端测试',
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                message=f'管道执行失败: {str(e)}'
            )

    def _run_component_test(self, transformer: Callable, test_data: Dict, index: int) -> TestResult:
        """组件测试"""
        start = time.time()
        try:
            result = transformer(test_data)
            return TestResult(
                test_name=f'组件_{index}_测试',
                passed=result is not None,
                duration_ms=(time.time() - start) * 1000,
                message='组件执行成功'
            )
        except Exception as e:
            return TestResult(
                test_name=f'组件_{index}_测试',
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                message=f'组件执行失败: {str(e)}'
            )

class TestAssertions:
    """测试断言工具"""

    def assert_equal(self, actual: Any, expected: Any) -> bool:
        """相等断言"""
        return actual == expected

    def assert_not_none(self, value: Any) -> bool:
        """非空断言"""
        return value is not None

    def assert_contains(self, container: Any, item: Any) -> bool:
        """包含断言"""
        return item in container

    def assert_type(self, value: Any, expected_type: type) -> bool:
        """类型断言"""
        return isinstance(value, expected_type)

# 实际应用示例
# 模拟转换函数
def simple_transformer(schema: Dict) -> Dict:
    return {'transformed': True, 'original': schema}

def validate_transformer(schema: Dict) -> Dict:
    if not isinstance(schema, dict):
        raise ValueError('Invalid schema type')
    return schema

# 创建测试框架
framework = SchemaTransformationTestFramework()

# 示例1：单元测试
print("=== 示例1：单元测试 ===")
unit_test_cases = [
    {'name': 'basic_transform', 'input': {'type': 'object'},
     'expected_output': {'transformed': True, 'original': {'type': 'object'}}},
    {'name': 'empty_schema', 'input': {},
     'expected_output': {'transformed': True, 'original': {}}}
]
unit_suite = framework.run_unit_tests(simple_transformer, unit_test_cases)
print(f"通过率: {unit_suite.pass_rate:.0%}")

# 示例2：集成测试
print("\n=== 示例2：集成测试 ===")
pipeline = [validate_transformer, simple_transformer]
integration_suite = framework.run_integration_tests(pipeline, {'type': 'string'})
print(f"通过率: {integration_suite.pass_rate:.0%}")

# 示例3：性能测试
print("\n=== 示例3：性能测试 ===")
perf_suite = framework.run_performance_tests(
    simple_transformer, {'type': 'object'}, iterations=50, target_ms=10
)
print(f"通过率: {perf_suite.pass_rate:.0%}")

# 示例4：生成测试报告
print("\n=== 测试报告 ===")
report = framework.generate_test_report()
print(f"总测试数: {report['summary']['total_tests']}")
print(f"通过数: {report['summary']['passed']}")
print(f"总体通过率: {report['summary']['pass_rate']:.0%}")
print(f"总耗时: {report['summary']['total_duration_ms']:.2f}ms")
```

---

## 10. 相关文档

### 模式文档 ⭐新增

- `docs/structure/DESIGN_PATTERNS_SUMMARY.md`：设计模式总结（15个模式）
  - 在测试框架设计中，可以参考工厂模式、策略模式、模板方法模式等
- `docs/structure/ARCHITECTURE_PATTERNS_SUMMARY.md`：架构模式总结（12个模式）
  - 在测试系统架构设计中，可以参考分层架构、微服务架构等模式
- `docs/structure/INFORMATION_PROCESSING_PATTERNS_SUMMARY.md`：信息处理模式总结（12个模式）
  - 在测试数据处理中，可以参考批处理模式、实时处理模式等
- `docs/structure/PATTERNS_QUICK_REFERENCE.md`：模式快速参考指南 ⭐推荐

### 其他实践文档

- `practices/09_Performance_Optimization.md`：性能优化指南
- `practices/10_Security_Considerations.md`：安全考虑指南
- `practices/12_Real_World_Case_Studies.md`：实际应用案例研究

---

## 📝 版本历史

### v1.2 (2025-01-21) - 实际应用示例增强版

- ✅ 扩展第9章：为测试验证添加综合应用实际示例（包含Schema转换测试框架实现、单元测试、集成测试、回归测试、性能测试、安全测试、测试报告生成）
- ✅ 添加版本历史章节
- ✅ 更新文档版本号至v1.2

### v1.1 (2025-01-27) - 初始版本

- ✅ 创建文档：测试与验证方法
- ✅ 添加单元测试章节
- ✅ 添加集成测试章节
- ✅ 添加回归测试章节
- ✅ 添加性能测试章节
- ✅ 添加安全测试章节
- ✅ 添加测试最佳实践章节

---

**文档版本**：1.2（实际应用示例增强版）
**最后更新**：2025-01-27
**维护者**：DSL Schema研究团队
