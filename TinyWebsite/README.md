TinyWebsite
============

TinyWebsite, a simple CMS that allows you to create, update, delete your website pages.
TinyWebsite is powered by Web2py, python web framework (http://www.web2py.com/)

When you create a page, you can choose
- A parent page
- The content, with a wysiwyg editor (you can also upload images)
- The layout (Activate a left sidebar or a right sidebar)
- A component :
    * Calendar with a booking form (receive and manage booking request notifications)
    * Events calendar (visitors can see how many positions remains available) and possibility to subscribe to an event
    * Latest news
    * Photo gallery rendered with Twitter bootstrap carousel
    * File manager : attach downloadable files to your pages
    * Newsletter
    * Contact (you can have several addresses and display them on contact form)

- Advanced built-in features :
    * Automatic RSS feed for latest news
    * Create protected downloadable files visible only for registered users
    * Edit your pages content directly with raw HTML
    * Add a custom banner
    * Define a custom bootstrap theme file
    * Use your own custom CSS file
    * Google Analytics automatic tracking


... and some other features to come...

You can have a look at the final result here : http://www.tinywebsite.net

Requirements
============
- Python 2.5+
- PIL
- web2py

Installation
============
- git clone git://github.com/web2py/web2py.git web2py
- cd web2py/applications
- git clone git://github.com/espern/tiny_website.git
- cd ..
- python web2py.py -a "choose_a_password"

In your favourite browser you can open : http://localhost:8000/tiny_website
