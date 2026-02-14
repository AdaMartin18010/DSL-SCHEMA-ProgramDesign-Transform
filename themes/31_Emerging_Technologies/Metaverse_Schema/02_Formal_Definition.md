# 元宇宙Schema形式化定义 (Metaverse Schema Formal Definition)

## 1. 实体定义 (Entity Definition)

### 1.1 实体类型层次结构 (Entity Type Hierarchy)

```yaml
# 实体类型本体 (Entity Type Ontology)
metaverse_entity_types:
  Entity:
    abstract: true
    properties:
      - entity_id: UUID
      - created_at: Timestamp
      - updated_at: Timestamp
      - metadata: JSON
    
    subclasses:
      Avatar:
        description: "用户虚拟化身"
        properties:
          - user_id: Reference[User]
          - appearance: AppearanceConfig
          - skeleton: SkeletonDefinition
          - animations: AnimationSet
          - current_location: SpatialCoordinate
        
      Object:
        description: "虚拟世界中的物体"
        properties:
          - asset_reference: URI
          - physics_properties: PhysicsConfig
          - interaction_capabilities: InteractionSet
          - state_machine: StateDefinition
        
      Environment:
        description: "环境元素"
        abstract: true
        subclasses:
          Terrain:
            properties:
              - heightmap: URI
              - material_layers: MaterialStack
              - vegetation: VegetationSystem
          
          Lighting:
            properties:
              - light_type: Enum[Directional, Point, Spot, Area]
              - color: RGBA
              - intensity: Float
              - shadow_settings: ShadowConfig
          
          ParticleSystem:
            properties:
              - emitter_config: EmitterDefinition
              - particle_lifetime: DurationRange
              - rendering_material: MaterialReference
```

### 1.2 实体组件系统 (Entity Component System)

```typescript
// 组件接口定义 (Component Interface Definitions)
interface Component {
  componentId: UUID;
  entityId: UUID;
  componentType: string;
  version: SemanticVersion;
  enabled: boolean;
}

// 变换组件 (Transform Component)
interface TransformComponent extends Component {
  componentType: "Transform";
  localPosition: Vector3;
  localRotation: Quaternion;
  localScale: Vector3;
  parent: UUID | null;
  children: UUID[];
  
  // 世界空间计算
  getWorldPosition(): Vector3;
  getWorldRotation(): Quaternion;
  getWorldScale(): Vector3;
  getWorldMatrix(): Matrix4x4;
}

// 渲染组件 (Render Component)
interface RenderComponent extends Component {
  componentType: "Render";
  meshReference: URI;
  materialReferences: MaterialReference[];
  visibility: VisibilityConfig;
  lodSettings: LODConfig;
  castShadows: boolean;
  receiveShadows: boolean;
}

// 物理组件 (Physics Component)
interface PhysicsComponent extends Component {
  componentType: "Physics";
  bodyType: BodyType; // Static, Dynamic, Kinematic
  colliderShape: ColliderShape;
  mass: number;
  friction: number;
  restitution: number;
  useGravity: boolean;
  isTrigger: boolean;
}

// 交互组件 (Interaction Component)
interface InteractionComponent extends Component {
  componentType: "Interaction";
  interactionType: InteractionType;
  triggerShape: ColliderShape;
  actions: InteractionAction[];
  cooldown: Duration;
  requiresAuthority: boolean;
}

// 动画组件 (Animation Component)
interface AnimationComponent extends Component {
  componentType: "Animation";
  animatorController: URI;
  currentState: string;
  parameters: AnimationParameter[];
  layers: AnimationLayer[];
  blendTree: BlendTreeConfig;
}

// 音频组件 (Audio Component)
interface AudioComponent extends Component {
  componentType: "Audio";
  audioClip: URI;
  spatialBlend: number; // 0 = 2D, 1 = 3D
  volume: number;
  pitch: number;
  loop: boolean;
  minDistance: number;
  maxDistance: number;
  rolloffMode: RolloffMode;
}

// 脚本组件 (Script Component)
interface ScriptComponent extends Component {
  componentType: "Script";
  scriptSource: URI;
  scriptType: ScriptType; // Lua, Python, JavaScript, C#
  publicVariables: VariableDefinition[];
  executionOrder: number;
  updateMode: UpdateMode; // Update, FixedUpdate, LateUpdate
}
```

