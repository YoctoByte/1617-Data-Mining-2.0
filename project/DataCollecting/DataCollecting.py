from project import Paths
import json


def initialize_database(verbose=True):
    final_database = dict()

    # First add the PubChem molecules to the database:
    with open(Paths.FN_PUBCHEM_DATABASE_RAW) as json_file:
        pubchem_database = json.loads(json_file.read())
        if verbose:
            print('Loaded PubChem database to RAM.')

    for molecule in pubchem_database.values():
        for pubchem_page in molecule.values():
            if 'Canonical SMILES' in pubchem_page:
                canonical_smiles = pubchem_page['Canonical SMILES'][0]['StringValue']
                if canonical_smiles not in final_database:
                    final_database[canonical_smiles] = dict()
                if 'Isomeric SMILES' in pubchem_page:
                    isomeric_smiles = pubchem_page['Isomeric SMILES'][0]['StringValue']
                    final_database[canonical_smiles][isomeric_smiles] = dict()
                    final_database[canonical_smiles][isomeric_smiles]['__source__'] = 'PubChem'
                else:
                    final_database[canonical_smiles][canonical_smiles] = dict()
                    final_database[canonical_smiles][canonical_smiles]['__source__'] = 'PubChem'
    if verbose:
        print('Finished processing PubChem data.')

    # Then add the Wikipedia molecules to the database:
    with open(Paths.FN_WIKI_DATABASE_RAW) as json_file:
        wikipedia_database = json.loads(json_file.read())
        if verbose:
            print('Loaded Wikipedia database to RAM.')

    for molecule in wikipedia_database.values():
        if 'SMILES' in molecule:
            smiles = molecule['SMILES'][0]
            if smiles not in final_database:
                final_database[smiles] = dict()
            if smiles not in final_database[smiles]:
                final_database[smiles][smiles] = dict()
            if '__source__' in final_database[smiles][smiles]:
                final_database[smiles][smiles]['__source__'] += ', Wikipedia'
            else:
                final_database[smiles][smiles]['__source__'] = 'Wikipedia'
    if verbose:
        print('Finished processing Wikipedia data.')

    # And finally store the database in a file:
    with open(Paths.FN_DATABASE_JSON, 'w') as json_file:
        json_file.write(json.dumps(final_database, separators=(',', ':'), indent=4))
