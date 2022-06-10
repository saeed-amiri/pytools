import sys
import pandas as pd
import re


class Doc:
    """ Converting LAMMPS data file to PDB
    This scripts temp to convert LAMMPS full atom style file to PDB file
    which can easily be read by VMD, ...
    ~/.local/bin/pycodestyle top_to_lammps.py
    """


class FILEERROR:
    """
    there is problem in the header of the INFILE,
    maybe long header!\n
    """


class HEADER:
    """
    read haeder data of the data file
    check the number of the lines, atom, bond ... informations
    get the box , pairs, ... coefficents
    """

    def __init__(self) -> None:
        self.atomsLine = 0
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
        # An integer to prevent overreading in case of header bugs
        MAXHEADER = 1000
        # track the number of lines in the hedaer
        linecount = 0
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

    def read_header(self):
        """read header to get all the available info
        Read header now get data
        """
        # Setting dictionaries to save data of each block in the header
        self.Masses, self.PairCoeff, self.BondCoeff, self.AngleCoeff,\
            self.DihedralCoeff, self.Names =\
            dict(), dict(), dict(), dict(), dict(), dict()
        # Setting flags to save data correctly
        Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
            = False, False, False, False, False, False
        # Track the number of lines
        linecount = 0
        with open(INFILE, 'r') as f:
            while True:
                linecount += 1
                if linecount > self.atomsLine:
                    break
                line = f.readline()
                # self.process_type_box(line)
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
                elif line.strip().startswith("Masses"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
                         = True, False, False, False, False, False
                elif line.strip().startswith("Pair"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
                        = False, True, False, False, False, False
                elif line.strip().startswith("Bond Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
                        = False, False, True, False, False, False
                elif line.strip().startswith("Angle Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
                        = False, False, False, True, False, False
                elif line.strip().startswith("Dihedral Coeffs"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
                        = False, False, False, False, True, False
                elif line.strip().startswith("Atoms"):
                    Masses, PairCoeff, BondCoeff, AngleCoeff, DihedralCoeff, Atoms\
                        = False, False, False, False, False, True
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

    def get_axis_lim(self, lim) -> list:
        lim = lim.split(' ')
        lim = [float(item) for item in lim if item]
        return lim

    def get_masses(self, line, check) -> dict:
        if check not in line:
            typ = int(line.split(' ')[0])
            mass = float(line.split(' ')[1])
            atom_name = line.split('#')[1].strip()
            self.Masses[typ] = mass
            self.Names[typ] = atom_name
        else:
            pass

    def get_pair_coeff(self, line, check) -> dict:
        if check not in line:
            line = line.split(' ')
            typ = line[0]
            self.PairCoeff[typ] = dict(
                                        style=line[1],
                                        coeff=line[2:]
                                       )
        else:
            pass

    def get_bond_coeff(self, line, check) -> dict:
        if check not in line:
            line = line.split(' ')
            typ = line[0]
            self.BondCoeff[typ] = dict(
                                        style=line[1],
                                        coeff=line[2:]
                                       )
        else:
            pass

    def get_angle_coeff(self, line, check) -> dict:
        if check not in line:
            line = line.split(' ')
            typ = line[0]
            self.AngleCoeff[typ] = dict(
                                        style=line[1],
                                        coeff=line[2:]
                                       )
        else:
            pass

    def get_dihedral_coeff(self, line, check) -> dict:
        if check not in line:
            line = line.split(' ')
            typ = line[0]
            self.DihedralCoeff[typ] = dict(
                                            style=line[1],
                                            coeff=line[2:]
                                           )
        else:
            pass


class BODY:
    """
    read the data for atoms,velocities, bonds, angles, dihedrals
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
            self.Atoms_df = self.Atoms_df.astype(
                            {'atom_id': 'int', 'mol': 'int', 'typ': 'int'})
            self.Atoms_df = self.Atoms_df.astype(
                            {'nx': 'int', 'ny': 'int', 'nz': 'int'})
            self.Bonds_df = pd.DataFrame.from_dict(self.Bonds).T
            self.Bonds_df = self.Bonds_df.astype({'ai': 'int', 'aj': 'int'})

    def get_atoms(self, line) -> dict:
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
                i_nx = str(line[7])
                i_ny = str(line[8])
                i_nz = str(line[9])
            except:
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
        else:
            pass

    def get_velocities(self, line) -> dict:
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
        else:
            pass

    def get_bonds(self, line) -> dict:
        if 'Bonds' not in line:
            line = line.split()
            line = [int(item) for item in line if item]
            bond_id = line[0]
            i_typ = line[1]
            i_ai = line[2]
            i_aj = line[3]
            self.Bonds[bond_id] = dict(
                                        typ=i_typ,
                                        ai=i_ai,
                                        aj=i_aj
                                       )
        else:
            pass

    def get_angles(self, line) -> dict:
        if "Angles" not in line:
            line = line.split()
            line = [int(item) for item in line if item]
            angle_id = line[0]
            i_typ = line[1]
            i_ai = line[2]
            i_aj = line[3]
            i_ak = line[4]
            self.Angles[angle_id] = dict(
                                         typ=i_typ,
                                         ai=i_ai,
                                         aj=i_aj,
                                         ak=i_ak
                                        )

    def get_dihedrals(self, line) -> dict:
        if "Dihedrals" not in line:
            line = line.split()
            line = [int(item) for item in line if item]
            dihedrals_id = line[0]
            i_typ = line[1]
            i_ai = line[2]
            i_aj = line[3]
            i_ak = line[4]
            i_ah = line[5]
            self.Dihedrals[dihedrals_id] = dict(
                                                 typ=i_typ,
                                                 ai=i_ai,
                                                 aj=i_aj,
                                                 ak=i_ak,
                                                 ah=i_ah
                                                )


INFILE = sys.argv[1]
header = HEADER()
body = BODY(header.Names)
body.read_body()
