# coding: utf8

def __index_0(table):
    title = T('Manage')
    grid = SQLFORM.grid(table, 
                        user_signature = False)
    return dict(title = title, 
                grid = grid)

def __index_1(table, 
              add_link, 
              search_link, 
              show_link, 
              manage_link, 
              active):
    menu = ('[ ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')), 
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')), 
            ' ]')
    title = T('List')

    if len(request.args): 
        page = int(request.args[0])
    else: 
        page = 0

    items_per_page = 10
    limitby = (page * items_per_page, 
              (page + 1) * items_per_page + 1)
    rows = db(active == True).select(limitby = limitby, 
                                     orderby = ~table.id, 
                                     cache = (cache.ram, 
                                              10))
    return dict(menu = menu, 
                title = title, 
                show_link = show_link,
                rows = rows, 
                page = page, 
                items_per_page = items_per_page)

def __index_2(table, 
              draft_link, 
              add_link, 
              search_link, 
              show_link, 
              manage_link, 
              status, 
              active):
    menu = ('[ ', 
            A(T('Draft'), 
              _href = URL(draft_link), 
              _title = T('Draft')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')), 
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')), 
            ' ]')
    title = T('List')

    if len(request.args): 
        page = int(request.args[0])
    else: 
        page = 0

    items_per_page = 10
    limitby = (page * items_per_page, 
              (page + 1) * items_per_page + 1)
    rows = db((status == 'Published') & (active == True)).select(limitby = limitby, 
                                                                 orderby = ~table.id, 
                                                                 cache = (cache.ram, 
                                                                          10))
    return dict(menu = menu, 
                title = title, 
                show_link = show_link,
                rows = rows, 
                page = page, 
                items_per_page = items_per_page)

@auth.requires(auth.has_membership(role = 'Admin') or
               auth.has_membership(role = 'Manager'))
def __draft_0(table, 
              index_link, 
              add_link, 
              search_link, 
              show_link, 
              manage_link, 
              status, 
              active):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')), 
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')), 
            ' ]')
    title = T('List')

    if len(request.args): 
        page = int(request.args[0])
    else: 
        page = 0

    items_per_page = 10
    limitby = (page * items_per_page, 
              (page + 1) * items_per_page + 1)
    rows = db((status == 'Draft') & (active == True)).select(limitby = limitby, 
                                                             orderby = ~table.id, 
                                                             cache = (cache.ram, 
                                                                      10))
    return dict(menu = menu, 
                title = title, 
                show_link = show_link,
                rows = rows, 
                page = page, 
                items_per_page = items_per_page)

@auth.requires(auth.has_membership(role = 'Admin') or
               auth.has_membership(role = 'Manager'))
def __add_0(table, 
            index_link, 
            search_link, 
            manage_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')), 
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')), 
            ' ]')
    title = T('Add')
    form = crud.create(table, 
                       next = URL(index_link))
    return dict(menu = menu, 
                title = title, 
                form = form)

@auth.requires(auth.has_membership(role = 'Admin') or
               auth.has_membership(role = 'Manager'))
def __add_1(table, 
            index_link, 
            search_link, 
            manage_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')), 
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')), 
            ' ]')
    title = T('Add')
    form = crud.create(table,
                       onvalidation = __date_comparation, 
                       onaccept = __update_table_2, 
                       next = URL(index_link)
                       )
    return dict(menu = menu, 
                title = title, 
                form = form)

@auth.requires(auth.has_membership(role = 'Admin') or
               auth.has_membership(role = 'Manager'))
def __add_2(table, 
            index_link, 
            draft_link,
            search_link, 
            manage_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Draft'), 
              _href = URL(draft_link), 
              _title = T('Draft')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')), 
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')),
            ' ]')
    title = T('Add')
    form = crud.create(table)
    return dict(menu = menu, 
                title = title, 
                form = form)

@auth.requires_login()
def __add_3(table_0, 
            index_link,
            table_1, 
            field):
    page = table_0(request.args(0)) or redirect(URL(index_link))
    field.default = page.id
    form = crud.create(table_1,
                       message = T('Record Inserted'), 
                       next = URL(args = page.id))
    return dict(page = page, 
                form = form)

@auth.requires(auth.has_membership(role = 'Manager'))
def __edit_0(table, 
             index_link, 
             add_link, 
             search_link, 
             show_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')),  
            ' | ', 
            A(T('Show'), 
              _href = URL(show_link, 
                          args = request.args), 
              _title = T('Show')), 
            ' ]')
    title = T('Edit')
    page = table(request.args(0)) or redirect(URL(index_link))
    form = crud.update(table, 
                       page, 
                       next = URL(show_link, 
                                  args = request.args), 
                       onaccept = crud.archive)
    return dict(menu = menu, 
                title = title, 
                form = form)

