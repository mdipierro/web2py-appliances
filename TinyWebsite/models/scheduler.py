from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def mail_send():
    if not WEBSITE_PARAMETERS:
        return "No Website parameters configured..."
    if not mail:
        return "No mail configured..."
    news_to_send = db((db.news.send_mail==True) & (db.news.mail_sent==False)).select()

    mail_subject = T('%d news on %s website!') % (len(news_to_send), WEBSITE_PARAMETERS.website_name)
    if news_to_send:
        message = T('%d news on %s website!%s') % (len(news_to_send), WEBSITE_PARAMETERS.website_url, '\n\n')
        for news in news_to_send:
            message += T("*** %s ***%s%s%s") % (news.title, '\n', strip_tags(news.text), '\n\n')
            news.mail_sent=True
            news.update_record()
            db.commit()
        registered_users = db((db.registered_user.subscribe_to_newsletter==True)).select()
        for r_user in registered_users:
            footer = T("You receive this email because you subscribed on %s website.\nTo unsubscribe from this newsletter, please click here : %s") % (
                            WEBSITE_PARAMETERS.website_url, URL(WEBSITE_PARAMETERS.website_url, 'news', 'mailing_unsubscribe', vars=dict(email=r_user.email)))
            mail.send(
                        to=r_user.email,
                        subject=mail_subject,
                        message = message+footer
                    )
    else:
        return "no news to send..."