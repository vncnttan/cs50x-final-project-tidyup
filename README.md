<img src="./app/static/TidyupFullLogo.png">

# Tidyup!
#### Video Demo:  https://youtu.be/uRg5OgE7frI
#### Description:
Tidyup! is a web-based basic event scheduler and reminder that is easy-to-use, simple, and straightforward because tidyup! has already set event types with their corresponding colour and emoji. The downside of this is, your calendar and event are **not customizable or unique** per user. What unique in tidyup! is that tidy-up is *half a social media* too. You can **add users to get their social media data and their birthdate**. You can add their birthday to your event calendar automatically with just a single click. You will get a notifier from tidyup using email when the event occurs *(this feature require you to bind your account us   ing email)*.

## How to start the server?
#### Make sure you had install all of the requirements
- Install redis using `sudo apt-get install redis`
- The other can be installed with `pip install <package name>`

### Start running the server and setting up the celery and flask
##### Redis and Celery
1. Open up a terminal with ctrl + `
2. Start up redis server with `redis-server` on the terminal window
3. Open up new terminal and try `redis-cli ping` (If it succeed, it should reply back PONG). If it does not succeed:
    - Try to delete `dump.rdb` file
    - Try to update redis using `pip install redis --upgrade`
    - Try to `sudo apt-get install redis`
4. cd to the project directory and run celery beat with this command on the new terminal window: `celery -A app.celery beat --loglevel=INFO`
5. Open up new terminal, cd to the project directory and type this command `celery -A tasks.daily.celery worker --loglevel=INFO`
##### Flask
6. Open up a new terminal, cd to the project directory and type `flask run`
7. Click/copy the link or share it. The server is up and running, you can login through your gmail to receive notifications from email. For codespace sharing, don't forget to make the port visibility to be public


## Modify mailing sender
Default mail sender:
- Mail Sender = tidyupevent@gmail.com
- Web Password = oxswleqrbxvdugwo

## Some hard design/regrettable choices and some of the web weakness
1.	Server-side data-handling vs. Client-side

    I chose to do server-side data handling because:
    -	Minimize data loss
    -	It is easier to make and debug
    -	I was more familiar with it (because it was taught in CS50 on Finance PSET, I was more comfortable with it) and I prefer python than JavaScript syntax
    -	Hard to implement notifier using web (where email is not required)

    This was quite a regrettable choice because server-side data handling and operation come with some downside:
    -	It causes lags because it sends and receive too many requests from users to the server (request sent every time you want to add, edit, or delete events / friends)
    -	It loads slow and it’s amplified if multiple user log in and use tidyup
    -	Its advantage is more significant for more important application, e.g., ticketing system, etc. where money is involved
    -	Missed opportunity to familiar myself with JavaScript and client-side data handling e.g., IndexedDB

2. Celery beat and cron-job email notifier

        It was easier and safer to implement event notifier using celery beat and cron job, but it requires the server celery beat running every day. It also requires users to provide their email (binds and authenticates user email to prove it was theirs).
3. POST is used to render html on `app.route('events/edit-short-event')` and `app.route('events/edit-long-event')` because it have sensitive information that will be put in the URL (the event id) if it uses the GET method. Irresponsible person can use it to access other events that belong to someone else by changing the event id on the url. But, then, the method that was used to submit the edit events form is GET, so, someone ca be fooled to editing their event if they click a naughty link. (Even though it was unlikely because then they need to have everything in the link like the event date, event name, etc)
4. It was innefective. Some codes can be shortened and/or changed to be more effective. Some function are repeated multiple time with slight/no changes at all. There was definitely many way to make all of this code shortened.
5. It will be an easy fix but the user id was shown on the menu offcanvas should be hashed because it will be more prone to hackers. Now, the user id that was shown was the core user id that connects everything on the users database (including emails, hash password, events, friends, etc.)

To set up the mailing, go to **email.py** and change the the *mail username* and *mail password* on the mail config

## What each of the file does
Let's group the file to sections that is easier to disect
### Celery and Redis Configuration
For some system running in the server background. So, even though no one clicked the link, the server that up and run can execute program to send email for whoever event was that day
```
1. celeryconfig.py: Configure celery settings (How the schedule works, in this case, using cron job, how often is it called? everyday. When the celery is called? Every 00:00)
2. config.py: Configure redis settings and connect redis server to our main app and celery
3. celerybeat-schedule.bak: Default celery-beat service
4. celerybeat-schedule.dat: Default celery-beat service
5. celerybeat-schedule.dir: Default celery-beat service
6. tasks/daily.py: Configure celery worker. If the celery is called, what the program need to be run?
    - Delete outdated events
    - Mail people if they had an event that day
