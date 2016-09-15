from project import Paths
from threading import Thread
from time import sleep
import json
import requests


def get_ids_from_wiki_database():
    with open(Paths.FN_WIKI_DATABASE_RAW) as file:
        database = json.loads(file.read())
        for mol_name, mol in database.items():
            if 'PubChem' in mol.keys():
                pubchem_data = mol['PubChem']
                for pubchem_id in pubchem_data.split('\n'):
                    pubchem_id = pubchem_id.split(' ', 1)[0]
                    if pubchem_id.isnumeric():
                        yield mol_name, pubchem_id


def get_pubchem_data(pubchem_id):
    url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/' + pubchem_id + '/JSON'
    json_request = requests.get(url)
    json_string = json_request.content.decode('utf-8')
    with open(Paths.DIR_PUBCHEM_JSON_RAW + pubchem_id + '.json', 'w') as json_file:
        json_file.write(json_string)
    json_data_raw = json.loads(json_string)

    data = dict()
    descriptions = dict()
    record = json_data_raw['Record']
    main_section = record['Section']

    def extract_values(section):
        for item in section:
            if 'Section' in item:
                extract_values(item['Section'])
            elif 'Information' in item:
                heading, information = item['TOCHeading'], item['Information']
                try:
                    description = item['Description']
                except KeyError:
                    description = None
                data[heading] = information
                descriptions[heading] = description

    extract_values(main_section)

    return data, descriptions


def collect_pubchem_data(nr_of_threads=40, verbose=True):
    database = dict()
    descriptions = dict()
    pubchem_ids = dict()

    def request_thread():
        while len(pubchem_ids) > 0:
            pubchem_id, mol_name = pubchem_ids.popitem()

            try:
                data, new_descriptions = get_pubchem_data(pubchem_id)
            except (KeyError, UnicodeDecodeError):
                print(mol_name + ' NOT PARSED!!')
                continue

            if verbose:
                print(mol_name, 'received from pubchem.')

            if mol_name not in database:
                database[mol_name] = dict()
            database[mol_name][pubchem_id] = data

            for description in new_descriptions:
                if description not in descriptions:
                    descriptions[description] = new_descriptions[description]

    def save_thread():
        while True:
            sleep(60)
            with open(Paths.FN_PUBCHEM_DATABASE_RAW, 'w') as json_file:
                json_file.write(json.dumps(database, separators=(',', ':'), sort_keys=True, indent=4))
            if len(pubchem_ids) == 0:
                break

    # collect the PubChem ids:
    for name, pubchem_id in get_ids_from_wiki_database():
        pubchem_ids[pubchem_id] = name

    # start the collector threads:
    t_data = Thread(target=save_thread)
    t_data.start()
    t_parsers = list()
    for _ in range(nr_of_threads):
        t_parser = Thread(target=request_thread)
        t_parser.start()
        t_parsers.append(t_parser)

    t_data.join()
    for t in t_parsers:
        t.join()
