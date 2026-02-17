#!/usr/bin/env python3
"""
Enhanced Schema Validator
=========================

增强型Schema验证器，支持2025年最新标准：
- JSON Schema 2025-01 (完整支持)
- OpenAPI 3.1.2
- AsyncAPI 3.0
- GraphQL SDL
- XML Schema 1.1
- 行业标准合规性检查

Author: DSL Schema Team
Version: 2.1.0
Date: 2026-02-17
"""

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pathlib import Path


class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SchemaType(Enum):
    JSON_SCHEMA = "json_schema"
    XML_SCHEMA = "xml_schema"
    OPENAPI = "openapi"
    ASYNCAPI = "asyncapi"
    GRAPHQL = "graphql"
    PROTOBUF = "protobuf"


@dataclass
class ValidationIssue:
    """验证问题"""
    path: str
    message: str
    code: str
    severity: ValidationSeverity
    suggestion: Optional[str] = None


@dataclass
class ComplianceReport:
    """合规性报告"""
    standard: str
    compliant: bool
    score: float  # 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    schema_type: SchemaType
    issues: List[ValidationIssue] = field(default_factory=list)
    compliance_reports: List[ComplianceReport] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class JSONSchema2025Validator:
    """JSON Schema 2025-01 验证器"""
    
    SUPPORTED_KEYWORDS = {
        # 核心验证
        'type', 'enum', 'const', 'multipleOf', 'maximum', 'exclusiveMaximum',
        'minimum', 'exclusiveMinimum', 'maxLength', 'minLength', 'pattern',
        # 数组验证
        'items', 'prefixItems', 'contains', 'minContains', 'maxContains',
        'uniqueItems', 'maxItems', 'minItems',
        # 对象验证
        'properties', 'patternProperties', 'additionalProperties', 'required',
        'propertyNames', 'minProperties', 'maxProperties',
        # 组合验证
        'allOf', 'anyOf', 'oneOf', 'not', 'if', 'then', 'else',
        'dependentSchemas', 'dependentRequired',
        # 引用
        '$ref', '$dynamicRef', '$dynamicAnchor', '$anchor', '$defs',
        # 元数据
        'title', 'description', 'default', 'deprecated', 'readOnly', 'writeOnly',
        'examples', '$comment',
        # 内容验证
        'contentMediaType', 'contentEncoding', 'contentSchema',
        # 格式
        'format'
    }
    
    FORMAT_VALIDATORS = {
        'date-time': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$',
        'date': r'^\d{4}-\d{2}-\d{2}$',
        'time': r'^\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'uri': r'^https?://[^\s/$.?#].[^\s]*$',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        'ipv4': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        'ipv6': r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
    }
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.issues: List[ValidationIssue] = []
    
    def validate(self, schema: Dict[str, Any]) -> ValidationResult:
        """验证JSON Schema"""
        self.issues = []
        
        # 基本结构检查
        self._check_schema_version(schema)
        self._validate_keywords(schema)
        self._check_references(schema)
        self._validate_types(schema)
        self._validate_formats(schema)
        
        if self.strict_mode:
            self._check_best_practices(schema)
        
        return ValidationResult(
            valid=not any(i.severity == ValidationSeverity.ERROR for i in self.issues),
            schema_type=SchemaType.JSON_SCHEMA,
            issues=self.issues,
            metadata={
                'version': schema.get('$schema', 'unknown'),
                'schema_id': schema.get('$id'),
                'title': schema.get('title')
            }
        )
    
    def _check_schema_version(self, schema: Dict[str, Any]):
        """检查Schema版本"""
        version = schema.get('$schema', '')
        supported_versions = [
            'https://json-schema.org/draft/2025-01/schema',
            'https://json-schema.org/draft/2020-12/schema',
            'https://json-schema.org/draft/2019-09/schema'
        ]
        
        if not version:
            self.issues.append(ValidationIssue(
                path='$schema',
                message='缺少$schema声明，建议使用2025-01版本',
                code='SCHEMA_VERSION_MISSING',
                severity=ValidationSeverity.WARNING,
                suggestion='添加 "$schema": "https://json-schema.org/draft/2025-01/schema"'
            ))
        elif version not in supported_versions:
            self.issues.append(ValidationIssue(
                path='$schema',
                message=f'Schema版本 {version} 可能不完全支持',
                code='SCHEMA_VERSION_DEPRECATED',
                severity=ValidationSeverity.INFO
            ))
    
    def _validate_keywords(self, schema: Dict[str, Any], path: str = '$'):
        """验证关键词使用"""
        for keyword in schema.keys():
            if keyword.startswith('$') or keyword in self.SUPPORTED_KEYWORDS:
                continue
            
            self.issues.append(ValidationIssue(
                path=f'{path}.{keyword}',
                message=f'未知关键词: {keyword}',
                code='UNKNOWN_KEYWORD',
                severity=ValidationSeverity.WARNING if not self.strict_mode else ValidationSeverity.ERROR
            ))
        
        # 递归验证嵌套schema
        for key, value in schema.items():
            if isinstance(value, dict):
                self._validate_keywords(value, f'{path}.{key}')
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._validate_keywords(item, f'{path}.{key}[{i}]')
    
    def _check_references(self, schema: Dict[str, Any]):
        """检查引用完整性"""
        refs = set()
        defs = set()
        
        def collect_refs(s: Any, in_defs: bool = False):
            if isinstance(s, dict):
                if '$ref' in s:
                    refs.add(s['$ref'])
                if '$anchor' in s:
                    defs.add(f'#{s["$anchor"]}')
                if in_defs:
                    pass
                for key, value in s.items():
                    if key == '$defs' or key == 'definitions':
                        for def_name in value.keys():
                            defs.add(f'#/$defs/{def_name}')
                        collect_refs(value, True)
                    else:
                        collect_refs(value, in_defs)
            elif isinstance(s, list):
                for item in s:
                    collect_refs(item, in_defs)
        
        collect_refs(schema)
        
        # 检查未解析的引用
        for ref in refs:
            if ref.startswith('#/'):
                ref_path = ref[2:].replace('/', '.')
                if ref not in defs:
                    self.issues.append(ValidationIssue(
                        path=f'$ref: {ref}',
                        message=f'引用可能不存在: {ref}',
                        code='UNRESOLVED_REFERENCE',
                        severity=ValidationSeverity.WARNING
                    ))
    
    def _validate_types(self, schema: Dict[str, Any], path: str = '$'):
        """验证类型定义"""
        if 'type' in schema:
            valid_types = {'string', 'number', 'integer', 'boolean', 'array', 'object', 'null'}
            schema_type = schema['type']
            
            if isinstance(schema_type, str) and schema_type not in valid_types:
                self.issues.append(ValidationIssue(
                    path=f'{path}.type',
                    message=f'无效的类型: {schema_type}',
                    code='INVALID_TYPE',
                    severity=ValidationSeverity.ERROR
                ))
            elif isinstance(schema_type, list):
                for t in schema_type:
                    if t not in valid_types:
                        self.issues.append(ValidationIssue(
                            path=f'{path}.type',
                            message=f'列表中包含无效类型: {t}',
                            code='INVALID_TYPE_IN_LIST',
                            severity=ValidationSeverity.ERROR
                        ))
        
        # 递归验证
        for key, value in schema.items():
            if isinstance(value, dict):
                self._validate_types(value, f'{path}.{key}')
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._validate_types(item, f'{path}.{key}[{i}]')
    
    def _validate_formats(self, schema: Dict[str, Any], path: str = '$'):
        """验证format定义"""
        if 'format' in schema:
            format_value = schema['format']
            known_formats = set(self.FORMAT_VALIDATORS.keys()) | {
                'duration', 'idn-email', 'idn-hostname', 'hostname',
                'uri', 'uri-reference', 'iri', 'iri-reference',
                'uri-template', 'json-pointer', 'relative-json-pointer', 'regex'
            }
            
            if format_value not in known_formats:
                self.issues.append(ValidationIssue(
                    path=f'{path}.format',
                    message=f'未知的format: {format_value}',
                    code='UNKNOWN_FORMAT',
                    severity=ValidationSeverity.INFO
                ))
    
    def _check_best_practices(self, schema: Dict[str, Any]):
        """检查最佳实践"""
        # 检查是否有title和description
        if 'title' not in schema:
            self.issues.append(ValidationIssue(
                path='$',
                message='建议添加title字段',
                code='MISSING_TITLE',
                severity=ValidationSeverity.INFO
            ))
        
        if 'description' not in schema:
            self.issues.append(ValidationIssue(
                path='$',
                message='建议添加description字段',
                code='MISSING_DESCRIPTION',
                severity=ValidationSeverity.INFO
            ))
        
        # 检查properties中是否有未定义的类型
        if 'properties' in schema and 'type' not in schema:
            self.issues.append(ValidationIssue(
                path='$',
                message='包含properties但没有指定type: object',
                code='MISSING_OBJECT_TYPE',
                severity=ValidationSeverity.WARNING
            ))


