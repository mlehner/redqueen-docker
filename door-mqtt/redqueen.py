#!/usr/bin/env python3

import MySQLdb
import os
import arrow
import json
import paho.mqtt.client as mqtt

print("BOOTED")

mysql_database = os.environ.get('REDQUEEN_DATABASE')
mysql_host = os.environ.get('REDQUEEN_DB_HOST')
mysql_user = os.environ.get('REDQUEEN_DB_USER')
mysql_pass = os.environ.get('REDQUEEN_DB_PASS')
mqtt_host = os.environ.get('REDQUEEN_MQTT_HOST')


def on_connect(client, userdata, flags, reason_code):
    print("Connected with result code", reason_code)
    client.subscribe("esp-rfid/+/send")


def on_message(client, userdata, msg):
    print(msg.topic, str(msg.payload))

    payload = json.loads(msg.payload)

    if payload.get("type") != "access":
        return

    if 'uid' not in payload:
        print("Missing uid")
        return

    conn = MySQLdb.connect(
        host=mysql_host,
        user=mysql_user,
        passwd=mysql_pass,
        db=mysql_database
    )

    door_card = str(payload["uid"]).upper()
    valid_pin = False

    if payload.get("isKnown") != "false":
        if door_card == ' ' and payload.get("username") == 'MQTT':
            return

        valid_pin = True

        print("Card was known already")

        with conn.cursor() as c:
            c.execute('INSERT INTO logs (code, validPin, created_at) VALUES (%s, %s, NOW())', (door_card, valid_pin))
            conn.commit()

        return

    print("Card", door_card)

    dowToColumn = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    # Schedules are relative to where the door is, our only door is in EST
    dateToday = arrow.utcnow().to('America/New_York')

    dayColumn = dowToColumn[dateToday.weekday()]

    query = """
   SELECT DISTINCT
       c.id
   FROM
       cards c
   LEFT JOIN
       card_schedule cs ON (c.id = cs.card_id)
   LEFT JOIN
       schedules s ON (cs.schedule_id = s.id)
   WHERE
       c.code = %%s
       AND c.isActive = 1
       AND s.%s = 1
       AND %%s BETWEEN s.startTime AND s.endTime
  """ % (dayColumn,)

    with conn.cursor() as c:
        c.execute(query, (door_card, dateToday.format('HH:mm:ss'),))
        card = c.fetchone()

    if card is None:
        print("No card found")
    else:
        print("Found card, valid pin... opening door!")
        valid_pin = True

        door_ip = payload.get("doorip")

        if door_ip is None:
            print("Door IP not included in payload")
        else:
            doorcmd = {'cmd': 'open', 'door': '0', 'doorip': door_ip}

            cmd_topic = msg.topic.replace("/send", "/cmd")
            client.publish(cmd_topic, payload=json.dumps(doorcmd))

    with conn.cursor() as c:
        c.execute('INSERT INTO logs (code, validPin, created_at) VALUES (%s, %s, NOW())', (door_card, valid_pin))
        conn.commit()

    conn.close()


mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(mqtt_host, 1883, 60)

try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    mqttc.disconnect()
