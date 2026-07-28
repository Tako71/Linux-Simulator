from ..model import Module, Task

LAB = "/root/lab"

m10 = Module(
    id="m10", title="Сеть", level="продвинутый",
    tasks=[
        Task(
            id="m10-01", title="Интерфейсы и адреса",
            brief="""Сетевой интерфейс — абстракция над физическим или виртуальным
сетевым адаптером. У каждого интерфейса есть имя и IP-адрес(а).

Типичные имена интерфейсов:
  lo          loopback (127.0.0.1 — всегда есть, это «сам с собой»)
  eth0/ens3   проводной Ethernet (старый/новый стиль имён)
  wlan0       Wi-Fi
  docker0     виртуальный мост Docker
  veth...     виртуальные интерфейсы контейнеров

Современная утилита: `ip` (из пакета iproute2):
  ip a                   # показать все интерфейсы и адреса (ip address)
  ip a show eth0         # только интерфейс eth0
  ip link                # только уровень L2 (mac-адреса, состояние)
  ip link set eth0 up    # поднять интерфейс

Устаревший инструмент (всё ещё встречается): `ifconfig`
  ifconfig               # показывает только активные интерфейсы
  ifconfig eth0          # конкретный интерфейс

Вывод `ip a`:
  2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
      inet 10.0.2.15/24 brd 10.0.2.255 scope global eth0
  ↑ имя    ↑ MAC-уровень              ↑ IP/маска

Задание: сохрани информацию об интерфейсах в `~/lab/ip-addr.txt`.""",
            check=f"grep -q 'inet ' {LAB}/ip-addr.txt && grep -q 'lo' {LAB}/ip-addr.txt",
            hints=["`ip a > ~/lab/ip-addr.txt`"],
            solution="ip a > ~/lab/ip-addr.txt",
        ),
        Task(
            id="m10-02", title="Маршруты и шлюз",
            brief="""Когда пакет уходит с сервера, ядро смотрит таблицу маршрутизации:
«куда отправить пакет с этим адресом назначения?»

Основные записи таблицы:
  Конкретная сеть: 10.0.0.0/24 via 10.0.0.1    — в эту сеть через этот шлюз
  Маршрут по умолчанию: default via 10.0.0.1   — всё остальное через этот шлюз

`ip route` — таблица маршрутизации:
  ip route               # полная таблица
  ip route show          # то же самое
  ip route get 8.8.8.8   # какой маршрут выберется для этого адреса

Строка default via ... — это шлюз по умолчанию (default gateway).
Без него сервер не может выйти в интернет.

Управление маршрутами:
  ip route add 192.168.1.0/24 via 10.0.0.1     # добавить маршрут
  ip route del 192.168.1.0/24                    # удалить маршрут
  ip route add default via 10.0.0.1              # добавить шлюз по умолчанию

Постоянные маршруты настраиваются через файлы конфигурации
(зависит от дистрибутива: /etc/network/interfaces, netplan, NetworkManager).

Устаревший инструмент: `route -n`

Задание: запиши таблицу маршрутизации в `~/lab/routes.txt`.""",
            check=f"grep -q 'default' {LAB}/routes.txt",
            hints=["`ip route > ~/lab/routes.txt`"],
            solution="ip route > ~/lab/routes.txt",
        ),
        Task(
            id="m10-03", title="Открытые порты: ss",
            brief="""`ss` (socket statistics) — показывает сокеты и порты. Замена устаревшего `netstat`.

Синтаксис ключей:
  -t    TCP сокеты
  -u    UDP сокеты
  -l    только слушающие (listening)
  -p    показать процесс (program)
  -n    числа вместо имён (не резолвить hostname и порты)
  -a    все сокеты (включая неслушающие)

Самая частая команда: `ss -tulpn`

Вывод:
  Netid  State   Recv-Q Send-Q  Local Address:Port    Peer Address:Port  Process
  tcp    LISTEN  0      128     0.0.0.0:22             0.0.0.0:*          users:(("sshd",pid=1234))

  0.0.0.0:22 — слушает на всех интерфейсах порт 22
  127.0.0.1:5432 — только на localhost (не доступен снаружи)
  :::80 — IPv6 (обычно слушает и IPv4 тоже)

Типичные сценарии:
  Сервис не отвечает — не запущен? Не тот порт?
    ss -tlnp | grep :8080
  Порт занят при старте сервиса:
    ss -tlnp | grep :80     # кто занял порт

Устаревший аналог: `netstat -tulpn` (пакет net-tools).

Задание: сохрани список слушающих сокетов в `~/lab/ports.txt`.""",
            check=f"test -s {LAB}/ports.txt && grep -qi 'state\\|LISTEN' {LAB}/ports.txt",
            check_history=r"\bss\b",
            hints=["`ss -tulpn > ~/lab/ports.txt`"],
            solution="ss -tulpn > ~/lab/ports.txt",
        ),
        Task(
            id="m10-04", title="Своё имя в /etc/hosts",
            brief="""`/etc/hosts` — локальная таблица DNS-резолвинга. Проверяется до обращения
к DNS-серверу. Один из первых файлов конфигурации в истории интернета.

Порядок резолвинга определён в `/etc/nsswitch.conf`:
  hosts: files dns     # сначала /etc/hosts, потом DNS
  hosts: dns files     # наоборот

Формат /etc/hosts:
  IP-адрес   имя_хоста   [псевдоним ...]
  127.0.0.1  localhost
  ::1        localhost   ip6-localhost
  10.0.0.5   db-server   db

Применения:
  — Блокировка рекламы (0.0.0.0 ads.example.com)
  — Переопределение DNS в разработке (127.0.0.1 myapp.local)
  — Быстрые псевдонимы для часто используемых серверов
  — В контейнерах для связи сервисов без DNS

Редактировать надо осторожно — ошибки могут сломать резолвинг.
После изменения проверить: `getent hosts имя` или `ping -c1 имя`.

`getent hosts имя` — запрос через nsswitch (учитывает /etc/hosts):
  getent hosts myserver    # → 10.10.10.50 myserver

Задание: добавь в `/etc/hosts` запись, чтобы имя `myserver` резолвилось в `10.10.10.50`.""",
            setup="sed -i '/myserver/d' /etc/hosts",
            check="getent hosts myserver | grep -q '10.10.10.50'",
            hints=["`echo '10.10.10.50 myserver' >> /etc/hosts`", "Проверить: `getent hosts myserver` или `ping -c1 myserver`"],
            solution="echo '10.10.10.50 myserver' >> /etc/hosts",
        ),
        Task(
            id="m10-05", title="DNS: dig",
            brief="""DNS (Domain Name System) — распределённая база данных, переводящая
имена (example.com) в IP-адреса и обратно.

Типы DNS-записей:
  A      IPv4-адрес для имени
  AAAA   IPv6-адрес
  MX     почтовые серверы
  CNAME  псевдоним (алиас)
  NS     серверы имён для домена
  TXT    текстовые данные (SPF, DKIM, верификация)
  PTR    обратный DNS (IP → имя)

`dig` — основной инструмент для DNS-запросов:
  dig example.com              # A-запись (полный вывод)
  dig +short example.com       # только ответ (IP)
  dig example.com MX           # MX-записи
  dig example.com ANY          # все типы записей
  dig @8.8.8.8 example.com     # спросить конкретный DNS-сервер

Обратный DNS (IP → имя):
  dig -x 93.184.216.34         # PTR-запись
  dig +short -x 8.8.8.8        # имя для Google DNS

`host` — более простой аналог:
  host example.com             # IP-адрес
  host 8.8.8.8                 # обратный DNS

Настройки резолвера в `/etc/resolv.conf`:
  nameserver 8.8.8.8    # DNS-сервер
  search example.com    # поиск без домена

Задание: получи A-запись для `example.com` и сохрани короткий ответ в `~/lab/dns.txt`.""",
            needs="net",
            check=f"grep -Eq '^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+' {LAB}/dns.txt",
            hints=["`dig +short example.com > ~/lab/dns.txt`"],
            solution="dig +short example.com > ~/lab/dns.txt",
        ),
        Task(
            id="m10-06", title="curl: HTTP из терминала",
            brief="""`curl` (Client URL) — делать HTTP/HTTPS-запросы из командной строки.
Поддерживает десятки протоколов, незаменим при работе с API.

Основные ключи:
  -o файл    сохранить ответ в файл (output)
  -O         сохранить с именем из URL
  -I         только заголовки (HEAD-запрос)
  -i         заголовки + тело
  -s         тихий режим, без прогресс-бара (silent)
  -S         показывать ошибки даже с -s
  -L         следовать редиректам (Location)
  -v         verbose: показывать запрос и ответ полностью
  -w         формат вывода после завершения
  -X POST    тип запроса
  -H 'Header: value'    добавить заголовок
  -d 'data'  тело POST-запроса

Примеры:
  curl https://api.example.com/users          # GET-запрос
  curl -s https://api.example.com | python3 -m json.tool  # красиво JSON
  curl -sI https://example.com               # только заголовки ответа
  curl -L https://short.url/redirect         # следовать редиректам
  curl -X POST -H 'Content-Type: application/json' \\
       -d '{"key":"value"}' https://api/endpoint   # POST JSON

Скачать файл:
  curl -O https://example.com/file.tar.gz    # сохранить с оригинальным именем
  curl -o myfile.zip https://example.com/f  # сохранить с другим именем

Статус-код ответа:
  curl -o /dev/null -s -w "%{http_code}" https://example.com

Задание: сохрани HTTP-заголовки ответа `http://example.com` в `~/lab/headers.txt`.""",
            needs="net",
            check=f"grep -qi 'HTTP/' {LAB}/headers.txt",
            hints=["`curl -sI http://example.com > ~/lab/headers.txt`"],
            solution="curl -sI http://example.com > ~/lab/headers.txt",
        ),
        Task(
            id="m10-07", title="Слушаем порт",
            brief="""`nc` (netcat) — «швейцарский нож» для TCP/UDP. Может создавать соединения
и слушать порты, что удобно для отладки сети.

Режим сервера (слушать):
  nc -l 8080               # слушать TCP-порт 8080
  nc -l -p 8080            # некоторые версии требуют -p
  nc -lu 8080              # UDP-порт

Режим клиента (подключиться):
  nc hostname 8080         # подключиться к хосту:порт
  nc -z hostname 8080      # проверить доступность порта (port scan)
  nc -zv hostname 8080     # то же + verbose

Тест достижимости порта:
  nc -zv db-server 5432    # доступен ли PostgreSQL
  nc -zv lb-server 443     # доступен ли HTTPS

Передача данных:
  nc -l 9999 > received.txt       # принять файл
  nc hostname 9999 < file.txt     # отправить файл

Почему фоновый режим (&):
  nc -l 8080 &    # занять порт и вернуть управление терминалу
                  # затем проверить ss -tlnp | grep 8080

Современная альтернатива: `socat` (мощнее, но сложнее).
Для проверки портов также: `telnet host port`, `curl -v telnet://host:port`

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
            brief="""systemd — система инициализации: запускает всё после загрузки ядра.
PID 1 — это systemd. Он управляет службами, монтированием, логами и многим другим.

Основная единица: «unit». Типы unit-ов:
  .service   служба (nginx, postgresql, ssh)
  .socket    сокет (активация по подключению)
  .timer     периодические задачи (аналог cron)
  .mount     монтирование ФС
  .target    группа unit-ов (аналог runlevel)

`systemctl` — основной инструмент управления:

Просмотр:
  systemctl status служба          # состояние конкретной службы
  systemctl list-units --type=service   # все активные службы
  systemctl list-units --type=service --all    # включая неактивные
  systemctl list-units --failed    # что упало
  systemctl is-active служба       # active / inactive
  systemctl is-enabled служба      # enabled / disabled

Вывод systemctl status:
  ● nginx.service - A high performance web server
       Loaded: loaded (/lib/systemd/system/nginx.service; enabled)
       Active: active (running) since ...
      Process: ...ExecStart=/usr/sbin/nginx ...
     Main PID: 1234 (nginx)

Задание: сохрани список служб в `~/lab/services.txt`.""",
            needs="systemd",
            check=f"grep -q '\\.service' {LAB}/services.txt",
            hints=["`systemctl list-units --type=service > ~/lab/services.txt`"],
            solution="systemctl list-units --type=service --all > ~/lab/services.txt",
        ),
        Task(
            id="m11-02", title="Запуск и автозагрузка",
            brief="""Два независимых состояния службы:

«Сейчас работает»:
  systemctl start служба     # запустить сейчас
  systemctl stop служба      # остановить сейчас
  systemctl restart служба   # перезапустить
  systemctl reload служба    # перечитать конфиг (без перезапуска, если служба поддерживает)
  systemctl status служба    # текущее состояние

«Запускать при загрузке»:
  systemctl enable служба    # включить автозапуск
  systemctl disable служба   # выключить автозапуск
  systemctl is-enabled служба # проверить: enabled/disabled/static

КЛЮЧЕВОЕ РАЗЛИЧИЕ:
  start без enable → работает сейчас, не запустится после перезагрузки
  enable без start → запустится при следующей загрузке, сейчас не работает

Комбинация для «сделать всё сразу»:
  systemctl enable --now служба    # включить автозапуск И запустить
  systemctl disable --now служба   # выключить автозапуск И остановить

Распространённые службы:
  ssh / sshd       SSH-сервер
  cron             планировщик задач
  nginx            веб-сервер
  postgresql       БД

Задание: запусти службу `cron` и включи её автозагрузку.""",
            needs="systemd",
            setup="systemctl disable --now cron 2>/dev/null; true",
            check="systemctl is-active cron | grep -q '^active' && systemctl is-enabled cron | grep -q 'enabled'",
            hints=["`systemctl enable --now cron`", "Проверить: `systemctl status cron`"],
            solution="systemctl enable --now cron",
        ),
        Task(
            id="m11-03", title="Логи: journalctl",
            brief="""`journalctl` — чтение журнала systemd (journald). Собирает логи всей системы
в бинарном формате с метаданными: время, приоритет, юнит, PID и др.

Основные варианты:
  journalctl                    # весь журнал (с начала)
  journalctl -n 50              # последние 50 строк
  journalctl -f                 # следить в реальном времени (follow)
  journalctl -e                 # перейти в конец
  journalctl --no-pager         # не листать, вывести всё

Фильтрация:
  journalctl -u nginx           # только служба nginx
  journalctl -u nginx -u ssh    # несколько служб
  journalctl -p err             # только ошибки (err, warning, info, debug)
  journalctl -p 0..3            # critical и выше
  journalctl --since '10 min ago'          # за последние 10 минут
  journalctl --since '2026-07-28 10:00'   # с определённого времени
  journalctl --since yesterday             # с вчера

Формат вывода:
  journalctl -o json            # JSON (для парсинга)
  journalctl -o short-precise   # с точным временем (миллисекунды)

Размер журнала:
  journalctl --disk-usage       # сколько занимает
  journalctl --vacuum-size=500M # оставить только 500 МБ

Задание: сохрани последние 50 строк системного журнала в `~/lab/journal.txt`.""",
            needs="systemd",
            check=f"test -s {LAB}/journal.txt",
            check_history=r"journalctl",
            hints=["`journalctl -n 50 --no-pager > ~/lab/journal.txt`"],
            solution="journalctl -n 50 --no-pager > ~/lab/journal.txt",
        ),
        Task(
            id="m11-04", title="Свой unit-файл",
            brief="""Любой скрипт или программу можно запустить как systemd-службу.
Unit-файл — это INI-файл с тремя секциями:

[Unit] — описание и зависимости:
  Description=   описание
  After=network.target   запускать после получения сети
  Requires=      обязательная зависимость

[Service] — как запускать:
  ExecStart=     команда запуска (абсолютный путь!)
  ExecStop=      команда остановки (необязательно)
  Restart=       когда перезапускать: always / on-failure / no
  RestartSec=5   пауза перед перезапуском
  User=          от какого пользователя запускать
  WorkingDirectory= рабочий каталог

[Install] — для enable/disable:
  WantedBy=multi-user.target   запускать в обычном режиме работы

После создания или изменения unit-файла:
  systemctl daemon-reload       # ОБЯЗАТЕЛЬНО перечитать файлы
  systemctl enable --now имя   # включить и запустить

Где хранить unit-файлы:
  /etc/systemd/system/          ТВОИ файлы (приоритет над системными)
  /usr/lib/systemd/system/      файлы пакетов (не редактировать!)
  /etc/systemd/system/имя.d/    переопределение отдельных параметров

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
            brief="""Когда служба не поднимается, есть стандартный алгоритм диагностики.

Шаг 1: `systemctl status имя`
  — Показывает последние строки лога и причину падения
  — Смотри на строку «Active:» и код ошибки

Шаг 2: `journalctl -u имя -n 50 --no-pager`
  — Подробные логи службы
  — Ищи ERROR, Failed, Permission denied

Шаг 3: `systemctl cat имя`
  — Показывает содержимое unit-файла как его видит systemd
  — Проверь ExecStart: файл существует? Есть бит +x?

Шаг 4: исправить и применить:
  nano /etc/systemd/system/имя.service
  systemctl daemon-reload            # ОБЯЗАТЕЛЬНО после изменений
  systemctl restart имя

Типичные ошибки:
  ExecStart: путь не существует или нет +x
  Permission denied: нет прав на файл
  Start request repeated: служба падает и перезапускается

Управление запущенной службой:
  systemctl restart имя    # stop + start
  systemctl reload имя     # SIGHUP (конфиг без рестарта)
  systemctl kill имя       # SIGTERM всем процессам службы

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
            brief="""Bash-скрипт — это файл с командами, которые выполняются последовательно.
Мощь скриптов — в автоматизации повторяющихся задач.

Обязательная первая строка (шебанг):
  #!/bin/bash         явно bash
  #!/usr/bin/env bash ищет bash в PATH (переносимее)

Позиционные параметры (аргументы):
  $0   имя скрипта
  $1   первый аргумент
  $2   второй аргумент
  $@   все аргументы как отдельные элементы
  $*   все аргументы как одна строка
  $#   количество аргументов

Пример скрипта:
  #!/bin/bash
  echo "Скрипт: $0"
  echo "Первый аргумент: $1"
  echo "Всего аргументов: $#"

Запуск с аргументами:
  ./script.sh arg1 arg2 arg3

Кавычки важны! Без них пробелы в аргументах ломают скрипт:
  echo "Привет, $1!"    # правильно: аргумент как одно слово
  echo Привет, $1!      # может сломаться если в $1 есть пробелы

Задание: напиши `~/lab/greet.sh`, который на `./greet.sh Мир` печатает `Привет, Мир!`.""",
            setup=f"rm -f {LAB}/greet.sh",
            check=f"test -x {LAB}/greet.sh && bash {LAB}/greet.sh Мир | grep -qi 'привет' && bash {LAB}/greet.sh Мир | grep -q 'Мир'",
            hints=["Внутри: `echo \"Привет, $1!\"`", "Не забудь `chmod +x`"],
            solution="printf '#!/bin/bash\\necho \"Привет, $1!\"\\n' > ~/lab/greet.sh && chmod +x ~/lab/greet.sh",
        ),
        Task(
            id="m12-02", title="Переменные и подстановка команд",
            brief="""Переменные в bash:
  NAME=значение     присвоить (без пробелов вокруг =!)
  $NAME             использовать значение
  ${NAME}           использовать (рекомендуется для ясности)
  unset NAME        удалить переменную
  readonly NAME     сделать неизменяемой

Типичные ошибки:
  NAME = value   ← ОШИБКА: пробелы вокруг = недопустимы
  $NAME=value    ← ОШИБКА: нельзя присваивать через $

Подстановка команд — вставить вывод команды в переменную:
  DATE=$(date)          # современный синтаксис (предпочтительный)
  DATE=`date`           # старый синтаксис (работает, но устарел)
  FILES=$(ls ~/lab)     # список файлов в переменную
  HOST=$(hostname)      # имя хоста

Кавычки:
  Двойные "" — раскрывают переменные и подстановки:
    echo "Хост: $HOST"     → Хост: myserver
  Одинарные '' — всё буквально:
    echo 'Хост: $HOST'     → Хост: $HOST

Встроенные переменные:
  $HOME    домашний каталог
  $USER    текущий пользователь
  $PWD     текущий каталог (как pwd)
  $PATH    список каталогов для поиска команд
  $SHELL   текущий интерпретатор
  $$       PID текущего процесса

Задание: напиши `~/lab/sysinfo.sh`, который создаёт файл `~/lab/sysinfo.txt`
со строками вида `host=<имя хоста>` и `date=<текущая дата>`, и запусти его.""",
            setup=f"rm -f {LAB}/sysinfo.sh {LAB}/sysinfo.txt",
            check=f"grep -q \"^host=$(hostname)\" {LAB}/sysinfo.txt && grep -q '^date=' {LAB}/sysinfo.txt && test -s {LAB}/sysinfo.sh",
            hints=["`echo \"host=$(hostname)\" > ~/lab/sysinfo.txt`", "`echo \"date=$(date)\" >> ~/lab/sysinfo.txt`"],
            solution="printf '#!/bin/bash\\necho \"host=$(hostname)\" > /root/lab/sysinfo.txt\\necho \"date=$(date)\" >> /root/lab/sysinfo.txt\\n' > ~/lab/sysinfo.sh && bash ~/lab/sysinfo.sh",
        ),
        Task(
            id="m12-03", title="Условия",
            brief="""Условная конструкция в bash:

  if [ условие ]; then
      команды если истина
  elif [ другое условие ]; then
      команды
  else
      команды если ложь
  fi

`[` — это команда test. `[[` — расширенная версия (bash only).

Проверки файлов:
  -f файл    файл существует и является обычным файлом
  -d путь    путь существует и является каталогом
  -e путь    путь существует (любой тип)
  -r файл    файл читаем
  -w файл    файл записываем
  -x файл    файл исполняем
  -s файл    файл не пустой (непустой)
  -L файл    симлинк

Проверки строк:
  -z "$str"        строка пустая (zero length)
  -n "$str"        строка непустая
  "$a" = "$b"      строки равны
  "$a" != "$b"     строки не равны

Проверки чисел:
  $a -eq $b    равно (equal)
  $a -ne $b    не равно (not equal)
  $a -lt $b    меньше (less than)
  $a -gt $b    больше (greater than)
  $a -le $b    меньше или равно
  $a -ge $b    больше или равно

Задание: напиши `~/lab/check.sh`, который печатает `EXISTS`, если переданный путь существует, иначе `MISSING`.""",
            setup=f"rm -f {LAB}/check.sh",
            check=f"bash {LAB}/check.sh /etc | grep -q EXISTS && bash {LAB}/check.sh /nope | grep -q MISSING",
            hints=["`if [ -e \"$1\" ]; then echo EXISTS; else echo MISSING; fi`"],
            solution="printf '#!/bin/bash\\nif [ -e \"$1\" ]; then echo EXISTS; else echo MISSING; fi\\n' > ~/lab/check.sh && chmod +x ~/lab/check.sh",
        ),
        Task(
            id="m12-04", title="Циклы",
            brief="""Три основных цикла в bash:

`for` — перебор элементов:
  for i in 1 2 3; do echo $i; done
  for f in *.txt; do echo "$f"; done        # перебор файлов
  for i in {1..10}; do echo $i; done       # диапазон
  for i in $(seq 1 5); do echo $i; done    # через seq
  for i in $(cat list.txt); do ...; done   # строки из файла

C-стиль for:
  for ((i=0; i<10; i++)); do echo $i; done

`while` — пока условие истинно:
  while true; do                     # бесконечный цикл
      echo "работаю"
      sleep 5
  done
  while read -r line; do             # читать файл строку за строкой
      echo "$line"
  done < файл.txt

`until` — пока условие ложно (противоположность while):
  until ping -c1 server.com; do
      echo "жду доступности..."
      sleep 5
  done

Прерывание цикла:
  break     выйти из цикла
  continue  перейти к следующей итерации

Задание: одной командой (циклом) создай файлы `~/lab/gen/report1.txt` ... `report5.txt`,
в каждом должна быть строка `report N`.""",
            setup=f"rm -rf {LAB}/gen; mkdir -p {LAB}/gen",
            check=f"[ \"$(ls {LAB}/gen | wc -l)\" -eq 5 ] && grep -q 'report 3' {LAB}/gen/report3.txt",
            hints=["`for i in {1..5}; do echo \"report $i\" > ~/lab/gen/report$i.txt; done`"],
            solution="for i in {1..5}; do echo \"report $i\" > ~/lab/gen/report$i.txt; done",
        ),
        Task(
            id="m12-05", title="Коды возврата",
            brief="""Каждая команда возвращает код завершения (exit code):
  0     успех
  1     общая ошибка
  2     неверный синтаксис / аргументы
  127   команда не найдена
  128+N завершена сигналом N

`$?` — код последней команды:
  ls /tmp
  echo $?    # → 0 (успех)
  ls /nope
  echo $?    # → 2 (ошибка)

Условное выполнение:
  команда1 && команда2   # команда2 только если команда1 успешна (AND)
  команда1 || команда2   # команда2 только если команда1 упала (OR)
  команда1; команда2     # выполнить обе, независимо от результата

Примеры:
  mkdir /tmp/dir && cd /tmp/dir && touch file.txt    # цепочка
  cp important.txt /backup/ || echo "Ошибка бэкапа!"
  command -v docker || { echo "Нет docker"; exit 1; }

`exit N` — выйти из скрипта с кодом N:
  exit 0    # успех
  exit 1    # ошибка

Защита скрипта — в начале скрипта:
  set -e    # выйти при любой ошибке (как && для всего скрипта)
  set -u    # ошибка при использовании неинициализированных переменных
  set -o pipefail  # ошибка если упала команда в конвейере
  set -euo pipefail   # всё вместе (рекомендуется для prod-скриптов)

Задание: напиши `~/lab/fail.sh`, который завершается с кодом 3.""",
            setup=f"rm -f {LAB}/fail.sh",
            check=f"bash {LAB}/fail.sh; [ $? -eq 3 ]",
            hints=["Содержимое: `#!/bin/bash` и `exit 3`", "Проверить: `bash ~/lab/fail.sh; echo $?`"],
            solution="printf '#!/bin/bash\\nexit 3\\n' > ~/lab/fail.sh",
        ),
        Task(
            id="m12-06", title="cron: задания по расписанию",
            brief="""`cron` — демон для выполнения команд по расписанию.
Расписание каждого пользователя хранится в его `crontab`.

Формат строки crontab:
  минуты часы день_месяца месяц день_недели команда
  0-59   0-23  1-31       1-12  0-7(0=вс)

Специальные значения:
  *   любое значение
  */5  каждые 5 единиц (например */5 в минутах — каждые 5 минут)
  1,15 первое и пятнадцатое
  1-5  с первого по пятое

Примеры:
  * * * * * /path/script.sh          # каждую минуту
  */5 * * * * /path/script.sh        # каждые 5 минут
  0 3 * * * /path/backup.sh          # каждый день в 3:00
  0 9 * * 1 /path/report.sh          # каждый понедельник в 9:00
  30 8 1 * * /path/monthly.sh        # 1-го числа каждого месяца в 8:30

Управление:
  crontab -e    редактировать своё расписание
  crontab -l    показать текущее расписание
  crontab -r    удалить всё расписание (осторожно!)

Системный cron: /etc/crontab, /etc/cron.d/, /etc/cron.daily/

ВАЖНО: в cron урезанный PATH. Используй абсолютные пути!
Проверить что PATH в cron: добавить в начало crontab строку:
  PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

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

Хороший скрипт резервного копирования:
  — Начинается с set -euo pipefail (падать при ошибках)
  — Использует переменные для путей
  — Включает дату в имя архива
  — Создаёт каталог для бэкапов если нет
  — Проверяет результат

Формат даты для имён файлов:
  $(date +%F)     → 2026-07-28 (ISO 8601, сортируется хронологически)
  $(date +%Y%m%d) → 20260728
  $(date +%F_%H%M) → 2026-07-28_1430

tar для бэкапа:
  tar -czf "$BACKUP_DIR/etc-$(date +%F).tar.gz" /etc
  -c создать, -z gzip, -f имя файла

Ротация старых бэкапов:
  find /backup -name '*.tar.gz' -mtime +7 -delete   # удалять старше 7 дней

Структура скрипта:
  #!/bin/bash
  set -euo pipefail
  DIR=/root/lab/backups
  mkdir -p "$DIR"
  tar -czf "$DIR/etc-$(date +%F).tar.gz" /etc
  echo "Готово: $DIR/etc-$(date +%F).tar.gz"

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