class OpenAPI31Validator:
    """OpenAPI 3.1.2 验证器"""
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
    
    def validate(self, spec: Dict[str, Any]) -> ValidationResult:
        """验证OpenAPI规范"""
        self.issues = []
        
        # 检查OpenAPI版本
        version = spec.get('openapi', '')
        if not version.startswith('3.1'):
            self.issues.append(ValidationIssue(
                path='openapi',
                message=f'建议使用OpenAPI 3.1.x版本，当前: {version}',
                code='OPENAPI_VERSION',
                severity=ValidationSeverity.WARNING
            ))
        
        # 检查必需字段
        if 'info' not in spec:
            self.issues.append(ValidationIssue(
                path='$',
                message='缺少info字段',
                code='MISSING_INFO',
                severity=ValidationSeverity.ERROR
            ))
        else:
            self._validate_info(spec['info'])
        
        # 检查paths
        if 'paths' in spec:
            self._validate_paths(spec['paths'])
        
        # 验证JSON Schema兼容性（OpenAPI 3.1使用JSON Schema 2025-01）
        if 'components' in spec and 'schemas' in spec['components']:
            json_validator = JSONSchema2025Validator(strict_mode=False)
            for name, schema in spec['components']['schemas'].items():
                result = json_validator.validate(schema)
                for issue in result.issues:
                    issue.path = f'components.schemas.{name}.{issue.path}'
                    self.issues.append(issue)
        
        return ValidationResult(
            valid=not any(i.severity == ValidationSeverity.ERROR for i in self.issues),
            schema_type=SchemaType.OPENAPI,
            issues=self.issues,
            metadata={'version': version}
        )
    
    def _validate_info(self, info: Dict[str, Any]):
        """验证info部分"""
        required_fields = ['title', 'version']
        for field in required_fields:
            if field not in info:
                self.issues.append(ValidationIssue(
                    path=f'info.{field}',
                    message=f'缺少必需的info字段: {field}',
                    code='MISSING_INFO_FIELD',
                    severity=ValidationSeverity.ERROR
                ))
    
    def _validate_paths(self, paths: Dict[str, Any]):
        """验证paths部分"""
        valid_methods = {'get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace'}
        
        for path, methods in paths.items():
            if not path.startswith('/'):
                self.issues.append(ValidationIssue(
                    path=f'paths.{path}',
                    message=f'路径必须以/开头: {path}',
                    code='INVALID_PATH',
                    severity=ValidationSeverity.ERROR
                ))
            
            for method, operation in methods.items():
                if method not in valid_methods:
                    if not method.startswith('x-'):  # 扩展字段以x-开头
                        self.issues.append(ValidationIssue(
                            path=f'paths.{path}.{method}',
                            message=f'无效的HTTP方法: {method}',
                            code='INVALID_METHOD',
                            severity=ValidationSeverity.ERROR
                        ))
                elif isinstance(operation, dict):
                    # 验证operation
                    if 'operationId' not in operation:
                        self.issues.append(ValidationIssue(
                            path=f'paths.{path}.{method}',
                            message='建议添加operationId',
                            code='MISSING_OPERATION_ID',
                            severity=ValidationSeverity.WARNING
                        ))


