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


#zeigt alle angemeldeten Nutzer
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    print(posts[0]['title'])
    return render_template('status.html')

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

    while(1):
        id,_=reader.read()

        if id:
            print(f'card detected: {id}')
            GPIO.output(LED_PIN_GREEN,GPIO.HIGH)
            sleep(2)
            GPIO.output(LED_PIN_GREEN, GPIO.LOW)



if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()
    do_my_stuff()

#flask run --host=0.0.0.0