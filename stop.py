#!/usr/bin/python3
import sys, time, os

def stoprouter(routername):
  #print(routername)
  os.system("docker stop -t 0 %s" % routername)

if len(sys.argv) == 1:
  print("Usage:", sys.argv[0], "<simulation>")
  sys.exit()

sim = sys.argv[1]
sys.path.append(sim)
from settings import *

print("Stopping routers:")
print

n = 0
for i in asats:
  n = n + 1
  stoprouter(asatnames[n])

n = 0
for i in bsats:
  n = n + 1
  stoprouter(bsatnames[n])

n = 0
for i in csats:
  n = n + 1
  stoprouter(csatnames[n])


