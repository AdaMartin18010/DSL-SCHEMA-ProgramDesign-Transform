# 全渠道零售Schema案例研究

## 案例概述

**项目名称**: 全渠道零售平台数据标准化  
**行业**: 零售电商  
**涉及标准**: GS1 GDSN, ARTS, JSON Schema, GraphQL  
**目标**: 统一线上线下商品数据，实现全渠道库存和价格同步

---

## 背景介绍

### 业务背景

某大型零售集团拥有：
- 500+线下门店
- 3个电商平台（自营+第三方）
- 100万+SKU商品
- 每日订单量10万+

现有问题：
- 线上线下商品信息不一致
- 库存数据孤岛，超卖/缺货频繁
- 价格体系混乱，渠道冲突
- 供应商数据格式不统一

### 改造目标

1. 建立统一的商品主数据模型
2. 实现实时库存同步
3. 统一价格管理体系
4. 供应商数据标准化接入

---

## Schema设计

### 商品主数据模型

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://retailcorp.com/schemas/product/v2",
  "title": "Omni-Channel Product Master",
  "type": "object",
  "required": ["gtin", "name", "category", "channels"],
  "properties": {
    "gtin": {
      "type": "string",
      "pattern": "^[0-9]{8,14}$",
      "description": "GS1全球贸易项目代码"
    },
    "name": {
      "type": "object",
      "properties": {
        "default": {"type": "string", "maxLength": 200},
        "localized": {
          "type": "object",
          "additionalProperties": {"type": "string"}
        }
      }
    },
    "category": {
      "type": "object",
      "properties": {
        "hierarchy": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "level": {"type": "integer"},
              "code": {"type": "string"},
              "name": {"type": "string"}
            }
          }
        },
        "gpc": {
          "type": "object",
          "description": "GS1全球产品分类",
          "properties": {
            "brickCode": {"type": "string"},
            "brickName": {"type": "string"},
            "classCode": {"type": "string"}
          }
        }
      }
    },
    "attributes": {
      "type": "object",
      "properties": {
        "physical": {
          "type": "object",
          "properties": {
            "weight": {"type": "number", "minimum": 0},
            "weightUnit": {"type": "string", "enum": ["g", "kg", "lb", "oz"]},
            "dimensions": {
              "type": "object",
              "properties": {
                "length": {"type": "number"},
                "width": {"type": "number"},
                "height": {"type": "number"},
                "unit": {"type": "string", "enum": ["cm", "m", "in"]}
              }
            }
          }
        },
        "logistics": {
          "type": "object",
          "properties": {
            "hazardous": {"type": "boolean"},
            "temperatureRequirement": {
              "type": "object",
              "properties": {
                "min": {"type": "number"},
                "max": {"type": "number"},
                "unit": {"type": "string", "enum": ["C", "F"]}
              }
            }
          }
        }
      }
    },
    "media": {
      "type": "object",
      "properties": {
        "images": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "url": {"type": "string", "format": "uri"},
              "type": {"type": "string", "enum": ["main", "detail", "lifestyle", "swatch"]},
              "order": {"type": "integer"}
            }
          }
        },
        "videos": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "url": {"type": "string", "format": "uri"},
              "type": {"type": "string", "enum": ["demo", "review", "360"]}
            }
          }
        }
      }
    },
    "channels": {
      "type": "object",
      "properties": {
        "offline": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "storeSpecificAttributes": {
              "type": "object",
              "additionalProperties": true
            }
          }
        },
        "online": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "platforms": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "platformId": {"type": "string"},
                  "externalId": {"type": "string"},
                  "listingStatus": {"type": "string", "enum": ["active", "inactive", "pending"]}
                }
              }
            }
          }
        }
      }
    },
    "pricing": {
      "type": "object",
      "properties": {
        "basePrice": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "enum": ["CNY", "USD", "EUR"]},
        "channelPrices": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "channelId": {"type": "string"},
              "price": {"type": "number", "minimum": 0},
              "promotionPrice": {"type": "number"},
              "validFrom": {"type": "string", "format": "date-time"},
              "validTo": {"type": "string", "format": "date-time"}
            }
          }
        }
      }
    },
    "inventory": {
      "type": "object",
      "properties": {
        "safetyStock": {"type": "integer", "minimum": 0},
        "reorderPoint": {"type": "integer", "minimum": 0},
        "leadTimeDays": {"type": "integer", "minimum": 0},
        "warehouses": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "warehouseId": {"type": "string"},
              "quantity": {"type": "integer"},
              "reserved": {"type": "integer"},
              "available": {"type": "integer"}
            }
          }
        }
      }
    },
    "suppliers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "supplierId": {"type": "string"},
          "supplierSku": {"type": "string"},
          "isPrimary": {"type": "boolean"},
          "leadTime": {"type": "integer"},
          "moq": {"type": "integer", "description": "Minimum Order Quantity"},
          "costPrice": {"type": "number"}
        }
      }
    },
    "compliance": {
      "type": "object",
      "properties": {
        "certifications": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {"type": "string", "enum": ["3C", "CE", "FDA", "ISO"]},
              "number": {"type": "string"},
              "validUntil": {"type": "string", "format": "date"}
            }
          }
        },
        "countryOfOrigin": {"type": "string", "pattern": "^[A-Z]{2}$"},
        "customsCode": {"type": "string"}
      }
    }
  }
}
```

---

## 实时库存同步实现

```python
import asyncio
import json
from datetime import datetime
from typing import Dict, List
import aioredis
import asyncpg

