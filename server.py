"""Server for pup journey app."""

from flask import Flask, render_template, json, jsonify, request, flash, session, redirect
import cloudinary.uploader
import os
from datetime import datetime

from model import connect_to_db, db, ma, app, PetSchema, CheckInSchema
import crud_bookmarks_lists
import crud_check_ins
import crud_comments
import crud_hikes_bookmarks_lists
import crud_hikes
import crud_pets
import crud_users

from jinja2 import StrictUndefined

app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

CLOUDINARY_KEY = os.environ["CLOUDINARY_KEY"]
CLOUDINARY_SECRET = os.environ["CLOUDINARY_SECRET"]
CLOUD_NAME = "hbpupjourney"


@app.route("/")
def homepage():
    """View homepage."""

    return render_template("homepage.html")


@app.route("/hikes")
def all_hikes():
    """View all hikes."""

    search_hikes = hikes = crud_hikes.get_hikes()
    states = crud_hikes.get_hike_states()
    cities = crud_hikes.get_hike_cities()
    areas = crud_hikes.get_hike_areas()
    parking = crud_hikes.get_hike_parking()

    return render_template(
        "all_hikes.html",
        search_hikes=search_hikes,
        hikes=hikes,
        states=states,
        cities=cities,
        areas=areas,
        parking=parking,
    )


@app.route("/dashboard")
def dashboard():
    """View dashboard."""

    if "user_email" in session:
        user = crud_users.get_user_by_email(session["user_email"])
        pets = crud_pets.get_pets_by_user_id(user.user_id)
        hikes = crud_hikes.get_hikes()
        check_ins = crud_check_ins.get_check_ins_by_user_id(user.user_id)
        bookmarks_lists = crud_bookmarks_lists.get_bookmarks_lists_by_user_id(
            user.user_id
        )

        return render_template("dashboard.html", pets=pets, hikes=hikes, check_ins=check_ins, bookmarks_lists=bookmarks_lists)
    else:
        flash("You must log in to view your dashboard.")

        return redirect("/")


@app.route("/hikes/search")
def find_hikes():
    """Search for hikes"""

    keyword = request.args.get("keyword", "")
    difficulty = request.args.get("difficulty", "")
    leash_rule = request.args.get("leash_rule", "")
    area = request.args.get("area", "")
    city = request.args.get("city", "")
    state = request.args.get("state", "")
    length_min = request.args.get("length_min", "")
    length_max = request.args.get("length_max", "")
    park = request.args.get("parking", "")

    search_hikes = crud_hikes.get_hikes_by_search(
        keyword, difficulty, leash_rule, area, city, state, length_min, length_max, park
    )
    hikes = crud_hikes.get_hikes()
    states = crud_hikes.get_hike_states()
    cities = crud_hikes.get_hike_cities()
    areas = crud_hikes.get_hike_areas()
    parking = crud_hikes.get_hike_parking()

    return render_template(
        "all_hikes.html",
        search_hikes=search_hikes,
        hikes=hikes,
        states=states,
        cities=cities,
        areas=areas,
        parking=parking,
    )


@app.route("/hikes/<hike_id>")
def show_hike(hike_id):
    """Show details on a particular hike."""

    hike = crud_hikes.get_hike_by_id(hike_id)
    hike_resources = hike.resources.split(",")
    comments = crud_comments.get_comment_by_hike_id(hike_id)

    logged_in_email = session.get("user_email")

    if logged_in_email is None:

        return render_template(
            "hike_details.html",
            hike=hike,
            hike_resources=hike_resources,
            comments=comments,
        )
    else:
        user = crud_users.get_user_by_email(logged_in_email)
        pets = crud_pets.get_pets_by_user_id(user.user_id)
        check_ins = crud_check_ins.get_check_ins_by_user_id_and_hike_id(
            user.user_id, hike.hike_id
        )

        sorted_check_ins = sorted(check_ins, key=lambda x: x.date_hiked, reverse=True)

        bookmarks_list_by_user = crud_bookmarks_lists.get_bookmarks_lists_by_user_id(
            user.user_id
        )
        bookmarks_lists_by_user_hike = (
            crud_bookmarks_lists.get_bookmarks_lists_by_user_id_and_hike_id(
                user.user_id, hike.hike_id
            )
        )

        return render_template(
            "hike_details.html",
            hike=hike,
            hike_resources=hike_resources,
            user=user,
            comments=comments,
            pets=pets,
            check_ins=sorted_check_ins,
            bookmarks_list_by_user=bookmarks_list_by_user,
            bookmarks_lists_by_user_hike=bookmarks_lists_by_user_hike,
        )


