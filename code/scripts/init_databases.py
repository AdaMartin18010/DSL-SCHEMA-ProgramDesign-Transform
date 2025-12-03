"""
数据库初始化脚本

初始化所有数据库
"""

import sys
import os
# 添加code目录到Python路径
code_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, code_dir)

from multimodal_kg import MultimodalKGStorage
from temporal_kg import TemporalKGStorage
from config import config


def init_multimodal_db():
    """初始化多模态知识图谱数据库"""
    print("初始化多模态知识图谱数据库...")
    storage = MultimodalKGStorage(database_url=config.database.multimodal_db_url)
    success = storage.initialize_database()
    if success:
        print("✅ 多模态知识图谱数据库初始化成功")
    else:
        print("❌ 多模态知识图谱数据库初始化失败")
    return success


def init_temporal_db():
    """初始化时序知识图谱数据库"""
    print("初始化时序知识图谱数据库...")
    storage = TemporalKGStorage(database_url=config.database.temporal_db_url)
    success = storage.initialize_database()
    if success:
        print("✅ 时序知识图谱数据库初始化成功")
    else:
        print("❌ 时序知识图谱数据库初始化失败")
    return success


def main():
    """主函数"""
    print("开始初始化数据库...")
    
    multimodal_success = init_multimodal_db()
    temporal_success = init_temporal_db()
    
    if multimodal_success and temporal_success:
        print("\n🎉 所有数据库初始化成功！")
        return 0
    else:
        print("\n❌ 数据库初始化失败")
        return 1


if __name__ == "__main__":
    exit(main())
