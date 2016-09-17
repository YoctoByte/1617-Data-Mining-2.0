import json


def _load_data():
    with open('../project/PyChem/elements.json') as elements_data_file:
        raw_data = json.loads(elements_data_file.read())

    data = dict()
    for i, entry in enumerate(raw_data):
        entry['atomic number'] = i+1
        data[entry['element']] = entry
        data[entry['element'].lower()] = entry
        data[entry['element name']] = entry
        data[entry['element name'].lower()] = entry
        data[entry['atomic number']] = entry
    return data


ELEMENTS_DATA = _load_data()


class Atom:
    def __init__(self, element, isotope=None, charge=None, aromatic=None):
        try:
            element_data = ELEMENTS_DATA[element]
        except IndexError:
            raise ValueError('"' + element + '" is not a valid element.')

        self.isotope = isotope
        self.charge = charge
        self.aromatic = aromatic

        self.symbol = element_data['element']
        self.element = element_data['element name']
        self.atomic_number = element_data['atomic number']
        self.atomic_weight = element_data['atomic weight']
        self.group = element_data['group']
        self.period = element_data['period']
        self.electronegativity = element_data['electronegativity']

        self.adjacent_atoms = set()
        self.bonds = dict()


class Molecule:
    def __init__(self, smiles=None):
        self.atoms = set()
        self.mass = 0

        if smiles:
            _parse_from_smiles(self, smiles)
            self._fill_hydrogen()

    def add_atom(self, atom):
        if atom not in self.atoms:
            self.atoms.add(atom)
            self.mass += atom.atomic_weight

    def add_bond(self, atoms, bond_type='-'):
        for atom1 in atoms:
            self.atoms.add(atom1)
            for atom2 in atoms:
                if atom1 != atom2:
                    atom1.adjacent_atoms.add(atom2)
                    atom1.bonds[atom2] = bond_type

    def bond_table(self):
        bond_table = list()
        for atom in self.atoms:
            for other_atom in atom.bonds:
                bond_type = atom.bonds[other_atom]
                entry = (atom, other_atom, bond_type)
                other_entry = (other_atom, atom, bond_type)
                if other_entry not in bond_table:
                    bond_table.append(entry)
        return bond_table

    def _fill_hydrogen(self):
        bond_electrons = {'-': 1, '=': 2, '#': 3, '$': 4, ':': 1}

        for atom in self.atoms.copy():
            try:
                hydrogen_to_add = atom.hydrogen_count
            except AttributeError:
                hydrogen_to_add = 0
                if atom.symbol in ['B', 'C', 'N', 'O', 'P', 'S', 'F', 'Cl', 'Br', 'I']:
                    bonded_electrons = 0
                    for bond in atom.bonds.values():
                        bonded_electrons += bond_electrons[bond]
                    if atom.aromatic:
                        bonded_electrons += 1
                    hydrogen_to_add = 18 - (atom.group + bonded_electrons)
                    if atom.charge:
                        hydrogen_to_add += atom.charge

            for _ in range(hydrogen_to_add):
                hydrogen = Atom('H')
                self.add_atom(hydrogen)
                self.add_bond(atoms={atom, hydrogen})


