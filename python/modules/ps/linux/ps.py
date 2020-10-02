#!/usr/bin/env python3

import subprocess
import re

def get_ps():
    alert_data = {}
    cmd="ps -ef"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    exit_code = p.wait()
    if (exit_code != 0):
        print('Error: ' + str(err) + ' ' + str(output))
        return exit_code

    multilines = output.splitlines()

    odict = {}
    count = 0
    for line in multilines:
       count += 1
       line = line.decode('utf-8')
       #print(str(count) + ': ' + str(line))
       odict[count] = line


    number_of_procs = len(odict)
    number_of_defunct = 0
    for num in odict:
        line = odict[num]

        if re.search(r'<defunct>', line):
            number_of_defunct += 1
            alert_data[number_of_defunct] = str(line)

    #alert_data[1] = '503 19591 19580   0  6:57PM ttys010    0:00.00 defunct'

    #import sys
    #print('sys.exit')
    #sys.exit(1)

    Dct = {}

    Dct['procs'] = number_of_procs
    Dct['defunct'] = number_of_defunct

    Dct.update(alert_data)

    #json_data = '{"ps":"%s","val":"%s"}' % ('ps', ps_num_procs)

    #import json
    #return json.loads(json_data), alert_data
    #print(str(type(json_data)))
    #print(str(type(data)))
    #return json_data
    return Dct

if __name__ == '__main__':

    run = get_ps()
    print(run)

#>>> import sys
#>>> sys.path.append('/ufs/guido/lib/python')

