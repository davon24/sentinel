#!/usr/bin/env python3

import mmap

filepath="/tmp/file"

#create file object using open function call
file_object= open(filepath,mode="r+",encoding="utf8")
print("Initial data in the file is:")
print(file_object.read())

#create an mmap object using mmap function call
mmap_object= mmap.mmap(file_object.fileno(),length=0,access=mmap.ACCESS_WRITE,offset=0 )

#write something into file
text="Rink is writing this text to file  "
mmap_object.write(bytes(text,encoding="utf8"))

# read data from file
nfile_object= open(filepath,mode="r+",encoding="utf8")

print("Modified data from file is:")
print(nfile_object.read())



