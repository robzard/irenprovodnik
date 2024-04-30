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

#при первом запуске
if ! command -v htpasswd &> /dev/null
then
    echo "htpasswd could not be found, installing..."
    sudo apt-get update && sudo apt-get install -y apache2-utils
fi

# Проверка и установка Docker
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found, installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    newgrp docker
fi

# Проверка и установка Docker Compose
if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose could not be found, installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
#при первом запуске

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
docker compose build
docker compose up -d


# Проверка наличия сертификатов
if [ ! -f "/etc/letsencrypt/live/$DOMEN_WEB_APP.ru/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/$DOMEN_WEB_APP.ru/privkey.pem" ]; then
    echo "Сертификаты не найдены. Запускаем Certbot для создания сертификатов..."

    # Остановка сервисов, которые могут использовать порт 80
    docker-compose stop nginx

    # Запуск Certbot
    docker run -it --rm -p 80:80 --name certbot \
        certbot/certbot certonly --standalone \
        -d $DOMEN_WEB_APP.ru --agree-tos \
        --email $DOMAIN_EMAIL --non-interactive

    docker cp certbot:/etc/letsencrypt/live/irenprovodnik.ru/fullchain.pem .
    docker cp certbot:/etc/letsencrypt/live/irenprovodnik.ru/privkey.pem .

    # Перезапуск сервисов после получения сертификатов
    docker-compose start nginx
fi
