from main import DATABASE_PATH
from pokemon import Pokemon, PokemonDAO
from utils import DatabaseConnection

if __name__ == '__main__':
    with DatabaseConnection('pokedex.db') as conn:
        dao = PokemonDAO(conn)
        articuno: Pokemon = dao.get_by_name(name='Articuno')
        pp: Pokemon = dao.get_by_name(name='Blastoise')
        print(f'Articuno: {articuno.similar(pp.html)}')
        articuno_variants = dao.get_variants(pokemon=articuno)
        print(f'Articuno variants: {len(articuno_variants)}')
        for pokemon in articuno_variants:
            print(type(pokemon))
            print(pokemon.name)
            print(pokemon.id)
            print(pokemon.generation)
            print(pokemon.similar(pp.html))

