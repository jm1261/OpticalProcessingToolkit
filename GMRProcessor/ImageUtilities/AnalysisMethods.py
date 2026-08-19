###############################################################################
###############################################################################
#                            Peak Analysis Methods                            #
#                             Author: Joshua Male                             #
#                              Date: 31/03/2026                               #
#                Description: Resonance image analysis methods                #
#                            Project: GMRProcessor                            #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import logging
import numpy as np

from pathlib import Path
from scipy.optimize import curve_fit

from typing import Dict

# Start logging
logger = logging.getLogger(Path(__file__).stem)


def max_intensity(data: np.ndarray) -> Dict:
	"""
	Function Details
	================
    Return the index of the maximum intensity value in an array.

	Parameters
	----------
	data: np.ndarray
		Array containing intensity values.

	Returns
	-------
	intensity: Dict
        Dictionary containing the index of the maximum value under the
        ``'max_intensity'`` key.

	Raises
	------
    ValueError: If data is empty.

	---------------------------------------------------------------------------
	Update History
	==============

	19/08/2026
	----------
	- Initial implementation.

	"""
	return {"max_intensity": np.argmax(data)}


def centre(data: np.ndarray) -> Dict:
    """
    Function Details
    ================
    Return the thresholded centre of mass of an array.

    Parameters
    ----------
    data: np.ndarray
        Array containing intensity values.

    Returns
    -------
    centre: Dict
        Dictionary containing the centre of mass under the ``'centre'`` key.

    Raises
    ------
    None.

    Notes
    -----
    - Values below ``mean(data) + 3 * std(data)`` are set to zero.
        - Empty, all-zero, or fully thresholded data produces ``nan`` and a
            runtime warning from the division.
        - Array positions are one-based.

    ---------------------------------------------------------------------------
    Update History
    ==============
    19/08/2026
    ----------
    - Initial implementation.

    """
    threshold = (np.std(data) * 3.0) + np.mean(data)
    data = np.where(data < threshold, 0, data)
    return {
        "centre": np.sum(data * np.arange(1, len(data) + 1)) / np.sum(data)
    }


def gaussian(data: np.ndarray) -> Dict:
    """
    Function Details
    ================
    Fit a Gaussian curve to one-dimensional intensity data.

    Parameters
    ----------
    data: np.ndarray
        Array containing intensity values sampled at uniform positions.

    Returns
    -------
    fit: Dict
        Dictionary containing the fitted amplitude, mean, standard deviation,
        offset, and root mean square error. Returns an empty dictionary when
        the fit cannot be calculated.

    Raises
    ------
    ValueError: If data is empty or cannot be used to initialise the fit
        before curve fitting begins.
    TypeError: If data contains fewer points than the Gaussian has parameters.

    Notes
    -----
    - RuntimeError and ValueError from the fitting procedure are logged and
            return an empty dictionary.

    ---------------------------------------------------------------------------
    Update History
    ==============

    19/08/2026
    ----------
    - Initial implementation.

    """
    def gaussian_function(
        x: np.ndarray,
        a: float,
        mu: float,
        sigma: float,
        offset: float,
    ) -> np.ndarray:
        """
        Return Gaussian values for the supplied parameters.

        Parameters
        ----------
        x: np.ndarray
            Positions at which to evaluate the Gaussian.
        a: float
            Gaussian amplitude.
        mu: float
            Gaussian centre position.
        sigma: float
            Gaussian standard deviation.
        offset: float
            Constant vertical offset.

        Returns
        -------
        values: np.ndarray
            Gaussian values evaluated at each position.

        """
        return a * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) + offset
    xdata = np.arange(0, len(data))
    p0 = [np.max(data) - np.min(data), np.argmax(data), 1, np.mean(data)]
    try:
        popt, _ = curve_fit(gaussian_function, xdata, data, p0=p0)
    except (RuntimeError, ValueError) as e:
        logger.error(f"Gaussian fit failed: {e}")
        return {}
    error = RMSE(data, gaussian_function(xdata, *popt))
    return {
        "amplitude": popt[0],
        "mean": popt[1],
        "stddev": popt[2],
        "offset": popt[3],
        "rmse": error,
    }


def fano(data: np.ndarray) -> Dict:
    """
    Function Details
    ================
    Return the fitting parameters after fitting a fano function to the
    distribution of pixel values

    Parameters
    ----------
    data: np.ndarray
        Array containing intensity values for a Fano fit.

    Returns
    -------
    result: Dict
        Dictionary containing the fitted amplitude, ``'assymmetry'``,
        resonance, gamma, offset, and root mean square error. Returns an
        empty dictionary when the fit cannot be calculated.

    Raises
    ------
        ValueError: If data is empty or cannot be used to initialise the fit.
        TypeError: If data contains fewer points than the Fano has parameters.

        Notes
        -----
        - RuntimeError and ValueError from the fitting procedure are logged and
            return an empty dictionary.

    ---------------------------------------------------------------------------
    Update History
    ==============

    19/08/2026
    ----------
    - Initial implementation.

    """
    def fano_function(
        x: np.ndarray,
        amp: float,
        assym: float,
        res: float,
        gamma: float,
        offset: float,
    ) -> np.ndarray:
        """
        Return Fano values for the supplied parameters.

        Parameters
        ----------
        x: np.ndarray
            Positions at which to evaluate the Fano function.
        amp: float
            Fano amplitude.
        assym: float
            Fano asymmetry parameter.
        res: float
            Resonance position.
        gamma: float
            Resonance width parameter.
        offset: float
            Constant vertical offset.

        Returns
        -------
        values: np.ndarray
            Fano values evaluated at each position.

        """
        numerator = (
            (assym * gamma) + (x - res)) * ((assym * gamma) + (x - res)
        )
        denominator = (gamma * gamma) + ((x - res) * (x - res))
        return (amp * (numerator / denominator)) + offset
    xdata = np.arange(0, len(data))
    p0 = [
        np.max(data) - np.min(data), 1, np.argmax(data), len(data) / 4,
        np.mean(data)
    ]
    try:
        popt, _ = curve_fit(fano_function, xdata, data, p0=p0)
    except (RuntimeError, ValueError) as e:
        logger.error(f"Fano fit failed: {e}")
        return {}
    error = RMSE(data, fano_function(xdata, *popt))
    return {
        "amplitude": popt[0],
        "asymmetry": popt[1],
        "resonance": popt[2],
        "gamma": popt[3],
        "offset": popt[4],
        "rmse": error,
    }


def RMSE(
    data1: np.ndarray,
    data2: np.ndarray
) -> float:
    """
    Function Details
    ================
    Calculate the root mean square error between two arrays.

    Parameters
    ----------
    data1: np.ndarray
        First array of values.
    data2: np.ndarray
        Second array of values.

    Returns
    -------
    error: float
        Root mean square error between the two arrays.

    Raises
    ------
    ValueError: If the arrays cannot be broadcast together.

    ---------------------------------------------------------------------------
    Update History
    ==============

    19/08/2026
    ----------
    - Initial implementation.

    """
    squared_difference = (data1 - data2) ** 2
    mean_squared_error = np.mean(squared_difference)
    return np.sqrt(mean_squared_error)
