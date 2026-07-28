from ..model import Module, Task

LAB = "/root/lab"

m06 = Module(
    id="m06", title="Права доступа", level="администратор",
    tasks=[
        Task(
            id="m06-01", title="Читаем права",
            brief="""В выводе `ls -l` строка вида `-rwxr-xr--` это: тип, права владельца, группы, остальных.
r=4, w=2, x=1. То есть `rwxr-xr--` = 754.
`stat -c '%a %U %G' файл` покажет права числом, владельца и группу.

Задание: запиши числовые права файла `/etc/passwd` в `~/lab/passwd-perm.txt` (только число, например `644`).""",
            check=f"[ \"$(cat {LAB}/passwd-perm.txt 2>/dev/null | tr -d ' ')\" = \"$(stat -c '%a' /etc/passwd)\" ]",
            hints=["`stat -c '%a' /etc/passwd > ~/lab/passwd-perm.txt`"],
            solution="stat -c '%a' /etc/passwd > ~/lab/passwd-perm.txt",
        ),
        Task(
            id="m06-02", title="chmod числом",
            brief="""`chmod 750 файл` — владельцу всё, группе чтение+выполнение, остальным ничего.
Типовые значения: 644 (обычный файл), 755 (скрипт/каталог), 600 (секрет), 700 (личный каталог).

Задание: выставь файлу `~/lab/deploy.sh` права `750`.""",
            setup=f"echo '#!/bin/bash\\necho hi' > {LAB}/deploy.sh; chmod 644 {LAB}/deploy.sh",
            check=f"[ \"$(stat -c '%a' {LAB}/deploy.sh)\" = '750' ]",
            hints=["`chmod 750 ~/lab/deploy.sh`"],
            solution="chmod 750 ~/lab/deploy.sh",
        ),
        Task(
            id="m06-03", title="chmod символами",
            brief="""Второй синтаксис: `chmod u+x файл`, `chmod go-rwx файл`, `chmod a+r файл`.
u — владелец, g — группа, o — остальные, a — все.

Задание: закрой файл `~/lab/secret.txt` от всех, кроме владельца (должно получиться 600), символьным синтаксисом.""",
            setup=f"echo 'token=123' > {LAB}/secret.txt; chmod 644 {LAB}/secret.txt",
            check=f"[ \"$(stat -c '%a' {LAB}/secret.txt)\" = '600' ]",
            check_history=r"chmod\s+[ugoa]*[-+=]",
            hints=["`chmod go-rwx ~/lab/secret.txt`"],
            solution="chmod go-rwx ~/lab/secret.txt",
        ),
        Task(
            id="m06-04", title="Владелец и группа",
            brief="""`chown пользователь:группа файл` меняет владельца, `chgrp` — только группу.
Для каталогов рекурсивно: `chown -R`.

Задание: сделай владельцем каталога `~/lab/www` пользователя `www-data` и группу `www-data`, рекурсивно.""",
            setup=f"mkdir -p {LAB}/www/html && touch {LAB}/www/html/index.html && chown -R root:root {LAB}/www",
            check=f"[ \"$(stat -c '%U:%G' {LAB}/www/html/index.html)\" = 'www-data:www-data' ]",
            hints=["`chown -R www-data:www-data ~/lab/www`"],
            solution="chown -R www-data:www-data ~/lab/www",
        ),
        Task(
            id="m06-05", title="umask — права по умолчанию",
            brief="""`umask` задаёт, какие права вычитаются у новых файлов. При umask 022 новый файл получит 644.
При umask 077 — 600, то есть только для владельца.

Задание: установи `umask 077` и создай файл `~/lab/private.txt` — он должен получить права 600.""",
            setup=f"rm -f {LAB}/private.txt",
            check=f"[ \"$(stat -c '%a' {LAB}/private.txt 2>/dev/null)\" = '600' ]",
            check_history=r"umask\s+077",
            hints=["`umask 077` затем `touch ~/lab/private.txt`"],
            solution="umask 077; touch ~/lab/private.txt",
        ),
        Task(
            id="m06-06", title="Бит выполнения и запуск скрипта",
            brief="""Файл запускается, только если у него есть бит `x`. Первая строка скрипта `#!/bin/bash` — «шебанг».
Запуск из текущего каталога: `./script.sh` (просто `script.sh` не сработает — текущего каталога нет в PATH).

Задание: сделай `~/lab/hello.sh` исполняемым и запусти его так, чтобы он создал файл `~/lab/hello.out`.""",
            setup=(f"printf '#!/bin/bash\\necho \"привет из скрипта\" > /root/lab/hello.out\\n' > {LAB}/hello.sh; "
                   f"chmod 644 {LAB}/hello.sh; rm -f {LAB}/hello.out"),
            check=f"test -x {LAB}/hello.sh && grep -q 'привет' {LAB}/hello.out",
            hints=["`chmod +x ~/lab/hello.sh`", "`cd ~/lab && ./hello.sh`"],
            solution="chmod +x ~/lab/hello.sh && cd ~/lab && ./hello.sh",
        ),
    ],
)

