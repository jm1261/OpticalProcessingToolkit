###############################################################################
###############################################################################
#                               Time Experiment                               #
#                             Author: Joshua Male                             #
#                              Date: 19/08/2026                               #
#          Description: Experiment script for time-dependent analysis         #
#                            Project: GMRProcessor                            #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import InitializeScripts  #noqa

import logging
import GeneralUtils.FileIO as io

from pathlib import Path

# Start logging
logger = logging.getLogger(name=Path(__file__).stem)

# Define the path to the experiment
experiment = {
    "Root Path": Path(Path().absolute(), 'GMRProcessor'),
    "Experiment Path": Path(
        'K://Josh',
        'Phorest',
        'SodiumHydroxideExperiment',
        'IE2607'
    ),
    "Results Path": Path(
        'K://Josh',
        'Phorest',
        'SodiumHydroxideExperiment',
        'ProcessedData'
    ),
    "Measurement Type": "Time",
    "Chip Type": "IMEC-II 4",
    "Serial Number": 260818
}
logger.info(f'Processing Experiment: {experiment}')

# Load images and select the region of interest (ROI)
config = io.ExperimentalConfiguration(parameters=experiment)
measurement_paths = config.get_measurement_paths()
info_lookup = config.get_info_dates()

for sample, values in info_lookup.items():
    logger.info(f'Processing sample: {sample}, with details: {values}')
    date, datapath = values
    new_user_config = io.creates_new_configs(
        default_config=config.default_config,
        default_path=config.default_path,
        root_path=Path(datapath),
        results_path=config.results_path,
        serial_number=experiment["Serial Number"],
        image_name=f'{sample}_{date}',
        chip_type=config.chip_type
    )
    image_config = io.load_user_config(file_path=new_user_config)
    logger.info(f'Config file created at: {new_user_config}')

# Process ROI data

# Plot the results
