# AITP-Research-Protocol 仓库审查报告

> 审查视角：使用者（新用户 + 日常使用者）
> 审查日期：2026-05-06
> 仓库版本：v2.9 (milestone_active)

---

## 总评

| 维度 | 评分 | 等级 |
|------|------|------|
| **设计理念与架构** | 9/10 | 优秀 |
| **文档注释质量** | 9/10 | 优秀 |
| **代码风格一致性** | 8/10 | 良好 |
| **架构与设计质量** | 7/10 | 良好 |
| **安全性** | 7/10 | 良好 |
| **错误处理** | 6/10 | 中等偏上 |
| **测试覆盖度** | 5/10 | 中等 |
| **新手可上手性** | 3/10 | 需改进 |
| **文档一致性** | 3/10 | 需改进 |
| **Windows 体验** | 2/10 | 严重不足 |
| **综合** | **6.2/10** | **中等偏上，设计优秀但体验粗糙** |

**一句话总结**：这是一个设计理念极为出色的研究协议系统——五层知识管线、对抗性四-agent 审查、文件即状态的持久化方案都展现了深度的系统思考。但从使用者角度看，文档一致性、Windows 支持、新手引导和工程基础设施（CI/CD、日志、测试覆盖）存在明显短板，阻碍了它从"个人研究工具"走向"可协作的开源项目"。

---

## 一、实际 Bug（需立即修复）

### BUG-1: `hooks/session_start.py` 第 345 行 — `NameError`

```python
# main() 函数中
ideas = _read_idea_registry(root)
if ideas:
    idea_context = _build_idea_context(ideas)
    context += f"\n{idea_context}\n"
    subplane_info += ", multi-idea: selection required"  # ← NameError!
```

`subplane_info` 在 `main()` 作用域中未定义（它只在 `_build_context_injection` 内部存在）。当 topic 有多个 idea 时，SessionStart hook 会因 `NameError` 崩溃，且 hook 错误通常静默不显示给用户。

**影响**：多 idea topic 无法正常启动会话。
**修复**：在 `main()` 中初始化 `subplane_info = ""`，或将此逻辑移入 `_build_context_injection`。

### BUG-2: `docs/INSTALL.md` 第 67 行 — 链接错误

```markdown
- [Kimi Code](INSTALL_CLAUDE_CODE.md) — same pattern, different paths
```

Kimi Code 的安装链接错误指向了 `INSTALL_CLAUDE_CODE.md`。

---

## 二、严重问题（High Priority）

### H-1: Windows 支持严重不足

仓库明显在 Windows 环境开发（路径 `D:\BaiduSyncdisk\...`，`.cmd` 文件），但几乎所有文档的命令示例都是 bash 格式：

| 受影响文件 | 问题 |
|-----------|------|
| `INSTALL.md` | 全部 bash 命令，无 Windows 说明 |
| `INSTALL_CLAUDE_CODE.md` | 全部 bash 命令 |
| `MIGRATE_LOCAL_INSTALL.md` | `rm -f` 在 Windows 不可用 |
| `UNINSTALL.md` | 全部 `rm` 命令 |
| `QUICKSTART.md` | 仅有简短 Windows note |

仅 `QUICKSTART.md` 末尾有两行 Windows 替代命令。对于一个 Windows 优先开发的项目，这是严重的体验断裂。

### H-2: Agent 名称在文档间不一致

| 文档 | 列出的 Agent |
|------|-------------|
| CHARTER.md | Claude Code, Kimi Code |
| architecture.md | OpenClaw, Codex, Claude Code, OpenCode |
| INSTALL.md | Claude Code, Kimi Code |
| README.md | "Claude Code 等" |
| UNINSTALL.md | Claude Code, Kimi Code |

新用户无法确定项目到底支持哪些 agent、自己该用哪个。

### H-3: 无 CI/CD 配置

`.github/workflows/` 目录不存在。测试只能手动运行，PR 无法自动验证。对于一个有 367 个测试用例的项目，没有 CI 是重大的工程缺陷。

### H-4: 无日志系统

整个 `brain/` 目录中零处 `import logging`。53 处 `except Exception` 静默吞掉异常。生产环境下，当 MCP 服务器或 CLI 出现问题时，用户和开发者都无从诊断。

