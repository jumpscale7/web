import os
from flask import g, render_template, Markup
from portal import blueprint, Page

def is_page(f):
    return f.endswith('.md') or (os.path.isdir(f) and os.path.exists(os.path.join(f, 'index.md')))


def get_dir_tree(dir):
    children = [Page(os.path.join(dir, f)) for f in os.listdir(dir) if is_page(f)]
    return children

@blueprint.app_template_global('childrentree')
def macro():
    pages = get_dir_tree(g.app.config['PAGES_DIR'])

    return Markup(render_template('_childrentree.html', pages=pages))