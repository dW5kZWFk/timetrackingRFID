#!/usr/bin/env python3
import csv
import os
import threading
from datetime import datetime, timedelta

from flask import Flask, request, send_file, jsonify, Response, flash, redirect
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
    sleep(3)
    GPIO.output(LED_PIN_RED, GPIO.LOW)
    return


#green led on for 2 sec
def blink_log_in_success():
    GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
    sleep(3)
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


def blink_error_endless():
    while (1):
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(LED_PIN_RED, GPIO.LOW)
        sleep(0.5)


#red and green blink 5 times
def blink_unregistered():
    for i in range(0, 5):
        GPIO.output(LED_PIN_RED, GPIO.HIGH)
        GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(LED_PIN_RED, GPIO.LOW)
        GPIO.output(LED_PIN_GREEN, GPIO.LOW)
        sleep(0.5)
    return


#views........................................................................................

#display employees currently at work
#display info color code leds
@app.route('/')
def index():
    conn = get_db_connection()
    sql = f'SELECT name FROM employee_state WHERE state==1'
    cur = conn.cursor()
    rows = cur.execute(sql).fetchall()
    conn.close()
    return render_template('state.html', names=rows)


@app.route('/YWRtaW4', methods=['GET', 'POST'])
def admin_view():
    if request.method == "POST" and "reset_worktime" in "request_form":
        conn = get_db_connection()
        sql = f'DELETE * from working_time'
        cur = conn.cursor()
        rows = cur.execute(sql).fetchall()
        conn.close()
        flash("Arbeitszeiten zurückgesetzt.", 'success')
        return redirect("admin.html")

    return render_template('admin.html')


#ajax-csv-functions.............................................................................
@app.route('/create_csv_ajax', methods=['GET'])
def create_csv_ajax():
    conn = get_db_connection()
    sql = f'SELECT date, name, time from working_time left join employee_state on working_time.employee_uid = employee_state.uid'
    cur = conn.cursor()
    rows = cur.execute(sql).fetchall()
    conn.close()

    col_labels = ['Datum', 'Name', 'Arbeitszeit']

    #write csv:
    with open('working_time_export.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(col_labels)
        for row in rows:
            csvwriter.writerow(row)

    return jsonify("success")


@app.route('/working_time', methods=['GET'])
def download_working_time_csv():
    with open("working_time_export.csv", "r") as fp:
        csv = fp.read()
    return Response(csv, mimetype="text/csv")


#RFID functions..................................................................................
#check whether employee is logged in or logged out
def check_state(uid):
    conn = get_db_connection()
    sql = f'SELECT state FROM employee_state WHERE uid=={uid}'

    cur = conn.cursor()
    rows = cur.execute(sql).fetchone()
    conn.close()

    if rows is None:  #unregistered tag-ID
        return 'empty'

    return rows[0][0]


#log in / out..............................................................................................

#changes employee state to (-> currently at work (1) / currently not at work (0))
def change_employee_state(uid, new_state):
    conn = get_db_connection()

    sql = f'UPDATE employee_state set state = {new_state}, start_time=DateTime(\'now\',\'localtime\') WHERE uid=={uid}'

    print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    return 0


def log_out(uid):
    #get start time
    conn = get_db_connection()
    sql = f'SELECT datetime(start_time) FROM employee_state WHERE uid=={uid}'

    cur = conn.cursor()
    rows = cur.execute(sql).fetchall()
    start_time = rows[0][0]

    #calculate work hours
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")  # str to datetime
    end_dt = datetime.now()
    print(start_dt)
    print(end_dt)
    work_hours = end_dt.replace(second=0, microsecond=0) - start_dt.replace(second=0,
                                                                            microsecond=0)  #rounded difference
    #work_hours=end_dt-start_dt
    today = datetime.today().strftime('%d.%m.%Y')

    print(f'work_hours:{work_hours}')
    print(f'today:{today}')

    #write to db
    sql = f'INSERT INTO working_time (employee_uid,date,time) values({uid},\'{today}\',\'{work_hours}\')'
    cur.execute(sql)
    conn.commit()
    conn.close()

    #change employee state
    try:
        change_employee_state(uid, 0)
    except Exception as e:
        raise Exception

    return


#main loop..............................................................................................
def rfid_loop():
    print("scanning for cards")
    #register rfid scanner
    reader = SimpleMFRC522()

    #register leds
    #SimpleMFRC522 uses GPIO BOARD Mode !

    GPIO.setup(LED_PIN_GREEN, GPIO.OUT)
    GPIO.setup(LED_PIN_RED, GPIO.OUT)

    #toDo: following two lines should not be necessary
    #(currently necessary for main looop crash exception if it's not handled via reboot)
    GPIO.output(LED_PIN_GREEN, GPIO.LOW)
    GPIO.output(LED_PIN_RED, GPIO.LOW)

    try:
        while (1):
            id, _ = reader.read()

            if id:
                print(f'card detected: {id}')
                state = check_state(id)

                if state == '0':  #proceed with log in
                    try:
                        change_employee_state(id, 1)
                        blink_log_in_success()

                    except Exception as e:
                        print(e)
                        blink_error()

                elif state == '1':  #proceed with log out
                    try:
                        log_out(id)
                        blink_log_out_success()
                    except Exception as e:
                        print(e)
                        blink_error()

                elif state == 'empty':  #tag is not registered
                    blink_unregistered()
                    return -1


    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False, host="0.0.0.0")).start()

    try:
        rfid_loop()
    except Exception as e:
        blink_error_endless()

#flask run --host=0.0.0.0
