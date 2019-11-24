from flask import *
import os; import base64; import time; import threading;

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')

# init the mailer
from flask_mail import Mail, Message
mail = Mail(app)

# init the login manager
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, mixins
login_manager = LoginManager(app)
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

app.login_hashtable = {}
app.user_sessions = {}

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
        if email in app.user_sessions:
            return User(email)
        else:
            return None

def kill_hashtable_entry(hash):
    if hash in app.login_hashtable:
        del app.login_hashtable[hash]

# GET Login/Registration route, same logic!
@app.route( '/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect( url_for( 'user_portal', user = current_user.get_id() ) )

    # Toss the values in from the post request into the form (if present)
    form = UserForm(request.values)

    if request.method == 'POST' and form.validate():
        # Literally random numbers for hash
        usr_hash = base64.urlsafe_b64encode( os.urandom(18) ).decode('utf-8')
        app.login_hashtable[ usr_hash ] = form.data['email']
        threading.Timer(5*60, kill_hashtable_entry, args=[usr_hash]).start()

        msg = Message(
            subject="magic link/nopassword login",
            sender="allesrebel@yahoo.com",
            recipients=[form.data['email']],
            body="Login with: http://{}/login/{}\nLink Expires in 5 minutes!".format('localhost:5000', usr_hash )
        )
        mail.send(msg)

        # User already exists
        if form.data['email'] in app.login_hashtable:
            flash('Welcome back {}, login email sent!'.format( form.data['email'] ))
        else: # User Does not Exist
            flash('Email Sent! Please confirm your account')

        return redirect( url_for( 'index' ) )
    else:
        return render_template('login.html', form=form )

# Actual Session Start from hash
@app.route('/login/<string:hash>', methods = ['GET'])
def login_processor(hash):
    if hash in app.login_hashtable:
        email = app.login_hashtable[hash]
        app.user_sessions[email] = time.time()
        del app.login_hashtable[hash]

        if login_user( User( email ), force=True, remember=True ) is False:
            abort(201) # error!

        flash( 'Welcome {}'.format( email ) )
        return redirect( url_for( 'index' ) )
    else:
        return abort(404)

# Logout Route
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
    return str( app.login_hashtable ).encode()
