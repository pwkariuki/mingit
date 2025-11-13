#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 15:47:43 2025

@author: patrickkariuki
"""
# To parse command-line arguments
import argparse
# For date/time manipulation
from datetime import datetime
# To read the users/group database on Unix
import grp, pwd
# To match filenames against patterns e.g. '.gitignore'
from fnmatch import fnmatch
# Ceiling function from math library
from math import ceil
# For regex
import re
# To access actual command-line arguments
import sys

from git_repo import repo_create, repo_find
from git_object import object_read, object_find, object_hash

argparser = argparse.ArgumentParser(description="The stupidest content tracker")
argsubparser = argparser.add_subparsers(title="Commands", dest="command")
argsubparser.required = True

# init command: wyag init [path]
argsp = argsubparser.add_parser("init", help="Initialize a new, empty repository.")

argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")

def cmd_init(args):
    repo_create(args.path)

# cat-file command: wyag cat-file type object
argsp = argsubparser.add_parser("cat-file",
                                help="Provide content of repository objects")

argsp.add_argument("type",
                   metavar="type",
                   choices=["blob", "commit", "tag", "tree"],
                   help="Specify the type")

argsp.add_argument("object",
                   metavar="object",
                   help="The object to display")

def cmd_cat_file(args):
    repo = repo_find()
    cat_file(repo, args.object, fmt=args.type.encode())

def cat_file(repo, obj, fmt=None):
    obj = object_read(repo, object_find(repo, obj, fmt=fmt))
    sys.stdout.buffer.write(obj.serialize())

# hash-object command: wyag hash-object [-w] [-t type] file
argsp = argsubparser.add_parser("hash-object",
            help="Compute object ID and optionally creata a blob from a file")

argsp.add_argument("-t",
                   metavar="type",
                   dest="type",
                   choices=["blob", "commit", "tag", "tree"],
                   default="blob",
                   help="Specify the type")

argsp.add_argument("-w",
                   dest="write",
                   action="store_true",
                   help="Actually write the object into the database")

argsp.add_argument("path",
                   help="Read object from <file>")

def cmd_hash_object(args):
    if args.write:
        repo = repo_find()
    else:
        repo = None

    with open(args.path, "rb") as f:
        sha = object_hash(fd, args.type.encode(), repo)
        print(sha)

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        # case "add"          : cmd_add(args)
        case "cat-file"     : cmd_cat_file(args)
        # case "check-ignore" : cmd_check_ignore(args)
        # case "checkout"     : cmd_checkout(args)
        # case "commit"       : cmd_commit(args)
        case "hash-object"  : cmd_hash_object(args)
        case "init"         : cmd_init(args)
        # case "log"          : cmd_log(args)
        # case "ls-files"     : cmd_ls_files(args)
        # case "ls-tree"      : cmd_ls_tree(args)
        # case "rev-parse"    : cmd_rev_parse(args)
        # case "rm"           : cmd_rm(args)
        # case "show-ref"     : cmd_show_ref(args)
        # case "status"       : cmd_status(args)
        # case "tag"          : cmd_tag(args)
        case _              : print("Bad command.")
