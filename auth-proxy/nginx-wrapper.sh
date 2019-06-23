#!/bin/bash

echo "${HTPASSWD_CONTENTS}" > /.htpasswd
envsubst '$SERVER_NAME' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;' "$@"
