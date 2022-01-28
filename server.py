"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect)
import cloudinary.uploader
import os
from datetime import datetime

from model import connect_to_db, db
import crud_bookmarks_lists
import crud_check_ins
import crud_comments
import crud_hikes_bookmarks_lists
import crud_hikes
import crud_pets
import crud_users

from jinja2 import StrictUndefined

CLOUDINARY_KEY = os.environ["CLOUDINARY_KEY"]
CLOUDINARY_SECRET = os.environ["CLOUDINARY_SECRET"]
CLOUD_NAME = "hbpupjourney"

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage."""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        return render_template("homepage.html")
    else:
        user = crud_users.get_user_by_email(logged_in_email)
        pets = crud_pets.get_pets_by_user_id(user.user_id)
        return render_template("homepage.html", pets=pets)


@app.route("/hikes")
def all_hikes():
    """View all hikes."""

    hikes = crud_hikes.get_hikes()

    return render_template("all_hikes.html", hikes=hikes)


@app.route("/hikes/<hike_id>")
def show_hike(hike_id):
    """Show details on a particular hike."""

    hike = crud_hikes.get_hike_by_id(hike_id)
    hike_resources = hike.resources.split(",")
    comments = crud_comments.get_comment_by_hike_id(hike_id)

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        
        return (render_template("hike_details.html", hike=hike,
                                                    hike_resources=hike_resources,
                                                    comments=comments))
    else:
        user = crud_users.get_user_by_email(logged_in_email)
        pets = crud_pets.get_pets_by_user_id(user.user_id)
        check_ins = crud_check_ins.get_check_ins_by_user_id_and_hike_id(user.user_id, hike.hike_id)

        sorted_check_ins = sorted(check_ins, key=lambda x: x.date_hiked, reverse=True)

        bookmarks_list_by_user = crud_bookmarks_lists.get_bookmarks_lists_by_user_id(user.user_id)
        bookmarks_lists_by_user_hike = crud_bookmarks_lists.get_bookmarks_lists_by_user_id_and_hike_id(user.user_id, hike.hike_id)
        
        return (render_template("hike_details.html", hike=hike,
                                                    hike_resources=hike_resources,
                                                    user=user,
                                                    comments=comments,
                                                    pets=pets,
                                                    check_ins=sorted_check_ins,
                                                    bookmarks_list_by_user=bookmarks_list_by_user,
                                                    bookmarks_lists_by_user_hike=bookmarks_lists_by_user_hike))


@app.route("/bookmarks")
def all_bookmarks():
    """View all bookmarks."""

    if "user_email" in session:
        user = crud_users.get_user_by_email(session["user_email"])
        bookmarks_lists = crud_bookmarks_lists.get_bookmarks_lists_by_user_id(user.user_id)

        return render_template("all_bookmarks.html", bookmarks_lists=bookmarks_lists)
    else:
        flash("You must log in to view your bookmarks.")
        return redirect("/")


@app.route("/add-bookmarks-list", methods=["POST"])
def add_bookmarks_list():
    """Create a bookmark list"""

    if "user_email" in session:
        user = crud_users.get_user_by_email(session["user_email"])
        user_id = user.user_id
        bookmarks_list_name = request.form.get("bookmarks_list_name")
        hikes = []
        bookmarks_list = crud_bookmarks_lists.create_bookmarks_list(bookmarks_list_name, user_id, hikes)
        db.session.add(bookmarks_list)
        db.session.commit()
        flash(f"Success! {bookmarks_list_name} has been added to your bookmarks.")
        return redirect("/bookmarks")
    else:
        flash("You must log in to add a bookmark list.")
        return redirect("/")


@app.route("/add-pet", methods=["POST"])
def add_pet():
    """Create a pet profile"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to add a pet profile.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)

        pet_name = request.form.get("pet_name")
        gender = request.form.get("gender")

        if gender == "":
            gender = None

        birthday = request.form.get("birthday")

        if birthday == "":
            birthday = None

        breed = request.form.get("breed")

        if breed == "":
            breed = None

        my_file = request.files["my_file"]

        if my_file.filename == "":
            pet_imgURL = None
            img_public_id = None
        else:
            # save the uploaded file to Cloudinary by making an API request
            result = cloudinary.uploader.upload(my_file,
                                                api_key=CLOUDINARY_KEY,
                                                api_secret=CLOUDINARY_SECRET,
                                                cloud_name=CLOUD_NAME)

            pet_imgURL = result["secure_url"]
            img_public_id = result["public_id"]

        check_ins = []

        pet = crud_pets.create_pet(user, pet_name, gender, birthday, breed, pet_imgURL, img_public_id, check_ins) # add img_public_id
        db.session.add(pet)
        db.session.commit()
        flash(f"Success! {pet_name} profile has been added.")

    return redirect("/")


