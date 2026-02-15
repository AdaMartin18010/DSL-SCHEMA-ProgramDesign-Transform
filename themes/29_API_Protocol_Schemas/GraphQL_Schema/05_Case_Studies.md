# GraphQL Schema实践案例

## 📑 目录

- [GraphQL Schema实践案例](#graphql-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：电商平台统一API网关](#2-案例1电商平台统一api网关)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 完整代码实现](#25-完整代码实现)
    - [2.6 效果评估与ROI](#26-效果评估与roi)

---

## 2. 案例1：电商平台统一API网关

### 2.1 企业背景

**企业概况**：
"优选商城"（化名）是中国领先的全渠道零售平台，拥有APP、小程序、H5、Web多个客户端，日均活跃用户超过800万，SKU数量超过500万。

### 2.2 业务痛点

1. **API版本管理混乱**
   - 多版本API共存，维护困难
   - 客户端适配成本高
   - 接口文档更新不及时

2. **过度获取数据**
   - REST API返回冗余数据
   - 移动端流量浪费严重
   - 页面加载速度慢

3. **多次请求问题**
   - 一个页面需要调用5-10个接口
   - 瀑布式请求影响性能
   - 错误处理复杂

4. **微服务调用复杂**
   - 前端需要了解后端服务架构
   - 服务依赖关系复杂
   - 故障传播风险高

### 2.3 业务目标

1. **统一API入口**
   - 所有客户端通过GraphQL网关访问
   - 单一端点简化调用
   - 统一认证和限流

2. **按需获取数据**
   - 精确获取所需字段
   - 减少数据传输量
   - 提升页面加载速度

3. **简化前端开发**
   - 一次请求获取所有数据
   - 前端自主决定数据结构
   - 减少前后端沟通成本

4. **微服务聚合**
   - 网关层聚合多个服务
   - 前端无需关心服务划分
   - 支持服务独立演进

### 2.4 技术挑战

1. **N+1查询问题**
   - 关联数据查询优化
   - DataLoader批处理
   - 查询复杂度控制

2. **性能优化**
   - 查询缓存策略
   - 字段级缓存
   - 持久化查询

3. **安全防护**
   - 查询复杂度限制
   - 深度限制
   - 成本分析

4. **监控运维**
   - 查询性能监控
   - 错误追踪
   - 调用链分析

### 2.5 完整代码实现

```python
#!/usr/bin/env python3
"""
GraphQL Schema完整实现
优选商城统一API网关
"""

import graphene
from graphene import ObjectType, String, Int, Float, List, Field, Mutation, InputObjectType
from typing import List, Optional
import json
import time
from functools import lru_cache


# ==================== 类型定义 ====================

class ProductType(ObjectType):
    """商品类型"""
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    price = graphene.Float()
    original_price = graphene.Float()
    stock = graphene.Int()
    category = graphene.Field('CategoryType')
    images = graphene.List(String)
    reviews = graphene.List('ReviewType')
    rating = graphene.Float()
    sales_count = graphene.Int()
    
    def resolve_reviews(self, info):
        # 使用DataLoader避免N+1问题
        loader = info.context['review_loader']
        return loader.load(self.id)


class CategoryType(ObjectType):
    """分类类型"""
    id = graphene.ID()
    name = graphene.String()
    parent = graphene.Field('CategoryType')
    children = graphene.List('CategoryType')
    products = graphene.List(ProductType)


class ReviewType(ObjectType):
    """评价类型"""
    id = graphene.ID()
    user_id = graphene.ID()
    user_name = graphene.String()
    rating = graphene.Int()
    content = graphene.String()
    created_at = graphene.String()
    images = graphene.List(String)


class OrderItemType(ObjectType):
    """订单项类型"""
    id = graphene.ID()
    product = graphene.Field(ProductType)
    quantity = graphene.Int()
    price = graphene.Float()
    total = graphene.Float()


class OrderType(ObjectType):
    """订单类型"""
    id = graphene.ID()
    order_no = graphene.String()
    status = graphene.String()
    total_amount = graphene.Float()
    items = graphene.List(OrderItemType)
    shipping_address = graphene.Field('AddressType')
    created_at = graphene.String()
    pay_time = graphene.String()


class AddressType(ObjectType):
    """地址类型"""
    id = graphene.ID()
    name = graphene.String()
    phone = graphene.String()
    province = graphene.String()
    city = graphene.String()
    district = graphene.String()
    detail = graphene.String()


class UserType(ObjectType):
    """用户类型"""
    id = graphene.ID()
    nickname = graphene.String()
    avatar = graphene.String()
    phone = graphene.String()
    level = graphene.Int()
    points = graphene.Int()
    orders = graphene.List(OrderType, page=graphene.Int(), size=graphene.Int())
    cart = graphene.List('CartItemType')
    coupons = graphene.List('CouponType')


class CartItemType(ObjectType):
    """购物车项类型"""
    id = graphene.ID()
    product = graphene.Field(ProductType)
    quantity = graphene.Int()
    selected = graphene.Boolean()


class CouponType(ObjectType):
    """优惠券类型"""
    id = graphene.ID()
    name = graphene.String()
    amount = graphene.Float()
    min_order = graphene.Float()
    valid_start = graphene.String()
    valid_end = graphene.String()
    status = graphene.String()


# ==================== 查询定义 ====================

class Query(ObjectType):
    """查询根类型"""
    
    # 商品查询
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    products = graphene.List(
        ProductType, 
        category_id=graphene.ID(),
        keyword=graphene.String(),
        min_price=graphene.Float(),
        max_price=graphene.Float(),
        sort=graphene.String(),
        page=graphene.Int(default_value=1),
        size=graphene.Int(default_value=20)
    )
    
    # 分类查询
    categories = graphene.List(CategoryType, parent_id=graphene.ID())
    category = graphene.Field(CategoryType, id=graphene.ID(required=True))
    
    # 用户查询
    me = graphene.Field(UserType)
    user = graphene.Field(UserType, id=graphene.ID(required=True))
    
    # 订单查询
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    orders = graphene.List(
        OrderType,
        status=graphene.String(),
        page=graphene.Int(default_value=1),
        size=graphene.Int(default_value=10)
    )
    
    # 解析器实现
    def resolve_product(self, info, id):
        # 实际实现会从数据库或服务获取
        return MockData.get_product(id)
    
    def resolve_products(self, info, **kwargs):
        return MockData.search_products(**kwargs)
    
    def resolve_categories(self, info, parent_id=None):
        return MockData.get_categories(parent_id)
    
    def resolve_me(self, info):
        # 从context获取当前用户
        user_id = info.context.get('user_id')
        return MockData.get_user(user_id) if user_id else None
    
    def resolve_order(self, info, id):
        return MockData.get_order(id)


# ==================== 变更定义 ====================

class CreateOrderInput(InputObjectType):
    """创建订单输入"""
    cart_item_ids = graphene.List(graphene.ID, required=True)
    address_id = graphene.ID(required=True)
    coupon_id = graphene.ID()
    remark = graphene.String()


class CreateOrder(Mutation):
    """创建订单"""
    class Arguments:
        input = CreateOrderInput(required=True)
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        # 实际实现会调用订单服务
        order = MockData.create_order(input)
        return CreateOrder(order=order, success=True, message="订单创建成功")


class AddToCartInput(InputObjectType):
    """添加购物车输入"""
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True, default_value=1)
    sku_id = graphene.ID()


class AddToCart(Mutation):
    """添加购物车"""
    class Arguments:
        input = AddToCartInput(required=True)
    
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        cart_item = MockData.add_to_cart(input)
        return AddToCart(cart_item=cart_item, success=True, message="添加成功")


class Mutation(ObjectType):
    """变更根类型"""
    create_order = CreateOrder.Field()
    add_to_cart = AddToCart.Field()


# ==================== Schema定义 ====================

schema = graphene.Schema(query=Query, mutation=Mutation)


# ==================== 模拟数据 ====================

class MockData:
    """模拟数据"""
    
    @staticmethod
    def get_product(id):
        return ProductType(
            id=id,
            name=f"商品{id}",
            description="这是一个优质商品",
            price=199.99,
            original_price=299.99,
            stock=100,
            rating=4.8,
            sales_count=1234,
            images=["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
        )
    
    @staticmethod
    def search_products(**kwargs):
        return [MockData.get_product(f"P{i}") for i in range(1, 11)]
    
    @staticmethod
    def get_categories(parent_id=None):
        return [
            CategoryType(id="C1", name="数码家电"),
            CategoryType(id="C2", name="服饰鞋包"),
            CategoryType(id="C3", name="食品生鲜")
        ]
    
    @staticmethod
    def get_user(id):
        return UserType(
            id=id,
            nickname="用户" + str(id),
            level=3,
            points=1250
        )
    
    @staticmethod
    def get_order(id):
        return OrderType(
            id=id,
            order_no=f"ORD{id}",
            status="PAID",
            total_amount=599.99,
            created_at="2025-01-15T10:30:00Z"
        )
    
    @staticmethod
    def create_order(input):
        return OrderType(
            id="NEW001",
            order_no="ORD202501150001",
            status="PENDING_PAY",
            total_amount=399.99
        )
    
    @staticmethod
    def add_to_cart(input):
        return CartItemType(
            id="CI001",
            quantity=input.quantity,
            selected=True
        )


# ==================== 查询示例 ====================

QUERY_PRODUCT_DETAIL = '''
query GetProductDetail($id: ID!) {
    product(id: $id) {
        id
        name
        price
        originalPrice
        stock
        rating
        images
        reviews {
            id
            userName
            rating
            content
        }
        category {
            id
            name
        }
    }
}
'''

QUERY_USER_ORDERS = '''
query GetUserOrders {
    me {
        id
        nickname
        level
        orders(page: 1, size: 5) {
            id
            orderNo
            status
            totalAmount
            items {
                product {
                    name
                    image
                }
                quantity
                price
            }
        }
    }
}
'''

MUTATION_CREATE_ORDER = '''
mutation CreateNewOrder($input: CreateOrderInput!) {
    createOrder(input: $input) {
        order {
            id
            orderNo
            status
            totalAmount
        }
        success
        message
    }
}
'''


# 使用示例
def main():
    print("=" * 60)
    print("【优选商城GraphQL API】")
    print("=" * 60)
    
    # 查询商品详情
    result = schema.execute(QUERY_PRODUCT_DETAIL, variables={"id": "P123"})
    print("\n📦 商品详情查询:")
    print(json.dumps(result.data, indent=2, ensure_ascii=False))
    
    # 查询用户订单
    result = schema.execute(QUERY_USER_ORDERS, context={"user_id": "U001"})
    print("\n👤 用户订单查询:")
    print(json.dumps(result.data, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
```

### 2.6 效果评估与ROI

| 指标 | REST API | GraphQL | 提升幅度 |
|------|----------|---------|----------|
| 平均请求数/页面 | 8.5次 | 1.2次 | 86%减少 |
| 数据传输量 | 100% | 45% | 55%减少 |
| 页面加载时间 | 2.8s | 1.2s | 57%减少 |
| API版本数 | 12个 | 1个 | 92%减少 |
| 开发效率 | 基准 | +40% | 显著提升 |

**ROI计算**：

```
项目投资：320万元
年度收益：1,280万元
  - 带宽成本节省：420万元
  - 开发效率提升：480万元
  - 用户体验提升带来的GMV增长：380万元

第一年ROI = (1,280 - 320) / 320 = 300%
```

---

**创建时间**：2025-01-21
**最后更新**：2025-02-15
