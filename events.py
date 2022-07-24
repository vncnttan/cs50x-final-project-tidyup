from cs50 import SQL
from datetime import date, datetime, timedelta
from flask import flash, redirect, render_template, Response, request, session
from helpers import login_req, theme_color, event_icons
import json

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

from app import app

@app.route("/events", methods=["GET","POST"])
@login_req
def events():

    if request.method == "POST":
        rows = db.execute("SELECT id, event_name, event_type, event_date, event_description, notify_email FROM events WHERE user_id = ?", session["user_id"])
        event = []
        for row in rows:
            if row["notify_email"] == "True":
                notif_icon = "fa-solid fa-bell fa-shake"
            elif row["notify_email"] == "False":
                notif_icon = "fa-solid fa-bell-slash"
            event.append({
                "id": row["id"],
                "time": row["event_date"],
                "type": row["event_type"],
                "cls": theme_color[row["event_type"]],
                "name": row["event_name"],
                "details": row["event_description"],
                "icon": event_icons[row["event_type"]],
                "notify_icon": notif_icon
            })
        return Response(json.dumps(event), mimetype='application/json')


    now = date.today().strftime("%B %d, %Y")
    long_events = db.execute("SELECT id, event_name, event_type, event_date_start, event_date_end, event_description, notify_email FROM long_events WHERE user_id = ? ORDER BY event_date_start", session["user_id"])

    # Some tidyup so the data are more accesible and easy to read fo users
    for row in long_events:
        row["event_date_start"] = datetime.strptime(row["event_date_start"], "%Y-%m-%d").strftime("%d %B %Y")
        row["event_date_end"] = datetime.strptime(row["event_date_end"], "%Y-%m-%d").strftime("%d %B %Y")
        row["event_color"] = theme_color[row["event_type"]]
        row["event_icon"] = event_icons[row["event_type"]]
    return render_template("events.html",  now=now, long_events=long_events)

