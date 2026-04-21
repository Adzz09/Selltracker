\# 🛒 SellTracker – Retail Management System



A \*\*Python Tkinter desktop application\*\* for managing retail operations including \*\*billing, stock management, and analytics dashboards\*\* with real-time charts and PDF bill generation.



\---



\## ✨ Features



\### 📊 Dashboard



\* Total sales overview

\* Product count tracking

\* Low stock alerts

\* Best-selling products



\### 🧾 Billing System



\* Add products to cart

\* Auto GST calculation (18%)

\* Discount support

\* Stock validation

\* PDF bill generation



\### 📦 Inventory Management



\* Add / Update / Delete products

\* Live stock tracking

\* Low-stock indicators



\### 📈 Analytics Dashboard



\* Sales trend visualization (Matplotlib)

\* Top customers analysis

\* Best-selling products pie chart

\* Category-based insights



\---



\## 🛠️ Tech Stack



\* Python 🐍

\* Tkinter (GUI)

\* MySQL (Database)

\* Matplotlib (Charts)

\* ReportLab (PDF generation)



\---



\## ⚙️ Installation



\### 1. Clone repo



git clone https://github.com/Adzz09/selltracker.git

cd selltracker

```



\### 2. Install dependencies



pip install -r requirements.txt

```



\### 3. Run project



python main.py

```



\---



\## 🗄️ Database Setup



Create a MySQL database:



CREATE DATABASE selltracker;



CREATE TABLE stocks (

&#x20;   id INT AUTO\_INCREMENT PRIMARY KEY,

&#x20;   name VARCHAR(100),

&#x20;   quantity INT,

&#x20;   price FLOAT,

&#x20;   product\_cat VARCHAR(50)

);



CREATE TABLE customers (

&#x20;   id INT AUTO\_INCREMENT PRIMARY KEY,

&#x20;   customer\_name VARCHAR(100),

&#x20;   purchase\_amt FLOAT,

&#x20;   date\_time TIMESTAMP DEFAULT CURRENT\_TIMESTAMP

);



CREATE TABLE sold\_products (

&#x20;   id INT AUTO\_INCREMENT PRIMARY KEY,

&#x20;   prodt\_name VARCHAR(100),

&#x20;   qty INT

);

```



\---



\## 📦 requirements.txt



tk

pymysql

reportlab

matplotlib

```



\---



\## 🚀 Future Improvements



\* Login system with roles (Admin/Cashier)

\* Cloud database support

\* Receipt email sending

\* Dark mode UI

\* Barcode scanner integration



\---



\## 📄 License



This project is licensed under the \*\*MIT License\*\*.



\---



\## 👨‍💻 Author



Mayukh Mallick

GitHub: https://github.com/Adzz09
