to=['mdipierro@cs.depaul.edu','paula@mikrut.org']

def index():
    form=SQLFORM(db.message,fields=['your_name','your_email','your_message'])
    if form.accepts(request,session):
       subject='cfgroup message from '+form.vars.your_name
       email_user(sender=form.vars.your_email,\
                  to=to,\
                  message=form.vars.your_message,\
                  subject=subject)
       response.flash='your message has been submitted'
    elif form.errors:
       response.flash='please check the form and try again'
    return dict(form=form)