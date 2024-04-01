"""This module contains code related to the functionality of the 'register' page,
including initializing page jinja variables, validating user input, adding an entry
for the user in the user information database (if the information is correct), and
returning error messages if the user entered invalid data."""
import uuid
import re
from passlib.hash import sha256_crypt
from database_modules import database_access_module, user_database_module, db_scripts
import server_constants

# declare module variables
PAGE_BANNER_MESSAGE = "Join the club!"
USERNAME_DESCRIPTOR = ("Please enter a username that is a minimum of 4 characters and a maximum"
                       " of 20 characters. All whitespace characters will be removed and not count"
                       " towards the password length.")
PASSWORD_DESCRIPTOR = ("Please enter a password that is at least 12 characters long. It must "
                       "include at least 1 uppercase letter, 1 lowercase letter, 1 number and "
                       "1 special character.  All whitespace characters will be removed and not "
                       "count towards the password length.")

NAME_DESCRIPTOR = ("Please enter your name. You can leave this field blank if you'd like to"
                   " remain anonymous.")

EMAIL_DESCRIPTOR = ("Please enter your email address, in case we need to get in touch with you."
                    " Please enter an email formatted like 'johndoe@example.com'.")

# constants
USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 20

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 20

# colors, used to indicate errors in entry
USERNAME_TB_BACKCOLOR = "#ffffff"
PASSWORD_TB_BACKCOLOR = "#ffffff"
EMAIL_TB_BACKCOLOR = "#ffffff"

