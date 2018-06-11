drop table if exists users;
create table users (
  id integer primary key autoincrement,
  login text not null,
  password text not null,
  email text not null,
  telegram text,
  name text not null,
  status text not null
);

drop table if exists check_users;
create table check_users (
  id integer primary key autoincrement,
  login text not null,
  type text not null,
  status text not null,
  check_hash text not null
);

drop table if exists tasks;
create table tasks (
  id integer primary key autoincrement,
  login text not null,
  title text not null,
  description text not null,
  content mediumtext not null,
  max_people integer not null,
  now_people integer,
  date date not null,
  deadline date not null,
  subject text not null
);

drop table if exists works;
create table works (
  id integer primary key autoincrement,
  login text not null,
  content mediumtext not null,
  task integer not null
);

drop table if exists adds;
create table adds (
  name text not null,
  content text not null,
  url text not null  
);





