import csv
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
#%matplotlib notebook

def Maximalkraft(filename, sampletime='3s', plot=False):
    """
    bestimme die Maximalkraft
    
    """                           
    
    # einlesen der Daten
    
    df = pd.read_csv(filename, names = ['kraft','sec'])

    kraft = df['kraft']
    sec = df['sec']

    peak_force = kraft.max(0, skipna=False)

    df['sec'] = df['sec'].astype('float64') 
    df['zeit'] = pd.to_datetime(df['sec'], unit='s')
    zeit = df['zeit']

    rolling_window = df.rolling(window=sampletime, on='zeit').mean()

    average_force = max(rolling_window['kraft'])

    if plot:
        plt.plot(rolling_window['kraft'])
        plt.plot(kraft)
        plt.show()

        
    return peak_force, average_force

# Peakforce, avg_kraft_3s = Maximalkraft(filename=filename)

