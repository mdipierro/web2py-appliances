def rate():
    N=5
    pm = db.plugin_rating_master
    pa = db.plugin_rating_aux
    tablename = request.vars.tablename
    record_id = request.vars.record_id
    rating = int(request.vars.rating or 0) #### TODO: check rate in range
    master = db(pm.tablename==tablename)(pm.record_id==record_id).select().first()
    if master:
        master_rating, master_counter = master.rating, master.counter
    else:
        master_rating, master_counter = 0, 0
        master=pm.insert(tablename=tablename,record_id=record_id,rating=master_rating,counter=master_counter)
    record = db(pa.master==master)(pa.created_by==auth.user_id).select().first()
    if record:
        user_rating = record.rating
    else:
        user_rating = 0
    print request.vars
    if rating:
        if not record:
           record = db.plugin_rating_aux.insert(master=master,rating=rating,created_by=auth.user_id)
           master_rating = (master_rating*master_counter + rating)/(master_counter+1)
           master_counter = master_counter + 1
        else:
           master_counter = master_counter
           master_rating = (master_rating*master_counter - record.rating + rating)/master_counter
           record.update_record(rating=rating)
        master.update_record(rating=master_rating, counter=master_counter)
        user_rating = rating
    print user_rating
    return ''
