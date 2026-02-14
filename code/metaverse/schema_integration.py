"""
元宇宙Schema集成模块
Metaverse Schema Integration Module

提供OpenXR/glTF集成、3D资产转换、场景图构建功能
Provides OpenXR/glTF integration, 3D asset transformation, and scene graph construction

作者: Metaverse Schema Team
版本: 1.0.0
"""

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# 枚举定义 (Enum Definitions)
# =============================================================================

class EntityType(Enum):
    """实体类型"""
    AVATAR = "avatar"
    OBJECT = "object"
    ENVIRONMENT = "environment"
    TRIGGER = "trigger"
    LIGHT = "light"
    CAMERA = "camera"
    PARTICLE_SYSTEM = "particle_system"


class ComponentType(Enum):
    """组件类型"""
    TRANSFORM = "transform"
    RENDER = "render"
    PHYSICS = "physics"
    CAMERA = "camera"
    LIGHT = "light"
    AUDIO = "audio"
    ANIMATION = "animation"
    SCRIPT = "script"
    INTERACTION = "interaction"
    SPRING_BONE = "spring_bone"


class AssetType(Enum):
    """资产类型"""
    MODEL = "model"
    MATERIAL = "material"
    TEXTURE = "texture"
    AUDIO = "audio"
    ANIMATION = "animation"
    PREFAB = "prefab"
    SCRIPT = "script"
    SCENE = "scene"


class BodyType(Enum):
    """物理体类型"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    KINEMATIC = "kinematic"


class InteractionType(Enum):
    """交互类型"""
    COLLISION = "collision"
    GRAB = "grab"
    USE = "use"
    RAYCAST = "raycast"
    GESTURE = "gesture"
    VOICE = "voice"


class ReferenceSpaceType(Enum):
    """OpenXR参考空间类型"""
    VIEW = "view"
    LOCAL = "local"
    LOCAL_FLOOR = "local_floor"
    STAGE = "stage"
    UNBOUNDED = "unbounded"


# =============================================================================
# 数据类定义 (Data Class Definitions)
# =============================================================================

@dataclass
class Vector3:
    """三维向量"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]
    
    @classmethod
    def from_list(cls, data: List[float]) -> "Vector3":
        return cls(x=data[0], y=data[1], z=data[2])


