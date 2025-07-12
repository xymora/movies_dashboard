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

# Función que intenta leer desde Firestore (pero SIN bloqueo)
def try_firestore_fetch():
    try:
        docs = db.collection(collection_name).limit(50).stream()
        data = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            data.append(d)
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame()

# Función final que interrumpe si tarda mucho
@st.cache_data
def load_data():
    if firestore_active:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(try_firestore_fetch)
                return future.result(timeout=5)  # corta en 5 segundos
        except Exception as e:
            st.warning(f"⚠️ Firestore no respondió a tiempo: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()
