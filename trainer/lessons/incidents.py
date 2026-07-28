from ..model import Module, Task

LAB = "/root/lab"
INC = "/root/lab/incident"

m14 = Module(
    id="m14", title="Разбор инцидентов: диагностика и починка", level="продвинутый",
    tasks=[
        Task(
            id="m14-01", title="Инцидент: кончается место на диске",
            brief="""Мониторинг кричит: раздел заполнен. Классический порядок действий:
`df -h` — где именно кончилось, `du -sh /* | sort -h` — спускаемся вниз по дереву,
`du -x` — не выходя за пределы одной ФС, `find / -size +100M` — крупные файлы.

Инцидент: в `/var` кто-то оставил огромный файл. Найди его, запиши полный путь
в `{INC}/bigfile.txt` и удали сам файл.""".replace("{INC}", INC),
            setup=(f"mkdir -p {INC} /var/log/oldapp && rm -f {INC}/bigfile.txt && "
                   f"dd if=/dev/zero of=/var/log/oldapp/dump.bin bs=1M count=120 2>/dev/null"),
            check=f"! test -e /var/log/oldapp/dump.bin && grep -q 'dump.bin' {INC}/bigfile.txt",
            hints=["`du -xh /var | sort -h | tail`",
                   "`find /var -type f -size +50M`",
                   "Путь в файл: `find /var -type f -size +50M > ~/lab/incident/bigfile.txt`, затем `rm` его"],
            solution=(f"find /var -type f -size +50M > {INC}/bigfile.txt && rm -f /var/log/oldapp/dump.bin"),
            fail_msg="Файл ещё на месте или путь не записан. Ищи через du/find, потом удаляй.",
        ),
        Task(
            id="m14-02", title="Инцидент: место не освободилось после удаления",
            brief="""Файл удалили, а `df` показывает то же самое. Причина: файл удалён из каталога,
но процесс держит открытым дескриптор — место вернётся только когда процесс закроет файл или умрёт.
Диагностика: `lsof +L1` (файлы с нулём ссылок) или `lsof | grep deleted`.

Инцидент: место занято удалённым файлом `/var/log/app/leak.log`. Найди процесс, который его держит,
и заверши этот процесс.""",
            setup=("pkill -f 'leak\\.lo[g]' 2>/dev/null; mkdir -p /var/log/app; "
                   "setsid bash -c 'exec 3>/var/log/app/leak.log; while true; do echo data >&3; sleep 2; done' "
                   "</dev/null >/dev/null 2>&1 & sleep 0.5; rm -f /var/log/app/leak.log; true"),
            check="! pgrep -f 'leak\\.lo[g]' >/dev/null",
            check_history=r"lsof|fuser",
            hints=["`lsof +L1` покажет открытые файлы с нулём ссылок",
                   "или `lsof | grep deleted`",
                   "Нашёл PID — `kill <PID>`"],
            solution="kill $(lsof -t /var/log/app/leak.log 2>/dev/null || pgrep -f 'leak\\.lo[g]')",
            fail_msg="Процесс, удерживающий удалённый файл, ещё жив.",
        ),
        Task(
            id="m14-03", title="Инцидент: порт уже занят",
            brief="""«Address already in use» — самая частая ошибка при запуске сервиса.
Ищем виновника: `ss -tlnp | grep :ПОРТ` или `lsof -i :ПОРТ` или `fuser -n tcp ПОРТ`.

Инцидент: порт 9000 занят посторонним процессом. Определи, что это за программа,
запиши её имя в `{INC}/port.txt` и освободи порт.""".replace("{INC}", INC),
            setup=(f"mkdir -p {INC} && rm -f {INC}/port.txt; pkill -f 'nc -l 900[0]' 2>/dev/null; "
                   "setsid nc -l 9000 </dev/null >/dev/null 2>&1 & sleep 0.5; true"),
            check=f"! ss -tln | grep -q ':9000' && grep -qi 'nc' {INC}/port.txt",
            hints=["`ss -tlnp | grep 9000` — в конце строки будет users:((\"имя\",pid=...))",
                   "Запиши имя программы: `echo nc > ~/lab/incident/port.txt`",
                   "Освободи порт: `kill <PID>` или `fuser -k -n tcp 9000`"],
            solution=f"ss -tlnp | grep 9000 > {INC}/port.txt; fuser -k -n tcp 9000",
            fail_msg="Порт 9000 всё ещё занят или имя процесса не записано.",
        ),
        Task(
            id="m14-04", title="Инцидент: служба не поднимается",
            brief="""Служба `broken-app` не стартует. Алгоритм:
1. `systemctl status broken-app` — краткая причина и последние строки лога.
2. `journalctl -u broken-app -n 50 --no-pager` — подробности.
3. Проверить сам unit: `systemctl cat broken-app`, существует ли ExecStart, есть ли на нём бит +x.
4. Починить, `systemctl daemon-reload`, `systemctl restart`.

Инцидент: почини службу так, чтобы `systemctl is-active broken-app` показывал `active`.""",
            needs="systemd",
            setup=("systemctl stop broken-app 2>/dev/null; mkdir -p /opt/app; "
                   "printf '#!/bin/bash\\nwhile true; do echo working; sleep 5; done\\n' > /opt/app/start.sh; "
                   "chmod +x /opt/app/start.sh; rm -f /opt/app/run.sh; "
                   "printf '[Unit]\\nDescription=Broken app\\n\\n[Service]\\nExecStart=/opt/app/run.sh\\n"
                   "Restart=no\\n\\n[Install]\\nWantedBy=multi-user.target\\n' > /etc/systemd/system/broken-app.service; "
                   "systemctl daemon-reload; systemctl start broken-app 2>/dev/null; true"),
            check="systemctl is-active broken-app | grep -q '^active'",
            check_history=r"journalctl|systemctl\s+status",
            hints=["Начни с `systemctl status broken-app` — что за ошибка?",
                   "`ls -l /opt/app/` — сравни с тем, что написано в ExecStart",
                   "Правь unit: `systemctl edit --full broken-app` или `nano /etc/systemd/system/broken-app.service`",
                   "После правки обязательно `systemctl daemon-reload && systemctl restart broken-app`"],
            solution=("systemctl status broken-app --no-pager; "
                      "journalctl -u broken-app -n 20 --no-pager; "
                      "sed -i 's#ExecStart=/opt/app/run.sh#ExecStart=/opt/app/start.sh#' "
                      "/etc/systemd/system/broken-app.service && systemctl daemon-reload && systemctl restart broken-app"),
            fail_msg="Служба ещё не в состоянии active. Смотри journalctl -u broken-app.",
        ),
        Task(
            id="m14-05", title="Инцидент: сервис не читает свои файлы",
            brief="""Веб-сервер отдаёт 403. Обычно виноваты права: чтобы прочитать файл, нужен бит `r` на нём
И бит `x` на КАЖДОМ каталоге по пути. Проверять удобно `namei -l /путь/к/файлу`
и `sudo -u пользователь cat /путь` — воспроизвести проблему от лица сервиса.

Инцидент: `www-data` не может прочитать `/srv/site/index.html`. Почини права, не делая файл доступным
на запись всем подряд.""",
            setup=("mkdir -p /srv/site && echo '<h1>hello</h1>' > /srv/site/index.html && "
                   "chown -R root:root /srv/site && chmod 700 /srv/site && chmod 600 /srv/site/index.html"),
            check=("sudo -u www-data cat /srv/site/index.html >/dev/null 2>&1 && "
                   "[ \"$(stat -c '%a' /srv/site/index.html)\" != '777' ]"),
            check_history=r"namei|sudo\s+-u|ls\s+-l|stat",
            hints=["Воспроизведи проблему: `sudo -u www-data cat /srv/site/index.html`",
                   "`namei -l /srv/site/index.html` покажет, на каком уровне не хватает прав",
                   "Каталогу нужен бит x для остальных: `chmod 755 /srv/site`, файлу — r: `chmod 644 /srv/site/index.html`",
                   "Альтернатива правильнее: `chown -R root:www-data /srv/site` + `chmod 750/640`"],
            solution=("namei -l /srv/site/index.html; "
                      "chmod 755 /srv/site && chmod 644 /srv/site/index.html"),
            fail_msg="www-data всё ещё не может прочитать файл (или права выставлены слишком широко).",
        ),
        Task(
            id="m14-06", title="Инцидент: пользователь не может войти",
            brief="""Пользователь жалуется, что пароль не принимается. Проверяем состояние учётки:
`passwd -S имя` — вторая колонка: `P` пароль установлен, `L` заблокирован, `NP` пароля нет.
Ещё смотрят `chage -l имя` (не истёк ли срок) и оболочку в `/etc/passwd` (не `nologin` ли).
Блокировка: `usermod -L`, снятие: `usermod -U`.

Инцидент: разберись, почему `alice` не может войти, и верни ей доступ.""",
            setup=("id alice >/dev/null 2>&1 || useradd -m -s /bin/bash alice; "
                   "echo 'alice:TempPass123' | chpasswd; usermod -L alice; "
                   "usermod -s /usr/sbin/nologin alice"),
            check=("passwd -S alice | awk '{print $2}' | grep -qx P && "
                   "getent passwd alice | cut -d: -f7 | grep -qv nologin"),
            check_history=r"passwd\s+-S|chage|getent|grep.*alice",
            hints=["`passwd -S alice` — что во второй колонке?",
                   "Разблокировать: `usermod -U alice`",
                   "Проверь ещё оболочку: `getent passwd alice` — там `nologin`, верни `/bin/bash` через `usermod -s /bin/bash alice`"],
            solution="passwd -S alice; usermod -U alice && usermod -s /bin/bash alice",
            fail_msg="Учётка всё ещё заблокирована или оболочка не позволяет войти.",
        ),
        Task(
            id="m14-07", title="Инцидент: скрипт из cron не запускается",
            brief="""Скрипт руками работает, а «сам» — нет. Типичные причины: нет бита `+x`, нет шебанга
(`#!/bin/bash` в первой строке), относительные пути внутри, и урезанный `PATH` в cron.
Проверить можно так: `head -1 script`, `ls -l script`, `bash -n script` (синтаксис).

Инцидент: почини `~/lab/run.sh` так, чтобы работала команда `./run.sh` и печатала `OK`.""",
            setup=(f"printf 'echo OK\\n' > {LAB}/run.sh && chmod 644 {LAB}/run.sh"),
            check=(f"test -x {LAB}/run.sh && head -1 {LAB}/run.sh | grep -q '^#!' && "
                   f"cd {LAB} && ./run.sh | grep -q OK"),
            hints=["`ls -l run.sh` — есть ли x?", "`head -1 run.sh` — есть ли шебанг?",
                   "Добавь первой строкой `#!/bin/bash` и сделай `chmod +x run.sh`"],
            solution=(f"sed -i '1i #!/bin/bash' {LAB}/run.sh && chmod +x {LAB}/run.sh"),
            fail_msg="Скрипт всё ещё не запускается как ./run.sh.",
        ),
        Task(
            id="m14-08", title="Инцидент: разбор лога веб-сервера",
            brief="""Сайт лёг, в логе тысячи строк. Формат: `IP - - [время] "МЕТОД путь" КОД размер`.
Стандартный приём — конвейер: отфильтровать нужные строки, вырезать поле, посчитать, отсортировать.

Инцидент: в `{INC}/access.log` найди IP-адрес, который чаще всех получал ответ 500,
и запиши только сам адрес в `{INC}/culprit.txt`.""".replace("{INC}", INC),
            setup=(f"mkdir -p {INC} && rm -f {INC}/culprit.txt && "
                   "ips=(198.51.100.4 203.0.113.77 192.0.2.9 198.51.100.23) && "
                   "codes=(200 200 200 301 404) && { "
                   "for i in $(seq 1 600); do "
                   "printf '%s - - [10/Oct/2026:13:%02d:00] \"GET /page%d HTTP/1.1\" %s 1234\\n' "
                   "\"${ips[i%4]}\" \"$((i%60))\" \"$((i%17))\" \"${codes[i%5]}\"; done; "
                   "for i in $(seq 1 140); do "
                   "printf '203.0.113.77 - - [10/Oct/2026:14:%02d:00] \"POST /api/pay HTTP/1.1\" 500 0\\n' "
                   "\"$((i%60))\"; done; "
                   "for i in $(seq 1 35); do "
                   "printf '192.0.2.9 - - [10/Oct/2026:14:%02d:00] \"POST /api/pay HTTP/1.1\" 500 0\\n' "
                   "\"$((i%60))\"; done; "
                   f"}} | shuf > {INC}/access.log"),
            check=f"grep -qx '203.0.113.77' {INC}/culprit.txt",
            hints=["Сначала отфильтруй: `grep ' 500 ' access.log`",
                   "Потом первое поле: `awk '{print $1}'`",
                   "Посчитай и отсортируй: `| sort | uniq -c | sort -rn | head -1`",
                   "Оставить только адрес: добавь в конец `| awk '{print $2}'`"],
            solution=(f"grep ' 500 ' {INC}/access.log | awk '{{print $1}}' | sort | uniq -c | sort -rn | "
                      f"head -1 | awk '{{print $2}}' > {INC}/culprit.txt"),
            fail_msg="В culprit.txt должен быть один IP-адрес и ничего кроме него.",
        ),
        Task(
            id="m14-09", title="Итоговый разбор: что вообще происходит с сервером",
            brief="""Ты зашёл на незнакомый сервер, которым «что-то не то». Быстрый чеклист:

  uptime                      # нагрузка и как давно работает
  df -h                       # место на дисках
  free -h                     # память
  ps aux --sort=-%mem | head  # кто ест память
  ss -tulpn                   # что слушает сеть
  systemctl --failed          # что упало
  journalctl -p err -n 50     # свежие ошибки

Задание: собери такой отчёт в файл `{INC}/report.txt` — он должен содержать вывод
как минимум `uptime`, `df -h`, `free -h` и списка процессов.""".replace("{INC}", INC),
            setup=f"mkdir -p {INC}; rm -f {INC}/report.txt",
            check=(f"test -s {INC}/report.txt && grep -q 'load average' {INC}/report.txt && "
                   f"grep -q 'Filesystem\\|Файл' {INC}/report.txt && grep -qi 'mem' {INC}/report.txt && "
                   f"grep -q 'USER\\|PID' {INC}/report.txt"),
            hints=["Дописывай через `>>`: `uptime >> ~/lab/incident/report.txt`",
                   "`df -h >> ...`, `free -h >> ...`, `ps aux --sort=-%mem | head >> ...`",
                   "Красивее — сделать из этого скрипт и запустить его один раз"],
            solution=(f"{{ uptime; df -h; free -h; ps aux --sort=-%mem | head; }} > {INC}/report.txt"),
            fail_msg="В отчёте не хватает какого-то раздела (uptime / df / free / список процессов).",
        ),
    ],
)

MODULES = [m14]