@app.route("/bookmarks")
def all_bookmarks():
    """View all bookmarks."""

    if "user_email" in session:
        user = crud_users.get_user_by_email(session["user_email"])
        bookmarks_lists = crud_bookmarks_lists.get_bookmarks_lists_by_user_id(
            user.user_id
        )

        return render_template("all_bookmarks.html", bookmarks_lists=bookmarks_lists)
    else:
        flash("You must log in to view your bookmarks.")
        return redirect("/")


@app.route("/add-bookmarks-list", methods=["POST"])
def add_bookmarks_list():
    """Create a bookmark list"""

    if "user_email" in session:
        user = crud_users.get_user_by_email(session["user_email"])
        bookmarks_list_name = request.form.get("bookmarks_list_name")
        hikes = []

        bookmarks_list = crud_bookmarks_lists.create_bookmarks_list(
            bookmarks_list_name, user.user_id, hikes
        )

        db.session.add(bookmarks_list)
        db.session.commit()

        flash(f"Success! {bookmarks_list_name} has been added to your bookmarks.")

        return redirect(request.referrer)
    else:
        flash("You must log in to add a bookmark list.")

        return redirect("/")


@app.route("/edit-bookmarks-list", methods=["POST"])
def edit_bookmarks_list():
    """Edit a bookmark list"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to edit a bookmarks list.")
    else:
        bookmarks_list_id = request.form.get("edit")
        bookmarks_list = crud_bookmarks_lists.get_bookmarks_list_by_bookmarks_list_id(
            bookmarks_list_id
        )
        bookmarks_list.bookmarks_list_name = request.form.get("bookmarks_list_name")

        flash(f"Success! Your list has been renamed to {bookmarks_list.bookmarks_list_name}.")

        db.session.commit()

    return redirect(request.referrer)


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
            result = cloudinary.uploader.upload(
                my_file,
                api_key=CLOUDINARY_KEY,
                api_secret=CLOUDINARY_SECRET,
                cloud_name=CLOUD_NAME,
            )

            pet_imgURL = result["secure_url"]
            img_public_id = result["public_id"]

        check_ins = []

        pet = crud_pets.create_pet(
            user,
            pet_name,
            gender,
            birthday,
            breed,
            pet_imgURL,
            img_public_id,
            check_ins,
        )
        db.session.add(pet)
        db.session.commit()
        flash(f"Success! {pet_name} profile has been added.")

        pet_schema = PetSchema()
        pet_json = pet_schema.dump(pet)

    # return jsonify({"success": True, "petAdded": pet_json})
    return redirect(request.referrer)


@app.route("/edit-pet", methods=["POST"])
def edit_pet():
    """Edit a pet"""

    # would be nice for this to be a react inline form editor

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to edit a pet profile.")
    else:
        # this would be better if user can edit one line at a time,
        # in case they want to keep some info and change/remove other info
        pet_id = request.form.get("edit")
        pet = crud_pets.get_pet_by_id(pet_id)

        pet.pet_name = request.form.get("pet_name")

        gender = request.form.get("gender")
        birthday = request.form.get("birthday")
        breed = request.form.get("breed")
        my_file = request.files["my_file"]

        if gender != "":
            pet.gender = gender
        if birthday != "":
            pet.birthday = birthday
        if breed != "":
            pet.breed = breed

        # if user uploads new image file, delete old image from cloudinary
        # then upload new image
        if my_file.filename != "":
            img_public_id = pet.img_public_id
            if img_public_id != None:
                cloudinary.uploader.destroy(
                    img_public_id,
                    api_key=CLOUDINARY_KEY,
                    api_secret=CLOUDINARY_SECRET,
                    cloud_name=CLOUD_NAME,
            )
            # save the uploaded file to Cloudinary by making an API request
            result = cloudinary.uploader.upload(
                my_file,
                api_key=CLOUDINARY_KEY,
                api_secret=CLOUDINARY_SECRET,
                cloud_name=CLOUD_NAME,
            )

            pet.pet_imgURL = result["secure_url"]
            pet.img_public_id = result["public_id"]

        flash(f"Success! Your {pet.pet_name}'s profile has been updated.")

        db.session.commit()

    return redirect(request.referrer)


@app.route("/delete-pet", methods=["POST"])
def delete_pet():
    """Delete a pet profile"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to delete a pet profile.")
    else:
        pet_id = request.form.get("delete")
        pet = crud_pets.get_pet_by_id(pet_id)
        img_public_id = pet.img_public_id
        if img_public_id != None:
            cloudinary.uploader.destroy(
                img_public_id,
                api_key=CLOUDINARY_KEY,
                api_secret=CLOUDINARY_SECRET,
                cloud_name=CLOUD_NAME,
            )
        flash(f"Success! {pet.pet_name} profile has been deleted.")

        db.session.delete(pet)
        db.session.commit()

    return redirect(request.referrer)


