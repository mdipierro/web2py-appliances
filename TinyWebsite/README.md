TinyWebsite
============

TinyWebsite, a basic CMS that allows you to create, update, delete your website pages.
TinyWebsite is powered by Web2py, python web framework (http://www.web2py.com/)

When you create a page, you can choose
- A parent page
- The content, with a wysiwyg editor (you can also upload images)
- The layout (Activate a left sidebar or a right sidebar)
- A component :
    * Photo_gallery : to render random images of the image gallery
    * News : to see the latest news on your website
    * Calendar : You can attach a calendar to a page, and manage the booking requests

Tiny_website also includes :
- A photo gallery
- A list of files to download
- A contact form

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
