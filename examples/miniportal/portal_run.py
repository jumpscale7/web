import os
import codecs
from flask import Flask, g, render_template, render_template_string, send_from_directory, abort, Markup, current_app
from flask_debugtoolbar import DebugToolbarExtension
import jinja2

from portal import blueprint, Page
from portal.macros import youtube, childrentree


app = Flask(__name__)
app.config['SECRET_KEY'] = '3294038'
app.debug = True
toolbar = DebugToolbarExtension(app)

app.config['PAGES_DIR'] = os.path.join(app.root_path, 'pages')

@app.before_request
def store_config():
    g.app = app


@blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@blueprint.route('/', defaults={'path': 'index'})
@blueprint.route('/<path:path>')
def render_page(path):
    page = Page(os.path.join(app.config['PAGES_DIR'], path + '.md'))
    g.page = page
    
    try:
        page.load()
    except IOError:
        print os.path.join(app.config['PAGES_DIR'], path + '.md')
        abort(404)

    meta = page.meta
    meta = dict((k, v[0]) for k, v in meta.iteritems())
    meta['page'] = page
    template = meta.get('template', 'page.html')

    return render_template(template, content=Markup(page.html_content), **meta)


# from flask.ext.admin import Admin, BaseView, expose

# class MyView(BaseView):
#     @expose('/admin')
#     def index(self):
#         return self.render('index.html')

# admin = Admin(app)
# admin.add_view(MyView(name='Hello 1', endpoint='test1', category='Test'))
# admin.add_view(MyView(name='Hello 2', endpoint='test2', category='Test'))
# admin.add_view(MyView(name='Hello 3', endpoint='test3', category='Test'))

app.register_blueprint(blueprint)

app.run()