@app.route("/edit-check-in", methods=["POST"])
def edit_check_in():
    """Edit a check in"""

    # would be nice for this to be a react inline form editor

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to edit a check in.")
    else:
        # this would be better if user can edit one line at a time,
        # in case they want to keep some info and change/remove other info
        check_in_id = request.form.get("check_in_id")
        check_in = crud_check_ins.get_check_ins_by_check_in_id(check_in_id)

        date_hiked = request.form.get("date_hiked")
        
        if date_hiked == "":
            date_hiked = check_in.date_hiked

        date_started = request.form.get("date_started")

        if date_started == "":
            date_started = check_in.date_started

        date_completed = request.form.get("date_completed")

        if date_completed == "":
            date_completed = check_in.date_completed

        miles_completed = request.form.get("miles_completed")

        if miles_completed == "":
            miles_completed = check_in.miles_completed

        total_time = request.form.get("total_time")

        if total_time == "":
            total_time = check_in.total_time

        check_in.date_hiked = date_hiked
        check_in.date_started = date_started
        check_in.date_completed = date_completed
        check_in.miles_completed = miles_completed
        check_in.total_time = total_time

        flash(f"Success! Your check in has been updated.")

        db.session.commit()

    return redirect(request.referrer)


@app.route("/delete-check-in", methods=["POST"])
def delete_check_in():
    """Delete a check-in"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to delete a check in.")
    else:
        check_in_id = request.form.get("delete")
        check_in = crud_check_ins.get_check_ins_by_check_in_id(check_in_id)

        flash(
            f"Success! Check in at {check_in.hike.hike_name} by {check_in.pet.pet_name} has been deleted."
        )

        db.session.delete(check_in)
        db.session.commit()

    return redirect(request.referrer)


@app.route("/edit-comment", methods=["POST"])
def edit_comment():
    """Edit a comment"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to edit a bookmarks list.")
    else:
        comment_id = request.form.get("edit")
        comment = crud_comments.get_comment_by_comment_id(comment_id)
        comment.body = request.form.get("body")
        comment.edit = True
        comment.date_edited = datetime.now()

        flash(f"Success! Your comment has been updated.")

        db.session.commit()

    return redirect(request.referrer)


