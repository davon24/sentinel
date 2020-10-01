#!/usr/bin/env python3

import subprocess
import re

def get_ps():
    alert_data = {}
    collect="ps -ef"
    p = subprocess.Popen(collect, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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
       #print(str(count) + ': ' + line)
       odict[count] = line

    number_of_procs = len(odict)
    number_of_defunct = 0
    for num in odict:
        line = odict[num]

        if re.search(r'<defunct>', line):
            number_of_defunct += 1
            alert_data[number_of_defunct] = str(line)

    #alert_data[1] = '503 19591 19580   0  6:57PM ttys010    0:00.00 defunct'

    ps_rrdupdate = 'N:' + str(number_of_procs)
    ps_rrdupdate += ':' + str(number_of_defunct)
    json_data = '{"rrd":"%s","val":"%s"}' % ('ps', ps_rrdupdate)
    return json.loads(json_data), alert_data



if __name__ == '__main__':

    rrd_ps, alert_ps = get_ps()

#>>> import sys
#>>> sys.path.append('/ufs/guido/lib/python')

