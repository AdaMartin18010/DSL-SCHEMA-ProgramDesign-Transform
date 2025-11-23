# Schema错误处理和边界情况处理增强指南

## 📋 概述

本文档总结了为所有Schema添加的错误处理和边界情况处理增强措施。

## 🎯 增强目标

1. **输入验证**：所有方法都进行输入参数验证
2. **类型检查**：验证参数类型，防止类型错误
3. **边界检查**：检查数值范围、字符串长度等边界情况
4. **资源管理**：确保资源（连接、文件句柄等）正确释放
5. **错误分类**：区分不同类型的错误（ValueError、TypeError、ConnectionError等）
6. **详细日志**：记录详细的错误信息，便于调试

## 📝 增强模式

### 1. 输入验证模式

```python
def method_name(self, param: str) -> Dict:
    """方法描述 - 增强错误处理"""
    # 输入验证
    if not param:
        raise ValueError("Parameter cannot be empty")

    if not isinstance(param, str):
        raise TypeError(f"Parameter must be a string, got {type(param)}")

    # 边界检查
    if len(param) > MAX_LENGTH:
        raise ValueError(f"Parameter too long: {len(param)} (max {MAX_LENGTH})")

    try:
        # 实际逻辑
        result = do_something(param)
        return result
    except SpecificError as e:
        logger.error(f"Specific error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise RuntimeError(f"Operation failed: {e}") from e
```

### 2. 连接管理模式

```python
def connect(self, host: str, port: int, timeout: float = 10.0) -> bool:
    """连接方法 - 增强错误处理"""
    # 输入验证
    if not host:
        raise ValueError("Host cannot be empty")

    if not (1 <= port <= 65535):
        raise ValueError(f"Port must be between 1 and 65535, got {port}")

    if timeout <= 0:
        raise ValueError(f"Timeout must be positive, got {timeout}")

    # 如果已连接，先断开
    if self.connected:
        try:
            self.disconnect()
        except Exception as e:
            logger.warning(f"Error disconnecting: {e}")

    try:
        # 连接逻辑
        self.socket = socket.socket(...)
        self.socket.settimeout(timeout)
        self.socket.connect((host, port))
        self.connected = True
        return True
    except socket.timeout:
        self._cleanup_socket()
        raise TimeoutError(f"Connection timeout") from None
    except socket.error as e:
        self._cleanup_socket()
        raise ConnectionError(f"Cannot connect: {e}") from e
    except Exception as e:
        self._cleanup_socket()
        raise RuntimeError(f"Connection failed: {e}") from e

def _cleanup_socket(self):
    """清理资源"""
    if self.socket:
        try:
            self.socket.close()
        except Exception:
            pass
        finally:
            self.socket = None
            self.connected = False
```

### 3. 文件操作模式

```python
def parse_file(self, file_path: str) -> Dict:
    """解析文件 - 增强错误处理"""
    # 输入验证
    if not file_path:
        raise ValueError("File path cannot be empty")

    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not os.path.isfile(file_path):
        raise ValueError(f"Path is not a file: {file_path}")

    # 文件大小检查
    file_size = os.path.getsize(file_path)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size} bytes")

    try:
        # 解析逻辑
        with open(file_path, 'r') as f:
            content = f.read()
        return parse_content(content)
    except PermissionError as e:
        raise PermissionError(f"Cannot read file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to parse file: {e}") from e
```

### 4. 数据验证模式

```python
def validate_data(self, data: Dict) -> bool:
    """验证数据 - 增强错误处理"""
    if not isinstance(data, dict):
        raise TypeError(f"Data must be a dictionary, got {type(data)}")

    # 必需字段检查
    required_fields = ["field1", "field2"]
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    # 数值范围检查
    value = data.get("value")
    if value is not None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Value must be a number, got {type(value)}")
        if not (MIN_VALUE <= value <= MAX_VALUE):
            raise ValueError(f"Value out of range: {value}")

    # 字符串格式检查
    code = data.get("code")
    if code and not re.match(r'^[A-Z0-9]+$', code):
        raise ValueError(f"Invalid code format: {code}")

    return True
```

## ✅ 已增强的Schema

### P2优先级Schema

1. **Smart_Home_Schema**
   - Matter SDK集成：添加连接超时、重试机制
   - 场景联动：添加条件验证、执行状态检查
   - PostgreSQL存储：添加事务回滚、连接池管理

2. **Thread_Schema**
   - 网络管理：添加节点验证、网络状态检查
   - 路由算法：添加路由表验证、循环检测
   - PostgreSQL存储：添加并发控制、死锁处理

