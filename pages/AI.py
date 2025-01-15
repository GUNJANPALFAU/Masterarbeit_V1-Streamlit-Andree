import pandas as pd
import pickle
import os
import streamlit as st


def display_page():
    """Streamlit page for invoice extraction"""
    st.title("Data Extraction")
    st.write("Information from the invoices/bills.")
    st.write(f"Streamlit version: {st.__version__}")
    # File upload widget for multiple files
    uploaded_files = st.file_uploader("Upload invoice PDFs", type=["pdf"], accept_multiple_files=True)
    st.write(f"Streamlit version: {st.__version__}")
    if uploaded_files:
        # Ensure `uploaded_files` is a list
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]

        all_invoice_data = []

        for uploaded_file in uploaded_files:
            st.write(f"Processing file: {uploaded_file.name}")
            # Analyze each uploaded document
            invoice_data = analyze_invoice(uploaded_file)

            if invoice_data:
                # Add extracted data to the list
                all_invoice_data.extend(invoice_data)
            else:
                st.write(f"No relevant data found in file: {uploaded_file.name}")

        # Display extracted data in a table format if any data is found
        if all_invoice_data:
            st.subheader("Extracted Data")
            invoice_df = pd.DataFrame(all_invoice_data)
            st.dataframe(invoice_df)  # Display the invoice data in a table
        else:
            st.write("No relevant invoice data found in the uploaded files.")
    else:
        st.write("Please upload PDF invoice files for analysis.")
    # Example of saving session state after analyzing
    session_state = load_session_state()
    session_state['last_uploaded_files'] = [file.name for file in uploaded_files] if uploaded_files else None
    save_session_state(session_state)
