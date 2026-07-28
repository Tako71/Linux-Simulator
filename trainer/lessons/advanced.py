from ..model import Module, Task

LAB = "/root/lab"

m10 = Module(
    id="m10", title="Сеть", level="продвинутый",
    tasks=[
        Task(
            id="m10-01", title="Интерфейсы и адреса",
            brief="""`ip a` (полностью `ip address show`) показывает интерфейсы и IP-адреса.
Старые аналоги `ifconfig`/`netstat` считаются устаревшими — учись сразу на `ip` и `ss`.

Задание: сохрани информацию об интерфейсах в `~/lab/ip-addr.txt`.""",
            check=f"grep -q 'inet ' {LAB}/ip-addr.txt && grep -q 'lo' {LAB}/ip-addr.txt",
            hints=["`ip a > ~/lab/ip-addr.txt`"],
            solution="ip a > ~/lab/ip-addr.txt",
        ),
        Task(
            id="m10-02", title="Маршруты и шлюз",
            brief="""`ip route` показывает таблицу маршрутизации. Строка `default via X dev eth0` — это шлюз по умолчанию.

Задание: запиши таблицу маршрутизации в `~/lab/routes.txt`.""",
            check=f"grep -q 'default' {LAB}/routes.txt",
            hints=["`ip route > ~/lab/routes.txt`"],
            solution="ip route > ~/lab/routes.txt",
        ),
        Task(
            id="m10-03", title="Открытые порты: ss",
            brief="""`ss -tulpn`: t=TCP, u=UDP, l=слушающие, p=процесс, n=номера портов вместо имён.
Первое, что смотрят, когда «сервис не отвечает» или «порт занят».

Задание: сохрани список слушающих сокетов в `~/lab/ports.txt`.""",
            check=f"test -s {LAB}/ports.txt && grep -qi 'state\\|LISTEN' {LAB}/ports.txt",
            check_history=r"\bss\b",
            hints=["`ss -tulpn > ~/lab/ports.txt`"],
            solution="ss -tulpn > ~/lab/ports.txt",
        ),
        Task(
            id="m10-04", title="Своё имя в /etc/hosts",
            brief="""`/etc/hosts` — локальная таблица имён, она проверяется раньше DNS. Формат: `IP имя [псевдонимы]`.

Задание: добавь в `/etc/hosts` запись, чтобы имя `myserver` резолвилось в `10.10.10.50`.""",
            setup="sed -i '/myserver/d' /etc/hosts",
            check="getent hosts myserver | grep -q '10.10.10.50'",
            hints=["`echo '10.10.10.50 myserver' >> /etc/hosts`", "Проверить: `getent hosts myserver` или `ping -c1 myserver`"],
            solution="echo '10.10.10.50 myserver' >> /etc/hosts",
        ),
        Task(
            id="m10-05", title="DNS: dig",
            brief="""`dig имя` делает DNS-запрос, `dig +short имя` — только ответ, `dig @8.8.8.8 имя` — к конкретному серверу.
Настройки резолвера — в `/etc/resolv.conf`.

Задание: получи A-запись для `example.com` и сохрани короткий ответ в `~/lab/dns.txt`.""",
            needs="net",
            check=f"grep -Eq '^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+' {LAB}/dns.txt",
            hints=["`dig +short example.com > ~/lab/dns.txt`"],
            solution="dig +short example.com > ~/lab/dns.txt",
        ),
        Task(
            id="m10-06", title="curl: HTTP из терминала",
            brief="""`curl URL` печатает ответ, `-o файл` сохраняет, `-I` — только заголовки,
`-s` — тихо, `-L` — идти по редиректам.

Задание: сохрани HTTP-заголовки ответа `http://example.com` в `~/lab/headers.txt`.""",
            needs="net",
            check=f"grep -qi 'HTTP/' {LAB}/headers.txt",
            hints=["`curl -sI http://example.com > ~/lab/headers.txt`"],
            solution="curl -sI http://example.com > ~/lab/headers.txt",
        ),
        Task(
            id="m10-07", title="Слушаем порт",
            brief="""`nc -l 8080` открывает TCP-порт на прослушивание — удобно проверять сетевую доступность.

Задание: запусти в фоне прослушивание TCP-порта 8080 и убедись через `ss`, что порт слушается.""",
            setup="pkill -f 'nc -[l]' 2>/dev/null; true",
            check="ss -tln | grep -q ':8080'",
            hints=["`nc -l 8080 &`", "Проверить: `ss -tlnp | grep 8080`"],
            solution="nc -l 8080 &",
        ),
    ],
)

