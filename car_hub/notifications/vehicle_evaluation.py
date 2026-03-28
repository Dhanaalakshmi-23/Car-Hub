import frappe
from car_hub.utils.email import send_system_notification

def on_submit(doc, method):

    # Get Sales Manager users
    users = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager"},
        fields=["parent"]
    )

    user_list = [u.parent for u in users]

    message = f"""
    Evaluation complete for {doc.vehicle}.
    Verdict: {doc.verdict}
    """

    send_system_notification(user_list, message)