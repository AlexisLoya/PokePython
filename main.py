# SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# PYTHON
import re
import os
import time

# DATABASE
import sqlite3
from utils.connection import setup_database

# Ruta al controlador de Chrome
CHROME_DRIVER_PATH = './chrome/chromedriver.exe'
WEB_URL = 'http://silph.co/'
FOLDER_PATH = 'pokedex'
DATABASE_PATH = 'pokedex.db'

def save_pokemon_to_database(pokemon_name, generation):
    print(f"Pokemon Name: {pokemon_name} (Type: {type(pokemon_name)})")
    print(f"Generation: {generation} (Type: {type(generation)})")

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    c.execute("INSERT INTO pokemons (name, generation) VALUES (?, ?)", (pokemon_name, generation))

    pokemon_id = c.lastrowid
    conn.commit()
    conn.close()
    return pokemon_id


def save_variant_to_database(pokemon_id, html):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO variants (pokemon_id, html) VALUES (?, ?)", (pokemon_id, html))
    conn.commit()
    conn.close()


def is_pokemon_downloaded(pokemon_name):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM pokemons WHERE name=?", (pokemon_name,))
    data = c.fetchone()
    conn.close()
    return data is not None


def pokemon_and_variant_exists_in_database(pokemon):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # First, check if the Pokémon exists
    c.execute("SELECT id FROM pokemons WHERE name=?", (pokemon['name'],))
    result = c.fetchone()

    # If the Pokémon doesn't exist at all, return False
    if not result:
        conn.close()
        return False

    # If we're looking for a variant, then check in the variants table
    if pokemon['variant']:
        pokemon_id = result[0]
        c.execute("SELECT id FROM variants WHERE pokemon_id=? AND html=?", (pokemon_id, pokemon['html']))
        variant_result = c.fetchone()

        conn.close()

        # If variant_result is not None, it means the variant exists
        return variant_result is not None

    else:
        conn.close()
        return True  # Because the Pokémon exists and it's not a variant

def save_pokemon(counter):

    # Configuración de Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecutar en modo sin ventana

    # Crear objeto Service para el controlador de Chrome
    service = Service(CHROME_DRIVER_PATH)

    # Crear instancia del controlador de Chrome
    driver = webdriver.Chrome(service=service, options=options)

    # Abrir la página web
    driver.get(WEB_URL)

    # Obtener el contenido HTML completo
    html = driver.page_source

    # Buscar el patrón de la etiqueta <title> que contiene el nombre del archivo (pokemon)
    pattern = r'<title>pokemon(/alt)?/(.*?).html</title>'

    matches = re.findall(pattern, html)
    
    if matches:
        # make pokemon object
        pokemon = {}
        pokemon['name'] = matches[0][1]
        pokemon['html'] = html
        pokemon['variant'] = matches[0][0] == '/alt'

        # If it's a variant ("/alt" is present in the matched string)
        # is_variant = matches[0][0] == '/alt'
        # pokemon_name = matches[0][1]


        # check if pokemon is downloaded
        if pokemon_and_variant_exists_in_database(pokemon):
            print(f"El archivo {pokemon['name']}.html ya existe.")
            counter += 1
        else:
            pokemon_id = save_pokemon_to_database(pokemon['name'], 1)
            save_in_pokedex(pokemon, pokemon['variant'])

            if pokemon['variant']:
                save_variant_to_database(pokemon_id, html)
                print(f"Se guardó la variante de {pokemon['name']}.html.")
            else:
                print(f"El archivo se ha guardado como:{pokemon['name']}.html.")

            save_in_pokedex(pokemon)
    else:
        print("No se encontró el nombre del Pokémon en el contenido HTML.")
        print(f"Nombre: {html} ")

    # Cerrar el navegador
    driver.quit()
    return counter


def save_in_pokedex(pokemon, is_variant=False):
    # Create the pokedex directory if it doesn't exist
    if not os.path.exists(FOLDER_PATH):
            os.makedirs(FOLDER_PATH)

    # Create a specific directory for each Pokémon
    pokemon_folder_path = os.path.join(FOLDER_PATH, pokemon["name"])
    if not os.path.exists(pokemon_folder_path):
        os.makedirs(pokemon_folder_path)

    # Determine the filename
    # If it's a variant, then find the next available variant number
    if is_variant:
        variant_num = 1
        while os.path.exists(os.path.join(pokemon_folder_path, f'{pokemon["name"]}_variant_{variant_num}.html')):
            variant_num += 1
        filename = os.path.join(pokemon_folder_path, f'{pokemon["name"]}_variant_{variant_num}.html')
    else:
        filename = os.path.join(pokemon_folder_path, f'{pokemon["name"]}.html')
        # Save the HTML content to the determined filename

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(pokemon["html"])
            
 
def get_pokemon_list_downloaded():
    folder_path = 'pokedex'
    return [pokemon.split('.')[0] for pokemon in os.listdir(folder_path)]

def compare_if_pokemon_is_downloaded(pokemon_name):
    return pokemon_name in get_pokemon_list_downloaded()

if __name__ == '__main__':
    setup_database()
    counter = 0
    while True:
        # break if 100 pokemon are downloaded
        if counter == 200:
            break
        
        limit_counter = save_pokemon(counter)
        time.sleep(0)
  