#!/usr/bin/python3
import sys, time, os

def startrouter(dockerargs, labpath, configdir, dockerimage, routernum, routername):
  print(routername + "...")
  os.system("docker run %s -v \"%s%s:%s\" --name %s -d %s >/dev/null" % (dockerargs, labpath, routername, configdir, routername, dockerimage))
  time.sleep(0.5)
  os.system("docker exec -d %s bash %s/vlans.sh" % (routername, configdir))
  time.sleep(0.5)

if len(sys.argv) == 1:
  print("Usage:", sys.argv[0], "<simulation>")
  sys.exit()

sim = sys.argv[1]
sys.path.append(sim)
from settings import *

print("Starting routers:")
print

dockerargs = "--rm -t --pull never --sysctl net.ipv6.conf.all.disable_ipv6=0 --cap-add cap_net_admin --cap-add cap_net_raw --cap-add cap_sys_admin"
dockerimage = "frrouting/frr:v8.3.1"
configdir = "/etc/frr"
labpath = os.getcwd() + "/%s/" % sim

n = 0
for i in asats:
  n = n + 1
  startrouter(dockerargs, labpath, configdir, dockerimage, asatnums[n], asatnames[n])

n = 0
for i in bsats:
  n = n + 1
  startrouter(dockerargs, labpath, configdir, dockerimage, bsatnums[n], bsatnames[n])

n = 0
for i in csats:
  n = n + 1
  startrouter(dockerargs, labpath, configdir, dockerimage, csatnums[n], csatnames[n])


