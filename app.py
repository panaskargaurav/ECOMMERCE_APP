from flask import Flask, render_template, request, redirect, url_for, session
from routes.users.users import users_bp
from routes.customers.customers import customers_bp
from routes.products.products import products_bp
from routes.orders.orders import orders_bp
import pandas as pd

EXCEL_FILE = "data_new.xlsx"

# ---------- Helper ----------
def read_sheet(sheet_name):
    """Read any Excel sheet and normalize column names"""
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    df.columns = df.columns.str.strip().str.lower()
    return df

def read_users():
    """Read users sheet specifically for login"""
    df = pd.read_excel(EXCEL_FILE, sheet_name="users")
    df.columns = df.columns.str.strip().str.lower()
    return df

# ---------- Flask App ----------
app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"

# ---------- Register Blueprints ----------
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(customers_bp)
app.register_blueprint(products_bp)
app.register_blueprint(orders_bp)

# ---------- Home Route ----------
@app.route("/")
def home():
    return render_template("home.html")

# ---------- Unified Login Route ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip().lower()

        if role not in ["customer", "seller", "admin"]:
            return "Invalid role!", 403

        users_df = read_users()
        user = users_df[
            (users_df["username"].str.strip() == username) &
            (users_df["password"].str.strip() == password) &
            (users_df["role"].str.strip().str.lower() == role)
        ]

        if user.empty:
            return "Invalid credentials or role!", 403

        # Save session info
        session["user_id"] = int(user.iloc[0]["id"])
        session["role"] = role

        # Redirect based on role
        if role == "customer":
            return redirect(url_for("view_products"))
        elif role == "seller":
            return redirect(url_for("manage_products"))
        elif role == "admin":
            return redirect(url_for("view_admin_data"))

    return render_template("login.html")

# ---------- Customer View Products ----------
@app.route("/products")
def view_products():
    if session.get("role") != "customer":
        return "Unauthorized", 403
   

    products_df = read_sheet("products")
    return render_template("products/details.html", products=products_df.to_dict(orient="records"))

# ---------- Seller Manage Products ----------
@app.route("/products/manage")
def manage_products():
    if session.get("role") != "seller":
        return "Unauthorized", 403

    products_df = read_sheet("products")
    return render_template("products/manage_products.html", products=products_df.to_dict(orient="records"))

# ---------- Admin Route: View All Data ----------
@app.route("/admin/dashboard")
def view_admin_data():
    if session.get("role") != "admin":
        return "Unauthorized", 403

    customers_df = read_sheet("customers")
    products_df = read_sheet("products")
    orders_df = read_sheet("orders")

    # Merge orders with products to show product name + price
    merged_df = pd.merge(
        orders_df,
        products_df,
        left_on="productid",
        right_on="id",
        suffixes=("_order", "_product"),
        how="left"
    )

    if not merged_df.empty:
        merged_df["total_price"] = merged_df["quantity"].astype(float) * merged_df["price"].astype(float)
        total_quantity = int(merged_df["quantity"].sum())
        total_revenue = float(merged_df["total_price"].sum())
        total_profit = round(total_revenue * 0.08, 2)
    else:
        total_quantity, total_revenue, total_profit = 0, 0, 0

    context = {
        "customers": customers_df.to_dict(orient="records"),
        "products": products_df.to_dict(orient="records"),
        "orders": merged_df.to_dict(orient="records"),
        "total_quantity": total_quantity,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "logged_in_user_id": session.get("user_id"),
    }

    return render_template("admin/data.html", **context)

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------- Run App ----------
if __name__ == "__main__":
    app.run(debug=True)
