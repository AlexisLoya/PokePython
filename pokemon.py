import difflib


class Pokemon:
    def __init__(self, name, generation, html, variant=False, id=None):
        self.id = id
        self.name = name
        self.generation = generation
        self.html = html
        self.variant = variant

    def __str__(self):
        return f"Pokemon: {self.name} (Generation: {self.generation})"

    def similar(self, html):
        normalized_html = ''.join(self.html.split())
        return difflib.SequenceMatcher(None, normalized_html, html).ratio()


class PokemonDAO:
    def __init__(self, db_conn):
        self.conn = db_conn

    def is_variant_similar(self, pokemon):
        # Normalize the content by stripping whitespaces
        cursor = self.conn.cursor()

        cursor.execute("SELECT v.html FROM variants v LEFT JOIN main.pokemons p on p.id = v.pokemon_id WHERE p.name=?", (pokemon.id,))
        variants = cursor.fetchall()

        for variant in variants:
            existing_html = ''.join(variant[0].split())

            if pokemon.similar(existing_html) > 0.95:  # 0.95 is the threshold, can be adjusted
                cursor.close()
                return True

        cursor.close()
        return False

    def save(self, pokemon):

        if pokemon.variant:
            # Check if the variant is similar to an existing one
            if self.is_variant_similar(pokemon):
                print("This variant is similar to an existing one and won't be saved again.")
                return

            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO variants (pokemon_id, html) VALUES (?, ?)",
                (pokemon.id, pokemon.html)
            )
            self.conn.commit()
            cursor.close()

        if pokemon.id is None:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO pokemons (name, generation, html) VALUES (?, ?, ?)",
                (pokemon.name, pokemon.generation, pokemon.html)
            )
            pokemon.id = cursor.lastrowid
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
            return Pokemon(*result)
        return None

    def get_variants(self, pokemon):
        cursor = self.conn.cursor()
        cursor.execute("SELECT html FROM variants WHERE pokemon_id=?", (pokemon.id,))
        results = cursor.fetchall()
        cursor.close()
        return results

    def pokemon_and_variant_exists_in_database(self, pokemon):
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM pokemons WHERE name=?", (pokemon.name,))
        result = cursor.fetchone()

        if not result:
            return False

        if pokemon.variant:
            cursor.execute("SELECT id FROM variants WHERE pokemon_id=? AND html=?", (result[0], pokemon.html))
            variant_result = cursor.fetchone()

            return variant_result is not None

        return True