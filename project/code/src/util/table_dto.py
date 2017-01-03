#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 03.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''
from numpy import array

from config.config import ConfigProvider

TIMESTAMP_STRING = "Timestamp" # key which specifies the unix timestamp of the data

class TableDto(object):
    '''
    Representation of Signal table data
    '''

    def __init__(self, header=None, data=None, filePath="", samplingRate=None):
        '''
        table data with header, data and the filepath
        
        :param header:
        :param data:
        :param filePath:
        '''
        self.filePath = filePath
        self.header = header
        self.setData(data)
        self.setSamplingRate(samplingRate)

    def setHeader(self, header):  # pragma: no cover
        self.header = header

    def setData(self, data):  # pragma: no cover
        self.data = data
        if data is not None:
            self.len = len(data)

    def setSamplingRate(self, samplingRate=None):
        if samplingRate is not None:
            self.samplingRate = samplingRate
        else:
            self.samplingRate = self._calcSamplingRate()

    def _calcSamplingRate(self):
        '''
        calcs the samplerate for the whole dataset based on the timestamp column   
        
        :return: samplerate
        :rtype: float

        '''
        try:
            duration = self.getDuration()
            return self.len / duration
        except:
            return 0.0

    def getHeader(self):  # pragma: no cover
        return self.header

    def getData(self):  # pragma: no cover
        return self.data

    def getTimeIndex(self, fromTime):
        '''
        get the index for the given fromTime
        if fromTime < min(timestamp) return 0
        if fromTime > max(timestamp) return len(data)
        
        :param    float   fromTime:    time as unix timestamp 
        
        :return   int     the index of the given fromTime 
        '''
        data = self.getColumn(TIMESTAMP_STRING)
        if not self._timeInData(data, fromTime):
            raise ValueError('could not find %f in data' % fromTime)
        
        for i, time in enumerate(data):
            if time >= fromTime:
                return i

    def getTime(self, offset=0, limit=-1, length=-1):
        return self.getColumn(TIMESTAMP_STRING, offset, limit, length)

    def getColumn(self, columnName, offset=0, limit=-1, length=-1):
        '''
        get dataset from a certain column, either from offset to limit or till length
        if only column_name is specified, it returns the whole column
        if offset and length are both defined, length will be ignored
        
        :param     string column_name:   the name of the column
        :param     int    offset:        startindex of dataset
        :param     int    limit:         endpoint of dataset
        :param     int    length:        length of dataset
        
        :return: dataset for given column
        :rtype: array
        '''
        
        if columnName not in self.header:
            return None

        if limit == -1:
            if  length == -1:
                limit = self.len
            else:
                limit = offset+length

        index = self.header.index(columnName)
        return self.data[:, index][offset:limit]

    def getColumnByTime(self, columnName, fromTime, toTime):
        '''
        get dataset from a certain column, for a time interval (fromTime -> toTime)
             
        :param string    columnName:   the name of the column 
        :param float     fromTime:     start time of dataset as unix timestamp   
        :param float     toTime:       start time of dataset as unix timestamp
        
        :return: dataset for given column
        :rtype: array 
        
        :raise: ValueError if time could not be found in dataset 
        '''
        fromIndex, toIndex = -1, -1

        if fromTime > toTime:
            fromTime, toTime = self._switchTime(fromTime, toTime)
        
        data = self.getColumn(TIMESTAMP_STRING)
        
        if not self._timeInData(data, fromTime):
            raise ValueError('could not find %f in data' % fromTime)

        if not self._timeInData(data, toTime):
            raise ValueError('could not find %f in data' % toTime)

        for i, time in enumerate(data):
            if time >= fromTime and fromIndex == -1:
                fromIndex = i
            if time >= toTime:
                toIndex = i
                break

        return self.getColumn(columnName, fromIndex, toIndex)


    def getDuration(self):
        '''
        get the duration for the current data
        
        :return: duration
        :rtype: long

        '''
        data = self.getTime()
        duration = data[self.len - 1] - data[0]
        return duration

    def getSamplingRate(self):
        return self.samplingRate

    def getStartTime(self):
        '''
        get the first value from the timestamp column

        :return: start time
        :rtype: long

        '''
        return self.getTime()[0]

    def getEndTime(self):
        '''
        get the last value from the timestamp column
        
        :return: end time
        :rtype: long

        '''
        return self.getTime()[self.len-1]

    def getValueCount(self):
        return len(self.getColumn(self.header[0]))

    def _switchTime(self, time1, time2):
        return time2, time1

    def _timeInData(self, data, time):
        return (min(data) <= time <= max(data))

    def __repr__(self):
        return "EEGTableDto from '%s' shape %s\nheader %s" % (self.filePath, self.data.shape, self.header)

    def getColumns(self, columnNames):
        data = []
        for columnName in columnNames:
            data.append(self.getColumn(columnName))
        return array(data)

class EEGTableDto(TableDto):
    '''
    Representation of EEG table data
    '''

    def __init__(self, header=None, data=None, filePath="", samplingRate=None):
        super(EEGTableDto, self).__init__(header, data, filePath, samplingRate)

    def getEEGHeader(self):
        eegFields = ConfigProvider().getEmotivConfig().get("eegFields")
        return [head for head in self.header if head in eegFields]

    def getEEGData(self):
        eegFields = self.getEEGHeader()
        return self.getColumns(eegFields)

    def getQualityData(self):
        eegQualFields = ["Q"+head for head in self.getEEGHeader()]
        return self.getColumns(eegQualFields)

    def getQuality(self, eegQualField):
        return self.getColumn(eegQualField)

    def __repr__(self):
        return "EEGTableDto from '%s' shape %s\nheader %s" % (self.filePath, self.data.shape, self.header)

class ECGTableDto(TableDto):
    '''
    Representation of ECG table data
    '''

    def __init__(self, header=None, data=None, filePath="", samplingRate=None):
        super(ECGTableDto, self).__init__(header, data, filePath, samplingRate)

    def getECGHeader(self):
        return self.header[1]

    def getECGData(self):
        return array([self.getColumn("ECG")])

    def __repr__(self):
        return "ECGTableDto from '%s' shape %s\nheader %s" % (self.filePath, self.data.shape, self.header)