class OmniChannelInventoryManager:
    """全渠道库存管理器"""
    
    def __init__(self, redis_url: str, db_url: str):
        self.redis = None
        self.db_url = db_url
        self.redis_url = redis_url
        
    async def connect(self):
        """连接数据库和缓存"""
        self.redis = await aioredis.from_url(self.redis_url)
        self.db = await asyncpg.connect(self.db_url)
    
    async def update_inventory(self, gtin: str, warehouse_id: str, 
                               quantity_change: int, reason: str) -> bool:
        """
        更新库存
        
        Args:
            gtin: 商品GTIN
            warehouse_id: 仓库ID
            quantity_change: 数量变化（正数入库，负数出库）
            reason: 变更原因
        
        Returns:
            更新是否成功
        """
        try:
            # 数据库事务更新
            async with self.db.transaction():
                # 获取当前库存
                current = await self.db.fetchval(
                    """SELECT quantity FROM inventory 
                       WHERE gtin = $1 AND warehouse_id = $2""",
                    gtin, warehouse_id
                )
                
                new_quantity = current + quantity_change
                
                if new_quantity < 0:
                    raise ValueError("Insufficient inventory")
                
                # 更新数据库
                await self.db.execute(
                    """UPDATE inventory 
                       SET quantity = $3, updated_at = $4
                       WHERE gtin = $1 AND warehouse_id = $2""",
                    gtin, warehouse_id, new_quantity, datetime.now()
                )
                
                # 记录库存变动
                await self.db.execute(
                    """INSERT INTO inventory_log 
                       (gtin, warehouse_id, change, reason, created_at)
                       VALUES ($1, $2, $3, $4, $5)""",
                    gtin, warehouse_id, quantity_change, reason, datetime.now()
                )
            
            # 更新Redis缓存
            cache_key = f"inventory:{gtin}"
            await self.redis.hincrby(cache_key, warehouse_id, quantity_change)
            
            # 发布库存变更事件
            event = {
                "gtin": gtin,
                "warehouse_id": warehouse_id,
                "change": quantity_change,
                "new_quantity": new_quantity,
                "timestamp": datetime.now().isoformat()
            }
            await self.redis.publish("inventory:changes", json.dumps(event))
            
            return True
        
        except Exception as e:
            print(f"Inventory update failed: {e}")
            return False
    
    async def get_available_inventory(self, gtin: str) -> Dict:
        """获取可用库存（聚合所有渠道）"""
        # 先从缓存获取
        cache_key = f"inventory:{gtin}"
        cached = await self.redis.hgetall(cache_key)
        
        if cached:
            return {
                "gtin": gtin,
                "warehouses": {k: int(v) for k, v in cached.items()},
                "total_available": sum(int(v) for v in cached.values()),
                "source": "cache"
            }
        
        # 缓存未命中，查询数据库
        rows = await self.db.fetch(
            """SELECT warehouse_id, quantity, reserved 
               FROM inventory WHERE gtin = $1""",
            gtin
        )
        
        result = {
            "gtin": gtin,
            "warehouses": {},
            "total_available": 0,
            "source": "database"
        }
        
        for row in rows:
            available = row['quantity'] - row['reserved']
            result["warehouses"][row['warehouse_id']] = available
            result["total_available"] += available
            
            # 回填缓存
            await self.redis.hset(cache_key, row['warehouse_id'], available)
        
        return result
    
    async def reserve_inventory(self, gtin: str, warehouse_id: str, 
                                quantity: int, order_id: str) -> bool:
        """预留库存（订单预占）"""
        try:
            async with self.db.transaction():
                # 检查可用库存
                row = await self.db.fetchrow(
                    """SELECT quantity, reserved FROM inventory
                       WHERE gtin = $1 AND warehouse_id = $2""",
                    gtin, warehouse_id
                )
                
                if not row:
                    return False
                
                available = row['quantity'] - row['reserved']
                if available < quantity:
                    return False
                
                # 增加预留
                await self.db.execute(
                    """UPDATE inventory 
                       SET reserved = reserved + $3
                       WHERE gtin = $1 AND warehouse_id = $2""",
                    gtin, warehouse_id, quantity
                )
                
                # 记录预留
                await self.db.execute(
                    """INSERT INTO inventory_reservation
                       (order_id, gtin, warehouse_id, quantity, status, created_at)
                       VALUES ($1, $2, $3, $4, 'active', $5)""",
                    order_id, gtin, warehouse_id, quantity, datetime.now()
                )
            
            return True
        
        except Exception as e:
            print(f"Reservation failed: {e}")
            return False


