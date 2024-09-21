#!/bin/bash

docker compose exec mysql sh -c 'exec mysqldump -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" --no-tablespaces "${MYSQL_DATABASE}"'
