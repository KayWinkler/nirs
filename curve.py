"""
curve fitting

- approximate the given values of a data frame with a polynomial curve x^8

used to identify the curve minima and maxima to identify the direction and
calculate the tendencies

"""

from scipy import optimize


class Curve():
    """
    low level mathematical helper to fit a data set
    """

    def __init__(self, params=None):
        self.curve_params = params

    def curve_fitting(self, x, a, b, c, d, e, f, g, h):
        """
        calculate the polynomial curve values
        """

        sumup = 0.0
        count = 0

        for var in [a, b, c, d, e, f, g, h]:
            sumup += var * x**count
            count += 1

        return sumup

    def get_curve_data(self, row_num, data):
        """
        get the y values for the given index
        """

        params, _covariance = optimize.curve_fit(
            self.curve_fitting, row_num, data)

        self.curve_params = params

        values = []
        for x in row_num:
            y = self.curve_fitting(x, *self.curve_params)
            values.append(y)

        return values


class CurveDataFrame():
    """
    data frame with data of the interpolated function
    """

    def __init__(self, df):
        self.curve_df = self.get_curve_df(df)

    @staticmethod
    def get_curve_df(df):
        """
        create a copy of a given data frame and for each column interpolate
        the data at each values
        """

        ts_curve_df = df.copy()

        ts_index = ts_curve_df.index.tolist()
        for column_name in ts_curve_df.columns.tolist():

            try:
                curve = Curve()
                values = curve.get_curve_data(
                    ts_index, ts_curve_df[column_name])
                ts_curve_df[column_name] = values

            except Exception as _exx:
                ts_curve_df[column_name] = ''

        return ts_curve_df

    def get_df(self):
        """
        provide the interpolated data frame for other pandas operations
        :return: the pandas data frame
        """
        return self.curve_df

    @staticmethod
    def _slices(curve_df, slices=3):
        """
        helper - to slide with overlap over a data frame

         [--------][-------][--------]
             [--------][--------]
                   [-------][--------]
                       [--------]
                            [--------]

        :yield: a sub data frame
        """

        first = curve_df.index.tolist()[0]
        last = curve_df.index.tolist()[-1]
        len_df = last - first

        slice_size = ((last - len_df) // slices)
        slice_shift = (slice_size // 2)

        for range_start in range(first, last, slice_shift):
            range_end = range_start + slice_size

            if range_end > last:
                range_end = last

            # slices of data frames are not index based! they are arrays!

            slice_df = curve_df[range_start - first:range_end - first]
            yield slice_df

    @staticmethod
    def _get_min_max(curve_df, maxima=True):
        """
        internal helper:

        iterate through the slices of a data frame and get the min or max
        of the local slice.
        If the min or max is direct on the border of the slice, we skip this
        entry as it might be no local max or min. In case it is a min or max,
        the next slice will identify this.

        :param curve_df: the interpolated data frame
        :param maxima: switch if minima or maxima are searched
        :return: dict for each column with a dict of x,y values
        """

        column_names = curve_df.columns.tolist()

        extrema_dict = {}

        for slice_df in CurveDataFrame._slices(curve_df):

            _idx = slice_df.index
            start = slice_df.index.tolist()[0]
            end = slice_df.index.tolist()[-1]

            for column_name in column_names:
                try:
                    if maxima:
                        row_num = slice_df[column_name].idxmax()
                    else:
                        row_num = slice_df[column_name].idxmin()

                    row = slice_df.iloc[slice_df.index == row_num]
                    row_data = row[column_name].tolist()[0]

                    # preserve the data in a dictionary

                    val = extrema_dict.get(column_name, {})

                    if row_num > start + 2 and row_num < end - 2:
                        val[row_num] = row_data

                    extrema_dict[column_name] = val

                except TypeError as _exx:
                    extrema_dict[column_name] = extrema_dict.get(
                        column_name, {})

                except Exception as exx:
                    print('unknown exception occured: %r' % exx)

        return extrema_dict

    def get_maxima(self):
        """
        get the maxima of the CurveDataFrame

        :return: dict for each column with a dict of x,y values
        """
        return self._get_min_max(self.curve_df, maxima=True)

    def get_minima(self):
        """
        get the minima of the CurveDataFrame

        :return: dict for each column with a dict of x,y values
        """
        return self._get_min_max(self.curve_df, maxima=False)


def usage():
    """
    interface usage verification
    """

    from nirs import Nirs
    from testing import Testing
    from matplotlib import pyplot as plt

    # load the nirs data

    df, _events, _baseline = Nirs().load_nirs_data('NIRS_daten/311_d.xlsx')
    ts_df = Testing.get_df(df, 'T1 ', 'E1 ')
    ts_df['HHb'] = 100 - ts_df['HHb']

    # create the interpolated data frame
    curve_dataframe = CurveDataFrame(ts_df)

    # and get the minima and maxima

    minima_dict = curve_dataframe.get_minima()
    print('## local minima at %r' % minima_dict)

    maxima_dict = curve_dataframe.get_maxima()
    print('## local maxima at %r' % maxima_dict)

    curve_df = curve_dataframe.get_df()

    column_names = curve_df.columns.tolist()
    for column_name in column_names:

        plt.plot(curve_df[column_name], label=column_name)

    plt.legend()
    plt.show()
    print('done!')
