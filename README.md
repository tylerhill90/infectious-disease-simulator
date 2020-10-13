# COVID-19 Simulator

The intent of this project is to run simple simulations of how infectious
diseases spread through a population. The InfectionSim.py file houses the
classes necessary to run these simulations.

The Environment class creates an NumPy 2D array to act as an environment for
a population to randomly move around in. The environment is populated randomly
with ints representing unique people in the population. Each int is
associated with a Person instance in a dictionary to keep track of their
state. The first n number of people put into the environment are set as
'infected' where n is defined as the initial number of infected people.

Each Person instance is assigned a number of days (time steps) until they
recover from the infection based on a defined normal distribution.

When the simulation is run everyone in the environment moves a random
direction in the environment from their current position, with the edges of
the environment wrapping around to the other side. If a person is boxed in by
other people they will stay put for that time step. If a person is currently
infectious there is a chance they will infect the other people immediately
around them based on the interaction and infection rate defined.

After this there is a cleanup phase where the environment is traversed and for
every infected person their is a chance they will die. This probability is
based on cumulative density function of how many days they have been infected
and a normal distribution of the how many days a person takes to die. If they
die they are removed from the environment. The cleanup phase next checks if
the person recovers based on the number of days it takes for them to recover
defined when they were instantiated.

Run the [basic_sim.py](basic_sim.py) script to see the graphical output from a basic
simulation.

Below is an example plot outputted from a basic simulation.
![Example Figure](/figures/example_fig.png)

# PyGame Visualization

A simulation visualization tool has also been developed. See example screenshot
below. Black squares represent uninfected people. Light green squares are
currently infectious and the darker green circle surrounding them shows the
cells affected by the interaction rate parameter. The blue squares represent
recovered people who are no longer infectious or able to contract the disease.
Red squares represent a deceased person.

Run the [pygame_sim.py](pygame_sim.py) script to see the realtime visualization and then
graphical output from a basic simulation.

![Example visualization](/figures/pygame_viz.png)