m11 = Module(
    id="m11", title="systemd: службы и логи", level="продвинутый",
    tasks=[
        Task(
            id="m11-01", title="Состояние служб",
            brief="""`systemctl status служба` — состояние, `systemctl list-units --type=service` — список,
`--failed` — что упало. systemd — это система инициализации: он запускает и следит за всеми службами.

Задание: сохрани список служб в `~/lab/services.txt`.""",
            needs="systemd",
            check=f"grep -q '\\.service' {LAB}/services.txt",
            hints=["`systemctl list-units --type=service > ~/lab/services.txt`"],
            solution="systemctl list-units --type=service --all > ~/lab/services.txt",
        ),
        Task(
            id="m11-02", title="Запуск и автозагрузка",
            brief="""`systemctl start|stop|restart служба` — управление сейчас.
`systemctl enable|disable служба` — автозапуск при загрузке. `enable --now` делает и то и другое.
Разница принципиальная: `start` без `enable` не переживёт перезагрузку.

Задание: запусти службу `cron` и включи её автозагрузку.""",
            needs="systemd",
            setup="systemctl disable --now cron 2>/dev/null; true",
            check="systemctl is-active cron | grep -q '^active' && systemctl is-enabled cron | grep -q 'enabled'",
            hints=["`systemctl enable --now cron`", "Проверить: `systemctl status cron`"],
            solution="systemctl enable --now cron",
        ),
        Task(
            id="m11-03", title="Логи: journalctl",
            brief="""`journalctl -u служба` — логи конкретной службы, `-f` — следить в реальном времени,
`-n 50` — последние 50 строк, `-p err` — только ошибки, `--since '10 min ago'` — по времени.

Задание: сохрани последние 50 строк системного журнала в `~/lab/journal.txt`.""",
            needs="systemd",
            check=f"test -s {LAB}/journal.txt",
            check_history=r"journalctl",
            hints=["`journalctl -n 50 --no-pager > ~/lab/journal.txt`"],
            solution="journalctl -n 50 --no-pager > ~/lab/journal.txt",
        ),
        Task(
            id="m11-04", title="Свой unit-файл",
            brief="""Собственная служба описывается файлом `/etc/systemd/system/имя.service`:

  [Unit]
  Description=My worker
  [Service]
  ExecStart=/root/lab/worker.sh
  Restart=always
  [Install]
  WantedBy=multi-user.target

После создания обязателен `systemctl daemon-reload`.

Задание: создай службу `worker.service`, запускающую готовый скрипт `/root/lab/worker.sh`,
включи её автозагрузку и запусти. Служба должна быть active.""",
            needs="systemd",
            setup=(f"printf '#!/bin/bash\\nwhile true; do echo worker alive; sleep 5; done\\n' > {LAB}/worker.sh && "
                   f"chmod +x {LAB}/worker.sh; systemctl disable --now worker 2>/dev/null; "
                   f"rm -f /etc/systemd/system/worker.service; systemctl daemon-reload 2>/dev/null; true"),
            check=("test -f /etc/systemd/system/worker.service && systemctl is-active worker | grep -q '^active' "
                   "&& systemctl is-enabled worker | grep -q 'enabled'"),
            hints=["Создай файл редактором: `nano /etc/systemd/system/worker.service`",
                   "Затем `systemctl daemon-reload`",
                   "И `systemctl enable --now worker`"],
            solution=("cat > /etc/systemd/system/worker.service <<'EOF'\n[Unit]\nDescription=Worker\n\n[Service]\n"
                      "ExecStart=/root/lab/worker.sh\nRestart=always\n\n[Install]\nWantedBy=multi-user.target\nEOF\n"
                      "systemctl daemon-reload && systemctl enable --now worker"),
        ),
        Task(
            id="m11-05", title="Диагностика своей службы",
            brief="""Когда служба не поднимается, смотрят `systemctl status имя` и `journalctl -u имя -n 50`.

Задание: сохрани логи службы `worker` в `~/lab/worker-log.txt` и перезапусти её.""",
            needs="systemd",
            check=f"test -s {LAB}/worker-log.txt && grep -qi 'worker' {LAB}/worker-log.txt",
            check_history=r"systemctl\s+restart\s+worker",
            hints=["`journalctl -u worker -n 50 --no-pager > ~/lab/worker-log.txt`", "`systemctl restart worker`"],
            solution="journalctl -u worker -n 50 --no-pager > ~/lab/worker-log.txt; systemctl restart worker",
        ),
    ],
)

