import os
import codecs
from markdown import Markdown
from werkzeug.utils import cached_property
from flask import Flask, current_app, request, abort, url_for, render_template, render_template_string, Markup, Blueprint, send_from_directory
from .markdown_extensions import BootstrapTableExtension


class Page:
    def __init__(self, path, content=None):
        self.path = path
        # UTF-8 here is intentional!
        if content is None:
            with codecs.open(self.path, encoding='utf-8') as f:
                self.raw_content = f.read()
        else:
            self.raw_content = content

        self._load_meta()

    # Because we need only the meta, we parse the document without executing jinja templates inside it
    def _load_meta(self):
        markdown = Markdown(extensions=['meta']) # No need for other extensions
        markdown.convert(self.raw_content)
        self.meta = markdown.Meta
        self.meta['page'] = self
        self.meta['template'] = self.meta.get('template', 'page.html')

    def load(self):
        content = render_template_string(self.raw_content, page=self)
        markdown = Markdown(extensions=[BootstrapTableExtension(), 'meta', 'fenced_code', 'codehilite', 'nl2br'])
        self.html_content = markdown.convert(content)

    @cached_property
    def url(self):
        path =  os.path.relpath(self.path, current_app.config['PAGES_DIR'])
        path = os.path.splitext(path)[0]
        return url_for('portal.render_page', path=path)

    @cached_property
    def title(self):
        path =  os.path.relpath(self.path, current_app.config['PAGES_DIR'])
        alt_title = os.path.splitext(path)[0]
        return self.meta.get('title', [alt_title])[0]

# Stop autoescaping
class Portal(Flask):
    def select_jinja_autoescape(self, filename):
        return False


blueprint = Blueprint('portal', __name__)

from portal import macros

@blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@blueprint.route('/', defaults={'path': 'index'})
@blueprint.route('/<path:path>')
def render_page(path):
    try:
        page = Page(os.path.join(current_app.config['PAGES_DIR'], path + '.md'))
        page.load()
    except IOError:
        abort(404)

    return render_template(page.meta['template'], content=page.html_content, page=page)

