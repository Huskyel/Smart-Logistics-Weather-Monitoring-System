import requests
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PUNKTY_KONTROLNE = [
    {"miasto": "Warszawa", "rola": "Centrum Przeładunkowe"},
    {"miasto": "Berlin", "rola": "Magazyn Docelowy"},
    {"miasto": "Poznan", "rola": "Punkt Kontrolny"}
]

def analizuj_pogode_logistyczna(miasto):
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={miasto}&appid={api_key}&units=metric&lang=pl"
    
    try:
        response = requests.get(url).json()
        
        temp = response['main']['temp']
        wiatr = response['wind']['speed']
        warunki = response['weather'][0]['main'] # np. "Rain", "Snow", "Clear"
        opis = response['weather'][0]['description']
        lat = response['coord']['lat']
        lon = response['coord']['lon']
        
        poziom_ryzyka = "NISKIE"
        zalecenie = "Kontynuuj transport"

        if wiatr > 20 or warunki in ["Snow", "Thunderstorm"]:
            poziom_ryzyka = "WYSOKIE"
            zalecenie = "Wstrzymaj wyjazd / Wyślij alert do kierowców"
        elif temp < 0 or warunki == "Rain":
            poziom_ryzyka = "ŚREDNIE"
            zalecenie = "Zachowaj ostrożność, możliwe opóźnienia"

        return {
        "miasto": miasto,
        "temp": response['main']['temp'],
        "lat": response['coord']['lat'],
        "lon": response['coord']['lon'],
        "opis": response['weather'][0]['description'],  # <-- UPEWNIJ SIĘ, ŻE TO TU JEST
        "ryzyko": poziom_ryzyka,
        "zalecenie": zalecenie
    }
    except Exception as e:
        print(f"Błąd dla miasta {miasto}: {e}")
        return None
    
if __name__ == "__main__":
    print("=== SYSTEM MONITORINGU POGODY LOGISTYCZNEJ v1.0 ===\n")
    raporty = []
    for punkt in PUNKTY_KONTROLNE:
        wynik = analizuj_pogode_logistyczna(punkt['miasto'])
        if wynik:
            raporty.append(wynik)
            print(f"📍 {punkt['miasto']} ({punkt['rola']}):")
            print(f"   Pogoda: {wynik['opis']}, Temp: {wynik['temp']}°C")
            print(f"   RYZYKO: {wynik['ryzyko']} -> {wynik['zalecenie']}\n")

def inicjalizuj_baze():
    conn = sqlite3.connect('logistyka.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raporty_pogodowe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_pomiaru TEXT,
            miasto TEXT,
            temperatura REAL,
            lat REAL,   -- NOWA KOLUMNA
            lon REAL,   -- NOWA KOLUMNA
            ryzyko TEXT,
            zalecenie TEXT
        )
    ''')
    conn.commit()
    conn.close()

def zapisz_do_bazy(wynik):
    conn = sqlite3.connect('logistyka.db')
    cursor = conn.cursor()
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO raporty_pogodowe (data_pomiaru, miasto, temperatura, lat, lon, ryzyko, zalecenie)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (teraz, wynik['miasto'], wynik['temp'], wynik['lat'], wynik['lon'], wynik['ryzyko'], wynik['zalecenie']))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("=== SYSTEM LOGISTYCZNY SQL v1.0 ===\n")
    
    inicjalizuj_baze()
    
    for punkt in PUNKTY_KONTROLNE:
        wynik = analizuj_pogode_logistyczna(punkt['miasto'])
        
        if wynik:
            zapisz_do_bazy(wynik)
            
            print(f"✅ Dane dla {punkt['miasto']} zapisane w bazie.")
            print(f"   Status: {wynik['ryzyko']} ({wynik['temp']}°C)")
    
    print("\n--- PROCES ZAKOŃCZONY ---")

    import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Logistics Weather Dashboard", layout="wide")

st.title("🚚 System Monitoringu Ryzyka Logistycznego")
st.markdown("Raport generowany na podstawie danych pogodowych i bazy SQL")

def pobierz_dane():
    conn = sqlite3.connect('logistyka.db')
    df = pd.read_sql_query("SELECT * FROM raporty_pogodowe ORDER BY id DESC", conn)
    conn.close()
    return df

df = pobierz_dane()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Liczba kontroli", len(df))
with col2:
    ryzyko_high = len(df[df['ryzyko'] == 'WYSOKIE'])
    st.metric("Alerty (WYSOKIE)", ryzyko_high, delta_color="inverse")
with col3:
    ostatnie_miasto = df['miasto'].iloc[0] if not df.empty else "Brak"
    st.info(f"Ostatnia kontrola: {ostatnie_miasto}")

st.subheader("Historia Temperatur w Punktach Kontrolnych")
if not df.empty:
    fig = px.line(df, x="data_pomiaru", y="temperatura", color="miasto", markers=True)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Szczegóły raportów")
st.dataframe(df, use_container_width=True)

st.subheader("Lokalizacja Punktów Kontrolnych")
if not df.empty:
    st.map(df)