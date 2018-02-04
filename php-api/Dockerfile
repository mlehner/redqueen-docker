ARG BASE_IMAGE=resin/raspberrypi3-alpine:3.5
FROM $BASE_IMAGE

RUN apk add --no-cache git php5-fpm php5-pdo_mysql php5-json php5-ctype php5-intl php5-iconv php5-opcache

COPY php-fpm.conf /etc/php5/

RUN git clone --branch release --depth 1 https://github.com/mlehner/redqueen-php-api.git /redqueen

ENTRYPOINT [ "/usr/bin/php-fpm5" ]
