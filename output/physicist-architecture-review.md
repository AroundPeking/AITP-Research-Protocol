---
reviewer: developer (理论物理学家视角)
date: 2026-04-28
review_type: 深度架构审查
scope: AITP v4.0 全部 Python 代码 + 关键文档
---

# AITP Research Protocol v4.0 — 理论物理学家架构审查报告

## 总体评价

AITP 是一个认真对待理论物理工作流的协议。它不是"用 AI 写论文"的玩具——它试图在 AI agent 的对话循环中植入理论物理学家日常工作的核心纪律：**来源追踪、假设显式化、推导可审计、验证对抗性**。代码质量扎实，测试覆盖良好（141/141 pass），从 L0 到 L4 的门模型（gate model）形成了一套逻辑自洽的流程。

但作为实际做 GW、多体微扰、QFT 计算的物理学家，我能感受到几个结构性的缺失——不是 bug，而是协议在建模物理研究时的缝隙。

---

## 1. 整体架构：L0-L4 五层是否合理？

### 架构图

```
L0 (discover) → L1 (read → frame) → L3 (derive) ⇄ L4 (validate) → L2 (knowledge)
```

### 优点

**L0 → L1 → L3 的线性流 + L3 ⇄ L4 的对抗循环 + L2 作为汇聚终点**，这个拓扑结构准确地反映了真实物理研究的节奏：
- L0 发现源 → 你确实需要先知道文献里有什么
- L1 阅读+框架 → 锁定问题边界、符号约定、推导锚点
- L3 推导 ⇄ L4 验证 → 这是核心循环，承认"推导-验证-回修"是迭代的，不是一次通过的
- L2 作为终点 → L5（写作）被移除了，这是 v4 的好决定。纸是人的事。

**L2 同时是起点和终点**的设计是深刻的——每个新 topic 从查询 L2 开始（"前人已经验证了什么？"），每个完成 topic 将结果推入 L2。这模拟了物理学作为累积学科的实质。

**两个路径（Path A: L0→L2 轻量级，Path B: L0→L1→L3→L4→L2 深度）**对应了真实科研中两类工作：引用已知结果 vs. 验证新 claim。不需要所有工作都走完整流水线。

### 问题

**L1→L3 的直接跳越（没有 L2 的中间状态）是一个遗漏**。在真实的物理工作中，好的 L1 阅读会在提取概念的同时立即建立初始 L2 图结构——事实上 `skill-read.md` 和 `aitp_batch_extract_section` 已经做到了这一点。但架构图显示 L1→L3 没有途经 L2，而实际上 L1 intake 阶段就在创建 L2 节点和边了。架构图和实际工作流脱节。

**L3 的"灵活工作区"设计在实践中可能过于灵活**。8 个活动（ideate, plan, derive, trace-derivation, gap-audit, connect, integrate, distill）之间允许任意切换。设计意图是好的（不强制线性），但物理推导实际上有一定的结构：plan→derive→gap-audit→integrate→distill 是一个自然的 sequence。完全打乱可能让 agent 迷失。`skill-l3-analyze.md` 中已经定义了 escape hatches 和前后边关系，但 skill 文件之间的一致性不够——有些说"前向: integrate"，有些说"前向: distill 或 submit candidate"。

---

## 2. 逐层细节：物理学正确性

### 2.1 L0 — Source Discovery

**source_registry.md 的 Coverage Assessment 模板**写得很准确："Define the dimensions that matter for YOUR research question... choose dimensions that would block your derivation if missing." 这捕捉了真实的文献评估——不是数论文数，而是判断关键维度是否覆盖。

**L0_SOURCE_TYPES** 明确收窄了源的类型：`paper, preprint, book, dataset, code, experiment, simulation, lecture_notes, reference`。对于 GW 计算，这个列表足够了。但对于需要 interaction parameters（U, J）、Wannier 函数、赝势等领域，`experiment` 不够——缺少 `parameter_database` 或 `benchmark_set` 这种类型。

### 2.2 L1 — Reading & Framing

这是协议中最强的一层。

