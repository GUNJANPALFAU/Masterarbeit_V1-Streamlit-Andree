import pandas as pd
import pickle
import os
import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Azure Form Recognizer endpoint and API key
endpoint = "https://sustainability-fau.cognitiveservices.azure.com/"
key = "DNjmy8Ljo0XverRQ9e1a9vu104RcZ5mAegO0B3jwN7PxFKY6mkblJQQJ99AKACPV0roXJ3w3AAALACOGE42s"

# Initialize the client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

SESSION_STATE_PATH = "session_state.pkl"

def load_session_state():
    """Load session state from a Pickle file."""
    try:
        with open(SESSION_STATE_PATH, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def save_session_state(state):
    """Save session state to a Pickle file."""
    with open(SESSION_STATE_PATH, "wb") as f:
        pickle.dump(state, f)

def analyze_invoice(document): 
    """Analyze the invoice document and extract relevant information"""
    poller = client.begin_analyze_document("prebuilt-invoice", document)
    result = poller.result()

    rows = {}
    # Process and extract table rows
    for table in result.tables:
        for cell in table.cells:
            if cell.row_index not in rows:
                rows[cell.row_index] = {}
            rows[cell.row_index][cell.column_index] = cell.content

    # Prepare data for display
    invoice_data = []
    for row_index, row in rows.items():
        # Extract relevant columns for quantity, description, and amount
        quantity = row.get(0, "").strip()  # Column 0 for quantity
        description = row.get(1, "").strip()  # Column 1 for description
        amount = row.get(3, "").strip()  # Column 3 for total amount

        # Skip header row
        if row_index == 0:  
            continue

        # Skip irrelevant rows (subtotal, sales tax, shipping & handling, total due)
        if description.lower() in ["subtotal", "sales tax", "shipping & handling", "total due"]:
            continue

        # Ensure 'amount' is a valid number before adding to data
        if amount:  # Check if amount is not empty or None
            try:
                amount = float(amount.replace(",", "").replace("$", ""))  # Clean and convert amount to float
            except ValueError:
                amount = None  # If invalid, set as None
        else:
            amount = None  # If amount is empty or None, set as None

        # Filter out rows where all fields are empty
        if description or quantity or amount:
            invoice_data.append({"Description": description, "Quantity": quantity, "Amount": amount})

    return invoice_data

def display_page():
    """Streamlit page for invoice extraction"""
    st.title("Data extraction")
    st.write("Information from the invoice/bills.")
    
    # File upload widget
    uploaded_file = st.file_uploader("Upload an invoice PDF", type=["pdf"])

    if uploaded_file:
        # Analyze the uploaded document
        invoice_data = analyze_invoice(uploaded_file)
        
        # Display extracted data in a table format
        if invoice_data:
            st.subheader("Extracted Data")
            invoice_df = pd.DataFrame(invoice_data)
            st.dataframe(invoice_df)  # Display the invoice data in a table
        else:
            st.write("No relevant invoice data found.")
    else:
        st.write("Please upload a PDF invoice file for analysis.")

    # Example of saving session state after analyzing
    session_state = load_session_state()
    session_state['last_uploaded_file'] = uploaded_file.name if uploaded_file else None
    save_session_state(session_state)
