# 照镜子 / Finding Blind Spots

一个以证据为基础的问题发现与纠偏 Skill。它帮助你把“哪里不对但说不清”变成可验证的问题，也能在 AI 辅助工作中发现目标漂移、重复无效尝试、过度准备、未经验证的确信和高风险遗漏。

当前版本：`v0.1.1`（公开测试版）

## 它能做什么

- **问题澄清**：一次只问一个高价值问题，把模糊感受还原为具体事件、行为和结果。
- **工作纠偏**：从当前对话或产物中识别最关键的问题，只给一个有证据的下一步。
- **深度审视**：在用户明确同意后，分析重复模式、反例、置信度、80/20 取舍和现实实验。
- **低打扰触发**：普通任务保持安静；证据充分或风险较高时才提醒。
- **可撤回判断**：用户可以纠正、暂停或拒绝任何分析，Skill 不会为旧结论辩护。
- **自然表达**：使用自然、完整、尊重、有分寸的语言，不采用算命式反转、混合隐喻、假亲密或结尾金句。

## 核心原则

1. 从行为和结果找问题，不读心。
2. 区分观察事实、用户自述、推断、假设和未知。
3. 按需比较用户自述、实际行为、外部反馈和真实结果，不机械收集四类证据。
4. 先确认发生了什么，再把原因、动机或心理解释作为待验证假设。
5. 一次事件不能定义稳定人格。
6. 给出“当前最佳下一步”，不声称掌握唯一正确方法。
7. 连续两轮没有新事实、反证或可区分预测时停止推演，但仍可继续倾听。

## 安装

### 方法一：Skills CLI（推荐）

```powershell
npx skills add https://github.com/ZhiNai1314/finding-blind-spots -g -y
```

查看仓库中可安装的 Skill：

```powershell
npx skills add https://github.com/ZhiNai1314/finding-blind-spots --list
```

### 方法二：Codex 手动安装

Windows PowerShell：

```powershell
git clone https://github.com/ZhiNai1314/finding-blind-spots "$env:USERPROFILE\.agents\skills\finding-blind-spots"
```

如果你配置了 `CODEX_HOME`，也可以放入：

```text
%CODEX_HOME%\skills\finding-blind-spots
```

修改后未出现在 Skill 列表时，新建一个任务或重启 Codex。

### 方法三：其他 Agent Skills 兼容工具

把整个仓库复制到该工具的用户级 Skills 目录。Claude Code 通常使用：

```text
~/.claude/skills/finding-blind-spots
```

不同工具的目录规则可能变化，优先查阅对应工具的官方说明。

## 使用

最简单的中文口令：

```text
照镜子
```

附带上下文：

```text
照镜子，我最近一直在准备，却迟迟没有把产品交给用户。
```

显式调用：

```text
$finding-blind-spots 帮我检查当前决策中有没有被忽略的假设。
```

深度审视：

```text
$finding-blind-spots 根据当前对话和我授权的记忆，对我做一次深度旁观者审视。
```

## 输出方式

日常纠偏只指出当前最关键的一个问题：

```text
问题：观察事实或明确标注的假设
证据：用户原话、操作、产物或结果
影响：继续下去的具体代价
下一步：现在最值得做的一件事
置信度：高 / 中 / 低
```

## 注意事项

- 这个 Skill 不是心理医生、心理测评或治疗工具。
- 它不会诊断抑郁症、创伤、依恋类型、人格障碍或潜意识动机。
- 它不能保证“彻底了解”任何人，只能根据可用证据提出可修正的判断。
- **隐私**：不要把密码、密钥、身份证件、客户机密或其他敏感资料交给 Skill。
- 长期记忆必须由用户授权；新发现的模式未经确认不得写入记忆。
- 医疗、法律、财务、安全和不可逆决策需要可靠来源或专业人员复核。
- 隐式调用由宿主 Agent 决定，不保证每个符合场景的请求都会自动触发。需要确定调用时使用 `$finding-blind-spots`。
- “照镜子”只表示自我审视口令，不应在购买镜子、图片镜面效果、相机或反射类任务中触发。

## 评测

仓库中的 `evals/evals.json` 包含 24 个行为场景，覆盖：

- 模糊问题与单问式澄清；
- 无证据读心和伪深度；
- 目标漂移、重复失败与过度准备；
- 高风险操作与恢复路径；
- 当前指令覆盖历史偏好；
- 用户撤回纠偏；
- 及时停止追问；
- 四类可选证据之间的差距与冲突；
- 事实先于原因、停止推演但继续倾听；
- 外部反馈仅在用户已经提供时评估；
- 占位符、错误搭配、混合隐喻和戏剧化表达；
- 中文“照镜子”正触发与字面镜子负触发。

这些场景用于行为回归，不代表已经完成临床、职业或人格有效性验证。

### 本地质量校验

Windows PowerShell：

```powershell
python -X utf8 scripts\test_validate_quality.py
python -X utf8 scripts\validate_quality.py source .
Get-Content .\response.txt -Raw | python -X utf8 scripts\validate_quality.py response -
Get-Clipboard | python -X utf8 scripts\validate_quality.py response - --prompt-text "别安慰我，不要幽默，只讲证据和不确定性。"
```

命令通过时输出 `PASS` 并返回退出码 0；发现占位符、禁用句式、戏剧化破折号、结尾金句或已知错误搭配时输出对应规则并返回退出码 1。`--prompt-text`用于检查用户明确限定的输出字段和情绪边界。只有明确邀请用户填写句式时，才为回复校验增加 `--allow-fill-in`。

## 目录

```text
finding-blind-spots/
├─ SKILL.md
├─ agents/openai.yaml
├─ references/
│  ├─ dialogue-protocol.md
│  ├─ work-mirror.md
│  ├─ deep-review.md
│  └─ evidence-safety.md
├─ evals/evals.json
└─ scripts/
   ├─ validate_quality.py
   └─ test_validate_quality.py
```

## English summary

Finding Blind Spots is an evidence-based Agent Skill for clarifying vague personal problems and correcting observable work or decision patterns. It separates facts from inference, avoids unsupported psychological claims, asks one high-value question at a time, and moves from explanation to a reversible reality test.

Install:

```bash
npx skills add https://github.com/ZhiNai1314/finding-blind-spots -g -y
```

Use explicitly with `$finding-blind-spots`, or use the Chinese conversational command `照镜子` in hosts that support implicit Skill invocation.

## 设计参考 / Acknowledgements

这个 Skill 独立编写，没有复制其他仓库的提示词或问题库。设计过程中参考了以下开源项目的思路：

- [ergini/socratic-method](https://github.com/ergini/socratic-method)：用外部证据检验关键假设，MIT License。
- [Thomaszhou22/self-refine-skill](https://github.com/Thomaszhou22/self-refine-skill)：生成、批评、修正与检查循环，MIT License。
- [SwePalm/socratic-skill](https://github.com/SwePalm/socratic-skill)：高价值澄清问题与显式假设，CC BY 4.0。

The implementation and wording in this repository are original. The projects above informed the general design direction and remain subject to their own licenses.

## License

MIT License. See [LICENSE](LICENSE).
