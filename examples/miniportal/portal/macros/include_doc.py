import os
from flask import current_app, abort
from portal import Page

def include_doc(actors, path):
    try:
        page = Page(os.path.join(current_app.config['PAGES_DIR'], path + '.md'))
        page.load()
        return page.html_content
    except IOError:
        return ''