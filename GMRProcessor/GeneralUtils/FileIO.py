###############################################################################
###############################################################################
#                              File I/O Functions                             #
#                             Author: Joshua Male                             #
#                              Date: 30/04/2025                               #
#            Description: File Input, Output, and Handling Functions          #
#                            Project: GMRProcessor                            #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import os
import re
import yaml
import json
import logging
import numpy as np
import pandas as pd

from enum import Enum
from pathlib import Path
from typing import Mapping
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)


class ExperimentalConfiguration:
    """
    Class Details
    =============
    Store experiment paths and metadata used by file-processing workflows.

    Attributes
    ----------
    root_path: Path
        Root directory for the experiment.
    data_path: Path
        Directory containing measurement data.
    results_path: Path
        Directory for processed results.
    measurement_type: str
        Measurement mode used to select measurement directories.
    chip_type: str
        Chip type associated with the experiment.
    measurement_paths: list[Path]
        Measurement directories discovered by ``get_measurement_paths``.
    info_lookup: dict[str, list[str | Path]]
        Mapping built by ``get_info_dates`` from measurement directory names.

    Notes
        The supplied path values are normalized to ``Path`` objects and the
        metadata values are normalized to strings.

        Side Effects
        ------------
        Stores the configuration values as instance attributes and emits two
        ``INFO`` log records through the ``FileIO`` logger.
    -----
    Call ``get_measurement_paths`` before ``get_info_dates``.

    ---------------------------------------------------------------------------
    Update History
    ==============

    19/08/2026
    ----------
    - Initial implementation.

    """

    root_path: Path
    data_path: Path
    results_path: Path
    measurement_type: str
    chip_type: str
    measurement_paths: list[Path]
    info_lookup: dict[str, list[str | Path]]

    def __init__(
            self,
            parameters: Mapping[str, Path | str]
        ) -> None:
        """
        Function Details
        ================
        Initialize an experiment configuration from a parameter mapping.

        Parameters
        ----------
        parameters: Mapping[str, Path | str]
            Configuration values with the keys ``Root Path``,
            ``Experiment Path``, ``Results Path``, ``Measurement Type``, and
            ``Chip Type``.

        Returns
        -------
        None

        Raises
        ------
        KeyError: If a required configuration key is missing.

        Notes
        -----

        -----------------------------------------------------------------------
        Update History
        ==============

        19/08/2026
        ----------
        - Initial implementation.

        """
        self.root_path = Path(parameters["Root Path"])
        self.data_path = Path(parameters["Experiment Path"])
        self.results_path = Path(parameters["Results Path"])
        logger.info(
            'Configuration - Root Path: %s, Data Path: %s, Results Path: %s',
            self.root_path,
            self.data_path,
            self.results_path
        )
        self.measurement_type = str(parameters["Measurement Type"])
        self.chip_type = str(parameters["Chip Type"])
        logger.info(
            'Configuration - Measurement Type: %s, Chip Type: %s',
            self.measurement_type,
            self.chip_type
        )
        self.default_path = Path(
            self.root_path,
            'Config',
            'DEFAULT.yml'
        )
        self.default_config = load_user_config(file_path=self.default_path)
        logger.info(
            'Default Path: %s, Default Config: %s',
            self.default_path,
            self.default_config
        )

    def get_measurement_paths(self) -> list[Path]:
        """
        Function Details
        ================
        Find measurement directories for time-based experiments.

        Parameters
        ----------
        None.

        Returns
        -------
        measurement_paths: list[Path]
            Directories found under ``data_path`` for a ``Time`` measurement.
            Returns an empty list for other measurement types.

        Raises
        ------
        FileNotFoundError: If ``data_path`` does not exist.
        NotADirectoryError: If ``data_path`` is not a directory.
        PermissionError: If access to ``data_path`` is denied.

        Side Effects
        ------------
        Stores the discovered directories in ``self.measurement_paths`` and
        logs the search and result.

        Notes
        -----

        -----------------------------------------------------------------------
        Update History
        ==============

        19/08/2026
        ----------
        - Initial implementation.

        """
        logger.info(f'Looking for measurements in {self.data_path}')

        if self.measurement_type == "Time":
            measurement_paths = [
                directory
                for directory in self.data_path.iterdir()
                if directory.is_dir()
            ]
        else:
            measurement_paths = []
        logger.info(f'Found paths: {measurement_paths}')
        self.measurement_paths = measurement_paths
        return measurement_paths

    def get_info_dates(self) -> dict[str, list[str | Path]]:
        """
        Function Details
        ================
        Build a lookup of measurement information and dates.

        Parameters
        ----------
        None.

        Returns
        -------
        info_lookup: dict[str, list[str | Path]]
            Mapping from the information prefix in each measurement directory
            name to a ``[date, path]`` list.

        Raises
        ------
        AttributeError: If ``get_measurement_paths`` has not been called.

        Side Effects
        ------------
        Stores the lookup in ``self.info_lookup`` and logs the result.

        Notes
        -----
        Directory names must contain two or three underscore-separated parts.
        Other names are ignored, and duplicate information keys are overwritten
        by later entries.
        """
        infos, dates = [], []
        for file in self.measurement_paths:
            parts = file.stem.split('_')
            if len(parts) == 2:
                infos.append(parts[0])
                dates.append(parts[1])
            if len(parts) == 3:
                infos.append('_'.join(parts[:-1]))
                dates.append(parts[-1])
        info_lookup = {
            info: [date, path]
            for info, date, path
            in zip(infos, dates, self.measurement_paths)
        }
        self.info_lookup = info_lookup
        logger.info(f'Sample database: {info_lookup}')
        return info_lookup


