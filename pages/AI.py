import os
import shutil
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import streamlit as st

# Set Tesseract executable path dynamically
import platform
if platform.system() == "Linux":
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
else:
    pytesseract.pytesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_file(file_path, file_ext):
    """Extract text from a single file (image or PDF)."""
    text_data = []
    try:
        if file_ext.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            text_data.append({"Page": 1, "Text": text})
        elif file_ext.lower() == '.pdf':
            images = convert_from_path(file_path)
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                text_data.append({"Page": i + 1, "Text": page_text})
    except Exception as e:
        st.error(f"Failed to process file {file_path}: {e}")
    return text_data

def display_page():
    """Streamlit page for text extraction."""
    st.title("Text Extraction Tool")
    st.write("Upload images or PDFs to extract text using OCR.")

    uploaded_files = st.file_uploader(
        "Upload files (PDFs or images)", 
        type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        os.makedirs("temp", exist_ok=True)
        all_text_data = []

        for uploaded_file in uploaded_files:
            st.write(f"Processing file: {uploaded_file.name}")

            # Save uploaded file to a temporary location
            temp_file_path = os.path.join("temp", uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.read())

            # Extract text from the file
            file_name, file_ext = os.path.splitext(uploaded_file.name)
            text_data = extract_text_from_file(temp_file_path, file_ext)

            if text_data:
                all_text_data.extend([{"File": uploaded_file.name, "Page": t["Page"], "Text": t["Text"]} for t in text_data])
            else:
                st.warning(f"No text extracted from file: {uploaded_file.name}")

        # Display extracted text in a table format if any data is found
        if all_text_data:
            st.subheader("Extracted Text Data")
            text_df = pd.DataFrame(all_text_data)
            st.dataframe(text_df)

        # Clean up the temporary directory
        shutil.rmtree("temp", ignore_errors=True)
    else:
        st.info("Please upload files to start processing.")

if __name__ == "__main__":
    display_page()