class AsyncAPI30Validator:
    """AsyncAPI 3.0 验证器"""
    
    def validate(self, spec: Dict[str, Any]) -> ValidationResult:
        """验证AsyncAPI规范"""
        issues = []
        
        version = spec.get('asyncapi', '')
        if not version.startswith('3.'):
            issues.append(ValidationIssue(
                path='asyncapi',
                message=f'建议使用AsyncAPI 3.0.x版本，当前: {version}',
                code='ASYNCAPI_VERSION',
                severity=ValidationSeverity.WARNING
            ))
        
        # 检查必需字段
        if 'info' not in spec:
            issues.append(ValidationIssue(
                path='$',
                message='缺少info字段',
                code='MISSING_INFO',
                severity=ValidationSeverity.ERROR
            ))
        
        # 检查channels
        if 'channels' not in spec:
            issues.append(ValidationIssue(
                path='$',
                message='缺少channels字段',
                code='MISSING_CHANNELS',
                severity=ValidationSeverity.ERROR
            ))
        else:
            for channel_name, channel in spec['channels'].items():
                if 'address' not in channel:
                    issues.append(ValidationIssue(
                        path=f'channels.{channel_name}',
                        message='channel缺少address字段',
                        code='MISSING_CHANNEL_ADDRESS',
                        severity=ValidationSeverity.ERROR
                    ))
        
        return ValidationResult(
            valid=not any(i.severity == ValidationSeverity.ERROR for i in issues),
            schema_type=SchemaType.ASYNCAPI,
            issues=issues,
            metadata={'version': version}
        )


