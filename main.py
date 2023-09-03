# SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# PYTHON
import re
import os
import time
import difflib

# DATABASE
from utils import setup_database, DatabaseConnection
from pokemon import Pokemon, PokemonDAO

# GLOBAL VARIABLES
CHROME_DRIVER_PATH = './chrome/chromedriver.exe'
WEB_URL = 'http://silph.co/'
FOLDER_PATH = 'pokedex'
DATABASE_PATH = 'pokedex.db'


def save_pokemon(counter):
    # Selenium configurations
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
            variant = dao.get_by_name(name=matches[0][1]) is not None
            print(f'variant: {variant}')
            pokemon = Pokemon(
                name=matches[0][1],
                generation=1,
                html=html,
                variant=variant
            )
            print(f'es variante: {pokemon.variant}')

            # Check if pokemon is downloaded
            if dao.pokemon_and_variant_exists_in_database(pokemon):
                print(f"El archivo {pokemon.name}.html ya existe.")
                counter += 1
            else:
                dao.save(pokemon)
                save_in_pokedex(pokemon, pokemon.variant)
                print(f"El archivo se ha guardado como:{pokemon.name}.html.")

        else:
            print("No se encontró el nombre del Pokémon en el contenido HTML.")
            print(f"Nombre: {html} ")

    driver.quit()
    return counter


def save_in_pokedex(pokemon: Pokemon, is_variant=False):
    # Create the pokedex directory if it doesn't exist
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)

    # Create a specific directory for each Pokémon
    pokemon_folder_path = os.path.join(FOLDER_PATH, pokemon.name)
    if not os.path.exists(pokemon_folder_path):
        os.makedirs(pokemon_folder_path)

    # Determine the filename
    # If it's a variant, then find the next available variant number
    if is_variant:
        variant_num = 1
        while os.path.exists(os.path.join(pokemon_folder_path, f'{pokemon.name}_variant_{variant_num}.html')):
            variant_num += 1
        filename = os.path.join(pokemon_folder_path, f'{pokemon.name}_variant_{variant_num}.html')
    else:
        filename = os.path.join(pokemon_folder_path, f'{pokemon.name}.html')
        # Save the HTML content to the determined filename

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(pokemon.html)


if __name__ == '__main__':
    setup_database()
    counter = 0
    while True:
        # break if 100 pokemon are downloaded
        if counter == 200:
            break

        limit_counter = save_pokemon(counter)
        time.sleep(0)
