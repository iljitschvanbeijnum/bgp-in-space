#!/usr/bin/python3
import sys, time, os, shutil

if len(sys.argv) != 6:
  print("Usage:", sys.argv[0], "<simulation> <ixps> <cons-number> <cons-name> <satellites>")
  sys.exit()

print("Generating constellation config files:")
print

sim = sys.argv[1]
sixps = int(sys.argv[2])
consnum = int(sys.argv[3])
consname = sys.argv[4]
satellites = int(sys.argv[5])

acsats = ""
acsatnums = ""
acsatnames = ""
acinterfaces = ""

for sat in range(1, satellites + 1):
  print("Satellite %d" % sat)

  acsats = acsats + "%d, " % int(360 / satellites * (sat - 1))
  acsatnums = acsatnums + "%d, " % sat
  acsatnames = acsatnames + "\"%s-%02d\", " % (consname, sat)

  dir = "%s/%s-%02d" % (sim, consname, sat)
  if not os.path.exists(dir):
    os.makedirs(dir)
  shutil.copyfile("daemons", dir + "/daemons")

  # vlans.sh
  file = open(dir + "/vlans.sh", "w")
  file.write("#!/bin/sh\n")
  vlans = "vlans=\"%d" % consnum
  for i in range(1, sixps + 1):
    vlans = vlans + " %d" % (i * 256 + consnum * 16 + sat)
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
  file.write("hostname %s%02d\n" % (consname,  sat))
  file.write("!\n")
  file.write("terminal paginate\n")
  file.write("!\n")
  file.close()

  # zebra.conf
  file = open(dir + "/zebra.conf", "w")
  file.write("!\n")
  file.write("interface lo\n")
  file.write(" ip address 172.2%d.%d.1/32\n" % (consnum, sat))
  file.write("!\n")
  file.write("interface eth0.%d\n" % consnum)
  file.write(" ip address 172.31.%d.%d/30\n" % (consnum, 4 * sat + 1))
  file.write(" ip address 172.31.%d.%d/30\n" % (consnum, 4 * sat + 6))
  file.write("!\n")
  for i in range(1, sixps + 1):
    acinterfaces = acinterfaces + "\"eth0.%d\", " % (i * 256 + consnum * 16 + sat)
    file.write("interface eth0.%d\n" % (i * 256 + consnum * 16 + sat))
    file.write(" ip address 10.%d.%d.1/24\n" % (i, consnum * 16 + sat))
    file.write("!\n")
  file.close()

  # staticd.conf
  file = open(dir + "/staticd.conf", "w")
  file.write("!\n")
  for i in range(0, 8):
    file.write("ip route 172.2%d.%d.0/24 null0\n" % (consnum, 32 * i + sat))
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

  # ospfd.conf
  file = open(dir + "/ospfd.conf", "w")
  file.write("!\n")
  file.write("interface eth0.%d\n" % consnum)
  file.write(" ip ospf cost %d\n" % (40000 / satellites))
  file.write("!\n")
  file.write("router ospf\n");
  file.write(" network 172.2%d.%d.0/24\n" % (consnum, sat))
  file.write(" network 172.31.0.0/16 area 0\n");
  file.write(" redistribute connected\n");
  file.write("!\n")
  file.close()

  # bgpd.conf
  file = open(dir + "/bgpd.conf", "w")
  file.write("!\n")
  file.write("router bgp %d\n" % (65000 + consnum))
  file.write(" no bgp ebgp-requires-policy\n")
  for i in range(0, 8):
    file.write(" network 172.2%d.%d.0/24\n" % (consnum, 32 * i + sat))
  '''
  if (sat > 1):
    file.write(" neighbor 172.31.%d.%d description Link to previous satellite\n" % (consnum, sat - 1))
    file.write(" neighbor 172.31.%d.%d remote-as %d\n" % (consnum, sat - 1, 65000 + consnum))
    file.write(" neighbor 172.31.%d.%d next-hop-self\n" % (consnum, sat - 1))
  else:
    file.write(" neighbor 172.31.%d.%d description Link to previous satellite\n" % (consnum, satellites))
    file.write(" neighbor 172.31.%d.%d remote-as %d\n" % (consnum, satellites, 65000 + consnum))
    file.write(" neighbor 172.31.%d.%d next-hop-self\n" % (consnum, satellites))
  if (sat < satellites):
    file.write(" neighbor 172.31.%d.%d description Link to next satellite\n" % (consnum, sat + 1))
    file.write(" neighbor 172.31.%d.%d remote-as %d\n" % (consnum, sat + 1, 65000 + consnum))
    file.write(" neighbor 172.31.%d.%d next-hop-self\n" % (consnum, sat + 1))
  else:
    file.write(" neighbor 172.31.%d.%d description Link to next satellite\n" % (consnum, 1))
    file.write(" neighbor 172.31.%d.%d remote-as %d\n" % (consnum, 1, 65000 + consnum))
    file.write(" neighbor 172.31.%d.%d next-hop-self\n" % (consnum, 1))
  '''
  # iBGP
  for i in range(1, satellites + 1):
    if (i != sat):
      file.write(" neighbor 172.31.%d.%d remote-as %d\n" % (consnum, i, 65000 + consnum))
  # to SIXPs
  for i in range(1, sixps + 1):
    file.write(" neighbor 10.%d.%d.254 remote-as %d\n" % (i, consnum * 16 + sat, 64900 + i))
    file.write(" neighbor 10.%d.%d.254 shutdown\n" % (i, consnum * 16 + sat))
    #file.write(" neighbor 10.%d.%d.254 bfd\n" % (i, consnum * 16 + sat))
    file.write(" neighbor 10.%d.%d.254 bfd profile 100ms\n" % (i, consnum * 16 + sat))
  file.write("!\n")
  file.close()

  # neighbor up/down config files
  for i in range(1, sixps + 1):
    file = open(dir + "/up%d.conf" % i, "w")
    file.write("!\n")
    file.write("router bgp\n")
    file.write(" no neighbor 10.%d.%d.254 shutdown\n" % (i, consnum * 16 + sat))
    file.write("!\n")
    file.close()
    file = open(dir + "/down%d.conf" % i, "w")
    file.write("!\n")
    file.write("router bgp\n")
    file.write(" neighbor 10.%d.%d.254 shutdown\n" % (i, consnum * 16 + sat))
    file.write("!\n")
    file.close()

# settings.py
ac = str.lower(consname[-1:])
file = open(sim + "/settings.py", "a")
file.write(ac + "height = 500\n")
file.write(ac + "sats = [ " + acsats[0:-2] + " ]\n")
file.write(ac + "satnums = [ \"\", " + acsatnums[0:-2] + " ]\n")
file.write(ac + "satnames = [ \"\", " + acsatnames[0:-2] + " ]\n")
file.write(ac + "interfaces = [ \"\", " + acinterfaces[0:-2] + " ]\n")
file.write(ac + "up = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]\n")
file.write(ac + "period = 2 * math.pi * math.sqrt(pow((6371 + " + ac + "height) * 1000, 3) / (3.986 * pow(10, 14)))\n")
file.write(ac + "retrograde = 1\n")
file.write("\n")
file.close()
