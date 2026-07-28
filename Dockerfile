FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        systemd systemd-sysv dbus \
        bash-completion sudo procps psmisc lsof file less tree \
        nano vim-tiny \
        iproute2 iputils-ping dnsutils curl wget netcat-openbsd net-tools \
        cron rsyslog logrotate \
        openssh-server openssh-client \
        man-db manpages \
        tar gzip bzip2 xz-utils zip unzip \
        acl attr util-linux findutils grep sed gawk \
        iptables ca-certificates tzdata rsync jq \
    && rm -rf /var/lib/apt/lists/*

# Убираем то, что в контейнере только шумит и мешает старту systemd
RUN systemctl mask getty.target console-getty.service systemd-udevd.service \
        systemd-udev-trigger.service systemd-networkd.service \
        systemd-resolved.service systemd-timesyncd.service 2>/dev/null || true

RUN mkdir -p /var/log/ltrain /root/lab && touch /var/log/ltrain/history.log

COPY container/profile.sh /etc/profile.d/00-ltrain.sh

STOPSIGNAL SIGRTMIN+3
CMD ["/sbin/init"]
