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
# Reemplaza por el enlace RAW de tu archivo items.json
# Ejemplo: "https://raw.githubusercontent.com/usuario/repositorio/main/items.json"
URL_JSON = "https://raw.githubusercontent.com/sofiaamata/Estres-en-el-deporte-de-alto-rendimiento/main/item.json"

# --- FUNCIÓN PARA CARGAR LOS DATOS DESDE GITHUB ---
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
        st.subheader(f"Pregunta {st.session_state.indice + 1} de {len(items)}")
        st.write(item["pregunta"])

        # Mostrar opciones
        opcion = st.radio("Selecciona una opción:", item["opciones"], index=None)

        # Botón de respuesta
        if st.button("Responder"):
            if opcion is None:
                st.warning("Selecciona una opción antes de continuar.")
            else:
                correcta = item["opciones"][item["correcta"]]
                if opcion == correcta:
                    st.success("✅ ¡Correcto!")
                    st.session_state.puntaje += 1
                else:
                    st.error(f"❌ Incorrecto. La respuesta correcta era: '{correcta}'")

                # Mostrar justificación
                st.info(f"💡 {item['justificacion']}")
                st.session_state.respondido = True

        # Botón siguiente solo si ya respondió
        if st.session_state.respondido:
            if st.button("➡️ Siguiente pregunta"):
                st.session_state.indice += 1
                st.session_state.respondido = False

    # Si ya terminó todas las preguntas
    else:
        st.success("🎉 ¡Has completado el cuestionario!")
        total = len(items)
        puntaje = st.session_state.puntaje
        porcentaje = (puntaje / total) * 100

        st.metric(label="Puntaje final", value=f"{puntaje}/{total}")
        st.progress(porcentaje / 100)

        if porcentaje == 100:
            st.balloons()
            st.write("🏆 ¡Excelente! Has respondido todo correctamente.")
        elif porcentaje >= 70:
            st.write("👏 Buen trabajo, tienes un dominio sólido del tema.")
        else:
            st.write("💡 Sigue practicando, puedes mejorar con un poco más de estudio.")

        # Botón para reiniciar
        if st.button("🔁 Reiniciar cuestionario"):
            st.session_state.indice = 0
            st.session_state.puntaje = 0
            st.session_state.respondido = False
