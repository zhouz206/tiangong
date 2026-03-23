"""
自动归档系统

实现基于规则的文档自动归档功能。
"""
from typing import Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from .models import (
    KnowledgeDocument,
    DocumentStatus,
    ArchiveRule,
)
from .vector_store import VectorStore, vector_store


class ArchiveAction(str, Enum):
    """归档动作"""
    ARCHIVE = "archive"
    DELETE = "delete"
    NOTIFY = "notify"
    REVIEW = "review"


class AutoArchiver:
    """
    自动归档器

    根据预定义规则自动归档文档。
    """

    # 默认归档规则
    DEFAULT_RULES = [
        ArchiveRule(
            id="rule_draft_30d",
            name="草稿超 30 天未更新",
            condition_type="age_draft",
            condition_value=30,  # 天
            action=ArchiveAction.ARCHIVE,
            enabled=True,
        ),
        ArchiveRule(
            id="rule_deprecated",
            name="标记为废弃的文档",
            condition_type="status",
            condition_value="deprecated",
            action=ArchiveAction.ARCHIVE,
            enabled=True,
        ),
        ArchiveRule(
            id="rule_review_90d",
            name="审核中超 90 天未处理",
            condition_type="age_review",
            condition_value=90,
            action=ArchiveAction.NOTIFY,
            enabled=True,
        ),
    ]

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
    ):
        """
        初始化自动归档器

        Args:
            vector_store: 向量存储实例
        """
        self.vector_store = vector_store or vector_store

        # 归档规则
        self._rules: dict[str, ArchiveRule] = {
            rule.id: rule for rule in self.DEFAULT_RULES
        }

        # 归档记录
        self._archive_log: list[dict[str, Any]] = []

    def get_rules(self) -> list[ArchiveRule]:
        """获取所有归档规则"""
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> Optional[ArchiveRule]:
        """获取单个规则"""
        return self._rules.get(rule_id)

    def create_rule(
        self,
        name: str,
        condition_type: str,
        condition_value: Any,
        action: str = "archive",
        enabled: bool = True,
    ) -> ArchiveRule:
        """
        创建归档规则

        Args:
            name: 规则名称
            condition_type: 条件类型
            condition_value: 条件值
            action: 执行动作
            enabled: 是否启用

        Returns:
            创建的规则
        """
        rule_id = f"rule_{name.lower().replace(' ', '_')}"
        rule = ArchiveRule(
            id=rule_id,
            name=name,
            condition_type=condition_type,
            condition_value=condition_value,
            action=action,
            enabled=enabled,
        )
        self._rules[rule_id] = rule
        return rule

    def update_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        condition_value: Optional[Any] = None,
        action: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> bool:
        """更新规则"""
        rule = self._rules.get(rule_id)
        if not rule:
            return False

        if name:
            rule.name = name
        if condition_value is not None:
            rule.condition_value = condition_value
        if action:
            rule.action = action
        if enabled is not None:
            rule.enabled = enabled

        return True

    def delete_rule(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        return self.update_rule(rule_id, enabled=True)

    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        return self.update_rule(rule_id, enabled=False)

    def run_archival(self, dry_run: bool = False) -> dict[str, Any]:
        """
        执行归档任务

        Args:
            dry_run: 是否仅模拟执行（不实际归档）

        Returns:
            归档结果统计
        """
        now = datetime.now()
        result = {
            "total_processed": 0,
            "archived": 0,
            "deleted": 0,
            "notified": 0,
            "review_required": 0,
            "details": [],
        }

        # 获取所有文档
        documents = self.vector_store.list_documents(limit=1000)

        for doc_info in documents:
            doc_id = doc_info.get("id")
            metadata = doc_info.get("metadata", {})

            # 跳过已归档的文档
            if metadata.get("status") == DocumentStatus.ARCHIVED:
                continue

            # 检查每条规则
            for rule in self._rules.values():
                if not rule.enabled:
                    continue

                # 检查是否满足规则条件
                if self._check_condition(metadata, rule, now):
                    # 执行动作
                    action_result = self._execute_action(
                        doc_id, metadata, rule, dry_run
                    )

                    result["total_processed"] += 1
                    result["details"].append({
                        "document_id": doc_id,
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "action": rule.action,
                        "dry_run": dry_run,
                        **action_result,
                    })

                    # 统计
                    if rule.action == ArchiveAction.ARCHIVE:
                        result["archived"] += 1
                    elif rule.action == ArchiveAction.DELETE:
                        result["deleted"] += 1
                    elif rule.action == ArchiveAction.NOTIFY:
                        result["notified"] += 1
                    elif rule.action == ArchiveAction.REVIEW:
                        result["review_required"] += 1

                    # 一个文档只应用一条规则
                    break

        # 记录日志
        self._archive_log.append({
            "timestamp": now.isoformat(),
            "dry_run": dry_run,
            "result": result,
        })

        return result

    def _check_condition(
        self,
        metadata: dict[str, Any],
        rule: ArchiveRule,
        now: datetime,
    ) -> bool:
        """
        检查文档是否满足归档条件

        Args:
            metadata: 文档元数据
            rule: 归档规则
            now: 当前时间

        Returns:
            是否满足条件
        """
        condition_type = rule.condition_type
        condition_value = rule.condition_value

        try:
            if condition_type == "age_draft":
                # 草稿超期
                if metadata.get("status") != DocumentStatus.DRAFT:
                    return False
                updated_at = metadata.get("updated_at")
                if updated_at:
                    updated = datetime.fromisoformat(updated_at)
                    age_days = (now - updated).days
                    return age_days >= condition_value

            elif condition_type == "age_review":
                # 审核超期
                if metadata.get("status") != DocumentStatus.REVIEW:
                    return False
                updated_at = metadata.get("updated_at")
                if updated_at:
                    updated = datetime.fromisoformat(updated_at)
                    age_days = (now - updated).days
                    return age_days >= condition_value

            elif condition_type == "age_published":
                # 发布超期
                if metadata.get("status") != DocumentStatus.PUBLISHED:
                    return False
                updated_at = metadata.get("updated_at")
                if updated_at:
                    updated = datetime.fromisoformat(updated_at)
                    age_days = (now - updated).days
                    return age_days >= condition_value

            elif condition_type == "status":
                # 特定状态
                return metadata.get("status") == condition_value

            elif condition_type == "category":
                # 特定分类
                return metadata.get("category") == condition_value

            elif condition_type == "no_views":
                # 无访问记录
                views = metadata.get("views", 0)
                return views == 0

            elif condition_type == "age_no_update":
                # 超期未更新
                updated_at = metadata.get("updated_at")
                if updated_at:
                    updated = datetime.fromisoformat(updated_at)
                    age_days = (now - updated).days
                    return age_days >= condition_value

        except Exception as e:
            print(f"Error checking condition for rule {rule.id}: {e}")

        return False

    def _execute_action(
        self,
        doc_id: str,
        metadata: dict[str, Any],
        rule: ArchiveRule,
        dry_run: bool,
    ) -> dict[str, Any]:
        """
        执行归档动作

        Args:
            doc_id: 文档 ID
            metadata: 文档元数据
            rule: 归档规则
            dry_run: 是否模拟执行

        Returns:
            执行结果
        """
        result = {"success": False, "message": ""}

        if dry_run:
            result["success"] = True
            result["message"] = f"Would {rule.action} document {doc_id}"
            return result

        try:
            if rule.action == ArchiveAction.ARCHIVE:
                # 获取完整文档数据
                doc_data = self.vector_store.get_document(doc_id)
                if doc_data:
                    # 更新状态为已归档
                    doc_data["metadata"]["status"] = DocumentStatus.ARCHIVED
                    doc_data["metadata"]["archived_at"] = datetime.now().isoformat()
                    doc_data["metadata"]["archive_rule"] = rule.id

                    # 更新向量存储
                    self.vector_store.update_document(
                        document=KnowledgeDocument(
                            id=doc_id,
                            title=doc_data["metadata"]["title"],
                            content=doc_data["content"],
                            category=doc_data["metadata"]["category"],
                            status=DocumentStatus.ARCHIVED,
                            metadata=doc_data["metadata"],
                        ),
                        embedding=doc_data.get("embedding", []),
                    )

                    result["success"] = True
                    result["message"] = f"Archived document {doc_id}"

            elif rule.action == ArchiveAction.DELETE:
                # 删除文档
                if self.vector_store.delete_document(doc_id):
                    result["success"] = True
                    result["message"] = f"Deleted document {doc_id}"

            elif rule.action == ArchiveAction.NOTIFY:
                # 仅记录需要通知
                result["success"] = True
                result["message"] = f"Notification required for {doc_id}"

            elif rule.action == ArchiveAction.REVIEW:
                # 标记为需要审核
                result["success"] = True
                result["message"] = f"Review required for {doc_id}"

        except Exception as e:
            result["message"] = f"Error executing action: {e}"

        return result

    def get_archive_log(
        self,
        limit: int = 10,
        dry_run_only: bool = False,
    ) -> list[dict[str, Any]]:
        """
        获取归档日志

        Args:
            limit: 返回数量
            dry_run_only: 是否仅返回模拟执行记录

        Returns:
            归档日志列表
        """
        logs = self._archive_log
        if dry_run_only:
            logs = [log for log in logs if log.get("dry_run")]
        return logs[-limit:]

    def restore_document(self, doc_id: str) -> bool:
        """
        恢复已归档文档

        Args:
            doc_id: 文档 ID

        Returns:
            是否恢复成功
        """
        try:
            doc_data = self.vector_store.get_document(doc_id)
            if not doc_data:
                return False

            # 恢复状态
            doc_data["metadata"]["status"] = DocumentStatus.DRAFT
            doc_data["metadata"]["archived_at"] = None
            doc_data["metadata"].pop("archive_rule", None)

            # 更新向量存储
            self.vector_store.update_document(
                document=KnowledgeDocument(
                    id=doc_id,
                    title=doc_data["metadata"]["title"],
                    content=doc_data["content"],
                    category=doc_data["metadata"]["category"],
                    status=DocumentStatus.DRAFT,
                    metadata=doc_data["metadata"],
                ),
                embedding=doc_data.get("embedding", []),
            )

            return True
        except Exception as e:
            print(f"Error restoring document: {e}")
            return False

    def get_archive_stats(self) -> dict[str, Any]:
        """获取归档统计"""
        all_docs = self.vector_store.list_documents(limit=10000)
        archived_docs = [
            d for d in all_docs
            if d.get("metadata", {}).get("status") == DocumentStatus.ARCHIVED
        ]

        return {
            "total_documents": len(all_docs),
            "archived_documents": len(archived_docs),
            "active_documents": len(all_docs) - len(archived_docs),
            "archive_rules": len([r for r in self._rules.values() if r.enabled]),
            "last_archival": self._archive_log[-1]["timestamp"] if self._archive_log else None,
        }


# 默认自动归档器实例
auto_archiver = AutoArchiver()
