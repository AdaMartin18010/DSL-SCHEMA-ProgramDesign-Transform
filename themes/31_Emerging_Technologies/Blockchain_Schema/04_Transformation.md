# 区块链Schema转换体系

## 📑 目录

- [区块链Schema转换体系](#区块链schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 转换方向](#2-转换方向)
  - [3. Solidity转换](#3-solidity转换)
  - [4. Web3转换](#4-web3转换)
  - [5. PostgreSQL存储](#5-postgresql存储)
  - [6. 转换工具](#6-转换工具)
  - [7. 转换验证](#7-转换验证)

---

## 1. 转换体系概述

区块链Schema转换体系支持**区块链Schema到各种格式的转换**，包括Solidity、Web3、PostgreSQL等格式。

**转换目标**：

- Solidity代码
- Web3 JSON格式
- PostgreSQL数据库
- JSON格式

---

## 2. 转换方向

### 2.1 转换矩阵

| 转换方向 | 源格式 | 目标格式 | 转换复杂度 | 工具支持 | 数据完整性 |
|---------|--------|----------|------------|----------|------------|
| **Blockchain → Solidity** | Blockchain_Schema | Solidity | ⭐⭐⭐ | ✅ 良好 | 高 |
| **Blockchain → Web3** | Blockchain_Schema | Web3 JSON | ⭐⭐ | ✅ 良好 | 高 |
| **Blockchain → PostgreSQL** | Blockchain_Schema | SQL DDL | ⭐⭐⭐ | ✅ 良好 | 高 |
| **Blockchain → JSON** | Blockchain_Schema | JSON Schema | ⭐⭐ | ✅ 良好 | 高 |

---

## 3. Solidity转换

### 3.1 Blockchain → Solidity转换

**转换函数**：

```text
to_solidity: Blockchain_Schema → Solidity_Code
```

**转换示例**：

**输入（Blockchain_Schema）**：

```dsl
smart_contract ERC20_Token {
  functions: [
    transfer(to: Address, value: Wei),
    approve(spender: Address, value: Wei),
    balanceOf(owner: Address): Wei
  ]
  state: {
    balances: Map[Address, Wei]
    allowances: Map[Address, Map[Address, Wei]]
  }
}
```

**输出（Solidity）**：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ERC20Token {
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowances;

    function transfer(address to, uint256 value) public returns (bool) {
        require(balances[msg.sender] >= value, "Insufficient balance");
        balances[msg.sender] -= value;
        balances[to] += value;
        return true;
    }

    function approve(address spender, uint256 value) public returns (bool) {
        allowances[msg.sender][spender] = value;
        return true;
    }

    function balanceOf(address owner) public view returns (uint256) {
        return balances[owner];
    }
}
```

---

## 4. Web3转换

### 4.1 Blockchain → Web3转换

**转换函数**：

```text
to_web3: Blockchain_Schema → Web3_JSON
```

**转换示例**：

```json
{
  "contractAddress": "0x...",
  "abi": [
    {
      "name": "transfer",
      "type": "function",
      "inputs": [
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"}
      ],
      "outputs": [{"name": "", "type": "bool"}]
    }
  ],
  "bytecode": "0x..."
}
```

---

## 5. PostgreSQL存储

### 5.1 数据库Schema设计

```sql
CREATE TABLE smart_contracts (
    id VARCHAR(50) PRIMARY KEY,
    address VARCHAR(42) UNIQUE,
    abi JSONB,
    bytecode TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transactions (
    hash VARCHAR(66) PRIMARY KEY,
    from_address VARCHAR(42),
    to_address VARCHAR(42),
    value NUMERIC(78, 0),
    gas_limit INTEGER,
    gas_price NUMERIC(78, 0),
    block_number INTEGER,
    block_hash VARCHAR(66),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE blocks (
    hash VARCHAR(66) PRIMARY KEY,
    number INTEGER UNIQUE,
    parent_hash VARCHAR(66),
    timestamp TIMESTAMP,
    miner VARCHAR(42),
    transaction_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. 转换工具

### 6.1 开源工具

- **Solidity Compiler**：Solidity编译器
- **Web3.js**：Web3 JavaScript库
- **ethers.js**：ethers.js库

---

## 7. 转换验证

### 7.1 合约验证

**验证方法**：

1. 验证Solidity代码语法
2. 验证ABI正确性
3. 验证字节码一致性

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队
