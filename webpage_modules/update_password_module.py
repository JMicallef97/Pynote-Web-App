"""This module contains code related to the 'update password' page of the website,
including password validation and user information database updates."""
from webpage_modules import registration_module, update_password_module
import user_session_manager_module
from database_modules import user_database_module

PAGE_BANNER_MESSAGE = ("Passwords are like habits - hard to change but sometimes it needs "
                       "to happen.")
PASSWORD_DESCRIPTOR = ("Please enter a different password than your current one. It must "
                       "be at least 12 characters long, and must include at least 1 uppercase "
                       "letter, 1 lowercase letter, 1 number and 1 special character. All "
                       "whitespace characters will be removed and not count towards the "
                       "password length.")
PASSWORD_REPEAT_DESCRIPTOR = "Please re-enter the password you typed."
PASSWORD_TB_BACKCOLOR = "#ffffff"
PASSWORD_REPEAT_TB_BACKCOLOR = "#ffffff"

MOST_COMMON_PASSWORD_LIST = []

def try_update_user_password(new_password, repeated_password, session_id, page_jinja_variables):
    """This function checks the password the user entered (and the repeated password)
    against basic password requirements, as well as NIST SP 800-63B criteria. If the
    password passes all checks, the user's password will be updated in the user information
    database. If not, an error message will be returned in the page_jinja_variables
    dictionary."""

    # check if passwords don't match
    if new_password != repeated_password:
        # update error message, return page
        page_jinja_variables["BANNER_MESSAGE"] = ("Error! The passwords you entered don't"
            " match, please try again.")
        return page_jinja_variables

    # check if new password matches original requirements (12 characters, at least 1 character
    # from each category)
    if not registration_module.is_password_valid(new_password):
        # update error message, return page
        page_jinja_variables["BANNER_MESSAGE"] = ("Password is invalid! Please ensure "
             "you follow all password criteria when making a password.")
        return page_jinja_variables

    # check if password is on list of most common passwords (loaded from CommonPasswords.txt)
    if new_password in MOST_COMMON_PASSWORD_LIST:
        # update error message, return page
        page_jinja_variables["BANNER_MESSAGE"] = ("Your password is too common to be used,"
            " please pick another one.")
        return page_jinja_variables

    # if this point reached, all checks passed
    # -update password in user information
    # -firstly, need to get user ID from session ID (contact user session manager module for it)
    user_id = user_session_manager_module.get_user_id_from_session_id(session_id)
    # -next, get password hash (contact registration module for it)
    new_password_hash = registration_module.compute_password_hash(new_password, user_id)
    # -finally, store the new password hash in the database by running a query
    user_database_module.update_user_password_hash(str(user_id), str(new_password_hash))

    # update error message, return page
    page_jinja_variables["BANNER_MESSAGE"] = ("Your password has been changed!"
        " Click 'cancel' to return to the homepage.")
    return page_jinja_variables

def try_load_most_common_passwords(most_common_passwords_filepath):
    """This function tried to load the most common passwords into a list in
    the server program, from the file at the specified filepath. If it fails,
    it prints an error message indicating the problem."""

    try:
        with open(most_common_passwords_filepath, 'r', encoding='utf-8') as file:
            # read file lines into program
            update_password_module.MOST_COMMON_PASSWORD_LIST = file.readlines()

            # strip newline characters off items
            update_password_module.MOST_COMMON_PASSWORD_LIST = [item.strip()
                for item in update_password_module.MOST_COMMON_PASSWORD_LIST]

    except FileNotFoundError:
        print("Error - unable to access CommonPasswords.txt. Server restart recommended!")

def init_jinja_var_dictionary():
    """This function initializes default values for the page's jinja dictionary.
    Note: this function should only be run once, when the web server is initially
    launched."""
    page_jinja_variable_dictionary = {}
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = PAGE_BANNER_MESSAGE
    page_jinja_variable_dictionary["USERNAME_DESCRIPTOR"] = PASSWORD_DESCRIPTOR
    page_jinja_variable_dictionary["PASSWORD_DESCRIPTOR"] = PASSWORD_REPEAT_DESCRIPTOR
    page_jinja_variable_dictionary["USERNAME_TB_BACKCOLOR"] = PASSWORD_TB_BACKCOLOR
    page_jinja_variable_dictionary["PASSWORD_TB_BACKCOLOR"] = PASSWORD_REPEAT_TB_BACKCOLOR
    return page_jinja_variable_dictionary
