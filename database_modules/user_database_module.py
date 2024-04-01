"""This module contains functions related to accessing/updating the user
information database."""

import server_constants
from database_modules import db_scripts, database_access_module


def does_user_exist(user_name):
    """This function checks if a user already exists in the program database,
    returning a boolean indicating the result."""

    # declare function variables
    # -construct the username check script by appending the username to the script template.

    # run the query, store the result (which is either None if no entry exists, or 1 if
    # an entry exists)
    query_data = database_access_module.perform_db_query(server_constants.USERS_INFO_DB_NAME,
        "Does_Username_Exist_Check", db_scripts.GET_USER_RECORD_BY_USERNAME_TEMPLATE,
                                                         [user_name]).fetchone()

    # return result of check of query_data being none (indicating that username isn't taken)
    # -function returns false if query data is none (indicating that  user doesn't exist)
    # -function returns true if query data exists (indicating user exists)
    return bool(query_data is not None)

def get_user_record(user_name):
    """This function runs a query on the user information database, searching for a
    record that contains the username specified in the 'user_name' parameter, and
    returns it."""

    # run the query, store the result
    query_data = database_access_module.perform_db_query(server_constants.USERS_INFO_DB_NAME,
        "Does Username Exist Check", db_scripts.GET_USER_RECORD_BY_USERNAME_TEMPLATE,
                                                         [user_name]).fetchone()
    return query_data

def update_user_password_hash(user_id, new_password_hash):
    """This function updates the password hash for the user whose ID number is
    user_id. This should ONLY be called by the 'try_update_user_password' function."""
    database_access_module.perform_db_query(server_constants.USERS_INFO_DB_NAME,
        "Update user password hash", db_scripts.UPDATE_USER_PASSWORD_HASH,
                                            [new_password_hash, user_id])