@app.route("/delete-pet", methods=["POST"])
def delete_pet():
    """Delete a pet profile"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to delete a pet profile.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)

        pet_id = request.form.get("delete")
        pet = crud_pets.get_pet_by_id(pet_id)
        img_public_id = pet.img_public_id
        if img_public_id != None:
            cloudinary.uploader.destroy(img_public_id,
                                        api_key=CLOUDINARY_KEY,
                                        api_secret=CLOUDINARY_SECRET,
                                        cloud_name=CLOUD_NAME)
        flash(f"Success! {pet.pet_name} profile has been deleted.")

        db.session.delete(pet)
        db.session.commit()

    return redirect("/")


@app.route("/delete-check-in", methods=["POST"])
def delete_check_in():
    """Delete a check-in"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to delete a check in.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)

        check_in_id = request.form.get("delete")
        check_in = crud_check_ins.get_check_ins_by_check_in_id(check_in_id)

        flash(f"Success! Check in at {check_in.hike.hike_name} by {check_in.pet.pet_name} has been deleted.")
        
        db.session.delete(check_in)
        db.session.commit()

    return redirect(request.referrer)


@app.route("/delete-comment", methods=["POST"])
def delete_comment():
    """Delete a comment"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to delete a comment.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)

        comment_id = request.form.get("delete")
        comment = crud_comments.get_comment_by_comment_id(comment_id)

        flash(f"Success! Your comment has been deleted.")

        db.session.delete(comment)
        db.session.commit()

    return redirect(request.referrer)


@app.route("/delete-bookmarks-list", methods=["POST"])
def delete_bookmarks_list():
    """Delete a bookmarks list"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to delete a bookmarks list.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)

        bookmarks_list_id = request.form.get("delete")
        bookmarks_list = crud_bookmarks_lists.get_bookmarks_list_by_bookmarks_list_id(bookmarks_list_id)
        bookmarks_list.hikes.clear()

        flash(f"Success! Your {bookmarks_list.bookmarks_list_name} has been deleted.")

        db.session.delete(bookmarks_list)
        db.session.commit()
    
    return redirect(request.referrer)


