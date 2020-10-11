#!/usr/bin/env python3

from multiprocessing import Process, Pipe
#from unprivileged import Unprivileged

import os

class Unprivileged:

  def __init__(self, unprivilegedProcessPipeEnd):
    self._unprivilegedProcessPipeEnd = unprivilegedProcessPipeEnd

  def operate(self):
    invokerUid = os.getuid()

    if invokerUid == 0:
      # started by root; TODO: drop to predefined standard user
      # os.setuid(standardUid)
      pass
    else:
      # started by a regular user through a setuid-binary
      os.setuid(invokerUid) # TODO: drop to predefined standard user (save invokerUid for future stuff)

    # os.setuid(0) # not permitted anymore, cannot become root again

    print("os.getuid(): " + str(os.getuid()))

    self._unprivilegedProcessPipeEnd.send("invoke privilegedFunction1")
    print(self._unprivilegedProcessPipeEnd.recv())
    self._unprivilegedProcessPipeEnd.send("invoke privilegedFunction2")
    print(self._unprivilegedProcessPipeEnd.recv())

    return


if __name__ == '__main__':
  privilegedProcessPipeEnd, unprivilegedProcessPipeEnd = Pipe()
  unprivilegedProcess = Process(target=Unprivileged(unprivilegedProcessPipeEnd).operate)
  unprivilegedProcess.start()

  print(privilegedProcessPipeEnd.recv())
  privilegedProcessPipeEnd.send("ok")
  print(privilegedProcessPipeEnd.recv())
  privilegedProcessPipeEnd.send("nok")

  privilegedProcessPipeEnd.close()
  unprivilegedProcessPipeEnd.close()
  unprivilegedProcess.join()

