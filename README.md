# 🛒 E-Commerce Web Application  
 A Flask-based **E-Commerce Web App** where:  
  - Users can register/login and browse products  
  - Customers can place orders  
  - Sellers can add/update products  
  - Admins can manage users, products, and orders  
 Data can be stored in Excel (beginner-friendly).

## 🚀 Features  

 - 👤 **User Roles**:  
   - **Customer** → Browse products, place orders, view past orders  
   - **Seller** → Add, update, and manage products  
   - **Admin** → Full CRUD (Users, Products, Orders)  

 - 📦 **Products Management**  
   - Add, update, delete products  
   - View all products  

 - 🛍 **Orders Management**  
   - Customers place orders  
   - Admin manages all orders  

 - 🗂 **Excel**  
   - Beginner friendly with Excel  

## 📂 Project Structure  
<img width="1209" height="927" alt="image" src="https://github.com/user-attachments/assets/7f32bc03-354b-434e-82f9-5802a244f153" />


## ⚙️ Installation  

1. **Clone the repo**  

  
  git clone https://github.com/yourusername/ECOMMERCE_APP.git
  cd ECOMMERCE_APP

*Create virtual environment (recommended)

  python -m venv venv
  source venv/bin/activate   # On Linux/Mac
  venv\Scripts\activate      # On Windows

*Install dependencies

  pip install -r requirements.txt


# 📦 Requirements

  Your requirements.txt should contain:

  flask
  pandas


▶️ Running the App
	
  Run Flask server

  python app.py

▶️Open in browser

  http://127.0.0.1:5000/

# 🔑 Default Credentials

 Admin Login

  Username: admin

  Password: admin (or as configured in your users.xlsx)

 (Update credentials in your Excel)

# 🛠 Tech Stack

 *Backend → Python, Flask, Pandas/SQLite

 *Frontend → HTML, CSS (Bootstrap), Jinja2

 *Storage → Excel 

# 🤝 Contributing

  Fork the repo

  Create a feature branch (git checkout -b feature-name)

  Commit changes (git commit -m "Add feature")

  Push to branch (git push origin feature-name)

  Create a Pull Request
