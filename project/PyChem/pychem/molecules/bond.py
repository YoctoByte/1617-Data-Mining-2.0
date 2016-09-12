BOND_TYPES = {'-': 'single',
              '=': 'double',
              '#': 'triple',
              '$': 'quadruple',
              ':': 'aromatic'}


class Bond:
    def __init__(self, bond_type='-', atoms=set(), energy=None, length=None, electron_count=None):
        self.bond_type_symbol = bond_type
        try:
            self.bond_type = BOND_TYPES[bond_type]
        except KeyError:
            self.bond_type = None
        self.atoms = set(atoms)
        self.energy = energy
        self.length = length
        self.electron_count = electron_count

    def copy(self):
        bond_copy = Bond()
        for key, item in self.__dict__.items():
            try:
                bond_copy.__dict__[key] = item.copy()
            except AttributeError:
                bond_copy.__dict__[key] = item
        return bond_copy
