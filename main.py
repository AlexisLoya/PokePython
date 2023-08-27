from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
import os
import time

def save_pokemon(counter):
    # Ruta al controlador de Chrome
    chrome_driver_path = './chrome/chromedriver.exe'

    # Configuración de Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecutar en modo sin ventana

    # Crear objeto Service para el controlador de Chrome
    service = Service(chrome_driver_path)

    # Crear instancia del controlador de Chrome
    driver = webdriver.Chrome(service=service, options=options)

    # Abrir la página web
    url = 'http://silph.co/'
    driver.get(url)

    # Obtener el contenido HTML completo
    html = driver.page_source

    # Buscar el patrón de la etiqueta <title> que contiene el nombre del archivo (pokemon)
    pattern = r'<title>pokemon/alt/(.*?).html</title>'
    matches = re.findall(pattern, html)
    
    if matches:
        # make pokemon object
        pokemon = {}
        pokemon['name'] = matches[0]
        pokemon['html'] = html
        
        # check if pokemon is downloaded
        if compare_if_pokemon_is_downloaded(pokemon['name']):
            print("El archivo {f}.html ya existe.".format(f=pokemon['name']))
            counter += 1
        else:
            save_in_pokedex(pokemon)
            print(f"El archivo se ha guardado como: {matches[0]}.html")
    else:
        print("No se encontró el nombre del Pokémon en el contenido HTML.")
        print(f"Nombre: {html} ")

    # Cerrar el navegador
    driver.quit()
    return counter

def save_in_pokedex(pokemon):
        folder_path = 'pokedex'
        
        # Crear la carpeta "pokedex" si no existe
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filename = f'{folder_path}/{pokemon["name"]}.html'

        # Guardar el contenido HTML en un archivo con el nombre del Pokémon
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(pokemon["html"])
            
 
def get_pokemon_list_downloaded():
    folder_path = 'pokedex'
    return [pokemon.split('.')[0] for pokemon in os.listdir(folder_path)]

def compare_if_pokemon_is_downloaded(pokemon_name):
    return pokemon_name in get_pokemon_list_downloaded()

if __name__ == '__main__':
    counter = 0
    while True:
        # break if 100 pokemon are downloaded
        if counter == 200:
            break
        
        limit_counter = save_pokemon(counter)
        time.sleep(0)
  