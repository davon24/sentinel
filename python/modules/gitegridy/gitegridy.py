#!/usr/bin/env python3


import os
from subprocess import Popen, PIPE

import sys

def gitStoreLink(git_store, List, verbose=False):

    if not os.path.isdir(git_store):
        if verbose: print('mkdir ' + str(git_store))
        os.mkdir(git_store, 0o755)

    for f in List:

        gfile = git_store + f

        if not os.path.isdir(os.path.dirname(gfile)):
            if verbose: print('mkdir ' + str(os.path.dirname(gfile)))
            os.mkdir(os.path.dirname(gfile), 0o755)

        if not os.path.isfile(gfile):
            if verbose: print('link ' + str(gfile))
            os.link(f, gfile)

    return True

def gitStoreInit(git_store, verbose=False):
    os.chdir(git_store)
    if not os.path.isdir(git_store + '/.git'):
        if verbose: print('git init ' + str(git_store))
        cmd = 'git init ' + str(git_store)
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        if verbose:
            for line in proc.stdout.readlines():
                print(line.decode('utf-8').strip('\n'))
    return True

def gitStoreAdd(git_store, f, verbose=False):
    os.chdir(git_store)
    if verbose: print('git add ' + git_store + f)
    cmd = 'git add ' + git_store + f
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))
    return proc.stdout.readlines()

def gitStoreCommit(git_store, f, verbose=False):
    os.chdir(git_store)
    if verbose: print('git commit -m "sentinel" ' + git_store + f)
    cmd = 'git commit -m "commit" ' + git_store + f
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))
    return proc.stdout.readlines()


def gitStoreStatus(git_store, verbose=False):
    os.chdir(git_store)
    cmd = 'git status'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))
    return proc.stdout.readlines()

def gitStoreLsFiles(git_store, verbose=False):
    os.chdir(git_store)
    cmd = 'git ls-files'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))
    return proc.stdout.readlines()

def gitStoreLog(git_store, verbose=False):
    os.chdir(git_store)
    cmd = 'git log'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))
    return proc.stdout.readlines()


if __name__ == '__main__':

    git_store = '/opt/sentinel/db/git'
    L = [ '/etc/hosts', '/etc/ssh/sshd_config' ]

    git_init = gitStoreInit(git_store)
    git_link = gitStoreLink(git_store, L)

    #for f in L:
    #    git_add  = gitStoreAdd(git_store, f)
    #    git_commit = gitStoreCommit(git_store, f)


    if sys.argv[1:]:

        if sys.argv[1] == 'git-status':
            git_status = gitStoreStatus(git_store, verbose=True)

        if sys.argv[1] == 'git-files':
            git_files = gitStoreLsFiles(git_store, verbose=True)

        if sys.argv[1] == 'git-log':
            git_log = gitStoreLog(git_store, verbose=True)

        if sys.argv[1] == 'git-add':
            _file = sys.argv[2]

            if not os.access(_file, os.F_OK):
                print('Not Found: ' + str(_file))
                sys.exit(1)
            elif not os.access(_file, os.R_OK):
                print('No Access: ' + str(_file))
                sys.exit(1)

            git_link = gitStoreLink(git_store, [_file], verbose=True)
            git_add  = gitStoreAdd(git_store, _file, verbose=True)
            git_commit = gitStoreCommit(git_store, _file, verbose=True)



# git + tegridy


