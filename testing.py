import pandas as pd
from nirs import Nirs

Rename_Min_Mapping = {
    'HHb': 'minima_HHb', 
    'HbDiff' : 'minima_HbDiff', 
    'O2Hb' : 'minima_O2Hb',
    'TSI': 'minima_TSI', 
    'TSI Fit Factor' : 'minima_TSI Fit Factor' ,
    'tHb': 'minima_tHb'
    }

Rename_Max_Mapping = {
    'HHb': 'maxima_HHb',
    'HbDiff' : 'maxima_HbDiff',
    'O2Hb' : 'maxima_O2Hb',
    'TSI': 'maxima_TSI',
    'TSI Fit Factor' : 'maxima_TSI Fit Factor' ,
    'tHb': 'maxima_tHb'
    }

EmptyDeltaKontraktion = {
    'DeltaKontraktion_TSI': None,
    'DeltaKontraktion_O2Hb': None,
    'DeltaKontraktion_HHb': None,
    'DeltaKontraktion_tHb': None,
    'DeltaKontraktion_HbDiff': None,
}
EmptyDeltaRelaxation = {
    'DeltaRelaxation_TSI': None,
    'DeltaRelaxation_O2Hb': None,
    'DeltaRelaxation_HHb': None,
    'DeltaRelaxation_tHb': None,
    'DeltaRelaxation_HbDiff': None,
}
#Minima über gesamten Test
class Testing():


    def __init__(self, df, events, baselines):

        self.t_events = events
        self.df = df
        self.baselines = baselines


    def get_minima(self, max_events):
        """"""

        minima_gesamter_test = self._minma_relevant(self.df, self.t_events, max_events)

        differenz = self._differenz(self.baselines, minima_gesamter_test)

        return minima_gesamter_test, differenz


    def _minma_relevant(self, df, df_all_events, max_events):

        df_events = df_all_events[0:max_events]
        df_events_sample_number = df_events.index
        sample_number_firstT = df_events_sample_number.min()
        sample_number_lastT = df_events_sample_number.max()
        minima_gesamter_test_df = df[sample_number_firstT-1:sample_number_lastT]

        minima_gesamter_test = minima_gesamter_test_df.min()

        return minima_gesamter_test


    def _differenz(self, baselinewerte, minima_gesamter_test):
        """
        comment helperfunktion zur Berechnung der Differenz zwischen den Baselinewerten minus des Minimas der gesamten Testspanne
        :param base...:
        :return: dict ...
        """
        liste_baselinewerte = baselinewerte.to_numpy()
        liste_minima_gesamter_test = minima_gesamter_test.to_numpy()

        res = {}

        idx = -1
        for key in baselinewerte.keys().tolist():
            idx += 1
            if key.startswith("Empty"):
                continue

            diff = liste_baselinewerte[idx] - liste_minima_gesamter_test[idx]
            res[key] = diff
        return res

    def _get_minima_einzelne_wdh(self, max_events):
        events = self.t_events[:max_events]

        res = self._avg_minima_einzelne_wdh(self.df, events)
        min_cont, max_cont, min_rel, max_rel = res
        mean_minima = min_cont.mean()

        return mean_minima

    def _differenz_einzelne_wdh(self, baselinewerte, mean_minima):
        """
        comment helperfunktion zur Berechnung der Differenz zwischen den Baselinewerten minus des Minimas der gesamten Testspanne
        :param base...:
        :return: dict ...
        """
        liste_baselinewerte = baselinewerte.to_numpy()
        liste_mean_minima = mean_minima.to_numpy()

        res = {}

        idx = -1
        for key in baselinewerte.keys().tolist():
            idx += 1
            if key.startswith("Empty"):
                continue

            diff = liste_baselinewerte[idx] - liste_mean_minima[idx]
            res[key] = diff
        return res

    def get_mean_minima(self, max_events):
        """
        Funktion gibt Ergebnisse aus helperfuntionen __get_minima_einzelne_wdh und _differenz_einzelne_wdh zurück
        :param base...:
        :return: dict ...
        """

        mean_minima = self._get_minima_einzelne_wdh(max_events)

        differenz_mean_minima = self._differenz_einzelne_wdh(self.baselines, mean_minima)

        return mean_minima, differenz_mean_minima



    def _avg_minima_einzelne_wdh(self, raw_df, df_t_events):
        """
        Durchschnitt Minima der einzelnen Wdh

        :param raw_df: Rohdaten
        :param df_t_events: alle T Events

        :return: DataFrames mit den Minima und Maxima
                    der einzelnen Wiederholungen
        """

        df_t_events = df_t_events.set_index('Sample number')
        Events = df_t_events['Events']

        all_maximas = []
        all_minimas = []

        vorgänger = None
        for item in Events.items():
            sample, tn = item

            if vorgänger:
                minima = raw_df[vorgänger:sample].min()
                maxima = raw_df[vorgänger:sample].max()

                all_minimas.append(minima)
                all_maximas.append(maxima)

            vorgänger = sample
            vorgänger_tn = tn

        minima_einzelne_wdh = pd.DataFrame(all_minimas)
        maxima_einzelne_wdh = pd.DataFrame(all_maximas)

        relax_min_einzelne_wdh = pd.DataFrame(all_minimas[:-1])
        relax_max_einzelne_wdh = pd.DataFrame(all_maximas[1:])

        return (minima_einzelne_wdh, maxima_einzelne_wdh,
                relax_min_einzelne_wdh, relax_max_einzelne_wdh)

    def baselinewerte_minima_einzelne_wdh(self, baselinewerte, avg_minima_einzelne_wdh):
        """
        Durchschnitt Baseline - Minima der einzelnen Wdh

        """
        diff_baselinewerte_minima_einzelne_wdh = (baselinewerte - avg_minima_einzelne_wdh)

        return diff_baselinewerte_minima_einzelne_wdh

    def _delta(self, min_df, max_df, scope):
        """
        
        :param scope: Kontraktion or 
        """

        # Arbeitskopie erzeugen um Konflike beim Umbenennen zu vermeiden

        minima_wdh = pd.DataFrame(min_df)
        maxima_wdh = pd.DataFrame(max_df)

        # Spaltennamen umbenennen

        minima_wdh = minima_wdh.rename(columns= Rename_Min_Mapping)
        maxima_wdh = maxima_wdh.rename(columns=Rename_Max_Mapping)

        # Dataframe mit Minima und Maxima einzelne WDh erstellen

        delta_all = pd.concat([minima_wdh, maxima_wdh], axis=1)
        delta = pd.DataFrame()

        # Delta alle Wdh

        delta['Delta'+scope+'_TSI'] = delta_all['minima_TSI'] - delta_all['maxima_TSI']
        delta['Delta'+scope+'_O2Hb'] = ((delta_all['minima_O2Hb']/delta_all['maxima_O2Hb'])-1)*100
        delta['Delta'+scope+'_HHb'] = ((delta_all['minima_HHb']/delta_all['maxima_HHb'])-1)*100
        delta['Delta'+scope+'_tHb'] = ((delta_all['minima_tHb']/delta_all['maxima_tHb'])-1)*100
        delta['Delta'+scope+'_HbDiff'] = ((delta_all['minima_HbDiff']/delta_all['maxima_HbDiff'])-1)*100

        return delta


    def _deltacontraction(self, cont_min_df, cont_max_df):
        """
        Delta Kontraktion
        """

        return self._delta(cont_min_df, cont_max_df, scope='Kontraktion')

    def _deltarelaxation(self, relax_min_df, relax_max_df):
        """
        Delta Relaxation
        """

        return self._delta(relax_min_df, relax_max_df, scope='Relaxation')

    # ---------------------------------------------------------------------- --

    # relaxation

    def _get_avg_delta_relaxation(self, events=None):
        """
        calculate the average delta relaxation

        :paran events: list of events
        :return: pd.Series
        """
        if events is None:
            events = self.t_events

        result = self._avg_minima_einzelne_wdh(self.df, events)

        (_, _, relax_min_einzelne_wdh, relax_max_einzelne_wdh) = result

        delta_relaxation = self._deltarelaxation(
                            relax_min_einzelne_wdh, relax_max_einzelne_wdh
                            )

        return delta_relaxation.mean()

    def get_avg_delta_relaxation_all(self):
        return self._get_avg_delta_relaxation()

    def get_avg_delta_relaxation_first(self, max_, num=3):
        if max_ < num:
            return EmptyDeltaRelaxation
        events = self.t_events[:max_]
        events = events[:num]

        return self._get_avg_delta_relaxation(events)

    def get_avg_delta_relaxation_last(self, max_, num=3):
        if max_ < num:
            return EmptyDeltaRelaxation
        events = self.t_events[:max_]
        events = events[-num:]

        return self._get_avg_delta_relaxation(events)

    def get_avg_delta_relaxation_mid(self, max_, num=3):
        if max_ <= num:
            return EmptyDeltaRelaxation
        mid = ((max_-num) // 2)
        events = self.t_events[mid:mid+num]
        return self._get_avg_delta_relaxation(events)

    # ------------------------------------------------------

    # contraction

    def _get_avg_delta_contraction(self, events=None):
        """ """
        if events is None:
            events = self.t_events

        result = self._avg_minima_einzelne_wdh(self.df, events)

        (minima_einzelne_wdh, maxima_einzelne_wdh, _, _) = result

        delta_contraction = self._deltacontraction(minima_einzelne_wdh, maxima_einzelne_wdh)

        # return the Series of average delta contraction

        return delta_contraction.mean()


    def get_avg_delta_contraction_all(self):
        return self._get_avg_delta_contraction()


    def get_avg_delta_contraction_first(self, max_, num=3):
        if max_ < num:
            return EmptyDeltaKontraktion
        events = self.t_events[:max_]
        events = events[:num]
        return self._get_avg_delta_contraction(events)


    def get_avg_delta_contraction_last(self, max_, num=3):
        if max_ <= num:
            return EmptyDeltaKontraktion
        events = self.t_events[:max_]
        events = events[-num:]
        return self._get_avg_delta_contraction(events)

    def get_avg_delta_contraction_mid(self, max_, num=3):
        if max_ < num:
            return EmptyDeltaKontraktion
        mid = ((max_-num) // 2)
        events = self.t_events[mid:mid+num]
        return self._get_avg_delta_contraction(events)


