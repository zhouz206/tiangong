"""
数据库模型单元测试

测试所有模型的基本功能、关系和约束。
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, database
from app.models import (
    User, Workspace, WorkspaceMember, MemberRole,
    Project, ProjectStatus, ProjectPhase,
    Task, TaskStatus, TaskPriority,
    Agent, AgentStatus, AgentRole,
    ModelConfig, ModelProvider,
    KnowledgeDocument, KnowledgeType, SourceType,
    AuditLog, ActorType,
    AgentMessage, MessageType,
)


def create_user(email="test@example.com", name="测试用户", **kwargs):
    """创建用户对象的辅助函数"""
    user = User()
    user.email = email
    user.name = name
    user.hashed_password = kwargs.get("hashed_password", "password_hash")
    user.is_active = kwargs.get("is_active", True)
    user.is_superuser = kwargs.get("is_superuser", False)
    return user


def create_workspace(name="测试工作空间", owner_id=None, **kwargs):
    """创建工作空间对象的辅助函数"""
    ws = Workspace()
    ws.name = name
    ws.description = kwargs.get("description")
    ws.owner_id = owner_id
    ws.slug = kwargs.get("slug", "test-slug")
    ws.is_active = kwargs.get("is_active", True)
    return ws


def create_project(name="测试项目", workspace_id=None, owner_id=None, **kwargs):
    """创建项目对象的辅助函数"""
    proj = Project()
    proj.name = name
    proj.description = kwargs.get("description")
    proj.workspace_id = workspace_id
    proj.owner_id = owner_id
    proj.status = kwargs.get("status", ProjectStatus.ACTIVE)
    proj.current_phase = kwargs.get("current_phase", ProjectPhase.PLANNING)
    return proj


def create_task(title="测试任务", project_id=None, **kwargs):
    """创建任务对象的辅助函数"""
    task = Task()
    task.title = title
    task.description = kwargs.get("description")
    task.project_id = project_id
    task.status = kwargs.get("status", TaskStatus.PENDING)
    task.priority = kwargs.get("priority", TaskPriority.MEDIUM)
    return task


def create_agent(name="测试 Agent", workspace_id=None, **kwargs):
    """创建 Agent 对象的辅助函数"""
    agent = Agent()
    agent.name = name
    agent.role = kwargs.get("role", AgentRole.PROGRAMMER)
    agent.workspace_id = workspace_id
    agent.project_id = kwargs.get("project_id")
    agent.system_prompt = kwargs.get("system_prompt", "测试系统提示")
    agent.status = kwargs.get("status", AgentStatus.ACTIVE)
    return agent


def create_model_config(name="测试配置", workspace_id=None, **kwargs):
    """创建模型配置对象的辅助函数"""
    config = ModelConfig()
    config.name = name
    config.workspace_id = workspace_id
    config.provider = kwargs.get("provider", ModelProvider.OPENAI)
    config.model_name = kwargs.get("model_name", "gpt-4")
    return config


def create_knowledge_doc(title="测试文档", workspace_id=None, created_by=None, **kwargs):
    """创建知识文档对象的辅助函数"""
    doc = KnowledgeDocument()
    doc.title = title
    doc.content = kwargs.get("content", "测试内容")
    doc.workspace_id = workspace_id
    doc.type = kwargs.get("type", KnowledgeType.DOC)
    doc.source_type = kwargs.get("source_type", SourceType.MANUAL)
    doc.created_by = created_by
    return doc


def create_audit_log(workspace_id=None, action="create", **kwargs):
    """创建审计日志对象的辅助函数"""
    log = AuditLog()
    log.workspace_id = workspace_id
    log.action = action
    log.resource_type = kwargs.get("resource_type", "test")
    log.resource_id = kwargs.get("resource_id", "test_123")
    log.actor_id = kwargs.get("actor_id")
    log.actor_type = kwargs.get("actor_type")
    return log


def create_agent_message(project_id=None, sender_agent_id=None, **kwargs):
    """创建 Agent 消息对象的辅助函数"""
    msg = AgentMessage()
    msg.project_id = project_id
    msg.sender_agent_id = sender_agent_id
    msg.content = kwargs.get("content", "测试消息")
    msg.message_type = kwargs.get("message_type", MessageType.DISCUSSION)
    return msg


@pytest.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    # 删除所有表并重新创建
    await database.drop_tables()
    await database.create_tables()
    
    async with database.async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    """创建测试用户"""
    user = create_user()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def test_workspace(db_session: AsyncSession, test_user: User):
    """创建测试工作空间"""
    workspace = create_workspace(owner_id=test_user.id, slug="test-workspace")
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


@pytest.fixture(scope="function")
async def test_project(db_session: AsyncSession, test_workspace: Workspace, test_user: User):
    """创建测试项目"""
    project = create_project(workspace_id=test_workspace.id, owner_id=test_user.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


class TestUser:
    """User 模型测试"""
    
    async def test_create_user(self, db_session: AsyncSession):
        """测试创建用户"""
        user = create_user(email="newuser@example.com", name="新用户")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.email == "newuser@example.com"
        assert user.name == "新用户"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.id is not None
    
    async def test_user_unique_email(self, db_session: AsyncSession):
        """测试邮箱唯一性"""
        user1 = create_user(email="unique@example.com")
        db_session.add(user1)
        await db_session.commit()
        
        # 尝试创建重复邮箱的用户应该失败
        user2 = create_user(email="unique@example.com", name="用户 2")
        db_session.add(user2)
        
        with pytest.raises(Exception):
            await db_session.commit()
    
    async def test_user_repr(self, test_user: User):
        """测试用户字符串表示"""
        assert f"User(id={test_user.id}" in repr(test_user)
        assert "test@example.com" in repr(test_user)


class TestWorkspace:
    """Workspace 模型测试"""
    
    async def test_create_workspace(self, db_session: AsyncSession, test_user: User):
        """测试创建工作空间"""
        workspace = create_workspace(name="新工作空间", owner_id=test_user.id, slug="new-workspace")
        db_session.add(workspace)
        await db_session.commit()
        await db_session.refresh(workspace)
        
        assert workspace.name == "新工作空间"
        assert workspace.owner_id == test_user.id
        assert workspace.is_active is True
    
    async def test_workspace_unique_slug(self, db_session: AsyncSession, test_user: User):
        """测试 slug 唯一性"""
        ws1 = create_workspace(name="工作空间 1", owner_id=test_user.id, slug="unique-slug")
        db_session.add(ws1)
        await db_session.commit()
        
        ws2 = create_workspace(name="工作空间 2", owner_id=test_user.id, slug="unique-slug")
        db_session.add(ws2)
        
        with pytest.raises(Exception):
            await db_session.commit()
    
    async def test_workspace_owner_relationship(self, test_workspace: Workspace, test_user: User):
        """测试工作空间所有者关系"""
        assert test_workspace.owner.id == test_user.id
        assert len(test_user.workspaces) > 0
        assert test_user.workspaces[0].id == test_workspace.id


class TestWorkspaceMember:
    """WorkspaceMember 模型测试"""
    
    async def test_create_member(self, db_session: AsyncSession, test_workspace: Workspace, test_user: User):
        """测试创建成员"""
        member = WorkspaceMember()
        member.workspace_id = test_workspace.id
        member.user_id = test_user.id
        member.role = MemberRole.COLLABORATOR
        db_session.add(member)
        await db_session.commit()
        await db_session.refresh(member)
        
        assert member.role == MemberRole.COLLABORATOR
        assert member.is_active is True
    
    async def test_member_unique_constraint(self, db_session: AsyncSession, test_workspace: Workspace, test_user: User):
        """测试成员唯一约束"""
        member1 = WorkspaceMember()
        member1.workspace_id = test_workspace.id
        member1.user_id = test_user.id
        member1.role = MemberRole.OBSERVER
        db_session.add(member1)
        await db_session.commit()
        
        # 尝试创建重复的成员关系应该失败
        member2 = WorkspaceMember()
        member2.workspace_id = test_workspace.id
        member2.user_id = test_user.id
        member2.role = MemberRole.COLLABORATOR
        db_session.add(member2)
        
        with pytest.raises(Exception):
            await db_session.commit()
    
    async def test_has_permission(self):
        """测试权限检查"""
        owner = WorkspaceMember()
        owner.role = MemberRole.OWNER
        assert owner.has_permission("read") is True
        assert owner.has_permission("write") is True
        assert owner.has_permission("delete") is True
        assert owner.has_permission("admin") is True
        
        collaborator = WorkspaceMember()
        collaborator.role = MemberRole.COLLABORATOR
        assert collaborator.has_permission("read") is True
        assert collaborator.has_permission("write") is True
        assert collaborator.has_permission("delete") is False
        
        observer = WorkspaceMember()
        observer.role = MemberRole.OBSERVER
        assert observer.has_permission("read") is True
        assert observer.has_permission("write") is False


class TestProject:
    """Project 模型测试"""
    
    async def test_create_project(self, db_session: AsyncSession, test_workspace: Workspace, test_user: User):
        """测试创建项目"""
        project = create_project(name="测试项目", workspace_id=test_workspace.id, owner_id=test_user.id)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        assert project.name == "测试项目"
        assert project.status == ProjectStatus.ACTIVE
        assert project.current_phase == ProjectPhase.PLANNING
    
    async def test_project_phase_transition(self, test_workspace: Workspace, test_user: User):
        """测试项目阶段转换"""
        project = create_project(workspace_id=test_workspace.id, owner_id=test_user.id, current_phase=ProjectPhase.PLANNING)
        
        # 规划 -> 执行 (合法)
        assert project.can_transition_to(ProjectPhase.EXECUTING) is True
        
        # 规划 -> 审查 (非法)
        assert project.can_transition_to(ProjectPhase.REVIEWING) is False
        
        # 完成阶段不可逆
        project.current_phase = ProjectPhase.COMPLETED
        assert project.can_transition_to(ProjectPhase.PLANNING) is False
    
    async def test_project_relationships(self, test_project: Project, test_workspace: Workspace):
        """测试项目关系"""
        assert test_project.workspace.id == test_workspace.id
        assert len(test_workspace.projects) > 0
        assert test_workspace.projects[0].id == test_project.id


class TestTask:
    """Task 模型测试"""
    
    async def test_create_task(self, db_session: AsyncSession, test_project: Project):
        """测试创建任务"""
        task = create_task(title="测试任务", project_id=test_project.id, priority=TaskPriority.HIGH)
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)
        
        assert task.title == "测试任务"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
    
    async def test_task_dependency(self, db_session: AsyncSession, test_project: Project):
        """测试任务依赖关系"""
        task1 = create_task(title="上游任务", project_id=test_project.id)
        db_session.add(task1)
        await db_session.commit()
        
        task2 = create_task(title="下游任务", project_id=test_project.id, upstream_task_id=task1.id)
        db_session.add(task2)
        await db_session.commit()
        await db_session.refresh(task2)
        
        assert task2.upstream_task_id == task1.id
        assert task2.is_blocked() is True
        
        # 完成上游任务后，下游任务不再被阻塞
        task1.status = TaskStatus.COMPLETED
        await db_session.commit()
        await db_session.refresh(task2)
        
        assert task2.is_blocked() is False
        assert task2.can_start() is True


class TestAgent:
    """Agent 模型测试"""
    
    async def test_create_agent(self, db_session: AsyncSession, test_workspace: Workspace):
        """测试创建 Agent"""
        agent = create_agent(name="项目经理", workspace_id=test_workspace.id, role=AgentRole.MANAGER, system_prompt="你是一位项目经理")
        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)
        
        assert agent.name == "项目经理"
        assert agent.role == AgentRole.MANAGER
        assert agent.status == AgentStatus.ACTIVE
        assert agent.temperature == 0.7
        assert agent.max_tokens == 2048
    
    async def test_agent_can_accept_task(self, test_workspace: Workspace):
        """测试 Agent 任务接受能力"""
        agent = create_agent(workspace_id=test_workspace.id)
        
        # 活跃且无当前任务时可以接受
        assert agent.can_accept_task() is True
        
        # 忙碌时不能接受
        agent.status = AgentStatus.BUSY
        assert agent.can_accept_task() is False
        
        # 非活跃时不能接受
        agent.status = AgentStatus.ACTIVE
        agent.current_task_id = "task_123"
        assert agent.can_accept_task() is False
    
    async def test_agent_skills_management(self, test_workspace: Workspace):
        """测试 Agent 技能管理"""
        agent = create_agent(workspace_id=test_workspace.id, skills=["code_review"])
        
        agent.add_skill("unit_testing")
        assert "unit_testing" in agent.skills
        
        agent.remove_skill("code_review")
        assert "code_review" not in agent.skills


class TestModelConfig:
    """ModelConfig 模型测试"""
    
    async def test_create_model_config(self, db_session: AsyncSession, test_workspace: Workspace):
        """测试创建模型配置"""
        config = create_model_config(name="GPT-4 配置", workspace_id=test_workspace.id, model_name="gpt-4")
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        
        assert config.provider == ModelProvider.OPENAI
        assert config.is_active is True
        assert config.is_offline is False
        assert config.priority == 1
    
    async def test_fallback_management(self, test_workspace: Workspace):
        """测试降级模型管理"""
        config = create_model_config(workspace_id=test_workspace.id)
        
        config.add_fallback("model_1")
        config.add_fallback("model_2")
        assert len(config.fallback_model_ids) == 2
        
        config.remove_fallback("model_1")
        assert len(config.fallback_model_ids) == 1


class TestKnowledgeDocument:
    """KnowledgeDocument 模型测试"""
    
    async def test_create_knowledge_document(self, db_session: AsyncSession, test_workspace: Workspace, test_user: User):
        """测试创建知识文档"""
        doc = create_knowledge_doc(title="测试文档", workspace_id=test_workspace.id, created_by=test_user.id)
        db_session.add(doc)
        await db_session.commit()
        await db_session.refresh(doc)
        
        assert doc.type == KnowledgeType.DOC
        assert doc.tags == []
    
    async def test_tag_management(self, test_workspace: Workspace, test_user: User):
        """测试标签管理"""
        doc = create_knowledge_doc(workspace_id=test_workspace.id, created_by=test_user.id)
        
        doc.add_tag("python")
        doc.add_tag("tutorial")
        assert "python" in doc.tags
        assert "tutorial" in doc.tags
        
        doc.remove_tag("python")
        assert "python" not in doc.tags


class TestAuditLog:
    """AuditLog 模型测试"""
    
    async def test_create_audit_log(self, db_session: AsyncSession, test_workspace: Workspace, test_user: User):
        """测试创建审计日志"""
        log = create_audit_log(
            workspace_id=test_workspace.id,
            action="create",
            resource_type="project",
            resource_id="project_123",
            actor_id=test_user.id,
            actor_type=ActorType.USER,
            after={"name": "新项目"},
        )
        db_session.add(log)
        await db_session.commit()
        await db_session.refresh(log)
        
        assert log.action == "create"
        assert log.actor_id == test_user.id
        assert log.actor_type == ActorType.USER
    
    async def test_audit_log_no_soft_delete(self, test_workspace: Workspace, test_user: User):
        """测试审计日志不支持软删除"""
        # AuditLog 不应该有 deleted_at 字段
        log = create_audit_log(workspace_id=test_workspace.id)
        assert not hasattr(log, 'deleted_at')


class TestAgentMessage:
    """AgentMessage 模型测试"""
    
    async def test_create_message(self, db_session: AsyncSession, test_project: Project, test_workspace: Workspace):
        """测试创建 Agent 消息"""
        agent = create_agent(workspace_id=test_workspace.id)
        db_session.add(agent)
        await db_session.commit()
        
        message = create_agent_message(project_id=test_project.id, sender_agent_id=agent.id)
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)
        
        assert message.message_type == MessageType.DISCUSSION
        assert message.is_private is False
        assert message.is_read is False
    
    async def test_message_read_status(self, test_project: Project, test_workspace: Workspace):
        """测试消息已读状态"""
        agent = create_agent(workspace_id=test_workspace.id)
        
        message = create_agent_message(project_id=test_project.id, sender_agent_id=agent.id)
        
        assert message.is_read is False
        assert message.read_at is None
        
        message.mark_as_read()
        assert message.is_read is True
        assert message.read_at is not None
    
    async def test_message_reply(self, test_project: Project, test_workspace: Workspace):
        """测试消息回复"""
        agent = create_agent(workspace_id=test_workspace.id)
        
        parent = create_agent_message(project_id=test_project.id, sender_agent_id=agent.id, content="父消息")
        
        reply = create_agent_message(project_id=test_project.id, sender_agent_id=agent.id, content="回复消息", parent_message_id=parent.id)
        
        assert reply.is_reply() is True
        assert parent.is_reply() is False


class TestSoftDelete:
    """软删除功能测试"""
    
    async def test_soft_delete_user(self, db_session: AsyncSession, test_user: User):
        """测试用户软删除"""
        assert test_user.deleted_at is None
        
        test_user.deleted_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(test_user)
        
        assert test_user.deleted_at is not None
    
    async def test_soft_delete_workspace(self, db_session: AsyncSession, test_workspace: Workspace):
        """测试工作空间软删除"""
        assert test_workspace.deleted_at is None
        
        test_workspace.deleted_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(test_workspace)
        
        assert test_workspace.deleted_at is not None


class TestTimestamps:
    """时间戳功能测试"""
    
    async def test_auto_created_at(self, db_session: AsyncSession):
        """测试自动创建时间"""
        user = create_user(email="timestamp@example.com")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
    
    async def test_auto_updated_at(self, db_session: AsyncSession, test_workspace: Workspace):
        """测试自动更新时间"""
        original_updated = test_workspace.updated_at
        
        await asyncio.sleep(0.1)  # 等待一小段时间
        
        test_workspace.name = "更新后的名称"
        await db_session.commit()
        await db_session.refresh(test_workspace)
        
        assert test_workspace.updated_at >= original_updated


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
