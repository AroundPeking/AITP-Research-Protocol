# AITP 自然语言驱动可行性测试 — 多方向

> 测试日期: 2026-04-28
> 测试方法: 以理论物理学家身份，用自然语言模拟四个不同物理学研究方向，检验 AITP v4 协议对多领域的适应能力。
> 协议版本: v4 (flexible workspace, no forced subplane sequence)

---

## 测试总览

| 方向 | 领域 | 输入语句 | 核心检验点 |
|------|------|---------|-----------|
| 1 | 多体物理 (GW/RPA) | "我想研究准粒子自洽GW近似（qsGW）在关联材料中的系统性改进，从Hedin方程出发" | domain skill 触发、artifact 模板覆盖 |
| 2 | 量子场论/高能理论 | "验证在N=4 SYM中，强耦合极限下Wilson loop期望值与AdS对偶预测是否一致" | formal_derivation lane、L2 概念映射 |
| 3 | 凝聚态/拓扑 | "检验Berry曲率在非平庸拓扑相中的量子度规与超导转变温度的关联" | 跨领域概念映射、gate 阻挡直觉 |
| 4 | 交叉/方法论 | "机器学习势能面的uncertainty quantification与DFT计算误差的关联" | 交叉学科适应、自然语言→tool翻译 |

---

## 方向1: 多体物理 — qsGW 系统性改进

### 输入
> "我想研究准粒子自洽GW近似（qsGW）在关联材料中的系统性改进，从Hedin方程出发"

### L0: 源发现与注册

**自然语言→tool 翻译:**
- 关键词提取: "qsGW", "Hedin equations", "self-consistent GW", "correlated materials", "vertex corrections"
- 触发的 tool: `search_arxiv` (paper-search-mcp, Pattern B)
- 匹配的 physics aliases: `qsGW → quasiparticle self-consistent gw`, `self-energy → sigma`
- 建议的 search query: `"quasiparticle self-consistent GW" AND "Hedin" AND ("vertex correction" OR "systematic improvement")`

**gate 阻挡直觉:**
- L0 gate 要求 `source_registry.md` + 至少一个注册源 → 如果 agent 只搜索不注册，blocked_missing_artifact
- `search_status` 必须非空 → agent 必须记录搜索方法论，不能跳过
- `coverage_status` 维度需包含: method/regime/approximation order → 缺失任何一个都会被 blocked

