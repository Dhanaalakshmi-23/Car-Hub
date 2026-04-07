import frappe
from frappe.utils import nowdate, add_days, getdate

def auto_close_vehicle_sales():
    # Fetch only Delivered sales that are 15+ days old based on delivered_date (new field we'll add)
    sales = frappe.get_all(
        "Vehicle Sale",
        filters={
            "workflow_state": "Delivered",
            "delivered_date": ["<=", add_days(nowdate(), -15)]
        },
        fields=["name"]
    )

    for sale in sales:
        doc = frappe.get_doc("Vehicle Sale", sale.name)
        doc.workflow_state = "Closed"
        doc.save(ignore_permissions=True)
        frappe.db.commit()  # Ensure immediate save for scheduled job