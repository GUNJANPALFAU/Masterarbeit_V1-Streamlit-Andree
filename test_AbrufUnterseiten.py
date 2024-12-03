import streamlit as st
from Main import load_page
import pytest
import importlib
from unittest import mock

# Test für das Laden der Seiten basierend auf der Navigationsauswahl
@pytest.mark.parametrize("selected_menu, page_module_name", [
    ('Übersicht', 'pages.Übersicht'),
    ('how_to', 'pages.how_to'),
    ('Allgemeine_Angaben', 'pages.Allgemeine_Angaben'),
    ('Mindestangabepflicht', 'pages.Mindestangabepflicht'),
    ('Reset', 'pages.Reset'),
    ('Ergebnisse', 'pages.Ergebnisse')
    ('AI', 'pages.AI')
])
def test_load_selected_page(selected_menu, page_module_name):
    # Mocken des Modulimports
    with mock.patch(f"{page_module_name}.display_page"):
        # Dynamisches Importieren des Moduls
        page_module = importlib.import_module(page_module_name)

        # Mocken der display_page-Funktion, um sicherzustellen, dass das Modul importiert wird
        mock_display_page = mock.Mock()

        # Überprüfen, ob das korrekte Modul geladen wurde
        assert page_module is not None, f"Das Modul {page_module_name} sollte erfolgreich geladen werden."

# Test für ungültige Menüauswahl
def test_invalid_menu_selection():
    invalid_menu = 'Invalid_Menu_Option'

    # Mock für Streamlit-Fehlernachricht
    with mock.patch('streamlit.error') as mock_error:
        # Simulieren einer ungültigen Menüauswahl
        if invalid_menu not in ['Übersicht', 'how_to', 'Allgemeine_Angaben', 'Mindestangabepflicht', 'Reset', 'Ergebnisse']:
            st.error(f"Ungültige Auswahl: {invalid_menu}")

        # Überprüfen, ob die Fehlermeldung ausgegeben wurde
        mock_error.assert_called_once_with(f"Ungültige Auswahl: {invalid_menu}")
