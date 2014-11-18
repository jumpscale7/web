import os
from flask import current_app, abort
from .. import Page

def include_doc(path):
    try:
        page = Page(os.path.join(current_app.config['PAGES_DIR'], path + '.md'))
        page.load()
        return page.html_content
    except IOError:
        return ''