### H-5: 无 `pyproject.toml`

项目没有标准的 Python 包配置文件。依赖管理仅靠 `aitp-manifest.json` 中的注释和 `README.md` 的零散提及。无法通过 `pip install -e .` 安装，也无法声明开发依赖（pytest、ruff 等）。

---

## 三、中等问题（Medium Priority）

### M-1: YAML frontmatter 解析逻辑重复三处

`_parse_md_local` 在 `state.py` 和 `preflight.py` 中各有一份，`mcp_server.py` 中又有基于正则的 `_parse_md`。三处实现功能相同但写法不同，违反 DRY 原则，且行为可能不一致。

### M-2: 原子写入逻辑重复两处

`state.py` 的 `atomic_write` 和 `mcp_server.py` 的 `_atomic_write_text` 实现相同功能但代码略有差异。

### M-3: `mcp_server.py` 过于庞大

从 `state_model` 导入超过 30 个符号，承担了过多职责，是典型的 God Object 倾向。应按领域拆分为独立模块。

### M-4: 测试覆盖不均衡

40 个源文件仅 10 个测试文件。`preflight.py`、`contracts.py`、`mcp_server.py`（最大文件）缺少直接测试。无覆盖率工具配置。

### M-5: 缺少 Troubleshooting / FAQ 文档

文档中没有常见问题排查指引：
- `aitp doctor` 某项检查失败怎么办？
- MCP server 连接不上怎么办？
- SessionStart hook 没有触发怎么办？
- Windows 上 PATH 相关错误怎么办？

### M-6: 缺少统一的"从零开始"新手路径

文档分散在 20+ 个文件中，没有 "Start Here" 式的统一入口。新用户理想路径（了解 → 安装 → 快速上手 → 遇到问题）缺少衔接。

### M-7: 文档语言不一致

- README.md: 中英混合（中文为主）
- CHARTER.md: 纯英文
- INSTALL 系列: 纯英文
- MIGRATE_MULTI_TOPIC.md: 英文为主，夹杂中文

### M-8: `CLAUDE.md` 和 `AGENTS.md` 高度重复

两个文件都在根目录，内容大量重叠（都指向 PROJECT_MEMORY.md，都有 Operator rule）。新用户困惑该看哪个。

### M-9: `DEEPSEEK_PROMPTS.md` 不应在仓库根目录

这是开发者内部工作文档，包含硬编码本地路径 `D:\BaiduSyncdisk\...`，不是用户文档。放在根目录会给新用户造成困惑。

### M-10: `package.json` 过于简陋

仅 `{"name": "aitp", "version": "1.0.0"}`，无 scripts、无 dependencies。Node.js 生态集成不成熟。

---

## 四、低优先级问题（Low Priority）

### L-1: 缺少代码格式化/lint 配置

无 `ruff.toml`、`.flake8`、`.pre-commit-config.yaml`。代码风格靠人工维护。

### L-2: backlog 中大量 `.gitkeep` 空目录

`.planning/backlog/` 下 30+ 个目录仅有 `.gitkeep`，无 CONTEXT.md。这些空壳目录增加了仓库噪音。

### L-3: `.opencode/node_modules/` 应加入 .gitignore

`node_modules` 不应被版本控制。虽然 `.gitignore` 中有 `node_modules/` 规则，但 `.opencode/node_modules/` 仍出现在仓库中。

### L-4: 部分 Skill 触发条件文档不够明确

例如 `skill-continuous.md` 的触发条件是"会话中断后的任何状态"，但具体如何检测"会话中断"没有说明。

### L-5: 缺少贡献者指南 (CONTRIBUTING.md)

对于开源项目，缺少贡献流程、代码规范、PR 模板等。

---

## 五、亮点与优势

### 1. 设计理念极为出色

五层知识管线（L0 Source → L1 Read → L3 Derive → L4 Verify → L2 Memory）的设计展现了深度的系统思考。"Skill 告诉 Agent 应该怎么做，Harness 保证 Agent 确实这么做了"——这个定位精准且有说服力。

### 2. 对抗性四-Agent 审查

