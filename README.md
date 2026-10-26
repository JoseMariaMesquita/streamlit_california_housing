Aplicación Streamlit para el precio de casas en California

Esta aplicación permite estimar el precio medio de las viviendas en California mediante un modelo de inteligencia artificial.
El proyecto está formado por dos servicios: una API desarrollada con FastAPI y una interfaz web desarrollada con Streamlit.
El usuario introduce dos variables: el ingreso medio de la zona y el número medio de habitaciones por vivienda.
Las seis variables restantes se completan automáticamente con valores predeterminados.
La interfaz comprueba que estén presentes las ocho variables necesarias antes de enviar la petición.
A continuación, realiza una petición HTTP POST al endpoint /predict de la API.
La API procesa los datos con el modelo de predicción y devuelve el valor estimado de la vivienda.
Finalmente, Streamlit transforma el resultado a dólares y lo muestra en pantalla.
La aplicación también controla los errores de comunicación y las respuestas HTTP de error de la API.

Autores: <nombre1>, <nombre2>

Servicios desplegados en Render
Servicio	Qué es	URL
API	FastAPI con el modelo de predicción (app.py)	https://tu-servicio-api.onrender.com
Interfaz	Aplicación Streamlit (streamlit_app.py) que llama a la API	https://tu-servicio-streamlit.onrender.com

Importante: sustituye las URL de ejemplo por las direcciones reales de tus servicios en Render.

Cómo ejecutarla en local
1. Instalar las dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

bash
pip install -r requirements.txt

2. Arrancar la API

Abre una primera terminal y ejecuta:

bash
uvicorn app:app --reload


La API estará disponible en:

API: http://localhost:8000
Documentación interactiva: http://localhost:8000/docs
3. Arrancar la interfaz Streamlit

Abre una segunda terminal, en la misma carpeta del proyecto, y ejecuta:

bash
streamlit run streamlit_app.py


La interfaz estará disponible normalmente en http://localhost:8501.

En la barra lateral de Streamlit, introduce esta URL para conectar con la API local:

text
http://localhost:8000


Ambos servicios deben estar en funcionamiento para que la aplicación pueda realizar predicciones.

Despliegue en Render

El proyecto se despliega mediante dos servicios web independientes.

1. Servicio API (FastAPI)

Build Command:

bash
pip install -r requirements.txt


Start Command:

bash
uvicorn app:app --host 0.0.0.0 --port $PORT


Una vez desplegada, copia la URL pública que proporciona Render.

2. Servicio de interfaz (Streamlit)

Build Command:

bash
pip install -r requirements.txt


Start Command:

bash
streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true

3. Conectar la interfaz con la API desplegada

En streamlit_app.py, busca la variable API_URL y sustituye la dirección local por la URL pública de la API:

python
API_URL = "https://tu-servicio-api.onrender.com"


Sustituye tu-servicio-api por el nombre real del servicio de FastAPI en Render.

También puedes introducir la URL de la API desde la barra lateral de Streamlit.

Importante: la interfaz debe utilizar la URL pública de la API cuando esté desplegada. No debe utilizar localhost:8000, porque en Render cada servicio se ejecuta de forma independiente.

Documentación de la API

URL base local: http://localhost:8000

URL base desplegada: https://tu-servicio-api.onrender.com

Sustituye la URL desplegada por la dirección real de tu API.

POST /predict

Este endpoint recibe una petición JSON con las ocho variables necesarias para estimar el precio medio de las viviendas en una zona de California. Si los datos son válidos, devuelve el valor estimado en cientos de miles de dólares, que la interfaz convierte posteriormente a dólares.

Variables de entrada
Variable	Descripción	Valor utilizado por la aplicación
MedInc	Ingreso medio de la zona	Introducido por el usuario
HouseAge	Antigüedad media de las viviendas	29.0
AveRooms	Número medio de habitaciones por vivienda	Introducido por el usuario
AveBedrms	Número medio de dormitorios por vivienda	1.05
Population	Población de la zona	1166.0
AveOccup	Número medio de ocupantes por vivienda	2.8
Latitude	Latitud de la zona	34.26
Longitude	Longitud de la zona	-118.49
Ejemplo de petición

Método: POST

Endpoint: /predict

Cabecera: Content-Type: application/json

Cuerpo JSON:

json
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


La petición también se puede probar con curl:

bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 3.5,
    "HouseAge": 29.0,
    "AveRooms": 5.2,
    "AveBedrms": 1.05,
    "Population": 1166.0,
    "AveOccup": 2.8,
    "Latitude": 34.26,
    "Longitude": -118.49
  }'

Ejemplo de respuesta correcta (200)

Si la API devuelve un valor de 4.53, la respuesta será:

json
{
  "MedHouseVal": 4.53
}


Interpretación: el valor 4.53 representa 453.000 dólares, ya que el modelo expresa el resultado en cientos de miles de dólares.

La interfaz Streamlit realiza la conversión y muestra:

text
Precio estimado: $453,000


Nota: el valor 4.53 es un ejemplo ilustrativo. Para documentar una ejecución real, sustitúyelo por el resultado obtenido al realizar una petición a tu API.

Errores
Código	Cuándo ocurre	Qué muestra la aplicación
200	La predicción se realiza correctamente.	El precio estimado formateado en dólares.
422	Falta una variable obligatoria o algún dato tiene un tipo incorrecto.	El código HTTP y el detalle devuelto por la API.
500	Se produce un error interno en el servidor.	El código HTTP y el texto del error, sin intentar interpretarlo como JSON.
Sin respuesta HTTP	La API no está disponible, la URL es incorrecta o se agota el tiempo de espera.	Un mensaje que recomienda comprobar la URL, el estado del servicio e intentarlo de nuevo.
Validación y pruebas de errores

La aplicación incluye opciones en la barra lateral para comprobar la validación de los datos y el tratamiento de errores.

Prueba 1: validación local

Activa la casilla «Prueba: omitir HouseAge de la petición» y pulsa «Estimar precio».

La aplicación detecta que falta la variable HouseAge, muestra un mensaje de error y no envía la petición a la API.

Prueba 2: respuesta HTTP 422

Activa simultáneamente las casillas:

«Prueba: omitir HouseAge de la petición».
«Prueba: saltar la validación local (provoca un 422 de la API)».

La aplicación envía una petición incompleta. La API debería responder con HTTP 422, y Streamlit muestra el código de error junto con el detalle devuelto.

Prueba 3: fallo de comunicación

Introduce una URL incorrecta en el campo «URL de la API» de la barra lateral y pulsa «Estimar precio».

La aplicación captura el fallo de comunicación y muestra un mensaje claro al usuario, sin interrumpir la ejecución con una excepción sin controlar.

Tecnologías utilizadas
Python: lenguaje de programación.
FastAPI: desarrollo de la API de predicción.
Streamlit: interfaz web interactiva.
Requests: comunicación HTTP entre Streamlit y FastAPI.
Render: despliegue de ambos servicios.
