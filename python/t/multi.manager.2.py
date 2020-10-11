#!/usr/bin/env python3

import os, pwd, grp

from multiprocessing import Process, Manager

def f(d):
    d[1] += '1'
    d['2'] += 2

if __name__ == '__main__':
    manager = Manager()

    d = manager.dict()
    d[1] = '1'
    d['2'] = 2

    p1 = Process(target=f, args=(d,))
    p1.start()
    p1.join()

    run_as_user = "nobody"
    uid = pwd.getpwnam(run_as_user)[2]
    print('user.nobody ' + str(uid))
        
    run_as_group = "nobody"
    gid = grp.getgrnam(run_as_group)[2]
    print('group.nobody ' + str(gid))
 
    os.setuid(uid)
    #os.setgid(gid)


    p2 = Process(target=f, args=(d,))
    p2.start()
    p2.join()

    print(d)