@auth.requires(auth.has_membership(role = 'Manager'))
def __edit_1(table, 
             index_link, 
             draft_link,
             add_link, 
             search_link, 
             show_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Draft'), 
              _href = URL(draft_link), 
              _title = T('Draft')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')),  
            ' | ', 
            A(T('Show'), 
              _href = URL(show_link, 
                          args = request.args), 
              _title = T('Show')), 
            ' ]')
    title = T('Edit')
    page = table(request.args(0)) or redirect(URL(index_link))
    form = crud.update(table, 
                       page, 
                       next = URL(show_link, 
                                  args = request.args), 
                       onaccept = crud.archive)
    return dict(menu = menu, 
                title = title, 
                form = form)

def __show_0(table, 
             index_link, 
             add_link, 
             search_link, 
             edit_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')),  
            ' | ', 
            A(T('Edit'), 
              _href = URL(edit_link, 
                          args = request.args), 
              _title = T('Edit')), 
            ' ]')
    page = table(request.args(0)) or redirect(URL(index_link))
    return dict(menu = menu, 
                page = page)

@auth.requires_login()
def __show_1(table, 
             index_link, 
             draft_link, 
             add_link, 
             search_link, 
             edit_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Draft'), 
              _href = URL(draft_link), 
              _title = T('Draft')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')),  
            ' | ', 
            A(T('Edit'), 
              _href = URL(edit_link, 
                          args = request.args), 
              _title = T('Edit')),
            ' ]')
    page = table(request.args(0)) or redirect(URL(index_link))
    return dict(menu = menu, 
                page = page)

@auth.requires_login()
def __show_2(table_0, 
             index_link, 
             table_1, 
             field, 
             active):
    page = table_0(request.args(0)) or redirect(URL(index_link))
    results = db((field == page.id) & (active == True)).select(orderby = ~table_1.id, 
                                                               cache = (cache.ram, 
                                                                        10))
    return dict(page = page, 
                results = results)

def __search_0(table, 
               index_link, 
               add_link, 
               manage_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')),
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')),
            ' ] ')
    title = T('Search')
    search, rows = crud.search(table)
    return dict(menu = menu, 
                title = title, 
                table = table,
                search = search, 
                rows = rows)

def __search_1(table, 
               index_link, 
               draft_link, 
               add_link, 
               manage_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Draft'), 
              _href = URL(draft_link), 
              _title = T('Draft')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')),
            ' | ', 
            A(T('Manage'), 
              _href = URL(manage_link), 
              _title = T('Manage')),
            ' ] ')
    title = T('Search')
    search, rows = crud.search(table)
    return dict(menu = menu, 
                title = title, 
                table = table,
                search = search, 
                rows = rows)

@auth.requires(auth.has_membership(role = 'Manager'))
def __manage_0(table, 
               index_link, 
               add_link, 
               search_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')),  
            ' ] ')
    title_1 = T('Manage')
    title_2 = T('Search')
    form = crud.update(table, 
                       request.args(1), 
                       message = T("Succeed"), 
                       onaccept = crud.archive)
    table.id.represent = lambda id: A('Edit:', 
                                      id, 
                                      _href = URL(args = (request.args(0), 
                                                          id)))
    search, rows = crud.search(table)
    return dict(menu = menu, 
                title_1 = title_1, 
                title_2 = title_2, 
                form = form, 
                table = table,
                search = search, 
                rows = rows)

@auth.requires(auth.has_membership(role = 'Manager'))
def __manage_1(table, 
               index_link, 
               draft_link, 
               add_link, 
               search_link):
    menu = ('[ ', 
            A(T('Index'), 
              _href = URL(index_link), 
              _title = T('Index')), 
            ' | ', 
            A(T('Draft'), 
              _href = URL(draft_link), 
              _title = T('Draft')), 
            ' | ', 
            A(T('Add'), 
              _href = URL(add_link), 
              _title = T('Add')), 
            ' | ', 
            A(T('Search'), 
              _href = URL(search_link), 
              _title = T('Search')),  
            ' ] ')
    title_1 = T('Manage')
    title_2 = T('Search')
    form = crud.update(table, 
                       request.args(1), 
                       message = T("Succeed"), 
                       onaccept = crud.archive)
    table.id.represent = lambda id: A('Edit:', 
                                      id, 
                                      _href = URL(args = (request.args(0), 
                                                          id)))
    search, rows = crud.search(table)
    return dict(menu = menu, 
                title_1 = title_1, 
                title_2 = title_2, 
                form = form, 
                table = table,
                search = search, 
                rows = rows)
                
def __update_table_2(form):
    if request.function == 'check_out_add':
        db.room(db.room.id == form.vars.room_id).update_record(status_id = 1)
    elif request.function == 'cleaning_add':
        db.room(db.room.id == form.vars.room_id).update_record(status_id = 2)
    elif request.function == 'booking_add':
        db.room(db.room.id == form.vars.room_id).update_record(status_id = 3)
    elif request.function == 'check_in_add':
        db.room(db.room.id == form.vars.room_id).update_record(status_id = 4)
                
def __date_comparation(form):
    if request.function == 'booking_add':
        if form.vars.from_date > form.vars.to_date:
            form.errors.to_date = 'To Date must Greater than From Date'

def __like(table):
    page = table[request.vars.id]
    new_like = page.like + 1
    page.update_record(like = new_like)
    return str(new_like)
