def plugin_mediaplayer(filename,width=400,height=300):
    return TAG.embed(_src=URL(r=request,c='static',f='plugin_mediaplayer/mediaplayer.swf'),_width="%spx" % width,_height="%spx" % height,_allowscriptaccess="always",_allowfullscreen="true",_flashvars="height=%s&width=%s&file=%s" % (height,width,filename))
