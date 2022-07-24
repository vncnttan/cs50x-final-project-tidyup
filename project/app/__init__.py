from cs50 import SQL
from celery import Celery
from datetime import date, datetime
from flask import flash, Flask, redirect, render_template, request, session
from flask_session import Session


from helpers import login_req, theme_color, event_icons

app = Flask(__name__)

app.config.from_object('config')

# Import celery configuration
import celeryconfig

# Importing application from other file
import friends
import events
import opening

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session nto use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def make_celery(app):
    # Create context tasks in celery
    celery = Celery(
        app.import_name,
        broker=app.config['BROKER_URL']
    )
    celery.conf.update(app.config)
    celery.config_from_object(celeryconfig)
    TaskBase = celery.Task
    print(celery)

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery

celery = make_celery(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")


# Ensure response aren't cached
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Pass data to all html in the app
@app.context_processor
def user_data():
    try:
        user_data = {
            'username': db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"],
            'id': session["user_id"]
        }
        if len(db.execute("SELECT email_address FROM emails WHERE user_id = ?", session["user_id"])) == 1:
            user_data["email_binded"] = db.execute("SELECT email_address FROM emails WHERE user_id = ?", session["user_id"])[0]["email_address"]
    except KeyError:
        user_data = {}
    return dict(user_data=user_data)

@app.route("/")
@login_req
def index():
    # Get Today Long Events and Short Events
    today_short_events = db.execute("SELECT * FROM events WHERE user_id = ? and event_date = ?", session["user_id"], date.today())
    for row in today_short_events:
        row["event_color"] = theme_color[row["event_type"]]
        row["event_icon"] = event_icons[row["event_type"]]
        if row["notify_email"] == "True":
            row["notif_icon"] = "fa-solid fa-bell fa-shake"
        elif row["notify_email"] == "False":
            row["notif_icon"] = "fa-solid fa-bell-slash"

    all_long_events = db.execute("SELECT * FROM long_events WHERE user_id = ? ORDER BY event_date_end", session["user_id"])
    today_long_events = []
    for row in all_long_events:
        if datetime.strptime(row["event_date_start"], "%Y-%m-%d").date() <= date.today() and datetime.strptime(row["event_date_end"], "%Y-%m-%d").date() >= date.today():
            row["event_color"] = theme_color[row["event_type"]]
            row["days_left"] = (datetime.strptime(row["event_date_end"], "%Y-%m-%d").date() - date.today()).days
            row["event_icon"] = event_icons[row["event_type"]]
            if row["notify_email"] == "True":
                row["notif_icon"] = "fa-solid fa-bell fa-shake"
            elif row["notify_email"] == "False":
                row["notif_icon"] = "fa-solid fa-bell-slash"
            today_long_events.append(row)

    today_legible_date = date.today().strftime("%B %d, %Y")

    return render_template("index.html", today_legible_date=today_legible_date, short_events=today_short_events, long_events=today_long_events)

@app.route("/logout")
@login_req
def logout():

    # Clearing the session
    session.clear()

    return redirect("/landing")


@app.route("/edit-username", methods=["GET", "POST"])
@login_req
def editusername():
    if request.method == "POST":
        # User clicked cancel
        if request.form.get("action") == "cancel":
            return redirect("/")

        username = request.form.get("newUN")

        if username == db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]:
            return redirect("/")

        # Ensure username was submitted
        if not username:
            flash("Please provide username.")
            return redirect("/edit-username")

        # Ensure username is not taken already
        elif len(db.execute("SELECT * FROM users WHERE username = ?", username)) == 1:
            flash("Username already taken")
            return redirect("/edit-username")

        elif len(username) > 50:
            flash("Username inputted exceeds maximum character")
            return redirect("/edit-alias")

        db.execute("UPDATE users SET username = ? WHERE id = ?", username, session["user_id"])
        flash("Username updated!")
        return redirect("/")

    return render_template("edit-username.html")


if __name__ == "__main__":
    app.run()