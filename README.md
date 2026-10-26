# Aplicación Streamlit para el precio de casas en California

Esta aplicación estima el precio medio de las viviendas de una zona censal de California a partir de un modelo de machine learning. El usuario introduce dos datos (ingreso medio de la zona y número medio de habitaciones por vivienda); la aplicación completa las otras seis variables con valores por defecto, comprueba que están las 8 que necesita el modelo y consulta la API.

Está formada por dos servicios:

- **API (FastAPI, `app.py`)**: carga `modelo_california.pkl` y expone el endpoint `POST /predict`.
- **Interfaz (Streamlit, `streamlit_app.py`)**: recoge los datos, los valida y llama a la API por HTTP. Convierte la respuesta (cientos de miles de dólares) a dólares y gestiona los errores con mensajes claros.

La interfaz se conecta a la API mediante la URL configurada en `API_URL` (o en la barra lateral de la aplicación).

Autores: SanchezL, MesquitaJ

## Servicios desplegados en Render

| Servicio | Qué es | URL |
|----------|--------|-----|
| API | FastAPI con el modelo (`app.py`) | https://TU-SERVICIO-API.onrender.com |
| Interfaz | Streamlit (`streamlit_app.py`), que llama a la API | https://TU-SERVICIO-STREAMLIT.onrender.com |

> En el plan gratuito de Render los servicios se duermen por inactividad: la primera petición puede tardar más de un minuto.

## Cómo ejecutarla en local

1. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. En una terminal, arranca la API (necesita `modelo_california.pkl` en la misma carpeta):

   ```bash
   uvicorn app:app --reload
   ```

   Queda en http://localhost:8000 (documentación interactiva en `/docs`).

3. En otra terminal, arranca la interfaz:

   ```bash
   streamlit run streamlit_app.py
   ```

4. En la barra lateral de la aplicación, escribe `http://localhost:8000` como **URL de la API**.

## Despliegue en Render

**API (Web Service)**

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

**Interfaz (Web Service)**

- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
- URL de la API: se cambia en la constante `API_URL` de `streamlit_app.py` (debe ser la URL pública del servicio API) o, sin tocar código, en el campo "URL de la API" de la barra lateral.

## Documentación de la API

URL base: <https://TU-SERVICIO-API.onrender.com>

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health-check: devuelve `{"status": "ok"}` |
| POST | `/predict` | Estima el precio medio de las viviendas |

### `POST /predict`

Recibe un JSON con las 8 variables numéricas del modelo (una zona censal) y devuelve `MedHouseVal`, el precio medio estimado en cientos de miles de dólares.

**Ejemplo de petición**

```json
{
  "MedInc": 3.5,
  "HouseAge": 29.0,
  "AveRooms": 5.2,
  "AveBedrms": 1.05,
  "Population": 1166.0,
  "AveOccup": 2.8,
  "Latitude": 34.26,
  "Longitude": -118.49
}
```

**Ejemplo de respuesta correcta (200)**

```json
{
  "MedHouseVal": 1.8437
}
```

Equivale a 1,8437 × 100 000 = **$184 370**.

**Errores**

| Código | Cuándo ocurre | Qué muestra la aplicación |
|--------|---------------|---------------------------|
| 422 | Falta un campo o tiene un tipo incorrecto | "Error de la API (HTTP 422). Detalle: …" con el cuerpo devuelto por la API, que indica el campo problemático. Normalmente la validación local lo evita: "Faltan variables obligatorias: …" |
| 500 | Error interno de la API (por ejemplo, fallo del modelo) | "Error de la API (HTTP 500). Detalle: …" con el texto de la respuesta (puede no ser JSON) |
| Sin respuesta | La API no está disponible o tarda más de 90 s | "No se pudo contactar con la API. Comprueba que el servicio está en marcha y que la URL es correcta…", con aviso de que Render puede estar arrancando |

Todos los errores se registran además en el log de la aplicación (`logging`).
