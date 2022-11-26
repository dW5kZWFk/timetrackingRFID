CREATE TABLE employee_state (uid integer primary key not null, start_time [timestamp], name text not null, state text not null);
CREATE TABLE working_time (id integer primary key not null key autoincrement, employee_uid integer not null, date text not null, time text not null, FOREIGN KEY(employee_uid) REFERENCES employee_state(uid));

55396084254