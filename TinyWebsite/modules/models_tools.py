def start_datetime(row):
    from datetime import datetime

    #dbg.set_trace()
    _row = row[row.keys()[0]]
    if _row.duration:
        myDateTime = datetime(_row.start_date.year, _row.start_date.month, _row.start_date.day,
                                      _row.duration.start_hour.hour, _row.duration.start_hour.minute,
                                      _row.duration.start_hour.second)
    else:
        myDateTime = datetime(_row.start_date.year, _row.start_date.month, _row.start_date.day)
    return myDateTime.strftime('%B %d, %Y %H:%M:%S')

def end_datetime(row):
    from datetime import datetime, timedelta

    #dbg.set_trace()
    _row = row[row.keys()[0]]
    if _row.duration:
        delta = timedelta(minutes=_row.duration.duration_in_minutes)
        myDateTime = datetime(_row.start_date.year, _row.start_date.month, _row.start_date.day,
                                      _row.duration.start_hour.hour, _row.duration.start_hour.minute,
                                      _row.duration.start_hour.second)
        myDateTime = myDateTime + delta
    else:
        myDateTime = datetime(_row.start_date.year, _row.start_date.month, _row.start_date.day)
    return myDateTime.strftime('%B %d, %Y %H:%M:%S')