@app.route("/delete-comment", methods=["POST"])
def delete_comment():
    """Delete a comment"""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to delete a comment.")
    else:
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
        bookmarks_list_id = request.form.get("delete")
        bookmarks_list = crud_bookmarks_lists.get_bookmarks_list_by_bookmarks_list_id(
            bookmarks_list_id
        )
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
        hike_id, bookmarks_list_id = request.form.get("delete").split(",")
        hike = crud_hikes.get_hike_by_id(hike_id)
        bookmarks_list = crud_bookmarks_lists.get_bookmarks_list_by_bookmarks_list_id(
            bookmarks_list_id
        )
        hikes_bookmarks_list = crud_hikes_bookmarks_lists.get_hike_bookmarks_list_by_hike_id_bookmarks_list_id(
            hike_id, bookmarks_list_id
        )

        flash(
            f"Success! {hike.hike_name} has been removed from {bookmarks_list.bookmarks_list_name}."
        )

        db.session.delete(hikes_bookmarks_list)
        db.session.commit()

    return redirect(request.referrer)


@app.route("/check-in", methods=["POST"])
def add_check_in():
    """Add check in for a hike."""

    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to check in.")
    else:
        hike_id = request.form.get("hike_id")
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

        check_in = crud_check_ins.create_check_in(
            hike,
            pet,
            date_hiked,
            date_started,
            date_completed,
            miles_completed,
            total_time,
        )
        db.session.add(check_in)
        db.session.commit()
        flash(f"Success! {pet.pet_name} has been checked into {hike.hike_name}.")

    return redirect(request.referrer)


@app.route("/add-hike", methods=["POST"])
def add_hike_to_bookmark():
    """Add hike to a bookmarks list"""
    logged_in_email = session.get("user_email")

    if logged_in_email is None:
        flash("You must log in to bookmark a hike.")
    else:
        hike_id = request.form.get("hike_id")
        user = crud_users.get_user_by_email(logged_in_email)
        hike = crud_hikes.get_hike_by_id(hike_id)
        bookmarks_list_id = request.form.get("bookmarks_list_id")
        bookmarks_list_name = request.form.get("bookmarks_list_name")

        if bookmarks_list_id != None and bookmarks_list_id != "":
            hike_bookmark = crud_hikes_bookmarks_lists.create_hike_bookmarks_list(hike_id, bookmarks_list_id)
        else:
            hikes = [hike]
            hike_bookmark = crud_bookmarks_lists.create_bookmarks_list(
                bookmarks_list_name, user.user_id, hikes
            )

        db.session.add(hike_bookmark)
        db.session.commit()

        flash(
            f"A bookmark to {hike.hike_name} has been added to your list."
        )

    return redirect(request.referrer)


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

        comment = crud_comments.create_comment(
            user, hike, body, date_created, edit, date_edited
        )
        db.session.add(comment)
        db.session.commit()

        flash("Your comment has been added.")

    return redirect(f"/hikes/{hike_id}")


@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud_users.get_user_by_email(email)
    if user:
        flash(
            "There is already an account associated with that email. Please try again."
        )
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

    return redirect(request.referrer)


@app.route("/logout")
def process_logout():
    """Log user out of site.

    Delete the login session
    """

    del session["login"]
    del session["user_email"]
    flash("Successfully logged out!")
    return redirect("/")


@app.route("/pets.json")
def get_pets_json():
    """Return a JSON response with all pets given user."""

    logged_in_email = session.get("user_email")

    user = crud_users.get_user_by_email(logged_in_email)
    pets = crud_pets.get_pets_by_user_id(user.user_id)

    pets_schema = PetSchema(many=True)
    pets_json = pets_schema.dump(pets)

    return jsonify({"pets": pets_json})