**question_contract.md 的 `_check_question_semantic_validity` 函数**（`state_model.py:491-550`）实施了三条真实物理学家会坚持的规则：
1. 问题必须包含问题词干（what, derive, compute...）
2. scope_boundaries 必须明确排除（"This question does NOT ask about..."）
3. target_quantities 必须有可测量/可计算的量

这个检查防止了无限探索——每个做物理的人都知道，不设边界的问题等于浪费时间的授权。

**convention_snapshot.md 的设计**是 AITP 真正成熟的一个信号。符号约定的冲突（Fourier 因子 2π vs 1/√(2π)、度规 mostly-plus vs mostly-minus、CS 归一化 k/(4π) vs k/(2π)）在真实物理协作中是最隐蔽的错误源。L1 要求锁定符号、L3 派生符号发现（"## L3 Discoveries" append）——这是深刻的设计。

**source_toc_map.md 的机械完整性要求**（必须列全部 section、skim 全部后 deep-extract 部分）直接针对 AI agent 的"挑选阅读"倾向。强制 TOC 全覆盖 + intake quality audit 防止了 agent 只读头几页就假装理解了整篇论文。

**intake note 的 argument role + authority level 双层标记**（`state_model.py:440-453`）是协议中最接近真实 peer review 思维的部分：
- `physical_principle` vs `algebraic_identity` vs `assumption` vs `approximation` vs `conjecture`
- `source_grounded` vs `provisional` vs `tentative`

在 GW 计算中，区分 "这个结果是 W 的解析结构必然导出的" 和 "这个是数值拟合给出的" 恰恰是可靠 vs 不可靠的分界线。AITP 将此编码为 intake 协议是明智的。

**缺失**：
- `competing_hypotheses` 在 quick 模式不要求。虽然 quick 是轻量级模式，但即使快速探测也应该知道 alternative——"RPA 是否足够，还是我们需要 vertex correction？" 这种问题在快速模式也应该至少有一个备选假说。
- 没有明确的结构来记录"对偶性线索"（duality hints）——比如当 source 暗示系统在某参数下有隐藏的粒子-空穴对称性，而这可能是推导的关键。Convention Snapshot 的 `## Unresolved Tensions` 勉强覆盖，但不够具体。

### 2.3 L2 — Knowledge Graph

**NODE_TYPES 和 EDGE_TYPES 的选择**（`state_model.py:1064-1099`）反映了严肃的理论物理思考：

**节点类型精准度**：
- `concept`, `theorem`, `technique`, `derivation_chain` 这些是标准分类
- `approximation`, `regime_boundary` 是关键补充——物理知识的核心不仅是"什么是正确的"，更是"在什么条件下是正确的"
- `negative_result`（被测试和排除的 claim）——做得非常好。失败的尝试和成功的尝试同等重要
- `caveat` 和 `diagram` 作为节点类型是罕见但明智的选择

**边类型**的物理学抽象水平很高：
- 标准依赖：`derives_from`, `proven_by`, `assumes`, `uses`
- 近似层级：`limits_to`, `specializes`, `generalizes`, `approximates`
- EFT 塔：`matches_onto`, `decouples_at`, `emerges_from` —— 这些专为 Wilsonian RG 思维设计
- **物理学特有关系**（`state_model.py:1094-1099`）是这个知识图谱区别于通用知识图谱的核心：
  - `dual_to`（Kramers-Wannier, AdS/CFT）
  - `conjugate_to`（Fourier 共轭，Legendre 共轭）
  - `perturbative_in`（展开在小参数中）
  - `superseded_by`（旧结果被新结果取代）
  - `invariant_under`（量在对称群下不变）

`dual_to` 的包含是 v4 的优雅补充——量子多体物理和 QFT 中，对偶性提供了最重要的非微扰信息（如 2+1D 中的粒子-涡旋对偶、1+1D 中的玻色化）。大多数知识图谱框架不包含这个概念。

**DOMAIN_TAXONOMY**（`state_model.py:1105-1142`）覆盖了主要领地。域是开放的（任何字符串有效），这避免了枚举不足的问题。

