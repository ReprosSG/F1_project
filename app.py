import streamlit as st
import pandas as pd

# config de base de la page
st.set_page_config(
    page_title = "Dashboard F1",
    layout = "wide"
)

#titre principal
st.title("Tableau de bord de Formule 1")
st.markdown("---")
st.write("Bienvenue ! Les donnees de la couche gold sont affichées ici !")

