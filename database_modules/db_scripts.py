"""This module contains SQLite script strings, used by various parts of the program."""

# initialization check script - used to initialize the database tables
USER_DB_INIT_CHECK_SCRIPT = """
CREATE TABLE IF NOT EXISTS users(
    user_id VARCHAR PRIMARY_KEY,
    username VARCHAR,
    name VARCHAR,
    email VARCHAR,
    password_hash VARCHAR
);
"""

# script used to add a user record into the database.
# -entry values will be provided as parameters
CREATE_USER_SCRIPT_TEMPLATE = """INSERT INTO users
    (user_id, username, name, email, password_hash)
VALUES
    ( ? , ? , ?, ?, ?);"""

UPDATE_USER_PASSWORD_HASH = """
UPDATE users
SET password_hash = ?
WHERE user_id = ?;
"""

# script used to get a record by username (if it exists)
# -also used to check if someone registered under a username already.
# -username will be provided as a parameter.
GET_USER_RECORD_BY_USERNAME_TEMPLATE = """
SELECT * FROM users
WHERE username = ?"""


# script used to initialize a user database (to store reminders)
INITIALIZE_USER_REMINDER_DB = """
CREATE TABLE IF NOT EXISTS reminders(
    reminder_id VARCHAR PRIMARY_KEY,
    due_date VARCHAR,
    title VARCHAR,
    tags VARCHAR,
    description VARCHAR
);
"""

# script used to add a reminder to a user database
INSERT_NEW_REMINDER = """
INSERT INTO reminders
    (reminder_id, due_date, title, tags, description)
VALUES
    ( ? , ? , ? , ? , ? );"""

# script used to identify reminder entries that are within a certain number
# of hours from the present
# -hour number is filled in where ? is.
GET_REMINDERS_BY_DATETIME = """
SELECT *
FROM reminders
WHERE ((JULIANDAY(due_date) - JULIANDAY('now', 'localtime')) * 24 <= ? AND
    (JULIANDAY(due_date) - JULIANDAY('now', 'localtime')) * 24 > 0);
"""

# when this script is run, all reminders that are over 3 days old will be
# removed.
EXPIRED_REMINDER_AUTODELETE_SCRIPT = """
DELETE FROM reminders WHERE (JULIANDAY('now', 'localtime') - JULIANDAY(due_date)) > 3;
"""

GET_PAST_REMINDERS = """
SELECT *
FROM reminders
WHERE (JULIANDAY('now', 'localtime') - JULIANDAY(due_date)) * 24 > 0;
"""

INITIALIZE_FAILED_SIGNIN_LOG_DB = """
CREATE TABLE IF NOT EXISTS failed_logins(
    event_id VARCHAR PRIMARY_KEY,
    event_datetime VARCHAR,
    event_ip_address VARCHAR)
"""

# this script deletes old entries from the signin log (over a week old)
# to avoid the database growing out of control. If needed the webmaster
# can make a backup of the sign-in log before the 1-week deadline.
DELETE_OLD_SIGNIN_ENTRIES = """
DELETE FROM failed_logins WHERE (JULIANDAY('now', 'localtime') - JULIANDAY(event_datetime)) > 7
"""

# this script adds a login attempt to the
RECORD_LOGIN_ATTEMPT = """
INSERT INTO failed_logins
    (event_id, event_datetime, event_ip_address)
VALUES
    ( ? , ? , ? );"""