**缺失**：
- `justification_type` 列表中包含 `conjecture` 和 `gap`——这很好，但缺少 `numerical_evidence` 和 `experiment` 以外的另一种重要类型：`lattice_regularization`（晶格正规化——许多 QFT 结果只在特定 lattice regularization 下有效）
- 边类型缺少 `commutes_with` 或 `simultaneously_diagonalizable`——在量化与守恒律相关的推导中至关重要
- 没有直接的 `renormalizes` 边。`refines` 覆盖了部分语义，但 "A renormalizes B"（如 counterterm 抵消发散）是一个不同于 "A refines B" 的操作

### 2.4 L2 Embedding — l2_embedding.py

**字符 n-gram embedding**（`l2_embedding.py:70-77`）对于 L2 规模（数百个概念）的选择是务实的。不需要下载模型，离线工作，subword 匹配天然适合技术术语（"RPA" 匹配 "Random Phase Approximation" via rp+pa bigram）。`_PHYSICS_ALIASES` 覆盖了 GW/DFT/多体物理的主要缩写。

**`semantic_score` 函数**（`state_model.py:1703-1761`）使用了 LaTeX 归一化 + alias 扩展 + Jaccard-like token overlap。LaTeX 命令提取 bonus（`\sigma` → self-energy, correlation, many-body, Dyson）体现了对物理搜索需求的理解——物理学家用符号思维，不仅用单词。

**局限性**：字符 n-gram 在 256 维上的哈希碰撞会随概念数增加而加剧。1000 个以上概念后，区分精度显会下降。但当前 L2 规模下这不是实际瓶颈。

### 2.5 L3 — Derivation Workspace

**L3 的活动集合**（ideate, plan, derive, trace-derivation, gap-audit, connect, integrate, distill）形成了从想法到 claim 的完整链。特别是 `gap-audit` 和 `trace-derivation` 体现了对 source study 场景的认真处理——不是所有 L3 都是新推导，很多时候是追踪论文中的推导。

**derive 活动中的 round_type 字段**（`skill-l3-analyze.md:84-94`）——`derivation_round`, `source_restoration_round`, `numerical_or_benchmark_round`, `synthesis_round`——是对不同推导场景的细粒度区分。`source_restoration_round` 特别有用：从论文中恢复一个隐含的推导步骤，这在 GW 文献中极其常见（Hedin 1965 的原始方程就跳过了许多步骤）。

**步骤级推导纪律**（`skill-l3-analyze.md:98-111`）——每个步骤要求 equation + justification + step_origin + source_anchor + assumption_dependencies + open_gap。这是 derivation traceability 的最低标准。

**Failure Route Template**（`skill-l3-analyze.md:141-149`）记录"为什么看似合理的路径失败了"——这对长期研究项目来说价值极高。避免未来的 session 重复死胡同。

**问题**：
- **connect 活动**（概念连接）的目标含糊。在推导过程中，"连接两个概念"可以是任何事情——一条边、一个对应关系、一个类比。缺少具体的 artifact 结构和 exit condition 定义。
- **没有实验/数值验证在 L3 内部的直接通道**。`numerical_or_benchmark_round` 存在，但整个 L3 的心智模型偏向解析推导。对于做 GW 的物理学家，数值验证（"我的 RPA 能量在 Si 上收敛到 10 meV 以内"）和解析推导向样重要。

### 2.6 L4 — Validation

这是协议最独特、也最有哲学立场的一层。

**"你试图证伪，而非认证"**（`skill-validate.md:18-20`）——这捕捉了科学验证的核心精神。不是 checklist compliance，而是 adversarial review。

**5 维 Devil's Advocate**（`skill-validate.md:76-95`）：
1. Load-bearing assumption（如果违反则整个 claim 坍缩的假设）
2. Falsification scenario（具体的证伪条件）
3. Untested regime boundary
4. Alternative explanation
5. Hidden approximation

这是 v4.0 中我最欣赏的设计。在物理学中，最危险的错误不是计算错误（可以纠正），而是隐性假设（你不知道自己在假设什么）。5 维 Devil's Advocate 直接针对这个问题。

