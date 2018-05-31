import numpy as np
import pandas as pd
import pickle

class FlagDF:
    def __init__(self):
        self.second = None      # (n seconds,)
        self.flags = None       # (n seconds, n flags)
        self.filename = None
        self.input_fn = None
        self.channels = None
    
    def save(self):
        s = {'input_fn': self.input_fn, 'second': self.second, 'flags': self.flags, 'channels':self.channels}
        pickle.dump(s, open(self.filename, 'wb'))
    
    def load_from_file(filename, input_fn):
        f = pickle.load( open(filename, 'rb') )
        if f['input_fn'] != input_fn:
            return

        self.filename = filename
        self.input_fn = input_fn
        self.second = f['second']
        self.flags = f['flags']
        self.channels = f['channels']
