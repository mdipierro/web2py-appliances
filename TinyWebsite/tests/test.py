# in MS Windows, create en environment variable (if not exists)
# PYTHONPATH containing the path to web2py

from gluon.contrib.webclient import WebClient

# pages = db().select(db.page.ALL)
# for page in pages:
# 	client.get('pages/show_page/%s' %page.url)
# 	assert(page.title in client.text)

# # register
# data = dict(first_name = 'Homer',
#             last_name = 'Simpson',
#             email = 'homer@web2py.com',
#             password = 'test',
#             password_two = 'test',
#             _formname = 'register')
# client.post('user/register',data = data)

# # logout
# client.get('user/logout')

# # login again
# data = dict(email='homer@web2py.com',
#             password='test',
#             _formname = 'login')
# client.post('user/login',data = data)

# # check registration and login were successful
# client.get('index')
# assert('Welcome Homer' in client.text)
