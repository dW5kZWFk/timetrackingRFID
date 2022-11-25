#!/usr/bin/env python3
import threading
from datetime import datetime, timedelta

from flask import Flask
from flask import render_template
import sqlite3
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
from time import sleep, strptime

app = Flask(__name__)

LED_PIN_GREEN = 11  #17 BCM
LED_PIN_RED = 13  #27 BCM

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


#blink codes.................................................................................
#red led on for 2 sec
def blink_log_out_success():
    GPIO.output(LED_PIN_RED, GPIO.HIGH)
    sleep(2)
    GPIO.output(LED_PIN_RED, GPIO.LOW)
    return


#green led on for 2 sec
def blink_log_in_success():
    GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
    sleep(2)
    GPIO.output(LED_PIN_GREEN, GPIO.LOW)
    return


#red led blinks 10 times
def blink_error():
    for i in range(0, 10):
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(LED_PIN_RED, GPIO.LOW)
        sleep(0.5)
    return

#views........................................................................................

#display employees currently at work
#display info color code leds
@app.route('/')
def index():

    return render_template('state.html')


#check whether employee is logged in or logged out
def check_state(uid):
    conn = get_db_connection()
    sql = f'SELECT state FROM employee_state WHERE uid=={uid}'

    cur = conn.cursor()
    rows=cur.execute(sql).fetchall()
    conn.close()

    return rows[0][0]

#log in / out..............................................................................................

#changes employee state to (-> currently at work (1) / currently not at work (0))
def change_employee_state(uid, state):
    conn = get_db_connection()

    sql = f'UPDATE employee_state set state = {state}, start_time=DateTime(\'now\') WHERE uid=={uid}'
    print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    return 0


def log_out(uid):

    #change employee state
    try:
        change_employee_state(uid, 0)
    except Exception as e:
        raise Exception

    #get start time
    conn = get_db_connection()
    sql = f'SELECT start_time FROM employee_state WHERE uid=={uid}'

    cur = conn.cursor()
    rows = cur.execute(sql).fetchall()
    start_time=rows[0][0]

    #calculate work hours
    start_dt=datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") # str to datetime
    end_dt= datetime.now()

    work_hours= start_dt.replace(second=0, microsecond=0) - end_dt.replace(second=0,microsecond=0)  #rounded difference
    today=datetime.today().strftime('%d.%m.%Y')

    print(f'work_hours:{work_hours}')
    print(f'today:{today}')
    #write to db
    return

#main loop..............................................................................................
def do_my_stuff():
    print("scanning for cards")
    #register rfid scanner
    reader = SimpleMFRC522()

    #register leds
    #SimpleMFRC522 uses GPIO BOARD Mode !

    GPIO.setup(LED_PIN_GREEN, GPIO.OUT)
    GPIO.setup(LED_PIN_RED, GPIO.OUT)

    #toDo: following two lines should not be necessary
    GPIO.output(LED_PIN_GREEN, GPIO.LOW)
    GPIO.output(LED_PIN_GREEN, GPIO.LOW)

    try:
        while(1):
            id,_=reader.read()

            if id:
                print(f'card detected: {id}')
                state=check_state(id)

                if state=='0':
                    try:
                        change_employee_state(id, 1)
                        blink_log_in_success()

                    except Exception as e:
                        print(e)
                        blink_error()

                if state=='1':
                    try:
                        log_out(id)
                        blink_log_in_success()
                    except Exception as e:
                        print(e)
                        blink_error()


    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False, host="0.0.0.0")).start()
    do_my_stuff()

#flask run --host=0.0.0.0