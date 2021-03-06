import PyDataSource
import numpy as np

class Qadc(PyDataSource.Detector):
    """Qadc waveform sampling module filters each of the four waveforms.
    """

    def __init__(self,*args,**kwargs):

        PyDataSource.Detector.__init__(self,*args,**kwargs)

        self.add.parameter(nchannels=4)
        
        signal_width=10
        hw = signal_width/2
        filter=np.array([-np.ones(hw),np.ones(hw)]).flatten()/(hw*2)
        self.add.parameter(filter=filter)

        for ch in range(4):
            name = 'Ch'+str(ch+1) 
            setattr(self, name, Channel(self,ch,name))

        self.add.property(amplitudes)
        self.add.property(filtered)
#        self._update_xarray_info()

    def _update_xarray_info(self):

        nchannels = self.nchannels
        length = self.configData.Length[0]

        xattrs = {'doc': 'IMP filtered amplitudes for 4 diode channel waveforms',
                  'unit': 'ADU'}
        self._xarray_info['dims'].update({'amplitudes': (['ch'], nchannels, xattrs)}) 
        
        xattrs = {'doc': 'IMP filtered waveforms for 4 diode channels',
                  'unit': 'ADU'}
        self._xarray_info['dims'].update({'filtered': (['ch', 't'], (nchannels, length), xattrs)}) 
        self._xarray_info['coords'].update({'t': np.arange(length)}) 


class Channel(object):
    """Channel class for Qacd Detector.
    """
    def __init__(self, qadc, channel, name):
        self._qadc = qadc 
        self._channel = channel
        self._name = name
        self.baseline = 0.

    @property
    def waveform(self):
        """Waveform of channel.
        """
        return np.array(self._qadc.evtData.data_u16[self._channel])

    @property
    def amplitude(self):
        """Amplitude of filtered channel.
        """
        return self.filtered.max()

    @property
    def filter(self):
        return self._qadc.filter
    
    @property
    def filtered(self):
        from scipy import signal
        hw = len(self.filter)/2
        f = -signal.convolve(self.waveform,self.filter)
        f[0:len(self.filter)+1] = 0
        f[-len(self.filter)-1:] = 0
        return f[hw:self.waveform.size+hw]

    @property
    def time(self):
        """Time of signal in waveform. (currently channel number needs to be converted)
           qadc signals are step functions.
           Additional noise needs to be subtracted.
        """
        hw = len(self.filter)/2
        return self.filtered.argmax()+hw

    @property
    def peak(self):
        """peak of signal in waveform.
           Currently crude calculation with no advanced background subtraction.
        """
        hw = len(self.filter)/2
        wf = self.waveform
        t0 = self.time
        amp = wf[t0+hw:t0+hw*2].mean() \
             -wf[t0-hw*2:t0-hw].mean()
        
        return amp

def amplitudes(self):
    """Amplitude of each filtered waveform.
    """
    return [getattr(self, 'Ch'+str(ch+1)).amplitude for ch in range(self.nchannels)]
    
def filtered(self):
    """Amplitude of each filtered waveform.
    """
    return np.array([getattr(self, 'Ch'+str(ch+1)).filtered for ch in range(self.nchannels)])
    

