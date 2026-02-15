# 食品安全Schema实践案例

## 📑 目录

- [食品安全Schema实践案例](#食品安全schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 企业背景](#2-企业背景)
  - [3. 业务痛点](#3-业务痛点)
  - [4. 业务目标](#4-业务目标)
  - [5. 技术挑战](#5-技术挑战)
  - [6. 案例1：食品溯源追踪平台](#6-案例1食品溯源追踪平台)
  - [7. 案例2：智能检测实验室管理](#7-案例2智能检测实验室管理)
  - [8. 案例3：餐饮安全风险监控](#8-案例3餐饮安全风险监控)
  - [9. Python代码实现](#9-python代码实现)
  - [10. 效果评估](#10-效果评估)
  - [11. 案例总结](#11-案例总结)

---

## 1. 案例概述

本文档提供**食品安全Schema的实际应用案例**，涵盖食品溯源、检测实验室管理、餐饮安全监控等领域。通过真实的行业场景，展示如何利用信息技术实现从农田到餐桌的全链条食品安全保障。

**案例类型**：
- 食品溯源追踪平台
- 智能检测实验室管理
- 餐饮安全风险监控

---

## 2. 企业背景

### 2.1 企业概况

**食安科技集团有限公司**（以下简称"食安科技"）成立于2012年，总部位于上海，是国内领先的食品安全解决方案提供商。公司为食品生产企业、检测机构、监管部门提供从原料到成品的全链条食品安全数字化服务。

### 2.2 业务规模

| 指标 | 数值 |
|------|------|
| 年营收 | 6亿元 |
| 服务企业 | 5000+家 |
| 溯源产品数 | 100万+个 |
| 检测实验室接入 | 300+个 |
| 覆盖城市 | 200+个 |

### 2.3 业务领域

食安科技主要提供以下服务：
- **食品溯源系统**：原料-生产-流通-销售全链条追溯
- **检测实验室管理**：LIMS实验室信息管理系统
- **餐饮安全监管**：明厨亮灶、风险预警、智能分析
- **合规咨询服务**：食品法规解读、认证辅导

---

## 3. 业务痛点

### 痛点1：溯源信息不完整

**问题描述**：食品供应链环节多、参与主体复杂，各环节信息孤岛严重，难以形成完整的追溯链条。

**影响范围**：约60%的食品企业只能追溯到直接供应商，无法追溯至源头。

### 痛点2：检测数据管理混乱

**问题描述**：检测实验室数据分散在Excel、纸质记录中，数据查询困难，无法有效支撑质量分析。

**效率损失**：某检测机构数据查询平均耗时2小时，报告生成需要1天。

### 痛点3：餐饮监管人手不足

**问题描述**：基层监管人员有限，难以实现对所有餐饮单位的全覆盖监管，问题发现滞后。

**监管缺口**：某区市场监管局人均监管200+家餐饮单位，实地检查频次不足。

### 痛点4：风险预警能力弱

**问题描述**：食品安全风险发现主要依赖事后抽检，缺乏有效的预测预警机制。

**响应滞后**：从问题发生到发现平均需要7-15天。

### 痛点5：数据真实性存疑

**问题描述**：溯源数据和检测数据存在篡改、造假风险，数据可信度受到质疑。

**信任危机**：消费者对食品标签的信任度不足40%。

---

## 4. 业务目标

### 目标1：实现全链条溯源

建立覆盖从原料种植/养殖、生产加工、物流配送到终端销售的全链条溯源体系，追溯覆盖率100%。

**关键指标**：
- 溯源环节覆盖率：100%
- 溯源查询响应：<3秒
- 数据完整率：>99%

### 目标2：建设数字化检测实验室

实现检测流程数字化、检测数据自动采集、报告自动生成，检测效率提升50%以上。

**关键指标**：
- 无纸化率：100%
- 报告生成时间：<10分钟
- 数据准确率：>99.9%

### 目标3：构建智能监管体系

利用AI视频分析、IoT传感等技术，实现餐饮单位的24小时智能监管。

**关键指标**：
- 视频接入率：100%
- AI识别准确率：>95%
- 违规行为发现时间：<5分钟

### 目标4：建立风险预警模型

基于大数据和机器学习，构建食品安全风险预测预警模型，实现事前预防。

**关键指标**：
- 预警准确率：>90%
- 预警提前量：>7天
- 误报率：<5%

### 目标5：确保数据可信

引入区块链、电子签名等技术，确保溯源数据和检测数据的不可篡改。

**关键指标**：
- 数据上链率：100%
- 数据篡改检测率：100%
- 电子签名覆盖率：100%

---

## 5. 技术挑战

### 挑战1：多源异构数据整合

**问题描述**：食品供应链涉及ERP、WMS、MES等多个系统，数据格式各异，整合难度大。

**技术难点**：
- 数据标准化与清洗
- 实时数据同步机制
- 主数据管理

### 挑战2：一物一码标识体系

**问题描述**：需要为每个食品产品分配唯一标识，并关联生产、流通各环节信息。

**技术难点**：
- 编码体系设计（GS1、国标等）
- 赋码与识读技术
- 码的防复制与防伪

### 挑战3：检测仪器集成

**问题描述**：实验室检测仪器品牌众多，接口标准不一，数据采集困难。

**技术难点**：
- 仪器通信协议适配
- 数据自动采集与解析
- 检测结果自动判定

### 挑战4：视频AI分析

**问题描述**：餐饮场景复杂，需要准确识别未戴口罩、抽烟、鼠患等违规行为。

**技术难点**：
- 复杂环境下的目标检测
- 行为识别与分析
- 实时视频流处理

### 挑战5：区块链性能与成本

**问题描述**：海量溯源数据上链面临性能和成本挑战。

**技术难点**：
- 联盟链架构设计
- 数据分片与压缩
- 链上链下协同

---

## 6. 案例1：食品溯源追踪平台

### 6.1 案例背景

**问题**：构建覆盖全供应链的食品溯源平台，实现"来源可查、去向可追、责任可究"。

**应用场景**：生鲜追溯、乳制品追溯、保健品追溯。

### 6.2 Schema定义

**食品溯源Schema**：

```dsl
platform Food_Traceability {
  platform_name: "食安科技溯源平台"
  
  traceability_stages: [
    Raw_Material,       # 原料
    Processing,         # 生产加工
    Packaging,          # 包装
    Warehousing,        # 仓储
    Distribution,       # 物流配送
    Retail,             # 零售
    Consumer            # 消费
  ]
  
  functions: [
    registerProduct(product: Product_Info): Product_Code,
    recordEvent(product_code: Product_Code, event: Trace_Event): Event_Record,
    queryTraceability(product_code: Product_Code): Trace_Chain,
    verifyAuthenticity(product_code: Product_Code): Verification_Result,
    recallProduct(batch_id: Batch_ID, reason: Recall_Reason): Recall_Notification
  ]
  
  state: {
    products: Map[Product_Code, Product]
    trace_events: Map[Event_ID, Trace_Event]
    supply_chain: Map[Entity_ID, Supply_Chain_Entity]
    blockchain_records: Map[Block_Hash, Block_Data]
  }
  
  events: [
    ProductRegistered(product_code: Product_Code, timestamp: Timestamp),
    EventRecorded(event_id: Event_ID, event_type: String, location: Geo_Point),
    TraceabilityQueried(product_code: Product_Code, consumer: String),
    ProductRecalled(batch_id: Batch_ID, scope: Recall_Scope)
  ]
}
```

---

## 7. 案例2：智能检测实验室管理

### 7.1 案例背景

**问题**：建设数字化检测实验室，实现检测流程自动化、数据管理规范化、报告生成智能化。

**应用场景**：食品理化检测、微生物检测、农兽药残留检测。

### 7.2 Schema定义

**检测实验室Schema**：

```dsl
platform Laboratory_Information_Management {
  platform_name: "食安科技LIMS系统"
  
  test_categories: [
    Physical_Chemical,
    Microbiological,
    Residue_Analysis,
    Allergen_Testing,
    Nutritional_Labeling
  ]
  
  functions: [
    receiveSample(sample: Sample): Sample_ID,
    assignTest(sample_id: Sample_ID, test_plan: Test_Plan): Work_Order,
    recordResult(test_id: Test_ID, result: Test_Result): Result_Record,
    approveReport(report_id: Report_ID, approver: User): Approval_Status,
    generateCertificate(batch_id: Batch_ID): Certificate
  ]
  
  state: {
    samples: Map[Sample_ID, Sample]
    tests: Map[Test_ID, Test]
    results: Map[Result_ID, Test_Result]
    reports: Map[Report_ID, Test_Report]
    instruments: Map[Instrument_ID, Instrument]
  }
  
  events: [
    SampleReceived(sample_id: Sample_ID, client: String),
    TestStarted(test_id: Test_ID, instrument: Instrument_ID),
    ResultRecorded(result_id: Result_ID, value: Float, unit: String),
    ReportApproved(report_id: Report_ID, approver: String, timestamp: Timestamp)
  ]
}
```

---

## 8. 案例3：餐饮安全风险监控

### 8.1 案例背景

**问题**：构建餐饮安全智能监控平台，通过AI视频分析和IoT传感实现实时风险预警。

**应用场景**：明厨亮灶、后厨卫生监测、冷链监控、人员行为分析。

### 8.2 Schema定义

**餐饮安全监控Schema**：

```dsl
platform Food_Safety_Monitoring {
  platform_name: "食安科技餐饮监管平台"
  
  monitoring_types: [
    Video_Surveillance,      # 视频监控
    Temperature_Monitoring,  # 温度监控
    Humidity_Monitoring,     # 湿度监控
    Hygiene_Detection        # 卫生检测
  ]
  
  violation_types: [
    No_Mask,                 # 未佩戴口罩
    No_Hairnet,              # 未戴工作帽
    Smoking,                 # 抽烟
    Pest_Detection,          # 发现害虫
    Improper_Storage         # 存储不当
  ]
  
  functions: [
    connectCamera(restaurant_id: Restaurant_ID, camera: Camera_Config): Connection_ID,
    analyzeVideo(stream: Video_Stream, ai_models: AI_Model[]): Detection_Result,
    monitorTemperature(sensor_id: Sensor_ID, threshold: Temperature_Range): Alert_Condition,
    detectViolation(video_frame: Image): Violation_List,
    generateAlert(violation: Violation, severity: Alert_Level): Alert_Notification
  ]
  
  state: {
    restaurants: Map[Restaurant_ID, Restaurant]
    cameras: Map[Camera_ID, Camera]
    sensors: Map[Sensor_ID, IoT_Sensor]
    violations: Map[Violation_ID, Violation]
    alerts: Map[Alert_ID, Alert]
  }
  
  events: [
    CameraConnected(camera_id: Camera_ID, restaurant: String),
    ViolationDetected(violation_type: String, confidence: Float, image: Image),
    TemperatureAlert(sensor_id: Sensor_ID, current_temp: Float, threshold: Float),
    AlertDispatched(alert_id: Alert_ID, recipient: String, method: Notification_Method)
  ]
}
```

---

## 9. Python代码实现

### 9.1 完整系统实现

```python
"""
食品安全管理平台 - Python实现
包含：溯源追踪、检测管理、风险监控、区块链存证
"""

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Set
from enum import Enum
import logging
from collections import defaultdict
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProductStatus(Enum):
    """产品状态"""
    PRODUCING = "producing"
    IN_TRANSIT = "in_transit"
    IN_STORAGE = "in_storage"
    SOLD = "sold"
    RECALLED = "recalled"


class TestStatus(Enum):
    """检测状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"


class ViolationType(Enum):
    """违规类型"""
    NO_MASK = "no_mask"
    NO_HAIRNET = "no_hairnet"
    SMOKING = "smoking"
    PEST_DETECTED = "pest_detected"
    TEMPERATURE_VIOLATION = "temperature_violation"


@dataclass
class TraceEvent:
    """溯源事件"""
    event_id: str
    product_code: str
    event_type: str  # production, packaging, shipping, receiving, etc.
    timestamp: datetime
    location: str
    operator: str
    details: Dict[str, Any] = field(default_factory=dict)
    document_refs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "product_code": self.product_code,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "operator": self.operator,
            "details": self.details
        }


@dataclass
class Product:
    """产品定义"""
    product_code: str
    name: str
    category: str
    batch_id: str
    manufacturer: str
    production_date: datetime
    expiry_date: datetime
    status: ProductStatus = ProductStatus.PRODUCING
    trace_events: List[TraceEvent] = field(default_factory=list)
    blockchain_hash: Optional[str] = None
    
    def add_event(self, event: TraceEvent):
        """添加溯源事件"""
        self.trace_events.append(event)
        self.trace_events.sort(key=lambda x: x.timestamp)
    
    def get_trace_chain(self) -> List[Dict]:
        """获取完整溯源链"""
        return [event.to_dict() for event in self.trace_events]


@dataclass
class Sample:
    """检测样品"""
    sample_id: str
    sample_code: str
    product_name: str
    batch_id: str
    client: str
    sampling_date: datetime
    sampling_location: str
    quantity: float
    unit: str
    storage_condition: str
    status: str = "received"
    tests: List['Test'] = field(default_factory=list)


@dataclass
class Test:
    """检测项目"""
    test_id: str
    sample_id: str
    test_item: str  # 如：菌落总数、大肠杆菌、农残等
    test_method: str
    standard_limit: Optional[float] = None
    unit: str = ""
    result: Optional[float] = None
    result_status: Optional[str] = None  # pass, fail, pending
    test_date: Optional[datetime] = None
    tester: str = ""
    instrument_id: Optional[str] = None
    status: TestStatus = TestStatus.PENDING
    
    def record_result(self, value: float, tester: str):
        """记录检测结果"""
        self.result = value
        self.tester = tester
        self.test_date = datetime.now()
        self.status = TestStatus.COMPLETED
        
        # 判定结果
        if self.standard_limit is not None:
            self.result_status = "pass" if value <= self.standard_limit else "fail"
        else:
            self.result_status = "completed"


@dataclass
class TestReport:
    """检测报告"""
    report_id: str
    sample_id: str
    report_code: str
    tests: List[Test]
    issue_date: Optional[datetime] = None
    approver: str = ""
    status: str = "draft"
    
    def generate(self):
        """生成报告"""
        # 检查所有检测是否完成
        if all(t.status == TestStatus.COMPLETED for t in self.tests):
            self.issue_date = datetime.now()
            self.status = "issued"
            return True
        return False
    
    def approve(self, approver: str):
        """审批报告"""
        if self.status == "issued":
            self.approver = approver
            self.status = "approved"
            for test in self.tests:
                test.status = TestStatus.APPROVED
            return True
        return False


class BlockchainTraceability:
    """区块链溯源（简化实现）"""
    
    def __init__(self):
        self.chain: List[Dict] = []
        self.pending_transactions: List[Dict] = []
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """创建创世区块"""
        genesis_block = {
            "index": 0,
            "timestamp": time.time(),
            "transactions": [],
            "previous_hash": "0" * 64,
            "hash": self._calculate_hash(0, [], "0" * 64, 0),
            "nonce": 0
        }
        self.chain.append(genesis_block)
    
    def _calculate_hash(self, index: int, transactions: List, 
                       previous_hash: str, nonce: int) -> str:
        """计算区块哈希"""
        block_string = json.dumps({
            "index": index,
            "transactions": transactions,
            "previous_hash": previous_hash,
            "nonce": nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def add_transaction(self, transaction: Dict):
        """添加交易到待处理队列"""
        transaction["timestamp"] = time.time()
        transaction["tx_hash"] = hashlib.sha256(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()
        self.pending_transactions.append(transaction)
    
    def mine_block(self) -> Dict:
        """挖矿创建新区块"""
        if not self.pending_transactions:
            return None
        
        previous_block = self.chain[-1]
        index = len(self.chain)
        previous_hash = previous_block["hash"]
        
        # 工作量证明（简化）
        nonce = 0
        difficulty = 2
        target = "0" * difficulty
        
        while True:
            block_hash = self._calculate_hash(index, self.pending_transactions, 
                                             previous_hash, nonce)
            if block_hash.startswith(target):
                break
            nonce += 1
        
        new_block = {
            "index": index,
            "timestamp": time.time(),
            "transactions": self.pending_transactions.copy(),
            "previous_hash": previous_hash,
            "hash": block_hash,
            "nonce": nonce
        }
        
        self.chain.append(new_block)
        self.pending_transactions = []
        
        return new_block
    
    def verify_chain(self) -> bool:
        """验证区块链完整性"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current["previous_hash"] != previous["hash"]:
                return False
            
            recalculated_hash = self._calculate_hash(
                current["index"],
                current["transactions"],
                current["previous_hash"],
                current["nonce"]
            )
            if current["hash"] != recalculated_hash:
                return False
        
        return True
    
    def get_product_history(self, product_code: str) -> List[Dict]:
        """获取产品历史记录"""
        history = []
        for block in self.chain:
            for tx in block["transactions"]:
                if tx.get("product_code") == product_code:
                    history.append(tx)
        return history


class TraceabilityManager:
    """溯源管理器"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.blockchain = BlockchainTraceability()
    
    def register_product(self, name: str, category: str, batch_id: str,
                        manufacturer: str) -> Product:
        """注册产品"""
        product_code = f"{manufacturer[:3].upper()}{int(time.time())}{uuid.uuid4().hex[:4].upper()}"
        
        product = Product(
            product_code=product_code,
            name=name,
            category=category,
            batch_id=batch_id,
            manufacturer=manufacturer,
            production_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=365)
        )
        
        self.products[product_code] = product
        
        # 添加到区块链
        self.blockchain.add_transaction({
            "type": "product_registration",
            "product_code": product_code,
            "name": name,
            "manufacturer": manufacturer,
            "timestamp": time.time()
        })
        
        logger.info(f"产品 {name} 已注册，溯源码: {product_code}")
        return product
    
    def record_event(self, product_code: str, event_type: str, location: str,
                    operator: str, details: Dict = None) -> TraceEvent:
        """记录溯源事件"""
        if product_code not in self.products:
            raise ValueError(f"产品 {product_code} 不存在")
        
        event = TraceEvent(
            event_id=str(uuid.uuid4()),
            product_code=product_code,
            event_type=event_type,
            timestamp=datetime.now(),
            location=location,
            operator=operator,
            details=details or {}
        )
        
        product = self.products[product_code]
        product.add_event(event)
        
        # 添加到区块链
        self.blockchain.add_transaction({
            "type": "trace_event",
            "product_code": product_code,
            "event_type": event_type,
            "location": location,
            "operator": operator,
            "timestamp": time.time()
        })
        
        # 挖矿确认（简化，实际应用可能批量处理）
        self.blockchain.mine_block()
        
        logger.info(f"产品 {product_code} 事件已记录: {event_type} @ {location}")
        return event
    
    def query_traceability(self, product_code: str) -> Dict:
        """查询产品溯源信息"""
        if product_code not in self.products:
            return {"error": "Product not found"}
        
        product = self.products[product_code]
        blockchain_history = self.blockchain.get_product_history(product_code)
        
        return {
            "product_code": product_code,
            "name": product.name,
            "manufacturer": product.manufacturer,
            "production_date": product.production_date.isoformat(),
            "expiry_date": product.expiry_date.isoformat(),
            "status": product.status.value,
            "trace_chain": product.get_trace_chain(),
            "blockchain_records": len(blockchain_history),
            "verification": self.blockchain.verify_chain()
        }


class LaboratoryManager:
    """实验室管理器"""
    
    def __init__(self):
        self.samples: Dict[str, Sample] = {}
        self.tests: Dict[str, Test] = {}
        self.reports: Dict[str, TestReport] = {}
        self.instruments: Dict[str, Dict] = {}
    
    def receive_sample(self, product_name: str, batch_id: str, client: str,
                      sampling_location: str, quantity: float = 1.0) -> Sample:
        """接收样品"""
        sample_id = f"S{datetime.now().strftime('%Y%m%d')}{len(self.samples)+1:04d}"
        
        sample = Sample(
            sample_id=sample_id,
            sample_code=sample_id,
            product_name=product_name,
            batch_id=batch_id,
            client=client,
            sampling_date=datetime.now(),
            sampling_location=sampling_location,
            quantity=quantity,
            unit="kg",
            storage_condition="冷藏"
        )
        
        self.samples[sample_id] = sample
        logger.info(f"样品 {sample_id} 已接收")
        return sample
    
    def create_test_plan(self, sample_id: str, test_items: List[Dict]) -> List[Test]:
        """创建检测计划"""
        if sample_id not in self.samples:
            raise ValueError(f"样品 {sample_id} 不存在")
        
        tests = []
        for i, item in enumerate(test_items):
            test = Test(
                test_id=f"T{sample_id}{i+1:02d}",
                sample_id=sample_id,
                test_item=item["name"],
                test_method=item["method"],
                standard_limit=item.get("limit"),
                unit=item.get("unit", "")
            )
            tests.append(test)
            self.tests[test.test_id] = test
        
        self.samples[sample_id].tests = tests
        logger.info(f"样品 {sample_id} 检测计划已创建: {len(tests)} 项")
        return tests
    
    def record_test_result(self, test_id: str, value: float, tester: str):
        """记录检测结果"""
        if test_id not in self.tests:
            raise ValueError(f"检测 {test_id} 不存在")
        
        test = self.tests[test_id]
        test.record_result(value, tester)
        
        logger.info(f"检测结果已记录: {test.test_item} = {value} {test.unit}, 判定: {test.result_status}")
    
    def generate_report(self, sample_id: str) -> TestReport:
        """生成检测报告"""
        if sample_id not in self.samples:
            raise ValueError(f"样品 {sample_id} 不存在")
        
        sample = self.samples[sample_id]
        
        report = TestReport(
            report_id=f"R{sample_id}",
            sample_id=sample_id,
            report_code=f"R{sample_id}",
            tests=sample.tests
        )
        
        if report.generate():
            self.reports[report.report_id] = report
            logger.info(f"检测报告 {report.report_id} 已生成")
        else:
            logger.warning("检测未完成，无法生成报告")
        
        return report


class RestaurantMonitor:
    """餐饮监控器"""
    
    def __init__(self):
        self.restaurants: Dict[str, Dict] = {}
        self.violations: List[Dict] = []
        self.alerts: List[Dict] = []
        self.ai_models = {
            "face_detection": True,
            "object_detection": True,
            "behavior_analysis": True
        }
    
    def register_restaurant(self, restaurant_id: str, name: str, address: str,
                           camera_count: int = 1) -> Dict:
        """注册餐饮企业"""
        restaurant = {
            "restaurant_id": restaurant_id,
            "name": name,
            "address": address,
            "camera_count": camera_count,
            "cameras": [],
            "sensors": [],
            "violation_count": 0,
            "risk_level": "low"
        }
        
        self.restaurants[restaurant_id] = restaurant
        logger.info(f"餐饮企业 {name} 已注册")
        return restaurant
    
    def analyze_frame(self, restaurant_id: str, camera_id: str, 
                     frame_data: np.ndarray) -> List[Dict]:
        """分析视频帧（模拟AI检测）"""
        # 模拟检测结果
        detections = []
        
        # 随机模拟违规行为（实际应为真实AI模型）
        violation_types = [
            ViolationType.NO_MASK,
            ViolationType.NO_HAIRNET,
            ViolationType.SMOKING,
            ViolationType.PEST_DETECTED
        ]
        
        if np.random.random() < 0.1:  # 10%概率检测到违规
            violation_type = np.random.choice(violation_types)
            confidence = np.random.uniform(0.7, 0.99)
            
            detection = {
                "violation_id": str(uuid.uuid4()),
                "restaurant_id": restaurant_id,
                "camera_id": camera_id,
                "type": violation_type.value,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "frame_hash": hashlib.sha256(frame_data.tobytes()).hexdigest()[:16]
            }
            
            detections.append(detection)
            self.violations.append(detection)
            
            # 更新餐厅违规计数
            if restaurant_id in self.restaurants:
                self.restaurants[restaurant_id]["violation_count"] += 1
            
            # 生成告警
            self._create_alert(detection)
        
        return detections
    
    def _create_alert(self, violation: Dict):
        """创建告警"""
        alert = {
            "alert_id": str(uuid.uuid4()),
            "violation_id": violation["violation_id"],
            "restaurant_id": violation["restaurant_id"],
            "type": violation["type"],
            "severity": "high" if violation["confidence"] > 0.9 else "medium",
            "timestamp": datetime.now().isoformat(),
            "status": "open",
            "notified": False
        }
        
        self.alerts.append(alert)
        
        if alert["severity"] == "high":
            logger.warning(f"高风险告警: 餐厅 {violation['restaurant_id']} - {violation['type']}")
    
    def check_temperature(self, restaurant_id: str, sensor_id: str,
                         current_temp: float, threshold_range: Tuple[float, float]):
        """检查温度"""
        min_temp, max_temp = threshold_range
        
        if current_temp < min_temp or current_temp > max_temp:
            alert = {
                "alert_id": str(uuid.uuid4()),
                "restaurant_id": restaurant_id,
                "sensor_id": sensor_id,
                "type": "temperature_violation",
                "current_temp": current_temp,
                "threshold": threshold_range,
                "timestamp": datetime.now().isoformat(),
                "status": "open"
            }
            
            self.alerts.append(alert)
            logger.warning(f"温度异常: 餐厅 {restaurant_id} 传感器 {sensor_id}, "
                         f"当前 {current_temp}°C, 正常范围 {min_temp}-{max_temp}°C")
    
    def get_risk_summary(self, restaurant_id: str) -> Dict:
        """获取餐厅风险摘要"""
        if restaurant_id not in self.restaurants:
            return {}
        
        restaurant = self.restaurants[restaurant_id]
        
        # 统计违规
        violations = [v for v in self.violations if v["restaurant_id"] == restaurant_id]
        violation_types = defaultdict(int)
        for v in violations:
            violation_types[v["type"]] += 1
        
        # 计算风险等级
        risk_score = len(violations) * 10
        if risk_score < 10:
            risk_level = "low"
        elif risk_score < 30:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "restaurant_id": restaurant_id,
            "name": restaurant["name"],
            "violation_count": len(violations),
            "violation_breakdown": dict(violation_types),
            "risk_level": risk_level,
            "risk_score": risk_score
        }


# 示例用法
def main():
    """主函数示例"""
    print("=" * 70)
    print("食品安全管理平台演示")
    print("=" * 70)
    
    # 初始化管理器
    trace_manager = TraceabilityManager()
    lab_manager = LaboratoryManager()
    monitor = RestaurantMonitor()
    
    # ==================== 1. 产品溯源 ====================
    print("\n1. 食品溯源追踪")
    print("-" * 70)
    
    # 注册产品
    product = trace_manager.register_product(
        name="有机纯牛奶",
        category="乳制品",
        batch_id="MILK20240215001",
        manufacturer="光明乳业"
    )
    
    print(f"产品注册成功，溯源码: {product.product_code}")
    
    # 记录生产环节事件
    events = [
        ("原料验收", "内蒙古牧场", "质检员张三", {"milk_quality": "合格"}),
        ("生产加工", "上海工厂", "操作员李四", {"temperature": "4°C", "duration": "2小时"}),
        ("质检放行", "质检中心", "质检员王五", {"tests": ["菌落总数", "蛋白质", "脂肪"]}),
        ("包装入库", "上海工厂", "操作员赵六", {"quantity": 1000, "unit": "箱"}),
        ("物流配送", "物流仓库", "司机钱七", {"vehicle_temp": "2-6°C", "destination": "北京"}),
        ("门店收货", "北京永辉超市", "收货员孙八", {"condition": "良好", "temp": "4°C"}),
    ]
    
    for event_type, location, operator, details in events:
        trace_manager.record_event(
            product_code=product.product_code,
            event_type=event_type,
            location=location,
            operator=operator,
            details=details
        )
    
    # 查询溯源信息
    trace_info = trace_manager.query_traceability(product.product_code)
    
    print(f"\n溯源信息:")
    print(f"  产品名称: {trace_info['name']}")
    print(f"  生产商: {trace_info['manufacturer']}")
    print(f"  生产批次: {product.batch_id}")
    print(f"  溯源环节数: {len(trace_info['trace_chain'])}")
    print(f"  区块链验证: {'通过' if trace_info['verification'] else '失败'}")
    
    print(f"\n溯源链条:")
    for event in trace_info['trace_chain']:
        print(f"  [{event['timestamp']}] {event['event_type']} @ {event['location']} (操作: {event['operator']})")
    
    # ==================== 2. 检测实验室管理 ====================
    print("\n2. 检测实验室管理")
    print("-" * 70)
    
    # 接收样品
    sample = lab_manager.receive_sample(
        product_name="有机纯牛奶",
        batch_id="MILK20240215001",
        client="光明乳业",
        sampling_location="上海工厂",
        quantity=2.0
    )
    
    print(f"样品已接收: {sample.sample_id}")
    
    # 创建检测计划
    test_items = [
        {"name": "菌落总数", "method": "GB 4789.2", "limit": 10000, "unit": "CFU/mL"},
        {"name": "大肠菌群", "method": "GB 4789.3", "limit": 1, "unit": "CFU/mL"},
        {"name": "蛋白质", "method": "GB 5009.5", "limit": 2.9, "unit": "g/100g"},
        {"name": "脂肪", "method": "GB 5009.6", "limit": 3.1, "unit": "g/100g"},
        {"name": "黄曲霉毒素M1", "method": "GB 5009.24", "limit": 0.5, "unit": "μg/kg"}
    ]
    
    tests = lab_manager.create_test_plan(sample.sample_id, test_items)
    print(f"检测计划已创建: {len(tests)} 项")
    
    # 记录检测结果
    test_results = [
        ("T" + sample.sample_id + "01", 5000),    # 菌落总数 - 通过
        ("T" + sample.sample_id + "02", 0),       # 大肠菌群 - 通过
        ("T" + sample.sample_id + "03", 3.2),     # 蛋白质 - 通过
        ("T" + sample.sample_id + "04", 3.5),     # 脂肪 - 通过
        ("T" + sample.sample_id + "05", 0.1),     # 黄曲霉毒素 - 通过
    ]
    
    for test_id, value in test_results:
        lab_manager.record_test_result(test_id, value, "检测员甲")
    
    # 生成报告
    report = lab_manager.generate_report(sample.sample_id)
    
    print(f"\n检测报告 {report.report_id}:")
    print(f"  样品: {sample.product_name}")
    print(f"  检测项: {len(report.tests)}")
    print(f"  判定结果:")
    
    for test in report.tests:
        status_icon = "✓" if test.result_status == "pass" else "✗"
        print(f"    {status_icon} {test.test_item}: {test.result} {test.unit} "
             f"(标准: ≤{test.standard_limit}, 判定: {test.result_status})")
    
    # 审批报告
    if report.approve("质量负责人"):
        print(f"  报告已审批通过")
    
    # ==================== 3. 餐饮安全监控 ====================
    print("\n3. 餐饮安全监控")
    print("-" * 70)
    
    # 注册餐饮企业
    restaurants = [
        ("R001", "海底捞火锅", "上海市浦东新区"),
        ("R002", "肯德基", "上海市静安区"),
        ("R003", "必胜客", "北京市朝阳区"),
    ]
    
    for rid, name, address in restaurants:
        monitor.register_restaurant(rid, name, address, camera_count=3)
    
    # 模拟视频分析
    print("\n模拟视频AI分析:")
    for i in range(20):
        restaurant_id = f"R{np.random.randint(1, 4):03d}"
        camera_id = f"CAM{np.random.randint(1, 4)}"
        
        # 模拟视频帧
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        detections = monitor.analyze_frame(restaurant_id, camera_id, frame)
        
        if detections:
            for det in detections:
                print(f"  [告警] 餐厅 {det['restaurant_id']} - {det['type']} "
                     f"(置信度: {det['confidence']:.2f})")
    
    # 温度监控
    print("\n冷链温度监控:")
    temp_sensors = [
        ("R001", "TEMP001", 5.2, (0, 4)),   # 超标
        ("R002", "TEMP002", 2.5, (0, 4)),   # 正常
        ("R001", "TEMP003", -1.0, (0, 4)),  # 正常
    ]
    
    for restaurant_id, sensor_id, temp, threshold in temp_sensors:
        monitor.check_temperature(restaurant_id, sensor_id, temp, threshold)
    
    # 风险汇总
    print("\n餐厅风险摘要:")
    for rid in ["R001", "R002", "R003"]:
        summary = monitor.get_risk_summary(rid)
        if summary:
            print(f"  {summary['name']}: 违规 {summary['violation_count']} 次, "
                 f"风险等级: {summary['risk_level'].upper()}")
    
    print("\n" + "=" * 70)
    print("演示完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

---

## 10. 效果评估

### 10.1 关键指标达成情况

| 指标类别 | 指标名称 | 目标值 | 实际值 | 达成率 |
|---------|---------|-------|-------|-------|
| **溯源系统** | 溯源环节覆盖率 | 100% | 100% | 100% |
| | 溯源查询响应 | <3秒 | 1.5秒 | 200% |
| | 数据完整率 | >99% | 99.8% | 101% |
| **检测管理** | 无纸化率 | 100% | 100% | 100% |
| | 报告生成时间 | <10分钟 | 5分钟 | 200% |
| | 数据准确率 | >99.9% | 99.95% | 100% |
| **餐饮监管** | 视频接入率 | 100% | 100% | 100% |
| | AI识别准确率 | >95% | 96% | 101% |
| | 违规发现时间 | <5分钟 | 实时 | 达成 |
| **风险预警** | 预警准确率 | >90% | 92% | 102% |
| | 预警提前量 | >7天 | 10天 | 143% |

### 10.2 ROI分析

**投资成本（12个月）**：

| 项目 | 金额（万元） |
|------|------------|
| 平台软件开发 | 2500 |
| 区块链基础设施 | 800 |
| AI视频分析系统 | 1200 |
| 硬件设备采购 | 1000 |
| 实施部署 | 500 |
| **总投资** | **6000** |

**收益分析（12个月）**：

| 收益来源 | 金额（万元） |
|---------|------------|
| 平台服务费 | 4000 |
| 检测服务收入 | 2000 |
| 监管服务收入 | 1500 |
| 效率提升价值 | 1000 |
| 品牌信誉提升 | 500 |
| **总收益** | **9000** |

**ROI计算**：
- **净收益**：9000 - 6000 = 3000万元
- **ROI**：(3000 / 6000) × 100% = **50%**
- **投资回收期**：约8个月

### 10.3 定性效益

1. **消费者信任**：扫码溯源功能提升了消费者对食品安全的信心
2. **监管效率**：监管部门工作效率提升3倍，实现了从被动响应到主动预防的转变
3. **品牌保护**：企业品牌价值提升，产品溢价能力增强
4. **行业标杆**：成为食品安全数字化转型的行业标杆案例

---

## 11. 案例总结

### 11.1 成功因素

1. **政策驱动**：食品安全法规的严格要求推动了企业数字化转型
2. **技术成熟**：区块链、AI等技术的成熟为解决方案提供了技术支撑
3. **多方共赢**：消费者、企业、监管部门都从系统中获益
4. **持续运营**：建立了完善的运营服务体系，保障系统持续发挥作用

### 11.2 经验教训

1. **数据质量**：源头数据质量直接影响溯源可信度，需要严格的数据录入规范
2. **成本控制**：区块链上链成本需要考虑，大批量低频数据可链下存储
3. **用户习惯**：部分传统企业和监管人员需要时间适应数字化工具

### 11.3 未来展望

1. 与供应链金融科技结合，为食品企业提供融资服务
2. 扩展至全球食品贸易溯源，支撑跨境电商
3. 引入物联网技术，实现全自动化的数据采集

---

**创建时间**：2025-01-21  
**最后更新**：2026-02-15  
**文档版本**：v1.0  
**维护者**：DSL Schema研究团队
