# Chemnitz Library News Scraper

Extrahiert aktuelle News-Artikel von [stadtbibliothek-chemnitz.de](https://www.stadtbibliothek-chemnitz.de/) und speichert Titel, Link, Datum und Vorschaubild in einer SQLite-Datenbank.

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung

```bash
python chemnitz_library_scraper.py
```

### Optionen

| Option | Env-Variable | Standard | Beschreibung |
|---|---|---|---|
| `--db` | `SCRAPER_DB_PATH` | `/usr/local/sisis-pap/wwwdir/cgi-bin/news.sqlite` | Pfad zur SQLite-Datenbank |
| `--proxy` | `SCRAPER_PROXY` | `http://proxy:3128` | HTTP(S)-Proxy (leerer String deaktiviert) |
| `--limit` | `SCRAPER_LIMIT` | `5` | Max. Anzahl News-Einträge |
| `--url` | `SCRAPER_URL` | `https://www.stadtbibliothek-chemnitz.de/` | URL zum Scrapen |
| `--verbose` / `-v` | – | aus | Debug-Logging aktivieren |

### Beispiele

```bash
# Ohne Proxy, eigene Datenbank
python chemnitz_library_scraper.py --proxy "" --db ./news.sqlite

# Per Environment-Variablen
export SCRAPER_DB_PATH=./news.sqlite
export SCRAPER_PROXY=""
python chemnitz_library_scraper.py

# Mehr Einträge mit Debug-Ausgabe
python chemnitz_library_scraper.py --limit 10 -v
```

## Datenbank-Schema

Das Script erwartet eine bestehende SQLite-Tabelle `news` mit den Spalten:

| Spalte | Beschreibung |
|---|---|
| `ID` | Primärschlüssel (1-basiert) |
| `link` | HTML-Link zum Artikel |
| `title` | HTML-Titel (`<h3>`-Tag) |
| `kat` | Kategorie (wird auf `"News"` gesetzt) |
| `image` | HTML-Bild-Tag (Thumbnail) |
