import numpy as np
import pandas as pd
import pickle

class OutputDF:
    def __init__(self):
        self.bad = []
        self.responses = None
        self.labels = []
        self.now_displaying = -1
        self.filename = None
        self.input_fn = None
    
    def save(self):
        responses = np.array(self.responses)
        labels = [np.array_str(i) for i in self.labels]
        df = pd.DataFrame({"bad seconds" : self.bad, "response" : responses, "labels" : labels})
        a = {'filename': self.input_fn, 'df': df}
        # df.to_csv(self.filename, index=False)
        pickle.dump(a, open(self.filename, 'wb'))
    
    def update_one(self, r, start):
        if not start:
            self.responses[self.now_displaying] = r
        self.now_displaying += 1
        if self.now_displaying >= len(self.bad):
            self.save()
            return True
        return False
        