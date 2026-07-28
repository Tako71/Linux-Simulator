"""Структуры данных для уроков."""
from dataclasses import dataclass, field


@dataclass
class Task:
    id: str
    title: str
    brief: str                     # текст задания (можно многострочный)
    check: str = ""                # shell-команда в песочнице; код 0 == задание сдано
    check_history: str = ""        # regex по командам, введённым после открытия задания
    hints: tuple = ()              # подсказки, выдаются по одной
    solution: str = ""             # эталонное решение
    setup: str = ""                # что подготовить перед заданием
    needs: str = ""                # "systemd" | "net" | ""
    fail_msg: str = "Пока не сходится. Проверь ещё раз."


@dataclass
class Module:
    id: str
    title: str
    level: str                     # новичок / уверенный / администратор / продвинутый
    tasks: list = field(default_factory=list)
