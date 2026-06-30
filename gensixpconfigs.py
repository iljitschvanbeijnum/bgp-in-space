#!/usr/bin/python3
import sys, os, shutil

if len(sys.argv) != 5:
  print("Usage:", sys.argv[0], "<sim> <sixps> <constellations> <satellites>")
  sys.exit()
  
print("Generating constellation config files:")
print
    
sim = sys.argv[1]
sixps = int(sys.argv[2]) 
cons = int(sys.argv[3])
satellites = int(sys.argv[4])

acsats = ""
acsatnums = ""
acsatnames = ""
acinterfaces = ""
acup = ""

for sixp in range(1, sixps + 1):
  print("SIXP%02d" % sixp)

  acsats = acsats + "%d, " % int(360 / sixps * (sixp - 0.5))
  acsatnums = acsatnums + "%d, " % sixp
  acsatnames = acsatnames + "\"SIXP%02d\", " % sixp

  dir = "%s/SIXP%02d" % (sim, sixp)
  if not os.path.exists(dir):
    os.makedirs(dir)
  shutil.copyfile("daemons", dir + "/daemons")

  # vlans.sh
  file = open(dir + "/vlans.sh", "w")
  file.write("#!/bin/sh\n")
  vlans = "vlans=\"192 203"
  for i in range(1, sixps + 1):
    for j in range(1, satellites + 1):
      for k in range(1, cons + 1):
        vlans = vlans + " %d" % (i * 256 + k * 16 + j)
  vlans = vlans + "\"\n"
  file.write(vlans)
  file.write("# set up VLANs\n")
  file.write("for vlanid in $vlans\n")
  file.write("  do\n")
  file.write("    ip link add link eth0 name eth0.$vlanid type vlan id $vlanid\n")
  file.write("  done\n")
  file.close()

  # vtysh.conf
  file = open(dir + "/vtysh.conf", "w")
  file.write("!\n")
  file.write("hostname SIXP%02d\n" % sixp)
  file.write("!\n")
  file.write("terminal paginate\n")
  file.write("!\n")
  file.close()

  # zebra.conf
  file = open(dir + "/zebra.conf", "w")
  file.write("!\n")
  file.write("interface eth0.19\n")
  file.write(" ip address 192.0.2.%d/24\n" % sixp)
  file.write("!\n")
  file.write("interface eth0.20\n")
  file.write(" ip address 203.0.113.1%d/24\n" % sixp)
  file.write("!\n")
  #for i in range(1, sixps + 1):
  for j in range(1, satellites + 1):
    for k in range(1, cons + 1):
      acinterfaces = acinterfaces + "\"eth0.%d\", " % (sixp * 256 + k * 16 + j)
      file.write("interface eth0.%d\n" % (sixp * 256 + k * 16 + j))
      file.write(" ip address 10.%d.%d.254/24\n" % (sixp, k * 16 + j))
      file.write("!\n")
  file.close()

  # staticd.conf
  file = open(dir + "/staticd.conf", "w")
  file.write("!\n")
  for i in range(150, 250):
    file.write("ip route 10.%d.%d.0/24 null0\n" % (sixp, i))
  file.write("!\n")
  file.close()

  # bfdd.conf
  file = open(dir + "/bfdd.conf", "w")
  file.write("!\n")
  file.write("bfd\n")
  file.write(" profile 100ms\n")
  file.write("  detect-multiplier 4\n")
  file.write("  transmit-interval 25\n")
  file.write("  receive-interval 25\n")
  file.write(" exit\n")
  file.write(" !\n")
  file.write("!\n")
  file.close()

  # bgpd.conf
  file = open(dir + "/bgpd.conf", "w")
  file.write("!\n")
  file.write("router bgp %d\n" % (64900 + sixp))
  file.write(" no bgp ebgp-requires-policy\n")
  for i in range(0, 100):
    file.write(" network 10.%d.%d.0/24\n" % (sixp, i))
  '''
  # links between neighboring SIXPs
  if (sixp > 1):
    file.write(" neighbor 192.0.2.%d description Link to previous SIXP\n" % (sixp - 1))
    file.write(" neighbor 192.0.2.%d remote-as %d\n" % (sixp - 1, 64899 + sixp))
    file.write(" neighbor 192.0.2.%d next-hop-self\n" % (sixp - 1))
  else:
    file.write(" neighbor 192.0.2.%d description Link to previous SIXP\n" % sixps))
    file.write(" neighbor 192.0.2.%d remote-as %d\n" % (int(sys.argv[1]), 64900 + sixps))
    file.write(" neighbor 192.0.2.%d next-hop-self\n" % sixps)
  if (sixp < sixps):
    file.write(" neighbor 192.0.2.%d description Link to next SIXP\n" % (sixp + 1))
    file.write(" neighbor 192.0.2.%d remote-as %d\n" % (sixp + 1, 64901 + sixp))
    file.write(" neighbor 192.0.2.%d next-hop-self\n" % (sixp + 1))
  else:
    file.write(" neighbor 192.0.2.%d description Link to next SIXP\n" % 1)
    file.write(" neighbor 192.0.2.%d remote-as %d\n" % (1, 64901))
    file.write(" neighbor 192.0.2.%d next-hop-self\n" % 1)
  '''
  # eBGP to customer constellations
  for j in range(1, satellites + 1):
    for k in range(1, cons + 1):
      file.write(" neighbor 10.%d.%d.%d remote-as %d\n" % (sixp, k * 16 + j, j, 65000 + k))
      file.write(" neighbor 10.%d.%d.%d bfd profile 100ms\n" % (sixp, k * 16 + j, j))
  file.write("!\n")
  file.write("route-map nexthop permit 10\n")
  file.write(" set ip next-hop 172.20.0.%d\n" % sixp)
  file.write("!\n")
  file.close()