### 1.3 实体关系模型 (Entity Relationship Model)

```yaml
entity_relationships:
  ownership:
    type: "1:N"
    description: "用户拥有实体"
    constraints:
      - "用户可拥有多个实体"
      - "实体只能有一个所有者"
    
  containment:
    type: "N:1"
    description: "实体包含关系"
    examples:
      - "世界包含空间"
      - "空间包含实体"
      - "实体包含组件"
    
  attachment:
    type: "N:N"
    description: "实体附加关系"
    examples:
      - "化身穿戴装备"
      - "手持物品"
      - "坐骑关系"
    
  proximity:
    type: "动态"
    description: "空间邻近关系"
    computed: true
    triggers:
      - "进入触发区域"
      - "离开触发区域"
      - "距离变化"
```

## 2. 场景定义 (Scene Definition)

### 2.1 场景图结构 (Scene Graph Structure)

```yaml
# 场景图定义 (Scene Graph Definition)
scene_graph:
  root:
    type: "WorldRoot"
    properties:
      - world_id: UUID
      - world_name: String
      - coordinate_system: CoordinateSystem
    
  nodes:
    spatial_node:
      type: "Spatial"
      properties:
        - transform: TransformComponent
        - bounds: BoundingVolume
        - visibility: VisibilityFlags
      
    group_node:
      type: "Group"
      extends: "spatial_node"
      properties:
        - children: NodeReference[]
        - culling_mode: CullingMode
      
    instance_node:
      type: "Instance"
      extends: "spatial_node"
      properties:
        - prefab_reference: URI
        - instance_id: UUID
        - overrides: PropertyOverride[]
      
    portal_node:
      type: "Portal"
      extends: "spatial_node"
      properties:
        - target_space: SpaceReference
        - transition_type: TransitionType
        - loading_strategy: LoadingStrategy
      
    lod_node:
      type: "LOD"
      extends: "group_node"
      properties:
        - lod_levels: LODLevel[]
        - switching_distances: Float[]
        - hysteresis: Float
```

### 2.2 场景层次结构 (Scene Hierarchy)

```
World (世界)
├── Metadata (元数据)
│   ├── WorldSettings
│   ├── NavigationSettings
│   └── PhysicsSettings
│
├── GlobalSystems (全局系统)
│   ├── LightingSystem
│   ├── PhysicsSystem
│   ├── AudioSystem
│   └── NavigationSystem
│
├── Spaces (空间)
│   ├── Space_001
│   │   ├── Environment
│   │   │   ├── Terrain
│   │   │   ├── Skybox
│   │   │   └── Lighting
│   │   ├── Entities (实体)
│   │   │   ├── StaticObjects
│   │   │   ├── DynamicObjects
│   │   │   ├── Avatars
│   │   │   └── NPCs
│   │   └── Triggers (触发器)
│   │       ├── SpawnPoints
│   │       ├── Teleporters
│   │       └── EventZones
│   └── Space_002
│       └── ...
│
└── Portals (传送门)
    ├── Portal_001 (Space_001 ↔ Space_002)
    └── Portal_002 (Space_001 → Space_003)
```

### 2.3 空间分区系统 (Spatial Partitioning System)

```yaml
spatial_partitioning:
  octree:
    description: "八叉树空间划分"
    use_cases:
      - "视锥剔除"
      - "碰撞检测优化"
      - "光线追踪加速"
    parameters:
      max_depth: 8
      max_objects_per_node: 16
      min_node_size: 1.0  # 米
  
  grid:
    description: "均匀网格划分"
    use_cases:
      - "大规模开放世界"
      - "流式加载"
    parameters:
      cell_size: 100.0  # 米
      streaming_radius: 5  # 单元格
  
  bvh:
    description: "层次包围盒"
    use_cases:
      - "静态场景加速"
      - "复杂模型碰撞"
    build_strategy: "SAH优化"
```

