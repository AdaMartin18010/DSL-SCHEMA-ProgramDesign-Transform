"""
数据压缩模块

专注于数据压缩、解压缩、压缩算法
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import gzip
import zlib
import bz2
import json
import logging

logger = logging.getLogger(__name__)


class CompressionType(Enum):
    """压缩类型"""
    GZIP = "gzip"
    ZLIB = "zlib"
    BZ2 = "bz2"
    NONE = "none"


@dataclass
class CompressionResult:
    """压缩结果"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_type: CompressionType
    compressed_data: bytes


class DataCompression:
    """
    数据压缩器
    
    专注于数据压缩、解压缩、压缩算法
    """
    
    def __init__(self):
        self.compression_history: List[CompressionResult] = []
    
    def compress(self, data: Union[str, bytes, Dict, List],
                compression_type: CompressionType = CompressionType.GZIP) -> CompressionResult:
        """
        压缩数据
        
        Args:
            data: 要压缩的数据
            compression_type: 压缩类型
            
        Returns:
            压缩结果
        """
        # 转换为字节
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        original_size = len(data_bytes)
        
        # 执行压缩
        if compression_type == CompressionType.GZIP:
            compressed_data = gzip.compress(data_bytes)
        elif compression_type == CompressionType.ZLIB:
            compressed_data = zlib.compress(data_bytes)
        elif compression_type == CompressionType.BZ2:
            compressed_data = bz2.compress(data_bytes)
        else:
            compressed_data = data_bytes
        
        compressed_size = len(compressed_data)
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0.0
        
        result = CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compression_type=compression_type,
            compressed_data=compressed_data
        )
        
        self.compression_history.append(result)
        return result
    
    def decompress(self, compressed_data: bytes,
                  compression_type: CompressionType = CompressionType.GZIP) -> bytes:
        """
        解压缩数据
        
        Args:
            compressed_data: 压缩的数据
            compression_type: 压缩类型
            
        Returns:
            解压缩后的数据
        """
        try:
            if compression_type == CompressionType.GZIP:
                return gzip.decompress(compressed_data)
            elif compression_type == CompressionType.ZLIB:
                return zlib.decompress(compressed_data)
            elif compression_type == CompressionType.BZ2:
                return bz2.decompress(compressed_data)
            else:
                return compressed_data
        except Exception as e:
            logger.error(f"解压缩失败: {e}")
            raise
    
    def compress_json(self, data: Dict[str, Any],
                     compression_type: CompressionType = CompressionType.GZIP) -> bytes:
        """
        压缩JSON数据
        
        Args:
            data: JSON数据
            compression_type: 压缩类型
            
        Returns:
            压缩后的字节数据
        """
        json_string = json.dumps(data)
        result = self.compress(json_string, compression_type)
        return result.compressed_data
    
    def decompress_json(self, compressed_data: bytes,
                       compression_type: CompressionType = CompressionType.GZIP) -> Dict[str, Any]:
        """
        解压缩JSON数据
        
        Args:
            compressed_data: 压缩的数据
            compression_type: 压缩类型
            
        Returns:
            JSON数据
        """
        decompressed_data = self.decompress(compressed_data, compression_type)
        json_string = decompressed_data.decode('utf-8')
        return json.loads(json_string)
    
    def compare_compression(self, data: Union[str, bytes, Dict, List]) -> Dict[str, Any]:
        """
        比较不同压缩算法的效果
        
        Args:
            data: 要压缩的数据
            
        Returns:
            比较结果
        """
        results = {}
        
        for comp_type in [CompressionType.GZIP, CompressionType.ZLIB, CompressionType.BZ2]:
            result = self.compress(data, comp_type)
            results[comp_type.value] = {
                'original_size': result.original_size,
                'compressed_size': result.compressed_size,
                'compression_ratio': result.compression_ratio
            }
        
        return results
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """
        获取压缩统计
        
        Returns:
            压缩统计
        """
        if not self.compression_history:
            return {
                'total_compressions': 0,
                'average_ratio': 0.0
            }
        
        total_compressions = len(self.compression_history)
        average_ratio = sum(r.compression_ratio for r in self.compression_history) / total_compressions
        
        return {
            'total_compressions': total_compressions,
            'average_ratio': average_ratio
        }


def main():
    """主函数 - 示例用法"""
    compression = DataCompression()
    
    # 压缩数据
    data = {'key1': 'value1', 'key2': 'value2'}
    result = compression.compress(data, CompressionType.GZIP)
    print(f"压缩结果: 原始大小={result.original_size}, 压缩后大小={result.compressed_size}, 压缩率={result.compression_ratio:.2f}%")
    
    # 解压缩
    decompressed = compression.decompress_json(result.compressed_data, CompressionType.GZIP)
    print(f"解压缩结果: {decompressed}")


if __name__ == '__main__':
    main()
