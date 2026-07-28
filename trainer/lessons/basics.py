from ..model import Module, Task

LAB = "/root/lab"

m01 = Module(
    id="m01", title="Навигация по файловой системе", level="новичок",
    tasks=[
        Task(
            id="m01-01", title="Где я нахожусь",
            brief="""Первое, что нужно уметь — понимать, где ты стоишь.
`pwd` печатает текущий каталог, `cd` переходит в другой.

Задание: убедись, что ты находишься в `/root/lab`, и запиши текущий путь в файл `where.txt`.
Подсказка по синтаксису: `>` перенаправляет вывод команды в файл.""",
            setup=f"mkdir -p {LAB}; rm -f {LAB}/where.txt",
            check=f"grep -qx '/root/lab' {LAB}/where.txt",
            hints=["Сначала `cd /root/lab`", "Потом `pwd > where.txt`"],
            solution="cd /root/lab && pwd > where.txt",
        ),
        Task(
            id="m01-02", title="Абсолютные и относительные пути",
            brief="""Путь, начинающийся со `/` — абсолютный (от корня). Всё остальное — относительно текущего каталога.
`.` — текущий каталог, `..` — родительский, `~` — домашний каталог, `cd -` — вернуться назад.

Задание: сходи в `/etc`, оттуда — обратно одной командой, а затем создай в `~/lab` дерево каталогов `a/b/c` одной командой.""",
            check=f"test -d {LAB}/a/b/c",
            check_history=r"cd\s+/etc",
            hints=["`cd /etc`, затем `cd -`", "`mkdir -p a/b/c` — ключ `-p` создаёт цепочку каталогов"],
            solution="cd /etc; cd -; mkdir -p ~/lab/a/b/c",
        ),
        Task(
            id="m01-03", title="ls и скрытые файлы",
            brief="""`ls` показывает содержимое каталога. Полезные ключи:
`-l` — подробно, `-a` — включая скрытые (начинаются с точки), `-h` — размеры по-человечески, `-t` — сортировка по времени.

Задание: создай скрытый файл `.secret` в `~/lab` и сохрани подробный листинг каталога (со скрытыми файлами) в `listing.txt`.""",
            setup=f"rm -f {LAB}/.secret {LAB}/listing.txt",
            check=f"test -f {LAB}/.secret && grep -q '\\.secret' {LAB}/listing.txt",
            hints=["`touch .secret` создаст пустой файл", "`ls -la > listing.txt`"],
            solution="touch ~/lab/.secret && ls -la ~/lab > ~/lab/listing.txt",
        ),
        Task(
            id="m01-04", title="Смотрим на систему",
            brief="""Каталоги Linux не случайны: `/etc` — конфиги, `/var` — изменяемые данные и логи,
`/usr` — программы, `/home` — домашние каталоги, `/proc` — виртуальная ФС с информацией о ядре и процессах.

Задание: сохрани подробный список содержимого `/etc` в файл `~/lab/etc-list.txt`.""",
            check=f"grep -q 'hosts' {LAB}/etc-list.txt && grep -q 'passwd' {LAB}/etc-list.txt",
            hints=["`ls -l /etc > ~/lab/etc-list.txt`"],
            solution="ls -l /etc > ~/lab/etc-list.txt",
        ),
        Task(
            id="m01-05", title="Дерево каталогов",
            brief="""`tree` рисует структуру каталогов. Ключ `-L N` ограничивает глубину.

Задание: сохрани дерево каталога `/etc` глубиной 1 уровень в файл `~/lab/tree.txt`.""",
            check=f"grep -q 'directories' {LAB}/tree.txt && grep -q 'systemd' {LAB}/tree.txt",
            hints=["`tree -L 1 /etc > ~/lab/tree.txt`"],
            solution="tree -L 1 /etc > ~/lab/tree.txt",
        ),
        Task(
            id="m01-06", title="Справка: man и --help",
            brief="""Главный навык администратора — уметь читать справку.
`man ls` — полное руководство (выход по `q`), `ls --help` — короткая справка.

Задание: посмотри `man ls`, а затем сохрани короткую справку `ls` в `~/lab/lshelp.txt`.""",
            check=f"grep -q 'almost-all' {LAB}/lshelp.txt",
            check_history=r"\bman\b",
            hints=["`man ls`, выход — клавиша q", "`ls --help > ~/lab/lshelp.txt`"],
            solution="man ls; ls --help > ~/lab/lshelp.txt",
        ),
    ],
)

