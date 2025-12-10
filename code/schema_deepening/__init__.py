"""
Schema深化模块

专注于Smart_Home、OA、Maritime、Food_Industry等Schema的深化实现
"""

from .smart_home_converter import (
    SmartHomeConverter,
    DeviceProtocol,
    DeviceType
)
from .oa_converter import (
    OAConverter,
    DocumentFormat,
    DocumentType
)
from .maritime_converter import (
    MaritimeConverter,
    EDIFACTMessageType,
    AISMessageType
)
from .food_industry_converter import (
    FoodIndustryConverter,
    EPCISEventType,
    TraceDirection
)
from .bpmn_processor import (
    BPMNProcessor,
    TaskStatus,
    ProcessStatus
)
from .epcis_processor import (
    EPCISProcessor
)
from .edifact_parser import (
    EDIFACTParser,
    EDIFACTMessageType
)
from .ais_processor import (
    AISProcessor,
    AISMessageType
)
from .exceptions import (
    SchemaDeepeningError,
    ConversionError,
    DeviceNotFoundError,
    SceneNotFoundError,
    StorageError,
    ValidationError,
    ProcessingError,
    ParseError
)
from .logger import logger, setup_logger
from .utils import (
    validate_uuid,
    validate_email,
    parse_datetime,
    safe_json_loads,
    safe_json_dumps,
    normalize_path,
    ensure_directory,
    format_file_size,
    truncate_string,
    deep_merge_dict,
    get_nested_value,
    set_nested_value,
    chunk_list,
    remove_none_values,
    calculate_percentage,
    generate_id,
    is_valid_url
)

__all__ = [
    # Smart Home转换器
    'SmartHomeConverter',
    'DeviceProtocol',
    'DeviceType',
    # OA转换器
    'OAConverter',
    'DocumentFormat',
    'DocumentType',
    # Maritime转换器
    'MaritimeConverter',
    'EDIFACTMessageType',
    'AISMessageType',
    # Food Industry转换器
    'FoodIndustryConverter',
    'EPCISEventType',
    'TraceDirection',
    # BPMN处理器
    'BPMNProcessor',
    'TaskStatus',
    'ProcessStatus',
    # EPCIS处理器
    'EPCISProcessor',
    # EDIFACT解析器
    'EDIFACTParser',
    'EDIFACTMessageType',
    # AIS处理器
    'AISProcessor',
    'AISMessageType',
    # 异常类
    'SchemaDeepeningError',
    'ConversionError',
    'DeviceNotFoundError',
    'SceneNotFoundError',
    'StorageError',
    'ValidationError',
    'ProcessingError',
    'ParseError',
    # 日志工具
    'logger',
    'setup_logger',
    # 工具函数
    'validate_uuid',
    'validate_email',
    'parse_datetime',
    'safe_json_loads',
    'safe_json_dumps',
    'normalize_path',
    'ensure_directory',
    'format_file_size',
    'truncate_string',
    'deep_merge_dict',
    'get_nested_value',
    'set_nested_value',
    'chunk_list',
    'remove_none_values',
    'calculate_percentage',
    'generate_id',
    'is_valid_url'
]
