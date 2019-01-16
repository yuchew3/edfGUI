import numpy as np
import pickle

# store response information
class OutputDF:
    def __init__(self):
        self.bad = []
        self.responses = None
        self.channels = []
        self.now_displaying = -1
        self.filename = None
        self.input_fn = None
        self.flag_fn = None
    
    # save current resposnes to a pickle file (*.response)
    def save(self):
        a = {'input_fn': self.input_fn, 'flag_fn':self.flag_fn, 'bad':self.bad, 'responses':self.responses, 'channels':self.channels}
        pickle.dump(a, open(self.filename, 'wb'))
    
    # update one response for the "now_displaying th" data
    def update_one(self, r, start):
        if not start:
            self.responses[self.now_displaying] = r
        self.now_displaying += 1
        if self.now_displaying >= len(self.bad):
            self.save()
            return True
        return False

    # load from a response file
    def load_response(self, response_name, input_fn, flag_fn=None):
        y = pickle.load( open(response_name, 'rb') )
        # if the response file is not the one corresponding to the input file or flag file
        # just leave everything None
        if y['input_fn'] != input_fn or y['flag_fn'] != flag_fn:
            print(y['input_fn'])
            print(input_fn)
            return

        self.filename = response_name
        self.input_fn = input_fn
        self.flag_fn = flag_fn
        self.bad = y['bad']
        self.responses = y['responses']
        self.channels = y['channels']

        # find the first -1 (i.e. not answered) in responses
        n = 0
        try:
            n = self.responses.tolist().index(-1)
        except ValueError:
            n = 0
        self.now_displaying = n - 1   # is there better way?
    
    # create a new response file based on a given flag file
    def create_on_flag(self, flag_df):
        self.input_fn = flag_df.input_fn
        self.flag_fn = flag_df.filename
        self.bad = flag_df.second
        self.responses = -1 * np.ones(len(self.bad))
        self.channels = flag_df.channels
    
    # create a new response file based on the input data and some criteria
    def create_on_input(self, input_data, input_fn):
        self.input_fn = input_fn
        seconds = input_data.length / input_data.frequency
        if input_data.length%input_data.frequency != 0:
            seconds += 1
        seconds = int(seconds)
        print(seconds, ' seconds in total')

        outlier_points = np.abs(input_data.sigbuf) > 5

        # check if one point is an outlier
        def check_bad(i, outlier_points):
            lo = int(i * input_data.frequency)
            hi = int(lo + input_data.frequency)
            if hi > input_data.length:
                hi = input_data.length
            labels = np.zeros(input_data.num_channels)
            t_idx = np.arange(lo, hi)
            return np.sum(outlier_points[:, t_idx], axis=1) > 0.2 * input_data.frequency

        y = np.zeros((seconds, input_data.num_channels))
        for i in xrange(seconds):
            y[i, :] = check_bad(i, outlier_points)
            if np.sum(y[i, :]) > 0:
                self.bad.append(i)
                self.channels.append(y[i, :])

        self.responses = -np.ones(len(self.bad))


        