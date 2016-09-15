from project.DataCollecting import HTMLParser
from project import Paths
from threading import Thread
from time import sleep
import json
import os
import requests


def extract_wiki_links(wikipedia_url):
    wiki_domain = wikipedia_url.split('.org')[0] + '.org'
    page = WikipediaPage(url=wikipedia_url)
    for link in page.get_links():
        if link[:5] == '/wiki':
            link = link.split('#', 1)[0]
            yield wiki_domain+link


def collect_pages():
    wikicollector = WikipediaCollector()
    wikicollector.run()


def parse_all_pages(verbose=True):
    database = dict()
    for html_file in os.listdir(Paths.DIR_WIKI_PAGES):
        if verbose:
            print(html_file + ' is being parsed.')
        wiki_page = WikipediaPage(filename=Paths.DIR_WIKI_PAGES + html_file)
        data_table = wiki_page.get_molecule_table()
        molecule_name = html_file.rsplit('.html', 1)[0]
        molecule_data = dict()
        for attr, value in _parse_info_table(data_table):
            molecule_data[attr] = value
        database[molecule_name] = molecule_data
    with open(Paths.FN_WIKI_DATABASE_RAW, 'w') as json_file:
        json_file.write(json.dumps(database, separators=(',', ':'), sort_keys=True, indent=4))


def _parse_info_table(info_table):
    for row in info_table:
        key = None
        value = None
        row.remove('sup')
        if len(row) == 2:
            key = str(row[0])
            try:
                list_element = row[1].get_elements('ul')
            except AttributeError:
                continue
            if list_element:
                value = list()
                for item in list_element[0]:
                    value.append(str(item))
            else:
                value = str(row[1])
        elif len(row) == 1:
            list_element = row.get_elements('ul')
            if list_element:
                value = list()
                for item in list_element[0]:
                    value.append(str(item))
                key = str(row).replace(str(list_element[0]), '')
        if key and value:
            yield key, value


class WikipediaPage(HTMLParser.HTMLPage):
    """
    Inherits functions from HTMLPage and adds function to get info table from a wikipedia molecule page.
    """
    def get_molecule_table(self):
        for table in self.get_elements('table'):
            is_info_table = True
            for tag_name in ['Identifiers', 'Properties']:
                if tag_name not in str(table):
                    is_info_table = False
            if is_info_table:
                return table


class WikipediaCollector:
    def __init__(self, verbose=True):
        self.terminate = False
        self.verbose = verbose

        self.urls_done = set()
        self.urls_to_do = set()
        self.downloaded_pages = set()

        self._load_state()

    def _load_state(self):
        with open(Paths.FN_WIKI_URLS_TO_DO) as file:
            for line in file:
                self.urls_to_do.add(line.strip())
        with open(Paths.FN_WIKI_URLS_DONE) as file:
            for line in file:
                self.urls_done.add(line.strip())
        for filename in os.listdir(Paths.DIR_WIKI_PAGES):
            self.downloaded_pages.add(filename.rsplit('.', 1)[0])
        if self.verbose:
            print('length of wait-list: ' + str(len(self.urls_to_do)))
            print('length of tested urls: ' + str(len(self.urls_done)))

    def _save_state(self):
        with open(Paths.FN_WIKI_URLS_TO_DO, 'w') as file:
            file_string = ''
            for url in self.urls_to_do.copy():
                file_string += url + '\n'
            file.write(file_string)
        with open(Paths.FN_WIKI_URLS_DONE, 'w') as file:
            file_string = ''
            for url in self.urls_done.copy():
                file_string += url + '\n'
            file.write(file_string)
        if self.verbose:
            print('length of waitlist: ' + str(len(self.urls_to_do)))
            print('length of tested urls: ' + str(len(self.urls_done)))

    def _page_collector_thread(self):
        while not self.terminate:
            current_url = self.urls_to_do.pop()
            if current_url in self.urls_done:
                continue
            self.urls_done.add(current_url)

            molecule_name = current_url.rsplit('/', 1)[-1]
            try:
                if molecule_name in self.downloaded_pages:
                    with open(Paths.DIR_WIKI_PAGES + molecule_name + '.html') as file:
                        page_string = file.read()
                else:
                    try:
                        page_string = requests.get(current_url).content.decode('utf-8')
                    except requests.exceptions.ConnectionError as e:
                        print(e)
                        self.urls_done.remove(current_url)
                        self.urls_to_do.add(current_url)
                        continue
                page = WikipediaPage(html_string=page_string)
            except ValueError:
                continue

            info_table = page.get_molecule_table()
            if info_table:
                if not os.path.exists(Paths.DIR_WIKI_PAGES + molecule_name + '.html'):
                    with open(Paths.DIR_WIKI_PAGES + molecule_name + '.html', 'w') as file:
                        file.write(page_string)
                wiki_domain = current_url.split('.org', 1)[0] + '.org'
                for link in page.get_links():
                    if link[:5] == '/wiki':
                        if wiki_domain + link not in self.urls_done:
                            self.urls_to_do.add(wiki_domain+link)
                if self.verbose:
                    print(current_url.split('/')[-1] + ' downloaded.')

    def _save_state_thread(self):
        while not self.terminate:
            sleep(5)
            self._save_state()

    def _input_thread(self):
        while not self.terminate:
            inp = input('Enter command: ')
            if inp.lower() in ['quit', 'q']:
                self.terminate = True

    def run(self, nr_of_threads=40):
        t_data = Thread(target=self._save_state_thread)
        t_data.start()
        t_input = Thread(target=self._input_thread)
        t_input.start()
        t_parsers = list()
        for _ in range(nr_of_threads):
            t_parser = Thread(target=self._page_collector_thread)
            t_parser.start()
            t_parsers.append(t_parser)

        t_data.join()
        t_input.join()
        for t in t_parsers:
            t.join()
