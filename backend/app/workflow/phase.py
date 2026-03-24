"""
Phase — 项目阶段定义
"""
import enum


class ProjectPhase(str, enum.Enum):
    """
    项目阶段枚举
    
    四阶段简化工作流:
    PLANNING → EXECUTING → REVIEWING → COMPLETED
    """
    PLANNING = "planning"      # 规划阶段
    EXECUTING = "executing"    # 执行阶段
    REVIEWING = "reviewing"    # 审查阶段
    COMPLETED = "completed"    # 完成阶段


class PhaseTransition:
    """
    阶段转换规则
    
    定义合法的状态转换
    """
    
    # 合法的状态转换
    VALID_TRANSITIONS = {
        ProjectPhase.PLANNING: {ProjectPhase.EXECUTING, ProjectPhase.PLANNING},
        ProjectPhase.EXECUTING: {ProjectPhase.REVIEWING, ProjectPhase.EXECUTING, ProjectPhase.PLANNING},
        ProjectPhase.REVIEWING: {ProjectPhase.COMPLETED, ProjectPhase.EXECUTING, ProjectPhase.REVIEWING},
        ProjectPhase.COMPLETED: {ProjectPhase.COMPLETED},  # 完成阶段不可逆
    }
    
    @classmethod
    def can_transition(cls, from_phase: ProjectPhase, to_phase: ProjectPhase) -> bool:
        """
        检查阶段转换是否合法
        
        Args:
            from_phase: 当前阶段
            to_phase: 目标阶段
            
        Returns:
            bool: 是否可以转换
        """
        valid_targets = cls.VALID_TRANSITIONS.get(from_phase, set())
        return to_phase in valid_targets
    
    @classmethod
    def get_valid_transitions(cls, phase: ProjectPhase) -> set:
        """
        获取某个阶段的所有合法转换目标
        
        Args:
            phase: 当前阶段
            
        Returns:
            set: 合法的目标阶段集合
        """
        return cls.VALID_TRANSITIONS.get(phase, set())
