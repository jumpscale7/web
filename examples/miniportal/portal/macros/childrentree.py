import os
from flask import current_app, render_template, Markup
from portal import Page


def is_page(f):
    return f.endswith('.md') or (os.path.isdir(f) and os.path.exists(os.path.join(f, 'index.md')))


def get_dir_tree(dir):
    children = [Page(os.path.join(dir, f)) for f in os.listdir(dir) if is_page(f)]
    return children


def childrentree():
    pages = get_dir_tree(current_app.config['PAGES_DIR'])

    return Markup(render_template('partials/_childrentree.html', pages=pages))