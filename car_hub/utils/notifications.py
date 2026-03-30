import frappe
from frappe.utils import today, add_days

# 1. New vehicle added matching customer preferences
def notify_matching_customers(vehicle):
    """Called via background job from vehicle_inventory.py → after_insert"""
    if not frappe.db.exists("Vehicle Inventory", vehicle):
        return

    inv = frappe.get_doc("Vehicle Inventory", vehicle)
    classification = inv.vehicle_classification
    price = inv.expected_selling_price or 0

    customers = frappe.get_all(
        "Customer Registry",
        fields=["name", "full_name", "email", "budget_min", "budget_max"],
    )

    for cust in customers:
        if not cust.email:
            continue
        # Budget check
        if cust.budget_max and price > cust.budget_max:
            continue
        if cust.budget_min and price < cust.budget_min:
            continue
        # Preferred vehicle type check
        if classification:
            preferred = frappe.get_all(
                "Customer Preferred Vehicle Type",
                filters={"parent": cust.name, "vehicle_classification": classification},
            )
            if not preferred:
                continue

        frappe.sendmail(
            recipients=[cust.email],
            subject="A vehicle matching your preferences is now available!",
            message=f"""Dear {cust.full_name},

A vehicle matching your preferences is now available — {inv.manufacturer} {inv.model} {inv.year_of_manufacture}.

Expected Price: ₹{price:,.2f}

Contact us today to know more!

Best regards,
Car Hub Dealership
""",
        )


# 2. Vehicle Sale submitted

def notify_sale_submitted(sale_name):
    """Called from vehicle_sale.py → on_submit"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)
    if not sale.customer_email:
        return

    frappe.sendmail(
        recipients=[sale.customer_email],
        subject=f"Your vehicle purchase has been initiated — Sale Ref: {sale_name}",
        message=f"""Dear {sale.customer_name},

Your purchase of {sale.vehicle} has been initiated. Sale Ref: {sale_name}

We will keep you updated on every step.

Thank you for choosing Car Hub!

Best regards,
Car Hub Dealership
""",
    )


# 3. Status changes to "Documentation In Progress"
def notify_documentation_in_progress(sale_name):
    """Called from vehicle_sale.py → on_update when status == 'Documentation In Progress'"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)
    if not sale.customer_email:
        return

    frappe.sendmail(
        recipients=[sale.customer_email],
        subject=f"Paperwork in progress — Sale Ref: {sale_name}",
        message=f"""Dear {sale.customer_name},

Paperwork for your vehicle is being processed.

Sale Reference: {sale_name}
Vehicle        : {sale.vehicle}

We will notify you once documentation is complete.

Best regards,
Car Hub Dealership
""",
    )


# 4. Status changes to "Delivered"
def notify_vehicle_delivered(sale_name):
    """Called from vehicle_sale.py → on_update when status == 'Delivered'"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)

    settings = frappe.get_single("Dealership Settings")
    warranty_days = settings.standard_warranty_days or 365
    delivery_date = sale.delivery_date or today()
    warranty_expiry = add_days(delivery_date, warranty_days)

    # ── EMAIL ──
    if sale.customer_email:
        frappe.sendmail(
            recipients=[sale.customer_email],
            subject=f"Congratulations! Your vehicle has been delivered — {sale_name}",
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
        )

    # ── SYSTEM (In-App) NOTIFICATION ──
    customer_user = get_customer_user(sale.customer)
    if customer_user:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Vehicle Delivered — {sale_name}",
            "email_content": (
                f"Congratulations! Your vehicle {sale.vehicle} has been delivered. "
                f"Warranty valid until {warranty_expiry}."
            ),
            "for_user": customer_user,
            "type": "Alert",
            "document_type": "Vehicle Sale",
            "document_name": sale_name,
        }).insert(ignore_permissions=True)


# 5. Discount approval needed

def notify_discount_approval_needed(sale_name, discount_amount, discount_pct):
    """Called from vehicle_sale.py → _validate_discount when limit exceeded"""
    managers = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager", "parenttype": "User"},
        fields=["parent"],
    )

    for m in managers:
        # In-app notification log
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
            "document_name": sale_name,
        }).insert(ignore_permissions=True)

        # Real-time desktop pop-up
        frappe.publish_realtime(
            event="msgprint",
            message=(
                f"Discount approval required for sale {sale_name} — "
                f"{discount_pct}% requested"
            ),
            user=m.parent,
        )


# 6. Vehicle evaluation completed

def notify_evaluation_completed(task_name):
    """Called from vehicle_evaluation_task.py → on_update when status == 'Completed'"""
    task = frappe.get_doc("Vehicle Evaluation Task", task_name)
    vehicle = task.vehicle_inventory or "Unknown Vehicle"
    verdict = task.overall_condition_verdict or "N/A"

    managers = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager", "parenttype": "User"},
        fields=["parent"],
    )

    for m in managers:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Evaluation Complete — {vehicle}",
            "email_content": (
                f"Evaluation complete for {vehicle}. "
                f"Verdict: {verdict}. Evaluator: {task.evaluator}."
            ),
            "for_user": m.parent,
            "type": "Alert",
            "document_type": "Vehicle Evaluation Task",
            "document_name": task_name,
        }).insert(ignore_permissions=True)

        frappe.publish_realtime(
            event="msgprint",
            message=f"Evaluation complete for {vehicle}. Verdict: {verdict}",
            user=m.parent,
        )


# 7. Vehicle Sale cancelled

def notify_sale_cancelled(sale_name):
    """Called from vehicle_sale.py → on_cancel"""
    sale = frappe.get_doc("Vehicle Sale", sale_name)
    if not sale.customer_email:
        return

    frappe.sendmail(
        recipients=[sale.customer_email],
        subject=f"Your vehicle purchase {sale_name} has been cancelled",
        message=f"""Dear {sale.customer_name},

Your vehicle purchase {sale_name} has been cancelled.

Vehicle            : {sale.vehicle}
Cancellation Reason: {sale.cancellation_reason or 'Not specified'}

If you have any questions, please do not hesitate to contact us.

Best regards,
Car Hub Dealership
""",
    )


# 8. Referral bonus credited

def notify_referral_bonus_credited(referrer_customer, bonus_amount):
    """Called from vehicle_sale.py → _credit_referral_bonus"""
    if not referrer_customer:
        return

    cust = frappe.get_doc("Customer Registry", referrer_customer)
    if not cust.email:
        return

    frappe.sendmail(
        recipients=[cust.email],
        subject="You've earned a referral bonus!",
        message=f"""Dear {cust.full_name},

You've earned a referral bonus of ₹{bonus_amount:,.2f}! Thank you for the referral.

Your total referral bonus earned: ₹{cust.referral_bonus_earned or 0:,.2f}

Keep referring and keep earning!

Best regards,
Car Hub Dealership
""",
    )


def get_customer_user(customer_id):
    """Get the Frappe User linked to a Customer Registry via email."""
    if not customer_id:
        return None
    email = frappe.db.get_value("Customer Registry", customer_id, "email")
    if email and frappe.db.exists("User", email):
        return email
    return None