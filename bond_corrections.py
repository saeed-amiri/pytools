import typing
import sys
import pandas as pd
import numpy as np


class DOC:
    """
    A script to correct the bond problem in LAMMPS's write_data
    command and the boundary conditions.
    These scripts read the data file from write_data, check the
    distance between particles that have a bond between them;
    if the distance between two particles that have shared a bond is
    bigger than the HALF OF THE BOX SIZE, move the particle,with
    smaller z close to the other one, i.e., just adding the length of
    the box to the z component.
    [ checking PEP8
        ~/.local/bin/pycodestyle bond_corrections.py
        and typing"
        ~/.local/bin/mypy bond_corrections.py
    ]
    The script is wrote for INFILE which have hybrid style, i.e.:

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
    there is problem in the header of the INFILE,
    maybe a long header!\n
    """


class HEADER:
    """
    read haeder data of the data file
    check the number of the lines, atom, bond ... informations
    get the box , pairs, ... coefficents
    Use this class to read the header of the file (LAMMPS data file),
    and the file should have Masses with their name specified after (#)
    e.g.:

        Masses

        1 1.008000 # H
        2 16.000000 # OH
        3 16.000000 # OB
        4 28.059999 # Si

    it will return a few attributes for the class if they existed:
    Masses, Pair, and Angel and Dihedral coefficients. And also the name
    of the atoms types.
    The class BODY needs' names' to read the data file.
    """

    def __init__(self) -> None:
        self.atomsLine: int = 0
        self.atomsLine = self.check_file()
        print(f'number of header lines: {self.atomsLine}\n')
        self.read_header()

    def check_file(self) -> int:
        """ Check header
        input:
            - INFILE (lammps data file)
        output:
            - number of header lines
        """
        # An integer to prevent over-reading in case of header bugs
        MAXHEADER: int = 1000
        # track the number of lines in the hedaer
        linecount: int = 0
        with open(INFILE, 'r') as f:
            while True:
                linecount += 1
                line = f.readline()
                if line.strip().startswith('Atoms'):
                    atomsLine = linecount
                    break
                if linecount > MAXHEADER:
                    err = FILEERROR()
                    exit(err.__doc__)
                if not line:
                    exit("wrong data file\n")
        return atomsLine

    def read_header(self) -> None:
        """read header to get all the available info
        Read header now and get the data
        """
        # Setting dictionaries to save data of each block in the header
        self.set_attrs()
        # Setting flags to save data correctly
        Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
            = False, False, False, False, False, False
        # Track the number of lines
        linecount: int = 0
        with open(INFILE, 'r') as f:
            while True:
                linecount += 1
                if linecount > self.atomsLine:
                    break
                line: str = f.readline()
                if line.strip().endswith("atoms"):
                    self.NATOMS = int(line.strip().split(' ')[0])
                elif line.strip().endswith("atom types"):
                    self.NATomTyp = int(line.strip().split(' ')[0])
                elif line.strip().endswith("bonds"):
                    self.NBonds = int(line.strip().split(' ')[0])
                elif line.strip().endswith("bond types"):
                    self.NBondTyp = int(line.strip().split(' ')[0])
                elif line.strip().endswith("angles"):
                    self.NAngles = int(line.strip().split(' ')[0])
                elif line.strip().endswith("angle types"):
                    self.NAngleTyp = int(line.strip().split(' ')[0])
                elif line.strip().endswith("dihedrals"):
                    self.NDihedrals = int(line.strip().split(' ')[0])
                elif line.strip().endswith("dihedral typss"):
                    self.NDihedralsTyp = int(line.strip().split(' ')[0])
                elif line.strip().endswith("xhi"):
                    self.Xlim = self.get_axis_lim(line.strip().split('xlo')[0])
                elif line.strip().endswith("yhi"):
                    self.Ylim = self.get_axis_lim(line.strip().split('ylo')[0])
                elif line.strip().endswith("zhi"):
                    self.Zlim = self.get_axis_lim(line.strip().split('zlo')[0])
                # setting up Flages for reading the cards of data in the file
                elif line.strip().startswith("Masses"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff,\
                        Atoms = True, False, False, False, False, False
                elif line.strip().startswith("Pair"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff,\
                        Atoms = False, True, False, False, False, False
                elif line.strip().startswith("Bond Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff,\
                        Atoms = False, False, True, False, False, False
                elif line.strip().startswith("Angle Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff,\
                        Atoms = False, False, False, True, False, False
                elif line.strip().startswith("Dihedral Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff,\
                        Atoms = False, False, False, False, True, False
                elif line.strip().startswith("Atoms"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff,\
                        Atoms = False, False, False, False, False, True
                elif line.strip():
                    if Masses:
                        self.get_masses(line.strip(), 'Masses')
                    elif PairCoeff:
                        self.get_pair_coeff(line.strip(), 'Pair')
                    elif BondCoeff:
                        self.get_bond_coeff(line.strip(), 'Bond')
                    elif AngleCoeff:
                        self.get_angle_coeff(line.strip(), 'Angle')
                    elif DihedralCoeff:
                        self.get_dihedral_coeff(line.strip(), 'Dihedral')
                if Atoms:
                    break
                if not line:
                    break

    def set_attrs(self) -> None:
        self.Names: dict[int, str] = dict()
        self.Masses: dict[int, float] = dict()
        self.PairCoeff: dict[int, typing.Any] = dict()
        self.BondCoeff: dict[int, typing.Any] = dict()
        self.AngleCoeff: dict[int, typing.Any] = dict()
        self.DihedralCoeff: dict[int, typing.Any] = dict()

    def get_axis_lim(self, lim) -> list:
        lim = lim.split(' ')
        lim = [float(item) for item in lim if item]
        return lim

    def get_masses(self, line, check) -> None:
        # stting the nth row of the dictionary
        if check not in line:
            typ = int(line.split(' ')[0])
            mass = float(line.split(' ')[1])
            try:
                atom_name = line.split('#')[1].strip()
            except IndexError:
                atom_name = None
            self.Masses[typ] = mass
            self.Names[typ] = atom_name

    def get_pair_coeff(self, line, check) -> None:
        # stting the nth row of the dictionary
        if check not in line:
            line = line.split(' ')
            typ = int(line[0])
            i_style = line[1]
            i_coeff = line[2:]
            self.PairCoeff[typ] = dict(
                                        style=i_style,
                                        coeff=i_coeff
                                       )

    def get_bond_coeff(self, line, check) -> None:
        # stting the nth row of the dictionary
        if check not in line:
            line = line.split(' ')
            typ = int(line[0])
            i_style = line[1]
            i_coeff = line[2:]
            self.BondCoeff[typ] = dict(
                                        style=i_style,
                                        coeff=i_coeff
                                       )

    def get_angle_coeff(self, line, check) -> None:
        # stting the nth row of the dictionary
        if check not in line:
            line = line.split(' ')
            typ = int(line[0])
            i_style = line[1]
            i_coeff = line[2:]
            self.AngleCoeff[typ] = dict(
                                        style=i_style,
                                        coeff=i_coeff
                                       )

    def get_dihedral_coeff(self, line, check) -> None:
        # stting the nth row of the dictionary
        if check not in line:
            line = line.split(' ')
            typ = int(line[0])
            i_style = line[1]
            i_coeff = line[2:]
            self.DihedralCoeff[typ] = dict(
                                            style=i_style,
                                            coeff=i_coeff
                                           )


class BODY:
    """
    read the data for atoms,velocities, bonds, angles, dihedrals
    It needs the names of the atoms read by HEADER class
    """

    def __init__(self, names) -> None:
        self.Name = names
        del names

    def read_body(self):
        self.Atoms, self.Velocities, self.Bonds, self.Angles, self.Dihedrals\
            = dict(), dict(), dict(), dict(), dict()
        Atoms, Velocities, Bonds, Angles, Dihedrals\
            = False, False, False, False, False

        with open(INFILE, 'r') as f:
            while True:
                line = f.readline()
                if line.strip().startswith('Atoms'):
                    Atoms, Velocities, Bonds, Angles, Dihedrals\
                        = True, False, False, False, False
                if line.strip().startswith('Velocities'):
                    Atoms, Velocities, Bonds, Angles, Dihedrals\
                        = False, True, False, False, False
                if line.strip().startswith('Bonds'):
                    Atoms, Velocities, Bonds, Angles, Dihedrals\
                        = False, False, True, False, False
                if line.strip().startswith('Angles'):
                    Atoms, Velocities, Bonds, Angles, Dihedrals\
                        = False, False, False, True, False
                if line.strip().startswith('Dihedrals'):
                    Atoms, Velocities, Bonds, Angles, Dihedrals\
                        = False, False, False, False, True
                if line.strip():
                    if Atoms:
                        self.get_atoms(line.strip())
                    if Velocities:
                        self.get_velocities(line.strip())
                    if Bonds:
                        self.get_bonds(line.strip())
                    if Angles:
                        self.get_angles(line.strip())
                    if Dihedrals:
                        self.get_dihedrals(line.strip())
                if not line:
                    break
            self.Atoms_df = pd.DataFrame.from_dict(
                            self.Atoms, orient='columns').T
            self.Bonds_df = pd.DataFrame.from_dict(self.Bonds).T

    def get_atoms(self, line) -> None:
        # stting the nth row of the dictionary
        if 'Atoms' not in line:
            line = line.split()
            line = [item for item in line if item]
            atom_id = int(line[0])
            i_mol = int(line[1])
            i_typ = int(line[2])
            i_charge = float(line[3])
            i_x = float(line[4])
            i_y = float(line[5])
            i_z = float(line[6])
            i_name = self.Name[i_typ]
            try:
                i_nx = int(line[7])
                i_ny = int(line[8])
                i_nz = int(line[9])
            except ValueError:
                i_nx = 0
                i_ny = 0
                i_nz = 0
            self.Atoms[atom_id] = dict(
                                        atom_id=atom_id,
                                        mol=i_mol,
                                        typ=i_typ,
                                        charge=i_charge,
                                        x=i_x,
                                        y=i_y,
                                        z=i_z,
                                        nx=i_nx,
                                        ny=i_ny,
                                        nz=i_nz,
                                        cmt='#',
                                        name=i_name
                                       )

    def get_velocities(self, line) -> None:
        # stting the nth row of the dictionary
        if 'Velocities' not in line:
            line = line.split()
            line = [item for item in line if item]
            atom_id = int(line[0])
            i_vx = float(line[1])
            i_vy = float(line[2])
            i_vz = float(line[3])
            self.Velocities[atom_id] = dict(
                                             vx=i_vx,
                                             vy=i_vy,
                                             vz=i_vz
                                            )

    def get_bonds(self, line) -> None:
        # stting the nth row of the dictionary
        if 'Bonds' not in line:
            line = line.split()
            line = [int(item) for item in line if item]
            bond_id = line[0]
            i_typ = int(line[1])
            i_ai = int(line[2])
            i_aj = int(line[3])
            self.Bonds[bond_id] = dict(
                                        typ=i_typ,
                                        ai=i_ai,
                                        aj=i_aj
                                       )

    def get_angles(self, line) -> None:
        # stting the nth row of the dictionary
        if "Angles" not in line:
            line = line.split()
            line = [int(item) for item in line if item]
            angle_id = line[0]
            i_typ = int(line[1])
            i_ai = int(line[2])
            i_aj = int(line[3])
            i_ak = int(line[4])
            self.Angles[angle_id] = dict(
                                         typ=i_typ,
                                         ai=i_ai,
                                         aj=i_aj,
                                         ak=i_ak
                                        )

    def get_dihedrals(self, line) -> None:
        # stting the nth row of the dictionary
        if "Dihedrals" not in line:
            line = line.split()
            line = [int(item) for item in line if item]
            dihedrals_id = line[0]
            i_typ = int(line[1])
            i_ai = int(line[2])
            i_aj = int(line[3])
            i_ak = int(line[4])
            i_ah = int(line[5])
            self.Dihedrals[dihedrals_id] = dict(
                                                 typ=i_typ,
                                                 ai=i_ai,
                                                 aj=i_aj,
                                                 ak=i_ak,
                                                 ah=i_ah
                                                )


class UPDATE:
    """
    Update data, checking the bonds
    Based on the this:
    https://docs.lammps.org/2001/data_format.html
    nx, ny, and nz:
    ``The final 3 nx,ny,nz values on a line of the Atoms entry are optional.
    LAMMPS only reads them if the "true flag" command is specified in
    the input command script. Otherwise they are initialized to 0 by
    LAMMPS.
    Their meaning, for each dimension, is that "n" box-lengths are
    added to xyz to get the atom's "true" un-remapped position.
    This can be useful in pre- or post-processing to enable the
    unwrapping of long-chained molecules which wind thru the periodic
    box one or more times. The value of "n" can be positive, negative,
    or zero. For 2-d simulations specify nz as 0.``

    Here I add the n * box to each coordinates!


    """
    def __init__(self, Bonds, Atoms, header) -> None:
        self.Bonds = Bonds
        self.Atoms = Atoms
        self.header = header
        del Bonds, Atoms, header

    def update_atoms(self) -> None:
        self.set_sizes()
        xyz_array = self.conver_to_array()
        new_xyz = self.crct_coord(xyz_array)
        df = self.shift_atoms(new_xyz)

    def set_sizes(self):
        self.boxx = self.header.Xlim[1]-self.header.Xlim[0]
        self.boxy = self.header.Ylim[1]-self.header.Ylim[0]
        self.boxz = self.header.Zlim[1]-self.header.Zlim[0]

    def set_extermun(self):
        self.XMIN = np.min(self.df.x)
        self.XMAX = np.max(self.df.x)
        self.YMIN = np.min(self.df.y)
        self.YMAX = np.max(self.df.y)
        self.ZMIN = np.min(self.df.z)
        self.ZMAX = np.max(self.df.z)

    def conver_to_array(self) -> np.array:
        """convert xyz nx ny nz to array"""
        # first sort the df based on the atom id
        self.Atoms = self.Atoms.sort_values(by=['atom_id'])
        # convert to np.array
        columns = ['x', 'y', 'z', 'nx', 'ny', 'nz']
        xyz_array = self.Atoms[columns].to_numpy()
        return xyz_array
    
    def crct_coord(self, xyz: np.array) -> np.array:
        """based on the last three, update the first three coulmns"""
        for i in xyz:
            i[0] += self.boxx*i[3]
            i[1] += self.boxx*i[4]
            i[2] += self.boxx*i[5]
        return xyz
    
    def shift_atoms(self, xyz: np.array) -> pd.DataFrame:
        """conver the updated the array atoms coordinates to DataFrame"""
        columns = ['x', 'y', 'z', 'nx', 'ny', 'nz']
        df = pd.DataFrame(xyz, columns=columns)
        return df

    def mk_atoms(self, df: pd.DataFrame) -> pd.DataFrame:
        """add the other columns of the atoms card to the new atom DataFrame"""
        pass

if __name__ == "__main__":
    # check the input file
    if len(sys.argv) == 1:
        doc = DOC()
        exit(f'\nONE INPUT IS RWUIRED\n{doc.__doc__}')
    INFILE = sys.argv[1]
    OUTEX = INFILE.split('.')[0]
    header = HEADER()
    body = BODY(header.Names)
    body.read_body()
    update = UPDATE(body.Bonds, body.Atoms_df, header)
    update.update_atoms()
