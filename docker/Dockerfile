# 1. Базов Linux
FROM debian:stable

ENV DEBIAN_FRONTEND=noninteractive
ENV VENV_PATH=/opt/venv

# 2. Инсталиране на нужния софтуер
# Системни пакети + Python venv
RUN apt-get update && apt-get install -y \
    fetchmail \
    dovecot-imapd \
    dovecot-lmtpd \
    python3 \
    python3-venv \
    ca-certificates \
    cron \
    && python3 -m venv $VENV_PATH \
    && $VENV_PATH/bin/pip install --no-cache-dir requests pyyaml flask \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Правим venv python по подразбиране
ENV PATH="$VENV_PATH/bin:$PATH"

# Работна директория за твоя код
WORKDIR /app

# 3. Създаваме нужните директории в контейнера
RUN mkdir -p /config /scripts /maildata /logs

# 4. Копираме entrypoint и скриптовете
COPY entrypoint.sh /entrypoint.sh
COPY scripts/ /scripts/
COPY web/ /app/web/

# 5. Права за изпълнение
RUN chmod +x /entrypoint.sh && chmod +x /scripts/*.py

# 6. Това се изпълнява при старт на контейнера
CMD ["/entrypoint.sh"]
