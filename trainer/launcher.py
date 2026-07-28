"""Точка входа: поднимает песочницу и раскладывает терминал на две панели."""
import argparse
import os
import shlex
import shutil
import subprocess
import sys

from . import sandbox
from .config import (CONTAINER, PROGRESS_FILE, PROJECT_ROOT, TMUX_SESSION,
                     docker_host, load_config, save_config)

B, R, RED, GREEN, YELLOW, DIM = "\033[1m", "\033[0m", "\033[31m", "\033[32m", "\033[33m", "\033[2m"


def die(msg: str, code: int = 1):
    print(f"{RED}✗ {msg}{R}")
    sys.exit(code)


def require_docker():
    if not sandbox.docker_available():
        if docker_host():
            die(f"Не удалось подключиться к Docker на {docker_host()}.\n"
                "  Проверь: ssh на сервер работает без пароля, там установлен Docker,\n"
                "  а твой пользователь состоит в группе docker (проверка: ssh СЕРВЕР docker ps).\n"
                "  Вернуться к локальному режиму: ./ltrain local")
        die("Docker не найден или не запущен.\n"
            "  Установи Docker Desktop (https://www.docker.com/products/docker-desktop/)\n"
            "  или OrbStack (brew install orbstack), запусти его и повтори.\n"
            "  Либо используй сервер: ./ltrain remote user@ip-адрес")


def ensure_ready(prefer_systemd=True) -> bool:
    require_docker()
    sandbox.ensure_image()
    return sandbox.ensure_container(prefer_systemd=prefer_systemd)


def tmux_ok() -> bool:
    return shutil.which("tmux") is not None


def tmux_has_session() -> bool:
    return subprocess.run(["tmux", "has-session", "-t", TMUX_SESSION],
                          capture_output=True).returncode == 0


def cmd_start(args):
    # Уже есть живая сессия (например, после переподключения по SSH) — просто возвращаемся в неё.
    if tmux_ok() and tmux_has_session() and not getattr(args, "fresh", False) and not args.no_tmux:
        print(f"{GREEN}↻ возвращаюсь в открытую сессию{R} {DIM}(начать заново: ./ltrain start --fresh){R}")
        os.execvp("tmux", ["tmux", "attach", "-t", TMUX_SESSION])

    systemd = ensure_ready(prefer_systemd=not args.no_systemd)
    py = sys.executable or "python3"
    dh = docker_host()
    dh_prefix = f"DOCKER_HOST={shlex.quote(dh)} " if dh else ""
    panel_cmd = (
        f"cd {shlex.quote(str(PROJECT_ROOT))} && "
        f"{dh_prefix}LTRAIN_SYSTEMD={'1' if systemd else '0'} {shlex.quote(py)} -m trainer.panel; "
        f"tmux kill-session -t {TMUX_SESSION}"
    )
    shell_cmd = f"{dh_prefix}docker exec -it {CONTAINER} bash -l"

    if args.no_tmux or not tmux_ok():
        if not tmux_ok():
            print(f"{YELLOW}tmux не установлен (brew install tmux) — запускаю без разделения экрана.{R}")
            print(f"{DIM}Открой второе окно терминала и выполни: ./ltrain shell{R}\n")
            input("Enter чтобы продолжить...")
        os.environ["LTRAIN_SYSTEMD"] = "1" if systemd else "0"
        from .panel import main as panel_main
        panel_main()
        return

    subprocess.run(["tmux", "kill-session", "-t", TMUX_SESSION], capture_output=True)
    subprocess.run(["tmux", "new-session", "-d", "-s", TMUX_SESSION, "-n", "lab", shell_cmd], check=True)

    split = ["tmux", "split-window", "-h", "-t", f"{TMUX_SESSION}:0", "-l", "42%", panel_cmd]
    if subprocess.run(split, capture_output=True).returncode != 0:
        subprocess.run(["tmux", "split-window", "-h", "-t", f"{TMUX_SESSION}:0", "-p", "42", panel_cmd], check=True)

    for opt in (["mouse", "on"], ["history-limit", "20000"]):
        subprocess.run(["tmux", "set-option", "-t", TMUX_SESSION, *opt], capture_output=True)
    subprocess.run(["tmux", "set-option", "-t", TMUX_SESSION, "status-left",
                    " linux-trainer "], capture_output=True)
    subprocess.run(["tmux", "set-option", "-t", TMUX_SESSION, "status-right",
                    " Ctrl+b o — сменить панель | Ctrl+b d — выйти "], capture_output=True)
    subprocess.run(["tmux", "select-pane", "-t", f"{TMUX_SESSION}:0.0"], capture_output=True)

    os.execvp("tmux", ["tmux", "attach", "-t", TMUX_SESSION])


def cmd_shell(args):
    require_docker()
    sandbox.ensure_container()
    if docker_host():
        os.environ["DOCKER_HOST"] = docker_host()
    os.execvp("docker", ["docker", "exec", "-it", CONTAINER, "bash", "-l"])


def cmd_remote(args):
    target = args.target
    if "://" not in target:
        target = "ssh://" + target
    cfg = load_config()
    cfg["docker_host"] = target
    save_config(cfg)
    print(f"{GREEN}✓ песочница будет запускаться на {target}{R}")
    print(f"{DIM}Требования на сервере: установлен Docker, вход по SSH-ключу без пароля,\n"
          f"пользователь состоит в группе docker.{R}")
    print("Проверка: ./ltrain status")


