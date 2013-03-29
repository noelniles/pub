#!/usr/bin/python
import argparse
import glob
import os
import random
import re
import sys
import time
from datetime import date
import webbrowser
from bs4 import BeautifulSoup as bs

"""pub is inspired by bashblog, a program written by Carles Fenolosa.

    This program is made by Noel Niles and isn't very good or original.
    Basically it builds a text file converts it to html and then rebuilds the 
    index and anything else that needs rebuilt.
    
    Dependencies:   
    - python-BeautifulSoup: I will eventually include this, but for now you 
                            must install BeautifulSoup manually
    
    Files that this script generates(so far):
    - all_posts.html
    - index.html 
    - one html file for each post; these are stored in '/posts/'
    - a bunch of tmp files that are eventually deleted
    
    There are a lot of loops on '*.html' so keep everything else out of this 
    dir. Be careful to write valid html!

"""
class Pub():


    #Define some constants.
    SOFTWARE_NAME = "pub" 
    SOFTWARE_VERS = "0.0.1"
    """Blog information"""
    BLOG_NAME = "MY_BLOG"
    BLOG_DESC = ""
    BLOG_ADDR = "http://www.myblog.com"
    #Author information
    AUTH_NAME = "Author Name"
    AUTH_ADDR = "http://authors_address.com"
    AUTH_MAIL = "author@email.com"
    #Licensing and stuff
    LICENSE = "GPLv3000"  
    #Blog generated files
    INDEX_FILE = "index.html"
    NUMBER_OF_INDEX_ARTICLES = "8"
    ARCHIVE_INDEX = "all_posts.html"
    BLOG_FEED = "feed.rss"
    #Localization an i18n
    #Used in link after every post
    TEMPLATE_COMMENTS = "Comments?"
    #Used on the bottom of every page to link to archive
    TEMPLATE_ARCHIVE = "View more posts?"
    #link back to the blog index
    TEMPLATE_ARCHIVE_INDEX_PAGE = "Back to the blog index?"
    #Used on the bottom of index page. It is link to RSS feed
    TEMPLATE_SUBSCRIBE = "Subsribe?"
    #Used as text for browser feed button that is embedded to html
    TEMPLATE_SUBSCIRBE_BROWSER_BUTTON = "Subscribe to this page?..."
    #The locale and format used for the date
    DATE_FORMAT = "%a, %d %b %Y %H:%M"
    DATE_LOCALE = ""
    
    """
        Check the $EDITOR variable.
        
        If the system editor is not set try to use vim; otherwise give up
        
    """
    def check_editor(self):
        #check if the editor is set
        print 'checking setup'
        if not os.getenv('EDITOR'):
            print 'please set your $EDITOR variable'
            wanna_use_vim = raw_input('want to use vim? [Y]es or [N]o')
            if wanna_use_vim.upper() == 'Y':
                os.environ['EDITOR'] = 'vim'
            else:
                print 'OK, no more suit yourself\n'
                print 'leaving pub'
                sys.exit()
        else:
            print 'editor checks good'
    
    """
        List all of the posts
               
    """
    def list_posts(self):
        posts = os.listdir('posts')
        
        for post in posts:
            print post
                
    """
        Rebuild the index.
        
        Build a new index.html file when a new post is made 
        
        Vars:
        content        -- the actual post in between the entry begin and entry end 
                          tags
        new_index_file -- temporary index file
        content_list   -- list containing all of the post content
        post_dir       -- directory that contains all of the posts '/posts/'
        
        TODO(noel): Sort the posts by date. chmod? 
        
    """
    def rebuild_index(self):
        print 'rebuilding the index'
        rstr = str(random.randint(1, 1000000))
        new_index_file = '%s.%s' % (self.INDEX_FILE, rstr)
        content_list = []

        #all of the posts
        for i in self.sort_ls('posts/'):
            with (open(os.getcwd()+'/posts/'+i)) as post_file:
                post_html = post_file.read()
                content = re.search(ur'<!-- entry begin -->(.*?)<!-- entry end -->', post_html, re.DOTALL)
                if content:
                    content_list.append(content.group(1))
        
        content_list = ''.join(content_list)       
        self.create_html_page(content_list, new_index_file, 'no', self.
                              BLOG_NAME)
        
        os.system('%s %s %s' % ('mv', new_index_file, self.INDEX_FILE))
    
    def sort_ls(self, path):
        mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return list(sorted(os.listdir(path), key=mtime, reverse=True))

    def all_posts(self):
        """
            Create archive all_posts.html page with all of the posts.
            
            Vars:
            filename     -- string; archive file
            tmp_filename -- string; temporary archive file
            text         -- file; text from all of the post files
            soup         -- all of the posts inside a bs object
            ttag         -- all of the titles with the <title> tags
            tlst         -- list of all titles sans tags
            title        -- list of all the pretty titles we just grabbed
            posts        -- glob of all the html files in '/posts' dir
            titles       -- itertable of tlst
            
        """
        print "creating an "
        prefix = str(random.randint(1, 1000000))
        filename = self.ARCHIVE_INDEX
        tmp_filename = '%s.%s.%s' % (prefix, filename, 'tmp')
        
        #find all of the post titles in the post dir
        posts = glob.iglob('posts/*.html')
        title = []
        content = []
        
        #get all of the titles 
        for v in self.sort_ls('posts/'):
            with open(os.getcwd()+'/posts/'+v) as post:
                #get the date
                stat = os.stat(os.getcwd()+'/posts/'+v)
                udate = stat.st_mtime
                #convert the date to pretty date
                hdate = date.fromtimestamp(udate)
                text = post.read()
                soup = bs(''.join(text))
                ttag = soup.title
                tlst = ttag.contents
                titles = iter(tlst)
                titles = titles.next()
                #clean up the title        
                title.append(''.join(['<li><a href=%s/%s>%s',
                                      '</a>&mdash;%s',
                                      '</li>']) % (self.BLOG_ADDR, v, 
                                                   titles, hdate))
                                    
        #opening tags for the content
        
        content.append('<h3>All Posts</h3><ul>')  
        for i,t in enumerate(title):                                   
            content.append(''.join([title[i]]))

        #join the content with the closing tags
        #TODO(noel): the link is created with a tmp file name that will
        #            no longer exist. create_html_page should strip 
        #            the prefix and '.tmp'
        content.append('</ul>')
        self.create_html_page(''.join(content), tmp_filename, 'no', 
                              self.BLOG_NAME+' all posts')
        
        #move tmp file to archive
        os.system(('%s %s %s') % ('mv', tmp_filename, filename))
    
    def create_html_page(self, content, filename, index, new_title):
        """
            Create an html page.
    
            Uses input from write_entry() and the html includes
            created by create_includes to build a complete html page.
                
            Keyword Arguments:
            content   -- the actual content of a new post
            filename  -- filename created by write_entry()
            index     -- 'yes' to generate a new index.html, 'no' to insert
                         new blog posts
            new_title -- title for html header generated by write_entry()
            
            TODO(noel): - Building the html string might be able to be 
                          separated into its own method.
                        - Write the files in a loop.
               
        """
    
        #get the correct filename from rebuilt files
        
        file_url = filename.split('.rebuilt')[0]
        blog_addr = self.BLOG_ADDR
        auth_name = self.AUTH_NAME
        
        # read the header template
        
        with open(".header.html", "r") as header:
            header_str = header.read()
            
        # read the title string
        
        with open(".title.html", "r") as title:
            title_str = title.read()
            
        #read the footer string
        
        with open(".footer.html", "r") as footer:
            footer_str = footer.read()
            
        #create the timestamp
        
        timestamp = time.strftime(self.DATE_FORMAT)
                
        # If this blog doesn't exist yet then create new timestamp, 
        # author and new begining tags
        if index is 'no':
            new_post = ''.join(['<!-- entry begin -->',
                                '<h3><a class="ablack"',
                                ' href="%(blog_addr)s/%(file_url)s">',
                                '%(new_title)s',
                                '</a></h3>',
                                '<div class="subtitle">&mdash;',
                                '%(timestamp)s ',
                                '%(auth_name)s',
                                '</div>',
                                '<!-- text begin -->',
                               ]) % locals()
                                
            end_tags = ''.join(['<!-- text end -->',
                                '<!-- entry end -->',
                               ])
            
        """
            Build the html page.
        
            All of the strings are ready to be put into BeautifulSoup.
            
            Variables:
            header_str -- string that comes from '.header.html' file
            new_title  -- title of new blog entry;  
            title_str  -- blog name string comes from '.title.html'
                          file 
            new_post   -- string; created if index is 'no'; builds the
                          beginning of a new blog
            content    -- string; this will be created by
                          write_entry()   
            end_tags   -- string; created if index is 'no'; builds end
                          of new blog
            footer_str -- string; comes from '.footer.html' file
                
        """
        html = bs(''.join(['%(header_str)s',
                           '<title>%(new_title)s</title>',
                           '</head><body>', #end of head; beginning of body
                           #self.google_analytics(),
                           '<div id="divbodyholder">',
                           '<div class="headerholder"><div class="header">',
                           '<div id="title">',
                           '%(title_str)s',
                           '</div></div></div>',
                           '<div id="divbody"><div class="content">',
                           '%(new_post)s',
                           '%(content)s',
                           '%(end_tags)s',                           
                           '%(footer_str)s',
                           '</div></div>',
                           '</body></html>'
                          ]) % locals()).prettify()

        #write the html file
        
        with open(filename, "w+") as hf: #[h]tml [f]ile
            hf.write(html.encode('utf-8'))    
           
    """ 
        Create_includes
        
        Creates the temp files that are used as the title 
        header and footer
        
        TODO(noel): - Get rid of those useles vars and fix the strings. 
                    - Write the files in a loop.
               
    """
    def create_includes(self):
    
        blog_addr = self.BLOG_ADDR
        blog_name = self.BLOG_NAME
        license = self.LICENSE
        auth_addr = self.AUTH_ADDR
        author = self.AUTH_NAME
        safe_mail = self.AUTH_MAIL
        
        title_str = ''.join(['<h1 class="nomargin">',
                             '<a class="ablack"',
                             'href="%(blog_addr)s">%(blog_name)s</a>',
                             '</h1>',
                            ]) % locals()
                   
        header_str = ''.join(['<!DOCTYPE html>',
                              '<head>',
                              '<meta http-equiv="Content-type"',
                              'content="text/html;charset=utf-8" />',
                              '<link rel="stylesheet" href="main.css"',
                              'type="text/css" />',
                              '<link rel="stylesheet" href="blog.css"',
                              'type="text/css" />',
                             ])
                  
        footer_str = ''.join(['<div id="footer">%(license)s',
                              '<a href="%(auth_addr)s">',
                              '%(author)s</a> &mdash;',
                              '<a href="mailto:'
                              '%(safe_mail)s">%(safe_mail)s</a>',
                              '</div>'
                             ]) % locals()
        
        #write header, footer and title templates
        
        with open('.title.html', 'w+') as title_file:
            title_file.write(title_str)
        with open('.header.html', 'w+') as header_file:
            header_file.write(header_str)
        with open('.footer.html', 'w+') as footer_file:
            footer_file.write(footer_str)
    
    """
       Write entry manges the creation of html file
       
       TODO(noel): This might be kind of smelly
       
    """
    def write_entry(self, post_status):
        
        tmp_str = ''.join(['title on this line(do not use apostophies!)\n',
                           '<p>The rest of the text file is an',
                           '<b>html</b>', 
                           'blog post. The process will continue when ', 
                           'you exit the editor</p>',
                          ])
        tmp_file = ''.join([str(random.randint(0,1000000)),'.tmp.html'])
                          
        with open(tmp_file, 'w+') as tmp:
            tmp.write(tmp_str)

        
        while post_status:
            
            #Edit the post
            if post_status.upper() == 'E':
                #edit the file 
                editor = str(os.getenv('EDITOR'))
                os.system('%s %s/%s' % (editor, os.getcwd(), tmp_file))

                #get title from first line of file
                with open(tmp_file) as f:
                    #title is the first line
                    title = f.readline()
                    #content or body is the rest
                    content = f.read()
            
                #change the filename to the title string with underscores
                #clean the filename so bash doesn't give up'
                filename = title.replace(' ', '_').strip().lower()
                pat = re.compile('[^\w\s]+')
                filename = pat.sub('', filename)
                filename += '.html'
            
                #create the html page
                self.create_html_page(content, filename, 'no', title) 
            
                preview = raw_input('would you like to preview the page?'
                                    '[y]yes or [n]no\n')
            
                if preview.upper() == 'Y':
                    preview_filename = 'file:///%s/%s' % (os.getcwd(),
                                                          filename)

                    webbrowser.open_new_tab(preview_filename)
                
            post_status = raw_input('[E]dit, [D]raft, [P]ost\n')
            
            #Save post to drafts folder
            if post_status.upper() == 'D':
                #create the drafts folder if it's not there
                if not os.path.isdir(''.join([os.getcwd(), '/drafts'])):
                    os.mkdir(os.getcwd()+'/drafts', 0700)

                #move the newly created file into drafts
                #TODO(noel): add '.draft' to the filename
                cmd = ''.join(['mv ',
                               '%s/%s ',
                               '%s/drafts/',
                              ]) % (os.getcwd(),filename, os.getcwd())

                os.system(cmd)
                
                print ' '.join(['saved your file to',                               
                               '%s/drafts/%s',
                              ]) % (os.getcwd(), filename)
                break
            
            #Save post to posts folder
            if post_status.upper() == 'P':
                if not os.path.isdir(''.join([os.getcwd(), '/posts'])):
                    os.mkdir(os.getcwd()+'/posts', 0700)
                
                cmd = ''.join(['mv ',
                               '%s/%s ', 
                               '%s/posts',
                              ]) % (os.getcwd(), filename, os.getcwd())

                os.system(cmd)

                print "blog posted"
                break
                   
            
    """
        Delete the tempory files
        
    """
    def delete_includes(self):
    
        temporary_files = glob.iglob('*.html')
        
        for i in temporary_files:
            #do not remove the archive file or the index file
            if i != self.ARCHIVE_INDEX and i != self.INDEX_FILE:
                os.remove(i)
            
    """
        Edit an html file keeping the original timestamp
        
    """        
    def edit_html(self, file_to_edit):
    
        post_date = os.stat(os.getcwd()+'/'+file_to_edit)
        editor = str(os.getenv('EDITOR'))
        
        os.system(editor +" " + os.getcwd() +'/'+ file_to_edit)
        os.utime(file_to_edit, (post_date.st_atime, post_date.st_mtime))
         
    def main(self):
        self.check_editor()
        #Create includes
        self.create_includes()
        #Create parser for command line arguments
        parser = argparse.ArgumentParser(
                            description='Edit a blog from the command line')
        #Add command line arguments                    
        parser.add_argument('-e','--edit', nargs=1, 
                            help='''edit a live blog file; do not manually 
                            edit blog files. This functions maintains the 
                            original timestamp''')
                            
        parser.add_argument('-p', '--post', action='store_true',
                            help='''insert a new blog post or the FILENAME of 
                                    a draft to continue editing it.''')
        
        parser.add_argument('-l', '--list', action='store_true',
                            help="""List all the the live posts""")
                    
        self.args = parser.parse_args()
        
        if self.args.edit:
            file_to_edit = str(self.args.edit[0])
            self.edit_html(file_to_edit)
            
        if self.args.post:
            self.write_entry('E')
            #Generate an html page with all of the posts
            self.all_posts()
            #rebuild the index
            self.rebuild_index()
            
        if self.args.list:
            self.list_posts()
        
        #delete the junk
        self.delete_includes()
                                                  
                                                      
if __name__ == "__main__": 
    pub = Pub()
    pub.main()
