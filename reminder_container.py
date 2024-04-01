"""This module contains the code for the ReminderContainer class, which is
a class that defines an object which is a container for reminder-related
information."""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class ReminderContainer:
    """This class is used to store data related to an individual reminder that a user
    creates (such as reminder title, date/time due, notes and tags)."""
    # constructor
    def __init__(self, reminder_datetime, reminder_title, reminder_tags, reminder_description):
        """This function is the constructor for the ReminderContainer object."""
        # assign variables
        self.reminder_datetime = reminder_datetime
        self.reminder_title = reminder_title
        self.reminder_tags = reminder_tags
        self.reminder_description = reminder_description
        # color used to color the cells of the reminder row that this ReminderContainer's
        # data is populated to. Orange = deadline within the next 24 hours, Yellow = by tomorrow
        # within next 48 hours), green = longer deadline (at least 2 days out). Default color is
        # light gray (#989898)
        self.deadline_proximity_color = self.get_deadline_proximity_color_from_datetime(
            reminder_datetime)

    def get_deadline_proximity_color_from_datetime(self, reminder_datetime):
        """This function returns an RGB color as a hexadecimal string, used to visually
        indicate to the user roughly how close the deadline of a particular reminder is,
        based on the reminder's distance in hours from the current time."""

        # convert the reminder datetime to a python datetime object
        reminder_deadline = datetime.strptime(reminder_datetime, '%Y-%m-%d %H:%M:%S')

        # get hours by subtracting datetime.now() from reminder_datetime_obj, getting seconds and
        # dividing by 3600.
        hours_left = int((reminder_deadline - datetime.now()).total_seconds() / 3600)

        # return the appropriate color based on hours left
        if 0 <= hours_left < 24:
            # deadline imminent - color red
            return "#e3735d"
        if 24 <= hours_left < 48:
            # deadline within 48 hours but greater than 24 - color orange
            return "#dba723"
        if 48 <= hours_left < 72:
            # deadline within 72 hours but greater than 48 - color yellow
            return "#d1d435"
        if 72 <= hours_left:
            # deadline is more than 72 hours (3 days) away - color green
            return "#3bc930"

        # return default cell color (gray) if for whatever reason none of the
        # above situations apply (for instance, a reminder whose due date has
        # passed)
        return "#989898"
