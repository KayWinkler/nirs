"""
retults - iterate over the data and create the result csv output
"""
import csv
import os

import kraftausdauer
from maximalkraft import Maximalkraft
from nirs import Nirs
import pandas as pd


maxkraft_inputdir = 'maximalkraft_daten'
kraftausdauer_inputdir = 'kraftausdauer_daten'
nirs_inputdir = 'NIRS_daten'


def process_probands(maxkraft_inputdir):
    for filename in os.listdir(maxkraft_inputdir):
        if not filename.endswith('.txt'):
            continue
        basename, _, _ext = filename.rpartition('.')
        proband, _, hand = basename.partition('_')
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
                    head = ':'.join([prefix, k])
                else:
                    head = k

                headers.append(head.replace(' ', '_'))

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
                val = data_dict[k]
                if not isinstance(val, (float, int)):
                    pass
                if "%r" % val in ['nan']:
                    val = ''
                if val is None:
                    val = ''

                datas.append(val)

        return datas

    def get(self):
        headers = self.get_header()
        datas = self.get_data()
        return list(zip(headers, datas))

    def __repr__(self):
        headers = self.get_header()
        datas = self.get_data()
        return "#%d %r" % (len(datas), list(zip(headers, datas)))


'''
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
'''


class CSVWriter(object):
    def __init__(self, filename):
        self.filename = filename
        self.writer = None
        self.headers_written = False

    def __enter__(self):
        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.writer(
            self.file, quoting=csv.QUOTE_NONNUMERIC, delimiter=',')
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

    df = pd.DataFrame()
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
            row.add('RecoveryDeltaprozent', recovery.get_deltaprozent())

            testing = Testing(nirs_data, nirs_event, nirs_baseline)

            for item in kraftausdauer:

                citeria = list(item.keys())[0]
                valid_intervals = item[citeria]['valid']

                row.add('Testing_' + citeria, {'valid': valid_intervals})

                try:
                    row.add(
                        'TestingMeanMin_' + citeria,
                        testing.get_mean_minima(valid_intervals)[0]
                    )
                except Exception as exx:
                    testing.get_mean_minima(valid_intervals)[0]

                try:
                    row.add(
                        'TestingMeanMinDiff_' + citeria,
                        testing.get_mean_minima(valid_intervals)[1]
                    )
                except Exception as exx:
                    testing.get_mean_minima(valid_intervals)[1]

                row.add(
                    'TestingMin_' + citeria,
                    testing.get_minima(valid_intervals)[0]
                )
                row.add(
                    'TestingMinDiff_' + citeria,
                    testing.get_minima(valid_intervals)[1]
                )

                row.add(
                    'TestingAll_' + citeria,
                    testing.get_avg_delta_relaxation_all(valid_intervals)
                )
                row.add(
                    'TestingAll_' + citeria,
                    testing.get_avg_delta_contraction_all(valid_intervals)
                )

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

            serie = pd.Series(row.get_data(), index=row.get_header())
            new_df = pd.DataFrame(columns=row.get_header())
            new_df = new_df.append(serie, ignore_index=True)
            df = df.append(new_df)

    # print(df)
    df.to_excel("output.xlsx")


if __name__ == '__main__':
    test()
    print('done!')
