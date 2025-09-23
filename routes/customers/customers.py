import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template

EXCEL_FILE = "data_new.xlsx"
CUSTOMERS_SHEET = "customers"

customers_bp = Blueprint("customers", __name__, template_folder="../../templates/customers")

# ---------- Helper ----------
def read_customers():
    df = pd.read_excel(EXCEL_FILE, sheet_name=CUSTOMERS_SHEET)
    df.columns = df.columns.str.strip().str.lower()  # ensure lowercase
    return df

def write_customers(df):
    with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=CUSTOMERS_SHEET, index=False)

# ---------- Display ----------
@customers_bp.route("/customers/details")
def display_customers():
    df = read_customers()
    return render_template("customers/details.html", customers=df.to_dict(orient="records"))

# ---------- Add ----------
@customers_bp.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form.get("email","").strip()
        phone = request.form.get("phone","").strip()
        address = request.form.get("address","").strip()

        df = read_customers()
        new_id = int(df["id"].max()) + 1 if not df.empty else 1
        new_row = pd.DataFrame([[new_id, name, email, phone, address]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        write_customers(df)

        return redirect(url_for("customers.display_customers"))

    return render_template("customers/add.html")

# ---------- Update ----------
@customers_bp.route("/customers/update/<int:id>", methods=["GET","POST"])
def update_customer(id):
    df = read_customers()
    idx = df.index[df["id"]==id].tolist()
    if not idx:
        return "Customer not found", 404
    row_idx = idx[0]

    if request.method=="POST":
        df.at[row_idx,"name"]=request.form["name"].strip()
        df.at[row_idx,"email"]=request.form.get("email","").strip()
        df.at[row_idx,"phone"]=request.form.get("phone","").strip()
        df.at[row_idx,"address"]=request.form.get("address","").strip()
        write_customers(df)
        return redirect(url_for("customers.display_customers"))

    customer = df.loc[row_idx].to_dict()
    return render_template("customers/update.html", customer=customer)

# ---------- Delete ----------
@customers_bp.route("/customers/delete/<int:id>", methods=["POST"])
def delete_customer(id):
    df = read_customers()
    df = df[df["id"]!=id]
    write_customers(df)
    return redirect(url_for("customers.display_customers"))