m07 = Module(
    id="m07", title="Пользователи и группы", level="администратор",
    tasks=[
        Task(
            id="m07-01", title="Создаём пользователя",
            brief="""`useradd -m -s /bin/bash имя` создаёт пользователя с домашним каталогом и оболочкой bash.
(`adduser` в Debian/Ubuntu — интерактивная обёртка, тоже годится.)

Задание: создай пользователя `alice` с домашним каталогом `/home/alice` и оболочкой `/bin/bash`.""",
            setup="userdel -r alice 2>/dev/null; true",
            check="id alice >/dev/null 2>&1 && test -d /home/alice && [ \"$(getent passwd alice | cut -d: -f7)\" = '/bin/bash' ]",
            hints=["`useradd -m -s /bin/bash alice`", "Проверить: `id alice`"],
            solution="useradd -m -s /bin/bash alice",
        ),
        Task(
            id="m07-02", title="Пароль",
            brief="""`passwd alice` задаёт пароль интерактивно. Неинтерактивно (в скриптах): `echo 'alice:пароль' | chpasswd`.
Хеши паролей лежат в `/etc/shadow` (доступен только root), сами учётки — в `/etc/passwd`.

Задание: задай пользователю `alice` любой пароль.""",
            check="getent shadow alice | cut -d: -f2 | grep -q '^\\$'",
            hints=["`passwd alice` и введи пароль дважды", "или `echo 'alice:SuperSecret1' | chpasswd`"],
            solution="echo 'alice:SuperSecret1' | chpasswd",
        ),
        Task(
            id="m07-03", title="Группы",
            brief="""`groupadd имя` создаёт группу, `usermod -aG группа пользователь` добавляет в дополнительную группу
(`-a` обязателен, иначе остальные группы затрутся!). `id имя` и `groups имя` показывают членство.

Задание: создай группу `devs` и добавь в неё `alice`.""",
            setup="groupdel devs 2>/dev/null; true",
            check="getent group devs >/dev/null && id -nG alice | tr ' ' '\\n' | grep -qx devs",
            hints=["`groupadd devs`", "`usermod -aG devs alice`"],
            solution="groupadd devs && usermod -aG devs alice",
        ),
        Task(
            id="m07-04", title="Сервисный пользователь без входа",
            brief="""Для служб создают пользователя без домашнего каталога и без возможности логина:
оболочка `/usr/sbin/nologin`, ключ `-r` делает системную учётку (UID < 1000).

Задание: создай системного пользователя `svc-app` с оболочкой `/usr/sbin/nologin`.""",
            setup="userdel -r svc-app 2>/dev/null; true",
            check="getent passwd svc-app | cut -d: -f7 | grep -q nologin && [ \"$(id -u svc-app)\" -lt 1000 ]",
            hints=["`useradd -r -s /usr/sbin/nologin svc-app`"],
            solution="useradd -r -s /usr/sbin/nologin svc-app",
        ),
        Task(
            id="m07-05", title="Разбираем /etc/passwd",
            brief="""Строка `/etc/passwd`: `имя:x:UID:GID:комментарий:домашний_каталог:оболочка` (7 полей через двоеточие).

Задание: запиши UID пользователя `alice` (только число) в `~/lab/alice-uid.txt`.""",
            check=f"[ \"$(cat {LAB}/alice-uid.txt 2>/dev/null | tr -d ' ')\" = \"$(id -u alice)\" ]",
            hints=["`id -u alice > ~/lab/alice-uid.txt`", "или `getent passwd alice | cut -d: -f3 > ...`"],
            solution="id -u alice > ~/lab/alice-uid.txt",
        ),
        Task(
            id="m07-06", title="sudo и повышение прав",
            brief="""В Ubuntu право `sudo` даёт членство в группе `sudo`. Тонкая настройка — в `/etc/sudoers`
(редактировать только через `visudo`!) или файлами в `/etc/sudoers.d/`.
`su - alice` переключает сессию на другого пользователя.

Задание: дай `alice` права sudo и переключись в её сессию через `su - alice` (выход — `exit`).""",
            check="id -nG alice | tr ' ' '\\n' | grep -qx sudo",
            check_history=r"su\s+-\s*(l\s+)?alice",
            hints=["`usermod -aG sudo alice`", "`su - alice`, поработай, потом `exit`"],
            solution="usermod -aG sudo alice; su - alice",
        ),
    ],
)