m02 = Module(
    id="m02", title="Операции с файлами и каталогами", level="новичок",
    tasks=[
        Task(
            id="m02-01", title="Создание файлов пачкой",
            brief="""`touch` создаёт пустой файл (или обновляет время изменения).
Bash умеет раскрывать фигурные скобки: `file{1,2,3}.txt` превратится в три имени.

Задание: одной командой создай в `~/lab` файлы `one.txt`, `two.txt`, `three.txt`.""",
            setup=f"cd {LAB} && rm -f one.txt two.txt three.txt",
            check=f"test -f {LAB}/one.txt && test -f {LAB}/two.txt && test -f {LAB}/three.txt",
            hints=["`touch {one,two,three}.txt`"],
            solution="cd ~/lab && touch {one,two,three}.txt",
        ),
        Task(
            id="m02-02", title="Каталоги проекта",
            brief="""`mkdir -p` создаёт вложенные каталоги, скобки работают и здесь.

Задание: создай структуру `~/lab/project/` с подкаталогами `src`, `bin`, `docs` — одной командой.""",
            check=f"test -d {LAB}/project/src && test -d {LAB}/project/bin && test -d {LAB}/project/docs",
            hints=["`mkdir -p ~/lab/project/{src,bin,docs}`"],
            solution="mkdir -p ~/lab/project/{src,bin,docs}",
        ),
        Task(
            id="m02-03", title="Копирование",
            brief="""`cp источник назначение`. Для каталогов нужен ключ `-r` (рекурсивно),
`-a` сохраняет права и время, `-v` показывает, что происходит.

Задание: скопируй `one.txt` в `project/src/`, а весь каталог `project` — в `project-backup`.""",
            check=f"test -f {LAB}/project/src/one.txt && test -d {LAB}/project-backup/src && test -f {LAB}/project-backup/src/one.txt",
            hints=["`cp one.txt project/src/`", "`cp -r project project-backup`"],
            solution="cd ~/lab && cp one.txt project/src/ && cp -r project project-backup",
        ),
        Task(
            id="m02-04", title="Перемещение и переименование",
            brief="""В Linux переименование и перемещение — это одна команда `mv`.

Задание: переименуй `two.txt` в `notes.md` и перемести `three.txt` в каталог `project/docs/`.""",
            check=f"test -f {LAB}/notes.md && ! test -f {LAB}/two.txt && test -f {LAB}/project/docs/three.txt",
            hints=["`mv two.txt notes.md`", "`mv three.txt project/docs/`"],
            solution="cd ~/lab && mv two.txt notes.md && mv three.txt project/docs/",
        ),
        Task(
            id="m02-05", title="Удаление (осторожно!)",
            brief="""`rm файл` удаляет файл, `rm -r каталог` — каталог с содержимым. Корзины нет: удалённое не вернуть.
Профессиональная привычка — сначала `ls` на ту же маску, потом `rm`.

Задание: удали каталог `~/lab/trash` вместе с содержимым и файл `~/lab/junk.tmp`.""",
            setup=f"mkdir -p {LAB}/trash/sub && touch {LAB}/trash/sub/x {LAB}/junk.tmp",
            check=f"! test -e {LAB}/trash && ! test -e {LAB}/junk.tmp",
            hints=["`rm -r trash`", "`rm junk.tmp`"],
            solution="cd ~/lab && rm -r trash && rm junk.tmp",
        ),
        Task(
            id="m02-06", title="Ссылки: жёсткие и символические",
            brief="""`ln -s цель имя` создаёт символическую ссылку (ярлык на путь).
`ln цель имя` — жёсткую ссылку (второе имя того же файла на диске).

Задание: сделай символическую ссылку `~/lab/latest` на файл `~/lab/notes.md`.""",
            check=f"test -L {LAB}/latest && readlink -f {LAB}/latest | grep -q 'notes.md'",
            hints=["`ln -s notes.md latest` (из каталога ~/lab)", "Проверить: `ls -l latest`"],
            solution="cd ~/lab && ln -s notes.md latest",
        ),
    ],
)

