import os

import pandas as pd
import streamlit as st


# Config de la page

st.set_page_config(
    page_title="Dashboard F1",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# STYLE PERSONNALISE

st.markdown(
    """
    <style>
        /* Réduction de l'espace au-dessus de la page */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        /* En-tête principal */
        .hero {
            padding: 2rem;
            margin-bottom: 1.5rem;
            color: white;
            border-radius: 18px;
            background: linear-gradient(
                120deg,
                #e10600 0%,
                #9e0500 45%,
                #15151e 100%
            );
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.20);
        }

        .hero h1 {
            margin: 0;
            padding: 0;
            color: white;
            font-size: 2.4rem;
            font-weight: 800;
        }

        .hero p {
            margin-top: 0.65rem;
            margin-bottom: 0;
            color: #f1f1f1;
            font-size: 1.05rem;
        }

        /* Conteneurs des sections */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px;
        }

        /* Indicateurs */
        div[data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 14px;
            background-color: rgba(128, 128, 128, 0.05);
        }

        /* Boutons */
        .stButton > button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
        }

        .stDownloadButton > button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
        }

        /* Séparateur rouge */
        .f1-separator {
            height: 4px;
            margin: 0.5rem 0 1.5rem 0;
            border-radius: 4px;
            background: linear-gradient(
                90deg,
                #e10600,
                #ff8700,
                transparent
            );
        }

        /* Pied de page */
        .footer {
            margin-top: 2rem;
            color: #777777;
            text-align: center;
            font-size: 0.85rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# CHARGEMENT DES DONNEES


@st.cache_data(
    ttl=3600,
    show_spinner="Chargement des données depuis Azure..."
)
def load_data():
    connection_string = st.secrets.get(
        "AZURE_STORAGE_CONNECTION_STRING",
        os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
    )

    if not connection_string:
        raise ValueError(
            "La variable AZURE_STORAGE_CONNECTION_STRING "
            "n'est pas configurée."
        )

    dataframe = pd.read_parquet(
        "az://gold/drivers/gold_drivers_by_country.parquet",
        storage_options={
            "connection_string": connection_string
        },
    )

    return dataframe


def find_value_column(dataframe):
    """
    Cherche la colonne numérique représentant le nombre de pilotes.
    """

    priority_columns = [
        "nombre_pilotes",
        "nb_pilotes",
        "nombre_de_pilotes",
        "driver_count",
        "count",
        "total",
    ]

    for column in priority_columns:
        if column in dataframe.columns:
            return column

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns.tolist()

    if numeric_columns:
        return numeric_columns[0]

    return None


def format_column_name(column):
    """
    Transforme 'nombre_pilotes' en 'Nombre Pilotes'.
    """
    return column.replace("_", " ").strip().title()



# EN-TETE


st.markdown(
    """
    <div class="hero">
        <h1>🏎️ Tableau de bord Formule 1</h1>
        <p>
            Analyse de la répartition des pilotes par nationalité,
            à partir des données de la couche Gold.
        </p>
    </div>
    <div class="f1-separator"></div>
    """,
    unsafe_allow_html=True,
)



# CHARGEMENT ET AFFICHAGE


try:
    df_data = load_data()

    if df_data.empty:
        st.warning(
            "Le fichier a bien été chargé, mais il ne contient "
            "aucune donnée."
        )
        st.stop()

    if "nationalite" not in df_data.columns:
        st.error(
            "La colonne `nationalite` est absente du fichier Parquet."
        )
        st.write("Colonnes disponibles :", list(df_data.columns))
        st.stop()

    value_column = find_value_column(df_data)

    if value_column is None:
        st.error(
            "Aucune colonne numérique n'a été trouvée pour construire "
            "le graphique."
        )
        st.stop()

    # Nettoyage léger
    df_data = df_data.copy()

    df_data["nationalite"] = (
        df_data["nationalite"]
        .fillna("Nationalité inconnue")
        .astype(str)
        .str.strip()
    )

    df_data[value_column] = pd.to_numeric(
        df_data[value_column],
        errors="coerce",
    ).fillna(0)

    # ========================================================
    # BARRE LATÉRALE
    # ========================================================

    with st.sidebar:
        st.header("🏁 Filtres")

        st.caption(
            "Personnalisez les données affichées dans le tableau "
            "et dans le graphique."
        )

        nationalities = sorted(
            df_data["nationalite"].dropna().unique().tolist()
        )

        selected_nationalities = st.multiselect(
            "Nationalités",
            options=nationalities,
            default=nationalities,
            placeholder="Sélectionner une nationalité",
        )

        maximum_rows = len(nationalities)

        top_n = st.slider(
            "Nombre de nationalités à afficher",
            min_value=1,
            max_value=max(1, maximum_rows),
            value=min(10, max(1, maximum_rows)),
        )

        st.divider()

        if st.button(
            "🔄 Actualiser les données",
            type="primary",
        ):
            load_data.clear()
            st.rerun()

        st.caption(
            "Source : Azure Data Lake — couche Gold"
        )

    # FILTRAGE

    if selected_nationalities:
        df_filtered = df_data[
            df_data["nationalite"].isin(selected_nationalities)
        ].copy()
    else:
        df_filtered = df_data.iloc[0:0].copy()

    df_chart = (
        df_filtered
        .groupby("nationalite", as_index=False)[value_column]
        .sum()
        .sort_values(value_column, ascending=False)
        .head(top_n)
    )

    # INDICATEURS

    total_drivers = int(df_filtered[value_column].sum())
    total_nationalities = df_filtered["nationalite"].nunique()

    if not df_chart.empty:
        leading_country = df_chart.iloc[0]["nationalite"]
        leading_value = int(df_chart.iloc[0][value_column])
    else:
        leading_country = "Aucune"
        leading_value = 0

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric(
            label="Nombre total de pilotes",
            value=f"{total_drivers:,}".replace(",", " "),
        )

    with metric2:
        st.metric(
            label="Nationalités représentées",
            value=total_nationalities,
        )

    with metric3:
        st.metric(
            label="Nationalité dominante",
            value=leading_country,
        )

    with metric4:
        st.metric(
            label="Pilotes de cette nationalité",
            value=leading_value,
        )

    st.write("")


    # GRAPHIQUE ET RESUME


    chart_col, ranking_col = st.columns(
        [2, 1],
        gap="large",
    )

    with chart_col:
        with st.container(border=True):
            st.subheader("📊 Répartition des pilotes")

            st.caption(
                f"Top {min(top_n, len(df_chart))} des nationalités "
                "selon le nombre de pilotes."
            )

            if df_chart.empty:
                st.info(
                    "Aucune donnée ne correspond aux filtres sélectionnés."
                )
            else:
                st.bar_chart(
                    data=df_chart,
                    x="nationalite",
                    y=value_column,
                    color="#E10600",
                    horizontal=True,
                    sort=f"-{value_column}",
                    height=480,
                )

    with ranking_col:
        with st.container(border=True):
            st.subheader("🏆 Classement")

            if df_chart.empty:
                st.info("Aucun classement disponible.")
            else:
                ranking = df_chart.reset_index(drop=True).copy()
                ranking.index = ranking.index + 1

                for position, row in ranking.head(5).iterrows():
                    if position == 1:
                        medal = "🥇"
                    elif position == 2:
                        medal = "🥈"
                    elif position == 3:
                        medal = "🥉"
                    else:
                        medal = "🏁"

                    st.markdown(
                        f"""
                        **{medal} {position}. {row["nationalite"]}**  
                        {int(row[value_column])} pilote(s)
                        """
                    )

                    if position < min(5, len(ranking)):
                        st.divider()


    # TABLEAU


    st.write("")

    with st.container(border=True):
        table_title_col, download_col = st.columns(
            [4, 1],
            vertical_alignment="center",
        )

        with table_title_col:
            st.subheader("📋 Données détaillées")
            st.caption(
                f"{len(df_filtered)} ligne(s) affichée(s)."
            )

        with download_col:
            csv_data = df_filtered.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="⬇️ Télécharger CSV",
                data=csv_data,
                file_name="f1_pilotes_par_nationalite.csv",
                mime="text/csv",
            )

        column_configuration = {
            "nationalite": st.column_config.TextColumn(
                "Nationalité",
                help="Nationalité des pilotes",
                width="large",
            ),
            value_column: st.column_config.NumberColumn(
                format_column_name(value_column),
                help="Nombre de pilotes",
                format="%d",
            ),
        }

        st.dataframe(
            df_filtered.sort_values(
                value_column,
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
            column_config=column_configuration,
            height=450,
        )


    # INFORMATIONS TECHNIQUES


    with st.expander("ℹ️ Informations sur les données"):
        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.write("**Nombre de lignes**")
            st.write(len(df_data))

        with info_col2:
            st.write("**Nombre de colonnes**")
            st.write(len(df_data.columns))

        with info_col3:
            st.write("**Colonne analysée**")
            st.code(value_column)

        st.write("**Colonnes disponibles :**")
        st.write(", ".join(df_data.columns))

    st.markdown(
        """
        <div class="footer">
            Dashboard F1 • Données Azure Gold • Réalisé avec Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception as error:
    st.error("Impossible de charger les données depuis Azure.")

    with st.expander("Afficher le détail de l'erreur"):
        st.exception(error)

    st.info(
        """
        Vérifiez les éléments suivants :

        1. la variable `AZURE_STORAGE_CONNECTION_STRING` est définie ;
        2. le conteneur `gold` est accessible ;
        3. le fichier Parquet existe au chemin attendu ;
        4. les dépendances Azure nécessaires sont installées.
        """
    )
