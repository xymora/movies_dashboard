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

@st.cache_data
def load_data():
    docs = db.collection(collection_name).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        data.append(d)
    df = pd.DataFrame(data)

    # Convertir name en title si title no existe
    if "name" in df.columns and "title" not in df.columns:
        df.rename(columns={"name": "title"}, inplace=True)

    return df

df = load_data()

st.title("🎬 Movies Dashboard")

if df.empty:
    st.warning("No hay datos disponibles en Firestore.")
else:
    available_filters = {}

    with st.sidebar:
        st.header("🔍 Filtros personalizados y dinámicos")

        # Búsqueda por título (aunque sea columna name)
        search_text = st.text_input("🔎 Buscar por título")
        search_button = st.button("Buscar")

        # Filtros básicos
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

        # Otros filtros automáticos
        excluded_cols = ["id", "title", "director", "genre", "company"]
        for col in df.columns:
            if col not in excluded_cols and df[col].nunique() < 50 and df[col].dtype in [object, int, float]:
                sel = st.multiselect(f"{col.capitalize()}", sorted(df[col].dropna().unique()))
                if sel:
                    available_filters[col] = sel

    # Filtrado
    filtered_df = df.copy()
    for col, vals in available_filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(vals)]

    if "title" in filtered_df.columns and search_text and search_button:
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(search_text, case=False, na=False)
        ]

    st.subheader("📋 Películas filtradas")
    filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
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
            st.cache_data.clear()
            st.sidebar.success(f"Película '{new_title}' agregada exitosamente.")
            st.experimental_rerun()
