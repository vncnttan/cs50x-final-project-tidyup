from datetime import date, datetime
from functools import wraps
from flask import session, redirect

# From CS50 Pset 9 - Finance
def login_req(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/landing")
        return f(*args, **kwargs)
    return decorated_function

# Get the next birthday
def next_birthday(dob):
    this_year = int(date.today().strftime("%Y"))
    this_year_birthday = datetime.strptime(dob, "%Y-%m-%d").replace(year=this_year)

    if this_year_birthday >= datetime.today():
        return this_year_birthday.strftime("%Y-%m-%d")
    else:
        return this_year_birthday.replace(year=(this_year + 1)).strftime("%Y-%m-%d")

# The dictionary pair of each the event type and their color
theme_color = {
    "Birthday": 'bg-pink-alt',
    "Quiz": 'bg-orange-alt',
    "Exam": 'bg-red-orange-alt',
    "Important": 'bg-red-alt',
    "Meeting": 'bg-cyan-alt',
    "Hangout": 'bg-sky-blue-alt',
    "Rest": 'bg-blue-alt',
    "Travel": 'bg-green-alt',
    "Formal": 'bg-purple-alt',
    "Others": 'bg-dark-blue-alt'
}

# The dictionary pair of each the status type and their color
status_color = {
    "Online": 'bg-logo-theme-alt',
    "Do not disturb": 'bg-red-alt',
    "Away": 'bg-purple-alt'
}

# The dictionary pair of each event type and their respective fa-icon
event_icons = {
    "Birthday": 'fa-solid fa-cake-candles',
    "Quiz": 'fa-solid fa-file-circle-question',
    "Exam": 'fa-solid fa-school',
    "Important": 'fa-solid fa-circle-exclamation',
    "Meeting": 'fa-solid fa-handshake',
    "Hangout": 'fa-solid fa-champagne-glasses',
    "Rest": 'fa-solid fa-umbrella-beach',
    "Travel": 'fa-solid fa-suitcase-rolling',
    "Formal": 'fa-solid fa-user-tie',
    "Others": 'fa-solid fa-grip'
}