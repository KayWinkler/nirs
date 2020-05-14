import os
import pandas as pd

from nirs import Nirs
from maximalkraft import Maximalkraft
import kraftausdauer


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

def get_maxkraft(filename):
    """ zur Bestimmung der Maximalkraft """
    maxkraft_file = os.path.join(maxkraft_inputdir, filename)
    if not os.path.isfile(maxkraft_file):
        raise Exception('Unable to load Maximalkraft')

    return Maximalkraft(maxkraft_file)


def get_kraftausdauer(filename, f_max):
    """ Permutation über die Abbruchkriterien """
    kraftausdauer_file = os.path.join(kraftausdauer_inputdir, filename)

    if not os.path.isfile(kraftausdauer_file):
        raise Exception('Unable to load Kraftausdauer')

    return kraftausdauer.get_kraftausdauer(
                            kraftausdauer_file, f_max)

def load_nirs_data(filename):

    nirs_file = os.path.join(nirs_inputdir, filename.replace('.txt', '.xlsx'))

    if not os.path.isfile(nirs_file):
        raise Exception('Nirsfile not found')

    return Nirs().load_nirs_data(nirs_file)



class Row():
    def __init__(self):
        self.results = []

    def add(self, prefix, result):
        self.results.append((prefix, result))

    def get_header(self):
        '''
        return the flat headers in a list

        the header must be sorted
        '''
        headers = []
        for prefix, res in self.results:

            if isinstance(res, dict):
                data_dict = res

            if isinstance(res, pd.Series):
                data_dict = res.to_dict()
 
            for k in sorted(data_dict.keys()):
                if prefix:
                    head = ':'.join([prefix,k])
                else:
                    head = k

                headers.append(head.replace(' ','_'))

        return headers

    def get_data(self):
        '''
        return the flat data in a list

        the data must be sorted
        '''
        datas = []
        for _prefix, res in self.results:

            if isinstance(res, dict):
                data_dict = res

            if isinstance(res, pd.Series):
                data_dict = res.to_dict()

            for k in sorted(data_dict.keys()):
                datas.append(data_dict[k])

        return datas

    def __repr__(self):
        headers = self.get_header()
        datas = self.get_data()
        return "#%d %r" % (len(datas), list(zip(headers, datas)))
'''
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
'''
import csv
class CSVWriter(object):
    def __init__(self, filename):
        self.filename = filename
        self.writer = None
        self.headers_written = False

    def __enter__(self):
        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.writer(self.file, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
        return self

    def writerow(self, row):

        if not isinstance(row, Row):
            self.writer.writerow(row)
            return

        if not self.headers_written:
            headers = row.get_header()
            self.writer.writerow(headers)
            self.headers_written = True

        self.writer.writerow(row.get_data())


    def __exit__(self, type, value, traceback):
        self.file.close()

def test():

    from recovery import Recovery
    from testing import Testing

    with CSVWriter('output.csv') as writer:

        for entry in process_probands('maximalkraft_daten'):

            row = Row()

            proband, hand, filename = entry
            row.add('', {'proband': proband, 'hand': hand})
            print(row)

            try:
                nirs_data, nirs_event, nirs_baseline = load_nirs_data(filename)
                f_max, f_avg = get_maxkraft(filename)
                kraftausdauer = get_kraftausdauer(filename, f_max)
            except Exception as exx:
                print('Failed to load file: %r : %r' % (filename, exx))
                continue

            row.add('', {'peak force': f_max, 'max force': f_avg})

            # print("== processing recovery ==")

            recovery = Recovery(nirs_data, nirs_event, nirs_baseline)

            row.add('RecoveryHalftime', recovery.get_timetohalf_recovery())
            row.add('RecoveryDepletion', recovery.get_dept())
            row.add('RecoveryDeltaprozent',recovery.get_deltaprozent())

            testing = Testing(nirs_data, nirs_event, nirs_baseline)

            row.add('TestingAll', testing.get_avg_delta_relaxation_all()) # Series
            row.add('TestingAll', testing.get_avg_delta_contraction_all()) # Series

            for item in kraftausdauer:

                citeria = list(item.keys())[0]
                valid_intervals = item[citeria]['valid']

                row.add('Testing_' + citeria,{'valid': valid_intervals})

                row.add(
                    'TestingFirst_' + citeria,
                    testing.get_avg_delta_relaxation_first(valid_intervals)
                    )
                row.add(
                    'TestingFirst_' + citeria,
                    testing.get_avg_delta_contraction_first(valid_intervals)
                    )

                row.add(
                    'TestingMid_' + citeria,
                    testing.get_avg_delta_relaxation_mid(valid_intervals)
                    )
                row.add(
                    'TestingMid_' + citeria,
                    testing.get_avg_delta_contraction_mid(valid_intervals)
                    )

                row.add(
                    'TestingLast_' + citeria,
                    testing.get_avg_delta_relaxation_last(valid_intervals)
                    )
                row.add(
                    'TestingLast_' + citeria,
                    testing.get_avg_delta_contraction_last(valid_intervals)
                    )

            writer.writerow(row)



if __name__ == '__main__':
    test()
    print('done!')