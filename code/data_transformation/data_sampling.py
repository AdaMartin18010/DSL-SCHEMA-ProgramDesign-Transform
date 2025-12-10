"""
数据采样模块

专注于数据采样、随机采样、分层采样、系统采样
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


class SamplingMethod(Enum):
    """采样方法"""
    RANDOM = "random"  # 随机采样
    SYSTEMATIC = "systematic"  # 系统采样
    STRATIFIED = "stratified"  # 分层采样
    CLUSTER = "cluster"  # 聚类采样
    RESERVOIR = "reservoir"  # 蓄水池采样


@dataclass
class SamplingConfig:
    """采样配置"""
    method: SamplingMethod
    sample_size: Optional[int] = None  # 样本大小
    sample_ratio: Optional[float] = None  # 采样比例
    strata_field: Optional[str] = None  # 分层字段（用于分层采样）
    random_seed: Optional[int] = None  # 随机种子


@dataclass
class SamplingResult:
    """采样结果"""
    sample_id: str
    original_size: int
    sample_size: int
    method: SamplingMethod
    sample_data: List[Dict[str, Any]]
    sampling_time: float


class DataSampling:
    """
    数据采样器
    
    专注于数据采样、随机采样、分层采样、系统采样
    """
    
    def __init__(self):
        self.sampling_history: List[SamplingResult] = []
    
    def sample(self, data: List[Dict[str, Any]], config: SamplingConfig) -> SamplingResult:
        """
        采样数据
        
        Args:
            data: 数据列表
            config: 采样配置
            
        Returns:
            采样结果
        """
        sample_id = f"sample_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        # 设置随机种子
        if config.random_seed is not None:
            random.seed(config.random_seed)
        
        # 确定样本大小
        if config.sample_size:
            sample_size = min(config.sample_size, len(data))
        elif config.sample_ratio:
            sample_size = int(len(data) * config.sample_ratio)
        else:
            sample_size = len(data) // 10  # 默认10%
        
        # 根据方法采样
        if config.method == SamplingMethod.RANDOM:
            sample_data = self._random_sample(data, sample_size)
        elif config.method == SamplingMethod.SYSTEMATIC:
            sample_data = self._systematic_sample(data, sample_size)
        elif config.method == SamplingMethod.STRATIFIED:
            sample_data = self._stratified_sample(data, sample_size, config.strata_field)
        elif config.method == SamplingMethod.CLUSTER:
            sample_data = self._cluster_sample(data, sample_size)
        elif config.method == SamplingMethod.RESERVOIR:
            sample_data = self._reservoir_sample(data, sample_size)
        else:
            sample_data = self._random_sample(data, sample_size)
        
        end_time = datetime.utcnow()
        sampling_time = (end_time - start_time).total_seconds()
        
        result = SamplingResult(
            sample_id=sample_id,
            original_size=len(data),
            sample_size=len(sample_data),
            method=config.method,
            sample_data=sample_data,
            sampling_time=sampling_time
        )
        
        self.sampling_history.append(result)
        return result
    
    def _random_sample(self, data: List[Dict[str, Any]], sample_size: int) -> List[Dict[str, Any]]:
        """随机采样"""
        return random.sample(data, min(sample_size, len(data)))
    
    def _systematic_sample(self, data: List[Dict[str, Any]], sample_size: int) -> List[Dict[str, Any]]:
        """系统采样"""
        if len(data) == 0:
            return []
        
        step = len(data) // sample_size if sample_size > 0 else 1
        return [data[i] for i in range(0, len(data), step)][:sample_size]
    
    def _stratified_sample(self, data: List[Dict[str, Any]], sample_size: int,
                          strata_field: Optional[str]) -> List[Dict[str, Any]]:
        """分层采样"""
        if not strata_field:
            return self._random_sample(data, sample_size)
        
        # 按字段分组
        strata = {}
        for record in data:
            key = record.get(strata_field)
            if key not in strata:
                strata[key] = []
            strata[key].append(record)
        
        # 每层采样
        sample_data = []
        samples_per_stratum = sample_size // len(strata) if len(strata) > 0 else sample_size
        
        for stratum_data in strata.values():
            stratum_sample = self._random_sample(stratum_data, samples_per_stratum)
            sample_data.extend(stratum_sample)
        
        # 如果样本数不足，随机补充
        if len(sample_data) < sample_size:
            remaining = sample_size - len(sample_data)
            remaining_data = [r for r in data if r not in sample_data]
            sample_data.extend(self._random_sample(remaining_data, remaining))
        
        return sample_data[:sample_size]
    
    def _cluster_sample(self, data: List[Dict[str, Any]], sample_size: int) -> List[Dict[str, Any]]:
        """聚类采样（简化实现：随机选择聚类）"""
        # 简化实现：随机采样
        return self._random_sample(data, sample_size)
    
    def _reservoir_sample(self, data: List[Dict[str, Any]], sample_size: int) -> List[Dict[str, Any]]:
        """蓄水池采样"""
        if len(data) <= sample_size:
            return data.copy()
        
        reservoir = data[:sample_size].copy()
        
        for i in range(sample_size, len(data)):
            j = random.randint(0, i)
            if j < sample_size:
                reservoir[j] = data[i]
        
        return reservoir
    
    def get_sampling_stats(self) -> Dict[str, Any]:
        """
        获取采样统计
        
        Returns:
            采样统计
        """
        total_samplings = len(self.sampling_history)
        
        if total_samplings == 0:
            return {
                'total_samplings': 0
            }
        
        method_counts = {}
        for result in self.sampling_history:
            method = result.method.value
            method_counts[method] = method_counts.get(method, 0) + 1
        
        total_samples = sum(r.sample_size for r in self.sampling_history)
        total_original = sum(r.original_size for r in self.sampling_history)
        
        return {
            'total_samplings': total_samplings,
            'method_counts': method_counts,
            'total_samples': total_samples,
            'total_original': total_original,
            'average_sampling_ratio': (total_samples / total_original * 100) if total_original > 0 else 0.0
        }


def main():
    """主函数 - 示例用法"""
    sampling = DataSampling()
    
    # 采样数据
    data = [{'id': i, 'value': i * 2} for i in range(100)]
    
    config = SamplingConfig(
        method=SamplingMethod.RANDOM,
        sample_size=10
    )
    
    result = sampling.sample(data, config)
    print(f"采样结果: 原始={result.original_size}, 样本={result.sample_size}")


if __name__ == '__main__':
    main()