EMAIL_VALIDATION_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_VALIDATION_REGEX = (re.compile
        (r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&*!])[A-Za-z\d@#$%^&*!]{12,}$'))

def registration_script(request_data):
    """This function is run when the user clicks the 'register' button in the registration
    page, and contains logic for attempting to register the user (or return an error message).
    This function returns a dictionary containing the jinja variables for the page."""
    print("Running user registration script...")

    # declare variables
    # -dictionary used to store jinja variables for page
    page_jinja_variable_dictionary = {}
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = PAGE_BANNER_MESSAGE
    page_jinja_variable_dictionary["USERNAME_DESCRIPTOR"] = USERNAME_DESCRIPTOR
    page_jinja_variable_dictionary["PASSWORD_DESCRIPTOR"] = PASSWORD_DESCRIPTOR
    page_jinja_variable_dictionary["NAME_DESCRIPTOR"] = NAME_DESCRIPTOR
    page_jinja_variable_dictionary["EMAIL_DESCRIPTOR"] = EMAIL_DESCRIPTOR
    # reset textbox colors
    page_jinja_variable_dictionary["USERNAME_TB_BACKCOLOR"] = USERNAME_TB_BACKCOLOR
    page_jinja_variable_dictionary["PASSWORD_TB_BACKCOLOR"] = PASSWORD_TB_BACKCOLOR
    page_jinja_variable_dictionary["EMAIL_TB_BACKCOLOR"] = EMAIL_TB_BACKCOLOR

    # load information from form into variables
    registration_username = str(request_data.form['Username'])
    registration_password = str(request_data.form['Password'])
    registering_person_name = str(request_data.form['Name'])
    registration_email = str(request_data.form['Email'])

    # check if username is invalid
    if not is_username_valid(registration_username):
        # assign reason for registration failure.
        page_jinja_variable_dictionary["BANNER_MESSAGE"] = \
            ("Username is invalid! Please enter a username that is not composed"
            " solely of whitespace characters.")
        # update the color for the username textbox in the jinja dictionary
        page_jinja_variable_dictionary["USERNAME_TB_BACKCOLOR"] = "#e3735d"
        # return result
        return page_jinja_variable_dictionary

    # check if password is invalid
    if not is_password_valid(registration_password):
        # assign reason for registration failure.
        page_jinja_variable_dictionary["BANNER_MESSAGE"] = \
            ("Password is invalid! Please ensure you follow all password criteria"
             " when making a password.")
        # update the color for the username textbox in the jinja dictionary
        page_jinja_variable_dictionary["PASSWORD_TB_BACKCOLOR"] = "#e3735d"
        # return results
        return page_jinja_variable_dictionary

    # check if user email is invalid
    if not is_email_valid(registration_email):
        # user e-mail is invalid, tell user
        # assign reason for registration failure.
        page_jinja_variable_dictionary["BANNER_MESSAGE"] = \
            "E-mail is invalid! Please enter a valid e-mail. Example: 'johndoe@example.com'"
        # update the color for the username textbox in the jinja dictionary
        page_jinja_variable_dictionary["EMAIL_TB_BACKCOLOR"] = "#e3735d"
        return page_jinja_variable_dictionary

    # check if user exists by running a database check
    does_user_exist = user_database_module.does_user_exist(registration_username)
    # check if user doesn't already exist
    if not does_user_exist:
        # registration info is valid and username isn't taken

        # generate user ID
        user_id = str(uuid.uuid4())

        # -salt the user's password with their user ID
        registration_password = compute_password_hash(registration_password, user_id)

        # check if user left their name blank (want to remain anonymous)
        if len(registering_person_name.strip()) == 0:
            # assign "Anonymous" to their name
            registering_person_name = "Anonymous"

        # create a database entry for the user by running the query.
        database_access_module.perform_db_query(server_constants.USERS_INFO_DB_NAME,
            'Register_New_User', db_scripts.CREATE_USER_SCRIPT_TEMPLATE,
             [str(user_id), str(registration_username),
             str(registering_person_name), str(registration_email),
             str(registration_password)])

        # send a response to the website to display in the action banner.
        page_jinja_variable_dictionary["BANNER_MESSAGE"] = ("Welcome " + registration_username +
                               "! You have been successfully registered for Pynote!")

        return page_jinja_variable_dictionary

    # send a response to the website to display in the action banner.
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = ("Unable to register "
        "- a user with the username '" + registration_username + "'"
        " already exists!")
    return page_jinja_variable_dictionary

def compute_password_hash(base_password_string, user_id):
    """This function generates a password hash (to be stored in the user information
    database to verify user login passwords), and returns it as a string."""
    # -salt the user's password with their user ID
    password_hash = str(user_id) + str(base_password_string)
    # -hash the user's password
    password_hash = str(sha256_crypt.hash(password_hash))
    # return the password hash
    return password_hash

def is_username_valid(username_string):
    """This function checks if the string specified in the 'username_string' parameter
    matches requirements for a username, and returns a boolean indicating the result."""
    # remove whitespace
    username_string = username_string.strip()
    # return true if username is >= min length, < max lenght
    return bool(USERNAME_MIN_LENGTH <= len(username_string) < USERNAME_MAX_LENGTH)

def is_password_valid(password_string):
    """This function checks if the string specified in the 'password_string' parameter
    matches requirements for a password, and returns a boolean indicating the result."""

    # remove whitespace
    password_string = password_string.strip()
    # check if password is between min and max length
    is_password_string_valid = bool(PASSWORD_MIN_LENGTH <= len(password_string)
        < PASSWORD_MAX_LENGTH)

    # check if password at least meets length requirement before checking further requirements.
    if is_password_string_valid:
        # check if password has 1 uppercase char, 1 lowercase char, 1 number, and 1 special char
        is_password_string_valid = bool(re.match(PASSWORD_VALIDATION_REGEX, password_string)
            is not None)

    # return result
    return is_password_string_valid

def is_email_valid(email_string):
    """This function checks if the string specified in the 'email_string' parameter
    is in the form of a valid e-mail, and returns a boolean indicating the result."""
    # return result of regex check of email
    return bool((re.match(EMAIL_VALIDATION_REGEX, email_string) is not None))

def init_jinja_var_dictionary():
    """This function initializes default values for the page's jinja dictionary.
    Note: this function should only be run once, when the web server is initially
    launched."""
    page_jinja_variable_dictionary = {}
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = PAGE_BANNER_MESSAGE
    page_jinja_variable_dictionary["USERNAME_DESCRIPTOR"] = USERNAME_DESCRIPTOR
    page_jinja_variable_dictionary["PASSWORD_DESCRIPTOR"] = PASSWORD_DESCRIPTOR
    page_jinja_variable_dictionary["NAME_DESCRIPTOR"] = NAME_DESCRIPTOR
    page_jinja_variable_dictionary["EMAIL_DESCRIPTOR"] = EMAIL_DESCRIPTOR
    page_jinja_variable_dictionary["USERNAME_TB_BACKCOLOR"] = USERNAME_TB_BACKCOLOR
    page_jinja_variable_dictionary["PASSWORD_TB_BACKCOLOR"] = PASSWORD_TB_BACKCOLOR
    return page_jinja_variable_dictionary
