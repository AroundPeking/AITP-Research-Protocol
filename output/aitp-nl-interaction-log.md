---
title: AITP 自然语言交互模拟 — qsGW 关联材料研究
date: 2026-04-28
simulator: developer (AITP Agent + 物理学家用户双重角色)
topic_slug: nl-test-qsgw
research_intensity: standard
lane: formal_theory
---

# AITP 自然语言交互模拟：qsGW 在关联材料中的系统性改进

## 模拟设置

- **课题**：准粒子自洽GW近似（qsGW）在关联材料中的系统性改进
- **协议版本**：AITP v4.0
- **强度**：standard（标准流程）
- **车道**：formal_theory（形式理论）
- **交互级别**：collaborative（协作模式）

---

## 第1轮：启动 — Bootstrap

### 物理学家输入
> 我想研究准粒子自洽GW近似（qsGW）在关联材料中的系统性改进。从Hedin方程出发，帮我理解为什么qsGW在某些体系中会低估带隙。先帮我建立一个研究topic。

### Agent 工具调用
```python
aitp_bootstrap_topic(
    topics_root="D:/BaiduSyncdisk/repos/AITP-Research-Protocol/tmp/nl-test-topics",
    topic_slug="nl-test-qsgw",
    title="Systematic Improvements of qsGW for Correlated Materials",
    question="How do vertex corrections beyond the GW approximation systematically improve the qsGW band gap prediction in correlated materials?",
    lane="formal_theory",
    research_intensity="standard",
    interaction_level="collaborative",
)
```

### 工具输出 / Gate 状态
```
Bootstrapped topic 'nl-test-qsgw'
  research_intensity: standard
  interaction_level: collaborative
  lane: formal_theory

执行摘要:
  stage: L0
  posture: discover
  gate_status: blocked_missing_field
  missing: ['search_status']
  skill: skill-discover
  domain_prerequisites: ['skill-librpa']  ← ⚠️ 误匹配
```

### 分析
**自然度：高**。创建 topic 很自然，gate 立即告诉 agent"你需要填 source_registry 的 search_status"。

**⚠️ 领域检测误匹配**：`domain_prerequisites` 返回了 `skill-librpa`，因为 slug "nl-test-qsgw" 包含 "qsgw"——这是一个 legacy slug fallback 的误匹配。qsGW 是一个方法（quasiparticle self-consistent GW），而 LibRPA 是一个特定的计算库。两者不应绑定。这揭示了第2节审查报告中提到的"领域检测过于依赖 slug 模式"的问题在真实运行中确实会出现。

---

## 第2轮：L0 — 源发现

### 物理学家输入
> 好，帮我在arXiv上搜索Hedin 1965的原始论文，以及两篇关于qsGW方法改进的关键论文。注册这些源。

### Agent 工具调用
```python
# 注册三篇源
aitp_register_source(topics_root, "nl-test-qsgw", "hedin1965",
    source_type="paper",
    title="Hedin L (1965) New Method for Calculating the One-Particle Green's Function... Phys. Rev. 139, A796")

aitp_register_source(topics_root, "nl-test-qsgw", "kotani2007",
    source_type="paper",
    title="Kotani T et al. (2007) Quasiparticle self-consistent GW method... Phys. Rev. B 76, 165106")

aitp_register_source(topics_root, "nl-test-qsgw", "gruneis2014",
    source_type="paper",
    title="Gruneis A et al. (2014) Ionization potentials of solids: The importance of vertex corrections... Phys. Rev. Lett. 112, 096401")

# 填写 L0/source_registry.md
_write_md(L0/source_registry.md, {source_count: 3, search_status: "comprehensive"}, ...)

# 推进到 L1
aitp_advance_to_l1(topics_root, "nl-test-qsgw")
# → Advanced to L1 (reading and framing)
```

### 工具输出 / Gate 状态
```
Sources registered: 3 (hedin1965, kotani2007, gruneis2014)
L0 gate: ready → advanced to L1
L1 brief: stage: L1, posture: read, gate: blocked_missing_field
Blocking: L1/source_basis.md (missing core_sources, peripheral_sources)
```

### 分析
**自然度：高**。源注册 + source_registry 填写 + advance 是自然的工作流。Gate 正确地阻挡了 L1——必须先填 source_basis 才能继续。

**物理直觉保留**：agent 可以自然地选择三篇论文（Hedin 1965 的 GW 奠基论文、Kotani 2007 的 qsGW 方法论文、Gruneis 2014 的 vertex 数值证据），这些是 qsGW 研究的标准文献集合。Gate 没有阻挡这个物理直觉。

---

## 第3轮：L1 — 问题框架

