
"""
Plantilla: aplicación Streamlit conectada a tu servicio de IA.

Autores: SanchezL, MesquitaJ

Qué hace la app: el usuario introduce 2 variables (ingreso medio y número de
habitaciones); la app completa el resto con valores por defecto, comprueba que
están las 8 variables, llama a la API (POST /predict), transforma la respuesta
a dólares y la muestra.
"""

import logging
import time
import requests
import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

# Nombres que aparecerán en la interfaz (necesario para las capturas).
AUTORES = "SanchezL, MesquitaJ"

# En local se utiliza localhost. Para desplegar en Render, sustituye esta
# dirección por la URL pública de tu servicio API.
API_URL = "http://localhost:8000"
# API_URL = "https://<tu-servicio-api>.onrender.com"

# Segundos de espera.
TIMEOUT = 90

# Las 8 variables que necesita el modelo.
FEATURE_NAMES = [
    "MedInc", "HouseAge", "AveRooms", "AveBedrms",
    "Population", "AveOccup", "Latitude", "Longitude",
]

# Variables que NO se piden al usuario.
DEFAULTS = {
    "HouseAge": 29.0,
    "AveBedrms": 1.05,
    "Population": 1166.0,
    "AveOccup": 2.8,
    "Latitude": 34.26,
    "Longitude": -118.49,
}


def find_missing(payload: dict) -> list[str]:
    """Devuelve las variables de FEATURE_NAMES que faltan en payload."""

    # TODO 2: identificar las claves ausentes o con valor None.
    return [
        nombre
        for nombre in FEATURE_NAMES
        if payload.get(nombre) is None
    ]


def format_price(med_house_val: float) -> str:
    """Convierte el valor del modelo a un texto legible en dólares."""

    # TODO 3: el valor está expresado en cientos de miles de dólares.
    precio = med_house_val * 100_000
    return f"${precio:,.0f}"


# ---------------------------------------------------------------- Interfaz --

st.set_page_config(page_title="Precio de casas en California")
st.title("Precio de casas en California")
st.caption(f"{AUTORES} - P3")
st.write("Introduce los datos de la zona y estima el precio medio de sus viviendas.")

# Barra lateral: permite cambiar de servidor y provocar errores de prueba.
api_url = st.sidebar.text_input("URL de la API", API_URL).rstrip("/")
simulate_missing = st.sidebar.checkbox("Prueba: omitir HouseAge de la petición")
skip_validation = st.sidebar.checkbox(
    "Prueba: saltar la validación local (provoca un 422 de la API)"
)

# Variables clave que introduce el usuario.
med_inc = st.number_input(
    "Ingreso medio de la zona (decenas de miles de $)",
    min_value=0.0,
    max_value=15.0,
    value=3.5,
    step=0.1,
)

# TODO 6: campo de entrada para el número medio de habitaciones.
ave_rooms = st.number_input(
    "Número medio de habitaciones por vivienda",
    min_value=1.0,
    max_value=15.0,
    value=5.2,
    step=0.1,
)

if st.button("Estimar precio"):
    payload = {
        **DEFAULTS,
        "MedInc": med_inc,
        "AveRooms": ave_rooms,
    }

    if simulate_missing:  # Solo para la prueba de errores.
        payload.pop("HouseAge", None)

    # Apartado b: validar los datos ANTES de enviarlos.
    missing = find_missing(payload)

    if skip_validation and missing:
        logger.warning(
            "Validación local saltada (prueba). Faltan: %s",
            missing,
        )
    elif missing:
        logger.warning("Petición no enviada, faltan: %s", missing)
        st.error(f"Faltan variables obligatorias: {', '.join(missing)}")
        st.stop()

    if "<" in api_url:
        st.error("Configura la URL de la API en la barra lateral o en API_URL.")
        st.stop()

    try:
        start = time.perf_counter()

        with st.spinner(
            "Consultando la API (la primera vez puede tardar más de un minuto)..."
        ):
            # TODO 1: enviar los datos mediante POST al endpoint /predict.
            response = requests.post(
                api_url + "/predict",
                json=payload,
                timeout=TIMEOUT,
            )

        elapsed_ms = (time.perf_counter() - start) * 1000

    except requests.RequestException as exc:
        logger.error("Fallo de comunicación con %s: %s", api_url, exc)

        # TODO 5a: informar al usuario de forma clara.
        st.error(
            "No se pudo contactar con la API. Comprueba que el servicio está "
            "en marcha y que la URL es correcta. Si el servicio está alojado "
            "en Render, puede que esté arrancando; inténtalo de nuevo en unos "
            "instantes."
        )

    else:
        logger.info(
            "POST %s/predict -> HTTP %s en %.0f ms",
            api_url,
            response.status_code,
            elapsed_ms,
        )

        if response.status_code == 200:
            med_house_val = response.json()["MedHouseVal"]

            # TODO 4: mostrar el precio convertido a dólares.
            st.metric(
                "Precio estimado",
                format_price(med_house_val),
            )

            # Mostrar opcionalmente el valor original devuelto por la API.
            st.caption(
                f"Valor original de la API: {med_house_val} "
                "(cientos de miles de dólares)"
            )

        else:
            # TODO 5b: mostrar el código HTTP y el cuerpo de la respuesta.
            # Se utiliza response.text porque los errores 500 pueden no
            # devolver un cuerpo JSON.
            detalle = response.text.strip()

            logger.warning(
                "La API devolvió HTTP %s: %s",
                response.status_code,
                detalle,
            )

            st.error(
                f"Error de la API (HTTP {response.status_code}). "
                f"Detalle: {detalle or 'La API no proporcionó detalles.'}"
            )