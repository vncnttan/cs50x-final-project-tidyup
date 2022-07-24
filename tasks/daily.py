from cs50 import SQL
from celery import shared_task, Celery
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask_mail import Message, Mail

from helpers import next_birthday

from app import app

app.config.from_object('config')
celery = Celery(
    app.import_name,
    broker=app.config['BROKER_URL']
)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

# Configure mailing
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tidyupevent@gmail.com'
app.config['MAIL_PASSWORD'] = 'oxswleqrbxvdugwo'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


email_sender = 'tidyupevent@gmail.com'


@shared_task()
def email_and_expiredEventClear():
    # Clear Events and Long Event 4 month before this date
    # Get date of two months before today
    two_months_before = datetime.today() + relativedelta(months=-2)

    # Get user's events
    events = db.execute("SELECT id, event_date FROM events")
    for event in events:

        # Delete Events before that date
        if datetime.strptime(event["event_date"], "%Y-%m-%d") < two_months_before:

            # If it's an automatic added event from someone birthday notification, update user table data
            if len(db.execute("SELECT * FROM friends WHERE birthday_event_id = ?", id)) == 1:

                # Get the appropriate data
                friendship_data = db.execute("SELECT user_id, user_friend_id FROM friends WHERE birthday_event_id = ?", id)[0]
                user_id = friendship_data["user_id"]
                friend_id = friendship_data["user_friend_id"]
                event_data = db.execute("SELECT * FROM events WHERE id = ?", id)

                # Make a new event for that friend next birthday
                birthdate = next_birthday(event_data["event_date"])
                db.execute("INSERT INTO events (user_id, event_name, event_type, event_date, event_description, notify_email) VALUES (?, ?, ?, ?, ?, ?)", user_id, event_data["event_name"], event_data["event_type"], birthdate, "no details", event_data["notify_email"])
                db.execute("UPDATE friends SET birthday_event_id = (select seq from sqlite_sequence where name = 'events') WHERE user_id = ? AND user_friend_id = ?", user_id, friend_id)

            db.execute("DELETE FROM events WHERE id = ?", event["id"])

    # Delete Long Events before that date
    long_events = db.execute("SELECT id, event_date_end FROM long_events")
    for event in long_events:
        if datetime.strptime(event["event_date_end"], "%Y-%m-%d") < two_months_before:
            db.execute("DELETE FROM events WHERE id = ?", event["id"])


    # The emailing
    # Get all short event dated today and long event started today
    today_short_events = db.execute("SELECT * FROM events WHERE event_date = ?", date.today())
    today_long_events = db.execute("SELECT * FROM long_events WHERE event_date_start = ?", date.today())

    for short_event in today_short_events:
        # Checking if user opt in to get a notifier
        if short_event["notify_email"] == "True":
            # Email for short events today
            email_address = db.execute("SELECT email_address FROM emails WHERE user_id = ?", short_event["user_id"])[0]["email_address"]
            username = db.execute("SELECT username FROM users WHERE id = ?", short_event["user_id"])[0]["username"]
            msg = Message('You have an event waiting for you today!', sender = email_sender, recipients = [email_address])
            msg.body = "Hi " + username + ", you have an event today! Event name = " + short_event["event_name"] + " Event type = " + short_event["event_type"] + " Event date = " + short_event["event_date"] + " Event details = " + short_event["event_description"] + " Don't forget to attend it today! Mark other days using tidyup to receive daily event reminder!"
            msg.html = "<h1> Hi " + username + ", you have an event today!  &#127881; </h1> <br> <h3> <b>Event name: " + short_event["event_name"] + "</b> <br> Event type: " + short_event["event_type"] + " <br> Event date: " + short_event["event_date"] + " <br> Event details: " + short_event["event_description"] + " </h3> <br><br> Don't forget to attend it today! <br> Mark other days using <a href='https://vncnttan-code50-96110981-r4w994wg6fwq59-5000.githubpreview.dev/events'>tidyup</a> to receive daily event reminder!"
            with app.app_context():
                mail.send(msg)
    for long_event in today_long_events:

        # Checking if user opt in to get a notifier
        if long_event["notify_email"] == "True":
            # Email for long events today
            email_address = db.execute("SELECT email_address FROM emails WHERE user_id = ?", long_event["user_id"])[0]["email_address"]
            username = db.execute("SELECT username FROM users WHERE id = ?", long_event["user_id"])[0]["username"]
            msg = Message('A long event has started today!', sender = email_sender, recipients = [email_address])
            msg.body = "Hi " + username + ", your multi-day event has started today! Event name = " + long_event["event_name"] + " Event type = " + long_event["event_type"] + " Event start date = " + long_event["event_date_start"] + " Event end date: " + long_event["event_date_end"] + "Event details = " + long_event["event_description"] + " Gear up your gear this will be AMAZING! Mark other days using tidyup to receive daily event reminder!"
            msg.html = "<h1> Hi " + username + ", your multi-day event has started today! &#10002; </h1> <br> <h3> <b>Event name: " + long_event["event_name"] + "</b> <br> Event type: " + long_event["event_type"] + " <br> Event start date: " + long_event["event_date_start"] + " <br> Event end date: " + long_event["event_date_end"] + " <br> Event details: " + long_event["event_description"] + " </h3> <br><br> Gear up your gear this will be AMAZING! <br> Mark other days using <a href='https://vncnttan-code50-96110981-r4w994wg6fwq59-5000.githubpreview.dev/events'>tidyup</a> to receive daily event reminder!"
            with app.app_context():
                mail.send(msg)