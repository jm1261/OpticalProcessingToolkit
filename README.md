# OpticalProcessingToolkit

Tools and projects for image analysis, optical processing, and resonance analysis.

## Contents

- [About](#about)
- [Projects](#projects)
- [GMRProcessor](#gmrprocessor)
  - [ImageUtilities](#imageutilities)
  - [Logging](#logging)
- [Repository Layout](#repository-layout)
- [Setup](#setup)
- [Usage](#usage)
- [Testing](#testing)

## About

OpticalProcessingToolkit is a collection of Python tools for processing optical data and images, with a current focus on guided-mode resonance (GMR) analysis.

## Projects

### GMRProcessor

`GMRProcessor` contains tools for resonance image analysis and shared processing support.

#### ImageUtilities

Path: `GMRProcessor/ImageUtilities/`

This directory contains image-analysis methods.

##### AnalysisMethods.py

Defines the `AnalysisMethods` module logger and image-analysis functions.

###### `max_intensity(data: np.ndarray) -> Dict`

Returns the index of the maximum intensity value in `data`.

- `data`: Array containing intensity values.
- Returns a dictionary containing the index under the `'max_intensity'` key.
- Raises `ValueError` when `data` is empty.

###### `centre(data: np.ndarray) -> Dict`

Calculates the centre of mass of the values at or above a threshold of three standard deviations above the mean. Values below that threshold are set to zero before calculating the centre using one-based array positions.

- `data`: Array containing intensity values.
- Returns a dictionary containing the calculated centre under the `'centre'` key.
- Empty data produces `nan` and a runtime warning from the division.

###### `gaussian(data: np.ndarray) -> Dict`

Fits a Gaussian curve to one-dimensional intensity data using the array indices as the x positions.

- `data`: Array containing intensity values sampled at uniform positions.
- Returns a dictionary containing `'amplitude'`, `'mean'`, `'stddev'`, `'offset'`, and `'rmse'`. Returns an empty dictionary when the fit raises `RuntimeError` or `ValueError` during fitting.
- Empty input raises `ValueError` while the initial fit parameters are prepared. Fewer than four data points raises `TypeError` from the fitting procedure because the Gaussian has four parameters.

Internal helper:

- `gaussian_function(x, a, mu, sigma, offset)`: Calculates the Gaussian value for the supplied x values and parameters.

###### `fano(data: np.ndarray) -> Dict`

Fits a Fano function to the intensity data using the array indices as the x positions.

- `data`: Array containing intensity values for the fit.
- Returns a dictionary containing `'amplitude'`, `'assymmetry'`, `'resonance'`, `'gamma'`, `'offset'`, and `'rmse'`. Returns an empty dictionary when the fit raises `RuntimeError` or `ValueError` during fitting.
- Empty input raises `ValueError` while the initial fit parameters are prepared. Fewer than five data points raises `TypeError` from the fitting procedure because the Fano function has five parameters.

Internal helper:

- `fano_function(x, amp, assym, res, gamma, offset)`: Calculates the Fano value for the supplied x values and parameters.

###### `RMSE(data1: np.ndarray, data2: np.ndarray) -> float`

Calculates the root mean square error between two arrays.

- `data1`: First array of values.
- `data2`: Second array of values.
- Returns the root mean square error as a float.
- Raises `ValueError` when the arrays cannot be broadcast together.

#### Logging

Path: `GMRProcessor/Logging/`

This directory provides shared logging configuration and log maintenance utilities.

##### logging.conf

Configures INFO-level console and daily rotating file logging. Log output is written to `application.log` and rotated daily, with up to 30 days retained.

##### cleanup_logs.py

Provides the following functions:

###### `contains_retain_marker(log_file: Path) -> bool`

Checks whether a log file contains an error, warning, or failure marker.

- `log_file`: Log file to inspect.
- Returns `True` when the file contains `ERROR`, `WARNING`, `FAILURE`, or `FAILED`; otherwise returns `False`.

###### `cleanup_logs(log_directory: Path, dry_run: bool = False) -> tuple[int, int]`

Deletes generated `application.log*` files that do not contain a retain marker and reports the number deleted and retained.

- `log_directory`: Directory containing generated application log files.
- `dry_run`: When `True`, reports files that would be deleted without removing them.
- Returns a `(deleted, retained)` count tuple.

###### `main() -> None`

Parses command-line options and runs log cleanup in the directory containing the script.

### Other Projects

No other top-level projects are currently present in the repository. Add new projects to this section and to the contents list as they are created.

## Repository Layout

```text
.
├── GMRProcessor/
│   ├── ImageUtilities/
│   │   └── AnalysisMethods.py
│   └── Logging/
│       ├── cleanup_logs.py
│       ├── logging.conf
│       └── application.log
├── README.md
└── .github/
```

## Setup

The repository includes a Python virtual environment directory named `.venv`. Activate or select a Python 3 environment before running scripts. No dependency manifest is currently present.

## Usage

Run log cleanup from the repository root:

```powershell
python GMRProcessor/Logging/cleanup_logs.py --dry-run
python GMRProcessor/Logging/cleanup_logs.py
```

Scripts can load the shared logging configuration with `logging.config.fileConfig` using `GMRProcessor/Logging/logging.conf`.

## Testing

No automated test suite is currently present. Validate changes with targeted Python checks and compile checks such as:

```powershell
python -m py_compile GMRProcessor/Logging/cleanup_logs.py
```
