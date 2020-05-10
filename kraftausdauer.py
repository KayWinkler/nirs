#!/usr/bin/env python
# coding: utf-8

import csv
import math

def std_derivation(list_of_values, med=None):

    rel_med = 1
    #berechnet den Mittelwert
    if not med:
        avg_vals = 0.0
        for val in list_of_values:
            avg_vals = avg_vals + val
        med = avg_vals / len(list_of_values)
        rel_med = 0 

    #berechnet Standardabweichung
    sum_vals = 0.0
    if len(list_of_values) > 1:
        for val in list_of_values:
            sum_vals = sum_vals + (val - med)*(val - med)
        res = math.sqrt(sum_vals / (len(list_of_values) - rel_med))
    elif len(list_of_values) == 1:
        res = list_of_values[0]
    else:
        print("empty list")
        res = 0.0
    return res


def daten_aufbereiten(filename, kraft_schwellwert):
    """

    """
    #setzt den initialen wdh_counter auf 0
    wdh_counter = 0

    #csv reader, r bedeutet read, durch quote_nonnumeric werden werte als numersich dargestellt
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)

        #Leere Liste wird erstellt
        row_old = []
        #beginnend ab Zeile 14
        zeile = 14
        # für jede Zeile der Datei
        for row in csvreader:

            #Iterator, so lange die vorherige Zeile nicht der aktuellen entspricht, mache weiter
            if not row_old:
                row_old = row
                #yield is a keyword that is used like return, except the function will return a generator.
                yield 0.0, 0.0, 0.0, 0
                continue

            # definition der Parameter für Liste
            kraft, zeit = row
            kraft_old, zeit_old = row_old
            zeitdelta = zeit - zeit_old
            kraft_integral = zeitdelta*kraft
            
            #wenn Kraft größer gleich dem Kraftschwellwert und vorherige Kraft kleiner Kraftschwellwert erhöhe 
            #wdh counter um 1
            if kraft >= kraft_schwellwert and kraft_old < kraft_schwellwert:
                wdh_counter = wdh_counter + 1

            yield kraft, zeitdelta, kraft_integral, wdh_counter

            # hebe die aktuelle Zeile auf
            row_old = row
            


# funktion zur Analyse der einzelnen Intervalle mit filename und maximal_kraft als Eingabeparameter
def analyse_intervals(filename, maximal_kraft):

    kraft_target = maximal_kraft * 0.6
    min_TZ = kraft_target - (kraft_target * 0.05)
    max_TZ = kraft_target + (kraft_target * 0.05)
    min_TZ_10 = kraft_target - (kraft_target * 0.1)
    max_TZ_10 = kraft_target + (kraft_target * 0.1)

    kraft_schwellwert = kraft_target * 0.2

    #erstelle leeres dictionary
    summup = {}
    
    for prep in daten_aufbereiten(filename, kraft_schwellwert):
        kraft, delta_t, _int_k, wdh = prep
        #wenn 
        if wdh not in summup:
            #definiere Einträge für dictionary
            summup[wdh] = {
                'bT': 0.0, 'pT': 0.0, 'gT': 0.0, 'dTZ': 0.0, 'dTZ_10': 0.0, 
                'aK': 0.0, 'bC': 0.0, 'sK': 0.0}

        #wenn Bedingung erfüllt:
        if kraft >= kraft_schwellwert:
            #summiere in Abhängigkeit der Wdh vorherige Summe + Zeitdelta
            summup[wdh]['bT'] = summup[wdh]['bT'] + delta_t
        # ansonsten
        else:
            #summiere in Abhängigkeit der Wdh vorherige Summe + Zeitdelta
            summup[wdh]['pT'] = summup[wdh]['pT'] + delta_t

        #summiere in Abhängigkeit der Wdh vorherige Summe + Zeitdelta
        summup[wdh]['gT'] = summup[wdh]['gT'] + delta_t

        # zeit in TargetZone 5%
        if kraft >= min_TZ and kraft <= max_TZ:
            # summup[wdh]['kTZ'].append(kraft)
            summup[wdh]['dTZ'] = summup[wdh]['dTZ'] + delta_t

        # zeit in TargetZone 10%
        if kraft >= min_TZ_10 and kraft <= max_TZ_10:
            # summup[wdh]['kTZ'].append(kraft)
            summup[wdh]['dTZ_10'] = summup[wdh]['dTZ_10'] + delta_t
            

        # Kraftdurchschnitt über Schwellwert
        if kraft >= kraft_schwellwert:
            #sk = summe Kraft
            summup[wdh]['sK'] = summup[wdh]['sK'] + kraft * delta_t
            #Zählt die Anzahl der Werte
            summup[wdh]['bC'] = summup[wdh]['bC'] + 1.0
            # ak = average Kraft
            summup[wdh]['aK'] = summup[wdh]['sK'] / summup[wdh]['bT']

    return summup


