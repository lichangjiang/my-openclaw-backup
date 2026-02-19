# OpenSpec Day 7 学习笔记：深入原理

## 学习日期
2026-02-18

---

## Part 1: Delta Spec 机制

### 1.1 Delta Spec 格式定义

**数据结构**（`src/core/schemas/change.schema.ts`）：
```typescript
export const DeltaOperationType = z.enum(['ADDED', 'MODIFIED', 'REMOVED', 'RENAMED']);

export const DeltaSchema = z.object({
  spec: z.string(),           // 目标 spec 名称
  operation: DeltaOperationType,
  description: z.string(),    // 描述
  requirement: RequirementSchema.optional(),
  requirements: z.array(RequirementSchema).optional(),
  rename: z.object({ from, to }).optional(),  // RENAMED 专用
});
```

**四种操作类型：**
1. **ADDED**: 新增需求
2. **MODIFIED**: 修改现有需求
3. **REMOVED**: 删除需求
4. **RENAMED**: 重命名需求（包含 FROM 和 TO）

### 1.2 Delta Spec 解析

**解析器**（`src/core/parsers/change-parser.ts`）：

解析流程：
1. 识别 Delta 章节：`## ADDED Requirements`、`## MODIFIED Requirements` 等
2. 提取需求块：`### Requirement: <name>`
3. 提取场景：`#### Scenario: <name>`
4. 解析 RENAME：`FROM: ### Requirement: <old>` 和 `TO: ### Requirement: <new>`

```typescript
private parseSpecDeltas(specName: string, content: string): Delta[] {
  const sections = this.parseSectionsFromContent(content);

  // 解析 ADDED
  const addedSection = this.findSection(sections, 'ADDED Requirements');
  if (addedSection) {
    const requirements = this.parseRequirements(addedSection);
    requirements.forEach(req => {
      deltas.push({
        spec: specName,
        operation: 'ADDED',
        description: `Add requirement: ${req.text}`,
        requirement: req,
        requirements: [req],
      });
    });
  }

  // 解析 MODIFIED、REMOVED、RENAMED（类似）
  // ...
}
```

### 1.3 Delta Spec 验证

**验证器**（`src/core/validation/validator.ts`）：

验证规则：
1. **章节内重复检查**：ADDED/MODIFIED/REMOVED/RENAMED 中不能有重复的需求名称
2. **跨章节冲突检查**：同一需求不能出现在多个章节
3. **格式要求**：
   - ADDED/MODIFIED：必须有需求文本（SHALL/MUST），必须有至少一个场景
   - REMOVED：只需要名称，不需要场景
   - RENAMED：必须有 FROM 和 TO 配对

```typescript
// 跨章节冲突检查示例
for (const n of modifiedNames) {
  if (removedNames.has(n)) {
    issues.push({
      level: 'ERROR',
      path: entryPath,
      message: `Requirement present in both MODIFIED and REMOVED: "${n}"`
    });
  }
}
```

### 1.4 Delta Spec 合并

**合并逻辑**（`src/core/specs-apply.ts`）：

**合并顺序**（非常重要）：
1. **RENAMED**：先重命名（修改 header）
2. **REMOVED**：再删除（避免重命名后删除错误的内容）
3. **MODIFIED**：再修改（替换现有需求）
4. **ADDED**：最后追加（避免后续修改）

```typescript
// 应用顺序
// RENAMED
for (const r of plan.renamed) {
  const block = nameToBlock.get(from)!;
  const newHeader = `### Requirement: ${to}`;
  // 更新 block 的 header
  nameToBlock.delete(from);
  nameToBlock.set(to, renamedBlock);
}

// REMOVED
for (const name of plan.removed) {
  nameToBlock.delete(key);
}

// MODIFIED
for (const mod of plan.modified) {
  nameToBlock.set(key, mod);
}

// ADDED
for (const add of plan.added) {
  nameToBlock.set(key, add);
}
```

**重建规范文件**：
- 保留原有顺序
- 新增的需求追加到最后
- 保持格式一致性（避免空行过多）

---

## Part 2: 工件生成机制

### 2.1 工件模板系统

**模板位置**：`schemas/spec-driven/templates/`

**四个工件模板**：
1. **proposal.md**：变更提案（Why, What Changes, Capabilities, Impact）
2. **design.md**：设计文档（Context, Goals/Non-Goals, Decisions, Risks）
3. **tasks.md**：任务清单（按章节组织的复选框）
4. **spec.md**：Delta Spec（ADDED/MODIFIED/REMOVED/RENAMED 章节）

**模板示例**（proposal.md）：
```markdown
## Why
<!-- Explain the motivation for this change. What problem does this solve? Why now? -->

