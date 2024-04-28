#!/bin/sh

# Замена $DOMEN_WEB_APP на значение переменной окружения DOMEN_WEB_APP в nginx.conf
if [ -n "$DOMEN_WEB_APP" ]; then
  sed -i "s/\$DOMEN_WEB_APP/$DOMEN_WEB_APP/g" /etc/nginx/nginx.conf
else
  echo "Переменная DOMEN_WEB_APP не установлена."
fi

# Запуск nginx
exec nginx -g 'daemon off;'
