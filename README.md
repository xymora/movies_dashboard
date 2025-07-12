# dashboard_movies

Aplicación interactiva desarrollada con Streamlit para visualizar, buscar, filtrar e insertar información de filmes almacenados en una base de datos Firestore.

## 🚀 Funcionalidades

- Visualización del catálogo completo desde Firestore.
- Búsqueda por título (sin distinción de mayúsculas/minúsculas).
- Filtro por director con selectbox y botón de comando.
- Formulario para insertar nuevos filmes con validación.
- Interfaz limpia y organizada en el sidebar.

## 📁 Estructura del Proyecto

```
dashboard_movies/
├── notebooks/
│   ├── movies_dashboard.ipynb     # Cuaderno en Google Colab
│   └── movies.csv                 # Dataset original descargado
├── app/
│   └── streamlit_app.py           # App principal
├── requirements.txt               # Dependencias
└── README.md                      # Documentación del proyecto
```

## ⚙️ Requisitos

- Python 3.7 o superior
- Librerías:
  - Streamlit
  - Firebase Admin SDK
  - Pandas

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## ▶️ Ejecución local

Desde la raíz del proyecto:

```bash
streamlit run app/streamlit_app.py
```

## 🌐 Despliegue en producción

Este proyecto puede ser desplegado en [Streamlit Cloud](https://streamlit.io/cloud) desde un repositorio en GitHub.

## 📌 Créditos

Desarrollado por **Álvaro Rodrigo Moctezuma Ramírez**, alumno de la certificación
**The Learning Gate para Data Scientist – Tecnológico de Monterrey**.

## 🔐 Seguridad

Se recomienda cargar las credenciales de Firebase mediante `st.secrets` o variables de entorno en producción.
