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

# logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def save_pokemon_html(pokemon, dao, html,):
    pokemon_id = dao.save_pokemon(pokemon)
    filename = determine_filename(pokemon)
    dao.save_variant(pokemon_id, filename, html)
    save_to_file(filename, html)


def save_variants_html(pokemon, dao, html,):
    filename = determine_filename(pokemon)
    dao.save_variant(pokemon.id, filename, html)
    save_to_file(filename, html)


def save_pokemon(counter):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(WEB_URL)
    html = driver.page_source

    pattern = r'<title>pokemon(/alt)?/(.*?).html</title>'
    matches = re.findall(pattern, html)

    with DatabaseConnection(DATABASE_PATH) as conn:
        dao = PokemonDAO(conn)

        if matches:
            pokemon_name = matches[0][1]
            existing_pokemon = dao.get_pokemon_by_name(name=pokemon_name)

            try:
                if existing_pokemon:
                    logging.info(f"El Pokémon {pokemon_name} ya existe.")
                    if dao.variant_already_exists(existing_pokemon.id, html):
                        logging.info(f"El Pokémon {pokemon_name} ya existe.")
                    else:
                        logging.info(f"Guardando nueva variante para {pokemon_name}.")
                        save_variants_html(existing_pokemon, dao, html)
                else:

                    pokemon = Pokemon(
                        name=matches[0][1],
                        generation=1,
                    )

                    logging.info(f"Guardando nuevo Pokémon {pokemon_name}.")
                    save_pokemon_html(pokemon, dao, html)
                    logging.info(f"El archivo se ha guardado como: {pokemon.name}.html")

            except Exception as e:
                logging.error(f"Error: {e}")
                logging.error(f"Pokemon: {pokemon}")

        else:
            logging.error("No se encontró el nombre del Pokémon en el contenido HTML.")

    driver.quit()
    return counter


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
    while True:
        if counter == 200:
            break
        counter = save_pokemon(counter)
        logging.info(f"counter: {counter}")
        time.sleep(0)
