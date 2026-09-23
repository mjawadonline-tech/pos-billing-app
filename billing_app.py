from datetime import datetime
import json
import os
import sys

STOCK_FILE = "inventory.json"
BILLS_FILE = "bills_history.json"


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {} if "inventory" in filename else []
    return {} if "inventory" in filename else []


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ================= INVENTORY / STOCK =================
def manage_inventory():
    while True:
        clear_screen()
        stock = load_json(STOCK_FILE)
        print("==================================================")
        print("             INVENTORY & STOCK MANAGEMENT         ")
        print("==================================================")
        print("1. Naya Item Add Karein / Stock Update Karein")
        print("2. Tamam Items Ki List Dekhein")
        print("3. Wapas Main Menu Par Jayein")
        print("--------------------------------------------------")

        choice = input("Option Chunien (1-3): ").strip()

        if choice == "1":
            name = input("\nItem ka naam: ").strip().lower()
            if not name:
                continue
            try:
                price = float(input("Per-Unit Price (PKR): ").strip())
                qty = float(
                    input("Quantity / Stock Kitna Hai (e.g. 50): ").strip()
                )

                if name in stock:
                    stock[name]["price"] = price
                    stock[name]["qty"] += qty
                else:
                    stock[name] = {"price": price, "qty": qty}

                save_json(STOCK_FILE, stock)
                print(f"\n✅ '{name.title()}' ka stock successfully save ho gaya!")
                input("\nAage badhne ke liye Enter dabayein...")
            except ValueError:
                print("\n❌ Ghalat input! Sirf numbers likhein.")
                input("\nDobara koshish ke liye Enter dabayein...")

        elif choice == "2":
            clear_screen()
            print("==================================================")
            print(f"{'Item Name':<20} {'Price (PKR)':<15} {'Available Stock':<15}")
            print("--------------------------------------------------")
            if not stock:
                print("Koi item stock me majood nahi hai.")
            else:
                for item, details in stock.items():
                    print(
                        f"{item.title():<20} {details['price']:<15.2f} {details['qty']:<15.2f}"
                    )
            print("==================================================")
            input("\nWapas jaane ke liye Enter dabayein...")

        elif choice == "3":
            break


# ================= NEW BILL / SALE =================
def create_bill():
    clear_screen()
    stock = load_json(STOCK_FILE)

    print("==================================================")
    print("                NAYA BILL / INVOICE               ")
    print("==================================================")

    cust_name = input("\nCustomer ka Naam: ").strip() or "Walk-in Customer"
    cust_phone = input("Customer ka Phone Number: ").strip() or "N/A"

    cart = []

    while True:
        print("\n--------------------------------------------------")
        item_name = (
            input("Item ka naam (Bill khatam karne ke liye 'done' likhein): ")
            .strip()
            .lower()
        )

        if item_name == "done":
            break

        if not item_name:
            continue

        price = 0.0
        if item_name in stock:
            print(
                f"ℹ️ Stock me majood hai! Price: PKR {stock[item_name]['price']} | Available: {stock[item_name]['qty']}"
            )
            price = stock[item_name]["price"]
        else:
            try:
                price = float(
                    input(f"'{item_name}' ki Per-Unit Price (PKR): ").strip()
                )
            except ValueError:
                print("❌ Ghalat price! Sirf numbers likhein.")
                continue

        while True:
            try:
                qty = float(
                    input(
                        f"'{item_name}' ki Quantity (Sirf number, e.g. 1 ya 0.5): "
                    ).strip()
                )
                if (
                    item_name in stock
                    and stock[item_name]["qty"] < qty
                ):
                    print(
                        f"⚠️ Khabardar: Stock me sirf {stock[item_name]['qty']} baki hain!"
                    )
                break
            except ValueError:
                print("❌ Ghalat quantity! Sirf numbers likhein.")

        cart.append(
            {"name": item_name.title(), "qty": qty, "price": price, "total": qty * price}
        )

        if item_name in stock:
            stock[item_name]["qty"] -= qty

        print(f"✅ '{item_name.title()}' bill me add ho gaya!")

    if not cart:
        print("\n❌ Bill me koi item add nahi hua.")
        input("\nEnter dabayein...")
        return

    subtotal = sum(i["total"] for i in cart)
    print("\n--------------------------------------------------")
    print(f"Subtotal: PKR {subtotal:.2f}")

    try:
        discount = float(
            input("Discount (PKR me, agar nahi hai to 0): ").strip()
            or 0
        )
    except ValueError:
        discount = 0.0

    grand_total = max(0.0, subtotal - discount)
    print(f"Grand Total: PKR {grand_total:.2f}")

    try:
        cash_paid = float(
            input("Vasool Shuda Cash (Cash Paid): ").strip() or 0
        )
    except ValueError:
        cash_paid = 0.0

    udhar = 0.0
    change = 0.0

    if cash_paid >= grand_total:
        change = cash_paid - grand_total
        status = "PAID"
    else:
        udhar = grand_total - cash_paid
        status = "UDHAR"

    bill_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    date_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    bill_record = {
        "bill_id": bill_id,
        "date": date_str,
        "customer": {"name": cust_name, "phone": cust_phone},
        "items": cart,
        "subtotal": subtotal,
        "discount": discount,
        "grand_total": grand_total,
        "cash_paid": cash_paid,
        "udhar": udhar,
        "change": change,
        "status": status,
    }

    history = load_json(BILLS_FILE)
    history.append(bill_record)
    save_json(BILLS_FILE, history)
    save_json(STOCK_FILE, stock)

    clear_screen()
    print("=" * 50)
    print("                   OFFICIAL RECEIPT               ")
    print("=" * 50)
    print(f"Bill No  : {bill_id}")
    print(f"Date     : {date_str}")
    print(f"Customer : {cust_name}")
    print(f"Phone    : {cust_phone}")
    print("-" * 50)
    print(f"{'Item':<20} {'Qty':<6} {'Price':<10} {'Total':<10}")
    print("-" * 50)

    for item in cart:
        print(
            f"{item['name']:<20} {item['qty']:<6.2f} {item['price']:<10.2f} {item['total']:<10.2f}"
        )

    print("-" * 50)
    print(f"{'Subtotal:':<38} PKR {subtotal:.2f}")
    if discount > 0:
        print(f"{'Discount:':<38} PKR {discount:.2f}")
    print(f"{'GRAND TOTAL:':<38} PKR {grand_total:.2f}")
    print("-" * 50)
    print(f"{'Cash Paid:':<38} PKR {cash_paid:.2f}")

    if udhar > 0:
        print(f"{'UDHAR (Baqaya):':<38} PKR {udhar:.2f}")
        print("STATUS: UDHAR RECORDED")
    else:
        print(f"{'Change Return:':<38} PKR {change:.2f}")
        print("STATUS: FULLY PAID")

    print("=" * 50)
    print("         Shukriya! Dobara Tashreef Layein.        ")
    print("=" * 50)
    input("\nMain Menu par jaane ke liye Enter dabayein...")


