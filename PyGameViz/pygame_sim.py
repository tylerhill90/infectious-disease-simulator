#!/usr/bin/env python3
"""
"""

import pygame
from InfectionSim import *
from helper_functions import *

def main():
    # Get environment parameters from the user
    env_dim = 50
    pop_size = 200
    initially_infected = 2
    interaction_rate = 2
    time = 180


    # Load environment parameters into a dict
    env_params = {
            'time': time,
            'env_dim': env_dim,
            'pop_size': pop_size,
            'initially_infected': initially_infected,
            'interaction_rate': interaction_rate,
            'infection_rate': .2,  # Need to confirm
            'mortality_rate': .02,  # Need to confirm
            'days_to_recover': (19, 5),  # Need to confirm
            'days_to_die': (14, 4)  # Need to confirm
    }

    # Set up the simulation environment
    env = Environment(env_params)

    pygame.init()

    # Define screen size based on the env_dim
    screen = pygame.display.set_mode((env_dim * 10, env_dim * 10))
    screen.fill((255, 255, 255))

    while time != 0:
        # Draw the current environment state
        ## TODO

        # Display the current environment state
        pygame.display.flip()

        # Move the simulation one time step forward
        for person in env.pop:
                if (env.pop[person].alive, env.pop[person].recovered) == \
                        (True, False):
                    env.move(person)
                    if env.pop[person].infected == True:
                        env.infect(person)

        # Perform the clean up phase and save stats for plotting
        env.clean_up()
        env.save_stats()
        
        # Decrement the time steps left
        time -= 1

    pygame.quit()

    env.generate_plot()

if __name__ == '__main__':
    main()