# settings.py
ac = "b"
file = open(sim + "/settings.py", "a")

file.write("#!/usr/bin/python3\n")
file.write("import sys, math\n")
file.write("\n")
file.write("# how long to run in simulated time (hours):\n")
file.write("simperiod = 72\n")
file.write("# number of seconds to advance simulated time:\n")
file.write("simsecs = 432\n")
file.write("# number of seconds real time to wait between iterations:\n")
file.write("realsecs = 0.05\n")
file.write("# talk to docker containers (0 = no, 1 = yes):\n")
file.write("docker = 0\n")
file.write("# for retrograde, 1 is a regular prograde orbit, -1 means a retrograde orbit\n")
file.write("\n")
file.write("# with these codes in place, the screen will refresh in-place:\n")
file.write("clearscreen = \"\\033[2J\"\n")
file.write("topscreen = \"\\033[0;0H\"\n")
file.write("clearrestofline = \"\\033[0K\"\n")
file.write("\n")
file.write("# with these uncommented, the screen will scroll:\n")
file.write("#clearscreen = \"\"\n")
file.write("#topscreen = \"\"\n")
file.write("#clearrestofline = \"\"\n")
file.write("\n")
file.write("range = 4300\n")
file.write("earth = 6371\n")
file.write("\n")

file.write(ac + "height = 600\n")
file.write(ac + "sats = [ " + acsats[0:-2] + " ]\n")
file.write(ac + "satnums = [ \"\", " + acsatnums[0:-2] + " ]\n")
file.write(ac + "satnames = [ \"\", " + acsatnames[0:-2] + " ]\n")
file.write(ac + "interfaces = [ \"\", " + acinterfaces[0:-2] + " ]\n")
file.write(ac + "period = 2 * math.pi * math.sqrt(pow((6371 + " + ac + "height) * 1000, 3) / (3.986 * pow(10, 14)))\n")
file.write(ac + "retrograde = 1\n")
file.write("\n")
file.close()
