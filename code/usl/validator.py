"""
USL验证器

实现类型检查和约束验证
"""

from typing import Dict, Any, List, Optional


class USLTypeChecker:
    """USL类型检查器"""
    
    def __init__(self, ast: Dict[str, Any]):
        """
        初始化类型检查器
        
        Args:
            ast: USL AST
        """
        self.ast = ast
        self.type_registry = {}
        self.errors = []
    
    def check(self) -> bool:
        """
        执行类型检查
        
        Returns:
            是否通过检查
        """
        self.errors = []
        
        # 1. 注册所有类型
        self._register_types()
        
        # 2. 检查字段类型
        self._check_fields()
        
        # 3. 检查约束
        self._check_constraints()
        
        # 4. 检查关系
        self._check_relations()
        
        return len(self.errors) == 0
    
    def _register_types(self):
        """注册所有类型定义"""
        if 'body' in self.ast and 'types' in self.ast['body']:
            for type_def in self.ast['body']['types']:
                type_name = type_def.get('name')
                if type_name:
                    self.type_registry[type_name] = type_def
    
    def _check_fields(self):
        """检查字段类型"""
        if 'body' in self.ast and 'fields' in self.ast['body']:
            for field in self.ast['body']['fields']:
                type_spec = field.get('type_specifier')
                if type_spec:
                    if not self._is_valid_type(type_spec):
                        self.errors.append(
                            f"字段 {field.get('name')} 的类型无效: {type_spec}"
                        )
    
    def _check_constraints(self):
        """检查约束"""
        if 'body' in self.ast and 'fields' in self.ast['body']:
            for field in self.ast['body']['fields']:
                constraint = field.get('constraint')
                if constraint:
                    self._validate_constraint(field, constraint)
    
    def _check_relations(self):
        """检查关系"""
        if 'body' in self.ast and 'relations' in self.ast['body']:
            for relation in self.ast['body']['relations']:
                source = relation.get('source')
                target = relation.get('target')
                
                # 检查源和目标实体是否存在
                if not self._entity_exists(source):
                    self.errors.append(f"关系源实体不存在: {source}")
                if not self._entity_exists(target):
                    self.errors.append(f"关系目标实体不存在: {target}")
    
    def _is_valid_type(self, type_spec: Dict[str, Any]) -> bool:
        """检查类型是否有效"""
        if type_spec.get('type') == 'primitive':
            return True
        elif type_spec.get('type') == 'reference':
            ref_name = type_spec.get('name')
            return ref_name in self.type_registry
        elif type_spec.get('type') in ['array', 'map', 'object']:
            return True
        return False
    
    def _validate_constraint(self, field: Dict[str, Any], constraint: Dict[str, Any]):
        """验证约束"""
        field_type = field.get('type_specifier', {})
        
        # 检查数值约束是否适用于数值类型
        if 'min' in constraint or 'max' in constraint:
            if field_type.get('type') != 'primitive' or field_type.get('name') not in ['Integer', 'Float', 'Decimal']:
                self.errors.append(f"字段 {field.get('name')} 的min/max约束仅适用于数值类型")
        
        # 检查长度约束是否适用于字符串类型
        if 'minLength' in constraint or 'maxLength' in constraint:
            if field_type.get('type') != 'primitive' or field_type.get('name') != 'String':
                self.errors.append(f"字段 {field.get('name')} 的长度约束仅适用于字符串类型")
    
    def _entity_exists(self, entity_name: str) -> bool:
        """检查实体是否存在"""
        # 简化实现：检查是否在字段或类型中
        if 'body' in self.ast:
            if 'fields' in self.ast['body']:
                for field in self.ast['body']['fields']:
                    if field.get('name') == entity_name:
                        return True
            if 'types' in self.ast['body']:
                for type_def in self.ast['body']['types']:
                    if type_def.get('name') == entity_name:
                        return True
        return False
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors


class USLValidator:
    """USL验证器（组合类型检查和约束验证）"""
    
    def __init__(self, ast: Dict[str, Any]):
        """
        初始化验证器
        
        Args:
            ast: USL AST
        """
        self.ast = ast
        self.type_checker = USLTypeChecker(ast)
    
    def validate(self) -> Dict[str, Any]:
        """
        执行完整验证
        
        Returns:
            验证结果字典
        """
        type_check_passed = self.type_checker.check()
        
        return {
            'valid': type_check_passed,
            'errors': self.type_checker.get_errors(),
            'warnings': []
        }
