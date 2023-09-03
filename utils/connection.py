import sqlite3

def setup_database():
    conn = sqlite3.connect('pokedex.db')
    c = conn.cursor()

    # Create a new table to store Pokemons and their generations
    c.execute('''
    CREATE TABLE IF NOT EXISTS pokemons (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL unique,
        generation INTEGER,
        html TEXT NOT NULL,
        UNIQUE(name)
    ) 
    ''')
    # Create a variants table
    c.execute('''
        CREATE TABLE IF NOT EXISTS variants (
            id INTEGER PRIMARY KEY,
            pokemon_id INTEGER not null,
            html TEXT NOT NULL unique,
            FOREIGN KEY (pokemon_id) REFERENCES pokemons(id)
        )
        ''')

    conn.commit()
    conn.close()