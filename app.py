import streamlit as st
import json
import re
import pandas as pd
from utils.pdf_parser import read_pdf_from_streamlit
from utils.data_extractor import extract_invoice_data, is_invoice_text
from utils.csv_helper import save_to_csv
import os

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="Invoice Data Extractor",
    page_icon="📑",
    layout="wide"
)

# ---------------- Sidebar ---------------- #
st.sidebar.title("📂 Invoice Upload")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF invoices",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- Theme Switcher ---------------- #
# ---------------- Theme Switcher ---------------- #
theme = st.sidebar.selectbox(
    "🎨 Choose Theme",
    ["Custom Blue", "Light", "Dark"],
    index=0
)

# CSS injection based on theme
if theme == "Light":
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #e5e7eb;
            color: #1f2937;
        }
        .stMarkdown, .stChatMessage, .greeting-box {
            color: #1f2937 !important;
        }
        .greeting-box {
            padding: 14px;
            border-radius: 10px;
            background-color: #dbeafe;
            font-weight: 500;
            margin-bottom: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
elif theme == "Dark":
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #0e1117;
            color: #f1f5f9;
        }
        .stMarkdown, .stChatMessage, .greeting-box {
            color: #f1f5f9 !important;
        }
        .greeting-box {
            padding: 14px;
            border-radius: 10px;
            background-color: #1e293b;
            font-weight: 500;
            margin-bottom: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
elif theme == "Custom Blue":
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #001f3f;
            color: #e0eaff;
        }
        .stMarkdown, .stChatMessage, .greeting-box {
            color: #e0eaff !important;
        }
        .greeting-box {
            padding: 14px;
            border-radius: 10px;
            background-color: #0d3b66;
            font-weight: 500;
            margin-bottom: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------- Greeting ---------------- #
st.markdown(
    """
    <div class="greeting-box">
        💬 Chat <br>
        👋 Hello Sir! Welcome to the <b>Invoice Data Extractor</b>. 
        Upload invoices from the sidebar and I’ll extract all the details for you!
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- JSON Cleaner ---------------- #
def clean_json_response(response: str):
    """
    Cleans and safely parses a JSON-like string.
    Falls back to raw dict if parsing fails.
    """
    cleaned = re.sub(r"```json|```", "", response, flags=re.IGNORECASE).strip()
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)

    try:
        return json.loads(cleaned)
    except Exception:
        return {"raw_text": response}

# ---------------- Main Processing ---------------- #
if uploaded_files:
    extracted_data_list = []
    st.markdown("### 📑 Processed Invoices")

    progress = st.progress(0)
    total_files = len(uploaded_files)

    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        st.subheader(f"📄 {uploaded_file.name}")

        pdf_text = read_pdf_from_streamlit(uploaded_file)

        # Detect invoice or not
        if not is_invoice_text(pdf_text):
            st.warning("⚠️ This file does not look like an invoice. Showing raw text instead.")
            invoice_data = {"raw_text": pdf_text[:2000] + "... (truncated)"}
        else:
            invoice_data = extract_invoice_data(pdf_text)
            invoice_data = clean_json_response(invoice_data)

        extracted_data_list.append(invoice_data)

        # -------- Show Invoice Details -------- #
        if "raw_text" in invoice_data:
            st.text_area(
                "📄 Raw Text Preview",
                invoice_data["raw_text"],
                height=200,
                key=f"raw_text_{uploaded_file.name}_{idx}"  # FIX: unique key
            )
        else:
            st.write("### Invoice Summary")

            fields_to_show = [
                ("Invoice Number", invoice_data.get("Invoice Number")),
                ("User Name", invoice_data.get("User Name")),
                ("Due Date", invoice_data.get("Due Date")),
                ("Billing Address", invoice_data.get("Billing Address")),
                ("Currency", invoice_data.get("Currency")),
                ("Tax Amount", invoice_data.get("Tax Amount")),
                ("Payment Terms", invoice_data.get("Payment Terms")),
                ("Total Amount", invoice_data.get("Total Amount")),
            ]

            for label, value in fields_to_show:
                if value and value != "N/A":
                    st.write(f"**{label}:** {value}")

            # -------- Product Details -------- #
            if "Product Details" in invoice_data and isinstance(invoice_data["Product Details"], list):
                st.write("### 🛒 Product Details")
                df = pd.DataFrame(invoice_data["Product Details"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No product details found in this invoice.")

        # Update progress
        progress.progress(idx / total_files)

    # -------- CSV Download Options -------- #
    st.markdown("### ⬇️ Download Options")

    col1, col2 = st.columns(2)

    with col1:
        combined_csv = save_to_csv(extracted_data_list, file_name="all_invoices.csv")
        st.download_button(
            label="📥 Download All Invoices (Single CSV)",
            data=open(combined_csv, "rb"),
            file_name="all_invoices.csv",
            mime="text/csv",
            key="all_invoices"
        )

    with col2:
        if len(extracted_data_list) > 1:
            for idx, invoice in enumerate(extracted_data_list, start=1):
                if "Invoice Number" in invoice:
                    inv_num = invoice.get("Invoice Number", f"Invoice_{idx}")
                else:
                    inv_num = f"Invoice_{idx}_raw"

                safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', str(inv_num))
                sep_file = save_to_csv([invoice], file_name=f"{safe_name}.csv")
                st.download_button(
                    label=f"📥 {safe_name}.csv",
                    data=open(sep_file, "rb"),
                    file_name=f"{safe_name}.csv",
                    mime="text/csv",
                    key=f"invoice_{idx}"
                )


