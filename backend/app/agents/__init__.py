"""
天工工作流引擎 - 8 个预置 Agent

包含：
- ProjectManagerAgent: 项目经理
- ResearcherAgent: 研究员
- CoderAgent: 程序员
- DesignerAgent: 设计师
- WriterAgent: 文案
- ReviewerAgent: 审核员
- DataAnalystAgent: 数据分析师
- KnowledgeManagerAgent: 知识管理员
"""
from .project_manager import ProjectManagerAgent
from .researcher import ResearcherAgent
from .coder import CoderAgent
from .designer import DesignerAgent
from .writer import WriterAgent
from .reviewer import ReviewerAgent
from .data_analyst import DataAnalystAgent
from .knowledge_manager import KnowledgeManagerAgent

__all__ = [
    "ProjectManagerAgent",
    "ResearcherAgent",
    "CoderAgent",
    "DesignerAgent",
    "WriterAgent",
    "ReviewerAgent",
    "DataAnalystAgent",
    "KnowledgeManagerAgent",
]
