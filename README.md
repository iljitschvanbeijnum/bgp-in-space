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

Everything currently works under MacOS and Linux, but there are some issues running under Windows.

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
You can then python3 connect.py ConsA-01 / SIXP0[1-6] / ConsC-01 to
connect to that router and execute FRR commands.
Or add "bash" and you're on the commandline of that container. Or something like "show ip bgp summary" and you get the results of that command.
To start the constellation with routers, run stars6docker:

``` bash
python3 start.py stars6docker
```


Settings are in the <sim name>/settings.py file.

Stop the Docker virtual routers with python3 stars6docker. Or in the Docker dashboard. The containers are then killed off. If you've saved their configuration, that should be in <sim name>/<router name>/<daemon>.conf

##

There are two scripts for generating simulated space routers. First, run:

``` bash
python3 gensixpconfigs.py
```

The arguments are:

- the name of the simulation (a folder with that name will be created)
- the number of space IXPs
- the number of constellations the space IXPs connect to (1 or 2)
- the number of satellites in these constellations

Then, run once or twice:

``` bash
python3 genconstellation.py
```

Here, the arguments are:

- the name of the simulation
- the constellation number (1 - 7)
- the constellation name (first one must end in an A and the second one in a C currently)
- number of satellites in the constellation (max 15)

Then, edit the <simname>/settings.py file to adjust the simulation settings. By default, the simulation will just show distances between the space IXPs and other satellites and whether those are in communications range. Do this with:

``` bash
python3 orbit.py <simname>
```

With docker = 1, Docker containers running FRR virtual routers will see their connectivity change based on that range. Before running orbit.py, run the following to start up the containers:

``` bash
python3 start.py <simname>
```

And after you're done, to remove the containers:

``` bash
python3 stop.py <simname>
```

Adjust the timing so the virtual routers have enough time to create BGP connections. Running at an hour of simulated time in a second of real time won't work here.
