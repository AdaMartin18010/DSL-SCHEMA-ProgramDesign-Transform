"""
Schema深化模块异常类

定义所有自定义异常类型
"""


class SchemaDeepeningError(Exception):
    """Schema深化模块基础异常"""
    pass


class ConversionError(SchemaDeepeningError):
    """转换错误"""
    pass


class DeviceNotFoundError(SchemaDeepeningError):
    """设备未找到错误"""
    pass


class SceneNotFoundError(SchemaDeepeningError):
    """场景未找到错误"""
    pass


class StorageError(SchemaDeepeningError):
    """存储错误"""
    pass


class ValidationError(SchemaDeepeningError):
    """验证错误"""
    pass


class ProcessingError(SchemaDeepeningError):
    """处理错误"""
    pass


class ParseError(SchemaDeepeningError):
    """解析错误"""
    pass