m12 = Module(
    id="m12", title="Bash-скрипты и планировщик", level="продвинутый",
    tasks=[
        Task(
            id="m12-01", title="Скрипт с аргументом",
            brief="""В скрипте `$1`, `$2` — аргументы, `$0` — имя скрипта, `$#` — их количество, `$@` — все.
Начинай скрипты с `#!/bin/bash` и делай `chmod +x`.

Задание: напиши `~/lab/greet.sh`, который на `./greet.sh Мир` печатает `Привет, Мир!`.""",
            setup=f"rm -f {LAB}/greet.sh",
            check=f"test -x {LAB}/greet.sh && bash {LAB}/greet.sh Мир | grep -qi 'привет' && bash {LAB}/greet.sh Мир | grep -q 'Мир'",
            hints=["Внутри: `echo \"Привет, $1!\"`", "Не забудь `chmod +x`"],
            solution="printf '#!/bin/bash\\necho \"Привет, $1!\"\\n' > ~/lab/greet.sh && chmod +x ~/lab/greet.sh",
        ),
        Task(
            id="m12-02", title="Переменные и подстановка команд",
            brief="""`NAME=значение` (без пробелов вокруг `=`), обращение — `$NAME` или `${NAME}`.
`$(команда)` подставляет вывод команды. Двойные кавычки сохраняют подстановку, одинарные — нет.

Задание: напиши `~/lab/sysinfo.sh`, который создаёт файл `~/lab/sysinfo.txt`
со строками вида `host=<имя хоста>` и `date=<текущая дата>`, и запусти его.""",
            setup=f"rm -f {LAB}/sysinfo.sh {LAB}/sysinfo.txt",
            check=f"grep -q \"^host=$(hostname)\" {LAB}/sysinfo.txt && grep -q '^date=' {LAB}/sysinfo.txt && test -s {LAB}/sysinfo.sh",
            hints=["`echo \"host=$(hostname)\" > ~/lab/sysinfo.txt`", "`echo \"date=$(date)\" >> ~/lab/sysinfo.txt`"],
            solution="printf '#!/bin/bash\\necho \"host=$(hostname)\" > /root/lab/sysinfo.txt\\necho \"date=$(date)\" >> /root/lab/sysinfo.txt\\n' > ~/lab/sysinfo.sh && bash ~/lab/sysinfo.sh",
        ),
        Task(
            id="m12-03", title="Условия",
            brief="""  if [ -f "$1" ]; then
    echo "файл есть"
  else
    echo "файла нет"
  fi

Проверки: `-f` файл, `-d` каталог, `-z` пустая строка, `-eq/-lt/-gt` числа, `=`/`!=` строки.

Задание: напиши `~/lab/check.sh`, который печатает `EXISTS`, если переданный путь существует, иначе `MISSING`.""",
            setup=f"rm -f {LAB}/check.sh",
            check=f"bash {LAB}/check.sh /etc | grep -q EXISTS && bash {LAB}/check.sh /nope | grep -q MISSING",
            hints=["`if [ -e \"$1\" ]; then echo EXISTS; else echo MISSING; fi`"],
            solution="printf '#!/bin/bash\\nif [ -e \"$1\" ]; then echo EXISTS; else echo MISSING; fi\\n' > ~/lab/check.sh && chmod +x ~/lab/check.sh",
        ),
        Task(
            id="m12-04", title="Циклы",
            brief="""  for i in 1 2 3; do echo $i; done
  for f in *.txt; do echo "$f"; done
  while read -r line; do echo "$line"; done < файл

Диапазон: `{1..5}` или `$(seq 1 5)`.

Задание: одной командой (циклом) создай файлы `~/lab/gen/report1.txt` ... `report5.txt`,
в каждом должна быть строка `report N`.""",
            setup=f"rm -rf {LAB}/gen; mkdir -p {LAB}/gen",
            check=f"[ \"$(ls {LAB}/gen | wc -l)\" -eq 5 ] && grep -q 'report 3' {LAB}/gen/report3.txt",
            hints=["`for i in {1..5}; do echo \"report $i\" > ~/lab/gen/report$i.txt; done`"],
            solution="for i in {1..5}; do echo \"report $i\" > ~/lab/gen/report$i.txt; done",
        ),
        Task(
            id="m12-05", title="Коды возврата",
            brief="""Каждая команда возвращает код: 0 — успех, не 0 — ошибка. Последний код — в `$?`.
`команда1 && команда2` — вторая выполнится только при успехе первой, `||` — только при неудаче.
`exit N` завершает скрипт с кодом N. В боевых скриптах в начало ставят `set -euo pipefail`.

Задание: напиши `~/lab/fail.sh`, который завершается с кодом 3.""",
            setup=f"rm -f {LAB}/fail.sh",
            check=f"bash {LAB}/fail.sh; [ $? -eq 3 ]",
            hints=["Содержимое: `#!/bin/bash` и `exit 3`", "Проверить: `bash ~/lab/fail.sh; echo $?`"],
            solution="printf '#!/bin/bash\\nexit 3\\n' > ~/lab/fail.sh",
        ),
        Task(
            id="m12-06", title="cron: задания по расписанию",
            brief="""`crontab -e` редактирует расписание, `crontab -l` показывает.
Формат: `минуты часы день месяц день_недели команда`. Пример: `*/5 * * * * /root/backup.sh` — каждые 5 минут.
`0 3 * * *` — каждый день в 3:00.

Задание: добавь в crontab пользователя root задание, которое каждую минуту запускает `/root/lab/sysinfo.sh`.""",
            setup="crontab -r 2>/dev/null; true",
            check="crontab -l 2>/dev/null | grep -q 'sysinfo.sh' && crontab -l | grep -qE '^\\*(/1)? '",
            hints=["`crontab -e` и строка: `* * * * * /root/lab/sysinfo.sh`",
                   "Быстрый вариант: `echo '* * * * * /root/lab/sysinfo.sh' | crontab -`"],
            solution="echo '* * * * * /root/lab/sysinfo.sh' | crontab -",
        ),
        Task(
            id="m12-07", title="Итог: скрипт резервного копирования",
            brief="""Собери всё вместе: переменные, подстановка команд, tar, коды возврата.

Задание: напиши `~/lab/backup.sh`, который архивирует каталог `/etc` в файл вида
`/root/lab/backups/etc-ГГГГ-ММ-ДД.tar.gz` (дата в имени, каталог `backups` создаётся скриптом),
и запусти его.""",
            setup=f"rm -rf {LAB}/backups {LAB}/backup.sh",
            check=f"ls {LAB}/backups/etc-$(date +%F).tar.gz >/dev/null 2>&1 && tar -tzf {LAB}/backups/etc-$(date +%F).tar.gz | head -1 | grep -q etc",
            hints=["Дата: `$(date +%F)` даёт 2026-07-28",
                   "`mkdir -p /root/lab/backups`",
                   "`tar -czf /root/lab/backups/etc-$(date +%F).tar.gz /etc`"],
            solution=("printf '#!/bin/bash\\nset -e\\nDIR=/root/lab/backups\\nmkdir -p \"$DIR\"\\n"
                      "tar -czf \"$DIR/etc-$(date +%%F).tar.gz\" /etc\\n' > ~/lab/backup.sh && bash ~/lab/backup.sh"),
        ),
    ],
)

MODULES = [m10, m11, m12]
