#!/usr/bin/env python3

import mmap
import contextlib

word = 'hello'
_reversed = word[::-1]
print('Looking for    :', word)
print('Replacing with :', _reversed)

with open('/tmp/file', 'r+') as f:
    with contextlib.closing(mmap.mmap(f.fileno(), 0)) as m:
        print('Before:' + str(m.readline().rstrip()))
        m.seek(0) # rewind

        loc = m.find(word)
        m[loc:loc+len(word)] = _reversed
        m.flush()

        m.seek(0) # rewind
        print('After :' + str(m.readline().rstrip()))


