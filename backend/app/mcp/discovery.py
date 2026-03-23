"""
MCP 服务发现

用于发现和注册 MCP 服务。
"""
import asyncio
import logging
import time
from typing import Any, Optional, List, Dict, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import httpx

from .types import ServiceInfo, ToolDefinition, ResourceDefinition


logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """服务状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class DiscoveredService:
    """发现的服务"""
    info: ServiceInfo
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: float = field(default_factory=time.time)
    check_failures: int = 0
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "info": self.info.to_dict(),
            "status": self.status.value,
            "last_check": self.last_check,
            "check_failures": self.check_failures,
            "metadata": self.metadata,
        }


class ServiceRegistry:
    """
    服务注册中心
    
    管理 MCP 服务的注册、注销和发现。
    
    使用示例:
        registry = ServiceRegistry()
        
        # 注册服务
        await registry.register(service_info)
        
        # 发现服务
        services = await registry.discover()
        
        # 获取特定服务
        service = await registry.get("file-system")
    """
    
    def __init__(
        self,
        heartbeat_interval: float = 30.0,
        heartbeat_timeout: float = 90.0,
    ):
        """
        初始化服务注册中心
        
        Args:
            heartbeat_interval: 心跳间隔（秒）
            heartbeat_timeout: 心跳超时时间（秒）
        """
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        
        self._services: Dict[str, DiscoveredService] = {}
        self._listeners: List[Callable[[str, DiscoveredService], Awaitable[None]]] = []
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def start(self) -> None:
        """启动服务注册中心"""
        if self._running:
            return
        
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Service registry started")
    
    async def stop(self) -> None:
        """停止服务注册中心"""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Service registry stopped")
    
    async def register(self, service_info: ServiceInfo) -> bool:
        """
        注册服务
        
        Args:
            service_info: 服务信息
            
        Returns:
            是否成功
        """
        async with self._lock:
            service = DiscoveredService(
                info=service_info,
                status=ServiceStatus.ONLINE,
            )
            
            self._services[service_info.name] = service
            
            logger.info(f"Service registered: {service_info.name}")
            await self._notify_listeners("registered", service)
            
            return True
    
    async def unregister(self, service_name: str) -> bool:
        """
        注销服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            是否成功
        """
        async with self._lock:
            if service_name not in self._services:
                return False
            
            service = self._services[service_name]
            service.status = ServiceStatus.OFFLINE
            
            del self._services[service_name]
            
            logger.info(f"Service unregistered: {service_name}")
            await self._notify_listeners("unregistered", service)
            
            return True
    
    async def update_heartbeat(self, service_name: str) -> bool:
        """
        更新服务心跳
        
        Args:
            service_name: 服务名称
            
        Returns:
            是否成功
        """
        async with self._lock:
            if service_name not in self._services:
                return False
            
            service = self._services[service_name]
            service.info.last_heartbeat = time.time()
            service.status = ServiceStatus.ONLINE
            service.check_failures = 0
            
            return True
    
    async def get(self, service_name: str) -> Optional[DiscoveredService]:
        """
        获取服务信息
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务信息，不存在则返回 None
        """
        return self._services.get(service_name)
    
    async def discover(
        self,
        capability: Optional[str] = None,
        status: Optional[ServiceStatus] = None,
    ) -> List[DiscoveredService]:
        """
        发现服务
        
        Args:
            capability: 按能力过滤
            status: 按状态过滤
            
        Returns:
            服务列表
        """
        async with self._lock:
            services = list(self._services.values())
        
        # 过滤
        if capability:
            services = [
                s for s in services
                if capability in s.info.capabilities
            ]
        
        if status:
            services = [s for s in services if s.status == status]
        
        return services
    
    async def list_tools(self, service_name: Optional[str] = None) -> List[ToolDefinition]:
        """
        列出工具
        
        Args:
            service_name: 服务名称，None 表示所有服务
            
        Returns:
            工具定义列表
        """
        tools = []
        
        if service_name:
            service = await self.get(service_name)
            if service:
                tools.extend(service.info.tools)
        else:
            services = await self.discover(status=ServiceStatus.ONLINE)
            for service in services:
                tools.extend(service.info.tools)
        
        return tools
    
    async def find_tool(self, tool_name: str) -> Optional[tuple[str, ToolDefinition]]:
        """
        查找工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            (服务名称，工具定义) 或 None
        """
        services = await self.discover(status=ServiceStatus.ONLINE)
        
        for service in services:
            for tool in service.info.tools:
                if tool.name == tool_name:
                    return (service.info.name, tool)
        
        return None
    
    def add_listener(
        self,
        callback: Callable[[str, DiscoveredService], Awaitable[None]],
    ) -> None:
        """
        添加事件监听器
        
        Args:
            callback: 回调函数 (event_type, service)
        """
        self._listeners.append(callback)
    
    def remove_listener(
        self,
        callback: Callable[[str, DiscoveredService], Awaitable[None]],
    ) -> None:
        """移除事件监听器"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    async def _notify_listeners(self, event_type: str, service: DiscoveredService) -> None:
        """通知监听器"""
        for listener in self._listeners:
            try:
                await listener(event_type, service)
            except Exception as e:
                logger.warning(f"Listener error: {e}")
    
    async def _heartbeat_loop(self) -> None:
        """心跳检测循环"""
        while self._running:
            await asyncio.sleep(self.heartbeat_interval)
            
            try:
                await self._check_services()
            except Exception as e:
                logger.exception(f"Heartbeat check error: {e}")
    
    async def _check_services(self) -> None:
        """检查服务健康状态"""
        async with self._lock:
            current_time = time.time()
            
            for service in list(self._services.values()):
                # 检查心跳超时
                time_since_heartbeat = current_time - service.info.last_heartbeat
                
                if time_since_heartbeat > self.heartbeat_timeout:
                    if service.status == ServiceStatus.ONLINE:
                        service.status = ServiceStatus.OFFLINE
                        service.check_failures += 1
                        logger.warning(f"Service timeout: {service.info.name}")
                        await self._notify_listeners("timeout", service)
                
                elif time_since_heartbeat > self.heartbeat_interval * 2:
                    if service.status != ServiceStatus.DEGRADED:
                        service.status = ServiceStatus.DEGRADED
                        logger.info(f"Service degraded: {service.info.name}")
                        await self._notify_listeners("degraded", service)
                
                else:
                    if service.status != ServiceStatus.ONLINE:
                        service.status = ServiceStatus.ONLINE
                        service.check_failures = 0
                        logger.info(f"Service recovered: {service.info.name}")
                        await self._notify_listeners("recovered", service)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        services = list(self._services.values())
        
        return {
            "total": len(services),
            "online": len([s for s in services if s.status == ServiceStatus.ONLINE]),
            "offline": len([s for s in services if s.status == ServiceStatus.OFFLINE]),
            "degraded": len([s for s in services if s.status == ServiceStatus.DEGRADED]),
        }


