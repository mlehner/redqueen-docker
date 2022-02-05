ARG BASE_IMAGE=resin/raspberrypi3-alpine:3.5
FROM $BASE_IMAGE

RUN apk add --no-cache git php7-fpm php7-pdo_mysql php7-json php7-ctype php7-intl php7-iconv php7-opcache

COPY php-fpm.conf /etc/php7/

RUN git clone --branch release --depth 1 https://github.com/mlehner/redqueen-php-api.git /redqueen

ENTRYPOINT [ "/usr/sbin/php-fpm7" ]
