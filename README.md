# TimetrackingRFID

This project provides a simple solution for tracking working hours using a Raspberry Pi in combination with an RFID Reader.

### Log in / out
Users can log in and out by scanning RFID tags. LED indicators provide immediate feedback on successful login and logout actions through RFID tag recognition.
A list of currently logged-in users is displayed on a small locally hosted website.
 
### Receive working hours
An working hour entry is created and saved to the database after the user logs out successfully. Entries can be downloaded from the local web server at "/YWRtaW4"  which is password protected. 

## Built with
<ul> <li> 
	
Frameworks/Libraries: [Flask](https://flask.palletsprojects.com/en/2.3.x/), [MFRC522-python](https://github.com/pimylifeup/MFRC522-python/tree/master) </li>

<li>
	
Database: SQLite </li>

<li>
	
Hardware: Raspberry Pi, RC522 RFID reader </li> 
</ul>

## Hardware Setup
One possible configuration includes the Raspberry Pi Zero (other Pi versions are compatible as well) in conjunction with the RC522 RFID reader and multiple RFID tags. 
Connect the RC522 reader as instructed in the image below. Then attach a green LED to pin 13 (BOARD) and another red LED to pin 11 (BOARD).

![PiZero_FRID-RC522_Steckplatine_small](https://github.com/dW5kZWFk/timetrackingRFID/assets/100794989/5603c887-47f2-4dbc-bbad-dbc703791b85)

## Getting started

<ol>
	<li> 
		
Provide an admin name and corresponding password hash in the 'app.py'-file. ([flask-httpauth](https://flask-httpauth.readthedocs.io/en/latest/))
</li>

<li> 
	
Next, [create an SQLite database](https://github.com/dW5kZWFk/timetrackingRFID/blob/master/schema.sql) and proceed to register the RFID-tags by executing the following SQL query:
	
```INSERT INTO employee_state (uid, name, state) VALUES (53531515, user1, 0);```

(Choose a username and assign a UID that corresponds to the RFIDTag-ID.)

</li>

<li> 
	
[Deploy the server](https://flask.palletsprojects.com/en/2.3.x/deploying/). For testing purposes, you can use the following command: <br> ```flask run --host=0.0.0.0```
</li>
</ol>


