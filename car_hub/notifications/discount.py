import frappe
from car_hub.utils.email import send_system_notification

def notify_discount_approval(doc):
    
    # Get Sales Managers
    users = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager"},
        fields=["parent"]
    )

    user_list = [u.parent for u in users]

    message = f"""
    Discount approval required for sale {doc.name}
    — {doc.discount_percentage}% requested
    """

    send_system_notification(user_list, message)