#!/usr/bin/env bash
# Подготовка VPS (Debian/Ubuntu) к запуску linux-trainer.
# Запускать на СЕРВЕРЕ: bash install-server.sh
set -e

SUDO=""
[ "$(id -u)" -ne 0 ] && SUDO="sudo"

echo "==> Ставлю tmux, python3, git"
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq tmux python3 git curl

if ! command -v docker >/dev/null; then
  echo "==> Ставлю Docker"
  curl -fsSL https://get.docker.com | $SUDO sh
else
  echo "==> Docker уже установлен"
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "==> Добавляю $USER в группу docker"
  $SUDO usermod -aG docker "$USER"
  echo "    ВАЖНО: выйди и зайди по SSH заново, чтобы членство в группе применилось"
fi

echo
echo "Проверка:"
docker --version || true
tmux -V
python3 --version
echo
echo "Готово. Дальше:  cd linux-trainer && ./ltrain"
