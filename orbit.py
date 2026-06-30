#!/usr/bin/python3
import sys, math, time, os, shutil

def distance(heighta, wherea, heightb, whereb):
  longa = wherea / 360 * math.pi * 2
  longb = whereb / 360 * math.pi * 2
  heighta = heighta + earth
  heightb = heightb + earth

  xa = math.sin(wherea / 360 * math.pi * 2) * (heighta)
  ya = math.cos(wherea / 360 * math.pi * 2) * (heighta)
  xb = math.sin(whereb / 360 * math.pi * 2) * (heightb)
  yb = math.cos(whereb / 360 * math.pi * 2) * (heightb)

  distance = math.hypot(xa - xb, ya - yb)
  return distance

if len(sys.argv) == 1:
  print("Usage:", sys.argv[0], "<simulation>")
  sys.exit()

sim = sys.argv[1]
sys.path.append(sim)
from settings import *

abmin = 1000
cbmin = 1000

red = "\033[31m"
green = "\033[32m"
yellow = "\033[33m"
resetcolor = "\033[39m"

b = 1
while b <= len(bsatnames):
  a = 1
  while a < len(asatnames):
    os.system("docker exec -it %s vtysh -e \"copy /etc/frr/down%d.conf running-config\" >/dev/null" % (asatnames[a], b))
    a = a + 1
  c = 1
  while c < len(csatnames):
    os.system("docker exec -it %s vtysh -e \"copy /etc/frr/down%d.conf running-config\" >/dev/null" % (csatnames[c], b))
    c = c + 1
  b = b + 1

print(clearscreen, end="")

ts1 = int(time.time())
ts2 = int(time.time())
s = 0
while s < simperiod * 3600:
  print(topscreen, end="")
  print("Distances at %2d:%02d:%02d" % (s / 3600, (s / 60) % 60, s % 60))
  print("")

  abinrange = 0
  cbinrange = 0

  an = 0
  for a in asats:
    an = an + 1
    bn = 0
    for b in bsats:
      bn = bn + 1
      awhere = ((s / aperiod * aretrograde * 360) + a) % 360
      bwhere = ((s / bperiod * bretrograde * 360) + b) % 360
      d = distance(aheight, awhere, bheight, bwhere)
      if d < range:
        print("%s - %s: %s %5d km " % (asatnames[an], bsatnames[bn], green, d) + ("━" * int(d / 500)) + resetcolor + clearrestofline)
        abinrange = abinrange + 1
        #print("A%d - B%d: bringing link up       %s %s " % (an, bn, asatnames[an], ainterfaces[bn]))
        if docker and aup[bn] == 0:
          os.system("docker exec -it %s ip link set %s up >/dev/null" % (asatnames[an], ainterfaces[bn]))
          os.system("docker exec -it %s vtysh -e \"copy /etc/frr/up%d.conf running-config\" >/dev/null" % (asatnames[an], bn))
          aup[bn] = 2
      else:
        #print("A%d - B%d: %5d km - out of range        " % (an, bn, d))
        #print("A%d - B%d: taking link down       %s %s" % (an, bn, asatnames[an], ainterfaces[bn]))
        if aup[bn]:
          if aup[bn] > 1:
            print("%s - %s: %s %5d km " % (asatnames[an], bsatnames[bn], yellow, d) + ("━" * int(d / 500)) + resetcolor + clearrestofline)
            if docker:
              os.system("docker exec -it %s vtysh -e \"copy /etc/frr/down%d.conf running-config\" >/dev/null" % (asatnames[an], bn))
            aup[bn] = aup[bn] - 1
          else:
            print("%s - %s: %s %5d km " % (asatnames[an], bsatnames[bn], red, d) + ("━" * int(d / 500)) + resetcolor + clearrestofline)
            if docker:
              os.system("docker exec -it %s ip link set %s down >/dev/null" % (asatnames[an], ainterfaces[bn]))
            aup[bn] = 0
        else:
          print("%s - %s: %s %5d km " % (asatnames[an], bsatnames[bn], red, d) + ("━" * int(d / 500)) + resetcolor + clearrestofline)
  #print("AB: %d in range        " % abinrange)
  #abmin = min(abmin, abinrange)

  print("")

  cn = 0
  for c in csats:
    cn = cn + 1
    bn = 0
    for b in bsats:
      bn = bn + 1
      cwhere = ((s / cperiod * cretrograde * 360) + c) % 360
      bwhere = ((s / bperiod * bretrograde * 360) + b) % 360
      d = distance(cheight, cwhere, bheight, bwhere)
      if d < range:
        #print("C%d - B%d: %5d km - in range        " % (cn, bn, d))
        print("%s - %s: %s %5d km " % (csatnames[cn], bsatnames[bn], green, d) + ("━" * int(d / 500)) + resetcolor + clearrestofline)
        cbinrange = cbinrange + 1
        #print("C%d - B%d: bringing link up       %s %s " % (cn, bn, csatnames[cn], cinterfaces[bn]))
        if docker and cup[bn] == 0:
          os.system("docker exec -it %s ip link set %s up >/dev/null" % (csatnames[cn], cinterfaces[bn]))
          os.system("docker exec -it %s vtysh -e \"copy /etc/frr/up%d.conf running-config\" >/dev/null" % (csatnames[cn], bn))
          cup[bn] = 2
      else:
        #print("C%d - B%d: %5d km - out of range        " % (cn, bn, d))
        print("%s - %s: %s %5d km " % (csatnames[cn], bsatnames[bn], red, d) + ("━" * int(d / 500)) + resetcolor + clearrestofline)
        #print("C%d - B%d: taking link down       %s %s" % (cn, bn, asatnames[cn], cinterfaces[bn]))
        if docker and cup[bn]:
          if cup[bn] > 1:
            os.system("docker exec -it %s vtysh -e \"copy /etc/frr/down%d.conf running-config\" >/dev/null" % (csatnames[cn], bn))
            cup[bn] = cup[bn] - 1
          else:
            os.system("docker exec -it %s ip link set %s down >/dev/null" % (csatnames[cn], cinterfaces[bn]))
            cup[bn] = 0

  print("")
  print("AB: %d in range        " % abinrange)
  print("CB: %d in range        " % cbinrange)
  abmin = min(abmin, abinrange)

  '''
  cn = 0
  for c in csats:
    cn = cn + 1
    bn = 0
    for b in bsats:
      bn = bn + 1
      cwhere = ((s / cperiod * 360) + c) % 360
      bwhere = ((s / bperiod * 360) + b) % 360
      d = distance(cheight, cwhere, bheight, bwhere)
      print("C%d - B%d: %5d km " % (cn, bn, d), end="")
      if d < range:
        #print("C%d - B%d: %5d km - in range        " % (cn, bn, d))
        i = 0
        while i < d:
          print("+", end = "")
          i = i + 1000
        cbinrange = cbinrange + 1
      else:
        #print("C%d - B%d: %5d km - out of range        " % (cn, bn, d))
        i = int(d / 1000)
        print(red, "━" * i, end = "")
      print(resetcolors + clearrestofline)
  print("CB: %d in range        " % cbinrange)
  cbmin = min(cbmin, cbinrange)
  '''

  print()
  # increase time (seconds):
  s = s + simsecs

  # delay until next iteration
  '''
  ts2 = time.time()
  sleeptime = max(0, realsecs + ts1 - ts2)
  print("sleep %f" % sleeptime)
  time.sleep(sleeptime)
  ts1 = ts2
  '''
  time.sleep(realsecs)

print("Minimum A - B in range: %d" % abmin)
#print("Minimum C - B in range: %d" % cbmin)