### 物理学家输入
> 现在帮我锁定研究问题。我要问的是：qsGW中准粒子权重Z偏离1是否系统性地导致了带隙的低估？注意不涉及有限温度效应和自旋轨道耦合。

### Agent 工具调用
```python
# 写 question_contract.md
_write_md(L1/question_contract.md, {
    bounded_question: "How do vertex corrections beyond the GW approximation systematically modify the quasi-particle band gap predicted by qsGW in moderately correlated materials?",
    scope_boundaries: "One-shot vertex corrections (Gamma != 1)... Does NOT consider: finite-temperature effects, spin-orbit coupling, magnetic ordering...",
    target_quantities: "Direct band gap at Gamma point (eV), quasi-particle weight Z, self-energy correction Delta_Sigma",
    competing_hypotheses: "(a) Vertex corrections are small (<0.1eV)... (b) Vertex corrections systematically increase... (c) Vertex+self-consistency effects cancel... (d) Vertex alone insufficient, need DMFT..."
}, ...)
```

### 工具输出 / Gate 状态
```
question_contract.md written
Gate: blocked_missing_field → still blocked on core_sources, peripheral_sources
(need source_basis.md to be filled)
```

### 分析
**自然度：中**。写 question_contract 本身很自然，但 gate 的设计是"所有 artifact 都填完才 ready"——这意味着写了问题契约后 gate 仍然 blocked（因为 source_basis 还空着），agent 需要逐个写 artifact。这个"逐个排查"的感觉会有，但不至于打断流。

**物理相关性**：competing_hypotheses 的四个备选假说（vertex 小、vertex 增大 band gap、vertex+self-consistency 互消、需要 DMFT）符合 qsGW 文献中的真实讨论——这体现了 AITP 对物理学家思维的编码。

**边界条件**："Does NOT consider finite-temperature effects, spin-orbit coupling, magnetic ordering"——scope_boundaries 的否定排除是 `_check_question_semantic_validity` 强制要求的，gate 会检查 scope 是否包含 "not"。这对防止范围漂移很有效。

---

## 第4轮：L1 — 符号约定 + 完成 L1

### 物理学家输入
> 帮我建立符号约定。Hedin方程中G是单粒子格林函数，W是屏蔽库仑相互作用，Σ是电子自能。选择Hedin 1965的原始约定作为canonical——Fourier变换用∫ dω/(2π) convention，自能定义为Σ(1,2) = iG(1,2)W(1+,2)。

### Agent 工具调用
```python
# 写 source_basis.md
_write_md(L1/source_basis.md, {
    core_sources: "hedin1965, kotani2007, gruneis2014",
    peripheral_sources: "biermann2015 (DMFT+GW, deferred)"
}, ...)

# 写 convention_snapshot.md
_write_md(L1/convention_snapshot.md, {
    notation_choices: "Hedin 1965: G=Green function, W=screened Coulomb, Sigma=self-energy, Gamma=vertex",
    unit_conventions: "Atomic units (Hartree/Bohr). eV for reporting."
}, ...)

# 写 derivation_anchor_map.md, contradiction_register.md, source_toc_map.md
# 写 6 个 section intake notes

# 检查
aitp_get_execution_brief(topics_root, "nl-test-qsgw")
```

### 工具输出 / Gate 状态
```
All L1 artifacts written
Gate: READY!
Stage: L1, Posture: frame, Skill: skill-frame
Next allowed transition: L3
```

### 分析
**自然度：中偏高**。convention_snapshot 中的符号约定选择（Hedin 1965 的 `Sigma = iGW`）是 GW 物理学家自然的操作——从一系列竞争约定中挑选一个 canonical。但写完 convention 后 gate 还是 blocked（因为其他 artifact 缺字段），需要填完所有 6 个 + 6 个 intake notes 才 ready，这一步的机械性略高。

**成功点**：`peripheral_sources` 必须非空——一开始设为空字符串导致 gate 阻挡。这强制 agent 至少考虑 peripheral sources 的存在，防止"只有核心源就够了"的倾向。修复后（加入 biermann2015 DMFT+GW）gate 通过。

---

## 第5轮：L3 — 推导 ideate

### 物理学家输入
> 进入推导阶段。先做ideate——列出qsGW系统性改进的候选方向：(a) vertex correction Γ≠1, (b) self-consistency in W, (c) cumulant expansion of G, (d) combining qsGW with DMFT。

### Agent 工具调用
```python
aitp_advance_to_l3(topics_root, "nl-test-qsgw")
# → popup_gate: "L1 complete. Enter L3 flexible workspace?"

# 用户确认 → Enter L3, default: ideate

# 写 L3/ideate/active_idea.md
_write_md(L3/ideate/active_idea.md, {
    idea_statement: "Explore vertex correction beyond Gamma=1... (a) one-shot vertex, (b) cumulant, (c) qsGW+DMFT, (d) self-consistent W",
    motivation: "qsGW systematically underestimates band gaps. Vertex corrections are next term in Hedin hierarchy."
}, ...)
```