### 2.4 场景序列化格式 (Scene Serialization Format)

```json
{
  "schema_version": "1.0.0",
  "world": {
    "id": "world-001",
    "name": "科幻都市",
    "settings": {
      "coordinate_system": "cartesian_meters",
      "physics_gravity": [0, -9.81, 0],
      "ambient_light": {"color": [0.2, 0.2, 0.3], "intensity": 0.5}
    }
  },
  "assets": {
    "prefabs": [
      {"id": "prefab-building-01", "uri": "assets://buildings/skyscraper_01.gltf"},
      {"id": "prefab-vehicle-01", "uri": "assets://vehicles/flying_car_01.gltf"}
    ],
    "materials": [
      {"id": "mat-glass", "uri": "assets://materials/glass_pbr.json"}
    ]
  },
  "spaces": [
    {
      "id": "space-downtown",
      "name": "市中心",
      "bounds": {
        "min": [-1000, 0, -1000],
        "max": [1000, 500, 1000]
      },
      "entities": [
        {
          "id": "entity-building-001",
          "name": "摩天大楼A",
          "prefab": "prefab-building-01",
          "transform": {
            "position": [100, 0, -200],
            "rotation": [0, 45, 0],
            "scale": [1, 1.5, 1]
          },
          "components": {
            "render": {"lod_distances": [50, 150, 500]},
            "physics": {"body_type": "static", "collider": "mesh"}
          }
        }
      ],
      "lighting": {
        "sun": {
          "type": "directional",
          "direction": [0.5, -0.8, 0.3],
          "color": [1.0, 0.95, 0.8],
          "intensity": 1.2,
          "cast_shadows": true
        }
      }
    }
  ],
  "portals": [
    {
      "id": "portal-001",
      "source_space": "space-downtown",
      "source_position": [500, 0, 0],
      "target_space": "space-suburbs",
      "target_position": [-400, 0, 100],
      "transition": "fade"
    }
  ]
}
```

## 3. 交互定义 (Interaction Definition)

### 3.1 交互类型分类 (Interaction Type Classification)

```yaml
interaction_types:
  # 物理交互 (Physical Interaction)
  physical:
    collision:
      description: "碰撞检测"
      types:
        - "enter": 进入碰撞
        - "stay": 持续碰撞
        - "exit": 离开碰撞
      parameters:
        - contact_points
        - impact_force
        - collision_normal
    
    grab:
      description: "抓取物体"
      modes:
        - "kinematic": 运动学抓取
        - "physics": 物理抓取
      constraints:
        - "one-handed"
        - "two-handed"
        - "precision"
    
    throw:
      description: "投掷物体"
      parameters:
        - initial_velocity
        - angular_velocity
        - release_point
  
  # 界面交互 (UI Interaction)
  ui:
    raycast:
      description: "射线检测"
      sources:
        - "head": 头部指向
        - "hand": 手部指向
        - "controller": 控制器指向
      feedback:
        - "visual": 高亮、光标
        - "haptic": 触觉反馈
        - "audio": 声音提示
    
    gesture:
      description: "手势识别"
      gestures:
        - "pinch": 捏合
        - "grab": 握拳
        - "point": 指向
        - "swipe": 滑动
        - "wave": 挥手
    
    voice:
      description: "语音命令"
      processing:
        - "wake_word": 唤醒词
        - "intent_recognition": 意图识别
        - "entity_extraction": 实体提取
  
  # 社交交互 (Social Interaction)
  social:
    presence:
      description: "存在感"
      indicators:
        - "avatar_visibility": 化身可见性
        - "nameplate": 名牌显示
        - "activity_indicator": 活动指示器
    
    communication:
      description: "通信"
      channels:
        - "proximity_voice": 近距离语音
        - "global_voice": 全局语音
        - "text_chat": 文字聊天
        - "emotes": 表情动作
    
    collaboration:
      description: "协作"
      features:
        - "shared_workspace": 共享工作区
        - "synchronized_actions": 同步动作
        - "hand_raising": 举手
        - "voting": 投票
```

