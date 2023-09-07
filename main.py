# SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# PYTHON
import re
import os
import time
import logging

# DATABASE
from utils import setup_database, DatabaseConnection
from pokemon import Pokemon, PokemonDAO

# GLOBAL VARIABLES
CHROME_DRIVER_PATH = './chrome/chromedriver.exe'
WEB_URL = 'http://silph.co/'
FOLDER_PATH = 'pokedex'
DATABASE_PATH = 'pokedex.db'
SLEEP_TIME = 0
LIMIT_TRIES = 1000

# logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PokemonSaver:
    def __init__(self, dao, web_driver, folder_path):
        self.dao = dao
        self.web_driver = web_driver
        self.folder_path = folder_path

    def fetch_html(self, url):
        self.web_driver.get(url)
        return self.web_driver.page_source

    def save_pokemon(self, counter):
        html = self.fetch_html(WEB_URL)
        matches = re.findall(r'<title>pokemon(/alt)?/(.*?).html</title>', html)

        if not matches:
            logging.error("Pokemon not found in HTML content.")
            return counter

        pokemon_name = matches[0][1]
        existing_pokemon = self.dao.get_pokemon_by_name(name=pokemon_name)

        try:
            if existing_pokemon:
                self.handle_existing_pokemon(existing_pokemon, html)
                counter += 1
            else:
                self.handle_new_pokemon(pokemon_name, html)
                counter += 1

        except Exception as e:
            logging.error(f"Error: {e}")

        return counter

    def handle_existing_pokemon(self, pokemon, html):
        logging.info(f"The Pokemon {pokemon.name} already exists.")
        if self.dao.variant_already_exists(pokemon.id, html):
            logging.info(f"the variant for {pokemon.name} already exists.")
        else:
            logging.info(f"Saving new variant for {pokemon.name}.")
            self.save_variants_html(pokemon, html)

    def handle_new_pokemon(self, pokemon_name, html):
        pokemon = Pokemon(name=pokemon_name, generation=1)
        logging.info(f"Saving new Pokemon {pokemon_name}.")
        self.save_pokemon_html(pokemon, html)

    def save_pokemon_html(self, pokemon, html):
        pokemon_id = self.dao.save_pokemon(pokemon)
        filename = determine_filename(pokemon, is_variant=False)
        self.dao.save_variant(pokemon_id, filename, html)
        save_to_file(filename, html)

    def save_variants_html(self, pokemon, html):
        filename = determine_filename(pokemon)
        self.dao.save_variant(pokemon.id, filename, html)
        save_to_file(filename, html)


def determine_filename(pokemon, is_variant=True):
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)

    pokemon_folder_path = os.path.join(FOLDER_PATH, pokemon.name)
    if not os.path.exists(pokemon_folder_path):
        os.makedirs(pokemon_folder_path)

    if is_variant:
        variant_num = 1
        while os.path.exists(os.path.join(pokemon_folder_path, f'{pokemon.name}_variant_{variant_num}.html')):
            variant_num += 1
        return os.path.join(pokemon_folder_path, f'{pokemon.name}_variant_{variant_num}.html')
    else:
        return os.path.join(pokemon_folder_path, f'{pokemon.name}.html')


def save_to_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


if __name__ == '__main__':
    setup_database()
    counter = 0

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = Service(CHROME_DRIVER_PATH)
    web_driver = webdriver.Chrome(service=service, options=options)

    with DatabaseConnection(DATABASE_PATH) as conn:
        dao = PokemonDAO(conn)
        pokemon_saver = PokemonSaver(dao, web_driver, FOLDER_PATH)

        while counter < LIMIT_TRIES:
            counter = pokemon_saver.save_pokemon(counter)
            logging.info(f"counter: {counter}")
            time.sleep(SLEEP_TIME)
