#!/bin/bash
export LD_LIBRARY_PATH=/usr/libexec/sentinel/runtime/lib
export PATH=/usr/libexec/sentinel/runtime/bin:/usr/bin:/usr/sbin:/bin:/sbin
/usr/libexec/sentinel/sentinel.py "$@"