@app.route("/events/add-event", methods=["GET","POST"])
@login_req
def add_event():

    # User inputted the form
    if request.method == "POST":

        #Assign variables
        event_name = request.form.get("event_name")
        event_desc = request.form.get("event_desc")
        event_type = request.form.get("categories")
        event_notify_email = request.form.get("email_reminder")
        # Check user's compliance
        if not event_name:
            flash("Please input your event's name")
            return redirect("/events/add-event")
        if len(event_name) > 50:
            flash("Your event name exceeds 50 character")
            return redirect("/events/add-event")
        if not event_desc:
            event_desc = "no details"
        if not event_type:
            event_type = "Others"
        if not event_notify_email:
            event_notify_email = "False"

        # One-day events
        if request.form.get("event_date"):
            db.execute("INSERT INTO events (user_id, event_name, event_type, event_date, event_description, notify_email) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], event_name, event_type, request.form.get("event_date"), event_desc, event_notify_email)
            flash("Event added!")
            return redirect("/events")

        # Multi-day Events
        elif request.form.get("event_start_date"):
            # Check user's compliance
            event_start_date = request.form.get("event_start_date")
            event_end_date = request.form.get("event_end_date")
            if not event_end_date:
                flash("Please input your event's end date")
                return redirect("/events/add-event")

            # Start date should be earlier than the end date
            if datetime.strptime(event_start_date, "%Y-%m-%d") >= datetime.strptime(event_end_date, "%Y-%m-%d"):
                flash("Invalid long event : End date is earlier than start date or the end date is the same with the start date")
                return redirect("/events/add-event")

            # Insert into the database
            db.execute("INSERT INTO long_events (user_id, event_name, event_type, event_date_start, event_date_end, event_description, notify_email) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], event_name, event_type, request.form.get("event_start_date"), event_end_date, event_desc, event_notify_email)

            flash("Long event added")
            return redirect("/events")

        # No date inputted
        else:
            flash ("Please input your event's date")
            return redirect("/events/add-event")

    types = theme_color.keys()
    now = date.today().strftime("%Y-%m-%d")

    return render_template("add-events.html", types=types, now=now)

@app.route("/events/del-long-event", methods=["POST"])
@login_req
def del_long_ev():
    # Get the form data
    id = request.form.get("del_long_event_id")
    name = request.form.get("del_long_event_name")

    # Remove from the database
    db.execute("DELETE FROM long_events WHERE id = ?", id)
    flash(name +" successfully deleted!")
    return redirect("/events")

@app.route("/events/del-short-event", methods=["POST"])
@login_req
def del_short_ev():
    # Get the selected data event to be deleted
    id = request.form.get("del_event_id")
    name = request.form.get("del_event_name")

    # If it's an automatic added event from someone birthday notification, update their table data
    if db.execute("SELECT * FROM friends WHERE birthday_event_id = ?", id):
        db.execute("UPDATE friends SET birthday_event_id = null WHERE birthday_event_id = ?", id)

    # Remove from the database
    db.execute("DELETE FROM events WHERE id = ?", id)
    flash(name +" successfully deleted!")
    return redirect("/events")

@app.route("/events/edit-short-event", methods=["GET","POST"])
@login_req
def edit_short_ev():

    # User clicked from events.html
    if request.method == "POST":
        id = request.form.get("edit_event_id")

        # Get the necessary data for
        # the initial value of the selected event
        now = date.today()
        now = now.strftime("%Y-%m-%d")
        event = db.execute("SELECT * FROM events WHERE id = ?", id)[0]

        types = theme_color.keys()
        return render_template("edit-short-event.html", event=event, types=types, now=now)

    # User done filling the edit form and clicked submit
    submit = request.args.get("submit")

    # User clicked cancel
    if submit == "cancel":
        flash("Edit event canceled")
        return redirect("/events")

    # User clicked edit event
    # Get the value from the form
    id = request.args.get("event_id")
    event_name = request.args.get("event_name")
    event_date = request.args.get("event_date")
    event_desc = request.args.get("event_desc")
    event_type = request.args.get("event_type")
    notify_email = request.args.get("email_reminder")

    # Check user's compliance
    if not event_name:
        flash("Please input your event's name, edit failed")
        return redirect("/events")
    if len(event_name) > 50:
        flash("Your event name exceeds 50 character, edit failed")
        return redirect("/events")
    if not event_desc:
        event_desc = "no details"
    if not event_type:
        flash("Please input your event's type, edit failed")
        return redirect("/events")
    if not event_date:
        flash ("Please input your event's date, edit failed")
        return redirect("/events/add-event")
    if not notify_email:
        notify_email = "False"

    # User tried to edit an official friend birthday event date
    if db.execute("SELECT * FROM friends WHERE birthday_event_id = ?", id):
        db.execute("UPDATE events SET event_description = ? WHERE id = ?", event_desc, id)
        flash("You can't edit automatic events' attribute (except their description)")
        return redirect("/events")

    # Update the table
    db.execute("UPDATE events SET event_name = ?, event_type = ?, event_date = ?, event_description = ?, notify_email = ? WHERE id = ?", event_name, event_type, event_date, event_desc, notify_email, id)
    flash('"' + event_name + '" edited !')

    return redirect("/events")

@app.route("/events/edit-long-event", methods=["GET","POST"])
@login_req
def edit_long_ev():
    if request.method == "POST":
        id = request.form.get("edit_event_id")

        # Get the necessary data for the initial value of the selected event
        now = date.today().strftime("%Y-%m-%d")
        lastmonth = date.today().replace(day=1) - timedelta(days=1)
        event = db.execute("SELECT * FROM long_events WHERE id = ?", id)[0]

        types = theme_color.keys()

        return render_template("edit-long-event.html",  event=event, types=types, now=now, lastmonth=lastmonth)

    submit = request.args.get("action")

    # User clicked cancel
    if not submit:
        flash("Edit event canceled")
        return redirect("/events")

    # User clicked edit event
    # Get the value from the form
    id = request.args.get("event_id")
    event_name = request.args.get("event_name")
    event_start_date = request.args.get("event_start_date")
    event_end_date = request.args.get("event_end_date")
    event_desc = request.args.get("event_desc")
    event_type = request.args.get("event_type")
    notify_email = request.args.get("email_reminder")

    # Check user's compliance
    if not event_name:
        flash("Please input your event's name, edit failed")
        return redirect("/events")
    if len(event_name) > 50:
        flash("Your event name exceeds 50 character, edit failed")
        return redirect("/events")
    if not event_desc:
        event_desc = "no details"
    if not event_type:
        flash("Please input your event's type, edit failed")
        return redirect("/events")
    if not event_start_date or not event_end_date:
        flash ("Please input your event's date, edit failed")
        return redirect("/events")
    if datetime.strptime(event_start_date, "%Y-%m-%d") >= datetime.strptime(event_end_date, "%Y-%m-%d"):
        flash("Invalid long event : End date should be later than start date")
        return redirect("/events")
    if not notify_email:
        notify_email = "False"

    # Update the table
    db.execute("UPDATE long_events SET event_name = ?, event_type = ?, event_date_start = ?, event_date_end = ?, event_description = ?, notify_email = ? WHERE id = ?", event_name, event_type, event_start_date, event_end_date, event_desc, notify_email, id)
    flash('"' + event_name + '" edited !')

    return redirect("/events")

@app.route("/events/add-event/longevcheck")
@login_req
def addlongev():
    types = theme_color.keys()
    now = date.today().strftime("%Y-%m-%d")
    longevcheck = True
    return render_template("add-events.html", types=types, now=now, longevcheck=longevcheck)