import os
from flask import Flask, g
from flask_debugtoolbar import DebugToolbarExtension

from portal import blueprint


app = Flask(__name__)
app.config['SECRET_KEY'] = '3294038'
app.debug = True
toolbar = DebugToolbarExtension(app)

# Required by the portal
app.config['PAGES_DIR'] = os.path.join(app.root_path, 'pages')
app.register_blueprint(blueprint)

# from flask.ext.admin import Admin, BaseView, expose

# class MyView(BaseView):
#     @expose('/admin')
#     def index(self):
#         return self.render('index.html')

# admin = Admin(app)
# admin.add_view(MyView(name='Hello 1', endpoint='test1', category='Test'))
# admin.add_view(MyView(name='Hello 2', endpoint='test2', category='Test'))
# admin.add_view(MyView(name='Hello 3', endpoint='test3', category='Test'))


app.run()
