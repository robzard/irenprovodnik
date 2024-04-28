FROM nginx:latest

WORKDIR /app

# Копирование конфигурационного файла Nginx и скрипта замены
COPY nginx.conf /etc/nginx/nginx.conf
COPY replace_domain.sh /app/replace_domain.sh

# Делаем скрипт замены исполняемым
RUN chmod +x /app/replace_domain.sh

# Запуск скрипта при старте контейнера
CMD ["/app/replace_domain.sh"]