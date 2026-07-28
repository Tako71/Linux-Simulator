"""Реестр учебных модулей.

Чтобы добавить свой модуль: создай файл рядом с этим, опиши Module/Task
и добавь его MODULES в список ниже.
"""
from . import admin, advanced, basics, incidents, ssh, text, theory

MODULES = (basics.MODULES + text.MODULES + admin.MODULES + advanced.MODULES
           + ssh.MODULES + incidents.MODULES + theory.MODULES)

TASK_INDEX = {t.id: (m, t) for m in MODULES for t in m.tasks}
ALL_TASKS = [t for m in MODULES for t in m.tasks]
