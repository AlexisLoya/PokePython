![banner](https://i.imgur.com/NVGKU4X.jpeg)

# PokePython

## Description

PokePython is a web scraping project that uses Selenium to "catch 'em all" — Pokémons, that is. This project scrapes Pokémon and their variant information from [The Silph Road](http://silph.co/) and stores it in an SQLite database for further analysis and usage.

## Libraries Used

- Selenium: For web scraping.
- SQLite: For data storage.
- Logging: For logging activity and errors.
- re (Regex): For pattern matching in strings.
- time: For controlling the time between requests.
- os: For filesystem manipulation.

## Installation Guide

1. **Create a Virtual Environment (venv)**

   ```bash
   python3 -m venv .venv
   ```

2. **Activate the Virtual Environment**

   - **Windows**
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS and Linux**
     ```bash
     source .venv/bin/activate
     ```

3. **Install Dependencies from `requirements.txt`**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download `chromedriver.exe` File**

   - Visit the [ChromeDriver download page](https://sites.google.com/a/chromium.org/chromedriver/downloads).
   - Download the version that matches your Chrome browser version.
   - Extract the `chromedriver.exe` file and place it in the `chrome` folder within the project directory.

## Usage

To start catching all the Pokémons, simply run the `main.py` script.

```bash
python main.py
```

This will initiate the web scraping process and store the data in the SQLite database pokedex.db and as HTML files within the pokedex folder.

## License

This project is under the MIT license. See the [LICENSE](LICENSE) file for more details.