3. **Matter_Schema**
   - 设备控制：添加设备状态验证、命令超时处理
   - 集群操作：添加属性范围检查、命令参数验证
   - PostgreSQL存储：添加外键约束检查

4. **OA_Schema**
   - 文档转换：添加文件格式验证、大小限制
   - BPMN引擎：添加流程定义验证、节点可达性检查
   - PostgreSQL存储：添加全文索引错误处理

5. **Maritime_Schema**
   - EDIFACT解析：添加消息格式验证、段计数检查
   - AIS集成：添加消息类型验证、数据范围检查
   - 航线优化：添加坐标验证、路径有效性检查

6. **Food_Industry_Schema**
   - EPCIS处理：添加事件类型验证、EPC格式检查
   - 追溯链查询：添加循环检测、路径验证
   - 质量监控：添加规则验证、阈值检查

### P1优先级Schema

7. **GS1_Schema**
   - EPCIS实现：添加XML格式验证、事件完整性检查
   - 追溯链查询：添加EPC格式验证、路径循环检测

8. **EDI_Schema**
   - X12解析：添加交换控制号验证、段计数检查
   - EDIFACT解析：添加消息头尾验证、段顺序检查

9. **Smart_City_Schema**
   - IoT数据聚合：添加数据有效性检查、时间窗口验证
   - 城市数据分析：添加数据范围检查、统计计算验证

10. **Healthcare_Schema**
    - HL7/FHIR转换：添加消息格式验证、资源完整性检查
    - 医疗数据分析：添加患者ID验证、日期范围检查

### 新增领域Schema

11. **IEC61850_Schema** ✅ 已增强
    - SCL解析：添加文件大小检查、XML格式验证、命名空间验证
    - MMS客户端：添加连接超时、DNS解析错误处理、socket错误分类
    - GetDirectory：添加对象名称格式验证、响应验证

12. **MES_Schema** ✅ 已增强
    - ERP订单解析：添加必需字段验证、数量范围检查、日期逻辑验证
    - 日期解析：添加多种格式支持、格式验证
    - ERP到MES转换：添加订单ID验证、产品ID验证、数量验证

## 🔧 通用错误处理工具类

```python
class SchemaErrorHandler:
    """Schema错误处理工具类"""

    @staticmethod
    def validate_string(value: Any, field_name: str, max_length: Optional[int] = None) -> str:
        """验证字符串参数"""
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string, got {type(value)}")
        if not value.strip():
            raise ValueError(f"{field_name} cannot be empty")
        if max_length and len(value) > max_length:
            raise ValueError(f"{field_name} too long: {len(value)} (max {max_length})")
        return value

    @staticmethod
    def validate_number(value: Any, field_name: str, min_val: Optional[float] = None,
                       max_val: Optional[float] = None) -> float:
        """验证数值参数"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number, got {type(value)}")
        if min_val is not None and value < min_val:
            raise ValueError(f"{field_name} must be >= {min_val}, got {value}")
        if max_val is not None and value > max_val:
            raise ValueError(f"{field_name} must be <= {max_val}, got {value}")
        return float(value)

    @staticmethod
    def validate_dict(value: Any, field_name: str, required_keys: Optional[List[str]] = None) -> Dict:
        """验证字典参数"""
        if not isinstance(value, dict):
            raise TypeError(f"{field_name} must be a dictionary, got {type(value)}")
        if required_keys:
            missing = [k for k in required_keys if k not in value]
            if missing:
                raise ValueError(f"{field_name} missing required keys: {', '.join(missing)}")
        return value
```

## 📊 错误处理统计

- **已增强方法数**：100+个方法
- **输入验证**：所有公共方法都添加了输入验证
- **错误分类**：区分了ValueError、TypeError、ConnectionError、TimeoutError等
- **资源管理**：所有连接和文件操作都添加了资源清理
- **日志记录**：所有错误都添加了详细的日志记录

## 🎯 最佳实践

1. **始终验证输入**：每个公共方法都应该验证输入参数
2. **使用具体异常**：使用具体的异常类型（ValueError、TypeError等）而不是通用的Exception
3. **提供有用信息**：错误消息应该包含有用的调试信息
4. **资源清理**：确保在异常情况下也能正确清理资源
5. **日志记录**：记录所有错误，包括堆栈跟踪
6. **边界检查**：检查所有边界情况（空值、范围、格式等）

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**状态**：持续更新中
