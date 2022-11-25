CREATE TABLE employee_state (id int primary key, uid int not null, start_time [timestamp], name text, state text);
CREATE TABLE working_time (id int, uid int, date text, time text);
