from output import OutputDF
from inputData import InputData
import utils

import pyedflib
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import types
import h5py
import pickle

def load_file(filename):
    if filename[-3:] == '.h5':
        print "h5 file!"
        return load_h5_file(filename)
    try:
        f = pyedflib.EdfReader(filename)
    except:
        return None
    input_data = InputData()
    input_data.num_channels = f.signals_in_file
    input_data.labels = f.getSignalLabels()
    input_data.frequency = f.samplefrequency(0)
    input_data.sigbuf = np.zeros((input_data.num_channels, f.getNSamples()[0]))
    input_data.length = f.getNSamples()[0]

    for i in range(input_data.num_channels):
        print("loading " + str(i) + ", signal: " + input_data.labels[i])
        input_data.sigbuf[i, :] = f.readSignal(i)
        mean = np.mean(input_data.sigbuf[i])
        std = np.std(input_data.sigbuf[i])
        input_data.sigbuf[i, :] = (input_data.sigbuf[i, :] - mean) / std
    
    return input_data

def load_h5_file(filename):
    fin = h5py.File(filename, 'r')

    input_data = InputData()
    input_data.sigbuf = fin['dataset'][:]
    input_data.num_channels = len(input_data.sigbuf)
    input_data.frequency = fin['f_sample'][()]
    input_data.length = len(input_data.sigbuf[0])
    return input_data

def load_response(response_name, input_fn):
    # y = pd.read_csv(response_name)
    y = pickle.load( open(response_name, 'rb') )
    if not y['filename'] == input_fn:
        print y['filename']
        print input_fn
        return None
    print y['filename']
    y = y['df']
    # y = y['df']

    output_df = OutputDF()
    output_df.filename = response_name
    output_df.input_fn = input_fn
    output_df.bad = y['bad seconds'].values
    print output_df.bad.shape
    output_df.responses = y['response'].values
    print output_df.responses.shape
    output_df.labels = y['labels'].values
    output_df.labels = [np.fromstring(n[1:-1], sep=' ') for n in output_df.labels]
    output_df.labels = np.array(output_df.labels)
    print output_df.labels.shape
    n = 0
    try:
        n = output_df.responses.tolist().index(-1)
    except ValueError:
        n = 0
    output_df.now_displaying = n - 1   # is there better way?

    return output_df

def find_bad(input_data, input_fn):
    output_df = OutputDF()
    output_df.input_fn = input_fn
    seconds = input_data.length / input_data.frequency
    if input_data.length%input_data.frequency != 0:
        seconds += 1
    seconds = int(seconds)
    print seconds, ' seconds in total'

    outlier_points = np.abs(input_data.sigbuf) > 5

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
            output_df.bad.append(i)
            output_df.labels.append(y[i, :])

    output_df.responses = -np.ones(len(output_df.bad))
    return output_df

class X_Pan_Axes(matplotlib.axes.Axes):
    name = "X_Pan_Axes"
    def drag_pan(self, button, key, x, y):
        # pretend key=='x'
        matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y)
matplotlib.projections.register_projection(X_Pan_Axes)

def constrainXPanZoomBehavior(fig):
    # ensure figure toolbars call a postPressZoomHandler()
    def overrideZoomMode(oldZoom, target):
        def newZoom(self, event):
            oldZoom(self, event)
            if hasattr(self, 'postPressZoomHandler'):
                self.postPressZoomHandler()
        return newZoom
    def overrideToolbarZoom(fig, methodname, functransform, *args):
        toolbar = fig.canvas.toolbar
        oldMethod = getattr(toolbar.__class__, methodname)
        newMethod = functransform(oldMethod, toolbar, *args)
        setattr(toolbar.__class__, methodname, newMethod)
    overrideToolbarZoom(fig, 'press_zoom', overrideZoomMode)

    # for this specific instance, override the zoom mode to 'x' always
    def postPressZoomHandler(self):
        self._zoom_mode = 'x'
    fig.canvas.toolbar.postPressZoomHandler = \
      types.MethodType(postPressZoomHandler, fig.canvas.toolbar)
    return fig

def draw_selected(selected, input_data, output_df):
    i = output_df.bad[output_df.now_displaying]
    vlines = [i, i+1]
    margin = 0.2
    frequency = input_data.frequency
    lo = i*frequency - margin*frequency
    if lo < 0:
        lo = 0
    hi = (i+1)*frequency + margin*frequency
    if hi > input_data.length:
        hi = input_data.length
    lo = int(lo)
    hi = int(hi)
    t_idx = np.arange(lo, hi)
    X = range(lo, hi)
    X=[i*1.0/frequency for i in X]
    amp_scale = 3.5

    fig, ax1 = plt.subplots(1, 1, subplot_kw=dict(projection="X_Pan_Axes"))
    fig = constrainXPanZoomBehavior(fig)
    i = 1
    for chan in selected:
        height = (i*1.0 / (len(selected)+1)) * input_data.num_channels
        ax1.plot(X, height*10 + amp_scale * input_data.sigbuf[chan, t_idx].T,
                             lw=0.5)
    	i += 1
    ax1.set_ylim(-10, (input_data.num_channels+1)*10)
    ax1.set_xlim(X[0], X[-1])
    for x in vlines:
        ax1.axvline(x=x, ls='--', color='k')

    return fig

def draw_figure(input_data, output_df):
    i = output_df.bad[output_df.now_displaying]
    vlines = [i, i+1]
    margin = 0.2
    frequency = input_data.frequency
    lo = i*frequency - margin*frequency
    if lo < 0:
        lo = 0
    hi = (i+1)*frequency + margin*frequency
    if hi > input_data.length:
        hi = input_data.length
    lo = int(lo)
    hi = int(hi)
    t_idx = np.arange(lo, hi)
    X = range(lo, hi)
    X=[i*1.0/frequency for i in X]
    bad_channels = np.where(output_df.labels[output_df.now_displaying])[0]
    print bad_channels
    amp_scale = 3.5
    
    
    fig, (ax1, ax2) =  \
              plt.subplots(2, 1, sharex=True,
                            subplot_kw = dict(projection="X_Pan_Axes") )
    # DPI = fig.get_dpi()
    # fig.set_size_inches(float(width*0.8)/DPI, float(height*0.8)/DPI)
    fig = constrainXPanZoomBehavior(fig)
    for chan in xrange(input_data.num_channels):
        ax1.plot(X, chan*10 + amp_scale * input_data.sigbuf[chan, t_idx].T,
                             lw=0.5)
    i = 1
    for chan in bad_channels:
        height = (i*1.0 / (len(bad_channels)+1)) * input_data.num_channels
        ax2.plot(X, height*10 + amp_scale * input_data.sigbuf[chan, t_idx].T,
                             lw=0.5)
        i += 1
    ax1.set_ylim(-10, (input_data.num_channels+1)*10)
    ax2.set_ylim(-10, (input_data.num_channels+1)*10)
    ax1.set_xlim(X[0], X[-1])
    for x in vlines:
        ax1.axvline(x=x, ls='--', color='k')
        ax2.axvline(x=x, ls='--', color='k')

    return fig


