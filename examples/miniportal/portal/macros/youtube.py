from portal import blueprint

@blueprint.app_template_global('youtube')
def macro(video_id, width=420, height=315):
    return '<iframe width="{width}" height="{height}" src="//www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'.format(video_id=video_id, width=width, height=height)