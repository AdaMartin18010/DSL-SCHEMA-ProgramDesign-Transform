"""
配置管理

统一管理所有配置
"""

import os
from typing import Optional
from pydantic import BaseSettings


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    multimodal_db_url: str = os.getenv(
        'MULTIMODAL_DB_URL',
        'postgresql://user:password@localhost:5432/multimodal_kg'
    )
    temporal_db_url: str = os.getenv(
        'TEMPORAL_DB_URL',
        'postgresql://user:password@localhost:5432/temporal_kg'
    )

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class LLMConfig(BaseSettings):
    """LLM配置"""
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    anthropic_model: str = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
    llm_provider: str = os.getenv('LLM_PROVIDER', 'openai')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class APIConfig(BaseSettings):
    """API配置"""
    multimodal_api_port: int = int(os.getenv('MULTIMODAL_API_PORT', '8000'))
    temporal_api_port: int = int(os.getenv('TEMPORAL_API_PORT', '8001'))
    llm_api_port: int = int(os.getenv('LLM_API_PORT', '8002'))
    usl_api_port: int = int(os.getenv('USL_API_PORT', '8003'))
    api_host: str = os.getenv('API_HOST', '0.0.0.0')
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class Config:
    """全局配置"""
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    api: APIConfig = APIConfig()


# 全局配置实例
config = Config()
