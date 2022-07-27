import os
import sys
import pandas as pd


class Doc:
    """read log.lammps and extract thermo_style output
    This script reads the log without time_reset 0 and appends all
    the thermo after time_reset to a DataFrame.
    The thermo_style must include 'Step' key, the rest is arbitrary
    and also during the simulation the thermo_style should reamin the
    same.
    Input:
        log.lammps
    Output:
        pd.DataFrame to csv
    """


class ReadLog:
    """read log.lammps"""
    def __init__(self) -> None:
        self.fanme = sys.argv[1]
        self.read_log()

    def read_log(self) -> None:
        """reading the file"""
        run: bool = False  # If line starts with 'run'
        loop: bool = False  # If line starts with 'Loop'
        step: bool = False  # If line starts with 'Step'
        line_list: list[str] = []  # To save the thermo line line
        head: str  # To save the columns name for the DataFrame
        with open(self.fanme, 'r') as f:
            while True:
                line = f.readline()
                if line.strip().startswith('run'):
                    run = True
                if line.strip().startswith('Step'):
                    step = True
                    head = line
                if line:
                    if run and step:
                        line_list.append(line)
                if line.strip().startswith('Loop'):
                    step = False
                    run = False
                if not line:
                    break


if __name__ == "__main__":
    log = ReadLog()