### 3.2 交互状态机 (Interaction State Machine)

```yaml
interaction_state_machine:
  states:
    idle:
      description: "空闲状态"
      transitions:
        - target: "hover"
          condition: "射线检测到可交互对象"
        - target: "gesture_detected"
          condition: "识别到手势"
    
    hover:
      description: "悬停状态"
      actions:
        - "显示高亮"
        - "显示提示信息"
      transitions:
        - target: "idle"
          condition: "射线移开"
        - target: "selected"
          condition: "用户确认选择"
    
    selected:
      description: "选中状态"
      actions:
        - "显示选择效果"
        - "准备交互"
      transitions:
        - target: "interacting"
          condition: "开始交互动作"
        - target: "idle"
          condition: "取消选择"
    
    interacting:
      description: "交互中状态"
      sub_states:
        - "grabbing"
        - "manipulating"
        - "using"
      transitions:
        - target: "idle"
          condition: "交互完成或取消"
    
    gesture_detected:
      description: "手势已识别"
      actions:
        - "执行对应手势命令"
      transitions:
        - target: "idle"
          condition: "手势结束"
```

### 3.3 输入映射系统 (Input Mapping System)

```yaml
input_mapping:
  devices:
    vr_controller:
      bindings:
        grip_button: "grab"
        trigger_button: "select/use"
        primary_button: "menu"
        secondary_button: "alternate"
        joystick: "locomotion"
        joystick_click: "teleport"
      haptics:
        grab_feedback: {duration: 50ms, amplitude: 0.5}
        collision_feedback: {duration: 100ms, amplitude: 0.8}
    
    hand_tracking:
      bindings:
        pinch: "select/grab"
        grab_gesture: "grab"
        point: "ui_raycast"
        thumbs_up: "like/confirm"
      gestures:
        confidence_threshold: 0.8
        smoothing_factor: 0.3
    
    keyboard_mouse:
      bindings:
        wasd: "locomotion"
        mouse_move: "look"
        mouse_left: "select/interact"
        mouse_right: "alternate/rotate"
        space: "jump"
        e: "use"
        tab: "inventory/menu"
    
    gamepad:
      bindings:
        left_stick: "locomotion"
        right_stick: "look"
        a_button: "jump/confirm"
        b_button: "cancel/back"
        x_button: "interact"
        y_button: "inventory"
        triggers: "grab/use"
        bumpers: "switch_hand"
```

## 4. 资产定义 (Asset Definition)

### 4.1 资产类型体系 (Asset Type System)

```yaml
asset_types:
  # 3D模型 (3D Models)
  model:
    formats:
      primary: "glTF 2.0"
      supported: ["FBX", "OBJ", "USD", "VRM"]
    components:
      - meshes
      - materials
      - textures
      - skeletons
      - animations
      - morph_targets
    optimization:
      - "LOD链"
      - "遮挡剔除数据"
      - "碰撞网格"
  
  # 材质 (Materials)
  material:
    workflow: "PBR Metallic-Roughness"
    properties:
      - base_color: Texture | Color
      - metallic: Texture | Float
      - roughness: Texture | Float
      - normal: Texture
      - occlusion: Texture
      - emissive: Texture | Color
    variants:
      - "透明材质"
      - "次表面散射"
      - "各向异性"
      - "清漆"
  
  # 纹理 (Textures)
  texture:
    formats: ["KTX2", "PNG", "JPEG", "WebP"]
    compression:
      - "BC1-BC7 (桌面)"
      - "ASTC (移动端)"
      - "ETC2 (移动端)"
    properties:
      - resolution
      - color_space
      - mipmaps
      - wrap_mode
      - filter_mode
  
  # 音频 (Audio)
  audio:
    formats: ["OGG", "WAV", "MP3"]
    types:
      - "2D音效"
      - "3D空间音效"
      - "环境音"
      - "音乐"
    properties:
      - sample_rate
      - bit_depth
      - channels
      - compression
  
  # 动画 (Animation)
  animation:
    types:
      - "骨骼动画"
      - "变形动画"
      - "顶点动画"
      - "物理动画"
    properties:
      - duration
      - frame_rate
      - loop
      - blend_mode
      - root_motion
  
  # 预制体 (Prefab)
  prefab:
    description: "可复用的实体模板"
    components:
      - entity_hierarchy
      - component_configurations
      - default_values
      - exposed_variables
  
  # 脚本 (Script)
  script:
    languages: ["Lua", "Python", "JavaScript", "C#"]
    types:
      - "行为脚本"
      - "交互脚本"
      - "游戏逻辑"
      - "工具脚本"
```

