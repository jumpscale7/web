import os
from flask import request, current_app
from flask.ext.admin import BaseView, expose
from . import Page


class EditView(BaseView):
    @expose('/')
    def index(self):
        path = request.args['path']
        page = Page(os.path.join(current_app.config['PAGES_DIR'], path + '.md'))
        return self.render('edit.html', page=page)
