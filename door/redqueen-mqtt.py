#!/usr/bin/env python3

import MySQLdb
import os
import json
import paho.mqtt.client as mqtt
import database

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

    door_identifier = payload.get("doorName")

    if payload.get("type") == "access":
        if payload.get("isKnown") == "false":
            return

        if door_card == ' ' and payload.get("username") == 'MQTT':
            return

        if payload.get("log_id"):
            return

        print("Card was known already")

        database.log_access(conn, None, door_card, True, door_identifier)

        return

    print("Card", door_card)

    if door_identifier is None:
        print("Missing door identifier (doorName)")
        return

    door_ip = payload.get("doorip")

    if door_ip is None:
        print("Door IP not included in payload")
        return

    card = database.query_access(conn, door_card, door_identifier)

    if card is None:
        print("No card found")
        log_id = database.log_access(conn, None, door_card, valid_pin, door_identifier)
        reply_to_mqtt_msg(client, msg, {'cmd': 'accessdenied', 'doorip': door_ip, 'uid': door_card, 'user': 'Unknown',
                                        'log_id': str(log_id)})
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

        log_id = database.log_access(conn, card[0], door_card, valid_pin, door_identifier)

        if valid_pin:
            print("Valid pin, opening door")
            reply_to_mqtt_msg(client, msg, {'cmd': 'accessgranted', 'door': '0', 'doorip': door_ip, 'uid': door_card,
                                            'user': card[3], 'log_id': str(log_id)})
        else:
            print("Invalid pin")
            reply_to_mqtt_msg(client, msg, {'cmd': 'accessdenied', 'doorip': door_ip, 'uid': door_card, 'user': card[3],
                                            'log_id': str(log_id)})

    conn.close()


mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(mqtt_host, 1883, 60)

try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    mqttc.disconnect()
