from ..model import Module, Task

LAB = "/root/lab"

m06 = Module(
    id="m06", title="Права доступа", level="администратор",
    tasks=[
        Task(
            id="m06-01", title="Читаем права",
            brief="""Каждый файл в Linux имеет три уровня доступа:
  u — user (владелец файла)
  g — group (группа файла)
  o — others (все остальные)

И три типа разрешений:
  r — read     чтение (открыть файл / вывести содержимое каталога)
  w — write    запись (изменить файл / создать/удалить файлы в каталоге)
  x — execute  выполнение (запустить файл / зайти в каталог через cd)

`ls -l` показывает права в виде строки, например: `-rwxr-xr--`
  -         тип: - файл, d каталог, l симлинк
  rwx       права владельца: чтение+запись+выполнение
  r-x       права группы: чтение+выполнение, без записи
  r--       права остальных: только чтение

Числовое представление: r=4, w=2, x=1, сложи для каждой тройки:
  rwx = 4+2+1 = 7
  r-x = 4+0+1 = 5
  r-- = 4+0+0 = 4
  --- = 0

  rwxr-xr-- = 754
  rw-r--r-- = 644 (обычный файл)
  rwxr-xr-x = 755 (скрипт или каталог)

`stat -c '%a %U %G' файл` — права числом, владелец, группа.

Задание: запиши числовые права файла `/etc/passwd` в `~/lab/passwd-perm.txt` (только число, например `644`).""",
            check=f"[ \"$(cat {LAB}/passwd-perm.txt 2>/dev/null | tr -d ' ')\" = \"$(stat -c '%a' /etc/passwd)\" ]",
            hints=["`stat -c '%a' /etc/passwd > ~/lab/passwd-perm.txt`"],
            solution="stat -c '%a' /etc/passwd > ~/lab/passwd-perm.txt",
        ),
        Task(
            id="m06-02", title="chmod числом",
            brief="""`chmod` (change mode) изменяет права доступа к файлу.

Числовой синтаксис: `chmod NNN файл`
Три цифры — владелец, группа, остальные. Каждая = сумма r(4)+w(2)+x(1).

Типичные значения и их смысл:
  600   rw-------   секретный файл (только владелец читает)
  644   rw-r--r--   обычный файл (все читают, только владелец пишет)
  700   rwx------   личный скрипт (только владелец)
  750   rwxr-x---   скрипт для группы (группа запускает, не пишет)
  755   rwxr-xr-x   публичный скрипт/каталог (все запускают)
  777   rwxrwxrwx   открыт всем полностью (опасно! почти никогда не нужно)

Права каталогов:
  r  — можно прочитать список файлов (ls)
  w  — можно создавать и удалять файлы внутри
  x  — можно войти (cd) и обращаться к файлам внутри
  (без x нет доступа даже если знаешь имена файлов)

  chmod 750 ~/lab/deploy.sh    # например

Рекурсивно:
  chmod -R 755 /var/www/html   # применить ко всем файлам в каталоге

Задание: выставь файлу `~/lab/deploy.sh` права `750`.""",
            setup=f"echo '#!/bin/bash\\necho hi' > {LAB}/deploy.sh; chmod 644 {LAB}/deploy.sh",
            check=f"[ \"$(stat -c '%a' {LAB}/deploy.sh)\" = '750' ]",
            hints=["`chmod 750 ~/lab/deploy.sh`"],
            solution="chmod 750 ~/lab/deploy.sh",
        ),
        Task(
            id="m06-03", title="chmod символами",
            brief="""Второй синтаксис chmod — символьный. Удобен когда нужно
добавить или убрать конкретное право, не зная текущих прав.

Формат: `chmod [кому][операция][что] файл`

Кому:
  u   владелец (user)
  g   группа (group)
  o   остальные (others)
  a   все (all = u+g+o)

Операция:
  +   добавить право
  -   убрать право
  =   установить точно такие права

Что:
  r   чтение
  w   запись
  x   выполнение

Примеры:
  chmod +x script.sh          # добавить x для всех (= a+x)
  chmod u+x script.sh         # добавить x только владельцу
  chmod go-rwx secret.txt     # убрать всё у группы и остальных
  chmod a+r public.html       # всем добавить чтение
  chmod u=rw,go=r file.txt    # задать права явно

Можно комбинировать:
  chmod u+x,go-w script.sh    # владельцу +x, группе и остальным -w

Числовой и символьный синтаксис взаимозаменяемы, используй тот,
который понятнее в конкретной ситуации.

Задание: закрой файл `~/lab/secret.txt` от всех, кроме владельца (должно получиться 600), символьным синтаксисом.""",
            setup=f"echo 'token=123' > {LAB}/secret.txt; chmod 644 {LAB}/secret.txt",
            check=f"[ \"$(stat -c '%a' {LAB}/secret.txt)\" = '600' ]",
            check_history=r"chmod\s+[ugoa]*[-+=]",
            hints=["`chmod go-rwx ~/lab/secret.txt`"],
            solution="chmod go-rwx ~/lab/secret.txt",
        ),
        Task(
            id="m06-04", title="Владелец и группа",
            brief="""Каждый файл принадлежит пользователю (owner) и группе (group).
Это определяет, кто относится к категории `u` и `g` при проверке прав.

`chown` (change owner) меняет владельца и/или группу:
  chown alice файл              # сменить владельца на alice
  chown alice:devs файл         # владелец alice, группа devs
  chown :devs файл              # сменить только группу
  chown -R alice:devs каталог   # рекурсивно для всего дерева

`chgrp` (change group) меняет только группу:
  chgrp www-data /var/www/html

Только root может менять владельца файла.
Пользователь может менять группу на одну из своих групп.

Типичный паттерн для веб-сервера:
  chown -R www-data:www-data /var/www/
  chmod -R 755 /var/www/
  chmod -R 644 /var/www/*.html

`id пользователь` — посмотреть UID, GID и группы пользователя.
`stat -c '%U:%G %a' файл` — владелец:группа и права числом.

Задание: сделай владельцем каталога `~/lab/www` пользователя `www-data` и группу `www-data`, рекурсивно.""",
            setup=f"mkdir -p {LAB}/www/html && touch {LAB}/www/html/index.html && chown -R root:root {LAB}/www",
            check=f"[ \"$(stat -c '%U:%G' {LAB}/www/html/index.html)\" = 'www-data:www-data' ]",
            hints=["`chown -R www-data:www-data ~/lab/www`"],
            solution="chown -R www-data:www-data ~/lab/www",
        ),
        Task(
            id="m06-05", title="umask — права по умолчанию",
            brief="""`umask` (user file-creation mask) задаёт, какие права УБИРАЮТСЯ
у новых файлов и каталогов при их создании.

Логика: права_по_умолчанию - umask = финальные_права

Файлы создаются с максимальными правами 666 (без x):
  666 - 022 = 644  → rw-r--r--  (стандартно)
  666 - 027 = 640  → rw-r-----
  666 - 077 = 600  → rw-------  (только владелец)

Каталоги создаются с максимальными правами 777:
  777 - 022 = 755  → rwxr-xr-x  (стандартно)
  777 - 077 = 700  → rwx------

Просмотр текущей umask:
  umask           # числом (например 0022)
  umask -S        # символьно (u=rwx,g=rx,o=rx)

Установка:
  umask 022       # стандартная (открыто для чтения)
  umask 027       # группа читает, остальные — ничего
  umask 077       # только владелец (максимально закрыто)

umask действует только в текущей shell-сессии и для дочерних процессов.
В bash настраивается в ~/.bashrc или /etc/profile.

Задание: установи `umask 077` и создай файл `~/lab/private.txt` — он должен получить права 600.""",
            setup=f"rm -f {LAB}/private.txt",
            check=f"[ \"$(stat -c '%a' {LAB}/private.txt 2>/dev/null)\" = '600' ]",
            check_history=r"umask\s+077",
            hints=["`umask 077` затем `touch ~/lab/private.txt`"],
            solution="umask 077; touch ~/lab/private.txt",
        ),
        Task(
            id="m06-06", title="Бит выполнения и запуск скрипта",
            brief="""Для запуска файла нужны два условия:
1. У файла должен быть бит `x` (execute) у нужного пользователя.
2. Первая строка должна содержать «шебанг» (`#!`) с интерпретатором.

Шебанг (shebang, hashbang): `#!/путь/к/интерпретатору`
  #!/bin/bash         bash-скрипт
  #!/usr/bin/python3  Python-скрипт
  #!/usr/bin/env node Node.js-скрипт

Без шебанга скрипт будет выполнен через текущий shell, что не всегда
предсказуемо. Всегда добавляй шебанг!

Добавить бит выполнения:
  chmod +x script.sh          # для всех (u+g+o)
  chmod u+x script.sh         # только для владельца

Запуск скрипта:
  ./script.sh                 # из текущего каталога (нужен ./)
  /full/path/script.sh        # по абсолютному пути
  bash script.sh              # явно через bash (x не нужен)

Почему `./` а не просто `script.sh`:
По соображениям безопасности текущий каталог не входит в PATH.
Без `./` система не найдёт скрипт в текущем каталоге.

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
            brief="""В Linux каждый процесс запускается от имени пользователя. Безопасность
строится на принципе минимальных прав: каждый пользователь/сервис
получает только то, что необходимо.

Информация о пользователях хранится в:
  /etc/passwd   имя:x:UID:GID:комментарий:домашний_каталог:оболочка
  /etc/shadow   хеши паролей (только root)
  /etc/group    группы и их состав

`useradd` — создать пользователя:
  useradd alice                    # минимально (без домашнего каталога!)
  useradd -m alice                 # с домашним каталогом /home/alice
  useradd -m -s /bin/bash alice    # + оболочка bash
  useradd -m -s /bin/bash -c "Alice Smith" alice   # + комментарий

`adduser` в Debian/Ubuntu — интерактивная обёртка над useradd:
  adduser alice     # задаёт пароль, копирует /etc/skel в домашний каталог

Проверить результат:
  id alice          # UID, GID, группы
  getent passwd alice   # строка из /etc/passwd
  ls -la /home/alice    # содержимое домашнего каталога

`/etc/skel` — шаблон домашнего каталога: при создании пользователя
файлы оттуда копируются в /home/alice.

Задание: создай пользователя `alice` с домашним каталогом `/home/alice` и оболочкой `/bin/bash`.""",
            setup="userdel -r alice 2>/dev/null; true",
            check="id alice >/dev/null 2>&1 && test -d /home/alice && [ \"$(getent passwd alice | cut -d: -f7)\" = '/bin/bash' ]",
            hints=["`useradd -m -s /bin/bash alice`", "Проверить: `id alice`"],
            solution="useradd -m -s /bin/bash alice",
        ),
        Task(
            id="m07-02", title="Пароль",
            brief="""Пароли никогда не хранятся в открытом виде — только их хеши в `/etc/shadow`.
Только root имеет доступ к `/etc/shadow`.

`passwd` — задать/сменить пароль:
  passwd alice              # задать пароль alice (интерактивно)
  passwd                    # сменить свой собственный пароль

Неинтерактивно в скриптах:
  echo 'alice:ПаРОль' | chpasswd    # сразу для одного пользователя
  chpasswd < users.txt               # из файла (формат: имя:пароль)

Управление состоянием пароля:
  passwd -l alice      # заблокировать учётку (lock)
  passwd -u alice      # разблокировать (unlock)
  passwd -e alice      # принудительно сменить при следующем входе
  passwd -S alice      # статус пароля
  chage -l alice       # срок действия пароля

Статус из passwd -S: P — пароль есть, L — заблокирован, NP — нет пароля.

Хеш в /etc/shadow начинается с `$id$`:
  $6$ = SHA-512 (современный, правильный)
  $1$ = MD5 (старый, уязвимый)
  ! или !! = нет пароля / заблокирован

Задание: задай пользователю `alice` любой пароль.""",
            check="getent shadow alice | cut -d: -f2 | grep -q '^\\$'",
            hints=["`passwd alice` и введи пароль дважды", "или `echo 'alice:SuperSecret1' | chpasswd`"],
            solution="echo 'alice:SuperSecret1' | chpasswd",
        ),
        Task(
            id="m07-03", title="Группы",
            brief="""Группы позволяют предоставлять доступ к ресурсам нескольким пользователям.
У каждого пользователя есть одна основная (primary) группа и
любое число дополнительных (supplementary).

Просмотр групп:
  groups alice           # группы пользователя alice
  id alice               # UID, primary GID и все группы
  getent group devs      # кто в группе devs

`groupadd` — создать группу:
  groupadd devs          # создать группу devs

`usermod -aG` — добавить пользователя в дополнительную группу:
  usermod -aG devs alice

КРИТИЧНО: ключ `-a` (append) обязателен!
  usermod -G devs alice    # ← ОПАСНО: затрёт все остальные группы
  usermod -aG devs alice   # ← правильно: добавит к существующим

`groupdel` — удалить группу:
  groupdel devs    # нельзя удалить primary group пользователя

Изменения вступают в силу при следующем входе.
Для немедленного применения: `newgrp devs` или перезайти.

Задание: создай группу `devs` и добавь в неё `alice`.""",
            setup="groupdel devs 2>/dev/null; true",
            check="getent group devs >/dev/null && id -nG alice | tr ' ' '\\n' | grep -qx devs",
            hints=["`groupadd devs`", "`usermod -aG devs alice`"],
            solution="groupadd devs && usermod -aG devs alice",
        ),
        Task(
            id="m07-04", title="Сервисный пользователь без входа",
            brief="""Каждый сервис (nginx, postgres, redis) должен работать от отдельного
системного пользователя. Это ограничивает ущерб при взломе.

Требования к сервисному пользователю:
  — Нет пароля (нельзя залогиниться через ssh или консоль)
  — Оболочка `/usr/sbin/nologin` или `/bin/false` (запрещает вход)
  — Нет домашнего каталога (или минимальный)
  — UID < 1000 (системные пользователи)

`useradd` с нужными ключами:
  useradd -r -s /usr/sbin/nologin svc-app
  -r    системный пользователь (UID < 1000, выбирается автоматически)
  -s    оболочка (shell)
  -M    не создавать домашний каталог

Для сервисов с данными:
  useradd -r -s /usr/sbin/nologin -d /var/lib/myapp -m myapp
  -d    домашний каталог
  -m    создать его

Проверить:
  id svc-app
  su - svc-app    # должно сказать «This account is currently not available»

Задание: создай системного пользователя `svc-app` с оболочкой `/usr/sbin/nologin`.""",
            setup="userdel -r svc-app 2>/dev/null; true",
            check="getent passwd svc-app | cut -d: -f7 | grep -q nologin && [ \"$(id -u svc-app)\" -lt 1000 ]",
            hints=["`useradd -r -s /usr/sbin/nologin svc-app`"],
            solution="useradd -r -s /usr/sbin/nologin svc-app",
        ),
        Task(
            id="m07-05", title="Разбираем /etc/passwd",
            brief="""Файл `/etc/passwd` — база данных пользователей. Читается всеми пользователями.
Паролей тут нет (они в `/etc/shadow`), `x` — заглушка.

Формат строки (7 полей через `:`):
  alice:x:1001:1001:Alice Smith:/home/alice:/bin/bash
  1     2 3    4    5            6           7

  1  имя пользователя
  2  пароль (x = в /etc/shadow)
  3  UID (User ID) — числовой идентификатор
  4  GID (Group ID) — основная группа
  5  GECOS — комментарий (полное имя, телефон и т.п.)
  6  домашний каталог
  7  оболочка (shell)

Системные пользователи имеют UID < 1000.
root всегда имеет UID=0 и GID=0.

Полезные команды для работы с пользователями:
  getent passwd alice           # строка из /etc/passwd
  id alice                      # UID, GID, группы
  id -u alice                   # только UID
  id -g alice                   # только primary GID
  id -G alice                   # все GID
  id -nG alice                  # имена всех групп

`cut` для разбора:
  cut -d: -f1 /etc/passwd           # список всех пользователей
  getent passwd alice | cut -d: -f3  # UID пользователя alice

Задание: запиши UID пользователя `alice` (только число) в `~/lab/alice-uid.txt`.""",
            check=f"[ \"$(cat {LAB}/alice-uid.txt 2>/dev/null | tr -d ' ')\" = \"$(id -u alice)\" ]",
            hints=["`id -u alice > ~/lab/alice-uid.txt`", "или `getent passwd alice | cut -d: -f3 > ...`"],
            solution="id -u alice > ~/lab/alice-uid.txt",
        ),
        Task(
            id="m07-06", title="sudo и повышение прав",
            brief="""`sudo` (superuser do) позволяет выполнить команду с правами другого пользователя.
Это безопаснее, чем работать постоянно от root.

Преимущества sudo перед работой от root:
  — Журналируется: все sudo-команды пишутся в лог
  — Минимальные права: делаем root только одно действие
  — Без sudo нет риска случайных деструктивных команд

Конфигурация:
  /etc/sudoers           основной файл (редактировать только через visudo!)
  /etc/sudoers.d/        директория с дополнительными файлами

В Ubuntu членство в группе `sudo` даёт полный доступ к sudo:
  usermod -aG sudo alice     # дать alice права sudo

visudo проверяет синтаксис перед сохранением — если ошибиться в sudoers
вручную, можно заблокировать доступ к sudo на сервере.

Тонкая настройка в sudoers:
  alice ALL=(ALL) ALL              # полный доступ
  alice ALL=(ALL) NOPASSWD: ALL   # без пароля
  alice ALL=(ALL) /usr/bin/apt    # только apt

`su` — сменить пользователя:
  su alice            # стать alice (без -)
  su - alice          # стать alice с его окружением (правильный вариант)
  su -                # стать root
  exit                # вернуться к предыдущему пользователю

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
            brief="""Каждая запущенная программа — это процесс с уникальным PID.
У процесса есть родитель (PPID), владелец, приоритет и потребляемые ресурсы.

`ps` — снимок процессов в текущий момент:
  ps aux                   # все процессы, BSD-стиль (без дефиса)
  ps -ef                   # все процессы, System V стиль
  ps aux --sort=-%mem      # сортировка по памяти (убывание)
  ps aux --sort=-%cpu      # по CPU
  ps -u alice              # только процессы пользователя alice

Колонки ps aux:
  USER   PID  %CPU %MEM   VSZ   RSS  TTY STAT START TIME COMMAND

  VSZ  — виртуальная память (включая shared libs)
  RSS  — реальная занятая память (Resident Set Size)
  STAT — состояние: S=спит, R=работает, Z=зомби, D=ожидает I/O

`top` — интерактивный монитор:
  Клавиши внутри top:
  q     выйти
  P     сортировать по CPU
  M     сортировать по памяти
  k     kill: ввести PID
  1     показать все CPU по отдельности

`htop` — улучшенная версия top (может быть не установлен).

Задание: сохрани полный список процессов в `~/lab/procs.txt` и загляни в `top`.""",
            check=f"grep -q 'USER' {LAB}/procs.txt && grep -q 'bash' {LAB}/procs.txt",
            check_history=r"\btop\b",
            hints=["`ps aux > ~/lab/procs.txt`", "`top`, выход — `q`"],
            solution="ps aux > ~/lab/procs.txt; top",
        ),
        Task(
            id="m08-02", title="Фоновые задачи",
            brief="""Процессы в shell могут быть:
  Foreground (передний план) — занимают терминал, ты ждёшь завершения.
  Background (фон) — работают параллельно, терминал свободен.

Управление задачами (job control):
  команда &       запустить сразу в фоне
  Ctrl+Z          приостановить текущий процесс (SIGTSTP)
  bg              продолжить приостановленный процесс в фоне
  fg              вернуть фоновый процесс на передний план
  fg %2           вернуть задачу номер 2
  jobs            список задач текущего shell

Пример сессии:
  sleep 100 &         # → [1] 12345  (номер задачи, PID)
  jobs                # → [1]+  Running   sleep 100 &
  fg %1               # вернуть на передний план
  Ctrl+Z              # приостановить
  bg                  # снова в фон

Важно: задачи привязаны к текущей shell-сессии. При закрытии терминала
они получают SIGHUP и завершаются. Для «вечного» фона используй
`nohup`, `tmux`, `screen` или systemd.

`pgrep`, `ps aux | grep` — найти PID по имени:
  pgrep sleep            # PID всех процессов sleep
  pgrep -af sleep        # PID и полная командная строка

Задание: запусти в фоне `sleep 900`.""",
            setup="pkill -f '^sleep 90[0]$' 2>/dev/null; true",
            check="pgrep -f '^sleep 90[0]$' >/dev/null",
            hints=["`sleep 900 &`", "Посмотреть: `jobs`"],
            solution="sleep 900 &",
        ),
        Task(
            id="m08-03", title="Находим и убиваем процесс",
            brief="""«Убить» процесс значит отправить ему сигнал. Сигнал — это уведомление
от ОС или другого процесса. Процесс может обработать сигнал или игнорировать.

Основные сигналы:
  SIGTERM (15)   вежливое завершение — процесс может очиститься и выйти
  SIGKILL (9)    принудительное уничтожение — ядро убивает немедленно
  SIGHUP (1)     перечитать конфигурацию (reload)
  SIGSTOP (19)   приостановить
  SIGCONT (18)   продолжить

Стратегия: сначала SIGTERM, если не помогает — SIGKILL:
  kill PID                 # отправить SIGTERM (по умолчанию)
  kill -9 PID              # SIGKILL (последнее средство)
  kill -TERM PID           # то же что kill PID

Найти процесс:
  pgrep -af шаблон         # PID и командная строка
  ps aux | grep шаблон     # подробнее

Убить по имени:
  pkill -f шаблон          # SIGTERM всем совпадающим
  pkill -9 -f шаблон       # SIGKILL всем совпадающим
  killall nginx            # все процессы с именем nginx

Узнать PID и убить одной командой:
  kill $(pgrep -f 'my-app')

SIGKILL нельзя перехватить или заблокировать, но процесс не успевает
закрыть файлы — возможна потеря данных. Используй только если SIGTERM
не сработал через 10–30 секунд.

Задание: найди и заверши подготовленный процесс `sleep 4242`.""",
            setup="pkill -f '^sleep 424[2]$' 2>/dev/null; setsid sleep 4242 </dev/null >/dev/null 2>&1 & sleep 0.3; true",
            check="! pgrep -f '^sleep 424[2]$' >/dev/null",
            hints=["`pgrep -af 'sleep 4242'` покажет PID", "`kill <PID>` или `pkill -f 'sleep 4242'`"],
            solution="pkill -f 'sleep 4242'",
        ),
        Task(
            id="m08-04", title="Приоритеты: nice",
            brief="""Когда процессов много и CPU один, ОС делит время между ними.
«Nice value» — приоритет процесса: чем ниже число, тем выше приоритет.

Диапазон: -20 (максимальный приоритет) до 19 (минимальный).

По умолчанию: 0.
Обычный пользователь может только понижать свой приоритет (увеличивать число).
Только root может повышать (устанавливать отрицательные значения).

`nice` — запустить с приоритетом:
  nice команда                   # nice=10 (по умолчанию)
  nice -n 10 команда             # nice=10 (явно)
  nice -n 19 команда             # минимальный приоритет
  nice -n -5 команда             # высокий (только root)

`renice` — изменить приоритет работающего процесса:
  renice -n 5 -p 1234            # изменить для PID 1234
  renice -n 10 -u alice          # изменить для всех процессов alice

Когда это нужно:
  nice -n 19 tar czf backup.tar.gz /data    # архивирование не мешает работе
  nice -n 19 rsync -av /src /dst             # синхронизация в фоне
  renice -n -5 -p $(pgrep nginx)            # повысить приоритет сервера

Посмотреть nice value:
  ps -o pid,ni,cmd -p PID
  top (колонка NI)

Задание: запусти в фоне `sleep 800` с приоритетом nice = 10.""",
            setup="pkill -f '^sleep 80[0]$' 2>/dev/null; true",
            check="ps -o ni= -p \"$(pgrep -f '^sleep 80[0]$' | head -1)\" 2>/dev/null | tr -d ' ' | grep -qx 10",
            hints=["`nice -n 10 sleep 800 &`", "Проверить: `ps -o pid,ni,cmd -p $(pgrep -f 'sleep 800')`"],
            solution="nice -n 10 sleep 800 &",
        ),
        Task(
            id="m08-05", title="Процесс, переживающий выход",
            brief="""При закрытии терминала (или разрыве SSH) shell посылает SIGHUP всем
дочерним процессам. Обычно это их убивает. Иногда нужно, чтобы процесс
продолжал работать после нашего выхода.

`nohup команда &` — игнорировать SIGHUP:
  nohup python3 server.py &
  — отсоединяет от терминала
  — stdout и stderr → nohup.out (если не перенаправлены)
  — процесс переживёт закрытие терминала

Другие варианты:
  setsid команда        запустить в новой сессии (без SIGHUP)
  disown %1             отцепить задачу от shell (уже запущенную)
  disown -h %1          disown но без удаления из jobs

Лучшие варианты на практике:
  tmux / screen — мультиплексор: сессия живёт независимо от терминала
  systemd unit — процесс как служба, с автозапуском и мониторингом

Запуск с перенаправлением (чтобы не создавать nohup.out):
  nohup python3 app.py > /var/log/app.log 2>&1 &

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
            brief="""`lsof` (list open files) — один из главных диагностических инструментов.
В Linux «всё есть файл»: обычные файлы, сокеты, пайпы, устройства —
всё это файловые дескрипторы, и lsof их показывает.

Основные случаи использования:

Кто держит конкретный файл:
  lsof /var/log/app.log

Что открыл процесс:
  lsof -p 1234            # все файлы процесса 1234
  lsof -p $(pgrep nginx)  # файлы nginx

Кто слушает порт:
  lsof -i :80             # процессы на порту 80
  lsof -i TCP:8080        # TCP-порт 8080
  lsof -i UDP:53          # UDP-порт 53

Удалённые, но открытые файлы (место не освобождается):
  lsof +L1                # файлы с нулём жёстких ссылок

Все сетевые соединения:
  lsof -i                 # все
  lsof -i -s TCP:LISTEN   # только слушающие

Вывод: COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
  FD: типы дескрипторов: cwd(текущий), txt(код), mem(маппинг), 0(stdin), 1(stdout)...

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
            brief="""В Ubuntu/Debian используется система пакетов APT.
Пакет — это архив с бинарниками, конфигами и метаданными (зависимости, версия).

Два уровня:
  apt — высокоуровневый, разрешает зависимости автоматически
  dpkg — низкоуровневый, устанавливает .deb файлы напрямую

`apt` — работа с пакетами:
  apt update              обновить локальный список пакетов с серверов
  apt upgrade             обновить установленные пакеты
  apt install -y пакет    установить пакет (-y — без вопросов)
  apt remove пакет        удалить (оставить конфиги)
  apt purge пакет         удалить вместе с конфигами
  apt autoremove          удалить ненужные зависимости
  apt search слово        поиск по описаниям пакетов
  apt show пакет          подробная информация о пакете
  apt list --installed    список установленных пакетов

Важно: `apt update` обновляет только СПИСОК пакетов (кеш),
а не сами программы. После этого `apt upgrade` устанавливает обновления.

Без `apt update` apt может не знать о новых версиях пакетов.

Источники пакетов прописаны в `/etc/apt/sources.list`
и файлах в `/etc/apt/sources.list.d/`.

Задание: установи пакет `cowsay`.""",
            needs="net",
            check="command -v cowsay >/dev/null || test -x /usr/games/cowsay",
            hints=["`apt update && apt install -y cowsay`", "Проверить: `/usr/games/cowsay привет`"],
            solution="apt update && apt install -y cowsay",
        ),
        Task(
            id="m09-02", title="Что внутри пакета",
            needs="net",
            brief="""`dpkg` — низкоуровневый менеджер пакетов Debian. Полезен для диагностики.

`dpkg -l` — список установленных пакетов:
  dpkg -l               # все пакеты
  dpkg -l 'nginx*'      # только nginx и связанные
  Статус: ii = установлен, rc = удалён, но конфиги остались

`dpkg -L пакет` — что установил пакет (какие файлы):
  dpkg -L openssh-server    # покажет /usr/sbin/sshd и т.д.

`dpkg -S /путь/к/файлу` — какому пакету принадлежит файл:
  dpkg -S /usr/bin/grep     # → grep: /usr/bin/grep
  dpkg -S $(which python3)  # какой пакет дал python3

`dpkg -s пакет` — статус и информация о пакете:
  dpkg -s nginx             # версия, зависимости, описание

`apt show пакет` — подробное описание (включая зависимости):
  apt show curl

Посмотреть содержимое .deb файла не устанавливая:
  dpkg -c package.deb    # список файлов
  dpkg -I package.deb    # метаданные

Задание: сохрани список файлов пакета `cowsay` в `~/lab/cowsay-files.txt`.""",
            check=f"grep -q '/usr' {LAB}/cowsay-files.txt",
            hints=["`dpkg -L cowsay > ~/lab/cowsay-files.txt`"],
            solution="dpkg -L cowsay > ~/lab/cowsay-files.txt",
        ),
        Task(
            id="m09-03", title="Место на диске",
            brief="""Заполненный диск — одна из самых частых причин инцидентов. Нужно уметь
быстро найти виновника.

`df` (disk free) — свободное место на файловых системах:
  df -h           # все смонтированные ФС, в человекочитаемом виде
  df -h /         # только корневая ФС
  df -i           # inode usage (заполнение таблицы inode)

Пример вывода:
  Filesystem  Size  Used Avail Use% Mounted on
  /dev/sda1   20G   15G  4.1G  79%  /

`du` (disk usage) — сколько занимает каталог:
  du -sh /var/log            # размер одного каталога
  du -sh /var/log/*          # размер каждого подкаталога
  du -sh * | sort -h         # отсортировать по размеру

Алгоритм поиска «где место»:
  1. df -h                         — на каком разделе кончается место
  2. du -xsh /*                    — что занимает больше на корне (-x: не выходить за ФС)
  3. du -xsh /var/*                — спускаемся вглубь
  4. du -xsh /var/log/*            — и дальше
  5. find /var -type f -size +100M — крупные файлы

`ncdu` — интерактивный навигатор использования диска (если установлен).

Задание: сохрани вывод `df -h` в `~/lab/df.txt` и размер каталога `/etc` в `~/lab/etc-size.txt`.""",
            check=f"grep -q '%' {LAB}/df.txt && grep -q '/etc' {LAB}/etc-size.txt",
            hints=["`df -h > ~/lab/df.txt`", "`du -sh /etc > ~/lab/etc-size.txt`"],
            solution="df -h > ~/lab/df.txt; du -sh /etc > ~/lab/etc-size.txt",
        ),
        Task(
            id="m09-04", title="Точки монтирования",
            brief="""В Linux нет «дисков» C:/, D:/. Все устройства монтируются в единое дерево.

Концепция:
  Блочное устройство (/dev/sda1) → монтируется → в точку монтирования (/home)
  После монтирования содержимое устройства доступно через /home/*

`mount` — смонтировать ФС:
  mount /dev/sdb1 /mnt/data     # монтировать устройство
  mount -o ro /dev/sdb1 /mnt    # только для чтения (read-only)
  mount --bind /src /dst        # bind mount (пересмонтировать)
  umount /mnt/data              # отмонтировать

Просмотр смонтированных ФС:
  mount                          # все монтирования (длинный вывод)
  findmnt                        # дерево монтирований (читабельно)
  findmnt /                      # только конкретная точка
  lsblk                          # блочные устройства и их монтирования

Постоянные монтирования — `/etc/fstab`:
  /dev/sda1  /       ext4  defaults  0 1
  /dev/sda2  /home   ext4  defaults  0 2
  UUID=...   /data   xfs   defaults  0 2
  # устройство  точка_монтирования  тип_ФС  опции  dump  pass

UUID вместо /dev/sda надёжнее: имена устройств могут меняться.
Узнать UUID: `blkid /dev/sda1`

Задание: сохрани строку монтирования корневой ФС `/` в файл `~/lab/rootmount.txt`.""",
            check=f"grep -q ' / ' {LAB}/rootmount.txt || grep -q '^/' {LAB}/rootmount.txt",
            hints=["`findmnt / > ~/lab/rootmount.txt`", "или `mount | grep ' / ' > ~/lab/rootmount.txt`"],
            solution="findmnt / > ~/lab/rootmount.txt",
        ),
        Task(
            id="m09-05", title="Архивы tar",
            brief="""`tar` (Tape ARchive) — создание и распаковка архивов. Несмотря на название
«лента», используется повсеместно для архивирования файлов.

`tar` сам не сжимает — он объединяет файлы. Сжатие — отдельный шаг:
  -z    gzip (.tar.gz = .tgz)
  -j    bzip2 (.tar.bz2)
  -J    xz (.tar.xz)

Создать архив: `c` (create)
  tar -czf архив.tar.gz каталог/       # создать сжатый архив
  tar -czf backup.tar.gz /etc /home    # несколько источников
  tar -cf архив.tar каталог/           # без сжатия (быстрее для сетевой передачи)

Посмотреть содержимое: `t` (list)
  tar -tzf архив.tar.gz                # список файлов
  tar -tf архив.tar                    # без сжатия

Распаковать: `x` (extract)
  tar -xzf архив.tar.gz                # в текущий каталог
  tar -xzf архив.tar.gz -C /dest/      # в указанный каталог
  tar -xzf архив.tar.gz file.txt       # только один файл из архива

Полезные ключи:
  -v    verbose: показывать имена файлов
  -p    сохранить права доступа (permissions)
  --exclude='*.log'   исключить файлы

Задание: заархивируй каталог `~/lab/project` в `~/lab/project.tar.gz`.""",
            setup=f"mkdir -p {LAB}/project/src && touch {LAB}/project/src/main.py; rm -f {LAB}/project.tar.gz",
            check=f"tar -tzf {LAB}/project.tar.gz 2>/dev/null | grep -q 'project/src'",
            hints=["`cd ~/lab && tar -czf project.tar.gz project`"],
            solution="cd ~/lab && tar -czf project.tar.gz project",
        ),
        Task(
            id="m09-06", title="Распаковка в нужное место",
            brief="""При распаковке важно куда распаковывается архив. Без указания места
tar распаковывает в текущий каталог, что может перезаписать файлы.

Ключ `-C каталог` (--directory) — указать место распаковки:
  tar -xzf backup.tar.gz -C /restore/        # в /restore
  tar -xzf backup.tar.gz -C /tmp/test/       # в /tmp/test

Каталог для распаковки должен существовать:
  mkdir -p /restore && tar -xzf backup.tar.gz -C /restore

Распаковать конкретный файл:
  tar -xzf archive.tar.gz -C /dest/ path/inside/archive/file.txt

Посмотреть что внутри перед распаковкой (хорошая практика):
  tar -tzf archive.tar.gz | head -20

Проверить целостность архива:
  tar -tzf archive.tar.gz > /dev/null && echo "OK" || echo "CORRUPT"

Работа с zip (не tar):
  unzip archive.zip -d /dest/    # распаковать zip
  zip -r archive.zip каталог/    # создать zip

Задание: распакуй `~/lab/project.tar.gz` в каталог `~/lab/restore` (каталог придётся создать).""",
            setup=f"rm -rf {LAB}/restore",
            check=f"test -f {LAB}/restore/project/src/main.py",
            hints=["`mkdir -p ~/lab/restore`", "`tar -xzf ~/lab/project.tar.gz -C ~/lab/restore`"],
            solution="mkdir -p ~/lab/restore && tar -xzf ~/lab/project.tar.gz -C ~/lab/restore",
        ),
    ],
)

MODULES = [m06, m07, m08, m09]