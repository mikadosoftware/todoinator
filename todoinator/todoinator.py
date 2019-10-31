#! -*- coding:utf-8 -*-

"""There is a story I like about PG Wodehouse, author of the Jeeves
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

There are two parts - the rating of the code, by the author.  this
will be a simple five star system ::

   # rate: * * * * *
   # 

And we can then see this rating in a specialised `ls`.

specialised ls - walk over a package source and tell me ::

   star rating
   todos
   (milestones) new features

I think I will have a second system that correlates to a map of my
todos and some external systems And some way of recording success /
failures

Rating
------

The star rating is more useful as an indicator of *tolerance* - how
tolerant can the buiness-value-creation process be to the quality of
this script.

1* - it can be run by a developer, can fail gracelessly, and may give 95% results
5* - utterly mission critical and runs lights out.

As such we can see a discrepancy - this is of course all self
assemessment but can be useful.  It allows us to focus discussion on
the tolerance of the script during a review.  It gives momentum to
reviews that can be ::

    # rate: **
    # tol: ***
 
THis indicates a *risk* based approach to a release - if a reviewer
has allowed this to go (and we can check it) we know we have a level
of technical debt and a level of risk in the release.



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

{x} Create a Milestone approach as wella s todo
{ } how to integrate with some ticket tracker?
{ } how to show in webbroswer in docker


"""

# rate: **
# life: prototype
# TODO: build basic walk and parse and report features

import os
import re
import logging

VALID_SUFFIX = [".py", ".rst", ".txt"]
### config
confd = {"todoinator.priorityregex": "\{\d+\}"}


class TODO(object):
    """
    """

    def __init__(self, isDone, todotxt, linenum, filepath):
        """
        """
        self.isDone = isDone

        self.todotxt = todotxt
        self.txt = self.todotxt

        self.linenum = linenum
        self.line = self.linenum

        self.filepath = filepath
        # [ ] Need to think of something re: priority
        self.priority = 1
        try:
            absfilepath = os.path.abspath(filepath)
            bits = absfilepath.split("/")
            idx = bits.index("projects")  # assume thats there
            self.reponame = bits[idx + 1]
        except ValueError:  # cant find projects in path
            self.reponame = "?"

    def __repr__(self):
        return "[{}] {}".format("x" if self.isDone else " ", self.todotxt)


def keep_file(filepath):
    """Decide if we keep the filepath, solely by exlcusion of end of path

    This is primarily to avoid keeping .pyc files

    >>> keep_file('/foo.pyc')
    False

    """
    ignoredpathendings = [".pyc"]
    for ending in ignoredpathendings:
        if filepath.endswith(ending):
            return False
    return True


def walk_tree(rootpath):
    """
    """
    ignoredirs = [".git"]

    for dirpath, dirs, files in os.walk(rootpath):
        # change dirs to remove unwanted dirs to descend into
        # rememer we need to use .remove as dirs seems to just point at
        # underlying implementation, so substitution has no effect
        for d in ignoredirs:
            if d in dirs:
                dirs.remove(d)

        files = list(filter(keep_file, files))
        for file in files:
            thisfile = os.path.join(dirpath, file)
            yield thisfile


def linenumber_lookup(linenumbers, filepos):
    """
    >>> linenumbers = [0, 4, 7, 9]
    >>> linenumber_lookup(linenumbers, 3)
    1
    >>> linenumber_lookup(linenumbers, 8)
    3
    >>> linenumber_lookup(linenumbers, 33)
    -1

    """
    #    print("looking up", linenumbers, filepos)
    foundlinenumber = -1
    for idx, linestartpos in enumerate(linenumbers):
        # [ ] handle last idx pos better here
        try:
            if filepos >= linestartpos and filepos <= linenumbers[idx + 1]:
                foundlinenumber = idx + 1
        except IndexError as e:
            if filepos <= linestartpos:
                foundlinenumber = idx
            else:
                foundlinenumber = -1

    return foundlinenumber


def linenumber_creator(txt):
    """
    >>> txt = '''This
    ... is
    ... a
    ... file'''
    >>> linenumber_creator(txt)
    [0, 4, 7, 9]

    >>> linenumber_creator('')
    []

    """
    linenumbers = []
    for idx, val in enumerate(txt):
        if val == "\n":
            linenumbers.append(idx)
    if linenumbers and linenumbers[0] != 0:
        linenumbers.insert(0, 0)
    return linenumbers


def base_file_parse(txt, filepath, regex, isMileStone=False):
    """
    """
    if isMileStone:
        DONETOKEN = "{x}"
        RHS = "}"
    else:
        DONETOKEN = "[x]"
        RHS = "]"
    todos = []
    linenumbers = linenumber_creator(txt)

    # StartLine:ZeroMoreSpaces:ZeroMoreHash:ZeroMoreSpaces:box
    REGEX = regex
    flag = re.MULTILINE | re.IGNORECASE | re.UNICODE
    pattern = re.compile(REGEX, flags=flag)

    # matchiter = re.finditer(REGEX, txt, flags=flag)
    matchiter = pattern.finditer(txt)
    for match in matchiter:
        goodline = match.groups()[0]  # we wont match twice on same line??
        done = False
        if DONETOKEN in goodline.lower():
            done = True
        todo_txt = goodline.split(RHS)[1].strip()
        _start = match.start()
        linenum = linenumber_lookup(linenumbers, _start)
        todos.append(TODO(done, todo_txt, linenum, filepath))
    return todos


