#!/bin/bash
# generate-certificate.sh

# чистим папку, где могут находиться старые сертификаты
rm -rf /etc/letsencrypt/live/$DOMAIN_URL

echo $DOMAIN_URL
echo helloworld

# выдаем себе сертификат
certbot certonly --standalone --non-interactive --email $DOMAIN_EMAIL -d $DOMAIN_URL --cert-name=certfolder --key-type rsa --agree-tos -v

# удаляем старые сертификаты из примонтированной
# через Docker Compose папки Nginx
rm -rf /etc/nginx/cert.pem
rm -rf /etc/nginx/key.pem

# копируем сертификаты из образа certbot в папку Nginx
cp /etc/letsencrypt/live/$DOMAIN_URL/fullchain.pem /etc/nginx/cert.pem
cp /etc/letsencrypt/live/$DOMAIN_URL/privkey.pem /etc/nginx/key.pem