### 4.2 资产管理元数据 (Asset Management Metadata)

```json
{
  "asset_metadata": {
    "asset_id": "asset-12345",
    "name": "科幻飞船",
    "description": "未来风格的单人驾驶飞船",
    "type": "model",
    
    "version": {
      "major": 1,
      "minor": 2,
      "patch": 0,
      "created_at": "2024-01-15T10:30:00Z"
    },
    
    "author": {
      "id": "user-789",
      "name": "艺术家A",
      "wallet_address": "0x..."
    },
    
    "license": {
      "type": "CC-BY-SA-4.0",
      "commercial_use": true,
      "attribution_required": true,
      "share_alike": true
    },
    
    "technical_specs": {
      "polygon_count": 15000,
      "texture_resolution": "4K",
      "material_count": 5,
      "bone_count": 32,
      "animation_count": 8,
      "file_size_mb": 45.2,
      "supported_platforms": ["PC", "VR", "Mobile"]
    },
    
    "optimization": {
      "lod_levels": [
        {"distance": 0, "polygon_count": 15000},
        {"distance": 50, "polygon_count": 7500},
        {"distance": 100, "polygon_count": 3000},
        {"distance": 200, "polygon_count": 500}
      ],
      "occlusion_culling": true,
      "texture_atlas": false
    },
    
    "tags": ["科幻", "载具", "飞行器", "单人"],
    "categories": ["交通工具", "飞行器"],
    
    "dependencies": [
      {"type": "texture", "asset_id": "tex-001", "required": true},
      {"type": "shader", "asset_id": "shader-001", "required": true}
    ],
    
    "blockchain": {
      "token_id": "12345",
      "contract_address": "0x...",
      "chain": "ethereum",
      "ownership_verified": true,
      "last_transfer": "2024-06-01T12:00:00Z"
    }
  }
}
```

### 4.3 资产引用系统 (Asset Reference System)

```yaml
asset_referencing:
  uri_schemes:
    local:
      scheme: "file://"
      description: "本地文件系统"
      example: "file:///assets/models/ship.gltf"
    
    package:
      scheme: "package://"
      description: "包内资源"
      example: "package://my_package/entities/player.prefab"
    
    remote:
      scheme: "https://"
      description: "远程服务器"
      example: "https://cdn.example.com/assets/ship.gltf"
    
    ipfs:
      scheme: "ipfs://"
      description: "IPFS去中心化存储"
      example: "ipfs://QmXxXxXxXx.../ship.gltf"
    
    blockchain:
      scheme: "blockchain://"
      description: "区块链存储"
      example: "blockchain://ethereum/0x.../token/123"
  
  resolution_strategy:
    order:
      - "缓存检查"
      - "本地资源"
      - "CDN资源"
      - "IPFS资源"
    
    fallback:
      - "使用占位资源"
      - "显示加载错误"
      - "异步加载低分辨率版本"
```

## 5. 形式化Schema定义 (Formal Schema Definition)