class PriceEngine:
    """动态定价引擎"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
    
    async def calculate_price(self, gtin: str, channel_id: str, 
                             customer_segment: str = None) -> Dict:
        """
        计算商品价格
        
        考虑因素：
        - 基础价格
        - 渠道定价策略
        - 客户等级折扣
        - 促销活动
        - 动态定价规则
        """
        # 获取基础价格
        base_price = await self._get_base_price(gtin)
        
        # 应用渠道定价
        channel_price = await self._apply_channel_pricing(
            gtin, channel_id, base_price
        )
        
        # 应用客户折扣
        if customer_segment:
            channel_price = await self._apply_customer_discount(
                channel_price, customer_segment
            )
        
        # 检查促销活动
        promotion = await self._get_active_promotion(gtin, channel_id)
        if promotion:
            channel_price = self._apply_promotion(channel_price, promotion)
        
        return {
            "gtin": gtin,
            "channel_id": channel_id,
            "original_price": base_price,
            "final_price": round(channel_price, 2),
            "currency": "CNY",
            "promotion_applied": promotion is not None
        }
    
    async def _get_base_price(self, gtin: str) -> float:
        """获取基础价格"""
        # 实现省略
        return 100.0
    
    async def _apply_channel_pricing(self, gtin: str, channel_id: str, 
                                    base_price: float) -> float:
        """应用渠道定价策略"""
        # 实现省略
        return base_price
    
    async def _apply_customer_discount(self, price: float, 
                                      segment: str) -> float:
        """应用客户折扣"""
        discounts = {
            "vip": 0.9,
            "gold": 0.95,
            "silver": 0.98
        }
        return price * discounts.get(segment, 1.0)
    
    async def _get_active_promotion(self, gtin: str, channel_id: str):
        """获取有效促销"""
        # 实现省略
        return None
    
    def _apply_promotion(self, price: float, promotion) -> float:
        """应用促销"""
        if promotion['type'] == 'percentage':
            return price * (1 - promotion['value'])
        elif promotion['type'] == 'fixed':
            return max(0, price - promotion['value'])
        return price
```

---

## 供应商数据标准化

```python
class SupplierDataTransformer:
    """供应商数据转换器"""
    
    def __init__(self):
        self.mappings = {}
    
    def register_supplier_mapping(self, supplier_id: str, mapping_config: Dict):
        """
        注册供应商字段映射
        
        Args:
            supplier_id: 供应商ID
            mapping_config: 映射配置
        """
        self.mappings[supplier_id] = mapping_config
    
    def transform_supplier_data(self, supplier_id: str, 
                               raw_data: Dict) -> Dict:
        """
        转换供应商数据为标准格式
        """
        if supplier_id not in self.mappings:
            raise ValueError(f"No mapping registered for supplier {supplier_id}")
        
        mapping = self.mappings[supplier_id]
        result = {}
        
        for standard_field, source_config in mapping.items():
            if isinstance(source_config, str):
                # 简单字段映射
                result[standard_field] = raw_data.get(source_config)
            elif isinstance(source_config, dict):
                # 复杂转换
                source_field = source_config.get('field')
                transform_type = source_config.get('transform')
                
                value = raw_data.get(source_field)
                
                if transform_type == 'concat':
                    # 字符串拼接
                    separator = source_config.get('separator', ' ')
                    fields = source_config.get('fields', [])
                    value = separator.join(
                        str(raw_data.get(f, '')) for f in fields
                    )
                
                elif transform_type == 'unit_conversion':
                    # 单位转换
                    from_unit = source_config.get('from')
                    to_unit = source_config.get('to')
                    value = self._convert_unit(value, from_unit, to_unit)
                
                elif transform_type == 'lookup':
                    # 查找表映射
                    lookup_table = source_config.get('table', {})
                    value = lookup_table.get(value, value)
                
                result[standard_field] = value
        
        return result
    
    def _convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """单位转换"""
        conversions = {
            ('kg', 'g'): 1000,
            ('g', 'kg'): 0.001,
            ('lb', 'kg'): 0.453592,
            ('inch', 'cm'): 2.54
        }
        
        factor = conversions.get((from_unit, to_unit), 1)
        return value * factor if value else None


# 使用示例
if __name__ == "__main__":
    transformer = SupplierDataTransformer()
    
    # 注册供应商映射
    transformer.register_supplier_mapping("SUPPLIER_A", {
        "gtin": "barcode",
        "name": {
            "field": ["brand", "product_name"],
            "transform": "concat",
            "separator": " "
        },
        "weight": {
            "field": "weight",
            "transform": "unit_conversion",
            "from": "lb",
            "to": "kg"
        },
        "category": {
            "field": "category_code",
            "transform": "lookup",
            "table": {
                "ELEC": "Electronics",
                "CLOTH": "Clothing"
            }
        }
    })
    
    # 转换数据
    raw = {
        "barcode": "1234567890123",
        "brand": "Apple",
        "product_name": "iPhone 15",
        "weight": 0.5,
        "category_code": "ELEC"
    }
    
    result = transformer.transform_supplier_data("SUPPLIER_A", raw)
    print(json.dumps(result, indent=2))
```

---

## 实施成果

### 业务效果

| 指标 | 改造前 | 改造后 | 提升 |
|------|--------|--------|------|
| 库存准确率 | 85% | 99.5% | +14.5% |
| 超卖率 | 3% | 0.1% | -2.9% |
| 价格一致性 | 75% | 99% | +24% |
| 商品上架时间 | 3天 | 4小时 | -94% |
| 供应商接入时间 | 2周 | 2天 | -86% |

### 技术架构

```
┌─────────────────────────────────────────┐
│         Omni-Channel Retail Platform    │
├─────────────────────────────────────────┤
│  Web   │  Mobile  │  POS   │  Third-Party│
└────────┴──────────┴────────┴─────────────┘
                    │
        ┌───────────┴───────────┐
        │   API Gateway         │
        └───────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐    ┌────▼────┐    ┌─────▼────┐
│Product │    │ Inventory│    │  Pricing │
│Service │    │ Service  │    │  Service │
└────────┘    └──────────┘    └──────────┘
```

---

**创建时间**: 2026-02-17  
**维护者**: DSL Schema研究团队
