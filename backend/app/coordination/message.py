"""
MessageBus — 消息总线
"""
import asyncio
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import enum


class MessageType(str, enum.Enum):
    """消息类型"""
    TASK_ASSIGN = "task_assign"          # 任务分配
    TASK_HANDOFF = "task_handoff"        # 任务传递
    STATUS_UPDATE = "status_update"      # 状态更新
    REQUEST_HELP = "request_help"        # 请求帮助
    PROVIDE_RESULT = "provide_result"    # 提供结果
    NOTIFICATION = "notification"        # 通知


@dataclass
class Message:
    """消息"""
    type: MessageType
    channel: str  # 项目 ID 作为频道
    sender: str   # Agent ID
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


class MessageBus:
    """
    消息总线
    
    支持按项目分频道的发布/订阅模式
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}  # channel -> callbacks
        self._history: Dict[str, List[Message]] = {}  # channel -> messages
    
    def subscribe(self, channel: str, callback: Callable) -> None:
        """
        订阅频道
        
        Args:
            channel: 频道名称（项目 ID）
            callback: 回调函数
        """
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)
    
    def unsubscribe(self, channel: str, callback: Callable) -> bool:
        """
        取消订阅
        
        Args:
            channel: 频道名称
            callback: 回调函数
            
        Returns:
            bool: 是否成功取消
        """
        if channel in self._subscribers and callback in self._subscribers[channel]:
            self._subscribers[channel].remove(callback)
            return True
        return False
    
    async def publish(self, message: Message, async_mode: bool = True) -> None:
        """
        发布消息
        
        Args:
            message: 消息实例
            async_mode: 是否异步发布
        """
        # 保存消息历史
        if message.channel not in self._history:
            self._history[message.channel] = []
        self._history[message.channel].append(message)
        
        # 通知订阅者
        callbacks = self._subscribers.get(message.channel, [])
        
        if async_mode:
            # 异步通知所有订阅者
            await asyncio.gather(
                *[self._safe_invoke(callback, message) for callback in callbacks],
                return_exceptions=True
            )
        else:
            # 同步通知
            for callback in callbacks:
                try:
                    callback(message)
                except Exception:
                    pass  # 忽略错误，避免影响其他订阅者
    
    async def _safe_invoke(self, callback: Callable, message: Message) -> None:
        """安全调用回调"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception:
            pass
    
    def get_history(self, channel: str, limit: int = 100) -> List[Message]:
        """
        获取频道历史消息
        
        Args:
            channel: 频道名称
            limit: 最大返回数量
            
        Returns:
            List[Message]: 历史消息列表
        """
        messages = self._history.get(channel, [])
        return messages[-limit:]
    
    def clear_history(self, channel: str) -> None:
        """
        清空频道历史
        
        Args:
            channel: 频道名称
        """
        if channel in self._history:
            self._history[channel] = []
    
    def __repr__(self) -> str:
        return f"<MessageBus(channels={len(self._subscribers)})>"