@app.route("/check-ins-by-user.json")
def get_check_ins_by_user_json():
    """Return a JSON response with all check ins for a pet."""

    logged_in_email = session.get("user_email")

    user = crud_users.get_user_by_email(logged_in_email)
    check_ins_by_user = crud_check_ins.get_check_ins_by_user_id(user.user_id)

    check_in_schema = CheckInSchema(many=True)
    check_ins_by_user_json = check_in_schema.dump(check_ins_by_user)

    return jsonify({"checkIns": check_ins_by_user_json})


@app.route("/check-ins-by-pets.json")
def get_check_ins_by_pets_json():
    """Return a JSON response with all check ins for each pet."""

    logged_in_email = session.get("user_email")

    user = crud_users.get_user_by_email(logged_in_email)
    pets = crud_pets.get_pets_by_user_id(user.user_id)
    check_ins_by_user = crud_check_ins.get_check_ins_by_user_id(user.user_id)

    check_in_data = []

    for pet in pets:
        pet_data = {"pet_id": pet.pet_id, "pet_name": pet.pet_name, "data": []}

        sorted_check_ins = sorted(pet.check_ins, key=lambda x: x.date_hiked, reverse=True)

        for check_in in sorted_check_ins:
            pet_data["data"].append({"date_hiked": check_in.date_hiked.isoformat(), "miles_completed": check_in.miles_completed})
        
        check_in_data.append(pet_data)



    # for check_in in check_ins_by_user:
    #     check_in_data = {}
    #     check_in_data["petCheckIns"][check_in.pet_id]["date_hiked"].append(check_in.date_hiked)
    #     check_in_data["petCheckIns"][check_in.pet_id]["miles_completed"].append(check_in.miles_completed)
        

    # check_in_schema = CheckInSchema(many=True)
    # check_ins_by_user_json = check_in_schema.dump(check_ins_by_user)

    return jsonify({"petCheckIns": check_in_data})


# @app.route("/pet-check-ins.json")
# def get_pet_check_ins_json():
#     """Return a JSON response with all check ins for a pet."""

#     logged_in_email = session.get("user_email")

#     user = crud_users.get_user_by_email(logged_in_email)
    # pets = crud_pets.get_pets_by_user_id(user.user_id)
    # pets_json = []

    # for pet in pets:
    #     if pet.birthday != None:
    #         birthday = pet.birthday.strftime("%b %d, %Y")
    #     else:
    #         birthday = pet.birthday
    #     pets_json.append(
    #         {
    #             "pet_id": pet.pet_id,
    #             "user_id": pet.user_id,
    #             "pet_name": pet.pet_name,
    #             "gender": pet.gender,
    #             "birthday": birthday,
    #             "breed": pet.breed,
    #             "pet_imgURL": pet.pet_imgURL,
    #             "img_public_id": pet.img_public_id,
    #         }
    #     )

    # return jsonify({"pets": pets_json})
    # pass


@app.route("/hike-check-ins.json")
def get_hike_check_ins_json():
    """Return a JSON response with all check ins for a hike/user."""

    # logged_in_email = session.get("user_email")

    # user = crud_users.get_user_by_email(logged_in_email)
    # pets = crud_pets.get_pets_by_user_id(user.user_id)
    # pets_json = []

    # for pet in pets:
    #     if pet.birthday != None:
    #         birthday = pet.birthday.strftime("%b %d, %Y")
    #     else:
    #         birthday = pet.birthday
    #     pets_json.append(
    #         {
    #             "pet_id": pet.pet_id,
    #             "user_id": pet.user_id,
    #             "pet_name": pet.pet_name,
    #             "gender": pet.gender,
    #             "birthday": birthday,
    #             "breed": pet.breed,
    #             "pet_imgURL": pet.pet_imgURL,
    #             "img_public_id": pet.img_public_id,
    #         }
    #     )

    # return jsonify({"pets": pets_json})
    pass


if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
