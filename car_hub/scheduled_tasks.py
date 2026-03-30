import frappe
from datetime import datetime, timedelta
from car_hub.utils.notifications import send_email

def send_slow_inventory_report():

    date_30_days_ago = datetime.now() - timedelta(days=30)

    vehicles = frappe.get_all(
        "Vehicle Inventory",
        filters={
            "status": "Available for Sale",
            "creation": ["<", date_30_days_ago]
        },
        fields=["name", "manufacturer", "model", "year"]
    )

    if not vehicles:
        return

    # Get Sales Managers
    users = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager"},
        fields=["parent"]
    )

    emails = []
    for u in users:
        email = frappe.db.get_value("User", u.parent, "email")
        if email:
            emails.append(email)

    # Build message
    message = "Slow Moving Inventory (>30 days):<br><br>"

    for v in vehicles:
        message += f"{v.manufacturer} {v.model} ({v.year})<br>"

    send_email(emails, "Weekly Slow Inventory Report", message)

def auto_close_sales():

    date_15_days_ago = datetime.now() - timedelta(days=15)

    sales = frappe.get_all(
        "Vehicle Sale",
        filters={
            "status": "Delivered",
            "modified": ["<", date_15_days_ago]
        },
        fields=["name"]
    )

    for sale in sales:
        doc = frappe.get_doc("Vehicle Sale", sale.name)

        doc.status = "Closed"
        doc.save(ignore_permissions=True)

        frappe.db.commit()
def log_overdue_evaluations():

    date_5_days_ago = datetime.now() - timedelta(days=5)

    evaluations = frappe.get_all(
        "Vehicle Evaluation",
        filters={
            "status": "Pending",
            "creation": ["<", date_5_days_ago]
        },
        fields=["name", "vehicle"]
    )

    if not evaluations:
        return

    message = "Overdue Vehicle Evaluations (>5 days):\n\n"

    for e in evaluations:
        message += f"{e.name} - {e.vehicle}\n"

    frappe.log_error(message, "Overdue Evaluations Alert")