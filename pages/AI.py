import pandas as pd
import pickle
import os
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

# Dynamically set Tesseract path for Streamlit Cloud
if os.name == "posix":  # For Linux/Streamlit Cloud
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
else:  # For Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to process and extract text
def process_files(uploaded_files):
    """
    Processes uploaded image or PDF files, extracts text, and returns the results.

    Args:
        uploaded_files (list): List of uploaded files from Streamlit.

    Returns:
        dict: Dictionary mapping filenames to extracted text.
    """
    results = {}

    for uploaded_file in uploaded_files:
        file_name, file_ext = os.path.splitext(uploaded_file.name)

        # Process image files
        if file_ext.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            try:
                image = Image.open(uploaded_file)
                text = pytesseract.image_to_string(image)
                results[file_name] = text
            except Exception as e:
                results[file_name] = f"Error processing image: {e}"

        # Process PDF files
        elif file_ext.lower() == '.pdf':
            try:
                images = convert_from_path(uploaded_file)
                pdf_text = ""
                for i, image in enumerate(images):
                    page_text = pytesseract.image_to_string(image)
                    pdf_text += f"--- Page {i + 1} ---\n{page_text}\n"
                results[file_name] = pdf_text
            except Exception as e:
                results[file_name] = f"Error processing PDF: {e}"

        else:
            results[file_name] = "Unsupported file format."

    return results
def display_page():
    """Streamlit page for document text extraction."""
    st.title("Document Text Extraction App")
    st.write("Upload invoices or bills (PDFs or images) to extract information.")
    
    # File upload widget
    uploaded_files = st.file_uploader(
        "Upload files (Images or PDFs)", 
        type=["png", "jpg", "jpeg", "bmp", "tiff", "pdf"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(f"{len(uploaded_files)} files uploaded. Processing...")

        # Process files and display results
        with st.spinner("Extracting text from uploaded files..."):
            extracted_texts = process_files(uploaded_files)

        st.success("Text extraction complete!")

        # Display extracted data
        for file_name, text in extracted_texts.items():
            st.subheader(f"Extracted Text: {file_name}")
            st.text_area(f"Text from {file_name}", text, height=300)

        # Option to download extracted text
        for file_name, text in extracted_texts.items():
            st.download_button(
                label=f"Download Text for {file_name}",
                data=text,
                file_name=f"{file_name}.txt",
                mime="text/plain"
            )

    else:
        st.warning("Please upload files to begin text extraction.")

