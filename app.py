import os
import requests, json
from datetime import datetime
from flask_mail import Mail, Message
from apikey import API_SECRET_KEY
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError



from models import db, connect_db, season, User_Favorite, User, Recipe
from forms import UserAddForm, LoginForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# #mailserver
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# # app.config['MAIL_DEBUG'] = True
# app.config['MAIL_USERNAME'] = "clark.smith79@gmail.com"
# app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
# app.config['MAIL_DEFAULT_SENDER'] = "clark.smith79@gmail.com"
# mail = Mail(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///athomechef'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)


db.create_all()

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.first_name}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout') 
def logout():
    """Handle logout of user."""
    session.pop(CURR_USER_KEY)
    return redirect("/")


@app.route("/", methods=["GET"])
def show_homepage():
    """show homepage"""
    vars = season()
    session["season"] = vars[0]
    session["icon"] = vars[1]
    return render_template("home.html")

@app.route("/", methods=["POST"])
def get_results():
    """show homepage"""
    dish = request.form["dish"]
    diet = request.form["diet"]
 
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?query={dish}&diet={diet}&addRecipeInformation=true&apiKey={API_SECRET_KEY}")
    data = response.json()
  
    list = data["results"]
    results = [e for e in list]

    if not len(results):
        no_results = "No recipes available with that name, check your spelling"
    else:
        no_results = ""
    
    if g.user:
        if g.user.recipes:
            favorited_recipes = [recipe.recipe_id for recipe in g.user.recipes]
        else:
            favorited_recipes = None
    else:
        favorited_recipes = None
        
    return render_template("home.html", results = results, no_results= no_results, favorited_recipes = favorited_recipes)



@app.route("/dish/<int:dish_id>")
def show_dish(dish_id):
    """show recipe for specific dish"""
    response = requests.get(f"https://api.spoonacular.com/recipes/{dish_id}/information?&apiKey={API_SECRET_KEY}")
    dish = response.json()

   
    for step in dish["analyzedInstructions"]:
       steps = [ e["step"] for e in step["steps"] ]
    
    if g.user:
        if g.user.recipes:
            favorited_recipes = [recipe.recipe_id for recipe in g.user.recipes]
        else:
            favorited_recipes = None
    else: 
        favorited_recipes = None
        
    return render_template("dish.html", dish = dish, steps = steps, favorited_recipes = favorited_recipes)

@app.route("/dish/<int:dish_id>/grocerylist", methods=["POST"])
def send_grocery_list(dish_id):
    """ sends a grocery list email """
    if not g.user:
        flash("Access Denied Please Login First", "danger")
        return redirect("/login")

    response = requests.get(f"https://api.spoonacular.com/recipes/{dish_id}/information?&apiKey={API_SECRET_KEY}")
    dish = response.json()
    grocery_list = ''
    for ingredient in dish["extendedIngredients"]: 
        grocery_list += (f'<li>{ingredient["originalString"]}</li>')

    list_html = f'<ul> {grocery_list} </ul>'  
    print(list_html)

    msg = Message("Grocery List for Dish")
    msg.add_recipient(f'{g.user.email}')
    msg.html = list_html
    mail.send(msg)

    flash("Grocery list has been sent to your email address!", "success")

    return redirect(f"/dish/{dish_id}")

@app.route("/user")
def show_user_details():
    """show user details"""

    if not g.user:
        flash("Access Denied Please Login First", "danger")
        return redirect("/login")

    else:
        favorites = User_Favorite.query.filter(User_Favorite.user_id == g.user.id).order_by(
        User_Favorite.timestamp.desc()).all()
        print(favorites)
        ordered_recipe_ids = [ favorite.recipe_id for favorite in favorites]
        print(ordered_recipe_ids)
        ordered_favorites = [Recipe.query.get(id) for id in ordered_recipe_ids]
        print(ordered_favorites)
        return render_template("users/details.html", favorites = ordered_favorites )


@app.route("/favorite/<int:dish_id>", methods=["POST"])
def add_favorite_dish(dish_id):
    """add favorite dish"""

    if not g.user:
        flash("Access Denied Please Login First", "danger")
        return redirect("/login")
        
        
    if not Recipe.query.get(dish_id):
        response = requests.get(f"https://api.spoonacular.com/recipes/{dish_id}/information?&apiKey={API_SECRET_KEY}")
        dish = response.json()
        new_recipe = Recipe(recipe_id = dish_id, title = dish["title"], image= dish["image"])
        db.session.add(new_recipe)
        db.session.commit()
        
    timestamp = datetime.utcnow()
    new_favorite = User_Favorite(user_id = g.user.id, timestamp = timestamp, recipe_id = dish_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(message="Dish Favorited")

@app.route("/removefavorite/<int:dish_id>", methods=["POST"])
def remove_favorite_dish(dish_id):
    """remove favorite dish"""

    if not g.user:
        flash("Access Denied Please Login First", "danger")
        return redirect("/login")

    favorite = User_Favorite.query.filter(
        User_Favorite.recipe_id == dish_id, User_Favorite.user_id == g.user.id).first()

    db.session.delete(favorite)
    db.session.commit()

    return jsonify(message="Removed Favorite")


@app.route("/seasonal")
def show_seasonal_dish():
    """show random seasonal dish"""
    season = session["season"]
    response = requests.get(f"https://api.spoonacular.com/recipes/random?tags={season}&number=10&apiKey={API_SECRET_KEY}")
    data = response.json()


    list = data["recipes"]
    results = [e for e in list]
    
    if g.user:
        if g.user.recipes:
            favorited_recipes = [recipe.recipe_id for recipe in g.user.recipes]
        else:
            favorited_recipes = None
    else:
        favorited_recipes = None
        
    return render_template("seasonal.html", results = results, favorited_recipes = favorited_recipes)


@app.route("/user/deleteprofile", methods=["GET"])
def show_delete_profile():
    """delete user profile"""

    if not g.user:
        flash("Access Denied Please Login First", "danger")
        return redirect("/login") 

    
    return render_template("deleteprofile.html")



@app.route("/user/deleteprofile", methods=["POST"])
def delete_profile():
    """delete user profile"""

    if not g.user:
        flash("Access Denied Please Login First", "danger")
        return redirect("/login") 

    db.session.delete(g.user)
    db.session.commit()
    do_logout()
    
    return redirect("/")


@app.route("/user/editprofile", methods=["GET", "POST"])
def edit_profile():
    """edit profile info"""

    if not g.user:
        flash("Access Denied Please Login First", "danger")
        return redirect("/login") 

    form = UserAddForm(obj=g.user)

    if form.validate_on_submit():
        
        g.user.username = form.username.data
        g.user.first_name = form.first_name.data
        g.user.last_name = form.last_name.data
        g.user.email = form.email.data
        password = form.password.data

        user = User.authenticate(g.user.username, password)
        if user:

            db.session.add(g.user)
            db.session.commit()

            return redirect("/user")

        else:
            flash("Password Incorrect")
 
    return render_template("/users/editprofile.html", form = form, user_id = g.user.id)


