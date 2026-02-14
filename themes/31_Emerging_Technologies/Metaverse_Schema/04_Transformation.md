# 元宇宙Schema转换规则 (Metaverse Schema Transformation)

## 1. 转换概述 (Transformation Overview)

### 1.1 转换目标 (Transformation Goals)

```yaml
transformation_goals:
  format_conversion:
    - "glTF ↔ 内部场景图"
    - "VRM ↔ Avatar系统"
    - "OpenXR ↔ 输入系统"
    - "USD ↔ 场景合成"
  
  storage_optimization:
    - "二进制序列化"
    - "差异压缩"
    - "LOD链生成"
    - "纹理压缩"
  
  runtime_efficiency:
    - "GPU友好格式"
    - "内存布局优化"
    - "流式加载支持"
    - "增量更新"
```

### 1.2 转换架构 (Transformation Architecture)

```
┌──────────────────────────────────────────────────────────────────┐
│                      转换管道 (Transformation Pipeline)            │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │ 源格式   │───▶│ 中间表示 │───▶│ 目标格式 │───▶│ 验证/优化│   │
│  │ Source   │    │  IR      │    │ Target   │    │ Validate │   │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│        │              │              │              │           │
│        ▼              ▼              ▼              ▼           │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│   │ glTF    │   │ 场景图  │   │ PostgreSQL│   │ 校验和  │        │
│   │ VRM     │   │ 节点树  │   │ JSONB    │   │ 完整性  │        │
│   │ USD     │   │ 组件集  │   │ 二进制   │   │ 优化    │        │
│   │ FBX     │   │         │   │          │   │         │        │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

## 2. 格式转换规则 (Format Transformation Rules)

### 2.1 glTF 转换规则 (glTF Transformation)

```yaml
gltf_transformation_rules:
  import:
    scene_to_space:
      rule: "glTF.scene → Space"
      steps:
        - "解析场景图结构"
        - "转换节点为实体"
        - "提取全局设置"
      
    node_to_entity:
      rule: "glTF.node → Entity"
      mapping:
        transform: "matrix/translation/rotation/scale → TransformComponent"
        mesh: "mesh → RenderComponent + MeshReference"
        camera: "camera → CameraComponent"
        skin: "skin → SkinComponent"
        children: "递归处理子节点"
      
    mesh_to_geometry:
      rule: "glTF.mesh → Mesh"
      steps:
        - "提取顶点数据"
        - "生成索引缓冲区"
        - "创建子网格"
        - "计算包围盒"
      
    material_conversion:
      rule: "glTF.material → Material"
      pbr_mapping:
        baseColorFactor: "albedoColor"
        baseColorTexture: "albedoTexture"
        metallicFactor: "metallic"
        roughnessFactor: "roughness"
        metallicRoughnessTexture: "metallicRoughnessTexture"
        normalTexture: "normalMap"
        occlusionTexture: "occlusionMap"
        emissiveTexture: "emissiveMap"
        emissiveFactor: "emissiveColor"
      
    animation_conversion:
      rule: "glTF.animation → AnimationClip"
      channel_mapping:
        translation: "Position"
        rotation: "Rotation"
        scale: "Scale"
        weights: "BlendShape"
      sampler_interpolation:
        LINEAR: "Linear"
        STEP: "Step"
        CUBICSPLINE: "CubicSpline"
  
  export:
    space_to_scene:
      rule: "Space → glTF.scene"
      steps:
        - "收集所有实体"
        - "构建节点层次"
        - "生成glTF结构"
      
    entity_to_node:
      rule: "Entity → glTF.node"
      mapping:
        TransformComponent: "matrix/translation/rotation/scale"
        RenderComponent: "mesh"
        CameraComponent: "camera"
        SkinComponent: "skin"