# ================= REPORTS & UDHAR LEDGER =================
def show_reports():
    clear_screen()
    history = load_json(BILLS_FILE)

    print("==================================================")
    print("             SALES & UDHAR LEDGER REPORT          ")
    print("==================================================")

    if not history:
        print("Abhi tak koi sale record nahi hui.")
        input("\nEnter dabayein...")
        return

    total_sales = sum(b["grand_total"] for b in history)
    total_cash_collected = sum(b["cash_paid"] for b in history)
    total_udhar = sum(b["udhar"] for b in history)

    print(f"Total Bills Count      : {len(history)}")
    print(f"Total Sales            : PKR {total_sales:.2f}")
    print(f"Total Cash Collected   : PKR {total_cash_collected:.2f}")
    print(f"Market Me Total Udhar  : PKR {total_udhar:.2f}")
    print("--------------------------------------------------")
    print("\nUdhar Waale Customers Ki List:")
    print(f"{'Customer':<20} {'Phone':<15} {'Udhar Amount (PKR)':<15}")
    print("-" * 50)

    udhar_exists = False
    for b in history:
        if b["udhar"] > 0:
            udhar_exists = True
            print(
                f"{b['customer']['name']:<20} {b['customer']['phone']:<15} {b['udhar']:<15.2f}"
            )

    if not udhar_exists:
        print("Kisi bhi customer ka udhar baqaya nahi hai.")

    print("==================================================")
    input("\nWapas jaane ke liye Enter dabayein...")


# ================= MAIN MENU =================
def main():
    while True:
        clear_screen()
        print("==================================================")
        print("        PROFESSIONAL SHOP POS & BILLING           ")
        print("==================================================")
        print("1. Naya Bill Banayein (New Sale / Invoice)")
        print("2. Stock & Items Manage Karein")
        print("3. Sales Report & Udhar Ledger")
        print("4. Exit")
        print("--------------------------------------------------")

        choice = input("Option Chunien (1-4): ").strip()

        if choice == "1":
            create_bill()
        elif choice == "2":
            manage_inventory()
        elif choice == "3":
            show_reports()
        elif choice == "4":
            print("\nSoftware band ho raha hai. Shukriya!")
            sys.exit()


if __name__ == "__main__":
    main()