m03 = Module(
    id="m03", title="Чтение и создание текстовых файлов", level="новичок",
    tasks=[
        Task(
            id="m03-01", title="cat и heredoc",
            brief="""`cat файл` печатает файл целиком. `cat > файл` пишет в файл то, что ты набираешь (закончить Ctrl+D).
Удобнее «heredoc»:
  cat > poem.txt << 'EOF'
  первая строка
  вторая строка
  EOF

Задание: создай `~/lab/poem.txt` ровно из трёх непустых строк.""",
            setup=f"rm -f {LAB}/poem.txt",
            check=f"test -f {LAB}/poem.txt && [ \"$(grep -c . {LAB}/poem.txt)\" -eq 3 ]",
            hints=["Можно и так: `printf 'a\\nb\\nc\\n' > poem.txt`"],
            solution="printf 'раз\\nдва\\nтри\\n' > ~/lab/poem.txt",
        ),
        Task(
            id="m03-02", title="head, tail и большие файлы",
            brief="""`head -n 20 файл` — первые 20 строк, `tail -n 20` — последние.
`tail -f файл` следит за файлом в реальном времени — незаменимо для логов.

Задание: из подготовленного `~/lab/big.log` (1000 строк) сохрани последние 20 строк в `~/lab/tail20.txt`.""",
            setup=f"seq 1 1000 | sed 's/^/line /' > {LAB}/big.log; rm -f {LAB}/tail20.txt",
            check=f"[ \"$(wc -l < {LAB}/tail20.txt)\" -eq 20 ] && grep -qx 'line 1000' {LAB}/tail20.txt && grep -qx 'line 981' {LAB}/tail20.txt",
            hints=["`tail -n 20 big.log > tail20.txt`"],
            solution="cd ~/lab && tail -n 20 big.log > tail20.txt",
        ),
        Task(
            id="m03-03", title="less — листаем большие файлы",
            brief="""`less файл` — интерактивный просмотр: стрелки и PgUp/PgDn листают, `/текст` ищет,
`n` — следующее совпадение, `G` — в конец, `g` — в начало, `q` — выход.

Задание: открой `~/lab/big.log` в `less`, найди строку `line 777`, выйди. Затем подтверди проверку.""",
            check_history=r"\bless\b",
            hints=["`less big.log`, затем набери `/line 777` и Enter, выход — `q`"],
            solution="less ~/lab/big.log",
        ),
        Task(
            id="m03-04", title="wc — считаем строки и слова",
            brief="""`wc -l` — строки, `-w` — слова, `-c` — байты.

Задание: посчитай, сколько строк в `/etc/passwd`, и запиши только число в `~/lab/users-count.txt`.""",
            check=f"[ \"$(cat {LAB}/users-count.txt 2>/dev/null | tr -d ' ')\" = \"$(wc -l < /etc/passwd)\" ]",
            hints=["`wc -l < /etc/passwd > ~/lab/users-count.txt` — при вводе через `<` имя файла не печатается"],
            solution="wc -l < /etc/passwd > ~/lab/users-count.txt",
        ),
        Task(
            id="m03-05", title="Редактор в терминале",
            brief="""Уметь править конфиг на сервере без графики обязательно. `nano` — простой (Ctrl+O сохранить, Ctrl+X выйти).
`vim` — мощный: `i` — режим ввода, `Esc`, `:wq` — сохранить и выйти, `:q!` — выйти без сохранения.

Задание: создай редактором файл `~/lab/editor.txt` со словом `готово` внутри.""",
            setup=f"rm -f {LAB}/editor.txt",
            check=f"grep -q 'готово' {LAB}/editor.txt",
            hints=["`nano ~/lab/editor.txt`, набери текст, Ctrl+O, Enter, Ctrl+X"],
            solution="nano ~/lab/editor.txt",
        ),
    ],
)

MODULES = [m01, m02, m03]
