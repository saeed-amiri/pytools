import os
from pprint import pprint
import sys
import pandas as pd


class Doc:
    """read log.lammps and extract thermo_style output
    This script reads the log without 'time_reset 0' and appends all
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
        lines: list[str]  # A list of the thermo lines
        header: str  # A str of the thermo_style
        lines, header = self.get_lines()
        self.df = self.mk_df(lines, header)

    def get_lines(self) -> tuple[list[str], str]:
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
                elif line.strip().startswith('Step'):
                    step = True
                    head = line.strip()
                elif line.strip().startswith('Loop'):
                    step = False
                    run = False
                elif line and not loop:
                    if run and step:
                        line_list.append(line.strip())
                if not line:
                    break
        return line_list, head

    def mk_df(self, lines: list[str], header: str) -> pd.DataFrame:
        """make DataFrame from the list of the lines"""
        columns_names: list[str] = self.break_header(header)
        line_list: list[list[str]] = self.break_lines(lines)
        df = pd.DataFrame(line_list, columns=columns_names)
        df.drop_duplicates(subset=['Step'], inplace=True)
        return df

    def break_header(self, header: str) -> list[str]:
        return header.split(' ')

    def break_lines(self, lines: list[str]) -> list[list[str]]:
        """break the lines of the thermo-lines"""
        temp = [item.split(' ') for item in lines]
        return [[sub_item for sub_item in item if sub_item] for item in temp]


if __name__ == "__main__":
    log = ReadLog()
