"""
统一API网关模块

提供统一的API访问入口
"""

from .gateway import app, SERVICES, forward_request

__all__ = [
    'app',
    'SERVICES',
    'forward_request',
]
