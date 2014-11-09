import os
import codecs
from flask import Blueprint, render_template, render_template_string, send_from_directory, abort
from markdown import Markdown
import jinja2


def favicon():
    return send_from_directory(os.path.join(portal.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def render_page(path, content_folder):
    try:
        # UTF-8 here is intentional!
        with codecs.open(os.path.join(content_folder, path + '.md'), encoding='utf-8') as f:
            content = f.read()
    except IOError:
        abort(404)

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


def add_portal(app, portal_name, **options):
    content_folder = options.pop('content_folder')

    portal = Blueprint(portal_name, portal_name, **options)
    portal.add_url_rule('/favicon.ico', 'favicon',     favicon)
    portal.add_url_rule('/',            'render_page', render_page, defaults={'content_folder': content_folder, 'path': 'index'})
    portal.add_url_rule('/<path:path>', 'render_page', render_page, defaults={'content_folder': content_folder})

    # Add macros
    from .macros import youtube
    app.jinja_env.globals['youtube'] = youtube.macro

    app.register_blueprint(portal)
