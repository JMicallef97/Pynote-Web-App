"""This module contains the entry point for the program, and code which initializes
the Flask web server, receives requests from clients, serves web pages and calls
functions in other modules to handle back-end related tasks like database processing,
user authentication, retrieving data and other functions."""

from flask import Flask, render_template, request
from webpage_modules import login_module, new_reminder_page_module, registration_module, \
    update_password_module, user_homepage_module
import user_session_manager_module
from database_modules import database_access_module
import server_constants

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
# contains the index (home page) code, which is the log in screen
def index():
    """This function contains code for responding to clients requesting the index
    (home page) of the website, and calling functions to authenticate and admit entry to users
    trying to log into the website."""
    # check for post (web page posting user information)
    if request.method == 'POST':
        # read form fields (user name and password)
        entered_username = request.form['Username']
        entered_password = request.form['Password']

        # validate the username and password
        jinja_var_dict = login_module.authenticate_user_login(entered_username,
            entered_password, str(request.remote_addr))

        # if validates, return the landing page with the cookie key stored in the URL
        # as a parameter, and store user's cookie key in a list on the server

        # -pass jinja variable so that landing page (upon being sent now) stores the
        # cookie. Subsequent landing page replies won't include the javascript.

        # check if any login errors occurred (would be reflected in the banner message)
        if not jinja_var_dict["loginPassed"]:
            # return the page with the jinja variables
            return render_template("index.html", jinja_variables = jinja_var_dict)

        # initialize user session container
        session_token = user_session_manager_module.initialize_user_session_container(
            jinja_var_dict["UserID"], jinja_var_dict["PasswordHash"],
            jinja_var_dict["Username"], jinja_var_dict["Name"], str(request.remote_addr))

        # remove user information from jinja variable dict (not used in HTML page)
        del jinja_var_dict["UserID"]
        del jinja_var_dict["PasswordHash"]
        del jinja_var_dict["Username"]
        del jinja_var_dict["Name"]

        # generate jinja variable dictionary for page
        jinja_var_dict = user_session_manager_module.get_user_session_page_jinja_vars(
            session_token)

        # add entry in dictionary for reminder entries (blank)
        jinja_var_dict["Reminder_Entries"] = {}

        # proceed to home page
        return render_template("user_homepage.html",
            jinja_variables = jinja_var_dict)

    # no actionable request occurred, post the original page
    return render_template("index.html", jinja_variables =
            login_module.init_jinja_var_dictionary())

@app.route('/new_reminder_page/', methods=['POST', 'GET'])
def new_reminder_page():
    """This function contains code for responding to clients requesting the 'new reminder'
    page of the website, and calling functions to implement page functionality (such
    as serving the page, validating reminder data, updating the user's database with
    the new reminder data or returning an error message to the user)."""
    # check for posts
    if request.method == 'POST':
        # validate the user's session ID
        post_session_id = request.form['session_id']

        # check if user's session ID is valid (session ID is correct, and the response
        # it arrived from came from the IP address the session was issued to)
        if user_session_manager_module.is_session_id_valid(str(post_session_id),
            str(request.remote_addr)):
            # user validated

            # -populate jinja page variable dictionary with defaults
            jinja_page_variables = new_reminder_page_module.init_jinja_var_dictionary()
            # -add session token to dictionary (carry forward) so user will remain validated
            #  in future pages
            jinja_page_variables["SessionID"] = post_session_id

            # pick an action based on the post action
            match str(request.form['post_action']):
                case "save_reminder":
                    # user saved/updated a reminder
                    # -run the function to save the reminder in the user's database
                    # -banner message in jinja variable dictionary will be internally updated
                    #  based on if reminder could be saved
                    #jinja_page_variables = new_reminder_page_module.save_reminder(post_session_id,
                    #    request.form["reminder_title"], request.form["reminder_datetime"],
                    #    request.form["rem_tags_textbox"], request.form["rem_description_textbox"],
                    #    jinja_page_variables)
                    jinja_page_variables = new_reminder_page_module.save_reminder(post_session_id,
                        {'reminder_title' : request.form["reminder_title"],
                        'reminder_datetime' : request.form["reminder_datetime"],
                        'reminder_tags' : request.form["rem_tags_textbox"],
                        'reminder_description' : request.form["rem_description_textbox"]},
                        jinja_page_variables)

            # render the page with updated jinja page variables.
            return render_template("new_reminder_page.html",
                jinja_variables=jinja_page_variables)

    # user tried directly accessing the new reminder page which is a no-no (have to sign in first)
    # -populate dictionary containing banner message with explanation.
    jinja_page_var_dict = {}
    jinja_page_var_dict["BANNER_MESSAGE"] = "Ah-ah-ah! You'll need to log in first."
    return render_template("index.html",
        jinja_variables = jinja_page_var_dict)


