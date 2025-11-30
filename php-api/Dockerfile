ARG BASE_IMAGE=arm64v8/alpine:3.19
FROM $BASE_IMAGE

RUN apk add --no-cache git php81 php81-fpm php81-pdo_mysql php81-json php81-ctype php81-intl php81-iconv php81-opcache php81-bcmath php81-tokenizer php81-dom

COPY php-fpm.conf /etc/php81/

RUN git clone --branch release --depth 1 https://github.com/mlehner/redqueen-php-api.git /redqueen

ENTRYPOINT [ "/usr/sbin/php-fpm81" ]
