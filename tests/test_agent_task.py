"""0.8.0 step 4: the contract of the agent tray task (`agent-task.schema.json`) and its answer bodies.

An answer valid for the schema must be accepted by the function behind the API route that takes that body, and one
the API refuses must fail the schema too, so the forms of 0.7-0.8 are already the bodies of `gimg agent answer`."""
import unittest

from gimg import brandsheet, failures, orders, schema as S, server
from gimg.errors import GimgError
from tests.test_brand_orders import SHEET
from tests.test_brandsheet import PORTAL, SUBJECT, ZONE
from tests.test_failures import FailBase, K, P, PR

TYPES = {"subject": "answerSubject", "judgment": "answerJudgment", "redesign": "answerRedesign",
         "choice": "answerChoice", "sheet": "answerSheet"}
SCH = S.load_schema("agent-task")


def errors(task):
    """The task against the schema, and its answer against the definition its type names."""
    out = S.validate(task, SCH)
    answer = task.get("answer")
    if answer is not None and task.get("type") in TYPES:
        found = S.validate(answer, {"$ref": "#/$defs/" + TYPES[task["type"]], "$defs": SCH["$defs"]})
        out += [e._replace(path="/answer" + e.path) for e in found]
    return out


def task(kind, answer=None, **kw):
    base = {"schemaVersion": 1, "id": 1, "type": kind, "state": "pending", "question": "Which one?",
            "order": {"key": K, "profile": PR}}
    if answer is not None:
        base.update(state="answered", answer=answer, answeredBy="claude")
    return {**base, **kw}


def codes(found):
    return sorted((e.path, e.code) for e in found)


class Shape(unittest.TestCase):
    def test_schema_is_valid_for_the_validator(self):
        S.check_schema(SCH)
        self.assertEqual(set(TYPES.values()), {n for n in SCH["$defs"]})
        self.assertEqual(set(TYPES), set(SCH["properties"]["type"]["enum"]))

    def test_valid_example_of_each_type(self):
        for kind, answer in {
            "subject": {"subject": SUBJECT, "cleanZone": ZONE},
            "judgment": {"attempt": 2, "human": {"horizon": "ok", "grain": "bad"}},
            "redesign": {"key": K, "profile": PR, "problem": "the horizon tilts", "attempts": [1], "terms": ["tilt"]},
            "choice": {"attempt": 1, "reason": "the cleanest zone"},
            "sheet": {"sheet": PORTAL},
        }.items():
            with self.subTest(kind):
                self.assertEqual(errors(task(kind, answer)), [])
        self.assertEqual(errors({k: v for k, v in task("sheet").items() if k != "order"}), [])

    def test_invalid_for_the_right_reason(self):
        self.assertEqual(codes(errors(task("poem"))), [("/type", "enum")])
        self.assertEqual(codes(errors(task("subject", state="done"))), [("/state", "enum")])
        self.assertEqual(codes(errors({k: v for k, v in task("subject").items() if k != "question"})),
                         [("", "required")])
        self.assertEqual(codes(errors(task("subject", extra=1))), [("/extra", "additionalProperties")])
        self.assertEqual(codes(errors(task("subject", answeredBy="bot"))), [("/answeredBy", "enum")])
        self.assertEqual(codes(errors(task("subject", {"subject": "x", "by": "y"}))), [("/answer/by", "additionalProperties")])
        self.assertEqual(codes(errors(task("judgment", {"attempt": 1, "human": {"horizon": "meh"}}))),
                         [("/answer/human/horizon", "enum")])
        self.assertEqual(codes(errors(task("judgment", {"attempt": 1, "human": {}}))), [("/answer/human", "minProperties")])
        self.assertEqual(codes(errors(task("choice", {"attempt": 1}))), [("/answer", "required")])
        self.assertEqual(codes(errors(task("sheet", {"sheet": "x"}))), [("/answer/sheet", "type")])


