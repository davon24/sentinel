#!/bin/bash
LD_LIBRARY_PATH=/usr/libexec/sentinel/runtime/lib
PATH=/usr/libexec/sentinel/runtime/bin:/usr/bin:/usr/sbin:/bin:/sbin
/usr/libexec/sentinel/sentinel.py $@
