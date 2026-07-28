from ..model import Module, Task

LAB = "/root/lab"

m04 = Module(
    id="m04", title="Поиск: find, grep, which", level="уверенный",
    tasks=[
        Task(
            id="m04-01", title="grep — поиск по содержимому",
            brief="""`grep шаблон файл` ищет строки. Ключи: `-i` — без учёта регистра, `-r` — рекурсивно по каталогу,
`-n` — с номерами строк, `-v` — инвертировать, `-c` — только количество.

Задание: найди в `/etc/passwd` все строки, где оболочка `/bin/bash`, и сохрани их в `~/lab/bash-users.txt`.""",
            check=f"test -s {LAB}/bash-users.txt && ! grep -q 'nologin' {LAB}/bash-users.txt && grep -q '/bin/bash' {LAB}/bash-users.txt",
            hints=["`grep '/bin/bash' /etc/passwd > ~/lab/bash-users.txt`"],
            solution="grep '/bin/bash' /etc/passwd > ~/lab/bash-users.txt",
        ),
        Task(
            id="m04-02", title="Рекурсивный grep",
            brief="""`grep -rn шаблон каталог` пройдёт по всем файлам внутри.

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
            brief="""`find ГДЕ -name 'ШАБЛОН'` ищет файлы по имени. Ещё: `-type f|d`, `-iname` (без регистра).

Задание: найди в `/etc` все файлы с расширением `.conf` и сохрани список в `~/lab/confs.txt`.""",
            check=f"test -s {LAB}/confs.txt && grep -q '\\.conf$' {LAB}/confs.txt",
            hints=["`find /etc -type f -name '*.conf' > ~/lab/confs.txt`", "Кавычки вокруг `*.conf` обязательны"],
            solution="find /etc -type f -name '*.conf' > ~/lab/confs.txt",
        ),
        Task(
            id="m04-04", title="find по размеру и времени",
            brief="""`-size +10M` — больше 10 мегабайт, `-mtime -7` — изменён за последние 7 дней,
`-mmin -60` — за последний час. Это основной инструмент, когда «кончилось место на диске».

Задание: найди в `~/lab` файлы размером больше 100 килобайт и запиши их пути в `~/lab/big-files.txt`.""",
            setup=f"dd if=/dev/zero of={LAB}/huge.bin bs=1K count=300 2>/dev/null; rm -f {LAB}/big-files.txt",
            check=f"grep -q 'huge.bin' {LAB}/big-files.txt",
            hints=["`find ~/lab -type f -size +100k > ~/lab/big-files.txt`"],
            solution="find ~/lab -type f -size +100k > ~/lab/big-files.txt",
        ),
        Task(
            id="m04-05", title="find -exec: действие над найденным",
            brief="""`find ... -exec КОМАНДА {} \\;` выполняет команду для каждого найденного файла.
`{}` подставляет имя файла, `\\;` завершает выражение.

Задание: удали из `~/lab/tmpdir` все файлы с расширением `.tmp`, используя `find -exec` или `-delete`.""",
            setup=f"mkdir -p {LAB}/tmpdir && touch {LAB}/tmpdir/{{a,b,c}}.tmp {LAB}/tmpdir/keep.txt",
            check=f"test -f {LAB}/tmpdir/keep.txt && [ -z \"$(find {LAB}/tmpdir -name '*.tmp')\" ]",
            check_history=r"\bfind\b",
            hints=["`find ~/lab/tmpdir -name '*.tmp' -delete`", "или `find ~/lab/tmpdir -name '*.tmp' -exec rm {} \\;`"],
            solution="find ~/lab/tmpdir -name '*.tmp' -delete",
        ),
        Task(
            id="m04-06", title="Где лежит программа",
            brief="""`which команда` — путь к исполняемому файлу, `type` — что это вообще (алиас, функция, встроенная команда),
`whereis` — бинарник + man-страница.

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
            brief="""Философия Unix: маленькие программы, соединённые конвейером. `A | B` отправляет вывод A на вход B.

Задание: посчитай, сколько файлов и каталогов в `/etc`, соединив `ls` и `wc`, и сохрани число в `~/lab/etc-count.txt`.""",
            check=f"[ \"$(cat {LAB}/etc-count.txt | tr -d ' ')\" = \"$(ls /etc | wc -l | tr -d ' ')\" ]",
            hints=["`ls /etc | wc -l > ~/lab/etc-count.txt`"],
            solution="ls /etc | wc -l > ~/lab/etc-count.txt",
        ),
        Task(
            id="m05-02", title="Потоки: stdout, stderr, >>",
            brief="""У процесса три потока: 0 — stdin, 1 — stdout, 2 — stderr.
`>` перезаписывает, `>>` дописывает, `2>` перенаправляет ошибки, `&>` — и то и другое,
`2>/dev/null` — выбросить ошибки.

Задание: выполни `ls /etc /nosuchdir` так, чтобы обычный вывод попал в `~/lab/out.txt`,
а сообщение об ошибке — в `~/lab/err.txt`.""",
            setup=f"rm -f {LAB}/out.txt {LAB}/err.txt",
            check=f"test -s {LAB}/out.txt && grep -qi 'nosuchdir' {LAB}/err.txt && ! grep -qi 'No such' {LAB}/out.txt",
            hints=["`ls /etc /nosuchdir > ~/lab/out.txt 2> ~/lab/err.txt`"],
            solution="ls /etc /nosuchdir > ~/lab/out.txt 2> ~/lab/err.txt",
        ),
        Task(
            id="m05-03", title="sort и uniq",
            brief="""`sort` сортирует (`-n` — численно, `-r` — обратно, `-k2` — по второму полю),
`uniq -c` считает повторы (работает только по соседним строкам, поэтому сначала sort).

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
            brief="""`cut -d: -f1` вырезает поле по разделителю, `tr 'a-z' 'A-Z'` заменяет символы,
`tee файл` пишет в файл и одновременно отдаёт дальше по конвейеру.

Задание: получи список имён всех пользователей системы из `/etc/passwd`, переведи их в ВЕРХНИЙ регистр
и сохрани в `~/lab/USERS.txt`.""",
            check=f"grep -qx 'ROOT' {LAB}/USERS.txt && ! grep -q '[a-z]' {LAB}/USERS.txt",
            hints=["`cut -d: -f1 /etc/passwd | tr 'a-z' 'A-Z' > ~/lab/USERS.txt`"],
            solution="cut -d: -f1 /etc/passwd | tr 'a-z' 'A-Z' > ~/lab/USERS.txt",
        ),
        Task(
            id="m05-05", title="sed — потоковая замена",
            brief="""`sed 's/что/на_что/g' файл` заменяет текст, `-i` правит файл на месте,
`sed -n '5,10p'` печатает диапазон строк, `sed '/шаблон/d'` удаляет строки.

Задание: в файле `~/lab/config.ini` замени все `localhost` на `example.com` прямо в файле.""",
            setup=f"printf 'host=localhost\\nbackup=localhost\\nport=8080\\n' > {LAB}/config.ini",
            check=f"! grep -q localhost {LAB}/config.ini && [ \"$(grep -c example.com {LAB}/config.ini)\" -eq 2 ]",
            hints=["`sed -i 's/localhost/example.com/g' ~/lab/config.ini`"],
            solution="sed -i 's/localhost/example.com/g' ~/lab/config.ini",
        ),
        Task(
            id="m05-06", title="awk — работа по полям",
            brief="""`awk` — мини-язык обработки таблиц. `awk -F: '{print $1, $3}'` печатает 1-е и 3-е поле,
`awk -F: '$3 >= 1000 {print $1}'` — с условием.

Задание: выпиши в `~/lab/system-users.txt` имена пользователей с UID меньше 10 (третье поле `/etc/passwd`).""",
            check=f"grep -qx 'root' {LAB}/system-users.txt && grep -qx 'daemon' {LAB}/system-users.txt && ! grep -q ':' {LAB}/system-users.txt",
            hints=["`awk -F: '$3 < 10 {print $1}' /etc/passwd > ~/lab/system-users.txt`"],
            solution="awk -F: '$3 < 10 {print $1}' /etc/passwd > ~/lab/system-users.txt",
        ),
        Task(
            id="m05-07", title="xargs",
            brief="""`xargs` превращает строки со стандартного ввода в аргументы команды.
Классика: `find . -name '*.log' | xargs rm`. Безопаснее: `find . -print0 | xargs -0 rm`.

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