def _parse_from_smiles(molecule, smiles_string, _active_atom=None, _labels=None):
    active_atom = _active_atom
    if _labels is None:
        labels = dict()
    else:
        labels = _labels

    bond_type = '-'
    for token in _tokenize_smiles(smiles_string):
        if token[0] == '(':
            _parse_from_smiles(molecule, token[1:-1], _active_atom=active_atom, _labels=labels)
        elif token[0] == '[':
            isotope, element, h_count, charge, chirality = _parse_smiles_parenthesis(token)
            new_atom = Atom(element, isotope=isotope, charge=charge, aromatic=element.islower())
            new_atom.h_count = h_count
            molecule.add_atom(new_atom)
            if active_atom:
                molecule.add_bond(atoms={active_atom, new_atom}, bond_type=bond_type)
            active_atom = new_atom
            bond_type = '-'
        elif token.lower() in ['b', 'c', 'n', 'o', 'p', 's', 'f', 'cl', 'br', 'i']:
            new_atom = Atom(token, aromatic=token.islower())
            molecule.add_atom(new_atom)
            if active_atom:
                molecule.add_bond(atoms={active_atom, new_atom}, bond_type=bond_type)
            active_atom = new_atom
            bond_type = '-'
        elif token[0] == '%':
            label = token[1:]
            if label not in labels:
                labels[label] = active_atom
            else:
                molecule.add_bond(atoms={active_atom, labels[label]}, bond_type=bond_type)
                bond_type = '-'
        elif token in ['-', '=', '#', '$', ':']:
            bond_type = token


def _tokenize_smiles(smiles_string):
    index = 0
    while index < len(smiles_string):
        if smiles_string[index] == '(':
            right_brack = index
            while index < len(smiles_string):
                right_brack = smiles_string.find(')', right_brack) + 1
                if right_brack == 0:
                    raise ValueError
                bracketed_string = smiles_string[index:right_brack]
                if bracketed_string.count('(') == bracketed_string.count(')'):
                    yield bracketed_string
                    index = right_brack
                    break
        elif smiles_string[index] == '[':
            right_brack = smiles_string.find(']', index) + 1
            if right_brack == 0:
                raise ValueError
            yield smiles_string[index:right_brack]
            index = right_brack
        elif smiles_string[index] == '%':
            label_string = '%'
            while index + 1 < len(smiles_string):
                index += 1
                if smiles_string[index] in '0123456789':
                    label_string += smiles_string[index]
                else:
                    break
            yield label_string
        else:
            if smiles_string[index] in '0123456789':
                yield '%' + smiles_string[index]
            else:
                element_string = smiles_string[index]
                if index+1 < len(smiles_string) and smiles_string[index+1].islower():
                    element_string += smiles_string[index+1]
                    index += 1
                yield element_string
            index += 1


def _parse_smiles_parenthesis(token):
    token = token[1:-1]
    token = token.replace(' ', '')

    isotope = None
    element = ''
    h_count = None
    charge = None
    chirality = ''

    index = 0
    # parse the isotope from the token:
    isotope_string = ''
    while index < len(token) and token[index] in '0123456789':
        isotope_string += token[index]
        index += 1
    if isotope_string:
        isotope = int(isotope_string)
    # parse the element from the token:
    while index < len(token) and token[index].isalpha():
        if element and token[index] == 'H':
            break
        element += token[index]
        index += 1
    # parse the hydrogen count from the token:
    if index < len(token) and token[index] == 'H':
        index += 1
        h_count_string = ''
        while index < len(token) and token[index] in '0123456789':
            h_count_string += token[index]
            index += 1
        if h_count_string:
            h_count = int(h_count_string)
    # parse the charge from the token:
    if index < len(token) and token[index] in '-+':
        charge_string = ''
        while index < len(token) and token[index] in '-+0123456789':
            charge_string += token[index]
            index += 1
        try:
            charge = int(charge_string[1:])
            if charge_string[0] == '-':
                charge *= -1
        except ValueError:
            charge = charge_string.count('+') - charge_string.count('-')
    # parse the chirality from the token:
    if index < len(token) and token[index] == '@':
        chirality += '@'
        index += 1
        if index < len(token) and token[index] == '@':
            chirality += '@'
            index += 1
        if index+1 < len(token) and token[index:index+2] in ['TH', 'AL', 'SP', 'TB', 'OH']:
            # TH: Tetrahedral, AL: Allenal, SP: Square Planar, TB: Trigonal Bipyramidal, OH: Octahedral
            chirality += token[index:index+2]

    return isotope, element, h_count, charge, chirality
