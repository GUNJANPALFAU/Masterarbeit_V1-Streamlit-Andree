import os
import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Azure Form Recognizer endpoint and API key
endpoint = "https://sustainability-fau.cognitiveservices.azure.com/"
key = "DNjmy8Ljo0XverRQ9e1a9vu104RcZ5mAegO0B3jwN7PxFKY6mkblJQQJ99AKACPV0roXJ3w3AAALACOGE42s"

# Initialize the client
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

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
        quantity = row.get(0, "")  # Column 0 for quantity
        description = row.get(1, "")  # Column 1 for description
        amount = row.get(3, "")  # Column 3 for total amount

        if row_index == 0:  # Skip header row
            continue

        # Skip subtotal, sales tax, etc.
        if description.lower() in ["subtotal", "sales tax", "shipping & handling", "total due"]:
            continue

        # Filter out rows where all fields are empty
        if description or quantity or amount:
            invoice_data.append({"Description": description, "Quantity": quantity, "Amount": amount})
    
    return invoice_data

def display_page():
    """Streamlit page for invoice extraction"""
    st.title("Material Extraction - AI Page")
    st.write("This page displays the invoice extraction details.")
    
    # File upload widget
    uploaded_file = st.file_uploader("Upload an invoice PDF", type=["pdf"])
    
    if uploaded_file:
        # Analyze the uploaded document
        invoice_data = analyze_invoice(uploaded_file)

        # Display extracted data in a table format
        if invoice_data:
            st.subheader("Extracted Invoice Data")
            invoice_df = pd.DataFrame(invoice_data)
            st.dataframe(invoice_df)  # Display the invoice data in a table
        else:
            st.write("No relevant invoice data found.")

    else:
        st.write("Please upload a PDF invoice file for analysis.")



