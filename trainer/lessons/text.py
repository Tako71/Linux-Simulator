from ..model import Module, Task

LAB = "/root/lab"

m04 = Module(
    id="m04", title="Поиск: find, grep, which", level="уверенный",
    tasks=[
        Task(
            id="m04-01", title="grep — поиск по содержимому",
            brief="""`grep` (Global Regular Expression Print) — ищет строки, содержащие шаблон.
Один из самых используемых инструментов при работе с логами и конфигами.

Основной синтаксис: `grep [ключи] шаблон файл`

Ключи:
  -i    регистронезависимый поиск (Error = error = ERROR)
  -v    инвертировать: показать строки БЕЗ шаблона
  -n    показать номера строк
  -c    только количество совпавших строк (count)
  -l    только имена файлов с совпадениями
  -r    рекурсивно по каталогу
  -E    расширенные регулярные выражения (egrep)
  -F    шаблон — буквальная строка, без regex (fgrep)
  -w    только целое слово (не подстрока)
  -A 3  показать 3 строки После совпадения (After)
  -B 3  показать 3 строки До совпадения (Before)
  -C 3  3 строки вокруг совпадения (Context)

Примеры:
  grep 'error' /var/log/syslog        # найти ошибки в логе
  grep -i 'warning' app.log           # без учёта регистра
  grep -v '#' /etc/ssh/sshd_config    # убрать комментарии
  grep -n 'root' /etc/passwd          # с номерами строк

Задание: найди в `/etc/passwd` все строки, где оболочка `/bin/bash`, и сохрани их в `~/lab/bash-users.txt`.""",
            check=f"test -s {LAB}/bash-users.txt && ! grep -q 'nologin' {LAB}/bash-users.txt && grep -q '/bin/bash' {LAB}/bash-users.txt",
            hints=["`grep '/bin/bash' /etc/passwd > ~/lab/bash-users.txt`"],
            solution="grep '/bin/bash' /etc/passwd > ~/lab/bash-users.txt",
        ),
        Task(
            id="m04-02", title="Рекурсивный grep",
            brief="""`grep -r` рекурсивно обходит каталог и ищет во всех файлах.
Незаменимо при поиске по исходному коду или конфигурациям.

  grep -r шаблон каталог           # рекурсивно, без регистра по имени файла
  grep -rn шаблон каталог          # с номерами строк
  grep -rl шаблон каталог          # только имена файлов
  grep -ri шаблон каталог          # без учёта регистра
  grep -r шаблон --include='*.py'  # только в .py файлах
  grep -r шаблон --exclude='*.log' # исключить .log файлы

Вывод по умолчанию: `имя_файла:номер_строки:содержимое_строки`

Практические применения:
  grep -rn 'TODO' ./src/            # найти все TODO в проекте
  grep -r 'password' /etc/          # искать пароли в конфигах
  grep -rl 'import os' /opt/app/    # файлы, использующие os

Для очень больших деревьев быстрее работает `ripgrep` (rg) или `ag`,
но grep есть везде, rg — нет.

Задание: в подготовленном каталоге `~/lab/logs` найди все строки со словом `ERROR`
(с именами файлов и номерами строк) и сохрани результат в `~/lab/errors.txt`.""",
            setup=(f"mkdir -p {LAB}/logs && printf 'INFO start\\nERROR disk full\\nINFO ok\\n' > {LAB}/logs/a.log && "
                   f"printf 'WARN slow\\nERROR timeout\\n' > {LAB}/logs/b.log; rm -f {LAB}/errors.txt"),
            check=f"grep -q 'disk full' {LAB}/errors.txt && grep -q 'timeout' {LAB}/errors.txt && grep -q 'b.log' {LAB}/errors.txt",
            hints=["`grep -rn ERROR ~/lab/logs > ~/lab/errors.txt`"],
            solution="grep -rn ERROR ~/lab/logs > ~/lab/errors.txt",
        ),
        Task(
            id="m04-03", title="find по имени",
            brief="""`find` — поиск файлов по любым критериям. Мощнее, чем кажется.

Синтаксис: `find ГДЕ [критерии] [действие]`

Критерии по имени:
  -name '*.conf'       точное совпадение (чувствительно к регистру)
  -iname '*.Conf'      без учёта регистра
  -name 'log_???.txt'  ? заменяет один символ

Критерии по типу:
  -type f    обычные файлы (file)
  -type d    каталоги (directory)
  -type l    символические ссылки (link)

Сочетание критериев:
  find /etc -type f -name '*.conf'    # только файлы .conf
  find . -type d -name 'tmp'          # только каталоги с именем tmp
  find / -type l -name 'python*'      # симлинки на python

Важно: шаблоны (`*.conf`) надо брать в кавычки, иначе shell раскрывает
их в текущем каталоге ДО передачи find, что приводит к ошибкам.

Задание: найди в `/etc` все файлы с расширением `.conf` и сохрани список в `~/lab/confs.txt`.""",
            check=f"test -s {LAB}/confs.txt && grep -q '\\.conf$' {LAB}/confs.txt",
            hints=["`find /etc -type f -name '*.conf' > ~/lab/confs.txt`", "Кавычки вокруг `*.conf` обязательны"],
            solution="find /etc -type f -name '*.conf' > ~/lab/confs.txt",
        ),
        Task(
            id="m04-04", title="find по размеру и времени",
            brief="""`find` умеет фильтровать по размеру и времени — это главный инструмент
когда «нет места на диске» или нужно найти старые/недавно изменённые файлы.

По размеру (`-size`):
  -size +10M    больше 10 мегабайт
  -size -1k     меньше 1 килобайта
  -size +100c   больше 100 байт (c = bytes)
  Единицы: c б), k (кило), M (мега), G (гига)

По времени изменения содержимого (`-mtime`, modify time):
  -mtime -7     изменён за последние 7 дней
  -mtime +30    не изменялся более 30 дней
  -mmin -60     изменён за последний час (minutes)
  -newer ref    новее чем файл ref

По времени доступа (`-atime`) и изменения метаданных (`-ctime`).

Практика — найти всё крупное:
  find / -type f -size +100M 2>/dev/null
  find /var -mtime -1 -type f         # что изменилось сегодня
  find /tmp -mtime +7 -delete         # удалить старше недели

`2>/dev/null` — подавить ошибки доступа к системным каталогам.

Задание: найди в `~/lab` файлы размером больше 100 килобайт и запиши их пути в `~/lab/big-files.txt`.""",
            setup=f"dd if=/dev/zero of={LAB}/huge.bin bs=1K count=300 2>/dev/null; rm -f {LAB}/big-files.txt",
            check=f"grep -q 'huge.bin' {LAB}/big-files.txt",
            hints=["`find ~/lab -type f -size +100k > ~/lab/big-files.txt`"],
            solution="find ~/lab -type f -size +100k > ~/lab/big-files.txt",
        ),
        Task(
            id="m04-05", title="find -exec: действие над найденным",
            brief="""`find` с `-exec` выполняет команду над каждым найденным файлом.
Это мощная комбинация: найти + сделать что-то.

Синтаксис:
  find ... -exec КОМАНДА {} \\;
  {}   подставляется имя найденного файла
  \\;   завершает блок команды (нужен escape от shell)

Варианты:
  -exec команда {} \\;      запускать для каждого файла отдельно
  -exec команда {} +        передать все файлы одним вызовом (эффективнее)
  -delete                   удалить найденные файлы (встроено в find)

Примеры:
  find . -name '*.tmp' -delete               # удалить все .tmp
  find . -name '*.sh' -exec chmod +x {} \\;  # дать +x всем скриптам
  find /old -type f -exec cp {} /backup/ \\; # скопировать найденные
  find . -size +1M -exec ls -lh {} \\;       # показать крупные файлы

Безопаснее для имён с пробелами:
  find . -print0 | xargs -0 rm    # \0 как разделитель

Задание: удали из `~/lab/tmpdir` все файлы с расширением `.tmp`, используя `find -exec` или `-delete`.""",
            setup=f"mkdir -p {LAB}/tmpdir && touch {LAB}/tmpdir/{{a,b,c}}.tmp {LAB}/tmpdir/keep.txt",
            check=f"test -f {LAB}/tmpdir/keep.txt && [ -z \"$(find {LAB}/tmpdir -name '*.tmp')\" ]",
            check_history=r"\bfind\b",
            hints=["`find ~/lab/tmpdir -name '*.tmp' -delete`", "или `find ~/lab/tmpdir -name '*.tmp' -exec rm {} \\;`"],
            solution="find ~/lab/tmpdir -name '*.tmp' -delete",
        ),
        Task(
            id="m04-06", title="Где лежит программа",
            brief="""Иногда нужно знать, какой именно файл выполняется при вводе команды,
или убедиться что нужная программа вообще установлена.

`which команда` — полный путь к исполняемому файлу в PATH:
  which python3       → /usr/bin/python3
  which ls            → /usr/bin/ls

`type команда` — что именно это (алиас, функция, встроенная, файл):
  type ls             → ls is aliased to `ls --color=auto'
  type cd             → cd is a shell builtin
  type grep           → grep is /usr/bin/grep

`whereis команда` — бинарник + man-страница + источники:
  whereis nginx       → nginx: /usr/sbin/nginx /usr/share/man/man8/nginx.8.gz

`command -v команда` — аналог which, POSIX-совместимый (для скриптов):
  command -v docker || echo "docker не установлен"

Зачем это нужно:
— Когда в системе несколько версий python/java/node.
— Когда команда не находится (нет в PATH).
— При отладке скриптов.

Задание: запиши полный путь к программе `grep` в файл `~/lab/where-grep.txt`.""",
            check=f"grep -q '/grep$' {LAB}/where-grep.txt",
            hints=["`which grep > ~/lab/where-grep.txt`"],
            solution="which grep > ~/lab/where-grep.txt",
        ),
    ],
)

