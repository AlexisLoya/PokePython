class Pokemon:
    def __init__(self, name, generation, variants: tuple = (), id: int =None):
        self.id: int = id
        self.name: str = name
        self.generation: int = generation
        self.variants: tuple = variants

    def __str__(self):
        return f"Pokemon: {self.name} - Variants:{len(self.variants)} (Generation: {self.generation})"


class Variant:
    def __init__(self, html, name=None, id=None):
        self.id: int = id
        self.name: str = name
        self.html: str = html

    def __str__(self):
        return f"Variant: {self.id}"


class PokemonDAO:
    def __init__(self, conn):
        self.conn = conn

    def save_pokemon(self, pokemon):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO pokemons (name, generation) VALUES (?, ?)", (pokemon.name, pokemon.generation))
        pokemon_id = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        return pokemon_id

    def save_variant(self, pokemon_id, filename, html):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO variants (pokemon_id, filename, html) VALUES (?, ?, ?)",
                       (pokemon_id, filename, html))
        self.conn.commit()
        cursor.close()

    def get_pokemon_by_name(self, name):

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, generation FROM pokemons WHERE name=?", (name,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            id, name, generation = result
            return Pokemon(id=id, name=name, generation=generation)

        return None

    def get_variants(self, pokemon_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT html FROM variants WHERE pokemon_id=?", (pokemon_id,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def pokemon_exists(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM pokemons WHERE name=?", (name,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def variant_already_exists(self, pokemon_id, html):
        existing_variants = self.get_variants(pokemon_id)

        for variant in existing_variants:
            if variant[0] == html:
                return True
        return False

