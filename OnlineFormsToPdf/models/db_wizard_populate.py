from gluon.contrib.populate import populate
if not db(db.auth_user).count():
     populate(db.auth_user,100)
     populate(db.t_form,100)
