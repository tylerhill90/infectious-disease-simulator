#!/usr/bin/env python3
"""Show the difference in runtimes for idenitcal starting parameters between
the two different implementations of the infection simulators. Generates plots
for each simulation to show how they differ in outcome as well.
"""

import InfectionSim
import InfectionSimClass
from helper_functions import generate_plot
import time


def main():
    env_params = {
        'env_dim': 50,
        'pop_size': 250,
        'initially_infected': 1,
        'time': 180,
        'interaction_type': 'static',
        'interaction_rate': 2,
        'mortality_rate': .02,
        'infection_rate': .2,
        'days_to_recover': (19, 5),
        'days_to_die': (13, 4),
    }

    for key, value in env_params.items():
        print(f'{key}: {value}')
    print('\n')

    # NumPy implementation
    print('NumPy implementation')
    start_time = time.perf_counter()
    env_1 = InfectionSim.Environment(env_params)
    env_1.run_sim()
    end_time = time.perf_counter()
    run_time = end_time - start_time
    print(f"Finished in {run_time:.4f} secs\n\n")

    # Dynamic python lists implementation
    print('Dynamic python lists implementation')
    start_time = time.perf_counter()
    env_2 = InfectionSimClass.Environment(env_params)
    env_2.run_sim()
    end_time = time.perf_counter()
    run_time = end_time - start_time
    print(
        f"Finished in {run_time:.4f} secs")

    generate_plot(env_1, save=True)
    generate_plot(env_2)


if __name__ == '__main__':
    main()
