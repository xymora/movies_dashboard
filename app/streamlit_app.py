import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import concurrent.futures

# ================================
# 🔐 Inicializar Firebase
# ================================
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

# ================================
# 🔄 Cargar datos desde Firestore
# ================================
def try_firestore_fetch():
    try:
        docs = db.collection(collection_name).stream()
        data = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            data.append(d)
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

@st.cache_data
def load_data():
    if firestore_active:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(try_firestore_fetch)
                df = future.result(timeout=5)
                if not df.empty:
                    return df
                st.warning("Firestore devolvió datos vacíos. Usando CSV.")
        except:
            st.warning("⏱️ Firestore no respondió. Usando CSV.")
    try:
        return pd.read_csv("movies.csv")
    except:
        st.error("❌ No se pudo cargar ni Firestore ni movies.csv.")
        return pd.DataFrame()

df = load_data()

# ================================
# 🎯 Unificar columnas title y name
# ================================
if not df.empty:
    if "title" not in df.columns and "name" in df.columns:
        df["title"] = df["name"]
    elif "title" in df.columns and "name" not in df.columns:
        df["name"] = df["title"]
    elif "title" in df.columns and "name" in df.columns:
        df["title"].fillna(df["name"], inplace=True)
        df["name"].fillna(df["title"], inplace=True)
    else:
        df["title"] = ""
        df["name"] = ""

# ================================
# 🎬 INTERFAZ Streamlit
# ================================
st.title("🎬 Movies Dashboard")

if df.empty:
    st.warning("No hay datos disponibles.")
else:
    with st.sidebar:
        st.header("🔍 Filtros personalizados")
        search_title = st.text_input("🔎 Buscar por título")
        search_btn = st.button("Buscar")

        filters = {}
        for col, label in [("director", "🎬 Director"), ("genre", "🎭 Género"), ("company", "🏢 Compañía")]:
            if col in df.columns:
                selected = st.multiselect(label, sorted(df[col].dropna().unique()))
                if selected:
                    filters[col] = selected

    filtered_df = df.copy()

    # 🔍 Buscar por título
    if search_title and search_btn:
        filtered_df = filtered_df[filtered_df["title"].str.contains(search_title, case=False, na=False)]

    # Aplicar filtros
    for col, selected in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

    st.subheader("📋 Películas filtradas")
    st.dataframe(filtered_df[["title", "company", "director", "genre", "id"]])
    st.markdown(f"🎯 Total encontradas: **{len(filtered_df)}**")

# ================================
# ➕ Formulario para agregar nueva película
# ================================
st.sidebar.markdown("---")
st.sidebar.subheader("🎥 Nuevo filme")

with st.sidebar.form("form_movie"):
    new_title = st.text_input("Título")
    new_director = st.text_input("Director")
    new_genre = st.text_input("Género")
    new_company = st.text_input("Compañía")
    new_year = st.number_input("Año", min_value=1900, max_value=2100, step=1)
    submit = st.form_submit_button("Agregar")

    if submit:
        if not new_title:
            st.sidebar.error("⚠️ El título es obligatorio.")
        else:
            new_doc = {
                "title": new_title,
                "name": new_title,
                "director": new_director,
                "genre": new_genre,
                "company": new_company,
                "year": int(new_year)
            }
            try:
                if firestore_active:
                    db.collection(collection_name).document().set(new_doc)
                    st.cache_data.clear()
                    st.sidebar.success("✅ Película guardada.")
                    st.experimental_rerun()
                else:
                    st.sidebar.error("🚫 Firestore no está activo.")
            except Exception as e:
                st.sidebar.error(f"❌ Error al guardar: {e}")
