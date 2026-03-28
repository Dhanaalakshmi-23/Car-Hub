import frappe
from frappe.utils import nowdate, add_days

def auto_close_vehicle_sales():
    sales = frappe.get_all(
        "Vehicle Sale",
        filters={"workflow_state": "Delivered"},
        fields=["name", "modified"]
    )

    for sale in sales:
        if add_days(sale.modified, 15) <= nowdate():
            doc = frappe.get_doc("Vehicle Sale", sale.name)
            doc.workflow_state = "Closed"
            doc.save(ignore_permissions=True)