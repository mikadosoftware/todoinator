#!

'''There is a story I like about PG Wodehouse, author of the Jeeves
and Wooster novels.  He had an unusual method of editing his own work.
He would write (long hand) a page of his new book.  And read it, and
place the page on the wall of his study, and start on the next page.
But the page stuck to the wall was not at some random location - it
was, perhaps obviously, in order going horizontally around the room,
but it was also vertically where he thought it should be relative to
the *quality* he expected of himself.::

   "Pages would start near the floor and slowly work their way up
    until they touched the picture rail, when they were good enough
    for publication"

This jibes marvellously with how I think of software development.  It
is focused on the code itself - the rating system is not in a
notebook, spreadsheet or bug tracker, it is a natural extension of where
and how the code is stored.

So I intend to update and release my todo-inator idea.

There are two parts - the rating of the code, by the author.  this will be a simple
five star system ::

   # rate: * * * * *
   # lifecycle: <prototype/PoC>, <pre-release>, maturing, mature, retiring
   # TODO:

And we can then see this rating in a specialised `ls`.

specialised ls - walk over a package source and tell me ::

   star rating
   todos
   new features

I think I will have a second system that correlates to a map of my todos and
some external systems
And some way of recording success / failures

Design
------

walk a source tree, and build a dict of file: {markers...}
return that



Todos 
-----

We have a slight finesse on the TODO.  Every TODO is assigned a
priority. By default that is 30/100.  100 being the most hair on fire
thing we can imagine, and 1 being lets get around to this before the 
heat death of the universe.

but we can alter that priority by putting a {val} after the text
(we do not want to confuse with [x] form of done / not done.)



Future enhancements:

* "TODO-feature: "
* have a store of todos in .todoinator in the current repo, 
  which lets us compute what has changed ?



#TODO: build a test framework / runner {20}
#TODO: build a lifecycle todo listing {99}
#TODO: build a ticketing system??? at least a list of todos
#TODO: linting etc - a pre-commit check system ala phabricator


'''

# rate: **
# life: prototype
# TODO: build basic walk and parse and report features

import os
import re
import logging

VALID_SUFFIX = ['.py', '.rst']
### config
confd = {'todoinator.priorityregex': "\{\d+\}"} 

class TODO(object):
    """
    """
    def __init__(self, line, filepath=None):
        """
        """
        parsedline, priority = parse_line(line)
        self.line = parsedline
        self.priority = priority
        self.origpath = filepath
        try:
            absfilepath = os.path.abspath(filepath)
            bits = absfilepath.split("/")
            idx = bits.index("projects") #assume thats there
            self.reponame = bits[idx+1]
        except ValueError: # cant find projects in path
            self.reponame = '?'


def keep_file(filepath):
    """Decide if we keep the filepath, solely by exlcusion of end of path

    This is primarily to avoid keeping .pyc files

    >>> keep_file('/foo.pyc')
    False

    """
    ignoredpathendings = ['.pyc',]
    for ending in ignoredpathendings:
        if filepath.endswith(ending):
            return False
    return True

def walk_tree(rootpath):
    """
    """
    ignoredirs = ['.git',]

    for dirpath, dirs, files in os.walk(rootpath):
        #change dirs to remove unwanted dirs to descend into
        #rememer we need to use .remove as dirs seems to just point at
        #underlying implementation, so substitution has no effect
        for d in ignoredirs:
            if d in dirs:
                dirs.remove(d)

        files = list(filter(keep_file, files))
        for file in files:
            thisfile = os.path.join(dirpath, file)
            yield thisfile

def parse_file(txt):
    """extract todo lines from a file

    >>> parse_file("# todo: foo\\n foo")
    [' foo']
    
    """
    res = []
    for line in txt.split('\n'):
        if line.strip().startswith('#'):
            #valid possible
            for token in ['todo:']:
                stpoint = line.lower().find(token)
                if stpoint >-1:
                    res.append(line[stpoint+len(token):])
    
    return res

def parse_line(todoline):
    """extract data from a todo line
    
    >>> parse_line(" some note unadorned")
    (' some note unadorned', 30)
    >>> parse_line(" some note {88}")
    (' some note ', 88)
    
    """
    rgx = re.compile(confd['todoinator.priorityregex'])
    vals = rgx.findall(todoline) # returns [] or ['{4}']    
    if vals:
        token = sorted(vals)[-1]
        priority = int(token.replace("{", "").replace("}", ""))
    else:
        token = ''
        priority = 30
    return todoline.replace(token, ''), priority


def parse_tree(rootpath):
    """
    """
    all_todos = []
    textfrag = "TODO\n"
    htmlfrag = "<table>"
    
    for filepath in walk_tree(rootpath):
        # test if suffix valid (ie dont parse pyc or wheel)
        suffix = os.path.splitext(filepath)[1]
        if suffix not in VALID_SUFFIX:
            continue
        try:

            todo_list = parse_file(open(filepath).read())
            res = sorted([TODO(line, filepath) for line in todo_list], key=lambda t: t.priority, reverse=True)
        except IOError:
            res = []
        except UnicodeDecodeError as e:
            logging.error("could not read %s - unicode err",filepath)
            
        if res:
            all_todos.extend(res)

    all_todos = sorted(all_todos, key=lambda t: t.priority, reverse=True)
    for todo in all_todos:
        textfrag += "{0} {2} ({1})\n".format(todo.priority, todo.reponame, todo.line)
        htmlfrag += "<tr><td>%s</td> <td>%s</td> <td>%s</td> </tr>\n" %  (todo.priority, todo.reponame, todo.line)
    htmlfrag += "</table>"
    #######################
    path = "/tmp/todo.html"
    open(path, 'w').write(htmlfrag)
    import webbrowser
    #webbrowser.open(path)
    print(textfrag)

def main():
    rootpath = '/home/pbrian/projects/weaver'
    parse_tree(rootpath)
    
    
if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
 
