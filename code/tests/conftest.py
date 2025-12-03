"""
pytest配置文件

提供测试用的fixtures和配置
"""

import pytest
import os
from datetime import datetime


@pytest.fixture(scope="session")
def test_database_url():
    """测试数据库URL"""
    return os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://test:test@localhost:5432/test_schema_db'
    )


@pytest.fixture(scope="session")
def test_openai_api_key():
    """测试OpenAI API密钥"""
    return os.getenv('TEST_OPENAI_API_KEY', 'test_key')


@pytest.fixture(scope="session")
def test_anthropic_api_key():
    """测试Anthropic API密钥"""
    return os.getenv('TEST_ANTHROPIC_API_KEY', 'test_key')


@pytest.fixture
def sample_schema_text():
    """示例Schema文本"""
    return """
    schema PaymentSchema {
      field amount: Decimal {
        required: true
        constraint: {
          min: 0
          max: 1000000
        }
      }
      
      field currency: String {
        required: true
        default: "USD"
      }
    }
    """


@pytest.fixture
def sample_entity():
    """示例实体"""
    return {
        'id': 'entity_001',
        'type': 'schema',
        'properties': {
            'name': 'PaymentSchema',
            'version': '1.0'
        }
    }
