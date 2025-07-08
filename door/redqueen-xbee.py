#!/usr/bin/env python3

import MySQLdb
from xbee import ZigBee
import serial
from struct import pack
import argparse
import os
import database

parser = argparse.ArgumentParser(description='RedQueen door system daemon.')
parser.add_argument('--baud-rate', type=int, default=115200)
parser.add_argument('--serial-port', default='ttyUSB0')

args = parser.parse_args()

ser = serial.Serial('/dev/%s' % args.serial_port, args.baud_rate)
xbee = ZigBee(ser)

xbee.send('at', command='AT')
xbee.send('at', command='ID')
xbee.send('at', command='CN')

print("BOOTED")

mysql_database = os.environ.get('REDQUEEN_DATABASE')
mysql_host = os.environ.get('REDQUEEN_DB_HOST')
mysql_user = os.environ.get('REDQUEEN_DB_USER')
mysql_pass = os.environ.get('REDQUEEN_DB_PASS')
door_identifier = os.environ.get('REDQUEEN_XBEE_DOOR_IDENTIFIER')

# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print(response)

        if 'rf_data' in response:
            conn = MySQLdb.connect(
                host=mysql_host,
                user=mysql_user,
                passwd=mysql_pass,
                db=mysql_database
            )
            cmd, data = response['rf_data'].decode('ASCII').split(':', 1)
            if cmd != 'A':
                continue

            door_card, pin = data.split(':')

            print("Card ", door_card, " PIN ", pin)

            card = database.query_access(conn, door_card, door_identifier)

            valid_pin = False

            if card is None:
                print("No card found")
            elif card[2] == 0 or (card[2] == 1 and card[1] == pin):
                print("Found card, valid pin... opening door!")
                valid_pin = True
                print({'data': pack('>bL', 0, 5)})
                xbee.send('tx', dest_addr=response['source_addr'], dest_addr_long=response['source_addr_long'],
                          data=pack('>bL', 0, 5))
            else:
                print("Found card, invalid pin")

            database.log_access(conn, door_card, door_card, valid_pin, door_identifier)

            conn.close()
    except KeyboardInterrupt:
        break

ser.close()
