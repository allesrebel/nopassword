from flask import *
from flask.helpers import *

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')

# init the login manager
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, mixins
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# We'll keep things super simple.
# Everything will be inmemory for now

"""
Database connection setup etc
"""

app.users = {}
app.user_subscribers = {}
app.user_settings = {}

"""
App Router Definitions + Blank Pages
"""

@app.route( rule = '/', methods = ['GET'] )
def index():
    return render_template('index.html')

resource_file_whitelist = ['favicon.ico']

"""
Not sure I need this route tbh
Probably just a landing for the user itself
"""
@app.route( rule = '/<string:user>/', methods = ['GET', 'POST'] )
@login_required
def user( user ):
    #Handle Icon requests
    if user in resource_file_whitelist:
        return app.send_static_file( user )

    if user not in app.users:
        abort(404)

    return 'user page'

from wtforms import Form, StringField, validators

class UserForm(Form):
    email = StringField(
        'Email Address', 
        [
            validators.Length(min=6, max=35), 
            validators.Email(), 
            validators.InputRequired()
        ]
    )

class User(mixins.UserMixin):
    def __init__(self, email):
        self.id = email
    
    def get(email):
        if email in app.users:
            return User(email)
        else:
            return None

# GET Registration route
@app.route( rule = '/register', methods = ['GET', 'POST'])
def register():
    # Toss the values in from the post request into the form (if present)
    form = UserForm(request.values)

    if request.method == 'POST' and form.validate():

        # User already logged in
        if current_user.is_authenticated:
            flash('Already Logged In')

        # User already exists
        elif form.data['email'] in app.users:
            flash('User/Email {} Already Exists, please log in'.format( form.data['email'] ))
            return redirect( url_for( 'login' ) )
        
        else: # create user
            app.users[ form.data['email'] ] = True
            login_user( User(form.data['email']) )
            flash('user account created and logged in')
            return redirect( url_for( 'index' ) )

        return redirect( url_for( 'index' ) )
    else:
        return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods = ['GET', 'POST'])
def login():

    # Toss the values in from the post request into the form (if present)
    form = UserForm(request.values)

    if request.method == 'POST' and form.validate() :

        if current_user.is_authenticated:
            flash('Already logged in!')
            return redirect(url_for('index'))

        # check if user exists
        elif form.data['email'] in app.users:

            login_user(User(form.data['email']))

            flash('Logged in successfully.')

            next = request.args.get('next')

            if not escape(next):
                return abort(400)
            return redirect(next or url_for('index'))
        else:
            flash('no matching user found, please register')
            return redirect(url_for('register'))
    else:
        return render_template('login.html', form=form)

# Login Route
@app.route('/logout', methods = ['GET'])
def logout():
    logout_user()
    flash('logged out!')
    return redirect( url_for( 'index' ) )

# Modify User Settings
@login_required
@app.route( rule = '/<string:user>/settings/', methods = ['GET', 'POST'] )
def user_settings( user ):
    if request.method == 'POST':
        return 'POSTED'
    else: # is GET
        url_for('user_settings', user=user)
        return 'Settings for user'

@app.route( rule = '/users', methods = ['GET'])
@login_required
def users():
    print( request.args )
    return str( app.users ).encode()
