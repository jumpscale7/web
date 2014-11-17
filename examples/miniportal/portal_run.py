import os
from flask import request, current_app, render_template, abort
from flask_debugtoolbar import DebugToolbarExtension

from portal import blueprint, Page, Portal

app = Portal(__name__)
app.config['SECRET_KEY'] = '3294038'
app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

# Required by the portal
app.config['PAGES_DIR'] = os.path.join(app.root_path, 'pages')
app.register_blueprint(blueprint)

from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib import fileadmin

class EditView(BaseView):
    @expose('/')
    def index(self):
        path = request.args['path']
        page = Page(os.path.join(current_app.config['PAGES_DIR'], path + '.md'))
        return self.render('edit.html', page=page)

    @expose('/render_edit/')
    def render_edit_page(self):
        try:
            content = request.args.get('content', None)
            path = request.args.get('path', '')
            page = Page(os.path.join(current_app.config['PAGES_DIR'], path + '.md'), content=content)
            page.load()
        except IOError:
            abort(404)

        return render_template(page.meta['template'], content=page.html_content, page=page)

admin = Admin(app, 'Portal Admin', template_mode='bootstrap3')
admin.add_view(fileadmin.FileAdmin(app.root_path, '/', name='Files'))
admin.add_view(EditView(name='Edit page', endpoint='edit', category='Test'))


app.run()
