# ---------------------------------------------------------------
# Dashboard interactivo: Estrés en el Deporte de Alto Rendimiento
# Autor: Tu nombre
# ---------------------------------------------------------------
# 📦 Requerimientos (instala antes de ejecutar):
# pip install streamlit==1.39.0
# pip install requests==2.32.3
# ---------------------------------------------------------------

import streamlit as st
import requests

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(
    page_title="Cuestionario: Estrés Deportivo",
    page_icon="💪",
    layout="centered"
)

# --- URL DEL ARCHIVO JSON EN GITHUB ---
# Debes reemplazar el siguiente enlace por el tuyo en formato RAW:
# Ejemplo: https://raw.githubusercontent.com/usuario/repositorio/main/items.json
URL_JSON = "https://raw.githubusercontent.com/usuario/repositorio/main/items.json"

# --- FUNCIÓN PARA CARGAR LOS DATOS ---
@st.cache_data
def cargar_items(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {e}")
        return []

items = cargar_items(URL_JSON)

# --- VARIABLES DE SESIÓN ---
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "puntaje" not in st.session_state:
    st.session_state.puntaje = 0
if "respondido" not in st.session_state:
    st.session_state.respondido = False

# --- INTERFAZ PRINCIPAL ---
st.title("🏋️‍♂️ Cuestionario: Estrés en el Deporte de Alto Rendimiento")
st.caption("Responde cada pregunta. Obtendrás retroalimentación inmediata y un puntaje final al terminar.")

if not items:
    st.warning("⚠️ No se encontraron preguntas. Verifica el archivo JSON en GitHub.")
else:
    # Si aún quedan preguntas
    if st.session_state.indice < len(items):
        item = items[st.session_state.indice]
        st.subheader(f"Pregunta {st.session

