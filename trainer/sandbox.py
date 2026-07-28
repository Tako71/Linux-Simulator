"""Всё, что связано с Docker-песочницей."""
import os
import shutil
import subprocess
import time

from .config import (CONTAINER, CWD_FILE, HISTORY_FILE, LAB_DIR,
                     PROJECT_ROOT, docker_host, image)


class SandboxError(RuntimeError):
    pass


def docker_env() -> dict:
    """Окружение для docker-клиента: локальный демон или демон на VPS."""
    env = os.environ.copy()
    host = docker_host()
    if host:
        env["DOCKER_HOST"] = host
    return env


def where() -> str:
    host = docker_host()
    return f"удалённо ({host})" if host else "локально на этой машине"


def _run(args, timeout=600, capture=True):
    try:
        return subprocess.run(
            args,
            capture_output=capture,
            text=True,
            timeout=timeout,
            env=docker_env(),
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, 127, "", "docker не установлен")


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return _run(["docker", "info"], timeout=30).returncode == 0
    except Exception:
        return False


def image_exists() -> bool:
    r = _run(["docker", "image", "inspect", image()])
    return r.returncode == 0


def is_remote_image() -> bool:
    """Образ из реестра (есть хост с точкой или порт) — значит его можно скачать."""
    ref = image()
    head = ref.split("/")[0]
    return "/" in ref and ("." in head or ":" in head or head == "localhost")


def pull_image() -> bool:
    print(f"Скачиваю готовый образ {image()}...")
    r = subprocess.run(["docker", "pull", image()], text=True, env=docker_env())
    return r.returncode == 0


def ensure_image():
    """Достаём образ: скачиваем из реестра либо собираем локально."""
    if image_exists():
        return
    if is_remote_image() and pull_image():
        return
    build_image()


def build_image(verbose=True):
    print(f"Собираю образ {image()} (первый раз это 2-4 минуты)...")
    r = subprocess.run(
        ["docker", "build", "-t", image(), "."],
        cwd=str(PROJECT_ROOT),
        text=True,
        env=docker_env(),
    )
    if r.returncode != 0:
        raise SandboxError("не удалось собрать образ")


def container_state() -> str:
    """running | exited | absent"""
    r = _run(["docker", "inspect", "-f", "{{.State.Status}}", CONTAINER])
    if r.returncode != 0:
        return "absent"
    return r.stdout.strip()


def remove_container():
    _run(["docker", "rm", "-f", CONTAINER], timeout=120)


def _start_container(systemd: bool):
    args = [
        "docker", "run", "-d",
        "--name", CONTAINER,
        "--hostname", "lab",
    ]
    if systemd:
        args += [
            "--privileged",
            "--cgroupns=host",
            "-v", "/sys/fs/cgroup:/sys/fs/cgroup:rw",
            "--tmpfs", "/run",
            "--tmpfs", "/run/lock",
        ]
    args += [image()]
    if not systemd:
        args += ["sleep", "infinity"]
    r = _run(args, timeout=180)
    if r.returncode != 0:
        raise SandboxError(r.stderr.strip())


def _systemd_alive(timeout=25) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = _run(["docker", "exec", CONTAINER, "systemctl", "is-system-running"], timeout=20)
        out = (r.stdout + r.stderr).strip()
        if out in ("running", "degraded", "starting", "maintenance"):
            if out != "starting":
                return True
        elif "offline" in out or "Failed to connect" in out:
            pass
        time.sleep(1.5)
    return False


def ensure_container(prefer_systemd=True) -> bool:
    """Гарантирует, что контейнер запущен. Возвращает True, если systemd доступен."""
    state = container_state()
    if state == "running":
        return has_systemd()
    if state == "exited":
        _run(["docker", "start", CONTAINER], timeout=120)
        time.sleep(1)
        if container_state() == "running":
            return has_systemd()
        remove_container()

    if prefer_systemd:
        print("Запускаю песочницу с systemd...")
        _start_container(systemd=True)
        if _systemd_alive():
            return True
        print("systemd в контейнере не поднялся — перезапускаю в упрощённом режиме.")
        remove_container()

    _start_container(systemd=False)
    time.sleep(1)
    if container_state() != "running":
        raise SandboxError("контейнер не запустился")
    return False


def has_systemd() -> bool:
    r = _run(["docker", "exec", CONTAINER, "systemctl", "is-system-running"], timeout=15)
    return (r.stdout + r.stderr).strip() in ("running", "degraded", "maintenance", "starting")


# --------------------------------------------------------------------------
# Выполнение команд внутри песочницы
# --------------------------------------------------------------------------

def sh(command: str, cwd: str | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    args = ["docker", "exec"]
    if cwd:
        args += ["-w", cwd]
    args += [CONTAINER, "bash", "-lc", command]
    try:
        return _run(args, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, "", "timeout")


def read_file(path: str) -> str:
    r = sh(f"cat {path} 2>/dev/null || true")
    return r.stdout


def current_cwd() -> str:
    cwd = read_file(CWD_FILE).strip()
    if not cwd:
        return LAB_DIR
    r = sh(f"test -d {cwd}")
    return cwd if r.returncode == 0 else LAB_DIR


def history_lines() -> list[str]:
    return [ln for ln in read_file(HISTORY_FILE).splitlines() if ln.strip()]


def reset_lab():
    sh(f"rm -rf {LAB_DIR}; mkdir -p {LAB_DIR}")
