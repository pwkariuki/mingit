#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 15:47:43 2025

@author: patrickkariuki
"""
# To parse command-line arguments
import argparse
# To read configuration files
import configparser
# For date/time manipulation
from datetime import datetime
# To read the users/group database on Unix
import grp, pwd
# To match filenames against patterns e.g. '.gitignore'
from fnmatch import fnmatch
# For hash functions
import hashlib
# Ceiling function from math library
from math import ceil
# For filesystem abstraction routines
import os
# For regex
import re
# To access actual command-line arguments
import sys
# Git compresses everything using zlib
import zlib

argparser = argparse.ArgumentParser(description="The stupidest content tracker")
argsubparser = argparser.add_subparsers(title="Commands", dest="command")
argsubparser.required = True

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        # case "add"          : cmd_add(args)
        # case "cat-file"     : cmd_cat_file(args)
        # case "check-ignore" : cmd_check_ignore(args)
        # case "checkout"     : cmd_checkout(args)
        # case "commit"       : cmd_commit(args)
        # case "hash-object"  : cmd_hash_object(args)
        # case "init"         : cmd_init(args)
        # case "log"          : cmd_log(args)
        # case "ls-files"     : cmd_ls_files(args)
        # case "ls-tree"      : cmd_ls_tree(args)
        # case "rev-parse"    : cmd_rev_parse(args)
        # case "rm"           : cmd_rm(args)
        # case "show-ref"     : cmd_show_ref(args)
        # case "status"       : cmd_status(args)
        # case "tag"          : cmd_tag(args)
        case _                : print("Bad command.")
