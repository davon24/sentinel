#!/usr/bin/env python3

import mmap

filepath="/tmp/file"

#create file object using open function call
file_object= open(filepath,mode="r",encoding="utf8")

#create an mmap object using mmap function call
mmap_object= mmap.mmap(file_object.fileno(),length=0,access=mmap.ACCESS_READ,offset=0)

#read data from mmap object
txt=mmap_object.read()

#print the data
print("Data read from file in byte format is:")
print(txt)
print("Text data is:")
print(txt.decode())

