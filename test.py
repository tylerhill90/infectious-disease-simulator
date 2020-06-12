#!/usr/bin/env python3

import NumPyInfectionSimClass
import InfectionSimClass
import numpy as np
import matplotlib.pyplot as plt
import time


def generate_plot(env):
    """Generate a plot from a simulation."""

    # Collect the data for graphing
    time = np.array(range(env.time + 1))
    infectious = np.array(env.report['infectious'])
    recovered = np.array(env.report['recovered'])
    dead = np.array(env.report['dead'])

    # Plot the data
    infectious, = plt.plot(
        time, infectious, label=f'Infectious (max of {max(infectious)})')
    recovered, = plt.plot(
        time, recovered, label=f'Recovered ({recovered[-1]})')
    dead, = plt.plot(time, dead, label=f'Deceased ({dead[-1]})')

    # Set graph title, axis, and legend
    plt.title(
        f'Infection Simulation Results\nInteraction Rate of '
        f'{env.interaction_rate}'
    )
    plt.ylabel('Number of people')
    plt.xlabel('Time')
    plt.legend(handles=[infectious, recovered, dead])

    # Show the graph
    plt.show()
    plt.close()


env_params = {
    'env_dim': 100,
    'pop_size': 1000,
    'initially_infected': 10,
    'time': 90,
    'interaction_type': 'static',
    'interaction_rate': 2,
    'mortality_rate': .02,
    'infection_rate': .2,
    'days_to_recover': (19, 5),
    'days_to_die': (13, 4),
}

start_time = time.perf_counter()
env_1 = NumPyInfectionSimClass.Environment(env_params)
env_1.run_sim()
end_time = time.perf_counter()
run_time = end_time - start_time
print(f"Finished NumPy env in {run_time:.4f} secs\n\n")

# Display a graph of the simulation results
generate_plot(env_1)

start_time = time.perf_counter()
env_2 = InfectionSimClass.Environment(env_params)
env_2.run_sim()
end_time = time.perf_counter()
run_time = end_time - start_time
print(f"Finished lists env in {run_time:.4f} secs\n\n")

# Display a graph of the simulation results
generate_plot(env_2)
