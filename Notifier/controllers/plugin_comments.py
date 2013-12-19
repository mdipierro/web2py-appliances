# coding: utf8
# try something like

db = plugins.comments.db
Post = db.plugin_comments_post

@auth.requires_signature()
def index():
    tablename = request.args(0)
    record_id = request.args(1,cast=int)
    Post.tablename.default = tablename
    Post.record_id.default=record_id
    if auth.user:
        form = SQLFORM(Post).process()
        if form.accepted and plugins.comments.callbacks:
            if tablename in plugins.comments.callbacks:
                plugins.comments.callbacks[tablename](form)
    else:
        form = None
    posts = db(Post.tablename==tablename)\
        (Post.record_id==record_id).select(orderby=Post.created_on)
    return dict(form=form, posts=posts)

def delete_post():
    if request.env.request_method=='POST' and auth.user:
        post_id = request.vars.id
        post = Post(post_id)
        if post and post.created_by == auth.user.id:
            post.delete_record()
            return 'true'
    return 'false'
