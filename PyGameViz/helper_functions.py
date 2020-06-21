#!/usr/bin/env python
"""Helper functions for running simulations from user inputs.
"""


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
