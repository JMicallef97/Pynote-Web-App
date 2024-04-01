# Pynote-Web-App
A locally-hosted reminder web app, developed using Python and the Flask web framework. The project was created and built using Pycharm 2023.3.4 Community Edition and Python version 3.12. Website was tested in Firefox 115.9.1 64-bit. All python code was linted using Pylint. No external dependencies are required. Website databases are created and maintained using Python's sqlite3 library. The web app has been fully tested - for documentation refer to the Pynote Test Plan .pdf file.

# Setup Information
In order for project to work correctly, the PROJECT_ROOT_DIRECTORY in server_constants.py must be set to the project's root directory. main.py, reminder-container.py, server_constants.py, user_session_manager_module.py, and all project folders (database_modules, databases, static, templates, and webpage_modules) must be contained within the directory specified in PROJECT_ROOT_DIRECTORY.

# Uses
The website allows users to create an account and make reminders at any point in the future. The user can filter reminders by those due within the next 24 hours, next week, next month, and next year, in addition to displaying expired reminders (that are less than or equal to 72 hours old). 
