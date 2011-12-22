plugin_translate_current_language = 'en'

session._language = request.vars._language or session._language or plugin_translate_current_language
T.force(session._language)
if T.accepted_language != session._language:
    import re
    lang = re.compile('\w{2}').findall(session._language)[0]
    response.files.append(URL(r=request,c='static',f='plugin_translate/jquery.translate-1.4.3-debug-all.js'))
    response.files.append(URL(r=request,c='plugin_translate',f='translate',args=lang+'.js'))

def plugin_translate(languages=[('en','English'),('es','Spanish'),('fr','French'),('de','German'),('ru','Russian')]):
    return FORM(SELECT(
            _onchange="document.location='%s?_language='+jQuery(this).val()" \
                % URL(r=request,args=request.args),
            value=session._language,
            _style = 'width:100px',
            *[OPTION(k,_value=v) for v,k in languages]))

 
