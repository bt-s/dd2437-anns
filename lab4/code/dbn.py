#!/usr/bin/python3

"""dbn.py - Containing the DeepBeliefNet class.

For the DD2437 Artificial Neural Networks and Deep Architectures course at KTH
Royal Institute of Technology

Note: Part of this code was provided by the course coordinators.
"""

__author__ = "Anton Anderzén, Stella Katsarou, Bas Straathof"


from util import *
from rbm import RestrictedBoltzmannMachine as RBM


class DeepBeliefNet():
    """A Deep Belief Net

    network          : [top] <---> [pen] ---> [hid] ---> [vis]
                               `-> [lbl]
    lbl : label
    top : top
    pen : penultimate
    hid : hidden
    vis : visible"""

    def __init__(self, sizes, image_size, n_labels, batch_size):
        """Class Constructior
        Args:
            sizes (dict): Dictionary of layer names and dimensions
            image_size (list): Image dimension of data
            n_labels (int): Number of label categories
            batch_size (int): Size of mini-batch
        """

        self.rbm_stack = {
            'vis--hid': RBM(ndim_visible=sizes["vis"], ndim_hidden=sizes["hid"],
                is_bottom=True, image_size=image_size, batch_size=batch_size),

            'hid--pen': RBM(ndim_visible=sizes["hid"], ndim_hidden=sizes["pen"],
                batch_size=batch_size),

            'pen+lbl--top': RBM(ndim_visible=sizes["pen"] + sizes["lbl"],
                ndim_hidden=sizes["top"], is_top=True, n_labels=n_labels,
                batch_size=batch_size)
        }

        self.sizes = sizes
        self.image_size = image_size
        self.batch_size = batch_size
        self.n_gibbs_recog = 15
        self.n_gibbs_gener = 200
        self.n_gibbs_wakesleep = 5
        self.print_period = 2000


    def recognize(self, true_img, true_lbl):
        """Recognize/Classify the data into label categories and calc accuracy

        Args:
          true_imgs (np.ndarray): visible data of shape (number of samples,
                                  size of visible layer)
          true_lbl (np.ndarray): true labels of shape (number of samples,
                                 size of label layer). Used only for calculating
                                 accuracy, not driving the net
        """
        n_samples = true_img.shape[0]

        # Visible layer gets the image data
        vis = true_img

        # Start the net by telling you know nothing about labels
        lbl = np.ones(true_lbl.shape)/10.

        for _ in range(self.n_gibbs_recog):
            pass

        predicted_lbl = np.zeros(true_lbl.shape)

        print ("accuracy = %.2f%%" % (100. * np.mean(np.argmax(
            predicted_lbl, axis=1) == np.argmax(true_lbl, axis=1))))

        return


    def generate(self, true_lbl,name):
        """Generate data from labels

        Args:
          true_lbl (np.ndarray): true labels shaped (number of samples,
                                 size of label layer)
          name (str): used for saving a video of generated visible activations
        """
        n_sample, records = true_lbl.shape[0], []
        fig,ax = plt.subplots(1,1,figsize=(3,3))
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        ax.set_xticks([]); ax.set_yticks([])

        lbl = true_lbl

        for _ in range(self.n_gibbs_gener):
            vis = np.random.rand(n_sample,self.sizes["vis"])
            records.append([ax.imshow(vis.reshape(self.image_size), cmap="bwr",
                vmin=0, vmax=1, animated=True, interpolation=None)])

        anim = stitch_video(fig,records).save("plots_and_animations/%s.generate%d.mp4" %
                (name,np.argmax(true_lbl)))

        return


    def train_greedylayerwise(self, vis_trainset, lbl_trainset, n_iterations):
        """Greedy layer-wise training by stacking RBMs. This method first tries
        to load previous saved parameters of the entire RBM stack.
        If not found, learns layer-by-layer (which needs to be completed) .

        Notice that once you stack more layers on top of a RBM, the weights are
        permanently untwined.

        Args:
          vis_trainset (np.ndarray): Visible data shaped (size of training set,
                                     size of visible layer)
          lbl_trainset (np.ndarray): Label data shaped (size of training set,
                                     size of label layer)
          n_iterations (int): number of iterations of learning (each iteration
                              learns a mini-batch)
        """
        try :
            self.loadfromfile_rbm(loc="trained_rbm",name="vis--hid")
            self.rbm_stack["vis--hid"].untwine_weights()

            self.loadfromfile_rbm(loc="trained_rbm",name="hid--pen")
            self.rbm_stack["hid--pen"].untwine_weights()

            self.loadfromfile_rbm(loc="trained_rbm",name="pen+lbl--top")

        except IOError :
            print ("training vis--hid")

            # CD-1 training for vis--hid
            self.rbm_stack["vis--hid"].cd1(vis_trainset ,n_iterations=n_iterations)

            self.savetofile_rbm(loc="trained_rbm",name="vis--hid")

            print ("training hid--pen")

            # Initialize the weights of hid--pen to the learned vis--hid weights before untwining.
            """
            ' To guarantee that the generative model is improved by greedily learning more layers,
             it is convenient to consider models in which all layers are the same size so that 
             the higherlevel weights can be initialized to the values learned before
             they are untied from the weights in the layer below. '
            """
            self.rbm_stack["hid--pen"].weight_vh = self.rbm_stack["vis--hid"].weight_vh
            self.rbm_stack["hid--pen"].weight_v_to_h = self.rbm_stack["vis--hid"].weight_v_to_h
            self.rbm_stack["hid--pen"].weight_h_to_v = self.rbm_stack["vis--hid"].weight_h_to_v

            # Untwine weights
            self.rbm_stack["vis--hid"].untwine_weights()

            # CD-1 training for hid--pen
            self.rbm_stack["vis--hid"].cd1(vis_trainset, n_iterations=n_iterations)
            self.savetofile_rbm(loc="trained_rbm",name="hid--pen")

            print ("training pen+lbl--top")

            # Initialize the weights of pen+lbl--top to the learned hid--pen weights before untwining.
            self.rbm_stack["pen+lbl--top"].weight_vh = self.rbm_stack["hid--pen"].weight_vh
            self.rbm_stack["pen+lbl--top"].weight_v_to_h = self.rbm_stack["hid--pen"].weight_v_to_h
            self.rbm_stack["pen+lbl--top"].weight_h_to_v = self.rbm_stack["hid--pen"].weight_h_to_v

            self.rbm_stack["hid--pen"].untwine_weights()

            # CD-1 training for pen+lbl--top
            self.rbm_stack["pen+lbl--top"].cd1(np.hstack(vis_trainset,lbl_trainset), n_iterations=n_iterations)
            self.savetofile_rbm(loc="trained_rbm", name="pen+lbl--top")

        return


    def train_wakesleep_finetune(self, vis_trainset, lbl_trainset, n_iterations):
        """Wake-sleep method for learning all the parameters of network.
        First tries to load previous saved parameters of the entire network.

        Args:
          vis_trainset (np.ndarray): visible data shaped (size of training set,
                                     size of visible layer)
          lbl_trainset (np.ndarray): label data shaped (size of training set,
                                     size of label layer)
          n_iterations (int): number of iterations of learning (each iteration
                              learns a mini-batch)
        """
        print ("\nTraining wake-sleep...")

        try :
            self.loadfromfile_dbn(loc="trained_dbn",name="vis--hid")
            self.loadfromfile_dbn(loc="trained_dbn",name="hid--pen")
            self.loadfromfile_rbm(loc="trained_dbn",name="pen+lbl--top")

        except IOError :
            self.n_samples = vis_trainset.shape[0]

            for it in range(n_iterations):
                # wake-phase : drive the network bottom-to-top using visible
                # and label data

                # alternating Gibbs sampling in the top RBM : also store
                # neccessary information for learning this RBM

                # sleep phase : from the activities in the top RBM, drive the
                # network top-to-bottom

                # predictions : compute generative predictions from wake-phase
                # activations, and recognize predictions from sleep-phase
                # activations

                # update generative parameters :
                # here you will only use "update_generate_params" method from
                # rbm class

                # update parameters of top rbm:
                # here you will only use "update_params" method from rbm class

                # update generative parameters :
                # here you will only use "update_recognize_params" method from
                # rbm class

                if it % self.print_period == 0 : print ("iteration=%7d"%it)

            self.savetofile_dbn(loc="trained_dbn",name="vis--hid")
            self.savetofile_dbn(loc="trained_dbn",name="hid--pen")
            self.savetofile_rbm(loc="trained_dbn",name="pen+lbl--top")

        return


    def loadfromfile_rbm(self, loc, name):
        """Load RBM from file

        Args:
            loc (str): The location of the file
            name (str): Name of RBM
        """
        self.rbm_stack[name].weight_vh = np.load(f"{loc}/rbm.{name}.weight_vh.npy")
        self.rbm_stack[name].bias_v    = np.load(f"{loc}/rbm.{name}.bias_v.npy")
        self.rbm_stack[name].bias_h    = np.load(f"{loc}/rbm.{name}.bias_h.npy")
        print(f"Loaded rbm[{name}] from {loc}.")


    def savetofile_rbm(self, loc, name):
        """Save RBM to file

        Args:
            loc (str): The location of the file
            name (str): Name of RBM
        """
        np.save(f"{loc}/rbm.{name}.weight_vh", self.rbm_stack[name].weight_vh)
        np.save(f"{loc}/rbm.{name}.bias_v", self.rbm_stack[name].bias_v)
        np.save(f"{loc}/rbm.{name}.bias_h", self.rbm_stack[name].bias_h)


    def loadfromfile_dbn(self, loc, name):
        """Load DBN from file

        Args:
            loc (str): The location of the file
            name (str): Name of RBM
        """
        self.rbm_stack[name].weight_v_to_h = np.load(f"{loc}/dbn.{name}.weight_v_to_h.npy")
        self.rbm_stack[name].weight_h_to_v = np.load(f"{loc}/dbn.{name}.weight_h_to_v.npy")
        self.rbm_stack[name].bias_v        = np.load(f"{loc}/dbn.{name}.bias_v.npy")
        self.rbm_stack[name].bias_h        = np.load(f"{loc}/dbn.{name}.bias_h.npy")
        print(f"Loaded rbm[{name}] from {loc}.")


    def savetofile_dbn(self, loc, name):
        """Save DBN to file

        Args:
            loc (str): The location of the file
            name (str): Name of RBM
        """
        np.save(f"{loc}/dbn.{name}.weight_v_to_h", self.rbm_stack[name].weight_v_to_h)
        np.save(f"{loc}/dbn.{name}.weight_h_to_v", self.rbm_stack[name].weight_h_to_v)
        np.save(f"{loc}/dbn.{name}.bias_v",        self.rbm_stack[name].bias_v)
        np.save(f"{loc}/dbn.{name}.bias_h",        self.rbm_stack[name].bias_h)

