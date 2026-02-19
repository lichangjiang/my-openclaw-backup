# OpenSpec Day 7 学习笔记：深入原理

## 学习日期
2026-02-18

## 核心内容摘要

### Part 1: Delta Spec 机制

**四种操作类型：**
1. **ADDED**: 新增需求
2. **MODIFIED**: 修改现有需求
3. **REMOVED**: 删除需求
4. **RENAMED**: 重命名需求

**关键要点：**
- 合并顺序必须遵循：RENAMED → REMOVED → MODIFIED → ADDED
- 验证规则：章节内不重复、跨章节不冲突
- 格式要求：ADDED/MODIFIED 需要 SHALL/MUST 和场景；REMOVED 只需要名称；RENAMED 需要 FROM 和 TO

### Part 2: 工件生成机制

**四个工件模板：**
1. **proposal.md**: 变更提案
2. **design.md**: 设计文档
3. **tasks.md**: 任务清单
4. **spec.md**: Delta Spec

**模板 vs AI 分工：**
- 模板：定义结构、降低难度、易于维护、保证一致性
- AI：理解 context、遵循 rules、填充内容、确保质量

### Part 3: 任务执行机制

**任务组织顺序：**
1. Infrastructure → Components → Features → Testing
2. 支持并行任务（无依赖关系）
3. 进度追踪：解析复选框，计算完成度

### Part 4: 归档机制

**一致性保证机制：**
1. 应用前验证 Delta Specs
2. 重建后验证规范
3. 正确的合并顺序
4. 跨平台兼容性（Windows 使用 copy + remove）
5. 错误处理和回滚

## 思考问题解答

### Q1: Delta Spec 中同时有 MODIFIED 和 REMOVED 同一个需求？
**答案**: 验证阶段会检测冲突，阻止归档。用户必须手动修正。

### Q2: 工件生成是模板化还是 AI 生成？
**答案**: 模板化 + AI 填充的混合模式。模板定义结构，AI 填充内容。

### Q3: 归档后的主规范如何保持一致性？
**答案**: 通过多层次的验证和重建机制：
- 应用前验证 + 重建后验证
- 正确的合并顺序
- 错误处理和回滚
- 重复和冲突检查

## 学习总结

**已掌握的核心概念：**
✅ Delta Spec 机制（格式、解析、验证、合并）
✅ 工件生成机制（模板系统、AI 指令）
✅ 任务执行机制（依赖关系、进度追踪）
✅ 归档机制（合并、更新、一致性保证）

**深入理解的关键：**
1. 数据流：Delta Spec → 验证 → 合并 → 重建 → 验证 → 写入
2. 顺序很重要：RENAMED → REMOVED → MODIFIED → ADDED
3. 验证是关键：应用前验证 + 重建后验证
4. 模板 vs AI：各司其职
5. 错误处理：准备失败不写入，保持原样

## 源码文件清单

| 文件路径 | 作用 |
|---------|------|
| `src/core/schemas/change.schema.ts` | Delta Spec 数据结构定义 |
| `src/core/parsers/change-parser.ts` | Delta Spec 解析器 |
| `src/core/validation/validator.ts` | Delta Spec 验证器 |
| `src/core/specs-apply.ts` | Delta Specs 合并逻辑 |
| `schemas/spec-driven/templates/` | 工件模板目录 |
| `src/commands/workflow/instructions.ts` | AI 指令生成 |
| `src/utils/task-progress.ts` | 任务进度追踪 |
| `src/core/archive.ts` | 归档命令实现 |

---

**完整学习笔记文件：**
`~/onedrive/auto-notes/01-技术学习/AI-学习笔记/openspec-learning-day7-notes.md`
