"""Правая панель тренажёра: задания, подсказки, проверка."""
import os
import re
import shutil
import sys
import textwrap

from . import sandbox
from .engine import Course

R = "\033[0m"
B = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[34m"
MAG = "\033[35m"


def width() -> int:
    return max(38, min(shutil.get_terminal_size((60, 40)).columns, 110))


def clear():
    sys.stdout.write("\033[2J\033[H")


def render_markup(text: str, w: int) -> list[str]:
    out = []
    for raw in text.splitlines():
        if raw.strip() == "":
            out.append("")
            continue
        code_block = raw.startswith("  ")
        body = re.sub(r"`([^`]+)`", CYAN + r"\1" + R, raw.strip())
        if code_block:
            out.append(f"  {CYAN}{raw.strip()}{R}")
        else:
            for ln in textwrap.wrap(body, w, drop_whitespace=True) or [""]:
                out.append(ln)
    return out


def bar(done: int, total: int, w: int) -> str:
    w = max(10, w)
    filled = int(w * done / total) if total else 0
    return GREEN + "█" * filled + DIM + "░" * (w - filled) + R


class Panel:
    def __init__(self, systemd: bool):
        self.course = Course(systemd_available=systemd)
        self.flash = ""
        self.flash_color = ""
        self.show_solution = False
        self.course.prepare()

    # ---------------------------------------------------------------- вывод
    def render(self):
        c = self.course
        w = width()
        t, m = c.task, c.module
        clear()
        done, total = c.total_stats()
        mdone, mtotal = c.module_stats(m)

        print(f"{B}{MAG}  LINUX TRAINER{R}  {DIM}курс от новичка до администратора{R}")
        print(f"{DIM}{'─' * w}{R}")
        print(f"{B}{BLUE}{m.id.upper()} · {m.title}{R} {DIM}[{m.level}]{R}")
        print(f"{DIM}модуль {mdone}/{mtotal} · всего {done}/{total}{R}  {bar(done, total, w - 30)}")
        print()
        mark = f"{GREEN}✓{R} " if t.id in c.progress.done else ""
        print(f"{B}Задание {c.index + 1}/{total}: {mark}{t.title}{R}")
        if t.needs == "net":
            print(f"{DIM}(нужен интернет в контейнере){R}")
        if t.needs == "systemd" and not c.systemd:
            print(f"{RED}(песочница без systemd — перезапусти ./ltrain restart){R}")
        print()
        for line in render_markup(t.brief, w):
            print(line)

        if self.course.hint_level:
            print()
            for i in range(min(self.course.hint_level, len(t.hints))):
                hint = re.sub(r"`([^`]+)`", CYAN + r"\1" + YELLOW, t.hints[i])
                for j, ln in enumerate(textwrap.wrap(hint, w - 3) or [""]):
                    print(f"{YELLOW}{'💡 ' if j == 0 else '   '}{ln}{R}")

        if self.show_solution and t.solution:
            print()
            print(f"{DIM}Решение:{R}")
            for ln in t.solution.splitlines():
                print(f"  {CYAN}{ln}{R}")

        print()
        print(f"{DIM}{'─' * w}{R}")
        if self.flash:
            print(f"{self.flash_color}{self.flash}{R}")
        print(f"{DIM}Enter{R} проверить  {DIM}h{R} подсказка  {DIM}s{R} решение  "
              f"{DIM}n/p{R} след./пред.  {DIM}l{R} список  {DIM}r{R} сброс  {DIM}q{R} выход")

    # -------------------------------------------------------------- команды
    def list_menu(self):
        c = self.course
        clear()
        print(f"{B}Модули курса{R}\n")
        for i, m in enumerate(c.modules, 1):
            d, t = c.module_stats(m)
            state = GREEN + "✓" + R if d == t else f"{d}/{t}"
            print(f" {i:>2}. {m.title:<42} {DIM}{m.level:<14}{R} {state}")
        print()
        raw = input("Номер модуля (Enter — назад): ").strip()
        if not raw.isdigit():
            return
        idx = int(raw) - 1
        if not 0 <= idx < len(c.modules):
            return
        module = c.modules[idx]
        clear()
        print(f"{B}{module.title}{R}\n")
        for i, t in enumerate(module.tasks, 1):
            state = GREEN + "✓" + R if t.id in c.progress.done else " "
            print(f" {i:>2}. [{state}] {t.title}")
        print()
        raw = input("Номер задания (Enter — первое): ").strip()
        pos = int(raw) - 1 if raw.isdigit() else 0
        pos = max(0, min(pos, len(module.tasks) - 1))
        target = module.tasks[pos]
        c.goto(c.tasks.index(target))
        self.show_solution = False
        self.flash = ""

    def do_check(self):
        self.flash, self.flash_color = "Проверяю...", DIM
        self.render()
        ok, msg = self.course.check()
        if ok:
            self.flash = "✓ " + msg + "  (Enter — дальше)"
            self.flash_color = GREEN + B
            self._solved = True
        else:
            self.flash = "✗ " + msg
            self.flash_color = RED
            self._solved = False

    def run(self):
        self._solved = False
        while True:
            self.render()
            try:
                cmd = input(f"\n{B}›{R} ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if cmd in ("q", "quit", "exit"):
                return
            if cmd == "":
                if self._solved:
                    self.show_solution = False
                    self.flash = ""
                    self._solved = False
                    self.course.next_unsolved()
                else:
                    self.do_check()
            elif cmd in ("c", "check"):
                self.do_check()
            elif cmd == "h":
                t = self.course.task
                if self.course.hint_level < len(t.hints):
                    self.course.hint_level += 1
                    self.flash = ""
                else:
                    self.flash, self.flash_color = "Подсказки закончились — жми s для решения.", YELLOW
            elif cmd == "s":
                self.show_solution = True
                self.flash = ""
            elif cmd == "n":
                self.show_solution = False
                self._solved = False
                self.flash = ""
                self.course.next()
            elif cmd == "p":
                self.show_solution = False
                self._solved = False
                self.flash = ""
                self.course.prev()
            elif cmd in ("l", "m"):
                self.list_menu()
            elif cmd == "r":
                self.course.prepare()
                self.flash, self.flash_color = "Окружение задания подготовлено заново.", YELLOW
            else:
                self.flash, self.flash_color = "Неизвестная команда.", DIM


def main():
    systemd = os.environ.get("LTRAIN_SYSTEMD", "1") == "1"
    if sandbox.container_state() != "running":
        print("Песочница не запущена. Закрой tmux и выполни ./ltrain start")
        input()
        return
    try:
        Panel(systemd).run()
    except Exception as e:  # чтобы панель не падала молча внутри tmux
        print(f"\n{RED}Ошибка панели:{R} {e}")
        input("Enter для выхода...")


if __name__ == "__main__":
    main()
