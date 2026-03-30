import frappe

def create_roles():
    roles = [
        "Sales Consultant",
        "Sales Manager",
        "Evaluator",
        "Acquisition Manager",
        "Dealership Admin"
    ]

    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role
            }).insert(ignore_permissions=True)