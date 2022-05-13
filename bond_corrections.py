import os, sys, re
import pandas as pd
import numpy as np

class DOC:
    """
    A script to correct the bond problem in LAMMPS's write_data command and the boundary conditions.
    These scripts read the data file from write_data, check the distance between particles that have a bond between them;
    if the distance between two particles that have shared a bond is bigger than the HALF OF THE BOX SIZE, move the particle,\
        with smaller z close to the other one, i.e., just adding the length of the box to the z component.
    """