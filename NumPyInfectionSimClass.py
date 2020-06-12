"""Classes for running simple airborne infection simulations."""

import numpy as np
from scipy.stats import norm
from random import choice, random
import sys


class Environment:

    def __init__(self, env_params):
        # Unpack user given environment parameters
        self.env_dim = env_params['env_dim']
        self.pop_size = env_params['pop_size']
        self.initially_infected = env_params['initially_infected']
        self.time = env_params['time']
        self.interaction_rate = env_params['interaction_rate']
        self.infection_rate = env_params['infection_rate']
        self.mortality_rate = env_params['mortality_rate']
        self.recovery_mean = env_params['days_to_recover'][0]
        self.recovery_sd = env_params['days_to_recover'][1]
        self.death_mean = env_params['days_to_die'][0]
        self.death_sd = env_params['days_to_die'][1]

        # Keeping track of stats
        self.total_interactions = 0
        self.report = {
            'infectious': [self.initially_infected],
            'recovered': [0],
            'dead': [0],
            'epoch_interactions': [0]
        }

        # Generate the environment and population
        self.env = np.full((self.env_dim, self.env_dim), np.Inf)
        self.pop = {x: Person(self.interaction_rate, self.recovery_mean,
                              self.recovery_sd)
                    for x in range(self.pop_size)}

        # Populate the environment
        self.populate()

    def populate(self):
        """Populate the environment randomly with the appropriate amount of 
        infected and non-infected people."""
        count = 0
        for person in self.pop:
            while True:
                row, col = choice(range(self.env_dim)), choice(
                    range(self.env_dim))
                if self.env[row, col] == np.Inf:
                    self.env[row, col] = person
                else:
                    continue
                if count < self.initially_infected:
                    self.pop[person].infected = True
                count += 1
                break



    def move(self, subject):
        """Take one random step from the current position."""
        position = np.where(self.env == subject)
        while True:
            step = [choice(range(-1, 2)), choice(range(-1, 2))]
            if step != [0, 0]:  # Check if moving
                new_position = [int(position[0] + step[0]),
                                int(position[1] + step[1])]

                # Check if new position will be out of bounds
                if any(x not in range(self.env_dim) for x in new_position):
                    continue

                # New positions within the bounds of the environment
                else:
                    new_row, new_col = new_position[0], new_position[1]
                    old_row, old_col = position[0], position[1]

                    # New position is empty
                    if self.env[new_row, new_col] == np.Inf:
                        # Move subject to new position
                        self.env[new_row, new_col] = subject
                        # Remove subject from previous position
                        self.env[old_row, old_col] = np.Inf

                    # New position is full so choose a new random step
                    else:
                        continue

                    break

    def infect(self, person):
        """See if an infected person infects others.

        Args:
            persons (int): The person who may infect others around them.
        """
        center = np.where(self.env == person)
        x_center, y_center = int(center[0]), int(center[1])
        n = self.env_dim
        r = self.interaction_rate

        y, x = np.ogrid[-y_center:n-y_center, -x_center:n-x_center]
        mask = x*x + y*y <= r*r

        mask_indices = np.where(mask == True)

        persons = [int(x) for x in self.env[mask_indices] if x != np.Inf]

        for person in persons:
            if random() <= self.infection_rate:
                self.pop[person].infected = True

    def clean_up(self):
        """Traverse the environment. For each person do the following:
                - If someone is infected, then
                    - See if they die
                        - If they do, remove them from the environment
                        - If not, advance their days_infected variable"""
        for ix, iy in np.ndindex(self.env.shape):
            if self.env[ix, iy] != np.Inf:
                person = self.env[ix, iy]
                if self.pop[person].infected == True:
                    # See if the infected person dies
                    self.death_roll(person)
                    # Remove them from the environment if they died
                    if self.pop[person].alive == False:
                        self.env[ix, iy] = np.Inf
                    # Else they didn't die so advance their days
                    # infected and check if they have recovered.
                    # Remove them if they have
                    else:
                        self.pop[person].days_infected += 1
                        if self.pop[person].days_infected == \
                                self.pop[person].days_to_recover:
                            self.env[ix, iy] = np.Inf
                            self.pop[person].recovered = True

    def death_roll(self, person):
        """See if an infected person dies or not based on how many days they
        have been infected."""
        days_infected = self.pop[person].days_infected
        # Normal distribution centered on median days it takes for infection to
        # kill and standard deviation of 4 days
        death_norm = norm(self.death_mean, self.death_sd)
        # Probability that someone will die given how many days they have been
        # infected so far
        death_prob = self.mortality_rate * \
            (death_norm.cdf(days_infected) - death_norm.cdf(days_infected - 1))
        if random() <= death_prob:
            self.pop[person].alive = False

    def run_sim(self):
        """Run the infection simulation and save relevant statistics at each
        epoch (time step)."""

        # For each epoch (time step) and for each person in the population,
        # if they are still alive and not recovered (if infected) move them
        # as per there respective interaction rate
        for epoch in range(self.time):
            for person in self.pop:
                if (self.pop[person].alive, self.pop[person].recovered) == \
                        (True, False):
                    self.move(person)
                    if self.pop[person].infected == True:
                        self.infect(person)
            self.clean_up()

            # Report simulation progress to user every 10 epochs
            if epoch % 10 == 0:
                print(
                    f'Calculating time steps {epoch + 1} through {epoch + 10} '
                    f'/ {self.time} ...')

            # Save stats for graphing each epoch
            self.report['infectious'].append(
                sum(
                    [1 for person in self.pop if (
                        [self.pop[person].infected, self.pop[person].recovered]
                    ) == [True, False]]
                )
            )
            self.report['recovered'].append(
                sum(
                    [1 for person in self.pop if
                        self.pop[person].recovered == True]
                )
            )
            self.report['dead'].append(
                sum(
                    [1 for person in self.pop if
                        self.pop[person].alive == False]
                )
            )
            self.report['epoch_interactions'].append(
                self.total_interactions -
                sum(self.report['epoch_interactions'])
            )


class Person:

    def __init__(self, interaction_rate, recovery_mean,
                 recovery_sd):
        # Assign random interaction rate from a normal distribution
        self.interaction_rate = interaction_rate
        self.infected = False
        self.days_infected = 0
        self.days_to_recover = round(np.random.normal(
            recovery_mean, recovery_sd
        ))
        self.recovered = False
        self.alive = True
