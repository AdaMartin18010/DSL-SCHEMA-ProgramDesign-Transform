# GraphQL Schema实践案例

## 📑 目录

- [GraphQL Schema实践案例](#graphql-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：电商平台GraphQL API](#2-案例1电商平台graphql-api)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：社交媒体GraphQL API](#3-案例2社交媒体graphql-api)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：微服务GraphQL网关](#4-案例3微服务graphql网关)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
    - [4.3 实现代码](#43-实现代码)
  - [5. 案例4：GraphQL到OpenAPI转换](#5-案例4graphql到openapi转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：GraphQL数据存储与分析系统](#6-案例5graphql数据存储与分析系统)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供GraphQL Schema在实际应用中的实践案例，涵盖电商平台、社交媒体、微服务网关等场景。

---

## 2. 案例1：电商平台GraphQL API

### 2.1 场景描述

**应用场景**：
电商平台使用GraphQL API提供商品查询、订单管理、用户管理等功能。

**需求**：
- 商品查询（支持分页、筛选、排序）
- 订单查询和管理
- 用户信息查询
- 购物车管理

### 2.2 Schema定义

**电商平台GraphQL Schema**：

```graphql
type Query {
  # 商品查询
  products(
    filter: ProductFilter
    sort: ProductSort
    pagination: Pagination
  ): ProductConnection!

  product(id: ID!): Product

  # 订单查询
  orders(
    filter: OrderFilter
    pagination: Pagination
  ): OrderConnection!

  order(id: ID!): Order

  # 用户查询
  me: User
  user(id: ID!): User
}

type Mutation {
  # 订单操作
  createOrder(input: CreateOrderInput!): Order!
  updateOrder(id: ID!, input: UpdateOrderInput!): Order!
  cancelOrder(id: ID!): Boolean!

  # 购物车操作
  addToCart(productId: ID!, quantity: Int!): CartItem!
  removeFromCart(cartItemId: ID!): Boolean!
  updateCartItem(cartItemId: ID!, quantity: Int!): CartItem!
}

type Subscription {
  orderStatusChanged(orderId: ID!): Order!
  productStockChanged(productId: ID!): Product!
}

# 类型定义
type Product {
  id: ID!
  name: String!
  description: String
  price: Decimal!
  stock: Int!
  category: Category!
  images: [Image!]!
  reviews: [Review!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Order {
  id: ID!
  orderNumber: String!
  user: User!
  items: [OrderItem!]!
  totalAmount: Decimal!
  status: OrderStatus!
  shippingAddress: Address!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type User {
  id: ID!
  email: String!
  name: String!
  avatar: String
  orders: [Order!]!
  cart: [CartItem!]!
}

enum OrderStatus {
  PENDING
  CONFIRMED
  PROCESSING
  SHIPPED
  DELIVERED
  CANCELLED
}

input ProductFilter {
  categoryId: ID
  minPrice: Decimal
  maxPrice: Decimal
  inStock: Boolean
  search: String
}

input CreateOrderInput {
  items: [OrderItemInput!]!
  shippingAddress: AddressInput!
}

input OrderItemInput {
  productId: ID!
  quantity: Int!
}
```

### 2.3 实现代码

**GraphQL Schema实现**：

```python
from graphql import GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString, GraphQLID
from graphql.type.definition import GraphQLNonNull, GraphQLList
import graphene

class Product(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=True)
    category = graphene.Field('Category', required=True)
    images = graphene.List('Image', required=True)
    reviews = graphene.List('Review')
    created_at = graphene.DateTime(required=True)
    updated_at = graphene.DateTime(required=True)

class Order(graphene.ObjectType):
    id = graphene.ID(required=True)
    order_number = graphene.String(required=True)
    user = graphene.Field('User', required=True)
    items = graphene.List('OrderItem', required=True)
    total_amount = graphene.Decimal(required=True)
    status = graphene.Field('OrderStatus', required=True)
    shipping_address = graphene.Field('Address', required=True)
    created_at = graphene.DateTime(required=True)
    updated_at = graphene.DateTime(required=True)

class Query(graphene.ObjectType):
    products = graphene.Field(
        'ProductConnection',
        filter=graphene.Argument('ProductFilter'),
        sort=graphene.Argument('ProductSort'),
        pagination=graphene.Argument('Pagination')
    )

    product = graphene.Field(Product, id=graphene.ID(required=True))

    orders = graphene.Field(
        'OrderConnection',
        filter=graphene.Argument('OrderFilter'),
        pagination=graphene.Argument('Pagination')
    )

    order = graphene.Field(Order, id=graphene.ID(required=True))

    me = graphene.Field('User')
    user = graphene.Field('User', id=graphene.ID(required=True))

    def resolve_products(self, info, filter=None, sort=None, pagination=None):
        # 实现商品查询逻辑
        pass

    def resolve_product(self, info, id):
        # 实现单个商品查询逻辑
        pass

class Mutation(graphene.ObjectType):
    create_order = graphene.Field(
        Order,
        input=graphene.Argument('CreateOrderInput', required=True)
    )

    update_order = graphene.Field(
        Order,
        id=graphene.ID(required=True),
        input=graphene.Argument('UpdateOrderInput', required=True)
    )

    cancel_order = graphene.Field(
        graphene.Boolean,
        id=graphene.ID(required=True)
    )

    def resolve_create_order(self, info, input):
        # 实现创建订单逻辑
        pass

schema = graphene.Schema(query=Query, mutation=Mutation)
```

---

## 3. 案例2：社交媒体GraphQL API

### 3.1 场景描述

**应用场景**：
社交媒体平台使用GraphQL API提供用户动态、评论、点赞、关注等功能。

**需求**：
- 用户动态查询（时间线）
- 评论和回复
- 点赞和收藏
- 用户关注关系

### 3.2 Schema定义

**社交媒体GraphQL Schema**：

```graphql
type Query {
  # 动态查询
  feed(pagination: Pagination): PostConnection!
  post(id: ID!): Post
  userPosts(userId: ID!, pagination: Pagination): PostConnection!

  # 用户查询
  me: User
  user(id: ID!): User
  users(search: String!, pagination: Pagination): UserConnection!

  # 评论查询
  comments(postId: ID!, pagination: Pagination): CommentConnection!
}

type Mutation {
  # 动态操作
  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: UpdatePostInput!): Post!
  deletePost(id: ID!): Boolean!

  # 评论操作
  createComment(postId: ID!, input: CreateCommentInput!): Comment!
  updateComment(id: ID!, input: UpdateCommentInput!): Comment!
  deleteComment(id: ID!): Boolean!

  # 互动操作
  likePost(postId: ID!): Like!
  unlikePost(postId: ID!): Boolean!
  followUser(userId: ID!): Follow!
  unfollowUser(userId: ID!): Boolean!
}

type Subscription {
  newPost(userId: ID!): Post!
  newComment(postId: ID!): Comment!
  postLiked(postId: ID!): Like!
}

type Post {
  id: ID!
  author: User!
  content: String!
  images: [Image!]!
  likes: LikeConnection!
  comments: CommentConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Comment {
  id: ID!
  post: Post!
  author: User!
  content: String!
  replies: [Comment!]!
  likes: Int!
  createdAt: DateTime!
}
```

### 3.3 实现代码

**社交媒体GraphQL Schema实现**：

```python
import graphene
from datetime import datetime

class Post(graphene.ObjectType):
    id = graphene.ID(required=True)
    author = graphene.Field('User', required=True)
    content = graphene.String(required=True)
    images = graphene.List('Image')
    likes = graphene.Field('LikeConnection', required=True)
    comments = graphene.Field('CommentConnection', required=True)
    created_at = graphene.DateTime(required=True)
    updated_at = graphene.DateTime(required=True)

class Comment(graphene.ObjectType):
    id = graphene.ID(required=True)
    post = graphene.Field(Post, required=True)
    author = graphene.Field('User', required=True)
    content = graphene.String(required=True)
    replies = graphene.List(lambda: Comment)
    likes = graphene.Int(required=True)
    created_at = graphene.DateTime(required=True)

class Query(graphene.ObjectType):
    feed = graphene.Field(
        'PostConnection',
        pagination=graphene.Argument('Pagination')
    )

    post = graphene.Field(Post, id=graphene.ID(required=True))

    user_posts = graphene.Field(
        'PostConnection',
        user_id=graphene.ID(required=True),
        pagination=graphene.Argument('Pagination')
    )

    def resolve_feed(self, info, pagination=None):
        # 实现动态时间线查询逻辑
        pass

class Mutation(graphene.ObjectType):
    create_post = graphene.Field(
        Post,
        input=graphene.Argument('CreatePostInput', required=True)
    )

    like_post = graphene.Field(
        'Like',
        post_id=graphene.ID(required=True)
    )

    def resolve_create_post(self, info, input):
        # 实现创建动态逻辑
        pass

schema = graphene.Schema(query=Query, mutation=Mutation)
```

---

## 4. 案例3：微服务GraphQL网关

### 4.1 场景描述

**应用场景**：
使用GraphQL作为API网关，聚合多个微服务的RESTful API。

**需求**：
- 统一API入口
- 聚合多个后端服务
- 减少客户端请求次数
- 类型安全的API调用

### 4.2 Schema定义

**微服务GraphQL网关Schema**：

```graphql
type Query {
  # 聚合用户和订单服务
  userWithOrders(userId: ID!): UserWithOrders!

  # 聚合商品和库存服务
  productWithInventory(productId: ID!): ProductWithInventory!
}

type UserWithOrders {
  user: User!
  orders: [Order!]!
  totalOrders: Int!
  totalSpent: Decimal!
}

type ProductWithInventory {
  product: Product!
  inventory: Inventory!
  available: Boolean!
}
```

### 4.3 实现代码

**微服务GraphQL网关实现**：

```python
import graphene
import requests
from typing import Dict, List

class UserService:
    """用户服务客户端"""
    BASE_URL = "http://user-service:8001"

    def get_user(self, user_id: str) -> Dict:
        response = requests.get(f"{self.BASE_URL}/users/{user_id}")
        return response.json()

class OrderService:
    """订单服务客户端"""
    BASE_URL = "http://order-service:8002"

    def get_orders_by_user(self, user_id: str) -> List[Dict]:
        response = requests.get(f"{self.BASE_URL}/orders?userId={user_id}")
        return response.json()

class User(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    email = graphene.String(required=True)

class Order(graphene.ObjectType):
    id = graphene.ID(required=True)
    order_number = graphene.String(required=True)
    total_amount = graphene.Decimal(required=True)

class UserWithOrders(graphene.ObjectType):
    user = graphene.Field(User, required=True)
    orders = graphene.List(Order, required=True)
    total_orders = graphene.Int(required=True)
    total_spent = graphene.Decimal(required=True)

class Query(graphene.ObjectType):
    user_with_orders = graphene.Field(
        UserWithOrders,
        user_id=graphene.ID(required=True)
    )

    def resolve_user_with_orders(self, info, user_id):
        user_service = UserService()
        order_service = OrderService()

        # 并行调用多个服务
        user_data = user_service.get_user(user_id)
        orders_data = order_service.get_orders_by_user(user_id)

        return UserWithOrders(
            user=User(**user_data),
            orders=[Order(**order) for order in orders_data],
            total_orders=len(orders_data),
            total_spent=sum(float(order['total_amount']) for order in orders_data)
        )

schema = graphene.Schema(query=Query)
```

---

## 5. 案例4：GraphQL到OpenAPI转换

### 5.1 场景描述

**应用场景**：
将GraphQL API转换为OpenAPI规范，用于API文档生成和工具集成。

**需求**：
- GraphQL Schema转换为OpenAPI规范
- 生成API文档
- 支持OpenAPI工具链

### 5.2 实现代码

**GraphQL到OpenAPI转换实现**：

```python
from graphql import build_schema
from openapi_spec_validator import validate_spec

def convert_graphql_to_openapi(graphql_schema_str: str) -> dict:
    """将GraphQL Schema转换为OpenAPI规范"""
    schema = build_schema(graphql_schema_str)

    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "GraphQL API",
            "version": "1.0.0",
            "description": "Generated from GraphQL Schema"
        },
        "servers": [
            {
                "url": "https://api.example.com/graphql",
                "description": "GraphQL API Server"
            }
        ],
        "paths": {
            "/graphql": {
                "post": {
                    "summary": "GraphQL Query/Mutation",
                    "operationId": "graphqlQuery",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string"},
                                        "variables": {"type": "object"},
                                        "operationName": {"type": "string"}
                                    },
                                    "required": ["query"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "GraphQL response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "data": {"type": "object"},
                                            "errors": {
                                                "type": "array",
                                                "items": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {}
        }
    }

    # 转换类型为OpenAPI Schema
    for type_name, graphql_type in schema.type_map.items():
        if type_name.startswith("__"):
            continue
        openapi_spec["components"]["schemas"][type_name] = \
            convert_graphql_type_to_openapi(graphql_type, schema)

    return openapi_spec

# 使用示例
graphql_schema = """
type Query {
  user(id: ID!): User
}

type User {
  id: ID!
  name: String!
  email: String!
}
"""

openapi_spec = convert_graphql_to_openapi(graphql_schema)
validate_spec(openapi_spec)
```

---

## 6. 案例5：GraphQL数据存储与分析系统

### 6.1 场景描述

**应用场景**：
存储GraphQL Schema定义、查询日志、性能指标等数据，进行API分析和优化。

**需求**：
- Schema版本管理
- 查询日志记录
- 性能指标分析
- 使用模式分析

### 6.2 实现代码

**GraphQL数据存储与分析系统实现**：

```python
from graphql_data_store import GraphQLDataStore
import hashlib
import time

class GraphQLAnalytics:
    """GraphQL分析系统"""

    def __init__(self, db_config: Dict):
        self.store = GraphQLDataStore(db_config)

    def store_schema_version(self, schema_name: str, schema_definition: str, version: str):
        """存储Schema版本"""
        return self.store.store_schema(schema_name, schema_definition, version)

    def log_query_execution(self, schema_id: int, query_string: str,
                           variables: Dict = None, operation_name: str = None):
        """记录查询执行"""
        start_time = time.time()
        error_message = None

        try:
            # 执行查询
            result = execute_query(query_string, variables)
            execution_time_ms = int((time.time() - start_time) * 1000)

            # 记录成功查询
            self.store.log_query(
                schema_id, query_string, variables, operation_name,
                execution_time_ms, None
            )

            # 更新性能指标
            query_hash = self._hash_query(query_string, variables)
            self.store.update_performance_metrics(
                schema_id, query_hash, operation_name,
                execution_time_ms, False
            )

            return result

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_message = str(e)

            # 记录失败查询
            self.store.log_query(
                schema_id, query_string, variables, operation_name,
                execution_time_ms, error_message
            )

            # 更新性能指标
            query_hash = self._hash_query(query_string, variables)
            self.store.update_performance_metrics(
                schema_id, query_hash, operation_name,
                execution_time_ms, True
            )

            raise

    def analyze_schema_usage(self, schema_id: int):
        """分析Schema使用情况"""
        with self.store.conn.cursor() as cur:
            # 查询最常用的类型
            cur.execute("""
                SELECT
                    gt.type_name,
                    COUNT(DISTINCT gq.id) as query_count,
                    AVG(gp.avg_execution_time_ms) as avg_time
                FROM graphql_types gt
                LEFT JOIN graphql_queries gq ON gt.schema_id = gq.schema_id
                LEFT JOIN graphql_performance gp ON gt.schema_id = gp.schema_id
                WHERE gt.schema_id = %s
                GROUP BY gt.id, gt.type_name
                ORDER BY query_count DESC
                LIMIT 10
            """, (schema_id,))

            return cur.fetchall()

    def _hash_query(self, query_string: str, variables: Dict = None) -> str:
        """生成查询哈希"""
        content = query_string
        if variables:
            content += str(sorted(variables.items()))
        return hashlib.sha256(content.encode()).hexdigest()

# 使用示例
analytics = GraphQLAnalytics({
    "host": "localhost",
    "database": "graphql_db",
    "user": "postgres",
    "password": "password"
})

# 存储Schema
schema_id = analytics.store_schema_version(
    "ECommerceAPI",
    graphql_schema_string,
    "1.0.0"
)

# 记录查询
result = analytics.log_query_execution(
    schema_id,
    "query { user(id: \"123\") { name email } }",
    operation_name="GetUser"
)

# 分析使用情况
usage_stats = analytics.analyze_schema_usage(schema_id)
```

---

**文档创建时间**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

**相关文档**：
- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
