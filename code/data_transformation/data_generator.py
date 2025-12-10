"""
数据生成模块

专注于测试数据生成、模拟数据生成、数据填充
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random
import string
import logging

logger = logging.getLogger(__name__)


class GeneratorType(Enum):
    """生成器类型"""
    RANDOM = "random"  # 随机生成
    SEQUENTIAL = "sequential"  # 顺序生成
    PATTERN = "pattern"  # 模式生成
    FAKE = "fake"  # 模拟数据生成


@dataclass
class FieldGenerator:
    """字段生成器"""
    field_name: str
    generator_type: GeneratorType
    generator_config: Dict[str, Any]


@dataclass
class GenerationResult:
    """生成结果"""
    generation_id: str
    records_generated: int
    generation_time: float
    data: List[Dict[str, Any]]


class DataGenerator:
    """
    数据生成器
    
    专注于测试数据生成、模拟数据生成、数据填充
    """
    
    def __init__(self, random_seed: Optional[int] = None):
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
        self.generation_history: List[GenerationResult] = []
    
    def generate(self, schema: List[FieldGenerator], count: int) -> GenerationResult:
        """
        生成数据
        
        Args:
            schema: 字段生成器列表
            count: 生成记录数
            
        Returns:
            生成结果
        """
        generation_id = f"gen_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        data = []
        for i in range(count):
            record = {}
            for field_gen in schema:
                value = self._generate_field_value(field_gen, i)
                record[field_gen.field_name] = value
            data.append(record)
        
        end_time = datetime.utcnow()
        generation_time = (end_time - start_time).total_seconds()
        
        result = GenerationResult(
            generation_id=generation_id,
            records_generated=count,
            generation_time=generation_time,
            data=data
        )
        
        self.generation_history.append(result)
        return result
    
    def _generate_field_value(self, field_gen: FieldGenerator, index: int) -> Any:
        """生成字段值"""
        gen_type = field_gen.generator_type
        config = field_gen.generator_config
        
        if gen_type == GeneratorType.RANDOM:
            return self._generate_random(field_gen.field_name, config)
        elif gen_type == GeneratorType.SEQUENTIAL:
            return self._generate_sequential(field_gen.field_name, index, config)
        elif gen_type == GeneratorType.PATTERN:
            return self._generate_pattern(field_gen.field_name, index, config)
        elif gen_type == GeneratorType.FAKE:
            return self._generate_fake(field_gen.field_name, config)
        else:
            return None
    
    def _generate_random(self, field_name: str, config: Dict[str, Any]) -> Any:
        """随机生成"""
        data_type = config.get('type', 'string')
        
        if data_type == 'integer':
            min_val = config.get('min', 0)
            max_val = config.get('max', 100)
            return random.randint(min_val, max_val)
        elif data_type == 'float':
            min_val = config.get('min', 0.0)
            max_val = config.get('max', 100.0)
            return random.uniform(min_val, max_val)
        elif data_type == 'string':
            length = config.get('length', 10)
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        elif data_type == 'boolean':
            return random.choice([True, False])
        elif data_type == 'date':
            start_date = config.get('start_date', datetime(2000, 1, 1))
            end_date = config.get('end_date', datetime.now())
            delta = end_date - start_date
            days = random.randint(0, delta.days)
            return (start_date + timedelta(days=days)).isoformat()
        else:
            return None
    
    def _generate_sequential(self, field_name: str, index: int, config: Dict[str, Any]) -> Any:
        """顺序生成"""
        data_type = config.get('type', 'integer')
        start = config.get('start', 0)
        step = config.get('step', 1)
        
        if data_type == 'integer':
            return start + index * step
        elif data_type == 'string':
            prefix = config.get('prefix', '')
            return f"{prefix}{start + index * step}"
        else:
            return start + index * step
    
    def _generate_pattern(self, field_name: str, index: int, config: Dict[str, Any]) -> Any:
        """模式生成"""
        pattern = config.get('pattern', '{index}')
        return pattern.format(index=index, field=field_name)
    
    def _generate_fake(self, field_name: str, config: Dict[str, Any]) -> Any:
        """模拟数据生成"""
        fake_type = config.get('fake_type', 'name')
        
        if fake_type == 'name':
            first_names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']
            return f"{random.choice(first_names)} {random.choice(last_names)}"
        elif fake_type == 'email':
            domains = ['example.com', 'test.com', 'demo.com']
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
            return f"{username}@{random.choice(domains)}"
        elif fake_type == 'phone':
            return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        elif fake_type == 'address':
            streets = ['Main St', 'Oak Ave', 'Park Rd', 'Elm St']
            return f"{random.randint(1, 999)} {random.choice(streets)}"
        else:
            return f"fake_{field_name}_{random.randint(1000, 9999)}"
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        获取生成统计
        
        Returns:
            生成统计
        """
        total_generations = len(self.generation_history)
        total_records = sum(r.records_generated for r in self.generation_history)
        
        if total_generations > 0:
            avg_time = sum(r.generation_time for r in self.generation_history) / total_generations
        else:
            avg_time = 0.0
        
        return {
            'total_generations': total_generations,
            'total_records_generated': total_records,
            'average_generation_time': avg_time
        }


def main():
    """主函数 - 示例用法"""
    generator = DataGenerator()
    
    # 定义Schema
    schema = [
        FieldGenerator('id', GeneratorType.SEQUENTIAL, {'type': 'integer', 'start': 1}),
        FieldGenerator('name', GeneratorType.FAKE, {'fake_type': 'name'}),
        FieldGenerator('age', GeneratorType.RANDOM, {'type': 'integer', 'min': 18, 'max': 65})
    ]
    
    # 生成数据
    result = generator.generate(schema, 10)
    print(f"生成结果: 记录数={result.records_generated}")


if __name__ == '__main__':
    main()
