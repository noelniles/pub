import os

"""Config file for Pub

    I will try to update this very infrequently. This way you can add this 
    file to your gitignore, allowing you to clone in changes to pub without 
    resetting all of you config variables.

"""

#Change dev to False when Pub is run on a server
DEV = True
if DEV is True: BLOG_ADDR = 'file:///%s' % (os.getcwd())
#Change this to the url were Pub has been cloned.
else: BLOG_ADDR = 'http://www.myblog.com/pub'

#Version info
SOFTWARE_NAME = 'pub' 
SOFTWARE_VERS = '0.0.1'

#Blog information
BLOG_NAME = 'MY_BLOG'
BLOG_DESC = ''

#Author information
AUTH_NAME = 'Author Name'
AUTH_ADDR = 'http://authors_address.com'
#I don't use this right now because I need to make an obfuscator
AUTH_MAIL = 'author@email.com'

#Licensing and stuff
LICENSE = 'GPLv3000'

#Blog generated files
INDEX_FILE = 'index.html'
ARCHIVE_INDEX = 'all_posts.html'
POST_DIR =  'posts'
DRAFT_DIR = 'drafts'

#Not used....yet
NUMBER_OF_INDEX_ARTICLES = '8'

#The locale and format used for the date
DATE_FORMAT = '%a, %d %b %Y %H:%M'

#Location of resources: CSS, JS...
RES = 'res'
CSS_DIR = os.path.join(BLOG_ADDR, RES, 'css')
CSS_FILE = 'foundation.css'
