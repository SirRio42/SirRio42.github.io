from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQL database
db = SQL("sqlite:///campsites.db")


@app.route("/", methods=["GET"])
def index():

    # Display login when site is initially loaded
    if request.method == "GET":
        return render_template("login.html")


@app.route("/map", methods=["GET"])
def map():

    # Display login when site is initially loaded
    if request.method == "GET":
        return render_template("index.html")


@app.route("/campsites", methods=["GET"])
def campsites():

    # Display campsite resources
    if request.method == "GET":
        return render_template("campsites.html")


@app.route("/visited", methods=["GET", "POST"])
def visited():

    # Display list of visited campsites from campsites database
    if request.method == "GET":
        camps = db.execute("SELECT * FROM campsites ORDER BY internet DESC")
        return render_template("visited.html", camps=camps)

    # Ensure admin is logged in before allowing access to add or edit camps
    if request.method == "POST":
        if session["user_id"] == "Rio":
            return render_template("addcamp.html")
        else:
            return render_template("denied.html")


@app.route("/addcamp", methods=["GET", "POST"])
def addcamp():

    # Display add campsites form
    if request.method == "GET":
        return render_template("addcamp.html")

    # If form is submitted, insert new campsite into database and redirect back to visited page
    if request.method == "POST":
        db.execute("INSERT INTO campsites (name, location, description, internet) VALUES(?, ?, ?, ?)",
                    request.form.get("name"), request.form.get("location"), request.form.get("description"), request.form.get("internet"))
        return redirect("/visited")

@app.route("/edit", methods=["GET", "POST"])
def edit():

    # Display edit page
    if request.method == "GET":
        camps = db.execute("SELECT name FROM campsites")
        return render_template("edit.html", camps=camps)

    # If form is submitted, make changes to databse based on which fields were selected
    if request.method == "POST":
        if request.form.get("select_field") == "Name":
            db.execute("UPDATE campsites SET name = ? WHERE name = ?", request.form.get("edit"), request.form.get("select_camp"))
        elif request.form.get("select_field") == "Location":
            db.execute("UPDATE campsites SET location = ? WHERE name = ?", request.form.get("edit"), request.form.get("select_camp"))
        elif request.form.get("select_field") == "Description":
            db.execute("UPDATE campsites SET description = ? WHERE name = ?", request.form.get("edit"), request.form.get("select_camp"))
        elif request.form.get("select_field") == "Internet":
            db.execute("UPDATE campsites SET internet = ? WHERE name = ?", request.form.get("edit"), request.form.get("select_camp"))
        return redirect("/visited")

@app.route("/delete", methods=["GET", "POST"])
def delete():

    if request.method == "GET":
        camps = db.execute("SELECT name FROM campsites")
        return render_template("delete.html", camps=camps)

    if request.method == "POST":
        db.execute("DELETE FROM campsites WHERE name = ?", request.form.get("select_camp"))
        return redirect("/visited")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("wrong.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("wrong.html")

        # Query database for user data
        user_data = db.execute("SELECT * FROM login WHERE username = ?", request.form.get("username"))

        # Ensure username exists in databae and password is correct
        if len(user_data) != 1 or not check_password_hash(user_data[0]["hash"], request.form.get("password")):
            return render_template("wrong.html")
        else:
            # Remember which user is logged in
            session["user_id"] = request.form.get("username")
            return render_template("index.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


##@app.route("/register", methods=["GET", "POST"])
##def register():

##    if request.method == "GET":
##        return render_template("register.html")

##    if request.method == "POST":
##        hash = generate_password_hash(request.form.get("password"), method="pbkdf2:sha256", salt_length=8)
##        db.execute("INSERT INTO login (username, hash) VALUES(?, ?)", request.form.get("username"), hash)

##        return redirect("/")