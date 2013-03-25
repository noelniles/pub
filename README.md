Pub
======

<p>Inpired by 
<a href="https://github.com/carlesfe/bashblog/blob/master/bb.sh">bashblog</a>
Create, edit and manage a blog, simply.
</p>

<b>Dependencies:</b><br>
<b>-------------</b>
<h5>BeautifulSoup:</h5> `sudo yum install python-BeautifulSoup`

<b>Setup:</b><br>
<b>------</b>
<ol>
    <li>Modify the variables in pb.py to suit your needs</li>
    <li>Make sure your `$EDITOR` is set</li>
</ol>

<b>Usage:</b><br>
<b>------</b>
<ul>
    <li>create a post -- create blog post and update index file</li>
         `pb.py -p`
    <li>edit a live post -- preserve timestamp while editing blog file</li>
         `pb.py -e 'name of existing file'`
</ul>

<b>TODO:</b>
    <ul>
        <li>Massage comments</li>
        <li>refactor</li>
        <li>package this sucker</li>
        <li>move strings to resource file</li>
        <li>SHIPIT!</li>
    </ul>
    
