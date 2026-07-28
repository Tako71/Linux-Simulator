"""Логика прохождения курса: прогресс, подготовка окружения, проверка."""
import json
import re

from . import sandbox
from .config import LAB_DIR, PROGRESS_FILE, STATE_DIR
from .lessons import ALL_TASKS, MODULES


class Progress:
    def __init__(self):
        self.done: set[str] = set()
        self.current: str | None = None
        self.load()

    def load(self):
        try:
            data = json.loads(PROGRESS_FILE.read_text())
            self.done = set(data.get("done", []))
            self.current = data.get("current")
        except Exception:
            pass

    def save(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        PROGRESS_FILE.write_text(json.dumps(
            {"done": sorted(self.done), "current": self.current},
            ensure_ascii=False, indent=2))

    def reset(self):
        self.done.clear()
        self.current = None
        self.save()


class Course:
    def __init__(self, systemd_available=True):
        self.modules = MODULES
        self.tasks = ALL_TASKS
        self.progress = Progress()
        self.systemd = systemd_available
        self.index = self._start_index()
        self._hist_mark = 0
        self.hint_level = 0

    # ---------------- позиционирование ----------------
    def _start_index(self) -> int:
        cur = self.progress.current
        if cur:
            for i, t in enumerate(self.tasks):
                if t.id == cur:
                    return i
        for i, t in enumerate(self.tasks):
            if t.id not in self.progress.done:
                return i
        return 0

    @property
    def task(self):
        return self.tasks[self.index]

    @property
    def module(self):
        for m in self.modules:
            if self.task in m.tasks:
                return m
        return self.modules[0]

    def goto(self, index: int):
        self.index = max(0, min(index, len(self.tasks) - 1))
        self.progress.current = self.task.id
        self.progress.save()
        self.hint_level = 0
        self.prepare()

    def next(self):
        self.goto(self.index + 1)

    def prev(self):
        self.goto(self.index - 1)

    def next_unsolved(self):
        for i in range(self.index + 1, len(self.tasks)):
            if self.tasks[i].id not in self.progress.done:
                self.goto(i)
                return
        self.next()

    # ---------------- подготовка и проверка ----------------
    def prepare(self):
        """Готовит окружение под текущее задание и запоминает точку в истории."""
        t = self.task
        self._hist_mark = len(sandbox.history_lines())
        if t.setup:
            sandbox.sh(f"mkdir -p {LAB_DIR}; " + t.setup, cwd=LAB_DIR, timeout=60)

    def new_history(self) -> list[str]:
        return sandbox.history_lines()[self._hist_mark:]

    def check(self) -> tuple[bool, str]:
        t = self.task
        if t.needs == "systemd" and not self.systemd:
            return False, "Это задание требует systemd, а песочница поднята без него. Перезапусти: ./ltrain restart"

        if t.check_history:
            pattern = re.compile(t.check_history)
            if not any(pattern.search(line) for line in self.new_history()):
                return False, "Нужная команда пока не встречалась в этой сессии. Выполни её в левой панели."

        if t.check:
            cwd = sandbox.current_cwd()
            r = sandbox.sh(t.check, cwd=cwd, timeout=45)
            if r.returncode != 0:
                return False, t.fail_msg

        self.progress.done.add(t.id)
        self.progress.save()
        return True, "Задание сдано."

    # ---------------- статистика ----------------
    def module_stats(self, module) -> tuple[int, int]:
        done = sum(1 for t in module.tasks if t.id in self.progress.done)
        return done, len(module.tasks)

    def total_stats(self) -> tuple[int, int]:
        return len(self.progress.done & {t.id for t in self.tasks}), len(self.tasks)
