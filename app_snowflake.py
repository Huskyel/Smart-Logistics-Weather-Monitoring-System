import streamlit as st
import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Cloud Logistics Dashboard", layout="wide")

def get_snowflake_data():
    conn = snowflake.connector.connect(
        user=os.getenv('SNOW_USER'),
        password=os.getenv('SNOW_PASS'),
        account=os.getenv('SNOW_ACCOUNT'),
        database='LOGISTYKA_CLOUD',
        schema='PUBLIC'
    )

    query = "SELECT * FROM ANALIZA_RYZYKA_LOGISTYCZNEGO"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("System Monitoringu Floty (Cloud Edition)")
st.write("Dane pobierane bezpośrednio z **Snowflake Data Warehouse**")

try:
    df = get_snowflake_data()

    col1, col2, col3 = st.columns(3)
    col1.metric("Liczba punktów", len(df))
    col2.metric("Średnia Temp", f"{round(df['TEMP'].mean(), 1)}°C")
    col3.metric("Najwyższe Ryzyko", df[df['STATUS_FLOTY'] != 'WARUNKI OPTYMALNE']['MIASTO'].count())

    st.subheader("Aktualny status transportów")
    
    def color_status(val):
        color = 'red' if 'ZAGROŻENIE' in val else 'green'
        return f'color: {color}'

    st.dataframe(df.style.map(color_status, subset=['STATUS_FLOTY']))

    st.subheader("Porównanie temperatur w miastach")
    st.bar_chart(df.set_index('MIASTO')['TEMP'])

except Exception as e:
    st.error(f"Błąd połączenia ze Snowflake: {e}")
    st.info("Upewnij się, że dane w .env są poprawne.")