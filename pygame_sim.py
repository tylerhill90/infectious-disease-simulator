#!/usr/bin/env python3
"""
"""

import sys
import pygame
import numpy as np
import itertools
from time import perf_counter
from InfectionSim import *


def main():
    # Environment parameters
    env_dim = 100
    pop_size = 500
    initially_infected = 3
    interaction_rate = 5

    # Load environment parameters into a dict
    env_params = {
        'time_steps': 0,
        'env_dim': env_dim,
        'pop_size': pop_size,
        'initially_infected': initially_infected,
        'interaction_rate': interaction_rate,
        'infection_rate': 1,  # Need to confirm
        'mortality_rate': .02,  # Need to confirm
        'days_to_recover': (19, 3),  # Need to confirm
        'days_to_die': (14, 4)  # Need to confirm
    }

    # Instantiate the simulation environment
    sim = Environment(env_params)

    # PYGAME VISUALIZATION
    pygame.init()

    # Define some visualization constants
    TIME_DELAY = 250  # Milliseconds
    CELL = 6
    MARGIN = 1
    SCREEN_DIM = env_dim * CELL + (MARGIN * env_dim + 1)

    # RGB Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    OLIVE = (100, 200, 0)
    BLUE = (0, 0, 255)

    # Define screen size based on the env_dim, the cell size of the grid, and
    # they margin size between cells
    screen = pygame.display.set_mode((SCREEN_DIM, SCREEN_DIM))

    running = True
    while running:
        start_time_step = perf_counter()
        infected_people = []
        circle_centers = []

        # Draw the current environment state
        screen.fill(BLACK)

        # Draw the "mask" around infected people showing their interaction rate
        mask_indices_set = set()
        for row, col in np.ndindex(sim.env.shape):
            pygame.draw.rect(screen, WHITE,
                             [(MARGIN + CELL) * col + MARGIN,
                              (MARGIN + CELL) * row + MARGIN,
                                 CELL,
                                 CELL])
            if sim.env[row, col] != np.Inf:  # Cell is occupied by a person
                person = sim.env[row, col]
                r = sim.pop[person].interaction_rate
                infectious = [sim.pop[person].alive,
                              sim.pop[person].infected,
                              sim.pop[person].recovered]
                # Change the color of the cell depending on the person's state
                if infectious == [True, True, False]:
                    y, x = np.ogrid[-col: env_dim - col, -row: env_dim - row]
                    mask = x*x + y*y <= r*r

                    # Get environment indices of the mask
                    mask_indices = np.where(mask == True)
                    mask_indices = [tuple(mask) for mask in mask_indices]
                    x_coordinates = mask_indices[1]
                    y_coordinates = mask_indices[0]
                    for x, y in zip(x_coordinates, y_coordinates):
                        mask_indices_set.add((x, y))
        mask_indices_set = tuple(mask_indices_set)

        for coordinate in mask_indices_set:
            row, col = coordinate[0], coordinate[1]
            # Fill in the cell's color
            pygame.draw.rect(screen, OLIVE,
                             [(MARGIN + CELL) * col + MARGIN,
                              (MARGIN + CELL) * row + MARGIN,
                              CELL,
                              CELL])

        # Draw in the people
        for row, col in np.ndindex(sim.env.shape):
            if sim.env[row, col] != np.Inf:  # Cell is occupied by a person
                person = sim.env[row, col]
                infectious = [sim.pop[person].alive,
                              sim.pop[person].infected,
                              sim.pop[person].recovered]
                # Change the color of the cell depending on the person's state
                if infectious == [True, True, False]:
                    color = GREEN
                    # Save the cell's x, y center for drawing circles later
                    circle_centers.append((
                        (MARGIN + CELL) * col + MARGIN + int(CELL / 2),
                        (MARGIN + CELL) * row + MARGIN + int(CELL / 2)
                    ))
                    infected_people.append(person)
                elif sim.pop[person].recovered == True:
                    color = BLUE
                elif sim.pop[person].alive == False:
                    color = RED
                else:
                    color = BLACK  # Unaffected

                # Fill in the cell's color
                pygame.draw.rect(screen, color,
                                 [(MARGIN + CELL) * col + MARGIN,
                                  (MARGIN + CELL) * row + MARGIN,
                                  CELL,
                                  CELL])

        # Move the simulation one time step forward
        for person in sim.pop.keys():
            if sim.pop[person].alive == True:
                sim.move(person)
                conditions = [
                    sim.pop[person].infected, sim.pop[person].recovered
                ]
                if conditions == [True, False]:  # Person is infectious
                    sim.infect(person)

        # Perform the clean up phase
        sim.clean_up(remove_persons=False)

        # Increment the time steps
        sim.time_steps += 1

        # Display the current environment state after a time delay if requested
        end_time_step = perf_counter()
        run_time = (end_time_step - start_time_step) * 1000  # Milliseconds
        delay = int(TIME_DELAY - run_time)
        if run_time < TIME_DELAY:
            pygame.time.delay(delay)
        pygame.display.flip()

        # Simulation is over when there are no more infectious persons
        if sim.report['infectious'][-1] == 0:
            sim.generate_plot()  # Show summary stats
            running = False

    # Exit pygame without errors
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main()
