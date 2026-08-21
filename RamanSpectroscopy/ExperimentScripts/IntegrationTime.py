###############################################################################
###############################################################################
#                               Time Experiment                               #
#                             Author: Joshua Male                             #
#                              Date: 19/08/2026                               #
#          Description: Experiment script for time-dependent analysis         #
#                         Project: Raman Spectroscopy                         #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import InitializeScripts  #noqa

import yaml
import logging
import GeneralUtils.FileIO as io

from pathlib import Path

# Start logging
logger = logging.getLogger(name=Path(__file__).stem)

# Directory paths
config_path = Path(__file__).resolve().parents[2] / 'local_config.yml'
with config_path.open(mode='r', encoding='utf-8') as config_file:
    local_config = yaml.safe_load(config_file)
root_path = Path(local_config['RAMAN_DATA_ROOT'])
data_path = root_path / 'TPBExperiment'


if __name__ == '__main__':
    print(list(data_path.iterdir()))