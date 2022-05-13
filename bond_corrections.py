import os, sys, re
from pprint import pprint
import pandas as pd
import numpy as np

class DOC:
    """
    A script to correct the bond problem in LAMMPS's write_data command and the boundary conditions.
    These scripts read the data file from write_data, check the distance between particles that have a bond between them;
    if the distance between two particles that have shared a bond is bigger than the HALF OF THE BOX SIZE, move the particle,
    with smaller z close to the other one, i.e., just adding the length of the box to the z component.
    The script is wrote for DATAFILE which have hybrid style, i.e.:
    
    Pair Coeffs # lj/cut/coul/long

    1 lj/cut/coul/long 0.1553 3.166
    2 lj/cut/coul/long 0 0
    
    Bond Coeffs # harmonic

    1 harmonic 600 1
    2 harmonic 268 1.526
    
    Angle Coeffs # harmonic

    1 harmonic 75 109.47
    2 harmonic 58.35 112.7

    Dihedral Coeffs # opls

    1 opls 1.3 -0.05 0.2 0
    2 opls 0 0 0.3 0
    
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
        self.atomsLine = self.check_file()
        print(f'number of header lines: {self.atomsLine}\n')
        self.read_header()


    def check_file(self) -> int:
        FILECHECK = False
        MAXHEADER = 1000
        linecount = 0
        with open(DATAFILE, 'r') as f:
            while True:
                linecount += 1
                line = f.readline()
                if line.startswith('Atoms'):
                    FILECHECK = True
                    atomsLine = linecount
                    break
                if linecount > MAXHEADER:
                    err = FILEERROR()
                    exit(err.__doc__)
                if not line:
                    exit("wrong data file\n")
        return atomsLine

    

    def read_header(self):
        """read header to get all the available info"""
        self.Masses, self.PairCoeff, self.BondCoeff, self.AngleCoeff, self.DihedralCoeff=dict(),dict(),dict(),dict(),dict()
        Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff=False, False, False, False, False
        linecount = 0
        with open(DATAFILE, 'r') as f:
            while True:
                linecount += 1
                line = f.readline()
                if line.strip().endswith("atoms"):      self.NATOMS = int(line.strip().split(' ')[0])
                if line.strip().endswith("atom types"): self.NATomTyp = int(line.strip().split(' ')[0])
                if line.strip().endswith("bonds"):      self.NBonds = int(line.strip().split(' ')[0])
                if line.strip().endswith("bond types"): self.NBondTyp = int(line.strip().split(' ')[0])
                if line.strip().endswith("angles"):     self.NAngles = int(line.strip().split(' ')[0])
                if line.strip().endswith("angle types"):self.NAngleTyp = int(line.strip().split(' ')[0])
                if line.strip().endswith("dihedrals"):  self.NDihedrals = int(line.strip().split(' ')[0])
                if line.strip().endswith("dihedral typss"): self.NDihedralsTyp = int(line.strip().split(' ')[0])
                if line.strip().endswith("xhi"): self.Xlim = self.get_axis_lim(line.strip().split('xlo')[0])
                if line.strip().endswith("yhi"): self.Ylim = self.get_axis_lim(line.strip().split('ylo')[0])
                if line.strip().endswith("zhi"): self.Zlim = self.get_axis_lim(line.strip().split('zlo')[0])

                if line.strip().startswith("Masses"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff = True, False, False, False, False
                if line.strip().startswith("Pair"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff = False, True, False, False, False
                if line.strip().startswith("Bond Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff = False, False, True, False, False
                if line.strip().startswith("Angle Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff = False, False, False, True, False
                if line.strip().startswith("Dihedral Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff = False, False, False, False, True
                if line.strip():
                    if Masses: self.get_masses(line.strip(), 'Masses')
                    if PairCoeff: self.get_pair_coeff(line.strip(), 'Pair')
                    if BondCoeff: self.get_bond_coeff(line.strip(), 'Bond')
                    if AngleCoeff: self.get_angle_coeff(line.strip(), 'Angle')
                    if DihedralCoeff: self.get_dihedral_coeff(line.strip(), 'Dihedral')
                if linecount > self.atomsLine: 
                    if not Masses:
                        # print(linecount)
                        # print(linecount, Masses)
                        # err = FILEERROR()
                        # print(f'{err.__doc__}')
                        break
                if not line: break

    def get_body(self):
        
        with open(DATAFILE, 'r') as f:

            pass
    
    def get_axis_lim(self, lim) -> list:
        lim = lim.split(' ')
        lim = [item for item in lim if item]
        return lim
    
    def get_masses(self, line, check) -> dict:
        if check not in line: 
            typ = line.split(' ')[0]
            mass = float(line.split(' ')[1])
            self.Masses[typ]=mass
        else: pass

    def get_pair_coeff(self, line, check)-> dict:
        if check not in line: 
            line = line.split(' ')
            typ = line[0]
            self.PairCoeff[typ]=dict(style=line[1], coeff=line[2:])
        else: pass
    
    def get_bond_coeff(self, line, check)-> dict:
        if check not in line:
            line = line.split(' ')
            typ = line[0]
            self.BondCoeff[typ]=dict(style=line[1], coeff=line[2:])
        else: pass
        
    def get_angle_coeff(self, line, check)-> dict:
        if check not in line:
            line = line.split(' ')
            typ = line[0]
            self.AngleCoeff[typ]=dict(style=line[1], coeff=line[2:])
        else: pass
    
    def get_dihedral_coeff(self, line, check)-> dict:
        if check not in line:
            line = line.split(' ')
            typ = line[0]
            self.DihedralCoeff[typ]=dict(style=line[1], coeff=line[2:])
        else: pass




        

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
    pprint(header.__dict__)
