class Config(object):
    def __init__(self):
        super(Config, self).__init__()
        #  ------------ General options ----------------------------------------
        self.save_path = "./plate_annotations/rnet/"
        self.dataPath = "/users/maqiao/DNN/MTCNN/data20180925"  # path for loading data set
        self.annoPath = "./plate_annotations/imglist_anno_24.txt"
        self.manualSeed = 1  # manually set RNG seed
        self.use_cuda = True
        self.GPU = "1"  # default gpu to use

        # ------------- Data options -------------------------------------------
        self.nThreads = 8  # number of data loader threads

        # ---------- Optimization options --------------------------------------
        self.nEpochs = 50  # number of total epochs to train 400
        self.batchSize = 512  # mini-batch size 128

        # lr master for optimizer 1 (mask vector d)
        self.lr = 0.001  # initial learning rate
        self.step = [10, 25, 40]  # step for linear or exp learning rate policy
        self.decayRate = 0.1  # lr decay rate
        self.endlr = -1

        # ---------- Model options ---------------------------------------------
        self.experimentID = "0930"

        # ---------- Resume or Retrain options ---------------------------------------------
        self.resume = None  # "./checkpoint_064.pth"
        self.retrain = None

        self.save_path = self.save_path + "log_bs{:d}_lr{:.3f}_{}/".format(self.batchSize, self.lr, self.experimentID)