@app.route('/changelog/', methods=['POST', 'GET'])
def changelog():
    """This function contains code for responding to clients requesting the 'changelog'
    web page (serving the web page)."""
    # serve the changelog page to the user
    return render_template("changelog.html")


@app.route('/user_homepage/', methods=['POST', 'GET'])
def user_homepage():
    """This function contains code for responding to clients requesting the 'home page'
    page of the website, and calling functions to implement page functionality (such
    as serving the page, filtering and retrieving reminders by time left, making
    new reminders, logging out, accessing external links, and more)"""

    # check if the form the user submitted contains a session ID field
    # (since a session ID is required to access a user homepage)
    if 'session_id' in request.form:
        # validate the user's session ID
        post_session_id = request.form['session_id']
        # check if user's session ID is valid (session ID is correct, and the response
        # it arrived from came from the IP address the session was issued to)
        if user_session_manager_module.is_session_id_valid(str(post_session_id),
            str(request.remote_addr)):

            # check for posts
            if request.method == 'POST':

                print(request.form['post_action'])
                # declare variables
                jinja_page_vars = {}

                # pick an action based on the post action
                match str(request.form['post_action']):
                    case "logout":
                        # user wants to log out.
                        # -run logout function in session manager module
                        user_session_manager_module.log_user_out(post_session_id)
                        # return the index page
                        login_page_jinja_variables = {}
                        login_page_jinja_variables["BANNER_MESSAGE"] = ("You're logged out."
                            " Come back soon!")
                        # return user to homepage
                        return render_template("index.html",
                            jinja_variables=login_page_jinja_variables)
                    case "new_reminder":
                        # user wants to make a new reminder
                        # -load page jinja variable dictionary
                        page_jinja_vars = new_reminder_page_module.init_jinja_var_dictionary()
                        # -load login-specific info for future requests (user session ID)
                        page_jinja_vars["SessionID"] = post_session_id
                        # serve new_reminder_page.html
                        # serve the 'new_reminder_page' to the user, with the page jinja variables
                        return render_template('new_reminder_page.html',
                            jinja_variables=page_jinja_vars)
                    case "rems_within_day":
                        # -user wants reminders within the next 24 hours (day).
                        # -first, initialize jinja page vars dictionary
                        jinja_page_vars = user_homepage_module.init_jinja_var_dictionary()
                        # -populate (carry forward) session ID and user's name
                        jinja_page_vars["SessionID"] = post_session_id
                        # -next, get all ReminderContainers that fall within the desired
                        #  timeframe.
                        jinja_page_vars["Reminder_Entries"] = (
                            user_homepage_module.get_reminders_within_time_period(
                                post_session_id, 24, jinja_page_vars
                            ))
                    case "rems_within_week":
                        # -user wants reminders within the next 168 hours (1 week).
                        # -first, initialize jinja page vars dictionary
                        jinja_page_vars = user_homepage_module.init_jinja_var_dictionary()
                        # -populate (carry forward) session ID and user's name
                        jinja_page_vars["SessionID"] = post_session_id
                        # -next, get all ReminderContainers that fall within the desired
                        #  timeframe.
                        jinja_page_vars["Reminder_Entries"] = (
                           user_homepage_module.get_reminders_within_time_period(
                               post_session_id, 168, jinja_page_vars
                           ))
                    case "rems_within_month":
                        # -user wants reminders within the next 731 hours (1 month).
                        # -first, initialize jinja page vars dictionary
                        jinja_page_vars = user_homepage_module.init_jinja_var_dictionary()
                        # -populate (carry forward) session ID and user's name
                        jinja_page_vars["SessionID"] = post_session_id
                        # -next, get all ReminderContainers that fall within the desired
                        #  timeframe.
                        jinja_page_vars["Reminder_Entries"] = (
                            user_homepage_module.get_reminders_within_time_period(
                                post_session_id, 731, jinja_page_vars
                            ))
                    case "rems_within_year":
                        # -user wants reminders within the next 8760 hours (1 year).
                        # -first, initialize jinja page vars dictionary
                        jinja_page_vars = user_homepage_module.init_jinja_var_dictionary()
                        # -populate (carry forward) session ID and user's name
                        jinja_page_vars["SessionID"] = post_session_id
                        # -next, get all ReminderContainers that fall within the desired
                        #  timeframe.
                        jinja_page_vars["Reminder_Entries"] = (
                            user_homepage_module.get_reminders_within_time_period(
                                post_session_id, 8760, jinja_page_vars
                            ))
                    case "past_rems":
                        # -user wants past reminders (within 3 days/72 hours after current time).
                        # -first, initialize jinja page vars dictionary
                        jinja_page_vars = user_homepage_module.init_jinja_var_dictionary()
                        # -populate (carry forward) session ID and user's name
                        jinja_page_vars["SessionID"] = post_session_id
                        # -next, get all ReminderContainers that fall within the desired
                        #  timeframe.
                        jinja_page_vars["Reminder_Entries"] = (
                            user_homepage_module.get_reminders_within_time_period(
                                post_session_id, -72, jinja_page_vars
                            ))
                    case "reload_page":
                        # reload page, due to redirect
                        # -initialize jinja var dictionary
                        jinja_page_vars = user_homepage_module.init_jinja_var_dictionary()
                        # -add session key (carry forward) to allow user to be authenticated
                        #  in future requests
                        jinja_page_vars["SessionID"] = post_session_id
                        # add entry in dictionary for reminder entries (blank)
                        jinja_page_vars["Reminder_Entries"] = {}

                # render/return the home page by default (jinja variables set according to
                # the post request form name)
                return render_template("user_homepage.html", jinja_variables=jinja_page_vars)

            # session ID is invalid
            # -alert user to reason by setting banner page
            login_page_jinja_variables = {}
            login_page_jinja_variables["BANNER_MESSAGE"] = ("Your session has expired,"
                " please log in again.")
            # return user to homepage
            return render_template("index.html", jinja_variables=login_page_jinja_variables)

    # user tried directly accessing the home page which is a no-no (have to sign in first)
    # -populate dictionary containing banner message with explanation.
    jinja_page_var_dict = {}
    jinja_page_var_dict["BANNER_MESSAGE"] = "Ah-ah-ah! You'll need to log in first."
    return render_template("index.html",
        jinja_variables = jinja_page_var_dict)

