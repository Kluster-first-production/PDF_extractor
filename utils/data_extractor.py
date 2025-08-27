from langchain_groq import ChatGroq
from config import GROQ_API_KEY

def is_invoice_text(text: str) -> bool:
    """
    Check if the PDF text looks like an invoice by scanning for common keywords.
    """
    invoice_keywords = [
        "invoice", "bill", "amount due", "due date",
        "billing address", "tax", "total", "payment terms"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in invoice_keywords)


def extract_invoice_data(pdf_text: str):
    """
    Extract structured invoice data if it looks like an invoice,
    otherwise return raw text (truncated).
    """
    if not is_invoice_text(pdf_text):
        return {
            "raw_text": pdf_text[:2000] + "... (truncated - not invoice)"
        }

    prompt = f"""
    Extract the following fields from the invoice text:

    - Invoice Number
    - User Name
    - Billing Address
    - Due Date
    - Payment Terms
    - Currency
    - Tax Amount
    - Product Details (list of objects with name, quantity, price, total)
    - Total Amount

    Output ONLY valid JSON. No explanations, no notes, no markdown fences.

    Invoice Text:
    {pdf_text}
    """

    chat = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.0,
        groq_api_key=GROQ_API_KEY
    )

    response = chat.invoke(prompt)
    return response.content
