import os
import sys
import pandas as pd

class Doc:
    """read log.lammps and extract thermo_style output
    This script reads the log without time_reset 0 and appends all
    the thermo after time_reset to a DataFrame.
    Input:
        log.lammps
    Output:
        pd.DataFrame to csv
    """


class ReadLog:
    """read log.lammps"""