```

### 2.2 VRM 转换规则 (VRM Transformation)

```yaml
vrm_transformation_rules:
  import:
    humanoid_conversion:
      rule: "VRM.humanoid → AvatarSkeleton"
      bone_mapping:
        VRM.hips: "Avatar.root"
        VRM.spine: "Avatar.spine[0]"
        VRM.chest: "Avatar.spine[1]"
        VRM.neck: "Avatar.neck"
        VRM.head: "Avatar.head"
        VRM.leftUpperLeg: "Avatar.leftLeg.upper"
        VRM.leftLowerLeg: "Avatar.leftLeg.lower"
        VRM.leftFoot: "Avatar.leftLeg.foot"
        VRM.rightUpperLeg: "Avatar.rightLeg.upper"
        VRM.rightLowerLeg: "Avatar.rightLeg.lower"
        VRM.rightFoot: "Avatar.rightLeg.foot"
        VRM.leftUpperArm: "Avatar.leftArm.upper"
        VRM.leftLowerArm: "Avatar.leftArm.lower"
        VRM.leftHand: "Avatar.leftArm.hand"
        VRM.rightUpperArm: "Avatar.rightArm.upper"
        VRM.rightLowerArm: "Avatar.rightArm.lower"
        VRM.rightHand: "Avatar.rightArm.hand"
      
    expression_conversion:
      rule: "VRM.expressions → AvatarExpressionSet"
      mapping:
        happy: "ExpressionType.HAPPY"
        angry: "ExpressionType.ANGRY"
        sad: "ExpressionType.SAD"
        surprised: "ExpressionType.SURPRISED"
        relaxed: "ExpressionType.RELAXED"
        neutral: "ExpressionType.NEUTRAL"
        blink: "ExpressionType.BLINK"
        lookUp: "ExpressionType.LOOK_UP"
        lookDown: "ExpressionType.LOOK_DOWN"
        lookLeft: "ExpressionType.LOOK_LEFT"
        lookRight: "ExpressionType.LOOK_RIGHT"
      
    spring_bone_conversion:
      rule: "VRM.springBone → SpringBoneComponent"
      parameter_mapping:
        dragForce: "drag"
        gravityDir: "gravity.direction"
        gravityPower: "gravity.strength"
        stiffiness: "stiffness"
        hitRadius: "collider.radius"
      
    material_conversion:
      rule: "VRM.material → AvatarMaterial"
      shader_mapping:
        VRM/MToon: "MaterialType.CARTOON"
          - litColor: "baseColor"
          - shadeColor: "shadowColor"
          - normalMap: "normalTexture"
          - emissionMap: "emissiveTexture"
          - matcap: "matcapTexture"
          - rimColor: "rimColor"
          - outline: "outlineSettings"
        VRM/Unlit: "MaterialType.UNLIT"
        VRM/Standard: "MaterialType.PBR"
  
  meta_conversion:
    rule: "VRM.meta → AssetMetadata"
    fields:
      title: "asset.name"
      version: "asset.version"
      author: "asset.creator"
      contactInformation: "asset.contact"
      reference: "asset.reference"
      allowed_user: "asset.usage.allowedUsers"
      violent_usage: "asset.usage.violent"
      sexual_usage: "asset.usage.sexual"
      commercial_usage: "asset.usage.commercial"
      license: "asset.license.type"
```

### 2.3 OpenXR 转换规则 (OpenXR Transformation)

```yaml
openxr_transformation_rules:
  space_conversion:
    openxr_to_schema:
      XrReferenceSpaceType_VIEW: "ViewSpace"
      XrReferenceSpaceType_LOCAL: "LocalSpace"
      XrReferenceSpaceType_LOCAL_FLOOR: "LocalFloorSpace"
      XrReferenceSpaceType_STAGE: "StageSpace"
      XrReferenceSpaceType_UNBOUNDED: "UnboundedSpace"
    
    pose_conversion:
      XrPosef_to_Transform: |
        position = [pose.position.x, pose.position.y, pose.position.z]
        rotation = [pose.orientation.x, pose.orientation.y, 
                    pose.orientation.z, pose.orientation.w]
  
  input_conversion:
    action_to_component:
      boolean_action: "ButtonInput"
      float_action: "AxisInput"
      vector2_action: "Vector2Input"
      pose_action: "TransformInput"
      haptic_action: "HapticOutput"
    
    subaction_path_mapping:
      /user/hand/left: "InputSource.LEFT_HAND"
      /user/hand/right: "InputSource.RIGHT_HAND"
      /user/head: "InputSource.HEAD"
      /user/gamepad: "InputSource.GAMEPAD"
  
  view_conversion:
    xrview_to_camera:
      view.pose: "camera.transform"
      view.fov: "camera.fieldOfView"
      view.pose.orientation: "camera.rotation"
      view.pose.position: "camera.position"
```

## 3. 数据库存储实现 (Database Storage Implementation)

### 3.1 PostgreSQL Schema 设计

```sql
-- =====================================================
-- 元宇宙Schema PostgreSQL 存储实现
-- Metaverse Schema PostgreSQL Storage Implementation
-- 版本: 1.0.0
-- =====================================================

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- 空间数据支持
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 文本搜索

-- =====================================================
-- 1. 核心类型定义
-- =====================================================

-- 实体类型枚举
CREATE TYPE entity_type AS ENUM (
    'AVATAR',
    'OBJECT', 
    'ENVIRONMENT',
    'TRIGGER',
    'LIGHT',
    'CAMERA',
    'PARTICLE_SYSTEM'
);

