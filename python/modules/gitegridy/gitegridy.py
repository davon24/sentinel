#!/usr/bin/env python3


import os
from subprocess import Popen, PIPE


def setupGitStore(git_store, List):

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


    os.chdir(git_store)

    if not os.path.isdir(git_store + '/.git'):
        print('git init .')
        cmd = 'git init .'
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        #out = proc.stdout.readlines()

        for line in proc.stdout.readlines():
            #print(line)
            line = line.decode('utf-8').strip('\n')
            print(line)

    return True




if __name__ == '__main__':

    git_store = '/opt/sentinel/db/git'
    L = [ '/etc/hosts', '/etc/ssh/sshd_config' ]

    setup = setupGitStore(git_store, L)





# git + tegridy






