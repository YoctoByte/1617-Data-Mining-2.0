from pychem.molecules.parsers import smiles, cas, iupac, formula
from pychem.molecules import gui
from pychem.molecules.atom import Atom
# from pychem.molecules.bond import Bond


# todo: calculate resonance structures
# todo: predict stability of molecule


class Molecule:
    def __init__(self, molecule_data=None, data_type=None):
        """
        :param molecule_data: The molecule data (see examples)
        :param data_type: The molecule data type (see examples)
        """
        self.atoms = set()
        self.bonds = set()
        self.rings = None
        self.parent_chain = None
        self.iupac_name = None
        self.cas_number = None
        self.smiles = None
        self.formula = None
        if molecule_data is not None:
            if data_type:
                if data_type.lower() == 'formula':
                    self.bonds, self.atoms = formula.from_formula(molecule_data)
                    self.formula = molecule_data
                elif data_type.lower() == 'smiles':
                    self.bonds, self.atoms = smiles.parse_from(molecule_data)
                    self.smiles = molecule_data
                elif data_type.lower() == 'cas':
                    self.bonds, self.atoms = cas.parse_from(molecule_data)
                    self.cas_number = molecule_data
                elif data_type.lower() == 'iupac':
                    self.bonds, self.atoms = iupac.parse_from(molecule_data)
                    self.iupac_name = molecule_data
            else:
                # parse
                pass

    def __iter__(self):
        for atom in self.atoms:
            yield atom

    def _reset_data(self):
        self.rings = None
        self.parent_chain = None
        self.iupac_name = None
        self.cas_number = None
        self.smiles = None
        self.formula = None

    def add_atom(self, atom):
        self.atoms.add(atom)
        self._reset_data()

    def add_bond(self, bond):
        self.bonds.add(bond)
        for atom in bond.atoms:
            self.atoms.add(atom)
            for other_atom in bond.atoms:
                if other_atom != atom:
                    atom.surrounding_atoms.add(other_atom)
        self._reset_data()

    def remove_atom(self, atom):
        self.atoms.delete(atom)
        bonds_to_remove = list()
        for bond in self.bonds:
            if atom in bond.atoms:
                bonds_to_remove.append(bond)
        for other_atom in self.atoms:
            if atom in other_atom.surrounding_atoms:
                other_atom.surrounding_atoms.remove(atom)
            for bond in other_atom.bonds.copy():
                if bond in bonds_to_remove:
                    other_atom.bonds.remove(bond)
        self._reset_data()

    def remove_bond(self, bond):
        self.bonds.delete(bond)
        for atom in self.atoms:
            if bond in atom.bonds:
                atom.bonds.remove(bond)
        self._reset_data()

    def shallow_copy(self):
        molecule_copy = Molecule()
        for key, item in self.__dict__.items():
            try:
                molecule_copy.__dict__[key] = item.copy()
            except AttributeError:
                molecule_copy.__dict__[key] = item
        return molecule_copy

    def copy(self):
        molecule_copy = Molecule()
        new_atoms = dict()
        for atom in self.atoms:
            new_atom = atom.copy()
            new_atom.surrounding_atoms = set()
            new_atom.bonds = set()
            new_atoms[atom] = new_atom
            molecule_copy.add_atom(new_atom)
        for bond in self.bonds:
            new_bond = bond.copy()
            for atom in new_bond.atoms.copy():
                new_bond.atoms.remove(atom)
                new_bond.atoms.add(new_atoms[atom])
            molecule_copy.add_bond(new_bond)
        return molecule_copy

    def draw_2d(self):
        canvas = gui.Canvas()
        canvas.draw_molecule(self.bonds, self.atoms)
