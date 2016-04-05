import os
from flask import request, current_app, render_template, abort
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.admin import Admin
from flask import jsonify
from flask_swagger import swagger

from portal import blueprint, Page, Portal
from portal.editing import PortalFileAdmin

app = Portal(__name__)
app.config['SECRET_KEY'] = '3294038'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True
toolbar = DebugToolbarExtension(app)

# Required by the portal
app.config['PAGES_DIR'] = os.path.join(app.root_path, 'pages')
app.register_blueprint(blueprint)

admin = Admin(app, 'Portal Admin', template_mode='bootstrap3')

admin.add_view(PortalFileAdmin(app.root_path, '/', name='Files'))

from wtforms import form, fields
from flask.ext.admin.model.fields import InlineFormField
from flask.ext.admin.form.fields import DateTimeField
from flask.ext.admin.contrib.pymongo import ModelView

class LocationForm(form.Form):
    address = fields.TextField()
    city = fields.TextField()

class PeopleForm(form.Form):
    name = fields.TextField()
    color=fields.SelectField("test",choices=[["blue","blue"],["red","red"],["greem","green"]])
    email = fields.TextField()
    born = DateTimeField()
    location = InlineFormField(LocationForm)

class PeopleView(ModelView):
    column_list = ('name', 'email', 'born')
    column_sortable_list = ('name', 'email', 'born')
    column_searchable_list = ('name', 'email')
    form = PeopleForm

import pymongo
conn = pymongo.MongoClient ()
db = conn.apitest

admin.add_view(PeopleView(db.people, 'People'))


from portal.actors import all_actors
from types import  ModuleType
methods = [method for method in dir(all_actors) if isinstance(getattr(all_actors, method), ModuleType)]
for method in methods:
    app.add_url_rule('/'+method, method, getattr(getattr(all_actors, method), method))
# app.view_functions['addUser'] = actors.addUser.addUser
app.run(host='0.0.0.0')
