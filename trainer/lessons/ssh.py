from ..model import Module, Task

LAB = "/root/lab"

m13 = Module(
    id="m13", title="SSH: ключи, доступ, настройка сервера", level="продвинутый",
    tasks=[
        Task(
            id="m13-01", title="Поднимаем SSH-сервер",
            brief="""SSH (Secure Shell) — протокол для безопасного удалённого управления серверами.
Всё, что идёт по SSH, шифруется. Без SSH администрирование удалённых серверов невозможно.

Компоненты SSH:
  openssh-server    SSH-сервер (демон sshd)
  openssh-client    SSH-клиент (команда ssh)

Важные файлы:
  /etc/ssh/sshd_config          конфиг сервера (sshd)
  /etc/ssh/ssh_config           конфиг клиента (системный)
  ~/.ssh/config                 конфиг клиента (пользовательский)
  /etc/ssh/ssh_host_*_key       ключи хоста (подтверждают идентичность сервера)

Демон и порты:
  sshd слушает TCP-порт 22 по умолчанию
  systemctl status ssh          состояние SSH-сервера
  ss -tlnp | grep :22           проверить что порт слушается

Запуск:
  systemctl enable --now ssh    рекомендуется (systemd)
  /usr/sbin/sshd                напрямую (если нет systemd)
  mkdir -p /run/sshd            каталог для pid-файла (нужен для sshd)

Логи SSH:
  journalctl -u ssh -f          смотреть логи в реальном времени
  grep sshd /var/log/auth.log   логи аутентификации

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
            brief="""Аутентификация по паролю — ненадёжна и устарела. Современный стандарт — ключи.

Как работает аутентификация по ключу:
  1. У тебя есть пара: закрытый ключ (у тебя) + открытый ключ (на сервере)
  2. При подключении сервер шлёт вызов (challenge)
  3. Твой клиент подписывает его закрытым ключом
  4. Сервер проверяет подпись открытым ключом — если сошлось, пускает

Типы ключей (от лучшего к худшему):
  ed25519   современный, маленький, быстрый (рекомендуется)
  ecdsa     тоже хорош
  rsa       4096 бит (совместим со старыми системами)
  dsa       устарел, не использовать

`ssh-keygen` — генерация пары ключей:
  ssh-keygen -t ed25519 -C "комментарий"
  -t    тип ключа
  -C    комментарий (обычно email или hostname)
  -N '' пустая парольная фраза (для автоматизации)
  -f    путь к файлу (по умолчанию ~/.ssh/id_ТYPE)

Файлы после генерации:
  ~/.ssh/id_ed25519      ЗАКРЫТЫЙ ключ (никому не показывай!)
  ~/.ssh/id_ed25519.pub  открытый ключ (этот раздаёшь)

Права КРИТИЧНЫ: sshd отказывает если права неправильные:
  ~/.ssh/            700 (только ты)
  ~/.ssh/id_ed25519  600 (только ты читаешь)
  ~/.ssh/id_ed25519.pub  644 (можно всем читать)

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
            brief="""Чтобы войти на сервер по ключу, твой открытый ключ должен быть
в файле `~/.ssh/authorized_keys` целевого пользователя.

Структура `authorized_keys`:
  каждая строка = один разрешённый открытый ключ
  формат: тип_ключа base64_ключ комментарий

  ssh-ed25519 AAAA...= user@laptop
  ssh-rsa AAAA...= backup-script

Права КРИТИЧНЫ (sshd проверяет и молча отказывает при нарушении):
  ~/.ssh/                 700, владелец = alice
  ~/.ssh/authorized_keys  600, владелец = alice

Способы добавить ключ:

`ssh-copy-id` (автоматически):
  ssh-copy-id -i ~/.ssh/id_ed25519.pub alice@server
  — сам создаёт .ssh, добавляет ключ, выставляет права

Вручную:
  mkdir -p /home/alice/.ssh
  cat /root/.ssh/id_ed25519.pub >> /home/alice/.ssh/authorized_keys
  chown -R alice:alice /home/alice/.ssh
  chmod 700 /home/alice/.ssh
  chmod 600 /home/alice/.ssh/authorized_keys

Ограничения в authorized_keys (одна строка = один ключ):
  command="only-this-command" ssh-ed25519 ...   # только эта команда
  from="10.0.0.*" ssh-ed25519 ...               # только с этого IP

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
            brief="""При первом подключении SSH предупреждает: сервер незнакомый, хочешь ли
принять его ключ? Это защита от атаки «человек посередине» (MITM).

  The authenticity of host 'server (10.0.0.1)' can't be established.
  ED25519 key fingerprint is SHA256:ABC...
  Are you sure you want to continue connecting (yes/no)?

Ответив «yes» — ключ хоста сохраняется в `~/.ssh/known_hosts`.
При следующем подключении ключ сравнивается с сохранённым.

Базовые команды клиента:
  ssh пользователь@хост              открыть сессию
  ssh пользователь@хост 'команда'    выполнить команду и вернуться
  ssh -p 2222 пользователь@хост      нестандартный порт
  ssh -i ~/.ssh/другой_ключ user@host  конкретный ключ

Ключи для автоматизации:
  -o StrictHostKeyChecking=no          принять любой ключ (НЕБЕЗОПАСНО!)
  -o StrictHostKeyChecking=accept-new  принять новый, отвергнуть изменённый
  -o StrictHostKeyChecking=yes         строгая проверка (по умолчанию)

`ssh -o StrictHostKeyChecking=accept-new` безопасен для первого подключения
к новому серверу в автоматизированных скриптах.

Если ключ хоста изменился (сервер переустановили):
  ssh-keygen -R hostname    удалить старый ключ из known_hosts

Задание: подключись по ключу как `alice@localhost` и создай там файл `/home/alice/ssh-ok`.""",
            setup="rm -f /home/alice/ssh-ok",
            check="test -f /home/alice/ssh-ok && [ \"$(stat -c '%U' /home/alice/ssh-ok)\" = 'alice' ]",
            hints=["`ssh -o StrictHostKeyChecking=accept-new alice@localhost 'touch ~/ssh-ok'`",
                   "Если просит пароль — значит authorized_keys или права заданы неверно, вернись к прошлому заданию"],
            solution="ssh -o StrictHostKeyChecking=accept-new alice@localhost 'touch ~/ssh-ok'",
        ),
        Task(
            id="m13-05", title="Копирование файлов: scp и rsync",
            brief="""Копировать файлы на/с удалённого сервера можно прямо через SSH.

`scp` (Secure Copy Protocol) — простое копирование:
  scp файл user@host:/путь          локально → на сервер
  scp user@host:/путь файл          с сервера → локально
  scp user@host1:/путь user@host2:/ сервер → сервер
  scp -r каталог/ user@host:/путь   рекурсивно
  scp -P 2222 файл user@host:/путь  нестандартный порт

`rsync` — умная синхронизация (копирует только изменения):
  rsync -av источник user@host:/путь/
  -a    архивный режим (рекурсия + права + время + симлинки)
  -v    verbose
  -z    сжимать при передаче
  -n    dry run: показать что будет скопировано без копирования
  --delete  удалить на цели файлы, которых нет в источнике
  --progress  прогресс

Преимущества rsync:
  — Докачивает только изменённые файлы (быстро при обновлении)
  — Сохраняет права и время изменения
  — Можно делать инкрементные бэкапы
  — Работает локально, по SSH и по rsync-протоколу

Локальная синхронизация:
  rsync -av /src/ /dst/           # без SSH, но та же логика

Важно: rsync -av /src/ /dst/   vs   rsync -av /src /dst/
  С / в конце источника: копируется СОДЕРЖИМОЕ /src
  Без / в конце: копируется сам каталог /src (в /dst/src/)

Задание: скопируй файл `~/lab/notes.md` в домашний каталог alice на `localhost` по SSH.""",
            setup=f"echo 'заметки' > {LAB}/notes.md; rm -f /home/alice/notes.md",
            check="test -f /home/alice/notes.md",
            hints=["`scp ~/lab/notes.md alice@localhost:~/`",
                   "или `rsync -av ~/lab/notes.md alice@localhost:~/`"],
            solution="scp -o StrictHostKeyChecking=accept-new /root/lab/notes.md alice@localhost:~/",
        ),
        Task(
            id="m13-06", title="~/.ssh/config — псевдонимы",
            brief="""Файл `~/.ssh/config` позволяет создать псевдонимы для хостов и задать
настройки подключения. Раз настроил — экономишь время каждый раз.

Формат:
  Host псевдоним
      HostName реальный_адрес_или_ip
      User имя_пользователя
      Port порт (по умолчанию 22)
      IdentityFile путь_к_ключу
      StrictHostKeyChecking accept-new

После настройки:
  ssh lab                  # вместо ssh -i ~/.ssh/id_ed25519 alice@10.0.0.5

Можно задать глобальные настройки:
  Host *
      ServerAliveInterval 60    # keepalive каждые 60 секунд
      ServerAliveCountMax 3     # попыток до разрыва
      StrictHostKeyChecking accept-new
      IdentityFile ~/.ssh/id_ed25519

Несколько хостов:
  Host prod
      HostName prod.example.com
      User deploy
      IdentityFile ~/.ssh/prod_key

  Host staging
      HostName staging.example.com
      User deploy

SSH через прыжок (jump host):
  Host internal
      HostName 192.168.1.5
      ProxyJump bastion.example.com

После `ProxyJump` подключаешься через bastion напрямую в одну команду.

Проверить как парсится конфиг: `ssh -G псевдоним`

Права файла ~/.ssh/config должны быть 600!

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
            brief="""По умолчанию sshd допускает аутентификацию по паролю и вход root.
Это опасно: боты непрерывно перебирают пароли на порту 22 (brute-force).

Минимальный набор защиты в `/etc/ssh/sshd_config`:

  PermitRootLogin no         # запретить вход root напрямую
  PasswordAuthentication no  # только ключи, пароли запрещены
  PubkeyAuthentication yes   # убедиться что ключи разрешены

Дополнительные меры:
  AllowUsers alice bob       # только эти пользователи (whitelist)
  MaxAuthTries 3             # попыток аутентификации (по умолчанию 6)
  LoginGraceTime 30          # секунд на аутентификацию (по умолчанию 120)

ОБЯЗАТЕЛЬНО перед сохранением:
  sshd -t                    # проверить синтаксис конфига (test)
  sshd -T                    # показать итоговую конфигурацию

В Ubuntu часть настроек может быть в `/etc/ssh/sshd_config.d/*.conf`
и переопределять основной файл. Проверь grep:
  grep -r PasswordAuthentication /etc/ssh/

После правки применить:
  systemctl reload ssh    # без разрыва сессий (предпочтительно)
  systemctl restart ssh   # с разрывом всех сессий

Правило: никогда не перезапускай sshd, не проверив синтаксис `sshd -t`,
и держи открытой вторую сессию на случай если что-то пойдёт не так.

Задание: запрети вход root и аутентификацию по паролю в sshd_config и применить конфиг.""",
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
            brief="""Смена стандартного порта 22 на нестандартный (например 2222) не является
серьёзной защитой, но резко снижает шум от автоматических атак ботов.

Настройка нестандартного порта в `/etc/ssh/sshd_config`:
  Port 22      # стандартный
  Port 2222    # добавить второй (можно несколько строк Port)

Или заменить 22 на 2222:
  Port 2222

Подключение на нестандартный порт:
  ssh -p 2222 user@host
  scp -P 2222 файл user@host:/путь   (-P заглавная!)

В ~/.ssh/config:
  Host myserver
      HostName 10.0.0.5
      Port 2222

На боевом сервере:
  — При смене порта нужно обновить правила firewall (ufw, iptables)
  — Открыть новый порт ДО закрытия старого
  — Держать открытой вторую SSH-сессию пока проверяешь

Проверка что порт слушается:
  ss -tlnp | grep :2222
  nmap -p 2222 localhost      # если установлен nmap

Проверка доступности с клиента:
  nc -zv server 2222          # netcat port scan
  ssh -p 2222 -v user@host    # verbose: покажет куда подключается

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
