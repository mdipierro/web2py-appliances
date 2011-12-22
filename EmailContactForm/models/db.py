# try something like
import datetime
db=DAL("sqlite://db.db")


VALUE="""
Hello,

please send me informations about DePaul's Computational Finance Group.

"""

db.define_table('message',
   Field('your_name',requires=IS_NOT_EMPTY()),
   Field('your_email',requires=IS_EMAIL()),
   Field('your_message','text',default=VALUE),
   Field('timestamp',default=str(datetime.datetime.now())))
   
   
def email_user(sender,to,message,subject="group notice"):
    import smtplib
    fromaddr=sender
    if type(to)==type([]): toaddrs=to
    else: toaddrs=[to]
    msg="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"%(fromaddr,", ".join(toaddrs),subject,message)
    server = smtplib.SMTP('localhost:25')
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()