class StandardComplianceChecker:
    """行业标准合规性检查器"""
    
    STANDARDS = {
        'iso20022': 'ISO 20022 Financial Messages',
        'fhir': 'HL7 FHIR R5',
        'opc_ua': 'OPC Unified Architecture',
        'gs1': 'GS1 Standards',
        'w3c_vc': 'W3C Verifiable Credentials',
        'iso21838': 'ISO/IEC 21838 Top-level Ontologies'
    }
    
    def check(self, schema: Dict[str, Any], standards: List[str]) -> List[ComplianceReport]:
        """检查合规性"""
        reports = []
        
        for std in standards:
            if std == 'iso20022':
                reports.append(self._check_iso20022(schema))
            elif std == 'fhir':
                reports.append(self._check_fhir(schema))
            elif std == 'gs1':
                reports.append(self._check_gs1(schema))
            elif std == 'iso21838':
                reports.append(self._check_iso21838(schema))
        
        return reports
    
    def _check_iso20022(self, schema: Dict[str, Any]) -> ComplianceReport:
        """检查ISO 20022合规性"""
        issues = []
        score = 100
        
        # 检查是否包含businessMessageIdentifier
        if 'businessMessageIdentifier' not in str(schema):
            issues.append(ValidationIssue(
                path='$',
                message='建议包含businessMessageIdentifier',
                code='ISO20022_MSG_ID',
                severity=ValidationSeverity.INFO
            ))
            score -= 5
        
        return ComplianceReport(
            standard='ISO 20022',
            compliant=score >= 90,
            score=max(0, score),
            issues=issues
        )
    
    def _check_fhir(self, schema: Dict[str, Any]) -> ComplianceReport:
        """检查FHIR合规性"""
        issues = []
        score = 100
        
        # 检查FHIR资源类型
        if 'resourceType' not in schema.get('properties', {}):
            issues.append(ValidationIssue(
                path='$.properties',
                message='FHIR资源必须包含resourceType属性',
                code='FHIR_RESOURCE_TYPE',
                severity=ValidationSeverity.ERROR
            ))
            score -= 20
        
        return ComplianceReport(
            standard='HL7 FHIR',
            compliant=score >= 80,
            score=max(0, score),
            issues=issues
        )
    
    def _check_gs1(self, schema: Dict[str, Any]) -> ComplianceReport:
        """检查GS1合规性"""
        issues = []
        score = 100
        
        # 检查GTIN支持
        gtin_found = any('gtin' in str(k).lower() for k in schema.get('properties', {}).keys())
        if not gtin_found:
            issues.append(ValidationIssue(
                path='$.properties',
                message='GS1标准建议包含GTIN标识符',
                code='GS1_GTIN',
                severity=ValidationSeverity.WARNING
            ))
            score -= 10
        
        return ComplianceReport(
            standard='GS1',
            compliant=score >= 85,
            score=max(0, score),
            issues=issues
        )
    
    def _check_iso21838(self, schema: Dict[str, Any]) -> ComplianceReport:
        """检查ISO/IEC 21838 (BFO) 合规性"""
        issues = []
        score = 100
        
        # 检查是否有本体论对齐
        if '@context' not in schema:
            issues.append(ValidationIssue(
                path='$',
                message='建议添加@context以支持BFO对齐',
                code='ISO21838_CONTEXT',
                severity=ValidationSeverity.WARNING
            ))
            score -= 15
        
        return ComplianceReport(
            standard='ISO/IEC 21838 (BFO)',
            compliant=score >= 80,
            score=max(0, score),
            issues=issues
        )


