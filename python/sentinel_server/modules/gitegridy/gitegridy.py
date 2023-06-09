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

    if not os.path.isdir(git_store):
        if verbose: print('mkdir ' + str(git_store))
        os.mkdir(git_store, 0o755)

    if not os.path.isdir(git_store + '/.git'):
        if verbose: print('git init ' + str(git_store))
        cmd = 'git init ' + str(git_store)
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        if verbose:
            for line in proc.stdout.readlines():
                print(line.decode('utf-8').strip('\n'))
    #os.chdir(git_store)
    return True

def gitStoreAdd(git_store, f, verbose=False):
    try:
        os.chdir(git_store)
    except FileNotFoundError as e:
        if verbose: print('FileNotFoundError: ' + str(e))
        return 'FileNotFoundError: ' + str(e)

    if not os.access(f, os.F_OK):
        if verbose: print('Not Found: ' + str(f))
        return 'Not Found: ' + str(f)
    elif not os.access(f, os.R_OK):
        if verbose: print('No Access: ' + str(f))
        return 'No Access: ' + str(f)

    cmd = 'git add ' + git_store + f
    if verbose: print('git add ' + git_store + f)

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    if verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))
        print(str(exit_code))

    return stdout, stderr, exit_code

def gitStoreDel(git_store, f, verbose=False):
    os.chdir(git_store)
    if verbose: print('git rm ' + git_store + f)
    cmd = 'git rm -f ' + git_store + f
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))

    if os.path.exists(git_store + f):
        if verbose: print('remove ' + git_store + f)
        os.remove(git_store + f)

    git_commit = gitStoreCommit(git_store, f, verbose=True)

    return True
    

def gitStoreCommit(git_store, f, verbose=False):
    os.chdir(git_store)
    if verbose: print('git commit me ' + git_store + f)
    #import shlex
    #shlex.split(cmd)
    #cmd = 'git commit -m "sentinel" ' + git_store + f
    #proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)

    cmd = ['git', 'commit', '-m', '"sentinel ' + str(f) + '"', git_store + f ]

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    if verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))
        print(str(exit_code))

    return stdout, stderr, exit_code

def gitStoreStatus(git_store, verbose=False):
    try:
        os.chdir(git_store)
    except FileNotFoundError as e:
        if verbose: print('FileNotFoundError: ' + str(e))
        return 'FileNotFoundError: ' + str(e)

    cmd = 'git status'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    if verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))
        print(str(exit_code))

    return stdout, stderr, exit_code


def gitStoreLsFiles(git_store, verbose=False):
    try:
        os.chdir(git_store)
    except FileNotFoundError as e:
        if verbose: print('FileNotFoundError: ' + str(e))
        return 'FileNotFoundError: ' + str(e)

    cmd = 'git ls-files'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    if verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))
        print(str(exit_code))

    return stdout, stderr, exit_code


def gitStoreLog(git_store, verbose=False):
    try:
        os.chdir(git_store)
    except FileNotFoundError as e:
        if verbose: print('FileNotFoundError: ' + str(e))
        return 'FileNotFoundError: ' + str(e)

    cmd = 'git log'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))
    return proc.stdout.readlines()

def gitStoreClearHistory(git_store, verbose=False):
    os.chdir(git_store)

    cmd = 'git checkout --orphan temp_branch'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))

    cmd = 'git add -A'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))

    cmd = ['git','commit','-am "sentinel re-commit"']
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))

    cmd = 'git branch -D master'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))

    cmd = 'git branch -m master'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))

    #cmd = 'git push -f origin master'
    #proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    #if verbose:
    #    for line in proc.stdout.readlines():
    #        print(line.decode('utf-8').strip('\n'))

    return True

#import mimetypes
#mime = mimetypes.guess_type(file)

def fileType(_file):
    try:
        with open(_file, 'r', encoding='utf-8') as f:
            f.read(4)
            return 'text'
    except UnicodeDecodeError:
        return 'binary'


def gitStoreDiff(git_store, f=None, verbose=False):
    try:
        os.chdir(git_store)
    except FileNotFoundError as e:
        if verbose: print('FileNotFoundError: ' + str(e))
        return 'FileNotFoundError: ' + str(e)

    if f is None:
        f = ''

    cmd = 'git diff ' + f

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    if verbose:
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))
        print(str(exit_code))

    return stdout, stderr, exit_code



if __name__ == '__main__':

    git_store = '/opt/sentinel/db/git/dir2'
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

        if sys.argv[1] == 'git-del':
            _file = sys.argv[2]
            git_del = gitStoreDel(git_store, _file, verbose=True)

        if sys.argv[1] == 'git-commit':
            _file = sys.argv[2]

            if not os.access(_file, os.F_OK):
                print('Not Found: ' + str(_file))
                sys.exit(1)
            elif not os.access(_file, os.R_OK):
                print('No Access: ' + str(_file))
                sys.exit(1)

            git_commit = gitStoreCommit(git_store, _file, verbose=True)


        if sys.argv[1] == 'git-clear-history':
            git_clear_hist = gitStoreClearHistory(git_store, verbose=True)

        if sys.argv[1] == 'git-diff':
            try: _file = sys.argv[2]
            except IndexError: _file = None
            git_diff = gitStoreDiff(git_store, _file, verbose=True)

        if sys.argv[1] == 'git-init':
            git_init = gitStoreInit(git_store)

        if sys.argv[1] == 'file-type':
            _file = sys.argv[2]
            file_type = fileType(_file)
            print(file_type)



# git + tegridy

