"""
缓存工具测试

测试缓存功能
"""

import unittest
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 使用相对导入
import os
os.chdir(project_root)

from code.schema_deepening.cache import SimpleCache, cached, get_global_cache


class TestSimpleCache(unittest.TestCase):
    """简单缓存测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.cache = SimpleCache()
    
    def test_set_and_get(self):
        """测试设置和获取"""
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
    
    def test_get_nonexistent(self):
        """测试获取不存在的键"""
        self.assertIsNone(self.cache.get('nonexistent'))
    
    def test_expiration(self):
        """测试过期"""
        self.cache.set('key1', 'value1', ttl=1)
        self.assertEqual(self.cache.get('key1'), 'value1')
        
        time.sleep(1.1)
        self.assertIsNone(self.cache.get('key1'))
    
    def test_delete(self):
        """测试删除"""
        self.cache.set('key1', 'value1')
        self.assertTrue(self.cache.delete('key1'))
        self.assertIsNone(self.cache.get('key1'))
        self.assertFalse(self.cache.delete('nonexistent'))
    
    def test_clear(self):
        """测试清空"""
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        self.cache.clear()
        self.assertEqual(self.cache.size(), 0)
    
    def test_cleanup_expired(self):
        """测试清理过期条目"""
        self.cache.set('key1', 'value1', ttl=0.1)
        self.cache.set('key2', 'value2', ttl=100)
        
        time.sleep(0.2)
        expired_count = self.cache.cleanup_expired()
        
        self.assertEqual(expired_count, 1)
        self.assertIsNone(self.cache.get('key1'))
        self.assertEqual(self.cache.get('key2'), 'value2')
    
    def test_size(self):
        """测试大小"""
        self.assertEqual(self.cache.size(), 0)
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.size(), 1)
        self.cache.set('key2', 'value2')
        self.assertEqual(self.cache.size(), 2)


class TestCachedDecorator(unittest.TestCase):
    """缓存装饰器测试类"""
    
    def test_cached_function(self):
        """测试缓存装饰器"""
        call_count = [0]
        
        @cached(ttl=10)
        def expensive_function(x, y):
            call_count[0] += 1
            return x + y
        
        # 第一次调用
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count[0], 1)
        
        # 第二次调用应该使用缓存
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count[0], 1)  # 没有再次调用
        
        # 不同参数应该重新计算
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count[0], 2)


class TestGlobalCache(unittest.TestCase):
    """全局缓存测试类"""
    
    def test_get_global_cache(self):
        """测试获取全局缓存"""
        cache1 = get_global_cache()
        cache2 = get_global_cache()
        
        # 应该是同一个实例
        self.assertIs(cache1, cache2)
        
        # 测试功能
        cache1.set('test_key', 'test_value')
        self.assertEqual(cache2.get('test_key'), 'test_value')


if __name__ == '__main__':
    unittest.main()
