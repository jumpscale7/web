from .. import blueprint
from . import childrentree, youtube, include_doc, add


for macro in [childrentree.childrentree, youtube.youtube, include_doc.include_doc, add.add]:
    blueprint.app_template_global(macro.__name__)(macro)