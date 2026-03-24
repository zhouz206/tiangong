"""
QualityGate — 质量门禁检查
"""
from typing import Any, Dict


class QualityGate:
    """质量门禁"""
    
    MIN_REVIEW_SCORE = 8.0
    MIN_TEST_COVERAGE = 70
    MIN_CORE_FLOWS_PASS = True
    
    def check_review_score(self, review_result: Dict[str, Any]) -> bool:
        score = review_result.get("overall_score", 0)
        return score >= self.MIN_REVIEW_SCORE
    
    def check_test_coverage(self, test_result: Dict[str, Any]) -> bool:
        coverage = test_result.get("coverage", 0)
        if coverage <= 1.0:
            coverage = coverage * 100
        return coverage >= self.MIN_TEST_COVERAGE
    
    def check_core_flows(self, qa_result: Dict[str, Any]) -> bool:
        return qa_result.get("core_flows_passed", False) is True
    
    def check_all(self, results: Dict[str, Dict]) -> Dict[str, bool]:
        checks = {"review_score": False, "test_coverage": False, "core_flows": False}
        if "review" in results:
            checks["review_score"] = self.check_review_score(results["review"])
        if "test" in results:
            checks["test_coverage"] = self.check_test_coverage(results["test"])
        if "qa" in results:
            checks["core_flows"] = self.check_core_flows(results["qa"])
        return checks
    
    def all_passed(self, checks: Dict[str, bool]) -> bool:
        return all(checks.values())