## What Changes
<!-- Describe what will change. Be specific about new capabilities, modifications, or removals. -->

## Capabilities
### New Capabilities
- `<name>`: <brief description of what this capability covers>

### Modified Capabilities
- `<existing-name>`: <what requirement is changing>

## Impact
<!-- Affected code, APIs, dependencies, systems -->
```

### 2.2 AI 指令生成

**指令生成**（`src/commands/workflow/instructions.ts`）：

指令结构：
```xml
<artifact id="proposal" change="<change-name>" schema="spec-driven">
  <task>Create the proposal artifact for change "<change-name>".</task>

  <project_context>
    <!-- 背景信息，AI 不要包含在输出中 -->
  </project_context>

  <rules>
    <!-- 约束条件，AI 必须遵循 -->
  </rules>

  <dependencies>
    <!-- 需要读取的依赖文件 -->
    <dependency id="design" status="done">
      <path>./design.md</path>
      <description>Design document</description>
    </dependency>
  </dependencies>

  <output>
    Write to: ./proposal.md
  </output>

  <instruction>
    <!-- 具体指导 -->
  </instruction>

  <template>
    <!-- 模板内容 -->
  </template>

  <success_criteria>
    <!-- 成功标准 -->
  </success_criteria>

  <unlocks>
    Completing this artifact enables: tasks, specs
  </unlocks>
</artifact>
```

### 2.3 工件生成的实现方式

**模板 vs AI 的分工**：

| 角色 | 职责 | 示例 |
|------|------|------|
| **模板** | 定义结构 | 定义章节、格式、占位符 |
| **AI** | 填充内容 | 根据模板生成具体内容 |

**为什么需要模板？**
- 保证一致性：所有工件都有相同的结构
- 降低 AI 生成难度：AI 只需要填充，不需要从头构建
- 易于维护：修改模板即可更新所有工件

**AI 的作用**：
1. 理解 context 和 rules
2. 根据用户的 prompt 生成内容
3. 填充模板中的占位符
4. 确保内容符合规范（SHALL/MUST、场景等）

**生成流程**：
1. 用户运行 `/opsx:ff proposal` 或 `/opsx:continue`
2. 系统生成指令（包括模板）
3. AI 读取依赖文件（context）
4. AI 根据模板生成内容
5. 写入到对应路径

---

## Part 3: 任务执行机制

### 3.1 任务依赖关系

**任务组织**（tasks.md）：
```markdown
## 1. Infrastructure
- [ ] 1.1 Set up database
- [ ] 1.2 Configure Redis

## 2. Components
- [ ] 2.1 Implement user service
- [ ] 2.2 Implement auth middleware

## 3. Features
- [ ] 3.1 Add user registration
- [ ] 3.2 Add user login

## 4. Testing
- [ ] 4.1 Write unit tests
- [ ] 4.2 Write integration tests
```

**依赖关系**：
- Infrastructure → Components → Features → Testing
- 基础任务必须先完成，后续任务依赖前面的完成
- 可以标记并行任务（如果需要）

### 3.2 任务进度追踪

**进度追踪**（`src/utils/task-progress.ts`）：

```typescript
// 解析复选框
const TASK_PATTERN = /^[-*]\s+\[[\sx]\]/i;
const COMPLETED_TASK_PATTERN = /^[-*]\s+\[x\]/i;

export function countTasksFromContent(content: string): TaskProgress {
  const lines = content.split('\n');
  let total = 0;
  let completed = 0;
  for (const line of lines) {
    if (line.match(TASK_PATTERN)) {
      total++;
      if (line.match(COMPLETED_TASK_PATTERN)) {
        completed++;
      }
    }
  }
  return { total, completed };
}

// 格式化状态
export function formatTaskStatus(progress: TaskProgress): string {
  if (progress.total === 0) return 'No tasks';
  if (progress.completed === progress.total) return '✓ Complete';
  return `${progress.completed}/${progress.total} tasks`;
}
```

**应用指令**（`src/commands/workflow/instructions.ts`）：

生成 apply 指令时会检查任务进度：
```typescript
const progress = await getTaskProgressForChange(changesDir, changeName);
const incompleteTasks = progress.total - progress.completed;

