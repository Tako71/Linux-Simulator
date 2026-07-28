"""Проверки целостности курса.

Запускаются без Docker, поэтому годятся для CI:
    python3 -m unittest discover -s tests -v
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trainer.lessons import ALL_TASKS, MODULES, TASK_INDEX  # noqa: E402

SHELL_FIELDS = ("setup", "check", "solution")


class TestStructure(unittest.TestCase):
    def test_modules_not_empty(self):
        self.assertGreater(len(MODULES), 0)
        for m in MODULES:
            self.assertGreater(len(m.tasks), 0, f"модуль {m.id} без заданий")

    def test_module_ids_unique(self):
        ids = [m.id for m in MODULES]
        self.assertEqual(len(ids), len(set(ids)), "дублирующиеся id модулей")

    def test_task_ids_unique(self):
        ids = [t.id for t in ALL_TASKS]
        self.assertEqual(len(ids), len(set(ids)), "дублирующиеся id заданий")

    def test_task_id_matches_module(self):
        for m in MODULES:
            for t in m.tasks:
                self.assertTrue(t.id.startswith(m.id + "-"),
                                f"{t.id} не соответствует модулю {m.id}")

    def test_index_covers_all(self):
        self.assertEqual(len(TASK_INDEX), len(ALL_TASKS))


class TestTaskContent(unittest.TestCase):
    def test_every_task_is_checkable(self):
        for t in ALL_TASKS:
            with self.subTest(task=t.id):
                self.assertTrue(t.check or t.check_history,
                                "задание невозможно проверить")

    def test_every_task_has_help(self):
        for t in ALL_TASKS:
            with self.subTest(task=t.id):
                self.assertTrue(t.hints, "нет подсказок")
                self.assertTrue(t.solution, "нет эталонного решения")

    def test_brief_mentions_assignment(self):
        for t in ALL_TASKS:
            with self.subTest(task=t.id):
                self.assertGreater(len(t.brief), 40, "слишком короткое описание")

    def test_needs_values(self):
        for t in ALL_TASKS:
            with self.subTest(task=t.id):
                self.assertIn(t.needs, ("", "net", "systemd"))

    def test_history_regex_compiles(self):
        for t in ALL_TASKS:
            if t.check_history:
                with self.subTest(task=t.id):
                    re.compile(t.check_history)

    def test_history_regex_matches_solution(self):
        """Эталонное решение обязано удовлетворять проверке по истории."""
        for t in ALL_TASKS:
            if t.check_history and t.solution:
                with self.subTest(task=t.id):
                    self.assertRegex(t.solution, t.check_history)


class TestShellSyntax(unittest.TestCase):
    def test_snippets_are_valid_bash(self):
        for t in ALL_TASKS:
            for field in SHELL_FIELDS:
                code = getattr(t, field)
                if not code:
                    continue
                with self.subTest(task=t.id, field=field):
                    r = subprocess.run(["bash", "-n", "-c", code],
                                       capture_output=True, text=True)
                    self.assertEqual(r.returncode, 0, r.stderr.strip())

    def test_no_self_matching_pgrep(self):
        """pgrep -f 'sleep 900' находит и сам процесс проверки.

        Защита — «трюк со скобками»: pgrep -f 'sleep 90[0]'.
        """
        for t in ALL_TASKS:
            for field in ("check", "setup"):
                code = getattr(t, field)
                for m in re.finditer(r"p(?:grep|kill) -f '([^']+)'", code or ""):
                    with self.subTest(task=t.id, field=field, pattern=m.group(1)):
                        self.assertIn("[", m.group(1),
                                      "шаблон совпадёт сам с собой")


class TestDangerousCommands(unittest.TestCase):
    FORBIDDEN = (
        r"docker\s+system\s+prune",
        r"docker\s+volume\s+prune",
        r"rm\s+-rf\s+/\s*$",
        r"mkfs",
        r":\(\)\s*\{",
    )

    def test_no_destructive_host_commands(self):
        for t in ALL_TASKS:
            for field in SHELL_FIELDS:
                code = getattr(t, field) or ""
                for pattern in self.FORBIDDEN:
                    with self.subTest(task=t.id, field=field, pattern=pattern):
                        self.assertIsNone(re.search(pattern, code))


if __name__ == "__main__":
    unittest.main()
