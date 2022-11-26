new_reader = SimpleMFRC522()
#destroy rfid loop
stop_scanner = True
GPIO.setmode(GPIO.BOARD)
#toDO: check for existing names
try:
    while (1):
        print("huh")
        GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(LED_PIN_GREEN, GPIO.LOW)
        sleep(0.5)
        try:
            new_id, _ = new_reader.read()
            print(id)
        except Exception as e:
            print(e)
            blink_error()

        if new_id:
            #prüfen ob Tag-ID bereits vergeben ist
            if check_state(new_id) != "empty":
                flash("Tag/Karte ist bereits registriert", "danger")
            #toDo: Prüfen, ob Name bereits vergeben ist

            else:
                conn = get_db_connection()
                cur = conn.cursor()
                name = request.form.get("employee_name")
                sql = f'INSERT INTO working_time (employee_uid,date,time) values(?)'
                cur.execute(sql, (name))
                conn.commit()
                conn.close()
                flash(f'Tag/Karte wurde für {name} registriert.', "success")

            #restart rfid loop:
            GPIO.cleanup()
            stop_scanner = False
            rfid_loop()
            return redirect("register.html")


except Exception as e:
    print(e)
    GPIO.cleanup()
    stop_scanner = False
    rfid_loop()
    flash("Unspezifische Fehlermeldung (register user Loop).", "danger")