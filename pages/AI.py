import os
import shutil
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import streamlit as st
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT


# Access the API key from secrets
api_key = st.secrets["ANTHROPIC_API_KEY"]

# Initialize the Anthropic client
client = Anthropic(api_key=api_key)

# Set Tesseract executable path
import platform
if platform.system() == "Linux":
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
else:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_file(file_path, file_ext):
    """Extract text from a single file (image or PDF)."""
    text_data = []
    if file_ext.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            text_data.append({"Page": 1, "Text": text})
        except Exception as e:
            st.error(f"Failed to process image file {file_path}: {e}")
    elif file_ext.lower() == '.pdf':
        try:
            images = convert_from_path(file_path)
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                text_data.append({"Page": i + 1, "Text": page_text})
        except Exception as e:
            st.error(f"Failed to process PDF file {file_path}: {e}")
    return text_data

def analyze_sustainability(text):
    """Send text to Claude.ai for sustainability analysis."""
    prompt = (
        f"Analyze the following text for sustainability-related data points, "
        f"such as energy consumption, carbon emissions, renewable resources, "
        f"water usage, or any other sustainability-related metrics. Provide a crisp summary:\n\n"
        f"{text}"
    )
    response = client.completions.create(
        model="claude 3.5-Haiku",
        prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
        max_tokens_to_sample=500,
        temperature=0.5
    )
    return response.completion

def display_page():
    st.title("Sustainability Analysis Tool")
    st.write("Upload images or PDFs to extract and analyze sustainability-related information.")

    uploaded_files = st.file_uploader(
        "Upload files (PDFs or images)", 
        type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        os.makedirs("temp", exist_ok=True)
        all_text_data = []
        all_analysis_results = []

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

                # Send extracted text to Claude.ai for analysis
                full_text = " ".join([t["Text"] for t in text_data])
                with st.spinner(f"Analyzing sustainability data for {uploaded_file.name}..."):
                    analysis = analyze_sustainability(full_text)
                all_analysis_results.append({"File": uploaded_file.name, "Analysis": analysis})
            else:
                st.write(f"No text extracted from file: {uploaded_file.name}")

        # Display extracted text in a table format if any data is found
        if all_text_data:
            st.subheader("Extracted Text Data")
            text_df = pd.DataFrame(all_text_data)
            st.dataframe(text_df)

        # Display sustainability analysis
        if all_analysis_results:
            st.subheader("Sustainability Analysis Results")
            for result in all_analysis_results:
                st.markdown(f"### File: {result['File']}")
                st.text_area("Analysis", result["Analysis"], height=200)

        shutil.rmtree("temp", ignore_errors=True)
    else:
        st.info("Please upload files to start processing.")

if __name__ == "__main__":
    display_page()