**artifact 模板覆盖:**
| Artifact | 覆盖状态 | 备注 |
|----------|---------|------|
| source_registry.md | 适用 | Search Methodology 需包含 Hedin equation 导出链的搜索策略 |
| sources/*.md | 适用 | 至少需要 Hedin 1965 原始论文 + 至少一篇 qsGW review |

**domain skill 触发:**
- slug 检测: `qsgw` → `_SLUG_FALLBACK_PATTERNS` 匹配 `skill-librpa`
- 正确触发: agent 必须加载 `skill-librpa.md` 了解 LibRPA/qsGW 特有的收敛判据、基组约定、k-point 采样惯例
- **风险**: 如果 topic slug 不含 `qsgw` 或 `librpa`，则需要 contract-based 检测 (`domain-manifest.md/json`)

### L1: 阅读与框架

**自然语言→tool 翻译:**
- "从Hedin方程出发" → 需要 `derivation_anchor_map.md` 将 Hedin 1965 的方程链作为 starting anchor
- "系统性改进" → 需要 `question_contract.md` 明确定义什么算 "systematic improvement"（vertex correction? self-consistency? frequency dependence?）

**gate 阻挡直觉:**
- `question_contract.md` 的 `scope_boundaries` 必须包含 "NOT" 语句 → 例如 "This question does NOT ask about finite-temperature extensions of GW"
- `competing_hypotheses` 必须非空 → 需列出至少一个替代方案（如 "vertex corrections are unnecessary because of error cancellation in GW+W")
- `coverage_status` 必须为 `complete` 或 `partial_with_deferrals` → 如果 Hedin 方程链中某一步未充分提取，会被 blocked_coverage_incomplete

**artifact 模板覆盖:**
| Artifact | 覆盖状态 | 备注 |
|----------|---------|------|
| question_contract.md | 适用 | 需定义 "systematic improvement" 的可测量判据 |
| source_basis.md | 适用 | 核心源: Hedin 1965, 至少一篇 qsGW 方法论文 |
| convention_snapshot.md | 适用 | 需统一 GW 社区中的符号分歧（G vs G, W vs W, Σ 的不同定义） |
| derivation_anchor_map.md | 适用 | anchor 类型: Hedin 五边形方程链中的每个箭头 |
| contradiction_register.md | 适用 | 可能矛盾: qsGW 中 G 和 W 的迭代是否收敛到唯一不动点？ |
| source_toc_map.md | 适用 | 覆盖 qsGW 论文中每个方程节 |

**关键 gap:**
- `convention_snapshot.md` 的 "Categorized Assumptions" 要求区分 mathematical/physical/notational 三类 → 对 GW 理论，物理假设（准粒子图像成立）和数学假设（G 的解析结构）的边界难以清晰划分
- "Canonical Notation" 要求统一符号 → 不同 GW 实现（VASP, BerkeleyGW, FHI-aims）使用不同符号约定

### L3: 推导活动

**自然语言→tool 翻译:**
- "系统性改进" 的物理含义需要 `ideate` 活动展开
- 可能的 ideate 输出: vertex correction (Γ beyond Γ=1), self-consistency in G and W, cumulant expansion, stochastic GW

**gate 阻挡直觉:**
- L3 是 flexible workspace → 从 `ideate` 开始，不强制子平面顺序
- 但每个 activity 仍有 required_fields 和 required_headings
- `derive` 活动要求 `all_steps_justified` → 如果 Hedin 方程链中某步是 "it can be shown that..."，需要 `gap-audit` 标记

### L4: 验证

**gate 阻挡直觉:**
- 提交至少一个 candidate → 例如 "qsGW with vertex corrections improves band gaps by 0.3 eV over G₀W₀"
- 每个 candidate 必须有 review 且包含 counterargument
- 关键 counterargument: "vertex corrections may be within the error bars of the numerical implementation"
- domain invariant check: 如果 topic 注册了 `abacus-librpa` domain，需要验证 LibRPA 的不变量（如 basis set convergence, k-point convergence）

---

## 方向2: 量子场论/高能理论 — N=4 SYM Wilson Loop & AdS/CFT

### 输入
> "验证在N=4 SYM中，强耦合极限下Wilson loop期望值与AdS对偶预测是否一致"

### L0: 源发现与注册

**自然语言→tool 翻译:**
- 关键词: "N=4 SYM", "Wilson loop", "AdS/CFT", "strong coupling", "Maldacena"
- LaTeX 符号匹配: `\mathcal{N}=4`, `\langle W \rangle`, `\lambda \to \infty`, `\sqrt{\lambda}`
- physics aliases: `AdS/CFT` 虽未在 `PHYSICS_CONCEPT_ALIASES` 中直接出现，但 `qft` → `quantum field theory` 可触发
- 关键源: Maldacena 1998 (AdS/CFT), Rey-Yee 2001 (Wilson loop), Erickson-Semenoff-Zarembo 2000

**gate 阻挡直觉:**
- L0 gate 需要 `source_registry.md` → 至少需要 Maldacena 1998 + 至少一篇 Wilson loop 计算论文
- `search_status` 需记录搜索方法论 → 是只在 arXiv 搜索还是包含 hep-th citation graph 遍历？

**artifact 模板覆盖:**
| Artifact | 覆盖状态 | 备注 |
|----------|---------|------|
| source_registry.md | 适用 | 需包含 hep-th 文献的 Coverage Assessment |
| sources/*.md | 适用 | Maldacena 论文、Wilson loop 经典论文 |

**domain skill 触发:**
- **无直接 domain skill 匹配** — `_SLUG_FALLBACK_PATTERNS` 中无 AdS/CFT/SYM 条目
- 这意味着 formal_derivation lane 上 agent 不会收到专门的 domain 指令
- **gap**: AdS/CFT 背景 agent 需要知道 `large-N limit`, `'t Hooft coupling λ = g²N`, `AdS₅ × S⁵` 几何 → 但这些不会通过 domain skill 注入

### L1: 阅读与框架

**gates 阻挡直觉 — 关键问题:**
- `question_contract.md` 的 `bounded_question` 需要 question stem → "verify whether..." 可以被接受（虽不在 `_QUESTION_STEMS` 列表中，但语义接近 `determine`/`compare`）
- **风险**: 如果 agent 判断 `verify` 不是有效的 question stem → blocked_missing_field
- `scope_boundaries` 需要 NOT 语句 → 例如 "This question does NOT ask about 1/N corrections or instanton contributions"
- `target_quantities` → Wilson loop expectation value 是明确的 target quantity（有量纲/无量纲特性）

**artifact 模板覆盖:**
| Artifact | 覆盖状态 | 备注 |
|----------|---------|------|
| convention_snapshot.md | 部分适用 | N=4 SYM 的 convention snapshot 包括: 规范群 SU(N), 't Hooft 耦合定义, 欧氏 vs 闵氏度规 |
| derivation_anchor_map.md | 适用 | anchor: Maldacena 的低能 D-brane 论证、GKPW 关系 |
| contradiction_register.md | 适用 | 不同方法计算 Wilson loop 是否一致（Gaussian matrix model vs minimal surface） |

**convention_snapshot 的局限性:**
- N=4 SYM 的 "Categorized Assumptions" 主要是数学的（超对称性、共形对称性）→ assumption 分类在 QFT 语境下与材料物理不同
- "Canonical Notation" 在 hep-th 中习惯使用欧氏度规而 cond-mat 使用闵氏 → 模板不强制 agent 澄清度规选择
- "L3 Discoveries" (用于记录推导中发现的新约定) → AdS/CFT 推导中不会产生新的符号约定，只有已知约定的应用

### L2 概念映射

**现有 L2 节点/边类型覆盖度:**

| 概念 | 可用的 L2 节点类型 | 是否匹配 |
|------|-------------------|---------|
| N=4 SYM | `concept`, `theorem` | 适中的 |
| Wilson loop operator | `concept`, `equation` | 适中的 |
| AdS/CFT correspondence | `correspondence_link` (EFT tower), `dual_to` edge | 接近，但 AdS/CFT 不是 EFT tower |
| Strong coupling limit | `regime_boundary` | 适中的 |
| Minimal surface in AdS | `concept`, `derivation_chain` | 适中的 |
| String tension √λ/2π | `equation` | 适中的 |

**gap — 缺失的概念类型:**
- "duality"（对偶）有 `dual_to` edge，但 "holographic duality" 比 `dual_to` 更丰富：它涉及维度变换、耦合强弱反转
- EFT tower 的 `layers` 和 `matches_onto`/`decouples_at` 是为 RG flow 设计的，不适合 AdS/CFT 的 UV/IR 对应
- `correspondence_link` 模板的 `limit_condition` 字段可以用于描述 λ → ∞ 极限，但不够自然

### L3: 推导活动

**推导路径:**
1. `plan`: "计算强耦合 Wilson loop: 通过 AdS 最小面积 → compare with Gaussian matrix model result"
2. `derive`: 写出 Nambu-Goto 作用量 → 求经典解 → 在适当地时间坐标下求 on-shell 作用量 → 与场论结果比较
3. `gap-audit`: 标记以下步骤的证明缺口 — 为什么最小面积给出的是精确结果而不是 saddle-point 近似？

**gate 阻挡直觉:**
- `derive` 活动要求 `all_steps_justified` → 经典弦解的存在性 + 单圈修正 → 后者在大多数源中是 stated_with_sketch
- `gap-audit` 的 "Unstated Assumptions" → 例如 "the string worldsheet is smooth (no folds)" → 需要 agent 识别这个隐含假设

### L4: 验证

**gate 阻挡:**
- `dimensional_consistency` (PHYSICS_CHECK_FIELDS 之一) → 检查 `⟨W⟩ ∼ exp(√λ)` 的无量纲性
- `correspondence_check` → 与弱耦合微扰展开比较 → 在 λ ≪ 1 极限下必须匹配
- counterargument → "The AdS minimal surface computation assumes the string is classical — a full quantum string calculation might differ by O(1)"

**关键 obstacle:**
- `PHYSICS_CHECK_FIELDS` 的 `conservation_check` → Wilson loop 是规范不变的，但模板问 "conservation" 可能让 agent 寻找守恒流（不存在）

---

## 方向3: 凝聚态/拓扑 — Berry 曲率、量子度规与超导

### 输入
> "检验Berry曲率在非平庸拓扑相中的量子度规与超导转变温度的关联"

### L0: 源发现与注册

**自然语言→tool 翻译:**
- 关键词: "Berry curvature", "quantum metric", "topological phase", "superconducting Tc", "quantum geometry"
- LaTeX 符号: `\Omega_{\mu\nu}` (Berry curvature), `g_{\mu\nu}` (quantum metric), `T_c`, `\Delta`
- physics aliases: `Berry phase → geometric phase`, `Chern number → Chern invariant`
- 需同时搜索 cond-mat.supr-con + cond-mat.mes-hall 两个 arXiv 分类
- **关键入口论文**: Peotta-Törmä 2015 (superfluid weight from quantum metric), 可能需要多篇

**gate 阻挡直觉:**
- L0 gate 要求 `register at least one source in L0/sources/` → 但正确的第一源是什么？Peotta-Törmä? 还是 Berry 1984?
- `source_registry.md` 的 Coverage Assessment 维度自选 → 正确维度应为: spatial dimension (2D vs 3D), band topology (Chern number ≠ 0), interaction strength

### L1: 阅读与框架

**artifact 模板覆盖 — 跨领域概念映射问题:**
| Artifact | 挑战 |
|----------|------|
| question_contract.md | "superconducting Tc" 是一个 emergent quantity，它同时依赖 band structure topology (单粒子) 和 pairing interaction (多体) → `scope_boundaries` 必须明确排除纯单粒子图像 |
| derivation_anchor_map.md | 两个子领域的 anchor 需要跨领域连接: Berry curvature (几何) → superfluid weight (多体) → Tc (热力学) |
| convention_snapshot.md | Berry curvature 在多体论中可能有不同的符号约定；超导文献中的 gap function 符号与能带论中的 band gap 易混淆 |

**gate 阻挡直觉:**
- `question_contract.md` 的 `competing_hypotheses` → 需列出至少一个替代机制（如 electron-phonon coupling, BEC-BCS crossover 等可独立解释 Tc 的机制）
- `target_quantities` 必须有明确的可测量量 → "correlation with Tc" 过于模糊，agent 可能无法通过 gate
- 建议改写为: "compute ∂Tc/∂gᵢⱼ where gᵢⱼ is the quantum metric"

**convention_snapshot 的跨领域冲突:**
- Berry phase convention: 通常定义为 `-i⟨uₖ|∇ₖ|uₖ⟩` 或 `i⟨uₖ|∇ₖ|uₖ⟩` → 影响所有后续推导
- Superfluid weight 在数学上正比于 quantum metric 但仅在 flat-band 极限 → agent 可能忽略 regime 条件

### L2 概念映射

**跨领域映射检验:**

| 源自领域 A (拓扑) | → L2 连接类型 | → 目标领域 B (超导) |
|-------------------|--------------|-------------------|
| Berry curvature Ω | `motivates` / `derives_from` | Superfluid weight Dˢ |
| Quantum metric g | `generalizes` | BCS coherence length ξ |
| Chern number | `specializes` | Vortex winding number |
| Topological band | `assumes` | Flat-band condition |

**L2 节点类型覆盖度:**
- `regime_boundary` 可以用来标记 flat-band 条件 → 适用于
- `caveat` → 标记 "quantum metric alone does not guarantee high Tc — pairing mechanism still required" → 适用于
- `correspondence_link` 不适合这里的跨领域连接 → **缺失**: 需要 "cross-domain_bridge" 或类似的 edge 类型

### L3: 推导活动

**gate 阻挡直觉:**
- `derive` 活动需要从 Berry curvature 的最小耦合哈密顿量出发 → 多步骤推导
- `gap-audit` 的 "Approximation Regimes" → 需要 agent 理解 BCS 平均场近似的适用条件在平带极限下失效
  - 如果 agent 是纯凝聚态背景，可能忽略这个 subtlety

### L4: 验证

**counterargument 需求:**
- "The quantum metric-Tc correlation may be coincidental in specific models and not generalizable beyond flat-band systems"
- L4 review 的 "## Devil's Advocate" section → agent 需主动发现这个反论

---

## 方向4: 交叉/方法论 — ML 势能面的 UQ 与 DFT 误差

### 输入
> "机器学习势能面的uncertainty quantification与DFT计算误差的关联"

### L0: 源发现与注册

**自然语言→tool 翻译:**
- 关键词: "machine learning interatomic potential", "uncertainty quantification", "DFT error", "Gaussian approximation potential", "neural network potential"
- 交叉学科信号: ML (statistical learning theory) + DFT (computational chemistry/physics)
- physics aliases 中的 `dft → density functional theory` → 触发
- **无 ML 领域的 physics aliases** → "Gaussian process", "Bayesian", "active learning" 不在 `PHYSICS_CONCEPT_ALIASES` 中

**gate 阻挡直觉:**
- `search_status` 需记录搜索方法论 → 需要同时搜索 physics (cond-mat.mtrl-sci) 和 ML (stat.ML, cs.LG) 领域 → agent 是否知道跨 arXiv 分类搜索？
- Paper-search-mcp 默认搜索物理文献，可能遗漏 ML 领域的关键论文

### L1: 阅读与框架

**convention_snapshot 的领域间符号冲突:**
| 概念 | 物理社区 | ML 社区 |
|------|---------|---------|
| Uncertainty | "error bar" (通常不量化) | "predictive variance" / "epistemic vs aleatoric" |
| Model | "functional XC approximation" | "neural network architecture" |
| Loss function | "energy minimization" | "MSE on forces" |
| Convergence | "k-point and cutoff convergence" | "train/validation loss convergence" |

- `convention_snapshot.md` 的 "Canonical Notation" 和 "Unresolved Tensions" 部分需要 agent 主动进行跨领域术语映射
- **AITP 目前不提供跨领域 ontology mapping** — agent 需要自己理解 "UQ" 在物理和 ML 中的不同含义

**question_contract 的挑战:**
- 什么是 UQ 的 "target quantity"？→ 可以是 calibration error, sharpness, dispersion 等
- 必须定义 "DFT calculation error" → 相对于 experiment? coupled-cluster? full CI?
- `competing_hypotheses` → 至少一个（如 "ML potential errors are dominated by training data bias, not DFT error"）

### domain skill 触发

- **无直接 domain skill 匹配** — 没有 `skill-ml-potential` 或类似技能
- `_SLUG_FALLBACK_PATTERNS` 中无 ML 相关条目
- `DOMAIN_TAXONOMY` 中无 "machine-learning" 或 "computational-materials" domain
- **这暴露了 AITP 的核心 gap**: 对交叉学科，既缺 domain skill 也缺 domain taxonomy entry

### L2 概念映射

**尝试映射到现有 L2 类型:**

| ML+DFT 概念 | 最近的 L2 节点类型 | 匹配度 |
|-------------|------------------|--------|
| ML potential (e.g. MACE, CHGNet) | `technique` | 低 |
| DFT error vs CCSD(T) reference | `approximation` | 中 |
| Epistemic uncertainty | `open_question` | 低 — 不是开放问题，是方法属性 |
| Active learning acquisition function | `technique` | 低 |
| Force prediction RMSE | `result` | 中 |

**缺失的 L2 节点类型:**
- `benchmark` — ML 领域的 standard benchmark datasets (e.g. MD17, QM9, rMD17)
- `methodology` — 用于描述方法论的元层次节点
- `calibration` — UQ 专有的校准概念
- `metric` — 评估指标（RMSE, MAE, E vs F error...）

### L3: 推导活动

**gate 阻挡直觉:**
- 研究路线的 "推导" 不完全是 pencil-and-paper → 可能涉及数据分析流水线
- `derive` 活动模板的 "Derivation Chains" + "Step-by-Step Trace" → 对于数据分析型研究，这些 heading 不够自然
- `plan` 活动的 "Tool And Knowledge Requirements" → 需要 agent 识别需要特定 ML package (e.g. `pyACE`, `fairchem`, `matgl`)

### L4: 验证

**FIX:**
- `PHYSICS_CHECK_FIELDS` 中的 `dimensional_consistency` → ML 势能面的 uncertainty 可能没有物理量纲
- `correspondence_check` → 与什么对应？实验？更高精度计算？
- **基本问题**: L4 的物理验证检查是为 pencil-and-paper derivation 设计的，不适合 computational methodology 研究

---

## 综合横切分析

### 1. 自然语言 → Tool 调用翻译

| 检验维度 | 评分 | 说明 |
|---------|------|------|
| 关键词提取 | 良好 | `PHYSICS_CONCEPT_ALIASES` 覆盖了大部分标准物理术语 |
| LaTeX 符号识别 | 良好 | `semantic_score` 的 LaTeX normalization 和 command extraction bonus 设计合理 |
| 跨 arXiv 分类搜索 | 不足 | 方向4 需要跨领域搜索，agent 可能不会自动意识到 |
| 非物理术语 (ML 词汇) | 缺失 | `PHYSICS_CONCEPT_ALIASES` 不包含 ML/numerical methods 领域术语 |
| 自然语言意图 → 具体 tool 路由 | 部分 | L0 discover 阶段 tool catalog 清晰，但 Pattern B tools 只有 `paper-search-mcp` 和 `scientific-brainstorming` |

### 2. Gate 阻挡直觉

| 检验维度 | 评分 | 说明 |
|---------|------|------|
| blocked_missing_artifact | 良好 | 所有四个方向都能正确触发：缺少 source registry / question contract 等 |
| blocked_missing_field | 良好 | frontmatter + heading 双重检查覆盖所有关键字段 |
| blocked_coverage_incomplete | 良好 | `coverage_status` 的 complete/partial_with_deferrals 二分 + intake 审计合理 |
| blocked_stuck | 适用 | 方向2 (AdS/CFT) 中 quantum string correction 可能导致 stuck |
| blocked_contradiction | 适用 | 方向3 中 flat-band 条件与 BCS 近似的矛盾可触发 |
| **question semantic validity** | **部分** | `_QUESTION_STEMS` 列表缺少 `verify`, `examine`, `test`, `investigate` → 可能错误阻挡 |
| **cross-domain gate gaps** | **不足** | 方向4 中 "derivation" 活动对数据分析型研究不自然 |

### 3. Artifact 模板覆盖

| Artifact 模板 | 方向1 (GW) | 方向2 (AdS/CFT) | 方向3 (拓扑) | 方向4 (ML+DFT) |
|---------------|-----------|----------------|-------------|---------------|
| source_registry.md | 适用 | 适用 | 适用 | 适用 |
| question_contract.md | 适用 | 适用 | 适用 | **需改写 target** |
| source_basis.md | 适用 | 适用 | 适用 | 适用 |
| convention_snapshot.md | 适用 | 部分适用 | 适用，但有冲突 | **跨领域映射困难** |
| derivation_anchor_map.md | 适用 | 适用 | 适用 | **不自然** |
| contradiction_register.md | 适用 | 部分适用 | 适用 | 部分适用 |
| source_toc_map.md | 适用 | 适用 | 适用 | 适用 |
| L3 derive | 适用 | 适用 | 适用 | **不自然** |
| L3 gap-audit | 适用 | 适用 | 适用 | 部分适用 |
| L3 distill | 适用 | 适用 | 适用 | 适用 |
| L4 review templates | 适用 | 适用 | 适用 | **物理检查不适用** |

### 4. Domain Skill 触发

| 方向 | 可触发的 domain skill | 触发机制 | 状态 |
|------|---------------------|---------|------|
| 方向1 (qsGW) | `skill-librpa` | slug fallback (`qsgw` in slug) | 正常触发 |
| 方向2 (AdS/CFT) | — | 无匹配 | **缺失 domain skill** |
| 方向3 (拓扑超导) | — | 无匹配 | **缺失 domain skill** |
| 方向4 (ML+DFT) | — | 无匹配 | **缺失 domain skill + domain taxonomy** |

**总体: 4 个方向中仅有 1 个触发 domain skill → 覆盖率 25%**

### 5. L2 概念映射

| 映射需求 | 现有支持 | gap |
|---------|---------|-----|
| AdS/CFT duality | `dual_to` edge, `correspondence_link` | 不完全: AdS/CFT 涉及维度变换，非简单对偶 |
| QFT regime boundary | `regime_boundary` node | 适中的 |
| Topology ↔ superconductivity | `motivates`, `derives_from` edges | 路径存在但体感不够精确 |
| Benchmark dataset | — | **缺失**: `benchmark` / `dataset` 节点类型 |
| UQ calibration | — | **缺失**: `calibration` / `metric` 节点类型 |
| EFT tower for QFT RG flow | `l2_tower` | 适中的 |

### 6. 阻碍和缺失 — 优先级排序

| 优先级 | 问题 | 影响方向 | 建议 |
|-------|------|---------|------|
| **P0** | `_QUESTION_STEMS` 缺少 `verify`, `test`, `examine`, `investigate` | 方向2, 3, 4 | 扩展 stem 列表或改为语义匹配 |
| **P0** | 无 ML/computational methods 的 physics aliases 和 domain taxonomy | 方向4 | 新增 `DOMAIN_TAXONOMY["computational-materials"]` 和对应 aliases |
| **P1** | L4 PHYSICS_CHECK_FIELDS 对计算方法学研究不适用 | 方向4 | 允许 lane 特定的 check 字段集，或增加 `methodology_lane` |
| **P1** | `derive` 活动模板不适合数据驱动型研究 | 方向4 | 新增 `benchmark` / `compute` 活动类型 |
| **P1** | 跨领域 convention 冲突无自动检测 | 方向3, 4 | `convention_snapshot.md` 的 Unresolved Tensions 需增加跨领域对比指引 |
| **P2** | AdS/CFT, 拓扑超导缺少 domain skill | 方向2, 3 | 按需创建 `skill-adscft` 和 `skill-topological-matter` |
| **P2** | EFT tower 模板不适用于 AdS/CFT 对偶 | 方向2 | 新增 `duality_link` 节点/边类型或放宽 `correspondence_link` 的语义 |
| **P3** | LaTeX alias `\\mathcal` 命令无直接匹配 | 方向2 | 增强 `normalize_latex` 或 `_ALIAS_LOOKUP` |
| **P3** | `conservation_check` 在规范理论语境下可能误导 | 方向2 | 将 `conservation_check` 重命名为 `invariance_check` 或增加语境文档 |

---

## 结论

**AITP v4 的自然语言驱动在以下方面表现良好:**
1. 标准凝聚态/多体物理（方向1）: 端到端流程清晰，domain skill 自动触发，artifact 模板完备
2. Gate 模型的基本阻挡逻辑（artifact 缺失、字段缺失、覆盖率不足）在所有方向上工作正常
3. `semantic_score` 的 LaTeX 提取和 alias 扩展对物理学方法类查询准确

**AITP v4 的自然语言驱动在以下方面存在显著 gap:**
1. 交叉学科（ML+物理）缺乏词汇表、domain skill 和适合的 artifact 结构
2. QFT/高能物理的推导风格（大量使用对称性论证、对偶映射、经典极限）与现有推导模板不完全匹配
3. L4 物理检查假设研究结果是 pencil-and-paper 推导 — 不适合 computational workflow 和 data-driven methodology
4. Domain skill 覆盖率仅 25%（4 中 1）— 需要大量扩充 registry

**总体判断：AITP v4 对凝聚态/多体物理的 formal_derivation 路线已具备较好的自然语言驱动能力，向 QFT、拓扑和交叉学科的推广还需要协议层面的结构性扩展。**
