"""
消息总线单元测试
"""
import pytest
import asyncio
from datetime import datetime
from app.core.message import (
    MessageBus,
    Message,
    MessageType,
    Subscription,
    get_message_bus,
    reset_message_bus,
)


@pytest.fixture
def clean_message_bus():
    """清理消息总线"""
    reset_message_bus()
    yield
    reset_message_bus()


@pytest.fixture
def message_bus():
    """创建消息总线实例"""
    return MessageBus()


class TestMessageType:
    """测试消息类型枚举"""

    def test_message_type_values(self):
        """测试消息类型枚举值"""
        assert MessageType.TASK_ASSIGN.value == "task_assign"
        assert MessageType.TASK_HANDOFF.value == "task_handoff"
        assert MessageType.STATUS_UPDATE.value == "status_update"
        assert MessageType.REQUEST_HELP.value == "request_help"
        assert MessageType.PROVIDE_RESULT.value == "provide_result"
        assert MessageType.NOTIFICATION.value == "notification"


class TestMessage:
    """测试消息数据结构"""

    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(
            content="Test message",
            project_id="project-1",
            message_type=MessageType.NOTIFICATION,
        )

        assert msg.content == "Test message"
        assert msg.project_id == "project-1"
        assert msg.message_type == MessageType.NOTIFICATION
        assert msg.sender_id is None
        assert msg.receiver_id is None
        assert msg.id.startswith("msg_")

    def test_message_with_sender_receiver(self):
        """测试带发送者和接收者的消息"""
        msg = Message(
            content="Test",
            project_id="project-1",
            sender_id="agent-1",
            receiver_id="agent-2",
        )

        assert msg.sender_id == "agent-1"
        assert msg.receiver_id == "agent-2"

    def test_message_with_metadata(self):
        """测试带元数据的消息"""
        msg = Message(
            content="Test",
            project_id="project-1",
            metadata={"key": "value"},
        )

        assert msg.metadata["key"] == "value"

    def test_message_default_type(self):
        """测试默认消息类型"""
        msg = Message(
            content="Test",
            project_id="project-1",
        )

        assert msg.message_type == MessageType.NOTIFICATION