@app.route('/register/', methods=['POST', 'GET'])
def register():
    """This function contains code for responding to clients requesting the 'register'
    page of the website, and calling functions to implement page functionality (such
    as serving the page, validating reminder data, updating the user database with
    the user's registration data or returning an error message to the user)."""

    print(request.method)

    # check for post (web page posting user registration info)
    if request.method == 'POST':
        # check if form contains a 'to_homepage' element (indicating
        # that the form that was submit was registration information)
        if 'registration_form' in request.form:
            # call the registration script in the registration module
            # and pass it the form information.
            # -function will return a page banner message explaining status
            # (ie, if registration successful, if it failed, etc)
            page_jinja_vars = registration_module.registration_script(request)
            return render_template("register.html", jinja_variables =
                page_jinja_vars)
        if 'cancel_form' in request.form:
            # user clicked the 'cancel' button, indicating they want to back to
            # the home page.
            return render_template("index.html")
    elif request.method == 'GET':
        # page is being requested, return the page with the jinja variables initialized
        page_jinja_vars = registration_module.init_jinja_var_dictionary()
        return render_template("register.html", jinja_variables=page_jinja_vars)

    return render_template("register.html", jinja_variables =
        registration_module.init_jinja_var_dictionary())  #, [variables here]

@app.route('/update_password/', methods=['POST', 'GET'])
def reset_password():
    """This function contains code for responding to clients requesting the 'reset password'
    page of the website, and calling functions to implement page functionality (such
    as serving the page, validating the user's new passowrd, updating the user database with
    the new password hash or returning an error message to the user)."""

    # check for posts
    if request.method == 'POST':
        # validate the user's session ID
        post_session_id = request.form['session_id']
        # check if user's session ID is valid (session ID is correct, and the response
        # it arrived from came from the IP address the session was issued to)
        if user_session_manager_module.is_session_id_valid(str(post_session_id),
            str(request.remote_addr)):
            # user validated
            # -check the value of post_action
            match str(request.form['post_action']):
                case "load_page":
                    # request to initially load page (for instance, after user clicked
                    # the 'update password' button in the homepage)
                    # -initialize page jinja variable dictionary
                    jinja_var_dict = update_password_module.init_jinja_var_dictionary()
                    # -add (carry forward) session ID, to authenticate user in further
                    #  interactions.
                    jinja_var_dict["SessionID"] = post_session_id
                    # -load page with jinja variable dictionary
                    return render_template("update_password.html", jinja_variables=jinja_var_dict)
                case "update_password":
                    # -initialize page jinja variable dictionary
                    jinja_var_dict = update_password_module.init_jinja_var_dictionary()
                    # try validating the password
                    jinja_var_dict = update_password_module.try_update_user_password(
                        str(request.form['Password']), str(request.form['Repeated_Password']),
                        post_session_id, jinja_var_dict)
                    # -add (carry forward) session ID, to authenticate user in further
                    #  interactions.
                    jinja_var_dict["SessionID"] = post_session_id
                    # -load page with jinja variable dictionary
                    return render_template("update_password.html", jinja_variables=jinja_var_dict)

    # user tried directly accessing the new reminder page which is a no-no (have to sign in first)
    # -populate dictionary containing banner message with explanation.
    jinja_page_var_dict = {}
    jinja_page_var_dict["BANNER_MESSAGE"] = "Ah-ah-ah! You'll need to log in first."
    return render_template("index.html",
        jinja_variables=jinja_page_var_dict)

def main():
    """This function is the main entry point of the application; it establishes
    connections to the website databases, loads information from files into the
    program and initializes/launches the Flask server."""

    print("Starting flask server")
    # connect to databases
    database_access_module.connect_to_website_databases(
        (server_constants.PROJECT_ROOT_DIRECTORY + "databases"),
        [server_constants.USERS_INFO_DB_NAME, server_constants.LOGIN_LOG_DB_NAME])

    # try loading the 10,000 most common passwords
    update_password_module.try_load_most_common_passwords(
        server_constants.PROJECT_ROOT_DIRECTORY + "static\\CommonPassword.txt")

    # initialize page jinja dictionaries
    login_module.init_jinja_var_dictionary()
    registration_module.init_jinja_var_dictionary()
    new_reminder_page_module.init_jinja_var_dictionary()

    # launch the flask app
    Flask.run(app)

main()