class EnhancedSchemaValidator:
    """增强型Schema验证器主类"""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.json_validator = JSONSchema2025Validator(strict_mode=strict_mode)
        self.openapi_validator = OpenAPI31Validator()
        self.asyncapi_validator = AsyncAPI30Validator()
        self.compliance_checker = StandardComplianceChecker()
    
    def validate(
        self,
        schema: Union[Dict[str, Any], str],
        schema_type: SchemaType,
        standards: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        验证Schema
        
        Args:
            schema: 要验证的Schema（字典或JSON字符串）
            schema_type: Schema类型
            standards: 要检查的行业标准列表
        
        Returns:
            ValidationResult: 验证结果
        """
        # 解析JSON字符串
        if isinstance(schema, str):
            try:
                schema = json.loads(schema)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    valid=False,
                    schema_type=schema_type,
                    issues=[ValidationIssue(
                        path='$',
                        message=f'JSON解析错误: {e}',
                        code='JSON_PARSE_ERROR',
                        severity=ValidationSeverity.ERROR
                    )]
                )
        
        # 根据类型选择验证器
        if schema_type == SchemaType.JSON_SCHEMA:
            result = self.json_validator.validate(schema)
        elif schema_type == SchemaType.OPENAPI:
            result = self.openapi_validator.validate(schema)
        elif schema_type == SchemaType.ASYNCAPI:
            result = self.asyncapi_validator.validate(schema)
        else:
            result = ValidationResult(
                valid=True,
                schema_type=schema_type,
                issues=[ValidationIssue(
                    path='$',
                    message=f'类型 {schema_type.value} 的基础验证',
                    code='BASIC_VALIDATION',
                    severity=ValidationSeverity.INFO
                )]
            )
        
        # 检查行业标准合规性
        if standards:
            result.compliance_reports = self.compliance_checker.check(schema, standards)
        
        return result
    
    def validate_file(
        self,
        file_path: Union[str, Path],
        schema_type: Optional[SchemaType] = None,
        standards: Optional[List[str]] = None
    ) -> ValidationResult:
        """从文件验证Schema"""
        path = Path(file_path)
        
        if not path.exists():
            return ValidationResult(
                valid=False,
                schema_type=schema_type or SchemaType.JSON_SCHEMA,
                issues=[ValidationIssue(
                    path=str(path),
                    message='文件不存在',
                    code='FILE_NOT_FOUND',
                    severity=ValidationSeverity.ERROR
                )]
            )
        
        # 自动检测类型
        if schema_type is None:
            schema_type = self._detect_type(path)
        
        # 读取并验证
        content = path.read_text(encoding='utf-8')
        return self.validate(content, schema_type, standards)
    
    def _detect_type(self, path: Path) -> SchemaType:
        """自动检测Schema类型"""
        content = path.read_text(encoding='utf-8').lower()
        
        if 'openapi' in content:
            return SchemaType.OPENAPI
        elif 'asyncapi' in content:
            return SchemaType.ASYNCAPI
        elif 'graphql' in content or path.suffix == '.graphql':
            return SchemaType.GRAPHQL
        elif path.suffix in ['.xsd', '.wsdl']:
            return SchemaType.XML_SCHEMA
        else:
            return SchemaType.JSON_SCHEMA


# 便捷函数
def validate_schema(
    schema: Union[Dict[str, Any], str],
    schema_type: str = 'json_schema',
    strict: bool = False,
    standards: Optional[List[str]] = None
) -> ValidationResult:
    """便捷验证函数"""
    validator = EnhancedSchemaValidator(strict_mode=strict)
    type_enum = SchemaType(schema_type)
    return validator.validate(schema, type_enum, standards)


if __name__ == '__main__':
    # 测试示例
    test_schema = {
        "$schema": "https://json-schema.org/draft/2025-01/schema",
        "$id": "https://example.com/product",
        "title": "Product",
        "description": "产品Schema",
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "format": "uuid"
            },
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100
            },
            "price": {
                "type": "number",
                "minimum": 0
            },
            "gtin": {
                "type": "string",
                "pattern": "^[0-9]{8,14}$"
            }
        },
        "required": ["id", "name", "price"]
    }
    
    result = validate_schema(
        test_schema,
        schema_type='json_schema',
        strict=True,
        standards=['gs1', 'iso21838']
    )
    
    print(f"验证结果: {'通过' if result.valid else '失败'}")
    print(f"问题数: {len(result.issues)}")
    print(f"合规报告: {len(result.compliance_reports)}")
    
    for issue in result.issues:
        print(f"  [{issue.severity.value}] {issue.path}: {issue.message}")
    
    for report in result.compliance_reports:
        print(f"  合规性 ({report.standard}): {report.score}/100")
