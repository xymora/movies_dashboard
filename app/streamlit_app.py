import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Inicializar Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection_name = "movies"
    firestore_active = True
except Exception as e:
    st.warning(f"⚠️ No se pudo conectar a Firebase: {e}")
    firestore_active = False

# Función segura para cargar datos desde Firestore (corte en 5 segundos)
@st.cache_data
def load_data():
    if firestore_active:
        data = []
        try:
            start_time = time.time()
            docs = db.collection(collection_name).limit(50).stream()
            for doc in docs:
                if time.time() - start_time > 5:
                    raise TimeoutError("⏱️ Firestore tardó demasiado.")
                d = doc.to_dict()
                d["id"] = doc.id
                data.append(d)
            return pd.DataFrame(data)
        except Exception as e:
            st.warning(f"⚠️ Error al leer Firestore: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

# Cargar datos
df = load_data()

# Título
st.title("🎬 Movies Dashboard")

# Mostrar vista previa para depuración
st.subheader("🧪 Vista previa de datos crudos")
st.write(df.head())
st.write("Columnas disponibles:", df.columns.tolist())

# Si no hay datos
if df.empty:
    st.warning("No hay datos disponibles en Firestore.")
else:
    available_filters = {}

    with st.sidebar:
        st.header("🎛️ Filtros disponibles")

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

    # Aplicar filtros
    filtered_df = df.copy()
    for col, vals in available_filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(vals)]

    # Mostrar resultados
    st.subheader("📋 Películas filtradas")
    st.dataframe(filtered_df)
    st.markdown(f"🎯 Total encontradas: **{len(filtered_df)}**")

# ---------------------
# Formulario para agregar nueva película
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
            if firestore_active:
                db.collection(collection_name).add(doc)
                st.cache_data.clear()
                st.sidebar.success(f"Película '{new_title}' agregada exitosamente.")
                st.experimental_rerun()
            else:
                st.sidebar.error("🚫 No se pudo guardar. Firestore está inactivo.")
