DROP TABLE IF EXISTS user_accounts;
DROP TABLE IF EXISTS rpi;
DROP TABLE IF EXISTS access_attemps;
DROP TABLE IF EXISTS whitelists;
DROP TABLE IF EXISTS plates;
DROP TABLE IF EXISTS whitelist_assignment;
DROP TABLE IF EXISTS log_session;
DROP TABLE IF EXISTS active_rpi;

PRAGMA foreign_keys = ON;

CREATE TABLE user_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE rpi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_id TEXT NOT NULL UNIQUE,
    user_id INTEGER NULL,
    FOREIGN KEY (user_id) REFERENCES user_accounts (id)
);

CREATE TABLE access_attemps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo BLOB NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rpi_id INTEGER NOT NULL,
    FOREIGN KEY (rpi_id) REFERENCES rpi (id)
);

CREATE TABLE log_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rpi_id INTEGER NOT NULL,
    log TEXT NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(rpi_id) REFERENCES rpi (id)
);

CREATE TABLE active_rpi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rpi_id INTEGER NOT NULL UNIQUE,
    sid TEXT NOT NULL,
    FOREIGN KEY (rpi_id) REFERENCES rpi (id)
);

CREATE TABLE whitelists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_accounts (id)
);

CREATE TABLE plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT NOT NULL
);

CREATE TABLE whitelist_assignment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_id INTEGER NOT NULL,
    whitelist_id INTEGER NOT NULL,
    FOREIGN KEY (plate_id) REFERENCES plates(id),
    FOREIGN KEY (whitelist_id) REFERENCES whitelists(id)
);