if (incompleteTasks > 0) {
  console.log(`Warning: ${incompleteTasks} incomplete task(s) found.`);
}
```

### 3.3 任务执行的顺序

**推荐顺序**：
1. **Infrastructure**：数据库、缓存、配置等基础设置
2. **Components**：核心组件和服务
3. **Features**：具体功能实现
4. **Testing**：测试和验证

**并行任务**：
- 如果某些任务之间没有依赖，可以并行执行
- 使用不同的章节或子章节来组织
- 例如：`1.1` 和 `1.2` 可以并行，但 `2.x` 必须在 `1.x` 之后

---

## Part 4: 归档机制

### 4.1 Delta Specs 合并

**合并步骤**（`src/core/specs-apply.ts`）：

1. **查找 Delta Specs**：扫描 `changes/<name>/specs/` 目录
2. **准备更新**：
   - 读取 Delta Spec 内容
   - 验证重复和冲突
   - 读取主规范（如果存在）
3. **构建更新后的规范**：
   - 应用 RENAMED、REMOVED、MODIFIED、ADDED 操作
   - 重建规范文件
4. **验证重建后的规范**：
   - 确保格式正确
   - 确保没有重复或冲突
5. **写入文件**：更新 `openspec/specs/<name>/spec.md`

```typescript
export async function applySpecs(
  projectRoot: string,
  changeName: string,
  options: { dryRun?: boolean; skipValidation?: boolean; silent?: boolean }
): Promise<SpecsApplyOutput> {
  // 1. 查找要更新的 specs
  const specUpdates = await findSpecUpdates(changeDir, mainSpecsDir);

  // 2. 准备所有更新（验证阶段，不写入）
  const prepared = [];
  for (const update of specUpdates) {
    const built = await buildUpdatedSpec(update, changeName);
    prepared.push({ update, rebuilt: built.rebuilt, counts: built.counts });
  }

  // 3. 验证重建的 specs
  if (!options.skipValidation) {
    const validator = new Validator();
    for (const p of prepared) {
      const report = await validator.validateSpecContent(specName, p.rebuilt);
      if (!report.valid) {
        throw new Error(`Validation errors in rebuilt spec for ${specName}`);
      }
    }
  }

  // 4. 写入文件
  for (const p of prepared) {
    if (!options.dryRun) {
      await fs.mkdir(targetDir, { recursive: true });
      await fs.writeFile(update.target, p.rebuilt);
    }
  }
}
```

### 4.2 主规范更新

**更新流程**：
1. 读取主规范文件（`openspec/specs/<name>/spec.md`）
2. 提取 Requirements 章节
3. 应用 Delta 操作（按顺序：RENAMED → REMOVED → MODIFIED → ADDED）
4. 重建整个文件
5. 验证重建后的文件
6. 写回主规范

**保持一致性**：
- 保留原有的 Purpose 和其他章节
- 只更新 Requirements 章节
- 保持格式一致（避免空行过多）
- 保留原有顺序（新增的追加到最后）

### 4.3 归档组织

**归档结构**（`src/core/archive.ts`）：

```
openspec/changes/archive/
  2026-02-14-add-user-auth/
    proposal.md
    design.md
    tasks.md
    specs/
      user-auth/
        spec.md
  2026-02-16-fix-bug-123/
    proposal.md
    design.md
    tasks.md
    specs/
      core/
        spec.md