@app.route("/remove-hike", methods=["POST"])
def remove_hike():
    """Delete a hike from a bookmarks list"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to remove a hike from your bookmarks.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)

        hike_id, bookmarks_list_id = request.form.get("delete").split(",")
        hike = crud_hikes.get_hike_by_id(hike_id)
        bookmarks_list = crud_bookmarks_lists.get_bookmarks_list_by_bookmarks_list_id(bookmarks_list_id)
        hikes_bookmarks_list = crud_hikes_bookmarks_lists.get_hike_bookmarks_list_by_hike_id_bookmarks_list_id(hike_id, bookmarks_list_id)

        flash(f"Success! {hike.hike_name} has been removed from {bookmarks_list.bookmarks_list_name}.")

        db.session.delete(hikes_bookmarks_list)
        db.session.commit()
        

    return redirect(request.referrer)


@app.route("/hikes/<hike_id>/check-in", methods=["POST"])
def add_check_in(hike_id):
    """Add check in for a hike."""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to check in.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)
        hike = crud_hikes.get_hike_by_id(hike_id)
        pet_id = request.form.get("pet_id")
        pet = crud_pets.get_pet_by_id(pet_id)
        date_hiked = request.form.get("date_hiked")
        date_started = request.form.get("date_started")

        if date_started == "":
            date_started = None

        date_completed = request.form.get("date_completed")

        if date_completed == "":
            date_completed = None

        miles_completed = request.form.get("miles_completed")

        if miles_completed == "":
            miles_completed = None

        total_time = request.form.get("total_time")

        if total_time == "":
            total_time = None

        check_in = crud_check_ins.create_check_in(hike, pet, date_hiked, date_started, date_completed, miles_completed, total_time)
        db.session.add(check_in)
        db.session.commit()
        flash(f"Success! {pet.pet_name} has been checked into {hike.hike_name}.")

    return redirect(f"/hikes/{hike_id}") 


@app.route("/hikes/<hike_id>/bookmark", methods=["POST"])
def add_hike_to_bookmark(hike_id):
    """Add hike to a bookmarks list"""
    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to bookmark a hike.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)
        hike = crud_hikes.get_hike_by_id(hike_id)
        bookmarks_list_name = request.form.get("bookmarks_list_name")

        # check list of all of user's bookmarks lists
        # if bookmarks list object exists, add hike to bookmarks list
        # if not, create bookmarks list then add hike
        bookmarks_lists_names_by_user = crud_bookmarks_lists.get_names_of_bookmarks_lists_by_user_id(user.user_id)

        if bookmarks_list_name in bookmarks_lists_names_by_user:
            existing_bookmarks_list_id = crud_bookmarks_lists.get_bookmarks_list_by_user_id_and_bookmarks_list_name(user.user_id, bookmarks_list_name).bookmarks_list_id
            hike_bookmark = crud_hikes_bookmarks_lists.create_hike_bookmarks_list(hike_id, existing_bookmarks_list_id)
        else:
            hikes = [hike]
            hike_bookmark = crud_bookmarks_lists.create_bookmarks_list(bookmarks_list_name, user.user_id, hikes)
        
        db.session.add(hike_bookmark)
        db.session.commit()

        flash(f"A bookmark to {hike.hike_name} has been added to your {bookmarks_list_name} bookmark list.")

    return redirect(f"/hikes/{hike_id}")



@app.route("/hikes/<hike_id>/comments", methods=["POST"])
def add_comment(hike_id):
    """Add a comment for a hike"""
    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to add a comment.")
    else:
        user = crud_users.get_user_by_email(logged_in_email)
        hike = crud_hikes.get_hike_by_id(hike_id)
        body = request.form.get("body")
        date_created = datetime.now()
        edit = False
        date_edited = None

        comment = crud_comments.create_comment(user, hike, body, date_created, edit, date_edited)
        db.session.add(comment)
        db.session.commit()

        flash("Your comment has been added.")

    return redirect(f"/hikes/{hike_id}")


# @app.route('/pets.json')
# def pets():
#     """Return a list of pet-info dictionary for all pets."""

#     pets = crud.get_pets()
#     pets_json = []

#     for pet in pets:
#         pets_json.append({"user_id": pet.user_id, "pet_name": pet.pet_name, "gender": pet.gender, "birthday": pet.birthday, "breed": pet.breed, "pet_imgURL": pet.pet_imgURL})

#     return jsonify(pets_json)


@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud_users.get_user_by_email(email)
    if user:
        flash("There is already an account associated with that email. Please try again.")
    else:
        user = crud_users.create_user(full_name, email, password)
        db.session.add(user)
        db.session.commit()
        flash("Success! Account created. Please log in.")

    return redirect("/")


@app.route("/login", methods=["POST"])
def process_login():
    """Process user login"""
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud_users.get_user_by_email(email)
    if not user or user.password != password:
        flash("The email or password is incorrect.")
    else:
        # Log in user by storing the user's email in session
        session["user_email"] = user.email
        session["login"] = True
        flash(f"Welcome back, {user.full_name}!")
    
    return redirect("/")


@app.route("/login", methods=["GET"])
def show_login():
    """Show login form."""

    return render_template("login.html")


@app.route("/logout")
def process_logout():
    """Log user out of site.

    Delete the login session
    """

    del session["login"]
    del session["user_email"]
    flash("Successfully logged out!")
    return redirect("/")


if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
