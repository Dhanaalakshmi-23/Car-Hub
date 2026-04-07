import frappe

def set_permissions():

    permissions = [

        # Vehicle Sale
        {
            "doctype": "Vehicle Sale",
            "role": "Sales Consultant",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 0,
            "delete": 0
        },
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
        {
            "doctype": "Vehicle Sale",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1,
            "delete": 1
        },

        # Vehicle Acquisition
        {
            "doctype": "Vehicle Acquisition",
            "role": "Acquisition Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Acquisition",
            "role": "Sales Manager",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Acquisition",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1,
            "delete": 1
        },

        # Vehicle Inventory
        {
            "doctype": "Vehicle Inventory",
            "role": "Sales Consultant",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Inventory",
            "role": "Sales Manager",
            "read": 1,
            "write": 1,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Inventory",
            "role": "Acquisition Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Inventory",
            "role": "Evaluator",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Inventory",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 1
        },

        # Vehicle Evaluation Task
        {
            "doctype": "Vehicle Evaluation Task",
            "role": "Evaluator",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Evaluation Task",
            "role": "Sales Manager",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Evaluation Task",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 1
        },

        # Customer Registry
        {
            "doctype": "Customer Registry",
            "role": "Sales Consultant",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Customer Registry",
            "role": "Sales Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Customer Registry",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 1
        },

        # Seller Registry
        {
            "doctype": "Seller Registry",
            "role": "Acquisition Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Seller Registry",
            "role": "Sales Manager",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Seller Registry",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 1
        },

        # Consulting Engagement
        {
            "doctype": "Consulting Engagement",
            "role": "Sales Consultant",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Consulting Engagement",
            "role": "Sales Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1,
            "delete": 0
        },
        {
            "doctype": "Consulting Engagement",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1,
            "delete": 1
        },

        # Vehicle Classification
        {
            "doctype": "Vehicle Classification",
            "role": "Sales Consultant",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Classification",
            "role": "Acquisition Manager",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Classification",
            "role": "Sales Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Vehicle Classification",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 1
        },

        # Manufacturer
        {
            "doctype": "Manufacturer",
            "role": "Acquisition Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Manufacturer",
            "role": "Sales Manager",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Manufacturer",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "delete": 1
        },

        # Dealership Settings
        {
            "doctype": "Dealership Settings",
            "role": "Sales Manager",
            "read": 1,
            "write": 0,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        },
        {
            "doctype": "Dealership Settings",
            "role": "Dealership Admin",
            "read": 1,
            "write": 1,
            "create": 0,
            "submit": 0,
            "cancel": 0,
            "delete": 0
        }

    ]

    for perm in permissions:
        frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": perm["doctype"],
            "parenttype": "DocType",
            "parentfield": "permissions",

            "role": perm["role"],
            "read": perm.get("read", 0),
            "write": perm.get("write", 0),
            "create": perm.get("create", 0),
            "submit": perm.get("submit", 0),
            "cancel": perm.get("cancel", 0),
            "delete": perm.get("delete", 0)
        }).insert(ignore_permissions=True)

    frappe.db.commit()