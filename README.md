# RefriTati – Monitor de Salud Básico

Proyecto demo: aplicación web en **Flask** que recibe lecturas biométricas (colesterol, glucosa, temperatura) enviadas por un dispositivo (chip/simulador), con autenticación de usuarios y almacenamiento en **MongoDB Atlas**.

![Dashboard preview](https://via.placeholder.com/800x400.png?text=Dashboard+RefriTati+Preview)  
*(próximamente: captura real del dashboard)*

## Características principales

- Registro e inicio de sesión de usuarios
- Recepción de lecturas biométricas vía API (POST)
- Visualización de historial de lecturas en dashboard personal
- Base de datos en la nube (MongoDB Atlas)
- Interfaz moderna y responsive con **Tailwind CSS** (vía CDN)
- Autenticación con contraseñas hasheadas
- API simple para integración con dispositivos hardware

## Tecnologías utilizadas

- **Backend**: Flask (Python)
- **Base de datos**: MongoDB Atlas
- **Autenticación**: Flask + werkzeug.security
- **Frontend**: HTML + Tailwind CSS (CDN) + Alpine.js (opcional)
- **Entorno**: python-dotenv

## Requisitos mínimos

- Python 3.9 o superior
- pip
- Cuenta gratuita en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

## Instalación (desarrollo local)

1. Clona o descomprime el proyecto

```bash
git clone <URL-del-repositorio>
cd refritati

Crea y activa entorno virtual

Bash# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows (cmd)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

Instala dependencias

Bashpip install -r requirements.txt

Configura MongoDB Atlas
Crea cuenta en https://www.mongodb.com/cloud/atlas
Crea un cluster gratuito (M0)
Crea un usuario de base de datos
Crea una base de datos (ejemplo: refritati_db)
Copia la Connection String (formato SRV)
Ejemplo:textmongodb+srv://usuario:contraseña@cluster0.xxxxx.mongodb.net/refritati_db?retryWrites=true&w=majority
Crea y configura el archivo .env

Bashcp .env.example .env
Abre .env y pega tu cadena de conexión:
envMONGO_URI=mongodb+srv://<tu-usuario>:<tu-contraseña>@...
SECRET_KEY=tu-clave-secreta-super-larga-aqui   # ¡cámbiala!

Inicia la aplicación

Bashpython app.py
Abre en el navegador:
→ http://127.0.0.1:5000
Endpoints principales


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



RutaMétodoDescripciónAutenticación/GETPágina principal (redirige a login)No/registerGET/POSTRegistro de usuarioNo/loginGET/POSTInicio de sesiónNo/dashboardGETPanel con lecturas del usuarioSí/api/readingsPOSTRecibe lecturas del dispositivo (JSON)No*/api/readingsGETObtiene lecturas del usuario autenticadoSí

* Actualmente la ruta POST es pública (para facilitar pruebas con el chip).
En producción se recomienda protegerla con token por dispositivo o IP.
Ejemplo de payload para /api/readings (POST):
JSON{
  "device_id": "chip-01",
  "cholesterol": 180.5,
  "sugar": 95.2,
  "fever": 37.1
}

Seguridad – Notas importantes
Estado actual (demo):

Contraseñas hasheadas con werkzeug.security
Sesiones básicas con Flask

Para producción se debe implementar:

HTTPS (obligatorio)
Validación y token por dispositivo
Rate limiting (Flask-Limiter)
CORS restringido
Protección contra ataques comunes (CSRF ya incluido en forms)

Estructura del proyecto
text.
├── app.py               # Aplicación principal Flask + rutas + auth
├── requirements.txt     # Dependencias
├── .env.example         # Plantilla de variables de entorno
├── .gitignore
├── static/              # favicon.ico, css personalizado, etc.
├── templates/
│   ├── base.html        # Plantilla base con Tailwind
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── README.md
Próximos pasos / Ideas de mejora

Gráficos de evolución (Chart.js o similar)
Alertas por email/SMS cuando valores están fuera de rango
Autenticación de dispositivos (API keys o JWT por chip)
Soporte multi-dispositivo por usuario
Exportación de datos (CSV/PDF)
Versión móvil progresiva (PWA)
Tests unitarios (pytest)

¡Cualquier contribución o sugerencia es bienvenida!

Hecho con ♥ por [Harvey Castellanos / Davsergamer1 ]
