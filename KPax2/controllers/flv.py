def player():
    filename=URL('folders','download',args=request.args)
    return dict(filename=filename)
