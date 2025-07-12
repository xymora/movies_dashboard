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

# Leer datos desde Firestore
def get_data():
    docs = db.collection(collection_name).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        # Garantizar claves esperadas
        d.setdefault("title", "")
        d.setdefault("genre", "")
        d.setdefault("rating", "")
        d.setdefault("company", "")
        d.setdefault("director", "")
        data.append(d)
    return pd.DataFrame(data)

df = get_data()

# Sidebar con filtros
st.sidebar.header("🎬 Filtros")

genre_filter = st.sidebar.multiselect("Género", sorted(df["genre"].dropna().unique()))
company_filter = st.sidebar.multiselect("Compañía", sorted(df["company"].dropna().unique()))
rating_filter = st.sidebar.multiselect("Rating", sorted(df["rating"].dropna().unique()))

# Búsqueda por título
st.sidebar.markdown("### 🔍 Buscar por título")
search_title = st.sidebar.text_input("Ingrese nombre o fragmento del título")
search_button = st.sidebar.button("Buscar")

# Agregar nueva película
st.sidebar.markdown("### ➕ Agregar nueva película")
with st.sidebar.form("movie_form"):
    new_title = st.text_input("Título")
    new_genre = st.text_input("Género")
    new_rating = st.text_input("Rating")
    new_company = st.text_input("Compañía")
    new_director = st.text_input("Director")
    submitted = st.form_submit_button("Guardar")

    if submitted and new_title:
        db.collection(collection_name).add({
            "title": new_title,
            "genre": new_genre,
            "rating": new_rating,
            "company": new_company,
            "director": new_director
        })
        st.sidebar.success("Película guardada. Recarga la app para verla.")

# Título principal
st.title("🎥 Dashboard de Películas")

# Aplicar filtros
filtered_df = df.copy()

if genre_filter:
    filtered_df = filtered_df[filtered_df["genre"].isin(genre_filter)]

if company_filter:
    filtered_df = filtered_df[filtered_df["company"].isin(company_filter)]

if rating_filter:
    filtered_df = filtered_df[filtered_df["rating"].isin(rating_filter)]

# Búsqueda por título
if search_button and search_title:
    filtered_df = filtered_df[filtered_df["title"].str.contains(search_title, case=False, na=False)]

# Mostrar resultados
st.markdown("### 📋 Resultados")
cols = ["title", "company", "director", "genre"]
available_cols = [col for col in cols if col in filtered_df.columns]
st.dataframe(filtered_df[available_cols])