m08 = Module(
    id="m08", title="Процессы и управление задачами", level="администратор",
    tasks=[
        Task(
            id="m08-01", title="Кто сейчас работает",
            brief="""`ps aux` — все процессы системы, `ps -ef` — то же в другом формате,
`ps aux --sort=-%mem | head` — топ по памяти. `top` — интерактивный монитор (выход `q`).

Задание: сохрани полный список процессов в `~/lab/procs.txt` и загляни в `top`.""",
            check=f"grep -q 'USER' {LAB}/procs.txt && grep -q 'bash' {LAB}/procs.txt",
            check_history=r"\btop\b",
            hints=["`ps aux > ~/lab/procs.txt`", "`top`, выход — `q`"],
            solution="ps aux > ~/lab/procs.txt; top",
        ),
        Task(
            id="m08-02", title="Фоновые задачи",
            brief="""`команда &` запускает в фоне, `jobs` показывает задачи текущей оболочки,
`fg %1` возвращает на передний план, `Ctrl+Z` приостанавливает, `bg` продолжает в фоне.

Задание: запусти в фоне `sleep 900`.""",
            setup="pkill -f '^sleep 90[0]$' 2>/dev/null; true",
            check="pgrep -f '^sleep 90[0]$' >/dev/null",
            hints=["`sleep 900 &`", "Посмотреть: `jobs`"],
            solution="sleep 900 &",
        ),
        Task(
            id="m08-03", title="Находим и убиваем процесс",
            brief="""`pgrep -af шаблон` находит процессы, `kill PID` шлёт SIGTERM (мягко),
`kill -9 PID` — SIGKILL (жёстко, последнее средство), `pkill -f шаблон` — по имени.

Задание: найди и заверши подготовленный процесс `sleep 4242`.""",
            setup="pkill -f '^sleep 424[2]$' 2>/dev/null; setsid sleep 4242 </dev/null >/dev/null 2>&1 & sleep 0.3; true",
            check="! pgrep -f '^sleep 424[2]$' >/dev/null",
            hints=["`pgrep -af 'sleep 4242'` покажет PID", "`kill <PID>` или `pkill -f 'sleep 4242'`"],
            solution="pkill -f 'sleep 4242'",
        ),
        Task(
            id="m08-04", title="Приоритеты: nice",
            brief="""Приоритет процесса (nice) от -20 (самый высокий) до 19 (самый низкий).
`nice -n 10 команда` запускает с пониженным приоритетом, `renice -n 5 -p PID` меняет у работающего.

Задание: запусти в фоне `sleep 800` с приоритетом nice = 10.""",
            setup="pkill -f '^sleep 80[0]$' 2>/dev/null; true",
            check="ps -o ni= -p \"$(pgrep -f '^sleep 80[0]$' | head -1)\" 2>/dev/null | tr -d ' ' | grep -qx 10",
            hints=["`nice -n 10 sleep 800 &`", "Проверить: `ps -o pid,ni,cmd -p $(pgrep -f 'sleep 800')`"],
            solution="nice -n 10 sleep 800 &",
        ),
        Task(
            id="m08-05", title="Процесс, переживающий выход",
            brief="""Если закрыть терминал, дочерние процессы получают SIGHUP и умирают.
`nohup команда &` отвязывает процесс и пишет вывод в `nohup.out`. Ещё варианты: `setsid`, `tmux`, `systemd`.

Задание: запусти через `nohup` фоновый цикл, который каждую секунду дописывает строку в `~/lab/heartbeat.log`.""",
            setup=f"pkill -f 'heartbea[t]' 2>/dev/null; rm -f {LAB}/heartbeat.log; true",
            check=f"test -s {LAB}/heartbeat.log && pgrep -f 'heartbea[t]\\.log' >/dev/null",
            check_history=r"nohup",
            hints=["`nohup bash -c 'while true; do date >> ~/lab/heartbeat.log; sleep 1; done' &`",
                   "Слово heartbeat должно быть в командной строке процесса — оно там есть за счёт пути к файлу"],
            solution="nohup bash -c 'while true; do date >> /root/lab/heartbeat.log; sleep 1; done' &",
        ),
        Task(
            id="m08-06", title="Кто держит файл: lsof",
            brief="""`lsof файл` — какие процессы открыли файл, `lsof -p PID` — что открыл процесс,
`lsof -i :80` — кто слушает порт. Незаменимо при «device is busy» и «port already in use».

Задание: сохрани в `~/lab/lsof-init.txt` список файлов, открытых процессом с PID 1.""",
            check=f"test -s {LAB}/lsof-init.txt && grep -qi 'command\\|/' {LAB}/lsof-init.txt",
            hints=["`lsof -p 1 > ~/lab/lsof-init.txt`"],
            solution="lsof -p 1 > ~/lab/lsof-init.txt",
        ),
    ],
)

