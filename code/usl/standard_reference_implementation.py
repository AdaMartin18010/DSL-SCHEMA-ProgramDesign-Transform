#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Schema Language (USL) v1.0 Standard Reference Implementation

USL标准参考实现 - 符合USL v1.0规范

本模块提供了USL语言的完整参考实现，包括：
- USL解析器（Parser）
- 类型检查器（Type Checker）
- 约束验证器（Constraint Validator）
- 多格式转换器（Multi-format Transformer）

Version: 1.0.0
License: Apache-2.0
"""

from __future__ import annotations

import json
import re
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Callable, Dict, Generic, Iterator, List, Optional, 
    Set, Tuple, TypeVar, Union, Protocol
)
from collections import defaultdict
from functools import lru_cache

# =============================================================================
# 1. 基础类型定义
# =============================================================================

T = TypeVar('T')


class USLType(Enum):
    """USL类型枚举"""
    # 原始类型
    STRING = "String"
    TEXT = "Text"
    CHAR = "Char"
    INTEGER = "Integer"
    INT8 = "Int8"
    INT16 = "Int16"
    INT32 = "Int32"
    INT64 = "Int64"
    INT128 = "Int128"
    UNSIGNED = "Unsigned"
    UINT8 = "UInt8"
    UINT16 = "UInt16"
    UINT32 = "UInt32"
    UINT64 = "UInt64"
    UINT128 = "UInt128"
    FLOAT = "Float"
    FLOAT32 = "Float32"
    FLOAT64 = "Float64"
    FLOAT128 = "Float128"
    DECIMAL = "Decimal"
    BOOLEAN = "Boolean"
    BOOL = "Bool"
    DATE = "Date"
    TIME = "Time"
    DATETIME = "DateTime"
    TIMESTAMP = "Timestamp"
    DURATION = "Duration"
    UUID = "UUID"
    URI = "URI"
    URL = "URL"
    EMAIL = "Email"
    IPV4 = "IPv4"
    IPV6 = "IPv6"
    CIDR = "CIDR"
    BINARY = "Binary"
    BYTES = "Bytes"
    BASE64 = "Base64"
    HEX = "Hex"
    ANY = "Any"
    NEVER = "Never"
    UNKNOWN = "Unknown"
    # 复合类型
    ARRAY = "Array"
    LIST = "List"
    VECTOR = "Vector"
    MAP = "Map"
    DICT = "Dict"
    SET = "Set"
    RECORD = "Record"
    FUNCTION = "Function"
    # 自定义类型
    CUSTOM = "Custom"


@dataclass(frozen=True)
class SourceLocation:
    """源代码位置"""
    line: int
    column: int
    filename: Optional[str] = None
    
    def __str__(self) -> str:
        if self.filename:
            return f"{self.filename}:{self.line}:{self.column}"
        return f"line {self.line}, column {self.column}"


@dataclass
class USLError(Exception):
    """USL基础错误"""
    message: str
    location: Optional[SourceLocation] = None
    
    def __str__(self) -> str:
        if self.location:
            return f"{self.location}: {self.message}"
        return self.message


class USLParseError(USLError):
    """USL解析错误"""
    pass


class USLValidationError(USLError):
    """USL验证错误"""
    pass


class USLTypeError(USLError):
    """USL类型错误"""
    pass


# =============================================================================
# 2. AST节点定义
# =============================================================================

class ASTNode(ABC):
    """AST基础节点"""
    location: Optional[SourceLocation] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        """接受访问者"""
        method_name = f'visit_{self.__class__.__name__}'
        method = getattr(visitor, method_name, visitor.visit_default)
        return method(self)


class ASTVisitor(ABC):
    """AST访问者基类"""
    
    @abstractmethod
    def visit_default(self, node: ASTNode) -> Any:
        pass


@dataclass
class USLDocument(ASTNode):
    """USL文档根节点"""
    schema: Optional[SchemaNode] = None
    imports: List[ImportNode] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_USLDocument(self)


@dataclass
class SchemaNode(ASTNode):
    """Schema定义节点"""
    name: str = ""
    version: Optional[str] = None
    extends: List[str] = field(default_factory=list)
    elements: List[SchemaElement] = field(default_factory=list)
    metadata: Optional[MetadataNode] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_SchemaNode(self)


@dataclass
class ImportNode(ASTNode):
    """导入语句节点"""
    path: str = ""
    alias: Optional[str] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ImportNode(self)


@dataclass
class MetadataNode(ASTNode):
    """元数据定义节点"""
    items: Dict[str, Any] = field(default_factory=dict)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_MetadataNode(self)


# Schema元素联合类型
SchemaElement = Union[
    'TypeDefinitionNode',
    'FieldDefinitionNode', 
    'ConstraintDefinitionNode',
    'RelationDefinitionNode',
    'OperationDefinitionNode',
    'EnumDefinitionNode',
    'InterfaceDefinitionNode',
    'StructDefinitionNode',
    'EntityDefinitionNode',
    'ValueDefinitionNode'
]


@dataclass
class TypeDefinitionNode(ASTNode):
    """类型定义节点"""
    name: str = ""
    type_expr: 'TypeExpression' = field(default_factory=lambda: PrimitiveTypeNode(USLType.ANY))
    generic_params: List[str] = field(default_factory=list)
    constraints: List['ConstraintNode'] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_TypeDefinitionNode(self)


@dataclass
class FieldDefinitionNode(ASTNode):
    """字段定义节点"""
    name: str = ""
    type_expr: 'TypeExpression' = field(default_factory=lambda: PrimitiveTypeNode(USLType.ANY))
    modifiers: List[str] = field(default_factory=list)
    default_value: Optional[Any] = None
    constraints: List['ConstraintNode'] = field(default_factory=list)
    description: Optional[str] = None
    examples: List[Any] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_FieldDefinitionNode(self)


@dataclass
class ConstraintDefinitionNode(ASTNode):
    """约束定义节点"""
    name: str = ""
    expression: 'ConstraintExpression' = field(default_factory=lambda: LiteralConstraintNode(True))
    message: Optional[str] = None
    severity: str = "error"  # error, warning, info
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ConstraintDefinitionNode(self)


@dataclass
class RelationDefinitionNode(ASTNode):
    """关系定义节点"""
    name: str = ""
    relation_type: str = ""  # one_to_one, one_to_many, etc.
    source: str = ""
    target: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_RelationDefinitionNode(self)


@dataclass
class OperationDefinitionNode(ASTNode):
    """操作定义节点"""
    operation_type: str = ""  # query, mutation, subscription, rpc
    name: str = ""
    parameters: List['ParameterNode'] = field(default_factory=list)
    return_type: Optional['TypeExpression'] = None
    body: Optional['OperationBodyNode'] = None
    throws: List[str] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_OperationDefinitionNode(self)


@dataclass
class ParameterNode(ASTNode):
    """参数节点"""
    name: str = ""
    type_expr: 'TypeExpression' = field(default_factory=lambda: PrimitiveTypeNode(USLType.ANY))
    default_value: Optional[Any] = None
    is_optional: bool = False
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ParameterNode(self)


@dataclass
class OperationBodyNode(ASTNode):
    """操作体节点"""
    statements: List['StatementNode'] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_OperationBodyNode(self)


@dataclass
class EnumDefinitionNode(ASTNode):
    """枚举定义节点"""
    name: str = ""
    members: List[Tuple[str, Optional[Any]]] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_EnumDefinitionNode(self)


@dataclass
class InterfaceDefinitionNode(ASTNode):
    """接口定义节点"""
    name: str = ""
    extends: List[str] = field(default_factory=list)
    fields: List[FieldDefinitionNode] = field(default_factory=list)
    methods: List['MethodSignatureNode'] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_InterfaceDefinitionNode(self)


@dataclass
class MethodSignatureNode(ASTNode):
    """方法签名节点"""
    name: str = ""
    parameters: List[ParameterNode] = field(default_factory=list)
    return_type: Optional['TypeExpression'] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_MethodSignatureNode(self)


@dataclass
class StructDefinitionNode(ASTNode):
    """结构定义节点"""
    name: str = ""
    generic_params: List[str] = field(default_factory=list)
    fields: List[FieldDefinitionNode] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_StructDefinitionNode(self)


@dataclass
class EntityDefinitionNode(ASTNode):
    """实体定义节点"""
    name: str = ""
    generic_params: List[str] = field(default_factory=list)
    identifiers: List[str] = field(default_factory=list)
    fields: List[FieldDefinitionNode] = field(default_factory=list)
    relations: List[RelationDefinitionNode] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_EntityDefinitionNode(self)


@dataclass
class ValueDefinitionNode(ASTNode):
    """值类型定义节点"""
    name: str = ""
    generic_params: List[str] = field(default_factory=list)
    fields: List[FieldDefinitionNode] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ValueDefinitionNode(self)


# 类型表达式联合类型
TypeExpression = Union[
    'PrimitiveTypeNode',
    'ArrayTypeNode',
    'MapTypeNode',
    'SetTypeNode',
    'ReferenceTypeNode',
    'OptionalTypeNode',
    'UnionTypeNode',
    'FunctionTypeNode',
    'GenericTypeNode'
]


@dataclass
class PrimitiveTypeNode(ASTNode):
    """原始类型节点"""
    type_kind: USLType = USLType.ANY
    precision: Optional[int] = None
    scale: Optional[int] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_PrimitiveTypeNode(self)


@dataclass
class ArrayTypeNode(ASTNode):
    """数组类型节点"""
    element_type: TypeExpression = field(default_factory=lambda: PrimitiveTypeNode(USLType.ANY))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ArrayTypeNode(self)


@dataclass
class MapTypeNode(ASTNode):
    """映射类型节点"""
    key_type: TypeExpression = field(default_factory=lambda: PrimitiveTypeNode(USLType.STRING))
    value_type: TypeExpression = field(default_factory=lambda: PrimitiveTypeNode(USLType.ANY))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_MapTypeNode(self)


@dataclass
class SetTypeNode(ASTNode):
    """集合类型节点"""
    element_type: TypeExpression = field(default_factory=lambda: PrimitiveTypeNode(USLType.ANY))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_SetTypeNode(self)


@dataclass
class ReferenceTypeNode(ASTNode):
    """引用类型节点"""
    name: str = ""
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ReferenceTypeNode(self)


@dataclass
class OptionalTypeNode(ASTNode):
    """可选类型节点"""
    inner_type: TypeExpression = field(default_factory=lambda: PrimitiveTypeNode(USLType.ANY))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_OptionalTypeNode(self)


@dataclass
class UnionTypeNode(ASTNode):
    """联合类型节点"""
    types: List[TypeExpression] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_UnionTypeNode(self)


@dataclass
class FunctionTypeNode(ASTNode):
    """函数类型节点"""
    param_types: List[TypeExpression] = field(default_factory=list)
    return_type: TypeExpression = field(default_factory=lambda: PrimitiveTypeNode(USLType.VOID))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_FunctionTypeNode(self)


@dataclass
class GenericTypeNode(ASTNode):
    """泛型类型节点"""
    base_type: str = ""
    type_args: List[TypeExpression] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_GenericTypeNode(self)


# 约束表达式联合类型
ConstraintExpression = Union[
    'LiteralConstraintNode',
    'IdentifierConstraintNode',
    'BinaryConstraintNode',
    'UnaryConstraintNode',
    'CallConstraintNode',
    'PathConstraintNode',
    'ConditionalConstraintNode'
]


@dataclass
class LiteralConstraintNode(ASTNode):
    """字面量约束节点"""
    value: Any = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_LiteralConstraintNode(self)


@dataclass
class IdentifierConstraintNode(ASTNode):
    """标识符约束节点"""
    name: str = ""
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_IdentifierConstraintNode(self)


@dataclass
class BinaryConstraintNode(ASTNode):
    """二元约束节点"""
    operator: str = ""  # +, -, *, /, =, !=, <, >, <=, >=, and, or, in
    left: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    right: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_BinaryConstraintNode(self)


@dataclass
class UnaryConstraintNode(ASTNode):
    """一元约束节点"""
    operator: str = ""  # -, !, not
    operand: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_UnaryConstraintNode(self)


@dataclass
class CallConstraintNode(ASTNode):
    """函数调用约束节点"""
    function: str = ""
    arguments: List[ConstraintExpression] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_CallConstraintNode(self)


@dataclass
class PathConstraintNode(ASTNode):
    """路径约束节点"""
    base: str = ""
    path: List[Union[str, int]] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_PathConstraintNode(self)


@dataclass
class ConditionalConstraintNode(ASTNode):
    """条件约束节点"""
    condition: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(True))
    then_expr: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    else_expr: Optional[ConstraintExpression] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ConditionalConstraintNode(self)


StatementNode = Union[
    'VariableDeclarationNode',
    'AssignmentNode',
    'ReturnNode',
    'IfNode',
    'ForNode',
    'WhileNode',
    'MatchNode',
    'ExpressionStatementNode'
]


@dataclass
class VariableDeclarationNode(ASTNode):
    """变量声明节点"""
    is_mutable: bool = False
    name: str = ""
    type_expr: Optional[TypeExpression] = None
    initializer: Optional[ConstraintExpression] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_VariableDeclarationNode(self)


@dataclass
class AssignmentNode(ASTNode):
    """赋值节点"""
    target: str = ""
    value: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_AssignmentNode(self)


@dataclass
class ReturnNode(ASTNode):
    """返回节点"""
    value: Optional[ConstraintExpression] = None
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ReturnNode(self)


@dataclass
class IfNode(ASTNode):
    """条件节点"""
    condition: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(True))
    then_body: List[StatementNode] = field(default_factory=list)
    else_body: List[StatementNode] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_IfNode(self)


@dataclass
class ForNode(ASTNode):
    """循环节点"""
    variable: str = ""
    iterable: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    body: List[StatementNode] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ForNode(self)


@dataclass
class WhileNode(ASTNode):
    """While循环节点"""
    condition: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(True))
    body: List[StatementNode] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_WhileNode(self)


@dataclass
class MatchNode(ASTNode):
    """匹配节点"""
    expression: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    arms: List[Tuple['PatternNode', List[StatementNode]]] = field(default_factory=list)
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_MatchNode(self)


PatternNode = Union[
    'LiteralPatternNode',
    'IdentifierPatternNode',
    'WildcardPatternNode',
    'ConstructorPatternNode',
    'ArrayPatternNode',
    'RecordPatternNode'
]


@dataclass
class LiteralPatternNode(ASTNode):
    value: Any = None


@dataclass
class IdentifierPatternNode(ASTNode):
    name: str = ""


@dataclass
class WildcardPatternNode(ASTNode):
    pass


@dataclass
class ConstructorPatternNode(ASTNode):
    name: str = ""
    patterns: List[PatternNode] = field(default_factory=list)


@dataclass
class ArrayPatternNode(ASTNode):
    patterns: List[PatternNode] = field(default_factory=list)


@dataclass
class RecordPatternNode(ASTNode):
    fields: Dict[str, PatternNode] = field(default_factory=dict)


@dataclass
class ExpressionStatementNode(ASTNode):
    """表达式语句节点"""
    expression: ConstraintExpression = field(default_factory=lambda: LiteralConstraintNode(None))
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_ExpressionStatementNode(self)


# =============================================================================
# 3. USL解析器
# =============================================================================

class USLParser:
    """
    USL解析器 - 将USL源代码解析为AST
    
    这是一个简化版的递归下降解析器，用于演示USL解析的核心逻辑。
    生产环境建议使用Lark或ANTLR等专业解析器生成器。
    """
    
    def __init__(self):
        self.tokens: List[Tuple[str, Any]] = []
        self.pos: int = 0
        self.current_line: int = 1
        self.current_column: int = 1
        self.filename: Optional[str] = None
    
    def parse(self, source: str, filename: Optional[str] = None) -> USLDocument:
        """
        解析USL源代码
        
        Args:
            source: USL源代码字符串
            filename: 源文件名（用于错误报告）
            
        Returns:
            USLDocument: 解析后的AST文档
            
        Raises:
            USLParseError: 解析错误
        """
        self.filename = filename
        self.tokens = self._tokenize(source)
        self.pos = 0
        
        return self._parse_document()
    
    def parse_file(self, filepath: Path) -> USLDocument:
        """从文件解析USL"""
        source = filepath.read_text(encoding='utf-8')
        return self.parse(source, str(filepath))
    
    def _tokenize(self, source: str) -> List[Tuple[str, Any]]:
        """
        词法分析 - 将源代码转换为Token序列
        
        这是一个简化的词法分析器，仅支持核心Token类型。
        """
        tokens = []
        i = 0
        line = 1
        column = 1
        
        keywords = {
            'schema', 'type', 'newtype', 'enum', 'union', 'interface', 
            'struct', 'entity', 'value', 'field', 'constraint', 'relation',
            'query', 'mutation', 'subscription', 'rpc', 'metadata', 'import',
            'extends', 'readonly', 'mutable', 'private', 'protected', 'public',
            'static', 'abstract', 'true', 'false', 'null', 'nil', 'undefined',
            'if', 'then', 'else', 'for', 'in', 'while', 'match', 'return',
            'let', 'var', 'and', 'or', 'not', 'implies', 'this', 'self'
        }
        
        while i < len(source):
            ch = source[i]
            
            # 跳过空白字符
            if ch.isspace():
                if ch == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1
                continue
            
            # 跳过注释
            if ch == '/' and i + 1 < len(source):
                if source[i + 1] == '/':
                    # 行注释
                    while i < len(source) and source[i] != '\n':
                        i += 1
                    continue
                elif source[i + 1] == '*':
                    # 块注释
                    i += 2
                    while i < len(source) - 1 and not (source[i] == '*' and source[i + 1] == '/'):
                        if source[i] == '\n':
                            line += 1
                            column = 1
                        i += 1
                    i += 2
                    continue
            
            # 字符串字面量
            if ch == '"' or ch == "'":
                quote = ch
                start = i
                i += 1
                value = ""
                while i < len(source) and source[i] != quote:
                    if source[i] == '\\' and i + 1 < len(source):
                        i += 1
                        if source[i] == 'n':
                            value += '\n'
                        elif source[i] == 't':
                            value += '\t'
                        elif source[i] == 'r':
                            value += '\r'
                        else:
                            value += source[i]
                    else:
                        value += source[i]
                    i += 1
                i += 1  # 跳过结束引号
                tokens.append(('STRING', value))
                column += i - start
                continue
            
            # 数字字面量
            if ch.isdigit() or (ch == '-' and i + 1 < len(source) and source[i + 1].isdigit()):
                start = i
                if ch == '-':
                    i += 1
                is_float = False
                while i < len(source) and (source[i].isdigit() or source[i] == '.'):
                    if source[i] == '.':
                        is_float = True
                    i += 1
                value_str = source[start:i]
                if is_float:
                    tokens.append(('NUMBER', float(value_str)))
                else:
                    tokens.append(('NUMBER', int(value_str)))
                column += i - start
                continue
            
            # 标识符和关键字
            if ch.isalpha() or ch == '_':
                start = i
                while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                    i += 1
                value = source[start:i]
                if value in keywords:
                    tokens.append((value.upper(), value))
                else:
                    tokens.append(('IDENTIFIER', value))
                column += i - start
                continue
            
            # 多字符运算符
            if i + 1 < len(source):
                two_char = source[i:i+2]
                if two_char in ('==', '!=', '<=', '>=', '->', '<-', '<->', '~>', '<~', '=>'):
                    tokens.append((two_char, two_char))
                    i += 2
                    column += 2
                    continue
            
            # 单字符Token
            single_char_tokens = {
                '{': 'LBRACE', '}': 'RBRACE', '(': 'LPAREN', ')': 'RPAREN',
                '[': 'LBRACKET', ']': 'RBRACKET', ':': 'COLON', ',': 'COMMA',
                '.': 'DOT', ';': 'SEMICOLON', '+': 'PLUS', '-': 'MINUS',
                '*': 'STAR', '/': 'SLASH', '%': 'PERCENT', '=': 'ASSIGN',
                '<': 'LT', '>': 'GT', '&': 'AMPERSAND', '|': 'PIPE',
                '!': 'BANG', '?': 'QUESTION', '@': 'AT', '#': 'HASH'
            }
            
            if ch in single_char_tokens:
                tokens.append((single_char_tokens[ch], ch))
                i += 1
                column += 1
                continue
            
            # 未知字符
            raise USLParseError(
                f"Unexpected character: {ch}",
                SourceLocation(line, column, self.filename)
            )
        
        tokens.append(('EOF', None))
        return tokens
    
    def _current(self) -> Tuple[str, Any]:
        """获取当前Token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', None)
    
    def _peek(self, offset: int = 0) -> Tuple[str, Any]:
        """预览Token"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return ('EOF', None)
    
    def _advance(self) -> Tuple[str, Any]:
        """前进到下一个Token"""
        token = self._current()
        self.pos += 1
        return token
    
    def _expect(self, token_type: str) -> Any:
        """期望特定类型的Token"""
        token_type_current, value = self._current()
        if token_type_current != token_type:
            raise USLParseError(
                f"Expected {token_type}, got {token_type_current}",
                self._location()
            )
        self._advance()
        return value
    
    def _match(self, *token_types: str) -> bool:
        """匹配Token类型"""
        return self._current()[0] in token_types
    
    def _consume(self, token_type: str) -> bool:
        """消费特定类型的Token"""
        if self._match(token_type):
            self._advance()
            return True
        return False
    
    def _location(self) -> SourceLocation:
        """获取当前位置"""
        return SourceLocation(self.current_line, self.current_column, self.filename)
    
    def _parse_document(self) -> USLDocument:
        """解析USL文档"""
        doc = USLDocument()
        doc.location = self._location()
        
        # 解析导入语句
        while self._match('IMPORT'):
            doc.imports.append(self._parse_import())
        
        # 解析Schema
        if self._match('SCHEMA'):
            doc.schema = self._parse_schema()
        
        self._expect('EOF')
        return doc
    
    def _parse_import(self) -> ImportNode:
        """解析导入语句"""
        self._expect('IMPORT')
        
        node = ImportNode()
        node.location = self._location()
        
        if self._match('STRING'):
            node.path = self._advance()[1]
        elif self._match('IDENTIFIER'):
            # 解析路径如 a.b.c
            parts = [self._advance()[1]]
            while self._consume('DOT'):
                parts.append(self._expect('IDENTIFIER'))
            node.path = '.'.join(parts)
        else:
            raise USLParseError("Expected import path", self._location())
        
        if self._consume('AS'):
            node.alias = self._expect('IDENTIFIER')
        
        return node
    
    def _parse_schema(self) -> SchemaNode:
        """解析Schema定义"""
        self._expect('SCHEMA')
        
        node = SchemaNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        # 解析版本
        if self._consume('V'):
            version_parts = [str(self._expect('NUMBER'))]
            while self._consume('DOT'):
                version_parts.append(str(self._expect('NUMBER')))
            node.version = '.'.join(version_parts)
        
        # 解析继承
        if self._consume('EXTENDS'):
            node.extends.append(self._expect('IDENTIFIER'))
            while self._consume('COMMA'):
                node.extends.append(self._expect('IDENTIFIER'))
        
        self._expect('LBRACE')
        
        # 解析Schema体
        while not self._match('RBRACE'):
            if self._match('EOF'):
                raise USLParseError("Unexpected end of file, expected }", self._location())
            node.elements.append(self._parse_schema_element())
        
        self._expect('RBRACE')
        return node
    
    def _parse_schema_element(self) -> SchemaElement:
        """解析Schema元素"""
        # 检查注释
        if self._match('IDENTIFIER') and self._peek()[0] == 'COLON':
            return self._parse_field_definition()
        
        token_type = self._current()[0]
        
        if token_type == 'TYPE':
            return self._parse_type_definition()
        elif token_type == 'FIELD':
            return self._parse_field_definition()
        elif token_type == 'CONSTRAINT':
            return self._parse_constraint_definition()
        elif token_type == 'RELATION':
            return self._parse_relation_definition()
        elif token_type == 'QUERY':
            return self._parse_operation_definition('query')
        elif token_type == 'MUTATION':
            return self._parse_operation_definition('mutation')
        elif token_type == 'SUBSCRIPTION':
            return self._parse_operation_definition('subscription')
        elif token_type == 'RPC':
            return self._parse_operation_definition('rpc')
        elif token_type == 'ENUM':
            return self._parse_enum_definition()
        elif token_type == 'INTERFACE':
            return self._parse_interface_definition()
        elif token_type == 'STRUCT':
            return self._parse_struct_definition()
        elif token_type == 'ENTITY':
            return self._parse_entity_definition()
        elif token_type == 'VALUE':
            return self._parse_value_definition()
        elif token_type == 'METADATA':
            return self._parse_metadata_definition()
        elif token_type == 'READONLY' or token_type == 'MUTABLE' or token_type == 'PRIVATE':
            return self._parse_field_definition()
        else:
            raise USLParseError(f"Unexpected token: {token_type}", self._location())
    
    def _parse_type_definition(self) -> TypeDefinitionNode:
        """解析类型定义"""
        self._expect('TYPE')
        
        node = TypeDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        # 解析泛型参数
        if self._consume('LT'):
            node.generic_params.append(self._expect('IDENTIFIER'))
            while self._consume('COMMA'):
                node.generic_params.append(self._expect('IDENTIFIER'))
            self._expect('GT')
        
        self._expect('COLON')
        node.type_expr = self._parse_type_expression()
        
        # 解析约束
        if self._consume('LBRACE'):
            while not self._match('RBRACE'):
                node.constraints.append(self._parse_constraint_item())
            self._expect('RBRACE')
        
        return node
    
    def _parse_field_definition(self) -> FieldDefinitionNode:
        """解析字段定义"""
        node = FieldDefinitionNode()
        node.location = self._location()
        
        # 解析修饰符
        while self._match('READONLY') or self._match('MUTABLE') or self._match('PRIVATE'):
            node.modifiers.append(self._advance()[1])
        
        if self._consume('FIELD'):
            node.name = self._expect('IDENTIFIER')
        else:
            node.name = self._expect('IDENTIFIER')
        
        self._expect('COLON')
        node.type_expr = self._parse_type_expression()
        
        # 解析属性
        if self._consume('LBRACE'):
            while not self._match('RBRACE'):
                self._parse_field_attribute(node)
            self._expect('RBRACE')
        
        return node
    
    def _parse_field_attribute(self, node: FieldDefinitionNode) -> None:
        """解析字段属性"""
        attr_name = self._expect('IDENTIFIER')
        self._expect('COLON')
        
        if attr_name == 'default':
            node.default_value = self._parse_value()
        elif attr_name == 'constraint':
            node.constraints.append(self._parse_constraint_expression())
        elif attr_name == 'description':
            node.description = self._expect('STRING')
        elif attr_name == 'example':
            node.examples.append(self._parse_value())
        elif attr_name == 'examples':
            self._expect('LBRACKET')
            while not self._match('RBRACKET'):
                node.examples.append(self._parse_value())
                self._consume('COMMA')
            self._expect('RBRACKET')
        else:
            # 未知属性，跳过值
            self._parse_value()
    
    def _parse_type_expression(self) -> TypeExpression:
        """解析类型表达式"""
        # 简化实现，只处理基本类型
        token_type, value = self._current()
        
        if token_type == 'IDENTIFIER':
            self._advance()
            
            # 检查是否是泛型
            if self._match('LT'):
                type_args = []
                self._expect('LT')
                type_args.append(self._parse_type_expression())
                while self._consume('COMMA'):
                    type_args.append(self._parse_type_expression())
                self._expect('GT')
                return GenericTypeNode(base_type=value, type_args=type_args)
            
            # 检查是否是可选类型
            if self._consume('QUESTION'):
                return OptionalTypeNode(ReferenceTypeNode(name=value))
            
            return ReferenceTypeNode(name=value)
        
        elif token_type in ['STRING', 'INTEGER', 'FLOAT', 'BOOLEAN', 'DATE', 'DATETIME', 
                           'UUID', 'DECIMAL', 'ANY', 'NEVER', 'UNKNOWN']:
            self._advance()
            type_map = {
                'STRING': USLType.STRING, 'INTEGER': USLType.INTEGER, 
                'FLOAT': USLType.FLOAT, 'BOOLEAN': USLType.BOOLEAN,
                'DATE': USLType.DATE, 'DATETIME': USLType.DATETIME,
                'UUID': USLType.UUID, 'DECIMAL': USLType.DECIMAL,
                'ANY': USLType.ANY, 'NEVER': USLType.NEVER,
                'UNKNOWN': USLType.UNKNOWN
            }
            return PrimitiveTypeNode(type_kind=type_map.get(token_type, USLType.ANY))
        
        elif token_type == 'ARRAY' or token_type == 'LIST':
            self._advance()
            self._expect('LT')
            element_type = self._parse_type_expression()
            self._expect('GT')
            return ArrayTypeNode(element_type=element_type)
        
        elif token_type == 'MAP' or token_type == 'DICT':
            self._advance()
            self._expect('LT')
            key_type = self._parse_type_expression()
            self._expect('COMMA')
            value_type = self._parse_type_expression()
            self._expect('GT')
            return MapTypeNode(key_type=key_type, value_type=value_type)
        
        else:
            raise USLParseError(f"Expected type expression, got {token_type}", self._location())
    
    def _parse_constraint_definition(self) -> ConstraintDefinitionNode:
        """解析约束定义"""
        self._expect('CONSTRAINT')
        
        node = ConstraintDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        self._expect('LBRACE')
        
        while not self._match('RBRACE'):
            key = self._expect('IDENTIFIER')
            self._expect('COLON')
            
            if key == 'expression':
                node.expression = self._parse_constraint_expression()
            elif key == 'message':
                node.message = self._expect('STRING')
            elif key == 'severity':
                node.severity = self._expect('IDENTIFIER')
        
        self._expect('RBRACE')
        return node
    
    def _parse_constraint_item(self) -> ConstraintNode:
        """解析约束项（简化版）"""
        # 简化的约束解析
        if self._match('IDENTIFIER'):
            key = self._advance()[1]
            self._expect('COLON')
            value = self._parse_value()
            return ConstraintNode(key=key, value=value)
        
        return ConstraintNode()
    
    def _parse_constraint_expression(self) -> ConstraintExpression:
        """解析约束表达式（简化版）"""
        # 简化实现，仅支持基本表达式
        return self._parse_or_expression()
    
    def _parse_or_expression(self) -> ConstraintExpression:
        """解析或表达式"""
        left = self._parse_and_expression()
        
        while self._consume('OR'):
            right = self._parse_and_expression()
            left = BinaryConstraintNode(operator='or', left=left, right=right)
        
        return left
    
    def _parse_and_expression(self) -> ConstraintExpression:
        """解析与表达式"""
        left = self._parse_comparison()
        
        while self._consume('AND'):
            right = self._parse_comparison()
            left = BinaryConstraintNode(operator='and', left=left, right=right)
        
        return left
    
    def _parse_comparison(self) -> ConstraintExpression:
        """解析比较表达式"""
        left = self._parse_additive()
        
        if self._match('EQ'):
            self._advance()
            right = self._parse_additive()
            return BinaryConstraintNode(operator='=', left=left, right=right)
        elif self._match('NE'):
            self._advance()
            right = self._parse_additive()
            return BinaryConstraintNode(operator='!=', left=left, right=right)
        elif self._match('LT'):
            self._advance()
            right = self._parse_additive()
            return BinaryConstraintNode(operator='<', left=left, right=right)
        elif self._match('GT'):
            self._advance()
            right = self._parse_additive()
            return BinaryConstraintNode(operator='>', left=left, right=right)
        elif self._match('LE'):
            self._advance()
            right = self._parse_additive()
            return BinaryConstraintNode(operator='<=', left=left, right=right)
        elif self._match('GE'):
            self._advance()
            right = self._parse_additive()
            return BinaryConstraintNode(operator='>=', left=left, right=right)
        
        return left
    
    def _parse_additive(self) -> ConstraintExpression:
        """解析加减表达式"""
        left = self._parse_multiplicative()
        
        while self._match('PLUS') or self._match('MINUS'):
            op = '+' if self._advance()[0] == 'PLUS' else '-'
            right = self._parse_multiplicative()
            left = BinaryConstraintNode(operator=op, left=left, right=right)
        
        return left
    
    def _parse_multiplicative(self) -> ConstraintExpression:
        """解析乘除表达式"""
        left = self._parse_unary()
        
        while self._match('STAR') or self._match('SLASH') or self._match('PERCENT'):
            token_type = self._advance()[0]
            op = {'STAR': '*', 'SLASH': '/', 'PERCENT': '%'}[token_type]
            right = self._parse_unary()
            left = BinaryConstraintNode(operator=op, left=left, right=right)
        
        return left
    
    def _parse_unary(self) -> ConstraintExpression:
        """解析一元表达式"""
        if self._consume('NOT') or self._consume('BANG'):
            operand = self._parse_unary()
            return UnaryConstraintNode(operator='not', operand=operand)
        elif self._consume('MINUS'):
            operand = self._parse_unary()
            return UnaryConstraintNode(operator='-', operand=operand)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> ConstraintExpression:
        """解析基本表达式"""
        if self._match('NUMBER'):
            return LiteralConstraintNode(value=self._advance()[1])
        elif self._match('STRING'):
            return LiteralConstraintNode(value=self._advance()[1])
        elif self._match('TRUE'):
            self._advance()
            return LiteralConstraintNode(value=True)
        elif self._match('FALSE'):
            self._advance()
            return LiteralConstraintNode(value=False)
        elif self._match('NULL'):
            self._advance()
            return LiteralConstraintNode(value=None)
        elif self._match('THIS') or self._match('SELF'):
            self._advance()
            return IdentifierConstraintNode(name='this')
        elif self._match('IDENTIFIER'):
            name = self._advance()[1]
            
            # 检查是否是函数调用
            if self._consume('LPAREN'):
                args = []
                while not self._match('RPAREN'):
                    args.append(self._parse_constraint_expression())
                    self._consume('COMMA')
                self._expect('RPAREN')
                return CallConstraintNode(function=name, arguments=args)
            
            # 检查是否是路径表达式
            path = []
            while self._consume('DOT'):
                if self._match('IDENTIFIER'):
                    path.append(self._advance()[1])
                elif self._match('STRING'):
                    path.append(self._advance()[1])
                elif self._match('NUMBER'):
                    path.append(self._advance()[1])
            
            if path:
                return PathConstraintNode(base=name, path=path)
            
            return IdentifierConstraintNode(name=name)
        elif self._consume('LPAREN'):
            expr = self._parse_constraint_expression()
            self._expect('RPAREN')
            return expr
        else:
            raise USLParseError(f"Unexpected token in expression: {self._current()[0]}", self._location())
    
    def _parse_relation_definition(self) -> RelationDefinitionNode:
        """解析关系定义"""
        self._expect('RELATION')
        
        node = RelationDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        self._expect('COLON')
        
        # 解析关系类型
        relation_type = self._expect('IDENTIFIER')
        node.relation_type = relation_type
        
        self._expect('LPAREN')
        node.source = self._expect('IDENTIFIER')
        self._expect('COMMA')
        node.target = self._expect('IDENTIFIER')
        self._expect('RPAREN')
        
        # 解析属性
        if self._consume('LBRACE'):
            while not self._match('RBRACE'):
                key = self._expect('IDENTIFIER')
                self._expect('COLON')
                value = self._parse_value()
                node.attributes[key] = value
            self._expect('RBRACE')
        
        return node
    
    def _parse_operation_definition(self, op_type: str) -> OperationDefinitionNode:
        """解析操作定义"""
        self._advance()  # 消费操作类型关键字
        
        node = OperationDefinitionNode()
        node.location = self._location()
        node.operation_type = op_type
        node.name = self._expect('IDENTIFIER')
        
        # 解析泛型参数
        if self._consume('LT'):
            while not self._match('GT'):
                self._advance()  # 简化处理
            self._expect('GT')
        
        # 解析参数
        self._expect('LPAREN')
        while not self._match('RPAREN'):
            node.parameters.append(self._parse_parameter())
            self._consume('COMMA')
        self._expect('RPAREN')
        
        # 解析返回类型
        if self._consume('COLON'):
            node.return_type = self._parse_type_expression()
        
        return node
    
    def _parse_parameter(self) -> ParameterNode:
        """解析参数"""
        node = ParameterNode()
        node.location = self._location()
        
        node.name = self._expect('IDENTIFIER')
        
        # 检查可选参数标记
        if self._consume('QUESTION'):
            node.is_optional = True
        
        self._expect('COLON')
        node.type_expr = self._parse_type_expression()
        
        if self._consume('ASSIGN'):
            node.default_value = self._parse_value()
        
        return node
    
    def _parse_enum_definition(self) -> EnumDefinitionNode:
        """解析枚举定义"""
        self._expect('ENUM')
        
        node = EnumDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        self._expect('LBRACE')
        
        while not self._match('RBRACE'):
            member_name = self._expect('IDENTIFIER')
            member_value = None
            
            if self._consume('ASSIGN'):
                member_value = self._parse_value()
            
            node.members.append((member_name, member_value))
            self._consume('COMMA')
        
        self._expect('RBRACE')
        return node
    
    def _parse_interface_definition(self) -> InterfaceDefinitionNode:
        """解析接口定义（简化版）"""
        self._expect('INTERFACE')
        
        node = InterfaceDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        if self._consume('EXTENDS'):
            node.extends.append(self._expect('IDENTIFIER'))
            while self._consume('COMMA'):
                node.extends.append(self._expect('IDENTIFIER'))
        
        self._expect('LBRACE')
        
        while not self._match('RBRACE'):
            if self._match('FIELD'):
                node.fields.append(self._parse_field_definition())
            else:
                # 跳过未知内容
                self._advance()
        
        self._expect('RBRACE')
        return node
    
    def _parse_struct_definition(self) -> StructDefinitionNode:
        """解析结构定义"""
        self._expect('STRUCT')
        
        node = StructDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        self._expect('LBRACE')
        
        while not self._match('RBRACE'):
            node.fields.append(self._parse_field_definition())
        
        self._expect('RBRACE')
        return node
    
    def _parse_entity_definition(self) -> EntityDefinitionNode:
        """解析实体定义"""
        self._expect('ENTITY')
        
        node = EntityDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        self._expect('LBRACE')
        
        while not self._match('RBRACE'):
            if self._match('IDENTIFIER'):
                # 可能是identifier定义或字段
                if self._peek()[0] == 'COLON':
                    node.fields.append(self._parse_field_definition())
                else:
                    self._advance()
            elif self._match('FIELD'):
                node.fields.append(self._parse_field_definition())
            elif self._match('RELATION'):
                node.relations.append(self._parse_relation_definition())
            else:
                self._advance()
        
        self._expect('RBRACE')
        return node
    
    def _parse_value_definition(self) -> ValueDefinitionNode:
        """解析值类型定义"""
        self._expect('VALUE')
        
        node = ValueDefinitionNode()
        node.location = self._location()
        node.name = self._expect('IDENTIFIER')
        
        self._expect('LBRACE')
        
        while not self._match('RBRACE'):
            node.fields.append(self._parse_field_definition())
        
        self._expect('RBRACE')
        return node
    
    def _parse_metadata_definition(self) -> MetadataNode:
        """解析元数据定义"""
        self._expect('METADATA')
        
        node = MetadataNode()
        node.location = self._location()
        
        self._expect('LBRACE')
        
        while not self._match('RBRACE'):
            key = self._expect('IDENTIFIER')
            self._expect('COLON')
            value = self._parse_value()
            node.items[key] = value
        
        self._expect('RBRACE')
        return node
    
    def _parse_value(self) -> Any:
        """解析值"""
        if self._match('STRING'):
            return self._advance()[1]
        elif self._match('NUMBER'):
            return self._advance()[1]
        elif self._match('TRUE'):
            self._advance()
            return True
        elif self._match('FALSE'):
            self._advance()
            return False
        elif self._match('NULL'):
            self._advance()
            return None
        elif self._match('IDENTIFIER'):
            return self._advance()[1]
        elif self._match('LBRACKET'):
            # 数组
            self._advance()
            arr = []
            while not self._match('RBRACKET'):
                arr.append(self._parse_value())
                self._consume('COMMA')
            self._expect('RBRACKET')
            return arr
        elif self._match('LBRACE'):
            # 对象
            self._advance()
            obj = {}
            while not self._match('RBRACE'):
                key = self._expect('IDENTIFIER')
                self._expect('COLON')
                obj[key] = self._parse_value()
                self._consume('COMMA')
            self._expect('RBRACE')
            return obj
        else:
            raise USLParseError(f"Expected value, got {self._current()[0]}", self._location())


@dataclass
class ConstraintNode:
    """约束节点（简化）"""
    key: str = ""
    value: Any = None


# =============================================================================
# 4. 类型系统
# =============================================================================

class TypeChecker:
    """
    USL类型检查器
    
    实现USL类型系统的类型推导和类型检查。
    """
    
    def __init__(self):
        self.type_registry: Dict[str, TypeDefinitionNode] = {}
        self.errors: List[USLTypeError] = []
        self.warnings: List[str] = []
    
    def check(self, document: USLDocument) -> bool:
        """
        对USL文档执行类型检查
        
        Returns:
            bool: 类型检查是否通过
        """
        self.errors = []
        self.warnings = []
        
        if not document.schema:
            return True
        
        # 第一步：注册所有类型定义
        self._register_types(document.schema)
        
        # 第二步：检查类型定义
        self._check_schema(document.schema)
        
        return len(self.errors) == 0
    
    def _register_types(self, schema: SchemaNode) -> None:
        """注册所有类型定义"""
        for element in schema.elements:
            if isinstance(element, TypeDefinitionNode):
                self.type_registry[element.name] = element
            elif isinstance(element, EnumDefinitionNode):
                # 创建枚举类型定义
                type_def = TypeDefinitionNode(
                    name=element.name,
                    type_expr=PrimitiveTypeNode(USLType.STRING)
                )
                self.type_registry[element.name] = type_def
            elif isinstance(element, (StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode)):
                type_def = TypeDefinitionNode(
                    name=element.name,
                    type_expr=ReferenceTypeNode(name=element.name)
                )
                self.type_registry[element.name] = type_def
    
    def _check_schema(self, schema: SchemaNode) -> None:
        """检查Schema定义"""
        for element in schema.elements:
            self._check_element(element)
    
    def _check_element(self, element: SchemaElement) -> None:
        """检查Schema元素"""
        if isinstance(element, FieldDefinitionNode):
            self._check_field(element)
        elif isinstance(element, TypeDefinitionNode):
            self._check_type_definition(element)
        elif isinstance(element, (StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode)):
            self._check_composite_type(element)
        elif isinstance(element, OperationDefinitionNode):
            self._check_operation(element)
    
    def _check_field(self, field: FieldDefinitionNode) -> None:
        """检查字段定义"""
        # 检查类型是否有效
        field_type = self._resolve_type(field.type_expr)
        if field_type is None:
            self.errors.append(USLTypeError(
                f"Unknown type for field '{field.name}'",
                field.location
            ))
        
        # 检查默认值类型是否匹配
        if field.default_value is not None:
            if not self._check_value_type(field.default_value, field.type_expr):
                self.errors.append(USLTypeError(
                    f"Default value type mismatch for field '{field.name}'",
                    field.location
                ))
    
    def _check_type_definition(self, type_def: TypeDefinitionNode) -> None:
        """检查类型定义"""
        # 检查类型表达式是否有效
        resolved = self._resolve_type(type_def.type_expr)
        if resolved is None:
            self.errors.append(USLTypeError(
                f"Invalid type expression in definition of '{type_def.name}'",
                type_def.location
            ))
    
    def _check_composite_type(self, composite: Union[StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode]) -> None:
        """检查复合类型"""
        field_names: Set[str] = set()
        
        for field in composite.fields:
            # 检查重复字段名
            if field.name in field_names:
                self.errors.append(USLTypeError(
                    f"Duplicate field name '{field.name}' in '{composite.name}'",
                    field.location
                ))
            field_names.add(field.name)
            
            # 检查字段
            self._check_field(field)
    
    def _check_operation(self, operation: OperationDefinitionNode) -> None:
        """检查操作定义"""
        # 检查参数类型
        for param in operation.parameters:
            param_type = self._resolve_type(param.type_expr)
            if param_type is None:
                self.errors.append(USLTypeError(
                    f"Unknown type for parameter '{param.name}'",
                    param.location
                ))
        
        # 检查返回类型
        if operation.return_type:
            return_type = self._resolve_type(operation.return_type)
            if return_type is None:
                self.errors.append(USLTypeError(
                    f"Unknown return type for operation '{operation.name}'",
                    operation.location
                ))
    
    def _resolve_type(self, type_expr: TypeExpression) -> Optional[TypeDefinitionNode]:
        """解析类型表达式"""
        if isinstance(type_expr, PrimitiveTypeNode):
            # 原始类型总是有效
            return TypeDefinitionNode(name=type_expr.type_kind.value, type_expr=type_expr)
        
        elif isinstance(type_expr, ReferenceTypeNode):
            # 查找引用类型
            return self.type_registry.get(type_expr.name)
        
        elif isinstance(type_expr, OptionalTypeNode):
            # 可选类型，检查内部类型
            return self._resolve_type(type_expr.inner_type)
        
        elif isinstance(type_expr, ArrayTypeNode):
            # 数组类型，检查元素类型
            element_type = self._resolve_type(type_expr.element_type)
            if element_type is None:
                return None
            return TypeDefinitionNode(
                name=f"Array<{element_type.name}>",
                type_expr=type_expr
            )
        
        elif isinstance(type_expr, MapTypeNode):
            # 映射类型，检查键值类型
            key_type = self._resolve_type(type_expr.key_type)
            value_type = self._resolve_type(type_expr.value_type)
            if key_type is None or value_type is None:
                return None
            return TypeDefinitionNode(
                name=f"Map<{key_type.name},{value_type.name}>",
                type_expr=type_expr
            )
        
        elif isinstance(type_expr, GenericTypeNode):
            # 泛型类型，检查基础类型和类型参数
            base_type = self.type_registry.get(type_expr.base_type)
            if base_type is None:
                return None
            for type_arg in type_expr.type_args:
                if self._resolve_type(type_arg) is None:
                    return None
            return base_type
        
        elif isinstance(type_expr, UnionTypeNode):
            # 联合类型，检查所有成员类型
            for member_type in type_expr.types:
                if self._resolve_type(member_type) is None:
                    return None
            return TypeDefinitionNode(name="Union", type_expr=type_expr)
        
        return None
    
    def _check_value_type(self, value: Any, type_expr: TypeExpression) -> bool:
        """检查值是否与类型匹配"""
        if isinstance(type_expr, PrimitiveTypeNode):
            return self._check_primitive_value(value, type_expr.type_kind)
        
        elif isinstance(type_expr, OptionalTypeNode):
            if value is None:
                return True
            return self._check_value_type(value, type_expr.inner_type)
        
        elif isinstance(type_expr, ArrayTypeNode):
            if not isinstance(value, list):
                return False
            return all(
                self._check_value_type(item, type_expr.element_type)
                for item in value
            )
        
        return True  # 默认通过
    
    def _check_primitive_value(self, value: Any, type_kind: USLType) -> bool:
        """检查原始类型值"""
        if type_kind == USLType.STRING:
            return isinstance(value, str)
        elif type_kind in (USLType.INTEGER, USLType.INT8, USLType.INT16, 
                          USLType.INT32, USLType.INT64, USLType.INT128,
                          USLType.UNSIGNED, USLType.UINT8, USLType.UINT16,
                          USLType.UINT32, USLType.UINT64, USLType.UINT128):
            return isinstance(value, int)
        elif type_kind in (USLType.FLOAT, USLType.FLOAT32, USLType.FLOAT64, USLType.FLOAT128):
            return isinstance(value, (int, float))
        elif type_kind in (USLType.BOOLEAN, USLType.BOOL):
            return isinstance(value, bool)
        elif type_kind == USLType.ANY:
            return True
        return True


# =============================================================================
# 5. 约束验证器
# =============================================================================

class ConstraintValidator:
    """
    USL约束验证器
    
    验证USL Schema定义的所有约束。
    """
    
    def __init__(self):
        self.errors: List[USLValidationError] = []
        self.warnings: List[str] = []
        self.custom_constraints: Dict[str, ConstraintDefinitionNode] = {}
    
    def validate(self, document: USLDocument) -> bool:
        """
        验证USL文档
        
        Returns:
            bool: 验证是否通过
        """
        self.errors = []
        self.warnings = []
        
        if not document.schema:
            return True
        
        # 注册自定义约束
        self._register_constraints(document.schema)
        
        # 验证Schema元素
        self._validate_schema(document.schema)
        
        return len(self.errors) == 0
    
    def _register_constraints(self, schema: SchemaNode) -> None:
        """注册自定义约束"""
        for element in schema.elements:
            if isinstance(element, ConstraintDefinitionNode):
                self.custom_constraints[element.name] = element
    
    def _validate_schema(self, schema: SchemaNode) -> None:
        """验证Schema定义"""
        for element in schema.elements:
            self._validate_element(element)
    
    def _validate_element(self, element: SchemaElement) -> None:
        """验证Schema元素"""
        if isinstance(element, FieldDefinitionNode):
            self._validate_field_constraints(element)
        elif isinstance(element, (StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode)):
            self._validate_composite_constraints(element)
    
    def _validate_field_constraints(self, field: FieldDefinitionNode) -> None:
        """验证字段约束"""
        for constraint in field.constraints:
            # 这里可以执行更复杂的约束验证
            pass
    
    def _validate_composite_constraints(self, composite: Union[StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode]) -> None:
        """验证复合类型的约束"""
        # 验证字段间的约束关系
        pass
    
    def validate_data(self, data: Any, schema: SchemaNode, type_name: str) -> bool:
        """
        验证数据是否符合Schema定义
        
        Args:
            data: 要验证的数据
            schema: Schema定义
            type_name: 类型名称
            
        Returns:
            bool: 验证是否通过
        """
        # 查找类型定义
        type_def = None
        for element in schema.elements:
            if isinstance(element, (StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode)):
                if element.name == type_name:
                    type_def = element
                    break
        
        if type_def is None:
            self.errors.append(USLValidationError(f"Type '{type_name}' not found"))
            return False
        
        return self._validate_data_against_type(data, type_def)
    
    def _validate_data_against_type(self, data: Any, type_def: Union[StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode]) -> bool:
        """验证数据与类型定义"""
        if not isinstance(data, dict):
            self.errors.append(USLValidationError(
                f"Expected object for type '{type_def.name}', got {type(data).__name__}"
            ))
            return False
        
        valid = True
        
        for field in type_def.fields:
            field_value = data.get(field.name)
            
            # 检查必需字段
            if 'required' in field.modifiers and field_value is None:
                self.errors.append(USLValidationError(
                    f"Required field '{field.name}' is missing"
                ))
                valid = False
                continue
            
            if field_value is not None:
                # 验证字段值类型
                if not self._validate_value_type(field_value, field.type_expr, field.name):
                    valid = False
                
                # 验证字段约束
                for constraint in field.constraints:
                    if not self._validate_constraint(field_value, constraint, data):
                        valid = False
        
        return valid
    
    def _validate_value_type(self, value: Any, type_expr: TypeExpression, field_name: str) -> bool:
        """验证值与类型表达式"""
        if isinstance(type_expr, PrimitiveTypeNode):
            return self._validate_primitive(value, type_expr.type_kind, field_name)
        elif isinstance(type_expr, OptionalTypeNode):
            if value is None:
                return True
            return self._validate_value_type(value, type_expr.inner_type, field_name)
        elif isinstance(type_expr, ArrayTypeNode):
            if not isinstance(value, list):
                self.errors.append(USLValidationError(
                    f"Field '{field_name}' expected array, got {type(value).__name__}"
                ))
                return False
            return all(
                self._validate_value_type(item, type_expr.element_type, f"{field_name}[]")
                for item in value
            )
        elif isinstance(type_expr, MapTypeNode):
            if not isinstance(value, dict):
                self.errors.append(USLValidationError(
                    f"Field '{field_name}' expected map, got {type(value).__name__}"
                ))
                return False
            return True
        elif isinstance(type_expr, ReferenceTypeNode):
            # 引用类型验证需要类型注册表
            return True
        
        return True
    
    def _validate_primitive(self, value: Any, type_kind: USLType, field_name: str) -> bool:
        """验证原始类型"""
        type_checks = {
            USLType.STRING: lambda v: isinstance(v, str),
            USLType.INTEGER: lambda v: isinstance(v, int) and not isinstance(v, bool),
            USLType.FLOAT: lambda v: isinstance(v, (int, float)),
            USLType.BOOLEAN: lambda v: isinstance(v, bool),
            USLType.UUID: lambda v: isinstance(v, str) and bool(re.match(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v, re.I
            )),
            USLType.EMAIL: lambda v: isinstance(v, str) and bool(re.match(
                r'^[\w\.-]+@[\w\.-]+\.\w+$', v
            )),
            USLType.URL: lambda v: isinstance(v, str) and v.startswith(('http://', 'https://')),
            USLType.ANY: lambda v: True,
        }
        
        check = type_checks.get(type_kind)
        if check and not check(value):
            self.errors.append(USLValidationError(
                f"Field '{field_name}' expected {type_kind.value}, got {type(value).__name__}"
            ))
            return False
        
        return True
    
    def _validate_constraint(self, value: Any, constraint: ConstraintExpression, context: Any) -> bool:
        """验证约束表达式"""
        # 简化的约束验证实现
        return True


# =============================================================================
# 6. 代码生成器
# =============================================================================

class CodeGenerator(ABC):
    """代码生成器基类"""
    
    @abstractmethod
    def generate(self, document: USLDocument, options: Dict[str, Any] = None) -> str:
        """生成代码"""
        pass


class JSONSchemaGenerator(CodeGenerator):
    """JSON Schema生成器"""
    
    def __init__(self):
        self.definitions: Dict[str, dict] = {}
    
    def generate(self, document: USLDocument, options: Dict[str, Any] = None) -> str:
        """生成JSON Schema"""
        options = options or {}
        
        if not document.schema:
            return json.dumps({})
        
        schema = document.schema
        
        # 构建JSON Schema
        json_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": options.get("id", f"urn:usl:{schema.name}"),
        }
        
        if schema.version:
            json_schema["$version"] = schema.version
        
        # 处理元数据
        if schema.metadata:
            if schema.metadata.items.get("title"):
                json_schema["title"] = schema.metadata.items["title"]
            if schema.metadata.items.get("description"):
                json_schema["description"] = schema.metadata.items["description"]
        
        # 收集所有类型定义
        self.definitions = {}
        for element in schema.elements:
            if isinstance(element, (StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode)):
                self.definitions[element.name] = self._convert_type(element)
            elif isinstance(element, EnumDefinitionNode):
                self.definitions[element.name] = self._convert_enum(element)
        
        if self.definitions:
            json_schema["$defs"] = self.definitions
        
        # 如果只有一个主类型，提升到根
        if len(self.definitions) == 1:
            main_type = list(self.definitions.values())[0]
            json_schema.update(main_type)
        
        indent = options.get("indent", 2)
        return json.dumps(json_schema, indent=indent, ensure_ascii=False)
    
    def _convert_type(self, type_def: Union[StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode]) -> dict:
        """转换类型定义"""
        result = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for field in type_def.fields:
            result["properties"][field.name] = self._convert_field(field)
            if "required" in field.modifiers or field.default_value is None:
                result["required"].append(field.name)
        
        return result
    
    def _convert_field(self, field: FieldDefinitionNode) -> dict:
        """转换字段定义"""
        result = self._convert_type_expression(field.type_expr)
        
        # 添加约束
        for constraint in field.constraints:
            self._apply_constraint(result, constraint)
        
        # 添加默认值
        if field.default_value is not None:
            result["default"] = field.default_value
        
        # 添加描述
        if field.description:
            result["description"] = field.description
        
        # 添加示例
        if field.examples:
            if len(field.examples) == 1:
                result["examples"] = [field.examples[0]]
            else:
                result["examples"] = field.examples
        
        return result
    
    def _convert_type_expression(self, type_expr: TypeExpression) -> dict:
        """转换类型表达式"""
        if isinstance(type_expr, PrimitiveTypeNode):
            return self._convert_primitive(type_expr)
        
        elif isinstance(type_expr, OptionalTypeNode):
            inner = self._convert_type_expression(type_expr.inner_type)
            return {"anyOf": [inner, {"type": "null"}]}
        
        elif isinstance(type_expr, ArrayTypeNode):
            return {
                "type": "array",
                "items": self._convert_type_expression(type_expr.element_type)
            }
        
        elif isinstance(type_expr, MapTypeNode):
            return {
                "type": "object",
                "additionalProperties": self._convert_type_expression(type_expr.value_type)
            }
        
        elif isinstance(type_expr, ReferenceTypeNode):
            return {"$ref": f"#/$defs/{type_expr.name}"}
        
        elif isinstance(type_expr, UnionTypeNode):
            return {"anyOf": [self._convert_type_expression(t) for t in type_expr.types]}
        
        return {"type": "object"}
    
    def _convert_primitive(self, type_node: PrimitiveTypeNode) -> dict:
        """转换原始类型"""
        type_mapping = {
            USLType.STRING: {"type": "string"},
            USLType.TEXT: {"type": "string"},
            USLType.CHAR: {"type": "string", "minLength": 1, "maxLength": 1},
            USLType.INTEGER: {"type": "integer"},
            USLType.INT8: {"type": "integer", "minimum": -128, "maximum": 127},
            USLType.INT16: {"type": "integer", "minimum": -32768, "maximum": 32767},
            USLType.INT32: {"type": "integer", "minimum": -2147483648, "maximum": 2147483647},
            USLType.INT64: {"type": "integer"},
            USLType.UNSIGNED: {"type": "integer", "minimum": 0},
            USLType.UINT8: {"type": "integer", "minimum": 0, "maximum": 255},
            USLType.UINT16: {"type": "integer", "minimum": 0, "maximum": 65535},
            USLType.UINT32: {"type": "integer", "minimum": 0, "maximum": 4294967295},
            USLType.UINT64: {"type": "integer", "minimum": 0},
            USLType.FLOAT: {"type": "number"},
            USLType.FLOAT32: {"type": "number"},
            USLType.FLOAT64: {"type": "number"},
            USLType.DECIMAL: {"type": "number"},
            USLType.BOOLEAN: {"type": "boolean"},
            USLType.BOOL: {"type": "boolean"},
            USLType.DATE: {"type": "string", "format": "date"},
            USLType.DATETIME: {"type": "string", "format": "date-time"},
            USLType.TIMESTAMP: {"type": "integer"},
            USLType.UUID: {"type": "string", "format": "uuid"},
            USLType.EMAIL: {"type": "string", "format": "email"},
            USLType.URL: {"type": "string", "format": "uri"},
            USLType.URI: {"type": "string", "format": "uri"},
            USLType.IPV4: {"type": "string", "format": "ipv4"},
            USLType.IPV6: {"type": "string", "format": "ipv6"},
            USLType.BINARY: {"type": "string", "contentEncoding": "base64"},
            USLType.BASE64: {"type": "string", "contentEncoding": "base64"},
            USLType.ANY: {},
        }
        
        result = type_mapping.get(type_node.type_kind, {"type": "string"})
        
        # 添加精度信息
        if type_node.type_kind == USLType.DECIMAL:
            if type_node.precision is not None:
                result["multipleOf"] = 10 ** -type_node.scale if type_node.scale else 1
        
        return result
    
    def _apply_constraint(self, schema: dict, constraint: ConstraintExpression) -> None:
        """应用约束到JSON Schema"""
        # 简化的约束应用
        pass
    
    def _convert_enum(self, enum_def: EnumDefinitionNode) -> dict:
        """转换枚举定义"""
        values = []
        for member, value in enum_def.members:
            if value is not None:
                values.append(value)
            else:
                values.append(member)
        
        return {"enum": values}


class OpenAPIGenerator(CodeGenerator):
    """OpenAPI生成器"""
    
    def __init__(self):
        self.schemas: Dict[str, dict] = {}
        self.paths: Dict[str, dict] = {}
    
    def generate(self, document: USLDocument, options: Dict[str, Any] = None) -> str:
        """生成OpenAPI规范"""
        options = options or {}
        
        if not document.schema:
            return json.dumps({})
        
        schema = document.schema
        
        # 构建OpenAPI规范
        openapi = {
            "openapi": "3.1.0",
            "info": {
                "title": schema.metadata.items.get("title", schema.name) if schema.metadata else schema.name,
                "version": schema.version or "1.0.0"
            },
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        # 添加服务器信息
        if schema.metadata and schema.metadata.items.get("servers"):
            openapi["servers"] = schema.metadata.items["servers"]
        
        # 收集Schema定义
        json_gen = JSONSchemaGenerator()
        for element in schema.elements:
            if isinstance(element, (StructDefinitionNode, EntityDefinitionNode, ValueDefinitionNode)):
                openapi["components"]["schemas"][element.name] = json_gen._convert_type(element)
            elif isinstance(element, EnumDefinitionNode):
                openapi["components"]["schemas"][element.name] = json_gen._convert_enum(element)
        
        # 生成路径
        for element in schema.elements:
            if isinstance(element, OperationDefinitionNode):
                self._add_operation(openapi["paths"], element)
        
        indent = options.get("indent", 2)
        return json.dumps(openapi, indent=indent, ensure_ascii=False)
    
    def _add_operation(self, paths: Dict[str, dict], operation: OperationDefinitionNode) -> None:
        """添加操作到路径"""
        path_key = f"/{operation.name}"
        
        method_map = {
            'query': 'get',
            'mutation': 'post',
            'subscription': 'post',
            'rpc': 'post'
        }
        
        method = method_map.get(operation.operation_type, 'post')
        
        operation_spec = {
            "operationId": operation.name,
            "parameters": [],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": self._convert_return_type(operation.return_type)
                        }
                    }
                }
            }
        }
        
        # 添加参数
        for param in operation.parameters:
            param_spec = {
                "name": param.name,
                "in": "query" if operation.operation_type == 'query' else "path",
                "required": not param.is_optional,
                "schema": self._convert_parameter_type(param.type_expr)
            }
            operation_spec["parameters"].append(param_spec)
        
        if path_key not in paths:
            paths[path_key] = {}
        paths[path_key][method] = operation_spec
    
    def _convert_return_type(self, type_expr: Optional[TypeExpression]) -> dict:
        """转换返回类型"""
        if type_expr is None:
            return {"type": "object"}
        
        json_gen = JSONSchemaGenerator()
        return json_gen._convert_type_expression(type_expr)
    
    def _convert_parameter_type(self, type_expr: TypeExpression) -> dict:
        """转换参数类型"""
        json_gen = JSONSchemaGenerator()
        return json_gen._convert_type_expression(type_expr)


class GraphQLGenerator(CodeGenerator):
    """GraphQL Schema生成器"""
    
    def generate(self, document: USLDocument, options: Dict[str, Any] = None) -> str:
        """生成GraphQL Schema"""
        if not document.schema:
            return ""
        
        schema = document.schema
        lines = []
        
        # 生成类型定义
        for element in schema.elements:
            if isinstance(element, EnumDefinitionNode):
                lines.append(self._generate_enum(element))
            elif isinstance(element, (StructDefinitionNode, EntityDefinitionNode)):
                lines.append(self._generate_object_type(element))
        
        # 生成Query类型
        queries = [e for e in schema.elements if isinstance(e, OperationDefinitionNode) and e.operation_type == 'query']
        if queries:
            lines.append("type Query {")
            for query in queries:
                lines.append(self._generate_field(query))
            lines.append("}")
        
        # 生成Mutation类型
        mutations = [e for e in schema.elements if isinstance(e, OperationDefinitionNode) and e.operation_type == 'mutation']
        if mutations:
            lines.append("type Mutation {")
            for mutation in mutations:
                lines.append(self._generate_field(mutation))
            lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_enum(self, enum_def: EnumDefinitionNode) -> str:
        """生成枚举类型"""
        lines = [f"enum {enum_def.name} {{"]
        for member, _ in enum_def.members:
            lines.append(f"  {member}")
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_object_type(self, type_def: Union[StructDefinitionNode, EntityDefinitionNode]) -> str:
        """生成对象类型"""
        lines = [f"type {type_def.name} {{"]
        for field in type_def.fields:
            graphql_type = self._convert_to_graphql_type(field.type_expr)
            lines.append(f"  {field.name}: {graphql_type}")
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_field(self, operation: OperationDefinitionNode) -> str:
        """生成GraphQL字段"""
        params = ", ".join([
            f"{p.name}: {self._convert_to_graphql_type(p.type_expr)}"
            for p in operation.parameters
        ])
        return_type = self._convert_to_graphql_type(operation.return_type) if operation.return_type else "String"
        return f"  {operation.name}({params}): {return_type}"
    
    def _convert_to_graphql_type(self, type_expr: Optional[TypeExpression]) -> str:
        """转换为GraphQL类型"""
        if type_expr is None:
            return "String"
        
        if isinstance(type_expr, PrimitiveTypeNode):
            mapping = {
                USLType.STRING: "String",
                USLType.INTEGER: "Int",
                USLType.FLOAT: "Float",
                USLType.BOOLEAN: "Boolean",
                USLType.ID: "ID",
            }
            return mapping.get(type_expr.type_kind, "String")
        
        elif isinstance(type_expr, OptionalTypeNode):
            inner = self._convert_to_graphql_type(type_expr.inner_type)
            return inner  # GraphQL默认可空
        
        elif isinstance(type_expr, ArrayTypeNode):
            inner = self._convert_to_graphql_type(type_expr.element_type)
            return f"[{inner}]"
        
        elif isinstance(type_expr, ReferenceTypeNode):
            return type_expr.name
        
        return "String"


# =============================================================================
# 7. USL转换器
# =============================================================================

class USLTransformer:
    """
    USL转换器
    
    负责将USL文档转换为目标格式。
    """
    
    def __init__(self):
        self.generators: Dict[str, CodeGenerator] = {
            'json-schema': JSONSchemaGenerator(),
            'openapi': OpenAPIGenerator(),
            'graphql': GraphQLGenerator(),
        }
    
    def transform(
        self, 
        document: USLDocument, 
        target_format: str,
        options: Dict[str, Any] = None
    ) -> str:
        """
        转换USL文档到目标格式
        
        Args:
            document: USL文档
            target_format: 目标格式（json-schema, openapi, graphql等）
            options: 转换选项
            
        Returns:
            str: 生成的代码
            
        Raises:
            ValueError: 不支持的目标格式
        """
        if target_format not in self.generators:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        generator = self.generators[target_format]
        return generator.generate(document, options)
    
    def register_generator(self, format_name: str, generator: CodeGenerator) -> None:
        """注册新的代码生成器"""
        self.generators[format_name] = generator


# =============================================================================
# 8. 解析缓存
# =============================================================================

class USLParserCache:
    """
    USL解析缓存系统
    
    提供增量解析和缓存功能。
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path('.usl_cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache: Dict[str, USLDocument] = {}
    
    def get_or_parse(self, filepath: Path, parser: USLParser) -> USLDocument:
        """
        获取或解析USL文档
        
        使用内容哈希进行缓存验证。
        """
        content = filepath.read_bytes()
        content_hash = hashlib.sha256(content).hexdigest()
        cache_key = f"{filepath}:{content_hash}"
        
        # 检查内存缓存
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # 检查磁盘缓存
        cache_file = self.cache_dir / f"{content_hash}.pickle"
        if cache_file.exists():
            import pickle
            with open(cache_file, 'rb') as f:
                doc = pickle.load(f)
            self.memory_cache[cache_key] = doc
            return doc
        
        # 解析并缓存
        doc = parser.parse_file(filepath)
        
        # 保存到磁盘缓存
        import pickle
        with open(cache_file, 'wb') as f:
            pickle.dump(doc, f)
        
        self.memory_cache[cache_key] = doc
        return doc
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob('*.pickle'):
            cache_file.unlink()


# =============================================================================
# 9. 测试套件
# =============================================================================

class USLTestSuite:
    """
    USL测试套件
    
    提供USL实现的测试用例。
    """
    
    @staticmethod
    def get_parser_tests() -> List[Tuple[str, str]]:
        """
        获取解析器测试用例
        
        Returns:
            List[Tuple[str, str]]: (描述, USL代码) 列表
        """
        return [
            ("简单Schema", """
schema User {
    field id: UUID
    field name: String
    field email: Email
}
"""),
            ("带约束的Schema", """
schema Product {
    field id: UUID
    field name: String {
        constraint: { minLength: 1, maxLength: 200 }
    }
    field price: Decimal {
        constraint: { min: 0 }
    }
}
"""),
            ("复杂Schema", """
schema Order v1.0 {
    metadata {
        title: "Order Schema"
        version: "1.0.0"
    }
    
    entity User {
        field id: UUID
        field email: Email
        relation orders: has_many(Order)
    }
    
    entity Order {
        field id: UUID
        field total: Decimal
        relation user: belongs_to(User)
    }
    
    query getOrder(id: UUID): Order
    mutation createOrder(input: OrderInput): Order
}
"""),
            ("枚举定义", """
schema StatusEnum {
    enum Status {
        pending, active, completed, cancelled
    }
}
"""),
            ("泛型类型", """
schema GenericTypes {
    type Container<T> {
        field value: T
        field metadata: Map<String, Any>
    }
    
    field items: Array<String>
    field lookup: Map<String, Integer>
}
"""),
        ]
    
    @staticmethod
    def get_validation_tests() -> List[Tuple[str, str, Any, bool]]:
        """
        获取验证测试用例
        
        Returns:
            List[Tuple[str, str, Any, bool]]: (描述, Schema代码, 测试数据, 期望结果) 列表
        """
        return [
            (
                "有效的用户数据",
                """
schema UserSchema {
    struct User {
        field id: UUID
        field name: String
        field age: Integer
    }
}
""",
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "John Doe",
                    "age": 30
                },
                True
            ),
            (
                "无效的UUID格式",
                """
schema UserSchema {
    struct User {
        field id: UUID
        field name: String
    }
}
""",
                {
                    "id": "not-a-uuid",
                    "name": "John Doe"
                },
                False
            ),
            (
                "缺少必需字段",
                """
schema UserSchema {
    struct User {
        field id: UUID
        field name: String
    }
}
""",
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000"
                    # 缺少name字段
                },
                False
            ),
            (
                "数组类型验证",
                """
schema OrderSchema {
    struct Order {
        field id: UUID
        field items: Array<String>
    }
}
""",
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "items": ["item1", "item2", "item3"]
                },
                True
            ),
        ]
    
    @staticmethod
    def get_transformation_tests() -> List[Tuple[str, str, str, List[str]]]:
        """
        获取转换测试用例
        
        Returns:
            List[Tuple[str, str, str, List[str]]]: (描述, USL代码, 目标格式, 期望包含) 列表
        """
        return [
            (
                "JSON Schema转换",
                """
schema User {
    field id: UUID
    field name: String
    field age: Integer
}
""",
                "json-schema",
                ['"type": "object"', '"properties"', '"id"', '"name"', '"age"']
            ),
            (
                "OpenAPI转换",
                """
schema UserAPI v1.0 {
    metadata {
        title: "User API"
    }
    
    struct User {
        field id: UUID
        field name: String
    }
    
    query getUser(id: UUID): User
}
""",
                "openapi",
                ['"openapi":', '"paths"', '"/getUser"', '"components"', '"schemas"']
            ),
            (
                "GraphQL转换",
                """
schema UserSchema {
    entity User {
        field id: UUID
        field name: String
    }
    
    query getUser(id: UUID): User
}
""",
                "graphql",
                ['type User', 'id:', 'name:', 'type Query']
            ),
        ]
    
    @classmethod
    def run_tests(cls, verbose: bool = False) -> bool:
        """
        运行所有测试
        
        Returns:
            bool: 所有测试是否通过
        """
        parser = USLParser()
        type_checker = TypeChecker()
        validator = ConstraintValidator()
        transformer = USLTransformer()
        
        all_passed = True
        
        # 解析测试
        print("=" * 60)
        print("Running Parser Tests")
        print("=" * 60)
        
        for desc, code in cls.get_parser_tests():
            try:
                doc = parser.parse(code)
                if verbose:
                    print(f"✓ {desc}")
            except Exception as e:
                print(f"✗ {desc}: {e}")
                all_passed = False
        
        # 验证测试
        print("\n" + "=" * 60)
        print("Running Validation Tests")
        print("=" * 60)
        
        for desc, code, data, expected in cls.get_validation_tests():
            try:
                doc = parser.parse(code)
                validator.errors = []
                result = validator.validate_data(data, doc.schema, "User")
                actual = result and len(validator.errors) == 0
                
                if actual == expected:
                    if verbose:
                        print(f"✓ {desc}")
                else:
                    print(f"✗ {desc}: expected {expected}, got {actual}")
                    all_passed = False
            except Exception as e:
                print(f"✗ {desc}: {e}")
                all_passed = False
        
        # 转换测试
        print("\n" + "=" * 60)
        print("Running Transformation Tests")
        print("=" * 60)
        
        for desc, code, format_name, expected_parts in cls.get_transformation_tests():
            try:
                doc = parser.parse(code)
                output = transformer.transform(doc, format_name)
                
                missing = [part for part in expected_parts if part not in output]
                if not missing:
                    if verbose:
                        print(f"✓ {desc}")
                else:
                    print(f"✗ {desc}: missing {missing}")
                    all_passed = False
            except Exception as e:
                print(f"✗ {desc}: {e}")
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("All tests passed! ✓")
        else:
            print("Some tests failed! ✗")
        print("=" * 60)
        
        return all_passed


