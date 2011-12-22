# coding: utf8
plugin_fbconnect=local_import('plugin_fbconnect/facebook')

plugin_fbconnect.settings.FACEBOOK_API_KEY = ''
plugin_fbconnect.settings.FACEBOOK_SECRET_KEY = ''
plugin_fbconnect.settings.FACEBOOK_APP_NAME = "fbconnect-web2py"
plugin_fbconnect.settings.FACEBOOK_INTERNAL = True
plugin_fbconnect.settings.FACEBOOK_CALLBACK_PATH = "/fbconnect/default/test"
plugin_fbconnect.user = session.plugin_fbconnect_user

def plugin_fbconnect_button():
    connected = plugin_fbconnect.connect(request, plugin_fbconnect.settings)
    if connected:
        plugin_fbconnect.user = session.plugin_fbconnect_user = plugin_fbconnect.get_user(request.facebook)
	response.flash = T("Welcome %s", plugin_fbconnect.user)
	return False
    else:
        return TAG[''](
            SCRIPT(_src="http://static.ak.connect.facebook.com/js/api_lib/v0.4/FeatureLoader.js.php",
                   _type="text/javascript"),
            DIV(TAG['fb:login-button'](_length='long',_onlogin="update_user_box();"),_id="fbconnect_user"),
            SCRIPT("""
  function update_user_box() {
    jQuery("#fbconnect_user").html(
     "<fb:profile-pic uid='loggedinuser' facebook-logo='true'></fb:profile-pic>" +
     "Welcome, <fb:name uid='loggedinuser' useyou='false'></fb:name>" +
     '<a href="#" onclick="FB.Connect.logout();" ><img id="fb_logout_image" src="http://static.ak.fbcdn.net/images/fbconnect/logout-buttons/logout_small.gif" alt="Connect"/></a>');
     FB.XFBML.Host.parseDomTree();
  }
  var api_key = '%s';
  var channel_path = "{{=URL(request.application,'static','plugin_fbconnect/xd_receiver.htm')}}";
  FB.init(api_key, channel_path);
  FB.ensureInit(function () { FB.Connect.ifUserConnected(update_user_box, null); });
""" % plugin_fbconnect.settings.FACEBOOK_API_KEY))

