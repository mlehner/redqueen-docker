#!/bin/bash

docker exec redqueen_mysql mysqldump redqueen > redqueen_`date +%s`.sql
