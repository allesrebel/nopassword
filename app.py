from flask import Flask
from flask.helpers import *
from flask.app import *

app = Flask(__name__)

# We'll keep things super simple.
# Everything will be inmemory for now

"""
Database connection setup etc
"""

app.users = {}

"""
App Router Definitions + Blank Pages
"""

@app.route( rule = '/' )
def index( **req ):
    print( req )
    return 'hello world'

@app.route( rule = '/<string:user>', methods = ['GET', 'POST'] )
@app.route( rule = '/settings/<string:user>', methods = ['GET', 'POST'] )
def user( **req ):
    #Handle Icon requests
    if req['user'] in ['favicon.ico']:
        return app.send_static_file( req['user'] )

    print( req )
    if req['user'] not in app.users:
        raise default_exceptions[404]
    return 'user page'

