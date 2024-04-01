"""This module contains code related to the functionality of the 'new reminder' page,
including initializing page jinja variables, validating user input and storing
reminder details in database files."""

import uuid
from datetime import datetime
import user_session_manager_module
from database_modules import db_scripts, database_access_module

# declare module variables
PAGE_BANNER_MESSAGE = "Quick, hold that thought!"
REM_DATETIME_DESCRIPTOR = ("Please enter the date that the reminder is due by. Obviously, don't"
                           " enter dates/times in the past.")
REM_TITLE_DESCRIPTOR = ("Please enter a title for the reminder. You'll have a chance to write"
                        " down specifics in the 'reminder description' section. Please limit"
                        " titles to 100 characters, but make it at least 3 characters. Titles"
                        " cannot be composed of only whitespace characters.")

REM_TAGS_DESCRIPTOR = ("Enter a comma-separated value (CSV) list of tags for the reminder, which "
                       "will help with categorizing and searching for related reminders. Tags are "
                       "optional. Please limit length to 350 characters. Tags cannot be composed "
                       "of only whitespace characters.")

REM_DESCRIPTION_DESCRIPTOR = ("Enter details/specifics about the reminder here - contact "
                              "information, addresses, et cetera. Please limit length to "
                              "1500 characters. Description is optional. Description cannot be "
                              "composed of only whitespace characters.")

# constants
REM_TITLE_MIN_LENGTH = 3
REM_TITLE_MAX_LENGTH = 100
REM_TAGS_MIN_LENGTH = 0
REM_TAGS_MAX_LENGTH = 350
REM_DESC_MIN_LENGTH = 0
REM_DESC_MAX_LENGTH = 1500

# colors, used to indicate errors in entry
REM_TITLE_TB_BACKCOLOR = "#ffffff"
REM_DATEPICKER_PANEL_BACKCOLOR = "#fff563"

# dictionary, used to store jinja variables for the page.
PAGE_JINJA_VARIABLE_DICTIONARY = {}

#def save_reminder(session_id, reminder_title, reminder_datetime, reminder_tags,
#                  reminder_description, page_jinja_var_dict):
def save_reminder(session_id, reminder_details, page_jinja_var_dict):
    """This module saves the reminder details (function parameters) to a database file
    [labeled with the user's ID number], or updates an existing reminder. The value
    associated with the BANNER_MESSAGE key in the page_jinja_var_dict dictionary and
    related variables (such as textbox color) will be updated to values based on if
    the reminder was able to be saved or not (for instance, one or more pieces of
    information were incorrect)."""

    # firstly, get username from session ID through the session manager module
    session_user_id = user_session_manager_module.get_user_id_from_session_id(session_id)

    if session_user_id is not None:
        # session ID is valid

        # check if reminder title is valid
        #if not is_reminder_datetime_valid(reminder_datetime):
        if not is_reminder_datetime_valid(reminder_details['reminder_datetime']):
            # update banner message in jinja variable dictionary
            page_jinja_var_dict["BANNER_MESSAGE"] = ("Error! The reminder date was invalid."
                " Please pick a valid date in the future.")
            # return jinja variable dictionary
            return page_jinja_var_dict

        # check if reminder title is valid
        #if not is_reminder_title_valid(reminder_title):
        if not is_reminder_title_valid(reminder_details['reminder_title']):
            # update banner message in jinja variable dictionary
            page_jinja_var_dict["BANNER_MESSAGE"] = ("Error! Your title was either too"
                " short or too long, please use a different title.")
            # return jinja variable dictionary
            return page_jinja_var_dict

        # check if reminder tags are valid
        if not is_reminder_tags_string_valid(reminder_details['reminder_tags']):
            # update banner message in jinja variable dictionary
            # update banner message in jinja variable dictionary
            page_jinja_var_dict["BANNER_MESSAGE"] = ("Error! The tag string you entered is"
                " too long (>350 characters). Please shorten the reminder tag string and try "
                "again.")
            # return jinja variable dictionary
            return page_jinja_var_dict

        # check if reminder description is valid
        if not is_reminder_description_valid(reminder_details['reminder_description']):
            # update banner message in jinja variable dictionary
            # update banner message in jinja variable dictionary
            page_jinja_var_dict["BANNER_MESSAGE"] = ("Error! The description you entered is"
                " too long (>1500 characters). Please shorten the description and try again.")
            # return jinja variable dictionary
            return page_jinja_var_dict

        # convert the reminder datetime to a workable format
        #workable_datetime_string = convert_datetime_from_iso_to_sqlite(reminder_datetime)
        workable_datetime_string = convert_datetime_from_iso_to_sqlite(
            reminder_details['reminder_datetime'])

        # if this point reached, reminder fields are validated.
        # -run query through the database access module
        #database_access_module.perform_user_reminder_db_query(session_user_id,
        #    "Add Reminder", db_scripts.INSERT_NEW_REMINDER,
        #    [str(uuid.uuid4()), str(workable_datetime_string), str(reminder_title),
        #     str(reminder_tags), str(reminder_description)])
        database_access_module.perform_user_reminder_db_query(session_user_id,
            "Add Reminder", db_scripts.INSERT_NEW_REMINDER,
            [str(uuid.uuid4()), str(workable_datetime_string),
             str(reminder_details['reminder_title']),
             str(reminder_details['reminder_tags']),
             str(reminder_details['reminder_description'])])

        # update banner message in jinja variable dictionary to indicate reminder was successfully
        # saved.
        page_jinja_var_dict["BANNER_MESSAGE"] = ("Your reminder was saved! To return"
            " to the home page, click the 'cancel' button.")
        # return jinja variable dictionary
        return page_jinja_var_dict

    # session ID is invalid (not on file), meaning user can't be tracked down
    # -this branch should only be reachable if someone tried using a random token
    #  (attacker maybe?)
    # -print to banner message, so user will be made aware of problem.
    page_jinja_var_dict["BANNER_MESSAGE"] = ("Session ID invalid, could not save "
          "reminder! Please log out and back in, and try again.")

    return page_jinja_var_dict

