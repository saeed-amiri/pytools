import os, sys, re
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

class HEADER:
    """
    read haeder data of the data file
    """
    def __init__(self) -> None:
        pass

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



# check the input file 
if len(sys.argv)==1:
    doc = DOC()
    exit(f'\nONE INPUT IS RWUIRED\n{doc.__doc__}')