```

**归档流程**：
1. 验证 Delta Specs（如果存在）
2. 显示任务进度
3. 应用 Delta Specs 到主规范
4. 创建带日期的归档目录：`YYYY-MM-DD-<change-name>/`
5. 移动变更文件夹到 `archive/`
6. 保留完整的变更历史

**跨平台兼容性**：
- 使用 `fs.rename()` 在 Unix 系统上
- 在 Windows 上，如果 `fs.rename()` 失败（EPERM/EXDEV），则使用 copy + remove
- 确保 Windows 用户也能正常归档

---

## 思考问题解答

### Q1: 如果 Delta Spec 中同时有 MODIFIED 和 REMOVED 同一个需求，会发生什么？

**答案**：会发生验证错误，归档会被阻止。

**原因**（`src/core/validation/validator.ts`）：
```typescript
// 跨章节冲突检查
for (const n of modifiedNames) {
  if (removedNames.has(n)) {
    issues.push({
      level: 'ERROR',
      path: entryPath,
      message: `Requirement present in both MODIFIED and REMOVED: "${n}"`
    });
  }
}
```

**冲突检查**：
- MODIFIED vs REMOVED：❌ 冲突
- MODIFIED vs ADDED：❌ 冲突
- ADDED vs REMOVED：❌ 冲突
- RENAMED vs MODIFIED/ADDED：⚠️ 需要注意（MODIFIED 必须引用新名称）

**如何处理**：
- 用户必须手动修正 Delta Spec
- 选择正确的操作类型（要么 MODIFIED，要么 REMOVED，不能同时）
- 或者删除重复的需求

---

### Q2: 工件生成是模板化的还是完全 AI 生成的？

**答案**：是**模板化 + AI 填充**的混合模式。

**模板的作用**：
1. **定义结构**：确保所有工件都有统一的格式
2. **降低难度**：AI 不需要从头构建文档，只需要填充内容
3. **易于维护**：修改模板即可更新所有工件
4. **保证一致性**：避免 AI 生成杂乱无章的格式

**AI 的作用**：
1. **理解 context**：读取依赖文件，理解项目背景
2. **遵循 rules**：遵守约束条件（SHALL/MUST、场景等）
3. **填充内容**：根据模板生成具体内容
4. **确保质量**：生成符合规范的文档（需求文本、场景描述等）

**为什么选择混合模式？**

| 方式 | 优点 | 缺点 |
|------|------|------|
| **完全模板化** | 结构一致，简单易用 | 缺乏灵活性，内容质量依赖人工 |
| **完全 AI 生成** | 灵活，内容质量高 | 格式不一致，不可预测 |
| **模板 + AI** | ✅ 结构一致<br>✅ 内容质量高<br>✅ 易于维护 | 需要维护模板 |

**实际流程**：
1. 用户运行 `/opsx:ff proposal`
2. 系统加载模板（`schemas/spec-driven/templates/proposal.md`）
3. 系统生成指令（包含 context、rules、template）
4. AI 读取依赖文件（如果有）
5. AI 根据模板生成内容
6. 写入到 `openspec/changes/<name>/proposal.md`

---

### Q3: 归档后的主规范如何保持一致性和准确性？

**答案**：通过**多层次的验证和重建机制**来确保。

**一致性保证机制**：

### 1. 应用前的验证
```typescript
// 验证 Delta Specs
const deltaReport = await validator.validateChangeDeltaSpecs(changeDir);
if (!deltaReport.valid) {
  console.log(chalk.red('\nValidation errors in change delta specs:'));
  for (const issue of deltaReport.issues) {
    console.log(chalk.red(`  ✗ ${issue.message}`));
  }
  return; // 阻止归档
}
```

### 2. 重建后的验证
```typescript
// 准备所有更新（验证阶段，不写入）
for (const update of specUpdates) {
  const built = await buildUpdatedSpec(update, changeName);
  prepared.push({ update, rebuilt: built.rebuilt, counts: built.counts });
}

// 验证重建的 specs
const validator = new Validator();
for (const p of prepared) {
  const report = await validator.validateSpecContent(specName, p.rebuilt);
  if (!report.valid) {
    console.log(chalk.red(`\nValidation errors in rebuilt spec for ${specName}:`));
    for (const issue of report.issues) {
      console.log(chalk.red(`  ✗ ${issue.message}`));
    }
    return; // 阻止写入
  }
}
```

### 3. 合并顺序的正确性
```typescript
// RENAMED → REMOVED → MODIFIED → ADDED
// 1. 先重命名（避免删除错误的内容）
// 2. 再删除（删除旧的需求）
// 3. 再修改（替换现有需求）
// 4. 最后追加（新增的需求）
```

### 4. 格式保持
```typescript
// 重建规范时保留原有顺序
const keptOrder: RequirementBlock[] = [];
const seen = new Set<string>();
for (const block of parts.bodyBlocks) {
  const key = normalizeRequirementName(block.name);
  const replacement = nameToBlock.get(key);
  if (replacement) {
    keptOrder.push(replacement);
    seen.add(key);
  }
}

// 新增的追加到最后
for (const [key, block] of nameToBlock.entries()) {
  if (!seen.has(key)) {
    keptOrder.push(block);
  }
}
```

### 5. 跨平台兼容性
```typescript
// Windows 上使用 copy + remove，避免 EPERM 错误
async function moveDirectory(src: string, dest: string): Promise<void> {
  try {
    await fs.rename(src, dest);
  } catch (err: any) {
    if (err.code === 'EPERM' || err.code === 'EXDEV') {
      await copyDirRecursive(src, dest);
      await fs.rm(src, { recursive: true, force: true });
    } else {
      throw err;
    }
  }
}
```

### 6. 错误处理和回滚
```typescript
// 准备阶段失败 → 不写入任何文件
try {
  for (const update of specUpdates) {
    const built = await buildUpdatedSpec(update, changeName);
    prepared.push({ update, rebuilt: built.rebuilt, counts: built.counts });
  }
} catch (err: any) {
  console.log(String(err.message || err));
  console.log('Aborted. No files were changed.');
  return; // 中止归档，保持原样
}

