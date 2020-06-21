"""Classes for running simple infection simulations.
"""

import numpy as np
from scipy.stats import norm
from random import random, choice
import sys
import matplotlib.pyplot as plt


class Environment:
    """A class for setting up and running the infection simulation.
    """

    def __init__(self, env_params):

        # Unpack user given environment parameters
        self.time = env_params['time']
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
            'not_infected': [self.pop_size - self.initially_infected]
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
        infected and non-infected people with no overlap.
        """

        # Error check user
        if self.pop_size > self.env_dim ** 2:
            sys.exit('Population larger than environment can support.')

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
            None
        """

        position = np.where(self.env == person)  # Current position in env
        directions = [
            [-1, 1], [0, 1], [1, 1],
            [-1, 0], [1, 0],
            [-1, -1], [0, -1], [1, -1]
        ]
        while True:
            if directions == []:
                break
            step = choice(directions)
            directions.remove(step)
            new_position = [position[0] + step[0],
                            position[1] + step[1]]

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
                continue

            break

    def infect(self, person):
        """See if an infectious person infects others.

        Args:
            person (int): The person who may infect others around them.

        Return:
            None
        """

        center = np.where(self.env == person)  # Position of the subject
        x_center, y_center = int(center[0]), int(center[1])
        n = self.env_dim
        r = self.interaction_rate  # Radius of circle surrounding subject

        # Create a mask to look for people surrounding the subject
        y, x = np.ogrid[-y_center: n-y_center, -x_center: n-x_center]
        mask = x*x + y*y < r*r

        # Get environment indices of the mask
        mask_indices = np.where(mask == True)

        # Create a list of people in the circle surrounding the subject
        persons = [x for x in self.env[mask_indices] if x != np.Inf]

        # See if these people become infected
        for subject in persons:
            if self.pop[subject].infected == False:
                if random() <= self.infection_rate:
                    self.pop[subject].infected = True

    def clean_up(self, remove_persons=True):
        """Traverse the environment and for each person do the following:
                - If someone is infected, then
                    - See if they die
                        - If they do, remove them from the environment
                        - If not, advance their days_infected variable
                            - Check if they recover
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
                clean_up_conditions = [
                    self.pop[person].alive,
                    self.pop[person].infected,
                    self.pop[person].recovered
                ]
                if clean_up_conditions == [True, True, False]:
                    # See if the infected person dies
                    self.death_roll(person)
                    # Remove them from the environment if they died
                    if self.pop[person].alive == False:
                        self.dead += 1
                        if remove_persons:
                            self.env[ix, iy] = np.Inf
                    # Else they didn't die so advance their days infected and
                    # check if they have recovered. Remove them if they have.
                    else:
                        self.pop[person].days_infected += 1
                        if self.pop[person].days_infected == \
                                self.pop[person].days_to_recover:
                            self.pop[person].recovered = True
                            self.pop[person].infected = False
                            self.recovered += 1
                            if remove_persons:
                                self.env[ix, iy] = np.Inf

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

    def run_basic_sim(self):
        """Run the infection simulation and save relevant statistics at each
        time step.
        """

        # Reset the report variable in case a previous simulation was run
        self.report = {
            'infectious': [self.initially_infected],
            'recovered': [0],
            'dead': [0],
            'not_infected': [self.pop_size - self.initially_infected]
        }

        # For each epoch (time step) and for each person in the population,
        # if they are still alive and not recovered move them. If they are also
        # infected they have a chance to infect those around them.
        for epoch in range(self.time):
            for person in self.pop:
                if (self.pop[person].alive, self.pop[person].recovered) == \
                        (True, False):
                    self.move(person)
                    if self.pop[person].infected == True:
                        self.infect(person)

            # Perform the clean up phase
            self.clean_up()

            # Report simulation progress to user every 10 time steps (epochs)
            if epoch % 10 == 0:
                print(
                    f'Calculating time steps {epoch + 1} through {epoch + 10} '
                    f'/ {self.time} ...')

            # Save stats for graphing each epoch
            self.save_stats()

    def generate_plot(self, show=True, save=False):
        """Generate a plot from a simulation.

        Args:
            show (bool): Boolean for if user wants to show the plot
            save (bool): Boolean for is user wants to save the plot

        Return:
            None
        """

        # Collect the data for graphing
        time = np.array(range(self.time + 1))
        infectious = np.array(self.report['infectious'])
        recovered = np.array(self.report['recovered'])
        dead = np.array(self.report['dead'])
        not_infected = np.array(self.report['not_infected'])

        # Plot the data
        infectious, = plt.plot(
            time, infectious, label=str(
                f'Infectious (end: {infectious[-1]} | max: {max(infectious)})'
            ))
        recovered, = plt.plot(
            time, recovered, label=f'Recovered (end: {recovered[-1]})')
        dead, = plt.plot(time, dead, label=f'Deceased (end: {dead[-1]})')
        not_infected, = plt.plot(
            time, not_infected, label=f'Not infected (end: {not_infected[-1]})'
        )

        # Set graph title, axis, and legend
        plt.title(
            f'Infection Simulation Results'
        )
        plt.ylabel('Number of people')
        plt.xlabel('Time')
        plt.legend(handles=[infectious, recovered, dead, not_infected])

        # Plot description
        plt_txt = str(
            f'This simulation was run in a {self.env_dim}x{self.env_dim} '
            f'environment with a population size of {self.pop_size}, with '
            f'{self.initially_infected} initially infected people. '
            f'An interaction rate of {self.interaction_rate} was used and '
            f'the simulation was run for {self.time} time steps.'
        )

        # Add the plot description below x-axis
        plt.subplots_adjust(bottom=0.4)
        plt.figtext(0.5, 0.175, plt_txt, wrap=True,
                    ha='center', va='bottom', fontsize=10)

        # Save and show the graph if requested
        if save == True:
            plt.savefig(f'./{self}')
        if show == True:
            plt.show()
            plt.close()

    def __repr__(self):
        return str(f'Pop{self.pop_size}-'
                   f'Env{self.env_dim}x{self.env_dim}-'
                   f'InitInfect{self.initially_infected}-'
                   f'IntRate{self.interaction_rate}'
                   '.png')


class Person:
    """A class for creating people to populate the Environment class with.
    """

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
