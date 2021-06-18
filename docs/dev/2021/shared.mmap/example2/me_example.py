#!/usr/bin/env python3

import os
import mmap

def memory_map(filename,access = mmap.ACCESS_WRITE):
    size = os.path.getsize(filename)
    # the os.open() method returns a file descriptor for the newly opened file
    file_descriptor = os.open(filename,os.O_RDWR)
    return mmap.mmap(file_descriptor,size,access = access)




