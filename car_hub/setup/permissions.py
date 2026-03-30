import frappe

def set_permissions():
    permissions = [
        # Sales Consultant
        {
            "doctype": "Vehicle Sale",
            "role": "Sales Consultant",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },

        # Sales Manager
        {
            "doctype": "Vehicle Sale",
            "role": "Sales Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1,
            "delete": 1
        },

        # Evaluator
        {
            "doctype": "Evaluation Task",
            "role": "Evaluator",
            "read": 1,
            "write": 1,
            "create": 0
        },

        # Acquisition Manager
        {
            "doctype": "Vehicle Acquisition",
            "role": "Acquisition Manager",
            "read": 1,
            "write": 1,
            "create": 1
        },

        # Admin (Full Access)
        {
            "doctype": "*",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1,
            "delete": 1
        }
    ]

    for perm in permissions:
        frappe.get_doc({
            "doctype": "Custom DocPerm",
            **perm
        }).insert(ignore_permissions=True)