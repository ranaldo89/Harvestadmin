from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:00000@localhost/harvest'
db = SQLAlchemy(app)

class User(db.Model):
    """User of website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    pw = db.Column(db.String(100), nullable=False)
    bday = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String(1), nullable=False)

    def __init__(self, fname, lname, email, pw, bday, gender):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.pw = pw
        self.bday = bday
        self.gender = gender

    def getuserid(self):
        return self.user_id


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} fname={} lname={}>".format(self.user_id, self.fname, self.lname)



class Meals(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    foodName = db.Column(db.String(150))
    description = db.Column(db.String(350))
    prepTime = db.Column(db.Integer)
    cookTime=db.Column(db.Integer)
    serves = db.Column(db.Integer)
    cuisine = db.Column(db.String(10))
    calories= db.Column(db.String(50))
    ingredients = db.Column(db.String(350))
    photo = db.Column(db.String(250))
    def __init__(self, foodName, description, prepTime, cookTime,serves,cuisine,calories,ingredients,photo):
        self.foodName = foodName
        self.description = description
        self.prepTime = prepTime
        self.cookTime = cookTime
        self.serves=serves
        self.cuisine=cuisine
        self.calories=calories
        self.ingredients = ingredients
        self.photo=photo

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return "<Recipe id={} foodName={} description={}>".format(self.id, self.foodName, self.description)



class Recipe(db.Model):
    """Saved recipe on website (from Spoonacular API)."""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, primary_key=True)
    num_saved = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    image = db.Column(db.String(250), nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Recipe recipe_id={} title={} num_saved={}>".format(self.recipe_id, self.title, self.num_saved)



class Plan(db.Model):
    """Saved meal plans on website."""

    __tablename__ = "plans"

    plan_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), index=True)
    start = db.Column(db.Date, nullable=False)
    order_status = db.Column(db.String(100), nullable=False)

    recipes = db.relationship("Recipe", secondary="assoc", backref="plans")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Plan plan_id={} user_id={} start={}>".format(self.plan_id, self.user_id, self.start)


class PlanRecipe(db.Model):
    """User of website."""

    __tablename__ = "assoc"

    assoc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.plan_id'), index=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), index=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Assoc assoc_id={} user_id={} recipe_id={}>".format(self.assoc_id, self.user_id, self.recipe_id)




@app.route('/', methods=['GET', 'POST'])
def home():

    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            return render_template('index.html', plans=Plan.query.all())
        return render_template('index.html', plans=Plan.query.all())


@app.route("/plan-<int:plan_id>-<int:user_id>")
def show_saved_recipes(plan_id, user_id):


    session["plan_id"] = plan_id

    user = User.query.filter_by(user_id=user_id).first()
    plan = Plan.query.filter_by(plan_id=plan_id).first()
    recipes = plan.recipes
    start = plan.start.strftime("%b %#d, %Y")
    # all past plans made by current user
    #past_plans = Plan.query.filter_by(user_id=user.user_id).all()

    return render_template("plan.html", start=start, recipes=recipes, fname=user.fname, plan_id=plan.plan_id)


@app.route('/updateorder', methods=['GET', 'POST'])
def update_orderstatus():
    orderstatus = request.form.get("order_status")
    planid = request.form.get("planid")

    plan = Plan.query.filter_by(plan_id=planid).first()
    if request.method == 'POST':
        #stmt = update(Plan).where(Plan.plan_id==planid).
        plan.order_status = orderstatus

    db.session.commit()
        
      
      # db.session.commit()

    
    
    #flash("Updated Successfully")

    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        try:
            if name == "admin" and passw == "admin123" :
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                return 'Dont Login'
        except:
            return "Dont Login"

@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run(debug=True, host="0.0.0.0", port=5508)
