import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.dont_write_bytecode = True

from validate_quality import main, validate_response, validate_source


def codes(findings):
    return {finding.code for finding in findings}


class ResponseQualityTests(unittest.TestCase):
    def test_clean_response_passes(self):
        text = (
            "你最近两次都跳过了用户试用。现有信息来自你的自述，"
            "那次效果更好还没有记录核实。可以先记录下次是否试用以及跳过原因。"
        )
        self.assertEqual(validate_response(text), [])

    def test_unresolved_underscore_placeholder_fails(self):
        self.assertIn("placeholder-underscore", codes(validate_response("当____发生时")))

    def test_template_token_fails(self):
        self.assertIn("placeholder-template", codes(validate_response("结果是{{result}}")))

    def test_fill_in_label_requires_explicit_allowance(self):
        text = "当[具体事件]发生时，我做了[行动]。"
        self.assertIn("placeholder-label", codes(validate_response(text)))
        self.assertNotIn(
            "placeholder-label", codes(validate_response(text, allow_fill_in=True))
        )

    def test_markdown_link_is_not_a_placeholder(self):
        self.assertEqual(validate_response("参见[官方说明](https://example.com)。"), [])

    def test_dramatic_dash_fails(self):
        self.assertIn("dramatic-dash", codes(validate_response("你担心的是——被拒绝。")))

    def test_fortune_teller_phrase_fails(self):
        self.assertIn(
            "fortune-teller-phrase",
            codes(validate_response("真正的盲点不是能力，而是恐惧。")),
        )

    def test_generic_binary_reveal_fails(self):
        text = "最值得纠正的不是态度，而是流程没有固定下来。"
        self.assertIn("binary-reveal", codes(validate_response(text)))

    def test_final_bold_punchline_fails(self):
        text = "证据仍然不足。\n\n**你缺的只是一次勇敢。**"
        self.assertIn("final-bold-punchline", codes(validate_response(text)))

    def test_bold_checkpoint_label_is_allowed(self):
        text = "- **问题：**最近两次都跳过了试用。\n- **证据：**来自你的自述。"
        self.assertNotIn("final-bold-punchline", codes(validate_response(text)))

    def test_known_bad_collocation_fails(self):
        self.assertIn("bad-collocation", codes(validate_response("最渴的就是有人选择他。")))

    def test_mixed_water_metaphor_fails(self):
        text = "这口渴有自己的泉眼，最后要有人把他捞出来。"
        self.assertIn("mixed-water-metaphor", codes(validate_response(text)))

    def test_known_performative_humor_metaphor_fails(self):
        text = "截止时间被你兼职聘成了启动按钮，它会把全部余量吃掉。"
        self.assertIn("performative-metaphor", codes(validate_response(text)))

    def test_task_personification_humor_fails(self):
        text = "五分钟的任务，很擅长在待办列表里住上好几天。"
        self.assertIn("performative-metaphor", codes(validate_response(text)))

    def test_stock_therapeutic_acknowledgement_fails(self):
        self.assertIn("therapeutic-script", codes(validate_response("你现在很自责，我听到了。")))

    def test_known_unsupported_causal_style_fails(self):
        text = "自我攻击会继续消耗行动力，却解释不了拖延原因。"
        self.assertIn("unsupported-causal-style", codes(validate_response(text)))

    def test_inferred_emotion_fails_when_prompt_did_not_name_it(self):
        prompt = "我又拖到最后才开始，我觉得自己很差劲。"
        response = "你现在很挫败，但这仍不能解释拖延原因。"
        self.assertIn(
            "inferred-emotion",
            codes(validate_response(response, prompt_text=prompt)),
        )

    def test_explicit_emotion_is_allowed(self):
        prompt = "我现在很挫败。"
        response = "你明确说自己很挫败。现有信息还不足以解释原因。"
        self.assertNotIn(
            "inferred-emotion",
            codes(validate_response(response, prompt_text=prompt)),
        )

    def test_evidence_only_control_rejects_extra_checkpoint_fields(self):
        prompt = "别安慰我，不要幽默，只讲证据和不确定性。"
        response = "问题：流程没有检查点。证据：三次自述。下一步：建立记录。"
        self.assertIn(
            "tone-control-scope",
            codes(validate_response(response, prompt_text=prompt)),
        )


class SourceQualityTests(unittest.TestCase):
    def make_source(self, root: Path, skill_text: str):
        (root / "SKILL.md").write_text(skill_text, encoding="utf-8")
        (root / "README.md").write_text("参见[说明](README.md)。", encoding="utf-8")
        references = root / "references"
        references.mkdir()
        (references / "example.md").write_text(
            "Correction checkpoint\nProblem: observation\n", encoding="utf-8"
        )

    def test_clean_source_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_source(root, "Use complete examples without template blanks.")
            self.assertEqual(validate_source(root), [])

    def test_source_placeholder_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_source(root, "The result is ___.")
            self.assertIn("placeholder-underscore", codes(validate_source(root)))

    def test_source_polluting_example_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_source(root, "The real blind spot is not X but Y.")
            self.assertIn("runtime-prompt-pollution", codes(validate_source(root)))


class CliTests(unittest.TestCase):
    def test_response_exit_codes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            clean = Path(temp_dir) / "clean.txt"
            clean.write_text("现有信息来自你的自述。", encoding="utf-8")
            bad = Path(temp_dir) / "bad.txt"
            bad.write_text("真正的盲点不是能力，而是恐惧。", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["response", str(clean)]), 0)
                self.assertEqual(main(["response", str(bad)]), 1)

    def test_missing_response_file_returns_usage_error(self):
        missing = Path(tempfile.gettempdir()) / "missing-quality-response.txt"
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["response", str(missing)]), 2)

    def test_cli_fill_in_override(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = Path(temp_dir) / "fill-in.txt"
            response.write_text("当[具体事件]发生时，我做了[行动]。", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["response", str(response)]), 1)
                self.assertEqual(
                    main(["response", str(response), "--allow-fill-in"]), 0
                )

    def test_cli_prompt_text_enforces_content_scope(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            response = Path(temp_dir) / "response.txt"
            response.write_text(
                "问题：流程没有检查点。证据：来自你的自述。", encoding="utf-8"
            )
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "response",
                            str(response),
                            "--prompt-text",
                            "只讲证据和不确定性。",
                        ]
                    ),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