class TestMessageBus:
    """测试消息总线"""

    def test_subscribe(self, message_bus):
        """测试订阅"""
        def callback(msg):
            pass

        message_bus.subscribe("project-1", callback)

        count = message_bus.get_subscription_count("project-1")
        assert count == 1

    def test_subscribe_with_message_types(self, message_bus):
        """测试带类型过滤的订阅"""
        received = []

        def callback(msg):
            received.append(msg)

        message_bus.subscribe(
            "project-1",
            callback,
            message_types=[MessageType.TASK_ASSIGN],
        )

        # 发送匹配类型的消息
        message_bus.publish_sync(Message(
            content="Test",
            project_id="project-1",
            message_type=MessageType.TASK_ASSIGN,
        ))

        # 发送不匹配类型的消息
        message_bus.publish_sync(Message(
            content="Test",
            project_id="project-1",
            message_type=MessageType.NOTIFICATION,
        ))

        assert len(received) == 1
        assert received[0].message_type == MessageType.TASK_ASSIGN

    def test_subscribe_with_agent_id(self, message_bus):
        """测试带 Agent ID 过滤的订阅"""
        received = []

        def callback(msg):
            received.append(msg)

        message_bus.subscribe(
            "project-1",
            callback,
            agent_id="agent-1",
        )

        # 广播消息应该被接收
        message_bus.publish_sync(Message(
            content="Broadcast",
            project_id="project-1",
        ))

        # 明确发给该 Agent 的消息应该被接收
        message_bus.publish_sync(Message(
            content="Direct",
            project_id="project-1",
            receiver_id="agent-1",
        ))

        # 发给其他 Agent 的消息不应该被接收
        message_bus.publish_sync(Message(
            content="Other",
            project_id="project-1",
            receiver_id="agent-2",
        ))

        assert len(received) == 2

    def test_unsubscribe(self, message_bus):
        """测试取消订阅"""
        def callback(msg):
            pass

        message_bus.subscribe("project-1", callback)
        message_bus.unsubscribe("project-1", callback)

        count = message_bus.get_subscription_count("project-1")
        assert count == 0

    def test_publish_sync(self, message_bus):
        """测试同步发布"""
        received = []

        def callback(msg):
            received.append(msg)

        message_bus.subscribe("project-1", callback)

        message_bus.publish_sync(Message(
            content="Test",
            project_id="project-1",
        ))

        assert len(received) == 1
        assert received[0].content == "Test"

    @pytest.mark.asyncio
    async def test_publish_async(self, message_bus):
        """测试异步发布"""
        received = []

        async def callback(msg):
            received.append(msg)

        message_bus.subscribe("project-1", callback)

        await message_bus.publish(Message(
            content="Test",
            project_id="project-1",
        ))

        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_publish_to_multiple_subscribers(self, message_bus):
        """测试发布给多个订阅者"""
        received1 = []
        received2 = []

        message_bus.subscribe("project-1", lambda msg: received1.append(msg))
        message_bus.subscribe("project-1", lambda msg: received2.append(msg))

        await message_bus.publish(Message(
            content="Test",
            project_id="project-1",
        ))

        assert len(received1) == 1
        assert len(received2) == 1

    def test_publish_to_different_projects(self, message_bus):
        """测试发布到不同项目"""
        received1 = []
        received2 = []

        message_bus.subscribe("project-1", lambda msg: received1.append(msg))
        message_bus.subscribe("project-2", lambda msg: received2.append(msg))

        message_bus.publish_sync(Message(
            content="Test 1",
            project_id="project-1",
        ))
        message_bus.publish_sync(Message(
            content="Test 2",
            project_id="project-2",
        ))

        assert len(received1) == 1
        assert len(received2) == 1
        assert received1[0].content == "Test 1"
        assert received2[0].content == "Test 2"

    def test_get_history(self, message_bus):
        """测试获取历史消息"""
        message_bus.publish_sync(Message(
            content="Message 1",
            project_id="project-1",
        ))
        message_bus.publish_sync(Message(
            content="Message 2",
            project_id="project-1",
        ))
        message_bus.publish_sync(Message(
            content="Message 3",
            project_id="project-1",
        ))

        history = message_bus.get_history("project-1")

        # 应该按时间倒序
        assert len(history) == 3
        assert history[0].content == "Message 3"
        assert history[1].content == "Message 2"
        assert history[2].content == "Message 1"

    def test_get_history_with_limit(self, message_bus):
        """测试获取带限制的历史消息"""
        for i in range(10):
            message_bus.publish_sync(Message(
                content=f"Message {i}",
                project_id="project-1",
            ))

        history = message_bus.get_history("project-1", limit=5)

        assert len(history) == 5
        assert history[0].content == "Message 9"

    def test_get_history_with_type_filter(self, message_bus):
        """测试获取带类型过滤的历史消息"""
        message_bus.publish_sync(Message(
            content="Notification",
            project_id="project-1",
            message_type=MessageType.NOTIFICATION,
        ))
        message_bus.publish_sync(Message(
            content="Task Assign",
            project_id="project-1",
            message_type=MessageType.TASK_ASSIGN,
        ))

        history = message_bus.get_history(
            "project-1",
            message_type=MessageType.TASK_ASSIGN,
        )

        assert len(history) == 1
        assert history[0].message_type == MessageType.TASK_ASSIGN

    def test_clear_history(self, message_bus):
        """测试清空历史"""
        message_bus.publish_sync(Message(
            content="Test",
            project_id="project-1",
        ))

        message_bus.clear_history("project-1")

        history = message_bus.get_history("project-1")
        assert len(history) == 0

    def test_callback_error_handling(self, message_bus):
        """测试回调错误处理"""
        def good_callback(msg):
            pass

        def bad_callback(msg):
            raise Exception("Test error")

        message_bus.subscribe("project-1", good_callback)
        message_bus.subscribe("project-1", bad_callback)

        # 不应该抛出异常
        message_bus.publish_sync(Message(
            content="Test",
            project_id="project-1",
        ))

        # good_callback 应该仍然收到消息
        # （这个测试主要是确保 bad_callback 不会阻止其他订阅者）

    def test_subscription_count(self, message_bus):
        """测试订阅者数量"""
        assert message_bus.get_subscription_count("project-1") == 0

        message_bus.subscribe("project-1", lambda msg: None)
        message_bus.subscribe("project-1", lambda msg: None)

        assert message_bus.get_subscription_count("project-1") == 2

        message_bus.subscribe("project-2", lambda msg: None)
        assert message_bus.get_subscription_count("project-2") == 1


