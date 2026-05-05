# AITP — AI-assisted Theoretical Physics

> 追求真理而非沽名钓誉 · *Pursue truth, not fame.*

AITP gives an AI agent the discipline of a good research collaborator: **show your sources, justify every step, don't skip gates, and only call something "known" after adversarial review.**

---

## Why

LLMs can discuss physics fluently but have no built-in discipline: they skip derivations, forget sources, and state conjectures as facts. A human postdoc keeps a lab notebook, traces every equation to its source, and subjects claims to adversarial review. AITP is that discipline, encoded as a protocol.

## What it does

```
你: "我想研究 GW 近似中 head-wing correction"
AITP: 创建课题 → 注册论文 → 拆解章节 → 记录推导 → 打包候选 → 
     SymPy 验证 / HPC 计算 → 4-agent 对抗审查 → 晋升到全局知识图
```

Every step is enforced — you can't submit a claim without derivation steps, can't promote without Skeptic review. State is plain Markdown files, never lost between sessions.

## Workflow

```
                  ┌──────────────┐
                  │  L0: SOURCE  │  找论文、注册源、评估覆盖
                  │   discover   │  aitp source add / discover
                  └──────┬───────┘
                         │ advance
                  ┌──────▼───────┐
                  │  L1: READ    │  拆 TOC、提取章节、锁定约定
                  │   & frame    │  aitp source extract / convention lock
                  └──────┬───────┘
                         │ advance
                  ┌──────▼───────┐
                  │  L3: DERIVE  │  推导、SymPy 检查、生成候选
                  │   flexible   │  aitp derive record → pack → submit
                  └──────┬───────┘
                         │ candidate submit
           ┌─────────────▼─────────────┐
           │     L4: VERIFY            │
           │                           │
           │  ┌─────────────────────┐  │
           │  │ Algebraic Verifier  │  │  代数逐步验证
           │  │ Physical Verifier   │  │  物理极限/对称性
           │  │ Numerical Verifier  │  │  HPC 输出校验
           │  │ Skeptic (盲审)      │  │  只看结论，找矛盾
           │  └─────────────────────┘  │
           │           ↓               │
           │    分歧矩阵 → 判决        │
           └─────────────┬─────────────┘
                         │ promote
                  ┌──────▼───────┐
                  │  L2: MEMORY  │  全局知识图，跨课题积累
                  │  knowledge   │
                  └──────────────┘
```

**L3 ⇄ L4 是一个循环**：验证失败 → 返回 L3 修正 → 重新提交。最多 3 轮，之后人工裁决。

## Architecture

```
CLI 强制 ──── MCP 便利 ──── Skill 指导 ──── Hook 监视

  硬拦截          转发           文本注入         事后检测
```

| 层 | 位置 | 做什么 |
|----|------|--------|
| **CLI** | `brain/cli/` | 强制执行引擎。Preflight + Pydantic 合同 + state validator。唯一能改 topic 状态的路径。21 个命令 |
| **MCP** | `brain/mcp_server.py` | 给 Agent 用的便利层。参数解析 → dispatch 到 CLI。~55 个 tool |
| **Skill** | `skills/`, `deploy/skills/` | 告诉 Agent 协议规则、红线、常见用户短语→CLI 命令的映射 |
| **Hook** | `hooks/` | SessionStart 注入网关 skill。Stop 写 HUD 状态 + 日志 |

## Folder structure

```
AITP-Research-Protocol/
├── brain/
│   ├── cli/                  CLI 强制执行引擎
│   │   ├── state.py              原子写入、stage 转换 (advance/retreat)
│   │   ├── preflight.py          10 项注册检查、两速设计
│   │   ├── contracts.py          Pydantic 验证 (extra="forbid")
│   │   ├── decorators.py         @require_stage + @with_preflight
│   │   └── commands/             9 个命令模块 (21 个 CLI 命令)
│   ├── commands/              23 个策略文件 (YAML frontmatter)
│   ├── agents/                4 个审查 Agent 模板
│   └── mcp_server.py          MCP 服务器
├── hooks/                     SessionStart / Stop / 事件记录
├── skills/                    协议 skills (L0-L4 + domain)
├── deploy/                    安装部署源 (skills / hooks / config)
└── scripts/                   aitp CLI 入口 + 包管理器
```

**每个研究课题的文件树**（由 `aitp topic init` 创建）：

```
<topic-slug>/
├── state.md           课题状态 (stage, lane, gate, cycle...)
├── MEMORY.md          记录 (Steering, Decisions, Pitfalls)
├── research.md        自动追加的研究轨迹
├── compute/targets.yaml  HPC 目标配置
├── L0/sources/        注册的论文/代码
├── L1/intake/         提取的章节笔记 (按 source 嵌套)
├── L2/graph/          局部知识图 (promote 后→全局 L2)
├── L3/candidates/     候选声明
├── L4/reviews/        审查报告
├── L4/scripts/        Slurm 脚本
├── L4/outputs/        HPC 输出
├── L4/reports/        验证报告
└── notebook/          LaTeX 笔记
```

## Install

```bash
git clone git@github.com:bhjia-phys/AITP-Research-Protocol.git
cd AITP-Research-Protocol
AITP_TOPICS_ROOT=~/research/aitp-topics python scripts/aitp-pm.py install
```

After install, use `aitp` from anywhere:

```bash
aitp doctor          # 健康检查
aitp update          # 同步部署文件
aitp upgrade         # git pull + 重部署
```

## Quick start

```bash
# 1. 创建课题
aitp topic init gw-headwing --lane code_method

# 2. 绑定会话
aitp session resume gw-headwing

# 3. 注册论文
aitp source add gw-headwing --id hedin1965 --title "Hedin 1965" --type paper

# 4. 推进到阅读阶段
aitp state advance gw-headwing L1
aitp source parse-toc gw-headwing --source hedin1965 --sections "Intro, Eqs, GW"
aitp source extract gw-headwing --source hedin1965 --section "GW Approx" --content "..."

# 5. 推进到推导阶段
aitp state advance gw-headwing L3
aitp derive record gw-headwing --step D1 --source "hedin1965:Eq20" \
    --input "Sigma=iGW" --output "Sigma_head=..." --justification approximation

# 6. 打包提交
aitp derive pack gw-headwing --candidate-id v1
aitp candidate submit gw-headwing --candidate-id v1 --type research_claim \
    --claim "Head-wing correction modifies GW self-energy by..."

# 7. 形式化验证或数值计算
aitp sympy execute gw-headwing --candidate v1       # formal_theory lane
aitp compute prepare gw-headwing --candidate-id v1   # code_method lane

# 8. 对抗审查 → 晋升
aitp verify run gw-headwing --candidate v1
aitp verify results gw-headwing --candidate v1
aitp promote gw-headwing --candidate v1
```

每个命令都有 `--help`。完整的 21 个命令参考运行 `aitp --help`。

## Design principles

- **溯源优先** — 每个 claim 必须有 source_ref，每个 L2 node 必须有 provenance
- **人类拥有信任** — promotion gate 存在是因为 "AI 看起来很自信" 不是有效理由
- **文件即状态** — 纯 Markdown + YAML frontmatter，不依赖数据库、不丢失于会话
- **两速设计** — 探索时零阻力 (quick mode)，提交时硬拦截 (standard/full)
- **两条 lane** — `code_method` (HPC + domain invariants) 和 `formal_theory` (SymPy + analytic)，可在项目中切换
- **Agent 无关** — 任何能说 MCP 的 Agent 都能驱动协议

## License

MIT. See [LICENSE](LICENSE).
