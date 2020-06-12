"""A very simple simulation of infection in a square closed environment."""

from InfectionSimClass import *
import sys
import time
from math import floor
from statistics import median
import matplotlib.pyplot as plt
import numpy as np


def get_env_dim():
    """Get the environment dimensions (length of one side of the square) from
    user."""
    while True:
        try:
            env_dim = int(input('Environment dimensions: '))
            if not 0 < env_dim <= 100:
                print(
                    'Environment dimensions must be a positive integer '
                    'below 100'
                )
            else:
                return env_dim
        except ValueError:
            print(
                'Environment dimensions must be a positive integer less than '
                'or equal to 100.'
            )


def get_pop():
    """Get population size from user."""
    while True:
        try:
            pop = int(input('Population size: '))
            if not 0 < pop <= 1000:
                print('Population size must be a positive integer below 1,000')
            else:
                return pop
        except ValueError:
            print('Population size must be a positive integer below 1,000')


def get_interation_type():
    """Ask user if they want a static interaction rate for each person or a
    normalized range of rates around a selected mean."""
    while True:
        interaction_type = input(
            'Would you like a [s]tatic interaction rate of a [n]ormalized '
            'range of interaction rates around a given mean.\n'
        )
        if interaction_type == 's':
            return 'static'
        elif interaction_type == 'n':
            return 'normalized'
        else:
            print(
                'Invalid entry.\nOnly "s" for static interaction rate or '
                '"n" for normalized range of interaction rates supported.'
            )


def get_interaction_rate(interaction_type):
    """Get an interaction rate from the user."""
    while True:
        try:
            if interaction_type == 'static':
                rate = int(input(
                    'Static interaction rate: '
                ))
            else:
                rate = int(input(
                    'Select a mean interaction rate per time step based on a '
                    'normal distribution with standard deviation equal to one '
                    'fifth of the mean rounded down.\nInteraction rate: '
                ))
            if not 0 < rate <= 10:
                print(
                    'Rate must be a positive integer between 1 and 10.\n'
                    'Higher rates slow the simulation too much.'
                )
            else:
                return rate
        except ValueError:
            print(
                'Rate must be a positive integer between 1 and 10. Higher '
                'rates slow the simulation too much.'
            )


def get_initial_infected(population):
    """Get the number of initially infected persons from the user.
    Must be less than the population."""
    while True:
        try:
            initial_infected = int(
                input('Number of initially infected persons: '))
            if not 0 < initial_infected < population:
                print(
                    'The number of initially infected persons must be an '
                    'integer that is more than 0 and less than the total '
                    'population.'
                )
            else:
                return initial_infected
        except ValueError:
            print(
                'The number of initially infected persons must be an '
                'integer that is more than 0 and less than the total '
                'population.'
            )


def get_percent():
    """Get a percentage from the user."""

    while True:
        try:
            percent = float(input('Percentage: '))
            if not 0 <= percent <= 100:
                print('Percentage must be a real number between 0 and 100.')
            else:
                return percent / 100
        except ValueError:
            print('Percentage must be a real number between 0 and 100.')


def get_mean_and_sd_days():
    """Get the mean and standard deviation for generating a normal
    distribution."""

    while True:
        try:
            mean = int(input('Mean: '))
            if not 0 < mean <= 30:
                print(
                    'Mean must be a positive integer less than 30.'
                )
                continue
            sd = int(input('Standard deviation: '))
            if not 0 < sd < mean:
                print(
                    'Standard deviation must be a positive integer less than '
                    'the mean.'
                )
                continue
            return (mean, sd)
        except ValueError:
            print(
                'Mean and standard deviation must be a positive integer.'
            )


def get_time():
    """Get the amount of time the simulation should run from user."""

    while True:
        try:
            time = int(input('Time: '))
            if not((0 < time < 1000) and (time % 10 == 0)):
                print(
                    'Time must be a positive integer below 1,000 and a '
                    'multiple of 10.'
                )
            else:
                return time
        except ValueError:
            print(
                'Time must be a positive integer below 1,000 and a multiple '
                'of 10.'
            )


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
    if env.interaction_type == 'normalized':
        plt.title(
            f'Infection Simulation Results\nMedian Interaction Rate of '
            f'{env.interaction_rate}')
    else:
        plt.title(
            f'Infection Simulation Results\nInteraction Rate of '
            f'{env.interaction_rate}')
    plt.ylabel('Number of people')
    plt.xlabel('Time')
    plt.legend(handles=[infectious, recovered, dead])

    # Show the graph
    plt.show()
    plt.close()


