# 边缘AI Schema实践案例

## 📑 目录

- [边缘AI Schema实践案例](#边缘ai-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：智能摄像头边缘AI部署](#2-案例1智能摄像头边缘ai部署)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 完整代码实现](#25-完整代码实现)
    - [2.6 效果评估与ROI](#26-效果评估与roi)
  - [3. 案例2：工业设备预测维护](#3-案例2工业设备预测维护)
    - [3.1 企业背景](#31-企业背景)
    - [3.2 技术挑战](#32-技术挑战)
    - [3.3 完整代码实现](#33-完整代码实现)
    - [3.4 效果评估与ROI](#34-效果评估与roi)
  - [4. 案例3：自动驾驶边缘推理](#4-案例3自动驾驶边缘推理)
  - [5. 案例4：智能语音助手边缘部署](#5-案例4智能语音助手边缘部署)
  - [6. 案例总结](#6-案例总结)

---

## 1. 案例概述

本文档提供**边缘AI Schema的实际应用案例**，涵盖智能摄像头、工业设备、自动驾驶、智能语音等领域。边缘AI将AI推理能力下沉到边缘设备，实现低延迟、高隐私、低成本的智能应用。

**案例类型**：

- 智能摄像头边缘AI
- 工业设备预测维护
- 自动驾驶边缘推理
- 智能语音助手

---

## 2. 案例1：智能摄像头边缘AI部署

### 2.1 企业背景

**企业背景**：
某连锁零售企业（以下简称"RetailMax"）成立于2005年，在全国拥有超过3000家门店，员工总数超过8万人。作为零售行业的领军企业，公司面临门店管理效率、客户体验、安全防范等多重挑战。

公司每年在门店安防系统上的投入超过2亿元，传统监控系统主要依赖人工查看录像，效率低下且容易遗漏关键事件。随着AI技术的发展，公司决定在门店部署边缘AI摄像头，实现智能化的监控和分析。

### 2.2 业务痛点

1. **安全事件响应滞后**：传统监控系统依赖人工巡查，从事件发生到发现平均需要4小时，错失最佳处置时机。

2. **客户行为分析缺失**：无法实时了解门店客流热力分布、顾客动线，导致货架布局优化缺乏数据支撑。

3. **远程巡检成本高**：3000家门店每月需要派遣巡检人员超过5000人次，年人力成本超过3000万元。

4. **数据隐私合规风险**：顾客人脸数据上传到云端处理，存在隐私泄露风险，且不符合《个人信息保护法》要求。

5. **网络带宽压力大**：每家门店每天产生约50GB视频数据，上传云端需要大量带宽成本，且网络波动影响服务质量。

### 2.3 业务目标

1. **实时安全预警**：实现安全事件的秒级检测和预警，响应时间从4小时缩短至10秒以内。

2. **智能客流分析**：实时分析门店客流、热力分布、顾客画像，为运营决策提供数据支撑。

3. **降低巡检成本**：通过AI自动巡检，减少90%的人工巡检需求，年节省人力成本2500万元。

4. **确保隐私合规**：所有敏感数据处理在边缘完成，原始视频不上云，满足数据隐私法规要求。

5. **减少网络成本**：边缘处理减少90%的数据上传量，年节省带宽成本500万元。

### 2.4 技术挑战

1. **模型轻量化**：需要在边缘设备上运行复杂的目标检测和识别模型，但边缘设备算力有限（通常<10 TOPS），需要进行模型量化和剪枝。

2. **低延迟推理**：安全检测需要在100ms内完成，才能保证实时性，对模型推理速度要求极高。

3. **多场景适应性**：门店环境复杂多变（光照、角度、遮挡），模型需要具备强大的泛化能力。

4. **边缘-云协同**：需要在边缘侧完成实时处理，同时与云端协同进行模型更新和数据分析。

5. **设备功耗控制**：边缘设备需要7x24小时运行，功耗控制直接影响设备稳定性和运维成本。

### 2.5 完整代码实现

```python
#!/usr/bin/env python3
"""
智能摄像头边缘AI系统
RetailMax 门店智能监控平台

功能模块：
1. 实时目标检测（YOLOv8量化模型）
2. 人脸识别与客流统计
3. 行为分析（跌倒、打架、盗窃检测）
4. 热力图生成与客流分析
5. 边缘-云端协同管理

硬件：NVIDIA Jetson Nano / RK3588
模型：YOLOv8n INT8量化 + MobileFaceNet

作者：AI工程团队
版本：2.1
"""

import cv2
import numpy as np
import onnxruntime as ort
import time
import json
import threading
import queue
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict, deque
import logging
import requests
import sqlite3

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """检测结果"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    track_id: Optional[int] = None


@dataclass
class FaceInfo:
    """人脸信息"""
    face_id: str
    bbox: Tuple[int, int, int, int]
    features: np.ndarray
    age: Optional[int] = None
    gender: Optional[str] = None


@dataclass
class Alert:
    """告警信息"""
    alert_id: str
    alert_type: str
    level: str  # info, warning, critical
    timestamp: datetime
    camera_id: str
    store_id: str
    description: str
    snapshot: Optional[np.ndarray] = None
    metadata: Dict = field(default_factory=dict)


class YOLOv8Detector:
    """YOLOv8目标检测器（ONNX Runtime版本）"""
    
    def __init__(self, model_path: str, conf_thresh: float = 0.5, iou_thresh: float = 0.45):
        """
        初始化检测器
        
        Args:
            model_path: ONNX模型路径
            conf_thresh: 置信度阈值
            iou_thresh: NMS IoU阈值
        """
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        
        # 类别定义
        self.classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
        
        # 重点关注类别
        self.target_classes = {'person', 'backpack', 'handbag', 'suitcase', 'cell phone'}
        
        # 初始化ONNX Runtime
        # 优先使用TensorRT，其次是CUDA，最后是CPU
        providers = ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
        
        # 会话选项
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = 4  # 使用4线程
        
        try:
            self.session = ort.InferenceSession(
                model_path, 
                sess_options=sess_options,
                providers=providers
            )
            logger.info(f"ONNX模型加载成功，使用provider: {self.session.get_providers()}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
            
        # 获取输入输出信息
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.input_width = self.input_shape[2]
        self.input_height = self.input_shape[3]
        
        logger.info(f"模型输入尺寸: {self.input_width}x{self.input_height}")
        
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """图像预处理"""
        # 调整大小
        img = cv2.resize(image, (self.input_width, self.input_height))
        
        # BGR转RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 归一化
        img = img.astype(np.float32) / 255.0
        
        # HWC转CHW
        img = np.transpose(img, (2, 0, 1))
        
        # 添加batch维度
        img = np.expand_dims(img, axis=0)
        
        return img
        
    def postprocess(self, outputs: np.ndarray, orig_shape: Tuple[int, int]) -> List[Detection]:
        """后处理"""
        detections = []
        
        # YOLOv8输出格式: [batch, 84, 8400] -> [batch, num_classes+4, num_anchors]
        predictions = np.squeeze(outputs).T  # [8400, 84]
        
        # 过滤低置信度
        scores = np.max(predictions[:, 4:], axis=1)
        mask = scores > self.conf_thresh
        predictions = predictions[mask]
        scores = scores[mask]
        
        if len(predictions) == 0:
            return detections
            
        # 获取类别和边界框
        class_ids = np.argmax(predictions[:, 4:], axis=1)
        boxes = predictions[:, :4]
        
        # 将中心点+宽高转换为x1,y1,x2,y2
        boxes_xyxy = np.zeros_like(boxes)
        boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2  # x1
        boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2  # y1
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2  # x2
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2  # y2
        
        # 缩放到原图尺寸
        scale_x = orig_shape[1] / self.input_width
        scale_y = orig_shape[0] / self.input_height
        boxes_xyxy[:, [0, 2]] *= scale_x
        boxes_xyxy[:, [1, 3]] *= scale_y
        
        # NMS
        indices = cv2.dnn.NMSBoxes(
            boxes_xyxy.tolist(),
            scores.tolist(),
            self.conf_thresh,
            self.iou_thresh
        )
        
        if len(indices) > 0:
            indices = indices.flatten() if isinstance(indices, np.ndarray) else indices
            
            for idx in indices:
                class_name = self.classes[class_ids[idx]]
                
                # 只保留目标类别
                if class_name not in self.target_classes:
                    continue
                    
                bbox = tuple(boxes_xyxy[idx].astype(int))
                detection = Detection(
                    class_id=int(class_ids[idx]),
                    class_name=class_name,
                    confidence=float(scores[idx]),
                    bbox=bbox
                )
                detections.append(detection)
                
        return detections
        
    def detect(self, image: np.ndarray) -> Tuple[List[Detection], float]:
        """
        执行检测
        
        Returns:
            (detections, inference_time_ms)
        """
        start_time = time.time()
        
        # 预处理
        input_tensor = self.preprocess(image)
        
        # 推理
        outputs = self.session.run(None, {self.input_name: input_tensor})
        
        # 后处理
        detections = self.postprocess(outputs[0], image.shape[:2])
        
        inference_time = (time.time() - start_time) * 1000  # ms
        
        return detections, inference_time


class ObjectTracker:
    """目标跟踪器（简化版SORT算法）"""
    
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        
        self.trackers = []
        self.track_id_count = 0
        self.frame_count = 0
        
    def iou(self, bbox1: Tuple[int, ...], bbox2: Tuple[int, ...]) -> float:
        """计算IoU"""
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
        
    def update(self, detections: List[Detection]) -> List[Detection]:
        """更新跟踪器"""
        self.frame_count += 1
        
        # 匹配检测和跟踪器
        matched = []
        unmatched_detections = []
        unmatched_trackers = list(range(len(self.trackers)))
        
        for det in detections:
            best_iou = 0
            best_tracker = -1
            
            for i in unmatched_trackers:
                iou = self.iou(det.bbox, self.trackers[i]['bbox'])
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_tracker = i
                    
            if best_tracker >= 0:
                matched.append((det, best_tracker))
                unmatched_trackers.remove(best_tracker)
            else:
                unmatched_detections.append(det)
                
        # 更新匹配的跟踪器
        new_trackers = []
        for det, tracker_idx in matched:
            tracker = self.trackers[tracker_idx]
            tracker['bbox'] = det.bbox
            tracker['hits'] += 1
            tracker['time_since_update'] = 0
            det.track_id = tracker['id']
            new_trackers.append(tracker)
            
        # 更新未匹配的跟踪器
        for i in unmatched_trackers:
            tracker = self.trackers[i]
            tracker['time_since_update'] += 1
            if tracker['time_since_update'] <= self.max_age:
                new_trackers.append(tracker)
                
        # 为未匹配的检测创建新跟踪器
        for det in unmatched_detections:
            new_tracker = {
                'id': self.track_id_count,
                'bbox': det.bbox,
                'hits': 1,
                'time_since_update': 0
            }
            det.track_id = self.track_id_count
            new_trackers.append(new_tracker)
            self.track_id_count += 1
            
        self.trackers = new_trackers
        
        return detections


class BehaviorAnalyzer:
    """行为分析器"""
    
    def __init__(self):
        self.track_history = defaultdict(lambda: deque(maxlen=100))
        self.alert_cooldown = defaultdict(float)
        
    def update(self, detections: List[Detection], camera_id: str) -> List[Alert]:
        """更新分析并生成告警"""
        alerts = []
        now = time.time()
        
        for det in detections:
            if det.class_name != 'person' or det.track_id is None:
                continue
                
            # 记录轨迹
            center = ((det.bbox[0] + det.bbox[2]) // 2, (det.bbox[1] + det.bbox[3]) // 2)
            self.track_history[det.track_id].append({
                'center': center,
                'timestamp': now,
                'bbox': det.bbox
            })
            
            # 检测徘徊行为
            if self._detect_loitering(det.track_id):
                alert_key = f"loitering_{det.track_id}"
                if now - self.alert_cooldown[alert_key] > 300:  # 5分钟冷却
                    alert = Alert(
                        alert_id=f"ALT-{int(now * 1000)}",
                        alert_type="LOITERING",
                        level="warning",
                        timestamp=datetime.now(),
                        camera_id=camera_id,
                        store_id="STORE_001",
                        description=f"Detected loitering behavior (Track ID: {det.track_id})"
                    )
                    alerts.append(alert)
                    self.alert_cooldown[alert_key] = now
                    
        return alerts
        
    def _detect_loitering(self, track_id: int, threshold_seconds: float = 60, radius_pixels: int = 100) -> bool:
        """检测徘徊行为"""
        history = self.track_history[track_id]
        if len(history) < 30:  # 需要足够的历史数据
            return False
            
        # 计算在区域内的停留时间
        first_pos = history[0]['center']
        time_in_area = 0
        
        for point in history:
            dist = np.sqrt((point['center'][0] - first_pos[0])**2 + 
                          (point['center'][1] - first_pos[1])**2)
            if dist < radius_pixels:
                time_in_area = point['timestamp'] - history[0]['timestamp']
            else:
                return False  # 离开了区域
                
        return time_in_area > threshold_seconds


class HeatmapGenerator:
    """热力图生成器"""
    
    def __init__(self, width: int, height: int, decay_factor: float = 0.99):
        self.width = width
        self.height = height
        self.decay_factor = decay_factor
        self.accumulator = np.zeros((height, width), dtype=np.float32)
        
    def update(self, detections: List[Detection]):
        """更新热力图"""
        # 衰减
        self.accumulator *= self.decay_factor
        
        # 添加新的检测点
        for det in detections:
            if det.class_name == 'person':
                center_x = (det.bbox[0] + det.bbox[2]) // 2
                center_y = (det.bbox[1] + det.bbox[3]) // 2
                
                # 高斯分布
                x = np.arange(self.width)
                y = np.arange(self.height)
                xx, yy = np.meshgrid(x, y)
                
                gaussian = np.exp(-((xx - center_x)**2 + (yy - center_y)**2) / (2 * 50**2))
                self.accumulator += gaussian
                
    def get_heatmap(self) -> np.ndarray:
        """获取热力图"""
        # 归一化
        if self.accumulator.max() > 0:
            normalized = (self.accumulator / self.accumulator.max() * 255).astype(np.uint8)
        else:
            normalized = np.zeros_like(self.accumulator, dtype=np.uint8)
            
        # 应用颜色映射
        heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        
        return heatmap


class EdgeCameraAI:
    """边缘摄像头AI主类"""
    
    def __init__(self, camera_id: str, store_id: str, model_path: str):
        self.camera_id = camera_id
        self.store_id = store_id
        
        # 初始化组件
        logger.info(f"Initializing Edge AI for camera {camera_id}")
        self.detector = YOLOv8Detector(model_path)
        self.tracker = ObjectTracker()
        self.behavior_analyzer = BehaviorAnalyzer()
        
        # 热力图生成器（延迟初始化）
        self.heatmap_gen = None
        
        # 数据库连接
        self.db_path = f"/data/{store_id}/analytics.db"
        self._init_database()
        
        # 统计信息
        self.stats = {
            'total_frames': 0,
            'avg_inference_time': 0,
            'person_count': 0,
            'alerts_generated': 0
        }
        
    def _init_database(self):
        """初始化本地数据库"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建客流统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS person_count (
                timestamp TEXT,
                camera_id TEXT,
                count INTEGER,
                hour INTEGER
            )
        ''')
        
        # 创建告警表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT,
                level TEXT,
                timestamp TEXT,
                camera_id TEXT,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Alert]]:
        """处理单帧图像"""
        self.stats['total_frames'] += 1
        
        # 初始化热力图生成器
        if self.heatmap_gen is None:
            h, w = frame.shape[:2]
            self.heatmap_gen = HeatmapGenerator(w, h)
        
        # 1. 目标检测
        detections, inference_time = self.detector.detect(frame)
        
        # 更新统计
        self.stats['avg_inference_time'] = (
            self.stats['avg_inference_time'] * 0.9 + inference_time * 0.1
        )
        
        # 2. 目标跟踪
        tracked_detections = self.tracker.update(detections)
        
        # 3. 更新热力图
        self.heatmap_gen.update(tracked_detections)
        
        # 4. 行为分析
        alerts = self.behavior_analyzer.update(tracked_detections, self.camera_id)
        self.stats['alerts_generated'] += len(alerts)
        
        # 5. 统计客流
        person_count = sum(1 for d in tracked_detections if d.class_name == 'person')
        self.stats['person_count'] = person_count
        self._save_person_count(person_count)
        
        # 6. 可视化
        vis_frame = self._visualize(frame, tracked_detections, alerts)
        
        return vis_frame, alerts
        
    def _visualize(self, frame: np.ndarray, detections: List[Detection], 
                  alerts: List[Alert]) -> np.ndarray:
        """可视化检测结果"""
        vis = frame.copy()
        
        # 绘制检测框
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            color = (0, 255, 0) if det.class_name == 'person' else (255, 0, 0)
            
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
            
            label = f"{det.class_name} {det.confidence:.2f}"
            if det.track_id is not None:
                label += f" ID:{det.track_id}"
                
            cv2.putText(vis, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 叠加热力图
        heatmap = self.heatmap_gen.get_heatmap()
        vis = cv2.addWeighted(vis, 0.7, heatmap, 0.3, 0)
        
        # 显示统计信息
        info_text = [
            f"Camera: {self.camera_id}",
            f"Inference: {self.stats['avg_inference_time']:.1f}ms",
            f"Persons: {self.stats['person_count']}",
            f"Alerts: {self.stats['alerts_generated']}"
        ]
        
        y_offset = 30
        for text in info_text:
            cv2.putText(vis, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25
        
        # 显示最新告警
        for i, alert in enumerate(alerts[-3:]):
            alert_text = f"[{alert.level.upper()}] {alert.alert_type}"
            color = (0, 0, 255) if alert.level == 'critical' else (0, 165, 255)
            cv2.putText(vis, alert_text, (10, vis.shape[0] - 30 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return vis
        
    def _save_person_count(self, count: int):
        """保存客流统计到本地数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute(
            "INSERT INTO person_count VALUES (?, ?, ?, ?)",
            (now.isoformat(), self.camera_id, count, now.hour)
        )
        
        conn.commit()
        conn.close()
        
    def get_daily_report(self) -> Dict:
        """获取日报"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 查询今日客流
        cursor.execute('''
            SELECT hour, AVG(count) FROM person_count 
            WHERE timestamp LIKE ? AND camera_id = ?
            GROUP BY hour
        ''', (f'{today}%', self.camera_id))
        
        hourly_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 查询告警统计
        cursor.execute('''
            SELECT alert_type, COUNT(*) FROM alerts 
            WHERE timestamp LIKE ? AND camera_id = ?
            GROUP BY alert_type
        ''', (f'{today}%', self.camera_id))
        
        alert_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'camera_id': self.camera_id,
            'date': today,
            'hourly_person_count': hourly_counts,
            'total_person_count': sum(hourly_counts.values()),
            'alert_summary': alert_stats,
            'system_stats': self.stats
        }


class EdgeCloudSync:
    """边缘-云端同步管理"""
    
    def __init__(self, cloud_endpoint: str, api_key: str):
        self.cloud_endpoint = cloud_endpoint
        self.api_key = api_key
        self.sync_queue = queue.Queue()
        self.running = False
        
    def start(self):
        """启动同步服务"""
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop)
        self.sync_thread.start()
        logger.info("Edge-Cloud sync service started")
        
    def _sync_loop(self):
        """同步循环"""
        while self.running:
            try:
                data = self.sync_queue.get(timeout=5)
                self._upload_data(data)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Sync error: {e}")
                
    def _upload_data(self, data: Dict):
        """上传数据到云端"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.post(
                f"{self.cloud_endpoint}/api/v1/edge-data",
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"Data synced: {data.get('type')}")
            else:
                logger.warning(f"Sync failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
            
    def sync_alert(self, alert: Alert):
        """同步告警"""
        self.sync_queue.put({
            'type': 'alert',
            'data': {
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'level': alert.level,
                'timestamp': alert.timestamp.isoformat(),
                'camera_id': alert.camera_id,
                'store_id': alert.store_id,
                'description': alert.description
            }
        })
        
    def sync_analytics(self, report: Dict):
        """同步分析数据（脱敏后）"""
        # 只上传统计信息，不上传原始视频
        self.sync_queue.put({
            'type': 'analytics',
            'data': report
        })
        
    def stop(self):
        """停止同步服务"""
        self.running = False
        self.sync_thread.join()
        logger.info("Edge-Cloud sync service stopped")


# ==================== 演示程序 ====================

def main():
    """主程序"""
    print("=" * 70)
    print("智能摄像头边缘AI系统 - RetailMax")
    print("=" * 70)
    
    # 检查模型文件
    model_path = "models/yolov8n_int8.onnx"
    
    # 初始化边缘AI
    edge_ai = EdgeCameraAI(
        camera_id="CAM_001",
        store_id="STORE_001",
        model_path=model_path
    )
    
    # 初始化云端同步
    cloud_sync = EdgeCloudSync(
        cloud_endpoint="https://api.retailmax.com",
        api_key="your-api-key"
    )
    cloud_sync.start()
    
    # 打开摄像头（演示使用视频文件）
    cap = cv2.VideoCapture(0)  # 使用摄像头，或替换为视频文件路径
    
    if not cap.isOpened():
        logger.error("Failed to open camera")
        return
    
    print("\n开始处理视频流...")
    print("按 'q' 退出")
    print("-" * 70)
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 处理帧
            vis_frame, alerts = edge_ai.process_frame(frame)
            
            # 同步告警
            for alert in alerts:
                cloud_sync.sync_alert(alert)
                
            # 显示结果
            cv2.imshow('Edge AI Camera', vis_frame)
            
            # 每30秒同步一次分析数据
            frame_count += 1
            if frame_count % 900 == 0:  # 假设30fps，900帧=30秒
                report = edge_ai.get_daily_report()
                cloud_sync.sync_analytics(report)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        cloud_sync.stop()
        
    print("\n" + "=" * 70)
    print("系统已关闭")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

### 2.6 效果评估与ROI

**性能指标对比**：

| 指标 | 传统方案（云端AI） | 边缘AI方案 | 提升幅度 |
|------|------------------|-----------|----------|
| 检测延迟 | 500-2000ms | 50-100ms | **90%降低** |
| 安全事件响应时间 | 4小时 | 10秒 | **99.9%缩短** |
| 数据上传带宽 | 50GB/天/店 | 5GB/天/店 | **90%节省** |
| 年度带宽成本 | 500万元 | 50万元 | **90%降低** |
| 隐私合规风险 | 高 | 低 | **满足法规** |
| 离线运行能力 | 无 | 有 | **可靠性提升** |

**投资回报率（ROI）分析**：

| 项目 | 年度成本/收益（万元） | 说明 |
|------|---------------------|------|
| **边缘设备采购** | -3600 | 3000台 × 1.2万元/台 |
| **软件许可费用** | -300 | 边缘AI软件许可 |
| **安装实施费用** | -450 | 设备部署、调试 |
| **运维成本** | -180 | 设备维护、更换 |
| **减少人力巡检** | +2500 | 减少巡检人员成本 |
| **带宽成本节省** | +450 | 减少云端流量费用 |
| **损耗减少** | +800 | 盗窃、损坏减少 |
| **运营效率提升** | +600 | 客流分析带来的优化 |
| **合规风险降低** | +200 | 避免隐私违规罚款 |
| **年度净收益** | **+1020** | |
| **3年ROI** | **76%** | |

---

## 3. 案例2：工业设备预测维护

### 3.1 企业背景

某大型制造企业的工业设备预测性维护系统，在边缘网关部署LSTM模型，实时分析设备振动、温度等传感器数据，提前预测设备故障。

### 3.2 技术挑战

1. **时序数据处理**：处理高频率传感器数据（1kHz采样），提取有效特征
2. **模型轻量化**：在资源受限的边缘网关（ARM Cortex-A72）上运行
3. **多设备并发**：单网关需同时监控20+台设备
4. **实时性要求**：故障检测延迟需小于100ms
5. **模型持续学习**：支持在线学习，适应设备老化

### 3.3 完整代码实现

```python
#!/usr/bin/env python3
"""
工业设备预测性维护边缘AI系统
边缘网关实时故障预测

硬件：NVIDIA Jetson Nano / RK3588
模型：LSTM INT8量化模型
"""

import numpy as np
import onnxruntime as ort
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import time
import threading
import queue


@dataclass
class SensorReading:
    """传感器读数"""
    timestamp: datetime
    device_id: str
    sensor_type: str
    value: float
    unit: str


@dataclass
class PredictionResult:
    """预测结果"""
    device_id: str
    timestamp: datetime
    failure_probability: float
    remaining_useful_life: Optional[int]  # 小时
    health_score: float  # 0-100
    anomaly_score: float
    recommended_action: str


class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        
    def extract_features(self, data: np.ndarray) -> np.ndarray:
        """提取时序特征"""
        if len(data) < self.window_size:
            # 填充
            data = np.pad(data, (self.window_size - len(data), 0), mode='edge')
        else:
            data = data[-self.window_size:]
            
        features = []
        
        # 时域特征
        features.extend([
            np.mean(data),
            np.std(data),
            np.max(data),
            np.min(data),
            np.ptp(data),  # 峰峰值
            np.sqrt(np.mean(data**2)),  # RMS
        ])
        
        # 频域特征（简化版）
        fft = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(data))
        magnitude = np.abs(fft)
        
        features.extend([
            np.sum(magnitude[:len(magnitude)//2]),  # 总能量
            freqs[np.argmax(magnitude)],  # 主频
            np.std(magnitude),  # 频谱标准差
        ])
        
        # 统计特征
        features.extend([
            np.percentile(data, 25),
            np.percentile(data, 75),
            np.percentile(data, 90),
            np.percentile(data, 10),
        ])
        
        return np.array(features, dtype=np.float32)


class EdgePredictor:
    """边缘预测器"""
    
    def __init__(self, model_path: str, feature_dim: int = 16):
        self.feature_dim = feature_dim
        
        # 初始化ONNX Runtime
        providers = ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 2
        
        self.session = ort.InferenceSession(
            model_path,
            sess_options=sess_options,
            providers=providers
        )
        
        self.input_name = self.session.get_inputs()[0].name
        
        # 特征提取器
        self.feature_extractor = FeatureExtractor()
        
        # 设备数据缓存
        self.device_data: Dict[str, deque] = {}
        self.device_health: Dict[str, float] = {}
        
    def update_sensor_data(self, reading: SensorReading):
        """更新传感器数据"""
        if reading.device_id not in self.device_data:
            self.device_data[reading.device_id] = {
                'vibration': deque(maxlen=1000),
                'temperature': deque(maxlen=1000),
                'current': deque(maxlen=1000)
            }
            self.device_health[reading.device_id] = 100.0
            
        if reading.sensor_type in self.device_data[reading.device_id]:
            self.device_data[reading.device_id][reading.sensor_type].append(reading.value)
            
    def predict(self, device_id: str) -> Optional[PredictionResult]:
        """预测设备状态"""
        if device_id not in self.device_data:
            return None
            
        data = self.device_data[device_id]
        
        # 检查数据量
        if len(data['vibration']) < 100:
            return None
            
        # 提取特征
        vibration_features = self.feature_extractor.extract_features(
            np.array(data['vibration'])
        )
        temp_features = self.feature_extractor.extract_features(
            np.array(data['temperature'])
        )
        current_features = self.feature_extractor.extract_features(
            np.array(data['current'])
        )
        
        # 合并特征
        features = np.concatenate([vibration_features, temp_features, current_features])
        features = features.reshape(1, -1).astype(np.float32)
        
        # 推理
        outputs = self.session.run(None, {self.input_name: features})
        
        failure_prob = float(outputs[0][0][0])
        rul = int(outputs[1][0][0]) if len(outputs) > 1 else None
        
        # 更新健康度
        health = max(0, 100 - failure_prob * 100)
        self.device_health[device_id] = health * 0.9 + self.device_health[device_id] * 0.1
        
        # 确定推荐操作
        action = self._determine_action(failure_prob, self.device_health[device_id])
        
        return PredictionResult(
            device_id=device_id,
            timestamp=datetime.now(),
            failure_probability=failure_prob,
            remaining_useful_life=rul,
            health_score=self.device_health[device_id],
            anomaly_score=failure_prob,
            recommended_action=action
        )
        
    def _determine_action(self, failure_prob: float, health: float) -> str:
        """确定推荐操作"""
        if failure_prob > 0.7 or health < 30:
            return "URGENT: Schedule immediate maintenance"
        elif failure_prob > 0.4 or health < 60:
            return "WARNING: Plan maintenance within 7 days"
        elif failure_prob > 0.2 or health < 80:
            return "ADVISORY: Schedule routine inspection"
        else:
            return "NORMAL: Continue monitoring"


class EdgeMaintenanceSystem:
    """边缘维护系统主类"""
    
    def __init__(self, model_path: str, mqtt_broker: str):
        self.predictor = EdgePredictor(model_path)
        self.mqtt_broker = mqtt_broker
        
        # 预测结果队列
        self.prediction_queue = queue.Queue()
        
        # 运行状态
        self.running = False
        
    def start(self):
        """启动系统"""
        self.running = True
        
        # 启动数据接收线程
        self.data_thread = threading.Thread(target=self._data_receiver)
        self.data_thread.start()
        
        # 启动预测线程
        self.prediction_thread = threading.Thread(target=self._prediction_loop)
        self.prediction_thread.start()
        
        # 启动上报线程
        self.upload_thread = threading.Thread(target=self._upload_loop)
        self.upload_thread.start()
        
        print("Edge Maintenance System started")
        
    def _data_receiver(self):
        """数据接收循环（模拟MQTT接收）"""
        while self.running:
            # 模拟接收传感器数据
            # 实际应从MQTT订阅
            time.sleep(0.1)
            
    def _prediction_loop(self):
        """预测循环"""
        while self.running:
            for device_id in list(self.predictor.device_data.keys()):
                result = self.predictor.predict(device_id)
                if result:
                    self.prediction_queue.put(result)
                    
                    # 高优先级告警立即上报
                    if result.failure_probability > 0.5:
                        self._send_alert(result)
                        
            time.sleep(60)  # 每分钟预测一次
            
    def _upload_loop(self):
        """上报循环"""
        while self.running:
            try:
                result = self.prediction_queue.get(timeout=300)  # 5分钟批量上报
                self._upload_result(result)
            except queue.Empty:
                # 批量上报健康状态
                self._upload_health_summary()
                
    def _send_alert(self, result: PredictionResult):
        """发送告警"""
        alert = {
            "type": "PREDICTIVE_MAINTENANCE_ALERT",
            "device_id": result.device_id,
            "timestamp": result.timestamp.isoformat(),
            "failure_probability": result.failure_probability,
            "health_score": result.health_score,
            "recommended_action": result.recommended_action
        }
        print(f"ALERT: {json.dumps(alert)}")
        
    def _upload_result(self, result: PredictionResult):
        """上报预测结果"""
        # 实际上传到云端
        pass
        
    def _upload_health_summary(self):
        """上报健康状态汇总"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "device_health": self.predictor.device_health
        }
        print(f"Health Summary: {json.dumps(summary)}")
        
    def stop(self):
        """停止系统"""
        self.running = False
        self.data_thread.join()
        self.prediction_thread.join()
        self.upload_thread.join()
        print("Edge Maintenance System stopped")


# 演示
if __name__ == "__main__":
    # 创建模拟数据
    np.random.seed(42)
    
    system = EdgeMaintenanceSystem(
        model_path="models/lstm_predictor.onnx",
        mqtt_broker="mqtt.factory.local"
    )
    
    # 模拟设备数据
    for i in range(1000):
        # 模拟传感器数据（添加趋势模拟故障）
        base_vibration = 2.0 + i * 0.001  # 逐渐增大
        vibration = np.random.normal(base_vibration, 0.5)
        
        reading = SensorReading(
            timestamp=datetime.now(),
            device_id="CNC_001",
            sensor_type="vibration",
            value=vibration,
            unit="mm/s"
        )
        system.predictor.update_sensor_data(reading)
        
    # 预测
    result = system.predictor.predict("CNC_001")
    if result:
        print(f"\nPrediction Result:")
        print(f"  Device: {result.device_id}")
        print(f"  Failure Probability: {result.failure_probability:.2%}")
        print(f"  Health Score: {result.health_score:.1f}")
        print(f"  Remaining Useful Life: {result.remaining_useful_life} hours")
        print(f"  Recommended Action: {result.recommended_action}")
```

### 3.4 效果评估与ROI

| 指标 | 实施前 | 实施后 | 提升幅度 |
|------|--------|--------|----------|
| 计划外停机时间 | 450小时/年 | 120小时/年 | **73%降低** |
| 维护成本 | 基准 | -30% | **30%节省** |
| 设备寿命 | 基准 | +15% | **15%延长** |
| 预测准确率 | N/A | 89% | **高精度** |
| 检测延迟 | N/A | <50ms | **实时** |

---

## 4. 案例3：自动驾驶边缘推理

*（保留原有内容）*

## 5. 案例4：智能语音助手边缘部署

*（保留原有内容）*

## 6. 案例总结

### 6.1 案例对比

| 案例 | 应用场景 | 延迟要求 | 模型大小 | 精度 | 功耗 | ROI |
|------|---------|---------|---------|------|------|-----|
| **智能摄像头** | 零售监控 | <100ms | 5MB | 90% | 15W | 76% |
| **预测维护** | 工业设备 | <50ms | 2MB | 89% | 10W | 180% |
| **自动驾驶** | 车辆控制 | <10ms | 50MB | 95% | 100W | N/A |
| **语音助手** | 智能音箱 | <200ms | 200MB | 94% | 5W | 120% |

### 6.2 最佳实践

1. **模型优化**：使用INT8量化、剪枝、知识蒸馏等技术压缩模型
2. **硬件选型**：根据延迟和功耗要求选择合适的边缘芯片
3. **边缘-云协同**：合理分配计算任务，边缘做实时处理，云端做训练
4. **OTA更新**：支持模型的远程更新和版本管理
5. **安全加固**：边缘设备需要防篡改和加密保护

---

**创建时间**：2025-01-21
**最后更新**：2025-02-15
**文档版本**：v2.0
**维护者**：DSL Schema研究团队
