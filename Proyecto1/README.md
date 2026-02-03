#  Sensor Dashboard (Flask + MongoDB Atlas)

Proyecto demo: aplicación web en Flask que recibe lecturas de un *chip* (colesterol, azúcar, fiebre),
con autenticación (registro / login) usando MongoDB Atlas como base de datos.

**Estructura del proyecto**:
- app.py                -> App Flask principal (rutas, API, auth)
- requirements.txt      -> Dependencias Python
- .env.example          -> Ejemplo de variables de entorno
- templates/            -> Archivos HTML con Tailwind CDN (base, login, register, dashboard)
- static/               -> Archivos estáticos (favicon, css adicional si los deseas)

## Requisitos
- Python 3.9+
- pip

## Instalación (local)
1. Clona o descomprime este proyecto.
2. Crea y activa un virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows (PowerShell)
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura MongoDB Atlas:
   - Crea una cuenta en MongoDB Atlas (https://www.mongodb.com/cloud/atlas), crea un Cluster gratuito.
   - Crea un usuario (username/password) y una base de datos (por ejemplo `refritati_db`).
   - Obtén la URI de conexión (Connection string). Será algo así:
     `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/refritati_db?retryWrites=true&w=majority`
   - Copia la URI en un archivo `.env` con la variable `MONGO_URI` (ver `.env.example`).
5. Crea `.env` (usa .env.example):
   ```bash
   cp .env.example .env
   ```
   Edita `.env` y pega tu `MONGO_URI`.
6. Ejecuta la app:
   ```bash
   python app.py
   ```
   Abre `http://127.0.0.1:5000` en tu navegador.

## Endpoints importantes
- `/register` - registro de usuarios
- `/login` - inicio de sesión
- `/dashboard` - panel del usuario con lecturas del chip
- `POST /api/readings` - API pública para que el chip envíe lecturas (JSON)
  ```json
  {
    "device_id": "chip-01",
    "cholesterol": 180.5,
    "sugar": 95.2,
    "fever": 37.1
  }
  ```
- `GET /api/readings` - obtiene lecturas del usuario (autenticado)

## Seguridad básica
- Las contraseñas se guardan con hashing (werkzeug.security).
- Para producción: usa HTTPS, habilita CORS de forma segura, añade límites de tasa y validación de dispositivos (tokens).

## Diseño
- Se usa Tailwind CDN para lograr un diseño moderno y responsive con micro-interacciones.
- Puedes personalizar colores y animaciones en `templates/base.html`.


