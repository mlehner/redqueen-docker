import arrow

def log_access(conn, card_id, door_card, valid_pin, door_identifier):
    with conn.cursor() as c:
        c.execute('INSERT INTO logs (card_id, code, validPin, created_at, door_identifier) VALUES (%s, %s, %s, NOW(), %s)',
                  (card_id, door_card, valid_pin, door_identifier))
        conn.commit()
        return c.lastrowid

def query_access(conn, door_card, door_identifier):
    dowToColumn = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    # Schedules are relative to where the door is, our only door is in EST
    dateToday = arrow.utcnow().to('America/New_York')

    dayColumn = dowToColumn[dateToday.weekday()]

    query = """
      SELECT
          c.id AS card_id,
          c.pin,
          COUNT(IF(s.authenticationMode = "card_pin", 1, NULL)) > 0 as require_pin,
          c.name,
          COUNT(IF(s.%s = 1, 1, NULL)) > 0 as matched_days,
          COUNT(IF(d.identifier = %%s, 1, NULL)) > 0 as matched_doors
      FROM cards c
      LEFT JOIN card_schedule cs ON (c.id = cs.card_id)
      LEFT JOIN schedules s ON (cs.schedule_id = s.id)
      LEFT JOIN door_schedule ds ON (s.id = ds.schedule_id)
      LEFT JOIN doors d ON (d.id = ds.door_id)
      WHERE
          c.disabled_at IS NULL
          c.code = %%s
          AND c.isActive = 1
          AND s.%s = 1
          AND d.identifier = %%s
          AND %%s BETWEEN s.startTime AND s.endTime
      GROUP BY c.id, d.id
    """ % (dayColumn,dayColumn,)

    with conn.cursor() as c:
        c.execute(query, (door_identifier, door_card, door_identifier, dateToday.format('HH:mm:ss'),))
        return c.fetchone()
