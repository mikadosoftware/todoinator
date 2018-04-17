#! -*- coding:utf-8 -*-

from docopt import docopt
from todoinator import todoinator

DOCOPT = """ todoinator

Usage:
    todoinator <rootpath>

Options:
    -h --help Show this
    -d --docs Show docs

"""

def run(args):
    
    todoinator.parse_tree(args['<rootpath>'])    


def main():
    args = docopt(DOCOPT)
    run(args)