def kraftausdauer_auswertung(Wiederholungen, Maximalkraft,
                             Zeitbeschränkung=None, Zeitschwellwert=2.0,
                             Kraftbeschränkung=None):
    counter = 0
    summup_bT = 0.0
    summup_dTZ = 0.
    summup_dTZ_10 = 0.0

    Liste_bT = []
    Liste_avgKraft = []
    Zeitschwellwert = 2

    zeit_wdh = -1
    kraft_wdh = -1
 
    kraft_target = Maximalkraft * 0.6
    Kraftschwellwert = kraft_target * 0.2

    wdh_list = []

    for wdh, data_dict in Wiederholungen.items():

        # skip the first interval as it contains nothing relevant
        if wdh == 0:
            continue

        belastungs_kraft = data_dict.get('aK')
        belastungs_zeit = data_dict.get('bT')

        # nimm zu kleine Werte nicht mit in die Berechnung
        if Zeitschwellwert != 0 and belastungs_zeit <= Zeitschwellwert:
            continue

        # nimm zu kleine Werte nicht mit in die Berechnung
        if Kraftschwellwert != 0 and belastungs_kraft <= Kraftschwellwert:
            continue


        if Zeitbeschränkung != 0 and belastungs_zeit <= Zeitbeschränkung:
            if wdh - zeit_wdh == 1:
                break
            zeit_wdh = wdh
            

        if Kraftbeschränkung != 0 and belastungs_kraft <= kraft_target - kraft_target * Kraftbeschränkung:
            if wdh - kraft_wdh == 1:
                break
            kraft_wdh = wdh

        #print('%d: %r' % (wdh, data_dict))
        counter = counter + 1
        summup_bT = summup_bT + data_dict.get('bT')
        summup_dTZ = summup_dTZ + data_dict.get('dTZ')
        summup_dTZ_10 = summup_dTZ_10 + data_dict.get('dTZ_10')
 
        Liste_bT.append(data_dict.get('bT'))
        Liste_avgKraft.append(data_dict.get('aK'))
        wdh_list.append(wdh)

    avg_bT = summup_bT / counter
    avg_dTZ = summup_dTZ / counter
    avg_dTZ_10 = summup_dTZ_10 / counter

    std_bT = std_derivation(Liste_bT, Kraftschwellwert)
    std_avgKraft = std_derivation(Liste_avgKraft, kraft_target)

    results = {}
    results['Kraftbeschränkung (%)'] = Kraftbeschränkung
    
    results['effektive Kraftbeschränkung (kg)'] = (kraft_target - kraft_target * Kraftbeschränkung)
    results['Zeitbeschränkung'] = Zeitbeschränkung

    results["Abruch bei Interval"] = wdh
    results['gültige Intervalle'] = counter
    results['durchschnittliche Belastungszeit'] = avg_bT 
    results['Durchschnitt in Targetzone 5%'] = avg_dTZ
    results['Durchschnitt in Targetzone 10%'] = avg_dTZ_10
    results['Standardabweichung Belastungszeit'] = std_bT
    results['Standartabweichung Krafttarget'] = std_avgKraft

    idx = "k%.2f:t%.2f" % (Kraftbeschränkung, Zeitbeschränkung)
    return  {idx: {
        'detail': results,
        'valid': counter,
        'wdhs': wdh_list,
        }
    }


def Kraftausdauer(filename, maximalkraft):
    """
    Kraftausdauer Auswertung mit verschiedenen Zeit und Kraft Beschränkungen
    """

    Ergebnisse = []

    Zeitbeschränkungen = [0.0, 6.0, 5.0, 4.0]
    Kraftbeschränkungen = [0.0, 0.1, 0.07]

    wiederholungen = analyse_intervals(filename, maximal_kraft=maximalkraft)

    for Kraftbeschränkung in Kraftbeschränkungen:
        for Zeitbeschränkung in Zeitbeschränkungen:
            Ergebniss = kraftausdauer_auswertung(wiederholungen,
                            Maximalkraft=maximalkraft,
                            Zeitbeschränkung=Zeitbeschränkung,
                            Kraftbeschränkung=Kraftbeschränkung
                            )

            Ergebnisse.append(Ergebniss)

    return Ergebnisse







# %%
