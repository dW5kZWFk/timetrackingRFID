# TimetrackingRFID

This project provides a simple solution for tracking working hours using a Raspberry Pi in combination with an RFID Reader.

## Usage

### Log in /out
Users can log in and out by scanning RFID tags. LED indicators provide immediate feedback on successful login and logout actions through RFID tag recognition.
A list of currently logged-in users is displayed on a small locally hosted website.
 
### Receive working hours
An working hour entry is created and saved to the database after the user logs out successfully. Entries can be downloaded from the local web server at "/YWRtaW4"  which is password protected. 

## Getting started

<ol>
	<li> provide admin name and password hash in app.py <br>
(https://flask-httpauth.readthedocs.io/en/latest/) <br> <br> </li>

<li> create sqlite database as described in "schema.sql" and register RFID-tags:

example: 
INSERT INTO employee_state (uid, name, state) VALUES (53531515, user1, 0);

<ul>
	<li>UID has to be equal to RFIDTag-ID </li>
	<li>choose name</li> 
  <li>set state = 0</li> 
</ul>

</li>

<li> 
deploy server(https://flask.palletsprojects.com/en/2.3.x/deploying/) <br>
(flask run --host=0.0.0.0 can be used for testing purpose)
</li>
</ol>

## Built with
<ul>
	<li>Python-Flask https://flask.palletsprojects.com/en/2.3.x/</li>
<li>SimpleMFRC522 https://docs.sunfounder.com/projects/davinci-kit/en/latest/2.2.7_mfrc522_rfid_module.html </li>
</ul>
