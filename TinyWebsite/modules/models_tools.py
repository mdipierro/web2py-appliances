def start_datetime(row):
    from datetime import datetime

    #dbg.set_trace()
    if row.calendar_event.duration:
        myDateTime = datetime(row.calendar_event.start_date.year, row.calendar_event.start_date.month, row.calendar_event.start_date.day,
                                      row.calendar_event.duration.start_hour.hour, row.calendar_event.duration.start_hour.minute,
                                      row.calendar_event.duration.start_hour.second)
    else:
        myDateTime = datetime(row.calendar_event.start_date.year, row.calendar_event.start_date.month, row.calendar_event.start_date.day)
    return myDateTime.strftime('%B %d, %Y %H:%M:%S')

def end_datetime(row):
    from datetime import datetime, timedelta

    if row.calendar_event.duration:
        delta = timedelta(minutes=row.calendar_event.duration.duration_in_minutes)
        myDateTime = datetime(row.calendar_event.start_date.year, row.calendar_event.start_date.month, row.calendar_event.start_date.day,
                                      row.calendar_event.duration.start_hour.hour, row.calendar_event.duration.start_hour.minute,
                                      row.calendar_event.duration.start_hour.second)
        myDateTime = myDateTime + delta
    else:
        myDateTime = datetime(row.calendar_event.start_date.year, row.calendar_event.start_date.month, row.calendar_event.start_date.day)
    return myDateTime.strftime('%B %d, %Y %H:%M:%S')