def cmd_image(args):
    cfg = load_config()
    if args.ref in ("local", "default", "-"):
        cfg.pop("image", None)
        save_config(cfg)
        print(f"{GREEN}✓ образ будет собираться локально{R}")
    else:
        cfg["image"] = args.ref
        save_config(cfg)
        print(f"{GREEN}✓ будет использоваться готовый образ {args.ref}{R}")
        print(f"{DIM}Применить: ./ltrain restart{R}")


def cmd_local(args):
    cfg = load_config()
    cfg.pop("docker_host", None)
    save_config(cfg)
    print(f"{GREEN}✓ песочница снова запускается локально{R}")


def cmd_stop(args):
    subprocess.run(["tmux", "kill-session", "-t", TMUX_SESSION], capture_output=True)
    subprocess.run(["docker", "stop", CONTAINER], capture_output=True)
    print(f"{GREEN}✓ песочница остановлена (данные сохранены){R}")


def cmd_restart(args):
    subprocess.run(["tmux", "kill-session", "-t", TMUX_SESSION], capture_output=True)
    sandbox.remove_container()
    cmd_start(args)


def cmd_reset(args):
    args.fresh = True
    require_docker()
    print("Пересоздаю песочницу с нуля...")
    subprocess.run(["tmux", "kill-session", "-t", TMUX_SESSION], capture_output=True)
    sandbox.remove_container()
    if args.progress and PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
        print("Прогресс обучения сброшен.")
    sandbox.ensure_container()
    print(f"{GREEN}✓ готово, запускай ./ltrain start{R}")


def cmd_rebuild(args):
    require_docker()
    subprocess.run(["tmux", "kill-session", "-t", TMUX_SESSION], capture_output=True)
    sandbox.remove_container()
    subprocess.run(["docker", "rmi", "-f", sandbox.image()], capture_output=True)
    if sandbox.is_remote_image():
        sandbox.pull_image()
    else:
        sandbox.build_image()
    print(f"{GREEN}✓ образ пересобран{R}")


def cmd_status(args):
    print(f"песочница:   {sandbox.where()}")
    print(f"образ:       {sandbox.image()}"
          f"{' (из реестра)' if sandbox.is_remote_image() else ' (локальная сборка)'}")
    print(f"docker:      {'доступен' if sandbox.docker_available() else 'НЕДОСТУПЕН'}")
    print(f"tmux:        {'есть' if tmux_ok() else 'НЕТ (brew install tmux)'}")
    if sandbox.docker_available():
        print(f"статус:      {'готов' if sandbox.image_exists() else 'не скачан/не собран'}")
        state = sandbox.container_state()
        print(f"контейнер:   {state}")
        if state == "running":
            print(f"systemd:     {'работает' if sandbox.has_systemd() else 'нет'}")
    if PROGRESS_FILE.exists():
        import json
        data = json.loads(PROGRESS_FILE.read_text())
        print(f"прогресс:    сдано заданий {len(data.get('done', []))}")


def main():
    p = argparse.ArgumentParser(prog="ltrain", description="Тренажёр Linux в терминале")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("start", help="запустить тренажёр (по умолчанию)")
    s.add_argument("--no-tmux", action="store_true", help="без разделения экрана")
    s.add_argument("--no-systemd", action="store_true", help="песочница без systemd")
    s.add_argument("--fresh", action="store_true", help="пересоздать раскладку панелей с нуля")
    s.set_defaults(func=cmd_start)

    sub.add_parser("shell", help="просто зайти в песочницу").set_defaults(func=cmd_shell)
    sub.add_parser("stop", help="остановить песочницу").set_defaults(func=cmd_stop)

    rs = sub.add_parser("restart", help="перезапустить песочницу")
    rs.add_argument("--no-tmux", action="store_true")
    rs.add_argument("--no-systemd", action="store_true")
    rs.add_argument("--fresh", action="store_true")
    rs.set_defaults(func=cmd_restart)

    r = sub.add_parser("reset", help="пересоздать песочницу с нуля")
    r.add_argument("--progress", action="store_true", help="ещё и обнулить прогресс")
    r.set_defaults(func=cmd_reset)

    sub.add_parser("rebuild", help="пересобрать образ").set_defaults(func=cmd_rebuild)

    rm = sub.add_parser("remote", help="держать песочницу на своём сервере (VPS)")
    rm.add_argument("target", help="user@host или ssh://user@host:порт")
    rm.set_defaults(func=cmd_remote)

    sub.add_parser("local", help="вернуть песочницу на эту машину").set_defaults(func=cmd_local)

    im = sub.add_parser("image", help="использовать готовый образ из реестра")
    im.add_argument("ref", help="ghcr.io/user/repo:latest  или  local для локальной сборки")
    im.set_defaults(func=cmd_image)
    sub.add_parser("status", help="что установлено и в каком состоянии").set_defaults(func=cmd_status)

    args = p.parse_args()
    if not args.cmd:
        args = p.parse_args(["start"])
    try:
        args.func(args)
    except sandbox.SandboxError as e:
        die(str(e))
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
