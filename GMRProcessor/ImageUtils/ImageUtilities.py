###############################################################################
###############################################################################
#                               Image Utilities                               #
#                             Author: Joshua Male                             #
#                              Date: 30/04/2025                               #
#                     Description: Image utility functions                    #
#                            Project: GMRProcessor                            #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import cv2
import logging
import numpy as np

from pathlib import Path
from typing import Any, List, Tuple, Union
from numpy.typing import NDArray
from ImageUtils.AnalysisMethods import (
    max_intensity,
    centre,
    gaussian,
    fano
)

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)