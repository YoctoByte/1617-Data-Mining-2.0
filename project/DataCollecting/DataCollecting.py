from project.DataCollecting import PubChemAPI, Wikipedia
from threading import Thread
import os


def get_pubchem_ids_from_file():
    with open(FN_PUBCHEM_URLS) as file:
        data = dict()
        for line in file:
            urls = line.strip().split(',')
            molecule = urls.pop(0)
            data[molecule] = list()
            for url in urls:
                pubchem_id = url.rsplit('/', 1)[-1]
                if pubchem_id.isnumeric():
                    data[molecule].append(pubchem_id)
        return data


def collect_pubchem_data(pubchem_id_list):
    def collecting_thread():
        while True:
            try:
                pubchem_id = pubchem_id_list.pop()
            except IndexError:
                break

            try:
                pubchem_data_obj = PubChemAPI.PubChemPage(pubchem_id)
                print(pubchem_data_obj.iupac_name())
                pubchem_data_obj.save()
            except (KeyError, UnicodeDecodeError):
                print(pubchem_id + ' DATA NOT COLLECTED!')

    collectors = list()
    for _ in range(10):
        thread = Thread(target=collecting_thread)
        thread.start()
        collectors.append(thread)

    for t in collectors:
        t.join()


if __name__ == '__main__':
    # wikiparser = WikipediaParser()
    # wikiparser.run()
    # get_urls_from_tables('pubchem')
    # get_pubchem_urls()
    # download_page('https://pubchem.ncbi.nlm.nih.gov/compound/294764')
    pass
