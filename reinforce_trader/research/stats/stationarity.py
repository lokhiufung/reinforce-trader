import typing

import numpy as np
from statsmodels.tsa.stattools import adfuller


# stationarity
def perform_adf_test(array: np.ndarray) -> typing.Dict[str, float]:
    """
    Perform the Augmented Dickey-Fuller test on a time series.

    :param series: Time series data.
    :return: ADF test result with test statistic, p-value, and critical values.
    """
    adf_test = adfuller(array, autolag='AIC')  # Using AIC to choose the lag
    value_names = ['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used']
    result = {name: value for name, value in zip(value_names, adf_test[0:4])}

    for key, value in adf_test[4].items():
        result[f'critical_value_{key}'] = value
    return result