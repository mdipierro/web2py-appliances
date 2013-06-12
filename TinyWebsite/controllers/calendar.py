#from gluon.debug import dbg

def calendar_booking():
    """
    Allows to access the "calendar_boking" component
    """
    month_list = [T('January'),T('February'),T('March'),T('April'),T('May'),T('June'),T('July'),T('August'),T('September'),T('October'),T('November'),T('December')]
    shortmonth_list = [T('Jan'),T('Feb'),T('Mar'),T('Apr'),T('May'),T('Jun'),T('Jul'),T('Aug'),T('Sep'),T('Oct'),T('Nov'),T('Dec')]
    day_list = [T('Sunday'),T('Monday'),T('Tuesday'),T('Wednesday'),T('Thursday'),T('Friday'),T('Saturday')]
    shortday_list = [T('Sun'),T('Mon'),T('Tue'),T('Wed'),T('Thu'),T('Fri'),T('Sat')]

    page = db.page(request.vars.container_id)
    rows = db(db.calendar_event.page==page)(db.calendar_event.is_confirmed==True).select()

    #dbg.set_trace()
    return dict(rows=rows,
                page=page,
                month_list=month_list,
                shortmonth_list=shortmonth_list,
                day_list=day_list,
                shortday_list=shortday_list)

def add_booking_request():
    """
    Add a booking request to a calendar event
    """
    page = db.page(request.args(0))
    if not page:
        redirect(URL('index'))
    form = SQLFORM.factory(db.calendar_contact, db.calendar_event)
    page_low_title = page.title.lower()
    if form.process().accepted:
        _id = db.calendar_contact.insert(**db.calendar_contact._filter_fields(form.vars))
        form.vars.contact=_id
        form.vars.page=page.id
        _id = db.calendar_event.insert(**db.calendar_event._filter_fields(form.vars))
        
        duration = db.calendar_duration(form.vars.duration)

        #send an email
        message=T("""
            The following person would like to book %s :

            Name : %s
            Email : %s
            Phone number : %s
            Address : %s
            From : %s
            During : %s
        """) % (page_low_title, form.vars.name, form.vars.email, form.vars.phone_number, form.vars.address,
                form.vars.start_date.strftime("%d/%m/%Y"), duration.name if duration else '')
        if mail.send(to=WEBSITE_PARAMETERS.booking_form_email,
                  cc=[WEBSITE_PARAMETERS.booking_form_cc if WEBSITE_PARAMETERS.booking_form_cc else ''],
                  bcc=[WEBSITE_PARAMETERS.booking_form_bcc if WEBSITE_PARAMETERS.booking_form_bcc else ''],
                  subject=T('Booking request for %s on %s website') % (page_low_title,WEBSITE_PARAMETERS.website_name),
                  reply_to = form.vars.email,
                  message = message):
            session.flash = T('Your booking request has been recorded. Somebody will contact you as soon as possible. Thank you')
            redirect(URL('pages','show_page',args=page.url))
        else:
            form.errors.your_email = T('Unable to send the email')
    elif form.errors:
       response.flash = T('form has errors')
    return dict(form=form,left_sidebar_enabled=True,right_sidebar_enabled=True)

@auth.requires_membership('booking_manager')
def edit_booking_requests():
    db.calendar_event.is_confirmed.readable = db.calendar_event.is_confirmed.writable = True
    db.calendar_event.page.readable = db.calendar_event.page.writable = True
    db.calendar_event.contact.readable = db.calendar_event.contact.writable = True

    linked_tables=['page, contact']
    fields=[db.calendar_event.page,db.calendar_event.contact, db.calendar_event.start_date, db.calendar_event.duration, db.calendar_event.is_confirmed]
    orderby = db.calendar_event.is_confirmed | ~db.calendar_event.start_date
    exportclasses=dict(
            csv_with_hidden_cols=False,
            xml=False,
            html=False,
            csv=False,
            json=False,
            tsv_with_hidden_cols=False,
            tsv=False)
    grid = SQLFORM.smartgrid(db.calendar_event,
                            linked_tables=linked_tables,
                            exportclasses=exportclasses,
                            orderby=orderby,
                            fields=fields)
    return dict(grid=grid)