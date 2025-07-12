import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Inicializar Firebase desde secrets
if not firebase_admin._apps:
    firebase_json = json.loads(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_json)
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

# Cargar datos
df = load_data()

st.title("🎬 Movies Dashboard")

if df.empty:
    st.warning("No hay datos disponibles en Firestore.")
else:
    st.dataframe(df)
