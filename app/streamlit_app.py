import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import concurrent.futures

# Inicializar Firebase con protección
firestore_active = False
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    collection_name = "movies"
    firestore_active = True
except Exception as e:
    st.warning(f"⚠️ Firebase error: {e}")
    firestore_active = False

# Intento de carga desde Firestore
def try_firestore_fetch():
    try:
        docs = db.collection(collection_name).stream()  # Se quita el límite de 50
        data = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            data.append(d)
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# Función definitiva con fallback
@st.cache_data
def load_data():
    if firestore_active:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(try_firestore_fetch)
                df = future.result(timeout=5)
                if not df.empty:
                    return df
                st.warning("Firestore devolvió datos vacíos. Se usa CSV.")
        except:
            st.warning("⏱️ Firestore no respondió. Usando CSV.")
    # Fallback
    try:
        return pd.read_csv("movies.csv")
    except:
        st.error("❌ No se pudo cargar ni Firestore ni movies.csv")
        return pd.DataFrame()

df = load_data()
st.title("🎬 Movies Dashboard")

if df.empty:
    st.warning("No hay datos disponibles.")
else:
    possible_title_cols = ["title", "name", "titulo"]
    title_col = next((c for c in possible_title_cols if c in df.columns), None)

    with st.sidebar:
        st.header("🔍 Filtros personalizados")

        search_text = st.text_input("🔎 Buscar por título")
        search_button = st.button("Buscar")

        filters = {}
        for col_name, label in [("director", "🎬 Director"), ("genre", "🎭 Género"), ("company", "🏢 Compañía")]:
            if col_name in df.columns:
                sel = st.multiselect(label, sorted(df[col_name].dropna().unique()))
                if sel:
                    filters[col_name] = sel

    filtered_df = df.copy()

    # Búsqueda por título
    if title_col and search_text and search_button:
        filtered_df = filtered_df[filtered_df[title_col].astype(str).str.contains(search_text, case=False, na=False)]

    # Filtros dinámicos
    for col, vals in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(vals)]

    st.subheader("📋 Películas filtradas")
    st.dataframe(filtered_df)
    st.markdown(f"🎯 Total encontradas: **{len(filtered_df)}**")

# --------------------------
# Formulario para agregar nueva película
# --------------------------
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
            new_doc = {
                "title": new_title,
                "director": new_director,
                "genre": new_genre,
                "company": new_company,
                "year": int(new_year)
            }
            try:
                if firestore_active:
                    doc_ref = db.collection(collection_name).document()
                    doc_ref.set(new_doc)
                    st.cache_data.clear()
                    st.sidebar.success("Película agregada con éxito.")
                    st.experimental_rerun()
                else:
                    st.sidebar.error("🚫 Firestore inactivo. No se pudo guardar.")
            except Exception as e:
                st.sidebar.error(f"❌ Error al guardar en Firestore: {e}")
