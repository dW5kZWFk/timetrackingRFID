CREATE TABLE employee_state (uid int primary key, start_time [timestamp], name text, state text);
CREATE TABLE working_time (id int, employee_uid int, date text, time text, FOREIGN KEY(employee_uid) REFERENCES employee_state(uid));

