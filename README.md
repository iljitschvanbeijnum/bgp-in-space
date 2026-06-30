# bgp-in-space
A set of Python scripts to simulate running BGP between satellites. The output is the distance between sets of satellites and whether that's within reach of optical inter-satellite link range, but when configured to to so, the scripts will fire up FRR routers in Docker containers that will connect to each other when in range in order to evaluate whether BGP can handle the dynamics of inter-domain routing in space.

Unzip the stars5, stars6 and stars6docker zip files which contain settings and configurations simulating a single satellite in constellation A talking to a single satellite in constellation C through 5 or 6 "space IXP" satellites. Run those like this:

python3 stars5
python3 stars6
python3 stars6docker

In the last case, you need to have Docker running and do python3 start.py stars6docker. You can then python3 connect.py ConsA-01 / SIXP0[1-6] / ConsB-01 to connect to that router and execute FRR commands. Or add "bash" and you're on the commandline of that container. Or something like "show ip bgp summary" and you get the results of that command.

Settings are in the <sim name>/settings.py file.

Stop the Docker virtual routers with python3 stars6docker. Or in the Docker dashboard. The containers are then killed off. If you've saved their configuration, that should be in <sim name>/<router name>/<daemon>.conf

More information about the "gen" scripts to generate configurations soon.
