"""This module contains functions related to accessing/initializing databases for the website."""

import sqlite3
from sqlite3 import Error
import server_constants
from database_modules import db_scripts, database_access_module

# Dictionary that contains connection objects to various databases.
# -The key is the database name
# -The value is the connection object
DATABASE_CONNECTION_DICTIONARY = {}
DB_DIRECTORY_ROOT = ""

def connect_to_website_databases(db_directory_root, db_names):
    """This function populates the DATABASE_CONNECTION_DICTIONARY with connection objects
    to the databases used by the website. Returns true if all databases initialized
    successfully, false if not.

    db_directory_root is the folder path to the directory that contains all the databases.
    db_names is a list containing the database names (the file names specifically, excluding
    the file extension)"""

    database_access_module.DB_DIRECTORY_ROOT = db_directory_root

    # reset the dictionary (in case calling this function after dictionary was initialized)
    DATABASE_CONNECTION_DICTIONARY.clear()

    for db_name in db_names:
        # try getting connection to database
        db_connection = try_get_database_connection(
            db_directory_root + "\\" + db_name + ".sqlite", db_name)

        # check if database connection was successful (db_connection not null)
        if db_connection is not None:
            # add to dictionary
            DATABASE_CONNECTION_DICTIONARY[db_name] = db_connection

    # run the db initialization check
    run_db_init_check()


def run_db_init_check():
    """This function runs the database initialization check scripts, which are scripts run
    at startup that ensure that the databases are initialized with the required tables if
    any are missing (or database file was newly created)."""

    # run the user database initialization script
    perform_db_query(server_constants.USERS_INFO_DB_NAME, "Initialization check script, user db",
                     db_scripts.USER_DB_INIT_CHECK_SCRIPT, None)

    # run the failed sign in log database initialization script
    perform_db_query(server_constants.LOGIN_LOG_DB_NAME, "Initialization check script, log in db",
                     db_scripts.INITIALIZE_FAILED_SIGNIN_LOG_DB, None)


def perform_user_reminder_db_query(user_id, query_name, query_string, query_parameters):
    """This function attempts to perform/commit a database query (query_string) on the reminder
    database for the user with the user id specified (in the user_id parameter), and returns the
    results of the query. If query is unsuccessful, None is returned."""

    # -get connection to user database (or create it if doesn't exist)
    # try getting connection to database
    db_connection = try_get_database_connection(
        database_access_module.DB_DIRECTORY_ROOT + "\\" + user_id + ".sqlite", "user "
        + user_id + " reminder")

    # check if database connection was successful (db_connection not null)
    if db_connection is not None:
        # made a successful connection to the user's database
        # -get a cursor to the database
        cursor = db_connection.cursor()
        # try performing the query
        try:
            # declare variable to hold query results
            query_results = None

            # run the initialization/check script to ensure the user database has
            # the required tables
            cursor.execute(db_scripts.INITIALIZE_USER_REMINDER_DB)
            # commit results
            db_connection.commit()

            # run old query auto-delete script, as well as main query as parametric query
            if query_parameters is not None:
                cursor.execute(db_scripts.EXPIRED_REMINDER_AUTODELETE_SCRIPT)
                query_results = cursor.execute(query_string, query_parameters)
            else:
                cursor.execute(db_scripts.EXPIRED_REMINDER_AUTODELETE_SCRIPT)
                query_results = cursor.execute(query_string)

            # commit results to database.
            db_connection.commit()

            # print query success message
            print("Successfully performed '" + query_name + "' query on reminder database "
                  + "for user " + user_id)
            # return query results
            return query_results

        except Error as exception:
            # print error message
            print("Error occurred trying to perform query '" + str(query_name)
                  + "' on reminder database for user "  + str(user_id))
            print(str(exception))
            return None
    else:
        # should only occur due to file/io error
        print("Error! Unable to access reminder database for user " + user_id + "!")
        return None


def perform_db_query(db_name, query_name, query_string, query_parameters):
    """This function attempts to perform/commit a database query (query_string) on the specified
    database (db_name), and returns the results of the query. If query is unsuccessful, None is
    returned."""

    # ensure database name exists
    if db_name in DATABASE_CONNECTION_DICTIONARY:  #.keys()
        # get cursor object, used to execute query
        cursor = DATABASE_CONNECTION_DICTIONARY[db_name].cursor()
        # try performing the query
        try:
            # declare variable to hold query results
            query_results = None

            # run query as parametric query
            if query_parameters is not None:
                query_results = cursor.execute(query_string, query_parameters)
            else:
                query_results = cursor.execute(query_string)

            # commit results to database.
            DATABASE_CONNECTION_DICTIONARY[db_name].commit()

            # print query success message
            print("Successfully performed '" + query_name + "' query on database " + db_name)
            # return true - query performed
            return query_results

        except Error as exception:
            # print error message
            print("Error occurred trying to perform query '" + str(query_name) + "' on database "
                  + str(db_name))
            print(str(exception))
    else:
        # print error message
        print("Unable to perform query - no database named '" + db_name + "' exists!")

    # return false; query not performed
    return None

def try_get_database_connection(db_path, db_name):
    """This function tries to connect to an sqlite database at the specified path, and
     returns the connection if successful. If connection is unsuccessful, None is
     returned."""

    # declare connection variable
    db_connection = None

    # try connecting to the database
    try:
        db_connection = sqlite3.connect(db_path,check_same_thread=False)
        print("Connected to " + db_name + " database.")
    except Error as exception:
        # print error message and exception
        print("Error occurred while trying to connect to the " + db_name + " database!")
        print(str(exception))

    # no matter what happens, return the connection object
    # -if no connection succeeded, returns null. Otherwise returns the
    # connection object.
    return db_connection
