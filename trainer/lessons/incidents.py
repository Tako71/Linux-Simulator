from ..model import Module, Task

LAB = "/root/lab"
INC = "/root/lab/incident"

m14 = Module(
    id="m14", title="Разбор инцидентов: диагностика и починка", level="продвинутый",
    tasks=[
        Task(
            id="m14-01", title="Инцидент: кончается место на диске",
            brief="""«Диск заполнен» — сервис перестаёт принимать новые данные, базы данных
падают, логи перестают писаться. Нужно действовать быстро и методично.

Алгоритм поиска «где место»:

Шаг 1: на каком разделе кончается место?
  df -h                        # все разделы с % использования
  df -h /var                   # конкретный раздел

Шаг 2: что занимает место на этом разделе?
  du -xsh /*                   # верхний уровень (-x: не выходить за ФС)
  du -xsh /var/*               # спускаемся вглубь
  du -xsh /var/log/*           # ещё глубже

Шаг 3: найти крупные файлы:
  find /var -type f -size +100M 2>/dev/null
  find / -xdev -type f -size +50M 2>/dev/null

Шаг 4: освободить место:
  rm файл                           # удалить файл
  > файл                            # обнулить файл (если процесс держит его)
  apt clean                         # очистить кеш apt
  journalctl --vacuum-size=500M     # урезать журнал systemd
  find /tmp -mtime +7 -delete       # старые временные файлы

Инструменты:
  ncdu /var           # интерактивный навигатор (если установлен)
  du -sh * | sort -h  # отсортировать по размеру

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
            brief="""Классическая ловушка: удалил большой файл командой `rm`, но `df` показывает
то же самое. Место не вернулось!

Причина: в Linux файл удаляется из каталога (убирается hard link),
но данные на диске существуют пока хотя бы один процесс держит открытый
файловый дескриптор на этот файл. Место освободится только когда процесс
закроет дескриптор (завершится или закроет файл).

Как найти виновника:

`lsof +L1` — файлы с нулём жёстких ссылок (удалены, но открыты):
  lsof +L1
  # показывает: процесс, PID, файл (deleted), размер

`lsof | grep deleted`:
  lsof | grep deleted

`fuser файл` — кто использует файл:
  fuser /var/log/app/file.log

Как освободить место не убивая процесс:
  > /proc/PID/fd/NUM    # обнулить файл через дескриптор
  # NUM — номер дескриптора из lsof

Когда всё же нужно убить процесс:
  kill PID          # SIGTERM (мягко, процесс может очиститься)
  kill -9 PID       # SIGKILL (жёстко, если не помогло)

После kill:
  df -h             # проверить что место вернулось

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
            brief="""«Address already in use» или «bind: address already in use» — стандартная
ошибка при попытке запустить сервис, когда порт уже занят другим процессом.

Инструменты для поиска виновника:

`ss` (предпочтительно):
  ss -tlnp | grep :80         # кто слушает порт 80
  ss -tlnp | grep :9000       # порт 9000
  # вывод: users:(("nginx",pid=1234,fd=6))

`lsof`:
  lsof -i :80                 # кто использует порт 80
  lsof -i TCP:8080            # TCP-порт 8080

`fuser`:
  fuser 9000/tcp              # показать PID
  fuser -v 9000/tcp           # verbose
  fuser -k 9000/tcp           # убить процесс занимающий порт

`netstat` (устарел, но встречается):
  netstat -tlnp | grep :80

Действия:
  1. Определить какой процесс занял порт
  2. Понять нормально ли это (может уже запущен нужный сервис?)
  3. Если лишний — убить: `kill PID` или `fuser -k порт/tcp`
  4. Запустить нужный сервис заново

Запись имени процесса:
  ss -tlnp | grep 9000         # в скобках: имя и PID
  ps -p PID -o comm=            # имя процесса по PID

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
            brief="""«Failed to start service» — служба не запускается. Это может быть что угодно:
неверный путь к бинарнику, нет бита +x, ошибка конфигурации, нет прав.

Системный алгоритм диагностики:

1. Краткий статус:
  systemctl status имя-службы
  — строка «Active:» — что произошло
  — последние строки лога сразу в выводе

2. Подробные логи:
  journalctl -u имя-службы -n 50 --no-pager
  — ищи: «Failed», «No such file», «Permission denied», «ExecStart»

3. Проверить unit-файл:
  systemctl cat имя-службы
  — что написано в ExecStart?
  — файл существует?
  — есть ли бит +x?

4. Исправить и применить:
  nano /etc/systemd/system/имя.service    # или через systemctl edit
  systemctl daemon-reload                 # ОБЯЗАТЕЛЬНО после правки
  systemctl restart имя-службы

5. Проверить результат:
  systemctl status имя-службы
  systemctl is-active имя-службы          # → active

Типичные причины:
  «No such file or directory»   неверный путь в ExecStart
  «Permission denied»           нет прав на файл или каталог
  «Start request repeated»      служба падает сразу и повторно стартует

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
            brief="""Веб-сервер отдаёт 403 Forbidden — самый частый источник проблем
после «неверного конфига». Почти всегда это права доступа.

Модель доступа к файлу по пути /srv/site/index.html:
  Нужен x на /              (как правило есть)
  Нужен x на /srv/          бит execute на каталоге
  Нужен x на /srv/site/     бит execute на каталоге
  Нужен r на /srv/site/index.html   бит read на файле

Даже если у файла есть r — без x на КАЖДОМ каталоге по пути
доступ будет закрыт.

`namei -l /путь/к/файлу` — показывает права каждого компонента пути:
  namei -l /srv/site/index.html
  Удобно: сразу видно на каком уровне не хватает прав

Воспроизвести проблему от имени сервиса:
  sudo -u www-data cat /srv/site/index.html
  sudo -u nginx ls /srv/site/
  # если выдаёт ошибку — права неправильные

Типичное исправление:
  chmod 755 /srv/site          # x для всех на каталог
  chmod 644 /srv/site/index.html    # r для всех на файл

Или правильнее через группу:
  chown -R root:www-data /srv/site   # группа www-data
  chmod -R 750 /srv/site/            # группе rwx, остальным ничего
  chmod -R 640 /srv/site/*.html      # группе rw

Второй вариант безопаснее: файлы недоступны «всем», только группе www-data.

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
            brief="""«Неверный пароль» — пользователь жалуется что пароль не принимается,
хотя уверен что вводит правильно. Причин может быть несколько.

Диагностика учётки:

`passwd -S имя` — статус пароля:
  alice P 2026-07-28 0 99999 7 -1 (Пароль задан)
  2-я колонка: P — пароль есть, L — заблокирован, NP — пароля нет

`chage -l имя` — срок действия пароля:
  Password expires: Jun 01, 2026    # истёк!
  Account expires: never

Оболочка пользователя:
  getent passwd alice               # 7-е поле — оболочка
  Если /usr/sbin/nologin → вход запрещён!

`usermod` для исправления:
  usermod -U alice              # разблокировать (unlock)
  usermod -L alice              # заблокировать (lock)
  usermod -s /bin/bash alice    # исправить оболочку
  usermod -e '' alice           # снять срок действия учётки
  passwd alice                  # задать новый пароль

Проверить блокировку:
  getent shadow alice           # хеш начинается с '!' если заблокирован
  passwd -S alice               # L = locked

Логи SSH-входов:
  grep alice /var/log/auth.log  # что происходило при попытках входа
  journalctl -u ssh -n 50       # логи SSH-демона

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
            brief="""«Скрипт руками работает, а из cron — нет» — одна из самых частых жалоб.
Причины типичны и повторяются.

Три главные причины:

1. Нет шебанга `#!/bin/bash` в первой строке:
  head -1 /path/script.sh     # должно быть #!/bin/bash
  Без шебанга cron запускает через /bin/sh, а не bash.
  Некоторые конструкции bash (массивы, [[, +=) не работают в sh.

2. Нет бита выполнения:
  ls -l /path/script.sh       # должен быть x
  chmod +x /path/script.sh    # добавить

3. Относительные пути и урезанный PATH:
  В cron PATH = /usr/bin:/bin (очень короткий!)
  Команды типа python3, node, pip — могут не найтись.
  Решение: использовать абсолютные пути:
    /usr/bin/python3 script.py      # вместо python3
    /usr/local/bin/node app.js      # вместо node

  Или задать PATH в начале crontab:
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

Дополнительная диагностика:
  bash -n script.sh            # проверить синтаксис без запуска
  bash -x script.sh            # запуск с трассировкой (печатает команды)
  env -i bash script.sh        # запуск в чистом окружении (как в cron)

Логи cron:
  grep CRON /var/log/syslog | tail -20
  journalctl -u cron -n 20

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
            brief="""Сайт лёг, в логе тысячи строк. Нужно быстро найти источник проблемы.

Стандартный формат логов nginx/Apache (Combined Log Format):
  IP - - [время] "МЕТОД путь протокол" КОД размер "referrer" "user-agent"

  203.0.113.1 - - [28/Jul/2026:13:05:00] "GET / HTTP/1.1" 200 1234

Коды ответа:
  200   OK (успех)
  301   перенаправление
  403   Forbidden (нет доступа)
  404   Not Found (не найдена страница)
  500   Internal Server Error (ошибка приложения)
  502   Bad Gateway (бэкенд недоступен)

Стандартная цепочка анализа:

Найти все ошибки 500:
  grep ' 500 ' access.log

Кто чаще всего получает 500 (топ атакующих IP):
  grep ' 500 ' access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head

Что за страницы вызывают 500:
  grep ' 500 ' access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head

Топ URL по числу запросов:
  awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -10

Запросы за период (grep по времени):
  grep '28/Jul/2026:14' access.log   # запросы в 14:00-14:59

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
            brief="""Ты зашёл на незнакомый сервер, которым «что-то не то». Нет документации,
нет истории. Что делать в первые 5 минут?

Быстрый чеклист первичной диагностики:

  uptime                      # нагрузка (load average) и аптайм
  whoami && id                # кто я, какие права
  df -h                       # место на дисках
  free -h                     # оперативная память (total/used/free/cache)
  ps aux --sort=-%mem | head  # кто ест память (топ 10)
  ps aux --sort=-%cpu | head  # кто ест CPU
  ss -tulpn                   # что слушает в сети, какие порты открыты
  systemctl --failed          # что упало (systemd)
  journalctl -p err -n 50     # свежие ошибки в системном журнале
  last                        # кто и когда заходил
  w                           # кто сейчас залогинен

Load average: три числа — нагрузка за 1, 5, 15 минут.
  Значение = числу CPU → нормально (CPU 100% загружен)
  Значение >> числу CPU → перегрузка

`free -h`:
  total   used  free  shared  buff/cache  available
  available — реально доступна для новых процессов (важнее чем free)

После чеклиста идёшь в логи того сервиса, который подозреваешь:
  journalctl -u имя-сервиса -n 100
  tail -100 /var/log/nginx/error.log

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
