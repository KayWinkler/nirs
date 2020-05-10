import pandas as pd



class Recovery():
    
    def __init__(self, df, events, baselines):

        self.t_events = events
        self.recovery_df = self._get_recovery_df(df)
        self.baseline = baselines

    @staticmethod
    def _get_recovery_df(df):
        """
        Berechnung der Halbwertszeit der Regeneration nach Testabbruch

        :param df: Rohdaten
        :return: recovery dataframe
        """

        e1_row_number = Recovery._get_rownummber_for_event(df, 'E1 ')
        e2_row_number = Recovery._get_rownummber_for_event(df, 'E2 ')

        return df[e1_row_number-1: e2_row_number]

    @staticmethod
    def _get_e1(recovery_df):
        e1 = recovery_df[recovery_df['Events'] == 'E1 '].mean()

    @staticmethod
    def _get_rownummber_for_event(df, event_name):
        """
        helper to get rownumber of event
        """
        E = df[df['Events'] == event_name]
        list_of_e = E.index.tolist()
        e_row_number = list_of_e[0]
        return e_row_number

    @staticmethod  
    def _get_timetohalf_recovery(recovery_df, baselinewerte):
        """
        Berechnung der Halbwertszeit der Regeneration nach Testabbruch

        :param df: df's mit recovery Daten
        :param baselinewerte: Baseline Werte

        :return: halftimes of TSI O2Hb HHb tHb HbDiff
        """

        # get the relaxation start series ('E1 ') to get the diff to the baseline
        e1 = recovery_df[recovery_df['Events'] == 'E1 '].mean()
        diff = (baselinewerte - e1) *0.5 + e1

        #4 Zeitpunkte finden
        TSI = diff['TSI']
        O2Hb = diff['O2Hb']
        HHb = diff['HHb']
        tHb = diff['tHb']
        HbDiff = diff['HbDiff']

        e1_row_number = Recovery._get_rownummber_for_event(recovery_df, 'E1 ')

        df_match_TSI = recovery_df[ recovery_df['TSI'] >= TSI]
        df_match_O2Hb = recovery_df[ recovery_df['O2Hb'] >= O2Hb]
        df_match_HHb = recovery_df[ recovery_df['HHb'] <= HHb]
        df_match_tHb = recovery_df[ recovery_df['tHb'] >= tHb]
        df_match_HbDiff = recovery_df[ recovery_df['HbDiff'] >= HbDiff]

        #5 Differenz Zeitpunkte T1/2
        index_df_match_TSI = df_match_TSI[0:1].index.tolist()
        index_df_match_O2Hb = df_match_O2Hb[0:1].index.tolist()
        index_df_match_HHb = df_match_HHb[0:1].index.tolist()
        index_df_match_tHb = df_match_tHb[0:1].index.tolist()
        index_df_match_HbDiff = df_match_HbDiff[0:1].index.tolist()

        T1_2_TSI_s = (index_df_match_TSI[0]- e1_row_number)/10
        T1_2_O2Hb_s = (index_df_match_O2Hb[0]- e1_row_number)/10
        T1_2_HHb_s = (index_df_match_HHb[0]- e1_row_number)/10
        T1_2_tHb_s = (index_df_match_tHb[0]- e1_row_number)/10
        T1_2_HbDiff_s = (index_df_match_HbDiff[0]- e1_row_number)/10

        #print('T1/2_TSI', T1_2_TSI)
        #print('T1/2_O2Hb', T1_2_O2Hb)
        #print('T1/2_HHb', T1_2_HHb)
        #print( 'T1/2_tHb', T1_2_tHb)
        #print('T1/2_HbDiff', T1_2_HbDiff)

        #fin result!

        return  T1_2_TSI_s, T1_2_O2Hb_s, T1_2_HHb_s, T1_2_tHb_s, T1_2_HbDiff_s

    @staticmethod
    def _recovery_per_second(recovery_df):
        """
        :return: average recovery per 0.1 seconds during T1/2    
        """

        #1 erzeuge ein neues DF und löschen darin die Spalten

        recoverypersecond_df = pd.DataFrame()
        recoverypersecond_df = recoverypersecond_df.append(recovery_df)

        #recoverypersecond_df = recoverypersecond_df.drop('Empty colum', axis = 1)
        recoverypersecond_df = recoverypersecond_df.drop('Event setting time', axis = 1)
        recoverypersecond_df = recoverypersecond_df.drop('Events', axis = 1)

        #2 Delta berechnen

        delta_df = recoverypersecond_df.diff()

        #3 delta% berechnen

        e1 = recovery_df[recovery_df['Events'] == 'E1 '].mean()
        deltaprozent = (100/(e1))*delta_df

        return deltaprozent

    @staticmethod
    def _avg_recovery_for(key, halftime, deltaprozent):
        """
        return average recovery per 0.1 second in percentage

        """
        deltaprozent_key = deltaprozent[key]
        halftime_rows = int(halftime*10)
        return deltaprozent_key[0:halftime_rows].mean()

    @staticmethod
    def _dept(baselinewerte, e1):
        dept = 100 - ((100 / baselinewerte) * e1)
        return dept
    
    def get_deltaprozent(self):

        result = {}
        
        deltaprozent = self._recovery_per_second(self.recovery_df)
        half = self._get_timetohalf_recovery(self.recovery_df, self.baseline)
    
        T1_2_TSI_s, T1_2_O2Hb_s, T1_2_HHb_s, T1_2_tHb_s, T1_2_HbDiff_s = half
        result['TSI'] = self._avg_recovery_for('TSI', T1_2_TSI_s, deltaprozent)
        result['O2Hb'] = self._avg_recovery_for('O2Hb', T1_2_O2Hb_s, deltaprozent)
        result['HHb'] = self._avg_recovery_for('HHb', T1_2_HHb_s, deltaprozent)
        result['tHb'] = self._avg_recovery_for('tHb', T1_2_tHb_s, deltaprozent)
        result['HbDiff'] = self._avg_recovery_for('HbDiff', T1_2_HbDiff_s, deltaprozent)
        
        return result
    
    def get_timetohalf_recovery(self):
        return self._get_timetohalf_recovery(self.recovery_df, self.baseline)
    
    def get_dept(self):
        e1 = self.recovery_df[self.recovery_df['Events'] == 'E1 '].mean()
        return self._dept(self.baseline, e1)
    
 


