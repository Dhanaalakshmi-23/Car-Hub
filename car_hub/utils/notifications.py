import frappe
from frappe.utils import today, add_days

# 1. Notify customers when a new vehicle matches their preferences
def notify_matching_customers(vehicle_name):
    """Notify customers when a matching vehicle is added"""

    if not frappe.db.exists("Vehicle Inventory", vehicle_name):
        return

    vehicle = frappe.get_doc("Vehicle Inventory", vehicle_name)
    classification = vehicle.vehicle_classification
    price = vehicle.expected_selling_price or 0

    customers = frappe.get_all(
        "Customer Registry",
        fields=[
            "name",
            "full_name",
            "email_address",
            "min_budget",
            "max_budget",
            "preferred_vehicle_types"
        ],
    )

    for cust in customers:
        if not cust.email_address:
            continue

        #Budget check
        if cust.max_budget and price > cust.max_budget:
            continue
        if cust.min_budget and price < cust.min_budget:
            continue

        #Preferred vehicle type check (single field)
        if cust.preferred_vehicle_types and classification:
            if classification not in cust.preferred_vehicle_types:
                continue

        #Send Mail
        frappe.sendmail(
            recipients=["dhanaalakshminarayanan@gmail.com"], 
            subject="New Vehicle Matching Your Interest!",
            message=f"""
Dear {cust.full_name or 'Customer'},

Good news! A vehicle that matches your preferences is now available in our inventory.

🔹 Vehicle Details:
• Brand: {vehicle.manufacturer}
• Model: {vehicle.model}
• Year: {vehicle.year_of_manufacture}
• Type: {classification or 'N/A'}

Expected Price: ₹{price:,.2f}

This vehicle aligns with your budget and interest. We recommend booking a consultation or visiting us soon, as such vehicles move quickly!

Feel free to contact us for more details or to schedule a test drive.

Best Regards,  
Car Hub Team
""",
now=True
        )


# 2. Notify customer when Vehicle Sale is submitted
def notify_sale_submitted(sale_name):
    """Called from vehicle_sale.py → on_submit"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)
    if not sale.email_address:
        return

    frappe.sendmail(
        recipients=["dhanaalakshminarayanan@gmail.com"],
        subject=f"Your vehicle purchase has been initiated — Sale Ref: {sale_name}",
        message=f"""Dear {sale.customer_name},

Your purchase of {sale.vehicle} has been initiated. Sale Ref: {sale_name}

We will keep you updated on every step.

Thank you for choosing Car Hub!

Best regards,
Car Hub Dealership
""",
now=True
    )


# 3. Notify when documentation is in progress
def notify_documentation_in_progress(sale_name):
    """Called from vehicle_sale.py → on_update when status == 'Documentation In Progress'"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)
    if not sale.email_address:
        return

    frappe.sendmail(
        recipients=["dhanaalakshminarayanan@gmail.com"],
        subject=f"Paperwork in progress — Sale Ref: {sale_name}",
        message=f"""Dear {sale.customer_name},

Paperwork for your vehicle is being processed.

Sale Reference: {sale_name}
Vehicle        : {sale.vehicle}

We will notify you once documentation is complete.

Best regards,
Car Hub Dealership
""",
now=True
    )


# 4. Notify when vehicle is delivered
def notify_vehicle_delivered(sale_name):
    """Called from vehicle_sale.py → on_update when status == 'Delivered'"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)

    settings = frappe.get_single("Dealership Settings")
    warranty_days = settings.standard_warranty_days or 365
    delivery_date = sale.delivery_date or today()
    warranty_expiry = add_days(delivery_date, warranty_days)

    # Email notification
    if sale.customer_email:
        frappe.sendmail(
            recipients=["dhanaalakshminarayanan@gmail.com"],
            subject=f"Congratulations! Your vehicle has been delivered — Sale Ref: {sale_name}",
            message=f"""Dear {sale.customer_name},

Congratulations! Your vehicle has been delivered.

Vehicle        : {sale.vehicle}
Sale Reference : {sale_name}
Delivery Date  : {delivery_date}
Warranty valid until: {warranty_expiry}

