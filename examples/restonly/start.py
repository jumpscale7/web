from JumpScale import j

from flask import Flask,jsonify,make_response,g, session,redirect

from flask.ext.admin import Admin
from flask.ext.httpauth import HTTPBasicAuth
from flask_debugtoolbar import DebugToolbarExtension

auth = HTTPBasicAuth()

app = Flask(__name__)

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'sdsdsd'


from flask.ext.openid import OpenID
j.system.fs.createDir("/var/flash/openid")
oid = OpenID(app, '/var/flash/openid', safe_roots=[])


admin = Admin(app)

users = {
    "admin": "admin"
}

@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        openid = session['openid']
        g.user = User.query.filter_by(openid=openid).first()


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'nickname'],
                                         ask_for_optional=['fullname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())        

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


tasks={
  "tasks": [
    {
      "title": "Buy groceries",
      "done": False,
      "description": "Milk, Cheese, Pizza, Fruit, Tylenol",
      "uri": "http://localhost:5000/todo/api/v1.0/tasks/1"
    },
    {
      "title": "Learn Python",
      "done": False,
      "description": "Need to find a good Python tutorial on the web",
      "uri": "http://localhost:5000/todo/api/v1.0/tasks/2"
    }
  ]
}

@app.route('/api/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    r="1"
    raise RuntimeError("ll")
    return "Hello, %s!" % auth.username()
    # return jsonify({'tasks': tasks})

app.debug = True
toolbar = DebugToolbarExtension(app)
app.run()


# # import mongoengine
# from eve import Eve
# # from eve_mongoengine import EveMongoengine

# from flask.ext.bootstrap import Bootstrap
# from eve_docs import eve_docs

# # default eve settings
# my_settings = {
#     'DOMAIN': {'jpackages': {}},
#     'RESOURCE_METHODS':[],
#     'ITEM_METHODS':[],
#     'ITEM_LOOKUP':False,
#     'DEBUG':True
# }

# class NoData():
#     def __init__(self,*args,**kwargs):
#         pass

# # init application
# app = Eve(settings=my_settings,data=NoData)

# Bootstrap(app)
# app.register_blueprint(eve_docs, url_prefix='/docs')

# print "visit:\nhttp://localhost:5000/docs/"

# # let's roll
# app.run()