# bgp-in-space
A set of Python scripts to simulate running BGP between satellites. The output is the distance between sets of satellites and whether that's within reach of optical inter-satellite link range, but when configured to to so, the scripts will fire up FRR routers in Docker containers that will connect to each other when in range in order to evaluate whether BGP can handle the dynamics of inter-domain routing in space.

## Requirements
The project requires the FRR docker image (v8.3.1) to be installed:
``` bash
docker pull frrouting/frr:v8.3.1
```

Extract the stars5, stars6 and stars6docker archives which contain settings and configurations simulating a single satellite in constellation A talking to a single satellite in constellation C through 5 or 6 "space IXP" satellites.

``` bash
unzip stars5.zip
unzip stars6.zip
unzip stars6docker.zip
```

## Running the simulations

### Simulating the IXP constellations:

``` bash
python3 stars5
```

``` bash
python3 stars6
```

### Running the constellations

You need to have Docker running before you run this simulator.
You can then python3 connect.py ConsA-01 / SIXP0[1-6] / ConsB-01 to
connect to that router and execute FRR commands.
Or add "bash" and you're on the commandline of that container. Or something like "show ip bgp summary" and you get the results of that command.
To start the constellation with routers, run stars6docker:

``` bash
python3 start.py stars6docker
```


Settings are in the <sim name>/settings.py file.

Stop the Docker virtual routers with python3 stars6docker. Or in the Docker dashboard. The containers are then killed off. If you've saved their configuration, that should be in <sim name>/<router name>/<daemon>.conf

More information about the "gen" scripts to generate configurations soon.