m05 = Module(
    id="m05", title="Потоки, конвейеры и обработка текста", level="уверенный",
    tasks=[
        Task(
            id="m05-01", title="Конвейер |",
            brief="""Философия Unix: одна программа — одна задача, но программы можно соединять.
Конвейер `|` передаёт stdout одной программы в stdin следующей.

  A | B | C | D

Данные текут слева направо, программы работают параллельно.
Ни A ни B не знают друг о друге — только читают/пишут в поток.

Мощность в цепочках:
  cat /etc/passwd | grep '/bin/bash' | cut -d: -f1   # имена bash-пользователей
  ps aux | grep nginx | grep -v grep                  # найти nginx-процессы
  ls -lt | head -5                                    # 5 последних изменённых файлов
  history | sort | uniq -c | sort -rn | head -10      # топ команд из истории

Счётчики через конвейер:
  ls /etc | wc -l               # сколько файлов в /etc
  grep -r ERROR /var/log | wc -l # сколько ошибок

`pgrep`, `grep -c` и `wc -l` — разные способы считать.

Конвейер — это не просто удобство, это способ мышления: описать
обработку данных как цепочку преобразований.

Задание: посчитай, сколько файлов и каталогов в `/etc`, соединив `ls` и `wc`, и сохрани число в `~/lab/etc-count.txt`.""",
            check=f"[ \"$(cat {LAB}/etc-count.txt | tr -d ' ')\" = \"$(ls /etc | wc -l | tr -d ' ')\" ]",
            hints=["`ls /etc | wc -l > ~/lab/etc-count.txt`"],
            solution="ls /etc | wc -l > ~/lab/etc-count.txt",
        ),
        Task(
            id="m05-02", title="Потоки: stdout, stderr, >>",
            brief="""У каждого процесса три стандартных потока (file descriptors):
  0   stdin  — стандартный ввод (с клавиатуры или от предыдущей команды)
  1   stdout — стандартный вывод (обычный результат)
  2   stderr — стандартный вывод ошибок (сообщения об ошибках)

По умолчанию stdout и stderr идут в терминал, их можно перенаправить:

  команда > файл           stdout в файл (перезапись)
  команда >> файл          stdout в файл (дописать в конец)
  команда 2> файл          stderr в файл
  команда 2>> файл         stderr дописать в файл
  команда &> файл          stdout и stderr в файл
  команда > /dev/null      выбросить stdout (null — «чёрная дыра»)
  команда 2>/dev/null      подавить ошибки
  команда > out 2> err     stdout и stderr в разные файлы
  команда 2>&1             объединить stderr с stdout

Пример разделения:
  find / -name '*.conf' > found.txt 2>/dev/null
  # → файлы пишутся в found.txt, ошибки доступа отбрасываются

Задание: выполни `ls /etc /nosuchdir` так, чтобы обычный вывод попал в `~/lab/out.txt`,
а сообщение об ошибке — в `~/lab/err.txt`.""",
            setup=f"rm -f {LAB}/out.txt {LAB}/err.txt",
            check=f"test -s {LAB}/out.txt && grep -qi 'nosuchdir' {LAB}/err.txt && ! grep -qi 'No such' {LAB}/out.txt",
            hints=["`ls /etc /nosuchdir > ~/lab/out.txt 2> ~/lab/err.txt`"],
            solution="ls /etc /nosuchdir > ~/lab/out.txt 2> ~/lab/err.txt",
        ),
        Task(
            id="m05-03", title="sort и uniq",
            brief="""`sort` и `uniq` — классическая пара для анализа текстовых данных.

`sort` — сортировка строк:
  sort файл             # алфавитная сортировка
  sort -n файл          # числовая сортировка (1, 2, 10 а не 1, 10, 2)
  sort -r файл          # обратный порядок (reverse)
  sort -k2 файл         # сортировать по 2-му полю
  sort -k2 -t: файл     # разделитель полей — двоеточие
  sort -u файл          # удалить дубликаты (unique)
  sort -h файл          # по «человеческим» размерам (1K < 1M < 1G)

`uniq` — удаление/подсчёт повторяющихся соседних строк:
  uniq файл             # убрать соседние дубликаты
  uniq -c файл          # подсчитать: "  3 строка"
  uniq -d файл          # показать только дубликаты
  uniq -u файл          # показать только уникальные

ВАЖНО: `uniq` сравнивает только соседние строки! Поэтому перед `uniq -c`
всегда нужен `sort`:
  sort access.log | uniq -c | sort -rn   # подсчитать частоту строк

Стандартная цепочка для топа:
  awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

Задание: в файле `~/lab/access.log` первое поле — IP. Посчитай, сколько запросов с каждого IP,
и сохрани результат, отсортированный по убыванию, в `~/lab/top-ip.txt`.""",
            setup=(f"printf '10.0.0.1 GET /\\n10.0.0.2 GET /a\\n10.0.0.1 GET /b\\n"
                   f"10.0.0.3 GET /\\n10.0.0.1 GET /c\\n10.0.0.2 GET /d\\n' > {LAB}/access.log; rm -f {LAB}/top-ip.txt"),
            check=f"head -1 {LAB}/top-ip.txt | grep -q '10.0.0.1' && head -1 {LAB}/top-ip.txt | grep -q '3'",
            hints=["Поле вырезается через `awk '{print $1}'` или `cut -d' ' -f1`",
                   "`cut -d' ' -f1 access.log | sort | uniq -c | sort -rn > top-ip.txt`"],
            solution="cd ~/lab && cut -d' ' -f1 access.log | sort | uniq -c | sort -rn > top-ip.txt",
        ),
        Task(
            id="m05-04", title="cut, tr, tee",
            brief="""Три маленьких, но полезных инструмента для обработки текста.

`cut` — вырезать поля или символы:
  cut -d: -f1 /etc/passwd       # поле 1, разделитель :
  cut -d: -f1,3 /etc/passwd     # поля 1 и 3
  cut -c1-10 файл               # первые 10 символов каждой строки
  cut -d' ' -f2- файл           # всё с 2-го поля до конца

`tr` — замена/удаление отдельных символов (translate):
  tr 'a-z' 'A-Z'                # строчные → заглавные
  tr 'A-Z' 'a-z'                # заглавные → строчные
  tr -d '\\n'                    # удалить все переводы строк
  tr -s ' '                     # сжать несколько пробелов в один
  tr ',' '\\n'                   # заменить запятые на переводы строк

`tee` — разветвить поток: записать в файл И передать дальше:
  команда | tee лог.txt | grep ERROR
  # → полный вывод в лог, только ERROR в терминал
  команда | tee -a файл         # дописывать (-a как у >>)

Пример цепочки:
  cut -d: -f1 /etc/passwd | tr 'a-z' 'A-Z' | sort

Задание: получи список имён всех пользователей системы из `/etc/passwd`, переведи их в ВЕРХНИЙ регистр
и сохрани в `~/lab/USERS.txt`.""",
            check=f"grep -qx 'ROOT' {LAB}/USERS.txt && ! grep -q '[a-z]' {LAB}/USERS.txt",
            hints=["`cut -d: -f1 /etc/passwd | tr 'a-z' 'A-Z' > ~/lab/USERS.txt`"],
            solution="cut -d: -f1 /etc/passwd | tr 'a-z' 'A-Z' > ~/lab/USERS.txt",
        ),
        Task(
            id="m05-05", title="sed — потоковая замена",
            brief="""`sed` (stream editor) — редактирование текста в потоке или файле.
Не открывает файл «для редактирования», а обрабатывает строку за строкой.

Замена (`s` — substitute):
  sed 's/старое/новое/'       # первое вхождение в каждой строке
  sed 's/старое/новое/g'      # все вхождения (g = global)
  sed 's/старое/новое/2'      # только 2-е вхождение
  sed 's/старое/новое/gi'     # все + без учёта регистра

Редактировать файл на месте (`-i`):
  sed -i 's/localhost/prod.example.com/g' config.ini
  sed -i.bak 's/old/new/g' file    # с бэкапом в file.bak

Удаление строк:
  sed '/шаблон/d'             # удалить строки с шаблоном
  sed '/^#/d'                 # удалить строки-комментарии
  sed '/^$/d'                 # удалить пустые строки

Диапазоны строк:
  sed -n '5,10p'              # напечатать строки 5–10
  sed '1,5d'                  # удалить строки 1–5

Добавление строк:
  sed '1i#!/bin/bash'         # вставить строку перед 1-й
  sed '$a# конец'             # добавить в конец

Задание: в файле `~/lab/config.ini` замени все `localhost` на `example.com` прямо в файле.""",
            setup=f"printf 'host=localhost\\nbackup=localhost\\nport=8080\\n' > {LAB}/config.ini",
            check=f"! grep -q localhost {LAB}/config.ini && [ \"$(grep -c example.com {LAB}/config.ini)\" -eq 2 ]",
            hints=["`sed -i 's/localhost/example.com/g' ~/lab/config.ini`"],
            solution="sed -i 's/localhost/example.com/g' ~/lab/config.ini",
        ),
        Task(
            id="m05-06", title="awk — работа по полям",
            brief="""`awk` — мини-язык программирования для обработки табличных данных.
Построчно читает текст, разбивает на поля, выполняет программу.

Основа: `awk 'программа' файл`
Поля: `$1`, `$2`, ..., `$NF` (последнее), `$0` (вся строка)
Разделитель полей: пробел/таб по умолчанию, `-F:` для другого

Примеры:
  awk '{print $1}'               # напечатать 1-е поле
  awk '{print $1, $3}'           # 1-е и 3-е поле через пробел
  awk -F: '{print $1, $3}'       # разделитель :
  awk '{print NR, $0}'           # с номером строки

Условия:
  awk '$3 >= 1000 {print $1}'    # поле 3 >= 1000
  awk -F: '$3 < 10 {print $1}'  # UID < 10
  awk '/Error/ {print}'          # строки с Error (regex)
  awk '$2 == "GET" {print $1}'   # второе поле равно GET

Встроенные переменные:
  NR    номер текущей строки (Number of Records)
  NF    количество полей (Number of Fields)
  FS    разделитель полей (Field Separator)

Суммирование:
  awk '{sum += $2} END {print sum}' data.txt

BEGIN/END — блоки до и после обработки:
  awk 'BEGIN{print "Начало"} {print} END{print "Конец"}'

Задание: выпиши в `~/lab/system-users.txt` имена пользователей с UID меньше 10 (третье поле `/etc/passwd`).""",
            check=f"grep -qx 'root' {LAB}/system-users.txt && grep -qx 'daemon' {LAB}/system-users.txt && ! grep -q ':' {LAB}/system-users.txt",
            hints=["`awk -F: '$3 < 10 {print $1}' /etc/passwd > ~/lab/system-users.txt`"],
            solution="awk -F: '$3 < 10 {print $1}' /etc/passwd > ~/lab/system-users.txt",
        ),
        Task(
            id="m05-07", title="xargs",
            brief="""`xargs` превращает строки из stdin в аргументы командной строки.
Нужен потому, что не все команды принимают ввод через stdin — они
принимают только аргументы.

Синтаксис: `команда-источник | xargs команда-назначение`

Примеры:
  find . -name '*.log' | xargs rm          # удалить все найденные файлы
  cat urls.txt | xargs wget                # скачать все URL из файла
  echo "f1 f2 f3" | xargs touch           # создать 3 файла
  cat pids.txt | xargs kill                # завершить все процессы

Полезные ключи:
  -n 1          передавать по одному аргументу за раз
  -P 4          запускать 4 процесса параллельно
  -I {}         заменять {} на аргумент (как в find -exec)
  -0            использовать \\0 как разделитель (для имён с пробелами)

Безопасный вариант для имён с пробелами:
  find . -print0 | xargs -0 rm      # \\0 вместо пробела как разделитель

`-I {}` для нестандартного размещения аргумента:
  cat files.txt | xargs -I {} cp {} /backup/{}

`wc -l` с несколькими файлами считает строки каждого плюс итог:
  find . -name '*.log' | xargs wc -l

Задание: с помощью конвейера `find ... | xargs` посчитай суммарное число строк во всех `.log` файлах в `~/lab/logs`
и сохрани итог в `~/lab/loglines.txt`.""",
            check=f"grep -q 'total\\|[0-9]' {LAB}/loglines.txt && test -s {LAB}/loglines.txt",
            check_history=r"xargs",
            hints=["`find ~/lab/logs -name '*.log' | xargs wc -l > ~/lab/loglines.txt`"],
            solution="find ~/lab/logs -name '*.log' | xargs wc -l > ~/lab/loglines.txt",
        ),
    ],
)

MODULES = [m04, m05]