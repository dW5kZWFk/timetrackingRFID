#!/usr/bin/env python3
import threading
from flask import Flask
from flask import render_template
import sqlite3
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
from time import sleep


app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


#zeigt alle aktuell angemeldeten Nutzer
@app.route('/')
def index():

    return render_template('status.html')


#check whether employee is logged in or logged out
def check_status(uid):
    conn = get_db_connection()
    sql = f'SELECT status FROM employee_status WHERE uid=={uid}'

    cur = conn.cursor()
    rows=cur.execute(sql).fetchall()
    conn.close()

    return rows[0][0]


def change_status_arrived(uid):
    conn = get_db_connection()

    sql = f'UPDATE table employee_status set status = 1 WHERE uid=={uid}'

    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    return 0


def do_my_stuff():
    print("scanning for cards")
    #register rfid scanner
    reader = SimpleMFRC522()

    #register leds
    #SimpleMFRC522 uses GPIO BOARD Mode !
    LED_PIN_GREEN = 11 #17 BCM
    LED_PIN_RED = 13    #27 BCM

    GPIO.setup(LED_PIN_GREEN, GPIO.OUT)
    GPIO.setup(LED_PIN_RED, GPIO.OUT)

    try:
        while(1):
            id,_=reader.read()

            if id:
                print(f'card detected: {id}')
                GPIO.output(LED_PIN_GREEN,GPIO.HIGH)
                sleep(2)
                GPIO.output(LED_PIN_GREEN, GPIO.LOW)
                print(check_status(id))


    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()
    do_my_stuff()

#flask run --host=0.0.0.0