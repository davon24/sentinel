#!/usr/bin/env python3

git_store = '/opt/sentinel/db/git'

import os

if not os.path.isdir(git_store):
    print('mkdir ' + str(db_store))
    os.mkdir(db_store, 0o755)


L = [ '/etc/hosts', '/etc/ssh/sshd_config' ]

for f in L:

    gfile = git_store + f

    if not os.path.isdir(os.path.dirname(gfile)):
        print('mkdir ' + str(os.path.dirname(gfile)))
        os.mkdir(os.path.dirname(gfile), 0o755)

    if not os.path.isfile(gfile):
        print('link ' + str(gfile))
        os.link(f, gfile)


# git + tegridy