def main():
    """Get user defined inputs and then run a simple simulation of 
    infection."""

    # Explain how the simulation works to the user
    print(
        'This program runs a simple simulation of how an airborne infection '
        'can spread through a population. The simulation takes place in a '
        'square grid environment with the user dictating the following:\n'
        '\t-environment dimensions (n x n)\n'
        '\t-population size\n'
        '\t-interaction rate of each person\n'
        '\t-infection rate of the disease\n'
        '\t-number of people initially infected\n'
        '\t-mortality rate of the disease\n'
        '\t-mean and standard deviation of the number of days it takes to '
        'recover\n'
        '\t-mean and standard deviation of the number of days it takes to die '
        'from the disease\n'
        '\t-how many time steps for the simulation to run\n'
        'The interaction rate can either be chosen randomly for each person '
        'from a normally distrubted range or a static number.\n\n'

        'At each time step, each person moves in a random direction a number '
        'of times equal to their respective interaction rate. If when they '
        'move they interact (overlap in a cell in the grid) with anyone else '
        'in the population, there is a chance they will infect the other '
        'person(s) in that space equal to the infection rate of the diesease '
        '(limit of 13 people per cell as this represents the maximum number '
        'of people in a 6 foot radius).\n\n'

        'At the end of each time step there is a chance that an infected '
        'person will recover or perish from the disease. These probabilities '
        'are based on the mean and standard deviation of the number of days '
        'it takes to recover, or die, and how long the person has been '
        'infected.'
    )

    # Empty dict to fill with user parameters for the environment
    env_params = {}

    # Get environment parameters from user
    print()
    env_params['env_dim'] = get_env_dim()

    print()
    env_params['pop_size'] = get_pop()

    print()
    env_params['initially_infected'] = get_initial_infected(
        env_params['pop_size']
    )

    print()
    env_params['time'] = get_time()

    print()
    env_params['interaction_type'] = get_interation_type()

    print()
    env_params['interaction_rate'] = get_interaction_rate(
        env_params['interaction_type']
    )

    print()
    while True:
        use_covid_params = input(
            'Use Covid-19 related parameters?\n[y]es\n[n]o\n'
        )
        if use_covid_params == 'y':
            break
        elif use_covid_params == 'n':
            break
        else:
            print(
                'Invalid entry.\nOnly "y" for yes or "n" for no supported.\n'
            )

    if use_covid_params == 'y':
        env_params['infection_rate'] = .2

        env_params['mortality_rate'] = .02

        env_params['days_to_recover'] = (19, 5)  # NEED TO CONFIRM THIS!!!

        env_params['days_to_die'] = (13, 4)  # NEED TO CONFIRM THIS!!!

    else:
        print('\nInfection rate per interaction')
        env_params['infection_rate'] = get_percent()

        print('\nMortality rate')
        env_params['mortality_rate'] = get_percent()

        print(
            '\nRecovery\n'
            'What are the mean and standard deviation number of days it takes '
            'for someone to recover from the disease.'
        )
        env_params['days_to_recover'] = get_mean_and_sd_days()

        print(
            '\nMortality\n'
            'What are the mean and standard deviation number of days it takes '
            'for someone to die from the disease.'
        )
        env_params['days_to_die'] = get_mean_and_sd_days()

    # Create environment
    env = Environment(env_params)

    # Report starting conditions
    print('\nStarting Conditions')
    print(f'Environment dimensions: {env.env_dim} x {env.env_dim}')
    print(f'Population size: {env.pop_size}')
    print(f'Number initially infected: {env.initially_infected}')
    print(f'Time: {env.time}\n')
    print(f'Interaction rate: {env.interaction_rate}')
    print(f'Infection rate: {env.infection_rate}')
    print(f'Mortality rate: {env.mortality_rate}')
    print(
        'Time taken to recover\n'
        f'Mean: {env.recovery_mean}\n'
        f'Standard deviation: {env.recovery_sd}'
    )
    print(
        'Time taken to die\n'
        f'Mean: {env.death_mean}\n'
        f'Standard deviation: {env.death_sd}\n'
    )

    # Run simulation
    env.run_sim()

    # Calculate some final number totals
    # Ad preceding zeroes to match length of population
    pop_len = len(str(env.pop_size))
    recovered = str(env.report['recovered'][-1]).zfill(pop_len)
    dead = str(env.report['dead'][-1]).zfill(pop_len)
    never_infected = str(sum([
        1 for person in env.pop if env.pop[person].infected == False
    ])).zfill(pop_len)

    # Report some simulation totals
    print('')  # Spacer
    if env.interaction_type == 'normalized':
        interaction_rates = [
            env.pop[person].interaction_rate for person in env.pop]
        print(
            'Population interaction rates\n'
            f'Min: {min(interaction_rates)}\n'
            f'Median: {median(interaction_rates)}\n'
            f'Max: {max(interaction_rates)}'
        )
    print(f'Total interactions: {env.total_interactions}\n')

    print(f'Recovered:\t{recovered} / {env.pop_size}')
    print(f'Dead:\t\t{dead} / {env.pop_size}')
    print(f'Never infected:\t{never_infected} / {env.pop_size}')

    # Display a graph of the simulation results
    generate_plot(env)


if __name__ == '__main__':
    main()