### 5.1 JSON Schema定义 (JSON Schema Definition)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://metaverse-schema.org/v1/entity",
  "title": "Metaverse Entity Schema",
  "type": "object",
  "required": ["entity_id", "entity_type", "transform"],
  "properties": {
    "entity_id": {
      "type": "string",
      "format": "uuid",
      "description": "全局唯一标识符"
    },
    "entity_type": {
      "type": "string",
      "enum": ["Avatar", "Object", "Environment", "Trigger", "Light", "Camera"]
    },
    "name": {
      "type": "string",
      "maxLength": 256
    },
    "transform": {
      "type": "object",
      "required": ["position", "rotation", "scale"],
      "properties": {
        "position": {
          "type": "array",
          "items": {"type": "number"},
          "minItems": 3,
          "maxItems": 3
        },
        "rotation": {
          "type": "array",
          "items": {"type": "number"},
          "minItems": 4,
          "maxItems": 4,
          "description": "Quaternion [x, y, z, w]"
        },
        "scale": {
          "type": "array",
          "items": {"type": "number"},
          "minItems": 3,
          "maxItems": 3,
          "default": [1, 1, 1]
        }
      }
    },
    "parent_id": {
      "type": "string",
      "format": "uuid",
      "description": "父实体ID"
    },
    "components": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/component"
      }
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"}
    },
    "metadata": {
      "type": "object"
    },
    "visibility": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": true},
        "cast_shadows": {"type": "boolean", "default": true},
        "receive_shadows": {"type": "boolean", "default": true},
        "layer_mask": {"type": "integer", "default": 1}
      }
    }
  },
  
  "definitions": {
    "component": {
      "type": "object",
      "required": ["component_type"],
      "properties": {
        "component_id": {
          "type": "string",
          "format": "uuid"
        },
        "component_type": {
          "type": "string"
        },
        "enabled": {
          "type": "boolean",
          "default": true
        },
        "properties": {
          "type": "object"
        }
      }
    }
  }
}
```

### 5.2 GraphQL Schema定义 (GraphQL Schema Definition)

```graphql
# 标量类型
scalar UUID
scalar Timestamp
scalar Vector3
scalar Quaternion
scalar JSON
scalar URI

# 实体接口
interface Entity {
  id: UUID!
  type: EntityType!
  name: String
  transform: Transform!
  parent: Entity
  children: [Entity!]!
  components: [Component!]!
  tags: [String!]!
  createdAt: Timestamp!
  updatedAt: Timestamp!
}

# 实体类型枚举
enum EntityType {
  AVATAR
  OBJECT
  ENVIRONMENT
  TRIGGER
  LIGHT
  CAMERA
  PARTICLE_SYSTEM
}

# 变换类型
type Transform {
  position: Vector3!
  rotation: Quaternion!
  scale: Vector3!
  worldMatrix: [[Float!]!]!
  parent: Transform
}

# 组件接口
interface Component {
  id: UUID!
  entity: Entity!
  type: String!
  enabled: Boolean!
}

# 渲染组件
type RenderComponent implements Component {
  id: UUID!
  entity: Entity!
  type: String!
  enabled: Boolean!
  mesh: Mesh
  materials: [Material!]!
  visibility: VisibilityConfig!
  lodSettings: LODConfig!
}

# 物理组件
type PhysicsComponent implements Component {
  id: UUID!
  entity: Entity!
  type: String!
  enabled: Boolean!
  bodyType: BodyType!
  mass: Float!
  velocity: Vector3!
  angularVelocity: Vector3!
  useGravity: Boolean!
  colliders: [Collider!]!
}

# 世界类型
type World {
  id: UUID!
  name: String!
  description: String
  owner: User!
  spaces: [Space!]!
  settings: WorldSettings!
  createdAt: Timestamp!
  updatedAt: Timestamp!
}

# 空间类型
type Space {
  id: UUID!
  world: World!
  name: String!
  bounds: BoundingBox!
  entities: [Entity!]!
  lighting: LightingSettings!
  physics: PhysicsSettings!
}

# 用户类型
type User {
  id: UUID!
  username: String!
  walletAddress: String
  avatar: Avatar
  inventory: [Asset!]!
  friends: [User!]!
  presence: PresenceStatus!
}

# 化身类型
type Avatar implements Entity {
  id: UUID!
  type: EntityType!
  name: String
  transform: Transform!
  parent: Entity
  children: [Entity!]!
  components: [Component!]!
  tags: [String!]!
  createdAt: Timestamp!
  updatedAt: Timestamp!
  user: User!
  appearance: AppearanceConfig!
  animations: AnimationState!
}