class TestSubscription:
    """测试订阅配置"""

    def test_subscription_creation(self):
        """测试订阅创建"""
        def callback(msg):
            pass

        sub = Subscription(callback=callback)

        assert sub.callback is callback
        assert sub.message_types is None
        assert sub.agent_id is None

    def test_subscription_with_filters(self):
        """测试带过滤器的订阅"""
        def callback(msg):
            pass

        sub = Subscription(
            callback=callback,
            message_types=[MessageType.TASK_ASSIGN],
            agent_id="agent-1",
        )

        assert sub.message_types == [MessageType.TASK_ASSIGN]
        assert sub.agent_id == "agent-1"


class TestGlobalMessageBus:
    """测试全局消息总线"""

    def test_get_message_bus_singleton(self, clean_message_bus):
        """测试单例"""
        bus1 = get_message_bus()
        bus2 = get_message_bus()

        assert bus1 is bus2

    def test_reset_message_bus(self, clean_message_bus):
        """测试重置"""
        bus1 = get_message_bus()
        reset_message_bus()
        bus2 = get_message_bus()

        assert bus1 is not bus2


class TestMessageBusIntegration:
    """测试消息总线集成"""

    @pytest.mark.asyncio
    async def test_full_publish_subscribe_cycle(self, message_bus):
        """测试完整的发布订阅流程"""
        received_messages = []

        def on_message(msg):
            received_messages.append(msg)

        # 订阅
        message_bus.subscribe(
            "project-1",
            on_message,
            message_types=[MessageType.TASK_ASSIGN, MessageType.TASK_HANDOFF],
        )

        # 发布多种类型的消息
        message_bus.publish_sync(Message(
            content="Task assigned",
            project_id="project-1",
            message_type=MessageType.TASK_ASSIGN,
        ))

        message_bus.publish_sync(Message(
            content="Task handoff",
            project_id="project-1",
            message_type=MessageType.TASK_HANDOFF,
        ))

        message_bus.publish_sync(Message(
            content="Notification",
            project_id="project-1",
            message_type=MessageType.NOTIFICATION,
        ))

        # 只应该收到匹配类型的消息
        assert len(received_messages) == 2
        assert all(
            m.message_type in [MessageType.TASK_ASSIGN, MessageType.TASK_HANDOFF]
            for m in received_messages
        )

    def test_project_isolation(self, message_bus):
        """测试项目隔离"""
        messages_project1 = []
        messages_project2 = []

        message_bus.subscribe("project-1", lambda msg: messages_project1.append(msg))
        message_bus.subscribe("project-2", lambda msg: messages_project2.append(msg))

        message_bus.publish_sync(Message(
            content="For project 1",
            project_id="project-1",
        ))
        message_bus.publish_sync(Message(
            content="For project 2",
            project_id="project-2",
        ))

        assert len(messages_project1) == 1
        assert len(messages_project2) == 1
        assert messages_project1[0].content == "For project 1"
        assert messages_project2[0].content == "For project 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
