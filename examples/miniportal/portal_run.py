import os
from flask import request, current_app, render_template, abort
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.admin import Admin

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

app.run()
