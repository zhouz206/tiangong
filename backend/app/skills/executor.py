"""
Skill 执行器

负责 Skill 的执行调度、超时控制、错误处理和结果管理。
"""
import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .base import (
    Skill,
    SkillContext,
    SkillResult,
    SkillStatus,
    SkillRegistry,
    get_registry,
)
from .loader import SkillLoader, get_loader


@dataclass
class ExecutionRecord:
    """
    Skill 执行记录

    Attributes:
        skill_id: Skill ID
        start_time: 开始时间
        end_time: 结束时间
        duration: 执行时长（秒）
        success: 是否成功
        error: 错误信息
        context: 执行上下文快照
        result: 执行结果快照
    """
    skill_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    success: bool = False
    error: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStats:
    """
    Skill 执行统计

    Attributes:
        total_executions: 总执行次数
        successful_executions: 成功次数
        failed_executions: 失败次数
        total_duration: 总执行时长（秒）
        avg_duration: 平均执行时长（秒）
        last_execution: 最后执行时间
    """
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0
    last_execution: Optional[datetime] = None

    @property
    def avg_duration(self) -> float:
        """计算平均执行时长"""
        if self.total_executions == 0:
            return 0.0
        return self.total_duration / self.total_executions

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions


class SkillExecutionError(Exception):
    """Skill 执行错误基类"""
    pass


class SkillTimeoutError(SkillExecutionError):
    """Skill 执行超时"""
    pass


class SkillValidationError(SkillExecutionError):
    """Skill 输入验证失败"""
    pass


