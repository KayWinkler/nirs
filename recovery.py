import pandas as pd

VALS = [
    ('TSI', 'ge'), ('O2Hb', 'ge'), ('HHb', 'le'),
    ('tHb', 'ge'), ('HbDiff', 'ge')
    ]

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

        E1 is the termination of test
        when will relaxation be half of the baseline starting from E1

        :param df: df's mit recovery Daten
        :param baselinewerte: Baseline Werte

        :return: halftimes of TSI O2Hb HHb tHb HbDiff
        """


        e1 = recovery_df[recovery_df['Events'] == 'E1 '].mean()
        e1_row_number = Recovery._get_rownummber_for_event(recovery_df, 'E1 ')
        diff = (baselinewerte - e1) * 0.5 + e1


        res = {}
        for val, comp in VALS:
            #4 Zeitpunkte finden
            diff_val = diff[val]

            if comp == 'le':
                df_match = recovery_df[ recovery_df[val] <= diff_val]
            elif comp == 'ge':
                df_match = recovery_df[ recovery_df[val] >= diff_val]

            if df_match.empty:
                res[val] = None
                continue

            # 5 Differenz Zeitpunkte T1/2
            index_df_match = df_match[0:1].index.tolist()

            # 6 scale down to time frame
            res[val] = (index_df_match[0]- e1_row_number)/10

        return res


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
        for val, _ in VALS:
            if half[val]:
                result[val] = self._avg_recovery_for(
                                        val, half[val], deltaprozent)
            else:
                result[val] = None

        return result

    def get_timetohalf_recovery(self):

        half = self._get_timetohalf_recovery(self.recovery_df, self.baseline)
        return half

    def get_dept(self):
        e1 = self.recovery_df[self.recovery_df['Events'] == 'E1 '].mean()
        return self._dept(self.baseline, e1)