// 所有验证通过 → 写入文件
for (const p of prepared) {
  await writeUpdatedSpec(p.update, p.rebuilt, p.counts);
}
```

**准确性保证机制**：

### 1. 重复检查
- 章节内：ADDED/MODIFIED/REMOVED/RENAMED 中不能有重复
- 跨章节：同一需求不能出现在多个章节

### 2. 冲突检查
- MODIFIED vs REMOVED：不能同时存在
- MODIFIED vs ADDED：不能同时存在
- ADDED vs REMOVED：不能同时存在
- RENAMED vs MODIFIED：MODIFIED 必须引用新名称

### 3. 格式要求
- ADDED/MODIFIED：必须有 SHALL/MUST，必须有至少一个场景
- REMOVED：只需要名称
- RENAMED：必须有 FROM 和 TO 配对

### 4. 新规范的验证
- 重建后的规范必须通过完整的 Schema 验证
- 如果验证失败，阻止归档，保留原样

**总结**：
归档后的主规范通过以下方式保持一致性和准确性：
1. ✅ 应用前验证 Delta Specs
2. ✅ 应用后验证重建的规范
3. ✅ 正确的合并顺序（RENAMED → REMOVED → MODIFIED → ADDED）
4. ✅ 保留原有格式和顺序
5. ✅ 跨平台兼容性（Windows 使用 copy + remove）
6. ✅ 错误处理和回滚（准备失败不写入）
7. ✅ 重复和冲突检查
8. ✅ 格式要求验证

如果出现合并错误或验证失败，系统会阻止归档，保持原样，确保主规范不会被破坏。

---

## 学习总结

### 已掌握的核心概念

✅ **Delta Spec 机制**
- 格式定义（ADDED/MODIFIED/REMOVED/RENAMED）
- 解析逻辑（识别章节、提取需求、解析场景）
- 验证规则（重复检查、冲突检查、格式要求）
- 合并顺序（RENAMED → REMOVED → MODIFIED → ADDED）

✅ **工件生成机制**
- 模板系统（四个工件模板）
- AI 指令生成（context、rules、template）
- 模板 vs AI 的分工（结构 vs 内容）
- 生成流程（加载模板 → 生成指令 → AI 填充 → 写入文件）

✅ **任务执行机制**
- 任务组织（按章节：Infrastructure → Components → Features → Testing）
- 依赖关系（基础先完成，后续依赖前面）
- 进度追踪（解析复选框、计算进度）
- 执行顺序（推荐顺序 + 并行任务）

✅ **归档机制**
- Delta Specs 合并（查找 → 准备 → 验证 → 写入）
- 主规范更新（重建文件、保持格式）
- 归档组织（带日期的归档目录）
- 一致性保证（多层次验证、错误处理）

### 能够解释的问题

1. ✅ Delta Spec 中的 MODIFIED 和 REMOVED 冲突如何处理？
   - 验证阶段会检测冲突，阻止归档
   - 用户必须手动修正

2. ✅ 工件生成是模板化还是 AI 生成？
   - 模板化 + AI 填充的混合模式
   - 模板定义结构，AI 填充内容

3. ✅ 归档后的主规范如何保持一致性？
   - 多层次验证（应用前、重建后）
   - 正确的合并顺序
   - 错误处理和回滚
   - 重复和冲突检查

### 深入理解的关键

1. **数据流**：从 Delta Spec → 验证 → 合并 → 重建 → 验证 → 写入
2. **顺序很重要**：RENAMED → REMOVED → MODIFIED → ADDED
3. **验证是关键**：应用前验证、重建后验证、双重保障
4. **模板 vs AI**：各司其职，模板定义结构，AI 填充内容
5. **错误处理**：准备失败不写入，保持原样

### 下一步建议

1. **实际应用**：在实际项目中使用 OpenSpec
2. **自定义模板**：根据项目需求修改或扩展模板
3. **参与社区**：分享经验，讨论改进
4. **深入源码**：继续阅读更多源码，理解更多细节

---

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

**学习完成！** 🎉

现在你已经深入理解了 OpenSpec 的底层实现原理，可以：
- 解释 Delta Spec 的解析、验证和合并机制
- 理解工件生成的模板化和 AI 填充模式
- 掌握任务执行和进度追踪的实现
- 理解归档机制和一致性保证

下一步：在实际项目中应用 OpenSpec，体验规范驱动开发的价值！
