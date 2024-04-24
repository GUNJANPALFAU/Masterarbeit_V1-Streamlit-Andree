import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def stakeholder_punkte():
    """ Diese Funktion zeigt die ausgewählten Daten in einem AgGrid an. """
    if 'stakeholder_punkte_df' in st.session_state:
        gb = GridOptionsBuilder.from_dataframe(st.session_state.stakeholder_punkte_df)
        gb.configure_pagination(paginationAutoPageSize=True, paginationPageSize=10)
        gb.configure_side_bar()
        grid_options = gb.build()
        AgGrid(st.session_state.stakeholder_punkte_df, gridOptions=grid_options, enable_enterprise_modules=True, update_mode=GridUpdateMode.MODEL_CHANGED)
    else:
        st.write("Keine Daten ausgewählt oder Button 'Hallo' wurde noch nicht gedrückt.")

def excel_upload():
    """ Diese Funktion lädt Excel-Dateien hoch und erstellt Rankings basierend auf den Bewertungen. """
    def get_numerical_rating(value):
        ratings = {
            'Wesentlich': 3,
            'Eher Wesentlich': 2,
            'Eher nicht Wesentlich': 1,
            'Nicht Wesentlich': 0
        }
        return ratings.get(value, 0)

    def aggregate_rankings(df):
        """ Erzeugt eine aggregierte Rangliste basierend auf den Bewertungen. """
        df['NumericalRating'] = df['Bewertung'].apply(get_numerical_rating)
        df.fillna({'Thema': 'Unbekannt', 'Unterthema': 'Unbekannt', 'Unter-Unterthema': '-'}, inplace=True)
        ranking = df.groupby(['Thema', 'Unterthema', 'Unter-Unterthema']).agg({'NumericalRating': 'sum'}).reset_index()
        ranking.sort_values(by='NumericalRating', ascending=False, inplace=True)
        ranking['Platzierung'] = ranking['NumericalRating'].rank(method='min', ascending=False).astype(int)
        return ranking[['Platzierung', 'Thema', 'Unterthema', 'Unter-Unterthema', 'NumericalRating']]

    uploaded_files = st.file_uploader("Excel-Dateien hochladen", accept_multiple_files=True, type=['xlsx'])
    if uploaded_files:
        df_list = [pd.read_excel(file, engine='openpyxl') for file in uploaded_files if file]
        combined_df = pd.concat(df_list)
        st.session_state.ranking_df = aggregate_rankings(combined_df)
        st.write("Aktuelles Ranking basierend auf hochgeladenen Dateien:")
        gb = GridOptionsBuilder.from_dataframe(st.session_state.ranking_df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        gb.configure_side_bar()
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children", rowMultiSelectWithClick=True)
        grid_options = gb.build()
        response = AgGrid(st.session_state.ranking_df, gridOptions=grid_options, enable_enterprise_modules=True, update_mode=GridUpdateMode.MODEL_CHANGED)
        st.session_state.grid_response = response

    if st.button('Hallo'):
        if 'grid_response' in st.session_state and 'selected_rows' in st.session_state.grid_response:
            selected_rows = st.session_state.grid_response['selected_rows']
            if selected_rows:  # Sicherstellen, dass Zeilen ausgewählt wurden
                selected_df = pd.DataFrame(selected_rows)
                st.session_state.stakeholder_punkte_df = selected_df
            else:
                st.error("Bitte wählen Sie mindestens eine Zeile aus.")
     
tab1, tab2 = st.tabs(["Stakeholder Nachhaltigkeitspunkte", "Excel-Upload"])
with tab1:
    stakeholder_punkte()
with tab2:
    excel_upload()