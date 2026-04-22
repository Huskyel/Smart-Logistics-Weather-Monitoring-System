System automatycznego monitorowania warunków pogodowych dla punktów kontrolnych w logistyce, zintegrowany z bazą danych SQL oraz dashboardem analitycznym.

## Główne Funkcjonalności
* **Monitorowanie Punktów Kontrolnych**: Automatyczna analiza pogody dla Warszawy, Berlina i Poznania.
* **Analiza Ryzyka**: System klasyfikuje ryzyko transportowe (NISKIE, ŚREDNIE, WYSOKIE) na podstawie temperatury, prędkości wiatru oraz opadów.
* **Baza Danych SQL**: Archiwizacja raportów pogodowych w lokalnej bazie SQLite (`logistyka.db`).
* **Dashboard Streamlit**: Interaktywna wizualizacja danych historycznych, trendów temperatury oraz lokalizacji punktów na mapie.

## Technologie
* **Język**: Python 3.x
* **Biblioteki**: `pandas`, `requests`, `streamlit`, `plotly`, `sqlite3`
* **API**: OpenWeatherMap API

## Instalacja i Uruchomienie

## Zainstaluj wymagane biblioteki:
   ```bash
   pip install requests pandas streamlit plotly python-dotenv
