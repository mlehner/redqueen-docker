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

def reply_to_mqtt_msg(mqtt_client, msg, reply_payload):
    cmd_topic = msg.topic.replace("/send", "/cmd")
    print(cmd_topic, reply_payload)
    mqtt_client.publish(cmd_topic, payload=json.dumps(reply_payload))

def on_connect(client, userdata, flags, reason_code):
    print("Connected with result code", reason_code)
    client.subscribe("esp-rfid/+/send")


def on_message(client, userdata, msg):
    print(msg.topic, str(msg.payload))

    payload = json.loads(msg.payload)

    if payload.get("type") != "cardswipe" and payload.get("type") != "pincodeentered" and payload.get("type") != "access":
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

    if payload.get("type") == "access":
        if payload.get("isKnown") == "false":
            return

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

    door_identifier = payload.get("doorName")

    if door_identifier is None:
        print("Missing door identifier (doorName)")
        return

    query = """
    SELECT
        c.id AS card_id,
        c.pin,
        COUNT(IF(s.authenticationMode = "card_pin", 1, NULL)) > 0 as require_pin
    FROM cards c
    LEFT JOIN card_schedule cs ON (c.id = cs.card_id)
    LEFT JOIN schedules s ON (cs.schedule_id = s.id)
    LEFT JOIN door_schedule ds ON (s.id = ds.schedule_id)
    LEFT JOIN doors d ON (d.id = ds.door_id)
    WHERE
        c.code = %%s
        AND c.isActive = 1
        AND s.%s = 1
        AND d.identifier = %%s
        AND %%s BETWEEN s.startTime AND s.endTime
    GROUP BY c.id, d.id
  """ % (dayColumn,)

    with conn.cursor() as c:
        c.execute(query, (door_card, door_identifier, dateToday.format('HH:mm:ss'),))
        card = c.fetchone()

    valid_pin = False

    if card is None:
        print("No card found")
    else:
        print("Found card")

        if card[2]:
            if payload.get("type") != "pincodeentered":
                # do nothing right now, wait for pincodeentered
                print("Waiting for PIN code...")
                return
            else:
                valid_pin = card[1] == payload.get("pincode")
        else:
            valid_pin = True

        door_ip = payload.get("doorip")

        if door_ip is None:
            print("Door IP not included in payload")
        elif valid_pin:
            print("Valid pin, opening door")
            doorcmd = {'cmd': 'open', 'door': '0', 'doorip': door_ip}

            cmd_topic = msg.topic.replace("/send", "/cmd")
            client.publish(cmd_topic, payload=json.dumps(doorcmd))
        else:
            print("Invalid pin")

    with conn.cursor() as c:
        c.execute('INSERT INTO logs (code, validPin, created_at, door_identifier) VALUES (%s, %s, NOW(), %s)', (door_card, valid_pin, door_identifier))
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
