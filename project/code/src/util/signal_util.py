#!/usr/bin/python

from scipy.signal import butter, lfilter
from numpy import count_nonzero

class SignalUtil(object):

    def __init__(self):
        """This class does signal processing with raw signals"""

    def normalize(self, data):
        '''normalizes data between -1 and 1

        :param numpy.array data: list of values
        
        :return: normalized data
        :rtype: numpy.array
        '''
        if count_nonzero(data) == 0:
            return data

        extreme = float(max(max(data), abs(min(data))))

        return data / extreme

    def energy(self, data):
        '''calculates signal energy 
        
        :math:`E = \sum(data^2)`
        
        * `Energy_(signal_processing) <https://en.wikipedia.org/wiki/Energy_(signal_processing)>`_
        
        :param numpy.array data: list of values
        
        :return: signal energy
        :rtype: float
        '''
        return sum(data ** 2)

    def butterBandpass(self, lowcut, highcut, samplingRate, order=5):
        '''
        Creates a butterworth filter design from lowcut to highcut and returns the filter coefficients
        :see: `scipy.signal.butter <http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html#scipy.signal.butter>`_

        note: :math:`lowcut >= 0` and :math:`highcut <= samplingRate / 2`

        :param int lowcut: lower border
        :param int highcut: upper border
        :param int samplingRate: sample frequency
        
        :return: filter coefficients a, b
        :rtype: float
        '''
        # TODO throw exception here? 
        if highcut > samplingRate / 2:
            highcut = samplingRate / 2
        if lowcut < 0:
            lowcut = 0
        
        nyq = 0.5 * samplingRate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a
    
    
    def butterBandpassFilter(self, data, lowcut, highcut, samplingRate, order=5):
        b, a = self.butterBandpass(lowcut, highcut, samplingRate, order)
        #TODO y u no use: y = filtfilt(b, a, data)
        # - slower, other values
        y = lfilter(b, a, data)
        return y
