import os
import codecs
from flask import Flask, render_template, render_template_string, send_from_directory
from markdown import Markdown
# from flask.ext.misaka import markdown
import jinja2

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(CURRENT_DIR, 'pages')
TEMPLATES_DIR = os.path.join(CURRENT_DIR, 'templates')


app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# from flask.ext.admin import Admin, BaseView, expose

# class MyView(BaseView):
#     @expose('/admin')
#     def index(self):
#         return self.render('index.html')

# admin = Admin(app)
# admin.add_view(MyView(name='Hello 1', endpoint='test1', category='Test'))
# admin.add_view(MyView(name='Hello 2', endpoint='test2', category='Test'))
# admin.add_view(MyView(name='Hello 3', endpoint='test3', category='Test'))


@app.route('/')
@app.route('/<path:path>')
def render_page(path=''):
    if not path:
        path = 'index'

    with codecs.open(os.path.join(PAGES_DIR, path + '.md'), encoding='utf-8') as f:
        content = f.read()

    content = render_template_string(content)

    markdown = Markdown(
        extensions=['meta', 'tables', 'fenced_code']
    )

    html_content = markdown.convert(content)

    #misaka
    # html_content = markdown(content)
    
    meta = markdown.Meta
    meta = dict((k, v[0]) for k, v in meta.iteritems())

    template = meta.get('template', 'page.html')

    return render_template(template, content=html_content, **meta)

# Add macro
from macros import youtube
app.jinja_env.globals['youtube'] = youtube.macro

app.debug = True
app.run()
