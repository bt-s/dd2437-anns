#!/usr/bin/python3

"""run.py - The main file for lab 4.

For the DD2437 Artificial Neural Networks and Deep Architectures course at KTH
Royal Institute of Technology

Note: Part of this code was provided by the course coordinators.
"""

__author__ = "Anton Anderzén, Stella Katsarou, Bas Straathof"


from util import *
from rbm import RestrictedBoltzmannMachine
from dbn import DeepBeliefNet

PLOTS = False

if __name__ == "__main__":
    # Fix the dimensions of the images
    image_size = [28, 28]

    # Load the MNIST data into numpy arrays
    train_imgs, train_lbls, test_imgs, test_lbls = read_mnist(
            dim=image_size, n_train=60000, n_test=10000)

    # The labels are stored as one-hot-encoded vectors
    # Let's also store them in digit format
    train_lbls_digits = np.argmax(train_lbls, axis=1)
    test_lbls_digits = np.argmax(test_lbls, axis=1)

    if PLOTS:
        # Training set class histogram
        create_histogram(train_lbls_digits, bins=19,
                title="Class distribution of the training data",
                ylabel="Occurences", xlabel="Class")

        # Test set class histogram
        create_histogram(test_lbls_digits, bins=19,
                title="Class distribution of the test data",
                ylabel="Occurences", xlabel="Class")

        # Visualize the first 10 digits
        for i in range(10):
            plot_digit(train_imgs[i], train_lbls_digits[i])


    # Restricted Boltzmann Machine
    print ("\nStarting a Restricted Boltzmann Machine...")

    rbm = RestrictedBoltzmannMachine(ndim_visible=image_size[0] * image_size[1],
            ndim_hidden=500, is_bottom=True, image_size=image_size, is_top=False,
            n_labels=10, batch_size=20)

    # First train on the first 400 images
    train_imgs = train_imgs[:400, :]
    rbm.cd1(X=train_imgs, n_iterations=30000)

    # We do not always want to run everything in this main file
    if False:
        # Deep Belief Net
        print ("\nStarting a Deep Belief Net...")

        dbn = DeepBeliefNet(sizes={"vis":image_size[0]*image_size[1], "hid":500,
            "pen":500, "top":2000, "lbl":10}, image_size=image_size, n_labels=10,
            batch_size=10)

        # Greedy layer-wise training
        dbn.train_greedylayerwise(vis_trainset=train_imgs, lbl_trainset=train_lbls,
                n_iterations=2000)

        dbn.recognize(train_imgs, train_lbls)
        dbn.recognize(test_imgs, test_lbls)

        for digit in range(10):
            digit_1hot = np.zeros(shape=(1, 10))
            digit_1hot[0, digit] = 1
            dbn.generate(digit_1hot, name="rbms")

        # Fine-tune wake-sleep training
        dbn.train_wakesleep_finetune(vis_trainset=train_imgs, lbl_trainset=train_lbls,
                n_iterations=2000)

        dbn.recognize(train_imgs, train_lbls)
        dbn.recognize(test_imgs, test_lbls)

        for digit in range(10):
            digit_1hot = np.zeros(shape=(1, 10))
            digit_1hot[0, digit] = 1
            dbn.generate(digit_1hot, name="dbn")

