from flask import *

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')

# init the login manager
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, mixins
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file( 'favicon.ico' )

# We'll keep things super simple.
# Everything will be inmemory for now

"""
Database connection setup etc
"""

app.users = {}

"""
App Router Definitions + Blank Pages
"""

@app.route( rule = '/', methods = ['GET'] )
def index():
    return render_template('index.html')

"""
Not sure I need this route tbh
Probably just a landing for the user itself
"""

@app.route( rule = '/<string:user>', methods = ['GET', 'POST'] )
@login_required
def user_portal( user ):
    if user != current_user.get_id():
        flash('We got lost! Redirected to your portal')
        return redirect( url_for( 'user_portal', user = current_user.get_id() ) )

    return render_template('index.html')

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
@app.route( '/register', methods = ['GET', 'POST'])
@app.route( '/register/<string:email>', methods = ['GET'])
def register( **req ):

    if current_user.is_authenticated:
        return redirect( url_for( 'user_portal', user = current_user.get_id() ) )

    # Toss the values in from the post request into the form (if present)
    form = UserForm(request.values)

    if request.method == 'POST' and form.validate():

        # User already exists
        elif form.data['email'] in app.users:
            flash('User/Email {} Already Exists, please log in'.format( form.data['email'] ))
            return redirect( url_for( 'login', email = form.data['email'] ))
        
        else: # create user
            app.users[ form.data['email'] ] = True
            login_user( User(form.data['email']) )
            flash('user account created and logged in')
            return redirect( url_for( 'index' ) )

        return redirect( url_for( 'index' ) )
    else:
        return render_template('register.html', form=form )

# Login Route
@app.route('/login', methods = ['GET', 'POST'])
@app.route('/login/<string:email>', methods = ['GET'])
def login( **req ):

    if current_user.is_authenticated:
        return redirect( url_for( 'user_portal', user = current_user.get_id() ) )

    # Toss the values in from the post request into the form (if present)
    form = UserForm(request.values)

    if request.method == 'POST' and form.validate() :

        # check if user exists
        if form.data['email'] in app.users:
            login_user( User(form.data['email']) )
            flash('Logged in successfully.')
            
        else:
            flash('no matching user found, please register')
            return redirect(url_for('register', email = form.data['email']))

        # maybe check the args to verify that next is
        # a valid location
        return redirect( url_for('user_portal', user = current_user.get_id() ) )
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
