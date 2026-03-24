"""
DataAnalystAgent — 数据分析师 Agent

职责：数据处理、可视化
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class DataAnalystAgent(Agent):
    """
    数据分析师 Agent
    
    核心能力:
    - 数据处理
    - 统计分析
    - 可视化
    """
    
    @property
    def role(self) -> str:
        return "data_analyst"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的数据分析师。

你的职责:
1. 数据处理 — 清洗、转换、整理数据
2. 统计分析 — 应用统计方法分析数据
3. 可视化 — 创建清晰的图表和仪表板

工作原则:
- 数据要准确
- 分析要有依据
- 可视化要清晰
- 结论要有洞察力
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        return TaskResult(
            success=True,
            output={
                "type": "analysis_report",
                "content": "# 数据分析完成"
            }
        )
