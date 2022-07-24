from cs50 import SQL
from flask import flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")

from app import app

@app.route("/landing", methods=["GET","POST"])
def landing():

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide username.")
            return redirect("/landing#register_section")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please provide password.")
            return redirect("/landing#register_section")

        password = request.form.get("password")
        if password != request.form.get("confirmation"):
            flash("Your confirmation password doesn't match.")
            return redirect("/landing#register_section")

        # Ensure username is not taken already
        elif len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))) == 1:
            flash("Username already taken")
            return redirect("/landing#register_section")

        # Ensure the password inputted complied to the requirements
        if len(password) < 8 or any(not c.isalnum for c in password) or not any(c.isnumeric for c in password):
            flash("Your password does not comply to the minimum requirements.")
            return redirect("/landing#register_section")

        # Enter values to the table database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        # Log in the user
        session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))[0]["id"]

        # Redirect user to home page
        flash("Registered!")
        return redirect("/")

    # User clicked from navbar
    print("landing")
    return render_template("landing.html")

@app.route("/login", methods=["GET","POST"])
def login():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username.")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password.")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Logged in!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")

@app.route("/login/google", methods=["POST"])
def auth_google():
    # Validate CSRF token!
    csrf_token_cookie = request.cookies.get('g_csrf_token')
    if not csrf_token_cookie:
        print('No CSRF token in Cookie.')
    csrf_token_body = request.form['g_csrf_token']
    if not csrf_token_body:
        print('No CSRF token in post body.')
    if csrf_token_cookie != csrf_token_body:
        print('Failed to verify double submit cookie.')

    # Get those token
    token = request.form["credential"]

    # Decode JWT by using google library:
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), "975330618542-vglsd8umiv11f5sl8k4ns5rh281f8fkv.apps.googleusercontent.com")

    # Get the required data
    email = idinfo["email"]
    email_id = idinfo["sub"]

    # Login, user id have been added in our database
    if len(db.execute("SELECT * FROM emails WHERE email_id = ?", email_id)) > 0:
        user_id = db.execute("SELECT user_id FROM emails WHERE email_id = ?", email_id)[0]["user_id"]

        # Remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to home page
        flash("We have found an account binded by this gmail account!")
        return redirect("/")

    try:
        # User is trying to bind account
        user_id = session["user_id"]
        flash("Account binded!")

    except KeyError:
        # There is no user_id in the session which means user is not trying to bind account to the gmail

        # Register, user id is not already in our database
        # Find a unique username
        name = idinfo["name"]
        for i in range(10):
            if len(db.execute("SELECT * FROM users WHERE username = ?", name)) == 0:
                break
            name = name + str(i)

        # Enter values to the user database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", name,
            generate_password_hash(name))

        # Enter values to the email database
        user_id = db.execute("SELECT seq from sqlite_sequence where name = 'users'")[0]["seq"]

        flash("Registered as a new account, your password for this account is " + name)


    # Tie the data in the email database with the user database
    db.execute("INSERT INTO emails (email_id, email_address, user_id) VALUES (?, ?, ?)", email_id, email, user_id)

    # Log in the user
    session["user_id"] = user_id


    return redirect("/")