def parse_file_miles(txt, filepath):
    """ Extract milestone lines from a file

    A Milestone is just like a Todo, but at a higher abstraction level 
    (there can be many todos to any single milestone)

    >>> testfile = '''
    ... [ ] A todo item
    ... [x] a done item
    ... #[x] done
    ... # not a todo!!! [ ]
    ... { } A MileStone
    ... {x} Completed Milestone
    ... bad'''
    >>> todos = parse_file_miles(testfile, '/tmp/todo.txt')
    >>> for todo in todos:
    ...     print(todo.isDone, todo.linenum)
    False 5
    True 6

    """
    regex = """^\s*\#*\s*(\{[\s|x]\}.*)"""
    return base_file_parse(txt, filepath, regex, isMileStone=True)


def parse_file_todos(txt, filepath):
    """Extract todo lines from a file

    Rules

    Item must be the first non-whitespace in a document
    whitespace can include comment markers 
    so ::

        [ ] a todo
        # [ ] another todo

    both work
    A todo marker can be ::

        [ ] 
        [X] 

    >>> parse_file_todos("#[ ] foo\\n foo", 'todo.txt')
    [[ ] foo]

    >>> testfile = '''
    ... [ ] A todo item
    ... [ ] A todo item 2
    ... [x] a done item
    ... #[x] done
    ...  # [ ] todo
    ... # not a todo!!! [ ]
    ... { } A MileStone'''
    >>> todos = parse_file_todos(testfile, '/tmp/todo.txt')
    >>> for todo in todos:
    ...     print(todo.isDone, todo.linenum)
    False 1
    False 2
    True 3
    True 4
    False 5
    


    """
    regex = """^\s*\#*\s*(\[[\s|x]\].*)"""
    return base_file_parse(txt, filepath, regex, isMileStone=False)


def parse_line(todoline):
    """extract data from a todo line
    
    >>> parse_line(" some note unadorned")
    (' some note unadorned', 30)
    >>> parse_line(" some note {88}")
    (' some note ', 88)
    >>> parse_line(" some note with non ascii ¥µ {88}")
    (' some note with non ascii ¥µ ', 88)

    
    """
    rgx = re.compile(confd["todoinator.priorityregex"])
    vals = rgx.findall(todoline)  # returns [] or ['{4}']
    if vals:
        token = sorted(vals)[-1]
        priority = int(token.replace("{", "").replace("}", ""))
    else:
        token = ""
        priority = 30
    return todoline.replace(token, ""), priority


def parse_tree(rootpath):
    """

    >>> import shutil, os
    >>> rootpath = '/tmp/todoinatortest'
    >>> tgtfile = rootpath + '/foo.txt'
    >>> shutil.rmtree(rootpath, True)
    >>> os.makedirs(rootpath)
    >>> txt = '''Hello
    ... [ ] Correct Todo item
    ... [x] DOne this
    ... { } Milestone item
    ... THis is just a line'''
    >>> print(len(txt))
    80
    >>> open(tgtfile, 'w').write(txt)
    80
    >>> parse_tree(rootpath)
    TODO
    Correct Todo item [/tmp/todoinatortest/foo.txt (2)]
    DOne this [/tmp/todoinatortest/foo.txt (3)]
    <BLANKLINE>
    Milestones
    Milestone item [/tmp/todoinatortest/foo.txt (4)]
    <BLANKLINE>

    """
    all_todos = []
    all_miles = []
    textfrag = "TODO\n"
    htmlfrag = "<table>"
    miles_text_frag = 'Milestones\n'
    miles_html_frag = '<table>'
    
    for filepath in walk_tree(rootpath):
        # test if suffix valid (ie dont parse pyc or wheel)
        suffix = os.path.splitext(filepath)[1]
        if suffix not in VALID_SUFFIX:
            continue
        try:
            # assume all files are utf-8???
            todo_list = parse_file_todos(
                open(filepath, encoding="utf-8").read(), filepath
            )
            milestone_list = parse_file_miles(
                open(filepath, encoding="utf-8").read(), filepath
            )
            todos = sorted(todo_list, key=lambda t: t.filepath)
            miles = sorted(milestone_list, key=lambda t: t.filepath)
        except IOError:
            todos = []
            miles = []
        except UnicodeDecodeError as e:
            logging.error("could not read %s - unicode err", filepath)
        if todos:
            all_todos.extend(todos)
        if miles:
            all_miles.extend(miles)
            
    all_todos = sorted(all_todos, key=lambda t: t.priority, reverse=True)
    all_miles = sorted(all_miles, key=lambda t: t.priority, reverse=True)
    for todo in all_todos:
        textfrag += "{0} [{1} ({2})]\n".format(todo.txt, todo.filepath, todo.linenum)
        htmlfrag += "<tr><td>%s</td> <td>%s</td> <td>%s</td> </tr>\n" % (
            todo.txt,
            todo.filepath,
            todo.linenum,
        )
    htmlfrag += "</table>"

    for mile in all_miles:
        miles_text_frag += "{0} [{1} ({2})]\n".format(mile.txt,
                                                      mile.filepath,
                                                      mile.linenum)
        miles_html_frag += "<tr><td>%s</td> <td>%s</td> <td>%s</td> </tr>\n" % (
            mile.txt,
            mile.filepath,
            mile.linenum,
        )
    htmlfrag += "</table>"
    #######################
    path = "/tmp/todo.html"
    open(path, "w").write(htmlfrag)
    # import webbrowser
    # webbrowser.open(path)
    print(textfrag)
    print(miles_text_frag)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=False)
