#!/bin/bash

echo "${HTPASSWD_CONTENTS}" > /.htpasswd

exec nginx -g 'daemon off;' "$@"
