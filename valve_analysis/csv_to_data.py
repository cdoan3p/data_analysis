import csv
from collections import OrderedDict
import numpy

def loadCSV(file, delimiter=None, errValue=None):
    """
    Reads a .csv file and creates a dictionary of numpy arrays.  Each column is turned into
        an array, with the first line used as the dictionary keys.

    inputs:
        file - file/path to read
        delimiter - character to use as a delimiter (defaults to comma)

    returns:
        dictionary of arrays
    """
    fp = open(file)

    if delimiter is None:
        reader = csv.reader(fp)
    else:
        reader = csv.reader(fp, delimiter=delimiter)

    rowCnt = 0
    dataSet = OrderedDict()

    for ln in reader:
        if(0 == rowCnt):
            columns = ln

            for c in columns:
                dataSet[c] = []
        
        elif 1 == rowCnt:
            pass

        else:
            try:
                for i in range(len(ln)):
                    try:
                        dataSet[columns[i]].append(float(ln[i]))
                    except:
                        if errValue is not None:
                            dataSet[columns[i]].append(errValue)
                        else:
                            dataSet[columns[i]].append(ln[i])
            except:
                print 'error parsing line %d' % (rowCnt+1)

        rowCnt += 1

    for k in dataSet.keys():
        dataSet[k] = numpy.array(dataSet[k])

    return dataSet

def _step_interp(x, xn, yn):
    y = [0]*len(x)
    for i in range(len(x)):
        pts = numpy.where(xn <= x[i])[0]
        if len(pts) > 0:
            y[i] = yn[pts[-1]]
        else:
            y[i] = yn[-1]
    return y


def mergeAndTimeCorrelateData(data, data2):
    tm = data['timestamp']
    for k in data2.keys():
        try:
            vals = numpy.interp(tm, data2['timestamp'], data2[k])
        except TypeError:
            vals = _step_interp(tm, data2['timestamp'], data2[k])
        if not k in data:
            data[k] = vals
        else:
            data['DL_' + k] = vals
    return data

def loadMultiple(filenames, adjust_time=False, delimiter=None, errValue=None):
    """
    Append multiple data sets

    inputs:
        filenames - a list of files/paths to read
    """
    data = OrderedDict()
    for f in filenames:
        try:
            new_data = loadCSV(f, delimiter=delimiter, errValue=errValue)
            for k in new_data.keys():
                if k in data:
                    if adjust_time and (k == 'elapsed_time'):
                        data[k] = numpy.append(data[k], new_data[k]+data[k][-1])
                    else:
                        data[k] = numpy.append(data[k], new_data[k])
                else:
                    data[k] = new_data[k]
        except Exception:
            print("Failed to load dataset: {fname}".format(fname=f))
    return data
