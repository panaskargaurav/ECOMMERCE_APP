import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, session

EXCEL_FILE = "data_new.xlsx"
USERS_SHEET = "users"
CUSTOMERS_SHEET = "customers"

users_bp = Blueprint("users", __name__, template_folder="../../templates/users")

# ---------- Helpers ----------
def read_users():
    df = pd.read_excel(EXCEL_FILE, sheet_name=USERS_SHEET)
    df.columns = df.columns.str.strip().str.lower()  # strip spaces & lowercase
    return df

def write_users(df):
    with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=USERS_SHEET, index=False)

def read_customers():
    df = pd.read_excel(EXCEL_FILE, sheet_name=CUSTOMERS_SHEET)
    df.columns = df.columns.str.strip().str.lower()
    return df

def write_customers(df):
    with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=CUSTOMERS_SHEET, index=False)

# ---------- Register ----------
@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()  # get role from form
        email = request.form.get("email","").strip()
        phone = request.form.get("phone","").strip()
        address = request.form.get("address","").strip()

        # --- Users sheet ---
        users_df = read_users()
        users_df[["username","password","role"]] = users_df[["username","password","role"]].astype(str).apply(lambda x: x.str.strip())

        # Check duplicate username + role
        if not users_df[(users_df["username"] == username) & (users_df["role"] == role)].empty:
            return "User with this username and role already exists!", 400

        # Generate new id
        new_user_id = int(users_df["id"].max()) + 1 if not users_df.empty else 1

        # Append new user
        new_user = pd.DataFrame([{
            "id": new_user_id,
            "username": username,
            "password": password,
            "role": role
        }])
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        write_users(users_df)

        # --- Customers sheet ---
        try:
            customers_df = read_customers()
        except:
            customers_df = pd.DataFrame(columns=["id", "name", "email", "phone", "address", "role"])

        new_customer = pd.DataFrame([{
            "id": new_user_id,
            "name": username,
            "email": email,
            "phone": phone,
            "address": address,
            "role": role
        }])
        customers_df = pd.concat([customers_df, new_customer], ignore_index=True)
        write_customers(customers_df)

        return redirect(url_for("users.login"))

    return render_template("users/register.html")

# ---------- Login ----------
@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form.get("role","").strip()  # get role from form

        # read users safely
        users_df = read_users()
        for col in ["username","password","role"]:
            users_df[col] = users_df[col].astype(str).str.strip()

        # match exactly
        user = users_df[(users_df["username"] == username) & 
                        (users_df["password"] == password) & 
                        (users_df["role"] == role)]

        if not user.empty:
            session["user_id"] = int(user.iloc[0]["id"])
            session["username"] = username
            session["role"] = role

            # redirect based on role
            if role == "customer":
                return redirect(url_for("products.display_products"))
            elif role == "seller":
                return redirect(url_for("products.manage_products"))
        return "Invalid credentials or role!", 401

    return render_template("users/login.html")

# ---------- Logout ----------
@users_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("users.login"))
