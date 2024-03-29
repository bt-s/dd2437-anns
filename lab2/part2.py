#!/usr/bin/python3

"""part2.py Containing the code for the seocnd part of lab 2

For the DD2437 Artificial Neural Networks and Deep Architectures course at KTH
Royal Institute of Technology"""

__author__ = "Anton Anderzén, Stella Katsarou, Bas Straathof"


import numpy as np
from helper import *
from algorithms.som import SOM

np.random.seed(42)

PROBLEM_4_1 = False
PROBLEM_4_2 = False
PROBLEM_4_3 = True

if PROBLEM_4_1:
    animal_props = get_animal_data("data_lab2/animals.dat")
    assert animal_props.shape == (32, 84)

    animal_names = get_animal_names('data_lab2/animalnames.txt')
    assert len(animal_names) == 32

    X = {"props": animal_props, "names": animal_names}

    som = SOM(epochs=20)
    som.initialize_weights(X["props"])
    som.train(X)

if PROBLEM_4_2:
    X = get_cities("data_lab2/cities.dat")
    assert X.shape == (10, 2)

    names = ["A", "B", "C", "D", "E", "F","G", "H", "I","J"]

    som = SOM(h=10, epochs=4, initial_neighborhood=6, problem=2)
    som.initialize_weights(X)
    som.train(X, names)
    plot_cities(X, names, 'SOM-generated salesman path', "plots/cities.pdf",
            save_plot=True)

if PROBLEM_4_3:
    X = get_votes("data_lab2/votes.dat")
    names = get_names("data_lab2/mpnames.txt")
    districts = get_districts("data_lab2/mpdistrict.dat")
    parties = get_parties("data_lab2/mpparty.dat")
    sexes = get_sex("data_lab2/mpsex.dat")

    # Sanity checks
    assert X.shape == (349, 31)
    assert len(names) == 349
    assert len(districts) == 349
    assert len(parties) == 349
    assert len(sexes) == 349

    som = SOM(h=100, epochs=4, initial_neighborhood=12, problem=3)
    som.initialize_weights(X)
    som.train(X, names, districts, parties, sexes )

