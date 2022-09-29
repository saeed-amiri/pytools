import pandas as pd
import sys
import numpy as np
import read_lmp_data as mlmp
import typing


class Doc:
    """set charges for each type in the output file of MOLTEMPLAE
    it writes the charges in a seperat file, name:
    system.in.charges
    e.g., 
        set type 1 charge -0.18
        set type 2 charge -0.12
        set type 3 charge 0.06
    """



class WriteLmp:
    """Write the data in a full atoms style for LAMMPS
    Input:
        atoms_df (DataFrame from PDBFILE: Pdb class)
        bonds_df, angles_df, dihedrals, impropers_df (DataFrame from
        PSFFILE Psf class)
    Output:
        A LAMMPS data file
    """

    def __init__(self, lmp: mlmp.Body, header: mlmp.Header) -> None:
        self.atoms = lmp.Atoms_df
        self.bonds = lmp.Bonds_df
        self.angles = lmp.Angles_df
        self.dihedrals = lmp.Dihedrals_df
        self.Natoms = header.NAtoms
        self.Natoms_type = header.NAtomTyp
        self.Nbonds = header.NBonds
        self.Nbonds_type = header.NBondTyp
        self.Nangles = header.NAngles
        self.Nangles_type = header.NAngleTyp
        self.NDihedrals = header.NDihedrals
        self.NDihedrals_type = header.NDihedralTyp
        self.Masses = header.Masses
        self.Names = header.Names
        print(f"Writting '{LMPFILE}' ...")

    def mk_lmp(self) -> None:
        """calling function to write data into a file"""
        # find box sizes
        self.set_box()
        # get number of atoms, types, bonds
        # self.set_numbers()
        # write file
        self.write_data()
        # print(self.atoms['charge'].sum())

    def set_box(self) -> None:
        """find Max and min of the data"""
        self.xlim = (self.atoms.x.min(), self.atoms.x.max())
        self.ylim = (self.atoms.y.min(), self.atoms.y.max())
        self.zlim = (self.atoms.z.min(), self.atoms.z.max())

    def set_numbers(self) -> None:
        """set the numbers of atoms, type, bonds"""
        self.Natoms = len(self.atoms)
        self.Nbonds = len(self.bonds)
        self.Natoms_type = np.max(self.atoms.typ)
        self.Nbonds_type = np.max(self.bonds.typ)

    def set_totals(self) -> None:
        """set the total numbers of charges, ..."""
        self.Tcharge = self.atoms['charge'].sum()

    def write_data(self) -> None:
        """write LAMMPS data file"""
        with open(LMPFILE, 'w') as f:
            f.write(f"Data file from VDM for silica slab\n")
            f.write(f"\n")
            self.write_numbers(f)
            self.write_box(f)
            self.write_masses(f)
            self.write_atoms(f)
            self.write_bonds(f)
            self.write_angles(f)
            self.write_dihedrals(f)

    def write_numbers(self, f: typing.TextIO) -> None:
        f.write(f"{self.Natoms} atoms\n")
        f.write(f"{self.Natoms_type} atom types\n")
        f.write(f"{self.Nbonds} bonds\n")
        f.write(f"{self.Nbonds_type} bond types\n")
        f.write(f"{self.Nangles} angles\n")
        f.write(f"{self.Nangles_type} angle types\n")
        f.write(f"{self.NDihedrals} dihedrals\n")
        f.write(f"{self.NDihedrals_type} dihedral types\n")
        f.write(f"\n")

    def write_box(self, f: typing.TextIO) -> None:
        f.write(f"{self.xlim[0]:.3f} {self.xlim[1]:.3f} xlo xhi\n")
        f.write(f"{self.ylim[0]:.3f} {self.ylim[1]:.3f} ylo yhi\n")
        f.write(f"{self.zlim[0]:.3f} {self.zlim[1]:.3f} zlo zhi\n")
        f.write(f"\n")

    def write_masses(self, f: typing.TextIO) -> None:
        f.write(f"Masses\n")
        f.write(f"\n")
        for typ, mass in self.Masses.items():
            f.write(f"{int(typ): 3} {mass:.5f} "
                    f"# {self.Names[typ]}\n")
        f.write(f"\n")

    def write_atoms(self, f: typing.TextIO) -> None:
        """Write atoms section inot file"""
        f.write(f"Atoms # full\n")
        f.write(f"\n")
        columns = ['mol', 'typ', 'charge', 'x', 'y', 'z', 'nx', 'ny', 'nz',
                   'cmt', 'name']
        self.atoms.to_csv(f, sep=' ', index=True, columns=columns,
                          header=None)
        f.write(f"\n")
        f.write(f"\n")

    def write_bonds(self, f: typing.TextIO) -> None:
        f.write(f"Bonds\n")
        f.write(f"\n")
        columns = ['typ', 'ai', 'aj']
        self.bonds.to_csv(f, sep=' ', index=True, columns=columns,
                          header=None)
        f.write(f"\n")

    def write_angles(self, f: typing.TextIO) -> None:
        f.write(f"Angles\n")
        f.write(f"\n")
        columns = ['typ', 'ai', 'aj', 'ak']
        self.angles.to_csv(f, sep=' ', index=True, columns=columns,
                          header=None)
        f.write(f"\n")

    def write_dihedrals(self, f: typing.TextIO) -> None:
        f.write(f"Dihedrals\n")
        f.write(f"\n")
        columns = ['typ', 'ai', 'aj', 'ak', 'ah']
        self.dihedrals.to_csv(f, sep=' ', index=True, columns=columns,
                          header=None)
        f.write(f"\n")



infile = sys.argv[1]
header = mlmp.Header(infile)
body = mlmp.Body(header.Names, infile)
body.read_body()
print(header.NDihedralTyp)

body.Atoms_df.loc[body.Atoms_df.typ == 1, 'charge'] = -0.18
body.Atoms_df.loc[body.Atoms_df.typ == 2, 'charge'] = -0.12
body.Atoms_df.loc[body.Atoms_df.typ == 3, 'charge'] = 0.06
print(body.Atoms_df)
LMPFILE = 'decane.data'
lmp = WriteLmp(body, header)
lmp.mk_lmp()