#!/usr/bin/env python3
"""Run a basic simulation of a COVID-19 outbreak in a 1000 person population
in an environment that is 10% populated and with 1% initially infected. The
simulation is run for 180 time steps with an interaction rate of 2.
"""

from InfectionSim import *
import time


def main():
    # Set up environmental parameters for simulation
    env_params = {
        'time_steps': 180,
        'env_dim': 100,
        'pop_size': 1000,
        'initially_infected': 10,
        'interaction_rate': 2,
        'infection_rate': .4,  # Need to confirm
        'mortality_rate': .02,  # Need to confirm
        'days_to_recover': (19, 5),  # Need to confirm
        'days_to_die': (14, 4)  # Need to confirm
    }

    # Report environmental parameters to the console
    print('Environment Parameters')
    [print(f'{key}: {value}') for key, value in env_params.items()]

    # Time the simulation
    start_time = time.perf_counter()

    # Create environment
    env = Environment(env_params)

    # Run simulation
    env.run_basic_sim()

    # Report max R efective value and the run time
    end_time = time.perf_counter()
    run_time = end_time - start_time

    print(f'\nMax R effective: {max(env.report["r_effective"])}')
    print(f'Run time: {run_time:.4} secs')

    # Graph results
    env.generate_plot()


if __name__ == '__main__':
    main()