**SymPy 验证**（`sympy_verify.py`）：
- `check_dimensions`：维度分析是物理学最基本的自检
- `check_algebra`：代数恒等式验证
- `check_limit`：极限行为检查（"量子→经典对应"，"强耦合→弱耦合极限"）
- `validate_derivation_step`：15 种推导规则的每一步 SymPy 检查
- 这些都是纯符号计算，不涉及 LLM——确保证据独立于 AI agent 的判断

**INFERENCE_RULES** 列表（`sympy_verify.py:581-597`）映射了物理学推导的标准操作：multiply/divide/add/subtract both sides, substitute, expand, factor, simplify, differentiate, integrate, take_limit, series_expand, commutator_eval, apply_identity, rearrange。`commutator_eval` 的非对易算子支持（`_v_commutator_eval`）是量子力学的必要补充——它检测算子符号（长度≤2 或含_）并声明为 non-commutative。

**L4 的 `blocked_contradiction` 状态**（`state_model.py:1436-1449`）——合约矛盾的审查被标记为一个不同的 gate status，不是 fail。在物理学中，矛盾是最有价值的结果——它可能表示新物理。AITP 将其路由到特殊处理（"Resolve: (a) new physics found, (b) error in derivation, or (c) regime mismatch"）而非简单标记为失败，是正确的。

**`PHYSICS_CHECK_FIELDS`**（`state_model.py:1243-1249`）：
- `dimensional_consistency` ✓
- `symmetry_compatibility` ✓
- `limiting_case_check` ✓
- `conservation_check` ✓
- `correspondence_check` ✓

这 5 个检查是物理学验证的基础集合。`correspondence_check`（新结果是否在适当的 limit 下还原为已知结果）尤其重要——这是任何理论推导的首要可信度测试（"在 T→0 时是否还原到基态？""在 N=1 时是否还原到 Redlich 的结果？"）。

**缺失**：
- 缺少 `unitarity_check`。对于 QFT 中的 S-matrix 计算（如散射振幅），unitarity 是最基本的约束。对凝聚态物理（如 spectral function 的正定性）也适用。
- 缺少 `causality_check`。Kramers-Kronig 关系的因果性基础在 response function 计算中至关重要。
- SymPy 验证无法处理路径积分、泛函导数、或涉及非平凡拓扑的推导步骤。这不是 SymPy 的错——而是这些操作超出了符号计算系统的能力。AITP 需要 explicit 标注哪些步骤是"SymPy 无法验证的"，并转而依赖逻辑一致性检查。

### 2.7 Domain Skill System

**Domain skill 机制**（`state_model.py:35-49`, `skill-librpa.md`）是 AITP 的扩展点设计。`skill-librpa.md` 展示了 domain skill 应该是 add-on（添加 LibRPA-specific knowledge），而不是 override（AITP 协议已经处理了通用部分）。

LibRPA domain skill 中的 **5 个领域不变量**（shrink_consistency, same_libri, keyword_compat, smoke_first, toolchain_consistency）都是从实际 GW 计算经验中提取的——这些是真实计算中最常见的故障点。

**问题**：目前只有一个 domain skill（skill-librpa），但 `DOMAIN_ID_TO_SKILL` 的设计暗示可以有更多。domain skill 的编写指南不够详细——什么应该进入 domain skill vs. 什么应该在 topic contract 中声明？边界模糊。

---

## 3. 真实物理学家使用体验

### 如果你做 GW 计算（LibRPA 工作流）

AITP 对 LibRPA 用户非常合适。`skill-librpa.md` + `domain-manifest.abacus-librpa.json` 提供了从 SCF 到 LibRPA 后处理的工作流映射。5 个不变量是真实计算中的故障点。L4 的数值证据要求（`evidence_scripts`, `evidence_outputs`, `execution_environment`）恰好映射了"我运行了什么、输出是什么、在哪台机器上"的记录——对可重复计算来说至关重要。

### 如果你做量子多体理论（GW, BSE, DMFT）

