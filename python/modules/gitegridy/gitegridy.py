#!/usr/bin/env python3


import os
from subprocess import Popen, PIPE

import sys

def gitStoreLink(git_store, List):

    if not os.path.isdir(git_store):
        print('mkdir ' + str(git_store))
        os.mkdir(git_store, 0o755)

    for f in List:

        gfile = git_store + f

        if not os.path.isdir(os.path.dirname(gfile)):
            print('mkdir ' + str(os.path.dirname(gfile)))
            os.mkdir(os.path.dirname(gfile), 0o755)

        if not os.path.isfile(gfile):
            print('link ' + str(gfile))
            os.link(f, gfile)

    return True

def gitStoreInit(git_store):
    #os.chdir(git_store)
    if not os.path.isdir(git_store + '/.git'):
        print('git init ' + str(git_store))
        cmd = 'git init ' + str(git_store)
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        #out = proc.stdout.readlines()

        for line in proc.stdout.readlines():
            #print(line)
            line = line.decode('utf-8').strip('\n')
            print(line)

    return True

def gitStoreAdd(git_store, f):
    os.chdir(git_store)
    print('git add ' + git_store + f)
    cmd = 'git add ' + git_store + f
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    for line in proc.stdout.readlines():
        print(line.decode('utf-8').strip('\n'))
    return True

def gitStoreCommit(git_store, f):
    os.chdir(git_store)
    print('git commit -m "commit" ' + git_store + f)
    cmd = 'git commit -m "commit" ' + git_store + f
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    for line in proc.stdout.readlines():
        print(line.decode('utf-8').strip('\n'))
    return True


def gitStoreStatus(git_store):
    os.chdir(git_store)
    cmd = 'git status'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    for line in proc.stdout.readlines():
        print(line.decode('utf-8').strip('\n'))
    return True


if __name__ == '__main__':

    git_store = '/opt/sentinel/db/git'
    L = [ '/etc/hosts', '/etc/ssh/sshd_config' ]

    git_init = gitStoreInit(git_store)
    git_link = gitStoreLink(git_store, L)

    #for f in L:
    #    git_add  = gitStoreAdd(git_store, f)
    #    git_commit = gitStoreCommit(git_store, f)


    if sys.argv[1:]:
        if sys.argv[1] == 'status':
            git_status = gitStoreStatus(git_store)


# git + tegridy