# 资产类型
type Asset {
  id: UUID!
  name: String!
  type: AssetType!
  uri: URI!
  metadata: JSON!
  owner: User
  license: LicenseInfo
  version: VersionInfo!
}

# 查询根类型
type Query {
  # 实体查询
  entity(id: UUID!): Entity
  entities(
    spaceId: UUID
    type: EntityType
    tags: [String!]
    bounds: BoundingBoxInput
    limit: Int = 100
    offset: Int = 0
  ): [Entity!]!
  
  # 世界查询
  world(id: UUID!): World
  worlds(
    ownerId: UUID
    public: Boolean
    limit: Int = 20
    offset: Int = 0
  ): [World!]!
  
  # 用户查询
  user(id: UUID!): User
  me: User
  
  # 资产查询
  asset(id: UUID!): Asset
  assets(
    ownerId: UUID
    type: AssetType
    tags: [String!]
    limit: Int = 50
    offset: Int = 0
  ): [Asset!]!
}

# 变更根类型
type Mutation {
  # 实体操作
  createEntity(input: CreateEntityInput!): Entity!
  updateEntity(id: UUID!, input: UpdateEntityInput!): Entity!
  deleteEntity(id: UUID!): Boolean!
  
  # 世界操作
  createWorld(input: CreateWorldInput!): World!
  updateWorld(id: UUID!, input: UpdateWorldInput!): World!
  deleteWorld(id: UUID!): Boolean!
  
  # 用户操作
  updateUser(id: UUID!, input: UpdateUserInput!): User!
  
  # 资产操作
  uploadAsset(input: UploadAssetInput!): Asset!
  updateAsset(id: UUID!, input: UpdateAssetInput!): Asset!
  transferAsset(id: UUID!, toUserId: UUID!): Asset!
}

# 订阅根类型
type Subscription {
  # 实体更新
  entityUpdates(spaceId: UUID): EntityUpdate!
  
  # 用户存在状态
  presenceUpdates(userIds: [UUID!]): PresenceUpdate!
  
  # 世界事件
  worldEvents(worldId: UUID!): WorldEvent!
}
```

## 6. 验证规则 (Validation Rules)

### 6.1 实体验证 (Entity Validation)

```yaml
validation_rules:
  entity_id:
    rule: "必须是有效的UUID v4"
    error_code: "E001"
  
  transform:
    position:
      rule: "数值范围必须在 ±1,000,000 内"
      error_code: "E002"
    rotation:
      rule: "必须是单位四元数"
      error_code: "E003"
    scale:
      rule: "所有分量必须大于0"
      error_code: "E004"
  
  components:
    unique_types:
      rule: "同一实体不能有多个同类型组件（除特定允许外）"
      error_code: "E005"
    dependencies:
      rule: "组件依赖必须满足（如Render需要Transform）"
      error_code: "E006"
  
  hierarchy:
    depth:
      rule: "层级深度不能超过256层"
      error_code: "E007"
    cycle:
      rule: "不能形成循环引用"
      error_code: "E008"
```

### 6.2 场景验证 (Scene Validation)

```yaml
scene_validation:
  bounds:
    rule: "实体必须在空间边界内"
    tolerance: 0.001
    error_code: "S001"
  
  portals:
    bidirectional:
      rule: "双向传送门必须成对配置"
      error_code: "S002"
    
    connectivity:
      rule: "所有空间必须可达"
      error_code: "S003"
  
  lighting:
    intensity:
      rule: "光源强度必须在合理范围内"
      range: [0, 100000]
      error_code: "S004"
    
    shadow_count:
      rule: "实时阴影光源数量不能超过限制"
      limit: 4
      error_code: "S005"
```

---

**相关文档：**
- [01_Overview.md](./01_Overview.md) - 概述
- [03_Standards.md](./03_Standards.md) - 标准对标
- [04_Transformation.md](./04_Transformation.md) - 转换规则
- [05_Case_Studies.md](./05_Case_Studies.md) - 应用案例
