# gstack 工作流指南

**基于 Garry Tan 的 gstack 工作流**  
**适用于 Claude Code**

---

## 📖 什么是 gstack

gstack 是一个结构化的 AI 协作工作流，包含 8 个阶段：

```
/office-hours → /plan-ceo-review → /plan-eng-review → Build → /review → /qa → /ship → /retro
```

每个阶段有明确的目标和输出，确保 AI 辅助开发的质量和可预测性。

---

## 🎯 gstack 8 个阶段

### 1. /office-hours — 需求澄清

**目标**: 需求澄清，明确问题

**核心活动**:
- 问 6 个 Forcing Questions
- 生成 3 个实现方案
- 选择推荐方案

**输出**: 设计文档 (design_doc)

**示例**:
```bash
/office-hours 修复前端构建失败问题
```

---

### 2. /plan-ceo-review — 产品审视

**目标**: 产品审视，范围决策

**核心活动**:
- 10 项产品审视
- 范围决策 (Selective Expansion)
- 工程规划

**输出**: CEO Review 报告 + 工程规划文档

**示例**:
```bash
/plan-ceo-review 制定前端测试修复方案
```

---

### 3. /plan-eng-review — 工程规划

**目标**: 工程技术规划

**核心活动**:
- 目录结构设计
- 核心类设计
- 工作流程定义

**输出**: 工程规划文档

**示例**:
```bash
/plan-eng-review 设计 vitest 配置分离方案
```

---

### 4. Build — 代码实现 ⛔ 墨菲斯不写

**目标**: 代码实现

**核心活动**:
- 按规划实现功能
- 编写单元测试
- 保持代码质量

**输出**: 可工作的代码 + 测试

**执行者**: Claude Code (不是墨菲斯)

---

### 5. /review — 代码审查

**目标**: 代码审查

**核心活动**:
- 5 维度代码审查
- 自动修复建议
- 质量评分

**输出**: 审查报告 (review_report)

**审查维度**:
| 维度 | 权重 |
|------|------|
| 代码规范 | 20% |
| 设计模式 | 20% |
| 可测试性 | 20% |
| 扩展性 | 20% |
| 文档 | 20% |

**示例**:
```bash
/review 审查前端配置修改
```

---

### 6. /qa — 质量保证

**目标**: 质量保证

**核心活动**:
- 运行测试套件
- 浏览器测试 (如有 UI)
- Bug 修复
- 回归测试

**输出**: QA 测试报告 (qa_report)

**验收标准**:
- 测试覆盖率 ≥ 80%
- 核心流程 100% 通过
- 无 P0/P1 级别 Bug

**示例**:
```bash
/qa 运行前后端测试
```

---

### 7. /ship — 发布提交

**目标**: 发布提交

**核心活动**:
- Git 同步
- 测试验证
- 覆盖率审计
- 创建 PR/Release

**输出**: 发布包 (release)

**示例**:
```bash
/ship 提交 M13 集成验证
```

---

### 8. /retro — 回顾总结

**目标**: 回顾总结

**核心活动**:
- 完成情况回顾
- 经验教训总结
- 改进计划制定

**输出**: 回顾报告 (retro_report)

**示例**:
```bash
/retro 总结 M13 修复过程
```

---

## 📋 完整工作流示例

### 场景：修复前端构建问题

```bash
# 1. /office-hours - 明确问题
/office-hours 前端 TypeScript 构建失败，vite 和 vitest 类型冲突

# 2. /plan-ceo-review - 产品审视
/plan-ceo-review 分析类型冲突原因，制定修复方案

# 3. /plan-eng-review - 工程规划
/plan-eng-review 设计 vitest 配置分离方案

# 4. Build - 实现修复 (Claude Code 执行 ⛔ 墨菲斯不写)
# Claude Code 创建独立的 vitest.config.ts，统一依赖版本

# 5. /review - 代码审查
/review 审查配置文件修改

# 6. /qa - 测试验证
/qa 运行前端测试，验证修复

# 7. /ship - 发布提交
/ship 提交修复代码，更新文档

# 8. /retro - 回顾总结
/retro 总结类型冲突修复经验
```

---

## 🎨 gstack 命令格式

### Claude Code 中的用法

```bash
# 直接使用 slash 命令
/office-hours <任务描述>
/plan-ceo-review <任务描述>
/plan-eng-review <任务描述>
/review <任务描述>
/qa <任务描述>
/ship <任务描述>
/retro <任务描述>
```

### 完整命令列表

| 阶段 | 命令 | 说明 |
|------|------|------|
| 1 | `/office-hours` | 需求澄清（6 个 Forcing Questions） |
| 2 | `/plan-ceo-review` | 产品审视（10 项审视） |
| 3 | `/plan-eng-review` | 工程规划（技术设计） |
| 4 | `Build` | 代码实现（Claude Code 执行） |
| 5 | `/review` | 代码审查（5 维度评分） |
| 6 | `/qa` | 质量保证（测试验证） |
| 7 | `/ship` | 发布提交（Git + Release） |
| 8 | `/retro` | 回顾总结（经验教训） |

---

## 📊 gstack 输出结构

### 设计文档 (Think)
```json
{
  "type": "design_doc",
  "problem": "核心问题描述",
  "options": [...],
  "recommendation": "推荐方案"
}
```

### 审查报告 (Review)
```json
{
  "type": "review_report",
  "dimensions": {
    "code_style": 9,
    "design_pattern": 9,
    "testability": 9,
    "extensibility": 8,
    "documentation": 8
  },
  "overall_score": 8.6,
  "issues": {...}
}
```

### QA 报告 (Test)
```json
{
  "type": "qa_report",
  "tests_run": 122,
  "tests_passed": 122,
  "tests_failed": 0,
  "coverage": 85,
  "core_flows_passed": true,
  "bugs_found": [],
  "go_recommendation": true
}
```

### 发布包 (Ship)
```json
{
  "type": "release",
  "git_commit": "abc123",
  "tests_passed": true,
  "coverage": 85,
  "pr_url": "https://...",
  "release_notes": "..."
}
```

---

## ⚠️ 常见错误

### ❌ 错误：跳过阶段
```bash
# 错误：直接 Build，没有 Plan
/build 修复前端问题

# 正确：先 Plan 再 Build
/plan 制定修复方案
/build 实现修复
```

### ❌ 错误：阶段顺序混乱
```bash
# 错误：先 Ship 再 Test
/ship 提交代码
/qa 运行测试

# 正确：先 Test 再 Ship
/qa 运行测试
/ship 提交代码
```

### ❌ 错误：没有明确任务描述
```bash
# 错误：太模糊
/fix 修复问题

# 正确：具体描述
/qa 前端 14 个测试失败，主要是 waitFor 异步断言问题
```

---

## 📚 参考资源

- Garry Tan 原始 gstack 工作流
- Claude Code 文档
- 项目内 gstack 技能实现：`backend/app/skills/gstack/`

---

*创建时间：2026-03-25*  
*版本：1.0*
