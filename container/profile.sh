# Настройки учебной песочницы linux-trainer

export HISTFILE=/var/log/ltrain/history.log
export HISTSIZE=200000
export HISTFILESIZE=200000
export HISTCONTROL=
shopt -s histappend 2>/dev/null

# После каждой команды: дописываем историю и запоминаем текущий каталог,
# чтобы правая панель могла проверять задания в том же месте, где ты работаешь.
export PROMPT_COMMAND='history -a; pwd > /var/log/ltrain/cwd 2>/dev/null'

export PS1='\[\e[1;32m\]lab\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '

case $- in
  *i*) cd /root/lab 2>/dev/null ;;
esac