def is_reminder_title_valid(reminder_title):
    """This function validates the reminder title, ensuring it is within the prescribed
    character lengths."""
    return REM_TITLE_MIN_LENGTH <= len(str(reminder_title).strip()) <= REM_TITLE_MAX_LENGTH

def is_reminder_tags_string_valid(reminder_tags):
    """This function validates the reminder tag string, ensuring it is within the prescribed
    character lengths"""
    return REM_TAGS_MIN_LENGTH <= len(str(reminder_tags).strip()) <= REM_TAGS_MAX_LENGTH

def is_reminder_description_valid(reminder_description):
    """This function validates the reminder description, ensuring it is within the prescribed
    character lengths"""
    return REM_DESC_MIN_LENGTH <= len(str(reminder_description).strip()) <= REM_DESC_MAX_LENGTH

def is_reminder_datetime_valid(reminder_datetime):
    """This function validates the reminder date/time, ensuring that it isn't in the past."""
    # ensure the reminder datetime entered is valid.
    if len(str(reminder_datetime)) > 0:
        # first, convert the reminder datetime into a python datetime object
        converted_rem_datetime = datetime.fromisoformat(reminder_datetime)
        # check if reminder datetime is less than datetime.now() (in the past), and return as a bool
        return bool(converted_rem_datetime > datetime.now())
    # return false by default
    return False

def convert_datetime_from_iso_to_sqlite(iso_string):
    """This function converts an iso 8601 date to a date in
    the format YYYY-MM-DD HH:MM:SS."""
    # declare variables
    corrected_datetime_obj = datetime.fromisoformat(iso_string)
    # return the formatted string
    return str(corrected_datetime_obj.strftime('%Y-%m-%d %H:%M:%S'))

def init_jinja_var_dictionary():
    """This function initializes default values for the page's jinja dictionary.
    Note: this function should only be run once, when the web server is initially
    launched."""
    PAGE_JINJA_VARIABLE_DICTIONARY["BANNER_MESSAGE"] = PAGE_BANNER_MESSAGE
    PAGE_JINJA_VARIABLE_DICTIONARY["REM_DATETIME_DESCRIPTOR"] = REM_DATETIME_DESCRIPTOR
    PAGE_JINJA_VARIABLE_DICTIONARY["REM_TITLE_DESCRIPTOR"] = REM_TITLE_DESCRIPTOR
    PAGE_JINJA_VARIABLE_DICTIONARY["REM_TAGS_DESCRIPTOR"] = REM_TAGS_DESCRIPTOR
    PAGE_JINJA_VARIABLE_DICTIONARY["REM_DESCRIPTION_DESCRIPTOR"] = REM_DESCRIPTION_DESCRIPTOR
    PAGE_JINJA_VARIABLE_DICTIONARY["REM_TITLE_TB_BACKCOLOR"] = REM_TITLE_TB_BACKCOLOR
    PAGE_JINJA_VARIABLE_DICTIONARY["REM_DATEPICKER_PANEL_BACKCOLOR"] = (
        REM_DATEPICKER_PANEL_BACKCOLOR)

    return PAGE_JINJA_VARIABLE_DICTIONARY
