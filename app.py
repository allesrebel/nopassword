from flask import Flask

app = Flask(__name__)

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
    print( req )
    return 'user page'
