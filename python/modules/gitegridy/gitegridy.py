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
    if verbose: print('git commit ' + git_store + f)
    #cmd = 'git commit -m "sentinel ' + str(f) + '" ' + git_store + f
    #cmd = 'git commit -m "sentinel ' + str(f) + '" ' + git_store + f
    #cmd = 'git commit -m "sentinel ' + str(f) + '" ' + str(git_store + f)
    #cmd = 'git commit -m "sentinel" ' + git_store + f
    #print(str(cmd))
    #print(str(cmd.split(' ')))

    #import shlex
    #shlex.split(cmd)

    #proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)

    cmd = ['git', 'commit', '-m', '"sentinel ' + str(f) + '"', git_store + f ]
    #print(str(cmd))

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
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

def fileType__1(_file):
    file_data = open(_file, 'rb').read()

    import codecs
    header_3byte = codecs.encode(file_data[0:3], 'hex')

    print(str(header_3byte))

    if header_3byte == b'474946':
        return 'image/gif'
    elif header_3byte == b'89504e':
        return 'image/png'
    elif header_3byte == b'ffd8ff':
        return 'image/jpeg'
    elif header_3byte == b'cffaed':
        return 'mach-o/binary'
    elif header_3byte == b'cafeba':
        return 'mach-o/u-binary'
    elif header_3byte == b'7f454c':
        return 'elf/binary'
    elif header_3byte == b'23212f':
        return 'text/plain'
    elif header_3byte == b'2d2d2d':
        return 'text/plain'
    else:
        return 'unknown/file'



def gitStoreDiff(git_store, f=None, verbose=False):
    os.chdir(git_store)

    if f is None:
        f = ''

    cmd = 'git diff ' + f

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    if verbose:
        for line in proc.stdout.readlines():
            print(line.decode('utf-8').strip('\n'))
    return proc.stdout.readlines()


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

