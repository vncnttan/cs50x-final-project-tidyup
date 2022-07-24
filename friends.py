from cs50 import SQL
from datetime import datetime
from flask import flash , redirect, render_template , request, session, url_for
from helpers import login_req, status_color, next_birthday

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

from app import app

@app.route("/friends", methods=["GET","POST"])
@login_req
def friends():
    # Form in friend is to change or make new social data in the table
    if request.method == "POST":
        # Assign variables
        birthdate = request.form.get("birthday")
        status = request.form.get("status")
        custom_status = request.form.get("custom_status")
        instagram = request.form.get("instagram")
        whatsapp = request.form.get("whatsapp")

        # Replace some character
        instagram = instagram.replace("@","")
        whatsapp = whatsapp.replace("-","")

        # Check user's compliance
        if not birthdate:
            flash("Please input your birthdate")
            return redirect("/friends")
        if len(custom_status) > 20:
            custom_status = ""
        if not status:
            flash("Please input your status")
            return redirect("/friends")
        if whatsapp:
            if not whatsapp.isdigit():
                whatsapp = ""
                flash("Your whatsapp number contain non-digit, it's failed to be added on your profile")

        if len(db.execute("SELECT * FROM socials WHERE user_id = ?", session["user_id"])) > 0:
            db.execute("DELETE FROM socials WHERE user_id = ?", session["user_id"])

        # Update their birthday in other user's interface
        for row in db.execute("SELECT birthday_event_id FROM friends WHERE user_friend_id = ?", session["user_id"]):
            birthday = next_birthday(birthdate)
            db.execute("UPDATE events SET event_date = ? WHERE id = ?", birthday, row["birthday_event_id"])

        # Insert data to the socials table
        db.execute("INSERT INTO socials (user_id, birthday, status, custom_status, instagram, phone) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], birthdate, status, custom_status, instagram, whatsapp)
        return redirect("/friends/profile-view")

    # Using the GET method
    user_friends = db.execute("SELECT * FROM friends WHERE user_id = ?", session["user_id"])

    # Looping for all friend
    for row in user_friends:
        # Friend that was added by their ID
        friend_socials = db.execute("SELECT * FROM socials WHERE user_id = ?", row["user_friend_id"])[0]
        row["friend_name"] = db.execute("SELECT username FROM users WHERE id = ?", row["user_friend_id"])[0]["username"]
        row["birthday"] = datetime.strptime(friend_socials["birthday"], "%Y-%m-%d").strftime("%d %B %Y")
        row["status"] = friend_socials["status"]
        row["theme_status"] = status_color[friend_socials["status"]]
        if friend_socials["custom_status"]:
            row["custom_status"] = friend_socials["custom_status"]
        else:
            row["custom_status"] = "no status added"

        # Get user social profile data
        try:
            row["email"] = db.execute("SELECT * FROM emails WHERE user_id = ?", row["user_friend_id"])[0]["email_address"]
        except IndexError:
            pass
        row["instagram"] = friend_socials["instagram"]
        row["phone"] = friend_socials["phone"]
        if not row["alias"]:
            row["alias"] = row["friend_name"]

    # Assign data for the HTML
    friend_count = len(user_friends)

    # Make a list of all available status
    statuses = list(status_color)

    # Prepare the data for the social form below the friend list
    if len(db.execute("SELECT * FROM socials WHERE user_id = ?", session["user_id"])) == 0:
        profile_complete = False
        user_profile = {}
    else:
        profile_complete = True
        user_profile = db.execute("SELECT birthday, status, custom_status, instagram, phone FROM socials WHERE user_id = ?", session["user_id"])[0]
        try:
            user_profile["email"] = db.execute("SELECT email_address FROM emails WHERE user_id = ?", session["user_id"])[0]["email_address"]
        except IndexError:
            pass

    invitation_notif = len(db.execute("SELECT * FROM invite_friend WHERE invitee_id = ?", session["user_id"]))


    return render_template("friends.html", friends=user_friends, statuses=statuses, friend_count=friend_count, profile_complete=profile_complete, user_profile=user_profile, invitation_notif=invitation_notif)

@app.route("/friends/edit-alias", methods=["GET", "POST"])
@login_req
def edit_alias():
    if request.method == "POST":
        if request.form.get("action") == "cancel":
            return redirect("/friends")

        # Assign variables
        id = request.form.get("id")
        nickname = request.form.get("alias")

        #Check user's compliance
        if len(nickname) > 50:
            flash("Nickname inputted exceeds maximum character")
            return redirect(url_for('edit_alias', id=id))

        db.execute ("UPDATE friends SET alias = ? WHERE id = ?", nickname, id)
        flash("Nickname changed")
        return redirect("/friends")

    # User clicked edit alias symbol from user friend's offcanvas
    id = request.args.get("id")
    initial_nick = db.execute("SELECT alias FROM friends WHERE id = ?", id)[0]["alias"]
    if initial_nick == None:
        initial_nick = ""
    real_username = db.execute("SELECT username FROM users WHERE id = (SELECT user_friend_id FROM friends WHERE id = ?)", id)[0]["username"]

    return render_template("edit-alias.html", id=id, initial_nick=initial_nick, real_username=real_username)


@app.route("/friends/add-friend", methods=["GET","POST"])
@login_req
def add_friend():
    if request.method == "POST":
        # User clicked cancel
        if request.form.get("action") == "cancel":
            return redirect("/friends")

        # Assign variable
        add_input = request.form.get("auto_add_input")
        data_inputted = request.form.get("data-auto")

        # Check user's compliance
        if not data_inputted:
            flash("Please input your friend's data")
            return redirect("/friends/add-friend")
        elif not add_input:
            flash("Please input the adding method")
            return redirect("/friends/add-friend")

        # Get user id on the inputted data and check user's compliance
        if add_input == "user_id":
            friend_id = int(data_inputted)
            try:
                friend_id = db.execute("SELECT * FROM users WHERE id = ?", friend_id)[0]["id"]
            except IndexError:
                flash("Make sure your friend ID is valid")
                return redirect("/friends/invitations")
        # Sort things out for instagram
        elif add_input == "email":
            try:
                friend_id = db.execute("SELECT user_id FROM emails WHERE email_address = ?", data_inputted)[0]["user_id"]
            except IndexError:
                flash("The binded email account is not available in our database, please make sure your input is right and your friend have signed up on tidyup!")
                return redirect("/friends/invitations")
        elif add_input == "username":
            try:
                friend_id = db.execute("SELECT id FROM users WHERE username = ?", data_inputted)[0]["id"]
                print(friend_id)
            except IndexError:
                flash("There is no such username in our database, please check your spellings and try again.")
                return redirect("/friends/invitations")

        rows = db.execute("SELECT * FROM friends WHERE user_id = ?", session["user_id"])
        for row in rows:
            if friend_id == row["user_friend_id"]:
                flash("You already befriended " + db.execute("SELECT username FROM users WHERE user_id = ?", row["user_friend_id"][0]["username"]))
                return redirect("/friends/invitations")

        # No self-adding friend
        if friend_id == session["user_id"]:
            flash("I get that you are lonely having no friend, but you can't add yourself ;)")
            return redirect("/friends/invitations")

        # To avoid double invitations
        try:
            db.execute("SELECT * FROM invite_friend WHERE inviter_id = ? AND invitee_id = ?", session["user_id"], friend_id)[0]["id"]
        except IndexError:
            # So, no invitation has been sent yet, than insert it
            db.execute("INSERT INTO invite_friend (inviter_id, invitee_id) VALUES (?, ?)", session["user_id"], friend_id)

        flash("Friend invitation sent!")
        return redirect("/friends/invitations")

    return render_template("add-friend.html")

@app.route("/friends/invitations")
@login_req
def tidyupinv():

    invitesent = db.execute("SELECT invite_friend.id, users.username FROM users INNER JOIN invite_friend ON invite_friend.invitee_id = users.id WHERE invite_friend.inviter_id = ?", session["user_id"])
    inviteinbox = db.execute("SELECT invite_friend.id, users.username FROM users INNER JOIN invite_friend ON invite_friend.inviter_id = users.id WHERE invite_friend.invitee_id = ?", session["user_id"])
    inboxcount = len(inviteinbox)
    sentcount = len(invitesent)
    return render_template("invitation.html",  inviteinbox=inviteinbox, invitesent=invitesent, inboxcount=inboxcount, sentcount=sentcount)

@app.route("/friends/del-friend", methods=["POST"])
@login_req
def delfriend():
    id = int(request.form.get("del_friend_id"))
    friend_id = int(db.execute("SELECT user_friend_id FROM friends WHERE id = ?", id)[0]["user_friend_id"])

    # Deleting user's friend from our friend data
    db.execute ("DELETE FROM friends WHERE user_id = ? AND user_friend_id = ?", session["user_id"], friend_id)

    # Deleting user from our friend's friend data
    db.execute ("DELETE FROM friends WHERE user_id = ? AND user_friend_id = ?", friend_id, session["user_id"])
    flash("Friend Deleted")
    return redirect("/friends")

@app.route("/friends/invitations/cancel-inv", methods=["POST"])
@login_req
def cancelinv():
    inv_id = request.form.get("id")
    db.execute("DELETE FROM invite_friend WHERE id = ?", inv_id)
    flash("Invitation cancelled!")
    return redirect("/friends/invitations")

@app.route("/friends/invitations/accept-inv", methods=["POST"])
@login_req
def acceptinv():
    inv_id = request.form.get("id")
    invitation = db.execute("SELECT * FROM invite_friend WHERE id = ?", inv_id)[0]

    # Get inviter and invitee id
    inviter = invitation["inviter_id"]
    invitee = invitation["invitee_id"]

    # Insert all the required values to the database
    db.execute("INSERT INTO friends (user_id, user_friend_id) VALUES (?, ?)", inviter, invitee)
    db.execute("INSERT INTO friends (user_id, user_friend_id) VALUES (?, ?)", invitee, inviter)

    db.execute("DELETE FROM invite_friend WHERE id = ?", inv_id)
    flash("Friend added!")
    return redirect("/friends")

@app.route("/friends/notify-birthday", methods=["POST","GET"])
@login_req
def notifybirthday():
    # Cancel notify birthday
    if request.method == "POST":
        event_id = request.form.get("bdayeventid")
        db.execute("UPDATE friends SET birthday_event_id = null WHERE birthday_event_id = ?", event_id)
        db.execute("DELETE FROM events WHERE id = ?", event_id)
        return redirect("/friends")

    # Notify birthday
    # Get friend's data
    friend_id = request.args.get("friendid")
    friend_data = db.execute("SELECT username, birthday FROM socials INNER JOIN users ON users.id = socials.user_id WHERE socials.user_id = ?", friend_id)[0]

    # Important: friend_data["birthday"] is their DOB, for example May 25, 1999
    birthday = next_birthday(friend_data["birthday"])

    if len(db.execute("SELECT * FROM emails WHERE user_id = ?", session["user_id"])) == 1:
        email = "True"
    else:
        email = "False"

    db.execute("INSERT INTO events (user_id, event_name, event_type, event_date, event_description, notify_email) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], friend_data["username"] + "'s birthday", "Birthday", birthday, "no details", email)

    # Adding that to the birthday_event_id
    db.execute("UPDATE friends SET birthday_event_id = (select seq from sqlite_sequence where name = 'events') WHERE user_id = ? AND user_friend_id = ?", session["user_id"], friend_id)
    return redirect("/friends")

@app.route("/friends/profile-view")
@login_req
def profileview():
    profile = db.execute("SELECT * FROM socials WHERE user_id = ?", session["user_id"])[0]

    # Get the necessary data
    profile["birthday"] = datetime.strptime(profile["birthday"], "%Y-%m-%d").strftime("%d %B %Y")
    try:
        profile["email"] = db.execute("SELECT email_address FROM emails WHERE user_id = ?", session["user_id"])[0]["email_address"]
    except IndexError:
        pass
    profile["theme_status"] = status_color[profile["status"]]
    if not profile["custom_status"]:
        profile["custom_status"] = "no status added"
    return render_template("profile-view.html", profile=profile)