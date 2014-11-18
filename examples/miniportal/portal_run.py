import os
from flask import request, current_app, render_template, abort
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.admin import Admin
from flask.ext.admin.contrib import fileadmin

from portal import blueprint, Page, Portal
from portal.editing import EditView

app = Portal(__name__)
app.config['SECRET_KEY'] = '3294038'
app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

# Required by the portal
app.config['PAGES_DIR'] = os.path.join(app.root_path, 'pages')
app.register_blueprint(blueprint)

admin = Admin(app, 'Portal Admin', template_mode='bootstrap3')
admin.add_view(fileadmin.FileAdmin(app.root_path, '/', name='Files'))
admin.add_view(EditView(name='Edit page', endpoint='edit', category='Test'))


app.run()
