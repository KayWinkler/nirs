import os
import pandas as pd

maxkraft_inputdir = 'maximalkraft_daten'
kraftausdauer_inputdir = 'kraftausdauer_daten'
nirs_inputdir = 'NIRS_daten'

def process_probands(maxkraft_inputdir):
    for filename in os.listdir(maxkraft_inputdir):
        if not filename.endswith('.txt'):
            continue
        basename, _, _ext = filename.rpartition('.')
        proband, _ , hand = basename.partition('_')
        yield proband, hand, filename

def get_maxkraft_file(filename):
    """ zur Bestimmung der Maximalkraft """
    maxkraft_file = os.path.join(maxkraft_inputdir, filename)
    if os.path.isfile(maxkraft_file):
        return maxkraft_file

    print('Kraftausdauer File not found! %r' % maxkraft_file)
    return None, None, None

def get_kraftausdauer_file(filename):
    """ Permutation über die Abbruchkriterien """
    kraftausdauer_file = os.path.join(kraftausdauer_inputdir, filename)
    if os.path.isfile(kraftausdauer_file):
        return kraftausdauer_file

    print('Kraftausdauer File not found! %r' % kraftausdauer_file)
    return None


def get_nirs_file(filename):

    nirs_file = os.path.join(nirs_inputdir, filename.replace('.txt', '.xlsx'))

    if os.path.isfile(nirs_file):
        return nirs_file

    print('Nirs File not found! %r' % nirs_file)
    return None



class Row():
    def __init__(self):
        self.results = []

    def add(self, result):
        self.results.append(result)

    def get_header(self):
        ''' return the flatened headers in a list'''
        headers = []
        for res in self.results:
            if isinstance(res, dict):
                headers.extend(list(res.keys()))
            if isinstance(res, pd.Series):
                headers.extend(res.keys().tolist())
        return headers

    def get_data(self):
        ''' return the flatened data in a list'''
        datas = []
        for res in self.results:
            if isinstance(res, dict):
                datas.extend(list(res.values()))
            if isinstance(res, pd.Series):
                datas.extend(res.tolist())
        return datas

    def __repr__(self):
        headers = self.get_header()
        datas = self.get_data()
        return "%r" % list(zip(headers, datas))