7. app/__init__.py: There is a celery in the main app, so the application celery can be made
```

### SQLite and Database Configuration
```
1. sql-commands.txt: To keep track of sql-commands (SQL .schema), made it easier to edit table and its content
2. users.db: Handle all of the database
    - users: Manage users and their hashed password
    - events: Manage one-day events
    - long_events: Manage multi-day events (has two event date, when it starts and when it ends)
    - friends: manage two interconnected users that has agree to be friend using the friend request
    - socials: Manage user's social data to be shared to their friends
    - invite_friend: Manage all pending requests
    - emails: Manage all user emails if the user have one
```

## The main app with Flask
### General
1. `app/templates/layout.html`: HTML Template Layout, including some javascript and css that is linked to the majorities on the HTML. Also the navbar, flash, and footer
2. `app/static/uplogo.png`: Tidyup logo for the web icon on top of the tab

### app/\_\_init\_\_.py (app.py)
The initial code that runs when flask run
1. Make and configure Flask
2. Make celery app
3. Configure SQL database
4. `@app.context_processor`: Get essential user data
5. `@app.route("/")`: Render home (index.html)
    - `app/templates/index.html`: user dashboard, show their today events and occuring multi-day events
    - `app/statis/indexHtml.js`
6. `@app.route("/logout")`: Logging out user
7. `@app.route("/edit-username")`: Editing username
    - GET: Render the `edit-username.html`
        - `app/templates/edit-username.html`: Input user editing
    - POST: Apply Changes

### opening.py
Register and login, something that user can access if they're not logged in
1. `@app.route("/landing")`: The main landing page:
    - GET: Render landing page
        - `app/templates/landing.html`: Tidyup! general description and preview for new user, also a register form
        - `app/static/tidyup-mockup.png`
    - POST: Register user and redirect them to their dashboard
2. `@app.route("/login")`
    - GET: Render login page
        -`app/templates/login.html`: Input login form
    - POST: Log user in then redirect them to the dashboard
3. `@app.route("/login/google")`
    - POST: Log or register in using google


### events.py
1. `@app.route("/events")`
    - GET: Render events page
        - `app/templates/events.html`: Calendar with events inside and list of long events
        - `app/static/calendar.js` Framework by ylli2000 : Make table to mock a calendar and events inside of it. There is also an offcanvas event details
        - `app/static/indexCalendar.js` Framework calendar renderer by ylli2000
        - `app/static/spinner.js` Framework spinner by ylli2000
        - `app/static/calendar.css` Framework calendar style by ylli2000
        - `app/static/themes.css` Event colors that was assigned
        - `app/static/ScriptsEventsHtml.js`: Manage offcanvas and the delete prompt
        - `app/static/events.js` JQUERY configuration to receive user events data from python
    - POST: Using Jquery, provide user's event data for the calendar
2. `@app.route("/events/add-event")`
    - GET: Render the add event form
        - `app/templates/add-events.html`: Add event form
        - `app/static/ScriptsAddEventHtml.js`: Clear date if animated tabs switched
        - `app/static/animatedTabs.css`: Tab by Kezz Bracey
    - POST: Add the event
3. `@app.route("/events/add-event/longevcheck")`
    - GET: Render the same event form, but with additional variable so the class that was checked first is the long event class
4. `@app.route("/events/del-long-event")`
    - POST: Delete Long Event
5. `@app.route("/events/del-short-event")`
    - POST: Delete short event
6. `@app.route("/events/edit-short-event")`
    - POST: Render the edit event form
        - `app/templates/edit-short-event.html`: Form that was defaulted to have the event details.
    - GET: Delete old event and make a new one with the new detail
7. `@app.route("/events/edit-long-event")`
    - POST: Render the edit event form (but with two dates)
        - `app/templates/edit-short-event.html`: Form that was defaulted to have the event details.
    - GET: Delete old event and make a new one with the new detail

### friends.py
1. `@app.route("/friends")`
    - GET: Render the friend page
        - `app/templates/friends.html`: Display friend list and social profile input form
        - `app/static/ScriptsFriendsHtml.js`: Make a prompt before deleting
    - POST: Update/add social profile to a user
2. `@app.route("/friends/edit-alias")`
    - GET: Render the edit-alias page for that friend
        - `app/templates/edit-alias.html`: Form edit alias
    - POST: Change the friend alias in the table
3. `@app.route("/friends/add-friend")`
    - GET: Render the add friend page
        - `app/templates/add-friend.html`: Form add friend
    - POST: Add the user friend to the pending invitation list
4. `@app.route("/friends/invitations")`
    - GET: Render the invitation page
        - `app/templates/invitations.html`: Show pending invitations from and to user
5. `@app.route("/friends/del-friend")`
    - POST: Delete that friend from a user friend list
6. `@app.route("/friends/invitations/cancel-inv")`
    - POST: Delete pending invitation
7. `@app.route("/friends/invitations/accept-inv")`
    - POST: Add the two id on their friend list
8. `@app.route("/friends/notify-birthday")`
    - GET: Automatically make the chosen user birthday event
    - POST: Delete said event
9. `@app.route("/friends/profile-view")`
    - GET: Preview your own profile that is seen by others

### helpers.py
Important function that was called in other functions multiple time
1. `login_req(f)`: Redirect to the landing page if user has not logged in
2. `next_birthday(dob)`: Find the next birthday event relative from today when the DOB is given
#TODO: GET dictionary pair event type with each color
3. `theme_color`: The dictionary pair of each the event type and their color
4. `status_color`: The dictionary pair of each the status type and their color
5. `event_icons`: The dictionary pair of each the event type and their emoji (This was added because this year CS50x's week 10 theme is about emoji)


## Credit
Special thanks to:
### David Christian
Early tester and design/color theme consultant
> "The color tones was too bright and contrast🧑‍🎨, try this color pallete instead 🖌️"
>
> "The text was too small 🤏, maybe consider making it bigger"

Socials:
- Instagram: [@davidchrs](https://www.instagram.com/davidchrs/)
- Discord: davidchrs#3439

### Bob Merlin
CS50 Alumni that help suggests ideas and features
> "I would just do it 🤷 and then see if you think you meet the requirements. If not you can always add more features ➕"
>
> "It depends on how you want to implement it, if you want to make it server-side you're on the right track. If you want to make it client-side you can use web-based database. Each on their own have their strengths 💪 and weaknesses. You can't always have the best of both worlds."

Socials:
- Discord: bob_merlin#8157

### ylli2000 and Kezz Bracey
for some of the code they left online for others to use and modify

### All of the web tester

### Professor David J. Malan and all CS50 staff
    I want to thank all of CS50 staff for making all of this possible and accesible to all people around the globe, especially beginners to try programming. This was designed very well and interactive. The staff too is very ready to help on technical things (When I couldn't configure the vscode on my pc) or even mentally. Not to forget all of the alumni that helps beginner on tasks and pset in the discord server without spoiling the solution :)

Vincent Tanjaya (vncnttan),
This was tidyup and this was cs50