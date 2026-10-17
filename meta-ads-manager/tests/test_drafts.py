import copy
import io
import unittest
from contextlib import redirect_stdout
from meta_ads.drafts import load_plan, is_qualified, render_markdown, main, validate_plan


class DraftTests(unittest.TestCase):
    def setUp(self):
        self.plan = load_plan()

    def test_offline_draft_and_account(self):
        self.assertTrue(self.plan["read_only"])
        self.assertEqual(self.plan["state"], "draft")
        self.assertEqual(self.plan["ad_account"], "act_184261823230641")
        self.assertIsNone(self.plan["lead_form"]["privacy_policy_url"])

    def test_three_distinct_angles_and_headline_variants(self):
        self.assertEqual(len(self.plan["campaigns"]), 3)
        self.assertEqual(len({x["id"] for x in self.plan["campaigns"]}), 3)
        for c in self.plan["campaigns"]:
            self.assertNotEqual(c["headline_a"], c["headline_b"])
            self.assertTrue(c["primary_text"])

    def test_qualified_lead_rules(self):
        base = {"cidade": "florianopolis", "faixa_preco": "sim_parcelado",
                "prazo": "ate_90", "quer_avaliacao": "sim"}
        self.assertTrue(is_qualified(base))
        for key, value in [("cidade", "outro"), ("faixa_preco", "nao"),
                           ("prazo", "pesquisando"), ("quer_avaliacao", "nao")]:
            other = dict(base, **{key: value})
            self.assertFalse(is_qualified(other))
        self.assertFalse(is_qualified({}))

    def test_invalid_plan_is_rejected(self):
        broken = copy.deepcopy(self.plan)
        broken["read_only"] = False
        with self.assertRaises(ValueError):
            validate_plan(broken)
        broken = copy.deepcopy(self.plan)
        broken["campaigns"][0]["headline_b"] = broken["campaigns"][0]["headline_a"]
        with self.assertRaises(ValueError):
            validate_plan(broken)

    def test_visual_first_plan(self):
        self.assertEqual(self.plan["creative_strategy"]["priority"], "video_first")
        self.assertEqual(len(self.plan["campaigns"]), 3)
        for campaign in self.plan["campaigns"]:
            self.assertTrue(campaign["scenes"])
            self.assertTrue(campaign["scenes"][-1][0].endswith("s"))
            self.assertLessEqual(len(campaign["primary_text"]), 110)
            self.assertIn("9:16", campaign["visual_brief"])
        self.assertIn("Vídeo: sequência visual", render_markdown(self.plan))

    def test_preview_and_cli(self):
        output = render_markdown(self.plan)
        self.assertIn("Florianópolis", output)
        self.assertIn("PENDENTE", output)
        self.assertIn("Título A", output)
        sink = io.StringIO()
        with redirect_stdout(sink):
            self.assertEqual(main(["--format", "markdown"]), 0)
        self.assertIn("RASCUNHO", sink.getvalue())


if __name__ == "__main__":
    unittest.main()
