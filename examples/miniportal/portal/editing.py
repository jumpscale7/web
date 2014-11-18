from flask.ext.admin import BaseView, expose

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