class Bodies(FailBase):
    def setUp(self):
        super().setUp()
        self.made()

    def valid(self, kind, answer):
        self.assertEqual(errors(task(kind, answer)), [], str(answer)[:80])

    def invalid(self, kind, answer, path):
        self.assertIn(path, [e.path for e in errors(task(kind, answer))], str(answer)[:80])

    def test_subject_is_the_attempt_and_prompt_body(self):
        body = {"subject": SUBJECT, "cleanZone": ZONE}
        self.valid("subject", body)
        candidate, changes, checks = orders.plan_attempt(P, K, PR, subject=body["subject"], clean_zone=body["cleanZone"])
        self.assertEqual(changes["subject"], body["subject"])
        self.assertTrue(brandsheet.assemble(brandsheet.resolve(P), "cover", body["subject"], body["cleanZone"])["prompt"])
        for bad, path in (({"subject": "  "}, "/answer/subject"), ({"subject": "x" * 4001}, "/answer/subject"),
                          ({"subject": "x", "cleanZone": "z" * 4001}, "/answer/cleanZone"),
                          ({"subject": 5}, "/answer/subject"), ({}, "/answer")):
            with self.subTest(bad):
                self.invalid("subject", bad, path)
                with self.assertRaises(GimgError):
                    orders.plan_attempt(P, K, PR, subject=bad.get("subject", ""), clean_zone=bad.get("cleanZone"))

    def test_judgment_traits_are_those_the_mark_reason_accepts(self):
        traits = sorted(orders._reason_traits(P))
        self.assertTrue(traits)
        body = {"attempt": 1, "human": {t: "bad" for t in traits}}
        self.valid("judgment", body)
        for trait in body["human"]:
            self.assertEqual(orders.check_reason(P, {"trait": trait}), {"trait": trait})
        self.assertEqual(server._attempt_id(body["attempt"]), 1)
        self.assertEqual(orders.mark(P, K, PR, 1, "discarded", reason={"trait": traits[0]})["reason"], {"trait": traits[0]})
        with self.assertRaises(GimgError) as cm:
            orders.check_reason(P, {"trait": "nonsense"})
        self.assertEqual(cm.exception.code, "order.reason_invalid")
        self.invalid("judgment", {"attempt": 1, "human": {"a" * 81: "ok"}}, "/answer/human/" + "a" * 81)  # the API caps a trait at 80
        with self.assertRaises(GimgError):
            orders.check_reason(P, {"trait": "a" * 81})
        self.invalid("judgment", {"attempt": True, "human": {"horizon": "ok"}}, "/answer/attempt")
        with self.assertRaises(GimgError):
            server._attempt_id(True)

    def test_redesign_is_the_troubleshooting_row_body(self):
        body = {"key": K, "profile": PR, "problem": "the horizon tilts", "attempts": [1, 2],
                "redesign": "level it", "terms": ["tilt", "slope"], "by": "claude"}
        self.valid("redesign", body)
        row = failures.add_row(P, body)
        self.assertEqual((row["problem"], row["attempts"], row["terms"], row["by"]),
                         ("the horizon tilts", [1, 2], ["tilt", "slope"], "claude"))
        self.valid("redesign", {"key": K, "profile": PR, "problem": "p"})
        refused = [({"key": K, "profile": PR, "problem": "  "}, "/answer/problem"),
                   ({"key": K, "profile": PR}, "/answer"),
                   ({"key": K, "problem": "p"}, "/answer"),
                   ({"key": K, "profile": PR, "problem": "p", "attempts": ["1"]}, "/answer/attempts/0"),
                   ({"key": K, "profile": PR, "problem": "p", "terms": [" "]}, "/answer/terms/0"),
                   ({"key": K, "profile": PR, "problem": "p", "terms": ["t"] * 31}, "/answer/terms"),
                   ({"key": K, "profile": PR, "problem": "p", "by": "b" * 81}, "/answer/by"),
                   ({"key": K, "profile": PR, "problem": "p", "extra": 1}, "/answer/extra"),
                   ({"key": K, "profile": PR, "problem": "p" * 4001}, "/answer/problem")]
        for bad, path in refused:
            with self.subTest(bad):
                self.invalid("redesign", bad, path)
                with self.assertRaises(GimgError):
                    failures.add_row(P, bad)

    def test_choice_attempt_is_the_choose_body(self):
        body = {"attempt": 2, "reason": "the cleanest zone"}
        self.valid("choice", body)
        self.assertEqual(server._attempt_id(body["attempt"]), 2)
        self.assertEqual(orders._attempt(orders.get(P, K, PR), 2)["id"], 2)
        self.invalid("choice", {"attempt": "2", "reason": "r"}, "/answer/attempt")
        self.invalid("choice", {"attempt": 0, "reason": "r"}, "/answer/attempt")
        self.invalid("choice", {"attempt": 2, "reason": " "}, "/answer/reason")  # kept in the task, not sent to the API
        with self.assertRaises(GimgError):
            server._attempt_id("2")
        with self.assertRaises(GimgError):
            orders._attempt(orders.get(P, K, PR), 0)
        with self.assertRaises(GimgError):
            orders._attempt(orders.get(P, K, PR), 99)

    def test_sheet_is_a_brand_sheet(self):
        self.valid("sheet", {"sheet": SHEET})
        self.assertEqual(S.validate(SHEET, S.load_schema("brand-sheet")), [])
        broken = {"schemaVersion": 1}
        self.valid("sheet", {"sheet": broken})  # the shape of the answer; the sheet itself is checked by its own schema
        self.assertIn(("", "required"), codes(S.validate(broken, S.load_schema("brand-sheet"))))


if __name__ == "__main__":
    unittest.main()
