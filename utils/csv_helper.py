import os
import pandas as pd

def save_to_csv(data_list, file_name="invoice_data.csv", folder="data/exports"):
    # Ensure export folder exists
    os.makedirs(folder, exist_ok=True)

    # 🔥 Cleanup: remove old CSV files
    for f in os.listdir(folder):
        if f.endswith(".csv"):
            os.remove(os.path.join(folder, f))

    # Prepare rows
    rows = []
    for invoice in data_list:
        invoice_number = invoice.get("Invoice Number", "")
        user_name = invoice.get("User Name", "")
        due_date = invoice.get("Due Date", "")
        total_amount = invoice.get("Total Amount", "")

        product_details = invoice.get("Product Details", [])
        if isinstance(product_details, list):
            for product in product_details:
                rows.append({
                    "Invoice Number": invoice_number,
                    "User Name": user_name,
                    "Due Date": due_date,
                    "Item Name": product.get("name", ""),
                    "Quantity": product.get("quantity", ""),
                    "Price": product.get("price", ""),
                    "Total": product.get("total", ""),
                    "Invoice Total Amount": total_amount
                })
        else:
            rows.append({
                "Invoice Number": invoice_number,
                "User Name": user_name,
                "Due Date": due_date,
                "Item Name": "",
                "Quantity": "",
                "Price": "",
                "Total": "",
                "Invoice Total Amount": total_amount
            })

    # Save new CSV
    path = os.path.join(folder, file_name)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return path
