"""This module contains the session manager (which manages access to the user
session information dictionary) and contains a class used to define a container
object, which stores a user's session data including authentication token
and page variables."""

from dataclasses import dataclass
import datetime
from passlib.hash import sha256_crypt
from webpage_modules import user_homepage_module

# dictionary, which associates session IDs for different users (keys) with
# corresponding usersessioncontainer objects (values), which store data
# related to a user session.
USER_SESSION_CONTAINER_DICTIONARY = {}

@dataclass
class UserSessionContainer:
    """This class is a container for information for a particular user's session."""
    # constructor
    def __init__(self, user_id, user_session_token, jinja_var_dict):
        self.user_id = user_id
        self.user_auth_token = user_session_token
        self.jinja_page_var_dict = jinja_var_dict

def initialize_user_session_container(user_id, password_hash, username, person_name, request_ip):
    """This function creates a user session container (used to store user session
    data), initializes the page jinja variable dictionary, and returns a session
    token (sent to client browser, and used to retrieve the session container
    information)."""

    # generate session token (combine user ID, password hash and current time and hash it)
    # -hasher will add random salt
    raw_session_token = str(user_id) + str(password_hash) + str(datetime.datetime.now())
    # -hash using sha256 hasher
    session_token = sha256_crypt.hash(raw_session_token)
    # generate ip hashed session token (used as key in USER_SESSION_CONTAINER_DICTIONARY)
    # -client is sent the unhashed (pre-IP hashed) session token
    # -when client sends the unhashed session token back, the server hashes it with the
    #  response IP address. If there is a match in the session container dictionary, the
    #  request was valid (sent back by the user it was issued to)
    ip_hashed_session_token = sha256_crypt.hash(str(session_token) + str(request_ip))

    # populate a UserSessionContainer (initialize with homepage jinja variables)
    new_user_session_container = UserSessionContainer(user_id, ip_hashed_session_token,
        user_homepage_module.init_jinja_var_dictionary())

    # add to USER_SESSION_CONTAINER_DICTIONARY
    USER_SESSION_CONTAINER_DICTIONARY[session_token] = new_user_session_container

    # populate the jinja variable dictionary with user-specific information
    USER_SESSION_CONTAINER_DICTIONARY[session_token].jinja_page_var_dict["Username"] = username
    USER_SESSION_CONTAINER_DICTIONARY[session_token].jinja_page_var_dict["Name"] = person_name
    USER_SESSION_CONTAINER_DICTIONARY[session_token].jinja_page_var_dict["SessionID"] = (
        session_token)

    # return the session token (the pre-ip hashed token)
    return session_token

def get_user_session_page_jinja_vars(user_session_id):
    """This function returns the jinja page variable dictionary for a given
    authenthication token (passed in as a URL variable)"""
    # check if user session ID is in dictionary
    if user_session_id in USER_SESSION_CONTAINER_DICTIONARY:
        # return the page variable dictionary for the given session ID
        return USER_SESSION_CONTAINER_DICTIONARY[user_session_id].jinja_page_var_dict
    # return None if user session ID is not in the user session container dictionary
    return None

def get_user_id_from_session_id(user_session_id):
    """This function returns the ID number of a user given a session ID.
    However, if the session ID is invalid (not on file), None is returned."""
    if user_session_id in USER_SESSION_CONTAINER_DICTIONARY:
        # session ID is valid; return user ID
        return USER_SESSION_CONTAINER_DICTIONARY[user_session_id].user_id
    # session ID is invalid; return none
    return None

def is_session_id_valid(response_session_id, response_ip_address):
    """This function checks if a session ID (supplied in the response_session_id
    parameter), when hashed with the response_ip_address, is in the user session
    container dictionary. Returns the result as a boolean."""

    # first, identify if session id is a key of the session container dictionary
    if response_session_id in USER_SESSION_CONTAINER_DICTIONARY:
        # declare function variables
        hash_string = str(response_session_id) + str(response_ip_address)
        ip_hashed_token = USER_SESSION_CONTAINER_DICTIONARY[response_session_id].user_auth_token
        # check if hash string matches ip_hashed_token, and return response
        return bool(sha256_crypt.verify(hash_string, ip_hashed_token))

    # response session ID didn't match anything on file; return false
    return False

def log_user_out(response_session_id):
    """This function logs out a user by deleting their current session container
    from the session container dictionary, and handles any other login-related
    actions."""
    del USER_SESSION_CONTAINER_DICTIONARY[response_session_id]
