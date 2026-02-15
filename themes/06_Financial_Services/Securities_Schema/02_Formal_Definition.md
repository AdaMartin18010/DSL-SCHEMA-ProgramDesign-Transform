# 证券业务Schema形式化定义

## 📑 目录

- [证券业务Schema形式化定义](#证券业务schema形式化定义)
  - [📑 目录](#-目录)
  - [1. 形式化模型](#1-形式化模型)
  - [2. 订单Schema](#2-订单schema)
  - [3. 持仓Schema](#3-持仓schema)
  - [4. 市场数据Schema](#4-市场数据schema)
  - [5. 结算Schema](#5-结算schema)
  - [6. 类型系统](#6-类型系统)
  - [7. 约束规则](#7-约束规则)
  - [8. 转换函数](#8-转换函数)
  - [9. 形式化定理](#9-形式化定理)
    - [9.1 订单一致性定理](#91-订单一致性定理)
    - [9.2 成交完备性定理](#92-成交完备性定理)
    - [9.3 结算原子性定理](#93-结算原子性定理)
  - [10. 数学模型](#10-数学模型)
    - [10.1 订单状态机](#101-订单状态机)
    - [10.2 结算状态机](#102-结算状态机)
    - [10.3 撮合引擎模型](#103-撮合引擎模型)

---

## 1. 形式化模型

**定义1（证券业务Schema）**：
证券业务Schema是一个六元组：

```text
Securities_Schema = (Order, Position, MarketData, Trade, Settlement, Account)
```

其中：

- `Order`：订单Schema
- `Position`：持仓Schema
- `MarketData`：市场数据Schema
- `Trade`：成交Schema
- `Settlement`：结算Schema
- `Account`：账户Schema

**形式化定义**：

$$
\mathcal{S} = \langle O, P, M, T, L, A, \Sigma, \Phi \rangle
$$

其中：
- $\mathcal{S}$：证券业务Schema
- $O$：订单实体集合
- $P$：持仓实体集合
- $M$：市场数据集合
- $T$：成交实体集合
- $L$：结算实体集合
- $A$：账户实体集合
- $\Sigma$：状态转移函数
- $\Phi$：约束规则集合

---

## 2. 订单Schema

**定义2（订单Schema）**：

```text
Order_Schema = (Order_Basic × Order_Price × Order_Quantity × Order_Time)
```

**形式化DSL定义**：

```dsl
schema SecuritiesOrder {
  // 订单基本信息
  order_basic: OrderBasic {
    order_id: String(30) @required @unique
    client_order_id: String(30) @required @unique
    
    // 账户信息
    account_id: String(30) @required
    client_id: String(20) @required
    
    // 证券信息
    security_code: String(20) @required
    security_name: String(200)?
    security_type: Enum {
      STOCK,              // 股票
      BOND,               // 债券
      FUND,               // 基金
      WARRANT,            // 权证
      OPTION,             // 期权
      FUTURES,            // 期货
      ETF,                // ETF
      LOF,                // LOF
      REIT                // REITs
    } @required
    
    // 交易所信息
    exchange: String(10) @required @pattern("X[A-Z]{3}")
    market_segment: Enum {
      MAIN,               // 主板
      SME,                // 中小板
      GEM,                // 创业板
      STAR,               // 科创板
      BSE                 // 北交所
    }?
    
    // 买卖方向
    side: Enum { BUY, SELL } @required
    
    // 订单类型
    order_type: Enum {
      MARKET,             // 市价单
      LIMIT,              // 限价单
      STOP,               // 止损单
      STOP_LIMIT,         // 止损限价
      IOC,                // 立即成交剩余撤销
      FOK,                // 全部成交或撤销
      GTC,                // 撤销前有效
      ICEBERG             // 冰山单
    } @required
    
    // 订单状态
    order_status: Enum {
      PENDING_SUBMIT,     // 待提交
      PENDING,            // 已报待撤
      NEW,                // 新订单
      PARTIALLY_FILLED,   // 部分成交
      FILLED,             // 完全成交
      CANCELED,           // 已撤单
      REJECTED,           // 已拒绝
      EXPIRED             // 已过期
    } @required
    
    // 订单来源
    order_source: Enum {
      COUNTER,            // 柜台
      INTERNET,           // 网上交易
      MOBILE,             // 手机
      API,                // API
      ALGO,               // 算法交易
      DMA                 // 直接市场接入
    } @required
    
    // 时间戳
    creation_time: DateTime @required
    submission_time: DateTime?
    update_time: DateTime @required
    expiry_time: DateTime?
  }

  // 订单价格信息
  order_price: OrderPrice {
    // 限价单
    limit_price: Decimal(15,4)?
    
    // 止损单
    stop_price: Decimal(15,4)?
    
    // 市价单保护限价
    price_protect_limit: Decimal(15,4)?
    
    // 价格类型
    price_type: Enum {
      BY_LIMIT,           // 限价
      BY_MARKET_BEST_5,   // 最优五档即时成交
      BY_MARKET_BEST,     // 对手方最优
      BY_MARKEST_OWN_BEST,// 本方最优
      BY_MARKET_IOC,      // 即时成交剩余撤销
      BY_MARKET_FOK,      // 最优五档即时成交剩余撤销
      BY_MARKET_5_IOC,    // 全额成交或撤销
      BY_MARKET_5_FOK     // 最优五档全额成交或撤销
    } @required
    
    // 价格限制
    price_ceiling: Decimal(15,4)?
    price_floor: Decimal(15,4)?
    
    // 实际成交价格
    avg_fill_price: Decimal(15,4) @default(0)
    last_fill_price: Decimal(15,4) @default(0)
  }

  // 订单数量信息
  order_quantity: OrderQuantity {
    // 订单数量
    order_quantity: Decimal(15,0) @required @min(1)
    
    // 最小成交数量（适用于FOK/IOC）
    min_fill_quantity: Decimal(15,0) @default(0)
    
    // 已成交数量
    filled_quantity: Decimal(15,0) @default(0)
    
    // 剩余数量
    remaining_quantity: Decimal(15,0) @default(0)
    
    // 已撤单数量
    canceled_quantity: Decimal(15,0) @default(0)
    
    // 显示数量（冰山单）
    display_quantity: Decimal(15,0)?
    hidden_quantity: Decimal(15,0)?
    
    // 数量单位
    quantity_unit: Enum { SHARES, LOTS, HANDS } @default("SHARES")
    lot_size: Integer @default(100)
  }

  // 订单时间属性
  order_time: OrderTime {
    // 有效期
    time_in_force: Enum {
      DAY,                // 当日有效
      GTC,                // 撤销前有效
      IOC,                // 立即成交剩余撤销
      FOK,                // 全部成交或撤销
      GTD,                // 指定日期前有效
      AT_OPEN,            // 开盘
      AT_CLOSE            // 收盘
    } @required
    
    // 到期日期
    expiry_date: Date?
    
    // 特定交易时段
    trading_session: Enum {
      PRE_MARKET,         // 盘前
      CONTINUOUS,         // 连续竞价
      POST_MARKET,        // 盘后
      AUCTION             // 集合竞价
    } @default("CONTINUOUS")
    
    // 提交时间
    submit_time: DateTime?
    
    // 成交时间
    fill_time: DateTime?
    
    // 撤单时间
    cancel_time: DateTime?
  }
} @domain("SECURITIES") @version("1.0")
```

**订单数学模型**：

**订单价值计算**：

$$
\text{Order Value} = \text{Order Quantity} \times \text{Order Price}
$$

**剩余数量计算**：

$$
\text{Remaining Quantity} = \text{Order Quantity} - \text{Filled Quantity} - \text{Canceled Quantity}
$$

---

## 3. 持仓Schema

**定义3（持仓Schema）**：

```text
Position_Schema = (Security_Position × Cash_Position × Margin_Position)
```

**形式化DSL定义**：

```dsl
schema SecuritiesPosition {
  // 证券持仓
  security_position: SecurityPosition {
    position_id: String(30) @required @unique
    account_id: String(30) @required
    security_code: String(20) @required
    
    // 持仓方向
    position_side: Enum { LONG, SHORT } @required
    
    // 持仓数量
    total_quantity: Decimal(15,0) @required @min(0)
    available_quantity: Decimal(15,0) @required @min(0)
    frozen_quantity: Decimal(15,0) @required @min(0) @default(0)
    pledged_quantity: Decimal(15,0) @required @min(0) @default(0)
    
    // 持仓成本
    cost_price: Decimal(15,4) @required @min(0)
    total_cost: Decimal(18,2) @required @min(0)
    
    // 市值
    market_price: Decimal(15,4) @required @min(0)
    market_value: Decimal(18,2) @required @min(0)
    
    // 盈亏
    realized_pnl: Decimal(18,2) @default(0)
    unrealized_pnl: Decimal(18,2) @default(0)
    total_pnl: Decimal(18,2) @default(0)
    
    // 盈亏率
    return_rate: Decimal(10,6) @default(0)
    
    // 更新时间
    last_update_time: DateTime @required
    valuation_date: Date @required
    
    // 持仓来源
    position_source: Enum {
      BUY,                // 买入
      SELL_SHORT,         // 卖空
      TRANSFER_IN,        // 转入
      ALLOTMENT,          // 配股
      DIVIDEND,           // 送股
      MERGER              // 合并
    } @required
  }

  // 资金持仓
  cash_position: CashPosition {
    account_id: String(30) @required @unique
    currency: String(3) @required @pattern("[A-Z]{3}")
    
    // 资金余额
    balance: Decimal(18,2) @required
    available_balance: Decimal(18,2) @required
    frozen_balance: Decimal(18,2) @required @default(0)
    
    // 可取资金
    withdrawable_balance: Decimal(18,2) @required
    
    // 在途资金
    unsettled_balance: Decimal(18,2) @required @default(0)
    
    // 购买力
    buying_power: Decimal(18,2) @required
    
    // 更新时间
    last_update_time: DateTime @required
  }

  // 保证金持仓（融资融券）
  margin_position: MarginPosition {
    margin_account_id: String(30) @required @unique
    account_id: String(30) @required
    
    // 保证金余额
    margin_balance: Decimal(18,2) @required
    
    // 融资负债
    debit_balance: Decimal(18,2) @required @default(0)
    
    // 融券负债
    short_balance: Decimal(18,2) @required @default(0)
    
    // 维持担保比例
    maintenance_ratio: Decimal(5,2) @required
    
    // 警戒线
    warning_line: Decimal(5,2) @required @default(150)
    
    // 平仓线
    liquidation_line: Decimal(5,2) @required @default(130)
    
    // 融资利率
    debit_interest_rate: Decimal(5,4) @required
    
    // 融券费率
    short_fee_rate: Decimal(5,4) @required
    
    // 融资融券额度
    debit_quota: Decimal(18,2) @required
    short_quota: Decimal(18,2) @required
    
    // 可用额度
    available_debit_quota: Decimal(18,2) @required
    available_short_quota: Decimal(18,2) @required
  }
} @domain("SECURITIES") @version("1.0")
```

**持仓数学模型**：

**市值计算**：

$$
\text{Market Value} = \text{Total Quantity} \times \text{Market Price}
$$

**浮动盈亏计算**：

$$
\text{Unrealized P\&L} = (\text{Market Price} - \text{Cost Price}) \times \text{Total Quantity}
$$

**盈亏率计算**：

$$
\text{Return Rate} = \frac{\text{Market Price} - \text{Cost Price}}{\text{Cost Price}} \times 100\%
$$

**维持担保比例**：

$$
\text{Maintenance Ratio} = \frac{\text{Margin Balance} + \text{Market Value of Collateral}}{\text{Debit Balance} + \text{Short Market Value}} \times 100\%
$$

---

## 4. 市场数据Schema

**定义4（市场数据Schema）**：

```text
Market_Data_Schema = (Quote × Trade_Tick × Order_Book × Index_Data)
```

**形式化DSL定义**：

```dsl
schema MarketData {
  // 行情报价
  quote: Quote {
    quote_id: String(30) @required @unique
    security_code: String(20) @required
    exchange: String(10) @required
    
    // 时间戳
    timestamp: DateTime @required
    date: Date @required
    time: Time @required
    
    // 价格
    last_price: Decimal(15,4) @required
    open_price: Decimal(15,4) @required
    high_price: Decimal(15,4) @required
    low_price: Decimal(15,4) @required
    close_price: Decimal(15,4)?
    prev_close: Decimal(15,4) @required
    
    // 涨跌
    change: Decimal(15,4) @required
    change_percent: Decimal(10,6) @required
    
    // 成交量额
    volume: Decimal(15,0) @required
    turnover: Decimal(18,2) @required
    
    // 盘口
    bid_prices: List<Decimal(15,4)> @length(5)
    bid_volumes: List<Decimal(15,0)> @length(5)
    ask_prices: List<Decimal(15,4)> @length(5)
    ask_volumes: List<Decimal(15,0)> @length(5)
    
    // 统计
    bid_volume_total: Decimal(15,0) @required
    ask_volume_total: Decimal(15,0) @required
    
    // 成交均价
    vwap: Decimal(15,4)?
    
    // 涨跌停
    upper_limit: Decimal(15,4) @required
    lower_limit: Decimal(15,4) @required
    
    // 停牌标志
    is_suspended: Boolean @default(false)
    
    // 数据质量
    quote_type: Enum { REALTIME, DELAYED, CLOSING } @required
  }

  // 逐笔成交
  trade_tick: TradeTick {
    tick_id: String(30) @required @unique
    security_code: String(20) @required
    exchange: String(10) @required
    
    // 时间
    timestamp: DateTime @required
    date: Date @required
    time: Time @required
    
    // 成交价格数量
    price: Decimal(15,4) @required
    volume: Decimal(15,0) @required
    amount: Decimal(18,2) @required
    
    // 买卖方向
    trade_type: Enum { BUY, SELL, UNKNOWN } @required
    
    // 成交类型
    exec_type: Enum {
      CONTINUOUS,         // 连续竞价
      AUCTION,            // 集合竞价
      BLOCK,              // 大宗交易
      AFTER_HOURS         // 盘后交易
    } @required
    
    // 订单ID（如有）
    bid_order_id: String(30)?
    ask_order_id: String(30)?
    
    // 序号
    sequence_number: Integer @required
  }

  // 订单簿
  order_book: OrderBook {
    book_id: String(30) @required @unique
    security_code: String(20) @required
    exchange: String(10) @required
    
    // 时间戳
    timestamp: DateTime @required
    
    // 深度
    depth: Integer @required @default(10)
    
    // 买单队列
    bids: List<OrderBookLevel> {
      level: Integer @required
      price: Decimal(15,4) @required
      total_volume: Decimal(15,0) @required
      order_count: Integer @required
      orders: List<OrderInBook> {
        order_id: String(30) @required
        volume: Decimal(15,0) @required
        timestamp: DateTime @required
      }
    }
    
    // 卖单队列
    asks: List<OrderBookLevel> {
      level: Integer @required
      price: Decimal(15,4) @required
      total_volume: Decimal(15,0) @required
      order_count: Integer @required
      orders: List<OrderInBook> {
        order_id: String(30) @required
        volume: Decimal(15,0) @required
        timestamp: DateTime @required
      }
    }
    
    // 汇总
    total_bid_volume: Decimal(15,0) @required
    total_ask_volume: Decimal(15,0) @required
    bid_ask_spread: Decimal(15,4) @required
    mid_price: Decimal(15,4) @required
    weighted_mid_price: Decimal(15,4)?
  }

  // 指数数据
  index_data: IndexData {
    index_code: String(20) @required @unique
    index_name: String(100) @required
    
    // 时间
    timestamp: DateTime @required
    date: Date @required
    
    // 指数值
    index_value: Decimal(15,4) @required
    open_value: Decimal(15,4) @required
    high_value: Decimal(15,4) @required
    low_value: Decimal(15,4) @required
    close_value: Decimal(15,4)?
    prev_close_value: Decimal(15,4) @required
    
    // 涨跌
    change: Decimal(15,4) @required
    change_percent: Decimal(10,6) @required
    
    // 成交量额
    total_volume: Decimal(15,0) @required
    total_turnover: Decimal(18,2) @required
    
    // 成分股数量
    constituent_count: Integer @required
    
    // 上涨下跌家数
    advancing_count: Integer @required
    declining_count: Integer @required
    unchanged_count: Integer @required
    
    // 基准日期
    base_date: Date @required
    base_value: Decimal(15,4) @required
  }
} @domain("SECURITIES") @version("1.0")
```

**市场数据数学模型**：

**涨跌幅计算**：

$$
\text{Change Percent} = \frac{\text{Last Price} - \text{Prev Close}}{\text{Prev Close}} \times 100\%
$$

**买卖价差**：

$$
\text{Bid-Ask Spread} = \text{Ask Price}_1 - \text{Bid Price}_1
$$

**中间价**：

$$
\text{Mid Price} = \frac{\text{Ask Price}_1 + \text{Bid Price}_1}{2}
$$

**成交量加权平均价（VWAP）**：

$$
\text{VWAP} = \frac{\sum_{i} \text{Price}_i \times \text{Volume}_i}{\sum_{i} \text{Volume}_i}
$$

---

## 5. 结算Schema

**定义5（结算Schema）**：

```text
Settlement_Schema = (Trade_Confirmation × Clearing × Settlement_Instruction × Delivery)
```

**形式化DSL定义**：

```dsl
schema SecuritiesSettlement {
  // 成交确认
  trade_confirmation: TradeConfirmation {
    confirmation_id: String(30) @required @unique
    trade_id: String(30) @required @unique
    
    // 成交信息
    trade_date: Date @required
    trade_time: Time @required
    
    // 买方信息
    buyer_account_id: String(30) @required
    buyer_settlement_id: String(30) @required
    
    // 卖方信息
    seller_account_id: String(30) @required
    seller_settlement_id: String(30) @required
    
    // 证券信息
    security_code: String(20) @required
    security_name: String(200)?
    
    // 成交数量价格
    trade_quantity: Decimal(15,0) @required
    trade_price: Decimal(15,4) @required
    trade_amount: Decimal(18,2) @required
    
    // 费用
    commission: Decimal(18,2) @required
    stamp_tax: Decimal(18,2) @required
    transfer_fee: Decimal(18,2) @required
    handling_fee: Decimal(18,2) @required
    total_fees: Decimal(18,2) @required
    
    // 净额
    buyer_net_amount: Decimal(18,2) @required
    seller_net_amount: Decimal(18,2) @required
    
    // 结算日期
    settlement_date: Date @required
    settlement_type: Enum { T0, T1, T2, T3 } @required
    
    // 状态
    confirmation_status: Enum { PENDING, CONFIRMED, REJECTED } @required
  }

  // 清算
  clearing: Clearing {
    clearing_id: String(30) @required @unique
    clearing_date: Date @required
    
    // 清算类型
    clearing_type: Enum {
      GROSS,              // 总额清算
      NET_BY_SECURITY,    // 证券净额
      NET_BY_VALUE,       // 资金净额
      MULTILATERAL_NET    // 多边净额
    } @required
    
    // 参与人清算汇总
    participant_clearings: List<ParticipantClearing> {
      participant_id: String(20) @required
      settlement_id: String(30) @required
      
      // 证券应收应付
      securities_receivable: List<SecurityPosition> {
        security_code: String(20) @required
        quantity: Decimal(15,0) @required
      }
      
      securities_payable: List<SecurityPosition> {
        security_code: String(20) @required
        quantity: Decimal(15,0) @required
      }
      
      // 资金应收应付
      cash_receivable: Decimal(18,2) @required
      cash_payable: Decimal(18,2) @required
      
      // 净额
      net_securities: List<SecurityPosition>?
      net_cash: Decimal(18,2) @required
    }
    
    // 清算状态
    clearing_status: Enum { PENDING, COMPLETED, FAILED } @required
    
    // 时间戳
    clearing_start_time: DateTime @required
    clearing_end_time: DateTime?
  }

  // 结算指令
  settlement_instruction: SettlementInstruction {
    instruction_id: String(30) @required @unique
    
    // 结算参与人
    delivering_agent: String(20) @required
    receiving_agent: String(20) @required
    
    // 结算要素
    security_code: String(20) @required
    settlement_quantity: Decimal(15,0) @required
    settlement_amount: Decimal(18,2) @required
    settlement_date: Date @required
    
    // 结算方式
    settlement_method: Enum { DVP, DVP_FREE, FREE } @required
    
    // 关联成交
    trade_ids: List<String(30)> @required
    
    // 状态
    instruction_status: Enum {
      PENDING,
      MATCHED,
      SETTLED,
      FAILED,
      CANCELED
    } @required
    
    // 失败原因
    fail_reason: String(200)?
    fail_code: String(10)?
    
    // 时间
    instruction_time: DateTime @required
    settlement_time: DateTime?
  }

  // 交收结果
  delivery: Delivery {
    delivery_id: String(30) @required @unique
    instruction_id: String(30) @required
    
    // 证券交收
    security_delivery: SecurityDelivery {
      depository: String(20) @required
      from_account: String(30) @required
      to_account: String(30) @required
      security_code: String(20) @required
      quantity: Decimal(15,0) @required
      delivery_status: Enum { PENDING, DELIVERED, FAILED } @required
      delivery_time: DateTime?
    }
    
    // 资金交收
    cash_delivery: CashDelivery {
      settlement_bank: String(20) @required
      from_account: String(30) @required
      to_account: String(30) @required
      amount: Decimal(18,2) @required
      currency: String(3) @required
      delivery_status: Enum { PENDING, PAID, FAILED } @required
      delivery_time: DateTime?
    }
    
    // 总体状态
    overall_status: Enum { PENDING, COMPLETED, PARTIAL, FAILED } @required
    
    // DVP标志
    is_dvp: Boolean @required
    dvp_link_id: String(30)?
    
    settlement_complete_time: DateTime?
  }
} @domain("SECURITIES") @version("1.0")
```

**结算数学模型**：

**净额计算**：

$$
\text{Net Cash} = \text{Cash Receivable} - \text{Cash Payable}
$$

**DVP结算条件**：

$$
\text{DVP Settlement} \Leftrightarrow \text{Security Delivery} \land \text{Cash Delivery}
$$

---

## 6. 类型系统

**定义6（证券业务数据类型）**：

```text
Securities_Data_Type = Order_Type | Position_Type | Market_Data_Type | Settlement_Type
```

**基本类型定义**：

```dsl
type AccountIdentification {
  account_type: Enum { CASH, MARGIN, CREDIT } @required
  account_number: String(30) @required
  account_holder_name: String(140) @required
  branch_code: String(20) @required
}

type SecurityIdentification {
  security_code: String(20) @required
    isin: String(12)? @pattern("[A-Z]{2}[A-Z0-9]{9}[0-9]")
  sedol: String(7)?
  cusip: String(9)?
  exchange: String(10) @required
}

type PriceLimit {
  upper_limit: Decimal(15,4) @required
  lower_limit: Decimal(15,4) @required
  limit_type: Enum { PERCENTAGE, ABSOLUTE } @required
}

type TradingSession {
  session_id: String(10) @required
  session_name: String(50) @required
  start_time: Time @required
  end_time: Time @required
  session_type: Enum { PRE_OPEN, OPEN, CONTINUOUS, CLOSE, POST_CLOSE } @required
}

type FeeStructure {
  commission_rate: Decimal(10,6) @required
  min_commission: Decimal(10,2) @required
  max_commission: Decimal(10,2)?
  stamp_tax_rate: Decimal(10,6) @required
  transfer_fee_rate: Decimal(10,6) @required
  handling_fee_rate: Decimal(10,6) @required
}
```

---

## 7. 约束规则

**约束1（订单有效性）**：

```text
∀ order ∈ Order:
  order.order_quantity > 0
  ∧ (order.order_type = LIMIT → order.limit_price > 0)
  ∧ (order.order_type = STOP → order.stop_price > 0)
  ∧ (order.order_type = STOP_LIMIT → order.stop_price > 0 ∧ order.limit_price > 0)
  ∧ order.remaining_quantity ≥ 0
  ∧ order.filled_quantity ≤ order.order_quantity
  ∧ order.canceled_quantity ≤ order.order_quantity
```

**约束2（持仓一致性）**：

```text
∀ position ∈ SecurityPosition:
  position.total_quantity ≥ 0
  ∧ position.available_quantity ≥ 0
  ∧ position.frozen_quantity ≥ 0
  ∧ position.pledged_quantity ≥ 0
  ∧ position.total_quantity = position.available_quantity + position.frozen_quantity + position.pledged_quantity
  ∧ position.market_value = position.total_quantity × position.market_price
```

**约束3（资金一致性）**：

```text
∀ cash ∈ CashPosition:
  cash.balance ≥ 0
  ∧ cash.available_balance ≥ 0
  ∧ cash.frozen_balance ≥ 0
  ∧ cash.balance = cash.available_balance + cash.frozen_balance
  ∧ cash.withdrawable_balance ≤ cash.available_balance
```

**约束4（保证金充足性）**：

```text
∀ margin ∈ MarginPosition:
  margin.maintenance_ratio ≥ margin.liquidation_line
  ∧ margin.available_debit_quota ≥ 0
  ∧ margin.available_short_quota ≥ 0
```

**约束5（结算匹配）**：

```text
∀ settlement ∈ SettlementInstruction:
  settlement.settlement_quantity > 0
  ∧ settlement.settlement_amount > 0
  ∧ (settlement.settlement_method = DVP → settlement.is_dvp = true)
```

---

## 8. 转换函数

**函数1（订单到FIX转换）**：

```text
convert_order_to_fix: Order → FIXMessage
```

**函数2（FIX到内部格式转换）**：

```text
convert_fix_to_order: FIXMessage → Order
```

**函数3（成交到结算指令转换）**：

```text
convert_trade_to_settlement: Trade → SettlementInstruction
```

**函数4（行情到K线转换）**：

```text
convert_ticks_to_kline: List<TradeTick> → KLine
```

**函数5（持仓盈亏计算）**：

```text
calculate_position_pnl: Position × Decimal → PnLResult
calculate_position_pnl(position, market_price) = {
  unrealized_pnl = (market_price - position.cost_price) × position.total_quantity,
  total_pnl = position.realized_pnl + unrealized_pnl,
  return_rate = (market_price - position.cost_price) / position.cost_price
}
```

---

## 9. 形式化定理

### 9.1 订单一致性定理

**定理1（订单数量守恒）**：

```text
∀ order ∈ Order:
  order.order_quantity = order.filled_quantity + order.remaining_quantity + order.canceled_quantity
```

**证明**：
由定义2中OrderQuantity的约束可得：
$$
\text{Order Quantity} = \text{Filled} + \text{Remaining} + \text{Canceled}
$$
这是订单数量守恒的基本性质 $\square$

### 9.2 成交完备性定理

**定理2（成交与订单一致性）**：

```text
∀ order ∈ Order:
  let trades = get_trades_for_order(order)
  in sum([t.trade_quantity for t in trades]) = order.filled_quantity
```

**证明**：
由成交记录与订单的关联关系，所有与该订单相关的成交数量之和应等于订单的已成交数量。$\square$

### 9.3 结算原子性定理

**定理3（DVP结算原子性）**：

```text
∀ settlement ∈ Settlement where settlement.is_dvp:
  (settlement.security_delivery.status = DELIVERED ∧ settlement.cash_delivery.status = PAID)
  ∨
  (settlement.security_delivery.status ≠ DELIVERED ∧ settlement.cash_delivery.status ≠ PAID)
```

**证明**：
DVP（券款对付）结算要求证券交割和资金支付同时完成或同时失败，不存在部分完成状态。$\square$

---

## 10. 数学模型

### 10.1 订单状态机

**订单状态转换**：

```
                    ┌─────────────┐
                    │   PENDING   │
                    │   SUBMIT    │
                    └──────┬──────┘
                           │ submit
                           ▼
                     ┌─────────────┐
                     │     NEW     │
                     └──────┬──────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            │ partial       │ filled        │ cancel
            ▼               │               ▼
     ┌─────────────┐        │        ┌─────────────┐
     │  PARTIALLY  │────────┴───────►│   FILLED    │
     │   FILLED    │      fill       │             │
     └──────┬──────┘                 └─────────────┘
            │
     cancel │
            ▼
     ┌─────────────┐
     │  CANCELED   │
     └─────────────┘
            ▲
            │ reject
            │
     ┌─────────────┐
     │  REJECTED   │
     └─────────────┘
            ▲
            │ expire
            │
     ┌─────────────┐
     │   EXPIRED   │
     └─────────────┘
```

**状态转移函数**：

$$
\delta_O: S_O \times E_O \rightarrow S_O
$$

其中：
- $S_O = \{\text{PENDING\_SUBMIT}, \text{NEW}, \text{PARTIALLY\_FILLED}, \text{FILLED}, \text{CANCELED}, \text{REJECTED}, \text{EXPIRED}\}$
- $E_O = \{\text{submit}, \text{partial\_fill}, \text{fill}, \text{cancel}, \text{reject}, \text{expire}\}$

### 10.2 结算状态机

**结算状态转换**：

```
┌───────────┐  match   ┌───────────┐  settle  ┌───────────┐
│  PENDING  │─────────►│  MATCHED  │─────────►│  SETTLED  │
│INSTRUCTION│          │           │          │           │
└───────────┘          └─────┬─────┘          └───────────┘
      │                      │                      ▲
      │                      │ fail                 │
      │                      ▼                      │
      │               ┌───────────┐               │
      │               │   FAILED  │───────────────┘
      │               │           │  retry
      │               └───────────┘
      │
      │ cancel
      ▼
┌───────────┐
│ CANCELED  │
└───────────┘
```

**状态转移函数**：

$$
\delta_L: S_L \times E_L \rightarrow S_L
$$

### 10.3 撮合引擎模型

**价格优先时间优先撮合模型**：

**匹配条件**：

对于买单 $b$ 和卖单 $s$，成交条件为：

$$
b.\text{price} \geq s.\text{price}
$$

**成交价格确定**：

$$
\text{Trade Price} = \begin{cases}
s.\text{price} & \text{if } b.\text{time} < s.\text{time} \\
b.\text{price} & \text{if } s.\text{time} < b.\text{time} \\
\min(b.\text{price}, s.\text{price}) & \text{otherwise}
\end{cases}
$$

**撮合优先级函数**：

对于买单队列 $B$ 和卖单队列 $S$：

$$
\text{Priority}(o) = (-o.\text{price}, o.\text{time}) \quad \text{for } o \in B
$$

$$
\text{Priority}(o) = (o.\text{price}, o.\text{time}) \quad \text{for } o \in S
$$

**撮合算法**：

```
Algorithm: Price-Time Matching Engine

Input: Buy orders B, Sell orders S
Output: Trades T

1. Sort B by priority (descending)
2. Sort S by priority (ascending)
3. While B ≠ ∅ and S ≠ ∅ and best_bid ≥ best_ask:
   a. b ← B.head
   b. s ← S.head
   c. If b.price ≥ s.price:
      i.   trade_qty ← min(b.remaining, s.remaining)
      ii.  trade_price ← determine_price(b, s)
      iii. Create trade t(trade_qty, trade_price, b, s)
      iv.  T ← T ∪ {t}
      v.   Update b.remaining and s.remaining
      vi.  If b.remaining = 0: Remove b from B
      vii. If s.remaining = 0: Remove s from S
   d. Else: Break
4. Return T
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