class SkillExecutor:
    """
    Skill 执行器

    提供 Skill 的执行、调度、超时控制和错误处理功能。

    使用示例:
        executor = SkillExecutor()
        
        # 执行 Skill
        result = await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "..."},
            metadata={"project_path": "/path/to/project"},
        )
        
        # 带超时执行
        result = await executor.execute(
            skill_id="security_scan",
            input_data={"path": "/path"},
            timeout=60,  # 60 秒超时
        )
        
        # 获取执行统计
        stats = executor.get_stats("code_analysis")
    """

    def __init__(
        self,
        registry: Optional[SkillRegistry] = None,
        loader: Optional[SkillLoader] = None,
    ):
        """
        初始化 Skill 执行器

        Args:
            registry: Skill 注册表实例
            loader: Skill 加载器实例
        """
        self.registry = registry or get_registry()
        self.loader = loader or get_loader()
        
        # 执行记录
        self._execution_history: dict[str, list[ExecutionRecord]] = {}
        # 执行统计
        self._stats: dict[str, ExecutionStats] = {}
        # 最大并发数
        self._max_concurrent = 10
        # 当前并发数
        self._current_concurrent = 0
        # 并发锁
        self._concurrency_lock = asyncio.Lock()

    async def execute(
        self,
        skill_id: str,
        input_data: Any,
        metadata: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> SkillResult:
        """
        执行 Skill

        Args:
            skill_id: Skill ID
            input_data: 输入数据
            metadata: 附加元数据
            timeout: 超时时间（秒），默认使用 Skill 的默认超时

        Returns:
            Skill 执行结果

        Raises:
            SkillExecutionError: 执行失败
            SkillTimeoutError: 执行超时
            SkillValidationError: 输入验证失败
        """
        # 获取 Skill
        skill = self.registry.get(skill_id)
        if not skill:
            # 尝试从内置加载
            try:
                skill = self.loader.load_builtin(skill_id)
            except Exception:
                raise SkillExecutionError(f"Skill not found: {skill_id}")

        # 检查是否启用
        if not self.registry.is_enabled(skill_id):
            raise SkillExecutionError(f"Skill is disabled: {skill_id}")

        # 创建上下文
        context = SkillContext(
            skill_id=skill_id,
            input_data=input_data,
            metadata=metadata or {},
            timeout=timeout or 300,
        )

        # 验证输入
        is_valid, error_msg = skill.validate_input(context)
        if not is_valid:
            raise SkillValidationError(f"Invalid input: {error_msg}")

        # 创建执行记录
        record = ExecutionRecord(
            skill_id=skill_id,
            start_time=datetime.utcnow(),
            context={
                "input_data": str(input_data)[:500],  # 截断避免过大
                "metadata": metadata,
            },
        )

        # 更新统计
        stats = self._get_or_create_stats(skill_id)
        stats.total_executions += 1

        try:
            # 执行 Skill（带超时控制）
            result = await self._execute_with_timeout(skill, context)
            
            # 记录成功
            record.success = True
            record.result = {
                "success": result.success,
                "output": str(result.output)[:500] if result.output else None,
            }
            stats.successful_executions += 1

            return result

        except SkillTimeoutError:
            record.error = "Execution timeout"
            stats.failed_executions += 1
            raise

        except SkillExecutionError as e:
            record.error = str(e)
            stats.failed_executions += 1
            raise

        except Exception as e:
            record.error = f"Unexpected error: {e}"
            stats.failed_executions += 1
            raise SkillExecutionError(f"Execution failed: {e}") from e

        finally:
            # 完成记录
            record.end_time = datetime.utcnow()
            record.duration = (record.end_time - record.start_time).total_seconds()
            stats.total_duration += record.duration
            stats.last_execution = record.end_time
            record.result["error"] = record.error
            
            # 保存执行历史
            self._save_execution_record(skill_id, record)

    async def execute_batch(
        self,
        tasks: list[dict[str, Any]],
        max_concurrent: Optional[int] = None,
    ) -> list[SkillResult]:
        """
        批量执行 Skill

        Args:
            tasks: 任务列表，每个任务包含:
                - skill_id: Skill ID
                - input_data: 输入数据
                - metadata: 元数据（可选）
                - timeout: 超时时间（可选）
            max_concurrent: 最大并发数，默认使用执行器的配置

        Returns:
            执行结果列表（按任务顺序）
        """
        concurrency = max_concurrent or self._max_concurrent
        semaphore = asyncio.Semaphore(concurrency)

        async def execute_with_semaphore(task: dict) -> SkillResult:
            async with semaphore:
                return await self.execute(**task)

        # 创建任务
        coroutines = [execute_with_semaphore(task) for task in tasks]
        
        # 并发执行（收集所有结果，包括失败的）
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # 转换异常为失败结果
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(SkillResult(
                    success=False,
                    error=str(result),
                    metadata={"task_index": i},
                ))
            else:
                final_results.append(result)

        return final_results

    async def execute_with_retry(
        self,
        skill_id: str,
        input_data: Any,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        metadata: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> SkillResult:
        """
        执行 Skill（带重试机制）

        Args:
            skill_id: Skill ID
            input_data: 输入数据
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            metadata: 附加元数据
            timeout: 超时时间（秒）

        Returns:
            Skill 执行结果
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.execute(
                    skill_id=skill_id,
                    input_data=input_data,
                    metadata=metadata,
                    timeout=timeout,
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)

        raise SkillExecutionError(
            f"Failed after {max_retries} retries: {last_error}"
        ) from last_error

    def get_stats(self, skill_id: str) -> Optional[ExecutionStats]:
        """
        获取 Skill 执行统计

        Args:
            skill_id: Skill ID

        Returns:
            执行统计，不存在返回 None
        """
        return self._stats.get(skill_id)

    def get_all_stats(self) -> dict[str, ExecutionStats]:
        """获取所有 Skill 的执行统计"""
        return dict(self._stats)

    def get_history(
        self,
        skill_id: str,
        limit: int = 10,
    ) -> list[ExecutionRecord]:
        """
        获取 Skill 执行历史

        Args:
            skill_id: Skill ID
            limit: 返回记录数量限制

        Returns:
            执行记录列表（按时间倒序）
        """
        history = self._execution_history.get(skill_id, [])
        return list(reversed(history[-limit:]))

    def clear_history(self, skill_id: Optional[str] = None) -> None:
        """
        清空执行历史

        Args:
            skill_id: Skill ID，为 None 则清空所有
        """
        if skill_id:
            self._execution_history.pop(skill_id, None)
        else:
            self._execution_history.clear()

    def reset_stats(self, skill_id: Optional[str] = None) -> None:
        """
        重置执行统计

        Args:
            skill_id: Skill ID，为 None 则重置所有
        """
        if skill_id:
            self._stats.pop(skill_id, None)
        else:
            self._stats.clear()

    def _get_or_create_stats(self, skill_id: str) -> ExecutionStats:
        """获取或创建 Skill 统计"""
        if skill_id not in self._stats:
            self._stats[skill_id] = ExecutionStats()
        return self._stats[skill_id]

    def _save_execution_record(
        self,
        skill_id: str,
        record: ExecutionRecord,
    ) -> None:
        """保存执行记录"""
        if skill_id not in self._execution_history:
            self._execution_history[skill_id] = []
        
        # 保留最近 100 条记录
        history = self._execution_history[skill_id]
        history.append(record)
        if len(history) > 100:
            history.pop(0)

    async def _execute_with_timeout(
        self,
        skill: Skill,
        context: SkillContext,
    ) -> SkillResult:
        """
        带超时控制的 Skill 执行

        Args:
            skill: Skill 实例
            context: Skill 上下文

        Returns:
            Skill 执行结果

        Raises:
            SkillTimeoutError: 执行超时
        """
        skill._before_execute()

        try:
            # 创建带超时的任务
            result = await asyncio.wait_for(
                skill.execute(context),
                timeout=context.timeout,
            )
            
            skill._after_execute(result)
            return result

        except asyncio.TimeoutError:
            skill._status = SkillStatus.FAILED
            raise SkillTimeoutError(
                f"Skill execution timeout after {context.timeout}s"
            )

        except Exception:
            skill._status = SkillStatus.FAILED
            raise


# 全局执行器实例
_executor: Optional[SkillExecutor] = None


def get_executor() -> SkillExecutor:
    """获取全局 Skill 执行器实例"""
    global _executor
    if _executor is None:
        _executor = SkillExecutor()
    return _executor


def reset_executor() -> None:
    """重置全局执行器（用于测试）"""
    global _executor
    _executor = None


async def execute_skill(
    skill_id: str,
    input_data: Any,
    metadata: Optional[dict[str, Any]] = None,
    timeout: Optional[int] = None,
) -> SkillResult:
    """便捷函数：执行 Skill"""
    return await get_executor().execute(
        skill_id=skill_id,
        input_data=input_data,
        metadata=metadata,
        timeout=timeout,
    )
