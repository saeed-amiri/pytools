import os, sys, re
import readline
import pandas as pd
import numpy as np

class DOC:
    """
    A script to correct the bond problem in LAMMPS's write_data command and the boundary conditions.
    These scripts read the data file from write_data, check the distance between particles that have a bond between them;
    if the distance between two particles that have shared a bond is bigger than the HALF OF THE BOX SIZE, move the particle,
    with smaller z close to the other one, i.e., just adding the length of the box to the z component.
    usages: {sys.argv[0]} system.data
    """

class FILEERROR:
    """
    there is problem in the header of the DATAFILE,
    maybe long header!\n
    """

class HEADER:
    """
    read haeder data of the data file
    """
    def __init__(self) -> None:
        self.atomsLine = 0

    def check_file(self) -> None:
        FILECHECK = False
        MAXHEADER = 200
        linecount = 0
        with open(DATAFILE, 'r') as f:
            while True:
                linecount += 1
                line = f.readline()
                print(line.strip())
                if line.startswith('Atoms'):
                    FILECHECK = True
                    self.atomsLine = linecount
                    break
                if linecount > MAXHEADER:
                    err = FILEERROR()
                    exit(err.__doc__)
                if not line:
                    exit("wrong data file\n")

class ATOMS:
    """
    read atoms coordinates
    """
    def __init__(self) -> None:
        pass

class BONDS:
    """
    read bonds
    """
    def __init__(self) -> None:
        pass

class ANGLES:
    """
    read angles
    """
    def __init__(self) -> None:
        pass

class DIHEDRALS:
    """
    read dihedrals
    """
    def __init__(self) -> None:
        pass




if __name__ == "__main__":
    # check the input file 
    if len(sys.argv)==1:
        doc = DOC()
        exit(f'\nONE INPUT IS RWUIRED\n{doc.__doc__}')
    DATAFILE = sys.argv[1]
    header = HEADER()
    header.check_file()
