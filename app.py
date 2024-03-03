from flask import Flask, render_template, redirect, flash, session
from models import db, connect_db, User, Feedback
from forms import RegistrationForm, LoginForm, DeleteForm, FeedbackForm
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["SECRET_KEY"] = "kumasan!"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///users_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

connect_db(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register_user():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        existing_user = User.query.filter_by(username=form.username.data).first()

        if existing_user is None:
            # Use the register class method to hash the password and save the user
            new_user = User.register(username, password, email, first_name, last_name)
            db.session.add(new_user)
            db.session.commit()

            session["username"] = username

            # Redirect to the secret page after successful registration
            flash("User registered successfully", "success")
            return redirect(f"/users/{username}")
        else:
            flash("That username is already registered!", "error")
    return render_template("registration.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    # Form will not validate?
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        valid_usr = User.authenticate(username, password)

        if valid_usr:
            session["username"] = username
            return redirect(f"/users/{username}")
        else:
            # If login is unsuccessful, display an error message
            flash("Invalid username or password!", "error")
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Logout route."""

    session.pop("username")
    return redirect("/")


@app.route("/users/<username>")
def show_user(username):
    """Example page for logged-in-users."""

    if "username" not in session or username != session["username"]:
        return redirect("/login")

    form = DeleteForm()
    user = User.query.get(username)

    return render_template("usr_info.html", user=user, form=form)


@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user & redirect to login."""

    if "username" not in session or username != session["username"]:
        return redirect("/login")

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    flash("User deleted successfully.", "success")
    return redirect("/")


@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def show_feedback_form(username):
    """Display a form to add feedback"""

    if "username" not in session or username != session["username"]:
        return redirect("/login")

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{username}")

    else:
        return render_template("/feedback/new_feedback.html", form=form)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def edit_feedback(feedback_id):
    """Display a form to edit feedback. Handles the form processing"""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        return redirect("/login")

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("/feedback/edit_feedback.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        return redirect("/login")

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")
