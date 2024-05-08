import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from pages.Bottom_up_stakeholder import stakeholder_punkte

def stakeholder_Nachhaltigkeitspunkte():
    # Zugriff auf den DataFrame aus Bottom_up_stakeholder.py über session_state
    if 'stakeholder_punkte_df' not in st.session_state:
        st.session_state.stakeholder_punkte_df = pd.DataFrame(columns=["Platzierung", "Thema", "Unterthema", "Unter-Unterthema", "NumericalRating"])
    df3 = st.session_state.stakeholder_punkte_df.copy()
    df3['Quelle'] = 'Stakeholder'

    # Berechnen Sie die Größe der Klassen
    class_size = (df3['NumericalRating'].max() - df3['NumericalRating'].min()) / 4

    # Fügen Sie einen Schieberegler in der Seitenleiste hinzu
    options = ['Nicht Wesentlich', 'Eher nicht wesentlich', 'Eher Wesentlich', 'Wesentlich']
    st.sidebar.markdown("---")
    st.sidebar.text("Grenzwert für die Auswahl der Stakeholderpunkte:")
    selection = st.sidebar.select_slider('', options=options)
    
    st.markdown("""
        <style>
        .st-emotion-cache-183lzff,
        .st-emotion-cache-1inwz65 {
            font-family: "Source Sans Pro", sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Berechnen Sie die Anzahl der ausgewählten Zeilen basierend auf der Auswahl
    if selection == 'Wesentlich':
        selected_rows = df3[df3['NumericalRating'] > 3 * class_size + df3['NumericalRating'].min()]
    elif selection == 'Eher Wesentlich':
        selected_rows = df3[df3['NumericalRating'] > 2 * class_size + df3['NumericalRating'].min()]
    elif selection == 'Eher nicht wesentlich':
        selected_rows = df3[df3['NumericalRating'] > class_size + df3['NumericalRating'].min()]
    else:  # Nicht Wesentlich
        selected_rows = df3[df3['NumericalRating'] > 0]

    # Speichern Sie die ausgewählten Zeilen im session_state
    st.session_state.selected_rows = selected_rows

    return selected_rows

def eigene_Nachhaltigkeitspunkte():
    # Zugriff auf den DataFrame aus Eigene.py über session_state
    if 'df2' not in st.session_state:
        st.session_state.df2 = pd.DataFrame(columns=["Thema", "Unterthema", "Unter-Unterthema"])
    # Erstellen Sie eine Kopie von df2
    df4 = st.session_state.df2.copy()
    df4['Quelle'] = 'Eigene'
    return df4

def Top_down_Nachhaltigkeitspunkte():
    # Initialize a list to store topic details
    essential_topics_data = []
    # Anpassung der Inahlte für die Tabelle aus der Top_down.py, für Inhalte nur mit Thema und Unterthema
    for topic, values in st.session_state.items():
        if isinstance(values, dict):
            if values.get('Wesentlich', False) or values.get('Eher Wesentlich', False):
                # Assuming topic names are stored in the format "Thema - Unterthema - Unter-Unterthema"
                topic_details = topic.split(' - ')
                while len(topic_details) < 3:
                    topic_details.append('')
                # Check if the topic starts with "climate_change", "pollution_" or "water_usage_" and change the theme and subtheme accordingly
                if topic_details[0].startswith('climate_change'):
                    topic_details = ['Klimawandel', topic_details[0].replace('climate_change', '').strip().replace('_', ' '), topic_details[1]]
                elif topic_details[0].startswith('pollution_'):
                    topic_details = ['Umweltverschmutzung', topic_details[0].replace('pollution_', '').strip().replace('_', ' '), topic_details[1]]
                elif topic_details[0].startswith('water_usage_'):
                    topic_details = ['Wasser- & Meeresressourcen', topic_details[0].replace('water_usage_', '').strip().replace('_', ' '), topic_details[1]]
                elif topic_details[0].startswith('kreislaufwirtschaft'):
                    topic_details = ['Kreislaufwirtschaft', topic_details[0].replace('kreislaufwirtschaft', '').strip().replace('_', ' '), topic_details[1]]
                elif topic_details[0].startswith('unternehmenspolitik'):
                    topic_details = ['Unternehmenspolitik', topic_details[0].replace('unternehmenspolitik', '').strip().replace('_', ' '), topic_details[1]]
                elif topic_details[0].startswith('biodiversity_'):
                    if topic_details[0] in ['biodiversity_Populationsgröße von Arten', 'biodiversity_Globales Ausrottungsrisiko von Arten']:
                        topic_details = ['Biodiversität', 'Auswirkungen auf den Zustand der Arten', topic_details[0].replace('biodiversity_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['biodiversity_Landdegradation', 'biodiversity_Wüstenbildung', 'biodiversity_Bodenversiegelung']:
                        topic_details = ['Biodiversität', 'Auswirkungen auf den Umfang und den Zustand von Ökosystemen', topic_details[0].replace('biodiversity_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['biodiversity_Auswirkungen und Abhängigkeiten von Ökosystemdienstleistungen']:
                        topic_details = ['Biodiversität','Auswirkungen und Abhängigkeiten von Ökosystemdienstleistungen', topic_details[0].replace('biodiversity_', '').strip().replace('_', ' ')]
                    else:
                        topic_details = ['Biodiversität', 'Direkte Ursachen des Biodiversitätsverlusts', topic_details[0].replace('biodiversity_', '').strip().replace('_', ' ')]
                elif topic_details[0].startswith('eigene_belegschaft_'):
                    if topic_details[0] in ['eigene_belegschaft_Sichere Beschäftigung', 'eigene_belegschaft_Arbeitszeit', 'eigene_belegschaft_Angemessene Entlohnung', 'eigene_belegschaft_Sozialer Dialog', 'eigene_belegschaft_Vereinigungsfreiheit, Existenz von Betriebsräten und Rechte der Arbeitnehmer auf Information, Anhörung und Mitbestimmung', 'eigene_belegschaft_Tarifverhandlungen, einschließlich der Quote der durch Tarifverträge abgedeckten Arbeitskräften', 'eigene_belegschaft_Vereinbarkeit von Berufs- und Privatleben', 'eigene_belegschaft_Gesundheitsschutz und Sicherheit']:
                        topic_details = ['Eigene Belegschaft','Arbeitsbedingungen', topic_details[0].replace('eigene_belegschaft_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['eigene_belegschaft_Gleichstellung der Geschlechter und gleicher Lohn für gleiche Arbeit', 'eigene_belegschaft_Schulungen und Kompetenzentwicklung', 'eigene_belegschaft_Beschäftigung und Inklusion von Menschen mit Behinderungen', 'eigene_belegschaft_Maßnahmen gegen Gewalt und Belästigung am Arbeitsplatz','eigene_belegschaft_Vielfalt']:
                        topic_details = ['Eigene Belegschaft','Gleichbehandlung und Chancengleichheit', topic_details[0].replace('eigene_belegschaft_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['eigene_belegschaft_Kinderarbeit', 'eigene_belegschaft_Zwangsarbeit', 'eigene_belegschaft_Angemessene Unterbringung', 'eigene_belegschaft_Datenschutz']:
                        topic_details = ['Eigene Belegschaft','Sonstige arbeitsbezogene Rechte', topic_details[0].replace('eigene_belegschaft_', '').strip().replace('_', ' ')]
                elif topic_details[0].startswith('wertschöpfungskette_belegschaft_'):
                    if topic_details[0] in ['wertschöpfungskette_belegschaft_Sichere Beschäftigung', 'wertschöpfungskette_belegschaft_Arbeitszeit', 'wertschöpfungskette_belegschaft_Angemessene Entlohnung', 'wertschöpfungskette_belegschaft_Sozialer Dialog', 'wertschöpfungskette_belegschaft_Vereinigungsfreiheit, Existenz von Betriebsräten und Rechte der Arbeitnehmer auf Information, Anhörung und Mitbestimmung', 'wertschöpfungskette_belegschaft_Tarifverhandlungen, einschließlich der Quote der durch Tarifverträge abgedeckten Arbeitskräften', 'wertschöpfungskette_belegschaft_Vereinbarkeit von Berufs- und Privatleben', 'wertschöpfungskette_belegschaft_Gesundheitsschutz und Sicherheit']:
                        topic_details = ['Arbeitskräfte in der Wertschöpfungskette','Arbeitsbedingungen', topic_details[0].replace('wertschöpfungskette_belegschaft_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['wertschöpfungskette_belegschaft_Gleichstellung der Geschlechter und gleicher Lohn für gleiche Arbeit', 'wertschöpfungskette_belegschaft_Schulungen und Kompetenzentwicklung', 'wertschöpfungskette_belegschaft_Beschäftigung und Inklusion von Menschen mit Behinderungen', 'wertschöpfungskette_belegschaft_Maßnahmen gegen Gewalt und Belästigung am Arbeitsplatz','wertschöpfungskette_belegschaft_Vielfalt']:
                        topic_details = ['Arbeitskräfte in der Wertschöpfungskette','Gleichbehandlung und Chancengleichheit', topic_details[0].replace('wertschöpfungskette_belegschaft_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['wertschöpfungskette_belegschaft_Kinderarbeit', 'wertschöpfungskette_belegschaft_Zwangsarbeit', 'wertschöpfungskette_belegschaft_Angemessene Unterbringung', 'wertschöpfungskette_belegschaft_Datenschutz']:
                        topic_details = ['Arbeitskräfte in der Wertschöpfungskette','Sonstige arbeitsbezogene Rechte', topic_details[0].replace('wertschöpfungskette_belegschaft_', '').strip().replace('_', ' ')] 
                elif topic_details[0].startswith('betroffene_gemeinschaften_'):
                    if topic_details[0] in ['betroffene_gemeinschaften_Angemessene Unterbringung', 'betroffene_gemeinschaften_Angemessene Ernährung', 'betroffene_gemeinschaften_Wasser- und Sanitäreinrichtungen', 'betroffene_gemeinschaften_Bodenbezogene Auswirkungen', 'betroffene_gemeinschaften_Sicherheitsbezogene Auswirkungen']:
                        topic_details = ['Betroffene Gemeinschaften','Wirtschaftliche, soziale und kulturelle Rechte von Gemeinschaften', topic_details[0].replace('betroffene_gemeinschaften_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['betroffene_gemeinschaften_Meinungsfreiheit', 'betroffene_gemeinschaften_Versammlungsfreiheit', 'betroffene_gemeinschaften_Auswirkungen auf Menschenrechtsverteidiger']:
                        topic_details = ['Betroffene Gemeinschaften','Bürgerrechte und politische Rechte von Gemeinschaften', topic_details[0].replace('betroffene_gemeinschaften_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['betroffene_gemeinschaften_Freiwillige und in Kenntnis der Sachlage erteilte vorherige Zustimmung', 'betroffene_gemeinschaften_Selbstbestimmung', 'betroffene_gemeinschaften_Kulturelle Rechte' ]:
                        topic_details = ['Betroffene Gemeinschaften','Rechte indigener Völker', topic_details[0].replace('betroffene_gemeinschaften_', '').strip().replace('_', ' ')] 
                elif topic_details[0].startswith('verbraucher_endnutzer_'):
                    if topic_details[0] in ['verbraucher_endnutzer_Datenschutz', 'verbraucher_endnutzer_Meinungsfreiheit', 'verbraucher_endnutzer_Faire Geschäftspraktiken', 'verbraucher_endnutzer_Zugang zu (hochwertigen) Informationen']:
                        topic_details = ['Verbraucher und Endnutzer','Informationsbezogene Auswirkungen für Verbraucher und/oder Endnutzer', topic_details[0].replace('verbraucher_endnutzer_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['verbraucher_endnutzer_Gesundheitsschutz und Sicherheit', 'verbraucher_endnutzer_Persönliche Sicherheit', 'verbraucher_endnutzer_Kinderschutz']:
                        topic_details = ['Verbraucher und Endnutzer','Persönliche Sicherheit von Verbrauchern und/oder Endnutzern', topic_details[0].replace('verbraucher_endnutzer_', '').strip().replace('_', ' ')]
                    elif topic_details[0] in ['verbraucher_endnutzer_Nichtdiskriminierung', 'verbraucher_endnutzer_Zugang zu Produkten und Dienstleistungen', 'verbraucher_endnutzer_Verantwortliche Vermarktungspraktiken' ]:
                        topic_details = ['Verbraucher und Endnutzer','Soziale Inklusion von Verbrauchern und/oder Endnutzern', topic_details[0].replace('verbraucher_endnutzer_', '').strip().replace('_', ' ')] 
                
                # Append to the list with importance level
                essential_topics_data.append(topic_details + ['Wesentlich' if values.get('Wesentlich', False) else 'Eher Wesentlich'])


    # Create a DataFrame from the collected data
    df_essential = pd.DataFrame(essential_topics_data, columns=['Thema', 'Unterthema', 'Unter-Unterthema', 'Wichtigkeit'])
    df_essential['Quelle'] = 'Top-down'
    return df_essential

def merge_dataframes():
    df4 = eigene_Nachhaltigkeitspunkte()
    df_essential = Top_down_Nachhaltigkeitspunkte()
    selected_rows = stakeholder_Nachhaltigkeitspunkte()
    
    combined_df = pd.concat([df_essential, df4, selected_rows], ignore_index=True)
    combined_df = combined_df.dropna(how='all')  # Entfernen von Zeilen, die in allen Spalten NaNs enthalten

    # Clean data
    combined_df['Thema'] = combined_df['Thema'].str.strip()
    combined_df['Unterthema'] = combined_df['Unterthema'].str.strip()
    combined_df['Unter-Unterthema'] = combined_df['Unter-Unterthema'].str.strip()

    # Entfernen von Zeilen, in denen 'Thema' leer ist
    combined_df = combined_df.dropna(subset=['Thema'])
    
    # Group by columns and merge sources intelligently to reflect all combinations
    combined_df = combined_df.groupby(['Thema', 'Unterthema', 'Unter-Unterthema']).agg({
        'Quelle': lambda x: ' & '.join(sorted(set(x)))  # Merge and sort unique sources
    }).reset_index()

    combined_df = combined_df.drop_duplicates(subset=['Thema', 'Unterthema', 'Unter-Unterthema']).sort_values(by=['Thema', 'Unterthema', 'Unter-Unterthema'])

    # Initialisieren Sie combined_df im st.session_state
    st.session_state.combined_df = combined_df

    # Erstellen Sie die Grid-Optionen
    gb = GridOptionsBuilder.from_dataframe(combined_df)
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children", rowMultiSelectWithClick=True)
    gridOptions = gb.build()
    AgGrid(combined_df, gridOptions=gridOptions, enable_enterprise_modules=True, update_mode=GridUpdateMode.MODEL_CHANGED, fill_screen=True)

    # Add a selectbox to the sidebar
    option = st.sidebar.selectbox(
    'Bitte wählen Sie aus:',
    ('Wesentlichkeit der Auswirkung', 'Finanzielle Wesentlichkeit', 'Beide Dimensionen'),
    
)
    # If 'Wesentlichkeit der Auswirkung' is selected, show another selectbox
    if option == 'Wesentlichkeit der Auswirkung':
        auswirkung_option = st.sidebar.selectbox(
            'Bitte wählen Sie die Eigenschaft der Auswirkung:',
            ('Positive Auswirkung', 'Negative Auswirkung', ''),
            index=2
        )
    
        # If 'Negative Auswirkung' is selected, show another selectbox
        if auswirkung_option == 'Negative Auswirkung':
            auswirkung_art_option = st.sidebar.selectbox(
                'Bitte wählen Sie die Art der Auswirkung:',
                ('Tatsächliche Auswirkung', 'Potenzielle Auswirkung', ''),
                index=2
        )
    
            # If 'Tatsächliche Auswirkung' is selected, show sliders in the sidebar
            if auswirkung_art_option == 'Tatsächliche Auswirkung':
                ausmass_neg_tat = st.sidebar.select_slider(
                    "Ausmaß:",
                    options=["Keines", "Minimal", "Niedrig", "Medium", "Hoch", "Sehr hoch"],
                    key="ausmass_negativ_tat_auswirkung"
                )
    
                umfang_neg_tat = st.sidebar.select_slider(
                    "Umfang:",
                    options=["Keine", "Lokal", "Regional", "National", "International", "Global"],
                    key="umfang_negativ_tat_auswirkung"
                )
    
                behebbarkeit_neg_tat = st.sidebar.select_slider(
                    "Behebbarkeit:",
                    options=["Kein Aufwand", "Leicht zu beheben", "Mit Aufwand", "Mit hohem Aufwand", "Mit sehr hohem Aufwand", "Nicht behebbar"],
                    key="behebbarkeit_negativ_tat_auswirkung"
                )
    
            # If 'Potenzielle Auswirkung' is selected, show sliders in the sidebar
            elif auswirkung_art_option == 'Potenzielle Auswirkung':
                ausmass_neg_pot = st.sidebar.select_slider(
                    "Ausmaß:",
                    options=["Keines", "Minimal", "Niedrig", "Medium", "Hoch", "Sehr hoch"],
                    key="ausmass_negativ_pot_auswirkung"
                )
    
                umfang_neg_pot = st.sidebar.select_slider(
                    "Umfang:",
                    options=["Keine", "Lokal", "Regional", "National", "International", "Global"],
                    key="umfang_negativ_pot_auswirkung"
                )
    
                behebbarkeit_neg_pot = st.sidebar.select_slider(
                    "Behebbarkeit:",
                    options=["Kein Aufwand", "Leicht zu beheben", "Mit Aufwand", "Mit hohem Aufwand", "Mit sehr hohem Aufwand", "Nicht behebbar"],
                    key="behebbarkeit_negativ_pot_auswirkung"
                )
    
                wahrscheinlichkeit_neg_pot = st.sidebar.select_slider(
                    "Wahrscheinlich:",
                    options=["Tritt nicht ein", "Unwahrscheinlich", "Eher unwahrscheinlich", "Eher wahrscheinlich", "Wahrscheinlich", "Sicher"],
                    key="wahrscheinlichkeit_negativ_pot_auswirkung"
                )
    
        if auswirkung_option == 'Positive Auswirkung':
            auswirkung_positiv_art_option = st.sidebar.selectbox(
                'Bitte wählen Sie die Art der Auswirkung:',
                ('Tatsächliche Auswirkung', 'Potenzielle Auswirkung', ''),
                index=2
            )
    
            # If 'Tatsächliche Auswirkung' is selected, show sliders in the sidebar
            if auswirkung_positiv_art_option == 'Tatsächliche Auswirkung':
                ausmass_pos_tat = st.sidebar.select_slider(
                    "Ausmaß:",
                    options=["Keines", "Minimal", "Niedrig", "Medium", "Hoch", "Sehr hoch"],
                    key="ausmass_positiv_tat_auswirkung"
                )
    
                umfang_pos_tat = st.sidebar.select_slider(
                    "Umfang:",
                    options=["Keine", "Lokal", "Regional", "National", "International", "Global"],
                    key="umfang_positiv_tat_auswirkung"
                )
    
            # If 'Potenzielle Auswirkung' is selected, show sliders in the sidebar
            elif auswirkung_positiv_art_option == 'Potenzielle Auswirkung':
                ausmass_pos_pot = st.sidebar.select_slider(
                    "Ausmaß:",
                    options=["Keines", "Minimal", "Niedrig", "Medium", "Hoch", "Sehr hoch"],
                    key="ausmass_positiv_pot_auswirkung"
                )
    
                umfang_pos_pot = st.sidebar.select_slider(
                    "Umfang:",
                    options=["Keine", "Lokal", "Regional", "National", "International", "Global"],
                    key="umfang_positiv_pot_auswirkung"
                )
    
                behebbarkeit_pos_pot = st.sidebar.select_slider(
                    "Behebbarkeit:",
                    options=["Kein Aufwand", "Leicht zu beheben", "Mit Aufwand", "Mit hohem Aufwand", "Mit sehr hohem Aufwand", "Nicht behebbar"],
                    key="behebbarkeit_positiv_pot_auswirkung"
                )

tab1, tab2, tab3 = st.tabs(["Eigene Nachhaltigkeitspunkte", "Stakeholder", "Gesamtübersicht"])
with tab1: 
    merge_dataframes()
with tab2:
    stakeholder_punkte()
with tab3:
    st.write("Gesamtübersicht")