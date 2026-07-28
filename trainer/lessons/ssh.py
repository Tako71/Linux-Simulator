from ..model import Module, Task

LAB = "/root/lab"

m13 = Module(
    id="m13", title="SSH: ключи, доступ, настройка сервера", level="продвинутый",
    tasks=[
        Task(
            id="m13-01", title="Поднимаем SSH-сервер",
            brief="""SSH — основной способ администрировать сервер. Пакет `openssh-server`, служба `ssh`,
конфиг сервера `/etc/ssh/sshd_config`, конфиг клиента `/etc/ssh/ssh_config` и `~/.ssh/config`.
По умолчанию слушает TCP-порт 22.

Задание: запусти SSH-сервер и убедись через `ss`, что порт 22 слушается.""",
            setup="systemctl stop ssh 2>/dev/null; pkill -x sshd 2>/dev/null; true",
            check="ss -tln | grep -qE ':22\\s'",
            check_history=r"\bss\b|systemctl|sshd",
            hints=["`systemctl enable --now ssh`",
                   "Если systemd недоступен: `mkdir -p /run/sshd && /usr/sbin/sshd`",
                   "Проверка: `ss -tlnp | grep 22`"],
            solution="systemctl enable --now ssh || (mkdir -p /run/sshd && /usr/sbin/sshd)",
        ),
        Task(
            id="m13-02", title="Пара ключей",
            brief="""Пароли на серверах — плохая практика, работают по ключам.
`ssh-keygen -t ed25519 -C комментарий` создаёт пару: `~/.ssh/id_ed25519` (закрытый, никому!)
и `~/.ssh/id_ed25519.pub` (открытый, его раздают). Ключ `-N ''` задаёт пустую парольную фразу,
`-f` — путь к файлу.

Задание: сгенерируй ключ ed25519 в `/root/.ssh/id_ed25519` без парольной фразы.""",
            setup="rm -f /root/.ssh/id_ed25519 /root/.ssh/id_ed25519.pub",
            check=("test -f /root/.ssh/id_ed25519 && test -f /root/.ssh/id_ed25519.pub "
                   "&& grep -q 'ssh-ed25519' /root/.ssh/id_ed25519.pub "
                   "&& [ \"$(stat -c '%a' /root/.ssh/id_ed25519)\" = '600' ]"),
            hints=["`ssh-keygen -t ed25519 -N '' -f /root/.ssh/id_ed25519`",
                   "Закрытый ключ обязан иметь права 600 — ssh-keygen делает это сам"],
            solution="ssh-keygen -t ed25519 -N '' -f /root/.ssh/id_ed25519 -C lab",
        ),
        Task(
            id="m13-03", title="authorized_keys",
            brief="""Чтобы пустить кого-то по ключу, его открытый ключ кладут в `~/.ssh/authorized_keys`
целевого пользователя. Права критичны: каталог `~/.ssh` — 700, файл — 600, владелец — сам пользователь.
При неверных правах sshd молча откажет (и напишет об этом в лог).

Задание: разреши root-у заходить по ключу к пользователю `alice`: положи открытый ключ root
в `/home/alice/.ssh/authorized_keys` с правильными правами и владельцем.""",
            setup=("id alice >/dev/null 2>&1 || useradd -m -s /bin/bash alice; "
                   "rm -rf /home/alice/.ssh"),
            check=("grep -q 'ssh-ed25519' /home/alice/.ssh/authorized_keys "
                   "&& [ \"$(stat -c '%a %U' /home/alice/.ssh)\" = '700 alice' ] "
                   "&& [ \"$(stat -c '%a %U' /home/alice/.ssh/authorized_keys)\" = '600 alice' ]"),
            hints=["Проще всего: `ssh-copy-id -i /root/.ssh/id_ed25519.pub alice@localhost` (спросит пароль alice)",
                   "Вручную: `mkdir -p /home/alice/.ssh && cat /root/.ssh/id_ed25519.pub >> /home/alice/.ssh/authorized_keys`",
                   "Потом: `chown -R alice:alice /home/alice/.ssh && chmod 700 /home/alice/.ssh && chmod 600 /home/alice/.ssh/authorized_keys`"],
            solution=("mkdir -p /home/alice/.ssh && cat /root/.ssh/id_ed25519.pub > /home/alice/.ssh/authorized_keys && "
                      "chown -R alice:alice /home/alice/.ssh && chmod 700 /home/alice/.ssh && "
                      "chmod 600 /home/alice/.ssh/authorized_keys"),
        ),
        Task(
            id="m13-04", title="Первое подключение",
            brief="""`ssh пользователь@хост` открывает сессию, `ssh пользователь@хост 'команда'` выполняет одну команду
и возвращает управление. При первом подключении ssh спрашивает про отпечаток хоста —
`-o StrictHostKeyChecking=accept-new` принимает его автоматически.

Задание: подключись по ключу как `alice@localhost` и создай там файл `/home/alice/ssh-ok`.""",
            setup="rm -f /home/alice/ssh-ok",
            check="test -f /home/alice/ssh-ok && [ \"$(stat -c '%U' /home/alice/ssh-ok)\" = 'alice' ]",
            hints=["`ssh -o StrictHostKeyChecking=accept-new alice@localhost 'touch ~/ssh-ok'`",
                   "Если просит пароль — значит authorized_keys или права заданы неверно, вернись к прошлому заданию"],
            solution="ssh -o StrictHostKeyChecking=accept-new alice@localhost 'touch ~/ssh-ok'",
        ),
        Task(
            id="m13-05", title="Копирование файлов: scp и rsync",
            brief="""`scp файл user@host:/путь` копирует по SSH, `-r` — каталог.
`rsync -avz источник user@host:/путь` умнее: докачивает изменения, сохраняет права, сжимает.
Обратное направление тоже работает: `scp user@host:/файл .`

Задание: скопируй файл `~/lab/notes.md` в домашний каталог alice на `localhost` по SSH.""",
            setup=f"echo 'заметки' > {LAB}/notes.md; rm -f /home/alice/notes.md",
            check="test -f /home/alice/notes.md",
            hints=["`scp ~/lab/notes.md alice@localhost:~/`",
                   "или `rsync -av ~/lab/notes.md alice@localhost:~/`"],
            solution="scp -o StrictHostKeyChecking=accept-new /root/lab/notes.md alice@localhost:~/",
        ),
        Task(
            id="m13-06", title="~/.ssh/config — псевдонимы",
            brief="""Чтобы не набирать длинные команды, хосты описывают в `~/.ssh/config`:

  Host lab
      HostName localhost
      User alice
      IdentityFile ~/.ssh/id_ed25519

После этого достаточно `ssh lab`.

Задание: опиши хост `lab` в `/root/.ssh/config` (HostName localhost, User alice) и подключись командой `ssh lab`.""",
            setup="rm -f /root/.ssh/config /home/alice/config-ok",
            check=("ssh -G lab 2>/dev/null | grep -q 'hostname localhost' && "
                   "ssh -G lab 2>/dev/null | grep -q 'user alice' && test -f /home/alice/config-ok"),
            hints=["Создай `/root/.ssh/config` с блоком Host lab",
                   "Проверить разбор конфига: `ssh -G lab`",
                   "Затем: `ssh lab 'touch ~/config-ok'`"],
            solution=("printf 'Host lab\\n    HostName localhost\\n    User alice\\n    "
                      "IdentityFile /root/.ssh/id_ed25519\\n    StrictHostKeyChecking accept-new\\n' > /root/.ssh/config && "
                      "chmod 600 /root/.ssh/config && ssh lab 'touch ~/config-ok'"),
        ),
        Task(
            id="m13-07", title="Ужесточаем sshd",
            brief="""Базовая защита сервера: запретить вход root-у и отключить пароли (только ключи).
В `/etc/ssh/sshd_config`:

  PermitRootLogin no
  PasswordAuthentication no

Внимание: в Ubuntu часть настроек переопределяется файлами из `/etc/ssh/sshd_config.d/`.
`sshd -t` проверяет синтаксис ДО перезапуска, `sshd -T` показывает итоговую конфигурацию.
Правило: никогда не перезапускай sshd, не проверив конфиг, — можно потерять доступ к серверу.""",
            setup="sed -i '/^PermitRootLogin/d;/^PasswordAuthentication/d' /etc/ssh/sshd_config; systemctl reload ssh 2>/dev/null; true",
            check=("sshd -t && sshd -T 2>/dev/null | grep -qi '^permitrootlogin no' && "
                   "sshd -T 2>/dev/null | grep -qi '^passwordauthentication no'"),
            check_history=r"sshd\s+-t|systemctl\s+(reload|restart)\s+ssh",
            hints=["Отредактируй `/etc/ssh/sshd_config` (nano или `echo ... >>`)",
                   "Проверь синтаксис: `sshd -t`",
                   "Если настройка не применяется — посмотри `/etc/ssh/sshd_config.d/` и `grep -r Password /etc/ssh/`",
                   "Применить: `systemctl reload ssh`"],
            solution=("printf 'PermitRootLogin no\\nPasswordAuthentication no\\n' >> /etc/ssh/sshd_config && "
                      "sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config.d/*.conf 2>/dev/null; "
                      "sshd -t && systemctl reload ssh"),
        ),
        Task(
            id="m13-08", title="Нестандартный порт и проверка доступности",
            brief="""Смена порта — не защита, но отсекает шум ботов. Директива `Port 2222` в `sshd_config`,
подключение — `ssh -p 2222 user@host`. На боевом сервере порт нужно ещё открыть в firewall.
Мудрое правило: меняя SSH, держи открытой вторую, уже работающую сессию — если сломаешь, будет как вернуться.

Задание: заставь sshd слушать ДОПОЛНИТЕЛЬНО порт 2222 и подключись через него.""",
            setup="sed -i '/^Port 2222/d' /etc/ssh/sshd_config; rm -f /home/alice/port-ok; systemctl reload ssh 2>/dev/null; true",
            check="ss -tln | grep -q ':2222' && test -f /home/alice/port-ok",
            hints=["Добавь строку `Port 2222` в `/etc/ssh/sshd_config` (строка `Port 22` может быть закомментирована — это нормально)",
                   "`sshd -t && systemctl restart ssh`",
                   "`ssh -p 2222 lab 'touch ~/port-ok'`"],
            solution=("echo 'Port 2222' >> /etc/ssh/sshd_config && sshd -t && systemctl restart ssh && "
                      "sleep 1 && ssh -p 2222 lab 'touch ~/port-ok'"),
        ),
    ],
)

MODULES = [m13]