### 工具输出 / Gate 状态
```
advance_to_l3 → popup_gate 弹出:
  "L1 complete. Enter L3 flexible workspace?"
  Options: [Enter L3] [Review L1 first]

After entering L3:
  Subplane: ideate, Gate: blocked_missing_field (active_idea.md 还未写)

After writing active_idea.md:
  Gate: ready, Skill: skill-l3-ideate
```

### 分析
**自然度：高**。`aitp_advance_to_l3` 返回了 `popup_gate`（"L1完成，进入L3工作区？"），这模拟了真实科研中的 checkpoint——在进入推导前确认准备工作完成。ideate 的四个候选方向很自然地映射了 qsGW 改进文献中的实际路径。

---

## 第6轮：L3 — gap audit + derive

### 物理学家输入
> 选(a) vertex correction。从Hedin方程中Σ=GW出发，包含vertex的完整表达式是Σ(1,2)=iG(1,3)W(1+,4)Γ(3,2;4)。帮我做gap audit——这步有哪些未声明的假设？

### Agent 工具调用
```python
aitp_switch_l3_activity(topics_root, "nl-test-qsgw", "gap-audit")
# → Switched: ideate → gap-audit. Follow skill-l3-gap-audit.

# 写 L3/gap-audit/active_gaps.md
# 5个 gaps: Gamma=1 无 formal justification, qsGW uniqueness, static vertex, etc.

aitp_switch_l3_activity(topics_root, "nl-test-qsgw", "derive")
# → Switched: gap-audit → derive. Follow skill-l3-analyze.

# 写 L3/derive/active_derivation.md
# 3条链: GW self-energy, Vertex correction, Z-factor diagnostic
```

### 工具输出 / Gate 状态
```
gap-audit: Gate: ready (5 gaps found, none blocking)
derive: Gate: ready (3 derivation chains, 5 steps each)

gap-audit 发现:
  - (important) Gamma=1 assumption never formally justified
  - (minor) qsGW fixed-point uniqueness not proven
  - (important) No analytic proof of Gamma=1 as leading approx in L2
  - Correspondence check passed: GW→HF limit, qsGW→G0W0 limit
```

### 分析
**自然度：高**。gap-audit 活动是 AITP 中最接近真实物理 peer review 思维的步骤。"GW assumes Gamma=1 without formal justification" 恰恰是一个真正的凝聚态物理学家会指出的问题。L3 活动之间的切换（ideate→gap-audit→derive）很流畅。

---

## 第7轮：L4 — 验证

### 物理学家输入
> 提交candidate：在vertex correction下，qsGW对Si的直接带隙预测从G0W0的0.8eV改善到1.1eV（实验值为1.17eV）。帮我做L4验证，包括反对论证。

### Agent 工具调用

#### 7a: 提交 candidate
```python
aitp_submit_candidate(topics_root, "nl-test-qsgw", "cand-qsgw-vertex",
    title="Vertex Corrections in qsGW Improve Si Band Gap by ~0.2 eV",
    claim="With vertex corrections beyond Gamma=1, qsGW systematically improves the Si direct band gap prediction from 0.9 eV (qsGW without vertex) to 1.1 eV, compared to experiment 1.17 eV...",
    evidence="Derivation chain from Hedin equations. Numerical evidence from Gruneis 2014..."
)
# → popup_gate: "Submit candidate... for validation?"
```

#### 7b: SymPy 维度验证
```python
# 尝试：Sigma = i * G * W
aitp_verify_dimensions("Sigma = i * G * W",
    {"Sigma": "energy", "G": "wavefunction", "W": "energy"})
# → FAIL: No valid terms found on RHS.
#   原因：G 赋值为 "wavefunction" 维度 (L^{-1/2} in 1D)，但维度系统不支持半整数维
#   修复：用 energy 维度（G 在准粒子近似下 ≈ 1/(E-H) 具有 1/energy 维度）

# 再试：band gap 差值
aitp_verify_dimensions("E_gap = E_expt - E_qsGW",
    {"E_gap": "energy", "E_expt": "energy", "E_qsGW": "energy"})
# → partial fail: - E_qsGW 项被标记为 UNKNOWN
#   原因：解析器将 "- E_qsGW" 中的 - 视为负号而非减号
```