L1/L2 的 convention snapshot、source type classification、edge types 非常适用。Hedin 方程的五条耦合积分微分方程的推导跨越了多篇论文，每篇用不同符号——convention_snapshot 的 canonical notation 选择 + unresolved tensions 记录在这个场景下价值极高。

**但有一个缺口**：DMFT 自洽性循环（impurity solver ↔ lattice Green's function）天生是迭代的，不是线性的。AITP 的 gate 模型是阶段性的（L0→L1→L3→L4），但自洽循环需要多次 L3→L4→L3 往返，每次都更新 self-energy。协议虽然允许 L3 ⇄ L4 循环，但没有显式的"自洽性回合"跟踪结构。

### 如果你做 QFT（散射振幅、反常、拓扑）

L2 的 EFT tower 结构（`L2_TOWER_TEMPLATE` + `matches_onto`/`decouples_at`/`emerges_from` 边类型）非常适合 Wilsonian RG 流分析。`conjugate_to` 边对 Legendre 变换共扼变量（如 T ↔ 1/T in modular invariance）很有用。

**但**：L3 derive 活动的微分几何需求（纤维丛、characteristic classes、index theorem）远远超出了 SymPy 的能力。协议虽然允许 `source_restoration_round` 来追踪论文推导，但缺少对几何/拓扑推导步骤的特定检查（homotopy invariance, gauge fixing consistency, BRST closure）。

### 如果你做凝聚态理论（拓扑绝缘体、强关联）

L2 的 `dual_to` 和 `invariant_under` 边类型对拓扑物理很有用。`regime_boundary` 节点类型有助于标记"这个拓扑不变量在该对称性破缺时不再保护"。

**但**：紧束缚模型、Wannier 函数、对称性指标（symmetry indicators）是凝聚态拓扑物理的核心对象——这些在当前的 node type 或 domain taxonomy 中没有专门体现。`electronic-structure` domain 覆盖了 DFT 方面，但拓扑能带论是另一个子域。

---

## 4. 缺失与不足（从物理实践出发）

### 4.1 结构性缺失

#### 4.1.1 数值/解析混合工作流

真实物理研究很少有纯解析或纯数值的。GW 计算同时涉及解析推导（Hedin 方程的 formal structure）和数值计算（Si 的能带）。AITP 将 `formal_theory` 和 `code_method`/`toy_numeric` 隔离在不同的 lane 中，但两者之间的交叉验证协议不够。当一个数值结果支持一个解析 claim 时（或矛盾时），如何在 L4 中记录和评估交叉验证？

#### 4.1.2 "近似控制"作为门的要求

物理学中最大的错误来源不是计算错误，而是**违反近似假设**——在耦合常数 λ=3 处使用微扰展开到二阶，或对强关联材料使用 GW 近似。AITP 的 L1 convention snapshot 记录了假设，L3 gap-audit 检查了 approximation regimes，但 L4 验证没有显式的"近似有效性检查"。应该有一个 `approximation_validity_check` 作为 PHYSICS_CHECK_FIELDS 的第 6 个字段。

具体例子：对于 GW 计算，`Z-factor`（准粒子权重）是一个内置的健康指标——Z≪1 意味着 GW 近似在失效。AITP 没有要求计算的指标附带其适用性范围。

#### 4.1.3 缺少"已知极限库"

许多推导的正确性首先通过对应原理来验证："在 T→0 时，我的结果还原为基态结果吗？""在 m→∞ 时，我的 Dirac 行列式还原为 CS term 吗？" AITP 的 L2 应该包含一个"已知极限"的子图——标准模型的已知极限（如量子谐振子在 n→∞ 时趋近经典，CS 理论在 k→∞ 时趋近 classical CS）。目前 L2 存储已验证的 claims，但没有显式的 "known_limits" 类别。

#### 4.1.4 缺少实验数据与理论的比较协议

L0 source types 包含 `experiment` 和 `simulation`，但 L4 验证中没有实验比较的显式机制。理论物理学中，与实验的比较是最强的验证形式。AITP 应该有一个 `experimental_comparison_check`——不仅是 "我的计算是否正确"，还有 "我的计算是否与已知实验数据一致"。

