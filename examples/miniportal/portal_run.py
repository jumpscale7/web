import os
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

from portal import add_portal

# from flask.ext.misaka import markdown

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = '3294038'
app.debug = True
toolbar = DebugToolbarExtension(app)
add_portal(app, 'bs3_portal',  content_folder=os.path.join(CURRENT_DIR, 'pages'), 
                               url_prefix='/')

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
