import os
import codecs
from markdown import Markdown
from werkzeug.utils import cached_property
from flask import Flask, g, url_for, render_template_string, Markup, Blueprint

class Page:
    def __init__(self, path):
        self.path = path
        # UTF-8 here is intentional!
        with codecs.open(self.path, encoding='utf-8') as f:
            self.raw_content = f.read()

        self._load_meta()

    # Because we need only the meta, we parse the document without executing jinja templates inside it
    def _load_meta(self):
        markdown = Markdown(extensions=['meta']) # No need for other extensions
        markdown.convert(self.raw_content)
        self.meta = markdown.Meta

    def load(self):
        content = render_template_string(Markup(self.raw_content), page=self)
        markdown = Markdown(extensions=['meta', 'tables', 'fenced_code'])
        self.html_content = markdown.convert(content)

    @cached_property
    def url(self):
        path =  os.path.relpath(self.path, g.app.config['PAGES_DIR'])
        path = os.path.splitext(path)[0]
        return url_for('portal.render_page', path=path)

    @property
    def title(self):
        return self.meta['title'][0]


blueprint = Blueprint('portal', __name__)

from portal import macros