# code.py — Cuestionado: Estrés en el Deporte de Alto Rendimiento
# Requerimientos: pip install streamlit==1.39.0 requests==2.32.3

import streamlit as st
import requests
import json
from urllib.parse import urlparse

st.set_page_config(page_title="Cuestionario: Estrés Deportivo", page_icon="💪", layout="centered")

# --- Pega tu enlace RAW o el enlace de GitHub aquí ---
# El código normaliza enlaces como:
# - https://raw.githubusercontent.com/usuario/repositorio/refs/heads/main/item.json
# - https://github.com/usuario/repositorio/blob/main/item.json
# - https://raw.githubusercontent.com/usuario/repositorio/main/item.json
URL_JSON = "https://raw.githubusercontent.com/sofiaamata/Estres-en-el-deporte-de-alto-rendimiento/refs/heads/main/items.json"

# --- ITEMS RESERVA (si falla la carga remota) ---
ITEMS_RESERVA = [
    {
        "pregunta": "¿Qué es el estrés en el deporte de alto rendimiento?",
        "opciones": [
            "Una respuesta física y psicológica ante demandas percibidas como superiores a los recursos del deportista",
            "Una emoción pasajera sin consecuencias",
            "Una actitud negativa hacia el entrenamiento"
        ],
        "correcta": 0,
        "justificacion": "El estrés en el deporte es una respuesta adaptativa del cuerpo y la mente ante demandas o presiones que el deportista percibe como excesivas."
    }
]

def normalize_github_url(url: str) -> str:
    """
    Normaliza diferentes formatos de URL de GitHub hacia la forma RAW que requests puede descargar:
    - raw.githubusercontent.com/.../refs/heads/...  -> raw.githubusercontent.com/.../...
    - github.com/user/repo/blob/branch/path -> raw.githubusercontent.com/user/repo/branch/path
    Si la URL ya parece raw y correcta, la devuelve tal cual.
    """
    if not url:
        return url

    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path

    # Caso: raw.githubusercontent.com con refs/heads
    if "raw.githubusercontent.com" in netloc and "/refs/heads/" in path:
        path = path.replace("/refs/heads/", "/")
        return f"https://raw.githubusercontent.com{path}"

    # Caso: raw.githubusercontent.com sin refs/heads -> devolver tal cual (asegúrate de que path comience con /usuario/...)
    if "raw.githubusercontent.com" in netloc:
        return f"https://raw.githubusercontent.com{path}"

    # Caso: github.com/.../blob/...
    if "github.com" in netloc and "/blob/" in path:
        path_parts = path.split("/blob/")
        if len(path_parts) == 2:
            repo_part = path_parts[0]  # /usuario/repositorio
            branch_and_file = path_parts[1]  # branch/dir/file.json
            return f"https://raw.githubusercontent.com{repo_part}/{branch_and_file}"

    # Si no se reconoce, devolver original
    return url

@st.cache_data
def intentar_cargas_posibles(url_original: str):
    """
    Intenta cargar el JSON desde varias variantes derivadas de la URL original:
    1) URL normalizada
    2) Si falla, si el nombre de archivo es item.json intenta items.json en la misma ruta
    3) Si la URL era blob GitHub, intenta convertirla a raw (ya hace normalize_github_url)
    Devuelve (data_or_none, debug_info)
    """
    debug = {"tried": [], "error": None}
    try:
        # Normaliza la URL inicial
        url_norm = normalize_github_url(url_original)
        debug["tried"].append(url_norm)

        # Intento 1: descargar la URL normalizada
        try:
            resp = requests.get(url_norm, timeout=10)
            debug["status_1"] = resp.status_code
            if resp.status_code == 200 and resp.text.strip():
                try:
                    data = resp.json()
                    debug["source"] = url_norm
                    return data, debug
                except Exception as je:
                    debug["error"] = f"JSON decode error en intento 1: {je}"
            else:
                debug["error"] = f"HTTP {resp.status_code} o contenido vacío en intento 1"
        except Exception as e:
            debug["error"] = f"Error request intento 1: {e}"

        # Intento 2: si el archivo final se llama item.json -> probar items.json
        # y viceversa; también probar variantes sin 'refs/heads' (ya normalizamos)
        path = url_norm.split("/")
        if len(path) >= 1:
            filename = path[-1]
            if filename.lower().endswith(".json"):
                alt_filename = None
                if filename.lower() == "item.json":
                    alt_filename = "items.json"
                elif filename.lower() == "items.json":
                    alt_filename = "item.json"

                if alt_filename:
                    alt_url = "/".join(path[:-1] + [alt_filename])
                    debug["tried"].append(alt_url)
                    try:
                        resp2 = requests.get(alt_url, timeout=10)
                        debug["status_2"] = resp2.status_code
                        if resp2.status_code == 200 and resp2.text.strip():
                            try:
                                data2 = resp2.json()
                                debug["source"] = alt_url
                                return data2, debug
                            except Exception as je2:
                                debug["error"] = f"JSON decode error en intento 2: {je2}"
                        else:
                            debug["error"] = f"HTTP {resp2.status_code} o contenido vacío en intento 2"
                    except Exception as e2:
                        debug["error"] = f"Error request intento 2: {e2}"

        # Intento 3: si la URL original era un enlace a la página (no raw), ya lo convertimos,
        # pero como último recurso devolvemos None con debug.
        return None, debug

    except Exception as e:
        return None, {"error": str(e)}

