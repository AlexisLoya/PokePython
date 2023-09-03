import difflib


class Pokemon:
    def __init__(self, name, generation, html, variant=False, id=None):
        self.id: int = id
        self.name: str = name
        self.generation: int = generation
        self.html: str = html
        self.variant: bool = variant

    def __str__(self):
        return f"Pokemon: {self.name} (Generation: {self.generation})"

    def similar(self, html):
        if isinstance(self.html, tuple):
            self.html = self.html[0]

        print("COMPARING")
        return difflib.SequenceMatcher(None, self.html, html).ratio() > 0.99


class PokemonDAO:
    def __init__(self, db_conn):
        self.conn = db_conn

    def is_variant_similar(self, pokemon):
        # Normalize the content by stripping whitespaces
        cursor = self.conn.cursor()
        print("VARIANTES")
        print(pokemon.name)
        cursor.execute("SELECT v.html FROM variants v LEFT JOIN main.pokemons p on p.id = v.pokemon_id WHERE p.name=?",
                       (pokemon.name,))
        variants = cursor.fetchall()
        print(len(variants))

        for variant in variants:
            existing_html = ''.join(variant[0].split())

            if pokemon.similar(existing_html):
                cursor.close()
                return True

        cursor.close()
        return False

    def save(self, pokemon):

        if pokemon.id is None and not pokemon.variant:
            cursor = self.conn.cursor()
            # capitalize the first letter of the name
            pokemon.name = pokemon.name.capitalize()
            print("INSERTING POKEMON: ", pokemon.name)
            cursor.execute(
                "INSERT INTO pokemons (name, generation, html) VALUES (?, ?, ?)",
                (pokemon.name, pokemon.generation, pokemon.html)
            )
            pokemon.id = cursor.lastrowid
            self.conn.commit()
            cursor.close()

        elif pokemon.variant:
            # Get the id of the pokemon
            original_pokemon: Pokemon = self.get_by_name(pokemon.name)

            cursor = self.conn.cursor()
            print("INSERTING VARIANT")
            print(original_pokemon.id)
            cursor.execute(
                "INSERT INTO variants (pokemon_id, html) VALUES (?, ?)",
                (original_pokemon.id, pokemon.html)
            )
            self.conn.commit()
            cursor.close()

        else:
            self.conn.execute(
                "UPDATE pokemons SET name=?, generation=?, html=? WHERE id=?",
                (pokemon.name, pokemon.generation, pokemon.html, pokemon.id)
            )
            self.conn.commit()

    def get_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, generation, html FROM pokemons WHERE name=?", (name,))

        result = cursor.fetchone()
        cursor.close()

        if result:
            id, name, generation, html = result
            return Pokemon(id=id, name=name, generation=generation, html=html)
        return None

    def get_variants(self, pokemon) -> list:
        cursor = self.conn.cursor()
        print("GETTING VARIANTS")
        print(pokemon.id)
        cursor.execute("SELECT html FROM variants WHERE pokemon_id=?", (pokemon.id,))
        results = cursor.fetchall()
        if results:
            print("SI HAY RESULTADOS")
            return [Pokemon(name=pokemon.name, generation=pokemon.generation, html=html, variant=True) for html in
                    results]
        cursor.close()
        return results

    def pokemon_and_variant_exists_in_database(self, pokemon):
        cursor = self.conn.cursor()
        print("EXISTS IN DATABASE")
        print(pokemon.name)
        cursor.execute("SELECT id FROM pokemons WHERE name=?", (pokemon.name,))
        result = cursor.fetchone()
        print(result)
        if not result:
            return False

        print(f"SI EXISTE {result}")

        if pokemon.variant:
            # First check if the specific variant exists based on similarity
            if self.is_variant_similar(pokemon):
                print("ES MUY SIMILAR")
                cursor.close()
                return True
            print("NO ES MUY SIMILAR")
            # # Check if any variant exists for the given Pokémon
            # cursor.execute("SELECT id FROM variants WHERE pokemon_id=?", (result[0],))
            # variant_result = cursor.fetchone()
            # cursor.close()
            return False

        cursor.close()
        return True