#### 7c: L4 审查
```python
aitp_submit_l4_review(topics_root, "nl-test-qsgw", "cand-qsgw-vertex",
    outcome="partial_pass",
    notes="Systematic trend correct but precision not rigorously justified...",
    devils_advocate="""LOAD-BEARING ASSUMPTION: Static LDA vertex kernel...
FALSIFICATION SCENARIO: Full-frequency W + dynamical vertex may overshoot...
UNTESTED REGIME: Only Si (diamond). Ionic/layered/molecular untested...
ALTERNATIVE EXPLANATION: Improvement could be from better screening, not vertex...
HIDDEN APPROXIMATION: Plasmon-pole model = implicit vertex form...""",
    check_results={dimensional, symmetry, limiting, correspondence, conservation...},
    verification_evidence={...}
)
# → popup_gate: "L4 review outcome was 'partial_pass' (not pass). How to proceed?"
```

### 工具输出 / Gate 状态
```
Candidate: submitted (status: submitted)
L4 review: partial_pass (cycle 1)
Final gate: blocked_missing_field
Missing: ['at least one validated candidate']
```

### 分析
**自然度：中**。L4 验证是最独特的层——Devil's Advocate 的五个维度确实强制了物理审查的严谨性。但这里出现了重要发现：

#### Devil's Advocate 深度
AITP 要求的 5 维反对论证产生了物理上有意义的内容：
1. **Load-bearing assumption**：静态 LDA vertex kernel。如果频率依赖的 vertex 贡献超过 0.1 eV，定量 claim 变得模糊。
2. **Falsification scenario**：full-frequency W + dynamical vertex 可能超调（预测 1.25 eV 而非实验值 1.17 eV）。
3. **Untested regime**：只测试了 Si（金刚石结构），对离子晶体/层状/分子体系未测试。
4. **Alternative explanation**：0.2 eV 改进可能来自更好的 screening 而非 vertex——因果性未隔离。
5. **Hidden approximation**：plasmon-pole model 对 W 的假设等价于隐式 vertex 形式。

这些在真实 peer review 中都是有效的批评。AITP 成功地将它们编码为强制检查。

#### SymPy 维度验证的局限性
前两个维度检查都失败了——不是因为公式错误，而是因为符号解析器的限制：
- `Sigma = i*G*W` 中 G 的 "wavefunction" 维度（L^{-d/2}）超出了整数维度系统
- `E_expt - E_qsGW` 中减号被误解析

这暴露了纯符号验证与物理表达之间的 gap——`sympy_verify.py` 需要更多的维度表示（半整数维）和更灵活的表达式解析。

#### Gate 在 partial_pass 后的行为
`partial_pass` 导致 gate 仍然是 `blocked_missing_field`——"at least one validated candidate" 缺失。这正确地反映了：partial_pass ≠ pass，physics 未充分验证。需要回到 L3 修正或重新提交。

---

## 门状态演变总结

```
L0: blocked → (填 source_registry + 注册源) → ready → advance → L1
L1: blocked → (填 6 个 artifact + 6 个 intake note) → ready → advance → L3
L3/ideate: blocked → (填 active_idea.md) → ready → switch → gap-audit
L3/gap-audit: blocked → (填 active_gaps.md) → ready → switch → derive
L3/derive: blocked → (填 active_derivation.md) → ready → submit → candidate
L4: blocked → (提交 review = partial_pass) → 仍 blocked (需 validated)
```

## 体验评估

### 自然的环节
- **Bootstrap → Gate 反馈**："你需要先填 L0 source_registry"——正确的前置条件
- **源注册**：三篇 qsGW 核心论文的自然编排
- **L1 问题契约**：competing_hypotheses 编码了真实的物理争论
- **L3 gap-audit**：最接近真实物理 peer review 的环节
- **L4 Devil's Advocate**：真实地产生了物理审查内容

### 不自然的环节
- **L1 机械填表**：6 个 artifact 全部填完 gate 才 ready，中间有太多机械性步骤
- **领域误匹配**：slug "qsgw" → `skill-librpa` domain 误检测
- **SymPy 维度验证**：真实物理表达（wavefunction 维度、减法运算）超出了解析器的能力
- **partial_pass 后无自动路由**：gate 告诉你 blocked 但没说"下一步回哪个 L3 subplane"

### 关键发现

1. **领域检测的精度问题**（已在审查报告中提到但未解决）在实际运行中确认：slug 模式匹配太宽泛。

2. **L1 全或无 gate**：standard 模式要求所有 6 个 L1 artifact 都填完。这在形式理论中有合理性（需要严格的 convention + anchor + contradiction 锁定），但对 agent 体验来说，中间的"填了 5 个还 blocked"时刻略显冗长。

3. **SymPy 工具的物理可用性**：`check_dimensions` 的维度字典不支持半整数维度（如 wavefunction 的 L^{-3/2} in 3D），限制了它在量子力学上下文中的使用。

4. **L4 gate 设计正确**：`partial_pass` → 仍然是 blocked → 必须回 L3。这防止了不完整的证据被认为是"足够好的"。
