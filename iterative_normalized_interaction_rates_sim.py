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
        except:
            print(
                'Environment dimensions must be a positive integer below 100'
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
        except:
            print('Population size must be a positive integer below 1,000')


def get_interaction_rate():
    """Get an interaction rate from the user."""
    while True:
        try:
            rate = int(input(
                'Select a mean interaction rate per time epoch based on a '
                'normal distribution with standard deviation equal to one '
                'third of the mean rounded down.\nInteraction rate: '
            ))
            if not 0 < rate <= 20:
                print(
                    'Rate must be a positive integer between 1 and 20.\n'
                    'Higher rates slow the simulation too much.'
                )
            else:
                return rate
        except:
            print(
                'Rate must be a positive integer between 1 and 20. Higher '
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
        except:
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
        except:
            print('Percentage must be a real number between 0 and 100.')


def get_time():
    """Get the amount of time the simulation should run from user."""
    while True:
        try:
            time = int(input('Time: '))
            if not 0 < time < 1000:
                print('Time must be a positive integer below 1,000')
            else:
                return time
        except:
            print('Time must be a positive integer below 1,000')


def get_silence_preference():
    """Ask the user if they would like to run the simulation silently"""
    while True:
        try:
            is_silent = input(
                'Run the simulation silently?\n[y]es\t[n]o\n'
            )
            if is_silent == 'y':
                return True
            elif is_silent == 'n':
                return False
            else:
                print(
                    'Invlaid entry. Please enter either "y" for yes or "n" '
                    'for no.'
                )


def generate_plot(env, init_cons):
    """Generate a plot from a simulation."""
    time = np.array(range(init_cons['time'] + 1))
    infectious = np.array(env.report['infectious'])
    recovered = np.array(env.report['recovered'])
    dead = np.array(env.report['dead'])

    infectious, = plt.plot(
        time, infectious, label=f'Infectious (max of {max(infectious)})')
    recovered, = plt.plot(
        time, recovered, label=f'Recovered ({recovered[-1]})')
    dead, = plt.plot(time, dead, label=f'Deceased ({dead[-1]})')

    plt.title(
        f'Infection Simulation Results\nMedian Interaction Rate of '
        f'{init_cons["interaction"]}')
    plt.ylabel('Number of people')
    plt.xlabel('Time')
    plt.legend(handles=[infectious, recovered, dead])

    plt.show()
    plt.close()


def main():
    """Get user defined inputs and then run a simple simulation of 
    infection."""

    # Explain how the simulation works to the user

    # Get environment parameters from user
    env_dim = get_env_dim()
    population = get_pop()
    print('Interaction rate:')
    interaction = get_interaction_rate()
    print('Infection rate for one interaction')
    infection = get_percent()
    initially_infected = get_initial_infected(population)
    print('Mortality rate')
    mortality = get_percent()
    time = get_time()

    # Run the simulation silently?
    is_silent = get_silence_preference()

    # Create environment
    env = Environment(env_dim, population, interaction,
                        infection, initially_infected, mortality)

    # Report starting conditions
    print('Starting Conditions')
    print(f'Environment dimensions: {env_dim} x {env_dim}')
    print(f'Population size: {population}')
    print(f'Interaction rate: mean of {interaction}')
    print(f'Infection rate: {infection}')
    print(f'Number initially infected: {initially_infected}')
    print(f'Mortality rate: {mortality}')
    print(f'Time: {time}\n')

    # Run simulation
    env.run_sim(time)

    # Calculate some final number totals
    # Ad preceding zeroes to match length of population
    pop_len = len(str(population))

    infected = str(env.report['infectious']).zfill(pop_len)

    recovered = str(env.report['recovered']).zfill(pop_len)

    dead = str(env.report['dead']).zfill(pop_len)

    # Report totals
    interaction_rates = [
        env.pop[person].interaction_rate for person in env.pop]
    print(
        f'\nInteraction rate\nMin: {min(interaction_rates)}\nMedian: '
        f'{median(interaction_rates)}\nMax: {max(interaction_rates)}'
    )
    print(f'Total interactions: {env.total_interactions}\n')
    print(f'Infected:\t{infected} / {population}')
    print(f'Recovered:\t{recovered} / {population}')
    print(f'Dead:\t\t{dead} / {population}')

    generate_plot(env, init_cons)


if __name__ == '__main__':
    main()
