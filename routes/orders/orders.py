import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, session
#

EXCEL_FILE = "data_new.xlsx"
ORDERS_SHEET = "orders"
PRODUCTS_SHEET = "products"

orders_bp = Blueprint("orders", __name__, template_folder="../../templates/orders")

# ---------- Helper ----------
def read_sheet(sheet_name):
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    df.columns = df.columns.str.strip().str.lower()
    return df

def read_orders():
    df = pd.read_excel(EXCEL_FILE, sheet_name=ORDERS_SHEET)
    df.columns = df.columns.str.strip().str.lower()
    return df

def write_orders(df):
    with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=ORDERS_SHEET, index=False)

def read_products():
    df = pd.read_excel(EXCEL_FILE, sheet_name=PRODUCTS_SHEET)
    df.columns = df.columns.str.strip().str.lower()
    return df

# ---------- Display ----------
@orders_bp.route("/orders/details")
def display_orders():
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    user_id = session["user_id"]
    df = read_orders()
    # Filter only orders belonging to the logged-in user
    df_user = df[df["customerid"] == user_id]

    return render_template("orders/details.html", orders=df_user.to_dict(orient="records"))


# ---------- Add ----------
@orders_bp.route("/orders/add", methods=["GET","POST"])
def add_order():
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    customer_id = session["user_id"]  # logged-in user
    products = read_products().to_dict(orient="records")

    if request.method=="POST":
        product_id = int(request.form["product_id"])
        quantity = int(request.form.get("quantity",1))

        df = read_orders()
        new_id = int(df["id"].max()) + 1 if not df.empty else 1
        new_row = pd.DataFrame([[new_id, customer_id, product_id, quantity]], columns=df.columns)
        df = pd.concat([df,new_row], ignore_index=True)
        write_orders(df)

        return redirect(url_for("orders.display_orders"))

    return render_template("orders/add.html", products=products)

# ---------- Update ----------
@orders_bp.route("/orders/update/<int:id>", methods=["GET","POST"])
def update_order(id):
    df = read_orders()
    idx = df.index[df["id"]==id].tolist()
    if not idx:
        return "Order not found", 404
    row_idx = idx[0]

    if request.method=="POST":
        df.at[row_idx,"productid"]=int(request.form["product_id"])
        df.at[row_idx,"quantity"]=int(request.form.get("quantity",1))
        write_orders(df)
        return redirect(url_for("orders.display_orders"))

    order = df.loc[row_idx].to_dict()
    products = read_products().to_dict(orient="records")
    return render_template("orders/update.html", order=order, products=products)

# ---------- Delete ----------
@orders_bp.route("/orders/delete/<int:id>", methods=["POST"])
def delete_order(id):
    df = read_orders()
    df = df[df["id"]!=id]
    write_orders(df)
    return redirect(url_for("orders.display_orders"))

@orders_bp.route("/my_orders")
def my_orders():
    if session.get("role") != "customer":
        return "Unauthorized", 403

    user_id = session.get("user_id")
    orders_df = read_sheet("orders")

    # filter only logged-in customer's orders
    my_orders = orders_df[orders_df["customer_id"] == user_id]

    return render_template("orders.html", orders=my_orders.to_dict(orient="records"))