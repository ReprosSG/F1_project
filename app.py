import streamlit as st
import pandas as pd
import os

# config de base de la page
st.set_page_config(
    page_title = "Dashboard F1",
    layout = "wide"
)

#titre principal
st.title("Tableau de bord de Formule 1")
st.markdown("---")
st.write("Bienvenue ! Les donnees de la couche gold sont affichées ici !")

#chargement des donnéees

@st.cache_data

def load_data():
    chaine_connexion = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    df = pd.read_parquet("az://gold/drivers/gold_drivers_by_country.parquet",
                         storage_options={"connection_string": chaine_connexion})
    return df

try:
    df_pays = load_data()
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Table Gold")
        st.dataframe(df_pays, use_container_width=True)
    with col2:
        st.write(" Répartition des pilotes")
        st.bar_chart(df_pays.set_index('nationalite'))
    
except Exception as e:
    st.error(f"Impossible de charger la donnée depuis Azure {e}")