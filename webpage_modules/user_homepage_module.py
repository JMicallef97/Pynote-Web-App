"""This module contains variables and functionality relating to the user home page
HTML page."""

import datetime
from datetime import datetime
import user_session_manager_module
from database_modules import db_scripts, database_access_module
import reminder_container

def init_jinja_var_dictionary():
    """This function initializes default values for the page's jinja dictionary,
    and returns the dictionary."""
    page_jinja_variable_dictionary = {}
    page_jinja_variable_dictionary["BANNER_MESSAGE"] = "Time to get caught up!"
    page_jinja_variable_dictionary["CURRENT_DATETIME"] = ("The current date/time is "
        + str(datetime.now()))
    # return dictionary
    return page_jinja_variable_dictionary

def get_reminders_within_time_period(session_id, period_hours, jinja_var_dict):
    """This function returns a list of ReminderContainer objects belonging to the
    user who the session_id was assigned to, that are within (the value of period_hours)
    hours from the current date/time. If no items are found, an empty list is returned.
    The function also updates the banner message in the jinja variable dictionary."""

    # declare function variables
    # -declare list to hold the ReminderContainer objects representing reminders within timeframe
    reminders_within_timeframe_list = []

    # get user ID from session ID
    user_id = user_session_manager_module.get_user_id_from_session_id(session_id)

    # check if user ID is invalid (someone trying to use a session token that wasn't assigned
    # to them, or a server error)
    if user_id is None:
        # update the banner message and return
        jinja_var_dict["BANNER_MESSAGE"] = ("Could not retrieve reminders due to invalid session"
            " token. Please log out, log back in and try again.")
        return reminders_within_timeframe_list

    # declare variable for query results
    query_results = []

    # user ID is valid for session token
    # -contact the database access module and run query to identify all reminders within the
    #  desired timeframe
    if period_hours >= 0:
        query_results = database_access_module.perform_user_reminder_db_query(user_id,
            "Get reminders within next " + str(period_hours) + " hours",
              db_scripts.GET_REMINDERS_BY_DATETIME,
              [period_hours])
    else:
        # get past results
        query_results = database_access_module.perform_user_reminder_db_query(user_id,
            "Get reminders within next " + str(period_hours) + " hours",
                db_scripts.GET_PAST_REMINDERS, None)

    # check if query result is not none
    if query_results is not None:
        # reminders within timeframe found
        # -populate ReminderContainers for each item, add them to REMINDERS_WITHIN_TIMEFRAME_LIST
        for row in query_results:
            # populate a reminder container object
            new_reminder_container = reminder_container.ReminderContainer(
                str(row[1]), str(row[2]),
                str(row[3]), str(row[4]))
            # add to the 'reminders within timeframe' list
            reminders_within_timeframe_list.append(new_reminder_container)

    # sort reminders by date (sorted in asscending order in hours to deadline)
    sorted_reminder_list = sorted(reminders_within_timeframe_list,
        key=lambda obj: obj.reminder_datetime)

    # check if reminders are for future or past
    if period_hours > 0:
        # update the banner message (with number of records found)
        jinja_var_dict["BANNER_MESSAGE"] = ("Found " + str(len(sorted_reminder_list))
            + (" reminder(s) within the next " + str(period_hours) + " hours."))
    else:
        # update banner message with number of records found, from the past:
        jinja_var_dict["BANNER_MESSAGE"] = ("Found " + str(len(sorted_reminder_list))
            + (" expired reminder(s) (up to 72 hours since the present)"))

    # return reminders within timeframe list
    return list(sorted_reminder_list)
