"""
Coordinator — Agent 协调器
"""
from typing import Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.agents.agent import Agent


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self._queue: List[dict] = []
    
    def add_task(self, task: dict) -> None:
        """添加任务到队列"""
        self._queue.append(task)
    
    def get_next_task(self) -> Optional[dict]:
        """获取下一个任务"""
        if self._queue:
            return self._queue.pop(0)
        return None


class Coordinator:
    """
    Agent 协调器
    
    负责任务分配、依赖管理、Agent 生命周期
    """
    
    def __init__(self, db: "Session"):
        self.db = db
        self._agents: Dict[str, "Agent"] = {}
        self._scheduler = TaskScheduler()
    
    def register_agent(self, agent_id: str, agent: "Agent") -> None:
        """注册 Agent"""
        self._agents[agent_id] = agent
    
    def unregister_agent(self, agent_id: str) -> bool:
        """注销 Agent"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional["Agent"]:
        """获取 Agent"""
        return self._agents.get(agent_id)
    
    def get_agents_by_role(self, role: str) -> List["Agent"]:
        """按角色获取 Agent"""
        return [a for a in self._agents.values() if a.role == role]
    
    def assign_task(self, agent_id: str, task: dict) -> bool:
        """分配任务给 Agent"""
        agent = self.get_agent(agent_id)
        if agent:
            self._scheduler.add_task({"agent_id": agent_id, "task": task})
            return True
        return False
    
    def __repr__(self) -> str:
        return f"<Coordinator(agents={len(self._agents)})>"