m09 = Module(
    id="m09", title="Пакеты, диски, архивы", level="администратор",
    tasks=[
        Task(
            id="m09-01", title="Установка пакета",
            brief="""В Debian/Ubuntu: `apt update` обновляет списки пакетов, `apt install -y пакет` ставит,
`apt remove` удаляет, `apt search` ищет. Низкий уровень — `dpkg`.

Задание: установи пакет `cowsay`.""",
            needs="net",
            check="command -v cowsay >/dev/null || test -x /usr/games/cowsay",
            hints=["`apt update && apt install -y cowsay`", "Проверить: `/usr/games/cowsay привет`"],
            solution="apt update && apt install -y cowsay",
        ),
        Task(
            id="m09-02", title="Что внутри пакета",
            needs="net",
            brief="""`dpkg -l` — список установленных пакетов, `dpkg -L пакет` — какие файлы он положил,
`dpkg -S /путь/к/файлу` — какому пакету принадлежит файл, `apt show пакет` — описание.

Задание: сохрани список файлов пакета `cowsay` в `~/lab/cowsay-files.txt`.""",
            check=f"grep -q '/usr' {LAB}/cowsay-files.txt",
            hints=["`dpkg -L cowsay > ~/lab/cowsay-files.txt`"],
            solution="dpkg -L cowsay > ~/lab/cowsay-files.txt",
        ),
        Task(
            id="m09-03", title="Место на диске",
            brief="""`df -h` — сколько свободно на смонтированных ФС, `du -sh каталог` — сколько занимает каталог,
`du -sh * | sort -h` — что занимает больше всего. Первое, что делают при «нет места».

Задание: сохрани вывод `df -h` в `~/lab/df.txt` и размер каталога `/etc` в `~/lab/etc-size.txt`.""",
            check=f"grep -q '%' {LAB}/df.txt && grep -q '/etc' {LAB}/etc-size.txt",
            hints=["`df -h > ~/lab/df.txt`", "`du -sh /etc > ~/lab/etc-size.txt`"],
            solution="df -h > ~/lab/df.txt; du -sh /etc > ~/lab/etc-size.txt",
        ),
        Task(
            id="m09-04", title="Точки монтирования",
            brief="""`mount` без аргументов и `findmnt` показывают смонтированные ФС, `lsblk` — блочные устройства.
Постоянные монтирования описываются в `/etc/fstab`: устройство, точка, тип ФС, опции, dump, pass.

Задание: сохрани строку монтирования корневой ФС `/` в файл `~/lab/rootmount.txt`.""",
            check=f"grep -q ' / ' {LAB}/rootmount.txt || grep -q '^/' {LAB}/rootmount.txt",
            hints=["`findmnt / > ~/lab/rootmount.txt`", "или `mount | grep ' / ' > ~/lab/rootmount.txt`"],
            solution="findmnt / > ~/lab/rootmount.txt",
        ),
        Task(
            id="m09-05", title="Архивы tar",
            brief="""`tar -czf архив.tar.gz каталог` — создать сжатый архив (c=create, z=gzip, f=file),
`tar -xzf архив.tar.gz -C /куда` — распаковать, `tar -tzf архив.tar.gz` — посмотреть содержимое.

Задание: заархивируй каталог `~/lab/project` в `~/lab/project.tar.gz`.""",
            setup=f"mkdir -p {LAB}/project/src && touch {LAB}/project/src/main.py; rm -f {LAB}/project.tar.gz",
            check=f"tar -tzf {LAB}/project.tar.gz 2>/dev/null | grep -q 'project/src'",
            hints=["`cd ~/lab && tar -czf project.tar.gz project`"],
            solution="cd ~/lab && tar -czf project.tar.gz project",
        ),
        Task(
            id="m09-06", title="Распаковка в нужное место",
            brief="""Ключ `-C каталог` говорит tar, куда распаковывать.

Задание: распакуй `~/lab/project.tar.gz` в каталог `~/lab/restore` (каталог придётся создать).""",
            setup=f"rm -rf {LAB}/restore",
            check=f"test -f {LAB}/restore/project/src/main.py",
            hints=["`mkdir -p ~/lab/restore`", "`tar -xzf ~/lab/project.tar.gz -C ~/lab/restore`"],
            solution="mkdir -p ~/lab/restore && tar -xzf ~/lab/project.tar.gz -C ~/lab/restore",
        ),
    ],
)

MODULES = [m06, m07, m08, m09]
