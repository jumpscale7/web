from .. import blueprint
from . import childrentree, youtube, include_doc

for macro in [childrentree.childrentree, youtube.youtube, include_doc.include_doc]:
    blueprint.app_template_global(macro.__name__)(macro)