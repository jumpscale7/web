import os
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.admin import Admin
from wtforms import form, fields
from flask.ext.admin.model.fields import InlineFormField
from flask.ext.admin.form.fields import DateTimeField
from flask.ext.admin.contrib.pymongo import ModelView
import pymongo
from portal import blueprint, Portal
from portal.editing import PortalFileAdmin
from flask import Blueprint
from portal.MacrosLoader import MacrosLoader
class LocationForm(form.Form):
    address = fields.TextField()
    city = fields.TextField()


class PeopleForm(form.Form):
    name = fields.TextField()
    color = fields.SelectField("test", choices=[["blue", "blue"], ["red", "red"], ["greem", "green"]])
    email = fields.TextField()
    born = DateTimeField()
    location = InlineFormField(LocationForm)


class PeopleView(ModelView):
    column_list = ('name', 'email', 'born')
    column_sortable_list = ('name', 'email', 'born')
    column_searchable_list = ('name', 'email')
    form = PeopleForm

from portal.ActorsLoader import ActorsLoader
class App(object):
    def __init__(self, settings):
        self._actors_path = settings["actors_path"]
        self.app = None
        self.actors = None

    def startapp(self):
        self.app = Portal(__name__)
        self.app.config['SECRET_KEY'] = '3294038'
        self.app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        self.app.debug = True
        toolbar = DebugToolbarExtension(self.app)
        mainbp = Blueprint('mainpb', __name__)

        # Required by the portal
        self.app.config['PAGES_DIR'] = os.path.join(self.app.root_path, 'pages')
        self.app.register_blueprint(blueprint)
        admin = Admin(self.app, 'Portal Admin', template_mode='bootstrap3')
        admin.add_view(PortalFileAdmin(self.app.root_path, '/', name='Files'))
        conn = pymongo.MongoClient()
        db = conn.apitest
        admin.add_view(PeopleView(db.people, 'People'))
        self.actors = ActorsLoader(self._actors_path).load_actors()
        self.generate_routes()
        self.load_macros(mainbp)
        self.app.register_blueprint(blueprint)
        self.app.register_blueprint(mainbp)
        self.app.run(host='0.0.0.0')

    def getCallback(self, fn):
        def wrapper(*args, **kwargs):
            return fn(self.actors, *args, **kwargs)

        return wrapper

    def generate_routes(self):
        for ns_name in dir(self.actors):
            if ns_name.startswith("__"):
                continue
            ns = getattr(self.actors, ns_name)
            for obj_name in dir(ns):
                if obj_name.startswith("__"):
                    continue
                obj = getattr(ns, obj_name)
                for method_name in dir(obj):
                    if method_name.startswith("_") or method_name.startswith("__"):
                        continue
                    method = getattr(obj, method_name)
                    self.app.add_url_rule("/"+'{namespace}/{object}/{method}'.format(namespace=ns_name, object=obj_name, method=method_name),
                                          method_name, self.getCallback(method))

    def getCallback(self, fn):
        def wrapper(*args, **kwargs):
            return fn(self.actors, *args, **kwargs)

        return wrapper

    def load_macros(self, pb):
        MacrosLoader("portal/macros").load_macros(pb, self.actors)

settings = {}
settings["actors_path"] = "portal/actors"
application = App(settings)
application.startapp()