@dataclass
class Quaternion:
    """四元数"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0
    
    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z, self.w]
    
    @classmethod
    def from_list(cls, data: List[float]) -> "Quaternion":
        return cls(x=data[0], y=data[1], z=data[2], w=data[3])


@dataclass
class Transform:
    """变换组件数据"""
    position: Vector3 = field(default_factory=Vector3)
    rotation: Quaternion = field(default_factory=Quaternion)
    scale: Vector3 = field(default_factory=lambda: Vector3(1.0, 1.0, 1.0))
    
    def to_dict(self) -> Dict:
        return {
            "position": self.position.to_list(),
            "rotation": self.rotation.to_list(),
            "scale": self.scale.to_list()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Transform":
        return cls(
            position=Vector3.from_list(data.get("position", [0, 0, 0])),
            rotation=Quaternion.from_list(data.get("rotation", [0, 0, 0, 1])),
            scale=Vector3.from_list(data.get("scale", [1, 1, 1]))
        )


@dataclass
class Component:
    """组件基类"""
    component_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    component_type: ComponentType = ComponentType.TRANSFORM
    enabled: bool = True
    properties: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "enabled": self.enabled,
            "properties": self.properties
        }


@dataclass
class TransformComponent(Component):
    """变换组件"""
    transform: Transform = field(default_factory=Transform)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.component_type = ComponentType.TRANSFORM
    
    def to_dict(self) -> Dict:
        base = super().to_dict()
        base["properties"] = {
            "transform": self.transform.to_dict(),
            "parent_id": self.parent_id,
            "children_ids": self.children_ids
        }
        return base


@dataclass
class RenderComponent(Component):
    """渲染组件"""
    mesh_uri: str = ""
    material_uris: List[str] = field(default_factory=list)
    cast_shadows: bool = True
    receive_shadows: bool = True
    lod_distances: List[float] = field(default_factory=lambda: [50.0, 150.0, 500.0])
    
    def __post_init__(self):
        self.component_type = ComponentType.RENDER
    
    def to_dict(self) -> Dict:
        base = super().to_dict()
        base["properties"] = {
            "mesh_uri": self.mesh_uri,
            "material_uris": self.material_uris,
            "cast_shadows": self.cast_shadows,
            "receive_shadows": self.receive_shadows,
            "lod_distances": self.lod_distances
        }
        return base


@dataclass
class PhysicsComponent(Component):
    """物理组件"""
    body_type: BodyType = BodyType.STATIC
    mass: float = 1.0
    friction: float = 0.5
    restitution: float = 0.0
    use_gravity: bool = True
    is_trigger: bool = False
    collider_shape: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        self.component_type = ComponentType.PHYSICS
    
    def to_dict(self) -> Dict:
        base = super().to_dict()
        base["properties"] = {
            "body_type": self.body_type.value,
            "mass": self.mass,
            "friction": self.friction,
            "restitution": self.restitution,
            "use_gravity": self.use_gravity,
            "is_trigger": self.is_trigger,
            "collider_shape": self.collider_shape
        }
        return base


@dataclass
class InteractionComponent(Component):
    """交互组件"""
    interaction_type: InteractionType = InteractionType.RAYCAST
    trigger_shape: Dict = field(default_factory=dict)
    actions: List[Dict] = field(default_factory=list)
    cooldown_ms: int = 0
    requires_authority: bool = False
    
    def __post_init__(self):
        self.component_type = ComponentType.INTERACTION
    
    def to_dict(self) -> Dict:
        base = super().to_dict()
        base["properties"] = {
            "interaction_type": self.interaction_type.value,
            "trigger_shape": self.trigger_shape,
            "actions": self.actions,
            "cooldown_ms": self.cooldown_ms,
            "requires_authority": self.requires_authority
        }
        return base


@dataclass
class Entity:
    """实体定义"""
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType = EntityType.OBJECT
    name: str = ""
    space_id: Optional[str] = None
    parent_id: Optional[str] = None
    components: List[Component] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def add_component(self, component: Component) -> None:
        """添加组件"""
        self.components.append(component)
    
    def get_component(self, component_type: ComponentType) -> Optional[Component]:
        """获取指定类型的组件"""
        for comp in self.components:
            if comp.component_type == component_type:
                return comp
        return None
    
    def to_dict(self) -> Dict:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "space_id": self.space_id,
            "parent_id": self.parent_id,
            "components": [c.to_dict() for c in self.components],
            "tags": self.tags,
            "metadata": self.metadata
        }


@dataclass
class Asset:
    """资产定义"""
    asset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: AssetType = AssetType.MODEL
    name: str = ""
    content_uri: str = ""
    owner_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    technical_specs: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "name": self.name,
            "content_uri": self.content_uri,
            "owner_id": self.owner_id,
            "metadata": self.metadata,
            "technical_specs": self.technical_specs,
            "tags": self.tags,
            "dependencies": self.dependencies
        }


@dataclass
class Space:
    """空间定义"""
    space_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    world_id: str = ""
    name: str = ""
    bounds: Dict = field(default_factory=lambda: {
        "min": [-1000, -100, -1000],
        "max": [1000, 500, 1000]
    })
    spawn_points: List[Dict] = field(default_factory=list)
    settings: Dict = field(default_factory=dict)
    entities: List[Entity] = field(default_factory=list)
    
    def add_entity(self, entity: Entity) -> None:
        """添加实体到空间"""
        entity.space_id = self.space_id
        self.entities.append(entity)
    
    def to_dict(self) -> Dict:
        return {
            "space_id": self.space_id,
            "world_id": self.world_id,
            "name": self.name,
            "bounds": self.bounds,
            "spawn_points": self.spawn_points,
            "settings": self.settings,
            "entities": [e.to_dict() for e in self.entities]
        }


# =============================================================================
# OpenXR集成 (OpenXR Integration)
# =============================================================================

class OpenXRAdapter:
    """
    OpenXR到Schema的适配器
    将OpenXR的数据结构转换为Schema格式
    """
    
    def __init__(self):
        self.session = None
        self.reference_spaces: Dict[ReferenceSpaceType, Any] = {}
        self.action_sets: Dict[str, Any] = {}
    
    def convert_reference_space(self, xr_space_type: str) -> ReferenceSpaceType:
        """转换OpenXR参考空间类型"""
        mapping = {
            "XR_REFERENCE_SPACE_TYPE_VIEW": ReferenceSpaceType.VIEW,
            "XR_REFERENCE_SPACE_TYPE_LOCAL": ReferenceSpaceType.LOCAL,
            "XR_REFERENCE_SPACE_TYPE_LOCAL_FLOOR": ReferenceSpaceType.LOCAL_FLOOR,
            "XR_REFERENCE_SPACE_TYPE_STAGE": ReferenceSpaceType.STAGE,
            "XR_REFERENCE_SPACE_TYPE_UNBOUNDED": ReferenceSpaceType.UNBOUNDED,
        }
        return mapping.get(xr_space_type, ReferenceSpaceType.LOCAL)
    
    def convert_pose_to_transform(self, position: List[float], 
                                   orientation: List[float]) -> Transform:
        """将OpenXR姿态转换为Schema变换"""
        return Transform(
            position=Vector3.from_list(position),
            rotation=Quaternion.from_list(orientation)
        )
    
    def create_input_mapping(self, action_set_name: str, 
                            bindings: Dict[str, str]) -> Dict:
        """
        创建输入映射配置
        
        Args:
            action_set_name: 动作集名称
            bindings: 动作到路径的映射
                例如: {"grab": "/user/hand/left/input/grip"}
        
        Returns:
            输入映射配置字典
        """
        return {
            "action_set_name": action_set_name,
            "bindings": [
                {
                    "action": action,
                    "path": path,
                    "component_type": self._infer_component_type(action)
                }
                for action, path in bindings.items()
            ]
        }
    
    def _infer_component_type(self, action: str) -> str:
        """根据动作名称推断组件类型"""
        action_lower = action.lower()
        if any(word in action_lower for word in ["grab", "trigger", "button"]):
            return "button"
        elif any(word in action_lower for word in ["move", "stick", "joystick"]):
            return "vector2"
        elif any(word in action_lower for word in ["pose", "hand", "controller"]):
            return "transform"
        elif "haptic" in action_lower:
            return "haptic"
        return "generic"
    
    def convert_view_to_camera(self, view_data: Dict) -> Dict:
        """将OpenXR视图转换为相机配置"""
        return {
            "camera_type": "perspective",
            "transform": self.convert_pose_to_transform(
                view_data["position"],
                view_data["orientation"]
            ).to_dict(),
            "fov": {
                "angle_left": view_data.get("fov", {}).get("angleLeft", -0.5),
                "angle_right": view_data.get("fov", {}).get("angleRight", 0.5),
                "angle_up": view_data.get("fov", {}).get("angleUp", 0.5),
                "angle_down": view_data.get("fov", {}).get("angleDown", -0.5),
            }
        }


# =============================================================================
# glTF集成 (glTF Integration)
# =============================================================================

class GLTFAdapter:
    """
    glTF到Schema的适配器
    支持glTF 2.0格式的导入和导出
    """
    
    def __init__(self):
        self.extensions_supported = [
            "KHR_draco_mesh_compression",
            "KHR_texture_transform",
            "KHR_materials_pbrSpecularGlossiness",
            "KHR_materials_clearcoat",
            "KHR_lights_punctual"
        ]
    
    def import_gltf(self, gltf_data: Dict) -> Space:
        """
        导入glTF数据为Schema空间
        
        Args:
            gltf_data: 解析后的glTF JSON数据
        
        Returns:
            Schema Space对象
        """
        space = Space(
            name=gltf_data.get("asset", {}).get("generator", "Imported glTF"),
            metadata={
                "gltf_version": gltf_data.get("asset", {}).get("version", "2.0"),
                "source_file": gltf_data.get("uri", "unknown")
            }
        )
        
        # 导入场景节点
        scene_index = gltf_data.get("scene", 0)
        scenes = gltf_data.get("scenes", [])
        if scenes and scene_index < len(scenes):
            scene = scenes[scene_index]
            nodes = gltf_data.get("nodes", [])
            
            # 递归导入节点
            for node_index in scene.get("nodes", []):
                if node_index < len(nodes):
                    entity = self._import_node(nodes[node_index], nodes, gltf_data)
                    space.add_entity(entity)
        
        logger.info(f"Imported glTF with {len(space.entities)} entities")
        return space
    
    def _import_node(self, node: Dict, all_nodes: List[Dict], 
                     gltf_data: Dict) -> Entity:
        """导入单个glTF节点为实体"""
        entity = Entity(
            name=node.get("name", f"Node_{id(node)}"),
            entity_type=EntityType.OBJECT,
            metadata={
                "gltf_node_index": all_nodes.index(node) if node in all_nodes else -1,
                "gltf_extras": node.get("extras", {})
            }
        )
        
        # 添加变换组件
        transform = Transform()
        if "matrix" in node:
            # 解析4x4矩阵
            matrix = node["matrix"]
            # 这里简化处理，实际应进行矩阵分解
            transform.position = Vector3(matrix[12], matrix[13], matrix[14])
        else:
            if "translation" in node:
                transform.position = Vector3.from_list(node["translation"])
            if "rotation" in node:
                transform.rotation = Quaternion.from_list(node["rotation"])
            if "scale" in node:
                transform.scale = Vector3.from_list(node["scale"])
        
        transform_comp = TransformComponent(transform=transform)
        entity.add_component(transform_comp)
        
        # 添加渲染组件（如果有mesh）
        if "mesh" in node:
            mesh_index = node["mesh"]
            meshes = gltf_data.get("meshes", [])
            if mesh_index < len(meshes):
                mesh = meshes[mesh_index]
                render_comp = RenderComponent(
                    mesh_uri=f"gltf://meshes/{mesh_index}",
                    metadata={"mesh_name": mesh.get("name", f"Mesh_{mesh_index}")}
                )
                entity.add_component(render_comp)
        
        # 处理子节点
        for child_index in node.get("children", []):
            if child_index < len(all_nodes):
                child_entity = self._import_node(all_nodes[child_index], all_nodes, gltf_data)
                child_entity.parent_id = entity.entity_id
                entity.components[0].children_ids.append(child_entity.entity_id)
        
        return entity
    
    def export_gltf(self, space: Space) -> Dict:
        """
        导出Schema空间为glTF格式
        
        Args:
            space: Schema Space对象
        
        Returns:
            glTF格式的字典数据
        """
        gltf = {
            "asset": {
                "version": "2.0",
                "generator": "Metaverse Schema Exporter"
            },
            "scene": 0,
            "scenes": [{"nodes": []}],
            "nodes": [],
            "meshes": [],
            "materials": [],
            "textures": [],
            "images": [],
            "buffers": [],
            "bufferViews": [],
            "accessors": []
        }
        
        # 导出实体为节点
        for entity in space.entities:
            if entity.parent_id is None:  # 只处理根级实体
                node_index = self._export_entity(entity, space, gltf)
                gltf["scenes"][0]["nodes"].append(node_index)
        
        logger.info(f"Exported {len(gltf['nodes'])} nodes to glTF")
        return gltf
    
    def _export_entity(self, entity: Entity, space: Space, 
                       gltf: Dict, parent_index: Optional[int] = None) -> int:
        """导出实体为glTF节点"""
        node = {"name": entity.name}
        
        # 导出变换
        transform_comp = entity.get_component(ComponentType.TRANSFORM)
        if transform_comp and isinstance(transform_comp, TransformComponent):
            transform = transform_comp.transform
            node["translation"] = transform.position.to_list()
            node["rotation"] = transform.rotation.to_list()
            node["scale"] = transform.scale.to_list()
        
        # 导出渲染组件
        render_comp = entity.get_component(ComponentType.RENDER)
        if render_comp and isinstance(render_comp, RenderComponent):
            mesh_index = len(gltf["meshes"])
            gltf["meshes"].append({
                "name": f"Mesh_{entity.name}",
                "primitives": [{"attributes": {"POSITION": 0}}]
            })
            node["mesh"] = mesh_index
        
        # 处理子实体
        children_indices = []
        for child in space.entities:
            if child.parent_id == entity.entity_id:
                child_index = self._export_entity(child, space, gltf, len(gltf["nodes"]))
                children_indices.append(child_index)
        
        if children_indices:
            node["children"] = children_indices
        
        node_index = len(gltf["nodes"])
        gltf["nodes"].append(node)
        
        return node_index


# =============================================================================
# VRM集成 (VRM Integration)
# =============================================================================

class VRMAdapter:
    """
    VRM到Schema的适配器
    支持VRM 0.x和1.0格式
    """
    
    # VRM人形骨骼到Schema的映射
    HUMANOID_BONE_MAPPING = {
        "hips": "root",
        "spine": "spine_0",
        "chest": "spine_1",
        "neck": "neck",
        "head": "head",
        "leftUpperLeg": "left_leg_upper",
        "leftLowerLeg": "left_leg_lower",
        "leftFoot": "left_foot",
        "rightUpperLeg": "right_leg_upper",
        "rightLowerLeg": "right_leg_lower",
        "rightFoot": "right_foot",
        "leftUpperArm": "left_arm_upper",
        "leftLowerArm": "left_arm_lower",
        "leftHand": "left_hand",
        "rightUpperArm": "right_arm_upper",
        "rightLowerArm": "right_arm_lower",
        "rightHand": "right_hand",
    }
    
    # VRM表情到Schema的映射
    EXPRESSION_MAPPING = {
        "happy": "happy",
        "angry": "angry",
        "sad": "sad",
        "relaxed": "relaxed",
        "surprised": "surprised",
        "neutral": "neutral",
        "blink": "blink",
        "blinkLeft": "blink_left",
        "blinkRight": "blink_right",
        "lookUp": "look_up",
        "lookDown": "look_down",
        "lookLeft": "look_left",
        "lookRight": "look_right",
    }
    
    def import_vrm(self, vrm_data: Dict) -> Dict:
        """
        导入VRM数据
        
        Args:
            vrm_data: 解析后的VRM JSON数据
        
        Returns:
            包含化身配置的字典
        """
        # 检测VRM版本
        vrm_extension = vrm_data.get("extensions", {}).get("VRM")
        vrmc_extension = vrm_data.get("extensions", {}).get("VRMC_vrm")
        
        if vrmc_extension:
            return self._import_vrm_1_0(vrm_data, vrmc_extension)
        elif vrm_extension:
            return self._import_vrm_0_x(vrm_data, vrm_extension)
        else:
            raise ValueError("Invalid VRM data: no VRM extension found")
    
    def _import_vrm_0_x(self, gltf_data: Dict, vrm_extension: Dict) -> Dict:
        """导入VRM 0.x格式"""
        meta = vrm_extension.get("meta", {})
        humanoid = vrm_extension.get("humanoid", {})
        blend_shapes = vrm_extension.get("blendShapeMaster", {}).get("blendShapeGroups", [])
        spring_bones = vrm_extension.get("secondaryAnimation", {})
        
        avatar_config = {
            "version": "0.x",
            "name": meta.get("title", "Unnamed Avatar"),
            "meta": {
                "author": meta.get("author"),
                "contact": meta.get("contactInformation"),
                "reference": meta.get("reference"),
                "allowed_user": meta.get("allowedUser"),
                "violent_usage": meta.get("violentUssageName"),
                "sexual_usage": meta.get("sexualUssageName"),
                "commercial_usage": meta.get("commercialUssageName"),
                "license": meta.get("otherLicenseUrl")
            },
            "skeleton": self._convert_humanoid_bones(humanoid.get("humanBones", [])),
            "expressions": self._convert_expressions(blend_shapes),
            "spring_bones": self._convert_spring_bones(spring_bones),
            "first_person": vrm_extension.get("firstPerson", {}),
            "materials": self._convert_vrm_materials(gltf_data.get("materials", []))
        }
        
        return avatar_config
    
    def _import_vrm_1_0(self, gltf_data: Dict, vrm_extension: Dict) -> Dict:
        """导入VRM 1.0格式"""
        meta = vrm_extension.get("meta", {})
        humanoid = vrm_extension.get("humanoid", {})
        expressions = vrm_extension.get("expressions", {})
        
        avatar_config = {
            "version": "1.0",
            "name": meta.get("name", "Unnamed Avatar"),
            "meta": {
                "authors": meta.get("authors", []),
                "copyright": meta.get("copyrightInformation"),
                "contact": meta.get("contactInformation"),
                "references": meta.get("references", []),
                "third_party_licenses": meta.get("thirdPartyLicenses"),
                "avatar_permission": meta.get("avatarPermission"),
                "violent_usage": meta.get("allowExcessivelyViolentUsage"),
                "sexual_usage": meta.get("allowExcessivelySexualUsage"),
                "commercial_usage": meta.get("commercialUsage"),
                "political_usage": meta.get("allowPoliticalOrReligiousUsage"),
                "antisocial_usage": meta.get("allowAntisocialOrHateUsage"),
                "redistribution": meta.get("redistribution"),
                "modification": meta.get("modification"),
                "license": meta.get("otherLicenseUrl")
            },
            "skeleton": self._convert_humanoid_bones_v1(humanoid.get("humanBones", [])),
            "expressions": self._convert_expressions_v1(expressions),
            "look_at": vrm_extension.get("lookAt", {}),
            "first_person": vrm_extension.get("firstPerson", {}),
            "materials": self._convert_vrm_materials(gltf_data.get("materials", []))
        }
        
        return avatar_config
    
    def _convert_humanoid_bones(self, human_bones: List[Dict]) -> Dict:
        """转换人形骨骼定义"""
        skeleton = {}
        for bone in human_bones:
            vrm_name = bone.get("bone")
            schema_name = self.HUMANOID_BONE_MAPPING.get(vrm_name, vrm_name)
            skeleton[schema_name] = {
                "node_index": bone.get("node"),
                "use_default_values": bone.get("useDefaultValues", True),
                "min": bone.get("min", {}),
                "max": bone.get("max", {}),
                "center": bone.get("center", {})
            }
        return skeleton
    
    def _convert_humanoid_bones_v1(self, human_bones: Dict) -> Dict:
        """转换VRM 1.0人形骨骼"""
        skeleton = {}
        for bone_name, bone_data in human_bones.items():
            schema_name = self.HUMANOID_BONE_MAPPING.get(bone_name, bone_name)
            skeleton[schema_name] = {
                "node_index": bone_data.get("node"),
            }
        return skeleton
    
    def _convert_expressions(self, blend_shapes: List[Dict]) -> Dict:
        """转换表情定义"""
        expressions = {}
        for shape in blend_shapes:
            vrm_name = shape.get("name")
            schema_name = self.EXPRESSION_MAPPING.get(vrm_name, vrm_name)
            expressions[schema_name] = {
                "preset": shape.get("presetName"),
                "binds": shape.get("binds", []),
                "material_values": shape.get("materialValues", []),
                "is_binary": shape.get("isBinary", False)
            }
        return expressions
    
    def _convert_expressions_v1(self, expressions: Dict) -> Dict:
        """转换VRM 1.0表情"""
        result = {}
        for expr_name, expr_data in expressions.items():
            schema_name = self.EXPRESSION_MAPPING.get(expr_name, expr_name)
            result[schema_name] = {
                "morph_target_binds": expr_data.get("morphTargetBinds", []),
                "material_color_binds": expr_data.get("materialColorBinds", []),
                "texture_transform_binds": expr_data.get("textureTransformBinds", []),
                "is_binary": expr_data.get("isBinary", False),
                "override_blink": expr_data.get("overrideBlink"),
                "override_look_at": expr_data.get("overrideLookAt"),
                "override_mouth": expr_data.get("overrideMouth")
            }
        return result
    
    def _convert_spring_bones(self, secondary_animation: Dict) -> Dict:
        """转换弹簧骨骼配置"""
        spring_bones = {
            "bone_groups": [],
            "colliders": []
        }
        
        for group in secondary_animation.get("boneGroups", []):
            spring_bones["bone_groups"].append({
                "comment": group.get("comment", ""),
                "stiffiness": group.get("stiffiness", 1.0),
                "gravity_power": group.get("gravityPower", 0.0),
                "gravity_direction": group.get("gravityDirection", {"x": 0, "y": -1, "z": 0}),
                "drag_force": group.get("dragForce", 0.4),
                "hit_radius": group.get("hitRadius", 0.02),
                "bones": group.get("bones", []),
                "collider_groups": group.get("colliderGroups", [])
            })
        
        for collider_group in secondary_animation.get("colliderGroups", []):
            spring_bones["colliders"].append({
                "node_index": collider_group.get("node"),
                "colliders": [
                    {
                        "offset": c.get("offset", {}),
                        "radius": c.get("radius", 0.0)
                    }
                    for c in collider_group.get("colliders", [])
                ]
            })
        
        return spring_bones
    
    def _convert_vrm_materials(self, materials: List[Dict]) -> List[Dict]:
        """转换VRM材质"""
        converted = []
        for mat in materials:
            extensions = mat.get("extensions", {})
            vrm_mat = extensions.get("VRMC_materials_mtoon") or extensions.get("VRM")
            
            if vrm_mat:
                converted.append({
                    "name": mat.get("name"),
                    "shader": "MToon",
                    "render_queue": vrm_mat.get("renderQueue", 2000),
                    "shade_color": vrm_mat.get("shadeColorFactor", [0, 0, 0]),
                    "shade_texture": vrm_mat.get("shadeMultiplyTexture", {}).get("index"),
                    "shading_shift": vrm_mat.get("shadingShiftFactor", 0.0),
                    "shading_toony": vrm_mat.get("shadingToonyFactor", 0.9),
                    "gi_equalization": vrm_mat.get("giEqualizationFactor", 0.9),
                    "matcap": vrm_mat.get("matcapTexture", {}).get("index"),
                    "rim_color": vrm_mat.get("parametricRimColorFactor", [0, 0, 0]),
                    "rim_lift": vrm_mat.get("parametricRimLiftFactor", 0.0),
                    "rim_fresnel_power": vrm_mat.get("parametricRimFresnelPowerFactor", 1.0),
                    "outline_width": vrm_mat.get("outlineWidthFactor", 0.0),
                    "outline_color": vrm_mat.get("outlineColorFactor", [0, 0, 0])
                })
            else:
                converted.append({
                    "name": mat.get("name"),
                    "shader": "Standard",
                    "pbr_metallic_roughness": mat.get("pbrMetallicRoughness", {})
                })
        
        return converted


# =============================================================================
# 场景图构建 (Scene Graph Construction)
# =============================================================================

class SceneGraphBuilder:
    """
    场景图构建器
    提供高效的场景层次结构管理和查询
    """
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.root_nodes: List[str] = []
        self.spatial_index: Dict[str, Any] = {}
    
    def add_node(self, entity: Entity, parent_id: Optional[str] = None) -> str:
        """
        添加节点到场景图
        
        Args:
            entity: 要添加的实体
            parent_id: 父节点ID（None表示根节点）
        
        Returns:
            节点ID
        """
        node_id = entity.entity_id
        
        node_data = {
            "entity": entity,
            "parent": parent_id,
            "children": [],
            "depth": 0,
            "world_transform": None  # 延迟计算
        }
        
        if parent_id:
            if parent_id in self.nodes:
                self.nodes[parent_id]["children"].append(node_id)
                node_data["depth"] = self.nodes[parent_id]["depth"] + 1
        else:
            self.root_nodes.append(node_id)
        
        self.nodes[node_id] = node_data
        
        # 更新空间索引
        self._update_spatial_index(entity)
        
        return node_id
    
    def remove_node(self, node_id: str) -> bool:
        """移除节点及其子树"""
        if node_id not in self.nodes:
            return False
        
        # 递归移除子节点
        children = self.nodes[node_id]["children"].copy()
        for child_id in children:
            self.remove_node(child_id)
        
        # 从父节点中移除引用
        parent_id = self.nodes[node_id]["parent"]
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id]["children"].remove(node_id)
        elif node_id in self.root_nodes:
            self.root_nodes.remove(node_id)
        
        del self.nodes[node_id]
        return True
    
    def get_world_transform(self, node_id: str) -> Optional[Transform]:
        """计算世界空间变换"""
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        entity = node["entity"]
        
        transform_comp = entity.get_component(ComponentType.TRANSFORM)
        if not transform_comp or not isinstance(transform_comp, TransformComponent):
            return None
        
        local_transform = transform_comp.transform
        
        # 递归计算世界变换
        parent_id = node["parent"]
        if parent_id:
            parent_world = self.get_world_transform(parent_id)
            if parent_world:
                # 这里简化处理，实际应进行矩阵乘法
                return Transform(
                    position=Vector3(
                        parent_world.position.x + local_transform.position.x,
                        parent_world.position.y + local_transform.position.y,
                        parent_world.position.z + local_transform.position.z
                    ),
                    rotation=local_transform.rotation,  # 简化：不考虑旋转组合
                    scale=Vector3(
                        parent_world.scale.x * local_transform.scale.x,
                        parent_world.scale.y * local_transform.scale.y,
                        parent_world.scale.z * local_transform.scale.z
                    )
                )
        
        return local_transform
    
    def query_frustum(self, frustum: Dict) -> List[Entity]:
        """
        视锥剔除查询
        
        Args:
            frustum: 视锥体定义
                {
                    "planes": [...],  # 六个平面
                    "position": [...],  # 观察者位置
                    "direction": [...]  # 观察方向
                }
        
        Returns:
            在视锥体内的实体列表
        """
        visible = []
        
        for node_id, node_data in self.nodes.items():
            entity = node_data["entity"]
            world_transform = self.get_world_transform(node_id)
            
            if world_transform and self._is_in_frustum(world_transform.position, frustum):
                visible.append(entity)
        
        return visible
    
    def query_radius(self, center: Vector3, radius: float) -> List[Entity]:
        """半径查询"""
        results = []
        
        for node_id, node_data in self.nodes.items():
            entity = node_data["entity"]
            world_transform = self.get_world_transform(node_id)
            
            if world_transform:
                distance = self._calculate_distance(world_transform.position, center)
                if distance <= radius:
                    results.append((entity, distance))
        
        # 按距离排序
        results.sort(key=lambda x: x[1])
        return [e for e, _ in results]
    
    def traverse(self, callback: Callable[[Entity, int], None], 
                 order: str = "pre") -> None:
        """
        遍历场景图
        
        Args:
            callback: 回调函数(entity, depth)
            order: 遍历顺序 ("pre", "post", "level")
        """
        if order == "pre":
            for root_id in self.root_nodes:
                self._traverse_pre(root_id, callback)
        elif order == "post":
            for root_id in self.root_nodes:
                self._traverse_post(root_id, callback)
        elif order == "level":
            self._traverse_level(callback)
    
    def _traverse_pre(self, node_id: str, callback: Callable, depth: int = 0) -> None:
        """前序遍历"""
        node = self.nodes[node_id]
        callback(node["entity"], depth)
        
        for child_id in node["children"]:
            self._traverse_pre(child_id, callback, depth + 1)
    
    def _traverse_post(self, node_id: str, callback: Callable, depth: int = 0) -> None:
        """后序遍历"""
        node = self.nodes[node_id]
        
        for child_id in node["children"]:
            self._traverse_post(child_id, callback, depth + 1)
        
        callback(node["entity"], depth)
    
    def _traverse_level(self, callback: Callable) -> None:
        """层级遍历"""
        from collections import deque
        
        queue = deque([(root_id, 0) for root_id in self.root_nodes])
        
        while queue:
            node_id, depth = queue.popleft()
            node = self.nodes[node_id]
            callback(node["entity"], depth)
            
            for child_id in node["children"]:
                queue.append((child_id, depth + 1))
    
    def _update_spatial_index(self, entity: Entity) -> None:
        """更新空间索引（简化实现）"""
        # 实际实现应使用八叉树或BVH
        pass
    
    def _is_in_frustum(self, position: Vector3, frustum: Dict) -> bool:
        """检查点是否在视锥体内（简化实现）"""
        # 实际实现应进行完整的视锥体测试
        return True
    
    def _calculate_distance(self, a: Vector3, b: Vector3) -> float:
        """计算两点距离"""
        import math
        return math.sqrt(
            (a.x - b.x) ** 2 + 
            (a.y - b.y) ** 2 + 
            (a.z - b.z) ** 2
        )
    
    def to_dict(self) -> Dict:
        """导出为字典"""
        return {
            "nodes": {
                node_id: {
                    "parent": node_data["parent"],
                    "children": node_data["children"],
                    "depth": node_data["depth"],
                    "entity": node_data["entity"].to_dict()
                }
                for node_id, node_data in self.nodes.items()
            },
            "root_nodes": self.root_nodes
        }


# =============================================================================
# 集成管理器 (Integration Manager)
# =============================================================================

class MetaverseSchemaManager:
    """
    元宇宙Schema集成管理器
    统一管理OpenXR、glTF、VRM等格式的转换和集成
    """
    
    def __init__(self):
        self.openxr_adapter = OpenXRAdapter()
        self.gltf_adapter = GLTFAdapter()
        self.vrm_adapter = VRMAdapter()
        self.scene_builder = SceneGraphBuilder()
        self.assets: Dict[str, Asset] = {}
        self.spaces: Dict[str, Space] = {}
    
    def import_scene(self, data: Dict, format_type: str) -> Space:
        """
        导入场景
        
        Args:
            data: 场景数据
            format_type: 格式类型 ("gltf", "vrm", "usd")
        
        Returns:
            Schema Space对象
        """
        if format_type.lower() == "gltf":
            space = self.gltf_adapter.import_gltf(data)
        elif format_type.lower() == "vrm":
            # VRM是个人化身，不是场景，这里返回一个包含化身的空间
            avatar_config = self.vrm_adapter.import_vrm(data)
            space = Space(name=avatar_config.get("name", "VRM Avatar"))
            space.metadata["avatar_config"] = avatar_config
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        self.spaces[space.space_id] = space
        
        # 构建场景图
        for entity in space.entities:
            self.scene_builder.add_node(entity, entity.parent_id)
        
        logger.info(f"Imported scene: {space.name} with {len(space.entities)} entities")
        return space
    
    def export_scene(self, space_id: str, format_type: str) -> Dict:
        """
        导出场景
        
        Args:
            space_id: 空间ID
            format_type: 目标格式 ("gltf")
        
        Returns:
            导出的数据字典
        """
        if space_id not in self.spaces:
            raise ValueError(f"Space not found: {space_id}")
        
        space = self.spaces[space_id]
        
        if format_type.lower() == "gltf":
            return self.gltf_adapter.export_gltf(space)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def register_asset(self, asset: Asset) -> str:
        """注册资产"""
        self.assets[asset.asset_id] = asset
        logger.info(f"Registered asset: {asset.name}")
        return asset.asset_id
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """获取资产"""
        return self.assets.get(asset_id)
    
    def create_entity_from_asset(self, asset_id: str, 
                                  position: Vector3 = None,
                                  name: str = None) -> Entity:
        """
        从资产创建实体
        
        Args:
            asset_id: 资产ID
            position: 初始位置
            name: 实体名称
        
        Returns:
            创建的实体
        """
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")
        
        entity = Entity(
            name=name or asset.name,
            entity_type=self._asset_type_to_entity_type(asset.asset_type)
        )
        
        # 添加变换组件
        transform = Transform(position=position or Vector3())
        entity.add_component(TransformComponent(transform=transform))
        
        # 添加渲染组件
        if asset.asset_type == AssetType.MODEL:
            entity.add_component(RenderComponent(mesh_uri=asset.content_uri))
        
        entity.metadata["asset_reference"] = asset_id
        
        return entity
    
    def _asset_type_to_entity_type(self, asset_type: AssetType) -> EntityType:
        """资产类型转实体类型"""
        mapping = {
            AssetType.MODEL: EntityType.OBJECT,
            AssetType.PREFAB: EntityType.OBJECT,
            AssetType.SCENE: EntityType.ENVIRONMENT,
        }
        return mapping.get(asset_type, EntityType.OBJECT)
    
    def setup_openxr_input(self, action_set_config: Dict) -> Dict:
        """
        设置OpenXR输入映射
        
        Args:
            action_set_config: 动作集配置
        
        Returns:
            输入映射配置
        """
        return self.openxr_adapter.create_input_mapping(
            action_set_config.get("name", "default"),
            action_set_config.get("bindings", {})
        )
    
    def serialize(self) -> Dict:
        """序列化管理器状态"""
        return {
            "spaces": {k: v.to_dict() for k, v in self.spaces.items()},
            "assets": {k: v.to_dict() for k, v in self.assets.items()},
            "scene_graph": self.scene_builder.to_dict()
        }
    
    def save_to_file(self, filepath: str) -> None:
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.serialize(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved to {filepath}")


# =============================================================================
# 使用示例 (Usage Examples)
# =============================================================================

def example_usage():
    """使用示例"""
    
    # 创建管理器
    manager = MetaverseSchemaManager()
    
    # 注册资产
    asset = Asset(
        name="科幻飞船",
        asset_type=AssetType.MODEL,
        content_uri="assets://models/spaceship.gltf",
        technical_specs={
            "polygon_count": 15000,
            "texture_resolution": "4K"
        }
    )
    manager.register_asset(asset)
    
    # 从资产创建实体
    entity = manager.create_entity_from_asset(
        asset.asset_id,
        position=Vector3(10, 0, -20),
        name="我的飞船"
    )
    
    # 添加交互组件
    interaction = InteractionComponent(
        interaction_type=InteractionType.GRAB,
        actions=[{"type": "pick_up"}, {"type": "pilot"}]
    )
    entity.add_component(interaction)
    
    # 创建空间并添加实体
    space = Space(name="科幻世界")
    space.add_entity(entity)
    
    # 注册空间
    manager.spaces[space.space_id] = space
    
    # 导出为glTF
    gltf_data = manager.export_scene(space.space_id, "gltf")
    print(json.dumps(gltf_data, indent=2))
    
    # 设置OpenXR输入
    input_config = manager.setup_openxr_input({
        "name": "gameplay",
        "bindings": {
            "grab": "/user/hand/left/input/grip",
            "teleport": "/user/hand/right/input/trigger"
        }
    })
    print("Input config:", input_config)
    
    # 保存状态
    manager.save_to_file("metaverse_scene.json")


if __name__ == "__main__":
    example_usage()
