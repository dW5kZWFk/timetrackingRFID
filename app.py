#!/usr/bin/env python3
import threading
from flask import Flask
from flask import render_template
import sqlite3
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
from time import sleep


app = Flask(__name__)

LED_PIN_GREEN = 11  #17 BCM
LED_PIN_RED = 13  #27 BCM

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

    sql = f'UPDATE employee_status set status = 1, start_time=datetime(now) WHERE uid=={uid}'

    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    return 0


def blink_log_in_success():
    GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
    sleep(1)
    GPIO.output(LED_PIN_GREEN, GPIO.LOW)
    return


def blink_error():

    for i in range(0,10):
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(LED_PIN_RED, GPIO.LOW)
        sleep(0.5)
    return


def do_my_stuff():
    print("scanning for cards")
    #register rfid scanner
    reader = SimpleMFRC522()

    #register leds
    #SimpleMFRC522 uses GPIO BOARD Mode !

    GPIO.setup(LED_PIN_GREEN, GPIO.OUT)
    GPIO.setup(LED_PIN_RED, GPIO.OUT)

    GPIO.output(LED_PIN_GREEN, GPIO.LOW)
    GPIO.output(LED_PIN_GREEN, GPIO.LOW)

    try:
        while(1):
            id,_=reader.read()

            if id:
                print(f'card detected: {id}')
                status=check_status(id)
                print(f'status:{status}')

                if status=='0':
                    print("status is null!")
                    try:
                        change_status_arrived(id)
                        blink_log_in_success()

                    except Exception as e:
                        print(e)
                        blink_error()

                if status==1:
                    print("already logged in")
                    blink_log_in_success()
                    blink_log_in_success()

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False, host="0.0.0.0")).start()
    do_my_stuff()

#flask run --host=0.0.0.0