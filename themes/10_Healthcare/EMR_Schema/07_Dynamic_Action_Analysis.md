# 电子病历动态行为分析视图

**版本**: v1.0
**创建日期**: 2026-02-15
**标准**: HL7 FHIR R5, ISO/TS 22220:2011, GB/T 31992-2015

---

## 📑 目录

- [电子病历动态行为分析视图](#电子病历动态行为分析视图)
  - [📑 目录](#-目录)
  - [1. 状态机形式化](#1-状态机形式化)
    - [1.1 病历文档状态机](#11-病历文档状态机)
    - [1.2 医嘱状态机](#12-医嘱状态机)
    - [1.3 签名状态机](#13-签名状态机)
  - [2. 时序图形式化](#2-时序图形式化)
    - [2.1 病历书写流程](#21-病历书写流程)
    - [2.2 医嘱下达与执行流程](#22-医嘱下达与执行流程)
    - [2.3 病历归档流程](#23-病历归档流程)
  - [3. 数据流分析](#3-数据流分析)
    - [3.1 病历数据在医生/护士/检验/药房间的流动](#31-病历数据在医生护士检验药房间的流动)
    - [3.2 数据流形式化定义](#32-数据流形式化定义)
  - [4. 实时性分析](#4-实时性分析)
    - [4.1 病历保存响应时间](#41-病历保存响应时间)
    - [4.2 医嘱执行时效](#42-医嘱执行时效)
  - [5. 异常处理](#5-异常处理)
    - [5.1 病历修改追溯](#51-病历修改追溯)
    - [5.2 医嘱撤销](#52-医嘱撤销)
    - [5.3 病历锁定冲突](#53-病历锁定冲突)

---

## 1. 状态机形式化

### 1.1 病历文档状态机

**病历文档生命周期状态转换**

```mermaid
stateDiagram-v2
    [*] --> 草稿: 创建病历
    草稿 --> 草稿: 编辑内容
    草稿 --> 待签名: 完成书写
    待签名 --> 已签名: 医生签名
    已签名 --> 已审核: 上级审核
    已审核 --> 已归档: 归档操作
    已签名 --> 待修改: 申请修改
    已审核 --> 待修改: 申请修改
    待修改 --> 草稿: 批准修改
    待修改 --> 已签名: 拒绝修改
    已归档 --> [*]: 销毁(超期)
    草稿 --> 已作废: 作废
    待签名 --> 已作废: 作废

    已归档: 已归档(只读)
    已作废: 已作废(不可恢复)
```

**状态转换形式化定义**

```text
病历文档状态机 M = (S, Σ, δ, s₀, F)

状态集 S = {
    DRAFT,          -- 草稿
    PENDING_SIGN,   -- 待签名
    SIGNED,         -- 已签名
    REVIEWED,       -- 已审核
    ARCHIVED,       -- 已归档
    PENDING_MOD,    -- 待修改
    VOID            -- 已作废
}

输入符号 Σ = {
    create,         -- 创建
    edit,           -- 编辑
    complete,       -- 完成
    sign,           -- 签名
    review,         -- 审核
    archive,        -- 归档
    request_mod,    -- 申请修改
    approve_mod,    -- 批准修改
    reject_mod,     -- 拒绝修改
    void            -- 作废
}

转移函数 δ:
    δ(DRAFT, edit) = DRAFT
    δ(DRAFT, complete) = PENDING_SIGN
    δ(PENDING_SIGN, sign) = SIGNED
    δ(SIGNED, review) = REVIEWED
    δ(REVIEWED, archive) = ARCHIVED
    δ(SIGNED, request_mod) = PENDING_MOD
    δ(REVIEWED, request_mod) = PENDING_MOD
    δ(PENDING_MOD, approve_mod) = DRAFT
    δ(PENDING_MOD, reject_mod) = SIGNED
    δ(DRAFT, void) = VOID
    δ(PENDING_SIGN, void) = VOID

初始状态 s₀ = DRAFT
终态集 F = {ARCHIVED, VOID}
```

### 1.2 医嘱状态机

**医嘱生命周期状态转换**

```mermaid
stateDiagram-v2
    [*] --> 草稿: 开立医嘱
    草稿 --> 待审核: 提交审核
    待审核 --> 已审核: 护士审核
    待审核 --> 已拒绝: 审核不通过
    已审核 --> 执行中: 开始执行
    执行中 --> 已完成: 执行完毕
    执行中 --> 已停止: 医生停止
    已审核 --> 已停止: 医生停止
    已拒绝 --> 草稿: 修改重提
    已停止 --> 已撤销: 撤销确认
    已完成 --> [*]: 归档
    已撤销 --> [*]: 归档

    执行中: 执行中(可部分执行)
    已停止: 已停止(未执行完)
```

**医嘱状态形式化定义**

```text
医嘱状态机 O = (S_order, Σ_order, δ_order, o₀, F_order)

状态集 S_order = {
    ORDER_DRAFT,        -- 草稿
    ORDER_PENDING,      -- 待审核
    ORDER_VERIFIED,     -- 已审核
    ORDER_REJECTED,     -- 已拒绝
    ORDER_ACTIVE,       -- 执行中
    ORDER_COMPLETED,    -- 已完成
    ORDER_STOPPED,      -- 已停止
    ORDER_CANCELLED     -- 已撤销
}

状态转换规则:
    ORDER_DRAFT --submit--> ORDER_PENDING
    ORDER_PENDING --verify--> ORDER_VERIFIED
    ORDER_PENDING --reject--> ORDER_REJECTED
    ORDER_VERIFIED --activate--> ORDER_ACTIVE
    ORDER_ACTIVE --complete--> ORDER_COMPLETED
    ORDER_ACTIVE --stop--> ORDER_STOPPED
    ORDER_VERIFIED --stop--> ORDER_STOPPED
    ORDER_REJECTED --revise--> ORDER_DRAFT
    ORDER_STOPPED --cancel--> ORDER_CANCELLED

状态不变式:
    ∀o ∈ Order:
        o.status = ORDER_COMPLETED → |o.execution_records| > 0
        o.status = ORDER_ACTIVE → o.start_time ≠ ⊥
        o.status = ORDER_VERIFIED → o.verified_by ≠ ⊥
```

### 1.3 签名状态机

**电子签名状态转换**

```mermaid
stateDiagram-v2
    [*] --> 未签名: 文档创建
    未签名 --> 待验证: 提交签名
    待验证 --> 已签名: 验证通过
    待验证 --> 验证失败: 验证失败
    验证失败 --> 待验证: 重新提交
    已签名 --> 已盖章: CA数字盖章
    已盖章 --> 已验章: 验章通过
    已签名 --> 签名失效: 证书过期
    已盖章 --> 签名失效: 证书过期
    签名失效 --> 待重新签名: 申请重签
    待重新签名 --> 待验证: 重新提交
    已验章 --> [*]: 永久保存
```

**签名状态形式化定义**

```text
签名状态机 Sig = (S_sig, Σ_sig, δ_sig, sig₀, F_sig)

状态集 S_sig = {
    UNSIGNED,           -- 未签名
    PENDING_VERIFY,     -- 待验证
    SIGNED,             -- 已签名
    VERIFY_FAILED,      -- 验证失败
    STAMPED,            -- 已盖章
    VERIFIED,           -- 已验章
    EXPIRED,            -- 签名失效
    PENDING_RESIGN      -- 待重新签名
}

签名规则约束:
    1. 签名者身份验证:
       ∀sig ∈ Signature:
           sig.status = SIGNED → authenticate(sig.signer_id) = true

    2. 时间戳约束:
       ∀sig ∈ Signature:
           sig.status = SIGNED → sig.timestamp ≤ current_time()

    3. 证书有效性:
       ∀sig ∈ Signature:
           sig.status ∈ {SIGNED, STAMPED, VERIFIED} →
               check_certificate(sig.certificate_id) = valid

    4. 签名与文档绑定:
       ∀doc ∈ Document, ∀sig ∈ doc.signatures:
           verify_binding(sig, doc.content_hash) = true
```

---

## 2. 时序图形式化

### 2.1 病历书写流程

**标准病历书写时序**

```mermaid
sequenceDiagram
    autonumber
    actor D as 主治医生
    participant S as 病历系统
    participant T as 模板引擎
    participant DB as 病历数据库
    participant A as 审核系统

    D->>S: 创建新病历
    S->>T: 请求病历模板
    T-->>S: 返回模板结构
    S-->>D: 展示病历模板

    loop 病历内容编辑
        D->>S: 输入病历内容
        S->>S: 实时校验(完整性/规范性)
        S->>DB: 自动保存草稿
        DB-->>S: 保存确认
    end

    D->>S: 提交病历
    S->>S: 完整性检查
    alt 检查通过
        S->>DB: 保存正式病历
        DB-->>S: 保存成功
        S-->>D: 提示提交成功
        S->>A: 触发审核流程
    else 检查不通过
        S-->>D: 返回错误信息
    end

    A->>S: 获取待审核病历
    S-->>A: 返回病历内容
    A->>A: 病历质量评估
    alt 审核通过
        A->>DB: 更新审核状态
        A-->>S: 审核通过通知
        S-->>D: 审核通过
    else 审核不通过
        A-->>D: 返回修改意见
        D->>S: 修改病历
    end
```

**病历书写形式化时序**

```text
病历书写流程 =
    CreateRecord(patient_id) →
    LoadTemplate(record_type) →
    repeat
        EditSection(section_id, content) →
        AutoSave(draft_data) →
        ValidateContent(content)
    until SubmitRecord() →
    FinalValidate() →
    if valid then
        SaveToDatabase(record_data) →
        TriggerReview()
    else
        ReturnError(errors)
    end →
    ReviewProcess()
```

### 2.2 医嘱下达与执行流程

**医嘱全生命周期时序**

```mermaid
sequenceDiagram
    autonumber
    actor Doc as 医生
    participant OS as 医嘱系统
    participant CDSS as 临床决策支持
    participant Nurs as 护士工作站
    participant Pharm as 药房系统
    participant Lab as 检验系统
    participant Exec as 执行记录

    Doc->>OS: 开立医嘱
    OS->>CDSS: 检查药物相互作用
    CDSS-->>OS: 返回警示信息
    alt 存在严重警示
        OS-->>Doc: 展示警示(需确认)
        Doc->>OS: 确认/修改医嘱
    end
    OS->>OS: 生成医嘱编号
    OS-->>Doc: 医嘱开立成功

    OS->>Nurs: 推送待审核医嘱
    Nurs->>Nurs: 护士审核医嘱
    alt 审核通过
        Nurs->>OS: 确认审核
        OS->>OS: 医嘱状态→已审核
    else 审核不通过
        Nurs->>OS: 退回医嘱
        OS-->>Doc: 通知修改
    end

    par 药品医嘱
        OS->>Pharm: 发送配药请求
        Pharm->>Pharm: 审核处方
        Pharm->>Pharm: 药品调配
        Pharm-->>Nurs: 药品送达通知
    and 检验医嘱
        OS->>Lab: 发送检验申请
        Lab->>Lab: 采集样本
        Lab->>Lab: 执行检验
        Lab-->>OS: 返回检验结果
    end

    Nurs->>Exec: 记录执行
    Exec->>OS: 更新执行状态
    OS->>OS: 检查医嘱完成度
    alt 全部执行完成
        OS->>OS: 医嘱状态→已完成
    else 部分执行
        OS->>OS: 保持执行中状态
    end
    OS-->>Doc: 医嘱执行反馈
```

**医嘱执行形式化时序**

```text
医嘱执行流程 =
    CreateOrder(patient_id, order_items) →
    CheckContraindications(order_items) →
    if has_severe_warning then
        RequireConfirmation(doctor)
    end →
    GenerateOrderId() →
    SubmitForVerification() →
    NurseVerify(order_id) →
    if verified then
        parallel
            ProcessMedicationOrder() → Dispense() → Deliver()
            ProcessLabOrder() → CollectSample() → ExecuteTest() → ReturnResult()
            ProcessNursingOrder() → ScheduleExecution() → Execute()
        end →
        RecordExecution(execution_data) →
        UpdateOrderStatus() →
        if all_items_completed then
            SetStatus(COMPLETED)
        else
            SetStatus(ACTIVE)
        end
    else
        ReturnToDoctor(reason)
    end
```

### 2.3 病历归档流程

**病历归档时序**

```mermaid
sequenceDiagram
    autonumber
    actor D as 医生
    participant EMR as 病历系统
    participant QCS as 质控系统
    participant Archive as 归档服务
    participant DB as 生产库
    participant ArchiveDB as 归档库
    participant Backup as 备份系统

    D->>EMR: 患者出院/就诊结束
    EMR->>QCS: 触发病历质控
    QCS->>QCS: 完整性检查
    QCS->>QCS: 时效性检查
    QCS->>QCS: 规范性评分

    alt 质控通过
        QCS-->>EMR: 质控合格
        EMR->>D: 可归档通知
        D->>EMR: 提交归档申请
    else 质控不通过
        QCS-->>EMR: 返回问题列表
        EMR-->>D: 要求完善病历
        D->>EMR: 修改后重新提交
        EMR->>QCS: 重新质控
    end

    EMR->>Archive: 启动归档流程
    Archive->>DB: 提取完整病历数据
    DB-->>Archive: 返回病历数据
    Archive->>Archive: 生成归档包
    Archive->>Archive: 计算哈希值
    Archive->>Archive: 数字签名

    par 归档存储
        Archive->>ArchiveDB: 写入归档库
        ArchiveDB-->>Archive: 存储确认
    and 备份存储
        Archive->>Backup: 发送备份
        Backup-->>Archive: 备份确认
    end

    Archive->>DB: 标记生产库归档状态
    Archive-->>EMR: 归档完成
    EMR-->>D: 归档成功通知
```

---

## 3. 数据流分析

### 3.1 病历数据在医生/护士/检验/药房间的流动

**跨部门病历数据流图**

```mermaid
flowchart TB
    subgraph 医生工作站["🩺 医生工作站"]
        DOC1[病历书写]
        DOC2[医嘱开立]
        DOC3[诊断录入]
        DOC4[病历审核]
    end

    subgraph 护士工作站["👩‍⚕️ 护士工作站"]
        NUR1[医嘱审核]
        NUR2[护理记录]
        NUR3[医嘱执行]
        NUR4[体征录入]
    end

    subgraph 检验科室["🔬 检验科室"]
        LAB1[检验申请接收]
        LAB2[样本采集]
        LAB3[检验执行]
        LAB4[结果发布]
    end

    subgraph 药房部门["💊 药房部门"]
        PHA1[处方审核]
        PHA2[药品调配]
        PHA3[药品发放]
    end

    subgraph 数据中心["🗄️ 病历数据中心"]
        EMR[(病历主库)]
        AUDIT[审计日志]
    end

    %% 医生到数据中心
    DOC1 -->|病历数据| EMR
    DOC2 -->|医嘱数据| EMR
    DOC3 -->|诊断数据| EMR

    %% 医生到护士
    DOC2 -->|医嘱通知| NUR1

    %% 医生到检验
    DOC2 -->|检验申请| LAB1

    %% 医生到药房
    DOC2 -->|处方信息| PHA1

    %% 护士到数据中心
    NUR2 -->|护理记录| EMR
    NUR3 -->|执行记录| EMR
    NUR4 -->|体征数据| EMR

    %% 护士到药房
    NUR3 -->|领药确认| PHA3

    %% 检验到数据中心
    LAB4 -->|检验结果| EMR

    %% 检验到医生
    LAB4 -->|结果通知| DOC1

    %% 药房到护士
    PHA3 -->|药品发放| NUR3

    %% 审计流
    DOC1 -.->|操作日志| AUDIT
    NUR3 -.->|操作日志| AUDIT
    LAB4 -.->|操作日志| AUDIT
    PHA2 -.->|操作日志| AUDIT
```

### 3.2 数据流形式化定义

**数据流动形式化模型**

```text
数据流系统 DFS = (Actors, DataTypes, Flows, Constraints)

参与者集 Actors = {
    DOCTOR,         -- 医生
    NURSE,          -- 护士
    LAB_TECH,       -- 检验技师
    PHARMACIST,     -- 药师
    EMR_SYSTEM      -- 病历系统
}

数据类型集 DataTypes = {
    MedicalRecord,      -- 病历数据
    MedicalOrder,       -- 医嘱数据
    Diagnosis,          -- 诊断数据
    LabResult,          -- 检验结果
    Prescription,       -- 处方数据
    NursingRecord,      -- 护理记录
    VitalSigns,         -- 生命体征
    ExecutionRecord     -- 执行记录
}

数据流 Flows ⊆ Actors × DataTypes × Actors

核心数据流:
    (DOCTOR, MedicalOrder, NURSE)           -- 医嘱下达
    (DOCTOR, MedicalOrder, LAB_TECH)        -- 检验申请
    (DOCTOR, MedicalOrder, PHARMACIST)      -- 药品处方
    (NURSE, ExecutionRecord, EMR_SYSTEM)    -- 执行记录
    (NURSE, NursingRecord, EMR_SYSTEM)      -- 护理记录
    (LAB_TECH, LabResult, EMR_SYSTEM)       -- 检验结果
    (LAB_TECH, LabResult, DOCTOR)           -- 结果反馈
    (PHARMACIST, Prescription, NURSE)       -- 药品发放
    (EMR_SYSTEM, MedicalRecord, *)          -- 病历查询

数据流约束 Constraints:
    1. 医嘱必须经护士审核后方可执行:
       ∀o ∈ MedicalOrder:
           flow(o, DOCTOR, NURSE) →
           ∃v ∈ Verification: v.order_id = o.id ∧ v.verified = true

    2. 检验结果必须关联申请单:
       ∀r ∈ LabResult:
           flow(r, LAB_TECH, EMR_SYSTEM) →
           ∃a ∈ LabApplication: r.application_id = a.id

    3. 执行记录必须关联医嘱:
       ∀e ∈ ExecutionRecord:
           flow(e, NURSE, EMR_SYSTEM) →
           ∃o ∈ MedicalOrder: e.order_id = o.id

    4. 数据完整性约束:
       ∀d ∈ DataTypes, ∀f ∈ flow(d, source, target):
           d.checksum = calculate_checksum(d.payload)
```

---

## 4. 实时性分析

### 4.1 病历保存响应时间

**响应时间要求与优化**

```mermaid
flowchart LR
    subgraph 客户端["客户端"]
        UI[用户界面]
    end

    subgraph 应用层["应用层"]
        API[API网关]
        Cache[(Redis缓存)]
        VAL[数据校验]
    end

    subgraph 数据层["数据层"]
        Master[(主库)]
        Slave[(从库)]
        Queue[消息队列]
    end

    UI -->|<50ms| API
    API -->|<10ms| Cache
    API -->|<30ms| VAL
    VAL -->|<100ms| Master
    Master -->|异步| Queue
    Queue -->|异步| Slave
```

**响应时间形式化定义**

```text
病历保存响应时间模型:

T_total = T_network + T_validate + T_cache + T_database + T_commit

其中:
    T_network ≤ 50ms      -- 网络传输延迟
    T_validate ≤ 30ms     -- 数据校验时间
    T_cache ≤ 10ms        -- 缓存操作时间
    T_database ≤ 100ms    -- 数据库写入时间
    T_commit ≤ 20ms       -- 事务提交时间

总体要求: T_total ≤ 200ms

不同操作类型的响应时间要求:

┌──────────────────┬─────────────┬─────────────┐
│ 操作类型          │ 目标响应时间  │ 最大容忍时间 │
├──────────────────┼─────────────┼─────────────┤
│ 病历自动保存      │ ≤ 100ms     │ ≤ 500ms     │
│ 病历提交保存      │ ≤ 200ms     │ ≤ 1000ms    │
│ 病历查询加载      │ ≤ 300ms     │ ≤ 1500ms    │
│ 病历打印导出      │ ≤ 500ms     │ ≤ 2000ms    │
│ 批量病历导出      │ ≤ 2000ms    │ ≤ 10000ms   │
└──────────────────┴─────────────┴─────────────┘

实时性保证策略:
    1. 自动保存采用异步写入:
       auto_save(record) = async_write_to_cache(record) →
                          background_sync_to_database()

    2. 关键操作同步写入:
       critical_save(record) = sync_write_to_database(record) →
                              confirm_commit()

    3. 读操作优先从缓存:
       read_record(id) = cache.get(id) ?? database.query(id) → cache.put(id)
```

### 4.2 医嘱执行时效

**医嘱执行时效模型**

```mermaid
gantt
    title 医嘱执行时效要求
    dateFormat HH:mm
    axisFormat %H:%M

    section 紧急医嘱(STAT)
    医嘱开立      :a1, 00:00, 5m
    护士审核      :a2, after a1, 5m
    开始执行      :a3, after a2, 5m
    完成执行      :a4, after a3, 15m

    section 紧急医嘱(URGENT)
    医嘱开立      :b1, 00:00, 15m
    护士审核      :b2, after b1, 15m
    开始执行      :b3, after b2, 30m
    完成执行      :b4, after b3, 60m

    section 常规医嘱(ROUTINE)
    医嘱开立      :c1, 00:00, 30m
    护士审核      :c2, after c1, 30m
    开始执行      :c3, after c2, 120m
    完成执行      :c4, after c3, 240m
```

**医嘱执行时效形式化定义**

```text
医嘱执行时效模型:

医嘱优先级 P = {STAT, URGENT, TIMED, ROUTINE, PRN}

时效约束函数:
    T_verify: P → TimeLimit     -- 审核时限
    T_start: P → TimeLimit      -- 开始执行时限
    T_complete: P → TimeLimit   -- 完成时限

具体时效要求:
    T_verify(STAT) = 5 minutes
    T_verify(URGENT) = 15 minutes
    T_verify(TIMED) = 30 minutes
    T_verify(ROUTINE) = 60 minutes
    T_verify(PRN) = 30 minutes

    T_start(STAT) = 15 minutes
    T_start(URGENT) = 60 minutes
    T_start(TIMED) = timed_point - 30 minutes
    T_start(ROUTINE) = 240 minutes
    T_start(PRN) = 60 minutes

时效监控规则:
    ∀o ∈ MedicalOrder:
        let elapsed = current_time() - o.order_time
        in
        if o.priority = STAT ∧ elapsed > T_verify(STAT) then
            trigger_alert("STAT医嘱未及时审核", o)
        else if o.priority = URGENT ∧ elapsed > T_verify(URGENT) then
            trigger_alert("紧急医嘱未及时审核", o)
        else if o.status = VERIFIED ∧
                (current_time() - o.verify_time) > T_start(o.priority) then
            trigger_alert("医嘱未及时执行", o)

时效性指标:
    审核及时率 = |{o | o.verify_time - o.order_time ≤ T_verify(o.priority)}| / |{o}|
    执行及时率 = |{o | o.start_time - o.verify_time ≤ T_start(o.priority)}| / |{o}|

    目标: 审核及时率 ≥ 98%, 执行及时率 ≥ 95%
```

---

## 5. 异常处理

### 5.1 病历修改追溯

**病历修改追溯机制**

```mermaid
sequenceDiagram
    autonumber
    actor D as 医生
    participant EMR as 病历系统
    participant AUD as 审计系统
    participant DB as 数据库
    participant Archive as 归档存储

    D->>EMR: 申请修改已归档病历
    EMR->>EMR: 检查修改权限
    alt 有权限
        EMR->>AUD: 记录修改申请
        AUD-->>EMR: 申请记录成功
        EMR->>DB: 创建病历副本
        DB-->>EMR: 返回副本ID

        D->>EMR: 提交修改内容
        EMR->>EMR: 差异对比
        EMR->>AUD: 记录修改详情
        Note over AUD: 记录:修改人/时间/<br/>原内容/新内容/原因

        EMR->>DB: 保存修改后病历
        DB->>DB: 原病历标记历史版本
        DB-->>EMR: 保存成功

        EMR->>Archive: 归档修改记录
        EMR-->>D: 修改完成通知
    else 无权限
        EMR-->>D: 拒绝修改申请
    end

    %% 追溯查询
    D->>EMR: 查询病历修改历史
    EMR->>AUD: 获取审计日志
    AUD-->>EMR: 返回修改记录
    EMR-->>D: 展示修改历史
```

**修改追溯形式化定义**

```text
病历修改追溯系统:

修改记录结构:
    ModificationRecord = {
        record_id: RecordId,
        version: Integer,
        modifier_id: ProviderId,
        modify_time: DateTime,
        original_content: ContentHash,
        new_content: ContentHash,
        diff_content: Diff,
        modify_reason: String,
        approval_id: ApprovalId?
    }

追溯查询操作:
    get_modification_history(record_id) → List<ModificationRecord>
    get_version_at_time(record_id, timestamp) → RecordVersion
    compare_versions(record_id, version1, version2) → Diff
    get_modifier_stats(provider_id, time_range) → Statistics

不可篡改保证:
    ∀m ∈ ModificationRecord:
        hash(m) = stored_hash(m)  -- 哈希校验
        ∧ m stored_in append_only_storage  -- 仅追加存储

审计规则:
    1. 所有修改必须记录理由:
       ∀m ∈ ModificationRecord: length(m.modify_reason) > 10

    2. 已归档病历修改需审批:
       ∀m: m.record_status = ARCHIVED → m.approval_id ≠ ⊥

    3. 修改历史永久保留:
       ∀m: retention_period(m) = forever

    4. 修改通知相关方:
       notify(party) where party ∈ stakeholders(m.record_id)
```

### 5.2 医嘱撤销

**医嘱撤销流程**

```mermaid
stateDiagram-v2
    [*] --> 医嘱生效: 正常流程
    医嘱生效 --> 撤销申请: 医生发起撤销
    撤销申请 --> 撤销审核: 提交审核

    撤销审核 --> 已撤销: 审核通过
    撤销审核 --> 撤销拒绝: 审核不通过
    撤销拒绝 --> 医嘱生效: 继续执行

    已撤销 --> 撤销归档: 记录归档
    撤销归档 --> [*]: 流程结束

    note right of 撤销申请
        撤销原因必填
        已执行部分需特别处理
    end note

    note right of 撤销审核
        护士确认未执行部分
        药房/检验已处理项目
    end note
```

**医嘱撤销形式化定义**

```text
医嘱撤销系统:

撤销条件:
    can_cancel(order) =
        order.status ∈ {PENDING, VERIFIED, ACTIVE}
        ∧ has_permission(doctor, order, CANCEL)
        ∧ (order.status = ACTIVE → partial_executed(order) = false)

撤销类型:
    CANCEL_TYPE = {
        FULL_CANCEL,        -- 完全撤销(未执行)
        PARTIAL_CANCEL,     -- 部分撤销(部分执行)
        POST_EXEC_CANCEL    -- 执行后撤销(需特殊审批)
    }

撤销流程:
    cancel_order(order_id, reason, cancel_type) =
        let order = get_order(order_id)
        in
        if not can_cancel(order) then
            return Error("不符合撤销条件")
        else
            create_cancel_request(order_id, reason, cancel_type) →
            route_for_approval(cancel_type) →
            if approve(cancel_request) then
                execute_cancel(order_id, cancel_type) →
                notify_stakeholders(order_id) →
                archive_cancel_record(order_id, cancel_type)
            else
                return Error("撤销申请被拒绝")
            end
        end

撤销影响范围:
    ┌─────────────────┬───────────────┬───────────────┬───────────────┐
    │ 医嘱状态         │ 药房影响       │ 检验影响       │ 护理影响       │
    ├─────────────────┼───────────────┼───────────────┼───────────────┤
    │ PENDING         │ 无            │ 无            │ 无            │
    │ VERIFIED        │ 取消配药      │ 取消采集      │ 取消执行计划   │
    │ ACTIVE(未执行)   │ 退回药品      │ 取消申请      │ 移除执行单     │
    │ ACTIVE(部分执行) │ 部分退回      │ 部分取消      │ 停止后续执行   │
    │ COMPLETED       │ 不可撤销      │ 不可撤销      │ 不可撤销      │
    └─────────────────┴───────────────┴───────────────┴───────────────┘

撤销记录:
    CancelRecord = {
        cancel_id: CancelId,
        order_id: OrderId,
        requester: ProviderId,
        request_time: DateTime,
        cancel_reason: String,
        cancel_type: CANCEL_TYPE,
        approval_id: ApprovalId,
        affected_items: List<OrderItem>,
        notification_status: NotificationStatus
    }
```

### 5.3 病历锁定冲突

**病历锁定冲突处理机制**

```mermaid
sequenceDiagram
    autonumber
    actor D1 as 医生A
    actor D2 as 医生B
    participant Lock as 锁定服务
    participant EMR as 病历系统
    participant Notify as 通知服务

    D1->>Lock: 请求锁定病历R
    Lock->>Lock: 检查锁定状态
    alt 病历未锁定
        Lock->>Lock: 创建锁定记录<br/>持有者=医生A
        Lock-->>D1: 锁定成功
        D1->>EMR: 编辑病历R

        D2->>Lock: 请求锁定病历R
        Lock->>Lock: 检查锁定状态
        Lock-->>D2: 病历已被医生A锁定

        D2->>EMR: 请求查看病历R
        EMR-->>D2: 返回只读版本

        alt 医生B需要编辑
            D2->>Lock: 申请强制解锁
            Lock->>Notify: 通知医生A
            Notify-->>D1: 解锁申请通知

            alt 医生A同意解锁
                D1->>Lock: 释放锁定
                Lock->>Lock: 保存医生A修改
                Lock-->>D1: 保存成功
                Lock->>Lock: 将锁定转移给医生B
                Lock-->>D2: 锁定获得
            else 医生A拒绝或超时
                Lock-->>D2: 解锁失败
                D2->>EMR: 继续只读查看
            end
        end

        D1->>Lock: 主动释放锁定
        Lock->>EMR: 提交最终版本
        Lock->>Lock: 清除锁定记录
    else 病历已锁定
        Lock-->>D1: 锁定失败，返回持有者信息
    end
```

**锁定冲突形式化定义**

```text
病历锁定系统:

锁类型:
    LOCK_TYPE = {READ_LOCK, WRITE_LOCK, EXCLUSIVE_LOCK}

锁状态:
    LockState = {
        UNLOCKED,           -- 未锁定
        LOCKED_READ,        -- 读锁定(多用户)
        LOCKED_WRITE,       -- 写锁定(单用户)
        LOCKED_EXCLUSIVE    -- 独占锁定(管理员)
    }

锁定记录:
    LockRecord = {
        record_id: RecordId,
        lock_type: LOCK_TYPE,
        holder: ProviderId,
        lock_time: DateTime,
        expire_time: DateTime,
        session_id: SessionId,
        is_recursive: Boolean  -- 是否允许同会话重入
    }

锁定操作:
    acquire_lock(record_id, lock_type, holder) → Result<LockToken, LockError>
    release_lock(lock_token) → Result<(), LockError>
    extend_lock(lock_token, duration) → Result<(), LockError>
    force_unlock(record_id, admin_id, reason) → Result<(), LockError>

锁定兼容性矩阵:
    ┌─────────────────┬───────────┬───────────┬───────────┐
    │ 已有锁 ↓ 请求锁 → │ READ_LOCK │ WRITE_LOCK│ EXCLUSIVE │
    ├─────────────────┼───────────┼───────────┼───────────┤
    │ UNLOCKED        │ ✓         │ ✓         │ ✓         │
    │ READ_LOCK       │ ✓         │ ✗         │ ✗         │
    │ WRITE_LOCK      │ ✗         │ ✗         │ ✗         │
    │ EXCLUSIVE       │ ✗         │ ✗         │ ✗         │
    └─────────────────┴───────────┴───────────┴───────────┘

冲突解决策略:
    1. 等待策略:
       wait_for_lock(record_id, timeout) →
           if lock_released_within(timeout) then
               retry_acquire_lock()
           else
               return TimeoutError

    2. 抢占策略(需审批):
       preempt_lock(record_id, requester) →
           if has_priority(requester, current_holder) then
               notify(current_holder, "锁被抢占")
               release_lock(current_holder)
               grant_lock(requester)
           else
               return PriorityError

    3. 合并策略:
       merge_on_unlock(record_id) →
           when lock_released then
               if has_pending_changes() then
                   show_diff_dialog()
                   let user_resolve_conflicts()
               end

锁超时机制:
    lock_timeout = case lock_type of
        READ_LOCK → 30 minutes
        WRITE_LOCK → 15 minutes
        EXCLUSIVE_LOCK → 60 minutes

    heartbeat_interval = 5 minutes

    if (current_time - last_heartbeat) > heartbeat_interval then
        release_lock_due_to_timeout()
        notify_holder("锁定因超时释放")
```

---

**参考文档**：

- `01_Overview.md` - EMR Schema概述
- `02_Formal_Definition.md` - 形式化定义
- `06_Formal_Grammar_Semantics.md` - 形式语法与语义

**创建时间**：2026-02-15
**最后更新**：2026-02-15
