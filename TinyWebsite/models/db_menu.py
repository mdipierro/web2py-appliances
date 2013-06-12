#Things to be initialized before menu.py


WEBSITE_PARAMETERS = db(db.website_parameters).select().first()

if WEBSITE_PARAMETERS:
    if WEBSITE_PARAMETERS.mailserver_url and WEBSITE_PARAMETERS.mailserver_port:
        ## configure email
        mail = auth.settings.mailer
        mail.settings.server = '%s:%s' %(WEBSITE_PARAMETERS.mailserver_url, WEBSITE_PARAMETERS.mailserver_port)
        mail.settings.sender = WEBSITE_PARAMETERS.mailserver_sender_mail
        mail.settings.login = '%s:%s' %(WEBSITE_PARAMETERS.mailserver_sender_login, WEBSITE_PARAMETERS.mailserver_sender_pass)

        ## your http://google.com/analytics id
        response.google_analytics_id = None if request.is_local else WEBSITE_PARAMETERS.google_analytics_id

        response.subtitle = WEBSITE_PARAMETERS.website_name

    if WEBSITE_PARAMETERS.force_language:
    	 T.force(WEBSITE_PARAMETERS.force_language)