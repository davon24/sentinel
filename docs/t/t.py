#!/usr/bin/env python3


import multiprocessing
manager = multiprocessing.Manager()
shared_dict = manager.dict()

def worker1(d):
    d["a"] = 1

def worker2(d):
    d["b"] = 2

process1 = multiprocessing.Process(
    target=worker1, args=[shared_dict])
process2 = multiprocessing.Process(
    target=worker2, args=[shared_dict])

process1.start()
process2.start()
process1.join()
process2.join()

print(shared_dict)


