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
	if WEBSITE_PARAMETERS.add_website_name_as_logo:
		website_name=[XML(c) if c.islower() else B(c) for c in WEBSITE_PARAMETERS.website_name]
		response.logo = A(website_name,_class="brand",_href=URL('pages','show_page'))
	if WEBSITE_PARAMETERS.seo_website_title:
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

pages = db((db.page.is_index==False) & ((db.page.is_enabled==True) | (db.page.is_enabled==None))).select(orderby=db.page.rank|db.page.title, cache=(cache.ram,5),cacheable=True)
pages_menu = HierarchicalMenu()
response.menu += pages_menu.create_menu(pages)

nb_images = db(db.image).count(cache=(cache.ram,60))
if nb_images:
	response.menu += [(T('Photo gallery'), False, URL('images','images'))]

nb_files = db(db.file.page<1).count(cache=(cache.ram,60))
if nb_files or auth.has_membership('manager'):
	response.menu += [(T('Files to download'), False, URL('files','files_list'))]


nb_booking_requests = db(db.calendar_booking_request.is_confirmed==False).count(cache=(cache.ram,60))
management_menu = []
if (WEBSITE_PARAMETERS and WEBSITE_PARAMETERS.show_booking_menu and nb_booking_requests and (auth.has_membership('manager')) or auth.has_membership('booking_manager')):
	management_menu += [(T('Booking requests (%d)', nb_booking_requests), False, URL('calendar','edit_booking_requests'))]
if (WEBSITE_PARAMETERS and WEBSITE_PARAMETERS.show_event_menu and (auth.has_membership('manager')) or auth.has_membership('event_manager')):
	management_menu += [(T('Events calendar'), False, URL('calendar','edit_events_calendar'))]
	management_menu += [(T('Contacts calendar'), False, URL('calendar','edit_contacts_calendar'))]
if auth.has_membership('manager'):
	management_menu += [(T('Website settings'), False, URL('default','settings'))]
if management_menu :
	response.menu += [(T('Website management'), False, None, management_menu)]
response.menu += [(T('Contact'), False, URL('default','contact_form'))]

# if auth.has_membership('manager'):
# 	response.menu += [(T('Website administration'),False, None, [
# 			[T('Add a page'), False, URL('default', 'edit_page')],
# 			[T('Add an image in library'), False, URL('images', 'edit_image')],
# 		])]

#Disable "registration" and "lost password" menu
auth.settings.actions_disabled.append('register') 
auth.settings.actions_disabled.append('request_reset_password')