# --- Intentar cargar ---
data, debug_info = intentar_cargas_posibles(URL_JSON)

# Si no cargó nada, usar respaldo y mostrar debug
if data is None:
    st.warning("❌ Error al cargar los datos desde GitHub. Se usará un conjunto de preguntas de respaldo.")
    st.info("Detalles de depuración (intentos):")
    st.json(debug_info)
    items = ITEMS_RESERVA
else:
    # Validar estructura básica
    if not isinstance(data, list):
        st.error("El JSON cargado no es una lista de items. Revisa tu archivo JSON en GitHub.")
        st.json({"preview_type": str(type(data)), "debug": debug_info})
        items = ITEMS_RESERVA
    else:
        # validar cada item mínimo
        fallo = False
        for i, it in enumerate(data):
            if not isinstance(it, dict) or "pregunta" not in it or "opciones" not in it or "correcta" not in it:
                st.error(f"Estructura inválida en el item índice {i}. Debe ser un objeto con 'pregunta','opciones','correcta'.")
                fallo = True
                break
        if fallo:
            items = ITEMS_RESERVA
        else:
            items = data
            st.success("✅ Preguntas cargadas correctamente desde GitHub.")
            st.caption(f"Origen: {debug_info.get('source', 'URL proporcionada')}")

# --- Variables de sesión ---
if "indice" not in st.session_state:
    st.session_state.indice = 0
if "puntaje" not in st.session_state:
    st.session_state.puntaje = 0
if "respondido" not in st.session_state:
    st.session_state.respondido = False

# --- Interfaz ---
st.title("🏋️‍♂️ Cuestionario: Estrés en el Deporte de Alto Rendimiento")
st.caption("Responde una pregunta a la vez. Recibirás retroalimentación inmediata.")

if not items or len(items) == 0:
    st.error("No hay preguntas disponibles (ni remotas ni de respaldo). Corrige tu items.json en GitHub.")
else:
    if st.session_state.indice < len(items):
        item = items[st.session_state.indice]
        st.subheader(f"Pregunta {st.session_state.indice + 1} de {len(items)}")
        st.write(item.get("pregunta", "Pregunta sin texto"))

        opciones = item.get("opciones", [])
        if not isinstance(opciones, list) or len(opciones) < 2:
            st.error("Formato de 'opciones' inválido en este item. Debe ser una lista con al menos 2 elementos.")
        else:
            # Usar key único por pregunta
            opcion = st.radio("Selecciona una opción:", opciones, index=0, key=f"opt_{st.session_state.indice}")

            if st.button("Responder", key=f"btn_resp_{st.session_state.indice}"):
                try:
                    correcta_idx = int(item.get("correcta"))
                    correcta_text = opciones[correcta_idx]
                except Exception:
                    correcta_idx = None
                    correcta_text = None

                if correcta_text is None:
                    st.error("Índice de 'correcta' inválido en este item.")
                else:
                    if opcion == correcta_text:
                        st.success("✅ ¡Correcto!")
                        st.session_state.puntaje += 1
                    else:
                        st.error(f"❌ Incorrecto. La respuesta correcta era: '{correcta_text}'")

                    if "justificacion" in item:
                        st.info(f"💡 {item['justificacion']}")

                    st.session_state.respondido = True

            if st.session_state.respondido:
                if st.button("➡️ Siguiente pregunta"):
                    st.session_state.indice += 1
                    st.session_state.respondido = False

    else:
        total = len(items)
        puntaje = st.session_state.puntaje
        porcentaje = round((puntaje / total) * 100, 1)
        st.success("🎉 ¡Has completado el cuestionario!")
        st.metric(label="Puntaje final", value=f"{puntaje}/{total}")
        st.progress(porcentaje / 100)
        st.write(f"Porcentaje: {porcentaje}%")
        if porcentaje == 100:
            st.balloons()
            st.write("🏆 ¡Excelente! Todo correcto.")
        elif porcentaje >= 70:
            st.write("👏 Buen trabajo.")
        else:
            st.write("💡 Revisa el contenido y vuelve a intentarlo.")

        if st.button("🔁 Reiniciar"):
            st.session_state.indice = 0
            st.session_state.puntaje = 0
            st.session_state.respondido = False
            st.experimental_rerun()
