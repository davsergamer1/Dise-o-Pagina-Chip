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
