#!/usr/bin/env python3

import sys
import subprocess
#import re

def get_ps():

    #if sys.platform == 'darwin':
    #    cmd='ps -A -o stat,uid,ppid,pid,user,etime,command'
    #if sys.platform == 'linux' or sys.platform == 'linux2':
    #    cmd='ps -ef'

    cmd='ps -A -o stat,uid,ppid,pid,user,etime,command'

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    exit_code = p.wait()
    if (exit_code != 0):
        print('Error: ' + str(err) + ' ' + str(output))
        return exit_code

    multilines = output.splitlines()
    defunct_data = {}
    odict = {}
    Dct = {}
    count = 0

    for line in multilines:
       count += 1
       line = line.decode('utf-8')
       odict[count] = line
       #print(str(count) + ': ' + str(line))

    number_of_procs = len(odict)
    number_of_defunct = 0

    for num in odict:
        line = odict[num]

        #linux
        #if re.search(r'<defunct>', line):
        #    number_of_defunct += 1
        #    defunct_data[number_of_defunct] = str(line)
        #defunct_data[1] = '503 19591 19580   0  6:57PM ttys010    0:00.00 defunct'

        #mac
        if line.startswith('Z'):
            number_of_defunct += 1
            #defunct_data[number_of_defunct] = str(line)
            _key = 'defunct' + str(number_of_defunct)
            defunct_data[_key] = str(line)

    Dct['procs'] = number_of_procs
    Dct['defunct'] = number_of_defunct
    Dct.update(defunct_data)
    return Dct

if __name__ == '__main__':

    run = get_ps()
    print(run)

#>>> import sys
#>>> sys.path.append('/ufs/guido/lib/python')

