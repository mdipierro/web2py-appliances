# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

## read more at http://dev.w3.org/html5/markup/meta.name.html

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################
from menu_tools import HierarchicalMenu

#If we don't show the banner, we add the website name with a link to index page
if WEBSITE_PARAMETERS:
	if not WEBSITE_PARAMETERS.with_banner:
		website_name=[XML(c) if c.islower() else B(c) for c in WEBSITE_PARAMETERS.website_name]
		response.logo = A(website_name,_class="brand",_href=URL('default','index'))
	if WEBSITE_PARAMETERS.website_title:
		response.title = WEBSITE_PARAMETERS.seo_website_title
	if WEBSITE_PARAMETERS.website_subtitle:
		response.subtitle = WEBSITE_PARAMETERS.website_subtitle

	if WEBSITE_PARAMETERS.seo_meta_author:
		response.meta.author = WEBSITE_PARAMETERS.seo_meta_author
	if WEBSITE_PARAMETERS.seo_meta_description:
		response.meta.description = WEBSITE_PARAMETERS.seo_meta_description
	if WEBSITE_PARAMETERS.seo_meta_keywords:
		response.meta.keywords = WEBSITE_PARAMETERS.seo_meta_keywords
	if WEBSITE_PARAMETERS.seo_meta_generator:
		response.meta.generator = WEBSITE_PARAMETERS.seo_meta_generator

pages = db(db.page.is_index==False).select(orderby=db.page.rank|db.page.title)

pages_menu = HierarchicalMenu()
response.menu += pages_menu.create_menu(pages)

images = db(db.image).select()
if images:
	response.menu += [(T('Photo gallery'), False, URL('images','images'))]

files = db(db.file.page<1).select()
if files or auth.has_membership('manager'):
	response.menu += [(T('Files to download'), False, URL('files','files_list'))]


nb_booking_requests = db(db.calendar_event.is_confirmed==False).count()
booking_menu = []
if nb_booking_requests and auth.has_membership('booking_manager'):
	booking_menu = [(T('Booking requests (%d)', nb_booking_requests), False, URL('calendar','edit_booking_requests'))]
if booking_menu :
	response.menu += [(T('Website management'), False, None, booking_menu)]
response.menu += [(T('Contact'), False, URL('default','contact_form'))]

# if auth.has_membership('manager'):
# 	response.menu += [(T('Website administration'),False, None, [
# 			[T('Add a page'), False, URL('default', 'edit_page')],
# 			[T('Add an image in library'), False, URL('images', 'edit_image')],
# 		])]

#Disable "registration" and "lost password" menu
auth.settings.actions_disabled.append('register') 
auth.settings.actions_disabled.append('request_reset_password')
