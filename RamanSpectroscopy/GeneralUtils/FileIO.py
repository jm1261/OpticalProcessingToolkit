###############################################################################
###############################################################################
#                                   File I/O                                  #
#                             Author: Joshua Male                             #
#                              Date: 21/08/2026                               #
#           Description: Functions for loading and outputting files           #
#                         Project: Raman Spectroscopy                         #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import csv
import logging
import numpy as np

from pathlib import Path

# Start logging
logger = logging.getLogger(name=Path(__file__).stem)


def load_csv(file_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Function Details
    ===============
    Load a CSV file and return (wavelengths, intensities) as 1D numpy arrays.

    Parameters
    ----------
    file_path: Path
        Path to csv file.

    Returns
    -------
    wavelength, intensity: tuple[list, list]
        Wavelength (nm) and intensity (au) data arrays.

    Raises
    ------
    None.

    Notes
    -----
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    21/08/2026
    ----------
    - Initial implementation.

    """
    try:
        import pandas as pd
        df = pd.read_csv(
            filepath_or_buffer=file_path,
            sep=',',
            names=['Wavelength', 'Intensity'],
            header=32,
            skipfooter=1,
            engine='python'
        )
        return df['Wavelength'].to_numpy(), df['Intensity'].to_numpy()
        
    except ImportError:
        with file_path.open(newline='') as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)

        data_rows = rows[32:-1]
        wavelengths = []
        intensities = []
        for row in data_rows:
            if len(row) >= 2 and row[0] and row[1]:
                wavelengths.append(float(row[0]))
                intensities.append(float(row[1]))
                
        return np.array(wavelengths), np.array(intensities)