-- 组件类型枚举
CREATE TYPE component_type AS ENUM (
    'TRANSFORM',
    'RENDER',
    'PHYSICS',
    'CAMERA',
    'LIGHT',
    'AUDIO',
    'ANIMATION',
    'SCRIPT',
    'INTERACTION',
    'PARTICLE',
    'SPRING_BONE'
);

-- 资产类型枚举
CREATE TYPE asset_type AS ENUM (
    'MODEL',
    'MATERIAL',
    'TEXTURE',
    'AUDIO',
    'ANIMATION',
    'PREFAB',
    'SCRIPT',
    'SCENE'
);

-- 空间类型枚举
CREATE TYPE space_type AS ENUM (
    'WORLD_ROOT',
    'SPATIAL',
    'GROUP',
    'INSTANCE',
    'PORTAL',
    'LOD'
);

-- 物理体类型枚举
CREATE TYPE body_type AS ENUM ('STATIC', 'DYNAMIC', 'KINEMATIC');

-- 交互类型枚举
CREATE TYPE interaction_type AS ENUM (
    'COLLISION',
    'GRAB',
    'USE',
    'RAYCAST',
    'GESTURE',
    'VOICE'
);

-- =====================================================
-- 2. 核心表定义
-- =====================================================

-- 用户表
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(256) UNIQUE,
    wallet_address VARCHAR(64) UNIQUE,
    profile_data JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) DEFAULT 'active'
);

