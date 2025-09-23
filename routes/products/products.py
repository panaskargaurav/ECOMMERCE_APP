import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, session

EXCEL_FILE = "data_new.xlsx"
PRODUCTS_SHEET = "products"

products_bp = Blueprint("products", __name__, template_folder="../../templates/products")

# ---------- Helpers ----------
def read_products():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=PRODUCTS_SHEET)
        df.columns = df.columns.str.strip().str.lower()
    except:
        # If file or sheet doesn't exist, create empty DataFrame
        df = pd.DataFrame(columns=[
            "id", "name", "price", "stock", "category",
            "details", "rating", "image_url", "seller_id"
        ])
    # Ensure seller_id column exists
    if "seller_id" not in df.columns:
        df["seller_id"] = None
    return df

def write_products(df):
    with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=PRODUCTS_SHEET, index=False)

# ---------- Display All Products (Customer view) ----------
@products_bp.route("/products/details")
def display_products():
    df = read_products()
    return render_template("products/details.html", products=df.to_dict(orient="records"))

# ---------- Add Product (Seller) ----------
@products_bp.route("/products/add", methods=["GET", "POST"])
def add_product():
    if session.get("role") != "seller":
        return "Unauthorized", 403

    if request.method == "POST":
        name = request.form["name"].strip()
        price = float(request.form.get("price", 0))
        stock = int(request.form.get("stock", 0))
        category = request.form.get("category", "").strip()
        details = request.form.get("details", "").strip()
        rating = float(request.form.get("rating", 0))
        image_url = request.form.get("image_url", "").strip()

        df = read_products()
        new_id = df["id"].max() + 1 if not df.empty else 1

        new_row = pd.DataFrame([{
            "id": new_id,
            "name": name,
            "price": price,
            "stock": stock,
            "category": category,
            "details": details,
            "rating": rating,
            "image_url": image_url,
            "seller_id": session["user_id"]
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        write_products(df)
        return redirect(url_for("products.manage_products"))

    return render_template("products/add.html")

# ---------- Update Product (Seller) ----------
@products_bp.route("/products/update/<int:id>", methods=["GET", "POST"])
def update_product(id):
    df = read_products()
    idx_list = df.index[df["id"] == id].tolist()
    if not idx_list:
        return "Product not found", 404
    row_idx = idx_list[0]

    # Only seller who owns the product can update
    if df.at[row_idx, "seller_id"] != session.get("user_id"):
        return "Unauthorized", 403

    if request.method == "POST":
        df.at[row_idx, "name"] = request.form["name"].strip()
        df.at[row_idx, "price"] = float(request.form.get("price", 0))
        df.at[row_idx, "stock"] = int(request.form.get("stock", 0))
        df.at[row_idx, "category"] = request.form.get("category", "").strip()
        df.at[row_idx, "details"] = request.form.get("details", "").strip()
        df.at[row_idx, "rating"] = float(request.form.get("rating", 0))
        df.at[row_idx, "image_url"] = request.form.get("image_url", "").strip()
        write_products(df)
        return redirect(url_for("products.manage_products"))

    product = df.loc[row_idx].to_dict()
    return render_template("products/update.html", product=product)

# ---------- Delete Product (Seller) ----------
@products_bp.route("/products/delete/<int:id>", methods=["POST"])
def delete_product(id):
    df = read_products()
    idx_list = df.index[df["id"] == id].tolist()
    if not idx_list:
        return "Product not found", 404
    row_idx = idx_list[0]

    # Only seller can delete their product
    if df.at[row_idx, "seller_id"] != session.get("user_id"):
        return "Unauthorized", 403

    df = df.drop(row_idx).reset_index(drop=True)
    write_products(df)
    return redirect(url_for("products.manage_products"))

# ---------- Seller Manage Products ----------
@products_bp.route("/products/manage")
def manage_products():
    if session.get("role") != "seller":
        return "Unauthorized", 403

    seller_id = session.get("user_id")
    df = read_products()
    my_products = df[df["seller_id"] == seller_id]

    show_add_button = True if my_products.empty else False

    return render_template(
        "products/manage_products.html",
        products=my_products.to_dict(orient="records"),
        show_add_button=show_add_button
    )

# ---------- List / Search Products (Customer) ----------
@products_bp.route("/products")
def list_products():
    q = request.args.get("q", "").lower()
    df = read_products()
    products = df.to_dict(orient="records")
    if q:
        products = [p for p in products if q in str(p["name"]).lower()]
    return render_template("products/details.html", products=products)

