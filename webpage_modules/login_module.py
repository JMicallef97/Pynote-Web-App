"""This module handles functionality relating to the user login page."""
import uuid
import datetime
from passlib.hash import sha256_crypt
import server_constants
from database_modules import db_scripts, database_access_module, user_database_module

DEFAULT_PAGE_BANNER_MSG = ("Pynote is a locally-hosted reminder app, developed by Jacob Micallef"
" using the Flask web framework.")

def authenticate_user_login(username, password, ip_address):
    """This function checks if the username and password parameters
    match an entry in the database, and returns a dictionary containing
    jinja variables for the page."""

    # declare variables
    page_jinja_variable_dictionary = {}
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = DEFAULT_PAGE_BANNER_MSG
    # initialize the 'loginPassed' to false (assume that the information is incorrect)
    page_jinja_variable_dictionary["loginPassed"] = False

    # first, check if user exists
    if user_database_module.does_user_exist(username):
        # get user ID (needed to hash with password to get password hash)
        user_db_record = user_database_module.get_user_record(username)
        user_id = user_db_record[0]
        stored_pass_hash = user_db_record[4]
        pass_hash_string = str(user_id) + str(password)

        # check if password_hash matches stored_pass_hash
        #if password_hash == stored_pass_hash:
        if sha256_crypt.verify(pass_hash_string, stored_pass_hash):
            # set message to default banner message
            page_jinja_variable_dictionary["loginPassed"] = True

            # load user information into the jinja dictionary
            page_jinja_variable_dictionary["UserID"] = user_id
            page_jinja_variable_dictionary["PasswordHash"] = stored_pass_hash
            page_jinja_variable_dictionary["Username"] = user_db_record[1]
            page_jinja_variable_dictionary["Name"] = user_db_record[2]
            return page_jinja_variable_dictionary

        # password incorrect
        page_jinja_variable_dictionary["BANNER_MESSAGE"] = ("Error! Your password is "
            "incorrect, please try again or reset it.")

        # run script to delete old (> 1 week) entries in the failed login attempt log, to
        # avoid the file blowing up in size out of control.
        # -if webmaster wants they can make a copy of the database for further analysis,
        # but if database gets too big that will slow the website down.
        database_access_module.perform_db_query(server_constants.LOGIN_LOG_DB_NAME,
                        "Delete old entries, failed sign-in log",
                                                db_scripts.DELETE_OLD_SIGNIN_ENTRIES, None)

        # log entry in failed login database
        database_access_module.perform_db_query(server_constants.LOGIN_LOG_DB_NAME,
            "Record failed login attempt - incorrect password",
                db_scripts.RECORD_LOGIN_ATTEMPT, [str(uuid.uuid4()),
                str(datetime.datetime.now()), str(ip_address)])

        return page_jinja_variable_dictionary

    # username missing
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = ("Error! Your username wasn't "
            "found, please try again or register.")

    # run script to delete old (> 1 week) entries in the failed login attempt log, to
    # avoid the file blowing up in size out of control.
    # -if webmaster wants they can make a copy of the database for further analysis,
    # but if database gets too big that will slow the website down.
    database_access_module.perform_db_query(server_constants.LOGIN_LOG_DB_NAME,
                    "Delete old entries, failed sign-in log",
                                            db_scripts.DELETE_OLD_SIGNIN_ENTRIES, None)

    # log entry in failed login database
    database_access_module.perform_db_query(server_constants.LOGIN_LOG_DB_NAME,
        "Record failed login attempt - unknown username",
            db_scripts.RECORD_LOGIN_ATTEMPT, [str(uuid.uuid4()), str(datetime.datetime.now()),
        str(ip_address)])

    return page_jinja_variable_dictionary

def init_jinja_var_dictionary():
    """This function initializes default values for the page's jinja dictionary.
    Note: this function should only be run once, when the web server is initially
    launched."""
    page_jinja_variable_dictionary = {}
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = DEFAULT_PAGE_BANNER_MSG
    return page_jinja_variable_dictionary
