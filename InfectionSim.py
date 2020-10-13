"""Classes for running simple infection simulations.
"""

import sys
from random import random, choice
from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt


class Environment:
    """A class for setting up and running the infection simulation.
    """

    def __init__(self, env_params):

        # Unpack user given environment parameters
        self.time_steps = env_params['time_steps']
        self.env_dim = env_params['env_dim']
        self.pop_size = env_params['pop_size']
        self.initially_infected = env_params['initially_infected']
        self.interaction_rate = env_params['interaction_rate']
        self.infection_rate = env_params['infection_rate']
        self.mortality_rate = env_params['mortality_rate']
        self.recovery_mean = env_params['days_to_recover'][0]
        self.recovery_sd = env_params['days_to_recover'][1]
        self.death_mean = env_params['days_to_die'][0]
        self.death_sd = env_params['days_to_die'][1]

        # Keep track of stats during the simulation to use for graphing
        self.recovered = 0
        self.dead = 0
        self.report = {
            'infectious': [self.initially_infected],
            'recovered': [0],
            'dead': [0],
            'not_infected': [self.pop_size - self.initially_infected],
            'r_naught': [0]
        }

        # Generate the environment and population
        self.env = np.full((self.env_dim, self.env_dim), np.Inf)
        self.pop = {x: Person(self.recovery_mean,
                              self.recovery_sd)
                    for x in range(self.pop_size)}

        # Populate the environment
        self.populate()

    def populate(self):
        """Populate the environment randomly with the appropriate amount of
        infected and non-infected people with no overlap.
        """

        # Error check user
        if self.pop_size > self.env_dim ** 2:
            sys.exit('Population larger than environment can support.')

        if self.pop_size < self.initially_infected:
            sys.exit(
                'Population smaller than the number of initially infected '
                'people defined.'
            )

        count_infected = 0  # Track the number of initially infected people
        for person in self.pop:
            while True:
                row = np.random.randint(self.env_dim)
                col = np.random.randint(self.env_dim)
                if self.env[row, col] == np.Inf:
                    self.env[row, col] = person
                else:
                    continue
                if count_infected < self.initially_infected:
                    self.pop[person].infected = True
                    count_infected += 1
                break

    def move(self, person):
        """Take one random step from the current position for a given subject
        in the population.

        Args:
            person (int): The person in the population who is moving

        Return:
            int: Returns 0 if the person did not move or 1 if they did
        """

        position = np.where(self.env == person)  # Current position in env
        directions = [
            [-1, 1], [0, 1], [1, 1],
            [-1, 0], [1, 0],
            [-1, -1], [0, -1], [1, -1]
        ]

        while True:
            # Positions exhausted so person doesn't move
            if directions == []:
                return 0

            step = choice(directions)  # Choose random direction to step
            new_position = [position[0] + step[0],
                            position[1] + step[1]]

            # The environment has no borders
            # Wrap around to other side if moving past the bounds of the
            # environment array
            for coordinate in range(len(new_position)):
                if new_position[coordinate] == -1:
                    new_position[coordinate] = self.env_dim - 1
                if new_position[coordinate] == self.env_dim:
                    new_position[coordinate] = 0

            # Check if new position is empty
            if self.env[new_position[0], new_position[1]] == np.Inf:
                # Move subject to new position
                self.env[new_position[0], new_position[1]] = person
                # Remove subject from previous position
                self.env[position[0], position[1]] = np.Inf

            # New position is full so choose a new random step
            else:
                directions.remove(step)  # Remove from future choices
                continue

            break

        return 1  # Person moved

    def infect(self, person):
        """See if an infectious person infects others.

        Args:
            person (int): The person who may infect others around them.

        Return:
            None
        """

        if self.pop[person].interaction_rate > 0:
            center = np.where(self.env == person)  # Position of the subject
            x_center, y_center = int(center[0]), int(center[1])
            n = self.env_dim
            # Radius of circle surrounding subject
            r = self.pop[person].interaction_rate

            # Create a mask to look for people surrounding the subject
            y, x = np.ogrid[-y_center: n-y_center, -x_center: n-x_center]
            mask = x*x + y*y <= r*r

            # Get environment indices of the mask
            mask_indices = np.where(mask)

            # Create a list of people in the circle surrounding the subject
            # who are not already infected
            persons = [int(x) for x in self.env[mask_indices]
                       if (x != np.Inf) and (
                           [self.pop[x].infected,
                            self.pop[x].recovered,
                            self.pop[x].alive
                            ] == [False, False, True])]

            # See if these people become infected
            for other_person in persons:
                if random() <= self.infection_rate:
                    self.pop[other_person].infected = True
                    self.pop[person].has_infected += 1

    def clean_up(self, remove_persons=True):
        """Traverse the environment and for each person do the following:
                - If someone is infected, then
                    - See if they are contagious yet
                        - If they are asymptomatic they have the defined 
                        interaction rate
                        - If they are symptomatic they have a random rounded
                        normalized interaction rate (mean: 1, sd: 0.25)
                    - See if they die
                        - If they do, remove them from the environment
                        - If not, advance their days_infected variable
                            - Check if they recover
                    - Save stats for the time step
        Args:
            remove_persons (bool): If True dead and recovered people are not
                removed from the environment. Useful for the PyGame
                visualization.

        Return:
            None
        """

        for ix, iy in np.ndindex(self.env.shape):
            if self.env[ix, iy] != np.Inf:  # Cell is occupied by a person
                person = self.env[ix, iy]

                # Check if person is alive, infected and hasn't recovered
                infectious_conditions = [
                    self.pop[person].alive,
                    self.pop[person].infected,
                    self.pop[person].recovered
                ]
                if infectious_conditions == [True, True, False]:
                    # It takes 48 hrs to become infectious
                    if self.pop[person].days_infected == 2:
                        # If they are asymptomatic they have a randomly
                        # assigned normally distributed interaction rate
                        if self.pop[person].asymptomatic:
                            int_rate = round(np.random.normal(
                                self.interaction_rate,
                                0.2 * self.interaction_rate))
                            if int_rate > 0:
                                self.pop[person].interaction_rate = int_rate
                            else:
                                self.pop[person].interaction_rate = 0
                        # Else person is symptomatic and thus either
                        # quarantines at home or is hospitalized (ie. lower
                        # interaction rate)
                        else:
                            int_rate = round(np.random.normal(0.75, 0.25))
                            if int_rate > 0:
                                self.pop[person].interaction_rate = int_rate
                            else:
                                self.pop[person].interaction_rate = 0

                    # See if the infected person dies
                    self.death_roll(person)
                    # If they died increment the total dead thus far variable
                    # and remove them from the environment if called for
                    if not self.pop[person].alive:
                        if remove_persons:
                            self.env[ix, iy] = np.Inf

                    # Else they didn't die so advance their days infected and
                    # check if they have recovered.
                    else:
                        self.pop[person].days_infected += 1
                        # Check if they recover and update their status if so
                        if self.pop[person].days_infected == \
                                self.pop[person].days_to_recover:
                            self.pop[person].recovered = True
                            self.pop[person].infected = False
                            self.recovered += 1  # Track total recovered
                            # Remove them from environment if called for
                            if remove_persons:
                                self.env[ix, iy] = np.Inf
        self.save_stats()

    def death_roll(self, person):
        """See if an infected person dies or not based on how many days they
        have been infected.

        Args:
            person (int): The person who may die.

        Return:
            None
        """

        days_infected = self.pop[person].days_infected

        # Normal distribution centered on median days it takes to die
        death_norm = norm(self.death_mean, self.death_sd)
        # Probability that someone will die given how many days they have
        # already been infected
        death_prob = self.mortality_rate * \
            (death_norm.cdf(days_infected) - death_norm.cdf(days_infected - 1))

        # See if they die
        if random() <= death_prob:
            self.pop[person].alive = False
            self.dead += 1

    def save_stats(self):
        """Save the number of infectious, recovered, and dead people in the
        population to the report dictionary.
        """

        self.report['infectious'].append(
            sum(
                [1 for person in self.pop if ([
                    self.pop[person].alive,
                    self.pop[person].infected,
                    self.pop[person].recovered
                ]) == [True, True, False]]
            )
        )

        self.report['recovered'].append(self.recovered)

        self.report['dead'].append(self.dead)

        self.report['not_infected'].append(
            self.pop_size -
            self.report['infectious'][-1] -
            self.report['recovered'][-1] -
            self.report['dead'][-1]
        )

    def calculate_r(self):
        """Calculate the R naught value of an infection simulation
        environment.
        """
        # Calculate R naught value for virus
        infected_total = 0
        infected_count = 0
        for person in self.pop.keys():
            if self.pop[person].recovered or not self.pop[person].alive:
                infected_total += self.pop[person].has_infected
                infected_count += 1

        # Don't allow a division by zero error
        if infected_total != 0:
            r_naught = round(infected_total / infected_count, 2)
        else:
            r_naught = 0

        return r_naught

    def run_basic_sim(self):
        """Run the infection simulation and save relevant statistics at each
        time step.
        """

        # Reset the report variable in case a previous simulation was run
        self.report = {
            'infectious': [self.initially_infected],
            'recovered': [0],
            'dead': [0],
            'not_infected': [self.pop_size - self.initially_infected],
            'r_naught': [0]
        }

        # For each epoch (time step) and for each person in the population,
        # if they are still alive and not recovered move them. If they are also
        # infected they have a chance to infect those around them.
        running = True
        epoch = 0
        while running:
            for person in self.pop:
                if (self.pop[person].alive, self.pop[person].recovered) == \
                        (True, False):
                    self.move(person)
                    if self.pop[person].infected:
                        self.infect(person)
            self.report['r_naught'].append(
                self.calculate_r()
            )

            # Perform the clean up phase
            self.clean_up()

            # Report simulation progress to user every 10 time steps (epochs)
            if epoch % 10 == 0:
                print(
                    f'\nR naught at time step {epoch + 1}: {self.calculate_r()}')
                print(
                    f'---\nCalculating time steps {epoch + 1} through {epoch + 10} ...')

            if epoch == 0 and self.time_steps == 0:
                epoch += 1
            elif self.report['infectious'][-1] == 0:
                running = False
                self.time_steps = epoch + 1
            elif epoch == self.time_steps:
                running = False
            else:
                epoch += 1

    def generate_plot(self, show=True, save=False):
        """Generate a plot from a simulation.

        Args:
            show (bool): Boolean for if user wants to show the plot
            save (bool): Boolean for is user wants to save the plot

        Return:
            None
        """

        # Collect the data for graphing
        time_steps = np.array(range(self.time_steps + 1))
        infectious = np.array(self.report['infectious'])
        recovered = np.array(self.report['recovered'])
        dead = np.array(self.report['dead'])
        not_infected = np.array(self.report['not_infected'])

        # Plot the data
        infectious, = plt.plot(
            time_steps, infectious, label=str(
                f'Infectious (end: {infectious[-1]} | max: {max(infectious)})'
            ))
        recovered, = plt.plot(
            time_steps, recovered, label=f'Recovered (end: {recovered[-1]})')
        dead, = plt.plot(time_steps, dead, label=f'Deceased (end: {dead[-1]})')
        not_infected, = plt.plot(
            time_steps, not_infected, label=f'Not infected (end: {not_infected[-1]})'
        )

        # Plot description
        plt_txt = str(
            'Simulation Parameters\n'
            f'Environment dimensions: {self.env_dim} x {self.env_dim}\n'
            f'Population size: {self.pop_size}\n'
            f'Initially infected: {self.initially_infected}\n'
            f'Interaction rate: {self.interaction_rate}\n'
            f'Time steps: {self.time_steps}'
        )

        # Set graph title, axis, and legend
        plt.title(
            'Infection Simulation Results'
        )
        plt.legend(handles=[infectious, recovered, dead, not_infected])
        plt.ylabel('Number of people')
        plt.xlabel(str(
            'Time\n\n' + plt_txt
        ))

        plt.subplots_adjust(bottom=0.35)

        # Save and show the graph if requested
        if save:
            plt.savefig(f'./{self}')
        if show:
            plt.show()
            plt.close()

    def __repr__(self):
        return str(
            f'Pop{self.pop_size}-'
            f'Env{self.env_dim}x{self.env_dim}-'
            f'InitInfect{self.initially_infected}-'
            f'IntRate{self.interaction_rate}'
        )


class Person:
    """A class for creating people to populate the Environment class with.
    """

    def __init__(self, recovery_mean,
                 recovery_sd):
        self.infected = False
        self.recovered = False
        self.alive = True
        self.interaction_rate = 0
        self.days_infected = 0
        self.has_infected = 0  # For calculating R naught value of virus
        self.days_to_recover = round(np.random.normal(
            recovery_mean, recovery_sd
        ))

        if random() <= 0.25:
            self.asymptomatic = True
        else:
            self.asymptomatic = False
