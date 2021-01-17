# Infectious Disease Simulator

The intent of this project is to run simple simulations of how an infectious disease spreads through a population.

[InfectionSim.py](InfectionSim.py) houses the classes necessary to run these simulations. The Environment class creates an NumPy 2D array to act as an environment for a population to randomly move around in. The environment is populated randomly with integers representing the people in the population. Each integer is associated with a Person instance in a dictionary to keep track of their state. The first n number of people put into the environment are infected where n is the initial number of infected people.

Each Person instance is assigned a number of days (time steps) until they recover from the infection based on a defined normal distribution and also whether they will be asymptomatic based on a predefined probability. If they are asymptomatic their interaction rate will likely be higher due to not knowing that they are sick. Conversely, if they are symptomatic then their interaction rate will be 0 or 1, representing their attempt to self isolate.

During the simulation each person moves one step from their current position and the edges of the environment wraparound. If a person is boxed in by other people they will stay put for that time step. If a person is currently infectious there is a chance they will infect the other people immediately around them based on their own interaction and the defined infection rate.

After this there is a cleanup phase where each person is checked to see if they have reached the number of days it takes for them to either recover or die. If they recover they are no longer infectious and are immune to reinfection and if they die they are removed from the simulation.

To see a graph of the results from a COVID-19 simulation run the [basic_sim.py](basic_sim.py) script.

# PyGame Visualization with GUI Inputs

A simulation can also be visualized with GUI inputs by running the [run_sim.py](run_sim.py) script. See the example GIFs below.

![Example GUI input](/figures/gui.gif)

![Example visualization](/figures/sim_running.gif)

![Example simulation graph](figures/infect_sim_graph.png)

Black squares are uninfected people. Light green squares are currently infectious people. The darker green circle surrounding them show the cells in the environment that represent their interaction rate and any uninfected people in these darker green squares may also become infected. The blue squares are recovered people who are no longer infectious or able to contract the disease. Red squares are deceased people.
