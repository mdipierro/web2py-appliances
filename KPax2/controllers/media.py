def player():
    filename=URL('folders','download',args=request.args)
    return dict(filename=filename)

def player_open():
    response.title="kpax"
    filename=URL('folders','download',args=request.args)
    return dict(filename=filename)