### 4.2 协议层面

#### 4.2.1 多源矛盾的分辨机制弱

L1 contradiction_register 记录了矛盾，但没有提供 resolution 的结构——只有 `blocking_status`。在 GW 文献中，常见的是多篇论文声称不同结果（如 Si 的 band gap 在 1.1-1.3 eV 之间），而差异来自不同赝势或 k-point 采样。AITP 应该有一个 resolution 策略："矛盾来自方法学差异→记录方法学差异→标记为 non-blocking" vs "矛盾来自物理差异→标记为 open question"。

#### 4.2.2 LaTeX 验证的链式依赖

`aitp_verify_derivation_chain` 可以对整个推导链做每步验证，但它依赖于每步的 `input_expr` 和 `output_expr` 都能解析为 SymPy 表达式。对于几乎任何涉及无限维（泛函积分）、非平凡拓扑（instanton, monopole）、或非对易几何的推导步骤，SymPy 都无法处理。AITP 缺少一个替代方案——当 SymPy 不可用时，推导链如何验证？

#### 4.2.3 "数值证据"的信任等级模糊

`JUSTIFICATION_TYPES` 中包含 `numerical_evidence`（"supported by computation but no analytic proof"），这是对物理中大量数值结果的诚实承认。但 numerical evidence 的质量差异巨大——从"在 2×2×2 k-mesh 上跑了一次"到"收敛到 10 meV 在 12×12×12 mesh + 10 个 band"。AITP 当前没有 numerical evidence 的质量分级。

### 4.3 代码层面

#### 4.3.1 mcp_server.py 的单体结构

~49 个 MCP 工具函数全部在一个文件中（`mcp_server.py` ~6000+ 行）。虽然工具本身组织良好，但代码层面的单体结构使维护和扩展变得困难。工具函数混合了 I/O、gate logic、和 physics validation——将这些拆分为独立的 concern 模块可以降低维护负担。

#### 4.3.2 semantic_score 的 LaTeX 匹配可能过度宽泛

`semantic_score` 中的 LaTeX 命令提取将 `\sigma` 扩展为 `self-energy, correlation, many-body, dyson`——这是 Heuristic 的，但在某些上下文中 `\sigma` 可能是 conductivity 或 Pauli matrix。当前 alias expansion 不区分上下文。

#### 4.3.3 测试覆盖中的物理内容偏少

测试覆盖了状态模型、路径解析、gate 评估、E2E pipeline——这些都是面向协议的。但缺少面向物理计算的测试：维度检查应该验证边界情况（half-integer 维度、角动量的维度），代数验证应该包含已知的非平凡恒等式（如 Baker-Campbell-Hausdorff 的简单情况），极限检查应该覆盖物理上有趣的极限（T→0, N→∞, hbar→0）。

---

## 5. 改进建议

### 5.1 高优先级（影响物理正确性）

1. **添加 `approximation_validity_check` 到 PHYSICS_CHECK_FIELDS**。在 L4 验证中，显式检查每个推导步骤的近似是否在声明的 regime 内有效。对于 GW 类计算，这包括 Z-factor check（准粒子权重是否接近 1？）和 spectral function 的正定性。

2. **在 L2 中添加 `known_limit` 节点类型**。这些节点存储标准模型的已知极限行为（如 "量子谐振子 → 经典谐振子 当 n→∞"），并在 L4 correspondence_check 中作为对照。这为 agent 提供了一个"对应原理测试库"。

3. **添加 `unitarity_check` 和 `causality_check` 到 physics check fields**。对 QFT 和 response function 计算最基本。

4. **为 numerical evidence 添加质量层级**。在 `JUSTIFICATION_TYPES` 或 `L4_OUTCOMES` 中增加 `numerical_evidence` 的精度等级（convergence_test_passed / benchmark_reproduced / exploratory_only / unresolved_discrepancy）。

### 5.2 中优先级（改善使用体验）

5. **为 DMFT/自洽场类问题添加 "自洽性回合" 跟踪**。在 L3/L4 循环中记录 self-consistency round 的编号和收敛度量。当前协议支持 L3 ⇄ L4 迭代，但没有显式的 convergence tracking。

