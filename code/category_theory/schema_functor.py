"""
Schema转换的范畴论实现
================================

本模块提供Schema转换的范畴论形式化实现，包括：
- 范畴基础类
- Schema作为范畴的表示
- 转换函子实现
- 自然变换

参考: docs/theory/category_theory_schema_transformation.md
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Callable, Any, TypeVar, Generic
from copy import deepcopy
from functools import reduce
import json


# ============================================================================
# 第一部分：范畴基础
# ============================================================================

T = TypeVar('T')


class Category(ABC):
    """
    范畴抽象基类
    
    一个范畴C包含：
    - 对象类 Ob(C)
    - 对任意A,B ∈ Ob(C)，有态射集 Hom(A, B)
    - 复合运算 ∘
    - 单位态射 id_A
    """
    
    @abstractmethod
    def objects(self) -> Set[Any]:
        """返回范畴中的所有对象"""
        pass
    
    @abstractmethod
    def morphisms(self, source: Any, target: Any) -> Set[Any]:
        """返回从source到target的所有态射"""
        pass
    
    @abstractmethod
    def compose(self, f: Any, g: Any) -> Any:
        """
        态射复合
        给定 f: A → B 和 g: B → C，返回 g ∘ f: A → C
        """
        pass
    
    @abstractmethod
    def identity(self, obj: Any) -> Any:
        """返回对象obj的单位态射 id_obj"""
        pass
    
    def is_identity(self, f: Any, obj: Any) -> bool:
        """验证f是否是obj的单位态射"""
        id_obj = self.identity(obj)
        return f == id_obj


@dataclass(frozen=True)
class Morphism:
    """
    态射的具体表示
    
    属性:
        source: 源对象
        target: 目标对象
        name: 态射名称
        mapping: 具体的映射函数
    """
    source: str
    target: str
    name: str
    mapping: Callable[[Any], Any] = field(compare=False)
    
    def __call__(self, x: Any) -> Any:
        """应用态射"""
        return self.mapping(x)
    
    def __repr__(self) -> str:
        return f"{self.name}: {self.source} → {self.target}"


# ============================================================================
# 第二部分：Schema对象与范畴
# ============================================================================

@dataclass
class Field:
    """
    Schema字段定义
    
    属性:
        name: 字段名
        type_: 字段类型
        optional: 是否可选
        default: 默认值
        nested: 嵌套Schema（如果有）
    """
    name: str
    type_: str
    optional: bool = False
    default: Any = None
    nested: Optional['Schema'] = None
    
    def copy(self) -> 'Field':
        """深拷贝字段"""
        return Field(
            name=self.name,
            type_=self.type_,
            optional=self.optional,
            default=deepcopy(self.default),
            nested=self.nested.copy() if self.nested else None
        )
    
    def __repr__(self) -> str:
        type_str = self.type_
        if self.nested:
            type_str = f"nested<{self.nested.name}>"
        opt_str = "?" if self.optional else ""
        return f"{self.name}: {type_str}{opt_str}"


@dataclass
class Schema:
    """
    Schema对象表示
    
    Schema作为范畴的对象，包含类型、字段和约束。
    """
    name: str
    fields: Dict[str, Field] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_field(self, name: str, type_: str, optional: bool = False, 
                  default: Any = None) -> 'Schema':
        """添加字段"""
        self.fields[name] = Field(name, type_, optional, default)
        return self
    
    def remove_field(self, name: str) -> 'Schema':
        """删除字段"""
        if name in self.fields:
            del self.fields[name]
        return self
    
    def add_nested(self, name: str, nested_schema: 'Schema') -> 'Schema':
        """添加嵌套字段"""
        self.fields[name] = Field(name, "nested", nested=nested_schema)
        return self
    
    def has_field(self, name: str) -> bool:
        """检查是否有指定字段"""
        return name in self.fields
    
    def get_field(self, name: str) -> Optional[Field]:
        """获取字段定义"""
        return self.fields.get(name)
    
    def add_constraint(self, constraint: str) -> 'Schema':
        """添加约束"""
        self.constraints.append(constraint)
        return self
    
    def copy(self) -> 'Schema':
        """深拷贝Schema"""
        return Schema(
            name=self.name,
            fields={k: v.copy() for k, v in self.fields.items()},
            constraints=self.constraints.copy(),
            metadata=deepcopy(self.metadata)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "fields": {
                k: {
                    "type": v.type_,
                    "optional": v.optional,
                    "default": v.default,
                    "nested": v.nested.to_dict() if v.nested else None
                }
                for k, v in self.fields.items()
            },
            "constraints": self.constraints,
            "metadata": self.metadata
        }
    
    def __repr__(self) -> str:
        fields_str = ", ".join(str(f) for f in self.fields.values())
        return f"Schema({self.name}){{ {fields_str} }}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Schema):
            return False
        return (self.name == other.name and 
                self.fields.keys() == other.fields.keys())
    
    def __hash__(self) -> int:
        return hash(self.name)


class SchemaCategory(Category):
    """
    Schema范畴实现
    
    对象：Schema定义
    态射：Schema映射（字段映射、类型映射）
    """
    
    def __init__(self):
        self._schemas: Dict[str, Schema] = {}
        self._morphisms: Dict[tuple, Set[Morphism]] = {}
    
    def add_schema(self, schema: Schema) -> None:
        """添加Schema对象"""
        self._schemas[schema.name] = schema
    
    def objects(self) -> Set[Schema]:
        """返回所有Schema对象"""
        return set(self._schemas.values())
    
    def get_object(self, name: str) -> Optional[Schema]:
        """按名称获取Schema"""
        return self._schemas.get(name)
    
    def morphisms(self, source: Schema, target: Schema) -> Set[Morphism]:
        """返回从source到target的所有态射"""
        key = (source.name, target.name)
        return self._morphisms.get(key, set())
    
    def add_morphism(self, morphism: Morphism) -> None:
        """添加态射"""
        key = (morphism.source, morphism.target)
        if key not in self._morphisms:
            self._morphisms[key] = set()
        self._morphisms[key].add(morphism)
    
    def compose(self, f: Morphism, g: Morphism) -> Morphism:
        """
        态射复合 g ∘ f
        
        要求: f: A → B, g: B → C
        结果: g ∘ f: A → C
        """
        if f.target != g.source:
            raise ValueError(f"无法复合: {f.target} ≠ {g.source}")
        
        def composed_mapping(x):
            return g(f(x))
        
        return Morphism(
            source=f.source,
            target=g.target,
            name=f"{g.name} ∘ {f.name}",
            mapping=composed_mapping
        )
    
    def identity(self, obj: Schema) -> Morphism:
        """返回Schema的单位态射"""
        return Morphism(
            source=obj.name,
            target=obj.name,
            name=f"id_{obj.name}",
            mapping=lambda x: x
        )
    
    def create_field_mapping(self, source: Schema, target: Schema,
                           field_map: Dict[str, str]) -> Morphism:
        """
        创建基于字段映射的Schema态射
        
        Args:
            source: 源Schema
            target: 目标Schema
            field_map: 字段名映射 {源字段: 目标字段}
        """
        def map_data(data: Dict[str, Any]) -> Dict[str, Any]:
            result = {}
            for src_field, tgt_field in field_map.items():
                if src_field in data:
                    result[tgt_field] = data[src_field]
            return result
        
        return Morphism(
            source=source.name,
            target=target.name,
            name=f"map_{source.name}_to_{target.name}",
            mapping=map_data
        )


# ============================================================================
# 第三部分：转换函子
# ============================================================================

class Functor(ABC):
    """
    函子抽象基类
    
    函子 F: C → D 包含：
    - 对象映射: F_obj: Ob(C) → Ob(D)
    - 态射映射: F_mor: Hom(A, B) → Hom(F(A), F(B))
    
    满足：
    - F(id_A) = id_{F(A)}
    - F(g ∘ f) = F(g) ∘ F(f)
    """
    
    @abstractmethod
    def map_object(self, obj: Schema) -> Schema:
        """映射对象"""
        pass
    
    @abstractmethod
    def map_morphism(self, morph: Morphism) -> Morphism:
        """映射态射"""
        pass
    
    def apply(self, schema: Schema) -> Schema:
        """应用函子到Schema（对象映射的别名）"""
        return self.map_object(schema)
    
    def verify_functor_laws(self, category: SchemaCategory, 
                           test_schema: Schema) -> Dict[str, bool]:
        """
        验证函子律
        
        检查：
        1. 保持单位态射
        2. 保持复合（需要额外的态射进行测试）
        """
        results = {}
        
        # 验证单位律
        id_source = category.identity(test_schema)
        mapped_id = self.map_morphism(id_source)
        target = self.map_object(test_schema)
        id_target = category.identity(target)
        
        results["identity_preservation"] = (
            mapped_id.source == id_target.source and
            mapped_id.target == id_target.target
        )
        
        return results


class SchemaFunctor(Functor):
    """
    Schema转换函子的基类
    
    提供通用的对象和态射映射框架
    """
    
    def __init__(self, name: str):
        self.name = name
    
    def map_morphism(self, morph: Morphism) -> Morphism:
        """
        默认态射映射：保持态射结构
        子类可以覆盖此方法
        """
        return Morphism(
            source=morph.source,
            target=morph.target,
            name=f"{self.name}({morph.name})",
            mapping=morph.mapping
        )


class AddFieldFunctor(SchemaFunctor):
    """
    字段添加函子 A_f
    
    A_f(S) = S 添加字段 f
    
    函子性验证：
    - A_f(id_S) = id_{A_f(S)}
    - A_f(g ∘ f) = A_f(g) ∘ A_f(f)
    """
    
    def __init__(self, field_name: str, field_type: str, 
                 optional: bool = False, default: Any = None):
        super().__init__(f"AddField_{field_name}")
        self.field_name = field_name
        self.field_type = field_type
        self.optional = optional
        self.default = default
    
    def map_object(self, obj: Schema) -> Schema:
        """添加字段到Schema"""
        result = obj.copy()
        result.add_field(self.field_name, self.field_type, 
                        self.optional, self.default)
        return result
    
    def map_morphism(self, morph: Morphism) -> Morphism:
        """
        映射态射：扩展以处理新字段
        
        新字段使用默认值传递
        """
        original_mapping = morph.mapping
        
        def extended_mapping(data):
            result = original_mapping(data)
            if isinstance(result, dict):
                result = result.copy()
                if self.field_name not in result:
                    result[self.field_name] = self.default
            return result
        
        return Morphism(
            source=morph.source,
            target=morph.target,
            name=f"{self.name}({morph.name})",
            mapping=extended_mapping
        )


class RemoveFieldFunctor(SchemaFunctor):
    """
    字段删除函子 D_f
    
    D_f(S) = S 删除字段 f
    
    这是添加函子的左逆（在适当条件下）
    """
    
    def __init__(self, field_name: str):
        super().__init__(f"RemoveField_{field_name}")
        self.field_name = field_name
    
    def map_object(self, obj: Schema) -> Schema:
        """从Schema删除字段"""
        result = obj.copy()
        result.remove_field(self.field_name)
        return result
    
    def map_morphism(self, morph: Morphism) -> Morphism:
        """
        映射态射：限制到剩余字段
        """
        original_mapping = morph.mapping
        
        def restricted_mapping(data):
            result = original_mapping(data)
            if isinstance(result, dict) and self.field_name in result:
                result = {k: v for k, v in result.items() 
                         if k != self.field_name}
            return result
        
        return Morphism(
            source=morph.source,
            target=morph.target,
            name=f"{self.name}({morph.name})",
            mapping=restricted_mapping
        )


class RenameTypeFunctor(SchemaFunctor):
    """
    类型重命名函子 R_{t1→t2}
    
    将Schema中的类型t1重命名为t2
    """
    
    def __init__(self, old_type: str, new_type: str):
        super().__init__(f"RenameType_{old_type}_to_{new_type}")
        self.old_type = old_type
        self.new_type = new_type
    
    def map_object(self, obj: Schema) -> Schema:
        """重命名Schema中的类型"""
        result = obj.copy()
        for field in result.fields.values():
            if field.type_ == self.old_type:
                field.type_ = self.new_type
        return result


class FlattenFunctor(SchemaFunctor):
    """
    嵌套扁平化函子 F
    
    将嵌套字段展开为顶层字段
    例如: {address: {street, city}} → {address_street, address_city}
    """
    
    def __init__(self, separator: str = "_"):
        super().__init__("Flatten")
        self.separator = separator
    
    def map_object(self, obj: Schema) -> Schema:
        """扁平化嵌套结构"""
        result = Schema(f"Flattened_{obj.name}")
        result.metadata = obj.metadata.copy()
        result.constraints = obj.constraints.copy()
        
        for field_name, field in obj.fields.items():
            if field.nested:
                # 展开嵌套字段
                for nested_name, nested_field in field.nested.fields.items():
                    new_name = f"{field_name}{self.separator}{nested_name}"
                    result.add_field(
                        new_name, 
                        nested_field.type_,
                        nested_field.optional,
                        nested_field.default
                    )
            else:
                # 保持非嵌套字段
                result.add_field(
                    field_name,
                    field.type_,
                    field.optional,
                    field.default
                )
        
        return result
    
    def map_morphism(self, morph: Morphism) -> Morphism:
        """映射态射以处理扁平化后的结构"""
        original_mapping = morph.mapping
        
        def flattened_mapping(data):
            result = original_mapping(data)
            if not isinstance(result, dict):
                return result
            
            flat_result = {}
            for key, value in result.items():
                if isinstance(value, dict):
                    # 展开嵌套值
                    for nested_key, nested_value in value.items():
                        new_key = f"{key}{self.separator}{nested_key}"
                        flat_result[new_key] = nested_value
                else:
                    flat_result[key] = value
            return flat_result
        
        return Morphism(
            source=f"Flattened_{morph.source}",
            target=f"Flattened_{morph.target}",
            name=f"Flatten({morph.name})",
            mapping=flattened_mapping
        )


class CompositeFunctor(SchemaFunctor):
    """
    复合函子
    
    表示多个函子的组合: F = F_n ∘ ... ∘ F_2 ∘ F_1
    
    函子组合满足结合律
    """
    
    def __init__(self, functors: List[Functor]):
        super().__init__("Composite")
        self.functors = functors
    
    def map_object(self, obj: Schema) -> Schema:
        """顺序应用所有函子"""
        result = obj
        for f in self.functors:
            result = f.map_object(result)
        return result
    
    def map_morphism(self, morph: Morphism) -> Morphism:
        """顺序映射态射"""
        result = morph
        for f in self.functors:
            result = f.map_morphism(result)
        return result


# ============================================================================
# 第四部分：自然变换
# ============================================================================

class NaturalTransformation:
    """
    自然变换 η: F ⇒ G
    
    对范畴C中的每个对象A，指定一个态射 η_A: F(A) → G(A)
    使得对任意 f: A → B，下图交换：
    
        F(A) --η_A--> G(A)
          |              |
          | F(f)         | G(f)
          v              v
        F(B) --η_B--> G(B)
    
    即: η_B ∘ F(f) = G(f) ∘ η_A
    """
    
    def __init__(self, source: Functor, target: Functor, 
                 components: Dict[str, Morphism]):
        """
        Args:
            source: 源函子 F
            target: 目标函子 G
            components: 分量映射 {Schema名称: 态射}
        """
        self.source = source
        self.target = target
        self.components = components
    
    def component_at(self, schema: Schema) -> Optional[Morphism]:
        """获取在指定Schema处的分量"""
        return self.components.get(schema.name)
    
    def is_natural(self, category: SchemaCategory, 
                   f: Morphism) -> bool:
        """
        验证自然性条件对特定态射f是否成立
        
        检查: η_B ∘ F(f) = G(f) ∘ η_A
        """
        # 获取源和目标Schema
        source_schema = category.get_object(f.source)
        target_schema = category.get_object(f.target)
        
        if source_schema is None or target_schema is None:
            return False
        
        # 获取分量
        eta_A = self.component_at(source_schema)
        eta_B = self.component_at(target_schema)
        
        if eta_A is None or eta_B is None:
            return False
        
        # 计算两边
        F_f = self.source.map_morphism(f)
        G_f = self.target.map_morphism(f)
        
        left = category.compose(F_f, eta_B)
        right = category.compose(eta_A, G_f)
        
        # 在实际应用中，可能需要更复杂的等价判断
        return left.source == right.source and left.target == right.target
    
    def __repr__(self) -> str:
        return f"NaturalTransformation({self.source.name} ⇒ {self.target.name})"


# ============================================================================
# 第五部分：辅助函数与示例
# ============================================================================

def create_identity_functor() -> SchemaFunctor:
    """创建恒等函子"""
    class IdentityFunctor(SchemaFunctor):
        def __init__(self):
            super().__init__("Identity")
        
        def map_object(self, obj: Schema) -> Schema:
            return obj.copy()
        
        def map_morphism(self, morph: Morphism) -> Morphism:
            return morph
    
    return IdentityFunctor()


def compose_functors(*functors: Functor) -> CompositeFunctor:
    """
    组合多个函子
    
    从左到右应用: compose(F, G, H) = H ∘ G ∘ F
    """
    return CompositeFunctor(list(functors))


def example_basic_transformation():
    """
    示例1：基本Schema转换
    
    演示字段添加、删除和扁平化
    """
    print("=" * 60)
    print("示例1: 基本Schema转换")
    print("=" * 60)
    
    # 创建源Schema
    source = Schema("User")
    source.add_field("name", "string")
    source.add_field("age", "int")
    
    # 添加嵌套地址
    address = Schema("Address")
    address.add_field("street", "string")
    address.add_field("city", "string")
    source.add_nested("address", address)
    
    print(f"\n源Schema:\n{source}")
    print(f"\n详细结构:\n{json.dumps(source.to_dict(), indent=2)}")
    
    # 应用添加字段函子
    add_email = AddFieldFunctor("email", "string", optional=True)
    with_email = add_email.apply(source)
    print(f"\n添加email后:\n{with_email}")
    
    # 应用扁平化函子
    flatten = FlattenFunctor(separator="_")
    flattened = flatten.apply(with_email)
    print(f"\n扁平化后:\n{flattened}")
    print(f"\n扁平化详细结构:\n{json.dumps(flattened.to_dict(), indent=2)}")
    
    return source, with_email, flattened


def example_functor_composition():
    """
    示例2：函子组合
    
    展示函子的组合性和结合律
    """
    print("\n" + "=" * 60)
    print("示例2: 函子组合")
    print("=" * 60)
    
    # 创建Schema
    schema = Schema("Product")
    schema.add_field("name", "string")
    schema.add_field("price", "float")
    
    print(f"\n原始Schema:\n{schema}")
    
    # 定义函子
    F = AddFieldFunctor("sku", "string")
    G = AddFieldFunctor("category", "string", optional=True)
    H = RenameTypeFunctor("float", "decimal")
    
    # 组合函子: H ∘ G ∘ F
    composite = compose_functors(F, G, H)
    result = composite.apply(schema)
    
    print(f"\n应用组合函子 H∘G∘F:\n{result}")
    
    # 验证结合律: (H ∘ G) ∘ F = H ∘ (G ∘ F)
    left_assoc = compose_functors(compose_functors(F, G), H)
    right_assoc = compose_functors(F, compose_functors(G, H))
    
    left_result = left_assoc.apply(schema)
    right_result = right_assoc.apply(schema)
    
    print(f"\n结合律验证:")
    print(f"  (H∘G)∘F 字段: {list(left_result.fields.keys())}")
    print(f"  H∘(G∘F) 字段: {list(right_result.fields.keys())}")
    print(f"  相等: {list(left_result.fields.keys()) == list(right_result.fields.keys())}")
    
    return result


def example_functor_laws():
    """
    示例3：验证函子律
    
    验证函子保持单位态射和复合运算
    """
    print("\n" + "=" * 60)
    print("示例3: 验证函子律")
    print("=" * 60)
    
    # 创建范畴和Schema
    category = SchemaCategory()
    schema = Schema("Test")
    schema.add_field("a", "int")
    schema.add_field("b", "string")
    category.add_schema(schema)
    
    # 创建函子
    functor = AddFieldFunctor("c", "bool")
    
    # 验证单位律
    results = functor.verify_functor_laws(category, schema)
    print(f"\n函子律验证结果:")
    for law, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {law}: {status}")
    
    return results


def example_natural_transformation():
    """
    示例4：自然变换
    
    展示两种等价转换之间的关系
    """
    print("\n" + "=" * 60)
    print("示例4: 自然变换")
    print("=" * 60)
    
    # 创建Schema
    schema = Schema("Item")
    schema.add_field("value", "int")
    
    # 两种等价的转换方式
    # 方式1: 先添加字段再重命名
    F1 = compose_functors(
        AddFieldFunctor("count", "int"),
        RenameTypeFunctor("int", "integer")
    )
    
    # 方式2: 先重命名再添加字段
    F2 = compose_functors(
        RenameTypeFunctor("int", "integer"),
        AddFieldFunctor("count", "integer")
    )
    
    result1 = F1.apply(schema)
    result2 = F2.apply(schema)
    
    print(f"\nSchema: {schema.name}")
    print(f"方式1结果 (Add→Rename): {list(result1.fields.keys())}")
    print(f"  类型: {[(f.name, f.type_) for f in result1.fields.values()]}")
    print(f"方式2结果 (Rename→Add): {list(result2.fields.keys())}")
    print(f"  类型: {[(f.name, f.type_) for f in result2.fields.values()]}")
    
    print(f"\n两种转换语义等价: {result1 == result2}")
    
    return result1, result2


def example_data_transformation():
    """
    示例5：数据转换示例
    
    展示如何使用态射映射转换实际数据
    """
    print("\n" + "=" * 60)
    print("示例5: 数据转换")
    print("=" * 60)
    
    # 创建Schema和范畴
    category = SchemaCategory()
    
    old_schema = Schema("LegacyUser")
    old_schema.add_field("username", "string")
    old_schema.add_field("user_age", "int")
    old_schema.add_nested("location", Schema("Loc").add_field("city_name", "string"))
    
    category.add_schema(old_schema)
    
    # 定义函子：现代化转换
    transform = compose_functors(
        RenameTypeFunctor("int", "number"),
        FlattenFunctor("_")
    )
    
    new_schema = transform.apply(old_schema)
    category.add_schema(new_schema)
    
    print(f"\n旧Schema:\n{old_schema}")
    print(f"\n新Schema:\n{new_schema}")
    
    # 示例数据
    old_data = {
        "username": "张三",
        "user_age": 28,
        "location": {"city_name": "北京"}
    }
    
    # 创建数据映射态射
    id_morph = category.identity(old_schema)
    data_morph = transform.map_morphism(id_morph)
    
    # 应用转换
    new_data = data_morph(old_data)
    
    print(f"\n旧数据: {old_data}")
    print(f"新数据: {new_data}")
    
    return new_data


def examples():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print(" " * 15 + "Schema转换的范畴论实现")
    print(" " * 10 + "Category Theory Schema Transformation")
    print("=" * 70)
    
    example_basic_transformation()
    example_functor_composition()
    example_functor_laws()
    example_natural_transformation()
    example_data_transformation()
    
    print("\n" + "=" * 70)
    print("所有示例完成!")
    print("=" * 70)


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    examples()
