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
import conf
print locals()
class Pub():
    """pub is inspired by bashblog, a program written by Carles Fenolosa.

        This program is made by Noel Niles and isn't very good or original.
        Basically it builds a text file converts it to html and then rebuilds 
        the index and anything else that needs rebuilt.
        
        Files that this script generates(so far):
        - all_posts.html
        - index.html 
        - one html file for each post; these are stored in '/posts/'
        - a bunch of tmp files that are eventually deleted
        
        There are a lot of loops on '*.html' so keep everything else out of 
        this dir. Be careful to write valid html!

    """

    def setup(self):
        gen_dirs = (conf.DRAFT_DIR, conf.POST_DIR)
        for directory in gen_dirs:
            if not os.path.isdir(directory):
                os.mkdir(directory, 0755)

        #check if the editor is set
        print 'checking setup'
        if not os.getenv('EDITOR'):
            print 'please set your $EDITOR variable'
            wanna_use_vim = raw_input('want to use vim? [Y]es or [N]o')
            if wanna_use_vim.upper() == 'Y':
                os.environ['EDITOR'] = 'vim'
            else:
                print 'leaving pub'
                sys.exit()
        else:
            print 'using %s to edit files' % (os.getenv('EDITOR'))

    def backup_posts(self):
        src = os.path.join(os.getcwd(), conf.POST_DIR)
        des = os.path.join(os.getcwd(), 'backups')

        os.system('rsync -ab %s %s' % (src, des))
        print 'backup completed'

    def rebuild_css(self):
        """Rebuilds the href attribute; used when the css changes."""

        print 'rebuilding css'
        oldfiles = os.listdir(conf.POST_DIR)
        for oldfile in oldfiles:
            abs_oldfile = '%s/%s/%s' % (os.getcwd(), 'posts', oldfile)
            newfilename = '%s.rebuilt' % abs_oldfile
            stats = os.stat(abs_oldfile)
            with open(abs_oldfile) as text:
                soup = bs(text)
                tag = soup.link
                tag['href'] = '%s/%s' % (conf.CSS_DIR, conf.CSS_FILE)

                with open(newfilename, 'w+') as newfile:
                    newfile.write(soup.encode("ascii"))
                os.system('%s %s %s' % ('mv', newfilename, abs_oldfile))
                os.utime(abs_oldfile, (stats.st_atime, stats.st_mtime))

    def rebuild_index(self):
        """
            Rebuild the index.
            
            Build a new index.html file when a new post is made 
            
            Vars:
            content        -- the actual post in between the entry begin 
                              and 
                              entry end tags
            new_index_file -- temporary index file
            content_list   -- list containing all of the post content
            
            TODO(noel): chmod? 
            
        """
        print 'rebuilding the index'
        rstr = str(random.randint(1, 1000000))
        new_index_file = '.%s.%s' % (rstr, conf.INDEX_FILE)
        content_list = []

        #all of the posts
        for sorted_post in self.sort_ls(conf.POST_DIR):
            filename = '%s/%s' % (conf.POST_DIR, sorted_post)
            with (open(filename)) as post_file:
                post_html = post_file.read()
                content = re.search((ur'<!-- entry begin -->(.*?)<!-- entry ' 
                                     'end -->'), post_html, re.DOTALL)
                if content:
                    content_list.append(content.group(1))
        
        content_list = ''.join(content_list)       
        self.create_html_page(content_list, new_index_file, conf.BLOG_NAME)
        
        os.system('mv %s %s' % (new_index_file, conf.INDEX_FILE))

    def sort_ls(self, path):
        """Sort path by reverse mtime, newest first"""
        mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return list(sorted(os.listdir(path), key=mtime, reverse=True))

    def all_posts(self):
        """
            Create archive all_posts.html page with all of the posts.
            
            Vars:
            filename     -- string; archive file
            text         -- file; text from all of the post files
            soup         -- all of the posts inside a bs object
            ttag         -- all of the titles with the <title> tags
            tlst         -- list of all titles sans tags
            titles       -- list of all the pretty titles we just grabbed
            posts        -- glob of all the html files in '/posts' dir
            title        -- itertable of tlst
            
        """
        print "creating an archive "
        filename = conf.ARCHIVE_INDEX
        
        #find all of the post titles in the post dir
        titles = []
        content = []
        
        #get all of the titles 
        for postfile in self.sort_ls(conf.POST_DIR):
            filepath = '%s/%s' % (conf.POST_DIR, postfile)

            with open(filepath) as post:
                print 'HI'
                #get the date
                stat = os.stat(filepath)
                #make sure the file is not empty
                #if it is we have big problems
                if stat.st_size != 0:
                    udate = stat.st_mtime
                    #convert the date to pretty date
                    hdate = date.fromtimestamp(udate)
                    text = post.read()
                    soup = bs(text)
                    ttag = soup.title
                    tlst = ttag.contents
                    title = iter(tlst).next()
                    #clean up the title        
                    titles.append('<li><a href=%s/%s>%s</a>&mdash;%s'
                                  '</li>' % (conf.BLOG_ADDR, filepath, title, 
                                             hdate))
                else:
                    print 'you have an empty file in posts'
        #opening tags for the content
        
        content.append('<h3>All Posts</h3><ul>')  
        for i, t in enumerate(titles):                                   
            content.append(titles[i])

        #join the content with the closing tags
        content.append('</ul>')
        content = ''.join(content)
        self.create_html_page(content, filename, 
                              '%s archive generated at: ' % conf.BLOG_NAME)
        
    def create_html_page(self, content, filename, new_title, 
                         when_created=False):
        """
            Create an html page.
    
            Uses input from and the html includes created by create_includes 
            to build a complete html page.
                
            Keyword Arguments:
            content   -- the actual content of a new post
            filename  -- filename created by write_entry()
            index     -- 'yes' to generate a new index.html, 'no' to insert
                         new blog posts
            new_title -- title for html header generated by write_entry()
            
            TODO(noel): - Building the html string might be able to be 
                          separated into its own method.
               
        """

        #get the correct filename from rebuilt files
        
        file_url = filename.split('.rebuilt')[0]
       
        # read the header template, title and footer

        with open(".header.html", "r") as header:
            header_str = header.read()           
        with open(".title.html", "r") as title:
            title_str = title.read()
        with open(".footer.html", "r") as footer:
            footer_str = footer.read()
            
        #create the timestamp
        
        timestamp = time.strftime(conf.DATE_FORMAT)
                
        # If this blog doesn't exist yet then create new timestamp, 
        # author and new begining tags
        new_post = ('<!-- entry begin --><h3><a href="%s/posts/%s">%s</a>'
                    '</h3><div class="subtitle">&mdash;%s %s</div>'
                    '<!-- text begin -->' % (conf.BLOG_ADDR, file_url,
                                            new_title, timestamp, 
                                            conf.AUTH_NAME))
                    
        end_tags = '<!-- text end --><!-- entry end -->'

        html = ('%s<title>%s</title></head><body><div class="row">'
                '<div class="large-12 columns"><div class="panel">%s</div>'
                '</div></div><div id="row"><div class="large-3 columns">'
                '<div class="panel">%s %s %s %s</div></div></body></html>' 
                % (header_str, new_title, title_str, new_post, content, 
                   end_tags, footer_str))               
        html = bs(html).prettify()

        #write the html file
        with open(filename, "w+") as hf: #[h]tml [f]ile
            hf.write(html.encode('utf-8'))
            if when_created:
                stat = os.stat(filename)
                os.utime(filename, (stat.st_atime, stat.st_mtime))
       
    def create_includes(self):
        """ 
            Create_includes
            
            Creates the temp files that are used as the title 
            header and footer
            
            TODO(noel): - Get rid of those useles vars and fix the strings. 
                   
        """
        title_str = ('<h1><a href="%s">%s</a>'
                     '</h1>' % (conf.BLOG_ADDR, conf.BLOG_NAME))

        header_str = ('<!DOCTYPE html><head><meta http-equiv="Content-type"'
                      'content="text/html;charset=utf-8" />'
                      '<link rel="stylesheet" href="%s/%s" type="text/css" />'
                      % (conf.CSS_DIR, conf.CSS_FILE))
                                        
        footer_str = ('<div id="footer">%s<a href="%s">%s</a> &mdash;'
                      '<a href="mailto:%s">%s</a></div>' % (conf.LICENSE, 
                          conf.AUTH_ADDR, conf.AUTH_NAME, conf.AUTH_MAIL, 
                          conf.AUTH_MAIL)) 
                              
        #write header, footer and title templates
        
        with open('.title.html', 'w+') as title_file:
            title_file.write(title_str)
        with open('.header.html', 'w+') as header_file:
            header_file.write(header_str)
        with open('.footer.html', 'w+') as footer_file:
            footer_file.write(footer_str)

    def write_entry(self, post_status):
        """Write entry manges the creation of html file"""

        tmp_str = ('title on this line(do not use apostophies!)\n'
                   '<p>The rest of the text file is an <b>html</b>'
                   'blog post. The process will continue when '
                   'you exit the editor</p>')

        tmp_file = '.%s.tmp.html' % (random.randint(0, 1000000))
                          
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
                    self.create_html_page(content, filename, title) 
                
                    preview = raw_input('would you like to preview the page?'
                                        '[y]yes or [n]no\n')
                
                    if preview.upper() == 'Y':
                        preview_filename = 'file:///%s/%s' % (os.getcwd(),
                                                              filename)
                        webbrowser.open_new_tab(preview_filename)
                    
                post_status = raw_input('[E]dit, [D]raft, [P]ost\n')

                #Save post to drafts folder
                if post_status.upper() == 'D':
                    #move the newly created file into drafts
                    #TODO(noel): add '.draft' to the filename
                    os.system('mv %s/%s %s' % (os.getcwd(), filename, 
                                               conf.DRAFT_DIR))
                    print 'saved to: %s/%s' % (conf.DRAFT_DIR, filename)
                    break
                
                #Save post to posts folder
                elif post_status.upper() == 'P':
                    os.system('mv %s/%s %s' % (os.getcwd(), filename, 
                                               conf.POST_DIR))
                    print "blog posted"
                    break
                else:
                    print 'invalid entry'

    def edit_html(self, file_to_edit):
        """Edit an html file keeping the original timestamp"""

        post_date = os.stat(os.getcwd()+'/'+file_to_edit)
        editor = str(os.getenv('EDITOR'))
        
        os.system(editor +" " + os.getcwd() +'/'+ file_to_edit)
        os.utime(file_to_edit, (post_date.st_atime, post_date.st_mtime))
         
    def main(self):
        self.setup()
        #Create includes
        self.create_includes()
        #Create parser for command line arguments
        parser = argparse.ArgumentParser(
                            description='Edit a blog from the command line')
        #Add command line arguments                    
        parser.add_argument('-e', '--edit', nargs=1, 
                            help="""edit a blog file""")
                            
        parser.add_argument('-p', '--post', action='store_true',
                            help="""insert a new blog post""")
        
        parser.add_argument('-l', '--list', action='store_true',
                            help="""List all the the live posts""")
                    
        parser.add_argument('-r', '--rebuild', action='store_true',
                            help="""rebuild css references""")

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
        if self.args.rebuild:
            self.rebuild_css()
            self.rebuild_index()
            self.all_posts()
        if self.args.list:
            posts = os.listdir('posts')
            for post in posts:
                print post
        
        #delete the junk
                                                  
        temporary_files = glob.iglob('.*.html')
        for i in temporary_files:
            os.remove(i)
        #backup posts
        self.backup_posts()
                                                      
if __name__ == "__main__": 
    pub = Pub()
    pub.main()
