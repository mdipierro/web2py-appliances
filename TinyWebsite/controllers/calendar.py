#from gluon.debug import dbg

def calendar_booking():
    """
    Allows to access the "calendar_boking" component
    """
    from calendar_tools import month_list, shortmonth_list, day_list, shortday_list

    page = db.page(request.vars.container_id)
    if page and page.is_index:
        #Index page : we show all booking requests
        r=db.calendar_booking_request.id > 0
    else:
        r=db.calendar_booking_request.page==page
    rows = db()(db.calendar_booking_request.is_confirmed==True).select()

    #dbg.set_trace()
    return dict(rows=rows,
                page=page,
                month_list=month_list,
                shortmonth_list=shortmonth_list,
                day_list=day_list,
                shortday_list=shortday_list)

def calendar_event():
    """
    Allows to access the "calendar_event" component
    """
    from controllers_tools import strip_accents
    from calendar_tools import month_list, shortmonth_list, day_list, shortday_list

    def get_available_positions(event_id, event_nb_positions_available):
        """
            Number of available positions for this event (None = illimited)
        """
        if event_nb_positions_available == None:
            return None
        return event_nb_positions_available - db(db.calendar_contact.event==event_id).count()

    page = db.page(request.vars.container_id)
    if page and page.is_index:
        #Index page : we show all events
        r=db.calendar_event.id > 0
    else:
        r=db.calendar_event.page==page
    rows = db(r).select()
    events_available_positions = dict((event.id, get_available_positions(event.id, event.nb_positions_available)) for event in rows)
    return dict(rows=rows,
                page=page,
                events_available_positions=events_available_positions,
                month_list=month_list,
                shortmonth_list=shortmonth_list,
                day_list=day_list,
                shortday_list=shortday_list,
                strip_accents=strip_accents)

def add_booking_request():
    """
    Add a booking request to a calendar event
    """
    page = db.page(request.args(0))
    if not page:
        redirect(URL('index'))
    form = SQLFORM.factory(db.calendar_contact, db.calendar_booking_request)
    page_low_title = page.title.lower()
    if form.process().accepted:
        _id = db.calendar_contact.insert(**db.calendar_contact._filter_fields(form.vars))
        form.vars.contact=_id
        form.vars.page=page.id
        _id = db.calendar_booking_request.insert(**db.calendar_booking_request._filter_fields(form.vars))
        
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
            Remark : %s
        """) % (page_low_title, form.vars.name, form.vars.email, form.vars.phone_number, form.vars.address,
                form.vars.start_date.strftime("%d/%m/%Y"), duration.name if duration else '', form.vars.remark)
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

@auth.requires(auth.has_membership('manager') or auth.has_membership('booking_manager'))
def edit_booking_requests():
    db.calendar_booking_request.is_confirmed.readable = db.calendar_booking_request.is_confirmed.writable = True
    db.calendar_booking_request.page.readable = db.calendar_booking_request.page.writable = True
    db.calendar_booking_request.contact.readable = db.calendar_booking_request.contact.writable = True

    linked_tables=['page, contact']
    fields=[db.calendar_booking_request.page,db.calendar_booking_request.contact, db.calendar_booking_request.start_date,
            db.calendar_booking_request.duration, db.calendar_booking_request.is_confirmed, db.calendar_booking_request.remark]
    orderby = db.calendar_booking_request.is_confirmed | ~db.calendar_booking_request.start_date
    exportclasses=dict(
            csv_with_hidden_cols=False,
            xml=False,
            html=False,
            csv=False,
            json=False,
            tsv_with_hidden_cols=False,
            tsv=False)
    grid = SQLFORM.smartgrid(db.calendar_booking_request,
                            linked_tables=linked_tables,
                            exportclasses=exportclasses,
                            orderby=orderby,
                            fields=fields)
    return dict(grid=grid)

@auth.requires(auth.has_membership('manager') or auth.has_membership('event_manager'))
def edit_events_calendar():
    db.calendar_event.page.readable = db.calendar_event.page.writable = True
    db.calendar_event.title.readable = db.calendar_event.title.writable = True
    db.calendar_event.description.readable = db.calendar_event.description.writable = True
    db.calendar_event.duration.readable = db.calendar_event.duration.writable = False
    linked_tables=['page']
    fields=[db.calendar_event.page,db.calendar_event.title,db.calendar_event.start_date, db.calendar_event.duration,
             db.calendar_event.nb_positions_available, db.calendar_event.is_enabled]
    orderby = ~db.calendar_event.start_date
    exportclasses=dict(
            csv_with_hidden_cols=False,
            xml=False,
            json=False,
            tsv_with_hidden_cols=False,
            tsv=False)
    grid = SQLFORM.smartgrid(db.calendar_event,
                            linked_tables=linked_tables,
                            exportclasses=exportclasses,
                            orderby=orderby,
                            fields=fields)
    return dict(grid=grid)

@auth.requires(auth.has_membership('manager') or auth.has_membership('event_manager'))
def edit_contacts_calendar():
    db.calendar_contact.event.readable = db.calendar_contact.event.writable = True
    linked_tables=['calendar_event']
    fields=[db.calendar_contact.name,db.calendar_contact.email, db.calendar_contact.phone_number, db.calendar_contact.address, db.calendar_contact.event]
    orderby = db.calendar_contact.name
    exportclasses=dict(
            csv_with_hidden_cols=False,
            xml=False,
            json=False,
            tsv_with_hidden_cols=False,
            tsv=False)
    grid = SQLFORM.smartgrid(db.calendar_contact,
                            linked_tables=linked_tables,
                            exportclasses=exportclasses,
                            orderby=orderby,
                            fields=fields)
    return dict(grid=grid)