class SensorType(Enum):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    UOY = 'UoY'
    IMECI = 'IMEC-I'
    IMECII = 'IMEC-II'
    CALIBRATION = 'Calibration'


class ImageType(Enum):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    PNG = 'png'
    JPG = 'jpg'
    TIF = 'tif'


class AnalysisMethod(Enum):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    MAX_INTENSITY = "max_intensity"
    CENTRE = "centre"
    GAUSSIAN = "gaussian"
    FANO = "fano"


class UserConfigModel(BaseModel):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    GMR_ID: str
    SENSOR_SERIAL_NUMBER: int = Field(gt=0)
    SETUP_SERIAL_NUMBER: int = Field(gt=0)
    MEASUREMENT_TYPE: str
    SENSOR_TYPE: SensorType = Field(default=SensorType.IMECII)
    CHIP_TYPE: int
    ROOT_PATH: str
    DATA_FORMAT: str
    IMAGE_TYPE: ImageType
    SAVE_PATH: str
    FIGURE_FILENAME: str
    ANALYSIS_METHOD: AnalysisMethod = Field(
        default=AnalysisMethod.MAX_INTENSITY
    )
    NUMBER_SUB_ROIS: int = Field(ge=0)
    DEVICE_SERIAL_NUMBER: int = Field(gt=0)
    MEASUREMENT_INTERVAL: int = Field(ge=0)


def saveuser_config(
        config: UserConfigModel,
        old_path: Path,
        new_path: Path
) -> None:
    """
    Function Details
    ================
    Saves a new config based on the changes made to an existing one. Do not use
    in normal circulation.

    Parameters
    ----------
    config: yaml
        Yaml structure.
    old_path, new_path: Path
        Original config path, new config path.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    30/04/2025
    ----------
    Copied and documented.

    """
    original_lines = []
    with open(old_path, 'r') as f:
        original_lines = f.readlines()

    config_dict = config.dict()

    # Convert enum values to strings
    for key, value in config_dict.items():
        if isinstance(value, Enum):
            config_dict[key] = value.value

    new_lines = []
    for line in original_lines:
        if ":" in line and not line.strip().startswith("#"):
            key = line.split(":")[0].strip()
            if key in config_dict:
                new_lines.append(f"{key}: {config_dict[key]}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(new_path, 'w') as f:
        f.writelines(new_lines)


def creates_new_configs(
        default_config: UserConfigModel,
        default_path: Path,
        root_path: Path,
        results_path: Path,
        serial_number: int,
        image_name: str,
        chip_type: str
) -> Path:
    """
    Function Details
    ================
    Build a version of the default config for each new image. Save it out.

    Parameters
    ----------
    default_config: yaml
        Yaml structure.
    default_path, root_path, results_path: Path
        Path to default config, path to chemical stability root path, path to
        results output.
    serial_number: int
        Sample ID number.
    image_name: str
        File name.
    chip_type: str
        Chip type, e.g., UoY, IMEC-I, IMEC-II

    Returns
    -------
    config_path: Path
        Path to newly created config file.

    ---------------------------------------------------------------------------
    Update History
    ==============

    30/04/2025
    ----------
    Copied and documented.

    26/05/2026
    ----------
    Added chip type to config creation.

    """
    default_config.ROOT_PATH = Path(root_path).as_posix()
    default_config.SAVE_PATH = Path(results_path).as_posix()
    default_config.FIGURE_FILENAME = 'None'
    default_config.SETUP_SERIAL_NUMBER = serial_number
    default_config.SENSOR_SERIAL_NUMBER = serial_number
    default_config.SENSOR_TYPE = chip_type.split(' ')[0]
    default_config.CHIP_TYPE = int(chip_type.split(' ')[-1])
    config_path = Path(root_path, f'{image_name}.yml')
    saveuser_config(
        config=default_config,
        old_path=default_path,
        new_path=config_path
    )
    return config_path


def load_user_config(file_path: Path) -> UserConfigModel:
    """
    Function Details
    ================
    Load user config file.

    Parameters
    ----------
    file_path: Path
        Path to config file.

    Returns
    -------
    UserConfigModel: class
        Typing.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied and documented from Chris' original coding.

    """
    with open(file=file_path, mode='r') as f:
        config_data = yaml.safe_load(f)

    try:
        return UserConfigModel(**config_data)
    except ValidationError as e:
        for err in e.errors():
            field_name = '.'.join(str(x) for x in err['loc'])
            logger.error(f'Error in field {field_name}: {err["msg"]}')
            exit(67)
