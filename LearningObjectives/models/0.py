from gluon.storage import Storage
settings=Storage()

settings.host='http://web2py.com'
settings.cas_base="https://login.depaul.edu/cas/"
settings.management_roles=['Instructor']
settings.link_color="#336699"
settings.production=True
settings.widgets = ['youtube','vimeo','latex','mediaplayer','bar_chart','pie_chart','slideshow']
settings.big_blue_button="http://demo.bigbluebutton.org/bigbluebutton/demo/create.jsp"
settings.big_blue_button_name='depaul_%s'
if not settings.production:
    print 'debug:'
    print request.application,request.controller,request.function, request.args
    print request.vars