# =============================================================================
# 10. 主函数和CLI
# =============================================================================

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python standard_reference_implementation.py <command> [args]")
        print("\nCommands:")
        print("  parse <file.usl>        Parse USL file and print AST")
        print("  validate <file.usl>     Validate USL file")
        print("  transform <file.usl> <format>  Transform to target format")
        print("  test                    Run test suite")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        USLTestSuite.run_tests(verbose=True)
    
    elif command == "parse":
        if len(sys.argv) < 3:
            print("Error: Missing file argument")
            return
        
        filepath = Path(sys.argv[2])
        parser = USLParser()
        
        try:
            doc = parser.parse_file(filepath)
            print(f"Parsed: {filepath}")
            if doc.schema:
                print(f"Schema: {doc.schema.name}")
                print(f"Elements: {len(doc.schema.elements)}")
        except USLError as e:
            print(f"Error: {e}")
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Error: Missing file argument")
            return
        
        filepath = Path(sys.argv[2])
        parser = USLParser()
        type_checker = TypeChecker()
        
        try:
            doc = parser.parse_file(filepath)
            if type_checker.check(doc):
                print("✓ Type check passed")
            else:
                print("✗ Type check failed")
                for error in type_checker.errors:
                    print(f"  - {error}")
        except USLError as e:
            print(f"Error: {e}")
    
    elif command == "transform":
        if len(sys.argv) < 4:
            print("Error: Missing file or format argument")
            return
        
        filepath = Path(sys.argv[2])
        target_format = sys.argv[3]
        
        parser = USLParser()
        transformer = USLTransformer()
        
        try:
            doc = parser.parse_file(filepath)
            output = transformer.transform(doc, target_format)
            print(output)
        except USLError as e:
            print(f"Error: {e}")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
