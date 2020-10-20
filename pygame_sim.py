#!/usr/bin/env python3
"""This uses PyGame to visualize a COVID-19 outbreak in a population of 1000
people living relatively close and with a high rate of interaction. The
simulation is run until there are no more infectious people.
"""

import sys
from time import perf_counter
import pygame
import numpy as np
import InfectionSim as infect


def main():
    """Set up and run the simulation until there are no more infectious people.
    """

    # Environment parameters that are used elsewhere for the visualization
    env_dim = 100
    pop_size = 1000
    initially_infected = 3
    interaction_rate = 4

    # Load environment parameters into a dict
    env_params = {
        'time_steps': 0,  # Run the sim until there are no infectious people
        'env_dim': env_dim,
        'pop_size': pop_size,
        'initially_infected': initially_infected,
        'interaction_rate': interaction_rate,
        'infection_rate': .4,  # Percent likelihood of spreading the disease
        'mortality_rate': .02,  # Percent likelihood of dieing from the disease
        'recovery_mean': 19,  # Mean number of days it takes to recover
        'recovery_sd': 3,  # Standard deviation of days it takes to recover
        'death_mean': 14,  # Mean number of days it takes to die
        'death_sd': 4,  # Standard deviation of days it takes to die
        'asymptomatic_prob': 0.25  # Probability of being asymptomatic
    }

    print('Environment Parameters')
    for key, value in env_params.items():
        print(f'{key}: {value}')

    # Instantiate the simulation environment
    sim = infect.Environment(env_params)

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
    OLIVE = (75, 150, 0)
    BLUE = (0, 0, 255)

    # Define screen size based on the env_dim, the cell size of the grid, and
    # they margin size between cells
    screen = pygame.display.set_mode((SCREEN_DIM, SCREEN_DIM))

    running = True
    while running:
        start_time_step = perf_counter()
        infected_people = []

        # Draw the current environment state
        screen.fill(BLACK)

        # Get a tuple object consisting of each coordinate in the environment
        # that is part of a "mask" that represents the interaction rate of each
        # infected person
        mask_indices_set = set()  # Empty master list
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

                # If the person is infectious then get environment indices of
                # their mask
                if infectious == [True, True, False]:
                    y, x = np.ogrid[-col: env_dim - col, -row: env_dim - row]
                    mask = x*x + y*y <= r*r
                    mask_indices = np.where(mask == True)
                    mask_indices = [tuple(mask) for mask in mask_indices]
                    x_coordinates = mask_indices[1]
                    y_coordinates = mask_indices[0]

                    # Add their mask indices to the master list
                    for x, y in zip(x_coordinates, y_coordinates):
                        mask_indices_set.add((x, y))

        mask_indices_set = tuple(mask_indices_set)

        # Draw in the masks
        for coordinate in mask_indices_set:
            row, col = coordinate[0], coordinate[1]
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
                    infected_people.append(person)
                elif sim.pop[person].recovered:
                    color = BLUE
                elif not sim.pop[person].alive:
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
            if sim.pop[person].alive:
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
