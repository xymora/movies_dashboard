import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import concurrent.futures

# Intentar inicializar Firebase
firestore_active = False
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    collection_name = "movies"
    firestore_active = True
except Exception as e:
    st.warning(f"⚠️ No se pudo inicializar Firebase: {e}")

# Función que intenta leer desde Firestore
def try_firestore_fetch():
    try:
        docs = db.collection(collection_name).limit(50).stream()
        data = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            data.append(d)
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

# Función principal con fallback a CSV
@st.cache_data
def load_data():
    if firestore_active:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(try_firestore_fetch)
                df = future.result(timeout=5)  # máximo 5 segundos
                if not df.empty:
                    return df
                else:
                    st.warning("⚠️ Firestore respondió vacío. Usando CSV local.")
        except Exception as e:
            st.warning(f"⚠️ Firestore no respondió a tiempo: {e}")

    # Fallback si Firestore falla
    try:
        st.info("📂 Cargando datos desde 'movies.csv'...")
        return pd.read_csv("movies.csv")
    except Exception as e:
        st.error(f"❌ No se pudo cargar Firestore ni CSV: {e}")
        return pd.DataFrame()
