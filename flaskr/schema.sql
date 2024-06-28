-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  administrator INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE category (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE pcb (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  name TEXT NOT NULL,
  view_num INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE pcb_category (
  pcb_id INTEGER NOT NULL,
  category_id INTEGER NOT NULL,
  FOREIGN KEY (pcb_id) REFERENCES pcb (id),
  FOREIGN KEY (category_id) REFERENCES category (id),
  PRIMARY KEY (pcb_id, category_id)
);

