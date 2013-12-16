CREATE TABLE if not exists users (user text PRIMARY KEY, password text, emails text);
CREATE TABLE if not exists grades (user text, test text, grade real, report integer, upload text, timestamp datetime);
CREATE TABLE if not exists reports (id integer primary key, detail text);
CREATE TABLE if not exists configuration (key text primary key, value text);
