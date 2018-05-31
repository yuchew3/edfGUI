from output import OutputDF
from inputData import InputData
import utils

import pyedflib
import numpy as np
import pandas as pd
import math
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
    # amp_scale = 3.5

    fig, ax1 = plt.subplots(1, 1, subplot_kw=dict(projection="X_Pan_Axes"))
    fig = constrainXPanZoomBehavior(fig)
    i = 1
    for chan in selected:
        variance = np.var(input_data.sigbuf[chan, t_idx])
        print variance
        variance = 7.0 / (1 + math.exp(-variance))
        print variance
        height = (i*1.0 / (len(selected)+1)) * input_data.num_channels
        ax1.plot(X, height*10 + variance * input_data.sigbuf[chan, t_idx].T,
                             lw=0.5)
    	i += 1
    ax1.set_ylim(-10, (input_data.num_channels+1)*10)
    ax1.set_xlim(X[0], X[-1])
    ax1.set_xlabel("time (s)")
    ax1.set_yticklabels([])
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

    bad_channels = np.where(output_df.channels[output_df.now_displaying])[0]
    print bad_channels
    amp_scale = 3.5
    
    
    fig, (ax1, ax2) =  \
              plt.subplots(2, 1, sharex=True,
                            subplot_kw = dict(projection="X_Pan_Axes") )
    # DPI = fig.get_dpi()
    # fig.set_size_inches(float(width*0.8)/DPI, float(height*0.8)/DPI)
    fig = constrainXPanZoomBehavior(fig)
    for chan in xrange(input_data.num_channels):
        variance = np.var(input_data.sigbuf[chan, t_idx])
        print variance
        variance = 5.0 / (1 + math.exp(-variance))
        print variance
        ax1.plot(X, chan*10 + variance * input_data.sigbuf[chan, t_idx].T,
                             lw=0.5)
    # amp_scale = amp_scale * input_data.num_channels / (len(bad_channels)+1)
    amp_scale = 7.0
    i = 1
    for chan in bad_channels:
        variance = np.var(input_data.sigbuf[chan, t_idx])
        print variance
        variance = 7.0 / (1 + math.exp(-variance))
        print variance
        height = (i*1.0 / (len(bad_channels)+1)) * input_data.num_channels
        ax2.plot(X, height*10 + variance * input_data.sigbuf[chan, t_idx].T,
                             lw=0.5)
        i += 1
    ax1.set_ylim(-10, (input_data.num_channels+1)*10)
    ax2.set_ylim(-10, (input_data.num_channels+1)*10)
    ax2.set_xlabel('time (s)')
    ax1.set_yticklabels([])
    ax2.set_yticklabels([])
    ax1.set_xlim(X[0], X[-1])
    for x in vlines:
        ax1.axvline(x=x, ls='--', color='k')
        ax2.axvline(x=x, ls='--', color='k')

    return fig

def draw(input_data, output_df, selected=None):
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

    if selected == None:
        selected = np.where(output_df.channels[output_df.now_displaying])[0]
