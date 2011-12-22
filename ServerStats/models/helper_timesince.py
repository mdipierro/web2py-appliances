import datetime, time

def timesince(d0, t0):
    chunks = (
      (60 * 60 * 24 * 365, lambda n: T('one year') if n==1 else T('%(n)d years',dict(n=n))),
      (60 * 60 * 24 * 30, lambda n: T('one month') if n==1 else T('%(n)d months',dict(n=n))),
      (60 * 60 * 24 * 7, lambda n: T('one week') if n==1 else T('%(n)d weeks',dict(n=n))),
      (60 * 60 * 24, lambda n: T('one day') if n==1 else T('%(n)d days',dict(n=n))),
      (60 * 60, lambda n: T('one hour') if n==1 else T('%(n)d hours',dict(n=n))),
      (60, lambda n: T('one minute') if n==1 else T('%(n)d minutes',dict(n=n))),      
      (1, lambda n: T('an instant') if n==1 else T('%(n)d seconds',dict(n=n))),
    )
    now = datetime.datetime.fromtimestamp(t0)
    d=datetime.datetime.fromtimestamp(d0)
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0: return T('an instant')
    for seconds, name in chunks:
        count = since // seconds
        if count != 0: break
    return name(count)