6. **添加实验比较协议**。在 L4 中支持 `experimental_comparison_check`：声明的 observable 是否与已知实验数据一致？差异是什么？差异是否在误差范围内？

7. **为 connect 活动定义更具体的 artifact 结构**。当前 "concepts being connected + proposed edges" 太宽泛。应该要求具体的边类型、regime 条件、和证据等级。

8. **扩展 physics concept aliases**。特别是拓扑物理（topological insulator, quantum spin Hall, Kitaev chain, Majorana zero mode, axion insulator）和强关联物理（Mott transition, charge density wave, spin liquid, Kondo effect）。

### 5.3 低优先级（工程改进）

9. **拆分 mcp_server.py**。将工具函数按层（L0, L1, L2, L3, L4, cross-cutting）模块化。不影响功能，但显著改善可维护性。

10. **为 sympy_verify.py 添加更多物理恒等式测试**。包括 Baker-Campbell-Hausdorff 展开、Fermion 反对易关系的符号处理、以及简单模型的已知极限（如 1D Ising model 的 T→0 极限）。

11. **在 `semantic_score` 中添加上下文消歧**。当 `\sigma` 出现在上下文中包含 "conductivity" 时不应优先扩展为 "self-energy"。可以通过检查 co-occurring tokens 的 domain 特征来实现。

12. **增加 domain skill 编写指南**。目前只有一个 domain skill（skill-librpa），但域扩展非常容易——只需在 `DOMAIN_ID_TO_SKILL` 中添加条目。需要一个模板和指南："domain skill 应该包含什么、不应该包含什么、如何编写不变量、如何与其他 stage skill 协作"。

---

## 总结评分

| 维度 | 评分 | 备注 |
|------|------|------|
| 架构设计 | ★★★★☆ | L0-L4 + L2 作为端点的设计深刻。L1→L3 的跳跃需要与 L2 intake 同步对齐 |
| 物理学正确性 | ★★★★☆ | 边类型、convention、gate model 的物理抽象准确。缺少 unitarity/causality/approximation-validity 检查 |
| Agent 可操作性 | ★★★★★ | Skill 文件质量高。mandatory 讨论 round + escape hatches 提供了真正有用的 guardrails，不是 checklist 空壳 |
| 扩展性 | ★★★★☆ | Domain skill + open taxonomy + progressive-disclosure tool catalog 设计允许扩展但样本不足 |
| 代码质量 | ★★★★☆ | 测试覆盖高 (141/141)、atomic writes、路径安全、但单体文件过大 |
| **总体** | ★★★★☆ | **AITP 是目前我看到的最认真对待理论物理 AI 辅助的协议。不是玩具。可以用来做真正的物理研究。** |

---

## 审查方法学说明

本审查通读了以下所有文件：
- `brain/mcp_server.py`（~49 个 MCP 工具，全量 L0-L4 实现 ~6000+ 行）
- `brain/state_model.py`（gate model, artifact templates, domain skill, semantic search, ~1762 行）
- `brain/native_mcp.py`（MCP stdio transport, ~224 行）
- `brain/sympy_verify.py`（符号计算验证，dimension/algebra/limit/step/inference rule, ~985 行）
- `brain/l2_embedding.py`（L2 向量嵌入, ~198 行）
- `brain/mcp_adapters/claude_code_bridge.py`（~84 行）
- `hooks/session_start.py`, `hooks/compact.py`, `hooks/stop.py`, `hooks/hook_utils.py`
- `scripts/aitp-pm.py`, `scripts/aitp-local.py`
- `skills/` 下全部 15 个 skill 文件
- `tests/` 下全部 11 个测试文件
- `deploy/templates/claude-code/` 下全部模板
- `README.md`, `PROJECT_MEMORY.md`, `aitp-manifest.json`
- `contracts/` 和 `schemas/` 目录

审查视角：凝聚态/量子多体/QFT 理论物理学家（GW, BSE, DMFT, topological phases, QFT anomalies）
