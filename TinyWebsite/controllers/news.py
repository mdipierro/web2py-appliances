def news():
    """
    Allows to access the "news" component
    """
    manager_toolbar = ManagerToolbar('news')
    rows = db(db.news).select(limitby=(0,6),orderby=~db.news.date|~db.news.published_on)
    newsS = [row for row in rows.find(lambda row: row.date >= request.now.date())]
    max_news = WEBSITE_PARAMETERS.max_old_news_to_show if WEBSITE_PARAMETERS.max_old_news_to_show is not None else 0
    newsS += [row for row in rows.find(lambda row: row.date < request.now.date())[:max_news]]
    return dict(newsS=newsS,
                manager_toolbar=manager_toolbar)

@auth.requires_membership('manager')
def edit_news():
    news = db.news(request.args(0))
    crud.settings.update_deletable=False
    if len(request.args) and news:
        form = crud.update(db.news,news,next=URL('default','index'))
    else:
        form = crud.create(db.news,URL('default','index'))
    return dict(news=news, form=form)

@auth.requires_membership('manager')
def delete_news():
    news = db.news(request.args(0))
    if len(request.args) and news:  
        form = FORM.confirm(T('Yes, I really want to delete this news'),{T('Back'):URL('index')})
        if form.accepted:
            #remove the news
            db(db.news.id==news.id).delete()
            session.flash = T('News deleted')
            redirect(URL('default', 'index'))
    return dict(news=news, form=form)

def rss_news():
    newsS = db(db.news).select(orderby=~db.news.date|~db.news.published_on)
    return dict(title=T('%s latest news',WEBSITE_PARAMETERS.website_name),
                link=WEBSITE_PARAMETERS.website_url if WEBSITE_PARAMETERS.website_url else '',
                description=T('%s latest news',WEBSITE_PARAMETERS.website_name),
                entries=[
                  dict(title=news.title.decode("utf-8", "replace" ),
                  link=WEBSITE_PARAMETERS.website_url if WEBSITE_PARAMETERS.website_url else '',
                  created_on = news.published_on,
                  description=news.text.decode("utf-8", "replace" )) for news in newsS
                ])