from flask import *
from flask.helpers import *
from flask.app import *

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')

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
"""
# Details about the user, Public landing
@app.route( rule = '/<string:user>/', methods = ['GET', 'POST'] )
def user( user ):
    #Handle Icon requests
    if user in resource_file_whitelist:
        return app.send_static_file( user )

    if user not in app.users:
        raise default_exceptions[404]
    return 'user page'

# POST Registration Route for new user
@app.route( rule = '/register/<string:user>/', methods = ['POST'])
def register_user( user ):
    return 'Registered!'

# GET Registration route
@app.route( rule = '/register/', methods = ['GET'])
def register():
    
    return 'Got to register page'

# Login Route
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        # User already logged in
        if 'user' in session:
            flash('Already Logged In')

        # User wants to log in
        elif len(request.form['user']) and request.form['user'] in app.users:
            flash('Welcome {}!'.format(user))
            session['user'] = request.form['user']
        else:
            flash('Enter valid username')
            return redirect( url_for( 'login' ) )

        return redirect( url_for( 'index' ) )
    else:
        return render_template(['login.html'])

# Login Route
@app.route('/logout', methods = ['GET'])
def logout():
    session.pop('user', None)
    flash('logged out!')
    return redirect( url_for( 'index' ) )

# Modify User Settings
@app.route( rule = '/<string:user>/settings/', methods = ['GET', 'POST'] )
def user_settings( user ):
    if request.method == 'POST':
        return 'POSTED'
    else: # is GET
        url_for('user_settings', user=user)
        return 'Settings for user'
