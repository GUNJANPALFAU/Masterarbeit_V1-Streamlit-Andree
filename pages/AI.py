import streamlit as st
import pytesseract
import platform
from PIL import Image
from pdf2image import convert_from_path
# Dynamically set Tesseract path for Streamlit Cloud
if platform.system() == "Linux":
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

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
