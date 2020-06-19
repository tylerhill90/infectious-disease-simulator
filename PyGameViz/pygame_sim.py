#!/usr/bin/env python3
"""
"""

import pygame
import numpy as np
from InfectionSim import *


def main():
    # Set some environment parameters
    env_dim = 60
    pop_size = 400
    initially_infected = 4
    interaction_rate = 2
    time = 90

    # Load environment parameters into a dict
    env_params = {
        'time': time,
        'env_dim': env_dim,
        'pop_size': pop_size,
        'initially_infected': initially_infected,
        'interaction_rate': interaction_rate,
        'infection_rate': .25,  # Need to confirm
        'mortality_rate': .02,  # Need to confirm
        'days_to_recover': (19, 5),  # Need to confirm
        'days_to_die': (14, 4)  # Need to confirm
    }

    # Set up the simulation environment
    env = Environment(env_params)

    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Define some other constants
    TIME_DELAY = 200  # Milliseconds
    CELL = 10
    MARGIN = 1
    SCREEN_DIM = env_dim * CELL + (MARGIN * env_dim + 1)

    pygame.init()

    # Define screen size based on the env_dim, the cell size of the grid, and
    # they margin size between cells
    screen = pygame.display.set_mode((SCREEN_DIM, SCREEN_DIM))
    screen.fill(BLACK)

    while time != 0:
        # Draw the current environment state
        for row, col in np.ndindex(env.env.shape):
            if env.env[row, col] != np.Inf:  # Cell is occupied by a person
                person = env.env[row, col]
                infectious = [env.pop[person].infected,
                  env.pop[person].alive, env.pop[person].recovered]
                if infectious == [True, True, False]:
                    color = GREEN
                elif env.pop[person].recovered == True:
                    color = BLUE
                elif env.pop[person].alive == False:
                    color = RED
                else:
                    color = BLACK
            else:
                color = WHITE
            pygame.draw.rect(screen, color,
                             [(MARGIN + CELL) * col + MARGIN,
                              (MARGIN + CELL) * row + MARGIN,
                              CELL,
                              CELL])

        # Display the current environment state
        pygame.display.flip()
        pygame.time.delay(TIME_DELAY)

        # Move the simulation one time step forward
        for person in env.pop.keys():
            if env.pop[person].alive == True:
                env.move(person)
                if env.pop[person].infected == True:
                    env.infect(person)

        # Perform the clean up phase and save stats for plotting
        env.clean_up(remove_persons=False)
        env.save_stats()

        # Decrement the time steps left
        time -= 1

    pygame.quit()

    env.generate_plot()


if __name__ == '__main__':
    main()