-- 世界表
CREATE TABLE worlds (
    world_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(256) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(user_id),
    configuration JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    max_capacity INTEGER DEFAULT 1000,
    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 空间表
CREATE TABLE spaces (
    space_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    world_id UUID NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    name VARCHAR(256) NOT NULL,
    space_type space_type DEFAULT 'SPATIAL',
    bounds JSONB NOT NULL,  -- {min: [x,y,z], max: [x,y,z]}
    spawn_points JSONB DEFAULT '[]',
    settings JSONB DEFAULT '{}',
    scene_graph JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 实体表
CREATE TABLE entities (
    entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    space_id UUID REFERENCES spaces(space_id) ON DELETE CASCADE,
    entity_type entity_type NOT NULL,
    name VARCHAR(256),
    parent_id UUID REFERENCES entities(entity_id),
    transform JSONB NOT NULL DEFAULT '{
        "position": [0,0,0],
        "rotation": [0,0,0,1],
        "scale": [1,1,1]
    }',
    visibility JSONB DEFAULT '{
        "enabled": true,
        "cast_shadows": true,
        "receive_shadows": true
    }',
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 组件表
CREATE TABLE components (
    component_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    component_type component_type NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 资产表
CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_type asset_type NOT NULL,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    content_uri TEXT NOT NULL,
    owner_id UUID REFERENCES users(user_id),
    metadata JSONB DEFAULT '{}',
    technical_specs JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    dependencies UUID[] DEFAULT '{}',
    blockchain_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 化身表 (VRM专用)
CREATE TABLE avatars (
    avatar_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    asset_id UUID REFERENCES assets(asset_id),
    name VARCHAR(256),
    skeleton_data JSONB NOT NULL,  -- 骨骼定义
    expression_set JSONB DEFAULT '{}',  -- 表情集合
    spring_bone_config JSONB DEFAULT '{}',  -- 弹簧骨骼配置
    appearance JSONB DEFAULT '{}',  -- 外观配置
    current_space_id UUID REFERENCES spaces(space_id),
    current_transform JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 交互表
CREATE TABLE interactions (
    interaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    interaction_type interaction_type NOT NULL,
    trigger_shape JSONB,  -- 触发器形状定义
    actions JSONB NOT NULL,  -- 动作定义
    cooldown_ms INTEGER DEFAULT 0,
    requires_authority BOOLEAN DEFAULT false,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 传送门表
CREATE TABLE portals (
    portal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(256),
    source_space_id UUID NOT NULL REFERENCES spaces(space_id),
    source_position JSONB NOT NULL,
    target_space_id UUID NOT NULL REFERENCES spaces(space_id),
    target_position JSONB NOT NULL,
    transition_type VARCHAR(64) DEFAULT 'fade',
    loading_strategy VARCHAR(64) DEFAULT 'async',
    is_bidirectional BOOLEAN DEFAULT false,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. 索引优化
-- =====================================================

-- 实体表索引
CREATE INDEX idx_entities_space ON entities(space_id);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_parent ON entities(parent_id);
CREATE INDEX idx_entities_tags ON entities USING GIN(tags);

-- 组件表索引
CREATE INDEX idx_components_entity ON components(entity_id);
CREATE INDEX idx_components_type ON components(component_type);

-- 空间表索引
CREATE INDEX idx_spaces_world ON spaces(world_id);

-- 资产表索引
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_owner ON assets(owner_id);
CREATE INDEX idx_assets_tags ON assets USING GIN(tags);

-- 用户表索引
CREATE INDEX idx_users_wallet ON users(wallet_address);
CREATE INDEX idx_users_username ON users USING gin(username gin_trgm_ops);

-- 化身表索引
CREATE INDEX idx_avatars_user ON avatars(user_id);
CREATE INDEX idx_avatars_space ON avatars(current_space_id);

-- =====================================================
-- 4. 触发器和函数
-- =====================================================

-- 自动更新时间戳函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为各表创建更新时间戳触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_worlds_updated_at BEFORE UPDATE ON worlds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_spaces_updated_at BEFORE UPDATE ON spaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_components_updated_at BEFORE UPDATE ON components
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_avatars_updated_at BEFORE UPDATE ON avatars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 实体层级验证函数
CREATE OR REPLACE FUNCTION validate_entity_hierarchy()
RETURNS TRIGGER AS $$
DECLARE
    parent_depth INTEGER;
    current_depth INTEGER;
BEGIN
    -- 检查循环引用
    IF NEW.parent_id IS NOT NULL THEN
        IF NEW.parent_id = NEW.entity_id THEN
            RAISE EXCEPTION 'Entity cannot be its own parent';
        END IF;
        
        -- 检查是否会导致循环
        WITH RECURSIVE hierarchy AS (
            SELECT entity_id, parent_id, 1 as depth
            FROM entities
            WHERE entity_id = NEW.parent_id
            UNION ALL
            SELECT e.entity_id, e.parent_id, h.depth + 1
            FROM entities e
            JOIN hierarchy h ON e.entity_id = h.parent_id
            WHERE h.depth < 256
        )
        SELECT COUNT(*) INTO parent_depth
        FROM hierarchy
        WHERE entity_id = NEW.entity_id;
        
        IF parent_depth > 0 THEN
            RAISE EXCEPTION 'Circular reference detected in entity hierarchy';
        END IF;
    END IF;
    
    -- 检查层级深度
    WITH RECURSIVE depth_calc AS (
        SELECT entity_id, parent_id, 1 as depth
        FROM entities
        WHERE entity_id = COALESCE(NEW.parent_id, NEW.entity_id)
        UNION ALL
        SELECT e.entity_id, e.parent_id, d.depth + 1
        FROM entities e
        JOIN depth_calc d ON e.parent_id = d.entity_id
        WHERE d.depth < 256
    )
    SELECT MAX(depth) INTO current_depth FROM depth_calc;
    
    IF current_depth > 256 THEN
        RAISE EXCEPTION 'Entity hierarchy depth exceeds maximum of 256';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_entity_hierarchy_trigger
    BEFORE INSERT OR UPDATE OF parent_id ON entities
    FOR EACH ROW EXECUTE FUNCTION validate_entity_hierarchy();

-- =====================================================
-- 5. 转换函数
-- =====================================================

-- glTF场景导入函数
CREATE OR REPLACE FUNCTION import_gltf_scene(
    p_world_id UUID,
    p_space_name VARCHAR,
    p_gltf_data JSONB
)
RETURNS UUID AS $$
DECLARE
    v_space_id UUID;
    v_node JSONB;
    v_entity_id UUID;
    v_node_map JSONB := '{}';
BEGIN
    -- 创建新空间
    INSERT INTO spaces (world_id, name, space_type, bounds, scene_graph)
    VALUES (
        p_world_id,
        p_space_name,
        'SPATIAL',
        p_gltf_data->'scene'->'bounds',
        p_gltf_data->'scene'
    )
    RETURNING space_id INTO v_space_id;
    
    -- 导入节点作为实体
    FOR v_node IN SELECT * FROM jsonb_array_elements(p_gltf_data->'nodes')
    LOOP
        INSERT INTO entities (
            space_id,
            entity_type,
            name,
            transform,
            metadata
        ) VALUES (
            v_space_id,
            CASE 
                WHEN v_node->>'mesh' IS NOT NULL THEN 'OBJECT'
                WHEN v_node->>'camera' IS NOT NULL THEN 'CAMERA'
                ELSE 'OBJECT'
            END::entity_type,
            v_node->>'name',
            jsonb_build_object(
                'position', COALESCE(v_node->'translation', '[0,0,0]'::jsonb),
                'rotation', COALESCE(v_node->'rotation', '[0,0,0,1]'::jsonb),
                'scale', COALESCE(v_node->'scale', '[1,1,1]'::jsonb)
            ),
            jsonb_build_object(
                'gltf_node_index', v_node->>'index',
                'gltf_extras', v_node->'extras'
            )
        )
        RETURNING entity_id INTO v_entity_id;
        
        -- 存储节点ID映射
        v_node_map := v_node_map || jsonb_build_object(v_node->>'index', v_entity_id::text);
    END LOOP;
    
    -- 更新父子关系
    FOR i IN 0..jsonb_array_length(p_gltf_data->'nodes') - 1 LOOP
        v_node := p_gltf_data->'nodes'->i;
        IF v_node->'children' IS NOT NULL THEN
            UPDATE entities
            SET parent_id = (v_node_map->>(v_node->>'index'))::UUID
            WHERE metadata->>'gltf_node_index' IN (
                SELECT jsonb_array_elements_text(v_node->'children')
            )
            AND space_id = v_space_id;
        END IF;
    END LOOP;
    
    RETURN v_space_id;
END;
$$ LANGUAGE plpgsql;

-- VRM化身导入函数
CREATE OR REPLACE FUNCTION import_vrm_avatar(
    p_user_id UUID,
    p_vrm_data JSONB,
    p_asset_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_avatar_id UUID;
    v_humanoid_bones JSONB;
    v_expressions JSONB;
    v_spring_bones JSONB;
BEGIN
    -- 提取人形骨骼
    v_humanoid_bones := p_vrm_data->'extensions'->'VRM'->'humanoid'->'humanBones';
    
    -- 提取表情
    v_expressions := p_vrm_data->'extensions'->'VRM'->'blendShapeMaster'->'blendShapeGroups';
    IF v_expressions IS NULL THEN
        v_expressions := p_vrm_data->'extensions'->'VRMC_vrm'->'expressions';
    END IF;
    
    -- 提取弹簧骨骼
    v_spring_bones := p_vrm_data->'extensions'->'VRM'->'secondaryAnimation';
    IF v_spring_bones IS NULL THEN
        v_spring_bones := p_vrm_data->'extensions'->'VRMC_springBone';
    END IF;
    
    -- 创建化身记录
    INSERT INTO avatars (
        user_id,
        asset_id,
        name,
        skeleton_data,
        expression_set,
        spring_bone_config,
        appearance,
        metadata
    ) VALUES (
        p_user_id,
        p_asset_id,
        COALESCE(
            p_vrm_data->'extensions'->'VRM'->'meta'->>'title',
            p_vrm_data->'extensions'->'VRMC_vrm'->'meta'->>'name',
            'Unnamed Avatar'
        ),
        jsonb_build_object(
            'humanoid', v_humanoid_bones,
            'bone_structure', p_vrm_data->'skins'
        ),
        v_expressions,
        v_spring_bones,
        jsonb_build_object(
            'materials', p_vrm_data->'materials',
            'first_person', COALESCE(
                p_vrm_data->'extensions'->'VRM'->'firstPerson',
                p_vrm_data->'extensions'->'VRMC_vrm'->'firstPerson'
            )
        ),
        jsonb_build_object(
            'vrm_version', COALESCE(
                p_vrm_data->'extensions'->'VRM'->>'exporterVersion',
                '1.0'
            ),
            'meta', COALESCE(
                p_vrm_data->'extensions'->'VRM'->'meta',
                p_vrm_data->'extensions'->'VRMC_vrm'->'meta'
            )
        )
    )
    RETURNING avatar_id INTO v_avatar_id;
    
    RETURN v_avatar_id;
END;
$$ LANGUAGE plpgsql;

-- 空间实体序列化为glTF
CREATE OR REPLACE FUNCTION export_space_to_gltf(p_space_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_gltf JSONB;
    v_nodes JSONB := '[]'::jsonb;
    v_meshes JSONB := '[]'::jsonb;
    v_materials JSONB := '[]'::jsonb;
    v_entity RECORD;
    v_node JSONB;
BEGIN
    -- 获取空间信息
    SELECT jsonb_build_object(
        'asset', jsonb_build_object('version', '2.0', 'generator', 'Metaverse Schema Exporter'),
        'scene', 0,
        'scenes', jsonb_build_array(jsonb_build_object('nodes', (
            SELECT jsonb_agg(entity_id::text::int)
            FROM entities
            WHERE space_id = p_space_id AND parent_id IS NULL
        )))
    ) INTO v_gltf;
    
    -- 序列化实体为节点
    FOR v_entity IN 
        SELECT e.*, c.properties as render_props
        FROM entities e
        LEFT JOIN components c ON e.entity_id = c.entity_id AND c.component_type = 'RENDER'
        WHERE e.space_id = p_space_id
    LOOP
        v_node := jsonb_build_object(
            'name', v_entity.name,
            'translation', v_entity.transform->'position',
            'rotation', v_entity.transform->'rotation',
            'scale', v_entity.transform->'scale'
        );
        
        -- 添加子节点引用
        IF EXISTS (SELECT 1 FROM entities WHERE parent_id = v_entity.entity_id) THEN
            v_node := v_node || jsonb_build_object(
                'children', (
                    SELECT jsonb_agg(row_number() OVER () - 1)
                    FROM entities
                    WHERE parent_id = v_entity.entity_id
                )
            );
        END IF;
        
        -- 添加网格引用
        IF v_entity.render_props IS NOT NULL THEN
            v_node := v_node || jsonb_build_object(
                'mesh', jsonb_array_length(v_meshes)
            );
            v_meshes := v_meshes || jsonb_build_array(
                jsonb_build_object('primitives', v_entity.render_props->'primitives')
            );
        END IF;
        
        v_nodes := v_nodes || jsonb_build_array(v_node);
    END LOOP;
    
    v_gltf := v_gltf || jsonb_build_object('nodes', v_nodes);
    
    IF jsonb_array_length(v_meshes) > 0 THEN
        v_gltf := v_gltf || jsonb_build_object('meshes', v_meshes);
    END IF;
    
    RETURN v_gltf;
END;
$$ LANGUAGE plpgsql;

-- 批量更新实体变换
CREATE OR REPLACE FUNCTION batch_update_transforms(
    p_updates JSONB
)
RETURNS INTEGER AS $$
DECLARE
    v_update JSONB;
    v_count INTEGER := 0;
BEGIN
    FOR v_update IN SELECT * FROM jsonb_array_elements(p_updates)
    LOOP
        UPDATE entities
        SET 
            transform = v_update->'transform',
            updated_at = NOW()
        WHERE entity_id = (v_update->>'entity_id')::UUID;
        
        v_count := v_count + 1;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 空间包围盒计算
CREATE OR REPLACE FUNCTION calculate_space_bounds(p_space_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_bounds JSONB;
BEGIN
    SELECT jsonb_build_object(
        'min', jsonb_build_array(
            MIN((transform->'position'->>0)::float),
            MIN((transform->'position'->>1)::float),
            MIN((transform->'position'->>2)::float)
        ),
        'max', jsonb_build_array(
            MAX((transform->'position'->>0)::float),
            MAX((transform->'position'->>1)::float),
            MAX((transform->'position'->>2)::float)
        )
    )
    INTO v_bounds
    FROM entities
    WHERE space_id = p_space_id;
    
    -- 更新空间记录
    UPDATE spaces
    SET bounds = v_bounds,
        updated_at = NOW()
    WHERE space_id = p_space_id;
    
    RETURN v_bounds;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. 查询视图
-- =====================================================

-- 实体完整信息视图
CREATE OR REPLACE VIEW entity_full_info AS
SELECT 
    e.entity_id,
    e.space_id,
    e.entity_type,
    e.name,
    e.transform,
    e.parent_id,
    e.tags,
    e.metadata,
    jsonb_agg(
        jsonb_build_object(
            'component_id', c.component_id,
            'component_type', c.component_type,
            'properties', c.properties,
            'enabled', c.enabled
        ) ORDER BY c.component_type
    ) FILTER (WHERE c.component_id IS NOT NULL) as components,
    s.name as space_name,
    w.name as world_name
FROM entities e
LEFT JOIN components c ON e.entity_id = c.entity_id
LEFT JOIN spaces s ON e.space_id = s.space_id
LEFT JOIN worlds w ON s.world_id = w.world_id
GROUP BY e.entity_id, s.name, w.name;

-- 世界完整层次视图
CREATE OR REPLACE VIEW world_hierarchy AS
WITH RECURSIVE entity_tree AS (
    SELECT 
        e.entity_id,
        e.space_id,
        e.parent_id,
        e.name,
        e.entity_type,
        e.transform,
        0 as depth,
        e.entity_id::text as path
    FROM entities e
    WHERE e.parent_id IS NULL
    
    UNION ALL
    
    SELECT 
        e.entity_id,
        e.space_id,
        e.parent_id,
        e.name,
        e.entity_type,
        e.transform,
        et.depth + 1,
        et.path || '.' || e.entity_id::text
    FROM entities e
    JOIN entity_tree et ON e.parent_id = et.entity_id
)
SELECT 
    w.world_id,
    w.name as world_name,
    s.space_id,
    s.name as space_name,
    et.entity_id,
    et.name as entity_name,
    et.entity_type,
    et.transform,
    et.depth,
    et.path
FROM worlds w
JOIN spaces s ON w.world_id = s.world_id
LEFT JOIN entity_tree et ON s.space_id = et.space_id
ORDER BY w.name, s.name, et.path;

-- 化身资产视图
CREATE OR REPLACE VIEW avatar_assets AS
SELECT 
    a.avatar_id,
    a.name as avatar_name,
    a.skeleton_data,
    a.expression_set,
    a.spring_bone_config,
    a.appearance,
    a.is_public,
    u.user_id,
    u.username as owner_name,
    u.wallet_address,
    ast.asset_id,
    ast.content_uri,
    ast.metadata as asset_metadata
FROM avatars a
JOIN users u ON a.user_id = u.user_id
LEFT JOIN assets ast ON a.asset_id = ast.asset_id;

-- =====================================================
-- 7. 存储过程和辅助函数
-- =====================================================

-- 克隆实体及其组件
CREATE OR REPLACE FUNCTION clone_entity(
    p_source_entity_id UUID,
    p_target_space_id UUID DEFAULT NULL,
    p_new_parent_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_new_entity_id UUID;
    v_component RECORD;
    v_target_space_id UUID;
BEGIN
    -- 确定目标空间
    IF p_target_space_id IS NULL THEN
        SELECT space_id INTO v_target_space_id
        FROM entities
        WHERE entity_id = p_source_entity_id;
    ELSE
        v_target_space_id := p_target_space_id;
    END IF;
    
    -- 克隆实体
    INSERT INTO entities (
        space_id, entity_type, name, parent_id, 
        transform, visibility, tags, metadata
    )
    SELECT 
        v_target_space_id,
        entity_type,
        name || '_clone',
        COALESCE(p_new_parent_id, parent_id),
        transform,
        visibility,
        tags,
        metadata || jsonb_build_object('cloned_from', p_source_entity_id)
    FROM entities
    WHERE entity_id = p_source_entity_id
    RETURNING entity_id INTO v_new_entity_id;
    
    -- 克隆组件
    FOR v_component IN 
        SELECT * FROM components WHERE entity_id = p_source_entity_id
    LOOP
        INSERT INTO components (
            entity_id, component_type, properties, enabled
        ) VALUES (
            v_new_entity_id,
            v_component.component_type,
            v_component.properties,
            v_component.enabled
        );
    END LOOP;
    
    RETURN v_new_entity_id;
END;
$$ LANGUAGE plpgsql;

-- 空间清理（删除孤立实体）
CREATE OR REPLACE FUNCTION cleanup_space(p_space_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_deleted INTEGER;
BEGIN
    -- 删除没有有效父实体的子实体（根级除外）
    DELETE FROM entities
    WHERE space_id = p_space_id
    AND parent_id IS NOT NULL
    AND parent_id NOT IN (SELECT entity_id FROM entities);
    
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    
    RETURN v_deleted;
END;
$$ LANGUAGE plpgsql;

-- 资产依赖检查
CREATE OR REPLACE FUNCTION check_asset_dependencies(p_asset_id UUID)
RETURNS TABLE (
    dependent_type VARCHAR,
    dependent_id UUID,
    dependent_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'entity'::VARCHAR,
        e.entity_id,
        e.name
    FROM entities e
    WHERE e.metadata->>'asset_reference' = p_asset_id::text
    
    UNION ALL
    
    SELECT 
        'avatar'::VARCHAR,
        a.avatar_id,
        a.name
    FROM avatars a
    WHERE a.asset_id = p_asset_id
    
    UNION ALL
    
    SELECT 
        'world'::VARCHAR,
        w.world_id,
        w.name
    FROM worlds w
    WHERE w.configuration->>'thumbnail_asset' = p_asset_id::text;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. 权限和安全
-- =====================================================

-- 行级安全策略启用
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE worlds ENABLE ROW LEVEL SECURITY;
ALTER TABLE spaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE avatars ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

-- 用户表策略
CREATE POLICY users_self_access ON users
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- 世界表策略
CREATE POLICY worlds_owner_access ON worlds
    FOR ALL
    USING (owner_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY worlds_public_read ON worlds
    FOR SELECT
    USING (is_public = true);

-- 化身表策略
CREATE POLICY avatars_owner_access ON avatars
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY avatars_public_read ON avatars
    FOR SELECT
    USING (is_public = true);

-- 资产表策略
CREATE POLICY assets_owner_access ON assets
    FOR ALL
    USING (owner_id = current_setting('app.current_user_id')::UUID);

-- 注释说明
COMMENT ON TABLE users IS '用户账户信息表';
COMMENT ON TABLE worlds IS '虚拟世界定义表';
COMMENT ON TABLE spaces IS '世界内空间/场景表';
COMMENT ON TABLE entities IS '场景中的实体对象表';
COMMENT ON TABLE components IS '实体组件表';
COMMENT ON TABLE assets IS '3D资产和资源表';
COMMENT ON TABLE avatars IS '用户虚拟化身表';
COMMENT ON TABLE interactions IS '实体交互定义表';
COMMENT ON TABLE portals IS '空间间传送门表';
```

## 4. 性能优化策略 (Performance Optimization)

### 4.1 数据库优化 (Database Optimization)

```yaml
database_optimization:
  indexing:
    spatial_index:
      type: "GiST/GIN"
      use_case: "空间查询"
      implementation: "PostGIS扩展"
    
    jsonb_index:
      type: "GIN"
      use_case: "JSONB字段查询"
      example: "CREATE INDEX idx_entities_transform ON entities USING GIN(transform)"
    
    fulltext_index:
      type: "GIN + trigram"
      use_case: "名称搜索"
      example: "CREATE INDEX idx_entities_name ON entities USING gin(name gin_trgm_ops)"
  
  partitioning:
    entity_partitioning:
      strategy: "按space_id哈希分区"
      benefit: "并行查询，单空间数据局部性"
    
    time_partitioning:
      table: "events, logs"
      strategy: "按月范围分区"
  
  caching:
    materialized_views:
      - "entity_full_info"
      - "world_hierarchy"
      - "popular_assets"
    
    redis_cache:
      keys:
        - "space:{id}:entities"
        - "world:{id}:spaces"
        - "user:{id}:avatars"
      ttl: "5分钟"
```

### 4.2 流式加载策略 (Streaming Strategy)

```yaml
streaming_strategy:
  lod_streaming:
    levels:
      - distance: 0-50m
        quality: "full"
        polygon_budget: "100%"
      - distance: 50-150m
        quality: "medium"
        polygon_budget: "50%"
      - distance: 150-500m
        quality: "low"
        polygon_budget: "10%"
      - distance: ">500m"
        quality: "impostor"
        polygon_budget: "1%"
    
    transition:
      hysteresis: "10%距离"
      fade_duration: "0.5s"
  
  spatial_partitioning:
    octree:
      max_depth: 8
      max_objects: 16
      cell_size: "自适应"
    
    grid_loading:
      cell_size: "100m"
      preload_radius: 2
      unload_radius: 3
```

## 5. 数据迁移策略 (Data Migration)

### 5.1 版本兼容性 (Version Compatibility)

```yaml
version_compatibility:
  schema_versions:
    current: "1.0.0"
    supported: ["0.9.x", "1.0.x"]
    
  migration_strategy:
    backward_compatible:
      - "新增字段提供默认值"
      - "保留废弃字段"
      - "API版本协商"
    
    upgrade_path:
      "0.9.0" → "1.0.0":
        - "VRM 0.x to 1.0转换"
        - "材质系统升级"
        - "骨骼系统规范化"
```

### 5.2 数据转换管道 (Data Conversion Pipeline)

```yaml
conversion_pipeline:
  import_pipeline:
    steps:
      1_validate:
        action: "验证源格式"
        tools: ["glTF Validator", "VRM Validator"]
      
      2_parse:
        action: "解析源数据"
        output: "中间表示(IR)"
      
      3_transform:
        action: "应用转换规则"
        rules: "格式特定映射"
      
      4_optimize:
        action: "运行时优化"
        tasks:
          - "LOD生成"
          - "纹理压缩"
          - "网格简化"
      
      5_validate:
        action: "验证输出"
        checks:
          - "Schema一致性"
          - "数据完整性"
          - "性能预算"
      
      6_store:
        action: "存储到数据库"
        target: "PostgreSQL"
  
  export_pipeline:
    steps:
      1_query:
        action: "查询数据库"
      
      2_assemble:
        action: "组装目标格式"
      
      3_optimize:
        action: "目标格式优化"
      
      4_package:
        action: "打包输出"
```

---

**相关文档：**
- [01_Overview.md](./01_Overview.md) - 概述
- [02_Formal_Definition.md](./02_Formal_Definition.md) - 形式化定义
- [03_Standards.md](./03_Standards.md) - 标准对标
- [05_Case_Studies.md](./05_Case_Studies.md) - 应用案例
