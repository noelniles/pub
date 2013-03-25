Pub
======

Inpired by [bashblog](https://github.com/carlesfe/bashblog); Create, edit and manage a blog, simply.

**Dependencies:**  
**-------------**  
BeautifulSoup: `sudo yum install python-BeautifulSoup`

**Setup:**  
**------**  

    1. Modify the variables in pb.py to suit your needs
    2. Make sure your `$EDITOR` is set


**Usage:**<br>
**------**<br>
    - create a post -- create blog post and update index file  
         `pb.py -p`  
    - edit a live post -- preserve timestamp while editing blog file  
         `pb.py -e 'name of existing file'`  

**TODO:**<br>
    - massage documentation<br>
    - use tempfiles<br>
    - decouple<br>
    - move strings to resource file<br>
    - SHIP IT!<br>
