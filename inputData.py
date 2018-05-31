# store input data information
class InputData:
    def __init__(self):
        self.num_channels = -1  # n of channels
        self.frequency = -1
        self.length = -1      
        self.sigbuf = None      # data
        self.labels = None      # label names
