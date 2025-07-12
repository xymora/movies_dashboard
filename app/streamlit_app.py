import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
collection_name = "movies"

# Función para cargar datos desde Firestore
@st.cache_data
def load_data():
    docs = db.collection(collection_name).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        data.append(d)
    return pd.DataFrame(data)

df = load_data()

st.title("🎬 Movies Dashboard")

if df.empty:
    st.warning("No hay datos disponibles en Firestore.")
else:
    available_filters = {}

    # Detectar nombre de columna para el título
    possible_title_cols = ["title", "name", "titulo"]
    title_col = next((c for c in possible_title_cols if c in df.columns), None)

    with st.sidebar:
        st.header("🔍 Filtros personalizados y dinámicos")

        # Filtro de búsqueda por título (o equivalente), con botón
        search_text = st.text_input("🔎 Buscar por título")
        search_button = st.button("Buscar")

        # Resto de filtros dinámicos
        if "director" in df.columns:
            sel = st.multiselect("🎬 Director", sorted(df["director"].dropna().unique()))
            if sel:
                available_filters["director"] = sel

        if "genre" in df.columns:
            sel = st.multiselect("🎭 Género", sorted(df["genre"].dropna().unique()))
            if sel:
                available_filters["genre"] = sel

        if "company" in df.columns:
            sel = st.multiselect("🏢 Compañía", sorted(df["company"].dropna().unique()))
            if sel:
                available_filters["company"] = sel

        for col in df.columns:
            if col not in ["id", "director", "genre", "company"] and df[col].nunique() < 50 and df[col].dtype in [object, int, float]:
                sel = st.multiselect(f"{col.capitalize()}", sorted(df[col].dropna().unique()))
                if sel:
                    available_filters[col] = sel

        # Si no se encontró columna de título, mostrar aviso
        if not title_col:
            st.error("No se encontró campo de título en los datos.")

    # Aplicar filtros
    filtered_df = df.copy()
    for col, vals in available_filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(vals)]

    # Aplicar búsqueda por título solo si existe la columna y se presionó el botón
    if title_col and search_text and search_button:
        filtered_df = filtered_df[
            filtered_df[title_col].str.contains(search_text, case=False, na=False)
        ]

    st.subheader("📋 Películas filtradas")
    st.dataframe(filtered_df)
    st.markdown(f"🎯 Total encontradas: **{len(filtered_df)}**")

# ---------------------
# Formulario para insertar nuevo filme
# ---------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🎥 Nuevo filme")

with st.sidebar.form(key="form_movie"):
    new_title = st.text_input("Título")
    new_director = st.text_input("Director")
    new_genre = st.text_input("Género")
    new_company = st.text_input("Compañía")
    new_year = st.number_input("Año", min_value=1900, max_value=2100, step=1)

    submit_btn = st.form_submit_button("Agregar")

    if submit_btn:
        if not new_title:
            st.sidebar.error("El título es obligatorio.")
        else:
            doc = {
                "title": new_title,
                "director": new_director,
                "genre": new_genre,
                "company": new_company,
                "year": int(new_year)
            }
            db.collection(collection_name).add(doc)
            # Limpiar el cache para que load_data vuelva a cargar desde Firestore
            st.cache_data.clear()
            st.sidebar.success(f"Película '{new_title}' agregada exitosamente.")
            st.experimental_rerun()
