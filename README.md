# OpticalProcessingToolkit

OpticalProcessingToolkit contains Python tools for optical data and image processing. It includes `GMRProcessor` for guided-mode resonance (GMR) image analysis and `RamanSpectroscopy` for Raman CSV input and application logging.

## Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup and quick start](#setup-and-quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project and API reference](#project-and-api-reference)
- [Repository layout](#repository-layout)
- [Logging](#logging)
- [Testing](#testing)

## Overview

This repository contains two Python projects:

- `GMRProcessor` contains configuration files, file and path helpers, image-analysis methods, experiment scripts, and logging support.
- `RamanSpectroscopy` contains Raman CSV input support and project-specific logging support.

## Prerequisites

- Python 3.
- An environment that provides the packages imported by the source files: NumPy, pandas, PyYAML, Pydantic, SciPy, and OpenCV.

The repository has no dependency manifest. It does not provide a `requirements.txt` file or another supported dependency installation command.

## Setup and quick start

1. Open the repository root as the working directory.
2. Select a Python 3 interpreter with the imported packages available.
3. Replace the placeholder values in `GMRProcessor/Config/DEFAULT.yml` for the experiment you want to process.
4. Create or edit the root-level `local_config.yml` file and set both required YAML keys, `GMR_DATA_ROOT` and `RAMAN_DATA_ROOT`, to the local parent directories that contain the experiment data.
5. Preview application-log cleanup:

   ```powershell
   python GMRProcessor/Logging/cleanup_logs.py --dry-run
   ```

   To preview cleanup for RamanSpectroscopy logs, run:

   ```powershell
   python RamanSpectroscopy/Logging/cleanup_logs.py --dry-run
   ```

Run the command without `--dry-run` only when you want to delete matching log files that contain no retention marker.

The local configuration file is required by both experiment scripts and uses
this format. Replace the example paths with paths appropriate to your local
data layout:

```yaml
GMR_DATA_ROOT: D:/data/gmr
RAMAN_DATA_ROOT: D:/data/raman
```

`local_config.yml` is ignored by Git through the `local_config.yml` rule in
`.gitignore`, so local directory paths remain outside version control. The
scripts do not read data from these roots directly; they append their
project-specific experiment directory names. `TimeExperiment.py` requires
`GMR_DATA_ROOT`, and `IntegrationTime.py` requires `RAMAN_DATA_ROOT`; missing
keys raise `KeyError` when the scripts load the YAML file.

## Configuration

The files in `GMRProcessor/Config/` define the current configuration data:

- `DEFAULT.yml` is the active default loaded by `ExperimentalConfiguration`. It currently uses `UoY` as `SENSOR_TYPE`, `tif` as `IMAGE_TYPE`, `gaussian` as `ANALYSIS_METHOD`, `0` sub-ROIs, and a 60-second measurement interval.
- `IMEC-II.yml` is an IMEC-II configuration template. It uses `IMEC-II` as `SENSOR_TYPE` and otherwise contains placeholder and example values.
- `IMEC-II.json` stores geometry and grating-period data for `IMEC-II 3` and `IMEC-II 4`. The `IMEC-II 3` entry also includes `Wavelength` and `Micron to Pixel`. Current Python modules do not load this JSON file directly.

`UserConfigModel` has different field defaults from `DEFAULT.yml`: its default `SENSOR_TYPE` is `IMEC-II`, and its default `ANALYSIS_METHOD` is `max_intensity`. The model requires positive `SENSOR_SERIAL_NUMBER`, `SETUP_SERIAL_NUMBER`, and `DEVICE_SERIAL_NUMBER` values. It requires non-negative `NUMBER_SUB_ROIS` and `MEASUREMENT_INTERVAL` values, and constrains sensor, image, and analysis values through enums.

`creates_new_configs()` updates the supplied model in place. It sets `ROOT_PATH`, `SAVE_PATH`, both sensor and setup serial numbers, the sensor and chip values derived from a `TYPE NUMBER` chip string, and sets `FIGURE_FILENAME` to the string `'None'`. It writes the resulting YAML file under the supplied root path and returns that path.

## Usage

### Run the time experiment

Before using this command, set the `GMR_DATA_ROOT` key in `local_config.yml`.
The script derives these directories:

- Measurements: `<GMR_DATA_ROOT>/Phorest/SodiumHydroxideExperiment/IE2607`
- Results: `<GMR_DATA_ROOT>/Phorest/SodiumHydroxideExperiment/ProcessedData`

The measurements directory must exist and contain sample directories. The results directory is passed to generated configurations as the save path; the script does not create or populate it yet. Sample directory names must contain two or three underscore-separated parts, such as `0_Hours_260818`, for the information/date lookup. ROI processing and result plotting are placeholders; the script currently discovers sample directories, creates and reloads image-specific configuration files, and logs their paths.

```powershell
python GMRProcessor/ExperimentScripts/TimeExperiment.py
```

### Initialize logging

These bootstrap scripts load `GMRProcessor/Logging/logging.conf`, add the project directory to `sys.path`, and configure logging for their area:

```powershell
python GMRProcessor/ImageUtils/InitializeImageUtils.py
python GMRProcessor/GeneralUtils/InitializeGeneralUtils.py
python GMRProcessor/ExperimentScripts/InitializeScripts.py
```

### Initialize RamanSpectroscopy logging

Run the RamanSpectroscopy bootstrap script from the repository root to configure its console and rotating file handlers:

```powershell
python RamanSpectroscopy/GeneralUtils/InitializeGeneralUtils.py
```

### Run Raman integration-time setup

Before using this script, set the `RAMAN_DATA_ROOT` key in
`local_config.yml`. It derives `<RAMAN_DATA_ROOT>/TPBExperiment` and prints
the resulting directory iterator. The current script does not iterate over
the directory, read CSV files, or perform integration-time processing, so no
additional file layout is verified here.

```powershell
python RamanSpectroscopy/ExperimentScripts/IntegrationTime.py
```

## Project and API reference

### `GMRProcessor/GeneralUtils/`

`InitializeGeneralUtils.py` initializes shared logging. `FileIO.py` provides configuration models and experiment path helpers.

#### `FileIO.py`

- `ExperimentalConfiguration(parameters: Mapping[str, Path | str]) -> None` stores paths and metadata, then loads `Config/DEFAULT.yml` through `load_user_config()`. Missing required mapping keys raise `KeyError`.
- `ExperimentalConfiguration.get_measurement_paths() -> list[Path]` returns child directories of `Experiment Path` when `Measurement Type == "Time"`; other types return an empty list. Missing paths raise `FileNotFoundError`, non-directories raise `NotADirectoryError`, and denied access can raise `PermissionError`.
- `ExperimentalConfiguration.get_info_dates() -> dict[str, list[str | Path]]` must run after path discovery. Exactly two underscore-separated name parts become `information_date`; exactly three parts use the first two as the information key and the last as the date. Other names are ignored, and duplicate keys are overwritten by later entries. Calling it before path discovery raises `AttributeError`.
- `load_user_config(file_path: Path) -> UserConfigModel` loads YAML with `yaml.safe_load()` and validates it with Pydantic. File and YAML parsing errors propagate. Validation errors are logged by field and end the process with exit code `67`.
- `saveuser_config(config: UserConfigModel, old_path: Path, new_path: Path) -> None` rewrites matching top-level keys in an existing YAML file, preserving comments, line order, and unmatched lines. Enum values use their string values; file I/O errors propagate.
- `creates_new_configs(default_config: UserConfigModel, default_path: Path, root_path: Path, results_path: Path, serial_number: int, image_name: str, chip_type: str) -> Path` mutates `default_config`, writes a copy under `root_path`, and returns its path. `chip_type` must contain a type and integer separated by a space, such as `IMEC-II 3`.

### `GMRProcessor/ImageUtils/`

`InitializeImageUtils.py` initializes logging. `ImageUtilities.py` imports OpenCV, NumPy, and the analysis functions but currently defines no utility functions or command-line entry point.

`AnalysisMethods.py` provides:

- `max_intensity(data: np.ndarray) -> Dict`: returns the maximum-value index; empty input raises `ValueError`.
- `centre(data: np.ndarray) -> Dict`: thresholds below mean plus three standard deviations and returns a one-based centre of mass. Empty, all-zero, or fully thresholded input produces `nan` and a runtime warning.
- `gaussian(data: np.ndarray) -> Dict`: fits a Gaussian and returns `amplitude`, `mean`, `stddev`, `offset`, and `rmse`. Fit `RuntimeError` and `ValueError` return `{}`; empty input raises `ValueError`, and fewer than four points can raise `TypeError`.
- `fano(data: np.ndarray) -> Dict`: fits a Fano function and returns `amplitude`, `asymmetry`, `resonance`, `gamma`, `offset`, and `rmse`. Fit `RuntimeError` and `ValueError` return `{}`; empty input raises `ValueError`, and fewer than five points can raise `TypeError`.
- `RMSE(data1: np.ndarray, data2: np.ndarray) -> float`: returns root mean square error; incompatible shapes raise `ValueError`.

The Gaussian and Fano functions use array indices as x positions and define their calculation helpers internally.

### `GMRProcessor/ExperimentScripts/`

`InitializeScripts.py` initializes logging. `TimeExperiment.py` runs the time-dependent workflow described above; its ROI and plotting sections do not yet implement processing.

### `GMRProcessor/Logging/`

`logging.conf` sends INFO-level messages to `stderr` and to a daily rotating `application_<YYYY-MM-DD>.log` file, retaining 30 backups.

`cleanup_logs.py` processes files beginning with `application_` in its own directory. `contains_retain_marker(log_file: Path) -> bool` detects case-insensitive `ERROR`, `WARNING`, `FAILURE`, or `FAILED` markers. `cleanup_logs(log_directory: Path, dry_run: bool = False) -> tuple[int, int]` deletes or previews files without a marker and returns deleted-or-previewed and retained counts. `main() -> None` parses `--dry-run`. Inspection and deletion failures raise `OSError`.

Generated application logs are runtime files and are not part of the repository layout.

### `RamanSpectroscopy/`

`RamanSpectroscopy` contains Raman CSV input support, the integration-time experiment script, and project-specific logging configuration. It has no configuration files.

#### `RamanSpectroscopy/ExperimentScripts/`

`InitializeScripts.py` initializes project logging. `IntegrationTime.py` derives the `TPBExperiment` data path from `RAMAN_DATA_ROOT`, but does not yet read data or perform integration-time processing.

#### `RamanSpectroscopy/GeneralUtils/`

`InitializeGeneralUtils.py` adds the project directory to `sys.path`, loads `Logging/logging.conf`, supplies the log directory and current date to the configuration, and emits an initialization message. `FileIO.py` defines:

- `load_csv(file_path: Path) -> tuple[np.ndarray, np.ndarray]` reads a Raman CSV file and returns wavelength and intensity columns as one-dimensional NumPy arrays. The pandas path reads rows after the first 32 header rows and skips the final footer row. If pandas is unavailable, the function uses Python's `csv` module with the same row positions. File I/O and numeric conversion errors propagate.

#### `RamanSpectroscopy/Logging/`

`logging.conf` configures INFO-level console and timed rotating file handlers. The file handler writes `application_<YYYY-MM-DD>.log` at midnight and retains 30 backups. `cleanup_logs.py` defines:

- `contains_retain_marker(log_file: Path) -> bool` returns `True` when a log contains `ERROR`, `WARNING`, `FAILURE`, or `FAILED`, case-insensitively. Read errors raise `OSError`.
- `cleanup_logs(log_directory: Path, dry_run: bool = False) -> tuple[int, int]` scans regular files beginning with `application_`, deletes or previews files without a retention marker, and returns deleted-or-previewed and retained counts. Inspection and deletion errors raise `OSError`.
- `main() -> None` parses `--dry-run`, processes the script's own logging directory, and prints the cleanup summary.

## Repository layout

```text
.
├── .github/
│   └── copilot-instructions.md
├── .gitignore
├── .vscode/
│   └── settings.json
├── GMRProcessor/
│   ├── Config/
│   │   ├── DEFAULT.yml
│   │   ├── IMEC-II.json
│   │   └── IMEC-II.yml
│   ├── ExperimentScripts/
│   │   ├── InitializeScripts.py
│   │   └── TimeExperiment.py
│   ├── GeneralUtils/
│   │   ├── FileIO.py
│   │   └── InitializeGeneralUtils.py
│   ├── ImageUtils/
│   │   ├── AnalysisMethods.py
│   │   ├── ImageUtilities.py
│   │   └── InitializeImageUtils.py
│   └── Logging/
│       ├── cleanup_logs.py
│       └── logging.conf
├── RamanSpectroscopy/
│   ├── ExperimentScripts/
│   │   ├── InitializeScripts.py
│   │   └── IntegrationTime.py
│   ├── GeneralUtils/
│   │   ├── FileIO.py
│   │   └── InitializeGeneralUtils.py
│   └── Logging/
│       ├── cleanup_logs.py
│       └── logging.conf
└── README.md
```

## Logging

Named module loggers propagate to the root logger, which writes to the console and rotating application log. `.gitignore` excludes `*.log` files and common Python cache, build, coverage, and environment artifacts.

`GMRProcessor` and `RamanSpectroscopy` use separate logging configurations in their respective `Logging/` directories. RamanSpectroscopy's configuration writes INFO-level records to `stderr` and to a midnight-rotating `application_<YYYY-MM-DD>.log` file with 30 backups. Its cleanup command retains matching log files that contain `ERROR`, `WARNING`, `FAILURE`, or `FAILED`; use `--dry-run` to preview deletions.

## Testing

No automated test suite exists, and no dependency manifest is available. Use targeted checks or Python compilation checks when validating changes, for example:

```powershell
python -m py_compile GMRProcessor/GeneralUtils/FileIO.py GMRProcessor/ImageUtils/AnalysisMethods.py GMRProcessor/Logging/cleanup_logs.py RamanSpectroscopy/GeneralUtils/FileIO.py RamanSpectroscopy/GeneralUtils/InitializeGeneralUtils.py RamanSpectroscopy/Logging/cleanup_logs.py
```
