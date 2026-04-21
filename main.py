import tkinter as tk
from tkinter import ttk, messagebox
import pymysql as c
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# -------- DATABASE --------
db = c.connect(DB_CONFIG)
cr = db.cursor()

# -------- MAIN WINDOW --------
root = tk.Tk()
root.title("SellTracker")
root.geometry("1000x600")
root.configure(bg="#f5f6fa")

# -------- SIDEBAR --------
sidebar = tk.Frame(root, bg="#f39c12", width=180)
sidebar.pack(side="left", fill="y")

# -------- MAIN AREA --------
main = tk.Frame(root, bg="#f5f6fa")
main.pack(side="right", fill="both", expand=True)

# -------- HEADER --------
header = tk.Frame(main, bg="white", height=60)
header.pack(fill="x")

tk.Label(header, text="SaleTracker", font=("Arial", 16, "bold"), bg="white").pack(side="left", padx=20)
tk.Label(header, text="Welcome, User", bg="white").pack(side="right", padx=20)

# -------- CONTENT --------
content = tk.Frame(main, bg="#f5f6fa")
content.pack(fill="both", expand=True, padx=20, pady=20)

# -------- CARD FUNCTIONS --------
def stat_card(parent, title, value, color="black"):
    c = tk.Frame(parent, bg="white", highlightbackground="#ddd", highlightthickness=1)
    c.pack(side="left", expand=True, fill="both", padx=10)

    tk.Label(c, text=title, bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
    tk.Label(c, text=value, bg="white", fg=color, font=("Arial", 18, "bold")).pack(pady=20)

    return c


def create_card(parent, title):
    c = tk.Frame(parent, bg="white", highlightbackground="#ddd", highlightthickness=1)
    c.pack(side="left", fill="both", expand=True, padx=10)

    tk.Label(c, text=title, font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)

    return c

# -------- MANAGE STOCKS POPUP --------
def manage_stocks_popup():
    popup = tk.Toplevel(root)
    popup.title("Manage Stocks")
    popup.geometry("300x300")

    action_var = tk.StringVar()

    ttk.Combobox(
        popup,
        textvariable=action_var,
        values=["Add Product", "Update Quantity", "Delete Product"]
    ).pack(pady=10)

    def load_ui(*args):
        for w in popup.winfo_children()[1:]:
            w.destroy()

        if action_var.get() == "Add Product":
            name = tk.Entry(popup)
            name.pack(pady=5)

            qty = tk.Entry(popup)
            qty.pack(pady=5)

            price = tk.Entry(popup)
            price.pack(pady=5)

            def save():
                cr.execute(
                    "INSERT INTO stocks(name,quantity,price) VALUES(%s,%s,%s)",
                    (name.get(), qty.get(), price.get())
                )
                db.commit()
                popup.destroy()
                show_screen("Products")

            tk.Button(popup, text="Save", command=save).pack(pady=10)

        elif action_var.get() == "Update Quantity":
            cr.execute("SELECT name FROM stocks")
            products = [r[0] for r in cr.fetchall()]

            p = tk.StringVar()
            ttk.Combobox(popup, textvariable=p, values=products).pack(pady=5)

            qty = tk.Entry(popup)
            qty.pack(pady=5)

            def update():
                cr.execute(
                    "UPDATE stocks SET quantity=%s WHERE name=%s",
                    (qty.get(), p.get())
                )
                db.commit()
                popup.destroy()
                show_screen("Products")

            tk.Button(popup, text="Update", command=update).pack(pady=10)

        elif action_var.get() == "Delete Product":
            cr.execute("SELECT name FROM stocks")
            products = [r[0] for r in cr.fetchall()]

            p = tk.StringVar()
            ttk.Combobox(popup, textvariable=p, values=products).pack(pady=5)

            def delete():
                cr.execute("DELETE FROM stocks WHERE name=%s", (p.get(),))
                db.commit()
                popup.destroy()
                show_screen("Products")

            tk.Button(popup, text="Delete", command=delete).pack(pady=10)

    action_var.trace_add("write", load_ui)

# -------- SCREEN SWITCH --------
def show_screen(name):
    for widget in content.winfo_children():
        widget.destroy()

    # -------- DASHBOARD --------
    if name == "Dashboard":
        top_frame = tk.Frame(content, bg="#f5f6fa")
        top_frame.pack(fill="x")

        q_sls = "Select sum(purchase_amt) from customers"
        cr.execute(q_sls)
        result = cr.fetchone()
        sls = result[0] if result and result[0] is not None else 0

        q_prd = "select count(*) from stocks"
        cr.execute(q_prd)
        result = cr.fetchone()
        prd = result[0] if result else 0

        q_stk = "select count(quantity) from stocks where quantity<=10"
        cr.execute(q_stk)
        result = cr.fetchone()
        l_stk = result[0] if result else 0

        stat_card(top_frame, "Total Sales", sls, "green")
        stat_card(top_frame, "Products", prd)
        stat_card(top_frame, "Low Stock", l_stk, "red")

        middle_frame = tk.Frame(content, bg="#f5f6fa")
        middle_frame.pack(fill="both", expand=True, pady=20)

        orders_card = create_card(middle_frame, "Last Orders")

        q_lord = "select * from customers order by id DESC limit 5;"
        cr.execute(q_lord)
        lord = cr.fetchall()

        for i in lord:
            row = tk.Frame(orders_card, bg="white")
            row.pack(fill="x", padx=10, pady=5)

            tk.Label(row, text=i[1], bg="white").pack(side="left")
            tk.Label(row, text=f"₹{i[2]}", bg="white").pack(side="right")

        stock_card = create_card(middle_frame, "Low Stock Items")

        q_lowstk_items = "select name, quantity from stocks where quantity<=10"
        cr.execute(q_lowstk_items)
        lstk_items = cr.fetchall()

        for item in lstk_items:
            row = tk.Frame(stock_card, bg="white")
            row.pack(fill="x", padx=10, pady=5)

            tk.Label(row, text=item[0], bg="white").pack(side="left")
            if item[1] == 0:
                tk.Label(row, text="Out of stock", fg="red", bg="white").pack(side="right")
            elif item[1] <= 5:
                tk.Label(row, text="Vey Low", fg="red", bg="white").pack(side="right")
            else:
                tk.Label(row, text="Low", fg="red", bg="white").pack(side="right")

        bottom_frame = tk.Frame(content, bg="#f5f6fa")
        bottom_frame.pack(fill="both", expand=True)

        best_card = create_card(bottom_frame, "Best Sellers")

        q_bst_seller = "select prodt_name, SUM(qty) AS total_qty from sold_products group by prodt_name order by total_qty desc limit 3"
        cr.execute(q_bst_seller)
        bst_seller = cr.fetchall()

        for item in bst_seller:
            tk.Label(best_card, text=item[0], bg="white").pack(anchor="w", padx=10, pady=5)

    # -------- BILLING --------
    elif name == "Billing":
        total = 0

        def add_item():
            nonlocal total
            product = product_var.get()
            qty = qty_entry.get()

            if not product or not qty:
                messagebox.showerror("Error", "Fill all fields")
                return

            qty = int(qty)

            cr.execute("SELECT price, quantity FROM stocks WHERE name=%s", (product,))
            data = cr.fetchone()

            if not data:
                messagebox.showerror("Error", "Invalid product")
                return

            price, stock_qty = data

            if qty > stock_qty:
                messagebox.showerror("Error", "Not enough stock!")
                return

            subtotal = qty * price
            total += subtotal

            tree.insert("", "end", values=(product, qty, price, subtotal))
            update_total()

        def update_total():
            tax = total * 0.18
            discount = int(discount_entry.get() or 0)
            final = total + tax - discount

            total_label.config(text=f"Subtotal: ₹{total}")
            tax_label.config(text=f"GST: ₹{tax:.2f}")
            final_label.config(text=f"Total: ₹{final:.2f}")

        def make_bill():
            pdts=[]
            name = name_entry.get()
            if not name:
                messagebox.showerror("Error", "Enter customer name")
                return

            tax = total * 0.18
            discount = int(discount_entry.get() or 0)
            final = total + tax - discount

            cr.execute("INSERT INTO customers(customer_name,purchase_amt) VALUES(%s,%s)", (name, final))

            for row in tree.get_children():
                item = tree.item(row)['values']
                pdts.append(item)
                cr.execute("UPDATE stocks SET quantity=quantity-%s WHERE name=%s", (item[1], item[0]))

                cr.execute("insert into sold_products(prodt_name, qty) values (%s,%s)", (item[0],item[1]))
                db.commit()

            db.commit()
            messagebox.showinfo("Success", "Bill created!")
            show_screen("Billing")

            def create_pdf(filename):
                now = datetime.now()
                dte = now.strftime("%d-%m-%Y")
                tme = now.strftime("%H:%M:%S")

                c = canvas.Canvas(filename, pagesize=A4)
                width, height = A4

                # Title
                c.setFont("Helvetica-Bold", 20)
                c.drawCentredString(width / 2, height - 50, "Bill")

                # Header info
                c.setFont("Helvetica", 12)
                c.drawString(100, height - 120, f"Customer Name: {name}")
                c.drawString(100, height - 100, f"Date: {dte}")
                c.drawString(300, height - 100, f"Time: {tme}")

                # Table header
                y = height - 160
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, y, "Product")
                c.drawString(250, y, "Qty")
                c.drawString(300, y, "Price")
                c.drawString(370, y, "Subtotal")
                c.line(100, y - 5, 450, y - 5)

                # Table rows from Treeview
                c.setFont("Helvetica", 12)
                y -= 25
                for q in pdts:
                    product, qty, price, subtotal = q[0], q[1], q[2], q[3]
                    c.drawString(100, y, str(product))
                    c.drawString(250, y, str(qty))
                    c.drawString(300, y, f"{price}")
                    c.drawString(370, y, f"{subtotal}")
                    y -= 20

                # Totals
                y -= 20
                c.line(100, y, 450, y)
                y -= 20
                c.drawString(100, y, f"Final Amount: ₹{final:.2f}")

                # Footer
                c.setFont("Helvetica-Oblique", 10)
                c.drawCentredString(width / 2, 50, "Generated by SellTracker")

                c.save()

            create_pdf(f"{name}.pdf")

        tk.Label(content, text="Billing", font=("Arial", 18), bg="#f5f6fa").pack(anchor="w")

        name_entry = tk.Entry(content)
        name_entry.pack(pady=5)
        name_entry.insert(0, "Customer Name")

        cr.execute("SELECT name FROM stocks")
        products = [r[0] for r in cr.fetchall()]

        product_var = tk.StringVar()
        ttk.Combobox(content, textvariable=product_var, values=products).pack(pady=5)

        qty_entry = tk.Entry(content)
        qty_entry.pack(pady=5)
        qty_entry.insert(0, "Quantity")

        tk.Button(content, text="Add Item", command=add_item).pack(pady=5)

        tree = ttk.Treeview(content, columns=("Product", "Qty", "Price", "Subtotal"), show="headings")
        for col in ("Product", "Qty", "Price", "Subtotal"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        discount_entry = tk.Entry(content)
        discount_entry.insert(0, "0")
        discount_entry.pack(pady=5)

        total_label = tk.Label(content, text="Subtotal: ₹0", bg="#f5f6fa")
        total_label.pack()

        tax_label = tk.Label(content, text="GST: ₹0", bg="#f5f6fa")
        tax_label.pack()

        final_label = tk.Label(content, text="Total: ₹0", bg="#f5f6fa")
        final_label.pack()

        tk.Button(content, text="Make Bill", command=make_bill).pack(pady=10)

    # -------- PRODUCTS --------
    elif name == "Products":
        tk.Label(content, text="Stocks", font=("Arial", 18), bg="#f5f6fa").pack(anchor="w")

        cr.execute("SELECT * FROM stocks")
        data = cr.fetchall()

        tree = ttk.Treeview(content, columns=("ID", "Name", "Quantity"), show="headings")
        for col in ("ID", "Name", "Quantity"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for row in data:
            tree.insert("", "end", values=row)

        tk.Button(content, text="Manage Stocks", command=manage_stocks_popup).pack(pady=10)

    # -------- ANALYTICS --------
    else:
        container = tk.Frame(content, bg="#f5f6fa")
        container.pack(fill="both", expand=True)
        
        top_row = tk.Frame(container, bg="#f5f6fa")
        top_row.pack(fill="x", pady=10)
        
        try:
            cr.execute("SELECT DATE(date_time), SUM(purchase_amt) FROM customers GROUP BY DATE(date_time) ORDER BY DATE(date_time) DESC LIMIT 7")
            daily_sales = cr.fetchall()
        except:
            cr.execute("SELECT purchase_amt FROM customers ORDER BY id DESC LIMIT 7")
            daily_sales = [(f"Day {i+1}", r[0]) for i, r in enumerate(cr.fetchall())]
        
        if daily_sales:
            dates = [str(r[0]) for r in reversed(daily_sales)]
            amounts = [float(r[1] or 0) for r in reversed(daily_sales)]
            
            fig1, ax1 = plt.subplots(figsize=(5, 3), dpi=100)
            fig1.patch.set_facecolor("#f5f6fa")
            ax1.set_facecolor("#f5f6fa")
            colors = ['#f39c12', '#e67e22', '#d35400', '#c0392b', '#e74c3c', '#e67e22', '#f39c12']
            bars = ax1.bar(range(len(dates)), amounts, color=colors[:len(dates)])
            ax1.set_xticks(range(len(dates)))
            ax1.set_xticklabels([d[-5:] for d in dates], rotation=45, ha='right', fontsize=8)
            ax1.set_ylabel("Sales (₹)", fontsize=10)
            ax1.set_title("Daily Sales (Last 7 Days)", fontsize=12, fontweight="bold")
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.grid(axis='y', alpha=0.3)
            
            for bar, val in zip(bars, amounts):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(amounts)*0.02, 
                        f"₹{int(val)}", ha='center', va='bottom', fontsize=8)
            
            canvas1 = FigureCanvasTkAgg(fig1, top_row)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)
        
        cr.execute("SELECT prodt_name, SUM(qty) FROM sold_products GROUP BY prodt_name ORDER BY SUM(qty) DESC LIMIT 5")
        top_products = cr.fetchall()
        
        if top_products:
            fig2, ax2 = plt.subplots(figsize=(5, 3), dpi=100)
            fig2.patch.set_facecolor("#f5f6fa")
            ax2.set_facecolor("#f5f6fa")
            products = [r[0] for r in top_products]
            qty_sold = [int(r[1]) for r in top_products]
            colors = ['#f39c12', '#e67e22', '#d35400', '#c0392b', '#e74c3c'][:len(products)]
            result = ax2.pie(qty_sold, labels=products, autopct='%1.1f%%', 
                                                colors=colors, startangle=90, pctdistance=0.75)
            ax2.set_title("Top Selling Products", fontsize=12, fontweight="bold")
            if len(result) == 3:
                wedges, texts, autotexts = result
                for autotext in autotexts:
                    autotext.set_fontsize(8)
                    autotext.set_fontweight("bold")
                for text in texts:
                    text.set_fontsize(9)
            
            canvas2 = FigureCanvasTkAgg(fig2, top_row)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)
        
        bottom_row = tk.Frame(container, bg="#f5f6fa")
        bottom_row.pack(fill="both", expand=True, pady=10)
        
        try:
            cr.execute("SELECT product_cat, COUNT(*) FROM stocks GROUP BY product_cat")
            cat_data = cr.fetchall()
        except:
            cr.execute("SELECT name, quantity FROM stocks ORDER BY quantity DESC LIMIT 5")
            cat_data = [(r[0], r[1]) for r in cr.fetchall()]
        
        if cat_data and any(r[0] for r in cat_data):
            fig3, ax3 = plt.subplots(figsize=(5, 3), dpi=100)
            fig3.patch.set_facecolor("#f5f6fa")
            ax3.set_facecolor("#f5f6fa")
            cats = [r[0] for r in cat_data if r[0]]
            counts = [r[1] for r in cat_data if r[0]]
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']
            ax3.barh(cats, counts, color=colors[:len(cats)])
            ax3.set_xlabel("Count", fontsize=10)
            ax3.set_title("Products by Category", fontsize=12, fontweight="bold")
            ax3.spines['top'].set_visible(False)
            ax3.spines['right'].set_visible(False)
            
            canvas3 = FigureCanvasTkAgg(fig3, bottom_row)
            canvas3.draw()
            canvas3.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)
        
        cr.execute("SELECT customer_name, purchase_amt FROM customers ORDER BY purchase_amt DESC LIMIT 5")
        top_customers = cr.fetchall()
        
        if top_customers:
            fig4, ax4 = plt.subplots(figsize=(5, 3), dpi=100)
            fig4.patch.set_facecolor("#f5f6fa")
            ax4.set_facecolor("#f5f6fa")
            customers = [str(r[0])[:10] for r in top_customers]
            amounts = [float(r[1] or 0) for r in top_customers]
            colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#3498db']
            ax4.barh(customers, amounts, color=colors[:len(customers)])
            ax4.set_xlabel("Total Purchases (₹)", fontsize=10)
            ax4.set_title("Top Customers", fontsize=12, fontweight="bold")
            ax4.spines['top'].set_visible(False)
            ax4.spines['right'].set_visible(False)
            
            for i, v in enumerate(amounts):
                ax4.text(v + max(amounts)*0.02, i, f"₹{int(v)}", va='center', fontsize=9)
            
            canvas4 = FigureCanvasTkAgg(fig4, bottom_row)
            canvas4.draw()
            canvas4.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)


# -------- SIDEBAR BUTTON --------
def menu_button(text, screen):
    return tk.Button(
        sidebar,
        text=text,
        fg="white",
        bg="#f39c12",
        activebackground="#e67e22",
        bd=0,
        anchor="w",
        padx=20,
        pady=10,
        command=lambda: show_screen(screen)
    )

menu_button("🏠 Dashboard", "Dashboard").pack(fill="x")
menu_button("🧾 Billing", "Billing").pack(fill="x")
menu_button("📦 Products", "Products").pack(fill="x")
menu_button("📊 Analytics", "Analytics").pack(fill="x")

show_screen("Dashboard")

root.mainloop()
