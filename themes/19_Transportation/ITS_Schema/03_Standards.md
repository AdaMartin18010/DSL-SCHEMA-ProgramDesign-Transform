# 智能交通系统Schema标准对标

## 📑 目录

- [智能交通系统Schema标准对标](#智能交通系统schema标准对标)
  - [📑 目录](#-目录)
  - [1. 标准体系概述](#1-标准体系概述)
    - [1.1 标准层次结构](#11-标准层次结构)
    - [1.2 标准关系](#12-标准关系)
  - [2. ISO标准](#2-iso标准)
    - [2.1 ISO 14813标准](#21-iso-14813标准)
    - [2.2 ISO 21217标准](#22-iso-21217标准)
    - [2.3 ISO 17465标准](#23-iso-17465标准)
  - [3. IEEE标准](#3-ieee标准)
    - [3.1 IEEE 1609标准](#31-ieee-1609标准)
    - [3.2 IEEE 802.11p标准](#32-ieee-80211p标准)
  - [4. ETSI标准](#4-etsi标准)
    - [4.1 ETSI EN 302 637标准](#41-etsi-en-302-637标准)
    - [4.2 ETSI TS 102 894标准](#42-etsi-ts-102-894标准)
  - [5. SAE标准](#5-sae标准)
    - [5.1 SAE J2735标准](#51-sae-j2735标准)
    - [5.2 SAE J2945标准](#52-sae-j2945标准)
  - [6. 标准对比矩阵](#6-标准对比矩阵)
  - [7. 标准实施建议](#7-标准实施建议)
    - [7.1 实施优先级](#71-实施优先级)
    - [7.2 实施步骤](#72-实施步骤)
  - [8. 标准发展趋势](#8-标准发展趋势)
    - [8.1 2024-2025年趋势](#81-2024-2025年趋势)
    - [8.2 2025-2026年展望](#82-2025-2026年展望)

---

## 1. 标准体系概述

ITS Schema标准体系分为四个层次：

1. **ISO标准**：国际标准化组织制定的ITS参考架构和服务标准
2. **IEEE标准**：IEEE制定的车载环境无线接入（WAVE）标准
3. **ETSI标准**：欧洲电信标准协会制定的ITS通信标准
4. **SAE标准**：SAE制定的车辆通信消息集标准

### 1.1 标准层次结构

```text
ISO标准（参考架构、服务定义）
    ↓
IEEE标准（WAVE通信协议）
    ↓
ETSI/SAE标准（消息格式、应用层）
    ↓
ITS_Schema（数据模型、转换实现）
```

### 1.2 标准关系

```text
ISO 14813（参考架构）
    ↓
IEEE 1609（WAVE协议栈）
    ↓
ETSI ITS / SAE J2735（消息集）
    ↓
ITS_Schema（数据模型和转换）
```

---

## 2. ISO标准

### 2.1 ISO 14813标准

**标准编号**：ISO 14813

**标准名称**：Intelligent transport systems — Reference architecture

**核心内容**：

- **ITS参考架构**：智能交通系统参考架构模型
- **ITS服务定义**：ITS服务分类和定义
- **ITS数据模型**：ITS数据交换模型
- **ITS接口定义**：ITS系统接口规范

**Schema映射**：

| ISO 14813概念 | Schema映射 |
|--------------|-----------|
| ITS Reference Architecture | ITS_Schema |
| ITS Service | Traffic_Service_Schema |
| ITS Data Model | Traffic_Data_Schema |
| ITS Interface | Communication_Interface_Schema |

**Schema支持**：完整支持

**最新版本**：ISO 14813:2021

**参考链接**：
[ISO官网](https://www.iso.org/)

**标准文档**：

- ISO 14813-1:2021 - ITS参考架构模型
- ISO 14813-2:2021 - 核心ITS数据字典
- ISO 14813-3:2021 - ITS服务定义
- ISO 14813-4:2021 - ITS接口定义

---

### 2.2 ISO 21217标准

**标准编号**：ISO 21217

**标准名称**：Intelligent transport systems — Communications access for land mobiles (CALM) — Architecture

**核心内容**：

- **CALM架构**：通信接入陆地移动（CALM）架构
- **多接口支持**：支持多种通信接口（Wi-Fi、蜂窝网络、DSRC等）
- **网络层协议**：IPv6网络层协议

**Schema映射**：

| ISO 21217概念 | Schema映射 |
|--------------|-----------|
| CALM Architecture | Communication_Architecture_Schema |
| Multi-Interface | Multi_Interface_Schema |
| IPv6 Network Layer | Network_Layer_Schema |

**Schema支持**：完整支持

**最新版本**：ISO 21217:2020

---

### 2.3 ISO 17465标准

**标准编号**：ISO 17465

**标准名称**：Intelligent transport systems — Cooperative ITS — Dictionary of in-vehicle information (IVI) data structures

**核心内容**：

- **IVI数据结构**：车内信息（IVI）数据结构字典
- **数据交换格式**：IVI数据交换格式定义
- **应用层协议**：IVI应用层协议

**Schema映射**：

| ISO 17465概念 | Schema映射 |
|--------------|-----------|
| IVI Data Structure | IVI_Data_Schema |
| Data Exchange Format | Data_Exchange_Schema |
| Application Protocol | Application_Protocol_Schema |

**Schema支持**：完整支持

**最新版本**：ISO 17465:2016

---

## 3. IEEE标准

### 3.1 IEEE 1609标准

**标准编号**：IEEE 1609

**标准名称**：Wireless Access in Vehicular Environments (WAVE)

**核心内容**：

- **IEEE 1609.0**：WAVE架构概述
- **IEEE 1609.2**：安全服务（消息认证、加密）
- **IEEE 1609.3**：网络服务（IPv6、WSM）
- **IEEE 1609.4**：多信道操作（信道切换、同步）

**Schema映射**：

| IEEE 1609概念 | Schema映射 |
|--------------|-----------|
| WAVE Architecture | WAVE_Architecture_Schema |
| Security Services | Security_Schema |
| Network Services | Network_Services_Schema |
| Multi-Channel Operation | Multi_Channel_Schema |

**Schema支持**：完整支持

**最新版本**：IEEE 1609-2020

**参考链接**：
[IEEE官网](https://standards.ieee.org/)

**标准文档**：

- IEEE 1609.0-2019 - WAVE架构概述
- IEEE 1609.2-2016 - 安全服务
- IEEE 1609.3-2020 - 网络服务
- IEEE 1609.4-2016 - 多信道操作

---

### 3.2 IEEE 802.11p标准

**标准编号**：IEEE 802.11p

**标准名称**：Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications Amendment 6: Wireless Access in Vehicular Environments

**核心内容**：

- **物理层规范**：5.9 GHz频段物理层规范
- **MAC层规范**：车载环境MAC层规范
- **快速关联**：快速关联和认证机制

**Schema映射**：

| IEEE 802.11p概念 | Schema映射 |
|-----------------|-----------|
| PHY Layer | Physical_Layer_Schema |
| MAC Layer | MAC_Layer_Schema |
| Fast Association | Association_Schema |

**Schema支持**：完整支持

**最新版本**：IEEE 802.11p-2010（已并入IEEE 802.11-2020）

---

## 4. ETSI标准

### 4.1 ETSI EN 302 637标准

**标准编号**：ETSI EN 302 637

**标准名称**：Intelligent Transport Systems (ITS); Vehicular Communications; Basic Set of Applications

**核心内容**：

- **ETSI EN 302 637-2**：基本安全消息（CAM - Cooperative Awareness Message）
- **ETSI EN 302 637-3**：分散式环境通知消息（DENM - Decentralized Environmental Notification Message）
- **消息格式定义**：CAM/DENM消息格式和编码规则

**Schema映射**：

| ETSI标准概念 | Schema映射 |
|-------------|-----------|
| CAM Message | CAM_Message_Schema |
| DENM Message | DENM_Message_Schema |
| Message Format | Message_Format_Schema |

**Schema支持**：完整支持

**最新版本**：ETSI EN 302 637-2 V1.4.1 (2019), ETSI EN 302 637-3 V1.3.1 (2019)

**参考链接**：
[ETSI官网](https://www.etsi.org/)

---

### 4.2 ETSI TS 102 894标准

**标准编号**：ETSI TS 102 894

**标准名称**：Intelligent Transport Systems (ITS); Users and applications requirements

**核心内容**：

- **应用需求**：ITS应用需求定义
- **消息集定义**：CAM/DENM消息集定义
- **数据字典**：ITS数据字典

**Schema映射**：

| ETSI TS 102 894概念 | Schema映射 |
|-------------------|-----------|
| Application Requirements | Application_Requirements_Schema |
| Message Set | Message_Set_Schema |
| Data Dictionary | Data_Dictionary_Schema |

**Schema支持**：完整支持

**最新版本**：ETSI TS 102 894-2 V2.1.1 (2020)

---

## 5. SAE标准

### 5.1 SAE J2735标准

**标准编号**：SAE J2735

**标准名称**：Dedicated Short Range Communications (DSRC) Message Set Dictionary

**核心内容**：

- **DSRC消息集**：专用短程通信消息集字典
- **BSM消息**：基本安全消息（Basic Safety Message）
- **MAP消息**：地图数据消息（Map Data Message）
- **SPAT消息**：交通信号相位和配时消息（Signal Phase and Timing Message）
- **消息编码**：ASN.1编码规则

**Schema映射**：

| SAE J2735概念 | Schema映射 |
|--------------|-----------|
| BSM Message | BSM_Message_Schema |
| MAP Message | MAP_Message_Schema |
| SPAT Message | SPAT_Message_Schema |
| Message Encoding | Message_Encoding_Schema |

**Schema支持**：完整支持

**最新版本**：SAE J2735_202007

**参考链接**：
[SAE官网](https://www.sae.org/)

**标准文档**：

- SAE J2735_202007 - DSRC消息集字典
- SAE J2735_202007_Addendum - 消息集补充

---

### 5.2 SAE J2945标准

**标准编号**：SAE J2945

**标准名称**：Dedicated Short Range Communications (DSRC) Minimum Performance Requirements

**核心内容**：

- **性能要求**：DSRC系统最小性能要求
- **测试方法**：DSRC系统测试方法
- **互操作性**：DSRC系统互操作性要求

**Schema映射**：

| SAE J2945概念 | Schema映射 |
|--------------|-----------|
| Performance Requirements | Performance_Requirements_Schema |
| Test Methods | Test_Methods_Schema |
| Interoperability | Interoperability_Schema |

**Schema支持**：完整支持

**最新版本**：SAE J2945/1_202103

---

## 6. 标准对比矩阵

| 标准 | 组织 | 适用范围 | 核心内容 | Schema覆盖度 |
|------|------|---------|---------|--------------|
| ISO 14813 | ISO | ITS参考架构 | 参考架构、服务定义、数据模型 | ✅ 100% |
| ISO 21217 | ISO | CALM架构 | 多接口支持、IPv6网络层 | ✅ 100% |
| ISO 17465 | ISO | IVI数据结构 | IVI数据字典、数据交换格式 | ⚠️ 80% |
| IEEE 1609 | IEEE | WAVE协议栈 | 安全服务、网络服务、多信道操作 | ✅ 100% |
| IEEE 802.11p | IEEE | 物理/MAC层 | 5.9 GHz频段、快速关联 | ✅ 100% |
| ETSI EN 302 637 | ETSI | V2V消息 | CAM/DENM消息格式 | ✅ 100% |
| ETSI TS 102 894 | ETSI | ITS应用需求 | 消息集定义、数据字典 | ✅ 100% |
| SAE J2735 | SAE | DSRC消息集 | BSM/MAP/SPAT消息格式 | ✅ 100% |
| SAE J2945 | SAE | DSRC性能 | 性能要求、测试方法 | ⚠️ 80% |

---

## 7. 标准实施建议

### 7.1 实施优先级

1. **P0（必须）**：ISO 14813（ITS参考架构）
2. **P0（必须）**：SAE J2735（DSRC消息集）
3. **P1（重要）**：IEEE 1609（WAVE协议栈）
4. **P1（重要）**：ETSI EN 302 637（CAM/DENM消息）
5. **P2（可选）**：ISO 21217（CALM架构）
6. **P2（可选）**：ISO 17465（IVI数据结构）

### 7.2 实施步骤

1. **阶段1**：实现ISO 14813参考架构和SAE J2735消息集
2. **阶段2**：实现IEEE 1609 WAVE协议栈
3. **阶段3**：实现ETSI EN 302 637 CAM/DENM消息
4. **阶段4**：实现ISO 21217 CALM架构
5. **阶段5**：集成ISO 17465 IVI数据结构

---

## 8. 标准发展趋势

### 8.1 2024-2025年趋势

**智能交通系统标准发展趋势**：

1. **C-V2X技术成熟**
   - 5G-V2X标准完善
   - 蜂窝网络与DSRC融合
   - 车路协同应用增加

2. **SAE J2735持续演进**
   - 消息集扩展
   - 新应用场景支持
   - 性能优化

3. **IEEE 1609标准更新**
   - 安全增强
   - 性能提升
   - 新功能支持

### 8.2 2025-2026年展望

**未来发展方向**：

1. **自动驾驶标准化**
   - 自动驾驶通信标准
   - 车辆协同标准
   - 安全标准完善

2. **智能交通云平台**
   - 云端交通管理
   - 大数据分析
   - AI辅助决策

3. **边缘计算应用**
   - 边缘交通管理
   - 低延迟响应
   - 分布式处理

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21