class ServiceDiscoveryClient:
    """
    服务发现客户端
    
    用于向注册中心注册和发现服务。
    """
    
    def __init__(self, registry_endpoint: str):
        """
        初始化服务发现客户端
        
        Args:
            registry_endpoint: 注册中心端点 URL
        """
        self.registry_endpoint = registry_endpoint
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self) -> None:
        """建立连接"""
        self._client = httpx.AsyncClient(base_url=self.registry_endpoint)
    
    async def close(self) -> None:
        """关闭连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def register(self, service_info: ServiceInfo) -> bool:
        """注册服务"""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.post(
                "/registry/register",
                json=service_info.to_dict(),
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            return False
    
    async def unregister(self, service_name: str) -> bool:
        """注销服务"""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.post(
                "/registry/unregister",
                json={"name": service_name},
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to unregister service: {e}")
            return False
    
    async def discover(self) -> List[ServiceInfo]:
        """发现服务"""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get("/registry/discover")
            response.raise_for_status()
            
            services_data = response.json().get("services", [])
            return [
                ServiceInfo(
                    name=s.get("name", ""),
                    description=s.get("description", ""),
                    version=s.get("version", "1.0.0"),
                    endpoint=s.get("endpoint", ""),
                    capabilities=s.get("capabilities", []),
                )
                for s in services_data
            ]
        except Exception as e:
            logger.error(f"Failed to discover services: {e}")
            return []
    
    async def heartbeat(self, service_name: str) -> bool:
        """发送心跳"""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.post(
                "/registry/heartbeat",
                json={"name": service_name},
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
            return False


class LocalServiceRegistry(ServiceRegistry):
    """
    本地服务注册中心
    
    用于单进程内的服务注册和发现，无需网络通信。
    """
    
    _instance: Optional["LocalServiceRegistry"] = None
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_instance(cls) -> "LocalServiceRegistry":
        """获取单例实例"""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
                await cls._instance.start()
            return cls._instance
    
    @classmethod
    async def reset_instance(cls) -> None:
        """重置单例实例"""
        async with cls._lock:
            if cls._instance:
                try:
                    await cls._instance.stop()
                except RuntimeError:
                    # 事件循环已关闭，跳过停止
                    pass
                cls._instance = None
