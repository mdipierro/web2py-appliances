def email(sender,to,subject='test',message='test',server='localhost:25',auth=None):
        """
        Sends an email. Returns True on success, False on failure.
        """
        if not isinstance(to,list): to=[to]
        try:
            try:
                from google.appengine.api import mail
                mail.send_mail(sender=sender,
                               to=to,
                               subject=subject,
                               body=message)
            except ImportError:
                msg="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"%(sender,\
                    ", ".join(to),subject,message)
                import smtplib, socket
                host, port=server.split(':')
                # possible bug fix? socket.setdefaulttimeout(None)
                server = smtplib.SMTP(host,port)
                #server.set_debuglevel(1)
                if auth:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    username, password=auth.split(':')
                    server.login(username, password)
                server.sendmail(sender, to, msg)
                server.quit()
        except Exception,e:
            return False
        else: return True