Algebraic / Physical / Numerical / Skeptic 四个独立审查者 + 分歧矩阵，是 AI 辅助研究中罕见的严谨设计。

### 3. 文件即状态的持久化方案

纯 Markdown + YAML frontmatter，不依赖数据库。原子写入保障崩溃安全。这个选择既透明又可靠。

### 4. 文档注释质量极高

模块级 docstring 包含职责描述、API 列表、使用示例、设计决策。函数级文档覆盖参数、返回值、行为注释。Schema 文档双轨对应（人类可读合约 + 机器可读 JSON Schema）。

### 5. 安全意识良好

路径遍历防护（测试覆盖 Unix + Windows）、YAML 安全加载（`safe_load`）、Pydantic 严格模式（`extra="forbid"`）。

### 6. 项目规划体系成熟

GSD 驱动的项目管理，60+ 里程碑、5 轴分类法、详细的阶段执行记录和证据链。`.planning/` 目录是项目管理的标杆。

### 7. Skills 体系设计精良

17 个协议 skill 覆盖完整研究生命周期，YAML frontmatter 标准化（name / description / trigger），三层架构（入口层 → 协议层 → 领域层），适配器模式支持多 Agent。

### 8. 丰富的协议文档

30+ 个协议文档覆盖 L0-L5 各层、Agent 治理、验证桥接等。22 个实施计划 + 15 个设计规范形成了完整的设计历史。

---

## 六、优先修复建议（按紧急度排序）

| # | 优先级 | 建议 | 预估工作量 |
|---|--------|------|-----------|
| 1 | 🔴 紧急 | 修复 `session_start.py` 第 345 行 `NameError` | 5 分钟 |
| 2 | 🔴 紧急 | 修复 `INSTALL.md` 中 Kimi Code 链接 | 2 分钟 |
| 3 | 🔴 高 | 添加 CI/CD（GitHub Actions: pytest + ruff） | 2 小时 |
| 4 | 🔴 高 | 引入 `logging` 模块，替换静默 `except Exception` | 4 小时 |
| 5 | 🟡 高 | 创建 `pyproject.toml`，标准化依赖管理 | 1 小时 |
| 6 | 🟡 高 | 补充 Windows 命令示例（至少 INSTALL/UNINSTALL） | 2 小时 |
| 7 | 🟡 高 | 统一所有文档中的 Agent 名称列表 | 1 小时 |
| 8 | 🟡 中 | 提取公共 `_parse_md` 到 `brain/cli/utils.py` | 1 小时 |
| 9 | 🟡 中 | 拆分 `mcp_server.py` 为多个模块 | 4 小时 |
| 10 | 🟡 中 | 添加 Troubleshooting / FAQ 文档 | 3 小时 |
| 11 | 🟡 中 | 合并或区分 `CLAUDE.md` 和 `AGENTS.md` | 30 分钟 |
| 12 | 🟢 低 | 移动 `DEEPSEEK_PROMPTS.md` 到 `.planning/` 或删除 | 5 分钟 |
| 13 | 🟢 低 | 清理 backlog 空目录（仅保留有 CONTEXT.md 的） | 30 分钟 |
| 14 | 🟢 低 | 添加 `.pre-commit-config.yaml` | 1 小时 |
| 15 | 🟢 低 | 添加 CONTRIBUTING.md | 2 小时 |

---

## 七、结论

AITP-Research-Protocol 是一个**设计远超实现成熟度**的项目。它的核心理念——强制执行研究纪律、对抗性审查、跨会话记忆积累——在 AI 辅助研究领域是领先的。文档注释和项目规划的深度令人印象深刻。

但从使用者视角看，项目目前更像是**一个人的研究工具**而非**可协作的开源项目**。最紧迫的改进不是添加新功能，而是：

1. **修复实际 Bug**（session_start.py NameError）
2. **补齐工程基础设施**（CI/CD、日志、pyproject.toml）
3. **统一文档一致性**（Agent 名称、Windows 支持、链接正确性）
4. **改善新手体验**（Troubleshooting、统一入口、FAQ）

这些改进不需要改变架构设计，但会显著提升项目的可采纳度和可维护性。
