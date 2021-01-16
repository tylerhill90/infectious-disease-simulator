#!/usr/bin/env python3
"""
"""

import PySimpleGUI as sg

from pygame_sim import run_sim


simulation_parameters = [
    [sg.Text('Simulation Parameters', font=('Helvetica', 18))],
    [sg.Text('Population:'), sg.Slider(range=(100, 1000),
                                       default_value=1000,
                                       size=(20, 15),
                                       orientation='horizontal',
                                       font=('Helvetica', 12),
                                       key='pop')],
    [sg.Text('Initially infected:'), sg.Slider(range=(1, 100),
                                               default_value=3,
                                               size=(20, 15),
                                               orientation='horizontal',
                                               font=('Helvetica', 12),
                                               key='init_infected')],
    [sg.Text('Days until infectious:'), sg.Slider(range=(1, 7),
                                                  default_value=2,
                                                  size=(20, 15),
                                                  orientation='horizontal',
                                                  font=('Helvetica', 12),
                                                  key='days_until_infect')],
    [sg.Text('Interaction rate:'), sg.Slider(range=(0, 10),
                                             default_value=3,
                                             size=(20, 15),
                                             orientation='horizontal',
                                             font=('Helvetica', 12),
                                             key='interaction')],
    [sg.Text('Infection rate:'), sg.Slider(range=(0, 100),
                                           default_value=25,
                                           size=(20, 15),
                                           orientation='horizontal',
                                           font=('Helvetica', 12),
                                           key='infection')],
    [sg.Text('Mortality rate:'), sg.Slider(range=(0, 100),
                                           default_value=2,
                                           size=(20, 15),
                                           orientation='horizontal',
                                           font=('Helvetica', 12),
                                           key='mortality')],
    [sg.Text('Asymptomatic rate:'), sg.Slider(range=(0, 100),
                                              default_value=25,
                                              size=(20, 15),
                                              orientation='horizontal',
                                              font=('Helvetica', 12),
                                              key='asymp')],
    [sg.Text('''Note: Symptomatic persons will have a lower interaction
 rate on average compared to asymptomatic persons.''')],
    [sg.Button('Run Simulation'), sg.Button('Quit')]

]

window = sg.Window('Infectious Disease Simulator', simulation_parameters)

while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event in (sg.WINDOW_CLOSED, 'Quit'):
        break
    elif event == 'Run Simulation':
        env_params = {
            'time_steps': 0,
            'env_dim': 100,
            'pop_size': int(values['pop']),
            'initially_infected': int(values['init_infected']),
            'interaction_rate': int(values['interaction']),
            'infection_rate': values['infection'] / 100,
            'mortality_rate': values['mortality'] / 100,
            'recovery_mean': 19,
            'recovery_sd': 3,
            'asymptomatic_prob': values['asymp'] / 100,
            'days_until_infectious': int(values['days_until_infect'])
        }
        print(env_params)
        run_sim(env_params)


# Finish up by removing from the screen
window.close()
