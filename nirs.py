#!/usr/bin/env python
# coding: utf-8

import csv
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import xlrd


def daten_plotten(df):
    Samplenumber = df['Sample number']
    TSI_Fit_Factor = df['TSI Fit Factor']
    O2Hb = df['O2Hb']
    HHb = df['HHb']
    tHb = df['tHb']
    HbDiff = df['HbDiff']
    TSI = df['TSI']
    Events = df['Events']


    #daten ploten
    plt.plot(TSI_Fit_Factor)
    plt.plot(O2Hb)
    plt.plot(HHb)
    plt.plot(tHb)
    plt.plot(HbDiff)
    plt.plot(TSI)
    #Legende einfügen
    plt.legend()
    plt.show()


class Nirs():
    
    def __init__(self):
        self.names = [
            'Sample number', 
            'TSI Fit Factor', 
            'O2Hb', 
            'HHb', 
            'tHb', 
            'HbDiff', 
            'TSI', 
            'Events', 
            'Empty colum', 
            'Event setting time'
        ]
    def gather_t_events(self, df):
        Events = df['Events']
        E = Events.dropna()
        E2 = E.tolist()

        e2 = []
        for item in E2:

            if not item.startswith('T'):
                continue

            e2.append(item)


        df_e_append = pd.DataFrame()

        e2_dict = {}
        for item in e2:
            query_str = 'Events == "%s"' % item
            df_e = df.query(query_str)
            df_e_append = df_e_append.append(df_e)

            e2_dict[item.strip()] = df_e

        return df_e_append
    
    @staticmethod
    def get_baseline_values(df):
        """#Baselinewerte"""
        df = df.set_index('Sample number')
        B1 = df[df['Events'] == 'B1 ']

        list_of_b1 = B1.index.tolist()
        assert len(list_of_b1) == 1

        b1_row_number = list_of_b1[0]

        start_baseline = b1_row_number - 60

        new_df = df[start_baseline:b1_row_number]
        baselinewerte = new_df.mean()
        return baselinewerte

    @staticmethod
    def load_nirs_column_names(filename):
        """
        read the column name description preface
        """
        names = []
        
        assoc = pd.read_excel(filename, skiprows=34, nrows=8)

        for index, row in assoc.iterrows():

            colname =  row['Trace (Measurement)']
            if 'Sample' in colname:
                names.append('Sample number')
            elif 'TSI Fit Factor' in colname:
                names.append('TSI Fit Factor')
            elif 'O2Hb' in colname:
                names.append('O2Hb')
            elif 'TSI' in colname:
                names.append('TSI')
            elif 'HHb' in colname:
                names.append('HHb')
            elif 'HbDiff' in colname:
                names.append('HbDiff')
            elif 'tHb' in colname:
                names.append('tHb')
            elif 'Event' in colname:
                names.append('Events')

        names.append('Empty Column')
        names.append('Event setting time')
        return names
    
    def load_nirs_data(self, filename):

        self.names = self.load_nirs_column_names(filename)
        raw_df = pd.read_excel(filename, skiprows=45, names=self.names)
       
        df_t_events = self.gather_t_events(raw_df)
        baselines = self.get_baseline_values(raw_df)
        raw_df = raw_df.set_index('Sample number')

        return raw_df, df_t_events, baselines
