"""
消息总线模块

实现 Agent 间通信的消息总线，支持按项目分频道、发布订阅模式。
"""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import asyncio
import uuid
import threading


class MessageType(str, Enum):
    """消息类型枚举"""
    TASK_ASSIGN = "task_assign"  # 任务分配
    TASK_HANDOFF = "task_handoff"  # 任务交接
    STATUS_UPDATE = "status_update"  # 状态更新
    REQUEST_HELP = "request_help"  # 请求帮助
    PROVIDE_RESULT = "provide_result"  # 提供结果
    NOTIFICATION = "notification"  # 通知


@dataclass
class Message:
    """
    消息数据结构

    Attributes:
        id: 消息唯一标识
        project_id: 项目 ID（消息频道）
        sender_id: 发送者 Agent ID
        receiver_id: 接收者 Agent ID（None 表示广播）
        message_type: 消息类型
        content: 消息内容
        metadata: 附加元数据
        created_at: 创建时间
    """
    content: str
    project_id: str
    message_type: MessageType = MessageType.NOTIFICATION
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Subscription:
    """订阅配置"""
    callback: Callable[[Message], None]
    message_types: Optional[list[MessageType]] = None  # None 表示接收所有类型
    agent_id: Optional[str] = None  # 仅接收发给自己的消息


class MessageBus:
    """
    消息总线实现

    功能:
    - 按项目分频道隔离消息
    - 支持发布/订阅模式
    - 支持点对点和广播消息
    - 异步消息处理支持
    """

    def __init__(self):
        # project_id -> list[Subscription]
        self._subscriptions: dict[str, list[Subscription]] = defaultdict(list)
        # project_id -> list[Message]
        self._message_history: dict[str, list[Message]] = defaultdict(list)
        self._async_lock = asyncio.Lock()
        self._sync_lock = threading.Lock()

    def subscribe(
        self,
        project_id: str,
        callback: Callable[[Message], None],
        message_types: Optional[list[MessageType]] = None,
        agent_id: Optional[str] = None,
    ) -> None:
        """
        订阅项目频道的消息

        Args:
            project_id: 项目 ID
            callback: 消息回调函数
            message_types: 感兴趣的消息类型列表，None 表示所有类型
            agent_id: Agent ID，用于过滤点对点消息
        """
        subscription = Subscription(
            callback=callback,
            message_types=message_types,
            agent_id=agent_id,
        )
        self._subscriptions[project_id].append(subscription)

    def unsubscribe(
        self,
        project_id: str,
        callback: Callable[[Message], None],
    ) -> None:
        """取消订阅"""
        if project_id in self._subscriptions:
            self._subscriptions[project_id] = [
                sub for sub in self._subscriptions[project_id]
                if sub.callback != callback
            ]

    async def publish(self, message: Message) -> None:
        """
        发布消息到项目频道

        Args:
            message: 要发布的消息
        """
        async with self._async_lock:
            # 记录消息历史
            self._message_history[message.project_id].append(message)

            # 获取该项目的订阅者
            subscriptions = self._subscriptions.get(message.project_id, [])

            # 分发消息给订阅者
            for subscription in subscriptions:
                if self._should_deliver(message, subscription):
                    try:
                        if asyncio.iscoroutinefunction(subscription.callback):
                            await subscription.callback(message)
                        else:
                            subscription.callback(message)
                    except Exception as e:
                        # 记录错误但不中断其他订阅者的接收
                        print(f"Error delivering message to subscriber: {e}")

    def publish_sync(self, message: Message) -> None:
        """
        同步发布消息（用于非异步上下文）

        Args:
            message: 要发布的消息
        """
        with self._sync_lock:
            # 记录消息历史
            self._message_history[message.project_id].append(message)

            # 获取该项目的订阅者
            subscriptions = self._subscriptions.get(message.project_id, [])

            # 分发消息给订阅者
            for subscription in subscriptions:
                if self._should_deliver(message, subscription):
                    try:
                        subscription.callback(message)
                    except Exception as e:
                        print(f"Error delivering message to subscriber: {e}")

    def _should_deliver(self, message: Message, subscription: Subscription) -> bool:
        """检查消息是否应该投递给订阅者"""
        # 检查消息类型过滤
        if subscription.message_types is not None:
            if message.message_type not in subscription.message_types:
                return False

        # 检查接收者过滤
        if subscription.agent_id is not None:
            # 广播消息或明确发给该 Agent 的消息
            if message.receiver_id is not None and message.receiver_id != subscription.agent_id:
                return False

        return True

    def get_history(
        self,
        project_id: str,
        limit: int = 100,
        message_type: Optional[MessageType] = None,
    ) -> list[Message]:
        """
        获取项目消息历史

        Args:
            project_id: 项目 ID
            limit: 最大返回数量
            message_type: 按类型过滤，None 表示不过滤

        Returns:
            消息列表，按时间倒序
        """
        history = self._message_history.get(project_id, [])
        if message_type is not None:
            history = [m for m in history if m.message_type == message_type]
        return list(reversed(history[-limit:]))

    def clear_history(self, project_id: str) -> None:
        """清空项目消息历史"""
        if project_id in self._message_history:
            self._message_history[project_id] = []

    def get_subscription_count(self, project_id: str) -> int:
        """获取项目订阅者数量"""
        return len(self._subscriptions.get(project_id, []))


# 全局消息总线实例
_message_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """获取全局消息总线实例"""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus


def reset_message_bus() -> None:
    """重置全局消息总线（用于测试）"""
    global _message_bus
    _message_bus = None
