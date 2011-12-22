# coding: utf8
db.define_table('recipient',
   Field('name',requires=IS_NOT_EMPTY()),
   Field('email',requires=IS_EMAIL()))   
   
def email_user(sender,message,subject="group notice"):
    import smtplib # change if you want to work on GAE
    fromaddr=sender
    toaddrs=[x.email for x in db().select(db.recipient.email)]
    msg="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"%(fromaddr,", ".join(toaddrs),subject,message)
    server = smtplib.SMTP('localhost:25')
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
