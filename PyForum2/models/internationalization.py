# Internationalization Settings:
# Do not "force" a lang anymore: T.current_languages=['en', 'en-en', 'en-us']
# If I see you pass URL?lang=es-mx, then set the preferences in the session

# Helper function to tell us what language we're using:
def get_lang():
    return session.lang_use or '' # English is the default

allowed_languages = ['es-mx', 'de-de'] # TODO: Grab this from the DB
if request.vars.lang and request.vars.lang in allowed_languages:
    session.lang_use = request.vars.lang
else:
    if request.vars.has_key('lang') and request.vars.get('lang', '') == '' and session.has_key('lang_use'):
        del session['lang_use']

if session.lang_use:
    T.force(session.lang_use)