Thank you for choosing Car Hub. Wishing you many happy miles!

Best regards,
Car Hub Dealership
""",
now=True
        )

    # In-App Notification
    customer_user = get_customer_user(sale.customer)
    if customer_user:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Vehicle Delivered — Sale Ref: {sale_name}",
            "email_content": (
                f"Congratulations! Your vehicle {sale.vehicle} has been delivered. "
                f"Warranty valid until {warranty_expiry}."
            ),
            "for_user": customer_user,
            "type": "Alert",
            "document_type": "Vehicle Sale",
            "document_name": sale_name
        }).insert(ignore_permissions=True)


# 5. Notify Sales Manager for discount approval

def notify_discount_approval_needed(sale_name, discount_amount, discount_pct):
    """Called from vehicle_sale.py → _validate_discount when limit exceeded"""
    managers = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager"},
        fields=["parent"]
    )

    for m in managers:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Discount Approval Required — Sale {sale_name}",
            "email_content": (
                f"Discount approval required for sale {sale_name} — "
                f"{discount_pct}% (₹{discount_amount:,.2f}) requested."
            ),
            "for_user": m.parent,
            "type": "Alert",
            "document_type": "Vehicle Sale",
            "document_name": sale_name
        }).insert(ignore_permissions=True)

        frappe.publish_realtime(
            event="msgprint",
            message=f"Discount approval required for sale {sale_name} — {discount_pct}% requested",
            user=m.parent
        )


# 6. Notify evaluation completed
def notify_evaluation_completed(task_name):
    """Called from vehicle_evaluation_task.py → on_update when status == 'Completed'"""
    task = frappe.get_doc("Vehicle Evaluation Task", task_name)
    vehicle = task.vehicle_inventory or "Unknown Vehicle"
    verdict = task.overall_condition or "N/A"

    managers = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager"},
        fields=["parent"]
    )

    for m in managers:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Evaluation Complete — {vehicle}",
            "email_content": f"Evaluation complete for {vehicle}. Verdict: {verdict}. Evaluator: {task.evaluator}.",
            "for_user": m.parent,
            "type": "Alert",
            "document_type": "Vehicle Evaluation Task",
            "document_name": task_name
        }).insert(ignore_permissions=True)

        frappe.publish_realtime(
            event="msgprint",
            message=f"Evaluation complete for {vehicle}. Verdict: {verdict}",
            user=m.parent
        )


# 7. Notify when Vehicle Sale is cancelled
def notify_sale_cancelled(sale_name):
    """Called from vehicle_sale.py → on_cancel"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)
    if not sale.email_address:
        return

    frappe.sendmail(
        recipients=["dhanaalakshminarayanan@gmail.com"],
        subject=f"Your vehicle purchase {sale_name} has been cancelled",
        message=f"""Dear {sale.customer_name},

Your vehicle purchase {sale_name} has been cancelled.

Vehicle            : {sale.vehicle}
Cancellation Reason: {sale.cancellation_reason or 'Not specified'}

If you have any questions, please contact us.

Best regards,
Car Hub Dealership
""",
now=True
    )


# 8. Notify referral bonus credited

def notify_referral_bonus_credited(referrer_customer, bonus_amount):
    """Called from vehicle_sale.py → _credit_referral_bonus"""
    if not referrer_customer:
        return

    cust = frappe.get_doc("Customer Registry", referrer_customer)
    if not cust.email_address:
        return

    frappe.sendmail(
        recipients=["dhanaalakshminarayanan@gmail.com"],
        subject="You've earned a referral bonus!",
        message=f"""Dear {cust.full_name},

You've earned a referral bonus of ₹{bonus_amount:,.2f}! Thank you for the referral.

Your total referral bonus earned: ₹{cust.referral_bonus_earned or 0:,.2f}

Keep referring and keep earning!

Best regards,
Car Hub Dealership
""",
now=True
    )


# Helper function
def get_customer_user(customer_id):
    """Get the Frappe User linked to a Customer Registry via email."""
    if not customer_id:
        return None
    email = frappe.db.get_value("Customer Registry", customer_id, "email")
    if email and frappe.db.exists("User", email):
        return email
    return None