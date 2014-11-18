from portal import blueprint

def youtube(video_id, width=420, height=315):
    return '<iframe width="{width}" height="{height}" src="//www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'.format(video_id=video_id, width=width, height=height)