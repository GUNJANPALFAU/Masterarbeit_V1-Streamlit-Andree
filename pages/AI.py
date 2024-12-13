import pandas as pd
import pickle
import os
import streamlit as st
from io import BytesIO
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
    headers = {}

    # Process and extract table rows
    for table in result.tables:
        for cell in table.cells:
            if cell.row_index == 0:  # First row as header
                headers[cell.column_index] = cell.content.lower().strip()
            if cell.row_index not in rows:
                rows[cell.row_index] = {}
            rows[cell.row_index][cell.column_index] = cell.content

    # Dynamically map columns to "Quantity", "Description", "Amount"
    column_map = {
        "quantity": None,
        "description": None,
        "amount": None
    }

    for col_index, header in headers.items():
        if "quantity" in header:
            column_map["quantity"] = col_index
        elif "description" in header:
            column_map["description"] = col_index
        elif "amount" in header or "total" in header:
            column_map["amount"] = col_index

    # Validate that required columns are identified
    if not all(column_map.values()):
        raise ValueError("Unable to map required columns from the invoice table headers.")

    # Prepare data for display
    invoice_data = []
    for row_index, row in rows.items():
        if row_index == 0:  # Skip header row
            continue

        # Extract values based on dynamic column mapping
        quantity = row.get(column_map["quantity"], "").strip()
        description = row.get(column_map["description"], "").strip()
        amount = row.get(column_map["amount"], "").strip()

        # Skip irrelevant rows (subtotal, sales tax, etc.)
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
    
    # File upload widget (allow multiple files)
    uploaded_files = st.file_uploader("Upload invoice PDFs", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        # Initialize an empty list to store the results for all files
        all_invoice_data = []

        # Process each uploaded file
        for uploaded_file in uploaded_files:
            # Analyze the uploaded document (use your custom logic here)
            invoice_data = analyze_invoice(uploaded_file)
            
            # Add extracted data to the results list
            if invoice_data:
                all_invoice_data.extend(invoice_data)
            else:
                st.write(f"No relevant data found in {uploaded_file.name}.")

        # Display extracted data for all files
        if all_invoice_data:
            st.subheader("Extracted Data from All Invoices")
            invoice_df = pd.DataFrame(all_invoice_data)
            st.dataframe(invoice_df)  # Display the combined invoice data in a table
        else:
            st.write("No relevant invoice data found in the uploaded files.")
    
    else:
        st.write("Please upload one or more PDF invoice files for analysis.")
    
    # Example of saving session state after analyzing
    session_state = load_session_state()
    session_state['last_uploaded_files'] = [file.name for file in uploaded_files] if uploaded_files else None
    save_session_state(session_state)

# You would also need these helper functions to manage session state:
def load_session_state():
    """Load session state"""
    if 'session_state' not in st.session_state:
        st.session_state['session_state'] = {}
    return st.session_state['session_state']

def save_session_state(session_state):
    """Save session state"""
    st.session_state['session_state'] = session_state
