"""
数据转换API网关模块

专注于数据转换API网关、路由管理、请求处理、响应管理
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class HttpMethod(Enum):
    """HTTP方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ApiVersion(Enum):
    """API版本"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"


class ResponseStatus(Enum):
    """响应状态"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL_SUCCESS = "partial_success"


@dataclass
class ApiRoute:
    """API路由"""
    route_id: str
    path: str
    method: HttpMethod
    handler: Callable
    version: ApiVersion = ApiVersion.V1
    description: str = ""
    parameters: Dict[str, Any] = None
    response_schema: Dict[str, Any] = None
    enabled: bool = True


@dataclass
class ApiRequest:
    """API请求"""
    request_id: str
    path: str
    method: HttpMethod
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Any
    timestamp: datetime
    client_ip: str = ""
    user_id: Optional[str] = None


@dataclass
class ApiResponse:
    """API响应"""
    response_id: str
    request_id: str
    status: ResponseStatus
    status_code: int
    data: Any
    message: str = ""
    errors: List[str] = None
    timestamp: datetime = None
    execution_time: float = 0.0


@dataclass
class RateLimitRule:
    """速率限制规则"""
    rule_id: str
    path: str
    method: HttpMethod
    limit: int  # 请求次数
    window: int  # 时间窗口（秒）
    enabled: bool = True


