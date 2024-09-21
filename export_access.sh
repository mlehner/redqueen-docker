#!/bin/sh

echo "select c.id,c.name,c.code,c.isActive,MAX(l.created_at),c.created_at,GROUP_CONCAT(distinct s.name) FROM cards c left join card_schedule cs on (c.id = cs.card_id) left join schedules s on (cs.schedule_id = s.id) left join logs l on (l.code = c.code and l.validPin = 1) group by c.id;" | docker compose exec mysql sh -c 'exec mysql -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}"'
