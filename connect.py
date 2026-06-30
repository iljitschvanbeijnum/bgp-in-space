#!/usr/bin/python3
import sys, time, os

if len(sys.argv) == 1:
  print("Usage:", sys.argv[0], "<routername> [command] [args]")
  sys.exit()

if len(sys.argv) == 2:
  os.system("docker exec -it %s vtysh" % sys.argv[1])

if len(sys.argv) == 3:
  os.system("docker exec -it %s %s" % (sys.argv[1], sys.argv[2]))

if len(sys.argv) > 3:
  cmd = ""
  for i in range(2, len(sys.argv)):
    cmd = cmd + " " + sys.argv[i]
  os.system("docker exec -it %s vtysh -e\"%s\"" % (sys.argv[1], cmd))


