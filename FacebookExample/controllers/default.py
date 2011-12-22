from applications.facebook.modules.facebook import *

facebook_settings.FACEBOOK_API_KEY = 'xxx'
facebook_settings.FACEBOOK_SECRET_KEY = 'xxx'
facebook_settings.FACEBOOK_APP_NAME = "web2py_test"
facebook_settings.FACEBOOK_INTERNAL = True
facebook_settings.FACEBOOK_CALLBACK_PATH = "/facebook/default/index"

def index():
    require_facebook_login(request,facebook_settings)
    return dict(message="Hello "+get_facebook_user(request))
