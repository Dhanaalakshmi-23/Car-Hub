import frappe
from car_hub.utils.email import send_email, send_system_notification

# Vehicle Sale Submitted → Customer Email
def on_submit(doc, method):
    if doc.customer_email:
        message = f"""
        Your purchase of {doc.vehicle} has been initiated.
        Sale Ref: {doc.name}
        """
        send_email([doc.customer_email], "Vehicle Purchase Confirmation", message)


# Status Change Notifications
def on_update(doc, method):

    # Documentation In Progress
    if doc.status == "Documentation In Progress":
        send_email(
            [doc.customer_email],
            "Documentation Started",
            "Paperwork for your vehicle is being processed"
        )

    # Delivered
    if doc.status == "Delivered":
        send_email(
            [doc.customer_email],
            "Vehicle Delivered",
            f"""
            Congratulations! Your vehicle has been delivered.
            Warranty valid until {doc.warranty_end_date}
            """
        )


# Sale Cancelled → Customer Email
def on_cancel(doc, method):
    send_email(
        [doc.customer_email],
        "Sale Cancelled",
        f"Your vehicle purchase {doc.name} has been cancelled"
    )