class DataTransformationApiGateway:
    """数据转换API网关"""
    
    def __init__(self):
        """初始化API网关"""
        self.routes: Dict[str, ApiRoute] = {}
        self.requests: List[ApiRequest] = []
        self.responses: List[ApiResponse] = []
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.middleware: List[Callable] = []
        self.gateway_config: Dict[str, Any] = {}
    
    def register_route(
        self,
        path: str,
        method: HttpMethod,
        handler: Callable,
        version: ApiVersion = ApiVersion.V1,
        description: str = "",
        parameters: Dict[str, Any] = None,
        response_schema: Dict[str, Any] = None
    ) -> ApiRoute:
        """注册API路由"""
        route_id = f"route_{hashlib.md5(f'{path}_{method.value}_{version.value}'.encode()).hexdigest()[:8]}"
        
        route = ApiRoute(
            route_id=route_id,
            path=path,
            method=method,
            handler=handler,
            version=version,
            description=description,
            parameters=parameters or {},
            response_schema=response_schema or {}
        )
        
        self.routes[route_id] = route
        logger.info(f"注册API路由: {path} [{method.value}] ({route_id})")
        
        return route
    
    def handle_request(
        self,
        path: str,
        method: HttpMethod,
        headers: Dict[str, str],
        query_params: Dict[str, Any] = None,
        body: Any = None,
        client_ip: str = ""
    ) -> ApiResponse:
        """处理API请求"""
        request_id = f"req_{hashlib.md5(f'{path}_{method.value}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        start_time = datetime.now()
        
        # 创建请求对象
        request = ApiRequest(
            request_id=request_id,
            path=path,
            method=method,
            headers=headers,
            query_params=query_params or {},
            body=body,
            timestamp=start_time,
            client_ip=client_ip
        )
        
        self.requests.append(request)
        
        try:
            # 执行中间件
            for middleware_func in self.middleware:
                middleware_func(request)
            
            # 查找路由
            route = self._find_route(path, method)
            
            if not route:
                return self._create_error_response(
                    request_id, 404, "Route not found", f"Path {path} not found"
                )
            
            if not route.enabled:
                return self._create_error_response(
                    request_id, 503, "Service unavailable", f"Route {route.route_id} is disabled"
                )
            
            # 检查速率限制
            if not self._check_rate_limit(path, method, client_ip):
                return self._create_error_response(
                    request_id, 429, "Too many requests", "Rate limit exceeded"
                )
            
            # 验证请求参数
            validation_result = self._validate_request(route, request)
            if not validation_result["valid"]:
                return self._create_error_response(
                    request_id, 400, "Bad request", validation_result["error"]
                )
            
            # 执行处理器
            result = route.handler(request)
            
            # 创建响应
            execution_time = (datetime.now() - start_time).total_seconds()
            response = ApiResponse(
                response_id=f"resp_{hashlib.md5(request_id.encode()).hexdigest()[:8]}",
                request_id=request_id,
                status=ResponseStatus.SUCCESS,
                status_code=200,
                data=result,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            
            self.responses.append(response)
            logger.info(f"API请求处理成功: {path} [{method.value}] - {execution_time:.3f}s")
            
            return response
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"API请求处理失败: {path} [{method.value}] - {str(e)}")
            
            return self._create_error_response(
                request_id, 500, "Internal server error", str(e), execution_time
            )
    
    def _find_route(self, path: str, method: HttpMethod) -> Optional[ApiRoute]:
        """查找路由"""
        for route in self.routes.values():
            if route.path == path and route.method == method:
                return route
        return None
    
    def _check_rate_limit(self, path: str, method: HttpMethod, client_ip: str) -> bool:
        """检查速率限制"""
        for rule in self.rate_limit_rules.values():
            if rule.enabled and rule.path == path and rule.method == method:
                # 这里应该实现实际的速率限制检查逻辑
                # 例如：使用Redis或内存计数器
                logger.debug(f"检查速率限制: {path} [{method.value}] - {client_ip}")
                return True
        return True
    
    def _validate_request(self, route: ApiRoute, request: ApiRequest) -> Dict[str, Any]:
        """验证请求"""
        # 这里应该实现实际的请求验证逻辑
        # 例如：检查必需参数、参数类型、参数范围等
        return {"valid": True, "error": ""}
    
    def _create_error_response(
        self,
        request_id: str,
        status_code: int,
        message: str,
        error: str,
        execution_time: float = 0.0
    ) -> ApiResponse:
        """创建错误响应"""
        response = ApiResponse(
            response_id=f"resp_{hashlib.md5(request_id.encode()).hexdigest()[:8]}",
            request_id=request_id,
            status=ResponseStatus.ERROR,
            status_code=status_code,
            data=None,
            message=message,
            errors=[error],
            timestamp=datetime.now(),
            execution_time=execution_time
        )
        
        self.responses.append(response)
        return response
    
    def add_rate_limit_rule(
        self,
        path: str,
        method: HttpMethod,
        limit: int,
        window: int
    ) -> RateLimitRule:
        """添加速率限制规则"""
        rule_id = f"ratelimit_{hashlib.md5(f'{path}_{method.value}'.encode()).hexdigest()[:8]}"
        
        rule = RateLimitRule(
            rule_id=rule_id,
            path=path,
            method=method,
            limit=limit,
            window=window
        )
        
        self.rate_limit_rules[rule_id] = rule
        logger.info(f"添加速率限制规则: {path} [{method.value}] - {limit}/{window}s")
        
        return rule
    
    def add_middleware(self, middleware_func: Callable):
        """添加中间件"""
        self.middleware.append(middleware_func)
        logger.info(f"添加中间件: {middleware_func.__name__}")
    
    def get_api_statistics(self) -> Dict[str, Any]:
        """获取API统计信息"""
        total_requests = len(self.requests)
        successful_requests = len([
            r for r in self.responses
            if r.status == ResponseStatus.SUCCESS
        ])
        failed_requests = total_requests - successful_requests
        
        avg_execution_time = sum(
            r.execution_time for r in self.responses
        ) / len(self.responses) if self.responses else 0
        
        requests_by_method = {}
        for req in self.requests:
            method = req.method.value
            requests_by_method[method] = requests_by_method.get(method, 0) + 1
        
        return {
            "total_routes": len(self.routes),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "avg_execution_time": avg_execution_time,
            "requests_by_method": requests_by_method
        }
    
    def get_route_list(self) -> List[Dict[str, Any]]:
        """获取路由列表"""
        return [
            {
                "route_id": route.route_id,
                "path": route.path,
                "method": route.method.value,
                "version": route.version.value,
                "description": route.description,
                "enabled": route.enabled
            }
            for route in self.routes.values()
        ]


class ApiGatewayMiddleware:
    """API网关中间件"""
    
    @staticmethod
    def authentication_middleware(request: ApiRequest):
        """认证中间件"""
        # 这里应该实现实际的认证逻辑
        # 例如：检查JWT token、API key等
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            logger.warning(f"请求缺少认证信息: {request.request_id}")
    
    @staticmethod
    def logging_middleware(request: ApiRequest):
        """日志中间件"""
        logger.info(f"API请求: {request.method.value} {request.path} - {request.request_id}")
    
    @staticmethod
    def cors_middleware(request: ApiRequest):
        """CORS中间件"""
        # 这里应该实现实际的CORS逻辑
        pass
    
    @staticmethod
    def request_id_middleware(request: ApiRequest):
        """请求ID中间件"""
        if "X-Request-ID" not in request.headers:
            request.headers["X-Request-ID"] = request.request_id
