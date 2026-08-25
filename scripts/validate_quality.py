#!/usr/bin/env python3
"""Deterministic quality checks for skill sources and sampled responses."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    location: str
    excerpt: str


PLACEHOLDER_PATTERNS = (
    ("placeholder-underscore", re.compile(r"_{3,}"), "Replace underscore blanks."),
    (
        "placeholder-template",
        re.compile(r"\{\{[^{}\r\n]+\}\}"),
        "Replace the unresolved template token.",
    ),
    (
        "placeholder-todo",
        re.compile(r"\b(?:TODO|TBD)\b", re.IGNORECASE),
        "Remove the unfinished marker.",
    ),
)

FILL_IN_LABEL = re.compile(
    r"\[(?:specific event|trigger|action|short-term payoff|long-term cost|"
    r"behavior|hypothesis|counterexample|result|具体事件|触发事件|行动|"
    r"短期收益|长期代价|行为|假设|反例|结果)\]",
    re.IGNORECASE,
)

FORTUNE_TELLER_PHRASES = (
    "真正的盲点不是",
    "你缺的不是",
    "镜子里的问题",
    "一句更直接的话",
    "你真正怕的是",
    "真正的你其实",
    "别人只看到表面",
    "the real blind spot is not",
    "what you lack is not",
    "the problem in the mirror",
    "one more direct sentence",
    "what you are really afraid of",
)

RUNTIME_POLLUTION_PHRASES = FORTUNE_TELLER_PHRASES

BAD_COLLOCATIONS = (
    "最渴的就是",
    "被拆过的人",
    "这口渴",
)

WATER_METAPHOR_GROUPS = (
    ("口渴",),
    ("泉眼",),
    ("下沉", "沉下"),
    ("捞出来", "捞起"),
)

BINARY_REVEAL_PATTERNS = (
    re.compile(r"不是[^。！？\r\n]{0,80}(?:而是|而在于)"),
    re.compile(r"\b(?:is not|isn't|not)\b[^.!?\r\n]{0,100}\b(?:but|rather)\b", re.IGNORECASE),
)

PERFORMATIVE_METAPHOR_PHRASES = (
    "兼职聘成",
    "启动按钮",
    "余量吃掉",
)

PERFORMATIVE_METAPHOR_PATTERNS = (
    re.compile(
        r"(?:任务|截止时间|待办(?:列表|事项)?)[^。！？\r\n]{0,35}"
        r"(?:擅长|住上|住在|聘成|吃掉|长腿|提醒器)"
    ),
)

THERAPEUTIC_SCRIPT_PHRASES = (
    "我听到了",
    "我懂你",
    "我能感受到",
    "我完全理解",
    "我在这里陪你",
)

UNSUPPORTED_CAUSAL_STYLE_PATTERNS = (
    re.compile(r"自我攻击[^。！？\r\n]{0,24}(?:消耗|削弱)[^。！？\r\n]{0,12}行动力"),
)

EMOTION_TERMS = (
    "难过",
    "焦虑",
    "挫败",
    "害怕",
    "自责",
    "愤怒",
    "孤独",
    "痛苦",
    "沮丧",
)

EVIDENCE_ONLY_CONTROLS = (
    "只讲证据和不确定性",
    "只说证据和不确定性",
    "evidence and uncertainty only",
)

EXTRA_CHECKPOINT_FIELD = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\\?\*\*)?"
    r"(?:问题|影响|下一步(?:最佳)?(?:动作|行动)|建议|problem|impact|next best action)"
    r"\s*[:：](?:\\?\*\*)?"
)

NO_COMFORT_CONTROLS = ("别安慰", "不要安慰", "不需要安慰", "do not comfort")
REASSURANCE_PHRASES = (
    "没关系",
    "别难过",
    "不要自责",
    "你已经很好",
    "我理解你",
    "我懂你",
    "这不是你的错",
)


def _finding(code: str, message: str, text: str, start: int, label: str) -> Finding:
    line_number = text.count("\n", 0, max(start, 0)) + 1
    line_start = text.rfind("\n", 0, max(start, 0)) + 1
    line_end = text.find("\n", max(start, 0))
    if line_end == -1:
        line_end = len(text)
    excerpt = text[line_start:line_end].strip()
    if len(excerpt) > 160:
        excerpt = excerpt[:157] + "..."
    return Finding(code, message, f"{label}:{line_number}", excerpt)


def _regex_findings(text: str, label: str) -> list[Finding]:
    findings: list[Finding] = []
    for code, pattern, message in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(_finding(code, message, text, match.start(), label))
    return findings


def validate_response(
    text: str, allow_fill_in: bool = False, prompt_text: str | None = None
) -> list[Finding]:
    findings = _regex_findings(text, "response")
    lowered = text.lower()

    if not allow_fill_in:
        for match in FILL_IN_LABEL.finditer(text):
            findings.append(
                _finding(
                    "placeholder-label",
                    "Use fill-in labels only in an explicitly requested sentence stem.",
                    text,
                    match.start(),
                    "response",
                )
            )

    for match in re.finditer(r"—+", text):
        findings.append(
            _finding(
                "dramatic-dash",
                "Replace the dramatic dash with ordinary punctuation.",
                text,
                match.start(),
                "response",
            )
        )

    for phrase in FORTUNE_TELLER_PHRASES:
        start = lowered.find(phrase.lower())
        if start != -1:
            findings.append(
                _finding(
                    "fortune-teller-phrase",
                    "State the evidence-based observation without a revelation formula.",
                    text,
                    start,
                    "response",
                )
            )

    for pattern in BINARY_REVEAL_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                _finding(
                    "binary-reveal",
                    "State the supported observation directly without a reversal formula.",
                    text,
                    match.start(),
                    "response",
                )
            )

    for phrase in PERFORMATIVE_METAPHOR_PHRASES:
        start = text.find(phrase)
        if start != -1:
            findings.append(
                _finding(
                    "performative-metaphor",
                    "Replace the performative metaphor with a brief literal observation.",
                    text,
                    start,
                    "response",
                )
            )

    for pattern in PERFORMATIVE_METAPHOR_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                _finding(
                    "performative-metaphor",
                    "Replace task or deadline personification with a brief literal observation.",
                    text,
                    match.start(),
                    "response",
                )
            )

    for phrase in THERAPEUTIC_SCRIPT_PHRASES:
        start = text.find(phrase)
        if start != -1:
            findings.append(
                _finding(
                    "therapeutic-script",
                    "Remove the stock therapeutic acknowledgement and use the user's exact words.",
                    text,
                    start,
                    "response",
                )
            )

    for pattern in UNSUPPORTED_CAUSAL_STYLE_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                _finding(
                    "unsupported-causal-style",
                    "Do not claim a causal effect without evidence from the user's situation.",
                    text,
                    match.start(),
                    "response",
                )
            )

    for phrase in BAD_COLLOCATIONS:
        start = text.find(phrase)
        if start != -1:
            findings.append(
                _finding(
                    "bad-collocation",
                    "Rewrite the malformed or unnatural Chinese collocation.",
                    text,
                    start,
                    "response",
                )
            )

    present_groups = [
        group for group in WATER_METAPHOR_GROUPS if any(term in text for term in group)
    ]
    if len(present_groups) >= 2:
        first_term = next(term for term in present_groups[0] if term in text)
        findings.append(
            _finding(
                "mixed-water-metaphor",
                "Replace the metaphor chain with literal, concrete language.",
                text,
                text.find(first_term),
                "response",
            )
        )

    if prompt_text is not None:
        lowered_prompt = prompt_text.lower()
        for emotion in EMOTION_TERMS:
            if emotion in prompt_text:
                continue
            pattern = re.compile(rf"你[^。！？\r\n]{{0,12}}{re.escape(emotion)}")
            for match in pattern.finditer(text):
                findings.append(
                    _finding(
                        "inferred-emotion",
                        "Acknowledge only emotions the user explicitly named.",
                        text,
                        match.start(),
                        "response",
                    )
                )

        if any(control in lowered_prompt for control in EVIDENCE_ONLY_CONTROLS):
            for match in EXTRA_CHECKPOINT_FIELD.finditer(text):
                findings.append(
                    _finding(
                        "tone-control-scope",
                        "The user requested evidence and uncertainty only; omit other checkpoint fields.",
                        text,
                        match.start(),
                        "response",
                    )
                )

        if any(control in lowered_prompt for control in NO_COMFORT_CONTROLS):
            for phrase in REASSURANCE_PHRASES:
                start = text.find(phrase)
                if start != -1:
                    findings.append(
                        _finding(
                            "tone-control-comfort",
                            "Remove reassurance because the user explicitly declined comfort.",
                            text,
                            start,
                            "response",
                        )
                    )
    nonempty_lines = [line for line in text.splitlines() if line.strip()]
    if nonempty_lines:
        final_line = nonempty_lines[-1].strip()
        if re.fullmatch(r"\*\*.+\*\*", final_line):
            start = text.rfind(nonempty_lines[-1])
            findings.append(
                _finding(
                    "final-bold-punchline",
                    "End with the checkpoint instead of a standalone bold maxim.",
                    text,
                    start,
                    "response",
                )
            )

    return _deduplicate(findings)


def validate_source(root: Path) -> list[Finding]:
    root = root.resolve()
    files = [root / "SKILL.md", root / "README.md"]
    references = root / "references"
    if references.is_dir():
        files.extend(sorted(references.glob("*.md")))

    findings: list[Finding] = []
    for path in files:
        if not path.is_file():
            findings.append(
                Finding(
                    "missing-source-file",
                    "Required source file is missing.",
                    str(path),
                    "",
                )
            )
            continue
        text = path.read_text(encoding="utf-8")
        label = path.relative_to(root).as_posix()
        findings.extend(_regex_findings(text, label))
        lowered = text.lower()
        for phrase in RUNTIME_POLLUTION_PHRASES:
            start = lowered.find(phrase.lower())
            if start != -1:
                findings.append(
                    _finding(
                        "runtime-prompt-pollution",
                        "Remove the copyable failure phrase from runtime instructions.",
                        text,
                        start,
                        label,
                    )
                )
        for phrase in BAD_COLLOCATIONS:
            start = text.find(phrase)
            if start != -1:
                findings.append(
                    _finding(
                        "runtime-prompt-pollution",
                        "Keep known malformed examples in eval data, not runtime instructions.",
                        text,
                        start,
                        label,
                    )
                )
    return _deduplicate(findings)


def _deduplicate(findings: list[Finding]) -> list[Finding]:
    unique: dict[tuple[str, str, str], Finding] = {}
    for finding in findings:
        unique[(finding.code, finding.location, finding.excerpt)] = finding
    return list(unique.values())


def _print_findings(findings: list[Finding]) -> None:
    for finding in findings:
        suffix = f" :: {finding.excerpt}" if finding.excerpt else ""
        print(
            f"FAIL [{finding.code}] {finding.location} {finding.message}{suffix}"
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    source = subparsers.add_parser("source", help="Validate runtime skill sources.")
    source.add_argument("root", nargs="?", default=".")

    response = subparsers.add_parser("response", help="Validate a sampled response.")
    response.add_argument("path", help="Response file path, or - for stdin.")
    response.add_argument("--allow-fill-in", action="store_true")
    response.add_argument(
        "--prompt-text",
        help="Optional user prompt for checking explicit tone and content controls.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "source":
            findings = validate_source(Path(args.root))
        else:
            if args.path == "-":
                text = sys.stdin.read()
            else:
                text = Path(args.path).read_text(encoding="utf-8")
            findings = validate_response(
                text,
                allow_fill_in=args.allow_fill_in,
                prompt_text=args.prompt_text,
            )
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if findings:
        _print_findings(findings)
        return 1
    print("PASS: no deterministic quality violations found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
