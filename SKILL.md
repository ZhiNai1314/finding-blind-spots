---
name: finding-blind-spots
description: "Use when the user uses '照镜子' as a standalone or conversational command for self-review (not a literal mirror, image, camera, or reflection task), cannot clearly describe a problem, asks for an evidence-based blind-spot review, or during AI-assisted work when observable behavior shows goal drift, repeated ineffective action, overplanning, premature certainty, unverified assumptions, repeated rework, or omission of a consequential step. Do not use for trivial preferences or to infer hidden trauma, diagnosis, or personality without consent."
license: MIT
---

# Finding Blind Spots

## Core principle

Find consequential problems from observable evidence, not mind reading. Help the user clarify, test, and correct one issue at a time. Match the user's language.

## Route

- The user says "照镜子" as a self-review command: treat it as an explicit general review request. Use available conversation evidence; if evidence is insufficient, ask one recent-event question using [references/dialogue-protocol.md](references/dialogue-protocol.md).
- The user feels something is wrong but cannot describe it: read [references/dialogue-protocol.md](references/dialogue-protocol.md).
- Current work shows goal drift, repeated failure, overplanning, unverified certainty, rework, or a consequential omission: read [references/work-mirror.md](references/work-mirror.md).
- The user explicitly requests a deep personal review, or accepts an invitation to one: read [references/deep-review.md](references/deep-review.md).
- For personal, memory-based, high-stakes, or psychologically loaded analysis, also read [references/evidence-safety.md](references/evidence-safety.md).
- For trivial work, ordinary preferences, or smooth progress without evidence of a problem: stay out of the way.

## Evidence and intervention gate

- **A:** direct statement plus observable behavior or result. Correct immediately when consequential.
- **B:** the same pattern appears in at least two independent observations. Correct at a natural checkpoint.
- **C:** one ambiguous observation. Label it as a hypothesis; ask one question only if it blocks progress.
- **D:** intuition, tone, or a compelling story without behavioral evidence. Do not surface it.

One observation never establishes a stable personal pattern.

## Correction contract

Surface only the most consequential current issue:

```text
Correction checkpoint
Problem: observation or clearly labeled hypothesis
Evidence: the user's words, actions, artifact, or result
Impact: the concrete cost of continuing
Next best action: one action to take now
Confidence: high / medium / low
```

Say **next best action**, not **the correct method**. Name the expected observable and revisit the conclusion when evidence arrives. Use a relevant domain skill or authoritative source when the remedy requires specialist knowledge.

## Non-negotiables

- In clarification mode, ask exactly one question per turn. Never dump a questionnaire.
- After refusing unsupported mind reading, do not continue with a guessed hidden fear, trauma, motive, or personality story.
- Prefer alternative explanations and counterevidence over harsh or flattering narratives.
- Use current user information over historical memory. Do not scan private files or write memory without explicit authorization.
- Respect "stop correcting", "skip this", and similar controls immediately. Do not repeat a correction without new evidence.
