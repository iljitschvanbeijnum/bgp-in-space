#!/usr/bin/python3
import math, sys

earth = 6371

if len(sys.argv) == 1:
  print("Usage:", sys.argv[0], "<range>")
  sys.exit()

range = int(sys.argv[1])
min = math.sqrt(math.pow(earth + 100, 2) + math.pow(range / 2, 2)) - earth
print("Minimum orbital height: %d km" % min)
period1 = 2 * math.pi * math.sqrt(pow((earth + min) * 1000, 3) / (3.986 * pow(10, 14)))
print("Orbital period at %4d km: %3d minutes" % (min, period1 / 60))

