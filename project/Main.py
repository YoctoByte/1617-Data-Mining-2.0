from project.DataCollecting import DataCollecting, Wikipedia
from project import Paths
import json
import os
import shutil


def create_files_and_dirs():
    for directory in [Paths.ALL_DIRS]:
        if not os.path.exists(directory):
            os.mkdir(directory)
    for filename in [Paths.ALL_FILES]:
        if not os.path.exists(filename):
            open(filename, 'w')


def collect_wikipedia_links():
    initial_urls = set()
    for wikipedia_url in ['https://en.wikipedia.org/wiki/Dictionary_of_chemical_formulas',
                          'https://en.wikipedia.org/wiki/Inorganic_compounds_by_element',
                          'https://en.wikipedia.org/wiki/List_of_alchemical_substances',
                          'https://en.wikipedia.org/wiki/List_of_biomolecules',
                          'https://en.wikipedia.org/wiki/List_of_chemical_compounds_with_unusual_names',
                          'https://en.wikipedia.org/wiki/List_of_inorganic_compounds',
                          'https://en.wikipedia.org/wiki/List_of_interstellar_and_circumstellar_molecules',
                          'https://en.wikipedia.org/wiki/List_of_named_inorganic_compounds']:
        for url in Wikipedia.extract_wiki_links(wikipedia_url):
            initial_urls.add(url)
    with open(Paths.FN_WIKI_URLS_INITIAL, 'w') as file:
        for url in initial_urls:
            file.write(url + '\n')


if __name__ == '__main__':
    def do_nothing():
        print('Starting data mining project.')
        # Create all necessary files and directories:
        create_files_and_dirs()
        print('Files and directories created.')

        # Collect wikipedia URLs for initializing the data collecting process.
        print('Starting Wikipedia url collecting.')
        collect_wikipedia_links()
        print('Finished Wikipedia url collecting.')

        # After the initial urls are collected they are transferred to "data/wikipedia/waitlist_urls.csv":
        shutil.copyfile(Paths.FN_WIKI_URLS_INITIAL, Paths.FN_WIKI_URLS_TO_DO)
        print('Copied collected urls to "' + Paths.FN_WIKI_URLS_TO_DO + '".')

        # Start the wikipedia data collecting process.
        print('Starting Wikipedia page collecting process.')
        Wikipedia.collect_pages()
        print('Finished Wikipedia page collecting process.')

        # Collect PubChem urls from wikipedia HTML database. Urls are stored in "data/pubchem/urls.csv":
        # DataCollecting.collect_pubchem_urls()


    def plz_dont():
        pubchem_id_data = DataCollecting.get_pubchem_ids_from_file()
        pubchem_ids = list()
        for ids in pubchem_id_data.values():
            pubchem_ids.extend(ids)
        DataCollecting.collect_pubchem_data(pubchem_ids)

        with open(Paths.FN_WIKI_DATABASE_RAW) as file:
            database = json.loads(file.read())
            for mol in database.values():
                if 'PubChem' in mol.keys():
                    print(mol['PubChem'])
