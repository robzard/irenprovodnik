#!/bin/bash

# Загрузите ключ в ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# Перейдите в директорию проекта
cd irenprovodnik

git checkout $CHECKOUT_BRANCH

# Создаём htpasswd для nginx
# Загрузка переменных из .env файла
source .env

# Проверка и создание файла .htpasswd
if [ ! -f /tmp/.htpasswd ]; then
  apt update && apt install apache2-utils
  touch /tmp/.htpasswd
  chmod 644 /tmp/.htpasswd
fi
if [[ -n "$HTPASSWD_USER" && -n "$HTPASSWD_PASS" ]]; then
    echo "Создание файла .htpasswd..."
    sudo htpasswd -cb /root/irenprovodnik/.htpasswd $HTPASSWD_USER $HTPASSWD_PASS
else
    echo "Переменные HTPASSWD_USER и HTPASSWD_PASS не определены."
    exit 1
fi

# Выполните git pull
git pull

# Дополнительные команды для деплоя, например:
docker-compose build
docker-compose up -d
